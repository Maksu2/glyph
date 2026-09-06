#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BASE="${SFT_BASE:-checkpoints/final.pt}"
TRAIN_JSONL="${SFT_TRAIN_JSONL:-data/sft/processed/sft_v0_train.jsonl}"
VAL_JSONL="${SFT_VAL_JSONL:-data/sft/processed/sft_v0_val.jsonl}"
OUTPUT="${SFT_OUTPUT:-checkpoints/sft-v0}"
BATCH_SIZE="${SFT_BATCH_SIZE:-16}"
LR="${SFT_LR:-2e-5}"
MIN_LR="${SFT_MIN_LR:-2e-6}"
EPOCHS="${SFT_EPOCHS:-1}"
TAG="${SFT_TAG:-glyph-27m-sft-v0}"

common_args=(
  --base "$BASE"
  --train-jsonl "$TRAIN_JSONL"
  --val-jsonl "$VAL_JSONL"
  --output "$OUTPUT"
  --epochs "$EPOCHS"
  --batch-size "$BATCH_SIZE"
  --learning-rate "$LR"
  --min-lr "$MIN_LR"
  --warmup-steps "${SFT_WARMUP_STEPS:-10}"
  --eval-interval "${SFT_EVAL_INTERVAL:-25}"
  --val-batches "${SFT_VAL_BATCHES:-10}"
  --checkpoint-interval "${SFT_CHECKPOINT_INTERVAL:-50}"
  --log-interval "${SFT_LOG_INTERVAL:-5}"
  --tag "$TAG"
)

if [[ "${SFT_SKIP_ROCM:-0}" != "1" ]]; then
  render_gid="$(getent group render | cut -d: -f3 || true)"
  video_gid="$(getent group video | cut -d: -f3 || true)"
  name="glyph-sft-v0-$(date -u +%Y%m%d-%H%M%S)"
  echo "Starting SFT v0 on ROCm container: $name"
  if RENDER_GID="${render_gid:-993}" VIDEO_GID="${video_gid:-44}" \
    docker compose -f docker-compose.train.rocm.yml run --rm --name "$name" trainer-rocm \
      python finetune.py --device cuda "${common_args[@]}"; then
    echo "SFT v0 ROCm run completed."
    exit 0
  fi
  echo "ROCm SFT failed. Falling back to CPU in a separate output directory." >&2
fi

fallback_output="${SFT_CPU_OUTPUT:-checkpoints/sft-v0-cpu-fallback}"
fallback_batch="${SFT_CPU_BATCH_SIZE:-8}"
threads="${TRAIN_NUM_THREADS:-6}"

echo "Starting SFT v0 CPU fallback: $fallback_output"
TRAIN_NUM_THREADS="$threads" .venv/bin/python finetune.py \
  --device cpu \
  --base "$BASE" \
  --train-jsonl "$TRAIN_JSONL" \
  --val-jsonl "$VAL_JSONL" \
  --output "$fallback_output" \
  --epochs "$EPOCHS" \
  --batch-size "$fallback_batch" \
  --learning-rate "$LR" \
  --min-lr "$MIN_LR" \
  --warmup-steps "${SFT_WARMUP_STEPS:-10}" \
  --eval-interval "${SFT_EVAL_INTERVAL:-25}" \
  --val-batches "${SFT_VAL_BATCHES:-10}" \
  --checkpoint-interval "${SFT_CHECKPOINT_INTERVAL:-50}" \
  --log-interval "${SFT_LOG_INTERVAL:-5}" \
  --tag "${SFT_CPU_TAG:-glyph-27m-sft-v0-cpu-fallback}"
