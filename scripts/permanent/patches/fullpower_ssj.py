r"""
fullpower_ssj.py - Patch: Goku and Gohan stay Super Saiyan from the Time Chamber until Cell is beaten.

Usage:   py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r28.gba
Input:   the ROM after scene_drain_pause (notes: ssj2_form table, npc_gi and cellgames_ssj record copies,
         scene_drain_pause tick). Run it last (build list end), so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["fullpower_ssj"].
Method:  The stretch is flag 149 set (Goku walks into the chamber, Vegeta and Trunks exit seq 33) and flag 195
         clear (Cell beaten). In it, for Goku (entry 20) and Gohan (entry 5) only:
         1. Tick: the Super Saiyan vtable 0x08024C58 +4 calls a check that returns at once when Goku or Gohan
            leads (no drain, no revert at 0 EP); everyone else runs the r27 scene-pause tick.
         2. B and Z: the ability 12 test (rom:0x1D99C8) returns 0 for entries 5 and 20, so the HUD shows the dim
            Z and B plays the refusal sound instead of the revert. Base entries keep the vanilla test.
         3. appearance_revert (0x08003ED4, now `ldr r3 ; bx r3` to a re-encoding): ext 70, ext 71, Switch
            Characters and Continue keep entries 5 and 20. Called from Continue (lr 0x0800185D), it also puts
            Goku 19 to 20 and Gohan 2 to 5 (Gohan only with Super Saiyan unlocked, record +0x14 bit 5).
         4. Knockout: state 0x21 enter (vtable 0x080254D8 +0) runs vanilla (form leave, revert, animation),
            then gives a Goku or Gohan leader back his Super Saiyan entry.
         5. Scripts: Goku's record to 20 at the chamber door (ext 73 (4, 61) after SET 149); NPC Goku 60 to 61
            and his raw portrait 63 to 65 in the chamber exit and Dende's ball talk; Gohan's chamber exit
            ext 73 (0, 157) to (0, 158); Goku's record back to 19 when Cell is beaten (ext 73 (4, 60) after
            Gohan's post-Cell ext 73 (0, 157)); r27's Goku power-up in the arena entry scene removed (Goku
            arrives in Super Saiyan, and set 61 has no anim 9).
Rules:   Source: docs\tasks\2026-10-22-r28-build\fullpower-ssj.md (final decisions), scripts\one-time\2026-10-22-r28-build\ (sweeps). Grown records
         are copied (npc_gi.relocate) and their one table word repointed; old ones stay unreferenced. Every
         byte, slot, record hash and table word is checked before any write; a second run raises. r27's
         Gohan inserts and EP refill stay (a state saved in base still leads in Super Saiyan; EP is visible).
"""
import hashlib
import struct

from scene.scene_lib import relocate
from patches.ssj2_form import assemble

