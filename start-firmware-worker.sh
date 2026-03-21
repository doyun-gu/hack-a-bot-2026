#!/bin/bash
# Start firmware development worker in tmux
# Usage: ./start-firmware-worker.sh

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

echo "========================================="
echo "  GridBox Firmware Worker"
echo "  Project: $PROJECT_DIR"
echo "========================================="

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo "ERROR: tmux not installed. Run: brew install tmux"
    exit 1
fi

# Check claude
if ! command -v claude &> /dev/null; then
    echo "ERROR: claude CLI not found"
    exit 1
fi

# Kill existing session if any
tmux kill-session -t firmware 2>/dev/null

echo "Starting firmware worker in tmux session 'firmware'..."
echo ""

tmux new-session -d -s firmware \
    "cd $PROJECT_DIR && claude \
    --dangerously-skip-permissions \
    --max-turns 200 \
    -p 'Read the file .claude/firmware-task.md in this project. It contains 21 numbered tasks. Execute them all in order. After completing each task, commit and push to git. Start with Task 1 now.'; \
    echo 'Worker finished. Press any key to close.'; \
    read"

echo "Worker started!"
echo ""
echo "Commands:"
echo "  Watch:    tmux attach -t firmware"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t firmware"
echo ""
echo "The worker is running in the background."
echo "You can close this terminal safely."
