r"""
vegeta_zplus.py - Patch: Vegeta's Z+ grade, gated on the Time Chamber exit the game already has.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_vegeta_zplus.txt
         --out builds\mockups\2026-11-12-zplus-unlock\log2_zplus_v2.gba
Input:   the ROM after the dev master. Reads alloc.notes["ssj2_form"] (its relocated table, gate, HUD hook and
         step_ok), alloc.notes["npc_gi"] (the live dialog portrait block) and alloc.notes["art_inject"].
         Art: art\hud_zplus_usable.bin, hud_zplus_dim.bin, art\tables\portraits\122_vegeta_grade2.png.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["vegeta_zplus"].

The unlock is the game's own chamber exit, and it is DATA, not a flag:

    before the chamber   base entry 8   Z = entry 11 (set 140, +10)   Z+ unreachable
    after the chamber    base entry 9   Z = entry 23 (set 140, +10)   Z+ = entry 10 (set 139, +15)

    Vanilla `ext 73 (2, 138)` at rom:0x3DE6BB moves Vegeta from entry 8 to entry 9 in the chamber exit
    scene, and nothing in the ROM moves him back: the only `ext 73 (2, 137)` is at rom:0x3E778B, which
    is Android 16 at Capsule Corp, BEFORE the chamber. So entry 9 is the post-chamber state, and which
    grade a base entry can reach is decided by its +4 chain alone. This module writes no flag, sets no
    ability bit and adds no unlock code.

Method:  1. Appearance table: copy the live 23 entry table to a 24 entry one and append entry 23, the
            POST-CHAMBER Super Saiyan: entry 11 copied, with +4 = 10 (B steps up to Z+) and +5 = 9 (it
            reverts to post-chamber base). It keeps entry 11's set 140, portrait 107 and ordinary Super
            Saiyan form object 0x030021EC, so it is the same Z, only one that can go further.
            Entry 9 (post-chamber base) gets +4 = 23, so his Z after the chamber is the new entry.
            Entry 10, which vanilla already reached from entry 9, BECOMES Z+: its portrait becomes 122,
            the owner's drawing, and its ascended form object 0x030021E8 (+15 STR, +10 POW, +15 END) is
            left alone, because that grade is the point of it.
            Entry 11 is not touched: its +4 stays 8, so pre-chamber Vegeta reaches Z and stops. THAT IS
            THE GATE. Every aligned ROM word that names the old table is repointed, which is 17 base
            literals plus one literal pool word in each later module that reads the table (ssj2_form,
            status_bonus, fullpower_ssj, bf_ki_pool, fullpower_hud).
         2. Dialog portrait: the block grows by one word for the new id 122, which points at the fixed art
            slot art_inject would use. Id 121 is NOT free: npc_gi gave it the armor frame and points the two
            chamber exit lines at it (see the report), so the owner's portrait takes the next id instead.
         3. Sets 140 (the set the step comes FROM) and 139 (Z+ itself, now stepped INTO) each borrow set
            137's anim 9 row. The record lookup indexes the animation table by number with no existence
            test (bible B0041), and every vanilla SUPER set except Gohan's 59 has a NULL anim 9, so
            without this a power-up follows a null record list and the game crashes. Sets 137 and 138,
            the two base sets of the chain, carry a live anim 9 of their own.
            borrow_anim_row is reusable: Trunks 133 from 132, Goku 61 from 60 and Piccolo 104 from 103
            have the same hole. Only Vegeta is wired here.
         4. Gate on the ability 12 action: entry 10 goes straight to the vanilla action (message 0x24,
            revert); entry 23 with EP >= 10 sends message 0x23 (step up to Z+); anything else tail-calls
            ssj2_form's gate. This gate is the Super Saiyan to Super Saiyan STEP, not the unlock. A step
            cannot be data alone, because the vanilla action reverts out of every super entry, and
            ssj2_form's own step_ok reads story flag 195, which must not gate Vegeta.
         5. The Z+ icon pair is the live ability 12 icon with the Z+ picture pasted in, which keeps whatever
            HUD look the build has. bf_hud (r39) moves every icon picture to the Buu's Fury layout, and it
            runs before this module, so the art files cannot be written in raw.
         6. HUD hook: ability 12 shows the Z+ icon pair in entry 10 and in entry 23 while B steps up, else it
            tail-calls ssj2_form's HUD hook. The gate and the HUD share zplus_ok, so the icon cannot disagree
            with B, which is the ssj2_form rule (bible B0454).
Rules:   Every site is checked against its live bytes before any write, the two chamber exit `ext 73` ops are
         checked and never written, and the two hooks must still hold ssj2_form's own routines, so this module
         cannot run out of order or twice. No module file of the two masters is edited and
         art\tables\portraits.json is untouched, so both master SHA-1s are unchanged.
         Hand-assembled Thumb with the ssj2_form assembler; tests\test_vegeta_zplus.py decodes and runs it.
"""
import struct

