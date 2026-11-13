r"""
bf_ki_pool.py - Patch: one Super Saiyan ki pool in the Buu's Fury style, drawn over the EP row (r39, HUD v2b part 2).

Usage:   py -3 -P scripts\permanent\log2_build.py --list --out builds\log2_poc_r39.gba
Input:   the ROM after bf_hud (its EP table places the pool pixels); the Buu's Fury USA ROM (read only).
API:     apply(rom, alloc) -> None; addresses, labels and hook offsets in alloc.notes["bf_ki_pool"].
Method:  New code and the two pool images in one allocation; pointer-level hooks only, no vanilla code byte changes.
         RAM 0x03003A00: +0 u16 pool, +2 u16 tag (0x8000 | leader << 8 | entry), +8 u32 drain accumulator,
         +0xC u8 HUD overlay fill cache, +0xD u8 swap guard, +0xE u8 bar colour (0 yellow, 1 orange).
         - pool_ref: the leader is in a pool form (form object 0x030021EC Super Saiyan, 0x030021E8 the ascended
           grade, or ssj2_form's Super Saiyan 2) and not in the r28 full-power stretch (fullpower_ssj
           stretch_on, leader 0 or 4). A tag that does not match fills the pool to max EP (any way into the
           form gets a full pool). It also writes the bar colour every call: orange for a second transformation
           (the ascended grade and Super Saiyan 2), yellow for a plain Super Saiyan, and 0 when there is no
           pool form, so a later draw never inherits a stale orange bar.
         - Fill: state 35 (transform) vtable 0x08025D9C +0x14 runs vanilla transform(player,1), then a full pool.
           Empty: state 36 (revert) +0x14 runs transform(player,0), then pool 0, tag 0.
         - Drain: Super Saiyan vtable 0x08024C58 +4, the ascended grade vtable 0x0802526C +4 and ssj2_form's
           vtable +4 (were fullpower_ssj's, the vanilla ascended tick and scene_drain_pause's): the vanilla
           base tick 0x08017028 first with the cooldown kept (regular EP
           regenerates), then the r28 stretch, r27 scene and state-0x24 gates, then +STEP per frame into the
           accumulator; per overflow pool -1, or at pool 0 and HP not 0 state 0x24 (BF 0x0800E412-0x0800E46C).
         - Spend: ability tests and actions 0-4, 6-10, 13 (ability table rom:0x1D9900) and the ki states 34 +4,
           46 +8 (Vegeta's hold, v2b), 48 +8, 49 +8, 51 +8 run with the leader record EP swapped for the pool.
         - HUD: vtable 0x0802408C +0x10: when the pool fill (pool x 49 / max EP) changes, HUD +0x15 = 0xFF forces
           the vanilla redraw; then EP steps below the fill get the pool pixels in OBJ VRAM (halfwords), from
           the yellow image or, 0x800 past it, from the orange one. Buu's Fury draws its second bar the same way,
           from a second image at a fixed offset past the first (BF 0x08713FD8, loop 0x0800BB98).
         - Z charge meter, where it empties: the same draw paints index 1 at the CD_TAIL icon bytes when the
           vanilla draw leaves its top charge level (4) at HUD +0x15. bf_hud gives LoG II the Buu's Fury
           meter, which is CD_STEPS pixels, and the vanilla table rom:0x3B5B90 holds CD_SLOTS, so without this
           the last 8 stay lit at every level and the meter never reads empty (Buu's Fury erases all 28).
         - Z charge meter, WHEN it empties: state 35 vtable 0x08025D9C +4 (was the vanilla anim 0x080155E4,
           which adds 8 to the cooldown every frame) runs that anim and then puts the cooldown back, and
           fill_end writes CD_SET in one store. On the landing frame powerup_tick calls fill_end from
           inside the anim, so tick_xform puts the old value back only when the cooldown moved by exactly
           8, which means the anim alone touched it. So the meter stays full through the transformation and
           empties in one step when the form lands, which is Buu's Fury's own order: its landing routine
           stores 0x37FFF to record +4 at BF 0x0801C34C, in the same breath as the pool. The anim's +8 is a
           pure side effect: powerup_tick 0x08011D4A counts its own u16 at actor +0x12 and never reads it.
         Layout = v2b's window plus the orange image: yellow 0x500, pad to 0x800, orange 0x500, the v2 code blob,
         then the st46 blob at the next word. The orange image is the yellow one with its five ramp indices
         swapped for their orange twins, which is exactly what the Buu's Fury pair does.
Rules:   Source: docs\tasks\2026-10-24-r39-build\r39.md, hud-ki-proto-report.md, hud-ki-proto-b-report.md,
         docs\tasks\2026-11-12-orange-ki-bar\rows.md (the Buu's Fury second bar and the orange ramp) and
         docs\tasks\2026-11-12-ki-meter-drain\report.md (the Z charge meter). Every hook word, ability word and
         earlier-patch address is checked before the first write; the new space must be 0xFF and named by no
         ROM word (a named chunk is left unused, notes "skipped"); a second run raises. Drain rates are LoG II's (final decisions open): SSJ 1 every 20 frames,
         SSJ2 1 every 10.
"""
import struct

