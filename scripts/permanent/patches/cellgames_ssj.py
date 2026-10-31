r"""
cellgames_ssj.py - Patch: Gohan and Goku in Super Saiyan through the Cell Games (final, 2026-10-20).

Usage:   py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r27.gba
Input:   the ROM after gohan_gi (notes: appearance_copy) and npc_gi (notes: records, the relocated Cell Games
         entry seq 1). Run it at the end of the build list, so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["cellgames_ssj"].
Method:  1. Reverse lookup copy entry 5 +1: 59 to 158, so ext 73 (0, 158) finds entry 5 (else the assert hang).
         2. NPC Gohan 157 to 158 (op 0 byte 9D to 9E) in the entry scene and "Me? Fight Cell?", and both map
            objects. NPC Goku 60 to 61 (varint 78 to 7A, op 0 3C to 3D) from "Me? Fight Cell?" seq 21 to his
            teleport (rom:0x3EB704 seq 23), plus the 14,1 map object. Actor lookup is by set pointer, so each
            group changes together.
         3. Portraits: NPC Gohan raw 59 to 62 (the cutscene hook shows 115 while his record is a gi entry);
            NPC Goku raw 63 to 65, including the 14,1 talk. Leader lines follow the record (entry 5: 115,
            entry 20: 65) with no byte change.
         4. Records that grow are copied to the expansion area and their one scene-table word repointed:
            - entry seq 1 (the npc_gi copy): its two Gohan bytes, and Goku's transform before `push 50 ; ext 46`:
              sound 55, state 9 (power up, set 60 has anim 9), flash, sound 55 off, ext 73 (4, 61), wait 10;
            - "Me? Fight Cell?" seq 21: its Gohan and Goku bytes, and ext 73 (0, 158) before `push 0 ; ext 70`;
            - Cell fight seq 1: ext 73 (0, 158) and ext 110 (0, 5000) (EP to full) before `push 0 ; ext 70`.
            Old records stay unchanged and unreferenced (a state paused inside one keeps running it).
Rules:   Source: docs\tasks\2026-10-20-r27-build\cellgames-build.md (final decisions) and cellgames-ssj-report.md (design).
         ext 73 for a non-leader writes only the record; ext 70 then builds the player from entry 5. The post-Cell
         group (rom:0x3EC758, set 157) and every pre-stretch site stay. Every byte, record hash and table word
         is checked before any write; a second run raises. Records have no jump ops (npc_gi.relocate checks).
"""
import hashlib
import struct

from scene.scene_lib import relocate

# ===== constants =====
ROM_BASE = 0x08000000
REVERSE_LITERAL, ENTRY, SSJ_ENTRY = 0x42F0, 20, 5
GOHAN_SSJ, GOHAN_ARMOR_SSJ = 158, 59
ENTRY_SEQ1_OLD = 0x3E8610                         # npc_gi key of the relocated entry seq 1

# rom offset: (old byte, new byte)
GOHAN_SITES = {o: (0x9D, 0x9E) for o in (0x408CA0, 0x408F8C,             # map objects 14,1 and 14,3
                                         0x3E8C2C, 0x3E8D1E, 0x3E8D41,   # entry seq 22, 26, 26
                                         0x3E921C, 0x3E9226)}            # "Me? Fight Cell?" seq 14
GOKU_SITES = {**{o: (0x78, 0x7A) for o in (                              # zigzag varint 60 to 61
    0x3E946B, 0x3E9807, 0x3E982C,                                        # rom:0x3E9D4C seq 1, 14
    0x3EA679, 0x3EA698, 0x3EA6D0, 0x3EA793, 0x3EA7ED, 0x3EA7F3, 0x3EA7FA, 0x3EA801, 0x3EA808, 0x3EA80F,
    0x3EA816, 0x3EA891, 0x3EA89F, 0x3EA8A5, 0x3EA8AC, 0x3EA8B3, 0x3EA8BA, 0x3EA8C1, 0x3EA8C8, 0x3EA8CD,
    0x3EA8D8, 0x3EA8E2, 0x3EA951)},                                      # rom:0x3EB704 seq 8-20
              0x3EA9CA: (0x3C, 0x3D),                                    # seq 23 remove (op 0)
              0x408D54: (0x3C, 0x3D)}                                    # map 14,1 object @0x08408D44 +0x10
