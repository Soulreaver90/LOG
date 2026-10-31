r"""
celljr_fight.py - Trial patch: Cell spawns 7 Cell Jrs; the relay Jrs end like a boss; Gohan (Super Saiyan 2) fights
                  1 Jr, then 3 at once, then finishes 3 more in a scripted scene before "You wretched child" and the
                  Cell fight (my ask 2026-10-24; v2-v5 from my play tests; v6 the rework, me, 2026-10-30;
                  v7 his v6 play test: the Jrs surround Gohan, and the "You wretched child" pair is centred;
                  v8 his v7 play test: Gohan teleports to the last Jr instead of flying at it; v9 his v8 play
                  test: the Jrs walk in, so no record plays the flying sound; v10 his v9 play test: each scene
                  sets NPC Cell's facing, because his face-the-player step does not run while a scene plays).

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial.txt --out <new .gba>
Input:   the ROM after the main build_list.txt (r40). Run it last, so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["celljr_fight"], every write as (offset, length,
         name) in its "sites". spawn_copy(), relay_end(), fight_start(), one_v_one_end(), counter(), finish(),
         restore(), telepathy_face() hold the records, and ai_tree(), to_copy(), trial_ai() the AI copy, so tests
         read the design from one place.
Method:  Map 14,3, table rom:0x3E9D4C (Cell type 23's death event) and table rom:0x3EA400 (the third Jr's death
         event, Gohan's transform scene). Study: docs\tasks\2026-10-24-celljr-fight-study\celljr-fight-study-report.md;
         v6 plan: docs\tasks\2026-10-30-celljr-rework-plan\plan-report.md, Part 1.
         1. Spawn 7: seq 27 stays vanilla (3 NPC Jrs). Word 30 (rom:0x3E9DC4) names a copy of seq 31 that first
            spawns 4 more NPC Jrs, then runs the vanilla body with 7 removes of set 31. v6: its bar is the slice
            ext 90 (31, 25, 100), so the bar stops at 1/4 when the Jr reaches HP 0.
         2. Relay ends (v6): type 26 +0x14 (rom:0x6D5930) names the boss descriptor, so a beaten relay Jr stays at
            HP 0 with no AI and its event runs. Word 0 of the 3 relay tables names a copy of its r40 record with a
            head (sound 60, flash, hold), ext 52 (31) right after the fade out (the beaten Jr goes, no stand-in),
            and, in the two that start the next relay fight, the same 1/4 bar slice.
         3. Spawn list: 13 words copied with 5 new items. Item 13 is the 1 v 1 Jr: item 8's bytes (type 26, AI 21,
            HP 4990, scannable), event table T1. Items 14-16 are the 1 v 3 group: the trial type (HP 1550, the v5
            AI, normal death), event table T. Item 17 is the NPC Cell that faces the player (v2, v3).
         4. Fight start X: word 30 of Gohan's table (rom:0x3EA478) swaps the type 24 Cell for item 17, walks one
            NPC Jr down from above the view (set 31 has no anim 12), swaps it for item 13 under a flash, full bar.
         5. 1 v 1 end K1 (T1 word 0): the Jr explodes by script (spark, sound 31, flash, ext 52): the boss
            descriptor has no poof. 12,500 EXP, var 1 = 0. v7: a short fade puts Gohan in the arena middle
            (MIDDLE) under a view on him; 3 NPC Jrs walk in from the left, right and top view edges and become
            items 14-16 left of, right of and above him. No bar.
         6. Each group death runs table T word 0 (the runner zeroes the index, @0x080106BA): counter C adds 1 to
            var 1 and gives 12,500 EXP. Deaths 1-2 leave 1 (END); death 3 leaves 28: finish F puts Gohan in the
            middle the same way, 3 new NPC Jrs walk in from the edges (above, left, right), Gohan punches one,
            blasts one, and (v8) teleports north of the third and punches it with Goku's own teleport effect
            (GOKU_TP). Then N (word 29): fade, Cell back on his vanilla spot, seq 11's camera (v7). Words 30 and
            31 name the vanilla "You wretched child" and seq 32 records.
         7. Super Perfect Cell talk: word 57 of table rom:0x3EB704 names a copy of seq 58 that faces Gohan right.
         8. v5 trial AI: a copy of AI 21 rows 21-28 (39 nodes re-pointed): row 26' waits 30 frames after the punch,
            row 22's blast roll is 2.5 %. The trial type is type 26's bytes with +4 = 1550 and +8 = the trial AI.
Rules:   Sources: docs\tasks\2026-10-24-celljr-trial\celljr-trial*.md (v1-v5) and
         docs\tasks\2026-10-30-celljr-rework\celljr-rework.md (final decisions v6), celljr-v7.md (v7).
         Every source byte, word and record is checked before the first write; a second run raises. Ext ops pop
         their arguments, so each code record ends with an empty stack except C, which leaves its next index.
         A find by set binds the newest actor (@0x08006E0A walks the world list from the end), so each ext 53
         follows its own ext 51, every NPC Jr is removed before the first Jr enemy exists, and F spawns its 3 Jrs
         in the reverse of the order it ends them. Each flash is a pair: ext 42 fades to white, ext 43 fades back.
         F waits on a hit (ext 60) only for the blast: a scene blast ends ext 60 on its target (VS4); a player
         melee on an NPC is not proven to, so the melee uses a fixed ext 69 in the group. VM var 0 is the 14,3
         ambient script's scratch (CJR), so the counter uses var 1. Positions are first guesses (check by eye).
"""
import struct

from patches.piccolo_gi_scene import code, ext, push

