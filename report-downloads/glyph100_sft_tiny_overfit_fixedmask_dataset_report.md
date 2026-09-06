# Glyph-100M fixed-mask tiny overfit dataset

- source dataset: `data/sft/glyph100_sft_smoke_v0.jsonl`
- output: `data/sft/processed/glyph100_sft_tiny_overfit_fixedmask_train.jsonl`
- examples: 64
- max template tokens: 61
- over context 512: 0

## Categories

- `krotkie_definicje`: 8
- `proste_techniczne_wyjasnienia`: 7
- `mvp_first_project_advice`: 7
- `brak_danych`: 7
- `krotkie_poprawki_tekstu`: 7
- `mini_streszczenia`: 7
- `anty_petle`: 7
- `codzienne_proste_pytania`: 7
- `ostrozne_odpowiedzi_przy_niepewnosci`: 7

## Sample Examples

### tiny-fixedmask-0001 / krotkie_definicje

Instruction: Co oznacza termin „metryka”?

Response: Metryka to liczba opisująca wybraną cechę działania systemu.

### tiny-fixedmask-0002 / krotkie_definicje

Instruction: Co oznacza termin „wersjonowanie”?

Response: Wersjonowanie pozwala śledzić zmiany i wracać do wcześniejszych stanów projektu.

### tiny-fixedmask-0003 / krotkie_definicje

Instruction: Podaj prostą definicję: dokumentacja.

Response: Dokumentacja opisuje, jak projekt działa, jak go uruchomić i jakie ma ograniczenia.

### tiny-fixedmask-0004 / krotkie_definicje

Instruction: Wyjaśnij krótko pojęcie: wątek.

Response: Wątek to część procesu, która może wykonywać pracę równolegle z innymi wątkami.

### tiny-fixedmask-0005 / krotkie_definicje

Instruction: Wyjaśnij krótko pojęcie: metryka.

Response: Metryka to liczba opisująca wybraną cechę działania systemu.

### tiny-fixedmask-0006 / krotkie_definicje

Instruction: Podaj prostą definicję: konfiguracja.

Response: Konfiguracja to zestaw ustawień sterujących działaniem systemu.

### tiny-fixedmask-0007 / proste_techniczne_wyjasnienia

Instruction: Krótko i konkretnie: Czym jest deduplikacja danych?

Response: Deduplikacja usuwa powtarzające się dokumenty albo fragmenty, żeby model nie uczył się jednego tekstu zbyt wiele razy.

### tiny-fixedmask-0008 / proste_techniczne_wyjasnienia

Instruction: Po co rozdziela się train i val?

Response: Rozdział train i val pozwala sprawdzić, czy model działa poza przykładami używanymi do uczenia.

### tiny-fixedmask-0009 / proste_techniczne_wyjasnienia

Instruction: Krótko i konkretnie: Po co używa się Dockera?

Response: Docker ułatwia uruchamianie aplikacji z tymi samymi zależnościami na różnych maszynach.

### tiny-fixedmask-0010 / proste_techniczne_wyjasnienia

Instruction: Wyjaśnij krótko, czym różni się RAM od dysku?

Response: RAM jest szybka i ulotna, a dysk jest wolniejszy, ale przechowuje dane po wyłączeniu komputera.
