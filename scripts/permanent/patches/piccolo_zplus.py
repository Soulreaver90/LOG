r"""
piccolo_zplus.py - Patch: Piccolo gains a grade above Super Namek, "Z+", reached FROM Super Namek.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_piccolo_fx.txt
         --out builds\mockups\2026-11-12-powerup-fx\log2_piccolo_zplus_v1.gba
Input:   the ROM after ssj2_form (its relocated appearance table), bf_ki_pool (the ki pool) and
         piccolo_z_start (which moved the Super Namek tick onto the pool tick and took the heal off).
         Art: art\hud_zplus_usable.bin, hud_zplus_dim.bin and the owner's own portrait at
         art\tables\portraits\123_piccolo_zplus.png, all read and never written.
API:     apply(rom, alloc) -> None; addresses and labels in alloc.notes["piccolo_zplus"].
Method:  1. Appearance table: copy the live table and append entry 24, a copy of entry 7 (Super Namek)
            with +4 = 24 (Z+ steps no further) and +5 = 6 (B drops him straight back to base, which is
            what Vegeta's Z+ does). Entry 7 gets +4 = 24, so Super Namek steps up. Every aligned ROM
            word that names the old table is repointed, which is vegeta_zplus's own check reused.
         2. Dialog portrait: entry 24 keeps set 104 and status portrait 18, and takes dialog portrait
            id 123 of its own. The block grows by one word for it, so it relocates and rom:0xBE10 plus
            the hook's pool word follow it, which is npc_gi's move and vegeta_zplus's after it (the
            live block holds ids 0-122, vegeta_zplus's 122 being the last). Id 123's art is the
            owner's own drawing, checked the way a table portrait is checked: at most 64 colours for
            the status page pool, and the outer 3 px frame read against id 121's.
         3. Form object and the ki pool. Entry 24 keeps the Namek form object 0x030021F0, which entry 7
            also holds, so an object compare cannot tell Z+ from Super Namek. The owner wants a pool for
            Z+ alone (2026-11-13), so pool_ref gets an ENTRY test: its `ldr r5,=SSJ_OBJ ; cmp r0,r5` pair
            becomes `bl zp_ref`, the same four bytes, and zp_ref returns the Z flag that the following
            `bne ref_none` already reads. It accepts the Super Saiyan object, or any object in entry 24.
            Only those four bytes are written, because by now vegeta_zplus and this module have repointed
            the appearance table literal that sits inside that same blob.
         4. Stats: the Namek apply 0x080173AA adds 6 to STR, POW and END. Z+ wants 10 (owner,
            2026-11-12), so the apply is wrapped: run the vanilla one, then add 4 more to the three
            bytes it just wrote, but only while the leader wears entry 24.
         5. Heal: the vanilla Super Namek tick added max HP x 0x290 >> 16 on every overflow, and
            piccolo_z_start took it off with the whole tick. The tick is wrapped the same way: run
            piccolo_z_start's pool tick, then, in entry 24 only, run that same heal on an accumulator
            of this module's own. The period and the constant are the vanilla ones.
         6. Gate: ability 11 is Piccolo's transform, not ability 12. Entry 24 goes to the vanilla
            action (which sends message 0x24, revert); entry 7 with EP >= 10 sends message 0x23, the
            SAIYAN transform state 35, not the Namek state 0x25. State 35 runs 0xA0 frames and shares
            its end with state 0x25, it is the state bf_ki_pool's cooldown freeze and ki pool fill
            already hook, and it is the state powerup_fx spawns the aura from. Anything else
            tail-calls the vanilla action unchanged.
         7. The Z+ icon pair is the live ability 11 icon with the Z+ picture pasted in, which keeps
            whatever HUD look the build has, exactly as vegeta_zplus builds Vegeta's.
         8. HUD hook: ability 11 shows the Z+ icon pair in entry 24 and in entry 7 while B steps up,
            else it tail-calls vegeta_zplus's HUD hook. The gate and the HUD share zplus_ok, so the
            icon cannot disagree with B, which is the ssj2_form rule (bible B0454).
Rules:   Z+ has NO story gate. It is open whenever Super Namek is, which is what vegeta_zplus does for
         Vegeta, and it is the only unlock the owner's own save can reach: his Piccolo record already
         has every ability slot open, so the Kami fusion's ext 82 never runs again. Every site is
         checked against its live bytes before any write, and the two wrapped vtable words must still
         hold piccolo_z_start's routines, so this module cannot run out of order or twice. No module
         file or build list of the two masters is edited, so both master SHA-1s are unchanged.
         Hand-assembled Thumb with the ssj2_form assembler; tests\test_piccolo_zplus.py runs it.
"""
import struct

