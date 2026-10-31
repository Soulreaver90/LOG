# LOG folder reorganization plan

For: I. Date: 2026-10-24. Status: **plan only. Nothing was moved, renamed or deleted.**
Raw counts behind every number: `scratch\sdd\slice1\folder-reorg-inventory.md`.

Labels: **C** = CONFIRMED (I read the file or ran the count), **L** = LIKELY, **S** = SPECULATIVE.

---

## 0. The short version

- 94 % of the 49,332 files sit in `scratch\` (C). The house rules call `scratch\` "safe to delete anytime".
- But `scratch\` holds your save files, your own drawings, every ROM you played, the art the game is built from, and files the tests read (C). Anyone who follows the house rule today loses things you cannot get back.
- The fix: give each kind of thing one home with a plain name, and keep only true throwaway in `scratch\`.
- The move is safe if we do it in small steps with a hard check after each step. Section 5 has the steps.
- You decide 10 things first (section 6). The biggest one: whether "art" and "builds" may be top-level folders.

---

## 1. Proposed layout

### 1.1 Two names you choose (decision 1)

The house rules say "do not invent new top-level names". Art and ROM builds have no home in the standard list. So the plan writes them as two placeholders. Your choice fills them in everywhere.

| Placeholder | Option A (recommended, needs your OK) | Option B (inside the house rules) |
|---|---|---|
| `<ART>` | `art\` | `scripts\permanent\art\` |
| `<BUILDS>` | `builds\` | `deploy\builds\` |

Why A: you asked for folders you can browse without help. "art" and "builds" are the two things you open most. Option B hides your sprites under `scripts\`.
Why B is possible: the build already keeps its portrait table in `scripts\permanent\art\` (C), and `deploy\` is a standard name.
Builds can never go under `data\`: `log2_save.py` line 431 refuses any path with a folder named `data`, and `log2_build.py` line 68 refuses `data\` too (C).

### 1.2 The tree

```
LOG\
  README.md                  Start here: this map and the "where does X go" table
  data\                      Your original files (ROM dumps, rips, references). Read only. Unchanged.
  docs\                      Everything to read
    RE-BIBLE.md              Every ROM fact ("RE" = reverse engineering). Name: decision 4
    build-log.md             Every build with its SHA-1
    data-index.md            What is in data\
    ledger\                  progress.md (the running log) and the morning reports
    design\                  The merge design and the slice plans
    research\                The research write-ups (today docs\re-*.md and docs\research-*.md)
    tasks\                   One dated folder per piece of work: the brief, the report, the review diff
      global.md              The rules every task brief includes
      2026-10-23-r35-build\  Example: r35.md (brief) and r35-build-report.md (report)
  <ART>\                     Art the game is built from, and your drawings
    README.md                What each folder is (new)
    gi_base\ gi_ssj_v2\ ...  Gohan gi frames per form. Names kept: the code reads them (decision 6)
    golden\                  Your approved model frames and your notes
    hand-fixes\              Per-frame hand fixes (today r12fix)
    locks\                   Fingerprints of approved frames
    cell_aura\               Super Perfect Cell aura (scale_15 is in the game)
    portrait-sources\        Portrait remasters, your portrait edits, references
    vanilla-sets\            The original game's sprite sets, exported (today scratch\sprites)
    base-audit\              The gi base frame audit, with your edits in owner\
    tables\                  The portrait and palette tables the inject tool uses
    work\                    Old-method frames one compare sheet still reads
    hud_z2_usable.bin ...    HUD icons
  <BUILDS>\                  Every ROM you play, with its .sav and .ss files (one flat folder)
    mockups\<task>\          Trial ROMs from studies (block, ki HUD, music)
  scripts\
    permanent\               The build, patches, tools and tests (stay where they are)
      disasm\                Our disassembler (today re\). Name: decision 5
      ghidra\                Ghidra seed scripts (.java)
      review\                snap.sh and package.sh (review diffs)
    one-time\                One dated folder per study: the scripts and the listings they made
      2026-10-23-r35-build\  Same folder name as its docs\tasks\ folder
  test-data\
    saves\                   Save files the tests read (today scratch\saves)
  archive\                   Old copies, by date: superseded art rounds, snapshots, bible copies
  scratch\                   Safe to delete: review renders, test ROMs, exports, ROM copies, venv, Ghidra projects
