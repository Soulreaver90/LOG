r"""
npc_gi.py - Patch: cutscene Gohan wears the armor until the player controls him after the chamber, the gi after.

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r16.gba <r15 patch list> npc_gi
Input:   the ROM after gohan_gi (notes: appearance_copy, the reverse lookup copy), gohan_portraits (notes: block)
         and cutscene_portraits (notes: code, size). Run it last.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["npc_gi"].
Method:  1. Pre-control portraits. The chamber exit (scene table rom:0x3DBDD4) sets Gohan's record to entry 2 at
            seq 3, so the r14 hook maps its two raw-59 lines (seq 16, 21) to the gi. Those two records get raw
            id 121, a new block word equal to word 59 (the armor frame). The hook never maps 121. The block moves
            (it cannot grow in place); rom:0xBE10 and the hook's pool word follow it.
         2. After-control NPC sprite. Every set-56 spawn and actor address in the Cell Games scenes (tables
            rom:0x3E8D98, rom:0x3E93E8), the post-Cell scene (rom:0x3EC758) and the two Cell Games map objects
            becomes set 157. Actor lookup matches by set pointer, so the whole group changes together.
            Two-value pushes `1D 02 70 v` become `00 9D 00 v'` (op 0 twice) in place. Three-value pushes grow by
            one byte (`00 9D` + `1D 02 x y`), so their three records are copied to the expansion area, jumps are
            re-encoded and the one scene-table word is repointed. The old records stay, unreferenced.
         3. The post-Cell ext 73 (0, 56) becomes (0, 157), so playable Gohan leaves Rage in the gi. The reverse
            lookup copy entry 2 +1 becomes 157, so the chamber exit ext 73 must say 157 too (else the assert
            hang). There Gohan is not the leader, so it only writes his record (entry 2 either way).
Rules:   Source: docs\tasks\2026-10-18-npc-gi\npc-gi-report.md, docs\research\re-outfit.md sections 3-5, cutscene-portraits-report.md.
         Pre-control set-56 sites (chamber exit seq 3 spawn, seq 32 walk-off) and all set-53 sites stay vanilla.
         Op 0 pushes a zero-extended byte (@0x08008F44), op 29 a list of zigzag varints. Set 157 has the set 56
         header (slot size). Every site is checked against its old bytes before any write. No palette change.
         After this patch alloc.notes["gohan_portraits"]["block"] is stale: read the block from rom:0xBE10 or
         alloc.notes["npc_gi"]["block"]. Edits to the three moved scenes go to the copies (notes "records").
"""
import hashlib
import struct

# ===== constants =====
ROM_BASE = 0x08000000
ARMOR_SET, GI_SET = 56, 157
SET_TABLE_LITERAL, FIRST_SET = 0x959C, 7
REVERSE_LITERAL, ENTRY, GOHAN_ENTRY = 0x42F0, 20, 2      # reverse lookup copy: entry 2 +1 is the set ext 73 names
PORTRAIT_LITERAL, ARMOR_ID, PRE_ID = 0xBE10, 59, 121     # block literal; raw 59 = armor base; 121 = new copy of it
PRE_CONTROL_RECORDS = (0x3DB930, 0x3DBABC)               # chamber exit seq 16, 21: `10 00 02 3B`, `15 00 02 3B`

# rom offset: (old, new). Op 0 pushes 157 as one byte; two op 0 pushes replace a two-value op 29 list in place.
IN_PLACE = {
    0x3DB627: ("1d020070", "0000009d"),     # chamber exit seq 3: push 0,56 before ext 73 (record write only)
    0x3E8C2B: ("1d027000", "009d0000"),     # Cell Games entry seq 22: push 56,0 ; ext 55
    0x3E8D1D: ("1d027000", "009d0000"),     # seq 26: push 56,0 ; ext 56
    0x3E8D40: ("1d027000", "009d0000"),     # seq 26: push 56,0 ; ext 56
    0x3E921B: ("1d027006", "009d0003"),     # "Me? Fight Cell?" seq 14: push 56,3 ; ext 55
    0x3E9225: ("1d027000", "009d0000"),     # seq 14: push 56,0 ; ext 55
    0x3E939A: ("0038", "009d"),             # seq 21: push 56 ; ext 52 (removes the 14,3 map object)
    0x408CA0: ("38000000", "9d000000"),     # map 14,1 object @0x08408C90 +0x10 (factory @0x0800B710)
    0x408F8C: ("38000000", "9d000000"),     # map 14,3 object @0x08408F80 +0xC (factory @0x0800D6DE)
}
# record: (scene-table word, length, SHA-1, {push offset: (old, new)})
RECORDS = {
    0x3E8610: (0x3E8D98, 0xD2, "fa6e397a3cdb7adce3d562d67639f9942453c9e6", {     # Cell Games entry seq 1
        0x3E866C: ("1d037087408c50", "009d1d0287408c50"),    # push 56,480,808 ; ext 51 (spawn)
        0x3E8681: ("1d037087408b00", "009d1d0287408b00")}),  # push 56,480,704 ; ext 53
    0x3EBE1C: (0x3EC7A4, 0x260, "ad29d6ecf617823afcbbd33aa747230bb0f4d3d5", {    # post-Cell seq 20
        0x3EBFF8: ("1d020070", "0000009d"),                  # push 0,56 ; ext 73
        0x3EC01A: ("1d037086608670", "009d1d0286608670"),    # push 56,432,440 ; ext 51 (spawn)
        0x3EC023: ("1d027002", "009d0001")}),                # push 56,1 ; ext 55
    0x3EC298: (0x3EC7E8, 0x60, "56eb5f09e4cf2f8eb103514312ff294383b533a7", {     # post-Cell seq 37
        0x3EC2CB: ("1d037086008830", "009d1d0286008830"),    # push 56,384,536 ; ext 54
        0x3EC2D4: ("0038", "009d")}),                        # push 56 ; ext 52
}


