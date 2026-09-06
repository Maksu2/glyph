#!/usr/bin/env python3
"""Evaluate the Glyph-100M v2.4.1 trajectory through 10k steps.

This is a base-LM continuation eval. It compares the planned 5k, 7.5k and
10k checkpoints and also regenerates the historical v2.3.1 10k prompt panel
for an equal-token-exposure comparison. It never starts training.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from eval_glyph100_stage2 import PRESETS as HISTORICAL_PRESETS
from eval_glyph100_stage2 import configure_attention_backend, generate_one, load_model, read_jsonl
from eval_glyph100_v241_5k_checkpoints import (
    PRESETS,
    checkpoint_contract,
    diagnostic,
    load_tokenizer,
    pairwise,
    summarize,
    write_samples_md,
)


ROOT = Path(__file__).resolve().parent.parent
PREFIX = "glyph100_v2_4_1_10k_eval_20260718"
CHECKPOINTS = {
    "5k": "checkpoints/glyph-100m-v2_4_1-5k/step_0005000.pt",
    "7.5k": "checkpoints/glyph-100m-v2_4_1-10k/step_0007500.pt",
    "10k": "checkpoints/glyph-100m-v2_4_1-10k/step_0010000.pt",
}
EXPECTED_STEPS = {"5k": 5000, "7.5k": 7500, "10k": 10000}
TRAJECTORY_PROMPTS = "eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl"
HISTORICAL_PROMPTS = "eval/glyph-100m/stage2_completion_prompts.jsonl"
HISTORICAL_SAMPLES = "eval/glyph-100m/stage2_samples.json"
TOKENIZER = "data/processed/tokenizer.model"
LOGS = (
    "logs/glyph-100m-v2_4_1-1k/train.log",
    "logs/glyph-100m-v2_4_1-5k/train.log",
    "logs/glyph-100m-v2_4_1-10k/train.log",
)


def validation_losses() -> list[dict]:
    import re

    pattern = re.compile(r"eval step=\s*(?P<step>\d+) \| val_loss=(?P<loss>[\d.]+)")
    rows: dict[int, dict] = {}
    for relative in LOGS:
        path = ROOT / relative
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = pattern.search(line)
            if match:
                step = int(match.group("step"))
                rows[step] = {
                    "step": step,
                    "val_loss": float(match.group("loss")),
                    "log": relative,
                }
    return [rows[step] for step in sorted(rows)]


def generate_panel(
    model,
    state: dict,
    tokenizer,
    device: torch.device,
    prompts: list[dict],
    presets: dict[str, dict],
    checkpoint_label: str,
    checkpoint: str,
    seed: int,
) -> list[dict]:
    rows = []
    for preset_name, settings in presets.items():
        for prompt_index, prompt in enumerate(prompts):
            result = generate_one(
                model,
                tokenizer,
                device,
                prompt["prompt"],
                settings,
                seed + prompt_index,
            )
            row = {
                "checkpoint_label": checkpoint_label,
                "checkpoint": checkpoint,
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
    return rows


def historical_rows() -> list[dict]:
    payload = json.loads((ROOT / HISTORICAL_SAMPLES).read_text(encoding="utf-8"))
    rows = []
    for old in payload["samples"]:
        row = {
            **old,
            "checkpoint_label": "v2.3.1-10k",
        }
        # The historical stage-2 schema predates explicit EOS accounting.
        row.setdefault("ended_by_eos", bool(row.get("analysis", {}).get("ended_by_eos", False)))
        row.setdefault("max_new_tokens", int(row["settings"]["max_new_tokens"]))
        row["diagnostic"] = diagnostic(row["new_text"], row)
        rows.append(row)
    return rows


def write_trajectory_md(path: Path, payload: dict) -> None:
    lines = [
        "# Glyph-100M v2.4.1: porównanie 5k / 7,5k / 10k",
        "",
        "Base-LM continuation eval, nie test asystenta. Wynik jakości jest heurystyką",
        "zakończeń, pętli i residue; próbki wymagają oceny semantycznej.",
        "",
        "## Trajektoria",
        "",
        "| checkpoint | avg score | median | natural | cutoff | repetition | pseudo-ency | web residue |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in CHECKPOINTS:
        item = payload["summaries"][label]["overall"]
        lines.append(
            f"| {label} | {item['avg_quality_score']:.3f} | {item['median_quality_score']:.3f} | "
            f"{item['natural_endings']}/{item['samples']} | {item['cutoff_like']}/{item['samples']} | "
            f"{item['repetition_samples']}/{item['samples']} | "
            f"{item['pseudo_ency_samples']}/{item['samples']} | "
            f"{item['web_residue_samples']}/{item['samples']} |"
        )
    lines.extend(
        [
            "",
            "## Pairwise",
            "",
            f"- 7,5k vs 5k: `{payload['pairwise']['5k_vs_7.5k']}`",
            f"- 10k vs 7,5k: `{payload['pairwise']['7.5k_vs_10k']}`",
            f"- 10k vs 5k: `{payload['pairwise']['5k_vs_10k']}`",
            f"- Heurystycznie najlepszy checkpoint: `{payload['heuristic_best_checkpoint']}`",
            "",
            "## Validation loss",
            "",
        ]
    )
    for row in payload["validation_losses"]:
        lines.append(f"- step `{row['step']}`: `{row['val_loss']:.4f}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_historical_md(path: Path, payload: dict, rows: list[dict]) -> None:
    lines = [
        "# Glyph-100M: v2.4.1 10k vs historyczne v2.3.1 10k",
        "",
        "Porównanie przy tej samej ekspozycji 163,84 mln tokenów, na zapisanym",
        "panelu 12 promptów i identycznych presetach/seeds z historycznego evala.",
        "",
        "## Podsumowanie",
        "",
        "| model | avg score | natural | cutoff | repetition | pseudo-ency | web residue |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("v2.3.1-10k", "v2.4.1-10k"):
        item = payload["summaries"][label]
        lines.append(
            f"| {label} | {item['avg_quality_score']:.3f} | "
            f"{item['natural_endings']}/{item['samples']} | "
            f"{item['cutoff_like']}/{item['samples']} | "
            f"{item['repetition_samples']}/{item['samples']} | "
            f"{item['pseudo_ency_samples']}/{item['samples']} | "
            f"{item['web_residue_samples']}/{item['samples']} |"
        )
    lines.extend(
        [
            "",
            f"Pairwise: `{payload['pairwise']}`",
            "",
            "## Próbki normal",
            "",
        ]
    )
    keyed = {
        (row["checkpoint_label"], row["prompt_id"], row["preset"]): row
        for row in rows
    }
    prompt_ids = sorted(
        {
            row["prompt_id"]
            for row in rows
            if row["checkpoint_label"] == "v2.4.1-10k" and row["preset"] == "normal"
        }
    )
    for prompt_id in prompt_ids:
        old = keyed[("v2.3.1-10k", prompt_id, "normal")]
        new = keyed[("v2.4.1-10k", prompt_id, "normal")]
        lines.extend(
            [
                f"### {prompt_id}",
                "",
                f"**Prompt:** `{new['prompt']}`",
                "",
                f"**v2.3.1 10k, score {old['diagnostic']['quality_score']}:**",
                "",
                "```text",
                old["new_text"].strip(),
                "```",
                "",
                f"**v2.4.1 10k, score {new['diagnostic']['quality_score']}:**",
                "",
                "```text",
                new["new_text"].strip(),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda", choices=["cpu", "cuda"])
    parser.add_argument("--attention-backend", default="sdpa", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260717)
    args = parser.parse_args()

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but unavailable")
    configure_attention_backend(args.attention_backend)
    tokenizer = load_tokenizer(ROOT / TOKENIZER)
    prompts = read_jsonl(ROOT / TRAJECTORY_PROMPTS)
    rows: list[dict] = []
    contracts: dict[str, dict] = {}

    for label, relative in CHECKPOINTS.items():
        print(f"loading {label}: {relative}", flush=True)
        model, state = load_model(ROOT / relative, device)
        contracts[label] = checkpoint_contract(state, EXPECTED_STEPS[label])
        if not contracts[label]["valid"]:
            raise SystemExit(f"checkpoint contract failed for {label}: {contracts[label]}")
        rows.extend(
            generate_panel(
                model,
                state,
                tokenizer,
                device,
                prompts,
                PRESETS,
                label,
                relative,
                args.seed,
            )
        )
        del model, state
        if device.type == "cuda":
            torch.cuda.empty_cache()
        print(f"completed {label}", flush=True)

    summaries = {
        label: {
            "overall": summarize([row for row in rows if row["checkpoint_label"] == label]),
            "by_preset": {
                preset: summarize(
                    [
                        row
                        for row in rows
                        if row["checkpoint_label"] == label and row["preset"] == preset
                    ]
                )
                for preset in PRESETS
            },
        }
        for label in CHECKPOINTS
    }
    pairwise_results = {
        "5k_vs_7.5k": pairwise(rows, "5k", "7.5k"),
        "7.5k_vs_10k": pairwise(rows, "7.5k", "10k"),
        "5k_vs_10k": pairwise(rows, "5k", "10k"),
    }
    trajectory_payload = {
        "run_id": PREFIX,
        "scope": "v2.4.1 base-LM trajectory; no training performed",
        "prompts": len(prompts),
        "presets": PRESETS,
        "checkpoints": CHECKPOINTS,
        "checkpoint_contracts": contracts,
        "validation_losses": validation_losses(),
        "summaries": summaries,
        "pairwise": pairwise_results,
        "heuristic_best_checkpoint": max(
            CHECKPOINTS,
            key=lambda label: summaries[label]["overall"]["avg_quality_score"],
        ),
        "methodology_note": "Diagnostic heuristic only; manual semantic review is required.",
        "samples": rows,
    }

    eval_dir = ROOT / "eval" / "glyph-100m"
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / f"{PREFIX}_samples.json").write_text(
        json.dumps(trajectory_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_samples_md(eval_dir / f"{PREFIX}_samples.md", rows)
    compact = {key: value for key, value in trajectory_payload.items() if key != "samples"}
    (eval_dir / f"{PREFIX}_comparison.json").write_text(
        json.dumps(compact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_trajectory_md(eval_dir / f"{PREFIX}_comparison.md", compact)

    print("generating equal-exposure historical comparison", flush=True)
    historical_prompts = read_jsonl(ROOT / HISTORICAL_PROMPTS)
    model, state = load_model(ROOT / CHECKPOINTS["10k"], device)
    new_historical = generate_panel(
        model,
        state,
        tokenizer,
        device,
        historical_prompts,
        HISTORICAL_PRESETS,
        "v2.4.1-10k",
        CHECKPOINTS["10k"],
        20260531,
    )
    del model, state
    if device.type == "cuda":
        torch.cuda.empty_cache()
    old_historical = historical_rows()
    historical_all = old_historical + new_historical
    historical_payload = {
        "run_id": PREFIX,
        "scope": "equal-token-exposure comparison using the historical stage2 panel; no training performed",
        "token_exposure_each": 163_840_000,
        "prompts": len(historical_prompts),
        "presets": HISTORICAL_PRESETS,
        "checkpoints": {
            "v2.3.1-10k": "stored eval/glyph-100m/stage2_samples.json",
            "v2.4.1-10k": CHECKPOINTS["10k"],
        },
        "summaries": {
            label: summarize(
                [row for row in historical_all if row["checkpoint_label"] == label]
            )
            for label in ("v2.3.1-10k", "v2.4.1-10k")
        },
        "pairwise": pairwise(historical_all, "v2.3.1-10k", "v2.4.1-10k"),
        "samples": historical_all,
    }
    (eval_dir / f"{PREFIX}_vs_v231_10k.json").write_text(
        json.dumps(historical_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_historical_md(
        eval_dir / f"{PREFIX}_vs_v231_10k.md",
        historical_payload,
        historical_all,
    )
    print(f"wrote outputs with prefix {PREFIX}", flush=True)


if __name__ == "__main__":
    main()
