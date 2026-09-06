#!/usr/bin/env python3
"""Compare v2.4.2 5k/10k and v2.4.1 10k on fixed v2.4.2 source bins."""
from __future__ import annotations

import json
from pathlib import Path

import torch

from eval_glyph100_stage2 import configure_attention_backend, load_model
from train import TokenDataset, estimate_loss


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_2_10k_gate_20260808"
SOURCE_INPUT = ROOT / "eval" / "glyph-100m" / "glyph100_v2_4_2_5k_gate_20260808_source_validation.json"
OUT_JSON = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.json"
OUT_MD = ROOT / "eval" / "glyph-100m" / f"{PREFIX}_source_validation.md"
CHECKPOINTS = {
    "v241_10k": ROOT / "checkpoints" / "glyph-100m-v2_4_1-10k" / "step_0010000.pt",
    "v242_5k": ROOT / "checkpoints" / "glyph-100m-v2_4_2-5k" / "step_0005000.pt",
    "v242_10k": ROOT / "checkpoints" / "glyph-100m-v2_4_2-10k" / "step_0010000.pt",
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
    source_payload = json.loads(SOURCE_INPUT.read_text(encoding="utf-8"))
    stats = source_payload["source_bins"]
    results = evaluate(stats, torch.device("cuda"))
    deltas = {
        source: {
            "v242_10k_minus_5k": round(
                results["v242_10k"]["sources"][source]["val_loss"]
                - results["v242_5k"]["sources"][source]["val_loss"],
                6,
            ),
            "v242_10k_minus_v241_10k": round(
                results["v242_10k"]["sources"][source]["val_loss"]
                - results["v241_10k"]["sources"][source]["val_loss"],
                6,
            ),
        }
        for source in stats
    }
    payload = {
        "run_id": PREFIX,
        "scope": "fixed v2.4.2 source-specific validation; no training performed",
        "source_bins": stats,
        "checkpoints": results,
        "deltas": deltas,
        "notes": [
            "Negative v242_10k_minus_5k means v2.4.2 improved between 5k and 10k.",
            "Negative v242_10k_minus_v241_10k means v2.4.2 has lower loss than v2.4.1 on the same source bin.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M v2.4.2 10k source-specific validation",
        "",
        "| source | docs | tokens | v2.4.1 10k | v2.4.2 5k | v2.4.2 10k | 10k-5k | v242-v241 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for source, item in stats.items():
        v241 = results["v241_10k"]["sources"][source]["val_loss"]
        five = results["v242_5k"]["sources"][source]["val_loss"]
        ten = results["v242_10k"]["sources"][source]["val_loss"]
        lines.append(
            f"| {source} | {item['documents']} | {item['tokens']:,} | {v241:.4f} | {five:.4f} | "
            f"{ten:.4f} | {ten - five:+.4f} | {ten - v241:+.4f} |"
        )
    lines.extend(["", "Negative deltas mean lower validation loss.", ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
