# GridBox — Smart Energy Recycling & Microgrid System

> "Waste energy in, useful power out — monitored, managed, and intelligent"

**Theme:** Sustainability + Autonomy
**Score: 96/100**

---

## The Big Idea

Energy is wasted everywhere — vibrations from machines, heat from engines, motion from doors closing, kinetic energy from footsteps. What if we could **capture that wasted energy, convert it into useful power, and intelligently distribute it?**

GridBox is a miniature smart grid that demonstrates this entire cycle:

```mermaid
graph LR
    WASTE["WASTED ENERGY<br/>Vibration, motion,<br/>mechanical waste"] -->|"DC motor<br/>as generator"| CAPTURE["ENERGY CAPTURE<br/>Motor converts<br/>motion → electricity"]
    CAPTURE -->|"buck converter<br/>regulates voltage"| STORE["POWER BUS<br/>Regulated, stable<br/>usable power"]
    STORE -->|"smart distribution"| USE["USEFUL LOADS<br/>LEDs, sensors,<br/>charging, alerts"]
    USE -->|"monitoring"| BRAIN["PICO BRAIN<br/>Measures, decides,<br/>optimises, reports"]
    BRAIN -->|"controls"| STORE

    style WASTE fill:#e74c3c,color:#fff
    style CAPTURE fill:#f39c12,color:#fff
    style STORE fill:#3498db,color:#fff
    style USE fill:#27ae60,color:#fff
    style BRAIN fill:#9b59b6,color:#fff
```

---

## The Problem

| Fact | Detail |
|---|---|
| **68%** | of energy produced globally is WASTED as heat, vibration, or friction |
| **$150 billion** | lost annually from industrial energy waste in the US alone |
| **Zero monitoring** | most small-scale energy systems have no smart management |
| **Grid blackouts** | caused by demand exceeding supply — preventable with smart load shedding |
| **Renewable variability** | wind/solar output changes constantly — needs intelligent grid management |

**The gap:** We have smart home devices but **no cheap, intelligent energy management system** that can capture waste energy, monitor production, and autonomously distribute power where it's needed.

---

## Where Does the Recycled Energy Come From?

DC motors run backwards are generators. In the real world, these energy sources are being wasted:

```mermaid
mindmap
  root((Wasted Energy<br/>Sources))
    Industrial
      Machine vibrations
        Motors, pumps, compressors
        Constant mechanical waste
      Conveyor belt motion
        Braking energy lost as heat
      Exhaust gas heat
        Captured via thermoelectric
    Building
      Door closing energy
        Millions of door cycles per day
      Elevator braking
        Descending elevator = free energy
      HVAC airflow
        Fan motion wasted at exhaust
      Footstep energy
        Piezoelectric floor tiles
    Transport
      Vehicle braking
        Regenerative braking in EVs
      Train deceleration
        Massive kinetic energy wasted
      Speed bumps
        Cars push down = energy capture
    Environment
      Wind
        Micro wind turbines
      Water flow
        Micro hydro in pipes
      Solar
        Variable but free
      Vibration from traffic
        Bridges, roads vibrate constantly
```

### Our Demo: Three Energy Sources (using DC motors)

| Source | How We Model It | Real-World Equivalent |
|---|---|---|
| **Motor 1: Wind Turbine** | Spin motor shaft by hand or with fan | Wind farm capturing wind energy |
| **Motor 2: Vibration Harvester** | Motor attached to vibrating surface (tap table) | Factory machine vibration capture |
| **Potentiometer: Solar Panel** | Turn dial to simulate variable solar output | Solar irradiance changing with clouds |

---

## Where Does the Recycled Energy Go?