```

### 1.3 Where does X go (from now on)

| You have | Put it in |
|---|---|
| An original you dumped, ripped or downloaded | `data\` (only you add files here) |
| A fact about the ROM | One line in `docs\RE-BIBLE.md` |
| A new build ROM, its `.sav` and states | `<BUILDS>\` (the tools do this) |
| A trial ROM made by a study | `<BUILDS>\mockups\<date>-<task>\` |
| Art the game reads (gi frames, aura, icons, portraits) | `<ART>\` |
| Your own drawing or edit | `<ART>\...\owner\` next to the art it changes |
| A sprite set exported from a ROM | `<ART>\vanilla-sets\` if a tool reads it, else `scratch\sprite-exports\` |
| A task brief, report or review diff | `docs\tasks\<date>-<task>\` |
| A study script and the listing it printed | `scripts\one-time\<date>-<task>\` |
| A tool we will run again | `scripts\permanent\` |
| A research write-up | `docs\research\` |
| A save file a test reads | `test-data\saves\` |
| A review sheet, render, GIF or zoom | `scratch\review-renders\` |
| A superseded copy you want to keep | `archive\<date>-<what>\` |
| Anything you can rebuild with one command | `scratch\` |

---

## 2. Pain points

### 2.1 Data-loss risk (the most important finding)

`scratch\` is "deletable without asking" in the house rules and in `LOG\README.md` (C). Yet it holds:

| Irreplaceable or live item | Where today | Who needs it |
|---|---|---|
| Your play saves (58 `.sav`, 136 states) next to 66 build ROMs | `scratch\build\` | You; 8 test files (C) |
| Your drawings: golden frames and notes, base audit edits, portrait edits, Super Perfect Cell portrait v3 | `scratch\art\golden\owner\`, `scratch\art\base_audit\owner\`, `scratch\art\portraits\remaster\...\owner_edit\`, `...\superperfect\owner\` | Tests read some of them (C) |
| The art the build reads | `scratch\art\gi_base\`, `gi_ssj_v2\`, `gi_ssj2_aura\`, `gi_rage_aura\`, `cell_aura\scale_15\`, `hud_z2_*.bin`, `portraits\` | `log2_build.py --list` (C) |
| Test inputs | `scratch\saves\`, `scratch\sprites\`, `scratch\art\golden\`, `r12fix\snap_r18\`, `snap_r19\`, the brief `scratch\sdd\slice1\r35.md` | 19 of the 30 test files name a `scratch\` path (C) |
| The ledger you resume from | `scratch\sdd\slice1\progress.md` | You, every session |
| ~180 briefs and reports the bible cites as sources | `scratch\sdd\slice1\` | `docs\RE-BIBLE.md` source list (C) |

If `scratch\` were emptied today: `test_tools.py` and `test_hand_frames.py` error at once (no guard, C), the build stops because its art is gone (C), many other tests fail or skip quietly (L), and your saves and drawings are gone (C).

### 2.2 The same kind of thing in many places

| Kind | Places today (C) |
|---|---|
| Sprites and art | `data\sprites`, `scratch\sprites`, `scratch\art` (27 folders), `scratch\re\base_audit\set56`, `set59`, `scratch\re\r30\set59`, `set61`, `scratch\re\r31\set103`, `set158`, `scratch\re\set57_png`, `scratch\research\bf-sprites\log2`, plus full art copies in `scratch\re\intake`, `intake17`, `intake18`, `r19`, `r29`, `obfix` and six `sdd\slice1\*-work` folders |
| ROMs and saves | `data\roms`, `scratch\build`, `scratch\build\test`, `scratch\saves`, `scratch\ghidra`, `scratch\ghidra\seeded`, `scratch\audio\rom`, `scratch\audio\test`, `scratch\re\block\mockups`, `scratch\re\hud_ki\mockups`, `scratch\re\palslot`, `scratch\re\r20`, `scratch\re\toolreview\rom`: 13 places, 99 `.gba` files |
| Reports and briefs | 186 loose files in one folder, `scratch\sdd\slice1` (the house rule says group at about 15) |
| Research notes | `docs\re-*.md` and `docs\research-*.md` (two prefixes for one kind), `scratch\research\`, `scratch\re\` |
| Tools | `scripts\permanent` (live), plus tools still used from scratch: `scratch\art\r12fix\edits.py` and `fix.py`, `scratch\re\remaster\anime\b1_label.py` to `b5_detail.py`, `scratch\re\base_audit\ba_*.py`, `scratch\ghidra\scripts\*.java`, `scratch\re\disasm\ghidra\*.java`, `scratch\audio\a0`-`a2`, `snap.sh`, `package.sh` |
| Bible copies | 38 full copies named `RE-BIBLE.before*.md` inside study folders, 6.3 MB |

Overall 27,805 of 42,398 PNG files are byte copies of another PNG (66 %), and 39 of 99 ROMs are byte copies (600 MB) (C).

### 2.3 Names that do not say what they are

| Name | What it means |
|---|---|
| `re` | "Reverse engineering". Used four ways: `scratch\re\` (studies), `scripts\permanent\re\` (disassembler), `docs\re-*.md` (write-ups), `RE-BIBLE.md` |
| `sdd`, `slice1` | The task method and the first slice of the merge plan |
| `r12fix`, `obfix`, `t6`, `palslot`, `status_same`, `set57_png` | Hand fixes after build r12; one-body fix; task 6; palette slot; status portrait; an export of set 57 |
| `intake`, `intake17`, `intake18`, `r19` ... `r38` | my art intake rounds and per-build work folders |
| `ba_*` | "Base audit" tools |
| `rAroot`, `r1a_`, `r1b_`, `armrev`, `tmpcmp`, `cur` | Early gi method rounds, 2026-10-16 to 17 |
| `gi_ssj_v2`, `_v3`, `_v4`, `gi_ssj2_v3_r3aura_20261017` | Versions of the gi frames; only some are live (section 3.4) |
| `owner-0853`, `owner-0948`, `shared-body-1240`, `gi-fix-1125` | Work named by the time of your message |
| `Inferred`, `Sound` | Buu's Fury tilesets and sound effects (capital letters break the lowercase rule) |
| `images` (7 files in `data\reference`) | Downloaded images without names |

### 2.4 Live work under `scratch\`, and dead files

- Live under `scratch\`: everything in section 2.1, plus the base audit (`scratch\re\base_audit\`, `scratch\art\base_audit\`) and the ki HUD study (`scratch\re\hud_ki\`). Two tasks write there now.
- Dead or superseded (C unless marked): the 38 bible copies; the art copies in the intake and build-round folders; six `sdd\slice1\*-work` folders (8,441 of 10,496 files are copies); 12 review snapshots; `scratch\art\work\` rounds except `*_old_method`; `gi_*_v3` previews (no code reads them); `gi_ssj2_v3_r3aura_20261017`; `sprites_backup_2330`; `scratch\verify` (no reference found); 72 `.pyc` caches.
- `scripts\one-time\` is empty, while about 600 run-once study scripts sit in `scratch\re\` (C).

---

## 3. Move map

Notation: "names kept" means every file inside keeps its name. `<ART>` and `<BUILDS>` come from decision 1.
Order matters only in section 5. This table is the input for the scripted moves and the scripted text rewrite in step 8.

### 3.1 `data\`

| Old | New | Note |
|---|---|---|
| `data\*` | unchanged | Your files. Renames only if you ask (decision 8) |

### 3.2 `docs\`

| Old | New |
|---|---|
| `docs\RE-BIBLE.md`, `docs\build-log.md`, `docs\data-index.md` | unchanged |
| `docs\2026-10-16-log-merge-design.md` | `docs\design\2026-10-16-log-merge-design.md` |
| `docs\plans\` | `docs\design\plans\` |
| `docs\re-forms.md`, `re-outfit.md`, `re-overview.md`, `re-portraits.md`, `re-save-format.md`, `re-sprite-decompression.md` | `docs\research\` (names kept) |
| `docs\research-bf-sprites.md`, `research-notes.md`, `research-status-screen.md` | `docs\research\` (names kept) |

### 3.3 `scratch\sdd\slice1\` loose files (names kept)

| Old files | New folder |
|---|---|
| `progress.md`, `morning-report.md`, `morning-report-1018.md`, `morning-2026-10-24.md`, `bible-pending-1018.md` | `docs\ledger\` |
| `global.md` | `docs\tasks\global.md` |
| `snap.sh`, `package.sh` | `scripts\permanent\review\` (change the `W=` line in each; snapshots go to `scratch\review-snapshots\`) |
| `task-1-brief.md`, `task-1-report.md`, `task-1-review.diff`, `task-1-fix-r2.diff` | `docs\tasks\2026-10-16-task-1-build-pipeline\` |
| `task-2-brief.md`, `task-2-report.md`, `task-2-review.diff` | `docs\tasks\2026-10-16-task-2-sprite-export\` |
| `task-3-brief.md`, `task-3-report.md`, `task-3-review.diff` | `docs\tasks\2026-10-16-task-3-outfit-research\` |
| `task-4-brief.md`, `task-4-report.md`, `task-4-review.diff`, `task-4-fix-r1.diff` | `docs\tasks\2026-10-16-task-4-forms-research\` |
| `task-5-brief.md`, `task-5-red.txt`, `task-5-fix-r1.md`, `task-5-part2-dispatch.md`, `task-5-review.diff`, `task-5-review-report.md`, `task-5-part2-report.md`, `task-5-report.md` | `docs\tasks\2026-10-16-task-5-gi-art\` |
| `task-6-brief.md`, `task-6-dispatch.md`, `task-6-red.txt`, `task-6-review.diff`, `task-6-review-report.md`, `task-6-report.md` | `docs\tasks\2026-10-16-task-6-ssj2\` |
| `task-7-brief.md`, `task-7-dispatch.md`, `task-7-review.diff`, `task-7-review-report.md`, `task-7-report.md` | `docs\tasks\2026-10-16-task-7-gi-portraits\` |
| `task-8-brief.md` | `docs\tasks\2026-10-16-task-8-owner-acceptance\` |
| `final-review.diff`, `final-review-report.md`, `final-fix.md`, `final-fix-report.md` | `docs\tasks\2026-10-17-final-review\` |
| `golden-brief.md`, `golden-fix-r1.md`, `golden-fix-r2.md` | `docs\tasks\2026-10-17-golden-frames\` |
| `gi-fix-1125.md`, `gi-fix-1125-report.md` | `docs\tasks\2026-10-17-gi-fix-1125\` |
| `portraits-piccolo.md`, `portraits-piccolo-report.md` | `docs\tasks\2026-10-17-portraits-piccolo\` |
| `hud-z2-next.md`, `hud-z2-next-report.md` | `docs\tasks\2026-10-17-hud-z2-next\` |
| `status-gold.md`, `status-gold-report.md` | `docs\tasks\2026-10-17-status-gold\` |
| `gi-fix-step.md`, `gi-fix-step-report.md` | `docs\tasks\2026-10-17-gi-fix-step\` |
| `gi-rules-night.md`, `gi-rules-night-report.md` | `docs\tasks\2026-10-18-gi-rules-night\` |
| `promote-chain.md`, `promote-chain-report.md` | `docs\tasks\2026-10-18-promote-chain\` |
| `tools-review.md`, `tools-review-report.md` | `docs\tasks\2026-10-18-review-tools\` |
| `owner-0804-fixes.md`, `owner-0804-fixes-report.md` | `docs\tasks\2026-10-18-owner-0804-fixes\` |
| `owner-0853-fixes.md`, `owner-0853-fixes-report.md` | `docs\tasks\2026-10-18-owner-0853-fixes\` |
| `owner-0948-walk.md`, `owner-0948-walk-report.md` | `docs\tasks\2026-10-18-owner-0948-walk\` |
| `eye-review-r12.md` | `docs\tasks\2026-10-18-eye-review-r12\` |
| `shared-body-1240.md`, `shared-body-1240-report.md` | `docs\tasks\2026-10-18-shared-body-1240\` |
| `save-slots.md`, `save-slots-report.md` | `docs\tasks\2026-10-18-save-slots\` |
| `save-slot3.md`, `save-slot3-report.md` | `docs\tasks\2026-10-18-save-slot3\` |
| `aura-rage.md`, `aura-rage-report.md` | `docs\tasks\2026-10-18-aura-rage\` |
| `cutscene-portraits.md`, `cutscene-portraits-report.md` | `docs\tasks\2026-10-18-cutscene-portraits\` |
| `r12fix-intake.md`, `r12fix-intake-report.md` | `docs\tasks\2026-10-18-r12fix-intake\` |
| `npc-gi.md`, `npc-gi-report.md` | `docs\tasks\2026-10-18-npc-gi\` |
| `portrait-remaster-study.md`, `portrait-remaster-study-report.md` | `docs\tasks\2026-10-18-portrait-remaster-study\` |
| `chamber-fights-study.md`, `chamber-fights-study-report.md` | `docs\tasks\2026-10-18-chamber-fights-study\` |
| `portrait-vegeta.md`, `portrait-vegeta-report.md` | `docs\tasks\2026-10-18-portrait-vegeta\` |
| `r17-intake.md`, `r17-intake-report.md` | `docs\tasks\2026-10-18-r17-intake\` |
| `portrait-gohan.md`, `portrait-gohan-report.md` | `docs\tasks\2026-10-18-portrait-gohan\` |
| `file-select.md`, `file-select-report.md` | `docs\tasks\2026-10-18-file-select\` |
| `disasm-study.md`, `disasm-study-report.md` | `docs\tasks\2026-10-18-disasm-study\` |
| `r18-intake.md`, `r18-intake-report.md` | `docs\tasks\2026-10-18-r18-intake\` |
| `portrait-soft.md`, `portrait-soft-report.md` | `docs\tasks\2026-10-19-portrait-soft\` |
| `status-same.md`, `status-same-report.md` | `docs\tasks\2026-10-19-status-portrait\` |
| `r19-build.md`, `r19-build-report.md` | `docs\tasks\2026-10-19-r19-build\` |
| `disasm-adopt.md`, `disasm-adopt-report.md` | `docs\tasks\2026-10-19-disasm-adopt\` |
| `toolchain.md`, `toolchain-report.md` | `docs\tasks\2026-10-19-toolchain\` |
| `r20-build.md`, `r20-build-report.md` | `docs\tasks\2026-10-19-r20-build\` |
| `portrait-from-anime.md`, `portrait-from-anime-report.md` | `docs\tasks\2026-10-19-portrait-from-anime\` |
| `portrait-vector.md`, `portrait-vector-report.md` | `docs\tasks\2026-10-19-portrait-vector\` |
| `r21-build.md`, `r21-build-report.md` | `docs\tasks\2026-10-19-r21-build\` |
| `portrait-cell.md`, `portrait-cell-report.md` | `docs\tasks\2026-10-19-portrait-cell\` |
| `palette-slot.md`, `palette-slot-report.md` | `docs\tasks\2026-10-19-palette-slot\` |
| `effects-trace.md`, `effects-trace-report.md` | `docs\tasks\2026-10-20-effects-trace\` |
| `r22-build.md`, `r22-build-report.md` | `docs\tasks\2026-10-20-r22-build\` |
| `inject-tool.md`, `inject-tool-report.md` | `docs\tasks\2026-10-20-inject-tool\` |
| `cellgames-ssj.md`, `cellgames-ssj-report.md` | `docs\tasks\2026-10-20-cellgames-ssj\` |
| `cellgames-build.md`, `r27-build-report.md` | `docs\tasks\2026-10-20-r27-build\` |
| `decomp-review.md`, `decomp-review-report.md` | `docs\tasks\2026-10-20-decomp-review\` |
| `fullpower-ssj.md`, `r28-build-report.md` | `docs\tasks\2026-10-22-r28-build\` |
| `tool-review.md`, `tool-review-report.md` | `docs\tasks\2026-10-22-modder-tool-review\` |
| `disasm-port.md`, `disasm-port-report.md` | `docs\tasks\2026-10-22-disasm-port\` |
| `superperfect-study.md`, `superperfect-study-report.md` | `docs\tasks\2026-10-22-superperfect-study\` |
| `one-body.md`, `one-body-report.md` | `docs\tasks\2026-10-22-one-body\` |
| `piccolo-gi-scene.md`, `piccolo-gi-scene-report.md` | `docs\tasks\2026-10-22-piccolo-gi-scene\` |
| `superperfect-aura.md`, `superperfect-aura-report.md` | `docs\tasks\2026-10-22-superperfect-aura\` |
| `r30.md`, `r30-build-report.md` | `docs\tasks\2026-10-23-r30-build\` |
| `r31.md`, `r31-build-report.md` | `docs\tasks\2026-10-23-r31-build\` |
| `r32.md`, `r32-build-report.md` | `docs\tasks\2026-10-23-r32-build\` |
| `one-body-fix.md`, `one-body-fix-report.md` | `docs\tasks\2026-10-23-one-body-fix\` |
| `r33.md`, `r33-build-report.md` | `docs\tasks\2026-10-23-r33-build\` |
| `base-audit.md` | `docs\tasks\2026-10-23-base-audit\` |
| `r34.md`, `r34-build-report.md` | `docs\tasks\2026-10-23-r34-build\` |
| `superperfect-portrait.md`, `superperfect-portrait-report.md` | `docs\tasks\2026-10-23-superperfect-portrait\` |
| `superperfect-portrait2.md`, `superperfect-portrait2-report.md` | `docs\tasks\2026-10-23-superperfect-portrait2\` |
| `r35.md`, `r35-build-report.md` | `docs\tasks\2026-10-23-r35-build\` (**a test reads `r35.md`**) |
| `palette-census-r35.md`, `palette-census-r35-report.md` | `docs\tasks\2026-10-23-palette-census\` |
| `r36-pins.md`, `r36-pins-report.md` | `docs\tasks\2026-10-24-r36-pins\` |
| `hud-ki-study.md`, `hud-ki-study-report.md`, `hud-ki-proto.md`, `hud-ki-proto-report.md` | `docs\tasks\2026-10-24-hud-ki\` |
| `chamber-proto.md`, `chamber-proto-report.md` | `docs\tasks\2026-10-24-chamber-proto\` |
| `block-study.md`, `block-study-report.md`, `block-pose.md`, `block-pose-report.md` | `docs\tasks\2026-10-24-block\` |
| `r38.md`, `r38-suite.txt`, `r38-report.md` | `docs\tasks\2026-10-24-r38-build\` |
| `folder-reorg-survey.md`, `folder-reorg-plan.md`, `folder-reorg-inventory.md` | `docs\tasks\2026-10-24-folder-reorg\` |

Total: 189 loose files into 78 task folders, `docs\ledger\` and two other homes. A script checked that every loose file is listed exactly once (C, at 11:30 AM). The folder had 186 loose files when the survey started; this plan, its inventory and a new `hud-ki-proto-report.md` (written by the ki HUD task during the survey) make 189. Re-run that check right before step 6, because tasks keep adding files.

### 3.4 `scratch\sdd\slice1\` subfolders

| Old | New |
|---|---|
| `snapshots\`, `backups\` | `archive\2026-10-17-review-snapshots\` |
| `gi-fix-1125\`, `gi-fix-step-work\`, `gi-rules-night-work\`, `owner-0853-work\`, `owner-0948-work\`, `shared-body-1240-work\` | `archive\2026-10-17-gi-art-rounds\` (names kept) |

### 3.5 `scratch\re\` and other study folders

Rule: a study folder goes to `scripts\one-time\<task folder name>\`, names kept inside. Big copies inside it go elsewhere (last column).
Depth check (C, by arithmetic): `scratch\re\X\f.py` and `scripts\one-time\X\f.py` both reach the LOG root with `parents[3]`. Study scripts that also name sibling folders or the absolute path (266 files, C) need an edit before they run again. They are kept as evidence, not promised to re-run.

| Old | New | Split out first |
|---|---|---|
| `scratch\re\` loose 22 files, `scratch\captures\`, `scratch\verify\` | `scripts\one-time\2026-10-16-first-probes\` (captures and verify as subfolders) | |
| `scratch\re\outfit\` | `scripts\one-time\2026-10-16-task-3-outfit-research\` | |
| `scratch\re\forms\` | `scripts\one-time\2026-10-16-task-4-forms-research\` | |
| `scratch\re\gi\` | `scripts\one-time\2026-10-16-task-5-gi-art\` | |
| `scratch\re\t6\` | `scripts\one-time\2026-10-16-task-6-ssj2\` | |
| `scratch\re\portraits\` | `scripts\one-time\2026-10-16-task-7-gi-portraits\` | |
| `scratch\re\set57_png\` | `scratch\sprite-exports\set57\` | (whole folder is an export) |
| `scratch\re\overview\` | `scripts\one-time\2026-10-17-engine-overview\` | |
| `scratch\research\bf-sprites\` | `scripts\one-time\2026-10-17-bf-sprites-research\` | `log2\set*` to `scratch\sprite-exports\bf-sprites-log2\` |
| `scratch\research\status\` | `scripts\one-time\2026-10-17-status-screen-research\` | |
| `scratch\re\save\` | `scripts\one-time\2026-10-18-save-slots\` (holds `slot3\` too) | |
| `scratch\re\aura\` | `scripts\one-time\2026-10-18-aura-rage\` | |
| `scratch\re\cutscene\` | `scripts\one-time\2026-10-18-cutscene-portraits\` | |
| `scratch\re\intake\` | `scripts\one-time\2026-10-18-r12fix-intake\` | `art_r14\` to `archive\2026-10-18-art-snapshots\intake-art_r14\` |
| `scratch\re\npc_gi\` | `scripts\one-time\2026-10-18-npc-gi\` | |
| `scratch\re\chamber\` | `scripts\one-time\2026-10-18-chamber-fights-study\` | |
| `scratch\re\intake17\` | `scripts\one-time\2026-10-18-r17-intake\` | `art_r16\` to `archive\2026-10-18-art-snapshots\intake17-art_r16\` |
| `scratch\re\file_select\` | `scripts\one-time\2026-10-18-file-select\` | |
| `scratch\re\disasm\` | `scripts\one-time\2026-10-18-disasm-study\` | `ghidra\proj\` to `scratch\ghidra\LoG2auto\`; `ghidra\*.java` and its `README.md` to `scripts\permanent\ghidra\` |
| `scratch\re\intake18\` | `scripts\one-time\2026-10-18-r18-intake\` | `art_r17\` to `archive\2026-10-18-art-snapshots\intake18-art_r17\` |
| `scratch\re\status_same\` | `scripts\one-time\2026-10-19-status-portrait\` | |
| `scratch\re\r19\` | `scripts\one-time\2026-10-19-r19-build\` | `art_r18\` to `archive\2026-10-18-art-snapshots\r19-art_r18\` |
| `scratch\re\asm\` | `scripts\one-time\2026-10-19-toolchain\` | |
| `scratch\re\r20\` | `scripts\one-time\2026-10-19-r20-build\` | `.gba` to `scratch\rom-copies\r20\` |
| `scratch\re\remaster\` | `scripts\one-time\2026-10-19-portrait-from-anime\` | Pipeline: promote later (decision 9) |
| `scratch\re\r21\` | `scripts\one-time\2026-10-19-r21-build\` | |
| `scratch\re\palslot\` | `scripts\one-time\2026-10-19-palette-slot\` | `.gba` to `scratch\rom-copies\palslot\` |
| `scratch\re\effects\` | `scripts\one-time\2026-10-20-effects-trace\` | |
| `scratch\re\r22\` | `scripts\one-time\2026-10-20-r22-build\` | |
| `scratch\re\inject\` | `scripts\one-time\2026-10-20-inject-tool\` | |
| `scratch\re\cellgames\` | `scripts\one-time\2026-10-20-cellgames-ssj\` | |
| `scratch\re\r27\` | `scripts\one-time\2026-10-20-r27-build\` | |
| `scratch\re\decomp-review\` | `scripts\one-time\2026-10-20-decomp-review\` | |
| `scratch\audio\` | `scripts\one-time\2026-10-21-rage-music\` | `rom\` and `export\` to `scratch\audio-export\`; `test\` to `<BUILDS>\mockups\2026-10-21-rage-music\` |
| `scratch\re\r28\` | `scripts\one-time\2026-10-22-r28-build\` | |
| `scratch\re\toolreview\` | `scripts\one-time\2026-10-22-modder-tool-review\` | `rom\` to `scratch\rom-copies\toolreview\` |
| `scratch\re\disasm-port\` | `scripts\one-time\2026-10-22-disasm-port\` | |
| `scratch\re\superperfect\` | `scripts\one-time\2026-10-22-superperfect-study\` | |
| `scratch\re\r29\` | `scripts\one-time\2026-10-22-one-body\` (its scripts are the one-body survey, C) | `art\` to `archive\2026-10-18-art-snapshots\r29-art\` |
| `scratch\re\piccolo\` | `scripts\one-time\2026-10-22-piccolo-gi-scene\` | |
| `scratch\re\r30\` | `scripts\one-time\2026-10-23-r30-build\` | `set59\`, `set61\` to `scratch\sprite-exports\r30\` |
| `scratch\re\r31\` | `scripts\one-time\2026-10-23-r31-build\` | `set103\`, `set158\` to `scratch\sprite-exports\r31\` |
| `scratch\re\r32\` | `scripts\one-time\2026-10-23-r32-build\` | |
| `scratch\re\obfix\` | `scripts\one-time\2026-10-23-one-body-fix\` | `art\` to `archive\2026-10-18-art-snapshots\obfix-art\` |
| `scratch\re\r33\` | `scripts\one-time\2026-10-23-r33-build\` | |
| `scratch\re\r34\` | `scripts\one-time\2026-10-23-r34-build\` | |
| `scratch\re\r35\` | `scripts\one-time\2026-10-23-r35-build\` | |
| `scratch\re\palette_census\`, `scratch\re\palette_use\` | `scripts\one-time\2026-10-23-palette-census\` (`palette_use\` as a subfolder) | |
| `scratch\re\base_audit\` | `scripts\one-time\2026-10-23-base-audit\` (**last: active now**) | |
| `scratch\re\gamefaqs\` | `docs\research\sources\gamefaqs\` | |
| `scratch\re\hud_ki\` | `scripts\one-time\2026-10-24-hud-ki\` (**last: active now**) | `mockups\` to `<BUILDS>\mockups\2026-10-24-hud-ki\` |
| `scratch\re\chamber_proto\` | `scripts\one-time\2026-10-24-chamber-proto\` | |
| `scratch\re\block\` | `scripts\one-time\2026-10-24-block\` | `mockups\` to `<BUILDS>\mockups\2026-10-24-block\` |
| `scratch\re\r38\` | `scripts\one-time\2026-10-24-r38-build\` | |
| `RE-BIBLE.before*.md` (38 copies, all study folders) | `archive\bible-copies\<study>\` or delete (decision 3) | |
| `__pycache__\` (every folder) | delete | Python rebuilds them |

### 3.6 `scratch\art\`, `scratch\sprites\`, `scripts\permanent\art\`

| Old | New | Why |
|---|---|---|
| `scratch\art\gi_base\`, `gi_ssj\`, `gi_ssj2\`, `gi_ssj_v2\`, `gi_ssj2_v2\`, `gi_rage\`, `gi_ssj2_aura\`, `gi_rage_aura\`, `gi_ssj_v4\`, `gi_ssj2_v4\`, `gi_ssj2_aura_v4\` | `<ART>\` (names kept) | Build or tests read them (C) |
| `scratch\art\golden\` | `<ART>\golden\` | Tools and tests (C) |
| `scratch\art\locks\` | `<ART>\locks\` | `frame_lock.py` (C) |
| `scratch\art\r12fix\` | `<ART>\hand-fixes\` | `test_hand_frames.py` lines 27-28 change |
| `scratch\art\cell_aura\` | `<ART>\cell_aura\` | `ART_FOLDER = "cell_aura/scale_15"` stays right |
| `scratch\art\hud_z2.png`, `hud_z2_usable.bin`, `hud_z2_dim.bin` | `<ART>\` (root) | `Z2_ICONS` reads the art root |
| `scratch\art\portraits\` | `<ART>\portrait-sources\` | Clearer, and no clash with `tables\portraits\` |
| `scratch\art\anim\`, loose `gi_*_sheet.png`, `gi_overview.png`, `gi_ssj_9_2_test_cases.png`, `portraits_*.png` | `<ART>\` (the tools write them there) | Regenerated output |
| `scratch\art\work\gi_base_old_method\`, `gi_ssj_old_method\`, `gi_ssj2_old_method\` | `<ART>\work\` | `gi_art.WORK` (C) |
| `scratch\art\work\` (all other rounds and scripts) | `archive\2026-10-17-gi-art-rounds\art-work\` | No code reads them (C) |
| `scratch\art\gi_ssj_v3\`, `gi_ssj2_v3\`, `gi_ssj2_aura_v3\` | `archive\2026-10-22-gi-v3-preview\` | No code reads them (C) |
| `scratch\art\gi_ssj2_v3_r3aura_20261017\` | `archive\2026-10-17-gi-art-rounds\` | Dated copy |
| `scratch\art\base_audit\`, `scratch\art\ingame_r28\` | `<ART>\base-audit\` (`ingame_r28\` inside it) (**last: active now**) | `ba_*.py` constants change with it |
| `scratch\art\review\` | `scratch\review-renders\` | Renders |
| `scratch\sprites\` | `<ART>\vanilla-sets\` | Tools and a test read it (C) |
| `scratch\sprites_backup_2330\` | `archive\2026-10-17-gi-art-rounds\` | One file |
| `scripts\permanent\art\portraits.json`, `palette.json`, `portraits\`, `README.md` | `<ART>\tables\` | Under option B this is required: `test_inject.py` line 57 copies the whole `ART_DIR`, so the tables must sit apart from the gi art (C) |

### 3.7 Builds, saves, Ghidra, venv, scripts

| Old | New | Note |
|---|---|---|
| `scratch\build\*.gba`, `*.sav`, `*.ss*` (240 files) | `<BUILDS>\` (flat, names kept) | `inject.py` finds the next number with a flat `glob("log2_poc_r*.gba")` (C) |
| `scratch\build\test\` | `scratch\test-roms\` | Tests rebuild it every run |
| `scratch\saves\` | `test-data\saves\` | `test_save.py` (C) |
| `scratch\ghidra\scripts\*.java` | `archive\2026-10-16-ghidra-first-scripts\` | Superseded by the `disasm\ghidra` set (L) |
| `scratch\ghidra\` (projects, ROM copy) | stays | Regenerable (L); project files hold no absolute path (C) |
| `scratch\venv\` | stays | `pyvenv.cfg` stores the absolute path (C); recreate, never move |
| `scripts\permanent\re\` | `scripts\permanent\disasm\` (decision 5) | `re_sym.py` line 15 and `test_re_tools.py` line 16 change |
| `scripts\permanent\*\__pycache__\` | delete | |

---

## 4. Reference impact

### 4.1 What must change for the build and the 605-test suite to stay green

Two search shapes agree (C):
- Shape A, the Python join `"scratch"`: **47 lines in 31 files** (17 lines in tools and patches, 30 in tests).
- Shape B, a quoted string with `scratch\` or `scratch/`: 0 lines. Shape C, `os.path`, `../` or `getcwd`: 0 lines. The 110 other lines that say `scratch` are docstrings.
The full line list is in the inventory, section 5.1.

| Change | Lines | Files |
|---|---|---|
| The 47 `"scratch"` join lines (art, sprites, build, saves, brief `r35.md`) | 47 | 31 |
| `art_tables.ART_DIR` (tables move to `<ART>\tables\`) | 1 | `art_tables.py` line 26 |
| `r12fix` to `hand-fixes` | 2 | `test_hand_frames.py` lines 27, 28 |
| `re` to `disasm` (only if decision 5 says yes) | 2 | `re_sym.py` line 15, `test_re_tools.py` line 16 |

Recommended: put every root in one new module, `scripts\permanent\log_paths.py`, and point the 47 lines at it. After that, each later move is a one-line change.

Names that must stay the same inside `<ART>` (C): `gi_base`, `gi_ssj_v2`, `gi_ssj2_aura`, `gi_rage_aura` (build defaults, `LOG_GI_SSJ` and `LOG_GI_SSJ2`), `cell_aura\scale_15` (`ART_FOLDER`), `hud_z2_usable.bin`, `hud_z2_dim.bin` (`Z2_ICONS`), `golden`, `work`, `gi_ssj2_v4`, `gi_ssj2_aura_v4` and the other folder names tests use, `portrait-sources\remaster\final_r24\` and `...\superperfect\owner\sp52_owner_v3.png` (tests).

Files that must exist after every step (C; full table in the inventory, section 4): `log2_poc.gba` and `log2_poc_r18.gba` (no guard: the test errors), the r27 to r38 ROMs, twins and saves, `test-data\saves\log2_lv40_postcell.sav` and `log2_lv40_cellgames.sav`, `docs\tasks\2026-10-23-r35-build\r35.md`.

### 4.2 Text references (not needed for green, needed so people and tasks find things)

| Where | Old-path mentions (C) | Plan |
|---|---|---|
| `docs\RE-BIBLE.md` | About 160: `scratch\re` 60, `scratch\sdd` 47 (the source-key line, backslash and forward slash and absolute shapes), `scratch\art` 22, `scratch\build` 14, `scratch\saves` 5, `scratch\ghidra` 4, `scratch\captures` 3, `scratch\sprites` 3 | Scripted rewrite from the move map, plus the alias table at the top |
| `docs\build-log.md` | 31 | Keep the history as written; add the alias table at the top. Code only appends to it (C: `inject.py` line 239, `log2_build.py` line 76), so either way is safe |
| `LOG\README.md`, `docs\data-index.md`, `<ART>\tables\README.md`, `docs\tasks\global.md` | About 15 | Rewrite (`global.md` tells every task "Builds go to `scratch\build\`") |
| Docstrings in `scripts\permanent` | 110 lines | Rewrite with the code change |
| Memory: `project_log_rom_hack.md` (13 paths that move), `feedback_log_gi_drawing_lessons.md` (3), `feedback_log_portrait_pipeline.md` (1), `feedback_log_sprite_fixes_by_eye.md` (1), the project notes line 58 (`scratch/art/r12fix`, forward slash). `feedback_log_re_bible.md` names only the bible, which does not move | 19 | Rewrite in the same step as the move it names |
| Briefs, reports, ledger (186 files) | About 1,700 (`scratch\art` 479, `scratch\build` 344, `scratch\re` 620, `scratch\sdd` 239, others) | Keep as written (they are history); the alias table resolves them |
| Study folders, `sdd\slice1` work folders and snapshots | About 6,000, including the 38 bible copies | Keep; they are frozen evidence |

Bare names (no folder in front) stay findable because file names do not change: 795 mentions of the research docs by name alone, 64 of `re\<sub>`, 7 of `art\gi_...` (C).

### 4.3 Shapes that can still miss a reference

- Prose with no path ("the r29 folder", "the golden sheet").
- Folder names built in code from a variable (`f"set{n}"`, `ART / name` from a list). I listed the ones in `scripts\permanent`; study scripts have more.
- Environment values typed in a shell (`LOG_GI_SSJ=gi_ssj_v4` for the preview builds).
- Absolute paths outside text files: `scratch\venv\webfoot-audio\pyvenv.cfg` (C), the `Scripts\*.exe` launchers in it (L), mGBA's recent-ROM list and your shortcuts to `scratch\build\*.gba` (S), image editor recent files (S).
- Files outside the scan: other memory files (I scanned the 9 LOG files and the project notes), `Documents\GitHub\buusfury-decomp` notes (S).

---

## 5. Migration plan

### 5.1 The gate after every step

A step is done only when all five checks pass. A failed check means: undo the step from the backup, then fix.

| Gate | Check | Why |
|---|---|---|
| G1 Suite | `py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v`. Same count (605 today), 0 failures, and the same "ok" and "skipped" list, test by test, as the baseline | A missed path often turns into a skip, not a failure (48 guard lines, C) |
| G2 Existence | A one-time script resolves every root in `log_paths.py` and every file in inventory section 4, and fails if one is missing | Some guards make no skip record at all: `test_save.py` lines 103 and 190, the `continue` lines in `test_piccolo_gi_scene.py` 775 and 789, `test_r31_saves.py` 39, `test_superperfect_cell.py` 765, 774 and 783 (C). They report "ok" either way |
| G3 Build | `py -3 -P <root>\scripts\permanent\log2_build.py --list --out <root>\scratch\reorg-check\check.gba --log <root>\scratch\reorg-check\build-log.md` gives the baseline SHA-1 (r38 today: `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3`, C). `--log` keeps the real build log clean | Proves the build reads the same art |
| G4 Tripwire | After G1 and G3, every old path of the step must NOT exist | Tools call `mkdir(parents=True, exist_ok=True)` (for example `gohan_portraits.py` line 206, `log2_build.py` line 71, C), so a missed constant silently recreates the old folder. Grep cannot see this |
| G5 Nothing lost | A hash list of every file before the step equals the hash list after (as a multiset), apart from deletions you approved | Proves no file vanished |

### 5.2 Steps

| Step | What | Proof | Effort | Risk |
|---|---|---|---|---|
| 0. Freeze | Confirm no task runs. The session lists 11 named tasks (block-pose, block-study, chamber-proto, hud-ki, hud-ki-proto, pal-census, r36-pins, r38-build, sheet-final-col, sp-portrait2, main). Let the base audit and the ki HUD work reach a stop point | Each task says it stopped; `scratch\` shows no new files for 10 minutes | 10 min | High if skipped: a running task writes into an old path |
| 1. Backup | Zip the whole LOG folder to `Workspace\LOG\archive\backups\2026-10-2X_pre-reorg.zip` and save a hash list (path, size, SHA-1) beside it | Zip test passes; file count 49,332 or the new count | 20 min | Low |
| 2. Baseline | Run G1 and save the `-v` output; run G3 and note the SHA-1; write the G2 script and run it | All pass on today's layout | 30 min | Low |
| 3. Paths module | Add `scripts\permanent\log_paths.py` with today's values. Point the 47 lines (plus `ART_DIR`) at it. Move nothing | G1 to G3 identical to baseline | 1-2 h (one task) | Low: pure refactor |
| 4. Builds and saves | Copy `scratch\build\*` to `<BUILDS>\`, `scratch\build\test\` to `scratch\test-roms\`, `scratch\saves\` to `test-data\saves\`; check hashes; then delete the old copies. Change 3 roots. Update `global.md`, `project_log_rom_hack.md` and `README.md` in this step | G1 to G5; `inject.py` still picks r39 as the next build number (L: check which command prints it) | 30 min | Medium: your saves. Copy, verify, then delete |
| 5. Live art | Move the section 3.6 rows that are not "last". Change `ART`, `SPRITES`, the `hand-fixes` and `portrait-sources` lines, `ART_DIR`. Update the 4 memory notes that name art paths | G1 to G5; `frame_lock.py check --golden` gives the same result as in the baseline | 1 h | Medium |
| 6. Docs and tasks | Section 3.2 and 3.3: create the task folders and move the loose files; change the `r35.md` test line; update `snap.sh` and `package.sh` | G1 to G5 | 1 h (scripted from table 3.3) | Low |
| 7. Studies | Section 3.5 except the two active ones; archive the art copies; move ROM copies and exports to `scratch\` | G1 to G5 (no code in `scripts\permanent` reads `scratch\re`: 0 join lines, C) | 1-2 h (scripted) | Low for the build; study scripts lose their old paths |
| 8. Text rewrite | Scripted prefix rewrite from the move map over the bible, README, data index, `global.md`, tables README, docstrings and memory. Add the alias table ("old path, new path") at the top of the bible and the build log | Rerun the reference counter: 0 old prefixes in live docs and code; every old prefix left in history files has an alias row | 1 h | Low |
| 9. Active work | When the base audit and the ki HUD work end: move `scratch\re\base_audit\`, `scratch\art\base_audit\`, `scratch\art\ingame_r28\`, `scratch\re\hud_ki\`, fix the `ba_*.py` root and sibling constants | G1 to G5; one `ba_sheet.py` run | 30 min | Medium: tools in use |
| 10. Clean up | Delete `__pycache__`; delete or archive per decisions 2 and 3; write the new `LOG\README.md` (tree plus "where does X go"); write `<ART>\README.md`; final G5 against the step 1 hash list | All gates; you browse the tree | 30 min | Low |

The RE-BIBLE's many old paths: rewrite the live ones by script (step 8) **and** keep an alias table at the top. The rewrite keeps search results clickable; the alias table explains old paths in reports and history.

Total: about one working day, spread over the steps, with one task doing steps 3 to 9 and the main loop running the gates (L).

---

## 6. Final decisions

| # | Decision | Options | My recommendation |
|---|---|---|---|
| 1 | Top-level `art\` and `builds\` | A: `art\` and `builds\` (LOG-only exception to "no new top-level names"). B: `scripts\permanent\art\` and `deploy\builds\` | A. It answers "where are my sprites?" in one click. Under B the inject tables must move to `<ART>\tables\` (section 3.6) |
| 2 | Old builds | Keep all 66 ROMs; or archive r1 to r17 and r19 to r26 (with their twins) to `archive\builds\`; or delete them | Archive, do not delete. **Never remove** `log2_poc.gba`, r18, or r27 to r38 with their twins and saves: the tests read them (C). Before any removal, say if any old `.sav` holds a playthrough you still want |
| 3 | Copies | Archive or delete: 38 bible copies (6 MB), art snapshots (about 7,700 PNG), six `*-work` folders and 12 snapshots, `scratch\art\work` rounds, `scratch\art\review` renders (8,205 files) | Archive the copies for one month, then delete; delete the renders now |
| 4 | Bible name | Keep `RE-BIBLE.md`, or rename (for example `ROM-FACTS.md`) | Keep, and explain "RE" in the README. A rename touches `symbols.py`, 2 memory notes and every brief |
| 5 | `scripts\permanent\re\` | Rename to `disasm\` or keep | Rename: 2 code lines, and it ends the fourth meaning of "re" |
| 6 | Gi art folder names (`gi_ssj_v2`, `gi_ssj2_aura_v4`, ...) | Keep now, or rename to plain names | Keep now: the build defaults, environment values, tests and about 800 text lines use them. Explain each in `<ART>\README.md`; rename later as its own step |
| 7 | Task folders | One dated folder per task (brief and report together), or `briefs\` and `reports\` folders | Dated folders: they read like a diary and keep each brief with its report |
| 8 | `data\` names | Leave, or rename `Sound` to `sounds`, `Inferred` to `bf-tilesets`, and name the 7 `images` files | Your call; only you touch `data\`. No code or doc names these folders by path (C) |
| 9 | Tools still in scratch | Promote the portrait pipeline (`remaster\anime\b1`-`b5`, `e0`-`e3`), the base audit tools (`ba_*.py`) and the hand-fix tools (`edits.py`, `fix.py`) to `scripts\permanent\` | Yes, as a separate step after the move, with tests |
| 10 | Evidence placement | Study scripts in `scripts\one-time\<task>\` with the report in `docs\tasks\<task>\` (same folder name, inside the house rules), or both together in `docs\tasks\<task>\` | Split, as planned. Together is easier to browse, but it puts about 600 scripts under `docs\` (against the house rule) and moves them one level deeper, which breaks their `parents[3]` root (C) |

Also needed from you: a time window with no tasks running (step 0).

## 7. My answers (2026-10-24, 11:30-11:50 AM)

| # | Answer |
|---|---|
| 1 | A: top-level `art\` and `builds\` |
| 2 | Archive r1-r17 and r19-r26 (with twins) to `archive\builds\`. Test inputs stay |
| 3 | Archive everything (copies AND review renders). Delete nothing |
| 4 | Keep `RE-BIBLE.md`; explain "RE" in the README |
| 5 | Rename `scripts\permanent\re\` to `disasm\` |
| 6 | Keep the gi folder names; explain each in `art\README.md` |
| 7 | One dated folder per task under `docs\tasks\` |
| 8 | Rename the unclear `data\` names (Sound, Inferred, the 7 images files). Each rename is listed for me and done only after my yes for that rename |
| 9 | Promote the reused tools to `scripts\permanent\` as a later step with tests |
| 10 | Split: scripts in `scripts\one-time\<date-task>\`, reports in `docs\tasks\<date-task>\` |