from patches.bf_hud import BF_CD, CD, CD_COUNTS, COUNTS, EP, load_bf, remap, t_bf, u32
from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF
YELLOW_LEN = 0x500
ORANGE_AT = 0x800                                         # put_px reaches the orange image with one shift, flag << 11
IMAGES_LEN = ORANGE_AT + YELLOW_LEN
# Yellow OBJ index -> its orange twin: #D06000, #F87000, #F89018, #F8B028, #F8D040. The owner chose
# this dark based ramp by eye over the nearer red one, so never "correct" step 1 to a closer match.
ORANGE_RAMP = {41: 33, 40: 32, 46: 39, 131: 38, 123: 37}
BF_YELLOW, BF_KI = 0x713AD8, 0x08071F40
RAM = 0x03003A00
STEP = {"ssj": 0x0CCD, "ssj2": 0x199A}                 # LoG II rates kept: 1 every 20 frames, 1 every 10 frames
WRAP_ABILITIES = (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 13)   # ki moves; 5 has no action, 11 and 12 are transforms
ABILITY_TABLE = 0x1D9900
ABILITY_WORDS = {0: (0x0801315D, 0x08013179), 1: (0x08013191, 0x080131AD), 2: (0x080131C5, 0x080131E1),
                 3: (0x080131F9, 0x08013215), 4: (0x0801322D, 0x08013249), 6: (0x08013261, 0x0801327D),
                 7: (0x080132F3, 0x0801330F), 8: (0x080133F1, 0x0801340D), 9: (0x08013425, 0x08013441),
                 10: (0x0801348D, 0x080134A9), 13: (0x08013459, 0x08013475)}   # vanilla test, action
