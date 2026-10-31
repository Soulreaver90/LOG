r"""
gohan_gi.py - Patch: playable post-chamber Gohan and Rage (Cell fight) wear the purple gi (Task 5, Rulings 18, 30, 35).

Usage:   py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc_gi.gba gohan_gi
Input:   art\gi_base\ (gi_art.py), gi_ssj_v2\ (gi_post.py), gi_ssj2_aura\ and gi_rage_aura\ (gi_aura.py all,
         run after gi_post.py all).
Env:     LOG_GI_BASE, LOG_GI_SSJ and LOG_GI_SSJ2 override the art folders that sets 157, 158 and 159 read
         (defaults gi_base, gi_ssj_v2, gi_ssj2_aura). Set 160 always reads gi_rage_aura.
API:     apply(rom, alloc) -> None; notes in alloc.notes["gohan_gi"].
         apply_sets(rom, alloc, art) is the body. art=False relocates the same four sets with vanilla pixels,
         which is what patches.gohan_gi_vanilla does for the golden master. apply() always paints the art.
Method:  1. Copy the appearance table (rom:0x1D967C, 440 bytes) before any edit and point the reverse lookup
            literal rom:0x42F0 at the copy, so ext op 73 still finds the original set ids (Rage: step 5).
         2. Build sets 157 (gi base, set 56 layout), 158 (gi Super Saiyan, set 59 layout), 159 (gi Super Saiyan 2,
            set 59 layout) and 160 (gi Rage, set 58 layout) with build_set: every record keeps its manifest
            geometry, frames are raw. Anim 0 takes as many records per dir as the art has (6 in 159 and 160:
            the ssj2_idle hook picks body * 3 + shape).
         3. Copy the set table (rom:0x3B4E90, ids 7-156) with words for 157-160 and point rom:0x959C at it.
         4. Appearance 2 +1 (rom:0x1D96A5) = 157 and appearance 5 +1 (rom:0x1D96E1) = 158.
         5. Rage: appearance 4 +1 (rom:0x1D96CD) = 160 in the table and in the reverse lookup copy, and the push
            before ext 73 at @0x083EA369 becomes `00 00 00 A0` (op 0 twice: push 0, push 160; op 0 pushes a
            zero-extended byte, @0x08008F4C ldrb), the same 4 bytes as `1D 02 00 74` (push 0,58). Rage form
            code and the other bytes of entry 4 stay vanilla.
Rules:   Source: docs\research\re-outfit.md section 6, task-5-part2-report.md, docs\tasks\2026-10-18-aura-rage\aura-rage-report.md.
         Sets 55, 56, 58, 59 and their table words stay as they are. Every frame fits the player slot
         (log2_sprites.SLOT_BYTES, set header u16 +0).
"""
import json
import os
import struct

from PIL import Image

import log_paths
from rom.log2_sprites import build_set, image_to_tiles, set_records
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, rom_ptr, unpack_frame

# ===== constants =====
ART = log_paths.ART
APPEARANCE, APPEARANCE_LEN = 0x1D967C, 22 * 20
REVERSE_LITERAL, SET_TABLE_LITERAL = 0x42F0, 0x959C
FIRST_ID, OLD_IDS = 7, 150                                   # the table holds ids 7-156
SETS = {157: (os.environ.get("LOG_GI_BASE", "gi_base"), 56), 158: (os.environ.get("LOG_GI_SSJ", "gi_ssj_v2"), 59),
        159: (os.environ.get("LOG_GI_SSJ2", "gi_ssj2_aura"), 59), 160: ("gi_rage_aura", 58)}   # id: (art, layout)
IDLE_RECORDS = {157: 2, 158: 2, 159: 6, 160: 6}              # anim 0 records per dir each set publishes
GI_BLOCK = 580076                                            # bytes the dev master allocates for the four sets
RAGE_SET, RAGE_ENTRY = 160, 4
APPEARANCE_SITES = {0x1D96A5: (0x38, 157), 0x1D96E1: (0x3B, 158), 0x1D96CD: (0x3A, RAGE_SET)}   # entry 2, 5, 4 +1
RAGE_SCRIPT = (0x3EA365, bytes.fromhex("1d020074"), bytes([0, 0, 0, RAGE_SET]))   # the push before ext 73 @0x083EA369


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _gba(off: int) -> bytes:
    return struct.pack("<I", off + ROM_BASE)


