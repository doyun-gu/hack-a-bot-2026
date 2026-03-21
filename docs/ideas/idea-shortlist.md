# Hack-A-Bot 2026 — Idea Shortlist

> Scored against the rubric: Problem Fit (30) | Live Demo (25) | Technical (20) | Innovation (15) | Docs (10) = 100

---

## 1. Gesture-Controlled Assistive Gripper Arm

**Theme:** Assistive Technology
**One-liner:** Wearable IMU glove wirelessly controls a multi-servo robotic gripper for people with limited reach/mobility.

| Pico A (Wearable) | Pico B (Actuator) |
|---|---|
| BMI160 IMU — hand orientation | PCA9685 + 3-4 MG90S servos — arm joints + gripper |
| Joystick — grip open/close | OLED — status, angles, signal strength |
| nRF24L01+ TX | nRF24L01+ RX |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **28** | Clear user (limited mobility), clear need (remote object manipulation), strong rationale |
| Live Demo (25) | **24** | Judge wears glove, moves arm — instant "wow". Interactive demos always score highest |
| Technical (20) | **18** | IMU sensor fusion, SPI wireless, I2C servo driver, dual-core task split, safety watchdog |
| Innovation (15) | **12** | Gesture vocabulary, proportional mapping, wearable-to-actuator bridge — not a new concept but creative execution |
| Docs (10) | **9** | Wiring diagram + architecture diagram are visually rich |
| **Total** | **91** | |

**Risk:** Mechanical arm assembly takes time. Mitigate: simple 2-DOF arm + gripper, no complex joints.

---

## 2. Tremor-Stabilising Platform — "SteadyHand"

**Theme:** Assistive Technology / Autonomy (semi-autonomous)
**One-liner:** A self-levelling platform that uses inverse kinematic compensation to cancel hand tremor and instability — like noise-cancelling headphones, but for physical movement.

### The Core Principle

```
Noise cancelling:    Mic detects sound  → speaker produces inverse wave  → silence
SteadyHand:          IMU detects tilt   → servos produce inverse tilt    → platform stays level
```

IMU measures the unwanted movement. Servos produce the exact opposite. The object on the platform doesn't move.

### Who Uses This? — Healthcare & Beyond

| End User | Problem | How SteadyHand Helps |
|---|---|---|
| **Parkinson's patients** | 6.1 million people worldwide. Resting tremor (4-6Hz) makes eating, drinking, carrying objects humiliating and dangerous | Platform keeps cup/spoon/plate level — restores independence and dignity at mealtimes |
| **Essential tremor patients** | Most common movement disorder — 7 million in US alone. Hands shake during intentional movement | Stabilises objects during purposeful tasks (writing, eating, holding phone) |
| **Elderly with age-related tremor** | Affects 15-25% of adults over 65. Often untreated because it's "just aging" | Simple assistive device for daily living — no medication side effects |
| **Post-stroke patients** | 25-50% develop upper limb tremor. Rehab takes months-years | Immediate functional aid during recovery — eat independently while rehabbing |
| **Surgeons & dentists** | Even micro-tremors affect precision in microsurgery, dental work, suturing | Instrument stabilisation platform — demonstrated concept used in Da Vinci surgical robots |
| **Lab technicians** | Pipetting, handling samples, pouring precise volumes — tremor causes errors | Stabilised work surface for precision liquid handling |
| **Photographers / videographers** | Camera shake ruins shots. Existing gimbals are expensive (£200+) | DIY camera stabiliser for £15 in components — proof of concept for low-cost gimbal |
| **Soldiers / veterans with PTSD** | Stress-induced tremor affects daily tasks. Stigma prevents seeking help | Discreet assistive device — no visible "medical equipment" look |
| **Cerebral palsy patients** | Involuntary movements affect 17 million people globally | Stabilised surface for eating, writing, using devices |
| **Multiple sclerosis patients** | Intention tremor worsens when reaching for objects — the exact moment you need stability | Compensates for the reach-triggered tremor that makes grasping difficult |

