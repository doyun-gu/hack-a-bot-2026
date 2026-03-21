# Smart Sorting System — Energy Signature + Time-of-Flight

> Extension of Model A: Mechanical Load Increase
> Uses conveyor motor current to detect anomalous objects, then times the sorting servo
> to trigger precisely when the object arrives at the gate.
> GridBox — Hack-A-Bot 2026

---

## Core Concept

The conveyor belt runs at a **fixed speed** carrying objects of **known, regular weight** at **regular intervals**. The motor learns this as its normal loaded baseline. When an object with different weight passes over the drive roller, the motor current deviates from baseline. The firmware timestamps that deviation, calculates how long the object takes to travel from the detection point to Servo 2 (sorting gate), and fires the servo at exactly that moment.

```
Regular objects  →  known current baseline
Anomalous object →  current deviation detected  →  start timer
                                                        │
                                             t = distance / belt_speed
                                                        │
                                                        ▼
                                               Servo 2 switches  →  object diverted
```

---

## System Layout Diagram

```
 TOP-DOWN VIEW — CONVEYOR BELT SORTING SYSTEM
 ═══════════════════════════════════════════════════════════════════════════════

  OBJECT                                                            SORTING
  ENTRY                                                             GATE
  POINT                                                          (Servo 2)
    │                                                                │
    ▼                                                                ▼
    ○ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ○
    ┊  [obj] ──────────────────────────────────────────── ► [obj]   ┊
    ○ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ○
    │                                                                │
 DRIVE                                                           IDLER
 ROLLER                                                          ROLLER
 (Motor 2)
    │
    │──→ 1Ω sense resistor ──→ GP28 (ADC2)
    │                               │
    │                          Pico A Core 1
    │                          (500Hz sampling)
    │                               │
    │                     detects current deviation
    │                               │
    │                          t_detect = now()
    │                               │
    │                  t_sort = t_detect + (d_belt / v_belt)
    │                               │
    └───────────────────────────────┼──────────────────────────────────────┐
                                    │                                      │
                               timer fires                           Servo 2 gate
                               at t_sort                             (PCA9685 ch2)
                                    │                                      │
                                    └──────────────────────────────────────┘
                                          SWITCH to divert angle


 SIDE VIEW — OBJECT TRAVEL PATH
 ═══════════════════════════════════════════════════════════════════════════════

                   d_belt (measured — e.g. 30 cm)
          ◄────────────────────────────────────────────►

  [Drive Roller]                                      [Idler + Servo Gate]
       ○ ══════════════════════════════════════════════ ○
                                                             │
           ──── regular ──── regular ──── HEAVY ────►        │  Servo 2
                                                             │  (PCA9685 ch2)
                                                        pass ┤├ divert
  GP28 ADC                                                   │
  detects load here                                     two lanes:
  (at drive roller)                                     PASS (0°) │ DIVERT (90°)


 CURRENT SIGNATURE TIMELINE
 ═══════════════════════════════════════════════════════════════════════════════

  Current
  (mA)
    │
560 ┤                                    ╔═══╗
    │                                    ║   ║    ← heavy object on belt
520 ┤              ╔═══╗       ╔═══╗     ║   ║
    │              ║   ║       ║   ║     ║   ║    ← regular objects (learned baseline)
480 ┤   ╔═══╗      ║   ║       ║   ║     ║   ║
    │   ║   ║      ║   ║       ║   ║     ║   ║
440 ┤───╝   ╚──────╝   ╚───────╝   ╚─────╝   ╚──── baseline (empty belt: ~420mA)
    │
420 ┤   ←──→        ←──→       ←──→     ←──→
    │  regular    regular    regular   ANOMALY
    │  object     object     object    DETECTED
    │
    └───────────────────────────────────────────────────────────────► time
                                              │
                                              t_detect
                                              │
                                              └──→ start countdown: d_belt / v_belt
                                                                           │
                                                                           ▼
                                                                      t_sort: FIRE SERVO


 STATE MACHINE
 ═══════════════════════════════════════════════════════════════════════════════

         ┌─────────────────────────────────────────────────────┐
         │                                                     │
         ▼                                                     │ object clears
   ┌───────────┐   anomaly     ┌───────────┐   timer fires    │ reset after
   │           │   detected    │           │   at t_sort      │ travel time
   │  BASELINE │ ────────────► │  TRACKING │ ──────────────►  │
   │  (learn)  │               │  (count)  │                  │
   └───────────┘               └───────────┘                  │
         ▲                                                     │
         │                                                     │
         │           ┌───────────┐                            │
         └────────── │   SORT    │ ◄──────────────────────────┘
           reset to  │ (servo 2) │
           baseline  └───────────┘
                      Servo 2 fires
                      at divert angle
                      for t_hold duration
                      then returns to pass
```

