#!/usr/bin/env python3
"""Supervised fine-tuning for Glyph SFT runs.

The SFT format is intentionally small and explicit:

<|user|>
instruction
<|assistant|>
response
<|end|>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import os
import random
import signal
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent))

from config import FinetuneConfig, ModelConfig
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, format_sft_text, load_jsonl, load_sentencepiece


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)


def configure_logging(log_dir: str, log_file: str | None = None) -> Path:
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
        handlers=[logging.FileHandler(target), logging.StreamHandler(sys.stdout)],
    )
    return target


@dataclass
class RunConfig:
    base: str
    resume: str | None
    train_jsonl: str
    val_jsonl: str | None
    tokenizer: str
    output: str
    log_dir: str
    device: str
    batch_size: int
    epochs: int
    max_steps: int | None
    learning_rate: float
    min_lr: float
    weight_decay: float
    grad_clip: float
    warmup_steps: int
    checkpoint_interval: int
    eval_interval: int
    val_batches: int
    log_interval: int
    seed: int
    tag: str
    context_len: int
    variant: str
    dataset_name: str
    dataset_report: str | None
    expected_base_step: int | None
    expected_tokenizer_sha: str | None
    max_loss: float


def configure_cpu_threads() -> None:
    n_threads = os.cpu_count() or 1
    if os.environ.get("TRAIN_NUM_THREADS"):
        n_threads = max(1, int(os.environ["TRAIN_NUM_THREADS"]))
    torch.set_num_threads(n_threads)
    try:
        torch.set_num_interop_threads(max(1, int(os.environ.get("TRAIN_INTEROP_THREADS", "1"))))
    except RuntimeError:
        pass
    log.info(f"CPU threading: torch_threads={torch.get_num_threads()}")


def select_device(requested: str) -> torch.device:
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
    log.error(f"Unsupported device: {requested!r}; use cpu, cuda, or auto")
    sys.exit(2)


def sync_if_needed(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def move_optimizer_state_to_device(optimizer: torch.optim.Optimizer, device: torch.device) -> None:
    if device.type == "cpu":
        return
    moved = 0
    for state in optimizer.state.values():
        for key, value in list(state.items()):
            if torch.is_tensor(value):
                state[key] = value.to(device)
                moved += 1
    log.info(f"Optimizer state tensors moved to {device}: {moved}")


class SFTDataset:
    def __init__(self, jsonl_path: str, sp, context_len: int):
        loaded = load_jsonl(jsonl_path)
        self.path = str(loaded.path)
        self.context_len = context_len
        self.pad_id = sp.pad_id()
        if self.pad_id < 0:
            self.pad_id = 0
        self.assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
        self.end_id = sp.piece_to_id(END_TOKEN)
        self.pairs: list[tuple[list[int], list[int]]] = []
        self.skipped_over_context = 0
        self.skipped_no_assistant = 0
        self.skipped_empty = 0

        for record in loaded.records:
            text = format_sft_text(record)
            ids = list(sp.encode(text, out_type=int))
            if not ids:
                self.skipped_empty += 1
                continue
            if len(ids) > context_len:
                self.skipped_over_context += 1
                continue
            pair = self._make_pair(ids)
            if pair is None:
                self.skipped_no_assistant += 1
                continue
            self.pairs.append(pair)

        if not self.pairs:
            raise ValueError(f"No usable SFT examples in {jsonl_path}")

        log.info(
            f"SFT dataset {jsonl_path}: usable={len(self.pairs):,} "
            f"skipped_over_context={self.skipped_over_context} "
            f"skipped_no_assistant={self.skipped_no_assistant} skipped_empty={self.skipped_empty}"
        )

    def _make_pair(self, ids: list[int]) -> tuple[list[int], list[int]] | None:
        if len(ids) < 2:
            return None
        x = list(ids[:-1])
        y = list(ids[1:])

        try:
            assistant_pos = x.index(self.assistant_id)
        except ValueError:
            return None

        y_masked = list(y)
        for i in range(len(y_masked)):
            if i < assistant_pos:
                y_masked[i] = -100
            if y[i] == self.pad_id:
                y_masked[i] = -100

        if all(label == -100 for label in y_masked):
            return None
        return x, y_masked

    def _batch_tensors(self, batch_idx: list[int], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
        xs_raw = [self.pairs[i][0] for i in batch_idx]
        ys_raw = [self.pairs[i][1] for i in batch_idx]
        max_len = max(len(x) for x in xs_raw)
        xs = [x + [self.pad_id] * (max_len - len(x)) for x in xs_raw]
        ys = [y + [-100] * (max_len - len(y)) for y in ys_raw]
        x = torch.tensor(xs, dtype=torch.long, device=device)
        y = torch.tensor(ys, dtype=torch.long, device=device)
        return x, y

    def iter_batches(self, batch_size: int, device: torch.device, rng: random.Random):
        indices = list(range(len(self.pairs)))
        rng.shuffle(indices)
        for start in range(0, len(indices), batch_size):
            batch_idx = indices[start : start + batch_size]
            yield self._batch_tensors(batch_idx, device)

    def random_batches(self, batch_size: int, batches: int, device: torch.device, rng: random.Random):
        for _ in range(max(1, batches)):
            idx = [rng.randrange(len(self.pairs)) for _ in range(min(batch_size, len(self.pairs)))]
            yield self._batch_tensors(idx, device)


def build_optimizer(model: GPT, run_cfg: RunConfig) -> torch.optim.Optimizer:
    decay_params = [p for _, p in model.named_parameters() if p.dim() >= 2]
    nodecay_params = [p for _, p in model.named_parameters() if p.dim() < 2]
    return torch.optim.AdamW(
        [
            {"params": decay_params, "weight_decay": run_cfg.weight_decay},
            {"params": nodecay_params, "weight_decay": 0.0},
        ],
        lr=run_cfg.learning_rate,
        betas=(0.9, 0.95),
        foreach=True,
        fused=False,
    )


def get_lr(step: int, total_steps: int, run_cfg: RunConfig) -> float:
    if step <= run_cfg.warmup_steps:
        return run_cfg.learning_rate * step / max(run_cfg.warmup_steps, 1)
    if step >= total_steps:
        return run_cfg.min_lr
    progress = (step - run_cfg.warmup_steps) / max(total_steps - run_cfg.warmup_steps, 1)
    cosine = 0.5 * (1.0 + math.cos(math.pi * progress))
    return run_cfg.min_lr + (run_cfg.learning_rate - run_cfg.min_lr) * cosine


@torch.no_grad()
def estimate_loss(
    model: GPT,
    dataset: SFTDataset,
    batch_size: int,
    device: torch.device,
    batches: int,
    rng: random.Random,
) -> float:
    was_training = model.training
    model.eval()
    losses = []
    for x, y in dataset.random_batches(batch_size, batches, device, rng):
        logits, _ = model(x)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)
        losses.append(float(loss.item()))
    if was_training:
        model.train()
    return sum(losses) / len(losses)


def sha256_file(path: str | Path) -> str | None:
    target = Path(path)
    if not target.exists() or not target.is_file():
        return None
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_step(state: dict) -> int:
    return int(state.get("current_step", state.get("step", 0)))


def checkpoint_dataset(state: dict) -> str | None:
    return state.get("dataset_name") or state.get("dataset")


def validate_base_checkpoint_state(state: dict, run_cfg: RunConfig, model_cfg: ModelConfig) -> None:
    if state.get("variant") and state.get("variant") != run_cfg.variant:
        raise ValueError(
            f"Base checkpoint variant mismatch: checkpoint={state.get('variant')!r}, "
            f"requested={run_cfg.variant!r}"
        )
    if state.get("model_config") and state["model_config"] != model_cfg.__dict__:
        raise ValueError("Base checkpoint model_config does not match reconstructed model config")
    if run_cfg.expected_base_step is not None and checkpoint_step(state) != run_cfg.expected_base_step:
        raise ValueError(
            f"Base checkpoint step mismatch: checkpoint={checkpoint_step(state)}, "
            f"expected={run_cfg.expected_base_step}"
        )
    if run_cfg.expected_tokenizer_sha and state.get("tokenizer_sha256") != run_cfg.expected_tokenizer_sha:
        raise ValueError(
            f"Base checkpoint tokenizer SHA mismatch: checkpoint={state.get('tokenizer_sha256')}, "
            f"expected={run_cfg.expected_tokenizer_sha}"
        )
    if checkpoint_dataset(state) and checkpoint_dataset(state) != "glyph100_v2_3_1":
        log.warning(f"Base checkpoint dataset is {checkpoint_dataset(state)!r}; SFT dataset is {run_cfg.dataset_name!r}")


def checkpoint_state(
    model: GPT,
    optimizer: torch.optim.Optimizer,
    step: int,
    epoch: int,
    loss: float,
    val_loss: float | None,
    model_cfg: ModelConfig,
    run_cfg: RunConfig,
) -> dict:
    metadata = {
        "phase": "sft-smoke",
        "variant": run_cfg.variant,
        "dataset_name": run_cfg.dataset_name,
        "dataset_report": run_cfg.dataset_report,
        "base_checkpoint": run_cfg.base,
        "expected_base_step": run_cfg.expected_base_step,
        "tokenizer_path": run_cfg.tokenizer,
        "tokenizer_sha256": sha256_file(run_cfg.tokenizer),
        "context_length": model_cfg.context_len,
        "batch_size": run_cfg.batch_size,
        "effective_tokens_per_step": run_cfg.batch_size * model_cfg.context_len,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {
        "phase": metadata["phase"],
        "variant": run_cfg.variant,
        "step": step,
        "current_step": step,
        "sft_step": step,
        "base_step": run_cfg.expected_base_step,
        "epoch": epoch,
        "loss": loss,
        "val_loss": val_loss,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "model_config": model_cfg.__dict__,
        "sft_config": asdict(run_cfg),
        "train_config": asdict(run_cfg),
        "dataset_name": run_cfg.dataset_name,
        "dataset_report": run_cfg.dataset_report,
        "tokenizer_path": run_cfg.tokenizer,
        "tokenizer_sha256": metadata["tokenizer_sha256"],
        "context_length": model_cfg.context_len,
        "batch_size": run_cfg.batch_size,
        "effective_tokens_per_step": metadata["effective_tokens_per_step"],
        "checkpoint_metadata": metadata,
        "special_tokens": {
            "user": USER_TOKEN,
            "assistant": ASSISTANT_TOKEN,
            "end": END_TOKEN,
        },
    }


def save_sft_checkpoint(
    model: GPT,
    optimizer: torch.optim.Optimizer,
    step: int,
    epoch: int,
    loss: float,
    val_loss: float | None,
    model_cfg: ModelConfig,
    run_cfg: RunConfig,
    tag: str | None = None,
    update_latest: bool = True,
) -> Path:
    out = Path(run_cfg.output)
    out.mkdir(parents=True, exist_ok=True)
    state = checkpoint_state(model, optimizer, step, epoch, loss, val_loss, model_cfg, run_cfg)
    if tag is None:
        path = out / f"step_{step:06d}.pt"
    else:
        path = out / f"{run_cfg.tag}-{tag}.pt"
    torch.save(state, path)

    if update_latest:
        tmp_latest = out / f"_{run_cfg.tag}-latest.tmp"
        latest = out / f"{run_cfg.tag}-latest.pt"
        torch.save(state, tmp_latest)
        tmp_latest.replace(latest)
    log.info(f"SFT checkpoint saved: {path} (loss={loss:.4f}, val_loss={val_loss})")
    return path


def write_emergency_report(run_cfg: RunConfig, step: int, epoch: int, reason: str, loss: float | None) -> Path:
    out = Path(run_cfg.log_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "emergency_stop.json"
    payload = {
        "phase": "sft-smoke",
        "variant": run_cfg.variant,
        "dataset_name": run_cfg.dataset_name,
        "step": step,
        "epoch": epoch,
        "reason": reason,
        "loss": loss,
        "latest_checkpoint_not_overwritten": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_config": asdict(run_cfg),
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def copy_checkpoint(src: Path, dest: Path) -> None:
    state = torch.load(src, map_location="cpu", weights_only=False)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    torch.save(state, tmp)
    tmp.replace(dest)


def load_model_from_base(base_path: str, device: torch.device, run_cfg: RunConfig) -> tuple[GPT, ModelConfig, int]:
    state = torch.load(base_path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config", {})
    model_cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
    validate_base_checkpoint_state(state, run_cfg, model_cfg)
    model = GPT(model_cfg).to(device)
    model.load_state_dict(state["model"])
    base_step = checkpoint_step(state)
    log.info(
        f"Loaded base checkpoint: {base_path} step={base_step} "
        f"variant={state.get('variant')} dataset={checkpoint_dataset(state)}"
    )
    return model, model_cfg, base_step


def load_sft_resume(
    path: str,
    model: GPT,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    run_cfg: RunConfig,
) -> tuple[int, int, float | None]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    if state.get("variant") and state.get("variant") != run_cfg.variant:
        raise ValueError(f"SFT resume variant mismatch: checkpoint={state.get('variant')!r}, requested={run_cfg.variant!r}")
    if state.get("dataset_name") and state.get("dataset_name") != run_cfg.dataset_name:
        raise ValueError(
            f"SFT resume dataset mismatch: checkpoint={state.get('dataset_name')!r}, requested={run_cfg.dataset_name!r}"
        )
    if run_cfg.expected_tokenizer_sha and state.get("tokenizer_sha256") != run_cfg.expected_tokenizer_sha:
        raise ValueError(
            f"SFT resume tokenizer SHA mismatch: checkpoint={state.get('tokenizer_sha256')}, "
            f"expected={run_cfg.expected_tokenizer_sha}"
        )
    model.load_state_dict(state["model"])
    if "optimizer" in state:
        optimizer.load_state_dict(state["optimizer"])
        move_optimizer_state_to_device(optimizer, device)
    step = checkpoint_step(state)
    epoch = int(state.get("epoch", 0))
    val_loss = state.get("val_loss")
    log.info(f"Resumed SFT checkpoint: {path} step={step} epoch={epoch} val_loss={val_loss}")
    return step, epoch, val_loss


_shutdown_requested = False


def _handle_signal(sig, frame) -> None:
    global _shutdown_requested
    log.info("Interrupt received; will save SFT emergency checkpoint after current step")
    _shutdown_requested = True


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


def run(args: argparse.Namespace) -> None:
    ft_defaults = FinetuneConfig()
    log_path = configure_logging(args.log_dir, args.log_file)
    run_cfg = RunConfig(
        base=args.base,
        resume=args.resume,
        train_jsonl=args.train_jsonl,
        val_jsonl=args.val_jsonl,
        tokenizer=args.tokenizer,
        output=args.output,
        log_dir=args.log_dir,
        device=args.device,
        batch_size=args.batch_size,
        epochs=args.epochs,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        min_lr=args.min_lr,
        weight_decay=args.weight_decay,
        grad_clip=args.grad_clip,
        warmup_steps=args.warmup_steps,
        checkpoint_interval=args.checkpoint_interval,
        eval_interval=args.eval_interval,
        val_batches=args.val_batches,
        log_interval=args.log_interval,
        seed=args.seed,
        tag=args.tag,
        context_len=args.context_len,
        variant=args.variant,
        dataset_name=args.dataset_name,
        dataset_report=args.dataset_report,
        expected_base_step=args.expected_base_step,
        expected_tokenizer_sha=args.expected_tokenizer_sha,
        max_loss=args.max_loss,
    )
    log.info(f"Logging to {log_path}")

    random.seed(run_cfg.seed)
    np.random.seed(run_cfg.seed)
    torch.manual_seed(run_cfg.seed)

    configure_cpu_threads()
    device = select_device(run_cfg.device)
    if device.type == "cuda":
        log.info(
            f"GPU: {torch.cuda.get_device_name(device)} | "
            f"HIP={getattr(torch.version, 'hip', None)} | torch={torch.__version__}"
        )
    else:
        log.info(f"Device: {device} | torch={torch.__version__}")

    sp = load_sentencepiece(run_cfg.tokenizer)
    tokenizer_sha = sha256_file(run_cfg.tokenizer)
    if run_cfg.expected_tokenizer_sha and tokenizer_sha != run_cfg.expected_tokenizer_sha:
        log.error(f"Tokenizer SHA mismatch: actual={tokenizer_sha}, expected={run_cfg.expected_tokenizer_sha}")
        sys.exit(2)
    log.info(
        f"Tokenizer: vocab={sp.vocab_size()} user_id={sp.piece_to_id(USER_TOKEN)} "
        f"assistant_id={sp.piece_to_id(ASSISTANT_TOKEN)} end_id={sp.piece_to_id(END_TOKEN)} sha256={tokenizer_sha}"
    )
    if min(sp.piece_to_id(USER_TOKEN), sp.piece_to_id(ASSISTANT_TOKEN), sp.piece_to_id(END_TOKEN)) < 0:
        log.error("SFT special tokens are missing from tokenizer")
        sys.exit(2)

    if run_cfg.resume:
        state = torch.load(run_cfg.resume, map_location="cpu", weights_only=False)
        cfg_dict = state.get("model_config", {})
        model_cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
        model = GPT(model_cfg).to(device)
        optimizer = build_optimizer(model, run_cfg)
        start_step, start_epoch, best_val_loss = load_sft_resume(run_cfg.resume, model, optimizer, device, run_cfg)
    else:
        model, model_cfg, base_step = load_model_from_base(run_cfg.base, device, run_cfg)
        if run_cfg.expected_base_step is None:
            run_cfg.expected_base_step = base_step
        optimizer = build_optimizer(model, run_cfg)
        start_step = 0
        start_epoch = 0
        best_val_loss = None

    if model_cfg.context_len != run_cfg.context_len:
        log.warning(f"Run context_len={run_cfg.context_len} differs from model context_len={model_cfg.context_len}")
        run_cfg.context_len = model_cfg.context_len

    train_data = SFTDataset(run_cfg.train_jsonl, sp, model_cfg.context_len)
    val_data = SFTDataset(run_cfg.val_jsonl, sp, model_cfg.context_len) if run_cfg.val_jsonl else None

    steps_per_epoch = math.ceil(len(train_data.pairs) / run_cfg.batch_size)
    planned_steps = run_cfg.epochs * steps_per_epoch
    if run_cfg.max_steps is not None:
        planned_steps = min(planned_steps, run_cfg.max_steps)
    target_step = start_step + planned_steps
    if args.eval_only:
        if not val_data:
            log.error("--eval-only requires --val-jsonl")
            sys.exit(1)
        val_loss = estimate_loss(model, val_data, run_cfg.batch_size, device, run_cfg.val_batches, random.Random(run_cfg.seed + 99))
        log.info(f"sft eval_only step={start_step} | val_loss={val_loss:.4f}")
        return

    log.info("=" * 72)
    log.info(f"Starting {run_cfg.variant} SFT smoke")
    log.info(f"Base checkpoint: {run_cfg.base} | expected_base_step={run_cfg.expected_base_step}")
    log.info(f"Output: {run_cfg.output} | dataset={run_cfg.dataset_name}")
    log.info(f"Train examples: {len(train_data.pairs):,} | Val examples: {len(val_data.pairs) if val_data else 0:,}")
    log.info(f"Steps per epoch: {steps_per_epoch:,} | Planned optimizer steps this run: {planned_steps:,}")
    log.info(f"Run config: {asdict(run_cfg)}")
    log.info("=" * 72)

    rng = random.Random(run_cfg.seed + start_step)
    eval_rng = random.Random(run_cfg.seed + 10_000)
    model.train()
    running_loss = 0.0
    running_steps = 0
    running_tokens = 0
    t0 = time.perf_counter()
    loss_val = float("nan")
    val_loss = best_val_loss
    global_step = start_step
    last_epoch = start_epoch

    for epoch_offset in range(run_cfg.epochs):
        epoch = start_epoch + epoch_offset + 1
        last_epoch = epoch
        for x, y in train_data.iter_batches(run_cfg.batch_size, device, rng):
            if global_step >= target_step:
                break

            global_step += 1
            lr = get_lr(global_step - start_step, planned_steps, run_cfg)
            for pg in optimizer.param_groups:
                pg["lr"] = lr

            logits, _ = model(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)
            if not torch.isfinite(loss):
                log.error(f"Non-finite SFT loss at step {global_step}: {loss.item()}")
                write_emergency_report(run_cfg, global_step, epoch, "non_finite_loss", float("nan"))
                save_sft_checkpoint(
                    model,
                    optimizer,
                    global_step,
                    epoch,
                    float("nan"),
                    val_loss,
                    model_cfg,
                    run_cfg,
                    tag="nan",
                    update_latest=False,
                )
                sys.exit(2)
            if run_cfg.max_loss > 0 and float(loss.item()) > run_cfg.max_loss:
                log.error(f"SFT loss exceeded max_loss at step {global_step}: {loss.item():.4f} > {run_cfg.max_loss:.4f}")
                write_emergency_report(run_cfg, global_step, epoch, "loss_exceeded_max_loss", float(loss.item()))
                sys.exit(2)

            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            if run_cfg.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), run_cfg.grad_clip)
            optimizer.step()
            sync_if_needed(device)

            loss_val = float(loss.item())
            running_loss += loss_val
            running_steps += 1
            running_tokens += int(x.numel())

            if global_step % run_cfg.log_interval == 0:
                elapsed = max(time.perf_counter() - t0, 1e-9)
                log.info(
                    f"sft step={global_step:6d} | epoch={epoch} | loss={running_loss / running_steps:.4f} "
                    f"| lr={lr:.2e} | tok/s={running_tokens / elapsed:,.0f}"
                )
                running_loss = 0.0
                running_steps = 0
                running_tokens = 0
                t0 = time.perf_counter()

            if val_data and run_cfg.eval_interval > 0 and global_step % run_cfg.eval_interval == 0:
                val_loss = estimate_loss(model, val_data, run_cfg.batch_size, device, run_cfg.val_batches, eval_rng)
                log.info(f"sft eval step={global_step:6d} | val_loss={val_loss:.4f} | batches={run_cfg.val_batches}")
                if best_val_loss is None or val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_path = save_sft_checkpoint(
                        model, optimizer, global_step, epoch, loss_val, val_loss, model_cfg, run_cfg, tag="best"
                    )
                    copy_checkpoint(best_path, Path(run_cfg.output) / f"{run_cfg.tag}-best.pt")

            if run_cfg.checkpoint_interval > 0 and global_step % run_cfg.checkpoint_interval == 0:
                save_sft_checkpoint(model, optimizer, global_step, epoch, loss_val, val_loss, model_cfg, run_cfg)

            if _shutdown_requested:
                save_sft_checkpoint(model, optimizer, global_step, epoch, loss_val, val_loss, model_cfg, run_cfg, tag="emergency")
                log.info("SFT stopped cleanly after emergency checkpoint.")
                sys.exit(0)

        if global_step >= target_step:
            break

    if val_data:
        val_loss = estimate_loss(model, val_data, run_cfg.batch_size, device, run_cfg.val_batches, eval_rng)
        log.info(f"sft final_eval step={global_step:6d} | val_loss={val_loss:.4f} | batches={run_cfg.val_batches}")
        if best_val_loss is None or val_loss < best_val_loss:
            best_val_loss = val_loss
            best_path = save_sft_checkpoint(model, optimizer, global_step, last_epoch, loss_val, val_loss, model_cfg, run_cfg, tag="best")
            copy_checkpoint(best_path, Path(run_cfg.output) / f"{run_cfg.tag}-best.pt")

    final_path = save_sft_checkpoint(model, optimizer, global_step, last_epoch, loss_val, val_loss, model_cfg, run_cfg, tag="final")
    copy_checkpoint(final_path, Path(run_cfg.output) / f"{run_cfg.tag}-final.pt")
    log.info(f"SFT complete. final={Path(run_cfg.output) / f'{run_cfg.tag}-final.pt'}")


def parse_args() -> argparse.Namespace:
    ft_cfg = FinetuneConfig()
    parser = argparse.ArgumentParser(description="Supervised fine-tune Glyph")
    parser.add_argument("--base", default="checkpoints/final.pt", help="Base Glyph checkpoint")
    parser.add_argument("--resume", default=None, help="Resume SFT checkpoint")
    parser.add_argument("--train-jsonl", default="data/sft/processed/sft_v0_train.jsonl")
    parser.add_argument("--val-jsonl", default="data/sft/processed/sft_v0_val.jsonl")
    parser.add_argument("--dataset-jsonl", default=None, help="Backward-compatible alias for --train-jsonl")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--output", default="checkpoints/sft-v0")
    parser.add_argument("--log-dir", default="logs/sft-v0")
    parser.add_argument("--log-file", default=None)
    parser.add_argument("--device", default=os.environ.get("TRAIN_DEVICE", "cpu"))
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--min-lr", type=float, default=2e-6)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--grad-clip", type=float, default=1.0)
    parser.add_argument("--warmup-steps", type=int, default=10)
    parser.add_argument("--checkpoint-interval", type=int, default=50)
    parser.add_argument("--eval-interval", type=int, default=25)
    parser.add_argument("--val-batches", type=int, default=10)
    parser.add_argument("--log-interval", type=int, default=5)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--tag", default="glyph-27m-sft-v0")
    parser.add_argument("--context-len", type=int, default=ModelConfig.context_len)
    parser.add_argument("--variant", default=os.environ.get("GLYPH_MODEL_VARIANT", "glyph-27m"))
    parser.add_argument("--dataset-name", default="sft_v0")
    parser.add_argument("--dataset-report", default=None)
    parser.add_argument("--expected-base-step", type=int, default=None)
    parser.add_argument("--expected-tokenizer-sha", default=None)
    parser.add_argument("--max-loss", type=float, default=20.0)
    parser.add_argument("--eval-only", action="store_true")
    args = parser.parse_args()
    if args.dataset_jsonl:
        args.train_jsonl = args.dataset_jsonl
    if args.epochs <= 0:
        parser.error("--epochs must be positive")
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.max_steps is not None and args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    return args


def main() -> None:
    run(parse_args())


if __name__ == "__main__":
    main()
