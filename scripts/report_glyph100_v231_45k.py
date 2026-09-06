#!/usr/bin/env python3
"""Build post-training report for Glyph-100M v2.3.1 35k->45k run."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "logs" / "glyph-100m-v2_3_1-45k" / "train.log"
CKPT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-45k"
LATEST = CKPT_DIR / "latest.pt"
STEP_45K = CKPT_DIR / "step_0045000.pt"
REPORT_MD = ROOT / "reports" / "glyph100_v2_3_1_45k_report.md"
REPORT_JSON = ROOT / "reports" / "glyph100_v2_3_1_45k_report.json"
TOKENS_PER_STEP = 4 * 512 * 8

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
RESUME_RE = re.compile(r"Resumed from step (?P<step>[\d,]+)")
RANGE_RE = re.compile(r"Training from step (?P<start>[\d,]+) to (?P<end>[\d,]+)")


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


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def checkpoint_meta(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    metadata = state.get("metadata") or {}
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size,
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config"),
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path") or metadata.get("tokenizer_path"),
        "tokenizer_sha256": state.get("tokenizer_sha256")
        or train_config.get("tokenizer_sha256")
        or metadata.get("tokenizer_sha256"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name") or metadata.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path")
        or train_config.get("dataset_metadata_path")
        or metadata.get("dataset_metadata_path"),
        "batch_size": state.get("batch_size") or train_config.get("batch_size") or metadata.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps")
        or train_config.get("gradient_accumulation_steps")
        or metadata.get("gradient_accumulation_steps"),
        "effective_tokens_per_step": state.get("effective_tokens_per_step")
        or train_config.get("effective_tokens_per_step")
        or metadata.get("effective_tokens_per_step")
        or TOKENS_PER_STEP,
    }


def parse_log() -> dict:
    steps = []
    evals = []
    checkpoints = []
    nonfinite = []
    oom = []
    crashes = []
    clean_interrupt = False
    complete_line = None
    resumes = []
    ranges = []

    for line in LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if "Exiting cleanly" in line:
            clean_interrupt = True
        if "Limited run complete" in line:
            complete_line = line
        lower = line.lower()
        if "nan" in lower or "inf" in lower or "non-finite" in lower:
            nonfinite.append(line)
        if "out of memory" in lower or "oom" in lower:
            oom.append(line)
        if "crash" in lower or "traceback" in lower or "exception" in lower:
            crashes.append(line)

        match = RESUME_RE.search(line)
        if match:
            resumes.append(int(match.group("step").replace(",", "")))
        match = RANGE_RE.search(line)
        if match:
            ranges.append(
                {
                    "start": int(match.group("start").replace(",", "")),
                    "end": int(match.group("end").replace(",", "")),
                    "line": line,
                }
            )

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
        "clean_interrupt": clean_interrupt,
        "complete_line": complete_line,
        "resumes": resumes,
        "ranges": ranges,
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


def active_duration_seconds(steps: list[dict]) -> float:
    if len(steps) < 2:
        return 0.0
    total = 0.0
    previous = parse_ts(steps[0]["ts"])
    for row in steps[1:]:
        current = parse_ts(row["ts"])
        gap = (current - previous).total_seconds()
        if gap < 10 * 60:
            total += gap
        previous = current
    return total


def main() -> None:
    if not LOG_PATH.exists():
        raise SystemExit(f"log not found: {LOG_PATH}")
    if not LATEST.exists() or not STEP_45K.exists():
        raise SystemExit("45k checkpoint missing")

    parsed = parse_log()
    steps = parsed["steps"]
    evals = parsed["evals"]
    if not steps:
        raise SystemExit("no step rows in log")

    first = steps[0]
    last = steps[-1]
    start_ts = parse_ts(first["ts"])
    end_ts = parse_ts(last["ts"])
    wall_seconds = (end_ts - start_ts).total_seconds()
    active_seconds = active_duration_seconds(steps)
    avg_toks = sum(row["toks"] for row in steps) / len(steps)
    ckpt_meta = checkpoint_meta(LATEST)
    step_meta = checkpoint_meta(STEP_45K)
    tokenizer_path = ROOT / (ckpt_meta["tokenizer_path"] or "data/processed/tokenizer.model")
    tokenizer_actual_sha = sha256(tokenizer_path)
    ckpt_size = sum(path.stat().st_size for path in CKPT_DIR.glob("*.pt"))
    ckpt_files = sorted(path.name for path in CKPT_DIR.glob("*.pt"))

    train_losses = [row["loss"] for row in steps]
    val_losses = [row["val_loss"] for row in evals]
    train_start_window = [row["loss"] for row in steps if 35000 < row["step"] <= 35500]
    train_mid_window = [row["loss"] for row in steps if 39500 <= row["step"] <= 40000]
    train_end_window = [row["loss"] for row in steps if 44500 <= row["step"] <= 45000]
    overfit_signal = (
        "no_obvious_overfit"
        if val_losses and val_losses[-1] <= val_losses[0] + 0.03
        else "watch_val_loss"
        if val_losses
        else "unknown"
    )
    expected_stage_tokens = (45000 - 35000) * TOKENS_PER_STEP

    payload = {
        "run": "glyph100_v2_3_1_35k_to_45k",
        "status": "complete" if last["step"] == 45000 and parsed["complete_line"] else "check_log",
        "log_path": str(LOG_PATH.relative_to(ROOT)),
        "checkpoint_dir": str(CKPT_DIR.relative_to(ROOT)),
        "latest_checkpoint": ckpt_meta,
        "step_45000_checkpoint": step_meta,
        "tokenizer_actual_sha256": tokenizer_actual_sha,
        "tokenizer_sha_stored": ckpt_meta["tokenizer_sha256"],
        "start_time": first["ts"],
        "end_time": last["ts"],
        "wall_duration_seconds": wall_seconds,
        "wall_duration_human": human_duration(wall_seconds),
        "active_duration_seconds": active_seconds,
        "active_duration_human": human_duration(active_seconds),
        "start_step": 35000,
        "end_step": last["step"],
        "stage_tokens_expected": expected_stage_tokens,
        "total_tokens_m": last["tokens_m"],
        "avg_tokens_per_second": round(avg_toks, 2),
        "train_loss_first_logged": first["loss"],
        "train_loss_last_logged": last["loss"],
        "train_loss_start_window_avg": round(sum(train_start_window) / len(train_start_window), 4),
        "train_loss_mid_window_avg": round(sum(train_mid_window) / len(train_mid_window), 4),
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
        "partial_files_preserved": {
            "45k_emergency_pt": (CKPT_DIR / "emergency.pt").exists(),
            "45k_partial_like_files": sorted(
                path.name
                for path in CKPT_DIR.glob("*")
                if "partial" in path.name.lower() or "emergency" in path.name.lower()
            ),
            "35k_step_0026000_pt": (ROOT / "checkpoints" / "glyph-100m-v2_3_1-35k" / "step_0026000.pt").exists(),
            "35k_emergency_pt": (ROOT / "checkpoints" / "glyph-100m-v2_3_1-35k" / "emergency.pt").exists(),
        },
        "resumes": parsed["resumes"],
        "ranges": parsed["ranges"],
        "clean_interrupt_seen": parsed["clean_interrupt"],
        "gpu_temperatures": "not logged in train.log",
        "vram_ram": "VRAM/RAM not logged in train.log; runtime telemetry was monitored separately",
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Glyph-100M v2.3.1 45k post-training report",
        "",
        "## Status",
        "",
        f"- status: `{payload['status']}`",
        f"- log: `{payload['log_path']}`",
        f"- checkpoint dir: `{payload['checkpoint_dir']}`",
        f"- latest checkpoint: `{payload['latest_checkpoint']['path']}`",
        f"- step checkpoint: `{payload['step_45000_checkpoint']['path']}`",
        "",
        "## Checkpoint metadata",
        "",
        f"- variant: `{ckpt_meta['variant']}`",
        f"- step/current_step: `{ckpt_meta['step']}` / `{ckpt_meta['current_step']}`",
        f"- dataset: `{ckpt_meta['dataset_name']}`",
        f"- tokenizer: `{ckpt_meta['tokenizer_path']}`",
        f"- tokenizer sha256 stored in checkpoint: `{ckpt_meta['tokenizer_sha256']}`",
        f"- tokenizer sha256 actual file: `{tokenizer_actual_sha}`",
        f"- batch/accum: `{ckpt_meta['batch_size']}` / `{ckpt_meta['gradient_accumulation_steps']}`",
        f"- effective tokens/step: `{ckpt_meta['effective_tokens_per_step']}`",
        "",
        "## Timing and throughput",
        "",
        f"- start: `{payload['start_time']}`",
        f"- end: `{payload['end_time']}`",
        f"- wall duration: `{payload['wall_duration_human']}`",
        f"- active duration: `{payload['active_duration_human']}`",
        f"- average tok/s: `{payload['avg_tokens_per_second']}`",
        f"- stage tokens expected: `{payload['stage_tokens_expected']:,}`",
        f"- total tokens from log: `{payload['total_tokens_m']:.2f}M`",
        "",
        "## Loss",
        "",
        f"- first logged train loss: `{payload['train_loss_first_logged']}`",
        f"- last logged train loss: `{payload['train_loss_last_logged']}`",
        f"- start-window avg loss: `{payload['train_loss_start_window_avg']}`",
        f"- mid-window avg loss: `{payload['train_loss_mid_window_avg']}`",
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
            f"- NaN/Inf markers: `{len(parsed['nonfinite'])}`",
            f"- OOM markers: `{len(parsed['oom'])}`",
            f"- crash/traceback markers: `{len(parsed['crashes'])}`",
            f"- clean interrupt seen: `{parsed['clean_interrupt']}`",
            "- GPU temps: not logged in `train.log`",
            "",
            "## Partial/emergency files",
            "",
            f"- 45k `emergency.pt`: `{payload['partial_files_preserved']['45k_emergency_pt']}`",
            f"- 45k partial-like files: `{payload['partial_files_preserved']['45k_partial_like_files']}`",
            f"- earlier 35k `step_0026000.pt`: `{payload['partial_files_preserved']['35k_step_0026000_pt']}`",
            f"- earlier 35k `emergency.pt`: `{payload['partial_files_preserved']['35k_emergency_pt']}`",
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
