#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/maksu/ai-model
CHECKPOINT_DIR=checkpoints/glyph-100m-v2_4_2-5k
LOG_DIR=logs/glyph-100m-v2_4_2-5k
VALIDATION=reports/glyph100_v2_4_2_validation.json

cd "$ROOT"

python3 - "$VALIDATION" <<'PY'
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
if not payload.get("ready_for_5k_proxy"):
    raise SystemExit("v2.4.2 independent validation did not approve the 5k proxy")
PY

if docker ps --format '{{.Names}} {{.Command}}' | grep -Eiq 'trainer-rocm|train\.py'; then
  echo "another training container is active" >&2
  exit 2
fi
if [[ -e "$CHECKPOINT_DIR/latest.pt" || -e "$LOG_DIR/train.log" ]]; then
  echo "v2.4.2 5k output already exists; refusing to overwrite" >&2
  exit 3
fi

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
    --max-steps 5000 \
    --data-path data/processed/glyph100_v2_4_2_train.bin \
    --val-data-path data/processed/glyph100_v2_4_2_val.bin \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --log-dir "$LOG_DIR" \
    --tokenizer-path data/processed/tokenizer.model \
    --dataset-name glyph100_dataset_v2_4_2_core \
    --dataset-metadata-path data/processed/glyph100_v2_4_2_metadata.json \
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
    --checkpoint-interval 1000 \
    --log-interval 10 \
    --finite-check-interval 100 \
  2>&1 | tee "$LOG_DIR/launcher.log"
status=${PIPESTATUS[0]}
set -e

printf '%s\n' "$status" > "$LOG_DIR/exit_code.txt"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$LOG_DIR/finished_at.txt"
exit "$status"
