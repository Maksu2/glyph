#!/usr/bin/env python3
"""Run a private, short Glyph-100M CUDA compatibility benchmark on Kaggle."""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "glyph100-v03-p100-fp32-smoke-001"
EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
INPUT_ARCHIVE = "glyph100-kaggle-input.tar.gz"
WORK_ROOT = Path("/tmp/glyph-kaggle-smoke")
OUTPUT_ROOT = Path("/kaggle/working") / RUN_ID
PYTORCH_VERSION = "2.10.0"
PYTORCH_INDEX = "https://download.pytorch.org/whl/cu126"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def ensure_import(module: str, package: str) -> None:
    try:
        importlib.import_module(module)
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "--quiet", package])


def install_pascal_compatible_pytorch() -> None:
    """Replace Kaggle's cu128 wheel, which omits P100's sm_60 kernels."""
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--quiet",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "--force-reinstall",
            f"torch=={PYTORCH_VERSION}",
            "--index-url",
            PYTORCH_INDEX,
        ]
    )


def locate_payload() -> tuple[Path, bool]:
    matches = list(Path("/kaggle/input").glob(f"**/{INPUT_ARCHIVE}"))
    if len(matches) == 1:
        extract_tar_safely(matches[0], WORK_ROOT)
        return WORK_ROOT, True
    manifests = list(Path("/kaggle/input").glob("**/bundle-manifest.json"))
    if len(manifests) == 1:
        return manifests[0].parent, False
    raise RuntimeError(
        f"Could not locate a unique Glyph payload: archives={matches}, manifests={manifests}"
    )


