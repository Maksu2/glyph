# Glyph: stan projektu, historia i następne kroki

Data audytu: 2026-09-05 UTC

## Podsumowanie techniczne

Glyph jest edukacyjno-badawczym projektem polskich modeli językowych typu decoder-only Transformer, trenowanych od zera. Projekt nie jest opakowaniem zewnętrznego LLM. Obejmuje własną architekturę PyTorch, tokenizer SentencePiece, pipeline przygotowania korpusów, pretraining, SFT, ewaluację, checkpointy, monitoring ROCm/CUDA, dashboard i narzędzia migracji do Colab/Kaggle.

Najważniejszy stan bieżący:

- ukończony milestone `Glyph-27M Base` istnieje jako `checkpoints/final.pt`, krok 200000;
- eksperymentalny `Glyph-27M SFT v0` istnieje jako `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt`, ale rygorystyczny eval pokazał, że nie jest niezawodnym asystentem;
- historycznie najlepszym checkpointem gałęzi `glyph100_v2_3_1` pozostaje 44k: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`;
- aktywna, nowsza gałąź bazowa to `glyph100_dataset_v2_4_2_core`, trenowana od zera do 15k; jej najnowszy checkpoint to `checkpoints/glyph-100m-v2_4_2-15k/latest.pt`;
- checkpoint 15k został poprawnie zapisany i ładuje się strict, lecz nie został jeszcze porównany jakościowo z 10k i 12.5k. Nie można więc uczciwie nazwać go najlepszym;
- żaden trening obecnie nie działa. Dalszy trening przed evalem nie jest zatwierdzony;
- Glyph-100M nadal jest bazowym modelem kontynuacji tekstu, nie gotowym chatbotem.

Najbliższa decyzja nie powinna dotyczyć kolejnych kroków treningu. Najpierw trzeba wykonać brakujący, identyczny metodologicznie eval checkpointów v2.4.2 10k, 12.5k i 15k oraz wybrać kanoniczny best checkpoint.

## Czym jest projekt i do czego służy

Projekt służy do praktycznego badania całego procesu budowy małego polskiego LLM:

1. przygotowania i filtrowania polskich korpusów;
2. trenowania modelu bazowego od losowej inicjalizacji;
3. badania wpływu pojemności modelu, source mixu i liczby kroków;
4. instruction tuningu na syntetycznych, ręcznie kontrolowanych przykładach;
5. porównywania checkpointów na stałych promptach, nie tylko przez loss;
6. uruchamiania tych samych eksperymentów na lokalnym ROCm i zewnętrznym CUDA;
7. dokumentowania awarii, regresji, kosztu obliczeń i ograniczeń jakościowych.

Nie ma podstaw, by przedstawiać Glyph jako model ogólnego przeznaczenia, źródło wiarygodnych faktów albo gotowego asystenta. W obecnej skali jego wartość jest przede wszystkim badawcza, edukacyjna i portfolio: pipeline naprawdę działa, ale jakość semantyczna pozostaje ograniczona.

## Architektura i wspólne elementy

Warianty definiuje `config.py`, a model implementuje `model/transformer.py`.

| Element | Glyph-27M | Glyph-100M |
|---|---:|---:|
| warstwy | 6 | 12 |
| wymiar embeddingu | 512 | 768 |
| głowy attention | 8 | 12 |
| FFN | 2048 | 3072 |
| context | 256 | 512 |
| vocab | 16000 | 16000 |
| dropout | 0.1 | 0.1 |
| unikalne/trenowalne parametry | 27,210,752 | 97,654,272 |
| parametry logiczne z liczonym tied head | 35,402,752 | 109,942,272 |
| embeddingi | 8,323,072 | 12,681,216 |
| bloki Transformera | 18,886,656 | 84,971,520 |

Źródłem dokładnych liczb jest `reports/glyph100_parameter_report.json`. Różnica między liczbą unikalną i logiczną wynika z powiązania wag token embeddingu z LM head. Implementacja używa pre-layernorm, GELU, fused QKV attention i weight tying. Generator obsługuje greedy, temperature, top-k, top-p, repetition penalty, no-repeat n-gram i token końca.

Wspólny tokenizer to `data/processed/tokenizer.model`, SentencePiece BPE 16k. Zweryfikowany SHA256:

`21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029`

## Co zrobiliśmy krok po kroku

### 1. Glyph-27M udowodnił pełny pipeline

Pretraining Glyph-27M zakończył się na kroku 200000. Checkpoint `checkpoints/final.pt` jest obecnie symlinkiem do zachowanej kopii na HDD. Z historycznego logu i watchdog state wynika końcowy loss 3.6068, około 11,579 tokenów/s i 1.6384 mld przetworzonych tokenów.

Ten model potwierdził, że działają: tokenizacja, binarny strumień danych, trening ROCm, checkpointy, resume, logi i generowanie. Nie potwierdził wysokiej jakości językowej.

### 2. Zrobiliśmy Glyph-27M SFT v0

Porównaliśmy dwa pliki po 1500 przykładów i wybraliśmy wariant expanded. Raport `data/sft/reports/sft_v0_token_stats.json` pokazuje 130,803 tokeny po templatingu, średnio 87.2 tokena, p95 102, maksimum 124. Wszystkie przykłady mieściły się w context 256; niczego nie skrócono ani nie odrzucono. Split wynosił 1350/150, stratified po kategorii z seedem 2026.

Format SFT został ustalony jako:

```text
<|user|>
{instruction}
<|assistant|>
{response}
<|end|>
```

Checkpoint `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt` ma krok 85, jedną epokę, train loss około 2.3539 i val loss około 2.0562. Dokumentacja znajduje się w `docs/sft-v0.md`.

Pierwszy eval był zbyt łagodny i dawał SFT 24 wygrane na 40. Eval v2 w `eval/sft-v0-v2/base_vs_sft_comparison_v2.json` dodał semantic relevance i task completion. Wynik zmienił się na 11 wygranych SFT, 5 base i 24 `both_bad`; 13 wcześniejszych słabych zwycięstw przestało być zwycięstwami. Wykryliśmy dryf w ogólne rady projektowe, schematyczne frazy i odpowiedzi poprawnie zakończone, ale semantycznie słabe. Glyph-27M został więc zamrożony jako proof-of-pipeline.

### 3. Dodaliśmy Glyph-100M i bezpieczny trening wielowariantowy

Dodaliśmy `glyph-100m` obok `glyph-27m`, bez zmiany starych checkpointów. `train.py` zapisuje wariant, model config, train config, batch, gradient accumulation, effective tokens, context, tokenizer path/hash, dataset i step. `validate_checkpoint_compatibility()` blokuje niezgodny wariant lub config modelu. Gradient accumulation jest realizowane przez dzielenie loss przez liczbę microstepów przed backward.

Dodaliśmy też:

- osobne logi i katalogi checkpointów dla etapów;
- twarde kontrole NaN/Inf i non-finite gradient norm;
- sampler możliwy do wznowienia;
- ewaluację i checkpointy liczone w optimizer steps;
- statusy publiczne bez pełnych prywatnych ścieżek.

### 4. Zweryfikowaliśmy Glyph-100M na RX 5500 XT

ROCm smoke w `reports/glyph100_rocm_smoke.json` potwierdził init, forward, backward, optimizer step i save/load przy context 512.

- batch 4: stabilny, około 3106 tokenów/s po warmupie, maksymalnie około 4466 MiB alokacji;
- batch 8: działał, około 3286 tokenów/s, ale zajmował około 98% VRAM i około 7346 MiB maksymalnej alokacji;
- batch 16: OOM;
- batch 4 + accum 8: stabilne 16,384 tokenów na optimizer step i około 3101 syntetycznych tokenów/s.

Dlatego długie lokalne runy używały konserwatywnego `batch_size=4`, `gradient_accumulation_steps=8`.

Kontener ROCm w `docker-compose.train.rocm.yml` nie używa `privileged` ani docker.sock. Ma tylko urządzenia `/dev/kfd` i `/dev/dri`, read-only root, `cap_drop: ALL` i `no-new-privileges`. Obraz `Dockerfile.train.rocm-gfx1012` opiera się jednak na konkretnej nightly PyTorch/ROCm dla gfx1012, co pozostaje ryzykiem utrzymaniowym.

### 5. Pierwszy korpus 100M wystarczył do sanity, nie do długiego treningu

Pierwszy `glyph100_stage1_candidate` miał około 117.87 mln train tokenów. Run do 10k zużył 163.84 mln tokenów, czyli około 1.39 przejścia przez korpus. `reports/glyph100_stage2_report.json` dokumentuje około 12 h 27 min, średnio 3293.5 tokenów/s i spadek val loss do około 3.3527. Przy wznawianiu wystąpił NaN w okolicy kroku 1002; run odzyskano po wyłączeniu AdamW foreach i wymuszeniu bezpiecznej ścieżki SDPA.

Wynik był technicznie zdrowy, lecz generacje nadal miały dużo powtórzeń i webowego stylu. Zdecydowaliśmy nie mnożyć epok na tym korpusie.

### 6. Iteracyjnie przebudowaliśmy dane v2 do v2.3.1

Kolejne wersje rozwiązywały inne problemy:

- v2: source-aware organizacyjnie, ale `legacy_mixed_corpus` wnosił forum, commerce i SEO residue;
- v2.1: około 134.2 mln tokenów, legacy 0%, lecz około 95.3% Wikipedii;
- v2.2: około 37.0 mln tokenów, Wikipedia ograniczona, ale 50k oznaczałoby około 22 epoki;
- FinetextPL-Edu: raport wykazał gated access i około 263.7 GB danych; nie uzyskaliśmy próbki. Z rozmowy wynika, że dostęp pozostał pending. Aktualnego stanu konta nie da się ustalić z dysku;
- v2.3: około 300 mln tokenów dzięki FineWeb2 PL, lecz próbki ujawniły sklepy, usługi, cookies, fora i SEO;
- v2.3.1: ostrzejsze filtry domen i treści zmniejszyły zbiór do około 175.9 mln tokenów; Wikipedia stanowiła około 72.7%, FineWeb2 około 21.0%. Jakość była lepsza, ale różnorodność nadal ograniczona.

### 7. Trening v2.3.1 doszedł kontrolowanie do 50k

Seria punktów kontrolnych 15k, 25k, 35k, 45k i diagnostyczne 50k pozwoliła oddzielić spadek loss od jakości generacji. Broad eval i seed sensitivity wybrały krok 44k, nie latest 50k.

`reports/glyph100_v2_3_1_final_decision.json` podaje:

- średni score: 44k = 6.198, 45k = 5.721, 50k = 5.644;
- 50k vs 44k: 126 wygranych 50k, 160 wygranych 44k, 194 remisy;
- seed sensitivity: średnia 44k = 8.37, 50k = 7.55;
- 50k było technicznie zdrowe, ale val loss rósł i jakość nie przebiła 44k.

Best practical checkpoint tej historycznej gałęzi pozostał:

`checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`

### 8. Znaleźliśmy i naprawiliśmy krytyczny błąd SFT label mask

Pierwszy Glyph-100M SFT smoke był niewiarygodny jakościowo. W `SFTDataset._make_pair()` maskowanie używało `i <= assistant_pos`, przez co pierwszy token odpowiedzi nie był supervised. Zmieniliśmy granicę na `i < assistant_pos` w `finetune.py`.

`reports/glyph100_sft_label_mask_fix_audit.json` potwierdza:

- pierwszy token `Loss`, `Nie` i `Projekt` jest supervised;
- `<|end|>` jest supervised;
- prompt jest zamaskowany;
- padding ma `-100`;
- żaden przykład nie pozostaje bez labeli odpowiedzi;
- poprawka dodała dokładnie 1500 brakujących supervised tokenów w 1500 przykładach.

CPU tiny overfit na 64 przykładach i 300 krokach zszedł z loss 4.1270 do 0.0014 i wygrał 32/32 porównań. Następnie bezpieczne ROCm FP32 przeszło 50 i 200 kroków bez NaN/OOM/crash. To wykazało, że poprawiony pipeline potrafi mechanicznie nauczyć model formatu.

### 9. SFT v0.1 i v0.2 poprawiły format, v0.3 nie poprawił znaczenia

Corrected SFT v0.1 był stabilny, ale miał 20/50 powtarzających się odpowiedzi. v0.2 zwiększył dataset do 2176 przykładów i przy `no_repeat_ngram_size=3` osiągnął średni score 5.38, repetition 1/150, `<|end|>` 100% i 142/150 naturalnych zakończeń. Nadal występowały cztery realne przypadki web residue i błędy semantyczne.

Dataset v0.3 miał 2753 przykłady i był zbudowany pod semantykę, różne początki, anty-web i anty-powtórzenia. Trening był stabilny: loss 4.813 do 1.404, best val loss 1.080 przy kroku 450. Mimo tego najlepszy eval miał średnią 4.785, repetition 4, real web residue 5, a v0.2 wygrał z v0.3 29 do 20 przy 151 remisach. Ręczna kontrola znalazła nonsensowne definicje GPU, kilometra i pojęć treningowych.

`reports/glyph100_sft_v0_3_next_decision.json` ma werdykt C: v0.3 nie poprawia v0.2, nie kontynuować SFT w tym kierunku. Nie powstał SFT v1.

### 10. Przygotowaliśmy migrację CUDA i sprawdziliśmy Kaggle P100

Powstały:

- `colab/Glyph_Colab.ipynb`;
- `scripts/pack_glyph_colab_bundle.py`;
- `scripts/verify_glyph_colab_bundle.py`;
- `scripts/colab_preflight.py`;
- `scripts/colab_run_sft.py`;
- `scripts/colab_export_results.py`;
- `docs/COLAB_MIGRATION.md`;
- zweryfikowana paczka `dist/glyph-colab-upload-ready-20260802T005327Z.zip` około 346 MiB.

Notebook domyślnie nie trenuje. Bundle zawiera odchudzony base 44k, tokenizer, wybrany dataset i kod, bez 50k i bez sekretów.

Na Kaggle P100 zgodność wymagała PyTorch CUDA 12.6, ponieważ użyta początkowo kompilacja cu128 nie obsługiwała sm_60. Po poprawce P100 przeszedł smoke i run v2.4.2 5k do 10k. Raport `reports/glyph100_v2_4_2_p100_10k_20260808.json` podaje około 9643.7 tokenów/s, 2.95 razy szybkość RX 5500 XT, około 4097 MiB VRAM i maksymalnie 59 C, bez NaN/OOM/crash.

### 11. Posprzątaliśmy i przenieśliśmy historię na HDD

Najpierw usunięto 122 redundantne checkpointy, odzyskując około 130.65 GB, po zachowaniu manifestu i kluczowych punktów. Późniejszy cleanup `reports/glyph_hdd_cleanup_20260831.json` odzyskał około 176.58 GiB przez ograniczenie starych checkpointów, usunięcie nagrań Bambu i Gemma oraz kompresję nieaktywnego korpusu. Nie usunięto aktywnych checkpointów.

Obecnie repo zajmuje około 36 GB, w tym około 26 GB checkpointów, 5 GB `.venv`, 2.1 GB materiałów Kaggle i 1.8 GB `data`. HDD `/mnt/data` ma około 1.4 TB wolnego. Zimne checkpointy Glyph-27M są dostępne przez symlinki.

### 12. Zbudowaliśmy czystsze gałęzie v2.4.1 i v2.4.2

v2.4.1 był świeżym treningiem na bardziej source-aware korpusie, ale analiza ujawniła niepożądane locality/urzędowe wzorce i nierówny styl. v2.4.2 skorygował mix i filtry, po czym przeszedł świeży proxy 0 do 5k, kontynuację 5k do 10k na P100 i 10k do 15k lokalnie na RX 5500 XT.

Aktualny dataset `glyph100_dataset_v2_4_2_core` ma:

- 159,579 dokumentów;
- 232,671,067 tokenów łącznie;
- 231,494,339 train i 1,176,728 val;
- token/word ratio 1.9382;
- około 40.83% Wikipedii;
- około 54.39% literatury;
- około 2.58% tekstów parlamentarnych;
- 0 wykrytych exact/normalized duplicates, parent leakage, residual web docs i residual locality docs według zapisanych gate'ów.

Źródła zapisane w `data/reports/glyph100_dataset_v2_4_2_stats.json` to: 1000 Novels, ELTeC PL, materiały parlamentarne, Wikibooks, Wikinews, Wikipedia PL, Wikisource i Wolne Lektury. Istotne ograniczenie: Wikisource ma 27,607,311 tokenów wyłącznie w train i 0 w val, więc jego zachowanie nie jest mierzone osobnym val splitem.

## Stan bieżący: co działa

### Aktywna gałąź v2.4.2

`reports/glyph100_status.json` oraz publiczny dashboard wskazują poprawnie:

- start z 10k i ukończenie 15k 2026-09-01;
- final train loss 4.0940;
- final val loss 3.9755;
- około 3276 tokenów/s;
- 245.76 mln efektywnie przetworzonych tokenów, czyli około 1.062 przejścia przez train corpus;
- exit code 0;
- brak aktywnego procesu treningowego.

Checkpoint `checkpoints/glyph-100m-v2_4_2-15k/latest.pt` ma krok 15000, wariant `glyph-100m`, context 512, właściwy tokenizer SHA, batch 4, accum 8, effective 16,384 tokenów na krok oraz stany optimizer, scheduler i data sampler. Model state ładuje się strict i ma 97,654,272 skończonych numerycznie parametrów.

W logu walidacja osiągnęła minimum 3.9538 przy 11k, następnie wzrosła, kończąc na 3.9755 przy 15k. To nadal lepiej interpretować jako plateau lub lekki sygnał pogorszenia niż jako dowód overfitu. Bez matched evala nie wiadomo, czy generacje 15k są lepsze od 10k.

### Pipeline i infrastruktura

Działają:

- warianty 27M/100M i strict shape loading;
- tokenizer o stabilnym checksumie;
- source-aware preprocessing i dokumentowy split;
- lokalny ROCm z monitoringiem temperatury i bezpiecznym batch 4/accum 8;
- CUDA/Kaggle P100 i odtwarzalny bundle Colab;
- checkpoint resume z optimizer/scheduler/data state;
- publiczny dashboard `trening.maksu.online` dla bieżącej gałęzi;
- lokalna strona raportów `http://192.168.100.105:8101/`;
- testy standard-library: 12/12 przeszło 2026-09-05 przez `python -m unittest discover -s tests -v`.

