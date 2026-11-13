r"""
scene_probe.py - The section 9 map reader, plus the scene table, record and text readers.

Usage:   py -3.14 -P scripts\permanent\scene\scene_probe.py --map 6,1
         py -3.14 -P scripts\permanent\scene\scene_probe.py --map 6,100 --rom <a build> --var 1
         py -3.14 -P scripts\permanent\scene\scene_probe.py --table 0x3DBDD4
         py -3.14 -P scripts\permanent\scene\scene_probe.py --record 0x3DB59C --len 0xCC
         py -3.14 -P scripts\permanent\scene\scene_probe.py --find-text "You look great"
         Add --rom <path> to read a build instead of the base ROM, and --count N to cap a table walk.
Output:  stdout. The tool never writes to the ROM and never writes a file.
Reads:   THIS ROM's map table, resolved by map_table() from the literal at rom:0xEBD8 and the count byte
         at rom:0xE0AE, so a build that moved its table reads its own and finds an appended map.
         MAP_TABLE and MAP_COUNT are the base ROM's documented values and are never the read path.
         scene_lib gives the op names, the decoder and the table walker.
Map:     `--map` prints one map end to end, from the bible section 9 rows:
         entry (56 bytes, tag OVW and 1312) +0x02 variations, +0x03/+0x10 regions, +0x04/+0x14 items,
         +0x08 combat, +0x0C banner, +0x24 music (a song id in 230 maps, a SCRIPT in 62, tag OPS),
         +0x28 variation script, +0x2C layout array, +0x30 enter script, +0x34 leave script;
         layout +0x0C/+0x10 animated tile groups, +0x14-+0x20 BG layer records, +0x24/+0x28 props
         (tag EFX), +0x34 collision (tag CSV), +0x40/+0x44 the layout door list (tags WRP and OPS),
         +0x48/+0x4C the tile stream and its chunk table.
         A map carries doors in TWO carriers and this reader prints BOTH, each labelled: the region list
         holds 69 of the game's 655 doors and the layout list holds the other 586 (tag OPS).
         An item is {factory, trigger, s16 x0 y0, s16 x1 y1, data}: a warp (factory @0x0800C233 or
         @0x0800D9C3) carries {dir, zone, area, var, s16 x, s16 y}, a scene item (@0x0800D7E1) a table
         pointer, a script region (@0x0800C2C3) a script. All CONFIRMED (bible SAV, CSV, SPC, WRP, OPS).
Floor:   a map reached only by a script `ext 35`, `38` or `39` has no door in either carrier, so a door
         count here is a FLOOR on the ways in, never a proof that a map is sealed to scripts.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

import log_paths  # noqa: E402
from scene import scene_lib as S                                         # noqa: E402

# ===== CONFIG =====
BASE = log_paths.BASE_ROM
TOOL_INDEX_NOTE = ("**`--map` is the section 9 READER.** It prints one map end to end: the entry fields "
                   "by name, the layout chain, BOTH door carriers side by side (the region list at entry "
                   "`+0x10` and the layout door list at `+0x40`/`+0x44`), the layout props, the collision "
                   "frame with its container type and open counts, and the BG layer records. It resolves "
                   "the map table from the ROM it is given, so `--rom <a build>` finds an appended map.")
MAP_TABLE, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56      # the BASE ROM's table; a build may move it
MAP_BASE_LITERAL, MAP_COUNT_BYTE = 0xEBD8, 0xE0AE       # where a build's own table base and count live
WARP_FACTORIES = (0x0800C233, 0x0800D9C3)
SCENE_FACTORY, SCRIPT_FACTORY, GROUP_FACTORY = 0x0800D7E1, 0x0800C2C3, 0x0800E77F
NPC_FACTORY = 0x0800D6DF                        # an NPC spawn item: +8 x, y, +0xC set id (bible CJ2)
TALK_FACTORIES = (0x0800B710, 0x0800B711)       # interactive object; the Thumb bit may be set
ITEM_SIZE, REGION_SIZE = 0x18, 8
SCRIPT_REGION = (0x3B0000, 0x420000)

# Map entry fields, 56 bytes (bible tag OVW and 1312). The byte at +N counts the list at the word.
ENTRY_BYTES = ((0x02, "variations"), (0x03, "region count"), (0x04, "item count"),
               (0x05, "swap count"), (0x06, "pickup count"), (0x07, "marker count"))
ENTRY_WORDS = ((0x08, "combat"), (0x0C, "banner"), (0x10, "region list"), (0x14, "item list"),
               (0x18, "swap list"), (0x1C, "pickup list"), (0x20, "marker list"), (0x24, "music"),
               (0x28, "variation script"), (0x2C, "layout array"), (0x30, "enter script"),
               (0x34, "leave script"))
BANNER_POOL = 0xE2840                           # the alphabetical name pool the +0x0C index reads (tag LAB, LAB)

# Layout fields (bible tags: EFX props, CSV collision, WRP doors, BMS layers).
L_LAYERS = (0x14, 0x18, 0x1C, 0x20)             # BG0, BG1, BG2, BG3 records
L_PROP_COUNT, L_PROP_LIST, L_PROP_SHEET = 0x24, 0x28, 0x2C   # NOT the entry's +0x2C: the offsets collide
L_COLLISION, L_DOOR_COUNT, L_DOOR_LIST = 0x34, 0x40, 0x44
DOOR_LIST_CAP, PROP_LIST_CAP = 64, 256          # vanilla peaks at 7 doors; a cap only stops a wild word
L_TILE_STREAM, L_TILE_TABLE = 0x48, 0x4C
L_GROUP_COUNT, L_GROUP_LIST = 0x0C, 0x10        # the animated tile groups (bible B1078, B1096)
TILE_BYTES = 64                                 # an 8x8 tile at 8bpp
TILE_BUDGET = 0x700 // 2                        # Map_LoadLayer decodes the stream into 0x700 bytes
GROUP_MAX = 16                                  # the IWRAM group state array holds 16 (bible B1096)
GROUP_MAX_TILES = 64                            # the group load buffer is 0x1000 bytes (bible B1078)
PROP_SIZE = 24                                  # x0, y0, x1, y1 as u32, attr pair, u16 tile, u8 prio, u8
LAYER_TILEMAP, LAYER_OVERLAY = 0x080056A1, 0x08004FCD        # the two layer classes (bible tag RAIN)
SCROLL_ONE = 0x400                              # rec +4 and +8: a scroll factor, 0x400 = 1.0 (bible tag BMS)
COLLISION_CELLS = 256                           # the frame is a 256 x 256 grid of 8 px cells, 8192 bytes
COLLISION_STRIDE = COLLISION_CELLS // 8


def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def _is_code(word: int) -> bool:
    """An item's first word is its factory, a Thumb entry point in the first 64 KB of code."""
    return 0x08000000 <= word < 0x08020000


