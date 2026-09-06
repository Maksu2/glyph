# Glyph-100M SFT v0.1 error analysis

## Summary

- source eval: `eval/glyph-100m/sft_smoke_v0_1_fixedmask_before_after.json`
- examples: 50
- winners: `{'tie': 14, 'sft': 34, 'base': 2}`
- SFT avg score: 4.22
- repetition samples: 20/50
- repetition by kind: `{'target_instruction': 8, 'diagnostic_instruction': 4, 'continuation': 8}`
- repetition by category: `{'brak_danych': 3, 'ostrozne_odpowiedzi_przy_niepewnosci': 1, 'naturalne_zakonczenia': 1, 'proste_techniczne_wyjasnienia': 1, 'mini_streszczenia': 1, 'mvp_first_project_advice': 1, 'technical': 1, 'missing_data': 2, 'uncertainty': 1, 'base_lm_sanity': 8}`
- repetition type: `{'single_word': 9, 'sentence_fragment': 4, 'phrase': 5, 'drift_or_light_repeat': 2}`
- avg words with repetition: 37.9
- instruction repetition end-token distribution: `{False: 7, True: 5}`

## Interpretation

- Repetition is concentrated in instruction-like rows, especially held-out target examples and missing-data/project/technical patterns.
- Missing `<|end|>` correlates with the worst loops: the highest-repetition rows usually do not terminate with `<|end|>`.
- Repetition is often single-word or short-phrase looping, not subtle style drift.
- v0.2 should add explicit anti-repetition/end-token examples and reduce repeated answer openings.

## 10 Worst Repetition Cases

### 1. target_instruction / brak_danych / glyph100-sft-smoke-v0-1407

- repetition ngrams: 57
- type: single_word
- ended by `<|end|>`: False
- prompt: Czy ten komputer wystarczy? Jak odpowiedzieć bez danych?

Nie. Bez danych nie da się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego

### 2. continuation / base_lm_sanity / cont-06

- repetition ngrams: 48
- type: phrase
- ended by `<|end|>`: None
- prompt: Na początku eksperymentu

ję z różnymi technikami, które pozwalają na lepszą poprawę jakości danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość

### 3. continuation / base_lm_sanity / cont-02

- repetition ngrams: 38
- type: single_word
- ended by `<|end|>`: None
- prompt: W fizyce energia

jest stabilna, ale nie zależy od modelu. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabil

### 4. continuation / base_lm_sanity / cont-05

- repetition ngrams: 38
- type: phrase
- ended by `<|end|>`: None
- prompt: Dobry raport techniczny

, który pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny

### 5. target_instruction / mvp_first_project_advice / glyph100-sft-smoke-v0-0468

- repetition ngrams: 37
- type: single_word
- ended by `<|end|>`: False
- prompt: Krótko doradź: Czy dodać animacje?

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.

### 6. diagnostic_instruction / missing_data / diag-missing-laptop

- repetition ngrams: 37
- type: single_word
- ended by `<|end|>`: False
- prompt: Czy ten laptop jest dobry?

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.

### 7. continuation / base_lm_sanity / cont-08

- repetition ngrams: 36
- type: single_word
- ended by `<|end|>`: None
- prompt: Walidacja pokazuje

, czy model uczy się przewidywać dane treningowe. Trening może być prosty, ale nie krótki. Trening może być prosty, ale prosty. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki

### 8. continuation / base_lm_sanity / cont-04

- repetition ngrams: 34
- type: phrase
- ended by `<|end|>`: None
- prompt: Najważniejszym problemem tego projektu jest

wybór konkretnego projektu, który może być przydatny przy tworzeniu nowych projektów. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko

### 9. diagnostic_instruction / missing_data / diag-missing-buy

- repetition ngrams: 33
- type: single_word
- ended by `<|end|>`: False
- prompt: Czy powinienem to kupić?

Nie. Brakuje informacji o produkcie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie

### 10. target_instruction / brak_danych / glyph100-sft-smoke-v0-0862

- repetition ngrams: 31
- type: single_word
- ended by `<|end|>`: False
- prompt: Czy wynik benchmarku jest dobry? Nie zgaduj.

Nie. Benchmark jest ważny, ale nie jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Ben

## 10 Best SFT Answers

