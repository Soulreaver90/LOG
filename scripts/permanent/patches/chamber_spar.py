r"""
chamber_spar.py - Patch: prototype sparring fight, Gohan (Demon Clothes) vs Goku (set 60), in the Capsule Corp
                  training room, map 6,70 (r37). First step to my Time Chamber fights.

Usage:   py -3 -P scripts\permanent\log2_build.py --list --out builds\log2_poc_r37.gba
Input:   the ROM after superperfect_cell (the r36 list). Run it last, so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["chamber_spar"]. scene(), win() and LINES hold the
         new records, so tests read the design from one place.
Method:  The vanilla room has three partners by flags 212-214 (Yamcha, Krillin, Tien). Each is an NPC spawn item,
         a walk-in region with a scene table, and an enemy spawn item that ext 104 builds in the NPC's place. This
         patch adds a fourth partner the same way, after Tien (flag 214) and after Cell (flag 195):
         1. Enemy type 95 (a boss placeholder: no spawn, no pointer, no scouter entry) becomes Goku: HP 3500,
            AI 98 (Krillin's and Tien's sparring AI), STR/POW/END 34/36/34. EXP 0, factors and the boss death
            descriptor stay.
         2. Map 6,70 (entry 175) gets copies of its spawn list (6 + NPC Goku + enemy Goku = 8) and region list
            (4 + one walk-in region = 5). The new items are Tien's three items with set 121 -> 60, type 98 -> 95,
            the NPC and region condition `flag 214 and flag 195`, and new scene tables. The old lists stay.
         3. Region scene: sound 50, fade out, ext 73 (0, 53) Demon Clothes, ext 70 (0) Gohan leads, fade in, two
            lines, ext 104 (60, 7) builds the enemy in NPC Goku's place, ext 85 (60) shows the HP bar.
         4. Win (the enemy's death event): Tien's win head with actor 60, two lines, Tien's fade, HP and EP
            refill, ext 73 (0, 157) back to the gi, Tien's warp to 6,3. No flag is set, so the fight repeats.
         5. Loss: the game-over table (rom:0x3B63B4, one literal rom:0x8870, no other word into it) gets two
            words in place. Word 4 names a copy of seq 5 with a first test: flags 214 and 195 go to index 14, the
            vanilla unused Goku line. Word 15 (END after that line) names a copy of the vanilla loss warp (seq 7)
            with ext 73 (0, 157) after the fade; its next index is 3 (END).
Rules:   Source: docs\tasks\2026-10-24-chamber-proto\chamber-proto.md, chamber-fights-study-report.md section 11. Every source
         byte, list and word is checked before the first write; a second run raises. No vanilla record changes:
         the Yamcha, Krillin and Tien paths keep their bytes. The fight sets no flag. Gohan stays the leader
         after the fight (the scene cannot read the old leader without a new variable). The four LINES are
         placeholders for me.
"""
import struct

from scene.scene_lib import code, ext, push, text

# ===== constants =====
ROM_BASE = 0x08000000
MAP_LITERALS, MAP_TABLE, MAP_SIZE = (0x5ADC, 0x5D5C, 0xEBD8), 0x409368, 56
ENTRY = 175                                            # map 6,70, the training room
REGIONS, REGION_COUNT = 0x3FB80C, 4                    # entry +0x10: {cond script, item} pairs; count at +3
SPAWNS, SPAWN_COUNT = 0x3FB7A4, 6                      # entry +0x14: item pointers; count at +4
TIEN_NPC, TIEN_ENEMY, TIEN_REGION = 0x3FB6FC, 0x3FB784, 0x3FB7F8   # spawn items 2 and 5, region item 3
TIEN_NPC_HEAD = bytes.fromhex("dfd60008" "e8b63f08" "80008800" "79000000")            # factory, cond, x y, 121
TIEN_ENEMY_HEAD = bytes.fromhex("7fe70008" "01000000" "62000000" "80008c00" "79000000" "7cb73f08")  # cond 1, 98
TIEN_REGION_ITEM = bytes.fromhex("e1d70008" "65d70008" "6800e800" "a1002101" "442f3d08")  # walk-in, Tien table
TIEN_EVENT = (0x3FB77C, bytes.fromhex("b3060108" "fc2f3d08"))                          # {event, Tien win}
EVENT_RUNNER = 0x080106B3
NPC_SIZE, ENEMY_SIZE = 0x18, 0x20
GOKU_SET, GOHAN_DEMON, GOHAN_GI = 60, 53, 157
ENEMY_ITEM = 7                                         # new spawn list: 0-5 vanilla, 6 NPC Goku, 7 enemy Goku
COND = push(214) + ext(19) + push(195) + ext(19) + bytes([4, 17])   # flag 214 and flag 195 ; end

