r"""
gameover_card.py - Trial patch: lose to Cell in the final arena and the game-over screen shows the owner's own
                   card instead of "You have died!".

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_gameover.txt --out <new .gba>
Input:   the ROM after build_list_trial_plateau.txt (dev r41, battle_arena, ending_fight, future_androids,
         plateau). It must run LAST: it reads the LIVE game-over table through the literal rom:0x8870, so
         chamber_spar's words 4 and 15 come with it, and it needs map 7,100 to exist.
API:     apply(rom, alloc) -> None; every write as (offset, length, name) in alloc.notes["gameover_card"]["sites"].
         `cards()`, `map_test()` and `record_zero()` hold the design, so a test reads it from one place.

The owner's idea, in his words (2026-11-07): "instead of the generic you died message, add a custom
message... Cell defeats trunks and takes his time machine blank years to the past... a call back to how
the other timeline cell beats trunks and goes to the past, thats how he ends up in the present".

         1. THE ENGINE ALREADY BRANCHES THE GAME-OVER SCREEN ON THE MAP, so this patch copies that shape
            and invents nothing. Vanilla record 0 rom:0x3B6104 opens with
            `ext 8 ; push 6 ; eq ; ext 9 ; push 70 ; eq ; and ; jz 3 ; push 4 ; end`: on map 6,70, the
            Capsule Corp sparring room, it runs the sparring loss instead of the death screen.
         2. ext 8 (@0x0800942A) and ext 9 (@0x0800943E) push bytes +0 and +1 of the struct at
            [0x083B5C78 + 0x10] = 0x03002080, the map info word: the CURRENT zone and area.
         3. A second test of the SAME shape goes in front of the vanilla one, so both read the map at the
            same point, before the record's own `ext 39` load of map 1,7. On map 7,100, the plateau where
            Cell fights Trunks, it jumps to a new table index.
         4. That index runs a BYTE COPY of record 0's own tail (music 16, HUD off, fade 120, load map 1,7
            at (112,144), fly pose, fade in 120), so the cards draw on the normal death screen, not over
            the arena. Then card 1, then card 2, then table index 2, the vanilla `ext 67 ; fade 240 ;
            ext 97` that ends the run. Nothing about the death screen changes except the words.
         5. The table grows from 24 words to 27. It cannot grow in place: rom:0x3B6414, the word after it,
            is the "@Game Saved!" record. So the whole table is COPIED into the expansion area with the
            three new words appended, and the one literal that names it, rom:0x8870, points at the copy.
            The vanilla table and every vanilla record stay where they are, byte for byte.
         6. SCOPE IS CELL'S FIGHT ONLY. The future 18 and 17 fights run on map 1,100 (future_androids),
            not 7,100, so they keep the vanilla "You have died!".

Capacity: a caption box is 4 lines of 144 px, not a character count. `@` and `^` are both eaten before the
         line counter runs (@0x0800B224-@0x0800B244 and @0x0800BA98), the counter breaks at the last space
         past 144 px (@0x0800B936, width 0x90), and a box that runs past 4 lines pages on (@0x0800B9A0).
         Card 1 is 44 characters and measures 2 lines, 142 px and 73 px. Both cards fit one page.

Rules:   Every source byte, word and namer is checked before the first write; a second run raises. Below
         rom:0x800000 this patch writes FOUR BYTES, the literal rom:0x8870, and nothing else.
"""
import struct

from scene.scene_lib import ROM_BASE, text, words_naming

# ===== constants: the live game-over table and its one literal (bible B0647, B0985) =====
GAME_OVER_LITERAL = 0x8870                     # the only ROM word that names the table (three shapes, base + build)
VANILLA_TABLE, TABLE_WORDS = 0x3B63B4, 24
AFTER_TABLE = 0x3B6414                         # the "@Game Saved!" record: why the table cannot grow in place
GAME_SAVED = bytes.fromhex("0100010040") + b"Game Saved!\0"
RECORD_ZERO = 0x3B6104
RECORD_ZERO_BYTES = bytes.fromhex(
    "010000"                                   # next index 1, type 0
    "020800060b020900460b0413030004110010023100000256007802281d05020e02816082"
    "2002271d02002202790078022911")