PORTRAIT_SITES = {**{o: (59, 62) for o in (0x3E8173, 0x3E81A3, 0x3E9233, 0x3E934F)},
                  **{o: (63, 65) for o in (0x3E9707, 0x3E977F, 0x3E9835, 0x3EA79F, 0x3EA823, 0x3EA8EF,
                                           0x3EA95F, 0x3E850B)}}

GOKU_TRANSFORM = bytes.fromhex("0037022e"        # push 55 ; ext 46 (aura sound on)
                               "1d0200120239"    # push 0,9 ; ext 57 (player: state 9, power up)
                               "000a022a"        # push 10 ; ext 42 (flash)
                               "0037022f"        # push 55 ; ext 47 (aura sound off)
                               "0004003d0249"    # push 4 ; push 61 ; ext 73 (Goku: Super Saiyan)
                               "000a022b")       # push 10 ; ext 43 (wait)
GOHAN_SSJ_RECORD = bytes.fromhex("0000009e0249")                 # push 0 ; push 158 ; ext 73
GOHAN_EP_FULL = bytes.fromhex("1d0200ce10026e")                  # push 0,5000 ; ext 110 (EP = max)

# name: (old record or None for the npc_gi copy, length, table word, SHA-1, {op offset in record: (old, new)})
RECORDS = {
    "entry_seq1": (None, 0xD4, 0x3E8D98, "5e3ea13732f224be3370ab99b4ce5ddb3de3973a", {
        0x5C: ("009d", "009e"),                                  # push 157 ; ext 51 (spawn NPC Gohan)
        0x72: ("009d", "009e"),                                  # push 157 ; ext 53
        0xCF: ("0032", GOKU_TRANSFORM.hex() + "0032")}),         # before push 50 ; ext 46
    "fight_cell_seq21": (0x3E9384, 0x61, 0x3E9438, "9a85a9ecf74f6ee5ac1f6e6d294f29569ccb7389", {
        0x16: ("009d", "009e"),                                  # push 157 ; ext 52 (remove NPC Gohan)
        0x22: ("0000", GOHAN_SSJ_RECORD.hex() + "0000"),         # before push 0 ; ext 70
        0x3B: ("1d037888508140", "1d037a88508140")}),          # push 60,272,160 ; ext 51 (NPC Goku)
    "cell_fight_seq1": (0x3E9E8C, 0x5E, 0x3EA400, "9ab323724c0cc1b8ce1f612d074aff7e8a9dff08", {
        0x13: ("0000", (GOHAN_SSJ_RECORD + GOHAN_EP_FULL).hex() + "0000")}),     # before push 0 ; ext 70
}


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _byte_sites() -> dict:
    return {**GOHAN_SITES, **GOKU_SITES, **PORTRAIT_SITES}


def apply(rom: bytearray, alloc) -> None:
    need = ("gohan_gi", "npc_gi")
    if any(k not in alloc.notes for k in need):
        raise ValueError(f"cellgames_ssj needs the {', '.join(need)} notes: run them first")
    if "cellgames_ssj" in alloc.notes:
        raise ValueError("cellgames_ssj already ran")
    copy = alloc.notes["gohan_gi"]["appearance_copy"]
    reverse = copy + ENTRY * SSJ_ENTRY + 1

    # checks, before any write
    _expect(rom, REVERSE_LITERAL, struct.pack("<I", copy + ROM_BASE))
    _expect(rom, reverse, bytes([GOHAN_ARMOR_SSJ]))
    for off, (old, _) in _byte_sites().items():
        _expect(rom, off, bytes([old]))
    sources, copies = {}, {}
    for name, (old, length, word, sha, edits) in RECORDS.items():
        rec = alloc.notes["npc_gi"]["records"][ENTRY_SEQ1_OLD] if old is None else old
        _expect(rom, word, struct.pack("<I", rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} ({name}) differs from the r26 bytes")
        sources[name] = rec
        copies[name] = relocate(rom, rec, length, {rec + o: e for o, e in edits.items()})

    # writes: in-place bytes, reverse copy, relocated records and their table words
    for off, (_, new) in _byte_sites().items():
        rom[off] = new
    rom[reverse] = GOHAN_SSJ
    moved = {}
    for name, data in copies.items():
        at = alloc.alloc(len(data))
        rom[at:at + len(data)] = data
        word = RECORDS[name][2]
        rom[word:word + 4] = struct.pack("<I", at + ROM_BASE)
        moved[name] = at

    alloc.notes["cellgames_ssj"] = {"records": moved, "sources": sources,
                                    "sizes": {k: len(v) for k, v in copies.items()}, "reverse_byte": reverse}