```mermaid
graph LR
    subgraph SOURCES["ENERGY SOURCES"]
        S1["Motor 1: Wind<br/>(spin = generate)"]
        S2["Motor 2: Vibration<br/>(shake = generate)"]
        S3["Potentiometer: Solar<br/>(dial = variable output)"]
    end

    subgraph GRID["SMART GRID (Pico A manages)"]
        BUS["Power Bus"]
        BUCK["Buck Converter<br/>Regulates to 3.3V/5V"]
        MONITOR["Voltage monitoring<br/>(ADC pins)"]
        BREAKERS["Servo circuit breakers<br/>(connect/disconnect)"]
    end

    subgraph LOADS["USEFUL LOADS (priority order)"]
        L1["PRIORITY 1: Emergency LED<br/>'Hospital' — never disconnected"]
        L2["PRIORITY 2: Sensor power<br/>'Water treatment plant'<br/>IMU monitors pipeline vibration"]
        L3["PRIORITY 3: Comfort LED<br/>'Street lighting'<br/>First to shed if power low"]
        L4["PRIORITY 4: Charging<br/>'EV charging station'<br/>Only when surplus power"]
    end

    S1 --> BUS
    S2 --> BUS
    S3 --> BUS
    BUS --> BUCK --> BREAKERS
    BREAKERS --> L1
    BREAKERS --> L2
    BREAKERS --> L3
    BREAKERS --> L4
    MONITOR --> GRID

    style SOURCES fill:#f39c12,color:#fff
    style GRID fill:#e74c3c,color:#fff
    style LOADS fill:#27ae60,color:#fff
```

### Load Priority System

```mermaid
flowchart LR
    MEASURE["Measure total generated power<br/>(ADC reads bus voltage)"] --> COMPARE{"Power vs Demand?"}

    COMPARE -->|"Surplus > 20%"| ALL_ON["ALL LOADS ON<br/>+ charge battery bank<br/>OLED: 'SURPLUS — STORING'<br/>LED 4 ON (EV charging)"]

    COMPARE -->|"Balanced ±20%"| NORMAL["PRIORITY 1-3 ON<br/>Charging OFF<br/>OLED: 'NORMAL'<br/>All essential loads powered"]

    COMPARE -->|"Deficit 10-30%"| SHED1["SHED PRIORITY 4+3<br/>Street lights + charging OFF<br/>OLED: 'LOAD SHEDDING L1'<br/>Servo disconnects LED 3+4"]

    COMPARE -->|"Critical deficit > 30%"| SHED2["EMERGENCY<br/>Only PRIORITY 1 stays ON<br/>Hospital LED only<br/>OLED: 'EMERGENCY POWER'<br/>Servos disconnect everything else"]

    ALL_ON --> MEASURE
    NORMAL --> MEASURE
    SHED1 --> MEASURE
    SHED2 --> MEASURE

    style ALL_ON fill:#27ae60,color:#fff
    style NORMAL fill:#3498db,color:#fff
    style SHED1 fill:#e67e22,color:#fff
    style SHED2 fill:#e74c3c,color:#fff
```

---

## System Architecture

```mermaid
graph LR
    subgraph PICO_A["PICO A — Grid Controller (the brain)"]
        ADC_V["ADC: Bus voltage measurement<br/>Reads power from each generator"]
        ADC_POT["ADC: Potentiometer<br/>Solar simulation / load demand"]
        IMU_A["BMI160 IMU<br/>Generator vibration monitoring<br/>Fault detection"]
        PCA_A["PCA9685 + 2x Servo<br/>Circuit breakers<br/>Connect/disconnect loads"]
        MOTOR_A["DC Motors × 2<br/>Used as GENERATORS<br/>Spin = generate power"]
        NRF_A["nRF24L01+ TX<br/>Sends telemetry to control centre"]
        LED_LOADS["LEDs × 4<br/>Represent consumer loads<br/>(house, factory, street, charging)"]
    end

    subgraph PICO_B["PICO B — SCADA Control Centre"]
        OLED_B["OLED 0.96&quot;<br/>Grid dashboard<br/>Voltage, loads, status, history"]
        JOY_B["Joystick<br/>Manual breaker override<br/>Scroll through views"]
        POT_B["Potentiometer<br/>Set demand threshold<br/>Adjust load shedding sensitivity"]
        NRF_B["nRF24L01+ RX<br/>Receives grid telemetry"]
        LED_B["LEDs<br/>Grid status indicators<br/>Green=normal Yellow=warning Red=emergency"]
    end

    PICO_A -->|"wireless 50Hz<br/>telemetry stream"| PICO_B

    style PICO_A fill:#e74c3c,color:#fff,stroke-width:2px
    style PICO_B fill:#3498db,color:#fff,stroke-width:2px
```

