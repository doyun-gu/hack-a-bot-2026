# Development Tasks — Background Worker

> Read CLAUDE.md for project context. Complete all tasks in order. Commit and push after each.

---

## Rules

1. Pull latest main first: `git pull origin main`
2. Commit and push after each task
3. Don't modify docs/ — only work in src/ and firmware/
4. Test what you can without hardware (Python tests, import checks, syntax)

---

## Task 1: Fix mock data to work with web dashboard

The mock data generator (src/tools/mock-data.py) currently writes to a file. Instead, make it work properly with the Flask dashboard.

Update `src/web/app.py`:
- Add a `/api/inject` POST endpoint that accepts JSON and stores it as latest_data + inserts to DB
- Add a `/api/mock/start` endpoint that starts generating mock data internally (no second terminal needed)
- Add a `/api/mock/stop` endpoint to stop mock generation

Update `src/tools/mock-data.py`:
- Use `urllib.request` to POST data to `http://localhost:8080/api/inject`
- Remove the file-writing approach

This way: run `python src/web/app.py --no-serial --mock` and the dashboard shows live mock data automatically.

Commit: `"Add mock data injection to web dashboard"`

---

## Task 2: Demo script document

Create `docs/03-factory/demo-script.md`:

Write the exact words the presenter says during the 3-minute demo. Include:
- Timing (second by second)
- Which team member does what
- What judges should be looking at
- What to say if something fails (backup script)
- Key pitch lines highlighted

Structure:
- Opening (15s) — who we are, what we built
- Normal operation (30s) — system running, explain what's happening
- Interactive (30s) — judge turns potentiometer, speed changes
- Sorting (30s) — items sorted by weight
- Fault injection (30s) — shake motor, show recovery
- Comparison (15s) — dumb vs smart savings
- Closing pitch (15s) — the £15 vs £162K line

Commit: `"Add demo script with exact presenter words"`

---

## Task 3: Presentation poster content

Create `docs/03-factory/poster-content.md`:

Content for a presentation poster/slide that the team can print or display. Include:
- Title + tagline
- Problem statement (3 bullet points with stats)
- Solution diagram (describe what to draw)
- Key metrics (£15 vs £162K, 69% savings, 7 fault types, <100ms response)
- Tech stack summary
- Team members
- QR code suggestion (link to GitHub repo)

Commit: `"Add poster content for presentation display"`

---

## Task 4: C SDK scaffolding for key modules

Scaffold the C SDK production firmware in `src/master-pico/c_sdk/`:

Create header files (.h) and stub implementations (.c) for:
- `bmi160.h/.c` — IMU driver function declarations
- `pca9685.h/.c` — PWM driver function declarations
- `nrf24l01.h/.c` — wireless driver function declarations
- `power_manager.h/.c` — ADC sensing function declarations

Each .h file should have:
- Include guards
- Function declarations matching the MicroPython API
- Struct definitions for return types
- Comments explaining each function

Each .c file should have:
- Include the header
- Stub implementations that print "[STUB] function_name called"
- TODO comments for actual implementation

Update CMakeLists.txt to include all new files.

Commit: `"Add C SDK header files and stubs for core modules"`

---

## Task 5: Integration test script

Create `src/master-pico/tests/test_integration.py`:

A single test that verifies ALL modules work together (without hardware):
- Import every module
- Verify config.py has all expected constants
- Verify protocol pack/unpack round-trips for all 6 packet types
- Verify fault_manager state transitions
- Verify sorter weight classification logic
- Verify power_manager calculations with fake ADC values
- Print summary: X/Y tests passed

This can run on the laptop (not on Pico) as a pre-flight check.

Commit: `"Add integration test — verify all modules without hardware"`

---

## Task 6: Create firmware v3 snapshot

After all tasks above:
1. Copy updated src/ files to `firmware/03-v3/`
2. Write `firmware/03-v3/README.md` with changelog from v2
3. Update `firmware/README.md` table

Commit: `"Create firmware v3 snapshot — mock data, C stubs, integration test"`
