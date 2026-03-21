# GridBox — Smart Infrastructure Control System

> "Recycled energy powers an intelligent system that monitors, decides, and acts autonomously"

**Theme:** Sustainability + Autonomy
**Score: 96/100**

---

## The Big Idea

Assume we have recycled energy available (from wind, solar, vibration harvesting, etc.). The 12V PSU represents this recycled energy input. The question we answer is: **how do you intelligently manage and distribute that energy to run an infrastructure system?**

GridBox is a miniature smart infrastructure system powered by recycled energy. DC motors drive actuators (fans, pumps, conveyors). Servos control gates and switches. The Pico monitors everything with sensors and makes autonomous decisions. A wireless SCADA dashboard shows it all in real-time.

```mermaid
graph LR
    RECYCLE[Recycled Energy Input] --> PSU[12V PSU]
    PSU --> BUCK[Buck Converter]
    BUCK --> PICO[Pico: Smart Brain]
    PICO --> MOTORS[DC Motors: Actuators]
    PICO --> SERVOS[Servos: Gates/Switches]
    PICO --> SENSORS[IMU + ADC: Monitoring]
    PICO -->|wireless| SCADA[OLED: Dashboard]
```

---

## The Problem

| Fact | Detail |
|---|---|
| **68%** | of energy produced globally is WASTED |
| **40%** | of building energy goes to HVAC — most runs at full speed constantly |
| **$150 billion** | lost annually from industrial energy waste in the US |
| **Zero intelligence** | most small-scale systems have no smart monitoring or control |

**The gap:** Recycled/renewable energy is available — but there's no cheap system to **manage it intelligently.** No monitoring, no autonomous control, no fault detection. We build that system for £15.

---

## System Overview

```mermaid
graph LR
    subgraph INPUT["Power Input (recycled energy)"]
        PSU[12V PSU]
        BUCK[Buck Converter: 12V → 5V/3.3V]
    end

    subgraph BRAIN["Smart Controller (Pico A)"]
        PICO[Raspberry Pi Pico 2]
        ADC[ADC: voltage/current sensing]
        IMU[BMI160: vibration monitor]
    end

    subgraph ACTUATORS["Actuators (what the energy drives)"]
        M1[DC Motor 1: Fan/Pump]
        M2[DC Motor 2: Conveyor/Vent]
        S1[Servo 1: Valve/Damper]
        S2[Servo 2: Gate/Switch]
    end

    subgraph MONITOR["SCADA (Pico B)"]
        OLED[OLED: Dashboard]
        JOY[Joystick: Override]
        POT[Potentiometer: Setpoint]
    end

    INPUT --> BRAIN
    BRAIN --> ACTUATORS
    BRAIN -->|"wireless telemetry"| MONITOR
```

| Block | Components | Role |
|---|---|---|
| Power Input | 12V PSU + LM2596S buck converter | Represents recycled energy source, regulates to usable voltage |
| Smart Controller | Pico A + ADC + BMI160 IMU + nRF24L01+ | Reads sensors, makes decisions, controls actuators |
| Actuators | DC motors (fans/pumps) + servos (valves/dampers) via PCA9685 | Physical actions driven by the recycled energy |
| SCADA | Pico B + OLED + joystick + potentiometer + nRF24L01+ | Remote monitoring dashboard + manual override |

---

## What Each Component DOES

| Component | Role as Actuator/Sensor | Real-World Equivalent |
|---|---|---|
| **DC Motor 1** | Fan — variable speed via PWM | HVAC intake fan, cooling fan, ventilation |
| **DC Motor 2** | Pump or conveyor — variable speed | Water pump, material conveyor, air circulation |
| **Servo 1** | Valve/damper — opens/closes a flow path | Duct damper, water valve, gas shut-off |
| **Servo 2** | Gate/switch — connects/disconnects a circuit | Circuit breaker, emergency shut-off, load switch |
| **BMI160 IMU** | Vibration sensor on motor — detects faults | Industrial condition monitoring on generators/pumps |
| **ADC (voltage)** | Measures bus voltage and motor current | Power monitoring, load measurement |
| **Potentiometer** | Setpoint dial (temperature, speed, threshold) | Thermostat dial, speed control, alarm threshold |
| **Joystick** | Manual override — control motors/servos directly | Operator console in a control room |
| **OLED** | SCADA dashboard — real-time system status | Control room display |
| **LEDs** | System status indicators | Green=normal, Yellow=warning, Red=fault |
| **nRF24L01+** | Wireless telemetry link | SCADA communication between field device and control room |

---

## Autonomous Control Logic

The Pico makes decisions without human input:

```mermaid
flowchart LR
    READ[Read sensors] --> V{Bus voltage OK?}
    V -->|Low| SHED[Reduce non-essential loads]
    V -->|OK| VIB{Motor vibration OK?}
    VIB -->|High| FAULT[Stop faulty motor, switch to backup]
    VIB -->|OK| DEMAND{Demand vs capacity?}
    DEMAND -->|Over| SLOW[Reduce motor speeds]
    DEMAND -->|Under| RAMP[Increase to optimal]
    DEMAND -->|Balanced| NORMAL[Continue normal ops]
```

| Decision | Trigger | Autonomous Action |
|---|---|---|
| **Load shedding** | Bus voltage drops below threshold | Servo disconnects non-essential loads (LEDs turn off) |
| **Fault isolation** | IMU detects motor vibration > 2g for 3s | PCA9685 stops faulty motor, switches to backup motor |
| **Speed control** | Potentiometer setpoint vs current state | PWM adjusts motor speed to match demand |
| **Emergency stop** | Voltage critical or vibration extreme | All servos close, motors stop, alert sent wirelessly |
| **Auto-recovery** | Fault clears, voltage recovers | Gradually reconnect loads, resume normal operation |

---

## Fault Detection — IMU as Vibration Monitor

```mermaid
stateDiagram-v2
    [*] --> HEALTHY: vibration < 1g

    HEALTHY --> WARNING: 1-2g
    WARNING --> HEALTHY: drops < 1g
    WARNING --> FAULT: > 2g for 3s

    FAULT --> HEALTHY: joystick reset
```

