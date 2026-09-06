#!/usr/bin/env python3
"""
Glyph Training Dashboard.

Pure stdlib HTTP server; no extra runtime dependencies.
Usage: python3 web/server.py [port]   (default: 8080)
"""

import html
import hashlib
import hmac
import json
import math
import os
import re
import subprocess
import threading
import time
from datetime import datetime, time as day_time, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_NAME = "Glyph"
MODEL_NAME = "Glyph-100M"
MODEL_VARIANT = "Base"
MODEL_FULL_NAME = f"{MODEL_NAME} {MODEL_VARIANT}"
MODEL_DESCRIPTION = (
    "Glyph-100M controlled training on ROCm/RX 5500 XT."
)
LEGACY_27M_LOG_FILE = BASE_DIR / "logs" / "train.log"
GLYPH27_LOG_FILE = BASE_DIR / "logs" / "glyph-27m" / "train.log"
GLYPH100_LOG_FILE = BASE_DIR / "logs" / "glyph-100m" / "train.log"
GLYPH100_PREFLIGHT_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-preflight" / "train.log"
GLYPH100_V231_25K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-25k" / "train.log"
GLYPH100_V231_35K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-35k" / "train.log"
GLYPH100_V231_45K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-45k" / "train.log"
GLYPH100_V231_50K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-50k" / "train.log"
GLYPH100_V241_10K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_4_1-10k" / "train.log"
GLYPH100_V242_15K_LOG_FILE = BASE_DIR / "logs" / "glyph-100m-v2_4_2-15k" / "train.log"
GLYPH100_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m" / "emergency_stop.json"
GLYPH100_PREFLIGHT_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-preflight" / "emergency_stop.json"
GLYPH100_V231_25K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-25k" / "emergency_stop.json"
GLYPH100_V231_35K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-35k" / "emergency_stop.json"
GLYPH100_V231_45K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-45k" / "emergency_stop.json"
GLYPH100_V231_50K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_3_1-50k" / "emergency_stop.json"
GLYPH100_V241_10K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_4_1-10k" / "emergency_stop.json"
GLYPH100_V242_15K_EMERGENCY_FILE = BASE_DIR / "logs" / "glyph-100m-v2_4_2-15k" / "emergency_stop.json"
SFT_LOG_FILE = BASE_DIR / "logs" / "sft-v0.log"
RESOURCE_STATE_FILE = BASE_DIR / "logs" / "resource_mode.json"
WATCHDOG_STATE_FILE = BASE_DIR / "logs" / "training-watchdog-state.json"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"
SFT_CHECKPOINT_DIR = CHECKPOINT_DIR / "sft-v0"
SFT_PREPARE_REPORT_FILE = BASE_DIR / "data" / "sft" / "reports" / "sft_v0_prepare_report.json"
SFT_EVAL_JSON_FILE = BASE_DIR / "eval" / "sft-v0" / "base_vs_sft_comparison.json"
SFT_EVAL_REPORT_FILE = BASE_DIR / "eval" / "sft-v0" / "base_vs_sft_comparison.md"
SFT_EVAL_V2_JSON_FILE = BASE_DIR / "eval" / "sft-v0-v2" / "base_vs_sft_comparison_v2.json"
SFT_EVAL_V2_REPORT_FILE = BASE_DIR / "eval" / "sft-v0-v2" / "base_vs_sft_comparison_v2.md"
SFT_DECODING_SWEEP_JSON_FILE = BASE_DIR / "eval" / "sft-v0" / "decoding_sweep.json"
GLYPH100_PARAM_REPORT_FILE = BASE_DIR / "reports" / "glyph100_parameter_report.json"
GLYPH100_SMOKE_REPORT_FILE = BASE_DIR / "reports" / "glyph100_rocm_smoke.json"
GLYPH100_STAGE_SMOKE_REPORT_FILE = BASE_DIR / "reports" / "glyph100_rocm_smoke_accum8.json"
GLYPH100_DATASET_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph_100m_dataset_stats.json"
GLYPH100_DATASET_V2_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_stats.json"
GLYPH100_DATASET_V2_1_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_1_stats.json"
GLYPH100_DATASET_V2_2_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_2_stats.json"
GLYPH100_DATASET_V2_3_1_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_3_1_stats.json"
GLYPH100_DATASET_V2_4_1_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_4_1_stats.json"
GLYPH100_DATASET_V2_4_2_STATS_FILE = BASE_DIR / "data" / "reports" / "glyph100_dataset_v2_4_2_stats.json"
GLYPH100_METADATA_FILE = BASE_DIR / "data" / "processed" / "glyph100_metadata.json"
GLYPH100_V231_25K_EVAL_REPORT_FILE = BASE_DIR / "reports" / "glyph100_v2_3_1_25k_eval_report.md"
GLYPH100_V231_35K_EVAL_REPORT_FILE = BASE_DIR / "reports" / "glyph100_v2_3_1_35k_eval_report.md"
GLYPH100_V231_45K_EVAL_REPORT_FILE = BASE_DIR / "reports" / "glyph100_v2_3_1_45k_eval_report.md"
GLYPH100_V231_50K_DECISION_REPORT_FILE = BASE_DIR / "reports" / "glyph100_v2_3_1_final_decision.md"
GLYPH100_V241_10K_EVAL_REPORT_FILE = BASE_DIR / "reports" / "glyph100_v2_4_1_10k_20260718_report.md"
ASSET_DIR = BASE_DIR / "web" / "assets"
STATIC_ASSETS = {
    "/assets/glyph_mark.png": ASSET_DIR / "glyph_mark.png",
    "/assets/glyph_wordmark.png": ASSET_DIR / "glyph_wordmark.png",
    "/assets/glyph_logo.png": ASSET_DIR / "glyph_logo.png",
    "/assets/glyph_logotext.png": ASSET_DIR / "glyph_logotext.png",
}
GEMMA_STATUS_FILE = BASE_DIR / "reports" / "gemma4_eval" / "status.json"
GEMMA_SUMMARY_FILE = BASE_DIR / "reports" / "gemma4_eval" / "latest_summary.json"
GEMMA_REPORT_FILE = BASE_DIR / "reports" / "gemma4_eval" / "latest.jsonl"
GEMMA_SERVICE = "ai-model-gemma4-eval.service"
GEMMA_DEFAULT_PROMPTS = int(os.environ.get("GEMMA4_EVAL_LIMIT", "60"))
GEMMA_SAMPLE_TOKENS = int(
    os.environ.get("GLYPH_EVAL_MAX_TOKENS", os.environ.get("MINIGPT_EVAL_MAX_TOKENS", "60"))
)
GEMMA_MANUAL_CODE = os.environ.get("GEMMA_MANUAL_CODE", "").strip()
GEMMA_MANUAL_CODE_SHA256 = os.environ.get("GEMMA_MANUAL_CODE_SHA256", "").strip().lower()
GEMMA_MANUAL_WINDOW = os.environ.get("GEMMA_MANUAL_WINDOW", "01:00-05:00")
GEMMA_MANUAL_REQUIRE_WINDOW = os.environ.get("GEMMA_MANUAL_REQUIRE_WINDOW", "true").lower() not in {
    "0",
    "false",
    "no",
    "off",
}

MAX_STEPS = int(os.environ.get("TRAIN_MAX_STEPS", "200000"))
GLYPH100_STAGE1_STEPS = 1_000
GLYPH100_STAGE2_STEPS = 10_000
GLYPH100_PREFLIGHT_STEPS = 15_000
GLYPH100_PREFLIGHT_START_STEP = 10_000
GLYPH100_V231_25K_STEPS = 25_000
GLYPH100_V231_25K_START_STEP = 15_000
GLYPH100_V231_35K_STEPS = 35_000
GLYPH100_V231_35K_START_STEP = 25_000
GLYPH100_V231_45K_STEPS = 45_000
GLYPH100_V231_45K_START_STEP = 35_000
GLYPH100_V231_50K_STEPS = 50_000
GLYPH100_V231_50K_START_STEP = 45_000
GLYPH100_V241_10K_STEPS = 10_000
GLYPH100_V241_10K_START_STEP = 5_000
GLYPH100_V242_15K_STEPS = 15_000
GLYPH100_ACTIVE_STAGE_STEPS = int(os.environ.get("GLYPH100_ACTIVE_STAGE_STEPS", str(GLYPH100_STAGE2_STEPS)))
SCHEDULE_TZ = os.environ.get("TRAIN_SCHEDULE_TZ", "Europe/Warsaw")
DEFAULT_TOKENS_PER_STEP = 32 * 256
GLYPH100_TOKENS_PER_STEP = 4 * 512 * 8

RATE_LIMITS = {
    "gemma_ip": (3, 86400),
    "gemma_device": (3, 86400),
    "gemma_global": (4, 86400),
}
RATE_BUCKETS = {}
RATE_LOCK = threading.Lock()


# Log parsing

def parse_log(log_file: Path = LEGACY_27M_LOG_FILE):
    """Return parsed train steps, eval records and the latest real training start timestamp."""
    steps = []
    evals = []
    started_at = None
    step_re = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) step=\s*(\d+) \| "
        r"loss=([\d.]+) \| lr=([\de.+\-]+) \| tok/s=([\d,]+) \| tokens=([\d.]+)M"
    )
    eval_re = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) eval step=\s*(\d+) \| "
        r"val_loss=([\d.]+)"
    )

    try:
        with open(log_file, encoding="utf-8", errors="replace") as f:
            for line in f:
                if "Training from step" in line:
                    m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                    if m:
                        started_at = m.group(1)

                m = step_re.match(line)
                if m:
                    steps.append({
                        "ts": m.group(1),
                        "step": int(m.group(2)),
                        "loss": float(m.group(3)),
                        "lr": float(m.group(4)),
                        "toks": int(m.group(5).replace(",", "")),
                        "tokens_m": float(m.group(6)),
                    })
                    continue

                m = eval_re.match(line)
                if m:
                    evals.append({
                        "ts": m.group(1),
                        "step": int(m.group(2)),
                        "val_loss": float(m.group(3)),
                    })
    except FileNotFoundError:
        pass

    return steps, evals, started_at


def tokens_per_step(steps, default_tokens_per_step=DEFAULT_TOKENS_PER_STEP):
    for prev, cur in zip(reversed(steps[:-1]), reversed(steps[1:])):
        step_delta = cur["step"] - prev["step"]
        token_delta = (cur["tokens_m"] - prev["tokens_m"]) * 1_000_000
        if step_delta > 0 and token_delta > 0:
            return token_delta / step_delta
    return default_tokens_per_step


