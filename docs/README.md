# Documentation

## Quick Links

| I want to... | Read this |
|---|---|
| **Get started fast** | [`01-overview/quick-start.md`](01-overview/quick-start.md) |
| **2-page summary for judges** | [`01-overview/project-summary.md`](01-overview/project-summary.md) |
| **Understand the project** | [`01-overview/context.md`](01-overview/context.md) |
| **See the full design** | [`01-overview/gridbox-design.md`](01-overview/gridbox-design.md) |
| **Wire the circuits** | [`02-electrical/wiring-connections.md`](02-electrical/wiring-connections.md) |
| **Build the factory** | [`03-factory/factory-design/`](03-factory/factory-design/) |
| **See my task list** | [`04-team/team-plan.md`](04-team/team-plan.md) |
| **Start firmware dev** | [`src/firmware-dev-plan.md`](../src/firmware-dev-plan.md) |

---

## Folder Structure

```
docs/
├── 01-overview/              ← START HERE
│   ├── quick-start.md        ← 10-step onboarding guide
│   ├── project-summary.md    ← 2-page executive summary for judges
│   ├── context.md            ← AI paste file (full project summary)
│   ├── gridbox-design.md     ← Main design doc (architecture, pins, BOM)
│   ├── gridbox-proposal.md   ← Why GridBox (problems, cost, creativity)
│   └── hardware-reference.md ← Kit component table
│
├── 02-electrical/            ← WOOSEONG + DOYUN
│   ├── wiring-connections.md ← 81 wires numbered + test order
│   ├── power-system.md       ← Power flow, waste targets, fault ladder
│   ├── motor-specs.md        ← DC motor datasheet + weight sensing
│   ├── datagram-design.md    ← nRF24L01+ wireless protocol (6 packet types)
│   ├── debug-system.md       ← LED blink codes, OLED errors, serial logging
│   ├── failure-handling.md   ← Failure scenarios (F1-F6) + simulator
│   └── energy-signature/     ← Current-based fault detection (Wooseong)
│       ├── README.md                    ← Energy signature index
│       ├── energy-signature-proposal.md ← Full proposal (30s learning, 500Hz)
│       ├── fault-models.md              ← 4 fault models (A-D)
│       ├── model-a-mechanical-load.md   ← Deep dive: mechanical load detection
│       └── smart-sorting.md             ← Current-based weight sorting
│
├── 03-factory/               ← BILLY + DOYUN
│   ├── dev-priority.md       ← What's locked vs flexible (4 phases)
│   ├── demo-script.md        ← Demo presentation script
│   └── factory-design/       ← Physical build
│       ├── README.md                  ← Factory design index
│       ├── weight-sensing-sorting.md  ← Current-based weight detection
│       ├── factory-layout.md          ← Physical dimensions + zones
│       ├── factory-build-plan.md      ← Battery sorting factory design
│       └── factory-deep-dive.md       ← 4 factory types scored
│
├── 04-team/                  ← EVERYONE
│   └── team-plan.md          ← 24-hour timeline, per-member tasks, milestones
│
├── 05-archive/               ← Past ideas (reference only)
│   └── ideas/
│       ├── README.md              ← Archive index
│       ├── idea-shortlist-v2.md   ← 14 ideas ranked
│       └── tremortray-proposal.md ← NeuroSync (98pts alternative)
│
└── images/                   ← Rendered diagrams + logos
    ├── logo.png
    ├── uom_black.png
    ├── demo_table_setup.png
    ├── factory_layout.png
    ├── factory_side_view.png
    └── steadyhand_*.png       ← SteadyHand concept art (archived)
```