| State | Action | OLED Display |
|---|---|---|
| HEALTHY | Normal operation | "MOTOR 1: OK — 0.3g" LED green |
| WARNING | Alert sent, monitor closely | "MOTOR 1: WARNING — 1.5g" LED yellow |
| FAULT | Motor stopped by PCA9685, backup activated | "MOTOR 1: FAULT — DISCONNECTED" LED red |

---

## Recommended Scenario: Smart Water Bottling Plant

We pick **one concrete factory** and build the full story around it. This is what judges see:

> *"This is a miniature smart water bottling plant. Recycled energy powers the system. Water is pumped, filtered, and bottled. Everything is monitored wirelessly. When equipment fails, the system protects itself automatically."*

### The Process (What the Factory Does)

```mermaid
graph LR
    WATER[Water Source] -->|"Pump"| FILTER[Filtration Stage]
    FILTER -->|"Conveyor"| FILL[Filling Station]
    FILL -->|"Valve"| BOTTLE[Bottled Output]
    BOTTLE -->|"Quality gate"| GOOD[Good bottles]
    BOTTLE -->|"Quality gate"| REJECT[Rejected bottles]
```

### Component → Factory Mapping

```mermaid
graph LR
    subgraph PLANT["Water Bottling Plant"]
        PUMP[DC Motor 1: Water Pump]
        CONV[DC Motor 2: Conveyor Belt]
        VALVE[Servo 1: Fill Valve]
        GATE[Servo 2: Quality Gate]
    end

    subgraph CONTROL["Smart Controller"]
        PICO[Pico A + IMU + ADC]
    end

    subgraph SCADA["Control Room"]
        DASH[Pico B + OLED + Joystick + Pot]
    end

    PLANT --> CONTROL
    CONTROL -->|wireless| SCADA
```

| Our Component | Factory Equipment | What It Does in the Plant |
|---|---|---|
| **DC Motor 1** | Water pump | Pumps water from source through filtration to filling station. Speed = flow rate. PWM controlled |
| **DC Motor 2** | Conveyor belt | Moves bottles along the production line. Speed = production rate. PWM controlled |
| **Servo 1** | Fill valve | Opens to fill bottle, closes when full. Timed open/close cycle per bottle |
| **Servo 2** | Quality/sorting gate | Directs bottles: good → output, bad → reject bin. Position based on IMU vibration data |
| **BMI160 IMU** | Equipment health monitor | Mounted on pump motor — detects bearing wear, cavitation, blockages via vibration |
| **Potentiometer** | Production speed dial | Sets bottles-per-minute target. Pico adjusts pump speed + conveyor speed to match |
| **Joystick** | Operator console | Manual override: control pump/conveyor speed, open/close valves, acknowledge faults |
| **OLED** | SCADA dashboard | Shows: production rate, pump health, valve status, energy use, fault alerts |
| **LEDs** | Status tower light | Green = running, Yellow = warning, Red = fault (like real factory stack lights) |
| **ADC** | Power monitor | Measures bus voltage + motor current → calculates energy per bottle |
| **nRF24L01+** | SCADA wireless link | Streams all data to control room — no wires between plant floor and office |
| **Buck converter** | Transformer | Steps recycled energy (12V) down to usable levels for control electronics |

### The Production Cycle (Automated)

```mermaid
flowchart LR
    START[Bottle on conveyor] --> MOVE[Motor 2: move to fill station]
    MOVE --> OPEN[Servo 1: open fill valve]
    OPEN --> FILL[Motor 1: pump water - timed fill]
    FILL --> CLOSE[Servo 1: close fill valve]
    CLOSE --> CHECK{IMU: vibration normal?}
    CHECK -->|Yes| PASS[Servo 2: pass → good output]
    CHECK -->|No| FAIL[Servo 2: reject → waste bin]
    PASS --> NEXT[Motor 2: next bottle]
    FAIL --> NEXT
    NEXT --> START
```

| Step | Duration | What Happens | What OLED Shows |
|---|---|---|---|
| 1. Move bottle | 1s | Conveyor motor runs at set speed | "CONVEYOR: MOVING" |
| 2. Open valve | 0.2s | Servo 1 opens to 90° | "VALVE: OPEN" |
| 3. Fill | 2s | Pump runs at calibrated speed | "FILLING: 2.0s" |
| 4. Close valve | 0.2s | Servo 1 returns to 0° | "VALVE: CLOSED" |
| 5. Quality check | 0.5s | IMU checks for abnormal vibration during fill | "QC: CHECKING..." |
| 6. Sort | 0.3s | Servo 2 directs to pass or reject | "QC: PASS ✓" or "QC: REJECT ✗" |
| 7. Next | 1s | Conveyor moves to next position | "BOTTLES: 47 | RATE: 12/min" |

**Total cycle time: ~5 seconds per bottle = 12 bottles/minute**

### What Can Go Wrong (And How GridBox Handles It)

| Factory Problem | How It Happens | How GridBox Detects | Autonomous Response |
|---|---|---|---|
| **Pump bearing failure** | Wear over time → vibration increases | IMU $a_{rms}$ rises above 2g threshold | Stop pump, close valve, alert operator. "PUMP FAULT — BEARING" |
| **Pipe blockage** | Debris in water → flow reduces | Pump motor current drops (less load), vibration pattern changes | Reduce pump speed, alert. "BLOCKAGE SUSPECTED" |
| **Conveyor jam** | Bottle stuck → motor stalls | Motor current spikes, vibration stops | Stop conveyor, open reject gate, alert. "CONVEYOR JAM" |
| **Overfill** | Valve timing wrong → water overflows | Fill time exceeds threshold | Close valve immediately. "OVERFILL — VALVE CLOSED" |
| **Power drop** | Recycled energy source varies | ADC reads bus voltage dropping | Reduce production rate (slower motors), shed non-essential loads. "POWER LOW — REDUCED RATE" |
| **Complete power loss** | Energy source stops | Bus voltage = 0 | All valves close (fail-safe), alert sent. "EMERGENCY SHUTDOWN" |

### OLED Dashboard for Water Plant

```
WATER PLANT SCADA    [LIVE]

Pump:      1200 RPM   0.8A
Conveyor:   800 RPM   0.4A
Valve:     CLOSED
QC Gate:   PASS position

Bottles today:    347
Rate:             12/min
Rejects:          3 (0.9%)
Energy/bottle:    0.42 mWh
Pump health:      0.3g OK
```

