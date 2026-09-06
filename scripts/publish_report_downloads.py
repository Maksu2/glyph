#!/usr/bin/env python3
"""Copy report/eval artifacts to the local download directory and rebuild index."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_DIR = ROOT / "report-downloads"

SOURCES = (
    ROOT / "reports",
    ROOT / "eval" / "glyph-100m",
    ROOT / "data" / "sft",
    ROOT / "backups" / "glyph100_v2_3_1_pre50k_manifest",
)

EXTRA_FILES = (
    ROOT / "colab" / "Glyph_Colab.ipynb",
    ROOT / "colab" / "README.md",
    ROOT / "docs" / "COLAB_MIGRATION.md",
    ROOT / "config" / "colab_bundle.example.json",
    ROOT / "requirements-colab.txt",
    ROOT / "scripts" / "colab_bundle_utils.py",
    ROOT / "scripts" / "pack_glyph_colab_bundle.py",
    ROOT / "scripts" / "verify_glyph_colab_bundle.py",
    ROOT / "scripts" / "colab_preflight.py",
    ROOT / "scripts" / "colab_run_sft.py",
    ROOT / "scripts" / "colab_export_results.py",
    ROOT / "checkpoints" / "glyph-100m_v2_3_1-best.json",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_report.md",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_stats.json",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_samples_accepted.jsonl",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_samples_rejected.jsonl",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_1_samples_final_random.jsonl",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_report.md",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_stats.json",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_samples_accepted.jsonl",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_samples_rejected.jsonl",
    ROOT / "data" / "reports" / "glyph100_dataset_v2_4_2_samples_final_random.jsonl",
)

SUFFIXES = (".md", ".json", ".jsonl", ".html", ".sql", ".tar.gz", ".zip", ".ipynb", ".py")
JSONL_REPORT_PREFIXES = (
    "glyph100_next_step_20260716",
    "glyph100_dataset_v2_4_1",
    "glyph100_v2_4_1_1k_20260716",
    "glyph100_v2_4_1_5k_eval_20260717",
    "glyph100_dataset_v2_4_2",
)


def should_publish(path: Path) -> bool:
    if path == ROOT / "requirements-colab.txt":
        return True
    if not path.is_file() or path.name == "index.html" or not path.name.endswith(SUFFIXES):
        return False
    if path.name.endswith(".jsonl"):
        return path.name.startswith(JSONL_REPORT_PREFIXES)
    return True


def target_name(path: Path) -> str:
    if path == ROOT / "colab" / "README.md":
        return "glyph_colab_README.md"
    if path == ROOT / "config" / "colab_bundle.example.json":
        return "glyph_colab_bundle_example.json"
    if path == ROOT / "requirements-colab.txt":
        return "glyph_colab_requirements.txt"
    if path.parent.name == "glyph100_v2_3_1_pre50k_manifest" and path.name.startswith("manifest."):
        return f"glyph100_v2_3_1_pre50k_{path.name}"
    return path.name


def publish() -> list[Path]:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for source in SOURCES:
        if not source.exists():
            continue
        for path in sorted(source.rglob("*")):
            if not should_publish(path):
                continue
            target = DOWNLOAD_DIR / target_name(path)
            if target.exists() and target.stat().st_mtime >= path.stat().st_mtime and target.stat().st_size == path.stat().st_size:
                continue
            shutil.copy2(path, target)
            copied.append(target)
    for path in EXTRA_FILES:
        if not should_publish(path):
            continue
        target = DOWNLOAD_DIR / target_name(path)
        if target.exists() and target.stat().st_mtime >= path.stat().st_mtime and target.stat().st_size == path.stat().st_size:
            continue
        shutil.copy2(path, target)
        copied.append(target)
    return copied


def main() -> None:
    copied = publish()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "update_report_downloads.py")], check=True)
    print(f"published {len(copied)} file(s)")
    for path in copied:
        print(f"- {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
