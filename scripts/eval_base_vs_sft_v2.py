#!/usr/bin/env python3
"""Stricter qualitative eval: Glyph-27M Base vs Glyph-27M SFT v0.

This keeps the v0 report intact and writes a new v2 report with two extra
dimensions: semantic_relevance and task_completion.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.eval_base_vs_sft import (
    PROMPTS,
    SFT_PHRASES,
    GenerationSettings,
    compare_scores,
    load_sentencepiece,
    run_model,
    score_output,
    select_device,
    web_garbage_score,
)


MISSING_DATA_TERMS = (
    "brakuje",
    "bez danych",
    "nie da się",
    "nie mogę ocenić",
    "nie znam",
    "podaj",
    "potrzeb",
    "zależy",
    "model",
    "cena",
    "zastosowanie",
    "kontekst",
    "parametr",
    "szczegół",
)
PROJECT_ADVICE_TERMS = (
    "mały test",
    "najkrótszy ruch",
    "rdzeń projektu",
    "po tym dalej",
    "w praktyce warto",
    "zacząć od",
    "dopiero potem",
    "kolejne elementy",
    "projekt",
)
COMMAND_TERMS = (
    "popraw tekst",
    "streść",
    "wyciągnij",
    "napisz krótką",
    "odpowiedz krótko",
    "popraw błędne założenie",
)
STOPWORDS = {
    "jest",
    "czy",
    "ten",
    "tego",
    "tym",
    "żeby",
    "która",
    "który",
    "które",
    "oraz",
    "albo",
    "nie",
    "się",
    "jak",
    "dla",
    "bez",
    "przy",
    "czym",
    "różni",
    "jednym",
    "dwóch",
    "zdaniu",
    "tekst",
    "krótko",
    "prosto",
}


EXPECTED_TERMS: dict[str, tuple[str, ...]] = {
    "Czy ten laptop jest dobry?": ("laptop", "model", "cena", "zastosowanie", "parametr", "specyfikacja"),
    "Czy ten wynik jest poprawny?": ("wynik", "dane", "obliczenie", "metoda", "kontekst"),
    "Czy to jest bezpieczne?": ("bezpiecz", "ryzyko", "kontekst", "dane", "sytuacja"),
    "Czy powinienem to kupić?": ("kup", "cena", "potrzeb", "zastosowanie", "budżet"),
    "Czy moja odpowiedź jest dobra?": ("odpowiedź", "treść", "kryteria", "cel", "ocenić"),
    "Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.": (
        "projekt",
        "dobry",
        "funkcj",
        "działa",
    ),
    "Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.": (
        "uważam",
        "problem",
        "rozwiąz",
        "szybko",
    ),
    "Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.": (
        "dzień dobry",
        "nauczyciel",
        "nie zdąż",
        "pracy",
        "przeprasz",
    ),
    "Skróć tekst: Ten projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.": (
        "projekt",
        "ciekawy",
        "zbyt wiele",
        "funkcj",
        "start",
    ),
    "Napisz neutralną wiadomość, że nie mogę dziś przyjść.": (
        "nie mogę",
        "przyjść",
        "dziś",
        "przeprasz",
        "dziękuję",
    ),
    "Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.": (
        "projekt",
        "upada",
        "zakres",
        "zbyt szerok",
    ),
    "Streść w dwóch zdaniach: Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt, plik tekstowy albo arkusz.": (
        "problem",
        "aplikac",
        "prosty",
        "skrypt",
        "arkusz",
    ),
    "Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.": (
        "uczenie",
        "czytanie",
        "zrozumienie",
        "znajomość",
    ),
    "Streść tekst: Najpierw trzeba zbudować działający prototyp. Dopiero potem warto poprawiać wygląd i automatyzację.": (
        "prototyp",
        "najpierw",
        "wygląd",
        "automatyzac",
    ),
    "Streść w jednym zdaniu: Dobry plan zaczyna się od małego testu, który pokazuje, czy warto rozwijać pomysł dalej.": (
        "plan",
        "test",
        "pomysł",
        "rozwijać",
    ),
    "Wyjaśnij prosto, czym różni się pogoda od klimatu.": ("pogoda", "klimat", "krótk", "dług", "średni"),
    "Wyjaśnij, czym jest inflacja.": ("inflac", "ceny", "pieniądz", "drożej", "wartość"),
    "Czym różni się fakt od opinii?": ("fakt", "opinia", "sprawdz", "subiektyw", "dowód"),
    "Wyjaśnij krótko, czym jest grawitacja.": ("grawitac", "przyciąg", "siła", "ziemia", "masa"),
    "Czym różni się masa od wagi?": ("masa", "waga", "ciężar", "grawitac", "kilogram"),
    "Mam zacząć projekt od UI czy od logiki?": ("logik", "ui", "najpierw", "działa", "interfejs"),
    "Mam ambitny projekt i chcę od razu zrobić backend, frontend, dashboard, AI, logowanie i ładne UI. Dobry plan?": (
        "zakres",
        "najpierw",
        "mvp",
        "prosto",
        "funkcj",
    ),
    "Mam dwie opcje: zrobić projekt szybko i prosto albo długo dopracowywać wszystkie detale. Co wybrać?": (
        "prosto",
        "szybko",
        "detal",
        "wersj",
    ),
    "Czy warto robić projekt, jeśli nie wiem jeszcze, czy go skończę?": ("projekt", "warto", "mały", "zakres", "skończ"),
    "Mam wybrać łatwiejszą czy ambitniejszą wersję projektu.": ("łatwiejsz", "ambitniejsz", "wersj", "wybierz"),
    "Popraw błędne założenie: droższy sprzęt zawsze jest lepszy.": ("droższ", "sprzęt", "lepsz", "potrzeb", "zastosowanie"),
    "Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.": (
        "ai",
        "projekt",
        "zaawans",
        "wartość",
        "problem",
    ),
    "Popraw błędne założenie: jak projekt ma dużo funkcji, to jest lepszy.": (
        "funkcj",
        "lepsz",
        "prostszy",
        "użytecz",
    ),
    "Popraw błędne założenie: Docker to to samo co maszyna wirtualna.": (
        "docker",
        "kontener",
        "maszyna",
        "wirtual",
        "system",
    ),
    "Popraw błędne założenie: im dłuższa odpowiedź, tym jest mądrzejsza.": (
        "dłuższ",
        "odpowiedź",
        "mądr",
        "konkret",
    ),
    "Czym jest backup?": ("backup", "kopia", "dane", "odzyskać", "utrata"),
    "Czym różni się plik od folderu?": ("plik", "folder", "katalog", "zawiera"),
    "Czy chmura jest zawsze lepsza niż lokalny serwer?": ("chmura", "lokalny", "serwer", "zależy"),
    "Czym różni się aplikacja od strony internetowej?": ("aplikac", "strona", "przeglądark", "program"),
    "Czym różni się CPU usage od load average?": ("cpu", "usage", "load", "proces", "kolejk"),
    "Napisz krótką odpowiedź i nie powtarzaj tej samej myśli.": ("krótk", "nie powtarz", "jedna", "myśl"),
    "Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?": (
        "nie",
        "konkret",
        "woda",
        "mądr",
    ),
    "Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego.": (
        "zapętla",
        "powtarz",
        "czytel",
        "sens",
    ),
    "Odpowiedz krótko: czego nie da się ocenić bez danych?": ("bez danych", "ocenić", "wynik", "jakość", "bezpieczeństwo"),
    "Odpowiedz krótko i zakończ po jednej myśli: co zrobić, gdy brakuje informacji?": (
        "brakuje",
        "informac",
        "dopytać",
        "dane",
    ),
}


def words(text: str) -> list[str]:
    return re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", text.lower())


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def prompt_keywords(prompt: str) -> set[str]:
    return {word for word in words(prompt) if len(word) >= 4 and word not in STOPWORDS}


def overlap_count(prompt: str, output: str) -> int:
    keys = prompt_keywords(prompt)
    out_words = set(words(output))
    return sum(1 for key in keys if any(word.startswith(key[:5]) or key.startswith(word[:5]) for word in out_words))


def answer_repeats_question(prompt: str, output: str) -> bool:
    out = " ".join(words(output))
    pr = " ".join(words(prompt))
    if not out:
        return False
    if out == pr:
        return True
    out_tokens = words(output)
    prompt_tokens = set(words(prompt))
    if len(out_tokens) <= len(prompt_tokens) + 3 and sum(1 for token in out_tokens if token in prompt_tokens) >= max(3, len(out_tokens) - 1):
        return True
    return False


def expected_hit_count(prompt: str, output: str) -> int:
    expected = EXPECTED_TERMS.get(prompt, ())
    lower = output.lower()
    return sum(1 for term in expected if term in lower)


def project_advice_drift(category: str, output: str) -> bool:
    if category == "decyzje_projektowe":
        return False
    lower = output.lower()
    hits = sum(1 for term in PROJECT_ADVICE_TERMS if term in lower)
    return hits >= 2


def command_echo(output: str) -> bool:
    return contains_any(output, COMMAND_TERMS)


def semantic_relevance(category: str, prompt: str, output: str, old_score: dict) -> int:
    text = output.strip()
    if not text or old_score["web_garbage_score"] >= 2 or old_score["coherence"] == 0:
        return 0
    if answer_repeats_question(prompt, text):
        return 0
    hits = expected_hit_count(prompt, text)
    overlap = overlap_count(prompt, text)
    drift = project_advice_drift(category, text)

    if category == "brak_danych":
        missing = contains_any(text, MISSING_DATA_TERMS)
        if missing and (hits >= 2 or overlap >= 2):
            return 3
        if missing:
            return 2
        if overlap >= 2:
            return 1
        return 0

    if category in {"pisanie_i_poprawianie", "streszczanie"}:
        if command_echo(text) and hits < 2:
            return 0
        if drift and hits < 2:
            return 1
        if hits >= 2:
            return 3 if old_score["coherence"] >= 2 else 2
        if overlap >= 2:
            return 2
        return 0

    if category == "korekta_zalozen":
        correction = contains_any(text, ("nie zawsze", "nie oznacza", "to zależy", "ważniejsze", "błęd"))
        if correction and hits >= 2:
            return 3
        if correction or hits >= 2:
            return 2
        return 1 if overlap >= 2 else 0

    if category == "decyzje_projektowe":
        if hits >= 2 or contains_any(text, ("wybierz", "najpierw", "zacznij", "prosts", "logik")):
            return 3 if old_score["coherence"] >= 2 else 2
        return 1 if overlap >= 2 else 0

    if category == "anty_petle":
        if old_score["repetition"] >= 2:
            return 1
        if hits >= 2 or overlap >= 2 or contains_any(text, ("danych", "informac", "nie powtarz", "krótko")):
            return 3 if old_score["coherence"] >= 2 else 2
        return 1 if text else 0

    if drift and hits < 2:
        return 1
    if hits >= 2:
        return 3 if old_score["coherence"] >= 2 else 2
    if overlap >= 2:
        return 2
    if overlap == 1:
        return 1
    return 0


def task_completion(category: str, prompt: str, output: str, old_score: dict, sem: int) -> int:
    text = output.strip()
    if not text or sem == 0 or answer_repeats_question(prompt, text):
        return 0
    lower = text.lower()
    word_count = old_score["word_count"]

    if category == "brak_danych":
        if contains_any(text, MISSING_DATA_TERMS) and sem >= 2:
            return 3
        return 1

    if category == "pisanie_i_poprawianie":
        if "popraw tekst" in prompt.lower() or "skróć tekst" in prompt.lower():
            if command_echo(text) or contains_any(text, ("trzeba", "warto", "najpierw", "podejdź")) and expected_hit_count(prompt, text) < 2:
                return 1
            return 3 if sem >= 2 and word_count <= 45 else 2
        if "wiadomość" in prompt.lower():
            if contains_any(lower, ("dzień dobry", "przeprasz", "nie zdąż", "nie mogę", "przyjść", "pracy")):
                return 3
            return 1
        return 2 if sem >= 2 else 1

    if category == "streszczanie":
        if command_echo(text):
            return 1
        if word_count <= 35 and sem >= 2:
            return 3
        if word_count <= 55 and sem >= 2:
            return 2
        return 1

    if category == "proste_wyjasnienia":
        if sem >= 3 and 8 <= word_count <= 65:
            return 3
        if sem >= 2:
            return 2
        return 1

    if category == "decyzje_projektowe":
        if sem >= 2 and contains_any(lower, ("wybierz", "zacznij", "najpierw", "lepiej", "warto")):
            return 3 if word_count <= 80 else 2
        return 1

    if category == "korekta_zalozen":
        if sem >= 2 and contains_any(lower, ("nie zawsze", "nie oznacza", "to zależy", "ważniejsze", "nie jest")):
            return 3
        return 1

    if category in {"techniczne_proste", "anty_petle"}:
        if sem >= 2 and old_score["repetition"] <= 1 and word_count <= 75:
            return 3
        if sem >= 2:
            return 2
        return 1

    return 2 if sem >= 2 else 1


def score_output_v2(category: str, prompt: str, text: str, old_score: dict | None = None) -> dict:
    if old_score is None:
        old_score = score_output(category, prompt, text, False, 0, 120)
    sem = semantic_relevance(category, prompt, text, old_score)
    task = task_completion(category, prompt, text, old_score, sem)
    echo = answer_repeats_question(prompt, text)
    drift = project_advice_drift(category, text)
    weak = (
        sem <= 1
        or task <= 1
        or echo
        or old_score["web_garbage_score"] >= 2
        or old_score["coherence"] == 0
    )
    total = (
        sem * 3
        + task * 3
        + old_score["coherence"]
        + old_score["usefulness"]
        - old_score["repetition"] * 2
        - min(old_score["web_garbage_score"], 3)
        - (1 if drift else 0)
    )
    if weak:
        total = min(total, 5)
    result = dict(old_score)
    result.update(
        {
            "semantic_relevance": int(sem),
            "task_completion": int(task),
            "question_echo": bool(echo),
            "project_advice_drift": bool(drift),
            "can_win": not weak,
            "total_v2": int(total),
        }
    )
    return result


def compare_scores_v2(base: dict, sft: dict) -> str:
    base_can = base["can_win"]
    sft_can = sft["can_win"]
    if not base_can and not sft_can:
        return "both_bad"
    if sft_can and not base_can:
        return "sft"
    if base_can and not sft_can:
        return "base"
    diff = sft["total_v2"] - base["total_v2"]
    if diff >= 3:
        return "sft"
    if diff <= -3:
        return "base"
    if max(base["total_v2"], sft["total_v2"]) <= 5:
        return "both_bad"
    return "tie"


def render_comparison_v2(rows: list[dict], settings: GenerationSettings, summary: dict) -> str:
    lines = [
        "# Glyph-27M Base vs SFT v0 - eval v2",
        "",
        "Stricter qualitative eval. This version adds semantic_relevance and task_completion and blocks wins for outputs that only end cleanly but do not answer the prompt.",
        "",
        "## Settings",
        "",
        f"- prompts: {summary['prompt_count']}",
        f"- sampling: `{json.dumps(asdict(settings), ensure_ascii=False)}`",
        f"- device: `{summary['device']}`",
        "",
        "## Winner counts",
        "",
        f"- old: `{summary['old_winner_counts']}`",
        f"- new: `{summary['winner_counts']}`",
        f"- weak SFT wins removed: {summary['weak_sft_wins_removed']}",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['index']:02d}. {row['category']}",
            "",
            f"**Prompt:** {row['prompt']}",
            "",
            f"Old winner: `{row['old_winner']}` · New winner: `{row['winner']}`",
            "",
            "### Base",
            "",
            row["base"]["output"] or "(empty)",
            "",
            f"Score v2: `{row['base']['score_v2']}`",
            "",
            "### SFT",
            "",
            row["sft"]["output"] or "(empty)",
            "",
            f"Score v2: `{row['sft']['score_v2']}`",
            "",
            f"**Assessment:** {row['assessment']}",
            "",
        ]
    return "\n".join(lines)


def summarize_v2(rows: list[dict], settings: GenerationSettings, device: str, old_counts: dict) -> dict:
    winners = Counter(row["winner"] for row in rows)
    old_winners = Counter(row["old_winner"] for row in rows)
    sft_sem = [row["sft"]["score_v2"]["semantic_relevance"] for row in rows]
    base_sem = [row["base"]["score_v2"]["semantic_relevance"] for row in rows]
    sft_task = [row["sft"]["score_v2"]["task_completion"] for row in rows]
    base_task = [row["base"]["score_v2"]["task_completion"] for row in rows]
    weak_removed = sum(1 for row in rows if row["old_winner"] == "sft" and row["winner"] != "sft")
    category_winners: dict[str, Counter] = defaultdict(Counter)
    phrase_counts = Counter()
    for row in rows:
        category_winners[row["category"]][row["winner"]] += 1
        phrase_counts.update(row["sft"]["score_v2"].get("sft_phrase_counts") or {})
    return {
        "prompt_count": len(rows),
        "settings": asdict(settings),
        "device": device,
        "old_winner_counts": old_counts or dict(old_winners),
        "old_recomputed_winner_counts": dict(old_winners),
        "winner_counts": dict(winners),
        "weak_sft_wins_removed": weak_removed,
        "category_winners": {key: dict(value) for key, value in category_winners.items()},
        "averages": {
            "base_semantic_relevance": round(statistics.mean(base_sem), 3),
            "sft_semantic_relevance": round(statistics.mean(sft_sem), 3),
            "base_task_completion": round(statistics.mean(base_task), 3),
            "sft_task_completion": round(statistics.mean(sft_task), 3),
        },
        "quality_counts": {
            "base_cannot_win": sum(1 for row in rows if not row["base"]["score_v2"]["can_win"]),
            "sft_cannot_win": sum(1 for row in rows if not row["sft"]["score_v2"]["can_win"]),
            "base_question_echo": sum(1 for row in rows if row["base"]["score_v2"]["question_echo"]),
            "sft_question_echo": sum(1 for row in rows if row["sft"]["score_v2"]["question_echo"]),
            "base_project_advice_drift": sum(1 for row in rows if row["base"]["score_v2"]["project_advice_drift"]),
            "sft_project_advice_drift": sum(1 for row in rows if row["sft"]["score_v2"]["project_advice_drift"]),
        },
        "sft_phrase_counts": dict(phrase_counts),
    }


def render_summary_v2(summary: dict, rows: list[dict]) -> str:
    lines = [
        "# Glyph-27M SFT v0 eval summary v2",
        "",
        "## Verdict",
        "",
    ]
    sft_wins = summary["winner_counts"].get("sft", 0)
    base_wins = summary["winner_counts"].get("base", 0)
    if sft_wins > base_wins:
        lines.append("SFT v0 still beats Base under the stricter scoring, but the margin is much less flattering than the old heuristic if weak wins are removed.")
    else:
        lines.append("Under stricter scoring, SFT v0 no longer clearly beats Base. Inspect failures before using it as the default.")
    lines += [
        "",
        "## Old vs new counts",
        "",
        f"- old counts from eval v1: `{summary['old_winner_counts']}`",
        f"- old counts recomputed in this run: `{summary['old_recomputed_winner_counts']}`",
        f"- new counts: `{summary['winner_counts']}`",
        f"- weak SFT wins removed: {summary['weak_sft_wins_removed']}",
        "",
        "## New average scores",
        "",
        f"- base semantic_relevance: {summary['averages']['base_semantic_relevance']:.2f}/3",
        f"- SFT semantic_relevance: {summary['averages']['sft_semantic_relevance']:.2f}/3",
        f"- base task_completion: {summary['averages']['base_task_completion']:.2f}/3",
        f"- SFT task_completion: {summary['averages']['sft_task_completion']:.2f}/3",
        "",
        "## New failure counters",
        "",
    ]
    for key, value in summary["quality_counts"].items():
        lines.append(f"- {key}: {value}")
    lines += [
        "",
        "## Repeated SFT phrases",
        "",
    ]
    if summary["sft_phrase_counts"]:
        for phrase, count in sorted(summary["sft_phrase_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{phrase}`: {count}")
    else:
        lines.append("- no tracked phrase appeared")
    lines += [
        "",
        "## Main read",
        "",
        "- Clean ending is useful, but it is no longer enough to win.",
        "- Rewriting and summarization remain the weakest practical areas.",
        "- Missing-data behavior improved slightly, but is still not reliable.",
        "- Factual definitions still need direct-answer data in SFT v0.1.",
        "",
        "## Examples to inspect first",
        "",
    ]
    for row in [r for r in rows if r["winner"] in {"both_bad", "base"}][:12]:
        lines.append(
            f"- {row['index']:02d}. `{row['category']}` old={row['old_winner']} new={row['winner']}: {row['prompt']}"
        )
    lines.append("")
    return "\n".join(lines)


def assessment_v2(base: dict, sft: dict, winner: str) -> str:
    b = base["score_v2"]
    s = sft["score_v2"]
    parts = [
        f"semantic base/SFT={b['semantic_relevance']}/{s['semantic_relevance']}",
        f"task base/SFT={b['task_completion']}/{s['task_completion']}",
    ]
    if s["project_advice_drift"]:
        parts.append("SFT drifts into project-advice template")
    if s["question_echo"]:
        parts.append("SFT mostly echoes the prompt")
    if not s["can_win"]:
        parts.append("SFT cannot win under v2 gates")
    parts.append(f"winner={winner}")
    return "; ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Glyph-27M Base vs SFT v0 with stricter v2 gates")
    parser.add_argument("--base-checkpoint", default="checkpoints/final.pt")
    parser.add_argument("--sft-checkpoint", default="checkpoints/sft-v0/glyph-27m-sft-v0-final.pt")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--old-json", default="eval/sft-v0/base_vs_sft_comparison.json")
    parser.add_argument("--out-dir", default="eval/sft-v0-v2")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--temperature", type=float, default=0.75)
    parser.add_argument("--top-k", type=int, default=40)
    parser.add_argument("--top-p", type=float, default=0.92)
    parser.add_argument("--max-new-tokens", type=int, default=120)
    parser.add_argument("--repetition-penalty", type=float, default=1.15)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    settings = GenerationSettings(
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
        repetition_penalty=args.repetition_penalty,
        seed=args.seed,
    )
    device = select_device(args.device)
    sp = load_sentencepiece(args.tokenizer)
    base_rows = run_model("base-v2", args.base_checkpoint, PROMPTS, sp, device, settings)
    sft_rows = run_model("sft-v2", args.sft_checkpoint, PROMPTS, sp, device, settings)

    old_counts = {}
    try:
        old_counts = json.loads(Path(args.old_json).read_text(encoding="utf-8")).get("summary", {}).get("winner_counts", {})
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    rows = []
    for base, sft in zip(base_rows, sft_rows, strict=True):
        old_winner = compare_scores(base["score"], sft["score"])
        base["score_v2"] = score_output_v2(base["category"], base["prompt"], base["output"], base["score"])
        sft["score_v2"] = score_output_v2(sft["category"], sft["prompt"], sft["output"], sft["score"])
        winner = compare_scores_v2(base["score_v2"], sft["score_v2"])
        rows.append(
            {
                "index": base["index"],
                "category": base["category"],
                "prompt": base["prompt"],
                "old_winner": old_winner,
                "winner": winner,
                "assessment": assessment_v2(base, sft, winner),
                "base": base,
                "sft": sft,
            }
        )

    summary = summarize_v2(rows, settings, str(device), old_counts)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "base_vs_sft_comparison_v2.md").write_text(render_comparison_v2(rows, settings, summary), encoding="utf-8")
    (out / "eval_summary_v2.md").write_text(render_summary_v2(summary, rows), encoding="utf-8")
    (out / "base_vs_sft_comparison_v2.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {out / 'base_vs_sft_comparison_v2.md'}")
    print(json.dumps(summary["winner_counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
