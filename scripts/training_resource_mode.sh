#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.train.yml"
STATE_FILE="${TRAIN_RESOURCE_STATE_FILE:-$PROJECT_DIR/logs/resource_mode.json}"

SCHEDULE_TZ="${TRAIN_SCHEDULE_TZ:-Europe/Warsaw}"
IMAGE="${TRAIN_IMAGE:-ai-model-trainer:cpu}"
STOP_TIMEOUT="${TRAIN_STOP_TIMEOUT:-300}"
RESTART_FOR_FULL="${TRAIN_SCHEDULE_RESTART_FOR_FULL:-1}"
AUTO_RESUME="${TRAIN_AUTO_RESUME:-0}"
PAUSE_FILE="${TRAIN_PAUSE_FILE:-$PROJECT_DIR/logs/training.paused}"
MAX_STEPS="${TRAIN_MAX_STEPS:-200000}"

ACTIVE_CPU_SHARES="${TRAIN_ACTIVE_CPU_SHARES:-256}"
ACTIVE_NICE="${TRAIN_ACTIVE_NICE:-10}"
ACTIVE_IONICE_CLASS="${TRAIN_ACTIVE_IONICE_CLASS:-2}"
ACTIVE_IONICE_LEVEL="${TRAIN_ACTIVE_IONICE_LEVEL:-7}"
ACTIVE_INTEROP_THREADS="${TRAIN_ACTIVE_INTEROP_THREADS:-1}"
ACTIVE_OMP_WAIT_POLICY="${TRAIN_ACTIVE_OMP_WAIT_POLICY:-PASSIVE}"
ACTIVE_OMP_PROC_BIND="${TRAIN_ACTIVE_OMP_PROC_BIND:-false}"
ACTIVE_OMP_PLACES="${TRAIN_ACTIVE_OMP_PLACES:-cores}"

FULL_CPU_SHARES="${TRAIN_FULL_CPU_SHARES:-2048}"
FULL_NICE="${TRAIN_FULL_NICE:-0}"
FULL_IONICE_CLASS="${TRAIN_FULL_IONICE_CLASS:-2}"
FULL_IONICE_LEVEL="${TRAIN_FULL_IONICE_LEVEL:-0}"
FULL_INTEROP_THREADS="${TRAIN_FULL_INTEROP_THREADS:-2}"
FULL_OMP_WAIT_POLICY="${TRAIN_FULL_OMP_WAIT_POLICY:-ACTIVE}"
FULL_OMP_PROC_BIND="${TRAIN_FULL_OMP_PROC_BIND:-spread}"
FULL_OMP_PLACES="${TRAIN_FULL_OMP_PLACES:-cores}"

OMP_DYNAMIC_VALUE="${TRAIN_OMP_DYNAMIC:-FALSE}"
MKL_DYNAMIC_VALUE="${TRAIN_MKL_DYNAMIC:-FALSE}"

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

mode_for_now() {
  local dow hm
  dow="$(TZ="$SCHEDULE_TZ" date '+%u')"
  hm="$(TZ="$SCHEDULE_TZ" date '+%H%M')"

  if [[ "$dow" -ge 1 && "$dow" -le 5 ]]; then
    if [[ "$hm" -ge 1500 && "$hm" -lt 2200 ]]; then
      printf 'active\n'
      return
    fi
  else
    if [[ "$hm" -ge 800 && "$hm" -lt 2200 ]]; then
      printf 'active\n'
      return
    fi
  fi

  printf 'full\n'
}

next_switch_label() {
  python3 - "$SCHEDULE_TZ" <<'PY'
import sys
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

tz = ZoneInfo(sys.argv[1])
now = datetime.now(tz)

def is_active(dt):
    weekday = dt.isoweekday()
    if weekday <= 5:
        start, end = time(15, 0), time(22, 0)
    else:
        start, end = time(8, 0), time(22, 0)
    return start <= dt.time() < end

current = is_active(now)
for minutes in range(1, 8 * 24 * 60 + 1):
    probe = now + timedelta(minutes=minutes)
    if is_active(probe) != current:
        print(probe.strftime("%Y-%m-%d %H:%M %Z"))
        break
PY
}

