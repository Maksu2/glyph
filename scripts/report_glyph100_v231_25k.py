#!/usr/bin/env python3
"""Build post-training report for Glyph-100M v2.3.1 15k->25k run."""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "logs" / "glyph-100m-v2_3_1-25k" / "train.log"
CKPT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-25k"
LATEST = CKPT_DIR / "latest.pt"
STEP_25K = CKPT_DIR / "step_0025000.pt"
REPORT_MD = ROOT / "reports" / "glyph100_v2_3_1_25k_report.md"
REPORT_JSON = ROOT / "reports" / "glyph100_v2_3_1_25k_report.json"

STEP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) step=\s*(?P<step>\d+) \| "
    r"loss=(?P<loss>[\d.]+) \| lr=(?P<lr>[\de.+\-]+) \| "
    r"tok/s=(?P<toks>[\d,]+) \| tokens=(?P<tokens>[\d.]+)M"
)
EVAL_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) eval step=\s*(?P<step>\d+) \| "
    r"val_loss=(?P<val_loss>[\d.]+)"
)
CKPT_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) Checkpoint saved: (?P<path>.+?) "
    r"\(loss=(?P<loss>[\d.]+)\)"
)


def parse_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def human_duration(seconds: float) -> str:
    minutes = int(seconds // 60)
    hours, mins = divmod(minutes, 60)
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def human_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"


def checkpoint_meta(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size,
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config"),
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path"),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path") or train_config.get("dataset_metadata_path"),
        "batch_size": state.get("batch_size") or train_config.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps")
        or train_config.get("gradient_accumulation_steps"),
        "effective_tokens_per_step": state.get("effective_tokens_per_step")
        or train_config.get("effective_tokens_per_step"),
    }


def parse_log() -> dict:
    steps = []
    evals = []
    checkpoints = []
    nonfinite = []
    oom = []
    crashes = []
    start_line = None
    complete_line = None

    for line in LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if "Training from step" in line:
            start_line = line
        if "Limited run complete" in line:
            complete_line = line
        lower = line.lower()
        if "nan" in lower or "inf" in lower or "non-finite" in lower:
            nonfinite.append(line)
        if "out of memory" in lower or "oom" in lower:
            oom.append(line)
        if "crash" in lower or "traceback" in lower or "exception" in lower:
            crashes.append(line)

        match = STEP_RE.match(line)
        if match:
            steps.append(
                {
                    "ts": match.group("ts"),
                    "step": int(match.group("step")),
                    "loss": float(match.group("loss")),
                    "lr": float(match.group("lr")),
                    "toks": int(match.group("toks").replace(",", "")),
                    "tokens_m": float(match.group("tokens")),
                }
            )
            continue

        match = EVAL_RE.match(line)
        if match:
            evals.append(
                {
                    "ts": match.group("ts"),
                    "step": int(match.group("step")),
                    "val_loss": float(match.group("val_loss")),
                }
            )
            continue

        match = CKPT_RE.match(line)
        if match:
            checkpoints.append(
                {
                    "ts": match.group("ts"),
                    "path": match.group("path"),
                    "loss": float(match.group("loss")),
                }
            )

    return {
        "steps": steps,
        "evals": evals,
        "checkpoints": checkpoints,
        "nonfinite": nonfinite,
        "oom": oom,
        "crashes": crashes,
        "start_line": start_line,
        "complete_line": complete_line,
    }


def trend(values: list[float]) -> str:
    if len(values) < 2:
        return "insufficient_data"
    delta = values[-1] - values[0]
    if delta < -0.05:
        return "falling"
    if delta > 0.05:
        return "rising"
    return "mostly_flat"


