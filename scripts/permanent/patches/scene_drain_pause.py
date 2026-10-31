r"""
scene_drain_pause.py - Patch: no Super Saiyan or Super Saiyan 2 ki drain while a scene plays (final, 2026-10-20).

Usage:   py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r27.gba
Input:   the ROM after patches.ssj2_form (alloc.notes["ssj2_form"]: vtable, tick). Run it last (build list end).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["scene_drain_pause"].
Method:  Two new ticks, each the ssj2_form tick re-encoding with a scene check in front: the drain step is 0xCCD
         (Super Saiyan, as vanilla @0x08017306) or 0x199A (Super Saiyan 2, as ssj2_form). The check skips the
         whole tick when the scene flag is set AND a scene is pushed:
           scene flag  @0x03001FDC (0x03001FD8 +4): 1 from scene setup @0x0800B4EC to cleanup @0x0800B506, the
                       only two writers; all 9 scene-table starters run setup > scene_push > cleanup.
           scene depth @0x03000E24 (scene_manager +8): written only by scene_push and the scene reset
                       @0x0801F346. The depth term covers ext 97 (@0x0800A3E8), which resets the scenes
                       without cleanup and so leaves the flag at 1.
         Then the base-relative tick slot (+4) of the vanilla Super Saiyan vtable 0x08024C58 (rom:0x24C5C) and
         of the ssj2_form vtable point at the new ticks. The vtables are ROM, so a loaded state uses them at once.
Rules:   Source: docs\tasks\2026-10-20-r27-build\cellgames-build.md, scripts\one-time\2026-10-20-r27-build\marker_proof.txt. The vanilla Super Saiyan
         vtable is the one class of form object @0x030021EC, so every Super Saiyan (Gohan, Goku, Vegeta, Trunks)
         pauses in scenes. Rage, Super (Vegeta/Trunks +15), Namek and base ticks stay vanilla. Never touches the
         shared pool @0x080174A0 or the ssj2_form code. Every slot is checked against its old value before any
         write. Hand-assembled Thumb through ssj2_form.assemble; tests\test_cellgames_ssj.py runs it.
"""
import struct

from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE = 0x08000000
SSJ_VTABLE, VANILLA_SSJ_TICK = 0x08024C58, 0x08017307
SCENE_FLAG_BASE, SCENE_MANAGER = 0x03001FD8, 0x03000E1C
STEPS = {"ssj": 0xCCD, "ssj2": 2 * 0xCCD}           # accumulator step per frame (1 EP per 20 or 10 frames)

# ===== new code (ARMv4T Thumb). r1 = player, as the form tick call @0x08008776 passes it =====
CODE = """
tick:
    push {r3,r4,r5,lr}
    add r5,r1,#0
    ldr r0,=SCENE_FLAG_BASE
    ldr r0,[r0,#0x4]
    cmp r0,#0x0
    beq tick_run            ; no scene set up: drain as today
    ldr r0,=SCENE_MANAGER
    ldr r0,[r0,#0x8]
    cmp r0,#0x0
    bne tick_end            ; a scene runs: no drain, no revert
tick_run:
    add r0,r5,#0
    ldr r1,[r5,#0x0]
    ldr r2,[r1,#0x2c]
    add r2,r2,r1
    mov r1,#0x24
    bl stub_r2              ; in state 0x24 (revert)? then skip
    cmp r0,#0x0
    bne tick_end
    add r4,r5,#0
    add r4,#0xff
    add r4,#0x81
    ldr r0,[r4,#0x4]
    ldr r1,=DRAIN_STEP
    add r0,r0,r1
    str r0,[r4,#0x4]
    lsr r0,r0,#16
    beq tick_end
    ldr r0,=0x086f7e50
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r3,r1,#3
    sub r1,r3,r1
    lsl r1,r1,#2
    add r0,r1,r0
    add r0,#0xc
    mov r3,#0x4
    ldsh r2,[r0,r3]         ; EP
    add r1,r0,#4
    cmp r2,#0x1
    bge tick_dec
    mov r2,#0x0
    strh r2,[r1,#0x0]
    b tick_check
tick_dec:
    sub r2,#0x1
    strh r2,[r1,#0x0]
tick_check:
    ldrh r1,[r0,#0x4]
    cmp r1,#0x0
    bne tick_mask
    ldrh r0,[r0,#0x0]
    cmp r0,#0x0
    beq tick_mask
    ldr r1,[r5,#0x0]
    add r0,r5,#0
    ldr r2,[r1,#0x28]
    add r2,r2,r1
    mov r1,#0x24
    bl stub_r2              ; EP 0 and HP not 0: state 0x24 (revert)
tick_mask:
    ldr r0,[r4,#0x4]
    lsl r0,r0,#16
    lsr r0,r0,#16
    str r0,[r4,#0x4]
tick_end:
    pop {r3,r4,r5,pc}
stub_r2:
    bx r2
"""


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _slot_word(vtable: int, target: int) -> bytes:
    """Base-relative vtable word: target address minus the vtable address."""
    return struct.pack("<i", target - vtable)


def _expect_slot(rom: bytearray, vtable: int, target: int) -> None:
    off = vtable - ROM_BASE + 4
    if bytes(rom[off:off + 4]) != _slot_word(vtable, target):
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + 4]).hex()}, expected the tick 0x{target:08X}")


def apply(rom: bytearray, alloc) -> None:
    if "ssj2_form" not in alloc.notes:
        raise ValueError("scene_drain_pause needs the ssj2_form notes: run ssj2_form first")
    if "scene_drain_pause" in alloc.notes:
        raise ValueError("scene_drain_pause already ran")
    form = alloc.notes["ssj2_form"]
    vtables = {"ssj": SSJ_VTABLE, "ssj2": form["vtable"] + ROM_BASE}
    olds = {"ssj": VANILLA_SSJ_TICK, "ssj2": (form["tick"] + ROM_BASE) | 1}
    for k in vtables:
        _expect_slot(rom, vtables[k], olds[k])

    blobs = {}
    for k, step in STEPS.items():
        syms = {"SCENE_FLAG_BASE": SCENE_FLAG_BASE, "SCENE_MANAGER": SCENE_MANAGER, "DRAIN_STEP": step}
        size = len(assemble(CODE, ROM_BASE, syms)[0])
        at = alloc.alloc(size)
        blob, labels = assemble(CODE, at + ROM_BASE, syms)
        if len(blob) != size:                    # pool padding depends on the address
            raise ValueError(f"tick {k} assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
        blobs[k] = (at, blob, labels["tick"])
    for k, (at, blob, tick) in blobs.items():
        rom[at:at + len(blob)] = blob
        off = vtables[k] - ROM_BASE + 4
        rom[off:off + 4] = _slot_word(vtables[k], tick | 1)

    alloc.notes["scene_drain_pause"] = {
        **{f"tick_{k}": at for k, (at, _, _) in blobs.items()},
        **{f"size_{k}": len(blob) for k, (_, blob, _) in blobs.items()},
        "slot_ssj": SSJ_VTABLE - ROM_BASE + 4, "slot_ssj2": form["vtable"] + 4}
