# Presentation Reference — Visual Assets

> All images generated for the PPT. Pick what you need. PNG files in `docs/03-factory/charts/`.

---

## 1. Cost Comparison (£15 vs Industrial)

Use for: **Problem Fit (30pts)** — shows the cost gap

![Cost Comparison](charts/01-cost-comparison.png)

---

## 2. Affinity Laws Power Curve (P ∝ n³)

Use for: **Technical + Innovation** — shows 49% power saving at 80% speed

![Affinity Laws](charts/02-affinity-laws.png)

---

## 3. Packet Protocol (6 Datagram Types)

Use for: **Technical** — shows our custom wireless protocol, packet structure, and all 6 types

![Packet Protocol](charts/03-packet-protocol.png)

---

## 4. System Architecture (Two-Pico)

Use for: **System Architecture slide** — shows Pico A (master) and Pico B (slave) with all peripherals and wireless link

![Architecture](charts/04-architecture.png)

---

## 5. Scoring Radar Chart

Use for: **Results slide** — shows how we score against each judging category

![Scoring Radar](charts/05-scoring-radar.png)

---

## 6. Closed-Loop Control Flow

Use for: **Technical** — shows SENSE → CALCULATE → DECIDE → ROUTE → VERIFY cycle at 100Hz

![Control Loop](charts/06-control-loop.png)

---

## 7. Fault Detection State Machine

Use for: **Technical + Innovation** — shows NORMAL → DRIFT → WARNING → FAULT → EMERGENCY + auto recovery

![Fault State Machine](charts/07-fault-state-machine.png)

---

## 8. Wiring Progress

Use for: **Results** — shows 77% wiring complete (48 done, 13 TODO, 18 cancelled)

![Wiring Progress](charts/08-wiring-progress.png)

---

## Mermaid Diagrams (render on GitHub or mermaid.live)

### Packet Rotation Schedule

```mermaid
graph LR
    R1["POWER"] --> R2["STATUS"] --> R3["POWER"] --> R4["PRODUCTION"]
    R4 --> R5["POWER"] --> R6["STATUS"] --> R7["POWER"] --> R8["HEARTBEAT"]
    R8 --> R1

    style R1 fill:#e94560,color:#fff
    style R3 fill:#e94560,color:#fff
    style R5 fill:#e94560,color:#fff
    style R7 fill:#e94560,color:#fff
    style R2 fill:#0f3460,color:#fff
    style R6 fill:#0f3460,color:#fff
    style R4 fill:#533483,color:#fff
    style R8 fill:#1a1a2e,color:#fff
```

### Demo Scenario Flow

```mermaid
graph LR
    PUMP["Pump<br/>(Motor 1)"] --> VALVE["Fill Valve<br/>(Servo 1)"]
    VALVE --> CONVEYOR["Conveyor<br/>(Motor 2)"]
    CONVEYOR --> GATE["Sort Gate<br/>(Servo 2)"]
    GATE --> GOOD["PASS"]
    GATE --> REJECT["REJECT"]

    IMU["BMI160 IMU<br/>Vibration"] -.-> CONVEYOR
    ADC["ADC<br/>Current Sense"] -.-> PUMP
    ADC -.-> CONVEYOR

    style PUMP fill:#0f3460,color:#fff
    style VALVE fill:#533483,color:#fff
    style CONVEYOR fill:#0f3460,color:#fff
    style GATE fill:#533483,color:#fff
    style GOOD fill:#2d6a4f,color:#fff
    style REJECT fill:#e94560,color:#fff
```

### Wireless Communication Flow

```mermaid
sequenceDiagram
    participant A as Pico A (Master)
    participant B as Pico B (Slave)

    A->>B: POWER (voltage, current, watts)
    A->>B: STATUS (state, fault, IMU, mode)
    A->>B: POWER (voltage, current, watts)
    A->>B: PRODUCTION (items, pass/reject)
    A->>B: POWER (voltage, current, watts)
    A->>B: STATUS (state, fault, IMU, mode)
    A->>B: POWER (voltage, current, watts)
    A->>B: HEARTBEAT (uptime, CPU, reliability)
    B->>A: COMMAND (speed, servo, mode, e-stop)

    Note over A,B: ALERT breaks rotation on fault
    A-->>B: ALERT (fault code, severity)
```

### Recycle Path Circuit

```mermaid
graph TD
    V5["5V Rail"] --> C["2N2222<br/>Collector (Pin 3)"]
    GP13["GP13"] --> R1["1kΩ"] --> B["2N2222<br/>Base (Pin 2)"]
    E["2N2222<br/>Emitter (Pin 1)"] --> CAP_P["Cap (+)<br/>200µF"]
    CAP_P --> LED["LED (green)"]
    LED --> R2["150Ω"] --> GND1["GND"]
    CAP_N["Cap (-)"] --> GND2["GND"]
    CAP_P --- CAP_N

    style V5 fill:#ff6b35,color:#fff
    style GP13 fill:#2d6a4f,color:#fff
    style C fill:#533483,color:#fff
    style B fill:#533483,color:#fff
    style E fill:#533483,color:#fff
    style LED fill:#2d6a4f,color:#fff
    style GND1 fill:#333,color:#fff
    style GND2 fill:#333,color:#fff
```

---

## Suggested Slide Mapping

| Slide | Charts to Use |
|---|---|
| Problem | `01-cost-comparison.png` |
| System Architecture | `04-architecture.png` |
| Technical Summary | `03-packet-protocol.png`, `06-control-loop.png` |
| EEE Theory | `02-affinity-laws.png`, `07-fault-state-machine.png` |
| Live Demo | Mermaid demo scenario flow |
| Results | `05-scoring-radar.png`, `08-wiring-progress.png` |
