# Energy Signature Anomaly Detection — Refined Proposal

## Context

This refines the original NILM-based fault detection extension for GridBox (Hack-A-Bot 2026, 24-hour hackathon). The refinements address six issues from review: long learning time, MicroPython sampling limits, missing peak detection, arbitrary weights, artificial fault simulation, and unprovable "hours of warning" claim.

The goal: select **practical fault models** that produce real, measurable signature changes on cheap DC motors, and restructure the demo to be bulletproof in 5 minutes.

---

## Refined Design

### 1. Shortened Learning Phase (30s, not 2 min)

**Problem:** 2 minutes of "LEARNING..." is dead time in a 5-minute demo.

**Fix:** Reduce baseline window to 30 seconds (30,000 samples at 1kHz). For a DC motor with a ~50Hz electrical period, 30s captures ~1500 cycles — statistically sufficient for mean, std, and peak interval. Pre-load a known-good baseline at boot as fallback.

```python
LEARNING_DURATION_MS = 30_000  # 30 seconds, not 120
FALLBACK_BASELINE = EnergySignature(mean=0.42, std=0.03, period=20.1, amplitude=0.58)
```

**Demo flow:** Start learning before judges arrive. By the time they're listening, the needle is already at 0° (healthy).

---

### 2. Simplified Signal Processing (no `find_peaks`)

**Problem:** No scipy on Pico. Complex peak detection is bug-prone under time pressure.

**Fix:** Replace `find_peaks` with a **zero-crossing counter** — count how many times the signal crosses the mean per window. This gives frequency information without needing derivative-based peak finding.

```python
def zero_crossings(samples, mean_val):
    count = 0
    above = samples[0] > mean_val
    for s in samples[1:]:
        now_above = s > mean_val
        if now_above != above:
            count += 1
            above = now_above
    return count
```

**Replaces:** `pulse_period` and `pulse_amplitude` with `crossing_rate` and `max_deviation`. Same physical information, trivial to implement.

Revised `EnergySignature`:
```python
class EnergySignature:
    def __init__(self):
        self.mean_current = 0.0      # average draw (mA)
        self.std_current = 0.0       # variability
        self.crossing_rate = 0.0     # zero-crossings per window
        self.max_deviation = 0.0     # peak distance from mean
```

---

### 3. Realistic Sampling Rate

**Problem:** MicroPython ADC at 1kHz with processing overhead may bottleneck.

**Fix:** Target **500Hz** (2ms per sample). This is comfortably achievable in MicroPython on RP2350's Core 1 with `machine.ADC.read_u16()`. A 1-second window = 500 samples — still sufficient for DC motor characterization (electrical frequencies < 100Hz).

```python
SAMPLE_RATE_HZ = 500
WINDOW_SIZE = 500  # 1 second of data
DUTY_CYCLE = 0.10  # 100ms sample, 900ms sleep → ~2mW
```

---

### 4. Factory Fault Models — What to Actually Demonstrate

This is the critical selection. Each model must produce a **measurable, repeatable** current signature change on the actual hardware.

#### Model A: Mechanical Load Increase (RECOMMENDED — Primary Demo)
- **Physical setup:** Attach a foam pad or rubber band to the conveyor motor shaft. During demo, press a finger or object against the conveyor belt to increase friction.
- **Signature change:** Mean current rises 15-40%, std increases, crossing rate drops (motor slows under load).
- **Why it works:** This is the real-world analogue of a blocked conveyor, seized bearing, or product jam. The current draw change is large and immediate.
- **Demo reliability:** 10/10 — guaranteed to produce a measurable signal every time.
- **Physical cause mapping:** Blockage / mechanical resistance → mean current ↑, crossing rate ↓

#### Model B: Voltage Sag Simulation (RECOMMENDED — Secondary Demo)
- **Physical setup:** Use the potentiometer (already wired to ADC) to adjust the buck-boost converter output voltage down by 1-2V during the demo.
- **Signature change:** Mean current drops, max deviation changes, crossing rate shifts as motor speed changes.
- **Why it works:** Simulates brownout / degraded power supply — a real factory failure mode. The potentiometer gives smooth, controllable degradation.
- **Demo reliability:** 9/10 — depends on buck-boost having accessible adjustment.
- **Physical cause mapping:** Power supply degradation → mean current ↓, std ↑