VANILLA_HOOKS = {                                      # name: (vtable, slot, vanilla target | 1, new label)
    "transform_end": (0x08025D9C, 0x14, 0x0801563D, "fill_end"),
    "revert_end": (0x080256AC, 0x14, 0x080157AF, "empty_end"),
    "hud_draw": (0x0802408C, 0x10, 0x08008BEF, "hud_draw"),
    "ki_blast": (0x08025D48, 0x04, 0x08014DF5, "st34"),
    "beam48": (0x08025CB8, 0x08, 0x08015249, "st48"),
    "beam49": (0x08025F70, 0x08, 0x0801539B, "st49"),
    "ball51": (0x08025CCC, 0x08, 0x080156B7, "st51"),
    "hold46": (0x080258B4, 0x08, 0x08015079, "st46"),       # v2b
    "asc_tick": (0x0802526C, 0x04, 0x080171E5, "tick_ssj"),  # the ascended grade (entries 10, 14 and Vegeta's Z+)
    "xform_tick": (0x08025D9C, 0x04, 0x080155E5, "tick_xform"),  # state 35 anim: the cooldown freeze
}
CD_SLOTS, CD_STEPS, CD_EMPTY, ICON_AT = 20, 28, 4, 0x300   # vanilla table slots, BF meter pixels, top level
CD_TAIL = (0xE0, 0xD9, 0xAE, 0xA7, 0xD8, 0xA6, 0x9F, 0x9E)  # icon bytes of BF meter steps 20-27, checked in _check
CD_CLAMP = (0x8D3E, "042800dd0420")                    # cmp r0,#0x4 ; ble ; mov r0,#0x4: the level reaches 4
CD_WRITEBACK = (0x8D90, "6075")                        # strb r0,[r4,#0x15]: the level this patch reads back
CD_SET = 0x500                                         # 0xA0 transform frames x 8: the value the anim reached
XFORM_ANIM = (0x155E4, "784a08b5d268936808339360fcf7abfb08bd")   # the +8 a frame tick_xform undoes
SSJ_VTABLE, APPEARANCE_LITERAL, BASE_FORM_VTABLE = 0x08024C58, 0x14FF4, 0x08024004
SSJ_OBJ, SSJ, SSJ2 = 0x030021EC, 5, 22
ASC_OBJ, ASC = 0x030021E8, 10                          # the ascended grade form object; entry 10 is Super Vegeta
STRETCH_ON_BYTES = "3c4b1a78920604d59a79120701d40122704700227047"   # fullpower_ssj stretch_on, 22 bytes
CODE_REGION = (0x0, 0x28724)                           # base-relative vtables live here and in ssj2_form's
MAX_TRIES = 4
SYMS = {"RAM": RAM, "SAVE_PTR": 0x086F7E50, "SSJ_OBJ": SSJ_OBJ, "BASE_TICK": 0x08017029, "DIV": 0x08021F31,
        "EP_TABLE": EP + ROM_BASE, "SCENE_FLAG": 0x03001FD8, "SCENE_MGR": 0x03000E1C, "VRAM_OBJ": 0x06010000,
        "VALID": 0x8000, "STEP_SSJ": STEP["ssj"], "STEP_SSJ2": STEP["ssj2"], "CD_EMPTY": CD_EMPTY,
        "ICON_HI": ICON_AT >> 8}

