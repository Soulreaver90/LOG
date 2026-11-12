# Brief: arena v7, the fight starts the way every other fight in the game starts

Build task. Build ONE trial ROM and run the full suite once at the end. Follow `docs\tasks\global.md`.

Read `docs\tasks\2026-11-06-arena-v6\brief.md` for the scope split that still applies. The 17/18 scene
stays byte for byte vanilla. Everything here is the future Cell scene and the arena map.

## The owner's finding, and why v6 is wrong

He played v6 and said:

> "Why is it fading!??? Look at how EVERY OTHER FIGHT WORKS! There should not be a fade at all after the
> diague! Dialogue ends fight begins with a camera pan to the user and the hud appearing, like every single
> fight int he game."

He is right. I CONFIRMED it by decoding the record he named, Piccolo against Android 17, map 11,4,
scene table `rom:0x3E47F8`. The fight starts in record 6 at `rom:0x3E47DC`:

```
ext104(9, 1) ; bar_set(set=9, lo=75, hi=100) ; header_bit1(value=1) ; camera_follow(who=0)
```

**Four ops. No fade, no map load, no wait.** Record 0 of the same table parks `camera(152, 96, speed=3)`
at the start of the talk. The whole conversation runs on that fixed camera, and `camera_follow(0)` then
glides the view to the player. That glide is the pan he screenshotted.

Record F cannot have that shape while it loads a map, because a map load replaces the camera in one frame
(bible row from the v5 study: `map_load @0x0800C584` writes the new player into `0x030020C0 + 4` and stores
it in `0x03000FF4`). I treated that snap as a missing cover and added a fade. **The load is what must move.**

## Part 1: move the arena load to the start of the Cell scene

Vanilla record 13 `rom:0x3B7E4A` already opens the Cell scene with its own cover:

```
wait(60) ; fade_out(frames=180) ; load_map(6,1,1,136,432) ; wait(120) ; walk(133,248,568) ; wait(100)
```

The new record 13 loads the ARENA there instead, under that same vanilla fade, and makes the player
Super Saiyan Trunks. Order, and each line is load bearing:

1. `wait(60) ; fade_out(180)` unchanged. Those bytes are the 17/18 side of the boundary.
2. `ext 73 (3, 133)` then `push 3 ; ext 70`. The form must be set BEFORE the load, because the load is what
   builds the player's body. CONFIRMED in the v5 study: `appearance_revert @0x08003ED4` skips the record
   whose index equals the leader byte that `set_leader` has just written.
3. `ext 39 load_map_at(6, 100, 1, 248, 624)`.
   **Use `ext 39`, never `ext 35`.** Only `ext 38` and `ext 39` reach `sub_0800C584`, the one route to the
   player constructor `player_ctor @0x080086D4`. `ext 35` builds no player at all. Bible row 1579 carried
   the opposite claim, it is corrected in place, and it cost build v6. Do not re-inherit it.
   **(248,624) is NOT a view origin. It is where the PLAYER lands.** It is map 6,1 item 5's own spot, the
   spot vanilla's NPC Trunks starts from. Bible row 1072 for `ext 39`, row 1094 for why `ext 35` differs.
   Loading the player at vanilla's `136,432` would rebuild the v4 and v7 defect, "it loads trunks in a
   different area then moves him back".
4. A short settle wait, under black. v4 proved a load does not finish inside its own op and wipes what
   follows it.
5. `camera(136, 456, 2)`, the existing `VIEW` constant in `ending_fight.py`, which frames Cell (244,504) and
   Trunks (248,568) together. This is the parked camera the Piccolo shape needs. **READ whether `ext 31`
   takes the view top left or its centre before you trust the numbers** (bible row 1000 bears on this).
6. `fade_in`. Vanilla has none here because `ext 35`'s handler `sub_08009852` carries its own fade path and
   `ext 39`'s `sub_08009A88` does not. Confirm that, then pick the length.
