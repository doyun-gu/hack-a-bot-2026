#!/bin/bash
cd "$(dirname "$0")"

tmux kill-session -t layout 2>/dev/null
tmux kill-session -t ui-polish 2>/dev/null

tmux new-session -d -s layout \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 60 \
    -p 'Pull latest main. Fix the web dashboard layout in src/web/templates/index.html.

PROBLEMS TO FIX:
1. Motor cards take 60% width, servo cards take 40% — they should ALL be equal width
2. Motor cards and servo cards are different heights — all cards in a row should be same height
3. Power flow diagram boxes are cut off on small screens
4. Production and Faults cards are not aligned with the cards above them
5. There is wasted empty space on the right side

LAYOUT RULES:
- Use a consistent 2-column grid for the ENTIRE page (grid-template-columns: 1fr 1fr)
- Every card in the same row must be the same height (use align-items: stretch on the grid)
- Row 1: Motor 1 (left) | Motor 2 (right) — same size
- Row 2: Servo 1 (left) | Servo 2 (right) — same size, same height as motor cards
- Row 3: Production (left) | Faults & Diagnostics (right) — same size
- Row 4: Power Flow diagram (full width, span 2 columns)
- Row 5: Power chart (left) | Current chart (right)
- No row should have uneven card widths
- Gap between cards: 8px
- Padding around grid: 12px

ALSO FIX THE MOCK DATA:
The dashboard shows dashes (--) even when mock data is running. The JavaScript update() function element IDs might not match the HTML. Verify every getElementById() call matches an actual element id in the HTML. The mock data sends: bus_v, m1_mA, m2_mA, m1_W, m2_W, total_W, efficiency, state, imu_rms, imu_status, es_score, m1_speed, m2_speed, mode, total_items, passed, rejected, reject_rate, faults_today.

ALSO FIX POWER FLOW:
- All boxes same size (140x44px)
- viewBox should be wide enough (960x280) so nothing is cut off
- Wires only horizontal and vertical
- No overlapping

Commit: \"Fix dashboard layout — consistent 2-column grid, same-size cards, working mock data\"'; \
    echo 'Done.'; read"

echo "Layout fix worker started: tmux attach -t layout"
