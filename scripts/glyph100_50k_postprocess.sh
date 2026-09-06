#!/usr/bin/env bash
set -euo pipefail

cd /home/maksu/ai-model

LOG_DIR="logs/glyph-100m-v2_3_1-50k"
TRAIN_LOG="${LOG_DIR}/train.log"
POST_LOG="${LOG_DIR}/postprocess.log"

mkdir -p "${LOG_DIR}"
exec > >(tee -a "${POST_LOG}") 2>&1

echo "$(date '+%F %T') postprocess watcher started"

while true; do
  if grep -q "Limited run complete" "${TRAIN_LOG}" 2>/dev/null; then
    echo "$(date '+%F %T') training completion marker found"
    break
  fi

  if ! tmux has-session -t glyph100-50k-diagnostic 2>/dev/null; then
    if grep -q "Limited run complete" "${TRAIN_LOG}" 2>/dev/null; then
      echo "$(date '+%F %T') training tmux ended with completion marker"
      break
    fi
    echo "$(date '+%F %T') ERROR: training tmux ended before completion marker"
    tail -n 120 "${TRAIN_LOG}" || true
    exit 1
  fi

  if grep -Eiq "non-finite|out of memory|oom|traceback|exception|crash" "${TRAIN_LOG}" 2>/dev/null; then
    echo "$(date '+%F %T') ERROR: failure marker detected in train log"
    grep -Ein "non-finite|out of memory|oom|traceback|exception|crash" "${TRAIN_LOG}" | tail -40 || true
    exit 1
  fi

  sleep 120
done

echo "$(date '+%F %T') writing 50k training report"
python3 scripts/report_glyph100_v231_50k.py

echo "$(date '+%F %T') running 44k/45k/50k eval"
RENDER_GID="$(getent group render | cut -d: -f3)"
VIDEO_GID="$(getent group video | cut -d: -f3)"
export RENDER_GID VIDEO_GID GLYPH_MODEL_VARIANT=glyph-100m
docker compose -f docker-compose.train.rocm.yml run --rm --no-deps \
  -v /home/maksu/ai-model/eval:/workspace/eval \
  trainer-rocm \
  python scripts/eval_glyph100_v231_50k_diagnostic.py --device cuda --attention-backend math

echo "$(date '+%F %T') publishing reports"
python3 scripts/publish_report_downloads.py

echo "$(date '+%F %T') postprocess complete"
