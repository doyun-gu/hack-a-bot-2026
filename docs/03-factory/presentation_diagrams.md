# Presentation Diagrams (Mermaid)

> Render on GitHub or paste into [mermaid.live](https://mermaid.live) → screenshot for PPT.

---

## 1. System Architecture (Full)

```mermaid
graph LR
    subgraph PICO_A["PICO A — MASTER (Grid Controller)"]
        direction TB
        A_SPI["SPI0: nRF24L01+<br/>2.4GHz Wireless"]
        A_I2C["I2C0: BMI160 IMU (0x68)<br/>+ PCA9685 PWM (0x40)"]
        A_PCA["PCA9685 Outputs:<br/>CH0: Servo 1 (Valve)<br/>CH1: Servo 2 (Gate)<br/>CH2: Motor 1 (Pump)<br/>CH3: Motor 2 (Conveyor)"]
        A_GPIO["GPIO:<br/>GP13: Recycle Path (2N2222)<br/>GP25: Heartbeat LED"]
        A_ADC["ADC:<br/>GP26: Bus Voltage<br/>GP27: Motor 1 Current<br/>GP28: Motor 2 Current"]
    end

    subgraph PICO_B["PICO B — SLAVE (SCADA Station)"]
        direction TB
        B_SPI0["SPI0: nRF24L01+<br/>2.4GHz Wireless"]
        B_SPI1["SPI1: MAX7219<br/>8-Digit 7-Segment"]
        B_LED["GP25: Heartbeat LED"]
    end

    A_SPI -- "nRF24L01+ PA+LNA<br/>Channel 100 · 250kbps<br/>32-byte packets · 0% error" --> B_SPI0

    subgraph ACTUATORS["Actuators"]
        M1["DC Motor 1<br/>(Pump)"]
        M2["DC Motor 2<br/>(Conveyor)"]
        S1["Servo 1<br/>(Fill Valve)"]
        S2["Servo 2<br/>(Sort Gate)"]
    end

    subgraph POWER["Power"]
        PSU["12V 6A PSU"]
        BUCK["LM2596S → 5V"]
        BOOST["Buck-Boost → 6-9V"]
    end

    A_PCA --> M1
    A_PCA --> M2
    A_PCA --> S1
    A_PCA --> S2

    PSU --> BUCK --> PICO_A
    BUCK --> PICO_B
    PSU --> BOOST --> M1
    BOOST --> M2

    style PICO_A fill:#1a1a2e,color:#fff
    style PICO_B fill:#16213e,color:#fff
    style ACTUATORS fill:#2d6a4f,color:#fff
    style POWER fill:#ff6b35,color:#fff
```

---

## 2. Wireless Protocol — 6 Datagram Types

```mermaid
graph TB
    subgraph TX["Pico A → Pico B (Telemetry)"]
        direction LR
        P1["POWER<br/>Bus V, Motor I,<br/>Total W, Efficiency %"]
        P2["STATUS<br/>State, Fault Source,<br/>IMU RMS, Mode, Uptime"]
        P3["PRODUCTION<br/>Items Count,<br/>Pass/Reject, Belt Speed"]
        P4["HEARTBEAT<br/>Timestamp, CPU Load,<br/>Wireless Reliability"]
        P5["ALERT<br/>Fault Code, Severity,<br/>Affected Subsystem"]
    end

    subgraph RX["Pico B → Pico A (Commands)"]
        C1["COMMAND<br/>Motor Speed, Servo Angle,<br/>Mode Switch, E-Stop"]
    end

    style TX fill:#0f3460,color:#fff
    style RX fill:#533483,color:#fff
    style P1 fill:#e94560,color:#fff
    style P2 fill:#0f3460,color:#fff
    style P3 fill:#533483,color:#fff
    style P4 fill:#1a1a2e,color:#fff
    style P5 fill:#e94560,color:#fff
    style C1 fill:#2d6a4f,color:#fff
```

---

## 3. Packet Structure (32 Bytes)

```mermaid
graph LR
    TYPE["Type<br/>1 byte"] --> SEQ["Sequence<br/>1 byte"] --> TS["Timestamp<br/>2 bytes"] --> PAYLOAD["Payload<br/>24 bytes"] --> CRC["CRC Check<br/>4 bytes"]

    style TYPE fill:#e94560,color:#fff
    style SEQ fill:#533483,color:#fff
    style TS fill:#0f3460,color:#fff
    style PAYLOAD fill:#2d6a4f,color:#fff
    style CRC fill:#e94560,color:#fff
```

---

## 4. Packet Rotation Schedule

```mermaid
graph LR
    R1["POWER"] --> R2["STATUS"] --> R3["POWER"] --> R4["PRODUCTION"]
    R4 --> R5["POWER"] --> R6["STATUS"] --> R7["POWER"] --> R8["HEARTBEAT"]
    R8 --> R1

    ALERT["ALERT<br/>(breaks rotation<br/>on fault)"] -.-> R1

    style R1 fill:#e94560,color:#fff
    style R3 fill:#e94560,color:#fff
    style R5 fill:#e94560,color:#fff
    style R7 fill:#e94560,color:#fff
    style R2 fill:#0f3460,color:#fff
    style R6 fill:#0f3460,color:#fff
    style R4 fill:#533483,color:#fff
    style R8 fill:#1a1a2e,color:#fff
    style ALERT fill:#e94560,color:#fff,stroke:#ff0,stroke-width:2px
```

---

## 5. Closed-Loop Control (Every 10ms)

```mermaid
graph LR
    SENSE["SENSE<br/>ADC reads voltage<br/>& current on<br/>every branch"] --> CALC["CALCULATE<br/>KCL/KVL<br/>energy balance<br/>check"]
    CALC --> DECIDE["DECIDE<br/>Firmware logic<br/>optimal power<br/>routing"]
    DECIDE --> ROUTE["ROUTE<br/>GPIO + PWM<br/>switch MOSFETs<br/>adjust motors"]
    ROUTE --> VERIFY["VERIFY<br/>ADC re-reads<br/>confirm result<br/>close loop"]
    VERIFY --> SENSE

    style SENSE fill:#e94560,color:#fff
    style CALC fill:#533483,color:#fff
    style DECIDE fill:#0f3460,color:#fff
    style ROUTE fill:#2d6a4f,color:#fff
    style VERIFY fill:#e94560,color:#fff
```

---

## 6. Fault Detection State Machine

```mermaid
stateDiagram-v2
    [*] --> NORMAL

    NORMAL --> DRIFT: Vibration increasing
    DRIFT --> WARNING: IMU RMS > 1.0g
    WARNING --> FAULT: IMU RMS > 2.0g sustained
    FAULT --> EMERGENCY: Bus voltage < 3.8V

    FAULT --> NORMAL: Vibration subsides\n(auto recovery)
    WARNING --> NORMAL: Vibration subsides
    DRIFT --> NORMAL: Vibration subsides

    NORMAL --> NORMAL: Every 10ms check

    note right of NORMAL: Motors running\nIMU < 1.0g\nAll sensors OK
    note right of FAULT: Motors STOPPED\nAlert sent wirelessly\nLED indicates fault
    note right of EMERGENCY: Full shutdown\nAll loads shed\nManual reset needed
```

---

## 7. Demo Scenario — Smart Water Bottling Plant

```mermaid
graph LR
    PUMP["💧 Pump<br/>(Motor 1)<br/>PCA9685 CH2"] --> VALVE["🔧 Fill Valve<br/>(Servo 1)<br/>PCA9685 CH0"]
    VALVE --> CONV["📦 Conveyor<br/>(Motor 2)<br/>PCA9685 CH3"]
    CONV --> GATE["⚖️ Sort Gate<br/>(Servo 2)<br/>PCA9685 CH1"]
    GATE --> GOOD["✅ PASS"]
    GATE --> REJECT["❌ REJECT"]

    IMU["📳 BMI160 IMU<br/>Vibration<br/>Fault Detection"] -.-> PUMP
    ADC["⚡ ADC Sensing<br/>Voltage + Current<br/>Power Monitoring"] -.-> PUMP
    ADC -.-> CONV
    REC["♻️ Recycle Path<br/>2N2222 + Cap<br/>Energy Capture"] -.-> CONV

    style PUMP fill:#0f3460,color:#fff
    style VALVE fill:#533483,color:#fff
    style CONV fill:#0f3460,color:#fff
    style GATE fill:#533483,color:#fff
    style GOOD fill:#2d6a4f,color:#fff
    style REJECT fill:#e94560,color:#fff
    style IMU fill:#ff6b35,color:#fff
    style ADC fill:#ff6b35,color:#fff
    style REC fill:#2d6a4f,color:#fff
```

---

## 8. Demo Sequence Timeline

```mermaid
gantt
    title Demo Sequence (35 seconds)
    dateFormat ss
    axisFormat %S s

    section Stage
    BOOT - Self Test           :boot, 00, 3s
    READY - System Ready       :ready, after boot, 2s
    Motor 1 ON (Pump 65%)      :m1, after ready, 5s
    Motor 2 ON (Conveyor 45%)  :m2, after m1, 5s
    FAULT - Shake Detection    :crit, fault, after m2, 5s
    RECOVERY - Motors Restart  :recover, after fault, 3s
    RECYCLE - Energy Demo      :recycle, after recover, 4s
    DONE - Summary             :done, after recycle, 2s
```

---

## 9. Communication Flow (Sequence)

```mermaid
sequenceDiagram
    participant A as Pico A (Master)
    participant W as nRF24L01+ Wireless
    participant B as Pico B (Slave)
    participant D as MAX7219 Display

    Note over A: Boot + Self-Test
    A->>W: STATUS (state=BOOT)
    W->>B: 32-byte packet
    B->>D: Show "bOOt"

    Note over A: Motors ON
    A->>W: POWER (M1=380mA, M2=280mA)
    W->>B: 32-byte packet
    B->>D: Show "P 3200"

    Note over A: IMU detects vibration > 2g
    A->>W: ALERT (F1, severity=FAULT)
    W->>B: 32-byte packet
    B->>D: Flash "F1 VIb"

    Note over A: Motors STOPPED

    A->>W: STATUS (state=RECOVERY)
    W->>B: 32-byte packet
    B->>D: Show "rECOVEr"

    Note over A: Motors restart in priority order
    A->>W: POWER (restored)
    W->>B: 32-byte packet
    B->>D: Show "5.0V"
```

---

## 10. EEE Theory — Voltage Divider + Current Sensing

```mermaid
graph TB
    subgraph VD["Voltage Divider (Bus Voltage)"]
        V12["12V Bus"] --> R1["10kΩ"]
        R1 --> J["Junction → GP26 (ADC)"]
        J --> R2["10kΩ"]
        R2 --> G1["GND"]
    end

    subgraph CS["Current Sensing (Per Motor)"]
        MOT["Motor"] --> RS["1Ω Sense Resistor"]
        RS --> G2["GND"]
        RS2["Voltage across R<br/>→ GP27/GP28 (ADC)"] -.-> RS
    end

    subgraph FORMULA["Formulas"]
        F1["V_bus = V_adc × 2<br/>(divider ratio)"]
        F2["I_motor = V_sense / R_sense<br/>(Ohm's Law)"]
        F3["P_total = V_bus × ΣI<br/>(Power equation)"]
    end

    style VD fill:#0f3460,color:#fff
    style CS fill:#533483,color:#fff
    style FORMULA fill:#2d6a4f,color:#fff
```

---

## 11. Recycle Path Circuit

```mermaid
graph TB
    V5["5V Rail"] --> LED_P["LED (+)"]
    LED_P --> LED_N["LED (-)"]
    LED_N --> R150["150Ω"]
    R150 --> COL["2N2222 Collector<br/>(Pin 3)"]
    GP["GP13 (Pico A)"] --> R1K["1kΩ"]
    R1K --> BASE["2N2222 Base<br/>(Pin 2)"]
    EMIT["2N2222 Emitter<br/>(Pin 1)"] --> GND["GND"]

    subgraph DEMO["Demo Effect"]
        ON["GP13 HIGH<br/>→ Transistor ON<br/>→ LED ON<br/>(current flows)"]
        OFF["GP13 LOW<br/>→ Transistor OFF<br/>→ LED OFF<br/>(path disconnected)"]
    end

    style V5 fill:#ff6b35,color:#fff
    style GP fill:#2d6a4f,color:#fff
    style COL fill:#533483,color:#fff
    style BASE fill:#533483,color:#fff
    style EMIT fill:#533483,color:#fff
    style GND fill:#333,color:#fff
    style ON fill:#2d6a4f,color:#fff
    style OFF fill:#e94560,color:#fff
```

---

## 12. Cost Comparison

```mermaid
graph LR
    subgraph IND["Industrial System: £162,000+"]
        S1["Siemens SCADA<br/>£80,000"]
        S2["Schneider Power Meters<br/>£15,000"]
        S3["NI Vibration Analyser<br/>£18,000"]
        S4["ABB Motor Drives<br/>£35,000"]
        S5["Honeywell BMS<br/>£14,000"]
    end

    subgraph GB["GridBox: £15"]
        G1["2x Pico 2<br/>£8"]
        G2["2x nRF24L01+<br/>£3"]
        G3["BMI160 IMU<br/>£2"]
        G4["PCA9685 + Driver<br/>£2"]
    end

    IND -. "10,800x cheaper" .-> GB

    style IND fill:#e94560,color:#fff
    style GB fill:#2d6a4f,color:#fff
```

---

## 13. Factory Layout — Battery Recovery Plant (Top View)

```mermaid
graph TB
    subgraph INTAKE["INTAKE ZONE"]
        HOPPER["Battery Hopper<br/>(Judge drops here)"]
        GATE["Intake Gate<br/>(Servo 1)"]
    end

    subgraph STAGE1["STAGE 1 — SIZE SORTING"]
        DISC["Turntable Disc<br/>(DC Motor 1)"]
        GAP["Size Gap<br/>(physical slot)"]
        ARM1["Size Reject Arm<br/>(Servo)"]
        SMALL["Small Bin<br/>Button Cells"]
        HAZMAT["Hazmat Bin<br/>Oversized"]
    end

    subgraph STAGE2["STAGE 2 — WEIGHT SORTING"]
        WEIGH["Weight Check Zone<br/>(ADC current sensing)"]
        HEAVY_ARM["Heavy Sort Arm<br/>(Servo)"]
        LIGHT_ARM["Light Sort Arm<br/>(Servo)"]
        HEAVY["Heavy Bin<br/>Li-ION"]
        LIGHT["Light Bin<br/>Alkaline"]
    end

    subgraph HVAC["HVAC SYSTEM"]
        FAN["Safety Fan<br/>(DC Motor 2)<br/>NEVER SHEDS"]
        ZONE_A["Zone A Damper<br/>Sorting Area"]
        ZONE_B["Zone B Damper<br/>Output Area"]
    end

    subgraph CONTROL["CONTROL ROOM (Pico B)"]
        OLED["OLED Display"]
        SEG["MAX7219<br/>7-Segment"]
    end

    HOPPER --> GATE --> DISC
    DISC --> GAP
    GAP -- "falls through" --> SMALL
    GAP -- "stays on disc" --> WEIGH
    ARM1 -- "too big" --> HAZMAT
    WEIGH -- "heavy" --> HEAVY_ARM --> HEAVY
    WEIGH -- "light" --> LIGHT_ARM --> LIGHT

    FAN --> ZONE_A
    FAN --> ZONE_B

    IMU["BMI160 IMU<br/>on Motor 1"] -.-> DISC
    PICO_A["Pico A<br/>(Master)"] -.-> DISC
    PICO_A -.->|"wireless"| CONTROL

    style INTAKE fill:#ff6b35,color:#fff
    style STAGE1 fill:#0f3460,color:#fff
    style STAGE2 fill:#533483,color:#fff
    style HVAC fill:#e94560,color:#fff
    style CONTROL fill:#16213e,color:#fff
```

---

## 14. Factory Sorting Flow

```mermaid
graph TD
    START["Judge drops battery<br/>onto turntable"] --> SPIN["Motor 1 spins<br/>turntable"]
    SPIN --> GAP{"SIZE GAP<br/>(physical slot)"}

    GAP -- "Small item<br/>falls through" --> SMALL_BIN["SMALL BIN<br/>Button cells<br/>Watch batteries"]

    GAP -- "Large item<br/>stays on disc" --> WEIGHT{"WEIGHT CHECK<br/>ADC reads Motor 1<br/>current (GP27)"}

    WEIGHT -- "Current > threshold<br/>(heavy)" --> SERVO1["Servo 1 pushes<br/>item off disc"] --> HEAVY_BIN["HEAVY BIN<br/>Li-ION batteries<br/>Phone/laptop cells"]

    WEIGHT -- "Current < threshold<br/>(light)" --> SERVO2["Servo 2 pushes<br/>item off disc"] --> LIGHT_BIN["LIGHT BIN<br/>Alkaline batteries<br/>Discharged cells"]

    style START fill:#ff6b35,color:#fff
    style SPIN fill:#0f3460,color:#fff
    style GAP fill:#533483,color:#fff
    style SMALL_BIN fill:#2d6a4f,color:#fff
    style WEIGHT fill:#e94560,color:#fff
    style SERVO1 fill:#533483,color:#fff
    style SERVO2 fill:#533483,color:#fff
    style HEAVY_BIN fill:#e94560,color:#fff
    style LIGHT_BIN fill:#2d6a4f,color:#fff
```

---

## 15. Water Bottling Plant (Demo Scenario — Detailed)

```mermaid
graph LR
    subgraph PROCESS["Production Line"]
        direction LR
        PUMP["Pump<br/>(Motor 1)<br/>PCA9685 CH2<br/>65% PWM"] --> VALVE["Fill Valve<br/>(Servo 1)<br/>PCA9685 CH0<br/>0° / 90°"]
        VALVE --> FILL["Fill Station<br/>Timed fill<br/>2 seconds"]
        FILL --> CONV["Conveyor<br/>(Motor 2)<br/>PCA9685 CH3<br/>45% PWM"]
        CONV --> GATE["Sort Gate<br/>(Servo 2)<br/>PCA9685 CH1<br/>0° / 180°"]
    end

    subgraph OUTPUT["Output"]
        GOOD["PASS<br/>Good bottle"]
        BAD["REJECT<br/>Bad bottle"]
    end

    GATE --> GOOD
    GATE --> BAD

    subgraph MONITOR["Monitoring"]
        IMU["BMI160 IMU<br/>Vibration RMS<br/>Fault if > 2g"]
        ADC["ADC Sensing<br/>Bus V (GP26)<br/>Motor I (GP27/28)"]
        REC["Recycle Path<br/>2N2222 + LED<br/>GP13 control"]
    end

    IMU -.->|"mounted on pump"| PUMP
    ADC -.->|"measures current"| PUMP
    ADC -.->|"measures current"| CONV

    subgraph WIRELESS["Wireless SCADA"]
        NRF_A["nRF24L01+<br/>Pico A (TX)"]
        NRF_B["nRF24L01+<br/>Pico B (RX)"]
        DISPLAY["MAX7219<br/>Shows: V, mA,<br/>FAULT, PASS"]
    end

    NRF_A -->|"250kbps<br/>32-byte packets"| NRF_B --> DISPLAY

    style PROCESS fill:#0f3460,color:#fff
    style OUTPUT fill:#2d6a4f,color:#fff
    style MONITOR fill:#ff6b35,color:#fff
    style WIRELESS fill:#533483,color:#fff
    style BAD fill:#e94560,color:#fff
```

---

## 16. Application Scenarios (GridBox Versatility)

```mermaid
graph TB
    GRIDBOX["GridBox<br/>£15 Controller<br/>Same firmware"] --> APP1["Water Bottling<br/>Plant"]
    GRIDBOX --> APP2["Battery Recovery<br/>Recycling"]
    GRIDBOX --> APP3["Pharmaceutical<br/>QC Inspection"]
    GRIDBOX --> APP4["Coffee Roasting<br/>Facility"]
    GRIDBOX --> APP5["HVAC Building<br/>Management"]

    APP1 --- D1["Pump + Conveyor<br/>Fill valve + Sort gate"]
    APP2 --- D2["Turntable + Fan<br/>Size gap + Weight sort"]
    APP3 --- D3["Inspection belt<br/>Pass / Quarantine"]
    APP4 --- D4["Roast drum + Cooling<br/>QC sort"]
    APP5 --- D5["Fan speed + Dampers<br/>Zone control"]

    style GRIDBOX fill:#ff6b35,color:#fff
    style APP1 fill:#0f3460,color:#fff
    style APP2 fill:#2d6a4f,color:#fff
    style APP3 fill:#533483,color:#fff
    style APP4 fill:#e94560,color:#fff
    style APP5 fill:#1a1a2e,color:#fff
```

---

## 17. Power Distribution

```mermaid
graph TD
    PSU["12V 6A PSU"] --> BUCK["LM2596S<br/>Buck Converter<br/>→ 5V Logic"]
    PSU --> BOOST["300W Buck-Boost<br/>→ 6-9V Motors"]

    BUCK --> PICO_A["Pico A (VSYS)"]
    BUCK --> PICO_B["Pico B (VSYS)"]
    BUCK --> PCA["PCA9685<br/>VCC = 3.3V (logic)<br/>V+ = 5V (servo)"]
    BUCK --> NRF1["nRF24L01+<br/>(3.3V from Pico)"]
    BUCK --> NRF2["nRF24L01+<br/>(3.3V from Pico)"]
    BUCK --> MAX["MAX7219<br/>(5V recommended)"]

    BOOST --> MOT1["DC Motor 1<br/>(Pump)"]
    BOOST --> MOT2["DC Motor 2<br/>(Conveyor)"]

    PICO_A -->|"3.3V out"| IMU["BMI160 IMU"]

    style PSU fill:#e94560,color:#fff
    style BUCK fill:#ff6b35,color:#fff
    style BOOST fill:#ff6b35,color:#fff
    style PICO_A fill:#1a1a2e,color:#fff
    style PICO_B fill:#16213e,color:#fff
```

---

## Suggested Slide Mapping

| Slide | Diagram # | Topic |
|---|---|---|
| Problem | 12 | Cost comparison |
| Solution | 7 | Demo scenario flow |
| Architecture | 1 | Full two-Pico system |
| Technical — Protocol | 2, 3, 4 | Datagram types, packet structure, rotation |
| Technical — Control | 5 | Closed-loop SENSE→ROUTE→VERIFY |
| EEE Theory | 10 | Voltage divider + current sensing |
| Fault Detection | 6 | State machine |
| Live Demo | 8, 9 | Timeline + communication sequence |
| Recycle Path | 11 | Circuit diagram |
