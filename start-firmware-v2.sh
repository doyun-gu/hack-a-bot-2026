#!/bin/bash
# Start firmware v2 improvement worker in tmux
# Usage: ./start-firmware-v2.sh

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

echo "========================================="
echo "  GridBox Firmware v2 Worker"
echo "  Project: $PROJECT_DIR"
echo "========================================="

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo "ERROR: tmux not installed. Run: brew install tmux"
    exit 1
fi

# Kill existing firmware session if any
tmux kill-session -t firmware-v2 2>/dev/null

echo "Starting v2 worker in tmux session 'firmware-v2'..."

tmux new-session -d -s firmware-v2 \
    "cd $PROJECT_DIR && claude \
    --dangerously-skip-permissions \
    --max-turns 150 \
    -p 'Read .claude/firmware-v2-task.md and execute all 5 tasks in order. Commit and push after each task. Pull latest main first with git pull origin main.'; \
    echo 'Worker finished. Press any key to close.'; \
    read"

echo "v2 Worker started!"
echo ""
echo "Commands:"
echo "  Watch:    tmux attach -t firmware-v2"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t firmware-v2"