CODE = """
; ===== 1. pool_ref: r0 = RAM when the leader is in a pool form, else 0; r1 = leader record; keeps r4-r7
pool_ref:
    push {r4,r5,lr}
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]        ; save struct 0x03000E90
    ldrb r2,[r0,#0x0]       ; leader
    lsl r1,r2,#3
    sub r1,r1,r2
    lsl r1,r1,#2
    add r1,r1,r0
    add r1,#0xc             ; leader record (+0 HP, +4 EP, +6 max EP, +8 entry)
    ldrb r3,[r1,#0x8]
    lsl r4,r2,#8
    add r4,r4,r3            ; leader << 8 | entry
    lsl r0,r3,#2
    add r0,r0,r3
    lsl r0,r0,#2
    ldr r5,=TABLE
    add r0,r0,r5
    ldr r0,[r0,#0x10]       ; form object of the entry
    ldr r5,=SSJ2_OBJ
    cmp r0,r5
    beq ref_second
    ldr r5,=SSJ_OBJ
    sub r5,#0x4             ; the ascended grade 0x030021E8, off the Super Saiyan literal: no new pool word
    cmp r0,r5
    beq ref_second
    ldr r5,=SSJ_OBJ
    cmp r0,r5
    bne ref_none
    ldr r3,=STRETCH_ON      ; r28 leaf: r2 = 1 when flag 149 is set and flag 195 clear; uses r2, r3
    bl via_r3
    cmp r2,#0x0
    beq ref_first
    lsr r2,r4,#8
    cmp r2,#0x0
    beq ref_none            ; Gohan in the full-power stretch: regular EP, as r28
    cmp r2,#0x4
    beq ref_none            ; Goku in the stretch
ref_first:
    mov r5,#0x0             ; a plain Super Saiyan draws yellow
ref_pool:
    ldr r0,=RAM
    strb r5,[r0,#0xe]       ; bar colour, read by put_px on every pixel
    ldr r3,=VALID
    add r4,r4,r3
    ldrh r3,[r0,#0x2]
    cmp r3,r4
    beq ref_done
    strh r4,[r0,#0x2]       ; new tag: a full pool for this leader and entry
    ldrh r3,[r1,#0x6]
    strh r3,[r0,#0x0]
    mov r3,#0x0
    str r3,[r0,#0x8]
    strb r3,[r0,#0xd]
ref_done:
    pop {r4,r5,pc}
ref_none:
    ldr r5,=RAM
    mov r0,#0x0
    strb r0,[r5,#0xe]       ; no pool form: fullpower_hud enters the draw without calling here, so clear it
    pop {r4,r5,pc}
ref_second:
    mov r5,#0x1             ; a second transformation draws orange
    b ref_pool

; ===== 2. fill and empty: transform and revert ends (state +0x14, r0 = state, r1 = player)
fill_end:
    push {r4,lr}
    ldr r3,=0x0801563d      ; vanilla: sound, transform(player, 1)
    bl via_r3
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]
    ldr r1,=CD_SET
    str r1,[r0,#0x8]        ; the whole cooldown in one store, so the charge meter empties in one step
    ldr r0,=RAM
    mov r1,#0x0
    strh r1,[r0,#0x2]       ; tag 0: pool_ref fills to max EP when the new entry is a pool form
    bl pool_ref
    pop {r4,pc}
; ===== 2b. transform tick: hold the Z charge meter full until the form lands, as Buu's Fury does
tick_xform:
    push {r4,r5,lr}
    ldr r4,=SAVE_PTR
    ldr r4,[r4,#0x4]
    ldr r5,[r4,#0x8]        ; the vanilla anim adds 8 a frame, which drains the meter through the transform
    ldr r3,=0x080155e5
    bl via_r3
    ldr r0,[r4,#0x8]
    sub r0,#0x8
    cmp r0,r5
    bne xform_done          ; on the landing frame powerup_tick called fill_end from inside the anim
    str r5,[r4,#0x8]        ; only the anim moved it: put it back
xform_done:
    pop {r4,r5,pc}

empty_end:
    push {r4,lr}
    ldr r3,=0x080157af      ; vanilla: transform(player, 0)
    bl via_r3
    ldr r0,=RAM
    mov r1,#0x0
    strh r1,[r0,#0x0]       ; the pool empties (BF revert 0x0801C206 zeroes both pools)
    strh r1,[r0,#0x2]
    strb r1,[r0,#0xd]
    pop {r4,pc}

; ===== 3. form ticks (r0 = form object, r1 = player)
tick_ssj:
    ldr r2,=STEP_SSJ
    b tick_go
tick_ssj2:
    ldr r2,=STEP_SSJ2
tick_go:
    push {r4,r5,r6,r7,lr}
    add r5,r1,#0
    add r6,r2,#0
    ldr r4,=SAVE_PTR
    ldr r4,[r4,#0x4]
    ldr r4,[r4,#0x8]        ; transform cooldown (struct +8)
    ldr r3,=BASE_TICK       ; regen underneath, as BF 0x0800E3EC calls its base tick
    bl via_r3
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]
    str r4,[r0,#0x8]        ; cooldown kept: BF counts it down only out of a pool form
    bl pool_ref
    cmp r0,#0x0
    beq tick_done           ; r28 stretch: no drain, no revert
    add r4,r0,#0
    add r7,r1,#0
    ldr r0,=SCENE_FLAG
    ldr r0,[r0,#0x4]
    cmp r0,#0x0
    beq tick_scene_ok
    ldr r0,=SCENE_MGR
    ldr r0,[r0,#0x8]
    cmp r0,#0x0
    bne tick_done           ; r27 scene pause
tick_scene_ok:
    add r0,r5,#0
    ldr r1,[r5,#0x0]
    ldr r2,[r1,#0x2c]
    add r2,r2,r1
    mov r1,#0x24
    bl via_r2               ; player vtable +0x2C: already in state 0x24
    cmp r0,#0x0
    bne tick_done
    ldr r0,[r4,#0x8]
    add r0,r0,r6
    str r0,[r4,#0x8]
    lsr r0,r0,#16
    beq tick_done
    ldrh r0,[r4,#0x0]
    cmp r0,#0x0
    beq tick_empty
    sub r0,#0x1
    strh r0,[r4,#0x0]
    b tick_wrap
tick_empty:
    ldrh r0,[r7,#0x0]       ; HP
    cmp r0,#0x0
    beq tick_wrap
    add r0,r5,#0
    ldr r1,[r5,#0x0]
    ldr r2,[r1,#0x28]
    add r2,r2,r1
    mov r1,#0x24
    bl via_r2               ; player vtable +0x28: state 0x24 (revert)
tick_wrap:
    ldr r0,[r4,#0x8]
    lsl r0,r0,#16
    lsr r0,r0,#16
    str r0,[r4,#0x8]
tick_done:
    pop {r4,r5,r6,r7,pc}

; ===== 4. HUD draw (r0 = HUD object, r1 = OAM cursor)
hud_draw:
    push {r4,r5,r6,r7,lr}
    add r4,r0,#0
    add r5,r1,#0
    mov r6,#0x0
    bl pool_ref
    cmp r0,#0x0
    beq hud_key
    add r7,r1,#0
    ldrh r1,[r0,#0x0]
    mov r3,#0x31
    mul r1,r3               ; pool x 49
    mov r3,#0x6
    ldsh r0,[r7,r3]         ; max EP
    cmp r0,#0x0
    ble hud_key
    ldr r3,=DIV             ; r0 = r1 / r0, as the EP fill @0x08008C9C
    bl via_r3
    add r6,r0,#0
    cmp r6,#0x31
    ble hud_key
    mov r6,#0x31
hud_key:
    ldr r3,=RAM
    ldrb r2,[r3,#0xc]
    cmp r2,r6
    beq hud_call
    strb r6,[r3,#0xc]
    mov r2,#0xff
    strb r2,[r4,#0x15]      ; cooldown key 0xFF: the vanilla draw repaints this frame
hud_call:
    add r0,r4,#0
    add r1,r5,#0
    ldr r3,=0x08008bef
    bl via_r3
    push {r0}
    ldrh r0,[r4,#0xc]       ; HUD tile
    ldrb r5,[r4,#0x15]      ; the Z charge level the vanilla draw wrote back @0x08008D90
    lsl r0,r0,#5
    ldr r1,=VRAM_OBJ
    add r4,r0,r1
    cmp r5,#CD_EMPTY
    bne hud_pool
    bl cd_tail              ; the vanilla table is 8 slots short of the meter, so empty means empty
hud_pool:
    cmp r6,#0x0
    beq hud_done
    ldr r5,=EP_TABLE
    mov r7,#0x0
hud_step:
    lsl r0,r7,#4
    add r0,r0,r5
    ldr r1,[r0,#0x0]
    bl put_px
    ldr r1,[r0,#0x4]
    bl put_px
    ldr r1,[r0,#0x8]
    bl put_px
    add r7,#0x1
    cmp r7,r6
    blt hud_step
hud_done:
    pop {r0}
    pop {r4,r5,r6,r7,pc}
put_px:                     ; r1 = buffer offset, r4 = VRAM base: pixel = IMAGE[r1]; keeps r0, r1, r4-r7
    push {r0,r5}
    ldr r2,=YELLOW
    ldr r0,=RAM
    ldrb r0,[r0,#0xe]
    lsl r0,r0,#11           ; the orange image sits ORANGE_AT = 0x800 past the yellow one
    add r2,r2,r0
    ldrb r2,[r2,r1]
    b px_merge
put_icon:                   ; r1 = icon byte of a Z charge meter step: that pixel = index 1, the empty colour
    push {r0,r5}
    mov r2,#ICON_HI
    lsl r2,r2,#8            ; the meter pixels live in the icon half of the buffer, ICON_AT to 0x4FF
    add r1,r1,r2
    mov r2,#0x1
px_merge:
    lsr r3,r1,#1
    lsl r3,r3,#1
    add r3,r3,r4
    ldrh r0,[r3,#0x0]
    lsl r5,r1,#31
    bmi px_odd
    lsr r0,r0,#8
    lsl r0,r0,#8
    add r0,r0,r2
    b px_put
px_odd:
    lsl r0,r0,#24
    lsr r0,r0,#24
    lsl r2,r2,#8
    add r0,r0,r2
px_put:
    strh r0,[r3,#0x0]
    pop {r0,r5}
    bx lr

; ===== 5. spend from the pool: the leader record EP and the pool trade places around a vanilla call
swap_rec:                   ; ability test or action: r0 = record, r1 = player, r3 = vanilla | 1
    push {r0,r1,r2,r3,r4,r5,lr}
    bl pool_ref
    ldr r2,[sp,#0x0]
    cmp r1,r2
    bne swap_none           ; not the leader record
    b swap_check
swap_state:                 ; state method: r0 = state, r1 = actor, r3 = vanilla | 1
    push {r0,r1,r2,r3,r4,r5,lr}
    bl pool_ref
swap_check:
    cmp r0,#0x0
    beq swap_none
    ldrb r2,[r0,#0xd]
    cmp r2,#0x0
    bne swap_none           ; an outer call holds the swap
    mov r2,#0x1
    strb r2,[r0,#0xd]
    add r4,r0,#0
    add r5,r1,#0
    ldrh r2,[r5,#0x4]
    str r2,[sp,#0x8]        ; regular EP
    ldrh r2,[r4,#0x0]
    strh r2,[r5,#0x4]       ; the vanilla code sees the pool as EP
    ldr r0,[sp,#0x0]
    ldr r1,[sp,#0x4]
    ldr r3,[sp,#0xc]
    bl via_r3
    ldrh r2,[r5,#0x4]
    strh r2,[r4,#0x0]       ; pool = what the move left
    ldr r2,[sp,#0x8]
    strh r2,[r5,#0x4]       ; regular EP back
    mov r2,#0x0
    strb r2,[r4,#0xd]
    add sp,#0x10
    pop {r4,r5,pc}
swap_none:
    pop {r0,r1,r2,r3,r4,r5}
    pop {r2}
    mov lr,r2
    bx r3                   ; vanilla with r0, r1 and lr as at entry
via_r2:
    bx r2
via_r3:
    bx r3

; ===== 8. Z charge meter tail: the meter steps rom:0x3B5B90 has no slot for (one pair each, CD_TAIL)
cd_tail:
    push {r3,lr}
"""
# Generated into CODE itself, not appended by layout(), because fullpower_hud and piccolo_z_start re-assemble
# bf_ki_pool from CODE plus stubs() alone and would otherwise find no cd_tail label.
CODE += "".join(f"    mov r1,#{b:#04x}\n    bl put_icon\n" for b in CD_TAIL) + "    pop {r3,pc}\n"

