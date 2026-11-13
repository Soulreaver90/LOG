r"""
ki_ramp.py - Patch: the ki bar ramps up over the green bar while the transformation plays.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_piccolo_fx.txt
         --out builds\mockups\2026-11-12-powerup-fx\log2_piccolo_zplus_v2.gba
Input:   the ROM after bf_ki_pool (its pool block, its put_px and its HUD draw) and after fullpower_hud
         (which owns the HUD vtable word). Runs LAST, after powerup_fx, so it chains whatever the state
         tick holds. Needs no art and allocates no table.
API:     apply(rom, alloc) -> None; addresses, labels and the hook words in alloc.notes["ki_ramp"].
Method:  1. SCHEDULE. Buu's Fury ramps its pool LINEARLY, every tick of the transform, with no steps:
            its transform tick `BF 0x0801C4F4` computes `max ki x actor +0x12 / (count << 4)` through
            SWI 6 and stores it. Ours is the same shape on the drawn overlay: `49 x tick / limit`,
            through the game's own divide. The 7 entry gradation table in the draw is a palette ramp,
            not a schedule.
         2. WHICH BAR. Buu's Fury picks the pool from the appearance entry the leader is LEAVING: bit 0
            of entry +0 set means he is already in a super form, so the SECOND (orange) pool ramps, else
            the first (yellow) one. We latch the same test into RAM before the chained tick runs,
            because the landing writes the new entry from inside that tick (bible B2418).
         3. WHERE IT DRAWS. The overlay is a draw, never a value: the pool still arrives in one store at
            the landing frame, so nothing about gameplay changes. The HUD hook calls the live draw first,
            which paints the green EP row and, on a second transformation, the yellow pool bar under us.
            Then the ramp steps go on top through bf_ki_pool's own `put_px`, with the bar colour byte
            set to the latched colour. So yellow goes over green and orange goes over yellow. The byte
            is put back afterwards, because fullpower_hud enters the draw without calling pool_ref and
            would otherwise inherit our colour.
         3b. PICCOLO'S Z+ BAR. His Z+ keeps the Namek form object, so pool_ref draws it the same yellow
            as Super Namek, and the orange ramp would snap back to yellow when the form lands. With no
            ramp live and the leader in entry 24, the steps the live draw just painted (hud_key leaves
            the count at RAM 0x03003A00 +0xC) are repainted orange over themselves. It is paint only:
            pool_ref, the drain and the revert are untouched, and a shrinking bar is already erased by
            bf_ki_pool's own +0xC key.
         4. INTERRUPTION. Buu's Fury zeroes the ramped pool when the transform state leaves without
            completing (`BF 0x0801C552`, +0xC of the sibling transform vtable `0x0804DCA4`). Ours cannot
            hook a leave word it has not measured, so the ramp carries a WATCHDOG instead: the tick
            stamps `0x5A02` and each HUD draw spends one. A tick that stops, for any reason, takes the
            bar off within two drawn frames, and the landing clears it in the same tick that fills the
            pool. The stamp is a magic value because this IWRAM is not cleared at power-on (bible B1632).
         5. TWO STATES. The Saiyan transform is state 35 (`0x08025D9C +4`, 0xA0 ticks) and Piccolo's
            first one is state 0x25 (`0x08025CE0 +4`, 0x40 ticks); both count the actor's own u16 at
            +0x12 and both end by calling their vtable +0x14 (bible B2416, both ticks read again here).
            State 0x25 is hooked ONLY when piccolo_z_start ran, because without it Super Namek has no
            pool and a ramp would have nothing to land on.
         RAM 0x03003A14, two words past piccolo_zplus's heal accumulator: +0 u16 watchdog stamp,
         +2 u8 ramp steps, +3 u8 bar colour, +4 u8 steps last drawn (the repaint key).
Rules:   Every hook word is read live and chained, never assumed, so this module cannot run out of order
         or twice, and powerup_fx's own chain onto state 35 is kept whole. No module file and no build
         list of the two masters is edited, so both master SHA-1s are unchanged. Hand-assembled Thumb
         with the ssj2_form assembler; tests\test_ki_ramp.py decodes and runs it.
"""
import struct

from patches.bf_hud import EP
from patches.ssj2_form import assemble
from patches.vegeta_zplus import namers
from rom.webfoot_decompress import ROM_BASE

