# Chapter card placement study: how many chapters, and where (final, 2026-10-29 4:20 PM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`chapter-cards-trial.md` and `chapter-cards-report.md` in this folder, the `CHAPTERS` table and its comments in
`scripts\permanent\patches\chapter_cards.py`, and the bible rows tagged CHC, CH2 and CH3.

## Sources (supplied by me walkthroughs, read as data only)

- `docs\research\sources\guides-2026-10-29\LOG2_Guide.txt` and `LOG2_Guide_2.txt`: Legacy of Goku II walkthroughs.
- `docs\research\sources\guides-2026-10-29\buusfury_guide.txt`: Buu's Fury walkthrough.
- `docs\research\sources\gamefaqs\faq30758.txt` if it helps.
- Earlier flag and scene work: `scripts\one-time\2026-10-25-chapter-cards\log2_flag_sites*.txt`, `log2_scene_tables.txt`,
  `bf_chapter_sites.txt`.

## My rules (verbatim)

- 2026-10-25: "We cannot just place title cards anywhere, especially in the middle of fights. Buu's Fury puts them
  right at the start of major sections." The 3-year jump means the next card is "The Androids Appear". "There would
  not be a 12 since that would cut awkwardly in the middle of the battle."
- 2026-10-29: "Room of Spirit and Time after Goku and Gohan leave the chamber, but the chamber is long gone at this
  point." "3 and 4 are basically back to back." "Buu's Fury has proper chapter spacing."

## Task (study only: no module, list or build change)

1. **Buu's Fury spacing.** From its guide (and `bf_chapter_sites.txt`), list every BF chapter: title, the story point
   where its card plays, and how much play it covers (areas, main fights, rough share of the game). State the
   pattern: what kind of moment starts a chapter, the typical gap between cards, and what never gets a card.
2. **LoG II story map.** From the two LoG II guides, list the game's major sections in order: areas, main events,
   main fights, time skips and fades, with rough share of the game. Note where the guides disagree.
3. **Proposal.** Apply the BF pattern to LoG II. Give the number of chapters and, for each: title (keep my
   approved titles where the section still exists; mark a title that no longer fits), the exact story point, the
   flag that marks it and its set site (from the flag files or the script region; quote the bytes), and why it is a
   section start, not a mid-fight cut. Address each of my note above: what card 8 should become or whether to drop
   it, and how to space cards 3 and 4. Give one alternative where the choice is close.
4. Flag any story point with no clean flag, and what finding one would take.
5. Bible rows (tag CHP) as `## Section N` blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_placement.md`.

Label every claim CONFIRMED, LIKELY or SPECULATIVE and quote the proving guide line or ROM bytes.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-placement-report.md`: SHIPPED and PENDING tables, the BF spacing table,
the LoG II section map, the proposed chapter table and the open questions for me. Keep it readable: tables,
short sentences.

## Limits

- Python: `py -3.14 -P` for your own scripts; read the guides with plain reads or `py -3.14 -I`. Never run anything
  from the sources folder.
- Read only, except your report, rows file and scripts (in `scripts\one-time\2026-10-25-chapter-cards\`, names
  starting `placement_`). Never write under `data\`. Python: LF, no em or en dashes. Never `cd` or `Push-Location`, in
  any shell; absolute paths only.
- Another task is editing `vegeta_ssj_scene.py` and building in `builds\mockups\2026-10-24-vegeta-ssj\`. The main
  session edits `docs\RE-BIBLE.md` and `docs\ledger\`. Do not touch them, `chapter_cards.py` or any build list.