---

## Fault Detection (IMU as Vibration Monitor)

Real power plants monitor generator vibration to detect faults. We do the same:

```mermaid
stateDiagram-v2
    [*] --> HEALTHY: IMU reads vibration < 1g

    HEALTHY: GENERATOR HEALTHY
    HEALTHY: Normal vibration levels
    HEALTHY: OLED: "GEN 1: OK"

    HEALTHY --> WARNING: vibration 1-2g

    WARNING: VIBRATION WARNING
    WARNING: Possible bearing wear
    WARNING: OLED: "GEN 1: WARNING"
    WARNING: LED: yellow

    WARNING --> HEALTHY: vibration drops < 1g

    WARNING --> FAULT: vibration > 2g sustained 3s

    FAULT: GENERATOR FAULT
    FAULT: Servo disconnects generator
    FAULT: Switch to backup generator
    FAULT: OLED: "GEN 1: FAULT — DISCONNECTED"
    FAULT: LED: red
    FAULT: Alert sent to control centre

    FAULT --> HEALTHY: Manual reset via joystick
```

---

## OLED SCADA Dashboard Views

### View 1: Live Grid Status (default)

```
┌──────────────────────────┐
│  GRIDBOX SCADA    [LIVE] │
│                          │
│  GEN 1 (WIND):  4.2V ON │
│  ████████████░░░░  78%   │
│  GEN 2 (VIBR):  1.8V ON │
│  █████░░░░░░░░░░░  33%   │
│  SOLAR SIM:      3.1V   │
│  ██████████░░░░░░  57%   │
│                          │
│  BUS: 3.8V  STATUS: OK  │
└──────────────────────────┘
```

### View 2: Load Management

```
┌──────────────────────────┐
│  LOAD STATUS             │
│                          │
│  P1 Hospital:   ON  ██  │
│  P2 Sensor:     ON  ██  │
│  P3 Street:     OFF ░░  │
│  P4 Charging:   OFF ░░  │
│                          │
│  DEMAND: 72%   GEN: 58% │
│  MODE: LOAD SHEDDING L1 │
└──────────────────────────┘
```

### View 3: Generator Health

```
┌──────────────────────────┐
│  GENERATOR HEALTH        │
│                          │
│  GEN 1 Vibration:        │
│  ∿∿∿∿∿∿∿∿∿∿  0.3g OK   │
│                          │
│  GEN 2 Vibration:        │
│  ∿∿╲╱∿∿∿∿∿∿  0.8g WARN │
│                          │
│  Uptime: 00:14:32        │
│  Faults today: 0         │
└──────────────────────────┘
```

### View 4: Energy Summary

```
┌──────────────────────────┐
│  ENERGY SUMMARY          │
│                          │
│  Generated:    48.2 mWh  │
│  Consumed:     31.7 mWh  │
│  Efficiency:   65.8%     │
│  Peak gen:     5.1V      │
│  Lowest bus:   2.8V      │
│  Shed events:  3         │
│                          │
│  STATUS: SUSTAINABLE     │
└──────────────────────────┘
```

Joystick up/down scrolls between views.

---

## Real-World Applications

