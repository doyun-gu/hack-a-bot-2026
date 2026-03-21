# Model A: Mechanical Load Increase — Implementation Guide

> Detailed design, wiring, and demo specification for the primary fault detection model
> in the GridBox Energy Signature Anomaly Detection system.
> GridBox — Hack-A-Bot 2026

---

## Factory System Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    GRIDBOX — MINIATURE SMART BOTTLING PLANT                    ║
║                         Model A: Mechanical Load Monitor                       ║
╚══════════════════════════════════════════════════════════════════════════════════╝

  POWER INPUT
  ┌─────────────┐
  │  12V 6A PSU │  ← "Recycled energy source"
  └──────┬──────┘
         │ 12V
    ┌────┴────┐
    │  Buck   │──→ 5V ──→ Pico A, PCA9685, Servos
    │ LM2596S │
    │  Buck-  │──→ 6-12V ─────────────────────────────────────┐
    │  Boost  │         (motor power rail)                     │
    └─────────┘                                                │
                                                               │
 ═══════════════════════════════════════════════════════════════════════════════
                          FACTORY FLOOR (Top-Down View)
 ═══════════════════════════════════════════════════════════════════════════════

   [WATER TANK]
        │
        │ water flow
        ▼
  ┌──────────────┐      ┌──────────────────────────────────────────────────┐
  │   MOTOR 1    │      │              CONVEYOR BELT                       │
  │  Water Pump  │      │                                                  │
  │  GP27 sense  │   ┌──┤ ○ ──────────────────────────────────── ○ ┤──┐   │
  │  GP10 MOSFET │   │  │    ← ← ← ←  belt direction  ← ← ← ←    │  │   │
  └──────┬───────┘   │  └──────────────────────────────────────────┘  │   │
         │           │                                                  │   │
         ▼           │         MOTOR 2 (Conveyor Drive)                │   │
    ┌─────────┐      │         ┌──────────────────┐                    │   │
    │  FILL   │      └─────────│  GP28 sense      │────────────────────┘   │
    │  VALVE  │                │  GP11 MOSFET     │                        │
    │ Servo 1 │                │  PCA9685 ch1 PWM │                        │
    │ PCA9685 │                └──────────────────┘                        │
    │  ch0    │                         ▲                                  │
    └────┬────┘                         │                                  │
         │                    ╔═════════╧═════════╗                        │
         │ water              ║  ◄◄ FAULT ZONE ►► ║                        │
         ▼                    ║                   ║                        │
  [BOTTLE POSITION]           ║  Press foam pad   ║                        │
     ┌───────┐                ║  here to increase ║                        │
     │  🍶   │                ║  friction load    ║                        │
     │Bottle │                ╚═══════════════════╝                        │
     └───┬───┘                                                             │
         │                                                                 │
         │ bottle travels on belt ──────────────────────────────────────►  │
         │                                                                 │
         ▼                                                                 │
  ┌──────────────┐                                                         │
  │   QUALITY    │                                                         │
  │    GATE      │ ← Servo 2 sorts: pass / reject                         │
  │  PCA9685 ch2 │                                                         │
  └──────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
                          ELECTRONICS (Pico A — Grid Controller)
 ═══════════════════════════════════════════════════════════════════════════════

                              PICO A (RP2350)
                         ┌──────────────────────┐
                         │                      │
          ADC GP26 ──────│ BUS VOLTAGE SENSE    │
                         │  (10kΩ + 10kΩ divider)│
                         │                      │
          ADC GP27 ──────│ MOTOR 1 CURRENT      │
                    ←────│  1Ω sense resistor   │
                         │                      │
          ADC GP28 ──────│ MOTOR 2 CURRENT ★    │  ← Core sensor for Model A
                    ←────│  1Ω sense resistor   │
                         │                      │
          I2C GP4/5 ─────│ BMI160 IMU           │  ← Vibration cross-check
                    ─────│ PCA9685 PWM driver   │
                         │                      │
          SPI GP0-3 ─────│ nRF24L01+ TX         │──→ wireless → Pico B
                         │                      │
          GPIO GP10 ─────│──→ MOSFET → Motor 1  │
          GPIO GP11 ─────│──→ MOSFET → Motor 2  │  ← Motor 2 power switch
          GPIO GP12 ─────│──→ MOSFET → LED bank │
          GPIO GP13 ─────│──→ MOSFET → Capacitor│
                         │                      │
          GPIO GP14 ─────│ Green LED (healthy)  │
          GPIO GP15 ─────│ Red LED   (fault)    │
                         │                      │
                         │  CORE 0: control loop│
                         │  CORE 1: ADC sampling│  ← 500Hz energy signature
                         └──────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
                     CURRENT SENSING CIRCUIT — Motor 2 (GP28)
 ═══════════════════════════════════════════════════════════════════════════════

   Buck-Boost (6-12V)
         │
         │
    ┌────┴────┐
    │  MOSFET │  ← GP11 gate (ON/OFF switch)
    │  IRF540 │
    └────┬────┘
         │
         ├──────────────── Motor 2 (+)
         │                 ┌────────┐
         │                 │ DC MTR │ ← Conveyor drive motor
         │                 └────────┘
         │                 Motor 2 (-)
         │                     │
         │              ┌──────┴──────┐
         │              │  1Ω SENSE   │  R_sense = 1.0Ω (1% tolerance)
         │              │  RESISTOR   │  Power rating ≥ 0.5W
         │              └──────┬──────┘
         │                     │
         │              ┌──────┴──────┐
         │              │  ADC GP28   │  V_adc = I_motor × 1.0Ω
         │              │  (0–3.3V)   │  I_motor = V_adc × 3.3 / 65535 × 1000 mA
         │              └─────────────┘
         │
        GND ─────────────────────────────────────────────── GND


 ═══════════════════════════════════════════════════════════════════════════════
                     SIGNAL PROCESSING PIPELINE (Core 1)
 ═══════════════════════════════════════════════════════════════════════════════

   GP28 ADC
      │
      │  read_u16() every 2ms (500Hz)
      ▼
  ┌─────────────────┐
  │  RAW SAMPLE     │  adc_raw → mA conversion
  │  BUFFER [500]   │  I = adc_raw × 3.3 / 65535 × 1000
  └────────┬────────┘
           │  1-second window fills
           ▼
  ┌─────────────────────────────────────────────────────┐
  │              EnergySignature EXTRACTION             │
  │                                                     │
  │  mean_current   = sum(samples) / 500                │
  │  std_current    = sqrt(sum((s - mean)²) / 500)      │
  │  crossing_rate  = count(sign changes vs mean)       │
  │  max_deviation  = max(abs(s - mean) for s)          │
  └────────────────────────┬────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────┐
  │              DIVERGENCE SCORE CALCULATION           │
  │                                                     │
  │  d_mean     = |curr.mean - base.mean| / base.mean   │
  │  d_std      = |curr.std  - base.std|  / base.std    │
  │  d_crossing = |curr.cr   - base.cr|   / base.cr     │
  │  d_maxdev   = |curr.maxd - base.maxd| / base.maxd   │
  │                                                     │
  │  score = 0.30×d_mean  + 0.25×d_std                  │
  │        + 0.25×d_cross + 0.20×d_maxdev               │
  │                                                     │
  │  score ∈ [0.0, 1.0]                                 │
  └────────────────────────┬────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────┐
  │              SERVO ANGLE MAPPING                    │
  │                                                     │
  │  angle = int(score × 180)                           │
  │                                                     │
  │   0°  ──────────── 90° ──────────────── 180°        │
  │  HEALTHY         WARNING              FAULT         │
  │  [0.00–0.14]  [0.15–0.69]         [0.70–1.00]       │
  └────────────────────────┬────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      Servo angle      OLED text      nRF packet → Pico B
      (PCA9685)       (Pico B)        (SCADA display)


 ═══════════════════════════════════════════════════════════════════════════════
                     WIRELESS LINK — Pico A → Pico B
 ═══════════════════════════════════════════════════════════════════════════════

  PICO A                                            PICO B
  (Factory Floor)                                   (Control Room)
  ┌─────────────┐      2.4GHz nRF24L01+      ┌─────────────────────┐
  │             │  ~~~~~~~~~~~~~~~~~~~~~~~~  │                     │
  │  TX packet  │ ~~~~~~~~~~~~~~~~~~~~~~~~~ │  RX + decode        │
  │  [32 bytes] │                            │                     │
  │             │                            │  ┌───────────────┐  │
  │  score      │                            │  │  OLED SSD1306 │  │
  │  mean_mA    │                            │  │               │  │
  │  std_mA     │                            │  │ ┌───────────┐ │  │
  │  cross_rate │                            │  │ │ENERGY SIG │ │  │
  │  fault_flag │                            │  │ │Score: 0.19│ │  │
  │  motor_rpm  │                            │  │ │DRIFT DET. │ │  │
  │             │                            │  │ └───────────┘ │  │
  └─────────────┘                            │  └───────────────┘  │
                                             │                     │
                                             │  Joystick → manual  │
                                             │  override / reset   │
                                             └─────────────────────┘