# v2b: second blob after the v2 blob (its own literal pool), so the v2 code and literals keep their bytes.
FIX_CODE = """
; ===== 7. v2b stubs (state 46 +8: vanilla 0x08015078 drains the leader record EP by 1 a call while B is held)
st46:
    ldr r3,=0x08015079
    b swap_state
"""


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & M32)


def hooks(notes: dict) -> dict:
    """name: (vtable, slot, current target | 1, new label); the two tick words come from the earlier patches."""
    vt2 = notes["ssj2_form"]["vtable"] + ROM_BASE
    return {"ssj_tick": (SSJ_VTABLE, 0x04, notes["fullpower_ssj"]["tick"] + ROM_BASE | 1, "tick_ssj"),
            "ssj2_tick": (vt2, 0x04, notes["scene_drain_pause"]["tick_ssj2"] + ROM_BASE | 1, "tick_ssj2"),
            **VANILLA_HOOKS}


def syms(notes: dict, yellow: int) -> dict:
    form = notes["ssj2_form"]
    return dict(SYMS, TABLE=form["table"] + ROM_BASE, SSJ2_OBJ=form["form_object"] + ROM_BASE,
                STRETCH_ON=notes["fullpower_ssj"]["stretch_on"] + ROM_BASE | 1, YELLOW=yellow, CD_SET=CD_SET)


