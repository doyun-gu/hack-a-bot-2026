#!/bin/bash
cd "$(dirname "$0")"

echo "========================================="
echo "  SVG Power Flow Diagram Worker"
echo "========================================="

tmux kill-session -t svg-flow 2>/dev/null

tmux new-session -d -s svg-flow \
    "cd $(pwd) && claude \
    --dangerously-skip-permissions \
    --max-turns 50 \
    -p 'Pull latest main first.

Replace the canvas-based power flow diagram in src/web/templates/index.html with an SVG-based version.

FIND the section starting at line ~315 with \"<!-- Power Flow Diagram -->\" and the <canvas class=\"flow-canvas\" id=\"power-flow\"></canvas>.

REPLACE the <canvas> with an inline <svg> element. Also REMOVE or disable the drawPowerFlow() JavaScript function (around line 461) since SVG replaces it. Keep the canvas hidden (display:none) so other code does not break.

SVG DESIGN RULES:
1. All wires are ORTHOGONAL — horizontal and vertical only, NO diagonals
2. Wires use L-shaped paths (M x1,y1 L x2,y1 L x2,y2 L x3,y2)
3. NO wires overlapping boxes — route wires through clear corridors between boxes
4. Boxes are spaced in a grid: 4 columns at x=30, x=230, x=460, x=680. Rows at y=40, y=110, y=180, y=250
5. Box size: 150x44px with rx=5 rounded corners
6. Background: #161b22, border: 1px solid colour, text in Inter/JetBrains Mono
7. Status dot: 4px circle at top-right of each box
8. Wire corridor: x=200 for column 1→2 connections, x=430 for column 2→3, x=650 for column 3→4
9. Animated power flow: use SVG <pattern> with <animate> to create moving dots along active wires
10. Inactive wires: stroke #21262d, no animation
11. Active wires: background stroke #21262d + animated pattern overlay
12. Wireless link: dashed line (#a371f7) with no animation
13. Colours: PSU=#58a6ff, Buck=#3fb950, Boost=#d29922, Motors=#3fb950/#58a6ff, Servos=#a371f7, LEDs=#3fb950, IMU=#3fb950, nRF=#a371f7, SCADA=#a371f7

LAYOUT (4 columns, 4 rows):
Column 1 (x=30): 12V PSU (row 2)
Column 2 (x=230): Buck Converter (row 1), Buck-Boost (row 3)
Column 3 (x=460): Motor 1 Fan (row 1), Motor 2 Conveyor (row 2), Servo 1+2 side by side (row 3), LEDs (row 4)
Column 4 (x=680): BMI160 IMU (row 1), ADC Sensing (row 2), nRF24L01+ (row 3), SCADA Pico B (row 4)

WIRE PATHS (all orthogonal, through corridors):
PSU → Buck: right from PSU to corridor x=200, up to row 1, right to Buck
PSU → Boost: right from PSU to corridor x=200, down to row 3, right to Boost
Buck → Motor 1: right from Buck to corridor x=430, stay at row 1, right to Motor 1
Buck → Motor 2: right from Buck to corridor x=430, down to row 2, right to Motor 2
Buck → Servos: right from Buck to corridor x=430, down to row 3, right to Servos
Buck → LEDs: right from Buck to corridor x=430, down to row 4, right to LEDs
Motor 1 → IMU: right from Motor 1 to corridor x=650, right to IMU (same row)
Motor 2 → ADC: right from Motor 2 to corridor x=650, right to ADC (same row)
nRF → SCADA: dashed line from nRF right side, down to SCADA

Give each text element an id (pf-m1-sub, pf-m2-sub, pf-imu-sub, pf-psu-sub, pf-led-sub, pf-nrf-sub) so the JavaScript can update values live.

Also update the JavaScript: in the update() function where it calls drawPowerFlow(), instead update the SVG text elements directly:
document.getElementById(\"pf-m1-sub\").textContent = m1.toFixed(0) + \"mA  \" + (d.m1_speed||0) + \"%\";
document.getElementById(\"pf-m2-sub\").textContent = m2.toFixed(0) + \"mA  \" + (d.m2_speed||0) + \"%\";
etc.

Commit: \"Replace canvas power flow with SVG — orthogonal wires, animated dots, no overlap\"'; \
    echo 'Done. Press any key.'; \
    read"

echo "Worker started in tmux session 'svg-flow'"
echo ""
echo "  Watch:    tmux attach -t svg-flow"
echo "  Progress: git log --oneline -3"
echo "  Stop:     tmux kill-session -t svg-flow"
