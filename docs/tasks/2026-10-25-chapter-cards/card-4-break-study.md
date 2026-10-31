# Card 4: find a real break between "Three years later..." and Kami's scene (final, 2026-10-30 3:41 PM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`chapter-placement-report.md`, `chapter-4-6-review-report.md`, `chapter-cards-v6-report.md`, the module
`scripts\permanent\patches\chapter_cards.py`, the save tools (`scripts\permanent\rom\log2_save.py`, the presave scripts in
`scripts\one-time\2026-10-25-chapter-cards\presave_*`), the guides in `docs\research\sources\guides-2026-10-29\`, and the
bible rows tagged CHP, CH5, CH6, CH7, CTS, SAV and the map rows.

## My words

Card 4 today (end of the post-Android 20 scene): "a bit odd, it just kinda happens mid gameplay, you take control of
Vegeta, fade, title, fade, back to control of Vegeta, not much else." The move to the 20 fight end: "seems like a
forced title, there is no scene change or anything." Without card 4, chapter 3 runs from flag 68 to the 129 Kami cut
(about 28 percent of guide 1, 23 percent of guide 2): "yeah so we need a break then."

## Task (study only: no module, list or ROM change)

1. List every scene change between flag 68 and flag 129 in story order: map changes into a new area with a scene or
   dialogue (not a plain door), fades, time cuts, arrivals by flight, and story scenes. For each: bytes, the story
   point, whether it plays once or every time, what plays after it, and the chapter 3 / 4 split it gives (guide shares,
   as the earlier reports measured them; BF range 3.7-23.8 percent, median about 7).
2. The first landing in the Northern Mountains (the lab hunt). How the landing works, whether any script runs on
   arrival, and how a card could play there only the first time: the visited-maps bits (save +0xE7) and when the game
   sets them relative to the arrival script, a story flag that changes at that point, or another one-shot test. Prove
   the guard with bytes and the save layout. Also: could a short new arrival line (one or two text boxes, for example a
   character saying Gero's lab must be in these mountains) follow the card, so it leads into dialogue as BF does? What
   text tools and portraits exist for that (cite our earlier text work, for example the scouter text rows R35).
3. Any other candidate that is a true scene change and splits the span near its middle.
4. Recommend one, with the exact insert point, the guard, the Continue flag (rising order), what the player sees, and
   the risk. Give a second choice.

## Report

`docs\tasks\2026-10-25-chapter-cards\card-4-break-report.md`: SHIPPED and PENDING tables, the scene change list, the
landing analysis, the recommendation, my questions. Label claims CONFIRMED, LIKELY or SPECULATIVE with addresses.
Bible rows (tag CH8) as `## Section N` table blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_card4.md`.

## Limits

- Read only, except your report, rows file and scripts (in `scripts\one-time\2026-10-25-chapter-cards\`, names starting
  `c4_`). Python: `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`. Never
  write under `data\`. LF, no em or en dashes. Never `cd` or `Push-Location`; absolute paths only.
- Other tasks: r40 (edits `log2_build.py`, the build lists and tests) and a fade study (`fade_` files). Do not touch
  their files, `chapter_cards.py`, `docs\RE-BIBLE.md` or `docs\ledger\`.

