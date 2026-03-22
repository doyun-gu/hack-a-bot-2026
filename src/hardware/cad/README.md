# CAD Designs — GridCell Battery Recovery Factory

All 3D printable parts for the sorting conveyor system.

---

## Folder Structure

```
cad/
├── fast-print/       ← Low-poly STLs for quick printing (small file size)
├── full-design/      ← High-detail STLs for final build
└── servo-mg90s/      ← MG90S servo reference model (STEP + photos)
```

---

## Parts List

### Fast Print (Low Poly — for test prints)

| File | What It Is |
|------|-----------|
| `bearing.stl` | Roller bearing for conveyor |
| `block.stl` | Mounting block |
| `fast side.stl` | Side panel (simplified) |
| `motor.stl` | Motor mount |
| `side bar.stl` | Side rail for conveyor |
| `slope.stl` | Ramp/chute for sorting output |
| `sort body.stl` | Main sorting body — holds servo push arms |

### Full Design (High Detail — for final build)

**STL Files (3D printable):**

| File | What It Is |
|------|-----------|
| `Bearing.stl` | Roller bearing (detailed) |
| `conveyortmotor.stl` | Conveyor motor mount assembly |
| `funnel.stl` | Intake funnel/hopper — where judge drops batteries |
| `motorlowerqual.stl` | Motor mount (lower section) |
| `sidebar.stl` | Side rail (detailed) |
| `slope.stl` | Output ramp/chute |
| `sort.stl` | Sorting mechanism body |

**STEP Files (editable in Fusion 360 / SolidWorks):**

| File | What It Is |
|------|-----------|
| `Belt Cover v5.step` | Belt cover / guard panel |
| `Conveyor Bearing v2.step` | Conveyor roller bearing assembly |
| `Conveyor motor v5.step` | Full conveyor motor mount |
| `Objects v2.step` | Sorting objects / battery props |
| `Sorter v3.step` | Sorting mechanism (latest version) |
| `Wheel v1.step` | Conveyor wheel / roller |

**Assembly Drawing:**

| File | What It Is |
|------|-----------|
| `Assemble.dxf` | Full assembly drawing — open in Fusion 360 or AutoCAD |

### Servo Reference Model (MG90S)

| File | What It Is |
|------|-----------|
| `Tower Pro MG90S Micro servo.STEP` | Full servo CAD model — import into Fusion 360 |
| `Bidirectional shoulder.STEP` | Servo horn — 2 directions |
| `Four directed shoulder.STEP` | Servo horn — 4 directions (cross) |
| `Unidirectional shoulder.STEP` | Servo horn — single arm |
| `Tower Pro MG90S micro servo 1.JPG` | Reference photo (front) |
| `Tower Pro MG90S micro servo 2.JPG` | Reference photo (side) |

---

## How The Parts Fit Together

```
                    FUNNEL (intake hopper)
                       |
                       v
    ┌──────────────────────────────────────┐
    │  SORT BODY (holds servo push arms)   │
    │                                      │
    │  BEARING ──── CONVEYOR ──── BEARING  │
    │               MOTOR                  │
    │                                      │
    │  SIDE BAR ────────────── SIDE BAR    │
    └──────────────────────────────────────┘
         |            |            |
         v            v            v
       SLOPE        SLOPE        SLOPE
       (bin 1)      (bin 2)      (bin 3)
       HAZMAT       HEAVY        LIGHT
```

---

## Print Settings (Recommended)

| Setting | Fast Print | Full Design |
|---------|-----------|-------------|
| Layer Height | 0.3mm | 0.2mm |
| Infill | 15% | 25% |
| Supports | No | Yes (for funnel) |
| Material | PLA | PLA or PETG |
| Est. Time | ~2 hours total | ~6 hours total |

---

## Servo Mount Notes

- The MG90S servo STEP file can be imported into Fusion 360 to check fitment
- Servo horns snap onto the servo spline (no screws needed for testing)
- Use the **Unidirectional shoulder** for push arms (sorting)
- Use the **Bidirectional shoulder** for gates (intake/HVAC dampers)
- Mount servos with M2 screws through the mounting tabs

---

## Source

- Sorting conveyor: Billy's custom Fusion 360 design
- MG90S servo model: [GrabCAD - Tower Pro MG90S](https://grabcad.com/library/tower-pro-mg90s-micro-servo-2)
