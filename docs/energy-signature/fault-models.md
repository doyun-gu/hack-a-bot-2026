# GridBox Energy Signature — Fault Models Reference

> Detailed technical specification for each fault model used in the Energy Signature Anomaly Detection system.
> For use during implementation, testing, and demo preparation.
> GridBox — Hack-A-Bot 2026

---

## Signature Metrics Reference

All fault models are evaluated against these four metrics, sampled at 500Hz in 1-second windows on Pico A Core 1:

| Metric | Symbol | Unit | What It Measures |
|---|---|---|---|
| Mean Current | `mean_current` | mA | Average current draw over window |
| Std Current | `std_current` | mA | Variability / noise in current draw |
| Crossing Rate | `crossing_rate` | crossings/window | How often signal crosses its own mean (frequency proxy) |
| Max Deviation | `max_deviation` | mA | Largest single-sample distance from mean (amplitude envelope) |

---

## Model A: Mechanical Load Increase

**Classification:** RECOMMENDED — Primary Demo
**Demo reliability:** 10/10
**Demo order:** 1st (safest opener, guaranteed to work)

### Industrial Scenario

A conveyor belt in a bottling plant encounters a product jam. Bottles pile up at a gate, increasing the friction load on the belt motor. The motor draws more current to maintain speed against the increased resistance. Over minutes to hours, the current draw creeps upward as the jam worsens — a textbook precursor to motor burnout or belt snap.

Real-world equivalents:
- Conveyor belt product jam or misaligned roller
- Pump impeller partially blocked by debris
- Fan blade accumulating dust/ice, increasing drag
- Bearing beginning to seize due to inadequate lubrication

This is the single most common failure mode in rotating machinery. According to IEEE 493 (Gold Book), mechanical overload accounts for ~33% of motor failures in industrial plants.

### Physical Setup

**Hardware required:** Conveyor motor (Motor 2, DC), foam pad or thick rubber band, breadboard wiring already in place.

**Steps:**
1. Motor 2 runs at normal PWM duty cycle via PCA9685 channel (I2C 0x40)
2. Current is sensed through the 1-ohm sense resistor on GP28 (Pico A ADC2)
3. Voltage reference: `V_sense = I_motor × R_sense = I_motor × 1.0 ohm`
4. ADC reads: `adc_value = machine.ADC(28).read_u16()` → convert to mA
5. During demo: presenter presses a foam pad against the conveyor belt surface, increasing friction gradually

**Pin mapping:**
```
GP28 (ADC2) ←── 1-ohm sense resistor ←── Motor 2 ground return
GP11 (GPIO) ──→ MOSFET gate ──→ Motor 2 power switch
PCA9685 ch1 ──→ Motor 2 PWM speed control
```

### Expected Signature Changes

Baseline (healthy motor, no load):
```
mean_current   = ~420 mA
std_current    = ~30 mA
crossing_rate  = ~45 crossings/window
max_deviation  = ~85 mA
```

Under increasing mechanical load (finger pressure on belt):

| Metric | Direction | Magnitude | Why |
|---|---|---|---|
| `mean_current` | **rises** | +15% to +40% (480–590 mA) | Motor draws more current to maintain torque against friction. Ohm's law: increased back-EMF reduction → more current. |
| `std_current` | **rises slightly** | +10% to +20% (33–36 mA) | Increased load creates more turbulent current draw as motor hunts for equilibrium speed. |
| `crossing_rate` | **drops** | -10% to -30% (31–40 crossings) | Motor slows under load → electrical frequency drops → fewer zero crossings per window. |
| `max_deviation` | **rises** | +15% to +30% (98–110 mA) | Current peaks increase as motor pulses harder to overcome resistance. |

### Detection Logic

Primary trigger: `d_mean` (0.30 weight) — mean current shift is the dominant signal.
Secondary trigger: `d_crossing` (0.25 weight) — crossing rate drop confirms the fault is mechanical (not electrical).

Expected divergence score: **0.15–0.45** depending on pressure applied.

```python
# Example calculation at moderate load:
d_mean     = abs(520 - 420) / 420 = 0.238
d_std      = abs(34 - 30) / 30   = 0.133
d_crossing = abs(36 - 45) / 45   = 0.200
d_maxdev   = abs(102 - 85) / 85  = 0.200

score = 0.30×0.238 + 0.25×0.133 + 0.25×0.200 + 0.20×0.200
      = 0.071 + 0.033 + 0.050 + 0.040
      = 0.194
```

Score of 0.194 → servo at ~35° → OLED: "DRIFT DETECTED — 0.19"

### Servo Response

| Score Range | Servo Angle | OLED Display |
|---|---|---|
| 0.00–0.15 | 0°–27° | HEALTHY — {score} |
| 0.15–0.30 | 27°–54° | DRIFT — {score} |
| 0.30–0.50 | 54°–90° | DEGRADING — {score} |

For this model, expect the servo to sweep from 0° to ~35°–80° depending on how hard you press.

### Demo Choreography

**Time:** 1:00–1:15 in the demo script (15 seconds)

