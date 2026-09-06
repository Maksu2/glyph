# Glyph SFT v0 expanded seed dataset stats

File: `glyph_sft_v0_seed_1500_expanded.jsonl`

Generated examples: **1500**

Approx words: **78085**

Approx tokens: **~113223**

Average words/example: **52.1**

Min words/example: **33**

Max words/example: **78**

Exact duplicate instruction-response pairs: **0**

Exact category counts:

| category | examples | words | approx tokens |
|---|---:|---:|---:|
| codzienne_decyzje | 600 | 35000 | ~50750 |
| pisanie_i_streszczanie | 300 | 14894 | ~21596 |
| proste_wyjasnienia | 250 | 11633 | ~16868 |
| brak_danych | 150 | 7750 | ~11238 |
| korekta_zalozen | 100 | 4619 | ~6698 |
| techniczne_proste | 100 | 4189 | ~6074 |

Notes:
- Source is synthetic curated, not copied from public datasets.
- Final order is shuffled with seed 2026 inherited from the base seed file.
- This expanded file is closer to the intended SFT v0 size than the short seed file.
- Token count is an estimate from word count. Run the real Glyph tokenizer before training.
- The file is JSONL: one JSON object per line.
