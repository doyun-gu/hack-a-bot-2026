Quick overview of the entire team's progress.

## What to do

1. **Git status** — run `git fetch origin` then check all branches
2. **Open PRs** — `gh pr list --state open`
3. **Recent activity** — for each team member, show their last 3 commits:
   - `git log origin/wooseong/electronics --oneline -3`
   - `git log origin/billy/mechanical --oneline -3`
   - `git log origin/doyun/firmware --oneline -3`
   - `git log origin/main --oneline -3`
4. **Files changed** — what each person is working on (changed files vs main)

## Format

```
── Team Progress ───────────────────────────────
WOOSEONG (Electronics)
  Last commit: "Added MOSFET circuit for Motor 1" (2h ago)
  Files changed: 3  |  PR: #4 open  |  Status: ✓ ready

BILLY (Mechanical)
  Last commit: "Motor mount STL v2" (45m ago)
  Files changed: 5  |  PR: none     |  Status: working

DOYUN (Firmware)
  Last commit: "IMU driver complete" (10m ago)
  Files changed: 8  |  PR: #5 open  |  Status: ✓ ready

MAIN
  Last merge: "Merge wooseong/electronics #3" (3h ago)
  Total commits: 42
────────────────────────────────────────────────
```
