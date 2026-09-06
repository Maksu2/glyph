#!/usr/bin/env python3
"""Build a small, deterministic Polish SFT smoke dataset for Glyph-100M."""

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

from scripts.sft_utils import collect_dataset_stats, format_sft_text, load_sentencepiece, normalize_for_dupes, write_json, write_jsonl


CATEGORY_TARGET = 150

SUSPICIOUS_PATTERNS = [
    "w latach 1975-1998",
    "w latach 1975–1998",
    "gminie",
    "powiecie",
    "strona główna",
    "cookies",
    "kup teraz",
    "dodaj do koszyka",
    "zaloguj",
    "zarejestruj",
    "polityka prywatności",
    "jako model językowy",
    "jako sztuczna inteligencja",
]


def cycle_take(items: list[dict], target: int) -> list[dict]:
    if len(items) < target:
        raise ValueError(f"not enough source records: have {len(items)}, need {target}")
    return items[:target]


def record(category: str, instruction: str, response: str, source_id: str) -> dict:
    return {
        "id": "",
        "category": category,
        "instruction": instruction.strip(),
        "response": response.strip(),
        "source": "synthetic_curated_sft_smoke",
        "source_id": source_id,
        "quality": "approved",
    }


def definitions() -> list[dict]:
    terms = [
        ("algorytm", "Algorytm to opis kolejnych kroków prowadzących do rozwiązania problemu."),
        ("backup", "Backup to kopia danych, którą można przywrócić po awarii albo pomyłce."),
        ("cache", "Cache to szybka pamięć podręczna używana po to, żeby nie liczyć lub pobierać tych samych danych ponownie."),
        ("model językowy", "Model językowy przewiduje kolejne fragmenty tekstu na podstawie wcześniejszego kontekstu."),
        ("token", "Token to mały fragment tekstu, na którym pracuje model językowy."),
        ("walidacja", "Walidacja to sprawdzenie, czy wynik działa na danych innych niż te użyte do uczenia."),
        ("overfit", "Overfit oznacza, że model za dobrze dopasował się do danych treningowych i gorzej działa na nowych przykładach."),
        ("latencja", "Latencja to czas oczekiwania na odpowiedź systemu."),
        ("przepustowość", "Przepustowość mówi, ile pracy system wykonuje w jednostce czasu."),
        ("kontener", "Kontener uruchamia aplikację z jej zależnościami w odizolowanym środowisku."),
        ("proces", "Proces to uruchomiony program wraz z pamięcią i zasobami systemu."),
        ("wątek", "Wątek to część procesu, która może wykonywać pracę równolegle z innymi wątkami."),
        ("plik", "Plik to nazwany zapis danych w systemie plików."),
        ("folder", "Folder porządkuje pliki i inne foldery w strukturze katalogów."),
        ("repozytorium", "Repozytorium przechowuje kod oraz historię zmian projektu."),
        ("checkpoint", "Checkpoint to zapis stanu modelu, z którego można wznowić trening albo uruchomić ewaluację."),
        ("tokenizer", "Tokenizer zamienia tekst na tokeny i tokeny z powrotem na tekst."),
        ("zbiór walidacyjny", "Zbiór walidacyjny służy do oceny modelu poza właściwym treningiem."),
        ("metryka", "Metryka to liczba opisująca wybraną cechę działania systemu."),
        ("hipoteza", "Hipoteza to sprawdzalne przypuszczenie, które można potwierdzić albo odrzucić testem."),
        ("interfejs", "Interfejs to sposób komunikacji użytkownika albo programu z systemem."),
        ("prototyp", "Prototyp to wczesna wersja rozwiązania używana do sprawdzenia pomysłu."),
        ("MVP", "MVP to najmniejsza wersja produktu, która pozwala sprawdzić główne założenie."),
        ("log", "Log to zapis zdarzeń, błędów i pomiarów z działania programu."),
        ("błąd", "Błąd to zachowanie programu niezgodne z oczekiwaniem."),
        ("test", "Test sprawdza, czy wybrany fragment systemu działa zgodnie z założeniem."),
        ("parametr", "Parametr to wartość sterująca zachowaniem programu, modelu albo eksperymentu."),
        ("dane treningowe", "Dane treningowe to przykłady, na których model uczy się wzorców."),
        ("inferencja", "Inferencja to użycie wytrenowanego modelu do wygenerowania wyniku."),
        ("prompt", "Prompt to tekst wejściowy przekazany modelowi."),
        ("odpowiedź", "Odpowiedź to tekst wygenerowany przez model po otrzymaniu promptu."),
        ("debugowanie", "Debugowanie to szukanie przyczyny błędu i sprawdzanie, co faktycznie dzieje się w programie."),
        ("wdrożenie", "Wdrożenie to uruchomienie projektu w miejscu, gdzie może z niego korzystać użytkownik."),
        ("konfiguracja", "Konfiguracja to zestaw ustawień sterujących działaniem systemu."),
        ("wersjonowanie", "Wersjonowanie pozwala śledzić zmiany i wracać do wcześniejszych stanów projektu."),
        ("dokumentacja", "Dokumentacja opisuje, jak projekt działa, jak go uruchomić i jakie ma ograniczenia."),
        ("ryzyko", "Ryzyko to możliwość wystąpienia problemu oraz jego potencjalny wpływ."),
        ("decyzja techniczna", "Decyzja techniczna wybiera konkretną drogę działania wraz z uzasadnieniem."),
        ("architektura", "Architektura opisuje główne części systemu i sposób ich współpracy."),
    ]
    templates = [
        ("Czym jest {term}?", "{definition}"),
        ("Wyjaśnij krótko pojęcie: {term}.", "{definition}"),
        ("Podaj prostą definicję: {term}.", "{definition}"),
        ("Co oznacza termin „{term}”?", "{definition}"),
    ]
    out = []
    for i, (term, definition) in enumerate(terms):
        for j, tpl in enumerate(templates):
            out.append(record("krotkie_definicje", tpl[0].format(term=term), tpl[1].format(definition=definition), f"def-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def technical_explanations() -> list[dict]:
    pairs = [
        ("Czym różni się CPU usage od load average?", "CPU usage pokazuje bieżące zajęcie procesora, a load average mówi, ile zadań czekało lub pracowało w pewnym oknie czasu."),
        ("Czym różni się RAM od dysku?", "RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera."),
        ("Po co używa się Dockera?", "Docker ułatwia uruchamianie aplikacji z tymi samymi zależnościami na różnych maszynach."),
        ("Czym różni się kontener od maszyny wirtualnej?", "Kontener współdzieli jądro systemu, a maszyna wirtualna uruchamia osobny system operacyjny."),
        ("Co oznacza limit RAM dla kontenera?", "Limit RAM ogranicza ilość pamięci, którą kontener może zużyć, żeby nie zajął całego hosta."),
        ("Po co robi się checkpointy modelu?", "Checkpointy pozwalają wrócić do wcześniejszego stanu modelu i wznowić trening po przerwie."),
        ("Czym jest learning rate?", "Learning rate określa, jak duży krok wykonuje optimizer przy aktualizacji wag modelu."),
        ("Co robi gradient clipping?", "Gradient clipping ogranicza zbyt duże gradienty, żeby trening nie stał się niestabilny."),
        ("Czym jest batch size?", "Batch size mówi, ile przykładów model przetwarza naraz przed aktualizacją albo częścią aktualizacji."),
        ("Po co jest walidacja podczas treningu?", "Walidacja sprawdza, czy model poprawia się na danych niewidzianych bezpośrednio w treningu."),
        ("Co oznacza token per second?", "Tokens per second mierzy, ile tokenów model przetwarza albo generuje w jednej sekundzie."),
        ("Co oznacza context length?", "Context length to maksymalna liczba tokenów, które model widzi jednocześnie."),
        ("Czym jest overfitting w modelu językowym?", "Overfitting występuje, gdy model uczy się zbyt konkretnych wzorców z datasetu i gorzej uogólnia."),
        ("Po co rozdziela się train i val?", "Rozdział train i val pozwala sprawdzić, czy model działa poza przykładami używanymi do uczenia."),
        ("Czym jest deduplikacja danych?", "Deduplikacja usuwa powtarzające się dokumenty albo fragmenty, żeby model nie uczył się jednego tekstu zbyt wiele razy."),
        ("Co oznacza OOM?", "OOM oznacza brak pamięci potrzebnej do wykonania operacji."),
        ("Czym jest scheduler learning rate?", "Scheduler zmienia learning rate w czasie, na przykład po rozgrzewce stopniowo go zmniejsza."),
        ("Po co mierzy się temperaturę GPU?", "Temperatura GPU pomaga ocenić, czy obciążenie jest bezpieczne i stabilne."),
        ("Czym jest tokenizer BPE?", "Tokenizer BPE buduje słownik z często występujących fragmentów tekstu, a potem dzieli tekst na te fragmenty."),
        ("Co oznacza resume treningu?", "Resume oznacza wznowienie treningu z checkpointu zamiast startu od zera."),
        ("Czym jest smoke test?", "Smoke test to krótka próba sprawdzająca, czy cały pipeline działa bez oczywistych błędów."),
        ("Po co są logi treningu?", "Logi treningu pokazują kroki, loss, prędkość, checkpointy i błędy."),
        ("Czym jest inference preset?", "Inference preset to zestaw ustawień generacji, na przykład temperatura i liczba tokenów."),
        ("Co robi repetition penalty?", "Repetition penalty zmniejsza szansę powtarzania tych samych tokenów lub fraz."),
        ("Czym jest top-k sampling?", "Top-k sampling ogranicza wybór kolejnego tokenu do kilku najbardziej prawdopodobnych opcji."),
        ("Czym jest top-p sampling?", "Top-p sampling wybiera tokeny z najmniejszego zbioru, którego łączna szansa przekracza ustalony próg."),
        ("Co oznacza val loss?", "Val loss mierzy błąd modelu na zbiorze walidacyjnym."),
        ("Co oznacza train loss?", "Train loss mierzy błąd modelu na przykładach używanych podczas treningu."),
        ("Czym jest fallback CPU?", "Fallback CPU to awaryjne uruchomienie pracy na procesorze, gdy GPU nie działa stabilnie."),
        ("Po co zapisuje się metadata checkpointu?", "Metadata checkpointu opisuje model, dataset i ustawienia, żeby uniknąć pomyłek przy resume albo ewaluacji."),
    ]
    out = []
    for i, (q, a) in enumerate(pairs):
        variants = [
            (q, a),
            (q.replace("Czym", "Wyjaśnij krótko, czym", 1) if q.startswith("Czym") else f"Wyjaśnij krótko: {q}", a),
            (f"Odpowiedz prosto: {q}", a),
            (f"W jednym akapicie: {q}", a),
            (f"Krótko i konkretnie: {q}", a),
        ]
        for j, (instruction, response) in enumerate(variants):
            out.append(record("proste_techniczne_wyjasnienia", instruction, response, f"tech-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def project_advice() -> list[dict]:
    scenarios = [
        ("Mam pomysł na aplikację i chcę od razu zrobić logowanie, dashboard i AI.", "Najpierw zbuduj najmniejszą wersję, która pokazuje główną wartość. Logowanie i dashboard dodaj dopiero, gdy podstawowy przepływ działa."),
        ("Nie wiem, czy zacząć projekt od UI czy od logiki.", "Zacznij od logiki i jednego prostego przepływu. UI dopracuj wtedy, gdy wiadomo już, co naprawdę ma działać."),
        ("Projekt robi się za duży.", "Zapisz jedną najważniejszą funkcję i odłóż resztę na później. Mniejszy zakres łatwiej ukończyć i ocenić."),
        ("Chcę poprawiać wygląd zanim działa backend.", "Najpierw upewnij się, że dane i podstawowe akcje działają. Wygląd ma sens dopiero, gdy nie maskuje braków funkcjonalnych."),
        ("Mam mało czasu na projekt.", "Wybierz wersję, którą da się pokazać od początku do końca. Lepiej mieć prosty działający projekt niż rozbudowany szkic."),
        ("Nie wiem, które funkcje zostawić.", "Zostaw funkcje potrzebne do jednego głównego scenariusza użytkownika. Resztę wpisz jako przyszłe rozszerzenia."),
        ("Chcę dodać AI, bo projekt będzie wyglądał lepiej.", "Dodaj AI tylko wtedy, gdy rozwiązuje konkretny problem. Sama obecność AI nie poprawia projektu."),
        ("Czy warto robić pełną automatyzację od razu?", "Nie zawsze. Najpierw sprawdź ręczny albo prosty półautomatyczny proces, a potem automatyzuj to, co faktycznie się powtarza."),
        ("Mam dużo pomysłów i nie wiem od czego zacząć.", "Wybierz jeden mierzalny cel na najbliższy etap. Po jego wykonaniu łatwiej zdecydować, co ma sens dalej."),
        ("Czy lepiej zrobić ambitnie czy prosto?", "Na start lepiej zrobić prosto, ale solidnie. Ambitniejsze elementy dodaj dopiero po sprawdzeniu podstaw."),
        ("Czy dokumentacja jest potrzebna w małym projekcie?", "Tak, ale krótka. Wystarczy opis uruchomienia, decyzji i ograniczeń."),
        ("Jak uniknąć utknięcia w projekcie?", "Ustal mały punkt kontrolny i sprawdź go szybko. Jeśli nie działa, zawęź zakres zamiast dokładać kolejne funkcje."),
        ("Czy warto od razu robić konta użytkowników?", "Tylko jeśli są konieczne do głównego celu. W przeciwnym razie zacznij bez kont."),
        ("Jak ocenić, czy projekt idzie dobrze?", "Sprawdź, czy da się przejść główny scenariusz od początku do końca. To ważniejsze niż liczba funkcji."),
        ("Co zrobić, gdy projekt jest brzydki, ale działa?", "Najpierw zachowaj działającą wersję. Potem poprawiaj UI w małych krokach, bez psucia logiki."),
        ("Czy robić panel admina od razu?", "Nie, jeśli dane można na początku obsłużyć prościej. Panel admina dodaj, gdy ręczna obsługa naprawdę przeszkadza."),
        ("Jak rozbić duży projekt?", "Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki."),
        ("Czy warto zmieniać stack w połowie?", "Tylko przy konkretnym problemie. Sama ciekawość nowej technologii zwykle opóźnia projekt."),
        ("Czy benchmark jest ważniejszy niż funkcje?", "Benchmark jest ważny, gdy mierzy realny problem. Nie powinien zastępować sprawdzenia, czy projekt działa dla użytkownika."),
        ("Mam pomysł na pięć modułów.", "Zacznij od jednego modułu i pokaż jego wartość. Kolejne moduły dodawaj po sprawdzeniu pierwszego."),
        ("Czy pisać testy od początku?", "Napisz testy dla krytycznej logiki i przypadków, które łatwo zepsuć. Nie musisz testować każdego szczegółu prototypu."),
        ("Jak wybrać następny krok?", "Wybierz krok, który najszybciej zmniejsza największą niepewność w projekcie."),
        ("Czy warto robić roadmapę?", "Tak, ale krótka roadmapa jest lepsza niż długa lista życzeń. Powinna pomagać w decyzjach, nie zastępować pracy."),
        ("Co zrobić, gdy pomysł nie działa?", "Nazwij konkretny problem i sprawdź, czy da się uprościć założenia. Jeśli nie, warto zmienić kierunek wcześnie."),
        ("Czy dodać integrację z zewnętrznym API?", "Dodaj ją dopiero, gdy masz jasny przypadek użycia i plan awarii. Na start często wystarczy lokalny mock."),
        ("Jak zrobić projekt portfolio?", "Pokaż działający efekt, decyzje techniczne, ograniczenia i wnioski. To jest cenniejsze niż lista technologii."),
        ("Czy dodać animacje?", "Dodaj tylko takie animacje, które pomagają zrozumieć stan interfejsu. Dekoracje nie powinny przykrywać funkcji."),
        ("Co jest lepsze: mniej funkcji czy więcej niedokończonych?", "Mniej funkcji, ale działających. Niedokończone funkcje zwykle obniżają wiarygodność projektu."),
        ("Czy optymalizować przed pierwszym demo?", "Optymalizuj tylko oczywiste blokady. Najpierw pokaż pełny przepływ."),
        ("Jak ograniczyć zakres projektu?", "Usuń wszystko, czego nie trzeba do pierwszego działającego scenariusza."),
    ]
    out = []
    prefixes = ["", "Krótko doradź: ", "Co zrobić? ", "Odpowiedz praktycznie: ", "Podaj rozsądny następny krok: "]
    for i, (instruction, response) in enumerate(scenarios):
        for j, prefix in enumerate(prefixes):
            out.append(record("mvp_first_project_advice", prefix + instruction, response, f"mvp-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def missing_data() -> list[dict]:
    items = [
        ("Czy ten laptop jest dobry?", "Nie da się tego ocenić bez modelu, ceny i zastosowania. Do pracy biurowej, gier i programowania kryteria będą inne."),
        ("Czy powinienem to kupić?", "Brakuje informacji o produkcie, cenie, stanie i twoich potrzebach. Bez tego można tylko zgadywać."),
        ("Czy ten wynik jest poprawny?", "Nie mam danych wejściowych ani oczekiwanego wyniku, więc nie da się tego rzetelnie sprawdzić."),
        ("Czy to jest bezpieczne?", "Potrzebny jest kontekst: co dokładnie robisz, w jakim środowisku i jakie są możliwe skutki błędu."),
        ("Czy moja odpowiedź jest dobra?", "Nie da się ocenić bez treści odpowiedzi i kryteriów oceny."),
        ("Czy ten plan ma sens?", "Potrzebuję celu, ograniczeń i dostępnych zasobów. Bez nich plan może wyglądać dobrze, ale nie pasować do sytuacji."),
        ("Czy ten komputer wystarczy?", "To zależy od zastosowania. Podaj programy, budżet i wymagania, wtedy da się ocenić sensownie."),
        ("Czy ta konfiguracja jest optymalna?", "Nie wiadomo bez obciążenia, celu i pomiarów. Najpierw trzeba sprawdzić realne metryki."),
        ("Czy ten model działa dobrze?", "Brakuje wyników ewaluacji i przykładów generacji. Sama nazwa checkpointu nie wystarcza."),
        ("Czy wybrałem dobrą technologię?", "To zależy od wymagań projektu, zespołu i czasu. Bez tych danych odpowiedź byłaby zbyt ogólna."),
        ("Czy mam za mało RAM-u?", "Trzeba znać użycie pamięci pod obciążeniem. Sam rozmiar RAM-u nie mówi, czy jest problem."),
        ("Czy warto kontynuować trening?", "Potrzebne są trendy loss, próbki jakościowe i koszt dalszego treningu. Bez tego decyzja jest niepewna."),
        ("Czy wynik benchmarku jest dobry?", "Trzeba znać sprzęt, ustawienia testu i punkt odniesienia. Sama liczba nie wystarcza."),
        ("Czy ta strona wygląda dobrze?", "Nie da się ocenić bez zrzutu ekranu albo opisu celu i odbiorców."),
        ("Czy to błąd w kodzie?", "Możliwe, ale potrzebny jest komunikat błędu, fragment kodu i sposób odtworzenia problemu."),
    ]
    out = []
    suffixes = [
        "",
        " Odpowiedz ostrożnie.",
        " Nie zgaduj.",
        " Co trzeba wiedzieć?",
        " Jak odpowiedzieć bez danych?",
        " Podaj uczciwą odpowiedź.",
        " Wskaż brakujące informacje.",
        " Nie udawaj pewności.",
        " Odpowiedz krótko.",
        " W jednym akapicie.",
    ]
    for i, (instruction, response) in enumerate(items):
        for j, suffix in enumerate(suffixes):
            out.append(record("brak_danych", instruction + suffix, response, f"missing-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def rewrites() -> list[dict]:
    pairs = [
        ("Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.", "Ten projekt jest solidny, bo ma wiele przydatnych funkcji i działa stabilnie."),
        ("W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.", "Uważam, że ten problem trzeba szybko rozwiązać."),
        ("Aplikacja posiada możliwość wykonywania wielu rzeczy naraz.", "Aplikacja pozwala wykonywać kilka zadań jednocześnie."),
        ("Ten tekst jest napisany w sposób niezbyt dobry i trzeba go poprawić.", "Ten tekst wymaga poprawy."),
        ("Projekt został wykonany przeze mnie i działa on dobrze.", "Samodzielnie wykonałem projekt, który działa poprawnie."),
        ("Nie mogę przyjść dzisiaj, bo wystąpiła u mnie sytuacja prywatna.", "Nie mogę dziś przyjść z powodów prywatnych."),
        ("Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.", "Proszę o informację zwrotną w tej sprawie."),
        ("System działa w taki sposób, że użytkownik może dokonać wyboru opcji.", "System pozwala użytkownikowi wybrać opcję."),
        ("W chwili obecnej nie jestem w stanie wykonać tego zadania.", "Obecnie nie mogę wykonać tego zadania."),
        ("To rozwiązanie cechuje się wysokim poziomem prostoty.", "To rozwiązanie jest proste."),
        ("Należy dokonać sprawdzenia poprawności działania programu.", "Trzeba sprawdzić, czy program działa poprawnie."),
        ("Użytkownik ma możliwość wpisania tekstu do formularza.", "Użytkownik może wpisać tekst w formularzu."),
        ("Wyniki pokazują, że doszło do poprawy jakości.", "Wyniki pokazują poprawę jakości."),
        ("Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.", "Nie zdążę dziś oddać pracy."),
        ("Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.", "Projekt jest ciekawy, ale ma zbyt szeroki zakres na start."),
        ("W celu uruchomienia programu należy nacisnąć przycisk start.", "Aby uruchomić program, naciśnij przycisk Start."),
        ("Dokonano analizy danych oraz wyciągnięto odpowiednie wnioski.", "Przeanalizowano dane i wyciągnięto wnioski."),
        ("Ten fragment można napisać w sposób bardziej naturalny.", "Ten fragment można napisać naturalniej."),
        ("Aplikacja nie posiada jeszcze pełnej funkcjonalności.", "Aplikacja nie ma jeszcze wszystkich funkcji."),
        ("W przypadku wystąpienia błędu należy ponownie uruchomić usługę.", "Jeśli wystąpi błąd, uruchom usługę ponownie."),
        ("Proces treningu został zakończony w sposób poprawny.", "Trening zakończył się poprawnie."),
        ("Wynik nie jest satysfakcjonujący z perspektywy użytkownika.", "Wynik nie jest zadowalający dla użytkownika."),
        ("Interfejs powinien zostać uproszczony w celu poprawy czytelności.", "Interfejs warto uprościć, żeby był czytelniejszy."),
        ("Została przeprowadzona walidacja poprawności działania systemu.", "Sprawdzono poprawność działania systemu."),
        ("Nie posiadam wystarczającej ilości danych do oceny.", "Nie mam wystarczających danych do oceny."),
        ("Należy zwrócić uwagę na możliwość wystąpienia błędów.", "Trzeba uwzględnić ryzyko błędów."),
        ("Warto byłoby dokonać porównania kilku wariantów.", "Warto porównać kilka wariantów."),
        ("Wprowadzone zmiany mają na celu poprawę jakości wyników.", "Zmiany mają poprawić jakość wyników."),
        ("Nie jest możliwe jednoznaczne stwierdzenie bez dodatkowych informacji.", "Bez dodatkowych informacji nie da się tego jednoznacznie stwierdzić."),
        ("Kod powinien zostać uporządkowany przed dalszym rozwojem.", "Przed dalszym rozwojem warto uporządkować kod."),
    ]
    out = []
    templates = [
        ("Popraw tekst: {bad}", "{good}"),
        ("Napisz naturalniej: {bad}", "{good}"),
        ("Skróć i popraw: {bad}", "{good}"),
        ("Przeredaguj zdanie: {bad}", "{good}"),
        ("Usuń lanie wody: {bad}", "{good}"),
    ]
    for i, (bad, good) in enumerate(pairs):
        for j, tpl in enumerate(templates):
            out.append(record("krotkie_poprawki_tekstu", tpl[0].format(bad=bad), tpl[1].format(good=good), f"rewrite-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def summaries() -> list[dict]:
    pairs = [
        ("Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.", "Zbyt szeroki zakres często szkodzi projektom bardziej niż sama trudność."),
        ("Nie każdy problem wymaga aplikacji, kont użytkowników i dashboardu. Czasem wystarczy prosty skrypt albo plik tekstowy.", "Najprostsze rozwiązanie bywa wystarczające."),
        ("Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.", "Samo czytanie odpowiedzi nie gwarantuje zrozumienia."),
        ("Najpierw trzeba zbudować działający prototyp. Dopiero potem warto poprawiać wygląd i automatyzację.", "Najpierw liczy się działający prototyp, potem dopracowanie."),
        ("Model językowy może generować płynny tekst, ale nie oznacza to, że zna prawdę o świecie.", "Płynny tekst modelu nie gwarantuje poprawności faktów."),
        ("Walidacja jest ważna, bo sam spadek train loss może ukrywać overfit.", "Walidacja pomaga wykryć overfit."),
        ("Czysty dataset jest ważniejszy niż sam rozmiar, bo większy model lepiej nauczy się także brudu.", "Jakość danych jest ważniejsza niż ich sama ilość."),
        ("Checkpoint pośredni może być lepszy praktycznie niż najnowszy, jeśli późniejszy trening pogarsza generacje.", "Najlepszy checkpoint nie zawsze jest najnowszy."),
        ("Dashboard ma pomagać w decyzjach, a nie tylko pokazywać dużo liczb.", "Dashboard powinien wspierać decyzje."),
        ("Dobre raporty zapisują nie tylko wynik, ale też założenia i ograniczenia eksperymentu.", "Raport powinien opisywać wynik, założenia i ograniczenia."),
        ("Przed długim treningiem warto zrobić krótki run kontrolny, żeby wykryć błędy pipeline’u.", "Krótki run kontrolny zmniejsza ryzyko długiego treningu."),
        ("Jeśli model powtarza frazy z datasetu, trzeba poprawić dane, a nie tylko zmienić temperaturę.", "Powtarzalny styl często wymaga poprawy danych."),
        ("Instrukcyjny tuning nie dodaje magicznej wiedzy, tylko uczy model formatu odpowiedzi.", "SFT poprawia format odpowiedzi, ale nie zastępuje wiedzy."),
        ("Dane webowe mogą zawierać menu, reklamy, komentarze i inne fragmenty, których model potem uczy się bezkrytycznie.", "Brudne dane webowe mogą przenosić śmieci do modelu."),
        ("W małym modelu krótki kontekst ogranicza zdolność utrzymania dłuższej wypowiedzi.", "Krótki kontekst ogranicza długie generacje."),
        ("Jeśli test zależy od losowego samplingu, trzeba sprawdzić kilka seedów.", "Kilka seedów pomaga odróżnić jakość od losowości."),
        ("Niska temperatura może ograniczyć chaos, ale nie naprawi braku wiedzy ani złych danych.", "Decoding pomaga, ale nie zastępuje jakości danych."),
        ("Najpierw warto sprawdzić, czy pipeline działa, zanim zwiększy się skalę eksperymentu.", "Skalę zwiększa się po sprawdzeniu pipeline’u."),
        ("Model bazowy kontynuuje tekst, więc nie należy oceniać go jak asystenta po instrukcyjnym tuningu.", "Model bazowy ocenia się jako generator kontynuacji."),
        ("Dobre metryki muszą być czytane razem z próbkami jakościowymi.", "Metryki i próbki powinny być analizowane razem."),
        ("Jeżeli walidacja spada, ale próbki są gorsze, trzeba sprawdzić metodologię evala.", "Rozbieżność loss i próbek wymaga audytu evala."),
        ("Nie każdy wzrost liczby parametrów rozwiązuje problemy danych.", "Większy model nadal zależy od jakości danych."),
        ("Mały test SFT ma sprawdzić reakcję modelu, a nie stworzyć gotowego chatbota.", "Smoke SFT jest testem reakcji modelu."),
        ("Jeśli raport nie trafia do łatwego pobrania, trudniej wrócić do decyzji po czasie.", "Raporty powinny być łatwe do znalezienia."),
        ("Przy eksperymentach warto oddzielać checkpoint najlepszy praktycznie od najnowszego diagnostycznego.", "Best checkpoint i latest checkpoint mogą być różne."),
        ("Częste checkpointy pomagają przy ryzyku awarii, ale zajmują dużo miejsca.", "Checkpointy zwiększają bezpieczeństwo kosztem miejsca."),
        ("Dobre ograniczenia zasobów chronią inne usługi na tym samym serwerze.", "Limity zasobów chronią stabilność hosta."),
        ("Dataset bez metadanych źródła utrudnia późniejsze usuwanie problematycznych fragmentów.", "Source metadata pomaga czyścić dane."),
        ("Ewaluacja jakościowa nie jest idealna, ale pokazuje problemy niewidoczne w samym loss.", "Eval jakościowy uzupełnia loss."),
        ("Nie warto trenować dalej tylko dlatego, że trening technicznie działa.", "Techniczna stabilność nie wystarcza do decyzji o dalszym treningu."),
    ]
    out = []
    templates = [
        ("Streść w jednym zdaniu: {text}", "{summary}"),
        ("Wyciągnij najważniejszą myśl: {text}", "{summary}"),
        ("Skróć tekst: {text}", "{summary}"),
        ("Podaj krótkie streszczenie: {text}", "{summary}"),
        ("Napisz sedno tego tekstu: {text}", "{summary}"),
    ]
    for i, (text, summary) in enumerate(pairs):
        for j, tpl in enumerate(templates):
            out.append(record("mini_streszczenia", tpl[0].format(text=text), tpl[1].format(summary=summary), f"summary-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def anti_loops() -> list[dict]:
    prompts = [
        ("Napisz krótką odpowiedź i nie powtarzaj tej samej myśli.", "Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się, gdy ta myśl jest jasna."),
        ("Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?", "Nie. Lepsza jest krótka, konkretna odpowiedź niż długi tekst bez treści."),
        ("Ten tekst nie powinien się zapętlać. Wyjaśnij krótko dlaczego.", "Zapętlenie utrudnia zrozumienie i nie dodaje nowych informacji."),
        ("Odpowiedz krótko: czego nie da się ocenić bez danych?", "Bez danych nie da się rzetelnie ocenić jakości, bezpieczeństwa ani opłacalności decyzji."),
        ("Zakończ po jednej myśli: po co robi się testy?", "Testy pomagają wykrywać błędy i upewnić się, że zmiany nie psują działania."),
        ("Napisz bez powtarzania: co zrobić, gdy brakuje informacji?", "Trzeba wskazać, jakich informacji brakuje, i nie zgadywać wyniku."),
        ("Odpowiedz krótko i zakończ naturalnie: czym jest backup?", "Backup to kopia danych potrzebna do odtworzenia ich po awarii."),
        ("Nie rozwijaj bez końca: dlaczego warto mierzyć loss?", "Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne."),
        ("Jedna myśl, bez listy: kiedy projekt jest za duży?", "Projekt jest za duży, gdy nie da się szybko pokazać jego głównej wartości."),
        ("Zakończ odpowiedź po drugim zdaniu: czym jest tokenizer?", "Tokenizer dzieli tekst na tokeny. Dzięki temu model może pracować na liczbach zamiast bezpośrednio na znakach."),
    ]
    out = []
    endings = [
        "",
        " Bez dodatkowego komentarza.",
        " Nie powtarzaj.",
        " Zakończ naturalnie.",
        " Nie dodawaj przykładu.",
        " W jednym akapicie.",
        " Jednym zdaniem.",
        " Bez listy.",
        " Bez drugiej myśli.",
        " Tylko sedno.",
        " Zwięźle.",
        " Nie rozwijaj dalej.",
        " Bez metafor.",
        " Bez dygresji.",
        " Odpowiedz wprost.",
    ]
    for i, (instruction, response) in enumerate(prompts):
        for j, suffix in enumerate(endings):
            out.append(record("anty_petle", instruction + suffix, response, f"loop-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def natural_endings() -> list[dict]:
    pairs = [
        ("Napisz krótką odpowiedź o tym, dlaczego warto robić notatki.", "Notatki pomagają wrócić do decyzji i nie powtarzać tych samych analiz."),
        ("Wyjaśnij jednym akapitem, po co robi się raport po eksperymencie.", "Raport zapisuje wynik, ustawienia i wnioski, dzięki czemu można później podjąć lepszą decyzję."),
        ("Napisz neutralną wiadomość, że nie mogę dziś przyjść.", "Cześć, niestety nie mogę dziś przyjść. Dam znać, kiedy będę dostępny."),
        ("Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.", "Dzień dobry, nie zdążę dziś oddać pracy. Czy mogę dosłać ją jutro?"),
        ("Odpowiedz spokojnie: projekt nie działa, co teraz?", "Najpierw sprawdź ostatnią zmianę, log błędu i najprostszy sposób odtworzenia problemu."),
        ("Napisz krótkie wyjaśnienie, dlaczego nie warto zgadywać bez danych.", "Zgadywanie może prowadzić do złych decyzji. Lepiej jasno wskazać brakujące informacje."),
        ("Zakończ naturalnie: czym jest prototyp?", "Prototyp to wczesna wersja rozwiązania używana do sprawdzenia, czy pomysł ma sens."),
        ("Napisz krótko, dlaczego warto robić backup.", "Backup chroni przed utratą danych po awarii, błędzie lub przypadkowym usunięciu."),
        ("Odpowiedz w dwóch zdaniach: czym jest walidacja?", "Walidacja sprawdza model na danych poza treningiem. Dzięki temu łatwiej zauważyć overfit."),
        ("Napisz krótką odpowiedź: czy więcej funkcji zawsze oznacza lepszy projekt?", "Nie. Lepszy projekt rozwiązuje konkretny problem, a nadmiar funkcji może przeszkadzać."),
        ("Wyjaśnij prosto, czym jest log.", "Log to zapis zdarzeń z działania programu, przydatny przy diagnozowaniu błędów."),
        ("Napisz krótką odpowiedź: po co ograniczać zakres?", "Ograniczenie zakresu pomaga szybciej ukończyć działającą wersję i sprawdzić pomysł."),
        ("Odpowiedz bez lania wody: czym jest checkpoint?", "Checkpoint to zapis stanu modelu, do którego można wrócić później."),
        ("Napisz końcową uwagę do raportu technicznego.", "Wnioski warto potwierdzić kolejnym krótkim testem przed większą zmianą."),
        ("Napisz prostą odpowiedź: czy wynik loss wystarczy do oceny modelu?", "Nie. Loss trzeba połączyć z próbkami generacji i ewaluacją jakościową."),
    ]
    out = []
    variants = [
        "",
        " Odpowiedź ma być krótka.",
        " Bez listy.",
        " Jednym akapitem.",
        " Zakończ po sensownej myśli.",
        " Bez dopisywania dalszych przykładów.",
        " Naturalnie.",
        " Prosto.",
        " Bez rozwijania w kolejny temat.",
        " Zwięźle.",
    ]
    for i, (instruction, response) in enumerate(pairs):
        for j, suffix in enumerate(variants):
            out.append(record("naturalne_zakonczenia", instruction + suffix, response, f"end-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def everyday_questions() -> list[dict]:
    pairs = [
        ("Jak zaplanować naukę na jutro?", "Wybierz dwa najważniejsze tematy i zaplanuj krótkie bloki pracy z przerwami."),
        ("Co zrobić, gdy mam za dużo zadań?", "Spisz zadania, wybierz najpilniejsze i usuń albo odłóż te, które nie są konieczne dziś."),
        ("Jak napisać prostą wiadomość z przeprosinami?", "Napisz, za co przepraszasz, krótko wyjaśnij sytuację i zaproponuj następny krok."),
        ("Jak zacząć porządkować pliki?", "Najpierw utwórz kilka głównych folderów i przenieś do nich oczywiste pliki."),
        ("Co zrobić, gdy nie rozumiem polecenia?", "Poproś o doprecyzowanie i powtórz własnymi słowami, jak rozumiesz zadanie."),
        ("Jak wybrać temat projektu?", "Wybierz temat, który da się zrealizować w dostępnym czasie i który możesz pokazać działająco."),
        ("Jak ograniczyć rozpraszacze?", "Wyłącz zbędne powiadomienia i pracuj przez krótki, ustalony czas nad jednym zadaniem."),
        ("Jak napisać krótkie podsumowanie?", "Zostaw tylko główną myśl, wynik i najważniejszy wniosek."),
        ("Co zrobić, gdy coś działa wolno?", "Najpierw zmierz, co jest wąskim gardłem, zamiast zgadywać przyczynę."),
        ("Jak sprawdzić, czy pomysł ma sens?", "Zrób prosty prototyp albo krótki test z realnym przykładem użycia."),
        ("Jak powiedzieć, że nie mam czasu?", "Napisz krótko, że teraz nie możesz się tym zająć, i podaj możliwy termin."),
        ("Jak przygotować się do rozmowy o projekcie?", "Przygotuj cel, obecny stan, problemy i jedną decyzję, której potrzebujesz."),
        ("Co zrobić, gdy odpowiedź jest zbyt długa?", "Usuń powtórzenia i zostaw tylko informacje potrzebne do decyzji."),
        ("Jak ocenić, czy tekst jest jasny?", "Sprawdź, czy po pierwszym czytaniu wiadomo, o co chodzi i co trzeba zrobić."),
        ("Jak zacząć raport?", "Zacznij od celu, wyniku i najważniejszego wniosku."),
        ("Jak kończyć odpowiedź?", "Zakończ wtedy, gdy główna myśl jest jasna i nie dodawaj nowych wątków na siłę."),
        ("Jak wybrać priorytet?", "Wybierz zadanie, które usuwa największą blokadę albo daje najwięcej informacji."),
        ("Co zrobić, gdy wynik mnie zaskakuje?", "Sprawdź dane wejściowe, metodę pomiaru i powtórz test w tych samych warunkach."),
        ("Jak poprosić o feedback?", "Pokaż konkretny fragment i zapytaj o jedną rzecz, którą chcesz poprawić."),
        ("Jak skrócić listę funkcji?", "Zostaw tylko te funkcje, które są potrzebne do podstawowego scenariusza."),
        ("Co zrobić, gdy projekt stoi?", "Znajdź najmniejszy krok, który da się wykonać dziś, i sprawdź jego efekt."),
        ("Jak nie przeciążyć planu?", "Dodawaj rezerwę czasu i nie zakładaj, że wszystko zadziała za pierwszym razem."),
        ("Jak pisać prościej?", "Używaj krótszych zdań i konkretnych czasowników."),
        ("Jak odpowiedzieć, gdy nie znam szczegółów?", "Powiedz, czego brakuje, i zaproponuj, jakie informacje są potrzebne."),
        ("Jak porównać dwie opcje?", "Ustal kryteria, porównaj koszt i ryzyko, a potem wybierz opcję lepiej pasującą do celu."),
        ("Jak zacząć naukę nowego narzędzia?", "Uruchom najmniejszy przykład i dopiero potem dodawaj bardziej złożone elementy."),
        ("Co zrobić, gdy mam sprzeczne wyniki?", "Sprawdź konfigurację testu i powtórz pomiar w kontrolowanych warunkach."),
        ("Jak dbać o jakość danych?", "Zbieraj źródła, usuwaj duplikaty i sprawdzaj losowe próbki."),
        ("Jak uniknąć złych decyzji technicznych?", "Zapisuj założenia i sprawdzaj je krótkimi testami."),
        ("Jak przygotować demo?", "Pokaż jeden działający scenariusz i nie ukrywaj znanych ograniczeń."),
    ]
    out = []
    variants = ["", " Odpowiedz krótko.", " Jednym akapitem.", " Bez listy.", " Daj prostą radę."]
    for i, (instruction, response) in enumerate(pairs):
        for j, suffix in enumerate(variants):
            out.append(record("codzienne_proste_pytania", instruction + suffix, response, f"daily-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def cautious_uncertainty() -> list[dict]:
    pairs = [
        ("Czy ta diagnoza jest pewna?", "Nie. Bez pełnych danych można mówić tylko o najbardziej prawdopodobnym wyjaśnieniu."),
        ("Czy zawsze warto wybrać szybsze rozwiązanie?", "Nie zawsze. Szybsze rozwiązanie ma sens, jeśli nie zwiększa zbyt mocno ryzyka i długu technicznego."),
        ("Czy nowsza wersja zawsze jest lepsza?", "Nie. Nowsza wersja może mieć poprawki, ale też nowe błędy albo niezgodności."),
        ("Czy większy model zawsze daje lepszy wynik?", "Nie. Większy model nadal zależy od jakości danych, treningu i sposobu ewaluacji."),
        ("Czy można ufać jednej próbce generacji?", "Nie. Jedna próbka może być przypadkowo dobra albo zła, więc warto sprawdzić więcej przykładów."),
        ("Czy niski loss oznacza dobry model?", "Nie zawsze. Loss jest ważny, ale trzeba też sprawdzić jakość generacji."),
        ("Czy benchmark wystarczy do decyzji?", "Nie. Benchmark trzeba połączyć ze stabilnością, kosztami i jakością wyniku."),
        ("Czy model może zmyślać?", "Tak. Model językowy może generować tekst brzmiący pewnie, nawet gdy informacja jest błędna."),
        ("Czy warto ignorować ostrzeżenia w logach?", "Nie. Ostrzeżenia mogą wskazywać problem, który później stanie się awarią."),
        ("Czy test na małej próbce wystarcza?", "Wystarcza do wstępnej decyzji, ale nie do mocnego wniosku jakościowego."),
        ("Czy można ocenić bezpieczeństwo bez kontekstu?", "Nie. Bez kontekstu da się najwyżej wskazać możliwe ryzyka."),
        ("Czy jedna metryka wystarczy?", "Rzadko. Lepiej użyć kilku metryk i sprawdzić przykłady ręcznie."),
        ("Czy kontynuować, gdy wynik jest mieszany?", "Najpierw trzeba ustalić, czy problem wynika z danych, modelu, czy sposobu oceny."),
        ("Czy automat powinien kasować stare checkpointy?", "Nie bez jasnej polityki retencji i potwierdzenia, bo checkpointy mogą być potrzebne do powrotu."),
        ("Czy model po SFT staje się asystentem?", "Nie automatycznie. SFT może poprawić format, ale jakość zależy od bazy i datasetu."),
        ("Czy dane webowe są zawsze złe?", "Nie, ale wymagają filtracji, bo mogą zawierać reklamy, menu i komentarze."),
        ("Czy mniejszy dataset może być lepszy?", "Tak, jeśli jest znacznie czystszy i lepiej pasuje do celu."),
        ("Czy trzeba trenować do końca planu?", "Nie. Jeśli eval pokazuje regres, lepiej zatrzymać się i przeanalizować przyczynę."),
        ("Czy zmiana temperatury naprawi model?", "Może poprawić stabilność generacji, ale nie naprawi braków danych ani wiedzy."),
        ("Czy wynik 50k musi być lepszy niż 44k?", "Nie. Późniejszy checkpoint może mieć niższą stratę, ale gorsze próbki jakościowe."),
        ("Czy trzeba robić pełny rebuild danych?", "Tylko jeśli obecne dane blokują dalszą poprawę albo wnoszą powtarzalne błędy."),
        ("Czy można porównać modele bez tych samych promptów?", "Można orientacyjnie, ale uczciwe porównanie wymaga tych samych promptów i ustawień."),
        ("Czy wynik z jednego seeda jest pewny?", "Nie. Dla samplingu warto sprawdzić kilka seedów."),
        ("Czy warto publikować eksperymentalny model?", "Można publikować jako eksperyment, ale trzeba jasno opisać ograniczenia."),
        ("Czy model bazowy powinien odpowiadać na instrukcje?", "Nie musi. Model bazowy głównie kontynuuje tekst."),
        ("Czy SFT może popsuć styl bazowy?", "Tak. Zbyt mocny albo schematyczny SFT może ograniczyć naturalność generacji."),
        ("Czy krótsze odpowiedzi zawsze są lepsze?", "Nie. Są lepsze wtedy, gdy odpowiadają na pytanie bez utraty potrzebnych informacji."),
        ("Czy brak błędu technicznego oznacza sukces?", "Nie. Trening może być stabilny technicznie, ale nadal dawać słaby model."),
        ("Czy można zgadywać brakujące parametry?", "Lepiej tego nie robić. Trzeba wskazać założenia albo poprosić o brakujące dane."),
        ("Czy warto robić kolejny etap bez raportu?", "Nie. Raport pomaga uniknąć powtarzania tych samych błędów."),
    ]
    out = []
    variants = ["", " Odpowiedz ostrożnie.", " Bez przesadnej pewności.", " Krótko.", " Wskaż ograniczenie."]
    for i, (instruction, response) in enumerate(pairs):
        for j, suffix in enumerate(variants):
            out.append(record("ostrozne_odpowiedzi_przy_niepewnosci", instruction + suffix, response, f"caution-{i}-{j}"))
    return cycle_take(out, CATEGORY_TARGET)


def build_records() -> list[dict]:
    builders = [
        definitions,
        technical_explanations,
        project_advice,
        missing_data,
        rewrites,
        summaries,
        anti_loops,
        natural_endings,
        everyday_questions,
        cautious_uncertainty,
    ]
    records: list[dict] = []
    for builder in builders:
        records.extend(builder())
    rng = random.Random(2026)
    rng.shuffle(records)
    for idx, item in enumerate(records, 1):
        item["id"] = f"glyph100-sft-smoke-v0-{idx:04d}"
    return records


def suspicious_counts(records: list[dict]) -> dict[str, int]:
    counts = {}
    for pattern in SUSPICIOUS_PATTERNS:
        pattern_l = pattern.lower()
        counts[pattern] = sum(
            1
            for r in records
            if pattern_l in (r["instruction"] + "\n" + r["response"]).lower()
        )
    return counts


def duplicate_report(records: list[dict]) -> dict:
    instruction_counts = Counter(normalize_for_dupes(r["instruction"]) for r in records)
    pair_counts = Counter(normalize_for_dupes(r["instruction"] + "\n" + r["response"]) for r in records)
    return {
        "duplicate_instructions_extra": sum(c - 1 for c in instruction_counts.values() if c > 1),
        "duplicate_pairs_extra": sum(c - 1 for c in pair_counts.values() if c > 1),
    }


def write_markdown_report(path: Path, records: list[dict], report: dict) -> None:
    by_category: dict[str, list[dict]] = defaultdict(list)
    for item in records:
        by_category[item["category"]].append(item)
    lines = [
        "# Glyph-100M SFT smoke v0 dataset report",
        "",
        "## Summary",
        "",
        f"- examples: {report['stats']['examples']}",
        f"- avg instruction words: {report['stats']['instruction_words_avg']:.2f}",
        f"- avg response words: {report['stats']['response_words_avg']:.2f}",
        f"- max template tokens: {report['stats']['token_stats']['template_max']}",
        f"- over context 512: {report['stats']['token_stats']['over_context']}",
        f"- duplicate instructions extra: {report['duplicates']['duplicate_instructions_extra']}",
        f"- duplicate instruction+response extra: {report['duplicates']['duplicate_pairs_extra']}",
        "",
        "## Categories",
        "",
    ]
    for category, count in sorted(report["stats"]["categories"].items()):
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## Suspicious Phrases", ""])
    for phrase, count in report["suspicious_phrase_counts"].items():
        lines.append(f"- `{phrase}`: {count}")
    lines.extend(["", "## Examples Per Category", ""])
    for category, items in sorted(by_category.items()):
        lines.append(f"### {category}")
        lines.append("")
        for item in items[:3]:
            lines.append(f"- prompt: {item['instruction']}")
            lines.append(f"  response: {item['response']}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Glyph-100M SFT smoke dataset")
    parser.add_argument("--output", default="data/sft/glyph100_sft_smoke_v0.jsonl")
    parser.add_argument("--report-md", default="data/sft/glyph100_sft_smoke_v0_report.md")
    parser.add_argument("--report-json", default="data/sft/glyph100_sft_smoke_v0_report.json")
    parser.add_argument("--tokenizer", default="data/processed/tokenizer.model")
    parser.add_argument("--context-len", type=int, default=512)
    args = parser.parse_args()

    records = build_records()
    sp = load_sentencepiece(args.tokenizer)
    stats = collect_dataset_stats(records, sp=sp, context_len=args.context_len)
    duplicates = duplicate_report(records)
    suspicious = suspicious_counts(records)

    empty_fields = [
        r["id"]
        for r in records
        if not r.get("instruction", "").strip() or not r.get("response", "").strip()
    ]
    over_context = stats["token_stats"]["over_context"]
    if empty_fields:
        raise SystemExit(f"empty fields found: {empty_fields[:5]}")
    if over_context:
        raise SystemExit(f"examples over context: {over_context}")
    if any(suspicious.values()):
        raise SystemExit(f"suspicious phrases found: {suspicious}")

    report = {
        "dataset": "glyph100_sft_smoke_v0",
        "purpose": "small controlled SFT smoke test for Glyph-100M 44k checkpoint",
        "context_len": args.context_len,
        "output": args.output,
        "tokenizer": args.tokenizer,
        "stats": stats,
        "duplicates": duplicates,
        "empty_fields": empty_fields,
        "suspicious_phrase_counts": suspicious,
        "quality_notes": [
            "Polish-only synthetic curated examples.",
            "Short answers with natural endings.",
            "No pseudo-encyclopedic demographic/date patterns.",
            "No web/forum/commerce/cookie residue phrases.",
        ],
    }

    write_jsonl(args.output, records)
    write_json(args.report_json, report)
    write_markdown_report(Path(args.report_md), records, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