| Second | Presenter Action | Presenter Says | System Response |
|---|---|---|---|
| 0 | Points to conveyor motor running normally | "This motor is running healthy. The energy signature baseline is locked in." | Servo at 0°, OLED: HEALTHY |
| 3 | Slowly presses foam pad against belt | "Now I'm simulating a product jam — increasing the mechanical load on the belt." | Servo begins drifting clockwise |
| 6 | Maintains pressure | "Watch the needle. The system detected the load change within 2 seconds. No vibration sensor needed — just current." | Servo at ~35°, OLED: DRIFT — 0.22 |
| 10 | Slowly releases pressure | "When I remove the blockage, the signature recovers." | Servo drifts back toward 0° |
| 15 | Points to OLED | "Back to healthy. That's predictive — the motor never actually failed." | Servo at 0°, OLED: HEALTHY |

**Key talking point:** "In a real factory, this drift would happen over hours, not seconds. The operator watches the needle creep and schedules maintenance before the line goes down."

### Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Motor too weak — stalls instead of loading | Low | Use Motor 2 (conveyor), not Motor 1 (pump). Conveyor motors handle load better. |
| ADC noise masks the signal | Low | 1-ohm sense resistor gives ~420mV at 420mA — well above ADC noise floor (~3mV on RP2350). |
| Foam pad slips, inconsistent pressure | Medium | Use rubber band wrapped around shaft instead — provides consistent, repeatable friction. |
| Score doesn't cross 0.15 threshold | Low | If current change is <15%, increase pressure or adjust threshold down to 0.10 during calibration. |

### EEE Theory Connection

**Ohm's Law:** `V_sense = I × R = I × 1.0 ohm` — the 1-ohm sense resistor converts current to voltage for the ADC. At 420mA baseline, the ADC sees 420mV.

**Motor torque equation:** `T = K_t × I` where K_t is the torque constant. Increasing mechanical load requires more torque → more current. This is the fundamental physics behind the detection.

**Affinity Laws:** For the pump motor (Model A variant), `P is proportional to n cubed`. Even a small speed reduction from loading implies significant power change — the cubic relationship amplifies the signal.

**ADC conversion:**
```
V_adc = adc_raw × 3.3 / 65535       # RP2350 ADC is 12-bit but read_u16 scales to 16-bit
I_motor = V_adc / R_sense            # R_sense = 1.0 ohm
I_mA = I_motor × 1000
```

### Judge Q&A

**Q: "Isn't this just an overcurrent alarm?"**
A: "An overcurrent alarm has one threshold — above it is fault, below is OK. We have a continuous score. A 5% current increase scores 0.05 — not a fault, but recorded. A 20% increase scores 0.20 — that's the amber zone where you schedule maintenance. A 50% increase scores 0.45 — stop the line. The gradient is the innovation."

**Q: "What if the motor naturally varies in load?"**
A: "The std_current metric captures normal variability during the learning phase. We're looking for deviation from that variability, not from a fixed number. If the motor normally fluctuates 30 plus or minus 5 mA, we only flag when it fluctuates 30 plus or minus 15 mA."

**Q: "How do you distinguish a load increase from a supply voltage increase?"**
A: "A load increase raises mean current AND drops crossing rate — the motor slows down. A supply voltage increase raises mean current but raises crossing rate — the motor speeds up. The crossing rate disambiguates."

---

## Model B: Voltage Sag / Brownout

**Classification:** OPTIONAL — Secondary Demo (use if time permits)
**Demo reliability:** 9/10
**Demo order:** Not in primary script (substitute for Model A if pot is more accessible than foam pad)

### Industrial Scenario

A factory power grid experiences a brownout — supply voltage drops 10–20% due to peak demand elsewhere in the facility. Motors connected to the degraded bus run slower, draw different current, and may overheat if the sag persists. This is the second most common power quality event in industrial settings after voltage spikes.

Real-world equivalents:
- Grid brownout during peak summer demand
- Generator fuel running low, output voltage sagging
- Long cable run with excessive voltage drop under load
- Transformer tap changer malfunction

### Physical Setup

**Hardware required:** Potentiometer (already wired to Pico B GP28), buck-boost converter (300W, adjustable output).

**The challenge:** The potentiometer is wired to Pico B, not Pico A. It cannot directly adjust the buck-boost output in the current architecture. Two options:

**Option 1 (Preferred):** Manually turn the buck-boost trim pot during demo. Most LM2596S / XL6009 modules have a small multi-turn potentiometer. Use a screwdriver to adjust output voltage from 12V down to 10V.

**Option 2 (If buck-boost is sealed):** Add a power resistor (2-5 ohm, 5W) in series with the motor power line. Insert it via a breadboard jumper during demo. This drops voltage by V = I × R at the motor.

**Pin mapping (sensing side):**
```
GP27 (ADC1) ←── 1-ohm sense resistor ←── Motor 1 ground return
GP26 (ADC0) ←── voltage divider (10k+10k) ←── bus voltage
```

GP26 provides bus voltage confirmation — if both voltage drops AND current changes, it's a supply issue, not a mechanical one.

### Expected Signature Changes

Baseline (healthy, 12V supply):
```
mean_current   = ~420 mA
std_current    = ~30 mA
crossing_rate  = ~45 crossings/window
max_deviation  = ~85 mA
```

Under voltage sag (supply drops to ~10V):

