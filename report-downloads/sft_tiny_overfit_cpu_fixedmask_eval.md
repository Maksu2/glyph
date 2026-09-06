# Glyph-100M SFT tiny overfit fixed-mask eval

## Summary

- base checkpoint: `checkpoints/glyph-100m-v2_3_1-45k/step_0044000.pt`
- tiny SFT checkpoint: `checkpoints/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask/glyph-100m-v2_3_1-44k-sft-tiny-overfit-cpu-fixedmask-final.pt`
- examples: 32
- base avg score: -1.53
- SFT avg score: 9.94
- winners: `{'sft': 32}`
- SFT exact/near target overlap >= 0.70: 32
- SFT starts with expected first word: 32
- SFT ended by `<|end|>`: 32
- SFT repetition samples: 0
- SFT web residue: 1
- SFT pseudo-ency: 0

## Samples

### 01. glyph100-sft-smoke-v0-0317 / krotkie_definicje

Prompt: Co oznacza termin „metryka”?

Target: Metryka to liczba opisująca wybraną cechę działania systemu.

Base:

Co oznacza, że „metryka” jest „metryką”? ____ Co oznacza, że „metryka” jest „metryką”? ____ Co oznacza, że „metryka” jest „metryką”? ____ Co oznacza, że „metryka” jest „metryką”? ____

