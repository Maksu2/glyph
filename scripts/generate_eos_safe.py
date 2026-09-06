#!/usr/bin/env python3
"""EOS-safe copy of GPT.generate (model/transformer.py is NOT modified).

Single behavioral change vs the original: top-k and top-p filtering NEVER
remove eos_token_id from the distribution. Everything else (repetition
penalty, no-repeat n-grams, temperature, greedy path, EOS break, finished
padding) is byte-for-byte the original logic.
"""
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import ModelConfig  # noqa: E402
from model import GPT  # noqa: E402


class EOSSafeGPT(GPT):
    @torch.no_grad()
    def generate(
        self,
        idx,
        max_new_tokens,
        temperature=1.0,
        top_k=None,
        top_p=1.0,
        repetition_penalty=1.0,
        no_repeat_ngram_size=0,
        eos_token_id=None,
    ):
        """Generate tokens, optionally stopping once every sequence emits EOS."""
        self.eval()
        finished = torch.zeros(idx.size(0), dtype=torch.bool, device=idx.device)
        for _ in range(max_new_tokens):
            # Trim to context window
            idx_cond = idx[:, -self.config.context_len:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]  # last token logits

            if repetition_penalty and repetition_penalty != 1.0:
                penalty = max(1.0, float(repetition_penalty))
                for batch_idx in range(idx.size(0)):
                    seen_tokens = idx[batch_idx].unique()
                    seen_logits = logits[batch_idx, seen_tokens]
                    logits[batch_idx, seen_tokens] = torch.where(
                        seen_logits < 0,
                        seen_logits * penalty,
                        seen_logits / penalty,
                    )

            if no_repeat_ngram_size and no_repeat_ngram_size > 1:
                n = int(no_repeat_ngram_size)
                for batch_idx in range(idx.size(0)):
                    sequence = idx[batch_idx].tolist()
                    if len(sequence) < n - 1:
                        continue
                    prefix = tuple(sequence[-(n - 1):])
                    banned = set()
                    for pos in range(len(sequence) - n + 1):
                        if tuple(sequence[pos:pos + n - 1]) == prefix:
                            banned.add(sequence[pos + n - 1])
                    if banned:
                        logits[batch_idx, list(banned)] = float("-inf")

            if temperature == 0.0:
                # Greedy
                idx_next = logits.argmax(dim=-1, keepdim=True)
            else:
                logits = logits / temperature
                if top_k is not None:
                    k = min(top_k, logits.size(-1))
                    top_values, _ = torch.topk(logits, k)
                    # EOS-SAFE CHANGE 1: snapshot EOS logit, restore after mask
                    eos_keep = None
                    if eos_token_id is not None:
                        eos_keep = logits[:, int(eos_token_id)].clone()
                    logits[logits < top_values[:, [-1]]] = float("-inf")
                    if eos_keep is not None:
                        logits[:, int(eos_token_id)] = eos_keep
                if top_p is not None and top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    sorted_probs = F.softmax(sorted_logits, dim=-1)
                    cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                    sorted_remove = cumulative_probs > top_p
                    sorted_remove[:, 1:] = sorted_remove[:, :-1].clone()
                    sorted_remove[:, 0] = False
                    remove = torch.zeros_like(logits, dtype=torch.bool)
                    remove.scatter_(1, sorted_indices, sorted_remove)
                    # EOS-SAFE CHANGE 2: EOS is never removed by top-p
                    if eos_token_id is not None:
                        remove[:, int(eos_token_id)] = False
                    logits = logits.masked_fill(remove, float("-inf"))
                probs = F.softmax(logits, dim=-1)
                idx_next = torch.multinomial(probs, num_samples=1)

            if eos_token_id is not None:
                eos = torch.full_like(idx_next, int(eos_token_id))
                idx_next = torch.where(finished.unsqueeze(1), eos, idx_next)

            idx = torch.cat((idx, idx_next), dim=1)
            if eos_token_id is not None:
                finished |= idx_next.squeeze(1).eq(int(eos_token_id))
                if bool(finished.all()):
                    break
        return idx


def load_eos_safe(path: Path, device: torch.device) -> tuple[EOSSafeGPT, dict]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg = ModelConfig(**{k: v for k, v in state["model_config"].items()
                         if k in ModelConfig.__dataclass_fields__})
    model = EOSSafeGPT(cfg)
    model.load_state_dict(state["model"])
    model.to(device)
    model.eval()
    return model, state


def load_tokenizer(path: Path):
    import sentencepiece as spm

    sp = spm.SentencePieceProcessor()
    sp.load(str(path))
    return sp


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--prompts",
                    default="eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl")
    ap.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    ap.add_argument("--out", required=True)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=40)
    ap.add_argument("--max-new-tokens", type=int, default=400)
    ap.add_argument("--seed-base", type=int, default=20260717)
    ap.add_argument("--seed-offset2", type=int, default=100000)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    device = torch.device(args.device)
    model, state = load_eos_safe(ROOT / args.checkpoint, device)
    sp = load_tokenizer(ROOT / args.tokenizer)
    prompts = [json.loads(l) for l in (ROOT / args.prompts).read_text(
        encoding="utf-8").splitlines() if l.strip()]

    rows = []
    t0 = time.perf_counter()
    for rep, seed_base in enumerate((args.seed_base, args.seed_base + args.seed_offset2)):
        for i, pr in enumerate(prompts):
            seed = seed_base + i
            torch.manual_seed(seed)
            ids = sp.encode(pr["prompt"], out_type=int)
            idx = torch.tensor([ids], dtype=torch.long, device=device)
            with torch.no_grad():
                out = model.generate(idx, max_new_tokens=args.max_new_tokens,
                                     temperature=args.temperature, top_k=args.top_k,
                                     eos_token_id=sp.eos_id())
            gen = out[0].tolist()[len(ids):]
            ended = bool(gen and gen[-1] == sp.eos_id())
            rows.append({"prompt_id": pr["id"], "rep": rep, "seed": seed,
                         "new_tokens": len(gen), "ended_by_eos": ended,
                         "len_to_eos": len(gen) if ended else None})
            print(f"ckpt={args.checkpoint} rep={rep} prompt={pr['id']} "
                  f"tokens={len(gen)} eos={ended}", flush=True)
    dt = time.perf_counter() - t0
    n = len(rows)
    ended = [r for r in rows if r["ended_by_eos"]]
    payload = {
        "checkpoint": args.checkpoint, "step": state.get("step"),
        "preset": {"temperature": args.temperature, "top_k": args.top_k,
                   "max_new_tokens": args.max_new_tokens,
                   "top_p": 1.0, "repetition_penalty": 1.0,
                   "no_repeat_ngram_size": 0, "eos_safe": True},
        "n": n, "ended_by_eos": len(ended),
        "hit_limit": sum(1 for r in rows if not r["ended_by_eos"]),
        "mean_len_to_eos": (sum(r["len_to_eos"] for r in ended) / len(ended)
                            if ended else None),
        "seconds": round(dt, 1),
        "rows": rows,
    }
    (ROOT / args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out} eos={len(ended)}/{n}", flush=True)