```mermaid
graph LR
    GRIDBOX["GridBox Core Technology<br/>Capture → Convert → Monitor → Distribute"] --> APP1["REMOTE VILLAGES<br/>Micro wind/hydro → powers<br/>medical fridge, phone charging,<br/>LED lighting<br/>Smart load shedding protects<br/>critical loads (vaccine storage)"]

    GRIDBOX --> APP2["FACTORY ENERGY RECYCLING<br/>Machine vibrations → captured<br/>Powers sensors, monitoring<br/>Reduces energy bill<br/>Detects machine faults early<br/>via vibration monitoring"]

    GRIDBOX --> APP3["SMART BUILDING<br/>Elevator braking, door closing,<br/>HVAC airflow → captured<br/>Powers emergency lighting,<br/>sensors, IoT devices<br/>Building becomes self-monitoring"]

    GRIDBOX --> APP4["DISASTER RELIEF<br/>No grid available<br/>Hand-crank generator<br/>Smart distribution ensures<br/>medical equipment powered first<br/>Communication radio second"]

    GRIDBOX --> APP5["EV CHARGING MANAGEMENT<br/>Solar + wind variable input<br/>Multiple vehicles need charging<br/>Smart scheduling based on<br/>available power + priority<br/>Grid doesn't overload"]

    GRIDBOX --> APP6["DEVELOPING COUNTRIES<br/>Unreliable grid + frequent outages<br/>Local generation + smart management<br/>Essential services stay powered<br/>£15 per installation<br/>Massive scalability"]

    style GRIDBOX fill:#f39c12,color:#fff,stroke-width:3px
    style APP1 fill:#e74c3c,color:#fff
    style APP2 fill:#3498db,color:#fff
    style APP3 fill:#27ae60,color:#fff
    style APP4 fill:#9b59b6,color:#fff
    style APP5 fill:#e67e22,color:#fff
    style APP6 fill:#1abc9c,color:#fff
```

---

## The Energy Cycle — From Waste to Useful

```mermaid
graph LR
    subgraph WASTE["WASTE ENERGY"]
        W1["Factory machine<br/>vibrating"]
        W2["Wind blowing<br/>doing nothing"]
        W3["Door closing<br/>energy lost"]
    end

    subgraph CAPTURE["ENERGY CAPTURE"]
        C1["DC motor on machine<br/>vibration → voltage"]
        C2["DC motor with fan blade<br/>wind → voltage"]
        C3["DC motor on door hinge<br/>motion → voltage"]
    end

    subgraph CONVERT["CONVERSION"]
        BUCK_C["Buck converter<br/>Raw voltage → stable 3.3V/5V"]
    end

    subgraph USE_POWER["WHAT THE RECYCLED ENERGY POWERS"]
        U1["Emergency lighting<br/>when grid fails"]
        U2["IoT sensors<br/>temperature, humidity,<br/>vibration monitoring"]
        U3["Communication<br/>wireless alerts,<br/>status reporting"]
        U4["Phone charging<br/>in remote areas"]
        U5["Medical equipment<br/>vaccine fridge in<br/>off-grid clinic"]
    end

    W1 --> C1
    W2 --> C2
    W3 --> C3
    C1 --> BUCK_C
    C2 --> BUCK_C
    C3 --> BUCK_C
    BUCK_C --> U1
    BUCK_C --> U2
    BUCK_C --> U3
    BUCK_C --> U4
    BUCK_C --> U5

    style WASTE fill:#e74c3c,color:#fff
    style CAPTURE fill:#f39c12,color:#fff
    style CONVERT fill:#3498db,color:#fff
    style USE_POWER fill:#27ae60,color:#fff
```

---

## Physical Build

