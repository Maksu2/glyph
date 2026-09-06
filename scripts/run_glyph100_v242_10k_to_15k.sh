#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/maksu/ai-model
BASE_CHECKPOINT=checkpoints/glyph-100m-v2_4_2-10k/step_0010000.pt
CHECKPOINT_DIR=checkpoints/glyph-100m-v2_4_2-15k
LOG_DIR=logs/glyph-100m-v2_4_2-15k

cd "$ROOT"

python3 - "$BASE_CHECKPOINT" <<'PY'
import hashlib
import sys

import torch

path = sys.argv[1]
checkpoint = torch.load(path, map_location="cpu", weights_only=False)
expected = {
    "variant": "glyph-100m",
    "step": 10000,
    "current_step": 10000,
    "dataset_name": "glyph100_dataset_v2_4_2_core",
    "tokenizer_sha256": "21bad2b08f1081afee40fbb6d5489d8199deebd7b81d76a34b347f2f01dd4029",
    "batch_size": 4,
    "gradient_accumulation_steps": 8,
    "effective_tokens_per_step": 16384,
}
for key, value in expected.items():
    if checkpoint.get(key) != value:
        raise SystemExit(
            f"checkpoint preflight failed: {key}={checkpoint.get(key)!r}, expected {value!r}"
        )
if "optimizer" not in checkpoint or "scheduler_state" not in checkpoint:
    raise SystemExit("checkpoint preflight failed: optimizer or scheduler state is missing")
tokenizer = "data/processed/tokenizer.model"
with open(tokenizer, "rb") as handle:
    digest = hashlib.file_digest(handle, "sha256").hexdigest()
if digest != expected["tokenizer_sha256"]:
    raise SystemExit(f"tokenizer checksum mismatch: {digest}")
PY

# pgrep (rg nie ma na hoscie). Wzorzec omija nazwe wlasnego skryptu,
# zeby straznik nie dopasowal sam siebie; lapie docker-cli i train.py.
if pgrep -f 'trainer-rocm|train[.]py' >/dev/null; then
  printf 'another training container is active\n' >&2
  exit 2
fi

if [[ -e "$CHECKPOINT_DIR/latest.pt" || -e "$LOG_DIR/train.log" ]]; then
  printf '15k output already exists; refusing to overwrite\n' >&2
  exit 3
fi

mkdir -p "$CHECKPOINT_DIR" "$LOG_DIR"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$LOG_DIR/started_at.txt"

RENDER_GID=$(getent group render | cut -d: -f3)
VIDEO_GID=$(getent group video | cut -d: -f3)
export RENDER_GID VIDEO_GID GLYPH_MODEL_VARIANT=glyph-100m

set +e
docker compose -f docker-compose.train.rocm.yml run --rm --no-deps \
  trainer-rocm \
  python train.py \
    --variant glyph-100m \
    --device cuda \
    --resume "$BASE_CHECKPOINT" \
    --max-steps 15000 \
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
    --eval-seed 2027 \
    --val-batches 64 \
    --eval-interval 500 \
    --checkpoint-interval 2500 \
    --log-interval 10 \
    --finite-check-interval 100 \
  2>&1 | tee "$LOG_DIR/launcher.log"
status=${PIPESTATUS[0]}
set -e

printf '%s\n' "$status" > "$LOG_DIR/exit_code.txt"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$LOG_DIR/finished_at.txt"
exit "$status"
