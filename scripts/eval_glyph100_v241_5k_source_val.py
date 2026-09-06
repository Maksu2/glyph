#!/usr/bin/env python3
"""Evaluate Glyph-100M v2.4.1 checkpoints on source-specific validation bins."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import sentencepiece as spm
import torch

from eval_glyph100_stage2 import configure_attention_backend, load_model
from train import TokenDataset, estimate_loss


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_1_5k_eval_20260717"
DOC_CANDIDATES = (
    ROOT / "data" / "processed" / "glyph100_v2_4_1_docs.jsonl",
    ROOT / "data" / "raw" / "glyph100_v2_4_1" / "glyph100_v2_4_1_docs.jsonl",
    ROOT / "source_docs.jsonl",
)
TOKENIZER = ROOT / "data" / "processed" / "tokenizer.model"
BIN_DIR = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_val_bins"
OUT_JSON = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.json"
OUT_MD = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.md"
CHECKPOINTS = {
    "1k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-1k" / "step_0001000.pt",
    "5k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-5k" / "step_0005000.pt",
}


def load_tokenizer() -> spm.SentencePieceProcessor:
    processor = spm.SentencePieceProcessor()
    if not processor.load(str(TOKENIZER)):
        raise RuntimeError(f"could not load tokenizer: {TOKENIZER}")
    return processor


def build_source_bins() -> dict[str, dict]:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    for path in BIN_DIR.glob("*.bin"):
        path.unlink()
    sp = load_tokenizer()
    eos_id = sp.eos_id()
    handles: dict[str, object] = {}
    stats: dict[str, dict] = {}
    docs_path = next((path for path in DOC_CANDIDATES if path.exists()), None)
    if docs_path is None:
        raise FileNotFoundError(f"none of the document stores is readable: {DOC_CANDIDATES}")
    try:
        with docs_path.open("r", encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                record = json.loads(line)
                if record.get("meta", {}).get("split") != "val":
                    continue
                source_name = record["source"]
                if source_name not in handles:
                    path = BIN_DIR / f"{source_name}.bin"
                    handles[source_name] = path.open("wb")
                    stats[source_name] = {"documents": 0, "tokens": 0, "path": str(path.relative_to(ROOT))}
                ids = sp.encode(record["text"], out_type=int)
                ids.append(eos_id)
                expected = int(record.get("meta", {}).get("token_count", len(ids)))
                if len(ids) != expected:
                    raise RuntimeError(
                        f"token mismatch at line {line_number}: source={source_name} expected={expected} got={len(ids)}"
                    )
                np.asarray(ids, dtype=np.uint16).tofile(handles[source_name])
                stats[source_name]["documents"] += 1
                stats[source_name]["tokens"] += len(ids)
    finally:
        for handle in handles.values():
            handle.close()
    return dict(sorted(stats.items()))


def evaluate(stats: dict[str, dict], device: torch.device) -> dict[str, dict]:
    results: dict[str, dict] = {}
    for label, checkpoint in CHECKPOINTS.items():
        print(f"loading {label}: {checkpoint.relative_to(ROOT)}", flush=True)
        model, state = load_model(checkpoint, device)
        source_results = {}
        for source_name, item in stats.items():
            dataset = TokenDataset(
                ROOT / item["path"],
                block_size=512,
                name=f"{source_name} validation",
                sampling="random",
                seed=2027,
            )
            batches = min(64, max(1, dataset.num_blocks // 4))
            loss = estimate_loss(model, dataset, batch_size=4, device=device, batches=batches, seed=2027)
            source_results[source_name] = {
                **item,
                "eval_batches": batches,
                "evaluated_blocks": batches * 4,
                "val_loss": round(loss, 6),
            }
            print(f"{label} {source_name}: val_loss={loss:.4f} batches={batches}", flush=True)
        results[label] = {
            "checkpoint": str(checkpoint.relative_to(ROOT)),
            "step": state.get("step"),
            "sources": source_results,
        }
        del model, state
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return results


def main() -> None:
    configure_attention_backend("sdpa")
    if not torch.cuda.is_available():
        raise SystemExit("ROCm/CUDA device unavailable")
    device = torch.device("cuda")
    stats = build_source_bins()
    results = evaluate(stats, device)
    deltas = {
        source: round(results["5k"]["sources"][source]["val_loss"] - results["1k"]["sources"][source]["val_loss"], 6)
        for source in stats
    }
    payload = {
        "run_id": PREFIX,
        "scope": "source-specific fixed validation; no training performed",
        "source_bins": stats,
        "checkpoints": results,
        "delta_5k_minus_1k": deltas,
        "notes": [
            "Negative delta means the 5k checkpoint improved over 1k.",
            "Wikisource has no validation documents in v2.4.1 and is therefore absent.",
            "Small sources use fewer non-overlapping fixed blocks than large sources.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M v2.4.1 source-specific validation",
        "",
        "| source | docs | tokens | 1k val loss | 5k val loss | delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for source, item in stats.items():
        one = results["1k"]["sources"][source]["val_loss"]
        five = results["5k"]["sources"][source]["val_loss"]
        lines.append(
            f"| {source} | {item['documents']} | {item['tokens']:,} | {one:.4f} | {five:.4f} | {five - one:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Negative deltas mean improvement at 5k. Wikisource is train-only in v2.4.1, so it has no source-specific validation result.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