# ===== constants: sources (r40 bytes, study CJR) =====
ROM_BASE = 0x08000000
MAPS, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56           # map table: +4 spawn count, +0x14 spawn list word
MAP_ENTRY = 0x40DA80                                   # map 14,3 (entry 325)
COUNT_AT, LIST_WORD = MAP_ENTRY + 4, MAP_ENTRY + 0x14
SPAWNS, SPAWN_COUNT = 0x409118, 13
ITEM8 = 0x409038                                       # first Jr enemy item (Piccolo's fight)
ITEM8_BYTES = bytes.fromhex("7fe70008" "01000000" "1a000000" "b0017801" "1f000000" "30904008" "01000000" "28904008")
ITEM8_TAIL = (0x409028, bytes.fromhex("0fcb0008" "007d0100"))       # +0x1C target, items 9-12 hold the same shape
ITEM8_EVENT = (0x409030, bytes.fromhex("b3060108" "249e3e08"))      # {event runner, Vegeta table}
ENEMY_FACTORY = 0x0800E77F
ENEMY_TABLE, ENEMY_ENTRY, JR_TYPE, JR_SET = 0x6D56AC, 24, 26, 31
TYPE26 = bytes.fromhex("00000000" "7e130000" "15000000" "2e322e" "8080" "000000" "54566d08")   # HP 4990, AI 21
TYPE_HP, TYPE_AI, TYPE_DESC = 4, 8, 0x14
NORMAL_DESC, BOSS_DESC = 0x086D5654, 0x086FF3C4        # poof and remove / stay at HP 0 with no AI (CJP rows)
BOSS_DESC_BYTES = (BOSS_DESC - ROM_BASE, bytes.fromhex("25a80108" "29a80108" "2da80108"))
TYPE26_DESC_AT = ENEMY_TABLE + ENEMY_ENTRY * JR_TYPE + TYPE_DESC   # rom:0x6D5930
JR_ITEMS_VANILLA = [(325, 8), (325, 9), (325, 10)]     # (map entry, item) of every enemy item of type 26
EVENT_RUNNER = 0x080106B3
ITEM_SIZE = 0x20

# NPC item: +0 factory, +4 cond, +8 x, y, +0xC set, +0x10 step count, +0x14 steps. Piccolo (item 4) and his step
NPC_FACTORY = 0x0800D6DF
FACE_PLAYER = bytes.fromhex("99000108" "007d0000")     # step @0x08010098 (tick @0x08010038), 32000 frames
PICCOLO_NPC = (0x408F98, FACE_PLAYER + bytes.fromhex("dfd60008" "00000000" "08026800" "67000000" "01000000"
                                                     "988f4008"))
PICCOLO_ITEM = 4
SET_TABLE_POOL, WALK_ANIM = 0x959C, 1                 # set header table; ext 53 shows anim 1 (ext 54: anim 12)

SPAWN_TABLE = 0x3E9D4C                                 # Cell type 23's death event
SEQ27 = (0x3E9C50, bytes.fromhex(
    "1b0000" "0005022a" "1d033e863086100233" "0005022b" "00280245"
    "0005022a" "1d033e866085700233" "0005022b" "00280245"
    "0005022a" "1d033e871086100233" "0005022b" "1d0200020237" "003c0245" "1d0200080239" "11"))
SEQ27_WORD = SPAWN_TABLE + 4 * 26
SEQ31 = (0x3E9CF0, bytes.fromhex(
    "1f0000" "00780228" "00230231" "1d03008660845002" "3e" "00670234" "001f0234" "001f0234" "001f0234"
    "001e0234" "00010246" "1d0200000237" "1d038500840014021f" "00080254" "1d023e020237" "00780229"
    "00280245" "00010256" "001f0255" "00000221" "11"))
SEQ31_WORD = SPAWN_TABLE + 4 * 30
REMOVE_JR = push(JR_SET) + bytes([2, 52])              # push 31 ; ext 52
SEQ31_REMOVES_END = 3 + 4 + 4 + 9 + 4 + 3 * 4          # after the third remove of set 31

GOHAN_TABLE = 0x3EA400                                 # third Jr's death event: transform scene
WRETCHED = (0x3EA3B4, bytes.fromhex("1f000128") + b"You wretched child!!!\x0bNOW TASTE MY TRUE POWER!!!!!!\x00")
SEQ32 = (0x3EA3EC, bytes.fromhex("200000" "00000221" "00010256" "1d033c328148025a" "11"))
FIGHT_WORD = GOHAN_TABLE + 4 * 30                      # rom:0x3EA478
RAGE_LINE_WORD, END_WORD = 29, 32                      # rage_text's line goes to 30; word 32 is END

# Relay death records, table word 0 each (r40 bytes, scripts\one-time\2026-10-30-celljr-rework\s3_relay_bytes.py)
VEGETA_TABLE, TRUNKS_TABLE = 0x3E9E24, 0x3E9E84        # items 8 and 9; item 10 names GOHAN_TABLE
R8 = (0x3E9DCC, bytes.fromhex(
    "010000025801868d20028b0000025600780228002702311d030086608450023e1d038500840014021f00890234000202461d020000"
    "0237000902541d023e020237007802290028024500010256001f02550000022111"))
R9 = (0x3E9E2C, bytes.fromhex(
    "010000025801868d20028b0000025600780228002602311d030086608450023e1d038500840014021f00840234000302461d020000"
    "0237000a02541d023e020237007802290028024500010256001f02550000022111"))
R10 = (0x89A71C, bytes.fromhex(                        # cellgames_ssj (r27) copy of vanilla seq 1
    "010000025801868d20028b00000256007802280000009e02491d0200ce10026e000002461d051c060289008570022700250231001e"
    "0234000002181d0200000237000b02541d0381108a00834002331d023c0202370000021d1d03877082303c021f007802290032022e"
    "11"))
