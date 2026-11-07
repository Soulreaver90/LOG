r"""
import_map.py - Turn a saved map document into a real map entry, appended to a ROM.

Usage:   py -3.14 -P scripts\permanent\map-editor\import_map.py --rom <a build .gba>
             --doc <a map .json> --zone 7 --area 101 --out <a new .gba>
         As a module: sys.path must hold scripts\permanent\map-editor (the folder name has a
         hyphen, so it is not an importable package), then `import import_map`.
         apply(rom, doc, zone, area) -> a NEW rom; the rom passed in is never changed.
Input:   a 16 MB ROM, which is what log2_build produces. The 8 MB base is refused: it has no
         expansion area, so there is nowhere to put the map. Build first.
Writes:  new data into the free tail of the expansion area rom:0x800000-0xEFFFFF, then FIVE
         hand-off sites in the base: the three map table literals rom:0x5ADC, rom:0x5D5C and
         rom:0xEBD8, the map entry 3 literal rom:0x195C, and the map count byte rom:0xE0AE.
         Those five are the same hand-off battle_arena, future_androids and plateau use, which is
         how each relocation passes the table on. Every other byte it writes was 0xFF.
Reads:   the LIVE table base from rom:0xEBD8 and the LIVE count from rom:0xE0AE, so it composes
         with a build whose table has already moved. A constant here would read a dead table and
         still find 327 plausible entries.

CAMERA, the rule this module exists to enforce. The layout +0x08 and +0x0A words are
         `world - 239` and `world - 159` (`Scene_BuildLayers` @0x08006152). They are COMPUTED from
         the document's `world` and never inherited: the plateau shipped its donor map's 449 on a
         1024 px wide world and the camera stopped 170 px short of walkable ground, which every
         full-map render showed as correct. A document that carries a `camera` or `clamp` key
         disagreeing with its own world is refused rather than obeyed.
GRID:    one `blocks` pair rules every BG layer, so layers cannot disagree. map_file.validate is
         run first and any problem raises, so nothing is written for a document the game would
         refuse: over the 896 tile budget, a layer whose cell count is not the grid, open ground
         the camera cannot reach.
COUNT:   the map count is one byte of code at rom:0xE0AE, read as 0xFF + that byte, so the table
         holds at most 509 entries. Appending past that fails closed, before any table walk: past
         the real entries the walk reads garbage and would raise for the wrong reason.
LAYOUT:  the struct is 0x50 bytes. Measured over all 336 vanilla layouts: every one has a ROM word
         naming its +0x50, where the next structure starts (192 a frame header, 137 a BG layer
         record). plateau.py copies 0xCC, which carries 0x7C bytes of its donor's neighbour along.
         The layout is built from zeros here, never copied, because a copy is how a donor's camera
         pair, props and doors travel into a new map.
TILES:   the +0x4C chunk table is the shared pool `tile_stream.CHUNK_TABLE`, and every (chunk, tile)
         pair is resolved through it in the TARGET rom before a byte is written. A document does not
         record which table its pairs index, so a map read from a build that gave itself a private
         chunk table would resolve to the wrong pixels here. Pass `chunk_table` to name another one.
Entry:   56 bytes built from zeros: no region, item, swap, pickup or marker list, and no enter,
         leave or variation script. Music, the banner and combat are not in the document by design
         (the owner: "no music or name"), so they are keyword arguments with the arena's values.
Rules:   never writes under data\, never overwrites a ROM, and never changes the rom it is given.
"""
import argparse
import struct
import sys
from pathlib import Path

for _folder in (Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
    sys.path.insert(0, str(_folder))              # -P omits the script folder; scene\ is one up

from rom.webfoot_decompress import decompress                          # noqa: E402
from rom.webfoot_lz_pack import pack                                   # noqa: E402
from scene import map_view                                             # noqa: E402
from scene import scene_probe                                          # noqa: E402
from scene.scene_lib import words_naming                               # noqa: E402
import map_file                                                        # noqa: E402
import tile_stream                                                     # noqa: E402

# ===== CONFIG: the ROM shape log2_build produces =====
ROM_BASE = map_view.ROM_BASE
ROM_SIZE = 0x1000000                        # 16 MB: base, 0xFF fill, then patches
ALLOC_REGION = (0x800000, 0xF00000)         # the expansion area; art_inject owns 0xF00000 and up

# ===== CONFIG: the map table, read LIVE =====
MAP_SIZE = 56
MAP_BASE_LITERAL, MAP_COUNT_BYTE = 0xEBD8, 0xE0AE
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)    # the 3 words that name the table base
ENTRY3, ENTRY3_LITERAL = 3, 0x195C          # one literal names map entry 3 directly
COUNT_FN = 0xE0AC
COUNT_CODE_HEAD, COUNT_CODE_TAIL = bytes.fromhex("ff20"), bytes.fromhex("307047")
MAP_COUNT_CAP = 0xFF + 0xFE                 # the count byte is one byte: 509 entries