## Stan bieżący: co jest niedokończone lub problematyczne

### BLOCKER decyzyjny: brak evala po 15k

Nie istnieje końcowy raport ani matched eval v2.4.2 10k vs 12.5k vs 15k. Istnieje tylko launch report, log, checkpoint i status `eval pending`. Dalszy trening byłby ponownie treningiem w ciemno.

Ostatni ukończony eval 10k wskazuje, że model jest technicznie zdrowy, ale semantycznie słaby: średni score 3.2, naturalne zakończenia 9/40, cutoff-like 34/40, repetition 17/40, błędne fakty oraz zmyślone daty i terminy. Nie ma dowodu, że 15k naprawiło te problemy.

### Nie ma kanonicznego best checkpointu dla v2.4.2

15k jest `latest`, nie `best`. Historyczny marker best dotyczy wyłącznie v2.3.1 44k. Nie należy mieszać tych gałęzi ani porównywać ich po surowym val loss, ponieważ używają innych datasetów i walidacji.

### Resume safety jest niepełne w głównym `train.py`

`validate_checkpoint_compatibility()` sprawdza wariant i model config, ale główny resume path nie wymusza zgodności nazwy datasetu ani tokenizer SHA. Dotychczas kontrolowały to wrappery i preflighty. Bez takiej walidacji człowiek może świadomie lub przypadkowo wznowić na innym zbiorze bez twardej blokady.