RELAYS = ((VEGETA_TABLE, R8, True), (TRUNKS_TABLE, R9, True), (GOHAN_TABLE, R10, False))   # bar: next fight

SPC_TABLE = 0x3EB704                                   # type 24 Cell's death event: self-destruct to Super Perfect
SEQ52, SEQ52_PLACE_AT = 0x3EB21C, 33                                # seq 52 and its Gohan placing ops
SEQ52_PLACE = (SEQ52 + SEQ52_PLACE_AT, bytes.fromhex("1d030086608730023e" "1d0200060237"))   # (432,472), right
SEQ58 = (0x3EB4C4, bytes.fromhex("3a0000" "1d0200000237" "11"))   # Gohan faces down before "Dad!? Where are you?"
SEQ58_WORD, SEQ58_NEXT = SPC_TABLE + 4 * 57, 58                     # rom:0x3EB7E8
SEQ65 = (0x3EB6E8, bytes.fromhex("410000" "1d0200060237"))          # vanilla faces him right again for the fight
ITEM12_AT = (0x4090F8 + 0xC, struct.pack("<hh", 512, 472))          # Super Perfect Cell enemy spot
ITEM0_AT = (0x408F18 + 0xC, struct.pack("<hh", 500, 440))           # type 22 Cell in the spawn scene (v1 ss1)
ITEM11_AT = (0x4090C8 + 0xC, struct.pack("<hh", 512, 472))          # type 24 Cell, Gohan's seq 1 ext 84 (v1 ss2)

# The game's own teleport: Goku vanishes from the Cell Games arena, table rom:0x3E6078 word 83 (bible CH6, the
# record right before Imperfect Cell's "#Instant transmission..."). A white flash pair holds the actor change, and
# a hold follows. Its arrival twin rom:0x3E5C50 has the same pair; that record's ext 49 (25) is music, not copied.
GOKU_TP = (0x3E5E6A, bytes.fromhex("540000" "000a022a" "003c0234" "000a022b" "003c0245" "11"))
TP_FLASH, TP_HOLD = GOKU_TP[1][4], GOKU_TP[1][16]                   # push 10 ; ext 42 ... push 60 ; ext 69

# ===== constants: AI 21 and the trial AI (study CJB, scripts\one-time\2026-10-25-celljr-balance) =====
AI_TABLE, AI_ROW = 0x6D5194, 8                          # row id = (address - table) / 8, u32 (@0x0801AA98)
JR_AI, JR_ROWS = 21, range(21, 29)
AI_21_ROWS = (AI_TABLE + AI_ROW * JR_AI, bytes.fromhex(  # {main, hit list} x 8
    "78236d08b0236d08" "2c246d08c4f46f08" "70246d08c4f46f08" "c0246d08c4f46f08"
    "a4256d08c4f46f08" "30266d08c4f46f08" "c8266d08c4f46f08" "20276d08c4f46f08"))
NODE_BLOCK = (0x6D0000, AI_TABLE)                       # 0x086FFxxx singletons lie outside: never copied
BLAST_ROLL = (0x6D23D8, bytes.fromhex("47ba0108" "69ba0108" "00000000" "cc0c0000" "c8236d08"))   # row 22, p 5 %
TRIAL_ROLL = 0x0666                                     # 2.5 %: rand16 @0x0802142E is (rand & 0xFFFF) < p
PUNCH_SEQ = (0x6D2630, bytes.fromhex("3fb60108" "89b60108" "bdb60108" "02000000" "bc256d08" "14266d08"))  # row 26
WAIT_30 = (0x6D1FC4, bytes.fromhex("adbb0108" "00000000" "00000000" "1e000000"))   # AI 8, 45, 52 post-punch wait
COPY_COUNT = 39                                         # ai_copy_plan.txt: nodes that name a row 21-28 or reach one
DIST, WAKE, RANDOM, GUARD, PUSH, JUMP = 0x0801AEF3, 0x0801D749, 0x0801BA47, 0x0801C05B, 0x0801AB65, 0x0801B511
COMPOSITES = (0x0801B63F, 0x0801B887, 0x0801B861)       # seq, or, third composite: {f, m, m, n, child x n}
LEAVES = (0x0801B333, 0x0801B15F, 0x0801C431, 0x0801C2AD, 0x0801BBAD, 0x0801BE8B)   # movers, wait, punch

