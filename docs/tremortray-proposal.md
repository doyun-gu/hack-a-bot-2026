# TremorTray — Hand Tremor Diagnostic Tool

> "A blood pressure monitor, but for hand stability"

**Theme:** Assistive Technology + Autonomy
**Score: 96/100** — Highest ranked idea

---

## The Problem

Neurologists diagnose tremor using the **UPDRS scale** — they watch the patient hold a cup and rate 0-4. It's completely **subjective**. Two doctors can give different scores for the same patient. There's no data, no frequency analysis, no tracking over time.

Professional tremor measurement devices (accelerometer-based clinical tools) cost **£5,000-£10,000+** and exist only in specialist labs.

**There is no cheap, objective, quantitative tremor diagnostic tool.**

We build one for **~£15** from hackathon kit parts.

---

## The Concept

Patient holds a tray. Ball sits on the tray. The device measures everything about their hand tremor and produces a clinical-grade diagnostic report on the OLED screen. A clinician's base station receives the data wirelessly for logging and comparison.

```mermaid
graph LR
    PATIENT["Patient holds tray<br/>with ball on top"] --> TRAY["TremorTray<br/>(Pico A)"]
    TRAY -->|"wireless 100Hz"| BASE["Clinician Station<br/>(Pico B)"]

    TRAY --> M1["Measures:<br/>• Tremor amplitude<br/>• Tremor frequency<br/>• Stability score<br/>• Ball position<br/>• Endurance time"]

    BASE --> M2["Displays:<br/>• Live score<br/>• History comparison<br/>• Severity level<br/>• Test difficulty<br/>• Frequency analysis"]

    style PATIENT fill:#3498db,color:#fff
    style TRAY fill:#e74c3c,color:#fff
    style BASE fill:#27ae60,color:#fff
    style M1 fill:#fff,stroke:#e74c3c
    style M2 fill:#fff,stroke:#27ae60
```

---

## Why This Scores Higher Than a Stabiliser

| | Stabiliser | TremorTray (Diagnostic) |
|---|---|---|
| Goal | Cancel tremor | **Measure and diagnose** tremor |
| Servo precision needed | Very high | Low — just calibrate + difficulty |
| Build complexity | Push rods, pivot, PID tuning | **Flat tray — much simpler** |
| Build risk | High | **Low** |
| Demo | "Spoon stays level" | **Judge gets a personal score** |
| Innovation | Gimbals exist | **No cheap diagnostic tool exists** |
| Clinical value | Helps eat | **Helps diagnose and track disease** |

---

## System Architecture

```mermaid
graph TB
    subgraph TRAY["PICO A — Diagnostic Tray (patient holds)"]
        direction TB
        IMU["BMI160 IMU<br/>Mounted on tray surface<br/>Measures tilt + rotation<br/>100Hz sampling<br/>(I2C: GP4 SDA, GP5 SCL)"]
        JOY_SENSE["Joystick (under tray)<br/>Ball position sensor<br/>Weight shift = deflection<br/>(ADC: GP26 X, GP27 Y)"]
        PCA_TRAY["PCA9685 + 2x MG90S<br/>Auto-level calibration<br/>Difficulty level tilting<br/>(I2C: same bus as IMU)"]
        NRF_A["nRF24L01+ TX<br/>Streams diagnostic data<br/>(SPI: GP2-GP6)"]
        LED_TRAY["LED Array<br/>Green = steady<br/>Yellow = mild shake<br/>Red = strong shake"]

        IMU --> NRF_A
        JOY_SENSE --> NRF_A
        PCA_TRAY --> NRF_A
    end

    subgraph LINK["2.4 GHz Wireless"]
        PACKET["Every 10ms:<br/>{ roll, pitch, gyro_rate,<br/>ball_x, ball_y, test_level,<br/>timestamp }"]
    end

    subgraph BASE["PICO B — Clinician Base Station"]
        direction TB
        NRF_B["nRF24L01+ RX<br/>Receives all data<br/>(SPI)"]
        OLED_B["OLED 0.96&quot;<br/>Diagnostic dashboard<br/>Score, frequency, history<br/>(I2C)"]
        JOY_B["Joystick<br/>Select test level<br/>Start/stop test<br/>Scroll results<br/>(ADC)"]
        LED_B["LED Array<br/>Patient status<br/>visible across room"]

        NRF_B --> OLED_B
        JOY_B --> OLED_B
        NRF_B --> LED_B
    end

    NRF_A --> PACKET --> NRF_B

    style TRAY fill:#fce4e4,stroke:#e74c3c,stroke-width:2px
    style BASE fill:#d4edda,stroke:#27ae60,stroke-width:2px
    style LINK fill:#fff3cd,stroke:#ffc107,stroke-width:2px
    style IMU fill:#9b59b6,color:#fff
    style JOY_SENSE fill:#1abc9c,color:#fff
    style PCA_TRAY fill:#e67e22,color:#fff
    style NRF_A fill:#3498db,color:#fff
    style NRF_B fill:#3498db,color:#fff
    style OLED_B fill:#1a1a2e,color:#00ff88
    style JOY_B fill:#1abc9c,color:#fff
    style LED_TRAY fill:#f39c12,color:#fff
    style LED_B fill:#e74c3c,color:#fff
```

