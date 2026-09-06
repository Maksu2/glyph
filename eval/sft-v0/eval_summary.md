# Glyph-27M SFT v0 eval summary

## Verdict

SFT v0 is usually better than Base for instruction-like prompts, but not good enough to call it a reliable assistant.

## Counts

- SFT wins: 24
- Base wins: 5
- Tie: 2
- Both bad: 9

## Lengths and endings

- Base avg words: 76.1
- SFT avg words: 35.1
- Base ended with `<|end|>`: 0
- SFT ended with `<|end|>`: 40
- Base likely cut off: 33
- SFT likely cut off: 0

## Main improvements

- SFT reduces obvious web/forum artifacts compared with Base.
- SFT more often attempts instruction-shaped answers.
- SFT is more likely to use uncertainty language on missing-data prompts.

## Main regressions / issues

- SFT often overuses dataset-like advice patterns.
- SFT can drift into generic project-advice wording even for factual/simple explanation prompts.
- SFT ends much more cleanly than Base, but some endings close a generic template instead of a useful answer.
- Some SFT wins are weak wins: the SFT output is less broken than Base, not necessarily good.

## Repeated SFT phrases

- `jeśli po tym dalej`: 10
- `w praktyce warto`: 4
- `podejdź do tego jak do małego testu`: 2
- `nie ma sensu`: 1

## SFT v0.1 dataset suggestions

- Add more direct answer examples that do not use the phrase `najkrótszy ruch` or `mały test`.
- Add missing-data examples with varied wording: `nie mam wystarczających informacji`, `potrzebny jest model/parametry/kontekst`, `tego nie da się rozstrzygnąć z opisu`.
- Add simple factual explanation examples with compact definitions and no project-advice framing.
- Add negative examples for rambling: short prompt, one concise paragraph, explicit stop after answer.
- Add rewriting/summarization examples where output is only the rewritten text, not meta-commentary.

## Category winners

- `anty_petle`: {'sft': 4, 'both_bad': 1}
- `brak_danych`: {'both_bad': 2, 'sft': 3}
- `decyzje_projektowe`: {'both_bad': 2, 'sft': 3}
- `korekta_zalozen`: {'both_bad': 3, 'base': 1, 'tie': 1}
- `pisanie_i_poprawianie`: {'tie': 1, 'sft': 2, 'both_bad': 1, 'base': 1}
- `proste_wyjasnienia`: {'sft': 4, 'base': 1}
- `streszczanie`: {'sft': 4, 'base': 1}
- `techniczne_proste`: {'base': 1, 'sft': 4}

## Examples to inspect first

- 01. `brak_danych` winner=both_bad: Czy ten laptop jest dobry?
- 04. `brak_danych` winner=both_bad: Czy powinienem to kupić?
- 08. `pisanie_i_poprawianie` winner=both_bad: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.
- 09. `pisanie_i_poprawianie` winner=base: Skróć tekst: Ten projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.
- 13. `streszczanie` winner=base: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.
- 19. `proste_wyjasnienia` winner=base: Wyjaśnij krótko, czym jest grawitacja.
- 21. `decyzje_projektowe` winner=both_bad: Mam zacząć projekt od UI czy od logiki?
- 22. `decyzje_projektowe` winner=both_bad: Mam ambitny projekt i chcę od razu zrobić backend, frontend, dashboard, AI, logowanie i ładne UI. Dobry plan?