def format_duration(seconds):
    if seconds is None or seconds <= 0 or not math.isfinite(seconds):
        return "—"
    minutes = int(seconds // 60)
    days, rem = divmod(minutes, 1440)
    hours, mins = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


def recent_stats(steps, total_steps=MAX_STEPS, default_tokens_per_step=DEFAULT_TOKENS_PER_STEP):
    if not steps:
        return {
            "avg_toks": 0,
            "steps_per_hour": 0,
            "eta": "—",
            "last_age": "—",
            "tokens_per_step": default_tokens_per_step,
        }

    latest = steps[-1]
    recent = steps[-30:]
    avg_toks = sum(s["toks"] for s in recent) / len(recent)
    tps = tokens_per_step(steps, default_tokens_per_step)
    steps_per_hour = avg_toks / tps * 3600 if tps else 0
    remaining = max(0, total_steps - latest["step"])
    eta_seconds = remaining / steps_per_hour * 3600 if steps_per_hour else None

    try:
        last_ts = datetime.strptime(latest["ts"], "%Y-%m-%d %H:%M:%S")
        age_seconds = (datetime.now() - last_ts).total_seconds()
        last_age = format_duration(age_seconds)
    except ValueError:
        last_age = "—"

    return {
        "avg_toks": avg_toks,
        "steps_per_hour": steps_per_hour,
        "eta": format_duration(eta_seconds),
        "last_age": last_age,
        "tokens_per_step": tps,
    }


def human_bytes(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"


def checkpoint_info(ckpt_dir: Path = CHECKPOINT_DIR):
    latest = ckpt_dir / "latest.pt"
    if not latest.exists():
        return {"label": "nie znaleziono", "size": "—", "mtime": "—"}

    stat = latest.stat()
    return {
        "label": latest.name,
        "size": human_bytes(stat.st_size),
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
    }


def sft_checkpoint_info():
    latest = SFT_CHECKPOINT_DIR / "glyph-27m-sft-v0-latest.pt"
    final = SFT_CHECKPOINT_DIR / "glyph-27m-sft-v0-final.pt"
    chosen = latest if latest.exists() else final
    if not chosen.exists():
        return {"label": "nie znaleziono", "size": "—", "mtime": "—"}
    stat = chosen.stat()
    return {
        "label": chosen.name,
        "size": human_bytes(stat.st_size),
        "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
    }


def sft_eval_state():
    data = load_json_file(SFT_EVAL_JSON_FILE)
    summary = data.get("summary") or {}
    counts = summary.get("winner_counts") or {}
    quality = summary.get("quality_counts") or {}
    prompt_count = summary.get("prompt_count") or sum(counts.values())
    v2_data = load_json_file(SFT_EVAL_V2_JSON_FILE)
    v2_summary = v2_data.get("summary") or {}
    v2_counts = v2_summary.get("winner_counts") or {}
    sweep = load_json_file(SFT_DECODING_SWEEP_JSON_FILE)
    if not summary:
        return {
            "status": "pending",
            "report": "—",
            "prompt_count": "—",
            "winner_line": "—",
            "quality_line": "—",
            "v2_status": "pending",
            "v2_winner_line": "—",
            "v2_delta": "—",
            "sweep_status": "pending",
            "sweep_line": "—",
            "verdict": "Eval Base vs SFT jeszcze nie został zapisany.",
        }
    v2_status = "completed" if v2_summary else "pending"
    v2_winner_line = (
        f"SFT {v2_counts.get('sft', 0)} · base {v2_counts.get('base', 0)} · "
        f"remis {v2_counts.get('tie', 0)} · oba złe {v2_counts.get('both_bad', 0)}"
        if v2_summary
        else "—"
    )
    sweep_status = "completed" if sweep else "pending"
    sweep_line = "—"
    if sweep:
        sweep_line = (
            f"preset {sweep.get('recommended_demo_preset', '—')} · "
            f"best {sweep.get('best_overall_preset', '—')} · "
            f"{sweep.get('prompt_count', '—')} promptów"
        )
    return {
        "status": "completed",
        "report": SFT_EVAL_REPORT_FILE.name if SFT_EVAL_REPORT_FILE.exists() else SFT_EVAL_JSON_FILE.name,
        "prompt_count": str(prompt_count or "—"),
        "winner_line": (
            f"SFT {counts.get('sft', 0)} · base {counts.get('base', 0)} · "
            f"remis {counts.get('tie', 0)} · oba złe {counts.get('both_bad', 0)}"
        ),
        "quality_line": (
            f"web śmieci base/SFT {quality.get('base_web_garbage', 0)}/{quality.get('sft_web_garbage', 0)} · "
            f"powtórzenia {quality.get('base_repetition', 0)}/{quality.get('sft_repetition', 0)}"
        ),
        "v2_status": v2_status,
        "v2_report": SFT_EVAL_V2_REPORT_FILE.name if SFT_EVAL_V2_REPORT_FILE.exists() else "—",
        "v2_winner_line": v2_winner_line,
        "v2_delta": (
            f"słabe wygrane SFT usunięte: {v2_summary.get('weak_sft_wins_removed', '—')}"
            if v2_summary
            else "—"
        ),
        "sweep_status": sweep_status,
        "sweep_line": sweep_line,
        "verdict": (
            "SFT v0 poprawia format odpowiedzi i kończenie generacji, ale nadal widać dryf, "
            "powtórzenia i schematyczny ton."
        ),
    }


def parse_sft_log():
    steps = []
    evals = []
    final = None
    step_re = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) sft step=\s*(\d+) \| epoch=(\d+) \| "
        r"loss=([\d.]+) \| lr=([\de.+\-]+) \| tok/s=([\d,]+)"
    )
    eval_re = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) sft (?:eval|final_eval) step=\s*(\d+) \| "
        r"val_loss=([\d.]+)"
    )
    try:
        with open(SFT_LOG_FILE, encoding="utf-8", errors="replace") as f:
            for line in f:
                m = step_re.match(line)
                if m:
                    steps.append({
                        "ts": m.group(1),
                        "step": int(m.group(2)),
                        "epoch": int(m.group(3)),
                        "loss": float(m.group(4)),
                        "lr": float(m.group(5)),
                        "toks": int(m.group(6).replace(",", "")),
                    })
                    continue
                m = eval_re.match(line)
                if m:
                    record = {
                        "ts": m.group(1),
                        "step": int(m.group(2)),
                        "val_loss": float(m.group(3)),
                    }
                    evals.append(record)
                    final = record
    except FileNotFoundError:
        pass
    return steps, evals, final


def sft_state():
    steps, evals, final = parse_sft_log()
    latest = steps[-1] if steps else {}
    report = load_json_file(SFT_PREPARE_REPORT_FILE)
    ckpt = sft_checkpoint_info()
    train_examples = report.get("train_examples")
    val_examples = report.get("val_examples")
    train_tokens = report.get("train_tokens")
    val_tokens = report.get("val_tokens")
    dataset_name = Path(report.get("input", "sft_v0_expanded")).name
    eval_state = sft_eval_state()
    return {
        "phase": "SFT v0" if ckpt["label"] != "nie znaleziono" else "Pretraining complete",
        "dataset": dataset_name,
        "split": f"{train_examples or '—'} / {val_examples or '—'}",
        "tokens": f"{(train_tokens or 0) + (val_tokens or 0):,}" if train_tokens or val_tokens else "—",
        "step": latest.get("step", 0),
        "epoch": latest.get("epoch", 0),
        "loss": f"{latest.get('loss'):.4f}" if latest.get("loss") is not None else "—",
        "val_loss": f"{final.get('val_loss'):.4f}" if final else "—",
        "lr": f"{latest.get('lr'):.2e}" if latest.get("lr") else "—",
        "toks": f"{latest.get('toks', 0):,}" if latest else "—",
        "device": "ROCm / RX 5500 XT",
        "base_checkpoint": "glyph-27m-base-final",
        "checkpoint": ckpt,
        "updated": final.get("ts") if final else latest.get("ts", "—"),
        "eval": eval_state,
    }


def hidden_sft_state():
    return {
        "phase": "hidden",
        "dataset": "—",
        "split": "—",
        "tokens": "—",
        "step": 0,
        "epoch": 0,
        "loss": "—",
        "val_loss": "—",
        "lr": "—",
        "toks": "—",
        "device": "—",
        "base_checkpoint": "—",
        "checkpoint": {"label": "—", "size": "—", "mtime": "—"},
        "updated": "—",
        "eval": {
            "status": "hidden",
            "report": "—",
            "prompt_count": "—",
            "winner_line": "—",
            "quality_line": "—",
            "v2_status": "hidden",
            "v2_winner_line": "—",
            "v2_delta": "—",
            "sweep_status": "hidden",
            "sweep_line": "—",
            "verdict": "Ukryte w aktywnym widoku Glyph-100M.",
        },
    }


