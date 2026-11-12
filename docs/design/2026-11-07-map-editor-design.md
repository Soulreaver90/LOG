# Design: the LOG map editor

Agreed with the owner on 2026-11-07, between about 2:00 PM and 2:40 PM. This document is the approved
description. A plan comes after it, and nothing is built before the owner approves this.

## Why it exists

A map generated from rules comes out bland. The plateau proved it the same day: the module filled a
1024x1024 field with one grass tile and ringed it with one rock tile, and the owner rejected it on sight.
His words: "Make the field more dynamic. Look at cell games ground, the vegeta vs 19 fight, no map is
just a bland thing."

He composes by eye. He draws the portraits, he judges every sprite frame, and he decides by looking. The
editor moves map composition from a script to him, the same way the portrait pipeline moved portraits.

A second reason arrived the same morning and is just as important. The plateau rim was drawn correctly
and the owner could never see it, because the camera stopped early. A full-map render hid the fault
completely. Only play proved it. An editor that shows play-scale truth catches that class of fault before
a ROM exists.

## What the owner decided, in his words

| decision | his words |
|---|---|
| Three panes: tiles left, map centre, layers and properties right | chose layout A from three mockups |
| Start from nothing, or from a game map | "Base blank slate, choose from build in maps" |
| Drag and drop to place art | "allow drag and drop of different map sprites, tiles, items" |
| Right click paints collision | "right click to set the collision boundary. The rest is just sprites I drag and drop" |
| Scenery only | "senery, not npcs" |
| Whole objects AND single tiles | "I guess it dpeends, maybe both?" |
| Local, in house | "an in house html map editor" |

## My calls, which he has not ruled on

Marked so he can overrule any of them while reading.

- **Four tools, not one.** Fill and a big brush for ground, stamps for scenery, single tile for touch-up,
  and grab.
- **Grab is the asset pipeline.** The owner opens a real map, drags a box around something he likes and
  names it. It becomes a stamp. There is no up-front library and no asset pass before the first map. The
  library grows out of the real game as he works. This is the single most important call in the document,
  because without it somebody must first cut 327 maps into named pieces, and that cost would sink the
  tool before it shipped.
- **A play-scale truth panel.** A draggable 240x160 screen box, and shading over any part of the map the
  camera can never reach. Driven by the plateau bug.
- **The editor writes a map file, not a ROM.** A separate patch module turns that file into a real map
  entry, the way `plateau.py` and `battle_arena.py` already append one.
- **Vanilla maps open as copies.** The original is never edited in place.
- **Scenery is tiles, not the ROM's prop objects.** A boulder or a tree is placed as a group of tile
  entries in a BG layer, which is how the floor already draws them. The layout prop list at `+0x24` is a
  separate mechanism and this editor does not touch it.
- **Undo is required**, with a deep history. A by-eye tool whose owner cannot step back is unusable.
- **A tiny local Python server serves the editor.** A page opened as `file://` cannot load its own tile
  and map data in a browser, and the project already runs Python everywhere.
