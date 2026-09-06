#!/usr/bin/env python3
"""Resume-safe Glyph SFT runner for a local Colab CUDA workspace.

Training is impossible unless --confirm-training is passed explicitly.
The default mode is conservative fp32 with a fresh AdamW optimizer.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import random
import shutil
import signal
import sys
import time
from contextlib import nullcontext
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.nn.functional as F


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import ModelConfig
from finetune import SFTDataset
from model import GPT
from scripts.colab_bundle_utils import atomic_copy_verified, atomic_write_json, sha256_file
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece


EXPECTED_TOKENIZER_SHA = "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029"
CONFIRMATION_HELP = "Training is disabled. Re-run with --confirm-training after reviewing preflight output."
shutdown_requested = False


@dataclass
class TrainingConfig:
    run_id: str
    base_checkpoint: str
    train_jsonl: str
    val_jsonl: str
    tokenizer: str
    output_dir: str
    resume_checkpoint: str | None
    max_steps: int
    batch_size: int
    gradient_accumulation_steps: int
    learning_rate: float
    min_lr: float
    warmup_steps: int
    weight_decay: float
    grad_clip: float
    eval_interval: int
    eval_batches: int
    checkpoint_interval: int
    log_interval: int
    precision: str
    save_best_on_val: bool
    seed: int
    expected_base_step: int
    expected_variant: str
    expected_tokenizer_sha: str
    dataset_name: str
    milestone_copy_dir: str | None
    milestone_copy_interval: int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = ROOT / value
    return value.resolve()


def signal_handler(signum, _frame) -> None:
    global shutdown_requested
    shutdown_requested = True
    logging.getLogger("glyph-colab-sft").warning("Signal %s received; stopping after the current optimizer step", signum)


def configure_logging(run_root: Path) -> logging.Logger:
    log_dir = run_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("glyph-colab-sft")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_dir / "train.log", encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def checkpoint_step(state: dict) -> int:
    return int(state.get("current_step", state.get("step", 0)))


def checkpoint_config(state: dict) -> ModelConfig:
    raw = state.get("model_config") or {}
    allowed = ModelConfig.__dataclass_fields__
    return ModelConfig(**{key: value for key, value in raw.items() if key in allowed})


def load_torch(path: Path, *, mmap: bool = False) -> dict:
    kwargs = {"map_location": "cpu", "weights_only": False}
    if mmap:
        try:
            return torch.load(path, mmap=True, **kwargs)
        except (TypeError, RuntimeError):
            pass
    return torch.load(path, **kwargs)


def validate_base(state: dict, cfg: TrainingConfig, tokenizer_sha: str) -> ModelConfig:
    step = checkpoint_step(state)
    variant = state.get("variant")
    model_cfg = checkpoint_config(state)
    problems = []
    if step != cfg.expected_base_step:
        problems.append(f"base step={step}, expected={cfg.expected_base_step}")
    if variant != cfg.expected_variant:
        problems.append(f"variant={variant!r}, expected={cfg.expected_variant!r}")
    if model_cfg.context_len != 512:
        problems.append(f"context_len={model_cfg.context_len}, expected=512")
    if state.get("tokenizer_sha256") != tokenizer_sha:
        problems.append("checkpoint tokenizer SHA differs from tokenizer file")
    if tokenizer_sha != cfg.expected_tokenizer_sha:
        problems.append("tokenizer file SHA differs from approved SHA")
    if not state.get("model"):
        problems.append("model state is missing")
    if problems:
        raise ValueError("Base checkpoint validation failed: " + "; ".join(problems))
    return model_cfg


def validate_special_tokens(tokenizer_path: Path):
    sp = load_sentencepiece(tokenizer_path)
    ids = {
        "user": sp.piece_to_id(USER_TOKEN),
        "assistant": sp.piece_to_id(ASSISTANT_TOKEN),
        "end": sp.piece_to_id(END_TOKEN),
    }
    if any(value < 0 for value in ids.values()):
        raise ValueError(f"Tokenizer is missing SFT special tokens: {ids}")
    return sp, ids


def validate_label_contract(dataset: SFTDataset) -> dict:
    if not dataset.pairs:
        raise ValueError("No usable training pairs")
    checked = min(64, len(dataset.pairs))
    first_supervised = True
    end_supervised = True
    prompt_masked = True
    for x, labels in dataset.pairs[:checked]:
        assistant_position = x.index(dataset.assistant_id)
        first_supervised &= labels[assistant_position] != -100
        end_supervised &= dataset.end_id in labels
        prompt_masked &= all(label == -100 for label in labels[:assistant_position])
    result = {
        "boundary": "i < assistant_pos",
        "checked_examples": checked,
        "first_assistant_token_supervised": first_supervised,
        "end_token_supervised": end_supervised,
        "prompt_not_supervised": prompt_masked,
        "padding_ignore_index": -100,
    }
    if not all((first_supervised, end_supervised, prompt_masked)):
        raise ValueError(f"SFT label contract failed: {result}")
    return result


def build_optimizer(model: GPT, cfg: TrainingConfig) -> torch.optim.Optimizer:
    decay = [parameter for parameter in model.parameters() if parameter.requires_grad and parameter.dim() >= 2]
    no_decay = [parameter for parameter in model.parameters() if parameter.requires_grad and parameter.dim() < 2]
    return torch.optim.AdamW(
        [
            {"params": decay, "weight_decay": cfg.weight_decay},
            {"params": no_decay, "weight_decay": 0.0},
        ],
        lr=cfg.learning_rate,
        betas=(0.9, 0.95),
        fused=False,
    )


def build_scheduler(optimizer: torch.optim.Optimizer, cfg: TrainingConfig):
    floor = cfg.min_lr / cfg.learning_rate

    def multiplier(step: int) -> float:
        if cfg.warmup_steps > 0 and step < cfg.warmup_steps:
            return max(1.0 / cfg.warmup_steps, (step + 1) / cfg.warmup_steps)
        span = max(1, cfg.max_steps - cfg.warmup_steps)
        progress = min(1.0, max(0.0, (step - cfg.warmup_steps) / span))
        return floor + 0.5 * (1.0 - floor) * (1.0 + math.cos(math.pi * progress))

    return torch.optim.lr_scheduler.LambdaLR(optimizer, multiplier)


def build_scaler(precision: str):
    if precision != "fp16":
        return None
    try:
        return torch.amp.GradScaler("cuda", enabled=True)
    except (AttributeError, TypeError):
        return torch.cuda.amp.GradScaler(enabled=True)


def autocast_context(precision: str):
    if precision == "fp32":
        return nullcontext()
    dtype = torch.float16 if precision == "fp16" else torch.bfloat16
    return torch.autocast(device_type="cuda", dtype=dtype, enabled=True)


def random_batch(dataset: SFTDataset, batch_size: int, device: torch.device, rng: random.Random):
    indices = [rng.randrange(len(dataset.pairs)) for _ in range(batch_size)]
    return dataset._batch_tensors(indices, device)


@torch.no_grad()
def evaluate(
    model: GPT,
    dataset: SFTDataset,
    cfg: TrainingConfig,
    device: torch.device,
    step: int,
) -> float:
    was_training = model.training
    model.eval()
    rng = random.Random(cfg.seed + 1_000_003 + step)
    losses = []
    for _ in range(max(1, cfg.eval_batches)):
        x, labels = random_batch(dataset, cfg.batch_size, device, rng)
        with autocast_context(cfg.precision):
            logits, _ = model(x)
            loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), labels.reshape(-1), ignore_index=-100)
        if not torch.isfinite(loss).item():
            raise RuntimeError(f"Non-finite validation loss at step {step}")
        losses.append(float(loss.detach().cpu().item()))
    if was_training:
        model.train()
    return sum(losses) / len(losses)


def global_grad_norm(model: GPT) -> float:
    squares = []
    for parameter in model.parameters():
        if parameter.grad is not None:
            squares.append(parameter.grad.detach().float().norm(2).pow(2))
    if not squares:
        return 0.0
    return float(torch.stack(squares).sum().sqrt().cpu().item())


def parameters_finite(model: GPT) -> bool:
    return all(bool(torch.isfinite(parameter).all().item()) for parameter in model.parameters())


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_pointer(source: Path, destination: Path) -> None:
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    try:
        os.link(source, temporary)
    except OSError:
        shutil.copy2(source, temporary)
    os.replace(temporary, destination)
    fsync_directory(destination.parent)


def validate_saved_checkpoint(path: Path, expected_step: int, expected_variant: str, tokenizer_sha: str) -> dict:
    state = load_torch(path, mmap=True)
    if checkpoint_step(state) != expected_step:
        raise IOError(f"Checkpoint reload step mismatch for {path}")
    if state.get("variant") != expected_variant:
        raise IOError(f"Checkpoint reload variant mismatch for {path}")
    if state.get("tokenizer_sha256") != tokenizer_sha:
        raise IOError(f"Checkpoint reload tokenizer mismatch for {path}")
    if not state.get("model") or not state.get("optimizer") or not state.get("scheduler"):
        raise IOError(f"Checkpoint reload missing model/optimizer/scheduler for {path}")
    return {
        "path": str(path),
        "step": checkpoint_step(state),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def checkpoint_payload(
    model: GPT,
    optimizer: torch.optim.Optimizer,
    scheduler,
    scaler,
    cfg: TrainingConfig,
    model_cfg: ModelConfig,
    step: int,
    train_loss: float,
    val_loss: float | None,
    best_val_loss: float | None,
    train_sha: str,
    val_sha: str,
    tokenizer_sha: str,
    base_checkpoint_sha: str,
    rng: random.Random,
) -> dict:
    return {
        "format": "glyph-colab-sft-v1",
        "saved_at_utc": utc_now(),
        "variant": cfg.expected_variant,
        "step": step,
        "current_step": step,
        "model": model.state_dict(),
        "model_config": asdict(model_cfg),
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict(),
        "scaler": scaler.state_dict() if scaler is not None else None,
        "train_loss": train_loss,
        "val_loss": val_loss,
        "best_val_loss": best_val_loss,
        "run_id": cfg.run_id,
        "run_config": asdict(cfg),
        "dataset_name": cfg.dataset_name,
        "base_checkpoint_sha256": base_checkpoint_sha,
        "train_dataset_sha256": train_sha,
        "val_dataset_sha256": val_sha,
        "tokenizer_path": cfg.tokenizer,
        "tokenizer_sha256": tokenizer_sha,
        "context_length": model_cfg.context_len,
        "batch_size": cfg.batch_size,
        "gradient_accumulation_steps": cfg.gradient_accumulation_steps,
        "effective_examples_per_step": cfg.batch_size * cfg.gradient_accumulation_steps,
        "effective_context_tokens_per_step": (
            cfg.batch_size * cfg.gradient_accumulation_steps * model_cfg.context_len
        ),
        "precision": cfg.precision,
        "label_mask_boundary": "i < assistant_pos",
        "rng_state": rng.getstate(),
        "torch_rng_state": torch.get_rng_state(),
        "cuda_rng_state": torch.cuda.get_rng_state_all(),
    }


def save_checkpoint(
    run_root: Path,
    name: str,
    payload: dict,
    *,
    update_latest: bool,
    update_best: bool,
    milestone_copy_dir: Path | None,
) -> dict:
    checkpoint_dir = run_root / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    target = checkpoint_dir / name
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite checkpoint: {target}")
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    with temporary.open("wb") as handle:
        torch.save(payload, handle)
        handle.flush()
        os.fsync(handle.fileno())
    validation = validate_saved_checkpoint(
        temporary,
        int(payload["current_step"]),
        str(payload["variant"]),
        str(payload["tokenizer_sha256"]),
    )
    os.replace(temporary, target)
    fsync_directory(checkpoint_dir)
    validation.update({"path": str(target), "sha256": sha256_file(target), "size": target.stat().st_size})
    if update_latest:
        atomic_pointer(target, checkpoint_dir / "latest.pt")
    if update_best:
        atomic_pointer(target, checkpoint_dir / "best.pt")
    if milestone_copy_dir is not None:
        destination = milestone_copy_dir / payload["run_id"] / "checkpoints" / target.name
        atomic_copy_verified(target, destination)
    return validation


def load_resume(
    path: Path,
    model: GPT,
    optimizer: torch.optim.Optimizer,
    scheduler,
    scaler,
    cfg: TrainingConfig,
    train_sha: str,
    val_sha: str,
    tokenizer_sha: str,
    base_checkpoint_sha: str,
    device: torch.device,
) -> tuple[int, float | None, random.Random]:
    state = load_torch(path)
    saved_cfg = state.get("run_config") or {}
    checks = {
        "variant": (state.get("variant"), cfg.expected_variant),
        "tokenizer_sha256": (state.get("tokenizer_sha256"), tokenizer_sha),
        "train_dataset_sha256": (state.get("train_dataset_sha256"), train_sha),
        "val_dataset_sha256": (state.get("val_dataset_sha256"), val_sha),
        "base_checkpoint_sha256": (state.get("base_checkpoint_sha256"), base_checkpoint_sha),
        "batch_size": (state.get("batch_size", saved_cfg.get("batch_size")), cfg.batch_size),
        "gradient_accumulation_steps": (
            state.get("gradient_accumulation_steps", saved_cfg.get("gradient_accumulation_steps")),
            cfg.gradient_accumulation_steps,
        ),
        "precision": (state.get("precision", saved_cfg.get("precision")), cfg.precision),
        "dataset_name": (state.get("dataset_name", saved_cfg.get("dataset_name")), cfg.dataset_name),
        "learning_rate": (saved_cfg.get("learning_rate"), cfg.learning_rate),
        "min_lr": (saved_cfg.get("min_lr"), cfg.min_lr),
        "warmup_steps": (saved_cfg.get("warmup_steps"), cfg.warmup_steps),
        "weight_decay": (saved_cfg.get("weight_decay"), cfg.weight_decay),
        "grad_clip": (saved_cfg.get("grad_clip"), cfg.grad_clip),
        "max_steps": (saved_cfg.get("max_steps"), cfg.max_steps),
    }
    mismatches = [f"{key}: checkpoint={actual!r}, requested={expected!r}" for key, (actual, expected) in checks.items() if actual != expected]
    if mismatches:
        raise ValueError("Resume mismatch: " + "; ".join(mismatches))
    loaded = model.load_state_dict(state["model"], strict=True)
    if loaded.missing_keys or loaded.unexpected_keys:
        raise ValueError(f"Resume state mismatch: {loaded}")
    optimizer.load_state_dict(state["optimizer"])
    for item in optimizer.state.values():
        for key, value in item.items():
            if torch.is_tensor(value):
                item[key] = value.to(device)
    scheduler.load_state_dict(state["scheduler"])
    if scaler is not None and state.get("scaler"):
        scaler.load_state_dict(state["scaler"])
    rng = random.Random(cfg.seed)
    if state.get("rng_state"):
        rng.setstate(state["rng_state"])
    if state.get("torch_rng_state") is not None:
        torch.set_rng_state(state["torch_rng_state"])
    if state.get("cuda_rng_state") is not None:
        torch.cuda.set_rng_state_all(state["cuda_rng_state"])
    return checkpoint_step(state), state.get("best_val_loss"), rng


def write_emergency(run_root: Path, reason: str, step: int, details: dict) -> None:
    payload = {
        "status": "STOPPED",
        "timestamp_utc": utc_now(),
        "reason": reason,
        "step": step,
        "details": details,
        "latest_valid_checkpoint_was_not_overwritten": True,
    }
    atomic_write_json(run_root / "reports" / "emergency_stop.json", payload)


def summary_markdown(summary: dict) -> str:
    return "\n".join(
        [
            f"# Glyph Colab SFT run: {summary['run_id']}",
            "",
            f"**Status: {summary['status']}**",
            "",
            f"- Start step: `{summary['start_step']}`",
            f"- End step: `{summary['end_step']}`",
            f"- Duration: `{summary['duration_seconds']:.1f}` seconds",
            f"- Final train loss: `{summary.get('final_train_loss')}`",
            f"- Final val loss: `{summary.get('final_val_loss')}`",
            f"- Best val loss: `{summary.get('best_val_loss')}`",
            f"- Precision: `{summary['precision']}`",
            f"- Effective examples/step: `{summary['effective_examples_per_step']}`",
            f"- Latest checkpoint: `{summary.get('latest_checkpoint')}`",
            f"- Best checkpoint: `{summary.get('best_checkpoint')}`",
            "",
            "Checkpoints were written locally and reloaded before being made visible.",
            "",
        ]
    )


def prepare(args: argparse.Namespace) -> tuple[TrainingConfig, dict]:
    cfg = TrainingConfig(
        run_id=args.run_id,
        base_checkpoint=str(resolve(args.base_checkpoint)),
        train_jsonl=str(resolve(args.train_jsonl)),
        val_jsonl=str(resolve(args.val_jsonl)),
        tokenizer=str(resolve(args.tokenizer)),
        output_dir=str(resolve(args.output_dir)),
        resume_checkpoint=str(resolve(args.resume_checkpoint)) if args.resume_checkpoint else None,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        min_lr=args.min_lr,
        warmup_steps=args.warmup_steps,
        weight_decay=args.weight_decay,
        grad_clip=args.grad_clip,
        eval_interval=args.eval_interval,
        eval_batches=args.eval_batches,
        checkpoint_interval=args.checkpoint_interval,
        log_interval=args.log_interval,
        precision=args.precision,
        save_best_on_val=args.save_best_on_val,
        seed=args.seed,
        expected_base_step=args.expected_base_step,
        expected_variant=args.expected_variant,
        expected_tokenizer_sha=args.expected_tokenizer_sha,
        dataset_name=args.dataset_name,
        milestone_copy_dir=str(resolve(args.milestone_copy_dir)) if args.milestone_copy_dir else None,
        milestone_copy_interval=args.milestone_copy_interval,
    )
    if cfg.max_steps <= 0 or cfg.batch_size <= 0 or cfg.gradient_accumulation_steps <= 0:
        raise ValueError("max_steps, batch_size and gradient_accumulation_steps must be positive")
    if cfg.learning_rate <= 0 or cfg.min_lr < 0 or cfg.min_lr > cfg.learning_rate:
        raise ValueError("Learning rate bounds are invalid")
    if cfg.precision != "fp32" and not torch.cuda.is_available():
        raise RuntimeError(f"{cfg.precision} requires CUDA")
    if cfg.precision == "bf16" and not getattr(torch.cuda, "is_bf16_supported", lambda: False)():
        raise RuntimeError("bf16 was requested but this GPU/PyTorch build does not support it")
    paths = [Path(cfg.base_checkpoint), Path(cfg.train_jsonl), Path(cfg.val_jsonl), Path(cfg.tokenizer)]
    if cfg.resume_checkpoint:
        paths.append(Path(cfg.resume_checkpoint))
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    tokenizer_sha = sha256_file(cfg.tokenizer)
    base_state = load_torch(Path(cfg.base_checkpoint), mmap=True)
    model_cfg = validate_base(base_state, cfg, tokenizer_sha)
    sp, special_ids = validate_special_tokens(Path(cfg.tokenizer))
    train_data = SFTDataset(cfg.train_jsonl, sp, model_cfg.context_len)
    val_data = SFTDataset(cfg.val_jsonl, sp, model_cfg.context_len)
    label_contract = validate_label_contract(train_data)
    details = {
        "model_config": asdict(model_cfg),
        "base_checkpoint_sha256": sha256_file(cfg.base_checkpoint),
        "train_dataset_sha256": sha256_file(cfg.train_jsonl),
        "val_dataset_sha256": sha256_file(cfg.val_jsonl),
        "tokenizer_sha256": tokenizer_sha,
        "train_examples": len(train_data.pairs),
        "val_examples": len(val_data.pairs),
        "special_token_ids": special_ids,
        "label_contract": label_contract,
        "effective_examples_per_step": cfg.batch_size * cfg.gradient_accumulation_steps,
    }
    return cfg, details


def train(cfg: TrainingConfig, details: dict) -> dict:
    global shutdown_requested
    shutdown_requested = False
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for colab_run_sft.py")
    device = torch.device("cuda")
    run_root = Path(cfg.output_dir)
    if run_root.exists() and any(run_root.iterdir()) and not cfg.resume_checkpoint:
        raise FileExistsError(f"Fresh run output is not empty: {run_root}")
    for child in ("checkpoints", "logs", "reports"):
        (run_root / child).mkdir(parents=True, exist_ok=True)
    logger = configure_logging(run_root)
    metrics_path = run_root / "logs" / "metrics.jsonl"
    run_config_path = run_root / "run_config.json"
    run_state_path = run_root / "run_state.json"
    requested_config = {**asdict(cfg), **details, "created_at_utc": utc_now()}
    if run_config_path.exists():
        if not cfg.resume_checkpoint:
            raise FileExistsError(f"Existing run config requires --resume-checkpoint: {run_config_path}")
        previous = json.loads(run_config_path.read_text(encoding="utf-8"))
        stable_keys = (
            "run_id",
            "base_checkpoint",
            "train_dataset_sha256",
            "val_dataset_sha256",
            "tokenizer_sha256",
            "batch_size",
            "gradient_accumulation_steps",
            "precision",
            "dataset_name",
            "learning_rate",
            "min_lr",
            "warmup_steps",
            "weight_decay",
            "grad_clip",
            "max_steps",
        )
        mismatches = [key for key in stable_keys if previous.get(key) != requested_config.get(key)]
        if mismatches:
            raise ValueError(f"Resume run_config mismatch for: {', '.join(mismatches)}")
        atomic_write_json(run_root / "resume_request.json", requested_config)
    else:
        atomic_write_json(run_config_path, requested_config)

    random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    torch.cuda.manual_seed_all(cfg.seed)
    base_state = load_torch(Path(cfg.base_checkpoint), mmap=True)
    model_cfg = checkpoint_config(base_state)
    model = GPT(model_cfg)
    loaded = model.load_state_dict(base_state["model"], strict=True)
    if loaded.missing_keys or loaded.unexpected_keys:
        raise ValueError(f"Base state mismatch: {loaded}")
    del base_state
    model.to(device)
    model.train()
    optimizer = build_optimizer(model, cfg)
    scheduler = build_scheduler(optimizer, cfg)
    scaler = build_scaler(cfg.precision)
    sp = load_sentencepiece(cfg.tokenizer)
    train_data = SFTDataset(cfg.train_jsonl, sp, model_cfg.context_len)
    val_data = SFTDataset(cfg.val_jsonl, sp, model_cfg.context_len)
    rng = random.Random(cfg.seed)
    start_step = 0
    best_val_loss = None
    if cfg.resume_checkpoint:
        start_step, best_val_loss, rng = load_resume(
            Path(cfg.resume_checkpoint),
            model,
            optimizer,
            scheduler,
            scaler,
            cfg,
            details["train_dataset_sha256"],
            details["val_dataset_sha256"],
            details["tokenizer_sha256"],
            details["base_checkpoint_sha256"],
            device,
        )
    if start_step >= cfg.max_steps:
        raise ValueError(f"Resume step {start_step} is already at or beyond max_steps={cfg.max_steps}")

    logger.info("Glyph Colab SFT run_id=%s start=%s target=%s", cfg.run_id, start_step, cfg.max_steps)
    logger.info(
        "device=%s gpu=%s precision=%s autocast=%s GradScaler=%s batch=%s accum=%s effective_examples=%s",
        device,
        torch.cuda.get_device_name(device),
        cfg.precision,
        cfg.precision != "fp32",
        scaler is not None,
        cfg.batch_size,
        cfg.gradient_accumulation_steps,
        cfg.batch_size * cfg.gradient_accumulation_steps,
    )
    logger.info("base=%s dataset=%s output=%s", cfg.base_checkpoint, cfg.dataset_name, run_root)
    logger.info("label_mask=i < assistant_pos prompt_masked=true end_supervised=true padding=-100")
    atomic_write_json(
        run_state_path,
        {"status": "RUNNING", "run_id": cfg.run_id, "current_step": start_step, "updated_at_utc": utc_now()},
    )

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    start_time = time.perf_counter()
    started_at = utc_now()
    step = start_step
    final_loss = None
    final_val_loss = None
    optimizer.zero_grad(set_to_none=True)
    milestone_dir = Path(cfg.milestone_copy_dir) if cfg.milestone_copy_dir else None
    saved = []
    try:
        while step < cfg.max_steps:
            micro_losses = []
            supervised_tokens = 0
            for _micro in range(cfg.gradient_accumulation_steps):
                x, labels = random_batch(train_data, cfg.batch_size, device, rng)
                supervised_tokens += int(labels.ne(-100).sum().item())
                with autocast_context(cfg.precision):
                    logits, _ = model(x)
                    loss = F.cross_entropy(
                        logits.reshape(-1, logits.size(-1)),
                        labels.reshape(-1),
                        ignore_index=-100,
                    )
                if not torch.isfinite(loss).item():
                    raise FloatingPointError(f"Non-finite loss before optimizer step {step + 1}")
                scaled_loss = loss / cfg.gradient_accumulation_steps
                if scaler is not None:
                    scaler.scale(scaled_loss).backward()
                else:
                    scaled_loss.backward()
                micro_losses.append(float(loss.detach().cpu().item()))

            if scaler is not None:
                scaler.unscale_(optimizer)
            grad_norm_before_clip = global_grad_norm(model)
            if not math.isfinite(grad_norm_before_clip):
                raise FloatingPointError(f"Non-finite gradient norm before optimizer step {step + 1}")
            clipped = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip) if cfg.grad_clip > 0 else None
            if scaler is not None:
                scaler.step(optimizer)
                scaler.update()
            else:
                optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)
            torch.cuda.synchronize(device)
            if not parameters_finite(model):
                raise FloatingPointError(f"Non-finite parameters after optimizer step {step + 1}")

            step += 1
            final_loss = sum(micro_losses) / len(micro_losses)
            elapsed = max(time.perf_counter() - start_time, 1e-9)
            metric = {
                "timestamp_utc": utc_now(),
                "step": step,
                "train_loss": final_loss,
                "learning_rate": optimizer.param_groups[0]["lr"],
                "grad_norm": grad_norm_before_clip,
                "clip_return": float(clipped.detach().cpu().item()) if torch.is_tensor(clipped) else clipped,
                "supervised_tokens": supervised_tokens,
                "optimizer_steps_per_second": (step - start_step) / elapsed,
                "cuda_memory_allocated": torch.cuda.memory_allocated(device),
                "cuda_memory_reserved": torch.cuda.memory_reserved(device),
            }
            if step <= start_step + 5 or step % cfg.log_interval == 0:
                logger.info(
                    "step=%6d loss=%.6f lr=%.3e grad_norm=%.4f supervised=%s opt_step/s=%.3f",
                    step,
                    final_loss,
                    metric["learning_rate"],
                    grad_norm_before_clip,
                    supervised_tokens,
                    metric["optimizer_steps_per_second"],
                )
                append_jsonl(metrics_path, metric)

            improved = False
            if cfg.eval_interval > 0 and step % cfg.eval_interval == 0:
                final_val_loss = evaluate(model, val_data, cfg, device, step)
                improved = best_val_loss is None or final_val_loss < best_val_loss
                if improved:
                    best_val_loss = final_val_loss
                logger.info("eval step=%6d val_loss=%.6f best=%s", step, final_val_loss, improved)
                append_jsonl(metrics_path, {**metric, "event": "eval", "val_loss": final_val_loss, "best": improved})

            payload = None
            if improved and cfg.save_best_on_val:
                payload = checkpoint_payload(
                    model,
                    optimizer,
                    scheduler,
                    scaler,
                    cfg,
                    model_cfg,
                    step,
                    final_loss,
                    final_val_loss,
                    best_val_loss,
                    details["train_dataset_sha256"],
                    details["val_dataset_sha256"],
                    details["tokenizer_sha256"],
                    details["base_checkpoint_sha256"],
                    rng,
                )
                record = save_checkpoint(
                    run_root,
                    f"best_step_{step:06d}.pt",
                    payload,
                    update_latest=False,
                    update_best=True,
                    milestone_copy_dir=milestone_dir,
                )
                saved.append(record)
                logger.info("best checkpoint validated: %s", record["path"])

            should_checkpoint = cfg.checkpoint_interval > 0 and step % cfg.checkpoint_interval == 0
            if should_checkpoint:
                if payload is None:
                    payload = checkpoint_payload(
                        model,
                        optimizer,
                        scheduler,
                        scaler,
                        cfg,
                        model_cfg,
                        step,
                        final_loss,
                        final_val_loss,
                        best_val_loss,
                        details["train_dataset_sha256"],
                        details["val_dataset_sha256"],
                        details["tokenizer_sha256"],
                        details["base_checkpoint_sha256"],
                        rng,
                    )
                copy_milestone = milestone_dir if cfg.milestone_copy_interval > 0 and step % cfg.milestone_copy_interval == 0 else None
                record = save_checkpoint(
                    run_root,
                    f"step_{step:06d}.pt",
                    payload,
                    update_latest=True,
                    update_best=False,
                    milestone_copy_dir=copy_milestone,
                )
                saved.append(record)
                logger.info("checkpoint validated: %s", record["path"])

            atomic_write_json(
                run_state_path,
                {
                    "status": "STOPPING" if shutdown_requested else "RUNNING",
                    "run_id": cfg.run_id,
                    "current_step": step,
                    "train_loss": final_loss,
                    "val_loss": final_val_loss,
                    "best_val_loss": best_val_loss,
                    "updated_at_utc": utc_now(),
                },
            )
            if shutdown_requested:
                emergency_payload = checkpoint_payload(
                    model,
                    optimizer,
                    scheduler,
                    scaler,
                    cfg,
                    model_cfg,
                    step,
                    final_loss,
                    final_val_loss,
                    best_val_loss,
                    details["train_dataset_sha256"],
                    details["val_dataset_sha256"],
                    details["tokenizer_sha256"],
                    details["base_checkpoint_sha256"],
                    rng,
                )
                record = save_checkpoint(
                    run_root,
                    f"emergency_step_{step:06d}.pt",
                    emergency_payload,
                    update_latest=False,
                    update_best=False,
                    milestone_copy_dir=milestone_dir,
                )
                saved.append(record)
                raise KeyboardInterrupt("Clean stop requested")

        final_val_loss = evaluate(model, val_data, cfg, device, step)
        if best_val_loss is None or final_val_loss < best_val_loss:
            best_val_loss = final_val_loss
            final_is_best = cfg.save_best_on_val
        else:
            final_is_best = False
        final_payload = checkpoint_payload(
            model,
            optimizer,
            scheduler,
            scaler,
            cfg,
            model_cfg,
            step,
            float(final_loss),
            final_val_loss,
            best_val_loss,
            details["train_dataset_sha256"],
            details["val_dataset_sha256"],
            details["tokenizer_sha256"],
            details["base_checkpoint_sha256"],
            rng,
        )
        record = save_checkpoint(
            run_root,
            f"final_step_{step:06d}.pt",
            final_payload,
            update_latest=True,
            update_best=final_is_best,
            milestone_copy_dir=milestone_dir,
        )
        saved.append(record)
        status = "COMPLETE"
    except KeyboardInterrupt as exc:
        status = "INTERRUPTED"
        write_emergency(run_root, "signal_or_keyboard_interrupt", step, {"message": str(exc)})
    except torch.cuda.OutOfMemoryError as exc:
        status = "FAILED"
        write_emergency(run_root, "cuda_out_of_memory", step, {"message": str(exc)})
        raise
    except Exception as exc:
        status = "FAILED"
        write_emergency(run_root, type(exc).__name__, step, {"message": str(exc)})
        raise
    finally:
        duration = time.perf_counter() - start_time
        summary = {
            "status": status,
            "run_id": cfg.run_id,
            "started_at_utc": started_at,
            "finished_at_utc": utc_now(),
            "duration_seconds": duration,
            "start_step": start_step,
            "end_step": step,
            "final_train_loss": final_loss,
            "final_val_loss": final_val_loss,
            "best_val_loss": best_val_loss,
            "precision": cfg.precision,
            "effective_examples_per_step": cfg.batch_size * cfg.gradient_accumulation_steps,
            "latest_checkpoint": str(run_root / "checkpoints/latest.pt") if (run_root / "checkpoints/latest.pt").exists() else None,
            "best_checkpoint": str(run_root / "checkpoints/best.pt") if (run_root / "checkpoints/best.pt").exists() else None,
            "saved_checkpoints": saved,
        }
        atomic_write_json(run_root / "reports" / "training_summary.json", summary)
        (run_root / "reports" / "training_summary.md").write_text(summary_markdown(summary), encoding="utf-8")
        atomic_write_json(
            run_state_path,
            {
                "status": status,
                "run_id": cfg.run_id,
                "current_step": step,
                "best_val_loss": best_val_loss,
                "updated_at_utc": utc_now(),
            },
        )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resume-safe Glyph SFT runner for Google Colab")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--base-checkpoint", required=True)
    parser.add_argument("--train-jsonl", required=True)
    parser.add_argument("--val-jsonl", required=True)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resume-checkpoint", default=None)
    parser.add_argument("--max-steps", type=int, default=400)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--min-lr", type=float, default=1e-6)
    parser.add_argument("--warmup-steps", type=int, default=10)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--grad-clip", type=float, default=0.5)
    parser.add_argument("--eval-interval", type=int, default=50)
    parser.add_argument("--eval-batches", type=int, default=20)
    parser.add_argument("--checkpoint-interval", type=int, default=100)
    parser.add_argument("--log-interval", type=int, default=5)
    parser.add_argument("--precision", choices=("fp32", "fp16", "bf16"), default="fp32")
    parser.add_argument("--save-best-on-val", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--expected-base-step", type=int, default=44000)
    parser.add_argument("--expected-variant", default="glyph-100m")
    parser.add_argument("--expected-tokenizer-sha", default=EXPECTED_TOKENIZER_SHA)
    parser.add_argument("--dataset-name", default="glyph100_sft_colab")
    parser.add_argument("--milestone-copy-dir", default=None)
    parser.add_argument("--milestone-copy-interval", type=int, default=0)
    parser.add_argument("--confirm-training", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg, details = prepare(args)
    preview = {"config": asdict(cfg), "validation": details, "training_will_run": bool(args.confirm_training and not args.dry_run)}
    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return
    if not args.confirm_training:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        raise SystemExit(CONFIRMATION_HELP)
    result = train(cfg, details)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
