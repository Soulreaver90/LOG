# LOG Map Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended)
> or superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Give the owner a local page where he composes a GBA map by eye, and a path that turns what he
composed into a map the game loads.

**Architecture:** Python owns the ROM. It exports the tiles and palettes once, and it turns a saved map
file back into a real map entry. The browser owns only composition, and talks to nothing but a tiny local
server that serves files. The map file is the contract between them, and it is the only thing either side
has to agree on.

**Tech Stack:** Python 3.14 with Pillow, already used by every tool here. Plain HTML, CSS and JavaScript
with no framework and no build step. `unittest`, the project's suite.

**Spec:** `docs\design\2026-11-07-map-editor-design.md`

## Global Constraints

- Run Python as `py -3.14 -P`. `py -3` is 3.15 and has no Pillow.
- Never write under `data\`. Never overwrite a ROM, a save or a state: check absence, then create.
- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Everything lives in `scripts\permanent\map-editor\`. Tests in `scripts\permanent\tests\`.
- Nothing is ever published to claude.ai. This is a local page opened from disk.
- **A map loads at most 896 tiles.** Loader `@0x080050C8` decodes the `+0x48` list into a `0x700` byte
  buffer.
- **The camera pair is `+0x08 = world_w - 239` and `+0x0A = world_h - 159`.** Always computed, never
  inherited.
- **The world size is NOT the block grid.** Measured over all 336 vanilla layouts: the grid equals the
  implied world on 17 and merely covers it on 334. Map 7,15 stores 713 on a 1280 grid, world 952. The
  document therefore carries `world: [w_px, h_px]`, `camera_pair` computes from `world`, `read_map`
  takes `world` from the map's own `+0x08`/`+0x0A`, and `validate` enforces `blocks * 256 >= world`.
  Computing the pair from the grid would rewrite 319 vanilla cameras and fail Task 8 on its first map.
- **Every BG layer of a map carries the same block grid.** A block is 32 x 32 tile entries. Padding a
  layer to one shared grid is lossless: pad then trim recovered the original grid on 1294 of 1294
  vanilla tilemap layers.
- **Layout bytes `+0x04` to `+0x07` are the BG0 to BG3 priorities**, added to the `BGxCNT` table at
  `0x081DA8EC` whose row 0 is `0x1C80`/`0x1D80`/`0x1E80`/`0x1F80` with all priority bits zero. Map 7,15
  reads `[3,1,3,3]`, so its BG1 is the canopy drawn over the player. Priority is read from the map, never
  defaulted.
- A tile entry is u16: tile `0x3FF`, `0x400` flip x, `0x800` flip y, `0xF000` palette. **The palette bits
  are unused in this game.** Tiles are 8bpp, 64 bytes each, and all draw through one shared 256-colour BG
  palette, so the editor needs no palette picker and the manifest carries exactly one palette. Flips are
  a runtime transform of the atlas cell.
- **Colour index 0 is transparent**, carried in the manifest as `transparent_index`. A reader that
  decodes the atlas PNG to raw indices, or ignores its `tRNS` marker, draws black where the game draws
  nothing.
- The editor does not set music or the map name. Scenery is tiles, not the layout prop list.
- Code style: `C:\Users\josephgonzalez\.claude\CODE-STYLE.md`. No em or en dashes anywhere.
- Suite: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`.
  Never pipe a test run into `tail` or `head`.

## Review Focus

Failure modes the spec implies that no task's happy path exercises. Each line names the task that owns
the test.

1. **A map over the 896 tile budget** must fail closed with the count and the limit, never emit a file
   that produces a ROM the game cannot load. Task 3.
2. **A camera pair inherited instead of computed** is the exact plateau fault. Import must recompute it
   and must reject a file that carries a pair disagreeing with its own size. Task 7.
3. **Layers disagreeing on the block grid** is the other half of the plateau fault. The file format must
   make it unrepresentable, and import must still check. Tasks 3 and 7.
