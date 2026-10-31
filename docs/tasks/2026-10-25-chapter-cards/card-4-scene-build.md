# Card 4 arrival scene: build (chapters v8) (final, 2026-10-30 8:00 PM)

The design and byte draft are in
`docs\tasks\2026-10-25-chapter-cards\card-4-scene-report.md` and `scripts\one-time\2026-10-25-chapter-cards\c4s_draft.py`
/ `.txt`. Read those, the dialogue in `card-4-scene-study.md`, `scripts\permanent\patches\chapter_cards.py`,
`tests\test_chapter_cards.py` and `scripts\permanent\build_list_trial_chapters.txt`. Read other files only when the
build needs them.

## Final decisions

- Card 4 moves to the first landing on the Northern Mountains, with the arrival scene from the report. Remove the
  current card 4 at the end of the post-Android 20 scene.
- The text shows only my words, with no "NAME:" prefixes (the names were only for us).
- Continue: option c. Chapter 4 shows when flag 86 and visited bit 211 are both set.
- The player stands farthest right. Gohan and Piccolo leading play the Piccolo and Tien lines; Vegeta leading plays the
  Vegeta and Trunks exchange. Everyone flies north except the player.

## Task

1. Build the scene into `chapter_cards.py` (or a new module listed after it in the chapters trial list, if that is
   cleaner: say why). The world map scene start is the one untested part: if the interpreter shows it cannot work,
   use the report's second choice and say so.
2. Tests: the guard (first landing only), the Continue rule, the branch per leader, the text bytes, the removed old card
   4 point.
3. Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v8.gba` from the chapters trial list (check
   absent first; exclusive create). Diff v7 to v8: every run inside a declared site.
4. Test saves next to it, from the report's plan: one slot per leader (Gohan, Piccolo, Vegeta) on the world map with
   bit 211 clear. Say which slot is which.
5. Full suite once at the end.

## Report

Short: `docs\tasks\2026-10-25-chapter-cards\card-4-scene-build-report.md`. SHIPPED and PENDING tables, sites, SHA-1s,
save slots, play steps, suite count. Bible rows (tag C4B, a few) in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_c4b.md`
as `## Section N` table blocks. Label claims CONFIRMED, LIKELY or SPECULATIVE.

## Limits

- Edit only `chapter_cards.py`, `tests\test_chapter_cards.py`, `build_list_trial_chapters.txt`, and a new module and
  test file if you make one. Scripts go in `scripts\one-time\2026-10-25-chapter-cards\` with names starting `c4b_`.
  Python: `py -3.14 -P`. Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Another task edits `celljr_fight.py` and its test. Do not touch them, `build_list.txt`, `docs\RE-BIBLE.md`,
  `docs\ledger\` or `LOG\zhack\`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Work lean: no full enumerations, no long tables. ROM quality comes first.

