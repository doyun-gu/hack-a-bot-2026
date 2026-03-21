#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  UI Polish Worker"
echo "========================================="

tmux kill-session -t ui-polish 2>/dev/null
tmux kill-session -t svg-flow 2>/dev/null
tmux kill-session -t dashboard 2>/dev/null

tmux new-session -d -s ui-polish \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 80 \
    -p 'Pull latest main first. Edit ONLY src/web/templates/index.html.

Do these tasks IN ORDER. Commit and push after each.

TASK 1: Remove the overview-row section entirely (the row with gauges, bus voltage, total power, efficiency, IMU badge, ES badge, uptime). This info is already shown in the main cards below. The overview row is redundant. Remove the CSS for .overview-row, .ov-item, .ov-sep, .ov-label, .ov-val, .ov-unit, .ov-item-gauge too.
Commit: \"Remove redundant overview row — info already in main cards\"

TASK 2: Add a light/dark mode toggle. Add a small button in the top-right of the header (before the state badge) that toggles between dark and light theme. Use CSS variables for all colours:
- Dark: bg=#0d1117, card=#161b22, border=#21262d, text=#c9d1d9
- Light: bg=#ffffff, card=#f6f8fa, border=#d0d7de, text=#1f2328
Store preference in localStorage. Default to dark.
The toggle should be a small icon or text: a moon icon for dark, sun for light (use unicode: dark=☾ light=☀).
Commit: \"Add dark/light mode toggle with localStorage\"

TASK 3: Add an About section. In the top-right corner of the header, add a small \"About\" link that opens a modal overlay showing:
- GridBox — Smart Infrastructure Control System
- Hack-A-Bot 2026 — Project 6: Creative — Group 1
- Team: Doyun Gu (System Designer), Wooseong Jung (Electronics), Billy Park (Mechanical)
- University of Manchester
- GitHub: github.com/doyun-gu/hack-a-bot-2026
- Close button (X or click outside)
Keep it minimal — dark semi-transparent overlay with a centred card.
Commit: \"Add About modal with team info\"

TASK 4: Fix any remaining issues with the power flow canvas. The drawPowerFlow JavaScript function should be updated or removed if the SVG version exists. If there is still a canvas element, hide it. Make sure the SVG power flow (if it exists from another worker) displays properly. If no SVG exists yet, keep the canvas but fix the layout:
- All boxes SAME SIZE (150x48px)
- Wires only horizontal and vertical (no diagonals)
- No overlapping
- Animated dots flowing along active wires
Commit: \"Fix power flow diagram — consistent boxes, no overlap\"

TASK 5: Overall visual polish:
- Make all cards the same height within each row (use min-height)
- Remove any remaining neon green (#00ff88) — replace with muted green (#3fb950)
- Ensure progress bars are visible but not distracting (4px height, no labels on bar)
- Clean up any CSS that is no longer used
- Test that dark mode and light mode both look good
Commit: \"Visual polish — consistent cards, remove neon, clean CSS\"
'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'ui-polish'"
echo ""
echo "  Watch:    tmux attach -t ui-polish"
echo "  Progress: git log --oneline -5"
echo "  Stop:     tmux kill-session -t ui-polish"