### Why Water Bottling?

| Reason | Detail |
|---|---|
| **Everyone understands it** | Judges don't need to know engineering — "we pump water, fill bottles, check quality" |
| **Visual demo** | Motors spinning, servos clicking open/close, LEDs showing status — physical and tangible |
| **Sustainability perfect** | Clean water access, energy efficiency, waste reduction (reject bad fills) |
| **Maps to real industry** | £50B global bottled water market. Same system scales to real plants |
| **Every component earns its place** | Nothing wasted — each part has a clear factory function |
| **Autonomy is genuine** | System runs the production cycle without human input. Detects faults. Makes decisions |

---

## Other Factory Scenarios (Same System, Different Story)

The exact same hardware and firmware works for other factories — just change what the motors and servos represent:

### Scenario B: Smart Greenhouse / Vertical Farm

| Component | Greenhouse Role |
|---|---|
| DC Motor 1 | Ventilation fan — temperature control |
| DC Motor 2 | Water pump — irrigation |
| Servo 1 | Roof vent — opens when temperature high |
| Servo 2 | Water valve — timed irrigation cycles |
| Potentiometer | Temperature setpoint |
| IMU | Fan vibration + structure tilt monitoring |
| OLED | Climate dashboard: temp, humidity, fan speed, water schedule |

### Scenario C: Recycling Sorting Facility

| Component | Recycling Role |
|---|---|
| DC Motor 1 | Conveyor belt — moves waste along |
| DC Motor 2 | Shredder motor — breaks down recyclables |
| Servo 1 | Sorting gate — plastic left, metal right |
| Servo 2 | Emergency stop gate |
| Joystick | Manual sort override for unusual items |
| IMU | Shredder vibration — detects jams |
| OLED | Sorting stats: items processed, categories, jam alerts |

### Scenario D: HVAC / Building Climate Control

| Component | HVAC Role |
|---|---|
| DC Motor 1 | Intake fan — fresh air supply |
| DC Motor 2 | Exhaust fan — stale air removal |
| Servo 1 | Duct damper — zone control |
| Servo 2 | Emergency ventilation override |
| Potentiometer | Thermostat setpoint |
| IMU | Fan bearing health monitor |
| OLED | Climate status: zone temperatures, fan speeds, energy use |

**The firmware is the same.** Only the labels on the OLED change. Tell judges: *"Today it's a water bottling plant. Tomorrow it's a greenhouse, a recycling facility, or a building HVAC system. Same £15 controller, different application."*

---

## BMI160 IMU — The £2 Sensor That Replaces £18K of Industrial Equipment

The 6-axis IMU (accelerometer + gyroscope) is the most versatile sensor in the system. One chip, mounted on a motor or pipe, provides **10 different industrial measurements:**

```mermaid
graph LR
    IMU_C[BMI160 IMU] --> VIB[Vibration monitoring]
    IMU_C --> RPM[RPM estimation]
    IMU_C --> JAM[Jam/blockage detection]
    IMU_C --> LEAK[Leak detection]
    IMU_C --> VALVE[Valve position sensing]
    IMU_C --> TILT[Structural tilt monitor]
    IMU_C --> QUAKE[Impact/earthquake detect]
    IMU_C --> FALL[Worker fall detection]
```

### What Each Measurement Does

| # | Measurement | IMU Data Used | Detection Method | Industrial Equivalent | Cost Replaced |
|---|---|---|---|---|---|
| 1 | **Motor vibration health** | Accel $a_{rms}$ | $a_{rms} = \sqrt{a_x^2 + a_y^2 + a_z^2}$, compare to ISO 10816 thresholds | Vibration analyser | £10,000 |
| 2 | **RPM estimation** | Accel frequency | Count dominant vibration peaks per second — one peak per revolution | Tachometer | £200 |
| 3 | **Jam / blockage** | Accel sudden spike then flat | High vibration spike (impact) followed by near-zero (motor stalled) | Overcurrent relay | £150 |
| 4 | **Pipe leak** | Accel high-freq vibration | Leaking fluid creates turbulent vibration in 100-500Hz range — distinct from normal flow | Acoustic leak detector | £5,000 |
| 5 | **Valve position** | Gyro angle (roll/pitch) | Mount on valve handle: 0° = closed, 90° = open. Tracks partial positions | Position sensor | £100 |
| 6 | **Structural tilt** | Accel gravity vector | Slow drift in gravity angle over days/weeks = foundation settling, wall movement | Inclinometer | £500 |
| 7 | **Earthquake / impact** | Accel sudden spike > 5g | Exceeds normal operational range → emergency shutdown | Seismic sensor | £2,000 |
| 8 | **Worker fall** | Accel freefall → impact → immobility | 0g (falling) → >3g (hit ground) → 0 movement (10s) = confirmed fall | Lone worker device | £300 |
| 9 | **Belt tension** | Accel vibration frequency shift | Loose belt vibrates at lower frequency than tight belt — frequency drop = tension loss | Tension monitor | £500 |
| 10 | **Door / gate status** | Gyro rotation event | Sudden rotation = door opened. Direction tells open vs close. No magnets needed | Reed switch | £10 |

**Total industrial replacement cost: £18,760. Our IMU cost: £2.**

### How We Use It in the Demo

For the hackathon, we demonstrate **3 of these 10** live:

| Demo | How | What Judges See |
|---|---|---|
| **Motor vibration → fault detection** | Mount IMU on DC motor. Shake it = simulate bearing fault | IMU detects vibration → OLED: "FAULT" → motor auto-stops |
| **Valve position sensing** | Mount IMU on servo (represents a valve). Servo moves = IMU reads angle | OLED shows valve angle updating in real-time: "VALVE: 45° (partially open)" |
| **Impact / emergency** | Hit the breadboard sharply | IMU spike > 5g → emergency shutdown → all motors stop → OLED: "EMERGENCY STOP" |

The other 7 measurements work with the same firmware — just different thresholds and mounting positions. Tell judges: *"One £2 sensor, ten industrial measurements. We demo three. The other seven are the same code with different thresholds."*

### IMU Measurement Equations

**Vibration severity (ISO 10816):**

