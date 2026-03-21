#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  Conveyor Belt Calculation Worker"
echo "========================================="

tmux kill-session -t conveyor 2>/dev/null

tmux new-session -d -s conveyor \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 100 \
    -p 'Read .claude/conveyor-calc-task.md and execute the task. Pull latest main first with git pull origin main. Write all calculations to docs/03-factory/conveyor-calculations.md with LaTeX equations, Mermaid diagrams, and tables. Commit and push when done.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'conveyor'"
echo ""
echo "  Watch:    tmux attach -t conveyor"
echo "  Detach:   Ctrl+B then D"
echo "  Progress: git log --oneline -5"
echo "  Stop:     tmux kill-session -t conveyor"
