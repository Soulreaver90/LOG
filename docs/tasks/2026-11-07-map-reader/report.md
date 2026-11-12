# Section 9 map reader: build report

Agent build, 2026-11-07. The agent could not write this file itself, so its report is saved below.
Everything under "My verification" is mine. Treat the agent's text as unverified except where I say so.

## The arena verdict, which was the point of the exercise

**Map 6,100 in `log2_poc_r41_arena_v7.gba` has 0 doors in BOTH carriers.** No live finding in approved
work. Full listings in `scripts\one-time\2026-11-07-map-reader\`.

```
  ENTRY FIELDS  rom:0x940614, index 327, 56 bytes
    +0x00 zone 6   +0x01 area 100   +0x02 variations 1   +0x03 region count 0   +0x04 item count 2
    +0x08 combat 1   +0x0C banner index 221   +0x24 music song id 38
  LAYOUT CHAIN  entry +0x2C -> array rom:0x93BE88, 1 variation(s); var 1: layout rom:0x93BDBC
  DOOR CARRIER A, the REGION list (entry +0x10): 0 region(s), 0 of them door(s)
  DOOR CARRIER B, the LAYOUT door list (+0x40 count, +0x44 list): +0x40 says 0, 0 decoded, list 0x0
  ITEM list: item 0 npc set 28 at (288,392); item 1 group enemy type 60 set 28 at (244,504)
  PROPS: 3    COLLISION: frame rom:0x93B650, type 1, 4399 of 8192 open inside bounds 512x1024
  DOORS IN ALL: 0  (0 region, 0 layout, 0 item)
```

It went past the brief, correctly: a door count is only a floor. The arena's variation, enter and leave
script words are all 0, and its one script, the enemy death table `rom:0x940744`, decodes in full to one
record plus 26 END entries with **no `ext 35`, `38` or `39`** in it. So the arena has no exit by door and
none by script. The build's own map 6,1 matches the base ROM's listing line for line except its entry
address, so the parent map was not touched.

Map 6,1 in the base ROM, for contrast: 6 regions, 2 of them doors, plus a layout door list of 3, to 4,6
and 6,21 and 6,2. **DOORS IN ALL: 5.**

## A third defect it found in map_view, which the brief did not know about

The brief named two defects. There were three.

**`map_view.py` read the layer `+4`/`+8` SCROLL FACTOR as a width and height**, so every map was cropped
or padded to 1024x1024. Map 9,1 is really 1536x1280 and lost its right-edge region at x 1217-1264
entirely. Map 6,1 is really 512x1024 and gained 512 px of black. The collision count ran over 16384 cells
for a map that holds 8192. It rendered both maps and checked them by eye before and after.

The two known defects are fixed too: a region is now a DOOR only if its factory says so, the layout door
list is drawn beside it, and props are drawn.

## What it changed

- **`scene\scene_probe.py`** is the section 9 reader: new `layouts`, `layout_doors`, `layout_props`,
  `layout_layers`, `map_bounds`, `collision_bits`, `is_open`, `collision`, and a rewritten `show_map`
  with `--var`. Declared counts print beside decoded counts, so a disagreement shows.
- **Reuse, not copies:** `map_view`, `map_index` and `warp_graph` now call `scene_probe.layouts`;
  `warp_graph` calls `scene_probe.layout_doors`; `map_view` uses `collision_bits` and `is_open`.
  `scene_probe` imports `rom\webfoot_decompress` lazily, inside the collision reader, so it took no new
  hard dependency on the package the other agent owned that hour.
- New `tests\test_scene_probe.py` (28) and `tests\test_map_view.py` (12). Neither existed before.
- `TOOL_INDEX_NOTE` rewritten in all three tools; `docs\tool-index.md` regenerated.

## Three findings beyond the brief

1. **Map entry `+0x0C` is a name index in 313 maps and a SCRIPT in 14.** This confirms the OVW row's
   "name text id or script" from L to C and counts it. **It corrects one of my own OPS rows from last
   night**, which said "Never a pointer: `+0x08` combat and `+0x0C` banner"; that row's own generated
   page counted 14 pointers, so its prose contradicted its table. It also closes the LAB row's open
   question: map 9,1's banner read as "index 64" because 64 is the low byte of the pointer `0x08403E40`.
2. **Map bounds come from the block grid of the scroll-1.0 layers.** Measured on all 327: 313 have every
   open collision cell inside that bound and none outside. The other 14 are the 12 with an all-open frame
   plus 1,7 and 6,99, which have no scroll-1.0 layer.
3. **The `+0x14` item list is not a third door carrier.** Walked item by item on both ROMs: 1108 items in
   the base, 1117 in v7, zero warps.

## Tests, real exit codes, no pipes

`test_scene_probe` 28 OK, `test_map_view` 12 OK, `test_scene_lib` 40 OK, `test_battle_arena` 61 OK,
`test_make_tool_index` 6 OK, `test_battle_start` 38 with the 1 known RED
(`test_form_survives_the_leader_change` at `rom:0x89A9C0`, in `fullpower_ssj`, which it never touched).
It did not run the full suite.

The reader is proved on the population, not on examples: one test opens `show_map` on all 327 base maps
and all 336 variations, another on all 328 entries of v7, and a third reconciles 283 + 44 = 327 layouts
and 586 + 69 = 655 doors against the WRP and OPS rows.

## It hit the citation problem independently

Unprompted, and while I was writing it up from the other direction: "the bible SHIFTED under me during
this task, by 4 to 9 lines, while another agent merged rows. Every citation I first wrote as a line number
was wrong within the hour. I converted all 49 of them in the code, the tests and `rows.md` to tag
citations. I suggest the project stop citing bible line numbers entirely."

That is independent corroboration of this morning's finding, from an agent that had not read it. The
owner approved the stable id fix at 9:30 AM and it is in flight.

## What it could not prove, in its own words

- **That the block-grid bound IS the engine's world extent.** What is confirmed is containment on 313 of
  313. It did not read the camera clamp at map view `+0x5C`/`+0x5E`, so a map whose engine extent is
  smaller than its art would not show in the measurement. Its row is labelled C for containment, L for
  equality.
- **That a drawn prop appears on screen.** The EFX row says props start hidden until a script shows them.
  A magenta box proves a layout entry exists, nothing more.
- **The item-list warp path in the reader is untested**, because no map in either ROM takes it. It is a
  guard, not a tested branch.
- Map 6,99, the world map, carries two BG layer classes nobody here decodes (`0x08012841`, `0x08012705`).
  The reader names them "unknown class" and prints their words raw rather than guessing.
- It did not regenerate `docs\research\warp-graph.md` or `map-index.md`, to avoid churn while another
  agent worked. Both still read correctly.

## My verification

I ran the new reader myself on the two maps whose bounds the width defect would have broken:

```
map 9,1: 8278 of 30720 open inside the map bounds 1536x1280 px
map 6,1: 4422 of 8192 open inside the map bounds 512x1024 px
         DOORS IN ALL: 5  (2 region, 3 layout, 0 item)
```

Both match its report. The arithmetic is self-consistent: 512x1024 px at 8 px cells is 64 x 128 = 8192
cells, and the old 1024x1024 cap would have counted 16384 for the same map. So the defect was real and
map 9,1 lost its right edge in every picture we have looked at until today.

Bible rows wait in `rows.md`, tag `MAP9`. I have NOT merged them yet: the stable id pass is rewriting the
bible, and merging into a file being rewritten is how we would lose rows.

Full suite: not run yet, for the same reason.
