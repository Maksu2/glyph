# Glyph-100M Dataset v2.4 Core Report

Generated: 2026-07-16T06:43:07.191636+00:00

## Decision

NOT READY: the core corpus missed the minimum token target or parent split gate; inspect source shortfalls before training.

No training was started. FineWeb2, HPLT, legacy and gated FinetextPL-Edu are not part of this build.

## Corpus

- total tokens: 249,447,890
- train tokens: 248,041,154
- validation tokens: 1,406,736
- documents/chunks: 167,959
- parent documents: 160,555
- parent leakage: 0
- token/word ratio: 1.920
- target reached: False

| source | upstream rows seen | selected chunks | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|---:|
| `wikipedia_pl` | 184,466 | 132,712 | 120,003,040 | 48.1% | 119,402,887 | 600,153 |
| `wolne_lektury` | 6,141 | 7,174 | 55,037,100 | 22.1% | 54,748,228 | 288,872 |
| `1000_novels` | 1,000 | 2,776 | 30,196,490 | 12.1% | 30,010,275 | 186,215 |
| `eltec_pol` | 100 | 1,058 | 13,841,376 | 5.5% | 13,706,531 | 134,845 |
| `parliamentary` | 324,622 | 11,575 | 23,852,526 | 9.6% | 23,689,194 | 163,332 |
| `wikibooks` | 9,112 | 4,286 | 3,772,313 | 1.5% | 3,752,725 | 19,588 |
| `wikinews` | 24,386 | 8,378 | 2,745,045 | 1.1% | 2,731,314 | 13,731 |

## Training Budget

At batch 4, context 512 and gradient accumulation 8, one optimizer step is 16,384 tokens.

| optimizer steps | tokens | train-corpus passes | estimated RX 5500 XT time |
|---:|---:|---:|---:|
| 1,000 | 16,384,000 | 0.07 | 1.4 h |
| 5,000 | 81,920,000 | 0.33 | 7.0 h |
| 20,000 | 327,680,000 | 1.32 | 28.1 h |
| 40,000 | 655,360,000 | 2.64 | 56.2 h |
| 50,000 | 819,200,000 | 3.30 | 70.2 h |

## Quality Gates

- deterministic source quotas and parent-level selection
- source-stratified parent-document validation split
- exact, normalized and practical near-duplicate rejection
- source-specific cleanup for literature, parliamentary records, Wikibooks and Wikinews
- real Glyph SentencePiece tokenizer used for every token count
- no web crawl source in the core build

## Top Rejection Reasons

```json
{
  "too_short": 60288,
  "repeated_ngrams": 13400,
  "wiki_markup_residue": 12653,
  "web_residue_pattern": 2528,
  "single_word_repetition": 1296,
  "too_many_urls": 1253,
  "near_duplicate": 816,
  "price_or_currency_heavy": 736,
  "normalized_duplicate": 503,
  "exact_duplicate": 430,
  "low_unique_word_ratio": 411,
  "very_long_line": 290,
  "too_much_punctuation_or_symbols": 254,
  "low_alpha_ratio": 192,
  "parliamentary_question_list_heavy": 181,
  "commerce_patterns": 96,
  "html_present": 70,
  "forum_patterns": 42,
  "too_many_boilerplate_patterns": 42,
  "low_polish_signal": 2,
  "empty_after_clean": 1
}
```

## Risks

- Literature is intentionally prominent; it improves continuous Polish but includes older style.
- Parliamentary text is capped and should not be allowed to dominate later builds.
- Wikibooks/Wikinews remain small because markup and short-page filters are strict.
- This corpus supports a staged from-scratch proxy run, not an automatic long training approval.
