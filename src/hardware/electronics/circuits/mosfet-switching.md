# MOSFET Switching Circuits — GridBox

> Author: Wooseong Jung (Electronics)
> **Revision 2 (2026-03-22):** LED bank circuit REMOVED (replaced by MAX7219 display on Pico B). Motor MOSFET gates now driven by PCA9685 PWM channels instead of direct Pico GPIO.

---

## Overview

DC motors draw too much current for Pico GPIO or PCA9685 outputs to drive directly. Each motor is switched via an N-channel MOSFET. The PCA9685 PWM driver provides the gate signal (12-bit, 4096-step speed control).

```
PCA9685 PWM output ──[ 1kΩ ]──→ MOSFET gate
                                 MOSFET drain ──→ Motor (–) terminal (via sense R)
                                 MOSFET source ──→ GND
                      Motor (+) terminal ──→ Motor power rail (6-9V)
```

**Why PCA9685 → MOSFET (not direct GPIO)?**
- PCA9685 gives 12-bit PWM (4096 steps) = smooth speed control
- Supports Affinity Laws savings (P ∝ n³ — 20% slower = 49% less power)
- Frees Pico GPIO pins for other use
- PCA9685 is already wired on I2C for servos

**MOSFET used:** IRF540N (or equivalent N-channel, logic-level, ≥2A, ≥20V)
- V_GS(th) ≈ 2-4V → PCA9685 output at 5V is sufficient
- R_DS(on) ≈ 44mΩ → negligible voltage drop
- Add a **flyback diode** (1N4007) across each motor — inductive kickback will damage the MOSFET without it

---

## Circuit 1 — Motor 1 (PCA9685 CH2 → MOSFET)

**Load:** DC Motor 1 (Water Pump/Fan)
**Gate signal:** PCA9685 Channel 2 (PWM speed control)
**Current sense:** 1Ω sense resistor on motor ground return → Pico A GP27 ADC

```
Motor Power Rail (+6-9V)
        |
        v
  Motor 1 (+) terminal
  +-------------------+
  |    DC MOTOR 1     |   <-- Water pump / fan
  |   (pump/fan)      |
  +-------------------+
  Motor 1 (-) terminal
        |
       [1R / 1W]          <-- R_sense: current sense resistor
        |    |
        |   GP27 ADC ---> Pico A (current measurement)
        |
   MOSFET 1 DRAIN (IRF540N)
   +------------------------+
   |      IRF540N           |
   |  G --[1k]-- PCA9685 CH2|  <-- Gate: PWM from PCA9685
   |  D -- to sense R       |  <-- Drain: motor current flows here
   |  S -- GND              |  <-- Source: common ground
   +------------------------+

  Flyback diode: 1N4007 across Motor 1 terminals (cathode to +, anode to -)

Component values:
  Gate resistor:   1k (limits gate current, prevents ringing)
  Sense resistor:  1.0R +/-1%, 1W rated
  Flyback diode:   1N4007 (reverse voltage: 1kV, forward current: 1A)

PCA9685 CH2 PWM high --> MOSFET ON  --> Motor 1 runs (speed = duty cycle)
PCA9685 CH2 PWM low  --> MOSFET OFF --> Motor 1 stops
```

---

## Circuit 2 — Motor 2 (PCA9685 CH3 → MOSFET)

**Load:** DC Motor 2 (Conveyor Belt Drive)
**Gate signal:** PCA9685 Channel 3 (PWM speed control)
**Current sense:** 1Ω sense resistor on motor ground return → Pico A GP28 ADC
**Critical:** This is the primary current sense channel for smart sorting and fault detection.

```
Motor Power Rail (+6-9V)
        |
        v
  Motor 2 (+) terminal
  +-------------------+
  |    DC MOTOR 2     |   <-- Conveyor belt drive motor
  |   (conveyor)      |
  +-------------------+
  Motor 2 (-) terminal
        |
       [1R / 1W]          <-- R_sense: MUST be on Motor 2 ground return ONLY
        |    |
        |   GP28 ADC ---> Pico A Core 1 (500Hz sampling for smart sorting)
        |
   MOSFET 2 DRAIN (IRF540N)
   +------------------------+
   |      IRF540N           |
   |  G --[1k]-- PCA9685 CH3|  <-- Gate: PWM from PCA9685
   |  D -- to sense R       |  <-- Drain
   |  S -- GND              |  <-- Source
   +------------------------+

  Flyback diode: 1N4007 across Motor 2 terminals (cathode to +, anode to -)

IMPORTANT -- sense resistor placement:
  The 1R resistor must be in series with Motor 2's ground return path ONLY.
  If placed on the motor power rail, it would measure current for all devices
  sharing that rail, not just Motor 2.

  CORRECT:   Motor 2 (-) --> [1R] --> MOSFET drain --> GND
  WRONG:     Motor rail (+) --> [1R] --> Motor 2 (+)   <-- measures all rail current
```

