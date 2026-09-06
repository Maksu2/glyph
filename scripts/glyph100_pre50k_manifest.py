#!/usr/bin/env python3
"""Write a pre-50k manifest for the Glyph-100M diagnostic run."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "backups" / "glyph100_v2_3_1_pre50k_manifest"
EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"

CHECKPOINTS = {
    "best_practical_checkpoint_before_50k": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt",
    "latest_checkpoint_before_50k": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/latest.pt",
    "step_45k_checkpoint": ROOT / "checkpoints/glyph-100m-v2_3_1-45k/step_0045000.pt",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_info(path: Path) -> dict[str, object]:
    info: dict[str, object] = {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }
    if not path.exists():
        return info
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    for key in (
        "variant",
        "step",
        "current_step",
        "dataset_name",
        "tokenizer_sha256",
        "tokenizer_path",
        "batch_size",
        "gradient_accumulation_steps",
        "effective_tokens_per_step",
        "context_length",
    ):
        info[key] = checkpoint.get(key)
    info["optimizer_state_present"] = isinstance(checkpoint.get("optimizer"), dict)
    info["scheduler_state_present"] = isinstance(checkpoint.get("scheduler_state"), dict)
    info["scheduler_state"] = checkpoint.get("scheduler_state")
    return info


def build_manifest() -> dict[str, object]:
    tokenizer_path = ROOT / "data/processed/tokenizer.model"
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision": "50k is diagnostic only; 44k remains best before experiment",
        "dataset": "glyph100_v2_3_1",
        "tokenizer_path": str(tokenizer_path.relative_to(ROOT)),
        "expected_tokenizer_sha256": EXPECTED_TOKENIZER_SHA,
        "actual_tokenizer_sha256": sha256(tokenizer_path),
        "start_checkpoint": str((ROOT / "checkpoints/glyph-100m-v2_3_1-45k/latest.pt").relative_to(ROOT)),
        "target_step": 50000,
        "stage_name": "v2_3_1_diagnostic_45k_to_50k",
        "output_checkpoint_dir": "checkpoints/glyph-100m-v2_3_1-50k",
        "output_log_dir": "logs/glyph-100m-v2_3_1-50k",
        "checkpoints": {name: checkpoint_info(path) for name, path in CHECKPOINTS.items()},
    }
    return manifest


def write_markdown(manifest: dict[str, object]) -> str:
    checkpoints = manifest["checkpoints"]
    lines = [
        "# Glyph-100M v2.3.1 pre-50k manifest",
        "",
        f"- created_at_utc: `{manifest['created_at_utc']}`",
        f"- decision: `{manifest['decision']}`",
        f"- dataset: `{manifest['dataset']}`",
        f"- tokenizer: `{manifest['tokenizer_path']}`",
        f"- tokenizer SHA expected: `{manifest['expected_tokenizer_sha256']}`",
        f"- tokenizer SHA actual: `{manifest['actual_tokenizer_sha256']}`",
        f"- start checkpoint: `{manifest['start_checkpoint']}`",
        f"- target step: `{manifest['target_step']}`",
        f"- output checkpoint dir: `{manifest['output_checkpoint_dir']}`",
        f"- output log dir: `{manifest['output_log_dir']}`",
        "",
        "## Checkpoints",
        "",
        "| role | path | exists | step | variant | dataset | batch/accum | optimizer | scheduler | size |",
        "|---|---|---:|---:|---|---|---|---:|---:|---:|",
    ]
    for role, info in checkpoints.items():
        lines.append(
            "| "
            + " | ".join(
                [
                    role,
                    f"`{info.get('path')}`",
                    str(info.get("exists")),
                    str(info.get("current_step")),
                    str(info.get("variant")),
                    str(info.get("dataset_name")),
                    f"{info.get('batch_size')}/{info.get('gradient_accumulation_steps')}",
                    str(info.get("optimizer_state_present")),
                    str(info.get("scheduler_state_present")),
                    str(info.get("size_bytes")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- 44k remains the best practical checkpoint before this diagnostic run.",
            "- 45k is the latest healthy checkpoint and the resume source for the 50k diagnostic run.",
            "- The 50k checkpoint must not become the best checkpoint without a separate eval.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT_DIR / "manifest.md").write_text(write_markdown(manifest), encoding="utf-8")
    print(f"wrote {OUT_DIR.relative_to(ROOT)}/manifest.md")
    print(f"wrote {OUT_DIR.relative_to(ROOT)}/manifest.json")


if __name__ == "__main__":
    main()