$$a_{rms} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

**RPM from vibration frequency:**

$$RPM = f_{dominant} \times 60$$

Where $f_{dominant}$ is found by counting zero-crossings: $f = \frac{crossings}{2 \times T_{sample}}$

**Tilt angle from gravity vector:**

$$\theta_{roll} = \arctan\left(\frac{a_y}{a_z}\right) \quad \theta_{pitch} = \arctan\left(\frac{a_x}{a_z}\right)$$

**Fall detection sequence:**

$$|a| < 0.3g \text{ (freefall)} \rightarrow |a| > 3g \text{ (impact)} \rightarrow |a| < 0.5g \text{ for 10s (immobile)}$$

---

## OLED SCADA Dashboard

### View 1: System Status

```
GRIDBOX SCADA      [LIVE]

MOTOR 1 (FAN):  1200 RPM
████████████░░░░░  75%
MOTOR 2 (PUMP): 800 RPM
████████░░░░░░░░░  50%

SERVO 1: OPEN   SERVO 2: CLOSED
BUS: 4.8V  POWER: 2.4W
STATUS: NORMAL
```

### View 2: Health Monitor

```
SYSTEM HEALTH

Motor 1 vibration:
∿∿∿∿∿∿∿∿∿∿  0.3g OK
Motor 2 vibration:
∿∿╲╱∿∿∿∿∿∿  0.8g WARN

Uptime: 00:14:32
Faults: 0   Shed events: 2
```

### View 3: Energy Summary

```
ENERGY REPORT

Input power:   5.0V  1.2A
Consumed:      31.7 mWh
Efficiency:    82%

Motor 1 duty:  72%   0.8A
Motor 2 duty:  48%   0.4A
STATUS: SUSTAINABLE
```

### View 4: Manual Control

```
MANUAL OVERRIDE    [JOY]

Motor 1: >>>>>>--  75%
         < Joy X to adjust >
Motor 2: >>>>----  50%
         < Joy Y to adjust >

Servo 1: [OPEN]   btn=toggle
Servo 2: [CLOSED]
Setpoint: 65%
```

Joystick Y scrolls between views. In View 4, joystick X/Y directly controls motor speeds.

---

## Factory Problems & How GridBox Solves Them

### The Reality of UK/Global Manufacturing

| Problem | Scale | Cost |
|---|---|---|
| **Unplanned downtime** | UK factories lose **£180 billion/year** from equipment failures | Average £250,000 per hour of downtime in automotive |
| **Energy waste** | Factories consume **42% of global electricity**, 30% is wasted on idle equipment | UK government net-zero mandate by 2050 requires 20% industrial energy reduction |
| **Manual monitoring** | 70% of small/medium factories still rely on **humans walking rounds** with clipboards | Missed faults, delayed responses, human error |
| **No predictive maintenance** | 82% of equipment failures are **random, not age-related** — scheduled maintenance doesn't catch them | Reactive repair costs **3-10x more** than predictive |
| **HVAC running blind** | Factory ventilation runs **24/7 at full speed** regardless of occupancy or temperature | 40% of building energy — most is wasted |
| **Regulatory pressure** | UK Energy Savings Opportunity Scheme (ESOS), Climate Change Levy, carbon reporting | Non-compliance = fines + reputational damage |
| **Automation cost barrier** | Industrial SCADA systems cost **£50,000–£500,000** to install | Small factories priced out of Industry 4.0 |

### How GridBox Replaces Expensive Industrial Systems

```mermaid
graph LR
    subgraph EXPENSIVE["Current: £50K–£500K"]
        E1[Siemens SCADA]
        E2[Honeywell BMS]
        E3[ABB Drives]
        E4[National Instruments DAQ]
    end

    subgraph GRIDBOX["GridBox: £15"]
        G1[Pico 2 + IMU + ADC]
        G2[nRF24L01+ wireless]
        G3[PCA9685 + motors]
        G4[OLED dashboard]
    end

    EXPENSIVE -.->|"same core functions<br/>for 1/3000th the cost"| GRIDBOX
```

| Industrial System | Cost | What It Does | GridBox Equivalent | Our Cost |
|---|---|---|---|---|
| **Siemens SCADA** | £100K+ | Monitor + control factory equipment remotely | Pico + OLED + nRF24L01+ wireless | £5 |
| **Honeywell BMS** | £50K+ | Building management — HVAC, lighting, access | Pico + PCA9685 + servos + potentiometer | £8 |
| **ABB VFD Drives** | £2K each | Variable speed motor control | PCA9685 PWM + DC motor | £3 |
| **NI Vibration Analyser** | £10K+ | Equipment condition monitoring | BMI160 IMU + firmware | £2 |
| **Schneider Power Meter** | £500+ | Energy consumption monitoring | ADC + voltage divider + resistors | £0.50 |

**Total industry cost: £162,500+. GridBox cost: ~£15.** Same core functions.

### Problem → Solution Mapping

#### 1. Unplanned Downtime → Predictive Maintenance

```mermaid
graph LR
    CURRENT[Current: Motor breaks → production stops → call engineer → wait 4 hours → £250K lost]
    GRIDBOX_SOL[GridBox: IMU detects vibration rising → alert at WARNING level → schedule repair at next shift → zero downtime]
```

**How it works:** BMI160 IMU mounted on motor housing continuously measures vibration. Firmware tracks the vibration trend:

$$a_{trend} = \frac{a_{rms}(today) - a_{rms}(yesterday)}{a_{rms}(yesterday)} \times 100\%$$

If $a_{trend} > 10\%$ per day → bearing deterioration → schedule maintenance **before** it fails.

**Government benefit:** UK Health and Safety Executive (HSE) requires employers to maintain equipment to prevent injury. Predictive maintenance demonstrates compliance.

#### 2. Energy Waste → Intelligent Speed Control

```mermaid
graph LR
    CURRENT2[Current: Fan runs at 100% 24/7 even when factory is empty]
    GRIDBOX_SOL2[GridBox: Potentiometer setpoint + PWM speed control = fan runs at 30% overnight, 80% during shifts]
```

**The Affinity Laws** (from EEE power systems):

$$P \propto n^3$$

Power consumption is proportional to the **cube** of motor speed. Reducing fan speed by 20% saves:

