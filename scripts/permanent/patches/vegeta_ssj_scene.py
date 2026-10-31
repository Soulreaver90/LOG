r"""
vegeta_ssj_scene.py - Trial patch: Vegeta goes Super Saiyan when he attacks Super Perfect Cell (my ask 2026-10-24
                      9:05 PM: "when Vegeta attacks S perfect cell, have him go super saiyan please!").

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_vegeta.txt --out <new .gba>
Input:   the ROM after superperfect_cell (main list, r39; celljr_fight may run before it or not). Run it last.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["vegeta_ssj_scene"], every write as (offset, length,
         name) in its "sites". transform(), volley(), exchange() and the EDITS and SHAPE tables hold the design.
Method:  Vegeta is a scene actor (NPC set 137) in both attacks; Gohan leads the whole stretch, so no record, form,
         ki or cooldown changes. Set 140 is the game's own Super Saiyan look for set 137 (appearance entry 8 +4 = 11,
         entry 11 +1 = 140). Study: docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-report.md.
         1. Attack 1, map 14,3, table rom:0x3EB704 seq 50 (after "He will pay!!!!"): word 49 (rom:0x3EB7C8) names a
            copy of the record. Vegeta walks to (376,416) and faces right as in vanilla, then powers up with the
            vanilla NPC transform (Goku rom:0x3D35D4: sound 55, state 9, sound 23, remove, spawn the Super Saiyan
            set) and faces right; every later actor push of 137 in the record becomes 140.
            v2 (final, 2026-10-25 9:16 AM): his group fires 3 ext 96 (140, 58, 100) and Cell takes 3 vanilla hits,
            the mirror of Cell's own volley at rom:0x3EB169 (each ext 96 runs 32 frames, fires at frame 16).
            v3 (final, 2026-10-25 12:44 PM) replaced Cell's answer (the second group) with a punch, a knock-out
            and a blast on Gohan. v4 (final, 2026-10-25 4:38 PM: Vegeta far right, Cell in the centre, Cell fires
            at Vegeta first, then Gohan runs in front of him) keeps that shape and changes the layout and order.
            Vegeta stands left of Cell (seq 50 walk), so Cell must cross over; the follow camera (seq 40 ext 33
            (58)) keeps Cell centred, so ext 31 fixes the view instead. Study: vegeta-ssj-v4-report.md.
            a. Cell flies past Vegeta to his left side: ext 121 (58, 12) (the fly pose ext 54 sets) and
               ext 136 (58, x, y, 500); ext 31 stops the camera on the fight; both turn to face; one punch
               ext 57 (58, 6) (16 frames, Cell's vanilla scene melee).
            b. Group: hit sound and flash on Vegeta, hurt pose ext 121 (140, 2), knock-back ext 136 far to the
               right, the v2 fall ext 57 (140, 3) (hair turns black; the hold state keeps him down until seq 52),
               ext 47 (55) ends his aura loop (as rom:0x3D8C14). Gohan walks to Vegeta's side and faces Cell.
            c. Group: Cell fires ext 96 (58, 0, n) at Gohan, who stands behind Vegeta on Cell's line, so the shot
               flies at Vegeta. A blast answers ext 60 only for its own target (@0x08011CB4-@0x08011CBA), so it
               cannot be aimed at 140. ext 69 (the plain wait; ext 43 is a fade from white) holds Gohan's ops
               until the blast is out; he flies in front of Vegeta (ext 121 (0, 12), ext 136: Cell's dash pair)
               and takes the vanilla hit (ext 60, 112, 95, 57 (0, 2)), the shape of rom:0x3D8BF6. Then he faces
               Cell and seq 51 (Cell's line) follows.
            v5 (final, 2026-10-25 9:10 PM: "Gohan jumps in front of Vegeta, he should fly in"): state 12 in
            place of the walk state 1, same move and timing. Gohan is set 160 (gi Rage, set 58 layout) here, and
            set 160 has no anim 12 (row 12 is 4 zero words; the state 12 enter @0x0800E7A0 loads set + 0x10C with
            no check). So row 12 of set 160 gets set 159's anim 12 words (gi Super Saiyan 2 flight, the same
            body and hair, 4 records a dir, 32x32, slot 0x400). Nothing else enters state 12 on set 160.
            ext 54 (the vanilla fly, 2 px a frame) would take 19 frames and miss the blast.
            Vegeta keeps 3 blasts: every ki op holds its actor 0x20 frames and fires at 0x10 (constants in the
            handlers @0x0800A19A, @0x0800A1F6, @0x0800A258), so 5 quicker blasts need new code.
         2. Seq 52 removes him: its `push 137 ; ext 52` byte (rom:0x3EB232) becomes 140, in place.
         3. Attack 2, map 14,4, table rom:0x3EC758 seq 17 (he flies at Cell in the beam struggle): word 16
            (rom:0x3EC798) names a copy that runs the same transform at his map spot (112,272), after the camera
            pan and before the camera follows him; every later push of 137 becomes 140, including the remove at its
            end. v3: ext 47 (55) follows that remove (vanilla Trunks: rom:0x3B80FD). Seq 20 spawns base 137 again.
Rules:   Source: docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-trial.md, -v2.md to -v5.md (seq 17 keeps the v1
         change and gets the aura stop: it has one blast and no answer from Cell). Every source record (SHA-1),
         table word, the seq 52 byte, the map 14,4 item and both set 160 and 159 rows are checked before the first
         write; a second run raises. The copies carry superperfect_cell's set 58 bytes; no byte that
         superperfect_cell or celljr_fight writes is written here (checked). The set 160 row is the one write into
         another module's output (gohan_gi's header, which names no sites); it is in this module's "sites".
         Old records stay unchanged and unreferenced (a state paused inside one ends it).
"""
import hashlib
import struct