PRELUDE_OFF = 0x13                             # the vanilla jz target: music 16 .. fade in 120, then `end`
TAIL_INDEX = 2                                 # the vanilla `ext 67 ; fade 240 ; ext 97` record, next index 3 (END)

# ===== constants: the map table, read LIVE (plateau appends to it) =====
MAP_BASE_LITERAL, MAP_COUNT_BYTE, MAP_SIZE = 0xEBD8, 0xE0AE, 56

# ===== the design =====
PLATEAU_ZONE, PLATEAU_AREA = 7, 100            # the final arena: plateau.py's clone of map 7,15
CURRENT_ZONE, CURRENT_AREA = 8, 9              # ext 8 and ext 9: the map info bytes at 0x03002080
PUSH_U8, EXT, AND, EQ, END, JZ = 0, 2, 4, 11, 17, 19          # base ops (rom:0x3B5C00)
BRANCH_BYTES = 3                               # what jz skips: `push <index> ; end`
PORTRAIT = 0                                   # the vanilla death box carries portrait 0
CARDS = ("@^Cell takes the time machine into the past...",
         "@^The nightmare is just beginning.")
# The owner may prefer this colder second card once he sees the pair in play. Not built.
CARD_TWO_ALTERNATIVE = "@^The nightmare was never over."
MAX_TRIES = 8


def cards() -> tuple:
    """The two caption boxes, in order. `@` picks the box y, `^` shows the whole box at once."""
    return CARDS


def map_test(index: int) -> bytes:
    """`ext 8 ; push 7 ; eq ; ext 9 ; push 100 ; eq ; and ; jz 3 ; push index ; end`: the vanilla 6,70 shape."""
    return bytes([EXT, CURRENT_ZONE, PUSH_U8, PLATEAU_ZONE, EQ,
                  EXT, CURRENT_AREA, PUSH_U8, PLATEAU_AREA, EQ,
                  AND, JZ, BRANCH_BYTES, PUSH_U8, index, END])


def record_zero(index: int) -> bytes:
    """Vanilla record 0 with the 7,100 test in front of the 6,70 test. Both read the map before any load."""
    return RECORD_ZERO_BYTES[:3] + map_test(index) + RECORD_ZERO_BYTES[3:]


def prelude(nxt: int) -> bytes:
    """A byte copy of record 0's tail: music, HUD off, fade, load map 1,7, pose, fade in, end."""
    return bytes([nxt, 0, 0]) + RECORD_ZERO_BYTES[PRELUDE_OFF:]


def blocks(table: list) -> tuple:
    """(payload, offsets) laid out as one chunk: the four records, 4-aligned padding, then the new table."""
    prelude_index = len(table)
    card_index = (prelude_index + 1, prelude_index + 2)
    parts = [("record0", record_zero(prelude_index)),
             ("prelude", prelude(card_index[0])),
             ("card1", text(card_index[1], PORTRAIT, CARDS[0])),
             ("card2", text(TAIL_INDEX, PORTRAIT, CARDS[1]))]
    payload, offsets = bytearray(), {}
    for name, data in parts:
        offsets[name] = len(payload)
        payload += data
    payload += b"\xFF" * (-len(payload) % 4)
    offsets["table"] = len(payload)
    payload += b"\0" * 4 * (len(table) + 3)                   # the words are filled once the chunk address is known
    return bytes(payload), offsets


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


