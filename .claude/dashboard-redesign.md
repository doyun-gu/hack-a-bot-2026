# Dashboard Professional Redesign — Worker Task

> Complete rewrite of src/web/templates/index.html. Make it look like a real industrial SCADA/HMI system, not a hacker tool.

## Design Direction

Reference: Siemens WinCC, Honeywell Experion, Grafana industrial dashboards. Clean, professional, muted.

## Rules

1. Pull latest main first
2. Replace the entire index.html content
3. Commit and push when done
4. Kill and restart Flask to test: `pkill -f "app.py"; sleep 2; python3 src/web/app.py --no-serial --mock`

## Colour Palette — NO NEON

| Use | Colour | Hex |
|---|---|---|
| Background | Very dark blue-grey | #0d1117 |
| Card background | Slightly lighter | #161b22 |
| Card border | Subtle | #21262d |
| Primary text | Off-white | #c9d1d9 |
| Secondary text | Muted grey | #8b949e |
| Label text | Dim grey | #484f58 |
| Healthy/OK | Muted green (not neon) | #3fb950 |
| Warning | Amber | #d29922 |
| Fault/Error | Muted red | #f85149 |
| Info/Blue | Calm blue | #58a6ff |
| Accent | Subtle purple | #a371f7 |
| Progress bar track | Dark grey | #21262d |

## Layout Changes

### Top Section: System Overview (single row, compact)
- System State badge (left)
- Bus Voltage with small circular gauge
- Total Power with small circular gauge
- Efficiency percentage
- IMU status badge
- Energy Signature status badge
- Uptime counter
- All in ONE row — no full-width cards wasting space

### Middle Section: Two Columns
**Left column: Motors & Actuators**
- Motor 1 card: name, current, power, speed — with a small horizontal bar
- Motor 2 card: same layout
- Servo 1 + Servo 2: compact inline, just angle + status

**Right column: Production & Faults**
- Production: total/pass/reject in a compact row with a donut chart for reject rate
- Fault log: last 3 fault events with timestamp (from database)

### Power Flow Diagram: SIMPLIFIED
Instead of trying to draw a complex circuit with overlapping wires, use a simple **linear flow** with status indicators:

```
[12V PSU] ──→ [Buck 5V] ──→ [Motor 1: 341mA ●]
    │                  ├──→ [Motor 2: 293mA ●]
    │                  ├──→ [Servo 1 ●] [Servo 2 ●]
    │                  └──→ [LEDs ●]
    └──→ [Boost 6-9V] ──→ [Motor Power Rail]

[IMU: 0.31g ●]  [ADC: OK ●]  [nRF: OK ●]  ──wireless──→  [SCADA Pico B ●]
```

Use a simple grid layout with coloured dots (green/yellow/red) instead of animated flowing wires. Dots are:
- Solid green circle = active and healthy
- Solid amber circle = warning
- Solid red circle = fault
- Grey circle with dashed border = inactive/off

The connections are simple grey lines (1px solid) between boxes — NOT overlapping, NOT animated. Clean and readable.

### Bottom: Charts (keep these — they look good)
- Power history chart (left half)
- Motor current chart (right half)
- Make them slightly taller (200px)

## Typography

Use Inter for all text. JetBrains Mono ONLY for numeric values.

| Element | Font | Size | Weight | Colour |
|---|---|---|---|---|
| Card label | Inter | 10px | 500 | #484f58 |
| Metric value | JetBrains Mono | 24px | 600 | #c9d1d9 |
| Unit text | Inter | 11px | 400 | #8b949e |
| Badge text | Inter | 9px | 600 | varies |
| Chart label | Inter | 9px | 400 | #484f58 |

## Power Flow Boxes

Each box in the power flow should be:
- Width: 140px, Height: 50px
- Background: #161b22
- Border: 1px solid #21262d (or status colour if active)
- Border-radius: 6px
- Title: 11px Inter 500, colour #c9d1d9
- Subtitle: 10px JetBrains Mono, colour = status colour (green/amber/red)
- Status dot: 8px circle, top-right corner inside the box

## Connections in Power Flow

- Simple 1px lines, colour #21262d (inactive) or #3fb950 (active)
- Lines go horizontally and vertically only (no diagonals)
- Use L-shaped paths with rounded corners if needed
- NO animated dots — too distracting and breaks professional look
- NO glow/shadow effects on connections

## Health Summary Bar (NEW)

At the very top, below the header, add a thin horizontal bar (24px tall) that shows overall system health at a glance:

```
[● PSU OK] [● Buck OK] [● M1 74%] [● M2 47%] [● S1 OK] [● S2 OK] [● IMU OK] [● ES OK] [● nRF OK] [● DB OK]
```

Each item is a small pill with a coloured dot. All green = system healthy. Any amber/red = immediately visible. This replaces the need to scan every card — one glance tells you the health.

## What NOT to Do

- NO neon green (#00ff88) anywhere
- NO glow effects / box-shadow with colour
- NO animated flowing dots on wires
- NO bright borders on boxes
- NO monospace font for labels (only for numbers)
- NO overlapping elements
- NO text on top of progress bars

Commit: `"Professional dashboard redesign — industrial SCADA look"`
