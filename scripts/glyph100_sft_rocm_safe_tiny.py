#!/usr/bin/env python3
"""ROCm safe-mode tiny SFT stability test for Glyph-100M.

This is intentionally separate from regular finetune.py. It is a backend
stability probe: fp32, no autocast, no GradScaler, explicit norm/stat logging,
and immediate stop on non-finite loss/logits/gradients/parameters.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from finetune import SFTDataset
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece


log = logging.getLogger("glyph100_rocm_safe_tiny")
_shutdown_requested = False


@dataclass
class RunConfig:
    base: str
    train_jsonl: str
    val_jsonl: str | None
    tokenizer: str
    output: str
    log_dir: str
    log_file: str
    variant: str
    dataset_name: str
    expected_base_step: int
    expected_tokenizer_sha: str
    batch_size: int
    gradient_accumulation_steps: int
    max_steps: int
    learning_rate: float
    weight_decay: float
    grad_clip: float
    eval_interval: int
    val_batches: int
    checkpoint_interval: int
    save_best_on_val: bool
    log_interval: int
    seed: int
    tag: str
    pass_name: str


def configure_logging(log_dir: str, log_file: str) -> Path:
    target = Path(log_dir) / log_file
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


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def handle_signal(sig, frame) -> None:
    global _shutdown_requested
    log.warning("Signal received; will write emergency checkpoint after current step")
    _shutdown_requested = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        raise SystemExit("ROCm/CUDA requested but torch.cuda.is_available() is false")
    return torch.device("cuda")


def global_param_norm(model: GPT) -> float:
    total = torch.zeros((), device=next(model.parameters()).device)
    with torch.no_grad():
        for param in model.parameters():
            total = total + param.detach().float().pow(2).sum()
    return float(torch.sqrt(total).detach().cpu().item())


def global_grad_norm(model: GPT) -> float:
    total = torch.zeros((), device=next(model.parameters()).device)
    found = False
    with torch.no_grad():
        for param in model.parameters():
            if param.grad is not None:
                found = True
                total = total + param.grad.detach().float().pow(2).sum()
    if not found:
        return 0.0
    return float(torch.sqrt(total).detach().cpu().item())


def params_are_finite(model: GPT) -> bool:
    with torch.no_grad():
        for param in model.parameters():
            if not torch.isfinite(param).all().item():
                return False
    return True


def build_optimizer(model: GPT, cfg: RunConfig) -> torch.optim.Optimizer:
    decay_params = [p for _, p in model.named_parameters() if p.dim() >= 2]
    nodecay_params = [p for _, p in model.named_parameters() if p.dim() < 2]
    return torch.optim.AdamW(
        [
            {"params": decay_params, "weight_decay": cfg.weight_decay},
            {"params": nodecay_params, "weight_decay": 0.0},
        ],
        lr=cfg.learning_rate,
        betas=(0.9, 0.95),
        foreach=False,
        fused=False,
    )


def load_base(cfg: RunConfig, device: torch.device) -> tuple[GPT, ModelConfig, dict]:
    state = torch.load(cfg.base, map_location="cpu", weights_only=False)
    if state.get("variant") != cfg.variant:
        raise ValueError(f"variant mismatch: checkpoint={state.get('variant')!r}, expected={cfg.variant!r}")
    step = int(state.get("current_step", state.get("step", 0)))
    if step != cfg.expected_base_step:
        raise ValueError(f"base step mismatch: checkpoint={step}, expected={cfg.expected_base_step}")
    if state.get("tokenizer_sha256") != cfg.expected_tokenizer_sha:
        raise ValueError(
            f"tokenizer sha mismatch in checkpoint: {state.get('tokenizer_sha256')} != {cfg.expected_tokenizer_sha}"
        )
    model_cfg = ModelConfig(
        **{k: v for k, v in state.get("model_config", {}).items() if k in ModelConfig.__dataclass_fields__}
    )
    model = GPT(model_cfg).to(device)
    model.load_state_dict(state["model"])
    return model, model_cfg, state


def save_checkpoint(
    model: GPT,
    optimizer: torch.optim.Optimizer,
    step: int,
    loss: float,
    val_loss: float | None,
    model_cfg: ModelConfig,
    cfg: RunConfig,
    reason: str,
    update_latest: bool,
    fixed_name: str | None = None,
) -> Path:
    out = Path(cfg.output)
    out.mkdir(parents=True, exist_ok=True)
    state = {
        "phase": "sft-rocm-safe-tiny",
        "variant": cfg.variant,
        "step": step,
        "current_step": step,
        "sft_step": step,
        "base_step": cfg.expected_base_step,
        "loss": loss,
        "val_loss": val_loss,
        "reason": reason,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "model_config": model_cfg.__dict__,
        "train_config": asdict(cfg),
        "dataset_name": cfg.dataset_name,
        "base_checkpoint": cfg.base,
        "tokenizer_path": cfg.tokenizer,
        "tokenizer_sha256": sha256_file(cfg.tokenizer),
        "batch_size": cfg.batch_size,
        "gradient_accumulation_steps": cfg.gradient_accumulation_steps,
        "effective_examples_per_step": cfg.batch_size * cfg.gradient_accumulation_steps,
        "effective_tokens_per_step": cfg.batch_size * cfg.gradient_accumulation_steps * model_cfg.context_len,
        "special_tokens": {"user": USER_TOKEN, "assistant": ASSISTANT_TOKEN, "end": END_TOKEN},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    path = out / fixed_name if fixed_name else out / f"{cfg.tag}-{reason}-step_{step:06d}.pt"
    torch.save(state, path)
    if update_latest:
        tmp = out / f"_{cfg.tag}-latest.tmp"
        latest = out / f"{cfg.tag}-latest.pt"
        torch.save(state, tmp)
        tmp.replace(latest)
    return path


def write_emergency(cfg: RunConfig, step: int, reason: str, details: dict) -> Path:
    path = Path(cfg.log_dir) / f"emergency_{cfg.pass_name}.json"
    payload = {
        "phase": "sft-rocm-safe-tiny",
        "pass_name": cfg.pass_name,
        "variant": cfg.variant,
        "dataset_name": cfg.dataset_name,
        "step": step,
        "reason": reason,
        "details": details,
        "latest_checkpoint_not_overwritten": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_config": asdict(cfg),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


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
        losses.append(float(loss.detach().cpu().item()))
    if was_training:
        model.train()
    return sum(losses) / len(losses)


def finite_or_stop(value: torch.Tensor, name: str, cfg: RunConfig, step: int, details: dict) -> None:
    if not torch.isfinite(value).all().item():
        write_emergency(cfg, step, f"non_finite_{name}", details)
        raise RuntimeError(f"non-finite {name} at step {step}")


def run(args: argparse.Namespace) -> None:
    cfg = RunConfig(**vars(args))
    log_path = configure_logging(cfg.log_dir, cfg.log_file)
    os.environ.setdefault("HIP_VISIBLE_DEVICES", os.environ.get("HIP_VISIBLE_DEVICES", "0"))
    torch.set_num_threads(max(1, int(os.environ.get("TRAIN_NUM_THREADS", "2"))))
    random.seed(cfg.seed)
    np.random.seed(cfg.seed)
    torch.manual_seed(cfg.seed)
    device = select_device()
    log.info("Logging to %s", log_path)
    log.info("torch=%s hip=%s device=%s", torch.__version__, getattr(torch.version, "hip", None), torch.cuda.get_device_name(device))
    log.info("autocast=disabled mixed_precision=disabled grad_scaler=disabled dtype=fp32")

    tokenizer_sha = sha256_file(cfg.tokenizer)
    if tokenizer_sha != cfg.expected_tokenizer_sha:
        raise ValueError(f"tokenizer SHA mismatch: {tokenizer_sha} != {cfg.expected_tokenizer_sha}")
    sp = load_sentencepiece(cfg.tokenizer)
    if min(sp.piece_to_id(USER_TOKEN), sp.piece_to_id(ASSISTANT_TOKEN), sp.piece_to_id(END_TOKEN)) < 0:
        raise ValueError("SFT special tokens missing from tokenizer")
    train_data = SFTDataset(cfg.train_jsonl, sp, 512)
    val_data = SFTDataset(cfg.val_jsonl or cfg.train_jsonl, sp, 512)
    model, model_cfg, base_state = load_base(cfg, device)
    if model_cfg.context_len != 512:
        raise ValueError(f"expected context_len 512, got {model_cfg.context_len}")
    optimizer = build_optimizer(model, cfg)
    rng = random.Random(cfg.seed)
    eval_rng = random.Random(cfg.seed + 1000)
    model.train()
    log.info("=" * 72)
    log.info("ROCm safe tiny SFT pass=%s max_steps=%s batch=%s accum=%s lr=%s grad_clip=%s", cfg.pass_name, cfg.max_steps, cfg.batch_size, cfg.gradient_accumulation_steps, cfg.learning_rate, cfg.grad_clip)
    log.info(
        "base=%s base_step=%s dataset=%s train_usable=%s val_usable=%s output=%s",
        cfg.base,
        cfg.expected_base_step,
        cfg.dataset_name,
        len(train_data.pairs),
        len(val_data.pairs),
        cfg.output,
    )
    log.info("=" * 72)

    step = 0
    val_loss: float | None = None
    best_val_loss: float | None = None
    running_loss = 0.0
    running_tokens = 0
    running_micro = 0
    t0 = time.perf_counter()
    batch_iter = train_data.iter_batches(cfg.batch_size, device, rng)
    last_details: dict = {}
    optimizer.zero_grad(set_to_none=True)
    while step < cfg.max_steps:
        micro_losses = []
        logits_stats = []
        for micro in range(cfg.gradient_accumulation_steps):
            try:
                x, y = next(batch_iter)
            except StopIteration:
                batch_iter = train_data.iter_batches(cfg.batch_size, device, rng)
                x, y = next(batch_iter)
            logits, _ = model(x)
            finite_or_stop(logits, "logits", cfg, step + 1, last_details)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y.view(-1), ignore_index=-100)
            finite_or_stop(loss, "loss", cfg, step + 1, last_details)
            (loss / cfg.gradient_accumulation_steps).backward()
            micro_losses.append(float(loss.detach().cpu().item()))
            logits_det = logits.detach().float()
            logits_stats.append(
                {
                    "min": float(logits_det.min().cpu().item()),
                    "max": float(logits_det.max().cpu().item()),
                    "mean": float(logits_det.mean().cpu().item()),
                }
            )
            running_tokens += int(x.numel())
            running_micro += 1

        step += 1
        raw_grad_norm = global_grad_norm(model)
        if not math.isfinite(raw_grad_norm):
            write_emergency(cfg, step, "non_finite_grad_norm", {"grad_norm": raw_grad_norm})
            save_checkpoint(model, optimizer, step, float("nan"), val_loss, model_cfg, cfg, "nan", update_latest=False)
            raise RuntimeError(f"non-finite grad norm at step {step}")
        clipped_norm = None
        if cfg.grad_clip > 0:
            clipped = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
            clipped_norm = float(clipped.detach().cpu().item()) if torch.is_tensor(clipped) else float(clipped)
        optimizer.step()
        torch.cuda.synchronize(device)
        optimizer.zero_grad(set_to_none=True)
        if not params_are_finite(model):
            details = {"raw_grad_norm": raw_grad_norm, "clipped_norm": clipped_norm}
            write_emergency(cfg, step, "non_finite_parameters_after_step", details)
            save_checkpoint(model, optimizer, step, float("nan"), val_loss, model_cfg, cfg, "nan", update_latest=False)
            raise RuntimeError(f"non-finite parameters after optimizer step {step}")

        loss_value = sum(micro_losses) / len(micro_losses)
        running_loss += loss_value
        last_logits = logits_stats[-1]
        param_norm = global_param_norm(model) if step % cfg.log_interval == 0 or step <= 5 else None
        last_details = {
            "step": step,
            "loss": loss_value,
            "raw_grad_norm": raw_grad_norm,
            "clipped_norm": clipped_norm,
            "param_norm": param_norm,
            "logits": last_logits,
        }
        if step <= 5 or step % cfg.log_interval == 0:
            elapsed = max(time.perf_counter() - t0, 1e-9)
            log.info(
                "safe step=%5d | loss=%.6f | avg_loss=%.6f | grad_norm=%.6f | clip_return=%s | param_norm=%s | logits[min=%.3f max=%.3f mean=%.3f] | tok/s=%.0f",
                step,
                loss_value,
                running_loss / step,
                raw_grad_norm,
                f"{clipped_norm:.6f}" if clipped_norm is not None else "none",
                f"{param_norm:.3f}" if param_norm is not None else "skip",
                last_logits["min"],
                last_logits["max"],
                last_logits["mean"],
                running_tokens / elapsed,
            )
        if cfg.eval_interval > 0 and step % cfg.eval_interval == 0:
            val_loss = estimate_loss(model, val_data, cfg.batch_size, device, cfg.val_batches, eval_rng)
            log.info("safe eval step=%5d | val_loss=%.6f | batches=%s", step, val_loss, cfg.val_batches)
            if cfg.save_best_on_val and (best_val_loss is None or val_loss < best_val_loss):
                best_val_loss = val_loss
                path = save_checkpoint(
                    model,
                    optimizer,
                    step,
                    loss_value,
                    val_loss,
                    model_cfg,
                    cfg,
                    "best",
                    update_latest=False,
                    fixed_name=f"{cfg.tag}-best.pt",
                )
                log.info("safe best checkpoint updated: %s (best_val_loss=%.6f)", path, best_val_loss)
        if cfg.checkpoint_interval > 0 and step % cfg.checkpoint_interval == 0:
            path = save_checkpoint(model, optimizer, step, loss_value, val_loss, model_cfg, cfg, f"step_{step:06d}", update_latest=True)
            log.info("safe checkpoint saved: %s", path)
        if _shutdown_requested:
            path = save_checkpoint(model, optimizer, step, loss_value, val_loss, model_cfg, cfg, "emergency", update_latest=False)
            log.warning("safe interrupted, emergency checkpoint saved: %s", path)
            return

    val_loss = estimate_loss(model, val_data, cfg.batch_size, device, cfg.val_batches, eval_rng)
    if cfg.save_best_on_val and (best_val_loss is None or val_loss < best_val_loss):
        best_val_loss = val_loss
        best_path = save_checkpoint(
            model,
            optimizer,
            step,
            loss_value,
            val_loss,
            model_cfg,
            cfg,
            "best",
            update_latest=False,
            fixed_name=f"{cfg.tag}-best.pt",
        )
        log.info("safe best checkpoint updated: %s (best_val_loss=%.6f)", best_path, best_val_loss)
    path = save_checkpoint(model, optimizer, step, loss_value, val_loss, model_cfg, cfg, "final", update_latest=True)
    log.info("safe final_eval step=%5d | val_loss=%.6f | batches=%s", step, val_loss, cfg.val_batches)
    log.info("safe complete final=%s", path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Glyph-100M ROCm safe-mode tiny SFT test")
    parser.add_argument("--base", default="checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt")
    parser.add_argument("--train-jsonl", default="data/sft/processed/glyph100_sft_tiny_overfit_fixedmask_train.jsonl")
    parser.add_argument("--val-jsonl", default=None)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--output", default="checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe")
    parser.add_argument("--log-dir", default="logs/glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe")
    parser.add_argument("--log-file", default="safe50.log")
    parser.add_argument("--variant", default="glyph-100m")
    parser.add_argument("--dataset-name", default="glyph100_sft_tiny_overfit_fixedmask")
    parser.add_argument("--expected-base-step", type=int, default=44000)
    parser.add_argument("--expected-tokenizer-sha", default="21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--learning-rate", type=float, default=1e-5)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--grad-clip", type=float, default=0.5)
    parser.add_argument("--eval-interval", type=int, default=10)
    parser.add_argument("--val-batches", type=int, default=16)
    parser.add_argument("--checkpoint-interval", type=int, default=50)
    parser.add_argument("--save-best-on-val", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--log-interval", type=int, default=1)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--tag", default="glyph-100m-v2_3_1-44k-sft-tiny-overfit-rocm-fixedmask-safe")
    parser.add_argument("--pass-name", default="safe50")
    args = parser.parse_args()
    if args.batch_size <= 0:
        parser.error("--batch-size must be positive")
    if args.gradient_accumulation_steps <= 0:
        parser.error("--gradient-accumulation-steps must be positive")
    if args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    return args


if __name__ == "__main__":
    run(parse_args())
