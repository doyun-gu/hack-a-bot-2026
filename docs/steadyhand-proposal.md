# SteadyHand — Tremor-Stabilising Assistive Device

> "Noise-cancelling headphones for physical movement"

**Theme:** Assistive Technology + Autonomy (semi-autonomous)
**Score: 95/100** — Highest ranked idea

---

## The Problem

| Stat | Source |
|---|---|
| **10 million+** people worldwide live with Parkinson's disease | WHO |
| **7 million** in the US alone have essential tremor | NIH |
| **25%** of adults over 65 have age-related tremor | Clinical studies |
| **25-50%** of stroke survivors develop upper limb tremor | Rehab literature |
| **£200+** cost of Liftware Steady (Google's stabilising spoon) | Retail |
| **£15** estimated cost of SteadyHand from our kit | Our build |

People with tremor can't eat independently, can't carry a cup of water, can't hold a phone steady. It strips dignity from daily life. Existing solutions are expensive or don't exist.

---

## The Solution

A handheld device with a small stabilised platform (~5x6cm). The IMU detects unwanted hand movement, servos produce the **exact opposite tilt** to cancel it. Objects on the platform stay level.

### Two Modes — Same Hardware

| Mode | What It Does | Who It's For |
|---|---|---|
| **Mode 1: Stabiliser** | Servos actively cancel tremor — spoon/cup stays level | Patients in daily life (eating, drinking) |
| **Mode 2: Rehab Trainer** | Servos OFF — IMU measures hand steadiness, ball on platform tests control | Therapists tracking rehab progress |

Switching modes = one joystick press. Zero extra hardware.

---

## How It Works — The Noise-Cancelling Analogy

```
Noise cancelling:    Mic detects sound wave  →  speaker produces inverse  →  silence
SteadyHand:          IMU detects hand tilt   →  servos produce inverse   →  platform stays level
```

### Control Loop (runs every 10ms)

```
PICO A (Wearable Sensor — on wrist/hand):
  1. Read BMI160 at 100Hz (accel + gyro, 6 values)
  2. Complementary filter → smooth roll + pitch angles
  3. Pack { roll, pitch, tremor_amplitude, mode, timestamp }
  4. Transmit via nRF24L01+ (SPI, ~2ms)

     ~~~~ 2.4 GHz wireless ~~~~

PICO B (Stabilised Platform — holds spoon/cup):
  MODE 1 (Stabiliser):
    1. Receive orientation packet
    2. PID controller: error = 0° - received_angle
       correction = Kp×error + Kd×(error_change/dt)
    3. Drive servos via PCA9685: servo_angle = 90° + correction
    4. Update OLED display every 100ms

  MODE 2 (Rehab Trainer):
    1. Receive orientation packet
    2. Servos stay at 90° (neutral — no compensation)
    3. Calculate steadiness score from tilt variance
    4. Update OLED with real-time score
```

**Total latency: ~4ms** (IMU 1ms + filter 0.1ms + wireless 2ms + PID 0.1ms + servo 0.5ms)

---

## Architecture

| Pico A — Wearable Sensor (wrist) | Pico B — Stabilised Platform (handheld) |
|---|---|
| BMI160 IMU — roll, pitch, gyro at 100Hz (I2C) | PCA9685 + 2x MG90S servos — roll + pitch compensation (I2C) |
| nRF24L01+ TX — streams orientation data (SPI) | nRF24L01+ RX — receives tilt data (SPI) |
| Joystick — sensitivity adjust, mode switch | OLED — health dashboard (see display modes below) (I2C) |
| LED — status (green=OK, red=fall detected) | LEDs — stability indicator (green/yellow/red) |

### Fall Detection (Bonus — runs on Pico A, Core 1)

The same IMU already on the wrist detects falls in parallel:

1. **Freefall** — accel ≈ 0g for 0.3-0.5s
2. **Impact** — spike >3g
3. **Immobility** — no movement for 10s after impact
4. All three in sequence → confirmed fall → wireless SOS to Pico B
5. Joystick press within 15s → cancel ("I'm OK")
6. No cancel → Pico B raises alarm (OLED + LEDs)

**Two features from one sensor.** Judges see efficient engineering.

---

## Who Uses This?

### Primary Users (Daily Assistance)

| User Group | Population | Problem | How SteadyHand Helps |
|---|---|---|---|
| **Parkinson's patients** | 10M worldwide | Resting tremor makes eating, drinking humiliating | Spoon/cup stays level — eat independently |
| **Essential tremor patients** | 7M in US | Hands shake during intentional movement | Stabilises objects during purposeful tasks |
| **Elderly (age-related tremor)** | 15-25% of over-65s | Untreated because "it's just aging" | Simple daily aid — no medication needed |
| **Post-stroke patients** | 25-50% develop tremor | Rehab takes months, can't eat independently meanwhile | Immediate functional aid during recovery |
| **Cerebral palsy** | 17M globally | Involuntary movements affect daily tasks | Stabilised eating surface |
| **Multiple sclerosis** | 2.8M worldwide | Intention tremor worsens when reaching | Compensates for reach-triggered tremor |

### Secondary Users (Professional / Clinical)

| User Group | Problem | How SteadyHand Helps |
|---|---|---|
| **Surgeons / dentists** | Micro-tremor affects precision procedures | Stabilised instrument platform concept |
| **Lab technicians** | Tremor causes pipetting errors | Stabilised work surface for liquid handling |
| **Occupational therapists** | Need objective tremor measurements | Rehab mode: quantified steadiness score over time |
| **Photographers** | Camera shake ruins shots | DIY gimbal proof of concept |

---

## Physical Build — Scaled for MG90S Servos

### What MG90S Can Handle

| Object | Weight | Feasible? |
|---|---|---|
| Spoon (empty) | ~40g | Yes — fast response |
| Spoon with food | ~60-80g | Yes |
| Small cup (espresso) | ~120g | Yes |
| Phone | ~180g | Borderline |
| Full mug | ~350g | No — servo stalls |

**Target: ~70g total platform weight (perfboard + spoon)**

### Assembly

```
SIDE VIEW:                          TOP VIEW:

  ┌────── spoon clips here          ┌───────────────┐
  │                                 │   spoon clip  │
  ┌┴────────────┐                   │               │
  │  PLATFORM   │ ← 5x6cm          │  SERVO A ─────┤ push rod
  └──┬──────┬───┘   perfboard      │      ●        │ (pivot)
     │  ●   │    ← M3 pivot        │  SERVO B ─────┤ push rod
     │      │                       │               │
  ┌──┴──────┴───┐                   └───────────────┘
  │  SERVO A  B │
  │   HANDLE    │ ← user grips
  └─────────────┘

  Servo A arm → pushes left/right edge → controls ROLL
  Servo B arm → pushes front/back edge → controls PITCH
  M3 bolt + loose nut at centre = cheap ball joint
  Push rods: 22AWG solid wire bent into Z-shape
```

### Materials from Kit

| Part | Component | Purpose |
|---|---|---|
| Platform | Perfboard 7x9cm (cut to 5x6cm) | Holds spoon/cup |
| Actuators | 2x MG90S servo | Roll + pitch compensation |
| Pivot | M3 bolt + nut (loose) | Centre ball joint |
| Push rods | 22AWG solid wire | Connect servo arms to platform |
| Mounting | M3 self-tapping screws | Attach servos to handle |
| Handle | Cardboard tube / marker body / perfboard | User grip |

**Assembly time: ~2 hours**
**Total device size: ~15cm long, ~6cm wide, ~8cm tall**

---

## OLED Display Modes

Joystick press cycles through 4 modes:

### Mode 1 — Live Spirit Level (default)
```
┌──────────────────────┐
│  STEADYHAND  [LIVE]  │
│      ┌─────────┐     │
│      │    o    │     │  ← dot = current tilt
│      │  ──┼──  │     │     crosshair = level
│      │    │    │     │     dot on cross = perfect
│      └─────────┘     │
│  Roll: -2.3°  OK     │
│  Pitch: +1.1° OK     │
└──────────────────────┘
```

### Mode 2 — Tremor Waveform
```
┌──────────────────────┐
│  TREMOR WAVEFORM     │
│  ∿∿∿╲╱∿∿∿∿∿∿∿∿∿∿   │  ← raw tremor (before)
│  ─────────────────   │  ← compensated (after)
│  Amplitude: 4.2°     │
│  Frequency: 4.8Hz    │
│  Reduction: 78%      │
└──────────────────────┘
```

### Mode 3 — Session Statistics
```
┌──────────────────────┐
│  SESSION STATS       │
│  Duration:  00:04:32 │
│  Avg tremor: 3.8°    │
│  Peak:      12.1°    │
│  Stability:  82%     │
│  Corrections: 1,847  │
│  Wireless:   98.2%   │
└──────────────────────┘
```

### Mode 4 — Calibration
```
┌──────────────────────┐
│  CALIBRATION         │
│  Place on flat       │
│  surface and press   │
│  joystick to zero.   │
│  > [CALIBRATE]       │
│  Sensitivity: ███░░  │
└──────────────────────┘
```

### Rehab Mode (when Mode 2 is active with servos off)
```
┌──────────────────────┐
│  REHAB TRAINER       │
│      ┌─────────┐     │
│      │  o      │     │  ← ball position (keep centred!)
│      │  ──┼──  │     │
│      │    │    │     │
│      └─────────┘     │
│  Score: 67%          │
│  Best today: 74%     │
└──────────────────────┘
```

---

## Demo Script (for judges)

| Step | Action | What Judges See |
|---|---|---|
| 1 | Place spoon on platform, put cereal/liquid on spoon | Setup — looks like a small handheld device |
| 2 | **Servos OFF** — shake hand | Cereal falls off / water spills |
| 3 | **Servos ON** — same shaking | Cereal stays on / water doesn't spill |
| 4 | Show OLED | "Tremor: 7.2° → Reduction: 82% → Stability: GOOD" |
| 5 | Switch to rehab mode — place ball on platform | Ball rolls when hand shakes — measures steadiness |
| 6 | Show OLED rehab score | "Score: 67% — quantified rehab progress" |
| 7 | Hand device to judge | They shake it, see the compensation live |
| 8 | Drop line | "A Liftware Steady costs £200. We built this for £15." |

---

## Scoring Breakdown

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **29** | 10M+ Parkinson's patients. Affects eating — most basic human need. Clear end users across 10+ groups |
| **Live Demo (25)** | **24** | Cereal-on-spoon test is visual and immediate. Before/after with servos off/on. Judge tries it. OLED quantifies the improvement |
| **Technical (20)** | **19** | Complementary filter, PID control, 100Hz IMU, 4ms latency, wireless streaming, dual-core (stabilisation + fall detection), 4 display modes |
| **Innovation (15)** | **14** | "Noise-cancelling for movement." Dual-mode (stabiliser + rehab trainer) from same hardware. DIY Liftware for £15 |
| **Docs (10)** | **9** | Control loop diagrams, mechanical drawings, OLED mockups, signal flow — visually rich documentation |
| **Total** | **95** | |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| MG90S too slow for fast tremors (>6Hz) | Incomplete compensation | Focus demo on slow/medium tremor (most common). Show % improvement, not perfection |
| Mechanical assembly takes too long | Less time for firmware | Pre-plan dimensions. Simple Z-wire push rods. Budget 2h max |
| Wireless latency spikes | Servo judder | Moving average on received data. Fallback to last known good angle |
| PID tuning is fiddly | Oscillating platform | Start with P+D only. Tune Kp first, add Kd for damping. Skip Ki |
| Judge asks "Apple Watch does this" | Perceived as unoriginal | "Apple Watch detects falls. SteadyHand actively cancels tremor. One monitors, ours solves." |

---

## Build Timeline (12 hours)

| Hour | Milestone |
|---|---|
| 0-1 | nRF24L01+ wireless link confirmed between two Picos |
| 1-2 | BMI160 IMU reading + complementary filter on Pico A |
| 2-3 | PCA9685 + servo control on Pico B. PID controller working |
| 3-4 | End-to-end: tilt hand → servo compensates. Basic stabilisation working |
| 4-5 | Mechanical assembly: platform, pivot, push rods, spoon mount |
| 5-6 | OLED display: spirit level + waveform modes |
| 6-8 | Fall detection on Core 1. Rehab trainer mode. Polish |
| 8-10 | Documentation: wiring diagram, README, architecture diagram |
| 10-11 | Practice demo. Tune PID. Reliability testing |
| 11-12 | Final demo prep. Backup plan if anything fails |

---

## vs Competitors

| Feature | Liftware Steady (Google) | Apple Watch | SteadyHand (Ours) |
|---|---|---|---|
| **Price** | £200 | £400+ | ~£15 |
| **Tremor cancellation** | Yes (active) | No | Yes (active) |
| **Fall detection** | No | Yes | Yes |
| **Rehab tracking** | No | No | Yes (Mode 2) |
| **Clinical metrics on display** | No | Heart rate only | Tremor amplitude, frequency, reduction %, stability score |
| **Phone required** | No | Yes (iPhone) | No |
| **Open source** | No | No | Yes |
| **Works in developing countries** | No (expensive) | No (expensive) | Yes — standalone, cheap |
