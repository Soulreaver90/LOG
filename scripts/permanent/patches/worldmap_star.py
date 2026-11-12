r"""
worldmap_star.py - Trial patch: Capsule Corp carries the GOAL star on the world map once the main
                   story is over, the way every other major quest does.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt
                --out <new .gba>
Input:   the ROM after build_list_trial_plateau.txt. It runs LAST, after every module that relocates
         the MAP table, because it writes the LIVE map 6,99 entry.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["worldmap_star"], every write as
         (offset, length, name) in its "sites". `insert()` is the two ops it adds, so a check, a
         test and the report read the same thing.
Design:  docs\design\2026-11-09-journal-and-world-map-star.md section 2.
         The owner: "With capsule corp starred in the world map as with all other major quests".

Method:  1. THE WORLD MAP IS MAP 6,99's ENTER SCRIPT. Its entry `rom:0x40B9E8` names `rom:0x3FB868`
            at `+0x30`, and that script draws 13 places, each as one block:
              `<goal condition> ; jz(9) ; ext102(x,y) ; jmp(13) ; test_flag(unlock) ; jz(7) ;
               ext101(x,y)`
            `ext 102` is the goal icon, the star, and `ext 101` the normal one. Capsule Corp is
            map 6,1 (bible B1136), its marker is (193,25), its goal block opens at `rom:0x3FB916`
            and its normal block at `rom:0x3FB925`.
         2. THE INSERT IS TWO OPS AND IT GOES ON THE `or`, NOT ON THE `jz`. The goal condition ends
            with `or` at `rom:0x3FB90E` and `jz(9)` at `rom:0x3FB90F`. This module appends
            `test_flag(196) ; or` to the `or`, so the block reads `(vanilla condition) or flag 196`.
            Editing the `or` and not the `jz` matters: `relocate` re-encodes a jump by the NEW
            address of its own op start, so folding new ops in front of the `jz` inside one edit
            would make it patch the offset byte of an inserted op instead.
         2a. NO OTHER BLOCK MOVES. That `jz` skips only its own `ext 102` and `jmp`, both of which
            sit after the insert, so its offset stays 9. Every other block's jumps are local to
            itself, and `relocate` re-encodes all of them from the new layout anyway.
         3. FLAG 196 IS THE GATE, and it is the end of the main story. Two sites in the whole ROM
            set it and both are game-ending records: `rom:0x3DCEF7`, inside the Dende farewell
            record 87, and `rom:0x3C4E8A`, inside `fade_out(300) ; ext 125 ; set_flag(196) ; end`.
            Nothing clears it. Map 6,1's own enter script already keys its rain off the same flag
            (bible B1154), and nine overworld maps branch their music on it, so it is the game's own
            "the Cell Games are over" flag. The star therefore cannot appear during the main story.
         4. THE SCRIPT IS VANILLA, so it is COPIED with the insert and the entry is repointed. Not
            one byte of `rom:0x3FB868` is written.
Rules:   Every source byte is checked before the first write; a second run raises. The only base-ROM
         write is the live map 6,99 entry's `+0x30`, and when an earlier module has already moved
         the map table that write lands in expansion instead.
"""
import struct

from scene.scene_lib import ext, op_end, push, relocate

ROM_BASE = 0x08000000

# ===== constants: the world map's own map and its enter script =====
WORLD_ZONE, WORLD_AREA = 6, 99
F_ENTER = 0x30                                    # the map entry word that names the enter script
SCRIPT_AT, SCRIPT_END = 0x3FB868, 0x3FBB28        # the script, and one past its `end` op
SCRIPT_LEN = SCRIPT_END - SCRIPT_AT               # 0x2C0

# ===== constants: Capsule Corp's own marker block =====
# Read op for op out of the base ROM 2026-11-09. A wrong byte raises instead of writing.
OR_AT, OR_BYTES = 0x3FB90E, "05"                  # the goal condition's closing `or`
JZ_AT, JZ_BYTES = 0x3FB90F, "1309"                # `jz(9)`, which skips the star and its `jmp`
GOAL_AT, NORMAL_AT = 0x3FB916, 0x3FB925           # `ext 102` the star, `ext 101` the plain icon
MARKER = (193, 25)                                # Capsule Corp's pixel on the world map
GOAL_ICON, NORMAL_ICON, TEST_FLAG = 102, 101, 19
OR_OP = 5

# ===== THE GATE =====
# Flag 196 is "the main story is over". The two records that set it are both endings, and this is
# the whole reason the star is safe: it cannot show while the player is still playing the story.
STORY_OVER = 196
SETTERS = (0x3DCEF7, 0x3C4E8A)                    # the only two SET sites in the ROM
SETTER_BYTES = "00c4021b"                         # push 196 ; ext 27 set_flag

# ===== the live map table, read the way every other module reads it =====
MAP_BASE_LITERAL, MAP_COUNT_BYTE, MAP_SIZE = 0xEBD8, 0xE0AE, 56


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()},"
                         f" expected {want.hex()}")


