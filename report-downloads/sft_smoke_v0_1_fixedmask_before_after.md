# Glyph-100M corrected SFT smoke v0.1 before/after eval

## Summary

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- SFT checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm/glyph-100m-v2_3_1-44k-sft-smoke-v0_1-fixedmask-rocm-latest.pt`
- examples: 50 (32 held-out target, 10 diagnostic, 8 continuation)
- decoding: `greedy temperature=0.0 top_k=None top_p=1.0`
- prompt template: `<|user|>\n{prompt}\n<|assistant|>\n`
- base avg score: -0.94
- SFT avg score: 4.22
- winners: `{'tie': 14, 'sft': 34, 'base': 2}`
- SFT first-token correct on target examples: 17/32
- SFT ended by `<|end|>` on instruction examples: 35/42
- SFT natural endings: 37/50
- SFT repetition samples: 20
- SFT pseudo-ency samples: 0
- SFT web residue samples: 0
- SFT generic assistant template samples: 0
- SFT prompt overlap samples: 0
- exact target matches on held-out val: 0

## Samples

### 01. target_instruction / brak_danych / glyph100-sft-smoke-v0-0862

Prompt: Czy wynik benchmarku jest dobry? Nie zgaduj.

Target: Trzeba znać sprzęt, ustawienia testu i punkt odniesienia. Sama liczba nie wystarcza.

Base:

Czy wynik jest dobry? __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 41, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 34, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Benchmark jest ważny, ale nie jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Benchmark jest ważny. Ben

SFT score: `{'words': 42, 'target_words': 12, 'target_overlap': 0.08333333333333333, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 31, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`
Winner: `tie`

### 02. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0239

Prompt: Popraw tekst: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.

Target: Uważam, że ten problem trzeba szybko rozwiązać.

Base:

Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sensu. __ Popraw tekst: W tym przypadku, jeśli chodzi o tekst, to nie ma sen

Base score: `{'words': 55, 'target_words': 7, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 38, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Uważam, że problem jest ważny.

SFT score: `{'words': 5, 'target_words': 7, 'target_overlap': 0.42857142857142855, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 8}`
Winner: `sft`

### 03. target_instruction / codzienne_proste_pytania / glyph100-sft-smoke-v0-0240

Prompt: Jak poprosić o feedback?

Target: Pokaż konkretny fragment i zapytaj o jedną rzecz, którą chcesz poprawić.

Base:

Jak poprosić o feedback? ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 4, 'target_words': 11, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': True, 'exact_target_match': False, 'score': -1}`

SFT v0.1:

Zacznij od celu, wyniku i wyniku.

SFT score: `{'words': 6, 'target_words': 11, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 04. target_instruction / mini_streszczenia / glyph100-sft-smoke-v0-0270

Prompt: Skróć tekst: Jeśli model powtarza frazy z datasetu, trzeba poprawić dane, a nie tylko zmienić temperaturę.

Target: Powtarzalny styl często wymaga poprawy danych.

Base:

__>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 1, 'target_words': 6, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`

SFT v0.1:

Najpierw trzeba sprawdzić, czy model działa poprawnie.

SFT score: `{'words': 7, 'target_words': 6, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 05. target_instruction / anty_petle / glyph100-sft-smoke-v0-0065

Prompt: Zakończ po jednej myśli: po co robi się testy? Tylko sedno.

Target: Testy pomagają wykrywać błędy i upewnić się, że zmiany nie psują działania.

Base:

Zakończ po drugiej stronie, aby dowiedzieć się, jak wygląda testowanie i jak wygląda testowanie i jak wygląda testowanie i jak wygląda testowanie. __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 23, 'target_words': 12, 'target_overlap': 0.16666666666666666, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 9, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Testy pomagają wykryć błędy i sprawdzić, czy model działa poprawnie.

SFT score: `{'words': 10, 'target_words': 12, 'target_overlap': 0.3333333333333333, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 7}`
Winner: `sft`

### 06. target_instruction / naturalne_zakonczenia / glyph100-sft-smoke-v0-0034

Prompt: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj. Zakończ po sensownej myśli.

Target: Dzień dobry, nie zdążę dziś oddać pracy. Czy mogę dosłać ją jutro?

Base:

Napisz wiadomość do nauczyciela, który w tym roku został nauczycielem. __ Napisz wiadomość do nauczyciela, który w tym roku został nauczycielem. __ Napisz wiadomość do nauczyciela, który w tym roku został nauczycielem. __ Napisz wiadomość do nauczyciela, który w tym roku został nauczycielem. __ Napisz wiadomość do nauczyciela, który w tym roku został nauczycielem. __

Base score: `{'words': 55, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 42, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Krótka odpowiedź powinna zawierać tekst, który uczy się przewidywać dalsze losy.

SFT score: `{'words': 11, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 07. target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / glyph100-sft-smoke-v0-0783

Prompt: Czy krótsze odpowiedzi zawsze są lepsze? Krótko.

Target: Nie. Są lepsze wtedy, gdy odpowiadają na pytanie bez utraty potrzebnych informacji.

Base:

Czy warto? __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 35, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Lepsza jest krótka, ale krótka, ale krótka, ale krótka i krótka. Lepsza jest krótka, ale krótka.

SFT score: `{'words': 17, 'target_words': 12, 'target_overlap': 0.08333333333333333, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 6, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 08. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-0143

Prompt: Skróć i popraw: Należy zwrócić uwagę na możliwość wystąpienia błędów.

Target: Trzeba uwzględnić ryzyko błędów.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 4, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Trzeba wskazać, jakich błędów brakuje, i nie zgadywać wyniku.

SFT score: `{'words': 9, 'target_words': 4, 'target_overlap': 0.5, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 8}`
Winner: `sft`

### 09. target_instruction / brak_danych / glyph100-sft-smoke-v0-0773

Prompt: Czy moja odpowiedź jest dobra? Nie zgaduj.

Target: Nie da się ocenić bez treści odpowiedzi i kryteriów oceny.

Base:

Czy mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję,

Base score: `{'words': 60, 'target_words': 10, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 54, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': True, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -4}`

SFT v0.1:

Nie. Nie. Nie. Lepsza jest krótka, konkretna odpowiedź niż długi tekst bez treści.

SFT score: `{'words': 13, 'target_words': 10, 'target_overlap': 0.3, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 7}`
Winner: `sft`

### 10. target_instruction / krotkie_definicje / glyph100-sft-smoke-v0-1151

Prompt: Czym jest plik?

Target: Plik to nazwany zapis danych w systemie plików.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 8, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Kod to zapis stanu modelu, który można uruchomić po uruchomieniu programu.

SFT score: `{'words': 11, 'target_words': 8, 'target_overlap': 0.25, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 4}`
Winner: `sft`

### 11. target_instruction / brak_danych / glyph100-sft-smoke-v0-1407

Prompt: Czy ten komputer wystarczy? Jak odpowiedzieć bez danych?

Target: To zależy od zastosowania. Podaj programy, budżet i wymagania, wtedy da się ocenić sensownie.

Base:

Czy komputer jest w stanie wykonać zadania, które nie jest w stanie wykonać zadania? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 15, 'target_words': 14, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 3, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Bez danych nie da się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego ocenić bez danych nie dających się tego

SFT score: `{'words': 70, 'target_words': 14, 'target_overlap': 0.21428571428571427, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 57, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -2}`
Winner: `tie`

### 12. target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / glyph100-sft-smoke-v0-0269

Prompt: Czy można zgadywać brakujące parametry? Odpowiedz ostrożnie.

Target: Lepiej tego nie robić. Trzeba wskazać założenia albo poprosić o brakujące dane.

Base:

Czy można je porównać z innymi, ale niekoniecznie. __> W tym roku w naszym kraju, w którym mieszkaliśmy, mamy do czynienia z bardzo dużą liczbą osób, które nie są w stanie zrozumieć, jak wygląda nasze życie. W tym roku w naszym kraju, w którym mieszkaliśmy, mamy do czynienia z bardzo dużą liczbą osób, które nie są w stanie zrozumieć,

Base score: `{'words': 59, 'target_words': 12, 'target_overlap': 0.08333333333333333, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 21, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Bez tego można zgadywać brakujące parametry.

SFT score: `{'words': 7, 'target_words': 12, 'target_overlap': 0.25, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 4}`
Winner: `sft`

### 13. target_instruction / brak_danych / glyph100-sft-smoke-v0-1148

Prompt: Czy to błąd w kodzie? Co trzeba wiedzieć?

Target: Możliwe, ale potrzebny jest komunikat błędu, fragment kodu i sposób odtworzenia problemu.

Base:

Czy to błąd w kodzie? __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 41, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 33, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Lepsza jest krótka, ale krótka, ale krótka, ale krótka, ale krótka, ale krótka i krótka.

SFT score: `{'words': 16, 'target_words': 12, 'target_overlap': 0.25, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 7, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 1}`
Winner: `sft`

### 14. target_instruction / krotkie_definicje / glyph100-sft-smoke-v0-0255

Prompt: Wyjaśnij krótko pojęcie: inferencja.

Target: Inferencja to użycie wytrenowanego modelu do wygenerowania wyniku.

Base:

Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferencja. __ Wyjaśnij krótko pojęcie: inferen

Base score: `{'words': 29, 'target_words': 8, 'target_overlap': 0.125, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 21, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': True, 'exact_target_match': False, 'score': -4}`

SFT v0.1:

Inferencja to zapis stanu modelu, modelu i stanu modelu.

SFT score: `{'words': 9, 'target_words': 8, 'target_overlap': 0.375, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 7}`
Winner: `sft`

### 15. target_instruction / anty_petle / glyph100-sft-smoke-v0-1022

Prompt: Napisz krótką odpowiedź i nie powtarzaj tej samej myśli. Bez drugiej myśli.

Target: Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się, gdy ta myśl jest jasna.

Base:

Napisz krótką odpowiedź i nie wiesz, jak się z nimi komunikować. _________________________________________________________________

Base score: `{'words': 12, 'target_words': 14, 'target_overlap': 0.23076923076923078, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 1}`

SFT v0.1:

Krótka odpowiedź powinna zawierać jedną myśl i zakończyć się.

SFT score: `{'words': 9, 'target_words': 14, 'target_overlap': 0.6923076923076923, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 9}`
Winner: `sft`

### 16. target_instruction / naturalne_zakonczenia / glyph100-sft-smoke-v0-0066

Prompt: Napisz krótką odpowiedź: czy więcej funkcji zawsze oznacza lepszy projekt? Zakończ po sensownej myśli.

Target: Nie. Lepszy projekt rozwiązuje konkretny problem, a nadmiar funkcji może przeszkadzać.

Base:

Napisz krótką odpowiedź: Czy jesteś gotowy na projekt? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 9, 'target_words': 11, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`

SFT v0.1:

Nie. Lepsza jest krótka, ale krótka, ale krótka, ale krótka, ale krótka, krótka i krótka.

SFT score: `{'words': 15, 'target_words': 11, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 5, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 17. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-1147

Prompt: Czym jest smoke test?

Target: Smoke test to krótka próba sprawdzająca, czy cały pipeline działa bez oczywistych błędów.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 13, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Smoke test to krótka teoria, którą można sprawdzić po sprawdzeniu, czy model działa poprawnie.

SFT score: `{'words': 14, 'target_words': 13, 'target_overlap': 0.46153846153846156, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 8}`
Winner: `sft`

### 18. target_instruction / krotkie_definicje / glyph100-sft-smoke-v0-0529

Prompt: Czym jest prompt?

Target: Prompt to tekst wejściowy przekazany modelowi.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 6, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Prompt to zapis stanu modelu, który można uruchomić dopiero po uruchomieniu programu.

SFT score: `{'words': 12, 'target_words': 6, 'target_overlap': 0.3333333333333333, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 7}`
Winner: `sft`

### 19. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-1500

Prompt: W jednym akapicie: Czym jest tokenizer BPE?

Target: Tokenizer BPE buduje słownik z często występujących fragmentów tekstu, a potem dzieli tekst na te fragmenty.

Base:

W drugim akapicie: Jaki jest akapit? ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 6, 'target_words': 16, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`

SFT v0.1:

Tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokenizer BPE tokeni

SFT score: `{'words': 23, 'target_words': 16, 'target_overlap': 0.125, 'starts_with_target_first_word': True, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 18, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`
Winner: `tie`

### 20. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-0058

Prompt: W jednym akapicie: Czym jest fallback CPU?

Target: Fallback CPU to awaryjne uruchomienie pracy na procesorze, gdy GPU nie działa stabilnie.

Base:

W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback CPU? __ W jednym akapicie: Jak wygląda fallback

Base score: `{'words': 38, 'target_words': 13, 'target_overlap': 0.15384615384615385, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 28, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Fallback CPU to fallback CPU, ale nie fallback CPU.

SFT score: `{'words': 9, 'target_words': 13, 'target_overlap': 0.3076923076923077, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 7}`
Winner: `sft`

### 21. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-1248

Prompt: Usuń lanie wody: Proces treningu został zakończony w sposób poprawny.

Target: Trening zakończył się poprawnie.

Base:

Zapytaj lanie wody: W tym roku w naszym kraju, w którym mieszkaliśmy, mamy do czynienia z bardzo dużym zainteresowaniem. W tym roku w naszym kraju, w którym mieszkaliśmy, mamy do czynienia z bardzo dużym zainteresowaniem. W tym roku w naszym kraju, w którym mieszkaliśmy, mamy do czynienia z bardzo dużym zainteresowaniem. W tym roku w naszym kraju, w którym mieszkaliśmy

Base score: `{'words': 60, 'target_words': 4, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 39, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Proces treningu zakończył się poprawnie.

SFT score: `{'words': 5, 'target_words': 4, 'target_overlap': 0.75, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 6}`
Winner: `sft`

### 22. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-1141

Prompt: Napisz naturalniej: Proces treningu został zakończony w sposób poprawny.

Target: Trening zakończył się poprawnie.

Base:

Napisz do mnie, że nie ma żadnych wątpliwości, że to nie jest to, co się dzieje. __ Napisz do mnie, że to jest to, co się dzieje. __ Napisz do mnie, że to jest to, co się dzieje. __ Napisz do mnie, że to jest, co się dzieje. __ Napisz do mnie, że to jest, co się dzieje. __

Base score: `{'words': 59, 'target_words': 4, 'target_overlap': 0.25, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 35, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -2}`

SFT v0.1:

Proces treningu zakończył się poprawnie.

SFT score: `{'words': 5, 'target_words': 4, 'target_overlap': 0.75, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 6}`
Winner: `sft`

### 23. target_instruction / mini_streszczenia / glyph100-sft-smoke-v0-0547

Prompt: Streść w jednym zdaniu: Ewaluacja jakościowa nie jest idealna, ale pokazuje problemy niewidoczne w samym loss.

Target: Eval jakościowy uzupełnia loss.

Base:

Streszczenie w jednym zdaniu: Ewaluacja jakościowa nie jest idealna dla osób, które chcą być w stanie wykonać zadania, które są dla nich ważne. ____ Streszczenie w jednym zdaniu: Ewaluacja jakościowa nie jest niezbędna dla osób, które chcą być w stanie wykonać zadania, które są dla nich ważne. ____ Streszczenie w jednym zdaniu: Ewalu

Base score: `{'words': 53, 'target_words': 4, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 23, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Lepsza jest krótka, ale krótka, ale krótka, ale krótka, ale krótka, krótka i krótka.

SFT score: `{'words': 15, 'target_words': 4, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 5, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`
Winner: `sft`

### 24. target_instruction / proste_techniczne_wyjasnienia / glyph100-sft-smoke-v0-0702

Prompt: Czym różni się RAM od dysku?

Target: RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.

Base:

Czym różni się komputer? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 5, 'target_words': 15, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`

SFT v0.1:

RAM to liczba naturalna, ale nie wystarczająca.

SFT score: `{'words': 7, 'target_words': 15, 'target_overlap': 0.14285714285714285, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 6}`
Winner: `sft`

### 25. target_instruction / codzienne_proste_pytania / glyph100-sft-smoke-v0-1362

Prompt: Jak zacząć naukę nowego narzędzia? Bez listy.

Target: Uruchom najmniejszy przykład i dopiero potem dodawaj bardziej złożone elementy.

Base:

¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 0, 'target_words': 10, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 0}`

SFT v0.1:

Najpierw sprawdź, czy model uczy się nowych technologii i zasobów.

SFT score: `{'words': 10, 'target_words': 10, 'target_overlap': 0.1, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 26. target_instruction / anty_petle / glyph100-sft-smoke-v0-1241

Prompt: Odpowiedz krótko: czego nie da się ocenić bez danych? Bez metafor.

Target: Bez danych nie da się rzetelnie ocenić jakości, bezpieczeństwa ani opłacalności decyzji.

Base:

Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __ Napisz krótko: __

Base score: `{'words': 48, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 43, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Bez danych nie da się rzetelnie ocenić jakości.

SFT score: `{'words': 8, 'target_words': 12, 'target_overlap': 0.6666666666666666, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 9}`
Winner: `sft`

### 27. target_instruction / krotkie_poprawki_tekstu / glyph100-sft-smoke-v0-1451

Prompt: Skróć i popraw: Proszę o przesłanie informacji zwrotnej w temacie tej sprawy.

Target: Proszę o informację zwrotną w tej sprawie.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'target_words': 7, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Proszę o informację zwrotną w sprawie.

SFT score: `{'words': 6, 'target_words': 7, 'target_overlap': 0.8571428571428571, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 10}`
Winner: `sft`

### 28. target_instruction / mvp_first_project_advice / glyph100-sft-smoke-v0-0829

Prompt: Odpowiedz praktycznie: Czy robić panel admina od razu?

Target: Nie, jeśli dane można na początku obsłużyć prościej. Panel admina dodaj, gdy ręczna obsługa naprawdę przeszkadza.

Base:

Zapytaj, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel admina, czy to jest panel ad

Base score: `{'words': 51, 'target_words': 16, 'target_overlap': 0.125, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 42, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Panel admina od razu pokazuje, czy model działa poprawnie.

SFT score: `{'words': 10, 'target_words': 16, 'target_overlap': 0.1875, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 6}`
Winner: `sft`

### 29. target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / glyph100-sft-smoke-v0-0622

Prompt: Czy SFT może popsuć styl bazowy? Bez przesadnej pewności.

Target: Tak. Zbyt mocny albo schematyczny SFT może ograniczyć naturalność generacji.

Base:

Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? ____ Czy SFT może być bardziej uniwersalny? __ Czy SFT

Base score: `{'words': 51, 'target_words': 10, 'target_overlap': 0.2, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 39, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -2}`

SFT v0.1:

Nie. SFT może popsuć styl bazowy, ale styl bazowy nie jest zbyt duży.

SFT score: `{'words': 13, 'target_words': 10, 'target_overlap': 0.3, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 4}`
Winner: `sft`

### 30. target_instruction / codzienne_proste_pytania / glyph100-sft-smoke-v0-0006

Prompt: Co zrobić, gdy wynik mnie zaskakuje? Odpowiedz krótko.

Target: Sprawdź dane wejściowe, metodę pomiaru i powtórz test w tych samych warunkach.

Base:

Co zrobić, gdy mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że

Base score: `{'words': 60, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 52, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': True, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -4}`

SFT v0.1:

Najpierw sprawdź, czy wynik jest ważny, czy da się ocenić bez wyniku.

SFT score: `{'words': 12, 'target_words': 12, 'target_overlap': 0.08333333333333333, 'starts_with_target_first_word': False, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 3}`
Winner: `sft`

### 31. target_instruction / mvp_first_project_advice / glyph100-sft-smoke-v0-0468

Prompt: Krótko doradź: Czy dodać animacje?

Target: Dodaj tylko takie animacje, które pomagają zrozumieć stan interfejsu. Dekoracje nie powinny przykrywać funkcji.

Base:

Krótko, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto? ¿eś, czy warto?

Base score: `{'words': 30, 'target_words': 14, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': True, 'repetition_ngrams': 24, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -2}`

SFT v0.1:

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.

SFT score: `{'words': 40, 'target_words': 14, 'target_overlap': 0.07142857142857142, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': True, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -2}`
Winner: `tie`

### 32. target_instruction / ostrozne_odpowiedzi_przy_niepewnosci / glyph100-sft-smoke-v0-0036

Prompt: Czy trzeba trenować do końca planu? Wskaż ograniczenie.

Target: Nie. Jeśli eval pokazuje regres, lepiej zatrzymać się i przeanalizować przyczynę.

Base:

Czy warto trenować do końca plan? __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 42, 'target_words': 11, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 33, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': -3}`

SFT v0.1:

Nie. Trening powinien być stabilny, ale trzeba sprawdzić, czy model działa poprawnie.

SFT score: `{'words': 12, 'target_words': 11, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'exact_target_match': False, 'score': 6}`
Winner: `sft`

### 33. diagnostic_instruction / definition / diag-definition-backup

Prompt: Czym jest backup?

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Backup to kopia danych potrzebna do odtworzenia ich po awarii.

SFT score: `{'words': 10, 'semantic_relevance': 3, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 9}`
Winner: `sft`

### 34. diagnostic_instruction / definition / diag-definition-tokenizer

Prompt: Wyjaśnij krótko, czym jest tokenizer.

Base:

Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w porządku. __ Wyjaśnij, co jest w

Base score: `{'words': 40, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 32, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Tokenizer dzieli tekst na tokeny.

SFT score: `{'words': 5, 'semantic_relevance': 2, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 8}`
Winner: `sft`

### 35. diagnostic_instruction / technical / diag-technical-cpu-load

Prompt: Czym różni się CPU usage od load average?

Base:

Czym różni się CPU usage? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 6, 'semantic_relevance': 3, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 5}`

SFT v0.1:

CPU usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage usage

SFT score: `{'words': 27, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 23, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`
Winner: `base`

### 36. diagnostic_instruction / missing_data / diag-missing-laptop

Prompt: Czy ten laptop jest dobry?

Base:

Czy laptop jest dobry? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 5, 'semantic_relevance': 1, 'task_completion': 1, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 2}`

SFT v0.1:

Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie. Nie.

SFT score: `{'words': 40, 'semantic_relevance': 1, 'task_completion': 1, 'ended_by_end_token': False, 'natural_end': True, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 0}`
Winner: `base`

### 37. diagnostic_instruction / missing_data / diag-missing-buy

Prompt: Czy powinienem to kupić?

Base:

Czy powinienem to zrobić? ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 4, 'semantic_relevance': 1, 'task_completion': 1, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 2}`

SFT v0.1:

Nie. Brakuje informacji o produkcie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie, cenie

SFT score: `{'words': 41, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 33, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 38. diagnostic_instruction / rewrite / diag-rewrite-project

Prompt: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.

Base:

Popraw tekst: Ten projekt jest bardzo prosty i wymaga wielu funkcji, które można wykonać w dowolnym momencie. __ Popraw tekst: Ten projekt jest bardzo prosty i wymaga wielu funkcji, które można wykonać w dowolnym momencie. __ Popraw tekst: Ten projekt jest bardzo prosty i wymaga wielu funkcji, które można wykonać w dowolnym momencie. __ Popraw tekst: Ten projekt jest bardzo prosty i wymaga

Base score: `{'words': 63, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 43, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Ten projekt jest ważny, gdy nie da się tego ocenić bez używania kryteria.

SFT score: `{'words': 13, 'semantic_relevance': 3, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 9}`
Winner: `sft`

### 39. diagnostic_instruction / summary / diag-summary-scope

Prompt: Streść w jednym zdaniu: Duże projekty często upadają przez zbyt szeroki zakres.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 40, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 37, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Duże projekty często upadają poza zakres.

SFT score: `{'words': 6, 'semantic_relevance': 3, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 9}`
Winner: `sft`

### 40. diagnostic_instruction / project / diag-project-ui

Prompt: Nie wiem, czy zacząć projekt od UI czy od logiki.

Base:

Nie chcę, żebym mógł się od niej od niej od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od razu od

Base score: `{'words': 78, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 66, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Najpierw sprawdź, czy model działa poprawnie.

SFT score: `{'words': 6, 'semantic_relevance': 3, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 9}`
Winner: `sft`

### 41. diagnostic_instruction / anti_loop / diag-anti-loop

Prompt: Odpowiedz krótko i nie powtarzaj tej samej myśli.

Base:

Napisz wiadomość o tym, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz się dowiedzieć, jak długo możesz

Base score: `{'words': 67, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 56, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

Krótka myśl powinna zawierać jedną myśl i zakończyć się.

SFT score: `{'words': 9, 'semantic_relevance': 3, 'task_completion': 3, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 9}`
Winner: `sft`

### 42. diagnostic_instruction / uncertainty / diag-uncertainty-loss

Prompt: Czy niski loss oznacza dobry model?

Base:

Czy niski loss jest lepszy? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 6, 'semantic_relevance': 3, 'task_completion': 2, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 5}`

SFT v0.1:

Nie. Loss pokazuje, czy model działa poprawnie. Loss pokazuje, czy model działa poprawnie.

SFT score: `{'words': 13, 'semantic_relevance': 2, 'task_completion': 2, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 4, 'web_residue': False, 'pseudo_ency': False, 'generic_assistant_template': False, 'template_leak': False, 'prompt_overlap': False, 'score': 4}`
Winner: `tie`

### 43. continuation / base_lm_sanity / cont-01

Prompt: Warszawa to

Base:

nie tylko kwestia bezpieczeństwa, ale także doskonałej obsługi. W tym artykule przyjrzymy się, jak kluczowe jest zapewnienie bezpieczeństwa i higieny pracy. W tym artykule przyjrzymy się, jak kluczowe jest odpowiednie przygotowanie odpowiednich narzędzi do pracy. W tym artykule przyjrzymy się, jak kluczowe jest odpowiednie przygotowanie odpowiednich narzędzi do pracy. W tym artykule przyjrzymy się, jak

Base score: `{'words': 55, 'natural_end': False, 'repetition_ngrams': 25, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

nie tylko czas, ale też czas, kiedy nie da się tego ocenić. Wnioski warto sprawdzić, czy czas, kiedy i kiedy działa. Wnioski warto sprawdzić, czy czas, kiedy działa. Wnioski warto sprawdzić, czy czas, kiedy działa. Wnioski warto sprawdzić, czy czas, kiedy działa. Wnioski warto sprawdzić, czy czas, kiedy działa. Wnioski

SFT score: `{'words': 50, 'natural_end': False, 'repetition_ngrams': 26, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 44. continuation / base_lm_sanity / cont-02

Prompt: W fizyce energia

Base:

elektryczna jest równa energii, a energia elektryczna jest równa energii. Energia elektryczna jest równa energii, a energia elektryczna jest równa energii. Energia elektryczna jest równa energii, a energia elektryczna jest równa energii. Energia elektryczna jest równa energii, a energia elektryczna jest równa energii. Energia elektryczna jest rów

Base score: `{'words': 47, 'natural_end': False, 'repetition_ngrams': 36, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

jest stabilna, ale nie zależy od modelu. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabilna, ale nie zależy od modelu. Energia jest stabilna. Energia jest stabil

SFT score: `{'words': 51, 'natural_end': False, 'repetition_ngrams': 38, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 45. continuation / base_lm_sanity / cont-03

Prompt: Uczenie maszynowe polega na

Base:

tym, że maszyna ta nie jest w stanie wykonać pracy w maszynie. W przypadku maszyn elektrycznych, maszyna ta nie jest w stanie wykonać pracy w maszynie. W przypadku maszyn elektrycznych, maszyna ta nie jest w stanie wykonać pracy w maszynie. W przypadku maszyn elektrycznych, maszyna ta nie jest w stanie wykonać pracy w maszynie. Maszyna ta nie jest w stanie wykonać pracy w

Base score: `{'words': 63, 'natural_end': False, 'repetition_ngrams': 43, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

uczeniu maszynowo-chemicznym, a maszynowo-chemicznym. Uczenie maszynowo-chemiczne pozwala uczyć maszynowo-chemiczną wersję bez uczenia maszynowo-chemicznego. Uczenie maszynowo-chemiczne pozwala uczyć maszynowo-chemiczną wersję bez uczenia maszynowo-chemicznego. Uczenie maszynowo-chemi

SFT score: `{'words': 24, 'natural_end': False, 'repetition_ngrams': 8, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 46. continuation / base_lm_sanity / cont-04

Prompt: Najważniejszym problemem tego projektu jest

Base:

wybór odpowiedniego miejsca na dysku twardym, który może być używany w wielu różnych sytuacjach. W tym artykule przyjrzymy się bliżej temu, jak kluczowe jest znalezienie miejsca na dysku twardym, który może być używany w wielu różnych sytuacjach. W dzisiejszych czasach coraz więcej osób decyduje się na korzystanie z usług profesjonalnych firm, które oferują profesjonalną usługę. Dzięki temu, że profesjonalna

Base score: `{'words': 59, 'natural_end': False, 'repetition_ngrams': 11, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

wybór konkretnego projektu, który może być przydatny przy tworzeniu nowych projektów. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko i sprawnie działających projektach. Dzięki temu można szybko

SFT score: `{'words': 55, 'natural_end': False, 'repetition_ngrams': 34, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 47. continuation / base_lm_sanity / cont-05

Prompt: Dobry raport techniczny

Base:

, który został opublikowany w czasopiśmie „Gazeta Wyborcza” w grudniu 2005. W tym samym roku został redaktorem naczelnym miesięcznika „Gazeta Wyborcza” w Warszawie. W tym samym roku został redaktorem naczelnym miesięcznika „Gazeta Wyborcza” w Warszawie. W tym samym roku został redaktorem naczelnym miesięcznika „Gazeta Wyborcza” w Warszawie. W

Base score: `{'words': 47, 'natural_end': False, 'repetition_ngrams': 24, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

, który pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny pozwala ocenić, czy model działa poprawnie. Raport techniczny

SFT score: `{'words': 49, 'natural_end': False, 'repetition_ngrams': 38, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 48. continuation / base_lm_sanity / cont-06

Prompt: Na początku eksperymentu

Base:

na temat tego, jak wyglądało to w przypadku innych osób, które nie miały pojęcia, jak wyglądało to w przypadku innych osób. W tym przypadku, w przypadku osób, które nie miały pojęcia, jak wyglądało to w przypadku innych osób, które nie miały pojęcia, jak wyglądało to w przypadku innych osób. W tym przypadku, w przypadku osób, które nie miały pojęcia, jak wyglądało to

Base score: `{'words': 62, 'natural_end': False, 'repetition_ngrams': 39, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

ję z różnymi technikami, które pozwalają na lepszą poprawę jakości danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość danych. Dzięki temu można szybko i bez problemu poprawić jakość

SFT score: `{'words': 70, 'natural_end': False, 'repetition_ngrams': 48, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 49. continuation / base_lm_sanity / cont-07

Prompt: Czysty dataset

Base:

ki, czy też inne. W tym przypadku, jeśli nie ma miejsca na to, aby być w stanie zrobić to, co zrobić, aby zrobić, aby zrobić to, co zrobić, aby zrobić, aby zrobić to, co zrobić, aby zrobić, aby zrobić to, co zrobić, aby zrobić, aby zrobić to, co zrobić, aby zrobić, aby zrobić to, co zrobić, aby zrobić,

Base score: `{'words': 58, 'natural_end': False, 'repetition_ngrams': 33, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

t można porównać do danych wejściowych. Dane wejściowe mogą wskazywać, czy model działa poprawnie. Wnioski warto potwierdzić kolejnym wejściem. Dane wejściowe mogą wskazywać, czy model działa poprawnie. Wnioski warto potwierdzić kolejnym wejściem. Dane wejściowe mogą wskazywać, czy model działa poprawnie. Wnioski warto potwierdzić kolejnym wej

SFT score: `{'words': 45, 'natural_end': False, 'repetition_ngrams': 23, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`

### 50. continuation / base_lm_sanity / cont-08

Prompt: Walidacja pokazuje

Base:

, że w tym roku w Polsce w tym roku w Polsce w tym roku w Polsce odnotowano ponad 330 tys. osób. W tym roku w Polsce odnotowano ponad 330 tys. osób. W tym roku w Polsce odnotowano ponad 330 tys. osób. W Polsce odnotowano ponad 330 tys. osób. W Polsce odnotowano ponad 330 tys. osób. W Polsce odnotowano

Base score: `{'words': 58, 'natural_end': False, 'repetition_ngrams': 42, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`

SFT v0.1:

, czy model uczy się przewidywać dane treningowe. Trening może być prosty, ale nie krótki. Trening może być prosty, ale prosty. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki. Trening może być prosty, ale nie krótki

SFT score: `{'words': 55, 'natural_end': False, 'repetition_ngrams': 36, 'web_residue': False, 'pseudo_ency': False, 'prompt_overlap': False, 'score': 1}`
Winner: `tie`
