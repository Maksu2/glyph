# Glyph-100M FinetextPL-Edu Access Check

Generated: 2026-06-02T04:35:19.437370+00:00

No training was started. No full dataset download was started. No Hugging Face token was written to the repo or printed.

## Access

- dataset: `FinetextPL/FinetextPL-Edu`
- URL: https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu
- gated: `manual`
- private: `False`
- disabled: `False`
- parquet files: 490
- data size: ~263.7 GB
- local HF auth detected: `True` (boolean only; token value not read or printed)
- stream status: not sampled: `DatasetNotFoundError: Dataset 'FinetextPL/FinetextPL-Edu' is a gated dataset on the Hub. Visit the dataset page at https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu to ask for access.`

## Dataset Card Facts

- claimed size: ~160M Polish documents
- sources: FineWeb2 + FinePDFs
- key field for pretraining: `text`
- quality score field: `prediction`
- recommended first threshold: `prediction >= 2.5`
- source field: `dataset_source`
- license tag: `odc-by`

## Stream Probe

- raw rows seen: 0
- accepted docs: 0
- rejected docs after threshold: 0
- accepted tokens: 0
- avg tokens / accepted doc: 0.0
- columns: `[]`

## Source Counts In Probe

| source | docs | tokens |
|---|---:|---:|
| — | — | — |

## Rejection Reasons

```json
{}
```

## Accepted Samples

_none_

## Rejected Samples

_none_

## v2.3 Options

| variant | target tokens | 50k epochs | recommended now | risk |
|---|---:|---:|---|---|
| A | 300,000,000 | 2.73 | False | Good first target if Finetext samples pass filters; still only ~2.7 epochs for 50k. |
| B | 500,000,000 | 1.64 | False | Best long-run shape, but only after bounded Finetext sampling confirms quality and storage plan. |
| C | 250,000,000 | 3.28 | False | Quality-first fallback; stage 3 becomes ~3.3 epochs, acceptable but not ideal. |
| D | 37,000,000 | 22.14 | True | Too many epochs for 50k; useful only for a short continuation sanity probe. |

## Manual Access Instructions

If stream access failed:

1. Open https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu.
2. Log in to Hugging Face.
3. Read and accept the gated dataset terms.
4. Prefer `huggingface-cli login` on the homelab, or run a command with `HF_TOKEN` in the environment.
5. Do not paste the token into repo files, scripts or logs.
6. Re-run:

```bash
cd /home/maksu/ai-model
./.venv/bin/python scripts/glyph100_finetext_probe.py --max-raw-docs 10000 --max-accepted-docs 1000
```

## Recommendation

A) najpierw uzyskać ręczny dostęp do FinetextPL-Edu on Hugging Face, then rerun the bounded probe. Do not train or download the full dataset yet.
