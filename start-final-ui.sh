#!/bin/bash
cd "$(dirname "$0")"

tmux kill-session -t final-ui 2>/dev/null
tmux kill-session -t layout 2>/dev/null
tmux kill-session -t ui-polish 2>/dev/null
tmux kill-session -t svg-flow 2>/dev/null
tmux kill-session -t dashboard 2>/dev/null

tmux new-session -d -s final-ui \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 80 \
    -p 'Pull latest main. You are fixing the web dashboard in src/web/templates/index.html.

READ THE CURRENT FILE FIRST. Then fix these specific issues:

ISSUE 1: POWER FLOW DIAGRAM
The drawPowerFlow() canvas function (around line 443) draws diagonal wires. FIX:
- ALL wires must be strictly horizontal or vertical — NO diagonals at all
- Use L-shaped paths: go horizontal first, then vertical, then horizontal
- PSU box is on the left. It connects to Buck (upper right) and Boost (lower right)
- The connection from PSU must go: RIGHT horizontally to a corridor x, then UP/DOWN vertically, then RIGHT horizontally to the target box
- Wire width: 2px for ALL wires — consistent, not varying
- Animated dots: small circles (radius 3px) that move along the wire path. Use requestAnimationFrame for smooth animation, not setInterval
- Each wire should have its OWN animated dot with different phase offsets so they dont all move together
- Dots should follow the orthogonal path (turn corners), not travel in straight lines
- Canvas resolution: set canvas.width and canvas.height to match offsetWidth and offsetHeight * devicePixelRatio for crisp rendering on retina displays
- Boxes: ALL same size (160x50px), rounded corners (6px), dark fill (#161b22), colored border (1.5px)
- Status dot: 6px circle inside box, top-right corner
- Text: title in 12px Inter semibold, subtitle in 10px JetBrains Mono with the status color
- Column labels at top in 9px uppercase grey

Layout grid (left to right):
Column 1 (x=30): 12V PSU
Column 2 (x=280): Buck Converter (y=40), Buck-Boost (y=200)
Column 3 (x=560): Motor 1 Fan (y=20), Motor 2 Conveyor (y=100), Servos PCA9685 (y=180), Status LEDs (y=260)

Wire corridors (vertical channels between columns):
Corridor A (x=220): connects PSU to both converters
Corridor B (x=500): connects converters to outputs

Wire paths (all orthogonal, using corridors):
PSU→Buck: right to x=220, up to y=65, right to x=280
PSU→Boost: right to x=220, down to y=225, right to x=280
Buck→Motor1: right to x=500, up to y=45, right to x=560
Buck→Motor2: right to x=500, stay at y=125, right to x=560  (separate vertical line from Buck)
Buck→Servos: right to x=500, down to y=205, right to x=560
Buck→LEDs: right to x=500, down to y=285, right to x=560

ISSUE 2: RETINA DISPLAY RESOLUTION
Canvas looks blurry because it does not account for devicePixelRatio. Fix:
const dpr = window.devicePixelRatio || 1;
canvas.width = canvas.offsetWidth * dpr;
canvas.height = canvas.offsetHeight * dpr;
ctx.scale(dpr, dpr);
Then draw using CSS pixel coordinates — the scaling handles retina automatically.

ISSUE 3: CARD LAYOUT
All cards must be consistent width. Use a simple 2-column CSS grid:
.main-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 12px; }
.full-width { grid-column: 1 / -1; }

Row 1: Motor 1 | Motor 2 (same height)
Row 2: Servo 1 | Servo 2 (same height, same as motor cards)
Row 3: Production (full width)
Row 4: Faults & Diagnostics (full width)
Row 5: Power Flow (full width)
Row 6: Chart left | Chart right

ISSUE 4: MORE INFORMATION ON POWER FLOW BOXES
Each box should show:
- Motor 1: name, current (mA), speed (%), power (W)
- Motor 2: same
- PSU: voltage, total power, efficiency
- Buck: input→output voltage
- Boost: input→output voltage
- Servos: channel count, status
- LEDs: system state

ISSUE 5: ABOUT MODAL
The About modal content should also include:
- Version: v2.0
- GitHub link should be clickable
- Add a line: Built with MicroPython + C SDK on RP2350

Commit: \"Final UI fix — crisp retina rendering, orthogonal wires, consistent layout\"
Then restart test: pkill -f app.py; sleep 2; python3 src/web/app.py --no-serial --mock'; \
    echo 'Done.'; read"

echo "Final UI worker: tmux attach -t final-ui"