def glyph100_state():
    param_report = load_json_file(GLYPH100_PARAM_REPORT_FILE)
    reports = param_report.get("reports") or []
    variant = next((item for item in reports if item.get("variant") == "glyph-100m"), {})
    cfg = variant.get("model_config") or {}
    smoke = load_json_file(GLYPH100_SMOKE_REPORT_FILE)
    stage_smoke = load_json_file(GLYPH100_STAGE_SMOKE_REPORT_FILE)
    dataset = load_json_file(GLYPH100_DATASET_STATS_FILE)
    dataset_v2 = load_json_file(GLYPH100_DATASET_V2_STATS_FILE)
    dataset_v2_1 = load_json_file(GLYPH100_DATASET_V2_1_STATS_FILE)
    dataset_v2_2 = load_json_file(GLYPH100_DATASET_V2_2_STATS_FILE)
    dataset_v2_3_1 = load_json_file(GLYPH100_DATASET_V2_3_1_STATS_FILE)
    dataset_v2_4_1 = load_json_file(GLYPH100_DATASET_V2_4_1_STATS_FILE)
    dataset_v2_4_2 = load_json_file(GLYPH100_DATASET_V2_4_2_STATS_FILE)
    metadata = load_json_file(GLYPH100_METADATA_FILE)
    eval25k_complete = GLYPH100_V231_25K_EVAL_REPORT_FILE.exists()
    eval35k_complete = GLYPH100_V231_35K_EVAL_REPORT_FILE.exists()
    eval45k_complete = GLYPH100_V231_45K_EVAL_REPORT_FILE.exists()
    eval50k_complete = GLYPH100_V231_50K_DECISION_REPORT_FILE.exists()
    eval_v241_10k_complete = GLYPH100_V241_10K_EVAL_REPORT_FILE.exists()
    run_v242_15k_active = GLYPH100_V242_15K_LOG_FILE.exists()
    run_v241_10k_active = GLYPH100_V241_10K_LOG_FILE.exists() and not run_v242_15k_active
    run50k_active = GLYPH100_V231_50K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active
    run45k_active = GLYPH100_V231_45K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active
    run35k_active = GLYPH100_V231_35K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active
    run25k_active = GLYPH100_V231_25K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active and not run35k_active
    preflight_active = GLYPH100_PREFLIGHT_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active and not run35k_active and not run25k_active
    v231_active = run50k_active or run45k_active or run35k_active or run25k_active or preflight_active
    active_log = (
        GLYPH100_V242_15K_LOG_FILE
        if run_v242_15k_active
        else GLYPH100_V241_10K_LOG_FILE
        if run_v241_10k_active
        else GLYPH100_V231_50K_LOG_FILE
        if run50k_active
        else GLYPH100_V231_45K_LOG_FILE
        if run45k_active
        else GLYPH100_V231_35K_LOG_FILE
        if run35k_active
        else GLYPH100_V231_25K_LOG_FILE
        if run25k_active
        else GLYPH100_PREFLIGHT_LOG_FILE
        if preflight_active
        else GLYPH100_LOG_FILE
    )
    active_total_steps = (
        GLYPH100_V242_15K_STEPS
        if run_v242_15k_active
        else GLYPH100_V241_10K_STEPS
        if run_v241_10k_active
        else GLYPH100_V231_50K_STEPS
        if run50k_active
        else GLYPH100_V231_45K_STEPS
        if run45k_active
        else GLYPH100_V231_35K_STEPS
        if run35k_active
        else GLYPH100_V231_25K_STEPS
        if run25k_active
        else GLYPH100_PREFLIGHT_STEPS
        if preflight_active
        else GLYPH100_ACTIVE_STAGE_STEPS
    )
    stage_steps, stage_evals, stage_started_at = parse_log(active_log)
    latest_stage = stage_steps[-1] if stage_steps else {}
    latest_stage_eval = stage_evals[-1] if stage_evals else {}
    emergency_file = (
        GLYPH100_V242_15K_EMERGENCY_FILE
        if run_v242_15k_active
        else GLYPH100_V241_10K_EMERGENCY_FILE
        if run_v241_10k_active
        else GLYPH100_V231_50K_EMERGENCY_FILE
        if run50k_active
        else GLYPH100_V231_45K_EMERGENCY_FILE
        if run45k_active
        else GLYPH100_V231_35K_EMERGENCY_FILE
        if run35k_active
        else GLYPH100_V231_25K_EMERGENCY_FILE
        if run25k_active
        else GLYPH100_PREFLIGHT_EMERGENCY_FILE
        if preflight_active
        else GLYPH100_EMERGENCY_FILE
    )
    emergency = load_json_file(emergency_file)
    emergency_reason = emergency.get("reason")
    emergency_step = emergency.get("step")
    emergency_micro_step = emergency.get("micro_step")

    max_ok_batch = smoke.get("max_ok_batch_size")
    stage_smoke_ok = bool(stage_smoke.get("max_ok_batch_size"))
    batch_line = (
        "batch 4 accum 8 OK · batch 8 OK but tight · batch 16 OOM"
        if stage_smoke_ok
        else "batch 4 recommended · batch 8 OK but tight · batch 16 OOM"
        if max_ok_batch
        else "pending"
    )
    if dataset.get("train_tokens"):
        dataset_line = (
            f"{dataset.get('train_tokens', 0):,} train · "
            f"{dataset.get('val_tokens', 0):,} val"
        )
    else:
        dataset_line = "pending"

    stage_step = latest_stage.get("step", 0)
    emergency_active = bool(emergency_reason and (not latest_stage or emergency_step is None or emergency_step > stage_step))
    if emergency_active:
        stage_status = (
            f"v2.4.2 15k checkpoint run stopped: {emergency_reason}"
            if run_v242_15k_active
            else f"v2.4.1 10k run stopped: {emergency_reason}"
            if run_v241_10k_active
            else f"v2.3.1 50k diagnostic stopped: {emergency_reason}"
            if run50k_active
            else f"v2.3.1 45k run stopped: {emergency_reason}"
            if run45k_active
            else f"v2.3.1 35k run stopped: {emergency_reason}"
            if run35k_active
            else f"v2.3.1 25k run stopped: {emergency_reason}"
            if run25k_active
            else f"v2.3.1 preflight stopped: {emergency_reason}"
            if preflight_active
            else f"stage 2 stopped: {emergency_reason}"
        )
    elif not stage_steps:
        stage_status = "prepared / waiting for approval"
    elif run_v242_15k_active and stage_step >= GLYPH100_V242_15K_STEPS:
        stage_status = "v2.4.2 15k checkpoint complete · eval pending"
    elif run_v242_15k_active:
        stage_status = "v2.4.2 controlled 10k→15k run"
    elif run_v241_10k_active and stage_step >= GLYPH100_V241_10K_STEPS:
        stage_status = (
            "v2.4.1 10k complete · eval complete"
            if eval_v241_10k_complete
            else "v2.4.1 10k complete · eval pending"
        )
    elif run_v241_10k_active and stage_step >= GLYPH100_V241_10K_START_STEP:
        stage_status = "v2.4.1 training to 10k"
    elif run50k_active and stage_step >= GLYPH100_V231_50K_STEPS:
        stage_status = "v2.3.1 pretraining stopped · 44k best · 50k diagnostic complete" if eval50k_complete else "v2.3.1 50k diagnostic complete · decision pending"
    elif run50k_active and stage_step >= GLYPH100_V231_50K_START_STEP:
        stage_status = "v2.3.1 50k diagnostic running"
    elif run45k_active and stage_step >= GLYPH100_V231_45K_STEPS:
        stage_status = "v2.3.1 45k run complete · eval complete" if eval45k_complete else "v2.3.1 45k run complete · eval pending"
    elif run45k_active and stage_step >= GLYPH100_V231_45K_START_STEP:
        stage_status = "v2.3.1 45k run running"
    elif run35k_active and stage_step >= GLYPH100_V231_35K_STEPS:
        stage_status = "v2.3.1 35k run complete · eval complete" if eval35k_complete else "v2.3.1 35k run complete · eval pending"
    elif run35k_active and stage_step >= GLYPH100_V231_35K_START_STEP:
        stage_status = "v2.3.1 35k run running"
    elif run25k_active and stage_step >= GLYPH100_V231_25K_STEPS:
        stage_status = "v2.3.1 25k run complete · eval complete" if eval25k_complete else "v2.3.1 25k run complete · eval pending"
    elif run25k_active and stage_step >= GLYPH100_V231_25K_START_STEP:
        stage_status = "v2.3.1 25k run running"
    elif preflight_active and stage_step >= GLYPH100_PREFLIGHT_STEPS:
        stage_status = "v2.3.1 preflight complete"
    elif preflight_active and stage_step >= GLYPH100_PREFLIGHT_START_STEP:
        stage_status = "v2.3.1 preflight running"
    elif stage_step >= GLYPH100_ACTIVE_STAGE_STEPS:
        stage_status = "stage 2 complete"
    elif stage_step >= GLYPH100_STAGE1_STEPS:
        stage_status = "stage 2 training"
    else:
        stage_status = "stage 1 training"
    if stage_step == GLYPH100_STAGE1_STEPS and not emergency_active:
        stage_status = "stage 1 complete"

    return {
        "status": stage_status,
        "name": variant.get("display_name", "Glyph-100M"),
        "params": (
            f"{variant.get('unique_parameters', 0) / 1_000_000:.2f}M unique · "
            f"{variant.get('logical_total_parameters', 0) / 1_000_000:.2f}M logical"
            if variant
            else "pending"
        ),
        "config": (
            f"{cfg.get('n_layers', '—')}L · {cfg.get('n_heads', '—')}H · "
            f"d={cfg.get('d_model', '—')} · ctx={cfg.get('context_len', '—')}"
            if cfg
            else "pending"
        ),
        "dataset": (
            "glyph100_dataset_v2_4_2_core"
            if run_v242_15k_active
            else "glyph100_dataset_v2_4_1_core"
            if run_v241_10k_active
            else "glyph100_v2_3_1"
            if v231_active
            else metadata.get("dataset_name") or dataset.get("dataset_name") or "glyph100_stage1_candidate"
        ),
        "dataset_note": (
            "v2.4.2 corrective source mix; controlled continuation from 10k to 15k total; automatic stop for evaluation"
            if run_v242_15k_active
            else "v2.4.1 source-aware core corpus; 10k complete; eval recommends a corrective v2.4.2 source mix"
            if run_v241_10k_active and eval_v241_10k_complete
            else "v2.4.1 source-aware core corpus; controlled continuation from 5k to 10k total"
            if run_v241_10k_active
            else "v2.3.1 diagnostic 45k→50k finished; 50k is healthy but did not beat 44k, so pretraining is stopped"
            if run50k_active
            else "v2.3.1 continuation 35k→45k; cleaner FineWeb2-filtered dataset; not stage 3 / 50k"
            if run45k_active
            else "v2.3.1 continuation 25k→35k; cleaner FineWeb2-filtered dataset; not stage 3 / 50k"
            if run35k_active
            else "v2.3.1 continuation 15k→25k; cleaner FineWeb2-filtered dataset; not stage 3 / 50k"
            if run25k_active
            else "v2.3.1 preflight 10k→15k; cleaner FineWeb2-filtered dataset; not stage 3 / 50k"
            if preflight_active
            else
            "stage 2 used this candidate; glyph100_dataset_v2_2 was built with legacy=0 and Wikipedia capped, but it is too small for 50k without another clean source"
            if dataset_v2_2
            else "stage 2 used this candidate; glyph100_dataset_v2_1 is cleaner and under review before any stage 3 / 50k decision"
            if dataset_v2_1
            else "stage 2 used this candidate; glyph100_dataset_v2 exists but quality audit says stage 3 is still pending"
            if dataset_v2
            else "stage 2 early-training candidate; not the final cleaner corpus for 50k+ runs"
        ),
        "dataset_tokens": (
            f"{dataset_v2_4_2.get('train_tokens', 0):,} train · {dataset_v2_4_2.get('val_tokens', 0):,} val"
            if run_v242_15k_active and dataset_v2_4_2.get("train_tokens")
            else f"{dataset_v2_4_1.get('train_tokens', 0):,} train · {dataset_v2_4_1.get('val_tokens', 0):,} val"
            if run_v241_10k_active and dataset_v2_4_1.get("train_tokens")
            else f"{dataset_v2_3_1.get('train_tokens', 0):,} train · {dataset_v2_3_1.get('val_tokens', 0):,} val"
            if v231_active and dataset_v2_3_1.get("train_tokens")
            else dataset_line
        ),
        "accepted_docs": (
            f"{dataset_v2_4_2.get('accepted_docs', dataset_v2_4_2.get('selected_docs', dataset_v2_4_2.get('total_docs', 0))):,}"
            if run_v242_15k_active and dataset_v2_4_2
            else f"{dataset_v2_4_1.get('accepted_docs', dataset_v2_4_1.get('selected_docs', dataset_v2_4_1.get('total_docs', 0))):,}"
            if run_v241_10k_active and dataset_v2_4_1
            else f"{dataset_v2_3_1.get('accepted_docs', 0):,}"
            if v231_active and dataset_v2_3_1.get("accepted_docs")
            else f"{dataset.get('accepted_docs', 0):,}"
            if dataset
            else "pending"
        ),
        "rocm_smoke": batch_line,
        "effective_batch": "4 × 512 × accum 8 = 16,384 tokens/step",
        "stage_log": active_log.relative_to(BASE_DIR).as_posix(),
        "stage_step": latest_stage.get("step", 0),
        "stage_total_steps": active_total_steps,
        "stage_loss": f"{latest_stage.get('loss'):.4f}" if latest_stage.get("loss") is not None else "—",
        "stage_tokens": f"{latest_stage.get('tokens_m', 0):.2f}M" if latest_stage else "—",
        "stage_val_loss": (
            f"{latest_stage_eval.get('val_loss'):.4f}" if latest_stage_eval.get("val_loss") is not None else "—"
        ),
        "stage_started_at": stage_started_at or "—",
        "stage_error": (
            f"{emergency_reason} @ step {emergency_step}, micro {emergency_micro_step}"
            if emergency_active
            else "—"
        ),
        "readiness": (
            "blocked; inspect emergency_stop.json before any restart"
            if emergency_active
            else "v2.4.2 controlled run active to 15k; evaluate 10k versus 15k before any continuation"
            if run_v242_15k_active and stage_step < GLYPH100_V242_15K_STEPS
            else "v2.4.2 15k checkpoint complete; matched checkpoint evaluation required before any continuation"
            if run_v242_15k_active
            else "v2.4.1 controlled run active to 10k total; evaluate 7.5k and 10k before any further stage"
            if run_v241_10k_active and stage_step < GLYPH100_V241_10K_STEPS
            else "v2.4.1 10k eval complete; prepare v2.4.2 before any further training"
            if run_v241_10k_active and eval_v241_10k_complete
            else "v2.4.1 10k complete; checkpoint evaluation required before any further stage"
            if run_v241_10k_active
            else "pretraining stopped; 44k is best practical checkpoint; next step: SFT smoke test or dataset v2.4"
            if run50k_active and stage_step >= GLYPH100_V231_50K_STEPS and eval50k_complete
            else "v2.3.1 50k diagnostic complete; final decision pending"
            if run50k_active and stage_step >= GLYPH100_V231_50K_STEPS
            else "v2.3.1 50k diagnostic running; do not start further stages"
            if run50k_active
            else "v2.3.1 45k run complete; eval complete; no further stage without separate approval"
            if run45k_active and stage_step >= GLYPH100_V231_45K_STEPS and eval45k_complete
            else "v2.3.1 45k run complete; eval pending; no further stage without separate approval"
            if run45k_active and stage_step >= GLYPH100_V231_45K_STEPS
            else "v2.3.1 45k run running to 45k total; no stage 3 / 50k"
            if run45k_active
            else "v2.3.1 35k run complete; eval complete; no further stage without separate approval"
            if run35k_active and stage_step >= GLYPH100_V231_35K_STEPS and eval35k_complete
            else "v2.3.1 35k run complete; eval pending; no further stage without separate approval"
            if run35k_active and stage_step >= GLYPH100_V231_35K_STEPS
            else "v2.3.1 35k run running to 35k total; no stage 3 / 50k"
            if run35k_active
            else "v2.3.1 25k run complete; eval complete; no further stage without separate approval"
            if run25k_active and stage_step >= GLYPH100_V231_25K_STEPS and eval25k_complete
            else "v2.3.1 25k run complete; eval pending; no further stage without separate approval"
            if run25k_active and stage_step >= GLYPH100_V231_25K_STEPS
            else "v2.3.1 25k run running to 25k total; no stage 3 / 50k"
            if run25k_active
            else "v2.3.1 preflight complete; stage 3 still requires separate approval"
            if preflight_active and stage_step >= GLYPH100_PREFLIGHT_STEPS
            else "v2.3.1 preflight running to 15k total; no stage 3"
            if preflight_active
            else "stage 2 complete; dataset v2.2 built, but more clean non-Wikipedia data is needed before stage 3"
            if stage_step >= GLYPH100_ACTIVE_STAGE_STEPS and dataset_v2_2
            else "stage 2 complete; dataset v2.1 cleanup/audit pending before stage 3"
            if stage_step >= GLYPH100_ACTIVE_STAGE_STEPS
            else "stage 2 approved/running to 10k total"
            if stage_step >= GLYPH100_STAGE1_STEPS and dataset.get("train_tokens") and max_ok_batch
            else "prepared, waiting for explicit approval"
            if dataset.get("train_tokens") and max_ok_batch
            else "pending"
        ),
    }


