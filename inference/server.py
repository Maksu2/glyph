#!/usr/bin/env python3
"""Public Glyph inference demo backend.

The server is intentionally small and stdlib-based. It exposes only:
- GET /health
- POST /api/generate

It does not log prompt or response contents by default.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import math
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from generate import load_model, load_tokenizer  # noqa: E402


MODEL_NAME = "Glyph-27M"
PRESET_NAME = os.environ.get("GLYPH_DEMO_PRESET", "balanced-long")
ENABLED = os.environ.get("GLYPH_DEMO_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
HOST = os.environ.get("GLYPH_DEMO_HOST", "127.0.0.1")
PORT = int(os.environ.get("GLYPH_DEMO_PORT", "8195"))
CHECKPOINT = os.environ.get("GLYPH_DEMO_CHECKPOINT", "checkpoints/public-demo.pt")
TOKENIZER = os.environ.get("GLYPH_DEMO_TOKENIZER", "data/processed/tokenizer.model")

MAX_BODY_BYTES = int(os.environ.get("GLYPH_DEMO_MAX_BODY_BYTES", "4096"))
MAX_PROMPT_CHARS = int(os.environ.get("GLYPH_DEMO_MAX_PROMPT_CHARS", "500"))
MAX_NEW_TOKENS = int(os.environ.get("GLYPH_DEMO_MAX_NEW_TOKENS", "120"))
TIMEOUT_SECONDS = float(os.environ.get("GLYPH_DEMO_TIMEOUT_SECONDS", "45"))
THREADS = max(1, int(os.environ.get("GLYPH_DEMO_THREADS", "4")))

TEMPERATURE = float(os.environ.get("GLYPH_DEMO_TEMPERATURE", "0.75"))
TOP_K = int(os.environ.get("GLYPH_DEMO_TOP_K", "40"))
TOP_P = float(os.environ.get("GLYPH_DEMO_TOP_P", "0.92"))
REPETITION_PENALTY = float(os.environ.get("GLYPH_DEMO_REPETITION_PENALTY", "1.15"))
NO_REPEAT_NGRAM = int(os.environ.get("GLYPH_DEMO_NO_REPEAT_NGRAM", "4"))

CONCURRENCY = max(1, int(os.environ.get("GLYPH_DEMO_CONCURRENCY", "1")))
QUEUE_SIZE = max(0, int(os.environ.get("GLYPH_DEMO_QUEUE_SIZE", "4")))
QUEUE_TIMEOUT_SECONDS = float(os.environ.get("GLYPH_DEMO_QUEUE_TIMEOUT_SECONDS", "10"))

RATE_LIMITS = (
    ("minute", int(os.environ.get("GLYPH_DEMO_RATE_PER_MINUTE", "3")), 60),
    ("ten_minutes", int(os.environ.get("GLYPH_DEMO_RATE_PER_10_MINUTES", "10")), 600),
    ("day", int(os.environ.get("GLYPH_DEMO_RATE_PER_DAY", "30")), 86400),
)
RATE_SALT = os.environ.get("GLYPH_DEMO_RATE_SALT", "glyph-demo-local-rate-salt")
CORS_ORIGIN = os.environ.get("GLYPH_DEMO_CORS_ORIGIN", "https://glyph.maksu.online")

CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class QueueFull(Exception):
    pass


class QueueTimeout(Exception):
    pass


class GenerationTimeout(Exception):
    pass


class GenerationGate:
    def __init__(self, concurrency: int, queue_size: int):
        self.concurrency = concurrency
        self.queue_size = queue_size
        self.active = 0
        self.queued = 0
        self.condition = threading.Condition()

    def acquire(self, timeout: float):
        deadline = time.monotonic() + timeout
        with self.condition:
            if self.active < self.concurrency:
                self.active += 1
                return _GateToken(self)
            if self.queued >= self.queue_size:
                raise QueueFull()
            self.queued += 1
            try:
                while self.active >= self.concurrency:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise QueueTimeout()
                    self.condition.wait(remaining)
                self.active += 1
                return _GateToken(self)
            finally:
                self.queued = max(0, self.queued - 1)

    def release(self):
        with self.condition:
            self.active = max(0, self.active - 1)
            self.condition.notify_all()

    def state(self) -> dict[str, int]:
        with self.condition:
            return {"active": self.active, "queued": self.queued}


class _GateToken:
    def __init__(self, gate: GenerationGate):
        self.gate = gate

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.gate.release()


class RateLimiter:
    def __init__(self):
        self.lock = threading.Lock()
        self.buckets: dict[str, list[float]] = {}

    def check(self, key: str) -> tuple[bool, str | None, int]:
        now = time.time()
        with self.lock:
            stamps = self.buckets.get(key, [])
            keep_window = max(window for _, _, window in RATE_LIMITS)
            stamps = [stamp for stamp in stamps if now - stamp < keep_window]

            for name, limit, window in RATE_LIMITS:
                if limit <= 0:
                    continue
                window_stamps = [stamp for stamp in stamps if now - stamp < window]
                if len(window_stamps) >= limit:
                    retry = max(1, int(window - (now - min(window_stamps))))
                    self.buckets[key] = stamps
                    return False, name, retry

            stamps.append(now)
            self.buckets[key] = stamps
        return True, None, 0


def configure_torch() -> None:
    torch.set_num_threads(THREADS)
    try:
        torch.set_num_interop_threads(max(1, min(THREADS, 2)))
    except RuntimeError:
        pass


def clamp_prompt(raw: Any) -> str:
    if not isinstance(raw, str):
        raise ValueError("Prompt must be a string.")
    prompt = raw.strip()
    if not prompt:
        raise ValueError("Prompt is empty.")
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError(f"Prompt is too long. Limit: {MAX_PROMPT_CHARS} characters.")
    if CONTROL_CHARS_RE.search(prompt):
        raise ValueError("Prompt contains unsupported control characters.")
    return prompt


def ip_hash(value: str) -> str:
    digest = hashlib.sha256((RATE_SALT + "|" + value).encode("utf-8", "ignore")).hexdigest()
    return digest[:20]


def client_ip(handler: BaseHTTPRequestHandler) -> str:
    remote = handler.client_address[0] if handler.client_address else "unknown"
    trusted_proxy_header = handler.headers.get("X-Glyph-Client-IP", "").strip()
    if trusted_proxy_header:
        try:
            remote_ip = ipaddress.ip_address(remote)
            if remote_ip.is_loopback or remote_ip.is_private:
                return trusted_proxy_header[:120]
        except ValueError:
            pass
    return remote


def log_event(**fields) -> None:
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def apply_repetition_penalty(logits: torch.Tensor, idx: torch.Tensor) -> None:
    if not REPETITION_PENALTY or REPETITION_PENALTY == 1.0:
        return
    penalty = max(1.0, REPETITION_PENALTY)
    for batch_idx in range(idx.size(0)):
        seen_tokens = idx[batch_idx].unique()
        seen_logits = logits[batch_idx, seen_tokens]
        logits[batch_idx, seen_tokens] = torch.where(
            seen_logits < 0,
            seen_logits * penalty,
            seen_logits / penalty,
        )


def block_repeated_ngrams(logits: torch.Tensor, idx: torch.Tensor) -> None:
    if not NO_REPEAT_NGRAM or NO_REPEAT_NGRAM <= 1:
        return
    n = int(NO_REPEAT_NGRAM)
    for batch_idx in range(idx.size(0)):
        sequence = idx[batch_idx].tolist()
        if len(sequence) < n - 1:
            continue
        prefix = tuple(sequence[-(n - 1) :])
        banned = set()
        for pos in range(len(sequence) - n + 1):
            if tuple(sequence[pos : pos + n - 1]) == prefix:
                banned.add(sequence[pos + n - 1])
        if banned:
            logits[batch_idx, list(banned)] = float("-inf")


@torch.no_grad()
def generate_with_deadline(prompt: str, deadline: float) -> tuple[str, int]:
    prompt_ids = TOKENIZER_MODEL.encode(prompt, out_type=int)
    if not prompt_ids:
        raise ValueError("Prompt is empty after tokenization.")
    idx = torch.tensor([prompt_ids[-(MODEL_CONFIG.context_len - 1) :]], dtype=torch.long)
    initial_len = idx.size(1)

    for _ in range(MAX_NEW_TOKENS):
        if time.monotonic() >= deadline:
            raise GenerationTimeout()

        idx_cond = idx[:, -MODEL_CONFIG.context_len :]
        logits, _ = MODEL(idx_cond)
        logits = logits[:, -1, :]

        apply_repetition_penalty(logits, idx)
        block_repeated_ngrams(logits, idx)

        if TEMPERATURE == 0.0:
            idx_next = logits.argmax(dim=-1, keepdim=True)
        else:
            logits = logits / TEMPERATURE
            if TOP_K > 0:
                k = min(TOP_K, logits.size(-1))
                top_values, _ = torch.topk(logits, k)
                logits[logits < top_values[:, [-1]]] = float("-inf")
            if TOP_P and TOP_P < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                sorted_probs = F.softmax(sorted_logits, dim=-1)
                cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                sorted_remove = cumulative_probs > TOP_P
                sorted_remove[:, 1:] = sorted_remove[:, :-1].clone()
                sorted_remove[:, 0] = False
                remove = torch.zeros_like(logits, dtype=torch.bool)
                remove.scatter_(1, sorted_indices, sorted_remove)
                logits = logits.masked_fill(remove, float("-inf"))
            probs = F.softmax(logits, dim=-1)
            if not torch.isfinite(probs).all():
                raise RuntimeError("Invalid probabilities.")
            idx_next = torch.multinomial(probs, num_samples=1)

        idx = torch.cat((idx, idx_next), dim=1)
        if int(idx_next.item()) == TOKENIZER_MODEL.eos_id():
            break

    all_ids = idx[0].tolist()
    generated_ids = all_ids[initial_len:]
    text_ids = generated_ids[:-1] if generated_ids and generated_ids[-1] == TOKENIZER_MODEL.eos_id() else generated_ids
    return TOKENIZER_MODEL.decode(all_ids[:initial_len] + text_ids), len(generated_ids)


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def error_payload(error: str, message: str) -> dict[str, str]:
    return {"error": error, "message": message}


class Handler(BaseHTTPRequestHandler):
    server_version = "GlyphInference/1.0"

    def log_message(self, format, *args):  # noqa: A002
        return

    def send_json(self, code: int, payload: dict, retry_after: int | None = None) -> None:
        body = json_bytes(payload)
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        origin = self.headers.get("Origin")
        if origin and origin == CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        if retry_after is not None:
            self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        if self.path != "/api/generate":
            self.send_json(404, error_payload("not_found", "Not found."))
            return
        self.send_response(204)
        origin = self.headers.get("Origin")
        if origin and origin == CORS_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] != "/health":
            self.send_json(404, error_payload("not_found", "Not found."))
            return
        self.send_json(
            200,
            {
                "status": "ok",
                "enabled": ENABLED,
                "model": MODEL_NAME,
                "preset": PRESET_NAME,
                "queue": GATE.state(),
            },
        )

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/api/generate":
            self.send_json(404, error_payload("not_found", "Not found."))
            return

        ip = client_ip(self)
        key = ip_hash(ip)
        start = time.perf_counter()
        prompt_chars = 0
        status = "internal_error"

        try:
            if not ENABLED:
                status = "disabled"
                self.send_json(503, error_payload("disabled", "Demo is temporarily disabled."))
                return

            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0 or length > MAX_BODY_BYTES:
                status = "invalid_prompt"
                self.send_json(400, error_payload("invalid_prompt", "Request body is too large or empty."))
                return

            allowed, limit_name, retry_after = RATE_LIMITER.check(key)
            if not allowed:
                status = "rate_limited"
                self.send_json(
                    429,
                    error_payload("rate_limited", "Too many requests. Please try again later."),
                    retry_after=retry_after,
                )
                return

            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                prompt = clamp_prompt(payload.get("prompt"))
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
                status = "invalid_prompt"
                self.send_json(400, error_payload("invalid_prompt", str(exc)))
                return

            prompt_chars = len(prompt)
            try:
                with GATE.acquire(QUEUE_TIMEOUT_SECONDS):
                    deadline = time.monotonic() + TIMEOUT_SECONDS
                    output, generated_tokens = generate_with_deadline(prompt, deadline)
            except QueueFull:
                status = "queue_full"
                self.send_json(429, error_payload("queue_full", "The demo is busy. Please try again soon."), retry_after=15)
                return
            except QueueTimeout:
                status = "queue_full"
                self.send_json(429, error_payload("queue_full", "The demo queue timed out. Please try again soon."), retry_after=15)
                return
            except GenerationTimeout:
                status = "timeout"
                self.send_json(504, error_payload("timeout", "Generation took too long. Please try a shorter prompt."))
                return

            duration_ms = int((time.perf_counter() - start) * 1000)
            status = "ok"
            self.send_json(
                200,
                {
                    "output": output,
                    "model": MODEL_NAME,
                    "preset": PRESET_NAME,
                    "duration_ms": duration_ms,
                    "generated_tokens": generated_tokens,
                },
            )
        except Exception:
            status = "internal_error"
            self.send_json(500, error_payload("internal_error", "Generation failed. Please try again later."))
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log_event(
                status=status,
                ip_hash=key,
                prompt_chars=prompt_chars,
                duration_ms=duration_ms,
            )


def require_file(path: str, label: str) -> None:
    if not Path(path).exists():
        raise SystemExit(f"{label} not found: {path}")


configure_torch()
require_file(CHECKPOINT, "checkpoint")
require_file(TOKENIZER, "tokenizer")
MODEL, MODEL_CONFIG = load_model(CHECKPOINT)
TOKENIZER_MODEL = load_tokenizer(TOKENIZER)
GATE = GenerationGate(CONCURRENCY, QUEUE_SIZE)
RATE_LIMITER = RateLimiter()


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(
        json.dumps(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": "startup",
                "host": HOST,
                "port": PORT,
                "enabled": ENABLED,
                "model": MODEL_NAME,
                "preset": PRESET_NAME,
                "threads": THREADS,
                "max_prompt_chars": MAX_PROMPT_CHARS,
                "max_new_tokens": MAX_NEW_TOKENS,
                "timeout_seconds": TIMEOUT_SECONDS,
                "concurrency": CONCURRENCY,
                "queue_size": QUEUE_SIZE,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
