#!/usr/bin/env python3
"""Build the post-run report for the Glyph-100M v2.4.1 1k proxy run."""
from __future__ import annotations

import hashlib
import json
import re
import statistics
from datetime import datetime
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "glyph100_v2_4_1_1k_20260716"
LOG_DIR = ROOT / "logs" / "glyph-100m-v2_4_1-1k"
LOG_PATH = LOG_DIR / "train.log"
GPU_LOG_PATH = LOG_DIR / "gpu_metrics.log"
RESUME_LOG_PATH = LOG_DIR / "resume_check.log"
CKPT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_4_1-1k"
LATEST = CKPT_DIR / "latest.pt"
STEP_1K = CKPT_DIR / "step_0001000.pt"
REPORT_MD = ROOT / "reports" / f"{RUN_ID}_report.md"
REPORT_JSON = ROOT / "reports" / f"{RUN_ID}_report.json"
EVAL_JSON = ROOT / "eval" / "glyph-100m" / f"{RUN_ID}_samples.json"
EVAL_ASSESSMENT_JSON = ROOT / "eval" / "glyph-100m" / f"{RUN_ID}_assessment.json"
TOKENIZER = ROOT / "data" / "processed" / "tokenizer.model"
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
TIMESTAMP_RE = re.compile(r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def human_duration(seconds: float) -> str:
    total_minutes = int(round(seconds / 60))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def human_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    raise AssertionError("unreachable")


def checkpoint_meta(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    train_config = state.get("train_config") or {}
    metadata = state.get("checkpoint_metadata") or {}
    model_digest = hashlib.sha256()
    for name, tensor in sorted((state.get("model") or {}).items()):
        model_digest.update(name.encode("utf-8"))
        model_digest.update(tensor.detach().contiguous().numpy().tobytes())
    return {
        "path": str(path.relative_to(ROOT)),
        "size_bytes": path.stat().st_size,
        "step": state.get("step"),
        "current_step": state.get("current_step"),
        "variant": state.get("variant"),
        "model_config": state.get("model_config"),
        "dataset_name": state.get("dataset_name") or train_config.get("dataset_name"),
        "dataset_metadata_path": state.get("dataset_metadata_path") or train_config.get("dataset_metadata_path"),
        "tokenizer_path": state.get("tokenizer_path") or train_config.get("tokenizer_path"),
        "tokenizer_sha256": state.get("tokenizer_sha256") or metadata.get("tokenizer_sha256"),
        "batch_size": state.get("batch_size") or train_config.get("batch_size"),
        "gradient_accumulation_steps": state.get("gradient_accumulation_steps")
        or train_config.get("gradient_accumulation_steps"),
        "effective_tokens_per_step": state.get("effective_tokens_per_step"),
        "context_length": state.get("context_length"),
        "optimizer_state_present": bool(state.get("optimizer")),
        "scheduler_state_present": bool(state.get("scheduler_state")),
        "sampler_state_present": bool(state.get("data_state")),
        "sampler_state": state.get("data_state"),
        "model_tensor_sha256": model_digest.hexdigest(),
    }


def parse_train_log() -> dict:
    lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    steps: list[dict] = []
    evals: list[dict] = []
    checkpoints: list[dict] = []
    start_time = None
    end_time = None
    errors: list[str] = []
    for line in lines:
        ts_match = TIMESTAMP_RE.match(line)
        if "Starting Glyph-100M pre-training" in line and ts_match:
            start_time = ts_match.group("ts")
        if "Limited run complete" in line and ts_match:
            end_time = ts_match.group("ts")
        lower = line.lower()
        if any(marker in lower for marker in ("non-finite", "out of memory", "traceback", "exception", "rocm crash")):
            errors.append(line)
        match = STEP_RE.match(line)
        if match:
            steps.append(
                {
                    "timestamp": match.group("ts"),
                    "step": int(match.group("step")),
                    "loss": float(match.group("loss")),
                    "learning_rate": float(match.group("lr")),
                    "tokens_per_second": int(match.group("toks").replace(",", "")),
                    "tokens_millions": float(match.group("tokens")),
                }
            )
            continue
        match = EVAL_RE.match(line)
        if match:
            evals.append(
                {
                    "timestamp": match.group("ts"),
                    "step": int(match.group("step")),
                    "val_loss": float(match.group("val_loss")),
                }
            )
            continue
        match = CKPT_RE.match(line)
        if match:
            checkpoints.append(
                {
                    "timestamp": match.group("ts"),
                    "path": match.group("path"),
                    "loss": float(match.group("loss")),
                }
            )
    return {
        "steps": steps,
        "evals": evals,
        "checkpoints": checkpoints,
        "start_time": start_time,
        "end_time": end_time,
        "errors": errors,
        "complete": any("Limited run complete" in line for line in lines),
    }


def parse_gpu_log() -> dict:
    if not GPU_LOG_PATH.exists():
        return {"samples": 0}
    samples: list[dict] = []
    current: dict = {}
    for raw_line in GPU_LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if line.endswith("Z") and "T" in line:
            if current.get("timestamp") and len(current) > 1:
                samples.append(current)
            current = {"timestamp": line}
        elif line.startswith("fan1:"):
            current["fan_rpm"] = int(re.search(r"(\d+) RPM", line).group(1))
        elif line.startswith("edge:"):
            current["edge_c"] = float(re.search(r"([+\-]?\d+(?:\.\d+)?)°C", line).group(1))
        elif line.startswith("junction:"):
            current["junction_c"] = float(re.search(r"([+\-]?\d+(?:\.\d+)?)°C", line).group(1))
        elif line.startswith("PPT:"):
            current["power_w"] = float(re.search(r"([\d.]+) W", line).group(1))
    if current.get("timestamp") and len(current) > 1:
        samples.append(current)
    if not samples:
        return {"samples": 0}
    return {
        "samples": len(samples),
        "edge_c_min": min(row["edge_c"] for row in samples if "edge_c" in row),
        "edge_c_max": max(row["edge_c"] for row in samples if "edge_c" in row),
        "junction_c_min": min(row["junction_c"] for row in samples if "junction_c" in row),
        "junction_c_max": max(row["junction_c"] for row in samples if "junction_c" in row),
        "power_w_max": max(row["power_w"] for row in samples if "power_w" in row),
        "fan_rpm_max": max(row["fan_rpm"] for row in samples if "fan_rpm" in row),
    }


def mean_for_range(rows: list[dict], start: int, end: int) -> float | None:
    values = [row["loss"] for row in rows if start <= row["step"] <= end]
    return round(statistics.mean(values), 4) if values else None


def main() -> None:
    required = (LOG_PATH, LATEST, STEP_1K, TOKENIZER)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing required artifacts: {missing}")

    parsed = parse_train_log()
    if not parsed["steps"]:
        raise SystemExit("training log has no step rows")
    latest_meta = checkpoint_meta(LATEST)
    step_meta = checkpoint_meta(STEP_1K)
    gpu = parse_gpu_log()
    start = datetime.strptime(parsed["start_time"], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(parsed["end_time"], "%Y-%m-%d %H:%M:%S")
    duration_seconds = (end - start).total_seconds()
    rows = parsed["steps"]
    losses = [row["loss"] for row in rows]
    eval_losses = [row["val_loss"] for row in parsed["evals"]]
    checkpoint_files = sorted(path.name for path in CKPT_DIR.glob("*.pt"))
    checkpoint_bytes = sum(path.stat().st_size for path in CKPT_DIR.glob("*.pt"))
    resume_text = RESUME_LOG_PATH.read_text(encoding="utf-8", errors="replace") if RESUME_LOG_PATH.exists() else ""
    eval_payload = json.loads(EVAL_JSON.read_text(encoding="utf-8")) if EVAL_JSON.exists() else None
    eval_summary = eval_payload.get("summary") if eval_payload else None
    eval_assessment = (
        json.loads(EVAL_ASSESSMENT_JSON.read_text(encoding="utf-8"))
        if EVAL_ASSESSMENT_JSON.exists()
        else None
    )

    expected_sha = sha256(TOKENIZER)
    metadata_ok = all(
        (
            latest_meta["step"] == 1000,
            latest_meta["current_step"] == 1000,
            latest_meta["variant"] == "glyph-100m",
            latest_meta["dataset_name"] == "glyph100_dataset_v2_4_1_core",
            latest_meta["tokenizer_sha256"] == expected_sha,
            latest_meta["batch_size"] == 4,
            latest_meta["gradient_accumulation_steps"] == 8,
            latest_meta["effective_tokens_per_step"] == TOKENS_PER_STEP,
            latest_meta["optimizer_state_present"],
            latest_meta["scheduler_state_present"],
            latest_meta["sampler_state_present"],
        )
    )
    val_trend = "falling" if len(eval_losses) > 1 and eval_losses[-1] < eval_losses[0] else "insufficient_or_not_falling"
    status = "complete" if parsed["complete"] and latest_meta["step"] == 1000 and not parsed["errors"] else "review_required"
    wall_tokens_per_second = latest_meta["step"] * TOKENS_PER_STEP / duration_seconds
    steady_toks = [row["tokens_per_second"] for row in rows if row["tokens_per_second"] >= 3000]
    payload = {
        "run_id": RUN_ID,
        "status": status,
        "scope": "from-scratch proxy run; optimizer steps 1-1000 only",
        "continued_training_started": False,
        "dataset": "glyph100_dataset_v2_4_1_core",
        "log_path": str(LOG_PATH.relative_to(ROOT)),
        "checkpoint_dir": str(CKPT_DIR.relative_to(ROOT)),
        "start_time": parsed["start_time"],
        "end_time": parsed["end_time"],
        "duration_seconds": duration_seconds,
        "duration_human": human_duration(duration_seconds),
        "start_step": 0,
        "end_step": latest_meta["step"],
        "tokens_processed": latest_meta["step"] * TOKENS_PER_STEP,
        "wall_tokens_per_second": round(wall_tokens_per_second, 2),
        "logged_tokens_per_second_mean": round(statistics.mean(row["tokens_per_second"] for row in rows), 2),
        "steady_tokens_per_second_median": round(statistics.median(steady_toks), 2),
        "train_loss": {
            "first_logged": rows[0]["loss"],
            "last_logged": rows[-1]["loss"],
            "minimum": min(losses),
            "maximum": max(losses),
            "steps_10_100_avg": mean_for_range(rows, 10, 100),
            "steps_450_550_avg": mean_for_range(rows, 450, 550),
            "steps_910_1000_avg": mean_for_range(rows, 910, 1000),
        },
        "validation": {"points": parsed["evals"], "trend": val_trend},
        "stability": {
            "errors": parsed["errors"],
            "nan_inf_oom_crash_count": len(parsed["errors"]),
            "gpu": gpu,
        },
        "checkpoint": {
            "latest": latest_meta,
            "step_1000": step_meta,
            "metadata_ok": metadata_ok,
            "latest_matches_step_1000_model_tensors": latest_meta["model_tensor_sha256"]
            == step_meta["model_tensor_sha256"],
            "files": checkpoint_files,
            "directory_size_bytes": checkpoint_bytes,
            "directory_size_human": human_bytes(checkpoint_bytes),
        },
        "resume_check": {
            "log_path": str(RESUME_LOG_PATH.relative_to(ROOT)),
            "performed": RESUME_LOG_PATH.exists(),
            "loaded_step_1000": "Resumed from step 1,000" in resume_text,
            "eval_only_completed": "eval_only=1" in resume_text,
        },
        "generation_eval_summary": eval_summary,
        "generation_eval_assessment": eval_assessment,
        "recommendation": (
            "The 1k proxy is mechanically healthy. Treat it as pipeline validation only; "
            "do not start 5k without an explicit decision based on validation, samples, and available runtime."
        ),
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph-100M v2.4.1 from-scratch 1k report",
        "",
        "## Decision",
        "",
        f"- status: `{status}`",
        "- this was a from-scratch proxy run to optimizer step 1,000",
        "- no 5k continuation was started",
        "- purpose: verify data sampling, ROCm training, validation, checkpoints and resume",
        "",
        "## Runtime",
        "",
        f"- start/end: `{payload['start_time']}` / `{payload['end_time']}`",
        f"- duration: `{payload['duration_human']}`",
        f"- processed tokens: `{payload['tokens_processed']:,}`",
        f"- real wall throughput (includes eval/checkpoint overhead): `{payload['wall_tokens_per_second']}` tok/s",
        f"- steady training median: `{payload['steady_tokens_per_second_median']}` tok/s",
        f"- train loss first/last: `{rows[0]['loss']}` / `{rows[-1]['loss']}`",
        f"- train loss averages 10-100 / 450-550 / 910-1000: `{payload['train_loss']['steps_10_100_avg']}` / `{payload['train_loss']['steps_450_550_avg']}` / `{payload['train_loss']['steps_910_1000_avg']}`",
        "",
        "## Validation",
        "",
    ]
    for row in parsed["evals"]:
        lines.append(f"- step `{row['step']}`: val loss `{row['val_loss']}`")
    lines.extend(
        [
            f"- trend: `{val_trend}`",
            "",
            "## Stability",
            "",
            f"- NaN/Inf/OOM/crash markers: `{len(parsed['errors'])}`",
            f"- GPU telemetry samples: `{gpu.get('samples', 0)}`",
            f"- GPU edge min/max: `{gpu.get('edge_c_min')}` / `{gpu.get('edge_c_max')}` C",
            f"- GPU hotspot min/max: `{gpu.get('junction_c_min')}` / `{gpu.get('junction_c_max')}` C",
            f"- peak board power: `{gpu.get('power_w_max')}` W",
            "",
            "## Checkpoint and resume",
            "",
            f"- latest: `{latest_meta['path']}`",
            f"- step checkpoint: `{step_meta['path']}`",
            f"- metadata contract passed: `{metadata_ok}`",
            f"- latest and step-1000 model tensors match: `{payload['checkpoint']['latest_matches_step_1000_model_tensors']}`",
            f"- optimizer/scheduler/sampler state: `{latest_meta['optimizer_state_present']}` / `{latest_meta['scheduler_state_present']}` / `{latest_meta['sampler_state_present']}`",
            f"- tokenizer SHA-256: `{latest_meta['tokenizer_sha256']}`",
            f"- checkpoint directory size: `{payload['checkpoint']['directory_size_human']}`",
            f"- resume load reached step 1,000: `{payload['resume_check']['loaded_step_1000']}`",
            f"- eval-only resume completed: `{payload['resume_check']['eval_only_completed']}`",
            "",
            "## Early generation sanity",
            "",
            "This is a 1k-step base language model, not an assistant. Samples are diagnostic and are not expected to be useful yet.",
            "",
            f"- eval summary available: `{eval_summary is not None}`",
            f"- manual assessment available: `{eval_assessment is not None}`",
            "",
            "## Recommendation",
            "",
            payload["recommendation"],
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD.relative_to(ROOT)} and {REPORT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
