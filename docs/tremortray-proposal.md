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

**Key moment:** Judge holds the tray and gets **their own tremor score.** They become the patient. They'll never forget that.

**Drop line:** *"A clinical tremor assessment costs £10,000. We built one for £15."*

---

## Scoring Breakdown

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **29** | UPDRS is subjective. 10M+ need objective measurement. No cheap tool exists. Real clinical gap |
| **Live Demo (25)** | **25** | Judge holds tray, gets personal score. Best possible demo — interactive, personal, memorable |
| **Technical (20)** | **18** | Dual sensor fusion, frequency analysis, 100Hz IMU, servo difficulty levels, wireless streaming, severity classification |
| **Innovation (15)** | **15** | No consumer tremor diagnostic exists. Joystick-as-position-sensor is novel. Multi-level assessment is new |
| **Docs (10)** | **9** | Mermaid diagrams, clinical comparison, UPDRS replacement narrative |
| **Total** | **96** | |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Joystick sensitivity too low for small ball movements | Use a heavier ball (marble). Calibrate ADC range at startup |
| Frequency detection is complex (FFT) | Use zero-crossing method instead — count how many times tilt crosses 0° per second. Much simpler, accurate enough |
| "How is this different from just a phone app?" | Phone lies flat — can't measure ball control. Our dual-sensor approach (IMU + joystick) gives position AND tilt. Plus servo difficulty levels — phone can't tilt itself |
| Judges don't understand clinical value | Lead with the demo (they try it). The score makes it personal. THEN explain UPDRS replacement |
| Ball rolls off tray | Add small wire bumper around edge (bent 22AWG). Or use a lip made from perfboard strips |

---

## Future Vision (Tell Judges)

> "Today it's a hackathon prototype. Tomorrow it's a £20 device that every GP clinic and care home has in their drawer. Patients do a 30-second test at every visit. Doctors track tremor progression over months on a graph. Medication effectiveness is measured objectively for the first time. And it all started with a perfboard, two servos, and an IMU."
