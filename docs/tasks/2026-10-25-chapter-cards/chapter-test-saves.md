# Chapter cards: test saves just before each story card (final, 2026-10-30 6:43 AM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`chapter-cards-v5-report.md` and `chapter-placement-report.md` in this folder, the save tools
`scripts\permanent\rom\log2_save.py` (presets, `seal_slot`, `set_bit`) and their tests, and the bible rows tagged SAV, CSV,
CJT, R39, CH5 and CHP. The v5 census is `scripts\one-time\2026-10-25-chapter-cards\v5_save_census.txt`.

## My words

"Reviewing the chapter cards, all saves load the card. I want to see the transition to the card as well, so we need
saves before." On the choice between hand-built test saves and his own playthrough saves: "Build test saves is best."
Slot 3 of the v5 save (Cell's TV announcement, Continue shows Chapter 6) is right: it shows the card 7 transition.

## Task

1. For each story card 2-8, make one save slot placed just before the scene that plays the card, so that walking a few
   steps (or talking to one NPC) starts the scene and the card. Card points and flags are in `chapter-cards-v5-report.md`
   (cards 2 Preparation flag 26, 3 The Androids Appear 68, 4 Into Gero's Lab 86, 5 A New Horror 127, 6 Perfection 148,
   7 The Cell Games 154/158, 8 The Champion's Hour 195). Card 7 already has slot 3 of the v5 save; card 8 has slot 2
   (check both and reuse them). Card 1 needs an empty slot (a new game).
2. Base each slot on the nearest real save in `builds\` (census): copy its slot, then set the story flags, map, position,
   party, leader and form the game would have at that point. Read the flag SET and CLR sites between the base save's
   point and the target (the study's `placement_sites.txt` lists them) and set or clear every flag the game would. Say
   which flags you set or cleared and why, and what you could not match (levels, items, EXP).
3. For each slot, prove the target scene starts: name the trigger (map entry, NPC talk, step on a spot), the table and
   record, and its condition flags, and show the slot meets the condition.
4. Write the saves as new files by exclusive create, 3 slots per file, in `builds\mockups\2026-10-25-chapter-cards\`:
   `log2_poc_r39_chapters_v5_pre_a.sav` (cards 2, 3, 4), `_pre_b.sav` (cards 5, 6, and an empty slot 3 for card 1 on a
   new game). Each slot resealed with `log2_save.seal_slot`. Also make a byte copy of the v5 ROM next to each save with
   the same base name, so the emulator pairs them (exclusive create).
5. Add tests for the save builder if it lands in `scripts\permanent\`; one-time scripts are fine without.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-test-saves-report.md`: SHIPPED and PENDING tables; one row per card with
file, slot, map, position, leader, the trigger and what I do to see the transition; flags set or cleared;
known gaps. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote the proving bytes or line.

## Limits

- Python: `py -3.14 -P` (the default `py -3` is 3.15 with no Pillow). The LoG II base ROM is
  `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`, not the Europe file.
- Never write under `data\`. Never overwrite a ROM, save or state: exclusive create only. Python: LF, no em or en
  dashes. Never `cd` or `Push-Location`, in any shell; absolute paths only. Scripts and outputs
  go in `scripts\one-time\2026-10-25-chapter-cards\` (names starting `presave_`).
- Do not edit any patch module, test file outside a new save-builder test, or build list. A read-only study task works
  in `scripts\one-time\2026-10-30-celljr-rework-plan\`. I am editing `docs\RE-BIBLE.md` and `docs\ledger\`.

