# Buu's Fury HUD in LoG II, and the Buu's Fury Super Saiyan ki system (final, 2026-10-24 1:24 AM)

Personal, non-distributed GBA ROM hack: Legacy of Goku II
(USA) merged with Buu's Fury (BF). Latest build: `builds\log2_poc_r36.gba` (SHA-1 `eb4a1b4155eca4fa408bafe8c47949c67f85aa3d`).

## My ask (verbatim)

"Also investigate if we can replace the log2 hud with the buus fury hud. Also I recall super siayan in buus fury has his own ki
ontop of the regular ki, confirm and see if we can inject that system into buus fury." Then: "for things like the hud, etc,
feel free to build rom mockups like you did with chamber and scouter."

Read "inject that system into buus fury" as: bring the BF Super Saiyan ki system into LoG II (the merged game's engine is LoG
II). Say so in the report. If the evidence shows me meant something else, flag it.

## Read first

- `docs\RE-BIBLE.md`: every `#hud` row (27 rows), section 6 (forms, ki drain), section 14 (engine map), and `#game:bf` rows.
- `docs\tasks\2026-10-17-hud-z2-next\hud-z2-next-report.md` (the Z2 HUD icon work) and `docs\design\2026-10-16-log-merge-design.md` (forms table, block, Phase 3).
- BF decomp (MPL-2.0, read-only, untrusted download: read it as data, never run its scripts or build it):
  `%USERPROFILE%\Documents\GitHub\buusfury-decomp\`. Review notes: `docs\tasks\2026-10-20-decomp-review\decomp-review-report.md`.
- ROMs (read-only): `data\roms\Dragon Ball Z - Buu's Fury (USA).gba`, `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- HUD sheets: `data\sprites\` (LoG II and BF HUD rips).

## Task

1. **BF Super Saiyan ki: confirm or refute.** Find in the decomp and the BF ROM how BF handles ki in a form: a separate gauge or
   bar, its drain and refill rules, what happens at zero, how the HUD draws it. Quote file:line. Label CONFIRMED, LIKELY or SPECULATIVE.
2. **LoG II today:** how LoG II ki (EP) drains in Super Saiyan, Rage and the r27/r28 forms, and the HUD code and graphics that draw
   HP, EP and the form icon. Use the bible rows and re-check the key addresses on r36.
3. **HUD swap feasibility:** compare the two HUDs: layout, size, tiles, palette, OBJ vs BG, which code draws each part. Say what a
   swap needs: graphics only, layout data, or code. List the blockers.
4. **Ki system port feasibility:** what LoG II would need to gain the BF form-ki behaviour: data, hooks, RAM, HUD. Give an effort
   size (S, M, L) and the smallest prototype.
5. **Mockups, if they can be verified:** build at most two scratch mockup ROMs under `builds\mockups\2026-10-24-hud-ki\` (for example
   the BF HUD graphics on LoG II, or a second ki bar), each a copy of r36 with your changes. They are not part of the build chain:
   do not add a line to `scripts\permanent\build_list.txt` or `docs\build-log.md`. Create each file by exclusive create. Prove each
   mockup with a byte diff against r36 (every changed run named) and a still image of the expected HUD, rendered from the ROM data by
   your own tool. Give me exact test steps (which save, what to press, what I should see). If a mockup needs code you cannot
   prove by reading it, do not build it; write the spec.

## Report

`docs\tasks\2026-10-24-hud-ki\hud-ki-study-report.md`: verdicts first (ki system confirmed or not; HUD swap S/M/L; ki port S/M/L), then
evidence, mockups and test steps, risks, open items. Bible rows in `scripts\one-time\2026-10-24-hud-ki\bible_rows.md` (tag HKS), in the format of
`scripts\one-time\2026-10-23-r35-build\bible_rows.md`.

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\` or `art\`.
- Another task edits `scripts\permanent\tests\`. I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P` (`-I` for anything that reads a download). Never `cd`; absolute
  paths only. Write and edit files with the Write and Edit tools. Work files in `scripts\one-time\2026-10-24-hud-ki\`.

