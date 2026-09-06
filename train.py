#!/usr/bin/env python3
"""
Pre-training loop for Glyph-27M Base.

Usage:
  python train.py                   # start fresh
  python train.py --resume          # resume from latest checkpoint
  python train.py --resume checkpoints/step_5000.pt
  python train.py --resume checkpoints/latest.pt --max-steps 10
"""
import os
import shutil
import sys
import math
import time
import signal
import logging
import argparse
import glob
import hashlib
import json
import numpy as np
import torch
from dataclasses import asdict
from pathlib import Path
from datetime import datetime, timezone

# Local imports
sys.path.insert(0, str(Path(__file__).parent))
from config import TrainConfig, get_model_config, get_train_config, model_variant_metadata
from model import GPT

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def configure_logging(log_dir: str, log_file: str | None = None) -> Path:
    """Install per-run logging after the variant-specific TrainConfig is known."""
    target = Path(log_file) if log_file else Path(log_dir) / "train.log"
    target.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
        handler.close()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(target),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return target


def configure_cpu_threads():
    """Configure PyTorch CPU thread counts from affinity/env and log the result."""
    affinity = None
    if hasattr(os, "sched_getaffinity"):
        affinity = sorted(os.sched_getaffinity(0))
        n_threads = len(affinity)
    else:
        n_threads = os.cpu_count() or 1

    env_threads = os.environ.get("TRAIN_NUM_THREADS")
    if env_threads:
        n_threads = max(1, int(env_threads))

    interop_threads = int(os.environ.get("TRAIN_INTEROP_THREADS", "1"))
    interop_threads = max(1, min(interop_threads, n_threads))

    torch.set_num_threads(n_threads)
    try:
        torch.set_num_interop_threads(interop_threads)
    except RuntimeError:
        # PyTorch only allows setting interop threads once per process.
        pass

    affinity_str = ",".join(map(str, affinity)) if affinity is not None else "system-default"
    log.info(
        f"CPU threading: affinity={affinity_str} | torch_threads={torch.get_num_threads()} "
        f"| interop_threads={interop_threads}"
    )


def select_device(requested: str | None) -> torch.device:
    """Select an explicit training device without changing the CPU default."""
    requested = (requested or os.environ.get("TRAIN_DEVICE", "cpu")).strip().lower()
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
    if requested in {"cuda", "gpu"}:
        if not torch.cuda.is_available():
            log.error("CUDA/HIP device requested, but torch.cuda.is_available() is false")
            sys.exit(2)
        return torch.device("cuda")
    if requested == "cpu":
        return torch.device("cpu")
    log.error(f"Unsupported --device/TRAIN_DEVICE value: {requested!r} (use cpu, cuda, or auto)")
    sys.exit(2)


def sync_if_needed(device: torch.device):
    """Synchronize GPU work for honest timing; no-op on CPU."""
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def parse_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def configure_attention_backend(requested: str | None):
    backend = (requested or os.environ.get("GLYPH_ATTENTION_BACKEND", "sdpa")).strip().lower()
    if backend not in {"sdpa", "math", "manual"}:
        log.error(f"Unsupported attention backend {backend!r}; use sdpa, math, or manual")
        sys.exit(2)

    if backend == "manual":
        os.environ["GLYPH_ATTENTION_IMPL"] = "manual"
        log.info("Attention backend: manual causal attention")
        return backend

    os.environ["GLYPH_ATTENTION_IMPL"] = "sdpa"
    if backend == "math":
        try:
            torch.backends.cuda.enable_flash_sdp(False)
            torch.backends.cuda.enable_mem_efficient_sdp(False)
            torch.backends.cuda.enable_math_sdp(True)
            if hasattr(torch.backends.cuda, "enable_cudnn_sdp"):
                torch.backends.cuda.enable_cudnn_sdp(False)
            log.info("Attention backend: SDPA math kernel preferred")
        except Exception as exc:
            log.warning(f"Could not configure SDPA math kernel preference: {exc}")
    else:
        log.info("Attention backend: default SDPA")
    return backend


def move_optimizer_state_to_device(optimizer, device: torch.device):
    """Move checkpointed optimizer tensors after a CPU checkpoint resume."""
    if device.type == "cpu":
        return
    moved = 0
    for state in optimizer.state.values():
        for key, value in list(state.items()):
            if torch.is_tensor(value):
                state[key] = value.to(device)
                moved += 1
    log.info(f"Optimizer state tensors moved to {device}: {moved}")


# ---------------------------------------------------------------------------
# Dataset: memory-mapped binary token file
# ---------------------------------------------------------------------------

