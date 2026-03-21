#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  C SDK Production Firmware Worker"
echo "========================================="

tmux kill-session -t c-sdk 2>/dev/null

tmux new-session -d -s c-sdk \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 200 \
    -p 'Read .claude/c-sdk-task.md and execute all 8 tasks in order. Commit and push after each task. Pull latest main first.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'c-sdk'"
echo ""
echo "  Watch:    tmux attach -t c-sdk"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t c-sdk"
