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

usage() {
  cat >&2 <<'EOF'
Użycie: run_decay_branch.sh --from-checkpoint PATH --out-dir PATH [--decay-steps INT] [--dry-run]
EOF
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-checkpoint) FROM="${2:-}"; shift 2 ;;
    --out-dir) OUT="${2:-}"; shift 2 ;;
    --decay-steps) DECAY_STEPS="${2:-}"; shift 2 ;;
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

# LR start/koniec liczone tym samym get_lr, co trening (ustawienia domyślne
# wariantu + wsd; gałąź nie podaje --learning-rate/--min-lr/--warmup-steps).
read -r LR_START LR_END VARIANT_USED <<<"$(
  cd "$ROOT" && "$PY" - "$CKPT_VARIANT" "$DECAY_START" "$DECAY_STEPS" "$END_STEP" <<'PY'
import sys
from config import get_train_config
from train import get_lr
variant, ds, dn, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
cfg = get_train_config(variant)
cfg.scheduler_type = "wsd"
cfg.decay_start_step = ds
cfg.decay_steps = dn
print(f"{get_lr(ds, cfg):.6e} {get_lr(end, cfg):.6e} {variant}")
PY
)"

TRAIN_CMD=("$PY" "$ROOT/train.py" --variant "$VARIANT_USED" --resume "$FROM"
  --scheduler wsd --decay-start-step "$DECAY_START" --decay-steps "$DECAY_STEPS"
  --max-steps "$END_STEP" --checkpoint-dir "$OUT_DIR" --log-dir "$OUT_DIR/logs"
  --allow-mismatch)

if [[ "$DRY_RUN" == "1" ]]; then
  cat <<EOF
dry-run gałęzi zjazdowej (nic nie zapisano):
  from-checkpoint : $FROM
  out-dir         : $OUT_DIR
  wariant         : $VARIANT_USED (ścieżki danych = domyślne wariantu)
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
