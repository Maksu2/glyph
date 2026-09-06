# Glyph-100M next dataset plan

Status: plan only. Do not run a heavy rebuild during training without a separate approval.

Update 2026-05-31: a first reproducible `glyph100_dataset_v2` candidate was built
under `data/processed/glyph100_v2_*`. It reaches the 300M-token minimum and
preserves source/doc metadata from ingest time, but manual sample review still
finds enough legacy web/forum/commerce residue that it is not automatically
approved for stage 3 / 50k. Treat it as a useful candidate and diagnostic
artifact, not the final long-run corpus.

## Goal

Build a source-aware Polish pretraining corpus for Glyph-100M before any 50k+ run. The current `glyph100_stage1_candidate` split is acceptable for stage 1/stage 2 sanity checks, but it is not a final long-training corpus.

The next corpus should optimize for:

- clean continuous Polish text,
- source and document traceability,
- document-level train/val split,
- less web/forum/SEO garbage than the 27M run,
- enough tokens to avoid excessive repeated epochs.

## Target Token Budget

With the current stage config:

- batch size: 4
- context length: 512
- gradient accumulation: 8
- effective tokens per optimizer step: 16,384

Training token budgets:

- 10k steps: 163.84M tokens
- 50k steps: 819.20M tokens
- 100k steps: 1.64B tokens
- 200k steps: 3.28B tokens

Recommendation:

- Stage 2 / 10k can use the current candidate if it is only an early-training check.
- Stage 3 / 50k should preferably use at least 500M-1B clean-ish train tokens.
- 100k/200k should not proceed on the current 117.9M-token candidate without accepting many repeated epochs and likely overfitting/style memorization.

## Source Plan

Use sources only after recording license/source metadata. This is a research/educational non-profit project, but the corpus should still be auditable.

| Source | Use | Why | Risks |
| --- | --- | --- | --- |
| Polish Wikipedia | yes | encyclopedic, continuous text, good baseline Polish | templates, tables, lists, boilerplate |
| Wolne Lektury | yes | long clean literary Polish, structured metadata | archaic style, duplicated editions, poems/dialogue formatting |
| OSCAR PL / mC4 PL | limited | scale and variety | web garbage, SEO, forums, menus, duplicates, PII |
| Polish educational/open articles | consider | good explanatory style | source-by-source license and quality review |
| Forums/comments/social text | mostly reject | conversational variety | signatures, usernames, dates, low quality, PII |
| Shops/classifieds/SEO pages | reject | little language-model value | product spam, boilerplate, duplicated snippets |
| SFT/instruction datasets | not for base pretraining | separate use case | can contaminate base model style |

## Metadata Schema

Every document/chunk should carry metadata before tokenization:

```json
{
  "source_id": "wikipedia_pl",
  "source_name": "Polish Wikipedia",
  "source_type": "encyclopedic",
  "license": "CC BY-SA",
  "doc_id": "stable-document-id-or-hash",
  "chunk_id": "doc-id:0003",
  "url": "optional-public-source-url",
  "title": "optional title",
  "text_sha256": "hash of cleaned text",
  "raw_chars": 12345,
  "clean_chars": 11234,
  "tokens": 2048,
  "filter_version": "glyph100-clean-v1",
  "accepted": true,
  "reject_reasons": []
}
```

Do not split train/val by chunk if chunks come from the same document. Split by `doc_id`.

## Pipeline Outline

1. Ingest each source into `data/glyph100_next/raw/<source>/`.
2. Normalize into JSONL documents with source metadata.
3. Clean text and compute quality metrics.
4. Reject low-quality documents and write rejected examples with reasons.
5. Deduplicate exact text by SHA256.
6. Run near-duplicate filtering before train/val split.
7. Split by document, stratified by source.
8. Chunk/tokenize with the existing SentencePiece tokenizer.
9. Write distinct outputs, not replacing old 27M or stage1 files:
   - `data/processed/glyph100_next_train.bin`
   - `data/processed/glyph100_next_val.bin`
   - `data/processed/glyph100_next_metadata.json`
10. Generate reports and samples before approving 50k+.

## Quality Filters

Recommended document-level metrics:

- alphabetic character ratio,
- Polish character/word ratio,
- control character count,
- URL/domain count,
- HTML tag residue count,
- average and max line length,
- repeated line ratio,
- repeated n-gram score,
- punctuation/symbol ratio,
- numeric-heavy ratio,
- boilerplate phrase hits,
- duplicate hash,
- near-duplicate cluster id.

Reject or heavily downweight text containing repeated patterns like:

- `czytaj więcej`,
- `strona główna`,
- `zobacz także` outside encyclopedia structure,
- navigation menus,
- cookie banners,
- newsletter/footer text,
- usernames/signatures/dates from forum posts,
- link lists,
- product grids,
- SEO keyword stuffing,
- long sequences of punctuation or random symbols.

## Leakage Avoidance

Train/val leakage prevention:

- assign split at `doc_id`, not `chunk_id`,
- perform near-duplicate detection before splitting,
- keep all chunks from a document in one split,
- keep all duplicate/near-duplicate documents in one split or reject duplicates,
- store `doc_id`, `source_id`, and split in metadata,
- generate a leakage report showing duplicate hashes and near-duplicate clusters across train/val.

## Validation Split

Target:

- val: 0.5-1.0% of tokens or a fixed representative cap,
- source-stratified,
- document-level,
- no document chunk leakage.

The validation set should include all major source types, but it should not be polluted with rejected/low-quality documents.

## Reports Required Before 50k+

Write:

- `data/reports/glyph100_next_dataset_report.md`
- `data/reports/glyph100_next_dataset_stats.json`
- `data/reports/glyph100_next_accepted_samples.md`
- `data/reports/glyph100_next_rejected_samples.md`
- `data/reports/glyph100_next_random_samples.md`
- `data/reports/glyph100_next_leakage_report.md`

The report should include:

- source table with license and decision,
- documents before/after filtering per source,
- tokens before/after filtering per source,
- reject reasons and counts,
- accepted/rejected/random sample snippets,
- token/word ratio,
- train/val split summary,
- duplicate and near-duplicate summary,
- final recommendation: ready for 50k, needs fixes, or do not use.

## Decision Gates

Do not start stage 3 / 50k until:

- source-aware metadata exists,
- train/val split is document-level,
- leakage report is clean or explained,
- rejected/accepted samples have been reviewed,
- the corpus is large enough for the chosen step count,
- the dashboard/public site clearly labels which dataset is active.

## Minimal Scripts To Prepare

These are safe to write later without running the heavy pipeline:

- `scripts/glyph100_ingest_sources.py`
- `scripts/glyph100_clean_docs.py`
- `scripts/glyph100_dedup.py`
- `scripts/glyph100_split_tokenize.py`
- `scripts/glyph100_dataset_report.py`

Each script should support a dry-run/sample mode first.