4. **A map file written by an older schema** must refuse to load rather than load wrong. Task 3.
5. **Appending past the map table's one-byte count** (`rom:0xE0AE`, cap `0xFF + 0xFE`) must fail closed.
   Task 7.

---

### Task 1: Prove a mixed tile stream, and own the codec

Settles the spec's one demonstration gap before anything is built on it.

**Files:**
- Create: `scripts\permanent\map-editor\tile_stream.py`
- Create: `scripts\permanent\tests\test_tile_stream.py`
- Read only: `scripts\permanent\scene\map_view.py` (`tiles`, `palette`, `layout_of`)

**Interfaces:**
- Produces: `decode_stream(rom: bytes, layout: int) -> list[tuple[int, int]]` returning `(chunk, tile)`
  pairs in load order; `encode_stream(pairs: list[tuple[int, int]]) -> bytes` returning the `+0x48` frame
  payload; `TILE_BUDGET = 896`.

- [ ] **Step 1: Write the failing round-trip test**

```python
def test_decode_then_encode_reproduces_every_vanilla_stream(self):
    # for each of maps 14,1 / 7,15 / 4,50: encode(decode(x)) == the ROM's own payload
def test_decode_matches_map_view_tile_count(self):
    # len(decode_stream(...)) == len(map_view.tiles(rom, layout)) on the same three maps
def test_encode_refuses_more_than_the_budget(self):
    # encode_stream of 897 pairs raises ValueError naming 897 and 896
```

- [ ] **Step 2: Run it and watch it fail**

Run: `py -3.14 -P -m unittest tests.test_tile_stream -v`
Expected: FAIL, no module named `tile_stream`.

- [ ] **Step 3: Implement `decode_stream` and `encode_stream` in `tile_stream.py`**

The list is delta coded as `e[i] += e[i-1] + 1`; the high byte is the chunk index into the layout `+0x4C`
table at `0x084DF574`, the low byte the 64-byte tile inside that chunk. Entry count is the frame header
size divided by 2. Bible `B1080` and `B1098`.

- [ ] **Step 4: Run it and watch it pass**

- [ ] **Step 5: Write the mixing proof as a one-time script**

Create `scripts\one-time\2026-11-07-map-editor\01_mixed_stream.py`. Build a stream whose pairs come from
two different maps' chunks, render a small tilemap through `map_view`, and save a PNG beside the script.
Print the chunk indices used and the total tile count.

- [ ] **Step 6: Look at the PNG**

Both sources must appear, correct, in one image. **If they do not, stop and report**: the spec's fallback
is one source per map, and that changes Tasks 2 and 5.

- [ ] **Step 7: Commit**

```bash
git add scripts/permanent/map-editor/tile_stream.py scripts/permanent/tests/test_tile_stream.py scripts/one-time/2026-11-07-map-editor/
git commit -m "Add the BG tile stream codec and prove mixing"
```

---

### Task 2: Export the tiles and palettes the editor loads

**Files:**
- Create: `scripts\permanent\map-editor\export_assets.py`
- Create: `scripts\permanent\tests\test_export_assets.py`

**Interfaces:**
- Consumes: Task 1's `decode_stream`.
- Produces: `export(rom: bytes, out_dir: Path) -> dict` writing `chunks\<n>.png` (one atlas per chunk, 16
  tiles across), `palettes.png`, and `assets.json` with `{"chunks": [{"index", "tiles", "png"}],
  "palettes": [[rgb, ...]], "tile_budget": 896}`. Returns the same dict it wrote.

- [ ] **Step 1: Write the failing test**

```python
def test_export_writes_one_atlas_per_chunk_that_holds_tiles(self):
def test_assets_json_tile_counts_match_the_atlas_pixel_sizes(self):
def test_export_refuses_to_write_into_a_non_empty_directory(self):
```

- [ ] **Step 2: Run it and watch it fail**
- [ ] **Step 3: Implement `export` in `export_assets.py`**