from scene.scene_lib import ext, push, relocate

# ===== constants: sources (r39 bytes, study s1_scene_r39.txt) =====
ROM_BASE = 0x08000000
VEGETA, VEGETA_SSJ = 137, 140                          # appearance entry 8 and entry 11 (+1 bytes)
RIGHT = 3
SPC_TABLE, DEATH_TABLE = 0x3EB704, 0x3EC758            # type 24 and type 25 death events

# name: (table, word index, record, length, SHA-1 of the r39 record, superperfect_cell bytes inside it)
RECORDS = {
    "seq50": (SPC_TABLE, 49, 0x3EB134, 0x91, "e9dd2012a3c4dee7fd26ed652fdcb0079abad916",
              (0x16, 0x20, 0x26, 0x2B, 0x30, 0x39, 0x42, 0x4B)),
    "seq17": (DEATH_TABLE, 16, 0x3EBD7C, 0x74, "b7263f249467b615d952c389e5eea48bec9ab201",
              (0x37, 0x3D, 0x65)),
}
# name: (op offset of the insert, the op there, Vegeta's spot, {op offset: push values that name 137 from the insert})
# Seq 50 has none left: SHAPE replaces both of its groups, which hold every 137 after the insert.
EDITS = {
    "seq50": (0x1A, "023f", (376, 416), {}),
    "seq17": (0x14, "0089", (112, 272), {0x14: (137,), 0x1C: (137, 208, 376), 0x26: (137, 3), 0x33: (137, 58, 100),
                                 0x40: (137, 20), 0x5F: (137,)}),
}
SEQ52_REMOVE = (0x3EB231, bytes.fromhex("0089" "0234"))   # seq 52 word 51: push 137 ; ext 52
MAP_14_4_ITEM1 = (0x409210, bytes.fromhex(               # stand step {0x0800CB0F, wait 0x7D00, facing 3}, then
    "0fcb0008" "007d0300" "dfd60008" "00000000" "70001001" "89000000" "01000000" "10924008"))   # NPC at (112,272)

