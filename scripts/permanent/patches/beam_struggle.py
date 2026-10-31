r"""
beam_struggle.py - Trial patch: the grand beam struggle of mockup v2 (final, 2026-10-25 4:22 PM: "Beam struggle mockup
                   is so much better! Go with the map tiles.") as BG0 tile art of map 14,4, the final Cell scene.

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_beam.txt --out <new .gba>
Input:   any ROM whose map 14,4 data is vanilla (the padded base or r39); the Buu's Fury USA ROM in data\roms (read
         only, SHA-1 checked, as patches.bf_hud). No earlier patch notes are needed.
API:     apply(rom, alloc) -> None; layout in alloc.notes["beam_struggle"], every write as (offset, length, name) in
         its "sites". plan(rom) -> the data before placement (slots, map entries, group payloads).
Method:  The art is beam_struggle_art.build(): the BF intro sphere, orbs and beams, 144 frames of 5 ticks (pulse
         0-1-2-1, 8 orbs out of the sphere edge that shrink, dim and vanish, the -3..+3 px sway with the beams
         joined, a soft local flash every 3.3-4.8 s). 124 world cells: 14 static, 110 animated.
         1. Static cells: 9 flip-folded tiles in a new chunk (table word 168), loaded to BG tiles 596-604 by 9 new
            index list entries (the 596 vanilla entries stay; loader @0x080050C8).
         2. Animated cells: one tile slot a cell. Group A = the 64 cells nearest the clash centre world (443, 388)
            (tiles 605-668), group B = the other 46 (tiles 669-714). Each group: 144 frame words, frame =
            {u32 5, bare codec stream} (@0x0800501E decompresses frame + 4 into 0x1000 B, so 64 tiles at most).
            The groups are k2 and k3 after the vanilla starburst (k0) and spark (k1): first change at tick 3 and 4
            (init @0x08005096). The 1-tick seam falls between the sphere body and the orb fringe.
         3. BG0 block (1,1) copy: the 124 footprint cells name the new tiles; every other cell (rocks) is vanilla.
            The footprint covers all 30 vanilla beam and spark cells, so no vanilla beam or spark cell shows.
         4. Layout copy of 0x084E2E7C: +0xC = 4 groups, +0x10 new group list, +0x14 new BG0 record, +0x48 new
            index list, +0x4C new chunk table (168 vanilla words + the new chunk). The only base ROM write is the
            14,4 layout word rom:0x4091EC. All frames are type 1 (packed) like the vanilla ones.
Rules:   Source: docs\tasks\2026-10-24-beam-struggle\beam-struggle-trial.md, beam-mockup-report.md (Mockup v2), the
         bible BMS and BMG rows. Every vanilla byte range read is pinned by SHA-1 before the first write; every
         footprint cell's vanilla tile must be empty, beam-only or spark; the new space must be 0xFF; every stream is
         decoded with webfoot_decompress and compared before the write; a second run raises. No code, no script, no
         palette change. tests\test_beam_struggle.py decodes the ROM and compares it with the mockup frames.
"""
import hashlib
import struct

from art import beam_struggle_art as art
from rom.webfoot_decompress import decompress, unpack_frame
from rom.webfoot_lz_pack import pack

# ===== constants: map 14,4 (base and r39 bytes, read 2026-10-25) =====
ROM_BASE = 0x08000000
LAYOUT_WORD = 0x4091EC                   # 14,4 layout list (entry rom:0x40DAB8 +0x2C names 0x084091EC)
LAYOUT, LAYOUT_LEN = 0x084E2E7C, 0x50
GROUP_LIST, BG0_REC, BG0_REC_LEN = 0x084E2E74, 0x084E0090, 0x58
CHUNK_TABLE, CHUNKS = 0x084DF574, 168     # words 0-167; word 168 is BG0 block 0's frame type (0x084DF814)
BLOCK = 5                                # BG0 block (1,1) of 4x4: world cells x 32-63, y 32-63
BG_PALETTE = (0x1DA4C8, 0x200)
PINS = {"layout": "5b852a9878c15761c4a7af851af0e23e831aabee",
        "group list": "91f5a713e8902729e69c38460db48ac3eac7a900",
        "BG0 record": "63a109a42df29f70a28c1f41b813ed0cee2e459f",
        "chunk table": "0e4b581e646d2ca5d7377553281c2609b1d858d5",     # 168 words
        "index list": "006d537bb72903e007d59e704c6d75a357c199fa",      # decoded, 596 entries
        "BG0 block (1,1)": "32d833b892ab2c71732223e82f274d6f86d4cf4d",  # decoded, 1024 entries
        "BG palette": "c3231aff7f1f53988cc881f7528491b43f5e3315"}       # the remap depends on it
