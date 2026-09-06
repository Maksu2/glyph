#!/usr/bin/env python3
"""Build the private Kaggle input bundle for Glyph-100M v2.4.2 pretraining."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parent.parent
EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
ARCHIVE_NAME = "glyph100-v242-pretrain-input.tar.gz"
REQUIRED = (
    "config.py",
    "train.py",
    "model/__init__.py",
    "model/transformer.py",
    "data/processed/tokenizer.model",
    "data/processed/glyph100_v2_4_2_train.bin",
    "data/processed/glyph100_v2_4_2_val.bin",
    "data/processed/glyph100_v2_4_2_metadata.json",
    "checkpoints/glyph-100m-v2_4_2-5k/step_0005000.pt",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_checkpoint(path: Path) -> dict:
    state = torch.load(path, map_location="cpu", weights_only=False)
    expected = {
        "step": 5000,
        "current_step": 5000,
        "variant": "glyph-100m",
        "dataset_name": "glyph100_dataset_v2_4_2_core",
        "tokenizer_sha256": EXPECTED_TOKENIZER_SHA,
        "batch_size": 4,
        "gradient_accumulation_steps": 8,
        "effective_tokens_per_step": 16384,
        "context_length": 512,
    }
    mismatches = {key: {"expected": value, "actual": state.get(key)} for key, value in expected.items() if state.get(key) != value}
    if mismatches:
        raise RuntimeError(f"checkpoint contract mismatch: {mismatches}")
    if not state.get("optimizer") or not state.get("scheduler_state") or not state.get("data_state"):
        raise RuntimeError("checkpoint lacks optimizer, scheduler, or sampler state")
    return {
        **expected,
        "model_tensors": len(state.get("model", {})),
        "optimizer_state_present": True,
        "scheduler_state_present": True,
        "sampler_state_present": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="kaggle/glyph100-v242-pretrain/input")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output_dir = (ROOT / args.output_dir).resolve()
    archive = output_dir / ARCHIVE_NAME
    manifest_path = output_dir / "bundle-manifest.json"
    sums_path = output_dir / "SHA256SUMS"
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"missing required files: {missing}")
    tokenizer_sha = sha256_file(ROOT / "data/processed/tokenizer.model")
    if tokenizer_sha != EXPECTED_TOKENIZER_SHA:
        raise SystemExit(f"tokenizer SHA mismatch: {tokenizer_sha}")
    checkpoint_contract = validate_checkpoint(ROOT / REQUIRED[-1])

    members = []
    total_size = 0
    for relative in REQUIRED:
        path = ROOT / relative
        size = path.stat().st_size
        total_size += size
        members.append({"path": relative, "size": size, "sha256": sha256_file(path)})
    metadata = json.loads((ROOT / "data/processed/glyph100_v2_4_2_metadata.json").read_text(encoding="utf-8"))
    manifest = {
        "bundle_version": "glyph100-v242-kaggle-pretrain-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Private P100 resume smoke at 5k followed by gated continuation to 10k total",
        "checkpoint_contract": checkpoint_contract,
        "dataset": {
            "name": "glyph100_dataset_v2_4_2_core",
            "metadata_path": "data/processed/glyph100_v2_4_2_metadata.json",
            "train_tokens": metadata.get("train_tokens"),
            "val_tokens": metadata.get("val_tokens"),
            "total_tokens": metadata.get("total_tokens"),
        },
        "members": members,
        "uncompressed_bytes": total_size,
        "excluded": [
            "all SFT checkpoints",
            "v2.3.1 checkpoints",
            "50k diagnostic checkpoint",
            "historical logs and reports",
            "raw document stores",
            "secrets and credentials",
        ],
    }
    print(json.dumps({"output": str(archive), "files": members, "uncompressed_bytes": total_size}, indent=2))
    if args.dry_run:
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path for path in (archive, manifest_path, sums_path) if path.exists()]
    if existing and not args.force:
        raise SystemExit(f"refusing to overwrite existing bundle files without --force: {existing}")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tar = subprocess.Popen(
        ["tar", "-C", str(ROOT), "-cf", "-", *REQUIRED, "-C", str(output_dir), manifest_path.name],
        stdout=subprocess.PIPE,
    )
    assert tar.stdout is not None
    with archive.open("wb") as target:
        pigz = subprocess.Popen(["pigz", "-1", "-c"], stdin=tar.stdout, stdout=target)
        tar.stdout.close()
        pigz_status = pigz.wait()
    tar_status = tar.wait()
    if tar_status or pigz_status:
        archive.unlink(missing_ok=True)
        raise SystemExit(f"archive creation failed: tar={tar_status} pigz={pigz_status}")

    archive_sha = sha256_file(archive)
    sums_path.write_text(f"{archive_sha}  {archive.name}\n", encoding="ascii")
    manifest["archive"] = {"path": archive.name, "size": archive.stat().st_size, "sha256": archive_sha}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["archive"], indent=2))


if __name__ == "__main__":
    main()
