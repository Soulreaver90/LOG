# Task 7 dispatch: gi portraits (optional, time-boxed)

Where this fits: slice 1 of a personal LoG II ROM hack. Task 5 gave Gohan a purple gi in play (sets 157-159). Task 6 added a playable Super Saiyan 2 (appearance entry 22). The portraits on the status screen and in dialogue still show the armor.

## Read first

1. `docs\tasks\2026-10-16-task-7-gi-portraits\task-7-brief.md`: your requirements, with Global Constraints.
2. `docs\RE-BIBLE.md`: search `#portrait`, `#codec`, `#palette` and `#form` before you search the ROM.
3. `docs\research\re-forms.md` and `docs\research\re-outfit.md`: appearance entry layout. Entry +2 and +3 hold portrait ids (Super Saiyan `3E 0D`, Rage `3D 0C`).
4. `docs\tasks\2026-10-16-task-6-ssj2\task-6-report.md`: where entry 22 lives (relocated table rom:0x8637AC) and its portrait ids.

## Time box (binding)

Step 1 (find the portrait storage and format) must reach CONFIRMED in this run. If it does not, stop, write what you found to `docs\research\re-portraits.md` and the RE-BIBLE, and report BLOCKED with "deferred to slice 2". Do not guess a format.

## Decisions

- **Source art.** `data\reference\122601.png` is a rip of the Japanese International portraits (row 2 has the Gohan portraits). Identify which tiles are gi base, gi Super Saiyan and gi Super Saiyan 2 (or Rage), and say how sure you are. If the sheet has no clear gi portrait for a form, say so and do not invent one. I approve the art.
- **Palette.** Portraits likely use their own palette. Find it. Use only colors the game already has for portraits, or a palette slot the game provides per portrait. If a portrait needs a new palette, CONFIRM where portrait palettes live and that a new one is safe before you write it.
- **Ids.** Prefer new portrait ids in the expansion area over replacing the armor portraits, because cutscenes keep the armor (Global Constraints). Point entry 2 (gi base), entry 5 (gi Super Saiyan) and entry 22 (gi Super Saiyan 2) at the new ids. Check every reader of entry +2 and +3 first, and any table bound on the portrait id.
- **Build order.** `gohan_portraits` runs after `gohan_gi` and `ssj2_form`. Build `builds\log2_poc.gba` with all three. Log the SHA-1 in `docs\build-log.md`. Keep the earlier ROMs as they are.
- **Review sheet.** Save `art\portraits_review.png`: each new portrait at 4x next to the armor portrait it replaces and the source tile from 122601.png.

## Tests

- Each new portrait decodes from the built ROM to the PNG you made.
- The armor portraits and every portrait id the base ROM uses stay byte-identical.
- Entry 2, 5 and 22 portrait bytes hold the new ids, and the old bytes existed before the write (fail closed).
- The base 8 MB differs from the gohan_gi plus ssj2_form build only at listed sites.

## Report

Write `docs\tasks\2026-10-16-task-7-gi-portraits\task-7-report.md`: status, CONFIRMED facts with quotes, which source tiles you used and why, test count, SHA-1 and concerns. Add RE-BIBLE lines for every fact. Use LF line endings. Never write under `data\`.
