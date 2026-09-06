#!/usr/bin/env python3
"""Export sanitized Glyph public-site JSON data from local training reports.

This script intentionally writes only public, non-operational project data into
site/data/*.json. It does not expose filesystem paths, ports, service names or
host topology.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent.parent
SITE_DATA = ROOT / "site" / "data"
LEGACY_27M_LOG_FILE = ROOT / "logs" / "train.log"
GLYPH100_LOG_FILE = ROOT / "logs" / "glyph-100m" / "train.log"
GLYPH100_PREFLIGHT_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-preflight" / "train.log"
GLYPH100_V231_25K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-25k" / "train.log"
GLYPH100_V231_35K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-35k" / "train.log"
GLYPH100_V231_45K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-45k" / "train.log"
GLYPH100_V231_50K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-50k" / "train.log"
GLYPH100_V241_10K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "train.log"
GLYPH100_V242_15K_LOG_FILE = ROOT / "logs" / "glyph-100m-v2_4_2-15k" / "train.log"
GLYPH100_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m" / "emergency_stop.json"
GLYPH100_PREFLIGHT_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-preflight" / "emergency_stop.json"
GLYPH100_V231_25K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-25k" / "emergency_stop.json"
GLYPH100_V231_35K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-35k" / "emergency_stop.json"
GLYPH100_V231_45K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-45k" / "emergency_stop.json"
GLYPH100_V231_50K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_3_1-50k" / "emergency_stop.json"
GLYPH100_V241_10K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_4_1-10k" / "emergency_stop.json"
GLYPH100_V242_15K_EMERGENCY_FILE = ROOT / "logs" / "glyph-100m-v2_4_2-15k" / "emergency_stop.json"
CHECKPOINT = ROOT / "checkpoints" / "final.pt"
GLYPH100_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m"
GLYPH100_PREFLIGHT_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-preflight"
GLYPH100_V231_25K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-25k"
GLYPH100_V231_35K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-35k"
GLYPH100_V231_45K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-45k"
GLYPH100_V231_50K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_3_1-50k"
GLYPH100_V241_10K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_4_1-10k"
GLYPH100_V242_15K_CHECKPOINT_DIR = ROOT / "checkpoints" / "glyph-100m-v2_4_2-15k"
SFT_LOG_FILE = ROOT / "logs" / "sft-v0.log"
SFT_CHECKPOINT = ROOT / "checkpoints" / "sft-v0" / "glyph-27m-sft-v0-final.pt"
SFT_PREPARE_REPORT = ROOT / "data" / "sft" / "reports" / "sft_v0_prepare_report.json"
SFT_EVAL_REPORT = ROOT / "eval" / "sft-v0" / "base_vs_sft_comparison.json"
SFT_EVAL_V2_REPORT = ROOT / "eval" / "sft-v0-v2" / "base_vs_sft_comparison_v2.json"
SFT_DECODING_SWEEP_REPORT = ROOT / "eval" / "sft-v0" / "decoding_sweep.json"
GLYPH100_PARAM_REPORT = ROOT / "reports" / "glyph100_parameter_report.json"
GLYPH100_SMOKE_REPORT = ROOT / "reports" / "glyph100_rocm_smoke.json"
GLYPH100_STAGE_SMOKE_REPORT = ROOT / "reports" / "glyph100_rocm_smoke_accum8.json"
GLYPH100_DATASET_STATS = ROOT / "data" / "reports" / "glyph_100m_dataset_stats.json"
GLYPH100_DATASET_V2_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_stats.json"
GLYPH100_DATASET_V2_1_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_1_stats.json"
GLYPH100_DATASET_V2_2_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_2_stats.json"
GLYPH100_DATASET_V2_3_1_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_3_1_stats.json"
GLYPH100_DATASET_V2_4_1_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_stats.json"
GLYPH100_DATASET_V2_4_2_STATS = ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_stats.json"
GLYPH100_V231_25K_EVAL_REPORT = ROOT / "reports" / "glyph100_v2_3_1_25k_eval_report.md"
GLYPH100_V231_35K_EVAL_REPORT = ROOT / "reports" / "glyph100_v2_3_1_35k_eval_report.md"
GLYPH100_V231_45K_EVAL_REPORT = ROOT / "reports" / "glyph100_v2_3_1_45k_eval_report.md"
GLYPH100_V231_50K_DECISION_REPORT = ROOT / "reports" / "glyph100_v2_3_1_final_decision.md"
GLYPH100_V241_10K_EVAL_REPORT = ROOT / "reports" / "glyph100_v2_4_1_10k_20260718_report.md"
GEMMA_SUMMARY = ROOT / "reports" / "gemma4_eval" / "latest_summary.json"
GEMMA_REPORT = ROOT / "reports" / "gemma4_eval" / "latest.jsonl"
SAMPLE_REPORT = ROOT / "reports" / "samples" / "latest.jsonl"
TOTAL_STEPS = 200_000
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
GLYPH100_ACTIVE_STAGE_STEPS = GLYPH100_STAGE2_STEPS
DEFAULT_TOKENS_PER_STEP = 32 * 256
GLYPH100_TOKENS_PER_STEP = 4 * 512 * 8
WARSAW = ZoneInfo("Europe/Warsaw")

STEP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) step=\s*(?P<step>\d+) \| "
    r"loss=(?P<loss>[\d.]+) \| lr=(?P<lr>[\de.+\-]+) \| "
    r"tok/s=(?P<toks>[\d,]+) \| tokens=(?P<tokens>[\d.]+)M"
)
EVAL_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) eval step=\s*(?P<step>\d+) \| "
    r"val_loss=(?P<val_loss>[\d.]+)"
)
SFT_STEP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) sft step=\s*(?P<step>\d+) \| "
    r"epoch=(?P<epoch>\d+) \| loss=(?P<loss>[\d.]+) \| lr=(?P<lr>[\de.+\-]+) \| "
    r"tok/s=(?P<toks>[\d,]+)"
)
SFT_EVAL_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) sft (?:eval|final_eval) step=\s*(?P<step>\d+) \| "
    r"val_loss=(?P<val_loss>[\d.]+)"
)


def atomic_write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp.replace(path)


def read_json(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return rows


def parse_log(log_file: Path = LEGACY_27M_LOG_FILE) -> tuple[list[dict], list[dict]]:
    steps: list[dict] = []
    evals: list[dict] = []
    try:
        with log_file.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
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
    except FileNotFoundError:
        pass
    return steps, evals


def parse_log_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def public_time(value: str | None) -> str:
    if not value:
        return "not found"
    dt = parse_log_time(value)
    if not dt:
        return value
    return dt.astimezone(WARSAW).strftime("%Y-%m-%d %H:%M %Z")


def public_report_time(value: str | None) -> str:
    if not value:
        return "not found"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(WARSAW).strftime("%Y-%m-%d %H:%M %Z")
    except ValueError:
        return public_time(value)


def compact_number(value: float | int | None, suffix: str = "") -> str:
    if value is None:
        return "not found"
    if isinstance(value, float) and abs(value) < 0.001 and value != 0:
        return f"{value:.2e}{suffix}"
    if isinstance(value, float):
        return f"{value:.4f}{suffix}"
    return f"{value:,}{suffix}"


def compact_tokens(tokens_m: float | None) -> str:
    if tokens_m is None:
        return "not found"
    if tokens_m >= 1000:
        return f"{tokens_m / 1000:.2f}B"
    return f"{tokens_m:.2f}M"


def compact_toks(value: float | int | None) -> str:
    if value is None:
        return "not found"
    if value >= 1000:
        return f"~{value / 1000:.2f}k tok/s"
    return f"~{value:.0f} tok/s"


def checkpoint_label() -> str:
    if CHECKPOINT.exists():
        return "glyph-27m-base-final"
    return "not found"


def glyph100_checkpoint_label(
    ckpt_dir: Path = GLYPH100_CHECKPOINT_DIR,
    label: str = "glyph-100m-stage2-latest",
    fallback: str = "not found",
) -> str:
    latest = ckpt_dir / "latest.pt"
    if latest.exists():
        return label
    return fallback


def glyph100_checkpoint_public_mtime(ckpt_dir: Path = GLYPH100_CHECKPOINT_DIR) -> str | None:
    latest = ckpt_dir / "latest.pt"
    if not latest.exists():
        return None
    return datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc).astimezone(WARSAW).strftime(
        "%Y-%m-%d %H:%M %Z"
    )


def checkpoint_public_mtime() -> str | None:
    if not CHECKPOINT.exists():
        return None
    return datetime.fromtimestamp(CHECKPOINT.stat().st_mtime, tz=timezone.utc).astimezone(WARSAW).strftime(
        "%Y-%m-%d %H:%M %Z"
    )


def parse_sft_log() -> tuple[list[dict], list[dict]]:
    steps: list[dict] = []
    evals: list[dict] = []
    try:
        with SFT_LOG_FILE.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = SFT_STEP_RE.match(line)
                if match:
                    steps.append(
                        {
                            "ts": match.group("ts"),
                            "step": int(match.group("step")),
                            "epoch": int(match.group("epoch")),
                            "loss": float(match.group("loss")),
                            "lr": float(match.group("lr")),
                            "toks": int(match.group("toks").replace(",", "")),
                        }
                    )
                    continue
                match = SFT_EVAL_RE.match(line)
                if match:
                    evals.append(
                        {
                            "ts": match.group("ts"),
                            "step": int(match.group("step")),
                            "val_loss": float(match.group("val_loss")),
                        }
                    )
    except FileNotFoundError:
        pass
    return steps, evals


def export_sft_state() -> dict | None:
    steps, evals = parse_sft_log()
    latest = steps[-1] if steps else {}
    last_eval = evals[-1] if evals else {}
    report = read_json(SFT_PREPARE_REPORT)
    if not latest and not report and not SFT_CHECKPOINT.exists():
        return None
    train_tokens = report.get("train_tokens")
    val_tokens = report.get("val_tokens")
    dataset = Path(report.get("input", "glyph_sft_v0_seed_1500_expanded")).stem
    sft = {
        "phase": "SFT v0",
        "status": "complete" if SFT_CHECKPOINT.exists() else "snapshot",
        "dataset": dataset,
        "examples": report.get("input_examples") or 1500,
        "split": f"{report.get('train_examples', '—')} / {report.get('val_examples', '—')}",
        "tokens": f"{(train_tokens or 0) + (val_tokens or 0):,}" if train_tokens or val_tokens else "not found",
        "step": latest.get("step"),
        "epoch": latest.get("epoch"),
        "trainLoss": compact_number(latest.get("loss")),
        "validationLoss": compact_number(last_eval.get("val_loss")),
        "learningRate": compact_number(latest.get("lr")),
        "throughput": compact_toks(latest.get("toks")),
        "device": "ROCm / RX 5500 XT",
        "baseCheckpoint": "glyph-27m-base-final",
        "checkpoint": "glyph-27m-sft-v0-final" if SFT_CHECKPOINT.exists() else "not found",
        "notes": "One small epoch over a synthetic curated dataset. It improves instruction format, but sample quality still needs review.",
    }
    eval_state = export_sft_eval_state()
    if eval_state:
        sft["evaluation"] = eval_state
    return sft


def export_sft_eval_state() -> dict | None:
    data = read_json(SFT_EVAL_REPORT)
    summary = data.get("summary") or {}
    if not summary:
        return None
    counts = summary.get("winner_counts") or {}
    quality = summary.get("quality_counts") or {}
    v2_data = read_json(SFT_EVAL_V2_REPORT)
    v2_summary = v2_data.get("summary") or {}
    v2_counts = v2_summary.get("winner_counts") or {}
    sweep = read_json(SFT_DECODING_SWEEP_REPORT)
    prompt_count = int(summary.get("prompt_count") or sum(counts.values()) or 0)
    state = {
        "status": "completed",
        "method": "Base vs SFT v0 qualitative heuristic eval",
        "promptCount": prompt_count,
        "winnerCounts": {
            "sft": int(counts.get("sft", 0)),
            "base": int(counts.get("base", 0)),
            "tie": int(counts.get("tie", 0)),
            "bothBad": int(counts.get("both_bad", 0)),
        },
        "qualityCounts": {
            "baseRepetition": int(quality.get("base_repetition", 0)),
            "sftRepetition": int(quality.get("sft_repetition", 0)),
            "baseWebGarbage": int(quality.get("base_web_garbage", 0)),
            "sftWebGarbage": int(quality.get("sft_web_garbage", 0)),
            "baseCutOff": int(quality.get("base_cut_off", 0)),
            "sftCutOff": int(quality.get("sft_cut_off", 0)),
        },
        "summary": (
            f"SFT {counts.get('sft', 0)} · Base {counts.get('base', 0)} · "
            f"Tie {counts.get('tie', 0)} · both bad {counts.get('both_bad', 0)}"
        ),
        "verdict": (
            "SFT v0 improves instruction format and ending behavior, but still shows drift, "
            "repetition and template-like advice."
        ),
        "v2": {
            "status": "completed" if v2_summary else "pending",
            "summary": (
                f"SFT {v2_counts.get('sft', 0)} · Base {v2_counts.get('base', 0)} · "
                f"Tie {v2_counts.get('tie', 0)} · both bad {v2_counts.get('both_bad', 0)}"
                if v2_summary
                else "pending"
            ),
            "weakSftWinsRemoved": v2_summary.get("weak_sft_wins_removed"),
        },
        "decodingSweep": {
            "status": "completed" if sweep else "pending",
            "bestOverallPreset": sweep.get("best_overall_preset"),
            "recommendedDemoPreset": sweep.get("recommended_demo_preset"),
            "promptCount": sweep.get("prompt_count"),
        },
    }


def export_glyph100_state() -> dict | None:
    param_report = read_json(GLYPH100_PARAM_REPORT)
    reports = param_report.get("reports") or []
    variant = next((item for item in reports if item.get("variant") == "glyph-100m"), {})
    smoke = read_json(GLYPH100_SMOKE_REPORT)
    stage_smoke = read_json(GLYPH100_STAGE_SMOKE_REPORT)
    dataset = read_json(GLYPH100_DATASET_STATS)
    dataset_v2 = read_json(GLYPH100_DATASET_V2_STATS)
    dataset_v2_1 = read_json(GLYPH100_DATASET_V2_1_STATS)
    dataset_v2_2 = read_json(GLYPH100_DATASET_V2_2_STATS)
    dataset_v2_3_1 = read_json(GLYPH100_DATASET_V2_3_1_STATS)
    dataset_v2_4_1 = read_json(GLYPH100_DATASET_V2_4_1_STATS)
    dataset_v2_4_2 = read_json(GLYPH100_DATASET_V2_4_2_STATS)
    eval25k_complete = GLYPH100_V231_25K_EVAL_REPORT.exists()
    eval35k_complete = GLYPH100_V231_35K_EVAL_REPORT.exists()
    eval45k_complete = GLYPH100_V231_45K_EVAL_REPORT.exists()
    eval50k_complete = GLYPH100_V231_50K_DECISION_REPORT.exists()
    eval_v241_10k_complete = GLYPH100_V241_10K_EVAL_REPORT.exists()
    next_dataset = dataset_v2_4_2 or dataset_v2_4_1 or dataset_v2_3_1 or dataset_v2_2 or dataset_v2_1 or dataset_v2
    run_v242_15k_active = GLYPH100_V242_15K_LOG_FILE.exists()
    run_v241_10k_active = GLYPH100_V241_10K_LOG_FILE.exists() and not run_v242_15k_active
    run50k_active = GLYPH100_V231_50K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active
    run45k_active = GLYPH100_V231_45K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active
    run35k_active = GLYPH100_V231_35K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active
    run25k_active = GLYPH100_V231_25K_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active and not run35k_active
    preflight_active = GLYPH100_PREFLIGHT_LOG_FILE.exists() and not run_v242_15k_active and not run_v241_10k_active and not run50k_active and not run45k_active and not run35k_active and not run25k_active
    v231_active = run50k_active or run45k_active or run35k_active or run25k_active or preflight_active
    stage_log_file = (
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
    stage_total_steps = (
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
    stage_checkpoint_dir = (
        GLYPH100_V242_15K_CHECKPOINT_DIR
        if run_v242_15k_active
        else GLYPH100_V241_10K_CHECKPOINT_DIR
        if run_v241_10k_active
        else GLYPH100_V231_50K_CHECKPOINT_DIR
        if run50k_active
        else GLYPH100_V231_45K_CHECKPOINT_DIR
        if run45k_active
        else GLYPH100_V231_35K_CHECKPOINT_DIR
        if run35k_active
        else GLYPH100_V231_25K_CHECKPOINT_DIR
        if run25k_active
        else GLYPH100_PREFLIGHT_CHECKPOINT_DIR
        if preflight_active
        else GLYPH100_CHECKPOINT_DIR
    )
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
    emergency = read_json(emergency_file)
    stage_steps, stage_evals = parse_log(stage_log_file)
    if not variant and not smoke and not dataset and not stage_steps:
        return None

    max_ok_batch = smoke.get("max_ok_batch_size")
    stage_smoke_ok = bool(stage_smoke.get("max_ok_batch_size"))
    latest_stage = stage_steps[-1] if stage_steps else {}
    latest_eval = stage_evals[-1] if stage_evals else {}
    stage_step = latest_stage.get("step", 0)
    stage_complete = stage_step >= stage_total_steps
    emergency_reason = emergency.get("reason")
    emergency_step = emergency.get("step")
    emergency_micro_step = emergency.get("micro_step")
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
        stage_status = "prepared, waiting for approval"
    elif run_v242_15k_active and stage_complete:
        stage_status = "v2.4.2 15k checkpoint complete · eval pending"
    elif run_v242_15k_active:
        stage_status = "v2.4.2 controlled 10k to 15k run"
    elif run_v241_10k_active and stage_complete:
        stage_status = (
            "v2.4.1 10k run complete · eval complete"
            if eval_v241_10k_complete
            else "v2.4.1 10k run complete · eval pending"
        )
    elif run_v241_10k_active and stage_step >= GLYPH100_V241_10K_START_STEP:
        stage_status = "v2.4.1 training to 10k"
    elif run50k_active and stage_complete:
        stage_status = "v2.3.1 pretraining stopped · 44k best · 50k diagnostic complete" if eval50k_complete else "v2.3.1 50k diagnostic complete · decision pending"
    elif run50k_active and stage_step >= GLYPH100_V231_50K_START_STEP:
        stage_status = "v2.3.1 50k diagnostic running"
    elif run45k_active and stage_complete:
        stage_status = "v2.3.1 45k run complete · eval complete" if eval45k_complete else "v2.3.1 45k run complete · eval pending"
    elif run45k_active and stage_step >= GLYPH100_V231_45K_START_STEP:
        stage_status = "v2.3.1 45k run running"
    elif run35k_active and stage_complete:
        stage_status = "v2.3.1 35k run complete · eval complete" if eval35k_complete else "v2.3.1 35k run complete · eval pending"
    elif run35k_active and stage_step >= GLYPH100_V231_35K_START_STEP:
        stage_status = "v2.3.1 35k run running"
    elif run25k_active and stage_complete:
        stage_status = "v2.3.1 25k run complete · eval complete" if eval25k_complete else "v2.3.1 25k run complete · eval pending"
    elif run25k_active and stage_step >= GLYPH100_V231_25K_START_STEP:
        stage_status = "v2.3.1 25k run running"
    elif preflight_active and stage_complete:
        stage_status = "v2.3.1 preflight complete"
    elif preflight_active and stage_step >= GLYPH100_PREFLIGHT_START_STEP:
        stage_status = "v2.3.1 preflight running"
    elif stage_complete:
        stage_status = "stage 2 complete"
    elif stage_step >= GLYPH100_STAGE1_STEPS:
        stage_status = "stage 2 training"
    else:
        stage_status = "stage 1 training"

    current_dataset = (
        dataset_v2_4_2
        if run_v242_15k_active and dataset_v2_4_2
        else dataset_v2_4_1
        if run_v241_10k_active and dataset_v2_4_1
        else dataset_v2_3_1
        if v231_active and dataset_v2_3_1
        else dataset
    )
    dataset_name = (
        "glyph100_dataset_v2_4_2_core"
        if run_v242_15k_active
        else "glyph100_dataset_v2_4_1_core"
        if run_v241_10k_active
        else "glyph100_v2_3_1"
        if v231_active
        else (current_dataset.get("dataset_name") if current_dataset else None) or "glyph100_stage1_candidate"
    )
    state = {
        "status": stage_status,
        "parameters": (
            f"{variant.get('unique_parameters', 0) / 1_000_000:.2f}M unique / "
            f"{variant.get('logical_total_parameters', 0) / 1_000_000:.2f}M logical"
            if variant
            else "pending"
        ),
        "context": str((variant.get("model_config") or {}).get("context_len", 512)),
        "dataset": dataset_name,
        "datasetScope": (
            "v2.4.2 corrective source mix; controlled continuation from 10k to 15k total with an automatic stop for checkpoint evaluation."
            if run_v242_15k_active
            else "v2.4.1 source-aware core corpus; 10k and its checkpoint evaluation are complete. The next recommendation is a corrective v2.4.2 source mix."
            if run_v241_10k_active and eval_v241_10k_complete
            else "v2.4.1 source-aware core corpus; controlled continuation from 5k to 10k total after the 5k checkpoint evaluation."
            if run_v241_10k_active
            else "v2.3.1 diagnostic 45k→50k finished; 50k is healthy but did not beat 44k, so pretraining is stopped."
            if run50k_active
            else "v2.3.1 continuation 35k→45k. Cleaner FineWeb2-filtered dataset; this is not stage 3 / 50k."
            if run45k_active
            else "v2.3.1 continuation 25k→35k. Cleaner FineWeb2-filtered dataset; this is not stage 3 / 50k."
            if run35k_active
            else "v2.3.1 continuation 15k→25k. Cleaner FineWeb2-filtered dataset; this is not stage 3 / 50k."
            if run25k_active
            else "v2.3.1 preflight 10k→15k. Cleaner FineWeb2-filtered dataset; this is not stage 3 / 50k."
            if preflight_active
            else
            "stage 2 used glyph100_stage1_candidate. glyph100_dataset_v2_2 was built with legacy=0 and "
            "Wikipedia capped to 70%, but it is too small for 50k without another clean source."
            if dataset_v2_2
            else
            "stage 2 used glyph100_stage1_candidate. glyph100_dataset_v2_1 is cleaner and under review; "
            "stage 3 / 50k still needs a separate decision."
            if dataset_v2_1
            else
            "stage 2 used glyph100_stage1_candidate. A source-aware glyph100_dataset_v2 candidate exists, "
            "but sample audit says it is not approved for stage 3 yet."
            if dataset_v2
            else "stage 2 early-training candidate; not the final cleaner corpus for 50k+ runs"
        ),
        "trainTokens": (
            f"{current_dataset.get('train_tokens', 0) / 1_000_000:.1f}M"
            if current_dataset and current_dataset.get("train_tokens")
            else "pending"
        ),
        "valTokens": (
            f"{current_dataset.get('val_tokens', 0) / 1_000_000:.2f}M"
            if current_dataset and current_dataset.get("val_tokens")
            else "pending"
        ),
        "device": "ROCm / RX 5500 XT",
        "rocmSmoke": (
            "batch 4 accum 8 ok · batch 8 ok but tight · batch 16 OOM"
            if stage_smoke_ok
            else "batch 4 recommended · batch 8 ok but tight · batch 16 OOM"
            if max_ok_batch
            else "pending"
        ),
        "effectiveBatch": f"4 × 512 × accum 8 = {GLYPH100_TOKENS_PER_STEP:,}",
        "stage": {
            "step": latest_stage.get("step", 0),
            "totalSteps": stage_total_steps,
            "loss": latest_stage.get("loss"),
            "validationLoss": latest_eval.get("val_loss"),
            "tokensProcessed": latest_stage.get("tokens_m"),
            "log": stage_log_file.relative_to(ROOT).as_posix(),
            "error": (
                {
                    "reason": emergency_reason,
                    "step": emergency_step,
                    "microStep": emergency_micro_step,
                    "latestCheckpointNotOverwritten": bool(emergency.get("latest_checkpoint_not_overwritten")),
                }
                if emergency_active
                else None
            ),
        },
        "readiness": (
            "blocked; inspect emergency_stop.json before any restart"
            if emergency_active
            else "v2.4.2 controlled run is active to 15k; evaluate 10k versus 15k before any continuation"
            if run_v242_15k_active and not stage_complete
            else "v2.4.2 15k checkpoint complete; matched checkpoint evaluation required before any continuation"
            if run_v242_15k_active
            else "v2.4.1 controlled run is active to 10k total; evaluate 7.5k and 10k before any further stage"
            if run_v241_10k_active and not stage_complete
            else "v2.4.1 10k eval complete; prepare v2.4.2 before any further training"
            if run_v241_10k_active and eval_v241_10k_complete
            else "v2.4.1 10k run complete; checkpoint evaluation required before any further stage"
            if run_v241_10k_active
            else "pretraining stopped; 44k is best practical checkpoint; next decision is SFT smoke test or dataset v2.4"
            if run50k_active and stage_complete and eval50k_complete
            else "v2.3.1 50k diagnostic complete; final decision pending"
            if run50k_active and stage_complete
            else "v2.3.1 50k diagnostic running; do not start further stages"
            if run50k_active
            else "v2.3.1 45k run complete; eval complete; no further stage without separate approval"
            if run45k_active and stage_complete and eval45k_complete
            else "v2.3.1 45k run complete; no further stage without separate approval"
            if run45k_active and stage_complete
            else "v2.3.1 45k run running to 45k total; no stage 3 / 50k"
            if run45k_active
            else "v2.3.1 35k run complete; eval complete; no further stage without separate approval"
            if run35k_active and stage_complete and eval35k_complete
            else "v2.3.1 35k run complete; no further stage without separate approval"
            if run35k_active and stage_complete
            else "v2.3.1 35k run running to 35k total; no stage 3 / 50k"
            if run35k_active
            else "v2.3.1 25k run complete; eval complete; no further stage without separate approval"
            if run25k_active and stage_complete and eval25k_complete
            else "v2.3.1 25k run complete; no further stage without separate approval"
            if run25k_active and stage_complete
            else "v2.3.1 25k run running to 25k total; no stage 3 / 50k"
            if run25k_active
            else "v2.3.1 preflight complete; stage 3 still requires separate approval"
            if preflight_active and stage_complete
            else "v2.3.1 preflight running to 15k total; no stage 3"
            if preflight_active
            else "stage 2 complete; dataset v2.2 built, but more clean non-Wikipedia data is needed before stage 3"
            if stage_complete and dataset_v2_2
            else "stage 2 complete; dataset v2.1 cleanup/audit pending before stage 3"
            if stage_complete
            else "stage 2 approved/running to 10k total"
            if stage_step >= GLYPH100_STAGE1_STEPS and max_ok_batch and dataset and dataset.get("train_tokens")
            else "prepared, waiting for explicit approval"
            if max_ok_batch and dataset and dataset.get("train_tokens")
            else "pending"
        ),
        "notes": (
            "Glyph-100M v2.4.2 15k checkpoint run stopped before completion; inspect the emergency report before any restart."
            if emergency_active and run_v242_15k_active
            else "Glyph-100M v2.4.1 10k run stopped before completion; inspect the emergency report before any restart."
            if emergency_active and run_v241_10k_active
            else "Stage 2 stopped on a non-finite loss during resume. latest.pt remains the stage-1 checkpoint at step 1000."
            if emergency_active
            else "Glyph-100M is continuing v2.4.2 from 10k to 15k total on the same corrective source mix. It will stop at 15k for evaluation."
            if run_v242_15k_active and not stage_complete
            else "Glyph-100M v2.4.2 reached 15k. Matched checkpoint evaluation is required before any continuation."
            if run_v242_15k_active
            else "Glyph-100M is running a controlled v2.4.1 continuation from 5k to 10k total on the source-aware core corpus."
            if run_v241_10k_active and not stage_complete
            else "Glyph-100M v2.4.1 reached 10k. Eval is complete: it beats the historical 10k at equal exposure, but semantic quality remains weak, so v2.4.2 data correction is next."
            if run_v241_10k_active and eval_v241_10k_complete
            else "Glyph-100M v2.4.1 reached 10k; checkpoint evaluation is pending and no further stage is approved."
            if run_v241_10k_active
            else "Glyph-100M v2.3.1 pretraining is stopped. 50k was technically healthy, but broad eval and seed sensitivity keep 44k as the best practical checkpoint."
            if run50k_active and stage_complete and eval50k_complete
            else "Glyph-100M is running a diagnostic v2.3.1 continuation from 45k to 50k total. This is not a new default best checkpoint."
            if run50k_active and not stage_complete
            else "Glyph-100M v2.3.1 50k diagnostic is complete. Final decision is pending."
            if run50k_active
            else "Glyph-100M is running a v2.3.1 continuation from 35k to 45k total. This is not stage 3 / 50k."
            if run45k_active and not stage_complete
            else "Glyph-100M v2.3.1 45k run and eval are complete. The next stage still needs a separate decision."
            if run45k_active and eval45k_complete
            else "Glyph-100M v2.3.1 45k run is complete. Eval is pending and the next stage still needs a separate decision."
            if run45k_active
            else "Glyph-100M is running a v2.3.1 continuation from 25k to 35k total. This is not stage 3 / 50k."
            if run35k_active and not stage_complete
            else "Glyph-100M v2.3.1 35k run and eval are complete. The next stage still needs a separate decision."
            if run35k_active and eval35k_complete
            else "Glyph-100M v2.3.1 35k run is complete. Eval is pending and the next stage still needs a separate decision."
            if run35k_active
            else "Glyph-100M is running a v2.3.1 continuation from 15k to 25k total. This is not stage 3 / 50k."
            if run25k_active and not stage_complete
            else "Glyph-100M v2.3.1 25k run and eval are complete. The next stage still needs a separate decision."
            if run25k_active and eval25k_complete
            else "Glyph-100M v2.3.1 25k run is complete. Eval is pending and the next stage still needs a separate decision."
            if run25k_active
            else "Glyph-100M is running a v2.3.1 preflight from 10k to 15k total. This is a dataset sanity run, not stage 3 / 50k."
            if preflight_active and not stage_complete
            else "Glyph-100M v2.3.1 preflight is complete. Stage 3 still needs a separate decision."
            if preflight_active
            else "Stage 2 early-training run is complete. Dataset v2.2 is cleaner and source-aware, but too small for 50k without another clean source."
            if stage_complete and dataset_v2_2
            else "Stage 2 early-training run is complete. The next decision is dataset v2.1 quality before stage 3 / 50k."
            if stage_complete
            else "Glyph-100M stage 2 is an early-training check, not a final long run."
        ),
    }
    if next_dataset:
        state["nextDataset"] = {
            "name": next_dataset.get("dataset_name", "glyph100_dataset_v2_3_1"),
            "trainTokens": f"{next_dataset.get('train_tokens', 0) / 1_000_000:.1f}M",
            "valTokens": f"{next_dataset.get('val_tokens', 0) / 1_000_000:.2f}M",
            "status": next_dataset.get("selected_variant", "candidate built"),
            "recommendation": next_dataset.get("recommendation", "review required"),
        }
    if run_v242_15k_active or run_v241_10k_active or v231_active:
        state["checkpoint"] = {
            "label": glyph100_checkpoint_label(
                stage_checkpoint_dir,
                "glyph-100m-v2_4_2-15k-latest"
                if run_v242_15k_active
                else "glyph-100m-v2_4_1-10k-latest"
                if run_v241_10k_active
                else "glyph-100m-v2_3_1-50k-latest-diagnostic"
                if run50k_active
                else "glyph-100m-v2_3_1-45k-latest"
                if run45k_active
                else "glyph-100m-v2_3_1-35k-latest"
                if run35k_active
                else "glyph-100m-v2_3_1-25k-latest"
                if run25k_active
                else "glyph-100m-v2_3_1-preflight-latest",
                "glyph-100m-v2_4_2-10k-resume"
                if run_v242_15k_active
                else "glyph-100m-v2_4_1-5k-resume"
                if run_v241_10k_active
                else "not found",
            ),
            "updatedAt": glyph100_checkpoint_public_mtime(stage_checkpoint_dir),
        }
        if run50k_active:
            state["bestCheckpoint"] = {
                "label": "44k best practical",
                "reason": "Broad eval and seed sensitivity keep 44k above 50k.",
            }
    return state


def tokens_per_step(steps: list[dict]) -> float:
    for prev, cur in zip(reversed(steps[:-1]), reversed(steps[1:])):
        step_delta = cur["step"] - prev["step"]
        token_delta = (cur["tokens_m"] - prev["tokens_m"]) * 1_000_000
        if step_delta > 0 and token_delta > 0:
            return token_delta / step_delta
    return DEFAULT_TOKENS_PER_STEP


def export_training() -> dict:
    glyph100_v242_15k = GLYPH100_V242_15K_LOG_FILE.exists()
    glyph100_v241_10k = GLYPH100_V241_10K_LOG_FILE.exists() and not glyph100_v242_15k
    glyph100_50k = GLYPH100_V231_50K_LOG_FILE.exists() and not glyph100_v242_15k and not glyph100_v241_10k
    glyph100_45k = GLYPH100_V231_45K_LOG_FILE.exists() and not glyph100_v242_15k and not glyph100_v241_10k and not glyph100_50k
    glyph100_35k = GLYPH100_V231_35K_LOG_FILE.exists() and not glyph100_v242_15k and not glyph100_v241_10k and not glyph100_50k and not glyph100_45k
    glyph100_25k = GLYPH100_V231_25K_LOG_FILE.exists() and not glyph100_v242_15k and not glyph100_v241_10k and not glyph100_50k and not glyph100_45k and not glyph100_35k
    glyph100_preflight = GLYPH100_PREFLIGHT_LOG_FILE.exists() and not glyph100_v242_15k and not glyph100_v241_10k and not glyph100_50k and not glyph100_45k and not glyph100_35k and not glyph100_25k
    glyph100_active = glyph100_v242_15k or glyph100_v241_10k or glyph100_50k or glyph100_45k or glyph100_35k or glyph100_25k or glyph100_preflight or GLYPH100_LOG_FILE.exists()
    glyph100_log = (
        GLYPH100_V242_15K_LOG_FILE
        if glyph100_v242_15k
        else GLYPH100_V241_10K_LOG_FILE
        if glyph100_v241_10k
        else GLYPH100_V231_50K_LOG_FILE
        if glyph100_50k
        else GLYPH100_V231_45K_LOG_FILE
        if glyph100_45k
        else GLYPH100_V231_35K_LOG_FILE
        if glyph100_35k
        else GLYPH100_V231_25K_LOG_FILE
        if glyph100_25k
        else GLYPH100_PREFLIGHT_LOG_FILE
        if glyph100_preflight
        else GLYPH100_LOG_FILE
    )
    glyph100_checkpoint_dir = (
        GLYPH100_V242_15K_CHECKPOINT_DIR
        if glyph100_v242_15k
        else GLYPH100_V241_10K_CHECKPOINT_DIR
        if glyph100_v241_10k
        else GLYPH100_V231_50K_CHECKPOINT_DIR
        if glyph100_50k
        else GLYPH100_V231_45K_CHECKPOINT_DIR
        if glyph100_45k
        else GLYPH100_V231_35K_CHECKPOINT_DIR
        if glyph100_35k
        else GLYPH100_V231_25K_CHECKPOINT_DIR
        if glyph100_25k
        else GLYPH100_PREFLIGHT_CHECKPOINT_DIR
        if glyph100_preflight
        else GLYPH100_CHECKPOINT_DIR
    )
    glyph100_emergency = (
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
    emergency = read_json(glyph100_emergency) if glyph100_active else {}
    emergency_reason = emergency.get("reason")
    emergency_step = emergency.get("step")
    steps, evals = parse_log(glyph100_log if glyph100_active else LEGACY_27M_LOG_FILE)
    latest = steps[-1] if steps else {}
    recent = steps[-30:] if steps else []
    avg_toks = sum(row["toks"] for row in recent) / len(recent) if recent else None
    total_steps = (
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
        if glyph100_active
        else TOTAL_STEPS
    )
    step = latest.get("step", 0)
    emergency_active = bool(emergency_reason and (not latest or emergency_step is None or emergency_step > step))
    progress = step / total_steps * 100 if total_steps else 0
    tps = tokens_per_step(steps) if not glyph100_active else GLYPH100_TOKENS_PER_STEP
    steps_per_hour = avg_toks / tps * 3600 if avg_toks and tps else None
    last_eval = evals[-1] if evals else {}

    last_dt = parse_log_time(latest.get("ts", ""))
    age_minutes = None
    if last_dt:
        age_minutes = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
    if glyph100_active:
        if emergency_active:
            status = (
                f"Glyph-100M v2.4.2 15k checkpoint run stopped: {emergency_reason}"
                if glyph100_v242_15k
                else f"Glyph-100M v2.4.1 10k stopped: {emergency_reason}"
                if glyph100_v241_10k
                else f"Glyph-100M v2.3.1 50k diagnostic stopped: {emergency_reason}"
                if glyph100_50k
                else f"Glyph-100M v2.3.1 45k stopped: {emergency_reason}"
                if glyph100_45k
                else f"Glyph-100M v2.3.1 35k stopped: {emergency_reason}"
                if glyph100_35k
                else f"Glyph-100M v2.3.1 25k stopped: {emergency_reason}"
                if glyph100_25k
                else f"Glyph-100M v2.3.1 preflight stopped: {emergency_reason}"
                if glyph100_preflight
                else f"Glyph-100M stage 2 stopped: {emergency_reason}"
            )
        elif glyph100_v242_15k and step >= GLYPH100_V242_15K_STEPS:
            status = "Glyph-100M v2.4.2 15k checkpoint complete; eval pending"
        elif glyph100_v242_15k:
            status = (
                "Glyph-100M v2.4.2 controlled run to 15k"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.4.2 15k run snapshot"
            )
        elif glyph100_v241_10k and step >= GLYPH100_V241_10K_STEPS:
            status = (
                "Glyph-100M v2.4.1 10k complete; eval complete"
                if GLYPH100_V241_10K_EVAL_REPORT.exists()
                else "Glyph-100M v2.4.1 10k complete; eval pending"
            )
        elif glyph100_v241_10k:
            status = (
                "Glyph-100M v2.4.1 training to 10k"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.4.1 10k snapshot"
            )
        elif glyph100_50k and step >= GLYPH100_V231_50K_STEPS:
            status = "Glyph-100M v2.3.1 pretraining stopped; 44k best, 50k diagnostic complete"
        elif glyph100_50k:
            status = (
                "Glyph-100M v2.3.1 50k diagnostic running"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.3.1 50k diagnostic snapshot"
            )
        elif glyph100_45k and step >= GLYPH100_V231_45K_STEPS:
            status = "Glyph-100M v2.3.1 45k complete + eval complete" if GLYPH100_V231_45K_EVAL_REPORT.exists() else "Glyph-100M v2.3.1 45k complete + eval pending"
        elif glyph100_45k:
            status = (
                "Glyph-100M v2.3.1 45k running"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.3.1 45k snapshot"
            )
        elif glyph100_35k and step >= GLYPH100_V231_35K_STEPS:
            status = "Glyph-100M v2.3.1 35k complete + eval complete" if GLYPH100_V231_35K_EVAL_REPORT.exists() else "Glyph-100M v2.3.1 35k complete + eval pending"
        elif glyph100_35k:
            status = (
                "Glyph-100M v2.3.1 35k running"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.3.1 35k snapshot"
            )
        elif glyph100_25k and step >= GLYPH100_V231_25K_STEPS:
            status = "Glyph-100M v2.3.1 25k complete + eval complete" if GLYPH100_V231_25K_EVAL_REPORT.exists() else "Glyph-100M v2.3.1 25k complete + eval pending"
        elif glyph100_25k:
            status = (
                "Glyph-100M v2.3.1 25k running"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.3.1 25k snapshot"
            )
        elif glyph100_preflight and step >= GLYPH100_PREFLIGHT_STEPS:
            status = "Glyph-100M v2.3.1 preflight complete"
        elif glyph100_preflight:
            status = (
                "Glyph-100M v2.3.1 preflight running"
                if age_minutes is None or age_minutes < 30
                else "Glyph-100M v2.3.1 preflight snapshot"
            )
        elif step >= GLYPH100_ACTIVE_STAGE_STEPS:
            status = "Glyph-100M stage 2 complete"
        else:
            status = "Glyph-100M stage 2 training in progress" if age_minutes is None or age_minutes < 30 else "Glyph-100M stage 2 snapshot"
    else:
        status = "pretraining in progress" if age_minutes is None or age_minutes < 30 else "training log snapshot"

    payload = {
        "snapshotDate": datetime.now(timezone.utc).astimezone(WARSAW).strftime("%Y-%m-%d %H:%M %Z"),
        "snapshotAt": datetime.now(timezone.utc).isoformat(),
        "status": status if glyph100_active else ("27M complete + 100M preparation" if SFT_CHECKPOINT.exists() else status),
        "step": step,
        "totalSteps": total_steps,
        "progressPct": round(progress, 3),
        "trainLoss": compact_number(latest.get("loss")),
        "validationLoss": compact_number(last_eval.get("val_loss")),
        "tokensProcessed": compact_tokens(latest.get("tokens_m")),
        "learningRate": compact_number(latest.get("lr")),
        "throughput": compact_toks(avg_toks or latest.get("toks")),
        "stepsPerHour": None if steps_per_hour is None else round(steps_per_hour),
        "lastLogAt": public_time(latest.get("ts")),
        "lastValidationAt": public_time(last_eval.get("ts")),
        "checkpoint": (
            glyph100_checkpoint_label(
                glyph100_checkpoint_dir,
                "glyph-100m-v2_4_2-15k-latest"
                if glyph100_v242_15k
                else "glyph-100m-v2_4_1-10k-latest"
                if glyph100_v241_10k
                else "glyph-100m-v2_3_1-50k-latest-diagnostic"
                if glyph100_50k
                else "glyph-100m-v2_3_1-45k-latest"
                if glyph100_45k
                else "glyph-100m-v2_3_1-35k-latest"
                if glyph100_35k
                else "glyph-100m-v2_3_1-25k-latest"
                if glyph100_25k
                else "glyph-100m-v2_3_1-preflight-latest",
                "glyph-100m-v2_4_2-10k-resume"
                if glyph100_v242_15k
                else "glyph-100m-v2_4_1-5k-resume"
                if glyph100_v241_10k
                else "not found",
            )
            if glyph100_v242_15k or glyph100_v241_10k or glyph100_50k or glyph100_45k or glyph100_35k or glyph100_25k or glyph100_preflight
            else glyph100_checkpoint_label()
            if glyph100_active
            else checkpoint_label()
        ),
        "checkpointUpdatedAt": (
            glyph100_checkpoint_public_mtime(glyph100_checkpoint_dir)
            if glyph100_active
            else checkpoint_public_mtime()
        ),
        "notes": (
            "Glyph-100M v2.4.2 15k checkpoint run stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_v242_15k
            else "Glyph-100M v2.4.1 10k run stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_v241_10k
            else "Glyph-100M v2.3.1 45k was stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_45k
            else "Glyph-100M v2.3.1 50k diagnostic stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_50k
            else "Glyph-100M v2.3.1 35k was manually stopped before completion for a batch-size benchmark. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_35k
            else "Glyph-100M v2.3.1 25k was stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_25k
            else "Glyph-100M v2.3.1 preflight was stopped before completion. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active and glyph100_preflight
            else "Glyph-100M stage 2 is currently stopped. "
            "No training is currently running. Public snapshot only; operational details are intentionally excluded."
            if emergency_active
            else "Glyph-100M is running a controlled v2.4.2 continuation from 10k to 15k total. It will stop at 15k for evaluation. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_v242_15k and step < GLYPH100_V242_15K_STEPS
            else "Glyph-100M v2.4.2 reached 15k. Matched checkpoint evaluation is pending. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_v242_15k
            else "Glyph-100M v2.4.1 reached 10k. Evaluation is required before any further stage. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_v241_10k and step >= GLYPH100_V241_10K_STEPS
            else "Glyph-100M is running a controlled v2.4.1 continuation from 5k to 10k total. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_v241_10k
            else "Glyph-100M v2.3.1 pretraining is stopped. 44k is the best practical checkpoint; 50k is healthy diagnostic latest, not best. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_50k and step >= GLYPH100_V231_50K_STEPS
            else "Glyph-100M is running the v2.3.1 diagnostic continuation from 45k to 50k total. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_50k
            else "Glyph-100M is running the v2.3.1 continuation from 35k to 45k total. This is not stage 3 / 50k. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_45k and step < GLYPH100_V231_45K_STEPS
            else "Glyph-100M v2.3.1 45k run and eval are complete. The next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_45k and GLYPH100_V231_45K_EVAL_REPORT.exists()
            else "Glyph-100M v2.3.1 45k run is complete. Eval is pending and the next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_45k
            else "Glyph-100M is running the v2.3.1 continuation from 25k to 35k total. This is not stage 3 / 50k. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_35k and step < GLYPH100_V231_35K_STEPS
            else "Glyph-100M v2.3.1 35k run and eval are complete. The next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_35k and GLYPH100_V231_35K_EVAL_REPORT.exists()
            else "Glyph-100M v2.3.1 35k run is complete. Eval is pending and the next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_35k
            else "Glyph-100M is running the v2.3.1 continuation from 15k to 25k total. This is not stage 3 / 50k. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_25k and step < GLYPH100_V231_25K_STEPS
            else "Glyph-100M v2.3.1 25k run and eval are complete. The next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_25k and GLYPH100_V231_25K_EVAL_REPORT.exists()
            else "Glyph-100M v2.3.1 25k run is complete. Eval is pending and the next stage still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_25k
            else "Glyph-100M is running the v2.3.1 preflight from 10k to 15k total. This is not stage 3 / 50k. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_preflight and step < GLYPH100_PREFLIGHT_STEPS
            else "Glyph-100M v2.3.1 preflight is complete. Stage 3 still needs separate approval. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_preflight
            else "Glyph-100M is the active stage-2 early-training run. Glyph-27M remains a completed proof-of-pipeline milestone. "
            "Public snapshot only; operational details are intentionally excluded."
            if glyph100_active
            else "Public snapshot only. Operational details are intentionally excluded."
        ),
    }
    sft = export_sft_state()
    if sft:
        payload["sft"] = sft
    glyph100 = export_glyph100_state()
    if glyph100:
        payload["glyph100"] = glyph100
    atomic_write_json(SITE_DATA / "training.json", payload)
    return payload


def export_evaluation() -> dict:
    summary = read_json(GEMMA_SUMMARY)
    averages = summary.get("averages") or {}
    training_stats = summary.get("training_stats") or {}
    generated_at = summary.get("generated_at")

    payload = {
        "method": "Gemma Judge over fixed Polish continuation prompts",
        "snapshotDate": public_report_time(generated_at),
        "count": int(summary.get("count") or 0),
        "validCount": int(summary.get("valid_count") or 0),
        "overall": summary.get("overall_avg"),
        "metrics": {
            "continuationFit": averages.get("continuation_fit"),
            "polish": averages.get("polish"),
            "coherence": averages.get("coherence"),
            "repetition": averages.get("repetition"),
            "safety": averages.get("safety"),
        },
        "checkpointStep": training_stats.get("step"),
        "trainLoss": training_stats.get("loss"),
        "validationLoss": (training_stats.get("last_eval") or {}).get("val_loss"),
        "learningRate": training_stats.get("lr"),
        "description": summary.get("description") or summary.get("gemma_description") or "No Gemma evaluation has been exported yet.",
        "categories": [
            "Polish fluency",
            "coherence",
            "repetition",
            "topic adherence",
            "technical style",
        ],
        "failureModes": [
            "phrase repetition",
            "topic drift",
            "SEO/forum-like text leakage",
            "weak factual reliability",
            "unstable long continuations",
        ],
    }
    atomic_write_json(SITE_DATA / "evaluation.json", payload)
    return payload


def score_value(row: dict, key: str = "overall") -> float | None:
    value = (row.get("scores") or {}).get(key)
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return None


def kind_for_score(score: float | None) -> str:
    if score is None:
        return "typical"
    if score >= 3.5:
        return "good"
    if score <= 2.25:
        return "failure"
    return "typical"


def pick_representative_samples(rows: list[dict], limit: int) -> list[dict]:
    valid = [row for row in rows if score_value(row) is not None]
    if not valid:
        return rows[:limit]

    ordered = sorted(valid, key=lambda row: score_value(row) or 0, reverse=True)
    good_count = max(1, limit // 3)
    failure_count = max(1, limit // 3)
    typical_count = max(1, limit - good_count - failure_count)
    if good_count + typical_count + failure_count > limit:
        typical_count = max(0, limit - good_count - failure_count)

    bottom = sorted(valid, key=lambda row: score_value(row) or 0)[:failure_count]
    top = ordered[:good_count]
    middle_ordered = sorted(valid, key=lambda row: abs((score_value(row) or 0) - 3.0))
    middle = middle_ordered[:typical_count]

    chosen: list[dict] = []
    seen: set[str] = set()
    for group in (top, middle, bottom, ordered):
        for row in group:
            prompt_id = str(row.get("prompt_id") or len(chosen))
            if prompt_id in seen:
                continue
            chosen.append(row)
            seen.add(prompt_id)
            if len(chosen) >= limit:
                return chosen
    return chosen


def english_diagnostic(row: dict) -> str:
    scores = row.get("scores") or {}
    overall = score_value(row)
    scored = [
        (key, value)
        for key, value in scores.items()
        if key != "safety" and isinstance(value, (int, float)) and math.isfinite(value)
    ]
    weakest = sorted(scored, key=lambda item: item[1])[:2]
    weakest_text = ", ".join(f"{name} {value:.1f}/5" for name, value in weakest) or "no reliable metric"
    if overall is None:
        return "The judge did not return a complete score for this sample."
    return f"Gemma Judge rated this continuation {overall:.1f}/5. The weakest signals are {weakest_text}."


def export_samples(limit: int) -> list[dict]:
    judged_rows = read_jsonl(GEMMA_REPORT)
    raw_samples = {row.get("prompt_id"): row for row in read_jsonl(SAMPLE_REPORT)}
    selected = pick_representative_samples(judged_rows, limit)

    public_rows = []
    for row in selected:
        prompt_id = row.get("prompt_id")
        raw = raw_samples.get(prompt_id) or {}
        score = score_value(row)
        scores = row.get("scores") or {}
        public_rows.append(
            {
                "kind": kind_for_score(score),
                "promptId": prompt_id,
                "category": row.get("category") or raw.get("category") or "unknown",
                "mode": row.get("mode") or raw.get("mode") or "base",
                "step": row.get("checkpoint_step") or raw.get("checkpoint_step"),
                "generatedAt": raw.get("generated_at") or row.get("judged_at"),
                "settings": {
                    "maxTokens": raw.get("max_tokens"),
                    "temperature": raw.get("temperature"),
                    "topK": raw.get("top_k"),
                    "topP": raw.get("top_p"),
                    "repetitionPenalty": raw.get("repetition_penalty"),
                    "noRepeatNgram": raw.get("no_repeat_ngram_size"),
                },
                "prompt": row.get("prompt") or raw.get("prompt") or "",
                "output": row.get("mini_response") or raw.get("response") or "",
                "scores": {
                    "continuationFit": scores.get("continuation_fit"),
                    "polish": scores.get("polish"),
                    "coherence": scores.get("coherence"),
                    "repetition": scores.get("repetition"),
                    "safety": scores.get("safety"),
                    "overall": score,
                },
                "comment": {
                    "pl": row.get("notes") or row.get("error") or "Brak komentarza Gemmy dla tej próbki.",
                    "en": english_diagnostic(row),
                },
            }
        )

    atomic_write_json(SITE_DATA / "samples.json", public_rows)
    return public_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Export sanitized JSON for glyph.maksu.online")
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    training = export_training()
    evaluation = export_evaluation()
    samples = export_samples(max(3, args.sample_limit))

    if not args.quiet:
        print(
            "Exported public Glyph snapshot: "
            f"step={training.get('step')}/{training.get('totalSteps')}, "
            f"overall={evaluation.get('overall')}, samples={len(samples)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