$$\text{Power saving} = 1 - (0.8)^3 = 1 - 0.512 = 48.8\%$$

**Running a fan at 80% speed saves nearly 50% energy.** This is real engineering — the cubic relationship means small speed reductions = massive energy savings.

| Fan Speed | Power Consumption | Savings vs 100% |
|---|---|---|
| 100% | 100% | — |
| 80% | 51.2% | **48.8%** |
| 60% | 21.6% | **78.4%** |
| 40% | 6.4% | **93.6%** |

GridBox demonstrates this live: turn the potentiometer down → motor slows → OLED shows power consumption dropping by the cube law.

**Government benefit:** UK Climate Change Levy charges companies per kWh. Reducing consumption = direct cost saving + tax reduction. ESOS requires large companies to audit energy use — GridBox provides the monitoring automatically.

#### 3. Manual Monitoring → Wireless Autonomous SCADA

```mermaid
graph LR
    CURRENT3[Current: Engineer walks factory floor every 2 hours with clipboard]
    GRIDBOX_SOL3[GridBox: nRF24L01+ streams data every 20ms → OLED shows everything → alerts are instant]
```

| | Manual Rounds | GridBox |
|---|---|---|
| Update frequency | Every 2 hours | Every 20ms (50Hz) |
| Fault detection time | Up to 2 hours late | Instant (<100ms) |
| Data logging | Paper records, often lost | Digital, automatic, timestamped |
| Night shifts | Often skipped | Continuous 24/7 |
| Cost per year | £30K+ (engineer salary) | £15 one-time |

#### 4. HVAC Waste → Demand-Based Ventilation

```mermaid
graph LR
    CURRENT4[Current: HVAC at 100% all day, same in summer and winter, occupied or empty]
    GRIDBOX_SOL4[GridBox: Potentiometer = temperature setpoint → PWM adjusts fan speed → servo controls dampers per zone]
```

**Real savings calculation for a small factory:**

| Parameter | Value |
|---|---|
| Current HVAC consumption | 50 kWh/day |
| Average over-ventilation | 40% |
| Electricity cost (UK 2025) | £0.30/kWh |
| Daily waste | 50 × 0.4 = 20 kWh = **£6/day** |
| Annual waste | **£2,190/year** |
| GridBox cost | **£15 one-time** |
| **Payback period** | **2.5 days** |

#### 5. Regulatory Compliance → Automatic Reporting

| UK Regulation | Requirement | How GridBox Helps |
|---|---|---|
| **ESOS** (Energy Savings Opportunity Scheme) | Large companies must audit energy use every 4 years | GridBox logs all energy data automatically — audit-ready |
| **Climate Change Levy** | Tax on energy consumption | Lower consumption = lower tax. GridBox proves the reduction |
| **Net Zero 2050** | Government mandate to reach carbon neutrality | Demonstrates energy monitoring infrastructure |
| **ISO 50001** | Energy management system certification | GridBox provides the monitoring layer required |
| **HSE PUWER** | Employers must maintain work equipment | Vibration monitoring demonstrates proactive maintenance |
| **Building Regulations Part L** | Energy efficiency requirements for buildings | HVAC optimisation evidence |

### Who Buys This?

```mermaid
graph LR
    subgraph SMALL["Small Factories (80% of UK manufacturing)"]
        S1[Can't afford £50K SCADA]
        S2[Still use manual monitoring]
        S3[Need to meet ESOS requirements]
    end

    subgraph GOV["Government / Local Authority"]
        G1[Schools — HVAC energy reduction]
        G2[Council buildings — heating control]
        G3[Public infrastructure — pump stations]
    end

    subgraph DEVELOPING["Developing Countries"]
        D1[No grid infrastructure]
        D2[Manual water pumps]
        D3[No monitoring at all]
    end

    GRIDBOX_WHO[GridBox: £15 each] --> SMALL
    GRIDBOX_WHO --> GOV
    GRIDBOX_WHO --> DEVELOPING
```

| Customer | Problem | What They Buy |
|---|---|---|
| **Small factory owner** | "I can't afford Siemens but I need to cut energy costs" | GridBox as motor speed controller + energy monitor |
| **Facilities manager** | "Building HVAC runs 24/7, I need to show energy savings for ESOS audit" | GridBox as HVAC optimizer with data logging |
| **Council engineer** | "Our pump station has no monitoring, we only know it's broken when water stops" | GridBox as remote pump monitor with fault alerts |
| **NGO in developing country** | "Village water pump breaks and nobody knows for days" | GridBox as autonomous pump controller with wireless alert |
| **Government regulator** | "We need companies to prove they're reducing energy use" | GridBox provides automated energy audit data |

---

## EEE Theory Applied

This project applies concepts from the EEE curriculum:

### Faraday's Law — Motor as Generator (Concept)

$$V_{emf} = -N \frac{d\Phi}{dt}$$

For a DC motor used as generator, the back-EMF is:

$$V_{gen} = K_e \cdot \omega$$

Where $K_e$ is the motor voltage constant (V/rad/s) and $\omega$ is angular velocity. Our 12V PSU represents the output of such a generator. We assume the energy conversion has happened and focus on intelligent management.

### Kirchhoff's Laws — Power Bus Analysis

```mermaid
graph LR
    PSU_K[PSU: V_in] --> BUS_K[Bus]
    BUS_K --> M1_K[Motor 1: I₁]
    BUS_K --> M2_K[Motor 2: I₂]
    BUS_K --> L_K[LEDs: I₃]
```

**KCL (current conservation at bus node):**

$$I_{gen} = I_{motor1} + I_{motor2} + I_{loads}$$

If total load current exceeds supply → bus voltage drops → ADC detects sag → load shedding triggers. This is exactly how real grid operators manage supply/demand balance.

**KVL (voltage loop):**

$$V_{supply} - I \cdot R_{wire} - V_{load} = 0$$

### PWM Motor Speed Control

$$V_{effective} = D \times V_{supply}$$

Where $D$ is the duty cycle (0 to 1). PCA9685 generates PWM at 25–1000Hz. This is the same principle as Variable Frequency Drives (VFDs) in industrial HVAC and pump systems.