# ===== script ops (interpreter @0x080092E4) =====
# Moved to scene_lib. Re-bound here: patches.cellgames_ssj, patches.chapter_cards,
# patches.fullpower_ssj, patches.piccolo_gi_scene and patches.vegeta_ssj_scene import them from here.
from scene.scene_lib import _op_end, _varint_end, copy_and_redirect, relocate  # noqa: E402,F401


# ===== patch =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def apply(rom: bytearray, alloc) -> None:
    need = ("gohan_gi", "gohan_portraits", "cutscene_portraits")
    if any(k not in alloc.notes for k in need):
        raise ValueError(f"npc_gi needs the {', '.join(need)} notes: run them first")
    copy = alloc.notes["gohan_gi"]["appearance_copy"]
    block = alloc.notes["gohan_portraits"]["block"]
    ids = max(alloc.notes["gohan_portraits"]["frames"]) + 1             # block words: ids 0-120
    hook = alloc.notes["cutscene_portraits"]

    # checks, before any write
    _expect(rom, REVERSE_LITERAL, _word(copy + ROM_BASE))
    _expect(rom, copy + ENTRY * GOHAN_ENTRY + 1, bytes([ARMOR_SET]))
    table = _u32(rom, SET_TABLE_LITERAL) - ROM_BASE
    sets = [_u32(rom, table + 4 * (s - FIRST_SET)) - ROM_BASE for s in (ARMOR_SET, GI_SET)]
    if rom[sets[0]:sets[0] + 8] != rom[sets[1]:sets[1] + 8]:              # header +0 = OBJ slot size
        raise ValueError(f"set {GI_SET} header differs from set {ARMOR_SET}")
    if ids != PRE_ID:
        raise ValueError(f"portrait block holds {ids} ids, expected {PRE_ID}")
    _expect(rom, PORTRAIT_LITERAL, _word(block + ROM_BASE))
    pools = [o for o in range(hook["code"], hook["code"] + hook["size"], 4) if _u32(rom, o) == block + ROM_BASE]
    if len(pools) != 1:
        raise ValueError(f"hook pool holds the block address {len(pools)} times, expected once")
    for rec in PRE_CONTROL_RECORDS:
        _expect(rom, rec + 1, bytes([0, 2, ARMOR_ID]))
    for off, (old, _) in IN_PLACE.items():
        _expect(rom, off, bytes.fromhex(old))
    # relocate() here only proves every edit lands on an op start, before any write. copy_and_redirect
    # relocates again when it moves the record, so this result is a check and is not kept.
    for rec, (word, length, sha, edits) in RECORDS.items():
        _expect(rom, word, _word(rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} differs from the r14 bytes")
        relocate(rom, rec, length, edits)

    # 1. portrait block with id 121 = the armor frame of id 59
    new_block = alloc.alloc(4 + 4 * (ids + 1))
    rom[new_block:new_block + 4 + 4 * ids] = rom[block:block + 4 + 4 * ids]
    rom[new_block + 4 + 4 * PRE_ID:new_block + 8 + 4 * PRE_ID] = rom[block + 4 + 4 * ARMOR_ID:block + 8 + 4 * ARMOR_ID]
    for off in (PORTRAIT_LITERAL, pools[0]):
        rom[off:off + 4] = _word(new_block + ROM_BASE)
    for rec in PRE_CONTROL_RECORDS:
        rom[rec + 3] = PRE_ID

    # 2-3. set 157 in place, relocated records, reverse lookup copy
    for off, (_, new) in IN_PLACE.items():
        rom[off:off + len(bytes.fromhex(new))] = bytes.fromhex(new)
    moved = {}
    for rec, (word, length, _sha, edits) in RECORDS.items():
        # The scene-table word is the only namer of each record, and copy_and_redirect proves that by
        # searching the whole ROM before it writes. The relocate above ran on the bytes before the IN_PLACE
        # edits; none of those offsets falls inside a RECORDS range, so relocating again here is identical.
        moved[rec] = copy_and_redirect(rom, alloc, rec, length, namers=[word], edits=edits)
    rom[copy + ENTRY * GOHAN_ENTRY + 1] = GI_SET

    alloc.notes["npc_gi"] = {"block": new_block, "pool": pools[0], "records": moved, "pre_id": PRE_ID}