#### Model C: Intermittent Connection (RECOMMENDED — Dramatic Demo)
- **Physical setup:** Use a loose jumper wire on the motor power path. Wiggle it during demo to create intermittent contact.
- **Signature change:** Std current spikes dramatically. Mean may stay similar but variance explodes. Crossing rate becomes erratic.
- **Why it works:** This is the most visually dramatic — the needle jitters then swings to fault. Simulates a real loose connection or corroded terminal.
- **Demo reliability:** 7/10 — less controllable, but very convincing when it works.
- **Physical cause mapping:** Loose connection → std ↑↑, crossing rate erratic

#### Model D: Motor Stall / Stop (Already Implemented — IMU shake)
- **Physical setup:** Physically hold the motor shaft or shake the motor (existing demo step).
- **Signature change:** Current spikes to stall current (2-5x normal), then drops to zero if motor stops.
- **Why it works:** Validates the energy signature system against the existing IMU fault detection — both should trigger simultaneously (sensor fusion argument).
- **Demo reliability:** 10/10 — already proven in existing demo.
- **Physical cause mapping:** Stall / seizure → current spike then dropout

#### Models NOT Recommended

| Model | Why Skip |
|---|---|
| Software PWM reduction | You're detecting your own input — not a real fault. Judges will notice. |
| Temperature drift | Too slow for demo, requires heating element |
| Capacitor aging | Unmeasurable in real-time on this hardware |
| Harmonic analysis (FFT) | Too computationally expensive for MicroPython, marginal demo value |

---

### 5. Revised Divergence Score

Weights justified by which fault models produce which signature changes:

```python
def divergence_score(baseline, current):
    d_mean     = abs(current.mean_current  - baseline.mean_current) / max(baseline.mean_current, 0.001)
    d_std      = abs(current.std_current   - baseline.std_current)  / max(baseline.std_current, 0.001)
    d_crossing = abs(current.crossing_rate - baseline.crossing_rate) / max(baseline.crossing_rate, 0.001)
    d_maxdev   = abs(current.max_deviation - baseline.max_deviation) / max(baseline.max_deviation, 0.001)

    # Weights: mean current shift is the strongest general indicator
    # std spike catches intermittent faults specifically
    score = (0.30 * d_mean +
             0.25 * d_std +
             0.25 * d_crossing +
             0.20 * d_maxdev)

    return min(score, 1.0)
```

**Weight justification (for judges):**
- Mean current (0.30): Most reliable indicator across all fault types — load increase, stall, and power sag all shift the mean
- Std current (0.25): Catches intermittent faults that don't change the mean — the "canary" metric
- Crossing rate (0.25): Frequency proxy — bearing wear and mechanical degradation change motor rhythm
- Max deviation (0.20): Amplitude envelope — catches blockages and resistance changes

Normalization is now relative (percentage change from baseline), not absolute — works regardless of motor size.

---

### 6. Revised Demo Script (5 minutes)

| Time | Action | What Judges See | Fault Model |
|---|---|---|---|
| 0:00 | System boots (pre-learned baseline) | Servo at 0°, OLED: "HEALTHY — 0.03" | — |
| 0:30 | Normal operation tour | Motors running, servos cycling, wireless active | — |
| 1:00 | Press finger on conveyor belt | Needle drifts to ~40° over 5s. OLED: "DRIFT — 0.22" | **Model A** |
| 1:15 | Release belt | Needle returns to 0° over 10s. OLED: "RECOVERING" | — |
| 1:45 | Wiggle loose wire | Needle jitters wildly, swings to ~110°. OLED: "PRE-FAULT" | **Model C** |
| 2:00 | Reconnect wire | Needle stabilizes back to 0° | — |
| 2:30 | Shake motor (existing demo) | IMU + energy signature both trigger. Needle to 150°. OLED: "FAULT — DUAL CONFIRM" | **Model D** |
| 3:00 | Unplug Pico A | Pico B heartbeat timeout → servo slams to 180°. OLED: "NODE OFFLINE" | Fail-safe |
| 3:15 | Replug Pico A | Re-learns baseline, needle returns to 0° | — |
| 3:30 | Show savings + summary | OLED: final statistics, energy saved | — |

