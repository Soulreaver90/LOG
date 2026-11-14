r"""
piccolo_z_start.py - Trial patch: Super Namek is Piccolo's from the start, and the form no longer heals him.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_piccolo.txt
         --out builds\mockups\2026-11-12-piccolo-z-start\log2_piccolo_z_v1.gba
Input:   the ROM after the dev master. Reads alloc.notes["bf_ki_pool"] (its code window, labels and the
         appearance table through alloc.notes["ssj2_form"]). Needs no art and allocates no space.
API:     apply(rom, alloc) -> None; every write as (offset, length, name) in alloc.notes["piccolo_z_start"].
Method:  1. From the start. Nothing tests a story flag. The ability test 0x080134F2 reads the APPEARANCE entry
            only, and the B fire path 0x08007EDA fires whatever record +9 names. What the player cannot do is
            SELECT the transform: slot cycling 0x08004284 walks record +0x14 bits 3-6, and Piccolo's default
            record carries 0x40 (slot 3 alone). The Kami fusion opens slot 2 with ext 82 at rom:0x3E0D75
            (orr #0x20 at 0x0800AA76). So the default record gets bit 5 instead, and a new game starts with
            the transform on the L ring. Piccolo's ability ids are 9, 8, 11, 2: slot 2 is ability 11, Namek.
         2. No heal, and no ki pool. The Super Namek tick 0x08017400 is the Super Saiyan tick plus one
            block that adds max HP x 0x290 >> 16 every overflow. The form therefore moves onto
            bf_ki_pool's tick_ssj. pool_ref takes the Super Saiyan form object and nothing else, so the
            Namek form object 0x030021F0 gets no pool, and tick_ssj then runs the vanilla base tick alone:
            regular EP regenerates, the bar stays plain green and nothing touches HP. The owner decided
            that colour on 2026-11-13, green for base AND for Super Namek. piccolo_zplus gives the pool
            to appearance entry 24 alone, so only Z+ carries one. Two runs carry this:
            - Namek vtable 0x08024ABC +4 names tick_ssj.
            - State 0x25 (Namek transform) vtable 0x08025CE0 +0x14 names fill_end, so the transform end
              clears the pool tag and empties the Z charge meter in one step, as the Saiyan end does.
Rules:   Source: docs\tasks\2026-11-12-piccolo-z-start\brief.md, the Option A measurements in
         docs\tasks\2026-10-30-piccolo-ki\piccolo-ki-report.md and docs\tasks\2026-11-13-xfm9\spec.md.
         Every site is read and checked before the first write. The pool code is re-assembled from
         bf_ki_pool's own source at its own address and must match the ROM byte for byte, so this module
         cannot run out of order, twice, or against a pool blob it does not recognise. It writes no byte
         of that blob. No module file and no build list of the two masters is edited, so both master
         SHA-1s are unchanged. The stats stay +6 and the portrait stays 94.
"""
import struct

from patches import bf_ki_pool as pool
from patches.ssj2_form import assemble

# ===== constants: sites read on the dev master, 2026-11-12 =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF

# 1. the gate
DEFAULT_RECORDS, RECORD, PICCOLO = 0x1D9548, 0x1C, 1      # save_defaults 0x08003C24 DMAs 6 x 28 bytes
DEFAULT_RECORDS_LITERAL = 0x3EA0                          # the one word that names the template
FLAGS, SLOT, ENTRY, ABILITIES = 0x14, 0x9, 0x8, 0x18      # record fields
NAMEK_SLOT, NAMEK_ABILITY = 2, 11                         # record +0x1A = 11; slot k is +0x14 bit 3 + k
FLAGS_BEFORE, FLAGS_AFTER = 0x40, 0x40 | 0x20             # slot 3 alone, then slot 3 and slot 2
PICCOLO_ENTRY = 6                                         # cape, weighted (appearance entry 6)

# 2. the tick
NAMEK_VTABLE, TICK_SLOT, VANILLA_NAMEK_TICK = 0x08024ABC, 0x04, 0x08017401
STATE25_VTABLE, END_SLOT, VANILLA_TRANSFORM_END = 0x08025CE0, 0x14, 0x0801563D
NAMEK_FORM_OBJECT, SUPER_NAMEK_ENTRY = 0x030021F0, 7


# ===== helpers =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _target(rom: bytes, vtable: int, slot: int) -> int:
    """A vtable word is an offset from the vtable START, never from the slot (bible B0541)."""
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & M32


def _word(target: int, vtable: int) -> bytes:
    return struct.pack("<I", (target - vtable) & M32)


def record(index: int) -> int:
    return DEFAULT_RECORDS + RECORD * index


def _moved(have: dict, want: dict) -> list:
    """Label names whose address is missing from `want` or differs there."""
    return sorted(k for k, v in have.items() if want.get(k) != v)


