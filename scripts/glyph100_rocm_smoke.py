#!/usr/bin/env python3
"""Synthetic ROCm smoke test for Glyph-100M.

Runs init, forward, backward, optimizer step, batch sweep and a checkpoint
save/load test. It does not use real datasets and does not start pretraining.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_model_config, model_variant_metadata
from model import GPT


def read_rocm_smi() -> dict:
    candidates = [
        ["rocm-smi", "--showtemp", "--showmemuse", "--json"],
        ["/opt/rocm/bin/rocm-smi", "--showtemp", "--showmemuse", "--json"],
    ]
    for cmd in candidates:
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=10)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if proc.returncode != 0 or not proc.stdout.strip():
            continue
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"raw": proc.stdout.strip()[-2000:]}
    return {}


def rss_mb() -> float | None:
    try:
        pages = int(Path("/proc/self/statm").read_text().split()[1])
        return pages * os.sysconf("SC_PAGE_SIZE") / 1024**2
    except Exception:
        return None


def run_one_batch(
    batch_size: int,
    steps: int,
    gradient_accumulation_steps: int,
    save_checkpoint: bool,
    out_dir: Path,
) -> dict:
    cfg = get_model_config("glyph-100m", dropout=0.1)
    device = torch.device("cuda")
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)
    torch.manual_seed(1000 + batch_size)
    torch.cuda.manual_seed_all(1000 + batch_size)

    result = {
        "batch_size": batch_size,
        "context_len": cfg.context_len,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "tokens_per_microstep": batch_size * cfg.context_len,
        "tokens_per_step": batch_size * cfg.context_len * gradient_accumulation_steps,
        "ok": False,
        "nan": False,
        "error": None,
        "steps": [],
        "checkpoint_save_load_ok": None,
        "rocm_smi_before": read_rocm_smi(),
    }
    started = time.perf_counter()
    try:
        model = GPT(cfg).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4, betas=(0.9, 0.95), weight_decay=0.1, foreach=True, fused=False)
        model.train()
        for step in range(steps):
            t0 = time.perf_counter()
            optimizer.zero_grad(set_to_none=True)
            step_loss = 0.0
            for micro_step in range(gradient_accumulation_steps):
                x = torch.randint(0, cfg.vocab_size, (batch_size, cfg.context_len), device=device)
                y = torch.randint(0, cfg.vocab_size, (batch_size, cfg.context_len), device=device)
                _, loss = model(x, y)
                if not torch.isfinite(loss.detach()):
                    result["nan"] = True
                step_loss += float(loss.detach().item())
                (loss / gradient_accumulation_steps).backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            torch.cuda.synchronize(device)
            elapsed = time.perf_counter() - t0
            loss_value = step_loss / gradient_accumulation_steps
            result["steps"].append(
                {
                    "step": step,
                    "loss": loss_value,
                    "seconds": elapsed,
                    "tokens_per_second": (batch_size * cfg.context_len * gradient_accumulation_steps) / elapsed if elapsed > 0 else None,
                    "allocated_mib": torch.cuda.memory_allocated(device) / 1024**2,
                    "reserved_mib": torch.cuda.memory_reserved(device) / 1024**2,
                    "max_allocated_mib": torch.cuda.max_memory_allocated(device) / 1024**2,
                    "rss_mib": rss_mb(),
                }
            )

        if save_checkpoint:
            out_dir.mkdir(parents=True, exist_ok=True)
            ckpt = out_dir / "glyph100_smoke_checkpoint.pt"
            torch.save(
                {
                    "model_config": asdict(cfg),
                    "model": model.state_dict(),
                    "smoke_test": True,
                    "batch_size": batch_size,
                    "gradient_accumulation_steps": gradient_accumulation_steps,
                    "tokens_per_step": batch_size * cfg.context_len * gradient_accumulation_steps,
                },
                ckpt,
            )
            state = torch.load(ckpt, map_location="cpu", weights_only=False)
            model2 = GPT(cfg)
            model2.load_state_dict(state["model"])
            result["checkpoint_path"] = str(ckpt)
            result["checkpoint_size_bytes"] = ckpt.stat().st_size
            result["checkpoint_save_load_ok"] = True

        measured = result["steps"][1:] if len(result["steps"]) > 1 else result["steps"]
        avg_seconds = sum(row["seconds"] for row in measured) / max(1, len(measured))
        result["avg_seconds_excluding_warmup"] = avg_seconds
        result["avg_tokens_per_second_excluding_warmup"] = (
            batch_size * cfg.context_len * gradient_accumulation_steps
        ) / avg_seconds if avg_seconds > 0 else None
        result["ok"] = not result["nan"]
    except RuntimeError as exc:
        result["error"] = str(exc).splitlines()[0][:500]
        if "out of memory" in str(exc).lower():
            result["oom"] = True
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
    finally:
        result["duration_seconds"] = time.perf_counter() - started
        result["rocm_smi_after"] = read_rocm_smi()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Glyph-100M ROCm smoke test")
    parser.add_argument("--out", default="reports/glyph100_rocm_smoke.json")
    parser.add_argument("--batches", default="4,8,16,32")
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--no-checkpoint", action="store_true")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise SystemExit("torch.cuda.is_available() is false; ROCm/HIP GPU is not available")

    out = Path(args.out)
    batches = [int(item.strip()) for item in args.batches.split(",") if item.strip()]
    meta = model_variant_metadata("glyph-100m")
    payload = {
        "variant": "glyph-100m",
        "model": meta,
        "torch": torch.__version__,
        "hip": getattr(torch.version, "hip", None),
        "gpu": torch.cuda.get_device_name(0),
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "batches": [],
    }
    print(f"torch={payload['torch']} hip={payload['hip']} gpu={payload['gpu']}")
    for index, batch in enumerate(batches):
        print(f"=== batch {batch} ===", flush=True)
        result = run_one_batch(
            batch,
            args.steps,
            args.gradient_accumulation_steps,
            save_checkpoint=(index == 0 and not args.no_checkpoint),
            out_dir=out.parent,
        )
        payload["batches"].append(result)
        status = "ok" if result["ok"] else "fail"
        tps = result.get("avg_tokens_per_second_excluding_warmup")
        print(f"batch={batch} status={status} tok/s={tps if tps else '—'} error={result.get('error')}")
        if not result["ok"] and result.get("oom"):
            print("OOM reached; stopping larger batch sweep.")
            break

    ok_batches = [row["batch_size"] for row in payload["batches"] if row["ok"]]
    payload["max_ok_batch_size"] = max(ok_batches) if ok_batches else None
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps({"max_ok_batch_size": payload["max_ok_batch_size"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
