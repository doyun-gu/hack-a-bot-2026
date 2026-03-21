# Chassis & Mechanical — Billy's Workspace

## Folder Structure

| Folder | What Goes Here |
|---|---|
| `cad-files/` | Source CAD files (Fusion 360 .f3d, OnShape links, FreeCAD .FCStd) |
| `stl-exports/` | Ready-to-print STL files for 3D printer |
| `assembly/` | Assembly instructions, dimension notes, build order |
| `photos/` | Photos of printed parts, assembly progress, final build |

## Your Tasks (from team-plan.md)

| # | Task | Time |
|---|---|---|
| B1 | Factory base plate design (40×50cm) | Hour 0-1.5 |
| B2 | 3D print motor mounts (×2) | Hour 1.5-3.5 |
| B3 | 3D print servo brackets (×2) | Hour 3.5-5 |
| B4 | Conveyor/turntable mechanism | Hour 5-7 |
| B5 | Factory station labels + walls | Hour 7-8 |
| B6 | Mount motors + servos to chassis | Hour 8-9.5 |
| B7 | Mount electronics to base | Hour 9.5-10.5 |
| B8 | Physical factory layout assembly | Hour 10.5-12.5 |
| B9 | Control room station (separate) | Hour 12.5-13.5 |
| B10 | Visual polish + labels | Hour 13.5-14.5 |
| B11 | Presentation display setup | Hour 14.5-15 |

## Key Dimensions

| Part | Size | Notes |
|---|---|---|
| Base plate | 40cm × 50cm | MDF, thick cardboard, or foamboard |
| Fan housing (Zone A) | 10cm × 10cm × 12cm tall | Cardboard box, open top + bottom |
| Turntable disc (Zone B) | 15-20cm diameter, 3-5mm thick | 3D print or cardboard on motor shaft |
| Motor 2 shaft hole | Drill in base plate centre of Zone B | Motor sits UNDER base, shaft pokes UP |
| Servo brackets | Fit MG90S: 23mm × 12mm × 28mm | M3 screw holes |
| Motor mounts | Fit your DC motor dimensions | Measure motor first! |
| Sorting bins | 5cm × 5cm × 4cm deep | Cardboard cups or boxes |
| LED tower | 3cm × 3cm × 15cm tall | Dark cardboard tube or 3D print |
| SCADA station | 15cm × 20cm separate board | Pico B + OLED + joystick + pot |
| Wire routing holes | ~5mm diameter | Drill where wires pass through base |

## Layout Reference

See `docs/factory-layout.md` for:
- Top-down view diagram
- Side view diagram
- Demo table setup
- Zone placement guide

## 3D Print Checklist

| Part | Qty | Estimated Print Time | Priority |
|---|---|---|---|
| Turntable disc (15-20cm) | 1 | 1-2h | High — start first |
| Motor mount (under-base) | 1 | 30min-1h | High |
| Servo bracket | 2 | 30min each | Medium |
| Propeller blade (fan) | 1 | 20min | Medium — or cut from plastic |
| LED tower housing | 1 | 30min | Low — cardboard tube works |
| Sorting arm extension | 1 | 15min | Low — wire works |

**Total print time: ~4-5 hours.** Start prints immediately — they run while you do other work.

## How to Commit Your Work

```bash
git checkout billy/mechanical
git add .
git commit -m "describe what you did"
git push
# Then create a PR on GitHub for Doyun to review
```

## Naming Convention for Files

```
stl-exports/
├── turntable_disc_v1.stl
├── turntable_disc_v2.stl      ← version number if you iterate
├── motor_mount_m1.stl
├── motor_mount_m2.stl
├── servo_bracket_s1.stl
├── servo_bracket_s2.stl
├── propeller_3blade.stl
└── led_tower_housing.stl

cad-files/
├── turntable_disc.f3d         ← source file (editable)
├── motor_mount.f3d
└── full_assembly.f3d          ← if you model the whole thing

photos/
├── 01_base_plate_cut.jpg
├── 02_motor_mounted.jpg
├── 03_turntable_test.jpg      ← number photos in build order
└── ...
```