VANILLA_TILES = 596
FREE = (596, 830)                        # spark group 831-842, starburst group 843-895
SPARK = (831, 842)
BEAM_IDX = (2, 67, 73, 74, 169)          # vanilla BG0 beam and spark colours
GROUP_MAX, GROUP_A = 64, 64
DURATION = art.STEP
CLASH = (443, 388)                       # world: BF (128, 108) + (315, 280)


# ===== helpers =====

def _u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE if a >= ROM_BASE else a)[0]


def _sha(b: bytes) -> str:
    return hashlib.sha1(bytes(b)).hexdigest()


def _frame(rom: bytes, a: int) -> bytes:
    return unpack_frame(rom, a - ROM_BASE)[2]


def _written(notes: dict) -> list:
    """(module, (offset, length, ...)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)))
    return out


def packed_frame(payload: bytes) -> bytes:
    """Type 1 frame {u32 1, u32 len, stream}, checked by decoding it."""
    f = pack(payload, kind=1)
    if decompress(f, 8)[0] != payload or len(f) % 4:
        raise ValueError("packed frame does not decode to its payload")
    return f


def bare_stream(payload: bytes) -> bytes:
    """A bare codec stream (group frames: @0x0800501E decodes frame + 4), checked by decoding it."""
    s = pack(payload, kind=1)[8:]
    if decompress(s, 0)[0] != payload or len(s) % 4:
        raise ValueError("bare stream does not decode to its payload")
    return s


def cell_entry(cell: tuple) -> int:
    """Entry index in BG0 block (1,1) of a world cell (BG0 layer pixel = world pixel, layer offset 0)."""
    cx, cy = cell
    if (cx // 32, cy // 32) != (BLOCK % 4, BLOCK // 4):
        raise ValueError(f"cell {cell} is outside BG0 block (1,1)")
    return (cy % 32) * 32 + cx % 32


# ===== plan (pure: no ROM write) =====

def plan(rom: bytes) -> dict:
    """Slots, map entries and group payloads from the generator; static tiles flip-folded in sorted cell order."""
    a = art.build(rom)
    cells, tiles = a["cells"], a["tiles"]
    static = [c for c in cells if len(set(tiles[c])) == 1]
    anim = [c for c in cells if c not in static]
    stored, entries = [], {}
    for c in static:
        t = tiles[c][0]
        canon = min(art.flips(t))
        if canon not in stored:
            stored.append(canon)
        k = art.flips(canon).index(t)
        entries[c] = (FREE[0] + stored.index(canon)) | (0x400 if k & 1 else 0) | (0x800 if k & 2 else 0)

    def d2(c):
        return ((c[0] * 8 + 4 - CLASH[0]) ** 2 + (c[1] * 8 + 4 - CLASH[1]) ** 2, c[1], c[0])
    near = sorted(anim, key=d2)[:GROUP_A]
    groups = [[c for c in anim if c in near], [c for c in anim if c not in near]]
    first = FREE[0] + len(stored)
    recs = []
    for cs in groups:
        if not 0 < len(cs) <= GROUP_MAX:
            raise ValueError(f"group of {len(cs)} tiles: 1-{GROUP_MAX} allowed")
        for i, c in enumerate(cs):
            entries[c] = first + i
        payloads = [b"".join(tiles[c][g] for c in cs) for g in range(art.NFRAMES)]
        recs.append({"first": first, "cells": cs, "payloads": payloads})
        first += len(cs)
    if first - 1 > FREE[1]:
        raise ValueError(f"tiles {FREE[0]}-{first - 1} pass the free range {FREE}")
    return {"art": a, "static": static, "stored": stored, "entries": entries, "groups": recs, "last_tile": first - 1}


# ===== checks =====

def _check(rom: bytearray, alloc) -> dict:
    """Every source pin; returns the decoded vanilla pieces."""
    if "beam_struggle" in alloc.notes:
        raise ValueError("beam_struggle already ran")
    if _u32(rom, LAYOUT_WORD) != LAYOUT:
        raise ValueError(f"rom:0x{LAYOUT_WORD:X} is 0x{_u32(rom, LAYOUT_WORD):08X}, expected 0x{LAYOUT:08X}")
    lay = LAYOUT - ROM_BASE
    idx = _frame(rom, _u32(rom, LAYOUT + 0x48))
    blk = _frame(rom, _u32(rom, BG0_REC + 0x18 + 4 * BLOCK))
    got = {"layout": rom[lay:lay + LAYOUT_LEN], "group list": rom[GROUP_LIST - ROM_BASE:GROUP_LIST - ROM_BASE + 8],
           "BG0 record": rom[BG0_REC - ROM_BASE:BG0_REC - ROM_BASE + BG0_REC_LEN],
           "chunk table": rom[CHUNK_TABLE - ROM_BASE:CHUNK_TABLE - ROM_BASE + 4 * CHUNKS],
           "index list": idx, "BG0 block (1,1)": blk, "BG palette": rom[BG_PALETTE[0]:sum(BG_PALETTE)]}
    for name, want in PINS.items():
        if _sha(got[name]) != want:
            raise ValueError(f"{name} SHA-1 is {_sha(got[name])}, expected {want}: map 14,4 is not vanilla")
    for name, site in _written(alloc.notes):
        s, n = site[:2]
        if s < LAYOUT_WORD + 4 and LAYOUT_WORD < s + n:
            raise ValueError(f"rom:0x{LAYOUT_WORD:X} is also written by {name} ({site}): stop and report")
    ent =list(struct.unpack("<%dH" % (len(idx) // 2), idx))
    for i in range(1, len(ent)):
        ent[i] = (ent[i] + ent[i - 1] + 1) & 0xFFFF
    used = max(e >> 8 for e in ent)
    if used >= CHUNKS:                                    # v1 fault: the new chunk took vanilla chunk 167
        raise ValueError(f"the 14,4 list names chunk {used}; the table copy keeps only words 0-{CHUNKS - 1}")
    return {"index": idx, "block": blk, "tiles": art.layout_tiles(bytes(rom[:0x800000]), LAYOUT)}


def _check_footprint(p: dict, van: dict) -> None:
    """Each footprint cell's vanilla tile is empty, beam-only or a spark tile, so no rock pixel is lost."""
    for c in p["art"]["cells"]:
        n = struct.unpack_from("<H", van["block"], 2 * cell_entry(c))[0] & 0x3FF
        if SPARK[0] <= n <= SPARK[1]:
            continue
        if n >= VANILLA_TILES or set(van["tiles"][n]) - {0} - set(BEAM_IDX):
            raise ValueError(f"world cell {c} holds vanilla tile {n} with non-beam pixels: stop and report")