| Metric | Direction | Magnitude | Why |
|---|---|---|---|
| `mean_current` | **drops** | -10% to -25% (315–378 mA) | Less voltage → less current through the motor (V=IR). Motor runs slower. |
| `std_current` | **rises slightly** | +5% to +15% (31–34 mA) | Motor hunting at lower speed, PWM compensation introduces ripple. |
| `crossing_rate` | **drops** | -15% to -25% (34–38 crossings) | Motor speed drops proportionally with voltage → lower electrical frequency. |
| `max_deviation` | **drops** | -10% to -20% (68–76 mA) | Lower supply voltage means smaller current peaks. |

### Detection Logic

Primary trigger: `d_mean` + `d_crossing` both drop together — this pattern uniquely identifies a supply-side fault (not mechanical). Cross-reference with GP26 bus voltage ADC to confirm voltage sag.

Expected divergence score: **0.12–0.30**

```python
# Example at 10V supply (from 12V baseline):
d_mean     = abs(350 - 420) / 420 = 0.167
d_std      = abs(33 - 30) / 30    = 0.100
d_crossing = abs(36 - 45) / 45    = 0.200
d_maxdev   = abs(72 - 85) / 85    = 0.153

score = 0.30×0.167 + 0.25×0.100 + 0.25×0.200 + 0.20×0.153
      = 0.050 + 0.025 + 0.050 + 0.031
      = 0.156
```

### Servo Response

Score 0.156 → servo at ~28° → OLED: "DRIFT — 0.16 (SUPPLY)"

The "(SUPPLY)" label can be added if GP26 voltage divider confirms bus voltage dropped simultaneously — differentiating from a mechanical fault.

### Demo Choreography

Not in the primary 3:30 script. Use as an alternate if Model A foam pad is unreliable:

| Second | Presenter Action | Presenter Says |
|---|---|---|
| 0 | Points to buck-boost module | "This converter supplies motor power. Watch what happens when the grid sags." |
| 3 | Turns trim pot slowly | "I'm dropping supply voltage — simulating a brownout." |
| 8 | Points to servo + OLED | "The system detected the supply change. Notice it shows SUPPLY, not FAULT — because it cross-references the bus voltage sensor." |
| 12 | Turns trim pot back | "Supply restored. Signature recovers." |

### Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Buck-boost trim pot is inaccessible | Medium | Pre-check during setup. If sealed, use Option 2 (series resistor). |
| Voltage change too small to detect | Low | A 2V drop on a 12V supply is 17% — well above the 0.15 threshold. |
| Adjusting voltage affects all motors simultaneously | Low | This is actually realistic — a brownout affects the whole bus. Both motors' signatures shift. |
| Trim pot breaks the converter | Low | Turn slowly, small adjustments only. Never go below 8V. |

### EEE Theory Connection

**Voltage divider (bus sensing):**
```
V_adc = V_bus × R2 / (R1 + R2) = V_bus × 10k / (10k + 10k) = V_bus / 2
```
At 12V: V_adc = 6.0V → clamped to 3.3V by Pico. **Note:** Need a 3:1 divider (10k + 20k) to keep ADC within range, or use the existing 10k+10k divider with a 6V max bus assumption.

**Ohm's Law (motor model):** `I = (V_supply - V_backEMF) / R_winding`. When V_supply drops, current drops, motor slows, V_backEMF drops — a coupled system that settles at a new equilibrium.

### Judge Q&A

**Q: "Can the system distinguish a brownout from a motor fault?"**
A: "Yes. A brownout drops both mean current AND max deviation — the motor runs quieter overall. A mechanical fault raises mean current and drops crossing rate — the motor works harder. The signature pattern is different, and we can cross-reference with the bus voltage ADC on GP26."

---

## Model C: Intermittent Connection

**Classification:** RECOMMENDED — Dramatic Demo
**Demo reliability:** 7/10
**Demo order:** 2nd in the primary script (after Model A establishes credibility)

### Industrial Scenario

A terminal on a motor junction box has corroded over months of exposure to humidity. The connection resistance fluctuates — sometimes making good contact, sometimes partial contact, sometimes open. The motor stutters, receiving power intermittently. This is the "mystery fault" that drives maintenance engineers mad — the motor works fine during inspection but fails under vibration or thermal expansion.

Real-world equivalents:
- Corroded screw terminal on motor junction box
- Crimped connector with hairline wire fracture
- Relay contact pitting from arc erosion
- Slip ring brush wear on wound-rotor motors
- Vibration-induced connector unseating

According to EPRI studies, intermittent connections cause ~12% of unplanned industrial outages and are the hardest fault type to diagnose with conventional tools because they don't trigger threshold alarms consistently.

### Physical Setup

**Hardware required:** One additional jumper wire (loose), existing motor power path.

**Steps:**
1. Identify the power wire between MOSFET output (GP10 or GP11) and Motor 1 or Motor 2
2. Insert a jumper wire in series — but leave one end loosely seated in the breadboard (1-2mm of contact, not fully pushed in)
3. During demo: gently tap or wiggle the breadboard near the loose connection
4. The intermittent contact creates rapid on-off-on current fluctuations

**Pin mapping:**
```
GP27 (ADC1) ←── 1-ohm sense resistor ←── [LOOSE JUMPER HERE] ←── Motor 1
GP10 (GPIO) ──→ MOSFET gate ──→ Motor 1 power
```