### Architecture

| Pico A — Wearable Sensor (on hand/wrist) | Pico B — Stabilised Platform (holds objects) |
|---|---|
| BMI160 IMU — roll, pitch, gyro at 100Hz | PCA9685 + 2x MG90S servos — 2-axis tilt compensation |
| nRF24L01+ TX — streams orientation data | nRF24L01+ RX — receives tilt data |
| Joystick — sensitivity adjust, manual override | OLED — real-time display (see below) |
| LED — status indicator | LEDs — stability indicator (green/yellow/red) |

### How the OLED Display Is Used

The 0.96" OLED (128x64 pixels) serves as a **real-time clinical dashboard.** Four display modes, cycled with joystick press:

**Mode 1 — Live Spirit Level (default)**
```
┌──────────────────────┐
│  STEADYHAND  [LIVE]  │
│                      │
│      ┌─────────┐     │
│      │    o    │     │  ← dot shows current tilt
│      │  ──┼──  │     │     crosshair = level target
│      │    │    │     │     dot ON crosshair = perfect
│      └─────────┘     │
│  Roll: -2.3°  OK     │
│  Pitch: +1.1° OK     │
└──────────────────────┘
```
A visual spirit level — the dot moves as the hand tilts. When the platform is compensating correctly, the dot stays centred. Judges can immediately SEE the stabilisation working.

**Mode 2 — Tremor Waveform**
```
┌──────────────────────┐
│  TREMOR WAVEFORM     │
│                      │
│  ∿∿∿╲╱∿∿∿∿∿∿∿∿∿∿   │  ← raw tremor (before)
│  ─────────────────   │  ← after compensation (flat)
│                      │
│  Amplitude: 4.2°     │
│  Frequency: 4.8Hz    │
│  Reduction: 78%      │
└──────────────────────┘
```
Shows the raw tremor signal vs the compensated output — exactly like showing noise-cancelling before/after. The **reduction percentage** is the key metric. Judges can see "78% tremor reduction" quantified.

**Mode 3 — Session Statistics**
```
┌──────────────────────┐
│  SESSION STATS       │
│                      │
│  Duration:  00:04:32 │
│  Avg tremor: 3.8°    │
│  Peak tremor: 12.1°  │
│  Stability:  82%     │
│  Corrections: 1,847  │
│  Wireless:   98.2%   │
└──────────────────────┘
```
Tracks the session over time. "Stability score" = percentage of time platform was within ±2° of level. This is the number a clinician would use to assess a patient's tremor severity over time.

**Mode 4 — Calibration**
```
┌──────────────────────┐
│  CALIBRATION         │
│                      │
│  Place on flat       │
│  surface and press   │
│  joystick to zero.   │
│                      │
│  > [CALIBRATE]       │
│  Sensitivity: ███░░  │
└──────────────────────┘
```
Joystick sets the "level" reference point (not always flat — a tilted work surface is fine). Joystick left/right adjusts servo sensitivity (aggressive vs smooth compensation). This lets different patients tune it to their tremor type.

### Control Loop Detail

```
PICO A (100Hz loop — every 10ms):
  1. Read BMI160 accel + gyro
  2. Complementary filter → roll, pitch (smooth, drift-free)
  3. Pack into struct: { roll, pitch, tremor_amplitude, timestamp }
  4. Send via nRF24L01+ (SPI)

     ~~~~ 2.4 GHz wireless (~2ms latency) ~~~~

PICO B (receives + actuates):
  1. Receive packet from nRF24L01+
  2. PID controller:
     error = target_angle - received_angle
     correction = Kp×error + Kd×(error - prev_error)/dt
  3. Map correction → servo PWM via PCA9685 (I2C)
     servo_angle = 90° + correction  (90° = centre)
  4. Update OLED display (every 100ms — don't slow the servo loop)
  5. Update stability score, log tremor data
```

