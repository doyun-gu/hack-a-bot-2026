# GridBox — Demo & Presentation Preparation

> What to show, what to say, and how it maps to the scoring criteria.

---

## Scoring Alignment

| Category | Weight | What Judges Want | Our Evidence |
|---|---|---|---|
| **Problem Fit** | 30 | Real problem, real market, cost advantage | £15 vs £162K industrial SCADA. UK factories waste 30% energy. £180B/year downtime |
| **Live Demo** | 25 | Working hardware, real sensors, visible output | Motors, servos, IMU, wireless link, OLED + 7-seg displays, LED fade |
| **Technical** | 20 | Engineering depth, real-time, reliability | Dual-core Pico, 6-type datagram protocol, 200+ packets 0 errors, C SDK |
| **Innovation** | 15 | Novel use of basic hardware | Pico IS the switching fabric — ADC=sensors, GPIO=switches, firmware=brain |
| **Documentation** | 10 | Complete, clear, professional | 35+ docs, Mermaid diagrams, wiring tables, design doc |

---

## Presentation Structure (5 slides)

### Slide 1: Title + Hook
- **GridBox** — Smart Infrastructure Control for £15
- "What if a £15 microcontroller could replace a £162,000 industrial system?"
- Team photo / names
- ARM + EEESoc Hack-A-Bot 2026

### Slide 2: The Problem
- UK factories waste 30% energy running motors at full speed
- £180B/year lost to undetected equipment faults
- Industrial SCADA costs £162,000+ per installation
- 80% of small factories priced out of Industry 4.0

### Slide 3: Our Solution — GridBox
- Architecture diagram: Pico A (controller) ↔ wireless ↔ Pico B (SCADA)
- Sense → Calculate → Decide → Route → Verify (closed loop)
- Key components: 2x Pico 2, nRF24L01+, BMI160 IMU, PCA9685, motor driver
- Demo scenario: Smart water bottling plant

### Slide 4: Technical Innovation
- **The Pico IS the grid:** ADC pins = sensors, GPIO = switches, firmware = brain
- **EEE Theory Applied:**
  - Affinity Laws: P ∝ n³ (20% speed reduction = 49% power saving)
  - KCL/KVL for energy balance
  - ISO 10816 vibration classification
  - Current sensing: I = V/R via sense resistors
- **Wireless SCADA:** 32-byte datagrams, 6 packet types, 250kbps, 0% error rate
- **Energy recycling:** Capacitor captures wasted energy, LED demonstrates reuse

### Slide 5: Results + What We Built
- Progress: 77% wiring complete, 200+ commits, 35+ test scripts
- Wireless: 200+ packets, 0 errors, all 6 datagram types verified
- Hardware tested: nRF (both Picos), MAX7219 display, IMU, motor driver, recycle path
- Cost: £15 total BOM
- Team: Doyun (firmware), Wooseong (electronics), Billy (chassis)

---

## Live Demo Script (2-3 minutes)

### Act 1: Boot + Wireless Link (15s)
- Power on both Picos
- MAX7219 shows "LINK On" when wireless connects
- OLED shows system status
- **Tell judges:** "Two Picos talking wirelessly at 250kbps — zero configuration"

### Act 2: Normal Operation (45s)
- Motors running via motor driver (PCA9685 PWM control)
- Servos moving (fill valve + sort gate)
- ADC sensing bus voltage and motor current
- Real-time data on OLED + 7-segment display
- **Tell judges:** "Every 10ms, the Pico reads voltage and current on every branch, applies Kirchhoff's Current Law, and decides where power should flow"

### Act 3: IMU Fault Detection (30s)
- Shake the motor/breadboard
- BMI160 detects vibration > 2g
- System enters FAULT state
- Wireless alert sent to Pico B
- 7-segment shows fault code
- **Tell judges:** "One £2 IMU replaces £18,000 of industrial vibration analysis equipment. Same ISO 10816 classification, fraction of the cost"

### Act 4: Energy Recycling (30s)
- Toggle recycle path (GP13)
- Capacitor charges from grid
- LED glows and fades — stored energy being reused
- **Tell judges:** "This capacitor demonstrates energy recycling at bench scale. In production, replace with a supercapacitor bank — same firmware, same GPIO control"

### Act 5: Dashboard (30s)
- Show web dashboard on laptop (Flask + SQLite)
- Real-time charts, fault log, power readings
- Historical data stored in database
- **Tell judges:** "Full SCADA dashboard, zero licensing fees, runs on any browser"

### Act 6: Closing Pitch (15s)
- "£15 replaces £162,000. Senses, decides, routes, recovers — autonomously"
- "Every GPIO pin is a switch. Every ADC pin is a sensor. The Pico IS the grid"

---

## Key Numbers to Memorise

| Metric | Value | Context |
|---|---|---|
| Cost | **£15** vs £162,000 | 10,800x cheaper |
| Energy saving | **49%** | From Affinity Laws (P ∝ n³) |
| Fault response | **<100ms** | IMU detection to motor stop |
| Wireless | **250kbps** | 32-byte packets, 0% error rate |
| Protocol | **6 types** | POWER, STATUS, PRODUCTION, HEARTBEAT, ALERT, COMMAND |
| Loop speed | **100 Hz** | 10ms per control cycle |
| Wiring | **77% done** | 48/66 wires, 10/13 tasks |

---

## EEE Theory to Mention

These earn Technical + Innovation points:

1. **Affinity Laws:** P ∝ n³ — "20% slower saves 49% power, that's thermodynamics not software"
2. **KCL:** "Current balance checked every 10ms — if numbers don't add up, something's wrong"
3. **Voltage divider:** "12V bus measured safely through 10kΩ+10kΩ divider → 3.3V ADC range"
4. **Current sensing:** "I = V/R through 1Ω sense resistors on each motor branch"
5. **ISO 10816:** "Same vibration classification used by industrial plants, running on a £2 chip"
6. **PWM:** "V_eff = duty × V_supply — PCA9685 gives us 12-bit (4096-step) speed control"

---

## Backup Plans

| If this fails... | Do this instead |
|---|---|
| Wireless link drops | "Demonstrates fault tolerance — master continues autonomously" |
| Motor doesn't start | Reset Pico, show self-test LED codes |
| Dashboard freezes | `python app.py --no-serial --mock` for simulated data |
| IMU no response | Show recorded vibration data on dashboard |
| Nothing works | Full demo with mock data + architecture walkthrough |

---

## What to Print / Display

- [ ] Architecture diagram (Mermaid → PNG)
- [ ] Wiring connection table (for judges to inspect)
- [ ] Cost comparison table (£15 vs £162K breakdown)
- [ ] 2N2222 pinout reference (already in docs)
- [ ] Pico 2 pinout reference (already in docs)

---

## Team Roles During Demo

| Person | Role | Responsibility |
|---|---|---|
| **Doyun** | Presenter | Drives narrative, explains technical decisions |
| **Wooseong** | Operator | Controls hardware, triggers faults, monitors |
| **Billy** | Support | Manages dashboard laptop, handles backup demo |
