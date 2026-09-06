# Glyph-100M SFT label mask fix audit

## Verdict

PASS: fixed label mask supervises the first assistant response token.

## Boundary

- old: `i <= assistant_pos`
- new: `i < assistant_pos`

## Checks

- first_Loss_token_supervised: `True`
- first_Nie_token_supervised: `True`
- first_Projekt_token_supervised: `True`
- end_token_supervised_all_examples: `True`
- padding_ignore_index_minus_100: `True`
- prompt_tokens_not_supervised_all_examples: `True`
- no_examples_without_assistant_labels: `True`

## Dataset-Level Counts

- train examples checked: 1500
- usable examples after fixed mask: 1500
- examples without assistant labels after fix: 0
- total supervised labels old: 27837
- total supervised labels new: 29337
- supervised labels gained: 1500

## Before / After Examples

### glyph100-sft-smoke-v0-0001 / anty_petle

Instruction: Nie rozwijaj bez końca: dlaczego warto mierzyć loss? Jednym zdaniem.

Response: Loss pokazuje, czy model uczy się przewidywać dane treningowe lub walidacyjne.

- old first supervised piece: `s`
- new first supervised piece: `▁Los`
- new first response supervised: `True`
- old supervised labels: `21`
- new supervised labels: `22`
- `<|end|>` supervised after fix: `True`
- prompt/user/instruction masked after fix: `True`
- first supervised sequence after fix: `▁Los s ▁pokazuje , ▁czy ▁model ▁uczy ▁się ▁przewi dy`

### glyph100-sft-smoke-v0-0003 / ostrozne_odpowiedzi_przy_niepewnosci

Instruction: Czy ta diagnoza jest pewna? Wskaż ograniczenie.

Response: Nie. Bez pełnych danych można mówić tylko o najbardziej prawdopodobnym wyjaśnieniu.

- old first supervised piece: `.`
- new first supervised piece: `▁Nie`
- new first response supervised: `True`
- old supervised labels: `19`
- new supervised labels: `20`
- `<|end|>` supervised after fix: `True`
- prompt/user/instruction masked after fix: `True`
- first supervised sequence after fix: `▁Nie . ▁Bez ▁peł nych ▁danych ▁można ▁mówić ▁tylko ▁o`

### glyph100-sft-smoke-v0-0002 / krotkie_poprawki_tekstu

Instruction: Popraw tekst: Projekt może być ciekawy, ale obecnie ma zbyt wiele funkcji planowanych na start.

Response: Projekt jest ciekawy, ale ma zbyt szeroki zakres na start.

- old first supervised piece: `▁jest`
- new first supervised piece: `▁Projekt`
- new first response supervised: `True`
- old supervised labels: `13`
- new supervised labels: `14`
- `<|end|>` supervised after fix: `True`
- prompt/user/instruction masked after fix: `True`
- first supervised sequence after fix: `▁Projekt ▁jest ▁ciekawy , ▁ale ▁ma ▁zbyt ▁szeroki ▁zakres ▁na`

### glyph100-sft-smoke-v0-0004 / anty_petle

Instruction: Odpowiedz jednym akapitem: czy warto lać wodę, żeby odpowiedź wyglądała mądrzej?

Response: Nie. Lepsza jest krótka, konkretna odpowiedź niż długi tekst bez treści.

- old first supervised piece: `.`
- new first supervised piece: `▁Nie`
- new first response supervised: `True`
- old supervised labels: `19`
- new supervised labels: `20`
- `<|end|>` supervised after fix: `True`
- prompt/user/instruction masked after fix: `True`
- first supervised sequence after fix: `▁Nie . ▁Le p sza ▁jest ▁kró tka , ▁konkre`

### glyph100-sft-smoke-v0-0005 / krotkie_poprawki_tekstu

Instruction: Usuń lanie wody: Warto byłoby dokonać porównania kilku wariantów.

Response: Warto porównać kilka wariantów.

- old first supervised piece: `▁porówna`
- new first supervised piece: `▁Warto`
- new first response supervised: `True`
- old supervised labels: `8`
- new supervised labels: `9`
- `<|end|>` supervised after fix: `True`
- prompt/user/instruction masked after fix: `True`
- first supervised sequence after fix: `▁Warto ▁porówna ć ▁kilka ▁warian tów . ▁ <|end|>`

## Previous SFT Smoke Status

The previous SFT smoke run is marked invalid-for-quality because it trained with the label mask off-by-one bug.
Its checkpoints and reports are preserved, but quality conclusions from that run should not be used as evidence against SFT.
