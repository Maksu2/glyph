#!/usr/bin/env python3
"""Deterministic per-domain validation loss protocol (Glyph-100M v2.4.2 line).

PROTOCOL (identical for every checkpoint x domain cell):
  - fp32 CPU, fresh model from checkpoint state_dict, model.eval()
  - torch.no_grad(), no RNG use anywhere (no sampling, dropout inactive)
  - data: raw uint16 token stream, sequential non-overlapping 512-token blocks
    from offset 0; trailing remainder < 512 tokens is dropped (count recorded)
  - each block scored as input=block[:-1], target=block[1:] (511 pred/block)
  - fixed batch_size=4 rows for every run (last batch may be shorter)
  - loss = sum(CE, reduction='sum') over ALL scored tokens / total scored
    tokens (token-weighted exact mean, batching-independent by construction)
  - perplexity = exp(loss)
Determinism check: the aggregate domain is scored twice for one checkpoint;
  |loss_run1 - loss_run2| must be exactly 0.0 and is stored as repeat_delta.

Usage:
  .venv/bin/python scripts/eval_domain_loss.py   # ~1.5h on CPU, background it
Output:
  reports/glyph100_domain_eval.json
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import ModelConfig  # noqa: E402
from model import GPT  # noqa: E402

BLOCK = 512
BATCH = 4

CHECKPOINTS = {
    "10k": "checkpoints/glyph-100m-v2_4_2-10k/step_0010000.pt",
    "12.5k": "checkpoints/glyph-100m-v2_4_2-15k/step_0012500.pt",
    "15k": "checkpoints/glyph-100m-v2_4_2-15k/latest.pt",
    "cooldown": "checkpoints/glyph-100m-v2_4_2-15k-cooldown/latest.pt",
}

DOMAINS = {
    "wikipedia": "data/processed/val_domain_wikipedia.bin",
    "wolne_lektury": "data/processed/val_domain_wolne_lektury.bin",
    "1000_novels": "data/processed/val_domain_1000_novels.bin",
    "eltec": "data/processed/val_domain_eltec.bin",
    "parlament_clean": "data/processed/val_domain_parlament_clean.bin",
    "wikibooks": "data/processed/val_domain_wikibooks.bin",
    "aggregate": "data/processed/glyph100_v2_4_2_val.bin",
}


def load_model(path: Path) -> tuple[GPT, dict]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config") or {}
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items()
                         if k in ModelConfig.__dataclass_fields__})
    model = GPT(cfg)
    model.load_state_dict(state["model"])
    assert model.tok_emb.weight.dtype == torch.float32
    model.eval()
    return model, state


def score_stream(model: GPT, tokens: np.ndarray) -> dict:
    n_blocks = len(tokens) // BLOCK
    used = n_blocks * BLOCK
    total_loss = 0.0
    total_tok = 0
    with torch.no_grad():
        for start in range(0, n_blocks, BATCH):
            rows = []
            for b in range(start, min(start + BATCH, n_blocks)):
                blk = tokens[b * BLOCK:(b + 1) * BLOCK]
                rows.append(np.asarray(blk, dtype=np.int64))
            x = torch.from_numpy(np.stack(rows))
            logits, _ = model(x[:, :-1])
            total_loss += F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                x[:, 1:].reshape(-1),
                reduction="sum",
            ).item()
            total_tok += x.size(0) * (BLOCK - 1)
    loss = total_loss / total_tok
    return {"loss": loss, "ppl": math.exp(loss), "blocks": n_blocks,
            "tokens_total": int(len(tokens)), "tokens_scored": total_tok,
            "tokens_dropped": int(len(tokens)) - used}


def main() -> None:
    t0 = time.perf_counter()
    streams = {}
    for label, rel in DOMAINS.items():
        p = ROOT / rel
        if not p.exists():
            raise SystemExit(f"missing domain file: {p}")
        streams[label] = np.memmap(p, dtype=np.uint16, mode="r")

    results: dict = {"protocol": {
        "block": BLOCK, "batch_size": BATCH, "dtype": "fp32", "device": "cpu",
        "order": "sequential from offset 0, remainder dropped",
        "loss": "token-weighted exact mean CE", "ppl": "exp(loss)"},
        "checkpoints": {}, "domains": {}}
    for label, arr in streams.items():
        results["domains"][label] = {
            "tokens": int(len(arr)),
            "blocks": int(len(arr) // BLOCK)}

    for ckpt_label, rel in CHECKPOINTS.items():
        p = ROOT / rel
        if not p.exists():
            print(f"SKIP checkpoint {ckpt_label}: {p} missing", flush=True)
            results["checkpoints"][ckpt_label] = {"missing": str(p)}
            continue
        model, state = load_model(p)
        step = state.get("step")
        print(f"checkpoint {ckpt_label}: {rel} (step={step})", flush=True)
        cell = {"path": rel, "step": step, "cells": {}}
        for dlabel, arr in streams.items():
            r = score_stream(model, arr)
            cell["cells"][dlabel] = r
            print(f"  {dlabel}: loss={r['loss']:.4f} ppl={r['ppl']:.2f} "
                  f"blocks={r['blocks']}", flush=True)
        if ckpt_label == "15k":
            r2 = score_stream(model, streams["aggregate"])
            r1 = cell["cells"]["aggregate"]["loss"]
            cell["repeat_delta_aggregate"] = abs(r1 - r2["loss"])
            print(f"  determinism repeat_delta={cell['repeat_delta_aggregate']!r}",
                  flush=True)
        results["checkpoints"][ckpt_label] = cell
        del model, state

    # spreads + deltas
    for ckpt_label, ck in results["checkpoints"].items():
        if "cells" not in ck:
            continue
        dom = {k: v for k, v in ck["cells"].items() if k != "aggregate"}
        lo = min(dom.items(), key=lambda kv: kv[1]["loss"])
        hi = max(dom.items(), key=lambda kv: kv[1]["loss"])
        ck["spread"] = {"easiest": lo[0], "easiest_loss": lo[1]["loss"],
                        "hardest": hi[0], "hardest_loss": hi[1]["loss"],
                        "delta": hi[1]["loss"] - lo[1]["loss"]}
    avail = [k for k in ("10k", "15k", "cooldown") if "cells" in results["checkpoints"].get(k, {})]
    results["domain_deltas"] = {}
    for dlabel in DOMAINS:
        d = {}
        if "10k" in avail and "15k" in avail:
            a = results["checkpoints"]["10k"]["cells"][dlabel]["loss"]
            b = results["checkpoints"]["15k"]["cells"][dlabel]["loss"]
            d["15k_minus_10k"] = b - a
        if "15k" in avail and "cooldown" in avail:
            b = results["checkpoints"]["15k"]["cells"][dlabel]["loss"]
            c = results["checkpoints"]["cooldown"]["cells"][dlabel]["loss"]
            d["cooldown_minus_15k"] = c - b
        results["domain_deltas"][dlabel] = d

    results["elapsed_seconds"] = round(time.perf_counter() - t0, 1)
    out = ROOT / "reports" / "glyph100_domain_eval.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} elapsed={results['elapsed_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