# ===== constants =====
ROM_BASE = 0x08000000
STRUCT = 0x03000E90
FLAG_149, FLAG_195 = (STRUCT + 0xB4 + 149 // 8, 149 & 7), (STRUCT + 0xB4 + 195 // 8, 195 & 7)
GOHAN, GOKU = 0, 4
GOHAN_BASE, GOHAN_SSJ, GOKU_BASE, GOKU_SSJ = 2, 5, 19, 20
SSJ_VTABLE, DEATH_VTABLE = 0x08024C58, 0x080254D8          # Super Saiyan form; player state 0x21 (knockout)
ABILITY_12_TEST, VANILLA_TEST = 0x1D99C8, 0x080134F3
VANILLA_DEATH = 0x0800833F
REVERT_SITE, REVERT_OLD = 0x3ED4, bytes.fromhex("30b49d4c00210278")
REVERT_TABLE_LITERAL = 0x414C                               # vanilla revert's table literal (ssj2_form repoints it)
CONTINUE_RET = 0x0800185D                                   # lr of `bl appearance_revert` in Continue @0x08001858

# rom offset: (old byte, new byte)
NPC_GOKU = {0x3DB5C3: (0x78, 0x7A), 0x3DB5CC: (0x78, 0x7A), 0x3DBBED: (0x3C, 0x3D),   # chamber exit 3, 3, 27
            0x3DD238: (0x78, 0x7A), 0x3DD241: (0x78, 0x7A), 0x3DD320: (0x78, 0x7A),   # Dende seq 4, 4, 7
            0x3DD328: (0x3C, 0x3D)}                                                    # Dende seq 7 remove
GOKU_PORTRAITS = {r + 3: (63, 65) for r in (0x3DB6AC, 0x3DB720, 0x3DB780, 0x3DD27C)}
GOHAN_EXIT = {0x3DB62A: (157, 158)}                         # chamber exit seq 3: push 0 ; push 157 ; ext 73

GOKU_TRANSFORM = "0037022e1d0200120239000a022a0037022f0004003d0249000a022b"    # r27 cellgames_ssj insert
# name: (record or the notes key, length or None for the notes size, table word, SHA-1, offset, old, new)
RECORDS = {
    "door_seq33": (0x3DE620, 0xB2, 0x3DE774, "e894d9b3cca20bc754af321858f5c2c4cdb20d07",
                   0x7C, "0095021b", "0095021b" "0004003d0249"),          # SET 149, then ext 73 (4, 61)
    "entry_seq1": ("cellgames_ssj", None, 0x3E8D98, "3d7448a18e0238bdda65300baeddaa0c90e6a018",
                   0xCF, GOKU_TRANSFORM + "0032", "0032"),                  # r27 power-up out
    "post_cell_seq20": ("npc_gi", 0x261, 0x3EC7A4, "e3aedfa6c75e17a72995a79bbdbd228235409421",
                        0x1DC, "0000009d0249", "0000009d0249" "0004003c0249"),  # then ext 73 (4, 60)
}
POST_CELL_SEQ20 = 0x3EBE1C                                  # npc_gi key of the post-Cell seq 20 copy

# ===== new code (ARMv4T Thumb) =====
CODE = """
stretch_on:                 ; leaf: r2 = 1 when flag 149 is set and flag 195 clear. Uses r2, r3 only
    ldr r3,=FLAG_149_BYTE
    ldrb r2,[r3,#0x0]
    lsl r2,r2,#SHIFT_149
    bpl stretch_no
    ldrb r2,[r3,#DELTA_195]
    lsl r2,r2,#SHIFT_195
    bmi stretch_no
    mov r2,#0x1
    bx lr
stretch_no:
    mov r2,#0x0
    bx lr
tick:                       ; Super Saiyan tick; r1 = player. Goku or Gohan leading in the stretch: no drain
    push {lr}
    bl stretch_on
    pop {r3}
    mov lr,r3
    cmp r2,#0x0
    beq tick_old
    ldr r3,=STRUCT
    ldrb r3,[r3,#0x0]
    cmp r3,#GOHAN
    beq tick_skip
    cmp r3,#GOKU
    bne tick_old
tick_skip:
    bx lr
tick_old:
    ldr r2,=OLD_TICK
    bx r2                   ; tail call with r0, r1 and lr as the form tick call passed them
test:                       ; ability 12 test(r0 = record): 0 for entries 5 and 20 in the stretch
    push {lr}
    bl stretch_on
    pop {r3}
    mov lr,r3
    cmp r2,#0x0
    beq test_old
    ldrb r2,[r0,#0x8]
    cmp r2,#GOHAN_SSJ
    beq test_no
    cmp r2,#GOKU_SSJ
    bne test_old
test_no:
    mov r0,#0x0
    bx lr
test_old:
    ldr r2,=OLD_TEST
    bx r2
revert:                     ; appearance_revert(r0 = save struct), vanilla loop plus the stretch rules
    push {r4,r5,r6,r7,lr}
    mov r7,lr
    bl stretch_on
    add r6,r2,#0
    ldr r4,=TABLE
    mov r1,#0x0
revert_loop:
    ldrb r2,[r0,#0x0]
    cmp r2,r1
    beq revert_next         ; the leader keeps his entry
    lsl r2,r1,#3
    sub r2,r2,r1
    lsl r2,r2,#2
    add r2,r2,r0            ; r2 = struct + 28 n; the entry is at +0x14
    ldrb r5,[r2,#0x14]
    cmp r6,#0x0
    beq revert_one
    cmp r5,#GOHAN_SSJ
    beq revert_next
    cmp r5,#GOKU_SSJ
    beq revert_next
revert_one:
    lsl r3,r5,#2
    add r3,r3,r5
    lsl r3,r3,#2
    add r3,r3,r4
    ldrb r5,[r3,#0x0]
    lsl r5,r5,#31
    beq revert_next         ; not a transformed entry
    ldrb r3,[r3,#0x5]
    strb r3,[r2,#0x14]
revert_next:
    add r1,#0x1
    cmp r1,#0x6
    blt revert_loop
    cmp r6,#0x0
    beq revert_done
    ldr r3,=CONTINUE_RET
    cmp r7,r3
    bne revert_done         ; only a Continue load restores Super Saiyan
    add r2,r0,#0
    add r2,#GOKU_ENTRY
    ldrb r3,[r2,#0x0]
    cmp r3,#GOKU_BASE
    bne revert_gohan
    mov r3,#GOKU_SSJ
    strb r3,[r2,#0x0]
revert_gohan:
    ldrb r3,[r0,#GOHAN_ENTRY]
    cmp r3,#GOHAN_BASE
    bne revert_done
    add r2,r0,#0
    add r2,#GOHAN_BITS
    ldrb r3,[r2,#0x0]
    lsl r3,r3,#26           ; bit 5: Super Saiyan unlocked (ext 82)
    bpl revert_done
    mov r3,#GOHAN_SSJ
    strb r3,[r0,#GOHAN_ENTRY]
revert_done:
    pop {r4,r5,r6,r7,pc}
death:                      ; state 0x21 enter; r0 = state, r1 = player. Vanilla, then the stretch entry back
    push {r4,r5,lr}
    ldr r4,=STRUCT
    ldrb r5,[r4,#0x0]
    lsl r3,r5,#3
    sub r3,r3,r5
    lsl r3,r3,#2
    add r4,r4,r3            ; r4 = struct + 28 x leader; the entry is at +0x14
    ldrb r5,[r4,#0x14]
    ldr r2,=OLD_DEATH
    bl stub_r2
    bl stretch_on
    cmp r2,#0x0
    beq death_done
    cmp r5,#GOHAN_SSJ
    beq death_keep
    cmp r5,#GOKU_SSJ
    bne death_done
death_keep:
    strb r5,[r4,#0x14]
death_done:
    pop {r4,r5,pc}
stub_r2:
    bx r2
"""
SITE_CODE = """
    ldr r3,=REVERT
    bx r3
"""


# ===== checks =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _slot_word(vtable: int, target: int) -> bytes:
    """Base-relative vtable word: target address minus the vtable address."""
    return struct.pack("<i", target - vtable)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def byte_sites() -> dict:
    return {**NPC_GOKU, **GOKU_PORTRAITS, **GOHAN_EXIT}


def _record_source(notes: dict, name: str) -> tuple:
    rec, length = RECORDS[name][:2]
    if rec == "cellgames_ssj":
        return notes[rec]["records"][name], notes[rec]["sizes"][name]
    if rec == "npc_gi":
        return notes[rec]["records"][POST_CELL_SEQ20], length
    return rec, length


def _symbols(notes: dict) -> dict:
    return {"FLAG_149_BYTE": FLAG_149[0], "SHIFT_149": 31 - FLAG_149[1], "DELTA_195": FLAG_195[0] - FLAG_149[0],
            "SHIFT_195": 31 - FLAG_195[1], "STRUCT": STRUCT, "GOHAN": GOHAN, "GOKU": GOKU,
            "GOHAN_SSJ": GOHAN_SSJ, "GOKU_SSJ": GOKU_SSJ, "GOHAN_BASE": GOHAN_BASE, "GOKU_BASE": GOKU_BASE,
            "GOHAN_ENTRY": 0xC + 28 * GOHAN + 8, "GOKU_ENTRY": 0xC + 28 * GOKU + 8, "GOHAN_BITS": 0xC + 0x14,
            "OLD_TICK": (notes["scene_drain_pause"]["tick_ssj"] + ROM_BASE) | 1, "OLD_TEST": VANILLA_TEST,
            "OLD_DEATH": VANILLA_DEATH, "TABLE": notes["ssj2_form"]["table"] + ROM_BASE,
            "CONTINUE_RET": CONTINUE_RET}


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    need = ("ssj2_form", "npc_gi", "cellgames_ssj", "scene_drain_pause")
    if any(k not in alloc.notes for k in need):
        raise ValueError(f"fullpower_ssj needs the {', '.join(need)} notes: run them first")
    if "fullpower_ssj" in alloc.notes:
        raise ValueError("fullpower_ssj already ran")
    syms = _symbols(alloc.notes)

    # checks, before any write
    _expect(rom, REVERT_SITE, REVERT_OLD)
    _expect(rom, REVERT_TABLE_LITERAL, _word(syms["TABLE"]))
    _expect(rom, SSJ_VTABLE - ROM_BASE + 4, _slot_word(SSJ_VTABLE, syms["OLD_TICK"]))
    _expect(rom, DEATH_VTABLE - ROM_BASE, _slot_word(DEATH_VTABLE, VANILLA_DEATH))
    _expect(rom, ABILITY_12_TEST, _word(VANILLA_TEST))
    for off, (old, _) in byte_sites().items():
        _expect(rom, off, bytes([old]))
    copies = {}
    for name, (_, _, word, sha, at, old, new) in RECORDS.items():
        rec, length = _record_source(alloc.notes, name)
        _expect(rom, word, _word(rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} ({name}) differs from the r27 bytes")
        copies[name] = relocate(rom, rec, length, {rec + at: (old, new)})

    # allocate and assemble; nothing is written until every size is checked
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:                         # pool padding depends on the address
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    site, _ = assemble(SITE_CODE, REVERT_SITE + ROM_BASE, {"REVERT": labels["revert"] | 1})
    if len(site) != len(REVERT_OLD):
        raise ValueError(f"revert site assembled to {len(site)} bytes, expected {len(REVERT_OLD)}")

    # writes
    rom[code:code + size] = blob
    rom[REVERT_SITE:REVERT_SITE + len(site)] = site
    rom[SSJ_VTABLE - ROM_BASE + 4:SSJ_VTABLE - ROM_BASE + 8] = _slot_word(SSJ_VTABLE, labels["tick"] | 1)
    rom[DEATH_VTABLE - ROM_BASE:DEATH_VTABLE - ROM_BASE + 4] = _slot_word(DEATH_VTABLE, labels["death"] | 1)
    rom[ABILITY_12_TEST:ABILITY_12_TEST + 4] = _word(labels["test"] | 1)
    for off, (_, new) in byte_sites().items():
        rom[off] = new
    moved = {}
    for name, data in copies.items():
        at = alloc.alloc(len(data))
        rom[at:at + len(data)] = data
        word = RECORDS[name][2]
        rom[word:word + 4] = _word(at + ROM_BASE)
        moved[name] = at

    alloc.notes["fullpower_ssj"] = {
        "code": code, "size": size, **{k: v - ROM_BASE for k, v in labels.items() if "_" not in k},
        "stretch_on": labels["stretch_on"] - ROM_BASE, "records": moved,
        "sizes": {k: len(v) for k, v in copies.items()},
        "sources": {k: _record_source(alloc.notes, k)[0] for k in RECORDS}}
