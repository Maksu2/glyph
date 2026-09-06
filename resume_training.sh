#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
LOG_FILE="$SCRIPT_DIR/logs/train.stdout.log"
PID_FILE="$SCRIPT_DIR/train.pid"
SESSION_NAME="polish-gpt-train"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python venv not found: $PYTHON_BIN" >&2
  exit 1
fi

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
  if [[ -n "${old_pid:-}" ]] && kill -0 "$old_pid" 2>/dev/null; then
    echo "Training already running (PID $old_pid)." >&2
    exit 1
  fi
  rm -f "$PID_FILE"
fi

mc_pid="$(ps -ef | awk '/java .*paper\.jar/ && !/awk/ {print $2; exit}')"
mc_core=""

if [[ -n "${mc_pid:-}" ]]; then
  mc_core="$(ps -Lp "$mc_pid" -o psr,pcpu --sort=-pcpu | awk 'NR==2 {print $1}')"
fi

total_cores="$(nproc)"
allowed_cores=()
for ((i=0; i<total_cores; i++)); do
  if [[ -n "$mc_core" && "$i" == "$mc_core" ]]; then
    continue
  fi
  allowed_cores+=("$i")
done

if [[ "${#allowed_cores[@]}" -eq 0 ]]; then
  echo "No CPU cores left after excluding Minecraft core '${mc_core:-unknown}'." >&2
  exit 1
fi

cpu_list="$(IFS=,; echo "${allowed_cores[*]}")"
thread_count="${#allowed_cores[@]}"

export OMP_NUM_THREADS="$thread_count"
export MKL_NUM_THREADS="$thread_count"
export OPENBLAS_NUM_THREADS="$thread_count"
export NUMEXPR_NUM_THREADS="$thread_count"
export TRAIN_NUM_THREADS="$thread_count"
export TRAIN_INTEROP_THREADS=1

echo "Starting training on cores: $cpu_list (excluding Minecraft core: ${mc_core:-none})"
echo "Logs: $LOG_FILE"

cd "$SCRIPT_DIR"
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
tmux new-session -d -s "$SESSION_NAME" \
  "bash -lc 'cd \"$SCRIPT_DIR\" && export OMP_NUM_THREADS=$thread_count MKL_NUM_THREADS=$thread_count OPENBLAS_NUM_THREADS=$thread_count NUMEXPR_NUM_THREADS=$thread_count TRAIN_NUM_THREADS=$thread_count TRAIN_INTEROP_THREADS=1 && exec taskset -c \"$cpu_list\" \"$PYTHON_BIN\" train.py --resume >> \"$LOG_FILE\" 2>&1'"

sleep 2
train_pid="$(pgrep -n -f "$PYTHON_BIN train.py --resume" || true)"
if [[ -z "${train_pid:-}" ]]; then
  echo "Training process did not start; inspect $LOG_FILE or attach to tmux session $SESSION_NAME." >&2
  exit 1
fi

echo "$train_pid" > "$PID_FILE"
echo "Training PID: $train_pid"
echo "tmux session: $SESSION_NAME"
