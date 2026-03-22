# GridBox — System Architecture Diagram

## Two-Pico Overview

```mermaid
graph LR
    subgraph PICO_A["Pico A — MASTER (Grid Controller)"]
        direction TB
        A_CORE0["Core 0<br/>Main Loop 100Hz"]
        A_CORE1["Core 1<br/>Fault Detection"]
        A_ADC["ADC<br/>GP26: Bus Voltage<br/>GP27: Motor 1 Current<br/>GP28: Motor 2 Current"]
        A_I2C["I2C0<br/>BMI160 IMU (0x68)<br/>PCA9685 PWM (0x40)"]
        A_SPI["SPI0<br/>nRF24L01+ Wireless"]
        A_GPIO["GPIO<br/>GP13: Recycle MOSFET<br/>GP14: Red LED<br/>GP15: Green LED<br/>GP25: Heartbeat"]
    end

    subgraph PICO_B["Pico B — SLAVE (SCADA Station)"]
        direction TB
        B_CORE["Main Loop"]
        B_I2C["I2C0<br/>SSD1306 OLED (0x3C)"]
        B_SPI0["SPI0<br/>nRF24L01+ Wireless"]
        B_SPI1["SPI1<br/>MAX7219 7-Segment"]
        B_ADC["ADC<br/>GP26: Joystick X<br/>GP27: Joystick Y<br/>GP28: Potentiometer"]
        B_GPIO["GPIO<br/>GP22: Joystick Button<br/>GP14: Red LED<br/>GP15: Green LED<br/>GP25: Heartbeat"]
    end

    A_SPI -- "nRF24L01+ 2.4GHz<br/>Channel 100 · 250kbps<br/>32-byte packets" --> B_SPI0

    style PICO_A fill:#1a1a2e,color:#fff
    style PICO_B fill:#16213e,color:#fff
```

## Wireless Protocol

```mermaid
graph LR
    subgraph A_TO_B["Pico A → Pico B (Telemetry)"]
        direction TB
        P1["POWER<br/>Bus voltage, motor currents,<br/>total power, efficiency %"]
        P2["STATUS<br/>System state, fault source,<br/>IMU, mode, uptime"]
        P3["PRODUCTION<br/>Items processed, pass/reject,<br/>belt speed, thresholds"]
        P4["HEARTBEAT<br/>Timestamp, CPU load,<br/>wireless reliability"]
        P5["ALERT<br/>Fault code, severity,<br/>affected subsystem"]
    end

    subgraph B_TO_A["Pico B → Pico A (Commands)"]
        direction TB
        C1["COMMAND<br/>Motor speed, servo position,<br/>mode switch, emergency stop"]
    end

    A_TO_B -- "Rotation: P·S·P·Pr·P·S·P·H<br/>(ALERT breaks rotation)" --> B_TO_A

    style A_TO_B fill:#0f3460,color:#fff
    style B_TO_A fill:#533483,color:#fff
```

## Packet Rotation Schedule

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

## Hardware Wiring

```mermaid
graph TB
    subgraph POWER["Power Supply"]
        PSU["12V 6A PSU"]
        BUCK["LM2596S Buck<br/>→ 5V Logic"]
        BOOST["300W Buck-Boost<br/>→ 6-9V Motors"]
    end

    subgraph MASTER["Pico A — MASTER"]
        MA_NRF["nRF24L01+<br/>SPI0: GP0-3, GP16"]
        MA_IMU["BMI160 IMU<br/>I2C0: GP4-5"]
        MA_PCA["PCA9685 PWM<br/>I2C0: GP4-5"]
        MA_ADC["ADC Sensing<br/>GP26-28"]
    end

    subgraph SLAVE["Pico B — SLAVE"]
        SL_NRF["nRF24L01+<br/>SPI0: GP0-3, GP16"]
        SL_OLED["SSD1306 OLED<br/>I2C0: GP4-5"]
        SL_7SEG["MAX7219 7-Seg<br/>SPI1: GP10-11, GP13"]
        SL_JOY["Joystick + Pot<br/>ADC: GP26-28"]
    end

    subgraph ACTUATORS["Actuators"]
        M1["DC Motor 1<br/>(Fan/Pump)"]
        M2["DC Motor 2<br/>(Conveyor)"]
        S1["Servo 1<br/>(Fill Valve)"]
        S2["Servo 2<br/>(Sort Gate)"]
    end

    PSU --> BUCK --> MASTER
    PSU --> BOOST
    BUCK --> SLAVE

    MA_PCA -- "CH2 → MOSFET" --> M1
    MA_PCA -- "CH3 → MOSFET" --> M2
    MA_PCA -- "CH0" --> S1
    MA_PCA -- "CH1" --> S2
    BOOST --> M1
    BOOST --> M2

    MA_NRF -. "2.4GHz" .-> SL_NRF

    style POWER fill:#ff6b35,color:#fff
    style MASTER fill:#1a1a2e,color:#fff
    style SLAVE fill:#16213e,color:#fff
    style ACTUATORS fill:#2d6a4f,color:#fff
```

## Software Layers

```mermaid
graph TB
    subgraph DEV["Development (MicroPython)"]
        direction LR
        MP_M["Master: 16 modules"]
        MP_S["Slave: 12 modules"]
        MP_P["Shared: protocol.py"]
    end

    subgraph PROD["Production (C SDK)"]
        direction LR
        C_M["Master: main.c + drivers"]
        C_S["Slave: main.c + drivers"]
        C_T["Test: test_hw.c"]
    end

    subgraph TOOLS["Tools"]
        direction LR
        FL["flash.sh<br/>12 commands"]
        BC["build-c.sh<br/>clean/flash"]
        WEB["Flask Dashboard<br/>localhost:5000"]
    end

    DEV --> PROD
    TOOLS --> DEV
    TOOLS --> PROD

    style DEV fill:#0f3460,color:#fff
    style PROD fill:#e94560,color:#fff
    style TOOLS fill:#533483,color:#fff
```

## Demo Scenario: Smart Water Bottling Plant

```mermaid
graph LR
    PUMP["💧 Pump<br/>(Motor 1)"] --> VALVE["🔧 Fill Valve<br/>(Servo 1)"]
    VALVE --> CONVEYOR["📦 Conveyor<br/>(Motor 2)"]
    CONVEYOR --> GATE["⚖️ Sort Gate<br/>(Servo 2)"]
    GATE --> GOOD["✅ Good"]
    GATE --> REJECT["❌ Reject"]

    IMU["📳 IMU<br/>Vibration"] -.-> CONVEYOR
    ADC["⚡ ADC<br/>Current"] -.-> PUMP
    ADC -.-> CONVEYOR

    style PUMP fill:#0f3460,color:#fff
    style VALVE fill:#533483,color:#fff
    style CONVEYOR fill:#0f3460,color:#fff
    style GATE fill:#533483,color:#fff
    style GOOD fill:#2d6a4f,color:#fff
    style REJECT fill:#e94560,color:#fff
```