```

---

## What Model A Detects

Model A simulates the most common industrial failure mode: **mechanical load increase on a rotating machine**.

In the miniature factory, Motor 2 drives the conveyor belt. When physical resistance is added to the belt (by pressing a foam pad against it), the motor must draw more current to maintain speed. This mirrors real-world scenarios:

- Conveyor belt product jam at a bottling gate
- Pump impeller partially blocked by debris
- Fan blade accumulating ice or dust
- Bearing beginning to seize from insufficient lubrication

According to IEEE 493 (Gold Book), mechanical overload accounts for approximately 33% of all motor failures in industrial plants. This is the highest single failure category — making it the most impactful demo choice.

---

## Physical Demo Setup

### What You Need

| Item | Source | Purpose |
|---|---|---|
| Foam pad (~2cm²) | any sponge material | Increase belt friction during demo |
| Rubber band | stationary kit | Alternative friction source (more controlled) |
| Motor 2 wired and running | existing harness | Baseline signal |
| GP28 sense resistor in place | your wiring | Current measurement |

### Wiring Checklist (Wooseong)

Before demo, verify:

- [ ] 1Ω sense resistor on Motor 2 ground return path
- [ ] GP28 connected to the junction between sense resistor and GND
- [ ] MOSFET on GP11 switching Motor 2 power correctly
- [ ] PCA9685 channel 1 outputting PWM to Motor 2 speed control
- [ ] Motor 2 running at ~50% duty cycle for stable baseline (not too fast, not too slow)

### Sense Resistor Sizing

```
Motor 2 rated current:  ~500 mA (typical small DC motor)
Sense resistor:         1.0Ω, 1W rated (burn margin: 2×)
Voltage at full load:   V = 0.5A × 1Ω = 0.5V
ADC input range:        0–3.3V
ADC resolution:         65535 counts
Counts at 500mA:        500mV / 3300mV × 65535 ≈ 9930 counts  ✓ (well within range)
```

---

## Expected Signal Behaviour

### Baseline (healthy, no load)

```
mean_current   ≈ 420 mA
std_current    ≈  30 mA
crossing_rate  ≈  45 crossings / 500-sample window
max_deviation  ≈  85 mA
```

### Under finger/foam pressure (moderate load)

```
mean_current   ≈ 520 mA   (+24% — motor drawing more to fight friction)
std_current    ≈  34 mA   (+13% — slight hunting as motor adjusts)
crossing_rate  ≈  36 crossings  (-20% — motor slows, electrical freq drops)
max_deviation  ≈ 102 mA   (+20% — current peaks increase)
```

### Divergence score calculation (moderate load)

```
d_mean     = |520 - 420| / 420 = 0.238
d_std      = | 34 -  30| /  30 = 0.133
d_crossing = | 36 -  45| /  45 = 0.200
d_maxdev   = |102 -  85| /  85 = 0.200

