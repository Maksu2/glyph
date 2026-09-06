#!/usr/bin/env python3
"""Evaluate corrected Glyph-100M SFT smoke v0.1 against the 44k base."""

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

GENERIC_TEMPLATE_PATTERNS = [
    "jako model językowy",
    "nie mam dostępu",
    "oto odpowiedź",
    "mam nadzieję",
    "chętnie pomogę",
]

DIAGNOSTIC_INSTRUCTIONS = [
    {"id": "diag-definition-backup", "category": "definition", "instruction": "Czym jest backup?"},
    {"id": "diag-definition-tokenizer", "category": "definition", "instruction": "Wyjaśnij krótko, czym jest tokenizer."},
    {"id": "diag-technical-cpu-load", "category": "technical", "instruction": "Czym różni się CPU usage od load average?"},
    {"id": "diag-missing-laptop", "category": "missing_data", "instruction": "Czy ten laptop jest dobry?"},
    {"id": "diag-missing-buy", "category": "missing_data", "instruction": "Czy powinienem to kupić?"},
    {
        "id": "diag-rewrite-project",
        "category": "rewrite",
        "instruction": "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.",
    },
    {
        "id": "diag-summary-scope",
        "category": "summary",
        "instruction": "Streść w jednym zdaniu: Duże projekty często upadają przez zbyt szeroki zakres.",
    },
    {"id": "diag-project-ui", "category": "project", "instruction": "Nie wiem, czy zacząć projekt od UI czy od logiki."},
    {"id": "diag-anti-loop", "category": "anti_loop", "instruction": "Odpowiedz krótko i nie powtarzaj tej samej myśli."},
    {"id": "diag-uncertainty-loss", "category": "uncertainty", "instruction": "Czy niski loss oznacza dobry model?"},
]

CONTINUATION_PROMPTS = [
    "Warszawa to",
    "W fizyce energia",
    "Uczenie maszynowe polega na",
    "Najważniejszym problemem tego projektu jest",
    "Dobry raport techniczny",
    "Na początku eksperymentu",
    "Czysty dataset",
    "Walidacja pokazuje",
]


def select_device(name: str) -> torch.device:
    requested = name.strip().lower()
    if requested in {"cuda", "gpu"}:
        if not torch.cuda.is_available():
            raise SystemExit("requested cuda/gpu but torch.cuda.is_available() is false")
        return torch.device("cuda")
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
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
def generate_one(model: GPT, sp, device: torch.device, prompt: str, max_new_tokens: int) -> tuple[str, str, bool, float]:
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
    raw_text = sp.decode(new_ids).strip()
    ended_by_end = END_TOKEN in raw_text
    text = raw_text.split(END_TOKEN, 1)[0].strip() if ended_by_end else raw_text
    return text, raw_text, ended_by_end, elapsed


def target_score(output: str, target: str, ended_by_end: bool, prompt: str) -> dict:
    out_words = words(output)
    target_words = words(target)
    target_set = set(target_words)
    overlap = len(set(out_words) & target_set) / len(target_set) if target_set else 0.0
    first_target = target_words[0] if target_words else ""
    starts_correctly = bool(first_target and out_words and out_words[0] == first_target)
    natural_end = bool(re.search(r"[.!?]$", output.strip())) or ended_by_end
    repetition = repeated_ngram(output)
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    generic = contains_any(output, GENERIC_TEMPLATE_PATTERNS)
    template_leak = any(tok in output for tok in (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN))
    prompt_overlap = normalize_space(prompt).lower() in normalize_space(output).lower()[:120]
    exact_target_match = normalize_space(output).lower() == normalize_space(target).lower()
    score = 0
    score += 3 if starts_correctly else 0
    score += min(4, int(overlap * 5))
    score += 2 if ended_by_end else 0
    score += 1 if natural_end else 0
    score -= min(repetition, 3)
    score -= 2 if web else 0
    score -= 1 if pseudo else 0
    score -= 1 if generic else 0
    score -= 2 if template_leak else 0
    score -= 1 if prompt_overlap else 0
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
        "generic_assistant_template": generic,
        "template_leak": template_leak,
        "prompt_overlap": prompt_overlap,
        "exact_target_match": exact_target_match,
        "score": score,
    }


