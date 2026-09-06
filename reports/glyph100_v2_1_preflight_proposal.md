# Glyph-100M v2.1 Preflight Proposal

Generated: 2026-06-01

No training was started. This is a fallback proposal only.

## Purpose

If we decide not to build v2.2 immediately, a short v2.1 continuation can answer one narrow question:

> Does the clean but wiki-heavy dataset keep training stable and improve base LM behavior over the 10k checkpoint?

It should not be treated as stage 3 / 50k.

## Proposed Run

Name:

`glyph100-v2-1-clean-wiki-heavy-preflight`

Start:

- checkpoint: `checkpoints/glyph-100m/latest.pt`
- expected current step: 10,000
- dataset: `glyph100_dataset_v2_1`
- train: `data/processed/glyph100_v2_1_train.bin`
- val: `data/processed/glyph100_v2_1_val.bin`

Length options:

| option | end step | additional steps | additional tokens | epochs over v2.1 |
|---|---:|---:|---:|---:|
| short | 12,000 | 2,000 | 32,768,000 | 0.24 |
| medium | 15,000 | 5,000 | 81,920,000 | 0.61 |

## Command Sketch

Do not run without explicit approval.

```bash
cd /home/maksu/ai-model
tmux new-session -d -s glyph100-v2-1-preflight 'cd /home/maksu/ai-model && RENDER_GID=$(getent group render | cut -d: -f3) VIDEO_GID=$(getent group video | cut -d: -f3) GLYPH_MODEL_VARIANT=glyph-100m docker compose -f docker-compose.train.rocm.yml run --rm --no-deps trainer-rocm python train.py --variant glyph-100m --device cuda --resume checkpoints/glyph-100m/latest.pt --max-steps 12000 --batch-size 4 --gradient-accumulation-steps 8 --learning-rate 2e-4 --min-lr 2e-5 --checkpoint-dir checkpoints/glyph-100m --log-dir logs/glyph-100m --dataset-name glyph100_dataset_v2_1 --dataset-metadata-path data/processed/glyph100_v2_1_metadata.json --eval-interval 500 --checkpoint-interval 1000 --log-interval 10'
```

For the 5k option, change `--max-steps 12000` to `--max-steps 15000`.

## What To Measure

- train loss slope from 10k to 12k/15k
- val loss on v2.1
- sample quality on base completion prompts
- whether output becomes more Wikipedia-like
- whether web/forum garbage stays suppressed
- whether syntax/coherence improves

## Stop Conditions

- NaN/Inf loss
- OOM
- ROCm crash/hang
- checkpoint write failure
- val loss worsens sharply
- obvious quality regression in samples

## Recommendation

This is a fallback, not the main path.

Prefer building `glyph100_dataset_v2_2` Option A first. Use this preflight only if we want a very cheap stability/quality signal while postponing source-mix work.
