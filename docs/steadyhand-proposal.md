# SteadyHand — Tremor-Stabilising Assistive Device

> "Noise-cancelling headphones for physical movement"

**Theme:** Assistive Technology + Autonomy (semi-autonomous)
**Score: 95/100** — Highest ranked idea

---

## The Problem

| Stat | Detail |
|---|---|
| **10 million+** | people worldwide live with Parkinson's disease |
| **7 million** | in the US alone have essential tremor |
| **25%** | of adults over 65 have age-related tremor |
| **25-50%** | of stroke survivors develop upper limb tremor |
| **£200+** | cost of Liftware Steady (Google's stabilising spoon) |
| **~£15** | estimated cost of SteadyHand from our kit |

People with tremor can't eat independently, can't carry a cup of water, can't hold a phone steady. It strips dignity from daily life. Existing solutions are expensive or don't exist.

---

## System Architecture

```mermaid
graph LR
    subgraph PICO_A["PICO A — Wearable Sensor (wrist)"]
        IMU["BMI160 IMU<br/>6-axis | 100Hz<br/>(I2C: SDA/SCL)"]
        JOY["Joystick<br/>Mode select / Sensitivity<br/>(ADC: GP26, GP27)"]
        NRF_TX["nRF24L01+ TX<br/>Streams orientation<br/>(SPI: MOSI/MISO/SCK)"]
        LED_A["Status LED<br/>Green=OK Red=Fall<br/>(GPIO)"]
        FALL["Fall Detection<br/>Runs on Core 1<br/>Freefall→Impact→Immobility"]

        IMU --> NRF_TX
        IMU --> FALL
        JOY --> NRF_TX
        FALL --> NRF_TX
        FALL --> LED_A
    end

    subgraph WIRELESS["2.4 GHz Wireless Link"]
        PACKET["Packet every 10ms<br/>{ roll, pitch, tremor_amp,<br/>mode, fall_alert }"]
    end

    subgraph PICO_B["PICO B — Stabilised Platform (handheld)"]
        NRF_RX["nRF24L01+ RX<br/>Receives data + RSSI<br/>(SPI)"]
        PID["PID Controller<br/>error = 0° - tilt<br/>correction = Kp·e + Kd·de/dt"]
        PCA["PCA9685 Servo Driver<br/>16-ch PWM | I2C"]
        SERVO_A["MG90S Servo A<br/>Roll compensation"]
        SERVO_B["MG90S Servo B<br/>Pitch compensation"]
        OLED["OLED 0.96&quot;<br/>Health dashboard<br/>4 display modes<br/>(I2C)"]
        LEDS["LED Array<br/>Green/Yellow/Red<br/>Stability indicator"]

        NRF_RX --> PID
        PID --> PCA
        PCA --> SERVO_A
        PCA --> SERVO_B
        NRF_RX --> OLED
        PID --> LEDS
    end

    NRF_TX -->|"~2ms latency"| PACKET
    PACKET -->|"~2ms latency"| NRF_RX

    style PICO_A fill:#e8f4fd,stroke:#2471a3,stroke-width:2px
    style PICO_B fill:#fef9e7,stroke:#d4ac0d,stroke-width:2px
    style WIRELESS fill:#fff3cd,stroke:#ffc107,stroke-width:2px
    style IMU fill:#9b59b6,color:#fff
    style NRF_TX fill:#3498db,color:#fff
    style NRF_RX fill:#3498db,color:#fff
    style PCA fill:#e67e22,color:#fff
    style SERVO_A fill:#e74c3c,color:#fff
    style SERVO_B fill:#e74c3c,color:#fff
    style OLED fill:#1a1a2e,color:#00ff88
    style FALL fill:#c0392b,color:#fff
    style PID fill:#27ae60,color:#fff
    style JOY fill:#1abc9c,color:#fff
    style LED_A fill:#f39c12,color:#fff
    style LEDS fill:#e74c3c,color:#fff
    style PACKET fill:#fff3cd,color:#856404
```

---

## Control Loop

```mermaid
flowchart LR
    START([Every 10ms — 100Hz loop]) --> READ_IMU[Read BMI160<br/>accel_x, accel_y, accel_z<br/>gyro_x, gyro_y, gyro_z]
    READ_IMU --> FILTER[Complementary Filter<br/>roll = 0.98 × prev_roll + gyro × dt + 0.02 × accel_roll<br/>pitch = same for pitch axis]
    FILTER --> CHECK_MODE{Which mode?}

    CHECK_MODE -->|Mode 1: Stabiliser| PID_CALC[PID Controller<br/>error = 0° - measured_angle<br/>P = Kp × error<br/>D = Kd × error_change / dt<br/>correction = P + D]
    PID_CALC --> SERVO_CMD[Send to PCA9685 via I2C<br/>servo_angle = 90° + correction<br/>Servo A = roll correction<br/>Servo B = pitch correction]
    SERVO_CMD --> TX[Transmit via nRF24L01+<br/>roll, pitch, tremor_amp, mode]

    CHECK_MODE -->|Mode 2: Rehab Trainer| NO_SERVO[Servos stay at 90° neutral<br/>No compensation]
    NO_SERVO --> SCORE[Calculate steadiness score<br/>score = % time within ±2°]
    SCORE --> TX

    TX --> UPDATE_OLED[Update OLED<br/>every 100ms]
    UPDATE_OLED --> START

    style START fill:#2ecc71,color:#fff
    style READ_IMU fill:#9b59b6,color:#fff
    style FILTER fill:#8e44ad,color:#fff
    style CHECK_MODE fill:#f39c12,color:#fff
    style PID_CALC fill:#27ae60,color:#fff
    style SERVO_CMD fill:#e67e22,color:#fff
    style NO_SERVO fill:#3498db,color:#fff
    style SCORE fill:#3498db,color:#fff
    style TX fill:#3498db,color:#fff
    style UPDATE_OLED fill:#1a1a2e,color:#00ff88
```

**Total latency: ~4ms** — IMU read (1ms) + Filter (0.1ms) + Wireless (2ms) + PID (0.1ms) + Servo (0.5ms)

---

## Fall Detection (Parallel on Core 1)

```mermaid
stateDiagram-v2
    [*] --> MONITORING: IMU sampling at 100Hz

    MONITORING --> FREEFALL: accel magnitude ≈ 0g<br/>(all axes near zero)
    FREEFALL --> MONITORING: timeout 0.5s<br/>(not a real fall)

    FREEFALL --> IMPACT: accel spike > 3g<br/>(hit the ground)
    IMPACT --> MONITORING: movement resumes<br/>(stumble, not fall)

    IMPACT --> IMMOBILE: no movement<br/>for 10 seconds

    IMMOBILE --> ALERT_SENT: Send SOS via wireless<br/>LED turns RED
    ALERT_SENT --> CANCELLED: Joystick pressed<br/>within 15 seconds<br/>"I'm OK"
    ALERT_SENT --> CONFIRMED_FALL: No cancel after 15s<br/>Base station alarm activates

    CANCELLED --> MONITORING: Resume normal operation
    CONFIRMED_FALL --> MONITORING: Manually reset
```

---

## Two Modes — Same Hardware

```mermaid
graph LR
    subgraph MODE1["Mode 1: STABILISER"]
        direction TB
        S1["Servos ACTIVE"]
        S2["Cancel tremor"]
        S3["Spoon/cup stays level"]
        S4["Daily life use"]
        S1 --> S2 --> S3 --> S4
    end

    subgraph MODE2["Mode 2: REHAB TRAINER"]
        direction TB
        R1["Servos OFF"]
        R2["Measure tremor"]
        R3["Ball on platform tests control"]
        R4["Clinical scoring"]
        R1 --> R2 --> R3 --> R4
    end

    SWITCH["Joystick press<br/>toggles mode"] --> MODE1
    SWITCH --> MODE2

    style MODE1 fill:#d4edda,stroke:#27ae60,stroke-width:2px
    style MODE2 fill:#d1ecf1,stroke:#17a2b8,stroke-width:2px
    style SWITCH fill:#fff3cd,stroke:#ffc107,stroke-width:2px
```

---

## Who Uses This?

### Healthcare Users

```mermaid
mindmap
  root((SteadyHand<br/>Users))
    Healthcare
      Parkinson's patients
        10M worldwide
        Resting tremor 4-6Hz
        Can't eat independently
      Essential tremor
        7M in US alone
        Shakes during movement
        Most common tremor disorder
      Post-stroke
        25-50% develop tremor
        Rehab takes months
        Need immediate functional aid
      Elderly
        15-25% of over-65s
        Age-related tremor
        Often untreated
      Cerebral palsy
        17M globally
        Involuntary movements
      Multiple sclerosis
        2.8M worldwide
        Intention tremor
    Household
      Eating & drinking
        Hold spoon level
        Carry cup without spilling
        Feed yourself independently
      Daily tasks
        Steady phone for video calls
        Hold reading glasses
        Carry small objects
        Pour liquid accurately
      Hobby & craft
        Steady paintbrush for art therapy
        Hold pen for writing
        Model building
    Professional
      Surgeons & dentists
        Micro-tremor affects precision
        Instrument stabilisation
      Lab technicians
        Pipetting accuracy
        Sample handling
      Photographers
        Camera stabilisation
        DIY gimbal proof of concept
    Clinical
      Occupational therapists
        Objective tremor measurement
        Track rehab progress over weeks
        Quantified steadiness score
      Neurologists
        Monitor medication effectiveness
        Tremor frequency analysis
```

---

## Household Applications (with our limited sensors)

We only have **IMU + Joystick + Servos** — no cameras, no force sensors, no extra inputs. But that's enough:

| Use Case | What's on the Platform | Why It Matters |
|---|---|---|
| **Eating** | Spoon / fork clip | #1 daily need — restores independent eating |
| **Drinking** | Small cup holder | Prevents spilling hot drinks (burn risk for elderly) |
| **Video calls** | Phone cradle | Steady image for elderly talking to family — no shaky camera |
| **Medication** | Pill tray | Prevents dropping small pills — safety critical |
| **Writing** | Pen holder | Steadier handwriting for signing documents, letters |
| **Art therapy** | Brush holder | Rehab activity — painting helps motor recovery |
| **Pouring** | Small bottle cradle | Pour liquid without spilling (cooking, lab) |

All achieved by **swapping what clips onto the same 5x6cm platform**. One device, many attachments.

---

## Joystick Usage

The joystick serves **four critical functions** — not filler:

```mermaid
graph LR
    JOY["Analog Joystick<br/>(X-axis ADC + Y-axis ADC + Button)"] --> PRESS["Button Press"]
    JOY --> X_AXIS["X-Axis (left/right)"]
    JOY --> Y_AXIS["Y-Axis (up/down)"]

    PRESS -->|"Short press"| MODE["Toggle Mode<br/>Stabiliser ↔ Rehab"]
    PRESS -->|"Long press 3s"| CALIBRATE["Calibrate Zero Point<br/>Set current angle as 'level'"]
    PRESS -->|"During fall alert"| CANCEL["Cancel SOS<br/>'I'm OK' — stops alarm"]

    X_AXIS --> SENSITIVITY["Adjust Servo Sensitivity<br/>Left = gentle (elderly)<br/>Right = aggressive (strong tremor)"]

    Y_AXIS --> OLED_SCROLL["Scroll OLED Display<br/>Up/Down cycles through:<br/>Spirit Level → Waveform →<br/>Stats → Calibration → Rehab"]

    style JOY fill:#1abc9c,color:#fff
    style MODE fill:#27ae60,color:#fff
    style CALIBRATE fill:#3498db,color:#fff
    style CANCEL fill:#e74c3c,color:#fff
    style SENSITIVITY fill:#9b59b6,color:#fff
    style OLED_SCROLL fill:#e67e22,color:#fff
```

### 3D Printed Joystick Adapter (if available)

If you have access to a 3D printer, you could print a **thumb-grip cap** that sits on the joystick to make it easier for tremor patients to use (larger surface, textured grip). But the stock joystick works fine for the demo.

---

## Physical Build

```mermaid
graph LR
    subgraph TOP["TOP PLATE (5x6cm perfboard)"]
        CLIP["Spoon/cup clip zone"]
    end

    subgraph MIDDLE["ACTUATION LAYER"]
        PIVOT["M3 bolt + nut<br/>(loose = ball joint)"]
        SA["MG90S Servo A<br/>Controls ROLL<br/>(left/right tilt)"]
        SB["MG90S Servo B<br/>Controls PITCH<br/>(forward/back tilt)"]
        ROD_A["Push rod A<br/>22AWG Z-wire"]
        ROD_B["Push rod B<br/>22AWG Z-wire"]
    end

    subgraph BASE["HANDLE / BASE"]
        GRIP["User grips here<br/>(cardboard tube /<br/>perfboard frame)"]
        PICO["Pico B + PCA9685<br/>+ nRF24L01+ inside"]
    end

    CLIP --- PIVOT
    SA -->|"servo arm"| ROD_A -->|"pushes edge"| TOP
    SB -->|"servo arm"| ROD_B -->|"pushes edge"| TOP
    PIVOT --- BASE
    SA --- BASE
    SB --- BASE

    style TOP fill:#f39c12,color:#fff,stroke:#d35400,stroke-width:2px
    style MIDDLE fill:#ecf0f1,stroke:#bdc3c7,stroke-width:2px
    style BASE fill:#8e44ad,color:#fff,stroke:#6c3483,stroke-width:2px
```

**Dimensions:** ~15cm long, ~6cm wide, ~8cm tall
**Weight of moving part:** ~70g (platform + spoon)
**Assembly time:** ~2 hours

### What MG90S Can Handle

| Object | Weight | Works? |
|---|---|---|
| Spoon (empty) | ~40g | Yes — fast response |
| Spoon with food | ~60-80g | Yes |
| Small cup (espresso) | ~120g | Yes |
| Phone | ~180g | Borderline |
| Full mug | ~350g | No — too heavy |

---

## OLED Display Modes

| Mode | Screen | What It Shows | Who It's For |
|---|---|---|---|
| **1. Spirit Level** | Dot + crosshair, tilt angles | Real-time platform tilt — dot on cross = level | Live demo for judges |
| **2. Waveform** | Raw tremor wave vs flat compensated line | Before/after comparison + "78% reduction" | Proving the concept works |
| **3. Stats** | Duration, avg tremor, peak, stability %, corrections count | Session-level clinical data | Therapists / doctors |
| **4. Calibration** | Zero-point setting + sensitivity bar | Set what "level" means for this user | Initial setup |
| **5. Rehab** | Ball position dot + steadiness score + best today | Real-time rehab exercise scoring | Patients in therapy |
| **6. Fall Alert** | "FALL DETECTED" + countdown to SOS | 15-second cancel window | Emergency safety net |

Cycled with joystick Y-axis (up/down).

See `docs/images/steadyhand_oled_modes.png` for rendered mockups of each screen.

---

## Demo Script

```mermaid
graph LR
    S1["1. SETUP<br/>Spoon on platform<br/>Cereal on spoon"] --> S2["2. SERVOS OFF<br/>Shake hand<br/>Cereal falls off"]
    S2 --> S3["3. SERVOS ON<br/>Same shaking<br/>Cereal STAYS ON"]
    S3 --> S4["4. SHOW OLED<br/>Waveform mode<br/>78% reduction"]
    S4 --> S5["5. REHAB MODE<br/>Ball on platform<br/>Score: 67%"]
    S5 --> S6["6. JUDGE TRIES<br/>They shake it<br/>Spoon stays level"]

    style S1 fill:#ffc107,color:#333
    style S2 fill:#e74c3c,color:#fff
    style S3 fill:#27ae60,color:#fff
    style S4 fill:#3498db,color:#fff
    style S5 fill:#9b59b6,color:#fff
    style S6 fill:#e67e22,color:#fff
```

**Drop line:** *"A Liftware Steady costs £200. We built this for £15."*

---

## Build Timeline

```mermaid
gantt
    title SteadyHand — 12 Hour Build Plan
    dateFormat HH:mm
    axisFormat %H:%M

    section Critical Path
    nRF24L01+ wireless link confirmed     :crit, w, 00:00, 1h
    BMI160 IMU + complementary filter      :crit, i, after w, 1h
    PCA9685 + servo PID control            :crit, p, after i, 1h
    End-to-end stabilisation working       :crit, e, after p, 1h

    section Mechanical
    Platform + pivot + push rods           :m, after e, 1h
    Spoon mount + handle assembly          :h, after m, 1h

    section Software Polish
    OLED display modes (4 screens)         :o, after h, 1h
    Fall detection on Core 1               :f, after o, 30min
    Rehab trainer mode                     :r, after f, 30min

    section Documentation
    Wiring diagram + README                :d, after r, 1h
    Architecture diagrams                  :a, after d, 30min

    section Final
    PID tuning + reliability testing       :t, after a, 1h
    Practice demo                          :demo, after t, 30min
```

---

## Scoring Breakdown

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **29** | 10M+ Parkinson's patients. Affects eating — most basic human need. 10+ user groups. Household + clinical + professional |
| **Live Demo (25)** | **24** | Cereal-on-spoon before/after. OLED shows quantified improvement. Dual-mode demo. Judge tries it |
| **Technical (20)** | **19** | Complementary filter, PID control, 100Hz IMU, 4ms latency, dual-core, wireless streaming, 4 OLED modes |
| **Innovation (15)** | **14** | "Noise-cancelling for movement." Dual-mode (stabiliser + rehab). DIY Liftware for £15. Household attachment system |
| **Docs (10)** | **9** | Mermaid diagrams, control flow, architecture, OLED mockups, mechanical drawings |
| **Total** | **95** | |

---

## vs Competitors

| Feature | Liftware Steady | Apple Watch | SteadyHand |
|---|---|---|---|
| **Price** | £200 | £400+ | ~£15 |
| **Tremor cancellation** | Yes | No | Yes |
| **Fall detection** | No | Yes | Yes |
| **Rehab scoring** | No | No | Yes |
| **Clinical metrics** | No | Heart rate | Tremor amp, freq, reduction %, stability |
| **Phone required** | No | Yes (iPhone) | No |
| **Swappable attachments** | No (spoon only) | N/A | Yes (spoon, cup, phone, pen) |
| **Open source** | No | No | Yes |

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| MG90S too slow for fast tremors (>6Hz) | Focus on slow/medium tremor. Show % improvement, not perfection |
| Mechanical assembly takes too long | Pre-plan dimensions. Simple Z-wire push rods. Budget 2h max |
| PID tuning is fiddly | Start P+D only. Tune Kp first, add Kd for damping. Skip Ki |
| "Apple Watch does this" | "Apple Watch detects falls. SteadyHand actively cancels tremor. One monitors, ours solves." |
| Wireless latency spikes | Moving average on received data. Fallback to last known angle |
