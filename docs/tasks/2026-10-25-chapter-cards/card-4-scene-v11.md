# Card 4 v11: the v10 play test fixes (final, 2026-10-30 11:55 PM)

Read `scripts\permanent\patches\chapter_cards.py`
(the card 4 block, `SPOTS`, `PLAYER_FACE`, `GROUPS`, `_arrival`), `scripts\permanent\tests\test_chapter_cards.py`,
`docs\tasks\2026-10-25-chapter-cards\card-4-scene-v10-report.md`, and the probes
`scripts\one-time\2026-10-30-card-4-v10\c4w_space.py` and `c4w_plan.py`. **`chapter_cards.py` may have just been
refactored onto `scene_lib`: read it as it is now, not as the v10 report describes it.**

## My words, after playing all three branches

- Gohan branch: "Gohan starts the scene facing down and then quickly turns right, which is ackward. I think looking
  down is the default view, just leave it that way instead of forcing the view to the right. Everything else in the
  gohan control is fine."
- Vegeta branch: "vegeta and trunks still stand too close to the save point, and gohan is very close to them, have
  him further to the right. Since he flies from the bottom, have him land facing up, not facing to the right. Its
  more natural that way."
- Piccolo branch: "For piccolo its even more messy, they all stay too close to the save point, gohan should stand
  further right like he would in the vegeta/trunks version. also have tien and krillin face piccolo. Gohan should be
  facing north as well."

## Build these. They are unambiguous.

1. **Gohan branch: no forced turn.** Remove the `gohan` entry from `PLAYER_FACE`. `_arrival` already emits
   `ext 55 (0, DOWN)` under black, so the player simply stays facing down. Change nothing else in that branch.
2. **Gohan faces up (north)** where he is an NPC, in the Vegeta and Piccolo branches: `SPOTS[branch]["Gohan"]`
   facing to `UP`.
3. **Piccolo branch: Tien and Krillin face Piccolo**, the player. Work out the facing from each one's spot relative
   to the player's, do not hardcode a guess.
4. **Both the Vegeta and Piccolo branches: widen the gap from the save point rect (56,48)-(105,97).** v10 kept spots
   out of the rect but sprites still crossed its edge by up to 192 px. Set a real clearance margin, assert it in a
   test, and report the margin you chose.

## The hard part, and I have already measured it. Do not re-derive.

"Gohan further right" has no clean ground. From my own run of `c4w_space.py`:

- In the whole band y 28-84 there is **no clear spot between x 148 and x 244**.
- The only ground further right is the east pocket, x 248-264 at y 84.
- **An actor at (248,84) overlaps the flight pad (249,89)-(296,144)** (box rule x-8..x+24, y-28..y+8 gives
  x 240-272, y 56-92). That is the same complaint I just made about the save point, on a different object.
  Worse, the flight pad is interactive.

So **do not silently put Gohan on the flight pad.** Instead:

- **Build option B:** keep Gohan at the x 144 end and move Vegeta and Trunks west to open the gap, using the left
  pocket (x 24-44 at y 84) that the Gohan branch already uses. The player lands at `ARRIVE`, which is shared by all
  three branches, so moving the player means moving `ARRIVE`: that is allowed, it is one constant, say so and
  re-clamp `CAMERA`. This satisfies my complaint, which was that Gohan is *too close to them*.
- **Picture, do not build, option A:** Gohan at the east pocket (248,84), that branch's camera moved east. Show the
  flight pad overlap clearly in the picture so I can judge it.
- **Picture, do not build, option C:** Gohan north of the player instead of east.

I decide between them. A, B and C each need one plan picture per affected branch.

## Rules that still hold from v10

No actor inside the save rect. No actor under a BG1 canopy (BG1 draws over actors). No actor south of y 84, where the
text box draws. Flood fill from the player's end spot. Groups: each actor has a mate within 32 px, other groups at
least 40 px away. Also fix the v10 leftovers: Tien and the player overlap 8x16 px in the Piccolo branch.

## Build and test

Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v11.gba` from
`scripts\permanent\build_list_trial_chapters.txt` (check the file is absent first). `.sav` as a byte copy of the v10
save, exclusive create. Update the tests for every new spot and facing; no test may be weakened. Run
`test_chapter_cards.py` only. I run the full suite.

## Report

Short. `docs\tasks\2026-10-25-chapter-cards\card-4-scene-v11-report.md`: SHIPPED and PENDING tables, the SHA-1, a
spot-and-facing table per leader, the clearance margin you chose, the plan picture paths for the built option and for
A and C, and the test count. Label every claim C, L or S. Bible rows (tag C4E) in
`scripts\one-time\2026-10-31-card-4-v11\bible_rows.md` as `## Section N` table blocks.

## Limits

- Edit only `chapter_cards.py` and `test_chapter_cards.py`. Python: `py -3.14 -P`. Never write under `data\`. Never
  overwrite a ROM or a save. LF, no em or en dashes, no byte order mark.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. Four tasks in a row have broken this. Do not be the fifth.
- Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\`, `celljr_fight.py`, `scene_lib.py` or anything under
  `scripts\permanent\emu\`. Do not run the full suite.

