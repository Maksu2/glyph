# Glyph-27M SFT v0 decoding sweep summary

- best overall preset: `creative_controlled`
- best public-demo preset: `creative_controlled`
- best usable outputs: 5/16
- demo usable outputs: 5/16

## Read

- Lower temperature did not help on its own if `strict_medium` vs `balanced_current` is used as the comparison: usable 2 vs 4, weak 14 vs 12.
- Higher repetition penalty in `anti_repeat` produced usable=4 and repetition_count=5.
- max_new_tokens=60 reduced length to avg 42.9 tokens, but weak outputs remained 14.

## Recommendation

Use `creative_controlled` for public-facing SFT v0 generation if SFT v0 must be exposed. It is more conservative than the previous preset, but decoding does not fix the core dataset/style problems.

## Cases decoding does not fix

- 01. `brak_danych`: Czy ten laptop jest dobry?
- 02. `brak_danych`: Czy powinienem to kupić?
- 03. `brak_danych`: Czy to jest bezpieczne?
- 05. `pisanie_i_poprawianie`: Popraw tekst, żeby brzmiał naturalniej: W mojej opinii uważam, że ten problem powinien zostać rozwiązany w szybkim czasie.
- 06. `pisanie_i_poprawianie`: Napisz krótką wiadomość do nauczyciela, że nie zdążę oddać pracy dzisiaj.
- 10. `proste_wyjasnienia`: Wyjaśnij, czym jest inflacja.
- 11. `proste_wyjasnienia`: Czym różni się fakt od opinii?
- 13. `korekta_zalozen`: Popraw błędne założenie: jeśli projekt używa AI, to automatycznie jest bardziej zaawansowany.