- **The editor lives in `scripts\permanent\map-editor\`**, with its exported data beside it, because
  `docs\tool-index.md` already indexes that tree and the README's placement table sends tools there.
- **Map size is chosen in blocks, and every layer is forced to the same grid.** The editor cannot produce
  a map whose layers disagree, which is the plateau fault.

## Goals

1. The owner composes a map by eye in one sitting, and the game loads it.
2. A fault that only shows at play scale is visible in the editor, before a ROM is built.
3. The stamp library grows from use, not from a separate project.

## Non-goals

- Enemy and NPC placement, fights, death tables. Scenery only.
- Scripts, dialogue, scene tables, events.
- Setting the map's music or its name. The owner ruled this out: "no music or name". The patch module
  sets both, away from the editor.
- **Scenery the player walks behind.** Deferred, not refused. Vanilla does it with layer priority: the
  Triceratops Jungle draws its canopy on a layer above the player, and map 7,15 does the same. The owner
  was unsure and asked to keep this basic, so the editor places everything behind the player. **The saved
  file must still carry a per-layer priority**, so adding the feature later is a new tool on an unchanged
  format rather than a migration.
- Editing a vanilla map in place.
- A general purpose ROM editor. This edits maps.
- Animation, palette editing, drawing new pixel art.

## Anti-goals

Each one would make this a failure even if every feature worked.

- **An asset pass before the first map.** If the owner must wait for a library, the tool is dead.
- **Thousands of drags to fill a field.** A 1024x1024 map is 128 x 128 tiles, which is 16,384 cells.
  Ground must be filled, never placed tile by tile.
- **Output that looks right in the editor and wrong in game.** This is the exact failure of 2026-11-07
  and the reason the truth panel exists.
- **Anything that writes under `data\`, or overwrites a ROM, a save or a state.**
- **A published artifact.** The owner's claude.ai account is his NYPL work account. This is a local file
  in this repo, opened from disk, and nothing about it is ever published.

## Constraints

- A local HTML file in this repo. No server required to use it, or a local one only.
- Python tooling is `py -3.14 -P`.
- Never write under `data\`. Check absence, then create exclusively.
- Absolute paths. Never `cd`.
- The export path must compose with the map table relocations that `battle_arena.py` and
  `future_androids.py` already perform, and read the live table base at `rom:0xEBD8` and the count byte
  at `rom:0xE0AE`.

## The data model the file must carry

These are confirmed and already read by `scene_probe.py`.

| piece | where it lives |
|---|---|
| entry, 56 bytes | `+0x02` variations, `+0x03`/`+0x10` regions, `+0x04`/`+0x14` items, `+0x08` combat, `+0x0C` banner, `+0x24` music, `+0x2C` layout array |
| layout | `+0x14` to `+0x20` the four BG layer records, `+0x24`/`+0x28` props, `+0x34` collision, `+0x40`/`+0x44` the layout door list |
| a BG layer | `+0x04` and `+0x08` a SCROLL FACTOR, not a size; `+0x14` blocks across, `+0x15` blocks down; `+0x18` one frame pointer per block |
| a block | 32 x 32 tile entries |
| a tile entry | u16: tile `0x3FF`, `0x400` flip x, `0x800` flip y, `0xF000` palette, **unused here** |

**These tiles are 8bpp, 64 bytes each, so the GBA ignores the `0xF000` palette bits.** Every tile draws
through one shared 256-colour BG palette. Measured during Task 2: `TILE_BYTES = 64`, and a 4bpp 8x8 tile
would be 32. The editor therefore needs **no palette picker**, and the exported manifest carries a list
of exactly one palette. An earlier draft of this document listed the palette bits without that caveat,
which would have sent the editor building a control that does nothing.
| collision | its own grid at layout `+0x34`, independent of the art, which is why right click paints it separately |

**The camera bound is the layout's own `+0x08` and `+0x0A`, and it comes from no layer.**
`Scene_BuildLayers` `@0x08006152` reads `LDRH r1,[r5,#0x8]`, subtracts 1 and stores it as the clamp, then
adds `0xEF` (239) for the view width; `+0x0A` does the same with `0x9F` (159). Confirmed in the
disassembly and against all 334 vanilla layouts with zero exceptions. **The rule the editor must write is
`+0x08 = width - 239` and `+0x0A = height - 159`.**

The plateau shipped this pair copied from its donor map, 449 on a 1024 wide map, so the camera stopped
170 px short of where the player could walk. The map looked correct in every full-map render and was
broken in play. **The editor must compute this pair itself and must never inherit it**, and the truth
panel exists to make the consequence visible before a ROM is built.

**The width in that rule is the WORLD size, which is NOT the block grid.** Measured over all 336 vanilla
layouts during Task 3: the block grid equals the implied world on only 17, and merely covers it on 334.
Map 7,15 stores 713 on a 1280 wide grid, so its real world is 952. Map 4,50 stores 449 on a 1024 grid,
for a world of 688. I verified both myself.

So the document carries an explicit **`world: [w_px, h_px]`**. `camera_pair` always computes from
`world`, `read_map` reads `world` back from the map's own `+0x08` and `+0x0A`, and `validate` enforces
`blocks * 256 >= world`. Deriving the pair from the block grid instead would silently rewrite 319 vanilla
cameras, which is the same class of fault as the plateau bug, applied to every map we touch.

## The tileset question: ANSWERED, and the answer is generous

**A map's tiles are an arbitrary selection from a global pool, not one donor map's set.**

BG tile loader `@0x080050C8` (bible `B1080`, `B1098`, two rows from two separate tasks): the layout
`+0x48` frame is a delta-coded u16 list, `e[i] += e[i-1] + 1`. Each entry's **high byte picks a chunk**
from the layout `+0x4C` chunk table at `0x084DF574`, which holds **168 chunk frames**, and its **low byte
picks a 64-byte tile** inside that chunk. Tiles load to `0x06000000` in order. The list is decoded into a
`0x700` byte buffer, so a map may load **at most 896 tiles**.

Three consequences for the editor:

1. **The palette can mix sources.** Grab may lift a boulder from the jungle and drop it into a Cell Games
   map, because both tiles are reachable from the same 168 chunk pool.
2. **896 is a hard budget**, and the editor must track it. A map that exceeds it will not load. The tile
   count is a live number in the right pane, not a late discovery.
3. **The editor builds the tile stream**, choosing which tiles the map loads from everything placed on it,
   and writes the `+0x48` list and the `+0x4C` table. Reusing a donor map's stream, which is what the
   plateau did, is what makes a map inherit a donor's limits.

**This is a mechanism read from the loader, not a demonstration.** Task 1 of the plan proves it by
building a map whose stream mixes two source maps' tiles and rendering it. If that fails, the editor
falls back to one source per map and grab is limited to within a tileset.

## What is left to the builder

- The page's own structure and libraries. Prefer no build step and no framework unless one earns itself.
- How ground fill picks edge and corner tiles.
- The on-disk map file format, provided it carries the block grid, the collision grid, the layer
  assignment and the stamp placements, and provided it round trips.
- How stamps are stored and named.
- How the truth panel draws the unreachable region. The camera bound itself is now settled, so this is
  presentation only.

## Order

1. Settle the tileset question. It is research, not building.
2. Export: the tiles, palettes and map data the editor loads.
3. The editor: three panes, four tools, the truth panel.
4. Import: the patch module that turns a saved map into a real map entry.
5. Prove the round trip on one real map before any new map is composed in it.