**Total latency budget:** IMU read (1ms) + filter (0.1ms) + wireless TX/RX (2ms) + PID (0.1ms) + servo command (0.5ms) = **~4ms.** Well within the 20ms needed for effective compensation.

### Mechanical Build

```
SIDE VIEW:                           TOP VIEW:

  ┌─────────────────┐ ← top plate    ┌─────────────────┐
  │  cup / object   │   (perfboard)  │                 │
  └────┬───────┬────┘                │   SERVO A ──────┤ push rod
       │ pivot │                     │       │         │
       │   ●   │ ← M3 bolt+nut      │    ●  pivot     │
       │       │    (loose=joint)    │       │         │
  ┌────┴───────┴────┐                │   SERVO B ──────┤ push rod
  │  SERVO A  B     │                │                 │
  │  base plate     │                └─────────────────┘
  └─────────────────┘

  Servo A arm pushes left edge up/down → controls ROLL
  Servo B arm pushes front edge up/down → controls PITCH
  Centre pivot allows 2-axis tilt

  Push rods: 22AWG solid wire bent into Z-shape
  Connects servo horn → hole in top plate edge
```

### Demo Script

1. **Setup:** Place SteadyHand on table. Put a cup of water on the platform. OLED shows spirit level — dot is centred
2. **Pick it up:** Hold the base in your hand. Platform auto-levels — cup stays flat. Spirit level dot stays centred even as your hand moves
3. **Tilt test:** Deliberately tilt your hand left, right, forward, back. Servo arrows move opposite — cup stays level
4. **Tremor simulation:** Shake your hand gently. Show the OLED waveform mode — raw tremor line is shaky, compensated line is flat. "78% tremor reduction"
5. **Walk test:** Walk across the room holding it. Cup stays level, no spilling
6. **Judge tries it:** Hand it to a judge. They feel the servos fighting to keep it level. Immediate understanding

### Scoring

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | Parkinson's + essential tremor + elderly + surgical precision — massive affected population, deeply emotional, real daily impact |
| Live Demo (25) | **24** | Cup of water stays level while you shake your hand. Judge tries it themselves. OLED shows quantified tremor reduction. Three demo moments |
| Technical (20) | **19** | Complementary filter, PID control loop, 100Hz sampling, wireless streaming, real-time servo compensation, 4ms latency budget |
| Innovation (15) | **14** | "Noise cancelling for physical movement" — reframing a known concept (gimbal) as medical assistive technology with clinical metrics |
| Docs (10) | **9** | PID diagrams, control loop flowchart, signal processing visualisation, mechanical assembly drawing |
| **Total** | **95** | |

**Risk:** MG90S servos can't cancel high-frequency tremors (>6Hz). Mitigate: focus demo on slow/medium tremor and postural instability (most common clinical need). Show the percentage improvement, not perfection. Frame as "proof of concept — production version uses faster actuators."

---

## 3. Wireless Braille Letter Display

**Theme:** Assistive Technology
**One-liner:** One Pico reads joystick input to select characters, wirelessly sends them to a second Pico that actuates servos to physically raise/lower pins in a Braille cell pattern.

| Pico A (Input) | Pico B (Display) |
|---|---|
| Joystick — character selection | PCA9685 + 6 MG90S servos — each servo raises one Braille dot |
| OLED — shows selected character | nRF24L01+ RX |
| nRF24L01+ TX | |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **27** | Visually impaired users, communication tool — strong social impact narrative |
| Live Demo (25) | **23** | Select a letter → watch pins physically move. Tangible and easy to understand |
| Technical (20) | **16** | Simpler firmware than IMU-based ideas, but mechanical precision of pin positioning is interesting |
| Innovation (15) | **14** | Physical Braille output from hobby servos is creative. Judges haven't seen this from Picos |
| Docs (10) | **9** | Braille encoding table, servo-to-pin mapping |
| **Total** | **89** | |

