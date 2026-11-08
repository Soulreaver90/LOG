r"""
map_file.py - The map editor's document: the one contract between the browser and the ROM.

Usage:   sys.path must hold scripts\permanent\map-editor (the folder name has a hyphen, so it is
         not an importable package), then `import map_file`.
         read_map(rom, zone, area) -> doc     turn any map in the ROM into a document
         validate(doc) -> ["problem", ...]    empty when the document is sound
         save(doc, path) / load(path)         JSON, never overwriting, schema gated
         camera_pair(w, h) -> (+0x08, +0x0A)  the camera clamp, always computed
Shape:   {"schema", "world": [w_px, h_px], "blocks": [bw, bh], "chunk_table": address,
          "layers": {"bg0".."bg3": {"priority", "scroll", "offset", "cells": [u16 x grid]}},
          "collision": [u8 x 8192], "terrain": [u8 x 8192], "tiles": [[chunk, tile], ...],
          "animated": [{"first", "frames": [{"duration", "pixels": [u8]}]}],
          "stamps": [...], "blend": {...}, "unread": {...}, "dropped": ["note", ...]}
         One `blocks` pair for the whole document, so a layer grid mismatch, the plateau fault,
         cannot be written down. Padding a smaller layer to it is lossless: pad then trim recovers
         the original grid on 1294 of 1294 vanilla tilemap layers.

CAMERA, the rule this file exists to enforce. `Scene_BuildLayers` @0x08006152 reads layout +0x08,
         subtracts 1 for the scroll clamp and adds 0xEF (239) for the view width; +0x0A does the
         same with 0x9F (159). So +0x08 = world width - 239. **The world is NOT the block grid.**
         Census of 336 vanilla layouts: the grid EQUALS the world on 17 and merely COVERS it on
         334 (the 2 left out, maps 1,7 and 6,99, carry no scroll-1.0 layer). Map 7,15 stores 713
         on a 1280 px grid, so its world is 952. Deriving the pair from the grid would rewrite 319
         vanilla cameras. The plateau shipped a donor's 449 on a 1024 px map and the camera stopped
         170 px short of walkable ground: it rendered perfectly and was broken in play. So `world`
         is its own field, `camera_pair` always computes from it, and a document with no `world` is
         REPORTED, never defaulted to the grid.
PRIORITY is read, never defaulted. Layout bytes +0x04 to +0x07 are the BG0 to BG3 priorities: the
         BGxCNT table 0x081DA8EC row 0 is 0x1C80, 0x1D80, 0x1E80, 0x1F80 with every priority bit
         clear, and the commit code adds those layout bytes in. Map 7,15 reads [3,1,3,3], its BG1
         being the canopy that draws over the player.
CHUNK TABLE, the provenance a tile pair cannot do without. A pair is (chunk, tile) in the table a
         layout names at +0x4C, and most layouts name the shared pool 0x084DF574. A BUILD may give
         one map its own: all 16 build lists give map 14,4 the table 0x0890A92C. A document that did
         not record its table had its pairs resolved against the pool instead, so it named art it
         never came from. Today's one witness EXTENDS the pool (168 equal entries plus a 169th), and
         map 14,4 loads from the 169th, so the pool raises. A table that REPLACED an entry would
         draw the wrong art in silence, and no build list has one. So `chunk_table` is a field,
         `read_map` takes it from the source layout, `blank` names the shared pool, and `validate`
         reports a document without it. This is why SCHEMA is 2: a schema 1 file carries no table.
TILES:   slots 0 to len(tiles)-1 are the static +0x48 stream. An ANIMATED GROUP owns slots
         [first, first + tiles) and usually sits PAST the static stream: map 7,15 decodes 633
         static tiles and its cells name tile 894. A document without the group leaves those cells
         naming nothing, which is how our renderer invented holes in a sound map. Groups are
         carried as decoded pixels, so the editor can draw them and `webfoot_lz_pack.pack` can
         write them back. Group order is kept: group k starts at countdown k + 1 (bible B1078).
         Groups may OVERLAP the static stream. One vanilla layout does it, map 6,99 with 5 groups
         over slots 1 to 49, so overlap is legal and is not reported.
Census:  read_map then validate, run through THIS module over all 336 vanilla layouts on
         2026-11-07: 334 give a sound document, map 6,99 gives an invalid one (its 1 x 1 art grid
         cannot cover its 4096 x 3328 px world, which is true of the map and not of the reader),
         and map 1,7 raises because its four records are all the overlay class, so it has no art.

A BG layer record is carried whole too, because a layer is more than its cells. +0x00 is the class,
         which decides whether the layer is editable at all; +0x04 and +0x08 are a SCROLL FACTOR where
         0x400 is 1.0, not a size (bible tag BMS); +0x0C and +0x10 are a scroll OFFSET; +0x14 and +0x15
         are the block grid; +0x18 on are the block pointers. Bytes +0x16 and +0x17 are zero in all
         1294 vanilla tilemap layers, so nothing hides there. Scroll and offset earn their place: 21
         layers scroll at something other than 1.0 and 364 carry a nonzero offset. Map 9,1 BG3 is the
         witness, a parallax layer at 0x200. Dropping them would write it back as a 1:1 layer, which
         looks right in a full-map render and is wrong the moment the camera moves.

Layout offsets +0x00 to +0x4F, so nothing is lost by silence:
  carried   +0x00 +0x02 +0x03 blend | +0x04-+0x07 priorities | +0x08 +0x0A world | +0x0C +0x10
            animated | +0x14-+0x20 BG layers (tilemap only) | +0x30 +0x3C unread, verbatim
            +0x34 collision | +0x38 terrain | +0x48 tiles | +0x4C the chunk table they index
  computed  +0x08 +0x0A from world, +0x14-+0x20 block grids from blocks, +0x48 from tiles
  dropped   +0x24 +0x28 +0x2C props | +0x40 +0x44 doors | any non-tilemap BG layer
            Each one that holds data is named in doc["dropped"], so the loss is loud.
Read-only on the ROM, and nothing here writes under data\.
"""
import json
import struct
import sys
from pathlib import Path

