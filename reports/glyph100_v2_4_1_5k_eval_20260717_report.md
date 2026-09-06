# Glyph-100M v2.4.1: raport po 5k

Data oceny: 2026-07-17

## Werdykt

**Można rozważyć kontrolowaną kontynuację do 10k total na tym samym
datasecie, ale checkpoint 5k nie jest jeszcze modelem jakościowym.**

Trening i resume są technicznie zdrowe, loss spada na całym validation set
oraz osobno na każdym źródle. Checkpoint 5k jest najlepszy z punktów
1k/2k/3k/4k/5k w użytym teście, ale przewaga nad 2k i 4k jest niewielka.
Generacje nadal są semantycznie słabe i często wpadają w łatwe szablony
parlamentarne oraz pseudo-encyklopedyczne.

Nie uruchomiono 10k ani żadnego innego treningu w ramach tego evala.

## Stan techniczny

- Model: `Glyph-100M`, wariant `glyph-100m`
- Dataset: `glyph100_dataset_v2_4_1_core`
- Checkpoint: `checkpoints/glyph-100m-v2_4_1-5k/latest.pt`
- Step: `5000`
- Tokeny przetworzone: `81,920,000`
- Udział train corpus: `29.46%` jednego przejścia
- Batch / grad accumulation: `4 / 8`
- Effective tokens/step: `16,384`
- Context: `512`
- Tokenizer SHA-256: `21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`
- Optimizer state: obecny
- Scheduler metadata: obecne, krok `5000`
- Resume check: przeszedł; odtworzono step, optimizer i sampler cursor `160,000`
- NaN / Inf / OOM / crash: brak
- Aktywny trening po ewaluacji: brak

Checkpointy `latest.pt` i `step_0005000.pt` ładują się poprawnie i mają
zgodne metadata. Katalog checkpointów 5k zajmuje około `5.5 GiB`.

## Przebieg

- Run 0 -> 1k: około `1 h 24 min`
- Run 1k -> 5k: `5 h 35 min 10 s`
- Łączny czas aktywnego treningu 0 -> 5k: około `6 h 59 min`
- End-to-end throughput: około `3,255 tok/s`
- Stabilny throughput bez eval/checkpoint overhead: około `3,283 tok/s`
- GPU edge podczas runu 1k -> 5k: średnio `65.9 C`, maks. `67 C`
- GPU hotspot: średnio `88.6 C`, maks. `95 C`
- Pobór GPU: średnio `113.9 W`, maks. odczyt `128 W`

Temperatury były wysokie, ale nie przekroczyły ustalonego progu stop.

## Validation loss

| step | val loss |
|---:|---:|
| 250 | 7.9565 |
| 500 | 7.3277 |
| 750 | 6.8266 |
| 1000 | 6.4298 |
| 1500 | 5.9220 |
| 2000 | 5.6551 |
| 2500 | 5.3442 |
| 3000 | 5.0933 |
| 3500 | 4.9110 |
| 4000 | 4.7702 |
| 4500 | 4.6665 |
| 5000 | 4.5902 |

Trend jest monotonicznie malejący. Nie ma sygnału overfitu na tym etapie.

## Walidacja per source

| source | 1k val loss | 5k val loss | zmiana |
|---|---:|---:|---:|
| 1000_novels | 6.1635 | 4.7146 | -1.4489 |
| eltec_pol | 6.0083 | 4.5009 | -1.5074 |
| parliamentary | 6.4505 | 4.3750 | -2.0754 |
| wikibooks | 7.0727 | 5.2204 | -1.8523 |
| wikinews | 7.0261 | 5.1516 | -1.8745 |
| wikipedia_pl | 6.7542 | 4.6365 | -2.1176 |
| wolne_lektury | 6.0762 | 4.5322 | -1.5440 |

Każde mierzone źródło się poprawiło. `Wikisource` jest train-only z powodu
braku bezpiecznego parent-work splitu, dlatego nie ma osobnego val loss.

Ważna obserwacja: parlament i Wikipedia poprawiają się najszybciej.
To są źródła z wieloma łatwymi, powtarzalnymi konstrukcjami. Model uczy się
ich szybciej niż bardziej zróżnicowanej prozy, co jest widoczne w generacji.

## Eval checkpointów 1k-5k

