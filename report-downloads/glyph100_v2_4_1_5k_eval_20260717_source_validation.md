# Glyph-100M v2.4.1 source-specific validation

| source | docs | tokens | 1k val loss | 5k val loss | delta |
|---|---:|---:|---:|---:|---:|
| 1000_novels | 17 | 186,215 | 6.1635 | 4.7146 | -1.4489 |
| eltec_pol | 10 | 134,845 | 6.0083 | 4.5009 | -1.5074 |
| parliamentary | 78 | 163,332 | 6.4505 | 4.3750 | -2.0754 |
| wikibooks | 26 | 19,588 | 7.0727 | 5.2204 | -1.8523 |
| wikinews | 45 | 13,731 | 7.0261 | 5.1516 | -1.8745 |
| wikipedia_pl | 647 | 600,153 | 6.7542 | 4.6365 | -2.1176 |
| wolne_lektury | 49 | 288,872 | 6.0762 | 4.5322 | -1.5440 |

Negative deltas mean improvement at 5k. Wikisource is train-only in v2.4.1, so it has no source-specific validation result.
