# HUD mockup v2: Buu's Fury HUD + Super Saiyan ki pool + boss HUD (final, 2026-10-24 8:13 AM)

Personal GBA ROM hack (Legacy of Goku II merged with Buu's
Fury, "BF"). Latest build: `builds\log2_poc_r38.gba` (SHA-1 `7a7cb85fa5873c4a44d360b33b6755d4e71e18e3`), suite 605 OK.

## My ask (verbatim)

"I also approve the hud but lets build on it first in the mockup with the ki code from buus fury. Also the HUD for the boss
should also be ported"

## Read first

- `docs\tasks\2026-10-24-hud-ki\hud-ki-study-report.md`: all of it. Section 5 is the approved data-only HUD mockup
  (`builds\mockups\2026-10-24-hud-ki\log2_poc_r36_bfhud.gba`, built on r36), section 6 is the ki pool prototype spec (form_ki u16 at
  `0x03003A00`, fill hook `@0x08014D92`, drain ticks `rom:0x89A788` and `0x89A81C`, HUD overlay). Its open decisions too.
- Its work files and tools in `scripts\one-time\2026-10-24-hud-ki\` (how BF code was read: `q.py bf dis`, `decomp_line.py`).
- `docs\RE-BIBLE.md` rows HKS (that study), BLK (the block study: how a pointer-level hook was proved and built in
  `scripts\one-time\2026-10-24-block\build_mock.py`, a model for a scratch mockup with code), and section 14 (engine).
- BF decomp (MPL-2.0, read-only, untrusted download: read as data, never run its scripts or build it):
  `%USERPROFILE%\Documents\GitHub\buusfury-decomp\`.

## Task

1. **Rebase:** re-apply the approved HUD mockup data onto r38 (not r36), with a script, so the HUD look is the same as the
   approved one. Prove each region still holds the bytes the r36 mockup expected before writing.
2. **Ki pool:** implement the section 6 spec as BF does it: a transform fills a separate form pool to max ki; ki moves in the
   form spend the pool; it drains 1 point every 20 frames; at 0 the player reverts and the pool empties; regular ki keeps
   regenerating underneath; the HUD draws the pool over the ki row in BF's colors. Use one pool for every form (Super Saiyan
   and Super Saiyan 2; I have not chosen two pools). Every hook must be proved by reading LoG II code and quoted with
   addresses; every BF behavior quoted with decomp lines. If a hook cannot be proved, build what can be proved and write the
   rest as a spec.
3. **Boss HUD:** find how BF shows a boss's health (bar, frame, name or portrait, when it shows and hides) and how LoG II
   shows it today. Port the BF look to LoG II bosses the same way as the player HUD (data first; code only if proved). Name
   which LoG II fights use it, and test on Super Perfect Cell (enemy type 25, map 14,3) or the Gohan vs Goku spar (r38 has
   it: training room 6,70).
4. **Build** `builds\mockups\2026-10-24-hud-ki\log2_poc_r38_bfhud2.gba` by exclusive create, not in the build chain (no line in
   `build_list.txt` or `docs\build-log.md`). Test pairs by exclusive create next to it: copies of `log2_poc_r38_scouter.sav`
   and `log2_poc_r38_spar.sav` from `builds\`. Byte diff against r38 with every run named; 0 bytes outside named
   regions; no word outside a new region points into it. Unit tests for the new code in the style of
   `scripts\one-time\2026-10-24-block\test_block.py`.
5. **My steps:** exact mGBA steps to see the HUD, transform and watch the pool fill, spend and drain, revert at 0, and see
   the boss HUD in a fight. Say what a pass looks like.

## Report

`docs\tasks\2026-10-24-hud-ki\hud-ki-proto-report.md`: verdicts first (built / spec only, each labeled CONFIRMED, LIKELY or
SPECULATIVE), the hooks with evidence, the diff proof, test results, my steps, risks, final decisions. Bible rows (tag HKP)
in `scripts\one-time\2026-10-24-hud-ki\proto\bible_rows.md`, in the format of `scripts\one-time\2026-10-24-block\bible_rows.md`.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\`, `build_list.txt`,
  `art\` or `docs\`. Work files only in `scripts\one-time\2026-10-24-hud-ki\` (new work in `scripts\one-time\2026-10-24-hud-ki\proto\`).
- Other work is running in `scripts\one-time\2026-10-24-block\`. I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`.
  Do not touch them.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P` (`-I` for anything that reads a download). Never `cd`, in any
  shell, ever; absolute paths only. Create and edit files with Python `open(..., "x")`, never shell
  redirection, `sed`, `printf`, `cp`, `rm` or `mkdir`.

