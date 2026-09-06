#!/usr/bin/env bash
set -euo pipefail

default_threads="$(nproc 2>/dev/null || echo 1)"
thread_count="${TRAIN_NUM_THREADS:-$default_threads}"

export TRAIN_NUM_THREADS="$thread_count"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-$thread_count}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-$thread_count}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-$thread_count}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-$thread_count}"
export TRAIN_INTEROP_THREADS="${TRAIN_INTEROP_THREADS:-1}"
export HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
export HF_DATASETS_CACHE="${HF_DATASETS_CACHE:-$HF_HOME/datasets}"
export TORCH_HOME="${TORCH_HOME:-/workspace/.cache/torch}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/workspace/.cache}"

mkdir -p "$HF_DATASETS_CACHE" "$TORCH_HOME" /workspace/logs /workspace/checkpoints

nice_level="${TRAIN_NICE:-10}"
ionice_class="${TRAIN_IONICE_CLASS:-2}"
ionice_level="${TRAIN_IONICE_LEVEL:-7}"

io_cmd=()
if command -v ionice >/dev/null 2>&1; then
  if [[ "$ionice_class" == "3" ]]; then
    io_cmd=(ionice -c 3)
  else
    io_cmd=(ionice -c "$ionice_class" -n "$ionice_level")
  fi
fi

exec "${io_cmd[@]}" nice -n "$nice_level" "$@"
