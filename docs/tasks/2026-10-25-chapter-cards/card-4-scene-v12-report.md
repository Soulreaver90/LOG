# Card 4 scene v12: the whole scene moves to the vanilla landing

Build `log2_poc_r40_chapters_v12.gba`, SHA-1 `b1743beb4bb73217ae0474d3e1ef25e08efa8da1` (C, rebuilt to a scratch
path and compared). Save `log2_poc_r40_chapters_v12.sav`, an exclusive byte copy of the v11 save, SHA-1
`d5a44ccc83b741f0265024fc1848dd0b134a9765`. Tests: `test_chapter_cards.py` only, 75 OK, the v11 count.

---

## SHIPPED

| Ask, in my words | What landed | Label |
|---|---|---|
| "Lets use the default landing location, not the save point" | Record 0 lands the first visit on `LAND` (8,1,1,272,128). Both arms carry one spot. The nearest actor now keeps 78 px of floor from the save point rect | C |
| "a wide top box", "the trio" | The clearing's wide top: Tien (232,84) and Krillin (264,84) facing each other, Piccolo (248,92) 8 px lower facing up | C |
| "a far left box", Gohan alone | The clearing's west arm: Gohan (184,100) in the Vegeta and Piccolo branches | C |
| "gohan is alone at the landing/map point" | Gohan branch: the player at (272,128), nobody else in his group | C |
| "trunks lands next to him" | Vegeta branch: Trunks (296,120), 25 px from Vegeta, facing him | C |
| "krillin/tien to either side of piccolo, both facing him" | Piccolo branch: Krillin (248,124) right, Tien (296,120) left, one in each south prong | C |
| "Vegeta and Trunks where gohan was" | Gohan branch: Trunks (176,100) and Vegeta (192,100), facing each other | C |
| "in the box that the trio was in" | Piccolo branch: Trunks (236,84) and Vegeta (256,84), facing each other | C |
| Re-derive the camera | `CAMERA = (137, 41, 255)`, the map clamp read from layout `0x0858CB30` +8 | C |
| Capture all three branches, read RAM | 18 of 18 spots and facings equal the module | C |

## PENDING

| Item | Label |
|---|---|
| My eye on the three frames. I play and decide | - |
| Whether the trio reads as a huddle. Its three frames touch along their edges, because the clearing is 48 px wide at that row, which is exactly three sprites | C (the width), L (how it reads) |
| Whether the first A press after the scene should leave the map. The player ends the scene inside the world map exit rect, so one A press returns him to the world map. That is the vanilla behaviour of that spot; v11 landed him away from it | C |
| Main `build_list.txt`. Still a trial list; approval moves the `chapter_cards` line | - |

---

## How the three areas were found

Not from the screenshots. `c4y_areas.py` builds the clear-spot grid of map 8,1 on the world-aligned step 4
grid, then takes its connected components. One component holds the landing, and its shape has exactly three
parts my three boxes map onto (C, `c4y_areas.txt`).

```
x 176..308, y 84..124, 178 spots      # = clear, o = clear but over BG2 decoration, . = not clear
     1111112222222222222222222222222333
     7888990001122233444556667788899000
     6048260482604826048260482604826048
y  84 ..............oooo#####...........
y  88 ............oooooo#######.........
y  92 ..........oooooooo#########.......
y  96 ..........oooooooo#########.......
y 100 oooo#####ooooooooo###############.
y 104 ...........ooooooo###############.
y 108 ...........ooooooo################
y 112 ............oooooo################
y 116 ..............#####...........####
y 120 ...............####...........####
y 124 .................##...........###.
```

| His words | The part | World |
|---|---|---|
| "a wide top box" | the wide top of the diamond | y 84-96, x 216-280 |
| "a far left box" | the west arm, one row | y 100, x 176-208 |
| "beside the landing" | the two south prongs | x 232-248 and x 296-308, y 116-124 |

The player sits one row below the grid, between the prongs, at (272,128).

**The camera** is the clamp (137, 41) (C). y 41 is forced: the landing is y 128, and a smaller camera y only
pushes him further down the screen. x 137 holds the whole clearing, because the widest sprite spans x - 9 to
x + 25 and 176 - 9 is east of 137. A smaller x buys ground the scene does not use.

---

## Spots and facings, read out of RAM

Every row comes from `emu\actors.py` on the EWRAM dump of a real run, not from the module (C).

| Gohan leads | Spot | Faces | Group |
|---|---|---|---|
| Tien | (232,84) | right | top |
| Piccolo | (248,92) | up | top |
| Krillin | (264,84) | left | top |
| Trunks | (176,100) | right | far left |
| Vegeta | (192,100) | left | far left |
| Gohan (player) | (272,128) | down | landing |

| Piccolo leads | Spot | Faces | Group |
|---|---|---|---|
| Trunks | (236,84) | right | top |
| Vegeta | (256,84) | left | top |
| Gohan | (184,100) | up | far left |
| Krillin | (248,124) | right | landing |
| Tien | (296,120) | left | landing |
| Piccolo (player) | (272,128) | up | landing |

| Vegeta leads | Spot | Faces | Group |
|---|---|---|---|
| Tien | (232,84) | right | top |
| Piccolo | (248,92) | up | top |
| Krillin | (264,84) | left | top |
| Gohan | (184,100) | up | far left |
| Trunks | (296,120) | left | landing |
| Vegeta (player) | (272,128) | right | landing |

