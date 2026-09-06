# Glyph-100M v2.4.1 source validation at 10k

| source | docs | tokens | 5k | 7.5k | 10k | 10k - 5k |
|---|---:|---:|---:|---:|---:|---:|
| 1000_novels | 17 | 186,215 | 4.7146 | 4.5191 | 4.3510 | -0.3637 |
| eltec_pol | 10 | 134,845 | 4.5009 | 4.2875 | 4.1103 | -0.3906 |
| parliamentary | 78 | 163,332 | 4.3750 | 4.1157 | 3.9115 | -0.4635 |
| wikibooks | 26 | 19,588 | 5.2204 | 4.8792 | 4.6204 | -0.6000 |
| wikinews | 45 | 13,731 | 5.1516 | 4.8521 | 4.6269 | -0.5247 |
| wikipedia_pl | 647 | 600,153 | 4.6365 | 4.2973 | 4.0440 | -0.5925 |
| wolne_lektury | 49 | 288,872 | 4.5322 | 4.3061 | 4.1414 | -0.3908 |

Negative deltas mean improvement. Wikisource remains train-only because
the upstream data does not preserve a safe parent-work split.
