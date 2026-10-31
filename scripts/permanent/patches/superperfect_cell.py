r"""
superperfect_cell.py - Patch: Cell returns from the self-destruct as Super Perfect Cell, with SSJ2 bolts (r30-r35).

Usage:   py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r35.gba
Input:   the ROM after piccolo_gi_scene (r29 list); art art\cell_aura\scale_15\ (final call 2026-10-23:
         1.5x, 1 px bolts; made by scripts\one-time\2026-10-22-superperfect-study\cell_aura.py).
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["superperfect_cell"].
Method:  1. Set 58 (dead in r29: no script, map, appearance or scouter reader) is built from the art with set 30's
            header, boxes and anim table (build_set, anim 0 = 6 records per dir), and its live set table word
            points at it. Set 30 stays as it is, so Cell before the self-destruct does not change.
         2. Cell's return: 68 actor pushes of 30 in table rom:0x3EB704 seq 40-65 and table rom:0x3EC758 (the
            type 25 death event, seq 20 is fullpower_ssj's copy) become 58, in place (op 0 `1E` to `3A`, op 29
            list `3C` to `74`, both one byte). The type 25 spawn (rom:0x409108) and the map 14,4 NPC
            (rom:0x409204) set words become 58. Params that equal 30 (waits, ext 121 and 134 args) stay.
         3. Idle flicker: a chained tick on the +4 words of vtables 0x08025A84 (state 0) and 0x08024BA0
            (state 38). Set 58 jumps into ssj2_idle's own step (idle_ours: anim 0 row test, shape every 8
            ticks, body 1 blink); every other set jumps to the ssj2_idle hook, so sets 159 and 160 tick as before.
         4. Portrait: the 10 Super Perfect Cell lines (record +3) go from 40 to 52. While block word 52 still
            names its vanilla frame (an unused hooded face), it is pointed at id 40's frame, so the lines look
            as today. Once I inject id 52 (art_inject, earlier in the list), word 52 is left alone.
         5. Scouter (r31): entry 19 +8 (set) 30 -> 58 and +0xC (portrait) 40 -> 52. scouter_match @0x08019102
            returns the first entry whose set header matches, so set 30 still gets entry 13 and set 58 gets 19,
            whose +0x10 enemy type 25 is this fight's (from r38: HP 9876, STR 72, POW 71, END 78, step 8).
            An enemy actor scans by its enemy type instead (@0x080190D4), which also gives entry 19.
         6. Name (r33, r34): entry 19 +0 names a new string 'Cell, "S. Perfect"' (entry 13's format) placed after
            the hook code. 13-18 keep the shared 'Cell, "Perfect"' string. The database groups rows by name
            pointer (@0x08019204), so entry 19 becomes its own row.
         7. Text (r35): entry 19 +4 names a new string, my text in entry 13's format (ASCII, two spaces
            between sentences, no break bytes: text_wrapped @0x0801F702 wraps at 160 px and the page scrolls).
            It is placed after the name. 13-18 keep the shared Perfect text.
         8. Stats (r38, +20% over vanilla; r35 was +10%): enemy type 25 (only spawn rom:0x4090F8) HP 8230 -> 9876,
            STR 60 -> 72, POW 59 -> 71, END 65 -> 78. The scouter reads them from entry 19 +0x10, so it shows them as is.
Rules:   Source: docs\tasks\2026-10-23-r30-build\r30.md, r31.md, r33.md, r35.md, superperfect-study-report.md (sites, design 6),
         superperfect-aura-report.md (art). Site bytes from scripts\one-time\2026-10-23-r30-build\cell_sites.py (r29). Every site is
         checked before the first write; a second run raises.
"""
import struct

from rom.log2_sprites import build_set
from patches.art_inject import slot
from patches.gohan_gi import art_records
from patches.ssj2_form import assemble
from patches.ssj2_idle import ANIM0_ROW, CODE as SSJ2_IDLE_CODE, VANILLA_TICK, VTABLES

# ===== constants =====
ROM_BASE = 0x08000000
SET_LITERAL, BLOCK_LITERAL = 0x959C, 0xBE10
CELL, SUPER = 30, 58                                   # set ids
CELL_HEADER, DEAD_58 = 0x242DBC, 0x2AB508              # set 30 header; vanilla set 58 (armor Rage, no reader)
ART_FOLDER, IDLE_RECORDS = "cell_aura/scale_15", 6
RETURN_TABLE, DEATH_TABLE = 0x3EB704, 0x3EC758
SEQ20 = "post_cell_seq20"                              # fullpower_ssj notes key of rom:0x3EC758 seq 20

