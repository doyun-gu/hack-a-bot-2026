Review a specific pull request in detail.

## Arguments
$ARGUMENTS should be a PR number (e.g., `3`) or branch name (e.g., `wooseong/electronics`).

## What to do

1. If a PR number is given, fetch that PR: `gh pr view $ARGUMENTS`
2. If a branch name is given, find any open PR from that branch: `gh pr list --head $ARGUMENTS`
3. Show:
   - PR title, author, created date
   - Files changed with diff summary
   - Full diff for each file (use `gh pr diff`)
4. For each changed file, comment on:
   - Does it follow the project conventions?
   - Any issues with the pin mapping (does it match `docs/gridbox-design.md`)?
   - Any wiring concerns?
   - File in correct location per CONTRIBUTING.md?
5. Ask: **Approve and merge?** / **Request changes?** / **Skip?**

## If approving and merging
- Run `gh pr merge $PR_NUMBER --merge --delete-branch`
- Then recreate the branch from latest main: `git push origin main:$BRANCH_NAME`
- Confirm the branch is back and up to date

## Rules
- Always show the full diff before merging
- Check for any files that shouldn't be committed (.env, credentials, large binaries)
- Warn if PR changes config.py pin assignments — must match design doc