settings_for_mode() {
  local mode="$1"
  if [[ "$mode" == "active" ]]; then
    printf '%s %s %s %s %s %s %s %s %s %s\n' \
      "$ACTIVE_CPU_SHARES" "$ACTIVE_NICE" "$ACTIVE_IONICE_CLASS" "$ACTIVE_IONICE_LEVEL" \
      "$ACTIVE_INTEROP_THREADS" "$ACTIVE_OMP_WAIT_POLICY" "$ACTIVE_OMP_PROC_BIND" "$ACTIVE_OMP_PLACES" \
      "$OMP_DYNAMIC_VALUE" "$MKL_DYNAMIC_VALUE"
  else
    printf '%s %s %s %s %s %s %s %s %s %s\n' \
      "$FULL_CPU_SHARES" "$FULL_NICE" "$FULL_IONICE_CLASS" "$FULL_IONICE_LEVEL" \
      "$FULL_INTEROP_THREADS" "$FULL_OMP_WAIT_POLICY" "$FULL_OMP_PROC_BIND" "$FULL_OMP_PLACES" \
      "$OMP_DYNAMIC_VALUE" "$MKL_DYNAMIC_VALUE"
  fi
}

current_state_mode() {
  [[ -f "$STATE_FILE" ]] || return 0
  python3 - "$STATE_FILE" <<'PY'
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.load(f).get("mode", ""))
except Exception:
    print("")
PY
}

latest_logged_step() {
  python3 - "$PROJECT_DIR/logs/train.log" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    print(0)
    raise SystemExit

step_re = re.compile(r"step=\s*(\d+)")
latest = 0
with path.open(encoding="utf-8", errors="replace") as handle:
    for line in handle:
        match = step_re.search(line)
        if match:
            latest = int(match.group(1))
print(latest)
PY
}

find_container() {
  if [[ -n "${TRAIN_CONTAINER_NAME:-}" ]]; then
    docker ps --filter "name=^/${TRAIN_CONTAINER_NAME}$" --format '{{.Names}}' | head -n 1
    return
  fi

  docker ps --filter "ancestor=$IMAGE" --format '{{.Names}}' | head -n 1
}

training_pids() {
  local container="$1"
  docker top "$container" -eo pid,ni,comm,args \
    | awk 'NR > 1 && $0 ~ /python train\.py/ {print $1 ":" $2}'
}

write_state() {
  local mode="$1" container="$2" shares="$3" nice="$4" ionice_class="$5" ionice_level="$6" interop="$7" wait_policy="$8" proc_bind="$9" places="${10}" omp_dynamic="${11}" mkl_dynamic="${12}" note="${13}"
  mkdir -p "$(dirname "$STATE_FILE")"
  cat > "$STATE_FILE" <<EOF
{"mode":"$mode","applied_at":"$(date -Iseconds)","timezone":"$SCHEDULE_TZ","next_switch":"$(next_switch_label)","container":"$container","cpu_shares":$shares,"nice":$nice,"ionice_class":$ionice_class,"ionice_level":$ionice_level,"interop_threads":$interop,"omp_wait_policy":"$wait_policy","omp_proc_bind":"$proc_bind","omp_places":"$places","omp_dynamic":"$omp_dynamic","mkl_dynamic":"$mkl_dynamic","note":"$note"}
EOF
}

start_training_for_mode() {
  local mode="$1" shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic name
  read -r shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic < <(settings_for_mode "$mode")
  name="ai-model-train-$(date '+%Y%m%d-%H%M%S')"

  log "Starting $name in $mode mode from checkpoints/latest.pt"
  (
    cd "$PROJECT_DIR"
    TRAIN_CPU_SHARES="$shares" \
    TRAIN_NICE="$nice" \
    TRAIN_IONICE_CLASS="$ionice_class" \
    TRAIN_IONICE_LEVEL="$ionice_level" \
    TRAIN_INTEROP_THREADS="$interop" \
    TRAIN_OMP_WAIT_POLICY="$wait_policy" \
    TRAIN_OMP_PROC_BIND="$proc_bind" \
    TRAIN_OMP_PLACES="$places" \
    TRAIN_OMP_DYNAMIC="$omp_dynamic" \
    TRAIN_MKL_DYNAMIC="$mkl_dynamic" \
    docker compose -f "$COMPOSE_FILE" run -d --name "$name" trainer \
      python train.py --resume checkpoints/latest.pt
  ) >/dev/null
  printf '%s\n' "$name"
}

