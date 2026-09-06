# Glyph SFT v0 dataset validation

## glyph_sft_v0_seed_1500.jsonl

- examples: 1500
- invalid JSON lines: 0
- records with missing fields: 0
- total words: 51500
- avg instruction words: 9.4
- avg response words: 25.0
- duplicate instructions, extra copies: 782
- duplicate instruction+response pairs, extra copies: 0
- real tokenizer template tokens: 90272
- template tokens avg/p50/p90/p95/max: 60.2 / 63.0 / 72.0 / 74.0 / 101
- fits context 256: 1500
- over context 256: 0

### Categories

- codzienne_decyzje: 600
- pisanie_i_streszczanie: 300
- proste_wyjasnienia: 250
- brak_danych: 150
- korekta_zalozen: 100
- techniczne_proste: 100

### Bad-pattern checks

- empty_instruction: 0
- empty_response: 0
- very_short_response_lt_8_words: 27
- very_long_response_gt_120_words: 0
- control_chars: 0
- as_language_model_phrase: 0
- english_pattern: 0

## glyph_sft_v0_seed_1500_expanded.jsonl

- examples: 1500
- invalid JSON lines: 0
- records with missing fields: 0
- total words: 78085
- avg instruction words: 9.4
- avg response words: 42.7
- duplicate instructions, extra copies: 782
- duplicate instruction+response pairs, extra copies: 0
- real tokenizer template tokens: 130803
- template tokens avg/p50/p90/p95/max: 87.2 / 89.0 / 99.0 / 102.0 / 124
- fits context 256: 1500
- over context 256: 0

### Categories

- codzienne_decyzje: 600
- pisanie_i_streszczanie: 300
- proste_wyjasnienia: 250
- brak_danych: 150
- korekta_zalozen: 100
- techniczne_proste: 100

### Bad-pattern checks

- empty_instruction: 0
- empty_response: 0
- very_short_response_lt_8_words: 0
- very_long_response_gt_120_words: 0
- control_chars: 0
- as_language_model_phrase: 0
- english_pattern: 0
