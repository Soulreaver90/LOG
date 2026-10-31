# Gi base frames: put the approved base-audit frames into a test build (final, 2026-10-30 9:30 PM)

Read `art\README.md`, `art\base-audit\` (folders
`approved` 103 PNGs, `owner` 11, `to_edit` 13, `proposed` 150), the base-audit tools in
`scripts\one-time\2026-10-23-base-audit\` (`ba_edit.py`, `ba_owner_carry.py`, `ba_pair.py`), the ledger lines about the
base audit (`docs\ledger\progress.md`, search "base 157" and "base-audit"), and `scripts\permanent\patches\gohan_gi.py`
with its input `art\gi_base\` (`manifest.json`, last changed 2026-10-19). Read other files only when needed.

## My words

"What about our Gohan sprites, have we ingested the latest changes?" They are not in any build: the build reads
`art\gi_base\`, last changed 2026-10-19; the approved frames date from 2026-10-23 and 2026-10-24. Me: "yes" to
ingesting them into a test build.

## Task

1. Map each approved frame (`157_a<anim>_d<dir>_i<index>.png`) to the frame it replaces in the build. Say how the
   hand-drawn frames in `owner\` relate to `approved\` (already carried in, or not). Frames in `to_edit\` and
   `proposed\` are not approved: leave them out and list them.
2. Check each approved frame against the build's rules (size, palette indices, the sprite slot) with the existing
   tools. Do not change any pixel. A frame that fails goes to the report, not into the build.
3. **Main must not change in this run** (two other tasks build on r40 and its pins). Put the frames in through a new
   trial module, `gi_base_audit`, listed after main in a new list `scripts\permanent\build_list_trial_gi_base.txt`
   (`include build_list.txt` plus the module). It replaces only the approved frames. Tests: every approved frame lands
   byte for byte; no other frame changes.
4. Build `builds\mockups\2026-10-30-gi-base\log2_poc_r40_gi_base.gba` (check absent; exclusive create) with
   `.sav` byte copies of `builds\log2_poc_r40.sav`. Diff r40 to it: every run inside a `gi_base_audit` site. Make a
   review sheet (before and after, 4x, per anim) at `builds\mockups\2026-10-30-gi-base\review_sheet.png` and a GIF per
   changed anim, so I can review by eye. Full suite once at the end.

## Report

Short: `docs\tasks\2026-10-30-gi-base-ingest\gi-base-ingest-report.md`. SHIPPED and PENDING tables, the frame map
(counts per anim, not every frame), frames left out and why, SHA-1, where to look in game, suite count. Bible rows
(tag GBA, a few) in `scripts\one-time\2026-10-30-gi-base-ingest\bible_rows.md` as `## Section N` table blocks.

## Limits

- Edit nothing under `art\`. New files: the module, its test, the trial list, scripts in
  `scripts\one-time\2026-10-30-gi-base-ingest\`, the build folder. Python: `py -3.14 -P`. Base ROM:
  `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Other tasks edit `celljr_fight.py` and `bf_ki_pool.py` and their tests. Do not touch them, `build_list.txt`,
  `gohan_gi.py`, `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Work lean. ROM quality comes first: never edit an approved pixel.

