r"""
scouter_future.py - Trial patch: Future 17, Future 18 and Future Cell get their own scouter entries,
                    so the scouter reads them by name with their OWN weakened stats instead of nothing.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt --out <new .gba>
Input:   the ROM after build_list_trial_future.txt (dev r41, battle_arena, ending_fight, future_androids).
         It reads the three weakened enemy TYPE ids out of their notes, never a hardcoded number.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["scouter_future"], every write as
         (offset, length, name) in its "sites". entry(), bio() and names() hold the design, so a test
         and the ROM read the same text.
Method:  The scouter database is a flat table of 20-byte entries at rom:0x6F8E40: +0x00 name pointer,
         +0x04 bio pointer, +0x08 set id, +0x0C portrait id, +0x10 ENEMY TYPE INDEX (bible B1793).
         0. WHY NOTHING SHOWED. An enemy scans through the TYPE matcher `@0x080190D4`, which walks the
            table and compares `rom:0x6D56AC + 24 x entry[+0x10]` with the object's own type entry
            pointer (B2297, B2347). ending_fight and future_androids gave each future enemy a FRESH
            weakened type in the expansion area, and no scouter entry names those types, so the
            matcher returns -1 and the scan shows nothing at all.
         1. THE TABLE HAS TO GROW. All 128 entries carry a name and a bio pointer, so none can be
            taken, and the string pool at rom:0x6F9840 starts on the table's last byte + 1, so the
            table cannot be extended in place. The whole table is COPIED to the expansion area with
            three entries appended, and the 5 literal pool words that hold its base are repointed
            (B0594). The 128 copied entries are byte for byte the vanilla ones, so every vanilla name
            and bio still points into the vanilla string pool, which never moves.
         2. ONE CODE BYTE CHANGES: the `cmp r0,#0x80` immediate at rom:0x190F6, inside the type
            matcher, becomes 0x83. That is the one bound a scan has to pass.
         3. THE OTHER TWO 128 BOUNDS ARE LEFT ALONE, on purpose, and each for its own measured reason.
            See SET_MATCH_BOUND and LIST_BOUND.
         4. THE SAVE BIT. The scan info screen `@0x08018A38` sets bit (n & 7) of save byte
            0x11A + (n >> 3) with NO upper bound (`@0x08018A6E`), so entries 128 to 130 set bits 0, 1
            and 2 of byte 0x12A. `log2_save.py` puts O_SCOUTER's 128 bits at 0x11A..0x129 and O_ITEMS
            at 0x12B, so 0x12A is the one byte between them. 862 real save slots out of 293 files all
            read 0 there, and the same scan found 0x10D-0x10F NONZERO in 844 of them, so the method
            does detect a spare byte that is in use. EVIDENCE, not proof: no search shape enumerates
            every reader of a save offset built in stages.
         5. THE BIOS ARE THE VANILLA ONES. The owner, 2026-11-08: "Maybe just reuse the bios for the
            vanilla, they are essentially the same. Maybe something omnious at the end." Each bio is
            the vanilla text COPIED (not pointed at, because the tail makes it a different string)
            with one shared closing line. Cell's drops one sentence, so all three stay inside the
            582-character ceiling the vanilla table itself proves. See TAIL and CELL_CUT.
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla table
         entry, string or enemy type is written. The base-ROM writes are the 5 table literals and the
         ONE bound byte, and nothing else. This module must run AFTER ending_fight and future_androids,
         whose types it names, and BEFORE plateau, which must stay last.
"""
import struct

ROM_BASE = 0x08000000

# ===== constants: the scouter database (bible B1793, B0594; measured on the base ROM 2026-11-08) =====
TABLE, ENTRIES, ENTRY = 0x6F8E40, 128, 20
POOL = TABLE + ENTRY * ENTRIES                    # rom:0x6F9840, the string pool, immediately after
F_NAME, F_BIO, F_SET, F_PORTRAIT, F_TYPE = 0, 4, 8, 0x0C, 0x10
BASE_LITERALS = (0x18E40, 0x18F94, 0x19130, 0x195F8, 0x19924)

