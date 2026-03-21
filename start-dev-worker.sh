#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  GridBox Dev Worker"
echo "========================================="

# Kill old sessions
tmux kill-session -t firmware 2>/dev/null
tmux kill-session -t firmware-v2 2>/dev/null
tmux kill-session -t dev-worker 2>/dev/null

tmux new-session -d -s dev-worker \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 150 \
    -p 'Read .claude/dev-tasks.md and execute all 6 tasks in order. Commit and push after each task. Pull latest main first.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'dev-worker'"
echo ""
echo "  Watch:    tmux attach -t dev-worker"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t dev-worker"
