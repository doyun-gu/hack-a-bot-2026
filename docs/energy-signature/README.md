# Energy Signature — Fault Detection System (by Wooseong)

Current-based fault detection using motor energy signatures. Complements the IMU vibration approach — two independent detection methods with sensor fusion.

| File | Contents |
|---|---|
| [`energy-signature-proposal.md`](energy-signature-proposal.md) | Refined proposal — 30s learning, zero-crossing, 500Hz sampling, divergence scoring, demo script |
| [`fault-models.md`](fault-models.md) | All 4 fault models (A-D) with quantitative analysis, expected values, detection logic |
| [`model-a-mechanical-load.md`](model-a-mechanical-load.md) | Deep dive on Model A — mechanical load increase (primary demo fault) |

## Key Concept

Every motor draws current in a unique pattern. Learn the healthy pattern (30s), then detect deviations:

| Metric | What It Catches |
|---|---|
| Mean current shift | Mechanical load (jam, blockage) |
| Std current spike | Intermittent connection (loose wire) |
| Crossing rate change | Speed change (supply sag, bearing wear) |
| Max deviation | Current peaks (overload, resistance) |

## Review Notes (from Doyun)

- **Approved and merged** — solid quantitative work with IEEE 493 references
- **Open issue:** Voltage divider needs 3:1 ratio (20kΩ+10kΩ) not 2:1 for 12V bus safety
- **Open issue:** "Health needle" servo needs to use OLED/LEDs instead (only 2 servos available)
- **Scope decision:** Energy signature is P1 (core) — implement after basic motor control works