7. `walk(0, 248, 568) ; wait(100)`, the player walking the NPC's own path. His words on 2026-11-05: "have it
   follow the same path as the NPC, no hand off needed".

Records 14 to 22, the conversation itself, then run on the player instead of set 133. Every actor op takes
set 0 except `spawn`; `ext 51 spawn`'s handler `@0x08009CC4` calls `npc_factory @0x0800D6DE`, which never
looks an actor up.

## Part 2: record F becomes the four op Piccolo shape

Record F, ending table word 23, becomes exactly:

```
ext104(28, 1) ; bar_set(28, lo, hi) ; header_bit1(1) ; camera_follow(0)
```

No fade, no load, no wait, no `ext 73`, no `ext 70`, no `ext 31`, no placing of anybody. The form, the
leader, the spots and the camera were all settled in record 13 and nothing has moved since.

Delete the `COVER` and `HOLD` constants. The owner's five second pause question dies with them.

## Part 3: you must READ how Cell exists during the talk

This is the one thing the design does not settle, and a guess here reproduces the v5 defect in a new place.

Today `battle_arena` makes Imperfect Cell the map's only ITEM, with condition 0, so the map load builds him
as the ENEMY, already wired to his death event. The Piccolo shape instead converts an ordinary NPC with
`ext 104` at the fight start.

Read `ext 104`'s handler, the arena item's wiring in `battle_arena.py`, and `celljr_fight.py`'s own
`ext 51` plus `ext 104` pair, then answer both:

- **Is a map built enemy item idle during a scene?** If he attacks, or the bar appears, during the
  conversation, he cannot be built as an enemy at load time.
- **Can `ext 104` carry the death event table D?** If it can, make the arena item an ordinary NPC Cell,
  vanilla record 15's `walk(set=28, 244, 504)` plays as written, and record F's `ext104(28,1)` turns him
  into the enemy exactly as Piccolo's record does. That is the better shape. If it cannot, keep the enemy
  item and state what you proved about his idleness.

State which it is, with the proving instruction, and label it CONFIRMED. **Do not guess.**

## Part 4: the Capsule Corp entrance, CONFIRMED by my own read

`INSIDE_BAND = (28, 9, 35, 11)`. That is the whole fix. Today it is `(28, 9, 35, 10)` and
`DOOR_MOUTH_ROW = 11` is left open on purpose, on line 117 of `battle_arena.py`.

The arena's collision at the entrance, from `map_view.collision` on the v6 build against the base ROM:

```
            x 224-287
  VANILLA 6,1        ARENA v6 6,100
  cy  9  ####........#####   #################
  cy 10  ####........#####   #################
  cy 11  ####........#####   ####........#####   <- the hole
  cy 12  ................    ................
```

Vanilla runs an 8 cell doorway corridor up from the plaza and catches the player with the layout warp at
(224,88)-(273,105). The arena kills the warps, so the corridor is just floor. Closing rows 9 and 10 only
left a one row pocket: the owner walks up into it, hits the wall a row later, and stands inside the recess
behind the BG1 glass, invisible. His words: "its like I run into a wall, but I can walk into it", and his
v3 state 5 shows him gone. His v3 state 4 at **(246,94)** is cell (30, **11**), the open row.

Closing row 11 makes the wall flush with the building face at cy 12. Nothing in the arena ever arrives from
inside, because the warps are gone, so the `map 6,2 lands him on cell (31,12)` reason in the docstring does
not apply to this map. Remove `DOOR_MOUTH_ROW` and the sentence that defends it.

**Backlog item 14 is WRONG and must be struck.** The blue at px (224-287, 200-223) is floor reflection art
in the plaza tiles, not a door, and it is open in vanilla too. Do not close it.

## Part 5: the save point and the map post are layout PROPS

CONFIRMED by my own read of map 6,1's layout `rom:0x5F209C`, using bible row 1119 (layout +0x24 prop count,
+0x28 prop entries of 24 bytes, +0x2C the prop sheet frame header):