---

## Where Each Sensor Goes (Physical Layout)

```mermaid
graph TB
    subgraph TRAY_TOP["TRAY TOP VIEW (7×9cm perfboard)"]
        direction TB
        BALL["Ball / marble<br/>sits here<br/>(centre of tray)"]
        IMU_POS["BMI160 IMU<br/>soldered to tray surface<br/>near centre"]
        EDGE_A["Servo A<br/>edge mount<br/>(roll axis)"]
        EDGE_B["Servo B<br/>edge mount<br/>(pitch axis)"]
    end

    subgraph TRAY_UNDER["UNDERNEATH THE TRAY"]
        JOY_POS["Joystick<br/>stick points UP<br/>through hole in perfboard<br/>ball weight deflects it"]
        WIRES["Wiring to breadboard below"]
    end

    subgraph BREADBOARD["BREADBOARD (below tray)"]
        PICO_A["Pico 2"]
        PCA["PCA9685"]
        NRF["nRF24L01+"]
        LEDS_POS["LEDs on edge<br/>(visible to patient)"]
    end

    TRAY_TOP --- TRAY_UNDER --- BREADBOARD

    style TRAY_TOP fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style TRAY_UNDER fill:#ecf0f1,stroke:#bdc3c7,stroke-width:2px
    style BREADBOARD fill:#3498db,color:#fff,stroke:#2980b9,stroke-width:2px
    style BALL fill:#fff,color:#333,stroke:#333
    style IMU_POS fill:#9b59b6,color:#fff
    style JOY_POS fill:#1abc9c,color:#fff
```

### IMU Mounting Detail

The BMI160 breakout board is tiny (~15×12mm). It solders directly to the perfboard tray surface, near the centre next to the joystick hole. It moves WITH the tray — so it measures exactly what the patient's hand is doing.

### Joystick Mounting Detail

The joystick stick pokes UP through a hole drilled in the perfboard. The ball sits on or near the stick tip. When the ball rolls, its weight pushes the joystick in that direction. The ADC reads the deflection as ball position.

---

## Dual Sensor System

```mermaid
graph LR
    subgraph TREMOR["Patient's Hand Tremor"]
        SHAKE["Hand shakes"]
    end

    SHAKE --> IMU_READ["IMU reads:<br/>Tilt angle (degrees)<br/>Rotation speed (deg/s)<br/>Frequency (Hz)"]
    SHAKE --> JOY_READ["Joystick reads:<br/>Ball position (X,Y)<br/>Weight shift direction<br/>Deflection magnitude"]

    IMU_READ --> COMBINE["Sensor Fusion<br/>Two independent measurements<br/>= more credible diagnosis"]
    JOY_READ --> COMBINE

    COMBINE --> METRICS["Output Metrics:<br/>• Stability Score (%)<br/>• Tremor Frequency (Hz)<br/>• Tremor Amplitude (°)<br/>• Ball Control Score (%)<br/>• Direction Bias<br/>• Endurance Time"]

    style TREMOR fill:#e74c3c,color:#fff
    style IMU_READ fill:#9b59b6,color:#fff
    style JOY_READ fill:#1abc9c,color:#fff
    style COMBINE fill:#f39c12,color:#fff
    style METRICS fill:#27ae60,color:#fff
```