**Risk:** MG90S is large for Braille pin actuation — need creative mechanical design. Mitigate: use raised pegs/flags instead of tiny dots. "Macro Braille" for learning purposes.

---

## 4. Motion-Mirror Physiotherapy Trainer

**Theme:** Assistive Technology
**One-liner:** Therapist wears IMU, performs rehab exercise. Patient's Pico receives the motion wirelessly and servos replicate it on a physical model arm, showing the target movement to copy.

| Pico A (Therapist) | Pico B (Patient) |
|---|---|
| BMI160 IMU — captures reference motion | PCA9685 + 2-3 MG90S servos — physical model arm |
| nRF24L01+ TX | OLED — rep count, accuracy score |
| | Joystick — patient confirms/pauses |
| | nRF24L01+ RX |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **26** | Rehab is real, but "therapist controls a model arm" is a stretch — real physio uses visual demo |
| Live Demo (25) | **23** | Move your arm → model arm copies. Clear and demonstrable |
| Technical (20) | **17** | Motion recording, playback, wireless streaming, servo interpolation |
| Innovation (15) | **12** | Concept exists in expensive rehab robotics — bringing it to Picos is the creative angle |
| Docs (10) | **8** | Standard architecture |
| **Total** | **86** | |

**Risk:** The "why not just show them?" question from judges. Mitigate: frame as remote physio — therapist and patient not in the same room.

---

## 5. Autonomous Self-Levelling Cargo Platform

**Theme:** Autonomy
**One-liner:** IMU detects tilt on a moving platform, servos auto-correct to keep cargo level. Second Pico wirelessly controls movement direction via joystick and monitors status on OLED.

| Pico A (Remote Control) | Pico B (Platform) |
|---|---|
| Joystick — drive direction | BMI160 IMU — tilt sensing |
| OLED — platform tilt, cargo status | PCA9685 + 3 MG90S servos — levelling actuators |
| nRF24L01+ TX | nRF24L01+ RX |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **23** | Use case: drone delivery, rough-terrain transport. Valid but less emotionally compelling |
| Live Demo (25) | **24** | Tilt the platform → it corrects itself. Very visual, easy to test live |
| Technical (20) | **19** | PID control loop, real-time IMU fusion, autonomous correction + remote override |
| Innovation (15) | **13** | Self-levelling is well-known in gimbals, but a cargo platform with remote control adds a twist |
| Docs (10) | **9** | Control diagrams, PID tuning |
| **Total** | **88** | |

**Risk:** Weaker problem definition score. Mitigate: frame as medical supply delivery over rough terrain.

---

## 6. Wireless Conductor's Baton → Percussion Orchestra

**Theme:** Interactive Play
**One-liner:** Wave a wand (IMU) to conduct a physical percussion orchestra — servos strike different instruments based on gesture direction and speed.

| Pico A (Baton) | Pico B (Orchestra) |
|---|---|
| BMI160 IMU — gesture recognition | PCA9685 + 4-6 MG90S servos — striker arms |
| Joystick — tempo/volume | OLED — current tempo, instrument selection |
| nRF24L01+ TX | nRF24L01+ RX |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **20** | "Fun" is a weak problem statement. Music therapy or accessibility angle helps |
| Live Demo (25) | **25** | The best demo of all — judge waves wand, instruments play. Pure spectacle |
| Technical (20) | **17** | Gesture classification, beat detection, servo timing synchronisation |
| Innovation (15) | **15** | Most creative idea on the list. Nobody else will build this. Judges remember it |
| Docs (10) | **9** | Gesture mapping diagrams |
| **Total** | **86** | |

**Risk:** Problem definition is the weakest category. Mitigate: frame as music therapy for motor-impaired patients who can't hold instruments.

---

## 7. Fall Detection & Emergency Alert System

**Theme:** Assistive Technology
**One-liner:** Wearable IMU detects falls in elderly users, wirelessly triggers a base station that activates physical alarms (servo-driven flag, LED, OLED alert) and logs events.