from art import art_tables as at
import log_paths
from patches import bf_ki_pool as pool
from patches import piccolo_z_start as zstart
from patches import vegeta_zplus as veg
from patches.art_inject import FRAME, RAW_HEADER, slot
from patches.ssj2_form import TABLE_LITERALS, assemble
from patches.vegeta_zplus import ICONS, ICON_LEN, bf_look, namers
from rom.webfoot_decompress import ROM_BASE

# ===== constants: sites read on the dev master plus piccolo_z_start, 2026-11-12 =====
M32 = 0xFFFFFFFF
ENTRY, ENTRIES = 20, 24                       # entry size; the live table after vegeta_zplus holds 0-23
PICCOLO_BASE, NAMEK, ZPLUS = 6, 7, 24         # cape (entry 6), Super Namek (entry 7), the new grade
NAMEK_SET, NAMEK_PORTRAIT, NAMEK_STATUS = 104, 94, 18
NAMEK_FORM_OBJECT = 0x030021F0
NAMEK_HEAD = bytes([0x01, NAMEK_SET, NAMEK_PORTRAIT, NAMEK_STATUS, PICCOLO_BASE, PICCOLO_BASE])
BASE_HEAD = bytes([0x00, 103, 90, 17, NAMEK, NAMEK])
TABLE_LITERAL = 0x1954                        # the first of the 17 base literals; the live table address
ABILITY_TABLE, ABILITY_11 = 0x1D9900, 11      # ability 11 is Piccolo's transform (bible: 11 Namek, 12 Saiyan)
ABILITY_11_ACTION = ABILITY_TABLE + 16 * ABILITY_11 + 12
VANILLA_ACTION = 0x080134C1                   # reads entry +0 bit 0: message 0x24 when set, else 0x25
STEP_EP = 10                                  # the ssj2_form step cost, mirrored
NAMEK_VTABLE, APPLY_SLOT, TICK_SLOT = 0x08024ABC, 0x00, 0x04
VANILLA_APPLY = 0x080173AB                    # adds 6 to STR, POW and END at actor +0x160, +0x161, +0x162
STAT_AT, STAT_BONUS = 0x160, 4                # 6 + 4 = 10, the owner's number for Z+
HEAL_STEP, HEAL_RATE = 0x0CCD, 0x290          # the vanilla Namek tick: 1 overflow every 20 frames, x max HP >> 16
HEAL_RAM = 0x03003A10                         # one word past bf_ki_pool's block (its fields end at +0xE)
SAVE_PTR = 0x086F7E50                         # [+4] is the save struct; +0 leader, +0xC the first record
HUD_LITERAL = 0x8E8C                          # the one word that picks the icon of the selected slot
ABILITY_TABLE_GBA = 0x081D9900                # the same table, as the HUD hook loads it
BLOCK_LITERAL, ZPLUS_PORTRAIT, REF_ID = 0xBE10, 123, 121   # the live block holds ids 0-122; 121 is the border
PORTRAIT_PNG = log_paths.TABLE_PORTRAITS / "123_piccolo_zplus.png"

