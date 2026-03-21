#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  Dashboard Professional Redesign"
echo "========================================="

tmux kill-session -t dashboard 2>/dev/null

tmux new-session -d -s dashboard \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 50 \
    -p 'Read .claude/dashboard-redesign.md and completely rewrite src/web/templates/index.html following every instruction. Pull latest main first. The JavaScript update() function and chart drawing should be preserved but ALL styling, layout, and the power flow diagram must be rewritten. Commit and push when done.'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'dashboard'"
echo ""
echo "  Watch:    tmux attach -t dashboard"
echo "  Stop:     tmux kill-session -t dashboard"
echo ""
echo "  After it finishes, restart Flask:"
echo "    pkill -f app.py; sleep 2; python3 src/web/app.py --no-serial --mock"
echo "  Then Cmd+Shift+R in browser"
