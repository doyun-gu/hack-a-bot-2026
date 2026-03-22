# Project Overview

## Hackathon

- **Event:** Hack-A-Bot 2026 (24-hour hackathon)
- **Sponsors:** ARM + EEESoc (University of Manchester)
- **Date:** TBD
- **Team:** 3 members
  - **Doyun** — firmware, software, AI-assisted development (lead dev)
  - **Wooseong** — electronics, wiring, circuit testing
  - **Billy** — mechanical chassis, factory model

## Judging Criteria

| Category | Weight | Our Strategy |
|---|---|---|
| Problem Fit | 30 | Smart grid replaces £162K industrial systems for £15 |
| Live Demo | 25 | Miniature water bottling plant running autonomously |
| Technical | 20 | Dual-core Pico, wireless SCADA, real-time fault detection |
| Innovation | 15 | Pico IS the switching fabric — ADC=sensors, GPIO=switches |
| Documentation | 10 | Extensive docs, Mermaid diagrams, design docs |

## Chosen Idea: GridBox — Smart Infrastructure Control System

A £15 smart infrastructure controller powered by recycled energy:
- **Senses** power usage at every branch via ADC
- **Routes** excess power autonomously via GPIO-controlled MOSFETs
- **Detects** equipment faults via IMU vibration analysis
- **Reports** wirelessly to a SCADA dashboard

**Demo scenario:** Miniature smart water bottling plant with pump, fill valve, conveyor, quality gate — all running autonomously with fault detection and wireless monitoring.

## Core Innovation

The Pico IS the power grid's switching fabric:
- ADC pins = power sensors at every branch
- GPIO pins + MOSFETs = electronic switches routing power
- Firmware = brain that decides where power goes
- Closed loop: sense → calculate → decide → route → verify

## Key EEE Theory

- **Affinity Laws:** P ∝ n³ (20% slower = 49% less power)
- **KCL/KVL** on power bus for energy balance
- **Voltage divider** for safe ADC measurement (12V → 3.3V)
- **Current sensing** via sense resistors (I = V/R)
- **ISO 10816** vibration classification for fault detection
- **PWM motor control:** V_eff = D × V_supply
