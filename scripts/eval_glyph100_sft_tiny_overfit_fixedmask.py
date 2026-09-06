#!/usr/bin/env python3
"""Evaluate fixed-mask tiny SFT overfit against the 44k base checkpoint."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_jsonl, load_sentencepiece, normalize_space


WEB_PATTERNS = [
    "cookies",
    "kup teraz",
    "dodaj do koszyka",
    "zaloguj",
    "zarejestruj",
    "polityka prywatności",
    "strona główna",
    "kliknij",
    "komentarze",
    "odpowiedz",
]

PSEUDO_PATTERNS = [
    "w latach 1975",
    "w latach 1975–1998",
    "gminie",
    "powiecie",
    "według najnowszych danych",
    "liczyła mieszkańców",
    "województwie",
]


def select_device(name: str) -> torch.device:
    requested = name.strip().lower()
    if requested in {"cuda", "gpu"}:
        if not torch.cuda.is_available():
            raise SystemExit("requested cuda/gpu but torch.cuda.is_available() is false")
        return torch.device("cuda")
    return torch.device("cpu")


def load_model(path: str, device: torch.device) -> tuple[GPT, dict]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config", {})
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
    model = GPT(cfg).to(device)
    model.load_state_dict(state["model"])
    model.eval()
    return model, state


def instruction_prompt(prompt: str) -> str:
    return f"{USER_TOKEN}\n{prompt.strip()}\n{ASSISTANT_TOKEN}\n"


def words(text: str) -> list[str]:
    return re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+", text.lower(), flags=re.UNICODE)


def repeated_ngram(text: str, n: int = 3) -> int:
    ws = words(text)
    counts: Counter[tuple[str, ...]] = Counter(tuple(ws[i : i + n]) for i in range(max(0, len(ws) - n + 1)))
    return sum(count - 1 for count in counts.values() if count > 1)


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


@torch.no_grad()
def generate_one(model: GPT, sp, device: torch.device, prompt: str, max_new_tokens: int) -> tuple[str, bool, float]:
    ids = sp.encode(prompt, out_type=int)
    idx = torch.tensor([ids], dtype=torch.long, device=device)
    start = time.perf_counter()
    out = model.generate(
        idx,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        top_k=None,
        top_p=1.0,
        repetition_penalty=1.0,
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = time.perf_counter() - start
    new_ids = out[0, idx.shape[1] :].detach().cpu().tolist()
    text = sp.decode(new_ids).strip()
    ended_by_end = END_TOKEN in text
    if ended_by_end:
        text = text.split(END_TOKEN, 1)[0].strip()
    return text, ended_by_end, elapsed


def score_output(output: str, target: str, ended_by_end: bool) -> dict:
    out_words = words(output)
    target_words = words(target)
    target_set = set(target_words)
    overlap = 0.0
    if target_set:
        overlap = len(set(out_words) & target_set) / len(target_set)
    first_target = target_words[0] if target_words else ""
    starts_correctly = bool(first_target and out_words and out_words[0] == first_target)
    natural_end = bool(re.search(r"[.!?]$", output.strip())) or ended_by_end
    repetition = repeated_ngram(output)
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    template_leak = any(tok in output for tok in (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN))
    score = 0
    score += 3 if starts_correctly else 0
    score += min(4, int(overlap * 5))
    score += 2 if ended_by_end else 0
    score += 1 if natural_end else 0
    score -= min(repetition, 3)
    score -= 2 if web else 0
    score -= 1 if pseudo else 0
    score -= 2 if template_leak else 0
    return {
        "words": len(out_words),
        "target_words": len(target_words),
        "target_overlap": overlap,
        "starts_with_target_first_word": starts_correctly,
        "ended_by_end_token": ended_by_end,
        "natural_end": natural_end,
        "repetition_ngrams": repetition,
        "web_residue": web,
        "pseudo_ency": pseudo,
        "template_leak": template_leak,
        "score": score,
    }


def run_model(checkpoint: str, prompts: list[dict], sp, device: torch.device, max_new_tokens: int) -> tuple[list[dict], dict]:
    model, state = load_model(checkpoint, device)
    results = []
    for item in prompts:
        text, ended, seconds = generate_one(model, sp, device, instruction_prompt(item["instruction"]), max_new_tokens)
        results.append(
            {
                "output": text,
                "ended_by_end_token": ended,
                "seconds": seconds,
                "score": score_output(text, item["response"], ended),
            }
        )
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return results, state


def build_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Glyph-100M SFT tiny overfit fixed-mask eval",
        "",
        "## Summary",
        "",
        f"- base checkpoint: `{s['base_checkpoint']}`",
        f"- tiny SFT checkpoint: `{s['sft_checkpoint']}`",
        f"- examples: {s['examples']}",
        f"- base avg score: {s['base_avg_score']:.2f}",
        f"- SFT avg score: {s['sft_avg_score']:.2f}",
        f"- winners: `{s['winners']}`",
        f"- SFT exact/near target overlap >= 0.70: {s['sft_overlap_ge_0_70']}",
        f"- SFT starts with expected first word: {s['sft_starts_correctly']}",
        f"- SFT ended by `<|end|>`: {s['sft_ended_by_end_token']}",
        f"- SFT repetition samples: {s['sft_repetition_samples']}",
        f"- SFT web residue: {s['sft_web_residue']}",
        f"- SFT pseudo-ency: {s['sft_pseudo_ency']}",
        "",
        "## Samples",
        "",
    ]
    for idx, row in enumerate(payload["results"], 1):
        lines.extend(
            [
                f"### {idx:02d}. {row['id']} / {row['category']}",
                "",
                f"Prompt: {row['instruction']}",
                "",
                f"Target: {row['response']}",
                "",
                "Base:",
                "",
                row["base_output"] or "[empty]",
                "",
                f"Base score: `{row['base_score']}`",
                "",
                "Tiny SFT:",
                "",
                row["sft_output"] or "[empty]",
                "",
                f"Tiny SFT score: `{row['sft_score']}`",
                f"Winner: `{row['winner']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Glyph fixed-mask tiny overfit SFT")
    parser.add_argument("--dataset", default="data/sft/processed/glyph100_sft_tiny_overfit_fixedmask_train.jsonl")
    parser.add_argument("--base-checkpoint", required=True)
    parser.add_argument("--sft-checkpoint", required=True)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--examples", type=int, default=32)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--output-md", default="eval/glyph-100m/sft_tiny_overfit_cpu_fixedmask_eval.md")
    parser.add_argument("--output-json", default="eval/glyph-100m/sft_tiny_overfit_cpu_fixedmask_eval.json")
    args = parser.parse_args()

    loaded = load_jsonl(args.dataset)
    prompts = loaded.records[: args.examples]
    sp = load_sentencepiece(args.tokenizer)
    device = select_device(args.device)

    base_results, base_state = run_model(args.base_checkpoint, prompts, sp, device, args.max_new_tokens)
    sft_results, sft_state = run_model(args.sft_checkpoint, prompts, sp, device, args.max_new_tokens)

    rows = []
    winners = Counter()
    for item, base, sft in zip(prompts, base_results, sft_results, strict=True):
        base_score = base["score"]["score"]
        sft_score = sft["score"]["score"]
        if sft_score >= base_score + 2:
            win = "sft"
        elif base_score >= sft_score + 2:
            win = "base"
        else:
            win = "tie"
        winners[win] += 1
        rows.append(
            {
                "id": item.get("id"),
                "category": item.get("category"),
                "instruction": item.get("instruction"),
                "response": item.get("response"),
                "base_output": base["output"],
                "base_score": base["score"],
                "base_seconds": base["seconds"],
                "sft_output": sft["output"],
                "sft_score": sft["score"],
                "sft_seconds": sft["seconds"],
                "winner": win,
            }
        )

    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_checkpoint": args.base_checkpoint,
        "sft_checkpoint": args.sft_checkpoint,
        "base_step": base_state.get("current_step", base_state.get("step")),
        "sft_step": sft_state.get("current_step", sft_state.get("step")),
        "base_variant": base_state.get("variant"),
        "sft_variant": sft_state.get("variant"),
        "examples": len(rows),
        "decoding": "greedy temperature=0.0 top_k=None top_p=1.0",
        "prompt_template": f"{USER_TOKEN}\\n{{prompt}}\\n{ASSISTANT_TOKEN}\\n",
        "winners": dict(winners),
        "base_avg_score": sum(row["base_score"]["score"] for row in rows) / len(rows),
        "sft_avg_score": sum(row["sft_score"]["score"] for row in rows) / len(rows),
        "base_overlap_ge_0_70": sum(1 for row in rows if row["base_score"]["target_overlap"] >= 0.70),
        "sft_overlap_ge_0_70": sum(1 for row in rows if row["sft_score"]["target_overlap"] >= 0.70),
        "sft_starts_correctly": sum(1 for row in rows if row["sft_score"]["starts_with_target_first_word"]),
        "sft_ended_by_end_token": sum(1 for row in rows if row["sft_score"]["ended_by_end_token"]),
        "sft_repetition_samples": sum(1 for row in rows if row["sft_score"]["repetition_ngrams"] > 0),
        "sft_web_residue": sum(1 for row in rows if row["sft_score"]["web_residue"]),
        "sft_pseudo_ency": sum(1 for row in rows if row["sft_score"]["pseudo_ency"]),
    }
    payload = {"summary": summary, "results": rows}
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