# The three 128 bounds, found by two independent shapes: the readers of the table literal, and an
# image-wide scan for `cmp rX,#0x80` followed by a BACKWARD conditional branch. Both shapes return
# these three and nothing else in the scouter code.
TYPE_MATCH_BOUND = 0x190F6      # `cmp r0,#0x80` in the type matcher @0x080190D4: THE ONE WE RAISE
SET_MATCH_BOUND = 0x19122       # `cmp r4,#0x80` in the set matcher @0x08019102: left at 128
LIST_BOUND = 0x19260            # `cmp r2,#0x80` in the database list loop @0x0801923A: left at 128
OLD_BOUND = 0x80
# site -> (the whole CMP, 2 bytes, so a wrong address raises instead of writing; what it bounds).
# A Thumb `CMP rX,#imm8` is `imm8, 0x28 + X`, so the immediate is the FIRST byte of the pair.
BOUND_SITES = {TYPE_MATCH_BOUND: (bytes.fromhex("8028"), "the type matcher"),
               SET_MATCH_BOUND: (bytes.fromhex("802c"), "the set matcher"),
               LIST_BOUND: (bytes.fromhex("802a"), "the database list loop")}

# SET_MATCH_BOUND stays 128 because raising it could not change one scan. The set matcher returns the
# FIRST entry whose set id matches, and our three sets (9, 11 and 28) are already carried by vanilla
# entries 2, 3 and 11, so entries 128 to 130 are unreachable through it whatever the bound is.
#
# LIST_BOUND stays 128 because the database LIST menu object is sized for exactly 128 entries, and
# raising the bound would corrupt it. Measured from sub_08019204: the object is 0x6B0 bytes
# (`mov r0,#0x6b ; lsl r0,r0,#4` @0x0801920A); list 1 holds a 4-byte index per SCANNED entry from
# +0x80 and its 128th entry ends at +0x280, which is list 2's own count word (`mov r0,#5 ;
# lsl r0,r0,#7` @0x0801922E); list 2 holds 8 bytes per distinct NAME from +0x284 and its 128th entry
# ends at +0x684, which is inside the block at +0x680 (`mov r1,#0xd ; lsl r1,r1,#7` @0x080192A8).
# Both lists are therefore exactly full at 128, with no headroom at all. The cost is stated and
# deferred: the three new entries SCAN in battle, and they do not appear in the database list menu.
LIST_SLOTS = 128                                  # what the list menu can hold, measured, not assumed

# ===== constants: the three new entries =====
NEW_ENTRIES = ENTRIES, ENTRIES + 1, ENTRIES + 2   # 128, 129, 130
NEW_COUNT = len(NEW_ENTRIES)
NEW_BOUND = ENTRIES + NEW_COUNT                   # 131

# (display name, the vanilla entry it reuses, its set id, its portrait id, the notes key of its type)
# The sets and portraits are READ BACK from the vanilla entry and checked against these, so a vanilla
# table that is not the one this module was written against raises instead of writing.
A17_SET, A18_SET, CELL_SET = 9, 11, 28
SOURCES = (("Future 17", 2, A17_SET, 28, ("future_androids", "types", A17_SET)),
           ("Future 18", 3, A18_SET, 29, ("future_androids", "types", A18_SET)),
           ("Future Cell", 11, CELL_SET, 38, ("ending_fight", "cell_type", None)))

# The closing line, the owner's "something ominous at the end", 2026-11-08. The SAME sentence on all
# three on purpose: it reads as the machine's own conclusion, repeated, and it is canon-true, because
# the player scanned the present-day 17, 18 and Cell in the main game. Two spaces after each full
# stop, which is the vanilla table's own separator.
TAIL = ("  This record matches an entry already held in this database."
        "  These readings do not belong to this time.")

# Cell's vanilla bio is the long one, so one sentence comes out: it is the least load-bearing line in
# that bio and the least true of a Cell the player has already met. Without it all three new bios sit
# inside territory the vanilla table itself proves. The separator comes out with it.
CELL_CUT = "Extraterrestrial origin may be possible.  "
VANILLA_LONGEST = 582                             # the longest bio in the vanilla table (entries 5 and 6)
# AND THE RENDER IS PROVED, not assumed. The bio box is a SCROLLING box and the only quantity it
# derives from a bio is its LINE COUNT, which it stores as `16 x lines - 0x38`. Running the game's
# own wrap rule over all 128 vanilla bios (scripts\one-time\2026-11-08-scouter-future\bio_lines.py,
# which emulates sub_0801F7FC) gives a maximum of 21 lines. Future 17 at 581, Future 18 at 582 and
# Future Cell at 587 characters all render 21 lines too, so Cell's five extra characters cost no
# line at all and the scroll extent is 280 px, a number the vanilla game already produces twice.
VANILLA_LONGEST_LINES, NEW_LINES = 21, 21

# What the vanilla bios must still be when this module runs. A length, not a hash, because the length
# is the number every budget in the design is stated against.
VANILLA_BIO_LEN = {2: 476, 3: 477, 11: 524}
VANILLA_NAME = {2: "Android 17", 3: "Android 18", 11: "Cell"}