# Map entry, 56 bytes (bible tag OVW and 1312).
F_ZONE, F_AREA, F_VARIATIONS = 0x00, 0x01, 0x02
F_COMBAT, F_BANNER, F_MUSIC, F_LAYOUTS = 0x08, 0x0C, 0x24, 0x2C

# Layout, 0x50 bytes.
L_BLEND, L_ALPHA, L_PRIORITY, L_CAMERA = 0x00, 0x02, 0x04, 0x08
L_GROUP_COUNT, L_GROUP_LIST = 0x0C, 0x10
L_LAYERS = (0x14, 0x18, 0x1C, 0x20)         # BG0 to BG3 records
L_PROP_COUNT, L_PROP_LIST, L_PROP_SHEET = 0x24, 0x28, 0x2C
L_UNREAD_30, L_COLLISION, L_TERRAIN, L_UNREAD_3C = 0x30, 0x34, 0x38, 0x3C
L_DOOR_COUNT, L_DOOR_LIST = 0x40, 0x44
L_TILE_STREAM, L_TILE_TABLE = 0x48, 0x4C
LAYOUT_SIZE = 0x50

# A BG layer record: class, two scroll words, two offset words, the grid, then one word per block.
LAYER_CLASS = 0x080056A1
LAYER_GRID, LAYER_HEAD = 0x14, 0x18
BLOCK_TILES = map_file.BLOCK_TILES
BLOCK_BYTES = map_file.BLOCK_BYTES
TILE_BYTES = map_file.TILE_BYTES

# The fields the document does not carry, because the editor does not set them.
DEFAULT_MUSIC, DEFAULT_BANNER, DEFAULT_COMBAT = 38, 0xDD, 1
VARIATIONS = 1
CAMERA_KEYS = ("camera", "clamp")           # schema 1 carries neither; one that does is checked


# ===== small helpers =====

def _word(value: int) -> bytes:
    return struct.pack("<I", value)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytes, off: int, want: bytes, what: str) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"{what} rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, "
                         f"expected {want.hex()}")


def _packed_frame(payload: bytes) -> bytes:
    """A {u32 type, u32 size} frame, checked by decoding it back. plateau.py does the same."""
    out = pack(payload, kind=1)
    if decompress(out, 8)[0] != payload or len(out) % 4:
        raise ValueError(f"the packed frame does not round trip, or is not 4 aligned "
                         f"({len(out)} bytes)")
    return out


def _bare_stream(payload: bytes) -> bytes:
    """A codec stream with no frame header: an animated group frame holds one, 4 bytes in.

    `Sprite_LoadTiles` @0x0800501E decompresses at frame + 4, past the duration word, so this
    payload must start at the stream itself and not at a frame header (bible B1078)."""
    out = pack(payload, kind=1)[8:]
    if decompress(out, 0)[0] != payload or len(out) % 4:
        raise ValueError(f"the group stream does not round trip, or is not 4 aligned "
                         f"({len(out)} bytes)")
    return out


def map_table(rom: bytes) -> tuple:
    """(file offset, entry count) of THIS rom's map table, from its own literal and count byte."""
    return _u32(rom, MAP_BASE_LITERAL) - ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]


# ===== free space =====

def free_from(rom: bytes) -> int:
    """The first 4-aligned offset in the expansion area with nothing but 0xFF above it.

    Patches bump upward from rom:0x800000, so the tail is free. Starting after the LAST non-fill
    byte wastes any hole a patch left and can never land on one, which is the safe direction."""
    start, end = ALLOC_REGION
    used = len(bytes(rom[start:end]).rstrip(b"\xFF"))
    return start + ((used + 3) & ~3)