Reuse `map_view.palette` for the colours. Write to a directory the caller names, defaulting to
`scripts\permanent\map-editor\assets\`, and create exclusively.

- [ ] **Step 4: Run it and watch it pass**
- [ ] **Step 5: Run the real export and open two atlases**

They must look like game tiles, not noise.

- [ ] **Step 6: Commit**

---

### Task 3: The map file, and every rule it enforces

The contract between the browser and the ROM. Owns Review Focus items 1, 3 and 4.

**Files:**
- Create: `scripts\permanent\map-editor\map_file.py`
- Create: `scripts\permanent\tests\test_map_file.py`

**Interfaces:**
- Produces: `SCHEMA = 1`; `save(doc: dict, path: Path) -> None`; `load(path: Path) -> dict`;
  `validate(doc: dict) -> list[str]` returning human readable problems, empty when valid;
  `camera_pair(width_px: int, height_px: int) -> tuple[int, int]`;
  `tile_count(doc: dict) -> int`;
  `read_map(rom: bytes, zone: int, area: int, var: int = 1) -> dict` turning any map in the ROM into a
  document, which is how the owner starts from a built-in map. The ROM is never modified.
- Document shape: `{"schema", "blocks": [bw, bh], "layers": {name: {"priority", "cells": [...]}},
  "collision": [...], "stamps": [...], "tiles": [[chunk, tile], ...]}`. One `blocks` pair for the whole
  document, which is what makes a layer grid mismatch unrepresentable.

- [ ] **Step 1: Write the failing tests**

```python
def test_camera_pair_is_width_minus_239_and_height_minus_159(self):
    self.assertEqual(camera_pair(1024, 1024), (785, 865))
def test_validate_rejects_more_than_896_tiles(self):
    # the message names both the count and 896
def test_validate_rejects_a_layer_whose_cell_count_is_not_the_block_grid(self):
def test_load_refuses_a_document_from_another_schema(self):
    # schema 2 raises, and the message says which schema it found
def test_every_layer_carries_a_priority(self):
def test_read_map_of_7_15_validates_and_reports_its_real_tile_count(self):
    # validate() returns [] and tile_count() equals len(decode_stream(...)) for that layout
