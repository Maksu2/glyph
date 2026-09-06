#!/usr/bin/env python3
"""Move inactive Glyph artifacts from the system disk to the 4 TB HDD.

The default mode is a dry run. With --apply, files are copied with rsync and
removed from the source only after a successful transfer. Absolute symlinks
preserve host-side paths for historical tools and documentation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = Path("/mnt/data/mac/GlyphArchive/glyph-cold-20260704")
REPORT_JSON = ROOT / "reports/glyph_cold_storage_migration_20260704.json"
REPORT_MD = ROOT / "reports/glyph_cold_storage_migration_20260704.md"

ACTIVE_PROCESSED = {
    "tokenizer.model",
    "tokenizer.vocab",
    "glyph100_v2_3_1_train.bin",
    "glyph100_v2_3_1_val.bin",
    "glyph100_v2_3_1_metadata.json",
}

ACTIVE_CHECKPOINTS = {
    "checkpoints/public-demo.pt",
    "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
    "checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_2-fixedmask-rocm-best.pt",
}

WHOLE_DIRECTORIES = (
    "data/raw",
    "models/gemma4",
    ".cache/llama-rocm-gfx1012",
)

EXTRA_FILES = (
    "reports/glyph100_smoke_checkpoint.pt",
)


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
        if "train.py" in cmdline or "finetune.py" in cmdline or "dataset_v2" in cmdline:
            found.append(f"{proc.name}: {cmdline.strip()}")
    return found


def collect_files() -> tuple[list[Path], list[Path]]:
    files: set[Path] = set()
    whole_dirs: list[Path] = []

    for raw in WHOLE_DIRECTORIES:
        path = ROOT / raw
        if path.is_symlink():
            continue
        if path.is_dir():
            whole_dirs.append(path)
            files.update(p for p in path.rglob("*") if p.is_file() and not p.is_symlink())

    processed = ROOT / "data/processed"
    files.update(
        p
        for p in processed.iterdir()
        if p.is_file() and not p.is_symlink() and p.name not in ACTIVE_PROCESSED
    )

    checkpoints = ROOT / "checkpoints"
    files.update(
        p
        for p in checkpoints.rglob("*.pt")
        if p.is_file() and not p.is_symlink() and rel(p) not in ACTIVE_CHECKPOINTS
    )

    for raw in EXTRA_FILES:
        path = ROOT / raw
        if path.is_file() and not path.is_symlink():
            files.add(path)

    return sorted(files), whole_dirs


def ensure_archive() -> None:
    mount = Path("/mnt/data")
    if not mount.is_mount():
        raise SystemExit("/mnt/data is not mounted; refusing migration")
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)


def rsync_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "rsync",
            "-a",
            "--fsync",
            "--remove-source-files",
            "--partial-dir=.rsync-partial",
            str(source),
            str(destination),
        ],
        check=True,
    )


def rsync_directory(source: Path, destination: Path) -> bool:
    destination.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "rsync",
            "-a",
            "--fsync",
            "--remove-source-files",
            "--partial-dir=.rsync-partial",
            f"{source}/",
            f"{destination}/",
        ],
        check=False,
    )
    if result.returncode == 0:
        return True
    remaining = [p for p in source.rglob("*") if p.is_file()]
    if result.returncode == 23 and remaining and all(
        (destination / p.relative_to(source)).is_file()
        and (destination / p.relative_to(source)).stat().st_size == p.stat().st_size
        for p in remaining
    ):
        return False
    raise subprocess.CalledProcessError(result.returncode, result.args)


def replace_file_with_symlink(source: Path, destination: Path, expected_size: int) -> None:
    if source.exists() or source.is_symlink():
        raise RuntimeError(f"Source still exists after rsync: {source}")
    if not destination.is_file() or destination.stat().st_size != expected_size:
        raise RuntimeError(f"Destination verification failed: {destination}")
    source.parent.mkdir(parents=True, exist_ok=True)
    source.symlink_to(destination)


def replace_whole_directory_with_symlink(source: Path) -> None:
    for directory in sorted((p for p in source.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    source.rmdir()
    source.symlink_to(ARCHIVE_ROOT / rel(source), target_is_directory=True)


def write_report(payload: dict) -> None:
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Glyph cold-storage migration - 2026-07-04",
        "",
        "## Result",
        "",
        f"- status: `{payload['status']}`",
        f"- archive: `{payload['archive_root']}`",
        f"- files migrated: `{payload['files_migrated']}`",
        f"- data migrated: `{human(payload['bytes_migrated'])}`",
        f"- system repository after: `{payload['repo_size_after']}`",
        f"- system filesystem free after: `{payload['system_free_after']}`",
        f"- HDD free after: `{payload['hdd_free_after']}`",
        "",
        "## Kept on the system disk",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["active_local_files"])
    lines += [
        "",
        "## Migrated groups",
        "",
    ]
    for group, stats in payload["groups"].items():
        lines.append(f"- `{group}`: {stats['files']} files, {human(stats['bytes'])}")
    lines += [
        "",
        "## Compatibility",
        "",
        "- Original host paths were replaced with absolute symlinks to the HDD archive.",
        "- Current training inputs, tokenizer and active checkpoints remain physically on the system disk.",
        "- Public inference remains on the local `public-demo.pt` checkpoint.",
        "- Docker jobs that need archived paths may require an explicit `/mnt/data` mount because absolute host symlinks are outside the project bind mount.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize_report_from_archive() -> None:
    ensure_archive()
    manifest = []
    for destination in sorted(p for p in ARCHIVE_ROOT.rglob("*") if p.is_file() and not p.is_symlink()):
        relative = destination.relative_to(ARCHIVE_ROOT).as_posix()
        manifest.append({"path": relative, "archive_path": str(destination), "bytes": destination.stat().st_size})
    partial_source_duplicates = []
    for raw in WHOLE_DIRECTORIES:
        source = ROOT / raw
        if source.is_dir() and not source.is_symlink():
            for path in sorted(p for p in source.rglob("*") if p.is_file()):
                destination = ARCHIVE_ROOT / rel(path)
                if destination.is_file() and destination.stat().st_size == path.stat().st_size:
                    partial_source_duplicates.append({
                        "path": rel(path),
                        "bytes": path.stat().st_size,
                        "reason": "source file owned by another user; verified archive copy exists",
                    })
    system_usage = shutil.disk_usage(ROOT)
    hdd_usage = shutil.disk_usage(ARCHIVE_ROOT)
    repo_size = subprocess.check_output(["du", "-sh", str(ROOT)], text=True).split()[0]
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "complete",
        "archive_root": str(ARCHIVE_ROOT),
        "files_migrated": len(manifest),
        "bytes_migrated": sum(item["bytes"] for item in manifest),
        "groups": group_summary_from_manifest(manifest),
        "manifest": manifest,
        "directory_symlinks": [raw for raw in WHOLE_DIRECTORIES if (ROOT / raw).is_symlink()],
        "partial_source_duplicates": partial_source_duplicates,
        "active_local_files": sorted(ACTIVE_PROCESSED | ACTIVE_CHECKPOINTS),
        "repo_size_after": repo_size,
        "system_free_after": human(system_usage.free),
        "hdd_free_after": human(hdd_usage.free),
    }
    write_report(payload)
    print(json.dumps({
        "status": payload["status"],
        "files_migrated": payload["files_migrated"],
        "bytes_migrated": payload["bytes_migrated"],
        "partial_source_duplicates": len(partial_source_duplicates),
        "report": rel(REPORT_JSON),
    }, indent=2))


def group_summary(files: list[Path]) -> dict[str, dict[str, int]]:
    groups: dict[str, dict[str, int]] = {}
    for path in files:
        parts = Path(rel(path)).parts
        key = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
        item = groups.setdefault(key, {"files": 0, "bytes": 0})
        item["files"] += 1
        item["bytes"] += path.stat().st_size
    return dict(sorted(groups.items()))


def group_summary_from_manifest(items: list[dict]) -> dict[str, dict[str, int]]:
    groups: dict[str, dict[str, int]] = {}
    for entry in items:
        parts = Path(entry["path"]).parts
        key = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
        item = groups.setdefault(key, {"files": 0, "bytes": 0})
        item["files"] += 1
        item["bytes"] += entry["bytes"]
    return dict(sorted(groups.items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--finalize-report", action="store_true")
    args = parser.parse_args()

    if args.finalize_report:
        finalize_report_from_archive()
        return

    files, whole_dirs = collect_files()
    total = sum(path.stat().st_size for path in files)
    groups = group_summary(files)
    print(json.dumps({
        "mode": "apply" if args.apply else "dry-run",
        "archive_root": str(ARCHIVE_ROOT),
        "files": len(files),
        "bytes": total,
        "human": human(total),
        "groups": groups,
        "whole_directories": [rel(path) for path in whole_dirs],
    }, ensure_ascii=False, indent=2))
    if not args.apply:
        return

    active = active_training_processes()
    if active:
        raise SystemExit("Refusing migration while training/data build is active:\n" + "\n".join(active))
    ensure_archive()
    free_before = shutil.disk_usage(ARCHIVE_ROOT).free
    if free_before < total + 10 * 1024**3:
        raise SystemExit(f"Insufficient HDD space: need {human(total + 10 * 1024**3)}, have {human(free_before)}")

    manifest = []
    whole_source_files = {
        source
        for source in files
        if any(source.is_relative_to(directory) for directory in whole_dirs)
    }
    individual_files = [source for source in files if source not in whole_source_files]

    directory_symlinks = []
    partial_source_duplicates = []
    for index, directory in enumerate(whole_dirs, 1):
        destination_dir = ARCHIVE_ROOT / rel(directory)
        print(f"[directory {index}/{len(whole_dirs)}] {rel(directory)}", flush=True)
        fully_removed = rsync_directory(directory, destination_dir)
        if fully_removed:
            replace_whole_directory_with_symlink(directory)
            directory_symlinks.append(rel(directory))
        else:
            partial_source_duplicates.extend(
                {
                    "path": rel(path),
                    "bytes": path.stat().st_size,
                    "reason": "source file owned by another user; verified archive copy exists",
                }
                for path in sorted(p for p in directory.rglob("*") if p.is_file())
            )
        for destination in sorted(p for p in destination_dir.rglob("*") if p.is_file()):
            original_rel = (Path(rel(directory)) / destination.relative_to(destination_dir)).as_posix()
            manifest.append({"path": original_rel, "archive_path": str(destination), "bytes": destination.stat().st_size})

    for index, source in enumerate(individual_files, 1):
        size = source.stat().st_size
        destination = ARCHIVE_ROOT / rel(source)
        if destination.exists():
            raise SystemExit(f"Archive destination already exists: {destination}")
        print(f"[file {index}/{len(individual_files)}] {rel(source)} ({human(size)})", flush=True)
        rsync_file(source, destination)
        replace_file_with_symlink(source, destination, size)
        manifest.append({"path": rel(source), "archive_path": str(destination), "bytes": size})

    system_usage = shutil.disk_usage(ROOT)
    hdd_usage = shutil.disk_usage(ARCHIVE_ROOT)
    repo_size = subprocess.check_output(["du", "-sh", str(ROOT)], text=True).split()[0]
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "complete",
        "archive_root": str(ARCHIVE_ROOT),
        "files_migrated": len(manifest),
        "bytes_migrated": sum(item["bytes"] for item in manifest),
        "groups": group_summary_from_manifest(manifest),
        "manifest": manifest,
        "directory_symlinks": directory_symlinks,
        "partial_source_duplicates": partial_source_duplicates,
        "active_local_files": sorted(ACTIVE_PROCESSED | ACTIVE_CHECKPOINTS),
        "repo_size_after": repo_size,
        "system_free_after": human(system_usage.free),
        "hdd_free_after": human(hdd_usage.free),
    }
    write_report(payload)
    print(json.dumps({"status": "complete", "report": rel(REPORT_JSON)}, indent=2))


if __name__ == "__main__":
    main()
