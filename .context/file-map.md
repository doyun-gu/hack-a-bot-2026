# File Map

Complete annotated file tree. Files marked with * are the most important to read first.

```
hack-a-bot-2026/
│
├── CLAUDE.md *                    # Project instructions for AI — single source of truth
├── CONTRIBUTING.md                # Team contribution guidelines
├── README.md                      # GitHub landing page
├── build-c.sh                     # Quick script to build C SDK firmware
├── .gitignore
│
├── .claude/                       # Claude Code config
│   ├── settings.local.json        # Local permissions (auto-commit, etc.)
│   ├── commands/                  # Custom slash commands
│   │   ├── collab-manager.md
│   │   ├── review-pr.md
│   │   ├── sync-branches.md
│   │   └── team-status.md
│   └── *-task.md                  # Task descriptions for worker dispatch
│
├── .context/                      # THIS DIRECTORY — AI context files
│   ├── README.md
│   ├── project-overview.md
│   ├── architecture.md
│   ├── file-map.md                # (this file)
│   ├── hardware.md
│   ├── dev-workflow.md
│   └── status.md
│
├── docs/                          # All documentation (GitHub-rendered)
│   ├── README.md                  # Docs index
│   ├── 01-overview/               # High-level project docs
│   │   ├── gridbox-design.md *    # THE design doc — architecture, pins, wiring, demo
│   │   ├── gridbox-proposal.md    # Full proposal with EEE theory
│   │   ├── hardware-reference.md  # Component datasheets summary
│   │   ├── project-summary.md     # One-page summary
│   │   ├── quick-start.md         # Getting started guide
│   │   └── context.md             # Early context doc
│   ├── 02-electrical/             # Electrical engineering docs
│   │   ├── wiring-connections.md *# 81-wire wiring plan
│   │   ├── nrf-wiring.md         # nRF24L01+ wiring guide with pinout images
│   │   ├── max7219-wiring.md     # MAX7219 7-seg wiring + indicator tables
│   │   ├── datagram-design.md    # Wireless protocol design
│   │   ├── debug-system.md       # LED blink codes + OLED error messages
│   │   ├── failure-handling.md   # F1-F6 fault handling protocol
│   │   ├── power-system.md       # Power supply design
│   │   ├── power-budget.md       # Current budget for all components
│   │   ├── component-values.md   # Resistor/capacitor values
│   │   ├── motor-specs.md        # DC motor specifications
│   │   ├── wireless-reliability.md # nRF reliability analysis
│   │   └── energy-signature/     # Vibration-based fault detection
│   │       ├── README.md
│   │       ├── energy-signature-proposal.md
│   │       ├── fault-models.md
│   │       ├── model-a-mechanical-load.md
│   │       └── smart-sorting.md
│   ├── 03-factory/               # Factory/demo design
│   │   ├── demo-script.md        # Demo day script
│   │   ├── conveyor-calculations.md
│   │   ├── poster-content.md
│   │   ├── dev-priority.md
│   │   ├── reference-cad-models.md
│   │   └── factory-design/       # Multiple factory layout iterations
│   ├── 04-team/                  # Team management
│   │   └── team-plan.md
│   ├── 05-archive/               # Old/rejected ideas
│   │   └── ideas/
│   │       ├── idea-shortlist-v2.md
│   │       ├── tremortray-proposal.md  # NeuroSync (98pts) — rejected
│   │       └── steadyhand-proposal.md  # SteadyHand (95pts) — rejected
│   └── images/                   # Reference images for docs
│       ├── nrf24l01_pinout.webp
│       ├── pico2_pinout.webp
│       └── max7219_pinout_reference.webp
│
├── src/                          # ACTIVE SOURCE CODE
│   ├── master-pico/              # Pico A — Grid Controller
│   │   ├── micropython/          # MicroPython firmware (16 modules)
│   │   │   ├── main.py *         # Dual-core orchestrator
│   │   │   ├── boot.py           # Pre-main setup
│   │   │   ├── config.py *       # Pin assignments + constants
│   │   │   ├── power_manager.py  # ADC sensing + power routing
│   │   │   ├── motor_control.py  # PWM motor speed control
│   │   │   ├── fault_manager.py  # F1-F6 fault handling
│   │   │   ├── energy_signature.py # Vibration fault classification
│   │   │   ├── bmi160.py         # IMU driver (I2C)
│   │   │   ├── pca9685.py        # Servo PWM driver (I2C)
│   │   │   ├── nrf24l01.py       # Wireless transceiver (SPI)
│   │   │   ├── heartbeat.py      # Timer-driven LED
│   │   │   ├── sorter.py         # Quality gate logic
│   │   │   ├── calibration.py    # ADC calibration
│   │   │   ├── led_stations.py   # Status LED control
│   │   │   ├── imu_reader.py     # IMU data reader
│   │   │   └── packet_tracker.py # Wireless packet stats
│   │   ├── tests/                # Hardware test scripts (28 tests)
│   │   │   ├── test_nrf_debug.py     # nRF SPI register test
│   │   │   ├── test_wireless.py      # PING sender (two-Pico test)
│   │   │   ├── test_imu.py           # BMI160 test
│   │   │   ├── test_motor.py         # DC motor test
│   │   │   ├── test_servo*.py        # Various servo tests (8 variants)
│   │   │   ├── test_adc*.py          # ADC tests
│   │   │   ├── test_led*.py          # LED tests
│   │   │   ├── test_7seg*.py         # 7-segment tests
│   │   │   └── test_integration.py   # Full integration test
│   │   └── c_sdk/
│   │       └── blink/            # Simple blink test (first C SDK test)
│   │
│   ├── slave-pico/               # Pico B — SCADA Station
│   │   ├── micropython/          # MicroPython firmware (12 modules)
│   │   │   ├── main.py *         # Display + wireless + input loop
│   │   │   ├── boot.py
│   │   │   ├── config.py *       # Pin assignments (SPI0, SPI1, I2C, ADC)
│   │   │   ├── dashboard.py      # OLED display layouts
│   │   │   ├── commander.py      # Command packet builder
│   │   │   ├── operator.py       # Joystick/pot input handler
│   │   │   ├── ssd1306.py        # OLED driver (I2C)
│   │   │   ├── nrf24l01.py       # Wireless transceiver (SPI0)
│   │   │   ├── heartbeat.py      # Timer-driven LED
│   │   │   ├── seg_display.py    # MAX7219 7-segment driver (SPI1)
│   │   │   ├── oled_default.py   # Default OLED screen
│   │   │   └── packet_tracker.py # Wireless packet stats
│   │   ├── tests/                # Hardware tests (6 tests)
│   │   │   ├── test_wireless.py      # PONG responder (two-Pico test)
│   │   │   ├── test_max7219.py       # 7-segment display test
│   │   │   ├── test_nrf_with_display.py # nRF + 7-seg combined test
│   │   │   └── test_oled*.py         # OLED display tests
│   │   └── c_sdk/ *              # C SDK firmware (production)
│   │       ├── CMakeLists.txt    # Build config — targets: gridbox_slave, test_hw
│   │       ├── config.h *        # All pin/bus definitions
│   │       ├── main.c            # Production main loop
│   │       ├── nrf24l01.c/h      # nRF driver
│   │       ├── ssd1306.c/h       # OLED driver
│   │       ├── max7219.c/h       # 7-segment driver
│   │       └── test_hw.c         # Combined HW test (nRF + 7-seg + LED)
│   │
│   ├── shared/                   # Shared between both Picos
│   │   └── protocol.py *        # 32-byte packet protocol (6 datagram types)
│   │
│   ├── web/                      # Web SCADA dashboard
│   │   ├── app.py               # Flask app + serial reader
│   │   ├── database.py          # SQLite schema
│   │   ├── gridbox.db           # SQLite database (generated)
│   │   └── templates/
│   │       └── index.html       # Dashboard UI
│   │
│   ├── tools/                    # Development tools
│   │   ├── flash.sh *           # Flash firmware to Pico via mpremote
│   │   ├── mock-data.py         # Generate mock data for dashboard testing
│   │   ├── setup-pico.sh        # Pico environment setup
│   │   └── setup-pico1.sh       # Alternative setup
│   │
│   ├── hardware/                 # Hardware documentation
│   │   ├── chassis/             # Mechanical (Billy)
│   │   └── electronics/         # Circuit designs + test logs (Wooseong)
│   │
│   └── firmware-dev-plan.md     # Firmware development plan
│
├── firmware/                     # FROZEN firmware snapshots
│   ├── README.md
│   ├── 01-v1/                   # v1: basic direct control
│   │   ├── master/ slave/ shared/
│   │   └── README.md
│   ├── 02-v2/                   # v2: datagram protocol + self-test
│   │   ├── master/ slave/ shared/
│   │   └── README.md
│   └── 03-v3/                   # v3: C SDK + integration tests
│       ├── master/ slave/ shared/ tests/
│       ├── c_sdk/               # C SDK drivers (frozen copy)
│       └── README.md
│
├── scripts/                      # Worker dispatch scripts
│   ├── start-c-sdk.sh
│   ├── start-firmware-v2.sh
│   ├── start-dashboard-redesign.sh
│   └── ... (various task starters)
│
├── media/                        # Photos and videos
│   ├── demo/                    # Demo day recordings
│   └── progress/                # Build progress photos
│
└── notes/                        # Local brainstorming (gitignored)
```

## File Counts

| Directory | Files | Description |
|---|---|---|
| `src/master-pico/micropython/` | 16 .py | Master firmware modules |
| `src/master-pico/tests/` | 28 .py | Master hardware tests |
| `src/slave-pico/micropython/` | 12 .py | Slave firmware modules |
| `src/slave-pico/tests/` | 6 .py | Slave hardware tests |
| `src/slave-pico/c_sdk/` | 10 files | C SDK production firmware |
| `src/shared/` | 1 .py | Shared protocol |
| `src/web/` | 4 files | Web dashboard |
| `src/tools/` | 4 files | Dev tools |
| `docs/` | ~35 .md | Documentation |
| `firmware/` | ~45 files | 3 frozen snapshots |
| **Total** | ~6300 | (including build artifacts) |