# ===== tables and records =====

def show_table(rom: bytes, at: int, count: int = None) -> list:
    """The whole table: one block a record, with the ops named and the text shown."""
    count = count or S.table_length(rom, at)   # NOT table_end: that stops at the first END entry
    out = [f"table rom:0x{at:X}  {count} words"]
    stray = S.stray_before(rom, at)
    if stray is not None:
        out.append(f"  note: the word before word 0 is 0x{stray:X}, a known stray. "
                   f"This listing walks forward from the address you gave, so no index shifts (CH6).")
    for i, word in S.walk(rom, at, count).items():
        if S.is_end_entry(word):
            out.append(f"  [{i:2d}] END, resume index {word}")
            continue
        out += ["  " + line for line in show_record(rom, word - S.ROM_BASE, index=i)]
    return out


def show_record(rom: bytes, at: int, length: int = None, index: int = None) -> list:
    """One record: its header, then the named ops or the line."""
    rec = S.decode_record(rom, at, length)
    tag = f"[{index:2d}] " if index is not None else ""
    head = f"{tag}rom:0x{at:X}  type {rec.kind}  next {rec.nxt}"
    if rec.portrait is not None:
        head += f"  portrait {rec.portrait}"
    out = [head]
    if rec.kind == S.TYPE_CODE:
        out += ["    " + line for line in S.listing(rom, at + 3, rec.end - 1)]
    elif rec.kind == S.TYPE_TEXT:
        out.append(f'    "{rec.line}"')
    elif rec.target:
        what = "table" if rec.kind == S.TYPE_JUMP else "payload"
        out.append(f"    {what} rom:0x{rec.target - S.ROM_BASE:X}"
                   + ("  (a type 2 stream: pass --len to show its length)" if rec.kind == S.TYPE_STREAM else ""))
    return out


# ===== maps =====

def map_table(rom: bytes) -> tuple:
    """(file offset, entry count) of THIS ROM's map table, read from the literal rom:0xEBD8 and the count
    getter sub_0800E0AC (`MOV r0,#0xFF ; ADD r0,#n`). A build that moves the table, as battle_arena does,
    is read correctly; MAP_TABLE and MAP_COUNT are the base ROM's values and would read the dead copy."""
    return u32(rom, MAP_BASE_LITERAL) - S.ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]


def map_entry(rom: bytes, zone: int, area: int, table: int = None, count: int = None) -> tuple:
    """(index, file offset) of one map's entry. table and count default to THIS ROM's own values, read
    from the literal by map_table(), so a build whose table has moved resolves its appended maps. On the
    base ROM map_table() returns MAP_TABLE and MAP_COUNT, so the default is unchanged there."""
    live_table, live_count = map_table(rom)
    table = live_table if table is None else table
    count = live_count if count is None else count
    for k in range(count):
        at = table + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the map table")


def item(rom: bytes, at: int) -> dict:
    """One region, warp or scene item: {factory, trigger, s16 rect, data}."""
    factory, trigger = u32(rom, at), u32(rom, at + 4)
    x0, y0, x1, y1 = struct.unpack_from("<4h", rom, at + 8)
    out = {"at": at, "factory": factory, "trigger": trigger, "rect": (x0, y0, x1, y1), "kind": "item"}
    if factory in WARP_FACTORIES:
        direction, zone, area, var = rom[at + 0x10:at + 0x14]
        x, y = struct.unpack_from("<2h", rom, at + 0x14)
        out.update(kind="warp", to=(zone, area, var), landing=(x, y), direction=direction)
    elif factory == SCENE_FACTORY:
        out.update(kind="scene", table=u32(rom, at + 0x10) - S.ROM_BASE)
    elif factory == SCRIPT_FACTORY:
        out.update(kind="script", script=u32(rom, at + 0x10) - S.ROM_BASE)
    elif factory in TALK_FACTORIES:
        # An interactive object: +0x08 s16 position, +0x0C its scene table, +0x10 its sprite set. CONFIRMED
        # on the map 9,1 Dende object rom:0x403F60 (table 0x3DD044, set 36 at 760,416; bible CSP).
        x, y = struct.unpack_from("<2h", rom, at + 8)
        out.update(kind="talk", at_xy=(x, y), table=u32(rom, at + 0x0C) - S.ROM_BASE, set_id=u32(rom, at + 0x10))
    elif factory == NPC_FACTORY:
        # An NPC spawn: +8 s16 x, y, +0xC set id, +0x10 step count, +0x14 step pointers (bible CJ2 row).
        # Without this the ending's two actors on map 6,1 print as a bare "item".
        x, y = struct.unpack_from("<2h", rom, at + 8)
        out.update(kind="npc", at_xy=(x, y), set_id=u32(rom, at + 0x0C), steps=u32(rom, at + 0x10))
    elif factory == GROUP_FACTORY:
        # +0x14 points at a sub-struct {@0x080106B3, scene table}. The Cell Games scenes are owned this way,
        # so a tool that reads only the region list misses them (bible SS3). CONFIRMED on map 14,3.
        # It is also the ENEMY SPAWN record: +8 enemy type, +0xC x, y, +0x10 set id (bible CFS row). The
        # kind stays "group" because map_index and the scene_lib tests read that name.
        sub = u32(rom, at + 0x14)
        x, y = struct.unpack_from("<2h", rom, at + 0x0C)
        out.update(kind="group", enemy_type=u32(rom, at + 8), at_xy=(x, y), set_id=u32(rom, at + 0x10))
        if sub >> 24 == 0x08 and u32(rom, sub - S.ROM_BASE) == 0x080106B3:
            out["table"] = u32(rom, sub - S.ROM_BASE + 4) - S.ROM_BASE
    return out