# (table, seq): (record in r29, value byte offsets from the record start)
ACTOR_SITES = {
    (RETURN_TABLE, 40): (0x3EACD0, (0x5, 0x10, 0x93, 0x98)),
    (RETURN_TABLE, 50): (0x3EB134, (0x16, 0x20, 0x26, 0x2B, 0x30, 0x39, 0x42, 0x4B)),
    (RETURN_TABLE, 52): (0x3EB21C, (0x1E, 0x36)),
    (RETURN_TABLE, 65): (0x3EB6E8, (0xB,)),
    (DEATH_TABLE, 1): (0x3EB80C, (0x31, 0x60)),                  # +0x60: push 30,30 ; ext 121, Cell is the first
    (DEATH_TABLE, 7): (0x3EBA4C, (0x7,)),
    (DEATH_TABLE, 11): (0x3EBC7E, (0x7,)),
    (DEATH_TABLE, 17): (0x3EBD7C, (0x37, 0x3D, 0x65)),
    (DEATH_TABLE, 20): (0x89AB4C, (0x29, 0x32, 0x38, 0x5D, 0x61, 0x66, 0x70, 0x76, 0x8D, 0x92, 0x97, 0x9F, 0xA5,
                                   0xAE, 0xB4, 0xCC, 0xD1, 0xD6, 0xDC, 0xE4, 0xEA, 0xF2, 0xF8, 0x111, 0x116, 0x11B,
                                   0x121, 0x12B, 0x131, 0x138, 0x13E, 0x155, 0x15A, 0x160, 0x166, 0x16F, 0x175,
                                   0x18C, 0x191, 0x197, 0x19D, 0x1A4, 0x1AB, 0x1B5, 0x1BD, 0x1C5)),
}
NEW_BYTE = {0x1E: 0x3A, 0x3C: 0x74}                    # op 0 byte 30 -> 58; op 29 zigzag 60 -> 116
SET_WORDS = (0x409108, 0x409204)                       # spawn rom:0x4090F8 +0x10 (type 25), 14,4 NPC rom:0x4091F8 +0xC

PORTRAIT_OLD, PORTRAIT_NEW = 40, 52
PORTRAIT_SEQS = {RETURN_TABLE: (41, 44, 51, 53, 55), DEATH_TABLE: (4, 6, 10, 16, 18)}
VANILLA_52 = 0x6BAF30                                  # vanilla frame of id 52 (a hooded face no record shows)

SCOUTER, SCOUTER_SIZE = 0x6F8E40, 20                   # entry: name, text, set, portrait, enemy type (u32 each)
PERFECT, SUPER_ENTRY = range(13, 19), 19               # 13-18 name set 30; enemies match 14-19 by type
SCOUTER_19 = bytes.fromhex("59a86f08" "69a86f08" "1e000000" "28000000" "19000000")   # vanilla entry 19
PERFECT_NAME = (0x6FA859, b'Cell, "Perfect"\0')       # the shared name of 13-19, kept for 13-18
SUPER_NAME = b'Cell, "S. Perfect"\0'                   # r34 final call: 85 px, fits the info field
OWNER_TEXT = ("After self-destructing, Cell regenerated from a single surviving cell. Analysis of his Namek cells "
              "reveals the ability to rebuild an entire body. The Saiyan cells in his structure reacted to the "
              "near-death experience and greatly increased his power. Electrical discharges now surround his body. "
              "The effect on his power level is so drastic that it cannot be calculated.")   # r35, verbatim
SUPER_TEXT = OWNER_TEXT.replace(". ", ".  ").encode("ascii") + b"\0"   # the game's sentence gap (entry 13)

TYPE25 = 0x6D5904                                      # enemy type 25: +4 u32 HP, +0xC STR, +0xD POW, +0xE END
STATS = {4: ((8230).to_bytes(4, "little"), (9876).to_bytes(4, "little")), 0xC: (bytes([60, 59, 65]),
                                                                                bytes([72, 71, 78]))}

