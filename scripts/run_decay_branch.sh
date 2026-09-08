#!/usr/bin/env bash
# Gałąź zjazdowa WSD z checkpointu głównej linii.
#
# Bierze checkpoint (typowo stable, decay_start_step=None) i robi z niego
# krótki annealing liniowy do min_lr. NIE dotyka katalogu źródłowego:
# zapis wyłącznie do --out-dir, a nadpisanie latest.pt głównej linii
# jest zablokowane twardym warunkiem.
#
# Użycie:
#   scripts/run_decay_branch.sh --from-checkpoint PATH --out-dir PATH
#       [--decay-steps INT] [--dry-run]
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
[[ -x "$PY" ]] || PY="python3"

FROM=""; OUT=""; DECAY_STEPS=500; DRY_RUN=0
DATA_PATH=""; VAL_DATA_PATH=""; DATASET_METADATA_PATH=""; DATASET_NAME=""; TOKENIZER_PATH=""

usage() {
  cat >&2 <<'EOF'
Użycie: run_decay_branch.sh --from-checkpoint PATH --out-dir PATH [--decay-steps INT]
    [--data-path P] [--val-data-path P] [--dataset-metadata-path P]
    [--dataset-name N] [--tokenizer-path P] [--dry-run]
Ścieżki danych jak w train.py; brak = domyślne wariantu z checkpointu.
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-checkpoint) FROM="${2:-}"; shift 2 ;;
    --out-dir) OUT="${2:-}"; shift 2 ;;
    --decay-steps) DECAY_STEPS="${2:-}"; shift 2 ;;
    --data-path) DATA_PATH="${2:-}"; shift 2 ;;
    --val-data-path) VAL_DATA_PATH="${2:-}"; shift 2 ;;
    --dataset-metadata-path) DATASET_METADATA_PATH="${2:-}"; shift 2 ;;
    --dataset-name) DATASET_NAME="${2:-}"; shift 2 ;;
    --tokenizer-path) TOKENIZER_PATH="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage ;;
    *) echo "nieznana flaga: $1" >&2; usage ;;
  esac
done

[[ -n "$FROM" && -n "$OUT" ]] || usage
[[ -f "$FROM" ]] || { echo "brak checkpointu: $FROM" >&2; exit 2; }
[[ "$DECAY_STEPS" =~ ^[0-9]+$ && "$DECAY_STEPS" -gt 0 ]] \
  || { echo "--decay-steps musi być dodatnią liczbą całkowitą" >&2; exit 2; }

# Meta checkpointu — WYŁĄCZNIE odczyt (torch.load, bez zapisu).
read -r CKPT_STEP CKPT_VARIANT CKPT_DECAY_START <<<"$(
  "$PY" - "$FROM" <<'PY'
import sys
import torch
state = torch.load(sys.argv[1], map_location="cpu", weights_only=False)
print(state.get("step"), state.get("variant") or "glyph-100m",
      (state.get("scheduler_state") or {}).get("decay_start_step"))
PY
)"
[[ "$CKPT_STEP" =~ ^[0-9]+$ ]] || { echo "nieczytelny step checkpointu" >&2; exit 2; }
DECAY_START="$CKPT_STEP"
END_STEP=$((CKPT_STEP + DECAY_STEPS))

# TWARDY WARUNEK: out-dir rozłączny z katalogiem źródłowym i bez latest.pt.
SRC_DIR="$(realpath "$(dirname "$FROM")")"
OUT_DIR="$(realpath -m "$OUT")"
if [[ "$OUT_DIR" == "$SRC_DIR" ]]; then
  echo "BŁĄD: --out-dir to katalog checkpointu źródłowego ($SRC_DIR); odmowa zapisu." >&2
  exit 2
fi
case "$OUT_DIR/" in
  "$SRC_DIR/"*) echo "BŁĄD: --out-dir leży WEWNĄTRZ katalogu źródłowego; odmowa zapisu." >&2; exit 2 ;;
esac
case "$SRC_DIR/" in
  "$OUT_DIR/"*) echo "BŁĄD: katalog źródłowy leży wewnątrz --out-dir; odmowa zapisu." >&2; exit 2 ;;