### Save checkpointu nie jest wszędzie równie odporny

`latest.pt` używa pliku tymczasowego i rename, ale zwykły step checkpoint w podstawowym `train.py` nie ma pełnego atomic write plus reload verification znanego ze skryptów Colab. To nie spowodowało utraty aktualnego checkpointu, ale jest technicznym długiem.

### Pipeline SFT jest rozfragmentowany

Podstawowy `finetune.py` ma poprawną maskę i ignore index, lecz nie ma tego samego pełnego gradient accumulation i bezpiecznego telemetrycznego flow co `scripts/glyph100_sft_rocm_safe_tiny.py` oraz `scripts/colab_run_sft.py`. Wyniki SFT są ważne badawczo, ale przed kolejnym SFT warto skonsolidować jedną referencyjną ścieżkę.

### Dataset ma lepszą higienę, ale nadal ma bias i lukę walidacyjną

Ponad połowa tokenów v2.4.2 pochodzi z literatury, więc możliwy jest archaiczny lub narracyjny bias. Wikisource nie ma reprezentacji w val. Automatyczne gate'y potwierdzają brak konkretnych wykrywanych śmieci, ale nie dowodzą pełnej poprawności faktów ani naturalności współczesnej polszczyzny.

### SFT poprawiał formę szybciej niż znaczenie

