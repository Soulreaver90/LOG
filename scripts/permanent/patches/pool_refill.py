r"""
pool_refill.py - Trial patch: a scripted form change (ext 73) gives the leader a FULL Super Saiyan ki pool
                 (the owner 2026-11-09, after future_v3: "his ssj ki is still not reset. When he transforms
                 against cell, it keeps the wasted ssj ki from the android battle").

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt --out <new .gba>
Input:   the ROM after bf_ki_pool (the pool, its RAM block and its pool_ref) and after the module that owns the
         LIVE ext op table, which is chapter_cards in the r41 lists. It runs BEFORE finale_blast, so that
         module's own copy of the table carries the wrapped word, the way chapter_cards carries
         relay_cooldown's ext 70 word. Run after finale_blast instead and the two copies disagree.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["pool_refill"], every write as
         (offset, length, name) in its "sites".
Method:  bf_ki_pool keeps the pool in RAM 0x03003A00: +0 u16 pool, +2 u16 tag (0x8000 | leader << 8 | entry).
         pool_ref fills the pool to max EP only when the tag does not match the leader it reads, and only
         state 35 (transform) clears that tag first. A SCRIPTED form change is ext 73, not state 35, so the
         tag survives it and the pool does not refill.
         THE DEFECT. The ending gives Trunks appearance entry 16 (`set:133`) for the android fights, so the
         tag is 0x8310. Ending word 13 puts him back to entry 15 (`set:132`), and pool_ref leaves the tag
         alone on that path. The plateau's own transform then sets entry 16 again, the tag it computes is
         0x8310 once more, and the pool keeps the value the android fights left.
         THE FIX. A wrapper on the ext 73 table word:
         1. Read the leader's appearance entry (save struct 0x03000E90 + 0xC + 28 x leader, +8), the byte
            ext 73 itself writes through the reverse lookup `@0x080042BC`.
         2. Call the vanilla handler 0x0800A8ED through bx r3, with r0, the script context, untouched, and
            keep its result. A Thumb BL cannot reach rom:0xA8EC from the expansion area.
         3. Read the entry again. When it is the same byte, do nothing: the op changed a non-leader, or it
            set the body the leader already wore, and his pool is his own.
         4. When it changed, write 0 to the tag and call bf_ki_pool's pool_ref. That is fill_end's own pair
            of steps, so there is one refill path in the ROM and not a second one. Into a pool form the
            leader gets a full pool; into any other form the tag stays 0, and the next way into a pool form
            fills it, which is what bf_ki_pool's header already promises.
         No vanilla code byte changes. The script VM reads the table word at each op.
Rules:   Every source is checked before the first write: the live ext table and its word 73, the vanilla
         handler bytes, the save pointer word, bf_ki_pool's own code at its window and the pool_ref label.
         No earlier module may list the ext 73 word in its "sites". The new space must be 0xFF and named by
         no ROM word (a named chunk stays unused, notes "skipped"). A second run raises.
         Hand-assembled Thumb through ssj2_form.assemble; tests\test_pool_refill.py decodes it with
         thumb_dis and runs it with tests.test_ssj2.Cpu.
"""
import struct

from patches import bf_ki_pool
from patches.bf_ki_pool import words_naming
from patches.finale_blast import live_ext_table
from patches.ssj2_form import assemble

# ===== constants (base ROM reads, 2026-11-09) =====
ROM_BASE = 0x08000000
EXT73 = 73
VANILLA_EXT73 = 0x0800A8ED                               # Thumb: pops the two args, leaves the form, writes
HANDLER_BODY = (0xA8EC, "f8b50168434f01398a00016012185668")   # @0x0800A8EC, the first 16 bytes
SAVE_PTR, SAVE = 0x086F7E50, 0x03000E90                  # base tick @0x0801702A: ldr r7,=0x086f7e50; ldr r0,[r7,#4]
RAM = bf_ki_pool.RAM                                     # 0x03003A00: +0 pool, +2 tag
TAG = 0x2
MAX_TRIES = 8