def map_entry(rom: bytes, zone: int, area: int) -> tuple:
    """(index, file offset) of one map's entry in THIS ROM's live table."""
    table = _u32(rom, MAP_BASE_LITERAL) - ROM_BASE
    count = 0xFF + rom[MAP_COUNT_BYTE]
    for k in range(count):
        at = table + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the live map table rom:0x{table:X} ({count} entries)")


def insert() -> bytes:
    """The two ops the star costs: `test_flag(196) ; or`.

    They go AFTER the condition's own closing `or`, so the stack is one value deep when they run and
    one value deep when they finish, which is what the `jz` that follows expects."""
    return push(STORY_OVER) + ext(TEST_FLAG) + bytes([OR_OP])


def starred_script(rom: bytes) -> bytes:
    """Map 6,99's enter script with Capsule Corp's goal condition widened by flag 196.

    `relocate` wants a record, so it is handed the three bytes in front of the script as a header
    and those three bytes are dropped again. Everything it does to the ops, the edit and the jump
    re-encode, is what this needs, and keeping one copy of that logic is why it is used at all."""
    edits = {OR_AT: (OR_BYTES, (bytes.fromhex(OR_BYTES) + insert()).hex())}
    return relocate(rom, SCRIPT_AT - 3, SCRIPT_LEN + 3, edits)[3:]


def _check(rom: bytes, alloc) -> tuple:
    """Every source byte, before the first write. A second run raises here."""
    if "worldmap_star" in alloc.notes:
        raise ValueError("worldmap_star has already run on this ROM")
    index, entry = map_entry(rom, WORLD_ZONE, WORLD_AREA)
    if _u32(rom, entry + F_ENTER) != SCRIPT_AT + ROM_BASE:
        raise ValueError(f"map {WORLD_ZONE},{WORLD_AREA} +0x{F_ENTER:X} is"
                         f" {_u32(rom, entry + F_ENTER):#010x}, not the vanilla enter script")
    _expect(rom, OR_AT, bytes.fromhex(OR_BYTES))
    _expect(rom, JZ_AT, bytes.fromhex(JZ_BYTES))
    for at, want in ((GOAL_AT, GOAL_ICON), (NORMAL_AT, NORMAL_ICON)):
        _expect(rom, at, ext(want))

    # The ops have to walk to the end exactly, or the script is not the length this module copies.
    o = SCRIPT_AT
    while o < SCRIPT_END:
        o = op_end(rom, o)
    if o != SCRIPT_END:
        raise ValueError(f"the enter script's ops end at rom:0x{o:X}, not rom:0x{SCRIPT_END:X}")

    # THE GATE. Both setters have to be where they were read, or flag 196 means something else.
    for at in SETTERS:
        _expect(rom, at, bytes.fromhex(SETTER_BYTES))
    return index, entry


def apply(rom: bytearray, alloc) -> None:
    index, entry = _check(rom, alloc)
    sites = []
    vanilla = bytes(rom[SCRIPT_AT:SCRIPT_END])        # kept, so the read-back can prove it unwritten

    blob = starred_script(rom)
    if len(blob) != SCRIPT_LEN + len(insert()):
        raise ValueError(f"the starred script is 0x{len(blob):X} bytes,"
                         f" expected 0x{SCRIPT_LEN + len(insert()):X}")
    where = alloc.alloc(len(blob))
    if set(rom[where:where + len(blob)]) != {0xFF}:
        raise ValueError(f"rom:0x{where:X} (0x{len(blob):X} bytes) is not free")
    rom[where:where + len(blob)] = blob
    sites.append((where, len(blob), "map 6,99's enter script, copied, with Capsule Corp's goal"
                                    " condition widened by flag 196"))
    rom[entry + F_ENTER:entry + F_ENTER + 4] = _word(where + ROM_BASE)
    sites.append((entry + F_ENTER, 4, f"map {WORLD_ZONE},{WORLD_AREA} +0x{F_ENTER:X}"
                                      " (the relocated enter script)"))

    # Read back out of the ROM, not out of the plan.
    if _u32(rom, entry + F_ENTER) - ROM_BASE != where:
        raise ValueError("the map 6,99 entry did not read back as the copied script")
    if bytes(rom[SCRIPT_AT:SCRIPT_END]) != vanilla:
        raise ValueError("the vanilla enter script was written; this module only copies it")
    o, copied = where, []
    while o < where + len(blob):
        copied.append(o)
        o = op_end(rom, o)
    if o != where + len(blob):
        raise ValueError(f"the copied script's ops end at rom:0x{o:X}, not its own end")

    alloc.notes["worldmap_star"] = {
        "script": where, "script_size": len(blob), "ops": len(copied),
        "source": SCRIPT_AT, "source_size": SCRIPT_LEN,
        "entry": entry, "entry_index": index, "zone": WORLD_ZONE, "area": WORLD_AREA,
        "insert": insert().hex(), "insert_at": OR_AT, "flag": STORY_OVER, "setters": list(SETTERS),
        "marker": MARKER, "goal_icon": GOAL_ICON, "normal_icon": NORMAL_ICON,
        "sites": sorted(sites)}