def map_items(rom: bytes, zone: int, area: int, table: int = None, count: int = None) -> dict:
    """{'regions': [(condition, item)], 'items': [item]} for one map. table and count are map_entry's."""
    _, at = map_entry(rom, zone, area, table, count)
    regions, items = [], []
    region_list, item_list, n_items = u32(rom, at + 0x10), u32(rom, at + 0x14), rom[at + 4]
    if region_list:
        base = region_list - S.ROM_BASE
        for i in range(64):
            cond, pointer = u32(rom, base + REGION_SIZE * i), u32(rom, base + REGION_SIZE * i + 4)
            # The list carries no count, so it ends at the first pair that is not {condition, item}. An item
            # always opens with a code factory, so a word outside the code area ends the walk. Without this
            # the walk runs past the end of map 9,1 and invents a region.
            if not pointer or pointer >> 24 != 0x08 or not _is_code(u32(rom, pointer - S.ROM_BASE)):
                break
            regions.append((cond, item(rom, pointer - S.ROM_BASE)))
    if item_list:
        base = item_list - S.ROM_BASE                 # a list of pointers to items, not inline items
        for i in range(n_items):
            pointer = u32(rom, base + 4 * i)
            if pointer >> 24 == 0x08:
                items.append(item(rom, pointer - S.ROM_BASE))
    return {"entry": at, "regions": regions, "items": items, "count": n_items}


# ===== the layout: the SECOND door carrier, the props, the collision and the BG layers =====

def is_pointer(word: int) -> bool:
    return 0x08000000 <= word < 0x0A000000


def layouts(rom: bytes, entry: int) -> list:
    """Every variation's layout file offset, from entry +0x2C. The array is indexed by variation - 1,
    and byte +0x02 is the variation count (1 in 318 of 327 maps, 2 in 9; bible tag ARN).

    The one place that walks this chain. map_view, map_index and warp_graph all call it, so a build that
    moves a layout cannot be read correctly by one tool and wrongly by the next."""
    array = u32(rom, entry + 0x2C)
    if not is_pointer(array):
        return []
    out = []
    for var in range(max(rom[entry + 0x02], 1)):
        word = u32(rom, array - S.ROM_BASE + 4 * var)
        out.append(word - S.ROM_BASE if is_pointer(word) else None)
    return out


def layout_doors(rom: bytes, layout: int) -> dict:
    """The LAYOUT door list: +0x40 is the count and +0x44 names a list of POINTERS to warp items.

    This is the carrier that holds 586 of the game's 655 doors (bible tag OPS). Reading the list as
    inline items finds zero doors in the whole ROM, which is how that mistake shows itself (tag OPS).
    The declared `count` and the decoded `doors` are both returned, because a disagreement is a finding
    and a reader that hides one is how the arena shipped three times with doors it inherited."""
    count, lst = u32(rom, layout + L_DOOR_COUNT), u32(rom, layout + L_DOOR_LIST)
    out = {"count": count, "list": lst, "doors": [], "not_a_warp": []}
    if not count or not is_pointer(lst):
        return out
    for i in range(min(count, DOOR_LIST_CAP)):             # a wild count must not run off the ROM
        pointer = u32(rom, lst - S.ROM_BASE + 4 * i)
        if not is_pointer(pointer):
            out["not_a_warp"].append((i, f"0x{pointer:X}, not a ROM pointer"))
            continue
        it = item(rom, pointer - S.ROM_BASE)
        if it["kind"] == "warp":
            out["doors"].append(it)
        else:
            out["not_a_warp"].append((i, f"factory @0x{it['factory']:08X}, kind {it['kind']}"))
    return out


def layout_props(rom: bytes, layout: int) -> list:
    """The layout prop list: +0x24 count, +0x28 entries of 24 bytes, +0x2C the shared sheet frame.

    An entry is {u32 x0, y0, x1, y1, u32 attr0 | attr1 << 16, u16 tile, u8 priority, u8} (bible EFX row
    1152). The coordinates are 32-bit words, not s16: map 6,1 prop 2 reads (408,556)-(472,620), which is
    the save point the SAV row puts at (408,568)-(457,617). Reading them as s16 gives every second field
    as zero, which is the loud failure of that mistake."""
    count, lst = u32(rom, layout + L_PROP_COUNT), u32(rom, layout + L_PROP_LIST)
    if not count or not is_pointer(lst):
        return []
    base, out = lst - S.ROM_BASE, []
    for i in range(min(count, PROP_LIST_CAP)):             # a wild count must not run off the ROM
        at = base + PROP_SIZE * i
        x0, y0, x1, y1, attr = struct.unpack_from("<5I", rom, at)
        tile, priority = struct.unpack_from("<HB", rom, at + 0x14)
        out.append({"at": at, "rect": (x0, y0, x1, y1), "attr0": attr & 0xFFFF,
                    "attr1": attr >> 16, "tile": tile, "priority": priority})
    return out


