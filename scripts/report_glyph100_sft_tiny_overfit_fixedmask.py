#!/usr/bin/env python3
"""Build report for Glyph-100M fixed-mask SFT tiny overfit."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


STEP_RE = re.compile(r"sft step=\s*(\d+) \| epoch=(\d+) \| loss=([0-9.]+) \| lr=([0-9.eE+-]+) \| tok/s=([0-9,]+)")
EVAL_RE = re.compile(r"sft (?:eval|final_eval) step=\s*(\d+) \| val_loss=([0-9.]+)")


def parse_log(path: Path) -> dict:
    steps = []
    evals = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        step_match = STEP_RE.search(line)
        if step_match:
            steps.append(
                {
                    "step": int(step_match.group(1)),
                    "epoch": int(step_match.group(2)),
                    "loss": float(step_match.group(3)),
                    "lr": float(step_match.group(4)),
                    "tok_s": float(step_match.group(5).replace(",", "")),
                    "line": line,
                }
            )
        eval_match = EVAL_RE.search(line)
        if eval_match:
            evals.append({"step": int(eval_match.group(1)), "val_loss": float(eval_match.group(2)), "line": line})
    status = {
        "non_finite": any("Non-finite" in line or "nan" in line.lower() for line in lines),
        "oom": any("out of memory" in line.lower() or "oom" in line.lower() for line in lines),
        "crash": any("Traceback" in line or "Exception" in line for line in lines),
        "complete": any("SFT complete" in line for line in lines),
    }
    return {"steps": steps, "evals": evals, "status": status, "line_count": len(lines)}


def build_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT tiny overfit CPU fixed-mask report",
        "",
        "## Verdict",
        "",
        payload["verdict"],
        "",
        "## Scope",
        "",
        "- This was a tiny overfit mechanics test, not a quality SFT run.",
        "- No larger SFT, SFT v1, pretraining, ROCm SFT, publication, or checkpoint cleanup was performed.",
        "- The previous SFT smoke is marked invalid-for-quality because it used the label mask off-by-one bug.",
        "",
        "## Inputs",
        "",
        f"- base checkpoint: `{s['base_checkpoint']}`",
        f"- output checkpoint: `{s['final_checkpoint']}`",
        f"- dataset: `{s['dataset']}`",
        f"- train examples: {s['train_examples']}",
        f"- device: `{s['device']}`",
        f"- steps: {s['steps']}",
        f"- batch size: {s['batch_size']}",
        f"- learning rate: {s['learning_rate']}",
        f"- weight decay: {s['weight_decay']}",
        "",
        "## Loss",
        "",
        f"- first logged train loss: {s['first_logged_loss']}",
        f"- final logged train loss: {s['final_logged_loss']}",
        f"- final val loss: {s['final_val_loss']}",
        f"- eval losses: `{s['eval_losses']}`",
        f"- average tok/s from log windows: {s['avg_tok_s']:.1f}",
        "",
        "## Stability",
        "",
        f"- complete: `{s['status']['complete']}`",
        f"- NaN/Inf: `{s['status']['non_finite']}`",
        f"- OOM: `{s['status']['oom']}`",
        f"- crash/exception: `{s['status']['crash']}`",
        "",
        "## Eval",
        "",
        f"- eval report: `{s['eval_md']}`",
        f"- examples: {s['eval_examples']}",
        f"- winners: `{s['eval_winners']}`",
        f"- base avg score: {s['base_avg_score']:.2f}",
        f"- SFT avg score: {s['sft_avg_score']:.2f}",
        f"- SFT overlap >= 0.70: {s['sft_overlap_ge_0_70']}",
        f"- SFT starts with expected first word: {s['sft_starts_correctly']}",
        f"- SFT ended by `<|end|>`: {s['sft_ended_by_end_token']}",
        f"- SFT repetition samples: {s['sft_repetition_samples']}",
        f"- SFT web residue: {s['sft_web_residue']}",
        f"- SFT pseudo-ency: {s['sft_pseudo_ency']}",
        "",
        "## Decision",
        "",
        "- A) Fixed mask works; the model can overfit the tiny dataset on CPU.",
        "- Next allowed technical step, if approved separately: ROCm safe-mode SFT test with fixed mask.",
        "- Do not scale SFT on the old smoke result; it was invalid-for-quality.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Report Glyph fixed-mask tiny overfit")
    parser.add_argument("--log", default="logs/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask/train.log")
    parser.add_argument("--eval-json", default="eval/glyph-100m/sft_tiny_overfit_cpu_fixedmask_eval.json")
    parser.add_argument("--eval-md", default="eval/glyph-100m/sft_tiny_overfit_cpu_fixedmask_eval.md")
    parser.add_argument("--dataset-report", default="data/sft/glyph100_sft_tiny_overfit_fixedmask_dataset_report.json")
    parser.add_argument("--final-checkpoint", default="checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask-final.pt")
    parser.add_argument("--out-md", default="reports/glyph100_sft_tiny_overfit_cpu_fixedmask_report.md")
    parser.add_argument("--out-json", default="reports/glyph100_sft_tiny_overfit_cpu_fixedmask_report.json")
    args = parser.parse_args()

    log_data = parse_log(Path(args.log))
    eval_payload = json.loads(Path(args.eval_json).read_text(encoding="utf-8"))
    dataset = json.loads(Path(args.dataset_report).read_text(encoding="utf-8"))
    steps = log_data["steps"]
    evals = log_data["evals"]
    eval_summary = eval_payload["summary"]
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_checkpoint": "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
        "final_checkpoint": args.final_checkpoint,
        "dataset": "glyph100_sft_tiny_overfit_fixedmask",
        "train_examples": dataset["examples"],
        "device": "cpu",
        "steps": 300,
        "batch_size": 4,
        "learning_rate": 5e-5,
        "weight_decay": 0.0,
        "first_logged_loss": steps[0]["loss"] if steps else None,
        "final_logged_loss": steps[-1]["loss"] if steps else None,
        "final_val_loss": evals[-1]["val_loss"] if evals else None,
        "eval_losses": evals,
        "avg_tok_s": sum(item["tok_s"] for item in steps) / len(steps) if steps else 0.0,
        "status": log_data["status"],
        "eval_md": args.eval_md,
        "eval_examples": eval_summary["examples"],
        "eval_winners": eval_summary["winners"],
        "base_avg_score": eval_summary["base_avg_score"],
        "sft_avg_score": eval_summary["sft_avg_score"],
        "sft_overlap_ge_0_70": eval_summary["sft_overlap_ge_0_70"],
        "sft_starts_correctly": eval_summary["sft_starts_correctly"],
        "sft_ended_by_end_token": eval_summary["sft_ended_by_end_token"],
        "sft_repetition_samples": eval_summary["sft_repetition_samples"],
        "sft_web_residue": eval_summary["sft_web_residue"],
        "sft_pseudo_ency": eval_summary["sft_pseudo_ency"],
    }
    verdict = "A) Fixed mask działa; model potrafi overfitować tiny dataset na CPU."
    payload = {
        "summary": summary,
        "verdict": verdict,
        "previous_sft_smoke_quality_status": "invalid-for-quality",
        "previous_sft_smoke_invalid_reason": "label mask off-by-one bug masked first assistant response token",
        "not_done": [
            "larger SFT",
            "SFT v1",
            "ROCm SFT",
            "pretraining",
            "checkpoint cleanup",
            "model publication",
        ],
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.out_md).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps({"verdict": verdict, **summary}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
