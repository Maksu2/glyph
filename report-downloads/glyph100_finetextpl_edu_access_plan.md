# Glyph-100M FinetextPL-Edu Access Plan

Generated: 2026-06-01

No training was started. No gated access was bypassed.

## Status

Dataset: `FinetextPL/FinetextPL-Edu`

URL: https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu

Observed metadata:

- access: gated/manual on Hugging Face
- language: Polish
- license tag: `odc-by`
- task: text generation
- size category: `100M<n<1B`
- files: 490 parquet data files
- data file size by HF metadata: ~283 GB
- first parquet file: ~592 MB
- downloads shown by HF metadata: 10

Dataset card/search summary says it contains about 160M Polish documents derived from Polish FineWeb2 and FinePDFs, with an educational-value `prediction` score. The recommended starting threshold is `prediction >= 2.5`.

## Why It Matters

This is the most promising source for `glyph100_dataset_v2_2` if we want:

- less Wikipedia style,
- more normal Polish educational/factual prose,
- enough non-Wikipedia tokens for a 50% or 70% Wiki cap,
- cleaner web/PDF data than our old `legacy_mixed_corpus`.

## Current Blocker

Access requires Hugging Face login / manual approval. Without an authenticated HF token with accepted access, streaming and sampling fail.

I did not read any token or credentials and did not try to bypass access.

## Manual Steps For Maks

1. Open https://huggingface.co/datasets/FinetextPL/FinetextPL-Edu.
2. Log in to Hugging Face.
3. Read and accept the gated dataset terms if acceptable.
4. Create a read-only Hugging Face token if needed.
5. Provide access to the environment explicitly, for example by logging in with `huggingface-cli login` yourself, or by telling Codex how you want the token handled.

Do not paste a token into random files or chat unless you explicitly choose that risk. Prefer local `huggingface-cli login`.

## Safe First Test After Access

Do not download all 283 GB.

First test should be streaming-only:

```bash
cd /home/maksu/ai-model
./.venv/bin/python - <<'PY'
from datasets import load_dataset
from itertools import islice

ds = load_dataset("FinetextPL/FinetextPL-Edu", split="train", streaming=True)
for row in islice(ds, 20):
    print(row.keys())
    print(row.get("prediction"), row.get("dataset_source"))
    print((row.get("text") or "")[:500].replace("\\n", " "))
    print("---")
PY
```

Then run a controlled sample audit:

- sample 1k rows with `prediction >= 2.5`,
- sample separately `fineweb2` and `finepdfs`,
- compute token counts with Glyph tokenizer,
- inspect 100 accepted / 100 rejected samples,
- only then decide whether to download a bounded shard.

## Recommended Use If Approved

For v2.2:

- use only `prediction >= 2.5` at first,
- cap per-source contribution,
- preserve `dataset_source`, source URL/id, and `doc_id`,
- reject commerce/forum/SEO even if prediction is high,
- keep exact and near-dedup against Wikipedia, Wolne Lektury, Wikisource, PSC, and Wikibooks.

## Decision

`later`.

FinetextPL-Edu is probably the best route for a robust v2.2-B or v2.3, but it needs manual access and a careful bounded sample audit first.
