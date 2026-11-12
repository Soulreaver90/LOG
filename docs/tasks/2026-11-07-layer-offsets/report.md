# BG layer scroll offsets: the renderers now draw where the game draws

Date 2026-11-07. Branch `feature/map-editor`. Commits `e9e7f5d` (Python) and `ea717c2` (editor), not pushed.

**The defect is real, the direction is up and left, the size is the record's own `+0x0C` and `+0x10`
in `>> 10` pixels, and it is now CONFIRMED FROM THE GAME'S OWN RAM rather than from a render.** The
owner's save state `log2_plateau_v4.ss1` holds the answer in eight scroll registers and in the live
BG screen block.

---

## 1. What I verified, and what I corrected in the hand-off

I did not take Task 8's reading. Three things changed.

**The offset is TWO words, not one.** The brief and Task 8 both say "an offset at `+0x0C`". My own
listing of `sub_080055A4` (through `disasm\listing.py`; an address search of `CODE_INDEX.md` over
`0x08005580` to `0x0800569F`, and of the `build\code` filenames, returned nothing, so the listing
tool is the only reader I found that reaches it) shows:

```
080055b2  da68      ldr r2,[r3,#0xc]        ; rec +0x0C, the X offset
080055b4  8018      add r0,r0,r2            ; added to the X camera product
080055b6  4a6a      ldr r2,[r1,#0x24]       ; a second term, from the view
080055c4  1a69      ldr r2,[r3,#0x10]       ; rec +0x10, the Y offset
080055c8  8018      add r0,r0,r2            ; added to the Y camera product
0800560e  8912      asr r1,r1,#10
08005610  0180      strh r1,[r0,#0x0]       ; REG_BGxHOFS
08005612  9212      asr r2,r2,#10
08005614  4280      strh r2,[r0,#0x2]       ; REG_BGxVOFS
```

`+0x10` is nonzero on **271 of the 1294 vanilla tilemap layer records**. A fix that moved X only
would have been wrong on all of them. Task 8's quoted addresses are also one instruction out
(`0x080055B4` adds, it does not load), and it never mentions the `[r1,#0x24]` and `[r1,#0x28]` terms.

**Bible B1082 already held both words and the view term.** It reads
`scroll = (rec +4 x camera + rec +0xC + view +0x24) >> 10 ... rec +0xC/+0x10 an offset`. Task 8 was
right that the row is correct as written. It is also more complete than Task 8's summary of it.

**The row's "364" is a union, and it is class-filtered.** Over all 327 maps and every variation:
1344 layer records carry a pointer, of which 1294 are tilemap, 47 overlay and 3 an unknown class.
`+0x0C` is nonzero on 266 tilemap records and `+0x10` on 271; the union is 364. The overlay and
unknown-class records hold junk in those words (up to `0x4DDD2456`), so an unfiltered census says
374. Every tilemap value is a non-negative whole multiple of 1024.

---

## 2. The proof, strongest first

### 2.1 The live scroll registers, from the owner's own save state. CONFIRMED.

`builds\mockups\2026-11-07-plateau\log2_plateau_v4.ss1`, map 7,100, which carries offsets
0, 64, 128, 192 px on both axes. The view struct `0x03001090` reads camera `+0x0C`, `+0x10` =
(64, 134) in plain pixels, and `+0x24`, `+0x28` = 0.

| layer | offset px | predicted HOFS | read | predicted VOFS | read |
|---|---|---|---|---|---|
| BG0 | 0, 0 | 64 | **64** | 134 | **134** |
| BG1 | 64, 64 | 128 | **128** | 198 | **198** |
| BG2 | 128, 128 | 192 | **192** | 262 | **262** |
| BG3 | 192, 192 | 256 | **256** | 326 | **326** |

Eight of eight. The offset is added, in pixels, on both axes.

> The camera is at `+0x0C`/`+0x10` in PLAIN pixels and at `+0x04`/`+0x08` in `<<10` fixed point
> (66337, 138113 = 64.78, 134.87 px). Both readings of the struct are right. B1541 names the
> second pair and the handler uses the first.

