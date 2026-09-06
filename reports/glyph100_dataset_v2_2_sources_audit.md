# Glyph-100M Dataset v2.2 Sources Audit

Generated: 2026-06-01

No training was started. This is a source audit for a possible `glyph100_dataset_v2_2`.

## Current Problem

`glyph100_dataset_v2_1` is clean but too Wikipedia-heavy:

| source | tokens | share |
|---|---:|---:|
| Wikipedia PL | 127,929,637 | ~95.3% |
| Wolne Lektury | 3,143,341 | ~2.3% |
| Wikisource PL | 3,115,955 | ~2.3% |
| legacy | 0 | 0% |
| total | 134,188,933 | 100% |

For stage 3 / 50k total, the model would see 819,200,000 tokens, which is about 6.10 epochs over v2.1. That is too many repeated passes over a very wiki-shaped corpus.

## Source Candidates

| source | URL / location | size / access | sample quality | decision |
|---|---|---:|---|---|
| FinetextPL-Edu | https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu | gated, 490 parquet files, ~283 GB data files by HF metadata | not sampled, access denied without HF auth/approval | later / likely best large source after manual access |
| Wolne Lektury | local `data/raw/wolnelektury_cache.json`; API https://wolnelektury.pl/api/books/ | local 7,469 books; API currently 7,473 | good literary text, but current token yield only ~3.1M | use, but little growth left |
| Wikisource PL | https://huggingface.co/datasets/wikimedia/wikisource config `20231201.pl` | small; already used | mixed: real source texts plus indexes/disambiguation/legal/Bible/metadata pages | use only after stricter cleanup |
| Wikibooks PL | https://dumps.wikimedia.org/plwikibooks/latest/ | `pages-articles.xml.bz2` ~20.2 MB | useful educational/tutorial text, but wikitext cleanup needed | use |
| Allegro Polish Summaries Corpus | https://huggingface.co/datasets/allegro/summarization-polish-summaries-corpus | ~21.7k rows, ~271 MB data files | good long Polish article/news/legal/business text; not instruction data if using `source` only | use as article source |
| adamo1139/finePDFs-pol | https://huggingface.co/datasets/adamo1139/finePDFs-pol | public, ~55 GB parquet files | first samples were schedules, tables, rajd results; noisy OCR/table residue | later/reject for v2.2 unless heavily filtered |
| HuggingFaceFW/finepdfs-edu | https://huggingface.co/datasets/HuggingFaceFW/finepdfs-edu | public but huge, ~735 GB data files; includes `pl` language | likely useful, but too large for this step without controlled slicing | later |
| NKJP1M | https://huggingface.co/datasets/ipipan/nkjp1m | small, official 1M-token balanced corpus, CC-BY-4.0 | high-quality, but loader uses deprecated dataset script; small token gain | later/use if loader adapted |
| ipipan/polqa | https://huggingface.co/datasets/ipipan/polqa | ~3.4 GB files | QA/retrieval passages; likely Wikipedia-like and task-shaped | later, not first-choice pretraining |
| ipipan/maupqa | https://huggingface.co/datasets/ipipan/maupqa | ~3.6 GB files | QA/retrieval, includes machine-generated/found annotations | reject/later for base LM |
| CLARIN/KPWr NER | https://huggingface.co/datasets/clarin-pl/kpwr-ner | small annotated NER corpus, CC-BY-3.0 | useful linguistically, but annotated IOB format; small | reject for base LM unless raw text recovered |
| Polish Wikiquote | https://dumps.wikimedia.org/plwikiquote/latest/ | `pages-articles.xml.bz2` ~34.2 MB | quote lists, attribution markup; not continuous prose | reject for pretraining mix |

## Local / Online Checks Performed

- Wolne Lektury local cache: 7,469 items.
- Wolne Lektury API current list: 7,473 items.
- Wikibooks PL dump sampled in memory only: ~20.2 MB compressed.
- Wikibooks rough audit cleanup estimate: 7,671 accepted pages, ~9.39M Glyph tokenizer tokens.
- Allegro PSC streaming sample: 200 rows, average ~2,500 Glyph tokens per `source`, estimated ~54M tokens across all splits if using `source` text only.
- FinePDFs-pol first streamed samples looked table-heavy: rally classifications, training schedules, advisory schedules.
- No huge dataset was downloaded into the project.

## Practical Read

The realistic near-term v2.2 source mix is:

- keep Wikipedia, but cap its share,
- add Allegro PSC `source` articles,
- add cleaned Wikibooks PL,
- keep Wolne Lektury,
- keep a stricter subset of Wikisource,
- keep legacy at 0.

This can probably get v2.2 to roughly 190-200M tokens with Wikipedia around 65-70%. It will not solve all quality issues, but it should be substantially less wiki-shaped than v2.1 without reintroducing legacy web garbage.

For a stronger 50/50 mix or a long 100k/200k run, FinetextPL-Edu or another large clean source is still needed.