20 promptów, dwa presety, po 40 próbek na checkpoint.

| checkpoint | avg score | natural ends | cutoff-like | repetition | pseudo-ency | web residue |
|---|---:|---:|---:|---:|---:|---:|
| 1k | 2.150 | 6/40 | 37/40 | 22/40 | 12/40 | 0/40 |
| 2k | 2.975 | 9/40 | 33/40 | 17/40 | 9/40 | 0/40 |
| 3k | 2.825 | 5/40 | 37/40 | 16/40 | 6/40 | 0/40 |
| 4k | 2.875 | 4/40 | 39/40 | 11/40 | 11/40 | 0/40 |
| 5k | 3.000 | 6/40 | 40/40 | 13/40 | 7/40 | 0/40 |

Pairwise:

- 5k wygrywa z 1k: `21`; 1k wygrywa: `7`; remisy: `12`
- 5k wygrywa z 4k: `14`; 4k wygrywa: `10`; remisy: `16`

Heurystyka ocenia zakończenia, pętle i residue. Nie jest oceną wiedzy ani
pełnym testem semantycznym.

## Ocena ręczna

5k jest bardziej podobne do polskiego tekstu niż 1k, lecz nadal często nie
kontynuuje znaczenia promptu. Najczęstsze problemy:

- rejestr parlamentarny: `Dziękuję`, `pan poseł`, `Wysoka Izbo`, ustawy,
  komisje i pytania do ministra;
- szablony Wikipedii o wsiach: gmina, powiat, województwo i fraza
  `w latach 1975-1998`;
- płynna składniowo, lecz semantycznie pusta wypowiedź;
- brak nauczenia końca dokumentu: wszystkie 40 generacji 5k doszły do limitu
  80 nowych tokenów;
- nadal 13/40 próbek z powtórzeniami.

Nie wykryto URL/HTML/SEO residue w tym zestawie. Problemem jest styl źródeł,
nie klasyczny web garbage.

Przykłady regresu semantycznego:

- `Woda jest substancją` -> model przechodzi do prawa administracyjnego.
- `W średniowieczu` -> model tworzy fałszywy opis wsi i województwa.
- `Uczenie maszynowe polega na` -> model przechodzi do projektu ustawy.

## Dlaczego nie zatrzymywać po 5k

Model zobaczył dopiero około `0.295` epoki i `81.92M` tokenów, czyli mniej
tokenów niż ma parametrów logicznych. Na tym etapie brak spójnych generacji
nie jest zaskakujący. Jednocześnie:

- train i val loss spadają;
- wszystkie źródła poprawiają się osobno;
- checkpoint/resume działa;
- 5k wygrywa z 1k;
- nie ma awarii ani klasycznego web garbage.

Przerwanie teraz nie dałoby odpowiedzi, czy bardziej zróżnicowane wzorce
zaczną wygrywać po dalszym treningu.

## Rekomendowany następny krok

Po osobnej zgodzie: kontrolowana kontynuacja `5k -> 10k total` na tym samym
datasecie i configu. Przy 10k model przetworzy `163.84M` tokenów, czyli około
`0.589` epoki.

Warunki:

1. Zachować osobny checkpoint/log directory dla runu 10k.
2. Zapisać checkpointy co 1k oraz obowiązkowo 7.5k i 10k.
3. Eval loss co 500 kroków.
4. Powtórzyć ten sam completion eval na 7.5k i 10k.
5. Powtórzyć source-specific validation na 10k.
6. Nie robić SFT ani publicznego demo.
7. Po 10k zatrzymać się i porównać 5k/7.5k/10k.

Warunek zmiany datasetu: jeśli przy 10k nadal dominują szablony
parlamentarne/gminne, a poprawa semantyczna jest mała mimo spadającego loss,
nie iść dalej automatycznie. Wtedy przygotować v2.4.2 z ograniczeniem
parliamentary i ostrzejszym filtrem szablonów miejscowości, bez porzucania
źródeł literackich i edukacyjnych.

## Artefakty

- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_prompts.jsonl`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_samples.md`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_samples.json`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_comparison.md`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_comparison.json`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_source_validation.md`
- `eval/glyph-100m/glyph100_v2_4_1_5k_eval_20260717_source_validation.json`

