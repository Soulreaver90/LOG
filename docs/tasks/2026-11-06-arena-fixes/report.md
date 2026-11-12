# The arena's two play-test defects, 2026-11-06

> **Controller note.** The agent could not write this file: this harness refuses a report `.md` from a
> subagent, so I saved its report below from the hand-back. This is the second arena task in a row to
> hit that refusal.
>
> **What I verified myself, independently, before relaying any of it.** I wrote my own ROM reader
> (`scratch\verify_arena_v2.py` and `verify_arena_v2b.py`) without reading the agent's probes, and
> resolved every pointer from the literal at `rom:0xEBD8` outward.
>
> | Claim | My result |
> |---|---|
> | v2 ROM SHA-1 `3efd69eb90d72efaa9da80e45dc97c89e7dfe069` | CONFIRMED |
> | v1 ROM still `d6348550`, its `.sav` and the owner's three `.ss` states intact | CONFIRMED, nothing overwritten |
> | Live map table `0x0893d704`, count byte `0x49`, 328 maps | CONFIRMED |
> | Arena entry 327: zone 6, area 100, combat 1, 0 regions, 1 item | CONFIRMED |
> | Arena has its OWN layout list and its OWN collision frame | CONFIRMED, `0x0893d700` and `0x0893b62c` against map 6,1's `0x083f9b2c` and `0x085f164c` |
> | Arena frame is type 0, size 0x2000 | CONFIRMED |
> | The layout copy differs from map 6,1's at bytes 0x34, 0x35, 0x36 ONLY | CONFIRMED |
> | 600 open cells | CONFIRMED |
> | Floor at px x 16..495, y 608..687, cells x 2..61, y 76..85 | CONFIRMED, exact match |
> | Both fighters stand on an open cell | CONFIRMED |
> | Map 6,1 entry 145 is vanilla, its own layout, type 1 frame | CONFIRMED |
>
> **My own error, recorded so the number is not read wrongly.** My first reader assumed a 128 cell
> grid stride and reported 0 open cells, which contradicted the agent. The agent was right and I was
> wrong: the stride is 256. I note it because the agent's own text says map 6,1 has "4422 open cells of
> 16384", which implies a 128 grid, and I could not check that figure because map 6,1's frame is type 1
> and compressed. The arena figure does not depend on it: the payload is 8112 zero bytes carrying
> exactly 600 set bits, so no cell outside the floor is open under ANY of the three geometries I tried.
>
> **Not verified by me and still open:** the knockback (SPECULATIVE in the agent's own words), the
> follow camera's settle offset, and the claim that the copy never opens a cell map 6,1 had closed,
> which needs the compressed frame expanded.

---

## The ROM

```
list   scripts\permanent\build_list_trial_ending.txt
out    builds\mockups\2026-11-06-arena-fixes\log2_poc_r41_arena_v2.gba
sha1   3efd69eb90d72efaa9da80e45dc97c89e7dfe069
save   log2_poc_r41_arena_v2.sav, 8192 bytes, seeded from log2_poc_r40.sav
```

Picture of the arena floor: `arena_floor_v2.png` beside this file. Red tint is a closed cell, blue
tint is a cell BG1 paints, and the two green marks are the fighters' spots.

The folder did not exist before the build. No ROM, save or state was overwritten. The agent rebuilt
the same list to a scratch path after its last edit and got the same SHA-1, so the file on disk is the
current source.

Probes: `scripts\one-time\2026-11-06-arena-fixes\p1_probe.py` to `p9_blockers.py`.

---

## 1. What v1 already tried

| Where | What it tried |
|---|---|
| `2026-11-05-ending-fight-1\root-cause.md` | v2 removed `ext 33 camera_follow(0)`. Not a camera fault |
| `v3-playtest.md` | v3 loaded map 6,1 at (248,568) and let the load spawn the player |
| `ending_fight.py` docstring, v4 | v4 moved the load to (136,432) and added `ext 62`. **This made the defect** |
| `2026-11-05-ending-arena\report.md` | v6 swapped map 6,1 for map 6,100, keeping v4's (136,432) |

The two step is v4's own change. The contradiction `root-cause.md` left open, "object 4's y does not
agree with `move_to`", is now explained: the player was at the LOAD position, not the `move_to` target.

## 2. Defect A: the player appears in the grass, then is moved

### Cause: CONFIRMED

`ext 39`'s x and y are the PLAYER's position. v4 read them as a view origin.

- `code_08009a88.s` (`ext 39`) pops five values, writes the last two into one `{s16 x, s16 y}` pair on
  its stack, and calls `loc_0800C584` with that pair in r3.
- `code_0800c584.s` builds the camera from the pair: `LDRSH r7,[r4,#0] ; SUB r7,#0x70` and
  `LDRSH r7,[r4,#2] ; SUB r7,#0x4C`, so the camera is (x - 112, y - 76).
- At `loc_0800C608` it passes **the same pair, unchanged**, as r2 to `loc_080086D4`, the constructor
  the v5 note already named as the one that gives the player a body.

So the load put the player at (136,432) with the camera on (24,356). Record F then waited 120 frames
and ran `ext 62` to (248,568), 112 px right and 136 px down, in plain view.

The owner's second capture confirms it independently: (136,432) is grass with trees, north of the
courtyard, with the building to the right. That is the view a camera at (24,356) gives.

`sub_0800C584` is the only function in the whole tree that subtracts both 0x70 and 0x4C.

Record K is cleared: its geometry restore runs between `ext 40` and `ext 41`, a fade, so it is not the
visible move.

### Fix

`map_reload()` now returns `(zone, area, 1) + TRUNKS_SPOT`. Decoded out of the built ROM:

```
rom:0x941EC7  push 3 ; leader
rom:0x941ECB  push 6, 100, 1, 248, 680 ; load_map_at
rom:0x941ED7  push 120 ; wait
rom:0x941EDB  push 0, 248, 680 ; move_to
rom:0x941EE4  push 0, 1 ; face
rom:0x941EEA  push 1 ; header_bit1
rom:0x941EEE  push 28 ; bar_show
next index 26 (END), 47 bytes
```

The load and the move name the SAME spot, so there is nothing to see. `ext 62` was kept on purpose: at
the same coordinates it is invisible, and it still puts the player right if anything else moves him
during the settle. A test fails if the two ever disagree.

### Not closed: LIKELY

The opening frame's framing. The map load centres at (x - 112, y - 76). Record K and `celljr_fight`
use (x - 112, y - 80) for a fixed view, so the two agree within 4 px. The agent did not find the follow
camera's own offsets, so it cannot prove the view does not shift a few pixels when control returns.

## 3. Defect B: the arena had no walkable bound at all

All three reports have one cause.

### Cause: CONFIRMED

Map 6,100 copied map 6,1's layout pointer, so it inherited Capsule Corp's whole collision bitmap. An
empty region list removes warps, exits, the save point and the world map. It does not remove GROUND.
Map 6,1 has 4422 open cells of 16384: the courtyard, the grass, the side paths and every interior.

```
map entry 145 rom:0x40B320  +0x2C -> 0x083F9B2C   a ONE word layout list, 1 variation
            0x083F9B2C     [0]   -> 0x085F209C   the layout struct
            0x085F209C     +0x34 -> 0x085F164C   the collision frame, type 1, 0x2000 bytes
```

### Why the head clips, and it is not a sorting bug: CONFIRMED

BG0 and BG1 carry priority 1 and draw OVER an actor. Map 6,1 has no BG0. Its BG1 carries the building
front:

- cell rows 60 to 68 (px y 480 to 551) are BG1 across the whole width, with a gap only at the gateway;
- collision rows 61 to 63 (px 488 to 511) are CLOSED except cells x 26 to 37 (px 208 to 303), the
  gateway through that wall;
- below row 68 there is no BG1 until row 89.

**Cell's own arena spawn, (244,504), is inside that gateway**: x 244 is cell 30, y 504 is cell 63. He
stood in the arch and the arch drew over him. That is the zoomed capture exactly: legs, feet and shadow
on the tile, head and upper torso under the pink and red band. His spawn was the worst cell on the map
for this, so no collision edit alone could have fixed it.

The bible CH8 row about BG2 does not cover this. The layer at fault is BG1.

### Collision cannot be bypassed: CONFIRMED

- `Object_IsBlocked` `@0x0800E438` and `Bitmap_RectIsBlocked` `@0x0800E45E` both return early with **1**
  when obj+0x18D is nonzero. The name is inverted: 1 means free, 0 means blocked.
- Enumerating every access to obj+0x18D by two shapes, the `0xFF + 0x8E` index and the `obj + 0x180`
  then `+0xD` base, gives five sites. Four only READ it (`Bitmap_FillObjectCells`,
  `Bitmap_RectIsBlocked`, `Object_IsBlocked`, `sub_0800E33A`). One writes it: `sub_0800E3EE`.
- **Zero aligned words in the whole ROM equal 0x0800E3EF**, and no `.s` file branches to that label. So
  nothing can call the only writer and the flag is never set.

### The collision box never reaches above the anchor: CONFIRMED

`Rect_FromFields` `@0x0800793A` builds the rect every blocked test and every footprint stamp uses:

```
x = obj+0x158 >> 8 ; y = obj+0x15C >> 8        the anchor, 8.8 fixed
w = byte [obj+0x154] ; h = byte [obj+0x155]
rect = {x, y, x + w, y + h}
```

The anchor is the rect's TOP LEFT and the rect extends right and down only. So an actor standing on the
floor's top row has his whole collision rect inside the floor, and the floor's top edge cannot be
crossed from above. The sprite still draws 56 px above the anchor, which the clearance rule accounts for.

### The engine accepts a raw collision frame: CONFIRMED

This was the ship blocker, and no vanilla map proves it: all 336 vanilla layouts carry a **type 1**
collision frame and zero carry type 0. So the agent read the loader.

`Scene_BuildLayers` `@0x08006152`, which `loc_0800C390` calls on the map load path, allocates the
0x2000 byte buffer and then:

```
LDR r1, [r4, #0x6C]      the 0x2000 buffer
LDR r0, [r5, #0x34]      r5 is the LAYOUT; +0x34 is the collision frame
BL  loc_0801F394         Container_Decode
```

`Container_Decode` `@0x0801F394`:

```
r3 = [frame + 0]                    the type
type 1 or 2 -> BL loc_080236A8      the decompressor
type 0      -> r2 = [frame + 4]     the size
               BL loc_08021DF0      a raw copy of size bytes from frame + 8
anything else -> returns, doing nothing
```

So layout +0x34 goes through the type dispatcher and type 0 is a raw copy. The frame declares 0x2000
and the buffer is exactly 0x2000 (`MOV r6,#1 ; LSL r6,#0xD`), so there is no overflow.

### Fix

```
arena entry 327 +0x2C -> a new ONE word layout list
                      -> a copy of map 6,1's layout, ONE word changed, +0x34
                      -> a new raw collision frame, 0x2008 bytes
```

- The layout copy is 0xCC bytes. Measured, not guessed: the closest pair of layout addresses in the
  table is 204 bytes apart (`0x086A8A1C` and `0x086A8AE8`), so the engine can never read more than 204
  bytes off a layout pointer.
- Every pointer in the copy except +0x34 is map 6,1's, so the arena still LOOKS like Capsule Corp.
  Those pointers are read only.
- The new frame keeps open only the arena floor and closes all 15784 other cells. It never opens a cell
  map 6,1 had closed, and a test enforces that.

### The arena floor, as a rectangle to judge by eye

```
px x 16..495, y 608..687        cells x 2..61, y 76..85
480 x 80 px                     600 open cells
```

It is the largest rectangle of the courtyard where every cell is open AND Imperfect Cell's whole sprite
stays off BG1. His sprite envelope is 20 px left, 44 right, 56 up and 8 down from his point, measured
over all 192 frame records of set 28. Trunks is 8, 24, 24 and 8 over 241 records, so Cell sets the
bound. The floor's south edge is map 6,1's own wall at y 688.

**Both spots had to move, and that is the owner's to reverse.** Neither old spot is legal:

| Actor | Was | Is | Why |
|---|---|---|---|
| Imperfect Cell | (244,504) | (244,616) | the old spot is the gateway, under the arch |
| the player | (248,568) | (248,680) | the old spot is 8 px above even Trunks' own clear band |

The pair keeps its 64 px gap and its x, so the framing is the one he saw working. Both moved 112 px
down. Record K's blast path, x 244 to 248 and y 616 to 680, is open in the new frame, so the vanilla ki
blast still reaches Cell. If he wants the fight further up the courtyard, the only way is to accept the
building front over their heads: rows 69 to 75 clear Trunks but not Cell.

### Still LIKELY, not CONFIRMED: the knockback

The layout makes this the common case, because the player stands below Cell and knocks him north toward
the floor's top edge, which has no margin.

What the agent has: of the seven functions in the AI range that write the position words +0x158 and
+0x15C, six also call one of the six collision entry points. The seventh, `sub_0801C144`, computes a
vector and appears to continue into `sub_0801C218`, which does test. The bible CJH row puts a knockback
at 36 to 59 px over about 32 frames.

What it could not do: the vtable at `0x08023D68` does not read as code pointers at file offset
0x23D68 (the words are `0xFFFF6E3D`, `0xFFFF6EAF`, `0xFFFF6F45`), so it could not name the tick slot
and open it. **SPECULATIVE: a knockback could carry Cell a short way past a closed cell, into the band
that was closed, under the building front.** Play test step 6 is the cheap answer.

## 4. The closed-box option, as a comparison only

`p5_enclosed.py` flood fills every layout's open cells and keeps only components that never reach the
grid edge, so closed cells surround them on all sides. 191 such rooms exist across 327 layouts.
`p6_confirm.py` then applies Cell's own BG0 and BG1 test to the best.

| Map | Layout | Enclosed open cells | Clear rectangle for Cell |
|---|---|---|---|
| **14,3, the Cell Games arena** | `0x084E50A4` | 4810 | **px x 320..575, y 296..679, 256 x 384** |
| 14,4 | `0x084E2E7C` | 4810 | px x 224..623, y 488..663, 400 x 176 |
| 1,2 | `0x086ACB68` | 5683 | px x 16..743, y 504..583, 728 x 80 |
| 6,3 | `0x085EF4F8` | 7213 | px x 680..823, y 312..391, 144 x 80 |
| 6,60 | `0x085C90E0` | 4747 | px x 432..495, y 496..647, 64 x 152 |

Map 14,3 is the clear winner and it needs no collision edit at all. It is the game's own arena, it is
already a sealed box, and it gives a 256 x 384 px floor against the courtyard's 480 x 80.
`celljr_fight` already stages fights on it. **The agent did not switch to it.** That is the owner's
design call.

A warning on the earlier metric: the agent's first survey ranked layouts by the largest all open
rectangle and returned twelve maps at a full 1024 x 1024. Those are maps whose collision frame is all
open. Largest all open is not a closed box test, which is why the table above uses enclosure instead.

## 5. Tests

`test_battle_arena.py` 32 to 41. `test_ending_fight.py` 28 to 31.

Defect A: `test_the_map_load_puts_the_player_on_the_fight_spot`,
`test_nothing_moves_the_player_to_a_second_place`, `test_both_fighters_stand_on_the_arena_floor`.

Defect B: `test_the_arena_frame_is_a_raw_frame_of_the_right_size`,
`test_exactly_the_arena_floor_is_open_and_nothing_else` (600 cells, no more and no fewer),
`test_the_copy_never_opens_a_cell_map_6_1_had_closed`,
`test_no_cell_of_the_floor_lets_a_wall_draw_over_cell_s_head`,
`test_map_6_1_s_whole_layout_chain_stays_vanilla` (entry, list, struct and frame),
`test_the_layout_copy_differs_from_map_6_1_s_only_at_the_collision_word`,
`test_a_changed_layout_chain_refuses_before_writing`,
`test_the_arena_has_its_own_layout_list_not_map_6_1_s`.

The head clearance test carries two guards against passing open, added after its first green run: it
asserts that BG0 or BG1 was found at all, and it asserts that the same rule REJECTS the gateway cell
the owner photographed. Without them a missing layer would have made it pass silently.

**One gap the tests cannot close:** every test decodes the new frame with Python's `unpack_frame`. No
test can see how the engine reads it. That is why the `Container_Decode` listing above is the real
evidence, not the tests.

## 6. Verified out of the built ROM by the agent

`p7_verify.py`, reading the v2 file from disk and resolving the LIVE map table from the literal at
`rom:0xEBD8`, because `map_view` and `scene_probe` still read the old 327 entry table:

```
live map table rom:0x93D704, count byte rom:0xE0AE = 0x49 (328 maps)
arena entry 327 rom:0x941E8C   zone 6 area 100 combat 1 regions 0 items 1
  +0x2C -> rom:0x93D700 -> layout rom:0x93D634 -> frame rom:0x93B62C
  the arena's frame: type 0, size 0x2000, unpacked 8192
open cells 600, bounds px x 16..495, y 608..687, and the set EQUALS the declared rectangle
Cell (244,616) open, Trunks (248,680) open
the layout copy differs from map 6,1's at bytes 0x34, 0x35 and 0x36 only
map 6,1 entry 145, its layout list, its layout struct and its collision frame: all vanilla
map 6,1's own collision is still type 1
the new table's entry 145 equals the base entry 145
```

## 7. What to check in mGBA

1. Trunks appears **on his fight spot** when the arena loads. Not anywhere else first, and never seen
   to move. That is defect A.
2. He can move, attack and transform, as in v1.
3. Imperfect Cell is there with a full boss bar and fights back.
4. **Walk in every direction.** The floor is 480 x 80 px. The grass, the side paths and every interior
   must be unreachable. That is defect B.
5. **Cell's head**, through the whole fight. No wall or building tile may cover him.
6. Knock him INTO the north edge and watch whether the knockback carries either fighter off the floor.
   That is the one hole measurement could not close.
7. The arena sits 112 px lower in the courtyard than v1. Say whether the framing still reads right.
8. Beating Cell still runs the collapse, the ki blast, the tail and "The End.".
9. A few other maps still load, because the map table still moves.

## 8. Rule breaks the agent disclosed

Three, all its own:

1. `cd` in Bash calls early in the session, against the absolute paths rule.
2. `cd` again in a small heredoc that added an `if __name__` guard to `p5_enclosed.py`.
3. That same heredoc ran bare `python`, not `py -3.14 -P`.

No harm resulted. Every call after that uses absolute paths. This is the second arena task in a row to
break the `cd` rule.

## 9. Still open

- The knockback trace. SPECULATIVE that a knockback can cross a closed cell. It decides whether a
  collision bound is enough on its own.
- Whether the follow camera settles at the map load's own offset. LIKELY, not proven.
- The arena's layout source: map 6,1's courtyard at 480 x 80, against map 14,3's sealed arena at
  256 x 384. Owner's call.
- Both spots moved 112 px down. Owner's call to reverse.
- The banner at entry +0x0C is still `0xBE`, the Capsule Corp name he called a fault. One word, carried
  from the v1 deferred list.
- The arena's music word +0x24 is still 0.
- The bible `EF1` row still describes the old map 6,1 route.

## 10. Bible rows to merge

- `ext 39`'s x and y are the PLAYER's position; the camera is (x - 112, y - 76), built in
  `sub_0800C584`, which hands the same pair to the player constructor `sub_080086D4`. C.
- Map 6,1's layout chain: entry 145 +0x2C -> `0x083F9B2C` (one word) -> `0x085F209C` -> +0x34 ->
  `0x085F164C`, type 1, 0x2000 bytes. One aligned word names each link. C.
- A layout struct is at most 204 bytes: the closest pair of layout addresses is `0x086A8A1C` and
  `0x086A8AE8`. C.
- `Container_Decode` `@0x0801F394`: type 0 is a raw copy of [frame+4] bytes from frame+8 via
  `loc_08021DF0`; types 1 and 2 go to `loc_080236A8`; any other type returns doing nothing.
  `Scene_BuildLayers` `@0x08006152` sends layout +0x34 through it into map view +0x6C, so a type 0
  collision frame works. All 336 vanilla layouts are type 1. C.
- `Rect_FromFields` `@0x0800793A` builds every collision rect as
  {x, y, x + [obj+0x154], y + [obj+0x155]} from the 8.8 anchor at +0x158 and +0x15C. The anchor is the
  rect's top left and the rect never reaches above it. C.
- `Object_IsBlocked` `@0x0800E438` and `Bitmap_RectIsBlocked` `@0x0800E45E` return 1 for FREE, and both
  bypass on obj+0x18D. The only writer of that byte is `sub_0800E3EE`, and no aligned word in the ROM
  names it, so the bypass is unreachable. C, two shapes.
- Map 6,1 BG1 carries the Capsule Corp building front across cell rows 60 to 68; collision rows 61 to
  63 are closed except the gateway at cells x 26 to 37. The courtyard below row 68 has no BG1 until row
  89. C.
- Sprite envelopes from the frame records: set 28 is 20 left, 44 right, 56 up, 8 down over 192 records;
  sets 132 and 133 are 8, 24, 24, 8 over 241 and 234. C.
- 191 enclosed open rooms exist across 327 layouts; map 14,3 `0x084E50A4` is the largest usable, with a
  256 x 384 px rectangle clear of BG0 and BG1 for set 28. C.