**Preparation note:** Test the loose connection before the demo. The jumper should be seated enough that the motor runs normally when the breadboard is undisturbed, but loses contact with a light tap. Practice the wiggle motion — too hard and it disconnects fully (becomes Model D), too soft and nothing happens.

### Expected Signature Changes

Baseline (healthy, solid connection):
```
mean_current   = ~420 mA
std_current    = ~30 mA
crossing_rate  = ~45 crossings/window
max_deviation  = ~85 mA
```

Under intermittent connection (loose wire wiggled):

| Metric | Direction | Magnitude | Why |
|---|---|---|---|
| `mean_current` | **drops slightly** | -5% to -15% (357–399 mA) | Average is reduced because current is zero during disconnected intervals. |
| `std_current` | **spikes dramatically** | +200% to +500% (90–180 mA) | The defining signature. Current oscillates between full draw and zero unpredictably. |
| `crossing_rate` | **spikes erratically** | +50% to +200% (68–135 crossings) | Rapid on-off creates many zero-crossings that have nothing to do with motor frequency. |
| `max_deviation` | **rises** | +50% to +100% (128–170 mA) | Full current vs zero current creates extreme deviations from the (now-lowered) mean. |

### Detection Logic

Primary trigger: `d_std` (0.25 weight) — this is the one fault type where std dominance is overwhelming. A 3x increase in std is unmistakable.

Secondary trigger: `d_crossing` (0.25 weight) — erratic crossing rate confirms the fault is electrical (connection), not mechanical (load).

Expected divergence score: **0.50–0.90** — this is the highest-scoring fault model.

```python
# Example at moderate intermittent contact:
d_mean     = abs(380 - 420) / 420 = 0.095
d_std      = abs(120 - 30) / 30   = 3.000  # capped contribution
d_crossing = abs(90 - 45) / 45    = 1.000
d_maxdev   = abs(150 - 85) / 85   = 0.765

# Before capping to 1.0:
score = 0.30×0.095 + 0.25×3.000 + 0.25×1.000 + 0.20×0.765
      = 0.029 + 0.750 + 0.250 + 0.153
      = 1.182 → capped to 1.0
```

**Note:** The raw score exceeds 1.0 easily. The `min(score, 1.0)` cap fires. This means the servo slams to near 180° — which is correct. Intermittent connections are severe faults.

**Implementation consideration:** You may want to add individual metric capping (e.g., cap each `d_x` at 2.0 before weighting) to maintain score granularity across fault types. Otherwise, intermittent connections always saturate at 1.0 regardless of severity.

```python
# Improved with per-metric capping:
d_mean     = min(abs(current.mean - baseline.mean) / baseline.mean, 2.0)
d_std      = min(abs(current.std - baseline.std) / baseline.std, 2.0)
d_crossing = min(abs(current.xing - baseline.xing) / baseline.xing, 2.0)
d_maxdev   = min(abs(current.maxd - baseline.maxd) / baseline.maxd, 2.0)
```

### Servo Response

Score saturates at 1.0 → servo at 180° (full fault) during active wiggling.
Between wiggles (connection re-seats): score drops to 0.3–0.5 → servo at 54°–90°.

The needle **jittering** between 90° and 180° is the visual that sells this model. It looks like a seismograph.

| State | Score | Servo | OLED |
|---|---|---|---|
| Between wiggles | 0.30–0.50 | 54°–90° | PRE-FAULT — {score} |
| During wiggle | 0.80–1.00 | 144°–180° | FAULT — {score} |
| Connection re-seated | recovering | drifting back | RECOVERING |

### Demo Choreography

**Time:** 1:45–2:00 in the demo script (15 seconds)

| Second | Presenter Action | Presenter Says | System Response |
|---|---|---|---|
| 0 | Points to breadboard | "This jumper wire is deliberately loose. In a factory, this is a corroded terminal — the fault you can't find during scheduled inspection." | Servo at 0°, HEALTHY |
| 3 | Taps breadboard lightly | "A slight vibration..." | Servo jitters to ~60°, OLED flickers |
| 5 | Wiggles breadboard | "...and the connection fails intermittently." | Servo swings wildly 90°–180°, OLED: PRE-FAULT |
| 8 | Stops wiggling | "The moment I stop, the connection re-seats. Traditional alarms would clear. But watch the score..." | Servo drifts back slowly, score still elevated |
| 12 | Points to OLED score | "The system remembers the instability. The score stays elevated even after the symptom disappears. That's the difference between detection and diagnosis." | Servo at ~30°, score ~0.18 |
| 15 | Pushes jumper wire firmly in | "Now it's properly connected again." | Returns to 0° over 10s |

**Key talking point:** "An intermittent connection is the hardest fault to find with conventional tools because it's only broken when you're not looking. Energy signature analysis catches the statistical ghost — the variance explosion — even if the mean current looks normal."

### Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Loose wire falls out completely | Medium | Practice the seating depth. Use a longer jumper — more surface contact, more controllable. |
| Loose wire has no effect (too tight) | Medium | Test before demo. The wire should run the motor normally when undisturbed. |
| Breadboard tap affects other connections | Low | Use a separate breadboard section for the loose wire, isolated from critical paths. |
| Motor stops entirely (becomes Model D) | Medium | This is actually fine — pivot to "and if the connection fails completely, watch what happens" and demonstrate Model D. |