---

## The Maths

### Variables

| Symbol | Meaning | How to get it |
|---|---|---|
| `d_belt` | Distance from drive roller to sorting gate | Measure physically (e.g. ruler on Billy's chassis) |
| `v_belt` | Belt surface speed (cm/s) | Calibrate: mark belt, time one full revolution |
| `t_sort` | Time after detection to fire servo | `d_belt / v_belt` |
| `t_hold` | Duration to hold servo at divert angle | `l_object / v_belt` (object length / belt speed) |
| `I_base` | Baseline current with regular objects | Learned from rolling average |
| `I_curr` | Current 1-second window mean | Sampled at 500Hz on Core 1 |
| `threshold` | Minimum divergence to count as anomaly | Tuned during testing (~15% change) |

### Time-of-Flight Calculation

```
t_sort (ms) = (d_belt (cm) / v_belt (cm/s)) × 1000
```

Example with a 30cm belt at 5cm/s:
```
t_sort = (30 / 5) × 1000 = 6000ms = 6 seconds
```

### Belt Speed Calibration

```
v_belt = belt_circumference / t_one_revolution

e.g.  belt length = 70cm (total loop)
      time for mark to complete one loop = 14s
      v_belt = 70 / 14 = 5 cm/s
```

Alternatively, derive from PWM:
```
v_belt = (PWM_duty × V_motor × k_motor) / (roller_circumference)
```
where `k_motor` is the no-load speed constant (RPM/V from motor datasheet).
PWM calibration is less accurate — **physical measurement preferred.**

### Anomaly Threshold

```
divergence = |I_curr - I_base| / I_base

if divergence > THRESHOLD:   # e.g. 0.15 = 15% change
    anomaly detected
    start timer: t_sort ms
```

A heavier object raises current. A lighter object (or missing object = gap) drops it. Both are detectable.

---

## Algorithm — Pico A Core 1

```python
# Constants — measure physically before demo
D_BELT_CM    = 30.0    # drive roller to sorting gate (measure!)
V_BELT_CMS   = 5.0     # belt surface speed in cm/s (calibrate!)
T_SORT_MS    = int((D_BELT_CM / V_BELT_CMS) * 1000)  # e.g. 6000ms
T_HOLD_MS    = 800     # how long servo holds divert position (tune)
THRESHOLD    = 0.15    # 15% current change = anomaly

# Baseline: rolling average over last N windows of regular objects
BASELINE_WINDOWS = 10
baseline_buffer  = []

# State
state          = "BASELINE"
sort_timer_ms  = 0

def core1_loop():
    global state, sort_timer_ms

    while True:
        # --- Sample 500 ADC readings at 500Hz ---
        samples = sample_adc_window()           # 1s of data from GP28
        I_curr  = mean(samples)
        t_now   = ticks_ms()

        if state == "BASELINE":
            # Learn baseline from regular objects
            baseline_buffer.append(I_curr)
            if len(baseline_buffer) > BASELINE_WINDOWS:
                baseline_buffer.pop(0)
            I_base = mean(baseline_buffer)

            divergence = abs(I_curr - I_base) / max(I_base, 0.001)

            if divergence > THRESHOLD:
                # Anomalous object detected at drive roller
                state         = "TRACKING"
                sort_timer_ms = t_now + T_SORT_MS
                signal_fault(divergence)   # update OLED + nRF packet

        elif state == "TRACKING":
            # Waiting for object to travel to sorting gate
            if ticks_diff(sort_timer_ms, t_now) <= 0:
                state = "SORT"

        elif state == "SORT":
            # Fire Servo 2 to divert position
            set_servo(channel=2, angle=90)     # divert lane
            sleep_ms(T_HOLD_MS)
            set_servo(channel=2, angle=0)      # return to pass lane
            state = "BASELINE"                 # reset, re-learn
```

---

## Integration with Existing Model A Infrastructure

This system reuses everything already built for Model A. No new hardware needed.

| Component | Model A use | Smart Sorting use |
|---|---|---|
| GP28 ADC | Detect motor overload | Detect per-object weight change |
| Core 1 (500Hz) | Continuous energy signature | Same — now also drives sort timer |
| PCA9685 ch2 | Servo 2 = quality gate | Servo 2 = sort actuator (timed) |
| nRF packet | Send fault score | Add `sort_event` flag + `t_sort_remaining` |
| OLED (Pico B) | Show divergence score | Show "SORT IN 3s... SORTING... DONE" |

The only firmware change is adding the state machine and timer logic to what already exists.

---

## Physical Setup (Wooseong — Electronics)

### What Needs to Be Verified

- [ ] **GP28 sense resistor is on Motor 2 (conveyor) ground return** — not Motor 1
- [ ] **Servo 2 on PCA9685 channel 2** — confirm in Billy's layout that this is the sorting gate servo
- [ ] **Belt speed is stable at the PWM duty cycle used** — test before demo, mark the belt, time it
- [ ] **Measure d_belt** — exact distance from the centre of the drive roller to the pivot point of Servo 2

### Sense Resistor Placement (Critical)

The sense resistor must be **after the motor** in the current path (on the ground return side), not on the power supply side. This ensures you measure current through Motor 2 specifically, not the whole motor rail.

```
Motor power rail (+)
        │
        ▼
   Motor 2 (+) terminal
   ┌────────┐
   │ DC MTR │
   └────────┘
   Motor 2 (−) terminal
        │
       [1Ω sense R]   ← R must be HERE (ground return of Motor 2 only)
        │
       GP28 ADC tap  ← measure voltage across this point and GND
        │
       GND
```

If the sense resistor is on the wrong side, the ADC sees noise from both motors.

### Object Spacing Requirement

For the baseline to be reliable, objects must be spaced far enough apart that only **one object at a time** is on the belt at the motor drive roller. If two objects overlap in the sensing window, the current signature blurs.

Minimum safe spacing:
```
gap_between_objects > l_object  (object length)
```

For the demo, manually place objects at least one object-length apart.

---

## Demo Choreography

| Time | Action | System Response | What to Say |
|---|---|---|---|
| T-30s | Place 3 regular objects on belt, one at a time | OLED: "LEARNING BASELINE..." | "The system is learning what a normal bottle looks like in the current." |
| T+0:00 | Start placing regular objects rhythmically | Needle at ~10°, servo stays at 0° (pass) | "Regular bottles — all passing through. Score near zero." |
| T+0:20 | Place a heavier object (e.g. water-filled bottle) | Current spike on GP28, OLED: "ANOMALY — SORT IN 6s" | "Heavier object detected. Timer started." |
| T+0:26 | Object reaches Servo 2 | Servo 2 swings to 90° for ~0.8s then returns | "Sorted. The servo fired exactly when the object arrived." |
| T+0:30 | Resume regular objects | Servo stays at 0°, needle returns to 0° | "Back to normal. No false triggers." |
| T+0:45 | Place lighter object (foam block) | Current drop detected, OLED: "ANOMALY — SORT IN 6s" | "Lighter object — could be an underfilled bottle. Also caught." |
| T+0:51 | Object reaches Servo 2 | Same divert response | "Both over-weight and under-weight — one sensor, both directions." |

**Key judge talking point:**
"There is no weight sensor, no camera, no extra hardware. The conveyor motor's own current draw is the detector. And the sorting is timed — not triggered by a physical trip sensor at the gate, but calculated from physics: distance divided by speed."

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| `d_belt` / `v_belt` miscalibrated → servo fires too early or late | Medium | Calibrate belt speed physically before demo. Tune `T_SORT_MS` with a test run. Mark the belt, time 3 runs, average. |
| Multiple objects overlap in current window → baseline corrupted | Medium | Space objects at least 1 object-length apart. Keep object spacing consistent. |
| Belt speed drifts under load → timing error accumulates | Low | Motor 2 runs at fixed PWM duty cycle. Speed is stable if voltage is stable. Use buck-boost (already regulated). |
| Servo 2 fires but object has already passed | Low | If early: increase `T_SORT_MS`. If late: decrease. Trim in firmware. |
| Baseline never settles (too much variance) | Low | Pre-load `FALLBACK_BASELINE` at boot. Use wider averaging window (20 instead of 10). |
| Light object (foam) current drop too small to detect | Medium | Lower threshold to 0.10 (10%). Risk: more false triggers. Tune on hardware. |

---

## What This Adds to the GridBox Story

The original GridBox pitch is about **fault detection** — catching problems before they become failures. Smart Sorting extends this to **active quality control** — the same hardware that protects the motor also sorts the product.

For judges:

> "We didn't add any sensors. The energy signature already existed to protect the motor. We realised the same signal tells us about the object too — its weight changes the current. So we added a timer. Now the system doesn't just detect problems: it acts on them, autonomously, with sub-second timing accuracy. Same £15. Same ADC pins. Same motor. Zero extra hardware."

This demonstrates **sensor fusion depth** — one physical signal (current) serving two functions simultaneously (fault protection + quality sorting), which directly addresses the Innovation & Creativity scoring category (15 points).