**Why two sensors matter:**
- IMU alone: measures tilt but can't see the ball
- Joystick alone: measures ball position but can't measure frequency or tilt angle
- **Together:** complete picture — "tray tilted 5° right at 4.8Hz AND ball shifted 30% right"
- If both sensors agree, the measurement is more **clinically credible**

---

## Servo Difficulty Levels

```mermaid
stateDiagram-v2
    [*] --> CALIBRATE: Press joystick button

    CALIBRATE --> LEVEL1: Auto-levelled

    LEVEL1: Level 1 — FLAT
    LEVEL1: Tray is level (0° tilt)
    LEVEL1: Baseline tremor test

    LEVEL1 --> LEVEL2: Joystick right

    LEVEL2: Level 2 — MILD TILT
    LEVEL2: Servos tilt tray 3°
    LEVEL2: Moderate challenge

    LEVEL2 --> LEVEL3: Joystick right

    LEVEL3: Level 3 — STRONG TILT
    LEVEL3: Servos tilt tray 6°
    LEVEL3: Hard challenge

    LEVEL3 --> LEVEL4: Joystick right

    LEVEL4: Level 4 — DYNAMIC
    LEVEL4: Servos slowly rock tray
    LEVEL4: Tests reaction time

    LEVEL4 --> LEVEL1: Joystick right (wraps)
```

**Clinical value of levels:**
- Score drops slightly Level 1→2: **mild tremor**
- Score drops a lot Level 1→3: **moderate tremor — likely Parkinson's**
- Score drops on Level 4 only: **intention tremor — likely essential tremor or MS**

This **differentiates types of tremor** — something even expensive clinical tools don't do easily.

---

## What the OLED Shows (on Clinician Base Station)

### During Test

```mermaid
graph TD
    subgraph SCREEN_LIVE["LIVE TEST DISPLAY"]
        direction TB
        TITLE_L["TREMORTRAY  Level 2"]
        TIMER["Time: 00:18 / 00:30"]
        SCORE_LIVE["Stability: 74%"]
        FREQ_L["Frequency: 4.8 Hz"]
        AMP_L["Amplitude: 3.2°"]
        BALL_POS["Ball: 30% right"]
        BAR["[████████░░] 74%"]
    end

    style SCREEN_LIVE fill:#000,color:#0f8,stroke:#333,stroke-width:2px
```

### After Test — Results

```mermaid
graph TD
    subgraph SCREEN_RESULTS["TEST RESULTS"]
        direction TB
        TITLE_R["RESULTS — Level 2"]
        SC["Stability Score:  74%"]
        FR["Tremor Frequency: 4.8 Hz"]
        AM["Tremor Amplitude: 3.2°"]
        EN["Endurance:        28.4s"]
        BI["Direction Bias:   RIGHT"]
        SV["Severity:         MODERATE"]
        COMP["vs Level 1:       -8%"]
    end

    style SCREEN_RESULTS fill:#000,color:#0f8,stroke:#333,stroke-width:2px
```

### Severity Classification (automated)

| Score | Frequency | Classification | Likely Condition |
|---|---|---|---|
| 90-100% | Any | MINIMAL | Normal / healthy |
| 70-89% | <4 Hz | MILD | Age-related tremor |
| 70-89% | 4-6 Hz | MILD | Early Parkinson's |
| 50-69% | 4-6 Hz | MODERATE | Parkinson's disease |
| 50-69% | 8-12 Hz | MODERATE | Essential tremor |
| <50% | Any | SEVERE | Advanced condition |

---

## vs Current Clinical Methods

```mermaid
graph LR
    subgraph CURRENT["Current Method (UPDRS)"]
        DOC["Doctor watches patient"]
        SUBJ["Subjective rating 0-4"]
        NO_DATA["No data saved"]
        NO_FREQ["No frequency analysis"]
        COST_HIGH["Free but unreliable"]
    end

    subgraph PRO["Professional Lab Tool"]
        ACCEL["Clinical accelerometer"]
        OBJ["Objective measurement"]
        DATA_YES["Data recorded"]
        FREQ_YES["Frequency analysis"]
        COST_PRO["£5,000 - £10,000+"]
    end

    subgraph OURS["TremorTray"]
        DUAL["Dual sensor (IMU + joystick)"]
        OBJ2["Objective measurement"]
        DATA2["Wireless data logging"]
        FREQ2["Frequency + amplitude + score"]
        COST_US["~£15"]
        LEVELS["Multi-level difficulty testing"]
    end

    style CURRENT fill:#fff5f5,stroke:#e74c3c
    style PRO fill:#fff3cd,stroke:#ffc107
    style OURS fill:#d4edda,stroke:#27ae60
```

