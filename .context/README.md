# .context/ — Project Context for AI Sessions

This directory contains structured context files that help Claude (or any AI assistant) understand the full state of the Hack-A-Bot 2026 project. These files are loaded after compaction or at session start to restore working knowledge.

## Files

| File | Purpose |
|---|---|
| `project-overview.md` | What GridBox is, hackathon rules, scoring, team, timeline |
| `architecture.md` | System architecture, hardware roles, communication protocol, software layers |
| `file-map.md` | Complete file tree with annotations — what every file/folder does |
| `hardware.md` | Pin mapping, wiring, components, SPI/I2C bus assignments |
| `dev-workflow.md` | How to build, flash, test, debug — all the commands |
| `status.md` | What's done, what's next, blockers — **update this frequently** |

## How to Use

- **CLAUDE.md** is the entry point — it references these files for depth
- **status.md** is the only file that changes frequently (update after each session)
- Other files change only when architecture/hardware/workflow changes
- After `/compact`, Claude reads these to restore full context