# ===== data =====

def _pieces(p: dict, van: dict) -> list:
    """[(name, bytes or None, align)] in blob order; pointer words are filled in by _place."""
    idx = list(struct.unpack("<%dH" % (len(van["index"]) // 2), van["index"]))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    idx += [(CHUNKS << 8) | t for t in range(len(p["stored"]))]
    raw = [idx[0]] + [(idx[i] - idx[i - 1] - 1) & 0xFFFF for i in range(1, len(idx))]
    block = bytearray(van["block"])
    for c, e in p["entries"].items():
        struct.pack_into("<H", block, 2 * cell_entry(c), e)
    out = [("layout", None), ("group list", None), ("group A", None), ("group B", None), ("BG0 record", None),
           ("chunk table", None),
           ("index list", packed_frame(struct.pack("<%dH" % len(raw), *raw))),
           ("static chunk", packed_frame(b"".join(p["stored"]))),
           ("BG0 block (1,1)", packed_frame(bytes(block)))]
    for k, g in enumerate(p["groups"]):
        seen = []
        for pl in g["payloads"]:
            if pl not in seen:
                seen.append(pl)
        g["streams"] = seen
        g["frame_of"] = [seen.index(pl) for pl in g["payloads"]]
        for i, pl in enumerate(seen):
            out.append((f"group {'AB'[k]} frame {i}", struct.pack("<I", DURATION) + bare_stream(pl)))
    return out


def _place(rom: bytes, p: dict, pieces: list, at: int) -> tuple:
    """(blob, offsets) for the blob at file offset at; every piece 4-aligned."""
    offs, pos = {}, at
    sizes = {"layout": LAYOUT_LEN, "group list": 16, "group A": 4 + 4 * art.NFRAMES, "group B": 4 + 4 * art.NFRAMES,
             "BG0 record": BG0_REC_LEN, "chunk table": 4 * (CHUNKS + 1)}
    for name, data in pieces:
        offs[name] = pos
        pos += (sizes[name] if data is None else len(data) + 3) & ~3
    blob = bytearray(b"\xFF" * (pos - at))

    def put(name, data):
        blob[offs[name] - at:offs[name] - at + len(data)] = data
    for name, data in pieces:
        if data is not None:
            put(name, data)
    ptr = {k: v + ROM_BASE for k, v in offs.items()}
    lay = bytearray(rom[LAYOUT - ROM_BASE:LAYOUT - ROM_BASE + LAYOUT_LEN])
    struct.pack_into("<II", lay, 0xC, 4, ptr["group list"])
    struct.pack_into("<I", lay, 0x14, ptr["BG0 record"])
    struct.pack_into("<II", lay, 0x48, ptr["index list"], ptr["chunk table"])
    put("layout", lay)
    put("group list", rom[GROUP_LIST - ROM_BASE:GROUP_LIST - ROM_BASE + 8] + struct.pack("<II", ptr["group A"],
                                                                                          ptr["group B"]))
    for k, g in enumerate(p["groups"]):
        name = f"group {'AB'[k]}"
        words = [ptr[f"{name} frame {i}"] for i in g["frame_of"]]
        put(name, struct.pack("<BBH", art.NFRAMES, len(g["cells"]), g["first"]) + struct.pack(
            "<%dI" % len(words), *words))
    rec = bytearray(rom[BG0_REC - ROM_BASE:BG0_REC - ROM_BASE + BG0_REC_LEN])
    struct.pack_into("<I", rec, 0x18 + 4 * BLOCK, ptr["BG0 block (1,1)"])
    put("BG0 record", rec)
    put("chunk table", rom[CHUNK_TABLE - ROM_BASE:CHUNK_TABLE - ROM_BASE + 4 * CHUNKS] + struct.pack(
        "<I", ptr["static chunk"]))
    return bytes(blob), offs


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    van = _check(rom, alloc)
    p = plan(bytes(rom[:0x800000]))
    _check_footprint(p, van)
    pieces = _pieces(p, van)
    size = len(_place(rom, p, pieces, 0x800000)[0])
    at = alloc.alloc(size)
    if set(rom[at:at + size]) != {0xFF}:
        raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
    blob, offs = _place(rom, p, pieces, at)
    if len(blob) != size:
        raise ValueError(f"beam_struggle laid out to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[at:at + size] = blob                              # first write: every check has passed
    rom[LAYOUT_WORD:LAYOUT_WORD + 4] = struct.pack("<I", offs["layout"] + ROM_BASE)
    alloc.notes["beam_struggle"] = {
        "block": at, "size": size, "offsets": dict(offs), "layout": offs["layout"],
        "static_tiles": len(p["stored"]), "last_tile": p["last_tile"],
        "groups": [{"first": g["first"], "tiles": len(g["cells"]), "streams": len(g["streams"])} for g in p["groups"]],
        "sites": [(LAYOUT_WORD, 4, "map 14,4 layout word"), (at, size, "beam struggle layout, groups, tiles")]}