def diagnostic_score(category: str, prompt: str, output: str, ended_by_end: bool) -> dict:
    out_words = words(output)
    lowered = output.lower()
    natural_end = bool(re.search(r"[.!?]$", output.strip())) or ended_by_end
    repetition = repeated_ngram(output)
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    generic = contains_any(output, GENERIC_TEMPLATE_PATTERNS)
    template_leak = any(tok in output for tok in (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN))
    prompt_overlap = normalize_space(prompt).lower() in normalize_space(output).lower()[:120]
    relevance = 1
    completion = 1
    if len(out_words) < 3 or web or template_leak:
        relevance = 0
        completion = 0
    elif category == "missing_data":
        ok = any(x in lowered for x in ["brak", "nie da", "potrzeb", "bez", "nie mam", "zależy"])
        relevance = 3 if ok else 1
        completion = 3 if ok else 1
    elif category == "rewrite":
        bad_meta = any(x in lowered for x in ["poprawiony tekst", "oto", "można napisać"])
        relevance = 3 if not bad_meta and 4 <= len(out_words) <= 28 else 2
        completion = relevance
    elif category == "summary":
        relevance = 3 if 5 <= len(out_words) <= 30 else 2
        completion = relevance
    elif category in {"definition", "technical"}:
        relevance = 3 if len(out_words) >= 6 and not pseudo else 2
        completion = 3 if len(out_words) <= 45 and natural_end else 2
    elif category == "anti_loop":
        relevance = 3 if repetition == 0 and len(out_words) <= 35 else 2
        completion = relevance
    else:
        relevance = 3 if 5 <= len(out_words) <= 55 else 2
        completion = 3 if natural_end else 2
    if repetition > 1:
        relevance = min(relevance, 2)
        completion = min(completion, 2)
    if pseudo:
        relevance = min(relevance, 1)
    score = relevance + completion + (2 if ended_by_end else 0) + (1 if natural_end else 0)
    score -= min(repetition, 3)
    score -= 2 if web else 0
    score -= 1 if pseudo else 0
    score -= 1 if generic else 0
    score -= 1 if prompt_overlap else 0
    return {
        "words": len(out_words),
        "semantic_relevance": relevance,
        "task_completion": completion,
        "ended_by_end_token": ended_by_end,
        "natural_end": natural_end,
        "repetition_ngrams": repetition,
        "web_residue": web,
        "pseudo_ency": pseudo,
        "generic_assistant_template": generic,
        "template_leak": template_leak,
        "prompt_overlap": prompt_overlap,
        "score": score,
    }


def continuation_score(prompt: str, output: str) -> dict:
    out_words = words(output)
    repetition = repeated_ngram(output)
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    natural_end = bool(re.search(r"[.!?]$", output.strip()))
    prompt_overlap = normalize_space(prompt).lower() in normalize_space(output).lower()[:120]
    score = 4
    score -= 2 if len(out_words) < 5 else 0
    score -= min(repetition, 3)
    score -= 2 if web else 0
    score -= 1 if pseudo else 0
    score += 1 if natural_end else 0
    score -= 1 if prompt_overlap else 0
    return {
        "words": len(out_words),
        "natural_end": natural_end,
        "repetition_ngrams": repetition,
        "web_residue": web,
        "pseudo_ency": pseudo,
        "prompt_overlap": prompt_overlap,
        "score": score,
    }


def run_model(checkpoint: str, rows: list[dict], sp, device: torch.device, max_instruction_tokens: int, max_continuation_tokens: int) -> tuple[list[dict], dict]:
    model, state = load_model(checkpoint, device)
    results = []
    for row in rows:
        prompt_text = instruction_prompt(row["instruction"]) if row["kind"] != "continuation" else row["prompt"]
        max_tokens = max_continuation_tokens if row["kind"] == "continuation" else max_instruction_tokens
        output, raw_output, ended, seconds = generate_one(model, sp, device, prompt_text, max_tokens)
        if row["kind"] == "target_instruction":
            score = target_score(output, row["response"], ended, row["instruction"])
        elif row["kind"] == "diagnostic_instruction":
            score = diagnostic_score(row["category"], row["instruction"], output, ended)
        else:
            score = continuation_score(row["prompt"], output)
        results.append({"output": output, "raw_output": raw_output, "ended_by_end_token": ended, "seconds": seconds, "score": score})
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return results, state