Naprawiony pipeline działa mechanicznie. v0.2 jest najlepszym z małych eksperymentów SFT, lecz v0.3, mimo lepszego datasetu i niższego val loss, pogorszył ręcznie ocenianą semantykę. Nie ma obecnie podstaw do SFT v1.

### Dokumentacja i strony są niespójne

- `README.md` nadal opisuje Glyph-100M jako wariant dopiero przygotowywany i zawiera stare ścieżki/statusy 27M;
- `glyph.maksu.online/data/training.json` pokazuje aktualne 15k, ale `glyph.maksu.online/data/model.json` i `site/content/pl.json`/`en.json` nadal opisują v2.3.1 44k/50k jako stan główny;
- publiczne demo faktycznie działa na `Glyph-27M`, a lokalny health endpoint zgłasza ten model;
- `checkpoints/public-demo.pt` jest checkpointem 27M z kroku 115000, a nie finalnym 200000, SFT ani Glyph-100M. Z dostępnych plików nie da się jednoznacznie ustalić, dlaczego wybrano akurat 115k;
- publiczny opis mówi miejscami, że Glyph-100M nie ma SFT, mimo że wykonano eksperymenty smoke v0.1-v0.3. Powinny być opisane jako nieudane/nieprodukcyjne eksperymenty, nie jako gotowa wersja.

