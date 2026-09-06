#!/usr/bin/env python3
"""Gated Glyph-100M v2.4.2 P100 resume smoke and continuation to 10k."""
from __future__ import annotations

import hashlib
import importlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "glyph100-v242-p100-5k-to-10k-001"
INPUT_ARCHIVE = "glyph100-v242-pretrain-input.tar.gz"
EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
EXPECTED_DATASET = "glyph100_dataset_v2_4_2_core"
WORK_ROOT = Path("/tmp/glyph-v242-pretrain")
OUTPUT_ROOT = Path("/kaggle/working") / RUN_ID
PYTORCH_VERSION = "2.10.0"
PYTORCH_INDEX = "https://download.pytorch.org/whl/cu126"
LOG_RE = re.compile(r"step=\s*(?P<step>\d+) \| loss=(?P<loss>[\d.]+) \| lr=(?P<lr>[\deE+.-]+) \| tok/s=(?P<tps>[\d,]+)")
VAL_RE = re.compile(r"eval step=\s*(?P<step>\d+) \| val_loss=(?P<loss>[\d.]+)")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path | None = None, env: dict | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def ensure_import(module: str, package: str) -> None:
    try:
        importlib.import_module(module)
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "--quiet", package])


def install_pascal_compatible_pytorch() -> None:
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


def extract_tar_safely(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    root = destination.resolve()
    with tarfile.open(archive, "r:gz") as handle:
        members = handle.getmembers()
        for member in members:
            target = (destination / member.name).resolve()
            if root != target and root not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name}")
            if member.issym() or member.islnk():
                raise RuntimeError(f"links are not allowed: {member.name}")
        handle.extractall(destination, members=members)


def locate_payload() -> tuple[Path, dict]:
    archives = list(Path("/kaggle/input").glob(f"**/{INPUT_ARCHIVE}"))
    if len(archives) == 1:
        archive = archives[0]
        sums = archive.parent / "SHA256SUMS"
        expected = sums.read_text(encoding="ascii").split()[0]
        actual = sha256_file(archive)
        if actual != expected:
            raise RuntimeError(f"input archive SHA mismatch: {actual} != {expected}")
        extract_tar_safely(archive, WORK_ROOT)
        return WORK_ROOT, {"mode": "archive", "path": str(archive), "sha256": actual}
    if len(archives) > 1:
        raise RuntimeError(f"multiple input archives found: {archives}")

    # Kaggle may unpack uploaded tarballs into a namespaced directory. Select
    # only a manifest whose parent also contains the expected code and checkpoint.
    candidates = []
    for manifest in Path("/kaggle/input").glob("**/bundle-manifest.json"):
        parent = manifest.parent
        if (
            (parent / "config.py").is_file()
            and (parent / "train.py").is_file()
            and (parent / "checkpoints/glyph-100m-v2_4_2-5k/step_0005000.pt").is_file()
        ):
            candidates.append(parent)
    if len(candidates) != 1:
        raise RuntimeError(f"expected one expanded payload root, found {candidates}")
    return candidates[0], {"mode": "kaggle_expanded", "path": str(candidates[0])}


