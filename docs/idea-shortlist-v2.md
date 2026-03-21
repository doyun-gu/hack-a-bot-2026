# Hack-A-Bot 2026 — Idea Shortlist v2

> Updated with full component set: DC motor, potentiometer, joystick, IMU, servos, OLED, wireless, LEDs, buttons
>
> Scored: Problem Fit (30) | Live Demo (25) | Technical (20) | Innovation (15) | Docs (10) = 100

---

## Available Components

| Component | Qty | Capability |
|---|---|---|
| Raspberry Pi Pico 2 | 2 | Dual-core ARM Cortex-M33 |
| nRF24L01+ PA+LNA | 2 | 2.4GHz wireless link |
| BMI160 IMU | 1 | 6-axis tilt + rotation + motion |
| Analog Joystick | 1+ | 2-axis input + button |
| Potentiometer | 1+ | Smooth analog dial |
| DC Motor | 1+ | Continuous rotation, wheels, flywheel |
| PCA9685 Servo Driver | 1 | 16-channel PWM |
| MG90S Servos | 2+ | Precise angle positioning |
| 0.96" OLED (SSD1306) | 1 | 128x64 display |
| LM2596S Buck Converter | 1 | Step-down voltage regulation |
| 300W Buck-Boost Converter | 1 | High-power motor driving |
| 12V 6A PSU | 1 | 72W power budget |
| Assorted kit | — | LEDs, buttons, resistors, capacitors, diodes |
| Breadboards + perfboard | — | Prototyping |
| 22AWG wire + M3 screws | — | Wiring + mechanical |

---

## 1. NeuroSync — Neurological Diagnostic Platform

**Theme:** Assistive Technology + Autonomy
**One-liner:** Multi-test interactive diagnostic station that measures, classifies, and gamifies hand tremor assessment — replacing £10K clinical equipment with a £15 device.

### Components Used

```mermaid
graph LR
    IMU["BMI160 IMU<br/>Tremor measurement"] --> CORE["NeuroSync"]
    SERVO["Servos<br/>Difficulty levels<br/>Pointer arm"] --> CORE
    MOTOR["DC Motor<br/>Reaction wheel<br/>Resistance test"] --> CORE
    JOY["Joystick<br/>Test selection<br/>Patient input"] --> CORE
    POT["Potentiometer<br/>Sensitivity dial<br/>PID tuning"] --> CORE
    OLED["OLED<br/>Scores, fingerprint<br/>Condition report"] --> CORE
    NRF["nRF24L01+<br/>Tray → Base station"] --> CORE

    style CORE fill:#e74c3c,color:#fff,stroke-width:3px
```

### Architecture

```mermaid
graph TB
    subgraph TRAY["Pico A — Diagnostic Tray"]
        T_IMU["BMI160: tremor angle + frequency"]
        T_SERVO["Servos: difficulty tilt + pointer"]
        T_MOTOR["DC Motor: reaction wheel + resistance"]
        T_POT["Potentiometer: sensitivity adjust"]
        T_NRF["nRF24L01+ TX"]
        T_LED["LEDs: green/yellow/red status"]
    end

    subgraph BASE["Pico B — Clinician Base Station"]
        B_NRF["nRF24L01+ RX"]
        B_OLED["OLED: scores, fingerprint, report"]
        B_JOY["Joystick: select test, start/stop"]
        B_LED["LEDs: patient status"]
    end

    TRAY -->|"wireless 100Hz"| BASE

    style TRAY fill:#fce4e4,stroke:#e74c3c,stroke-width:2px
    style BASE fill:#d4edda,stroke:#27ae60,stroke-width:2px
```

