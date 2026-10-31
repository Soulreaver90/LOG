r"""
fullpower_hud.py - Trial patch: the full-power Super Saiyan (r28 stretch) shows the yellow ki row on the HUD and
                   plays no aura sound loop for Goku and Gohan (final, 2026-10-25 12:14 PM).

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_fullpower.txt --out <new .gba>
Input:   the ROM after bf_ki_pool (notes: ssj2_form table, fullpower_ssj stretch_on, bf_ki_pool labels and window).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["fullpower_hud"], every write as (offset, length,
         name) in its "sites".
Method:  The stretch is fullpower_ssj's: flag 149 set and flag 195 clear, leader Gohan (0) or Goku (4).
         1. Yellow ki. bf_ki_pool's pool_ref returns 0 for a Super Saiyan (form object 0x030021EC) leader 0 or 4
            in the stretch, so its HUD draw paints no yellow (root cause). New HUD draw in HUD vtable 0x0802408C
            +0x10: in that case it computes fill = EP x 49 / max EP (0-49, as the vanilla EP row) and enters
            bf_ki_pool's hud_draw at its label hud_key with the same stack frame (push {r4-r7,lr}, r4 = HUD,
            r5 = OAM cursor, r6 = fill), so the yellow covers exactly the green EP steps. Otherwise it tail-calls
            bf_ki_pool's hud_draw unchanged. Pool, drain, spend and regen stay as r39 ("mirror": the yellow row
            is the regular EP, which ki moves spend and the base tick regenerates).
         2. Aura loop. The Super Saiyan enter 0x08017376 starts sound entry 55 (0x080E15B0 + 0x294, flags 1 =
            loop) and leave 0x08017392 stops it. New enter in Super Saiyan vtable 0x08024C58 +8: in the stretch
            with leader 0 or 4 it returns at once; else it tail-calls the vanilla enter. ssj2_form's vtable
            (+8 also names 0x08017377), Rage (0x08024E4C) and the transform state 35 sound stay vanilla, so
            Super Saiyan 2 and Rage keep the loop. Every enter caller (Continue, set_leader, ext 73, transform,
            menu return) picks the form from the leader byte, so the leader byte is the right key.
Rules:   Source: docs\tasks\2026-10-25-fullpower-hud\fullpower-hud-trial.md, fullpower-hud-report.md. Both vtable
         words, the vanilla enter bytes, the stretch_on bytes, the DIV entry, the form objects of entries 5 and 20,
         and bf_ki_pool's code (re-assembled at its window, and its hud_key-to-put_px bytes pinned) are checked
         before the first write; the new space must be 0xFF and named by no ROM word; a second run raises.
         Hand-assembled Thumb through ssj2_form.assemble; tests\test_fullpower_hud.py decodes it with thumb_dis.
"""
import hashlib
import struct

from patches import bf_ki_pool
from patches.bf_ki_pool import words_naming
from patches.ssj2_form import assemble

# ===== constants: sources (r39 bytes, re-read 2026-10-25) =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF
STRUCT, SSJ_OBJ = 0x03000E90, 0x030021EC
GOHAN, GOKU = 0, 4
SSJ_ENTRIES = (5, 20)                                    # Gohan gi Super Saiyan, Goku Super Saiyan
SSJ_VTABLE, ENTER_SLOT, VANILLA_ENTER = 0x08024C58, 0x8, 0x08017377
ENTER_BYTES = (0x17376, "10b54448a521444a89008918444c006840220023001908f086fc10bd")   # sound_start(mgr, entry 55)
HUD_VTABLE, HUD_SLOT = 0x0802408C, 0x10
DIV = 0x08021F31                                         # ARM signed divide r0 = r1 / r0 (bf_ki_pool SYMS["DIV"])
DIV_BYTES = (0x21F30, "78470000802410e2")                # bx pc ; ARM
STRETCH_ON_BYTES = bf_ki_pool.STRETCH_ON_BYTES           # fullpower_ssj stretch_on, 22 bytes
HUD_KEY = (0x4A, "f3cb6d1d5806eeea0f101eedfde389110f112f74")   # hud_key to put_px in r39: length, SHA-1
FILL_MAX = 0x31                                          # 49 EP steps
CODE_REGION = bf_ki_pool.CODE_REGION
MAX_TRIES = 8

