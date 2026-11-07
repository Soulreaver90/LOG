# map_view draws animated tile groups

**Date:** 2026-11-07. **Branch:** `feature/map-editor`.

`map_view` built its tile list from the layout `+0x48` static stream alone. A map also loads ANIMATED
tile groups, which DMA their tiles to their own VRAM slots, usually past the stream. Every BG cell
naming a group slot drew nothing, and the layer below showed through. Every render we showed the
owner was wrong in those cells.

---

## 1. The format, read out of the handler

`Sprite_LoadTiles @0x0800501E`, from
`GitHub\legacyofgoku2-disasm\build\code\Sprite_LoadTiles.s`, byte exact for this ROM:

| Thumb | What it does |
|---|---|
| `LDRSH r1, [r4, r3]` with `r3 = 0` | the current frame index, s16, from the IWRAM group state |
| `LDR r0, [r0, #0x4]` | the header F |
| `LDR r1, [r0, #0x4]` after `LSL r1, r1, #2`, `ADD r0, r0, r1` | the frame pointer at `F + 4 + 4 * index` |
| `ADD r1, #0x4` | skip the frame's u32 duration, then decompress |
| `LDRB r1, [r1, #0x1]` | `F+1` is the TILE COUNT |
| `LDRH r0, [r1, #0x2]` | `F+2` is the u16 DESTINATION SLOT |
| `LSL r0, r0, #6`, `ADD r0, r0, r2` with `r2 = 3 << 25` | the DMA lands at `0x06000000 + slot * 64` |
| `LSL r1, r1, #6`, `LSR r0, r1, #2` | `count * 64` bytes, as words |

The layout side: `+0x0C` is the group count and `+0x10` a list of **u32 pointers**, each straight to
a header F. The 8 byte `{s16 frame, u32 F}` record the handler receives in `r0` is the IWRAM state
the engine builds, not the list in ROM. `map_file._animated` already read the list correctly and
was the better reference, as the brief said.

The static stream DMAs entry i to `0x06000000 + 0x40 * i`, so a group slot number and a stream
position are the one scale: the VRAM slot a BG cell names.

## 2. Where the one decoder lives

`map_file` imports `map_view`, and `tile_stream` imports `map_view`, so neither could be the home.
`map-editor` also has a hyphen in its name, so it is not an importable package and a module in
`scene\` must never depend on it.

The decoders went **down** into `scene\scene_probe.py`, the section 9 map reader. It reads every
other layout field already, it works in file offsets, it imports nothing from `map-editor`, and
`docs\design\2026-11-06-one-reader-per-section.md` names it as the reader for this section.

New in `scene_probe`:

| Name | What it reads |
|---|---|
| `rom_offset(rom, word, what)` | the one pointer guard, which `map_file._offset` now is |
| `frame_at(rom, at)` | a frame at a file offset, lazy decoder import, as `collision_bits` does |
| `tile_pairs(payload)` | the `+0x48` delta decode, `e[i] += e[i-1] + 1` |
| `chunk_tiles(rom, pairs, table)` | the chunk walk, one decode per chunk |
| `static_tiles(rom, layout)` | the `+0x48` stream's tiles, slot i at position i |
| `layout_groups(rom, layout)` | the `+0x0C` / `+0x10` groups, frames decoded |
| `loaded_tiles(rom, layout)` | every VRAM slot the layout fills, INDEXED BY SLOT |

Then:

- `map_view.tiles` is `scene_probe.loaded_tiles` in the address form. Its list is indexed by slot,
  with `b""` where nothing loads, so `layer()`'s existing `if not any(px)` skips an unloaded slot
  without a new branch.
- `tile_stream.decode_payload` **is** `scene_probe.tile_pairs`, by identity. `tile_stream.tiles_of`
  keeps the address form and its range check and calls `scene_probe.chunk_tiles`.
  `TILE_BUDGET` and `TILE_BYTES` are aliases.
- `map_file._animated` calls `scene_probe.layout_groups` and only reshapes it into the document,
  dropping the ROM offsets a saved document must not carry. `GROUP_MAX` and `GROUP_MAX_TILES` are
  aliases, and `_offset` is `scene_probe.rom_offset`.
- `scene_probe --map` now prints the static tile count and every animated group, so the reader can
  no longer make a sound cell look like a hole.

**Load order decides.** The stream is laid first and the groups after, in list order, so a group
that overlaps the stream wins. That is what the loader does.

## 3. The proofs

### The 509 cells: 509 to 0

Build `builds\mockups\2026-11-07-plateau\log2_plateau_v5.gba`, map 7,100, rendered with
`--no-collision --no-items`, sampled with the caller's own script:

```
before   animated-slot cells sampled in the render: 509
         drawn as NON-green (dirt/pink) in our render: 509 (100.0%)
         control, 400 random cells inside the top: NON-green 140 (35.0%)
