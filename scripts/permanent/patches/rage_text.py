r"""
rage_text.py - Patch: the Cell fight Rage message says "Gohan has transformed" / "into Super Saiyan 2!".

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r19.gba <r18 patch list> rage_text
Input:   any ROM with the vanilla record; it needs no notes. API: apply(rom, alloc) -> None; alloc.notes["rage_text"].
Method:  The type 1 record rom:0x3EA388 (`1E 00 01 00`, text `40 5E` "Gohan has entered Super Saiyan Rage!" 00)
         has one reference, the scene list word rom:0x3EA474. The new text is 5 bytes longer than the old space,
         so a new record (same 4-byte head) goes to the expansion area and only that word is repointed, as npc_gi
         does. The old record stays, unreferenced; the next record rom:0x3EA3B4 and its word rom:0x3EA478 stay.
Rules:   Source: docs\tasks\2026-10-19-r19-build\r19-build.md, r19-build-report.md (reader evidence). scene_run 0x0800B520
         passes the list word to scene_type1 0x0800B438 (text = record +4, no range check); the box object keeps
         the text pointer and the line breaker 0x0801F7FC reads it to the first 00 at use time. In text, 0x0A ends
         the line in the same box; 0x0B ends the box (A press, new box), so the break here is 0x0A. Each line is
         at most 0x90 px wide in font 0x0802CC64. Every byte is checked before any write.
"""
import struct

# ===== constants =====
ROM_BASE = 0x08000000
RECORD, LIST_WORD = 0x3EA388, 0x3EA474                    # Rage record and its only scene list word
NEXT_RECORD, NEXT_WORD = 0x3EA3B4, 0x3EA478               # Cell's "You wretched child!!!" record, untouched
HEAD = bytes.fromhex("1e000100")                          # seq 30, 0, type 1, portrait 0
OLD_TEXT = b"\x40\x5e" + b"Gohan has entered Super Saiyan Rage!" + b"\x00\x00"   # text, terminator, pad
NEXT_HEAD = bytes.fromhex("1f000128")
NEW_TEXT = b"\x40\x5e" + b"Gohan has transformed" + b"\x0a" + b"into Super Saiyan 2!" + b"\x00"


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def apply(rom: bytearray, alloc) -> None:
    _expect(rom, RECORD, HEAD + OLD_TEXT)
    _expect(rom, NEXT_RECORD, NEXT_HEAD)
    _expect(rom, LIST_WORD, _word(RECORD + ROM_BASE) + _word(NEXT_RECORD + ROM_BASE))
    if any(len(line) > 21 for line in NEW_TEXT[2:-1].split(b"\x0a")):
        raise ValueError("a new text line is longer than 21 characters")

    record = HEAD + NEW_TEXT
    at = alloc.alloc(len(record))
    rom[at:at + len(record)] = record
    rom[LIST_WORD:LIST_WORD + 4] = _word(at + ROM_BASE)
    alloc.notes["rage_text"] = {"record": at, "size": len(record)}
