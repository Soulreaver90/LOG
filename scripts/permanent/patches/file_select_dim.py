r"""
file_select_dim.py - Patch: unselected characters on the file select and Switch Characters keep a skin-colored dim.

Usage:   py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc_rNN.gba <r17 list> file_select_dim
Input:   any ROM: the base ROM or a built one (no other patch touches the table or its pool word).
API:     apply(rom, alloc) -> None; notes in alloc.notes["file_select_dim"].
Method:  1. The menu sprite constructor 0x08007C70 (callers: file select 0x08000DCC, Switch Characters 0x08010C5C)
            gives every sprite the dim table 0x086D0ED0 (pool word rom:0x7D1C); vtable 0x08025C30 +0x28
            (0x08007CB6) clears it for the highlighted sprite (arg 1) and restores it (arg 0). 0x080076EE stores
            the table at obj+0x24; the frame upload remaps each pixel byte through it (0x0801F3BA, type 0 via
            0x0300029C, type 1 via 0x03000958).
         2. Every other dim entry the gi sets use (157-160, anims 0 and 1) keeps its hue (shift <= 12.3 deg, luma
            ratio 0.63-1.04).
            Two skin entries do not: 114 -> 124 (olive gray, hue 12 -> 50 deg) and 115 -> 244 (mauve, 15 -> 340 deg).
            The gi shows skin on the shoulders, arms and chest V, so the unselected gi reads as purple shoulders,
            an orange V and a gray face. The armor shows skin on the face only.
         3. Write 114 -> 116 and 115 -> 117 (two skin steps down; luma 0.72 and 0.68, hue 18 and 20 deg), in place.
Rules:   Source: docs\tasks\2026-10-18-file-select\file-select-report.md. Blast radius: every sprite drawn through the table with
         pixel 114 or 115, that is the unselected Gohan sets (53, 55, 57, 157-160) and Goku (60, 61) on these two
         screens. Piccolo, Vegeta, Trunks and Hercule use neither index. The palette has no duplicate of 114 or
         115, so a gi-only recolor is not possible without code. Both sites are checked before any write.
"""
import struct

# ===== constants =====
ROM_BASE = 0x08000000
DIM_TABLE = 0x6D0ED0                       # 256-byte remap, GBA 0x086D0ED0
DIM_LITERAL = 0x7D1C                       # pool word of ldr r1 @0x08007C9A and @0x08007CCE
FIXES = {114: (124, 116), 115: (244, 117)}  # index: (vanilla dim, new dim)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def apply(rom: bytearray, alloc) -> None:
    _expect(rom, DIM_LITERAL, struct.pack("<I", DIM_TABLE + ROM_BASE))
    for index, (old, _) in FIXES.items():
        _expect(rom, DIM_TABLE + index, bytes([old]))
    for index, (_, new) in FIXES.items():
        rom[DIM_TABLE + index] = new
    alloc.notes["file_select_dim"] = {"table": DIM_TABLE, "entries": {i: new for i, (_, new) in FIXES.items()}}