CODE = """
spc_idle:                   ; r0 = state, r1 = obj. Set 58: ssj2_idle's own step; else the ssj2_idle hook
    ldr r2,[r1,#0x48]
    ldr r3,=SET_SUPER
    cmp r2,r3
    bne spc_old
    ldr r3,=OURS
    bx r3                   ; idle_ours expects r2 = set: anim 0 row test, shape and blink
spc_old:
    ldr r3,=OLD
    bx r3                   ; tail call: r0, r1, lr and sp as at entry
"""


# ===== helpers =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _record(rom: bytearray, table: int, seq: int) -> int:
    return _u32(rom, table + 4 * (seq - 1)) - ROM_BASE


def _old_hook(rom: bytearray, alloc) -> dict:
    """ssj2_idle's labels, after its bytes are proved equal to a re-assembly at its notes address."""
    gi, n = alloc.notes["gohan_gi"], alloc.notes["ssj2_idle"]
    syms = {"SET_SSJ2": gi["set_159"] + ROM_BASE, "SET_RAGE": gi["set_160"] + ROM_BASE, "VANILLA": VANILLA_TICK,
            "ANIM0_ROW": ANIM0_ROW}
    blob, labels = assemble(SSJ2_IDLE_CODE, n["code"] + ROM_BASE, syms)
    _expect(rom, n["code"], blob)
    for vt in VTABLES:
        _expect(rom, vt + 4 - ROM_BASE, _word((labels["idle"] | 1) - vt))
    return labels


# ===== checks =====

def _sites(rom: bytearray, alloc) -> list:
    """File offsets of the 68 actor bytes, each checked to hold Cell's 30."""
    out = []
    for (table, seq), (rec, offs) in ACTOR_SITES.items():
        if _record(rom, table, seq) != rec:
            raise ValueError(f"table rom:0x{table:X} seq {seq} names 0x{_record(rom, table, seq):X}, not 0x{rec:X}")
        if rom[rec + 1:rec + 3] != b"\0\0" or rom[rec] != seq:
            raise ValueError(f"rom:0x{rec:X} is not the type 0 record of seq {seq}")
        for o in offs:
            if rom[rec + o] not in NEW_BYTE or (rom[rec + o] == 0x1E and rom[rec + o - 1] != 0):
                raise ValueError(f"rom:0x{rec + o:X} = {rom[rec + o]:02X} is not a push of Cell's 30")
            out.append(rec + o)
    if alloc.notes["fullpower_ssj"]["records"][SEQ20] != ACTOR_SITES[(DEATH_TABLE, 20)][0]:
        raise ValueError("fullpower_ssj moved seq 20 elsewhere")
    return out


def _portrait_records(rom: bytearray) -> list:
    out = []
    for table, seqs in PORTRAIT_SEQS.items():
        for seq in seqs:
            rec = _record(rom, table, seq)
            if rom[rec + 2] not in (1, 2) or rom[rec + 3] != PORTRAIT_OLD:
                raise ValueError(f"rom:0x{rec:X} (seq {seq}) is not a portrait {PORTRAIT_OLD} line")
            out.append(rec)
    return out


def _scouter_entry(rom: bytearray) -> int:
    """File offset of entry 19, after checking it is vanilla, 13-18 still name set 30 and no entry names 58."""
    entry = SCOUTER + SCOUTER_SIZE * SUPER_ENTRY
    _expect(rom, entry, SCOUTER_19)
    _expect(rom, PERFECT_NAME[0], PERFECT_NAME[1])
    for e in PERFECT:
        _expect(rom, SCOUTER + SCOUTER_SIZE * e + 8, _word(CELL))
    if any(_u32(rom, SCOUTER + SCOUTER_SIZE * e + 8) == SUPER for e in range(128)):
        raise ValueError(f"a scouter entry already names set {SUPER}")
    return entry


