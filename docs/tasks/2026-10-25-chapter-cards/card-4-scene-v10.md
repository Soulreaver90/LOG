# Card 4 v10: three groups, real facings, off the save point (my play test 2026-10-30 11:20 PM)

Read only these:
`scripts\permanent\patches\chapter_cards.py` (the card 4 scene block at lines 146-184 and `landing_records()` on),
`scripts\permanent\tests\test_chapter_cards.py`, `docs\tasks\2026-10-25-chapter-cards\card-4-scene-v9-report.md`,
and the v9 open-patch scripts `scripts\one-time\2026-10-25-chapter-cards\c4v_*`. Search `docs\RE-BIBLE.md` (tags
C4V, C4B, CH8) before you read the ROM.

## My words

"I dont like them standing in a straight line like that facing the same direction, especially ontop of the capsule
corp switcher. Have piccole/tien/krillen in their own group, gohan by himself, trunks and vegeta together. Trunks
already faces vegeta so thats fine for him, and dont have them all looking down towards the screen, maybe gohan on
the right, piccolo/tien/krillen at the top, tien and picclo faicing the north and krillin facing the left, gohan
facing the right. With playing as piccolo, keep the same group dynamic, but vegeta and trunks at the north, gohan at
the right and the piccolo trio near him during the tien/piccolo dialgue. If gohan flies in, same thing but vegeta and
trunks standing where gohan was on the left and gohan at the right."

The capsule corp switcher is the save point (I confirmed; bible lines 745 and 988).

## Task

1. **Replace the single row with three groups.** Today `_xs()` puts all five NPCs on one row at `ROW_Y` and `_arrival()`
   faces them all `DOWN`. Make the spots and the facings per actor and per branch. Build this reading, which the
   my already read back to me:

   | Leader | Vegeta and Trunks | Gohan | Piccolo, Tien, Krillin |
   |---|---|---|---|
   | Vegeta (player) | Stay at the v9 player end. Player faces left, Trunks faces right (unchanged) | Right of Vegeta, faces right | North group. Tien and Piccolo face north, Krillin faces left |
   | Piccolo (player) | North group | At the right, faces right | Next to Gohan, with the player. Same facings |
   | Gohan (player) | On the left, at Gohan's old v9 spot | The player, at the right, faces right | North group. Same facings |

   Each group reads as a group: its members stand within about 32 px of each other, and the groups stand apart.
2. **Checked for you, do not re-derive:** the landing `ext 39 (8,1,1,144,84)` is in `_guard()` (record 0), which runs
   before the leader pick (record 1), so the player lands at (144,84) in all three branches. Every layout above puts
   the player at or right of that spot. If a layout needs the landing moved, `ARRIVE` is one constant: move it, say so,
   and re-clamp `CAMERA`. A per-branch landing would need a new branch point: that is a stop-and-report.
3. **Hard constraints on every spot and every path.** Use the v9 method (flood fill from the player's end spot, the
   `c4v_*` scripts).
   - No actor inside the save point rect (56,48)-(105,97).
   - No actor under a BG1 canopy. BG1 draws over the actors (bible line 988). The open dirt path at top centre suits
     the north groups.
   - No actor south of the v9 row at y 84. The text box covers that area.
   - Every fly-in path, every fly-off path to the north, and every actor box must be on open collision cells, clear of
     the trees, the bushes and the rock at (272-287, 120-127).
4. **Plan picture, one per leader** (3 files, `scripts\one-time\2026-10-30-card-4-v10\`): the map with every actor box,
   the save point rect, the BG1 canopy mask and the text box area drawn and labelled. I view all three.
5. **Tests.** Update `test_chapter_cards.py` for the new spots and facings. New tests: no actor in the save rect, no
   actor under a canopy, no actor south of the row, each group within its distance, each branch's facings. No test may
   be weakened. If a test fails for a real reason, stop and report it.
6. **Build** `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v10.gba` with
   `scripts\permanent\build_list_trial_chapters.txt` (check the file is absent first). Make the `.sav` as a byte copy
   of the v9 save (exclusive create). Run `test_chapter_cards.py` only. I run the full suite.

## Report

Short. `docs\tasks\2026-10-25-chapter-cards\card-4-scene-v10-report.md`: SHIPPED and PENDING tables, the SHA-1, a
spot-and-facing table per leader, the plan picture paths, the test count, and I play steps per branch. Label
every claim C, L or S. Bible rows (tag C4T) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-card-4-v10\bible_rows.md`.

## Limits

- Edit only `chapter_cards.py` and `test_chapter_cards.py`. Python: `py -3.14 -P`. Never write under `data\`. Never
  overwrite a ROM or a save. LF, no em or en dashes, no byte order mark.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Another task may edit `celljr_fight.py`. Do not touch it, `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`. Do not. Do not run the full suite.

