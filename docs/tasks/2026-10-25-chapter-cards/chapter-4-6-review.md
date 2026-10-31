# Chapter cards 4-6: re-evaluate the story points (final, 2026-10-30 7:08 AM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`chapter-placement-report.md` and `chapter-cards-v5-report.md` in this folder, the module
`scripts\permanent\patches\chapter_cards.py`, the bible rows tagged CHC, CH3, CH5 and CHP, the study scripts in
`scripts\one-time\2026-10-25-chapter-cards\` (`placement_*`, `v5_*`, `bf_chapter_sites*`), and the guides in
`docs\research\sources\guides-2026-10-29\`.

This is a study only. Do not change the module, any list or any ROM.

## My words (play test of v5)

- Cards 2 and 3: "perfect". Card 7: right (shows after Cell's announcement). "So right now 4-6 needs to be re-evaluated."
- Card 4 (Into Gero's Lab, end of the post-Android 20 scene, our own fade and map reload): "a bit odd, no real sense
  of transition".
- Card 5 (A New Horror): "instead of fade to the world map, maybe fade to Kami's tower? In Buu's Fury, are there any
  chapter transitions to the world map? I recall most transition to a dialogue or cutscene, that's why those feel
  natural."
- Card 6 (Perfection): "Maybe after Imperfect Cell says '...I must figure out how he does that!' Transitions to the
  Lookout. Though that makes this chapter and the next a shorter leap."

## Task

1. **Buu's Fury pattern.** For every BF chapter card site you can decode (`bf_chapter_sites.txt`, the placement report),
   say what follows the card: a map load into a scene with dialogue, a cutscene, free play, or the world map. Use the BF
   guide for the rest. Answer I: does any BF card lead into the world map? (Label each.)
2. **Card 4.** Why it feels odd (no fade in the vanilla script; the player stands in the field). Find better points near
   the start of the Gero's lab section: a scene start with a fade or a map change that opens on dialogue or a cutscene
   (for example arriving in the Northern Mountains, a scene at the lab entrance). For each: bytes, flag for Continue,
   what plays after the card. Recommend one.
3. **Card 5.** My idea: the card, then the next view is Kami's Lookout (a scene with dialogue), not the world
   map. Find the scene after flag 127: Piccolo arriving at the Lookout and Kami's lines (table `rom:0x3DF71C`, "KAMI:
   Piccolo. You've returned."). Can the card play right before that scene's map load or fade in, so the card leads into
   it? Give the point, bytes and Continue flag. If the world map sits between them (the player flies there), say what
   the cleanest point is (for example at the Lookout arrival).
4. **Card 6.** Find the Imperfect Cell line I quote (the text may wrap with `0x0B` or differ in case; search
   by parts such as "figure out", "how he does"). Find the table, the fade and the Lookout transition after it, and the
   Continue flag. Measure the new chapter 5 and 6 lengths (guide lines, as the placement report did) and say whether the
   shorter leap is a problem by the BF spacing (median 6.8 percent, range 3.7-23.8).
5. **Proposal.** A table for cards 4-6: point, bytes, Continue flag (rising order with the other cards), what plays
   after the card, chapter share. Note any change to card 7 (Cell Games) spacing.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-4-6-review-report.md`: SHIPPED and PENDING tables, the BF answer, one
section per card, the proposal table and my questions. Label claims CONFIRMED, LIKELY or SPECULATIVE and quote
the bytes or guide line. Bible rows (tag CH6) as `## Section N` blocks in
`scripts\one-time\2026-10-25-chapter-cards\bible_rows_ch46.md`.

## Limits

- Read only, except your report, rows file and scripts (in `scripts\one-time\2026-10-25-chapter-cards\`, names starting
  `ch46_`). Python: `py -3.14 -P`. The LoG II base ROM is `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`,
  not the Europe file. Never write under `data\`. LF, no em or en dashes. Never `cd` or `Push-Location`; absolute paths
  only.
- Other tasks: one builds test saves in `builds\mockups\2026-10-25-chapter-cards\` (files `presave_*`), one studies the
  Cell Jr plan, one maps a third-party hack. I am editing `docs\RE-BIBLE.md` and `docs\ledger\`. Do not touch
  their files.