apply_mode() {
  local requested="${1:-auto}" mode container shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic restart_needed=0 note="applied" previous_mode

  if [[ "$requested" == "auto" ]]; then
    mode="$(mode_for_now)"
  else
    mode="$requested"
  fi

  read -r shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic < <(settings_for_mode "$mode")
  container="$(find_container)"
  previous_mode="$(current_state_mode)"

  if [[ -z "$container" ]]; then
    if [[ "$AUTO_RESUME" == "1" ]]; then
      if [[ -f "$PAUSE_FILE" ]]; then
        log "No running training container found, but pause file exists: $PAUSE_FILE"
        write_state "$mode" "" "$shares" "$nice" "$ionice_class" "$ionice_level" "$interop" "$wait_policy" "$proc_bind" "$places" "$omp_dynamic" "$mkl_dynamic" "paused"
        return 0
      fi

      latest_step="$(latest_logged_step)"
      if [[ "$latest_step" -ge "$MAX_STEPS" ]]; then
        log "No running training container found; training appears complete at step $latest_step"
        write_state "$mode" "" "$shares" "$nice" "$ionice_class" "$ionice_level" "$interop" "$wait_policy" "$proc_bind" "$places" "$omp_dynamic" "$mkl_dynamic" "complete"
        return 0
      fi

      log "No running training container found; auto-resuming in $mode mode"
      container="$(start_training_for_mode "$mode")"
      sleep 2
      docker update --cpu-shares "$shares" "$container" >/dev/null || true
      write_state "$mode" "$container" "$shares" "$nice" "$ionice_class" "$ionice_level" "$interop" "$wait_policy" "$proc_bind" "$places" "$omp_dynamic" "$mkl_dynamic" "auto-resumed"
      return 0
    fi

    log "No running training container found; recording $mode mode only"
    write_state "$mode" "" "$shares" "$nice" "$ionice_class" "$ionice_level" "$interop" "$wait_policy" "$proc_bind" "$places" "$omp_dynamic" "$mkl_dynamic" "no-running-container"
    return 0
  fi

  log "Applying $mode mode to $container: cpu_shares=$shares nice=$nice ionice=$ionice_class:$ionice_level interop=$interop omp_wait=$wait_policy"
  docker update --cpu-shares "$shares" "$container" >/dev/null

  if [[ -n "$previous_mode" && "$previous_mode" != "$mode" ]]; then
    restart_needed=1
    note="restarted-for-mode-env"
  fi

  while IFS=: read -r pid current_nice; do
    [[ -n "$pid" ]] || continue

    if command -v ionice >/dev/null 2>&1; then
      if [[ "$ionice_class" == "3" ]]; then
        ionice -c 3 -p "$pid" >/dev/null 2>&1 || true
      else
        ionice -c "$ionice_class" -n "$ionice_level" -p "$pid" >/dev/null 2>&1 || true
      fi
    fi

    if ! renice -n "$nice" -p "$pid" >/dev/null 2>&1; then
      if [[ "$mode" == "full" && "$RESTART_FOR_FULL" == "1" && "$current_nice" != "$nice" ]]; then
        restart_needed=1
      else
        note="renice-not-permitted"
      fi
    fi
  done < <(training_pids "$container")

  if [[ "$restart_needed" == "1" ]]; then
    log "Graceful restart is needed to apply $mode process environment"
    docker stop -t "$STOP_TIMEOUT" "$container" >/dev/null
    container="$(start_training_for_mode "$mode")"
    sleep 2
    docker update --cpu-shares "$shares" "$container" >/dev/null || true
    [[ "$note" == "applied" ]] && note="restarted-for-full-priority"
  fi

  write_state "$mode" "$container" "$shares" "$nice" "$ionice_class" "$ionice_level" "$interop" "$wait_policy" "$proc_bind" "$places" "$omp_dynamic" "$mkl_dynamic" "$note"
}

status() {
  local mode container shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic
  mode="$(mode_for_now)"
  read -r shares nice ionice_class ionice_level interop wait_policy proc_bind places omp_dynamic mkl_dynamic < <(settings_for_mode "$mode")
  container="$(find_container)"

  printf 'mode=%s\n' "$mode"
  printf 'timezone=%s\n' "$SCHEDULE_TZ"
  printf 'next_switch=%s\n' "$(next_switch_label)"
  printf 'target_cpu_shares=%s\n' "$shares"
  printf 'target_nice=%s\n' "$nice"
  printf 'target_ionice=%s:%s\n' "$ionice_class" "$ionice_level"
  printf 'target_interop_threads=%s\n' "$interop"
  printf 'target_omp_wait_policy=%s\n' "$wait_policy"
  printf 'target_omp_proc_bind=%s\n' "$proc_bind"
  printf 'container=%s\n' "${container:-none}"
  if [[ -n "$container" ]]; then
    docker top "$container" -eo pid,ni,pri,pcpu,pmem,comm,args | awk 'NR == 1 || /python train\.py/'
  fi
}

case "${1:-auto}" in
  auto|active|full)
    apply_mode "$1"
    ;;
  mode-only)
    mode_for_now
    ;;
  status)
    status
    ;;
  *)
    cat <<'EOF'
Usage:
  scripts/training_resource_mode.sh auto
  scripts/training_resource_mode.sh active
  scripts/training_resource_mode.sh full
  scripts/training_resource_mode.sh status
  scripts/training_resource_mode.sh mode-only
EOF
    exit 2
    ;;
esac