### Brakuje części narzędziowej higieny

Repo nie jest obecnie repozytorium Git, więc nie ma audytowalnej historii commitów ani commit ID w bundle. `pytest` nie jest zainstalowany w lokalnym `.venv`; testy unittest przechodzą. Aktualnego limitu Kaggle/Colab i aktualnego statusu dostępu FinetextPL-Edu nie da się ustalić z lokalnych plików.

## Co realnie jest dziś „modelem Glyph”

To określenie odnosi się obecnie do kilku różnych artefaktów i trzeba je rozdzielać:

| Rola | Artefakt | Status |
|---|---|---|
| ukończony proof-of-pipeline | `checkpoints/final.pt` | Glyph-27M Base, 200k |
| eksperymentalny instruct 27M | `checkpoints/sft-v0/glyph-27m-sft-v0-final.pt` | działa technicznie, słaby jakościowo |
| historyczny best gałęzi v2.3.1 | `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt` | wybrany broad evalem |
| aktywny latest gałęzi v2.4.2 | `checkpoints/glyph-100m-v2_4_2-15k/latest.pt` | poprawny technicznie, eval pending |
| najlepszy mały SFT smoke | checkpoint best v0.2 | eksperyment, nie model do publikacji |
| model publicznego demo | `checkpoints/public-demo.pt` | Glyph-27M Base step 115k |

