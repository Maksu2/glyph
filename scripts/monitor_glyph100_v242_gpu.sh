#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=/home/maksu/ai-model
SESSION=${1:-glyph100-v242-15k}
LOG=${2:-$ROOT/logs/glyph-100m-v2_4_2-15k/gpu_metrics.log}
HWMON=${3:-/sys/class/drm/card1/device/hwmon/hwmon3}
HOTSPOT_STOP_C=${GLYPH_HOTSPOT_STOP_C:-103}
HOTSPOT_STOP_SAMPLES=${GLYPH_HOTSPOT_STOP_SAMPLES:-3}
STOP_REPORT=$(dirname "$LOG")/temperature_stop.json

mkdir -p "$(dirname "$LOG")"
if [[ ! -s "$LOG" ]]; then
  printf 'timestamp,edge_c,hotspot_c,fan_rpm,power_w,gpu_busy_pct,vram_used_bytes\n' > "$LOG"
fi

read_value() {
  local path=$1
  local scale=${2:-1}
  if [[ -r "$path" ]]; then
    awk -v scale="$scale" '{ printf "%.3f", $1 / scale }' "$path"
  else
    printf ''
  fi
}

hotspot_streak=0
while tmux list-sessions -F '#S' 2>/dev/null | grep -Fxq "$SESSION"; do
  timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  edge=$(read_value "$HWMON/temp1_input" 1000)
  hotspot=$(read_value "$HWMON/temp2_input" 1000)
  fan=$(read_value "$HWMON/fan1_input" 1)
  power=$(read_value "$HWMON/power1_average" 1000000)
  busy=$(read_value /sys/class/drm/card1/device/gpu_busy_percent 1)
  vram=$(read_value /sys/class/drm/card1/device/mem_info_vram_used 1)
  printf '%s,%s,%s,%s,%s,%s,%s\n' \
    "$timestamp" "$edge" "$hotspot" "$fan" "$power" "$busy" "$vram" \
    >> "$LOG"

  if [[ -n "$hotspot" ]] && awk -v value="$hotspot" -v limit="$HOTSPOT_STOP_C" 'BEGIN { exit !(value >= limit) }'; then
    hotspot_streak=$((hotspot_streak + 1))
  else
    hotspot_streak=0
  fi

  if (( hotspot_streak >= HOTSPOT_STOP_SAMPLES )); then
    tmp_report="$STOP_REPORT.tmp"
    printf '{\n  "reason": "sustained_gpu_hotspot",\n  "timestamp_utc": "%s",\n  "hotspot_c": %s,\n  "threshold_c": %s,\n  "consecutive_samples": %s,\n  "action": "SIGINT sent to tmux training session"\n}\n' \
      "$timestamp" "$hotspot" "$HOTSPOT_STOP_C" "$hotspot_streak" > "$tmp_report"
    mv "$tmp_report" "$STOP_REPORT"
    tmux send-keys -t "$SESSION" C-c
    break
  fi
  sleep 30
done