import log_paths
from art import art_tables as at
from patches.art_inject import FRAME, RAW_HEADER, slot
from patches.ssj2_form import TABLE_LITERALS, assemble
from rom.webfoot_decompress import ROM_BASE, SET_DIRS, read_record, read_set, rom_ptr
from scene import scene_lib as sl

# ===== constants =====
ART = log_paths.ART
ENTRY, ENTRIES = 20, 23                             # the live table ssj2_form built: entries 0-22
PRE_BASE, POST_BASE = 8, 9                          # Vegeta before and after the Time Chamber exit
PRE_Z, ZPLUS, POST_Z = 11, 10, 23                   # Z before the chamber; Z+; the new Z after the chamber
ZPLUS_SET, ZPLUS_PORTRAIT = 139, 122                # set 139 is the ascended grade art; 122 is the new dialog id
ASCENDED_OBJ, ORDINARY_OBJ = 0x030021E8, 0x030021EC  # ascended (+15/+10/+15) and plain Super Saiyan (B0427)
PRE_BASE_HEAD = bytes([0x00, 137, 106, 24, PRE_Z, PRE_Z])
POST_BASE_HEAD = bytes([0x00, 138, 106, 24, ZPLUS, ZPLUS])
ZPLUS_HEAD = bytes([0x01, ZPLUS_SET, 107, 25, POST_BASE, POST_BASE])
PRE_Z_HEAD = bytes([0x01, 140, 107, 25, PRE_BASE, PRE_BASE])
# The chamber exit ops that do the unlocking. Checked, never written: `ext 73 (2, 138)` is the one op in the
# base ROM that moves Vegeta to entry 9, and `ext 73 (3, 129)` is Trunks' mirror, 7 bytes earlier. They are
# read through the scene TABLE WORD, never at rom:0x3DE620: fullpower_ssj relocates that record and repoints
# the word, so the vanilla address holds a dead copy in every build of the two masters.
EXIT_TABLE_WORD = 0x3DE774                          # scene table word of chamber exit seq 33 (next index 33)
EXIT_OPS = (sl.ext(73, 2, 138), sl.ext(73, 3, 129))
TABLE_LITERAL = 0x1954                              # the first of the 17 base literals; the live table address
ABILITY_12_ACTION, VANILLA_ACTION = 0x1D99CC, 0x0801353D
HUD_LITERAL, ABILITY_TABLE = 0x8E8C, 0x081D9900
BLOCK_LITERAL, BLOCK_IDS, REF_ID = 0xBE10, 122, 121  # block words 0-121; id 121's frame is the portrait border
STEP_EP = 10                                        # the ssj2_form step cost, mirrored (ssj2_form.STEP_EP)
ICONS = ("hud_zplus_usable.bin", "hud_zplus_dim.bin")
ICON_LEN, ABILITY_12 = 0x200, 12
PICTURE, SOURCE_DX = (3, 2, 18, 9), 10   # bf_hud puts the LoG II picture, columns 13-28, at columns 3-18
PORTRAIT_PNG = log_paths.ART_TABLES / "portraits" / "122_vegeta_grade2.png"
SET_TABLE_LITERAL, FIRST_SET = 0x959C, 7
POWER_UP, REVERT = 9, 21             # animation rows: 9 powers up, 21 reverts
VEG_Z_SET, VEG_BASE_SET = 140, 137   # the step comes FROM 140, which has no anim 9 of its own
BORROWERS = (VEG_Z_SET, ZPLUS_SET)   # both Vegeta super sets need one, and 137 lends to both
CHAIN_SETS = (137, 138, 140, 139)    # every set the entry chain walks through; each needs a live anim 9
BASE_CHAIN_SETS = (137, 138)         # the two of them that carry one in vanilla: checked, never written

