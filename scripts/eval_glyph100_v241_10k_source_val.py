#!/usr/bin/env python3
"""Source-specific validation for Glyph-100M v2.4.1 at 5k/7.5k/10k."""
from __future__ import annotations

import json
from pathlib import Path

import torch

from eval_glyph100_stage2 import configure_attention_backend, load_model
from eval_glyph100_v241_5k_source_val import build_source_bins
from train import TokenDataset, estimate_loss


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_1_10k_eval_20260718"
BIN_DIR = ROOT / "eval" / "glyph-100m" / "glyph100_v2_4_1_5k_eval_20260717_source_val_bins"
OUT_JSON = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.json"
OUT_MD = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.md"
CHECKPOINTS = {
    "5k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-5k" / "step_0005000.pt",
    "7.5k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-10k" / "step_0007500.pt",
    "10k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-10k" / "step_0010000.pt",
}


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
            loss = estimate_loss(
                model,
                dataset,
                batch_size=4,
                device=device,
                batches=batches,
                seed=2027,
            )
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
        source: {
            "7.5k_minus_5k": round(
                results["7.5k"]["sources"][source]["val_loss"]
                - results["5k"]["sources"][source]["val_loss"],
                6,
            ),
            "10k_minus_7.5k": round(
                results["10k"]["sources"][source]["val_loss"]
                - results["7.5k"]["sources"][source]["val_loss"],
                6,
            ),
            "10k_minus_5k": round(
                results["10k"]["sources"][source]["val_loss"]
                - results["5k"]["sources"][source]["val_loss"],
                6,
            ),
        }
        for source in stats
    }
    payload = {
        "run_id": PREFIX,
        "scope": "source-specific fixed validation; no training performed",
        "source_bins": stats,
        "checkpoints": results,
        "deltas": deltas,
        "notes": [
            "Negative delta means improvement.",
            "Wikisource has no validation documents in v2.4.1 and is absent.",
            "The source panel and seeds match the earlier v2.4.1 1k/5k evaluation.",
        ],
    }
    OUT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Glyph-100M v2.4.1 source validation at 10k",
        "",
        "| source | docs | tokens | 5k | 7.5k | 10k | 10k - 5k |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for source, item in stats.items():
        five = results["5k"]["sources"][source]["val_loss"]
        seven = results["7.5k"]["sources"][source]["val_loss"]
        ten = results["10k"]["sources"][source]["val_loss"]
        lines.append(
            f"| {source} | {item['documents']} | {item['tokens']:,} | "
            f"{five:.4f} | {seven:.4f} | {ten:.4f} | {ten - five:+.4f} |"
        )
    lines.extend(
        [
            "",
            "Negative deltas mean improvement. Wikisource remains train-only because",
            "the upstream data does not preserve a safe parent-work split.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