---

## Physical Build (Kit Only)

```mermaid
graph TD
    subgraph BUILD["Assembly — Kit Parts Only"]
        P["Perfboard 7×9cm<br/>(full size = tray surface)"]
        S1["MG90S Servo A<br/>screwed to edge"]
        S2["MG90S Servo B<br/>screwed to edge"]
        J["Joystick<br/>stick through hole<br/>in perfboard centre"]
        I["BMI160 breakout<br/>soldered near centre"]
        B["Breadboard below<br/>holds Pico + PCA9685<br/>+ nRF24L01+"]
        W["22AWG wire<br/>all connections"]
        SC["M3 screws<br/>mount servos + structure"]
    end

    style BUILD fill:#f8f9fa,stroke:#dee2e6
```

**Assembly time: ~1.5 hours**

No cutting, no push rods, no pivot joints. The perfboard IS the tray at full 7×9cm size. Components mount directly to it. Much simpler than the stabiliser.

---

## Build Timeline

```mermaid
gantt
    title TremorTray — 12 Hour Build Plan
    dateFormat HH:mm
    axisFormat %H:%M

    section Critical (wireless first)
    nRF24L01+ link between Picos        :crit, 00:00, 1h
    BMI160 IMU reading + filter          :crit, 01:00, 1h

    section Core Diagnostic
    Joystick ADC reading + calibration   :02:00, 30min
    Tremor analysis algorithm            :02:30, 1h
    Frequency detection (FFT/zero-cross) :03:30, 1h

    section Actuation
    PCA9685 + servo difficulty levels    :04:30, 1h
    Auto-calibration routine             :05:30, 30min

    section Display
    OLED live test screen                :06:00, 1h
    OLED results + severity scoring      :07:00, 1h

    section Physical Build
    Mount IMU + joystick to perfboard    :08:00, 45min
    Mount servos + wiring                :08:45, 45min

    section Polish
    Documentation + diagrams             :09:30, 1h
    Demo practice + tuning               :10:30, 1h
    Buffer time                          :11:30, 30min
```

---

## Demo Script

```mermaid
graph LR
    D1["1. CALIBRATE<br/>Press button<br/>Servos level tray<br/>OLED: Ready"] --> D2["2. PLACE BALL<br/>Ball on tray<br/>Joystick detects weight<br/>OLED: Ball detected"]
    D2 --> D3["3. JUDGE HOLDS<br/>30-second test<br/>Ball wobbles<br/>LEDs show stability"]
    D3 --> D4["4. RESULTS<br/>Score: 74%<br/>Freq: 2.1Hz<br/>Severity: MILD"]
    D4 --> D5["5. LEVEL UP<br/>Servo tilts tray 3°<br/>Repeat test<br/>Score drops to 58%"]
    D5 --> D6["6. COMPARE<br/>Base station shows<br/>both results<br/>Clinical comparison"]

    style D1 fill:#ffc107,color:#333
    style D2 fill:#17a2b8,color:#fff
    style D3 fill:#e74c3c,color:#fff
    style D4 fill:#27ae60,color:#fff
    style D5 fill:#9b59b6,color:#fff
    style D6 fill:#e67e22,color:#fff
```

**Key demo moments:**
1. Judge holds tray, gets **personal tremor score** — they become the patient
2. Two judges compete — social, memorable
3. Servo adapts difficulty in real-time — judges SEE the autonomy
4. Tremor fingerprint appears on OLED — personal, unique, beautiful
5. Condition classification — "Pattern suggests: Physiological tremor (stress)"

**Drop line:** *"A clinical tremor assessment costs £10,000. We built one for £15."*

---

## What Makes TremorTray Uncopyable

Other teams may use the same IMU. Here's why we're six layers deeper:

