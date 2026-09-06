#!/usr/bin/env python3
"""Benchmark small public-demo sampling presets for Glyph-27M."""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from generate import load_model, load_tokenizer  # noqa: E402


PRESETS = {
    "strict": {
        "temperature": 0.6,
        "top_k": 30,
        "top_p": 0.90,
        "max_new_tokens": 80,
        "repetition_penalty": 1.15,
        "no_repeat_ngram_size": 4,
    },
    "balanced": {
        "temperature": 0.75,
        "top_k": 40,
        "top_p": 0.92,
        "max_new_tokens": 100,
        "repetition_penalty": 1.15,
        "no_repeat_ngram_size": 4,
    },
    "creative": {
        "temperature": 0.9,
        "top_k": 50,
        "top_p": 0.95,
        "max_new_tokens": 120,
        "repetition_penalty": 1.2,
        "no_repeat_ngram_size": 4,
    },
}


def read_prompts(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def repeated_ngram_ratio(text: str, n: int = 4) -> float:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    if len(words) < n:
        return 0.0
    grams = [tuple(words[index : index + n]) for index in range(len(words) - n + 1)]
    if not grams:
        return 0.0
    return round(1.0 - (len(set(grams)) / len(grams)), 4)


def simple_flags(text: str) -> list[str]:
    lower = text.lower()
    flags = []
    if repeated_ngram_ratio(text, 3) > 0.08:
        flags.append("repeated-ngrams")
    if any(phrase in lower for phrase in ("odpowiedzi:", "wyświetleń:", "zobacz także", "polsat sport")):
        flags.append("web-noise")
    if len(re.findall(r"\b(\w+)\b(?:\W+\1\b){2,}", lower, flags=re.UNICODE)) > 0:
        flags.append("word-loop")
    if len(text.strip()) < 30:
        flags.append("very-short")
    return flags


def generate_one(model, tokenizer, cfg, prompt: str, preset: dict) -> tuple[str, float, int]:
    prompt_ids = tokenizer.encode(prompt, out_type=int)
    if not prompt_ids:
        return "", 0.0, 0
    idx = torch.tensor([prompt_ids[-(cfg.context_len - 1) :]], dtype=torch.long)
    start = time.perf_counter()
    with torch.no_grad():
        out = model.generate(
            idx,
            max_new_tokens=preset["max_new_tokens"],
            temperature=preset["temperature"],
            top_k=preset["top_k"],
            top_p=preset["top_p"],
            repetition_penalty=preset["repetition_penalty"],
            no_repeat_ngram_size=preset["no_repeat_ngram_size"],
        )
    duration = time.perf_counter() - start
    text = tokenizer.decode(out[0].tolist())
    generated_tokens = max(0, out.size(1) - idx.size(1))
    return text, duration, generated_tokens


def summarize(rows: list[dict]) -> dict:
    by_preset = {}
    for preset in PRESETS:
        subset = [row for row in rows if row["preset"] == preset]
        durations = [row["duration_seconds"] for row in subset]
        toks = [row["tokens_per_second"] for row in subset if row["tokens_per_second"]]
        flags = [flag for row in subset for flag in row["flags"]]
        by_preset[preset] = {
            "count": len(subset),
            "avg_duration_seconds": round(statistics.mean(durations), 3) if durations else None,
            "avg_tokens_per_second": round(statistics.mean(toks), 2) if toks else None,
            "flag_count": len(flags),
            "flags": sorted(set(flags)),
        }
    return by_preset


def atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Glyph public demo presets")
    parser.add_argument("--checkpoint", default="checkpoints/public-demo.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--prompts", default="eval/demo_prompts.json")
    parser.add_argument("--out", default="reports/demo_preset_benchmark/latest.json")
    parser.add_argument("--threads", type=int, default=int(os.environ.get("GLYPH_DEMO_THREADS", "1")))
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    torch.set_num_threads(max(1, args.threads))
    try:
        torch.set_num_interop_threads(max(1, args.threads))
    except RuntimeError:
        pass
    torch.manual_seed(args.seed)

    model, cfg = load_model(args.checkpoint)
    tokenizer = load_tokenizer(args.tokenizer)
    prompts = read_prompts(Path(args.prompts))

    rows = []
    for preset_name, preset in PRESETS.items():
        for item in prompts:
            text, duration, generated_tokens = generate_one(model, tokenizer, cfg, item["prompt"], preset)
            rows.append(
                {
                    "preset": preset_name,
                    "prompt_id": item["id"],
                    "prompt": item["prompt"],
                    "output": text,
                    "duration_seconds": round(duration, 3),
                    "generated_tokens": generated_tokens,
                    "tokens_per_second": round(generated_tokens / duration, 2) if duration else None,
                    "flags": simple_flags(text),
                }
            )
            print(
                f"{preset_name:8s} {item['id']:16s} "
                f"{duration:6.2f}s {generated_tokens:3d} tok "
                f"{generated_tokens / duration if duration else 0:5.1f} tok/s "
                f"flags={','.join(rows[-1]['flags']) or '-'}",
                flush=True,
            )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checkpoint": "checkpoints/public-demo.pt",
        "threads": max(1, args.threads),
        "presets": PRESETS,
        "summary": summarize(rows),
        "rows": rows,
    }
    atomic_write(Path(args.out), payload)
    print(f"Wrote benchmark report to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