# ===== constants: sites read on the dev master plus the trial modules, 2026-11-13 =====
M32 = 0xFFFFFFFF
RAM = 0x03003A00                      # bf_ki_pool's pool block; +0xE is the bar colour put_px reads
RAMP, RAMP_LEN = 0x03003A14, 8        # our own block, clear of piccolo_zplus's heal word 0x03003A10
LIVE = 0x5A02                         # the watchdog stamp: a magic high byte, two drawn frames
STEPS = 0x31                          # 49 EP steps, the full bar (bf_ki_pool's own fill)
DIV = 0x08021F31                      # ARM signed divide r0 = r1 / r0 (bf_ki_pool SYMS["DIV"])
SAVE_PTR, VRAM_OBJ = 0x086F7E50, 0x06010000
TABLE_LITERAL = 0x1954                # the first of the appearance table literals; the live table
HUD_VTABLE, HUD_SLOT = 0x0802408C, 0x10
XFORM_VTABLE, XFORM_SLOT, XFORM_LIMIT = 0x08025D9C, 0x04, 0xA0    # state 35, the Saiyan transform
NAMEK_VTABLE, NAMEK_SLOT, NAMEK_LIMIT = 0x08025CE0, 0x04, 0x40    # state 0x25, Piccolo's first one
VANILLA_NAMEK_TICK = 0x0801560F       # its vanilla tick, which piccolo_z_start leaves alone
NO_ENTRY = 0xFF                       # an appearance entry nothing holds: without piccolo_zplus there is no Z+

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
; ===== 1. the ramp, chained onto a transform state's own tick (r0 = state, r1 = actor)
tick35:
    mov r2,#XFORM_LIMIT
    ldr r3,=CHAIN35
    b ramp_tick
tick25:
    mov r2,#NAMEK_LIMIT
    ldr r3,=CHAIN25