class TokenDataset:
    """Memory-mapped tokens with reproducible random or shuffled-block sampling."""

    VALID_SAMPLING = {"random", "shuffled_blocks"}

    def __init__(
        self,
        path: str,
        block_size: int,
        name: str = "Dataset",
        max_tokens: int | None = None,
        sampling: str = "random",
        seed: int = 2026,
    ):
        if sampling not in self.VALID_SAMPLING:
            raise ValueError(f"Unsupported sampling={sampling!r}; use one of {sorted(self.VALID_SAMPLING)}")
        self.path = str(path)
        self.data = np.memmap(path, dtype=np.uint16, mode="r")
        self.block_size = block_size
        self.sampling = sampling
        self.seed = int(seed)
        self.length = len(self.data)
        if max_tokens is not None:
            if max_tokens <= 0:
                raise ValueError(f"max_tokens must be positive, got {max_tokens}")
            self.length = min(self.length, max_tokens)
        self.n = self.length - block_size
        self.rng = np.random.default_rng(self.seed)
        if self.n <= 0:
            raise ValueError(
                f"Token file too small ({self.length} usable tokens) for block_size={block_size}"
            )
        self.num_blocks = (self.n + self.block_size - 1) // self.block_size
        self.epoch = 0
        self.cursor = 0
        self._permutation_epoch = -1
        self._permutation: np.ndarray | None = None
        self.state_restored = False
        limit_note = f" (limited from {len(self.data):,})" if self.length != len(self.data) else ""
        log.info(
            f"{name}: {self.length:,} tokens{limit_note}, {self.n:,} valid start positions | "
            f"sampling={self.sampling} seed={self.seed} nonoverlap_blocks={self.num_blocks:,}"
        )

    def _permutation_for_epoch(self) -> np.ndarray:
        if self._permutation is None or self._permutation_epoch != self.epoch:
            rng = np.random.default_rng(self.seed + self.epoch)
            self._permutation = rng.permutation(self.num_blocks)
            self._permutation_epoch = self.epoch
        return self._permutation

    def _next_starts(self, count: int) -> np.ndarray:
        if self.sampling == "random":
            return self.rng.integers(0, self.n, size=count, dtype=np.int64)

        block_ids: list[np.ndarray] = []
        remaining = count
        while remaining:
            permutation = self._permutation_for_epoch()
            take = min(remaining, self.num_blocks - self.cursor)
            block_ids.append(permutation[self.cursor : self.cursor + take])
            self.cursor += take
            remaining -= take
            if self.cursor >= self.num_blocks:
                self.epoch += 1
                self.cursor = 0
                self._permutation = None
                self._permutation_epoch = -1
        return np.concatenate(block_ids).astype(np.int64, copy=False) * self.block_size

    def _batch_from_starts(self, starts: np.ndarray, device: torch.device):
        batch_size = len(starts)
        batch = np.empty((batch_size, self.block_size + 1), dtype=np.int64)
        for row, start in enumerate(starts):
            batch[row] = self.data[int(start) : int(start) + self.block_size + 1]

        x = torch.from_numpy(np.ascontiguousarray(batch[:, :-1]))
        y = torch.from_numpy(np.ascontiguousarray(batch[:, 1:]))
        return x.to(device), y.to(device)

    def get_batch(self, batch_size: int, device: torch.device):
        return self._batch_from_starts(self._next_starts(batch_size), device)

    def fixed_eval_batches(self, batch_size: int, batches: int, device: torch.device, seed: int):
        """Yield the same non-overlapping validation blocks on every invocation."""
        total = max(1, batches) * batch_size
        block_ids: list[np.ndarray] = []
        remaining = total
        cycle = 0
        while remaining:
            rng = np.random.default_rng(int(seed) + cycle)
            permutation = rng.permutation(self.num_blocks)
            take = min(remaining, self.num_blocks)
            block_ids.append(permutation[:take])
            remaining -= take
            cycle += 1
        starts = np.concatenate(block_ids).astype(np.int64, copy=False) * self.block_size
        for offset in range(0, total, batch_size):
            yield self._batch_from_starts(starts[offset : offset + batch_size], device)

    def state_dict(self) -> dict:
        state = {
            "version": 1,
            "sampling": self.sampling,
            "seed": self.seed,
            "length": self.length,
            "block_size": self.block_size,
            "num_blocks": self.num_blocks,
            "epoch": self.epoch,
            "cursor": self.cursor,
        }
        if self.sampling == "random":
            state["rng_state"] = self.rng.bit_generator.state
        return state

    def load_state_dict(self, state: dict) -> None:
        expected = {
            "sampling": self.sampling,
            "seed": self.seed,
            "length": self.length,
            "block_size": self.block_size,
            "num_blocks": self.num_blocks,
        }
        mismatches = [f"{key}: checkpoint={state.get(key)!r}, current={value!r}" for key, value in expected.items() if state.get(key) != value]
        if mismatches:
            raise ValueError("Dataset sampler state mismatch: " + "; ".join(mismatches))
        self.epoch = int(state.get("epoch", 0))
        self.cursor = int(state.get("cursor", 0))
        if not 0 <= self.cursor < self.num_blocks:
            raise ValueError(f"Invalid dataset sampler cursor: {self.cursor}")
        self._permutation = None
        self._permutation_epoch = -1
        if self.sampling == "random" and state.get("rng_state") is not None:
            self.rng.bit_generator.state = state["rng_state"]
        self.state_restored = True

    def seek_to_sample(self, sample_index: int) -> None:
        if self.sampling != "shuffled_blocks":
            return
        self.epoch, self.cursor = divmod(max(0, int(sample_index)), self.num_blocks)
        self._permutation = None
        self._permutation_epoch = -1


# ---------------------------------------------------------------------------
# Learning rate schedule
# ---------------------------------------------------------------------------

def get_lr(step: int, cfg: TrainConfig) -> float:
    # Linear warmup
    if step < cfg.warmup_steps:
        return cfg.max_lr * step / cfg.warmup_steps
    # Past max_steps: return min_lr
    if step >= cfg.max_steps:
        return cfg.min_lr
    # Cosine decay from max_lr -> min_lr
    progress = (step - cfg.warmup_steps) / (cfg.max_steps - cfg.warmup_steps)
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return cfg.min_lr + (cfg.max_lr - cfg.min_lr) * cosine


@torch.no_grad()
def estimate_loss(
    model,
    dataset: TokenDataset,
    batch_size: int,
    device: torch.device,
    batches: int,
    seed: int = 2027,
) -> float:
    """Estimate loss on a fixed, reproducible panel of validation blocks."""
    was_training = model.training
    model.eval()
    losses = []
    for x, y in dataset.fixed_eval_batches(batch_size, batches, device, seed):
        _, loss = model(x, y)
        losses.append(loss.item())
    if was_training:
        model.train()
    return sum(losses) / len(losses)


