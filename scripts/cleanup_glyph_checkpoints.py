#!/usr/bin/env python3
"""Conservatively prune redundant Glyph checkpoints.

The script only unlinks .pt files under checkpoints/ that are not on the
explicit keep list. It defaults to a dry run and refuses to apply while a
training process is active.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS = ROOT / "checkpoints"

KEEP = {
    "checkpoints/final.pt",
    "checkpoints/public-demo.pt",
    "checkpoints/sft-v0/glyph-27m-sft-v0-final.pt",
    "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
    "checkpoints/glyph-100m-v2_3_1-50k/latest.pt",
    "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt",
    "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt",
    "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-best.pt",
    "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_3-fixedmask-rocm-final-step_000586.pt",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def active_training_processes() -> list[str]:
    found = []
    own_pid = os.getpid()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == own_pid:
            continue
        try:
            cmdline = (proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if "train.py" in cmdline or "finetune.py" in cmdline:
            found.append(f"{proc.name}: {cmdline.strip()}")
    return found


def inventory() -> tuple[list[Path], list[Path]]:
    all_pt = sorted(p for p in CHECKPOINTS.rglob("*.pt") if p.is_file())
    keep_paths = [ROOT / p for p in sorted(KEEP)]
    missing = [p for p in keep_paths if not p.is_file()]
    if missing:
        raise SystemExit("Refusing cleanup; required keep files are missing:\n" + "\n".join(map(str, missing)))
    delete = [p for p in all_pt if rel(p) not in KEEP]
    return keep_paths, delete


def summarize(paths: list[Path]) -> dict[str, dict[str, int]]:
    grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for path in paths:
        key = rel(path.parent)
        grouped[key]["files"] += 1
        grouped[key]["bytes"] += path.stat().st_size
    return dict(sorted(grouped.items()))


def remove_empty_dirs() -> list[str]:
    removed = []
    dirs = sorted((p for p in CHECKPOINTS.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
    for path in dirs:
        try:
            path.rmdir()
            removed.append(rel(path))
        except OSError:
            pass
    return removed


def write_report(payload: dict) -> None:
    json_path = ROOT / "reports/glyph_checkpoint_cleanup_20260704.json"
    md_path = ROOT / "reports/glyph_checkpoint_cleanup_20260704.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph checkpoint cleanup - 2026-07-04",
        "",
        "## Result",
        "",
        f"- mode: `{payload['mode']}`",
        f"- checkpoint files before: `{payload['checkpoint_files_before']}`",
        f"- checkpoint files kept: `{payload['checkpoint_files_kept']}`",
        f"- checkpoint files removed: `{payload['checkpoint_files_removed']}`",
        f"- bytes selected for removal: `{human(payload['bytes_removed'])}`",
        f"- checkpoint directory after: `{human(payload['checkpoint_dir_bytes_after'])}`",
        f"- repository after: `{human(payload['repo_bytes_after'])}`",
        f"- filesystem free after: `{human(payload['filesystem_free_bytes_after'])}`",
        "",
        "## Kept checkpoints",
        "",
    ]
    lines.extend(f"- `{item['path']}` ({human(item['bytes'])})" for item in payload["kept"])
    lines += ["", "## Removed by directory", ""]
    for directory, stats in payload["removed_by_directory"].items():
        lines.append(f"- `{directory}`: {stats['files']} files, {human(stats['bytes'])}")
    lines += [
        "",
        "## Scope",
        "",
        "- Only redundant `.pt` files under `checkpoints/` were removed.",
        "- Datasets, tokenizer, source code, logs, evals, reports and model metadata were not removed.",
        "- Empty checkpoint directories were removed after their files were pruned.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def allocated_bytes(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        try:
            total += item.stat().st_blocks * 512
        except FileNotFoundError:
            pass
    return total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually unlink redundant checkpoint files")
    args = parser.parse_args()

    keep, delete = inventory()
    bytes_to_remove = sum(p.stat().st_size for p in delete)
    preview = {
        "mode": "apply" if args.apply else "dry-run",
        "keep_files": len(keep),
        "delete_files": len(delete),
        "bytes_to_remove": bytes_to_remove,
        "human_to_remove": human(bytes_to_remove),
        "delete_by_directory": summarize(delete),
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    active = active_training_processes()
    if active:
        raise SystemExit("Refusing cleanup while training is active:\n" + "\n".join(active))

    removed = []
    for path in delete:
        size = path.stat().st_size
        path.unlink()
        removed.append({"path": rel(path), "bytes": size})
    removed_dirs = remove_empty_dirs()
    statvfs = os.statvfs(ROOT)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "applied",
        "checkpoint_files_before": len(keep) + len(delete),
        "checkpoint_files_kept": len(keep),
        "checkpoint_files_removed": len(removed),
        "bytes_removed": sum(item["bytes"] for item in removed),
        "kept": [{"path": rel(path), "bytes": path.stat().st_size} for path in keep],
        "removed": removed,
        "removed_by_directory": summarize([ROOT / item["path"] for item in removed if (ROOT / item["path"]).exists()]),
        "removed_by_directory_precomputed": preview["delete_by_directory"],
        "empty_directories_removed": removed_dirs,
        "checkpoint_dir_bytes_after": allocated_bytes(CHECKPOINTS),
        "repo_bytes_after": allocated_bytes(ROOT),
        "filesystem_free_bytes_after": statvfs.f_bavail * statvfs.f_frsize,
    }
    # The files no longer exist, so retain the precomputed directory summary.
    payload["removed_by_directory"] = preview["delete_by_directory"]
    write_report(payload)
    print(json.dumps({"report": "reports/glyph_checkpoint_cleanup_20260704.json", "removed": len(removed)}, indent=2))


if __name__ == "__main__":
    main()
