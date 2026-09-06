# Glyph-100M: następny duży krok

Generated: 2026-07-16T07:20:40+00:00

## Decyzja

**Nie zwiększać teraz modelu i nie ciągnąć starego checkpointu. Największym sensownym krokiem jest ponowny trening tego samego Glyph-100M od zera na nowym korpusie `glyph100_dataset_v2_4_1_core`, najpierw jako kontrolowane proxy 1k, a następnie 5k.**

To jest większy krok niż dalsze poprawianie decoding albo kolejny mały SFT, bo usuwa trzy ograniczenia starego eksperymentu naraz:

1. zbyt wiki-heavy i wielokrotnie przechodzony korpus v2.3.1,
2. sampling z powtórzeniami zamiast pełnego tasowania bloków,
3. ewaluację, która wcześniej nie rozpoznawała prawidłowego EOS.

Pełnego treningu nie uruchomiono. GPU wykonało wyłącznie jeden rzeczywisty krok smoke testu.

## Co jest gotowe

- nowy korpus v2.4.1: **279,496,401 tokenów**,
- train/val: **278,089,665 / 1,406,736 tokenów**,
- dokumenty/chunki: **201,746**, rodzice: **193,129**,
- przeciek rodziców train-val: **0**,
- duplikaty identyfikatorów: **0**,
- Wikipedia: **42.94%**, literatura: **46.20%**, legacy/web crawl: **0%**,
- tokenizer: istniejący SentencePiece 16k, SHA-256 `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`,
- 9/9 niezależnych twardych kontroli datasetu: PASS,
- 12/12 testów kodu generacji, samplera i buildera: PASS,
- jeden pełny krok ROCm: PASS, 2,864 tok/s, brak NaN/OOM/crash.

## Skąd są dane

| Źródło | Tokeny | Udział | Rola |
|---|---:|---:|---|
| Wikipedia PL | 120,003,040 | 42.94% | wiedza encyklopedyczna |
| Wolne Lektury | 55,037,100 | 19.69% | literatura i naturalna polszczyzna |
| Wikisource | 30,048,511 | 10.75% | literatura, tylko train |
| 1000 polskich powieści | 30,196,490 | 10.80% | dłuższa proza |
| korpus parlamentarny | 23,852,526 | 8.53% | współczesny język formalny |
| ELTeC PL | 13,841,376 | 4.95% | kuratorowana literatura |
| Wikibooks PL | 3,772,313 | 1.35% | tekst edukacyjny |
| Wikinews PL | 2,745,045 | 0.98% | współczesny styl informacyjny |

Publicznym źródłem agregującym większość nowych, source-aware danych jest [Polish Dynaword](https://huggingface.co/datasets/SlayerLab/polish-dynaword). Surowe pliki kontrolowane są manifestem i leżą na HDD; na SSD zostały tylko binaria potrzebne do treningu.

`FinetextPL-Edu` pozostaje gated/pending i nie jest zależnością tego planu. HPLT3 oraz FineWeb2-HQ zostały zbadane próbkami, ale odrzucone jako główne źródła: po naszych filtrach przechodziło odpowiednio tylko 6.85% HPLT3 z etykietami register-aware i około 15.2% FineWeb2-HQ, a ręczne próbki nadal zawierały istotny webowy szum.

## Co zostało poprawione w pipeline

### Sampler

Glyph-100M domyślnie używa teraz tasowanych, niepokrywających się bloków bez losowania ze zwracaniem. Checkpoint przechowuje dokładny stan samplera, więc resume odtwarza kolejny batch, a nie tylko przybliżony seed.

### Split dokumentowy

Chunki jednej książki lub dokumentu mają wspólny `parent_doc_id`. Cały rodzic trafia wyłącznie do train albo val. Wikisource nie ma wystarczającego upstreamowego identyfikatora dzieła, dlatego jego 30.0M tokenów jest świadomie train-only zamiast tworzyć pozornie poprawny, przeciekający val.

### Generacja i eval

Generator zatrzymuje się na EOS i raportuje faktyczną liczbę nowych tokenów. Powtórny eval 44k/50k pokazał, że stary licznik ucięć przeceniał problem, ponieważ traktował generacje zakończone EOS jak cutoff. Mimo tego 44k pozostaje bezpiecznym best practical checkpointem: w zestawieniu par 44k wygrał 52 razy, 50k 44 razy, a 84 przypadki były remisami.

### Kontrola danych

Budowa v2.4.1 zachowuje źródło, dokument nadrzędny, licencję i wynik jakości. Selekcja limitów tokenowych odbywa się całymi rodzicami. Niezależny walidator ponownie policzył dokumenty i tokeny z JSONL oraz sprawdził rozmiary obu plików uint16.

## Co oznaczają wykryte wzorce

Walidator znalazł 1,638 dopasowań heurystyki `web_residue`, wszystkie w Wikipedii. Ręczne próbki to głównie fałszywe trafienia słowa `forum` w nazwach instytucji albo poprawne artykuły, nie sklepy, cookies czy SEO. Z kolei 30,121 trafień `pseudo_ency` to w większości oczekiwany styl biografii i opisów miejsc w części Wikipedii. Liczników nie należy przedstawiać jako błędów 1:1; są alarmem do inspekcji próbek.

## Ekspozycja danych

Przy 16,384 tokenach na krok:

| Punkt kontrolny | Tokeny przetworzone | Przejścia po train |
|---|---:|---:|
| 1k | 16.38M | 0.06x |
| 5k | 81.92M | 0.29x |
| 20k | 327.68M | 1.18x |
| 50k | 819.20M | 2.95x |

1k ma sprawdzić stabilność, checkpointy, loss i realny throughput. 5k jest pierwszym sensownym proxy jakościowym. 20k i 50k nie są zatwierdzone i nie powinny uruchamiać się automatycznie.

## Ryzyka

- **Archaiczny styl:** 46.2% tokenów literackich może przesunąć język w stronę starszej polszczyzny.
- **Niepełna reprezentacja val:** Wikisource jest train-only, więc walidacja nie mierzy tej części korpusu.
- **Wikipedia nadal największym pojedynczym źródłem:** udział spadł poniżej 45%, ale styl encyklopedyczny pozostaje ważnym sygnałem.
- **Korpus parlamentarny:** 8.5% może zwiększyć formalny, urzędowy ton.
- **Smoke to nie trening:** jeden krok dowodzi poprawności wykonania, nie jakości ani wielogodzinnej stabilności.
- **Model pozostaje mały:** 97.65M parametrów nie stanie się dużym asystentem samą zmianą danych.

## Rekomendowany plan

1. Po osobnej zgodzie uruchomić **from-scratch 1k** w nowym katalogu checkpointów i logów.
2. Zatrzymać się, sprawdzić loss, val, temperatury, checkpoint i resume.
3. Jeśli 1k jest zdrowe, uruchomić **do 5k total**, nie 5k dodatkowych.
4. Porównać v2.4.1 z historycznym modelem przy zbliżonej ekspozycji tokenów, tym samym EOS-aware evalem i kilkoma seedami.
5. Dopiero wtedy zdecydować o 20k. 50k wymaga osobnej decyzji po 20k.

## Werdykt

**Dataset i pipeline są gotowe do kontrolowanego stage 0/1k. Nie ma jeszcze podstaw do pełnego runu.** To jest obecnie najlepsza ścieżka dużego postępu bez nowego GPU: nie większy model, lecz uczciwy restart Glyph-100M na lepszych danych i z naprawioną metodologią.
