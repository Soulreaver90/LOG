# Chamber fight prototype: Gohan vs Goku, built as r37 (final, 2026-10-24 1:24 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Latest build:
`builds\log2_poc_r36.gba` (SHA-1 `eb4a1b4155eca4fa408bafe8c47949c67f85aa3d`), suite 578 OK.

## My ask (verbatim)

"can you look into how we can inject that time chamber boss fights I requested, the trunks vs vegeta and gohan vs goku."
Original ask (2026-10-18): "Ideally two Time Chamber fights, Trunks vs Vegeta and Gohan vs Goku, all
with armor."

## Read first

- The feasibility study: `docs\tasks\2026-10-18-chamber-fights-study\chamber-fights-study.md` (brief) and `chamber-fights-study-report.md` (report, built
  on r17). Its section 11 is the smallest first prototype. Its work files are in `scripts\one-time\2026-10-18-chamber-fights-study\`.
- `docs\RE-BIBLE.md`: rows tagged from that study, section 8 (story and script), section 14 (engine), and the r30-r35 rows (later
  builds moved and added tables since r17, so re-check every address the study names on r36).
- Build system: `scripts\permanent\log2_build.py`, `build_list.txt`, an existing patch with its test as the model
  (`scripts\permanent\patches\superperfect_cell.py`, `tests\test_superperfect_cell.py`), and `docs\tasks\2026-10-23-r35-build\r35-build-report.md`.

## Task

1. Re-verify the study's prototype plan on r36: every address, table, count, free enemy type and hook it names. Report each as
   still valid or moved.
2. Build the prototype as a new patch module plus its test, appended to `build_list.txt`, producing r37: Gohan (Demon Clothes) vs
   Goku (`set:60`) as an enemy with an existing AI, in the existing sparring room 6,70 (study section 11), with a short scene, a win
   path and a safe loss path. Placeholder dialogue is fine; mark each line as a placeholder in the report so I can write
   them.
3. Prove it: SHA-1, a diff where every changed run is named, the full suite green (578 plus your new tests), and a still image of
   the enemy's frames from the ROM. Make a test save by exclusive create next to r37 that starts close to the fight, and give the
   my exact steps (save, where to walk, what should happen, what a pass looks like).
4. Then write, but do not build, the plan to (a) move the fight into a chamber arena (study: map entry zone 9 area 8) and hook it
   into the chamber scenes, and (b) add Trunks vs Vegeta. List the final decisions each needs (outfits, AI, Goku armor art, stats).

If any step shows the prototype cannot be built safely (for example an address that moved and cannot be re-found), stop at that
step, write what you found, and do not build.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state (exclusive create). One build only (r37).
- Other work is running in `scripts\one-time\2026-10-24-hud-ki\` (read-only on `scripts\permanent\`, its mockups outside the build chain). The main
  session edits `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P`. Never `cd`; absolute paths only. Write and edit files with the
  Write and Edit tools. Work files in `scripts\one-time\2026-10-24-chamber-proto\`.
- Label every finding CONFIRMED, LIKELY or SPECULATIVE.

## Report

`docs\tasks\2026-10-24-chamber-proto\chamber-proto-report.md`: what was built (or why not), the proof, my test steps, the plan for the
arena and Trunks vs Vegeta, and the final decisions. Bible rows in `scripts\one-time\2026-10-24-chamber-proto\bible_rows.md` (tag CPR, in the format
of `scripts\one-time\2026-10-23-r35-build\bible_rows.md`).