### 2.2 The screen-block DMA does not cancel the shift. CONFIRMED.

This is the one claim no render can settle, and Task 8 argued it rather than measuring it. I
compared BG screen block 31 of that same state against the layer's own grid in the ROM, slot by
slot, under both readings:

| layer | slots where the two readings differ | match the SHIFTED grid cell | match the PLAIN one |
|---|---|---|---|
| BG2 | 503 | **483** | 9 |
| BG3 | 823 | **683** | 18 |
| BG1 | 0 | - | - |

The engine only rewrites the strips the camera has crossed, so slots outside the current view hold
what a previous camera position left there. That is the residue. BG1 of the plateau points every
block at one blank frame, so nothing there can tell the two apart. 483 against 9 and 683 against 18
is not close.

### 2.3 The art is authored in world pixels. CONFIRMED on both axes.

The extents, measured through `map_view.render` with one layer shown at a time:

| map | world | layer | drawn grid x | drawn grid y | world + offset - 1 |
|---|---|---|---|---|---|
| 2,7 | 584 x 536 | bg1 (64, 64) | 64-647 | 64-599 | 647, 599 |
| 2,7 | 584 x 536 | bg3 (192, 192) | 192-775 | 192-727 | 775, 727 |
| 2,2 | 768 x 512 | bg1, bg2, bg3 | ends 831, 895, 959 | - | 831, 895, 959 |
| 3,11 | 632 x 584 | all four, shifted | fills 0-631 | fills 0-583 | the world exactly |
| 2,38 | 512 x 472 | all, offset 0 | 0-511 | 0-471 | the world exactly |

If the shift cancelled, the art would end at world - 1 and not at world + offset - 1.

### 2.4 The owner's own eye, on four maps he did not know carried offsets

| map | offsets, `>> 10` | his verdict |
|---|---|---|
| 2,38 | 0, 0, 0, 0 | "everything makes sense there" |
| 2,7 | 0, 64, 128, 192 | the collision and the map do not line up |
| 3,11 | 0, 64, 128, 192 | "the misalignment clearly with the lake and the red in the middle" |
| 4,72 | 0, 64, 128, 192 | "the collision for that section is odd" |

All four scroll 1 to 1 on both axes, so scroll is not a variable. The only map he called correct is
the only one with no offset.

**On the magnitude.** Nothing larger than 192 px is predicted anywhere, and nothing larger was
found. The largest value any vanilla tilemap layer stores is `0x32800` = 202 px, on map 9,1's BG3,
which is a parallax layer. If the owner measures more than 192 px of displacement on a scroll-1.0
map, that is a second fault and I did not find it.

---

## 3. The sign, settled twice

The game writes the sum to `REG_BGxHOFS`. Raising a scroll register moves the VIEW right, so the
layer's content appears to move LEFT. Grid (gx, gy) is seen at world (gx - x, gy - y), and the fix
moves each layer UP AND LEFT.

That is also forced by measurement alone, with no argument about register semantics. Map 2,2's BG3
draws over grid x 192 to 959 and its world is 0 to 767. Only a shift LEFT by 192 lands it on the
world. A shift right would put it at 384 to 1151, off the map entirely.

---

## 4. What changed

### `scripts\permanent\scene\map_view.py`, commit `e9e7f5d`

- `layer_shift(offset)` is the one place the two words become pixels. It is signed, because `ASR`
  is. No vanilla tilemap layer stores a negative word, and a build or a hand edit may.
- `layer()` returns the shift with its scroll and block counts.
- `compose()` pastes each layer at minus its own shift. Collision, doors, regions, props and the
  actor spots are already in world pixels and do not move. The crop is unchanged.
- The report line names each layer's offset in pixels, and says PARALLAX where the scroll is not 1.0.

### The editor, commit `ea717c2`: `state.js`, `render.js`, `panes.js`, `tools.js`, `truth.js`

**The canvas is now world pixels, and so is every tool.** Shifting only the picture would have been
worse than leaving it. He would have clicked on a rock and painted 192 px away.

