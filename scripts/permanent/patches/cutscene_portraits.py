r"""
cutscene_portraits.py - Patch: cutscene dialog shows Gohan's gi portraits once his record wears the gi.

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r14.gba gohan_gi ssj2_form
         gohan_portraits status_bonus ssj2_idle cutscene_portraits
Input:   the ROM after patches.gohan_portraits (alloc.notes["gohan_portraits"]: block, frames 115-120) and
         patches.ssj2_form (alloc.notes["ssj2_form"]["table"]: the relocated appearance table).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["cutscene_portraits"].
Method:  1. Cutscene records pass raw portrait ids (59 = armor, entry 2 vanilla), and portrait() 0x0800BDCC reads
            ids > 7 straight from the table. Ids 1-7 resolve through appearance +2 and then call portrait()
            again with the resolved id (0x08026440), so the id > 7 path also sees Rage's 61 for speaker 1.
         2. The id > 7 path 0x0800BE06-0x0800BE0F (its only entry is `bgt` at 0x0800BDF0) becomes
            `ldr r1,=hook ; bx r1` and the hook address. The block literal at 0x0800BE10 stays: ids 1-7 use it.
         3. The hook reads Gohan's appearance entry (save struct = block word 0, record 0 at +0xC, +8) and maps:
            entry 2, 5 or 22 (gi): 59 to 119 (gi base), 62 to 115 (gi SSJ). Entry 4 (Rage, set 160 = gi):
            61 to 117 (gi SSJ2). Any other id or entry reads the table unchanged. Then `pop {r3,pc}`, as vanilla.
Rules:   Source: docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits-report.md, docs\research\re-portraits.md sections 1 and 3.
         State, not a list: pre-chamber records use 56/57 and Gohan's record is in entry 0 or 1 there, so they
         stay armor. 56, 57, 58 and 60 are never mapped (57 = Future Gohan; no post-chamber record uses the
         others). The hook uses r0, r1 and r3 only (r3 comes back from the pop), so r2 survives as in vanilla.
         The box style switch 0x0800B25E tests the speaker id, never the portrait id: untouched. No palette and
         no +3 (status) path is touched. Every site is checked against its old bytes before any write.
"""
import struct

from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE = 0x08000000
PORTRAIT = 0xBDCC                                  # portrait(id) 0x0800BDCC through its pool word 0x0800BE10
PORTRAIT_VANILLA = bytes.fromhex("08b5002800d108bd0e49012809d108680178cb00591a890008180c301af02afbf1e7"
                                 "072809dc0238c300181a0968800040180c301af01efbe5e70249800004310858e0e7")
SITE, SITE_LEN = 0xBE06, 10                        # id > 7 path: ldr ; lsl ; add ; ldr ; b 0x0800BDD2
BLOCK_LITERAL, STRUCT_WORD = 0xBE10, 0x03000E90
APPEARANCE_ENTRY, GOHAN_ENTRY = 20, 0x14           # record 0 (Gohan) at struct + 0xC, appearance at record +8
GI_ENTRIES = {2: 157, 5: 158, 22: 159}             # entry: gi set id (+1), checked in the relocated table
RAGE_ENTRY, RAGE_SET = 4, 160
GI_MAP = {59: 119, 62: 115}                        # armor dialog id: gi dialog id, in a gi entry
RAGE_MAP = {61: 117}                               # armor Rage: gi SSJ2, in the Rage entry

CODE = """
hook:                       ; r0 = id > 7. portrait() pushed {r3,lr}; ends with pop {r3,pc}, as vanilla
    ldr r1,=BLOCK
    ldr r3,[r1,#0x0]        ; save struct (block word 0, the pointer ids 1-7 use)
    ldrb r3,[r3,#GOHAN_ENTRY]
    cmp r0,#RAGE_ARMOR
    bne hook_gi
    cmp r3,#RAGE_ENTRY
    bne hook_lookup
    mov r0,#RAGE_GI
    b hook_lookup
hook_gi:
    cmp r3,#ENTRY_BASE
    beq hook_map
    cmp r3,#ENTRY_SSJ
    beq hook_map
    cmp r3,#ENTRY_SSJ2
    bne hook_lookup
hook_map:
    cmp r0,#BASE_ARMOR
    bne hook_ssj
    mov r0,#BASE_GI
hook_ssj:
    cmp r0,#SSJ_ARMOR
    bne hook_lookup
    mov r0,#SSJ_GI
hook_lookup:
    lsl r0,r0,#2
    add r1,#0x4
    ldr r0,[r1,r0]
    pop {r3,pc}
"""
SITE_CODE = """
    ldr r1,=HOOK
    bx r1
"""


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def apply(rom: bytearray, alloc) -> None:
    if "gohan_portraits" not in alloc.notes or "ssj2_form" not in alloc.notes:
        raise ValueError("cutscene_portraits needs the gohan_portraits and ssj2_form notes: run them first")
    block, frames = alloc.notes["gohan_portraits"]["block"], alloc.notes["gohan_portraits"]["frames"]
    table = alloc.notes["ssj2_form"]["table"]
    _expect(rom, PORTRAIT, PORTRAIT_VANILLA)
    _expect(rom, BLOCK_LITERAL, _word(block + ROM_BASE))
    _expect(rom, block, _word(STRUCT_WORD))
    for gi in list(GI_MAP.values()) + list(RAGE_MAP.values()):
        _expect(rom, block + 4 + 4 * gi, _word(frames[gi] + ROM_BASE))
    for entry, set_id in list(GI_ENTRIES.items()) + [(RAGE_ENTRY, RAGE_SET)]:
        _expect(rom, table + APPEARANCE_ENTRY * entry + 1, bytes([set_id]))

    (base_armor, base_gi), (ssj_armor, ssj_gi) = GI_MAP.items()
    (rage_armor, rage_gi), = RAGE_MAP.items()
    syms = {"BLOCK": block + ROM_BASE, "GOHAN_ENTRY": GOHAN_ENTRY, "RAGE_ENTRY": RAGE_ENTRY,
            "ENTRY_BASE": 2, "ENTRY_SSJ": 5, "ENTRY_SSJ2": 22, "BASE_ARMOR": base_armor, "BASE_GI": base_gi,
            "SSJ_ARMOR": ssj_armor, "SSJ_GI": ssj_gi, "RAGE_ARMOR": rage_armor, "RAGE_GI": rage_gi}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    site, _ = assemble(SITE_CODE, SITE + ROM_BASE, {"HOOK": labels["hook"] | 1})
    if len(site) != SITE_LEN:                      # ldr, bx, 2 pad bytes, pool word: exactly the old path
        raise ValueError(f"site assembled to {len(site)} bytes, expected {SITE_LEN}")
    rom[code:code + size] = blob
    rom[SITE:SITE + SITE_LEN] = site
    alloc.notes["cutscene_portraits"] = {"code": code, "hook": labels["hook"] - ROM_BASE, "size": size}