# ===== constants: the design (final decisions v1-v6) =====
# The 4 NPC Jrs after "Give them pain!" (v4: the last 2 in my circles, owner-jr-spots-2026-10-25.png).
EXTRA_SPAWNS = ((384, 408), (480, 408), (388, 366), (476, 370))
ONE_ITEM, GROUP_ITEMS = 13, (14, 15, 16)
FIGHT_ITEMS = (ONE_ITEM,) + GROUP_ITEMS
DOWN, UP, LEFT, RIGHT = 0, 1, 2, 3                 # ext 55 facings (bible CJ2 row; chapter_cards.py agrees)
# v10 (final, 2026-10-31): item 17's FACE_PLAYER step does not run while a scene plays, so each scene turns Cell
# itself. X: Gohan is 96 px north of him, the longer axis. K1 and F: Gohan sits 80 px west and 80 px north, an
# exact diagonal, and I chose left. The step sends an exact tie to its horizontal branch (`cmp r4,r5 ;
# blt`, rom:0x1006A), but it reads the live player, so it decides again once the scene ends.
CELL_FACES_X, CELL_FACES_MIDDLE = UP, LEFT
# v7 (final, 2026-10-30): the K1 and F walk-ins happen around Gohan in the arena middle, under a view on him.
# MIDDLE = the clear spot nearest the map centre (432,408); paths checked on the ss2 collision bitmap (v7_spots.py).
MIDDLE = (432, 392)
MIDDLE_VIEW = (MIDDLE[0] - 112, MIDDLE[1] - 80, 255)                # the follow target: no ease at ext 33 (0)
EDGE, VIEW_W = 24, 240                                              # a walk-in starts 24 px outside the view
GROUP_AT = ((392, 392), (472, 392), (432, 344))                     # items 14-16: left, right, above Gohan
FIGHT_AT = ((528, 344),) + GROUP_AT                                 # item 13: the v5 spot (X is unchanged)
CELL, CELL_ITEM = 30, 11
CELL_NPC_ITEM = 17                                                  # v2 change 1: NPC Cell that faces Gohan
CELL_STANDS = struct.unpack("<hh", ITEM11_AT[1])                    # v3 change 1: (512,472), Cell when X runs
CELL_AT = CELL_STANDS                                               # v7: N's spot = vanilla (v1-v6: (616,384))
GOHAN_AT, CAMERA = (576, 376), (432, 336, 40)                       # seq 1 reload spot; seq 11 camera (vanilla)
FIGHT_VIEW = (456, 288, 2)                                          # v2 change 2: Gohan near the view centre (L)
FLY_FROM_Y = 248                                                    # 40 px above the view top (L)
FLASH, FLASH_WAIT, SPAWN_PAUSE, FADE = 5, 5, 40, 120                # vanilla seq 27 and Jr table values
COUNTER_VAR, GROUP_COUNT = 1, len(GROUP_ITEMS)
EXP_EACH, GROUP_HP = 12500, 1550                                    # v6: 12,500 a Gohan Jr, 50,000 in all
T_WORDS, AFTER_KILL, FINISH_AT, RESTORE_AT, WRETCHED_AT, SEQ32_AT = 33, 1, 28, 29, 30, 31

# v6 relay end and 1 v 1 end
DING, DING_HOLD, RELAY_FLASH, BOOM = 60, 40, 10, 31                 # boss end sound; the poof's sound 31
FADE_OUT, BAR_FULL, BAR_QUARTER = ext(40, FADE), ext(85, JR_SET), ext(90, JR_SET, 25, 100)

# v6 finish F, v7 spots: Gohan at MIDDLE faces right. A (right) is punched, B (left) blasted. v8: C stands above
# him, Gohan teleports north of C, faces south and punches south (S, check by eye). C sits 32 px lower than in v7,
# because Gohan's 16 x 32 frame reaches 24 px above his spot and must stay inside the finish view (v8_spots.txt).
FINISH_FADE, ATTACK, HURT, HIT_SOUND, HIT_AT = 30, 7, 2, 34, 8      # state 7 melee (16 frames); hit at frame 8
PUNCH_AT, PUNCH_KNOCK = (456, 392), (520, 392)
BLAST_AT, BLAST_KNOCK = (384, 392), (352, 392)
TELE_AT, GOHAN_TELEPORTS_TO, TELE_KNOCK = (456, 368), (456, 344), (456, 392)
BLAST_N, KNOCK_N = 100, 600                                         # VS4 and VS5 values


# ===== the new records =====

def _spawn_group(x: int, y: int) -> bytes:
    """Vanilla seq 27 per Jr: flash, NPC Jr, wait, pause."""
    return ext(42, FLASH) + ext(51, JR_SET, x, y) + ext(43, FLASH_WAIT) + ext(69, SPAWN_PAUSE)


def _swap_once(rec: bytes, old: bytes, new: bytes) -> bytes:
    if rec.count(old) != 1:
        raise ValueError(f"{old.hex()} occurs {rec.count(old)} times, expected once")
    return rec.replace(old, new)


def spawn_copy() -> bytes:
    """Seq 31 with 4 more NPC Jrs at its head, 7 removes of set 31 (vanilla 3), and the 1/4 bar slice."""
    rec = SEQ31[1]
    groups = b"".join(_spawn_group(x, y) for x, y in EXTRA_SPAWNS)
    out = rec[:3] + groups + rec[3:SEQ31_REMOVES_END] + REMOVE_JR * len(EXTRA_SPAWNS) + rec[SEQ31_REMOVES_END:]
    return _swap_once(out, BAR_FULL, BAR_QUARTER)


def _flash(n: int) -> bytes:
    return ext(42, n) + ext(43, n)


def relay_end(rec: bytes, bar: bool) -> bytes:
    """R8, R9, R10: ding, flash, hold, then the r40 record; the beaten Jr goes right after the fade out."""
    if rec.count(FADE_OUT) != 1:
        raise ValueError("relay record: expected one ext 40 fade out")
    cut = rec.index(FADE_OUT) + len(FADE_OUT)
    out = rec[:3] + ext(46, DING) + _flash(RELAY_FLASH) + ext(69, DING_HOLD) + rec[3:cut] + REMOVE_JR + rec[cut:]
    return _swap_once(out, BAR_FULL, BAR_QUARTER) if bar else out


def _walk_in(start: tuple, spot: tuple) -> bytes:
    """One Jr: NPC at start (out of view), then a walk to its spot (the newest set 31 actor takes the walk)."""
    return ext(51, JR_SET, *start) + ext(53, JR_SET, *spot)


def _from_above(spot: tuple) -> tuple:
    """X's start: straight above the spot, above the X view (set 31 has no fly pose)."""
    return spot[0], FLY_FROM_Y


