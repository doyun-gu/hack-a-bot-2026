# Documentation

## Quick Links

| I want to... | Read this |
|---|---|
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
│   ├── context.md            ← AI paste file (full project summary)
│   ├── gridbox-design.md     ← Main design doc (architecture, pins, BOM)
│   ├── gridbox-proposal.md   ← Why GridBox (problems, cost, creativity)
│   └── hardware-reference.md ← Kit component table
│
├── 02-electrical/            ← WOOSEONG + DOYUN
│   ├── wiring-connections.md ← 81 wires numbered + test order
│   ├── power-system.md       ← Power flow, waste targets, fault ladder
│   └── energy-signature/     ← Current-based fault detection (Wooseong)
│       ├── energy-signature-proposal.md
│       ├── fault-models.md
│       ├── model-a-mechanical-load.md
│       └── smart-sorting.md
│
├── 03-factory/               ← BILLY + DOYUN
│   ├── dev-priority.md       ← What's locked vs flexible
│   └── factory-design/       ← Physical build
│       ├── weight-sensing-sorting.md
│       ├── factory-layout.md
│       ├── factory-build-plan.md
│       └── factory-deep-dive.md
│
├── 04-team/                  ← EVERYONE
│   └── team-plan.md          ← Task lists, timeline, milestones
│
├── 05-archive/               ← Past ideas (reference only)
│   └── ideas/
│       ├── idea-shortlist-v2.md
│       └── tremortray-proposal.md
│
└── images/                   ← Rendered diagrams
```