# ===== the design =====
AURA_SOUND, DONE_SOUND, POWER_UP = 55, 23, 9            # vanilla NPC transform (rom:0x3D35D4, rom:0x3B7C1C)
CELL, KI_N, VOLLEY, KNOCKED_DOWN = 58, 100, 3, 3        # Vegeta's vanilla ext 96 n; Cell's volley count; state 3
GOHAN, CELL_KI_N, HIT_SOUND = 0, 120, 34                # the player; Cell's vanilla ext 96 n; vanilla hit sound
HURT, PUNCH, FLY = 2, 6, 12                             # states: hurt, Cell's scene melee (16 frames), fly
LEFT = 2
GOHAN_RAGE, FLY_DONOR = 160, 159        # Gohan's set in the Cell fight (no anim 12); gi Super Saiyan 2 (has it)
SET_TABLE_LITERAL, FIRST_SET, ROWS, DIRS = 0x959C, 7, 0x4C, 4   # set header +2 anim count, +0x4C 4 words an anim
GOHAN_AT = (400, 408)                                   # vanilla seq 50 walk target (CELL_ANSWER)
CELL_FROM, VEGETA_AT, GOHAN_FROM = (428, 408), (376, 416), (432, 464)  # seq 40, seq 50 and seq 8 end spots
PUNCH_SPOT = (341, 408)              # left of Vegeta: anim 6 facing right reaches x + 43, 7 px into him (as v3)
KNOCKED_TO = (456, 424)              # far right: lying x 451-479, clear of 103 at (488,408)
GOHAN_WAITS = (468, 444)             # just below Vegeta's head, on the line from Cell's hand through his body
GOHAN_BLOCKS = (431, 425)            # in front of Vegeta on that line; the blast reaches his box after he stops
CAMERA, CAMERA_SPEED = (248, 328), 4                    # ext 31 view: Cell x 95-114, lying Vegeta 203-231 of 240
DASH_N, KNOCK_N, GOHAN_FLY_N = 500, 600, 500            # ext 136 speed n x 0x290 >> 8: 5, 6 and 5 px a frame
BLAST_N, GOHAN_WAIT = 80, 16                            # 2.4 px a frame; ext 96 fires 16 frames after its start
GROUP_OPEN, GROUP_CLOSE = bytes.fromhex("023f"), bytes.fromhex("0240")
CELL_HIT = ext(60, CELL) + ext(57, CELL, 2) + ext(95, CELL)      # Cell's vanilla reaction to one hit (seq 50 +0x25)
VEGETA_HIT = ext(60, VEGETA) + ext(57, VEGETA, 2) + ext(95, VEGETA)
CELL_ANSWER = (GROUP_OPEN + ext(96, CELL, VEGETA, CELL_KI_N) * VOLLEY + VEGETA_HIT * VOLLEY   # seq 50 +0x35, vanilla
               + ext(53, GOHAN, *GOHAN_AT) + ext(55, GOHAN, 3) + GROUP_CLOSE)


def transform(x: int, y: int) -> bytes:
    """Vanilla NPC Super Saiyan: aura sound, power-up anim (set 137 anim 9), sound 23, swap 137 for 140, face right."""
    return (ext(46, AURA_SOUND) + ext(57, VEGETA, POWER_UP) + ext(46, DONE_SOUND) + ext(52, VEGETA)
            + ext(51, VEGETA_SSJ, x, y) + ext(55, VEGETA_SSJ, RIGHT))


def volley(blaster: int) -> bytes:
    """v2 first group: 3 blasts from one actor, then Cell's 3 hits (Cell's volley at rom:0x3EB169, roles swapped)."""
    return GROUP_OPEN + ext(96, blaster, CELL, KI_N) * VOLLEY + CELL_HIT * VOLLEY + GROUP_CLOSE


def exchange() -> bytes:
    """v4 answer: Cell flies past Vegeta and punches him far right; his blast flies at Vegeta; Gohan flies in front
    (v5)."""
    dash_and_punch = (ext(121, CELL, FLY) + ext(136, CELL, *PUNCH_SPOT, DASH_N) + ext(31, *CAMERA, CAMERA_SPEED)
                      + ext(55, CELL, RIGHT) + ext(55, VEGETA_SSJ, LEFT) + ext(57, CELL, PUNCH))
    knock_out = (GROUP_OPEN + ext(112, VEGETA_SSJ, HIT_SOUND) + ext(95, VEGETA_SSJ) + ext(121, VEGETA_SSJ, HURT)
                 + ext(136, VEGETA_SSJ, *KNOCKED_TO, KNOCK_N) + ext(57, VEGETA_SSJ, KNOCKED_DOWN)
                 + ext(53, GOHAN, *GOHAN_WAITS) + ext(55, GOHAN, LEFT) + ext(47, AURA_SOUND) + GROUP_CLOSE)
    blast = (GROUP_OPEN + ext(96, CELL, GOHAN, BLAST_N) + ext(69, GOHAN_WAIT) + ext(121, GOHAN, FLY)
             + ext(136, GOHAN, *GOHAN_BLOCKS, GOHAN_FLY_N) + ext(60, GOHAN) + ext(112, GOHAN, HIT_SOUND) + ext(95, GOHAN)
             + ext(57, GOHAN, HURT) + GROUP_CLOSE + ext(55, GOHAN, LEFT))
    return dash_and_punch + knock_out + blast


