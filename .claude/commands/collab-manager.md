Review and manage team branches for the hack-a-bot-2026 project.

## What to do

1. **Check all open PRs** — run `gh pr list --state open` and show a summary table
2. **Check branch status** — for each team branch (`wooseong/electronics`, `billy/mechanical`, `doyun/firmware`), show:
   - How many commits ahead/behind main
   - Last commit message and date
   - Any merge conflicts with main
3. **Check for unreviewed changes** — show files changed on each branch vs main
4. **Present options** — for each branch with changes, ask:
   - **Merge** — merge their PR to main (if PR exists)
   - **Review diff** — show the actual changes
   - **Skip** — leave for later
   - **Comment** — add a comment on their PR

## Format

Present results as a clean dashboard:

```
── Team Branch Status ──────────────────────────
Branch                    Commits   Last Update   Status
wooseong/electronics      +3        2h ago        PR #4 open
billy/mechanical          +1        30m ago       No PR
doyun/firmware            +5        5m ago        PR #5 open
────────────────────────────────────────────────
```

Then for each branch with changes, show the file list and ask what to do.

## Rules
- Never merge without showing the diff first
- Always pull latest main before checking conflicts
- If there are merge conflicts, warn clearly and do NOT auto-merge
- After merging a PR, delete the remote branch and recreate it from latest main
