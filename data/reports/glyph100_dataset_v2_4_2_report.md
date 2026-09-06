# Glyph-100M Dataset v2.4.2 Core Report

Generated: 2026-07-18T04:50:25.580112+00:00

## Decision

READY FOR INDEPENDENT VALIDATION AND A FRESH 5K PROXY: all source-mix, residue, split, dedup and tokenizer gates passed.

This build does not overwrite v2.4.1. It removes strong Wikipedia locality/demography templates, caps parliamentary text and keeps only already source-aware, non-web-crawl material.

## Hard Gates

- PASS: minimum token floor
- PASS: literature share
- PASS: Wikipedia share
- PASS: parliamentary share
- PASS: web residue
- PASS: strong locality templates
- PASS: parent split leakage
- PASS: duplicate IDs
- PASS: exact text duplicates
- PASS: normalized text duplicates
- PASS: tokenizer checksum

## Corpus

- total tokens: 232,671,067
- train tokens: 231,494,339
- validation tokens: 1,176,728
- documents/chunks: 159,579
- parent leakage: 0
- duplicate IDs: 0
- literature share: 54.39%
- Wikipedia share: 40.83%
- parliamentary share: 2.58%
- web residue documents: 0
- strong locality-template documents: 0

| source | v2.4.1 tokens | v2.4.2 tokens | share | train tokens | val tokens |
|---|---:|---:|---:|---:|---:|
| `1000_novels` | 30,196,490 | 30,091,693 | 12.9% | 29,905,478 | 186,215 |
| `eltec_pol` | 13,841,376 | 13,827,409 | 5.9% | 13,692,564 | 134,845 |
| `parliamentary` | 23,852,526 | 6,010,376 | 2.6% | 5,966,996 | 43,380 |
| `wikibooks` | 3,772,313 | 3,608,515 | 1.6% | 3,588,927 | 19,588 |
| `wikinews` | 2,745,045 | 1,500,066 | 0.6% | 1,492,984 | 7,082 |
| `wikipedia_pl` | 120,003,040 | 95,000,929 | 40.8% | 94,504,183 | 496,746 |
| `wikisource` | 30,048,511 | 27,607,311 | 11.9% | 27,607,311 | 0 |
| `wolne_lektury` | 55,037,100 | 55,024,768 | 23.6% | 54,735,896 | 288,872 |

## Removed Patterns

```json
{
  "wiki_1975_1998_template": 21888,
  "wiki_locality_administrative_lead": 19749,
  "wiki_locality_template_cluster": 5669,
  "wiki_surface_template": 4209,
  "wiki_admin_template": 3977,
  "wiki_population_template": 3656,
  "web_residue_pattern": 1638,
  "wiki_register_template": 1621,
  "parliamentary_legal_citation_heavy": 1297,
  "wikisource_page_header_ocr": 764,
  "wiki_media_residue": 759,
  "wiki_markup_residue": 149,
  "wikibooks_link_list_heavy": 27,
  "source_metadata_preamble": 2
}
```

## Training Budget

- 5k proxy: 81,920,000 tokens = 0.354 train-corpus passes
- 10k: 163,840,000 tokens = 0.708 train-corpus passes

## Scope

The only approved automatic run after independent validation is a fresh, matched-config 5k proxy. A continuation beyond 5k requires checkpoint evaluation against v2.4.1 at equal exposure.