Jeżeli pytanie brzmi „na czym dziś stoi rozwój”, odpowiedź brzmi: na czystszym korpusie v2.4.2 i checkpointcie bazowym 15k, który czeka na eval. Jeżeli pytanie brzmi „jaki checkpoint 100M został już udowodniony jako najlepszy”, odpowiedź brzmi: tylko historyczny v2.3.1 44k w obrębie tamtej gałęzi. Nie wiadomo jeszcze, czy v2.4.2 10k, 12.5k lub 15k jest lepszy od niego.

## Konkretne następne kroki

### P0. Domknąć v2.4.2 bez dalszego treningu

1. Wygenerować post-run report 10k do 15k z logu, GPU telemetry i walidacji checkpointów.
2. Uruchomić matched eval checkpointów:
   - `checkpoints/glyph-100m-v2_4_2-10k/step_0010000.pt`;
   - `checkpoints/glyph-100m-v2_4_2-15k/step_0012500.pt`;
   - `checkpoints/glyph-100m-v2_4_2-15k/step_0015000.pt`.
3. Użyć tych samych promptów, presetów, seedów i limitów dla wszystkich checkpointów; oceniać base LM continuation, nie assistant behavior.
4. Raportować co najmniej: polską składnię, topic adherence, repetition, cutoff, natural ending, pseudo-ency, web residue i podstawowe błędy faktograficzne.
5. Dodać source-specific validation. Wprost oznaczyć, że Wikisource nie ma własnego val splitu.
6. Dopiero wtedy porównać zwycięzcę v2.4.2 z v2.3.1 44k na identycznym eval set. Nie porównywać samych val loss między datasetami.
7. Utworzyć kanoniczny manifest best checkpointu v2.4.2 albo jawnie zachować v2.3.1 44k jako najlepszy jakościowo.