def art_records(folder: str) -> tuple:
    """({key: record with a frame id}, {frame id: tile bytes}) from a gi art folder."""
    records, frames = {}, {}
    for m in json.loads((ART / folder / "manifest.json").read_text(encoding="ascii")):
        with Image.open(ART / folder / m["png"]) as img:
            frames[m["png"]] = image_to_tiles(img)
        for k in m["keys"]:
            records[(k["anim"], k["dir"], k["index"])] = {f: k[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")} \
                | {"frame": m["png"]}
    return records, frames


def vanilla_records(rom: bytes, src: int, idle: int) -> tuple:
    """({key: record with a frame id}, {frame id: tile bytes}) from the vanilla source set itself, with anim 0
    widened to `idle` records per dir. The frame id is the vanilla frame header offset, so records that share a
    frame still share one new frame. The ssj2_idle hook picks body * 3 + shape, and vanilla draws no aura, so
    index k shows vanilla body k // shapes: 0, 0, 0, 1, 1, 1 where the art has 3 shapes a body. A set whose art
    adds no shape divides by 1, which is the identity."""
    records, frames = {}, {}
    for r in set_records(rom, src):
        frames[r["header"]] = unpack_frame(rom, r["header"])[2]
        records[(r["anim"], r["dir"], r["index"])] = {f: r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")} \
            | {"frame": r["header"]}
    bodies = sum(1 for a, d, _ in records if (a, d) == (0, 0))
    if not bodies or idle % bodies:
        raise ValueError(f"anim 0 has {bodies} vanilla records per dir, which does not divide {idle}")
    shapes = idle // bodies
    records.update({(0, d, k): records[(0, d, k // shapes)]
                    for d in {d for a, d, _ in records if a == 0} for k in range(idle)})
    return records, frames


def apply_sets(rom: bytearray, alloc, art: bool) -> None:
    """The patch body. art=True paints the gi art folders over the vanilla layout sets, which is the dev master.
    art=False gives the same four relocated sets vanilla pixels, which is the golden master."""
    _expect(rom, REVERSE_LITERAL, _gba(APPEARANCE))
    _expect(rom, SET_TABLE_LITERAL, _gba(SET_TABLE))
    for off, (old, _) in APPEARANCE_SITES.items():
        _expect(rom, off, bytes([old]))
    _expect(rom, RAGE_SCRIPT[0], RAGE_SCRIPT[1] + bytes.fromhex("0249"))     # push 0,58 ; call ext_73

    # 1. appearance copy for the reverse lookup (0x080042BC): vanilla, except Rage's set id
    copy = alloc.alloc(APPEARANCE_LEN)
    rom[copy:copy + APPEARANCE_LEN] = rom[APPEARANCE:APPEARANCE + APPEARANCE_LEN]
    rom[copy + 20 * RAGE_ENTRY + 1] = RAGE_SET                  # ext 73 (0, 160) finds entry 4, as (0, 58) did
    rom[REVERSE_LITERAL:REVERSE_LITERAL + 4] = _gba(copy)

    # 2. the three gi sets
    offsets = {}
    for set_id, (folder, layout) in SETS.items():
        src = rom_ptr(rom, SET_TABLE + 4 * (layout - FIRST_ID))
        records, frames = art_records(folder) if art else vanilla_records(rom, src, IDLE_RECORDS[set_id])
        idle = sum(1 for a, d, _ in records if (a, d) == (0, 0))
        offsets[set_id] = build_set(rom, src, records, frames, alloc, counts={0: idle})

    # 2b. the golden master pads the block to the dev size, so every later allocation keeps its dev address.
    # superperfect_cell pins one of them and bf_hud digests words that name others. Nothing reads the pad.
    if not art:
        at, size = alloc.used()[-1]
        pad = copy + GI_BLOCK - (at + size)
        if pad < 0:
            raise ValueError(f"the vanilla sets take {at + size - copy} bytes, over the dev block GI_BLOCK "
                             f"= {GI_BLOCK}: rerun test_golden.py::test_the_dev_gi_block_is_the_padded_size")
        if pad:
            alloc.alloc(pad, align=1)

    # 3. set table with words for the new ids
    words = max(SETS) - FIRST_ID + 1
    table = alloc.alloc(4 * words)
    rom[table:table + 4 * OLD_IDS] = rom[SET_TABLE:SET_TABLE + 4 * OLD_IDS]
    for set_id, off in offsets.items():
        rom[table + 4 * (set_id - FIRST_ID):table + 4 * (set_id - FIRST_ID) + 4] = _gba(off)
    rom[SET_TABLE_LITERAL:SET_TABLE_LITERAL + 4] = _gba(table)

    # 4-5. playable appearances and the Rage script
    for off, (_, new) in APPEARANCE_SITES.items():
        rom[off] = new
    rom[RAGE_SCRIPT[0]:RAGE_SCRIPT[0] + 4] = RAGE_SCRIPT[2]

    alloc.notes["gohan_gi"] = {"appearance_copy": copy, "set_table": table,
                               **{f"set_{set_id}": off for set_id, off in offsets.items()}}


def apply(rom: bytearray, alloc) -> None:
    apply_sets(rom, alloc, art=True)
