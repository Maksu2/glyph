#!/usr/bin/env python3
"""Small health check for Glyph training containers and log progress."""
import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs" / "train.log"
WATCHDOG_STATE = ROOT / "logs" / "training-watchdog-state.json"
RESOURCE_STATE = ROOT / "logs" / "resource_mode.json"
STEP_RE = re.compile(
    r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*step=\s*(?P<step>\d+).*loss=(?P<loss>[0-9.]+).*tok/s=(?P<toks>[0-9,]+)"
)
VAL_RE = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*eval step=\s*(?P<step>\d+).*val_loss=(?P<loss>[0-9.]+)")


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)


def docker_containers():
    proc = run(["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}"])
    rows = []
    for line in proc.stdout.splitlines():
        name, image, status = (line.split("\t", 2) + ["", ""])[:3]
        if "ai-model-trainer" in image:
            rows.append({"name": name, "image": image, "status": status})
    return rows


def parse_log():
    latest = None
    latest_val = None
    if not LOG.exists():
        return {"latest": None, "latest_val": None}
    with LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = STEP_RE.search(line)
            if match:
                latest = {
                    "timestamp": match.group("ts"),
                    "step": int(match.group("step")),
                    "loss": float(match.group("loss")),
                    "tokens_per_second": int(match.group("toks").replace(",", "")),
                    "line": line.rstrip("\n"),
                }
            match = VAL_RE.search(line)
            if match:
                latest_val = {
                    "timestamp": match.group("ts"),
                    "step": int(match.group("step")),
                    "val_loss": float(match.group("loss")),
                    "line": line.rstrip("\n"),
                }
    return {"latest": latest, "latest_val": latest_val}


def checkpoint_info():
    result = {}
    for name in ["latest.pt", "emergency.pt"]:
        path = ROOT / "checkpoints" / name
        if path.exists():
            stat = path.stat()
            result[name] = {
                "path": str(path),
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            }
    return result


def read_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Check Glyph training progress")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    containers = docker_containers()
    backend = "none"
    if any("rocm" in row["image"] for row in containers):
        backend = "ROCm gfx1012"
    elif any("cpu" in row["image"] for row in containers):
        backend = "CPU"

    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "containers": containers,
        "log": parse_log(),
        "checkpoints": checkpoint_info(),
        "watchdog": read_json(WATCHDOG_STATE),
        "resource_mode": read_json(RESOURCE_STATE),
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    latest = payload["log"]["latest"] or {}
    latest_val = payload["log"]["latest_val"] or {}
    print(f"backend: {backend}")
    print(f"containers: {', '.join(row['name'] for row in containers) or 'none'}")
    print(f"last step: {latest.get('step', 'unknown')} loss={latest.get('loss', 'unknown')} tok/s={latest.get('tokens_per_second', 'unknown')}")
    print(f"last progress: {latest.get('timestamp', 'unknown')}")
    print(f"last val: step={latest_val.get('step', 'none')} val_loss={latest_val.get('val_loss', 'none')}")
    print(f"latest checkpoint: {payload['checkpoints'].get('latest.pt', {}).get('mtime', 'missing')}")
    if payload["watchdog"]:
        print(f"watchdog: {payload['watchdog'].get('status')} container={payload['watchdog'].get('container')} attempts={payload['watchdog'].get('gpu_attempts')}")


if __name__ == "__main__":
    main()