### 1. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-1451

- score: 10
- winner: sft

Proszę o informację zwrotną w sprawie.

### 2. target_instruction / anty_petle / glyph100-sft-smoke-v0-1022

- score: 9
- winner: sft

Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się.

### 3. target_instruction / anty_petle / glyph100-sft-smoke-v0-1241

- score: 9
- winner: sft

Bez danych nie da się rzetelnie ocenić jakości.

### 4. diagnostic_instruction / definition / diag-definition-backup

- score: 9
- winner: sft

Backup to kopia danych potrzebna do odtworzenia ich po awarii.

### 5. diagnostic_instruction / rewrite / diag-rewrite-project

- score: 9
- winner: sft

Ten projekt jest ważny, gdy nie da się tego ocenić bez używania kryteria.

### 6. diagnostic_instruction / summary / diag-summary-scope

- score: 9
- winner: sft

Duże projekty często upadają poza zakres.

### 7. diagnostic_instruction / project / diag-project-ui

- score: 9
- winner: sft

Najpierw sprawdź, czy model działa poprawnie.

### 8. diagnostic_instruction / anti_loop / diag-anti-loop

- score: 9
- winner: sft

Krótka myśl powinna zawierać jedną myśl i zakończyć się.

### 9. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0239

- score: 8
- winner: sft

Uważam, że problem jest ważny.

### 10. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0143

- score: 8
- winner: sft

Trzeba wskazać, jakich błędów brakuje, i nie zgadywać wyniku.

## 10 Clear SFT Wins

### 1. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-1451

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

SFT:

Proszę o informację zwrotną w sprawie.

### 2. target_instruction / anty_petle / glyph100-sft-smoke-v0-1241

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych? Bez metafor.

Base:

Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __

SFT:

Bez danych nie da się rzetelnie ocenić jakości.

### 3. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0239

Prompt: Popraw tekst: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Base:

Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sen

SFT:

Uważam, że problem jest ważny.

### 4. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0143

Prompt: Skróć i popraw: Należy zwrócić uwagę na możliwość wystąpienia błędów.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

SFT:

Trzeba wskazać, jakich błędów brakuje, i nie zgadywać wyniku.

### 5. target_instruction / brak_danych / glyph100-sft-smoke-v0-0773

Prompt: Czy moja odpowiedź jest dobra? Nie zgaduj.

Base:

Czy mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję,

SFT:

Nie. Nie. Nie. Lepsza jest krótka, konkretna odpowiedź niż długi tekst bez treści.

### 6. target_instruction / krotkie_definicje / glyph100-sft-smoke-v0-0255

Prompt: Wyjaśnij krótko pojęcie: inferencja.

Base:

Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferen

SFT:

Inferencja to zapis stanu modelu, modelu i stanu modelu.

### 7. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-1147

Prompt: Czym jest smoke test?

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

SFT:

Smoke test to krótka teoria, którą można sprawdzić po sprawdzeniu, czy model działa poprawnie.

### 8. target_instruction / anty_petle / glyph100-sft-smoke-v0-0065

Prompt: Zakończ po jednej myśli: po co robi się testy? Tylko sedno.

Base:

Zakończ po drugiej stronie, aby dowiedzieć się, jak wygląda testowanie i jak wygląda testowanie i jak wygląda testowanie i jak wygląda testowanie. __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

SFT:

Testy pomagają wykryć błędy i sprawdzić, czy model działa poprawnie.

### 9. target_instruction / krotkie_definicje / glyph100-sft-smoke-v0-0529

Prompt: Czym jest prompt?

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

SFT:

Prompt to zapis stanu modelu, który można uruchomić dopiero po uruchomieniu programu.

### 10. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-0058

Prompt: W jednym akapicie: Czym jest fallback CPU?

Base:

W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback

SFT:

Fallback CPU to fallback CPU, ale nie fallback CPU.

## Base Wins

### 1. diagnostic_instruction / technical / diag-technical-cpu-load

Prompt: Czym różni się CPU usage od load average?

Base:

Czym różni się CPU usage? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

SFT:

CPU usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage

### 2. diagnostic_instruction / missing_data / diag-missing-laptop

Prompt: Czy ten laptop jest dobry?

Base:

Czy laptop jest dobry? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

SFT:

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.