# ===== new code (ARMv4T Thumb). r0 = script context, as the VM's call_via_r1 passes it =====
CODE = """
ext73_fill:
    push {r4,r5,lr}
    add r4,r0,#0            ; the script context the VM passes, kept for the vanilla call
    bl lead_entry
    add r5,r0,#0            ; the leader's appearance entry before the op
    add r0,r4,#0
    ldr r3,=EXT73
    bl via_r3               ; vanilla ext 73 (r0 = its result)
    add r4,r0,#0
    bl lead_entry
    cmp r0,r5
    beq fill_done           ; the leader wears the same body: his pool is his own
    ldr r0,=RAM
    mov r1,#0x0
    strh r1,[r0,#0x2]       ; the tag is stale, so pool_ref fills the pool to max EP
    ldr r3,=POOL_REF
    bl via_r3
fill_done:
    add r0,r4,#0
    pop {r4,r5,pc}
lead_entry:                 ; r0 = the leader's appearance entry, read the way ext 73 writes it
    ldr r0,=SAVE_PTR
    ldr r0,[r0,#0x4]        ; save struct 0x03000E90
    ldrb r2,[r0,#0x0]       ; leader
    lsl r1,r2,#3
    sub r1,r1,r2
    lsl r1,r1,#2
    add r1,r1,r0
    ldrb r0,[r1,#0x14]      ; record 0xC + 28 x leader, +8 entry
    bx lr
via_r3:
    bx r3
"""


# ===== helpers =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    """(module, (offset, length)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


def syms(notes: dict) -> dict:
    return {"EXT73": VANILLA_EXT73, "SAVE_PTR": SAVE_PTR, "RAM": RAM,
            "POOL_REF": notes["bf_ki_pool"]["labels"]["pool_ref"] | 1}


# ===== checks =====

def _check(rom: bytearray, alloc) -> int:
    """The file offset of the live ext 73 table word."""
    if "pool_refill" in alloc.notes:
        raise ValueError("pool_refill already ran")
    for need in ("bf_ki_pool", "ssj2_form", "fullpower_ssj"):
        if need not in alloc.notes:
            raise ValueError(f"pool_refill needs the {need} notes: run the core list first")
    notes = alloc.notes

    # bf_ki_pool's own code, re-assembled at its window: pool_ref has to be the routine this module calls.
    pool = notes["bf_ki_pool"]
    blob, _fix, labels, _lay = bf_ki_pool.layout(pool["window"] + ROM_BASE, notes)
    if bytes(rom[pool["code"]:pool["code"] + len(blob)]) != blob or labels != pool["labels"]:
        raise ValueError("bf_ki_pool code differs from its source at its window")
    if pool["ram"] != RAM:
        raise ValueError(f"bf_ki_pool keeps the pool at 0x{pool['ram']:08X}, not 0x{RAM:08X}")

    at, count, owner = live_ext_table(rom, alloc)
    if count <= EXT73:
        raise ValueError(f"the live ext table rom:0x{at:X} holds {count} words, too few for ext {EXT73}")
    hook = at + 4 * EXT73
    _expect(rom, hook, struct.pack("<I", VANILLA_EXT73))
    _expect(rom, *((HANDLER_BODY[0], bytes.fromhex(HANDLER_BODY[1]))))
    _expect(rom, SAVE_PTR - ROM_BASE + 4, struct.pack("<I", SAVE))
    for name, (s, n) in _written(notes):
        if (name, s) == (owner, at):
            continue                                     # the table's own module laid every word of it
        if s < hook + 4 and hook < s + n:
            raise ValueError(f"ext 73 word rom:0x{hook:X} is also written by {name}: stop and report")
    return hook


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    hook = _check(rom, alloc)
    s = syms(alloc.notes)
    size, skipped = len(assemble(CODE, ROM_BASE, s)[0]), []
    for _ in range(MAX_TRIES):                           # a chunk that a ROM word names stays unused
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, ())
        if not named:
            break
        skipped.append((at, size, named))
    else:
        raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")
    blob, labels = assemble(CODE, at + ROM_BASE, s)
    if len(blob) != size:                                # pool padding depends on the address
        raise ValueError(f"wrapper assembled to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    rom[at:at + size] = blob
    rom[hook:hook + 4] = struct.pack("<I", labels["ext73_fill"] | 1)
    alloc.notes["pool_refill"] = {"wrapper": at, "size": size, "hook": hook, "labels": labels,
                                  "pool_ref": s["POOL_REF"], "skipped": skipped,
                                  "sites": [(hook, 4, "ext 73 table word"),
                                            (at, size, "ext 73 pool refill wrapper")]}
