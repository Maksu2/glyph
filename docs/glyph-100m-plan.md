# Glyph-100M Readiness Plan

Glyph-100M is the next base-model experiment after Glyph-27M proved the local
pipeline: tokenizer, PyTorch model, checkpointing, ROCm training, dashboard,
SFT, and evaluation.

This document is a readiness note, not approval to train. Do not start a full
run without an explicit approval step.

## Why Move Beyond Glyph-27M

Glyph-27M Base completed pretraining and Glyph-27M SFT v0 proved that the
instruction-tuning path works technically. Eval v2 showed that 27M is too small
to be the main quality target: SFT v0 improves endings and removes many web
artifacts, but it still often misses the actual task.

Glyph-100M is a capacity step, not a marketing number. It keeps the same simple
decoder-only architecture family while increasing width, depth, and context.

## Variant Config

| Field | Glyph-27M | Glyph-100M |
|---|---:|---:|
| layers | 6 | 12 |
| heads | 8 | 12 |
| d_model | 512 | 768 |
| FFN dim | 2048 | 3072 |
| context | 256 | 512 |
| vocab | 16,000 | 16,000 |
| dropout | 0.1 | 0.1 |
| unique/trainable params | 27,210,752 | 97,654,272 |
| logical params with tied head counted | 35,402,752 | 109,942,272 |

Parameter report: `reports/glyph100_parameter_report.json`.

## ROCm Smoke Test

Environment:

- GPU: AMD Radeon RX 5500 XT 8 GB
- backend: PyTorch ROCm/HIP in `ai-model-trainer:rocm-gfx1012`
- model: Glyph-100M, context 512

Result file: `reports/glyph100_rocm_smoke.json`.

| Microbatch | Result | Tokens/step | Synthetic tok/s | Peak allocated |
|---:|---|---:|---:|---:|
| 4 | ok | 2,048 | ~3,106 | ~4.47 GiB |
| 8 | ok | 4,096 | ~3,286 | ~7.17 GiB |
| 16 | OOM | 8,192 | - | VRAM full |
| 32 | not attempted | 16,384 | - | batch 16 already failed |

Recommended training shape:

- microbatch: 4
- gradient accumulation: 8
- effective tokens/optimizer step: 16,384
- reason: batch 8 passed synthetic smoke but leaves little VRAM headroom; batch 4 with accumulation 8 keeps the same effective batch with safer ROCm margin.

## Dataset Candidate

The initial Glyph-100M candidate split is named `glyph100_stage1_candidate`.
It is built from the existing legacy Polish corpus using stricter filtering,
not from a new download.

Outputs:

- `data/processed/glyph100_train.bin`
- `data/processed/glyph100_val.bin`
- `data/processed/glyph100_metadata.json`
- `data/reports/glyph_100m_dataset_report.md`
- `data/reports/glyph_100m_dataset_stats.json`

Current candidate stats:

- raw documents scanned: 289,973
- accepted documents: 250,000
- rejected documents: 39,973
- train docs: 247,439
- val docs: 2,561
- train tokens: 117,870,679
- val tokens: 1,239,948
- total tokens: 119,110,627
- token/word ratio: 2.020
- docs <= context 512: 73.22%

This is enough for a stage-1 sanity run. It is not yet a final long-run corpus;
longer stages should process the full corpus and preserve source metadata.

## Data Source Decisions

| Source | Decision | Reason |
|---|---|---|
| Polish Wikipedia | use | clean encyclopedic Polish and broad factual style |
| Wolne Lektury | use with boilerplate filtering | valuable long-form Polish, but project/license text must be removed |
| mC4 / OSCAR PL | use filtered only | useful breadth, but high risk of SEO/forum/web garbage |
| FinetextPL-Edu | later | promising Polish educational corpus, but gated and large; treat as a separate decision |

## Filters

The candidate pipeline rejects or marks:

- HTML and repeated URLs
- navigation/boilerplate phrases
- Wolne Lektury project boilerplate
- very short documents
- very long suspicious lines
- low alphabetic ratio
- weak Polish signal
- excess punctuation/symbols
- repeated n-grams
- low unique-word ratio
- exact duplicates
- simple near-duplicate prefixes

Script: `scripts/glyph100_prepare_dataset.py`.

## Tokenizer

Glyph-100M keeps the existing SentencePiece BPE tokenizer:

- tokenizer: `data/processed/tokenizer.model`
- vocab size: 16,000
- reason: fewer variables, comparability with Glyph-27M, faster experiment

Do not train a new tokenizer for stage 1 without a separate decision.

## Training Plan

All stages are approval-gated. Stage 1 is the only near-term candidate.

| Stage | Steps | Effective tokens | Purpose | Checkpoint |
|---|---:|---:|---|---|
| stage 0 | smoke only | synthetic | model/ROCm/memory/checkpoint sanity | none/fake smoke artifact |
| stage 1 | 1,000 | 16.4M | real data sanity, loss curve, val loss, checkpoint write | `checkpoints/glyph-100m/latest.pt` |
| stage 2 | 10,000 | 163.8M | early learning check | `checkpoints/glyph-100m/step_0010000.pt` |
| stage 3 | 50,000 | 819.2M | quality/eval checkpoint | `checkpoints/glyph-100m/step_0050000.pt` |
| stage 4 | 100,000 | 1.64B | proper mid-run checkpoint | `checkpoints/glyph-100m/step_0100000.pt` |
| stage 5 | 200,000 | 3.28B | final-ish run if dataset quality holds | `checkpoints/glyph-100m/final.pt` |

At observed synthetic throughput, stage 1 should be on the order of one to two
hours including validation/checkpoint overhead. Real throughput may differ from
synthetic smoke numbers.

## Proposed Hyperparameters

Initial Glyph-100M config:

- context length: 512
- microbatch: 4
- gradient accumulation: 8
- effective tokens/step: 16,384
- optimizer: AdamW
- max LR: 2e-4
- min LR: 2e-5
- warmup: 2,000 steps for long run; consider 100 warmup steps for stage-1-only sanity
- weight decay: 0.1
- grad clip: 1.0
- dropout: 0.1
- eval interval: 250
- eval batches: 5
- checkpoint interval: 500

The stage-1 run should use a checkpoint directory separate from 27M:
`checkpoints/glyph-100m`.

Logs are also variant-specific:

- Glyph-27M historical log: `logs/train.log`
- Glyph-27M future runs: `logs/glyph-27m/train.log`
- Glyph-100M stage runs: `logs/glyph-100m/train.log`

Glyph-100M checkpoints include variant metadata, train config, model config,
tokenizer path/checksum, dataset metadata path, gradient accumulation and
effective tokens per optimizer step. Resume must reject 27M/100M mismatches.

## Stop Conditions

Stop and inspect if any of these happen:

- NaN loss
- val loss increases absurdly or is not finite
- no progress in logs
- ROCm crash or hang
- repeated OOM
- GPU hotspot stays too high
- checkpoint write failure
- dataset path or tokenizer mismatch
- generated samples show obvious large-scale data garbage

## Eval Skeleton

Base-model continuation prompts are prepared in:

- `eval/glyph-100m/base_continuation_prompts.jsonl`

These prompts evaluate continuation quality, syntax, lack of web garbage,
anti-loop behavior, and simple factual completions. They are not SFT prompts.

## Stage 1 Command Template

Do not run this without approval:

```bash
cd /home/maksu/ai-model
RENDER_GID=$(getent group render | cut -d: -f3) \
VIDEO_GID=$(getent group video | cut -d: -f3) \
GLYPH_MODEL_VARIANT=glyph-100m \
docker compose -f docker-compose.train.rocm.yml run --rm --no-deps trainer-rocm \
  python train.py \
    --variant glyph-100m \
    --device cuda \
    --max-steps 1000 \
    --batch-size 4 \
    --gradient-accumulation-steps 8 \
    --learning-rate 2e-4 \
    --min-lr 2e-5 \
    --checkpoint-dir checkpoints/glyph-100m \
    --log-dir logs/glyph-100m \
    --dataset-name glyph100_stage1_candidate \
    --dataset-metadata-path data/processed/glyph100_metadata.json \
    --eval-interval 250 \
    --checkpoint-interval 500 \
    --log-interval 10
```

## Readiness Recommendation

Glyph-100M is ready for an approved stage-1 / 1k-step sanity run, with these
conditions:

- use the filtered `glyph100_*` split, not the legacy `tokens.bin`
- use ROCm microbatch 4 plus gradient accumulation 8
- keep stage 1 limited to 1,000 optimizer steps
- inspect train loss, val loss, checkpoint write, and a small sample before any longer stage
- process the full corpus with source-preserving metadata before stage 2+