def pool_code(notes: dict, source: str = None, extra: dict = None) -> tuple:
    """(blob, labels) for bf_ki_pool's code window at the address it already holds. `notes` is alloc.notes.

    bf_ki_pool.layout() builds the same blob from the same source at the same address, so a mismatch
    against the ROM means the pool moved or another module rewrote it. `source` replaces bf_ki_pool's
    own source and `extra` adds symbols, for a later module that splices pool_ref: piccolo_zplus does."""
    window = notes["bf_ki_pool"]["window"] + ROM_BASE
    code_at = notes["bf_ki_pool"]["code"] + ROM_BASE
    syms = pool.syms(notes, window)
    return assemble((pool.CODE if source is None else source) + pool.stubs()[0], code_at,
                    dict(syms, **extra) if extra else syms)


# ===== checks =====

def _check(rom: bytearray, alloc) -> dict:
    if "piccolo_z_start" in alloc.notes:
        raise ValueError("piccolo_z_start already ran")
    for need in ("ssj2_form", "bf_ki_pool"):
        if need not in alloc.notes:
            raise ValueError(f"piccolo_z_start needs the {need} notes: run the dev master first")

    if _u32(rom, DEFAULT_RECORDS_LITERAL) != DEFAULT_RECORDS + ROM_BASE:
        raise ValueError("the default record template moved: rom:0x3EA0 no longer names 0x081D9548")
    at = record(PICCOLO)
    if rom[at + ENTRY] != PICCOLO_ENTRY:
        raise ValueError(f"default record {PICCOLO} wears entry {rom[at + ENTRY]}, expected {PICCOLO_ENTRY}")
    if rom[at + ABILITIES + NAMEK_SLOT] != NAMEK_ABILITY:
        raise ValueError(f"default record {PICCOLO} slot {NAMEK_SLOT} is ability "
                         f"{rom[at + ABILITIES + NAMEK_SLOT]}, expected {NAMEK_ABILITY}")
    if _u32(rom, at + FLAGS) != FLAGS_BEFORE:
        raise ValueError(f"default record {PICCOLO} +0x14 is 0x{_u32(rom, at + FLAGS):08X}, "
                         f"expected 0x{FLAGS_BEFORE:08X}")

    for vtable, slot, want, name in ((NAMEK_VTABLE, TICK_SLOT, VANILLA_NAMEK_TICK, "Super Namek tick"),
                                     (STATE25_VTABLE, END_SLOT, VANILLA_TRANSFORM_END, "state 0x25 end")):
        have = _target(rom, vtable, slot)
        if have != want:
            raise ValueError(f"{name}: vtable 0x{vtable:08X} +0x{slot:X} names 0x{have:08X}, "
                             f"expected 0x{want:08X}")

    table = alloc.notes["ssj2_form"]["table"]
    if _u32(rom, table + 20 * SUPER_NAMEK_ENTRY + 0x10) != NAMEK_FORM_OBJECT:
        raise ValueError(f"appearance entry {SUPER_NAMEK_ENTRY} no longer holds the Namek form object")

    ki = alloc.notes["bf_ki_pool"]
    plain, plain_labels = pool_code(alloc.notes)
    here = bytes(rom[ki["code"]:ki["code"] + ki["code_len"]])
    if len(plain) != ki["code_len"] or plain != here:
        raise ValueError("the ki pool code in this ROM is not what bf_ki_pool's own source assembles to")
    moved = _moved(plain_labels, ki["labels"])           # the notes also carry the separate fix blob's labels
    if moved:
        raise ValueError("the ki pool labels moved: " + ", ".join(moved))
    return ki


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    _, labels = pool_code(alloc.notes)

    tick = NAMEK_VTABLE - ROM_BASE + TICK_SLOT
    end = STATE25_VTABLE - ROM_BASE + END_SLOT
    rom[tick:tick + 4] = _word(labels["tick_ssj"] | 1, NAMEK_VTABLE)
    rom[end:end + 4] = _word(labels["fill_end"] | 1, STATE25_VTABLE)

    gate = record(PICCOLO) + FLAGS
    rom[gate] = FLAGS_AFTER

    alloc.notes["piccolo_z_start"] = {
        "record": record(PICCOLO), "gate": gate, "flags": FLAGS_AFTER, "slot": NAMEK_SLOT,
        "tick_word": tick, "end_word": end, "tick": labels["tick_ssj"], "end": labels["fill_end"],
        "pool_ref": labels["pool_ref"],
        "sites": [(gate, 1, "Piccolo default record +0x14 (slot 2 enabled)"),
                  (tick, 4, "Namek vtable +4 (tick_ssj)"),
                  (end, 4, "state 0x25 vtable +0x14 (fill_end)")]}
