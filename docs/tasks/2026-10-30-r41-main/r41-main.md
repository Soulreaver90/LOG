# r41: promote chapter_cards (v7) into main (final, 2026-10-30 7:32 PM: "fade is great, add to the master")

Read only these:
`docs\tasks\2026-10-30-r40-main\r40-report.md` (the r40 promotion you repeat), `scripts\permanent\build_list.txt`,
`scripts\permanent\build_list_trial_chapters.txt`, the other `build_list_trial*.txt` files, and the tests that pin r40
(`grep -rn "14d6b831\|R40" scripts\permanent\tests`).

## Task

1. Move `chapter_cards` into `build_list.txt` as the last line, with an `r41` comment like the r40 lines. Turn
   `build_list_trial_chapters.txt` into an alias of main with a comment, as r40 did for its four lists.
2. Update the pins that name r40 as "main" so they name r41 or the right prefix. A module whose "before" is a main
   prefix keeps that prefix. No test may be weakened. If a test fails for a real reason (a byte conflict, a refusal),
   stop and report it.
3. Check that the Cell Jr trial (`build_list_trial.txt`) and the Vegeta 19 trial still build on r41. A refusal is a
   stop-and-report; moved addresses are expected.
4. Build `builds\log2_poc_r41.gba` with `log2_build.py --list scripts\permanent\build_list.txt` (check that the file is
   absent first). It must equal the chapters v7 ROM `57896c9f`: if it does not, report the diff runs. Make
   `log2_poc_r41.sav`, `_spar`, `_computer` as byte copies of the r40 saves (exclusive create), with `.gba` copies for
   the two named saves.
5. Full suite once at the end.

## Report

Short. `docs\tasks\2026-10-30-r41-main\r41-report.md`: SHIPPED and PENDING tables, SHA-1s (r41, trials on r41),
pins changed (file:line, old, new), suite count. Bible rows (tag R41, a few) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-r41-main\bible_rows.md`.

## Limits

- Edit only `build_list.txt`, the trial lists and the tests. Do not change any patch module. Python: `py -3.14 -P`.
  Never write under `data\`. Never overwrite a ROM or save. LF, no em or en dashes, no byte order mark.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens
  a file.
- Another task studies card 4 (read only). Do not touch `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`. Do not.

