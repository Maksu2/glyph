# Glyph-100M v2.4.2 Readiness Decision

Generated: 2026-07-18T04:59:18.843384+00:00

## Decision

**APPROVE fresh 0→5k proxy**

v2.4.2 passed the builder gates, an independent full-document validation pass and a manual source-balanced sample review. The approval covers only a fresh matched-config run to 5,000 optimizer steps. It does not approve 10k or a long training run.

## Result

- total tokens: 232,671,067
- train / val: 231,494,339 / 1,176,728
- documents: 159,579
- literature share: 54.39%
- Wikipedia share: 40.83%
- parliamentary share: 2.58%
- parent leakage: 0
- duplicate IDs / exact / normalized: 0 / 0 / 0
- residual blocked-pattern documents: 0

| source | v2.4.1 tokens | v2.4.2 tokens | v2.4.2 share |
|---|---:|---:|---:|
| `1000_novels` | 30,196,490 | 30,091,693 | 12.93% |
| `eltec_pol` | 13,841,376 | 13,827,409 | 5.94% |
| `parliamentary` | 23,852,526 | 6,010,376 | 2.58% |
| `wikibooks` | 3,772,313 | 3,608,515 | 1.55% |
| `wikinews` | 2,745,045 | 1,500,066 | 0.64% |
| `wikipedia_pl` | 120,003,040 | 95,000,929 | 40.83% |
| `wikisource` | 30,048,511 | 27,607,311 | 11.87% |
| `wolne_lektury` | 55,037,100 | 55,024,768 | 23.65% |

## Independent Checks

- PASS: dataset identity
- PASS: metadata total matches docs
- PASS: metadata train matches docs
- PASS: metadata val matches docs
- PASS: metadata docs match
- PASS: train binary size
- PASS: validation binary size
- PASS: tokenizer checksum
- PASS: minimum token floor
- PASS: literature share
- PASS: Wikipedia share
- PASS: parliamentary share
- PASS: unique document IDs
- PASS: no exact duplicates
- PASS: no normalized duplicates
- PASS: no parent leakage
- PASS: no residual rejected patterns
- PASS: builder gates passed
- PASS: all validation sources represented
- PASS: Wikisource remains train-only

## Manual Gate

The first automatic PASS was deliberately rejected after samples exposed source metadata and wiki-media residue. Filters were tightened and the corpus was rebuilt. The final sample audit found no remaining blocking pattern among the inspected source-balanced samples.

Known risks remain explicit: older literary spelling, train-only Wikisource, and a small parliamentary component. The 5k proxy must prove that the corrected source mix improves generation at equal exposure.

## Approved Run

- launcher: `scripts/run_glyph100_v242_5k.sh`
- checkpoint directory: `checkpoints/glyph-100m-v2_4_2-5k`
- log directory: `logs/glyph-100m-v2_4_2-5k`
- fresh initialization, no resume
- batch 4, accumulation 8, context 512
- 5k exposure: 81,920,000 tokens (0.354 corpus passes)
- stop at 5k for matched evaluation against v2.4.1