def _from_edge(spot: tuple) -> tuple:
    """v7 start under MIDDLE_VIEW: a Jr above Gohan comes from the top edge, else from the side it stands on."""
    x0, y0, _ = MIDDLE_VIEW
    if spot[1] < MIDDLE[1]:
        return spot[0], y0 - EDGE
    return (x0 - EDGE if spot[0] < MIDDLE[0] else x0 + VIEW_W + EDGE - 16), spot[1]


def _arrive_and_swap(walks: list, items: tuple) -> bytes:
    """NPC Jrs walk in to the item spots in one group, then a flash covers the swap to the enemy items."""
    arrive = ext(63) + b"".join(_walk_in(a, b) for a, b in walks) + ext(64)
    swap = ext(42, FLASH) + REMOVE_JR * len(items) + b"".join(ext(84, n) for n in items) + ext(43, FLASH_WAIT)
    return arrive + swap


def _to_middle(face: int, cell: int) -> bytes:
    """Behind a short fade: Gohan to MIDDLE, facing face, Cell turned to cell, and the view on him (v6 F's
    play-tested shape). v10: Cell turns under the black, so I never sees the turn."""
    return (ext(40, FINISH_FADE) + ext(62, 0, *MIDDLE) + ext(55, 0, face) + ext(55, CELL, cell)
            + ext(31, *MIDDLE_VIEW) + ext(41, FINISH_FADE))


def _teleport(spot: tuple, face: int) -> bytes:
    """Goku's teleport (GOKU_TP): the white flash pair holds the change, then the scene's hold. Gohan is the
    player, so the change is his ext 62 move, not the scene's remove of set 60 and its later respawn."""
    return ext(42, TP_FLASH) + ext(62, 0, *spot) + ext(55, 0, face) + ext(43, TP_FLASH) + ext(69, TP_HOLD)


def _explode() -> bytes:
    """The newest set 31 actor explodes: spark, sound 31, flash, gone (the boss descriptor has no poof)."""
    return ext(94, JR_SET, 0, 0) + ext(46, BOOM) + ext(42, FLASH) + REMOVE_JR + ext(43, FLASH_WAIT)


def fight_start() -> bytes:
    """X, Gohan's table word 30: NPC Cell (item 17) faces Gohan, one Jr comes down and becomes the 1 v 1 Jr,
    full bar. v10: the ext 55 follows the ext 84, because only then does a set 30 actor exist to bind."""
    return code(END_WORD, ext(52, CELL), ext(84, CELL_NPC_ITEM), ext(55, CELL, CELL_FACES_X),
                ext(31, *FIGHT_VIEW),
                _arrive_and_swap([(_from_above(FIGHT_AT[0]), FIGHT_AT[0])], (ONE_ITEM,)), ext(33, 0), ext(86, 1),
                BAR_FULL)


def one_v_one_end() -> bytes:
    """K1, table T1 word 0: bar off, the Jr explodes, EXP, var 1 = 0; v7: Gohan to the middle behind a fade, then
    3 Jrs walk in from the view edges and become items 14-16 around him. No bar."""
    return code(AFTER_KILL, ext(88), _explode(), ext(139, EXP_EACH), push(0) + bytes([3, COUNTER_VAR]),
                _to_middle(DOWN, CELL_FACES_MIDDLE),
                _arrive_and_swap([(_from_edge(s), s) for s in GROUP_AT], GROUP_ITEMS),
                ext(33, 0))


def counter() -> bytes:
    """C, table T word 0: var 1 += 1, 12,500 EXP, then next index 1 (END) while var 1 < 3, else 28."""
    test = bytes([21, COUNTER_VAR]) + ext(139, EXP_EACH) + bytes([2, COUNTER_VAR]) + push(GROUP_COUNT) + bytes([15])
    stay = push(AFTER_KILL) + b"\x11"
    return bytes([AFTER_KILL, 0, 0]) + test + bytes([19, len(stay)]) + stay + push(FINISH_AT) + b"\x11"


def _melee(knock: tuple) -> bytes:
    """Gohan's state 7 melee on the newest set 31 actor; the Jr reacts at a fixed frame, not on ext 60."""
    return (ext(63) + ext(57, 0, ATTACK) + ext(69, HIT_AT) + ext(112, JR_SET, HIT_SOUND) + ext(95, JR_SET)
            + ext(121, JR_SET, HURT) + ext(136, JR_SET, *knock, KNOCK_N) + ext(64))


def finish() -> bytes:
    """F, table T word 28: Gohan to the middle behind a fade; Jrs C, B, A walk in from the top, left and right
    view edges; punch A, blast B, then teleport north of C and punch it."""
    set_up = ext(88) + ext(86, 0) + _to_middle(RIGHT, CELL_FACES_MIDDLE)
    walks = b"".join(_walk_in(_from_edge(at), at) for at in (TELE_AT, BLAST_AT, PUNCH_AT))
    arrive = ext(63) + walks + ext(64)
    punch = ext(55, 0, RIGHT) + _melee(PUNCH_KNOCK) + _explode()
    blast = (ext(55, 0, LEFT) + ext(63) + ext(96, 0, JR_SET, BLAST_N) + ext(60, JR_SET) + ext(112, JR_SET, HIT_SOUND)
             + ext(95, JR_SET) + ext(121, JR_SET, HURT) + ext(136, JR_SET, *BLAST_KNOCK, KNOCK_N) + ext(64)
             + _explode())
    tele = _teleport(GOHAN_TELEPORTS_TO, DOWN) + _melee(TELE_KNOCK) + _explode()
    return code(RESTORE_AT, set_up, arrive, punch, blast, tele)