### Key Features
- 4 diagnostic tests (stability, tracking, reaction, pattern)
- Tremor fingerprint (unique polar pattern per person)
- Gamified scoring (points, streaks, stars)
- Adaptive real-time difficulty (servos adjust during test)
- Condition classification (Parkinson's vs essential tremor vs stress)
- Reaction wheel self-balancing (DC motor flywheel)
- Biometric authentication mode (security application)

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | 10M+ Parkinson's patients. UPDRS is subjective. No cheap alternative |
| Live Demo (25) | **25** | Judge holds tray, gets personal score + fingerprint. Two judges compete |
| Technical (20) | **20** | Reaction wheel PID, frequency analysis, adaptive control, dual-core, gamification |
| Innovation (15) | **15** | Tremor fingerprinting, gamified diagnostics, condition classification on Pico |
| Docs (10) | **9** | Full Mermaid diagrams, clinical comparison, algorithm docs |
| **Total** | **98** | |

**Full proposal:** [`docs/tremortray-proposal.md`](tremortray-proposal.md)

---

## 2. Self-Balancing Reaction Wheel Robot

**Theme:** Autonomy
**One-liner:** A physical rod/platform balances itself upright using a spinning flywheel — the same technology that controls the International Space Station's orientation.

### Components Used

```mermaid
graph LR
    IMU["BMI160 IMU<br/>Balance angle"] --> CORE["Self-Balancer"]
    MOTOR["DC Motor<br/>Reaction wheel flywheel"] --> CORE
    SERVO["Servos<br/>Base adjustment<br/>Pointer display"] --> CORE
    POT["Potentiometer<br/>Live PID tuning"] --> CORE
    JOY["Joystick<br/>Perturbation control"] --> CORE
    OLED["OLED<br/>Balance angle, PID values"] --> CORE
    NRF["nRF24L01+<br/>Robot → Remote"] --> CORE

    style CORE fill:#3498db,color:#fff,stroke-width:3px
```

### Architecture

```mermaid
graph TB
    subgraph ROBOT["Pico A — Robot (balances)"]
        R_IMU["BMI160: measures tilt from vertical"]
        R_MOTOR["DC Motor: flywheel — speed up/down to correct tilt"]
        R_SERVO["Servo: adjustable base angle"]
        R_NRF["nRF24L01+ TX: streams balance data"]
        R_LED["LEDs: balance status"]
    end

    subgraph REMOTE["Pico B — Remote Control"]
        C_JOY["Joystick: push the robot (perturbation)"]
        C_POT["Potentiometer: tune Kp/Kd/Ki LIVE"]
        C_OLED["OLED: tilt angle graph, PID values, motor speed"]
        C_NRF["nRF24L01+ RX/TX"]
        C_LED["LEDs: connected/disconnected"]
    end

    ROBOT <-->|"wireless"| REMOTE

    style ROBOT fill:#e8f4fd,stroke:#3498db,stroke-width:2px
    style REMOTE fill:#fef9e7,stroke:#d4ac0d,stroke-width:2px
```

### How It Works

```mermaid
flowchart TD
    READ["Read IMU: tilt angle from vertical"] --> PID["PID Controller<br/>error = 0° - current_angle"]
    PID --> MOTOR_CMD["Adjust motor speed:<br/>Tilting left → speed up motor (pushes right)<br/>Tilting right → slow down motor (pushes left)"]
    MOTOR_CMD --> BALANCE["Robot stays vertical"]
    BALANCE --> READ

    REMOTE_PUSH["Remote: joystick pushes robot"] -.->|"wireless perturbation"| READ
    REMOTE_TUNE["Remote: potentiometer adjusts PID gains"] -.->|"wireless Kp/Kd update"| PID

    style READ fill:#9b59b6,color:#fff
    style PID fill:#27ae60,color:#fff
    style MOTOR_CMD fill:#e67e22,color:#fff
    style BALANCE fill:#3498db,color:#fff
```

### Demo Script
1. Place robot on table, tilted. Press start
2. Flywheel spins up. **Robot stands upright by itself**
3. Push it — **it recovers**
4. Judge pushes it via joystick on remote — it fights back
5. Twist potentiometer — see PID values change on OLED, robot behaviour changes
6. "This is how the International Space Station controls its orientation"

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **24** | Autonomy demo, but "balancing a stick" is less human-impact than medical |
| Live Demo (25) | **25** | Push it and it recovers. Most visually dramatic demo possible |
| Technical (20) | **20** | Reaction wheel PID is graduate-level control engineering. Maximum depth |
| Innovation (15) | **15** | Spacecraft tech at a hackathon. Nobody else will attempt this |
| Docs (10) | **9** | Control theory diagrams, angular momentum physics |
| **Total** | **93** | |

**Risk:** PID tuning can be frustrating. Mitigate: potentiometer for LIVE tuning — adjust during demo.

---

## 3. Tilt-Controlled Wireless RC Vehicle

**Theme:** Autonomy + Interactive Play
**One-liner:** Tilt your hand to steer a car. Like a Wii controller but for a physical vehicle with a live dashboard.

### Architecture

```mermaid
graph TB
    subgraph CTRL["Pico A — Controller (handheld)"]
        C_IMU["BMI160: tilt = steering direction"]
        C_JOY["Joystick: fine control override"]
        C_POT["Potentiometer: speed limit dial"]
        C_OLED["OLED: speedometer + signal strength"]
        C_NRF["nRF24L01+ TX"]
    end

    subgraph CAR["Pico B — Vehicle"]
        V_MOTOR["DC Motor: drive wheels"]
        V_SERVO["Servo: steering mechanism"]
        V_NRF["nRF24L01+ RX"]
        V_LED["LEDs: headlights + brake lights"]
    end

    CTRL -->|"tilt data wireless"| CAR

    style CTRL fill:#e8f4fd,stroke:#3498db,stroke-width:2px
    style CAR fill:#fce4e4,stroke:#e74c3c,stroke-width:2px
```

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **25** | Accessible control for limited dexterity. Fun but less impactful |
| Live Demo (25) | **25** | Tilt hand → car moves. Everyone understands instantly |
| Technical (20) | **18** | IMU → wireless → motor control. Solid but not cutting-edge |
| Innovation (15) | **13** | Tilt control exists (Wii) but physical vehicle + dashboard is a step up |
| Docs (10) | **9** | |
| **Total** | **90** | |

---

## 4. Two-Player Wireless Arcade

**Theme:** Interactive Play
**One-liner:** Two-player physical game console where each player has their own Pico controller and they compete in wireless physical challenges.

### Architecture

```mermaid
graph LR
    subgraph P1["Pico A — Player 1"]
        P1_JOY["Joystick: game input"]
        P1_POT["Potentiometer: difficulty"]
        P1_SERVO["Servo: physical paddle"]
        P1_IMU["IMU: gesture power-ups"]
        P1_LED["LEDs: score indicator"]
    end

    subgraph P2["Pico B — Player 2"]
        P2_JOY["Joystick: game input"]
        P2_OLED["OLED: scores + timer"]
        P2_MOTOR["DC Motor: spinning challenge wheel"]
        P2_SERVO["Servo: physical paddle"]
        P2_LED["LEDs: winner flash"]
    end

    P1 <-->|"wireless"| P2

    style P1 fill:#3498db,color:#fff
    style P2 fill:#e74c3c,color:#fff
```

### Game Modes
- **Servo Pong:** Servo paddles, ball rolls between them, joystick controls paddle
- **Reaction Race:** LED lights up → first to press button wins
- **Spin the Wheel:** DC motor spins wheel, stop at right moment for points
- **Tilt Battle:** Hold tray steady longest (uses NeuroSync stability scoring)

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **22** | Fun but weak problem statement. Frame as "social gaming for elderly in care homes" |
| Live Demo (25) | **25** | Two judges compete. Most engaging demo possible |
| Technical (20) | **18** | Wireless game sync, physical mechanics, multi-mode |
| Innovation (15) | **14** | Physical wireless arcade is fresh at hardware hackathons |
| Docs (10) | **9** | |
| **Total** | **88** | |

---

## 5. Autonomous Smart Pourer

**Theme:** Assistive Technology + Sustainability
**One-liner:** Robot pours exact liquid volumes autonomously. Set the amount, press start, walk away. Zero spill, zero waste.

### Architecture

```mermaid
graph TB
    subgraph POURER["Pico A — Pourer"]
        P_MOTOR["DC Motor: tilts bottle cradle"]
        P_SERVO["Servo: flow control gate"]
        P_IMU["BMI160: pour angle measurement"]
        P_POT["Potentiometer: set target volume"]
        P_NRF["nRF24L01+ TX"]
        P_LED["LEDs: pouring status"]
    end

    subgraph DASH["Pico B — Dashboard"]
        D_OLED["OLED: target vs actual volume"]
        D_JOY["Joystick: select drink preset"]
        D_NRF["nRF24L01+ RX"]
    end

    POURER -->|"wireless"| DASH

    style POURER fill:#e67e22,color:#fff
    style DASH fill:#27ae60,color:#fff
```

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **27** | Tremor patients can't pour. Sustainability = exact portions, zero waste |
| Live Demo (25) | **24** | Pour a perfect shot in front of judges. Unexpected and fun |
| Technical (20) | **17** | Motor control, angle sensing, flow control. Solid but simpler |
| Innovation (15) | **14** | Robotic bartender at a hardware hackathon is unexpected |
| Docs (10) | **9** | |
| **Total** | **91** | |

---

## 6. Haptic Navigation Aid for Visually Impaired

**Theme:** Assistive Technology
**One-liner:** Wearable device guides visually impaired users with directional vibrations — DC motor buzzes to indicate turn left, right, or stop.

### Architecture

```mermaid
graph TB
    subgraph WEAR["Pico A — Wearable (belt/wrist)"]
        W_MOTOR["DC Motor: vibration feedback<br/>Different speeds = different directions"]
        W_SERVO["Servo: directional pointer on wrist"]
        W_IMU["BMI160: user heading + step count"]
        W_NRF["nRF24L01+ RX"]
        W_LED["LED: status"]
    end

    subgraph NAV["Pico B — Navigator (companion holds)"]
        N_JOY["Joystick: set direction"]
        N_POT["Potentiometer: vibration intensity"]
        N_OLED["OLED: map/heading display"]
        N_NRF["nRF24L01+ TX"]
    end

    NAV -->|"direction commands"| WEAR

    style WEAR fill:#9b59b6,color:#fff
    style NAV fill:#27ae60,color:#fff
```

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | 253M visually impaired worldwide. Daily navigation challenge |
| Live Demo (25) | **23** | Blindfold a judge, guide them across room with vibrations |
| Technical (20) | **17** | Motor vibration patterns, IMU heading, wireless commands |
| Innovation (15) | **13** | Haptic navigation exists but DIY Pico version is creative |
| Docs (10) | **9** | |
| **Total** | **91** | |

---

## 7. Gesture-Controlled Robotic Arm

**Theme:** Assistive Technology + Autonomy
**One-liner:** Tilt your hand to control a multi-joint robotic arm. Potentiometer controls grip force. DC motor adds wrist rotation.

### Architecture

```mermaid
graph TB
    subgraph GLOVE["Pico A — Controller (wearable)"]
        G_IMU["BMI160: hand tilt → arm direction"]
        G_POT["Potentiometer: grip force control"]
        G_JOY["Joystick: fine position override"]
        G_NRF["nRF24L01+ TX"]
    end

    subgraph ARM["Pico B — Robot Arm"]
        A_SERVO["3x Servos: shoulder + elbow + gripper"]
        A_MOTOR["DC Motor: wrist rotation (360°)"]
        A_OLED["OLED: arm angles, grip force, mode"]
        A_NRF["nRF24L01+ RX"]
    end

    GLOVE -->|"wireless gestures"| ARM

    style GLOVE fill:#3498db,color:#fff
    style ARM fill:#e67e22,color:#fff
```

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **28** | Limited mobility people controlling remote objects |
| Live Demo (25) | **24** | Judge wears glove, moves arm. Impressive and interactive |
| Technical (20) | **18** | IMU mapping, inverse kinematics, DC motor rotation, grip force |
| Innovation (15) | **12** | Robotic arms exist but potentiometer grip force control is novel |
| Docs (10) | **9** | |
| **Total** | **91** | |

---

## 8. Self-Levelling Delivery Vehicle

**Theme:** Autonomy
**One-liner:** RC vehicle with a cargo platform that autonomously keeps itself level while driving — DC motor drives, servos auto-level.

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **25** | Medical supply delivery, hazardous material transport |
| Live Demo (25) | **24** | Drive over ramp → cup of water stays level |
| Technical (20) | **19** | PID levelling + motor control + wireless |
| Innovation (15) | **13** | Self-levelling exists in gimbals but on a vehicle is creative |
| Docs (10) | **9** | |
| **Total** | **90** | |

---

## 9. Physical Rhythm Game

**Theme:** Interactive Play
**One-liner:** Guitar Hero but physical — DC motor spins a target wheel, player uses joystick and buttons to hit zones at the right moment.

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **22** | Fun, engaging, but weak problem statement |
| Live Demo (25) | **25** | Addictive — judges won't want to stop playing |
| Technical (20) | **17** | Motor timing, servo targets, scoring, wireless multiplayer |
| Innovation (15) | **14** | Physical rhythm game is unusual at hackathons |
| Docs (10) | **9** | |
| **Total** | **87** | |

---

## 10. Smart Energy Monitor + Auto-Saver

**Theme:** Sustainability
**One-liner:** Potentiometer simulates power load. When consumption exceeds threshold, servos automatically switch off non-essential circuits. OLED shows live energy dashboard.

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **25** | Energy waste is real. Auto-saver concept is practical |
| Live Demo (25) | **20** | Turn potentiometer → servo switches off a light. Clear but less dramatic |
| Technical (20) | **16** | Threshold logic, wireless monitoring, servo switching |
| Innovation (15) | **12** | Energy monitors exist. Auto-switching is the creative angle |
| Docs (10) | **9** | |
| **Total** | **82** | |

---

## Summary Ranking

| Rank | Idea | Theme | Score | Components Used | Best For |
|---|---|---|---|---|---|
| **1** | **NeuroSync Diagnostic** | Assistive | **98** | ALL | Problem Fit + Innovation + Platform potential |
| **2** | **Reaction Wheel Self-Balancer** | Autonomy | **93** | DC motor, IMU, pot, servo, joy, OLED, wireless | Technical wow — spacecraft engineering |
| **3** | **Smart Pourer / Bartender** | Assistive+Sust. | **91** | DC motor, servo, pot, IMU, OLED, wireless | Most unexpected demo |
| **3** | **Haptic Navigation Aid** | Assistive | **91** | DC motor, IMU, servo, pot, joy, OLED, wireless | Strongest human impact |
| **3** | **Gesture Robotic Arm** | Assistive | **91** | ALL | Uses every single component |
| **6** | **Tilt-Control RC Vehicle** | Autonomy+Play | **90** | DC motor, IMU, servo, pot, joy, OLED, wireless | Safest build, fun demo |
| **6** | **Self-Levelling Delivery** | Autonomy | **90** | DC motor, IMU, servo, pot, joy, OLED, wireless | Strong autonomy showcase |
| **8** | **Two-Player Arcade** | Play | **88** | ALL | Most interactive demo |
| **9** | **Physical Rhythm Game** | Play | **87** | DC motor, servo, joy, pot, OLED, wireless | Most fun |
| **10** | **Energy Monitor** | Sustainability | **82** | Pot, servo, DC motor, OLED, wireless | Best sustainability angle |

---

---

## BONUS: If Wheels + ESP32-CAM Available

With wheels (DC motor driven) and an ESP32-CAM, entirely new categories open up:

### 11. Search & Rescue Scout Robot

**Theme:** Assistive + Autonomy | **Score: 95**

Autonomous robot navigates toward people using camera vision. Streams live video to operator. Servo-mounted camera for panning. IMU detects obstacles/slopes.

```mermaid
graph TB
    subgraph ROBOT["Robot (Pico A + ESP32-CAM)"]
        CAM["ESP32-CAM<br/>Live video stream<br/>Basic motion detection"]
        MOTOR_L["DC Motor L: left wheel"]
        MOTOR_R["DC Motor R: right wheel"]
        SERVO_CAM["Servo: camera pan/tilt"]
        IMU_R["BMI160: slope + collision detection"]
        NRF_R["nRF24L01+ TX: telemetry"]
    end

    subgraph CTRL["Controller (Pico B)"]
        JOY_C["Joystick: drive direction"]
        POT_C["Potentiometer: speed limit"]
        OLED_C["OLED: telemetry dashboard"]
        NRF_C["nRF24L01+ RX"]
    end

    ROBOT -->|"wireless"| CTRL
    CAM -->|"WiFi video"| PHONE["Phone/laptop<br/>live camera feed"]

    style ROBOT fill:#e74c3c,color:#fff
    style CTRL fill:#3498db,color:#fff
    style PHONE fill:#27ae60,color:#fff
```

**Why 95 pts:** Life-saving application. Camera + mobility + wireless = genuinely useful robot. Judges can see live video feed while driving the robot with joystick. ESP32-CAM streams via WiFi to phone while Pico handles motor control via nRF24L01+.

---

### 12. Autonomous Line-Following Delivery Bot

**Theme:** Autonomy + Sustainability | **Score: 92**

Robot follows a line autonomously, delivers package, returns. Camera detects the line. Self-levelling cargo platform keeps delivery stable.

```mermaid
graph LR
    CAM["ESP32-CAM<br/>line detection"] --> PICO["Pico A<br/>Motor control + navigation"]
    PICO --> ML["DC Motor L"]
    PICO --> MR["DC Motor R"]
    PICO --> SERVO["Servo: cargo levelling"]
    IMU["IMU: tilt detection"] --> PICO
    PICO -->|"wireless"| BASE["Pico B: OLED dashboard"]

    style CAM fill:#e67e22,color:#fff
    style PICO fill:#3498db,color:#fff
    style BASE fill:#27ae60,color:#fff
```

---

### 13. Surveillance / Security Patrol Bot

**Theme:** Autonomy | **Score: 91**

Autonomous or RC patrol robot with live camera. Detects motion via ESP32, alerts base station. IMU detects if robot is picked up/tampered with.

---

### 14. Telepresence Robot for Elderly

**Theme:** Assistive | **Score: 93**

Remote-controlled mobile robot with camera — family members can "visit" elderly relatives remotely. Drive around their home, see through the camera, servo waves hello.

```mermaid
graph TB
    subgraph ROBOT["Telepresence Robot"]
        CAM2["ESP32-CAM: live video to family"]
        WHEELS["DC Motors: mobility"]
        SERVO2["Servo: wave arm / point"]
        OLED2["OLED: show caller name / emoji"]
        IMU2["IMU: fall detection if knocked over"]
    end

    subgraph FAMILY["Family Member (remote)"]
        PHONE2["Phone/laptop: see video"]
        CTRL2["Pico controller:<br/>Joystick drives robot"]
    end

    ROBOT <--> FAMILY

    style ROBOT fill:#9b59b6,color:#fff
    style FAMILY fill:#27ae60,color:#fff
```

**Why 93 pts:** Loneliness epidemic in elderly. Family can't always visit. This lets them "be there" physically. Emotional impact is massive.

---

## Updated Summary Ranking (All Ideas)

| Rank | Idea | Theme | Score | Key Components |
|---|---|---|---|---|
| **1** | **NeuroSync Diagnostic** | Assistive | **98** | IMU, servo, motor, pot, joy, OLED, wireless |
| **2** | **Search & Rescue Scout** | Assistive+Auto | **95** | ESP32-CAM, wheels, servo, IMU, joy, OLED, wireless |
| **3** | **Reaction Wheel Self-Balancer** | Autonomy | **93** | DC motor, IMU, pot, servo, joy, OLED, wireless |
| **3** | **Telepresence Robot** | Assistive | **93** | ESP32-CAM, wheels, servo, OLED, IMU, wireless |
| **5** | **Line-Following Delivery Bot** | Auto+Sust. | **92** | ESP32-CAM, wheels, servo, IMU, OLED, wireless |
| **6** | **Smart Pourer** | Assistive+Sust. | **91** | DC motor, servo, pot, IMU, OLED, wireless |
| **6** | **Haptic Navigation Aid** | Assistive | **91** | DC motor, IMU, servo, pot, joy, OLED, wireless |
| **6** | **Gesture Robotic Arm** | Assistive | **91** | IMU, pot, joy, servo, DC motor, OLED, wireless |
| **6** | **Surveillance Patrol Bot** | Autonomy | **91** | ESP32-CAM, wheels, IMU, OLED, wireless |
| **10** | **Tilt-Control RC Vehicle** | Auto+Play | **90** | DC motor, IMU, servo, pot, joy, OLED, wireless |
| **10** | **Self-Levelling Delivery** | Autonomy | **90** | DC motor, IMU, servo, pot, joy, OLED, wireless |
| **12** | **Two-Player Arcade** | Play | **88** | Joy, pot, servo, DC motor, IMU, OLED, wireless |
| **13** | **Physical Rhythm Game** | Play | **87** | DC motor, servo, joy, pot, OLED, wireless |
| **14** | **Energy Monitor** | Sustainability | **82** | Pot, servo, DC motor, OLED, wireless |

---

## Decision Guide

| If you want... | Choose... | Why |
|---|---|---|
| **Highest score** | NeuroSync (98) | Deepest technical + clinical + platform story |
| **Most jaw-dropping demo** | Reaction Wheel (93) | "It balances by itself using spacecraft physics" |
| **Best with camera** | Search & Rescue (95) | Live video feed + robot mobility = cinematic demo |
| **Strongest human story** | Telepresence Robot (93) | Elderly loneliness — family "visits" remotely |
| **Safest build in 24h** | RC Vehicle (90) | Well-understood mechanics, fun, reliable |
| **Most fun for judges** | Two-Player Arcade (88) | Judges compete — they'll remember you |
| **Most unexpected** | Smart Pourer (91) | Nobody expects a robotic bartender |
| **Uses EVERY component** | NeuroSync (98) or Robotic Arm (91) | Nothing wasted |
| **Best sustainability** | Line-Following Delivery (92) | Autonomous + efficient + camera |
