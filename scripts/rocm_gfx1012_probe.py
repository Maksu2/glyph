#!/usr/bin/env python3
"""Synthetic ROCm/HIP smoke test for Glyph-27M on RDNA1 gfx1012."""
import argparse
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from model import GPT


def main():
    parser = argparse.ArgumentParser(description="Probe Glyph-27M forward/backward on ROCm gfx1012")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--context-len", type=int, default=None)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("torch.cuda.is_available() is false; ROCm/HIP GPU is not available")

    cfg = ModelConfig(dropout=0.0)
    if args.context_len is not None:
        cfg.context_len = args.context_len

    device = torch.device("cuda")
    print(f"torch={torch.__version__} hip={getattr(torch.version, 'hip', None)}")
    print(f"gpu={torch.cuda.get_device_name(0)}")
    print(f"batch_size={args.batch_size} context_len={cfg.context_len} steps={args.steps}")

    torch.manual_seed(123)
    model = GPT(cfg).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, foreach=True, fused=False)

    measured = []
    for step in range(args.steps):
        t0 = time.perf_counter()
        idx = torch.randint(0, cfg.vocab_size, (args.batch_size, cfg.context_len), device=device)
        target = torch.randint(0, cfg.vocab_size, (args.batch_size, cfg.context_len), device=device)
        _, loss = model(idx, target)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        torch.cuda.synchronize()
        dt = time.perf_counter() - t0
        tokens = args.batch_size * cfg.context_len
        if step > 0:
            measured.append(dt)
        print(
            f"step={step} loss={loss.item():.4f} sec={dt:.3f} "
            f"tok/s={tokens / dt:,.0f} mem={torch.cuda.memory_allocated() / 1024**2:.1f}MiB",
            flush=True,
        )

    if measured:
        avg = sum(measured) / len(measured)
        tokens = args.batch_size * cfg.context_len
        print(f"avg_excluding_warmup sec={avg:.3f} tok/s={tokens / avg:,.0f}")


if __name__ == "__main__":
    main()