---

## ~~Circuit 3 — LED Bank (GP12)~~ — REMOVED

> **CANCELLED (2026-03-22):** The LED bank circuit has been replaced by a MAX7219 8-digit 7-segment display on Pico B (SPI1 bus). The display shows all status information wirelessly — load priority, fault codes, power readings — more clearly than 4 LEDs ever could.
>
> - Old wires A29-A34 are no longer needed
> - GP12 is now free on Pico A
> - MOSFET 3 (was LED bank) is now used for Recycle path instead
> - See `docs/02-electrical/max7219-wiring.md` for display wiring

---

## Circuit 3 — Recycle Path (GP13 → MOSFET)

**Load:** 100µF capacitor (energy storage for recycling demo)
**Gate signal:** Pico A GP13 (binary on/off — no PWM needed)

```
5V Rail
  |
  +---------------------------- Capacitor (+) terminal
                                [100uF electrolytic]
                                Capacitor (-) terminal
                                        |
                                 MOSFET 3 DRAIN
                                 +----------------+
                                 |   IRF540N      |
                                 | G --[1k]--GP13 |
                                 | D -- cap (-)   |
                                 | S -- GND       |
                                 +----------------+

Polarity warning: electrolytic capacitors are polarised.
  (+) terminal --> 5V rail side
  (-) terminal --> MOSFET drain side
  Reversed polarity will destroy the capacitor.

GP13 HIGH --> MOSFET ON  --> capacitor charges from 5V rail
GP13 LOW  --> MOSFET OFF --> capacitor holds charge (isolated)
```

---

## Component Summary

| Component | Qty | Value | Purpose |
|---|---|---|---|
| IRF540N MOSFET | **3** | N-ch, ≥2A, ≥20V | Motor 1, Motor 2, Recycle path |
| Gate resistor | 3 | 1kΩ | Limits gate current |
| Sense resistor | 2 | 1.0Ω ±1%, 1W | Motor current sensing |
| Flyback diode | 2 | 1N4007 | Motor back-EMF protection |
| Electrolytic cap | 1 | 100µF, ≥10V | Energy storage demo |

**Compared to Rev 1:** 1 fewer MOSFET, 4 fewer LEDs, 4 fewer 330Ω resistors, 6 fewer wires.

---

## PCA9685 Channel Assignment

| Channel | Connected To | Signal Type |
|---|---|---|
| CH0 | Servo 1 (fill valve) | Servo PWM |
| CH1 | Servo 2 (sort gate) | Servo PWM |
| CH2 | MOSFET 1 gate (Motor 1) | Motor PWM speed |
| CH3 | MOSFET 2 gate (Motor 2) | Motor PWM speed |
| CH4-CH15 | (available) | — |

---

## Breadboard Layout Notes

Wire in this order to avoid mistakes:

```
STEP 1: Place all 3 MOSFETs in a row on the breadboard.
        Leave 2 rows between each to avoid accidental bridging.

STEP 2: Wire PCA9685 CH2 and CH3 to MOSFET 1 and 2 gates (with 1k resistors).
        Wire GP13 to MOSFET 3 gate (with 1k resistor).
        Colour code: yellow wire to gate resistor.

STEP 3: Wire all sources to GND rail.
        Colour code: black wire.

STEP 4: Wire Motor 1 and Motor 2 sense resistors BEFORE connecting drain.
        Test sense resistor is correct value with multimeter (should read 1.0R).

STEP 5: Connect drain of MOSFET 1 --> sense R --> Motor 1 (-).
        Connect drain of MOSFET 2 --> sense R --> Motor 2 (-).

STEP 6: Connect motor (+) terminals to motor power rail.

STEP 7: Add flyback diodes across each motor.
        Double-check polarity: cathode (stripe) toward + terminal of motor.

STEP 8: Wire capacitor to MOSFET 3.
        Check polarity: (+) stripe toward 5V rail.

STEP 9: Power on and test each MOSFET independently.
```

---

## Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---|---|---|
| Sense resistor on power rail instead of ground return | ADC reads total rail current, not individual motor | Follow Circuit 2 diagram exactly |
| Flyback diode polarity reversed | Shorts motor supply when motor switches off | Stripe (cathode) faces motor (+) terminal |
| Electrolytic capacitor reversed | Capacitor overheats, may explode | Mark (+) terminal with red wire before inserting |
| No gate resistor (direct signal to gate) | Gate ringing, possible damage | Always use 1kΩ in series |
| Motor (+) connected to 3.3V rail | Motor barely runs, Pico regulator overloads | Motor (+) must go to the 6-9V motor power rail |
| Both motor sense resistors sharing a common node | GP27 and GP28 read the same combined current | Each sense R must be on its own motor's ground return |
| PCA9685 V+ not connected | Servos and motor gate signals don't work | Wire 5V rail to PCA9685 V+ pin |
