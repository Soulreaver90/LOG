# Card 4 scene v11: the v10 play test fixes (2026-10-31)

Brief: `card-4-scene-v11.md`. Labels: CONFIRMED (C) = ROM bytes, render, collision or a test run; LIKELY (L) = strong evidence, no emulator run; SPECULATIVE (S) = reasoned guess.

> Read the three PENDING rows marked **DECISION** first. Option B is built, but it moves the landing, and that changes the Gohan branch you called fine.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Gohan branch: no forced turn | `PLAYER_FACE` has no `gohan` row, so the arrival's `ext 55 (0, DOWN)` under black is the only facing he gets. He lands looking down and never turns. C (tests, built ops) |
| 2. Gohan faces up where he is an NPC | `SPOTS["piccolo"]["Gohan"]` and `SPOTS["vegeta"]["Gohan"]` are `(144, 84, UP)`. C |
| 3. Piccolo branch: Tien and Krillin face Piccolo | Both spots carry `AT_PLAYER`, and `facing_to()` works the byte out from the spot. Krillin gets LEFT, Tien gets LEFT. A diagonal spot raises instead of guessing. Trunks uses the same rule in the Vegeta branch. C |
| 4. Widen the gap from the save point rect | `CLEAR = 8` px of floor between the drawn 16x32 frame and the rect, `POCKET_CLEAR = 0` for an actor wholly west of it. Section "The margin, and why it is two numbers". C |
| Gohan further right (option B built) | The landing moves to the west pocket, so Gohan keeps the x 144 end. He is now 104 px from Vegeta and 120 px from Piccolo, against 24 px in v10. C |
| v10 leftover: Tien in the player, 8x16 px | Gone. A new test proves no two drawn frames share a pixel in any branch. C |
| Plan pictures | 3 for the built option B, 2 each for A and C. Section "Files" |
| Tests | `test_chapter_cards.py` **75 OK** (v10: 72). Three new tests, none weakened. Section "Tests" |
| Build | `log2_poc_r40_chapters_v11.gba` SHA-1 `8c2edb063e04cc619e7fae32e6e2e953ff92daa0`, `.sav` a byte copy of the v10 save (SHA-1 `d5a44ccc83b741f0265024fc1848dd0b134a9765`) |
| Bible rows | `scripts\one-time\2026-10-31-card-4-v11\bible_rows.md`, tag C4E |

## PENDING

| Item | Why | My step |
|---|---|---|
| **DECISION: A, B or C** | B is built. A and C are drawn only, but all three were laid out under the same rules and all three now pass with 0 faults, so the choice is about how they read, not about which is legal. Section "The three options, measured" | Look at the seven pictures and say which one you want |
| **DECISION: B moves the landing, so the Gohan branch changed** | The landing is one constant in record 0, which runs before the leader pick, so one spot serves all three branches. The player now lands in the west pocket, where Trunks and Vegeta used to stand, so that pair moved to (120,84) and (144,84). The composition is the same as the one you called fine, mirrored: pair facing each other, player alone, trio north. The trio itself did not move. C | Check the Gohan branch still reads right. If not, A or C keeps it exactly as you played it |
| **DECISION: B loses "the piccolo trio near him"** | Only one actor fits beside the player in the pocket, so Krillin stands with Piccolo and Tien moved to (120,76), 96 px east. He still faces Piccolo. C | Say if you want the trio back; that needs A or C |
| One actor still touches the save rect edge | In the Vegeta and Piccolo branches the pocket pair gets 16 px and 0 px of floor, because the pocket is exactly 32 px of floor wide. 0 px means the frame touches the rect edge and no pixel is on it, against -6 px in v10. Everyone else gets 14 px or more. C | Look at it. If the one at x 40 still reads as standing on the switcher, option A is the only one that gives every actor floor to spare, and its price is two actors on the flight pad |
| Tien still at (96,44) in the Gohan branch | His frame is 4 px on the rect, as in v10. Your words scoped ask 4 to the other two branches, and he cannot move: every spot with 8 px of floor is inside 40 px of the pair the new landing displaced, or overlaps Piccolo or Krillin. C | Say if you want him moved; it needs the Gohan trio redesigned |
| The scene in play | No emulator run. Every claim about how it *reads* is L | Play the v11 ROM with the v11 save, one branch at a time |
| What the save point actually draws | The v10 study found no BG2 or BG3 mark and no art on the item. Whether `save_point_factory` builds a sprite at run time is still untraced, so "too close to the save point" is measured against the 50x50 rect, not against anything drawn. S | Nothing to do; it only means the margin is conservative |
| Trunks and Vegeta climb behind treetops | Unchanged from v10. `ext 54` ignores collision, so nobody can be blocked (C); they pass behind trees | Check by eye |
| Build log line | `docs\build-log.md` is outside this task's files, so the build wrote its line to `scripts\one-time\2026-10-31-card-4-v11\c4x_build.md` | Append that line to `docs\build-log.md`, or ask me to |

