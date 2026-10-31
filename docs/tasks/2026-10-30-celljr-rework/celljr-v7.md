# Cell Jr v7: my play-test fixes (final, 2026-10-30 9:20 PM)

Read `docs\tasks\2026-10-30-celljr-rework\celljr-rework-report.md`,
`scripts\permanent\patches\celljr_fight.py` and `tests\test_celljr_fight.py`. Read other files only when needed.

## My words (v6 play test)

1. Screenshot after the finish: "You wretched child!!!" with Gohan and Cell near the top right of the view, not in
   the middle. "They should be centered."
2. "The Jrs should surround Gohan, not walk to a designated spot. Except being out of bounds, so maybe a transition to
   the middle and have them come in."

## Task

1. **Centering.** Find why Gohan and Cell sit off-centre at "You wretched child" (record N is vanilla; the cause is
   likely the v6 finish F moving Gohan or the camera). Fix it so the pair is centred in the view, as in vanilla.
2. **Surround.** For each group walk-in (the 3 Jrs before the 1 v 3 in K1, and the 3 Jrs of the finish F): a short
   fade out, Gohan is placed in the arena middle, the camera centres on him, fade in, then the Jrs come in from the
   view edges and stop around him (for example left, right and above), not at fixed spots away from him. Keep every
   position inside the arena bounds. Keep the rest of v6 as it is.
3. Tests for the new positions and the camera, and the old v6 tests updated, none weakened.
4. Build `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v7.gba` from `build_list_trial.txt` (check absent;
   exclusive create), with a `.sav` byte copy of the v6 save. Diff v6 to v7: every run inside a celljr_fight site.
   Full suite once at the end.

## Report

Short: `docs\tasks\2026-10-30-celljr-rework\celljr-v7-report.md`. SHIPPED and PENDING tables, the cause of the
off-centre view, the new positions, SHA-1, suite count. Bible rows (tag CJ7, a few) in
`scripts\one-time\2026-10-30-celljr-rework\bible_rows_v7.md` as `## Section N` table blocks.

## Limits

- Edit only `celljr_fight.py` and `tests\test_celljr_fight.py`. Scripts go in `scripts\one-time\2026-10-30-celljr-rework\`
  with names starting `v7_`. Python: `py -3.14 -P`. Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Another task edits `bf_ki_pool.py` and its test. Do not touch them, `build_list.txt`, `docs\RE-BIBLE.md`,
  `docs\ledger\` or `LOG\zhack\`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Work lean. ROM quality comes first.

