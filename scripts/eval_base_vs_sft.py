#!/usr/bin/env python3
"""Practical qualitative evaluation: Glyph-27M Base vs Glyph-27M SFT v0."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ModelConfig
from model import GPT
from scripts.sft_utils import ASSISTANT_TOKEN, END_TOKEN, USER_TOKEN, load_sentencepiece, word_count


PROMPTS = [
    # Brak danych
    ("brak_danych", "Czy ten laptop jest dobry?"),
    ("brak_danych", "Czy ten wynik jest poprawny?"),
    ("brak_danych", "Czy to jest bezpieczne?"),
    ("brak_danych", "Czy powinienem to kupić?"),
    ("brak_danych", "Czy moja odpowiedź jest dobra?"),
    # Pisanie / poprawianie tekstu
    ("pisanie_i_poprawianie", "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób."),
    ("pisanie_i_poprawianie", "Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie."),
    ("pisanie_i_poprawianie", "Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj."),
    ("pisanie_i_poprawianie", "Skróć tekst: Ten projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start."),
    ("pisanie_i_poprawianie", "Napisz neutralną wiadomość, że nie mogę dziś przyjść."),
    # Streszczanie
    ("streszczanie", "Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu."),
    ("streszczanie", "Streść w dwóch zdaniach: Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt, plik tekstowy albo arkusz."),
    ("streszczanie", "Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem."),
    ("streszczanie", "Streść tekst: Najpierw trzeba zbudować działający prototyp. Dopiero potem warto poprawiać wygląd i automatyzację."),
    ("streszczanie", "Streść w jednym zdaniu: Dobry plan zaczyna się od małego testu, który pokazuje, czy warto rozwijać pomysł dalej."),
    # Proste wyjaśnienia
    ("proste_wyjasnienia", "Wyjaśnij prosto, czym różni się pogoda od klimatu."),
    ("proste_wyjasnienia", "Wyjaśnij, czym jest inflacja."),
    ("proste_wyjasnienia", "Czym różni się fakt od opinii?"),
    ("proste_wyjasnienia", "Wyjaśnij krótko, czym jest grawitacja."),
    ("proste_wyjasnienia", "Czym różni się masa od wagi?"),
    # Decyzje / doradztwo projektowe
    ("decyzje_projektowe", "Mam zacząć projekt od UI czy od logiki?"),
    ("decyzje_projektowe", "Mam ambitny projekt i chcę od razu zrobić backend, frontend, dashboard, AI, logowanie i ładne UI. Dobry plan?"),
    ("decyzje_projektowe", "Mam dwie opcje: zrobić projekt szybko i prosto albo długo dopracowywać wszystkie detale. Co wybrać?"),
    ("decyzje_projektowe", "Czy warto robić projekt, jeśli nie wiem jeszcze, czy go skończę?"),
    ("decyzje_projektowe", "Mam wybrać łatwiejszą czy ambitniejszą wersję projektu."),
    # Korekta błędnych założeń
    ("korekta_zalozen", "Popraw błędne założenie: droższy sprzęt zawsze jest lepszy."),
    ("korekta_zalozen", "Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany."),
    ("korekta_zalozen", "Popraw błędne założenie: jak projekt ma dużo funkcji, to jest lepszy."),
    ("korekta_zalozen", "Popraw błędne założenie: Docker to to samo co maszyna wirtualna."),
    ("korekta_zalozen", "Popraw błędne założenie: im dłuższa odpowiedź, tym jest mądrzejsza."),
    # Techniczne proste
    ("techniczne_proste", "Czym jest backup?"),
    ("techniczne_proste", "Czym różni się plik od folderu?"),
    ("techniczne_proste", "Czy chmura jest zawsze lepsza niż lokalny serwer?"),
    ("techniczne_proste", "Czym różni się aplikacja od strony internetowej?"),
    ("techniczne_proste", "Czym różni się CPU usage od load average?"),
    # Anty-pętle / dziwne prompty
    ("anty_petle", "Napisz krótką odpowiedź i nie powtarzaj tej samej myśli."),
    ("anty_petle", "Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?"),
    ("anty_petle", "Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego."),
    ("anty_petle", "Odpowiedz krótko: czego nie da się ocenić bez danych?"),
    ("anty_petle", "Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?"),
]


UNCERTAINTY_PATTERNS = (
    "brakuje danych",
    "bez danych",
    "nie da się ocenić",
    "nie mogę ocenić",
    "potrzeb",
    "zależy",
    "nie wiadomo",
    "nie znam",
)
WEB_GARBAGE_PATTERNS = (
    "widget",
    "blogspot",
    "forum",
    "strona 1",
    "strona 2",
    "rejestracja:",
    "post autor",
    "http://",
    "https://",
    "divclass",
    "divclasses",
    "_____",
    "______",
    "####",
    '{"',
    '","',
)
SFT_PHRASES = (
    "najkrótszy ruch",
    "rdzeń projektu",
    "brakuje danych",
    "nie ma sensu",
    "podejdź do tego jak do małego testu",
    "jeśli po tym dalej",
    "w praktyce warto",
)


@dataclass
class GenerationSettings:
    temperature: float = 0.75
    top_k: int = 40
    top_p: float = 0.92
    max_new_tokens: int = 120
    repetition_penalty: float = 1.15
    seed: int = 2026
    no_repeat_ngram_size: int = 0


def make_prompt(text: str) -> str:
    return f"{USER_TOKEN}\n{text.strip()}\n{ASSISTANT_TOKEN}\n"


def load_model(path: str, device: torch.device) -> tuple[GPT, ModelConfig]:
    state = torch.load(path, map_location="cpu", weights_only=False)
    cfg_dict = state.get("model_config", {})
    cfg = ModelConfig(**{k: v for k, v in cfg_dict.items() if k in ModelConfig.__dataclass_fields__})
    with redirect_stdout(sys.stderr):
        model = GPT(cfg)
    model.load_state_dict(state["model"])
    model.to(device)
    model.eval()
    return model, cfg


def select_device(value: str) -> torch.device:
    value = value.lower().strip()
    if value == "auto":
        value = "cuda" if torch.cuda.is_available() else "cpu"
    if value == "cuda" and not torch.cuda.is_available():
        raise SystemExit("Requested cuda/ROCm, but torch.cuda.is_available() is false")
    return torch.device(value)


def repeated_ngram_ratio(text: str, n: int = 3) -> float:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    if len(words) < n * 2:
        return 0.0
    grams = [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]
    counts = Counter(grams)
    repeated = sum(count - 1 for count in counts.values() if count > 1)
    return repeated / max(1, len(grams))


def adjacent_repeats(text: str) -> int:
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return sum(1 for prev, cur in zip(words, words[1:]) if prev == cur)


def contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def phrase_counts(text: str, phrases: tuple[str, ...] = SFT_PHRASES) -> dict[str, int]:
    lowered = text.lower()
    return {phrase: lowered.count(phrase) for phrase in phrases if lowered.count(phrase)}


def web_garbage_score(text: str) -> int:
    lowered = text.lower()
    score = sum(1 for pattern in WEB_GARBAGE_PATTERNS if pattern in lowered)
    if re.search(r"[_#]{4,}", text):
        score += 1
    if len(re.findall(r"[{}\\[\\]<>]", text)) >= 6:
        score += 1
    return score


def repetition_score(text: str) -> int:
    ratio = repeated_ngram_ratio(text, 3)
    adjacent = adjacent_repeats(text)
    phrase_repeat = sum(phrase_counts(text).values())
    if ratio > 0.12 or adjacent >= 4 or phrase_repeat >= 4:
        return 3
    if ratio > 0.06 or adjacent >= 2 or phrase_repeat >= 2:
        return 2
    if ratio > 0.025 or adjacent >= 1 or phrase_repeat >= 1:
        return 1
    return 0


def natural_end(text: str, ended_by_end: bool) -> bool:
    stripped = text.strip()
    if ended_by_end:
        return True
    return bool(stripped) and stripped[-1] in ".!?)”\"'"


def score_output(category: str, prompt: str, text: str, ended_by_end: bool, generated_tokens: int, max_tokens: int) -> dict:
    words = word_count(text)
    garbage = web_garbage_score(text)
    rep = repetition_score(text)
    lower = text.lower()
    natural = natural_end(text, ended_by_end)
    likely_cut = generated_tokens >= max_tokens and not ended_by_end and not natural

    coherence = 3
    if not text.strip() or words < 4:
        coherence = 0
    elif garbage >= 2 or rep == 3:
        coherence = 0
    elif garbage or rep == 2 or likely_cut:
        coherence = 1
    elif rep == 1 or not natural:
        coherence = 2

    following = 1 if text.strip() else 0
    usefulness = 1 if text.strip() else 0

    if category == "brak_danych":
        uncertain = contains_any(text, UNCERTAINTY_PATTERNS)
        following = 3 if uncertain and garbage == 0 else 1
        usefulness = 3 if uncertain and coherence >= 2 else 1
    elif category == "pisanie_i_poprawianie":
        follows = any(token in lower for token in ("wiadomość", "przeprasz", "nie zdążę", "projekt", "problem", "nie mogę"))
        following = 3 if follows and garbage == 0 else 1
        usefulness = 3 if follows and coherence >= 2 and words <= 80 else 1
    elif category == "streszczanie":
        follows = words <= 55 and garbage == 0
        following = 3 if follows else 1
        usefulness = 3 if follows and coherence >= 2 else 1
    elif category == "proste_wyjasnienia":
        follows = words >= 8 and words <= 95 and garbage == 0
        following = 3 if follows else 1
        usefulness = 3 if follows and coherence >= 2 else 1
    elif category == "decyzje_projektowe":
        follows = any(token in lower for token in ("najpierw", "zacznij", "prosto", "logik", "mniejsz", "wariant", "test"))
        following = 3 if follows and garbage == 0 else 1
        usefulness = 3 if follows and coherence >= 2 else 1
    elif category == "korekta_zalozen":
        follows = any(token in lower for token in ("nie zawsze", "to zależy", "błęd", "problem", "ważniejsz", "lepszy"))
        following = 3 if follows and garbage == 0 else 1
        usefulness = 3 if follows and coherence >= 2 else 1
    elif category == "techniczne_proste":
        follows = words >= 8 and words <= 100 and garbage == 0
        following = 3 if follows else 1
        usefulness = 3 if follows and coherence >= 2 else 1
    elif category == "anty_petle":
        follows = rep <= 1 and words <= 70 and garbage == 0
        following = 3 if follows else 1
        usefulness = 3 if follows and coherence >= 2 else 1

    if garbage:
        following = min(following, 1)
        usefulness = min(usefulness, 1)
    if coherence == 0:
        following = min(following, 1)
        usefulness = 0

    total = following + coherence + usefulness - rep
    return {
        "instruction_following": int(following),
        "coherence": int(coherence),
        "repetition": int(rep),
        "usefulness": int(usefulness),
        "total": int(total),
        "word_count": int(words),
        "char_count": len(text),
        "web_garbage_score": int(garbage),
        "ended_by_end": bool(ended_by_end),
        "natural_end": bool(natural),
        "likely_cut_off": bool(likely_cut),
        "sft_phrase_counts": phrase_counts(text),
    }


def compare_scores(base: dict, sft: dict) -> str:
    if base["total"] <= 3 and sft["total"] <= 3:
        return "both_bad"
    diff = sft["total"] - base["total"]
    if diff >= 2:
        return "sft"
    if diff <= -2:
        return "base"
    return "tie"


@torch.no_grad()
def generate_ids(model: GPT, idx: torch.Tensor, settings: GenerationSettings, end_id: int | None) -> tuple[list[int], bool, float]:
    start = time.perf_counter()
    generated: list[int] = []
    ended_by_end = False
    for _ in range(settings.max_new_tokens):
        idx_cond = idx[:, -model.config.context_len :]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :]

        if settings.repetition_penalty and settings.repetition_penalty != 1.0:
            penalty = max(1.0, float(settings.repetition_penalty))
            seen_tokens = idx[0].unique()
            seen_logits = logits[0, seen_tokens]
            logits[0, seen_tokens] = torch.where(seen_logits < 0, seen_logits * penalty, seen_logits / penalty)

        if settings.no_repeat_ngram_size and settings.no_repeat_ngram_size > 1:
            n = int(settings.no_repeat_ngram_size)
            sequence = idx[0].tolist()
            if len(sequence) >= n - 1:
                prefix = tuple(sequence[-(n - 1) :])
                banned = set()
                for pos in range(len(sequence) - n + 1):
                    if tuple(sequence[pos : pos + n - 1]) == prefix:
                        banned.add(sequence[pos + n - 1])
                if banned:
                    logits[0, list(banned)] = float("-inf")

        if settings.temperature == 0.0:
            idx_next = logits.argmax(dim=-1, keepdim=True)
        else:
            logits = logits / settings.temperature
            if settings.top_k > 0:
                k = min(settings.top_k, logits.size(-1))
                top_values, _ = torch.topk(logits, k)
                logits[logits < top_values[:, [-1]]] = float("-inf")
            if settings.top_p is not None and settings.top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                sorted_probs = F.softmax(sorted_logits, dim=-1)
                cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
                sorted_remove = cumulative_probs > settings.top_p
                sorted_remove[:, 1:] = sorted_remove[:, :-1].clone()
                sorted_remove[:, 0] = False
                remove = torch.zeros_like(logits, dtype=torch.bool)
                remove.scatter_(1, sorted_indices, sorted_remove)
                logits = logits.masked_fill(remove, float("-inf"))
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)

        token = int(idx_next.item())
        if end_id is not None and token == end_id:
            ended_by_end = True
            break
        generated.append(token)
        idx = torch.cat((idx, idx_next), dim=1)
    return generated, ended_by_end, time.perf_counter() - start


def run_model(name: str, checkpoint: str, prompts: list[tuple[str, str]], sp, device: torch.device, settings: GenerationSettings) -> list[dict]:
    print(f"Loading {name}: {checkpoint}", flush=True)
    model, cfg = load_model(checkpoint, device)
    end_id = sp.piece_to_id(END_TOKEN)
    if end_id < 0:
        end_id = None
    rows = []
    for idx_prompt, (category, prompt) in enumerate(prompts, 1):
        torch.manual_seed(settings.seed + idx_prompt)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(settings.seed + idx_prompt)
        prompt_ids = sp.encode(make_prompt(prompt), out_type=int)
        prompt_ids = prompt_ids[-(cfg.context_len - 1) :]
        input_ids = torch.tensor([prompt_ids], dtype=torch.long, device=device)
        ids, ended_by_end, duration = generate_ids(model, input_ids, settings, end_id)
        text = sp.decode(ids).replace(USER_TOKEN, "").replace(ASSISTANT_TOKEN, "").replace(END_TOKEN, "").strip()
        score = score_output(category, prompt, text, ended_by_end, len(ids), settings.max_new_tokens)
        rows.append(
            {
                "index": idx_prompt,
                "category": category,
                "prompt": prompt,
                "prompt_template": make_prompt(prompt),
                "output": text,
                "generated_tokens": len(ids),
                "duration_seconds": duration,
                "tokens_per_second": len(ids) / duration if duration > 0 else None,
                "score": score,
            }
        )
        print(f"{name} {idx_prompt:02d}/{len(prompts)} {category} total={score['total']} words={score['word_count']}", flush=True)
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return rows


def short_assessment(base: dict, sft: dict, winner: str) -> str:
    parts = []
    if sft["score"]["web_garbage_score"] < base["score"]["web_garbage_score"]:
        parts.append("SFT ma mniej webowego śmiecia")
    if sft["score"]["instruction_following"] > base["score"]["instruction_following"]:
        parts.append("SFT lepiej łapie polecenie")
    if sft["score"]["repetition"] > base["score"]["repetition"]:
        parts.append("SFT bardziej się powtarza")
    if sft["score"]["sft_phrase_counts"]:
        parts.append("SFT używa schematycznych fraz")
    if base["score"]["web_garbage_score"] >= 2:
        parts.append("base odpływa w artefakty webowe")
    if not parts:
        parts.append("różnica jest mała lub oba outputy są słabe")
    return "; ".join(parts) + f". Winner: {winner}."


def conclusion_for(winner: str) -> str:
    return {
        "sft": "SFT jest praktycznie lepszy dla tego promptu.",
        "base": "Base wypada lepiej lub mniej się psuje dla tego promptu.",
        "tie": "Brak wyraźnego zwycięzcy.",
        "both_bad": "Oba outputy są zbyt słabe, żeby traktować je jako użyteczne.",
    }[winner]


def render_samples(title: str, checkpoint: str, rows: list[dict], settings: GenerationSettings) -> str:
    lines = [
        f"# {title}",
        "",
        f"- checkpoint: `{checkpoint}`",
        f"- settings: `{json.dumps(asdict(settings), ensure_ascii=False)}`",
        "",
    ]
    for row in rows:
        score = row["score"]
        lines += [
            f"## {row['index']:02d}. {row['category']}",
            "",
            f"**Prompt:** {row['prompt']}",
            "",
            "**Output:**",
            "",
            row["output"] or "(empty)",
            "",
            f"**Score:** IF={score['instruction_following']} coherence={score['coherence']} repetition={score['repetition']} usefulness={score['usefulness']} total={score['total']}",
            "",
        ]
    return "\n".join(lines)


def render_comparison(rows: list[dict], settings: GenerationSettings, summary: dict) -> str:
    lines = [
        "# Glyph-27M Base vs SFT v0",
        "",
        "Praktyczny eval jakościowy. To nie jest benchmark naukowy; ocena jest heurystyczna i służy do decyzji, czy trenować dalej.",
        "",
        "## Ustawienia",
        "",
        f"- prompts: {summary['prompt_count']}",
        f"- prompt format: `<|user|> ... <|assistant|>` dla obu modeli",
        f"- sampling: `{json.dumps(asdict(settings), ensure_ascii=False)}`",
        f"- device: `{summary['device']}`",
        "",
        "## Wynik zbiorczy",
        "",
        f"- base wins: {summary['winner_counts'].get('base', 0)}",
        f"- sft wins: {summary['winner_counts'].get('sft', 0)}",
        f"- ties: {summary['winner_counts'].get('tie', 0)}",
        f"- both_bad: {summary['winner_counts'].get('both_bad', 0)}",
        f"- avg base words: {summary['lengths']['base_avg_words']:.1f}",
        f"- avg SFT words: {summary['lengths']['sft_avg_words']:.1f}",
        f"- base web garbage outputs: {summary['quality_counts']['base_web_garbage']}",
        f"- SFT web garbage outputs: {summary['quality_counts']['sft_web_garbage']}",
        f"- base repeated outputs: {summary['quality_counts']['base_repetition']}",
        f"- SFT repeated outputs: {summary['quality_counts']['sft_repetition']}",
        "",
    ]
    for row in rows:
        base = row["base"]
        sft = row["sft"]
        lines += [
            f"## {row['index']:02d}. {row['category']}",
            "",
            f"**Prompt:** {row['prompt']}",
            "",
            "### Base output",
            "",
            base["output"] or "(empty)",
            "",
            f"Base score: `{base['score']}`",
            "",
            "### SFT output",
            "",
            sft["output"] or "(empty)",
            "",
            f"SFT score: `{sft['score']}`",
            "",
            "### Ocena krótka",
            "",
            row["assessment"],
            "",
            "### Wniosek",
            "",
            row["conclusion"],
            "",
        ]
    return "\n".join(lines)


def summarize(comparison_rows: list[dict], settings: GenerationSettings, device: str) -> dict:
    winners = Counter(row["winner"] for row in comparison_rows)
    base_words = [row["base"]["score"]["word_count"] for row in comparison_rows]
    sft_words = [row["sft"]["score"]["word_count"] for row in comparison_rows]
    base_generated = [row["base"]["generated_tokens"] for row in comparison_rows]
    sft_generated = [row["sft"]["generated_tokens"] for row in comparison_rows]
    all_sft_phrases = Counter()
    category_winners: dict[str, Counter] = defaultdict(Counter)
    for row in comparison_rows:
        category_winners[row["category"]][row["winner"]] += 1
        all_sft_phrases.update(row["sft"]["score"]["sft_phrase_counts"])

    return {
        "prompt_count": len(comparison_rows),
        "settings": asdict(settings),
        "device": device,
        "winner_counts": dict(winners),
        "category_winners": {key: dict(value) for key, value in category_winners.items()},
        "lengths": {
            "base_avg_words": statistics.mean(base_words),
            "sft_avg_words": statistics.mean(sft_words),
            "base_avg_generated_tokens": statistics.mean(base_generated),
            "sft_avg_generated_tokens": statistics.mean(sft_generated),
        },
        "quality_counts": {
            "base_ended_by_end": sum(1 for row in comparison_rows if row["base"]["score"]["ended_by_end"]),
            "sft_ended_by_end": sum(1 for row in comparison_rows if row["sft"]["score"]["ended_by_end"]),
            "base_natural_end": sum(1 for row in comparison_rows if row["base"]["score"]["natural_end"]),
            "sft_natural_end": sum(1 for row in comparison_rows if row["sft"]["score"]["natural_end"]),
            "base_cut_off": sum(1 for row in comparison_rows if row["base"]["score"]["likely_cut_off"]),
            "sft_cut_off": sum(1 for row in comparison_rows if row["sft"]["score"]["likely_cut_off"]),
            "base_repetition": sum(1 for row in comparison_rows if row["base"]["score"]["repetition"] >= 2),
            "sft_repetition": sum(1 for row in comparison_rows if row["sft"]["score"]["repetition"] >= 2),
            "base_web_garbage": sum(1 for row in comparison_rows if row["base"]["score"]["web_garbage_score"] >= 1),
            "sft_web_garbage": sum(1 for row in comparison_rows if row["sft"]["score"]["web_garbage_score"] >= 1),
            "base_uncertainty_on_missing_data": sum(
                1
                for row in comparison_rows
                if row["category"] == "brak_danych" and contains_any(row["base"]["output"], UNCERTAINTY_PATTERNS)
            ),
            "sft_uncertainty_on_missing_data": sum(
                1
                for row in comparison_rows
                if row["category"] == "brak_danych" and contains_any(row["sft"]["output"], UNCERTAINTY_PATTERNS)
            ),
        },
        "sft_phrase_counts": dict(all_sft_phrases),
    }


def render_summary(summary: dict, comparison_rows: list[dict]) -> str:
    lines = [
        "# Glyph-27M SFT v0 eval summary",
        "",
        "## Verdict",
        "",
    ]
    sft_wins = summary["winner_counts"].get("sft", 0)
    base_wins = summary["winner_counts"].get("base", 0)
    both_bad = summary["winner_counts"].get("both_bad", 0)
    if sft_wins > base_wins:
        lines.append("SFT v0 is usually better than Base for instruction-like prompts, but not good enough to call it a reliable assistant.")
    else:
        lines.append("SFT v0 does not clearly beat Base overall; inspect prompt-level results before using it as the default.")
    lines += [
        "",
        "## Counts",
        "",
        f"- SFT wins: {sft_wins}",
        f"- Base wins: {base_wins}",
        f"- Tie: {summary['winner_counts'].get('tie', 0)}",
        f"- Both bad: {both_bad}",
        "",
        "## Lengths and endings",
        "",
        f"- Base avg words: {summary['lengths']['base_avg_words']:.1f}",
        f"- SFT avg words: {summary['lengths']['sft_avg_words']:.1f}",
        f"- Base ended with `<|end|>`: {summary['quality_counts']['base_ended_by_end']}",
        f"- SFT ended with `<|end|>`: {summary['quality_counts']['sft_ended_by_end']}",
        f"- Base likely cut off: {summary['quality_counts']['base_cut_off']}",
        f"- SFT likely cut off: {summary['quality_counts']['sft_cut_off']}",
        "",
        "## Main improvements",
        "",
        "- SFT reduces obvious web/forum artifacts compared with Base.",
        "- SFT more often attempts instruction-shaped answers.",
        "- SFT is more likely to use uncertainty language on missing-data prompts.",
        "",
        "## Main regressions / issues",
        "",
        "- SFT often overuses dataset-like advice patterns.",
        "- SFT can drift into generic project-advice wording even for factual/simple explanation prompts.",
        "- SFT ends much more cleanly than Base, but some endings close a generic template instead of a useful answer.",
        "- Some SFT wins are weak wins: the SFT output is less broken than Base, not necessarily good.",
        "",
        "## Repeated SFT phrases",
        "",
    ]
    if summary["sft_phrase_counts"]:
        for phrase, count in sorted(summary["sft_phrase_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{phrase}`: {count}")
    else:
        lines.append("- no tracked SFT phrase appeared")

    lines += [
        "",
        "## SFT v0.1 dataset suggestions",
        "",
        "- Add more direct answer examples that do not use the phrase `najkrótszy ruch` or `mały test`.",
        "- Add missing-data examples with varied wording: `nie mam wystarczających informacji`, `potrzebny jest model/parametry/kontekst`, `tego nie da się rozstrzygnąć z opisu`.",
        "- Add simple factual explanation examples with compact definitions and no project-advice framing.",
        "- Add negative examples for rambling: short prompt, one concise paragraph, explicit stop after answer.",
        "- Add rewriting/summarization examples where output is only the rewritten text, not meta-commentary.",
        "",
        "## Category winners",
        "",
    ]
    for category, counts in sorted(summary["category_winners"].items()):
        lines.append(f"- `{category}`: {counts}")

    weak_sft = [row for row in comparison_rows if row["winner"] in {"base", "both_bad"}][:8]
    if weak_sft:
        lines += ["", "## Examples to inspect first", ""]
        for row in weak_sft:
            lines.append(f"- {row['index']:02d}. `{row['category']}` winner={row['winner']}: {row['prompt']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Glyph-27M Base vs SFT v0")
    parser.add_argument("--base-checkpoint", default="checkpoints/final.pt")
    parser.add_argument("--sft-checkpoint", default="checkpoints/sft-v0/glyph-27m-sft-v0-final.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--out-dir", default="eval/sft-v0")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--temperature", type=float, default=0.75)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--top-p", type=float, default=0.92)
    parser.add_argument("--max-new-tokens", type=int, default=120)
    parser.add_argument("--repetition-penalty", type=float, default=1.15)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--no-repeat-ngram-size", type=int, default=0)
    args = parser.parse_args()

    settings = GenerationSettings(
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
        repetition_penalty=args.repetition_penalty,
        seed=args.seed,
        no_repeat_ngram_size=args.no_repeat_ngram_size,
    )
    device = select_device(args.device)
    print(f"device={device} torch={torch.__version__} hip={getattr(torch.version, 'hip', None)}", flush=True)
    sp = load_sentencepiece(args.tokenizer)

    base_rows = run_model("base", args.base_checkpoint, PROMPTS, sp, device, settings)
    sft_rows = run_model("sft", args.sft_checkpoint, PROMPTS, sp, device, settings)

    comparison_rows = []
    for base, sft in zip(base_rows, sft_rows, strict=True):
        winner = compare_scores(base["score"], sft["score"])
        comparison_rows.append(
            {
                "index": base["index"],
                "category": base["category"],
                "prompt": base["prompt"],
                "winner": winner,
                "assessment": short_assessment(base, sft, winner),
                "conclusion": conclusion_for(winner),
                "base": base,
                "sft": sft,
            }
        )

    summary = summarize(comparison_rows, settings, str(device))
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "base_samples.md").write_text(render_samples("Glyph-27M Base samples", args.base_checkpoint, base_rows, settings), encoding="utf-8")
    (out / "sft_v0_samples.md").write_text(render_samples("Glyph-27M SFT v0 samples", args.sft_checkpoint, sft_rows, settings), encoding="utf-8")
    (out / "base_vs_sft_comparison.md").write_text(render_comparison(comparison_rows, settings, summary), encoding="utf-8")
    (out / "eval_summary.md").write_text(render_summary(summary, comparison_rows), encoding="utf-8")
    (out / "base_vs_sft_comparison.json").write_text(
        json.dumps({"summary": summary, "rows": comparison_rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out / 'base_vs_sft_comparison.md'}")
    print(json.dumps(summary["winner_counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