| Pico A (Wearable) | Pico B (Base Station) |
|---|---|
| BMI160 IMU — fall detection algorithm | OLED — alert status, fall history |
| nRF24L01+ TX | Servo — raises physical alert flag |
| | LEDs — visual alarm |
| | nRF24L01+ RX |

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | Elderly falls — real, deadly problem. Very strong narrative |
| Live Demo (25) | **20** | Drop/shake the wearable → alarm triggers. Works but less interactive |
| Technical (20) | **15** | Fall detection algorithm (threshold + freefall pattern), wireless alert — simpler than servo-heavy builds |
| Innovation (15) | **10** | Concept exists commercially. Innovation is limited — execution must be polished |
| Docs (10) | **9** | Algorithm flowchart, detection accuracy stats |
| **Total** | **83** | |

**Risk:** Low innovation score. Commercial products already do this. Mitigate: add unique features like fall direction analysis on OLED.

---

## 8. Silent Distress Signal (Dual-Input)

**Theme:** Assistive Technology
**One-liner:** Wearable detects the "Signal for Help" hand gesture via IMU OR a secret joystick code, wirelessly triggers a silent alert at a hidden base station — for domestic violence victims who can't call for help.

| Pico A (Wearable/Portable) | Pico B (Base Station) |
|---|---|
| BMI160 IMU — gesture detection (Signal for Help) | OLED — alert status, trigger method, event log |
| Joystick — secret directional code (pocket mode) | PCA9685 + servo — raises physical alert flag |
| LED — subtle confirmation blink | LEDs — silent visual alarm |
| nRF24L01+ TX | nRF24L01+ RX |

**Two trigger paths:**
- IMU gesture: Hand up → thumb tuck → fist close (3-phase state machine)
- Joystick code: Secret directional sequence e.g. Left-Right-Left (pocket/hidden use)
- Either input fires the same silent alert

**Joystick can also encode severity:**
- Up-Up-Down = "I need help"
- Down-Down-Down = "Emergency — come now"
- Left-Right-Left = "I'm safe, cancel alert"

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | Domestic violence — documented, urgent. Signal for Help already globally recognised |
| Live Demo (25) | **24** | Gesture → silent alert fires. Then "what if hands aren't free?" → pocket code → fires again. Two dramatic moments |
| Technical (20) | **18** | IMU state machine + joystick sequence matcher + wireless protocol + heartbeat monitoring + false-positive filtering |
| Innovation (15) | **14** | Making a known hand signal machine-detectable with IMU is novel. Dual-input is unique |
| Docs (10) | **9** | State machine diagrams, gesture signatures, architecture |
| **Total** | **94** | |

**Risk:** Gesture recognition accuracy with IMU alone (no camera). Mitigate: tune thresholds carefully, demonstrate false-positive rejection live.

---

## 9. Fire Escape Direction Finder (Extra: 2x DHT22 + buzzer)

**Theme:** Assistive Technology / Autonomy
**One-liner:** Sensor node detects fire via temperature, wirelessly guides a handheld device to point users AWAY from danger using RSSI signal strength — autonomous directional guidance in zero-visibility smoke.

**The Problem:** 3,500+ fire deaths per year in the US. 75% from smoke inhalation. #1 cause: disorientation — people run the wrong way. Fire alarms tell you there's fire but NOT which direction is safe. Zero devices solve this.

**End Users:** Hospital patients (bedridden, wheelchair), elderly/care home residents, visually impaired, school children, factory workers — anyone who cannot self-navigate in smoke.

| Pico A — Sensor Node (fixed near corridor) | Pico B — Handheld Escape Guide (user carries) |
|---|---|
| DHT22 #1 + #2 — temperature at two points | nRF24L01+ RX — receives packets + measures RSSI |
| nRF24L01+ TX — broadcasts temp data @ 200ms | BMI160 IMU — heading tracking + fall detection |
| LED — hazard indicator | OLED — "GO LEFT", "KEEP GOING", "TURN AROUND" |
| | PCA9685 + servo — physical arrow points away from danger |
| | Buzzer — slow beep (safe direction) / fast beep (danger) |
| | Joystick — acknowledge / silence alarm |
| | LEDs — green (safe) / red (danger) |