esac
if [[ -e "$OUT_DIR/latest.pt" ]]; then
  echo "BŁĄD: $OUT_DIR/latest.pt już istnieje; gałąź nie nadpisze cudzego latest.pt." >&2
  exit 2
fi

# Efektywne ścieżki danych: jawne flagi albo domyślne wariantu z checkpointu.
# LR start/koniec liczone tym samym get_lr, co trening.
read -r LR_START LR_END VARIANT_USED EFF_DATA_PATH <<<"$(
  cd "$ROOT" && "$PY" - "$CKPT_VARIANT" "$DECAY_START" "$DECAY_STEPS" "$END_STEP" \
      "$DATA_PATH" "$VAL_DATA_PATH" "$DATASET_METADATA_PATH" "$DATASET_NAME" "$TOKENIZER_PATH" <<'PY'
import sys
from config import get_train_config
from train import get_lr
variant, ds, dn, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
data_path, val_data_path, meta_path, ds_name, tok_path = sys.argv[5:10]
cfg = get_train_config(variant)
cfg.scheduler_type = "wsd"
cfg.decay_start_step = ds
cfg.decay_steps = dn
if data_path:
    cfg.data_path = data_path
if val_data_path:
    cfg.val_data_path = val_data_path
if meta_path:
    cfg.dataset_metadata_path = meta_path
if ds_name:
    cfg.dataset_name = ds_name
if tok_path:
    cfg.tokenizer_path = tok_path
print(f"{get_lr(ds, cfg):.6e} {get_lr(end, cfg):.6e} {variant} {cfg.data_path}")
PY
)"

TRAIN_CMD=("$PY" "$ROOT/train.py" --variant "$VARIANT_USED" --resume "$FROM"
  --scheduler wsd --decay-start-step "$DECAY_START" --decay-steps "$DECAY_STEPS"
  --max-steps "$END_STEP" --checkpoint-dir "$OUT_DIR" --log-dir "$OUT_DIR/logs"
  --allow-mismatch)
[[ -n "$DATA_PATH" ]] && TRAIN_CMD+=(--data-path "$DATA_PATH")
[[ -n "$VAL_DATA_PATH" ]] && TRAIN_CMD+=(--val-data-path "$VAL_DATA_PATH")
[[ -n "$DATASET_METADATA_PATH" ]] && TRAIN_CMD+=(--dataset-metadata-path "$DATASET_METADATA_PATH")
[[ -n "$DATASET_NAME" ]] && TRAIN_CMD+=(--dataset-name "$DATASET_NAME")
[[ -n "$TOKENIZER_PATH" ]] && TRAIN_CMD+=(--tokenizer-path "$TOKENIZER_PATH")

if [[ "$DRY_RUN" == "1" ]]; then
  cat <<EOF
dry-run gałęzi zjazdowej (nic nie zapisano):
  from-checkpoint : $FROM
  out-dir         : $OUT_DIR
  wariant         : $VARIANT_USED
  bin treningowy  : $EFF_DATA_PATH
  kroki           : $CKPT_STEP -> $END_STEP (zjazd $DECAY_STEPS kroków)
  decay_start_step: $DECAY_START (step checkpointu)
  LR start        : $LR_START
  LR koniec       : $LR_END
  wynik           : $OUT_DIR/step_$(printf '%07d' "$END_STEP").pt (ostatni wg harmonogramu)
  komenda         : ${TRAIN_CMD[*]}
EOF
  exit 0
fi

mkdir -p "$OUT_DIR"
echo "Gałąź startuje zjazd WSD (decay_start_step=$DECAY_START), a checkpoint ma decay_start_step=$CKPT_DECAY_START — rozjazd zamierzony, resume z --allow-mismatch."
"${TRAIN_CMD[@]}"
result="$(ls -1 "$OUT_DIR"/step_*.pt 2>/dev/null | sort | tail -n 1 || true)"
[[ -n "$result" ]] || { echo "BŁĄD: brak checkpointu wynikowego w $OUT_DIR" >&2; exit 1; }
echo "$result"
