# Glyph-100M Dataset v2 Inventory

Generated: 2026-05-31T20:32:20.257860+00:00

## Local Files

| path | size | modified |
|---|---:|---|
| `data/raw/corpus.txt` | 18.3 GB | 2026-03-31T17:08:14.528525+00:00 |
| `data/processed/corpus_clean.txt` | 18.0 GB | 2026-03-31T17:39:27.084306+00:00 |
| `data/processed/tokens.bin` | 9.6 GB | 2026-03-31T20:29:51.497880+00:00 |
| `data/processed/val_tokens.bin` | 95.4 MB | 2026-05-14T04:52:51.273493+00:00 |
| `data/processed/glyph100_train.bin` | 224.8 MB | 2026-05-26T05:28:33.822318+00:00 |
| `data/processed/glyph100_val.bin` | 2.4 MB | 2026-05-26T05:28:33.275315+00:00 |
| `data/processed/tokenizer.model` | 487.0 KB | 2026-03-31T18:11:39.630485+00:00 |
| `data/raw/wolnelektury_cache.json` | 5.0 MB | 2026-03-31T14:58:20.053401+00:00 |

## Corpus Counts

- raw corpus lines: 7,793,749
- cleaned corpus lines: 7,747,761
- current stage1 candidate train tokens: 117,870,679
- current stage1 candidate val tokens: 1,239,948

## Source Metadata Status

- `data/raw/corpus.txt`: monolithic one-document-per-line corpus; original source metadata not preserved per line
- `huggingface_wikipedia_cache`: source-aware id/url/title/text available through datasets cache
- `wolnelektury_cache`: book metadata list available; text must be fetched again or reconstructed from legacy corpus
- `glyph100_train.bin`: token-only; no source metadata retained

## Hugging Face Wikipedia Cache

- cached files: 7
- cached bytes: 2.7 GB
- load test confirmed `id`, `url`, `title`, `text` columns for `wikimedia/wikipedia 20231101.pl`.

## Decision

Use cached Wikipedia as true source-aware input, optional Wolne Lektury API fetch, and legacy_mixed_corpus only as filtered coarse source. Do not treat legacy corpus as final clean attribution.