# ===== new code (ARMv4T Thumb). Symbols in caps are filled in at assembly =====
CODE = """
zplus_ok:                   ; r0 = record. r2 = 1 when B steps up to Z+. Leaf: keeps r0, r1; uses r2, r3
    ldrb r2,[r0,#0x8]
    cmp r2,#POST_Z
    bne zp_no               ; not the post-chamber Super Saiyan, so no step: pre-chamber Z ends here
    mov r3,#0x4
    ldsh r2,[r0,r3]
    cmp r2,#STEP_EP
    blt zp_no               ; EP under the step cost
    mov r2,#0x1
    bx lr
zp_no:
    mov r2,#0x0
    bx lr
gate:                       ; r0 = record, r1 = player. Every exit tail-jumps with the caller's lr and sp
    push {lr}
    ldrb r2,[r0,#0x8]
    cmp r2,#ZPLUS_ENTRY
    beq gate_revert         ; Z+ never steps further, whatever its +4 says
    bl zplus_ok
    pop {r3}
    mov lr,r3               ; ARMv4T Thumb cannot pop lr
    cmp r2,#0x0
    beq gate_chain
    ldr r2,[r1,#0x0]
    ldr r3,[r2,#0x28]
    add r3,r3,r2
    add r0,r1,#0
    mov r1,#0x23
    bx r3                   ; tail call: player message 0x23 (transform into Z+)
gate_revert:
    pop {r3}
    mov lr,r3
    ldr r2,=VANILLA_ACTION
    bx r2                   ; tail call: the vanilla action sends message 0x24 (revert) for a super entry
gate_chain:
    ldr r2,=SSJ2_GATE
    bx r2                   ; tail call: ssj2_form's gate, r0 and r1 unchanged
hud:                        ; r0 = record, returns the icon in r0. Keeps r4-r7
    push {r4,r5,r6,lr}
    add r4,r0,#0
    ldrb r0,[r4,#0x9]
    add r0,r0,r4
    ldrb r5,[r0,#0x18]      ; ability id of the selected slot
    cmp r5,#0xc
    bne hud_chain
    ldrb r0,[r4,#0x8]
    cmp r0,#ZPLUS_ENTRY
    beq hud_mine            ; in Z+
    add r0,r4,#0
    bl zplus_ok
    cmp r2,#0x0
    beq hud_chain           ; B does not step up to Z+
hud_mine:
    lsl r0,r5,#4
    ldr r1,=0x081d9900
    add r6,r0,r1
    ldr r1,[r6,#0x8]
    add r0,r4,#0
    bl stub_r1              ; r0 = ability test(record): bright or dim
    ldr r1,=ICON_OK
    cmp r0,#0x0
    bne hud_done
    ldr r1,=ICON_DIM
    b hud_done
hud_chain:
    add r0,r4,#0
    ldr r1,=SSJ2_HUD
    bl stub_r1              ; ssj2_form's HUD hook picks the Z2 icon or the vanilla one
    pop {r4,r5,r6,pc}
hud_done:
    add r0,r1,#0
    pop {r4,r5,r6,pc}
stub_r1:
    bx r1
"""


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def namers(rom: bytes, address: int, allowed: list) -> list:
    """Every 4-aligned ROM word that equals `address`. Raises when one sits outside `allowed` spans."""
    want = _word(address)
    hits = [off for off in range(0, len(rom) - 3, 4) if rom[off:off + 4] == want]
    stray = [off for off in hits if not any(start <= off < start + size for start, size in allowed)]
    if stray:
        raise ValueError(f"word 0x{address:08X} is named at " + ", ".join(f"rom:0x{o:X}" for o in stray)
                         + ", which no patch allocated and no known literal covers")
    return hits