# ===== new code (ARMv4T Thumb) =====
CODE = """
; ===== 1. aura gate: Super Saiyan vtable +8 (r0 = form object). No sound 55 loop for Gohan or Goku in the stretch
enter_fp:
    push {lr}
    ldr r3,=STRETCH_ON
    bl via_r3               ; r28 leaf: r2 = 1 when flag 149 is set and flag 195 clear; uses r2, r3
    pop {r3}
    mov lr,r3
    cmp r2,#0x0
    beq enter_old
    ldr r3,=STRUCT
    ldrb r3,[r3,#0x0]       ; leader
    cmp r3,#GOHAN
    beq enter_quiet
    cmp r3,#GOKU
    bne enter_old
enter_quiet:
    bx lr
enter_old:
    ldr r2,=OLD_ENTER
    bx r2                   ; vanilla enter with r0, r1 and lr as the caller passed them

; ===== 2. HUD draw: HUD vtable +0x10 (r0 = HUD object, r1 = OAM cursor)
hud_fp:
    push {r4,r5,r6,r7,lr}   ; the frame bf_ki_pool's hud_draw builds before hud_key
    add r4,r0,#0
    add r5,r1,#0
    bl ep_fill
    cmp r0,#FILL_MAX
    bgt hud_pool
    add r6,r0,#0
    ldr r3,=HUD_KEY
    bx r3                   ; bf_ki_pool hud_draw from hud_key: r4 = HUD, r5 = OAM cursor, r6 = yellow steps
hud_pool:
    add r0,r4,#0
    add r1,r5,#0
    pop {r4,r5,r6,r7}
    pop {r3}
    mov lr,r3
    ldr r3,=OLD_HUD
    bx r3                   ; bf_ki_pool hud_draw with r0, r1 and lr as at entry
ep_fill:                    ; r0 = EP x 49 / max EP (0-49) for a Gohan or Goku leader in Super Saiyan in the stretch, else 0xFF
    push {r4,r5,r6,r7,lr}
    ldr r3,=STRETCH_ON
    bl via_r3
    cmp r2,#0x0
    beq fill_none
    ldr r0,=STRUCT
    ldrb r2,[r0,#0x0]       ; leader
    cmp r2,#GOHAN
    beq fill_leader
    cmp r2,#GOKU
    bne fill_none
fill_leader:
    lsl r1,r2,#3
    sub r1,r1,r2
    lsl r1,r1,#2
    add r1,r1,r0
    add r1,#0xc             ; leader record (+4 EP, +6 max EP, +8 entry)
    ldrb r3,[r1,#0x8]
    lsl r0,r3,#2
    add r0,r0,r3
    lsl r0,r0,#2
    ldr r3,=TABLE
    add r0,r0,r3
    ldr r0,[r0,#0x10]       ; form object of the entry
    ldr r3,=SSJ_OBJ
    cmp r0,r3
    bne fill_none           ; base, Rage, Super Saiyan 2: bf_ki_pool decides
    mov r3,#0x4
    ldsh r4,[r1,r3]         ; EP
    mov r3,#0x6
    ldsh r0,[r1,r3]         ; max EP
    cmp r0,#0x0
    ble fill_zero
    cmp r4,#0x0
    ble fill_zero
    mov r3,#FILL_MAX
    mul r4,r3
    add r1,r4,#0
    ldr r3,=DIV
    bl via_r3               ; r0 = r1 / r0, as the vanilla EP fill
    cmp r0,#FILL_MAX
    ble fill_done
    mov r0,#FILL_MAX
    b fill_done
fill_zero:
    mov r0,#0x0
    b fill_done
fill_none:
    mov r0,#0xff
fill_done:
    pop {r4,r5,r6,r7,pc}
via_r3:
    bx r3
"""


# ===== helpers =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _slot(rom: bytes, vtable: int, slot: int) -> int:
    """GBA address a base-relative vtable word names."""
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & M32


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def syms(notes: dict) -> dict:
    lab = notes["bf_ki_pool"]["labels"]
    return {"STRETCH_ON": (notes["fullpower_ssj"]["stretch_on"] + ROM_BASE) | 1, "STRUCT": STRUCT,
            "GOHAN": GOHAN, "GOKU": GOKU, "OLD_ENTER": VANILLA_ENTER, "FILL_MAX": FILL_MAX,
            "HUD_KEY": lab["hud_key"] | 1, "OLD_HUD": lab["hud_draw"] | 1,
            "TABLE": notes["ssj2_form"]["table"] + ROM_BASE, "SSJ_OBJ": SSJ_OBJ, "DIV": DIV}


