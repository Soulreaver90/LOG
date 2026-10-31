r"""
relay_cooldown.py - Trial patch: a scripted fighter change (ext 70) clears the party transform cooldown (me
                    2026-10-25 9:32 AM: "Agreed, menu unchanged, just plain").

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_cooldown.txt --out <new .gba>
Input:   any ROM whose ext 70 table word is vanilla (the padded base or r39). No earlier patch notes are needed.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["relay_cooldown"], every write as (offset, length,
         name) in its "sites".
Method:  The party has one transform cooldown, save struct +8 (0x03000E98). Only the base form tick lowers it, so a
         fighter who wins while transformed hands about 0x500 to the next fighter (study FCD, vanilla LoG II).
         1. A 28-byte wrapper in free space: push {r4,lr}, call the vanilla ext 70 0x0800A785 (set_leader, then
            appearance_revert) through r3 with r0 (the script context) untouched, then the base tick's own pointer
            [0x086F7E50 +4] = 0x03000E90 and str 0 to +8, then pop {r4,pc}. r0 (the handler result) is kept.
            The far call goes through bx r3: a Thumb BL cannot reach rom:0xA784 from the expansion area.
         2. Ext op table word 70 (table 0x083B5D28, @0x08009232) at rom:0x3B5E40 names the wrapper. The script VM
            reads the word from ROM at each op, so no code byte changes.
         Every scripted ext 70 (Cell Games relay, chamber entry and exit, story leader changes) starts the new
         leader ready to transform. Switch Characters (@0x08011172) does not run ext 70 and keeps vanilla behavior.
Rules:   Source: docs\tasks\2026-10-24-form-cooldown\relay-cooldown-trial.md, form-cooldown-report.md. The table word,
         the ext 70 body and the save pointer word are checked before the first write; the new space must be 0xFF
         and named by no ROM word (a named chunk stays unused, notes "skipped"); no earlier module may list the
         table word in its "sites"; a second run raises. Hand-assembled Thumb through ssj2_form.assemble;
         tests\test_relay_cooldown.py decodes it with thumb_dis.
"""
import struct

from patches.bf_ki_pool import words_naming
from patches.ssj2_form import assemble

# ===== constants: sources (base and r39 bytes, re-read 2026-10-25) =====
ROM_BASE = 0x08000000
EXT_TABLE, EXT70 = 0x083B5D28, 70
HOOK = EXT_TABLE - ROM_BASE + 4 * EXT70                  # rom:0x3B5E40
VANILLA_EXT70 = 0x0800A785                               # Thumb: push {r3,lr} ; set_leader ; appearance_revert
EXT70_BODY = (0xA784, bytes.fromhex("08b5fff77bff9d48006af9f7a1fb08bd"))
SAVE_PTR, SAVE = 0x086F7E50, 0x03000E90                  # base tick @0x0801702A: ldr r7,=0x086f7e50 ; ldr r0,[r7,#4]
COOLDOWN = 0x8                                           # save struct +8, u32
MAX_TRIES = 8

# ===== new code (ARMv4T Thumb). r0 = script context, as the VM's call_via_r1 passes it =====
CODE = """
ext70_cd:
    push {r4,lr}
    ldr r3,=EXT70
    bl via_r3               ; vanilla ext 70: set_leader, appearance_revert (r0 = its result)
    ldr r1,=SAVE_PTR
    ldr r1,[r1,#0x4]        ; save struct 0x03000E90
    mov r2,#0x0
    str r2,[r1,#0x8]        ; transform cooldown 0: the new leader starts ready
    pop {r4,pc}
via_r3:
    bx r3
"""
SYMS = {"EXT70": VANILLA_EXT70, "SAVE_PTR": SAVE_PTR}


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "relay_cooldown" in alloc.notes:
        raise ValueError("relay_cooldown already ran")
    _expect(rom, HOOK, struct.pack("<I", VANILLA_EXT70))
    _expect(rom, *EXT70_BODY)
    _expect(rom, SAVE_PTR - ROM_BASE + 4, struct.pack("<I", SAVE))
    for name, site in _written(alloc.notes):
        s, n = site[:2]
        if s < HOOK + 4 and HOOK < s + n:
            raise ValueError(f"ext 70 word rom:0x{HOOK:X} is also written by {name} ({site}): stop and report")


def _written(notes: dict) -> list:
    """(module, (offset, length, ...)) of every earlier module's "sites": triples, or bare offsets (superperfect_cell)."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)))
    return out


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    size, skipped = len(assemble(CODE, ROM_BASE, SYMS)[0]), []
    for _ in range(MAX_TRIES):                           # a chunk that a ROM word names stays unused (rom_space rule)
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, ())
        if not named:
            break
        skipped.append((at, size, named))
    else:
        raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")
    blob, labels = assemble(CODE, at + ROM_BASE, SYMS)
    if len(blob) != size:                                # pool padding depends on the address
        raise ValueError(f"wrapper assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[at:at + size] = blob
    rom[HOOK:HOOK + 4] = struct.pack("<I", labels["ext70_cd"] | 1)
    alloc.notes["relay_cooldown"] = {"wrapper": at, "size": size, "hook": HOOK, "skipped": skipped,
                                     "sites": [(HOOK, 4, "ext 70 table word"), (at, size, "ext 70 cooldown wrapper")]}