def stubs() -> tuple:
    """Stub source (one `ldr r3,= ; b` pair per wrapped word) and {name: (file offset of word, vanilla)}."""
    src, words = ["; ===== 6. stubs"], {}
    for n in WRAP_ABILITIES:
        for k, tag, v in ((8, "t", ABILITY_WORDS[n][0]), (12, "a", ABILITY_WORDS[n][1])):
            name = f"ab{n}{tag}"
            words[name] = (ABILITY_TABLE + 16 * n + k, v)
            src += [f"{name}:", f"    ldr r3,={v:#010x}", "    b swap_rec"]
    for name, state in (("st34", "ki_blast"), ("st48", "beam48"), ("st49", "beam49"), ("st51", "ball51")):
        src += [f"{name}:", f"    ldr r3,={VANILLA_HOOKS[state][2]:#010x}", "    b swap_state"]
    return "\n".join(src) + "\n", words


def cd_tail(bf: bytes) -> tuple:
    """Icon bytes of the Buu's Fury charge meter steps the vanilla CD_SLOTS-word table cannot erase."""
    out = tuple(t_bf(u32(bf, BF_CD + 4 * i)) - ICON_AT for i in range(CD_SLOTS, CD_STEPS))
    if len(set(out)) != len(out) or not all(0 <= b <= 0xFF for b in out):
        raise ValueError(f"the charge meter tail is not distinct icon bytes: {out}")
    return out


