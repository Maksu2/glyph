#!/usr/bin/env python3
"""Matched trajectory eval for Glyph-100M v2.4.2: 10k vs 12.5k vs 15k.

Base-LM continuation eval on IDENTICAL prompts, presets and seeds for every
checkpoint. Optionally adds the historical v2.3.1 44k checkpoint on the same
panel (``--with-v231-44k``) for a same-method cross-branch comparison.

Methodology mirrors scripts/eval_glyph100_v242_10k_gate.py:
  prompts: eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl (20)
  presets: conservative {temp 0.6, top_k 30} / normal {temp 0.8, top_k 40},
           max_new_tokens 80 (from eval_glyph100_v242_5k_gate.PRESETS)
  seed: 20260717 + prompt_index (identical for every checkpoint)
  scoring: deterministic diagnostic() heuristic (endings, loops, residue);
           semantic/factual review of samples is manual and mandatory.

This script never starts training. It loads one checkpoint at a time and
empties the CUDA cache between checkpoints (same VRAM-safe pattern as the
5k/10k gates; previously ran fine on RX 5500 XT).

Run from the repo root, e.g.:
  cd /home/maksu/ai-model && .venv/bin/python scripts/eval_glyph100_v242_15k_trajectory.py --device cuda
  cd /home/maksu/ai-model && .venv/bin/python scripts/eval_glyph100_v242_15k_trajectory.py --device cuda --with-v231-44k
Use --device cpu only as a slow fallback.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from eval_glyph100_stage2 import configure_attention_backend, generate_one, load_model, read_jsonl
from eval_glyph100_v242_5k_gate import (
    PRESETS,
    TOKENIZER_SHA256,
    checkpoint_contract,
    diagnostic,
    load_tokenizer,
    pairwise,
    summarize,
)


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_2_15k_trajectory_20260905"
PROMPTS = "eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl"
TOKENIZER = "data/processed/tokenizer.model"
SEED = 20260717
V242_DATASET = "glyph100_dataset_v2_4_2_core"

TRAJECTORY = {
    "v242_10k": {
        "path": "checkpoints/glyph-100m-v2_4_2-10k/step_0010000.pt",
        "step": 10000,
        "dataset": V242_DATASET,
    },
    "v242_12_5k": {
        "path": "checkpoints/glyph-100m-v2_4_2-15k/step_0012500.pt",
        "step": 12500,
        "dataset": V242_DATASET,
    },
    "v242_15k": {
        "path": "checkpoints/glyph-100m-v2_4_2-15k/step_0015000.pt",
        "step": 15000,
        "dataset": V242_DATASET,
    },
}
V231_44K = {
    "path": "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
    "step": 44000,
    "dataset": "glyph100_dataset_v2_3_1",
}


def v231_contract(state: dict) -> dict:
    """Relaxed contract for the historical branch: identity + tokenizer only.

    The strict contract() requires the v2.4.2 dataset, batch/accum and full
    optimizer/scheduler/sampler state, which must NOT be demanded from a
    checkpoint trained on another corpus. For generation-only comparison it
    is enough that the step, variant and tokenizer match. The v2.3.1 dataset
    name is accepted in both recorded spellings ("glyph100_dataset_v2_3_1"
    and "glyph100_v2_3_1"), because repo records use both.
    """
    contract = {
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "dataset_name": state.get("dataset_name"),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
    }
    contract["valid"] = all(
        (
            contract["step"] == V231_44K["step"],
            contract["current_step"] == V231_44K["step"],
            contract["variant"] == "glyph-100m",
            contract["dataset_name"] in (V231_44K["dataset"], "glyph100_v2_3_1"),
            contract["tokenizer_sha256"] == TOKENIZER_SHA256,
        )
    )
    return contract


def write_samples_md(path: Path, rows: list[dict]) -> None:
    lines = [
        "# Glyph-100M v2.4.2 10k / 12.5k / 15k matched trajectory samples",
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
    parser.add_argument("--prompts", default=PROMPTS)
    parser.add_argument("--tokenizer", default=TOKENIZER)
    parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    parser.add_argument("--attention-backend", default="sdpa", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--with-v231-44k",
        action="store_true",
        help="Also evaluate the historical v2.3.1 44k best on the same panel.",
    )
    args = parser.parse_args()

    prefix = PREFIX + ("_with_v23144k" if args.with_v231_44k else "")
    checkpoints: dict[str, dict] = dict(TRAJECTORY)
    if args.with_v231_44k:
        checkpoints["v231_44k"] = V231_44K

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but unavailable")
    configure_attention_backend(args.attention_backend)
    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer = load_tokenizer(ROOT / args.tokenizer)
    rows: list[dict] = []
    contracts: dict[str, dict] = {}

    for label, spec in checkpoints.items():
        print(f"loading {label}: {spec['path']}", flush=True)
        model, state = load_model(ROOT / spec["path"], device)
        if label == "v231_44k":
            contracts[label] = v231_contract(state)
        else:
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

    trajectory_labels = list(TRAJECTORY)
    summaries = {}
    for label in checkpoints:
        label_rows = [row for row in rows if row["checkpoint_label"] == label]
        summaries[label] = {
            "overall": summarize(label_rows),
            "by_preset": {
                preset: summarize([row for row in label_rows if row["preset"] == preset])
                for preset in PRESETS
            },
        }
    pairwise_results = {
        "v242_10k_vs_v242_12_5k": pairwise(rows, "v242_10k", "v242_12_5k"),
        "v242_12_5k_vs_v242_15k": pairwise(rows, "v242_12_5k", "v242_15k"),
        "v242_10k_vs_v242_15k": pairwise(rows, "v242_10k", "v242_15k"),
    }
    if args.with_v231_44k:
        for label in trajectory_labels:
            pairwise_results[f"{label}_vs_v231_44k"] = pairwise(rows, label, "v231_44k")
    best_label = max(trajectory_labels, key=lambda label: summaries[label]["overall"]["avg_quality_score"])
    payload = {
        "run_id": prefix,
        "scope": "matched base-LM continuation trajectory eval; no training performed",
        "prompts": len(prompts),
        "prompts_file": args.prompts,
        "seed": args.seed,
        "presets": PRESETS,
        "checkpoints": checkpoints,
        "checkpoint_contracts": contracts,
        "summaries": summaries,
        "pairwise": pairwise_results,
        "heuristic_best_v242": best_label,
        "methodology_note": (
            "Scores are deterministic diagnostics (endings, loops, residue); "
            "semantic and factual sample review is manual and mandatory before "
            "crowning a canonical best. Cross-branch heuristic scores share the "
            "panel and seeds but not the training corpus, so they rank "
            "generation behaviour only, never val loss."
        ),
        "samples": rows,
    }

    eval_dir = ROOT / "eval" / "glyph-100m"
    eval_dir.mkdir(parents=True, exist_ok=True)
    samples_json = eval_dir / f"{prefix}_samples.json"
    samples_md = eval_dir / f"{prefix}_samples.md"
    comparison_json = eval_dir / f"{prefix}_comparison.json"
    comparison_md = eval_dir / f"{prefix}_comparison.md"
    samples_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_samples_md(samples_md, rows)
    comparison_json.write_text(
        json.dumps({key: value for key, value in payload.items() if key != "samples"}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Glyph-100M v2.4.2 matched trajectory: 10k vs 12.5k vs 15k",
        "",
        "| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in checkpoints:
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
        ]
    )
    for name, result in pairwise_results.items():
        lines.append(f"- {name}: `{result}`")
    lines.extend(
        [
            f"- heuristic best v2.4.2: `{best_label}`",
            "",
            "The score is a deterministic diagnostic for endings, loops and residue. Manual semantic review is required.",
            "",
        ]
    )
    comparison_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote consolidated outputs with prefix {prefix}", flush=True)


if __name__ == "__main__":
    main()
