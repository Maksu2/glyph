#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

PYTHON="${PYTHON:-$PROJECT_DIR/.venv/bin/python}"
COMPOSE=(docker compose -f "$PROJECT_DIR/docker-compose.teacher.yml" --profile teacher)
RUN_ID="${GEMMA4_RUN_ID:-$(date '+%Y%m%d-%H%M%S')}"
MODEL_LABEL="${GEMMA4_MODEL_LABEL:-Gemma 4 E4B}"
MODEL_HOST="${GEMMA4_MODEL_HOST:-$PROJECT_DIR/models/gemma4/gemma-4-e4b-it-q4_k_m.gguf}"
MODEL_DIR_HOST="${GEMMA4_MODELS_DIR_HOST:-$(dirname "$MODEL_HOST")}"
MODEL_CONTAINER="${GEMMA4_MODEL:-/models/$(basename "$MODEL_HOST")}"
PORT="${GEMMA4_PORT:-8182}"
BASE_URL="${GEMMA4_BASE_URL:-http://127.0.0.1:$PORT}"
PROMPTS="${GEMMA4_PROMPTS:-$PROJECT_DIR/eval/prompts.jsonl}"
LIMIT="${GEMMA4_EVAL_LIMIT:-60}"
LOAD_TIMEOUT="${GEMMA4_LOAD_TIMEOUT:-600}"
STATE_FILE="$PROJECT_DIR/reports/gemma4_eval/status.json"
LOCK_FILE="$PROJECT_DIR/logs/gemma4_eval.lock"
LOG_FILE="$PROJECT_DIR/logs/gemma4_eval_cycle.log"

mkdir -p "$PROJECT_DIR/logs" "$PROJECT_DIR/reports/samples" "$PROJECT_DIR/reports/gemma4_eval"
exec > >(tee -a "$LOG_FILE") 2>&1

write_status() {
  local status="$1"
  local message="${2:-}"
  local report="${3:-}"
  local score="${4:-}"
  "$PYTHON" - "$STATE_FILE" "$status" "$MODEL_LABEL" "$message" "$report" "$score" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
score = None if sys.argv[6] == "" else float(sys.argv[6])
payload = {
    "status": sys.argv[2],
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "model": sys.argv[3],
    "message": sys.argv[4],
    "report": sys.argv[5],
    "overall_avg": score,
}
path.parent.mkdir(parents=True, exist_ok=True)
tmp = path.with_suffix(path.suffix + ".tmp")
tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(path)
PY
}

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  write_status "skipped" "previous Gemma 4 eval is still running"
  exit 0
fi

if [[ ! -x "$PYTHON" ]]; then
  write_status "error" "python not found: $PYTHON"
  exit 1
fi

if [[ ! -f "$MODEL_HOST" ]]; then
  write_status "model-missing" "expected GGUF model at $MODEL_HOST"
  exit 0
fi

export GEMMA4_MODELS_DIR_HOST="$MODEL_DIR_HOST"
export GEMMA4_MODEL="$MODEL_CONTAINER"
export RENDER_GID="${RENDER_GID:-$(getent group render | cut -d: -f3 || true)}"
export VIDEO_GID="${VIDEO_GID:-$(getent group video | cut -d: -f3 || true)}"
export RENDER_GID="${RENDER_GID:-993}"
export VIDEO_GID="${VIDEO_GID:-44}"

started_by_us=0
container_id="$("${COMPOSE[@]}" ps -q teacher-vulkan 2>/dev/null || true)"
if [[ -z "$container_id" ]] || [[ "$(docker inspect -f '{{.State.Running}}' "$container_id" 2>/dev/null || echo false)" != "true" ]]; then
  started_by_us=1
fi

cleanup() {
  if [[ "$started_by_us" == "1" ]]; then
    "${COMPOSE[@]}" stop teacher-vulkan >/dev/null 2>&1 || true
    "${COMPOSE[@]}" rm -f teacher-vulkan >/dev/null 2>&1 || true
  fi
}

mark_error() {
  local code=$?
  write_status "error" "Gemma 4 eval failed with exit code $code; see logs/gemma4_eval_cycle.log"
  cleanup
  exit "$code"
}

trap cleanup EXIT
trap mark_error ERR