ENEMY_TABLE, ENEMY_ENTRY = 0x6D56AC, 24
GOKU_TYPE = 95
TYPE95_VANILLA = bytes.fromhex("00000000" "05000000" "08000000" "010101" "8080" "000000" "c4f36f08")
GOKU_HP, GOKU_AI, GOKU_STATS = 3500, 98, (34, 36, 34)   # study section 8 (S): HP, AI, STR/POW/END

GAME_OVER, GAME_OVER_LITERAL = 0x3B63B4, 0x8870
SEQ5 = (0x3B615C, bytes.fromhex("050000" "00d4021300d50214041303001311" "00d502131302001011"))  # 212 !213: 19; 213: 16
SEQ7 = (0x3B61A8, bytes.fromhex("070000" "003c0245" "00780228" "020e00020a030d" "1d050c060284108520" "0226" "11"))
SEQ7_FADE_END = 11                                     # seq 7 record offset after `wait 60 ; fade 120`
GOKU_LINE, GOKU_LINE_HEAD = 0x3B627E, bytes([15, 0, 1, 63])        # word 14: "GOKU: Good fight! ..."
WORDS_OLD = {3: 0, 4: SEQ5[0] + ROM_BASE, 14: GOKU_LINE + ROM_BASE, 15: 14}
PICK_WORD, AFTER_LINE_WORD, END_WORD, GOKU_LOSS = 4, 15, 3, 14
TIEN_WIN_HEAD = (0x3D2F54, bytes.fromhex("010000" "001e0245" "1d02817208" "0239" "0258" "0032022e" "11"))
TIEN_WARP = (0x3D2FE0, bytes.fromhex("050000" "001e0245" "00780228" "1d050c0602842085200226" "00d6021b" "11"))

# ===== the new scenes =====
SOUND_SPAR, FADE, REFILL = 50, 30, 5000                # vanilla sparring sound (Tien seq 1); fade frames
GOKU_PORTRAIT, GOHAN_PORTRAIT = 63, 56                 # vanilla Goku loss line; pre-chamber Gohan
LINES = {"pre": ((GOKU_PORTRAIT, "GOKU: Gohan! Show me how strong you've gotten!"),
                 (GOHAN_PORTRAIT, "GOHAN: Okay, Dad! I won't hold back!")),
         "win": ((GOKU_PORTRAIT, "GOKU: Wow, Gohan! You're getting really strong!"),
                 (GOHAN_PORTRAIT, "GOHAN: Thanks, Dad! That was fun!"))}   # all four: my placeholders


def scene() -> list:
    """Records of the region table, in table order; each record's +0 is the next index (4 = END)."""
    (p1, l1), (p2, l2) = LINES["pre"]
    return [code(1, ext(46, SOUND_SPAR), ext(40, FADE), ext(73, 0, GOHAN_DEMON), ext(70, 0), ext(41, FADE)),
            text(2, p1, l1),
            text(3, p2, l2),
            code(4, ext(104, GOKU_SET, ENEMY_ITEM), ext(85, GOKU_SET))]


def win() -> list:
    """Records of the death event table: Tien's head (actor 60), two lines, Tien's warp without SET 214."""
    old_actor = push(121, 4)
    head = TIEN_WIN_HEAD[1].replace(old_actor, push(GOKU_SET, 4))
    warp = TIEN_WARP[1][3:-5]                          # wait 30 ; fade 120 ; push 6,3,1,272,336 ; ext 38
    tail = warp[:8] + ext(109, 0, REFILL) + ext(110, 0, REFILL) + ext(73, 0, GOHAN_GI) + warp[8:] + b"\x11"
    (p1, l1), (p2, l2) = LINES["win"]
    return [head, text(2, p1, l1), text(3, p2, l2), bytes([4, 0, 0]) + tail]


def seq5_copy() -> bytes:
    """Seq 5 with a first test: flags 214 and 195 -> index 14 (Goku's line); else the vanilla branches."""
    first = push(214) + ext(19) + push(195) + ext(19) + bytes([4, 19, 3]) + push(GOKU_LOSS) + b"\x11"
    return SEQ5[1][:3] + first + SEQ5[1][3:]           # `and ; jz +3` skips `push 14 ; end`


