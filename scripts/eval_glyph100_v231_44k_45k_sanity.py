#!/usr/bin/env python3
"""Greedy and seed-sensitivity eval for Glyph-100M v2.3.1 44k vs 45k.

Inference only. Does not train or mutate checkpoints.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_glyph100_stage2 import (  # noqa: E402
    configure_attention_backend,
    generate_one,
    load_model,
    load_tokenizer,
    qualitative_note,
    read_jsonl,
)
from eval_glyph100_v231_broad import (  # noqa: E402
    EXPECTED_TOKENIZER_SHA,
    enrich_result,
    load_checkpoint_metadata,
    quality_score,
    sha256,
    summarize,
)


CHECKPOINTS = {
    "44k": ("checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt", 44000),
    "45k": ("checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt", 45000),
}
GREEDY_PRESETS = {
    "greedy_80": {"temperature": 0.0, "top_k": None, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 80},
    "greedy_120": {"temperature": 0.0, "top_k": None, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 120},
}
SEED_PRESET = {
    "current_normal_80": {"temperature": 0.8, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 80}
}
SEEDS = [2026061101, 2026061102, 2026061103, 2026061104, 2026061105]


def validate_checkpoint(label: str, path: Path, expected_step: int) -> dict:
    meta = load_checkpoint_metadata(path)
    errors = []
    if meta["variant"] != "glyph-100m":
        errors.append(f"variant={meta['variant']}")
    if int(meta["step"] or 0) != expected_step:
        errors.append(f"step={meta['step']} expected={expected_step}")
    if meta["dataset_name"] != "glyph100_v2_3_1":
        errors.append(f"dataset={meta['dataset_name']}")
    if meta["tokenizer_sha256"] != EXPECTED_TOKENIZER_SHA:
        errors.append(f"tokenizer_sha={meta['tokenizer_sha256']}")
    if int(meta["batch_size"] or 0) != 4:
        errors.append(f"batch_size={meta['batch_size']}")
    if int(meta["gradient_accumulation_steps"] or 0) != 8:
        errors.append(f"gradient_accumulation_steps={meta['gradient_accumulation_steps']}")
    if errors:
        raise SystemExit(f"{label} checkpoint validation failed: {'; '.join(errors)}")
    return meta


def select_seed_prompts(prompts: list[dict], per_category: int = 2) -> list[dict]:
    grouped = defaultdict(list)
    for row in prompts:
        grouped[row["category"]].append(row)
    selected = []
    for category in sorted(grouped):
        selected.extend(grouped[category][:per_category])
    return selected


def run_generations(
    checkpoint_rows: dict[str, tuple[Path, dict]],
    prompts: list[dict],
    presets: dict[str, dict],
    seeds: list[int],
    sp,
    device: torch.device,
) -> list[dict]:
    rows = []
    for label, (checkpoint, meta) in checkpoint_rows.items():
        print(f"loading {label}: {checkpoint.relative_to(ROOT)}", flush=True)
        model, state = load_model(checkpoint, device)
        for preset_name, settings in presets.items():
            print(f"  preset {preset_name}", flush=True)
            for seed in seeds:
                for prompt_index, prompt_row in enumerate(prompts):
                    result = generate_one(model, sp, device, prompt_row["prompt"], settings, seed + prompt_index)
                    result = enrich_result(result, prompt_row)
                    rows.append(
                        {
                            "checkpoint_label": label,
                            "checkpoint": str(checkpoint.relative_to(ROOT)),
                            "checkpoint_step": state.get("step") or state.get("current_step"),
                            "checkpoint_variant": state.get("variant"),
                            "prompt_id": prompt_row["id"],
                            "category": prompt_row["category"],
                            "prompt": prompt_row["prompt"],
                            "expected_behavior": prompt_row.get("expected_behavior", ""),
                            "preset": preset_name,
                            "settings": settings,
                            "seed": seed + prompt_index,
                            **result,
                        }
                    )
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return rows


def compare_pairs(rows: list[dict], baseline: str = "44k", candidate: str = "45k") -> list[dict]:
    by_key = {(row["prompt_id"], row["preset"], row.get("seed"), row["checkpoint_label"]): row for row in rows}
    out = []
    for row in rows:
        if row["checkpoint_label"] != candidate:
            continue
        base = by_key.get((row["prompt_id"], row["preset"], row.get("seed"), baseline))
        if not base:
            continue
        delta = row["quality_score"] - base["quality_score"]
        winner = candidate if delta >= 2 else baseline if delta <= -2 else "tie"
        out.append(
            {
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "preset": row["preset"],
                "seed": row.get("seed"),
                "score_44k": base["quality_score"],
                "score_45k": row["quality_score"],
                "delta": delta,
                "winner": winner,
                "44k_output": base["full_text"].strip(),
                "45k_output": row["full_text"].strip(),
                "44k_analysis": base["analysis"],
                "45k_analysis": row["analysis"],
                "44k_residue": base["residue_hits"],
                "45k_residue": row["residue_hits"],
            }
        )
    return out


def summarize_by(rows: list[dict], key: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return {name: summarize(values) for name, values in sorted(grouped.items())}


def seed_stats(rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["checkpoint_label"], row["prompt_id"])].append(row["quality_score"])
    per_prompt = {}
    for (checkpoint, prompt_id), values in grouped.items():
        per_prompt.setdefault(prompt_id, {})[checkpoint] = {
            "mean": round(statistics.mean(values), 4),
            "stdev": round(statistics.stdev(values), 4) if len(values) > 1 else 0.0,
            "values": values,
        }
    comparisons = []
    for prompt_id, data in per_prompt.items():
        if "44k" not in data or "45k" not in data:
            continue
        diff = data["45k"]["mean"] - data["44k"]["mean"]
        typical_noise = max(data["44k"]["stdev"], data["45k"]["stdev"])
        comparisons.append(
            {
                "prompt_id": prompt_id,
                "mean_44k": data["44k"]["mean"],
                "mean_45k": data["45k"]["mean"],
                "diff_45k_minus_44k": round(diff, 4),
                "stdev_44k": data["44k"]["stdev"],
                "stdev_45k": data["45k"]["stdev"],
                "typical_seed_noise": typical_noise,
                "diff_gt_noise": abs(diff) > typical_noise,
            }
        )
    all44 = [row["quality_score"] for row in rows if row["checkpoint_label"] == "44k"]
    all45 = [row["quality_score"] for row in rows if row["checkpoint_label"] == "45k"]
    return {
        "overall": {
            "mean_44k": round(statistics.mean(all44), 4),
            "mean_45k": round(statistics.mean(all45), 4),
            "diff_45k_minus_44k": round(statistics.mean(all45) - statistics.mean(all44), 4),
            "stdev_44k": round(statistics.stdev(all44), 4) if len(all44) > 1 else 0.0,
            "stdev_45k": round(statistics.stdev(all45), 4) if len(all45) > 1 else 0.0,
        },
        "per_prompt": comparisons,
        "diff_gt_noise_count": sum(1 for row in comparisons if row["diff_gt_noise"]),
    }


def render_greedy_md(path: Path, payload: dict) -> None:
    counts = Counter(row["winner"] for row in payload["comparisons"])
    lines = [
        "# Glyph-100M v2.3.1 44k vs 45k greedy eval",
        "",
        "Deterministic base LM continuation eval. `temperature=0.0`, no top-k/top-p sampling.",
        "",
        f"- prompts: `{payload['prompt_count']}`",
        f"- generations: `{len(payload['samples'])}`",
        "",
        "## Summary",
        "",
        f"- 45k wins: `{counts.get('45k', 0)}`",
        f"- 44k wins: `{counts.get('44k', 0)}`",
        f"- ties: `{counts.get('tie', 0)}`",
        "",
        "## By Checkpoint",
        "",
        "```json",
        json.dumps(payload["summary_by_checkpoint"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## By Preset",
        "",
        "```json",
        json.dumps(payload["summary_by_preset"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Largest 45k regressions",
        "",
    ]
    regressions = sorted(payload["comparisons"], key=lambda row: row["delta"])[:8]
    for row in regressions:
        lines.extend(
            [
                f"### {row['prompt_id']} · {row['preset']} · delta={row['delta']}",
                "",
                f"- 44k score: `{row['score_44k']}`",
                f"- 45k score: `{row['score_45k']}`",
                "",
                "**44k:**",
                "```text",
                row["44k_output"][:1200],
                "```",
                "**45k:**",
                "```text",
                row["45k_output"][:1200],
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def render_seed_md(path: Path, payload: dict) -> None:
    counts = Counter(row["winner"] for row in payload["comparisons"])
    stats = payload["seed_stats"]
    lines = [
        "# Glyph-100M v2.3.1 44k vs 45k seed sensitivity",
        "",
        "Stochastic eval: 20 broad prompts, `current_normal_80`, 5 seeds.",
        "",
        f"- 45k wins: `{counts.get('45k', 0)}`",
        f"- 44k wins: `{counts.get('44k', 0)}`",
        f"- ties: `{counts.get('tie', 0)}`",
        "",
        "## Overall seed stats",
        "",
        "```json",
        json.dumps(stats["overall"], ensure_ascii=False, indent=2),
        "```",
        "",
        f"- prompts where mean diff exceeds local seed noise: `{stats['diff_gt_noise_count']}/{len(stats['per_prompt'])}`",
        "",
        "## Per-prompt mean/stdev",
        "",
        "| prompt | mean 44k | mean 45k | diff | stdev 44k | stdev 45k | diff > noise |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in stats["per_prompt"]:
        lines.append(
            f"| {row['prompt_id']} | {row['mean_44k']} | {row['mean_45k']} | {row['diff_45k_minus_44k']} | "
            f"{row['stdev_44k']} | {row['stdev_45k']} | {row['diff_gt_noise']} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="eval/glyph-100m/v2_3_1_broad_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--greedy-json", default="eval/glyph-100m/v2_3_1_44k_45k_greedy_eval.json")
    parser.add_argument("--greedy-md", default="eval/glyph-100m/v2_3_1_44k_45k_greedy_eval.md")
    parser.add_argument("--seed-json", default="eval/glyph-100m/v2_3_1_44k_45k_seed_sensitivity.json")
    parser.add_argument("--seed-md", default="eval/glyph-100m/v2_3_1_44k_45k_seed_sensitivity.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    if tokenizer_hash != EXPECTED_TOKENIZER_SHA:
        raise SystemExit(f"tokenizer sha mismatch: {tokenizer_hash}")
    sp = load_tokenizer(tokenizer_path)
    prompts = read_jsonl(ROOT / args.prompts)
    seed_prompts = select_seed_prompts(prompts, per_category=2)

    checkpoint_rows = {}
    checkpoint_meta = {}
    for label, (rel, expected_step) in CHECKPOINTS.items():
        path = ROOT / rel
        meta = validate_checkpoint(label, path, expected_step)
        checkpoint_rows[label] = (path, meta)
        checkpoint_meta[label] = meta

    greedy_rows = run_generations(checkpoint_rows, prompts, GREEDY_PRESETS, [0], sp, device)
    greedy_comparisons = compare_pairs(greedy_rows)
    greedy_payload = {
        "mode": "greedy",
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "checkpoints": checkpoint_meta,
        "prompt_count": len(prompts),
        "presets": GREEDY_PRESETS,
        "samples": greedy_rows,
        "comparisons": greedy_comparisons,
        "summary_by_checkpoint": summarize_by(greedy_rows, "checkpoint_label"),
        "summary_by_preset": summarize_by(greedy_rows, "preset"),
    }

    seed_rows = run_generations(checkpoint_rows, seed_prompts, SEED_PRESET, SEEDS, sp, device)
    seed_comparisons = compare_pairs(seed_rows)
    seed_payload = {
        "mode": "seed_sensitivity",
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "checkpoints": checkpoint_meta,
        "prompt_count": len(seed_prompts),
        "seeds": SEEDS,
        "presets": SEED_PRESET,
        "samples": seed_rows,
        "comparisons": seed_comparisons,
        "summary_by_checkpoint": summarize_by(seed_rows, "checkpoint_label"),
        "seed_stats": seed_stats(seed_rows),
    }

    greedy_json = ROOT / args.greedy_json
    greedy_md = ROOT / args.greedy_md
    seed_json = ROOT / args.seed_json
    seed_md = ROOT / args.seed_md
    for path in [greedy_json, greedy_md, seed_json, seed_md]:
        path.parent.mkdir(parents=True, exist_ok=True)
    greedy_json.write_text(json.dumps(greedy_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    seed_json.write_text(json.dumps(seed_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_greedy_md(greedy_md, greedy_payload)
    render_seed_md(seed_md, seed_payload)
    print(
        "done: greedy_counts="
        f"{dict(Counter(row['winner'] for row in greedy_comparisons))} "
        "seed_counts="
        f"{dict(Counter(row['winner'] for row in seed_comparisons))}",
        flush=True,
    )


if __name__ == "__main__":
    main()
