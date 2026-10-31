r"""
ssj2_idle.py - Patch: the idle tick cycles the aura shapes of sets 159 (gi SSJ2) and 160 (gi Rage).

Usage:   py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r13.gba gohan_gi ssj2_form
         gohan_portraits status_bonus ssj2_idle
Input:   the ROM after patches.gohan_gi (alloc.notes["gohan_gi"]: set_159, set_160).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["ssj2_idle"].
Method:  1. The idle tick @0x08007570 (obj+0x12 += 1; obj+0x14 = 1 when (tick & 0xFF) > 0xF0, else 0) is entry +4
            of three state vtables. Vtable words are offsets from the vtable base (target = base + word):
            0x08025A84 (state 0, the player's idle with control), 0x08024BA0 (state 38) and 0x0802588C
            (state 22, enter 0x08007588 sets anim row 22, so it is left vanilla).
         2. The +4 words of 0x08025A84 and 0x08024BA0 point at the hook. The hook tail-calls 0x08007571 with r0,
            r1, lr and sp as at entry unless obj+0x48 is set 159 or 160 AND obj+0x4C is the anim 0 row
            (set + 0x4C). Then it does the vanilla tick step and stores obj+0x14 = body * 3 + ((tick >> 3) % 3),
            body = 1 when (tick & 0xFF) > 0xF0, else 0: the 6 idle records gohan_gi builds per dir. One aura
            shape per 8 ticks (133 ms); r13-r16 used tick >> 2 (67 ms), my r17: "a bit fast".
Rules:   Source: docs\research\re-outfit.md section 7 (enter/tick pairs), re-forms.md section 7 (Thumb only, absolute
         entry pointers, no BL into the expansion area). Caller 0x0800772A: `ldr r2,[r1,#0x4] ; add r2,r2,r1 ;
         add r1,r4,#0 ; bl 0x8021d2c` (r0 = state, r1 = obj); after the call it reloads r0-r2, so the hook may
         use r0, r2 and r3 (ATPCS scratch). Leaf: no push, lr untouched. tick >> 3 < 0x2000, and
         (x * 0x5556) >> 16 is x / 3 exactly for x < 0x8000. Every site is checked before any write.
"""
import struct

from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE = 0x08000000
VANILLA_TICK = 0x08007571
VTABLES = (0x08025A84, 0x08024BA0)                       # state 0 (player idle), state 38
LEFT_VANILLA = 0x0802588C                                # state 22: anim row 22, never the anim 0 row
SETS = (159, 160)
ANIM0_ROW = 0x4C                                         # set + 12 + 16 * 4 dirs (re-outfit.md section 7)

CODE = """
idle:                       ; r0 = state, r1 = obj. Vanilla 0x08007570 unless set 159/160 on its anim 0 row
    ldr r2,[r1,#0x48]
    ldr r3,=SET_SSJ2
    cmp r2,r3
    beq idle_ours
    ldr r3,=SET_RAGE
    cmp r2,r3
    beq idle_ours
idle_vanilla:
    ldr r2,=VANILLA
    bx r2                   ; tail call: r0, r1, lr and sp as at entry
idle_ours:
    add r2,#ANIM0_ROW
    ldr r3,[r1,#0x4c]
    cmp r2,r3
    bne idle_vanilla        ; another anim row: vanilla
    ldrh r0,[r1,#0x12]
    add r0,#0x1
    strh r0,[r1,#0x12]      ; tick += 1, as vanilla
    lsl r2,r0,#16
    lsr r2,r2,#19           ; r2 = (tick & 0xFFFF) >> 3: one shape per 8 ticks
    ldr r3,=0x5556
    mul r3,r2
    lsr r3,r3,#16           ; r3 = r2 / 3
    sub r2,r2,r3
    sub r2,r2,r3
    sub r2,r2,r3            ; r2 = shape 0-2
    lsl r0,r0,#24
    lsr r0,r0,#24
    cmp r0,#0xf1
    blt idle_store          ; body 0 while (tick & 0xFF) <= 0xF0
    add r2,#0x3             ; body 1
idle_store:
    strh r2,[r1,#0x14]
    bx lr
"""


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def apply(rom: bytearray, alloc) -> None:
    if "gohan_gi" not in alloc.notes or not all(f"set_{s}" in alloc.notes["gohan_gi"] for s in SETS):
        raise ValueError("ssj2_idle needs the gohan_gi notes for sets 159 and 160: run gohan_gi first")
    gi = alloc.notes["gohan_gi"]
    for vt in VTABLES + (LEFT_VANILLA,):
        _expect(rom, vt + 4 - ROM_BASE, _word(VANILLA_TICK - vt))
    _expect(rom, (VANILLA_TICK & ~1) - ROM_BASE, bytes.fromhex("488a013048820006"))   # ldrh ; add ; strh ; lsl
    set_table = struct.unpack_from("<I", rom, 0x959C)[0] - ROM_BASE
    for s in SETS:
        _expect(rom, set_table + 4 * (s - 7), _word(gi[f"set_{s}"] + ROM_BASE))

    syms = {"SET_SSJ2": gi["set_159"] + ROM_BASE, "SET_RAGE": gi["set_160"] + ROM_BASE,
            "VANILLA": VANILLA_TICK, "ANIM0_ROW": ANIM0_ROW}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[code:code + size] = blob
    for vt in VTABLES:
        rom[vt + 4 - ROM_BASE:vt + 8 - ROM_BASE] = _word((labels["idle"] | 1) - vt)
    alloc.notes["ssj2_idle"] = {"code": code, "idle": labels["idle"] - ROM_BASE, "size": size}