---

## The margin, and why it is two numbers

Your words were that they "stand too close to the save point". v10 kept every actor's **spot** out of the rect but let the drawn frame cross its edge by up to 6 px. v11 measures the **drawn 16x32 frame** instead, and asks for floor between it and the rect (56,48)-(105,97).

I swept the whole band y 28-84 for the floor each clear spot gives. C (`c4x_plan.txt`).

| Floor wanted | Where an actor may stand |
|---|---|
| 8 px | x 116 and east (x 112 at y 32, x 120 at y 28); west, only the pocket x 24-32 at y 84 |
| 12 px | x 120 and east; west, x 24-28 |
| 16 px | x 124 and east; west, x 24 only |

**The west pocket is 32 px of floor wide**, from x 24 to x 55. Two 16 px sprites fill it exactly, so a pair standing there gets 16 px and 0 px and no better split exists. That is why the rule is two numbers: `CLEAR = 8` for everyone, and `POCKET_CLEAR = 0` for an actor wholly west of the rect. Both are asserted for the Vegeta and Piccolo branches. C.

This is a real deviation from the brief, which asked for one margin. One margin of 8 px would mean no pair in the pocket, and your Vegeta and Trunks argue with each other in that branch (lines 8-12), so I kept them side by side.

---

## The three options, measured

All three obey the same rules, so you compare like with like. For A and C I pinned only what the option *is* (where the player and Gohan stand) and placed every other actor again by an exhaustive search over the clear-spot set, keeping the layout that moves least from the v10 spots you played. **All three now have 0 faults.** C (`c4x_fit.txt`, `c4x_plan.txt`).

| | B (built) | A (drawn) | C (drawn) |
|---|---|---|---|
| Landing | west pocket (24,84) | (120,84), as v10 | (120,84), as v10 |
| Gohan | (144,84), 104-120 px from the pair | east pocket (248,84), 112 px | (120,44), 40 px north of the player |
| Gohan branch | **changes** (the displaced pair moves east) | untouched | untouched |
| Faults | 0 | 0 | 0 |
| Camera | (0,0), unchanged | (49,0) for that branch only | (0,0), unchanged |
| On the save rect | nobody; the pocket pair gets 16 and 0 px of floor | **nobody, and nobody on 0 px either**: the least floor is 8 px | nobody; the pocket pair gets 16 and 0 px of floor |
| On the flight pad | nobody | **two actors**: Gohan 15x3 px and whoever joins him 16x3 px, on an interactive object | nobody |
| Main cost | the Gohan branch changes | the strip east of the save point holds four actors, not five, so one more has to cross 100 px of trees to stand in the east pocket with Gohan | Gohan takes the only northern spot, so two actors go to the west pocket, which **splits Vegeta from Trunks**, the pair that argues in that branch's dialogue |

Option A needs its own camera, which is free: `ext 31` is inside each branch's own arrival record, so a per-branch camera adds no branch point. C.

**A is the only option with no actor at 0 px of floor from the save rect**, because it is the only one that uses neither pocket for a pair. Its price is the flight pad and a split cast. L (how either reads in play).

---

## Spots and facings (option B, built)

Facing byte: 0 down, 1 up, 2 left, 3 right. C (bible PGS and CJ2 rows). The player always lands at (24,84). "Floor" is px between the drawn frame and the save point rect.

**Gohan leads**

| Actor | Spot | Faces | Group | Floor |
|---|---|---|---|---|
| Tien | (96,44) | north | north | -4 (carried over, see PENDING) |
| Piccolo | (120,44) | north | north | 14 |
| Krillin | (136,32) | left | north | 30 |
| Trunks | (120,84) | right | east | 14 |
| Vegeta | (144,84) | left | east | 38 |
| **Gohan (player)** | (24,84) | **down** | on his own | 16 |

**Piccolo leads**

| Actor | Spot | Faces | Group | Floor |
|---|---|---|---|---|
| Trunks | (120,28) | right | north | 14 |
| Vegeta | (136,28) | left | north | 30 |
| Tien | (120,76) | left (at Piccolo) | east | 14 |
| Gohan | (144,84) | **north** | east | 38 |
| Krillin | (40,84) | left (at Piccolo) | pocket | 0 |
| **Piccolo (player)** | (24,84) | north | pocket | 16 |

**Vegeta leads**

| Actor | Spot | Faces | Group | Floor |
|---|---|---|---|---|
| Krillin | (136,32) | left | field | 30 |
| Piccolo | (120,44) | north | field | 14 |
| Tien | (120,76) | north | field | 14 |
| Gohan | (144,84) | **north** | field | 38 |
| Trunks | (40,84) | left (at Vegeta) | pocket | 0 |
| **Vegeta (player)** | (24,84) | **right** (at Trunks) | pocket | 16 |