after    animated-slot cells sampled in the render: 509
         drawn as NON-green (dirt/pink) in our render: 0 (0.0%)
         control, 400 random cells inside the top: NON-green 125 (31.2%)
```

### Vanilla maps, before and after

Rendered from the base ROM with the same flags, then diffed cell by cell. A changed 8x8 cell must
be a cell that names an animated slot, or the tile stream work changed a static tile.

| Map | Animated slots | Cells naming one | Cells changed | Changed OUTSIDE those cells |
|---|---|---|---|---|
| 7,15 | 894-895 | 56 | 56 | **0** |
| 4,50 | 890-895 | 86 | 51 | **0** |
| 6,99 | 1-49 | 0 | 0 | **0** |

- **7,15**: every one of the 56 cells that names the animated grass changed. They drew the layer
  below before and draw the grass now.
- **4,50**: 35 of the 86 named cells did not change. All 35 are covered by a fully opaque BG1 or
  BG0 cell, measured, not assumed. The visible ones all changed.
- **6,99**: its 5 groups overlap slots 1 to 49 and overwrite them, which `map_view.tiles` now
  shows, but no cell of its one tilemap layer names those slots, so the picture is unchanged.

### A test that fails before and passes after

`tests\test_map_view.py`, class `AnimatedGroupTests`. The expected pixels are read by walking the
header in the test itself, never through the shared decoder, so a wrong decode cannot agree with
itself and pass.

The failing run, before the change:

```
FAIL: test_an_animated_slot_cell_draws_the_groups_first_frame
AssertionError: Lists differ: [(0, 0, 0), (0, 0, 0), ... ] != [(120, 144, 0), (120, 144, 0), ...]
First differing element 0:
(0, 0, 0)
(120, 144, 0)

FAIL: test_the_tile_list_is_indexed_by_vram_slot
AssertionError: 633 != 896