def yellow_image(bf: bytes) -> bytes:
    """0x500-byte LoG II buffer: the BF yellow pool pixels (image 0x08713AD8) at the ki-row offsets, remapped."""
    img = bytearray(YELLOW_LEN)
    for j in range(41):
        for k in range(3):
            o = u32(bf, BF_KI + 16 * j + 4 * k)
            img[t_bf(o)] = remap(bf[BF_YELLOW + o:BF_YELLOW + o + 1])[0]
    return bytes(img)


def orange_image(yellow: bytes) -> bytes:
    """The same buffer with the five yellow ramp indices swapped for their orange twins, as Buu's Fury does."""
    missing = sorted(set(yellow) - set(ORANGE_RAMP) - {0})
    if missing:
        raise ValueError(f"the yellow pool image holds indices with no orange twin: {missing}")
    return bytes(ORANGE_RAMP.get(v, v) for v in yellow)


def layout(base: int, notes: dict) -> tuple:
    """(code blob, fix blob, labels, {window, yellow, orange, code, code_len, fix, fix_len}) for a GBA `base`."""
    code_at = base + IMAGES_LEN
    stub_src, _ = stubs()
    blob, labels = assemble(CODE + stub_src, code_at, syms(notes, base))
    fix_at = (code_at + len(blob) + 3) & ~3
    fix_blob, fix_labels = assemble(FIX_CODE, fix_at, {"swap_state": labels["swap_state"]})
    if set(fix_labels) & set(labels):
        raise ValueError("label clash")
    return blob, fix_blob, {**labels, **fix_labels}, {
        "window": base, "yellow": base, "orange": base + ORANGE_AT, "code": code_at, "code_len": len(blob),
        "fix": fix_at, "fix_len": len(fix_blob), "size": fix_at + len(fix_blob) - base}


def words_naming(rom: bytes, lo: int, hi: int, rel_ranges: tuple) -> list:
    """File offsets of aligned words naming GBA [lo, hi): absolute anywhere; base-relative (W at P is a vtable
    slot 0-15: P - 4k + W lands in the range) only inside rel_ranges, where those vtables live."""
    out = set()
    for top in range(lo >> 16, ((hi - 1) >> 16) + 1):
        pat, at = struct.pack("<H", top), 2
        while True:
            at = rom.find(pat, at)
            if at < 0:
                break
            if at % 4 == 2 and lo <= u32(rom, at - 2) < hi:
                out.add(at - 2)
            at += 1
    for s, e in rel_ranges:
        for p in range(s, e, 4):
            t = (ROM_BASE + p + u32(rom, p)) & M32
            if lo <= t < hi + 60:
                out.add(p)
    return sorted(out)


# ===== checks =====

