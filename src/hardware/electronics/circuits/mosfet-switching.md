# MOSFET Switching Circuits — GridBox

> Author: Wooseong Jung (Electronics)
> All 4 MOSFET switching circuits for Motor 1, Motor 2, LED bank, and Recycle path.
> Component values verified against GridBox pin mapping.

---

## Overview

Pico A GPIO pins output 3.3V logic. They cannot directly drive motors or LED banks (too much current). Each load is switched via an N-channel MOSFET. A 1kΩ gate resistor limits inrush current to the gate and prevents ringing.

```
Pico A GPIO (3.3V) ──[ 1kΩ ]──→ MOSFET gate
                                  MOSFET drain ──→ Load (–) terminal
                                  MOSFET source ──→ GND
                     Load (+) terminal ──→ Motor rail / 5V rail
```

**MOSFET used:** IRF540N (or equivalent N-channel, logic-level, ≥2A, ≥20V)
- V_GS(th) ≈ 2–4V → 3.3V from Pico is sufficient to turn on fully
- R_DS(on) ≈ 44mΩ at V_GS = 10V (lower at 3.3V, but still fine for ≤1A loads)
- Add a **flyback diode** (1N4007 or equivalent) across each motor — motors are inductive loads and will spike the drain voltage when switched off

---

## Circuit 1 — Motor 1 Switch (GP10)

**Load:** DC Motor 1 (Water Pump/Fan)
**Current sense:** 1Ω sense resistor on motor ground return → GP27 ADC

```
Motor Power Rail (+6–9V)
        │
        ▼
  Motor 1 (+) terminal
  ┌─────────────────┐
  │    DC MOTOR 1   │   ← Water pump / fan
  │   (pump/fan)    │
  └─────────────────┘
  Motor 1 (−) terminal
        │
       [1Ω / 1W]          ← R_sense: current sense resistor
        │    │
        │   GP27 ADC ──→ Pico A (current measurement)
        │
   MOSFET 1 DRAIN (IRF540N)
   ┌────────────────────────┐
   │      IRF540N           │
   │  G ──[1kΩ]── GP10      │  ← Gate: 3.3V logic from Pico A
   │  D ── to sense R       │  ← Drain: motor current flows here
   │  S ── GND              │  ← Source: common ground
   └────────────────────────┘

  Flyback diode: 1N4007 across Motor 1 terminals (cathode to +, anode to −)

Component values:
  Gate resistor:   1kΩ (limits gate current, prevents ringing)
  Sense resistor:  1.0Ω ±1%, 1W rated
  Flyback diode:   1N4007 (reverse voltage: 1kV, forward current: 1A)

GP10 HIGH (3.3V) → MOSFET ON  → Motor 1 runs
GP10 LOW  (0V)  → MOSFET OFF → Motor 1 stops
```

---

## Circuit 2 — Motor 2 Switch (GP11)

**Load:** DC Motor 2 (Conveyor Belt Drive)
**Current sense:** 1Ω sense resistor on motor ground return → GP28 ADC
**Critical:** This is the primary current sense channel for smart sorting and fault detection.

```
Motor Power Rail (+6–9V)
        │
        ▼
  Motor 2 (+) terminal
  ┌─────────────────┐
  │    DC MOTOR 2   │   ← Conveyor belt drive motor
  │   (conveyor)    │
  └─────────────────┘
  Motor 2 (−) terminal
        │
       [1Ω / 1W]          ← R_sense: MUST be on Motor 2 ground return ONLY
        │    │
        │   GP28 ADC ──→ Pico A Core 1 (500Hz sampling for smart sorting)
        │
   MOSFET 2 DRAIN (IRF540N)
   ┌────────────────────────┐
   │      IRF540N           │
   │  G ──[1kΩ]── GP11      │  ← Gate
   │  D ── to sense R       │  ← Drain
   │  S ── GND              │  ← Source
   └────────────────────────┘

  Flyback diode: 1N4007 across Motor 2 terminals (cathode to +, anode to −)

IMPORTANT — sense resistor placement:
  The 1Ω resistor must be in series with Motor 2's ground return path ONLY.
  If placed on the motor power rail, it would measure current for all devices
  sharing that rail, not just Motor 2.

  CORRECT:   Motor 2 (−) → [1Ω] → MOSFET drain → GND
  WRONG:     Motor rail (+) → [1Ω] → Motor 2 (+)   ← measures all rail current
```

---

