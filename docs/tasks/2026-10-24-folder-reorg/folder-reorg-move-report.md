# LOG folder move: report

For: I. Date: 2026-10-24, 3:15 PM to 6:05 PM Eastern. Brief: `folder-reorg-move.md` (this folder). Plan: `folder-reorg-plan.md` (this folder).

Every gate was green after every step. No step ran past a red gate. Two moves are pending, because File Explorer windows hold their folders open. Nothing was deleted except my own gate outputs.

---

## SHIPPED

| Ask (my words, short) | Result |
|---|---|
| Backup first, prove count and size | `archive\backups\2026-10-24_pre-reorg\`: 46,691 files, 2,527,533,606 bytes, equal to the source minus `data\`. Every SHA-1 also equal |
| Paths module first | `scripts\permanent\log_paths.py`. Every live path line (52 lines in 35 files) reads it. A later move is a one-line change |
| Top-level `art\` and `builds\` | Done. Build ROMs, saves and states in `builds\`; art in `art\` |
| Archive old builds r1-r17, r19-r26 with twins; test inputs stay | 80 files in `archive\builds\`. `log2_poc.gba`, r18 and r27-r39 stay in `builds\` |
| Archive every copy and the review renders; delete nothing | Bible copies, art snapshots, work rounds, review snapshots, review renders all in `archive\` |
| Keep `RE-BIBLE.md` | Kept. "RE" is explained in `LOG\README.md` |
| Rename `scripts\permanent\re\` to `disasm\` | Done |
| Keep the gi folder names, explain them | Kept. `art\README.md` explains each one |
| One dated folder per task under `docs\tasks\` | 84 task folders, plus `docs\ledger\`, `docs\design\`, `docs\research\` |
| Study scripts in `scripts\one-time\<date-task>\` | 54 study folders. Reports stay in the `docs\tasks\` folder of the same name |
| Rewrite live path references | Bible, data index, `global.md`, tables README, Ghidra README, 65 code files (docstrings), 4 memory notes. A recount found 0 old paths left in these files by the shapes it searches (relative backslash, forward slash, absolute `C:\...\LOG\`, the Ghidra recipe's `$L\` prefix), except 7 that name folders not moved yet. Prose with no path is not covered |
| Tasks put new files in the right place | `docs\tasks\global.md` (in every brief) now has one line: briefs and reports to `docs\tasks\<date>-<task>\`, study scripts to `scripts\one-time\<date>-<task>\`, trial ROMs to `builds\mockups\<date>-<task>\` |
| Alias table at the top of the bible and the build log | Done, in a folded block "Old paths (folder move, 2026-10-24)" |
| `LOG\README.md` (map, "where does X go") and `art\README.md` | Written |
| `data\` renames listed, not done | Section 5 |

## PENDING

| Item | Why | Next action |
|---|---|---|
| Move `scratch\sprites\` to `art\vanilla-sets\` (step 5b, second row) | Explorer (PID 64652) has `scratch\sprites\set56` open. Photos had frames from it open | Close that window, then run step 5b (section 6) |
| Move the base audit (step 9b): `scratch\re\base_audit\`, `scratch\art\base_audit\`, `scratch\art\ingame_r28\` | Explorer has `base_audit\to_edit` and `base_audit\sheets` open; you viewed `sheets\anim_09.png` at about 4:50 PM. This is your live sprite work, so I did not move it. No file in these folders changed since the backup (checked at 5:59 PM) | Close those windows, then run step 9b (section 6). It also fixes the `ba_*.py` path constants |
| Delete `__pycache__` folders (plan step 10) | The brief says delete nothing | Your call |
| `data\` renames | Need your yes per item | Section 5 |

---

## 1. Steps and gate results

Gates (plan 5.1): **G1** suite, test by test against the baseline (666 tests, all ok, 0 skips). **G2** every root in `log_paths.py` and 232 needed files exist. **G3** `log2_build.py --list` into a fresh folder under `scratch\reorg-check\` gives the r39 SHA-1 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`; that folder is deleted after. **G4** no old path of the step exists after G1 and G3. **G5** hash list before equals hash list after, file by file, with the step's renames applied.