def test_read_map_never_modifies_the_rom(self):
```

- [ ] **Step 2: Run them and watch them fail**
- [ ] **Step 3: Implement `map_file.py`**
- [ ] **Step 4: Run them and watch them pass**
- [ ] **Step 5: Commit**

---

### Task 4: Serve the page, and the three panes

**Files:**
- Create: `scripts\permanent\map-editor\serve.py`
- Create: `scripts\permanent\map-editor\index.html`
- Create: `scripts\permanent\map-editor\editor\state.js`, `render.js`, `panes.js`, `style.css`

**Interfaces:**
- Consumes: Task 2's `assets.json` and atlases, Task 3's document shape.
- Produces: a page that loads `assets.json`, draws a map document to a canvas, and shows the tile palette
  on the left, the map in the middle, layers and the live tile count on the right.

- [ ] **Step 1: Implement `serve.py`**

`http.server` bound to localhost on a fixed port, serving this directory only. Print the URL.

- [ ] **Step 2: Implement the page and the three panes**

Layout A from the owner's mockup. The right pane shows the layer list, the block grid, and the tile count
as `n / 896`.

- [ ] **Step 3: Implement "new blank" and "open a game map"**

Opening a game map calls Task 3's `read_map` through the server and loads the result as a document. It is
always a copy; the ROM is never touched. This is the owner's "choose from build in maps".

- [ ] **Step 4: Open it and look**

The palette must show real tiles, and opening map 7,15 must draw a map that looks like the game's.

- [ ] **Step 5: Commit**

---

### Task 5: The four tools and undo

**Files:**
- Create: `scripts\permanent\map-editor\editor\tools.js`, `history.js`
- Modify: `editor\panes.js`

**Interfaces:**
- Produces: tools `fill`, `stamp`, `tile`, `grab`; `history.push(before, after)`, `history.undo()`,
  `history.redo()`; a stamp is `{name, w, h, cells}` saved into the document's `stamps`.

- [ ] **Step 1: Implement fill and the single tile brush**
- [ ] **Step 2: Implement grab**

Drag a box on the canvas, name it, and it becomes a stamp in the palette. Grab is the asset pipeline: it
is what removes the need for a library before the first map.

- [ ] **Step 3: Implement stamp placement**
- [ ] **Step 4: Implement right click to paint collision**

Collision is its own grid and is never derived from the art.

- [ ] **Step 5: Implement undo and redo with a deep history**
- [ ] **Step 6: Compose a small test map by hand and save it**
- [ ] **Step 7: Commit**

---

### Task 6: The play-scale truth panel

The feature that exists because a correct-looking render hid a real fault for a whole morning.

**Files:**
- Create: `scripts\permanent\map-editor\editor\truth.js`
- Modify: `editor\panes.js`

**Interfaces:**
- Consumes: Task 3's `camera_pair`, reimplemented in JS and pinned to the same numbers.

- [ ] **Step 1: Write the failing browser check**

Load a 1024x1024 document, assert the shaded region is empty, then shrink the camera pair by hand and
assert the shaded region appears. Drive the browser through the chrome-devtools MCP.

- [ ] **Step 2: Implement a draggable 240x160 screen box**
- [ ] **Step 3: Shade every part of the map the camera can never reach**
- [ ] **Step 4: Re-run the check**
- [ ] **Step 5: Commit**

---

### Task 7: Import a map file into the ROM

Owns Review Focus items 2, 3 and 5.

**Files:**
- Create: `scripts\permanent\map-editor\import_map.py`
- Create: `scripts\permanent\tests\test_import_map.py`

**Interfaces:**
- Consumes: Task 1's `encode_stream`, Task 3's `load`, `validate`, `camera_pair`.
- Produces: `apply(rom: bytes, doc: dict, zone: int, area: int) -> bytes` returning a new ROM with the map
  appended. Reads the live table base at `rom:0xEBD8` and the count at `rom:0xE0AE`, so it composes with
  `battle_arena` and `future_androids`.

- [ ] **Step 1: Write the failing tests**

```python
def test_apply_writes_the_computed_camera_pair_not_the_documents(self):
    # a doc carrying a wrong pair still produces width-239 in the ROM
def test_apply_rejects_a_document_that_fails_validate(self):
def test_apply_refuses_when_the_map_count_byte_would_overflow(self):
def test_apply_composes_on_top_of_an_already_relocated_table(self):
    # apply twice; the second read finds the first map
def test_the_appended_map_reads_back_through_scene_probe(self):
```

- [ ] **Step 2: Run them and watch them fail**
- [ ] **Step 3: Implement `apply`**
- [ ] **Step 4: Run them and watch them pass**
- [ ] **Step 5: Commit**

---

### Task 8: Prove the round trip on one real map

Nothing is trusted until a map leaves the ROM, passes through the editor and comes back unchanged.

**Files:**
- Create: `scripts\permanent\map-editor\roundtrip.py`
- Create: `scripts\permanent\tests\test_roundtrip.py`

- [ ] **Step 1: Write the failing test**

```python
def test_a_vanilla_map_survives_export_import_unchanged(self):
    # read map 7,15 into a document, apply it back as a new map, and assert the new map's
    # layers, collision and tile stream equal the original's
```

- [ ] **Step 2: Run it and watch it fail**
- [ ] **Step 3: Close whatever the round trip loses**

`read_map` is Task 3's and `apply` is Task 7's, so this task writes no new reader. It finds what does not
survive the trip and fixes it in whichever of the two is wrong.

- [ ] **Step 4: Run it and watch it pass**
- [ ] **Step 5: Run the whole suite**

Run: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`
Expected: no new failures. The pre-existing `test_form_survives_the_leader_change` failure stays.

- [ ] **Step 6: Regenerate the tool index**

Run `scripts\permanent\make_tool_index.py`.

- [ ] **Step 7: Commit**

---

## Not in this plan

Walk-behind scenery, music and name, enemy and NPC placement, editing vanilla maps in place. The file
format carries a per-layer priority so walk-behind is a later tool, not a migration.
