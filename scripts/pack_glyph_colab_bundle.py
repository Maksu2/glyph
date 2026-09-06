#!/usr/bin/env python3
"""Build a minimal, explicit Glyph bundle for an offline Google Colab upload."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from scripts.colab_bundle_utils import (
    atomic_write_json,
    create_tar_zst,
    file_record,
    sha256_file,
    write_sha256sums,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt"
DEFAULT_DATASET = ROOT / "data/sft/glyph100_sft_smoke_v0_3.jsonl"
DEFAULT_TOKENIZER = ROOT / "data/processed/tokenizer.model"
EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"

CODE_PATHS = (
    "config.py",
    "finetune.py",
    "generate.py",
    "requirements-colab.txt",
    "model/__init__.py",
    "model/transformer.py",
    "scripts/sft_utils.py",
    "scripts/colab_bundle_utils.py",
    "scripts/verify_glyph_colab_bundle.py",
    "scripts/colab_preflight.py",
    "scripts/colab_run_sft.py",
    "scripts/colab_export_results.py",
    "config/colab_bundle.example.json",
    "docs/COLAB_MIGRATION.md",
    "colab/Glyph_Colab.ipynb",
    "colab/README.md",
)

OPTIONAL_REPORT_PATHS = (
    "reports/glyph_colab_migration_preparation.md",
    "reports/glyph_colab_migration_preparation.json",
    "reports/glyph100_sft_label_mask_fix_audit.md",
    "reports/glyph100_sft_label_mask_fix_audit.json",
    "reports/glyph100_sft_v0_3_dataset_plan.md",
    "reports/glyph100_sft_v0_3_dataset_plan.json",
    "reports/glyph100_sft_v0_3_next_decision.md",
    "reports/glyph100_sft_v0_3_next_decision.json",
    "reports/glyph100_44k_sft_smoke_v0_3_fixedmask_rocm_report.md",
    "reports/glyph100_44k_sft_smoke_v0_3_fixedmask_rocm_report.json",
    "eval/glyph-100m/sft_smoke_v0_3_fixedmask_before_after.md",
    "eval/glyph-100m/sft_smoke_v0_3_fixedmask_before_after.json",
)

FORBIDDEN_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".cache",
    ".env",
    "credentials",
    "credential",
    "client_secret",
    "secrets",
}


def resolve_input(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def relative_or_bundle_path(path: Path, fallback_prefix: str) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return f"{fallback_prefix}/{path.name}"


def reject_unsafe_path(path: Path) -> None:
    lowered = [part.lower() for part in path.parts]
    if any(any(blocked in part for blocked in FORBIDDEN_PARTS) for part in lowered):
        raise ValueError(f"Refusing sensitive or irrelevant path: {path}")
    if any("token" in part and part != "tokenizer.model" for part in lowered):
        raise ValueError(f"Refusing possible access-token file: {path}")


def load_checkpoint_metadata(path: Path) -> tuple[dict, dict]:
    kwargs = {"map_location": "cpu", "weights_only": False}
    try:
        state = torch.load(path, mmap=True, **kwargs)
    except (TypeError, RuntimeError):
        state = torch.load(path, **kwargs)
    step = int(state.get("current_step", state.get("step", 0)))
    cfg_dict = state.get("model_config") or {}
    metadata = {
        "step": step,
        "variant": state.get("variant"),
        "dataset": state.get("dataset_name", state.get("dataset")),
        "context_length": int(state.get("context_length", cfg_dict.get("context_len", 0))),
        "tokenizer_sha256": state.get("tokenizer_sha256"),
        "model_config": cfg_dict,
        "model_tensors": len(state.get("model") or {}),
        "optimizer_present_in_source": "optimizer" in state,
        "scheduler_present_in_source": "scheduler_state" in state or "scheduler" in state,
    }
    return state, metadata


def validate_base(path: Path, metadata: dict, tokenizer_sha: str) -> None:
    if "50k" in path.as_posix().lower() or "0050000" in path.name:
        raise ValueError("Checkpoint 50k is explicitly forbidden as the Colab base")
    if metadata["step"] != 44_000:
        raise ValueError(f"Expected base step 44000, got {metadata['step']}")
    if metadata["variant"] != "glyph-100m":
        raise ValueError(f"Expected glyph-100m, got {metadata['variant']!r}")
    if metadata["context_length"] != 512:
        raise ValueError(f"Expected context 512, got {metadata['context_length']}")
    if metadata["tokenizer_sha256"] != EXPECTED_TOKENIZER_SHA:
        raise ValueError("Checkpoint tokenizer SHA does not match the approved tokenizer")
    if tokenizer_sha != EXPECTED_TOKENIZER_SHA:
        raise ValueError("Tokenizer file SHA does not match the approved tokenizer")
    expected = ModelConfig(vocab_size=16000, context_len=512, d_model=768, n_heads=12, n_layers=12, ffn_mult=4, dropout=0.1)
    if metadata["model_config"] != expected.__dict__:
        raise ValueError("Base checkpoint model_config is not the approved Glyph-100M config")


def dataset_entries(dataset: Path) -> list[tuple[Path, str]]:
    entries = [(dataset, relative_or_bundle_path(dataset, "data/sft/input"))]
    stem = dataset.stem
    candidates = [
        ROOT / "data/sft" / f"{stem}_report.md",
        ROOT / "data/sft" / f"{stem}_report.json",
    ]
    for split in ("train", "val", "test"):
        candidates.append(ROOT / "data/sft/processed" / f"{stem}_{split}.jsonl")
    for candidate in candidates:
        if candidate.is_file():
            entries.append((candidate, candidate.relative_to(ROOT).as_posix()))
    return entries


def count_jsonl(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL line {line_no} is not an object")
            count += 1
    return count


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def source_records(entries: list[tuple[Path, str]]) -> list[dict]:
    records = []
    for source, arcname in entries:
        reject_unsafe_path(source)
        records.append(file_record(source, arcname))
    return records


def save_stripped_base(state: dict, metadata: dict, destination: Path, source_sha: str) -> None:
    allowed = {
        "variant",
        "step",
        "current_step",
        "loss",
        "model",
        "model_config",
        "dataset_name",
        "dataset_metadata_path",
        "tokenizer_path",
        "tokenizer_sha256",
        "context_length",
        "batch_size",
        "gradient_accumulation_steps",
        "effective_tokens_per_step",
        "checkpoint_metadata",
    }
    payload = {key: value for key, value in state.items() if key in allowed}
    payload.update(
        {
            "bundle_role": "glyph-100m-base44k-for-fresh-sft",
            "source_checkpoint_sha256": source_sha,
            "optimizer_removed_for_bundle": True,
            "scheduler_removed_for_bundle": True,
            "bundle_created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        torch.save(payload, handle)
        handle.flush()
        os.fsync(handle.fileno())
    check = torch.load(destination, map_location="cpu", weights_only=False, mmap=True)
    if int(check.get("current_step", check.get("step", 0))) != metadata["step"]:
        raise IOError("Derived base checkpoint failed reload validation")
    if "optimizer" in check or "scheduler_state" in check:
        raise IOError("Derived base checkpoint unexpectedly contains optimizer/scheduler state")


def print_dry_run(
    base: Path,
    dataset: Path,
    tokenizer: Path,
    code_entries: list[tuple[Path, str]],
    data_entries: list[tuple[Path, str]],
    report_entries: list[tuple[Path, str]],
    metadata: dict,
) -> None:
    model_bytes = sum(
        tensor.numel() * tensor.element_size()
        for tensor in torch.load(base, map_location="cpu", weights_only=False, mmap=True)["model"].values()
    )
    print("Glyph Colab bundle dry-run; no files will be written.\n")
    print(f"Base source: {base} ({base.stat().st_size / 2**30:.2f} GiB)")
    print(f"Derived optimizer-free base estimate: {model_bytes / 2**30:.2f} GiB")
    print(f"Checkpoint metadata: step={metadata['step']} variant={metadata['variant']} context={metadata['context_length']}")
    print(f"Tokenizer: {tokenizer} ({tokenizer.stat().st_size / 2**20:.2f} MiB)")
    print(f"Dataset: {dataset} ({dataset.stat().st_size / 2**20:.2f} MiB, {count_jsonl(dataset):,} examples)")
    for title, entries in (("code", code_entries), ("dataset", data_entries), ("reports", report_entries)):
        print(f"\n[{title}] {len(entries)} file(s), {sum(p.stat().st_size for p, _ in entries) / 2**20:.2f} MiB")
        for path, arcname in entries:
            print(f"  {arcname} <- {path}")
    print("\nExcluded by construction: 50k, old checkpoints, optimizer history, .git, .venv, caches, logs, credentials and unrelated datasets.")


def write_configured_notebook(source: Path, destination: Path, names: dict[str, str]) -> None:
    notebook = json.loads(source.read_text(encoding="utf-8"))
    replacements = {
        "CODE_ARCHIVE = ": f"CODE_ARCHIVE = {names['code']!r}\n",
        "TOKENIZER_ARCHIVE = ": f"TOKENIZER_ARCHIVE = {names['tokenizer']!r}\n",
        "BASE_CHECKPOINT_ARCHIVE = ": f"BASE_CHECKPOINT_ARCHIVE = {names['base']!r}\n",
        "DATASET_ARCHIVE = ": f"DATASET_ARCHIVE = {names['dataset']!r}\n",
        "REPORTS_ARCHIVE = ": f"REPORTS_ARCHIVE = {names.get('reports', '')!r}\n",
    }
    replaced = set()
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        updated = []
        for line in cell.get("source", []):
            replacement = next((value for prefix, value in replacements.items() if line.startswith(prefix)), None)
            if replacement is None:
                updated.append(line)
                continue
            prefix = line.split("=", 1)[0].strip() + " = "
            replaced.add(prefix)
            updated.append(replacement)
        cell["source"] = updated
    expected = set(replacements)
    if replaced != expected:
        raise ValueError(f"Notebook archive configuration fields missing: {sorted(expected - replaced)}")
    destination.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def upload_instructions(names: dict[str, str]) -> str:
    archives = [names[role] for role in ("code", "tokenizer", "base", "dataset")]
    if names.get("reports"):
        archives.append(names["reports"])
    listed = "\n".join(f"- `{name}`" for name in archives)
    return f"""# Upload this Glyph bundle to Google Drive