def _check(rom: bytearray, alloc) -> tuple:
    for need in ("ssj2_idle", "gohan_gi", "npc_gi", "fullpower_ssj", "piccolo_gi_scene"):
        if need not in alloc.notes:
            raise ValueError(f"superperfect_cell needs the {need} notes: run the r29 list first")
    if "superperfect_cell" in alloc.notes:
        raise ValueError("superperfect_cell already ran")
    set_table = _u32(rom, SET_LITERAL) - ROM_BASE
    _expect(rom, set_table + 4 * (CELL - 7), _word(CELL_HEADER + ROM_BASE))
    _expect(rom, set_table + 4 * (SUPER - 7), _word(DEAD_58 + ROM_BASE))
    for w in SET_WORDS:
        _expect(rom, w, _word(CELL))
    for at, (old, _) in STATS.items():
        _expect(rom, TYPE25 + at, old)
    block = _u32(rom, BLOCK_LITERAL) - ROM_BASE
    if block != alloc.notes["npc_gi"]["block"]:
        raise ValueError(f"rom:0x{BLOCK_LITERAL:X} names block 0x{block:X}, not npc_gi's")
    return (set_table, block, _sites(rom, alloc), _portrait_records(rom), _old_hook(rom, alloc),
            _word_52(rom, block), _scouter_entry(rom))


def _word_52(rom: bytearray, block: int) -> str:
    """'vanilla' (the hooded face: alias it to 40) or 'me' (art_inject's slot: leave it)."""
    word52 = _u32(rom, block + 4 + 4 * PORTRAIT_NEW)
    if word52 == slot(PORTRAIT_NEW) + ROM_BASE:
        return "owner"
    if word52 != VANILLA_52 + ROM_BASE:
        raise ValueError(f"block word {PORTRAIT_NEW} is 0x{word52:08X}: neither vanilla nor art_inject's slot")
    return "vanilla"


# ===== patch =====


def apply(rom: bytearray, alloc) -> None:
    set_table, block, sites, portraits, old, word_52, scouter = _check(rom, alloc)
    records, frames = art_records(ART_FOLDER)
    if sum(1 for a, d, _ in records if (a, d) == (0, 0)) != IDLE_RECORDS:
        raise ValueError(f"{ART_FOLDER}: anim 0 needs {IDLE_RECORDS} records per dir (the hook's body x 3 + shape)")

    head = build_set(rom, CELL_HEADER, records, frames, alloc, counts={0: IDLE_RECORDS})
    rom[set_table + 4 * (SUPER - 7):set_table + 4 * (SUPER - 6)] = _word(head + ROM_BASE)
    for at in sites:
        rom[at] = NEW_BYTE[rom[at]]
    for w in SET_WORDS:
        rom[w:w + 4] = _word(SUPER)
    for rec in portraits:
        rom[rec + 3] = PORTRAIT_NEW
    if word_52 == "vanilla":                           # until I draw 52, it shows 40's frame
        rom[block + 4 + 4 * PORTRAIT_NEW:block + 8 + 4 * PORTRAIT_NEW] = rom[block + 4 + 4 * PORTRAIT_OLD:
                                                                                block + 8 + 4 * PORTRAIT_OLD]
    rom[scouter + 8] = SUPER                           # u32 fields: only the low bytes change (30, 40 < 256)
    rom[scouter + 0xC] = PORTRAIT_NEW

    syms = {"SET_SUPER": head + ROM_BASE, "OURS": old["idle_ours"] | 1, "OLD": old["idle"] | 1}
    size = len(assemble(CODE, ROM_BASE, syms)[0])
    code = alloc.alloc(size)
    blob, labels = assemble(CODE, code + ROM_BASE, syms)
    if len(blob) != size:
        raise ValueError(f"code assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[code:code + size] = blob
    for vt in VTABLES:
        rom[vt + 4 - ROM_BASE:vt + 8 - ROM_BASE] = _word((labels["spc_idle"] | 1) - vt)

    name = alloc.alloc(len(SUPER_NAME))                # after the code, so r32's allocations keep their place
    rom[name:name + len(SUPER_NAME)] = SUPER_NAME
    rom[scouter:scouter + 4] = _word(name + ROM_BASE)
    text = alloc.alloc(len(SUPER_TEXT))                # after the name, so r34's allocations keep their place
    rom[text:text + len(SUPER_TEXT)] = SUPER_TEXT
    rom[scouter + 4:scouter + 8] = _word(text + ROM_BASE)
    for at, (_, new) in STATS.items():
        rom[TYPE25 + at:TYPE25 + at + len(new)] = new
    alloc.notes["superperfect_cell"] = {"set_58": head, "code": code, "size": size, "sites": sites,
                                        "portraits": portraits, "scouter_entry": scouter, "name_19": name,
                                        "text_19": text,
                                        "portrait_52": "alias_40" if word_52 == "vanilla" else "owner"}