def layout_layers(rom: bytes, layout: int) -> list:
    """The four BG layer records at +0x14 to +0x20, each with its class and its scroll words.

    Class 0x080056A1 is the ordinary tilemap layer; 0x08004FCD is the scrolling overlay class, whose
    width and height words are 0 because it is a wrapping 256x256 pattern, not a map-sized layer (bible
    tag RAIN). A reader that prints "none" for the overlay class hides map 6,1's rain."""
    out = []
    for n, off in enumerate(L_LAYERS):
        rec = u32(rom, layout + off)
        if not is_pointer(rec):
            out.append({"bg": n, "at": None, "word": rec, "kind": "none"})
            continue
        at = rec - S.ROM_BASE
        cls = u32(rom, at)
        kind = ("tilemap" if cls == LAYER_TILEMAP else
                "overlay" if cls == LAYER_OVERLAY else "unknown class")
        out.append({"bg": n, "at": at, "class": cls, "kind": kind,
                    "scroll": (u32(rom, at + 4), u32(rom, at + 8)),
                    "offset": (u32(rom, at + 0x0C), u32(rom, at + 0x10)),
                    "blocks": (rom[at + 0x14], rom[at + 0x15])})
    return out


def map_bounds(rom: bytes, layout: int) -> tuple:
    """(width, height) in pixels: the block extent of the layers that scroll with the world 1 to 1.

    A layer record's +4 and +8 are a SCROLL FACTOR, not a size: 0x400 is 1.0 (bible tag BMS). So a
    layer at 0x400 is in world coordinates and its blocks of 256 px give the world extent, while a
    parallax layer such as map 9,1's BG3 at 0x200 is wider than the map and must not set the bound.
    Measured over all 327 maps: every open collision cell is inside this bound on 313 of them and
    outside it on NONE. The 14 left out are the 12 whose collision frame is all open (every one of the
    65536 cells set) and maps 1,7 and 6,99, which carry no scroll-1.0 layer. CONFIRMED by that census."""
    w = h = 0
    for rec in layout_layers(rom, layout):
        if rec["at"] is None or rec["kind"] != "tilemap" or rec["scroll"] != (SCROLL_ONE, SCROLL_ONE):
            continue
        w, h = max(w, rec["blocks"][0] * 256), max(h, rec["blocks"][1] * 256)
    return w, h


def collision_bits(rom: bytes, layout: int) -> tuple:
    """(file offset, container type, bits) of the collision frame at layout +0x34.

    The frame is a 256 x 256 grid of 8 px cells: byte cy * 32 + (cx >> 3), bit cx & 7, SET = open
    (collision_test @0x08005D6C, bible tag CSV). The decoder lives in rom\\webfoot_decompress and is
    imported here lazily, so --table, --record and --find-text keep working while that package is edited.
    The one decoder: map_view draws the tint from these same bits."""
    from rom.webfoot_decompress import unpack_frame                  # noqa: PLC0415  (see the docstring)
    word = u32(rom, layout + L_COLLISION)
    if not is_pointer(word):
        return None, None, b""
    kind, _size, bits, _packed = unpack_frame(rom, word - S.ROM_BASE)
    return word - S.ROM_BASE, kind, bits


def is_open(bits: bytes, x: int, y: int) -> bool:
    """collision_test @0x08005D6C: byte cy * 32 + (cx >> 3), bit cx & 7, set = open, 8 px cells."""
    cx, cy = x >> 3, y >> 3
    return (0 <= cx < COLLISION_CELLS and 0 <= cy < COLLISION_CELLS
            and bool(bits[cy * COLLISION_STRIDE + (cx >> 3)] >> (cx & 7) & 1))