Base score: `{'words': 28, 'target_words': 8, 'target_overlap': 0.125, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 19, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Metryka to liczba opisująca wybraną cechę działania systemu.

Tiny SFT score: `{'words': 8, 'target_words': 8, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 02. glyph100-sft-smoke-v0-0713 / krotkie_definicje

Prompt: Co oznacza termin „wersjonowanie”?

Target: Wersjonowanie pozwala śledzić zmiany i wracać do wcześniejszych stanów projektu.

Base:

Co oznacza, że „wersjonowanie” jest procesem, który pozwala na szybkie i łatwe w użyciu. W tym przypadku, jeśli ktoś chce się z nim komunikować, to może to zrobić, gdy ktoś chce się z nim komunikować. W tym przypadku, jeśli ktoś chce się z nim komunikować, to może

Base score: `{'words': 47, 'target_words': 10, 'target_overlap': 0.3, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 14, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -2}`

Tiny SFT:

Wersjonowanie pozwala śledzić zmiany i wracać do wcześniejszych stanów projektu.

Tiny SFT score: `{'words': 10, 'target_words': 10, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 03. glyph100-sft-smoke-v0-1277 / krotkie_definicje

Prompt: Podaj prostą definicję: dokumentacja.

Target: Dokumentacja opisuje, jak projekt działa, jak go uruchomić i jakie ma ograniczenia.

Base:

Napisz do mnie, że w tym przypadku nie ma żadnych wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym przypadku nie ma wątpliwości, że w tym

Base score: `{'words': 56, 'target_words': 12, 'target_overlap': 0.09090909090909091, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 41, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Dokumentacja opisuje, jak projekt działa, jak go uruchomić i jakie ma ograniczenia.

Tiny SFT score: `{'words': 12, 'target_words': 12, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 04. glyph100-sft-smoke-v0-0797 / krotkie_definicje

Prompt: Wyjaśnij krótko pojęcie: wątek.

Target: Wątek to część procesu, która może wykonywać pracę równolegle z innymi wątkami.

Base:

Wyjaśnij, co jest dla Ciebie ważne. ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 6, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Wątek to część procesu, która może wykonywać pracę równolegle z innymi wątkami.

Tiny SFT score: `{'words': 12, 'target_words': 12, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 05. glyph100-sft-smoke-v0-0228 / krotkie_definicje

Prompt: Wyjaśnij krótko pojęcie: metryka.

Target: Metryka to liczba opisująca wybraną cechę działania systemu.

Base:

Wyjaśnij, co jest ważne, abyś mógł być zadowolony z tego, co jest ważne, abyś mógł być zadowolony z tego, co jest ważne, abyś mógł być zadowolony z tego, co jest ważne, abyś mógł być zadowolony z tego, co jest ważne, abyś mógł być zadowolony z tego

Base score: `{'words': 46, 'target_words': 8, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 34, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Metryka to liczba opisująca wybraną cechę działania systemu.

Tiny SFT score: `{'words': 8, 'target_words': 8, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 06. glyph100-sft-smoke-v0-0697 / krotkie_definicje

Prompt: Podaj prostą definicję: konfiguracja.

Target: Konfiguracja to zestaw ustawień sterujących działaniem systemu.

Base:

Napisz prostą definicję: konfiguracja. __ Napisz prostą definicję: konfiguracja. __ Napisz prostą definicję: konfiguracja. __ Napisz prostą definicję: konfiguracja. __ Napisz prostą definicję: konfiguracja. __ Napisz prostą defini

Base score: `{'words': 28, 'target_words': 7, 'target_overlap': 0.14285714285714285, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 20, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Konfiguracja to zestaw ustawień sterujących działaniem systemu.

Tiny SFT score: `{'words': 7, 'target_words': 7, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 07. glyph100-sft-smoke-v0-1213 / proste_techniczne_wyjasnienia

Prompt: Krótko i konkretnie: Czym jest deduplikacja danych?

Target: Deduplikacja usuwa powtarzające się dokumenty albo fragmenty, żeby model nie uczył się jednego tekstu zbyt wiele razy.

Base:

Krótko i konkretnie: ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___ ___

Base score: `{'words': 22, 'target_words': 17, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 16, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Deduplikacja usuwa powtarzające się dokumenty albo fragmenty, żeby model nie uczył się jednego tekstu zbyt wiele razy.

Tiny SFT score: `{'words': 17, 'target_words': 17, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 08. glyph100-sft-smoke-v0-0069 / proste_techniczne_wyjasnienia

Prompt: Po co rozdziela się train i val?

Target: Rozdział train i val pozwala sprawdzić, czy model działa poza przykładami używanymi do uczenia.

Base:

Po co rozdziela się train i val? ¿eś, co rozdzielasz? ¿eś, co rozdzielasz? ¿eś, co rozdzielasz? ¿eś, co rozdzielasz? ¿eś, co rozdzielasz? ¿e

Base score: `{'words': 23, 'target_words': 14, 'target_overlap': 0.21428571428571427, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 10, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -2}`

Tiny SFT:

Rozdział train i val pozwala sprawdzić, czy model działa poza przykładami używanymi do uczenia.

Tiny SFT score: `{'words': 14, 'target_words': 14, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 09. glyph100-sft-smoke-v0-0155 / proste_techniczne_wyjasnienia

Prompt: Krótko i konkretnie: Po co używa się Dockera?

Target: Docker ułatwia uruchamianie aplikacji z tymi samymi zależnościami na różnych maszynach.

Base:

Krótko i konkretnie: Po co używa się Dockera? _________________________________________________

Base score: `{'words': 9, 'target_words': 11, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Docker ułatwia uruchamianie aplikacji z tymi samymi zależnościami na różnych maszynach.

Tiny SFT score: `{'words': 11, 'target_words': 11, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 10. glyph100-sft-smoke-v0-1463 / proste_techniczne_wyjasnienia

Prompt: Wyjaśnij krótko, czym różni się RAM od dysku?

Target: RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.

Base:

Wyjaśnij krótko, co oznacza, że nie ma żadnych problemów z obsługą. __ Wyjaśnij krótko, co oznacza, że nie ma problemów z obsługą. __ Wyjaśnij krótko, co oznacza, że nie ma problemów z obsługą. __ Wyjaśnij krótko,

Base score: `{'words': 36, 'target_words': 15, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 20, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.

Tiny SFT score: `{'words': 15, 'target_words': 15, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 11. glyph100-sft-smoke-v0-1059 / proste_techniczne_wyjasnienia

Prompt: Wyjaśnij krótko: Co oznacza context length?

Target: Context length to maksymalna liczba tokenów, które model widzi jednocześnie.

Base:

Wyjaśnij krótko: Co oznacza context length? __ Wyjaśnij krótko: Co oznacza context length? __ Wyjaśnij krótko: Co oznacza context length? __ Wyjaśnij krótko: Co oznacza context leng

Base score: `{'words': 27, 'target_words': 10, 'target_overlap': 0.2, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 17, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -2}`

Tiny SFT:

Context length to maksymalna liczba tokenów, które model widzi jednocześnie.

Tiny SFT score: `{'words': 10, 'target_words': 10, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 12. glyph100-sft-smoke-v0-1133 / proste_techniczne_wyjasnienia

Prompt: Odpowiedz prosto: Po co są logi treningu?

Target: Logi treningu pokazują kroki, loss, prędkość, checkpointy i błędy.

Base:

Napisz do mnie: ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 3, 'target_words': 9, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Logi treningu pokazują kroki, loss, prędkość, checkpointy i błędy.

Tiny SFT score: `{'words': 9, 'target_words': 9, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 13. glyph100-sft-smoke-v0-0264 / mvp_first_project_advice

Prompt: Odpowiedz praktycznie: Jak ograniczyć zakres projektu?

Target: Usuń wszystko, czego nie trzeba do pierwszego działającego scenariusza.

Base:

Napisz do nas: email@example.com W tym roku w naszym kraju, w którym w tym roku w Polsce, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w naszym kraju, w

Base score: `{'words': 47, 'target_words': 9, 'target_overlap': 0.1111111111111111, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 27, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Usuń wszystko, czego nie trzeba do pierwszego działającego scenariusza.

Tiny SFT score: `{'words': 9, 'target_words': 9, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 14. glyph100-sft-smoke-v0-1101 / mvp_first_project_advice

Prompt: Co zrobić? Jak ocenić, czy projekt idzie dobrze?

Target: Sprawdź, czy da się przejść główny scenariusz od początku do końca. To ważniejsze niż liczba funkcji.

Base:

Co zrobić? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 3, 'target_words': 16, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Sprawdź, czy da się przejść główny scenariusz od początku do końca. To ważniejsze niż liczba funkcji.

Tiny SFT score: `{'words': 16, 'target_words': 16, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 15. glyph100-sft-smoke-v0-1336 / mvp_first_project_advice

Prompt: Krótko doradź: Chcę poprawiać wygląd zanim działa backend.

Target: Najpierw upewnij się, że dane i podstawowe akcje działają. Wygląd ma sens dopiero, gdy nie maskuje braków funkcjonalnych.

Base:

Krótko, jak się dzieje, gdy jest to możliwe. __ Krótko, jak się dzieje, gdy jest to możliwe. __ Krótko, jak się dzieje, gdy jest to możliwe. __ Krótko, jak się dzieje, gdy jest to możliwe. __ Krótko,

Base score: `{'words': 37, 'target_words': 18, 'target_overlap': 0.1111111111111111, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 26, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Najpierw upewnij się, że dane i podstawowe akcje działają. Wygląd ma sens dopiero, gdy nie maskuje braków funkcjonalnych.

Tiny SFT score: `{'words': 18, 'target_words': 18, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 16. glyph100-sft-smoke-v0-0637 / mvp_first_project_advice

Prompt: Krótko doradź: Jak rozbić duży projekt?

Target: Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki.

Base:

Krótko mówiąc, nie ma co robić, żeby zrobić to, żeby zrobić to, żeby zrobić to, żeby zrobić to, żeby zrobić to, żeby zrobić to, żeby zrobić to, żeby zrobić to, co robi. ___>>>>>>>>>>>>>>>>

Base score: `{'words': 33, 'target_words': 13, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 19, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki.

Tiny SFT score: `{'words': 13, 'target_words': 13, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 17. glyph100-sft-smoke-v0-1249 / mvp_first_project_advice

Prompt: Odpowiedz praktycznie: Jak rozbić duży projekt?

Target: Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki.

Base:

Napisz do mnie: ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 3, 'target_words': 13, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Podziel go na etapy: dane, główna logika, prosty widok, test, dopiero potem dodatki.

Tiny SFT score: `{'words': 13, 'target_words': 13, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 18. glyph100-sft-smoke-v0-0518 / mvp_first_project_advice

Prompt: Krótko doradź: Mam pomysł na aplikację i chcę od razu zrobić logowanie, dashboard i AI.

Target: Najpierw zbuduj najmniejszą wersję, która pokazuje główną wartość. Logowanie i dashboard dodaj dopiero, gdy podstawowy przepływ działa.

Base:

__>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 1, 'target_words': 17, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Najpierw zbuduj najmniejszą wersję, która pokazuje główną wartość. Logowanie i dashboard dodaj dopiero, gdy podstawowy przepływ działa.

Tiny SFT score: `{'words': 17, 'target_words': 17, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 19. glyph100-sft-smoke-v0-0107 / brak_danych

Prompt: Czy wynik benchmarku jest dobry? Odpowiedz krótko.

Target: Trzeba znać sprzęt, ustawienia testu i punkt odniesienia. Sama liczba nie wystarcza.

Base:

Czy wynik jest dobry? Napisz wiadomość o tym, jak długo będzie wyglądał na niego. __> W tym roku w Polsce w tym roku w Polsce w tym roku w Polsce w tym roku w Polsce w tym roku w Polsce było ponad 20 tys. osób. W tym roku w Polsce w tym roku w Polsce

Base score: `{'words': 55, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 26, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Trzeba znać sprzęt, ustawienia testu i punkt odniesienia. Sama liczba nie wystarcza.

Tiny SFT score: `{'words': 12, 'target_words': 12, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 20. glyph100-sft-smoke-v0-1322 / brak_danych

Prompt: Czy to błąd w kodzie? Podaj uczciwą odpowiedź.

Target: Możliwe, ale potrzebny jest komunikat błędu, fragment kodu i sposób odtworzenia problemu.

Base:

Czy to błąd w kodzie? Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie. __ Napisz do mnie

Base score: `{'words': 44, 'target_words': 12, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 33, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Możliwe, ale potrzebny jest komunikat błędu, fragment kodu i sposób odtworzenia problemu.

Tiny SFT score: `{'words': 12, 'target_words': 12, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 21. glyph100-sft-smoke-v0-0999 / brak_danych

Prompt: Czy moja odpowiedź jest dobra? Wskaż brakujące informacje.

Target: Nie da się ocenić bez treści odpowiedzi i kryteriów oceny.

Base:

Czy mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję, że mam nadzieję,

Base score: `{'words': 48, 'target_words': 10, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 42, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Nie da się ocenić bez treści odpowiedzi i kryteriów oceny.

Tiny SFT score: `{'words': 10, 'target_words': 10, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': True, 'pseudo_ency': False, 'template_leak': False, 'score': 8}`
Winner: `sft`

### 22. glyph100-sft-smoke-v0-0305 / brak_danych

Prompt: Czy ten plan ma sens? Jak odpowiedzieć bez danych?

Target: Potrzebuję celu, ograniczeń i dostępnych zasobów. Bez nich plan może wyglądać dobrze, ale nie pasować do sytuacji.

Base:

Czy to jest problem? ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 4, 'target_words': 17, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Potrzebuję celu, ograniczeń i dostępnych zasobów. Bez nich plan może wyglądać dobrze, ale nie pasować do sytuacji.

Tiny SFT score: `{'words': 17, 'target_words': 17, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 23. glyph100-sft-smoke-v0-1061 / brak_danych

Prompt: Czy wybrałem dobrą technologię? Nie zgaduj.

Target: To zależy od wymagań projektu, zespołu i czasu. Bez tych danych odpowiedź byłaby zbyt ogólna.

Base:

Czy nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie

Base score: `{'words': 33, 'target_words': 15, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 29, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

To zależy od wymagań projektu, zespołu i czasu. Bez tych danych odpowiedź byłaby zbyt ogólna.

Tiny SFT score: `{'words': 15, 'target_words': 15, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 24. glyph100-sft-smoke-v0-0555 / brak_danych

Prompt: Czy wybrałem dobrą technologię? Nie udawaj pewności.

Target: To zależy od wymagań projektu, zespołu i czasu. Bez tych danych odpowiedź byłaby zbyt ogólna.

Base:

Czy nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie, nie

Base score: `{'words': 33, 'target_words': 15, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 29, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

To zależy od wymagań projektu, zespołu i czasu. Bez tych danych odpowiedź byłaby zbyt ogólna.

Tiny SFT score: `{'words': 15, 'target_words': 15, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 25. glyph100-sft-smoke-v0-0708 / krotkie_poprawki_tekstu

Prompt: Napisz naturalniej: Chciałbym poinformować, że nie zdążę oddać pracy dzisiaj.

Target: Nie zdążę dziś oddać pracy.

Base:

Napisz, jak wygląda praca, która jest dla mnie bardzo ważna. ___>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 11, 'target_words': 5, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Nie zdążę dziś oddać pracy.

Tiny SFT score: `{'words': 5, 'target_words': 5, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 26. glyph100-sft-smoke-v0-1075 / krotkie_poprawki_tekstu

Prompt: Usuń lanie wody: System działa w taki sposób, że użytkownik może dokonać wyboru opcji.

Target: System pozwala użytkownikowi wybrać opcję.

Base:

Zapytaj lanie wody: System działa w taki sposób, aby nie było żadnych problemów z ich usunięciem. __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 17, 'target_words': 5, 'target_overlap': 0.2, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 1}`

Tiny SFT:

System pozwala użytkownikowi wybrać opcję.

Tiny SFT score: `{'words': 5, 'target_words': 5, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 27. glyph100-sft-smoke-v0-0812 / krotkie_poprawki_tekstu

Prompt: Skróć i popraw: Nie posiadam wystarczającej ilości danych do oceny.

Target: Nie mam wystarczających danych do oceny.

Base:

__ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __ __

Base score: `{'words': 32, 'target_words': 6, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 29, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -3}`

Tiny SFT:

Nie mam wystarczających danych do oceny.

Tiny SFT score: `{'words': 6, 'target_words': 6, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 28. glyph100-sft-smoke-v0-0660 / krotkie_poprawki_tekstu

Prompt: Usuń lanie wody: Została przeprowadzona walidacja poprawności działania systemu.

Target: Sprawdzono poprawność działania systemu.

Base:

Zapytaj lanie wody: Czy wiesz, że woda jest bezpieczna? __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 10, 'target_words': 4, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Sprawdzono poprawność działania systemu.

Tiny SFT score: `{'words': 4, 'target_words': 4, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 29. glyph100-sft-smoke-v0-1168 / krotkie_poprawki_tekstu

Prompt: Popraw tekst: To rozwiązanie cechuje się wysokim poziomem prostoty.

Target: To rozwiązanie jest proste.

Base:

Popraw tekst: To rozwiązanie jest bardzo łatwe i łatwe w obsłudze. ____ Popraw tekst: To rozwiązanie jest bardzo łatwe w obsłudze. ¿ Popraw tekst: To rozwiązanie jest bardzo łatwe w obsłudze. ¿ Popraw tekst: To rozwiązanie jest bardzo łatwe w obsłudze. ¿ Popraw tekst: To rozwiązanie

Base score: `{'words': 43, 'target_words': 4, 'target_overlap': 0.75, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 26, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

To rozwiązanie jest proste.

Tiny SFT score: `{'words': 4, 'target_words': 4, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 30. glyph100-sft-smoke-v0-1281 / krotkie_poprawki_tekstu

Prompt: Przeredaguj zdanie: Ten fragment można napisać w sposób bardziej naturalny.

Target: Ten fragment można napisać naturalniej.

Base:

Przeredaguj zdanie: Ten fragment jest prosty i prosty. __>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

Base score: `{'words': 9, 'target_words': 5, 'target_overlap': 0.4, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 2}`

Tiny SFT:

Ten fragment można napisać naturalniej.

Tiny SFT score: `{'words': 5, 'target_words': 5, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 31. glyph100-sft-smoke-v0-0639 / mini_streszczenia

Prompt: Wyciągnij najważniejszą myśl: Dobre ograniczenia zasobów chronią inne usługi na tym samym serwerze.

Target: Limity zasobów chronią stabilność hosta.

Base:

Wyciągnij wszystkie swoje usługi, aby uzyskać dostęp do Twoich usług. ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿ ¿

Base score: `{'words': 10, 'target_words': 5, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 0}`

Tiny SFT:

Limity zasobów chronią stabilność hosta.

Tiny SFT score: `{'words': 5, 'target_words': 5, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`

### 32. glyph100-sft-smoke-v0-0942 / mini_streszczenia

Prompt: Streść w jednym zdaniu: Jeśli test zależy od losowego samplingu, trzeba sprawdzić kilka seedów.

Target: Kilka seedów pomaga odróżnić jakość od losowości.

Base:

Streszczenie w jednym zdaniu: Jeśli test jest prosty, to warto sprawdzić, czy test jest prosty. ___________________________________________

Base score: `{'words': 16, 'target_words': 7, 'target_overlap': 0.0, 'starts_with_target_first_word': False, 'ended_by_end_token': False, 'natural_end': False, 'repetition_ngrams': 1, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': -1}`

Tiny SFT:

Kilka seedów pomaga odróżnić jakość od losowości.

Tiny SFT score: `{'words': 7, 'target_words': 7, 'target_overlap': 1.0, 'starts_with_target_first_word': True, 'ended_by_end_token': True, 'natural_end': True, 'repetition_ngrams': 0, 'web_residue': False, 'pseudo_ency': False, 'template_leak': False, 'score': 10}`
Winner: `sft`