def extract_tar_safely(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as handle:
        members = handle.getmembers()
        for member in members:
            target = (destination / member.name).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError(f"Unsafe archive member: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"Links are not allowed in the input archive: {member.name}")
        handle.extractall(destination, members=members)


def expected_member_hashes(manifest: dict) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for archive in manifest.get("archives", []):
        for member in archive.get("members", []):
            hashes[str(member["path"])] = str(member["sha256"])
    return hashes


def verify_payload(root: Path) -> dict:
    manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
    hashes = expected_member_hashes(manifest)
    required = [
        "config.py",
        "finetune.py",
        "model/transformer.py",
        "scripts/sft_utils.py",
        "scripts/colab_bundle_utils.py",
        "scripts/colab_preflight.py",
        "scripts/colab_run_sft.py",
        "checkpoints/glyph-100m-base44k.pt",
        "data/processed/tokenizer.model",
        "data/sft/glyph100_sft_smoke_v0_3.jsonl",
        "data/sft/processed/glyph100_sft_smoke_v0_3_train.jsonl",
        "data/sft/processed/glyph100_sft_smoke_v0_3_val.jsonl",
    ]
    checked = []
    for relative in required:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        expected = hashes.get(relative)
        if not expected:
            raise RuntimeError(f"No manifest hash for {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"SHA256 mismatch for {relative}: {actual} != {expected}")
        checked.append({"path": relative, "size": path.stat().st_size, "sha256": actual})
    return {"bundle_version": manifest.get("bundle_version"), "checked": checked}


def gpu_report() -> dict:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Kaggle job did not receive a CUDA GPU")
    props = torch.cuda.get_device_properties(0)
    free_vram, total_vram = torch.cuda.mem_get_info(0)
    return {
        "name": props.name,
        "compute_capability": f"{props.major}.{props.minor}",
        "total_vram_bytes": int(total_vram),
        "free_vram_bytes": int(free_vram),
        "pytorch": torch.__version__,
        "cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
    }


def load_metrics(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def export_model_only(run_root: Path) -> dict:
    import torch

    summary_path = run_root / "reports" / "training_summary.json"
    training_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    latest = Path(str(training_summary["latest_checkpoint"]))
    state = torch.load(latest, map_location="cpu", weights_only=False)
    required = ("model", "optimizer", "scheduler", "model_config", "current_step")
    missing = [key for key in required if key not in state]
    if missing:
        raise RuntimeError(f"Saved checkpoint is incomplete: {missing}")
    model_only = {
        key: value
        for key, value in state.items()
        if key not in {"optimizer", "scheduler", "scaler", "rng_state", "torch_rng_state", "cuda_rng_state"}
    }
    model_only.update(
        {
            "format": "glyph-kaggle-cuda-smoke-model-only-v1",
            "source_checkpoint_sha256": sha256_file(latest),
            "optimizer_checkpoint_validated": True,
            "diagnostic_only": True,
        }
    )
    target = OUTPUT_ROOT / "glyph100-v03-p100-smoke-model-only.pt"
    temporary = target.with_suffix(".pt.tmp")
    torch.save(model_only, temporary)
    reloaded = torch.load(temporary, map_location="cpu", weights_only=False)
    if reloaded.get("current_step") != 25 or not reloaded.get("model"):
        raise RuntimeError("Model-only round-trip validation failed")
    os.replace(temporary, target)
    return {
        "full_checkpoint_step": int(state["current_step"]),
        "full_checkpoint_size": latest.stat().st_size,
        "full_checkpoint_sha256": sha256_file(latest),
        "model_only_path": str(target),
        "model_only_size": target.stat().st_size,
        "model_only_sha256": sha256_file(target),
        "optimizer_present_before_export": bool(state.get("optimizer")),
        "scheduler_present_before_export": bool(state.get("scheduler")),
    }


def main() -> None:
    started = time.perf_counter()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=False)
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi:
        run([nvidia_smi])
    else:
        print("nvidia-smi is not present; CUDA validation will use PyTorch", flush=True)
    install_pascal_compatible_pytorch()
    ensure_import("sentencepiece", "sentencepiece>=0.2,<1")
    ensure_import("psutil", "psutil>=5.9,<8")
    payload_root, temporary_payload = locate_payload()
    payload_validation = verify_payload(payload_root)
    gpu = gpu_report()

    checkpoint = payload_root / "checkpoints/glyph-100m-base44k.pt"
    tokenizer = payload_root / "data/processed/tokenizer.model"
    dataset = payload_root / "data/sft/glyph100_sft_smoke_v0_3.jsonl"
    train_jsonl = payload_root / "data/sft/processed/glyph100_sft_smoke_v0_3_train.jsonl"
    val_jsonl = payload_root / "data/sft/processed/glyph100_sft_smoke_v0_3_val.jsonl"
    reports_dir = OUTPUT_ROOT / "preflight-reports"

    run(
        [
            sys.executable,
            str(payload_root / "scripts/colab_preflight.py"),
            "--run-id",
            RUN_ID,
            "--checkpoint",
            str(checkpoint),
            "--tokenizer",
            str(tokenizer),
            "--dataset",
            str(dataset),
            "--reports-dir",
            str(reports_dir),
            "--expected-step",
            "44000",
            "--expected-variant",
            "glyph-100m",
            "--expected-context",
            "512",
            "--expected-dataset",
            "glyph100_v2_3_1",
            "--expected-tokenizer-sha",
            EXPECTED_TOKENIZER_SHA,
            "--minimum-free-vram-gb",
            "10",
            "--precision",
            "fp32",
        ],
        cwd=payload_root,
    )

    run_root = OUTPUT_ROOT / "training"
    run(
        [
            sys.executable,
            str(payload_root / "scripts/colab_run_sft.py"),
            "--run-id",
            RUN_ID,
            "--base-checkpoint",
            str(checkpoint),
            "--train-jsonl",
            str(train_jsonl),
            "--val-jsonl",
            str(val_jsonl),
            "--tokenizer",
            str(tokenizer),
            "--output-dir",
            str(run_root),
            "--max-steps",
            "25",
            "--batch-size",
            "1",
            "--gradient-accumulation-steps",
            "4",
            "--learning-rate",
            "1e-5",
            "--min-lr",
            "1e-6",
            "--weight-decay",
            "0",
            "--grad-clip",
            "0.5",
            "--eval-interval",
            "25",
            "--eval-batches",
            "8",
            "--checkpoint-interval",
            "0",
            "--log-interval",
            "1",
            "--precision",
            "fp32",
            "--no-save-best-on-val",
            "--seed",
            "2026",
            "--expected-base-step",
            "44000",
            "--expected-variant",
            "glyph-100m",
            "--expected-tokenizer-sha",
            EXPECTED_TOKENIZER_SHA,
            "--dataset-name",
            "glyph100_sft_smoke_v0_3_kaggle_cuda_smoke",
            "--confirm-training",
        ],
        cwd=payload_root,
    )

    checkpoint_validation = export_model_only(run_root)
    metrics = load_metrics(run_root / "logs/metrics.jsonl")
    training_summary = json.loads((run_root / "reports/training_summary.json").read_text(encoding="utf-8"))
    duration = float(training_summary["duration_seconds"])
    supervised = sum(int(item.get("supervised_tokens", 0)) for item in metrics if item.get("event") != "eval")
    summary = {
        "status": "PASS",
        "run_id": RUN_ID,
        "started_at_utc": training_summary["started_at_utc"],
        "finished_at_utc": utc_now(),
        "gpu": gpu,
        "payload_validation": payload_validation,
        "training": training_summary,
        "checkpoint_validation": checkpoint_validation,
        "metrics_logged": len(metrics),
        "supervised_tokens_logged": supervised,
        "supervised_tokens_per_second": supervised / max(duration, 1e-9),
        "wall_seconds_with_preflight_and_export": time.perf_counter() - started,
        "purpose": "CUDA/P100 compatibility and throughput smoke only; not a quality training run",
        "full_v0_3_rerun_was_intentionally_not_performed": True,
    }
    reports = OUTPUT_ROOT / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "kaggle_cuda_smoke_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (reports / "kaggle_cuda_smoke_summary.md").write_text(
        "\n".join(
            [
                "# Glyph-100M Kaggle CUDA smoke",
                "",
                "**Status: PASS**",
                "",
                f"- GPU: `{gpu['name']}`",
                f"- PyTorch/CUDA: `{gpu['pytorch']}` / `{gpu['cuda']}`",
                f"- Steps: `{training_summary['start_step']} -> {training_summary['end_step']}`",
                f"- Training duration: `{duration:.2f} s`",
                f"- Final train loss: `{training_summary['final_train_loss']}`",
                f"- Final val loss: `{training_summary['final_val_loss']}`",
                f"- Supervised tokens/s: `{summary['supervised_tokens_per_second']:.2f}`",
                f"- Peak allocated VRAM is recorded in `{run_root / 'logs/metrics.jsonl'}`.",
                "- Full optimizer checkpoint was reloaded successfully before model-only export.",
                "- This was a compatibility benchmark, not a replacement SFT v0.3 quality run.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # Kaggle persists /kaggle/working. Retain the compact model-only result and reports,
    # not the temporary optimizer checkpoint that was already round-trip validated.
    shutil.rmtree(run_root / "checkpoints")
    if temporary_payload:
        shutil.rmtree(WORK_ROOT)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