**How location works (without GPS):**
- NOT "where is the exit" — instead "which direction is dangerous"
- RSSI increasing = user walking TOWARD fire → "TURN AROUND"
- RSSI decreasing = user walking AWAY from fire → "KEEP GOING"
- Temperature from sensor confirms real fire (not false alarm)
- IMU tracks heading direction for consistent arrow pointing

**Autonomous decision logic (every 200ms):**
1. Receive nRF24L01+ packet from sensor node
2. Measure RSSI (signal strength = distance proxy)
3. Compare RSSI to previous reading
4. RSSI rising + temp high → DANGER: servo points back, fast buzzer
5. RSSI falling + temp high → SAFE: servo points forward, slow buzzer
6. No packet received → OUT OF RANGE (far from hazard = safe)
7. IMU detects freefall → SOS MODE: rapid buzzer, OLED "PERSON DOWN"

**Scalability (tell judges):** One sensor node proves the concept. In production, sensor nodes at every corridor junction — handheld listens to all via nRF24L01+ multi-pipe (supports 6 nodes simultaneously). Triangulation from multiple RSSI readings gives true directional guidance.

**Extra components needed:** 2x DHT22 temperature sensor (~£6), 1x buzzer (~£0.50)

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **28** | Life-or-death problem. Clear end users (hospital, elderly, visually impaired). Gap in market — no existing device does directional guidance |
| Live Demo (25) | **23** | Heat sensor → walk away (safe beep) → walk toward (danger beep) → drop device (SOS). Four demo moments |
| Technical (20) | **19** | RSSI trending, autonomous decision loop, PID-style servo control, dual-core (main loop + fall detection), multi-pipe protocol |
| Innovation (15) | **14** | Using RSSI as proximity-to-danger metric is novel. Most fire safety = alarms, not guidance |
| Docs (10) | **9** | Architecture diagram, flowchart, spatial data flow, RSSI zone map — visually rich |
| **Total** | **93** | |

**Risk:** RSSI is noisy — needs moving average smoothing. Single sensor node gives toward/away only, not left/right. Mitigate: average over 5 readings, frame as "proof of concept that scales."

---

## 10. Elderly Fall Detection & Emergency Response System

**Theme:** Assistive Technology / Autonomy
**One-liner:** Wearable IMU detects falls in elderly users using a multi-phase detection algorithm, wirelessly triggers an autonomous emergency response at a base station — physical alarm, event logging, and caregiver alert.

**The Problem:** Falls are the #1 cause of injury death in adults over 65. 1 in 4 elderly people fall each year. 37% of falls happen when the person is alone. After a fall, the time spent on the ground before help arrives directly correlates with mortality — every minute counts.

**End Users:** Elderly people living alone, care home residents, post-surgery patients, people with mobility impairments, Parkinson's patients (high fall risk).

| Pico A — Wearable (on belt/wrist) | Pico B — Base Station (in home/room) |
|---|---|
| BMI160 IMU — 6-axis fall detection algorithm | nRF24L01+ RX — receives alerts + heartbeat |
| nRF24L01+ TX — sends alerts + heartbeat @ 1Hz | OLED — alert status, fall history log, time since last movement |
| Joystick — "I'm OK" cancel button / manual SOS | PCA9685 + servo — raises physical RED alert flag |
| LED — subtle status blink (green = OK, red = alert sent) | LEDs — flashing red alarm pattern |
| | Buzzer — audio alarm (escalating) |

