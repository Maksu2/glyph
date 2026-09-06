#!/usr/bin/env python3
"""Write the final Glyph-100M v2.3.1 pretraining decision artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRAIN_REPORT = ROOT / "reports/glyph100_v2_3_1_50k_diagnostic_report.json"
EVAL_REPORT = ROOT / "eval/glyph-100m/v2_3_1_44k_45k_50k_eval.json"
SEED_REPORT = ROOT / "eval/glyph-100m/v2_3_1_50k_seed_sensitivity.json"
OUT_JSON = ROOT / "reports/glyph100_v2_3_1_final_decision.json"
OUT_MD = ROOT / "reports/glyph100_v2_3_1_final_decision.md"
STATUS_JSON = ROOT / "reports/glyph100_status.json"
BEST_JSON = ROOT / "checkpoints/glyph-100m_v2_3_1-best.json"
SFT_PLAN_JSON = ROOT / "reports/glyph100_44k_sft_smoke_test_plan.json"
SFT_PLAN_MD = ROOT / "reports/glyph100_44k_sft_smoke_test_plan.md"

BEST_CHECKPOINT = "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt"
LATEST_DIAGNOSTIC_CHECKPOINT = "checkpoints/glyph-100m-v2_3_1-50k/latest.pt"
TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    train = read_json(TRAIN_REPORT)
    eval_data = read_json(EVAL_REPORT)
    seed = read_json(SEED_REPORT)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    summary = eval_data["summary_by_checkpoint"]
    pairwise = eval_data["pairwise_wins"]
    seed_stats = seed["seed_stats"]
    seed_pairwise = seed["pairwise_wins"]

    final_decision = {
        "created_at_utc": created_at,
        "model": "Glyph-100M",
        "variant": "glyph-100m",
        "dataset": "glyph100_v2_3_1",
        "status": "pretraining stopped",
        "decision": "44k remains best practical checkpoint; 50k is healthy but not better.",
        "best_practical_checkpoint": BEST_CHECKPOINT,
        "best_practical_label": "44k",
        "latest_diagnostic_checkpoint": LATEST_DIAGNOSTIC_CHECKPOINT,
        "latest_diagnostic_label": "50k",
        "tokenizer_sha256": TOKENIZER_SHA,
        "do_not_continue": ["55k", "60k", "further v2.3.1 pretraining"],
        "reason": (
            "50k finished cleanly, but broad eval and seed sensitivity do not beat 44k. "
            "Further pretraining on v2.3.1 is not justified."
        ),
        "training_50k": {
            "status": train["status"],
            "duration": train["wall_duration_human"],
            "avg_tokens_per_second": train["avg_tokens_per_second"],
            "train_loss_first_logged": train["train_loss_first_logged"],
            "train_loss_last_logged": train["train_loss_last_logged"],
            "val_loss_trend": train["val_loss_trend"],
            "overfit_signal": train["overfit_signal"],
            "final_val_loss": train["val_losses"][-1]["val_loss"] if train.get("val_losses") else None,
            "nan_inf_count": len(train["nan_inf"]),
            "oom_count": len(train["oom"]),
            "crash_count": len(train["crashes"]),
        },
        "broad_eval": {
            "avg_quality": {
                "44k": summary["44k"]["avg_quality_score"],
                "45k": summary["45k"]["avg_quality_score"],
                "50k": summary["50k"]["avg_quality_score"],
            },
            "median_quality": {
                "44k": summary["44k"]["median_quality_score"],
                "45k": summary["45k"]["median_quality_score"],
                "50k": summary["50k"]["median_quality_score"],
            },
            "pairwise": {
                "50k_vs_44k": {
                    "50k_wins": pairwise["44k_vs_50k"].get("50k", 0),
                    "44k_wins": pairwise["44k_vs_50k"].get("44k", 0),
                    "ties": pairwise["44k_vs_50k"].get("tie", 0),
                },
                "50k_vs_45k": {
                    "50k_wins": pairwise["45k_vs_50k"].get("50k", 0),
                    "45k_wins": pairwise["45k_vs_50k"].get("45k", 0),
                    "ties": pairwise["45k_vs_50k"].get("tie", 0),
                },
            },
        },
        "seed_sensitivity": {
            "50k_vs_44k": {
                **seed_pairwise["44k_vs_50k"],
                "mean_44k": seed_stats["44k_vs_50k"]["overall"]["mean_44k"],
                "mean_50k": seed_stats["44k_vs_50k"]["overall"]["mean_50k"],
                "diff_50k_minus_44k": seed_stats["44k_vs_50k"]["overall"]["diff_50k_minus_44k"],
            },
            "50k_vs_45k": {
                **seed_pairwise["45k_vs_50k"],
                "mean_45k": seed_stats["45k_vs_50k"]["overall"]["mean_45k"],
                "mean_50k": seed_stats["45k_vs_50k"]["overall"]["mean_50k"],
                "diff_50k_minus_45k": seed_stats["45k_vs_50k"]["overall"]["diff_50k_minus_45k"],
            },
        },
        "next_recommended_steps": [
            "small SFT smoke test on 44k",
            "dataset v2.4 work",
            "freeze project as portfolio milestone",
        ],
        "warning": "Glyph-100M remains a base language model, not a chatbot and not a final published model.",
    }

    best_metadata = {
        "label": "44k",
        "path": BEST_CHECKPOINT,
        "latest_diagnostic_path": LATEST_DIAGNOSTIC_CHECKPOINT,
        "reason": "44k beats 50k in broad eval and seed sensitivity",
        "dataset": "glyph100_v2_3_1",
        "tokenizer_sha256": TOKENIZER_SHA,
        "status": "pretraining stopped",
        "updated_at_utc": created_at,
    }

    status = {
        "status": "v2.3.1 pretraining stopped",
        "model": "Glyph-100M",
        "best_checkpoint": BEST_CHECKPOINT,
        "latest_checkpoint": LATEST_DIAGNOSTIC_CHECKPOINT,
        "verdict": "44k remains best practical checkpoint; 50k healthy but not better",
        "warning": "Base LM only; not chatbot, not final, no 55k/60k planned.",
        "avg_quality": final_decision["broad_eval"]["avg_quality"],
        "next_step": "SFT smoke test on 44k or dataset v2.4",
        "updated_at_utc": created_at,
    }

    sft_plan = {
        "created_at_utc": created_at,
        "status": "planned_only_not_started",
        "model": "Glyph-100M",
        "base_checkpoint": BEST_CHECKPOINT,
        "output_dir": "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke",
        "dataset_size_examples": {"min": 1000, "max": 3000},
        "dataset_requirements": [
            "very clean Polish examples",
            "short direct answers",
            "rewrite/summarize output-only tasks",
            "missing-data answers with varied wording",
            "no automatic publication",
        ],
        "goal": "Check whether the 44k base model can learn the format of simple answers without damaging the base checkpoints.",
        "eval": {
            "before": "base LM continuation and small instruction probe on 44k",
            "after": "same prompts after SFT smoke checkpoint",
            "compare": ["format following", "topic adherence", "repetition", "generic-template drift"],
        },
        "checkpoint_policy": {
            "separate_output_dir": True,
            "do_not_overwrite_pretraining_checkpoints": True,
            "do_not_publish_automatically": True,
        },
        "not_run_by_this_plan": True,
    }

    write_json(OUT_JSON, final_decision)
    write_json(BEST_JSON, best_metadata)
    write_json(STATUS_JSON, status)
    write_json(SFT_PLAN_JSON, sft_plan)

    lines = [
        "# Glyph-100M v2.3.1 final decision",
        "",
        "**Verdict: 44k remains the best practical checkpoint.**",
        "",
        "50k finished cleanly, but it did not beat 44k in the broad eval or seed-sensitivity check. "
        "Pretraining on dataset v2.3.1 is stopped; 50k is diagnostic latest, not best.",
        "",
        "## Checkpoints",
        "",
        f"- best practical checkpoint: `{BEST_CHECKPOINT}`",
        f"- latest diagnostic checkpoint: `{LATEST_DIAGNOSTIC_CHECKPOINT}`",
        f"- tokenizer SHA-256: `{TOKENIZER_SHA}`",
        "- status: `pretraining stopped`",
        "- no 55k/60k continuation planned",
        "",
        "## 50k training result",
        "",
        f"- status: `{train['status']}`",
        f"- duration: `{train['wall_duration_human']}`",
        f"- avg tok/s: `{train['avg_tokens_per_second']}`",
        f"- train loss: `{train['train_loss_first_logged']}` -> `{train['train_loss_last_logged']}`",
        f"- val loss trend: `{train['val_loss_trend']}`",
        f"- overfit signal: `{train['overfit_signal']}`",
        f"- final val loss: `{final_decision['training_50k']['final_val_loss']}`",
        f"- NaN/Inf/OOM/crash: `{len(train['nan_inf'])}` / `{len(train['oom'])}` / `{len(train['crashes'])}`",
        "",
        "## Broad eval",
        "",
        "| checkpoint | avg quality | median quality |",
        "|---|---:|---:|",
        f"| 44k | {summary['44k']['avg_quality_score']} | {summary['44k']['median_quality_score']} |",
        f"| 45k | {summary['45k']['avg_quality_score']} | {summary['45k']['median_quality_score']} |",
        f"| 50k | {summary['50k']['avg_quality_score']} | {summary['50k']['median_quality_score']} |",
        "",
        "## Pairwise",
        "",
        f"- 50k vs 44k: 50k wins `{pairwise['44k_vs_50k'].get('50k', 0)}`, 44k wins `{pairwise['44k_vs_50k'].get('44k', 0)}`, ties `{pairwise['44k_vs_50k'].get('tie', 0)}`.",
        f"- 50k vs 45k: 50k wins `{pairwise['45k_vs_50k'].get('50k', 0)}`, 45k wins `{pairwise['45k_vs_50k'].get('45k', 0)}`, ties `{pairwise['45k_vs_50k'].get('tie', 0)}`.",
        "",
        "## Seed sensitivity",
        "",
        f"- 44k mean `{seed_stats['44k_vs_50k']['overall']['mean_44k']}` vs 50k mean `{seed_stats['44k_vs_50k']['overall']['mean_50k']}`; diff 50k-44k `{seed_stats['44k_vs_50k']['overall']['diff_50k_minus_44k']}`.",
        f"- 45k mean `{seed_stats['45k_vs_50k']['overall']['mean_45k']}` vs 50k mean `{seed_stats['45k_vs_50k']['overall']['mean_50k']}`; diff 50k-45k `{seed_stats['45k_vs_50k']['overall']['diff_50k_minus_45k']}`.",
        "",
        "## Next options",
        "",
        "- A: run a small SFT smoke test on 44k, only with explicit approval.",
        "- B: work on dataset v2.4 before any further pretraining.",
        "- C: freeze the project and document it as a portfolio/research milestone.",
        "",
        "## Non-goals",
        "",
        "- no 55k / 60k / further v2.3.1 pretraining",
        "- no automatic SFT",
        "- no checkpoint cleanup",
        "- no automatic publication as a final model",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    sft_lines = [
        "# Glyph-100M 44k SFT smoke test plan",
        "",
        "**Status: plan only. SFT was not started.**",
        "",
        "## Goal",
        "",
        "Check whether the best practical Glyph-100M base checkpoint can learn a simple answer format "
        "from a small, clean supervised dataset without overwriting any pretraining checkpoint.",
        "",
        "## Inputs",
        "",
        f"- base checkpoint: `{BEST_CHECKPOINT}`",
        "- dataset size: `1000-3000` very clean examples",
        "- tokenizer: existing SentencePiece BPE, no new tokenizer",
        "",
        "## Output",
        "",
        "- checkpoint dir: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke`",
        "- separate logs and eval outputs",
        "- no automatic public demo",
        "",
        "## Dataset shape",
        "",
        "- short direct factual answers",
        "- rewrite/summarize tasks where the output is only the rewritten text",
        "- missing-data examples with varied wording",
        "- anti-rambling examples with explicit short endings",
        "- avoid repeated template phrases from Glyph-27M SFT v0",
        "",
        "## Eval",
        "",
        "- before/after on the same prompts",
        "- measure instruction format, topic adherence, repetition and generic-template drift",
        "- keep base LM continuation eval separate from instruction eval",
        "",
        "## Safety",
        "",
        "- do not overwrite pretraining checkpoints",
        "- do not publish automatically",
        "- stop after smoke test and review samples before any larger SFT",
        "",
    ]
    SFT_PLAN_MD.write_text("\n".join(sft_lines), encoding="utf-8")

    for path in (OUT_MD, OUT_JSON, BEST_JSON, STATUS_JSON, SFT_PLAN_MD, SFT_PLAN_JSON):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
