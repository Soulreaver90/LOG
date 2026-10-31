r"""
vegeta_19_reveal.py - Trial patch: Vegeta goes Super Saiyan after his line to Android 19 (final, 2026-10-30: "Let's
                      have him transform after the dialogue (no permanent ki).").

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_vegeta19.txt --out <new .gba>
Input:   any ROM whose Android 19 table word 41 and seq 42 record are vanilla (the padded base or r39). No earlier
         patch notes are needed. Run it last, so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["vegeta_19_reveal"], every write as (offset, length,
         name) in its "sites". record() holds the design.
Method:  Map 7,15 scene table rom:0x3D40C8 (named by rom:0x3FD4F4): word 40 = seq 41, "So, does a machine like
         yourself ever experience fear?"; word 41 (rom:0x3D416C) = seq 42 rom:0x3D40B2, the fight start (HUD on,
         ext 104 (12, 2), boss bar, camera on the player). Word 41 names a copy of seq 42 with a head:
         1. Guard: leader == 2 and not transformed, else jump to the vanilla ops. ext 126 (@0x0800AF72) pushes bit 0
            of the leader's appearance entry +0. A Vegeta who walks in as a Super Saiyan keeps his form: state 35
            on entry 11 would set entry 11 +4 = 8, his base form. The Cell scenes guard their state 35 with ext 126
            too (rom:0x3E65E2, rom:0x3E6F04).
         2. push 0,35 ; ext 57: the player transform, the same 6 bytes as the space scene (rom:0x3D1FDF) and both
            Cell scenes. State 35 starts sound 55 (aura) and the power-up pose; at frame 0xA0 it plays sound 23
            and calls vtable 0x08025D9C +0x14 = bf_ki_pool's fill_end: vanilla transform(player, 1), then a full
            pool. ext 57 waits until the player leaves state 35.
         3. push 10 ; ext 42 ; push 10 ; ext 43: a white flash and the fade back, the pair the r27 Goku transform
            and celljr_fight use. vegeta_ssj_scene's NPC transform has no flash (VSJ row).
         4. The vanilla seq 42 ops, unchanged. The HUD stays off through the transform, as in both Cell scenes.
         So the fight starts with Vegeta in the normal Super Saiyan form (entry 11, form object 0x030021EC): the
         pool drains, B on the form icon drops it, no flag, no cooldown write, no ki lock.
Rules:   Source: docs\tasks\2026-10-30-vegeta-19\vegeta-19-trial.md, docs\tasks\2026-10-30-celljr-rework-plan\
         plan-report.md item 11. The table word, the seq 42 record (SHA-1), its one namer and the space scene's
         transform bytes are checked before the first write; no earlier module may list the word or the record in
         its "sites"; the new space must be 0xFF and named by no ROM word; a second run raises. The old record
         stays unchanged and unreferenced.
"""
import hashlib
import struct

from patches.bf_ki_pool import words_naming
from scene.scene_lib import ext, push

# ===== constants: sources (base and r39 bytes, scripts\one-time\2026-10-30-vegeta-19\s1_study.txt) =====
ROM_BASE = 0x08000000
TABLE, WORD = 0x3D40C8, 41                              # Android 19 table; word 41 = seq 42
SEQ42, SEQ42_LEN = 0x3D40B2, 0x16
SEQ42_SHA1 = "13d010ae3f9032c98d1728b5dbfe142c1885c7d9"
SEQ42_HEADER = bytes([42, 0, 0])                        # next index 42 (END), 0, type 0
SPACE_TRANSFORM = (0x3D1FDF, bytes.fromhex("1d0200460239"))   # space scene seq 7: push 0,35 ; ext 57
MAX_TRIES = 8

# ===== the design =====
VEGETA, PLAYER = 2, 0
TRANSFORM, FLASH = 35, 10                               # player state 35; ext 42 / ext 43 frames (r27 Goku)
LEADER, IS_TRANSFORMED = 11, 126                        # ext 11 pushes the leader, ext 126 the form bit
EQ, AND, JZ = 11, 4, 19                                 # script VM ops: eq, and, jz (one offset byte)


def body() -> bytes:
    """The transform and the flash: run only when the guard holds."""
    return ext(57, PLAYER, TRANSFORM) + ext(42, FLASH) + ext(43, FLASH)


def guard() -> bytes:
    """leader == 2 and not transformed; else jz skips body()."""
    return (ext(LEADER) + push(VEGETA) + bytes([EQ]) + ext(IS_TRANSFORMED) + push(0) + bytes([EQ, AND])
            + bytes([JZ, len(body())]))


def record(rom: bytes) -> bytes:
    """The seq 42 copy: header, guard, body, then the vanilla ops after the header."""
    return SEQ42_HEADER + guard() + body() + bytes(rom[SEQ42 + 3:SEQ42 + SEQ42_LEN])


# ===== helpers =====

def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    """(module, (offset, length, ...)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)))
    return out


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "vegeta_19_reveal" in alloc.notes:
        raise ValueError("vegeta_19_reveal already ran")
    word = TABLE + 4 * WORD
    _expect(rom, word, struct.pack("<I", SEQ42 + ROM_BASE))
    if hashlib.sha1(rom[SEQ42:SEQ42 + SEQ42_LEN]).hexdigest() != SEQ42_SHA1:
        raise ValueError(f"record rom:0x{SEQ42:X} (seq 42) differs from the base bytes")
    if rom[SEQ42:SEQ42 + 3] != SEQ42_HEADER:
        raise ValueError(f"record rom:0x{SEQ42:X} header is not {SEQ42_HEADER.hex()}")
    if words_naming(rom, SEQ42 + ROM_BASE, SEQ42 + ROM_BASE + 1, ()) != [word]:
        raise ValueError(f"0x{SEQ42 + ROM_BASE:08X} (seq 42) is not named by one word at rom:0x{word:X}")
    _expect(rom, *SPACE_TRANSFORM)
    for name, site in _written(alloc.notes):
        s, n = site[:2]
        for lo, hi, what in ((word, word + 4, "table word 41"), (SEQ42, SEQ42 + SEQ42_LEN, "seq 42 record")):
            if s < hi and lo < s + n:
                raise ValueError(f"{what} rom:0x{lo:X} is also written by {name} ({site}): stop and report")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    data, skipped = record(rom), []
    for _ in range(MAX_TRIES):                           # a chunk that a ROM word names stays unused (rom_space rule)
        at = alloc.alloc(len(data))
        if set(rom[at:at + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(data):X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + len(data), ())
        if not named:
            break
        skipped.append((at, len(data), named))
    else:
        raise ValueError(f"no free chunk of 0x{len(data):X} bytes in {MAX_TRIES} tries")
    word = TABLE + 4 * WORD
    rom[at:at + len(data)] = data
    rom[word:word + 4] = struct.pack("<I", at + ROM_BASE)
    alloc.notes["vegeta_19_reveal"] = {"record": at, "size": len(data), "source": SEQ42, "word": word,
                                       "skipped": skipped,
                                       "sites": [(word, 4, "Android 19 table word 41 (seq 42)"),
                                                 (at, len(data), "seq 42 copy (Vegeta transforms)")]}