def restore() -> bytes:
    """N, table T word 29: boss bar and HUD off, fade out, Cell back as the type 24 enemy, both placed, fade in.
    v7: the vanilla "You wretched child" layout: Cell (512,472) faces right (v1 ss2 state), Gohan (576,376) faces
    down (seq 24 ext 55 (0, 0)), seq 11's camera (432,336) centres the pair."""
    return code(WRETCHED_AT, ext(88), ext(86, 0), ext(40, FADE), ext(52, CELL), ext(84, CELL_ITEM),
                ext(62, CELL, *CELL_AT), ext(55, CELL, RIGHT), ext(62, 0, *GOHAN_AT), ext(55, 0, DOWN),
                ext(31, *CAMERA), ext(41, FADE))


def telepathy_face() -> bytes:
    """Seq 58 copy: Gohan faces right, toward Super Perfect Cell (item 12 at x 512, Gohan at x 432)."""
    return code(SEQ58_NEXT, ext(55, 0, RIGHT))


def cell_npc(step_at: int) -> bytes:
    """Item 17: NPC Cell where the type 24 Cell stands, cond 1 (not built at map load), the face-the-player step."""
    return struct.pack("<IIhhIII", NPC_FACTORY, 1, *CELL_STANDS, CELL, 1, step_at + ROM_BASE)


def group_type(ai_id: int) -> bytes:
    """The trial type: type 26's bytes (normal death descriptor) with HP 1550 and the trial AI."""
    entry = bytearray(TYPE26)
    entry[TYPE_HP:TYPE_HP + 4], entry[TYPE_AI:TYPE_AI + 4] = _word(GROUP_HP), _word(ai_id)
    return bytes(entry)


# ===== the trial AI (v5) =====

def node_shape(rom: bytes, at: int) -> tuple:
    """(child slot offsets, size, row id or None) of the AI node at file offset at; an unknown factory raises."""
    f = _u32(rom, at)
    if f in (DIST, WAKE):
        return (16, 20), 24, None
    if f == RANDOM:
        return (16,), 20, None
    if f in COMPOSITES:
        n = _u32(rom, at + 12)
        return tuple(16 + 4 * i for i in range(n)), 16 + 4 * n, None
    if f == GUARD:
        return (12,), 16, None
    if f in (PUSH, JUMP):
        return (), 16, _u32(rom, at + 12)
    if f in LEAVES:
        return (), 16, None
    raise ValueError(f"rom:0x{at:X}: AI node factory 0x{f:08X} is not a known shape")


def ai_tree(rom: bytes) -> dict:
    """AI 21's nodes in the node block, reached from rows 21-28 (main and hit lists): {offset: (slots, size, row,
    child offsets)}."""
    nodes, todo = {}, [_u32(rom, AI_TABLE + AI_ROW * r + k) - ROM_BASE for r in JR_ROWS for k in (0, 4)]
    while todo:
        at = todo.pop()
        if at in nodes or not NODE_BLOCK[0] <= at < NODE_BLOCK[1]:
            continue
        slots, size, row = node_shape(rom, at)
        nodes[at] = (slots, size, row, [_u32(rom, at + s) - ROM_BASE for s in slots])
        todo += nodes[at][3]
    return nodes


def to_copy(nodes: dict) -> list:
    """Sorted offsets of the nodes that name a row 21-28 or reach one: each needs a re-pointed copy."""
    must = {a for a, (_, _, row, _) in nodes.items() if row in JR_ROWS}
    grown = True
    while grown:
        more = {a for a, (_, _, _, kids) in nodes.items() if a not in must and must.intersection(kids)}
        must |= more
        grown = bool(more)
    return sorted(must)


def trial_ai(rom: bytes, nodes_at: int, rows_at: int) -> tuple:
    """(node bytes for nodes_at, 8 row pairs for rows_at): the copy of rows 21-28 with row 26' = {PUNCH, wait 30,
    OR'} and row 22's roll at TRIAL_ROLL. Original order is kept; a child that was not copied stays shared."""
    nodes = ai_tree(rom)
    copy = to_copy(nodes)
    new, k = {}, nodes_at
    for a in copy:
        new[a] = k
        k += nodes[a][1] + (4 if a == PUNCH_SEQ[0] else 0)
    first_id = (rows_at - AI_TABLE) // AI_ROW

    def addr(p: int) -> int:
        return new[p - ROM_BASE] + ROM_BASE if p - ROM_BASE in new else p

    out = bytearray()
    for a in copy:
        slots, size, row, _ = nodes[a]
        rec = bytearray(rom[a:a + size])
        for s in slots:
            rec[s:s + 4] = _word(addr(_u32(rom, a + s)))
        if row in JR_ROWS:
            rec[12:16] = _word(first_id + row - JR_AI)
        if a == BLAST_ROLL[0]:
            rec[12:16] = _word(TRIAL_ROLL)
        if a == PUNCH_SEQ[0]:
            rec[12:] = _word(3) + rec[16:20] + _word(WAIT_30[0] + ROM_BASE) + rec[20:24]
        out += rec
    rows = b"".join(_word(addr(_u32(rom, AI_TABLE + AI_ROW * r + j))) for r in JR_ROWS for j in (0, 4))
    return bytes(out), rows


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytearray, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _aligned_words(rom: bytearray, value: int) -> list:
    """File offsets of the 4-aligned words equal to value."""
    pat, out, i = _word(value), [], -1
    while True:
        i = rom.find(pat, i + 1)
        if i < 0:
            return out
        if i % 4 == 0:
            out.append(i)


def _alloc_on_stride(alloc, size: int, base: int, stride: int) -> int:
    """Free space for size bytes at an offset with (offset - base) a multiple of stride (a table slot id)."""
    at = alloc.alloc(size + stride - 4)
    at += (base - at) % stride
    if (at - base) % stride or at % 4:
        raise ValueError(f"rom:0x{at:X} is not on the 0x{base:X} + {stride} x n grid")
    return at