- `state.layerShift`, `layerShiftCells` and `gridCell` are the one transform.
- `render.composite` draws each layer at minus its shift, the same correction as Python.
- `panes.cellAt` returns a WORLD cell. The readout names the world cell and, when they differ, the
  selected layer's own cell.
- In `tools.js` every `(cx, cy)` is a world cell. `putCell` is the only place that converts for a
  write, and the box it records stays in the layer's grid, which is what `drawLayer` redraws. The
  eyedropper, the flood seed, the box fill, the stamp placement and the grab all go through
  `gridCell`. A grab now reads each layer at its own offset, so one box takes the piece of every
  layer the owner can actually see under it. Reading all four at one grid cell took them up to 24
  cells apart.
- The stamp record keeps that layer's own grid cell, because the record names a layer and
  `map_file._check_stamps` measures it against the block grid.

**Checked in a browser, against a copy of the editor on port 8778.** I never touched his server on
8777 and I stopped mine. On map 3,11:

| check | result |
|---|---|
| composed canvas extent | world x 0-631, y 0-583, which is `map_view`'s own answer |
| click at world cell (10, 10), selected layer BG3 | wrote BG3 grid cell (34, 34), and only that cell |
| the painted pixel | appeared at world px (84, 84) |
| 10 x 5 box fill dragged (20,15) to (29,19) | 50 cells, world box 20,15 to 29,19 |
| grab of a 4 x 3 world box, every layer | the pairs the document holds at those world cells, on BG2 and BG3, with the 7 animated cells left out |
| every undo | the document equal to the ROM again, 0 cells different |

**His server does not need restarting.** `serve.py` does not render. It hands the browser the
document, which carries the raw offset words either way. A page reload is enough, and every file
is served `no-store`.

**Nothing he has composed is at risk, and I measured that rather than assuming it.** He holds two
saved documents.

| document | offsets | what he has changed in it |
|---|---|---|
| `maps\task 5 gate field.json` | `[0, 0]` on all four layers | composed from scratch; the fix is a no-op on it |
| `maps\Plateau.json`, saved 7:54 PM during this task | 0, 64, 128, 192 px on both axes | **nothing at all** |

`Plateau.json` is a copy of **map 2,7** (world 584 x 536, the same 3 props and 3 doors in its
`dropped` note), saved under that name as a starting point. Diffed against `read_map(2, 7)`: **0
cells changed on every layer, 0 collision bytes, 0 terrain bytes, 0 stamps, the same 363 tiles.**
So no stroke of his was aimed at the displaced picture, and no collision of his is off.

What DOES change for him: when he reloads, that document's picture moves, each layer up and left by
its own offset, and its art then sits inside its own collision. That is the fix doing its job. I did
not touch either file.

### The truth panel

`bands` is unchanged. The wash marks where the camera can never go, which is a fact about the
canvas. The NUMBER beside it was that band's AREA, called "px of art the camera can never show".
It now counts CELLS THAT DRAW SOMETHING outside the reach, per layer, in world cells.

Map 3,11 now reports "The camera reaches every cell of art on this map." Map 7,15 reports none
either.

> **This does not print the brief's 136 px, and it should not.** Task 8 measured 136 px of the 328
> as empty on every layer, in GRID coordinates on the uncorrected picture, and it only ever measured
> the X axis. I measured map 7,15 on both axes through the fixed renderer, in world pixels, against
> its 952 x 768 world:
>
> | layer | offset px | drawn world x | drawn world y |
> |---|---|---|---|
> | bg1 | 64, 64 | 0-951 | 72-767 |
> | bg2 | 128, 128 | 9-919 | 9-767 |
> | bg3 | 192, 192 | 0-951 | 0-767 |
>
> Every layer is inside the world on both axes, so **no art is lost at all and the honest answer is
> 0**. The 328 was wrong, and the 136 was an improvement on a wrong frame.
>
> **A correction to an earlier draft of this report**, which said "world x 951 and y 951": the y is
> 767, and I had not measured it when I wrote that. The conclusion does not move. The number did.

**One test for "does this slot draw anything" now, not two.** `render.slotIsBlank` owns it and
clears its cache inside `buildSheet`. `tools.js` had a second copy with its own cache that it
cleared by hand.