**Key moment (2:30):** Both IMU vibration AND energy signature trigger simultaneously — this is the sensor fusion argument. "Two independent detection methods confirming the same fault. No false positives."

---

### 7. Defensive Answers for Judges

| Question | Answer |
|---|---|
| "Why those weights?" | "Mean current is the strongest general indicator — it shifts in 3 of 4 fault types. Std catches the intermittent faults that mean misses." |
| "Can you prove hours of warning?" | "We can't in a 5-minute demo. What we show is the mechanism — continuous scoring, smooth degradation. In deployment, this drift is visible hours before failure. Here we compress the timeline." |
| "How is this different from a threshold alarm?" | "A threshold alarm has two states: OK and FAULT. Our system has infinite states between 0 and 1. The amber zone — 0.15 to 0.70 — is the innovation. That's where maintenance gets scheduled." |
| "What if the baseline is wrong?" | "The system re-learns on every boot. If the baseline is bad, the operator sees a permanently drifting needle and triggers re-learning via joystick." |

---

### 8. Implementation Priority (for 24-hour hackathon)

| Priority | Task | Time Est | Risk |
|---|---|---|---|
| P0 | ADC sampling loop on Core 1 (500Hz, 1s windows) | 2h | Low |
| P0 | EnergySignature class (mean, std, crossing_rate, max_dev) | 1h | Low |
| P0 | Divergence score + servo mapping on Pico B | 1h | Low |
| P0 | Heartbeat timeout fail-safe | 30min | Low |
| P1 | Model A fault demo (press conveyor) — test + tune thresholds | 1h | Medium |
| P1 | Wireless packet extension (add score + features to protocol) | 1h | Low |
| P2 | Model C fault demo (loose wire) | 30min | Medium |
| P2 | Model D cross-validation with IMU | 1h | Medium |
| P3 | OLED health history graph | 1h | Low |
| P3 | Pre-recorded replay mode (fallback if live demo fails) | 1h | Low |

**Total: ~10 hours.** Fits within a 24-hour hackathon alongside other GridBox work.

---

### 9. One-Paragraph Refined Pitch

"Every factory machine draws current in a pattern as unique as a heartbeat. GridBox learns that heartbeat in thirty seconds, then watches it — not for failure, but for the drift that comes before. Press the conveyor and the needle moves. Wiggle a wire and it spikes. Shake the motor and both vibration and energy signature confirm the fault independently. Unplug the sensor and silence itself triggers the alarm. Same ADC pins. Same £15. No extra sensors. The machine powers its own health monitor from waste energy — and when that energy stops, the silence is the diagnosis."

---

## Next Step: Detailed Fault Models Document

**Task:** Create a standalone markdown file with deep technical detail for each of the 4 fault models (A–D) plus the fail-safe model.

**Output file:** `docs/fault-models.md` (in the working directory, user copies to their repo)

**Structure per model:**
1. Model name, ID, and classification (recommended/optional/existing)
2. Real-world industrial scenario it simulates
3. Physical setup — exact hardware steps with pin references from GridBox architecture
4. Expected signature changes — quantitative estimates for each of the 4 metrics
5. Detection logic — which divergence score components trigger and why
6. Servo response — expected angle range and OLED display text
7. Demo choreography — what the presenter does and says, timing
8. Risk assessment — what could go wrong and mitigations
9. EEE theory connection — relevant equations and principles
10. Judge Q&A — anticipated questions specific to this model

**Also includes:**
- Comparison matrix (all models vs all 4 signature metrics)
- Recommended demo ordering with rationale
- Fallback strategy if a model fails during live demo
