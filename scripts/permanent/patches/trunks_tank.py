r"""
trunks_tank.py - Trial patch: Trunks wears the tank top instead of the jacket, in both forms.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_trunkstank.txt
             --out builds\mockups\2026-11-01-trunks-tank-lab\log2_poc_trunkstank.gba
             --save builds\mockups\2026-11-01-trunks-tank-lab\log2_trunkstank_lab.sav
Input:   art\trunks_tank\manifest.json and the PNGs it names. The manifest was generated from the ROM, so
         each "headers" entry is a vanilla frame header offset and each "keys" entry is the
         (anim, dir, index) that header serves. The manifest is the source of truth for both.
         Each row names its own "set", 128 (base) or 134 (Super Saiyan), and its own "form".
API:     apply(rom, alloc) -> None. Notes in alloc.notes["trunks_tank"], every write as (offset, length,
         name) in its "sites". art_frames(set_id) -> {vanilla header offset: tile bytes}.
         manifest() -> the parsed manifest rows. rows(set_id) -> that set's rows.
Method:  1. Resolve each set through the LIVE set table, the word at rom:0x959C. gohan_gi relocates that
            table, so the live table is its copy in the expansion area, not rom:0x3B4E90.
         2. Check each manifest header against ITS OWN set's records: the header must exist in that set, it
            must serve exactly the keys the manifest lists, and its size must be the manifest's w by h. A
            disagreement stops the build, because the manifest is proved and a mismatch means a set moved.
         3. clone_set copies the set header, the animation table and every record list into free space, and
            gives each listed header one new raw frame holding the drawn pixels. Records that share a header
            share the new frame, so the stand pose and the anim 4 idle variant both change, and dir 3 keeps
            reusing the dir 2 record with the OBJ h-flip bit. Nothing else in either set changes.
         4. The live table word for each set points at that set's clone.
Forms:   Set 134 is NOT a frame for frame copy of set 128 (bible TNK2). Every Super Saiyan frame here is
         set 134's own head rows 0-15, carrying the owner's edit only where the two vanilla frames agree,
         plus his tank body rows 16-31 wholesale. That is the one body rule of bible row 262, and no pixel
         is drawn, except at the collar. Super Saiyan art covers the side row, the front walk and the
         back row. Where the owner's back art closes the removed collar with BASE hair, which cannot
         go on a gold head, the Super Saiyan frame takes the gold of the SAME role, E5 to 14, 64 to 2E
         and 62 to 78, inside the head rows only. That is his decision of 2026-11-05, bible row TSB.
         Only the three front facing idles are NOT in the manifest: they drop 23 Super Saiyan body
         pixels, which is his call, and they wait on him. See docs\tasks\2026-11-02-trunks-ssj\brief.md.
Lab:     The lab shows the player. Set 128 reaches the player through the SAVE, not through this module:
         appearance 12 is set 128 and is a vanilla playable Trunks appearance (bible CFS, BLP), so a slot
         with leader 3 and Trunks on appearance 12 walks as set 128 with no code change at all.
         scripts\one-time\2026-11-01-trunks-tank-lab\make_lab_save.py writes that save.
         So this module changes no appearance byte and no player code, and it stays promotable as it is.
Rules:   Source: docs\tasks\2026-11-01-trunks-tank-lab\brief.md, docs\tasks\2026-11-02-trunks-ssj\brief.md
         and docs\sprite-guide.md. The art is the owner's, pixel for pixel: this module reads the PNGs and
         never edits a pixel. The set table must already be relocated, so this module writes no byte of the
         original ROM image. A second run raises.
Labels:  CONFIRMED = read from the ROM bytes. LIKELY = strong evidence, my test pending.
"""
import json
import struct

from PIL import Image

import log_paths
from rom.log2_sprites import clone_set, image_to_tiles, set_records
from rom.webfoot_decompress import ROM_BASE, rom_ptr