def holdout_metadata_path(val_path: Path) -> Path:
    return val_path.with_suffix(".meta.json")


def train_limit_from_holdout_metadata(data_path: Path, val_path: Path) -> int | None:
    """Use holdout metadata to avoid training on the validation tail."""
    meta_path = holdout_metadata_path(val_path)
    if not meta_path.exists():
        return None

    try:
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        log.warning(f"Could not read validation holdout metadata {meta_path}: {exc}")
        return None

    if meta.get("dtype") != "uint16":
        log.warning(f"Ignoring holdout metadata with unexpected dtype: {meta.get('dtype')}")
        return None

    expected_size = meta.get("source_size_bytes")
    try:
        actual_size = data_path.stat().st_size
    except OSError as exc:
        log.warning(f"Could not stat training token file {data_path}: {exc}")
        return None

    if expected_size is not None and int(expected_size) != actual_size:
        log.warning(
            f"Ignoring holdout metadata because source size changed: "
            f"metadata={expected_size}, current={actual_size}"
        )
        return None

    limit = meta.get("train_token_limit")
    if limit is None:
        return None

    limit = int(limit)
    if limit <= 0:
        log.warning(f"Ignoring invalid train_token_limit from {meta_path}: {limit}")
        return None

    log.info(
        f"Validation holdout metadata found: limiting train dataset to first {limit:,} tokens "
        f"so validation tail is not sampled"
    )
    return limit


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------


class NonFiniteLossError(RuntimeError):
    """Raised when training hits NaN/Inf and must stop without checkpointing."""


def effective_tokens_per_step(cfg: TrainConfig, model_cfg) -> int:
    return cfg.batch_size * model_cfg.context_len * cfg.gradient_accumulation_steps


