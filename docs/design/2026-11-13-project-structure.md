# LOG project structure: the standard going forward

The owner, 2026-11-13: "the folder structure has been an absolute mess... We need to not only
reorganize everything cleanly, but keep a document that concretes how the structure will be going
forward."

This is that document. **Nothing has been moved.** It extends
[the art map](2026-11-12-art-reorg-map.md), which already measured `art\` and found the one fact
that decides the whole job. Read that one first for the art detail; this one covers the project.

---

## 1. What is actually there, measured 2026-11-13

| Area | Files | Tracked in git | The problem |
|---|---|---|---|
| `archive\` | 77,574 | 0 | frozen history, 64% of the project by file count |
| `scratch\` | 18,779 | 0 | throwaway, correctly untracked |
| `art\` | 15,032 | **135** | **his drawings are not in version control** |
| `scripts\` | 5,519 | 264 | `one-time\` is ignored, 150 task folders |
| `data\` | 2,774 | 0 | correct: ROMs are inputs, never committed |
| `docs\` | 712 | 683 | the one healthy area |
| `builds\` | 630 | 0 | 176 loose files at its root |

Depth runs to 16 folders. 2,996 files sit at depth 11 or deeper.

### The four faults that cause the rest

**1. His art is not backed up by git.** 135 of 15,032 files. `.gitignore` line 63 is `art/*` with a
short allowlist. His portraits, his sprite edits and every approved frame live outside version
control. This is what he meant by "things that should be uploaded are not", and it is the only fault
here that can lose work rather than waste time.

**2. Folder names are hardcoded 344 times across 55 files.** `log_paths.py` names only five art
roots. Every other folder is spelled at each use site, and 50 of those joins are in
`scripts\permanent\` alone. **This is why the mess has never been cleaned: a rename today means
editing dozens of files and hoping the grep was complete.**

**3. The same task has two homes.** 123 of 178 task folders exist under BOTH `docs\tasks\` and
`scripts\one-time\` with the identical name. A task's writing and its scripts are in separate trees.

**4. Version lives in the folder name.** 19 of the 35 `art\` folders are `gi_*`, including
`gi_ssj_v2`, `gi_ssj_v4`, `gi_ssj_v5`, `gi_ssj2_aura_v4`, `gi_ssj2_aura_v5`. They look abandoned.
**They are not: 29 of the 34 folders are live build inputs.** Only four have no reader.

---

## 2. The rules going forward

These are the rules. A new folder that breaks one of them is the mess coming back.

1. **One subject, one folder.** A folder is named for WHAT it holds, never for a version or a date.
   `art\characters\gohan\gi\` holds every gi version. `gi_ssj_v5` never exists again.
2. **A version is a file suffix or a dated subfolder, never a new top folder.**
3. **Three levels below a root, and no more.** `art\characters\gohan\gi\` is the limit. If a fourth
   feels needed, the thing is a new subject and belongs beside its parent, not under it.
4. **Every folder the code reads is named exactly once, in `log_paths.py`.** Code never spells a
   folder name. This is the rule that makes every future move a one-file change.
5. **Names are lowercase, hyphenated, no spaces and no `owner`.** `art\Owner Build - Trunks Tank\`
   breaks all three. Renaming it is HIS call, because it is his live art.
6. **One task, ONE folder.** `tasks\<date>-<topic>\` holds the task's brief, report, bible rows AND
   its scripts, together (owner, 2026-11-13: "merge"). `docs\tasks\` and `scripts\one-time\` stop
   existing as separate trees.
   **A task folder holds inputs, never outputs.** Scripts and writing live there and are tracked.
   What a script PRODUCES, meaning PNG dumps, logs and JSON, goes to `scratch\<date>-<topic>\` and
   is never tracked. This is what keeps the merged tree small enough to commit: `scripts\one-time\`
   is 4,778 files today, but only 1,420 are `.py`. The other 2,900 are output that belongs in
   scratch.
7. **`scratch\` is deletable without asking. `archive\` is frozen and no tool may read it.**
8. **These stay out of git, always:** `archive\`, `scratch\`, `data\`, `builds\`, `zhack\`, `kai\`.
   Each already has its own explicit `.gitignore` rule, so none can be added by accident. `archive\`
   is local only and stays in place (owner, 2026-11-13).

---

## 3. The target tree

```
LOG\
  art\                        every pixel we own or export
    characters\<name>\<form>\     gohan\gi\, vegeta\zplus\, piccolo\zplus\
    portraits\                    THE home for finished portraits, <id>_<name>.png
    portraits\sources\<name>\     his working files for one portrait
    effects\<effect>\             aura\, dust\, and whatever comes next
    ui\                           HUD icons, bar images, menu art
    reference\vanilla\            sets exported from the base ROM
    reference\buus-fury\          art exported from Buu's Fury
    tables\                       portraits.json, palette.json: a build interface, leave it
    locks\                        golden fingerprints
  builds\
    masters\                      the golden and dev master ROMs, latest only
    trials\<date>-<topic>\        one folder per TYPE, every version of it inside
    saves\                        the seed saves, log2_poc_r*.sav
  data\                         untouchable inputs: base ROMs, his saves and states
  docs\                       writing that outlives a task
    design\  ledger\  playbooks\  research\  backlog\
  tasks\<date>-<topic>\       ONE folder per task: brief, report, rows AND its scripts
  scripts\
    permanent\                    tools, patches, tests, log_paths.py
    permanent\build-lists\        the 21 build_list*.txt, out of the tool folder
  scratch\                      throwaway, deletable without asking
  archive\                      frozen, read by nothing
```

`effects\` is the expandable case he named. A new effect is one folder beside `aura\`, one line in
`log_paths.py`, and nothing else.

---

## 4. What the move costs, and the one thing that makes it safe

**Do not move anything before rule 4 is in force.** The order is not negotiable, because 29 of 34
art folders are live build inputs and a missed string breaks a build quietly.

| Step | What | Risk |
|---|---|---|
| 1 | Extend `log_paths.py` from 5 art names to every folder the code reads | none: the paths still point at today's layout |
| 2 | Replace all 344 literals with those constants, file by file, suite green after each | low, and the suite proves it |
| 3 | Add a test: **no file under `scripts\permanent\` outside `log_paths.py` may hold a folder name as a string literal** | this is what stops the mess returning |
| 4 | Move the folders and change `log_paths.py` only | one file, reversible |
| 5 | Rebuild both masters and compare SHA-1s to before the move | proves no build input changed |

Step 5 is the real proof. If both masters rebuild to the same hashes they had before, the move
changed nothing the game sees.

---

## 5. The decisions only he can make

| # | Decision | Why it matters |
|---|---|---|
| 1 | ~~Does `art\` go into git?~~ | **SETTLED (owner, 2026-11-13): "All final approved art."** Finished, approved art is tracked. Exports, kits and working rounds stay out. He also settled the shape: "Ours will always be separate from vanilla, like our white aura effect", so the tree splits `ours\`, `vanilla\` and `ported\` at the top, and everything is renamed to the convention. |
| 2 | ~~Do the two task trees merge into one?~~ | **SETTLED (owner, 2026-11-13): "merge."** One folder per task, holding its writing AND its scripts. See the task rule below. |
| 5a | ~~The 176 loose files in `builds\`~~ | **SETTLED (owner, 2026-11-13): newest ROM per trial, with its own save and state. Everything older goes, saves and states included.** About 2.7 GB freed. The delete list gets his yes before anything is removed. |
| 3 | **Rename `art\Owner Build - Trunks Tank\`?** | It breaks three naming rules, and it is his live art, so nobody touches it without his word. |
| 4 | ~~What happens to `archive\`?~~ | **SETTLED (owner, 2026-11-13): "Archive is local only, git ignored."** It stays where it is and never enters git. Already true: `.gitignore` line 18 is an explicit `archive/` rule and 0 of its 77,574 files are tracked. No action. |
| 5 | **The 176 loose files in `builds\`** | 48 ROMs and 128 saves and states with no folder. Some are old masters. Which are worth keeping? |

---

## 6. What can be done safely before any decision

These need no go-ahead and carry no build risk:

1. The four faults from the art map: `portraits.json` resolving against the wrong folder, the 10
   older finals still in `art\tables\portraits\`, and the three filenames carrying `owner`.
2. The four dead art folders: `finale`, `gi_base_v2`, `gi_ssj_v5`, `gi_ssj2_aura_v5`. No reader in
   `scripts\permanent\`.
3. The 16 loose files at the `art\` root, and the 176 at the `builds\` root, given a home.
4. Step 1 and step 2 above, the `log_paths.py` work, which is the prerequisite for everything else.

**Rules that hold throughout, his own:** copy, never move, until he says otherwise. Never read from,
write to or delete anything in `art\Owner Build - Trunks Tank\`. Ask before touching a file he may
have open. Back the tree up before the first move.
