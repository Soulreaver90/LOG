# Cell Jr v10: Cell faces Gohan during the scenes

The approved v9 ("CELL JR IS GREAT NOW"), then found one remaining fault while replaying it.

> Cell for some reason goes from looking right to looking south when cell jr walks down, then when the
> battle start, cell looks north to follow gohan as normal, cell should move to follow gohan by looking
> north not south. Same issue with the 1v3, after the fade, cell is again looking south, then looks north
> when the battle starts.

Then, on the 1v3: "he should be facing to the left, not north". Then, on the 1v3 cutscene: "he should be
facing left or north, not south".

## The cause, which I traced before writing this

NPC Cell is item 17 (`CELL_NPC_ITEM`), and its step script is `FACE_PLAYER` (line 81, step `@0x08010098`).
That step turns Cell toward the player. **It does not run while a scene plays**, so during every scene Cell
shows his spawn facing, which is south. The moment the scene ends and normal ticking resumes, the step runs
and snaps him north. The snap I see at the battle start is the step catching up, not a bug in it.

The fix is to set Cell's facing explicitly inside each scene, with `ext 55`.

## The three places, and the facing I want

| Function | Moment | Facing | My words |
|---|---|---|---|
| `fight_start` | the 1v1 starts, one Jr comes down | `UP` | "looking north not south" |
| `one_v_one_end` | the 1v3 starts, after the fade | `LEFT` | "he should be facing to the left, not north" |
| `finish` | the 1v3 cutscene | `LEFT` | "facing left or north, not south" |

`UP` is **1**. The module only defines `DOWN, LEFT, RIGHT = 0, 2, 3` at line 158, because up was never
needed. Add `UP = 1`. Two independent sources confirm the value: `chapter_cards.py:197` defines
`DOWN, UP, LEFT, RIGHT = 0, 1, 2, 3` citing the bible PGS and CJ2 rows, and bible row CSV records `1 = up`.

The geometry agrees with me in both cases. Cell stands at `CELL_STANDS` (512,472).
- `fight_start`: Gohan is at `GOHAN_AT` (576,376), which is 96 px north. Up is right.
- `one_v_one_end` and `finish`: Gohan moves to `MIDDLE` (432,392), exactly 80 px west and 80 px north. The
  diagonal is exact, so the engine has no correct answer and my eye decides. I chose left.

## Do not change

`restore()` at line 315 already sets `ext(55, CELL, RIGHT)`. That is the vanilla restore. Leave it alone.
Do not change `FACE_PLAYER` or the item 17 descriptor. The step is correct, and other scenes rely on it.

## Files you may edit

`scripts\permanent\patches\celljr_fight.py` and `scripts\permanent\tests\test_celljr_fight.py`. Nothing else.

## Gates

1. Build v10 from `build_list_trial.txt`. Check the target is absent, then create it. Copy the v9 save to a
   v10 save the same way, exclusively, so I can play it at once.
2. Rebuild main and confirm it is unchanged.
3. **The op diff.** Compare the v9 and v10 scene records op by op. The only differences must be the added
   `ext 55` ops and the length and offset shifts that follow. If any other op moved or changed, stop and
   report that instead.
4. Confirm `ext(55, CELL, ...)` actually drives the NPC spawned by item 17. `restore()` proves the handle
   works for item 11. If item 17's actor handle differs, say so rather than assuming.
5. Full suite once. Redirect with `2>&1` to a file, read the real exit code, then grep the summary. Never
   pipe a suite through `tail` and read `$?`.
6. Add a test that pins Cell's facing in all three records, so this cannot regress.

## Report

Give: the v10 SHA-1, main's SHA-1, the op diff, the gate 4 answer, the suite count and real exit code, and
the exact lines you changed.
