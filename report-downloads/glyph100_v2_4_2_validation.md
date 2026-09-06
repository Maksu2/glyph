# Glyph-100M v2.4.2 Independent Validation

Generated: 2026-07-18T04:57:38.540643+00:00

## Verdict

PASS: v2.4.2 is mechanically and compositionally ready for one fresh 5k matched proxy.

## Hard Checks

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

## Observed Corpus

- documents: 159,579
- parent documents: 151,981
- train tokens: 231,494,339
- validation tokens: 1,176,728
- total tokens: 232,671,067
- literature share: 54.39%
- Wikipedia share: 40.83%
- parliamentary share: 2.58%
- duplicate IDs: 0
- exact text duplicates: 0
- normalized text duplicates: 0
- parent leakage: 0
- residual rejected-pattern documents: 0

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
| `1000_novels` | 2,767 | 30,091,693 | 12.93% | 29,905,478 | 186,215 |
| `eltec_pol` | 1,057 | 13,827,409 | 5.94% | 13,692,564 | 134,845 |
| `parliamentary` | 6,226 | 6,010,376 | 2.58% | 5,966,996 | 43,380 |
| `wikibooks` | 4,068 | 3,608,515 | 1.55% | 3,588,927 | 19,588 |
| `wikinews` | 4,544 | 1,500,066 | 0.64% | 1,492,984 | 7,082 |
| `wikipedia_pl` | 100,721 | 95,000,929 | 40.83% | 94,504,183 | 496,746 |
| `wikisource` | 33,023 | 27,607,311 | 11.87% | 27,607,311 | 0 |
| `wolne_lektury` | 7,173 | 55,024,768 | 23.65% | 54,735,896 | 288,872 |

## Residual Pattern Audit

```json
{}
```

The JSON companion contains 50 deterministic global samples, source-balanced samples and every residual pattern category found by the audit.