```mermaid
graph LR
    subgraph BOX["GRIDBOX — Physical Layout"]
        subgraph GEN_AREA["Left: Generation"]
            M1["DC Motor 1<br/>with fan blade or crank<br/>'Wind Turbine'"]
            M2["DC Motor 2<br/>on vibrating mount<br/>'Vibration Harvester'"]
            POT_SOLAR["Potentiometer<br/>'Solar Panel Simulator'"]
        end

        subgraph GRID_AREA["Centre: Grid Infrastructure"]
            BREAD["Breadboard<br/>Power bus rails"]
            SRV1["Servo 1: Breaker Gen1"]
            SRV2["Servo 2: Breaker Gen2"]
            BUCK_B["Buck converter<br/>Voltage regulation"]
            PICO_MAIN["Pico A<br/>+ PCA9685<br/>+ nRF24L01+<br/>+ BMI160 on Motor 1"]
        end

        subgraph LOAD_AREA["Right: Consumer Loads"]
            LED_H["LED: Hospital (P1)"]
            LED_F["LED: Factory (P2)"]
            LED_S["LED: Street (P3)"]
            LED_C["LED: Charging (P4)"]
        end
    end

    subgraph CONTROL_UNIT["SCADA Control Centre (separate)"]
        PICO_B_U["Pico B + OLED<br/>+ Joystick + Pot<br/>+ nRF24L01+"]
    end

    BOX -->|"wireless"| CONTROL_UNIT

    style GEN_AREA fill:#f39c12,color:#fff
    style GRID_AREA fill:#e74c3c,color:#fff
    style LOAD_AREA fill:#27ae60,color:#fff
    style CONTROL_UNIT fill:#3498db,color:#fff
```

### Materials (Kit Only)

| Part | Kit Item | Grid Equivalent |
|---|---|---|
| 2x DC motors | Provided | Generators |
| 2x MG90S servos | Provided | Circuit breakers |
| Potentiometer | Provided | Solar simulator / demand dial |
| BMI160 IMU | Provided | Vibration monitor |
| Buck converter | Provided | Transformer |
| 4x LEDs | From components kit | Consumer loads |
| Breadboard | Provided | Power bus |
| Pico 2 × 2 | Provided | Grid controller + SCADA |
| nRF24L01+ × 2 | Provided | Telemetry link |
| OLED | Provided | SCADA dashboard |
| Joystick | Provided | Operator console |
| Wire + resistors | Provided | Wiring infrastructure |

**No extra components needed. Everything from the kit.**

---

## Demo Script

```mermaid
graph LR
    D1["1. SHOW THE BOX<br/>'This is a miniature<br/>smart power grid'"] --> D2["2. SPIN MOTOR 1<br/>LEDs light up<br/>'You're generating<br/>electricity right now'"]
    D2 --> D3["3. ALL LOADS ON<br/>OLED: 'NORMAL'<br/>'Grid is healthy,<br/>all loads powered'"]
    D3 --> D4["4. STOP SPINNING<br/>Voltage drops<br/>Servo CLICKS<br/>Factory LED goes OFF"]
    D4 --> D5["5. LOAD SHEDDING<br/>OLED: 'EMERGENCY'<br/>'Hospital stays on.<br/>Non-essential shed.'"]
    D5 --> D6["6. SPIN AGAIN<br/>Voltage recovers<br/>Servo reconnects<br/>All loads back ON"]

    style D1 fill:#3498db,color:#fff
    style D2 fill:#f39c12,color:#fff
    style D3 fill:#27ae60,color:#fff
    style D4 fill:#e74c3c,color:#fff
    style D5 fill:#e74c3c,color:#fff
    style D6 fill:#27ae60,color:#fff
```

```mermaid
graph LR
    D7["7. SHAKE MOTOR 1<br/>'Generator fault!'<br/>IMU detects vibration"] --> D8["8. AUTO DISCONNECT<br/>Servo disconnects Gen 1<br/>Switches to Gen 2<br/>'Fault isolation'"]
    D8 --> D9["9. SHOW DASHBOARD<br/>Control centre OLED<br/>4 views: status,<br/>loads, health, summary"]
    D9 --> D10["10. THE PITCH<br/>'68% of energy is wasted.<br/>GridBox captures it,<br/>manages it, and keeps<br/>critical systems alive.<br/>£15. No cloud needed.'"]

    style D7 fill:#e67e22,color:#fff
    style D8 fill:#9b59b6,color:#fff
    style D9 fill:#3498db,color:#fff
    style D10 fill:#27ae60,color:#fff
```

