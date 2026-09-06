#!/usr/bin/env python3
"""Build the post-50k decision report and local status snapshot."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAIN_REPORT = ROOT / "reports/glyph100_v2_3_1_50k_diagnostic_report.json"
EVAL_REPORT = ROOT / "eval/glyph-100m/v2_3_1_44k_45k_50k_eval.json"
SEED_REPORT = ROOT / "eval/glyph-100m/v2_3_1_50k_seed_sensitivity.json"
OUT_JSON = ROOT / "reports/glyph100_v2_3_1_post_50k_decision.json"
OUT_MD = ROOT / "reports/glyph100_v2_3_1_post_50k_decision.md"
STATUS_JSON = ROOT / "reports/glyph100_status.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float) -> str:
    return f"{value:.3f}"


def main() -> None:
    train = load_json(TRAIN_REPORT)
    eval_data = load_json(EVAL_REPORT)
    seed = load_json(SEED_REPORT)

    summary = eval_data["summary_by_checkpoint"]
    pairwise = eval_data["pairwise_wins"]
    seed_pairwise = seed["pairwise_wins"]
    seed_stats = seed["seed_stats"]

    q44 = summary["44k"]["avg_quality_score"]
    q45 = summary["45k"]["avg_quality_score"]
    q50 = summary["50k"]["avg_quality_score"]

    verdict = "B"
    verdict_label = "44k zostaje best practical checkpoint"
    reason = (
        "50k is technically healthy and slightly better than 45k in seed sensitivity, "
        "but it does not beat 44k in broad eval or seed mean score."
    )

    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict": verdict,
        "verdict_label": verdict_label,
        "reason": reason,
        "best_practical_checkpoint": "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
        "latest_diagnostic_checkpoint": "checkpoints/glyph-100m-v2_3_1-50k/latest.pt",
        "latest_step_checkpoint": "checkpoints/glyph-100m-v2_3_1-50k/step_0050000.pt",
        "model": "Glyph-100M",
        "variant": "glyph-100m",
        "dataset": "glyph100_v2_3_1",
        "warning": "Base LM only; not an assistant/chatbot and not a final published model.",
        "training": {
            "status": train["status"],
            "start_step": train["start_step"],
            "end_step": train["end_step"],
            "duration": train["wall_duration_human"],
            "avg_tokens_per_second": train["avg_tokens_per_second"],
            "train_loss_first_logged": train["train_loss_first_logged"],
            "train_loss_last_logged": train["train_loss_last_logged"],
            "train_loss_min": train["train_loss_min"],
            "train_loss_max": train["train_loss_max"],
            "val_loss_trend": train["val_loss_trend"],
            "overfit_signal": train["overfit_signal"],
            "val_losses": train["val_losses"],
            "nan_inf_count": len(train["nan_inf"]),
            "oom_count": len(train["oom"]),
            "crash_count": len(train["crashes"]),
            "checkpoint_files": train["checkpoint_files"],
            "checkpoint_dir_size_human": train["checkpoint_dir_size_human"],
        },
        "eval": {
            "avg_quality": {"44k": q44, "45k": q45, "50k": q50},
            "median_quality": {
                "44k": summary["44k"]["median_quality_score"],
                "45k": summary["45k"]["median_quality_score"],
                "50k": summary["50k"]["median_quality_score"],
            },
            "summary_by_checkpoint": summary,
            "pairwise_wins": pairwise,
            "seed_pairwise_wins": seed_pairwise,
            "seed_stats": {
                "44k_vs_50k": seed_stats["44k_vs_50k"]["overall"],
                "45k_vs_50k": seed_stats["45k_vs_50k"]["overall"],
                "44k_vs_50k_diff_gt_noise_count": seed_stats["44k_vs_50k"]["diff_gt_noise_count"],
                "45k_vs_50k_diff_gt_noise_count": seed_stats["45k_vs_50k"]["diff_gt_noise_count"],
            },
        },
        "artifacts": {
            "training_report_md": "reports/glyph100_v2_3_1_50k_diagnostic_report.md",
            "training_report_json": "reports/glyph100_v2_3_1_50k_diagnostic_report.json",
            "broad_eval_md": "eval/glyph-100m/v2_3_1_44k_45k_50k_eval.md",
            "broad_eval_json": "eval/glyph-100m/v2_3_1_44k_45k_50k_eval.json",
            "seed_eval_md": "eval/glyph-100m/v2_3_1_50k_seed_sensitivity.md",
            "seed_eval_json": "eval/glyph-100m/v2_3_1_50k_seed_sensitivity.json",
        },
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    STATUS_JSON.write_text(
        json.dumps(
            {
                "status": "50k complete",
                "model": "Glyph-100M",
                "best_checkpoint": payload["best_practical_checkpoint"],
                "latest_checkpoint": payload["latest_diagnostic_checkpoint"],
                "verdict": f"{verdict}) {verdict_label}",
                "warning": payload["warning"],
                "avg_quality": payload["eval"]["avg_quality"],
                "updated_at_utc": payload["created_at_utc"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Glyph-100M v2.3.1 post-50k decision",
        "",
        f"**Verdict: {verdict}) {verdict_label}.**",
        "",
        reason,
        "",
        "## Decision",
        "",
        f"- best practical checkpoint: `{payload['best_practical_checkpoint']}`",
        f"- latest diagnostic checkpoint: `{payload['latest_diagnostic_checkpoint']}`",
        "- 50k is diagnostic latest, not best.",
        "- Model status: base LM only, not chatbot, not final published model.",
        "",
        "## Training 45k -> 50k",
        "",
        f"- status: `{train['status']}`",
        f"- duration: `{train['wall_duration_human']}`",
        f"- steps: `{train['start_step']}` -> `{train['end_step']}`",
        f"- avg tok/s: `{train['avg_tokens_per_second']}`",
        f"- train loss: `{train['train_loss_first_logged']}` -> `{train['train_loss_last_logged']}`",
        f"- train loss min/max: `{train['train_loss_min']}` / `{train['train_loss_max']}`",
        f"- val loss trend: `{train['val_loss_trend']}`",
        f"- overfit signal: `{train['overfit_signal']}`",
        f"- NaN/Inf/OOM/crash counts: `{len(train['nan_inf'])}` / `{len(train['oom'])}` / `{len(train['crashes'])}`",
        "",
        "### Validation losses",
        "",
    ]
    for row in train["val_losses"]:
        lines.append(f"- step `{row['step']}`: `{row['val_loss']}` at `{row['ts']}`")

    lines.extend(
        [
            "",
            "## Broad Eval",
            "",
            "| checkpoint | avg quality | median quality | repetition | natural endings | cutoff-like | pseudo-ency | web residue | wiki residue | drift | overlap |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label in ("44k", "45k", "50k"):
        row = summary[label]
        count = row["count"]
        lines.append(
            f"| {label} | {pct(row['avg_quality_score'])} | {row['median_quality_score']} | "
            f"{row['repetition_samples']}/{count} | {row['natural_endings']}/{count} | "
            f"{row['cutoff_like_samples']}/{count} | {row['pseudo_ency_samples']}/{count} | "
            f"{row['web_residue_samples']}/{count} | {row['wiki_residue_samples']}/{count} | "
            f"{row['topic_drift_samples']}/{count} | {row['avg_topic_overlap']} |"
        )

    lines.extend(
        [
            "",
            "## Pairwise",
            "",
            f"- 50k vs 44k: 50k wins `{pairwise['44k_vs_50k'].get('50k', 0)}`, 44k wins `{pairwise['44k_vs_50k'].get('44k', 0)}`, ties `{pairwise['44k_vs_50k'].get('tie', 0)}`.",
            f"- 50k vs 45k: 50k wins `{pairwise['45k_vs_50k'].get('50k', 0)}`, 45k wins `{pairwise['45k_vs_50k'].get('45k', 0)}`, ties `{pairwise['45k_vs_50k'].get('tie', 0)}`.",
            "",
            "## Seed Sensitivity",
            "",
            f"- 44k vs 50k mean: `{seed_stats['44k_vs_50k']['overall']['mean_44k']}` vs `{seed_stats['44k_vs_50k']['overall']['mean_50k']}`; diff 50k-44k `{seed_stats['44k_vs_50k']['overall']['diff_50k_minus_44k']}`; diff > noise `{seed_stats['44k_vs_50k']['diff_gt_noise_count']}/20`.",
            f"- 45k vs 50k mean: `{seed_stats['45k_vs_50k']['overall']['mean_45k']}` vs `{seed_stats['45k_vs_50k']['overall']['mean_50k']}`; diff 50k-45k `{seed_stats['45k_vs_50k']['overall']['diff_50k_minus_45k']}`; diff > noise `{seed_stats['45k_vs_50k']['diff_gt_noise_count']}/20`.",
            "",
            "## Read",
            "",
            "- 50k is technically healthy, but quality does not clearly improve over 44k.",
            "- 50k slightly beats 45k in some stochastic checks, but not enough to replace 44k.",
            "- Further pretraining on this dataset is not justified by this diagnostic result without a new decision.",
            "- Next rational step is either a small SFT smoke test on the best checkpoint or dataset v2.4 work, not more blind pretraining.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {STATUS_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