```
+0x24 count = 5   +0x28 list = 0x085F16DC
  prop 0  (224, 64)-(288, 96)    64x32
  prop 1  (240,200)-(272,232)    32x32   inside the A-press script region (225,193)-(272,248)
  prop 2  (408,556)-(472,620)    64x64   on the save point region (408,568)-(457,617)
  prop 3  (198, 95)-(214,127)    16x32
  prop 4  (294, 95)-(310,127)    16x32
```

The arena copies this layout and zeroes only +0x40 and +0x44, the warps, so all five props came with it.
v4 painted out their floor SHADOWS and left the objects. His words: "why are the map post and save spots
STILL THERE!??? I Thought we agreed to remove them, you only removed the shadows".

Give the arena its own prop list holding props 0, 3 and 4 only, with +0x24 = 3. **Render the layout and
confirm which prop is which before you cut any entry**, because props 0, 3 and 4 are probably the arch and
the two entrance posts and he has not asked for those to go. Do NOT simply zero +0x24 and +0x28.

Then read the collision cells under props 1 and 2. If they are closed, he is left with an invisible block
standing where the save point was, and that must be opened in the same build.

## Part 6: fix the checker, which is enforcing the wrong default

This is the thing he actually asked for on 2026-11-06: "if anything can be built into our tooling so all
future battles dont need this trouble again, just a standard battle start".

Of the 27 vanilla records that raise a boss bar, **26 load no map**. `scene_lib.battle_start()` was built
from the one that does, `rom:0x3E9384`, because that one matched the architecture I had already chosen.

- Make the Piccolo shape the DEFAULT of `battle_start()`: enemy, bar, HUD, `camera_follow`.
- Keep the fade and load variant, explicitly named, for a record that really does open a scene.
- Add an assertion to `test_battle_start.py`: a control record that shows a bar loads no map and opens no
  fade, unless its module declares a `BATTLE_START_EXCEPTIONS` entry. Record F fails this today.
- Keep every existing assertion. `test_form_survives_the_leader_change` is STILL expected to stay RED with
  exactly one finding, `rom:0x89A9C0` in `fullpower_ssj`. Do not touch `fullpower_ssj` and do not declare an
  exception for it.

## Already done by me, do not redo

`scene_probe.map_entry` now resolves the live map table from the literal at `rom:0xEBD8` instead of the base
ROM constants. That fixes `scene_probe --map --rom` and `map_view --rom` together, so both read an appended
map such as 6,100. Update the `map_view.py` docstring trap note and `docs\tool-index.md` line 52, which both
still warn about the stale table.

## Expected end state

- The 17/18 scene byte for byte vanilla. Prove it by comparing words 0 to 12 against the base ROM.
- Record F is four ops and loads no map.
- The arena entrance recess is closed, and the save point and map post are gone.
- Report the exact `Ran N tests` and `FAILED (failures=N)` lines.

## Build and rules

- Trial to `builds\mockups\2026-11-05-ending-arena\`, named `log2_poc_r41_arena_v7.gba`, from
  `build_list_trial_ending.txt`. Print the SHA-1 and pair a `.sav`. **That is the one arena mockup folder.**
  Do not create a new folder per version; the owner corrected this on 2026-11-06.
- Run the suite once at the end. **Redirect to a file and read the file.** A pipe or a trailing command
  reports the LAST command's exit code: on 2026-11-06 that showed "exit code 0" on a run with 3 failures.
- Every source byte, word and record checked before the first write; a second run raises.
- Absolute paths only. Never `cd`. Python header block, no em or en dashes, no byte order mark.
- Label every reverse-engineering claim CONFIRMED, LIKELY or SPECULATIVE.
- Write `docs\tasks\2026-11-06-arena-v7\report.md` content as your report message, and `rows.md` with tag
  `AR7` for any ROM fact you learn.

One report message, then stop. Do not add a byte order mark.