def loss_warp() -> bytes:
    """Seq 7 (wait, fade, half HP, warp to 6,3) with the gi back after the fade; next index END_WORD."""
    rec = SEQ7[1]
    return bytes([END_WORD]) + rec[1:SEQ7_FADE_END] + ext(73, 0, GOHAN_GI) + rec[SEQ7_FADE_END:]


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _entry() -> int:
    return MAP_TABLE + MAP_SIZE * ENTRY


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "superperfect_cell" not in alloc.notes:
        raise ValueError("chamber_spar needs the superperfect_cell notes: run the r36 list first")
    if "chamber_spar" in alloc.notes:
        raise ValueError("chamber_spar already ran")
    for lit in MAP_LITERALS:
        _expect(rom, lit, _word(MAP_TABLE + ROM_BASE))
    e = _entry()
    _expect(rom, e, bytes([6, 70]))
    _expect(rom, e + 3, bytes([REGION_COUNT, SPAWN_COUNT]))
    _expect(rom, e + 8, b"\x01")                       # combat allowed
    _expect(rom, e + 0x10, _word(REGIONS + ROM_BASE) + _word(SPAWNS + ROM_BASE))
    _expect(rom, SPAWNS + 4 * 2, _word(TIEN_NPC + ROM_BASE))
    _expect(rom, SPAWNS + 4 * 5, _word(TIEN_ENEMY + ROM_BASE))
    _expect(rom, REGIONS + 8 * 3 + 4, _word(TIEN_REGION + ROM_BASE))
    _expect(rom, TIEN_NPC, TIEN_NPC_HEAD)
    _expect(rom, TIEN_ENEMY, TIEN_ENEMY_HEAD)
    _expect(rom, TIEN_REGION, TIEN_REGION_ITEM)
    _expect(rom, *TIEN_EVENT)
    _expect(rom, ENEMY_TABLE + ENEMY_ENTRY * GOKU_TYPE, TYPE95_VANILLA)
    _expect(rom, GAME_OVER_LITERAL, _word(GAME_OVER + ROM_BASE))
    for i, w in WORDS_OLD.items():
        _expect(rom, GAME_OVER + 4 * i, _word(w))
    _expect(rom, GOKU_LINE, GOKU_LINE_HEAD)
    for at, want in (SEQ5, SEQ7, TIEN_WIN_HEAD, TIEN_WARP):
        _expect(rom, at, want)


# ===== patch =====

def _place(rom: bytearray, alloc, data: bytes) -> int:
    at = alloc.alloc(len(data))
    rom[at:at + len(data)] = data
    return at


def _place_table(rom: bytearray, alloc, records: list) -> tuple:
    """Records, then their END-terminated table; returns (table, [record offsets])."""
    recs = [_place(rom, alloc, r) for r in records]
    return _place(rom, alloc, b"".join(_word(r + ROM_BASE) for r in recs) + _word(0)), recs


def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    t95 = ENEMY_TABLE + ENEMY_ENTRY * GOKU_TYPE
    rom[t95 + 4:t95 + 0xC] = _word(GOKU_HP) + _word(GOKU_AI)
    rom[t95 + 0xC:t95 + 0xF] = bytes(GOKU_STATS)

    cond = _place(rom, alloc, COND)
    pre_table, pre_recs = _place_table(rom, alloc, scene())
    win_table, win_recs = _place_table(rom, alloc, win())
    event = _place(rom, alloc, _word(EVENT_RUNNER) + _word(win_table + ROM_BASE))
    seq5, loss = _place(rom, alloc, seq5_copy()), _place(rom, alloc, loss_warp())

    npc = bytearray(rom[TIEN_NPC:TIEN_NPC + NPC_SIZE])
    npc[4:8], npc[0xC:0x10] = _word(cond + ROM_BASE), _word(GOKU_SET)
    enemy = bytearray(rom[TIEN_ENEMY:TIEN_ENEMY + ENEMY_SIZE])
    enemy[8:0xC], enemy[0x10:0x18] = _word(GOKU_TYPE), _word(GOKU_SET) + _word(event + ROM_BASE)
    region = TIEN_REGION_ITEM[:0x10] + _word(pre_table + ROM_BASE)
    npc_at, enemy_at, region_at = (_place(rom, alloc, bytes(x)) for x in (npc, enemy, region))

    spawns = bytes(rom[SPAWNS:SPAWNS + 4 * SPAWN_COUNT]) + _word(npc_at + ROM_BASE) + _word(enemy_at + ROM_BASE)
    regions = bytes(rom[REGIONS:REGIONS + 8 * REGION_COUNT]) + _word(cond + ROM_BASE) + _word(region_at + ROM_BASE)
    spawns_at, regions_at = _place(rom, alloc, spawns), _place(rom, alloc, regions)

    e = _entry()
    rom[e + 3:e + 5] = bytes([REGION_COUNT + 1, SPAWN_COUNT + 2])
    rom[e + 0x10:e + 0x18] = _word(regions_at + ROM_BASE) + _word(spawns_at + ROM_BASE)
    rom[GAME_OVER + 4 * PICK_WORD:GAME_OVER + 4 * PICK_WORD + 4] = _word(seq5 + ROM_BASE)
    rom[GAME_OVER + 4 * AFTER_LINE_WORD:GAME_OVER + 4 * AFTER_LINE_WORD + 4] = _word(loss + ROM_BASE)
    alloc.notes["chamber_spar"] = {"cond": cond, "pre_table": pre_table, "pre_records": pre_recs,
                                   "win_table": win_table, "win_records": win_recs, "event": event,
                                   "seq5": seq5, "loss": loss, "npc": npc_at, "enemy": enemy_at,
                                   "region": region_at, "spawns": spawns_at, "regions": regions_at}
