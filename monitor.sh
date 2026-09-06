#!/usr/bin/env bash
# monitor.sh — Live training status dashboard
# Usage: ./monitor.sh [--watch]
# With --watch: refresh every 10 seconds. Without: print once and exit.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/train.log"
FT_LOG_FILE="$SCRIPT_DIR/logs/finetune.log"
PID_FILE="$SCRIPT_DIR/train.pid"
CHECKPOINT_DIR="$SCRIPT_DIR/checkpoints"
TOKENS_BIN="$SCRIPT_DIR/data/processed/tokens.bin"

WATCH=false
if [[ "${1:-}" == "--watch" ]]; then
    WATCH=true
fi

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

print_status() {
    local now
    now="$(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${BOLD}╔══════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}║           Glyph-27M — Training Monitor           ║${RESET}"
    echo -e "${BOLD}╚══════════════════════════════════════════════════╝${RESET}"
    echo -e "  ${CYAN}Time:${RESET} $now"
    echo ""

    # ── Process status ──────────────────────────────────────────────
    echo -e "${BOLD}[ Process ]${RESET}"
    local train_pid=""
    local finetune_pid=""

    # Find train.py process
    train_pid=$(pgrep -f "python.*train\.py" 2>/dev/null | head -1 || true)
    finetune_pid=$(pgrep -f "python.*finetune\.py" 2>/dev/null | head -1 || true)

    if [[ -n "$train_pid" ]]; then
        local cpu_usage ram_usage
        cpu_usage=$(ps -p "$train_pid" -o %cpu --no-headers 2>/dev/null | tr -d ' ' || echo "?")
        ram_usage=$(ps -p "$train_pid" -o rss --no-headers 2>/dev/null | awk '{printf "%.0f MB", $1/1024}' || echo "?")
        echo -e "  ${GREEN}● train.py running${RESET} (PID $train_pid) | CPU: ${cpu_usage}% | RAM: ${ram_usage}"
    else
        echo -e "  ${RED}● train.py not running${RESET}"
    fi

    if [[ -n "$finetune_pid" ]]; then
        local cpu_usage ram_usage
        cpu_usage=$(ps -p "$finetune_pid" -o %cpu --no-headers 2>/dev/null | tr -d ' ' || echo "?")
        ram_usage=$(ps -p "$finetune_pid" -o rss --no-headers 2>/dev/null | awk '{printf "%.0f MB", $1/1024}' || echo "?")
        echo -e "  ${GREEN}● finetune.py running${RESET} (PID $finetune_pid) | CPU: ${cpu_usage}% | RAM: ${ram_usage}"
    fi

    echo ""

    # ── System RAM ──────────────────────────────────────────────────
    echo -e "${BOLD}[ System Memory ]${RESET}"
    free -h | awk '
        /^Mem:/ { printf "  Total: %s  Used: %s  Free: %s  Available: %s\n", $2, $3, $4, $7 }
        /^Swap:/ { printf "  Swap: %s total, %s used\n", $2, $3 }
    '
    echo ""

    # ── Training log ────────────────────────────────────────────────
    echo -e "${BOLD}[ Pre-training Log — last 10 lines ]${RESET}"
    if [[ -f "$LOG_FILE" ]]; then
        # Extract and display last 10 log lines
        tail -n 10 "$LOG_FILE" | sed 's/^/  /'

        echo ""
        # Extract latest loss and step from log
        local last_step last_loss last_tokps
        last_step=$(grep -oP "step=\s*\K[0-9]+" "$LOG_FILE" 2>/dev/null | tail -1 || echo "0")
        last_loss=$(grep -oP "loss=\K[0-9]+\.[0-9]+" "$LOG_FILE" 2>/dev/null | tail -1 || echo "N/A")
        last_tokps=$(grep -oP "tok/s=\K[0-9,]+" "$LOG_FILE" 2>/dev/null | tail -1 || echo "N/A")

        echo -e "${BOLD}[ Latest Stats ]${RESET}"
        echo -e "  ${CYAN}Step:${RESET}     $last_step"
        echo -e "  ${CYAN}Loss:${RESET}     $last_loss"
        echo -e "  ${CYAN}Tok/s:${RESET}    $last_tokps"
    else
        echo -e "  ${YELLOW}No training log found at $LOG_FILE${RESET}"
        echo -e "  Start training with: python train.py"
    fi
    echo ""

    # ── Fine-tuning log ─────────────────────────────────────────────
    if [[ -f "$FT_LOG_FILE" ]]; then
        echo -e "${BOLD}[ Fine-tuning Log — last 5 lines ]${RESET}"
        tail -n 5 "$FT_LOG_FILE" | sed 's/^/  /'
        echo ""
    fi

    # ── Checkpoints ─────────────────────────────────────────────────
    echo -e "${BOLD}[ Checkpoints ]${RESET}"
    if [[ -d "$CHECKPOINT_DIR" ]]; then
        local n_ckpts
        n_ckpts=$(find "$CHECKPOINT_DIR" -name "*.pt" -not -name "latest.pt" -not -name "*_tmp*" 2>/dev/null | wc -l)
        echo -e "  Saved checkpoints: $n_ckpts"

        # Latest checkpoint info
        local latest="$CHECKPOINT_DIR/latest.pt"
        if [[ -f "$latest" ]]; then
            local size mtime
            size=$(du -sh "$latest" 2>/dev/null | cut -f1 || echo "?")
            mtime=$(stat -c '%y' "$latest" 2>/dev/null | cut -d'.' -f1 || echo "?")
            echo -e "  Latest: $size  (modified: $mtime)"
        fi

        # List 3 most recent checkpoints
        echo -e "  Recent:"
        find "$CHECKPOINT_DIR" -name "step_*.pt" 2>/dev/null \
            | sort -t_ -k2 -n | tail -3 \
            | while read -r f; do
                sz=$(du -sh "$f" 2>/dev/null | cut -f1 || echo "?")
                echo -e "    $(basename "$f")  ($sz)"
            done
    else
        echo -e "  ${YELLOW}No checkpoints directory found${RESET}"
    fi
    echo ""

    # ── Dataset info ────────────────────────────────────────────────
    echo -e "${BOLD}[ Dataset ]${RESET}"
    if [[ -f "$TOKENS_BIN" ]]; then
        local size_bytes n_tokens
        size_bytes=$(stat -c '%s' "$TOKENS_BIN" 2>/dev/null || echo "0")
        n_tokens=$(( size_bytes / 2 ))
        echo -e "  tokens.bin: $(du -sh "$TOKENS_BIN" | cut -f1) (~${n_tokens} uint16 tokens)"
    else
        echo -e "  ${YELLOW}tokens.bin not found — run: python data/download.py && python data/preprocess.py${RESET}"
    fi
    echo ""

    # ── Quick commands ───────────────────────────────────────────────
    echo -e "${BOLD}[ Quick Commands ]${RESET}"
    echo -e "  Start training:      ${CYAN}nohup python train.py > /dev/null 2>&1 &${RESET}"
    echo -e "  Resume training:     ${CYAN}nohup python train.py --resume > /dev/null 2>&1 &${RESET}"
    echo -e "  Fine-tune:           ${CYAN}python finetune.py --base checkpoints/latest.pt${RESET}"
    echo -e "  Generate text:       ${CYAN}python generate.py \"Stolica Polski to\"${RESET}"
    echo -e "  Kill training:       ${CYAN}pkill -SIGTERM -f 'python.*train.py'${RESET}"
    echo ""
}

if $WATCH; then
    echo "Watching (Ctrl+C to stop) ..."
    while true; do
        clear
        print_status
        sleep 10
    done
else
    print_status
fi