# The pool_ref entry test: the same four bytes, so every label, literal and later address is unchanged.
POOL_OLD = "    ldr r5,=SSJ_OBJ\n    cmp r0,r5\n    bne ref_none\n"
POOL_NEW = "    bl POOL_GATE            ; the Super Saiyan object, or entry 24\n    bne ref_none\n"

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
; ===== 1. is the leader in Z+? r0 = 1 when he is. Leaf: uses r0, r1, r2
in_zplus:
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]       ; leader
    lsl r2,r1,#3
    sub r2,r2,r1
    lsl r2,r2,#2
    add r0,r0,r2
    add r0,#0xc             ; leader record (+0 HP, +2 max HP, +4 EP, +6 max EP, +8 entry)
    ldrb r1,[r0,#0x8]
    cmp r1,#ZPLUS_ENTRY
    beq zp_yes
    mov r0,#0x0
    bx lr
zp_yes:
    mov r0,#0x1
    bx lr
; ===== 1b. pool_gate: bf_ki_pool's own accept, spliced into pool_ref. Z set = this form has a pool.
;     pool_ref calls it with r0 = the form object and r3 = the appearance entry, and reads the Z flag
;     through the `bne ref_none` that already follows. Keeps r1 and r4; uses r2 and the flags.
pool_gate:
    cmp r3,#ZPLUS_ENTRY
    beq pg_done             ; Z+ shares the Namek object, so the ENTRY is what tells it from entry 7
    ldr r2,=SSJ_OBJ
    cmp r0,r2
pg_done:
    bx lr
; ===== 2. apply: the vanilla +6, then +4 more in Z+ (r0 = form object, r1 = actor)
apply_zp:
    push {r4,lr}
    add r4,r1,#0
    ldr r3,=VANILLA_APPLY
    bl via_r3
    bl in_zplus
    cmp r0,#0x0
    beq ap_done
    add r4,#0xff
    add r4,#0x61            ; actor +0x160: STR, POW and END, one byte each
    mov r2,#0x0
ap_next:
    ldrb r0,[r4,r2]
    add r0,#STAT_BONUS
    strb r0,[r4,r2]
    add r2,#0x1
    cmp r2,#0x3
    bne ap_next
ap_done:
    pop {r4,pc}
; ===== 3. tick: piccolo_z_start's pool tick, then the vanilla heal in Z+ (r0 = form object, r1 = actor)
tick_zp:
    push {r4,r5,lr}
    ldr r3,=POOL_TICK
    bl via_r3
    bl in_zplus
    cmp r0,#0x0
    beq tk_done
    ldr r4,=HEAL_RAM
    ldr r0,[r4,#0x0]
    ldr r1,=HEAL_STEP
    add r0,r0,r1
    str r0,[r4,#0x0]
    lsr r1,r0,#16
    beq tk_done             ; no overflow this frame
    lsl r0,r0,#16
    lsr r0,r0,#16
    str r0,[r4,#0x0]
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]
    ldrb r1,[r0,#0x0]
    lsl r2,r1,#3
    sub r2,r2,r1
    lsl r2,r2,#2
    add r0,r0,r2
    add r0,#0xc
    mov r3,#0x2
    ldsh r1,[r0,r3]         ; max HP
    mov r3,#0x0
    ldsh r5,[r0,r3]         ; HP now
    ldr r2,=HEAL_RATE
    mul r2,r1
    asr r2,r2,#16
    add r2,r5,r2
    cmp r2,r1
    ble tk_store
    add r2,r1,#0            ; never past max HP
tk_store:
    strh r2,[r0,#0x0]
tk_done:
    pop {r4,r5,pc}
; ===== 4. zplus_ok: r0 = record. r2 = 1 when B steps up to Z+. Leaf: keeps r0, r1; uses r2, r3
zplus_ok:
    ldrb r2,[r0,#0x8]
    cmp r2,#NAMEK_ENTRY
    bne zo_no               ; not Super Namek
    mov r3,#0x4
    ldsh r2,[r0,r3]
    cmp r2,#STEP_EP
    blt zo_no               ; EP under the step cost
    mov r2,#0x1
    bx lr
zo_no:
    mov r2,#0x0
    bx lr
; ===== 5. gate on ability 11's action (r0 = record, r1 = player)
gate:
    push {lr}
    ldrb r2,[r0,#0x8]
    cmp r2,#ZPLUS_ENTRY
    beq ga_chain            ; Z+ never steps further: the vanilla action reverts it
    bl zplus_ok
    pop {r3}
    mov lr,r3               ; ARMv4T Thumb cannot pop lr
    cmp r2,#0x0
    beq ga_old
    ldr r2,[r1,#0x0]
    ldr r3,[r2,#0x28]
    add r3,r3,r2
    add r0,r1,#0
    mov r1,#0x23
    bx r3                   ; tail call: player message 0x23, the state 35 transform
ga_chain:
    pop {r3}
    mov lr,r3
ga_old:
    ldr r2,=VANILLA_ACTION
    bx r2                   ; tail call: the vanilla ability 11 action, r0 and r1 unchanged
; ===== 6. HUD: the icon of the selected slot (r0 = record, returns the icon in r0). Keeps r4-r7
hud:
    push {r4,r5,r6,lr}
    add r4,r0,#0
    ldrb r0,[r4,#0x9]
    add r0,r0,r4
    ldrb r5,[r0,#0x18]      ; ability id of the selected slot
    cmp r5,#ABILITY_ID
    bne hu_chain
    ldrb r0,[r4,#0x8]
    cmp r0,#ZPLUS_ENTRY
    beq hu_mine             ; in Z+
    add r0,r4,#0
    bl zplus_ok
    cmp r2,#0x0
    beq hu_chain            ; B does not step up to Z+
hu_mine:
    lsl r0,r5,#4
    ldr r1,=ABILITY_TABLE
    add r6,r0,r1
    ldr r1,[r6,#0x8]
    add r0,r4,#0
    bl via_r1               ; r0 = ability test(record): bright or dim
    ldr r1,=ICON_OK
    cmp r0,#0x0
    bne hu_done
    ldr r1,=ICON_DIM
    b hu_done
hu_chain:
    add r0,r4,#0
    ldr r1,=OLD_HUD
    bl via_r1               ; vegeta_zplus's HUD hook picks the Z+, Z2 or vanilla icon
    pop {r4,r5,r6,pc}
hu_done:
    add r0,r1,#0
    pop {r4,r5,r6,pc}
via_r1:
    bx r1
via_r3:
    bx r3
"""


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _target(rom: bytes, vtable: int, slot: int) -> int:
    """A vtable word is an offset from the vtable START, never from the slot (bible B0541)."""
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & M32


def _vword(target: int, vtable: int) -> bytes:
    return struct.pack("<I", (target - vtable) & M32)


def _pool_splice(rom: bytearray, notes: dict, gate: int) -> list:
    """[(file offset, byte)] that turn pool_ref's object compare into the entry test, checked first.

    Only the changed bytes are listed. The whole blob cannot be written back, because vegeta_zplus and
    this module repoint the appearance table literal that lives inside it, and a full write would send
    pool_ref back to a table that has no entry 24.
    """
    if pool.CODE.count(POOL_OLD) != 1:
        raise ValueError("bf_ki_pool pool_ref source changed: the entry test no longer applies")
    ki = notes["bf_ki_pool"]
    plain, plain_labels = zstart.pool_code(notes)
    blob, labels = zstart.pool_code(notes, pool.CODE.replace(POOL_OLD, POOL_NEW), {"POOL_GATE": gate})
    if len(blob) != len(plain):
        raise ValueError(f"the entry test assembled to 0x{len(blob):X} bytes, window is 0x{len(plain):X}")
    moved = sorted(k for k, v in labels.items() if plain_labels.get(k) != v)
    if moved:
        raise ValueError("the entry test moved a label: " + ", ".join(moved))
    changed = [i for i in range(len(blob)) if blob[i] != plain[i]]
    if not changed:
        raise ValueError("the entry test changed no byte")
    first, last = ki["code"] + ROM_BASE + changed[0], ki["code"] + ROM_BASE + changed[-1]
    if not plain_labels["pool_ref"] <= first <= last < plain_labels["fill_end"]:
        raise ValueError(f"the entry test changed bytes outside pool_ref: {[hex(c) for c in changed]}")
    stale = [i for i in changed if rom[ki["code"] + i] != plain[i]]
    if stale:
        raise ValueError("the ki pool code in this ROM is not bf_ki_pool's own at "
                         + ", ".join(f"rom:0x{ki['code'] + i:X}" for i in stale))
    return [(ki["code"] + i, blob[i]) for i in changed]


def _portrait(rom: bytearray, block: int) -> bytes:
    """The owner's Z+ portrait pixels, checked the way art_inject checks a table portrait.

    Nothing is snapped to a near colour and nothing is redrawn: a drawing that fails either check
    stops the build and is named, because his art is his.
    """
    palette = at.load_palette()
    pal, allowed = at.obj_palette(rom, palette), at.allowed_indices(rom, palette)
    px = at.png_pixels(PORTRAIT_PNG, pal, allowed)
    if len(set(px)) > at.MAX_COLORS:
        raise ValueError(f"{PORTRAIT_PNG.name}: {len(set(px))} colors, the status page pool holds {at.MAX_COLORS}")
    ref = at.live_frame(rom, block, REF_ID)[1]
    diff = [i for i in at.RING_IDX if px[i] != ref[i]]
    if diff:
        raise ValueError(f"{PORTRAIT_PNG.name}: the outer {at.RING} px frame differs from id {REF_ID}'s at "
                         f"{len(diff)} of {len(at.RING_IDX)} px, first at "
                         f"x={diff[0] % at.SIDE} y={diff[0] // at.SIDE}")
    return px


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    need = ("ssj2_form", "bf_ki_pool", "piccolo_z_start", "vegeta_zplus")
    if any(k not in alloc.notes for k in need):
        raise ValueError(f"piccolo_zplus needs the {', '.join(need)} notes: run them first")
    if "piccolo_zplus" in alloc.notes:
        raise ValueError("piccolo_zplus already ran")
    start = alloc.notes["piccolo_z_start"]

    # checks, before any write
    table = _u32(rom, TABLE_LITERAL) - ROM_BASE
    _expect(rom, table + ENTRY * PICCOLO_BASE, BASE_HEAD)
    _expect(rom, table + ENTRY * NAMEK, NAMEK_HEAD)
    _expect(rom, table + ENTRY * NAMEK + 0x10, _word(NAMEK_FORM_OBJECT))
    _expect(rom, ABILITY_11_ACTION, _word(VANILLA_ACTION))
    pool_tick = _target(rom, NAMEK_VTABLE, TICK_SLOT)
    if pool_tick != (start["tick"] | 1):
        raise ValueError(f"the Namek tick 0x{NAMEK_VTABLE:08X} +0x{TICK_SLOT:X} names 0x{pool_tick:08X}, "
                         f"not piccolo_z_start's 0x{start['tick'] | 1:08X}")
    apply_now = _target(rom, NAMEK_VTABLE, APPLY_SLOT)
    if apply_now != VANILLA_APPLY:
        raise ValueError(f"the Namek apply 0x{NAMEK_VTABLE:08X} +0 names 0x{apply_now:08X}, "
                         f"not the vanilla 0x{VANILLA_APPLY:08X}")
    spans = alloc.used() + [(off, 4) for off in TABLE_LITERALS]
    table_namers = namers(rom, table + ROM_BASE, spans)
    missing = [off for off in TABLE_LITERALS if off not in table_namers]
    if missing:
        raise ValueError("the table literals " + ", ".join(f"rom:0x{o:X}" for o in missing)
                         + " no longer name the live appearance table")
    if alloc.notes["vegeta_zplus"]["entry"] != ENTRIES - 1:
        raise ValueError(f"vegeta_zplus took entry {alloc.notes['vegeta_zplus']['entry']}, "
                         f"so the live table does not end at entry {ENTRIES - 1}")
    namers(rom, HEAL_RAM, alloc.used())      # raises when any ROM word already names the heal accumulator

    # the Z+ icon pair and the dialog portrait, all checked before the first write
    old_hud = _u32(rom, HUD_LITERAL)
    if old_hud != (alloc.notes["vegeta_zplus"]["hud"] + ROM_BASE + 1):
        raise ValueError(f"rom:0x{HUD_LITERAL:X} names 0x{old_hud:08X}, not vegeta_zplus's HUD hook "
                         f"0x{alloc.notes['vegeta_zplus']['hud'] + ROM_BASE + 1:08X}")
    if veg.ZPLUS_PORTRAIT != ZPLUS_PORTRAIT - 1:
        raise ValueError(f"vegeta_zplus took portrait {veg.ZPLUS_PORTRAIT}, so the block does not "
                         f"end at id {ZPLUS_PORTRAIT - 1}")
    old_block = _u32(rom, BLOCK_LITERAL) - ROM_BASE
    if old_block != alloc.notes["vegeta_zplus"]["block"]:
        raise ValueError(f"rom:0x{BLOCK_LITERAL:X} names block rom:0x{old_block:X}, "
                         f"not vegeta_zplus's rom:0x{alloc.notes['vegeta_zplus']['block']:X}")
    px = _portrait(rom, old_block)
    frame = slot(ZPLUS_PORTRAIT)
    if set(rom[frame:frame + FRAME]) != {0xFF}:
        raise ValueError(f"portrait {ZPLUS_PORTRAIT}: art slot rom:0x{frame:X} is not free")
    art = [(log_paths.ART_UI / name).read_bytes() for name in ICONS]
    if any(len(i) != ICON_LEN for i in art):
        raise ValueError(f"each Z+ icon must be 0x{ICON_LEN:X} bytes")
    live = [_u32(rom, ABILITY_TABLE + 16 * ABILITY_11 + k) - ROM_BASE for k in (0, 4)]
    icons = [bf_look(a, rom[off:off + ICON_LEN]) for a, off in zip(art, live)]
    if any(a == i for a, i in zip(art, icons)):
        raise ValueError("the Z+ icons did not change in the BF look: is bf_hud's icon layout still (3, 2, 18, 9)?")
    block_namers = namers(rom, old_block + ROM_BASE, alloc.used() + [(BLOCK_LITERAL, 4)])

    # 1. allocate; nothing is written until the code size is checked
    new_table = alloc.alloc(ENTRY * (ENTRIES + 1))
    block = alloc.alloc(4 + 4 * (ZPLUS_PORTRAIT + 1))
    usable, dim = alloc.alloc(ICON_LEN), alloc.alloc(ICON_LEN)
    syms = {"ZPLUS_ENTRY": ZPLUS, "NAMEK_ENTRY": NAMEK, "STEP_EP": STEP_EP, "STAT_BONUS": STAT_BONUS,
            "VANILLA_APPLY": VANILLA_APPLY, "VANILLA_ACTION": VANILLA_ACTION, "POOL_TICK": pool_tick,
            "SAVE_PTR": SAVE_PTR, "HEAL_RAM": HEAL_RAM, "HEAL_STEP": HEAL_STEP, "HEAL_RATE": HEAL_RATE,
            "ABILITY_ID": ABILITY_11, "ABILITY_TABLE": ABILITY_TABLE_GBA, "OLD_HUD": old_hud,
            "SSJ_OBJ": pool.SSJ_OBJ,          # the one object pool_ref took before the entry test
            "ICON_OK": usable + ROM_BASE, "ICON_DIM": dim + ROM_BASE}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                     # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    splice = _pool_splice(rom, alloc.notes, labels["pool_gate"])

    # 2. appearance table with entry 24, and entry 7 stepping into it
    entry = bytearray(rom[table + ENTRY * NAMEK:table + ENTRY * (NAMEK + 1)])
    entry[2] = ZPLUS_PORTRAIT                     # its own dialog portrait, the owner's drawing
    entry[4], entry[5] = ZPLUS, PICCOLO_BASE
    rom[new_table:new_table + ENTRY * ENTRIES] = rom[table:table + ENTRY * ENTRIES]
    rom[new_table + ENTRY * ENTRIES:new_table + ENTRY * (ENTRIES + 1)] = entry
    rom[new_table + ENTRY * NAMEK + 4] = ZPLUS
    for off in table_namers:
        rom[off:off + 4] = _word(new_table + ROM_BASE)

    # 3. dialog portrait block with the new id 123
    rom[block:block + 4 + 4 * ZPLUS_PORTRAIT] = rom[old_block:old_block + 4 + 4 * ZPLUS_PORTRAIT]
    rom[frame:frame + FRAME] = RAW_HEADER + px
    rom[block + 4 + 4 * ZPLUS_PORTRAIT:block + 8 + 4 * ZPLUS_PORTRAIT] = _word(frame + ROM_BASE)
    for off in block_namers:
        rom[off:off + 4] = _word(block + ROM_BASE)

    # 4. code, the icons, the two vtable wraps, the ability 11 gate and the HUD hook
    rom[code:code + size] = blob
    rom[usable:usable + ICON_LEN], rom[dim:dim + ICON_LEN] = icons
    ap = NAMEK_VTABLE - ROM_BASE + APPLY_SLOT
    tk = NAMEK_VTABLE - ROM_BASE + TICK_SLOT
    rom[ap:ap + 4] = _vword(labels["apply_zp"] | 1, NAMEK_VTABLE)
    rom[tk:tk + 4] = _vword(labels["tick_zp"] | 1, NAMEK_VTABLE)
    rom[ABILITY_11_ACTION:ABILITY_11_ACTION + 4] = _word(labels["gate"] | 1)
    rom[HUD_LITERAL:HUD_LITERAL + 4] = _word(labels["hud"] | 1)

    # 5. the pool_ref entry test, four bytes inside bf_ki_pool's blob
    for off, value in splice:
        rom[off] = value
    ki = alloc.notes["bf_ki_pool"]
    inside = [o for o in range(ki["code"], ki["code"] + ki["code_len"], 4)
              if _u32(rom, o) == new_table + ROM_BASE]
    if not inside:
        raise ValueError("the appearance table literal inside the ki pool blob no longer names the "
                         "live table: pool_ref would read entry 24 off the end of the old one")

    alloc.notes["piccolo_zplus"] = {
        "table": new_table, "entry": ZPLUS, "code": code, "code_len": size,
        "pool_splice": [off for off, _ in splice],
        "apply_word": ap, "tick_word": tk, "action": ABILITY_11_ACTION, "chained": pool_tick,
        "table_namers": table_namers, "heal_ram": HEAL_RAM, "block": block, "frame": frame,
        "portrait": ZPLUS_PORTRAIT, "block_namers": block_namers, "zplus": usable, "zplus_dim": dim,
        "chained_hud": old_hud,
        **{k: v - ROM_BASE for k, v in labels.items()
           if not k.startswith(("zp_", "ap_", "tk_", "ga_", "zo_", "hu_", "pg_"))}}
