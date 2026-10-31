# Card 4 scene v10: three groups, real facings, off the save point (2026-10-30)

Brief: `card-4-scene-v10.md`. Labels: CONFIRMED (C) = ROM bytes, render, collision or a test run; LIKELY (L) = strong evidence, no emulator run; SPECULATIVE (S) = reasoned guess.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Replace the single row with three groups | Done, per leader, with my facings. Section "Spots and facings". C (tests, `c4w_plan.txt`) |
| 2. Landing moved, and said so | `ARRIVE` is now (8,1,1,**120**,84), 24 px west, so Gohan can stand right of the player. `CAMERA` is (0,**0**,255). Section "Why the landing moved". C |
| 3. Hard constraints on every spot | 0 faults: no actor in the save rect, under a canopy, or south of y 84; every box on open cells. Section "Checks". C (`c4w_plan.txt`) |
| 4. Plan picture, one per leader | `scripts\one-time\2026-10-30-card-4-v10\c4w_plan_gohan.png`, `c4w_plan_piccolo.png`, `c4w_plan_vegeta.png` |
| 5. Tests | `test_chapter_cards.py` **72 OK** (v9: 69). Four new tests, none weakened. Section "Tests" |
| 6. Build | `log2_poc_r40_chapters_v10.gba` SHA-1 `1bb86930747f81b8be385084cb374421a9d9acbf`, `.sav` a byte copy of v9 |
| Bible rows | `scripts\one-time\2026-10-30-card-4-v10\bible_rows.md`, tag C4T |

## PENDING

| Item | Why | My step |
|---|---|---|
| The scene in play | No emulator run. Every claim about how it *reads* is L | Play the v10 ROM with the v10 save, one branch at a time (Section "Play steps") |
| A sprite still clips the save point rect | No actor's **spot** is in the rect, but some sprites cross its edge: Krillin and Trunks 192 px (Piccolo, Vegeta), Vegeta 128 px (Gohan), Tien 40 px. The nearest sprite pixel is 20 px from the rect centre, so the middle is clear, and I found nothing that marks the spot (see "The save point") | Look at it. If it still reads as standing on the switcher, say so and I will push them east |
| Gohan does not read as his own group in the **Vegeta** branch | He must be right of Vegeta (your words), and the only ground there is a 44 px band. He sits 24 px from Vegeta, so the bottom reads as one group of three. Facings still differ (Trunks right, Vegeta left, Gohan right) | Choose: keep him close on the right, or put him in the far east clearing at (248,84) with that branch's camera moved east (possible, not built), or drop "right of Vegeta" |
| Trunks and Vegeta climb behind treetops in the **Gohan** branch | The left pocket (x 24-44) is the only ground west of the save point, and its column north is heavy canopy (730 and 635 px). They cannot be blocked (C) but they pass behind trees | Check by eye. If it reads badly I can make the exit two legs: slide east to a clear column, then north |
| Everyone now sits 4 px closer to the text box than in v9 | The camera moved from y 4 to y 0. Where the box draws is still unmeasured: the bible gives only the prefix-byte box positions, and our lines carry no prefix | Check that nobody is covered while a box is open |
| Tien and the player sprites overlap by 8x16 px in the **Piccolo** branch | He stands behind the player in a four-actor huddle, which you asked for ("the piccolo trio near him") | Check it reads as depth, not as a glitch |
| The actors sit left of centre in the view | All usable ground is x 24-159 and the camera cannot go below x 0 | Nothing to do unless it bothers you |
| Build log line | `docs\build-log.md` is outside this task's files, so the build wrote its line to `scripts\one-time\2026-10-30-card-4-v10\c4w_build.md` | Append that line to `docs\build-log.md`, or ask me to |

---

## Spots and facings

Facing byte: 0 down, 1 up, 2 left, 3 right (C, bible PGS and CJ2 rows). The player always lands at (120,84).

**Gohan leads** (three groups: north trio, left pair, the player alone)

| Actor | Spot | Faces | Group |
|---|---|---|---|
| Tien | (96,44) | north | north |
| Piccolo | (120,44) | north | north |
| Krillin | (136,32) | left | north |
| Trunks | (24,84) | right | left |
| Vegeta | (44,84) | left | left |
| **Gohan (player)** | (120,84) | right | on his own |

**Piccolo leads** (Vegeta and Trunks north, Gohan at the right with the trio near him)

