Sync all team branches with the latest main branch.

## What to do

1. Fetch all remote branches: `git fetch origin`
2. For each team branch (`wooseong/electronics`, `billy/mechanical`, `doyun/firmware`):
   - Check if it's behind main
   - If behind, show how many commits behind
   - Ask if I should update it (merge main into it)
3. After syncing, show the updated status

## Rules
- Never force-push to anyone's branch
- If there are merge conflicts during sync, stop and report — do NOT resolve automatically
- Show a clear before/after status