def collision(rom: bytes, layout: int) -> dict:
    """The collision frame with its container type and its open counts, inside and outside the bounds."""
    at, kind, bits = collision_bits(rom, layout)
    if at is None:
        return {"at": None, "word": u32(rom, layout + L_COLLISION)}
    w, h = map_bounds(rom, layout)
    inside = total = 0
    for cy in range(min(h // 8, COLLISION_CELLS)):
        for cx in range(min(w // 8, COLLISION_CELLS)):
            total += 1
            inside += bits[cy * COLLISION_STRIDE + (cx >> 3)] >> (cx & 7) & 1
    return {"at": at, "type": kind, "bytes": len(bits),
            "open": sum(bin(b).count("1") for b in bits), "cells": COLLISION_CELLS ** 2,
            "open_in_bounds": inside, "cells_in_bounds": total, "bounds": (w, h)}


# ===== the tile loader: layout +0x48 static stream and +0x0C animated groups =====

def rom_offset(rom: bytes, word: int, what: str) -> int:
    """The file offset of a ROM pointer, refusing anything that is not one.

    Python takes a negative offset from the END of the ROM, so an unchecked word reads plausible
    bytes from the wrong place in silence."""
    if not (is_pointer(word) and word - S.ROM_BASE < len(rom)):
        raise ValueError(f"the {what} word is 0x{word:08X}, not a pointer into this ROM")
    return word - S.ROM_BASE


def frame_at(rom: bytes, at: int) -> bytes:
    """The decoded bytes of a frame at a file OFFSET. The decoder is imported lazily, as in
    collision_bits, so --table, --record and --find-text keep working while that package is edited."""
    from rom.webfoot_decompress import unpack_frame                  # noqa: PLC0415  (see above)
    return unpack_frame(rom, at)[2]


def tile_pairs(payload: bytes) -> list:
    """The (chunk, tile) pair of every entry of a delta coded +0x48 payload, in load order.

    The payload is a u16 list, delta coded e[i] += e[i-1] + 1. The entry's high byte picks a chunk
    in the +0x4C table and its low byte a 64 byte tile inside it (Map_LoadLayer @0x080050C8, bible
    B1080 and B1098). An odd length is refused rather than truncated: the loader would drop the
    stray byte, so a truncating reader agrees with the game and still hides the real fault, which
    is a frame that is not a tile list at all."""
    if len(payload) % 2:
        raise ValueError(f"a {len(payload)} byte payload is not a whole u16 list")
    count = len(payload) // 2
    entries = list(struct.unpack(f"<{count}H", payload))
    for i in range(1, count):
        entries[i] = (entries[i] + entries[i - 1] + 1) & 0xFFFF
    return [(e >> 8, e & 0xFF) for e in entries]


def chunk_tiles(rom: bytes, pairs: list, table: int) -> list:
    """The 64 byte pixels of every pair, in load order. `table` is a chunk table file OFFSET.

    One chunk decode per chunk, as the loader does. A tile past the end of its chunk raises: no
    vanilla tile does it over all 336 base layouts, and a short slice would otherwise travel into a
    stream the editor writes and only show up as missing pixels in game."""
    chunks, out = {}, []
    for chunk, tile in pairs:
        if chunk not in chunks:
            chunks[chunk] = frame_at(rom, u32(rom, table + 4 * chunk) - S.ROM_BASE)
        pixels = chunks[chunk][TILE_BYTES * tile:TILE_BYTES * (tile + 1)]
        if len(pixels) != TILE_BYTES:
            raise ValueError(f"chunk {chunk} holds {len(chunks[chunk]) // TILE_BYTES} tiles, "
                             f"so tile {tile} runs past its end")
        out.append(pixels)
    return out


def static_tiles(rom: bytes, layout: int) -> list:
    """The +0x48 stream's tiles of a layout OFFSET. Stream position i is VRAM slot i."""
    pairs = tile_pairs(frame_at(rom, u32(rom, layout + L_TILE_STREAM) - S.ROM_BASE))
    return chunk_tiles(rom, pairs, u32(rom, layout + L_TILE_TABLE) - S.ROM_BASE)


def layout_groups(rom: bytes, layout: int) -> list:
    """Every animated tile group of a layout OFFSET, in list order, with its frames decoded.

    Sprite_LoadTiles @0x0800501E: +0x0C is the group count and +0x10 a list of u32 pointers, each
    to a header F. F+0 is the frame count, F+1 the TILE COUNT, F+2 the u16 DESTINATION SLOT and
    F+4 an array of u32 frame pointers. A frame is {u32 duration, compressed pixels}, which is why
    the handler adds 4 before it decompresses. The loader then DMAs count * 64 bytes to
    0x06000000 + slot * 64, the same VRAM the +0x48 stream fills, so a slot number here and a tile
    number in a BG cell are the one scale. List order is the tick offset: group k starts at
    countdown k + 1 (bible B1078)."""
    count, lst = u32(rom, layout + L_GROUP_COUNT), u32(rom, layout + L_GROUP_LIST)
    if not count or not is_pointer(lst):
        return []
    if count > GROUP_MAX:
        raise ValueError(f"the layout declares {count} animated groups, past the {GROUP_MAX} the "
                         f"state array holds, so the count word is not a count")
    from rom.webfoot_decompress import decompress                    # noqa: PLC0415  (see frame_at)
    out, table = [], rom_offset(rom, lst, "animated group list")
    for k in range(count):
        rec = rom_offset(rom, u32(rom, table + 4 * k), f"animated group {k}")
        frames, tiles, first = rom[rec], rom[rec + 1], struct.unpack_from("<H", rom, rec + 2)[0]
        payload = tiles * TILE_BYTES
        group = {"at": rec, "first": first, "tiles": tiles, "frames": []}
        for f in range(frames):
            at = rom_offset(rom, u32(rom, rec + 4 + 4 * f), f"animated group {k} frame {f}")
            pixels, _packed = decompress(rom, at + 4, limit=max(payload, 0x100))
            if len(pixels) != payload:
                raise ValueError(f"animated group {k} frame {f} decodes to {len(pixels)} bytes, "
                                 f"not the {payload} its {tiles} tiles need")
            group["frames"].append({"at": at, "duration": u32(rom, at), "pixels": pixels})
        out.append(group)
    return out


def loaded_tiles(rom: bytes, layout: int) -> list:
    """Every VRAM tile slot this layout fills, INDEXED BY SLOT, with b"" where nothing loads.

    The static stream fills slots 0 upward, then each animated group's FIRST frame fills
    [first, first + tiles), usually past the stream. A renderer that stopped at the stream drew
    nothing in every cell naming a group slot and showed the layer below: 509 such cells on the
    plateau, all of them false, measured 2026-11-07. The groups are laid in load order, so a group
    that overlaps the stream wins, as it does in play. Map 6,99 is the one vanilla layout that
    overlaps, with 5 groups over slots 1 to 49."""
    out = static_tiles(rom, layout)
    for group in layout_groups(rom, layout):
        pixels = group["frames"][0]["pixels"] if group["frames"] else b""
        end = group["first"] + group["tiles"]
        if end > len(out):
            out += [b""] * (end - len(out))
        for n in range(group["tiles"]):
            out[group["first"] + n] = pixels[TILE_BYTES * n:TILE_BYTES * (n + 1)]
    return out


# ===== the map reader =====

def _warp_tail(it: dict) -> str:
    return (f"-> map {it['to'][0]},{it['to'][1]} var {it['to'][2]} "
            f"at {it['landing']} facing {it['direction']}")


def _item_tail(it: dict) -> str:
    """What one decoded item points at, whichever list it came from."""
    if it["kind"] == "warp":
        return _warp_tail(it)
    if it["kind"] == "scene":
        return f"-> scene table rom:0x{it['table']:X}"
    if it["kind"] == "script":
        return f"-> script rom:0x{it['script']:X}"
    if it["kind"] == "talk":
        return f"set {it['set_id']} at {it['at_xy']} -> table rom:0x{it['table']:X}"
    if it["kind"] == "npc":
        return f"set {it['set_id']} at {it['at_xy']}, {it['steps']} walk step(s)"
    if it["kind"] == "group":
        tail = f" -> death table rom:0x{it['table']:X}" if "table" in it else " (no scene sub-struct)"
        return f"enemy type {it['enemy_type']} set {it['set_id']} at {it['at_xy']}{tail}"
    return ""


def _music(rom: bytes, word: int) -> str:
    """Entry +0x24 takes two forms: a literal song id in 230 maps and a SCRIPT pointer in 62 (bible OPS
    tag OPS). Zero is song 0, not silence, so a cloned map left at 0 cuts the track (bible ARN3)."""
    if word == 0:
        return "0, which is SONG 0 and not silence: a map left at 0 restarts the music"
    if is_pointer(word):
        return f"a SCRIPT at rom:0x{word - S.ROM_BASE:X} that computes the song id"
    return f"song id {word}"


def entry_lines(rom: bytes, at: int, index: int) -> list:
    """Every map entry field by name, with the byte count printed beside the word it counts."""
    counts = dict(ENTRY_BYTES)
    out = [f"  ENTRY FIELDS  rom:0x{at:X}, index {index}, 56 bytes",
           f"    +0x00 zone {rom[at]}   +0x01 area {rom[at + 1]}   "
           + "   ".join(f"+0x{off:02X} {name} {rom[at + off]}" for off, name in ENTRY_BYTES)]
    pairs = {0x10: 0x03, 0x14: 0x04, 0x18: 0x05, 0x1C: 0x06, 0x20: 0x07}
    for off, name in ENTRY_WORDS:
        word = u32(rom, at + off)
        if off == 0x24:
            out.append(f"    +0x24 music          {_music(rom, word)}")
            continue
        if off == 0x0C:
            # +0x0C takes TWO forms, exactly as +0x24 does: 313 of 327 maps hold a literal name index
            # and 14 hold a SCRIPT that picks one of two indices on a flag. Reading the pointer as an
            # index is what made map 9,1's banner read as 64, an item name (bible tag LAB).
            out.append("    +0x0C banner         " + (
                f"a SCRIPT at rom:0x{word - S.ROM_BASE:X} that picks the name index on a flag"
                if is_pointer(word) else
                f"index {word} into the name pool rom:0x{BANNER_POOL:X}"))
            continue
        if off == 0x08:
            out.append(f"    +0x08 combat         {word}"
                       + ("  (the player may attack here)" if word else "  (no attacking here)"))
            continue
        value = f"rom:0x{word - S.ROM_BASE:X}" if is_pointer(word) else f"0x{word:X}"
        tail = ""
        if off in pairs:
            n = rom[at + pairs[off]]
            tail = f"   counted by +0x{pairs[off]:02X} = {n}"
            if bool(n) != is_pointer(word):
                tail += "   MISMATCH: the count and the list word disagree"
        out.append(f"    +0x{off:02X} {name:<14} {value}{tail}")
    return out


def region_lines(rom: bytes, info: dict) -> list:
    """DOOR CARRIER A. Every region of the entry +0x10 list, with the warps called warps and nothing else
    called a warp. This carrier holds only 69 of the game's 655 doors (bible tag OPS)."""
    warps = [it for _c, it in info["regions"] if it["kind"] == "warp"]
    out = [f"  DOOR CARRIER A, the REGION list (entry +0x10): {len(info['regions'])} region(s), "
           f"{len(warps)} of them door(s)"]
    if not info["regions"]:
        out.append("    (empty. An empty region list removes the EXITS, the save point and the world map "
                   "entry, and says nothing about the walls: bible tag ARN)")
    for n, (cond, it) in enumerate(info["regions"]):
        label = "DOOR" if it["kind"] == "warp" else it["kind"]
        out.append(f"    region {n:2d}  rom:0x{it['at']:X}  cond 0x{cond:08X}  {label:<7} "
                   f"rect {it['rect']}  {_item_tail(it)}".rstrip())
    return out


def door_lines(rom: bytes, lay: int) -> list:
    """DOOR CARRIER B. The layout's own door list, the carrier that holds the other 586 doors."""
    d = layout_doors(rom, lay)
    where = f"rom:0x{d['list'] - S.ROM_BASE:X}" if is_pointer(d["list"]) else f"0x{d['list']:X}"
    out = [f"  DOOR CARRIER B, the LAYOUT door list (layout +0x40 count, +0x44 list): "
           f"+0x40 says {d['count']}, {len(d['doors'])} decoded as doors, list {where}"]
    if d["count"] and not is_pointer(d["list"]):
        out.append("    MISMATCH: the count is not zero and the list word is not a pointer")
    if len(d["doors"]) != d["count"]:
        out.append(f"    MISMATCH: {d['count'] - len(d['doors'])} listed word(s) did not decode as a warp "
                   f"item: {d['not_a_warp']}")
    if not d["count"]:
        out.append("    (empty. 44 of the 327 vanilla maps carry no layout door list: bible tag WRP)")
    for n, it in enumerate(d["doors"]):
        out.append(f"    door   {n:2d}  rom:0x{it['at']:X}  factory @0x{it['factory']:08X}  "
                   f"rect {it['rect']}  {_warp_tail(it)}")
    return out


def item_lines(rom: bytes, info: dict) -> list:
    """The entry +0x14 spawn item list. A warp here would be a THIRD place a door can hide, so it is
    called out rather than listed quietly."""
    warps = [it for it in info["items"] if it["kind"] == "warp"]
    out = [f"  ITEM list (entry +0x14): {len(info['items'])} item(s) of a declared {info['count']}"]
    if warps:
        out.append(f"    NOTE: {len(warps)} item(s) in this list decode as WARPS, so this map carries "
                   f"doors in a third place. Read them as doors.")
    for n, it in enumerate(info["items"]):
        shape = f"  rect {it['rect']}" if it["kind"] in ("warp", "scene", "script") else ""
        out.append(f"    item   {n:2d}  rom:0x{it['at']:X}  factory @0x{it['factory']:08X}  "
                   f"{it['kind']}{shape}  {_item_tail(it)}".rstrip())
    return out


def chain_lines(rom: bytes, rom_entry: int, var: int) -> list:
    """The layout chain: entry +0x2C is an array of layout pointers indexed by variation - 1."""
    chain = layouts(rom, rom_entry)
    array = u32(rom, rom_entry + 0x2C)
    out = [f"  LAYOUT CHAIN  entry +0x2C -> array "
           + (f"rom:0x{array - S.ROM_BASE:X}" if is_pointer(array) else f"0x{array:X}")
           + f", {len(chain)} variation(s)"]
    for n, lay in enumerate(chain, start=1):
        mark = " <- read below" if n == var else ""
        out.append(f"    var {n}: " + (f"layout rom:0x{lay:X}" if lay is not None else "no layout") + mark)
    return out


def layout_lines(rom: bytes, rom_entry: int, var: int) -> list:
    """The props, the collision and the BG layers of one variation's layout."""
    chain = layouts(rom, rom_entry)
    if not chain or var > len(chain) or chain[var - 1] is None:
        return [f"  variation {var} has no layout, so there are no props, collision or BG layers to read"]
    lay = chain[var - 1]
    out = []
    props = layout_props(rom, lay)
    sheet = u32(rom, lay + L_PROP_SHEET)
    out.append(f"  PROPS (layout +0x24 count, +0x28 list, +0x2C sheet frame "
               + (f"rom:0x{sheet - S.ROM_BASE:X}" if is_pointer(sheet) else f"0x{sheet:X}")
               + f"): {len(props)}")
    out.append("    (layout +0x2C is the prop SHEET. The entry's +0x2C is the layout array. "
               "The two offsets collide and are different fields.)")
    for n, p in enumerate(props):
        out.append(f"    prop   {n:2d}  rom:0x{p['at']:X}  rect {p['rect']}  tile 0x{p['tile']:X}  "
                   f"priority {p['priority']}  attr 0x{p['attr0']:04X}/0x{p['attr1']:04X}")

    c = collision(rom, lay)
    out.append("")
    if c["at"] is None:
        out.append(f"  COLLISION (layout +0x34): no frame, the word is 0x{c['word']:X}")
    else:
        out.append(f"  COLLISION (layout +0x34): frame rom:0x{c['at']:X}, container type {c['type']} "
                   f"({'raw' if c['type'] == 0 else 'compressed'}), {c['bytes']} bytes")
        out.append(f"    {c['open']} of {c['cells']} cells open in the whole 256x256 grid")
        # Maps 1,7 and 6,99 carry no scroll-1.0 layer, so there is no world extent to count inside.
        out.append(f"    {c['open_in_bounds']} of {c['cells_in_bounds']} open inside the map bounds "
                   f"{c['bounds'][0]}x{c['bounds'][1]} px" if all(c["bounds"]) else
                   "    no scroll-1.0 BG layer, so this map has no block-grid bounds to count inside")

    out.append("")
    out.append("  BG LAYERS (layout +0x14, +0x18, +0x1C, +0x20). +4 and +8 are a SCROLL FACTOR, "
               "0x400 = 1.0, not a size.")
    for rec in layout_layers(rom, lay):
        if rec["at"] is None:
            out.append(f"    bg{rec['bg']}  no record, the word is 0x{rec['word']:X}")
            continue
        # Only a tilemap record's +0x14 and +0x15 are block counts. The overlay class is a wrapping
        # 256x256 pattern, and an unknown class is the world map's own, whose fields are not read here.
        size = {"tilemap": (f"blocks {rec['blocks'][0]} x {rec['blocks'][1]} = "
                            f"{rec['blocks'][0] * 256}x{rec['blocks'][1] * 256} px"),
                "overlay": "a wrapping 256x256 pattern, so it carries no block grid and no size",
                }.get(rec["kind"], "this class is not decoded here, so its fields above are raw words")
        out.append(f"    bg{rec['bg']}  rom:0x{rec['at']:X}  class 0x{rec['class']:08X} {rec['kind']}  "
                   f"scroll 0x{rec['scroll'][0]:X}/0x{rec['scroll'][1]:X}  "
                   f"offset 0x{rec['offset'][0]:X}/0x{rec['offset'][1]:X}  {size}")

    # A group usually sits PAST the static stream, so a cell may name a slot the stream never
    # reaches and still be sound. A reader that printed the stream alone invited that cell to be
    # read as a hole, which is how our renderer came to draw 509 false cells on the plateau.
    out.append("")
    static = len(tile_pairs(frame_at(rom, u32(rom, lay + L_TILE_STREAM) - S.ROM_BASE)))
    out.append(f"  TILES (layout +0x48 stream, +0x4C chunk table "
               f"rom:0x{u32(rom, lay + L_TILE_TABLE) - S.ROM_BASE:X}): {static} static tiles, "
               f"slots 0 to {static - 1} of the {TILE_BUDGET} slot budget")
    groups = layout_groups(rom, lay)
    out.append(f"  ANIMATED TILE GROUPS (layout +0x0C count, +0x10 list): {len(groups)}")
    for n, g in enumerate(groups):
        out.append(f"    group {n}  rom:0x{g['at']:X}  {g['tiles']} tile(s) to slots {g['first']} "
                   f"to {g['first'] + g['tiles'] - 1}  {len(g['frames'])} frame(s), durations "
                   f"{[f['duration'] for f in g['frames']]}")
    return out


def show_map(rom: bytes, zone: int, area: int, var: int = 1) -> list:
    """One map end to end: the entry fields by name, the layout chain, BOTH door carriers side by side,
    the item list, the props, the collision frame and the BG layer records.

    The two door carriers are printed as carrier A and carrier B and never merged, because the arena
    shipped three times carrying doors nobody could see: the region list was empty and the layout list
    it inherited was not."""
    index, at = map_entry(rom, zone, area)
    info = map_items(rom, zone, area)
    chain = layouts(rom, at)
    lay = chain[var - 1] if chain and var <= len(chain) else None
    out = [f"map {zone},{area}  variation {var}", ""] + entry_lines(rom, at, index) + [""]
    out += chain_lines(rom, at, var) + [""]
    # The two carriers are printed one after the other, with nothing between them, so a reader who sees
    # carrier A empty cannot stop reading before carrier B. That is the arena mistake, three times over.
    out += region_lines(rom, info) + [""]
    out += (door_lines(rom, lay) if lay is not None else ["  DOOR CARRIER B: no layout, so no door list"])
    out += [""] + item_lines(rom, info) + [""]
    out += layout_lines(rom, at, var) + [""]

    region_doors = sum(1 for _c, it in info["regions"] if it["kind"] == "warp")
    item_doors = sum(1 for it in info["items"] if it["kind"] == "warp")
    lay_doors = len(layout_doors(rom, lay)["doors"]) if lay is not None else 0
    out.append(f"  DOORS IN ALL: {region_doors + lay_doors + item_doors}  "
               f"({region_doors} region, {lay_doors} layout, {item_doors} item)")
    out.append("  This is a FLOOR on the ways in. A map entered by a script ext 35, 38 or 39 has no "
               "door in any carrier, so a count of 0 does not prove a map is sealed to scripts.")
    if not info["regions"] and not info["items"]:
        out.append("  No region list and no item list. A scene owned through the +0x14 group factory "
                   "@0x0800E77F sub-struct would not appear here (bible SS3).")
    return out


# ===== find text =====

def find_text(rom: bytes, needle: str, lo: int = SCRIPT_REGION[0], hi: int = SCRIPT_REGION[1]) -> list:
    """Every record whose ASCII holds needle, with the words that name it."""
    want, out, at = needle.encode("ascii"), [], lo
    while True:
        at = rom.find(want, at, hi)
        if at < 0:
            return out
        rec = _header_before(rom, at)
        namers = S.words_naming(rom, rec, lo, hi) if rec is not None else []
        out.append({"text_at": at, "record": rec,
                    "kind": rom[rec + 2] if rec is not None else None, "namers": namers})
        at += 1


def _header_before(rom: bytes, at: int, window: int = 400) -> int:
    """The type 1 record header that owns the text at at, or None.

    It scans back for the nearest {next, 0, 1, portrait} whose text reaches the hit with printable bytes
    only. A plain backward scan for a NUL is wrong: a line can open with a control byte such as '#' or '@',
    so the NUL before it belongs to the previous record."""
    for rec in range(at - 4, max(at - window, 0) - 1, -1):
        if rom[rec + 1] != 0 or rom[rec + 2] != S.TYPE_TEXT:
            continue
        body = rom[rec + 4:at]
        if all(b == 0x0B or 0x20 <= b < 0x7F or b in (0x23, 0x40, 0x5E) for b in body):
            return rec
    return None


def show_find(rom: bytes, needle: str) -> list:
    hits = find_text(rom, needle)
    out = [f'"{needle}": {len(hits)} hit(s) in rom:0x{SCRIPT_REGION[0]:X}-0x{SCRIPT_REGION[1]:X}']
    for h in hits:
        if h["record"] is None:
            out.append(f"  rom:0x{h['text_at']:X}  text, but the 4 bytes before it are not a type 1 header "
                       f"(type byte {h['kind']}). It may sit inside a type 2 stream or another payload.")
            continue
        out += ["  " + line for line in show_record(rom, h["record"])]
        if h["namers"]:
            out.append("    named by " + ", ".join(f"rom:0x{w:X}" for w in h["namers"]))
        else:
            out.append("    no aligned word names this record in the script region. A table word outside "
                       "the region, or a run-time index, would not show.")
    return out


# ===== CLI =====

def _main(argv: list) -> None:
    rom_path, action, arg, count, length, var = BASE, None, None, None, None, 1
    while argv:
        a = argv.pop(0)
        if a == "--rom":
            rom_path = Path(argv.pop(0))
        elif a == "--count":
            count = int(argv.pop(0), 0)
        elif a == "--len":
            length = int(argv.pop(0), 0)
        elif a == "--var":
            var = int(argv.pop(0), 0)
        elif a in ("--table", "--record", "--map", "--find-text"):
            action, arg = a, argv.pop(0)
        else:
            raise SystemExit(f"unknown argument {a}\n{__doc__}")
    if not action:
        raise SystemExit(__doc__)
    rom = rom_path.read_bytes()
    if action == "--table":
        lines = show_table(rom, int(arg, 0), count)
    elif action == "--record":
        lines = show_record(rom, int(arg, 0), length)
    elif action == "--map":
        zone, area = (int(v) for v in arg.split(","))
        lines = show_map(rom, zone, area, var)
    else:
        lines = show_find(rom, arg)
    print("\n".join(lines))


if __name__ == "__main__":
    _main(sys.argv[1:])
