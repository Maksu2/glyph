#!/usr/bin/env bash
# Start training dashboard in background.
# Usage: ./web/start.sh
# Stop:  kill $(cat /tmp/polish-gpt-dashboard.pid)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/polish-gpt-dashboard.pid"
LOG="/tmp/polish-gpt-dashboard.log"
PORT=8181

# Stop existing instance if running
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping existing dashboard (PID $OLD_PID)..."
        kill "$OLD_PID"
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# Start server
nohup python3 "$SCRIPT_DIR/server.py" "$PORT" > "$LOG" 2>&1 &
echo $! > "$PID_FILE"
echo "Dashboard started (PID $(cat $PID_FILE)) → http://localhost:$PORT"
echo "Log: $LOG"