write_status "running" "starting Gemma 4 teacher"
"${COMPOSE[@]}" up -d teacher-vulkan

deadline=$((SECONDS + LOAD_TIMEOUT))
while true; do
  code="$(curl -sS -o /tmp/gemma4-health.$$ -w '%{http_code}' "$BASE_URL/health" || true)"
  if [[ "$code" == "200" ]]; then
    break
  fi
  if [[ "$SECONDS" -ge "$deadline" ]]; then
    write_status "error" "Gemma 4 teacher did not become healthy within ${LOAD_TIMEOUT}s"
    exit 1
  fi
  sleep 5
done

samples="$PROJECT_DIR/reports/samples/$RUN_ID.jsonl"
sample_latest="$PROJECT_DIR/reports/samples/latest.jsonl"
report="$PROJECT_DIR/reports/gemma4_eval/$RUN_ID.jsonl"
summary="$PROJECT_DIR/reports/gemma4_eval/$RUN_ID.summary.json"
training_stats="$PROJECT_DIR/reports/gemma4_eval/$RUN_ID.training_stats.json"
summary_latest="$PROJECT_DIR/reports/gemma4_eval/latest_summary.json"
report_latest="$PROJECT_DIR/reports/gemma4_eval/latest.jsonl"

write_status "running" "generating Glyph-27M samples"
GEMMA4_RUN_ID="$RUN_ID" GLYPH_EVAL_THREADS="${GLYPH_EVAL_THREADS:-${MINIGPT_EVAL_THREADS:-2}}" \
  nice -n "${GEMMA4_NICE:-10}" ionice -c2 -n7 \
  "$PYTHON" "$PROJECT_DIR/scripts/run_minigpt_eval.py" \
    --checkpoint checkpoints/latest.pt \
    --prompts "$PROMPTS" \
    --out "$samples" \
    --limit "$LIMIT" \
    --max-tokens "${GLYPH_EVAL_MAX_TOKENS:-${MINIGPT_EVAL_MAX_TOKENS:-60}}" \
    --temperature "${GLYPH_EVAL_TEMPERATURE:-${MINIGPT_EVAL_TEMPERATURE:-0.75}}" \
    --top-k "${GLYPH_EVAL_TOP_K:-${MINIGPT_EVAL_TOP_K:-50}}" \
    --top-p "${GLYPH_EVAL_TOP_P:-${MINIGPT_EVAL_TOP_P:-0.92}}" \
    --repetition-penalty "${GLYPH_EVAL_REPETITION_PENALTY:-${MINIGPT_EVAL_REPETITION_PENALTY:-1.10}}" \
    --no-repeat-ngram-size "${GLYPH_EVAL_NO_REPEAT_NGRAM:-${MINIGPT_EVAL_NO_REPEAT_NGRAM:-4}}"
cp "$samples" "$sample_latest"

curl -fsS http://127.0.0.1:8181/api/stats -o "$training_stats" || printf '{}\n' > "$training_stats"

write_status "running" "judging Glyph-27M samples with Gemma 4"
nice -n "${GEMMA4_NICE:-10}" ionice -c2 -n7 \
  "$PYTHON" "$PROJECT_DIR/scripts/run_gemma4_judge.py" \
    --samples "$samples" \
    --out "$report" \
    --summary-out "$summary" \
    --base-url "$BASE_URL" \
    --model-label "$MODEL_LABEL" \
    --limit "$LIMIT" \
    --training-stats "$training_stats"
cp "$report" "$report_latest"
cp "$summary" "$summary_latest"

write_status "running" "exporting public Glyph snapshot"
nice -n "${GEMMA4_NICE:-10}" ionice -c2 -n7 \
  "$PYTHON" "$PROJECT_DIR/scripts/export_public_site_data.py" \
    --sample-limit "${GLYPH_PUBLIC_SAMPLE_LIMIT:-6}" \
    --quiet || echo "Warning: public snapshot export failed"

score="$("$PYTHON" - "$summary" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as f:
    value = json.load(f).get("overall_avg")
print("" if value is None else value)
PY
)"
write_status "ok" "Gemma 4 eval complete" "reports/gemma4_eval/$RUN_ID.jsonl" "$score"