# ===== constants =====
ART = log_paths.TRUNKS_TANK
FIRST_ID = 7                                   # set id N resolves through rom:0x959C, entry N - 7
SET_TABLE_LITERAL = 0x959C
VANILLA_SETS = {128: 0x35BBE0,                 # base Trunks, CONFIRMED by set_records
                134: 0x37FB74}                 # Super Saiyan Trunks, CONFIRMED by set_records
EXPANSION = 0x800000                           # the allocator's first byte: a relocated table lives here


def manifest() -> list:
    """The manifest rows, in file order."""
    return json.loads((ART / "manifest.json").read_text(encoding="ascii"))


def rows(set_id: int) -> list:
    """The manifest rows that belong to one set."""
    return [m for m in manifest() if m["set"] == set_id]


def art_frames(set_id: int) -> dict:
    """{vanilla frame header offset: tile bytes} for one set. Several headers may share one PNG."""
    frames = {}
    for m in rows(set_id):
        with Image.open(ART / m["png"]) as img:
            if img.size != (m["w"], m["h"]):
                raise ValueError(f"{m['png']} is {img.size[0]}x{img.size[1]}, the manifest says "
                                 f"{m['w']}x{m['h']}")
            tiles = image_to_tiles(img)
        for header in m["headers"]:
            frames[int(header, 16)] = tiles
    return frames


def _check_manifest(rom: bytes, src: int, set_id: int) -> None:
    """Every row of this set must serve exactly the keys and the size the manifest gives it."""
    keys, size = {}, {}
    for r in set_records(rom, src):
        keys.setdefault(r["header"], []).append((r["anim"], r["dir"], r["index"]))
        size[r["header"]] = (r["w"], r["h"])
    for m in rows(set_id):
        want = sorted(tuple(k) for k in m["keys"])
        got = []
        for header in m["headers"]:
            at = int(header, 16)
            if at not in keys:
                raise ValueError(f"{m['png']}: rom:0x{at:X} is no record of set {set_id} at rom:0x{src:X}")
            if size[at] != (m["w"], m["h"]):
                raise ValueError(f"{m['png']}: rom:0x{at:X} is {size[at][0]}x{size[at][1]}, the manifest "
                                 f"says {m['w']}x{m['h']}")
            got += keys[at]
        if sorted(got) != want:
            raise ValueError(f"{m['png']}: its headers serve {sorted(got)}, the manifest says {want}")


def apply(rom: bytearray, alloc) -> None:
    if "trunks_tank" in alloc.notes:
        raise ValueError("trunks_tank already ran")
    stray = {m["set"] for m in manifest()} - set(VANILLA_SETS)
    if stray:
        raise ValueError(f"the manifest names set(s) {sorted(stray)}, which this module does not build")
    table = rom_ptr(rom, SET_TABLE_LITERAL)          # a file offset, as every rom_ptr result is
    if table is None or table < EXPANSION:
        raise ValueError(f"the set table literal rom:0x{SET_TABLE_LITERAL:X} still names the original table: "
                         "run this module after gohan_gi, which relocates it")

    before = len(alloc.used())
    built, sites = {}, []
    for set_id, vanilla in sorted(VANILLA_SETS.items()):
        word = table + 4 * (set_id - FIRST_ID)
        src = rom_ptr(rom, word)
        if src != vanilla:
            raise ValueError(f"set {set_id} is rom:0x{src:X}, expected the vanilla rom:0x{vanilla:X}: "
                             "an earlier module already rebuilt it, stop and report")
        _check_manifest(rom, src, set_id)
        frames = art_frames(set_id)
        new = clone_set(rom, src, frames, alloc)
        struct.pack_into("<I", rom, word, new + ROM_BASE)
        built[set_id] = {"source": src, "clone": new, "word": word, "headers": sorted(frames),
                         "pngs": [m["png"] for m in rows(set_id)]}
        sites.append((word, 4, f"live set table word for set {set_id}"))
    mine = alloc.used()[before:]

    alloc.notes["trunks_tank"] = {
        "table": table, "sets": built, "pngs": [m["png"] for m in manifest()],
        "alloc": (mine[0][0], mine[-1][0] + mine[-1][1] - mine[0][0]) if mine else None,
        "sites": sites}