## Circuit 3 — LED Bank Switch (GP12)

**Load:** 4× status LEDs (white/green/yellow/red) for load indicator tower
**Each LED:** 5V → 330Ω → LED → MOSFET drain

```
5V Rail
  │
  ├──[330Ω]── LED1 (white  — Critical load) ──┐
  ├──[330Ω]── LED2 (green  — Primary load)  ──┤
  ├──[330Ω]── LED3 (yellow — Secondary)     ──┤
  └──[330Ω]── LED4 (red    — Non-essential) ──┤
                                               │
                                        MOSFET 3 DRAIN
                                        ┌────────────────┐
                                        │   IRF540N      │
                                        │ G ──[1kΩ]──GP12│
                                        │ D ── LED bank  │
                                        │ S ── GND       │
                                        └────────────────┘

LED current per LED:
  I = (5V − V_f) / 330Ω
  I = (5.0 − 2.0) / 330 = 9mA per LED  ← within LED limits (20mA max)

Total LED bank current:
  4 × 9mA = 36mA  ← well within MOSFET capability

GP12 HIGH → all 4 LEDs light (grid powered — showing load priority)
GP12 LOW  → all 4 LEDs off  (grid off / low power mode)
```

---

## Circuit 4 — Recycle Path Switch (GP13)

**Load:** 100µF capacitor (energy storage for recycling demo)
**Purpose:** Pico A controls when excess energy is routed to the capacitor

```
5V Rail
  │
  └──────────────────────── Capacitor (+) terminal
                            [100µF electrolytic]
                            Capacitor (−) terminal
                                    │
                             MOSFET 4 DRAIN
                             ┌────────────────┐
                             │   IRF540N      │
                             │ G ──[1kΩ]──GP13│
                             │ D ── cap (−)   │
                             │ S ── GND       │
                             └────────────────┘

Polarity warning: electrolytic capacitors are polarised.
  (+) terminal → 5V rail side
  (−) terminal → MOSFET drain side
  Reversed polarity will destroy the capacitor.

Charge time estimate:
  τ = R × C
  R = R_DS(on) of MOSFET ≈ 0.1Ω (at 3.3V gate)
  C = 100µF = 0.0001F
  τ = 0.1 × 0.0001 = 10µs  (effectively instant at demo speeds)

GP13 HIGH → MOSFET ON  → capacitor charges from 5V rail
GP13 LOW  → MOSFET OFF → capacitor holds charge (isolated)
```

---

## Breadboard Layout Notes

Wire in this order to avoid mistakes:

```
STEP 1: Place all 4 MOSFETs in a row on the breadboard.
        Leave 2 rows between each to avoid accidental bridging.

STEP 2: Wire all gates first (GP10, GP11, GP12, GP13) with 1kΩ resistors.
        Colour code: yellow wire from Pico A GPIO to gate resistor.

STEP 3: Wire all sources to GND rail.
        Colour code: black wire.

STEP 4: Wire Motor 1 and Motor 2 sense resistors BEFORE connecting drain.
        Test sense resistor is correct value with multimeter (should read 1.0Ω).

STEP 5: Connect drain of MOSFET 1 → sense R → Motor 1 (−).
        Connect drain of MOSFET 2 → sense R → Motor 2 (−).

STEP 6: Connect motor (+) terminals to motor power rail.

STEP 7: Add flyback diodes across each motor.
        Double-check polarity: cathode (stripe) toward + terminal of motor.

STEP 8: Wire LED bank (MOSFET 3) and capacitor (MOSFET 4).

STEP 9: Power on and test each MOSFET independently (see testing/circuit-test-log.md).
```

---

## Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---|---|---|
| Sense resistor on power rail instead of ground return | ADC reads total rail current, not individual motor | Follow Circuit 2 diagram exactly |
| Flyback diode polarity reversed | Shorts motor supply when motor switches off | Stripe (cathode) faces motor (+) terminal |
| Electrolytic capacitor reversed | Capacitor overheats, may explode | Mark (+) terminal with red wire before inserting |
| No gate resistor (direct GPIO to gate) | Gate ringing, possible GPIO damage | Always use 1kΩ in series |
| Motor (+) connected to 3.3V rail | Motor barely runs, Pico 3.3V regulator overloads | Motor (+) must go to the 6-9V motor power rail |
| Both motor sense resistors sharing a common node | GP27 and GP28 read the same combined current | Each sense R must be on its own motor's ground return |