```mermaid
graph TD
    subgraph OTHER["What other teams build"]
        O1["IMU reads shaking → shows numbers"]
    end

    subgraph OURS["Our six layers of depth"]
        L1["Layer 1: Dual-sensor measurement<br/>IMU (tilt/frequency) + ball (visual proof)"]
        L2["Layer 2: Frequency analysis<br/>Tremor type classification via zero-crossing"]
        L3["Layer 3: Adaptive servo difficulty<br/>Real-time autonomous adjustment during test"]
        L4["Layer 4: Gamified scoring<br/>Points, streaks, stars, competition mode"]
        L5["Layer 5: Tremor fingerprint<br/>Polar pattern unique to each person"]
        L6["Layer 6: Biofeedback therapy<br/>Servo nudges teach patient self-correction"]

        L1 --> L2 --> L3 --> L4 --> L5 --> L6
    end

    OTHER -.->|"They stop here"| L1

    style OTHER fill:#ffcccc,stroke:#e74c3c,stroke-width:2px
    style OURS fill:#d4edda,stroke:#27ae60,stroke-width:2px
    style L1 fill:#3498db,color:#fff
    style L2 fill:#2980b9,color:#fff
    style L3 fill:#9b59b6,color:#fff
    style L4 fill:#e67e22,color:#fff
    style L5 fill:#e74c3c,color:#fff
    style L6 fill:#c0392b,color:#fff
```

---

## Feature 1: Tremor Fingerprint (Visual Signature)

Every person's tremor produces a unique pattern — like a fingerprint. We plot roll (X) vs pitch (Y) over time on the OLED as a **polar/Lissajous pattern:**

```mermaid
graph LR
    subgraph HEALTHY["Healthy Hands"]
        H["Tight central dot<br/>Minimal movement<br/>No visible pattern"]
    end

    subgraph PARK["Parkinson's (4-6Hz)"]
        P["Slow wide loops<br/>Circular/elliptical<br/>Consistent rhythm"]
    end

    subgraph ESSENTIAL["Essential Tremor (8-12Hz)"]
        E["Tight fast oscillation<br/>Linear back-and-forth<br/>Along one axis mainly"]
    end

    subgraph STRESS["Stress/Caffeine"]
        S["Small jittery cloud<br/>No clear pattern<br/>Random directions"]
    end

    style HEALTHY fill:#27ae60,color:#fff
    style PARK fill:#e74c3c,color:#fff
    style ESSENTIAL fill:#e67e22,color:#fff
    style STRESS fill:#3498db,color:#fff
```

**Implementation:** Store last 200 IMU readings. Plot roll on X-axis, pitch on Y-axis. Each dot is one reading. The shape that forms IS the fingerprint.

**Why judges love it:** They see THEIR OWN pattern on screen. Personal. Visual. They'll talk about it after.

---

## Feature 2: Gamified Scoring

Instead of a boring clinical test, the patient plays a **game:**

```mermaid
flowchart TD
    START["TEST BEGINS<br/>OLED: 'Hold steady...'"] --> STABLE{"Tray within ±2°?"}

    STABLE -->|"Yes — stable"| POINTS["Award points<br/>+10 pts/second<br/>Streak counter: +1s<br/>LED: GREEN"]
    STABLE -->|"No — shaking"| PENALTY["Deduct points<br/>-5 pts/second<br/>Streak resets to 0<br/>LED: RED"]

    POINTS --> COMBO{"Streak > 5s?"}
    COMBO -->|"Yes"| BONUS["COMBO BONUS<br/>Points × 2 multiplier<br/>OLED: 'COMBO!'"]
    COMBO -->|"No"| CONTINUE["Continue test"]
    BONUS --> CONTINUE
    PENALTY --> CONTINUE

    CONTINUE --> TIME{"30 seconds done?"}
    TIME -->|"No"| STABLE
    TIME -->|"Yes"| RESULTS["FINAL RESULTS<br/>Total points: 1,247<br/>Longest streak: 8.1s<br/>Stars: ★★★☆☆<br/>Frequency: 4.8Hz"]

    RESULTS --> COMPARE["COMPARE MODE<br/>'Challenge a friend!'<br/>Second person takes test<br/>Side-by-side scores"]

    style START fill:#ffc107,color:#333
    style POINTS fill:#27ae60,color:#fff
    style PENALTY fill:#e74c3c,color:#fff
    style BONUS fill:#f39c12,color:#fff
    style RESULTS fill:#3498db,color:#fff
    style COMPARE fill:#9b59b6,color:#fff
```

