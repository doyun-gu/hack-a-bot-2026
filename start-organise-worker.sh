#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  GridBox Organisation Worker"
echo "========================================="

tmux kill-session -t organise 2>/dev/null

tmux new-session -d -s organise \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 150 \
    -p 'Read .claude/organise-tasks.md and execute all 7 tasks in order. Commit and push after each task that needs it. Pull latest main first.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'organise'"
echo ""
echo "  Watch:    tmux attach -t organise"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -10"
echo "  Stop:     tmux kill-session -t organise"