def exit_record(rom: bytes) -> tuple:
    """(offset, bytes) of the LIVE chamber exit record, read through its scene table word.

    The record holds the `ext 73 (2, 138)` that moves Vegeta to entry 9, which is the whole Z+ unlock.
    fullpower_ssj relocates the record and repoints rom:0x3DE774, so the vanilla address rom:0x3DE620
    holds a dead copy. Reading the word instead of the address follows whatever the game runs.
    """
    at = _u32(rom, EXIT_TABLE_WORD) - ROM_BASE
    if not 0 <= at < len(rom):
        raise ValueError(f"rom:0x{EXIT_TABLE_WORD:X} does not name a record: 0x{_u32(rom, EXIT_TABLE_WORD):08X}")
    return at, bytes(rom[at:sl.record_end(rom, at)])


def _icon_px(x: int, y: int) -> int:
    """Byte offset of pixel (x, y) in a 32x16 8bpp 1D-order tile image."""
    return (y // 8) * 256 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)


def bf_look(art: bytes, live: bytes) -> bytes:
    """The Z+ picture of `art`, drawn in the LoG II layout, on the live icon bf_hud put in the BF look."""
    x0, y0, x1, y1 = PICTURE
    out = bytearray(live)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            out[_icon_px(x, y)] = art[_icon_px(x + SOURCE_DX, y)]
    return bytes(out)


def _portrait(rom: bytearray, block: int) -> bytes:
    """The owner's Z+ portrait pixels, checked the way art_inject checks a table portrait."""
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


# ===== animation row borrow (reusable: Trunks 133 from 132, Goku 61 from 60, Piccolo 104 from 103) =====

def set_at(rom: bytes, set_id: int) -> int:
    """File offset of a set header, through THIS ROM's own relocated set table."""
    off = rom_ptr(rom, _u32(rom, SET_TABLE_LITERAL) - ROM_BASE + 4 * (set_id - FIRST_SET))
    if off is None:
        raise ValueError(f"set {set_id}: the set table word is not a pointer")
    return off


def anim_row(rom: bytes, set_id: int, anim: int) -> tuple:
    """(file offset of the row, the SET_DIRS pointer words). A missing animation is a row of zeros."""
    head = read_set(rom, set_at(rom, set_id))
    if anim >= head["anims"]:
        raise ValueError(f"set {set_id} holds {head['anims']} animation rows, so row {anim} is past the table")
    at = head["table"] + 4 * anim * SET_DIRS
    return at, struct.unpack_from(f"<{SET_DIRS}I", rom, at)


def _geometry(rom: bytes, word: int) -> tuple:
    r = read_record(rom, word - ROM_BASE)
    return r["w"], r["h"], r["dx"], r["dy"]


def plan_anim_borrow(rom: bytes, into_set: int, from_set: int, anim: int = POWER_UP) -> dict:
    """Check a borrow and return it as {row, from, anim, ptrs}. Writes nothing, so apply can
    run it with the other checks, before the first write.

    Refuses unless the target row is empty, the source row is whole in every direction, the two sets
    share one OBJ slot, and the borrowed frames match the geometry the target already draws.
    """
    into_head, from_head = read_set(rom, set_at(rom, into_set)), read_set(rom, set_at(rom, from_set))
    at, old = anim_row(rom, into_set, anim)
    _, new = anim_row(rom, from_set, anim)
    if any(old):
        raise ValueError(f"set {into_set} animation {anim} is already {old[0]:#010x}: nothing to borrow")
    if not all(new):
        raise ValueError(f"set {from_set} animation {anim} is {new}, so it has nothing to lend")
    if into_head["slot"] != from_head["slot"]:
        raise ValueError(f"set {into_set} slot 0x{into_head['slot']:X} differs from set {from_set} "
                         f"slot 0x{from_head['slot']:X}: the OBJ buffer would not fit")
    want = {_geometry(rom, w) for _, w in zip(range(SET_DIRS), anim_row(rom, into_set, REVERT)[1])}
    got = {_geometry(rom, w) for w in new}
    if want != got:
        raise ValueError(f"set {from_set} animation {anim} records are {sorted(got)}, but set {into_set} "
                         f"draws {sorted(want)}: the borrowed frames would not line up")
    return {"row": at, "from": from_set, "anim": anim, "ptrs": list(new)}


def borrow_anim_row(rom: bytearray, into_set: int, from_set: int, anim: int = POWER_UP) -> dict:
    """Give `into_set` the animation row of `from_set`, which it does not have of its own.

    The record lookup @0x0800775A indexes the row by animation number with no existence test, so a
    null row makes the state machine follow a null record list (bible B0041). Every vanilla SUPER
    set except Gohan's 59 has a null anim 9, which is why only Gohan's line can step Super Saiyan
    to Super Saiyan. Reusable as it stands: Trunks 133 from 132, Goku 61 from 60, Piccolo 104
    from 103.
    """
    plan = plan_anim_borrow(rom, into_set, from_set, anim)
    rom[plan["row"]:plan["row"] + 4 * SET_DIRS] = b"".join(_word(w) for w in plan["ptrs"])
    return plan


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    need = ("ssj2_form", "npc_gi", "art_inject", "bf_hud")
    if any(k not in alloc.notes for k in need):
        raise ValueError(f"vegeta_zplus needs the {', '.join(need)} notes: run them first")
    if "vegeta_zplus" in alloc.notes:
        raise ValueError("vegeta_zplus already ran")
    ssj2 = alloc.notes["ssj2_form"]

    # checks, before any write
    old_table = _u32(rom, TABLE_LITERAL) - ROM_BASE
    if old_table != ssj2["table"]:
        raise ValueError(f"rom:0x{TABLE_LITERAL:X} names table rom:0x{old_table:X}, "
                         f"not ssj2_form's rom:0x{ssj2['table']:X}")
    _expect(rom, old_table + ENTRY * PRE_BASE, PRE_BASE_HEAD)
    _expect(rom, old_table + ENTRY * POST_BASE, POST_BASE_HEAD)
    _expect(rom, old_table + ENTRY * ZPLUS, ZPLUS_HEAD)
    _expect(rom, old_table + ENTRY * ZPLUS + 0x10, _word(ASCENDED_OBJ))
    _expect(rom, old_table + ENTRY * PRE_Z, PRE_Z_HEAD)
    _expect(rom, old_table + ENTRY * PRE_Z + 0x10, _word(ORDINARY_OBJ))
    at, body = exit_record(rom)              # the unlock is the vanilla ops in this record, so check it lives
    for want in EXIT_OPS:
        if body.count(want) != 1:
            raise ValueError(f"the live chamber exit record rom:0x{at:X} holds {body.count(want)} copies of "
                             f"{want.hex()}, expected 1: that op IS the Z+ unlock")
    for set_id in BASE_CHAIN_SETS:           # a chain set with a null anim 9 crashes the power-up (B0041).
        row, ptrs = anim_row(rom, set_id, POWER_UP)   # The two super sets are checked by plan_anim_borrow.
        if not all(ptrs):
            raise ValueError(f"set {set_id} animation {POWER_UP} at rom:0x{row:X} is {ptrs}: the transform "
                             f"out of it would follow a null record list")
    _expect(rom, ABILITY_12_ACTION, _word(ssj2["gate"] + ROM_BASE + 1))
    _expect(rom, HUD_LITERAL, _word(ssj2["hud"] + ROM_BASE + 1))
    old_block = _u32(rom, BLOCK_LITERAL) - ROM_BASE
    if old_block != alloc.notes["npc_gi"]["block"]:
        raise ValueError(f"rom:0x{BLOCK_LITERAL:X} names block rom:0x{old_block:X}, "
                         f"not npc_gi's rom:0x{alloc.notes['npc_gi']['block']:X}")
    if alloc.notes["npc_gi"]["pre_id"] != BLOCK_IDS - 1:
        raise ValueError(f"the block holds ids 0-{alloc.notes['npc_gi']['pre_id']}, expected 0-{BLOCK_IDS - 1}")
    px = _portrait(rom, old_block)
    for step_set in BORROWERS:
        plan_anim_borrow(rom, step_set, VEG_BASE_SET, POWER_UP)
    frame = slot(ZPLUS_PORTRAIT)
    if set(rom[frame:frame + FRAME]) != {0xFF}:
        raise ValueError(f"portrait {ZPLUS_PORTRAIT}: art slot rom:0x{frame:X} is not free")
    art = [(ART / name).read_bytes() for name in ICONS]
    if any(len(i) != ICON_LEN for i in art):
        raise ValueError(f"each Z+ icon must be 0x{ICON_LEN:X} bytes")
    live = [_u32(rom, ABILITY_TABLE - ROM_BASE + 16 * ABILITY_12 + k) - ROM_BASE for k in (0, 4)]
    icons = [bf_look(a, rom[off:off + ICON_LEN]) for a, off in zip(art, live)]
    if any(a == i for a, i in zip(art, icons)):
        raise ValueError("the Z+ icons did not change in the BF look: is bf_hud's icon layout still (3, 2, 18, 9)?")
    spans = alloc.used() + [(off, 4) for off in TABLE_LITERALS]
    table_namers = namers(rom, old_table + ROM_BASE, spans)
    missing = [off for off in TABLE_LITERALS if off not in table_namers]
    if missing:
        raise ValueError("the table literals " + ", ".join(f"rom:0x{o:X}" for o in missing)
                         + " no longer name the live appearance table")
    block_namers = namers(rom, old_block + ROM_BASE, alloc.used() + [(BLOCK_LITERAL, 4)])

    # 1. allocate everything; nothing is written until the code size is checked
    table = alloc.alloc(ENTRY * (ENTRIES + 1))
    block = alloc.alloc(4 + 4 * (BLOCK_IDS + 1))
    usable, dim = alloc.alloc(ICON_LEN), alloc.alloc(ICON_LEN)
    entry = bytearray(rom[old_table + ENTRY * PRE_Z:old_table + ENTRY * (PRE_Z + 1)])
    entry[4], entry[5] = ZPLUS, POST_BASE   # the post-chamber Z: B steps up to Z+, and it reverts to entry 9
    syms = {"POST_Z": POST_Z, "ZPLUS_ENTRY": ZPLUS, "STEP_EP": STEP_EP, "VANILLA_ACTION": VANILLA_ACTION,
            "ICON_OK": usable + ROM_BASE, "ICON_DIM": dim + ROM_BASE,
            "SSJ2_GATE": _u32(rom, ABILITY_12_ACTION), "SSJ2_HUD": _u32(rom, HUD_LITERAL)}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                    # a size change would shift every later ROM byte
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")

    # 2. appearance table: the new post-chamber Z, entry 9 stepping into it, and entry 10 turned into Z+.
    #    Entry 11 is deliberately untouched. Its +4 stays 8, and that is the whole pre-chamber gate.
    rom[table:table + ENTRY * ENTRIES] = rom[old_table:old_table + ENTRY * ENTRIES]
    rom[table + ENTRY * ENTRIES:table + ENTRY * (ENTRIES + 1)] = entry
    rom[table + ENTRY * POST_BASE + 4] = POST_Z
    rom[table + ENTRY * ZPLUS + 2] = ZPLUS_PORTRAIT
    for off in table_namers:
        rom[off:off + 4] = _word(table + ROM_BASE)

    # 3. dialog portrait block with the new id 122
    rom[block:block + 4 + 4 * BLOCK_IDS] = rom[old_block:old_block + 4 + 4 * BLOCK_IDS]
    rom[frame:frame + FRAME] = RAW_HEADER + px
    rom[block + 4 + 4 * ZPLUS_PORTRAIT:block + 8 + 4 * ZPLUS_PORTRAIT] = _word(frame + ROM_BASE)
    for off in block_namers:
        rom[off:off + 4] = _word(block + ROM_BASE)

    # 4. the power-up animation: on the set the step comes FROM, and on Z+ itself
    borrowed = [borrow_anim_row(rom, s, VEG_BASE_SET, POWER_UP) for s in BORROWERS]

    # 5. code, icons and the two hooks
    rom[code:code + size] = blob
    rom[usable:usable + ICON_LEN], rom[dim:dim + ICON_LEN] = icons
    rom[ABILITY_12_ACTION:ABILITY_12_ACTION + 4] = _word(labels["gate"] | 1)
    rom[HUD_LITERAL:HUD_LITERAL + 4] = _word(labels["hud"] | 1)

    alloc.notes["vegeta_zplus"] = {"table": table, "block": block, "frame": frame, "zplus": usable,
                                   "anim_rows": borrowed,
                                   "zplus_dim": dim, "code": code,
                                   "zplus_entry": ZPLUS, "post_z_entry": POST_Z,
                                   "table_namers": table_namers, "block_namers": block_namers,
                                   **{k: v - ROM_BASE for k, v in labels.items()
                                      if not k.startswith(("zp_", "gate_", "hud_"))}}
