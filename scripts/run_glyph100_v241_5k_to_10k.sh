#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/maksu/ai-model
CHECKPOINT_DIR=checkpoints/glyph-100m-v2_4_1-10k
LOG_DIR=logs/glyph-100m-v2_4_1-10k

cd "$ROOT"
mkdir -p "$CHECKPOINT_DIR" "$LOG_DIR"

date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LOG_DIR/started_at.txt"
RENDER_GID=$(getent group render | cut -d: -f3)
VIDEO_GID=$(getent group video | cut -d: -f3)
export RENDER_GID VIDEO_GID GLYPH_MODEL_VARIANT=glyph-100m

set +e
docker compose -f docker-compose.train.rocm.yml run --rm --no-deps \
  trainer-rocm \
  python train.py \
    --variant glyph-100m \
    --device cuda \
    --resume checkpoints/glyph-100m-v2_4_1-5k/latest.pt \
    --max-steps 10000 \
    --data-path data/processed/glyph100_v2_4_1_train.bin \
    --val-data-path data/processed/glyph100_v2_4_1_val.bin \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --log-dir "$LOG_DIR" \
    --tokenizer-path data/processed/tokenizer.model \
    --dataset-name glyph100_dataset_v2_4_1_core \
    --dataset-metadata-path data/processed/glyph100_v2_4_1_metadata.json \
    --batch-size 4 \
    --gradient-accumulation-steps 8 \
    --learning-rate 2e-4 \
    --min-lr 2e-5 \
    --warmup-steps 2000 \
    --weight-decay 0.1 \
    --grad-clip 1.0 \
    --train-sampling shuffled_blocks \
    --data-seed 2026 \
    --eval-seed 2026 \
    --val-batches 64 \
    --eval-interval 500 \
    --checkpoint-interval 2500 \
    --log-interval 10 \
    --finite-check-interval 100 \
  2>&1 | tee "$LOG_DIR/launcher.log"
status=${PIPESTATUS[0]}
set -e

printf '%s\n' "$status" > "$LOG_DIR/exit_code.txt"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LOG_DIR/finished_at.txt"
exit "$status"