def set_rows(rom: bytes, set_id: int) -> list:
    """Per anim, the 4 direction row pointers of a sprite set (header +2 = anim count, rows at +0x4C)."""
    head = _u32(rom, _u32(rom, SET_TABLE_POOL) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE
    if not 0 <= head < len(rom) - 2:
        raise ValueError(f"set {set_id}: header 0x{head + ROM_BASE:08X} is outside the ROM")
    return [[_u32(rom, head + 0x4C + 16 * a + 4 * d) for d in range(4)] for a in range(rom[head + 2])]


def enemy_items_of_type(rom: bytes, type_id: int) -> list:
    """(map entry, item index) of every enemy item (factory ENEMY_FACTORY) whose type word is type_id."""
    out = []
    for m in range(MAP_COUNT):
        entry = MAPS + MAP_SIZE * m
        count, lst = rom[entry + 4], _u32(rom, entry + 0x14) - ROM_BASE
        for k in range(count if 0 <= lst < len(rom) else 0):
            item = _u32(rom, lst + 4 * k) - ROM_BASE
            if 0 <= item < len(rom) - 12 and _u32(rom, item) == ENEMY_FACTORY and _u32(rom, item + 8) == type_id:
                out.append((m, k))
    return out


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    for module in ("superperfect_cell", "vegeta_ssj_scene"):   # vegeta_ssj_scene is the last module of the main
        if module not in alloc.notes:                          # list, and this one runs after the whole list, so
            raise ValueError(f"celljr_fight needs the {module} notes: run the main list first")   # nothing moves
    if "celljr_fight" in alloc.notes:
        raise ValueError("celljr_fight already ran")
    _expect(rom, MAP_ENTRY, bytes([14, 3]))
    _expect(rom, COUNT_AT, bytes([SPAWN_COUNT]))
    _expect(rom, LIST_WORD, _word(SPAWNS + ROM_BASE))
    _expect(rom, SPAWNS + 4 * 8, _word(ITEM8 + ROM_BASE))
    _expect(rom, ITEM8, ITEM8_BYTES)
    _expect(rom, *ITEM8_TAIL)
    _expect(rom, *ITEM8_EVENT)
    _expect(rom, ENEMY_TABLE + ENEMY_ENTRY * JR_TYPE, TYPE26)
    if TYPE26[TYPE_DESC:] != _word(NORMAL_DESC):
        raise ValueError("TYPE26 constant: +0x14 is not the normal death descriptor")
    _expect(rom, *BOSS_DESC_BYTES)
    if enemy_items_of_type(rom, JR_TYPE) != JR_ITEMS_VANILLA:
        raise ValueError(f"type 26 enemy items {enemy_items_of_type(rom, JR_TYPE)}, expected {JR_ITEMS_VANILLA}")
    for at, want in (AI_21_ROWS, BLAST_ROLL, PUNCH_SEQ, WAIT_30):
        _expect(rom, at, want)
    copy = to_copy(ai_tree(rom))
    if len(copy) != COPY_COUNT or not {BLAST_ROLL[0], PUNCH_SEQ[0]} <= set(copy):
        raise ValueError(f"AI 21 copy plan has {len(copy)} nodes, expected {COPY_COUNT} with rows 22 and 26")
    _expect(rom, *PICCOLO_NPC)
    _expect(rom, SPAWNS + 4 * PICCOLO_ITEM, _word(PICCOLO_NPC[0] + 8 + ROM_BASE))
    rows = set_rows(rom, JR_SET)
    if not (WALK_ANIM < len(rows) and all(rows[WALK_ANIM])):
        raise ValueError(f"set {JR_SET}: {len(rows)} anims; the walk-in needs anim 1 in 4 directions")
    for at, want in (SEQ27, SEQ31, WRETCHED, SEQ32, SEQ52_PLACE, SEQ58, SEQ65, GOKU_TP, ITEM12_AT, ITEM0_AT,
                     ITEM11_AT):
        _expect(rom, at, want)
    _expect(rom, SEQ27_WORD, _word(SEQ27[0] + ROM_BASE))
    _expect(rom, SEQ31_WORD, _word(SEQ31[0] + ROM_BASE))
    _expect(rom, FIGHT_WORD, _word(WRETCHED[0] + ROM_BASE))
    _expect(rom, GOHAN_TABLE + 4 * SEQ32_AT, _word(SEQ32[0] + ROM_BASE))
    _expect(rom, GOHAN_TABLE + 4 * END_WORD, _word(0))
    _expect(rom, SPC_TABLE + 4 * 51, _word(SEQ52 + ROM_BASE))
    _expect(rom, SPC_TABLE + 4 * 64, _word(SEQ65[0] + ROM_BASE))
    for table, (rec, data), _ in RELAYS:
        _expect(rom, rec, data)
        _expect(rom, table, _word(rec + ROM_BASE))
    for table in (VEGETA_TABLE, TRUNKS_TABLE):
        _expect(rom, table + 4, _word(0))
    rage_line = _u32(rom, GOHAN_TABLE + 4 * RAGE_LINE_WORD) - ROM_BASE
    if not 0 <= rage_line < len(rom) or rom[rage_line] != WRETCHED_AT:
        raise ValueError(f"Gohan's table word {RAGE_LINE_WORD} does not go to index {WRETCHED_AT}")
    if bytes(rom[SEQ31[0] + SEQ31_REMOVES_END - 3 * len(REMOVE_JR):SEQ31[0] + SEQ31_REMOVES_END]) != REMOVE_JR * 3:
        raise ValueError("seq 31 does not hold 3 removes of set 31 where expected")
    for target, site in ((SEQ31[0], SEQ31_WORD), (WRETCHED[0], FIGHT_WORD), (SPAWNS, LIST_WORD),
                         (SEQ58[0], SEQ58_WORD)) + tuple((rec, table) for table, (rec, _), _ in RELAYS):
        if _aligned_words(rom, target + ROM_BASE) != [site]:
            raise ValueError(f"0x{target + ROM_BASE:08X} is named by {len(_aligned_words(rom, target + ROM_BASE))}"
                             f" words, expected one at rom:0x{site:X}")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    sites = []

    def place(data: bytes, name: str) -> int:
        at = alloc.alloc(len(data))
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))
        return at

    def put(at: int, data: bytes, name: str) -> None:
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))

    seq31 = place(spawn_copy(), "seq 31 copy (7 Jrs, 1/4 bar)")
    fight = place(fight_start(), "record X (1 v 1 start)")
    count = place(counter(), "record C (counter)")
    rest = place(restore(), "record N (fade, Cell back)")
    seq58 = place(telepathy_face(), "seq 58 copy (Gohan faces Super Perfect Cell)")
    fin = place(finish(), "record F (scripted finish)")
    words = [0] * T_WORDS
    words[0], words[FINISH_AT], words[RESTORE_AT] = count + ROM_BASE, fin + ROM_BASE, rest + ROM_BASE
    words[WRETCHED_AT], words[SEQ32_AT] = WRETCHED[0] + ROM_BASE, SEQ32[0] + ROM_BASE
    table = place(b"".join(_word(w) for w in words), "table T (group Jr death event)")
    k1 = place(one_v_one_end(), "record K1 (1 v 1 end, 1 v 3 start)")
    table1 = place(_word(k1 + ROM_BASE) + _word(0), "table T1 (1 v 1 Jr death event)")
    relays = {}
    for tab, (rec, data), bar in RELAYS:
        relays[tab] = place(relay_end(data, bar), f"relay end copy of 0x{rec + ROM_BASE:08X}")

    items = []
    for n, (x, y) in zip(FIGHT_ITEMS, FIGHT_AT):
        tail = place(ITEM8_TAIL[1], f"item {n} tail")
        event_table = table1 if n == ONE_ITEM else table
        event = place(_word(EVENT_RUNNER) + _word(event_table + ROM_BASE), f"item {n} event struct")
        item = bytearray(ITEM8_BYTES)
        item[0xC:0x10] = struct.pack("<hh", x, y)
        item[0x14:0x18], item[0x1C:0x20] = _word(event + ROM_BASE), _word(tail + ROM_BASE)
        items.append(place(bytes(item), f"item {n} (Jr enemy)"))
    step = place(FACE_PLAYER, f"item {CELL_NPC_ITEM} step (face the player)")
    cell = place(cell_npc(step), f"item {CELL_NPC_ITEM} (NPC Cell)")
    new_items = items + [cell]
    spawns = place(bytes(rom[SPAWNS:SPAWNS + 4 * SPAWN_COUNT]) + b"".join(_word(i + ROM_BASE) for i in new_items),
                   f"spawn list copy ({SPAWN_COUNT + len(new_items)} items)")

    put(SEQ31_WORD, _word(seq31 + ROM_BASE), "spawn table word 30")
    put(FIGHT_WORD, _word(fight + ROM_BASE), "Gohan table word 30")
    put(COUNT_AT, bytes([SPAWN_COUNT + len(new_items)]), "map 14,3 spawn count")
    put(LIST_WORD, _word(spawns + ROM_BASE), "map 14,3 spawn list word")
    put(SEQ58_WORD, _word(seq58 + ROM_BASE), "self-destruct table word 57")
    for tab, at in relays.items():
        put(tab, _word(at + ROM_BASE), f"relay table 0x{tab + ROM_BASE:08X} word 0")
    put(TYPE26_DESC_AT, _word(BOSS_DESC), "type 26 +0x14 (boss death descriptor)")

    nodes = ai_tree(rom)
    nodes_at = alloc.alloc(sum(nodes[a][1] for a in to_copy(nodes)) + 4)
    rows_at = _alloc_on_stride(alloc, AI_ROW * len(JR_ROWS), AI_TABLE, AI_ROW)
    node_bytes, row_bytes = trial_ai(rom, nodes_at, rows_at)
    put(nodes_at, node_bytes, "trial AI nodes (AI 21 copy: wait 30 after the punch, blast roll 2.5 %)")
    put(rows_at, row_bytes, "trial AI rows 21'-28'")
    ai_id = (rows_at - AI_TABLE) // AI_ROW
    type_at = _alloc_on_stride(alloc, ENEMY_ENTRY, ENEMY_TABLE, ENEMY_ENTRY)
    put(type_at, group_type(ai_id), "trial type entry (type 26, HP 1550, trial AI)")
    type_id = (type_at - ENEMY_TABLE) // ENEMY_ENTRY
    for n, item in zip(FIGHT_ITEMS, items):
        if n in GROUP_ITEMS:
            put(item + 8, _word(type_id), f"item {n} type word (trial type)")

    alloc.notes["celljr_fight"] = {"seq31": seq31, "fight": fight, "counter": count, "restore": rest,
                                   "finish": fin, "one_v_one_end": k1, "table": table, "table1": table1,
                                   "relays": relays, "items": items, "cell_npc": cell, "cell_step": step,
                                   "seq58": seq58, "spawns": spawns, "ai_nodes": nodes_at, "ai_rows": rows_at,
                                   "ai_id": ai_id, "type_entry": type_at, "type_id": type_id,
                                   "sites": sorted(sites)}