### P1. Podjąć decyzję o treningu dopiero po P0

Jeżeli 15k nie wygra, zatrzymać aktywną gałąź na 10k lub 12.5k. Jeżeli 15k wygra wyraźnie mimo lekkiego wzrostu val loss, rozważyć osobno zatwierdzony, krótki punkt kontrolny do 20k. Nie kontynuować automatycznie z obecnym prawie niezmienionym LR około 1.98e-4; najpierw sprawdzić scheduler i uzasadnić nowy przebieg LR.

### P2. Utwardzić kod przed kolejnym runem

1. Dodać do głównego resume hard fail dla tokenizer SHA i dataset identity, z jawną flagą dla świadomej zmiany etapu.
2. Zapisywać każdy checkpoint atomowo, fsync, ponownie ładować i dopiero wtedy aktualizować `latest.pt`.
3. Skonsolidować bezpieczny SFT runner: fixed mask, gradient accumulation, FP32/AMP modes, save-best, telemetry, NaN stop i identyczny template evala w jednym utrzymywanym path.
4. Dodać `pytest` do developerskich zależności albo jawnie standaryzować `unittest`.
5. Przywrócić Git lub inny jednoznaczny mechanizm wersjonowania kodu eksperymentów.

### P3. Naprawić obserwowalność i opis publiczny

1. Ujednolicić `README.md`, `site/content/pl.json`, `site/content/en.json`, `data/model.json` i `data/training.json` wokół rzeczywistego stanu v2.4.2 15k/eval pending.
2. Jasno oznaczyć demo jako archiwalne Glyph-27M step 115k albo po osobnej decyzji je wyłączyć/zmienić. Nie sugerować, że serwuje 100M.
3. Po evalie pokazywać osobno `latest checkpoint`, `best checkpoint` i `best branch`, aby latest nigdy nie wyglądał automatycznie jak best.

### P4. Dane i przyszły SFT