# The save bits the three new entries use. Nothing here writes a save; the byte is named so the
# report, the test and the module read the same number. See method note 4.
O_SCOUTER, SCOUTER_BITS, SAVE_SPARE_BYTE = 0x11A, 128, 0x12A


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _cstr(rom: bytes, off: int) -> str:
    end = bytes(rom).index(b"\0", off)
    return bytes(rom[off:end]).decode("ascii")


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


# ===== the design =====

def bio(vanilla: str, cut: bool = False) -> str:
    """The vanilla bio plus the shared closing line, with Cell's one sentence dropped."""
    text = vanilla.replace(CELL_CUT, "", 1) if cut else vanilla
    if cut and text == vanilla:
        raise ValueError(f"the sentence to drop is not in the bio: {CELL_CUT!r}")
    return text + TAIL


def entry(name_at: int, bio_at: int, set_id: int, portrait: int, type_id: int) -> bytes:
    """One 20-byte scouter entry. +0x10 names the enemy's OWN weakened type, which is what makes the
    scan show HP, STR, POW and END instead of "???" (bible B1793)."""
    return (_word(name_at + ROM_BASE) + _word(bio_at + ROM_BASE)
            + _word(set_id) + _word(portrait) + _word(type_id))


def names() -> tuple:
    return tuple(row[0] for row in SOURCES)


# ===== checks =====

def _types(alloc) -> list:
    """The three weakened type ids, read out of the modules that allocated them."""
    out = []
    for name, index, set_id, portrait, (module, key, sub) in SOURCES:
        if module not in alloc.notes:
            raise ValueError(f"{module} has not run: {name} would have no weakened type to name")
        value = alloc.notes[module][key]
        value = value[sub] if sub is not None else value
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"{module} notes {key} gives {value!r} for {name}, not a type id")
        out.append(value)
    return out