def active_training_context():
    """Return the log/checkpoint context for the model currently shown as active."""
    glyph100_log_file = (
        GLYPH100_V242_15K_LOG_FILE
        if GLYPH100_V242_15K_LOG_FILE.exists()
        else GLYPH100_V241_10K_LOG_FILE
        if GLYPH100_V241_10K_LOG_FILE.exists()
        else GLYPH100_V231_50K_LOG_FILE
        if GLYPH100_V231_50K_LOG_FILE.exists()
        else GLYPH100_V231_45K_LOG_FILE
        if GLYPH100_V231_45K_LOG_FILE.exists()
        else GLYPH100_V231_35K_LOG_FILE
        if GLYPH100_V231_35K_LOG_FILE.exists()
        else GLYPH100_V231_25K_LOG_FILE
        if GLYPH100_V231_25K_LOG_FILE.exists()
        else GLYPH100_PREFLIGHT_LOG_FILE
        if GLYPH100_PREFLIGHT_LOG_FILE.exists()
        else GLYPH100_LOG_FILE
    )
    glyph100_v242_15k = glyph100_log_file == GLYPH100_V242_15K_LOG_FILE
    glyph100_v241_10k = glyph100_log_file == GLYPH100_V241_10K_LOG_FILE
    glyph100_50k = glyph100_log_file == GLYPH100_V231_50K_LOG_FILE
    glyph100_45k = glyph100_log_file == GLYPH100_V231_45K_LOG_FILE
    glyph100_35k = glyph100_log_file == GLYPH100_V231_35K_LOG_FILE
    glyph100_25k = glyph100_log_file == GLYPH100_V231_25K_LOG_FILE
    glyph100_preflight = glyph100_log_file == GLYPH100_PREFLIGHT_LOG_FILE
    if glyph100_log_file.exists():
        steps, evals, started_at = parse_log(glyph100_log_file)
        emergency_file = (
            GLYPH100_V242_15K_EMERGENCY_FILE
            if glyph100_v242_15k
            else GLYPH100_V241_10K_EMERGENCY_FILE
            if glyph100_v241_10k
            else GLYPH100_V231_50K_EMERGENCY_FILE
            if glyph100_50k
            else GLYPH100_V231_45K_EMERGENCY_FILE
            if glyph100_45k
            else GLYPH100_V231_35K_EMERGENCY_FILE
            if glyph100_35k
            else GLYPH100_V231_25K_EMERGENCY_FILE
            if glyph100_25k
            else GLYPH100_PREFLIGHT_EMERGENCY_FILE
            if glyph100_preflight
            else GLYPH100_EMERGENCY_FILE
        )
        emergency = load_json_file(emergency_file)
        latest_step = steps[-1]["step"] if steps else 0
        emergency_step = emergency.get("step")
        failed = bool(emergency.get("reason") and (not steps or emergency_step is None or emergency_step > latest_step))
        return {
            "active_variant": "glyph-100m",
            "project_name": PROJECT_NAME,
            "model_name": "Glyph-100M",
            "variant": "Base",
            "model_description": (
                "v2.4.2 15k checkpoint run stopped on non-finite loss"
                if failed and glyph100_v242_15k
                else "v2.4.1 10k run stopped on non-finite loss"
                if failed and glyph100_v241_10k
                else "v2.3.1 50k diagnostic stopped on non-finite loss"
                if failed and glyph100_50k
                else "v2.3.1 45k run stopped on non-finite loss"
                if failed and glyph100_45k
                else "v2.3.1 35k run stopped on non-finite loss"
                if failed and glyph100_35k
                else "v2.3.1 25k run stopped on non-finite loss"
                if failed and glyph100_25k
                else "v2.3.1 preflight stopped on non-finite loss"
                if failed and glyph100_preflight
                else "Stage 2 stopped on non-finite loss · latest checkpoint remains step 1000"
                if failed
                else "v2.4.2 controlled continuation 10k→15k · corrective source mix · ROCm RX 5500 XT"
                if glyph100_v242_15k
                else "v2.4.1 10k complete · eval complete · v2.4.2 source correction next"
                if glyph100_v241_10k and GLYPH100_V241_10K_EVAL_REPORT_FILE.exists()
                else "v2.4.1 controlled continuation 5k→10k · ROCm RX 5500 XT · batch 4 · accum 8"
                if glyph100_v241_10k
                else "v2.3.1 diagnostic 45k→50k complete · 44k remains best practical checkpoint"
                if glyph100_50k
                else "v2.3.1 continuation 35k→45k · ROCm RX 5500 XT · batch 4 · accum 8"
                if glyph100_45k
                else "v2.3.1 continuation 25k→35k · ROCm RX 5500 XT · batch 4 · accum 8"
                if glyph100_35k
                else "v2.3.1 continuation 15k→25k · ROCm RX 5500 XT · batch 4 · accum 8"
                if glyph100_25k
                else "v2.3.1 preflight 10k→15k · ROCm RX 5500 XT · batch 4 · accum 8"
                if glyph100_preflight
                else "Stage 2 early training · ROCm RX 5500 XT · batch 4 · accum 8"
            ),
            "phase": (
                "v2.4.2 15k run stopped"
                if failed and glyph100_v242_15k
                else "v2.4.1 10k stopped"
                if failed and glyph100_v241_10k
                else "v2.3.1 50k stopped"
                if failed and glyph100_50k
                else "v2.3.1 45k stopped"
                if failed and glyph100_45k
                else "v2.3.1 35k stopped"
                if failed and glyph100_35k
                else "v2.3.1 25k stopped"
                if failed and glyph100_25k
                else "v2.3.1 preflight stopped"
                if failed and glyph100_preflight
                else "stage 2 stopped"
                if failed
                else "v2.4.2 10k→15k"
                if glyph100_v242_15k
                else "v2.4.1 10k eval complete"
                if glyph100_v241_10k and GLYPH100_V241_10K_EVAL_REPORT_FILE.exists()
                else "v2.4.1 10k"
                if glyph100_v241_10k
                else "v2.3.1 50k"
                if glyph100_50k
                else "v2.3.1 45k"
                if glyph100_45k
                else "v2.3.1 35k"
                if glyph100_35k
                else "v2.3.1 25k"
                if glyph100_25k
                else "v2.3.1 preflight"
                if glyph100_preflight
                else "stage 2 early training"
            ),
            "steps": steps,
            "evals": evals,
            "started_at": started_at,
            "total_steps": (
                GLYPH100_V242_15K_STEPS
                if glyph100_v242_15k
                else GLYPH100_V241_10K_STEPS
                if glyph100_v241_10k
                else GLYPH100_V231_50K_STEPS
                if glyph100_50k
                else GLYPH100_V231_45K_STEPS
                if glyph100_45k
                else GLYPH100_V231_35K_STEPS
                if glyph100_35k
                else GLYPH100_V231_25K_STEPS
                if glyph100_25k
                else GLYPH100_PREFLIGHT_STEPS
                if glyph100_preflight
                else GLYPH100_ACTIVE_STAGE_STEPS
            ),
            "default_tokens_per_step": GLYPH100_TOKENS_PER_STEP,
            "checkpoint_dir": (
                CHECKPOINT_DIR / "glyph-100m-v2_4_2-15k"
                if glyph100_v242_15k
                else CHECKPOINT_DIR / "glyph-100m-v2_4_1-10k"
                if glyph100_v241_10k
                else CHECKPOINT_DIR / "glyph-100m-v2_3_1-50k"
                if glyph100_50k
                else CHECKPOINT_DIR / "glyph-100m-v2_3_1-45k"
                if glyph100_45k
                else CHECKPOINT_DIR / "glyph-100m-v2_3_1-35k"
                if glyph100_35k
                else CHECKPOINT_DIR / "glyph-100m-v2_3_1-25k"
                if glyph100_25k
                else CHECKPOINT_DIR / "glyph-100m-v2_3_1-preflight"
                if glyph100_preflight
                else CHECKPOINT_DIR / "glyph-100m"
            ),
            "log_file": glyph100_log_file,
        }

    steps, evals, started_at = parse_log(LEGACY_27M_LOG_FILE)
    return {
        "active_variant": "glyph-27m",
        "project_name": PROJECT_NAME,
        "model_name": "Glyph-27M",
        "variant": MODEL_VARIANT,
        "model_description": (
            "Glyph-27M is a small Polish decoder-only Transformer trained from scratch on a homelab."
        ),
        "phase": "completed pretraining milestone",
        "steps": steps,
        "evals": evals,
        "started_at": started_at,
        "total_steps": MAX_STEPS,
        "default_tokens_per_step": DEFAULT_TOKENS_PER_STEP,
        "checkpoint_dir": CHECKPOINT_DIR,
        "log_file": LEGACY_27M_LOG_FILE,
    }


