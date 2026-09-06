# Glyph-27M SFT v0 eval summary v2

## Verdict

SFT v0 still beats Base under the stricter scoring, but the margin is much less flattering than the old heuristic if weak wins are removed.

## Old vs new counts

- old counts from eval v1: `{'both_bad': 9, 'sft': 24, 'tie': 2, 'base': 5}`
- old counts recomputed in this run: `{'both_bad': 9, 'sft': 24, 'tie': 2, 'base': 5}`
- new counts: `{'both_bad': 24, 'sft': 11, 'base': 5}`
- weak SFT wins removed: 13

## New average scores

- base semantic_relevance: 0.88/3
- SFT semantic_relevance: 1.02/3
- base task_completion: 0.78/3
- SFT task_completion: 1.12/3

## New failure counters

- base_cannot_win: 33
- sft_cannot_win: 29
- base_question_echo: 0
- sft_question_echo: 4
- base_project_advice_drift: 0
- sft_project_advice_drift: 11

## Repeated SFT phrases

- `jeśli po tym dalej`: 10
- `w praktyce warto`: 4
- `podejdź do tego jak do małego testu`: 2
- `nie ma sensu`: 1

## Main read

- Clean ending is useful, but it is no longer enough to win.
- Rewriting and summarization remain the weakest practical areas.
- Missing-data behavior improved slightly, but is still not reliable.
- Factual definitions still need direct-answer data in SFT v0.1.

## Examples to inspect first

- 01. `brak_danych` old=both_bad new=both_bad: Czy ten laptop jest dobry?
- 02. `brak_danych` old=sft new=both_bad: Czy ten wynik jest poprawny?
- 04. `brak_danych` old=both_bad new=both_bad: Czy powinienem to kupić?
- 05. `brak_danych` old=sft new=both_bad: Czy moja odpowiedź jest dobra?
- 06. `pisanie_i_poprawianie` old=tie new=both_bad: Popraw tekst: Ten projekt jest bardzo dobry, ponieważ posiada wiele funkcji i działa w dobry sposób.
- 08. `pisanie_i_poprawianie` old=both_bad new=both_bad: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.
- 09. `pisanie_i_poprawianie` old=base new=base: Skróć tekst: Ten projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.
- 10. `pisanie_i_poprawianie` old=sft new=base: Napisz neutralną wiadomość, że nie mogę dziś przyjść.
- 11. `streszczanie` old=sft new=both_bad: Streść w jednym zdaniu: Duże projekty często upadają nie dlatego, że są niemożliwe, ale dlatego, że zaczynają się od zbyt szerokiego zakresu.
- 13. `streszczanie` old=base new=both_bad: Wyciągnij najważniejszą myśl: Jeśli uczysz się tylko przez czytanie odpowiedzi, łatwo pomylić znajomość tekstu ze zrozumieniem.
- 16. `proste_wyjasnienia` old=sft new=base: Wyjaśnij prosto, czym różni się pogoda od klimatu.
- 17. `proste_wyjasnienia` old=sft new=both_bad: Wyjaśnij, czym jest inflacja.