**Fallback:** If Model C is unreliable during pre-demo testing, skip it from the script. Model A + Model D + Fail-safe is a complete demo without it. Model C is high reward but higher risk.

### EEE Theory Connection

**Contact resistance:** A corroded terminal has variable contact resistance R_contact. The total circuit resistance becomes R_winding + R_contact(t), where R_contact(t) fluctuates between ~0 ohm (good contact) and infinity (open circuit).

**Current during intermittent contact:**
```
I(t) = V_supply / (R_winding + R_contact(t))

When R_contact = 0:    I = V / R_winding = normal current
When R_contact = inf:  I = 0
When R_contact = 5 ohm: I = V / (R_winding + 5) = reduced current
```

The rapid switching between these states creates the characteristic std explosion.

**Arc energy:** At the moment of contact break, a small arc forms across the gap. Arc energy `E_arc = V_arc × I_arc × t_arc`. In real industrial systems, this arc progressively damages the contact surface, making the intermittent fault worse over time — a positive feedback loop.

### Judge Q&A

**Q: "How is this different from electrical noise?"**
A: "Electrical noise is symmetric and high-frequency — it increases std slightly but doesn't change mean or crossing rate. An intermittent connection creates asymmetric dropout events — current goes to zero then returns to full. The crossing rate spikes because each dropout creates two crossings. Noise creates small deviations; intermittent connections create full-scale deviations."

**Q: "Can you tell which connection is failing?"**
A: "With one current sensor per motor branch, we can tell which motor's circuit has the fault. We can't pinpoint the exact terminal — that requires physical inspection. But knowing which branch to inspect narrows a factory walkdown from hours to minutes."

---

## Model D: Motor Stall / Complete Stop

**Classification:** EXISTING — Already implemented via IMU; energy signature adds cross-validation
**Demo reliability:** 10/10
**Demo order:** 3rd in the primary script (the climax — sensor fusion moment)

### Industrial Scenario

A pump impeller seizes due to a foreign object (bolt, debris, ice) jamming the rotation. The motor attempts to continue spinning — stall current surges to 5-8x normal running current. If the overload protection doesn't trip within seconds, the motor windings overheat and the motor is destroyed. This is the most catastrophic (and expensive) motor failure mode.

Real-world equivalents:
- Pump impeller seized by foreign object
- Conveyor belt jammed by misaligned product
- Compressor locked rotor due to liquid slugging
- Gearbox tooth fracture causing immediate lockup
- Frozen bearing (complete seizure, not partial wear)

### Physical Setup

**Hardware required:** Motor 1 (pump/fan), hand grip or clamp, existing IMU (BMI160) on motor mount.

**Steps:**
1. Motor 1 runs at normal speed
2. IMU (BMI160 at I2C 0x68) monitors vibration on Core 1 (existing code)
3. Current sensed on GP27 (ADC1) through 1-ohm sense resistor
4. During demo: physically grip the motor shaft or housing to stop rotation
5. Alternative: shake the motor body vigorously (existing IMU demo step)

**Pin mapping:**
```
GP27 (ADC1) ←── 1-ohm sense resistor ←── Motor 1 ground return
GP10 (GPIO) ──→ MOSFET gate ──→ Motor 1 power switch
GP4/GP5 (I2C) ──→ BMI160 IMU (0x68) ──→ vibration data
```

**Two detection paths (sensor fusion):**
```
Path 1: GP27 ADC → current signature → divergence score → wireless → servo
Path 2: BMI160 I2C → vibration RMS → ISO 10816 threshold → wireless → OLED
```

Both paths trigger independently. When both trigger simultaneously, display "DUAL CONFIRM" — highest confidence fault declaration.

### Expected Signature Changes

**Phase 1: Stall current surge (0–500ms after seizure)**

| Metric | Direction | Magnitude | Why |
|---|---|---|---|
| `mean_current` | **spikes** | +200% to +500% (1260–2520 mA) | Motor draws locked-rotor current. Without back-EMF, current is limited only by winding resistance (typically 2-5 ohm for small DC motors). |
| `std_current` | **drops to near zero** | -80% (~6 mA) | Current is high but constant — no rotation means no ripple. |
| `crossing_rate` | **drops to zero** | -100% (0 crossings) | No oscillation. Flat DC at stall current. |
| `max_deviation` | **drops** | -50% (~42 mA) | Flat line — no peaks above or below. |

**Phase 2: Motor stopped / power cut (>500ms)**

If the MOSFET protection trips (firmware should do this when current exceeds threshold):

| Metric | Direction | Magnitude | Why |
|---|---|---|---|
| `mean_current` | **drops to zero** | -100% (0 mA) | Motor power cut by firmware or MOSFET driver. |
| `std_current` | **drops to zero** | -100% (0 mA) | No current, no variability. |
| `crossing_rate` | **drops to zero** | -100% (0 crossings) | No signal. |
| `max_deviation` | **drops to zero** | -100% (0 mA) | No signal. |

### Detection Logic

**Phase 1 detection:** `d_mean` spikes massively (200–500% increase). Score saturates at 1.0 within the first sample window (1 second).

