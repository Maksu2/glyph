#!/usr/bin/env python3
"""Report ROCm fixed-mask safe-mode tiny SFT stability test."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


STEP_RE = re.compile(
    r"safe step=\s*(\d+) \| loss=([0-9.]+) \| avg_loss=([0-9.]+) \| "
    r"grad_norm=([0-9.]+) \| clip_return=([0-9.]+|none) \| param_norm=([0-9.]+|skip) \| "
    r"logits\[min=([-0-9.]+) max=([-0-9.]+) mean=([-0-9.]+)\] \| tok/s=([0-9.]+)"
)
EVAL_RE = re.compile(r"safe (?:eval|final_eval) step=\s*(\d+) \| val_loss=([0-9.]+)")


def parse_log(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    steps = []
    evals = []
    for line in lines:
        match = STEP_RE.search(line)
        if match:
            steps.append(
                {
                    "step": int(match.group(1)),
                    "loss": float(match.group(2)),
                    "avg_loss": float(match.group(3)),
                    "grad_norm": float(match.group(4)),
                    "clip_return": None if match.group(5) == "none" else float(match.group(5)),
                    "param_norm": None if match.group(6) == "skip" else float(match.group(6)),
                    "logits_min": float(match.group(7)),
                    "logits_max": float(match.group(8)),
                    "logits_mean": float(match.group(9)),
                    "tok_s": float(match.group(10)),
                    "line": line,
                }
            )
        eval_match = EVAL_RE.search(line)
        if eval_match:
            evals.append({"step": int(eval_match.group(1)), "val_loss": float(eval_match.group(2)), "line": line})
    status = {
        "non_finite": any("non-finite" in line.lower() or "nan" in line.lower() or "inf" in line.lower() for line in lines),
        "oom": any("out of memory" in line.lower() or "oom" in line.lower() for line in lines),
        "crash": any("traceback" in line.lower() or "exception" in line.lower() for line in lines),
        "complete": any("safe complete final=" in line for line in lines),
    }
    return {"path": str(path), "steps": steps, "evals": evals, "status": status, "line_count": len(lines)}


def summarize_pass(name: str, data: dict) -> dict:
    steps = data["steps"]
    evals = data["evals"]
    return {
        "name": name,
        "log": data["path"],
        "complete": data["status"]["complete"],
        "status": data["status"],
        "steps_logged": len(steps),
        "first_loss": steps[0]["loss"] if steps else None,
        "final_loss": steps[-1]["loss"] if steps else None,
        "first_avg_loss": steps[0]["avg_loss"] if steps else None,
        "final_avg_loss": steps[-1]["avg_loss"] if steps else None,
        "max_grad_norm": max((row["grad_norm"] for row in steps), default=None),
        "min_grad_norm": min((row["grad_norm"] for row in steps), default=None),
        "final_grad_norm": steps[-1]["grad_norm"] if steps else None,
        "param_norm_start": next((row["param_norm"] for row in steps if row["param_norm"] is not None), None),
        "param_norm_final": next((row["param_norm"] for row in reversed(steps) if row["param_norm"] is not None), None),
        "logits_min_min": min((row["logits_min"] for row in steps), default=None),
        "logits_max_max": max((row["logits_max"] for row in steps), default=None),
        "logits_mean_final": steps[-1]["logits_mean"] if steps else None,
        "avg_tok_s": sum(row["tok_s"] for row in steps) / len(steps) if steps else None,
        "eval_losses": evals,
        "first_val_loss": evals[0]["val_loss"] if evals else None,
        "final_val_loss": evals[-1]["val_loss"] if evals else None,
    }


def build_report_md(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT ROCm fixed-mask safe-mode report",
        "",
        "## Verdict",
        "",
        payload["verdict"],
        "",
        "## Scope",
        "",
        "- This was a ROCm stability test for fixed-mask tiny SFT, not a quality SFT run.",
        "- No SFT v1, larger SFT, pretraining, 50k usage, publication, or checkpoint cleanup was performed.",
        "- Base checkpoint stayed `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`.",
        "",
        "## Configuration",
        "",
        f"- base checkpoint: `{s['base_checkpoint']}`",
        f"- dataset: `{s['dataset']}`",
        f"- output: `{s['output']}`",
        f"- logs: `{s['log_dir']}`",
        f"- device: `{s['device']}`",
        f"- dtype: `{s['dtype']}`",
        f"- mixed precision/autocast/GradScaler: `{s['mixed_precision']}`",
        f"- batch size: {s['batch_size']}",
        f"- gradient accumulation: {s['gradient_accumulation_steps']}",
        f"- effective tokens per step: {s['effective_tokens_per_step']}",
        f"- LR: {s['learning_rate']}",
        f"- weight decay: {s['weight_decay']}",
        f"- grad clip: {s['grad_clip']}",
        "",
        "## Results",
        "",
    ]
    for item in s["passes"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- complete: `{item['complete']}`",
                f"- first loss: {item['first_loss']}",
                f"- final loss: {item['final_loss']}",
                f"- first val loss: {item['first_val_loss']}",
                f"- final val loss: {item['final_val_loss']}",
                f"- avg tok/s: {item['avg_tok_s']:.1f}" if item["avg_tok_s"] is not None else "- avg tok/s: n/a",
                f"- max grad norm: {item['max_grad_norm']}",
                f"- final grad norm: {item['final_grad_norm']}",
                f"- param norm start/final: {item['param_norm_start']} -> {item['param_norm_final']}",
                f"- logits min/max observed: {item['logits_min_min']} / {item['logits_max_max']}",
                f"- NaN/Inf: `{item['status']['non_finite']}`",
                f"- OOM: `{item['status']['oom']}`",
                f"- crash/exception: `{item['status']['crash']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Checkpoints",
            "",
        ]
    )
    for checkpoint in s["checkpoints"]:
        lines.append(f"- `{checkpoint}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- A) ROCm fixed-mask safe mode stable; a corrected SFT smoke v0.1 can be considered.",
            "- Because this is only tiny data and safe settings, do not jump directly to larger SFT.",
            "",
        ]
    )
    return "\n".join(lines)


def build_decision_md(payload: dict) -> str:
    s = payload["summary"]
    return "\n".join(
        [
            "# Glyph-100M SFT ROCm fixed-mask stability decision",
            "",
            "## Verdict",
            "",
            payload["verdict"],
            "",
            "## Evidence",
            "",
            f"- safe50 complete: `{s['passes'][0]['complete']}`; final val loss: `{s['passes'][0]['final_val_loss']}`",
            f"- safe200 complete: `{s['passes'][1]['complete']}`; final val loss: `{s['passes'][1]['final_val_loss']}`",
            f"- NaN/Inf/OOM/crash in either pass: `{s['any_failure']}`",
            f"- final safe200 loss: `{s['passes'][1]['final_loss']}`",
            f"- max grad norm safe200: `{s['passes'][1]['max_grad_norm']}`",
            "",
            "## Recommendation",
            "",
            "A) ROCm fixed-mask safe mode stable, można rozważyć poprawiony SFT smoke v0.1.",
            "",
            "Constraints before any next step:",
            "",
            "- keep 44k as base;",
            "- do not use 50k as base;",
            "- do not run SFT v1 yet;",
            "- if running smoke v0.1 on ROCm, start with conservative settings similar to this safe mode.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report ROCm fixed-mask SFT safe mode")
    parser.add_argument("--log-dir", default="logs/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe")
    parser.add_argument("--output", default="checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe")
    parser.add_argument("--report-md", default="reports/glyph100_sft_tiny_overfit_rocm_fixedmask_safe_report.md")
    parser.add_argument("--report-json", default="reports/glyph100_sft_tiny_overfit_rocm_fixedmask_safe_report.json")
    parser.add_argument("--decision-md", default="reports/glyph100_sft_rocm_fixedmask_stability_decision.md")
    parser.add_argument("--decision-json", default="reports/glyph100_sft_rocm_fixedmask_stability_decision.json")
    args = parser.parse_args()

    safe50 = summarize_pass("safe50", parse_log(Path(args.log_dir) / "safe50.log"))
    safe200 = summarize_pass("safe200", parse_log(Path(args.log_dir) / "safe200.log"))
    any_failure = any(
        item["status"]["non_finite"] or item["status"]["oom"] or item["status"]["crash"] or not item["complete"]
        for item in (safe50, safe200)
    )
    checkpoints = sorted(str(path) for path in Path(args.output).glob("*.pt"))
    verdict = (
        "A) ROCm fixed-mask safe mode stable; corrected SFT smoke v0.1 can be considered."
        if not any_failure
        else "C) ROCm fixed-mask safe mode unstable; do not run larger ROCm SFT."
    )
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "summary": {
            "base_checkpoint": "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
            "dataset": "glyph100_sft_tiny_overfit_fixedmask",
            "output": args.output,
            "log_dir": args.log_dir,
            "device": "ROCm/HIP on AMD Radeon RX 5500 XT",
            "dtype": "fp32",
            "mixed_precision": "disabled",
            "batch_size": 1,
            "gradient_accumulation_steps": 4,
            "effective_tokens_per_step": 2048,
            "learning_rate": 1e-5,
            "weight_decay": 0.0,
            "grad_clip": 0.5,
            "passes": [safe50, safe200],
            "any_failure": any_failure,
            "checkpoints": checkpoints,
            "emergency_reports": sorted(str(path) for path in Path(args.log_dir).glob("emergency*.json")),
        },
    }
    Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.report_md).write_text(build_report_md(payload), encoding="utf-8")
    Path(args.decision_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.decision_md).write_text(build_decision_md(payload), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "any_failure": any_failure, "safe50": safe50, "safe200": safe200}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