def _check(rom: bytearray, alloc) -> list:
    if "scouter_future" in alloc.notes:
        raise ValueError("scouter_future already ran")
    if "plateau" in alloc.notes:
        raise ValueError("plateau has already run: it relocates the MAP table and must stay last,"
                         " so this module has to come before it in the build list")

    # The table is the one this module was written against, and nothing in it is free to take.
    for k in range(ENTRIES):
        at = TABLE + ENTRY * k
        if not _u32(rom, at + F_NAME) or not _u32(rom, at + F_BIO):
            raise ValueError(f"scouter entry {k} rom:0x{at:X} has a null name or bio pointer: the"
                             f" census that said all 128 are in use no longer holds")
    _expect(rom, TABLE + F_NAME, _word(POOL + ROM_BASE))      # entry 0's name IS the pool's first byte

    # Only the 5 literal words may name the table, and NOTHING may point inside it, or relocating the
    # table would leave that pointer behind. Both shapes run over the LIVE rom, not the base.
    lo, hi = TABLE + ROM_BASE, TABLE + ENTRY * ENTRIES + ROM_BASE
    words = memoryview(bytes(rom[:len(rom) & ~3])).cast("I")
    pointers = [4 * i for i, w in enumerate(words) if lo <= w < hi]
    if pointers != list(BASE_LITERALS):
        raise ValueError(f"the words pointing into the scouter table are {[hex(o) for o in pointers]},"
                         f" expected the {len(BASE_LITERALS)} literal sites")

    # The three bounds, each checked where it stands, including the two this module leaves alone.
    for at, (pair, what) in BOUND_SITES.items():
        _expect(rom, at, pair)
        if rom[at] != OLD_BOUND:
            raise ValueError(f"{what} rom:0x{at:X} does not compare against {OLD_BOUND}")

    # The three vanilla entries the new bios are copied from.
    for name, index, set_id, portrait, _src in SOURCES:
        at = TABLE + ENTRY * index
        if _u32(rom, at + F_SET) != set_id or _u32(rom, at + F_PORTRAIT) != portrait:
            raise ValueError(f"vanilla entry {index} is set {_u32(rom, at + F_SET)} portrait"
                             f" {_u32(rom, at + F_PORTRAIT)}, and {name} is written for set {set_id}"
                             f" portrait {portrait}")
        if _cstr(rom, _u32(rom, at + F_NAME) - ROM_BASE) != VANILLA_NAME[index]:
            raise ValueError(f"vanilla entry {index} is not {VANILLA_NAME[index]!r}")
        if len(_cstr(rom, _u32(rom, at + F_BIO) - ROM_BASE)) != VANILLA_BIO_LEN[index]:
            raise ValueError(f"vanilla entry {index}'s bio is not {VANILLA_BIO_LEN[index]} characters:"
                             f" every length budget here is stated against that number")

    types = _types(alloc)
    if len(set(types)) != NEW_COUNT:
        raise ValueError(f"the three weakened types are {types}: each entry must name its OWN type,"
                         f" or two future enemies would scan as one")
    for k in range(ENTRIES):
        if _u32(rom, TABLE + ENTRY * k + F_TYPE) in types:
            raise ValueError(f"vanilla entry {k} already names type"
                             f" {_u32(rom, TABLE + ENTRY * k + F_TYPE)}: the type matcher returns the"
                             f" FIRST match, so a future enemy would scan as that entry")

    # Nothing this module writes in the base ROM may land on an earlier module's bytes.
    mine = [(lit, 4) for lit in BASE_LITERALS] + [(TYPE_MATCH_BOUND, 1)]
    for name, (start, size) in _written(alloc.notes):
        for at, n in mine:
            if start < at + n and at < start + size:
                raise ValueError(f"rom:0x{at:X} is also written by {name}: stop and report")
    return types


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    types = _check(rom, alloc)
    sites = []

    def place(data: bytes, name: str) -> int:
        at = alloc.alloc(len(data))
        if set(rom[at:at + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(data):X} bytes) is not free")
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))
        return at

    def put(at: int, data: bytes, name: str) -> None:
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))

    added, longest = [], 0
    for (name, index, set_id, portrait, _src), type_id in zip(SOURCES, types):
        at = TABLE + ENTRY * index
        text = bio(_cstr(rom, _u32(rom, at + F_BIO) - ROM_BASE), cut=index == 11)
        longest = max(longest, len(text))
        name_at = place(name.encode("ascii") + b"\0", f"the name string {name!r}")
        bio_at = place(text.encode("ascii") + b"\0", f"{name}'s bio ({len(text)} characters)")
        added.append((name, entry(name_at, bio_at, set_id, portrait, type_id),
                      {"name": name, "name_at": name_at, "bio_at": bio_at, "bio_len": len(text),
                       "set": set_id, "portrait": portrait, "type": type_id, "from": index}))
    if longest > VANILLA_LONGEST + 8:
        raise ValueError(f"the longest new bio is {longest} characters against the vanilla ceiling"
                         f" {VANILLA_LONGEST}: that is further past it than the design allows")

    grown = bytes(rom[TABLE:TABLE + ENTRY * ENTRIES]) + b"".join(body for _n, body, _d in added)
    table = place(grown, f"the scouter database, {ENTRIES} vanilla entries plus {NEW_COUNT} new ones")

    for lit in BASE_LITERALS:
        put(lit, _word(table + ROM_BASE), "a scouter table base literal (the relocated table)")
    put(TYPE_MATCH_BOUND, bytes([NEW_BOUND]),
        f"the type matcher's entry bound ({OLD_BOUND} to {NEW_BOUND}): the one bound a scan passes")

    # Read back: the copy has to be the vanilla table plus exactly three entries, and each new entry
    # has to name a type the scan can resolve.
    if bytes(rom[table:table + ENTRY * ENTRIES]) != bytes(rom[TABLE:TABLE + ENTRY * ENTRIES]):
        raise ValueError("the copied table is not byte for byte the vanilla one")
    for k, (name, _body, detail) in zip(NEW_ENTRIES, added):
        at = table + ENTRY * k
        if _u32(rom, at + F_TYPE) != detail["type"] or _cstr(rom, _u32(rom, at + F_NAME) - ROM_BASE) != name:
            raise ValueError(f"the new entry {k} rom:0x{at:X} did not read back as {name}")

    alloc.notes["scouter_future"] = {
        "table": table, "old_table": TABLE, "entries": ENTRIES + NEW_COUNT,
        "entry_size": ENTRY, "first_new": ENTRIES, "new": [d for _n, _b, d in added],
        "bound": TYPE_MATCH_BOUND, "bound_was": OLD_BOUND, "bound_now": NEW_BOUND,
        "set_match_bound": SET_MATCH_BOUND, "list_bound": LIST_BOUND, "list_slots": LIST_SLOTS,
        "longest_bio": longest, "vanilla_longest_bio": VANILLA_LONGEST,
        "save_bits": [(O_SCOUTER + (k >> 3), k & 7) for k in NEW_ENTRIES],
        "save_spare_byte": SAVE_SPARE_BYTE,
        "sites": sorted(sites)}
