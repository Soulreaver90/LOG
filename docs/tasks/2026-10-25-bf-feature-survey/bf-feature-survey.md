# Buu's Fury features worth porting: survey (final, 2026-10-24 9:05 PM)

Read `LOG\README.md`, `docs\tasks\global.md` and the
bible: the source list, section 14 (game:bf) and the rows tagged BFS, HKS, HKP, HKB, R39, BMS, FRM, FCD.

## My ask (verbatim)

"Feel free to research the Buu's Fury disasm/rom for any other features you think we should port over? The block is
on hold. Maybe more of the GUI? The stat system? etc"

Already ported or in work (do not re-propose; you may propose extensions): the BF HUD and boss bar look (HUD v2b),
the shared Super Saiyan ki pool, the beam struggle study (BMS). The block is on hold: list it only as known.

## Task (study only: no patch, no build-list change)

1. Survey the BF ROM (`data\roms\`, read only) and the BF disasm the bible names. Cover at least: menus and GUI
   (pause, status, inventory, map, save), the stat system (level up, stat points, how stats feed damage and ki),
   equipment or item systems, character switching, transformations and form rules, combat moves and ki attacks,
   dialogue and text box features, quality of life (fast travel, quest log, scouter readouts).
2. For each feature: how BF does it (code and data addresses), the LoG II counterpart (addresses, or "none"), and
   the gap. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving line or address.
3. Rank the candidates in one table: value to the player, effort (bytes, new code, data), risk to existing saves and
   modules, OBJ or BG VRAM cost, and what I must draw. Mark the top 3 to 5 with a short trial module design
   each (my rule: mockups are trial patch modules built through a second build list). Do not build any.
4. Renders of BF screens or graphics that help I decide are welcome (in your scripts folder).
5. If a fact needs an emulator run, list the exact steps for me; do not guess.
6. Bible rows (tag BFP) as `## Section N` blocks in `scripts\one-time\2026-10-25-bf-feature-survey\bible_rows.md`.

## Report

`docs\tasks\2026-10-25-bf-feature-survey\bf-feature-survey-report.md`: SHIPPED and PENDING tables, the ranked table,
the top-pick designs, I drawing list and the emulator steps. Keep the report readable for me: one
purpose sentence per heading, then tables or bullets.

## Limits

- Read only, except your report, rows file, scripts and renders (in `scripts\one-time\2026-10-25-bf-feature-survey\`).
- Never write under `data\`. Never overwrite a ROM, save or state. Python: LF, no em or en dashes, `py -3 -P`, and
  `py -3 -I` for any script that reads downloaded files. Never `cd`, in any shell; absolute paths only.
- Another task is writing `scripts\permanent\patches\vegeta_ssj_scene.py`, its tests and a new trial list. The main
  session edits `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.