| Step | What | Moves | Edits | G5 | G1 | G2 | G3 | G4 |
|---|---|---|---|---|---|---|---|---|
| 0 | Backup (copy) | | | count, size, SHA-1 equal | | | | |
| 2 | Baseline | | | | 666 ok | 232 ok | r39 | |
| 3 | `log_paths.py` and 81 line edits, nothing moved | 0 | 35 files | 0 mismatches | 666 ok | ok | r39 | ok |
| 4 | Builds, saves, test ROMs | 252 | 1 | 0 mismatches | 666 ok | ok | r39 | 2 ok |
| 5 (5a) | Live art, art tables, `re` to `disasm`, archived art | 40 | 1 | 0 mismatches | 666 ok | ok | r39 | 40 ok |
| 5b | `scratch\art\portraits\` to `art\portrait-sources\` | 1 | 1 | 0 mismatches | 666 ok | ok | r39 | 1 ok |
| 6 | Docs and 213 task files | 213 | 3 | 0 mismatches | 666 ok | ok | r39 | 213 ok |
| 7 | Studies, copies, exports, ROM copies | 165 | 0 | 0 mismatches | 666 ok | ok | r39 | 167 ok |
| 8 | Text rewrite and alias tables | 0 | 74 | 0 mismatches | 666 ok | ok | r39 | |
| 8b | Second text pass (see note 3) | 0 | 7 | 0 mismatches | 666 ok | ok | r39 | |
| 9a | Ki HUD study and its mockups | 4 | 1 | 0 mismatches | 666 ok | ok | r39 | 4 ok |
| 9t | Text rewrite for the ki HUD move | 0 | 7 | 0 mismatches | 666 ok | ok | r39 | |
| 10 | READMEs, toolkit saved, one comment aligned | 0 | 14 | 0 mismatches | 666 ok | ok | r39 | |

Also checked: after step 4, `inject.py` still finds r39 as the latest build and plans r40 next. The r39 ROM on disk has the r39 SHA-1.

### Notes

1. **Step 5 first attempt.** The rename of `scratch\art\portraits\` was refused twice ("Access is denied"). Each time the step's journal was undone, and a fresh hash list matched the pre-step list exactly (0 mismatches). A handle scan found the cause: File Explorer (PID 64652) had `portraits\remaster\swatch` open. I ran step 5 without the held rows (5a). The window closed by 4:50 PM, so 5b moved `portraits\` then.
2. **Freeze.** The plan wants no activity for 10 minutes. No file outside the move changed from step 3 to step 10: each step's "before" hash list equals the previous step's "after" hash list, path by path (10 pairs, 0 differences; `__pycache__` and test ROMs left out). This also proves the gate runs changed no tracked file. But at 3:19 PM Photos opened frames from `scratch\sprites\set56`, and Explorer windows stayed open in the base audit. So I took the held folders out of the steps instead of waiting.
3. **Step 8b.** The first pass missed absolute paths (`C:\...\LOG\scratch\...`, 5 bible source keys). It also turned `docs\RE-BIBLE.md` into `docs\research\re-BIBLE.md` in 4 places (`global.md`, `symbols.py` docstring, the project notes, `project_log_rom_hack.md`), because the `docs\re-` rule ignored case. Step 8b fixed all of them. The refcount now shows 0 live old paths.
4. **Plan deviations.** Review renders went to `archive\2026-10-18-art-review-renders\`, not `scratch\review-renders\` (your answer 3). Text updates for `global.md`, the README and the memory notes ran in step 8, not in steps 4 and 5. `log2_hack.gba`, `log2_pad16.*`, `log2_poc_gi.gba` and `log2_poc_t6.gba` have no r-number, so they stay in `builds\`. `log2_poc_r6_hud.gba` went to `archive\builds\` with r6.
5. **Homes I chose for files that landed after the survey.**
   - `celljr-fight-study*.md` to `docs\tasks\2026-10-24-celljr-fight-study\`; `scratch\re\celljr\` to `scripts\one-time\2026-10-24-celljr-fight-study\`.
   - `computer-save*.md` to `docs\tasks\2026-10-24-computer-save\`; `scratch\re\computer_save\` to `scripts\one-time\2026-10-24-computer-save\`.
   - `r39.md`, `r39-report.md`, `r39-suite.txt` to `docs\tasks\2026-10-24-r39-build\`; `scratch\re\r39\` to `scripts\one-time\2026-10-24-r39-build\`.
   - `hud-ki-proto-b*.md` to `docs\tasks\2026-10-24-hud-ki\`; `folder-reorg-move.md` to this folder.
   - `scratch\sdd\research-1/2/3-*.md` (three early briefs the plan did not list) to `docs\tasks\2026-10-17-bf-sprites-research\`, `-status-screen-research\`, `-engine-overview\`.
   - The exactly-once check ran right before step 6: 199 loose files, each with one home.

## 2. Final proof

| Check | Result |
|---|---|
| Suite | 666 tests, 666 ok, 0 skips, same test-by-test list as the baseline (step 10 run) |
| r39 rebuild | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` (step 10 run) |
| End-to-end G5 against the backup hash list | 45,557 backup files (no `__pycache__`, no test ROMs). Every one has a byte-equal copy in the tree now, except the 124 originals of files I edited (kept in `scratch\reorg-check\orig-step*\`) |
| `data\` | 2,760 files, same paths and SHA-1 as before. Nothing written under `data\` |

### File counts (backup counted apart)

| Top folder | Before | After |
|---|---|---|
| root files | 1 | 1 (`README.md`, rewritten) |
| `data\` | 2,760 | 2,760 |
| `docs\` | 14 | 216 |
| `scratch\` | 46,504 | 8,703 |
| `scripts\` | 172 | 2,173 |
| `art\` | | 4,849 |
| `builds\` | | 211 |
| `test-data\` | | 3 |
| `archive\` (without the backup) | | 30,549 |
| **Tree total** | **49,451** | **49,465** |
| Backup | | 46,691 |
| `scratch\reorg-check\` (journals, hash lists, gate logs) | | 223 |

Reconciliation: 49,451 + 13 files I created (`log_paths.py`, `art\README.md`, 11 toolkit files) + 1 new `__pycache__` file (`log_paths.cpython-314.pyc`) = 49,465. This report is one more file in `docs\`.

### Top two levels

```
LOG\
  README.md
  archive\    2026-10-16-ghidra-first-scripts, 2026-10-17-gi-art-rounds, 2026-10-17-review-snapshots,
              2026-10-18-art-review-renders, 2026-10-18-art-snapshots, 2026-10-22-gi-v3-preview,
              backups, bible-copies, builds
  art\        README.md, gi_* (11 folders), golden, locks, hand-fixes, cell_aura, portrait-sources,
              tables, work, anim, hud_z2*, review sheets
  builds\     170 ROM, .sav and state files, mockups\
  data\       Inferred, Sound, items, reference, roms, sprites (unchanged)
  docs\       RE-BIBLE.md, build-log.md, data-index.md, design, ledger, research, tasks
  scratch\    art (base audit only), audio-export, ghidra, re (base audit only), reorg-check, rom-copies,
              sprite-exports, sprites, test-roms, venv
  scripts\    one-time (55 folders), permanent
  test-data\  saves
```

## 3. What is left under `scratch\`, and why

| Folder | Why it is still there |
|---|---|
| `scratch\sprites\` | Pending step 5b. Tests read it |
| `scratch\art\base_audit\`, `scratch\art\ingame_r28\`, `scratch\re\base_audit\` | Pending step 9b (your open work) |
| `scratch\reorg-check\` | Journals, hash lists and the G1 and G2 baselines. Steps 5b and 9b need them. Keep it until both ran |
| `scratch\test-roms\`, `sprite-exports\`, `rom-copies\`, `audio-export\`, `ghidra\`, `venv\` | Throwaway by the plan. `venv\` stores its absolute path, so it was not moved |

## 4. Known gaps (not fixed)

- Study scripts in `scripts\one-time\` that name sibling folders or absolute `scratch\` paths do not run again without an edit (plan 3.5). Examples: the portrait pipeline (`2026-10-19-portrait-from-anime\anime\`), and `art\hand-fixes\view.py` and `fix.py` (they use `parents[3]` and read `frames_r12` and the r12 ROM, now in `archive\`). Promoting these tools is your decision 9 (later, with tests). The memory note `feedback_log_sprite_fixes_by_eye.md` now says this, so a future session does not run them blind.
- 30 code files now have docstring lines over 120 characters, because the new paths are longer. No linter here enforces a limit. Rewrapping is cosmetic.
- History files (briefs, reports, ledger, build log lines, study folders) keep their old paths. The alias tables map them.
- `LOG\README.md`, `art\README.md` and the alias tables say "not moved yet" for the pending folders. Update those lines after step 9b.

## 5. `data\` renames for your yes, item by item

No code reads any of these names. Only text names them.

| # | Old | New (proposed) | Why | What names it today |
|---|---|---|---|---|
| 1 | `data\Sound\` | `data\sounds\` | Lowercase rule | `docs\data-index.md` line 14 |
| 2 | `data\Inferred\` | `data\bf-tilesets\` | Says what it is: Buu's Fury tileset atlases | `docs\data-index.md` line 13 |
| 3 | `data\reference\images.jpg` | `gohan-ssj-gi-manga-color-page.jpg` | Manga color page, Super Saiyan Gohan in the purple gi | `golden-brief.md` line 23 (history) |
| 4 | `images (1).jpg` | `gohan-ssj2-anime-closeup.jpg` | Anime close-up, Super Saiyan 2 | `golden-fix-r2.md` line 28 (history) |
| 5 | `images (2).jpg` | `gohan-ssj2-statue-front.jpg` | Statue, front view | `golden-fix-r2.md` line 29 (history) |
| 6 | `images (3).jpg` | `gohan-ssj2-art-powerup.jpg` | Drawing, power-up scream with bolts | `golden-fix-r2.md` line 28 (history) |
| 7 | `images (4).jpg` | `gohan-ssj2-figure-jump.jpg` | Banpresto figure, jumping | `golden-fix-r2.md` line 28 (history) |
| 8 | `images (5).jpg` | `gohan-ssj2-side-view.jpg` | Fan drawing, side view | `golden-fix-r2.md` line 28 (history) |
| 9 | `images (6).jpg` | `gohan-ssj2-poster-cell-goku.jpg` | Poster with Cell and Goku | `docs\RE-BIBLE.md` line 898, ledger |
| 10 | `images (7).jpg` | `gohan-ssj2-full-body-bolts.jpg` | Full body with aura bolts (the "outline" bolt reference) | `docs\RE-BIBLE.md` line 898, ledger, `art\golden\work_r3\aura2\bolts.py` line 3 (comment) |

Note: there are 8 `images` files, not 7 (`images.jpg` plus `images (1)` to `images (7)`). For each yes I would also update the live text that names it and add an alias row.

## 6. How to run the pending steps

The toolkit is saved in `scripts\one-time\2026-10-24-folder-reorg\`. Each step checks for open windows first, takes the hash lists, moves, edits, runs all five gates, and undoes itself on any red gate.

The commands use full paths, so they run from any folder. `$K` is `scripts\one-time\2026-10-24-folder-reorg`.

1. Close the Explorer windows in `scratch\sprites\` and `scratch\art\base_audit\`, and the Photos window.
2. **Re-baseline first**, if any test, patch or `build_list.txt` changed after 6:05 PM today (for example an r40 build): `py -3 -P "$K\reorg.py" rebaseline`. It reruns the suite and the `--list` build on the tree as it is, and stores both as the new G1 and G3 targets. Without it, a new test or a new build list makes G1 or G3 red, and the step undoes itself. Expected output: `REBASELINE: G1 True G3 True -> GREEN`. (I ran it once at the end as a test; it stored the r39 SHA-1.)
3. `py -3 -P "$K\step.py" step5b` (moves `scratch\sprites\` to `art\vanilla-sets\`, sets `SPRITES` in `log_paths.py`).
4. `py -3 -P "$K\step.py" step9b` (moves the base audit, fixes the `ARMOR`, `BASE`, `OUT` and `PAL_SRC` constants and usage lines in the `ba_*.py` tools).
5. `py -3 -P "$K\step.py" step_text` (rewrites the remaining text and clears the alias markers).
6. Check one base audit tool by a print-only run, for example `ba_pair.py` on one key. Do not use `ba_sheet.py` as the check: it rewrites `sheets\` and `gifs\`.

Expected output of steps 3 to 5: a `GATES ... GREEN` line, then `<step> GREEN`. A step that finds a window holding one of its folders stops before it moves anything (`HELD OPEN by another process`). I smoke-tested the saved toolkit from its folder: it builds the 5b table (1 move), the 9b table (3 moves, 20 edits in 8 `ba_*.py` files) and the text table without errors.
