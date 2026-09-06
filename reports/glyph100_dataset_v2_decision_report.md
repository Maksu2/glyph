# Glyph-100M Dataset v2 Decision Report

Generated: 2026-05-31T23:17:30.085613+00:00

## Verdict

B: do not approve stage 3 yet; improve/reduce legacy_mixed_corpus or add cleaner source-aware data first.

## Why

The v2 rebuild is source-aware and reaches 300M tokens, but manual sample review still finds accepted legacy_mixed_corpus rows that look like web listings, forums, ads, travel/product pages and other non-neutral pages. This is cleaner than glyph100_stage1_candidate and useful as a reproducible candidate, but I do not recommend approving stage 3 / 50k on it without either reducing legacy_mixed_corpus or adding cleaner source-aware data such as audited educational corpora.

## Dataset v2

- train tokens: 298,401,324
- val tokens: 1,598,783
- total tokens: 300,000,107
- train docs: 468,549
- val docs: 2,395
- source-aware JSONL: `data/processed/glyph100_v2_docs.jsonl`
- train bin: `data/processed/glyph100_v2_train.bin`
- val bin: `data/processed/glyph100_v2_val.bin`

## Source Mix

| source | accepted docs | train tokens | val tokens | acceptance |
|---|---:|---:|---:|---:|
| `wolne_lektury` | 1,525 | 3,128,722 | 14,619 | 98.77% |
| `wikipedia_pl` | 184,467 | 127,170,087 | 759,638 | 73.79% |
| `legacy_mixed_corpus` | 284,952 | 168,102,515 | 824,526 | 34.66% |

## Training Math

- 50k total consumes 819,200,000 tokens: 2.73 epochs over v2.
- 100k total consumes 1,638,400,000 tokens: 5.46 epochs over v2.
- 200k total consumes 3,276,800,000 tokens: 10.92 epochs over v2.

## Decision

Do not start stage 3 automatically. The dataset is reproducible and larger than `glyph100_stage1_candidate`, but still not clean enough to call the long-run corpus. Next best step: either rebuild v2 with stricter legacy filtering and/or add a cleaner audited educational source before 50k.

## Related Reports

- `data/reports/glyph100_dataset_v2_inventory.md`
- `data/reports/glyph100_dataset_v2_report.md`
- `data/reports/glyph100_dataset_v2_quality_audit.md`
- `reports/glyph100_dataset_v2_cleanup_proposal.md`