**Multi-phase fall detection algorithm:**
1. **Freefall phase** — accelerometer reads near 0g (body falling, ~0.3-0.5s)
2. **Impact phase** — sudden spike >3g (hitting the ground)
3. **Immobility phase** — no significant movement for 10 seconds after impact
4. All three phases must occur in sequence within a time window → confirmed fall
5. Single impacts (bumping table) or freefall alone (jumping) → NOT a fall

**Autonomous response sequence:**
1. Fall detected → wearable sends ALERT packet wirelessly
2. Wearable LED turns red, gives user 15-second window to press joystick "I'm OK"
3. If no cancel → base station activates:
   - OLED: "FALL DETECTED" + timestamp
   - Servo raises physical red flag (visible from across room)
   - LED array: flashing red
   - Buzzer: escalating pattern (quiet → loud over 30s)
4. Base station logs event with timestamp to internal memory
5. If wearable heartbeat stops (out of range / battery dead) → base station shows "WEARABLE DISCONNECTED" warning

**Heartbeat system:**
- Wearable sends heartbeat packet every 1 second
- Base station tracks last heartbeat time
- No heartbeat for 30s → "CONNECTION LOST" on OLED — this itself is an alert (user may have left range or device failed)

**Activity monitoring (bonus feature):**
- IMU step counter tracks daily activity
- Joystick on base station scrolls through: today's steps, last fall time, hours since last movement
- OLED shows: "Steps today: 342 | Last fall: none | Active: 2h ago"

**Extra components needed:** 1x buzzer (~£0.50) — everything else is in the kit

| Category | Score | Why |
|---|---|---|
| Problem Fit (30) | **29** | #1 injury killer in elderly. "Every minute on the ground matters." Universal, emotional, backed by statistics |
| Live Demo (25) | **22** | Drop/shake wearable → alarm fires. Press "I'm OK" → cancels. Show heartbeat loss. Clear but less interactive than other ideas |
| Technical (20) | **18** | Multi-phase detection algorithm (freefall→impact→immobility), false-positive rejection, heartbeat protocol, escalating alarm, event logging |
| Innovation (15) | **11** | Commercial products exist (Life Alert, Apple Watch). Innovation angle: multi-phase algorithm + physical flag alert + heartbeat monitoring on a £4 Pico |
| Docs (10) | **9** | Algorithm flowchart, detection phases diagram, false positive analysis |
| **Total** | **89** | |

**Risk:** Lower innovation score — judges may say "Apple Watch does this." Counter: "Apple Watch costs £400 and needs cellular. This is a £15 standalone system for care homes in developing countries where smartphones aren't available. And it has a physical flag alert that works without anyone checking a phone."

---

## Summary Ranking

| Rank | Idea | Total | Best For | Weakest Area |
|------|------|-------|----------|--------------|
| **1** | **Tremor-Stabilising "SteadyHand"** | **95** | Problem Fit (29) + Technical (19) + Demo (24) | — |
| **2** | **Silent Distress Signal** | **94** | Problem Fit (29) — domestic violence | Innovation (14) |
| **3** | **Fire Escape Direction Finder** | **93** | Technical (19) — RSSI + autonomous logic | Demo (23) — needs temp trigger |
| 4 | Gesture-Controlled Gripper Arm | **91** | Demo (24) — judge wears the glove | Innovation (12) |
| 5 | Elderly Fall Detection | **89** | Problem Fit (29) — #1 elderly killer | Innovation (11) — products exist |
| 5 | Wireless Braille Display | **89** | Innovation (14) — unique servo use | Technical (16) |
| 7 | Self-Levelling Cargo Platform | **88** | Demo (24) — self-correcting | Problem Fit (23) |
| 8 | Conductor's Baton Orchestra | **86** | Innovation (15) — most creative | Problem Fit (20) |
| 8 | Motion-Mirror Physio Trainer | **86** | Problem Fit (26) — rehab | Innovation (12) |
| 10 | Fall Detection (basic) | **83** | Problem Fit (29) | Innovation (10) |

---

*Pick based on: what excites you, what you can physically build, and what story you want to tell judges.*
