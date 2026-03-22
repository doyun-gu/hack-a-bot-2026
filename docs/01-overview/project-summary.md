# GridBox — Project Summary

> Smart Infrastructure Control System | Hack-A-Bot 2026

---

## Problem

Industrial energy monitoring costs £162,000+ per installation, putting it out of reach for 90% of UK factories. These facilities waste up to 68% of their energy because they can't sense, measure, or reroute power in real time. Equipment faults go undetected until catastrophic failure, costing an average of £22,000 per incident.

## Solution

GridBox is a £15 smart infrastructure controller that does what £162K systems do — sense power at every branch, autonomously reroute excess energy, detect equipment faults before damage, and report everything wirelessly to a SCADA dashboard. It runs on two Raspberry Pi Pico 2 microcontrollers coordinated over a 2.4GHz wireless link.

## How It Works

```
SENSE → DECIDE → ACT → REPORT → (loop)
```

**Pico A (Grid Controller)** reads voltage and current at every power branch via ADC, monitors equipment vibration via a 6-axis IMU, then autonomously controls power switches and motor speeds. **Pico B (SCADA Station)** receives wireless telemetry and displays live status on an OLED screen and MAX7219 7-segment display.

## Key Metrics

| Metric | Value |
|---|---|
| System cost | **£15** (vs £162K industrial equivalent) |
| Energy savings | **69%** via Affinity Laws ($P \propto n^3$) |
| Fault response | **<100ms** (autonomous MOSFET disconnect) |
| Fault types detected | **7** (vibration, overcurrent, overvoltage, drift, stall, overtemp, link loss) |
| Wireless range | **1km+** (nRF24L01+ PA+LNA) |
| Control loop | **100Hz** (10ms cycle) |

## Technical Depth

- **Affinity Laws** — 20% speed reduction = 49% power saving
- **Kirchhoff's Current/Voltage Laws** — power bus balance and voltage drop analysis
- **ISO 10816 vibration classification** — industrial-grade fault detection via IMU
- **Energy signature analysis** — 500Hz current sampling detects 4 fault models
- **Dual-core architecture** — Core 0: control loop, Core 1: fault detection
- **PWM motor control** — variable speed via $V_{eff} = D \times V_{supply}$
- **Current sensing** — 1Ω sense resistors with ADC ($I = V/R$)
- **Voltage divider** — safe 12V→3.3V ADC measurement

## Innovation

- **The Pico IS the switching fabric** — ADC pins = sensors, GPIO → MOSFETs = switches, firmware = intelligence. Not a monitor bolted onto existing infrastructure — the microcontroller IS the infrastructure.
- **£15 vs £162,000** — same sensing, switching, and reporting capabilities at 0.01% of the cost. One platform runs water plants, greenhouses, recycling centres, or HVAC.
- **Autonomous fault response** — no human in the loop. IMU detects vibration anomaly → firmware disconnects motor via MOSFET → power reroutes to other loads → OLED reports status. All within 100ms.

## Team

| Member | Role |
|---|---|
| **Doyun Gu** | System Designer / Lead — architecture, firmware, wireless protocol, dashboard, docs |
| **Wooseong Jung** | Electronics Engineer — ~66 wires, power distribution, motor driver, sensors |
| **Billy Park** | Mechatronics Engineer — CAD design (Fusion 360), 3D printing, conveyor, assembly |

## Demo (3 Minutes)

| Step | What Judges See | What They Learn |
|---|---|---|
| 1. Power on | Recycled energy powers a miniature water bottling plant | Problem framing |
| 2. Auto-start | Motors spin, servos move, LEDs light — no buttons pressed | Autonomous startup |
| 3. Wireless SCADA | Pico B display shows live motor speed, servo angle, fault status | Real-time wireless telemetry |
| 4. Shake motor | IMU detects fault → motor stops → power reroutes → display: FAULT | Autonomous fault response |
| 5. Auto-recovery | Vibration drops → system restores loads in priority order | Self-healing |
| 6. Energy summary | OLED shows "Smart mode saved 52% vs dumb mode" | Quantified sustainability |

**Pitch:** *"We didn't build a gadget. We built an infrastructure company in a box. Same £15 system runs a water plant, greenhouse, recycling centre, or HVAC. Today we show you one. The platform runs them all."*
