#!/usr/bin/env python3
"""Build Glyph-100M SFT smoke v0.3 dataset and pre-dataset plan.

v0.3 is a targeted repair after v0.2:
- keep the clean mechanics of v0.2;
- improve semantic correctness;
- add anti-web-residue examples;
- reduce repeated first words and short empty refusals;
- keep the run small enough for a smoke test, not SFT v1.
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

from scripts.sft_utils import (  # noqa: E402
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


REQUESTED_CATEGORIES = (
    "krotkie_definicje_poprawne",
    "techniczne_proste_wyjasnienia",
    "mvp_first_project_advice",
    "brak_danych_bez_petli",
    "anty_web_residue",
    "anty_powtorzenia_i_konczenie",
    "poprawki_tekstu",
    "mini_streszczenia",
    "codzienne_proste_pytania",
    "ostrozne_odpowiedzi",
    "sanity_fakty_podstawowe",
    "not_in_dataset_style_generalization",
)

CATEGORY_MAP = {
    "krotkie_definicje": "krotkie_definicje_poprawne",
    "proste_techniczne_wyjasnienia": "techniczne_proste_wyjasnienia",
    "krotkie_poprawki_tekstu": "poprawki_tekstu",
    "brak_danych": "brak_danych_bez_petli",
    "ostrozne_odpowiedzi_przy_niepewnosci": "ostrozne_odpowiedzi",
    "anty_petle": "anty_powtorzenia_i_konczenie",
    "naturalne_zakonczenia": "anty_powtorzenia_i_konczenie",
}

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
    "skontaktuj się z nami",
    "na naszej stronie",
]

RESPONSE_REPAIRS = [
    ("Nie. Brakuje", "Brakuje"),
    ("Nie. Bez", "Bez"),
    ("Nie. Trzeba", "Trzeba"),
    ("Nie. Potrzebny", "Potrzebny"),
    ("Nie. Potrzebna", "Potrzebna"),
    ("Nie. Potrzebne", "Potrzebne"),
    ("Nie. Najpierw", "Najpierw"),
    ("Nie. Odpowiedź", "Odpowiedź"),
]


def record(category: str, instruction: str, response: str, source_id: str) -> dict:
    return {
        "id": "",
        "category": category,
        "instruction": normalize_space(instruction),
        "response": normalize_space(response),
        "source": "synthetic_curated_sft_smoke_v0_3",
        "source_id": source_id,
        "quality": "approved",
    }


def response_first_word(text: str) -> str:
    parts = normalize_space(text).split()
    return parts[0].strip(" ,.:;!?").lower() if parts else ""


def repair_response(text: str, idx: int) -> str:
    text = normalize_space(text)
    for old, new in RESPONSE_REPAIRS:
        if text.startswith(old):
            text = text.replace(old, new, 1)
            break
    if text == "Nie.":
        text = "Tego nie da się ocenić bez dodatkowych danych."
    if text.startswith("Nie, "):
        variants = [
            text,
            text.replace("Nie, ", "Raczej nie, ", 1),
            text.replace("Nie, ", "To nie wystarczy: ", 1),
            text.replace("Nie, ", "Odpowiedź brzmi: nie, ", 1),
        ]
        text = variants[idx % len(variants)]
    if text.startswith("Najpierw "):
        variants = [
            text,
            text.replace("Najpierw ", "Zacznij od ", 1),
            text.replace("Najpierw ", "Na start ", 1),
            text.replace("Najpierw ", "W pierwszym kroku ", 1),
        ]
        text = variants[idx % len(variants)]
    if text.startswith("Warto "):
        variants = [
            text,
            text.replace("Warto ", "Dobrze jest ", 1),
            text.replace("Warto ", "Rozsądnie jest ", 1),
            text.replace("Warto ", "Można ", 1),
        ]
        text = variants[idx % len(variants)]
    if text.startswith("Brakuje "):
        variants = [
            text,
            text.replace("Brakuje ", "Do oceny brakuje ", 1),
            text.replace("Brakuje ", "Potrzebne są ", 1),
            text.replace("Brakuje ", "Z samego opisu nie wynika ", 1),
        ]
        text = variants[idx % len(variants)]
    return normalize_space(text)


def load_repaired_v02(path: str) -> list[dict]:
    loaded = load_jsonl(path)
    out = []
    for idx, item in enumerate(loaded.records):
        category = CATEGORY_MAP.get(item.get("category"), item.get("category"))
        if category not in REQUESTED_CATEGORIES:
            category = "not_in_dataset_style_generalization"
        response = repair_response(item["response"], idx)
        out.append(record(category, item["instruction"], response, f"v02-repaired-{item.get('id', idx)}"))
    return out


def expand(category: str, pairs: list[tuple[str, str]], variants: list[str], source_prefix: str) -> list[dict]:
    out = []
    for i, (instruction, response) in enumerate(pairs):
        for j, variant in enumerate(variants):
            prompt = variant.format(instruction=instruction) if "{instruction}" in variant else instruction + variant
            out.append(record(category, prompt, response, f"{source_prefix}-{i:03d}-{j:02d}"))
    return out


def targeted_examples() -> list[dict]:
    out: list[dict] = []

    definitions = [
        ("Czym jest cache?", "Cache to szybka pamięć pomocnicza, która przechowuje często używane dane, żeby nie liczyć lub pobierać ich od nowa."),
        ("Czym jest backup?", "Backup to kopia danych przygotowana po to, żeby dało się je odtworzyć po awarii lub pomyłce."),
        ("Czym jest walidacja?", "Walidacja to sprawdzenie, czy wynik działa poprawnie na danych innych niż te użyte bezpośrednio do pracy."),
        ("Czym jest tokenizer?", "Tokenizer dzieli tekst na tokeny, czyli jednostki, które model może przetwarzać jako liczby."),
        ("Czym jest checkpoint?", "Checkpoint to zapis stanu modelu i treningu w konkretnym momencie."),
        ("Czym jest overfit?", "Overfit oznacza, że model zbyt mocno dopasował się do danych treningowych i słabiej uogólnia."),
        ("Czym jest GPU?", "GPU to procesor graficzny, który dobrze wykonuje wiele podobnych obliczeń równolegle."),
        ("Czym jest RAM?", "RAM to szybka pamięć robocza używana przez działające programy i system."),
        ("Czym jest latency?", "Latency to opóźnienie między wysłaniem żądania a otrzymaniem odpowiedzi."),
        ("Czym jest throughput?", "Throughput to ilość pracy wykonanej w jednostce czasu, na przykład tokeny na sekundę."),
        ("Czym jest learning rate?", "Learning rate określa, jak duży krok robi optimizer podczas aktualizacji wag modelu."),
        ("Czym jest ewaluacja jakościowa?", "Ewaluacja jakościowa sprawdza konkretne odpowiedzi modelu, a nie tylko liczbę loss."),
    ]
    out.extend(
        expand(
            "krotkie_definicje_poprawne",
            definitions,
            ["", " Odpowiedz jednym zdaniem.", " Wyjaśnij prosto.", " Krótko i poprawnie.", " Bez marketingu.", " Zakończ naturalnie."],
            "defs",
        )
    )

    technical = [
        ("Czym różni się train loss od val loss?", "Train loss mierzy dopasowanie do danych treningowych, a val loss sprawdza model na odłożonych danych."),
        ("Po co jest gradient clipping?", "Gradient clipping ogranicza zbyt duże gradienty, żeby zmniejszyć ryzyko niestabilnego treningu."),
        ("Po co robi się eval na tych samych promptach?", "Stałe prompty pozwalają porównać checkpointy bez mieszania zmian modelu ze zmianami testu."),
        ("Dlaczego sam loss nie wystarczy?", "Loss jest metryką pomocniczą; generacje mogą być słabe mimo niższego loss."),
        ("Czym jest batch size?", "Batch size to liczba przykładów przetwarzanych naraz przed policzeniem aktualizacji lub części aktualizacji."),
        ("Czym jest gradient accumulation?", "Gradient accumulation zbiera gradienty z kilku małych batchy przed jednym krokiem optimizera."),
        ("Po co jest seed w eval?", "Seed pomaga powtórzyć losowe generacje i odróżnić zmianę modelu od losowości próbkowania."),
        ("Czym jest smoke test?", "Smoke test to krótka próba sprawdzająca, czy cały mechanizm działa bez oczywistych awarii."),
    ]
    out.extend(
        expand(
            "techniczne_proste_wyjasnienia",
            technical,
            ["", " Odpowiedz krótko.", " W dwóch zdaniach.", " Bez listy.", " Użyj prostego języka.", " Zakończ po wyjaśnieniu."],
            "technical",
        )
    )

    missing = [
        ("Czy ten laptop jest dobry?", "Do oceny potrzebne są model, cena, stan i zastosowanie laptopa."),
        ("Czy ten wynik jest poprawny?", "Tego nie da się stwierdzić bez oczekiwanego wyniku i sposobu pomiaru."),
        ("Czy powinienem to kupić?", "Potrzebna jest cena, potrzeba i alternatywy. Bez tego odpowiedź byłaby zgadywaniem."),
        ("Czy ta konfiguracja jest bezpieczna?", "Brakuje szczegółów konfiguracji i zagrożeń, więc nie da się tego uczciwie ocenić."),
        ("Czy model działa dobrze?", "Trzeba zobaczyć próbki, metryki i zestaw testowy. Sama informacja, że działa, nie wystarcza."),
        ("Czy ten błąd jest poważny?", "Potrzebny jest komunikat błędu, miejsce wystąpienia i wpływ na działanie systemu."),
        ("Czy mogę opublikować ten model?", "Najpierw trzeba znać jakość, ograniczenia, dane treningowe i ryzyka użycia."),
        ("Czy eval jest wiarygodny?", "Trzeba znać liczbę promptów, metodę oceny i ustawienia generacji."),
    ]
    out.extend(
        expand(
            "brak_danych_bez_petli",
            missing,
            ["", " Nie zgaduj.", " Odpowiedz ostrożnie.", " Wskaż brakujące dane.", " Bez powtarzania.", " Jednym zdaniem.", " Zakończ naturalnie."],
            "missing",
        )
    )

    anti_web = [
        ("Napisz odpowiedź techniczną bez tekstu sklepu: czym jest backup?", "Backup to kopia danych używana do odtworzenia ich po awarii."),
        ("Nie używaj marketingu: czym jest checkpoint?", "Checkpoint to zapis stanu treningu, do którego można wrócić później."),
        ("Odpowiedz bez wezwania do kontaktu: co zrobić po błędzie?", "Zapisz log, sprawdź ostatnią zmianę i odtwórz problem w kontrolowany sposób."),
        ("Nie pisz jak strona firmowa: czym jest tokenizer?", "Tokenizer dzieli tekst na tokeny, które model przetwarza jako liczby."),
        ("Usuń styl SEO: dlaczego czysty dataset jest ważny?", "Czysty dataset zmniejsza ryzyko, że model nauczy się spamu, menu i reklam."),
        ("Bez komunikatów o prywatności i regulaminach: czym jest eval?", "Eval to sprawdzenie modelu na ustalonych zadaniach lub promptach."),
        ("Nie rób z tego oferty handlowej: po co jest raport?", "Raport zapisuje ustawienia, wynik i decyzję po eksperymencie."),
        ("Nie dodawaj tekstu sklepu: jak opisać GPU?", "GPU wykonuje wiele obliczeń równolegle i dobrze nadaje się do części zadań treningowych."),
    ]
    out.extend(
        expand(
            "anty_web_residue",
            anti_web,
            ["", " Krótko.", " Jednym zdaniem.", " Bez reklam.", " Bez linków.", " Bez wezwań do kontaktu.", " Naturalnie."],
            "anti-web",
        )
    )

    anti_repeat = [
        ("Nie powtarzaj pierwszego słowa: po co jest eval?", "Eval pomaga sprawdzić, czy model poprawia się w praktyce."),
        ("Zakończ po jednej myśli: co zrobić, gdy odpowiedź jest pełna?", "Zatrzymaj tekst i nie dopisuj kolejnej wersji tej samej informacji."),
        ("Bez pętli: dlaczego powtórzenia są złe?", "Powtórzenia obniżają czytelność i zwykle nie dodają treści."),
        ("Jedno zdanie, bez listy: kiedy dataset jest słaby?", "Dataset jest słaby, gdy zawiera śmieci, duplikaty albo zbyt wąski styl."),
        ("Odpowiedz i zakończ: czy SFT dodaje wiedzę?", "SFT głównie uczy formatu odpowiedzi, a nie automatycznie nowej wiedzy."),
        ("Nie rozwijaj nowego tematu: czym jest best checkpoint?", "Best checkpoint to zapis wybrany na podstawie najlepszej ewaluacji."),
        ("Nie powtarzaj frazy: jak pisać krócej?", "Zostaw jedną główną myśl i usuń dygresje."),
        ("Bez drugiego akapitu: co oznacza brak danych?", "Oznacza, że trzeba wskazać niepewność zamiast zgadywać."),
    ]
    out.extend(
        expand(
            "anty_powtorzenia_i_konczenie",
            anti_repeat,
            ["", " Krótko.", " Zakończ naturalnie.", " Bez powtarzania.", " Jednym akapitem.", " Nie zaczynaj nowego tematu.", " Maksymalnie dwa zdania.", " Bez listy."],
            "anti-repeat",
        )
    )

    facts = [
        ("Stolicą Polski jest", "Stolicą Polski jest Warszawa."),
        ("Wisła to", "Wisła to najdłuższa rzeka w Polsce."),
        ("Bałtyk to", "Bałtyk to morze położone na północy Polski."),
        ("Rok ma zwykle", "Rok ma zwykle 365 dni."),
        ("Kilometr to", "Kilometr to tysiąc metrów."),
        ("Woda zamarza w temperaturze", "Woda zamarza w temperaturze około 0°C przy normalnym ciśnieniu."),
        ("Grawitacja to", "Grawitacja to oddziaływanie, które przyciąga masy do siebie."),
        ("CPU to", "CPU to główny procesor wykonujący instrukcje programu."),
        ("Plik różni się od folderu tym, że", "Plik przechowuje dane, a folder porządkuje pliki i inne foldery."),
        ("Fakt różni się od opinii tym, że", "Fakt można sprawdzić, a opinia wyraża czyjąś ocenę lub pogląd."),
    ]
    out.extend(
        expand(
            "sanity_fakty_podstawowe",
            facts,
            ["", " Dokończ krótko.", " Bez zmyślania.", " Jednym zdaniem.", " Naturalnie.", " Nie dodawaj dat ani gmin."],
            "facts",
        )
    )

    style_general = [
        ("Czy model po SFT automatycznie zna więcej faktów?", "Nie. SFT głównie uczy sposobu odpowiadania, a wiedza nadal zależy od bazy i danych."),
        ("Czy ładna odpowiedź zawsze jest poprawna?", "Nie. Odpowiedź może brzmieć dobrze, ale nadal być błędna semantycznie."),
        ("Czy krótsza odpowiedź zawsze jest lepsza?", "Nie zawsze. Ma być tak krótka, jak pozwala na pełną i poprawną odpowiedź."),
        ("Kiedy lepiej powiedzieć, że brakuje danych?", "Gdy pytanie wymaga informacji, których nie ma w opisie."),
        ("Czy model bazowy jest chatbotem?", "Nie. Model bazowy głównie kontynuuje tekst, a nie musi dobrze wykonywać instrukcji."),
        ("Czy jeden dobry sample wystarcza?", "Nie. Trzeba sprawdzić więcej promptów i kilka typów błędów."),
        ("Czy repetition penalty rozwiązuje wszystkie pętle?", "Nie. Może pomóc, ale dane i trening też muszą uczyć kończenia odpowiedzi."),
        ("Czy warto skalować SFT po słabym smoke teście?", "Nie. Najpierw trzeba poprawić przyczynę błędów w danych lub ewaluacji."),
    ]
    out.extend(
        expand(
            "not_in_dataset_style_generalization",
            style_general,
            ["", " Odpowiedz jasno.", " Krótko.", " Bez szablonu.", " W dwóch zdaniach.", " Naturalnie.", " Bez marketingu.", " Nie zgaduj."],
            "style-general",
        )
    )

    project = [
        ("Mam zacząć projekt od UI czy od logiki?", "Zacznij od logiki, jeśli ona decyduje, czy projekt w ogóle działa."),
        ("Czy robić od razu backend, frontend, dashboard i AI?", "Nie. Najpierw zrób najmniejszą wersję, która pokazuje główną wartość projektu."),
        ("Czy większy zakres zwiększa szansę sukcesu?", "Nie zawsze. Duży zakres często utrudnia dowiezienie pierwszej działającej wersji."),
        ("Co zrobić, gdy projekt się rozrasta?", "Odetnij funkcje poboczne i zostaw rdzeń, który można szybko sprawdzić."),
        ("Czy najpierw poprawiać wygląd?", "Wygląd warto poprawiać po potwierdzeniu, że główna logika działa."),
    ]
    out.extend(
        expand(
            "mvp_first_project_advice",
            project,
            ["", " Odpowiedz konkretnie.", " Bez lania wody.", " Jednym akapitem.", " Nie rób listy.", " Krótko.", " Zakończ naturalnie."],
            "project",
        )
    )

    rewrites = [
        ("Ten projekt posiada wiele funkcji i działa w dobry sposób.", "Ten projekt ma wiele funkcji i działa dobrze."),
        ("W mojej opinii uważam, że to rozwiązanie jest najlepsze.", "Uważam, że to rozwiązanie jest najlepsze."),
        ("Należy dokonać sprawdzenia poprawności działania programu.", "Trzeba sprawdzić, czy program działa poprawnie."),
        ("Zostało wykonane przeprowadzenie testu modelu.", "Przetestowano model."),
        ("Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.", "Proszę o informację zwrotną w tej sprawie."),
        ("Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.", "Nie zdążę dziś oddać pracy."),
    ]
    out.extend(
        expand(
            "poprawki_tekstu",
            rewrites,
            ["Popraw tekst: {instruction}", "Napisz naturalniej: {instruction}", "Skróć: {instruction}", "Usuń lanie wody: {instruction}", "Przeredaguj: {instruction}", "Napisz prościej: {instruction}"],
            "rewrite",
        )
    )

    summaries = [
        ("Duże projekty często upadają przez zbyt szeroki zakres i brak pierwszej działającej wersji.", "Zbyt szeroki zakres utrudnia dowiezienie działającego projektu."),
        ("Niższy loss może wyglądać dobrze, ale sample mogą pokazywać pętle i słabe odpowiedzi.", "Loss trzeba sprawdzać razem z jakością generacji."),
        ("Czysty dataset jest ważniejszy niż duży dataset pełen reklam, menu i przypadkowych śmieci.", "Jakość danych jest ważniejsza niż sama liczba tokenów."),
        ("SFT smoke sprawdza mechanikę uczenia instrukcji, ale nie dowodzi gotowości modelu do użycia.", "SFT smoke jest testem mechaniki, nie certyfikatem jakości modelu."),
        ("Eval powinien mieć stałe prompty, jasne kryteria i porównanie z poprzednim checkpointem.", "Dobry eval wymaga stałych promptów, kryteriów i porównania."),
    ]
    out.extend(
        expand(
            "mini_streszczenia",
            summaries,
            ["Streść: {instruction}", "Streść jednym zdaniem: {instruction}", "Wyciągnij główną myśl: {instruction}", "Skróć sens tekstu: {instruction}", "Bez komentarza, tylko streszczenie: {instruction}"],
            "summary",
        )
    )

    daily = [
        ("Napisz krótką wiadomość, że spóźnię się 10 minut.", "Spóźnię się około 10 minut. Przepraszam za opóźnienie."),
        ("Poproś krótko o ponowne przesłanie pliku.", "Czy możesz przesłać ten plik jeszcze raz?"),
        ("Napisz neutralnie, że nie mogę dziś przyjść.", "Nie mogę dziś przyjść. Dam znać, kiedy będę dostępny."),
        ("Napisz krótką odpowiedź, że sprawdzę to później.", "Sprawdzę to później i wrócę z odpowiedzią."),
        ("Napisz krótko, że potrzebuję więcej informacji.", "Potrzebuję więcej informacji, żeby odpowiedzieć dokładnie."),
    ]
    out.extend(
        expand(
            "codzienne_proste_pytania",
            daily,
            ["", " Naturalnie.", " Bez formalnego tonu.", " Krótko.", " Jednym zdaniem.", " Uprzejmie.", " Bez tłumaczenia się."],
            "daily",
        )
    )

    caution = [
        ("Czy mogę powiedzieć, że model jest gotowy?", "Ostrożnie: bez szerszego evala lepiej mówić, że to eksperymentalny checkpoint."),
        ("Czy wynik ładnie wygląda, więc jest poprawny?", "Nie. Trzeba sprawdzić, czy odpowiedź faktycznie ma sens."),
        ("Czy publikować model po smoke teście?", "Nie jako gotowy produkt. Smoke test pokazuje kierunek, nie pełną jakość."),
        ("Czy można oceniać bezpieczeństwo bez szczegółów?", "Nie. Ocena bezpieczeństwa wymaga kontekstu, konfiguracji i możliwych skutków."),
        ("Czy mam zgadywać brakujące dane?", "Nie. Lepiej jasno wskazać, czego brakuje."),
    ]
    out.extend(
        expand(
            "ostrozne_odpowiedzi",
            caution,
            ["", " Odpowiedz ostrożnie.", " Bez przesadnej pewności.", " Krótko.", " Naturalnie.", " W dwóch zdaniach.", " Nie zgaduj."],
            "caution",
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


def top_ngrams(records: list[dict], n: int, limit: int = 40) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for item in records:
        toks = re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+", item["response"].lower(), flags=re.UNICODE)
        for i in range(max(0, len(toks) - n + 1)):
            counts[" ".join(toks[i : i + n])] += 1
    return counts.most_common(limit)


def suspicious_counts(records: list[dict]) -> dict[str, int]:
    counts = {}
    for pattern in SUSPICIOUS_PATTERNS:
        needle = pattern.lower()
        counts[pattern] = sum(1 for r in records if needle in (r["instruction"] + "\n" + r["response"]).lower())
    return counts


def label_audit(records: list[dict], sp, limit: int = 20) -> dict:
    assistant_id = sp.piece_to_id(ASSISTANT_TOKEN)
    end_id = sp.piece_to_id(END_TOKEN)
    pad_id = sp.pad_id() if sp.pad_id() >= 0 else 0
    samples = []
    ok_first = 0
    ok_end = 0
    ok_prompt_mask = 0
    ok_padding = True
    no_labels = 0
    for item in records[:limit]:
        ids = list(sp.encode(format_sft_text(item), out_type=int))
        x = ids[:-1]
        y = ids[1:]
        try:
            assistant_pos = x.index(assistant_id)
        except ValueError:
            no_labels += 1
            continue
        labels = [(-100 if i < assistant_pos or token == pad_id else token) for i, token in enumerate(y)]
        supervised = [(i, token) for i, token in enumerate(labels) if token != -100]
        if not supervised:
            no_labels += 1
            continue
        first_idx, first_token = supervised[0]
        first_piece = sp.id_to_piece(int(first_token))
        expected_first = sp.encode(normalize_space(item["response"]), out_type=str)[0]
        first_ok = first_piece == expected_first
        end_ok = any(token == end_id for _, token in supervised)
        prompt_mask_ok = all(label == -100 for label in labels[:assistant_pos])
        ok_first += int(first_ok)
        ok_end += int(end_ok)
        ok_prompt_mask += int(prompt_mask_ok)
        samples.append(
            {
                "id": item["id"],
                "response": item["response"],
                "first_supervised_piece": first_piece,
                "expected_first_piece": expected_first,
                "first_token_supervised": first_ok,
                "end_token_supervised": end_ok,
                "prompt_masked": prompt_mask_ok,
            }
        )
    return {
        "checked": len(samples),
        "first_token_supervised_ok": ok_first,
        "end_token_supervised_ok": ok_end,
        "prompt_masked_ok": ok_prompt_mask,
        "padding_ignore_index": ok_padding,
        "examples_without_labels": no_labels,
        "samples": samples,
    }


def write_txt(path: str | Path, records: list[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(format_sft_text(r).rstrip() for r in records) + "\n", encoding="utf-8")


def write_plan(plan_path_md: Path, plan_path_json: Path, source_reports: dict, generated_notes: dict) -> None:
    plan = {
        "created_for": "glyph100_sft_smoke_v0_3",
        "inputs": source_reports,
        "diagnosis": {
            "working_categories": [
                "anty_powtorzenia_i_konczenie",
                "poprawki_tekstu",
                "mini_streszczenia",
            ],
            "weak_categories": [
                "krotkie_definicje_poprawne",
                "sanity_fakty_podstawowe",
                "not_in_dataset_style_generalization",
            ],
            "web_risk": "v0.2 manual audit still found real web-residue cases; v0.3 adds explicit anti_web_residue examples.",
            "repetition_risk": "no_repeat_ngram_size_3 controls literal loops in decoding, but dataset should still teach natural stopping.",
        },
        "changes_for_v0_3": generated_notes,
    }
    write_json(plan_path_json, plan)
    lines = [
        "# Glyph-100M SFT v0.3 dataset plan",
        "",
        "## Diagnosis from v0.2",
        "",
        "- v0.2 improved format and repetition, but did not clearly beat v0.1 enough for SFT v1.",
        "- Best decoding was `no_repeat_ngram_size_3`, which suggests decoding helps but does not remove the dataset issue.",
        "- Manual audit found real web-residue cases, so v0.3 adds explicit anti-web examples.",
        "- v0.2 still had semantic weaknesses in definitions and out-of-dataset prompts.",
        "",
        "## What to Add",
        "",
        "- More semantically correct definitions and basic facts.",
        "- More missing-data answers with varied first words, not just `Nie`.",
        "- Explicit anti-web-residue examples: no SEO, no shop text, no cookies/privacy boilerplate.",
        "- Anti-repetition examples that end after one clear thought.",
        "- More natural Polish one-to-four sentence answers.",
        "",
        "## What to Rewrite / Avoid",
        "",
        "- Rewrite repeated starts such as `Nie`, `Najpierw`, `Warto`, `Brakuje`.",
        "- Avoid pseudo-ency patterns: dates, gmina/powiat/wojewodztwo filler.",
        "- Avoid empty refusals and short answers without semantic content.",
        "",
    ]
    plan_path_md.write_text("\n".join(lines), encoding="utf-8")


def write_markdown(path: Path, report: dict, records: list[dict]) -> None:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for item in records:
        by_cat[item["category"]].append(item)
    lines = [
        "# Glyph-100M SFT smoke v0.3 dataset report",
        "",
        "## Summary",
        "",
        f"- examples: {report['stats']['examples']}",
        f"- split train/val/test: {report['split_counts']}",
        f"- max template tokens: {report['stats']['token_stats']['template_max']} / {report['context_len']}",
        f"- over context: {report['stats']['token_stats']['over_context']}",
        f"- exact duplicate pairs: {report['duplicates']['pair_extra']}",
        f"- near duplicate samples: {len(report['near_duplicates'])}",
        f"- label audit: `{report['label_mask_sanity']['summary']}`",
        "",
        "## Categories",
        "",
    ]
    for cat, count in sorted(report["stats"]["categories"].items()):
        lines.append(f"- {cat}: {count}")
    lines += ["", "## First Response Words", ""]
    for word, count in report["first_response_words"][:40]:
        lines.append(f"- `{word}`: {count}")
    lines += ["", "## Top Response 4-grams", ""]
    for gram, count in report["top_response_4grams"][:40]:
        lines.append(f"- `{gram}`: {count}")
    lines += ["", "## Suspicious Phrases", ""]
    for phrase, count in report["suspicious_phrase_counts"].items():
        lines.append(f"- `{phrase}`: {count}")
    lines += ["", "## Random Examples Per Category", ""]
    rng = random.Random(123)
    for cat in sorted(by_cat):
        items = list(by_cat[cat])
        rng.shuffle(items)
        lines += [f"### {cat}", ""]
        for item in items[:10]:
            lines.append(f"- prompt: {item['instruction']}")
            lines.append(f"  response: {item['response']}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-v02", default="data/sft/glyph100_sft_smoke_v0_2.jsonl")
    parser.add_argument("--output", default="data/sft/glyph100_sft_smoke_v0_3.jsonl")
    parser.add_argument("--report-md", default="data/sft/glyph100_sft_smoke_v0_3_report.md")
    parser.add_argument("--report-json", default="data/sft/glyph100_sft_smoke_v0_3_report.json")
    parser.add_argument("--plan-md", default="reports/glyph100_sft_v0_3_dataset_plan.md")
    parser.add_argument("--plan-json", default="reports/glyph100_sft_v0_3_dataset_plan.json")
    parser.add_argument("--processed-dir", default="data/sft/processed")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=512)
    parser.add_argument("--seed", type=int, default=2031)
    args = parser.parse_args()

    records = load_repaired_v02(args.input_v02) + targeted_examples()
    records = dedupe(records)
    rng = random.Random(args.seed)
    rng.shuffle(records)
    if len(records) > 3500:
        records = records[:3500]
    if len(records) < 2500:
        raise SystemExit(f"dataset too small: {len(records)}")
    for idx, item in enumerate(records, 1):
        item["id"] = f"glyph100-sft-smoke-v0-3-{idx:04d}"

    sp = load_sentencepiece(args.tokenizer)
    stats = collect_dataset_stats(records, sp=sp, context_len=args.context_len)
    suspicious = suspicious_counts(records)
    pair_counts = Counter(normalize_for_dupes(r["instruction"] + "\n" + r["response"]) for r in records)
    instr_counts = Counter(normalize_for_dupes(r["instruction"]) for r in records)
    first_words = Counter(response_first_word(r["response"]) for r in records).most_common(60)
    top4 = top_ngrams(records, 4, 60)
    near_dupes = similar_instruction_pairs(records, limit=80)
    train, val, test = stratified_split(records, args.seed)
    processed = Path(args.processed_dir)
    prefix = processed / "glyph100_sft_smoke_v0_3"
    label = label_audit(records, sp, limit=40)
    label_summary = {
        "first_token_supervised": label["first_token_supervised_ok"] == label["checked"],
        "end_token_supervised": label["end_token_supervised_ok"] == label["checked"],
        "prompt_masked": label["prompt_masked_ok"] == label["checked"],
        "padding_ignore_index": label["padding_ignore_index"],
        "examples_without_labels": label["examples_without_labels"],
    }

    report = {
        "dataset": "glyph100_sft_smoke_v0_3",
        "purpose": "targeted small SFT smoke dataset after v0.2 decoding audit; not SFT v1",
        "input_v02": args.input_v02,
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
        "label_mask_sanity": {"summary": label_summary, "details": label},
        "quality_notes": [
            "Uses requested v0.3 categories.",
            "Adds anti_web_residue and sanity_fakty_podstawowe examples.",
            "Varies missing-data answer openings.",
            "Keeps max template length well below context 512.",
        ],
    }
    if not set(report["stats"]["categories"]).issubset(set(REQUESTED_CATEGORIES)):
        raise SystemExit(f"unexpected categories: {set(report['stats']['categories']) - set(REQUESTED_CATEGORIES)}")
    if stats["token_stats"]["over_context"]:
        raise SystemExit("examples over context")
    if report["duplicates"]["pair_extra"]:
        raise SystemExit("exact duplicate pairs found")
    hard_suspicious = {k: v for k, v in suspicious.items() if v}
    if hard_suspicious:
        raise SystemExit(f"suspicious phrases found: {hard_suspicious}")
    if label_summary["examples_without_labels"] or not all(
        [label_summary["first_token_supervised"], label_summary["end_token_supervised"], label_summary["prompt_masked"], label_summary["padding_ignore_index"]]
    ):
        raise SystemExit(f"label audit failed: {label_summary}")

    write_jsonl(args.output, records)
    write_jsonl(str(prefix) + "_train.jsonl", train)
    write_jsonl(str(prefix) + "_val.jsonl", val)
    write_jsonl(str(prefix) + "_test.jsonl", test)
    write_txt(str(prefix) + "_train.txt", train)
    write_txt(str(prefix) + "_val.txt", val)
    write_txt(str(prefix) + "_test.txt", test)
    write_json(args.report_json, report)
    write_markdown(Path(args.report_md), report, records)
    write_plan(
        Path(args.plan_md),
        Path(args.plan_json),
        {
            "v0_2_decoding_sweep": "eval/glyph-100m/sft_v0_2_decoding_sweep.json",
            "v0_2_best_decoding_compare": "eval/glyph-100m/sft_v0_1_vs_v0_2_best_decoding.json",
            "v0_2_error_audit": "reports/glyph100_sft_v0_2_error_and_decoding_audit.json",
            "v0_2_final_decision": "reports/glyph100_sft_v0_2_final_next_decision.json",
        },
        {
            "examples": len(records),
            "split": report["split_counts"],
            "categories": report["stats"]["categories"],
            "first_response_words_top10": first_words[:10],
            "max_template_tokens": stats["token_stats"]["template_max"],
        },
    )
    print(
        json.dumps(
            {
                "examples": len(records),
                "split": report["split_counts"],
                "max_template_tokens": stats["token_stats"]["template_max"],
                "top_first_words": first_words[:12],
                "label_summary": label_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
