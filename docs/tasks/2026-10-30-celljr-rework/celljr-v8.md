# Cell Jr v8: Gohan teleports to the last Jr instead of flying (my play test 2026-10-30 11:20 PM)

Read only these:
`scripts\permanent\patches\celljr_fight.py` (the `finish()` block, lines 281-294, and `_explode()`),
`scripts\permanent\tests\test_celljr_fight.py`, and `docs\tasks\2026-10-30-celljr-rework\celljr-v7-report.md`.
Search `docs\RE-BIBLE.md` (tags CJ6, CJ7, CJP, CH6) before you read the ROM.

## My words

"The gohan flying up to the cell jr in the cutscene looks terrible, the sprite is just garbage. Maybe have him
teleport behind the top cell jr instead of flying."

## Task

1. **Replace the fly with a teleport.** In `finish()` the `fly` block is today
   `ext 121 (0, FLY)` + `ext 136 (0, *GOHAN_FLIES_TO, GOHAN_FLY_N)` + `ext 55 (0, RIGHT)` + `_melee(FLY_KNOCK)` +
   `_explode()`. Drop the `FLY` pose and the `ext 136` glide. Gohan vanishes where he stands, reappears north of the
   last Jr, faces it, and punches. The punch and the explosion do not change.
2. **Copy the game's own teleport look. Do not invent one.** Bible line 918 puts Imperfect Cell's
   "#Instant transmission..." line at record `rom:0x3E5E80`, table `rom:0x3E6078`. Goku's teleport plays in the words
   just before it. Decode those words, name the ops it uses, and reuse them. Only if that scene has no reusable effect,
   fall back to flash + remove + respawn + flash, and say so in the report.
3. **"Behind" means north of the Jr**, because the Jr faces Gohan. Gohan reappears facing south and punches south.
   Check that his new spot, his facing and the knock path are inside the finish view and on the open collision bands,
   with the v7 method and its scripts.
4. **Tests.** The finish no longer needs the Gohan fly row. Replace the fly-row test and its refusal with teleport
   assertions (vanish, spot, facing, punch, no `ext 121` FLY in `finish()`). That is a replacement, not a weakening. No
   other test may be weakened. **Do not touch any fly row that `vegeta_ssj_scene` uses: main must still rebuild to
   `14d6b831`.** If a test fails for a real reason, stop and report it.
5. **Build** `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v8.gba` with
   `scripts\permanent\build_list_trial.txt` (check the file is absent first). Make the `.sav` as a byte copy of the v7
   save (exclusive create). Run `test_celljr_fight.py` only. I run the full suite.

## Not in scope

The 1 v 1 Jr death is settled: I played it and it reads as an explosion. Every cutscene Jr uses `_explode()`.
Do not change the type descriptors, the scouter or `_explode()`.

## Report

Short. `docs\tasks\2026-10-30-celljr-rework\celljr-v8-report.md`: SHIPPED and PENDING tables, the SHA-1, the teleport
op sequence with its source address, Gohan's old and new spots, the test count, and I play steps. Label every
claim C, L or S. Bible rows (tag CJ8) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-celljr-v8\bible_rows.md`.

## Limits

- Edit only `celljr_fight.py` and `test_celljr_fight.py`. Python: `py -3.14 -P`. Never write under `data\`. Never
  overwrite a ROM or a save. LF, no em or en dashes, no byte order mark.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Another task is editing `chapter_cards.py` and `test_chapter_cards.py`. Do not touch them, `docs\RE-BIBLE.md`,
  `docs\ledger\` or `LOG\zhack\`. Do not run the full suite.