def _map_exists(rom: bytes, zone: int, area: int) -> bool:
    """The LIVE map table, read the way scene_probe.map_table() reads it: the base literal, and the count
    getter sub_0800E0AC (`MOV r0,#0xFF ; ADD r0,#n`), so an appended map is found."""
    base, count = _u32(rom, MAP_BASE_LITERAL) - ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]
    return any((rom[base + MAP_SIZE * i], rom[base + MAP_SIZE * i + 1]) == (zone, area) for i in range(count))


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "gameover_card" in alloc.notes:
        raise ValueError("gameover_card already ran")
    table = _u32(rom, GAME_OVER_LITERAL) - ROM_BASE
    if table != VANILLA_TABLE:
        raise ValueError(f"rom:0x{GAME_OVER_LITERAL:X} names rom:0x{table:X}, not the game-over table "
                         f"rom:0x{VANILLA_TABLE:X}: an earlier module moved it, stop and report")
    if words_naming(rom, table) != [GAME_OVER_LITERAL]:
        raise ValueError(f"the game-over table rom:0x{table:X} is named by more than rom:0x{GAME_OVER_LITERAL:X}: "
                         + ", ".join(f"rom:0x{w:X}" for w in words_naming(rom, table)))
    _expect(rom, AFTER_TABLE, GAME_SAVED)                     # the 24 words end here, so the table cannot grow
    _expect(rom, table, struct.pack("<I", RECORD_ZERO + ROM_BASE))
    _expect(rom, RECORD_ZERO, RECORD_ZERO_BYTES)
    if words_naming(rom, RECORD_ZERO) != [table]:
        raise ValueError(f"record 0 rom:0x{RECORD_ZERO:X} is named by a word other than table word 0")
    if RECORD_ZERO_BYTES[PRELUDE_OFF - BRANCH_BYTES:PRELUDE_OFF] != bytes([PUSH_U8, 4, END]):
        raise ValueError("record 0's jz does not skip `push 4 ; end`: the branch shape changed")
    if not _u32(rom, table + 4 * TAIL_INDEX):
        raise ValueError(f"game-over table word {TAIL_INDEX} is an END entry, not the record the cards end on")
    if not _map_exists(rom, PLATEAU_ZONE, PLATEAU_AREA):
        raise ValueError(f"map {PLATEAU_ZONE},{PLATEAU_AREA} does not exist: run plateau first")
    for name, site in _written(alloc.notes):
        s, n = site[:2]
        for lo, hi, what in ((GAME_OVER_LITERAL, GAME_OVER_LITERAL + 4, "the game-over literal"),
                             (table, table + 4 * TABLE_WORDS, "the game-over table"),
                             (RECORD_ZERO, RECORD_ZERO + len(RECORD_ZERO_BYTES), "game-over record 0")):
            if s < hi and lo < s + n:
                raise ValueError(f"{what} rom:0x{lo:X} is also written by {name} ({site}): stop and report")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    table_at = _u32(rom, GAME_OVER_LITERAL) - ROM_BASE
    table = [_u32(rom, table_at + 4 * i) for i in range(TABLE_WORDS)]
    payload, off = blocks(table)

    skipped = []
    for _ in range(MAX_TRIES):            # a chunk that a ROM word names stays unused (rom_space rule)
        at = alloc.alloc(len(payload))
        if set(rom[at:at + len(payload)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(payload):X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + len(payload))
        if not named:
            break
        skipped.append((at, len(payload), named))
    else:
        raise ValueError(f"no free chunk of 0x{len(payload):X} bytes in {MAX_TRIES} tries")

    new_words = list(table) + [at + off["prelude"] + ROM_BASE,
                               at + off["card1"] + ROM_BASE,
                               at + off["card2"] + ROM_BASE]
    new_words[0] = at + off["record0"] + ROM_BASE
    payload = bytearray(payload)
    payload[off["table"]:] = b"".join(struct.pack("<I", w) for w in new_words)

    rom[at:at + len(payload)] = payload
    rom[GAME_OVER_LITERAL:GAME_OVER_LITERAL + 4] = struct.pack("<I", at + off["table"] + ROM_BASE)
    alloc.notes["gameover_card"] = {
        "chunk": at, "size": len(payload), "offsets": dict(off), "skipped": skipped,
        "table": at + off["table"], "words": len(new_words), "old_table": table_at,
        "indices": {"prelude": TABLE_WORDS, "card1": TABLE_WORDS + 1, "card2": TABLE_WORDS + 2},
        "cards": list(CARDS),
        "sites": [(GAME_OVER_LITERAL, 4, "the game-over table literal, now the copy"),
                  (at, len(payload), "record 0 copy, prelude, two cards and the 27-word table")]}
