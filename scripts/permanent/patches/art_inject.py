r"""
art_inject.py - Patch: write the art tables into the ROM, OBJ palette entries and dialog portraits (final, 2026-10-20).

Usage:   listed in scripts\permanent\build_list.txt after rage_text and before status_portrait; inject.py builds it.
Input:   art\tables\palette.json, portraits.json and the PNGs it names, or the same tables staged by
         inject.py as alloc.notes["art_input"] = {"palette": {index: rgb}, "portraits": {id: 4096 pixel bytes}};
         alloc.notes["npc_gi"] (the live portrait block) and alloc.notes["gohan_portraits"] (its block, ids 0-120).
API:     apply(rom, alloc) -> None; notes in alloc.notes["art_inject"].    slot(pid) -> file offset of the id's frame.
Method:  1. Palette: entry i writes rom:0x1DA6C8 + 2i (BGR555) and the fade table rom:0x3ECBA4 + 3 (256 + i)
            (RGB888). The field shows the fade table copy after every fade in (palette-slot-report.md).
         2. Portraits: id pid gets a raw type 0 frame {0, 0x1000, pixels} at slot(pid) = rom:0xF00000 + 0x1008 pid,
            outside the allocator (log2_build.ART_REGION), and its live block word points at it. A slot depends on
            the id only, so adding or replacing one portrait never moves another one or any code.
         3. LEGACY_GAP: one 0x5028-byte allocation, left 0xFF, where the r20-r22 portrait_remaster first call put
            five frames. status_portrait and rage_stats keep their r22 addresses, so r22 save states still fit.
Rules:   Fail closed: every check runs before the first write. Each block word must still name the frame the
         earlier patches gave it (gohan_portraits' block; id 121 is word 59, as npc_gi made it); that frame's
         outer 3 px ring is the reference. Both palette copies must agree before the write. Old frames stay in
         the ROM. gohan_portraits keeps its own 115-120 frames: removing them would move every later allocation.
"""
import struct

from art import art_tables as at
from log2_build import ART_REGION
from patches.npc_gi import ARMOR_ID, PRE_ID
from rom.webfoot_decompress import ROM_BASE

# ===== constants =====
FRAME = 8 + at.SIZE
RAW_HEADER = struct.pack("<II", 0, at.SIZE)        # raw type 0 (@0x0801F394)
LEGACY_GAP = 5 * FRAME
BLOCK_LITERAL, STRUCT_WORD = 0xBE10, 0x03000E90


# ===== helpers =====

def slot(pid: int) -> int:
    return ART_REGION[0] + FRAME * pid


def palette_sites(index: int) -> tuple:
    """(BGR555 file offset, RGB888 file offset) of OBJ index."""
    return at.OBJ_PAL + 2 * index, at.RGB_TABLE + 3 * (256 + index)


def _u32(rom, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _expect(rom, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


# ===== checks =====

def _check_palette(rom: bytearray, palette: dict) -> None:
    for index, rgb in palette.items():
        problems, _ = at.check_palette_entry(rom, {k: v for k, v in palette.items() if k != index}, index, rgb)
        if problems:
            raise ValueError(f"palette {index}: " + "; ".join(problems))
        bgr, rgb_at = palette_sites(index)
        if at.obj_palette(rom)[index] != tuple(rom[rgb_at:rgb_at + 3]):
            raise ValueError(f"palette {index}: rom:0x{bgr:X} and rom:0x{rgb_at:X} disagree: written already?")


def _live_block(rom: bytearray, alloc) -> int:
    block = _u32(rom, BLOCK_LITERAL) - ROM_BASE
    if block != alloc.notes["npc_gi"]["block"]:
        raise ValueError(f"rom:0xBE10 names block 0x{block:X}, not npc_gi's 0x{alloc.notes['npc_gi']['block']:X}")
    _expect(rom, alloc.notes["npc_gi"]["pool"], _word(block + ROM_BASE))       # the cutscene hook's block word
    _expect(rom, block, _word(STRUCT_WORD))
    return block


def _old_word(rom: bytearray, alloc, pid: int) -> int:
    """The block word earlier patches gave pid: gohan_portraits' block, and word 59 for npc_gi's id 121."""
    return _u32(rom, alloc.notes["gohan_portraits"]["block"] + 4 + 4 * (ARMOR_ID if pid == PRE_ID else pid))


def _check_portraits(rom: bytearray, alloc, block: int, portraits: dict, allowed: set) -> None:
    for pid, px in sorted(portraits.items()):
        if not at.valid_id(pid):
            raise ValueError(f"portrait {pid}: " + "; ".join(at.check_pixels(pid, px, None, allowed)))
        old = _old_word(rom, alloc, pid)
        _expect(rom, block + 4 + 4 * pid, _word(old))
        problems = at.check_pixels(pid, px, at.live_frame(rom, block, pid)[1], allowed)
        if problems:
            raise ValueError(f"portrait {pid}: " + "; ".join(problems))
        if set(rom[slot(pid):slot(pid) + FRAME]) != {0xFF}:
            raise ValueError(f"portrait {pid}: slot rom:0x{slot(pid):X} is not free")
    end = ART_REGION[0] + ART_REGION[1]
    if any(off < end and off + n > ART_REGION[0] for off, n in alloc.used()):
        raise ValueError("an allocation overlaps the art region")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "art_inject" in alloc.notes:
        raise ValueError("art_inject already ran")
    if "npc_gi" not in alloc.notes or "gohan_portraits" not in alloc.notes:
        raise ValueError("art_inject needs the npc_gi and gohan_portraits notes: run them first")
    staged = alloc.notes.get("art_input")
    palette = dict(staged["palette"]) if staged else at.load_palette()
    _check_palette(rom, palette)
    pal, allowed = at.obj_palette(rom, palette), at.allowed_indices(rom, palette)
    portraits = dict(staged["portraits"]) if staged else \
        {pid: at.png_pixels(at.ART_DIR / e["png"], pal, allowed) for pid, e in at.load_portraits().items()}
    block = _live_block(rom, alloc)
    _check_portraits(rom, alloc, block, portraits, allowed)

    for index, (r, g, b) in sorted(palette.items()):
        bgr, rgb_at = palette_sites(index)
        rom[bgr:bgr + 2] = struct.pack("<H", (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10)
        rom[rgb_at:rgb_at + 3] = bytes((r, g, b))
    gap = alloc.alloc(LEGACY_GAP)
    for pid, px in sorted(portraits.items()):
        rom[slot(pid):slot(pid) + FRAME] = RAW_HEADER + px
        rom[block + 4 + 4 * pid:block + 8 + 4 * pid] = _word(slot(pid) + ROM_BASE)
    alloc.notes["art_inject"] = {"block": block, "frames": {pid: slot(pid) for pid in sorted(portraits)},
                                 "palette": sorted(palette), "gap": gap}
