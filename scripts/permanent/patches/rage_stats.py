r"""
rage_stats.py - Patch: Rage adds +20 to STR, POW and END, as playable Super Saiyan 2 does (final, 2026-10-19).

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r20.gba gohan_gi ssj2_form
         gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster
         status_portrait rage_stats
Input:   any ROM with the vanilla Rage form (no notes needed).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["rage_stats"].
Method:  1. Vanilla Rage apply (vtable 0x08024E4C +0, 0x080170D8) writes a flat 100 to player +0x160..+0x162:
            `mov r1,#0x64 ; strb r1,[r0,#0x0] ; strb r1,[r0,#0x1] ; strb r1,[r0,#0x2]` (0x080170E2).
         2. New apply in the expansion area: the leader record's STR, POW, END (+0x0A/+0x0C/+0x0E >> 8) plus 20,
            stored as u8, the same code shape as ssj2_form's apply (no clamp; END 100 + 20 stays <= 127).
            Everything else is the vanilla Rage apply: 0x80 at +0x163/+0x164, walk speed 0x40000000 at +0x188,
            run speed 0x40500000 at +0x18C (through 0x080265C4), drain accumulator +0x184 = 0.
         3. Repoint the Rage vtable +0 word (rom:0x24E4C, base-relative) to the new apply. The IWRAM form object
            0x030021E4 keeps the same vtable, so tick (HP regen), enter (sound 55) and leave stay vanilla.
Rules:   Source: docs\tasks\2026-10-19-r20-build\r20-build.md. The status page (status_bonus) shows live - base, so Rage reads
         "base+20". The old apply stays in the ROM, unreferenced. Every site is checked against its old bytes
         first. Hand-assembled Thumb with the ssj2_form assembler; tests\test_rage_stats.py runs it.
"""
import struct

from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE = 0x08000000
RAGE_VTABLE, VTABLE_WORD = 0x08024E4C, 0x24E4C          # vt_form_rage; +0 = apply
OLD_APPLY, OLD_LEN = 0x080170D8, 0x36
OLD_APPLY_BYTES = bytes.fromhex("10b50c1c201cff30613064210170417081708021c1700171c90528300ff066fa"
                                "201cff308d305a490ff060fa0020ff348134606010bd")
OLD_POOL = (0x17268, 0x40500000)                         # run speed word the old apply loads
FORM_INIT_POOL = 0x2330C                                 # form object init stores this vtable at 0x030021E4
BONUS = 20                                               # ssj2_form: +20 STR, POW, END
WALK, RUN, SPEED_SET = 0x40000000, 0x40500000, 0x080265C5

# ===== new code (ARMv4T Thumb) =====
CODE = """
apply:                      ; r1 = player. Re-encodes 0x080170D8 with leader base + 20 in place of a flat 100
    push {r4,lr}
    add r4,r1,#0
    ldr r0,=0x086f7e50
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r3,r1,#3
    sub r1,r3,r1
    lsl r1,r1,#2
    add r1,r1,r0
    add r1,#0xc             ; r1 = leader record
    add r0,r4,#0
    add r0,#0xff
    add r0,#0x61            ; r0 = player +0x160
    ldrh r2,[r1,#0xa]
    lsr r2,r2,#8
    add r2,#BONUS
    strb r2,[r0,#0x0]
    ldrh r2,[r1,#0xc]
    lsr r2,r2,#8
    add r2,#BONUS
    strb r2,[r0,#0x1]
    ldrh r2,[r1,#0xe]
    lsr r2,r2,#8
    add r2,#BONUS
    strb r2,[r0,#0x2]
    mov r1,#0x80
    strb r1,[r0,#0x3]
    strb r1,[r0,#0x4]
    lsl r1,r1,#23           ; walk speed 0x40000000, as vanilla Rage
    add r0,#0x28
    ldr r2,=SPEED_SET
    bl stub_r2
    add r0,r4,#0
    add r0,#0xff
    add r0,#0x8d
    ldr r1,=RUN
    ldr r2,=SPEED_SET
    bl stub_r2
    mov r0,#0x0
    add r4,#0xff
    add r4,#0x81
    str r0,[r4,#0x4]        ; drain accumulator +0x184
    pop {r4,pc}
stub_r2:
    bx r2
"""


# ===== helpers =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _expect(rom, VTABLE_WORD, _word((OLD_APPLY | 1) - RAGE_VTABLE))
    _expect(rom, OLD_APPLY - ROM_BASE, OLD_APPLY_BYTES)
    _expect(rom, OLD_POOL[0], _word(OLD_POOL[1]))
    _expect(rom, FORM_INIT_POOL, _word(RAGE_VTABLE))
    syms = {"BONUS": BONUS, "RUN": RUN, "SPEED_SET": SPEED_SET}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[code:code + size] = blob
    rom[VTABLE_WORD:VTABLE_WORD + 4] = _word((labels["apply"] | 1) - RAGE_VTABLE)
    alloc.notes["rage_stats"] = {"code": code, "size": size, "apply": labels["apply"] - ROM_BASE,
                                 "vtable_word": VTABLE_WORD}