class _Bump:
    """Hands out free space above everything a build already wrote. One per apply() call."""

    def __init__(self, rom: bytes):
        self.at = free_from(rom)

    def __call__(self, size: int, align: int = 4) -> int:
        at = -(-self.at // align) * align
        if at + size > ALLOC_REGION[1]:
            raise MemoryError(f"the expansion area has no room for 0x{size:X} more bytes "
                              f"(free from rom:0x{at:X} to rom:0x{ALLOC_REGION[1]:X})")
        self.at = at + size
        return at


# ===== checks, all of them before the first write =====

def _check_document(doc: dict) -> tuple:
    """The document's own problems, then its camera pair. Returns the computed pair."""
    problems = map_file.validate(doc)
    if problems:
        raise ValueError("this document is not sound, so no map was written:\n  "
                         + "\n  ".join(problems))
    pair = map_file.camera_pair(*doc["world"])
    for key in CAMERA_KEYS:
        stored = doc.get(key)
        if stored is not None and tuple(stored) != pair:
            raise ValueError(f"the document carries {key} {tuple(stored)}, and a "
                             f"{doc['world'][0]} x {doc['world'][1]} px world is {pair}. A pair "
                             f"copied from another map is the fault that stopped the plateau's "
                             f"camera 170 px short of walkable ground")
    return pair


def _check_rom(rom: bytes, zone: int, area: int) -> tuple:
    """The live table, checked the way every relocating module checks it. Returns (table, count)."""
    if len(rom) != ROM_SIZE:
        raise ValueError(f"this ROM is 0x{len(rom):X} bytes and a map needs the 0x{ROM_SIZE:X} byte "
                         f"shape with an expansion area: build it first with log2_build.py")
    if not (0 <= zone <= 0xFF and 0 <= area <= 0xFF):
        raise ValueError(f"map {zone},{area}: a zone and an area are each one byte")
    count = 0xFF + rom[MAP_COUNT_BYTE]
    if count >= MAP_COUNT_CAP:
        raise ValueError(f"the map count byte rom:0x{MAP_COUNT_BYTE:X} is "
                         f"0x{rom[MAP_COUNT_BYTE]:02X}, so the table already holds {count} entries "
                         f"and the byte cannot name one more: the cap is {MAP_COUNT_CAP}")
    _expect(rom, COUNT_FN, COUNT_CODE_HEAD, "the map count getter")
    _expect(rom, MAP_COUNT_BYTE + 1, COUNT_CODE_TAIL, "the map count getter")

    table = _u32(rom, MAP_BASE_LITERAL) - ROM_BASE
    for literal in BASE_LITERALS:
        _expect(rom, literal, _word(table + ROM_BASE), "the map table literal")
    _expect(rom, ENTRY3_LITERAL, _word(table + MAP_SIZE * ENTRY3 + ROM_BASE),
            f"the map entry {ENTRY3} literal")
    named = words_naming(rom, table)
    if named != list(BASE_LITERALS):
        raise ValueError(f"the live map table base rom:0x{table:X} is named by "
                         f"{[hex(w) for w in named]}, and this module moves "
                         f"{[hex(w) for w in BASE_LITERALS]}")

    pairs = [(rom[table + MAP_SIZE * k], rom[table + MAP_SIZE * k + 1]) for k in range(count)]
    if len(set(pairs)) != count:
        raise ValueError(f"(zone, area) is not unique across the {count} live map entries")
    if (zone, area) in pairs:
        raise ValueError(f"this ROM already holds map {zone},{area}")
    return table, count


# ===== the pieces a map is made of =====

def blocks_of(cells: list, blocks: tuple) -> list:
    """One layer's cells cut into 32 x 32 tile blocks, in the order a layer record names them.

    Block k draws at ((k % bw) * 256, (k // bw) * 256) px, which is the mapping map_file._cells
    reads back, so a block written here lands where it was composed."""
    bw, bh = blocks
    across = bw * BLOCK_TILES
    out = []
    for k in range(bw * bh):
        ox, oy = (k % bw) * BLOCK_TILES, (k // bw) * BLOCK_TILES
        entries = []
        for row in range(BLOCK_TILES):
            start = (oy + row) * across + ox
            entries += cells[start:start + BLOCK_TILES]
        out.append(struct.pack(f"<{BLOCK_TILES * BLOCK_TILES}H", *entries))
    return out


def layer_record(layer: dict, blocks: tuple, block_at: list) -> bytes:
    """A BG layer record: the tilemap class, the scroll and offset the document kept, then blocks.

    Scroll and offset are carried, not defaulted. 21 vanilla layers scroll at something other than
    1.0 and 364 carry a nonzero offset, so a defaulted 1:1 layer looks right in a full-map render
    and is wrong the moment the camera moves."""
    out = bytearray(LAYER_HEAD)
    struct.pack_into("<IIIII", out, 0, LAYER_CLASS,
                     layer["scroll"][0], layer["scroll"][1],
                     layer["offset"][0], layer["offset"][1])
    out[LAYER_GRID], out[LAYER_GRID + 1] = blocks
    for at in block_at:
        out += _word(at + ROM_BASE)
    return bytes(out)


def group_frame(frame: dict) -> bytes:
    """One animated frame: its duration word, then the bare stream the loader decodes at frame + 4."""
    return _word(frame["duration"]) + _bare_stream(bytes(frame["pixels"]))


def group_header(group: dict, frame_at: list) -> bytes:
    """A group header: u8 frame count, u8 tile count, u16 destination slot, then frame pointers."""
    return (bytes([len(frame_at), map_file.group_tiles(group)])
            + struct.pack("<H", group["first"])
            + b"".join(_word(at + ROM_BASE) for at in frame_at))


def map_entry(zone: int, area: int, layouts_at: int, music: int, banner: int,
              combat: int) -> bytes:
    """A 56 byte map entry built from zeros: one variation, one layout, and no list of any kind."""
    entry = bytearray(MAP_SIZE)
    entry[F_ZONE], entry[F_AREA], entry[F_VARIATIONS] = zone, area, VARIATIONS
    struct.pack_into("<I", entry, F_COMBAT, combat)
    struct.pack_into("<I", entry, F_BANNER, banner)
    struct.pack_into("<I", entry, F_MUSIC, music)
    struct.pack_into("<I", entry, F_LAYOUTS, layouts_at + ROM_BASE)
    return bytes(entry)


def layout_struct(doc: dict, pair: tuple, at: dict) -> bytes:
    """The 0x50 byte layout. The camera pair is the computed one, and props and doors are empty."""
    blend = doc.get("blend") or {}
    unread = doc.get("unread") or {}
    out = bytearray(LAYOUT_SIZE)
    struct.pack_into("<H", out, L_BLEND, blend.get("bldcnt", 0))
    out[L_ALPHA], out[L_ALPHA + 1] = blend.get("alpha", (0, 0))
    for bg, name in enumerate(map_file.LAYER_NAMES):
        layer = doc["layers"].get(name)
        out[L_PRIORITY + bg] = (layer or {}).get("priority", map_file.NEW_MAP_PRIORITY)
        if name in at["layers"]:
            struct.pack_into("<I", out, L_LAYERS[bg], at["layers"][name] + ROM_BASE)
    struct.pack_into("<HH", out, L_CAMERA, *pair)
    struct.pack_into("<I", out, L_GROUP_COUNT, len(doc.get("animated") or []))
    if at["group_list"] is not None:
        struct.pack_into("<I", out, L_GROUP_LIST, at["group_list"] + ROM_BASE)
    struct.pack_into("<I", out, L_UNREAD_30, unread.get("0x30", 0))
    struct.pack_into("<I", out, L_COLLISION, at["collision"] + ROM_BASE)
    struct.pack_into("<I", out, L_TERRAIN, at["terrain"] + ROM_BASE)
    struct.pack_into("<I", out, L_UNREAD_3C, unread.get("0x3C", 0))
    struct.pack_into("<I", out, L_TILE_STREAM, at["tiles"] + ROM_BASE)
    struct.pack_into("<I", out, L_TILE_TABLE, at["chunk_table"])
    return bytes(out)


# ===== apply =====

def apply(rom: bytes, doc: dict, zone: int, area: int, *,
          music: int = DEFAULT_MUSIC, banner: int = DEFAULT_BANNER, combat: int = DEFAULT_COMBAT,
          chunk_table: int = None, alloc=None, sites: list = None) -> bytes:
    """A NEW rom with this document appended as map zone,area. The rom given is never changed.

    `alloc(size, align=4) -> file offset` lets a build-list wrapper hand in the build's own
    Allocator, so a later module in the same build cannot allocate over this map. Without it the
    module bumps from the free tail of the expansion area.
    `sites` is filled with every (offset, length, name) written, for a caller that reports them."""
    pair = _check_document(doc)
    table, count = _check_rom(rom, zone, area)
    out = bytearray(rom)
    place_at = alloc or _Bump(rom)
    sites = [] if sites is None else sites

    def place(data: bytes, name: str) -> int:
        at = place_at(len(data))
        if set(out[at:at + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(data):X} bytes, {name}) is not free")
        out[at:at + len(data)] = data
        sites.append((at, len(data), name))
        return at

    def put(at: int, data: bytes, name: str) -> None:
        out[at:at + len(data)] = data
        sites.append((at, len(data), name))

    table_word = tile_stream.CHUNK_TABLE if chunk_table is None else chunk_table
    pairs = [tuple(p) for p in doc["tiles"]]
    scene_probe.chunk_tiles(rom, pairs, table_word - ROM_BASE)      # every pair must resolve here

    # One frame per DISTINCT block: a blank layer is 20 pointers at one frame, not 20 frames.
    frames, at = {}, {"layers": {}, "group_list": None, "chunk_table": table_word}

    def frame_for(payload: bytes, name: str) -> int:
        if payload not in frames:
            frames[payload] = place(_packed_frame(payload), name)
        return frames[payload]

    blocks = tuple(doc["blocks"])
    for name, layer in doc["layers"].items():
        block_at = [frame_for(payload, f"{name} block {k}")
                    for k, payload in enumerate(blocks_of(layer["cells"], blocks))]
        at["layers"][name] = place(layer_record(layer, blocks, block_at),
                                   f"the {name} record ({blocks[0]}x{blocks[1]} blocks)")

    at["collision"] = place(_packed_frame(bytes(doc["collision"])), "the collision frame")
    at["terrain"] = place(_packed_frame(bytes(doc["terrain"])), "the terrain frame")
    at["tiles"] = place(_packed_frame(tile_stream.encode_stream(pairs)),
                        f"the tile stream ({len(pairs)} tiles)")

    if doc.get("animated"):
        headers = []
        for k, group in enumerate(doc["animated"]):
            frame_at = [place(group_frame(f), f"animated group {k} frame {n}")
                        for n, f in enumerate(group["frames"])]
            headers.append(place(group_header(group, frame_at), f"animated group {k}"))
        at["group_list"] = place(b"".join(_word(h + ROM_BASE) for h in headers),
                                 f"the animated group list ({len(headers)} groups)")

    layout = place(layout_struct(doc, pair, at), f"the layout (camera pair {pair})")
    layouts = place(_word(layout + ROM_BASE), f"the layout array ({VARIATIONS} variation)")
    entry = map_entry(zone, area, layouts, music, banner, combat)
    new_table = place(bytes(rom[table:table + MAP_SIZE * count]) + entry,
                      f"the map table copy ({count + 1} entries)")

    for literal in BASE_LITERALS:
        put(literal, _word(new_table + ROM_BASE), f"map table literal rom:0x{literal:X}")
    put(ENTRY3_LITERAL, _word(new_table + MAP_SIZE * ENTRY3 + ROM_BASE),
        f"map entry {ENTRY3} literal")
    put(MAP_COUNT_BYTE, bytes([rom[MAP_COUNT_BYTE] + 1]),
        f"map count getter: {count} becomes {count + 1}")

    sites.sort()
    return bytes(out)


# ===== command line =====

def _main(argv: list) -> None:
    ap = argparse.ArgumentParser(description="Append a saved map document to a ROM as a new map.")
    ap.add_argument("--rom", required=True, help="a 16 MB build to read")
    ap.add_argument("--doc", required=True, help="a map document saved by the editor")
    ap.add_argument("--zone", required=True, type=int)
    ap.add_argument("--area", required=True, type=int)
    ap.add_argument("--out", required=True, help="the new ROM to create; it may not exist")
    ap.add_argument("--music", type=int, default=DEFAULT_MUSIC)
    ap.add_argument("--banner", type=int, default=DEFAULT_BANNER)
    ap.add_argument("--combat", type=int, default=DEFAULT_COMBAT)
    args = ap.parse_args(argv)

    out = Path(args.out).resolve()
    if "data" in (part.lower() for part in out.parts):
        raise ValueError(f"{out} is under a data folder, and nothing here writes there")
    sites = []
    rom = apply(Path(args.rom).read_bytes(), map_file.load(Path(args.doc)), args.zone, args.area,
                music=args.music, banner=args.banner, combat=args.combat, sites=sites)
    with open(out, "xb") as handle:             # "xb": never overwrite a ROM
        handle.write(rom)
    table, count = map_table(rom)
    print(f"map {args.zone},{args.area} appended: table rom:0x{table:X}, {count} entries")
    for site, size, name in sites:
        print(f"  rom:0x{site:06X} 0x{size:X} bytes  {name}")
    print(f"wrote {out}")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import log2_build                                             # noqa: PLC0415 (CLI only)
    log2_build.pair_save(out)
    print("no door and no script reach this map yet: a patch module has to lead the player to it")


if __name__ == "__main__":
    _main(sys.argv[1:])
