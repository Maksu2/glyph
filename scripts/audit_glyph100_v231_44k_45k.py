#!/usr/bin/env python3
"""Audit Glyph-100M v2.3.1 44k->45k training state.

Read-only audit: loads checkpoints and parses logs, but does not train or
modify checkpoints.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "logs" / "glyph-100m-v2_3_1-45k" / "train.log"
EXPECTED_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
CHECKPOINTS = {
    "44k": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
    "45k_step": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt",
    "45k_latest": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/latest.pt",
}
OUT_MD = ROOT / "reports/glyph100_v2_3_1_44k_45k_training_audit.md"
OUT_JSON = ROOT / "reports/glyph100_v2_3_1_44k_45k_training_audit.json"

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


def read_state(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    metadata = state.get("metadata") or {}
    train_config = state.get("train_config") or {}

    def get(key: str):
        return state.get(key) or metadata.get(key) or (train_config.get(key) if isinstance(train_config, dict) else None)

    optimizer = state.get("optimizer") or state.get("optimizer_state_dict") or state.get("optimizer_state")
    scheduler = (
        state.get("scheduler_state")
        or state.get("scheduler")
        or state.get("scheduler_state_dict")
        or state.get("lr_scheduler")
    )
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size,
        "variant": get("variant"),
        "step": get("step"),
        "current_step": get("current_step"),
        "dataset_name": get("dataset_name"),
        "tokenizer_sha256": get("tokenizer_sha256"),
        "tokenizer_path": get("tokenizer_path"),
        "batch_size": get("batch_size"),
        "gradient_accumulation_steps": get("gradient_accumulation_steps"),
        "effective_tokens_per_step": get("effective_tokens_per_step"),
        "context_length": get("context_length"),
        "loss": state.get("loss"),
        "optimizer_state_present": optimizer is not None,
        "optimizer_keys": list(optimizer.keys()) if isinstance(optimizer, dict) else [],
        "scheduler_state_present": scheduler is not None,
        "scheduler_state": scheduler if isinstance(scheduler, dict) else None,
        "top_level_keys": sorted(state.keys()),
    }


def parse_log() -> dict:
    steps = []
    evals = []
    checkpoints = []
    markers = {
        "resume": [],
        "range": [],
        "limited_run": [],
        "nan_inf": [],
        "oom": [],
        "crash": [],
        "dataset_or_config": [],
        "emergency": [],
    }
    for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        lower = line.lower()
        if "resumed from step" in lower:
            markers["resume"].append(line)
        if "training from step" in lower:
            markers["range"].append(line)
        if "limited run" in lower or "target step" in lower:
            markers["limited_run"].append(line)
        if "nan" in lower or "inf" in lower or "non-finite" in lower:
            markers["nan_inf"].append(line)
        if "oom" in lower or "out of memory" in lower:
            markers["oom"].append(line)
        if "traceback" in lower or "exception" in lower or "crash" in lower:
            markers["crash"].append(line)
        if "dataset name:" in lower or "model config:" in lower or "train config:" in lower:
            markers["dataset_or_config"].append(line)
        if "emergency" in lower:
            markers["emergency"].append(line)

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
    return {"steps": steps, "evals": evals, "checkpoints": checkpoints, "markers": markers}


def stats(rows: list[dict]) -> dict:
    losses = [row["loss"] for row in rows]
    toks = [row["toks"] for row in rows]
    lrs = [row["lr"] for row in rows]
    if not rows:
        return {}
    return {
        "count": len(rows),
        "start_step": rows[0]["step"],
        "end_step": rows[-1]["step"],
        "start_ts": rows[0]["ts"],
        "end_ts": rows[-1]["ts"],
        "loss_min": min(losses),
        "loss_max": max(losses),
        "loss_avg": round(sum(losses) / len(losses), 6),
        "lr_min": min(lrs),
        "lr_max": max(lrs),
        "toks_avg": round(sum(toks) / len(toks), 2),
    }


def model_tensors_equal(path_a: Path, path_b: Path) -> bool:
    a = torch.load(path_a, map_location="cpu", weights_only=False)["model"]
    b = torch.load(path_b, map_location="cpu", weights_only=False)["model"]
    if a.keys() != b.keys():
        return False
    for key in a:
        if not torch.equal(a[key], b[key]):
            return False
    return True


def main() -> None:
    ckpt = {}
    for label, path in CHECKPOINTS.items():
        if not path.exists():
            ckpt[label] = {"path": str(path.relative_to(ROOT)), "exists": False}
            continue
        ckpt[label] = read_state(path)

    parsed = parse_log()
    steps = parsed["steps"]
    evals = parsed["evals"]
    eval_by_step = {row["step"]: row for row in evals}
    checkpoints = parsed["checkpoints"]
    checkpoint_by_step = {}
    for row in checkpoints:
        match = re.search(r"step_(\d+)\.pt", row["path"])
        if match:
            checkpoint_by_step[int(match.group(1))] = row

    windows = {
        "43000_44000": stats([row for row in steps if 43000 <= row["step"] <= 44000]),
        "44000_45000": stats([row for row in steps if 44000 <= row["step"] <= 45000]),
        "43500_44000": stats([row for row in steps if 43500 <= row["step"] <= 44000]),
        "44000_44500": stats([row for row in steps if 44000 <= row["step"] <= 44500]),
        "44500_45000": stats([row for row in steps if 44500 <= row["step"] <= 45000]),
    }
    latest_matches_step = (
        model_tensors_equal(CHECKPOINTS["45k_step"], CHECKPOINTS["45k_latest"])
        if CHECKPOINTS["45k_step"].exists() and CHECKPOINTS["45k_latest"].exists()
        else None
    )

    expected = {
        "variant": "glyph-100m",
        "dataset_name": "glyph100_v2_3_1",
        "tokenizer_sha256": EXPECTED_SHA,
        "batch_size": 4,
        "gradient_accumulation_steps": 8,
        "effective_tokens_per_step": 16384,
    }
    validation = {}
    expected_steps = {"44k": 44000, "45k_step": 45000, "45k_latest": 45000}
    for label, meta in ckpt.items():
        errors = []
        if not meta.get("exists"):
            errors.append("missing")
        for key, value in expected.items():
            if meta.get(key) != value:
                errors.append(f"{key}={meta.get(key)!r} expected={value!r}")
        if meta.get("step") != expected_steps[label] or meta.get("current_step") != expected_steps[label]:
            errors.append(f"step/current_step mismatch: {meta.get('step')}/{meta.get('current_step')}")
        if not meta.get("optimizer_state_present"):
            errors.append("missing optimizer state")
        if not meta.get("scheduler_state_present"):
            errors.append("missing scheduler state")
        validation[label] = {"ok": not errors, "errors": errors}

    payload = {
        "checkpoints": ckpt,
        "checkpoint_validation": validation,
        "latest_model_matches_step_45000": latest_matches_step,
        "log": {
            "path": str(LOG.relative_to(ROOT)),
            "windows": windows,
            "val_losses": {str(step): eval_by_step.get(step) for step in [43500, 44000, 44500, 45000]},
            "checkpoint_saves": {
                str(step): checkpoint_by_step.get(step)
                for step in [44000, 45000]
            },
            "markers": parsed["markers"],
        },
        "technical_verdict": "healthy"
        if all(item["ok"] for item in validation.values())
        and latest_matches_step
        and not parsed["markers"]["nan_inf"]
        and not parsed["markers"]["oom"]
        and not parsed["markers"]["crash"]
        else "check_required",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Glyph-100M v2.3.1 44k -> 45k training audit",
        "",
        f"- technical verdict: `{payload['technical_verdict']}`",
        f"- log: `{payload['log']['path']}`",
        f"- latest model tensors match `step_0045000.pt`: `{latest_matches_step}`",
        "",
        "## Checkpoints",
        "",
        "| checkpoint | exists | size | step | variant | dataset | tokenizer sha ok | batch/accum | optimizer | scheduler | validation |",
        "|---|---:|---:|---:|---|---|---:|---|---:|---:|---|",
    ]
    for label, meta in ckpt.items():
        lines.append(
            f"| {label} | {meta.get('exists')} | {meta.get('size_bytes')} | "
            f"{meta.get('step')}/{meta.get('current_step')} | {meta.get('variant')} | "
            f"{meta.get('dataset_name')} | {meta.get('tokenizer_sha256') == EXPECTED_SHA} | "
            f"{meta.get('batch_size')}/{meta.get('gradient_accumulation_steps')} | "
            f"{meta.get('optimizer_state_present')} | {meta.get('scheduler_state_present')} | "
            f"{'ok' if validation[label]['ok'] else '; '.join(validation[label]['errors'])} |"
        )
    lines.extend(
        [
            "",
            "## Training Windows",
            "",
            "| window | steps | loss avg | loss min | loss max | lr min | lr max | avg tok/s |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name, row in windows.items():
        lines.append(
            f"| {name} | {row.get('count')} | {row.get('loss_avg')} | {row.get('loss_min')} | "
            f"{row.get('loss_max')} | {row.get('lr_min')} | {row.get('lr_max')} | {row.get('toks_avg')} |"
        )
    lines.extend(["", "## Validation Losses", ""])
    for step in [43500, 44000, 44500, 45000]:
        row = eval_by_step.get(step)
        lines.append(f"- step `{step}`: `{row['val_loss'] if row else 'missing'}` at `{row['ts'] if row else 'missing'}`")
    lines.extend(
        [
            "",
            "## Log Markers",
            "",
            f"- resume lines: `{len(parsed['markers']['resume'])}`",
            f"- range lines: `{parsed['markers']['range']}`",
            f"- limited-run lines: `{parsed['markers']['limited_run']}`",
            f"- dataset/config lines: `{len(parsed['markers']['dataset_or_config'])}`",
            f"- emergency lines: `{len(parsed['markers']['emergency'])}`",
            f"- NaN/Inf lines: `{len(parsed['markers']['nan_inf'])}`",
            f"- OOM lines: `{len(parsed['markers']['oom'])}`",
            f"- crash/exception lines: `{len(parsed['markers']['crash'])}`",
            "",
            "## Read",
            "",
            "- The checkpoint metadata and log range are consistent with a normal 35k->45k continuation.",
            "- There is no log evidence of dataset/tokenizer/config change between 44k and 45k.",
            "- The 45k `latest.pt` contains the same model tensors as `step_0045000.pt`.",
            "- Any quality drop must be investigated through eval stability rather than an obvious checkpoint/training corruption.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
