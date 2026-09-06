#!/usr/bin/env python3
"""Small before/after evaluation for Glyph-100M SFT smoke checkpoints."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece


INSTRUCTION_PROMPTS = [
    ("definition", "Czym jest backup?"),
    ("definition", "Wyjaśnij prosto, czym jest tokenizer."),
    ("technical", "Czym różni się CPU usage od load average?"),
    ("technical", "Po co zapisuje się checkpointy modelu?"),
    ("missing_data", "Czy ten laptop jest dobry?"),
    ("missing_data", "Czy powinienem to kupić?"),
    ("rewrite", "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób."),
    ("rewrite", "Napisz naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie."),
    ("summary", "Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu."),
    ("summary", "Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem."),
    ("project", "Mam pomysł na aplikację i chcę od razu zrobić logowanie, dashboard i AI. Co zrobić?"),
    ("project", "Nie wiem, czy zacząć projekt od UI czy od logiki."),
    ("anti_loop", "Napisz krótką odpowiedź i nie powtarzaj tej samej myśli."),
    ("anti_loop", "Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?"),
    ("daily", "Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj."),
    ("daily", "Jak napisać prostą wiadomość z przeprosinami?"),
    ("uncertainty", "Czy większy model zawsze daje lepszy wynik?"),
    ("uncertainty", "Czy niski loss oznacza dobry model?"),
]

CONTINUATION_PROMPTS = [
    "Warszawa to",
    "W fizyce energia",
    "Uczenie maszynowe polega na",
    "Najważniejszym problemem tego projektu jest",
    "Dobry raport techniczny",
    "Na początku eksperymentu",
    "Prosty backup",
    "Model językowy może",
    "Czysty dataset",
    "Walidacja pokazuje",
]

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
    if requested == "auto":
        requested = "cuda" if torch.cuda.is_available() else "cpu"
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


def encode(sp, text: str, device: torch.device) -> torch.Tensor:
    ids = sp.encode(text, out_type=int)
    return torch.tensor([ids], dtype=torch.long, device=device)


def decode(sp, ids: list[int]) -> str:
    return sp.decode(ids)


@torch.no_grad()
def generate_text(model: GPT, sp, prompt: str, device: torch.device, max_new_tokens: int, seed: int) -> tuple[str, float]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    idx = encode(sp, prompt, device)
    start = time.perf_counter()
    out = model.generate(
        idx,
        max_new_tokens=max_new_tokens,
        temperature=0.7,
        top_k=40,
        top_p=0.9,
        repetition_penalty=1.1,
    )
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = time.perf_counter() - start
    new_ids = out[0, idx.shape[1] :].detach().cpu().tolist()
    text = decode(sp, new_ids)
    if END_TOKEN in text:
        text = text.split(END_TOKEN, 1)[0].strip()
    return text.strip(), elapsed


def instruction_prompt(prompt: str) -> str:
    return f"{USER_TOKEN}\n{prompt.strip()}\n{ASSISTANT_TOKEN}\n"


def repeated_ngram(text: str, n: int = 3) -> int:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    counts: dict[tuple[str, ...], int] = {}
    for i in range(max(0, len(words) - n + 1)):
        gram = tuple(words[i : i + n])
        counts[gram] = counts.get(gram, 0) + 1
    return sum(c - 1 for c in counts.values() if c > 1)


def contains_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def score_instruction(category: str, prompt: str, output: str) -> dict:
    lowered = output.lower()
    words = len(re.findall(r"\w+", output, flags=re.UNICODE))
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    repetition = repeated_ngram(output)
    natural_end = bool(re.search(r"[.!?]$", output.strip()))
    template_leak = any(tok in output for tok in (USER_TOKEN, ASSISTANT_TOKEN, END_TOKEN))

    relevance = 1
    completion = 1
    if words < 3 or template_leak or web:
        relevance = 0
        completion = 0
    elif category == "missing_data":
        ok = any(x in lowered for x in ["brak", "nie da", "potrzeb", "bez", "nie mam"])
        relevance = 3 if ok else 1
        completion = 3 if ok else 1
    elif category == "rewrite":
        bad_meta = any(x in lowered for x in ["poprawiony tekst", "oto", "można napisać"])
        relevance = 3 if not bad_meta and 4 <= words <= 25 else 2
        completion = relevance
    elif category == "summary":
        relevance = 3 if 5 <= words <= 28 else 2
        completion = relevance
    elif category in {"definition", "technical"}:
        relevance = 3 if words >= 6 and not pseudo else 2
        completion = 3 if words <= 45 and natural_end else 2
    elif category == "anti_loop":
        relevance = 3 if repetition == 0 and words <= 35 else 2
        completion = relevance
    else:
        relevance = 3 if 5 <= words <= 55 else 2
        completion = 3 if natural_end else 2

    if repetition > 1:
        relevance = min(relevance, 2)
        completion = min(completion, 2)
    if pseudo:
        relevance = min(relevance, 1)
    return {
        "words": words,
        "semantic_relevance": relevance,
        "task_completion": completion,
        "repetition_ngrams": repetition,
        "natural_end": natural_end,
        "web_residue": web,
        "pseudo_ency": pseudo,
        "template_leak": template_leak,
        "score": relevance + completion + (1 if natural_end else 0) - min(repetition, 2) - (2 if web else 0) - (1 if pseudo else 0),
    }


def score_continuation(prompt: str, output: str) -> dict:
    words = len(re.findall(r"\w+", output, flags=re.UNICODE))
    web = contains_any(output, WEB_PATTERNS)
    pseudo = contains_any(output, PSEUDO_PATTERNS)
    repetition = repeated_ngram(output)
    natural_end = bool(re.search(r"[.!?]$", output.strip()))
    prompt_overlap = prompt.lower().strip() in output.lower()[:80]
    score = 4
    if words < 5:
        score -= 2
    if repetition:
        score -= min(repetition, 2)
    if web:
        score -= 2
    if pseudo:
        score -= 1
    if natural_end:
        score += 1
    if prompt_overlap:
        score -= 1
    return {
        "words": words,
        "repetition_ngrams": repetition,
        "natural_end": natural_end,
        "web_residue": web,
        "pseudo_ency": pseudo,
        "prompt_overlap": prompt_overlap,
        "score": score,
    }


def winner(base_score: int, sft_score: int | None) -> str:
    if sft_score is None:
        return "base_only"
    if sft_score >= base_score + 2:
        return "sft"
    if base_score >= sft_score + 2:
        return "base"
    return "tie"


def run_eval(args: argparse.Namespace) -> dict:
    device = select_device(args.device)
    sp = load_sentencepiece(args.tokenizer)
    base_model, base_state = load_model(args.base_checkpoint, device)
    sft_model = None
    sft_state = None
    if args.sft_checkpoint:
        sft_model, sft_state = load_model(args.sft_checkpoint, device)

    results = []
    seed = args.seed
    for idx, (category, prompt) in enumerate(INSTRUCTION_PROMPTS, 1):
        full_prompt = instruction_prompt(prompt)
        base_text, base_time = generate_text(base_model, sp, full_prompt, device, args.max_instruction_tokens, seed + idx)
        base_score = score_instruction(category, prompt, base_text)
        item = {
            "kind": "instruction",
            "category": category,
            "prompt": prompt,
            "base_output": base_text,
            "base_score": base_score,
            "base_seconds": base_time,
        }
        if sft_model is not None:
            sft_text, sft_time = generate_text(sft_model, sp, full_prompt, device, args.max_instruction_tokens, seed + idx)
            sft_score = score_instruction(category, prompt, sft_text)
            item.update(
                {
                    "sft_output": sft_text,
                    "sft_score": sft_score,
                    "sft_seconds": sft_time,
                    "winner": winner(base_score["score"], sft_score["score"]),
                }
            )
        results.append(item)

    for idx, prompt in enumerate(CONTINUATION_PROMPTS, 1):
        base_text, base_time = generate_text(base_model, sp, prompt, device, args.max_continuation_tokens, seed + 100 + idx)
        base_score = score_continuation(prompt, base_text)
        item = {
            "kind": "continuation",
            "category": "base_lm_sanity",
            "prompt": prompt,
            "base_output": base_text,
            "base_score": base_score,
            "base_seconds": base_time,
        }
        if sft_model is not None:
            sft_text, sft_time = generate_text(sft_model, sp, prompt, device, args.max_continuation_tokens, seed + 100 + idx)
            sft_score = score_continuation(prompt, sft_text)
            item.update(
                {
                    "sft_output": sft_text,
                    "sft_score": sft_score,
                    "sft_seconds": sft_time,
                    "winner": winner(base_score["score"], sft_score["score"]),
                }
            )
        results.append(item)

    winners = {}
    if args.sft_checkpoint:
        for item in results:
            winners[item["winner"]] = winners.get(item["winner"], 0) + 1
    summary = {
        "base_checkpoint": args.base_checkpoint,
        "sft_checkpoint": args.sft_checkpoint,
        "base_step": base_state.get("current_step", base_state.get("step")),
        "sft_step": sft_state.get("current_step", sft_state.get("step")) if sft_state else None,
        "base_variant": base_state.get("variant"),
        "sft_variant": sft_state.get("variant") if sft_state else None,
        "examples": len(results),
        "winners": winners,
        "base_avg_score": sum(r["base_score"]["score"] for r in results) / len(results),
        "sft_avg_score": (
            sum(r["sft_score"]["score"] for r in results) / len(results) if args.sft_checkpoint else None
        ),
        "base_repetition_samples": sum(1 for r in results if r["base_score"]["repetition_ngrams"] > 0),
        "sft_repetition_samples": (
            sum(1 for r in results if r["sft_score"]["repetition_ngrams"] > 0) if args.sft_checkpoint else None
        ),
        "base_web_residue": sum(1 for r in results if r["base_score"]["web_residue"]),
        "sft_web_residue": sum(1 for r in results if r["sft_score"]["web_residue"]) if args.sft_checkpoint else None,
        "base_pseudo_ency": sum(1 for r in results if r["base_score"]["pseudo_ency"]),
        "sft_pseudo_ency": sum(1 for r in results if r["sft_score"]["pseudo_ency"]) if args.sft_checkpoint else None,
    }
    return {"summary": summary, "results": results}


def write_markdown(path: Path, payload: dict) -> None:
    summary = payload["summary"]
    lines = [
        "# Glyph-100M 44k SFT smoke eval",
        "",
        "## Summary",
        "",
        f"- base checkpoint: `{summary['base_checkpoint']}`",
        f"- SFT checkpoint: `{summary['sft_checkpoint']}`",
        f"- examples: {summary['examples']}",
        f"- base avg score: {summary['base_avg_score']:.2f}",
    ]
    if summary["sft_avg_score"] is not None:
        lines.extend(
            [
                f"- SFT avg score: {summary['sft_avg_score']:.2f}",
                f"- winners: {summary['winners']}",
                f"- base repetition samples: {summary['base_repetition_samples']}",
                f"- SFT repetition samples: {summary['sft_repetition_samples']}",
                f"- base pseudo-ency: {summary['base_pseudo_ency']}",
                f"- SFT pseudo-ency: {summary['sft_pseudo_ency']}",
            ]
        )
    lines.extend(["", "## Samples", ""])
    for i, item in enumerate(payload["results"], 1):
        lines.append(f"### {i:02d}. {item['kind']} / {item['category']}")
        lines.append("")
        lines.append(f"Prompt: {item['prompt']}")
        lines.append("")
        lines.append("Base:")
        lines.append("")
        lines.append(item["base_output"] or "[empty]")
        lines.append("")
        lines.append(f"Base score: `{item['base_score']}`")
        lines.append("")
        if "sft_output" in item:
            lines.append("SFT:")
            lines.append("")
            lines.append(item["sft_output"] or "[empty]")
            lines.append("")
            lines.append(f"SFT score: `{item['sft_score']}`")
            lines.append(f"Winner: `{item['winner']}`")
            lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Glyph-100M SFT smoke before/after")
    parser.add_argument("--base-checkpoint", required=True)
    parser.add_argument("--sft-checkpoint", default=None)
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--max-instruction-tokens", type=int, default=80)
    parser.add_argument("--max-continuation-tokens", type=int, default=100)
    args = parser.parse_args()

    payload = run_eval(args)
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(Path(args.output_md), payload)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