**Phase 2 detection:** All metrics drop to zero. Score saturates at 1.0 from a different direction — everything is different from baseline.

**Sensor fusion logic:**
```python
imu_fault = vibration_rms > ISO_10816_THRESHOLD  # existing code
energy_fault = divergence_score > 0.70            # new code

if imu_fault and energy_fault:
    fault_confidence = "DUAL_CONFIRM"    # highest confidence
    oled_display = "FAULT — DUAL CONFIRM"
elif energy_fault:
    fault_confidence = "ENERGY_ONLY"     # energy signature triggered, IMU didn't
    oled_display = "FAULT — ENERGY SIG"
elif imu_fault:
    fault_confidence = "IMU_ONLY"        # vibration triggered, energy didn't
    oled_display = "FAULT — VIBRATION"
```

Expected divergence score: **1.0** (saturated) within 1 second.

### Servo Response

| Phase | Score | Servo | OLED |
|---|---|---|---|
| Stall surge (first 0.5s) | 1.0 | 180° (immediate) | FAULT — STALL CURRENT |
| Power cut by firmware | 1.0 | 180° (held) | FAULT — MOTOR STOPPED |
| IMU + energy confirm | 1.0 | 180° (held) | FAULT — DUAL CONFIRM |
| Recovery (after joystick reset) | decaying | returning to 0° | RECOVERING |

### Demo Choreography

**Time:** 2:30–3:00 in the demo script (30 seconds — the climax)

| Second | Presenter Action | Presenter Says | System Response |
|---|---|---|---|
| 0 | Points to Motor 1 running | "Both systems are watching this motor — vibration and energy signature, independently." | Servo at 0°, HEALTHY |
| 3 | Grips motor housing, shakes it | "Bearing seizure." | IMU alarm triggers on OLED |
| 4 | (continues shaking) | "The vibration sensor caught it — but look at the energy needle..." | Servo swings to 180° |
| 6 | Points to OLED | "DUAL CONFIRM. Two completely independent detection methods — vibration and current — both agree. This isn't a false positive." | OLED: FAULT — DUAL CONFIRM |
| 10 | Releases motor | "In a real plant, the firmware already cut power to this motor to prevent winding damage." | Motor stops (firmware protection) |
| 15 | Presses joystick to reset | "Maintenance resets the system after inspection." | Servo returns to 0° over 10s |
| 25 | Points to OLED history | "The fault is logged. The energy signature baseline re-learns from the repaired motor." | OLED: LEARNING... then HEALTHY |

**Key talking point:** "Any one sensor can have a false positive. When two independent physics — vibration and electrical current — both trigger at the same time, you have certainty. That's sensor fusion on a £15 system."

### Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Motor shaft too small to grip | Low | Grip the housing instead. Shaking produces the same IMU + current signature. |
| Stall current exceeds sense resistor power rating | Medium | P = I squared × R = (2A)^2 × 1 = 4W. Use a 5W or higher rated sense resistor. Or: firmware cuts power within 500ms, limiting thermal exposure. |
| IMU triggers but energy signature doesn't (or vice versa) | Low | Both are valid fault signals independently. Fusion is a bonus, not a requirement. Frame it as: "even partial agreement raises confidence." |
| Motor doesn't restart after stall | Low | Small DC motors recover from stalls reliably. If the motor overheats, swap to Motor 2 for the rest of the demo. |

### EEE Theory Connection

**Locked-rotor current:** `I_stall = V_supply / R_winding`. For a typical small DC motor: `I_stall = 12V / 3 ohm = 4A`. This is 5-10x normal running current. The sense resistor sees `V_sense = 4A × 1 ohm = 4V` — which exceeds the Pico's 3.3V ADC range. **The ADC will clip at 3.3V.** This clipping is itself a stall indicator — any saturated ADC reading means stall current.

**ISO 10816 (vibration classification):**
```
a_rms = sqrt(ax^2 + ay^2 + az^2)

Zone A: a_rms < 0.71 mm/s  — newly commissioned
Zone B: a_rms < 1.8 mm/s   — acceptable for long-term
Zone C: a_rms < 4.5 mm/s   — short-term only
Zone D: a_rms > 4.5 mm/s   — damage occurring
```

When you shake the motor, `a_rms` jumps to Zone C or D. The energy signature confirms the vibration isn't mechanical noise — it's a real fault.

**Thermal protection:** Motor winding temperature rise during stall: `delta_T = I^2 × R × t / (m × c)`. At 4A stall current, a small motor reaches thermal limit in 5-10 seconds. Firmware must cut power within 1 second. The energy signature detection (1-second window) provides this timing.

### Judge Q&A

**Q: "Why do you need two detection methods? Isn't one enough?"**
A: "Reliability. The vibration sensor can false-positive from external vibration — someone bumps the table. The energy signature can false-positive from a supply glitch. When both agree, the false positive probability is the product of individual false positive rates — orders of magnitude lower."

**Q: "What happens if the IMU and energy signature disagree?"**
A: "We report both independently. If only vibration triggers, it might be external disturbance — monitor but don't stop the line. If only energy triggers, it might be an electrical fault the IMU can't see — like an intermittent connection. Disagreement is diagnostic information."