Create `MyDrive/Glyph/colab/input/`, then upload these files from this folder:

- `manifest.json`
- `SHA256SUMS`
{listed}

Open `Glyph_Colab.ipynb` with Google Colaboratory. Its archive names are already
filled in for this bundle. Select a GPU runtime and run preflight first.

Keep `RUN_TRAINING = False` until training is explicitly approved. Do not upload
the outer convenience ZIP to Drive; extract it first and upload the files above.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an offline Glyph bundle for Google Colab")
    parser.add_argument("--base-checkpoint", default=str(DEFAULT_BASE.relative_to(ROOT)))
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET.relative_to(ROOT)))
    parser.add_argument("--tokenizer", default=str(DEFAULT_TOKENIZER.relative_to(ROOT)))
    parser.add_argument("--output-dir", default="dist/glyph-colab")
    parser.add_argument("--include-reports", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-mode", action="store_true", help="Create a metadata-only structural test bundle")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--timestamp", default=None, help="Override UTC filename timestamp")
    args = parser.parse_args()

    base = resolve_input(args.base_checkpoint)
    dataset = resolve_input(args.dataset)
    tokenizer = resolve_input(args.tokenizer)
    for path in (base, dataset, tokenizer):
        if not path.is_file():
            raise FileNotFoundError(path)
        reject_unsafe_path(path)

    tokenizer_sha = sha256_file(tokenizer)
    state, checkpoint_meta = load_checkpoint_metadata(base)
    validate_base(base, checkpoint_meta, tokenizer_sha)

    code_entries = [(ROOT / rel, rel) for rel in CODE_PATHS]
    missing_code = [str(path) for path, _ in code_entries if not path.is_file()]
    if missing_code:
        raise FileNotFoundError("Missing required code files: " + ", ".join(missing_code))
    data_entries = dataset_entries(dataset)
    report_entries = [
        (ROOT / rel, rel) for rel in OPTIONAL_REPORT_PATHS if args.include_reports and (ROOT / rel).is_file()
    ]
    source_records(code_entries + data_entries + report_entries)

    if args.dry_run:
        print_dry_run(base, dataset, tokenizer, code_entries, data_entries, report_entries, checkpoint_meta)
        return

    output_dir = resolve_input(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    protected = [output_dir / "manifest.json", output_dir / "SHA256SUMS"]
    if not args.force and any(path.exists() for path in protected):
        raise FileExistsError(f"Bundle metadata already exists in {output_dir}; choose another directory or use --force")

    timestamp = args.timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    names = {
        "code": f"glyph-code-{timestamp}.tar.zst",
        "tokenizer": f"glyph-tokenizer-{timestamp}.tar.zst",
        "base": f"glyph-base44k-{timestamp}.tar.zst",
        "dataset": f"glyph-sft-data-{timestamp}.tar.zst",
        "reports": f"glyph-reports-{timestamp}.tar.zst",
    }
    source_checkpoint_sha = sha256_file(base)
    archive_specs: list[tuple[str, Path, list[tuple[Path, str]]]] = []

    with tempfile.TemporaryDirectory(prefix="glyph-colab-pack-") as temp_name:
        temp = Path(temp_name)
        if args.test_mode:
            fixture = temp / "checkpoints/glyph-100m-base44k.metadata.json"
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_text(json.dumps(checkpoint_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            base_entries = [(fixture, "checkpoints/glyph-100m-base44k.metadata.json")]
            checkpoint_payload = "metadata_only_test_fixture"
        else:
            derived = temp / "checkpoints/glyph-100m-base44k.pt"
            save_stripped_base(state, checkpoint_meta, derived, source_checkpoint_sha)
            base_entries = [(derived, "checkpoints/glyph-100m-base44k.pt")]
            checkpoint_payload = "optimizer_free_torch_checkpoint"

        archive_specs.extend(
            [
                ("code", output_dir / names["code"], code_entries),
                ("tokenizer", output_dir / names["tokenizer"], [(tokenizer, "data/processed/tokenizer.model")]),
                ("base", output_dir / names["base"], base_entries),
                ("dataset", output_dir / names["dataset"], data_entries),
            ]
        )
        if report_entries:
            archive_specs.append(("reports", output_dir / names["reports"], report_entries))

        archives = []
        for role, archive_path, entries in archive_specs:
            if archive_path.exists() and not args.force:
                raise FileExistsError(archive_path)
            create_tar_zst(archive_path, entries)
            archives.append(
                {
                    "role": role,
                    **file_record(archive_path, archive_path.name),
                    "members": source_records(entries),
                }
            )

    notebook_copy = output_dir / "Glyph_Colab.ipynb"
    readme_copy = output_dir / "README.md"
    instructions_copy = output_dir / "UPLOAD_INSTRUCTIONS.md"
    for destination in (notebook_copy, readme_copy, instructions_copy):
        if destination.exists() and not args.force:
            raise FileExistsError(destination)
    configured_names = {**names, "reports": names["reports"] if report_entries else ""}
    write_configured_notebook(ROOT / "colab/Glyph_Colab.ipynb", notebook_copy, configured_names)
    readme_copy.write_bytes((ROOT / "colab/README.md").read_bytes())
    instructions_copy.write_text(upload_instructions(configured_names), encoding="utf-8")

    dataset_count = count_jsonl(dataset)
    manifest = {
        "bundle_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "test_mode": bool(args.test_mode),
        "git_commit": current_git_commit(),
        "repo_root_at_build": str(ROOT),
        "archives": archives,
        "external_files": [
            file_record(notebook_copy, notebook_copy.name),
            file_record(readme_copy, readme_copy.name),
            file_record(instructions_copy, instructions_copy.name),
        ],
        "checkpoint": {
            "source_path": relative_or_bundle_path(base, "external/checkpoints"),
            "source_sha256": source_checkpoint_sha,
            "bundle_path": "checkpoints/glyph-100m-base44k.pt" if not args.test_mode else "checkpoints/glyph-100m-base44k.metadata.json",
            "payload": checkpoint_payload,
            **checkpoint_meta,
            "approved_base": True,
            "checkpoint_50k_is_not_base": True,
        },
        "tokenizer": {
            "path": "data/processed/tokenizer.model",
            "sha256": tokenizer_sha,
        },
        "dataset": {
            "source_path": relative_or_bundle_path(dataset, "data/sft/input"),
            "examples": dataset_count,
            "sha256": sha256_file(dataset),
            "archive_role": "dataset",
        },
        "runtime": {
            "python": ">=3.10,<3.14",
            "pytorch": ">=2.1 with CUDA; use the Colab-provided build",
            "default_precision": "fp32",
        },
        "sft_contract": {
            "template": "<|user|>\\n{instruction}\\n<|assistant|>\\n{response}\\n<|end|>\\n",
            "label_mask_boundary": "i < assistant_pos",
            "first_assistant_token_supervised": True,
            "end_token_supervised": True,
            "prompt_supervised": False,
            "padding_ignore_index": -100,
        },
        "commands": {
            "prepare": "python3 scripts/pack_glyph_colab_bundle.py --include-reports",
            "verify": "python3 scripts/verify_glyph_colab_bundle.py --bundle-dir dist/glyph-colab",
            "preflight": "python3 scripts/colab_preflight.py --run-id <run_id>",
        },
        "excluded": [
            "checkpoint 50k",
            "SFT v0.1/v0.2 checkpoints unless explicitly supplied in a future bundle",
            "optimizer and scheduler state from base pretraining",
            "historical checkpoints and logs",
            ".git, virtualenvs and caches",
            "credentials, secrets and access tokens",
            "unrelated datasets",
        ],
    }
    manifest_path = output_dir / "manifest.json"
    atomic_write_json(manifest_path, manifest)
    checksummed = [Path(item["path"]) if Path(item["path"]).is_absolute() else output_dir / item["path"] for item in archives]
    checksummed.extend([notebook_copy, readme_copy, instructions_copy, manifest_path])
    write_sha256sums(output_dir / "SHA256SUMS", checksummed)

    print(f"Glyph Colab bundle prepared in {output_dir}")
    for path in sorted(output_dir.iterdir()):
        if path.is_file():
            print(f"- {path.name}: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
