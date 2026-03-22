# Documentation

## Quick Links

| I want to... | Read this |
|---|---|
| **Get started fast** | [`01-overview/quick-start.md`](01-overview/quick-start.md) |
| **2-page summary for judges** | [`01-overview/project-summary.md`](01-overview/project-summary.md) |
| **Understand the full project** | [`01-overview/context.md`](01-overview/context.md) |
| **See the full design** | [`01-overview/gridbox-design.md`](01-overview/gridbox-design.md) |
| **Wire the circuits** | [`02-electrical/wiring-connections.md`](02-electrical/wiring-connections.md) |
| **Build the factory** | [`03-factory/factory-design/`](03-factory/factory-design/) |
| **See my task list** | [`04-team/team-plan.md`](04-team/team-plan.md) |

---

## Folder Structure

```
docs/
├── 01-overview/                ← START HERE
│   ├── quick-start.md          ← 10-step onboarding guide
│   ├── project-summary.md      ← 2-page executive summary for judges
│   ├── context.md              ← Full project context document
│   ├── gridbox-design.md       ← Main design doc (architecture, pins, BOM)
│   ├── gridbox-proposal.md     ← Why GridBox (problems, cost, creativity)
│   ├── hardware-reference.md   ← Kit component table
│   └── architecture-diagram.md ← System architecture Mermaid diagrams
│
├── 02-electrical/              ← WOOSEONG + DOYUN
│   ├── wiring-connections.md   ← ~66 wires numbered + test order + progress
│   ├── power-system.md         ← Power flow, waste targets, fault ladder
│   ├── power-budget.md         ← Power consumption analysis
│   ├── motor-specs.md          ← DC motor datasheet + weight sensing
│   ├── component-values.md     ← Resistor/capacitor values + alternatives
│   ├── nrf-wiring.md           ← nRF24L01+ wiring guide + safety rules
│   ├── max7219-wiring.md       ← MAX7219 7-segment display wiring
│   ├── datagram-design.md      ← nRF24L01+ wireless protocol (6 packet types)
│   ├── wireless-reliability.md ← 5-layer wireless reliability strategy
│   ├── debug-system.md         ← LED blink codes, OLED errors, serial logging
│   ├── failure-handling.md     ← Failure scenarios (F1-F6) + simulator
│   └── energy-signature/       ← Current-based fault detection
│       ├── README.md                    ← Energy signature index
│       ├── energy-signature-proposal.md ← Full proposal (30s learning, 500Hz)
│       ├── fault-models.md              ← 4 fault models (A-D)
│       ├── model-a-mechanical-load.md   ← Deep dive: mechanical load detection
│       └── smart-sorting.md             ← Current-based weight sorting
│
├── 03-factory/                 ← BILLY + DOYUN
│   ├── dev-priority.md         ← What's locked vs flexible (4 phases)
│   ├── demo-script.md          ← 3-minute demo presentation script
│   ├── demo-preparation.md     ← Pre-demo setup checklist
│   ├── technical-summary.md    ← Technical overview for judges
│   ├── poster-content.md       ← Poster text and layout guide
│   ├── presentation_diagrams.md ← Mermaid diagrams for slides
│   ├── presentation_ref.md     ← Presentation reference material
│   ├── conveyor-calculations.md ← Belt speed, motor, sorting calcs
│   ├── reference-cad-models.md ← CAD reference links
│   └── factory-design/         ← Physical build
│       ├── README.md                  ← Factory design index
│       ├── weight-sensing-sorting.md  ← Current-based weight detection
│       ├── factory-layout.md          ← Physical dimensions + zones
│       ├── factory-full-layout.md     ← Complete factory schematic
│       ├── factory-build-plan.md      ← Battery sorting factory design
│       ├── factory-deep-dive.md       ← 4 factory types scored
│       ├── factory-options.md         ← Factory concept options
│       └── factory-options-v2.md      ← Revised factory options
│
├── 04-team/                    ← EVERYONE
│   └── team-plan.md            ← 24-hour timeline, per-member tasks, milestones
│
├── 05-archive/                 ← Past ideas (reference only)
│   └── ideas/
│       ├── README.md                ← Archive index
│       ├── idea-shortlist.md        ← Original idea shortlist
│       ├── idea-shortlist-v2.md     ← 14 ideas ranked (GridBox chosen, 96/100)
│       ├── tremortray-proposal.md   ← NeuroSync (98pts alternative)
│       └── steadyhand-proposal.md   ← SteadyHand (95pts alternative)
│
└── images/                     ← Reference images + diagrams
    ├── logo.png, uom_black.png            ← Branding
    ├── pico2_pinout_reference.png         ← Pico 2 pinout
    ├── nrf_pinout_*.png                   ← nRF24L01+ pinout + capacitor
    ├── max7219_pinout_reference.webp      ← MAX7219 pinout
    ├── 2N2222-pinout.webp                 ← 2N2222 transistor pinout
    ├── schematic_*.png                    ← Circuit schematics (power, I2C, motor, ADC)
    ├── factory_*.png                      ← Factory layout diagrams
    ├── demo_table_setup.png               ← Demo day table arrangement
    ├── ref_*.png                          ← Reference photos (conveyors, sorters)
    └── steadyhand_*.png                   ← SteadyHand concept art (archived)
```