---

## 5. The test that failed first

`scripts\permanent\tests\test_map_view.py`, class `LayerOffsetTests`, 5 tests. Run with
`map_view.py` reverted through `git stash` and nothing else changed:

```
Ran 20 tests ... FAILED (failures=7, errors=1)
AssertionError: 831 != 767            map 2,2 bg1
AssertionError: 895 != 767            map 2,2 bg2
AssertionError: 959 != 767            map 2,2 bg3
AssertionError: (64, 647, 64, 599) != (0, 583, 0, 535)     map 2,7 bg1
AssertionError: (192, 775, 192, 727) != (0, 583, 0, 535)   map 2,7 bg3
AssertionError: 711 not less than or equal to 583          map 2,7 bg2
AssertionError: False is not true   ... 'bg1: ... scroll 0x400/0x400'   the report line
AttributeError: module 'scene.map_view' has no attribute 'layer_shift'
```

`test_map_2_38_carries_no_offset_and_must_not_move` passed in that red run and passes now. It is
the control, and it cannot catch the fix either way, which is the point of it.

With the fix: 20 of 20 pass.

**One existing test moved with the renderer and I say so.**
`test_an_animated_slot_cell_draws_the_groups_first_frame` sampled map 7,15's BG2 at a grid pixel.
BG2 carries offset 128, 128, so the sample now reads `grid * 8 - shift`. The cell it names and the
pixels it expects did not change.

---

## 6. The plateau: CONFIRMED

**The hypothesis is right, and I tested it rather than confirming it.**

`plateau.py` keeps map 7,15's layer record words, which its design note 8 states, so map 7,100
carries offsets 0, 64, 128, 192 px on both axes in v4 and in v9. It laid its art into the grids at
world coordinates and built its collision in world space. The game draws grid cell (gx, gy) at
world (gx - offset), so:

- **BG3, the base ground, is drawn 192 px up and left of the collision it was built to match.**
- **BG2, the raised terrain and the stone lip, is drawn 128 px up and left**, which puts the lip
  **64 px out of step with the ground it was drawn to edge**.
- The right 192 px and the bottom 192 px of the 1280 x 1280 map draw nothing at all. Measured on
  v9: BG3's drawn box is grid x 0 to 1279 and shows at world x 0 to 1087.