for _folder in (Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
    sys.path.insert(0, str(_folder))                      # -P omits the script folder; scene\ is one up

from scene import map_view                                # noqa: E402
from scene import scene_probe                             # noqa: E402
import tile_stream                                        # noqa: E402

# ===== CONFIG =====
SCHEMA = 2                                  # 2 added chunk_table; a schema 1 file names no table
BASE_ROM = map_view.BASE
TILE_BUDGET = tile_stream.TILE_BUDGET       # 896 VRAM slots, the loader's 0x700 byte buffer
TILE_BYTES = tile_stream.TILE_BYTES         # an 8x8 tile at 8bpp
VIEW_W, VIEW_H = 240, 160                   # the GBA screen: the camera pair subtracts VIEW - 1
BLOCK_TILES = 32                            # a block is 32 x 32 tile entries
BLOCK_PIXELS = BLOCK_TILES * 8
BLOCK_BYTES = BLOCK_TILES * BLOCK_TILES * 2
GRID_BYTES = 0x2000                         # the collision and terrain frames, 256 x 256 cells of 8 px
GRID_CELLS, GRID_STRIDE = 256, 32
GROUP_MAX = scene_probe.GROUP_MAX           # the IWRAM group state array holds 16 (bible B1096)
GROUP_MAX_TILES = scene_probe.GROUP_MAX_TILES   # the group load buffer is 0x1000 bytes (bible B1078)
LAYER_NAMES = ("bg0", "bg1", "bg2", "bg3")
NEW_MAP_PRIORITY = 3                        # a new map draws every layer behind the player
SCROLL_ONE = scene_probe.SCROLL_ONE         # 0x400 in a layer's +0x04 and +0x08 is 1.0, not a size
TILE_INDEX = 0x3FF                          # a cell's tile bits; 0x400 and 0x800 flip, 0xF000 unused at 8bpp
ADDRESS_LOW, ADDRESS_HIGH = map_view.ROM_BASE, map_view.ROM_BASE + 0x2000000   # a ROM address

L_BLEND, L_ALPHA, L_PRIORITY = 0x00, 0x02, 0x04
L_CAMERA = 0x08                             # +0x0C and +0x10, the groups, are scene_probe's
L_UNREAD_30, L_COLLISION, L_TERRAIN, L_UNREAD_3C = 0x30, 0x34, 0x38, 0x3C
LAYER_BLOCKS = 0x18                         # a BG layer record's first block frame pointer


# ===== the camera, and the counts the editor shows live =====

def camera_pair(width_px: int, height_px: int) -> tuple:
    """The layout +0x08 and +0x0A words for a world this size. Never read a stored pair instead."""
    return width_px - (VIEW_W - 1), height_px - (VIEW_H - 1)


def tile_count(doc: dict) -> int:
    """Static tiles in the +0x48 stream. Animated groups own their own slots past these."""
    return len(doc.get("tiles") or [])


def group_tiles(group: dict) -> int:
    """Tiles in an animated group, derived from its frames so the two can never disagree."""
    frames = group.get("frames") or []
    return len(frames[0].get("pixels") or []) // TILE_BYTES if frames else 0


def loaded_slots(doc: dict) -> set:
    """Every VRAM slot the map fills: the static stream, then each animated group's own span.

    Capped at the budget, because a hand written 'first' of a billion must report a problem
    rather than build a billion element set on the way to reporting it."""
    slots = set(range(min(tile_count(doc), TILE_BUDGET)))
    for group in doc.get("animated") or []:
        first = group.get("first")
        if isinstance(first, int) and 0 <= first < TILE_BUDGET:
            slots |= set(range(first, min(first + group_tiles(group), TILE_BUDGET)))
    return slots


# ===== a new document =====

def blank(blocks: tuple, world: tuple) -> dict:
    """An empty map. `world` is required: a world guessed from the grid is the plateau fault."""
    bw, bh = blocks
    cells = bw * BLOCK_TILES * bh * BLOCK_TILES
    return {"schema": SCHEMA, "world": [world[0], world[1]], "blocks": [bw, bh],
            "chunk_table": tile_stream.CHUNK_TABLE,
            "layers": {name: {"priority": NEW_MAP_PRIORITY, "scroll": [SCROLL_ONE, SCROLL_ONE],
                              "offset": [0, 0], "cells": [0] * cells}
                       for name in LAYER_NAMES},
            "collision": [0] * GRID_BYTES, "terrain": [0] * GRID_BYTES,
            "tiles": [[0, 0]], "animated": [], "stamps": [],
            "blend": {"bldcnt": 0, "alpha": [0, 0]}, "unread": {"0x30": 0, "0x3C": 0},
            "dropped": []}


# ===== validate =====

def _pair_of_ints(value, name: str, problems: list) -> tuple:
    if not (isinstance(value, (list, tuple)) and len(value) == 2
            and all(isinstance(v, int) and v > 0 for v in value)):
        problems.append(f"{name}: expected two positive whole numbers, found {value!r}")
        return None
    return tuple(value)


def _check_chunk_table(doc: dict, problems: list) -> None:
    """The table a document's (chunk, tile) pairs index. Without it a pair names no art at all.

    A build may give one map its own table: all 16 build lists give map 14,4 0x0890A92C, not the
    shared pool. Resolving a document's pairs against a table it did not come from names art it
    never meant, which is why this is a field and not a default."""
    table = doc.get("chunk_table")
    if not isinstance(table, int) or not ADDRESS_LOW <= table < ADDRESS_HIGH:
        problems.append(f"chunk_table: expected the ROM address of a chunk table, found {table!r}. "
                        f"Without it a (chunk, tile) pair names no art, because a chunk number only "
                        f"means something in the table the map was read from")


def _check_tiles(doc: dict, problems: list) -> None:
    tiles = doc.get("tiles")
    if not isinstance(tiles, list) or not tiles:
        problems.append("tiles: a map loads at least one tile, and this document names none")
        return
    if len(tiles) > TILE_BUDGET:
        problems.append(f"tiles: {len(tiles)} tiles, and the loader decodes at most {TILE_BUDGET}")
    for n, pair in enumerate(tiles):
        if not (isinstance(pair, (list, tuple)) and len(pair) == 2
                and all(isinstance(v, int) and 0 <= v <= 0xFF for v in pair)):
            problems.append(f"tiles: entry {n} is {pair!r}, not a [chunk, tile] pair of bytes")
            return


def _check_animated(doc: dict, problems: list) -> None:
    groups = doc.get("animated")
    if not isinstance(groups, list):
        problems.append(f"animated: expected a list of groups, found {type(groups).__name__}")
        return
    if len(groups) > GROUP_MAX:
        problems.append(f"animated: {len(groups)} groups, and the state array holds {GROUP_MAX}")
    for k, group in enumerate(groups):
        frames = group.get("frames") if isinstance(group, dict) else None
        if not isinstance(frames, list) or not frames:
            problems.append(f"animated group {k}: a group needs at least one frame")
            continue
        lengths = {len(f.get("pixels") or []) for f in frames}
        if len(lengths) > 1:
            problems.append(f"animated group {k}: its frames hold {sorted(lengths)} bytes, and every "
                            f"frame of one group loads the same tiles")
            continue
        size = lengths.pop()
        if size % TILE_BYTES or not size:
            problems.append(f"animated group {k}: {size} bytes a frame is not a whole "
                            f"{TILE_BYTES} byte tile list")
            continue
        count = size // TILE_BYTES
        if count > GROUP_MAX_TILES:
            problems.append(f"animated group {k}: {count} tiles, and the load buffer holds "
                            f"{GROUP_MAX_TILES}")
        first = group.get("first")
        if not isinstance(first, int) or first < 0:
            problems.append(f"animated group {k}: 'first' is {first!r}, not a slot number")
        elif first + count > TILE_BUDGET:
            problems.append(f"animated group {k}: slots {first} to {first + count - 1}, past the "
                            f"{TILE_BUDGET} slot budget")


def _check_layers(doc: dict, blocks: tuple, problems: list) -> None:
    layers = doc.get("layers")
    if not isinstance(layers, dict) or not layers:
        problems.append("layers: the document carries no BG layer")
        return
    expected = blocks[0] * BLOCK_TILES * blocks[1] * BLOCK_TILES if blocks else None
    loaded = loaded_slots(doc)
    for name, layer in layers.items():
        if name not in LAYER_NAMES:
            problems.append(f"layer {name!r}: the BG layers are {', '.join(LAYER_NAMES)}")
            continue
        priority = layer.get("priority") if isinstance(layer, dict) else None
        if priority is None:
            problems.append(f"layer {name} carries no priority, and a later tool needs it to draw "
                            f"scenery in front of the player")
        elif not (isinstance(priority, int) and 0 <= priority <= 3):
            problems.append(f"layer {name} priority {priority!r}: the hardware has two priority "
                            f"bits, so 0 to 3")
        for field in ("scroll", "offset"):
            value = layer.get(field) if isinstance(layer, dict) else None
            if not (isinstance(value, (list, tuple)) and len(value) == 2
                    and all(isinstance(v, int) and 0 <= v <= 0xFFFFFFFF for v in value)):
                problems.append(f"layer {name} {field}: expected two whole words, found {value!r}")
        cells = layer.get("cells") if isinstance(layer, dict) else None
        if not isinstance(cells, list):
            problems.append(f"layer {name} carries no cells")
            continue
        if expected is not None and len(cells) != expected:
            problems.append(f"layer {name} holds {len(cells)} cells, and a "
                            f"{blocks[0]} x {blocks[1]} block grid is {expected}")
            continue
        unloaded = sorted({c & TILE_INDEX for c in cells if isinstance(c, int)} - loaded)
        if unloaded:
            problems.append(f"layer {name} names tile slots {unloaded[:4]} that the map never "
                            f"loads, so the game draws nothing there")


def _check_grid(doc: dict, key: str, problems: list) -> list:
    grid = doc.get(key)
    if not (isinstance(grid, list) and len(grid) == GRID_BYTES
            and all(isinstance(b, int) and 0 <= b <= 0xFF for b in grid)):
        problems.append(f"{key}: expected {GRID_BYTES} byte values, found "
                        f"{len(grid) if isinstance(grid, list) else type(grid).__name__}")
        return None
    return grid


def _check_reachable(bits: list, blocks: tuple, world: tuple, problems: list) -> None:
    """Open ground inside the art grid that the camera can never reach. The plateau, in one rule.

    An all-open frame is exempt: 13 vanilla layouts carry one, which means collision is unused
    rather than that every cell is walkable. Measured THROUGH THIS MODULE over all 336 vanilla
    layouts on 2026-11-07, no layout reports this problem. The bound is the document's own block
    grid, which includes parallax layers, so it checks a wider region than a scroll-1.0 bound."""
    if all(b == 0xFF for b in bits):
        return
    grid_w, grid_h = min(blocks[0] * BLOCK_PIXELS, GRID_CELLS * 8), min(blocks[1] * BLOCK_PIXELS,
                                                                        GRID_CELLS * 8)
    for cy in range(grid_h // 8):
        row = bits[cy * GRID_STRIDE:(cy + 1) * GRID_STRIDE]
        if not any(row):
            continue
        for cx in range(grid_w // 8):
            if not (row[cx >> 3] >> (cx & 7) & 1):
                continue
            if cx * 8 >= world[0] or cy * 8 >= world[1]:
                problems.append(f"collision is open at ({cx * 8},{cy * 8}), inside the "
                                f"{grid_w} x {grid_h} px art grid but past the "
                                f"{world[0]} x {world[1]} px world, so the camera can never reach it")
                return


def _check_stamps(doc: dict, blocks: tuple, problems: list) -> None:
    stamps = doc.get("stamps")
    if not isinstance(stamps, list):
        problems.append(f"stamps: expected a list, found {type(stamps).__name__}")
        return
    across, down = (blocks[0] * BLOCK_TILES, blocks[1] * BLOCK_TILES) if blocks else (0, 0)
    for n, stamp in enumerate(stamps):
        if not isinstance(stamp, dict) or not isinstance(stamp.get("name"), str):
            problems.append(f"stamp {n}: every stamp placement carries a name")
            continue
        if stamp.get("layer") not in (doc.get("layers") or {}):
            problems.append(f"stamp {n} ({stamp['name']}) sits on layer {stamp.get('layer')!r}, "
                            f"which this map has not got")
            continue
        box = [stamp.get(k) for k in ("x", "y", "w", "h")]
        if not all(isinstance(v, int) and v >= 0 for v in box):
            problems.append(f"stamp {n} ({stamp['name']}): x, y, w and h are cell counts")
        elif box[0] + box[2] > across or box[1] + box[3] > down:
            problems.append(f"stamp {n} ({stamp['name']}) runs past the {across} x {down} cell grid")


def validate(doc: dict) -> list:
    """Every problem with this document, in human words. Empty means it is sound. Never raises."""
    if not isinstance(doc, dict):
        return [f"the document is a {type(doc).__name__}, not an object"]
    problems = []
    if doc.get("schema") != SCHEMA:
        problems.append(f"schema {doc.get('schema')!r}: this tool reads and writes schema {SCHEMA}")

    blocks = _pair_of_ints(doc.get("blocks"), "blocks", problems)
    world = _pair_of_ints(doc.get("world"), "world", problems)
    if world and (world[0] < VIEW_W or world[1] < VIEW_H):
        problems.append(f"world {world[0]} x {world[1]} px is smaller than the {VIEW_W} x {VIEW_H} "
                        f"px screen, so the camera clamp would go negative")
    if blocks and world:
        grid = (blocks[0] * BLOCK_PIXELS, blocks[1] * BLOCK_PIXELS)
        if grid[0] < world[0] or grid[1] < world[1]:
            problems.append(f"a {blocks[0]} x {blocks[1]} block grid draws {grid[0]} x {grid[1]} px "
                            f"and cannot cover a world of {world[0]} x {world[1]} px")

    _check_chunk_table(doc, problems)
    _check_tiles(doc, problems)
    _check_animated(doc, problems)
    _check_layers(doc, blocks, problems)
    _check_stamps(doc, blocks, problems)
    bits = _check_grid(doc, "collision", problems)
    _check_grid(doc, "terrain", problems)
    if bits and blocks and world:
        _check_reachable(bits, blocks, world, problems)
    return problems


# ===== save and load =====

def save(doc: dict, path: Path) -> None:
    """Write a sound document. An unsound one is refused here rather than found in game."""
    problems = validate(doc)
    if problems:
        raise ValueError("this document is not sound:\n  " + "\n  ".join(problems))
    with open(Path(path), "x", encoding="utf-8") as handle:         # "x": never overwrite
        json.dump(doc, handle)


def load(path: Path) -> dict:
    """Read a document of THIS schema. Another schema raises rather than being read half right."""
    with open(Path(path), encoding="utf-8") as handle:
        doc = json.load(handle)
    found = doc.get("schema") if isinstance(doc, dict) else None
    if found != SCHEMA:
        raise ValueError(f"{Path(path).name} is schema {found!r} and this tool reads schema {SCHEMA}")
    return doc


# ===== read a map out of the ROM =====

_offset = scene_probe.rom_offset    # the one pointer guard; every pointer this module follows uses it


def _frame(rom: bytes, word: int, what: str, size: int) -> list:
    _offset(rom, word, what)
    data = map_view.frame(rom, word)
    if len(data) != size:
        raise ValueError(f"the {what} frame decodes to {len(data)} bytes, not {size}")
    return list(data)


def _cells(rom: bytes, rec: dict, blocks: tuple) -> list:
    """One BG layer's tile entries, padded out to the document's block grid.

    A null block pointer is empty ground, not a fault, and padding leaves the real blocks where
    they were because block k draws at ((k % bx) * 256, (k // bx) * 256)."""
    across = blocks[0] * BLOCK_TILES
    cells = [0] * (across * blocks[1] * BLOCK_TILES)
    bx, by = rec["blocks"]
    for b in range(bx * by):
        pointer = scene_probe.u32(rom, rec["at"] + LAYER_BLOCKS + 4 * b)
        if not pointer:
            continue
        _offset(rom, pointer, f"BG{rec['bg']} block {b}")
        block = map_view.frame(rom, pointer)
        if len(block) != BLOCK_BYTES:
            raise ValueError(f"BG{rec['bg']} block {b} decodes to {len(block)} bytes, not {BLOCK_BYTES}")
        entries = struct.unpack(f"<{BLOCK_TILES * BLOCK_TILES}H", block)
        ox, oy = (b % bx) * BLOCK_TILES, (b // bx) * BLOCK_TILES
        for row in range(BLOCK_TILES):
            start = (oy + row) * across + ox
            cells[start:start + BLOCK_TILES] = entries[row * BLOCK_TILES:(row + 1) * BLOCK_TILES]
    return cells


def _animated(rom: bytes, off: int) -> list:
    """Every animated group in list order, as the document holds it. Order is the tick (B1078).

    The read is scene_probe.layout_groups, the one the renderer draws from, so the editor and a
    picture cannot disagree about a group. This turns its bytes into the JSON shape and drops the
    ROM offsets, which a document must not carry: a saved offset is dead the moment a build moves
    the group."""
    return [{"first": g["first"],
             "frames": [{"duration": f["duration"], "pixels": list(f["pixels"])}
                        for f in g["frames"]]}
            for g in scene_probe.layout_groups(rom, off)]


def read_map(rom: bytes, zone: int, area: int, var: int = 1) -> dict:
    """One map in the ROM as a document. The ROM is read, never written.

    The camera world comes from this map's OWN +0x08 and +0x0A, which is a read and not an
    inheritance: a stored pair copied from a DONOR map is the plateau fault."""
    _index, entry = scene_probe.map_entry(rom, zone, area)
    off = map_view.layout_of(rom, entry, var) - map_view.ROM_BASE

    records = scene_probe.layout_layers(rom, off)
    tilemaps = [r for r in records if r["kind"] == "tilemap"]
    if not tilemaps:
        raise ValueError(f"map {zone},{area} variation {var} has no tilemap BG layer, so it has no "
                         f"block grid and no editable art")
    blocks = (max(r["blocks"][0] for r in tilemaps), max(r["blocks"][1] for r in tilemaps))

    dropped, layers = [], {}
    for rec in records:
        name = LAYER_NAMES[rec["bg"]]
        if rec["kind"] == "none":
            continue
        if rec["kind"] != "tilemap":
            why = ("a wrapping 256 px pattern, such as map 6,1's rain" if rec["kind"] == "overlay"
                   else "a layer class this project has not read")
            dropped.append(f"{name} is class 0x{rec['class']:08X}, {why}, which this document "
                           f"cannot hold")
            continue
        layers[name] = {"priority": rom[off + L_PRIORITY + rec["bg"]],
                        "scroll": list(rec["scroll"]), "offset": list(rec["offset"]),
                        "cells": _cells(rom, rec, blocks)}

    props = scene_probe.layout_props(rom, off)
    if props:
        dropped.append(f"{len(props)} layout props at +0x24, an OBJ mechanism this editor does not "
                       f"touch")
    doors = scene_probe.u32(rom, off + scene_probe.L_DOOR_COUNT)
    if doors:
        dropped.append(f"{doors} layout doors at +0x40, which the patch module sets, not the editor")

    camera = struct.unpack_from("<HH", rom, off + L_CAMERA)
    return {"schema": SCHEMA,
            "world": [camera[0] + VIEW_W - 1, camera[1] + VIEW_H - 1],
            "blocks": [blocks[0], blocks[1]],
            "layers": layers,
            "collision": _frame(rom, scene_probe.u32(rom, off + L_COLLISION), "collision", GRID_BYTES),
            "terrain": _frame(rom, scene_probe.u32(rom, off + L_TERRAIN), "terrain", GRID_BYTES),
            "chunk_table": tile_stream.chunk_table_of(rom, off + map_view.ROM_BASE),
            "tiles": [[chunk, tile] for chunk, tile
                      in tile_stream.decode_stream(rom, off + map_view.ROM_BASE)],
            "animated": _animated(rom, off),
            "stamps": [],
            "blend": {"bldcnt": struct.unpack_from("<H", rom, off + L_BLEND)[0],
                      "alpha": [rom[off + L_ALPHA], rom[off + L_ALPHA + 1]]},
            "unread": {"0x30": scene_probe.u32(rom, off + L_UNREAD_30),
                       "0x3C": scene_probe.u32(rom, off + L_UNREAD_3C)},
            "dropped": dropped}