ramp_tick:                  ; r2 = the tick the form lands on, r3 = the tick we chain
    push {r4,r5,r6,r7,lr}
    sub sp,#0x8
    str r0,[sp,#0x0]        ; the state, for the chained tick
    str r3,[sp,#0x4]        ; the tick we chain
    add r5,r1,#0            ; the actor: +0x12 is the state's own frame counter
    add r6,r2,#0
    bl leader
    add r7,r0,#0            ; the leader record
    ldrb r0,[r7,#0x8]
    bl super_entry          ; the entry he is LEAVING, as Buu's Fury reads it
    ldr r3,=RAMP
    strb r0,[r3,#0x3]       ; latched here: the landing rewrites the entry inside the chained tick
    ldrh r0,[r5,#0x12]
    add r0,#0x1             ; the chained tick adds this one
    cmp r0,r6
    ble rt_fill
    add r0,r6,#0            ; never past the landing tick
rt_fill:
    mov r1,#STEPS
    mul r1,r0               ; 49 x tick
    add r0,r6,#0
    ldr r3,=DIV
    bl via_r3               ; r0 = r1 / r0: linear over the whole animation, as Buu's Fury ramps
    ldr r3,=RAMP
    strb r0,[r3,#0x2]
    ldr r0,=LIVE
    strh r0,[r3,#0x0]       ; the watchdog the draw spends: a tick that stops takes the bar off
    ldrb r6,[r7,#0x8]       ; the entry, to tell a landing from an interruption
    ldr r0,[sp,#0x0]
    add r1,r5,#0
    ldr r3,[sp,#0x4]
    bl via_r3               ; the live tick: powerup_fx's aura, bf_ki_pool's meter freeze, the anim
    ldrb r0,[r7,#0x8]
    cmp r0,r6
    beq rt_done             ; still the form he is leaving: the ramp runs on
    ldr r3,=RAMP
    mov r0,#0x0
    strh r0,[r3,#0x0]       ; landed: the pool fills in the same tick and draws the bar itself
rt_done:
    add sp,#0x8
    pop {r4,r5,r6,r7,pc}

; ===== 2. HUD draw (r0 = HUD object, r1 = OAM cursor): the ramp goes OVER the live row
hud_ramp:
    push {r4,r5,r6,r7,lr}
    add r4,r0,#0
    add r5,r1,#0
    bl ramp_now
    add r6,r0,#0            ; the steps to paint this frame
    ldr r3,=RAMP
    ldrb r2,[r3,#0x4]
    cmp r2,r6
    beq hr_call
    strb r6,[r3,#0x4]
    mov r2,#0xff
    strb r2,[r4,#0x15]      ; the cooldown key the vanilla draw repaints on, so a shorter ramp is erased
hr_call:
    add r0,r4,#0
    add r1,r5,#0
    ldr r3,=OLD_HUD
    bl via_r3               ; the live draw: the green EP row, and the pool bar we ramp over
    push {r0}
    cmp r6,#0x0
    bne hr_mine
    bl zplus_steps          ; no ramp: Piccolo's Z+ bar is repainted in its own colour
    add r6,r0,#0
    cmp r6,#0x0
    beq hr_done
    mov r0,#0x1
    b hr_colour
hr_mine:
    ldr r3,=RAMP
    ldrb r0,[r3,#0x3]
hr_colour:
    ldr r3,=RAM
    ldrb r2,[r3,#0xe]
    push {r2}               ; the colour the live draw used, to put back after
    strb r0,[r3,#0xe]       ; put_px reads the bar colour here, on every pixel
    ldrh r0,[r4,#0xc]       ; HUD tile
    lsl r0,r0,#5
    ldr r1,=VRAM_OBJ
    add r4,r0,r1            ; the VRAM base put_px writes through
    ldr r5,=EP_TABLE
    mov r7,#0x0
hr_step:
    lsl r0,r7,#4
    add r0,r0,r5
    ldr r1,[r0,#0x0]
    bl hr_put
    ldr r1,[r0,#0x4]
    bl hr_put
    ldr r1,[r0,#0x8]
    bl hr_put
    add r7,#0x1
    cmp r7,r6
    blt hr_step
    pop {r0}
    ldr r3,=RAM
    strb r0,[r3,#0xe]       ; put it back: fullpower_hud draws without calling pool_ref
hr_done:
    pop {r0}
    pop {r4,r5,r6,r7,pc}
hr_put:                     ; r1 = a buffer offset: bf_ki_pool's put_px, which keeps r0, r1 and r4-r7
    ldr r3,=PUT_PX
    bx r3

; ===== 3. leaves
ramp_now:                   ; r0 = the ramp steps this frame, 0 when no tick has stamped one
    ldr r3,=RAMP
    ldrh r0,[r3,#0x0]
    ldr r2,=LIVE
    cmp r0,r2
    beq rn_spend
    sub r2,#0x1
    cmp r0,r2
    bne rn_none
rn_spend:
    sub r0,#0x1
    strh r0,[r3,#0x0]
    ldrb r0,[r3,#0x2]
    bx lr
rn_none:
    mov r0,#0x0
    bx lr
zplus_steps:                ; r0 = the pool steps the live draw just painted, in Piccolo's Z+ only
    push {r4,lr}
    bl leader
    ldrb r0,[r0,#0x8]
    mov r1,#ZPLUS_ENTRY
    cmp r0,r1
    bne zs_none
    ldr r3,=RAM
    ldrb r0,[r3,#0xc]       ; hud_key leaves the steps it painted here, every frame
    pop {r4,pc}
zs_none:
    mov r0,#0x0
    pop {r4,pc}
leader:                     ; r0 = the leader record, as bf_ki_pool's pool_ref reads it
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r2,r1,#3
    sub r2,r2,r1
    lsl r2,r2,#2            ; record stride 28
    add r0,r0,r2
    add r0,#0xc
    bx lr
super_entry:                ; r0 = an appearance entry, returns 1 when it is already a super form
    lsl r1,r0,#2
    add r1,r1,r0
    lsl r1,r1,#2            ; entry x 20
    ldr r0,=TABLE
    add r0,r0,r1
    ldrb r0,[r0,#0x0]
    lsl r0,r0,#31
    lsr r0,r0,#31           ; +0 bit 0, the bit Buu's Fury tests
    bx lr
via_r3:
    bx r3
"""


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & M32)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def vtable_target(rom: bytes, vtable: int, slot: int) -> int:
    """A vtable word is an offset from the vtable START, never from the slot (bible B0541)."""
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & M32


def _vword(target: int, vtable: int) -> bytes:
    return struct.pack("<I", (target - vtable) & M32)


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    if "ki_ramp" in alloc.notes:
        raise ValueError("ki_ramp already ran")
    for need in ("bf_ki_pool", "fullpower_hud"):
        if need not in alloc.notes:
            raise ValueError(f"ki_ramp needs the {need} notes: run the dev master first")
    pool = alloc.notes["bf_ki_pool"]["labels"]
    namek = "piccolo_z_start" in alloc.notes          # without it Super Namek has no pool to land on
    zplus = "piccolo_zplus" in alloc.notes

    # checks, before any write
    old_hud = vtable_target(rom, HUD_VTABLE, HUD_SLOT)
    want_hud = alloc.notes["fullpower_hud"]["labels"]["hud_fp"] | 1
    if old_hud != want_hud:
        raise ValueError(f"HUD vtable 0x{HUD_VTABLE:08X} +0x{HUD_SLOT:X} names 0x{old_hud:08X}, "
                         f"not fullpower_hud's draw 0x{want_hud:08X}")
    chain35 = vtable_target(rom, XFORM_VTABLE, XFORM_SLOT)
    expect35 = {pool["tick_xform"] | 1}
    if "powerup_fx" in alloc.notes:
        expect35 = {alloc.notes["powerup_fx"]["labels"]["fx_tick"] + ROM_BASE + 1}
    if chain35 not in expect35:
        raise ValueError(f"state 35 vtable 0x{XFORM_VTABLE:08X} +0x{XFORM_SLOT:X} names 0x{chain35:08X}, "
                         f"not the live tick " + ", ".join(f"0x{w:08X}" for w in sorted(expect35)))
    chain25 = vtable_target(rom, NAMEK_VTABLE, NAMEK_SLOT)
    if namek and chain25 != VANILLA_NAMEK_TICK:
        raise ValueError(f"state 0x25 vtable 0x{NAMEK_VTABLE:08X} +0x{NAMEK_SLOT:X} names 0x{chain25:08X}, "
                         f"not the vanilla tick 0x{VANILLA_NAMEK_TICK:08X}")
    for label in ("put_px", "hud_draw", "tick_xform"):
        if label not in pool:
            raise ValueError(f"bf_ki_pool has no {label} label: its code changed under this module")
    namers(rom, RAMP, alloc.used())        # raises when any ROM word already names our RAM block

    # 1. allocate; nothing is written until the code size is checked
    syms = {"XFORM_LIMIT": XFORM_LIMIT, "NAMEK_LIMIT": NAMEK_LIMIT, "STEPS": STEPS, "DIV": DIV,
            "CHAIN35": chain35, "CHAIN25": chain25 if namek else 0, "RAMP": RAMP, "RAM": RAM,
            "LIVE": LIVE, "OLD_HUD": old_hud, "PUT_PX": pool["put_px"] | 1, "SAVE_PTR": SAVE_PTR,
            "ZPLUS_ENTRY": alloc.notes["piccolo_zplus"]["entry"] if zplus else NO_ENTRY,
            "EP_TABLE": EP + ROM_BASE, "VRAM_OBJ": VRAM_OBJ,
            "TABLE": _u32(rom, TABLE_LITERAL)}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                  # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")

    # 2. the code and the hooks
    rom[code:code + size] = blob
    hud = HUD_VTABLE - ROM_BASE + HUD_SLOT
    rom[hud:hud + 4] = _vword(labels["hud_ramp"] | 1, HUD_VTABLE)
    xf = XFORM_VTABLE - ROM_BASE + XFORM_SLOT
    rom[xf:xf + 4] = _vword(labels["tick35"] | 1, XFORM_VTABLE)
    hooks = {"hud": hud, "state35": xf}
    if namek:
        nk = NAMEK_VTABLE - ROM_BASE + NAMEK_SLOT
        rom[nk:nk + 4] = _vword(labels["tick25"] | 1, NAMEK_VTABLE)
        hooks["state25"] = nk

    alloc.notes["ki_ramp"] = {
        "code": code, "code_len": size, "hooks": hooks, "ram": RAMP, "ram_len": RAMP_LEN,
        "chain_hud": old_hud, "chain35": chain35, "chain25": chain25 if namek else None,
        "limits": {"state35": XFORM_LIMIT, "state25": NAMEK_LIMIT if namek else None},
        "zplus_entry": alloc.notes["piccolo_zplus"]["entry"] if zplus else None,
        "labels": {k: v - ROM_BASE for k, v in labels.items()
                   if not k.startswith(("rt_", "hr_", "rn_", "zs_"))}}