**Q: "Doesn't the ADC clip during stall?"**
A: "Yes — at 4A through a 1-ohm resistor, the ADC sees 4V, but it clips at 3.3V. That clipping is actually useful — a saturated ADC reading is an unambiguous stall indicator. We don't need the exact current value; we just need to know it's way above normal."

---

## Model E: Communication Loss / Node Offline (Fail-Safe)

**Classification:** REQUIRED — Fail-safe design (not technically a "fault model" but a system safety feature)
**Demo reliability:** 10/10
**Demo order:** 4th (final, most dramatic ending)

### Industrial Scenario

A sensor node on a remote pump station loses power. The SCADA system receives no data. In a conventional system, the dashboard shows "N/A" or "OFFLINE" — a passive display that an operator might miss during a busy shift.

In GridBox, silence is treated as the most severe fault. The health servo moves to 180° (full fault) automatically when communication is lost. The system fails into a safe state — requiring active proof of health to stay green.

Real-world equivalents:
- Remote sensor node loses power (supply failure, fuse blown)
- Wireless link fails (interference, antenna damage, range exceeded)
- Field controller crashes (firmware hang, watchdog timeout)
- Cable cut between sensor and control room

This is fundamental to safety-critical embedded systems design. IEC 61508 (functional safety) requires that loss of the safety function is itself detected and reported.

### Physical Setup

**Hardware required:** Pico A power cable (USB or 5V supply wire), Pico B with OLED and servo already running.

**Steps:**
1. Both Picos running normally, wireless link active
2. Pico A sends heartbeat packets to Pico B every 20ms (50Hz telemetry)
3. Pico B monitors time since last received packet
4. During demo: physically unplug Pico A's power cable
5. Pico B detects heartbeat timeout after configurable delay (default: 2 seconds)
6. Servo moves to 180°, OLED displays "NODE OFFLINE"

**Pin mapping (Pico B side):**
```
SPI GP0-3,GP16 ←── nRF24L01+ RX ←── wireless heartbeat from Pico A
PCA9685 (I2C 0x40) ──→ Servo 2 (health meter)
OLED (I2C 0x3C) ──→ "NODE OFFLINE" display
```

**Wireless packet (heartbeat):**
```python
# 32-byte packet from Pico A includes:
{
    'seq': uint16,           # sequence number (rollover detection)
    'score': float16,        # divergence score
    'mean': float16,         # current mean
    'std': float16,          # current std
    'state': uint8,          # 0=learning, 1=healthy, 2=degrading, 3=fault
    'uptime_s': uint16,      # seconds since boot
    'checksum': uint8        # XOR checksum
}
```

When Pico A loses power, these packets stop. Pico B's receive loop times out.

### Detection Logic

```python
HEARTBEAT_TIMEOUT_MS = 2000  # 2 seconds without packet = offline

last_heartbeat = time.ticks_ms()

def check_heartbeat():
    elapsed = time.ticks_diff(time.ticks_ms(), last_heartbeat)
    if elapsed > HEARTBEAT_TIMEOUT_MS:
        return "OFFLINE"
    elif elapsed > HEARTBEAT_TIMEOUT_MS // 2:
        return "DEGRADED_LINK"  # packets arriving late
    else:
        return "CONNECTED"
```

**Three states:**
| State | Condition | Servo | OLED |
|---|---|---|---|
| CONNECTED | Packet received within 1s | normal (score-based) | Live health data |
| DEGRADED_LINK | Last packet 1–2s ago | 150° | LINK DEGRADED |
| OFFLINE | No packet for >2s | 180° (held) | NODE OFFLINE |

### Servo Response

The servo **slams** to 180° on timeout — it does not drift gradually. This is intentional. The transition from "last known score" to 180° is abrupt and dramatic.

```python
if heartbeat_state == "OFFLINE":
    servo_angle = 180  # immediate, no smoothing
    oled_text = "NODE OFFLINE"
elif heartbeat_state == "DEGRADED_LINK":
    servo_angle = 150  # warning
    oled_text = "LINK DEGRADED"
else:
    servo_angle = int(divergence_score * 180)  # normal mapping
```

### Demo Choreography

**Time:** 3:00–3:15 in the demo script (15 seconds — the finale)

| Second | Presenter Action | Presenter Says | System Response |
|---|---|---|---|
| 0 | Holds Pico A power cable | "This is the sensor node — the one doing all the monitoring. What happens when it dies?" | Normal operation |
| 2 | Pulls the USB cable | (silence — let the audience watch) | Pico A LEDs go dark |
| 4 | Points to servo | "Two seconds of silence..." | Servo snaps to 180° |
| 5 | Points to OLED | "NODE OFFLINE. The system didn't wait for an error message. It noticed the absence of proof that everything is OK." | OLED: NODE OFFLINE |
| 8 | Pauses for effect | "Silence is the loudest fault signal. If the machine can't tell you it's healthy, assume it isn't." | Servo held at 180° |
| 12 | Plugs Pico A back in | "And when power returns..." | Pico A boots, OLED: LEARNING... |
| 15 | Points to servo recovering | "The system re-learns the baseline from scratch. No stale data. No assumptions." | Servo returns to 0° |

**Key talking point:** "Most monitoring systems have three states: green, amber, red. We have four: green, amber, red, and black — where black means we don't know, and not knowing is the worst state of all."

### Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| USB cable hard to unplug smoothly | Low | Pre-loosen the USB connector. Or use a barrel jack with a quick-disconnect. |
| Pico B crashes when Pico A disconnects | Very Low | Pico B has no dependency on Pico A — it just stops receiving. Test this during setup. |
| Servo already at 180° from previous fault demo | Medium | Ensure Model D recovery completes before starting Model E. Joystick reset should bring servo to 0° first. |
| Re-learning takes too long after replug | Low | 30-second learning phase. Can pre-load fallback baseline to show 0° immediately, then refine. |

### EEE Theory Connection

**Watchdog timer principle:** In embedded systems, a watchdog timer resets the processor if the firmware fails to "kick" the timer within a deadline. The heartbeat timeout is the same principle applied to a wireless link — the receiver is the watchdog, and the transmitter must continuously prove it's alive.

**Fail-safe vs fail-secure:**
- **Fail-safe** (our approach): Loss of signal → assume worst case → flag fault. Maximizes safety.
- **Fail-secure** (alternative): Loss of signal → lock current state → prevent unauthorized changes. Used in access control, not appropriate here.

GridBox uses fail-safe because a false fault alarm (safe) is always preferable to a missed real fault (dangerous).

**Shannon's noisy channel theorem (relevance to wireless):** The nRF24L01+ operates at 2.4GHz with auto-acknowledgement. Packet loss rate depends on interference. The 2-second timeout allows ~100 missed packets before flagging offline — this provides resilience against brief RF interference without masking real failures.

### Judge Q&A

**Q: "What if the wireless link is just temporarily blocked?"**
A: "The 2-second timeout allows 100 packets to be missed. Brief interference — someone walking between the nodes, a microwave oven — recovers within 200-500ms. If we hit 2 seconds, something real has happened. And even if it's just a link issue, the operator should investigate."

**Q: "Why not just show 'NO DATA' instead of flagging it as a fault?"**
A: "Because 'NO DATA' requires the operator to decide if that's a problem. At 3am during a night shift, 'NO DATA' gets ignored. A servo at 180° with an alarm buzzer doesn't get ignored. We design for the tired operator, not the attentive one."

---

## Comparison Matrix

How each fault model affects each signature metric:

| Metric | Model A (Load) | Model B (Sag) | Model C (Intermittent) | Model D (Stall) | Model E (Offline) |
|---|---|---|---|---|---|
| `mean_current` | UP 15-40% | DOWN 10-25% | DOWN 5-15% | UP 200-500% then 0 | N/A (no data) |
| `std_current` | UP 10-20% | UP 5-15% | UP 200-500% | DOWN 80% then 0 | N/A |
| `crossing_rate` | DOWN 10-30% | DOWN 15-25% | UP 50-200% | DOWN 100% (zero) | N/A |
| `max_deviation` | UP 15-30% | DOWN 10-20% | UP 50-100% | DOWN 50% then 0 | N/A |
| **Divergence score** | **0.15–0.45** | **0.12–0.30** | **0.50–1.00** | **1.00 (saturated)** | **N/A (timeout)** |
| **Dominant metric** | d_mean | d_mean + d_crossing | d_std | d_mean (spike) | heartbeat |

**Key insight:** Each fault model has a unique signature pattern. The system doesn't just detect "something is wrong" — the pattern of which metrics changed and by how much narrows the diagnosis to a specific fault category.

---

## Recommended Demo Ordering

```
1. Model A (Load Increase)     — safe opener, guaranteed to work, establishes credibility
2. Model C (Intermittent)      — dramatic, shows the "ghost fault" detection capability
3. Model D (Stall + IMU)       — climax, sensor fusion moment, strongest technical argument
4. Model E (Offline/Fail-safe) — finale, philosophical statement, most memorable moment
```

**Why this order:**
- **Escalating severity:** mild drift → erratic jitter → full fault → complete silence
- **Escalating drama:** subtle needle → jittering needle → slamming needle → dead silence then slam
- **Escalating novelty:** standard detection → intermittent detection → sensor fusion → fail-safe philosophy

**Never open with Model D or E** — they're too dramatic. You need Model A to establish what "normal detection" looks like before showing the exceptional cases.

---

## Fallback Strategy

If a model fails during live demo:

| Failed Model | Fallback |
|---|---|
| Model A (load doesn't change signature) | Skip. Move to Model C. The load increase may be too small — adjust threshold or apply more force next time. |
| Model C (loose wire too unpredictable) | Skip. Move directly to Model D. Intermittent faults are inherently unpredictable — no shame in skipping. |
| Model D (IMU doesn't trigger) | Fall back to energy-only detection. Say: "Notice the energy signature caught the fault independently of the vibration sensor." |
| Model E (Pico A doesn't reconnect) | This is fine — the fail-safe demo only requires the disconnect. If reconnection fails, say: "In deployment, a maintenance crew would investigate the offline node." |
| All energy signature models fail | Fall back to pre-recorded replay mode. Display a pre-computed divergence score sequence on the OLED. Say: "This is recorded data from our test bench — let me walk you through the signature analysis." |

**The pre-recorded replay is the ultimate safety net.** Build it as P3 priority — it's cheap insurance.