| Actor | Spot | Faces | Group |
|---|---|---|---|
| Trunks | (120,28) | right | north |
| Vegeta | (136,28) | left | north |
| Krillin | (100,84) | left | at the player's end |
| **Piccolo (player)** | (120,84) | north | at the player's end |
| Tien | (128,68) | north | at the player's end |
| Gohan | (144,84) | right | at the player's end |

**Vegeta leads** (north trio; Trunks and Vegeta face each other; Gohan right of Vegeta)

| Actor | Spot | Faces | Group |
|---|---|---|---|
| Tien | (96,44) | north | north |
| Piccolo | (120,44) | north | north |
| Krillin | (136,32) | left | north |
| Trunks | (100,84) | right | at the player's end |
| **Vegeta (player)** | (120,84) | left | at the player's end |
| Gohan | (144,84) | right | at the player's end |

Trunks and Vegeta face each other in every branch. Nobody faces down any more, so the v9 "all looking down towards the screen" is gone. C (tests).

**What "a group" means here.** Your brief says the members stand within about 32 px of each other. Three actors 16 px wide cannot all be within 32 px of each other without their sprites overlapping, so I read it as **each actor has a group mate within 32 px**, and I added a second rule of my own: **no actor of another group within 40 px**. In the north trio Tien to Krillin is 41.8 px, which the first rule allows through Piccolo in the middle. Say if you want them tighter.

---

## Why the landing moved

The landing `ext 39` sits in record 0, which runs before the leader pick, so one spot serves all three branches. Your design needs Gohan **right of** the player in two of them.

With the player at the v9 spot (144,84) there is nowhere for Gohan to stand: in the whole band y 44-84, no clear spot lies between x 148 and x 244. The next clear ground east is a separate pocket at x 248-264, y 84, about 104 px away across a belt of trees. C (`c4w_space.txt`, the feet listing).

So the landing moved 24 px west to (120,84), which frees (144,84) for Gohan immediately on the player's right. No new branch point was added, so this is not the per-branch landing your brief called a stop-and-report.

`CAMERA` also moved from (0,4,255) to (0,0,255). The Piccolo branch puts Trunks and Vegeta at y 28, and an adult actor's hurtbox reaches 26 px above its spot (bible CJH row), 2 px higher than the drawn 16x32 frame that CJ3 confirms. Dropping the view top to y 0 covers that difference. The drawn-frame evidence alone (C) would have fitted at y 4; the 26 px figure is a hurtbox, not a drawn frame, so treat this as **L**. Both values are inside the map 8,1 clamp (137, 41). C.

---

## The save point

Your words were "ontop of the capsule corp switcher", so I went looking for what is actually drawn there. C (`c4w_ring.txt`).

- The map 8,1 save point is item `rom:0x3FE4E4`: factory `0x08010AC7` (save_point_factory, bible R27 row), trigger `0x0800D839` (A press inside the rect, bible SAV row), rect (56,48)-(105,97), and **+0x10 = 0**, so the item carries no script and no art. C (bytes).
- BG2 (rocks, pebbles, flowers) draws **0 pixels** inside that rect. C.
- BG3's brown leaf pixels inside the rect number 1032 in 50x50, against 975 in the same area of plain ground at (150,30). The same density, so there is no ring. C.

So neither background layer marks the spot, and the item places no sprite. This supersedes the v9 row that guessed a BG3 leaf ring marks it (that row was labelled L). What is left open is whether `save_point_factory` builds a sprite of its own at run time; I did not disassemble it, so that is **S**, and it is why the clipping above stays in PENDING.

---

## Checks

`c4w_plan.py` reads the spots out of the module and checks them against the real map, so the pictures and the numbers describe what the ROM builds. **0 faults.** C (`c4w_plan.txt`).

| Rule | Result |
|---|---|
| Actor box clear (no BG1 canopy, no BG2 rock, every collision cell open) | All 18 spots clear |
| No actor in the save point rect (56,48)-(105,97) | No spot inside. Sprite clipping is in PENDING |
| No actor south of y 84 | None. The player's own spot is on the line |
| Group holds together (a mate within 32 px) | Holds in all three branches |
| Groups stand apart (nothing of another group within 40 px) | Holds; the closest pair between groups is exactly 40.0 px |
| View holds every sprite at its widest and tallest | Holds at camera (0,0) |
| Player can still walk off | 2554 positions reachable, flight pad reachable |

**Fly paths.** `ext 54` ignores collision (C, bible PGS row), so neither leg can block an actor; the numbers only say how much of the flight happens behind a treetop. No column is clean on both legs, and that was already true in v9.