def sha256_file(path: str | Path) -> str | None:
    target = Path(path)
    if not target.exists() or not target.is_file():
        return None
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_metadata(
    model,
    cfg: TrainConfig,
    variant: str,
    step: int,
    effective_tokens: int,
    data_state: dict | None = None,
) -> dict:
    return {
        "variant": variant,
        "model_config": asdict(model.config),
        "train_config": asdict(cfg),
        "batch_size": cfg.batch_size,
        "gradient_accumulation_steps": cfg.gradient_accumulation_steps,
        "effective_tokens_per_step": effective_tokens,
        "context_length": model.config.context_len,
        "tokenizer_path": cfg.tokenizer_path,
        "tokenizer_sha256": sha256_file(cfg.tokenizer_path),
        "current_step": step,
        "dataset_metadata_path": cfg.dataset_metadata_path,
        "dataset_name": cfg.dataset_name,
        "data_sampler": data_state,
        "scheduler_state": {
            "type": "linear_warmup_cosine_decay",
            "step": step,
            "max_steps": cfg.max_steps,
            "warmup_steps": cfg.warmup_steps,
            "max_lr": cfg.max_lr,
            "min_lr": cfg.min_lr,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_checkpoint_compatibility(state: dict, expected_variant: str, expected_model_config) -> None:
    checkpoint_variant = state.get("variant")
    expected_config = asdict(expected_model_config)
    checkpoint_config = state.get("model_config") or {}

    if checkpoint_variant and checkpoint_variant != expected_variant:
        raise ValueError(
            f"Checkpoint variant mismatch: checkpoint={checkpoint_variant!r}, "
            f"requested={expected_variant!r}. Refusing to load."
        )

    if not checkpoint_variant:
        log.warning("Checkpoint has no variant metadata; validating by model_config only")

    if checkpoint_config and checkpoint_config != expected_config:
        raise ValueError(
            "Checkpoint model_config does not match requested variant. "
            f"checkpoint={checkpoint_config}, requested={expected_config}. Refusing to load."
        )


def validate_resume_contract(state: dict, train_cfg, model_cfg, dataset=None, strict: bool = True) -> None:
    """Hard resume checks: tokenizer, dataset, data length, context, batch/accum.

    Any mismatch raises ValueError (STOP) unless strict is False, in which
    case it logs a warning and continues (--allow-mismatch).
    """
    problems: list[str] = []
    live_tok = sha256_file(train_cfg.tokenizer_path)
    if state.get("tokenizer_sha256") != live_tok:
        problems.append(
            f"tokenizer_sha256: checkpoint={state.get('tokenizer_sha256')!r}, "
            f"current={live_tok!r}"
        )
    if state.get("dataset_name") != train_cfg.dataset_name:
        problems.append(
            f"dataset_name: checkpoint={state.get('dataset_name')!r}, "
            f"current={train_cfg.dataset_name!r}"
        )
    if dataset is not None:
        ckpt_len = (state.get("data_state") or {}).get("length")
        live_len = len(dataset.data) if hasattr(dataset, "data") else dataset.length
        if ckpt_len != live_len:
            problems.append(
                f"train_bin length: checkpoint={ckpt_len!r}, current={live_len!r}"
            )
    ckpt_ctx = state.get("context_length", (state.get("model_config") or {}).get("context_len"))
    if ckpt_ctx != model_cfg.context_len:
        problems.append(
            f"context_length: checkpoint={ckpt_ctx!r}, current={model_cfg.context_len!r}"
        )
    if state.get("batch_size") != train_cfg.batch_size:
        problems.append(
            f"batch_size: checkpoint={state.get('batch_size')!r}, "
            f"current={train_cfg.batch_size!r}"
        )
    if state.get("gradient_accumulation_steps") != train_cfg.gradient_accumulation_steps:
        problems.append(
            "gradient_accumulation_steps: "
            f"checkpoint={state.get('gradient_accumulation_steps')!r}, "
            f"current={train_cfg.gradient_accumulation_steps!r}"
        )
    if not problems:
        log.info("Resume contract OK: tokenizer, dataset, data length, context, batch/accum match")
        return
    message = "Resume contract mismatch:\n  " + "\n  ".join(problems)
    if strict:
        raise ValueError(message + "\nRefusing to resume. Pass --allow-mismatch to override.")
    log.warning(message + "\nContinuing due to --allow-mismatch.")


def write_emergency_report(
    cfg: TrainConfig,
    variant: str,
    step: int,
    micro_step: int,
    reason: str,
    loss_value: float,
    model_cfg=None,
) -> Path:
    report_dir = Path(cfg.log_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report = report_dir / "emergency_stop.json"
    payload = {
        "variant": variant,
        "step": step,
        "micro_step": micro_step,
        "reason": reason,
        "loss": loss_value,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "train_config": asdict(cfg),
        "model_config": asdict(model_cfg) if model_cfg is not None else None,
        "latest_checkpoint_not_overwritten": True,
    }
    tmp = report.with_suffix(report.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    tmp.replace(report)
    return report


def check_model_parameters_finite(model, cfg: TrainConfig, variant: str, step: int, reason: str, model_cfg) -> None:
    for name, param in model.named_parameters():
        if not torch.isfinite(param.detach()).all():
            report = write_emergency_report(
                cfg,
                variant=variant,
                step=step,
                micro_step=0,
                reason=reason,
                loss_value=float("nan"),
                model_cfg=model_cfg,
            )
            raise NonFiniteLossError(
                f"Non-finite model parameter after optimizer step {step}: {name}. "
                f"Emergency report written to {report}; latest checkpoint was not overwritten."
            )


def assert_finite_loss(loss, cfg: TrainConfig, variant: str, step: int, micro_step: int, model_cfg) -> None:
    if torch.isfinite(loss.detach()).all():
        return
    try:
        loss_value = float(loss.detach().item())
    except Exception:
        loss_value = float("nan")
    report = write_emergency_report(
        cfg,
        variant=variant,
        step=step,
        micro_step=micro_step,
        reason="non_finite_loss",
        loss_value=loss_value,
        model_cfg=model_cfg,
    )
    raise NonFiniteLossError(
        f"Non-finite loss at step {step}, micro_step {micro_step}: {loss_value}. "
        f"Emergency report written to {report}; latest checkpoint was not overwritten."
    )


def save_checkpoint(
    model,
    optimizer,
    step: int,
    loss: float,
    cfg: TrainConfig,
    variant: str,
    effective_tokens: int,
    tag: str = None,
    update_latest: bool = True,
    data_state: dict | None = None,
):
    ckpt_dir = Path(cfg.checkpoint_dir)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    tag = tag or f"step_{step:07d}"
    path = ckpt_dir / f"{tag}.pt"
    latest = ckpt_dir / "latest.pt"

    metadata = checkpoint_metadata(model, cfg, variant, step, effective_tokens, data_state=data_state)
    state = {
        "step": step,
        "loss": loss,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "model_config": metadata["model_config"],
        "variant": variant,
        "train_config": metadata["train_config"],
        "batch_size": metadata["batch_size"],
        "gradient_accumulation_steps": metadata["gradient_accumulation_steps"],
        "effective_tokens_per_step": metadata["effective_tokens_per_step"],
        "context_length": metadata["context_length"],
        "tokenizer_path": metadata["tokenizer_path"],
        "tokenizer_sha256": metadata["tokenizer_sha256"],
        "current_step": metadata["current_step"],
        "dataset_metadata_path": metadata["dataset_metadata_path"],
        "dataset_name": metadata["dataset_name"],
        "data_state": data_state,
        "scheduler_state": metadata["scheduler_state"],
        "checkpoint_metadata": metadata,
    }
    # Atomic write: single serialization to tmp, fsync, then rename.
    tmp = ckpt_dir / f".{tag}.pt.tmp"
    torch.save(state, tmp)
    with open(tmp, "rb") as handle:
        os.fsync(handle.fileno())
    os.replace(tmp, path)

    # Verify before touching latest: reload must deserialize with same step.
    probe = None
    try:
        probe = torch.load(path, map_location="cpu", weights_only=False)
        verified = (
            isinstance(probe, dict)
            and probe.get("step") == step
            and isinstance(probe.get("model"), dict)
            and set(probe["model"].keys()) == set(model.state_dict().keys())
        )
    except Exception:
        verified = False
    finally:
        del probe
    if not verified:
        corrupt = path.with_name(path.name + ".corrupt")
        os.replace(path, corrupt)
        raise IOError(
            f"Checkpoint verification failed for {path}; quarantined as {corrupt}. "
            "Previous checkpoints untouched."
        )

    # latest.pt is a hardlink (same bytes), not a second serialization.
    if update_latest:
        if latest.exists() or latest.is_symlink():
            latest.unlink()
        try:
            os.link(path, latest)
        except OSError:
            shutil.copyfile(path, latest)

    log.info(f"Checkpoint saved: {path} (loss={loss:.4f})")
    return path


def load_checkpoint(
    path: str,
    model,
    optimizer=None,
    expected_variant: str | None = None,
    expected_model_config=None,
    dataset: TokenDataset | None = None,
    train_cfg=None,
    strict: bool = True,
):
    log.info(f"Loading checkpoint: {path}")
    state = torch.load(path, map_location="cpu", weights_only=False)
    if expected_variant and expected_model_config is not None:
        validate_checkpoint_compatibility(state, expected_variant, expected_model_config)
    if train_cfg is not None:
        model_cfg = expected_model_config if expected_model_config is not None else model.config
        validate_resume_contract(state, train_cfg, model_cfg, dataset=dataset, strict=strict)
    model.load_state_dict(state["model"])
    if optimizer is not None and "optimizer" in state:
        optimizer.load_state_dict(state["optimizer"])
    if dataset is not None and state.get("data_state"):
        dataset.load_state_dict(state["data_state"])
        log.info(
            f"  Dataset sampler restored: sampling={dataset.sampling} "
            f"epoch={dataset.epoch} cursor={dataset.cursor:,}"
        )
    elif dataset is not None:
        log.warning("Checkpoint has no dataset sampler state; exact data-order resume is unavailable")
    step = state.get("step", 0)
    loss = state.get("loss", float("nan"))
    log.info(f"  Resumed from step {step:,} (last loss={loss:.4f})")
    return step


def prefer_foreach_optimizer(optimizer, enabled: bool):
    """Configure foreach AdamW updates while keeping checkpoint resumes intact."""
    for group in optimizer.param_groups:
        group["foreach"] = enabled
        group["fused"] = False


def find_latest_checkpoint(ckpt_dir: str) -> str | None:
    latest = Path(ckpt_dir) / "latest.pt"
    if latest.exists():
        return str(latest)
    # Fallback: find highest step checkpoint
    ckpts = sorted(glob.glob(str(Path(ckpt_dir) / "step_*.pt")))
    return ckpts[-1] if ckpts else None


# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------

_shutdown_requested = False


def _handle_signal(sig, frame):
    global _shutdown_requested
    log.info("Interrupt received — will save checkpoint and exit after current step")
    _shutdown_requested = True


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def _write_run_status(log_dir, exit_code: int, reason: str) -> None:
    """Record process exit status next to train.log (never raises)."""
    try:
        out_dir = Path(log_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (out_dir / "exit_code.txt").write_text(f"{exit_code}\n", encoding="utf-8")
        (out_dir / "finished_at.txt").write_text(f"{finished}\n", encoding="utf-8")
        (out_dir / "run_status.json").write_text(
            json.dumps({"exit_code": exit_code, "reason": reason,
                        "finished_at_utc": finished}) + "\n",
            encoding="utf-8",
        )
    except Exception as exc:
        log.warning(f"Could not write run status: {exc}")


def train(args):
    """Entry point: runs training and records the process exit status.

    Status files (exit_code.txt, finished_at.txt, run_status.json with the
    stop reason) are written from the training process itself in finally, so
    a dead tee/pipe cannot lose them the way the cooldown run did.
    """
    try:
        base_cfg = get_train_config(args.variant)
    except Exception:
        base_cfg = None
    log_dir = args.log_dir or (base_cfg.log_dir if base_cfg is not None else None)
    exit_code, reason = 0, "complete"
    try:
        _train_impl(args)
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1
        reason = "SIGINT-shutdown" if _shutdown_requested else f"SystemExit({exc.code})"
        raise
    except KeyboardInterrupt:
        exit_code, reason = 130, "KeyboardInterrupt"
        raise
    except Exception as exc:
        exit_code, reason = 1, f"{type(exc).__name__}: {exc}"
        raise
    finally:
        if log_dir:
            _write_run_status(log_dir, exit_code, reason)


def _train_impl(args):
    try:
        model_cfg = get_model_config(args.variant)
        train_cfg = get_train_config(args.variant)
        variant_meta = model_variant_metadata(args.variant)
    except ValueError as exc:
        log.error(str(exc))
        sys.exit(2)
    if args.eval_only and not args.resume:
        args.resume = True
    if args.checkpoint_dir is not None:
        train_cfg.checkpoint_dir = args.checkpoint_dir
    if args.log_dir is not None:
        train_cfg.log_dir = args.log_dir
    if args.tokenizer_path is not None:
        train_cfg.tokenizer_path = args.tokenizer_path
    if args.dataset_metadata_path is not None:
        train_cfg.dataset_metadata_path = args.dataset_metadata_path
    if args.dataset_name is not None:
        train_cfg.dataset_name = args.dataset_name
    if args.data_path is not None:
        train_cfg.data_path = args.data_path
    if args.val_data_path is not None:
        train_cfg.val_data_path = args.val_data_path
    if args.batch_size is not None:
        train_cfg.batch_size = args.batch_size
    if args.learning_rate is not None:
        train_cfg.max_lr = args.learning_rate
    if args.min_lr is not None:
        train_cfg.min_lr = args.min_lr
    if args.warmup_steps is not None:
        train_cfg.warmup_steps = args.warmup_steps
    if args.weight_decay is not None:
        train_cfg.weight_decay = args.weight_decay
    if args.grad_clip is not None:
        train_cfg.grad_clip = args.grad_clip
    if args.gradient_accumulation_steps is not None:
        train_cfg.gradient_accumulation_steps = args.gradient_accumulation_steps
    if args.train_sampling is not None:
        train_cfg.train_sampling = args.train_sampling
    if args.data_seed is not None:
        train_cfg.data_seed = args.data_seed
    if args.eval_seed is not None:
        train_cfg.eval_seed = args.eval_seed
    if args.eval_interval is not None:
        train_cfg.eval_interval = args.eval_interval
    if args.val_batches is not None:
        train_cfg.eval_batches = args.val_batches
    if args.checkpoint_interval is not None:
        train_cfg.checkpoint_interval = args.checkpoint_interval
    if args.log_interval is not None:
        train_cfg.log_interval = args.log_interval
    optimizer_foreach = parse_bool(args.optimizer_foreach, default=parse_bool(os.environ.get("TRAIN_OPTIMIZER_FOREACH"), True))
    finite_check_interval = args.finite_check_interval or 0

    if args.max_steps is not None and args.max_steps <= 0:
        log.error("--max-steps must be a positive integer")
        sys.exit(2)
    if args.batch_size is not None and args.batch_size <= 0:
        log.error("--batch-size must be a positive integer")
        sys.exit(2)
    if args.learning_rate is not None and args.learning_rate <= 0:
        log.error("--learning-rate must be positive")
        sys.exit(2)
    if args.min_lr is not None and args.min_lr < 0:
        log.error("--min-lr must be non-negative")
        sys.exit(2)
    if train_cfg.min_lr > train_cfg.max_lr:
        log.error("--min-lr cannot be larger than learning rate")
        sys.exit(2)
    if args.train_token_limit is not None and args.train_token_limit <= 0:
        log.error("--train-token-limit must be a positive integer")
        sys.exit(2)
    if train_cfg.gradient_accumulation_steps <= 0:
        log.error("--gradient-accumulation-steps must be a positive integer")
        sys.exit(2)
    if args.checkpoint_interval is not None and args.checkpoint_interval <= 0:
        log.error("--checkpoint-interval must be a positive integer")
        sys.exit(2)
    if args.log_interval is not None and args.log_interval <= 0:
        log.error("--log-interval must be a positive integer")
        sys.exit(2)
    if train_cfg.eval_batches <= 0:
        log.error("--val-batches must be a positive integer")
        sys.exit(2)

    log_file = configure_logging(train_cfg.log_dir, args.log_file)
    log.info(f"Log file: {log_file}")

    device = select_device(args.device)
    configure_attention_backend(args.attention_backend)
    configure_cpu_threads()
    if device.type == "cuda":
        log.info(
            f"GPU: {torch.cuda.get_device_name(device)} | "
            f"HIP={getattr(torch.version, 'hip', None)} | CUDA API via torch.cuda"
        )

    # Sanity check: token file exists
    data_path = Path(train_cfg.data_path)
    if not data_path.exists():
        log.error(f"Token file not found: {train_cfg.data_path}")
        log.error("Run: python data/download.py && python data/preprocess.py")
        sys.exit(1)

    log.info("=" * 60)
    if args.eval_only:
        log.info(f"Starting {variant_meta['display_name']} validation")
    else:
        log.info(f"Starting {variant_meta['display_name']} pre-training")
    log.info(f"Variant: {variant_meta['variant']} ({variant_meta['display_name']})")
    log.info(f"Device: {device}")
    log.info(f"Model config: {model_cfg}")
    log.info(f"Train config: {train_cfg}")
    log.info(f"Dataset name: {train_cfg.dataset_name}")
    log.info("=" * 60)

    val_dataset = None
    val_path = Path(train_cfg.val_data_path)
    train_token_limit = args.train_token_limit
    if val_path.exists():
        val_dataset = TokenDataset(
            str(val_path),
            model_cfg.context_len,
            name="Validation dataset",
            sampling="random",
            seed=train_cfg.eval_seed,
        )
        if train_token_limit is None:
            train_token_limit = train_limit_from_holdout_metadata(data_path, val_path)
    else:
        log.info(f"Validation token file not found: {val_path} (validation disabled)")

    # Dataset
    dataset = TokenDataset(
        train_cfg.data_path,
        model_cfg.context_len,
        name="Train dataset",
        max_tokens=train_token_limit,
        sampling=train_cfg.train_sampling,
        seed=train_cfg.data_seed,
    )

    # Model
    model = GPT(model_cfg).to(device)

    # Optimizer — separate weight decay for 2D params (matrices) only
    decay_params = [p for n, p in model.named_parameters() if p.dim() >= 2]
    nodecay_params = [p for n, p in model.named_parameters() if p.dim() < 2]
    optimizer = torch.optim.AdamW(
        [
            {"params": decay_params, "weight_decay": train_cfg.weight_decay},
            {"params": nodecay_params, "weight_decay": 0.0},
        ],
        lr=train_cfg.max_lr,
        betas=(train_cfg.beta1, train_cfg.beta2),
        foreach=optimizer_foreach,
        fused=False,  # fused AdamW not available on CPU
    )
    prefer_foreach_optimizer(optimizer, optimizer_foreach)
    log.info(f"Optimizer: AdamW foreach={optimizer_foreach} fused=False")

    # Resume
    start_step = 0
    if args.resume:
        ckpt_path = args.resume if isinstance(args.resume, str) and Path(args.resume).exists() \
            else find_latest_checkpoint(train_cfg.checkpoint_dir)
        if ckpt_path:
            try:
                start_step = load_checkpoint(
                    ckpt_path,
                    model,
                    optimizer,
                    expected_variant=variant_meta["variant"],
                    expected_model_config=model_cfg,
                    dataset=dataset,
                    train_cfg=train_cfg,
                    strict=not args.allow_mismatch,
                )
            except ValueError as exc:
                log.error(str(exc))
                sys.exit(2)
            move_optimizer_state_to_device(optimizer, device)
            prefer_foreach_optimizer(optimizer, optimizer_foreach)
            if dataset.sampling == "shuffled_blocks" and not dataset.state_restored:
                samples_seen = start_step * train_cfg.batch_size * train_cfg.gradient_accumulation_steps
                dataset.seek_to_sample(samples_seen)
                log.warning(
                    f"Derived shuffled sampler position from optimizer step: samples_seen={samples_seen:,} "
                    f"epoch={dataset.epoch} cursor={dataset.cursor:,}"
                )
        else:
            log.warning("No checkpoint found, starting from scratch")

    if args.eval_only:
        if val_dataset is None:
            log.error("Validation requested, but validation dataset is not available")
            sys.exit(1)
        val_loss = estimate_loss(
            model,
            val_dataset,
            train_cfg.batch_size,
            device,
            train_cfg.eval_batches,
            train_cfg.eval_seed,
        )
        log.info(
            f"eval step={start_step:7d} | val_loss={val_loss:.4f} | "
            f"batches={train_cfg.eval_batches} | eval_only=1"
        )
        return

    # Training
    model.train()
    t0 = time.perf_counter()
    effective_tokens = effective_tokens_per_step(train_cfg, model_cfg)
    effective_tokens_per_step_value = effective_tokens
    tokens_seen = start_step * effective_tokens_per_step_value
    running_loss = 0.0
    running_steps = 0
    data_time = 0.0
    forward_time = 0.0
    backward_time = 0.0
    optimizer_time = 0.0
    target_step = args.max_steps
    limited_run = target_step is not None
    end_step = train_cfg.max_steps
    if limited_run:
        end_step = min(train_cfg.max_steps, target_step)

    if start_step >= end_step:
        log.info(f"Checkpoint is already at or beyond target step ({end_step:,}); nothing to do")
        return

    log.info(f"Training from step {start_step + 1:,} to {end_step:,}")
    log.info(
        f"Microbatch={train_cfg.batch_size} context={model_cfg.context_len} "
        f"grad_accum={train_cfg.gradient_accumulation_steps} "
        f"effective_tokens/step={effective_tokens_per_step_value:,} "
        f"sampling={dataset.sampling} data_seed={dataset.seed}"
    )
    if limited_run:
        log.info(f"Limited run enabled: target step {target_step:,}")

    loss_val = None

    for step in range(start_step + 1, end_step + 1):
        # Adjust learning rate
        lr = get_lr(step, train_cfg)
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        optimizer.zero_grad(set_to_none=True)
        step_loss = 0.0

        for micro_step in range(1, train_cfg.gradient_accumulation_steps + 1):
            data_t0 = time.perf_counter()
            x, y = dataset.get_batch(train_cfg.batch_size, device)
            data_time += time.perf_counter() - data_t0

            forward_t0 = time.perf_counter()
            _, loss = model(x, y)
            sync_if_needed(device)
            forward_time += time.perf_counter() - forward_t0

            try:
                assert_finite_loss(loss, train_cfg, variant_meta["variant"], step, micro_step, model_cfg)
            except NonFiniteLossError as exc:
                log.error(str(exc))
                sys.exit(1)

            step_loss += loss.item()
            backward_t0 = time.perf_counter()
            (loss / train_cfg.gradient_accumulation_steps).backward()
            sync_if_needed(device)
            backward_time += time.perf_counter() - backward_t0

        if train_cfg.grad_clip > 0:
            try:
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    train_cfg.grad_clip,
                    error_if_nonfinite=True,
                )
            except RuntimeError as exc:
                report = write_emergency_report(
                    train_cfg,
                    variant=variant_meta["variant"],
                    step=step,
                    micro_step=0,
                    reason="non_finite_grad_norm",
                    loss_value=float("nan"),
                    model_cfg=model_cfg,
                )
                log.error(
                    f"Non-finite gradient norm at step {step}: {exc}. "
                    f"Emergency report written to {report}; latest checkpoint was not overwritten."
                )
                sys.exit(1)
        sync_if_needed(device)

        optimizer_t0 = time.perf_counter()
        optimizer.step()
        sync_if_needed(device)
        if finite_check_interval > 0 and step % finite_check_interval == 0:
            try:
                check_model_parameters_finite(
                    model,
                    train_cfg,
                    variant_meta["variant"],
                    step,
                    "non_finite_model_after_optimizer",
                    model_cfg,
                )
            except NonFiniteLossError as exc:
                log.error(str(exc))
                sys.exit(1)
        optimizer_time += time.perf_counter() - optimizer_t0

        loss_val = step_loss / train_cfg.gradient_accumulation_steps
        running_loss += loss_val
        running_steps += 1
        tokens_seen += effective_tokens_per_step_value

        # Logging
        if step % train_cfg.log_interval == 0 and step > 0:
            t1 = time.perf_counter()
            elapsed = t1 - t0
            avg_loss = running_loss / running_steps
            tokens_per_sec = (running_steps * effective_tokens_per_step_value) / elapsed
            log.info(
                f"step={step:7d} | loss={avg_loss:.4f} | lr={lr:.2e} | "
                f"tok/s={tokens_per_sec:,.0f} | tokens={tokens_seen/1e6:.2f}M | "
                f"data={data_time/elapsed:.1%} fwd={forward_time/elapsed:.1%} "
                f"bwd={backward_time/elapsed:.1%} opt={optimizer_time/elapsed:.1%}"
            )
            running_loss = 0.0
            running_steps = 0
            data_time = 0.0
            forward_time = 0.0
            backward_time = 0.0
            optimizer_time = 0.0
            t0 = time.perf_counter()

        # Checkpoint
        if step % train_cfg.checkpoint_interval == 0 and step > 0:
            save_checkpoint(
                model,
                optimizer,
                step,
                loss_val,
                train_cfg,
                variant_meta["variant"],
                effective_tokens_per_step_value,
                data_state=dataset.state_dict(),
            )

        # Optional validation, only if data/processed/val_tokens.bin exists.
        if (
            val_dataset is not None
            and train_cfg.eval_interval > 0
            and step % train_cfg.eval_interval == 0
            and step > 0
        ):
            val_loss = estimate_loss(
                model,
                val_dataset,
                train_cfg.batch_size,
                device,
                train_cfg.eval_batches,
                train_cfg.eval_seed,
            )
            log.info(
                f"eval step={step:7d} | val_loss={val_loss:.4f} | "
                f"batches={train_cfg.eval_batches}"
            )

        # Graceful shutdown
        if _shutdown_requested:
            log.info("Saving emergency checkpoint before exit ...")
            save_checkpoint(
                model,
                optimizer,
                step,
                loss_val,
                train_cfg,
                variant_meta["variant"],
                effective_tokens_per_step_value,
                tag="emergency",
                data_state=dataset.state_dict(),
            )
            log.info("Exiting cleanly.")
            sys.exit(0)

    if loss_val is None:
        log.info("No optimizer steps were run.")
        return

    if end_step >= train_cfg.max_steps:
        save_checkpoint(
            model,
            optimizer,
            train_cfg.max_steps,
            loss_val,
            train_cfg,
            variant_meta["variant"],
            effective_tokens_per_step_value,
            tag="final",
            data_state=dataset.state_dict(),
        )
        log.info("Training complete.")
    else:
        log.info("Limited run complete; no final checkpoint was written.")


def main():
    parser = argparse.ArgumentParser(description="Train Glyph model variants")
    parser.add_argument(
        "--variant",
        type=str,
        default=os.environ.get("GLYPH_MODEL_VARIANT", "glyph-27m"),
        help="Model variant: glyph-27m or glyph-100m (default: GLYPH_MODEL_VARIANT or glyph-27m)",
    )
    parser.add_argument(
        "--resume",
        nargs="?",
        const=True,
        default=False,
        help="Resume from latest checkpoint, or specify a checkpoint path",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="Target optimizer step to stop at (useful for staged runs and smoke tests)",
    )
    parser.add_argument(
        "--val-batches",
        type=int,
        default=None,
        help="Override number of fixed validation batches if val_tokens.bin exists",
    )
    parser.add_argument(
        "--eval-interval",
        type=int,
        default=None,
        help="Override validation interval in optimizer steps (0 disables validation)",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=None,
        help="Override checkpoint interval in optimizer steps",
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=None,
        help="Override training log interval in optimizer steps",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default=None,
        help="Override training token file path",
    )
    parser.add_argument(
        "--val-data-path",
        type=str,
        default=None,
        help="Override validation token file path",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default=None,
        help="Override checkpoint directory",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default=None,
        help="Override variant-specific log directory",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Override exact train log file path",
    )
    parser.add_argument(
        "--tokenizer-path",
        type=str,
        default=None,
        help="Tokenizer path recorded in checkpoint metadata",
    )
    parser.add_argument(
        "--dataset-metadata-path",
        type=str,
        default=None,
        help="Dataset metadata path recorded in checkpoint metadata",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default=None,
        help="Dataset name recorded in logs and checkpoint metadata",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override optimizer batch size",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="Override max learning rate",
    )
    parser.add_argument(
        "--min-lr",
        type=float,
        default=None,
        help="Override minimum learning rate",
    )
    parser.add_argument(
        "--warmup-steps",
        type=int,
        default=None,
        help="Override warmup steps",
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=None,
        help="Override AdamW weight decay",
    )
    parser.add_argument(
        "--grad-clip",
        type=float,
        default=None,
        help="Override gradient clipping norm",
    )
    parser.add_argument(
        "--gradient-accumulation-steps",
        type=int,
        default=None,
        help="Accumulate gradients over N microbatches before each optimizer step",
    )
    parser.add_argument(
        "--train-sampling",
        choices=sorted(TokenDataset.VALID_SAMPLING),
        default=None,
        help="Training sampler: random with replacement or shuffled non-overlapping blocks",
    )
    parser.add_argument(
        "--data-seed",
        type=int,
        default=None,
        help="Seed for the training sampler (stored in future checkpoints)",
    )
    parser.add_argument(
        "--eval-seed",
        type=int,
        default=None,
        help="Seed for the fixed validation panel",
    )
    parser.add_argument(
        "--optimizer-foreach",
        choices=["true", "false", "1", "0", "yes", "no", "on", "off"],
        default=os.environ.get("TRAIN_OPTIMIZER_FOREACH"),
        help="Enable or disable AdamW foreach updates (default: TRAIN_OPTIMIZER_FOREACH or true)",
    )
    parser.add_argument(
        "--attention-backend",
        choices=["sdpa", "math", "manual"],
        default=os.environ.get("GLYPH_ATTENTION_BACKEND", "sdpa"),
        help="Attention backend: default SDPA, SDPA math preference, or manual causal attention",
    )
    parser.add_argument(
        "--finite-check-interval",
        type=int,
        default=int(os.environ.get("TRAIN_FINITE_CHECK_INTERVAL", "0")),
        help="Check all model parameters for NaN/Inf every N optimizer steps; 0 disables",
    )
    parser.add_argument(
        "--train-token-limit",
        type=int,
        default=None,
        help="Limit training dataset to the first N tokens, useful when holding out the tail",
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Load a checkpoint and compute validation loss without training",
    )
    parser.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Resume despite tokenizer/dataset/batch contract mismatch (logs warning)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=os.environ.get("TRAIN_DEVICE", "cpu"),
        help="Training device: cpu, cuda, or auto (default: TRAIN_DEVICE or cpu)",
    )
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
