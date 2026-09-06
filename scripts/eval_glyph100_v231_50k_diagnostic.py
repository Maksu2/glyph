#!/usr/bin/env python3
"""Diagnostic eval for Glyph-100M v2.3.1 44k/45k/50k.

Inference only. Does not train and does not mutate checkpoints.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_glyph100_stage2 import (  # noqa: E402
    configure_attention_backend,
    generate_one,
    load_model,
    load_tokenizer,
    read_jsonl,
)
from eval_glyph100_v231_broad import (  # noqa: E402
    EXPECTED_TOKENIZER_SHA,
    PRESETS,
    compact_sample,
    enrich_result,
    load_checkpoint_metadata,
    sample_block,
    sha256,
    summarize,
)


CHECKPOINTS = {
    "44k": ("checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt", 44000),
    "45k": ("checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt", 45000),
    "50k": ("checkpoints/glyph-100m-v2_3_1-50k/latest.pt", 50000),
}
SEED_PRESET = {
    "current_normal_80": {"temperature": 0.8, "top_k": 40, "top_p": 1.0, "repetition_penalty": 1.0, "max_new_tokens": 80}
}
SEEDS = [2026061101, 2026061102, 2026061103, 2026061104, 2026061105]


def validate_checkpoint(label: str, path: Path, expected_step: int) -> dict:
    if not path.exists():
        raise SystemExit(f"{label} checkpoint missing: {path}")
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
    for label, (checkpoint, _meta) in checkpoint_rows.items():
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


def summarize_by(rows: list[dict], key: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return {name: summarize(values) for name, values in sorted(grouped.items())}


def compare_pair(rows: list[dict], baseline: str, candidate: str) -> list[dict]:
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
                "baseline": baseline,
                "candidate": candidate,
                "prompt_id": row["prompt_id"],
                "category": row["category"],
                "preset": row["preset"],
                "seed": row.get("seed"),
                "score_baseline": base["quality_score"],
                "score_candidate": row["quality_score"],
                "delta": delta,
                "winner": winner,
                "baseline_output": base["full_text"].strip(),
                "candidate_output": row["full_text"].strip(),
                "baseline_analysis": base["analysis"],
                "candidate_analysis": row["analysis"],
                "baseline_residue": base["residue_hits"],
                "candidate_residue": row["residue_hits"],
            }
        )
    return out


def winner_counts(comparisons: list[dict]) -> dict:
    return dict(Counter(row["winner"] for row in comparisons))


def seed_stats(rows: list[dict], baseline: str, candidate: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["checkpoint_label"], row["prompt_id"])].append(row["quality_score"])
    per_prompt = []
    for prompt_id in sorted({row["prompt_id"] for row in rows}):
        base = grouped.get((baseline, prompt_id), [])
        cand = grouped.get((candidate, prompt_id), [])
        if not base or not cand:
            continue
        base_mean = statistics.mean(base)
        cand_mean = statistics.mean(cand)
        base_stdev = statistics.stdev(base) if len(base) > 1 else 0.0
        cand_stdev = statistics.stdev(cand) if len(cand) > 1 else 0.0
        noise = max(base_stdev, cand_stdev)
        per_prompt.append(
            {
                "prompt_id": prompt_id,
                f"mean_{baseline}": round(base_mean, 4),
                f"mean_{candidate}": round(cand_mean, 4),
                f"diff_{candidate}_minus_{baseline}": round(cand_mean - base_mean, 4),
                f"stdev_{baseline}": round(base_stdev, 4),
                f"stdev_{candidate}": round(cand_stdev, 4),
                "typical_seed_noise": round(noise, 4),
                "diff_gt_noise": abs(cand_mean - base_mean) > noise,
            }
        )
    base_all = [row["quality_score"] for row in rows if row["checkpoint_label"] == baseline]
    cand_all = [row["quality_score"] for row in rows if row["checkpoint_label"] == candidate]
    return {
        "baseline": baseline,
        "candidate": candidate,
        "overall": {
            f"mean_{baseline}": round(statistics.mean(base_all), 4),
            f"mean_{candidate}": round(statistics.mean(cand_all), 4),
            f"diff_{candidate}_minus_{baseline}": round(statistics.mean(cand_all) - statistics.mean(base_all), 4),
            f"stdev_{baseline}": round(statistics.stdev(base_all), 4),
            f"stdev_{candidate}": round(statistics.stdev(cand_all), 4),
        },
        "per_prompt": per_prompt,
        "diff_gt_noise_count": sum(1 for row in per_prompt if row["diff_gt_noise"]),
    }


def render_table(title: str, summary: dict, order: list[str]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| item | avg_q | median_q | rep | natural | cutoff | pseudo | web | wiki | drift | overlap |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key in order:
        row = summary[key]
        count = row["count"]
        lines.append(
            f"| {key} | {row['avg_quality_score']} | {row['median_quality_score']} | "
            f"{row['repetition_samples']}/{count} | {row['natural_endings']}/{count} | "
            f"{row['cutoff_like_samples']}/{count} | {row['pseudo_ency_samples']}/{count} | "
            f"{row['web_residue_samples']}/{count} | {row['wiki_residue_samples']}/{count} | "
            f"{row['topic_drift_samples']}/{count} | {row['avg_topic_overlap']} |"
        )
    lines.append("")
    return lines


def compact_comparison(row: dict) -> dict:
    return {
        "prompt_id": row["prompt_id"],
        "category": row["category"],
        "preset": row["preset"],
        "delta": row["delta"],
        "winner": row["winner"],
        "score_baseline": row["score_baseline"],
        "score_candidate": row["score_candidate"],
        "baseline_output": row["baseline_output"][:1200],
        "candidate_output": row["candidate_output"][:1200],
        "baseline_residue": row["baseline_residue"],
        "candidate_residue": row["candidate_residue"],
    }


def render_eval_md(path: Path, payload: dict) -> None:
    lines = [
        "# Glyph-100M v2.3.1 44k / 45k / 50k diagnostic eval",
        "",
        "Base LM continuation eval. This is not an assistant/instruction eval.",
        "",
        f"- prompts: `{payload['prompt_count']}`",
        f"- presets: `{len(payload['presets'])}`",
        f"- generations: `{len(payload['samples'])}`",
        "",
    ]
    lines.extend(render_table("Checkpoint Summary", payload["summary_by_checkpoint"], payload["checkpoint_order"]))
    lines.extend(render_table("Preset Summary", payload["summary_by_preset"], list(PRESETS)))
    lines.extend(
        [
            "## Pairwise Wins",
            "",
            "| comparison | candidate wins | baseline wins | ties |",
            "|---|---:|---:|---:|",
        ]
    )
    for name, counts in payload["pairwise_wins"].items():
        baseline, candidate = name.split("_vs_")
        lines.append(f"| {candidate} vs {baseline} | {counts.get(candidate, 0)} | {counts.get(baseline, 0)} | {counts.get('tie', 0)} |")
    lines.extend(["", "## Largest 50k regressions vs 44k", ""])
    for row in payload["largest_50k_regressions_vs_44k"]:
        lines.extend(
            [
                f"### {row['prompt_id']} · {row['preset']} · delta={row['delta']}",
                "",
                f"- 44k score: `{row['score_baseline']}`",
                f"- 50k score: `{row['score_candidate']}`",
                "",
                "**44k:**",
                "```text",
                row["baseline_output"],
                "```",
                "**50k:**",
                "```text",
                row["candidate_output"],
                "```",
                "",
            ]
        )
    lines.extend(["## Best 50k samples", ""])
    for row in payload["best_50k_samples"]:
        lines.extend(sample_block(row))
    lines.extend(["## Worst 50k samples", ""])
    for row in payload["worst_50k_samples"]:
        lines.extend(sample_block(row))
    path.write_text("\n".join(lines), encoding="utf-8")


def render_seed_md(path: Path, payload: dict) -> None:
    lines = [
        "# Glyph-100M v2.3.1 50k seed sensitivity",
        "",
        "Stochastic eval: 20 broad prompts, `current_normal_80`, 5 seeds.",
        "",
    ]
    for name, stats in payload["seed_stats"].items():
        counts = payload["pairwise_wins"][name]
        baseline, candidate = name.split("_vs_")
        lines.extend(
            [
                f"## {candidate} vs {baseline}",
                "",
                f"- {candidate} wins: `{counts.get(candidate, 0)}`",
                f"- {baseline} wins: `{counts.get(baseline, 0)}`",
                f"- ties: `{counts.get('tie', 0)}`",
                "",
                "```json",
                json.dumps(stats["overall"], ensure_ascii=False, indent=2),
                "```",
                "",
                f"- prompts where mean diff exceeds local seed noise: `{stats['diff_gt_noise_count']}/20`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def choose_verdict(payload: dict, seed_payload: dict) -> dict:
    summary = payload["summary_by_checkpoint"]
    best = max(summary.items(), key=lambda item: item[1]["avg_quality_score"])[0]
    q44 = summary["44k"]["avg_quality_score"]
    q45 = summary["45k"]["avg_quality_score"]
    q50 = summary["50k"]["avg_quality_score"]
    wins_50_vs_44 = payload["pairwise_wins"]["44k_vs_50k"]
    wins_50_vs_45 = payload["pairwise_wins"]["45k_vs_50k"]
    if best == "50k" and wins_50_vs_44.get("50k", 0) > wins_50_vs_44.get("44k", 0):
        return {"verdict": "A", "label": "50k zostaje best practical checkpoint", "reason": "50k wins aggregate quality and pairwise comparison vs 44k."}
    if best == "44k" or q44 >= max(q45, q50):
        return {"verdict": "B", "label": "44k zostaje best practical checkpoint", "reason": "44k remains strongest by aggregate quality or is not clearly beaten by 50k."}
    if best == "45k" or q45 >= max(q44, q50):
        return {"verdict": "C", "label": "45k zostaje best practical checkpoint", "reason": "45k is strongest by aggregate quality in this eval."}
    if abs(q50 - q44) < 0.25 and abs(q50 - q45) < 0.25:
        return {"verdict": "D", "label": "różnice są w granicach sampling noise", "reason": "Aggregate quality scores are close."}
    return {"verdict": "E", "label": "stop pretraining, przejść do SFT smoke test", "reason": "50k does not provide a clean practical win."}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompts", default="eval/glyph-100m/v2_3_1_broad_prompts.jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--attention-backend", default="math", choices=["sdpa", "math", "manual"])
    parser.add_argument("--seed", type=int, default=20260611)
    parser.add_argument("--eval-json", default="eval/glyph-100m/v2_3_1_44k_45k_50k_eval.json")
    parser.add_argument("--eval-md", default="eval/glyph-100m/v2_3_1_44k_45k_50k_eval.md")
    parser.add_argument("--seed-json", default="eval/glyph-100m/v2_3_1_50k_seed_sensitivity.json")
    parser.add_argument("--seed-md", default="eval/glyph-100m/v2_3_1_50k_seed_sensitivity.md")
    args = parser.parse_args()

    device = torch.device("cuda" if args.device == "auto" and torch.cuda.is_available() else args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA/HIP requested but torch.cuda.is_available() is false")
    configure_attention_backend(args.attention_backend)

    prompts = read_jsonl(ROOT / args.prompts)
    tokenizer_path = ROOT / args.tokenizer
    tokenizer_hash = sha256(tokenizer_path)
    if tokenizer_hash != EXPECTED_TOKENIZER_SHA:
        raise SystemExit(f"tokenizer sha mismatch: {tokenizer_hash}")
    sp = load_tokenizer(tokenizer_path)

    checkpoint_rows = {}
    checkpoint_meta = {}
    for label, (rel, expected_step) in CHECKPOINTS.items():
        path = ROOT / rel
        meta = validate_checkpoint(label, path, expected_step)
        checkpoint_rows[label] = (path, meta)
        checkpoint_meta[label] = meta

    broad_samples = run_generations(checkpoint_rows, prompts, PRESETS, [args.seed], sp, device)
    summary_by_checkpoint = summarize_by(broad_samples, "checkpoint_label")
    summary_by_preset = summarize_by(broad_samples, "preset")
    comparisons_50_vs_44 = compare_pair(broad_samples, "44k", "50k")
    comparisons_50_vs_45 = compare_pair(broad_samples, "45k", "50k")
    pairwise_wins = {
        "44k_vs_50k": winner_counts(comparisons_50_vs_44),
        "45k_vs_50k": winner_counts(comparisons_50_vs_45),
    }
    samples_50 = [row for row in broad_samples if row["checkpoint_label"] == "50k"]
    payload = {
        "mode": "broad_44k_45k_50k",
        "device": str(device),
        "attention_backend": args.attention_backend,
        "seed": args.seed,
        "prompts_file": args.prompts,
        "prompt_count": len(prompts),
        "checkpoint_order": list(CHECKPOINTS),
        "checkpoints": checkpoint_meta,
        "tokenizer": {"path": args.tokenizer, "sha256": tokenizer_hash},
        "presets": PRESETS,
        "samples": broad_samples,
        "summary_by_checkpoint": summary_by_checkpoint,
        "summary_by_preset": summary_by_preset,
        "comparisons_50_vs_44": comparisons_50_vs_44,
        "comparisons_50_vs_45": comparisons_50_vs_45,
        "pairwise_wins": pairwise_wins,
        "largest_50k_regressions_vs_44k": [compact_comparison(row) for row in sorted(comparisons_50_vs_44, key=lambda row: row["delta"])[:10]],
        "largest_50k_improvements_vs_44k": [compact_comparison(row) for row in sorted(comparisons_50_vs_44, key=lambda row: row["delta"], reverse=True)[:10]],
        "best_50k_samples": [compact_sample(row) for row in sorted(samples_50, key=lambda row: row["quality_score"], reverse=True)[:10]],
        "worst_50k_samples": [compact_sample(row) for row in sorted(samples_50, key=lambda row: row["quality_score"])[:10]],
    }

    seed_prompts = select_seed_prompts(prompts, per_category=2)
    seed_samples = run_generations(checkpoint_rows, seed_prompts, SEED_PRESET, SEEDS, sp, device)
    seed_comparisons_50_vs_44 = compare_pair(seed_samples, "44k", "50k")
    seed_comparisons_50_vs_45 = compare_pair(seed_samples, "45k", "50k")
    seed_payload = {
        "mode": "seed_sensitivity_50k",
        "device": str(device),
        "attention_backend": args.attention_backend,
        "prompt_count": len(seed_prompts),
        "seeds": SEEDS,
        "presets": SEED_PRESET,
        "samples": seed_samples,
        "summary_by_checkpoint": summarize_by(seed_samples, "checkpoint_label"),
        "pairwise_wins": {
            "44k_vs_50k": winner_counts(seed_comparisons_50_vs_44),
            "45k_vs_50k": winner_counts(seed_comparisons_50_vs_45),
        },
        "seed_stats": {
            "44k_vs_50k": seed_stats(seed_samples, "44k", "50k"),
            "45k_vs_50k": seed_stats(seed_samples, "45k", "50k"),
        },
        "comparisons_50_vs_44": seed_comparisons_50_vs_44,
        "comparisons_50_vs_45": seed_comparisons_50_vs_45,
    }
    payload["decision"] = choose_verdict(payload, seed_payload)

    eval_json = ROOT / args.eval_json
    eval_md = ROOT / args.eval_md
    seed_json = ROOT / args.seed_json
    seed_md = ROOT / args.seed_md
    for path in (eval_json, eval_md, seed_json, seed_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    eval_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    seed_json.write_text(json.dumps(seed_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_eval_md(eval_md, payload)
    render_seed_md(seed_md, seed_payload)
    print(
        f"done: decision={payload['decision']['verdict']} "
        f"q44={summary_by_checkpoint['44k']['avg_quality_score']} "
        f"q45={summary_by_checkpoint['45k']['avg_quality_score']} "
        f"q50={summary_by_checkpoint['50k']['avg_quality_score']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