def main() -> None:
    if not LOG_PATH.exists():
        raise SystemExit(f"log not found: {LOG_PATH}")
    if not LATEST.exists() or not STEP_25K.exists():
        raise SystemExit("25k checkpoint missing")

    parsed = parse_log()
    steps = parsed["steps"]
    evals = parsed["evals"]
    if not steps:
        raise SystemExit("no step rows in log")

    first = steps[0]
    last = steps[-1]
    start_ts = parse_ts(first["ts"])
    end_ts = parse_ts(last["ts"])
    duration_seconds = (end_ts - start_ts).total_seconds()
    stage_tokens = (last["tokens_m"] - 245.76) * 1_000_000
    observed_stage_tokens = (last["step"] - 15000) * 4 * 512 * 8
    avg_toks = sum(row["toks"] for row in steps) / len(steps)
    ckpt_meta = checkpoint_meta(LATEST)
    step_meta = checkpoint_meta(STEP_25K)
    ckpt_size = sum(path.stat().st_size for path in CKPT_DIR.glob("*.pt"))
    ckpt_files = sorted(path.name for path in CKPT_DIR.glob("*.pt"))

    train_losses = [row["loss"] for row in steps]
    val_losses = [row["val_loss"] for row in evals]
    train_start_window = [row["loss"] for row in steps if 15000 < row["step"] <= 15500]
    train_end_window = [row["loss"] for row in steps if 24500 <= row["step"] <= 25000]
    overfit_signal = (
        "no_obvious_overfit"
        if val_losses and val_losses[-1] <= val_losses[0] + 0.03
        else "watch_val_loss"
        if val_losses
        else "unknown"
    )

    payload = {
        "run": "glyph100_v2_3_1_15k_to_25k",
        "status": "complete" if last["step"] == 25000 and parsed["complete_line"] else "check_log",
        "log_path": str(LOG_PATH.relative_to(ROOT)),
        "checkpoint_dir": str(CKPT_DIR.relative_to(ROOT)),
        "latest_checkpoint": ckpt_meta,
        "step_25000_checkpoint": step_meta,
        "start_time": first["ts"],
        "end_time": last["ts"],
        "duration_seconds": duration_seconds,
        "duration_human": human_duration(duration_seconds),
        "start_step": 15000,
        "end_step": last["step"],
        "stage_tokens_expected": observed_stage_tokens,
        "stage_tokens_from_log": int(stage_tokens),
        "total_tokens_m": last["tokens_m"],
        "avg_tokens_per_second": round(avg_toks, 2),
        "train_loss_first_logged": first["loss"],
        "train_loss_last_logged": last["loss"],
        "train_loss_start_window_avg": round(sum(train_start_window) / len(train_start_window), 4),
        "train_loss_end_window_avg": round(sum(train_end_window) / len(train_end_window), 4),
        "train_loss_min": min(train_losses),
        "train_loss_max": max(train_losses),
        "val_losses": evals,
        "val_loss_trend": trend(val_losses),
        "overfit_signal": overfit_signal,
        "nan_inf": parsed["nonfinite"],
        "oom": parsed["oom"],
        "crashes": parsed["crashes"],
        "checkpoint_saves": parsed["checkpoints"],
        "checkpoint_files": ckpt_files,
        "checkpoint_dir_size_bytes": ckpt_size,
        "checkpoint_dir_size_human": human_bytes(ckpt_size),
        "gpu_temperatures": "not logged in train.log",
        "vram_ram": "VRAM/RAM not logged in train.log; startup telemetry was monitored separately",
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Glyph-100M v2.3.1 25k post-training report",
        "",
        "## Status",
        "",
        f"- status: `{payload['status']}`",
        f"- log: `{payload['log_path']}`",
        f"- checkpoint dir: `{payload['checkpoint_dir']}`",
        f"- latest checkpoint: `{payload['latest_checkpoint']['path']}`",
        f"- step checkpoint: `{payload['step_25000_checkpoint']['path']}`",
        "",
        "## Checkpoint metadata",
        "",
        f"- variant: `{ckpt_meta['variant']}`",
        f"- step/current_step: `{ckpt_meta['step']}` / `{ckpt_meta['current_step']}`",
        f"- dataset: `{ckpt_meta['dataset_name']}`",
        f"- tokenizer: `{ckpt_meta['tokenizer_path']}`",
        f"- tokenizer sha256: `{ckpt_meta['tokenizer_sha256']}`",
        f"- batch/accum: `{ckpt_meta['batch_size']}` / `{ckpt_meta['gradient_accumulation_steps']}`",
        f"- effective tokens/step: `{ckpt_meta['effective_tokens_per_step']}`",
        "",
        "## Timing and throughput",
        "",
        f"- start: `{payload['start_time']}`",
        f"- end: `{payload['end_time']}`",
        f"- duration: `{payload['duration_human']}`",
        f"- average tok/s: `{payload['avg_tokens_per_second']}`",
        f"- stage tokens expected: `{payload['stage_tokens_expected']:,}`",
        f"- total tokens from log: `{payload['total_tokens_m']:.2f}M`",
        "",
        "## Loss",
        "",
        f"- first logged train loss: `{payload['train_loss_first_logged']}`",
        f"- last logged train loss: `{payload['train_loss_last_logged']}`",
        f"- start-window avg loss: `{payload['train_loss_start_window_avg']}`",
        f"- end-window avg loss: `{payload['train_loss_end_window_avg']}`",
        f"- val loss trend: `{payload['val_loss_trend']}`",
        f"- overfit signal: `{payload['overfit_signal']}`",
        "",
        "### Validation losses",
        "",
    ]
    for row in evals:
        lines.append(f"- step `{row['step']}`: val_loss `{row['val_loss']}` at `{row['ts']}`")
    lines.extend(
        [
            "",
            "## Stability",
            "",
            f"- NaN/Inf: `{len(parsed['nonfinite'])}`",
            f"- OOM: `{len(parsed['oom'])}`",
            f"- crash/traceback markers: `{len(parsed['crashes'])}`",
            "- GPU temps: not logged in `train.log`",
            "",
            "## Checkpoints",
            "",
            f"- checkpoint dir size: `{payload['checkpoint_dir_size_human']}`",
            f"- checkpoint files: `{len(ckpt_files)}`",
            "",
        ]
    )
    for name in ckpt_files:
        lines.append(f"- `{name}`")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_MD.relative_to(ROOT)} and {REPORT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