def verify_payload(root: Path) -> dict:
    manifest = json.loads((root / "bundle-manifest.json").read_text(encoding="utf-8"))
    checked = []
    for member in manifest["members"]:
        path = root / member["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = sha256_file(path)
        if actual != member["sha256"]:
            raise RuntimeError(f"member SHA mismatch for {member['path']}")
        checked.append({"path": member["path"], "size": path.stat().st_size, "sha256": actual})
    return {"bundle_version": manifest["bundle_version"], "checked": checked, "manifest": manifest}


def gpu_report() -> dict:
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Kaggle job did not receive a CUDA GPU")
    props = torch.cuda.get_device_properties(0)
    capability = (props.major, props.minor)
    if capability != (6, 0):
        print(f"Warning: requested P100 but received compute capability {capability}", flush=True)
    x = torch.randn(256, 256, device="cuda")
    y = x @ x
    torch.cuda.synchronize()
    if not torch.isfinite(y).all():
        raise RuntimeError("CUDA matmul smoke produced non-finite values")
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


def validate_checkpoint(path: Path, expected_step: int, *, finite_model: bool = True) -> dict:
    import torch

    state = torch.load(path, map_location="cpu", weights_only=False)
    expected = {
        "step": expected_step,
        "current_step": expected_step,
        "variant": "glyph-100m",
        "dataset_name": EXPECTED_DATASET,
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
    if finite_model:
        for name, tensor in state.get("model", {}).items():
            if not torch.isfinite(tensor).all():
                raise RuntimeError(f"non-finite model tensor: {name}")
    return {
        **expected,
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "model_tensors": len(state.get("model", {})),
        "optimizer_state_present": True,
        "scheduler_state_present": True,
        "sampler_state_present": True,
    }


def training_command(
    root: Path,
    resume: Path,
    target_step: int,
    checkpoint_dir: Path,
    log_dir: Path,
    eval_interval: int,
    checkpoint_interval: int,
    finite_check_interval: int,
) -> list[str]:
    return [
        sys.executable,
        str(root / "train.py"),
        "--variant", "glyph-100m",
        "--device", "cuda",
        "--resume", str(resume),
        "--max-steps", str(target_step),
        "--data-path", str(root / "data/processed/glyph100_v2_4_2_train.bin"),
        "--val-data-path", str(root / "data/processed/glyph100_v2_4_2_val.bin"),
        "--tokenizer-path", str(root / "data/processed/tokenizer.model"),
        "--dataset-metadata-path", str(root / "data/processed/glyph100_v2_4_2_metadata.json"),
        "--dataset-name", EXPECTED_DATASET,
        "--checkpoint-dir", str(checkpoint_dir),
        "--log-dir", str(log_dir),
        "--batch-size", "4",
        "--gradient-accumulation-steps", "8",
        "--learning-rate", "2e-4",
        "--min-lr", "2e-5",
        "--warmup-steps", "2000",
        "--weight-decay", "0.1",
        "--grad-clip", "1.0",
        "--train-sampling", "shuffled_blocks",
        "--data-seed", "2026",
        "--eval-seed", "2027",
        "--eval-interval", str(eval_interval),
        "--val-batches", "64",
        "--checkpoint-interval", str(checkpoint_interval),
        "--log-interval", "10",
        "--finite-check-interval", str(finite_check_interval),
        "--optimizer-foreach", "true",
        "--attention-backend", "sdpa",
    ]


def parse_train_log(path: Path) -> dict:
    rows = []
    validation = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        match = LOG_RE.search(line)
        if match:
            rows.append(
                {
                    "step": int(match.group("step")),
                    "loss": float(match.group("loss")),
                    "lr": float(match.group("lr")),
                    "tokens_per_second": int(match.group("tps").replace(",", "")),
                }
            )
        match = VAL_RE.search(line)
        if match:
            validation.append({"step": int(match.group("step")), "val_loss": float(match.group("loss"))})
    bad_terms = [term for term in ("Non-finite", "out of memory", "Traceback", "ROCm", "CUDA error") if term.lower() in text.lower()]
    return {
        "train_rows": rows,
        "validation": validation,
        "bad_terms": bad_terms,
        "average_tokens_per_second": sum(row["tokens_per_second"] for row in rows) / len(rows) if rows else None,
    }


class GpuMonitor:
    def __init__(self, output: Path) -> None:
        self.output = output
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=10)

    def _run(self) -> None:
        fields = "timestamp,name,temperature.gpu,memory.used,memory.total,utilization.gpu,power.draw"
        while not self.stop_event.is_set():
            try:
                result = subprocess.run(
                    ["nvidia-smi", f"--query-gpu={fields}", "--format=csv,noheader,nounits"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                with self.output.open("a", encoding="utf-8") as handle:
                    handle.write(result.stdout.strip() + "\n")
            except Exception as exc:
                print(f"GPU monitor warning: {exc}", flush=True)
            self.stop_event.wait(30)


def write_report(path: Path, payload: dict, title: str) -> None:
    path.with_suffix(".json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# {title}", "", f"**Status: {payload.get('status', 'UNKNOWN')}**", ""]
    for key, value in payload.items():
        if key in {"status", "smoke_log", "full_log"}:
            continue
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    started = time.perf_counter()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=False)
    reports_dir = OUTPUT_ROOT / "reports"
    reports_dir.mkdir(parents=True)
    monitor = GpuMonitor(OUTPUT_ROOT / "gpu_metrics.csv")
    monitor.start()
    status = "FAIL"
    try:
        run(["nvidia-smi"])
        install_pascal_compatible_pytorch()
        ensure_import("sentencepiece", "sentencepiece>=0.2,<1")
        payload_root, input_location = locate_payload()
        payload = verify_payload(payload_root)
        gpu = gpu_report()

        input_checkpoint = payload_root / "checkpoints/glyph-100m-v2_4_2-5k/step_0005000.pt"
        input_contract = validate_checkpoint(input_checkpoint, 5000)
        input_sha_before = sha256_file(input_checkpoint)
        metadata = json.loads((payload_root / "data/processed/glyph100_v2_4_2_metadata.json").read_text(encoding="utf-8"))
        if metadata.get("dataset_id") not in {None, EXPECTED_DATASET} and metadata.get("dataset_name") not in {None, EXPECTED_DATASET}:
            raise RuntimeError(f"unexpected dataset metadata identity: {metadata.get('dataset_id') or metadata.get('dataset_name')}")
        if metadata.get("tokenizer_sha256") != EXPECTED_TOKENIZER_SHA:
            raise RuntimeError("dataset tokenizer SHA mismatch")

        preflight = {
            "status": "PASS",
            "run_id": RUN_ID,
            "input_location": input_location,
            "payload": payload,
            "gpu": gpu,
            "input_checkpoint": input_contract,
            "disk_usage": shutil.disk_usage("/kaggle/working")._asdict(),
            "started_at_utc": utc_now(),
        }
        write_report(reports_dir / "preflight.md", preflight, "Glyph-100M v2.4.2 P100 preflight")

        env = os.environ.copy()
        env.update({"PYTHONUNBUFFERED": "1", "TRAIN_NUM_THREADS": "4", "TRAIN_INTEROP_THREADS": "1"})
        smoke_root = OUTPUT_ROOT / "smoke"
        smoke_checkpoints = smoke_root / "checkpoints"
        smoke_logs = smoke_root / "logs"
        smoke_started = time.perf_counter()
        run(
            training_command(payload_root, input_checkpoint, 5100, smoke_checkpoints, smoke_logs, 50, 100, 10),
            cwd=payload_root,
            env=env,
        )
        smoke_duration = time.perf_counter() - smoke_started
        smoke_checkpoint = smoke_checkpoints / "step_0005100.pt"
        smoke_contract = validate_checkpoint(smoke_checkpoint, 5100)
        smoke_log = parse_train_log(smoke_logs / "train.log")
        smoke_vals = smoke_log["validation"]
        smoke_gate = bool(
            smoke_log["train_rows"]
            and not smoke_log["bad_terms"]
            and smoke_vals
            and math.isfinite(smoke_vals[-1]["val_loss"])
            and smoke_vals[-1]["val_loss"] < 6.0
            and all(math.isfinite(row["loss"]) and 0.0 < row["loss"] < 20.0 for row in smoke_log["train_rows"])
        )
        smoke_report = {
            "status": "PASS" if smoke_gate else "FAIL",
            "run_id": RUN_ID,
            "start_step": 5000,
            "end_step": 5100,
            "duration_seconds": smoke_duration,
            "average_tokens_per_second": smoke_log["average_tokens_per_second"],
            "validation": smoke_vals,
            "checkpoint": smoke_contract,
            "bad_terms": smoke_log["bad_terms"],
            "training_continuation_allowed": smoke_gate,
            "smoke_log": smoke_log,
        }
        write_report(reports_dir / "smoke_report.md", smoke_report, "Glyph-100M v2.4.2 100-step P100 smoke")
        if not smoke_gate:
            raise RuntimeError("100-step smoke gate failed; full continuation was not started")

        full_root = OUTPUT_ROOT / "continuation"
        full_checkpoints = full_root / "checkpoints"
        full_logs = full_root / "logs"
        full_started = time.perf_counter()
        run(
            training_command(payload_root, smoke_checkpoint, 10000, full_checkpoints, full_logs, 500, 2500, 100),
            cwd=payload_root,
            env=env,
        )
        full_duration = time.perf_counter() - full_started
        final_checkpoint = full_checkpoints / "step_0010000.pt"
        final_contract = validate_checkpoint(final_checkpoint, 10000)
        latest_contract = validate_checkpoint(full_checkpoints / "latest.pt", 10000, finite_model=False)
        full_log = parse_train_log(full_logs / "train.log")
        if full_log["bad_terms"] or not full_log["validation"]:
            raise RuntimeError(f"full continuation log gate failed: {full_log['bad_terms']}")
        if input_sha_before != sha256_file(input_checkpoint):
            raise RuntimeError("input 5k checkpoint changed during the run")

        status = "PASS"
        summary = {
            "status": status,
            "run_id": RUN_ID,
            "started_at_utc": preflight["started_at_utc"],
            "finished_at_utc": utc_now(),
            "wall_seconds": time.perf_counter() - started,
            "gpu": gpu,
            "smoke": {key: value for key, value in smoke_report.items() if key != "smoke_log"},
            "continuation_start_step": 5100,
            "continuation_end_step": 10000,
            "continuation_duration_seconds": full_duration,
            "continuation_average_tokens_per_second": full_log["average_tokens_per_second"],
            "validation": full_log["validation"],
            "final_checkpoint": final_contract,
            "latest_checkpoint": latest_contract,
            "input_5k_checkpoint_unchanged": True,
            "next_training_started": False,
            "full_log": full_log,
        }
        write_report(reports_dir / "training_report.md", summary, "Glyph-100M v2.4.2 P100 continuation to 10k")
        (OUTPUT_ROOT / "SUCCESS").write_text(utc_now() + "\n", encoding="ascii")
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    except Exception as exc:
        failure = {
            "status": status,
            "run_id": RUN_ID,
            "failed_at_utc": utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "next_training_started": False,
        }
        write_report(reports_dir / "failure_report.md", failure, "Glyph-100M v2.4.2 P100 failure")
        raise
    finally:
        monitor.stop()


if __name__ == "__main__":
    main()
