#!/usr/bin/env python3
"""Run the matched post-training quality gate for Glyph-100M v2.4.2 at 10k."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from eval_glyph100_stage2 import configure_attention_backend, generate_one, load_model, read_jsonl
from eval_glyph100_v242_5k_gate import (
    PRESETS,
    checkpoint_contract,
    diagnostic,
    load_tokenizer,
    pairwise,
    summarize,
)


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_2_10k_gate_20260808"
CHECKPOINTS = {
    "v241_10k": {
        "path": "checkpoints/glyph-100m-v2_4_1-10k/step_0010000.pt",
        "step": 10000,
        "dataset": "glyph100_dataset_v2_4_1_core",
    },
    "v242_5k": {
        "path": "checkpoints/glyph-100m-v2_4_2-5k/step_0005000.pt",
        "step": 5000,
        "dataset": "glyph100_dataset_v2_4_2_core",
    },
    "v242_10k": {
        "path": "checkpoints/glyph-100m-v2_4_2-10k/step_0010000.pt",
        "step": 10000,
        "dataset": "glyph100_dataset_v2_4_2_core",
    },
}


def write_samples_md(path: Path, rows: list[dict]) -> None:
    lines = [
        "# Glyph-100M v2.4.2 10k quality-gate samples",
        "",
        "Matched base-LM continuation eval. This is not an assistant benchmark.",
        "",
    ]
    for row in rows:
        diag = row["diagnostic"]
        lines.extend(
            [
                f"## {row['checkpoint_label']} - {row['prompt_id']} - {row['preset']}",
                "",
                f"**Prompt:** `{row['prompt']}`",
                "",
                "```text",
                row["full_text"],
                "```",
                "",
                f"Score `{diag['quality_score']}`; natural `{diag['natural_ending']}`; "
                f"cutoff `{diag['cutoff_like']}`; repetition `{diag['repetition']}`; "
                f"pseudo-ency `{bool(diag['pseudo_ency_hits'])}`; "
                f"web `{bool(diag['web_residue_hits'])}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prompts",
        default="eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl",
    )
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    parser.add_argument("--attention-backend", default="sdpa", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but unavailable")
    configure_attention_backend(args.attention_backend)
    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer = load_tokenizer(ROOT / args.tokenizer)
    rows: list[dict] = []
    contracts: dict[str, dict] = {}

    for label, spec in CHECKPOINTS.items():
        print(f"loading {label}: {spec['path']}", flush=True)
        model, state = load_model(ROOT / spec["path"], device)
        contracts[label] = checkpoint_contract(state, spec)
        if not contracts[label]["valid"]:
            raise SystemExit(f"checkpoint contract failed for {label}: {contracts[label]}")
        for preset_name, settings in PRESETS.items():
            for prompt_index, prompt in enumerate(prompts):
                result = generate_one(
                    model,
                    tokenizer,
                    device,
                    prompt["prompt"],
                    settings,
                    args.seed + prompt_index,
                )
                row = {
                    "checkpoint_label": label,
                    "checkpoint": spec["path"],
                    "checkpoint_step": state.get("step"),
                    "prompt_id": prompt["id"],
                    "category": prompt["category"],
                    "expected": prompt.get("expected"),
                    "preset": preset_name,
                    "settings": settings,
                    **result,
                }
                row["diagnostic"] = diagnostic(row["new_text"], row)
                rows.append(row)
        del model, state
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"completed {label}: {len(prompts) * len(PRESETS)} samples", flush=True)

    summaries = {}
    for label in CHECKPOINTS:
        label_rows = [row for row in rows if row["checkpoint_label"] == label]
        summaries[label] = {
            "overall": summarize(label_rows),
            "by_preset": {
                preset: summarize([row for row in label_rows if row["preset"] == preset])
                for preset in PRESETS
            },
        }
    pairwise_results = {
        "v242_5k_vs_v242_10k": pairwise(rows, "v242_5k", "v242_10k"),
        "v241_10k_vs_v242_10k": pairwise(rows, "v241_10k", "v242_10k"),
    }
    best_label = max(CHECKPOINTS, key=lambda label: summaries[label]["overall"]["avg_quality_score"])
    payload = {
        "run_id": PREFIX,
        "scope": "matched base-LM continuation quality gate; no training performed",
        "prompts": len(prompts),
        "presets": PRESETS,
        "checkpoints": CHECKPOINTS,
        "checkpoint_contracts": contracts,
        "summaries": summaries,
        "pairwise": pairwise_results,
        "heuristic_best_checkpoint": best_label,
        "methodology_note": "Scores are deterministic diagnostics; semantic samples require manual review.",
        "samples": rows,
    }

    eval_dir = ROOT / "eval" / "glyph-100m"
    eval_dir.mkdir(parents=True, exist_ok=True)
    samples_json = eval_dir / f"{PREFIX}_samples.json"
    samples_md = eval_dir / f"{PREFIX}_samples.md"
    comparison_json = eval_dir / f"{PREFIX}_comparison.json"
    comparison_md = eval_dir / f"{PREFIX}_comparison.md"
    samples_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_samples_md(samples_md, rows)
    comparison_json.write_text(
        json.dumps({key: value for key, value in payload.items() if key != "samples"}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Glyph-100M v2.4.2 10k matched quality gate",
        "",
        "| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in CHECKPOINTS:
        item = summaries[label]["overall"]
        lines.append(
            f"| {label} | {item['avg_quality_score']:.3f} | {item['median_quality_score']:.3f} | "
            f"{item['natural_endings']}/{item['samples']} | {item['cutoff_like']}/{item['samples']} | "
            f"{item['repetition_samples']}/{item['samples']} | {item['pseudo_ency_samples']}/{item['samples']} | "
            f"{item['web_residue_samples']}/{item['samples']} |"
        )
    lines.extend(
        [
            "",
            "## Pairwise heuristic",
            "",
            f"- v2.4.2 5k vs 10k: `{pairwise_results['v242_5k_vs_v242_10k']}`",
            f"- v2.4.1 10k vs v2.4.2 10k: `{pairwise_results['v241_10k_vs_v242_10k']}`",
            f"- heuristic best checkpoint: `{best_label}`",
            "",
            "The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is required.",
            "",
        ]
    )
    comparison_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote consolidated outputs with prefix {PREFIX}", flush=True)


if __name__ == "__main__":
    main()