def _check(rom: bytearray, alloc) -> dict:
    for need in ("ssj2_form", "scene_drain_pause", "fullpower_ssj", "bf_hud"):
        if need not in alloc.notes:
            raise ValueError(f"bf_ki_pool needs the {need} notes: run the r38 list and bf_hud first")
    if "bf_ki_pool" in alloc.notes:
        raise ValueError("bf_ki_pool already ran")
    notes = alloc.notes
    s = syms(notes, 0)
    stretch = notes["fullpower_ssj"]["stretch_on"]
    if rom[stretch:stretch + 22].hex() != STRETCH_ON_BYTES:
        raise ValueError("stretch_on bytes differ")
    if u32(rom, APPEARANCE_LITERAL) != s["TABLE"]:
        raise ValueError("live appearance table literal moved")
    tb = s["TABLE"] - ROM_BASE
    want = (SSJ_OBJ, s["SSJ2_OBJ"], ASC_OBJ)
    if tuple(u32(rom, tb + 20 * e + 0x10) for e in (SSJ, SSJ2, ASC)) != want:
        raise ValueError(f"form objects of entries {SSJ}, {SSJ2} and {ASC} moved")
    if (BASE_FORM_VTABLE + u32(rom, BASE_FORM_VTABLE + 4)) & M32 != s["BASE_TICK"]:
        raise ValueError("base form tick moved")
    hk = hooks(notes)
    for name, (vt, slot, target, _) in hk.items():
        have = (vt + u32(rom, vt + slot)) & M32
        if have != target:
            raise ValueError(f"{name}: vtable 0x{vt:08X} +0x{slot:X} names 0x{have:08X}, expected 0x{target:08X}")
    for name, (off, v) in stubs()[1].items():
        if u32(rom, off) != v:
            raise ValueError(f"ability word rom:0x{off:X} ({name}) is 0x{u32(rom, off):08X}, expected 0x{v:08X}")
    _check_charge_meter(rom)
    return hk


def _check_charge_meter(rom: bytearray) -> None:
    """The Z charge meter tail is the complement of bf_hud's table, and the vanilla draw still feeds HUD +0x15."""
    bf = load_bf()
    want = [t_bf(u32(bf, BF_CD + 4 * i)) for i in range(CD_SLOTS)]
    if [u32(rom, CD + 4 * i) for i in range(CD_SLOTS)] != want:
        raise ValueError("the cooldown offset table is not bf_hud's Buu's Fury steps: run bf_hud first")
    if [u32(rom, CD_COUNTS + 4 * i) for i in range(len(COUNTS))] != list(COUNTS):
        raise ValueError("the cooldown count table is not bf_hud's")
    if cd_tail(bf) != CD_TAIL:
        raise ValueError(f"the charge meter tail is {cd_tail(bf)}, not the frozen {CD_TAIL}")
    for off, want_hex in (CD_CLAMP, CD_WRITEBACK, XFORM_ANIM):
        if rom[off:off + len(want_hex) // 2].hex() != want_hex:
            raise ValueError(f"rom:0x{off:X} is not the vanilla code this patch reads: re-check the charge meter")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    hk = _check(rom, alloc)
    notes = alloc.notes
    size = layout(ROM_BASE, notes)[3]["size"]
    vt2 = notes["ssj2_form"]["vtable"]
    rel, skipped = (CODE_REGION, (vt2, vt2 + 0x18)), []
    for _ in range(MAX_TRIES):                         # a chunk that a ROM word names stays unused (rom_space rule)
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, rel)
        if not named:
            break
        skipped.append((at, size, named))
    else:
        raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")
    blob, fix_blob, labels, lay = layout(at + ROM_BASE, notes)
    if lay["size"] != size:
        raise ValueError("layout size changed with the address")
    yellow = yellow_image(load_bf())
    _, ab_words = stubs()
    rom[at:at + YELLOW_LEN] = yellow
    rom[at + YELLOW_LEN:at + ORANGE_AT] = bytes(ORANGE_AT - YELLOW_LEN)
    rom[at + ORANGE_AT:at + ORANGE_AT + YELLOW_LEN] = orange_image(yellow)
    rom[lay["code"] - ROM_BASE:lay["code"] - ROM_BASE + len(blob)] = blob
    rom[lay["fix"] - ROM_BASE:lay["fix"] - ROM_BASE + len(fix_blob)] = fix_blob
    hook_words = {}
    for name, (vt, slot, _, label) in hk.items():
        off = vt - ROM_BASE + slot
        rom[off:off + 4] = _word((labels[label] | 1) - vt)
        hook_words[name] = off
    for name, (off, _) in ab_words.items():
        rom[off:off + 4] = _word(labels[name] | 1)
    offsets = {k: v - ROM_BASE if k in ("window", "yellow", "orange", "code", "fix") else v for k, v in lay.items()}
    notes["bf_ki_pool"] = {**offsets, "labels": labels, "hooks": hook_words, "ram": RAM, "skipped": skipped,
                           "cd_tail": list(CD_TAIL),
                           "ability_words": {name: off for name, (off, _) in ab_words.items()}}