**Star Rating System:**

| Stars | Score Range | Meaning |
|---|---|---|
| ★★★★★ | 90-100% | Excellent stability |
| ★★★★☆ | 75-89% | Good — minor tremor |
| ★★★☆☆ | 60-74% | Moderate — noticeable tremor |
| ★★☆☆☆ | 40-59% | Significant tremor |
| ★☆☆☆☆ | <40% | Severe — seek consultation |

---

## Feature 3: Adaptive Real-Time Difficulty

Servos don't just set a fixed difficulty — they **continuously adapt during the test:**

```mermaid
flowchart TD
    BEGIN["Test begins — tray flat (0°)"] --> SAMPLE["Measure stability<br/>for 3-second window"]

    SAMPLE --> EVAL{"Average stability<br/>in last 3 seconds?"}

    EVAL -->|"> 85% stable"| HARDER["INCREASE DIFFICULTY<br/>Servo tilts +1° more<br/>OLED: 'Getting harder...'"]
    EVAL -->|"60-85% stable"| HOLD["HOLD CURRENT LEVEL<br/>Patient at their limit<br/>OLED: 'Hold steady...'"]
    EVAL -->|"< 60% stable"| EASIER["DECREASE DIFFICULTY<br/>Servo eases back 1°<br/>OLED: 'Take it easy...'"]

    HARDER --> SAMPLE
    HOLD --> SAMPLE
    EASIER --> SAMPLE

    HARDER --> MAX{"Max tilt 8°?"}
    MAX -->|"Yes"| CAP["Stay at max<br/>Record: 'Patient stable<br/>up to 8° tilt'"]
    MAX -->|"No"| SAMPLE

    style BEGIN fill:#27ae60,color:#fff
    style EVAL fill:#f39c12,color:#fff
    style HARDER fill:#e74c3c,color:#fff
    style HOLD fill:#3498db,color:#fff
    style EASIER fill:#27ae60,color:#fff
    style CAP fill:#9b59b6,color:#fff
```

**Clinical value:** The device automatically finds the patient's **breaking point** — the exact difficulty level where their stability drops below 60%. This number IS the diagnosis.

