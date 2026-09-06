#!/usr/bin/env python3
"""Generate fixed prompt samples from the local Glyph-27M checkpoint."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import ModelConfig
from model import GPT
from generate import load_tokenizer, find_latest_checkpoint


def read_jsonl(path: Path) -> list[dict]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return items


def load_checkpoint(path: Path) -> tuple[GPT, ModelConfig, dict]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config", {})
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
    model = GPT(cfg)
    model.load_state_dict(state["model"])
    model.eval()
    return model, cfg, state


def atomic_write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Glyph-27M samples for fixed eval prompts")
    parser.add_argument("--checkpoint", default="checkpoints/latest.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--prompts", default="eval/prompts.jsonl")
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=120)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--repetition-penalty", type=float, default=1.0)
    parser.add_argument("--no-repeat-ngram-size", type=int, default=0)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args()

    threads = int(os.environ.get("GLYPH_EVAL_THREADS", os.environ.get("MINIGPT_EVAL_THREADS", "2")))
    torch.set_num_threads(max(1, threads))

    checkpoint = Path(args.checkpoint)
    if args.checkpoint == "latest":
        found = find_latest_checkpoint("checkpoints")
        if not found:
            raise SystemExit("No checkpoint found")
        checkpoint = Path(found)
    if not checkpoint.exists():
        raise SystemExit(f"Checkpoint not found: {checkpoint}")

    prompts = read_jsonl(Path(args.prompts))
    if args.limit > 0:
        prompts = prompts[: args.limit]

    torch.manual_seed(args.seed)
    model, cfg, state = load_checkpoint(checkpoint)
    sp = load_tokenizer(args.tokenizer)
    top_k = args.top_k if args.top_k > 0 else None
    run_id = os.environ.get("GEMMA4_RUN_ID") or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    generated_at = datetime.now(timezone.utc).isoformat()

    rows = []
    for item in prompts:
        prompt = item["prompt"]
        prompt_ids = sp.encode(prompt, out_type=int)
        if not prompt_ids:
            text = ""
        else:
            idx = torch.tensor([prompt_ids], dtype=torch.long)
            with torch.no_grad():
                out = model.generate(
                    idx,
                    max_new_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_k=top_k,
                    top_p=args.top_p,
                    repetition_penalty=args.repetition_penalty,
                    no_repeat_ngram_size=args.no_repeat_ngram_size,
                )
            text = sp.decode(out[0].tolist())

        rows.append({
            "run_id": run_id,
            "generated_at": generated_at,
            "prompt_id": item.get("id"),
            "mode": item.get("mode", "base"),
            "category": item.get("category"),
            "expected_behavior": item.get("expected_behavior", ""),
            "prompt": prompt,
            "checkpoint": str(checkpoint),
            "checkpoint_step": state.get("step"),
            "checkpoint_loss": state.get("loss"),
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_k": top_k,
            "top_p": args.top_p,
            "repetition_penalty": args.repetition_penalty,
            "no_repeat_ngram_size": args.no_repeat_ngram_size,
            "response": text,
        })

    atomic_write_jsonl(Path(args.out), rows)
    print(f"Wrote {len(rows)} Glyph-27M samples to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
