# Firmware Versions

Each version is a **complete snapshot** you can flash directly onto the Picos. Pick the version, follow its README, flash it.

| Version | Date | Status | Key Features |
|---|---|---|---|
| [`01-v1/`](01-v1/) | 2026-03-21 | Code complete, untested | Full feature set: 13 master + 7 slave modules, wireless, IMU, sorting, OLED dashboard |
| [`02-v2/`](02-v2/) | 2026-03-21 | Code complete, untested | Multi-type datagram (6 packets), self-test + blink codes, dumb-vs-smart A/B, error handling hardened |
| [`03-v3/`](03-v3/) | 2026-03-21 | Code complete, untested | Mock data injection, C SDK stubs (4 modules), integration test (115 checks) |
| `04-demo/` | — | Planned | Final demo version — polished, tuned, rehearsed |

## How to Flash Any Version

```bash
# 1. Pick a version folder
cd firmware/01-v1

# 2. Flash master Pico (plug in Pico A)
mpremote cp shared/protocol.py :protocol.py
for f in master/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset

# 3. Flash slave Pico (plug in Pico B)
mpremote cp shared/protocol.py :protocol.py
for f in slave/*.py; do mpremote cp "$f" ":$(basename $f)"; done
mpremote reset
```

## Version Naming

```
firmware/
├── 01-v1/     ← first complete build
├── 02-v2/     ← after adding datagram + debug
├── 03-v3/     ← mock data + C SDK stubs + integration tests
└── 04-demo/   ← final demo day version
```

Each version folder has its own README listing exactly what features are included and what changed from the previous version.

## Development Source

The **live development code** is in `src/master-pico/micropython/` and `src/slave-pico/micropython/`. When a version is ready to test, it gets copied into a new `firmware/XX-vX/` snapshot.
