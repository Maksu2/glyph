# Glyph-100M Dataset v2.4.1 Core Report

Generated: 2026-07-16T07:03:46.945869+00:00

## Decision

READY FOR CONTROLLED 1K/5K PROXY: v2.4.1 clears the token floor without web crawl data, keeps Wikipedia below 45%, and preserves a leakage-free validation set.

No training was started.

## Result

- total tokens: 279,496,401
- train tokens: 278,089,665
- validation tokens: 1,406,736
- total documents/chunks: 201,746
- parent leakage: 0
- Wikipedia share: 42.9%
- literature share: 46.2%
- parliamentary share: 8.5%
- Wikisource supplement: 30,048,511 tokens (10.8%)

| source | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|
| `wikipedia_pl` | 120,003,040 | 42.9% | 119,402,887 | 600,153 |
| `wolne_lektury` | 55,037,100 | 19.7% | 54,748,228 | 288,872 |
| `1000_novels` | 30,196,490 | 10.8% | 30,010,275 | 186,215 |
| `eltec_pol` | 13,841,376 | 5.0% | 13,706,531 | 134,845 |
| `parliamentary` | 23,852,526 | 8.5% | 23,689,194 | 163,332 |
| `wikibooks` | 3,772,313 | 1.3% | 3,752,725 | 19,588 |
| `wikinews` | 2,745,045 | 1.0% | 2,731,314 | 13,731 |
| `wikisource` | 30,048,511 | 10.8% | 30,048,511 | 0 |

## Wikisource Split Policy

The upstream rows lack a reliable parent-work title. All supplement rows are therefore train-only. This is conservative: validation cannot contain another fragment of the same unknown work, and the limitation remains explicit in metadata.

## Training Math

- 1k steps: 16,384,000 tokens = 0.06 corpus passes
- 5k steps: 81,920,000 tokens = 0.29 corpus passes
- 20k steps: 327,680,000 tokens = 1.18 corpus passes
- 50k steps: 819,200,000 tokens = 2.95 corpus passes

## Gate

This corpus is approved only for a from-scratch 1k stability run followed by a 5k matched-exposure proxy. A longer run still requires a separate quality comparison and approval.