# name: {op offset: (old ops, new ops)} beyond the 137 to 140 pushes. Seq 50: +0x1A is the whole vanilla first
# group (ext 63 to ext 64), so it carries the transform that EDITS puts there (v2 volley); +0x35 is the whole
# second group, Cell's answer (v4 exchange). Seq 17: the aura stop after the remove of 140.
SHAPE = {
    "seq50": {0x1A: (GROUP_OPEN + ext(96, VEGETA, CELL, KI_N) + CELL_HIT + GROUP_CLOSE,
                     transform(*EDITS["seq50"][2]) + volley(VEGETA_SSJ)),
              0x35: (CELL_ANSWER, exchange())},
    "seq17": {0x63: (push(CELL, 0, 0), ext(47, AURA_SOUND) + push(CELL, 0, 0))},
}


def _ssj(vals: tuple) -> tuple:
    return tuple(VEGETA_SSJ if v == VEGETA else v for v in vals)


def record_edits(name: str, rec: int) -> dict:
    """{absolute op offset: (old hex, new hex)} for npc_gi.relocate: the transform before the insert op, 137 to 140,
    then the SHAPE spans. Raises when an edit starts inside another (relocate would emit both)."""
    at, op, spot, pushes = EDITS[name]
    out = {rec + o: (push(*v).hex(), push(*_ssj(v)).hex()) for o, v in pushes.items()}
    old, new = out.get(rec + at, (op, op))
    out[rec + at] = (old, transform(*spot).hex() + new)
    for o, (old, new) in SHAPE.get(name, {}).items():
        out[rec + o] = (old.hex(), new.hex())
    for s, (old, _) in out.items():
        inside = [t for t in out if s < t < s + len(old) // 2]
        if inside:
            raise ValueError(f"{name}: edit at rom:0x{inside[0]:X} starts inside the edit at rom:0x{s:X}")
    return out


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _aligned_words(rom: bytearray, value: int) -> list:
    pat, out, i = _word(value), [], -1
    while True:
        i = rom.find(pat, i + 1)
        if i < 0:
            return out
        if i % 4 == 0:
            out.append(i)


def _set_header(rom: bytearray, set_id: int) -> int:
    """File offset of a set header, read through the live set table (gohan_gi repoints rom:0x959C)."""
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    return struct.unpack_from("<I", rom, table + 4 * (set_id - FIRST_SET))[0] - ROM_BASE


def _fly_row(rom: bytearray, set_id: int) -> int:
    """File offset of a set's anim 12 row (4 record-list words, one a dir)."""
    return _set_header(rom, set_id) + ROWS + 4 * DIRS * FLY


def _copy(rom: bytearray, name: str) -> bytes:
    _, _, rec, length, _, _ = RECORDS[name]
    return relocate(rom, rec, length, record_edits(name, rec))


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "superperfect_cell" not in alloc.notes:
        raise ValueError("vegeta_ssj_scene needs the superperfect_cell notes: run the main list first")
    if "vegeta_ssj_scene" in alloc.notes:
        raise ValueError("vegeta_ssj_scene already ran")
    spc_sites = set(alloc.notes["superperfect_cell"]["sites"])
    for name, (table, k, rec, length, sha, carried) in RECORDS.items():
        _expect(rom, table + 4 * k, _word(rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} ({name}) differs from the r39 bytes")
        if _aligned_words(rom, rec + ROM_BASE) != [table + 4 * k]:
            raise ValueError(f"0x{rec + ROM_BASE:08X} ({name}) is not named by one word at rom:0x{table + 4 * k:X}")
        if not {rec + o for o in carried} <= spc_sites:
            raise ValueError(f"{name}: superperfect_cell's set 58 bytes are not where expected")
    _expect(rom, *SEQ52_REMOVE)
    _expect(rom, SPC_TABLE + 4 * 51, _word(0x3EB21C + ROM_BASE))
    _expect(rom, *MAP_14_4_ITEM1)
    _check_fly_row(rom, alloc)


def _check_fly_row(rom: bytearray, alloc) -> None:
    """Set 160 row 12 is empty; set 159 row 12 is full; both sets share the slot. Set 160's header is named only by
    its table word and the ssj2_idle pool (@0x08894E2C compares the set pointer, then acts on the anim 0 row only)."""
    rage, donor = _set_header(rom, GOHAN_RAGE), _set_header(rom, FLY_DONOR)
    if min(rom[rage + 2], rom[donor + 2]) <= FLY:
        raise ValueError("set 160 or 159 has no row 12 in its anim table")
    _expect(rom, _fly_row(rom, GOHAN_RAGE), bytes(4 * DIRS))
    if not all(struct.unpack_from("<4I", rom, _fly_row(rom, FLY_DONOR))):
        raise ValueError("set 159 anim 12 is not set in all 4 dirs")
    if rom[rage:rage + 2] != rom[donor:donor + 2]:
        raise ValueError("sets 160 and 159 have different OBJ slots")
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    idle = alloc.notes.get("ssj2_idle", {})
    idle_span = range(idle.get("code", 0), idle.get("code", 0) + idle.get("size", 0))
    others = [w for w in _aligned_words(rom, rage + ROM_BASE) if w != table + 4 * (GOHAN_RAGE - FIRST_SET)]
    if [w for w in others if w not in idle_span]:
        raise ValueError(f"set 160 header 0x{rage + ROM_BASE:08X} is named outside its table word and ssj2_idle")


def _writes(rom: bytearray) -> list:
    """(offset, length, name) of the bytes this patch writes outside its own copies."""
    return [(t + 4 * k, 4, f"{n} table word") for n, (t, k, *_) in RECORDS.items()] + \
        [(SEQ52_REMOVE[0] + 1, 1, "seq 52 remove byte"),
         (_fly_row(rom, GOHAN_RAGE), 4 * DIRS, "set 160 anim 12 row (set 159's fly records)")]


def _no_shared_write(rom: bytearray, alloc) -> None:
    taken = {(o, 1, "superperfect_cell") for o in alloc.notes["superperfect_cell"]["sites"]}
    taken |= set(alloc.notes.get("celljr_fight", {}).get("sites", []))
    for at, n, name in _writes(rom):
        hit = [w for s, ln, w in taken if s < at + n and at < s + ln]
        if hit:
            raise ValueError(f"{name} rom:0x{at:X} is also written by {hit[0]}: stop and report")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    _no_shared_write(rom, alloc)
    copies = {name: _copy(rom, name) for name in RECORDS}
    sites, placed = [], {}
    for name, data in copies.items():
        at = alloc.alloc(len(data))
        rom[at:at + len(data)] = data
        sites.append((at, len(data), f"{name} copy (Super Saiyan Vegeta)"))
        placed[name] = at
    for name, (table, k, *_rest) in RECORDS.items():
        rom[table + 4 * k:table + 4 * k + 4] = _word(placed[name] + ROM_BASE)
    rom[SEQ52_REMOVE[0] + 1] = VEGETA_SSJ
    row = _fly_row(rom, GOHAN_RAGE)
    rom[row:row + 4 * DIRS] = rom[_fly_row(rom, FLY_DONOR):_fly_row(rom, FLY_DONOR) + 4 * DIRS]
    sites += _writes(rom)
    alloc.notes["vegeta_ssj_scene"] = {"records": placed, "sizes": {k: len(v) for k, v in copies.items()},
                                       "sources": {k: v[2] for k, v in RECORDS.items()}, "sites": sorted(sites)}
