# Glyph-100M Dataset v2.3 Plan

Generated: 2026-06-01

No training was started. No stage 3, SFT, tokenizer training, or full dataset download was started.

## Why v2.3 Exists

`glyph100_dataset_v2_2` is cleaner and source-aware, but too small:

- v2.2 total: ~37.0M Glyph tokenizer tokens
- stage 3 / 50k total: 819.2M tokens
- implied epochs: ~22.1

That is too many repeated passes for a sensible 50k continuation. The next dataset needs a large clean non-Wikipedia source.

## Primary Candidate: FinetextPL-Edu

- dataset: `FinetextPL/FinetextPL-Edu`
- URL: https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu
- access: gated/manual
- size: ~263.7 GiB parquet data by Hugging Face metadata
- claimed docs: ~160M Polish documents
- sources: FineWeb2 + FinePDFs
- pretraining field: `text`
- quality field: `prediction`
- source field: `dataset_source`
- recommended first filter from dataset card: `prediction >= 2.5`
- license tag: `odc-by`

Current status: access is not available in this environment. The bounded probe failed with:

```text
DatasetNotFoundError: Dataset 'FinetextPL/FinetextPL-Edu' is a gated dataset on the Hub. You must be authenticated to access it.
```

## Safe Access Workflow

1. Open https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu.
2. Log in to Hugging Face.
3. Read and accept the gated dataset terms.
4. On the homelab, use one of:

```bash
huggingface-cli login
```

or for one command only:

```bash
HF_TOKEN=... ./.venv/bin/python scripts/glyph100_finetext_probe.py --max-raw-docs 10000 --max-accepted-docs 1000
```

Do not write the token into repo files. Do not commit it. Do not put it in `.env` unless that file is explicitly outside versioned/project-visible data and you accept the risk.

## Probe Before Any Build

First command after access:

```bash
cd /home/maksu/ai-model
./.venv/bin/python scripts/glyph100_finetext_probe.py \
  --max-raw-docs 10000 \
  --max-accepted-docs 1000 \
  --min-prediction 2.5
```

If that looks good, second bounded probe:

```bash
./.venv/bin/python scripts/glyph100_finetext_probe.py \
  --max-raw-docs 100000 \
  --max-accepted-docs 10000 \
  --min-prediction 2.5
```

Only after those reports should a v2.3 build be approved.

## Finetext Filters

Use Finetext as promising but not automatically clean. Apply:

- `prediction >= 2.5` initially
- HTML removal / rejection
- URL spam rejection
- menu/navigation/boilerplate rejection
- link-list rejection
- forum/comment rejection
- commerce/price/shop rejection
- table/admin-heavy rejection
- very short document rejection
- very long noisy-line rejection
- low alphabetic ratio rejection
- low Polish signal rejection
- repetition score rejection
- exact duplicate rejection
- near duplicate rejection against v2.2 and within Finetext
- FinePDFs-specific: reject low `full_doc_lid_score`, reject `is_truncated` at first

Preserve metadata:

- `id`
- `dataset_source`
- `prediction`
- `file_path`
- `url`
- `date`
- `dump`
- `offset`
- `full_doc_lid`
- `full_doc_lid_score`
- `is_truncated`
- `minhash_cluster_size`

## Variant A: 300M, Wikipedia Max 50%

Target:

| source | tokens |
|---|---:|
| Wikipedia PL | 150M |
| FinetextPL-Edu filtered | 130M |
| Wolne/Wikisource/Wikibooks/Allegro | 20M |
| total | 300M |

Stage 3 / 50k epochs: `819.2M / 300M = 2.73`.

Recommendation: first realistic v2.3 target if Finetext samples look good.

## Variant B: 500M, Wikipedia Max 40%

Target:

| source | tokens |
|---|---:|
| Wikipedia PL | 200M |
| FinetextPL-Edu filtered | 275M |
| books/source texts/other | 25M |
| total | 500M |

Stage 3 / 50k epochs: `819.2M / 500M = 1.64`.

Recommendation: best shape for a longer run, but only after larger bounded probe and storage/time planning.

## Variant C: 200-300M Quality-First

Target:

| source | tokens |
|---|---:|
| Wikipedia PL | 80-120M |
| FinetextPL-Edu high-score subset | 100-150M |
| books/source texts | 20-30M |
| total | 200-300M |

Stage 3 / 50k epochs:

- 200M: `4.10`
- 250M: `3.28`
- 300M: `2.73`

Recommendation: use if Finetext samples are uneven and `prediction >= 2.5` still lets too much web/PDF residue through. Consider raising threshold to `prediction >= 3.0`.

## Variant D: No Finetext

If access fails:

- do not run stage 3 / 50k on v2.2
- keep v2.2 as a clean small audit dataset
- only consider a short v2.1/v2.2 preflight, not a real 50k stage

Stage 3 / 50k on v2.2 would be ~22 epochs, so it is not recommended.

## Decision Gate

Do not build `glyph100_dataset_v2_3` until:

1. Finetext access is accepted manually.
2. `scripts/glyph100_finetext_probe.py` collects at least 1k accepted samples.
3. Accepted/rejected samples are reviewed.
4. Token/doc stats look sane.
5. No dominant HTML/forum/commerce/admin-table residue appears.
6. A bounded build size is approved explicitly.

## Current Recommendation

A) Obtain access to FinetextPL-Edu and rerun the bounded probe. If sample quality passes, build v2.3 Variant A first.

No training should start before v2.3 quality is known.