---

## Scoring Breakdown

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **28** | 68% energy wasted globally. Smart grid is £50B market. Developing countries need cheap grid management. Disaster relief needs priority power. Real, massive, urgent |
| **Live Demo (25)** | **25** | Spin motor → lights on. Stop → auto load shedding. Shake → fault detection. Judge physically generates power. Three visible autonomous actions |
| **Technical (20)** | **20** | ADC voltage measurement, IMU vibration analysis, autonomous load shedding algorithm, servo breaker actuation, wireless SCADA telemetry, priority scheduling, fault detection state machine |
| **Innovation (15)** | **14** | Nobody builds a smart grid at a hackathon. DC motor as generator is clever. Vibration-based fault detection is industrial-grade thinking. ARM judges will recognise this as their IoT market |
| **Docs (10)** | **9** | Grid topology diagrams, SCADA screenshots, power flow, fault detection state machine, energy cycle |
| **Total** | **96** | |

---

## Why ARM Judges Love This

ARM makes chips for:
- **Smart meters** — GridBox IS a smart meter
- **Industrial IoT** — vibration monitoring IS industrial IoT
- **Grid infrastructure** — load management IS grid infrastructure
- **Edge computing** — autonomous decisions at the device IS edge AI

You're building a demo of ARM's own target market. On their chips. At their hackathon.

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| DC motor generates too little voltage | Use buck converter to step up. Or spin faster. Even 1-2V is measurable by ADC |
| ADC can't distinguish generators | Use separate ADC channels — GP26 for Gen1, GP27 for Gen2, GP28 for solar pot |
| Servo breakers don't actually cut power | Wire servo arm to push a physical switch, or use servo to move a wire jumper on/off the breadboard rail |
| "This is just LEDs turning on and off" | The AUTONOMOUS decision-making is the product, not the LEDs. Emphasise the SCADA dashboard and fault detection |
| Judges don't understand power grids | Lead with the physical demo (spin → lights). Then explain the intelligence behind it. Make it tangible first, technical second |

---

## Build Timeline

```mermaid
gantt
    title GridBox — 12 Hour Build Plan
    dateFormat HH:mm
    axisFormat %H:%M

    section Critical Path
    nRF24L01+ wireless link              :crit, 00:00, 1h
    ADC voltage reading from motors      :crit, 01:00, 1h
    Servo breaker control via PCA9685    :crit, 02:00, 1h
    Basic load shedding algorithm        :crit, 03:00, 1h

    section Grid Intelligence
    IMU vibration monitoring             :04:00, 1h
    Fault detection state machine        :05:00, 1h
    Priority-based load scheduling       :06:00, 1h

    section Display
    OLED SCADA dashboard (4 views)       :07:00, 1h30min
    Joystick navigation + manual override:08:30, 30min

    section Physical Build
    Wire generators + loads + bus        :04:00, 1h30min
    Servo breaker mechanism              :05:30, 30min
    Mount IMU on generator               :06:00, 15min

    section Polish
    Energy accounting (mWh tracking)     :09:00, 1h
    Documentation + diagrams             :10:00, 1h
    Demo practice                        :11:00, 1h
```

---

## Future Vision (Tell Judges)

> "68% of global energy is wasted. Not because we can't capture it — but because we can't MANAGE it intelligently at the point of generation.
>
> GridBox is a smart energy management system that costs £15 and needs no cloud, no internet, no subscription. It captures waste energy from vibrations, motion, and wind. It converts it to usable power. It autonomously decides which loads to power and which to shed. It detects generator faults before they cause outages.
>
> Put one in a remote village — it keeps the vaccine fridge running when the wind stops. Put one in a factory — it captures machine vibrations and uses them to power its own monitoring sensors. Put one in a disaster zone — hand-crank the generator and the system ensures the radio stays on.
>
> Smart grid infrastructure shouldn't cost millions. It should cost £15 and fit in a box. That's GridBox."
