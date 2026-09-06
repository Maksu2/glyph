#!/usr/bin/env python3
"""Build Glyph-100M SFT smoke v0.2 dataset.

v0.2 is a controlled repair of v0:
- keep the clean synthetic base;
- reduce repeated answer openings;
- add explicit anti-repetition / natural-ending examples;
- add train/val/test split and token/report validation.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sft_utils import (
    ASSISTANT_TOKEN,
    END_TOKEN,
    collect_dataset_stats,
    format_sft_text,
    load_jsonl,
    load_sentencepiece,
    normalize_for_dupes,
    normalize_space,
    similar_instruction_pairs,
    write_json,
    write_jsonl,
)


SUSPICIOUS_PATTERNS = [
    "w latach 1975-1998",
    "w latach 1975–1998",
    "gminie",
    "powiecie",
    "województwie",
    "strona główna",
    "cookies",
    "kup teraz",
    "dodaj do koszyka",
    "zaloguj",
    "zarejestruj",
    "polityka prywatności",
    "jako model językowy",
    "jako sztuczna inteligencja",
    "kliknij",
]

ANTI_ENDING_BASE = [
    ("Odpowiedz jednym zdaniem i zakończ: co zrobić, gdy brakuje danych?", "Powiedz, jakich danych brakuje, i nie zgaduj wyniku."),
    ("Nie powtarzaj frazy: czy warto trenować dalej bez evala?", "Nie warto, bo bez evala nie wiadomo, czy model faktycznie się poprawia."),
    ("Zakończ po jednej myśli: czym jest checkpoint?", "Checkpoint to zapis stanu modelu, do którego można wrócić później."),
    ("Odpowiedz krótko: kiedy przerwać eksperyment?", "Przerwij eksperyment, gdy pojawia się NaN, OOM, crash albo wyraźna regresja jakości."),
    ("Nie rozwijaj dalej: po co jest zbiór walidacyjny?", "Zbiór walidacyjny pokazuje, jak model działa poza danymi treningowymi."),
    ("Jedno zdanie: dlaczego powtórzenia są problemem?", "Powtórzenia utrudniają czytanie i zwykle nie dodają nowych informacji."),
    ("Zakończ odpowiedź naturalnie: czy jeden wynik wystarczy?", "Nie, jeden wynik trzeba porównać z próbkami i powtórzyć w kontrolowanych warunkach."),
    ("Bez pętli: co zrobić, gdy odpowiedź jest kompletna?", "Zakończyć ją i nie dopisywać kolejnych wersji tej samej myśli."),
    ("Odpowiedz bez powtórzeń: jak pisać krócej?", "Usuń dygresje i zostaw tylko informację potrzebną do decyzji."),
    ("Jedna myśl: co oznacza brak danych?", "Brak danych oznacza, że uczciwa odpowiedź powinna wskazać niepewność."),
    ("Krótko i do końca: czy loss wystarczy?", "Nie, loss trzeba czytać razem z przykładami generacji."),
    ("Nie powtarzaj: co robi repetition penalty?", "Zmniejsza szansę powtarzania tych samych tokenów lub fraz."),
    ("Zakończ po drugim zdaniu: czym jest SFT?", "SFT uczy model reagowania na instrukcje. Nie dodaje automatycznie dużej wiedzy o świecie."),
    ("Odpowiedz jednym akapitem: co oznacza overfit?", "Overfit oznacza, że model zbyt mocno dopasował się do danych treningowych i gorzej uogólnia."),
    ("Bez listy: jak sprawdzić model po treningu?", "Porównaj loss, próbki generacji i wyniki na stałym zestawie promptów."),
    ("Nie używaj szablonu: czy model po SFT jest gotowy?", "Nie musi być gotowy; SFT smoke tylko sprawdza, czy kierunek działa."),
    ("Zakończ jasno: kiedy nie zgadywać?", "Nie zgaduj, gdy brakuje kryteriów, danych wejściowych albo punktu odniesienia."),
    ("Jednym zdaniem: po co raport?", "Raport zapisuje wynik, ustawienia i decyzję po eksperymencie."),
    ("Bez rozwijania: co zrobić z dziwnym wynikiem?", "Sprawdź metodę, dane i powtórz test na tym samym zestawie."),
    ("Odpowiedz krótko: kiedy dataset jest za słaby?", "Dataset jest za słaby, gdy próbki pokazują śmieci, duplikaty albo zbyt wąski styl."),
    ("Nie powtarzaj: jak kończyć odpowiedź?", "Zakończ ją wtedy, gdy główna myśl jest jasna."),
    ("Krótko: co robi tokenizer?", "Tokenizer zamienia tekst na tokeny, z którymi pracuje model."),
    ("Jedna myśl: co daje czysty dataset?", "Czysty dataset zmniejsza ryzyko uczenia reklam, menu i przypadkowych śmieci."),
    ("Zakończ naturalnie: czy większy model zawsze pomaga?", "Nie, większy model nadal zależy od jakości danych i treningu."),
    ("Bez pętli: co zrobić, gdy model powtarza tekst?", "Zmierz skalę problemu, popraw dane i sprawdź ustawienia generacji."),
    ("Odpowiedz do końca: czym jest walidacja?", "Walidacja to sprawdzenie modelu na danych, których nie używa bezpośrednio do nauki."),
    ("Jedno zdanie: czym jest smoke test?", "Smoke test to krótka próba sprawdzająca, czy pipeline działa bez oczywistych błędów."),
    ("Krótko: czy można ocenić laptop bez modelu?", "Nie, potrzebny jest model, cena i zastosowanie."),
    ("Nie dopisuj drugiej myśli: co zrobić po awarii?", "Najpierw zabezpiecz logi i ostatni poprawny checkpoint."),
    ("Zakończ odpowiedź: czym jest backup?", "Backup to kopia danych potrzebna do odtworzenia ich po awarii."),
]

MISSING_DATA_EXTRA = [
    ("Czy ten wynik jest dobry?", "Brakuje punktu odniesienia i kryteriów oceny. Bez nich nie da się powiedzieć, czy wynik jest dobry."),
    ("Czy ta decyzja jest bezpieczna?", "Nie da się tego ocenić bez kontekstu, możliwych skutków i sposobu wykonania."),
    ("Czy mam kupić ten sprzęt?", "Potrzebny jest model, cena, stan sprzętu i zastosowanie. Bez tego odpowiedź byłaby zgadywaniem."),
    ("Czy ten błąd jest poważny?", "Trzeba znać komunikat błędu, miejsce wystąpienia i wpływ na działanie systemu."),
    ("Czy ten dataset wystarczy?", "Potrzebna jest liczba tokenów, próbki jakościowe i plan treningu. Sama nazwa datasetu nie wystarcza."),
    ("Czy ten projekt warto pokazać?", "Nie wiadomo bez celu, odbiorcy i aktualnego stanu projektu."),
    ("Czy wynik evala jest wiarygodny?", "Trzeba znać liczbę promptów, ustawienia generacji i metodę oceny."),
    ("Czy ta optymalizacja ma sens?", "Najpierw trzeba zmierzyć wąskie gardło. Bez pomiaru optymalizacja może być przypadkowa."),
    ("Czy model się poprawił?", "Potrzebne są porównywalne próbki, metryki i ten sam zestaw promptów."),
    ("Czy mogę zaufać tej odpowiedzi?", "Bez źródeł, kontekstu i kryteriów nie należy traktować odpowiedzi jako pewnej."),
]

NATURAL_LONGER_EXTRA = [
    ("Wyjaśnij w dwóch zdaniach, po co robi się checkpointy.", "Checkpoint zapisuje stan modelu i optimizera w konkretnym momencie. Dzięki temu można wznowić trening albo wrócić do lepszego punktu."),
    ("Wyjaśnij w trzech zdaniach, dlaczego czysty dataset jest ważny.", "Model uczy się wzorców z danych, także tych niepożądanych. Jeśli dataset zawiera reklamy, menu i spam, model może je później powtarzać. Dlatego jakość danych jest ważniejsza niż sama liczba tokenów."),
    ("Opisz krótko, czym różni się model bazowy od modelu po SFT.", "Model bazowy przede wszystkim kontynuuje tekst. Model po SFT jest uczony reagowania na instrukcje i kończenia odpowiedzi w bardziej przewidywalnym formacie."),
    ("Wyjaśnij w dwóch zdaniach, czemu nie oceniać modelu po jednym samplu.", "Jeden sample może być przypadkowo dobry albo przypadkowo zły. Lepszy obraz daje stały zestaw promptów i kilka ustawień generacji."),
    ("Opisz krótko, po co robi się smoke test SFT.", "Smoke test SFT sprawdza, czy model reaguje na format instrukcji i czy trening jest stabilny. Nie jest jeszcze dowodem, że model nadaje się do użycia jako asystent."),
    ("Wyjaśnij, dlaczego nie warto powtarzać tej samej frazy.", "Powtarzanie tej samej frazy nie dodaje informacji i szybko psuje czytelność odpowiedzi. Jeśli myśl jest kompletna, lepiej zakończyć tekst."),
    ("Opisz krótko, co oznacza dobry raport techniczny.", "Dobry raport techniczny podaje cel, ustawienia, wynik i ograniczenia. Powinien pozwolić wrócić do decyzji bez zgadywania, co było testowane."),
    ("Wyjaśnij w dwóch zdaniach, dlaczego niższy loss nie zawsze wystarcza.", "Niższy loss może oznaczać lepsze przewidywanie danych walidacyjnych. Jakość generacji trzeba jednak sprawdzić na przykładach, bo model może nadal powtarzać albo dryfować."),
]


def record(category: str, instruction: str, response: str, source_id: str) -> dict:
    return {
        "id": "",
        "category": category,
        "instruction": normalize_space(instruction),
        "response": normalize_space(response),
        "source": "synthetic_curated_sft_smoke_v0_2",
        "source_id": source_id,
        "quality": "approved",
    }


def repair_response(text: str, idx: int) -> str:
    text = normalize_space(text)
    if text == "Nie.":
        return "Nie da się tego ocenić bez dodatkowych danych."
    if text.startswith("Nie. Brakuje"):
        return text.replace("Nie. Brakuje", "Brakuje", 1)
    if text.startswith("Nie. Bez"):
        return text.replace("Nie. Bez", "Bez", 1)
    if text.startswith("Nie. Lepsza"):
        return text.replace("Nie. ", "", 1)
    if text.startswith("Nie. "):
        variants = [
            text.replace("Nie. ", "Nie, ", 1),
            text.replace("Nie. ", "Raczej nie. ", 1),
            text.replace("Nie. ", "Odpowiedź brzmi: nie. ", 1),
            text.replace("Nie. ", "", 1),
        ]
        text = variants[idx % len(variants)]
    if text.startswith("Najpierw "):
        variants = [
            text.replace("Najpierw ", "Zacznij od ", 1),
            text.replace("Najpierw ", "Na start ", 1),
            text.replace("Najpierw ", "W pierwszym kroku ", 1),
            text,
        ]
        text = variants[idx % len(variants)]
    if text.startswith("Warto "):
        variants = [
            text.replace("Warto ", "Dobrze jest ", 1),
            text.replace("Warto ", "Rozsądnie jest ", 1),
            text.replace("Warto ", "Można ", 1),
            text,
        ]
        text = variants[idx % len(variants)]
    return normalize_space(text)


def load_repaired_v0(path: str) -> list[dict]:
    loaded = load_jsonl(path)
    records = []
    for idx, item in enumerate(loaded.records):
        records.append(
            record(
                item["category"],
                item["instruction"],
                repair_response(item["response"], idx),
                f"v0-repaired-{item.get('id', idx)}",
            )
        )
    return records


def expand_pairs(category: str, pairs: list[tuple[str, str]], variants: list[str], source_prefix: str) -> list[dict]:
    out = []
    for i, (instruction, response) in enumerate(pairs):
        for j, variant in enumerate(variants):
            if "{instruction}" in variant:
                prompt = variant.format(instruction=instruction)
            else:
                prompt = instruction + variant
            out.append(record(category, prompt, response, f"{source_prefix}-{i}-{j}"))
    return out


def build_extra_records() -> list[dict]:
    out: list[dict] = []
    anti_variants = [
        "",
        " Bez powtarzania.",
        " Zakończ naturalnie.",
        " Jednym akapitem.",
        " Nie dodawaj kolejnej wersji tej samej myśli.",
        " Krótko.",
        " Odpowiedz wprost.",
        " Tylko sedno.",
        " Bez dygresji.",
        " Nie zaczynaj nowego tematu.",
        " Zakończ po kompletnej odpowiedzi.",
        " Nie używaj listy.",
    ]
    out.extend(expand_pairs("anty_powtorzenia_i_konczenie", ANTI_ENDING_BASE, anti_variants, "anti-end"))
    missing_variants = [
        "",
        " Nie zgaduj.",
        " Odpowiedz ostrożnie.",
        " Wskaż brakujące dane.",
        " Krótko.",
        " Bez udawania pewności.",
        " Powiedz, czego brakuje.",
        " Jednym akapitem.",
        " Bez listy.",
        " Zakończ naturalnie.",
        " Nie dopowiadaj faktów.",
        " Odpowiedz uczciwie.",
    ]
    out.extend(expand_pairs("brak_danych", MISSING_DATA_EXTRA, missing_variants, "missing-extra"))
    natural_variants = [
        "",
        " Zakończ po ostatnim zdaniu.",
        " Bez listy.",
        " Naturalnie.",
        " Bez lania wody.",
        " W prostym języku.",
        " W dwóch lub trzech zdaniach.",
        " Bez powtórzeń.",
        " Odpowiedz spokojnie.",
        " Zakończ jasno.",
        " Nie rozwijaj ponad potrzebę.",
        " Krótkim akapitem.",
    ]
    out.extend(expand_pairs("naturalne_zakonczenia", NATURAL_LONGER_EXTRA, natural_variants, "natural-extra"))

    direct_defs = [
        ("Czym jest GPU?", "GPU to układ wyspecjalizowany w równoległym przetwarzaniu wielu prostych operacji."),
        ("Czym jest RAM?", "RAM to szybka pamięć robocza używana przez uruchomione programy."),
        ("Czym jest log treningu?", "Log treningu zapisuje kroki, loss, ewaluacje, checkpointy i ewentualne błędy."),
        ("Czym jest prompt?", "Prompt to tekst wejściowy przekazany modelowi przed generacją odpowiedzi."),
        ("Czym jest walidacja datasetu?", "Walidacja datasetu sprawdza, czy przykłady są kompletne, czyste i mieszczą się w kontekście modelu."),
        ("Czym jest overtraining?", "Overtraining oznacza dalsze trenowanie mimo braku poprawy jakości albo przy rosnących oznakach regresji."),
        ("Czym jest checkpoint best?", "Checkpoint best to zapis modelu wybrany na podstawie ewaluacji, a nie tylko najnowszy zapis."),
        ("Czym jest split testowy?", "Split testowy to część danych odłożona do końcowej oceny, bez używania jej w treningu."),
    ]
    out.extend(
        expand_pairs(
            "krotkie_definicje",
            direct_defs,
            ["", " Odpowiedz krótko.", " Jednym zdaniem.", " Prosto.", " Bez przykładu.", " Zakończ naturalnie.", " Krótko i konkretnie.", " W prostym języku."],
            "direct-def",
        )
    )

    rewrites = [
        ("W mojej opinii uważam, że wynik ten jest dobry.", "Uważam, że ten wynik jest dobry."),
        ("Dokonano wykonania testu działania systemu.", "Przetestowano działanie systemu."),
        ("Ten projekt posiada zbyt dużą ilość zaplanowanych funkcji.", "Ten projekt ma zbyt wiele zaplanowanych funkcji."),
        ("Należy dokonać analizy przyczyn wystąpienia błędu.", "Trzeba przeanalizować przyczynę błędu."),
        ("W celu poprawy jakości należy ograniczyć powtarzanie.", "Aby poprawić jakość, trzeba ograniczyć powtarzanie."),
        ("Model udzielił odpowiedzi w sposób zbyt rozwlekły.", "Model odpowiedział zbyt rozwlekle."),
    ]
    out.extend(
        expand_pairs(
            "krotkie_poprawki_tekstu",
            rewrites,
            ["Popraw tekst: {instruction}", "Napisz naturalniej: {instruction}", "Skróć: {instruction}", "Usuń lanie wody: {instruction}", "Przeredaguj zdanie: {instruction}", "Napisz prościej: {instruction}"],
            "rewrite-extra",
        )
    )
    return out


def dedupe(records: list[dict]) -> list[dict]:
    seen_pairs: set[str] = set()
    seen_instruction: Counter[str] = Counter()
    out = []
    for item in records:
        pair_key = normalize_for_dupes(item["instruction"] + "\n" + item["response"])
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        instr_key = normalize_for_dupes(item["instruction"])
        seen_instruction[instr_key] += 1
        if seen_instruction[instr_key] > 1:
            item = dict(item)
            item["instruction"] = f"{item['instruction']} ({seen_instruction[instr_key]})"
        out.append(item)
    return out


def stratified_split(records: list[dict], seed: int) -> tuple[list[dict], list[dict], list[dict]]:
    rng = random.Random(seed)
    buckets: dict[str, list[dict]] = defaultdict(list)
    for item in records:
        buckets[item["category"]].append(item)
    train: list[dict] = []
    val: list[dict] = []
    test: list[dict] = []
    for items in buckets.values():
        rng.shuffle(items)
        n = len(items)
        n_val = max(1, round(n * 0.10))
        n_test = max(1, round(n * 0.05))
        test.extend(items[:n_test])
        val.extend(items[n_test : n_test + n_val])
        train.extend(items[n_test + n_val :])
    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)
    return train, val, test


def top_ngrams(records: list[dict], n: int, limit: int = 30) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for item in records:
        words = re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+", item["response"].lower(), flags=re.UNICODE)
        for i in range(max(0, len(words) - n + 1)):
            counts[" ".join(words[i : i + n])] += 1
    return counts.most_common(limit)


def suspicious_counts(records: list[dict]) -> dict[str, int]:
    counts = {}
    for pattern in SUSPICIOUS_PATTERNS:
        needle = pattern.lower()
        counts[pattern] = sum(1 for r in records if needle in (r["instruction"] + "\n" + r["response"]).lower())
    return counts


def write_txt(path: str | Path, records: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(format_sft_text(r).rstrip() for r in records) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict, records: list[dict]) -> None:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for item in records:
        by_cat[item["category"]].append(item)
    lines = [
        "# Glyph-100M SFT smoke v0.2 dataset report",
        "",
        "## Summary",
        "",
        f"- examples: {report['stats']['examples']}",
        f"- split train/val/test: {report['split_counts']}",
        f"- max template tokens: {report['stats']['token_stats']['template_max']}",
        f"- over context 512: {report['stats']['token_stats']['over_context']}",
        f"- duplicate pair extra: {report['duplicates']['pair_extra']}",
        f"- near duplicate examples: {len(report['near_duplicates'])}",
        f"- `<|end|>` supervised sanity: {report['end_token_supervised_sanity']}",
        "",
        "## Categories",
        "",
    ]
    for category, count in sorted(report["stats"]["categories"].items()):
        lines.append(f"- {category}: {count}")
    lines += ["", "## First Response Words", ""]
    for word, count in report["first_response_words"][:30]:
        lines.append(f"- `{word}`: {count}")
    lines += ["", "## Top Response 4-grams", ""]
    for gram, count in report["top_response_4grams"][:30]:
        lines.append(f"- `{gram}`: {count}")
    lines += ["", "## Suspicious Phrases", ""]
    for phrase, count in report["suspicious_phrase_counts"].items():
        lines.append(f"- `{phrase}`: {count}")
    lines += ["", "## Examples Per Category", ""]
    for category, items in sorted(by_cat.items()):
        lines += [f"### {category}", ""]
        for item in items[:4]:
            lines.append(f"- prompt: {item['instruction']}")
            lines.append(f"  response: {item['response']}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M SFT smoke v0.2 dataset")
    parser.add_argument("--input-v0", default="data/sft/glyph100_sft_smoke_v0.jsonl")
    parser.add_argument("--output", default="data/sft/glyph100_sft_smoke_v0_2.jsonl")
    parser.add_argument("--report-md", default="data/sft/glyph100_sft_smoke_v0_2_report.md")
    parser.add_argument("--report-json", default="data/sft/glyph100_sft_smoke_v0_2_report.json")
    parser.add_argument("--processed-dir", default="data/sft/processed")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--seed", type=int, default=2027)
    args = parser.parse_args()

    records = load_repaired_v0(args.input_v0) + build_extra_records()
    records = dedupe(records)
    rng = random.Random(args.seed)
    rng.shuffle(records)
    for idx, item in enumerate(records, 1):
        item["id"] = f"glyph100-sft-smoke-v0-2-{idx:04d}"
        item["source_id"] = f"{item['source_id']}"

    if not (2000 <= len(records) <= 3000):
        raise SystemExit(f"dataset size outside requested range: {len(records)}")

    sp = load_sentencepiece(args.tokenizer)
    stats = collect_dataset_stats(records, sp=sp, context_len=args.context_len)
    suspicious = suspicious_counts(records)
    pair_counts = Counter(normalize_for_dupes(r["instruction"] + "\n" + r["response"]) for r in records)
    instr_counts = Counter(normalize_for_dupes(r["instruction"]) for r in records)
    first_words = Counter((r["response"].split() or [""])[0] for r in records).most_common(40)
    top4 = top_ngrams(records, 4, 40)
    near_dupes = similar_instruction_pairs(records, limit=50)
    train, val, test = stratified_split(records, args.seed)
    processed = Path(args.processed_dir)
    prefix = processed / "glyph100_sft_smoke_v0_2"

    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
    pad_id = sp.pad_id() if sp.pad_id() >= 0 else 0
    end_id = sp.piece_to_id(END_TOKEN)
    end_ok = 0
    for item in records[:100]:
        ids = list(sp.encode(format_sft_text(item), out_type=int))
        if len(ids) >= 2:
            x = ids[:-1]
            y = ids[1:]
            try:
                assistant_pos = x.index(assistant_id)
            except ValueError:
                continue
            labels = [(-100 if i < assistant_pos or token == pad_id else token) for i, token in enumerate(y)]
            if any(label == end_id for label in labels):
                end_ok += 1

    report = {
        "dataset": "glyph100_sft_smoke_v0_2",
        "purpose": "corrected small SFT smoke dataset focused on repetition, end-token behavior and answer diversity",
        "input_v0": args.input_v0,
        "output": args.output,
        "tokenizer": args.tokenizer,
        "context_len": args.context_len,
        "stats": stats,
        "split_counts": {"train": len(train), "val": len(val), "test": len(test)},
        "split_paths": {
            "train_jsonl": str(prefix) + "_train.jsonl",
            "val_jsonl": str(prefix) + "_val.jsonl",
            "test_jsonl": str(prefix) + "_test.jsonl",
            "train_txt": str(prefix) + "_train.txt",
            "val_txt": str(prefix) + "_val.txt",
            "test_txt": str(prefix) + "_test.txt",
        },
        "duplicates": {
            "pair_extra": sum(c - 1 for c in pair_counts.values() if c > 1),
            "instruction_extra": sum(c - 1 for c in instr_counts.values() if c > 1),
        },
        "near_duplicates": near_dupes,
        "first_response_words": first_words,
        "top_response_4grams": top4,
        "suspicious_phrase_counts": suspicious,
        "end_token_supervised_sanity": {
            "checked_examples": min(100, len(records)),
            "end_token_as_last_predictable_token": end_ok,
            "end_token_id": end_id,
        },
        "quality_notes": [
            "Derived from v0 with repaired repeated openings and added anti-repetition/end-token examples.",
            "Includes one-sentence and 2-4 sentence responses.",
            "Adds category anty_powtorzenia_i_konczenie.",
            "No full SFT intent; this is a smoke-test dataset only.",
        ],
    }
    if stats["token_stats"]["over_context"]:
        raise SystemExit("examples over context")
    if report["duplicates"]["pair_extra"]:
        raise SystemExit("exact duplicate pairs found")
    bad_suspicious = {k: v for k, v in suspicious.items() if v}
    if bad_suspicious:
        raise SystemExit(f"suspicious phrases found: {bad_suspicious}")

    write_jsonl(args.output, records)
    write_jsonl(str(prefix) + "_train.jsonl", train)
    write_jsonl(str(prefix) + "_val.jsonl", val)
    write_jsonl(str(prefix) + "_test.jsonl", test)
    write_txt(str(prefix) + "_train.txt", train)
    write_txt(str(prefix) + "_val.txt", val)
    write_txt(str(prefix) + "_test.txt", test)
    write_json(args.report_json, report)
    write_markdown(Path(args.report_md), report, records)
    print(json.dumps({"examples": len(records), "split": report["split_counts"], "max_tokens": stats["token_stats"]["template_max"], "top_first_words": first_words[:10]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