- Breaking point at 6°: mild tremor
- Breaking point at 3°: moderate tremor
- Breaking point at 0° (can't even hold flat): severe tremor

**Why judges are impressed:** They SEE the servos adjusting during the test. The device is making autonomous decisions. That's real autonomy, not scripted behaviour.

---

## Feature 4: Condition Classification

Frequency analysis identifies tremor TYPE, not just severity:

```mermaid
flowchart LR
    FREQ["Measure tremor<br/>frequency via<br/>zero-crossing method"] --> CLASSIFY{"Dominant<br/>frequency?"}

    CLASSIFY -->|"3-5 Hz"| PARK["Parkinson's Pattern<br/>Slow, rhythmic<br/>Present at rest<br/>Reduces with movement"]
    CLASSIFY -->|"5-8 Hz"| ESSENTIAL["Essential Tremor<br/>Medium frequency<br/>Appears during action<br/>Worsens with intention"]
    CLASSIFY -->|"8-12 Hz"| PHYSIO["Physiological Tremor<br/>Fast, fine<br/>Normal / stress / caffeine<br/>Not pathological"]
    CLASSIFY -->|"Irregular"| CEREBELLAR["Cerebellar Pattern<br/>No consistent frequency<br/>Irregular, jerky<br/>Possible neurological issue"]

    PARK --> DISPLAY["OLED displays:<br/>'Pattern suggests:<br/>[condition name]<br/>Frequency: X.X Hz<br/>Consult neurologist'"]
    ESSENTIAL --> DISPLAY
    PHYSIO --> DISPLAY
    CEREBELLAR --> DISPLAY

    style FREQ fill:#3498db,color:#fff
    style CLASSIFY fill:#f39c12,color:#fff
    style PARK fill:#e74c3c,color:#fff
    style ESSENTIAL fill:#e67e22,color:#fff
    style PHYSIO fill:#27ae60,color:#fff
    style CEREBELLAR fill:#9b59b6,color:#fff
    style DISPLAY fill:#1a1a2e,color:#0f8
```

**Implementation:** Count zero-crossings per second on the roll axis. Dominant frequency = crossings ÷ 2. Simple, no FFT needed, runs on Pico easily.

**Disclaimer on OLED:** "This is a screening tool, not a diagnosis. Consult a healthcare professional."

---

## Feature 5: Biofeedback Therapy Mode (Stretch Goal)

The servos don't just test — they **teach the patient to control their tremor:**

```mermaid
sequenceDiagram
    participant P as Patient's Hand
    participant IMU as BMI160 IMU
    participant PID as PID Controller
    participant S as Servos

    Note over P,S: Biofeedback Loop (every 10ms)

    P->>IMU: Hand trembles RIGHT (+4°)
    IMU->>PID: Roll = +4°
    PID->>S: Counter-nudge LEFT (-2°)
    Note over S: Gentle nudge — only 50% compensation
    S->>P: Patient FEELS the nudge
    P->>P: Unconsciously corrects toward centre

    Note over P,S: Over 30 seconds, nudge strength decreases

    P->>IMU: Hand trembles RIGHT (+4°)
    IMU->>PID: Roll = +4°
    PID->>S: Counter-nudge LEFT (-1°)
    Note over S: Weaker nudge — patient learns to self-correct
    S->>P: Subtler feedback
    P->>P: Self-corrects faster

    Note over P,S: Eventually nudges reach 0% — patient is self-stabilising
```

**Key insight:** The servo provides PARTIAL compensation (not full). The patient's brain learns to provide the rest. Over time, nudge strength decreases — the patient is training their own motor control.

**Clinical basis:** This is how real biofeedback therapy works. Providing partial feedback that fades over time is a proven rehabilitation technique.

**Build priority:** Stretch goal — only if core features are done by hour 10.

---

## Ball on Tray — Visual Aid Design

The ball is **visual proof**, not an electronic sensor target:

```mermaid
graph TD
    subgraph DESIGN["Ball + Tray Design"]
        TRAY_SURFACE["Perfboard 7×9cm<br/>Full size — no cutting"]
        BUMPER["Wire bumper around edge<br/>Bent 22AWG wire<br/>Prevents ball rolling off<br/>~5mm height"]
        BALL_CHOICE["Ball choice:<br/>• Glass marble (~5g) — best visual<br/>• Steel ball bearing (~30g) — most movement<br/>• Rubber ball (~15g) — won't roll off table if dropped"]
        IMU_REAL["IMU measures the TRAY tilt<br/>Ball movement = visual confirmation<br/>Both show the same thing:<br/>physics guarantees it"]
    end

    style DESIGN fill:#f8f9fa,stroke:#dee2e6,stroke-width:2px
    style BUMPER fill:#f39c12,color:#fff
    style BALL_CHOICE fill:#3498db,color:#fff
    style IMU_REAL fill:#9b59b6,color:#fff
```

**Recommendation:** Glass marble — visually clear, judges can see it rolling from across the room.

---

## Complete OLED Screen Flow

```mermaid
stateDiagram-v2
    [*] --> IDLE: Power on

    IDLE: IDLE SCREEN
    IDLE: "TremorTray v1.0"
    IDLE: "Press to start"
    IDLE: Wireless: Connected

    IDLE --> CALIBRATING: Joystick button press

    CALIBRATING: CALIBRATING
    CALIBRATING: "Hold still..."
    CALIBRATING: Servos auto-level
    CALIBRATING: Sets zero reference

    CALIBRATING --> READY: 3 seconds

    READY: READY
    READY: "Place ball on tray"
    READY: "Hold tray level"
    READY: "Press to begin test"

    READY --> TESTING: Joystick button press

    TESTING: LIVE TEST
    TESTING: Score, streak, points
    TESTING: Star rating building
    TESTING: Servo adapting difficulty
    TESTING: 30 second countdown

    TESTING --> RESULTS: Timer ends

    RESULTS: RESULTS SCREEN
    RESULTS: Total score + stars
    RESULTS: Frequency + amplitude
    RESULTS: Condition suggestion
    RESULTS: Breaking point level
    RESULTS: "Press for fingerprint"

    RESULTS --> FINGERPRINT: Joystick button press

    FINGERPRINT: TREMOR FINGERPRINT
    FINGERPRINT: Polar plot of tremor
    FINGERPRINT: Unique visual pattern
    FINGERPRINT: "Press to restart"

    FINGERPRINT --> READY: Joystick button press

    RESULTS --> COMPARE: Joystick left/right

    COMPARE: COMPARE MODE
    COMPARE: "Challenge a friend!"
    COMPARE: Side-by-side scores
    COMPARE: Who has steadier hands?
```

---

## Build Priority Table

| Priority | Feature | Hours | Builds On |
|---|---|---|---|
| **P0 — Must** | nRF24L01+ wireless link | 1h | Nothing |
| **P0 — Must** | BMI160 IMU read + complementary filter | 1h | Wireless |
| **P0 — Must** | PCA9685 servo control + auto-calibration | 1h | IMU |
| **P0 — Must** | Basic stability score on OLED | 1h | IMU + Servo |
| **P1 — Core** | Frequency detection (zero-crossing) | 1h | IMU |
| **P1 — Core** | Adaptive servo difficulty | 1h | Servo + Score |
| **P1 — Core** | Gamified scoring (points, streaks, stars) | 1h | Score |
| **P2 — Wow** | Tremor fingerprint polar plot | 1h | IMU data |
| **P2 — Wow** | Condition classification | 30min | Frequency |
| **P2 — Wow** | Compare / competition mode | 30min | Scoring |
| **P3 — Stretch** | Biofeedback therapy mode | 1h | Servo + IMU |
| **Always** | Physical assembly | 1.5h | Parallel |
| **Always** | Documentation + diagrams | 1h | End |

**Critical path: P0 features done by hour 4.** Everything after is additive — each feature makes it better, but the core works without them.

---

## Scoring Breakdown (Updated)

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **29** | UPDRS is subjective. 10M+ need objective measurement. No cheap tool exists. Bridges clinical gap between £0 (subjective) and £10K (lab equipment) |
| **Live Demo (25)** | **25** | Judge holds tray, gets personal score AND tremor fingerprint. Two judges compete. Servo adapts in real-time. Most interactive demo possible |
| **Technical (20)** | **19** | 6-layer depth: dual sensor, frequency analysis, adaptive PID, gamification engine, polar plot rendering, biofeedback loop. Dual-core Pico (measurement + wireless) |
| **Innovation (15)** | **15** | Tremor fingerprinting: new. Gamified clinical tool: new. Adaptive servo difficulty: new. Condition classification on a Pico: new. No other team builds this |
| **Docs (10)** | **9** | Mermaid architecture, clinical comparison, algorithm docs, state machine, build timeline |
| **Total** | **97** | |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Frequency detection inaccurate | Zero-crossing is simple but works for 3-12Hz range. Validate against known frequency (tap tray at 4Hz, check reading) |
| Ball rolls off during demo | Wire bumper around edge. Practice the demo. Use a marble that fits snugly |
| Judges say "just a phone app" | Phone can't tilt itself (no servos for difficulty levels). Phone can't do biofeedback. Phone doesn't have a ball. Our dual-sensor gives richer data |
| Too many features, nothing works | P0 features are standalone — basic score works without gamification, fingerprint, etc. Each layer is additive |
| Condition classification is "not medical" | Disclaimer: "Screening tool — consult healthcare professional." Frame as awareness, not diagnosis |
| Servo adaptation looks random | Explain the logic clearly in demo. Show the OLED feedback: "Difficulty: increasing..." so judges understand it's intentional |

---

## Future Vision (Tell Judges)

> "Today it's a hackathon prototype on a perfboard. Tomorrow it's a £20 device in every GP clinic, care home, and physiotherapy practice.
>
> Patients take a 30-second test at every visit. Their tremor fingerprint is stored. Doctors see a graph: 'Your tremor has improved 15% since starting medication.' For the first time, treatment effectiveness is measured objectively — not guessed at.
>
> There are 10 million people with Parkinson's. There are 7 million with essential tremor. Today, their doctor watches them hold a cup and says 'looks about the same.' We replace that with a number, a frequency, a pattern, and a trend.
>
> And it all started with a perfboard, two servos, and an IMU."