1. Nie budować kolejnej ogromnej wersji korpusu przed zrozumieniem evala 15k.
2. Uzupełnić val dla Wikisource albo jawnie wyłączyć to źródło z twierdzeń o pełnej walidacji.
3. Audytować bias literacki i dodać nowoczesny, czysty polski tekst tylko przez mały probe i ręczne próbki.
4. FinetextPL-Edu rozważać dopiero po realnym przyznaniu dostępu i ograniczonym streamowanym probe; nie pobierać około 263.7 GB w ciemno.
5. Nie uruchamiać SFT v1. Jeżeli wrócimy do SFT po wyborze nowego base, użyć v0.2 tylko jako punktu odniesienia i zbudować ręcznie sprawdzony semantycznie dataset z zewnętrznym held-out evalem. v0.3 nie powinien być skalowany.

### P5. Zasoby

Kaggle P100 jest sensownym akceleratorem dla krótkich, zatwierdzonych runów, gdy przydział jest dostępny; lokalny RX 5500 XT pozostaje wolniejszym, ale działającym fallbackiem. Po wyborze best checkpointu można ponownie przejrzeć około 26 GB lokalnych checkpointów, lecz usuwanie powinno nastąpić dopiero po checksumach, manifeście i osobnej zgodzie.

## Fakty, których obecnie nie da się ustalić

- Czy v2.4.2 15k generuje lepiej niż 10k/12.5k: eval nie został wykonany.
- Czy v2.4.2 pokonuje historyczny v2.3.1 44k: brak matched cross-branch evala.
- Dlaczego publiczne demo wskazuje checkpoint 27M step 115k zamiast final 200k/SFT: brak jednoznacznego dokumentu decyzji.
- Czy dostęp do FinetextPL-Edu został ostatecznie przyznany: lokalne raporty kończą się na gated/pending.
- Jaki jest aktualny darmowy przydział GPU Kaggle/Colab: nie wynika z repo.
- Jaki commit dokładnie odpowiada checkpointom: katalog nie jest repozytorium Git.

## Źródła lokalne i walidacja tego podsumowania

Najważniejsze pliki dowodowe:

- `config.py`
- `model/transformer.py`
- `train.py`
- `finetune.py`
- `reports/glyph100_parameter_report.json`
- `reports/glyph100_status.json`
- `logs/glyph-100m-v2_4_2-15k/train.log`
- `reports/glyph100_v2_4_2_post_10k_decision_20260808.json`
- `data/reports/glyph100_dataset_v2_4_2_stats.json`
- `reports/glyph100_v2_3_1_final_decision.json`
- `reports/glyph100_sft_label_mask_fix_audit.json`
- `reports/glyph100_sft_v0_3_next_decision.json`
- `reports/glyph100_v2_4_2_p100_10k_20260808.json`
- `reports/glyph_hdd_cleanup_20260831.json`
- `docs/COLAB_MIGRATION.md`

Kontrola wykonana 2026-09-05:

- brak aktywnego `train.py`, `finetune.py` i `colab_run_sft.py`;
- działają kontenery raportów i CPU inference;
- tokenizer SHA zgodny;
- checkpoint 15k zweryfikowany wcześniej w tym audycie przez strict load i kontrolę finite parametrów;
- `python -m unittest discover -s tests -v`: 12/12 PASS;
- `pytest` nie został uruchomiony, ponieważ nie jest zainstalowany w `.venv`;
- `trening.maksu.online/api/stats` i publiczny snapshot training pokazują 15k complete/eval pending;
- publiczna warstwa Glyph ma niespójny model description względem training snapshotu.

## Werdykt

Glyph jest działającym, dobrze udokumentowanym eksperymentem end-to-end, a nie porzuconym szkicem. Największym sukcesem jest sprawny pipeline od surowych źródeł po trening na ROCm/CUDA, checkpoint resume, eval i publikację statusów. Największym nierozwiązanym problemem jest jakość semantyczna: loss i format poprawiają się szybciej niż prawdziwa użyteczność odpowiedzi.

Stan projektu nie uzasadnia dziś ani dalszego pretrainingu, ani SFT v1. Uzasadnia natomiast jeden konkretny kolejny pakiet pracy: matched eval v2.4.2 10k/12.5k/15k, wybór best checkpointu i dopiero potem decyzję, czy inwestować w 20k, nowy korpus, czy zamrozić model jako ukończony milestone badawczy.
