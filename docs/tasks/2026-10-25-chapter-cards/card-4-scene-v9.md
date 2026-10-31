# Card 4 scene v9: land the team on open ground (final, 2026-10-30 9:40 PM)

Read `docs\tasks\2026-10-25-chapter-cards\card-4-scene-build-report.md`,
`scripts\permanent\patches\chapter_cards.py` (the card 4 arrival records) and `tests\test_chapter_cards.py`. Read other
files only when needed (map 8,1 layout, collision and camera: search the bible for map render and collision tools).

## My words (v8 play test, Vegeta branch)

The scene starts and plays. "They fly in being blocked, I didn't consider the terrain." My screenshot: the row stands
across bushes and trees at the bottom of the view. Tien is half hidden in a bush, one team member is hidden behind a
bush, and Vegeta stands on a rock.

## Task

1. Render map 8,1 around the landing (BG layers plus collision) and pick an open patch with room for the whole row:
   five NPCs plus the player, on walkable ground with no tree, bush or rock over or under any of them, and no tree
   canopy between them and the camera. The player may be placed there too (the spawns happen under black). Keep
   the player farthest right. The fly-in and fly-out paths may cross trees (they fly), but the landed row must be clear.
2. Move the row, the player spot and the camera to that patch in all three branches. After the scene the player keeps
   control at that spot: check that it is walkable and not boxed in.
3. Make a picture of the planned row drawn on the map render (`builds\mockups\2026-10-25-chapter-cards\v9_row_plan.png`)
   so I can check it by eye before I play.
4. Update the tests, build `log2_poc_r40_chapters_v9.gba` in the same folder from `build_list_trial_chapters.txt`
   (check absent; exclusive create), with a `.sav` byte copy of the v8 save. Diff v8 to v9: every run inside a
   chapter_cards site. Full suite once at the end.

## Report

Short: `docs\tasks\2026-10-25-chapter-cards\card-4-scene-v9-report.md`. SHIPPED and PENDING tables, the chosen patch and
why, the positions, SHA-1, suite count. Bible rows (tag C4V, a few) in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_c4v.md`.

## Limits

- Edit only `chapter_cards.py` and `tests\test_chapter_cards.py`. Scripts go in `scripts\one-time\2026-10-25-chapter-cards\`
  with names starting `c4v_`. Python: `py -3.14 -P`. Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Other tasks edit `celljr_fight.py`, `bf_ki_pool.py`, a new `gi_base_audit` module and their tests. Do not touch them,
  `build_list.txt`, `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.
- Never write under `data\`. Never overwrite a ROM, save or state. LF, no em or en dashes.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file.
- Work lean. ROM quality comes first.

