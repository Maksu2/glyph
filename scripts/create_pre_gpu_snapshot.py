#!/usr/bin/env python3
"""Create a small pre-GPU migration snapshot without copying datasets."""
import argparse
import json
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS = ROOT / "checkpoints"
LOG = ROOT / "logs" / "train.log"
TOKENIZER = ROOT / "data" / "processed" / "tokenizer.model"


STEP_RE = re.compile(r"step=\s*(\d+)")
LOSS_RE = re.compile(r"loss=([0-9.]+)")


def stable_file(path: Path, checks: int = 3, delay: float = 5.0) -> dict:
    observations = []
    for _ in range(checks):
        stat = path.stat()
        observations.append((stat.st_size, stat.st_mtime_ns))
        if len(observations) < checks:
            time.sleep(delay)
    stable = len(set(observations)) == 1
    return {
        "path": str(path),
        "size": observations[-1][0],
        "mtime_ns": observations[-1][1],
        "stable": stable,
        "observations": observations,
    }


def parse_last_training_line():
    if not LOG.exists():
        return {}
    last = ""
    with LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if "step=" in line:
                last = line.rstrip("\n")
    if not last:
        return {}
    step = STEP_RE.search(last)
    loss = LOSS_RE.search(last)
    return {
        "line": last,
        "step": int(step.group(1)) if step else None,
        "loss": float(loss.group(1)) if loss else None,
    }


def copy_if_exists(src: Path, dst_dir: Path, checks: int, delay: float):
    if not src.exists():
        return None
    info = stable_file(src, checks=checks, delay=delay)
    if not info["stable"]:
        raise SystemExit(f"Refusing to copy unstable file: {src} observations={info['observations']}")
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    info["snapshot_path"] = str(dst)
    return info


def main():
    parser = argparse.ArgumentParser(description="Create pre-GPU checkpoint snapshot")
    parser.add_argument("--checks", type=int, default=3)
    parser.add_argument("--delay", type=float, default=5.0)
    args = parser.parse_args()

    stamp = datetime.now().strftime("pre-gpu-%Y%m%d-%H%M%S")
    dst = CHECKPOINTS / "snapshots" / stamp
    dst.mkdir(parents=True, exist_ok=False)

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "snapshot_dir": str(dst),
        "last_training": parse_last_training_line(),
        "files": {},
    }

    candidates = [
        CHECKPOINTS / "latest.pt",
        CHECKPOINTS / "emergency.pt",
    ]
    candidates.extend(sorted(CHECKPOINTS.glob("step_*.pt"), key=lambda p: p.stat().st_mtime)[-2:])

    for src in candidates:
        if src.exists() and src.name not in metadata["files"]:
            metadata["files"][src.name] = copy_if_exists(src, dst, args.checks, args.delay)

    for src in [ROOT / "config.py", TOKENIZER]:
        if src.exists():
            target = dst / src.name if src.name == "config.py" else dst / "tokenizer.model"
            shutil.copy2(src, target)
            metadata["files"][src.name] = {
                "path": str(src),
                "size": src.stat().st_size,
                "mtime_ns": src.stat().st_mtime_ns,
                "snapshot_path": str(target),
            }

    if LOG.exists():
        tail_path = dst / "train-tail.log"
        lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()[-300:]
        tail_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        metadata["files"]["train-tail.log"] = {"snapshot_path": str(tail_path), "lines": len(lines)}

    checkpoint_infos = [
        info for name, info in metadata["files"].items()
        if name.endswith(".pt") and info and info.get("stable")
    ]
    if not checkpoint_infos:
        raise SystemExit("No stable checkpoint copied")
    resume = max(checkpoint_infos, key=lambda item: item["mtime_ns"])
    metadata["recommended_resume_checkpoint"] = resume["snapshot_path"]

    meta_path = dst / "snapshot-metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "snapshot_dir": str(dst),
        "recommended_resume_checkpoint": metadata["recommended_resume_checkpoint"],
        "last_training": metadata["last_training"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
