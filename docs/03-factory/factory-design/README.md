# Factory Design

> **Note (2026-03-22):** Some files in this directory reference joystick and potentiometer inputs that were later cancelled to focus on wireless communication and autonomous operation. See the [wiring connections](../../02-electrical/wiring-connections.md) change log for the full scope reduction. The [demo script](../demo-script.md) reflects the final design.

## Chassis CAD Render

<img src="../../images/chassis_cad.png" alt="GridBox Chassis CAD Render" width="600"/>

> Sorting conveyor chassis designed by Billy Park in Fusion 360. Full CAD files in [`src/hardware/cad/`](../../../src/hardware/cad/).

---

| File | Author | Contents |
|---|---|---|
| [`weight-sensing-sorting.md`](weight-sensing-sorting.md) | Doyun | Weight detection via motor current — 4-LED station system, sorting logic, calibration |
| [`factory-layout.md`](factory-layout.md) | Doyun | Physical layout — zones, dimensions, side view, demo table setup, rendered diagrams |
| [`factory-build-plan.md`](factory-build-plan.md) | Doyun | Battery sorting factory — turntable + weight + size-gap mechanism, demo script, build materials |
| [`factory-deep-dive.md`](factory-deep-dive.md) | Doyun | 4 factory types compared with scoring — Battery Recovery chosen (96pts) |
| [`factory-full-layout.md`](factory-full-layout.md) | Doyun | Full component plan — PCA9685 channel map, conveyor + sorting + HVAC systems |