def hud_key_bytes(rom: bytes, notes: dict) -> bytes:
    """bf_ki_pool's hud_draw from hud_key up to put_px: the code hud_fp enters."""
    lab = notes["bf_ki_pool"]["labels"]
    return bytes(rom[lab["hud_key"] - ROM_BASE:lab["put_px"] - ROM_BASE])


# ===== checks =====

def _check(rom: bytearray, alloc) -> dict:
    for need in ("ssj2_form", "fullpower_ssj", "bf_ki_pool"):
        if need not in alloc.notes:
            raise ValueError(f"fullpower_hud needs the {need} notes: run the r39 list first")
    if "fullpower_hud" in alloc.notes:
        raise ValueError("fullpower_hud already ran")
    notes = alloc.notes
    s = syms(notes)
    stretch = notes["fullpower_ssj"]["stretch_on"]
    if rom[stretch:stretch + 22].hex() != STRETCH_ON_BYTES:
        raise ValueError("stretch_on bytes differ")
    _expect(rom, ENTER_BYTES[0], bytes.fromhex(ENTER_BYTES[1]))
    _expect(rom, DIV_BYTES[0], bytes.fromhex(DIV_BYTES[1]))
    if _slot(rom, SSJ_VTABLE, ENTER_SLOT) != VANILLA_ENTER:
        raise ValueError(f"Super Saiyan vtable +8 names 0x{_slot(rom, SSJ_VTABLE, ENTER_SLOT):08X}, "
                         f"expected 0x{VANILLA_ENTER:08X}")
    if _slot(rom, HUD_VTABLE, HUD_SLOT) != s["OLD_HUD"]:
        raise ValueError(f"HUD vtable +0x10 names 0x{_slot(rom, HUD_VTABLE, HUD_SLOT):08X}, "
                         f"expected bf_ki_pool hud_draw 0x{s['OLD_HUD']:08X}")
    tb = s["TABLE"] - ROM_BASE
    for e in SSJ_ENTRIES:
        if _u32(rom, tb + 20 * e + 0x10) != SSJ_OBJ:
            raise ValueError(f"entry {e} form object moved")
    pool = notes["bf_ki_pool"]
    blob, fix_blob, labels, lay = bf_ki_pool.layout(pool["window"] + ROM_BASE, notes)
    if bytes(rom[pool["code"]:pool["code"] + len(blob)]) != blob or labels != pool["labels"]:
        raise ValueError("bf_ki_pool code differs from its source at the r39 window")
    code = hud_key_bytes(rom, notes)
    if (len(code), hashlib.sha1(code).hexdigest()) != HUD_KEY:
        raise ValueError("bf_ki_pool hud_key code changed: re-check the hud_fp entry contract")
    return s


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    s = _check(rom, alloc)
    size, skipped = len(assemble(CODE, ROM_BASE, s)[0]), []
    vt2 = alloc.notes["ssj2_form"]["vtable"]
    rel = (CODE_REGION, (vt2, vt2 + 0x18))
    for _ in range(MAX_TRIES):                           # a chunk that a ROM word names stays unused (rom_space rule)
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, rel)
        if not named:
            break
        skipped.append((at, size, named))
    else:
        raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")
    blob, labels = assemble(CODE, at + ROM_BASE, s)
    if len(blob) != size:                                # pool padding depends on the address
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    enter_word, hud_word = SSJ_VTABLE - ROM_BASE + ENTER_SLOT, HUD_VTABLE - ROM_BASE + HUD_SLOT
    rom[at:at + size] = blob
    rom[enter_word:enter_word + 4] = struct.pack("<I", ((labels["enter_fp"] | 1) - SSJ_VTABLE) & M32)
    rom[hud_word:hud_word + 4] = struct.pack("<I", ((labels["hud_fp"] | 1) - HUD_VTABLE) & M32)
    alloc.notes["fullpower_hud"] = {
        "code": at, "size": size, "labels": labels, "skipped": skipped,
        "sites": [(enter_word, 4, "Super Saiyan vtable +8 (enter)"), (hud_word, 4, "HUD vtable +0x10 (draw)"),
                  (at, size, "fullpower_hud code")]}
