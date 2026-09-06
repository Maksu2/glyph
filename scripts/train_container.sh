#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

apply_scheduled_defaults() {
  local mode shares nice ionice_class ionice_level interop wait_policy proc_bind
  mode="${TRAIN_RESOURCE_MODE:-$("$SCRIPT_DIR/training_resource_mode.sh" mode-only)}"

  if [[ "$mode" == "active" ]]; then
    shares="${TRAIN_ACTIVE_CPU_SHARES:-256}"
    nice="${TRAIN_ACTIVE_NICE:-10}"
    ionice_class="${TRAIN_ACTIVE_IONICE_CLASS:-2}"
    ionice_level="${TRAIN_ACTIVE_IONICE_LEVEL:-7}"
    interop="${TRAIN_ACTIVE_INTEROP_THREADS:-1}"
    wait_policy="${TRAIN_ACTIVE_OMP_WAIT_POLICY:-PASSIVE}"
    proc_bind="${TRAIN_ACTIVE_OMP_PROC_BIND:-false}"
  else
    shares="${TRAIN_FULL_CPU_SHARES:-2048}"
    nice="${TRAIN_FULL_NICE:-0}"
    ionice_class="${TRAIN_FULL_IONICE_CLASS:-2}"
    ionice_level="${TRAIN_FULL_IONICE_LEVEL:-0}"
    interop="${TRAIN_FULL_INTEROP_THREADS:-2}"
    wait_policy="${TRAIN_FULL_OMP_WAIT_POLICY:-ACTIVE}"
    proc_bind="${TRAIN_FULL_OMP_PROC_BIND:-spread}"
  fi

  export TRAIN_CPU_SHARES="${TRAIN_CPU_SHARES:-$shares}"
  export TRAIN_NICE="${TRAIN_NICE:-$nice}"
  export TRAIN_IONICE_CLASS="${TRAIN_IONICE_CLASS:-$ionice_class}"
  export TRAIN_IONICE_LEVEL="${TRAIN_IONICE_LEVEL:-$ionice_level}"
  export TRAIN_INTEROP_THREADS="${TRAIN_INTEROP_THREADS:-$interop}"
  export TRAIN_OMP_WAIT_POLICY="${TRAIN_OMP_WAIT_POLICY:-$wait_policy}"
  export TRAIN_OMP_PROC_BIND="${TRAIN_OMP_PROC_BIND:-$proc_bind}"
  export TRAIN_OMP_PLACES="${TRAIN_OMP_PLACES:-cores}"
  export TRAIN_OMP_DYNAMIC="${TRAIN_OMP_DYNAMIC:-FALSE}"
  export TRAIN_MKL_DYNAMIC="${TRAIN_MKL_DYNAMIC:-FALSE}"
  export TRAIN_SCHEDULE_TZ="${TRAIN_SCHEDULE_TZ:-Europe/Warsaw}"
}

apply_scheduled_defaults
COMPOSE=(docker compose -f docker-compose.train.yml)

case "${1:-}" in
  shell)
    shift
    exec "${COMPOSE[@]}" run --rm trainer bash "$@"
    ;;
  smoke)
    shift
    exec "$SCRIPT_DIR/smoke_test_container.sh" "$@"
    ;;
  generate)
    shift
    exec "${COMPOSE[@]}" run --rm trainer python generate.py "$@"
    ;;
  resume)
    shift
    checkpoint="${1:-checkpoints/latest.pt}"
    if [[ "$#" -gt 0 ]]; then
      shift
    fi
    exec "${COMPOSE[@]}" run --rm trainer python train.py --resume "$checkpoint" "$@"
    ;;
  *)
    cat <<'EOF'
Usage:
  scripts/train_container.sh shell
  scripts/train_container.sh smoke
  scripts/train_container.sh generate "Stolica Polski to" --max-tokens 40
  scripts/train_container.sh resume checkpoints/latest.pt --max-steps 10

Resource schedule:
  weekdays 15:00-22:00 Europe/Warsaw: low priority, cpu_shares=256, nice=10, ionice=2:7
  weekends 08:00-22:00 Europe/Warsaw: low priority, cpu_shares=256, nice=10, ionice=2:7
  outside those windows: full priority, cpu_shares=2048, nice=0, ionice=2:0, OMP_WAIT_POLICY=ACTIVE

Long training is intentionally not the default.
EOF
    exit 2
    ;;
esac