def load_resource_state():
    try:
        with open(RESOURCE_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_watchdog_state():
    try:
        with open(WATCHDOG_STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_json_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def load_jsonl_file(path, limit=0):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                if limit and len(rows) >= limit:
                    break
    except FileNotFoundError:
        pass
    return rows


def short_timestamp(value):
    if not value:
        return "—"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        try:
            dt = dt.astimezone(ZoneInfo(SCHEDULE_TZ))
        except Exception:
            pass
        return dt.strftime("%Y-%m-%d %H:%M %Z")
    except ValueError:
        return str(value)


def public_artifact_label(value):
    if not value:
        return ""
    path = Path(str(value))
    try:
        return path.resolve().relative_to(BASE_DIR).as_posix()
    except (OSError, ValueError):
        return path.name


def fmt_number(value, digits=4):
    if value is None:
        return "brak"
    if isinstance(value, float):
        if abs(value) < 0.001 and value:
            return f"{value:.2e}"
        return f"{value:.{digits}f}"
    return str(value)


def gemma_diagnostic_description(summary, samples):
    if not summary:
        return "Opis pojawi się po pełnym przebiegu oceny Gemmą."

    averages = summary.get("averages") or {}
    stats = summary.get("training_stats") or {}
    last_eval = stats.get("last_eval") or {}
    overall = summary.get("overall_avg")
    count = summary.get("count")
    valid_count = summary.get("valid_count")

    metric_order = ("continuation_fit", "polish", "coherence", "repetition")
    scored = [
        (key, averages.get(key))
        for key in metric_order
        if isinstance(averages.get(key), (int, float))
    ]
    weakest = sorted(scored, key=lambda item: item[1])[:2]
    strongest = sorted(scored, key=lambda item: item[1], reverse=True)[:1]

    weakest_text = ", ".join(f"{key}={value:.2f}" for key, value in weakest) or "brak danych"
    strongest_text = ", ".join(f"{key}={value:.2f}" for key, value in strongest) or "brak danych"

    invalid = [row for row in samples if not row.get("valid")]
    loop_hits = []
    for row in samples:
        response = (row.get("mini_response") or "").lower()
        if any(phrase in response for phrase in ("nie jest żadne", "nie ma w tym", "no ale")):
            loop_hits.append(row.get("prompt_id") or "?")
    loop_text = ""
    if loop_hits:
        loop_text = f" Podejrzane powtórzenia widać m.in. w: {', '.join(loop_hits[:4])}."
    invalid_text = f" Nieudane oceny Gemmy: {len(invalid)}." if invalid else ""

    return (
        "Benchmark dotyczy kontynuacji tekstu bazowego modelu, nie trybu asystenta po SFT. "
        f"Wynik: overall={fmt_number(overall, 2)}/5 na {valid_count}/{count} poprawnie ocenionych próbkach. "
        f"Trening: step={stats.get('step', 'brak')}, train_loss={fmt_number(stats.get('loss'))}, "
        f"val_loss={fmt_number(last_eval.get('val_loss'))}, lr={fmt_number(stats.get('lr'))}. "
        f"Najsłabsze średnie: {weakest_text}; najmocniejsza metryka: {strongest_text}."
        f"{loop_text}{invalid_text}"
    )


def load_gemma_eval(samples=None):
    status = load_json_file(GEMMA_STATUS_FILE)
    summary = load_json_file(GEMMA_SUMMARY_FILE)
    overall = summary.get("overall_avg")
    if overall is None:
        overall = status.get("overall_avg")
    description = gemma_diagnostic_description(summary, samples or [])
    if not summary and status.get("message"):
        description = status["message"]
    return {
        "status": status.get("status", "not-run"),
        "message": status.get("message", ""),
        "updated_at": status.get("updated_at") or summary.get("generated_at"),
        "model": summary.get("model") or status.get("model", "Gemma 4 E4B"),
        "overall_avg": overall,
        "count": summary.get("count"),
        "valid_count": summary.get("valid_count"),
        "report": public_artifact_label(summary.get("report") or status.get("report", "")),
        "description": description,
    }


def hidden_gemma_eval():
    return {
        "status": "hidden",
        "message": "",
        "updated_at": None,
        "model": "—",
        "overall_avg": None,
        "count": None,
        "valid_count": None,
        "report": "",
        "description": "Ukryte w aktywnym widoku Glyph-100M.",
    }


def write_gemma_status(status, message):
    payload = {
        "status": status,
        "updated_at": datetime.now(timezone_utc()).isoformat(),
        "model": "Gemma 4 E4B",
        "message": message,
        "report": "",
        "overall_avg": None,
    }
    GEMMA_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = GEMMA_STATUS_FILE.with_suffix(GEMMA_STATUS_FILE.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(GEMMA_STATUS_FILE)


def timezone_utc():
    from datetime import timezone
    return timezone.utc


def clamp_int(value, default, low, high):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def rate_limit_check(key, limit_name):
    limit, window = RATE_LIMITS[limit_name]
    now = time.time()
    with RATE_LOCK:
        bucket = [stamp for stamp in RATE_BUCKETS.get(key, []) if now - stamp < window]
        if len(bucket) >= limit:
            retry = max(1, int(window - (now - bucket[0])))
            RATE_BUCKETS[key] = bucket
            return False, retry
        bucket.append(now)
        RATE_BUCKETS[key] = bucket
    return True, 0


def client_id_from_headers(headers):
    raw = headers.get("X-Client-Id", "")
    cleaned = re.sub(r"[^a-zA-Z0-9_.:-]", "", raw)[:80]
    return cleaned or "missing"


def gemma_manual_configured():
    return bool(GEMMA_MANUAL_CODE or GEMMA_MANUAL_CODE_SHA256)


def verify_gemma_manual_code(code):
    candidate = str(code or "").strip()
    if not candidate or len(candidate) > 128:
        return False
    if GEMMA_MANUAL_CODE:
        return hmac.compare_digest(candidate, GEMMA_MANUAL_CODE)
    if GEMMA_MANUAL_CODE_SHA256:
        digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
        return hmac.compare_digest(digest, GEMMA_MANUAL_CODE_SHA256)
    return False


def json_response(payload, code=200):
    return code, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False).encode()


# Resource schedule

def local_now():
    try:
        return datetime.now(ZoneInfo(SCHEDULE_TZ))
    except Exception:
        return datetime.now()


def active_window_for(day):
    if day.isoweekday() <= 5:
        return day_time(15, 0), day_time(22, 0)
    return day_time(8, 0), day_time(22, 0)


def is_active_time(dt):
    start, end = active_window_for(dt)
    return start <= dt.time() < end


def parse_clock(value):
    try:
        hour, minute = value.split(":", 1)
        return day_time(int(hour), int(minute))
    except (TypeError, ValueError):
        return None


def gemma_manual_window_status():
    if not GEMMA_MANUAL_REQUIRE_WINDOW:
        return True, "bez ograniczenia godzinowego"

    parts = GEMMA_MANUAL_WINDOW.split("-", 1)
    if len(parts) != 2:
        return False, f"błędna konfiguracja okna: {GEMMA_MANUAL_WINDOW}"

    start, end = parse_clock(parts[0]), parse_clock(parts[1])
    if start is None or end is None:
        return False, f"błędna konfiguracja okna: {GEMMA_MANUAL_WINDOW}"

    now_time = local_now().time()
    if start <= end:
        allowed = start <= now_time < end
    else:
        allowed = now_time >= start or now_time < end
    return allowed, f"{GEMMA_MANUAL_WINDOW} {SCHEDULE_TZ}"


def schedule_info():
    now = local_now()
    active = is_active_time(now)
    for minutes in range(1, 8 * 24 * 60 + 1):
        probe = now + timedelta(minutes=minutes)
        if is_active_time(probe) != active:
            next_switch = probe
            break
    else:
        next_switch = now

    return {
        "mode": "active" if active else "full",
        "now": now.strftime("%Y-%m-%d %H:%M %Z"),
        "next_switch": next_switch.strftime("%Y-%m-%d %H:%M %Z"),
        "window": "dni robocze 15:00-22:00, weekendy 08:00-22:00",
    }


# SVG chart

def downsample(items, limit=420):
    if len(items) <= limit:
        return items
    stride = math.ceil(len(items) / limit)
    sampled = items[::stride]
    if sampled[-1] is not items[-1]:
        sampled.append(items[-1])
    return sampled


def make_svg_chart(steps, width=920, height=280):
    if len(steps) < 2:
        return (
            f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{width}" height="{height}" fill="#151819" rx="8"/>'
            f'<text x="{width//2}" y="{height//2}" text-anchor="middle" fill="#78817f" '
            f'font-size="14">Za mało danych</text></svg>'
        )

    points_src = downsample(steps)
    losses = [s["loss"] for s in points_src]
    step_nums = [s["step"] for s in points_src]
    min_l, max_l = min(losses), max(losses)
    loss_range = max(max_l - min_l, 0.001)

    pl, pr, pt, pb = 58, 22, 20, 44
    cw = width - pl - pr
    ch = height - pt - pb

    def px(step):
        return pl + (step - step_nums[0]) / max(step_nums[-1] - step_nums[0], 1) * cw

    def py(loss):
        return pt + (1.0 - (loss - min_l) / loss_range) * ch

    line_points = " ".join(f"{px(s['step']):.1f},{py(s['loss']):.1f}" for s in points_src)
    area_points = f"{pl},{height-pb} {line_points} {width-pr},{height-pb}"

    grid = []
    for i in range(5):
        value = max_l - i * loss_range / 4
        yp = pt + i * ch / 4
        grid.append(
            f'<line x1="{pl}" y1="{yp:.1f}" x2="{width-pr}" y2="{yp:.1f}" '
            f'stroke="#252b2c" stroke-width="1"/>'
            f'<text x="{pl-8}" y="{yp+4:.1f}" text-anchor="end" fill="#7d8583" '
            f'font-size="11">{value:.2f}</text>'
        )

    x_ticks = []
    for i in range(5):
        step_value = step_nums[0] + i * (step_nums[-1] - step_nums[0]) / 4
        xp = px(step_value)
        x_ticks.append(
            f'<text x="{xp:.1f}" y="{height-13}" text-anchor="middle" fill="#7d8583" '
            f'font-size="11">{int(step_value):,}</text>'
        )

    lx, ly = px(points_src[-1]["step"]), py(points_src[-1]["loss"])
    return (
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Wykres loss">'
        f'<rect width="{width}" height="{height}" fill="#151819" rx="8"/>'
        f'{"".join(grid)}{"".join(x_ticks)}'
        f'<polygon points="{area_points}" fill="#1f6f681f"/>'
        f'<polyline points="{line_points}" fill="none" stroke="#2dd4bf" stroke-width="2.4" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="#f59e0b"/>'
        f'</svg>'
    )


# HTML

def metric(label, value, hint="", id_prefix=None):
    value_id = f' id="{id_prefix}-value"' if id_prefix else ""
    hint_id = f' id="{id_prefix}-hint"' if id_prefix else ""
    return (
        f'<section class="metric">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value"{value_id}>{value}</div>'
        f'<div class="metric-hint"{hint_id}>{html.escape(hint)}</div>'
        f'</section>'
    )


def score_chip(label, value):
    if isinstance(value, (int, float)):
        score = f"{value:.1f}"
        css_class = "score-chip"
        if value < 2.5:
            css_class += " weak"
        elif value >= 4.0:
            css_class += " strong"
        return f'<span class="{css_class}">{html.escape(label)} {score}</span>'
    return f'<span class="score-chip muted">{html.escape(label)} —</span>'


def sample_diagnostic(sample):
    scores = sample.get("scores") or {}
    scored = [
        (key, scores.get(key))
        for key in ("continuation_fit", "polish", "coherence", "repetition", "overall")
        if isinstance(scores.get(key), (int, float))
    ]
    if not scored:
        return sample.get("error") or "Brak poprawnej punktacji dla tej próbki."

    weakest = sorted(scored, key=lambda item: item[1])[:2]
    strongest = sorted(scored, key=lambda item: item[1], reverse=True)[:1]
    weakest_text = ", ".join(f"{key}={value:.1f}" for key, value in weakest)
    strongest_text = ", ".join(f"{key}={value:.1f}" for key, value in strongest)
    overall = scores.get("overall")

    flags = []
    response = (sample.get("mini_response") or "").lower()
    repeated_phrases = [phrase for phrase in ("nie jest żadne", "nie ma w tym", "no ale") if phrase in response]
    if repeated_phrases:
        flags.append("powtarza frazy: " + ", ".join(repeated_phrases[:3]))
    if isinstance(scores.get("coherence"), (int, float)) and scores["coherence"] <= 3:
        flags.append("spójność tylko częściowa")
    if isinstance(scores.get("repetition"), (int, float)) and scores["repetition"] <= 3:
        flags.append("ryzyko zapętlania")
    flag_text = "; ".join(flags) if flags else "bez oczywistej pętli w prostym skanie"

    return (
        f"overall={overall:.1f}/5. Najmocniej: {strongest_text}. "
        f"Najsłabiej: {weakest_text}. Flagi: {flag_text}."
    )


def render_sample_rows(samples):
    if not samples:
        return (
            '<section class="sample-panel">'
            f'<div class="section-title">Ostatnie próbki {MODEL_NAME}</div>'
            '<div class="sample-empty">Nie znalazłem jeszcze raportu z próbkami.</div>'
            '</section>'
        )

    labels = [
        ("overall", "all"),
        ("continuation_fit", "fit"),
        ("polish", "pl"),
        ("coherence", "coh"),
        ("repetition", "rep"),
    ]
    rows = []
    for index, sample in enumerate(samples, 1):
        scores = sample.get("scores") or {}
        score_line = "".join(score_chip(label, scores.get(key)) for key, label in labels)
        prompt_id = sample.get("prompt_id") or f"prompt-{index}"
        category = sample.get("category") or "—"
        prompt = sample.get("prompt") or ""
        response = sample.get("mini_response") or ""
        notes = sample.get("notes") or sample.get("error") or "brak komentarza"
        diagnostic = sample_diagnostic(sample)
        valid = "OK" if sample.get("valid") else "BŁĄD OCENY"
        rows.append(
            '<article class="sample-row">'
            f'<div class="sample-head">'
            f'<span>{index}. {html.escape(prompt_id)}</span>'
            f'<span>{html.escape(category)} · {html.escape(valid)}</span>'
            f'</div>'
            f'<div class="sample-scores">{score_line}</div>'
            f'<div class="sample-grid">'
            f'<div><div class="sample-label">Prompt</div><div class="sample-text">{html.escape(prompt)}</div></div>'
            f'<div><div class="sample-label">Kontynuacja {MODEL_NAME}</div><div class="sample-text response">{html.escape(response)}</div></div>'
            f'</div>'
            f'<div class="sample-label">Diagnoza</div>'
            f'<div class="sample-note">{html.escape(diagnostic)}</div>'
            f'<details class="raw-note"><summary>Surowy komentarz Gemmy</summary>'
            f'<div>{html.escape(notes)}</div></details>'
            '</article>'
        )

    return (
        '<section class="sample-panel">'
        f'<div class="section-title">Ostatnie próbki {MODEL_NAME} ({len(samples)})</div>'
        '<div class="sample-list">'
        + "".join(rows)
        + '</div></section>'
    )


def dashboard_state(context):
    steps = context["steps"]
    evals = context["evals"]
    started_at = context["started_at"]
    total_steps = context["total_steps"]
    latest = steps[-1] if steps else {}
    stats = recent_stats(steps, total_steps, context["default_tokens_per_step"])
    schedule = schedule_info()
    state = load_resource_state()
    watchdog = load_watchdog_state()
    ckpt = checkpoint_info(context["checkpoint_dir"])
    include_legacy = context["active_variant"] != "glyph-100m"
    sft = sft_state() if include_legacy else hidden_sft_state()
    glyph100 = glyph100_state()
    gemma_samples = load_jsonl_file(GEMMA_REPORT_FILE, GEMMA_DEFAULT_PROMPTS) if include_legacy else []
    gemma = load_gemma_eval(gemma_samples) if include_legacy else hidden_gemma_eval()

    cur_step = latest.get("step", 0)
    cur_loss = latest.get("loss", 0.0)
    cur_lr = latest.get("lr", 0.0)
    cur_toks = latest.get("toks", 0)
    cur_tokens_m = latest.get("tokens_m", 0.0)
    pct = cur_step / total_steps * 100 if total_steps else 0
    val_loss = f"{evals[-1]['val_loss']:.4f}" if evals else "brak"

    mode = state.get("mode") or schedule["mode"]
    mode_label = "FULL" if mode == "full" else "DOM"
    mode_class = "full" if mode == "full" else "active"
    mode_text = (
        "pełny priorytet poza godzinami aktywnego używania"
        if mode == "full"
        else "niższy priorytet w godzinach aktywnego używania"
    )

    state_note = state.get("note", "—")
    resource_line = (
        f"shares {state.get('cpu_shares', '—')} · nice {state.get('nice', '—')} · "
        f"ionice {state.get('ionice_class', '—')}:{state.get('ionice_level', '—')} · "
        f"interop {state.get('interop_threads', '—')} · OMP {state.get('omp_wait_policy', '—')}"
    )
    side_container = state.get("container", "—")
    if watchdog.get("backend") and context["active_variant"] != "glyph-100m":
        backend = watchdog.get("backend", "—")
        mode_label = "GPU" if "ROCm" in backend else "CPU"
        mode_class = "full" if "ROCm" in backend else "active"
        mode = backend
        mode_text = (
            "trening na ROCm gfx1012 · watchdog i fallback CPU aktywne"
            if "ROCm" in backend
            else "fallback CPU zarządzany przez watchdog"
        )
        state_note = watchdog.get("status", state_note)
        side_container = watchdog.get("container", side_container)
        resource_line = (
            f"{backend} · watchdog {watchdog.get('status', '—')} · "
            f"próba GPU {watchdog.get('gpu_attempts', '—')} · checkpoint co 500 kroków"
        )
    elif context["active_variant"] == "glyph-100m":
        if glyph100.get("stage_error") != "—":
            mode_label = "STOP"
            mode_class = "active"
            mode = "v2.3.1 preflight stopped" if context["phase"].startswith("v2.3.1") else "Stage 2 stopped"
            mode_text = (
                "Glyph-100M v2.3.1 preflight zatrzymany przez twardy stop NaN/Inf"
                if context["phase"].startswith("v2.3.1")
                else "Glyph-100M stage 2 zatrzymany przez twardy stop NaN/Inf"
            )
            resource_line = (
                f"{glyph100.get('stage_error')} · checkpoint preflightu nie powinien nadpisać głównego latest.pt"
                if context["phase"].startswith("v2.3.1")
                else f"{glyph100.get('stage_error')} · latest.pt pozostał na kroku 1000"
            )
            state_note = "Nie restartować bez diagnostyki resume/optimizer."
        else:
            mode_label = "GPU"
            mode_class = "full"
            mode = "ROCm / RX 5500 XT"
            mode_text = (
                "Glyph-100M v2.4.2: kontrolowany run 10k→15k na ROCm"
                if context["phase"] == "v2.4.2 10k→15k"
                else "Glyph-100M v2.3.1 pretraining zatrzymany · 44k best · 50k diagnostic"
                if context["phase"] == "v2.3.1 50k"
                else "Glyph-100M v2.3.1 run 35k→45k na ROCm"
                if context["phase"] == "v2.3.1 45k"
                else "Glyph-100M v2.3.1 run 25k→35k na ROCm"
                if context["phase"] == "v2.3.1 35k"
                else "Glyph-100M v2.3.1 run 15k→25k na ROCm"
                if context["phase"] == "v2.3.1 25k"
                else "Glyph-100M v2.3.1 preflight 10k→15k na ROCm"
                if context["phase"] == "v2.3.1 preflight"
                else "Glyph-100M stage 2 early training na ROCm"
            )
            resource_line = "ROCm / RX 5500 XT · batch 4 · accum 8 · 16,384 tokenów/krok"
    gemma_score = "—" if gemma["overall_avg"] is None else f"{gemma['overall_avg']:.2f}/5"
    gemma_count = "—"
    if gemma["valid_count"] is not None and gemma["count"] is not None:
        gemma_count = f"{gemma['valid_count']}/{gemma['count']}"
    gemma_report = gemma["report"] or "—"
    gemma_report_line = (
        f"Startuje usługę {GEMMA_SERVICE}. Raport: {gemma_report}"
        + (f" · {gemma['message']}" if gemma["message"] else "")
    )
    gemma_description = gemma["description"] or "Opis pojawi się po pełnym przebiegu oceny Gemmą."
    now = local_now().strftime("%Y-%m-%d %H:%M:%S %Z")
    samples_key = f"{gemma_report}|{gemma.get('updated_at')}|{len(gemma_samples)}" if include_legacy else ""

    return {
        "raw": {
            "project_name": PROJECT_NAME,
            "model_name": context["model_name"],
            "variant": context["variant"],
            "model_description": context["model_description"],
            "active_variant": context["active_variant"],
            "active_phase": context["phase"],
            "step": cur_step,
            "loss": cur_loss,
            "lr": cur_lr,
            "toks_per_sec": cur_toks,
            "avg_toks_per_sec": stats["avg_toks"],
            "steps_per_hour": stats["steps_per_hour"],
            "tokens_m": cur_tokens_m,
            "progress_pct": pct,
            "total_steps": total_steps,
            "eta": stats["eta"],
            "last_eval": evals[-1] if evals else None,
            "gemma_eval": gemma if include_legacy else None,
            "gemma_samples": gemma_samples if include_legacy else [],
            "sft": sft if include_legacy else None,
            "glyph100": glyph100,
            "started_at": started_at,
            "schedule": schedule,
            "resource_state": state,
            "watchdog_state": watchdog,
            "checkpoint": ckpt,
        },
        "formatted": {
            "project_name": PROJECT_NAME,
            "model_name": context["model_name"],
            "variant": context["variant"],
            "active_phase": context["phase"],
            "mode_label": mode_label,
            "mode_class": mode_class,
            "mode_text": mode_text,
            "schedule_now": schedule["now"],
            "progress_step": f"Krok {cur_step:,} / {total_steps:,}",
            "progress_eta": f"{pct:.3f}% · ETA {stats['eta']}",
            "progress_width": f"{pct:.4f}%",
            "loss_value": f"{cur_loss:.4f}" if cur_loss else "—",
            "loss_hint": f"val: {val_loss}",
            "toks_value": f"{cur_toks:,}",
            "toks_hint": f"średnio 30 wpisów: {stats['avg_toks']:,.0f}",
            "steps_value": f"{stats['steps_per_hour']:,.0f}",
            "steps_hint": f"~{stats['tokens_per_step']:,.0f} tokenów/krok",
            "tokens_value": f"{cur_tokens_m:.1f}M",
            "tokens_hint": "łącznie przetworzone",
            "lr_value": f"{cur_lr:.2e}" if cur_lr else "—",
            "lr_hint": "cosine decay",
            "checkpoint_value": ckpt["label"],
            "checkpoint_hint": f"{ckpt['size']} · {ckpt['mtime']}",
            "resources_value": mode_label,
            "resources_hint": resource_line,
            "log_value": stats["last_age"],
            "log_hint": "wiek ostatniego wpisu",
            "gemma_status": gemma["status"],
            "gemma_model": gemma["model"],
            "gemma_score": gemma_score,
            "gemma_count": gemma_count,
            "gemma_updated": short_timestamp(gemma["updated_at"]),
            "gemma_description": gemma_description,
            "gemma_report_line": gemma_report_line,
            "sft_phase": sft["phase"],
            "sft_dataset": sft["dataset"],
            "sft_split": sft["split"],
            "sft_tokens": sft["tokens"],
            "sft_step": str(sft["step"]),
            "sft_epoch": str(sft["epoch"]),
            "sft_loss": sft["loss"],
            "sft_val_loss": sft["val_loss"],
            "sft_lr": sft["lr"],
            "sft_toks": sft["toks"],
            "sft_device": sft["device"],
            "sft_base_checkpoint": sft["base_checkpoint"],
            "sft_checkpoint": sft["checkpoint"]["label"],
            "sft_checkpoint_hint": f"{sft['checkpoint']['size']} · {sft['checkpoint']['mtime']}",
            "sft_updated": sft["updated"],
            "sft_eval_status": sft["eval"]["status"],
            "sft_eval_report": sft["eval"]["report"],
            "sft_eval_prompt_count": sft["eval"]["prompt_count"],
            "sft_eval_winners": sft["eval"]["winner_line"],
            "sft_eval_quality": sft["eval"]["quality_line"],
            "sft_eval_v2_status": sft["eval"]["v2_status"],
            "sft_eval_v2_winners": sft["eval"]["v2_winner_line"],
            "sft_eval_v2_delta": sft["eval"]["v2_delta"],
            "sft_eval_sweep_status": sft["eval"]["sweep_status"],
            "sft_eval_sweep_line": sft["eval"]["sweep_line"],
            "sft_eval_verdict": sft["eval"]["verdict"],
            "glyph100_status": glyph100["status"],
            "glyph100_params": glyph100["params"],
            "glyph100_config": glyph100["config"],
            "glyph100_dataset": glyph100["dataset"],
            "glyph100_dataset_note": glyph100["dataset_note"],
            "glyph100_dataset_tokens": glyph100["dataset_tokens"],
            "glyph100_accepted_docs": glyph100["accepted_docs"],
            "glyph100_rocm_smoke": glyph100["rocm_smoke"],
            "glyph100_effective_batch": glyph100["effective_batch"],
            "glyph100_stage_step": str(glyph100["stage_step"]),
            "glyph100_stage_total_steps": str(glyph100.get("stage_total_steps", total_steps)),
            "glyph100_stage_loss": glyph100["stage_loss"],
            "glyph100_stage_tokens": glyph100["stage_tokens"],
            "glyph100_stage_val_loss": glyph100["stage_val_loss"],
            "glyph100_stage_error": glyph100["stage_error"],
            "glyph100_readiness": glyph100["readiness"],
            "side_mode": mode,
            "side_next_switch": state.get("next_switch") or schedule["next_switch"],
            "side_window": schedule["window"],
            "side_container": side_container,
            "side_priority": resource_line,
            "side_note": state_note,
            "side_started_at": started_at or "—",
            "footer": f"Odświeżanie danych co 20 s · {now}",
        },
        "html": {
            "chart": make_svg_chart(steps),
            "samples": render_sample_rows(gemma_samples) if include_legacy else "",
            "samples_key": samples_key,
        },
    }


def dashboard_script():
    return r"""<script>
(function(){
  const pollMs = 20000;
  const clientKey = "polish_gpt_dashboard_client_id";
  let inFlight = false;
  let lastSamplesKey = document.getElementById("samples-region")?.dataset.samplesKey || "";

  function clientId() {
    try {
      let value = localStorage.getItem(clientKey);
      if (!value) {
        value = (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + "-" + Math.random().toString(16).slice(2));
        localStorage.setItem(clientKey, value);
      }
      return value;
    } catch (_) {
      return "no-local-storage";
    }
  }

  function byId(id) {
    return document.getElementById(id);
  }

  function text(id, value) {
    const node = byId(id);
    if (node) node.textContent = value ?? "—";
  }

  function html(id, value) {
    const node = byId(id);
    if (node && typeof value === "string") node.innerHTML = value;
  }

  function applyStats(data) {
    const f = data.formatted || {};
    const fragments = data.html || {};

    const badge = byId("mode-badge");
    if (badge) {
      badge.textContent = f.mode_label || "—";
      badge.className = "badge " + (f.mode_class || "");
    }

    text("schedule-now", f.schedule_now);
    text("mode-text", f.mode_text);
    text("progress-step", f.progress_step);
    text("progress-eta", f.progress_eta);

    const fill = byId("progress-fill");
    if (fill && f.progress_width) fill.style.width = f.progress_width;

    text("glyph100-status", f.glyph100_status);
    text("glyph100-params", f.glyph100_params);
    text("glyph100-config", f.glyph100_config);
    text("glyph100-dataset", f.glyph100_dataset);
    text("glyph100-dataset-note", f.glyph100_dataset_note);
    text("glyph100-dataset-tokens", f.glyph100_dataset_tokens);
    text("glyph100-accepted-docs", f.glyph100_accepted_docs);
    text("glyph100-rocm-smoke", f.glyph100_rocm_smoke);
    text("glyph100-effective-batch", f.glyph100_effective_batch);
    text("glyph100-stage-step", f.glyph100_stage_step);
    text("glyph100-stage-loss", f.glyph100_stage_loss);
    text("glyph100-stage-tokens", f.glyph100_stage_tokens);
    text("glyph100-stage-val-loss", f.glyph100_stage_val_loss);
    text("glyph100-stage-error", f.glyph100_stage_error);
    text("glyph100-readiness", f.glyph100_readiness);

    text("metric-loss-value", f.loss_value);
    text("metric-loss-hint", f.loss_hint);
    text("metric-toks-value", f.toks_value);
    text("metric-toks-hint", f.toks_hint);
    text("metric-steps-value", f.steps_value);
    text("metric-steps-hint", f.steps_hint);
    text("metric-tokens-value", f.tokens_value);
    text("metric-tokens-hint", f.tokens_hint);
    text("metric-lr-value", f.lr_value);
    text("metric-lr-hint", f.lr_hint);
    text("metric-checkpoint-value", f.checkpoint_value);
    text("metric-checkpoint-hint", f.checkpoint_hint);
    text("metric-resources-value", f.resources_value);
    text("metric-resources-hint", f.resources_hint);
    text("metric-log-value", f.log_value);
    text("metric-log-hint", f.log_hint);

    text("side-mode", f.side_mode);
    text("side-next-switch", f.side_next_switch);
    text("side-window", f.side_window);
    text("side-container", f.side_container);
    text("side-priority", f.side_priority);
    text("side-note", f.side_note);
    text("side-started-at", f.side_started_at);
    text("footer-status", f.footer);

    html("loss-chart", fragments.chart);
    const samples = byId("samples-region");
    if (samples && fragments.samples && fragments.samples_key !== lastSamplesKey) {
      samples.innerHTML = fragments.samples;
      samples.dataset.samplesKey = fragments.samples_key || "";
      lastSamplesKey = fragments.samples_key || "";
    }
  }

  async function refreshStats() {
    if (inFlight) return;
    inFlight = true;
    try {
      const response = await fetch("/api/stats", {cache: "no-store"});
      if (!response.ok) throw new Error("HTTP " + response.status);
      applyStats(await response.json());
    } catch (err) {
      text("footer-status", "Nie udało się odświeżyć danych · " + new Date().toLocaleTimeString("pl-PL"));
    } finally {
      inFlight = false;
    }
  }

  setInterval(refreshStats, pollMs);
  document.addEventListener("visibilitychange", function() {
    if (!document.hidden) refreshStats();
  });
})();
</script>"""


def make_html(context):
    steps = context["steps"]
    evals = context["evals"]
    started_at = context["started_at"]
    total_steps = context["total_steps"]
    latest = steps[-1] if steps else {}
    stats = recent_stats(steps, total_steps, context["default_tokens_per_step"])
    schedule = schedule_info()
    state = load_resource_state()
    watchdog = load_watchdog_state()
    ckpt = checkpoint_info(context["checkpoint_dir"])
    include_legacy = context["active_variant"] != "glyph-100m"
    sft = sft_state() if include_legacy else hidden_sft_state()
    glyph100 = glyph100_state()
    gemma_samples = load_jsonl_file(GEMMA_REPORT_FILE, GEMMA_DEFAULT_PROMPTS) if include_legacy else []
    gemma = load_gemma_eval(gemma_samples) if include_legacy else hidden_gemma_eval()

    cur_step = latest.get("step", 0)
    cur_loss = latest.get("loss", 0.0)
    cur_lr = latest.get("lr", 0.0)
    cur_toks = latest.get("toks", 0)
    cur_tokens_m = latest.get("tokens_m", 0.0)
    pct = cur_step / total_steps * 100 if total_steps else 0
    lr_fmt = f"{cur_lr:.2e}" if cur_lr else "—"
    val_loss = f"{evals[-1]['val_loss']:.4f}" if evals else "brak"
    svg = make_svg_chart(steps)

    mode = state.get("mode") or schedule["mode"]
    mode_label = "FULL" if mode == "full" else "DOM"
    mode_class = "full" if mode == "full" else "active"
    mode_text = (
        "pełny priorytet poza godzinami aktywnego używania"
        if mode == "full"
        else "niższy priorytet w godzinach aktywnego używania"
    )

    now = local_now().strftime("%Y-%m-%d %H:%M:%S %Z")
    state_note = state.get("note", "—")
    resource_line = (
        f"shares {state.get('cpu_shares', '—')} · nice {state.get('nice', '—')} · "
        f"ionice {state.get('ionice_class', '—')}:{state.get('ionice_level', '—')} · "
        f"interop {state.get('interop_threads', '—')} · OMP {state.get('omp_wait_policy', '—')}"
    )
    side_container = state.get("container", "—")
    if watchdog.get("backend") and context["active_variant"] != "glyph-100m":
        backend = watchdog.get("backend", "—")
        mode_label = "GPU" if "ROCm" in backend else "CPU"
        mode_class = "full" if "ROCm" in backend else "active"
        mode = backend
        mode_text = (
            "trening na ROCm gfx1012 · watchdog i fallback CPU aktywne"
            if "ROCm" in backend
            else "fallback CPU zarządzany przez watchdog"
        )
        state_note = watchdog.get("status", state_note)
        side_container = watchdog.get("container", side_container)
        resource_line = (
            f"{backend} · watchdog {watchdog.get('status', '—')} · "
            f"próba GPU {watchdog.get('gpu_attempts', '—')} · checkpoint co 500 kroków"
        )
    elif context["active_variant"] == "glyph-100m":
        mode_label = "GPU"
        mode_class = "full"
        mode = "ROCm / RX 5500 XT"
        mode_text = (
            "Glyph-100M v2.4.2: kontrolowany run 10k→15k na ROCm"
            if context["phase"] == "v2.4.2 10k→15k"
            else "Glyph-100M v2.3.1 run 45k→50k zatrzymany"
            if context["phase"] == "v2.3.1 50k stopped"
            else "Glyph-100M v2.3.1 pretraining zatrzymany · 44k best · 50k diagnostic"
            if context["phase"] == "v2.3.1 50k"
            else "Glyph-100M v2.3.1 run 35k→45k zatrzymany"
            if context["phase"] == "v2.3.1 45k stopped"
            else "Glyph-100M v2.3.1 run 35k→45k na ROCm"
            if context["phase"] == "v2.3.1 45k"
            else "Glyph-100M v2.3.1 run 25k→35k zatrzymany"
            if context["phase"] == "v2.3.1 35k stopped"
            else "Glyph-100M v2.3.1 run 25k→35k na ROCm"
            if context["phase"] == "v2.3.1 35k"
            else "Glyph-100M v2.3.1 run 15k→25k na ROCm"
            if context["phase"] == "v2.3.1 25k"
            else "Glyph-100M v2.3.1 preflight 10k→15k na ROCm"
            if context["phase"] == "v2.3.1 preflight"
            else "Glyph-100M stage 2 early training na ROCm"
        )
        resource_line = "ROCm / RX 5500 XT · batch 4 · accum 8 · 16,384 tokenów/krok"
    gemma_score = "—" if gemma["overall_avg"] is None else f"{gemma['overall_avg']:.2f}/5"
    gemma_count = "—"
    if gemma["valid_count"] is not None and gemma["count"] is not None:
        gemma_count = f"{gemma['valid_count']}/{gemma['count']}"
    gemma_report = gemma["report"] or "—"
    gemma_description = gemma["description"] or "Opis pojawi się po pełnym przebiegu oceny Gemmą."
    sample_rows = render_sample_rows(gemma_samples) if include_legacy else ""
    samples_key = f"{gemma_report}|{gemma.get('updated_at')}|{len(gemma_samples)}" if include_legacy else ""
    gemma_manual_enabled = gemma_manual_configured()
    _, gemma_window_label = gemma_manual_window_status()
    gemma_manual_policy = (
        f"kod właściciela · okno {gemma_window_label} · limit 3/dzień/IP i 4/dzień globalnie"
        if gemma_manual_enabled
        else "wyłączone: brak skonfigurowanego kodu właściciela"
    )
    gemma_button_disabled = "" if gemma_manual_enabled else " disabled"
    gemma_button_text = (
        f"Odpal pełny test Gemma 4 E4B ({GEMMA_DEFAULT_PROMPTS} promptów)"
        if gemma_manual_enabled
        else "Ręczny test Gemmy wyłączony"
    )
    glyph100_description = (
        "Aktywny widok pokazuje zakończony eksperyment diagnostyczny Glyph-100M v2.3.1 45k→50k. "
        "50k jest technicznie zdrowe, ale nie przebiło 44k; pretraining v2.3.1 jest zatrzymany."
        if context["phase"] == "v2.3.1 50k"
        else
        "Aktywny widok pokazuje ręcznie zatrzymany run Glyph-100M v2.3.1 45k→50k. "
        "Trening nie działa; 44k pozostaje best practical checkpoint."
        if context["phase"] == "v2.3.1 50k stopped"
        else
        "Aktywny widok pokazuje ręcznie zatrzymany run Glyph-100M v2.3.1 35k→45k. "
        "Trening nie działa; kolejny start wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 45k stopped"
        else
        "Aktywny widok pokazuje Glyph-100M po runie v2.3.1 35k→45k. "
        "Run jest zakończony; kolejny etap wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 45k" and cur_step >= total_steps
        else "Aktywny widok pokazuje Glyph-100M w trakcie runu v2.3.1 35k→45k. "
        "To kontrolowana kontynuacja datasetu, nie stage 3 / 50k."
        if context["phase"] == "v2.3.1 45k"
        else
        "Aktywny widok pokazuje ręcznie zatrzymany run Glyph-100M v2.3.1 25k→35k. "
        "Trening nie działa; kolejny start wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 35k stopped"
        else
        "Aktywny widok pokazuje Glyph-100M po runie v2.3.1 25k→35k. "
        "Run jest zakończony; kolejny etap wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 35k" and cur_step >= total_steps
        else "Aktywny widok pokazuje Glyph-100M w trakcie runu v2.3.1 25k→35k. "
        "To kontrolowana kontynuacja datasetu, nie stage 3 / 50k."
        if context["phase"] == "v2.3.1 35k"
        else
        "Aktywny widok pokazuje Glyph-100M po runie v2.3.1 15k→25k. "
        "Run jest zakończony; kolejny etap wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 25k" and cur_step >= total_steps
        else "Aktywny widok pokazuje Glyph-100M w trakcie runu v2.3.1 15k→25k. "
        "To kontrolowana kontynuacja datasetu, nie stage 3 / 50k."
        if context["phase"] == "v2.3.1 25k"
        else
        "Aktywny widok pokazuje Glyph-100M po preflight v2.3.1 10k→15k. "
        "Run jest zakończony; stage 3 / 50k nadal wymaga osobnej decyzji."
        if context["phase"] == "v2.3.1 preflight" and cur_step >= total_steps
        else "Aktywny widok pokazuje Glyph-100M w trakcie preflight v2.3.1 10k→15k. "
        "To kontrolny run datasetu, nie stage 3 / 50k."
        if context["phase"] == "v2.3.1 preflight"
        else "Aktywny widok pokazuje Glyph-100M po stage 2 / 10k. "
        "Kolejny etap wymaga osobnej decyzji datasetowej."
    )

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(context["model_name"])} Training</title>
<link rel="icon" href="/assets/glyph_mark.png" type="image/png">
<style>
:root{{
  color-scheme:dark;
  --bg:#101211;
  --panel:#181b1a;
  --panel-2:#1f2321;
  --line:#2b302e;
  --text:#eef3ef;
  --muted:#8b9591;
  --soft:#c9d5cf;
  --teal:#2dd4bf;
  --green:#84cc16;
  --amber:#f59e0b;
  --red:#fb7185;
}}
*{{box-sizing:border-box}}
body{{
  margin:0;
  min-height:100vh;
  background:var(--bg);
  color:var(--text);
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  letter-spacing:0;
}}
.page{{max-width:1180px;margin:0 auto;padding:28px 22px 34px}}
.topbar{{display:flex;align-items:flex-start;justify-content:space-between;gap:20px;margin-bottom:22px}}
.brand-lockup{{display:flex;align-items:center;gap:13px;min-width:0}}
.brand-mark{{width:54px;height:54px;flex:0 0 auto;border-radius:8px;object-fit:contain;background:#f7f8f5}}
h1{{font-size:1.55rem;line-height:1.15;margin:0 0 7px;font-weight:720}}
.subtitle{{color:var(--muted);font-size:.9rem}}
.mode-pill{{
  min-width:190px;
  border:1px solid var(--line);
  border-radius:8px;
  padding:11px 13px;
  background:var(--panel);
}}
.mode-head{{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:6px}}
.badge{{font-size:.76rem;font-weight:780;letter-spacing:.08em;border-radius:999px;padding:4px 8px}}
.badge.full{{background:#12342f;color:#7ff5df;border:1px solid #236b61}}
.badge.active{{background:#332a14;color:#ffd27a;border:1px solid #6e5417}}
.mode-copy{{font-size:.78rem;color:var(--muted);line-height:1.35}}
.progress-panel{{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:8px;
  padding:18px;
  margin-bottom:16px;
}}
.progress-meta{{display:flex;justify-content:space-between;gap:16px;color:var(--soft);font-size:.9rem;margin-bottom:10px}}
.progress-track{{height:12px;background:#252a28;border-radius:999px;overflow:hidden}}
.progress-fill{{height:100%;width:{pct:.4f}%;background:linear-gradient(90deg,var(--green),var(--teal));border-radius:999px}}
.metrics{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px}}
.metric{{
  min-height:106px;
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:8px;
  padding:14px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}}
.metric-label{{font-size:.72rem;text-transform:uppercase;color:var(--muted);font-weight:700}}
.metric-value{{font-variant-numeric:tabular-nums;font-size:1.55rem;font-weight:760;line-height:1.1;overflow-wrap:anywhere}}
.metric-hint{{font-size:.78rem;color:var(--muted);min-height:1em}}
.wide{{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(280px,.9fr);gap:16px;align-items:start}}
.chart,.side{{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:8px;
  padding:16px;
}}
.teacher-panel{{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:8px;
  padding:16px;
  margin-bottom:16px;
}}
.teacher-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px}}
.teacher-item{{min-width:0}}
.teacher-key{{font-size:.72rem;text-transform:uppercase;color:var(--muted);font-weight:760;margin-bottom:5px}}
.teacher-value{{color:var(--soft);font-size:.9rem;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}}
.teacher-description{{margin-top:12px;color:var(--soft);font-size:.88rem;line-height:1.5;max-width:980px}}
.teacher-actions{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:12px}}
.teacher-button{{
  appearance:none;
  border:1px solid #236b61;
  background:#12342f;
  color:#7ff5df;
  border-radius:8px;
  padding:8px 12px;
  font:inherit;
  font-size:.82rem;
  font-weight:760;
  cursor:pointer;
}}
.teacher-button:hover{{border-color:#2dd4bf}}
.teacher-input{{
  width:92px;
  border:1px solid var(--line);
  border-radius:8px;
  background:#121514;
  color:var(--text);
  padding:8px 9px;
  font:inherit;
  font-size:.82rem;
}}
.teacher-button:disabled{{opacity:.55;cursor:not-allowed}}
.sample-panel{{
  background:var(--panel);
  border:1px solid var(--line);
  border-radius:8px;
  padding:16px;
  margin-bottom:16px;
}}
.sample-list{{max-height:560px;overflow:auto;border-top:1px solid var(--line)}}
.sample-row{{border-bottom:1px solid var(--line);padding:14px 0}}
.sample-row:last-child{{border-bottom:0}}
.sample-head{{display:flex;justify-content:space-between;gap:14px;color:var(--soft);font-size:.86rem;font-weight:720;margin-bottom:8px}}
.sample-scores{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}}
.score-chip{{border:1px solid #3a403d;border-radius:999px;padding:3px 7px;color:var(--soft);font-size:.72rem;font-variant-numeric:tabular-nums}}
.score-chip.strong{{border-color:#236b61;color:#7ff5df}}
.score-chip.weak{{border-color:#68404a;color:#ff9aac}}
.score-chip.muted{{color:var(--muted)}}
.sample-grid{{display:grid;grid-template-columns:minmax(0,.72fr) minmax(0,1.28fr);gap:12px;margin-bottom:10px}}
.sample-label{{font-size:.7rem;text-transform:uppercase;color:var(--muted);font-weight:760;margin-bottom:5px}}
.sample-text,.sample-note{{
  color:var(--soft);
  background:#141716;
  border:1px solid #252b29;
  border-radius:8px;
  padding:10px;
  font-size:.84rem;
  line-height:1.46;
  white-space:pre-wrap;
  overflow-wrap:anywhere;
}}
.sample-text.response{{color:var(--text)}}
.sample-note{{background:transparent;border:0;padding:0;color:#aab4af}}
.raw-note{{margin-top:8px;color:var(--muted);font-size:.8rem}}
.raw-note summary{{cursor:pointer;color:#8b9591}}
.raw-note div{{margin-top:6px;line-height:1.45;white-space:pre-wrap;overflow-wrap:anywhere}}
.sample-empty{{color:var(--muted);font-size:.86rem}}
.section-title{{font-size:.78rem;text-transform:uppercase;color:var(--muted);font-weight:760;margin-bottom:12px}}
.chart svg{{width:100%;height:auto;display:block}}
.side-row{{display:flex;justify-content:space-between;gap:16px;border-top:1px solid var(--line);padding:12px 0;font-size:.88rem}}
.side-row:first-of-type{{border-top:0;padding-top:0}}
.side-key{{color:var(--muted)}}
.side-val{{text-align:right;color:var(--soft);font-variant-numeric:tabular-nums;overflow-wrap:anywhere}}
footer{{color:#68716d;font-size:.76rem;text-align:right;margin-top:14px}}
@media (max-width:900px){{
  .topbar{{display:block}}
  .mode-pill{{margin-top:14px}}
  .metrics{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .wide{{grid-template-columns:1fr}}
  .teacher-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}
  .sample-grid{{grid-template-columns:1fr}}
}}
@media (max-width:560px){{
  .page{{padding:20px 14px 26px}}
  .brand-mark{{width:44px;height:44px}}
  .metrics{{grid-template-columns:1fr}}
  .teacher-grid{{grid-template-columns:1fr}}
  .teacher-actions{{display:block}}
  .teacher-button{{margin-bottom:10px;width:100%}}
  .teacher-input{{width:100%;margin-bottom:8px}}
  .progress-meta{{display:block}}
  .metric-value{{font-size:1.35rem}}
}}
</style>
</head>
<body>
<main class="page">
  <header class="topbar">
    <div class="brand-lockup">
      <img class="brand-mark" src="/assets/glyph_mark.png" alt="" width="54" height="54">
      <div>
        <h1>{html.escape(context["model_name"])} Training</h1>
        <div class="subtitle">{html.escape(context["phase"])} · ROCm RX 5500 XT · batch 4 · accum 8</div>
      </div>
    </div>
    <aside class="mode-pill">
      <div class="mode-head">
        <span id="mode-badge" class="badge {mode_class}">{mode_label}</span>
        <span id="schedule-now" class="mode-copy">{html.escape(schedule["now"])}</span>
      </div>
      <div id="mode-text" class="mode-copy">{html.escape(mode_text)}</div>
    </aside>
  </header>

  <section class="progress-panel">
    <div class="progress-meta">
      <span id="progress-step">Krok {cur_step:,} / {total_steps:,}</span>
      <span id="progress-eta">{pct:.3f}% · ETA {stats["eta"]}</span>
    </div>
    <div class="progress-track"><div id="progress-fill" class="progress-fill"></div></div>
  </section>

  <section class="teacher-panel">
    <div class="section-title">Glyph-100M status</div>
    <div class="teacher-grid">
      <div class="teacher-item"><div class="teacher-key">Status</div><div id="glyph100-status" class="teacher-value">{html.escape(glyph100["status"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Parametry</div><div id="glyph100-params" class="teacher-value">{html.escape(glyph100["params"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Config</div><div id="glyph100-config" class="teacher-value">{html.escape(glyph100["config"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Dataset</div><div id="glyph100-dataset" class="teacher-value">{html.escape(glyph100["dataset"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Zakres danych</div><div id="glyph100-dataset-note" class="teacher-value">{html.escape(glyph100["dataset_note"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Tokeny</div><div id="glyph100-dataset-tokens" class="teacher-value">{html.escape(glyph100["dataset_tokens"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Dokumenty</div><div id="glyph100-accepted-docs" class="teacher-value">{html.escape(glyph100["accepted_docs"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">ROCm smoke</div><div id="glyph100-rocm-smoke" class="teacher-value">{html.escape(glyph100["rocm_smoke"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Effective batch</div><div id="glyph100-effective-batch" class="teacher-value">{html.escape(glyph100["effective_batch"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Stage step</div><div id="glyph100-stage-step" class="teacher-value">{html.escape(str(glyph100["stage_step"]))}</div></div>
      <div class="teacher-item"><div class="teacher-key">Stage loss</div><div id="glyph100-stage-loss" class="teacher-value">{html.escape(glyph100["stage_loss"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Stage tokeny</div><div id="glyph100-stage-tokens" class="teacher-value">{html.escape(glyph100["stage_tokens"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Stage val</div><div id="glyph100-stage-val-loss" class="teacher-value">{html.escape(glyph100["stage_val_loss"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Stop</div><div id="glyph100-stage-error" class="teacher-value">{html.escape(glyph100["stage_error"])}</div></div>
      <div class="teacher-item"><div class="teacher-key">Gotowość</div><div id="glyph100-readiness" class="teacher-value">{html.escape(glyph100["readiness"])}</div></div>
    </div>
    <div class="teacher-description">
      {html.escape(glyph100_description)}
    </div>
  </section>

  <section class="metrics">
    {metric("Loss", f"{cur_loss:.4f}" if cur_loss else "—", f"val: {val_loss}", "metric-loss")}
    {metric("Tok/s", f"{cur_toks:,}", f"średnio 30 wpisów: {stats['avg_toks']:,.0f}", "metric-toks")}
    {metric("Kroki/h", f"{stats['steps_per_hour']:,.0f}", f"~{stats['tokens_per_step']:,.0f} tokenów/krok", "metric-steps")}
    {metric("Tokeny", f"{cur_tokens_m:.1f}M", "łącznie przetworzone", "metric-tokens")}
    {metric("Learning rate", lr_fmt, "cosine decay", "metric-lr")}
    {metric("Checkpoint", html.escape(ckpt["label"]), f"{ckpt['size']} · {ckpt['mtime']}", "metric-checkpoint")}
    {metric("Zasoby", html.escape(mode_label), resource_line, "metric-resources")}
    {metric("Log", html.escape(stats["last_age"]), "wiek ostatniego wpisu", "metric-log")}
  </section>

  <section class="wide">
    <div class="chart">
      <div class="section-title">Loss w czasie</div>
      <div id="loss-chart">{svg}</div>
    </div>
    <aside class="side">
      <div class="section-title">Stan uruchomienia</div>
      <div class="side-row"><span class="side-key">Tryb zasobów</span><span id="side-mode" class="side-val">{html.escape(mode)}</span></div>
      <div class="side-row"><span class="side-key">Następna zmiana</span><span id="side-next-switch" class="side-val">{html.escape(state.get("next_switch") or schedule["next_switch"])}</span></div>
      <div class="side-row"><span class="side-key">Okna aktywne</span><span id="side-window" class="side-val">{html.escape(schedule["window"])}</span></div>
      <div class="side-row"><span class="side-key">Kontener</span><span id="side-container" class="side-val">{html.escape(side_container)}</span></div>
      <div class="side-row"><span class="side-key">Priorytet</span><span id="side-priority" class="side-val">{html.escape(resource_line)}</span></div>
      <div class="side-row"><span class="side-key">Ostatnia akcja</span><span id="side-note" class="side-val">{html.escape(state_note)}</span></div>
      <div class="side-row"><span class="side-key">Start procesu</span><span id="side-started-at" class="side-val">{html.escape(started_at or "—")}</span></div>
    </aside>
  </section>

  <footer id="footer-status">Odświeżanie danych co 20 s · {html.escape(now)}</footer>
</main>
{dashboard_script()}
</body>
</html>"""


# HTTP handler

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def client_ip(self):
        forwarded = self.headers.get("CF-Connecting-IP") or self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()[:80]
        return self.client_address[0]

    def read_post_data(self):
        length = clamp_int(self.headers.get("Content-Length"), 0, 0, 8192)
        raw = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        ctype = self.headers.get("Content-Type", "")
        if "application/json" in ctype:
            try:
                return json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return {}
        parsed = parse_qs(raw, keep_blank_values=True)
        return {key: values[-1] if values else "" for key, values in parsed.items()}

    def respond_json(self, payload, code=200):
        _, ctype, body = json_response(payload, code)
        self._respond(code, ctype, body)

    def check_gemma_rate(self):
        ip = self.client_ip()
        device = client_id_from_headers(self.headers)
        ok, retry = rate_limit_check(f"gemma:ip:{ip}", "gemma_ip")
        if not ok:
            self.respond_json({"ok": False, "error": f"Limit IP. Spróbuj za {retry}s.", "retry_after": retry}, 429)
            return False
        ok, retry = rate_limit_check(f"gemma:device:{device}", "gemma_device")
        if not ok:
            self.respond_json({"ok": False, "error": f"Limit przeglądarki. Spróbuj za {retry}s.", "retry_after": retry}, 429)
            return False
        ok, retry = rate_limit_check("gemma:global", "gemma_global")
        if not ok:
            self.respond_json({"ok": False, "error": f"Globalny limit ręcznych testów. Spróbuj za {retry}s.", "retry_after": retry}, 429)
            return
        return True

    def require_fetch_same_origin(self):
        if self.headers.get("X-Requested-With") != "fetch":
            self.respond_json({"ok": False, "error": "Ten endpoint przyjmuje tylko żądania z dashboardu."}, 403)
            return False
        origin = self.headers.get("Origin", "")
        if origin:
            host = self.headers.get("Host", "")
            if origin not in {f"https://{host}", f"http://{host}"}:
                self.respond_json({"ok": False, "error": "Nieprawidłowe źródło żądania."}, 403)
                return False
        return True

    def gemma_service_active(self):
        proc = subprocess.run(
            ["systemctl", "--user", "is-active", "--quiet", GEMMA_SERVICE],
            cwd=str(BASE_DIR),
            timeout=3,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return proc.returncode == 0

    def do_GET(self):
        if self.path in STATIC_ASSETS:
            asset = STATIC_ASSETS[self.path]
            try:
                body = asset.read_bytes()
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                return
            self._respond(200, "image/png", body)
            return

        if self.path == "/api/stats":
            payload = dashboard_state(active_training_context())
            response = {**payload["raw"], "formatted": payload["formatted"], "html": payload["html"]}
            body = json.dumps(response, ensure_ascii=False).encode()
            self._respond(200, "application/json; charset=utf-8", body)
            return

        if self.path in ("/", "/index.html"):
            body = make_html(active_training_context()).encode()
            self._respond(200, "text/html; charset=utf-8", body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/gemma-eval/start":
            try:
                if active_training_context()["active_variant"] == "glyph-100m":
                    self.respond_json({"ok": False, "error": "Ręczny test Gemmy jest ukryty w widoku Glyph-100M."}, 410)
                    return
                if not self.require_fetch_same_origin():
                    return
                if not gemma_manual_configured():
                    self.respond_json({"ok": False, "error": "Ręczne testy Gemmy są wyłączone."}, 403)
                    return
                allowed_now, window_label = gemma_manual_window_status()
                if not allowed_now:
                    self.respond_json({"ok": False, "error": f"Ręczny test Gemmy działa tylko w oknie {window_label}."}, 403)
                    return
                if self.gemma_service_active():
                    self.respond_json({"ok": False, "error": "Test Gemmy już trwa."}, 409)
                    return
                if not self.check_gemma_rate():
                    return
                data = self.read_post_data()
                if not verify_gemma_manual_code(data.get("code", "")):
                    self.respond_json({"ok": False, "error": "Nieprawidłowy kod do ręcznego testu Gemmy."}, 403)
                    return
                write_gemma_status(
                    "queued",
                    f"manual eval: Gemma 4 E4B, {GEMMA_DEFAULT_PROMPTS} prompts, "
                    f"{GEMMA_SAMPLE_TOKENS} max tokens/sample, 2h timeout",
                )
                subprocess.run(
                    ["systemctl", "--user", "start", "--no-block", GEMMA_SERVICE],
                    cwd=str(BASE_DIR),
                    timeout=5,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if "application/json" in self.headers.get("Accept", ""):
                    payload = json.dumps({"ok": True}).encode()
                    self._respond(202, "application/json", payload)
                    return
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
            except Exception as exc:
                write_gemma_status("error", f"manual eval start failed: {type(exc).__name__}")
                payload = json.dumps({"ok": False, "error": "Nie udało się uruchomić testu Gemmy."}).encode()
                self._respond(500, "application/json", payload)
            return

        self.send_response(404)
        self.end_headers()

    def _respond(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Dashboard: http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