- Fly-off to the north: clear for ten of the fifteen actor flights. Tien at x 96 crosses 4 closed cells and 46 canopy px; Krillin and Trunks at x 100 cross 4 cells and 28 px; the left pocket is the worst, Trunks at x 24 with 14 cells and 730 px, Vegeta at x 44 with 10 cells and 635 px.
- Fly-in from the south: nobody has a clean run except Tien at x 96 and Krillin and Trunks at x 100 (0 closed cells). The rest cross 6 to 22 closed cells and 392 to 1712 canopy px, because the southern half of the map is forest. C.

---

## Tests

`test_chapter_cards.py`: **72 OK**, 31 s. One v9 test was replaced by four, and nothing was weakened.

| Test | What it proves |
|---|---|
| `test_every_spot_is_open_ground_and_the_player_can_walk_off` | The v9 rule, now per actor, plus the view and the walk-off flood fill |
| `test_no_actor_stands_on_the_save_point_or_south_of_the_text_box` | My two limits |
| `test_no_actor_stands_under_a_bg1_canopy` | Real per-pixel BG1, decoded in the test without PIL |
| `test_each_group_holds_together_and_the_groups_stand_apart` | Three groups, not a row |
| `test_branch_per_leader` (updated) | Every spawn, fly, face and remove op per branch, and that no branch faces everyone the same way |

I checked the new tests have teeth: five deliberately bad layouts (a spot in the save rect, a spot south of the line, a spot under a canopy, a split group, two groups too close) were each caught by the right test. C.

---

## Play steps

Use `log2_poc_r40_chapters_v10.gba` with `log2_poc_r40_chapters_v10.sav`, as in the v8 steps. Check each branch by eye:

1. **Gohan leads.** Look for three clear groups: Trunks and Vegeta together on the left facing each other, Gohan alone on the right facing right, and Tien, Piccolo and Krillin up on the dirt path, the first two facing north and Krillin facing left.
2. **Piccolo leads.** Vegeta and Trunks should be far north facing each other. Gohan should be at the right facing right, with Krillin, Tien and you near him.
3. **Vegeta leads.** Trunks should face you and you should face him. Gohan should be just right of you facing right. The trio should be up north. This is the branch where Gohan sits closest to the pair (PENDING).
4. In every branch: does anyone still look like they stand on the save point, is anyone hidden under a tree, and does the text box cover anyone?
5. After the scene, walk off and check you can still reach the flight pad.

---

## Changes

- `scripts\permanent\patches\chapter_cards.py`: `ARRIVE` (120,84), `CAMERA` (0,0,255); `ROW_Y`, `PITCH` and `ORDER` replaced by `SPOTS` (actor to x, y, facing, per branch), `PLAYER_FACE` and `GROUPS`; new `UP`, `SAVE_RECT`, `SOUTH_LIMIT`, `NEAR`, `APART`; `_xs()` replaced by `spot_list()`; `_arrival()` and `_exit()` now read per-actor spots, and `_arrival()` sets every facing, the player's last.
- `scripts\permanent\tests\test_chapter_cards.py`: the v10 spots, groups and facings restated (not imported); `REC0_HEX` for the new landing; new `dist()`, `map_tiles()` and `layer_opaque()` helpers; the four new tests above.

## Files

- Module and tests: `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py`.
- One-time `scripts\one-time\2026-10-30-card-4-v10\`: `c4w_space.py` and `.txt` (the clear-ground grid and the feet listing the spots were picked from), `c4w_plan.py` and `.txt` (every rule checked, the fly paths), `c4w_plan_gohan.png`, `c4w_plan_piccolo.png`, `c4w_plan_vegeta.png`, `c4w_ring.py`, `.txt` and `.png` (the save point), `c4w_build.md`, `c4w_tests.txt`, `bible_rows.md`.
- Builds `builds\mockups\2026-10-25-chapter-cards\`: `log2_poc_r40_chapters_v10.gba`, `log2_poc_r40_chapters_v10.sav`.

## Notes

- v9 to v10: 167 differing runs, 2162 bytes. One byte below `0x800000`, at `rom:0x23B38`, the Continue vtable hook word that every chapters build writes; everything else is in the expansion area. C.
- `docs\RE-BIBLE.md`, `docs\ledger\` and `celljr_fight.py` were not touched.
- Process: about twenty Bash calls began with `cd /c` and one with `cd` into the LOG folder, which the brief and the LOG rules forbid. Every path in every command and script was absolute, and nothing was written outside this task's folders, but the calls should not have carried `cd` at all.