Trunks and the player face each other in the Vegeta branch, and Trunks and Vegeta face each other in the other two. Nobody faces down except the Gohan branch player, which is the point of ask 1. C (tests).

---

## Checks

`c4x_plan.py` reads the spots out of the module, so the pictures and the numbers describe what the ROM builds. **0 faults for option B.** C (`c4x_plan.txt`).

| Rule | Result |
|---|---|
| Actor box clear (no BG1 canopy, no BG2 rock, every collision cell open) | All 18 spots clear |
| Drawn frame keeps CLEAR or POCKET_CLEAR floor from the save rect | Holds in the Vegeta and Piccolo branches; the Gohan branch keeps Tien at -4 on purpose |
| No actor south of y 84 | None. The landing is on the line itself |
| No two drawn frames share a pixel | Holds in all three branches (v10 had one 8x16 px overlap) |
| Group holds together (a mate within 32 px) | Holds; the longest nearest mate is 32.0 px |
| Groups stand apart (nothing of another group within 40 px) | Holds; the closest pair between groups is exactly 40.0 px |
| View holds every sprite at its widest and tallest | Holds at camera (0,0), unchanged and still inside the clamp (137, 41) |
| An AT_PLAYER facing really points at the player | Holds for all three |
| Player can still walk off | 2554 positions reachable, flight pad reachable, from the new landing |

---

## Tests

`test_chapter_cards.py`: **75 OK**, 30 s. Three new tests, nothing weakened.

| Test | What it proves |
|---|---|
| `test_every_sprite_keeps_floor_between_itself_and_the_save_point` | Ask 4, with the v10 spots as a yardstick inside the test |
| `test_no_two_sprites_overlap` | The v10 leftover cannot come back, in any branch |
| `test_tien_and_krillin_look_at_the_player_and_gohan_lands_facing_north` | Asks 1, 2 and 3. The looking facings are worked out in the test from the restated spots, so a hardcoded byte in the module cannot pass |

I checked the new tests have teeth: seven deliberately bad layouts (a frame 4 px on the rect, a frame with 6 px of floor where 8 is wanted, two kinds of sprite overlap, a looker facing away, Gohan back on the v10 facing, the forced turn restored) were each caught by the right test. C.

---

## Changes

- `scripts\permanent\patches\chapter_cards.py`: `ARRIVE` (24,84); new `SPRITE`, `CLEAR`, `POCKET_CLEAR`, `AT_PLAYER` and `facing_to()`; `SPOTS`, `PLAYER_FACE` and `GROUPS` rewritten; `spot_list()` resolves `AT_PLAYER` and defaults the player's facing to DOWN; `_arrival()` reads `spot_list()` and emits the player's `ext 55` only where `PLAYER_FACE` has a row. `CAMERA` is unchanged and re-checked.
- `scripts\permanent\tests\test_chapter_cards.py`: `REC0_HEX`, `PLAYER_SPOT` and the restated spots, facings and groups updated; new `SPRITE`, `CLEAR`, `POCKET_CLEAR`, `MARGIN_BRANCHES`, `LOOKS_AT_PLAYER`, `FACES_NORTH`, `DOWN`; `spots_of()` and `test_branch_per_leader` handle a branch with no player facing; the three new tests above.

## Files

- Module and tests: `scripts\permanent\patches\chapter_cards.py`, `scripts\permanent\tests\test_chapter_cards.py`.
- One-time `scripts\one-time\2026-10-31-card-4-v11\`: `c4x_plan.py` and `c4x_plan.txt` (every rule checked, all three options), `c4x_fit.py` and `c4x_fit.txt` (the search that laid options A and C out again under B's rules), `c4x_build.md`, `c4x_tests.txt`, `bible_rows.md`, and the seven pictures:
  - built option B: `c4x_plan_B_gohan.png`, `c4x_plan_B_piccolo.png`, `c4x_plan_B_vegeta.png`
  - option A, drawn only: `c4x_plan_A_vegeta.png`, `c4x_plan_A_piccolo.png`
  - option C, drawn only: `c4x_plan_C_vegeta.png`, `c4x_plan_C_piccolo.png`
- Builds `builds\mockups\2026-10-25-chapter-cards\`: `log2_poc_r40_chapters_v11.gba`, `log2_poc_r40_chapters_v11.sav`.

## Notes

- v10 to v11: 165 differing runs, 2222 bytes. One byte below `0x800000`, at `rom:0x23B38`, the Continue vtable hook word that every chapters build writes; everything else is in the expansion area. The built ROM holds the new record 0 once, and the v10 one is gone. C.
- `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\`, `celljr_fight.py`, `scene_lib.py` and `scripts\permanent\emu\` were not touched. `chapter_cards.py` still does not import `scene_lib`; it takes the encoders through `piccolo_gi_scene`, which re-exports them.
- Process: one Bash call began with a `cd` command, which the brief and the LOG rules forbid. Every path in every command and every script was absolute, and nothing was written outside this task's folders, but the call should not have carried `cd` at all.