score = 0.30×0.238 + 0.25×0.133 + 0.25×0.200 + 0.20×0.200
      = 0.071 + 0.033 + 0.050 + 0.040
      = 0.194
```

Servo angle: `0.194 × 180 ≈ 35°`
OLED: `DRIFT DETECTED — 0.19`

### Servo response table

| Pressure | Score | Servo | OLED |
|---|---|---|---|
| None | 0.00–0.05 | 0–9° | `HEALTHY — 0.03` |
| Light fingertip | 0.10–0.20 | 18–36° | `DRIFT — 0.15` |
| Moderate pad press | 0.20–0.40 | 36–72° | `DRIFT DETECTED — 0.30` |
| Heavy press (stall approach) | 0.50–0.70 | 90–126° | `PRE-FAULT — 0.55` |
| Full stall | 0.80–1.00 | 144–180° | `FAULT — MOTOR STALL` |

---

## EEE Theory — Why the Current Rises

### Back-EMF and Load Current

A DC motor in steady state obeys:

```
I_motor = (V_supply - V_back_EMF) / R_armature
```

Where `V_back_EMF ∝ motor_speed`.

When mechanical load increases:
1. Motor decelerates (speed drops)
2. `V_back_EMF` decreases
3. `(V_supply - V_back_EMF)` increases
4. `I_motor` increases

This is a self-reinforcing loop — more load → more current → more heat → accelerated wear. The energy signature detects the current rise **before** the temperature threshold is reached. That is the early warning.

### Affinity Laws (why this matters for energy)

For rotating machinery:

```
Power ∝ speed³
```

A 20% speed reduction (from load fighting the motor) = 49% power reduction if the controller were to respond by lowering the set point. GridBox can detect the drift and recommend a maintenance action before the motor burns out trying to maintain speed under overload.

### Zero-Crossing Rate as Frequency Proxy

The electrical ripple in a DC motor current is proportional to rotational speed (commutation frequency). When the motor slows under load:

```
f_electrical = (RPM × poles) / 60
```

Fewer crossings per window → lower RPM → confirms mechanical cause (not a power supply issue).

This distinguishes Model A (load increase) from Model B (voltage sag): both raise current, but only Model A also drops the crossing rate.

---

## Demo Choreography

| Time | Presenter Action | System Response | What to Say |
|---|---|---|---|
| T-60s | Start learning phase | OLED: `LEARNING... 0%` → `100%` | "The system is memorising the motor's heartbeat" |
| T+0:00 | Point to belt running normally | Needle at 0°, OLED: `HEALTHY — 0.02` | "Baseline established. Zero divergence from normal." |
| T+0:15 | Place foam pad lightly on belt | Needle drifts to ~25° over 3s | "Friction is increasing. Watch the needle move." |
| T+0:25 | Press slightly harder | Needle moves to ~45°, OLED: `DRIFT — 0.25` | "This is what a product jam looks like in the data." |
| T+0:35 | Release belt | Needle returns to 0° over ~8s | "Load removed. System re-centres. No false alarm." |
| T+0:50 | Full press (near stall) | Needle swings to ~100°, red LED, OLED: `PRE-FAULT — 0.56` | "At this point a real plant would schedule maintenance." |
| T+1:00 | Release | Recovery to green | "The needle came back — the fault was caught before failure." |

**Key talking point:** "A threshold alarm would only trigger at full stall — that's too late. Our system detected the drift at 0.19, giving the operator time to act."

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Motor too fast — friction not detectable | Medium | Reduce PWM duty cycle to 40–50% before demo. Slower motor = lower baseline current = larger relative change. |
| Motor stalls completely from too much pressure | Low | Brief full stall is fine — Model D. Just release quickly and show recovery. |
| Baseline learned incorrectly | Low | Pre-load fallback baseline at boot: `FALLBACK_BASELINE = EnergySignature(mean=420, std=30, crossing_rate=45, max_dev=85)` |
| Sense resistor voltage drop too low to read | Low | Verify GP28 reads at least 3000 counts at idle (use serial REPL to check before demo) |
| Belt slips off motor shaft | Medium | Wrap belt once extra around drive pulley. Test at demo speed beforehand. |

---

## Connection to Wider GridBox Story

Model A is not just a fault detector — it completes the GridBox narrative:

1. **Sustainability angle:** Motor running under load wastes energy (excess current = heat = waste). GridBox detects this and can autonomously reduce duty cycle, saving power.
2. **Autonomy angle:** No human needed to notice the belt is jammed. The system detects, alerts, and can reroute power to backup systems automatically.
3. **Sensor fusion angle:** When Model A triggers (high current) at the same time the BMI160 IMU detects increased vibration (motor hunting under load) — two independent sensors confirm the same fault. "No false positives."

**Pitch sentence for this moment:**
"The energy signature rose. The vibration sensor agreed. Two independent measurements, one fault confirmed. That is sensor fusion — and it happened on a £15 microcontroller."