Ran 14 tests ... FAILED (failures=2)   exit=1
```

Black where the grass belongs, and a 633 entry list where slot 894 is named. After the change the
same file runs 15 tests, OK.

`test_tile_stream.test_decode_stream_matches_map_view_tile_for_tile` had to change: it asserted
`len(map_view.tiles(...)) == len(pairs)`, which is false now that the list is slot indexed, and on
map 6,99 it compared a group tile with the static tile under it. It is now
`test_the_address_form_matches_the_offset_form_tile_for_tile`, comparing the address form with
`scene_probe.static_tiles`, which is the address-versus-offset conversion, the real trap there.
`test_the_decode_is_the_section_9_readers_own` locks the unification by identity.

### The suite

Run whole, with no pipe. The output went to a file with `> file 2>&1` and the shell's own exit code
was read, because a pipe reports the pipe's exit code and a red suite then reads as green.

```
py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent
Ran 1581 tests in 339.994s
FAILED (failures=1, skipped=3, expected failures=1)
exit code 1
```

**The one failure is not mine.** It is
`test_battle_start.BattleStartTests.test_form_survives_the_leader_change`:

```
record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
appearance(character=4, set=61), entry 20, before leader(2), so appearance_revert undoes it
```

Why it is not mine, with evidence rather than a shrug:

- The test imports `scene_harness`, `scene_lib`, `scene_probe` and `log2_build`. It imports neither
  `map_view`, `tile_stream` nor `map_file`.
- My `scene_probe` change is additive apart from one function: `layout_lines`, which only builds CLI
  text. `layout_lines` is called from `show_map` alone, and `show_map` from the CLI and
  `test_scene_probe` alone, which passes, 28 of 28.
- The test builds `build_list_trial_ending.txt` in memory. That list and
  `build_list_core.txt` are among the files already modified in this working tree by other work,
  and `fullpower_ssj` is the module the failure names.

It reproduces on its own in 3.2 seconds, `Ran 38 tests ... FAILED (failures=1)`, exit code 1, so it
is a real state of this tree and not an artifact of a concurrent edit during the long run. Every
other test module I touched passes: `test_map_view` 15 OK, `test_tile_stream` 14 OK, `test_map_file`
39 OK, `test_scene_probe` 28 OK, `test_export_assets` 8 OK, `test_plateau` 24 OK.

## 4. Also done

`scripts\one-time\2026-11-07-plateau\21_render_v4.py` carried `ANIM_STAND_IN = {0x37E: 0x60}`, which
substituted a neighbouring grass tile for the animated one. It calls `map_view.tiles`, so the
substitution is now wrong. It is removed, with the docstring note that explained it. The plateau's
map design is untouched.

## 5. What I could not prove, and what to watch

- **The `+0x48` decode was not duplicated twice. It was duplicated SIX times** in permanent
  non-test code. Two search shapes agree: the delta add `(x[i] + x[i-1] + 1) & 0xFFFF`, and the
  entry split `hi, lo = e >> 8, e & 0xFF` with the `[64 * lo:64 * lo + 64]` slice. A reader that
  decoded the stream some other way, for example from a table of absolute entries, would appear in
  neither shape, so this is "all six reachable by these two shapes", not "all six sites".

  | Site | State |
  |---|---|
  | `scene\map_view.py` | **folded in** |
  | `map-editor\tile_stream.py` | **folded in** |
  | `patches\plateau.py` `source_tiles` | still its own |
  | `patches\battle_arena.py` | still its own |
  | `patches\beam_struggle.py` (two places) | still its own |
  | `art\beam_struggle_art.py` `layout_tiles` | still its own |

  Every one of the four that remain is on the BUILD side, and `battle_arena.py` says why in its
  docstring: "Held here rather than imported from scene.map_view, which needs Pillow. A build must
  not." **That reason is now spent.** `scene_probe` needs no Pillow, so all four could import
  `scene_probe.tile_pairs` and `scene_probe.chunk_tiles`. I left them alone: the brief scoped the
  dedup to `map_view` and `tile_stream`, and proving a build module byte-identical needs a rebuild
  and a SHA-1 compare of the master and trial lists. It is a clean follow-up task.
  The copies inside `tests\` are deliberate independent oracles and must stay.
- **The working tree already carried uncommitted changes in `map_view.py`, `scene_probe.py` and
  `test_tile_stream.py`** before I started, and `test_map_view.py` and the whole
  `scripts\one-time\2026-11-07-plateau\` folder are untracked. My commit therefore carries other
  work in those files that I could not separate from mine. `21_render_v4.py` is left changed in the
  working tree and NOT committed, because committing one file out of an untracked folder is the
  main loop's call.
- **The sampler's green test is a proxy.** The direct pixel comparison against frame 0 is the test
  above, which is the real check; the 509 count is the caller's own measurement rerun unchanged.
- **Animation is not animated.** The render draws each group's FIRST frame. A still picture cannot
  show a cycle, and frame 0 is what the loader puts in VRAM before the first tick.
- **Other agents were live in this tree while I worked**, so the suite result is a reading of the
  tree as it was at that moment.