def build_rows(val_jsonl: str, val_examples: int) -> list[dict]:
    loaded = load_jsonl(val_jsonl)
    rows: list[dict] = []
    for record in loaded.records[:val_examples]:
        rows.append(
            {
                "kind": "target_instruction",
                "id": record.get("id"),
                "category": record.get("category", "unknown"),
                "instruction": record["instruction"],
                "response": record["response"],
            }
        )
    rows.extend({"kind": "diagnostic_instruction", **item} for item in DIAGNOSTIC_INSTRUCTIONS)
    rows.extend({"kind": "continuation", "id": f"cont-{idx:02d}", "category": "base_lm_sanity", "prompt": prompt} for idx, prompt in enumerate(CONTINUATION_PROMPTS, 1))
    return rows


def choose_winner(base_score: int, sft_score: int) -> str:
    if sft_score >= base_score + 2:
        return "sft"
    if base_score >= sft_score + 2:
        return "base"
    return "tie"


def build_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Glyph-100M corrected SFT smoke v0.1 before/after eval",
        "",
        "## Summary",
        "",
        f"- base checkpoint: `{s['base_checkpoint']}`",
        f"- SFT checkpoint: `{s['sft_checkpoint']}`",
        f"- examples: {s['examples']} ({s['target_instruction_examples']} held-out target, {s['diagnostic_instruction_examples']} diagnostic, {s['continuation_examples']} continuation)",
        f"- decoding: `{s['decoding']}`",
        f"- prompt template: `{s['prompt_template']}`",
        f"- base avg score: {s['base_avg_score']:.2f}",
        f"- SFT avg score: {s['sft_avg_score']:.2f}",
        f"- winners: `{s['winners']}`",
        f"- SFT first-token correct on target examples: {s['sft_starts_correctly']}/{s['target_instruction_examples']}",
        f"- SFT ended by `<|end|>` on instruction examples: {s['sft_instruction_ended_by_end_token']}/{s['instruction_examples']}",
        f"- SFT natural endings: {s['sft_natural_endings']}/{s['examples']}",
        f"- SFT repetition samples: {s['sft_repetition_samples']}",
        f"- SFT pseudo-ency samples: {s['sft_pseudo_ency']}",
        f"- SFT web residue samples: {s['sft_web_residue']}",
        f"- SFT generic assistant template samples: {s['sft_generic_template_samples']}",
        f"- SFT prompt overlap samples: {s['sft_prompt_overlap_samples']}",
        f"- exact target matches on held-out val: {s['sft_exact_target_matches']}",
        "",
        "## Samples",
        "",
    ]
    for idx, row in enumerate(payload["results"], 1):
        prompt = row.get("instruction") or row.get("prompt")
        lines.extend(
            [
                f"### {idx:02d}. {row['kind']} / {row['category']} / {row.get('id')}",
                "",
                f"Prompt: {prompt}",
                "",
            ]
        )
        if row["kind"] == "target_instruction":
            lines.extend([f"Target: {row['response']}", ""])
        lines.extend(
            [
                "Base:",
                "",
                row["base_output"] or "[empty]",
                "",
                f"Base score: `{row['base_score']}`",
                "",
                "SFT v0.1:",
                "",
                row["sft_output"] or "[empty]",
                "",
                f"SFT score: `{row['sft_score']}`",
                f"Winner: `{row['winner']}`",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate corrected Glyph SFT smoke v0.1")
    parser.add_argument("--val-jsonl", default="data/sft/processed/glyph100_sft_smoke_v0_val.jsonl")
    parser.add_argument("--base-checkpoint", required=True)
    parser.add_argument("--sft-checkpoint", required=True)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--val-examples", type=int, default=32)
    parser.add_argument("--max-instruction-tokens", type=int, default=80)
    parser.add_argument("--max-continuation-tokens", type=int, default=80)
    parser.add_argument("--output-md", default="eval/glyph-100m/sft_smoke_v0_1_fixedmask_before_after.md")
    parser.add_argument("--output-json", default="eval/glyph-100m/sft_smoke_v0_1_fixedmask_before_after.json")
    args = parser.parse_args()

    sp = load_sentencepiece(args.tokenizer)
    device = select_device(args.device)
    rows = build_rows(args.val_jsonl, args.val_examples)
    base_results, base_state = run_model(args.base_checkpoint, rows, sp, device, args.max_instruction_tokens, args.max_continuation_tokens)
    sft_results, sft_state = run_model(args.sft_checkpoint, rows, sp, device, args.max_instruction_tokens, args.max_continuation_tokens)

    winners = Counter()
    result_rows = []
    for row, base, sft in zip(rows, base_results, sft_results, strict=True):
        win = choose_winner(base["score"]["score"], sft["score"]["score"])
        winners[win] += 1
        out = {
            **row,
            "base_output": base["output"],
            "base_raw_output": base["raw_output"],
            "base_score": base["score"],
            "base_seconds": base["seconds"],
            "sft_output": sft["output"],
            "sft_raw_output": sft["raw_output"],
            "sft_score": sft["score"],
            "sft_seconds": sft["seconds"],
            "winner": win,
        }
        result_rows.append(out)

    instruction_rows = [r for r in result_rows if r["kind"] != "continuation"]
    target_rows = [r for r in result_rows if r["kind"] == "target_instruction"]
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_checkpoint": args.base_checkpoint,
        "sft_checkpoint": args.sft_checkpoint,
        "base_step": base_state.get("current_step", base_state.get("step")),
        "sft_step": sft_state.get("current_step", sft_state.get("step")),
        "base_variant": base_state.get("variant"),
        "sft_variant": sft_state.get("variant"),
        "base_dataset": base_state.get("dataset_name"),
        "sft_dataset": sft_state.get("dataset_name"),
        "examples": len(result_rows),
        "instruction_examples": len(instruction_rows),
        "target_instruction_examples": len(target_rows),
        "diagnostic_instruction_examples": sum(1 for r in result_rows if r["kind"] == "diagnostic_instruction"),
        "continuation_examples": sum(1 for r in result_rows if r["kind"] == "continuation"),
        "decoding": "greedy temperature=0.0 top_k=None top_p=1.0",
        "prompt_template": f"{USER_TOKEN}\\n{{prompt}}\\n{ASSISTANT_TOKEN}\\n",
        "winners": dict(winners),
        "base_avg_score": sum(row["base_score"]["score"] for row in result_rows) / len(result_rows),
        "sft_avg_score": sum(row["sft_score"]["score"] for row in result_rows) / len(result_rows),
        "base_repetition_samples": sum(1 for row in result_rows if row["base_score"]["repetition_ngrams"] > 0),
        "sft_repetition_samples": sum(1 for row in result_rows if row["sft_score"]["repetition_ngrams"] > 0),
        "base_web_residue": sum(1 for row in result_rows if row["base_score"]["web_residue"]),
        "sft_web_residue": sum(1 for row in result_rows if row["sft_score"]["web_residue"]),
        "base_pseudo_ency": sum(1 for row in result_rows if row["base_score"]["pseudo_ency"]),
        "sft_pseudo_ency": sum(1 for row in result_rows if row["sft_score"]["pseudo_ency"]),
        "sft_generic_template_samples": sum(1 for row in result_rows if row["sft_score"].get("generic_assistant_template")),
        "sft_prompt_overlap_samples": sum(1 for row in result_rows if row["sft_score"].get("prompt_overlap")),
        "sft_natural_endings": sum(1 for row in result_rows if row["sft_score"]["natural_end"]),
        "sft_instruction_ended_by_end_token": sum(1 for row in instruction_rows if row["sft_score"]["ended_by_end_token"]),
        "sft_starts_correctly": sum(1 for row in target_rows if row["sft_score"]["starts_with_target_first_word"]),
        "sft_exact_target_matches": sum(1 for row in target_rows if row["sft_score"]["exact_target_match"]),
        "sft_target_overlap_ge_0_70": sum(1 for row in target_rows if row["sft_score"]["target_overlap"] >= 0.70),
    }
    payload = {"summary": summary, "results": result_rows}
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
