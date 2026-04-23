#!/bin/bash
# OmniForge — Monitor experiment run status
# Usage: ./check_status.sh [pid]

cd "$(dirname "$0")"

if [ -n "$1" ]; then
    WATCH_PID="$1"
else
    # Find the most recent experiment.py process
    WATCH_PID=$(pgrep -f "python.*experiment.py" | head -1)
fi

while true; do
    clear
    echo "=== OmniForge Run Status ==="
    echo "Time: $(date)"
    echo ""

    if [ -n "$WATCH_PID" ]; then
        ps -p "$WATCH_PID" -o pid,etime,cmd 2>/dev/null || echo "Process $WATCH_PID not running"
    else
        echo "No experiment process found. Start with: python3 experiment.py --tag <name>"
    fi

    echo ""
    echo "--- Results ($(wc -l < results.tsv 2>/dev/null || echo 0) rows) ---"
    tail -5 results.tsv 2>/dev/null || echo "No results yet"
    sleep 10
done