Krillin, Tien and Trunks carry `AT_PLAYER`: the module works the facing out from the spot, and the test works
the same byte out again from its own restated spots.

---

## Captures and plan pictures

| Path | What it shows |
|---|---|
| `scratch\capture\v12_gohan-20261031-101756\shots\v12_gohan_settled.png` | Gohan branch, first box open |
| `scratch\capture\v12_piccolo-20261031-101806\shots\v12_piccolo_settled.png` | Piccolo branch, first box open |
| `scratch\capture\v12_vegeta-20261031-101814\shots\v12_vegeta_settled.png` | Vegeta branch, first box open |
| `scratch\capture\v12_gohan_after-20261031-101949\shots\v12_gohan_after.png` | after the lines: HUD back, NPCs gone, still on 8,1 |
| `scratch\capture\v12_vegeta_after-20261031-102000\shots\v12_vegeta_after.png` | the same run with presses to spare: he is on the world map |
| `scratch\capture\v12_gohan_strip-20261031-102049\shots\strip_01.png` to `strip_10.png` | one shot an A press, from the scene end |
| `scripts\one-time\2026-10-31-card-4-v12\c4y_plan_gohan.png`, `_piccolo.png`, `_vegeta.png` | the plan, one view a leader |

The strip shows the exit plainly: A on 8,1 gives the world map, A again lands him back on 8,1 with no card and
no scene, because the visited bit is set (C).

---

## Deliberate carry-overs

`c4y_plan.txt` lists these before its fault count, so none of them reads as a defect.

1. **The player's box is not clear** (C). It holds the two closed cells of the rock north of the landing,
   (272,120) and (280,120). The game itself puts him there. The test pins exactly those two cells.
2. **The player's feet sit at screen row 87** (C). The dialog box starts at screen row 88 (C, measured on a
   real frame), so the bottom 7 px of his 32 px frame go behind it. Every NPC keeps the v10 and v11 line of
   screen row 84, which gives up 4 px. The camera y clamp is 41, so no camera does better.
3. **BG2 decoration under four actors** (C): Tien (232,84) 14 px, Trunks (236,84) 14 px, Gohan (184,100) 32 px,
   Trunks (176,100) 56 px. v9 to v11 rejected any spot over BG2. v12 does not, because BG2 draws under an actor
   while BG1 draws over him, and the module's tests have only ever enforced the BG1 and collision rules. The
   strict rule leaves the trio nowhere to stand in this clearing (L, worked by hand over the clear-spot set).
4. **Touching frames** (C). Three sprites fill the top row exactly. The overlap rule bars a shared pixel, not a
   shared edge, and v10 and v11 both shipped touching frames.
5. **Flight paths cross canopy** (C). Every fly-in from y 260 and fly-off to y -40 passes behind BG1 trees, as
   in v11, whose worst column crossed 1658 canopy px against v12's 1454. Collision is not a flight rule: the
   v11 columns were blocked on 618 to 684 cells and played correctly.

---

## Tests

`test_chapter_cards.py`, 75 OK. The NPC rules are unchanged in screen terms. Three tests changed:

- **One is stricter.** `test_every_sprite_keeps_floor_between_itself_and_the_save_point` drops the Gohan-branch
  Tien carve-out and raises the worst margin from 0 px to 78 px.
- **Two give the player two named exceptions, and no one else anything.** `LAND` forces both, and both are
  pinned so they cannot grow. **Please confirm them.**
  - `test_no_actor_stands_on_the_save_point_or_south_of_the_text_box` now reads its limit as a screen row and
    converts it through the camera, so the NPC rule follows the camera. The player's feet move from screen row
    84 to 87. The test pins 87, pins it below the box top, and proves no camera improves it.
  - `test_every_spot_is_open_ground_and_the_player_can_walk_off` now compares the closed cells inside each box
    against an expected list. For every NPC that list is empty, which is the old rule. For the player it is the
    two rock cells.
- The walk-to-exit assertion in that same test now passes trivially, because `LAND` is inside the exit rect.

`REC0_HEX` changed by one push: the first-visit arm carries `1d0510020284208200`, the bytes the visited arm
carries. The `jz` span stays 14, because it covers the visited arm.

---

## Tools

All in `scripts\one-time\2026-10-31-card-4-v12\`, all on absolute paths: `c4y_lib.py` (the clear and flight
column rules on `scene\map_view.py`), `c4y_space.py` (the clear grid), `c4y_areas.py` (the components),
`c4y_view.py` (the view at a camera), `c4y_textbox.py` (the box top row), `c4y_plan.py` (every rule against the
module's own spots, 0 faults, plus the plan pictures).

> [!WARNING]
> The v9 helper `c4v_patch.py` can no longer be imported. It reaches the decompressor through the pre-move flat
> layout, which this morning's tool move ended. `c4y_lib.py` restates its rule on the permanent scene tools.
> The v10 and v11 card 4 tools import it, so they carry the same fault.

> [!NOTE]
> The plan pictures show scattered black 16x16 squares. They are a `map_view.py` artifact, not game content:
> the renderer skips a tile index past the end of the tile list and leaves palette index 0. The captures have
> none.

## Rule note

One Bash call in this task began with `cd <LOG root> 2>/dev/null;` before a `grep` that already used an
absolute path. That breaks the no-`cd` rule. The call was read only and changed nothing. Every other command
and every script used absolute paths.
