#!/usr/bin/env python3
"""Finalize Glyph-100M SFT smoke v0.2 reports from logs and eval JSON."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from statistics import mean


STEP_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe step=\s*(?P<step>\d+)"
    r" \| loss=(?P<loss>[-+\d.]+) \| avg_loss=(?P<avg_loss>[-+\d.]+)"
    r" \| grad_norm=(?P<grad_norm>[-+\d.]+).* \| tok/s=(?P<toks>[-+\d.]+)"
)
EVAL_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe eval step=\s*(?P<step>\d+)"
    r" \| val_loss=(?P<val_loss>[-+\d.]+) \| batches=(?P<batches>\d+)"
)
FINAL_EVAL_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) safe final_eval step=\s*(?P<step>\d+)"
    r" \| val_loss=(?P<val_loss>[-+\d.]+) \| batches=(?P<batches>\d+)"
)
CONFIG_RE = re.compile(
    r"ROCm safe tiny SFT pass=(?P<pass_name>\S+) max_steps=(?P<max_steps>\d+)"
    r" batch=(?P<batch>\d+) accum=(?P<accum>\d+) lr=(?P<lr>[-+eE\d.]+) grad_clip=(?P<grad_clip>[-+\d.]+)"
)
DATASET_RE = re.compile(
    r"base=(?P<base>\S+) base_step=(?P<base_step>\d+) dataset=(?P<dataset>\S+)"
    r" train_usable=(?P<train_usable>\d+) val_usable=(?P<val_usable>\d+) output=(?P<output>\S+)"
)


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_log(path: Path) -> dict:
    steps: list[dict] = []
    evals: list[dict] = []
    final_eval: dict | None = None
    config: dict = {}
    dataset: dict = {}
    checkpoints: list[str] = []
    best_updates: list[dict] = []
    complete_line = None
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    for line in raw_lines:
        if match := STEP_RE.search(line):
            item = match.groupdict()
            steps.append(
                {
                    "ts": item["ts"],
                    "step": int(item["step"]),
                    "loss": float(item["loss"]),
                    "avg_loss": float(item["avg_loss"]),
                    "grad_norm": float(item["grad_norm"]),
                    "tokens_per_second": float(item["toks"]),
                }
            )
        elif match := EVAL_RE.search(line):
            item = match.groupdict()
            evals.append(
                {
                    "ts": item["ts"],
                    "step": int(item["step"]),
                    "val_loss": float(item["val_loss"]),
                    "batches": int(item["batches"]),
                }
            )
        elif match := FINAL_EVAL_RE.search(line):
            item = match.groupdict()
            final_eval = {
                "ts": item["ts"],
                "step": int(item["step"]),
                "val_loss": float(item["val_loss"]),
                "batches": int(item["batches"]),
            }
        elif match := CONFIG_RE.search(line):
            item = match.groupdict()
            config = {
                "pass_name": item["pass_name"],
                "max_steps": int(item["max_steps"]),
                "batch_size": int(item["batch"]),
                "gradient_accumulation_steps": int(item["accum"]),
                "learning_rate": float(item["lr"]),
                "grad_clip": float(item["grad_clip"]),
            }
        elif match := DATASET_RE.search(line):
            item = match.groupdict()
            dataset = {
                "base": item["base"],
                "base_step": int(item["base_step"]),
                "dataset": item["dataset"],
                "train_usable": int(item["train_usable"]),
                "val_usable": int(item["val_usable"]),
                "output": item["output"],
            }
        if "safe checkpoint saved:" in line:
            checkpoints.append(line.split("safe checkpoint saved:", 1)[1].strip())
        if "safe best checkpoint updated:" in line:
            path_part = line.split("safe best checkpoint updated:", 1)[1].strip()
            val_match = re.search(r"best_val_loss=([-+\d.]+)", path_part)
            best_updates.append(
                {
                    "line": line,
                    "path": path_part.split(" ", 1)[0],
                    "best_val_loss": float(val_match.group(1)) if val_match else None,
                }
            )
        if "safe complete final=" in line:
            complete_line = line

    first_ts = parse_ts(steps[0]["ts"]) if steps else None
    last_ts = parse_ts(final_eval["ts"]) if final_eval else (parse_ts(steps[-1]["ts"]) if steps else None)
    duration_seconds = int((last_ts - first_ts).total_seconds()) if first_ts and last_ts else None
    losses = [row["loss"] for row in steps]
    avg_losses = [row["avg_loss"] for row in steps]
    grad_norms = [row["grad_norm"] for row in steps]
    toks = [row["tokens_per_second"] for row in steps]
    all_evals = evals + ([final_eval] if final_eval else [])
    best_eval = min(all_evals, key=lambda row: row["val_loss"]) if all_evals else None
    return {
        "log_path": str(path),
        "line_count": len(raw_lines),
        "config": config,
        "dataset": dataset,
        "steps_logged": steps,
        "evals": evals,
        "final_eval": final_eval,
        "best_eval": best_eval,
        "checkpoint_saves": checkpoints,
        "best_updates": best_updates,
        "complete_line": complete_line,
        "duration_seconds": duration_seconds,
        "loss_start": losses[0] if losses else None,
        "loss_end": losses[-1] if losses else None,
        "avg_loss_end": avg_losses[-1] if avg_losses else None,
        "loss_min": min(losses) if losses else None,
        "loss_max": max(losses) if losses else None,
        "loss_mean": mean(losses) if losses else None,
        "grad_norm_max": max(grad_norms) if grad_norms else None,
        "tokens_per_second_mean": mean(toks) if toks else None,
        "tokens_per_second_last": toks[-1] if toks else None,
        "has_nan_or_inf": any("nan" in line.lower() or "inf" in line.lower() for line in raw_lines),
        "has_oom_or_crash": any(
            needle in line.lower()
            for line in raw_lines
            for needle in ("out of memory", "oom", "traceback", "exception", "crash")
        ),
    }


def aggregate_eval(eval_payload: dict) -> dict:
    if not eval_payload:
        return {}
    summary = eval_payload.get("summary", {})
    mode_summaries = summary.get("mode_summaries", {})
    model_names = ("base44k", "sft_v0_1", "sft_v0_2")
    aggregate = {name: {"avg_scores": [], "repetitions": 0, "pseudo": 0, "web": 0, "first": 0} for name in model_names}
    pairwise_total: dict[str, dict[str, int]] = {}
    for mode_summary in mode_summaries.values():
        for model in model_names:
            stats = mode_summary.get("models", {}).get(model, {})
            if not stats:
                continue
            aggregate[model]["avg_scores"].append(float(stats.get("avg_score", 0.0)))
            aggregate[model]["repetitions"] += int(stats.get("repetition_samples", 0))
            aggregate[model]["pseudo"] += int(stats.get("pseudo_ency", 0))
            aggregate[model]["web"] += int(stats.get("web_residue", 0))
            aggregate[model]["first"] += int(stats.get("first_token_correct", 0))
        for key, counts in mode_summary.get("pairwise", {}).items():
            total = pairwise_total.setdefault(key, {})
            for winner, count in counts.items():
                total[winner] = total.get(winner, 0) + int(count)
    for model in model_names:
        scores = aggregate[model].pop("avg_scores")
        aggregate[model]["avg_score_mean_across_modes"] = mean(scores) if scores else None
    return {
        "rows": summary.get("rows"),
        "modes": list(mode_summaries.keys()),
        "models": aggregate,
        "pairwise_total": pairwise_total,
    }


def decide(eval_agg: dict) -> dict:
    if not eval_agg:
        return {
            "verdict": "D",
            "label": "eval missing",
            "recommendation": "Nie skalować. Najpierw uruchomić eval.",
        }
    models = eval_agg["models"]
    v02 = models["sft_v0_2"]
    v01 = models["sft_v0_1"]
    pair = eval_agg["pairwise_total"].get("sft_v0_2_vs_sft_v0_1", {})
    v02_wins = pair.get("sft_v0_2", 0)
    v01_wins = pair.get("sft_v0_1", 0)
    score_delta = (v02["avg_score_mean_across_modes"] or 0) - (v01["avg_score_mean_across_modes"] or 0)
    rep_delta = v02["repetitions"] - v01["repetitions"]
    if v02_wins > v01_wins * 1.5 and score_delta >= 0.8 and rep_delta <= 0:
        return {
            "verdict": "A",
            "label": "v0.2 mocno poprawia v0.1",
            "recommendation": "Można planować SFT v1, ale dopiero po decyzji użytkownika.",
        }
    if v02_wins >= v01_wins and score_delta >= 0 and rep_delta <= 0:
        return {
            "verdict": "B",
            "label": "v0.2 poprawia częściowo",
            "recommendation": "Kolejny krok to projekt datasetu v0.3 albo ostrożny plan SFT v1; nie uruchamiać automatycznie.",
        }
    if rep_delta > 0:
        return {
            "verdict": "C",
            "label": "v0.2 stabilny, ale repetition nadal problematyczne",
            "recommendation": "Nie skalować. Poprawić dataset/decoding pod powtórzenia.",
        }
    return {
        "verdict": "D",
        "label": "v0.2 nie przebija v0.1",
        "recommendation": "Nie skalować v0.2; wrócić do datasetu/evalu.",
    }


def fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "unknown"
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}m {sec}s"


def write_training_report(payload: dict, dataset_report: dict, eval_agg: dict, md_path: Path, json_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dataset_stats = dataset_report.get("stats", {})
    token_stats = dataset_stats.get("token_stats", {})
    lines = [
        "# Glyph-100M SFT smoke v0.2 fixed-mask ROCm report",
        "",
        "## Status",
        "",
        "- run: `complete`",
        "- type: corrected small SFT smoke, not SFT v1",
        "- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`",
        "- output: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm`",
        "- 50k checkpoint was not used.",
        "",
        "## Training",
        "",
        f"- duration: `{fmt_duration(payload['duration_seconds'])}`",
        f"- steps: `{payload['config'].get('max_steps')}`",
        f"- batch/accum: `{payload['config'].get('batch_size')}/{payload['config'].get('gradient_accumulation_steps')}`",
        f"- learning rate: `{payload['config'].get('learning_rate')}`",
        f"- grad clip: `{payload['config'].get('grad_clip')}`",
        f"- train loss start/end: `{payload['loss_start']}` -> `{payload['loss_end']}`",
        f"- final running avg loss: `{payload['avg_loss_end']}`",
        f"- best val loss: `{payload['best_eval']['val_loss'] if payload.get('best_eval') else None}` at step `{payload['best_eval']['step'] if payload.get('best_eval') else None}`",
        f"- final val loss: `{payload['final_eval']['val_loss'] if payload.get('final_eval') else None}`",
        f"- avg tok/s from log: `{payload['tokens_per_second_mean']:.1f}`",
        f"- max grad norm: `{payload['grad_norm_max']}`",
        f"- NaN/Inf: `{payload['has_nan_or_inf']}`",
        f"- OOM/crash/exception: `{payload['has_oom_or_crash']}`",
        "",
        "## Validation Loss",
        "",
    ]
    for row in payload["evals"]:
        lines.append(f"- step `{row['step']}`: val_loss `{row['val_loss']}`")
    if payload.get("final_eval"):
        lines.append(f"- final step `{payload['final_eval']['step']}`: val_loss `{payload['final_eval']['val_loss']}`")
    lines += [
        "",
        "## Dataset",
        "",
        f"- dataset: `{payload['dataset'].get('dataset')}`",
        f"- train usable: `{payload['dataset'].get('train_usable')}`",
        f"- val usable: `{payload['dataset'].get('val_usable')}`",
        f"- dataset report total examples: `{dataset_stats.get('examples')}`",
        f"- split: `{dataset_report.get('split_counts')}`",
        f"- max template tokens: `{token_stats.get('template_max')}`",
        "",
        "## Checkpoints",
        "",
        f"- checkpoint saves: `{len(payload['checkpoint_saves'])}`",
        f"- best updates: `{len(payload['best_updates'])}`",
        "- best checkpoint was saved with `save_best_on_val=true`.",
        "",
        "## Eval Snapshot",
        "",
    ]
    if eval_agg:
        for model, stats in eval_agg["models"].items():
            lines.append(
                f"- {model}: avg_score_mean `{stats['avg_score_mean_across_modes']:.2f}`, "
                f"repetition `{stats['repetitions']}`, first-token `{stats['first']}`, web `{stats['web']}`, pseudo `{stats['pseudo']}`"
            )
        lines.append(f"- pairwise totals: `{eval_agg['pairwise_total']}`")
    else:
        lines.append("- eval: not available when this report was generated")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_decision_report(decision_payload: dict, md_path: Path, json_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(decision_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d = decision_payload["decision"]
    lines = [
        "# Glyph-100M SFT v0.2 next decision",
        "",
        "## Verdict",
        "",
        f"- verdict: `{d['verdict']}`",
        f"- label: `{d['label']}`",
        f"- recommendation: {d['recommendation']}",
        "",
        "## Constraints",
        "",
        "- Do not run SFT v1 automatically.",
        "- Do not run further pretraining.",
        "- Do not use 50k as SFT base.",
        "- Do not publish as final chatbot.",
        "",
        "## Evidence",
        "",
        f"- eval rows: `{decision_payload['eval'].get('rows')}`",
        f"- modes: `{decision_payload['eval'].get('modes')}`",
        f"- pairwise totals: `{decision_payload['eval'].get('pairwise_total')}`",
        "",
    ]
    for model, stats in decision_payload["eval"].get("models", {}).items():
        lines.append(
            f"- {model}: avg `{stats['avg_score_mean_across_modes']:.2f}`, "
            f"repetition `{stats['repetitions']}`, first-token `{stats['first']}`, web `{stats['web']}`, pseudo `{stats['pseudo']}`"
        )
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="logs/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/train.log")
    parser.add_argument("--dataset-report", default="data/sft/glyph100_sft_smoke_v0_2_report.json")
    parser.add_argument("--eval-json", default="eval/glyph-100m/sft_smoke_v0_2_fixedmask_before_after.json")
    parser.add_argument("--training-md", default="reports/glyph100_44k_sft_smoke_v0_2_fixedmask_rocm_report.md")
    parser.add_argument("--training-json", default="reports/glyph100_44k_sft_smoke_v0_2_fixedmask_rocm_report.json")
    parser.add_argument("--decision-md", default="reports/glyph100_sft_v0_2_next_decision.md")
    parser.add_argument("--decision-json", default="reports/glyph100_sft_v0_2_next_decision.json")
    args = parser.parse_args()

    log_payload = parse_log(Path(args.log))
    dataset_report = read_json(Path(args.dataset_report))
    eval_payload = read_json(Path(args.eval_json))
    eval_agg = aggregate_eval(eval_payload)
    decision = decide(eval_agg)

    write_training_report(
        {**log_payload, "eval_summary": eval_agg},
        dataset_report,
        eval_agg,
        Path(args.training_md),
        Path(args.training_json),
    )
    decision_payload = {
        "decision": decision,
        "eval": eval_agg,
        "training": {
            "duration_seconds": log_payload["duration_seconds"],
            "loss_start": log_payload["loss_start"],
            "loss_end": log_payload["loss_end"],
            "best_eval": log_payload["best_eval"],
            "final_eval": log_payload["final_eval"],
            "has_nan_or_inf": log_payload["has_nan_or_inf"],
            "has_oom_or_crash": log_payload["has_oom_or_crash"],
        },
    }
    write_decision_report(decision_payload, Path(args.decision_md), Path(args.decision_json))
    print(json.dumps(decision_payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