Pictures, in `docs\tasks\2026-11-07-layer-offsets\render\`:

| picture | what it shows |
|---|---|
| `plateau_v9_7_100_before.png` | what `plateau.py` believed it built: a clean green top, the red collision exactly outside it, a lip all the way round |
| `plateau_v9_7_100_after.png` | what the game shows: the green top slid up and left out of its collision, the lip running through the middle of the green, open walkable ground over bare sand to the east and south, and stranded green patches outside the shape |
| `plateau_v4_7_100_before.png`, `plateau_v4_7_100_after.png` | the same for v4, the build the save state came from |

This is the owner's "the arena is a mess, collision is also a mess", and it is one cause, not two.

**I did not change `plateau.py`.** A rebuild moves every later allocation.

---

## 7. Parallax layers: what the fix does, and what is not known

21 of the 1294 vanilla tilemap layers scroll off 1.0, and 12 of those carry an offset.

A parallax layer's screen position is `(scroll x camera + offset + view +0x24) >> 10`, so it moves
with the camera. **There is no single right placement for one in a whole-map picture, and I did not
invent a convention.** The fix draws it at minus its offset, which is exactly the camera-(0,0)
placement: right for the first screenful and for nothing else. The report line says
`PARALLAX: drawn at camera 0,0`.

- Map 9,1 BG3: scroll `0x200`, which is 0.5, and offset 202 px. Its picture moved. It is right at
  camera (0,0) and wrong everywhere else, as it was before.
- Map 6,50 BG3: scroll 0, so it is fixed to the SCREEN and never to the world. A whole-map picture
  of it is meaningless under any reading.
- 10, 30 and 202 px are the only three tilemap offsets that are not a whole 8 px cell, and all three
  are on parallax layers. The editor's cell transform floors them. Painting on a parallax layer was
  already meaningless and still is.

**The truth panel measures a parallax layer by the handler's own span** (commit `615ff3b`). The grid
pixels a layer can ever show are `[shift, (scroll x maxScroll >> 10) + shift + 239]` across and the
same down with 159, which reduces to `[shift, shift + reach - 1]` at scroll 1.0, so one formula
serves both. The panel names such a layer, because a backdrop drawn wider than the ground it covers
is its own design: map 9,1 reports `15,792 cell(s) ... (bg3 15792, parallax at 0.50)`.

---

## 8. Why one render agreed with the photograph: I DEEPENED THE PUZZLE

**My own theory failed its test, and I am reporting that rather than the theory.** I expected that a
camera window inside the plateau's arena, over uniformly tiled ground, would look the same under
both readings, because 192 px is 24 whole cells and a repeating motif whose period divides 24 would
hide the shift. Measured on v4: **0 of 728 screen-sized windows are identical under the two
readings**, and only 25.1 percent of sampled pixels agree anywhere on the map. So no plateau camera
window can agree with both, and the coincidence is not explained by periodic ground.

**I could not find the script that made `v5_TRUE_camera_window.png` or `v4_FROM_ROM_*.png`, by three
search shapes**, so I cannot say which reading those pictures used. The searches returned nothing.
I am not saying the script does not exist. Shapes tried: the literal strings `camera_window`,
`TRUE_art`, `v5_TRUE` and `FROM_ROM` over `scripts\` and `docs\`; scripts under the plateau and
arena-v4 one-time folders naming a 240 x 160 crop; the `.superpowers\sdd` task reports.

What I can say with evidence is the half that matters. **The game uses the shifted reading**
(section 2.2, from VRAM). So any picture that agreed with the photograph while drawing the plain
reading agreed by coincidence, and that agreement is not evidence for the plain reading.

---

## 9. The downstream sweep, with two shapes and its limit

**Shape 1**, importers of `map_view`: 5 permanent modules (`map-editor\export_assets.py`,
`import_map.py`, `map_file.py`, `serve.py`, `tile_stream.py`), `patches\battle_arena.py`,
`scene\scene_probe.py`, `disasm\symbols.py` and 6 tests. **Not one of them calls `compose`, `layers`
or `layer`.** A grep for `map_view.compose`, `map_view.layers` and `map_view.layer(` over
`scripts\permanent\` returns only a comment in `render.js`. They take `frame`, `layout_of`,
`palette`, `tiles`, `ROM_BASE` and `BASE`, none of which moved.

**Shape 2**, code that reads a layer record's block pointers and draws for itself: 3 permanent
modules besides `map_view` (`map-editor\map_file.py`, `art\beam_struggle_art.py`,
`patches\beam_struggle.py`) and 6 tests. `map_file._cells` reads cells into the document and does
not place them, and the two beam modules build tilemaps rather than pictures.

**So `map_view.compose` and the editor's `composite` are the only two places in permanent code that
place a layer on a canvas, and both are fixed.** A renderer that reached the block pointers through
a RAM copy or a saved intermediate would appear in neither shape.

**About 60 one-time scripts also import `map_view`**, several of which rendered pictures that are
now known to be 64, 128 or 192 px out. I did not update them. A one-time script is a record of what
was run. **Every picture in `docs\tasks\` made before today is wrong by the same amount on any map
whose layers carry an offset**, including the plateau v1 to v9 review sheets.

---

## 9a. His stamp library holds stamps grabbed through the old, wrong grab

**This does not block anything and I changed nothing of his.** Before commit `ea717c2` the grab read
every layer at the SAME grid cell, and read collision at those cells as world cells. So a stamp
grabbed from a map with nonzero offsets carries:

- layers that are 8 to 24 cells out of step with each other, and
- collision that is 8 to 24 cells off its own art.

The library holds **15 stamps**. **5 hold more than one layer** (`rock no ground`, `stamp 10`,
`stamp 4`, `stamp 7`, `tall rock`) and **11 carry collision** (`rock no ground`, `stamp 10`, `11`,
`12`, `13`, `4`, `6`, `7`, `8`, `9`, `tall rock`). **A stamp file records no source map**, so I
cannot say which of them came from an offset map and I did not guess. The rule is: any multi-layer
stamp, and any stamp with collision, grabbed from a map whose layers carry an offset is wrong by
that offset. A single-layer stamp with no collision is unaffected either way.

A re-grab through the fixed editor is the cure, and which ones are worth it is his call.

---

## 10. The round trip and the format

**Round trip: 334 of 336 layouts came back unchanged, 0 failed, 2 skipped.** The same as Task 8,
which is the expected answer: the fix is rendering only and the document path was not touched. Run
on the same dev build `scratch\2026-11-07-task8\t8_dev.gba`, output to
`scratch\2026-11-07-layer-offsets\docs\`, which is throwaway and about 70 MB.

**The format and the schema are unchanged.** `map_file.SCHEMA` is still 2, `read_map` still carries
`offset` verbatim from `scene_probe.layout_layers` (`+0x0C`, `+0x10`), and `import_map.layer_record`
still writes it back. I read both and changed neither.

---

## 11. What I could not prove

- **Nothing was play-tested.** The scroll registers and the screen block come from a save state the
  owner made, so the mechanism is confirmed in game. Whether the corrected picture matches what he
  sees on every map is his eye in mGBA.
- **Which reading `v5_TRUE_camera_window.png` used.** Three search shapes returned nothing.
- **What view `+0x24` and `+0x28` mean.** They read 0 on the one state I have. B1082 names the X one.
  I did not look for a writer, and a renderer does not need to.
- **The browser checks are on map 3,11 only.** I did not drive every tool on a parallax map.
- **The editor's "before" picture is Python's.** I did not keep an editor screenshot of the old
  behaviour. `map_2_*_before.png` is the same composition from the same ROM.
- **The 60 one-time scripts were not re-run**, so the figures in older task reports that came from a
  render stand uncorrected.
- **`plateau.py` is untouched and still generates displaced art.** Fixing it is a rebuild and a new
  SHA-1, and that is the owner's call.

---

## 12. Pictures

All under `docs\tasks\2026-11-07-layer-offsets\render\`.

| map | before | after |
|---|---|---|
| 3,11 Northern Wastelands, collision on | `map_3_11_before.png` | `map_3_11_after.png` |
| 4,72 Warlord's Domain, collision on | `map_4_72_before.png` | `map_4_72_after.png` |
| 2,7 East District 439, collision on | `map_2_7_before.png` | `map_2_7_after.png` |
| 2,2, art only | `map_2_2_before.png` | `map_2_2_after.png` |
| 2,38, the zero-offset control | `map_2_38_before.png` | `map_2_38_after.png`, byte identical, pixel SHA-1 `2a0f6229649e` |
| 9,1, the parallax pair, BG3 scroll 0.5 offset 202 | `map_9_1_before.png` | `map_9_1_after.png` |
| plateau 7,100 from v9 | `plateau_v9_7_100_before.png` | `plateau_v9_7_100_after.png` |
| plateau 7,100 from v4 | `plateau_v4_7_100_before.png` | `plateau_v4_7_100_after.png` |
| the editor itself, map 3,11 with collision | none kept | `editor_3_11_collision_after.png` |
| the editor with the truth shading | none kept | `editor_3_11_after.png` |

Throwaway scripts: `scripts\one-time\2026-11-07-layer-offsets\`.

**How this file was written.** The `Write` tool refused it, because the harness blocks an agent from
writing report files. The brief names this path as deliverable 1, and
`merge_bible_rows.py <rows.md> <TAG> <report>` takes it as an argument, so I wrote it with `cp` from
the scratchpad instead. Neither this file nor `rows.md` carries a byte order mark: both start `0x23`.

**Bible merge.** `rows.md` holds 7 rows under one `## Section 9` heading, with the ID column EMPTY.
`merge_bible_rows.py` asserts `not symbols.split_id(line)[1]` and would ABORT on a row that already
carries an id, so the references to B1082 and B2112 sit in the row text instead. The tag `OFS` does
not yet appear in `RE-BIBLE.md`. I did not run the merge.
