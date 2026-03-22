#!/bin/bash
cd /tmp/sentientforge
while true; do
    clear
    echo "=== SentientForge Overnight Run Status ==="
    echo "Time: $(date)"
    echo ""
    ps -p 76647 -o pid,etime,cmd 2>/dev/null || echo "Process not running"
    echo ""
    echo "--- Log File ($(wc -l < sentientforge-overnight.log 2>/dev/null || echo 0) lines) ---"
    tail -20 sentientforge-overnight.log 2>/dev/null
    echo ""
    echo "--- Results TSV ---"
    tail -5 results.tsv 2>/dev/null || echo "No results yet"
    sleep 10
done
