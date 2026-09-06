# Glyph-100M v2.4.1 Independent Validation

Generated: 2026-07-16T07:18:11.592558+00:00

## Verdict

PASS: v2.4.1 is mechanically valid and ready for a controlled 1k/5k proxy, not an automatic long run.

## Checks

- PASS: metadata token total matches docs JSONL
- PASS: metadata train tokens match docs JSONL
- PASS: metadata val tokens match docs JSONL
- PASS: train binary byte size equals uint16 token count
- PASS: val binary byte size equals uint16 token count
- PASS: metadata document count matches docs JSONL
- PASS: document IDs are unique
- PASS: parent documents do not cross train and val
- PASS: minimum token floor is met

## Independently Observed

- docs: 201,746
- parent docs: 193,129
- tokens: 279,496,401
- train tokens: 278,089,665
- validation tokens: 1,406,736
- duplicate IDs: 0
- parent split leakage: 0
- web-residue heuristic hits: 1,638
- wiki-markup heuristic hits: 149
- pseudo-ency phrase hits: 30,121

Heuristic hits by source:

```json
{
  "1000_novels": {
    "pseudo_ency_phrase": 210,
    "wiki_markup": 7
  },
  "eltec_pol": {
    "pseudo_ency_phrase": 101,
    "wiki_markup": 1
  },
  "parliamentary": {
    "pseudo_ency_phrase": 1134,
    "wiki_markup": 1
  },
  "wikibooks": {
    "pseudo_ency_phrase": 16
  },
  "wikinews": {
    "pseudo_ency_phrase": 140
  },
  "wikipedia_pl": {
    "web_residue": 1638,
    "pseudo_ency_phrase": 27925,
    "wiki_markup": 139
  },
  "wikisource": {
    "pseudo_ency_phrase": 260
  },
  "wolne_lektury": {
    "pseudo_ency_phrase": 335,
    "wiki_markup": 1
  }
}
```

| source | docs | tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
| `1000_novels` | 2,776 | 30,196,490 | 10.8% | 30,010,275 | 186,215 |
| `eltec_pol` | 1,058 | 13,841,376 | 5.0% | 13,706,531 | 134,845 |
| `parliamentary` | 11,575 | 23,852,526 | 8.5% | 23,689,194 | 163,332 |
| `wikibooks` | 4,286 | 3,772,313 | 1.3% | 3,752,725 | 19,588 |
| `wikinews` | 8,378 | 2,745,045 | 1.0% | 2,731,314 | 13,731 |
| `wikipedia_pl` | 132,712 | 120,003,040 | 42.9% | 119,402,887 | 600,153 |
| `wikisource` | 33,787 | 30,048,511 | 10.8% | 30,048,511 | 0 |
| `wolne_lektury` | 7,174 | 55,037,100 | 19.7% | 54,748,228 | 288,872 |

## Interpretation

The residue counters are conservative search heuristics, not automatic quality failures. Every matching sample is retained in the JSON audit for manual inspection. Binary sizes, metadata counts and the parent split are hard gates.
