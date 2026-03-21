# Hardware

## Folder Structure

```
hardware/
├── electronics/              ← WOOSEONG's workspace
│   ├── README.md             ← Pin reference, task list, wiring guide
│   ├── circuits/             ← Schematics, circuit diagrams
│   ├── testing/              ← Test results, measurements
│   └── photos/               ← Wiring progress photos
│
├── chassis/                  ← BILLY's workspace
│   ├── README.md             ← Dimensions, print checklist, task list
│   ├── cad-files/            ← Source CAD (Fusion 360, OnShape)
│   ├── stl-exports/          ← Ready-to-print STL files
│   ├── assembly/             ← Assembly instructions, notes
│   └── photos/               ← Build progress photos
│
├── wiring/                   ← Shared wiring diagrams
├── datasheets/               ← Component datasheets (BMI160, PCA9685, etc.)
└── README.md                 ← This file
```

## Who Works Where

| Person | Their Folder | What They Put There |
|---|---|---|
| **Wooseong** | `electronics/` | Circuit schematics, wiring photos, test results, measurements |
| **Billy** | `chassis/` | CAD files, STL exports, assembly photos, dimension notes |
| **Both** | `wiring/` | Shared wiring diagrams that connect electronics to chassis |
| **Both** | `datasheets/` | Component datasheets for reference |

## Rules

1. **Stay in your folder** — don't edit files in the other person's folder
2. **Photos in your folder** — not in the root `media/` (unless it's final demo photos)
3. **Name files clearly** — `motor_mount_v2.stl` not `thing.stl`
4. **Commit often** — every finished part, every successful test

## Pin Mapping (Quick Reference)

See `electronics/README.md` for full pin-by-pin wiring table.

| Pico A Function | Pin | Protocol |
|---|---|---|
| I2C SDA (IMU + PCA) | GP4 | I2C0 |
| I2C SCL (IMU + PCA) | GP5 | I2C0 |
| SPI (nRF24L01+) | GP0-3, GP16 | SPI0 |
| Motor switches | GP10-13 | GPIO → MOSFET |
| ADC sensing | GP26-28 | ADC |
| Status LEDs | GP14-15 | GPIO |