| Duty Cycle $D$ | $V_{eff}$ (from 5V) | Motor Speed |
|---|---|---|
| 0.25 | 1.25V | Slow — energy saving mode |
| 0.50 | 2.50V | Medium — normal operation |
| 0.75 | 3.75V | Fast — high demand |
| 1.00 | 5.00V | Maximum — emergency ventilation |

### Voltage Divider for ADC Measurement

$$V_{ADC} = V_{bus} \times \frac{R_2}{R_1 + R_2}$$

With $R_1 = R_2 = 10k\Omega$:

$$V_{ADC} = \frac{V_{bus}}{2}$$

This safely maps 0–6.6V bus to the Pico's 0–3.3V ADC range. Resistors from the assorted components kit.

### Power Calculations (Displayed on OLED)

| Metric | Formula | How We Measure |
|---|---|---|
| Bus voltage | $V = \frac{ADC_{raw} \times 3.3}{65535} \times 2$ | ADC + voltage divider |
| Motor current | $I = \frac{V_{supply} - V_{motor}}{R_{sense}}$ | Sense resistor from kit |
| Power consumed | $P = V \times I$ | Calculated per motor |
| Energy used | $E = \sum P \cdot \Delta t$ | Accumulated over time |
| Efficiency | $\eta = \frac{P_{useful}}{P_{input}} \times 100\%$ | Ratio of output to input |

### Vibration Analysis (IMU)

RMS acceleration magnitude:

$$a_{rms} = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

| $a_{rms}$ Range | Condition | ISO 10816 Equivalent |
|---|---|---|
| < 1g | Good | Zone A — newly commissioned |
| 1–2g | Acceptable | Zone B — unrestricted operation |
| 2–4g | Warning | Zone C — restricted operation |
| > 4g | Danger | Zone D — damage occurring |

This is the same standard used by power plant engineers worldwide.

---

## Physical Build

```mermaid
graph LR
    subgraph LEFT["Power + Actuators"]
        PSU_B[12V PSU]
        BUCK_B[Buck → 5V]
        M1_B[DC Motor 1]
        M2_B[DC Motor 2]
        S1_B[Servo 1]
        S2_B[Servo 2]
    end

    subgraph CENTRE["Controller"]
        PICO_B[Pico A + PCA9685 + nRF + IMU]
        LEDS_B[LED loads: P1 P2 P3 P4]
    end

    subgraph RIGHT["SCADA Console"]
        PICO2_B[Pico B + OLED + Joystick + Pot]
    end

    LEFT --> CENTRE
    CENTRE -->|wireless| RIGHT
```

| Part | Kit Item | System Role |
|---|---|---|
| 12V PSU | Provided | Recycled energy input |
| LM2596S buck converter | Provided | Voltage regulation (12V → 5V) |
| 300W buck-boost | Provided | High-power motor driving |
| DC motors × 2 | Provided | Actuators: fan + pump/conveyor |
| MG90S servos × 2 | Provided | Actuators: valve + gate/breaker |
| PCA9685 | Provided | 16-ch PWM for motors + servos |
| BMI160 IMU | Provided | Vibration monitoring |
| LEDs × 4 | From kit | Load indicators (P1–P4) |
| nRF24L01+ × 2 | Provided | Wireless SCADA link |
| OLED | Provided | Dashboard display |
| Joystick | Provided | Manual override |
| Potentiometer | Provided | Setpoint control |
| Breadboard + wire | Provided | Power bus + wiring |
| Resistors | From kit | Voltage dividers, current sense |

**Assembly time: ~2 hours.** No complex mechanics. Mount motors to breadboard, wire to PCA9685, connect sensors.

---

## Demo Script

```mermaid
graph LR
    D1[1. Power on] --> D2[2. System starts]
    D2 --> D3[3. Adjust setpoint]
    D3 --> D4[4. Fault inject]
    D4 --> D5[5. Recovery]
    D5 --> D6[6. Manual override]
```

| Step | Action | What Judges See |
|---|---|---|
| 1. Power on | Plug in PSU (recycled energy) | "This represents energy harvested from waste" |
| 2. System starts | Motors spin up, servos open, LEDs light | Autonomous startup — system initialises itself |
| 3. Adjust setpoint | Turn potentiometer | Motor speeds change in real-time. OLED updates. "Like adjusting a thermostat" |
| 4. Fault inject | Shake motor 1 (vibration fault) | **IMU detects → motor stops → backup activates → OLED: FAULT.** Judges hear the motor stop |
| 5. Recovery | Press joystick to reset | Motor restarts, system returns to normal. OLED: "RECOVERED" |
| 6. Manual override | Joystick controls motor speeds directly | Switch from autonomous to manual — full operator control |

**Pitch:** *"Recycled energy is only useful if you can manage it intelligently. GridBox monitors, decides, and acts — autonomously. When a motor is failing, it shuts it down before damage. When demand drops, it saves energy. When something goes wrong, it alerts the operator wirelessly. All for £15, no cloud, no subscription."*

---

## Scoring

| Category | Score | Why |
|---|---|---|
| **Problem Fit (30)** | **28** | 68% energy wasted. Smart infrastructure management is a real industry need. HVAC, water, factory all benefit |
| **Live Demo (25)** | **25** | Motors spin, turn pot → speed changes, shake motor → fault detection, wireless dashboard. Multiple interactive moments |
| **Technical (20)** | **20** | PWM motor control, PID speed regulation, vibration analysis (ISO 10816), autonomous load shedding, KCL/KVL power bus, wireless SCADA, ADC voltage measurement |
| **Innovation (15)** | **14** | Smart infrastructure at hackathon is unique. EEE theory applied practically. Multi-scenario applicability |
| **Docs (10)** | **9** | Circuit theory, power calculations, Mermaid diagrams, SCADA mockups |
| **Total** | **96** | |

---

## What Makes This Creative (Innovation Score: 15/15)

### Defending Against "This Isn't Creative"

A judge might say: *"You're just reading sensors and controlling motors. That's standard embedded systems."*

Here's why that argument fails:

**The iPhone didn't invent touchscreens, cameras, or phones.** It combined them in a way nobody had before. The creativity was in the **architecture and integration**, not the individual components.

GridBox does the same thing. Yes, reading an IMU is standard. Yes, PWM motor control is standard. But:

| "Standard" Component | What Other Teams Do | What GridBox Does (Creative) |
|---|---|---|
| IMU | Read tilt, show on screen | **10 industrial measurements from one chip** — vibration health, RPM, jam detection, leak detection, valve position, structural tilt, earthquake, fall detection, belt tension, door status. One £2 sensor replaces £18,760 of industrial equipment |
| PWM motor control | Set motor speed to fixed value | **Autonomous speed adjustment using Affinity Laws** — system knows that $P \propto n^3$ so reducing speed 20% saves 49% energy. It calculates and displays the savings LIVE |
| Wireless | Send data from A to B | **Full SCADA architecture** — factory floor controller + remote control room + web dashboard. Three-tier monitoring like a real industrial system |
| Servo | Move to an angle | **Autonomous circuit breakers** — servos make DECISIONS. Fault detected → servo disconnects the faulty motor, switches to backup, no human needed |
| OLED | Display numbers | **Sustainability scoring with formula** — calculates $\eta = \frac{P_{useful}}{P_{input}} \times (1 - \frac{waste}{total}) \times 100\%$ and grades the system A/B/C/D in real-time |
| Potentiometer | Read analog value | **Live PID tuning + setpoint control** — acts as a thermostat that the system RESPONDS to autonomously |

**The creativity is not in what we USE. It's in what we BUILD with it.**

### The Three Layers of Innovation

```mermaid
graph LR
    subgraph L1["Layer 1: Component Level (Not Creative)"]
        C1["Read IMU"]
        C2["Control motor"]
        C3["Send wireless"]
    end

    subgraph L2["Layer 2: Integration Level (Creative)"]
        I1["IMU → fault detection → servo disconnects motor"]
        I2["ADC → load shedding → priority scheduling"]
        I3["Pot → demand setpoint → cubic law speed control"]
    end

    subgraph L3["Layer 3: System Level (Highly Creative)"]
        S1["Closed-loop autonomous infrastructure"]
        S2["£15 replaces £162K industrial systems"]
        S3["One firmware → 4 factory types"]
        S4["Dumb vs Smart A/B comparison"]
        S5["Sustainability scoring formula"]
    end

    L1 -->|"everyone stops here"| L2
    L2 -->|"good teams reach here"| L3
```

**Other teams operate at Layer 1.** They read a sensor and display a value. That's a lab exercise, not innovation.

**Good teams reach Layer 2.** They connect sensor → decision → action. That's a project.

**We operate at Layer 3.** We build a complete autonomous system with quantified performance, cost disruption, and platform scalability. That's an **engineering company in a box.**

### 5 Specific Innovations No Other Team Will Have

| Innovation | Why It's Novel | Why It Matters |
|---|---|---|
| **1. Affinity Laws in firmware** | $P \propto n^3$ — we programmed the cubic power law into the speed controller. The system KNOWS that 20% slower = 49% less energy | No hackathon team has ever applied fluid dynamics laws in embedded firmware. This is mechanical engineering + EEE + CS crossover |
| **2. ISO 10816 vibration classification** | Industrial standard for machine health, implemented on a £2 IMU | We're not just measuring vibration — we're classifying it using the same standard that power plant engineers use |
| **3. One sensor, ten measurements** | BMI160 used for vibration, RPM, jam, leak, valve, tilt, earthquake, fall, tension, door — all from same chip | Creative repurposing of one component. Judges see the engineering thinking, not just the component |
| **4. Quantified sustainability** | Formula produces a grade (A/B/C/D) in real-time, not just "we're green" | Sustainability becomes measurable and provable. Judges can compare dumb vs smart mode with NUMBERS |
| **5. Cost disruption ratio** | £15 vs £162,500 = **1:10,833 cost reduction** | This isn't incremental improvement. It's a completely different price point that changes who can access this technology |

### The Ultimate Defense

> *"Is reading an IMU creative? No. Is controlling a motor creative? No. Is combining them into an autonomous infrastructure system that replaces £162,000 of industrial equipment for £15, applies cubic power laws to save 50% energy, classifies machine health using ISO standards, and produces a real-time sustainability score — all on a chip that costs less than a sandwich?*
>
> *Yes. That's creative."*

### Why Other Teams Score Low on Creativity

| What Other Teams Build | Why It's Not Creative |
|---|---|
| "IMU reads tilt → shows on OLED" | Everyone does this. No decisions, no autonomy |
| "Joystick controls servo" | It's a TV remote. No intelligence |
| "Wireless remote control car" | Fun but done a thousand times |
| "LED turns on when sensor detects X" | If/else statement with a light. Not a system |

### 7 Things That Make GridBox Creative

**1. It's a SYSTEM, Not a Gadget**

Other teams build one device. We build an **interconnected infrastructure** — generation, distribution, monitoring, control, and SCADA. It's a complete industrial system on a breadboard.

```mermaid
graph LR
    subgraph OTHER["Other Teams"]
        O[One input] --> P[One process] --> Q[One output]
    end

    subgraph OURS["GridBox"]
        A[Energy input] --> B[Smart distribution]
        B --> C[Multiple actuators]
        C --> D[Sensor feedback]
        D --> E[Autonomous decisions]
        E --> B
        E -->|wireless| F[Remote SCADA]
        F -->|override| E
    end
```

Other teams have a **chain.** We have a **closed loop with remote monitoring.** That's the difference between a toy and a system.

**2. Dumb vs Smart A/B Comparison**

During the demo, we run the system in two modes back-to-back:

| Mode | What Happens | Energy Used |
|---|---|---|
| **DUMB mode** (no GridBox intelligence) | Motors run at 100% constantly, no fault detection, no speed adjustment | 100% = wasteful |
| **SMART mode** (GridBox active) | Motors at optimal speed, auto-adjustment, fault detection, load shedding | 40-60% = efficient |

OLED shows the energy savings in real-time: **"SMART mode saved 52% energy vs DUMB mode."**

Judges can SEE the difference. That's not just a demo — it's a **proof of concept with measured results.**

**3. Physical Factory Model (Not Just Breadboards)**

Use cardboard, paper labels, and coloured wire to make it LOOK like a factory:

```
┌─────────────────────────────────────────────────┐
│  ╔═══════╗     ╔═══════╗     ╔═══════╗         │
│  ║ PUMP  ║────>║ FILL  ║────>║  QC   ║───> OUT │
│  ║ [M1]  ║     ║ [S1]  ║     ║ [S2]  ║         │
│  ╚═══════╝     ╚═══════╝     ╚═══════╝         │
│       │             │             │              │
│  ╔════╧════════════╧═════════════╧═══╗          │
│  ║          CONVEYOR BELT [M2]        ║          │
│  ╚════════════════════════════════════╝          │
│                                                  │
│  [Pico A]  [IMU]  [PCA9685]  [nRF]   [LEDs]    │
│  ─────────── FACTORY FLOOR ──────────────       │
├──────────────────────────────────────────────────┤
│        CONTROL ROOM (separate table)             │
│  [Pico B]  [OLED]  [Joystick]  [Pot]            │
└──────────────────────────────────────────────────┘
```

Labels on each station: "PUMP STATION", "FILLING", "QUALITY CHECK", "CONVEYOR". LEDs as "factory stack lights" (green/yellow/red). This transforms breadboards into a **miniature world** that judges can walk around and explore.

**4. Sustainability Scoring on OLED**

The system calculates and displays a real-time **sustainability score:**

$$\text{Sustainability Score} = \frac{\text{Useful output}}{\text{Total energy input}} \times \left(1 - \frac{\text{Waste events}}{\text{Total cycles}}\right) \times 100\%$$

OLED shows: **"SUSTAINABILITY: 87% — GRADE A"**

This makes "sustainability" a MEASURABLE outcome, not just a buzzword. Judges from ARM who care about ESG metrics will appreciate quantified sustainability.

**5. Web Dashboard (Laptop Monitoring)**

While the OLED shows factory floor data, a laptop next to it shows the **web dashboard** (from `src/web/app.py`) with:
- Live graphs of motor speed, vibration, power consumption
- Historical data over the demo session
- Fault timeline
- Energy savings comparison

Two screens: OLED for operator, laptop for manager. This demonstrates **multi-tier monitoring** — the same data presented differently for different users.

**6. The Two-Pico Split is GENUINE**

Other teams put everything on one Pico and use the second for something trivial. Our split is **architecturally meaningful:**

| Pico A (Factory Floor) | Pico B (Control Room) |
|---|---|
| Noisy environment | Clean office |
| Needs fast real-time control (100Hz) | Needs good UI (OLED, joystick) |
| Handles motors + sensors | Handles display + operator input |
| Could be in a hazardous area | Safe for humans |
| Wireless TX — pushes data out | Wireless RX — receives + displays |

In a real factory, the controller IS on the floor and the SCADA IS in the control room. We model this correctly. Judges who've worked in industry will recognise this immediately.

**7. Swappable Scenarios = Platform Thinking**

We demo ONE factory (water bottling). But we show the OLED with different labels for:
- Water plant → Greenhouse → Recycling → HVAC

Same firmware, different `config.py`. Tell judges: *"This isn't one product. It's a platform. The £15 controller is the same. Only the labels change."*

Platform thinking > product thinking. That's startup-level innovation at a hackathon.

### The Creative Pitch (30 Seconds)

> "Every team built a gadget. We built a system.
>
> This is a miniature smart factory — a water bottling plant powered by recycled energy. The pump fills bottles. The conveyor moves them. The quality gate sorts good from bad. All running autonomously.
>
> But here's the creative part: shake the pump — it detects the fault and shuts down before damage. Turn the dial — it adjusts speed and saves 50% energy. Look at the OLED — it calculates sustainability in real-time.
>
> Same £15 system runs a greenhouse tomorrow, a recycling plant next week, or a building's HVAC next month. It's not a product, it's a platform.
>
> We didn't build a project. We built an infrastructure company in a box."

---

## Why ARM Judges Love This

ARM makes chips for: smart meters, industrial IoT, grid infrastructure, edge computing. GridBox demonstrates ALL of these on their Cortex-M33 chip.

You're building a demo of ARM's own target market. On their chips. At their hackathon. Their engineers will recognise every design pattern: PWM motor control, wireless telemetry, edge computing decisions, condition monitoring. This is what ARM sells billions of chips for — and you built it for £15.

---

## Build Timeline

```mermaid
gantt
    title GridBox — 12 Hour Build Plan
    dateFormat HH:mm
    axisFormat %H:%M

    section Critical Path
    nRF24L01+ wireless link              :crit, 00:00, 1h
    ADC voltage sensing + calibration    :crit, 01:00, 1h
    PCA9685 motor + servo control        :crit, 02:00, 1h
    Autonomous load shedding logic       :crit, 03:00, 1h

    section Intelligence
    IMU vibration monitoring             :04:00, 1h
    Fault detection state machine        :05:00, 1h
    PWM speed control + PID              :06:00, 1h

    section Display
    OLED SCADA dashboard (4 views)       :07:00, 1h30min
    Joystick manual override mode        :08:30, 30min

    section Assembly
    Wire motors + servos + power bus     :04:00, 1h30min
    Mount IMU + voltage divider          :05:30, 30min

    section Polish
    Energy calculations + logging        :09:00, 1h
    Documentation                        :10:00, 1h
    Demo practice                        :11:00, 1h
```

---

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Motors draw too much current for Pico | PCA9685 + motor driver handle power. Pico only sends control signals |
| ADC voltage reading inaccurate | Calibrate at startup with known voltage. Use voltage divider for range |
| IMU vibration thresholds too sensitive | Tune thresholds with potentiometer. Adjustable during demo |
| "It's just motors turning on and off" | The INTELLIGENCE is the product. Emphasise autonomous decisions, not the actuators |
| Wireless drops packets | Running average on received data. Timeout → alert on OLED |

---

## Future Vision

> "Every building wastes 40% of its energy on HVAC alone. Every factory loses millions to undetected equipment faults. Every remote village lacks intelligent power management.
>
> GridBox is a £15 embedded system that takes recycled energy and manages it intelligently — variable speed control, autonomous fault detection, smart load shedding, and wireless monitoring.
>
> It's not a smart plug. It's a smart infrastructure controller. The same Pico that runs our demo can run a building's ventilation, a village's water pump, or a factory's production line.
>
> The energy is already there. We just need the brains to use it."
