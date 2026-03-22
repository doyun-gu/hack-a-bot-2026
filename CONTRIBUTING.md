# How to Contribute — Step-by-Step Guide

> Follow these steps exactly. If you're unsure, ask Doyun.

---

## Step 1: Clone the Repo (One Time Only)

Open your terminal and run:

```bash
git clone https://github.com/doyun-gu/hack-a-bot-2026.git
cd hack-a-bot-2026
```

---

## Step 2: Create Your Branch (One Time Only)

**You CANNOT push directly to `main`.** You must work on your own branch.

### If you are Wooseong (Electronics):

```bash
git checkout -b wooseong/electronics
git push -u origin wooseong/electronics
```

### If you are Billy (Mechatronics):

```bash
git checkout -b billy/mechanical
git push -u origin billy/mechanical
```

### If you are Doyun (Firmware):

```bash
git checkout -b doyun/firmware
git push -u origin doyun/firmware
```

**After this, you stay on your branch.** All your work goes here.

---

## Step 3: Do Your Work

Edit files, add new files, whatever you need. Then save your changes:

```bash
# See what changed
git status

# Add your changes
git add .

# Commit with a message describing what you did
git commit -m "Added motor mount STL file"

# Push to GitHub
git push
```

**Repeat this every time you finish a piece of work.** Commit often — small commits are better than one giant one.

---

## Step 4: Get Latest Changes from Main

If Doyun has merged new changes into `main` and you want them:

```bash
git fetch origin
git merge origin/main
```

If there's a conflict, ask Doyun.

---

## Step 5: When Your Work is Ready — Create a Pull Request

When you've finished a task and want it merged into `main`:

### Option A: From GitHub Website

1. Go to https://github.com/doyun-gu/hack-a-bot-2026
2. You'll see a banner: "wooseong/electronics had recent pushes — Compare & pull request"
3. Click **"Compare & pull request"**
4. Write a short title: "Add MOSFET switching circuits"
5. Click **"Create pull request"**
6. **Doyun will review and merge it**

### Option B: From Terminal

```bash
gh pr create --title "Add motor mount designs" --body "Added STL files for motor 1 and motor 2 mounts"
```

---

## Step 6: After Doyun Merges Your PR

Update your branch with the latest `main`:

```bash
git fetch origin
git merge origin/main
git push
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│  DAILY WORKFLOW                         │
│                                         │
│  1. git pull                (get latest)│
│  2. (do your work)                      │
│  3. git add .              (stage)      │
│  4. git commit -m "message" (save)      │
│  5. git push               (upload)     │
│  6. Create PR when ready   (request)    │
│  7. Doyun reviews + merges              │
└─────────────────────────────────────────┘
```

---

## What Goes Where

### Wooseong — Electronics

Put your files in:
```
src/hardware/wiring/       ← wiring diagrams, photos of circuits
src/hardware/datasheets/   ← component datasheets you reference
media/                     ← photos of your build progress
```

### Billy — Mechatronics

Put your files in:
```
src/hardware/cad/          ← STL files, Fusion 360 exports, CAD designs
src/hardware/              ← assembly photos, dimension notes
media/                     ← photos and videos of build progress
```

### Doyun — Firmware

Put your files in:
```
src/master-pico/           ← Pico A firmware
src/slave-pico/            ← Pico B firmware
src/web/                   ← web dashboard
docs/                      ← documentation updates
```

---

## Rules

1. **Never push to `main` directly** — it's protected. Use your branch + PR
2. **Commit often** — every meaningful change, not one giant commit at the end
3. **Write clear commit messages** — "Added motor mount" not "stuff"
4. **Take photos** — put them in `media/` with descriptive names
5. **If something breaks, tell the team** — don't debug alone for hours
6. **If you're stuck with git, ask Doyun**

---

## Emergency Git Commands

```bash
# I accidentally committed to main
git reset HEAD~1                    # undo last commit (keeps files)
git checkout -b my-branch           # create your branch
git add . && git commit -m "fix"    # recommit on correct branch

# I have merge conflicts
git status                          # see conflicted files
# Open the file, look for <<<< ==== >>>> markers
# Keep the code you want, delete the markers
git add . && git commit -m "resolve conflicts"

# I broke everything
git stash                           # save your changes
git checkout main                   # go back to clean main
git pull                            # get latest
git checkout -b my-branch-v2        # start fresh branch
git stash pop                       # bring back your changes
```
