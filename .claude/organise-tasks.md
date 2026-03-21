# Organisation & Documentation Tasks — Background Worker

> Read CLAUDE.md for project context. Complete all tasks. Commit and push after each.

---

## Rules

1. Pull latest main first: `git pull origin main`
2. Commit and push after each task
3. Be thorough — read every file before reorganising
4. Don't delete content — only restructure, merge duplicates, update links

---

## Task 1: Audit and clean up all docs

Read every file in docs/ and subdirectories. For each file:
- Is the content still accurate with the current design?
- Are file links/references correct (files may have moved)?
- Are there broken Mermaid diagrams?
- Is there duplicate content across files?

Fix any issues found. Update cross-references between docs.

Commit: `"Audit and fix all doc cross-references and accuracy"`

---

## Task 2: Create a project summary document

Create `docs/01-overview/project-summary.md`:

A 2-page executive summary of the entire project. Written for judges who have 5 minutes to read. Include:

1. **Problem** (3 sentences) — what's wrong with current industrial monitoring
2. **Solution** (3 sentences) — what GridBox does
3. **How it works** (simple diagram + 1 paragraph)
4. **Key metrics** — £15 vs £162K, 69% savings, <100ms fault response, 7 fault types
5. **Technical depth** — list of EEE concepts applied (1 line each)
6. **Innovation** — what no other team does (3 bullet points)
7. **Team** — names + roles
8. **Demo** — what judges will see in 3 minutes

Keep it under 500 words. No fluff.

Commit: `"Add 2-page project summary for judges"`

---

## Task 3: Update CLAUDE.md with latest state

Read the current CLAUDE.md and update it to reflect everything built today:
- Firmware v1, v2 complete (v3 in progress)
- All documentation organised in numbered folders
- Web dashboard with SQLite database
- Mock data generator
- Protocol v2 (6-type datagram)
- Debug system with LED blink codes
- Failure handling with simulator
- Pico tested (LED + ADC confirmed working)
- Team PRs merged (Wooseong: 4 PRs, Billy: 1 PR)
- 100+ commits

Update the "Current State" and "Next" sections.

Commit: `"Update CLAUDE.md to reflect completed work"`

---

## Task 4: Create a quick-start guide

Create `docs/01-overview/quick-start.md`:

For a new team member or judge who clones the repo. 10 steps to understand everything:

1. Read this README (2 min)
2. Read the project summary (2 min)
3. See the design doc for architecture (5 min)
4. See the wiring guide for hardware (5 min)
5. Flash firmware: `./src/tools/setup-pico.sh install` then `./src/tools/setup-pico.sh master`
6. Run web dashboard: `python src/web/app.py --no-serial --mock`
7. Run tests: `mpremote run src/master-pico/tests/test_basic_alive.py`
8. See team plan for who does what
9. See demo script for presentation
10. See failure handling for fault tolerance

Commit: `"Add quick-start guide for new team members"`

---

## Task 5: Update docs/README.md index

After all changes, update the main docs/README.md to accurately list every file in every subfolder with correct links and descriptions. Make sure nothing is missing and nothing links to a deleted file.

Commit: `"Update docs index with all current files"`

---

## Task 6: Update memory files

Update the project memory files in ~/.claude/projects/-Users-doyungu-Developer-hack-a-bot-2026/memory/:

Read the existing memory files and update them with:
- Current project state (firmware complete, testing phase)
- What was decided today (GridBox chosen, factory type, protocol design)
- Team workflow established (branches, PRs, contributor setup)
- Development tools set up (mpremote, tmux workers, mock data)

Don't create new memory files — just update the existing ones.

Commit: no commit needed — memory files are local only

---

## Task 7: Sync all team branches

After all changes are on main:

```bash
git push origin main:wooseong/electronics
git push origin main:doyun/firmware
```

For billy/mechanical — check if he has unmerged work first. If yes, create a PR and merge it, then sync.

Commit: no commit — just branch operations
