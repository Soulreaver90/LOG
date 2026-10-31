r"""
test_celljr_fight.py - Tests for patches.celljr_fight (trial 2026-10-24): 7 Cell Jrs spawn, Gohan fights them.
                       v2 (my play test): Cell faces Gohan in the Jr fight, the Jrs come down from the top, and
                       Gohan faces Super Perfect Cell during Goku's telepathy lines. v3 (my play test): the
                       NPC Cell stands where the type 24 Cell stood. v4 (my screenshot): the 2 Jrs that v2
                       put in front and v3 put at the right edge stand in my two circles. v5: trial AI.
                       v6 (final, 2026-10-30): relay Jrs end like a boss (bar at 1/4, sound 60, flash, gone in the
                       fade); a 1 v 1 Jr (type 26, bar), a 1 v 3 group (HP 1550, no bar), a scripted finish.
                       v7 (my v6 play test): the K1 and F Jrs walk in from the view edges and surround Gohan in
                       the arena middle; N puts the "You wretched child" pair back in the vanilla layout.
                       v8 (my v7 play test): in F Gohan teleports north of the last Jr with Goku's own teleport
                       effect and punches south, instead of flying at it.
                       v9 (my v8 play test): the Jrs walk in, so no record plays the flying sound (ext 46 (26)).
                       v10 (my v9 play test): X, K1 and F set NPC Cell's facing, because his face-the-player
                       step does not run while a scene plays.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_celljr_fight.py -v
Builds build_list_trial.txt in memory: "before" = the list up to celljr_fight (the main list, r40), "rom" = with it.
Scripts are decoded with test_cellgames_ssj's decoder (ops) and run in a small stack model here. Expected values
are restated from docs\tasks\2026-10-24-celljr-trial\celljr-trial*.md (final decisions v1-v5),
docs\tasks\2026-10-30-celljr-rework\celljr-rework.md (v6), the plan docs\tasks\2026-10-30-celljr-rework-plan\
plan-report.md, the study celljr-fight-study-report.md and the r40 bytes, never imported from the patch module.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
from patches import celljr_fight
from tests.test_cellgames_ssj import diff, ops, u32, words_naming
from rom.webfoot_decompress import ROM_BASE

# ===== constants (brief, study, r39 and r40 reads) =====
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial.txt"
MAP_14_3 = 0x40DA80
COUNT_AT, LIST_WORD, OLD_LIST = 0x40DA84, 0x40DA94, 0x409118
ITEM8, ITEM9, ITEM10 = 0x409038, 0x409068, 0x409098
SPAWN_TABLE, SEQ27, SEQ31 = 0x3E9D4C, 0x3E9C50, 0x3E9CF0
SEQ31_WORD = 0x3E9DC4                                  # spawn table word 30
GOHAN_TABLE, FIGHT_WORD = 0x3EA400, 0x3EA478           # word 30
WRETCHED, SEQ32 = 0x3EA3B4, 0x3EA3EC
EVENT_RUNNER = 0x080106B3
JR_TYPE, JR_SET, CELL_SET = 26, 31, 30
VAR1 = 1                                               # decision 6
EXP_TOTAL = 50000                                      # decision 4; v6: 12,500 a Gohan Jr
VANILLA_JRS = [(408, 392), (432, 376), (456, 392)]
GOHAN_AT = (576, 376)                                   # Gohan's seq 1 reload spot (ext 39 (14, 3, 1, 576, 376))
# v2 sources (r39 reads, listings in celljr-trial-v2-report.md)
NPC_FACTORY, FACE_STEP = 0x0800D6DF, 0x08010099        # npc_factory; step that faces the player every frame
SPECTATORS = (1, 2, 3, 4, 6, 7)                         # 14,3 NPC items that use FACE_STEP in vanilla
PICCOLO_STEP = 0x408F98                                 # item 4's step struct {FACE_STEP, 0x7D00}
CELL_NPC_ITEM, NEW_COUNT = 17, 18
SET_TABLE_POOL = 0x959C                                 # set header table; anim count at header +2
SPC_TABLE = 0x3EB704                                    # type 24 Cell's death event (self-destruct, Super Perfect)
SEQ52, SEQ58, SEQ65 = 0x3EB21C, 0x3EB4C4, 0x3EB6E8      # words 51, 57, 64
SEQ58_WORD = SPC_TABLE + 4 * 57                         # rom:0x3EB7E8
ITEM12 = 0x4090F8                                       # Super Perfect Cell enemy item
SPC_GOHAN_AT = (432, 472)                               # seq 52 ext 62 (0, 432, 472)
# v3 sources (v1 states ss1, ss2; scripts\one-time\2026-10-24-celljr-trial\state_actors_v3.py, sprite_boxes_v3.py)
ITEM0, ITEM11 = 0x408F18, 0x4090C8                      # type 22 Cell (spawn scene), type 24 Cell (Gohan's table)
CELL_STANDS = (512, 472)                                # type 24 Cell at Gohan seq 24 (ss2: +0x158 0x20000, 0x1D800)
SPAWN_GOHAN_AT = (400, 440)                             # spawn table seq 1 ext 39 (ss1: player 0x19000, 0x1B800)
SEQ24 = 0x3E9BEC                                        # spawn table word 23: camera ext 31 (328, 312, 2)
VIEW_W, VIEW_H = 240, 160
JR_BOX, CELL_BOX = (1, 15, -15, 7), (-2, 26, -50, 7)    # opaque x0, x1, y0, y1 from (x, y): set 31, set 30, anim 0
GOHAN_BOX = (0, 15, -24, 7)                             # the player's 16x32 frame (ss1 OAM: x + 0, y - 24)
V2_FRONT_JRS = [(408, 424), (456, 424)]                 # the pair I saw in front of Gohan and Cell
# v4 sources (owner-jr-spots-2026-10-25.png; scripts\one-time\2026-10-24-celljr-trial\screen_map_v4.py, study_v4.txt)
V3_EDGE_JRS = [(536, 384), (544, 416)]                  # v3 spots, "awkwardly outside to the side"
CIRCLES = [(396, 362, (376, 416, 332, 381)),            # circle centre (inside centroid), pen stroke x0, x1, y0, y1
           (484, 366, (465, 502, 343, 383))]            # (the right inside is 22 px tall, a Jr box 23)
ALLIES = [(296, 104), (256, 112), (520, 104), (448, 112), (552, 96)]   # cj3 ss1 world list (+0x158/+0x15C)
ALLY_BOX = (-8, 23, -40, 7)                             # generous: a 32x48 body around any ally
POSITION_OPS = (51, 53, 54, 62)                         # ext ops that put an actor at (x, y) (bible PGS rows)
# v5 sources (celljr-trial-v5.md; CJB rows, scripts\one-time\2026-10-25-celljr-balance\ai_tree.txt, ai_copy_plan.txt;
# scripts\one-time\2026-10-24-celljr-trial\study_v5.txt)
AI_TABLE, ENEMY_TABLE = 0x6D5194, 0x6D56AC              # 8 bytes a row {main, hit list}; 24 bytes a type
TYPE26_AT = ENEMY_TABLE + 24 * JR_TYPE
TYPE26 = bytes.fromhex("00000000" "7e130000" "15000000" "2e322e" "8080" "000000" "54566d08")   # HP 4990, AI 21
NODE_BLOCK = (0x6D0000, AI_TABLE)
AI21_ROWS = range(21, 29)
COPIED, COPIED_BYTES = 39, 844                          # ai_copy_plan.txt; row 26' adds one 4-byte child
SHARED_IN_BLOCK = {0x086D2040, 0x086D23A0, 0x086D2404, 0x086D2498, 0x086D24D8, 0x086D255C, 0x086D25BC,
                   0x086D2648, 0x086D2658, 0x086D26E0}  # reached from rows 21-28, no row id below them
ROLL_NODE, ROLL_BEFORE, ROLL_AFTER = 0x6D23D8, 0x0CCC, 0x0666   # row 22 RANDOM p (rand16 @0x0802142E: p / 65536)
PUNCH_LEAF, WAIT_NODE = 0x086D25BC, 0x086D1FC4          # {0x0801BE8B,..,3}; {0x0801BBAD, 0, 0, 0x1E}
PUNCH_F, WAIT_F = 0x0801BE8B, 0x0801BBAD
SHARED_HIT = 0x086FF4C4                                 # rows 22-28 hit list: dispatches through type +8
SHAPES = {0x0801AEF3: "DIST", 0x0801D749: "DIST", 0x0801BA47: "RANDOM", 0x0801B63F: "SEQ", 0x0801B887: "OR",
          0x0801B861: "COMP", 0x0801C05B: "GUARD", 0x0801AB65: "PUSH", 0x0801B511: "JUMP"}
LEAF_FS = {0x0801B333, 0x0801B15F, 0x0801C431, 0x0801C2AD, WAIT_F, PUNCH_F}
HIT_PATH_IDS = {16, 17, 19, 20}                         # row ids a walk from rows 16-20 reaches (study_v5.txt)
CODE_PINS = ((0xE302, "28688168381c0cf0c6fb"),           # ctor: ldr r0,[r5] (type entry) ; ldr r1,[r0,#8] ; bl AI
             (0x1AAA2, "c8002949"),                     # AI start: lsl r0,r1,#3 ; ldr r1,=table (u32 id)
             (0x1B512, "c068084ac000"),                 # JUMP: ldr r0,[r0,#0xc] ; ldr r2,=table ; lsl r0,#3
             (0x1C456, "40580a4a8068c000"),              # hit singleton: [enemy +0x180] +8, x 8 (main)
             (0x1C470, "4058044b8068c000c0184068"),      # and the hit list: [table + 8 x id + 4]
             (0x2142E, "10b5041cfff7e3ff0004000ca04201d2"),   # rand16: (rand & 0xFFFF) < p
             (0x1BB94, "4168002901d1012070470139416001d10120704700207047"))   # wait: n ticks, done at 0
# v6 sources (celljr-rework.md final decisions; plan-report.md Q1-Q7; CJP rows; r40 reads, s3_relay_bytes.py)
TYPE26_DESC_AT, NORMAL_DESC, BOSS_DESC = TYPE26_AT + 0x14, 0x086D5654, 0x086FF3C4   # rom:0x6D5930
RELAY_RECS = {0x3E9E24: 0x3E9DCC, 0x3E9E84: 0x3E9E2C, GOHAN_TABLE: 0x89A71C}   # relay table -> r40 word 0 record
BAR_TABLES = (0x3E9E24, 0x3E9E84)                       # their records start the next relay fight
ONE, GROUP = 13, (14, 15, 16)
GROUP_HP, EXP_EACH = 1550, 12500
DING, BOOM, QUARTER = 60, 31, (JR_SET, 25, 100)          # boss end sound; the poof's sound; bar slice ending at 1/4
FINISH_AT = 28
GOHAN_RAGE, FLY_DONOR, FLY_ROW = 160, 159, 12            # set 160 borrows set 159's fly row (VS5)
MAPS, MAP_COUNT, MAP_SIZE, ENEMY_FACTORY = 0x409368, 327, 56, 0x0800E77F
FIGHT_VIEW = (456, 288)                                 # X's ext 31 view (v2)
# v7 sources (celljr-v7.md my words; scripts\one-time\2026-10-30-celljr-rework\v7_spots.txt, v7_camera_study.py)
MIDDLE = (432, 392)                                     # the clear spot nearest the map centre (432,408)
MIDDLE_VIEW = (MIDDLE[0] - 112, MIDDLE[1] - 80)         # follow target: footprint centre (x+8, y+4) - (120, 84)
MAP_W, MAP_H = 864, 816                                 # camera clamp 624 x 656 + the 240 x 160 view (ss1 state)
ARENA = ((297, 583, 377, 399), (432, 503, 273, 399))    # all-open bands of the ss2 collision bitmap (0 closed px)
FINISH_A, FINISH_B, FINISH_C = (456, 392), (384, 392), (456, 368)   # punched (right), blasted (left), teleported to
# v8 sources (celljr-v8.md my words; Goku's teleport out of the arena; scripts\one-time\2026-10-30-celljr-v8)
GOKU_TP_AT = 0x3E5E6A                                   # table rom:0x3E6078 word 83, before "#Instant transmission"
TP_FLASH, TP_HOLD = 10, 60                              # its push 10 ; ext 42 pair and its push 60 ; ext 69 hold
GOHAN_TELEPORTS_TO = (456, 344)                         # north of C; his 16 x 32 frame stays in the view (v8_spots)
TELE_KNOCK_SPOT = (456, 392)                            # C is knocked 24 px south, away from the punch
V6_N_CELL = (616, 384)                                  # v1-v6 N spot (the CJR misread of seq 19)
SEQ11, SEQ24_GOHAN = 0x3EA040, 0x3EA30C                 # Gohan table words 11 and 24 (camera; Gohan faces down)
# v9 sources (celljr-v9.md my words: there is no flying sprite, so the walk-ins keep no flying sound)
FLY_SOUND = 26                                          # the vanilla sound 26 that v8 played before each walk-in
# v10 sources (celljr-v10.md my words; bible CJ2 facing row; the vanilla ext 55 sites of rows VSJ and CJ8)
FACE_DOWN, FACE_UP, FACE_LEFT, FACE_RIGHT = 0, 1, 2, 3  # ext 55 direction values
CELL_FACES = {"fight": FACE_UP, "one_v_one_end": FACE_LEFT, "finish": FACE_LEFT, "restore": FACE_RIGHT}
CELL_ITEM = 11                                          # the type 24 Cell enemy item that N builds again
VEGETA_NPC_ITEM, VEGETA_SET = 0x408F40, 137             # map 14,3 item 1: the NPC that base seq 50 turns by set
SEQ50, SEQ50_TURN = 0x3EB134, 0x3EB141                  # table rom:0x3EB704 word 49: ext 55 (137, 3) on that NPC
TURN_VEGETA = bytes.fromhex("1d028212060237")           # push 137,3 ; ext 55, the vanilla bytes at SEQ50_TURN
STEP_RULE_AT = 0x1006A                                  # the step tick's compare and its 4 facing branches
STEP_RULE = bytes.fromhex("ac4207db002a02dd03220a7409e002220a7406e0002b02dd00220a7401e001220a74")
# Ext arity (handlers pop; bible PGS row, CJR study listings): ext 1 reads var 1 and pushes it
ARITY = {1: 0, 24: 1, 29: 1, 30: 1, 31: 3, 33: 1, 39: 5, 40: 1, 41: 1, 42: 1, 43: 1, 46: 1, 49: 1, 51: 3, 52: 1, 53: 3,
         54: 3, 55: 2, 56: 2, 57: 2, 60: 1, 62: 3, 63: 0, 64: 0, 69: 1, 70: 1, 73: 2, 84: 1, 85: 1, 86: 1, 88: 0,
         90: 3, 94: 3, 95: 1, 96: 3, 110: 2, 112: 2, 119: 0, 121: 2, 136: 4, 139: 1}
GETTERS = {0, 1, 2, 3}

R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"        # build_list.txt r40 (2026-10-30; r39 was aa51dc16)
R40_MODULES = ("relay_cooldown", "fullpower_hud", "beam_struggle", "vegeta_ssj_scene")
_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("celljr_fight")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["celljr_fight"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["celljr_fight"])
    return _CACHE


def calls(rom: bytes, rec: int) -> tuple:
    """Stack model of a constant type 0 record (no branches): ([(ext n, args)], values left at the first end)."""
    st, out = [], []
    for _, op, arg in ops(rom, rec + 3):
        if op in (0, 1, 29):
            st += arg
        elif op == 3:
            st.pop()
        elif op == 2:
            k = ARITY[arg]
            out.append((arg, tuple(st[len(st) - k:])))
            del st[len(st) - k:]
            if arg in GETTERS:
                st.append("var")
        elif op == 17:
            return out, st
        else:
            raise AssertionError(f"op {op} is not modelled")


def run_counter(rom: bytes, rec: int, var1: int) -> tuple:
    """Run record C with var 1: (next index, new var 1, [EXP given])."""
    body = ops(rom, rec + 3)
    at = {o: k for k, (o, _, _) in enumerate(body)}
    k, st, exp = 0, [], []
    while True:
        _, op, arg = body[k]
        k += 1
        if op in (0, 1, 29):
            st += arg
        elif op == 21:
            assert arg == VAR1
            var1 += 1
        elif op == 2 and arg == VAR1:
            st.append(var1)
        elif op == 2 and arg == 139:
            exp.append(st.pop())
        elif op == 15:
            b, a = st.pop(), st.pop()
            st.append(int(a < b))
        elif op == 19:
            if not st.pop():
                k = at[arg]
        elif op == 17:
            assert len(st) == 1, st                    # one value left = the next index (SS3)
            return st[0], var1, exp
        else:
            raise AssertionError(f"op {op} ext {arg} is not modelled")


def record(rom: bytes, table: int, k: int) -> int:
    return u32(rom, table + 4 * k) - ROM_BASE


def set_head(rom: bytes, set_id: int) -> int:
    return u32(rom, u32(rom, SET_TABLE_POOL) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE


def anim_count(rom: bytes, set_id: int) -> int:
    return rom[set_head(rom, set_id) + 2]


def fly_row(rom: bytes, set_id: int) -> bytes:
    at = set_head(rom, set_id) + 0x4C + 16 * FLY_ROW
    return rom[at:at + 16]


def spawn_item(rom: bytes, n: int) -> int:
    return u32(rom, u32(rom, LIST_WORD) - ROM_BASE + 4 * n) - ROM_BASE


def type_26_items(rom: bytes, by_factory: bool) -> list:
    """(map entry, item) of the spawn items of type 26: shape A = enemy factory and type word; shape B = any item
    whose +8 word is 26 and +0x10 word (set) is 31."""
    out = []
    for m in range(MAP_COUNT):
        entry = MAPS + MAP_SIZE * m
        lst = u32(rom, entry + 0x14) - ROM_BASE
        for k in range(rom[entry + 4] if 0 <= lst < len(rom) else 0):
            item = u32(rom, lst + 4 * k) - ROM_BASE
            if not 0 <= item < len(rom) - 0x14 or u32(rom, item + 8) != JR_TYPE:
                continue
            if (u32(rom, item) == ENEMY_FACTORY) if by_factory else (u32(rom, item + 0x10) == JR_SET):
                out.append((m, k))
    return out


def placed(rom: bytes, rec: int) -> list:
    """[(ext n, args)] of the POSITION_OPS and ext 52 calls in a type 0 record. Each ext is taken to pop all that
    was pushed since the last ext, which holds for the plain push-then-ext records read here."""
    st, out = [], []
    for _, op, arg in ops(rom, rec + 3):
        if op in (0, 1, 29):
            st += arg
        elif op == 3 and st:
            st.pop()
        elif op == 2:
            if arg in POSITION_OPS + (52,):
                out.append((arg, tuple(st[-1:] if arg == 52 else st[-3:])))
            st = []
        elif op == 17:
            break
    return out


def kids(rom: bytes, a: int) -> list:
    """Child node addresses of the AI node at GBA address a (restated node shapes, CJH/CJB rows)."""
    o = a - ROM_BASE
    shape = SHAPES.get(u32(rom, o))
    if shape == "DIST":
        return [u32(rom, o + 16), u32(rom, o + 20)]
    if shape == "RANDOM":
        return [u32(rom, o + 16)]
    if shape in ("SEQ", "OR", "COMP"):
        return [u32(rom, o + 16 + 4 * i) for i in range(u32(rom, o + 12))]
    if shape == "GUARD":
        return [u32(rom, o + 12)]
    return []


def walk(rom: bytes, first_row: int) -> dict:
    """{GBA address: factory} of every node reached from 8 rows from first_row (main and hit lists); nodes outside
    the node block and the ROM expansion (the 0x086FFxxx singletons) are listed but not opened."""
    seen, todo = {}, [u32(rom, AI_TABLE + 8 * r + k) for r in range(first_row, first_row + 8) for k in (0, 4)]
    while todo:
        a = todo.pop()
        if a in seen:
            continue
        seen[a] = u32(rom, a - ROM_BASE)
        inside = NODE_BLOCK[0] <= a - ROM_BASE < NODE_BLOCK[1] or a - ROM_BASE >= 0x800000
        if inside:
            todo += kids(rom, a)
    return seen


def box(spot: tuple, shape: tuple) -> tuple:
    (x, y), (x0, x1, y0, y1) = spot, shape
    return x + x0, x + x1, y + y0, y + y1


def overlap(a: tuple, b: tuple) -> bool:
    return a[0] <= b[1] and b[0] <= a[1] and a[2] <= b[3] and b[2] <= a[3]


def in_view(b: tuple, view: tuple) -> bool:
    return view[0] <= b[0] and b[1] < view[0] + VIEW_W and view[1] <= b[2] and b[3] < view[1] + VIEW_H


def swept(a: tuple, b: tuple, shape: tuple) -> tuple:
    """The box of shape moved in a straight line from spot a to spot b."""
    ba, bb = box(a, shape), box(b, shape)
    return min(ba[0], bb[0]), max(ba[1], bb[1]), min(ba[2], bb[2]), max(ba[3], bb[3])


def in_arena(b: tuple) -> bool:
    return any(r[0] <= b[0] and b[1] <= r[1] and r[2] <= b[2] and b[3] <= r[3] for r in ARENA)


def pair_centre(camera: tuple, gohan: tuple, cell: tuple) -> tuple:
    """Screen centre of the union of Gohan's and Cell's opaque boxes."""
    g, c = box(gohan, GOHAN_BOX), box(cell, CELL_BOX)
    return ((min(g[0], c[0]) + max(g[1], c[1])) / 2 - camera[0], (min(g[2], c[2]) + max(g[3], c[3])) / 2 - camera[1])


def walk_ins(got: list) -> list:
    """[(start, end)] of the set 31 spawns, each followed by its own walk (ext 51 then ext 53)."""
    return [(a[1:], got[k + 1][1][1:]) for k, (n, a) in enumerate(got) if n == 51 and a[0] == JR_SET]


def view_of(got: list) -> tuple:
    views = [a[:2] for n, a in got if n == 31]
    assert len(views) == 1, views
    return views[0]


def new_records(notes: dict) -> dict:
    recs = {k: notes[k] for k in ("seq31", "fight", "one_v_one_end", "finish", "restore", "seq58")}
    recs.update({f"relay {t:#x}": a for t, a in notes["relays"].items()})
    return recs


def bind_set_31(got: list) -> list:
    """[(ext n, args, bound Jr)] for the set 31 calls: each binds the newest live Jr (find by set, @0x08006E0A).
    A Jr is named by the spot its walk (ext 53) ends on; ext 96 binds through its target argument."""
    live, out = [], []
    for n, a in got:
        if n == 51 and a[0] == JR_SET:
            live.append(None)
        elif n == 53 and a[0] == JR_SET:
            live[-1] = a[1:]
        if (a[:1] == (JR_SET,) or (n == 96 and a[1] == JR_SET)) and n != 51:
            out.append((n, a, live[-1]))
        if n == 52 and a == (JR_SET,):
            live.pop()
    return out


# ===== tests =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "celljr_fight" in dev:
            self.skipTest("approved: the trial line is in build_list_core.txt, so build_list_trial.txt is retired")
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["celljr_fight"])

    def test_before_is_r40(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R40_SHA1)

    def test_no_write_inside_an_r40_module_site(self):
        """celljr_fight checks no other module's sites, and from r40 it runs after vegeta_ssj_scene."""
        b = built()
        notes = b["alloc_before"].notes
        sites = [(s[0], s[1], m) for m in R40_MODULES for s in notes[m]["sites"]]
        self.assertEqual([(hex(s), m) for s, n, m in sites if b["rom"][s:s + n] != b["before"][s:s + n]], [])

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["celljr_fight"] = {}
        with self.assertRaises(ValueError):
            celljr_fight.apply(rom, alloc)

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        for off in (WRETCHED + 6, SEQ31 + 30, ITEM8 + 8, COUNT_AT, SEQ27 + 10, SEQ58 + 6, PICCOLO_STEP, SEQ65 + 6,
                    GOKU_TP_AT + 4,
                    ITEM0 + 0xC, ITEM11 + 0xE, 0x3E9DCC + 0x20, 0x3E9E2C + 0x37, 0x89A71C + 0x26, TYPE26_DESC_AT,
                    BOSS_DESC - ROM_BASE + 4):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                celljr_fight.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_it_refuses_before_the_main_list_is_done(self):
        """This module runs after the whole main list, so no earlier allocation moves. v8: the fly row is no
        longer a source, so the module names the two main modules it needs in its notes instead."""
        b = built()
        for module in ("superperfect_cell", "vegeta_ssj_scene"):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            self.assertIn(module, alloc.notes)
            del alloc.notes[module]
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=module):
                celljr_fight.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_the_finish_needs_no_fly_row(self):
        """v8 replaces v6's fly with a teleport, so set 160 row 12 is no longer a source: the module builds with
        that row zeroed. It still writes no byte of it (vegeta_ssj_scene owns it in the main list)."""
        b = built()
        rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
        at = set_head(rom, GOHAN_RAGE) + 0x4C + 16 * FLY_ROW
        rom[at:at + 16] = bytes(16)
        celljr_fight.apply(rom, alloc)
        self.assertEqual(bytes(rom[at:at + 16]), bytes(16))
        self.assertEqual(fly_row(b["rom"], GOHAN_RAGE), fly_row(b["before"], GOHAN_RAGE))


class BaseSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_the_nine_base_sites_old_and_new(self):
        n = self.notes
        self.assertEqual(self.before[COUNT_AT], 13)
        self.assertEqual(self.rom[COUNT_AT], NEW_COUNT)
        self.assertEqual(u32(self.before, SEQ58_WORD), SEQ58 + ROM_BASE)
        self.assertEqual(u32(self.rom, SEQ58_WORD), n["seq58"] + ROM_BASE)
        self.assertEqual(u32(self.before, LIST_WORD), OLD_LIST + ROM_BASE)
        self.assertEqual(u32(self.rom, LIST_WORD), n["spawns"] + ROM_BASE)
        self.assertEqual(u32(self.before, SEQ31_WORD), SEQ31 + ROM_BASE)
        self.assertEqual(u32(self.rom, SEQ31_WORD), n["seq31"] + ROM_BASE)
        self.assertEqual(u32(self.before, FIGHT_WORD), WRETCHED + ROM_BASE)
        self.assertEqual(u32(self.rom, FIGHT_WORD), n["fight"] + ROM_BASE)
        for table, rec in RELAY_RECS.items():
            self.assertEqual(u32(self.before, table), rec + ROM_BASE)
            self.assertEqual(u32(self.rom, table), n["relays"][table] + ROM_BASE)
        self.assertEqual(u32(self.before, TYPE26_DESC_AT), NORMAL_DESC)
        self.assertEqual(u32(self.rom, TYPE26_DESC_AT), BOSS_DESC)

    def test_every_changed_byte_is_inside_a_named_site(self):
        sites = self.notes["sites"]
        changed = diff(self.before, self.rom)
        self.assertTrue(changed)
        outside = [i for i in changed if not any(s <= i < s + n for s, n, _ in sites)]
        self.assertEqual(outside, [])
        idle = [name for s, n, name in sites if not any(s <= i < s + n for i in changed)]
        self.assertEqual(idle, [])

    def test_base_data_changes_only_at_the_nine_sites(self):
        base = sorted({i for i in diff(self.before, self.rom) if i < 0x800000})
        words = (SEQ31_WORD, FIGHT_WORD, LIST_WORD, SEQ58_WORD, TYPE26_DESC_AT) + tuple(RELAY_RECS)
        want = {i for w in words for i in range(w, w + 4)} | {COUNT_AT}
        self.assertTrue(set(base) <= want, base)

    def test_superseded_targets_have_no_other_name(self):
        for gone in (SEQ31, OLD_LIST, SEQ58) + tuple(RELAY_RECS.values()):
            self.assertEqual(words_naming(self.rom, gone + ROM_BASE), [], hex(gone))
        self.assertEqual(words_naming(self.rom, WRETCHED + ROM_BASE), [self.notes["table"] + 4 * 30])

    def test_relay_records_and_items_keep_their_bytes(self):
        for table, rec in RELAY_RECS.items():
            self.assertEqual(self.rom[rec:rec + 0x50], self.before[rec:rec + 0x50])
            self.assertEqual(self.rom[table + 4:table + 8], self.before[table + 4:table + 8])
        for item in (ITEM8, ITEM9, ITEM10):
            self.assertEqual(self.rom[item - 0x10:item + 0x20], self.before[item - 0x10:item + 0x20])

    def test_word_data_is_4_aligned(self):
        n = self.notes
        for off in [n["table"], n["table1"], n["spawns"], n["cell_npc"], n["cell_step"]] + n["items"]:
            self.assertEqual(off % 4, 0)


class SpawnSceneTests(unittest.TestCase):
    """Decision 2: 3 Jrs, the two lines, then 4 more; all 7 gone in the ally fights."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.seq27, _ = calls(cls.rom, SEQ27)
        cls.copy, cls.left = calls(cls.rom, cls.notes["seq31"])
        cls.vanilla31, _ = calls(cls.before, SEQ31)

    def test_seq_27_is_vanilla_with_3_jrs(self):
        self.assertEqual(record(self.rom, SPAWN_TABLE, 26), SEQ27)
        self.assertEqual(self.rom[SEQ27:SEQ27 + 0x50], self.before[SEQ27:SEQ27 + 0x50])
        self.assertEqual([a[1:] for n, a in self.seq27 if n == 51], VANILLA_JRS)

    def test_copy_spawns_4_more_before_the_fade(self):
        spawns = [a for n, a in self.copy if n == 51]
        self.assertEqual(len(spawns), 4)
        self.assertTrue(all(a[0] == JR_SET for a in spawns))
        first_fade = [n for n, _ in self.copy].index(40)
        self.assertEqual(sum(1 for n, _ in self.copy[:first_fade] if n == 51), 4)
        pos = VANILLA_JRS + [a[1:] for a in spawns]
        self.assertEqual(len(set(pos)), 7)

    def test_spawned_jrs_equal_removed_jrs(self):
        spawned = sum(1 for n, a in self.seq27 + self.copy if n == 51 and a[0] == JR_SET)
        removed = sum(1 for n, a in self.copy if n == 52 and a == (JR_SET,))
        self.assertEqual((spawned, removed), (7, 7))

    def test_copy_is_vanilla_seq_31_after_the_spawns_but_the_bar(self):
        tail = self.copy[[n for n, _ in self.copy].index(40):]
        drop_extra = [(85, (JR_SET,)) if c == (90, QUARTER) else c for c in tail]
        for _ in range(4):
            drop_extra.remove((52, (JR_SET,)))
        self.assertEqual(drop_extra, self.vanilla31)
        self.assertEqual(self.left, [])
        self.assertEqual(self.rom[self.notes["seq31"]], 31)          # next index as vanilla seq 31
        self.assertEqual(u32(self.rom, SPAWN_TABLE + 4 * 31), 0)     # then END: the Piccolo fight runs


class RelayEndTests(unittest.TestCase):
    """v6: the relay Jrs end like a boss: bar at 1/4, sound 60, flash, then the fade, and the Jr is gone after it."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.copies = {t: calls(cls.rom, a) for t, a in cls.notes["relays"].items()}

    def test_type_26_uses_the_boss_descriptor_and_only_jr_items_name_it(self):
        self.assertEqual(u32(self.rom, TYPE26_DESC_AT), BOSS_DESC)
        vanilla = [(325, 8), (325, 9), (325, 10)]
        for by_factory in (True, False):                               # two shapes agree
            self.assertEqual(type_26_items(self.before, by_factory), vanilla)
            self.assertEqual(type_26_items(self.rom, by_factory), vanilla + [(325, ONE)])

    def test_relay_ends_start_with_sound_60_and_a_flash(self):
        for t, (got, left) in self.copies.items():
            self.assertEqual(got[:4], [(46, (DING,)), (42, (10,)), (43, (10,)), (69, (40,))], hex(t))
            self.assertEqual(left, [])

    def test_relay_bars_end_at_a_quarter(self):
        got, _ = calls(self.rom, self.notes["seq31"])
        self.assertIn((90, QUARTER), got)
        self.assertNotIn((85, (JR_SET,)), got)
        for t, (got, _) in self.copies.items():
            self.assertNotIn((85, (JR_SET,)), got, hex(t))
            self.assertEqual((90, QUARTER) in got, t in BAR_TABLES, hex(t))

    def test_the_beaten_jr_goes_in_the_fade_with_no_stand_in(self):
        for t, (got, _) in self.copies.items():
            k = got.index((40, (120,)))
            self.assertEqual(got[k + 1], (52, (JR_SET,)), hex(t))
            self.assertEqual([c for c in got if c == (52, (JR_SET,))], [(52, (JR_SET,))])
            self.assertFalse([a for n, a in got if n == 51 and a[0] == JR_SET], hex(t))
            builds = [k2 for k2, c in enumerate(got) if c[0] == 84 or c[0] == 39]
            self.assertLess(k + 1, min(builds), hex(t))                # gone before the next Jr or the reload

    def test_relay_copies_are_the_r40_records_plus_the_changes(self):
        for t, rec in RELAY_RECS.items():
            got, _ = self.copies[t]
            body = [(85, (JR_SET,)) if c == (90, QUARTER) else c for c in got[4:]]
            body.remove((52, (JR_SET,)))
            self.assertEqual(body, calls(self.before, rec)[0], hex(t))
            self.assertEqual(self.rom[self.notes["relays"][t]], self.before[rec])   # same next index


class SpawnListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.spawns = cls.notes["spawns"]

    def test_list_is_the_old_13_plus_4_jrs_and_the_npc_cell(self):
        self.assertEqual(self.rom[self.spawns:self.spawns + 52], self.before[OLD_LIST:OLD_LIST + 52])
        self.assertEqual([u32(self.rom, self.spawns + 4 * k) - ROM_BASE for k in range(13, 17)], self.notes["items"])
        self.assertEqual(u32(self.rom, self.spawns + 4 * CELL_NPC_ITEM) - ROM_BASE, self.notes["cell_npc"])
        self.assertEqual(self.rom[OLD_LIST:OLD_LIST + 52], self.before[OLD_LIST:OLD_LIST + 52])

    def test_new_items_are_item_8_with_own_place_tail_type_and_event(self):
        ref = self.before[ITEM8:ITEM8 + 0x20]
        self.assertEqual(u32(ref, 8), JR_TYPE)
        for n, item in zip((ONE,) + GROUP, self.notes["items"]):
            new = self.rom[item:item + 0x20]
            factory, cond, typ, x, y, set_id, event, one, tail = struct.unpack("<3I2h4I", new)
            self.assertEqual((factory, cond, set_id, one), struct.unpack("<2I", ref[:8]) + (JR_SET, 1))
            self.assertEqual(new[:0x8] + new[0x10:0x14] + new[0x18:0x1C], ref[:0x8] + ref[0x10:0x14] + ref[0x18:0x1C])
            want = (JR_TYPE, self.notes["table1"]) if n == ONE else (self.notes["type_id"], self.notes["table"])
            self.assertEqual((typ, cond), (want[0], 1), n)            # cond 1: seq 1's map reload does not build them
            self.assertEqual(struct.unpack("<2I", self.rom[event - ROM_BASE:event - ROM_BASE + 8]),
                             (EVENT_RUNNER, want[1] + ROM_BASE), n)
            self.assertEqual(self.rom[tail - ROM_BASE:tail - ROM_BASE + 8], self.before[ITEM8 - 0x10:ITEM8 - 8])

    def test_fight_positions_are_distinct_and_clear_of_cell_and_gohan(self):
        pos = [struct.unpack_from("<hh", self.rom, i + 0xC) for i in self.notes["items"]]
        self.assertEqual(len(set(pos)), 4)
        for spot in (V6_N_CELL, CELL_STANDS, GOHAN_AT, MIDDLE):
            self.assertNotIn(spot, pos)
        for spot in pos:                                               # v7: boxes, not only spots
            self.assertFalse(overlap(box(spot, JR_BOX), box(CELL_STANDS, CELL_BOX)), spot)
        for spot in pos[1:]:                                           # the group stands around Gohan in the middle
            self.assertFalse(overlap(box(spot, JR_BOX), box(MIDDLE, GOHAN_BOX)), spot)


class FightTests(unittest.TestCase):
    """v6: X starts the 1 v 1 with a bar, K1 ends it and starts the 1 v 3, C counts 3, F finishes, N restores."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.x, cls.x_left = calls(cls.rom, cls.notes["fight"])
        cls.k1, cls.k1_left = calls(cls.rom, cls.notes["one_v_one_end"])
        cls.n, cls.n_left = calls(cls.rom, cls.notes["restore"])

    def test_rage_line_goes_to_x_and_x_ends_the_scene(self):
        rage = record(self.rom, GOHAN_TABLE, 29)
        self.assertEqual(self.rom[rage], 30)
        self.assertEqual(self.rom[self.notes["fight"]], 32)
        self.assertEqual(u32(self.rom, GOHAN_TABLE + 4 * 32), 0)

    def test_x_swaps_cell_and_builds_the_1v1_jr_with_a_full_bar(self):
        self.assertEqual(self.x[:2], [(52, (CELL_SET,)), (84, (CELL_NPC_ITEM,))])
        self.assertEqual([a for n, a in self.x if n == 84], [(CELL_NPC_ITEM,), (ONE,)])
        self.assertEqual(self.x[-3:], [(33, (0,)), (86, (1,)), (85, (JR_SET,))])   # binds item 13, the only Jr
        self.assertEqual(self.x_left, [])

    def test_table_t1_runs_k1_once(self):
        t1 = self.notes["table1"]
        self.assertEqual(struct.unpack_from("<2I", self.rom, t1), (self.notes["one_v_one_end"] + ROM_BASE, 0))
        self.assertEqual(self.rom[self.notes["one_v_one_end"]], 1)

    def test_k1_ends_the_1v1_jr_with_an_explosion_not_a_ding(self):
        self.assertEqual(self.k1[:6], [(88, ()), (94, (JR_SET, 0, 0)), (46, (BOOM,)), (42, (5,)), (52, (JR_SET,)),
                                       (43, (5,))])
        self.assertNotIn((46, (DING,)), self.k1)
        self.assertEqual([a for n, a in self.k1 if n == 139], [(EXP_EACH,)])
        self.assertEqual(self.k1_left, [])

    def test_k1_resets_var_1_and_builds_the_group_with_no_bar(self):
        body = [(op, arg) for _, op, arg in ops(self.rom, self.notes["one_v_one_end"] + 3)]
        k = body.index((3, VAR1))
        self.assertEqual(body[k - 1], (0, [0]))
        self.assertLess(k, body.index((2, 84)))
        self.assertEqual([a for n, a in self.k1 if n == 84], [(g,) for g in GROUP])
        self.assertFalse([n for n, _ in self.k1 if n in (85, 90)])

    def test_k1_puts_gohan_in_the_middle_under_a_view_on_him_behind_a_short_fade(self):
        """v7: after the explosion, a short fade; Gohan to the middle; the camera on him; fade in; then the Jrs.
        v10: Cell turns left in the same fade, between the fade out and the fade in."""
        k = self.k1.index((43, (5,)))                                  # the explosion's flash ends first
        self.assertEqual(self.k1[k + 1], (139, (EXP_EACH,)))
        self.assertEqual(self.k1[k + 2:k + 8], [(40, (30,)), (62, (0,) + MIDDLE), (55, (0, FACE_DOWN)),
                                                (55, (CELL_SET, FACE_LEFT)), (31, MIDDLE_VIEW + (255,)),
                                                (41, (30,))])
        self.assertLess(k + 7, [n for n, _ in self.k1].index(51))
        self.assertEqual(self.k1[-1], (33, (0,)))                      # follow again: no ease (same target)

    def test_the_middle_view_is_the_follow_target_inside_the_map(self):
        x, y = MIDDLE
        self.assertEqual(MIDDLE_VIEW, (x + 8 - 120, y + 4 - 84))      # footprint 16x8 centre - (120, 84)
        self.assertTrue(0 <= MIDDLE_VIEW[0] <= MAP_W - VIEW_W and 0 <= MIDDLE_VIEW[1] <= MAP_H - VIEW_H)
        self.assertTrue(in_arena(box(MIDDLE, GOHAN_BOX)))
        g = box(MIDDLE, GOHAN_BOX)                                     # Gohan near the view centre
        self.assertLessEqual(abs((g[0] + g[1]) / 2 - MIDDLE_VIEW[0] - VIEW_W / 2), 1)
        self.assertLessEqual(abs((g[2] + g[3]) / 2 - MIDDLE_VIEW[1] - VIEW_H / 2), 9)

    def test_table_t_layout(self):
        t = self.notes["table"]
        words = struct.unpack_from("<33I", self.rom, t)
        self.assertEqual(words[0], self.notes["counter"] + ROM_BASE)
        self.assertEqual(words[FINISH_AT], self.notes["finish"] + ROM_BASE)
        self.assertEqual(words[29], self.notes["restore"] + ROM_BASE)
        self.assertEqual(words[30:], (WRETCHED + ROM_BASE, SEQ32 + ROM_BASE, 0))
        self.assertEqual(set(words[1:FINISH_AT]), {0})
        self.assertEqual([self.rom[a] for a in (self.notes["finish"], self.notes["restore"], WRETCHED, SEQ32)],
                         [29, 30, 31, 32])

    def test_counter_ends_two_kills_and_finishes_on_the_third(self):
        c, var1, nxt, exp = self.notes["counter"], 0, [], []
        for _ in GROUP:
            k, var1, given = run_counter(self.rom, c, var1)
            nxt.append(k)
            exp += given
        self.assertEqual(nxt, [1, 1, FINISH_AT])
        self.assertEqual(var1, 3)
        self.assertEqual(exp, [EXP_EACH] * 3)
        self.assertEqual(EXP_EACH + sum(exp), EXP_TOTAL)               # K1 + the group

    def test_a_double_kill_still_reaches_the_finish_once(self):
        c = self.notes["counter"]
        k2, v, _ = run_counter(self.rom, c, 1)
        k3, v, _ = run_counter(self.rom, c, v)
        self.assertEqual((k2, k3, v), (1, FINISH_AT, 3))

    def test_n_fades_and_brings_cell_back(self):
        names = [n for n, _ in self.n]
        self.assertEqual(self.n[:3], [(88, ()), (86, (0,)), (40, (120,))])
        self.assertEqual(self.n[-1], (41, (120,)))
        self.assertLess(names.index(52), names.index(84))
        self.assertIn((84, (11,)), self.n)
        self.assertIn((62, (CELL_SET,) + CELL_STANDS), self.n)
        self.assertIn((62, (0,) + GOHAN_AT), self.n)
        self.assertEqual(self.n_left, [])

    def test_n_puts_the_pair_in_the_vanilla_wretched_child_layout(self):
        """v7: vanilla shows "You wretched child" with seq 11's camera, Cell on item 11's spot facing right (v1 ss2
        state) and Gohan at the seq 1 spot facing down (seq 24), and nothing moves them or the camera after."""
        seq11 = calls(self.before, SEQ11)[0]
        self.assertEqual([a for n, a in seq11 if n == 31], [(432, 336, 2)])
        for k in range(12, 30):                                        # no camera or Gohan move after seq 11
            rec = record(self.before, GOHAN_TABLE, k)
            if self.before[rec + 2] == 0:
                ids = [arg for _, op, arg in ops(self.before, rec + 3) if op == 2]
                self.assertFalse([n for n in ids if n in (31, 33, 119, 39)], k)
                self.assertFalse([c for c in placed(self.before, rec) if c[1][:1] in ((0,), (CELL_SET,))], k)
        self.assertEqual(calls(self.before, SEQ24_GOHAN)[0], [(55, (0, 0))])
        self.assertEqual(struct.unpack_from("<hh", self.before, ITEM11 + 0xC), CELL_STANDS)
        self.assertIn((31, (432, 336, 40)), self.n)
        self.assertEqual([a for n, a in self.n if n == 55], [(CELL_SET, 3), (0, 0)])
        self.assertLess(self.n.index((62, (0,) + GOHAN_AT)), self.n.index((31, (432, 336, 40))))

    def test_the_wretched_child_pair_is_centred_in_the_view(self):
        cam = [a[:2] for n, a in self.n if n == 31][0]
        cell = [a[1:] for n, a in self.n if n == 62 and a[0] == CELL_SET][0]
        gohan = [a[1:] for n, a in self.n if n == 62 and a[0] == 0][0]
        cx, cy = pair_centre(cam, gohan, cell)
        self.assertLessEqual(abs(cx - VIEW_W / 2), 4)
        self.assertLessEqual(abs(cy - VIEW_H / 2), 4)
        for b in (box(gohan, GOHAN_BOX), box(cell, CELL_BOX)):
            self.assertTrue(in_view(b, cam), b)

    def test_the_centring_check_rejects_the_v6_cell_spot(self):
        """My v6 screenshot: the pair near the top right (v6 N put Cell at (616,384))."""
        cx, cy = pair_centre((432, 336), GOHAN_AT, V6_N_CELL)
        self.assertGreater(cx - VIEW_W / 2, 40)
        self.assertLess(cy - VIEW_H / 2, -40)

    def test_wretched_line_and_cell_fight_are_the_vanilla_records(self):
        self.assertEqual(self.rom[WRETCHED + 4:WRETCHED + 25], b"You wretched child!!!")
        seq32, left = calls(self.rom, SEQ32)
        self.assertEqual(seq32, [(33, (0,)), (86, (1,)), (90, (30, 25, 100))])
        self.assertEqual(left, [])


class FinishTests(unittest.TestCase):
    """v6: 3 new Jrs walk down; Gohan punches one, blasts one and flies at the third; then N."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.f, cls.left = calls(cls.rom, cls.notes["finish"])
        cls.bound = bind_set_31(cls.f)

    def test_gohan_is_placed_behind_a_fade_before_the_jrs(self):
        fade_out, place = self.f.index((40, (30,))), self.f.index((62, (0,) + MIDDLE))
        fade_in, first_jr = self.f.index((41, (30,))), [n for n, _ in self.f].index(51)
        self.assertTrue(fade_out < place < fade_in < first_jr)
        self.assertIn((86, (0,)), self.f[:fade_out])
        self.assertEqual(self.left, [])

    def test_jrs_walk_in_c_b_a_and_end_a_b_c(self):
        spawned = [a for n, a, _ in self.bound if n == 53]
        self.assertEqual([a[1:] for a in spawned], [FINISH_C, FINISH_B, FINISH_A])
        self.assertEqual([j for n, a, j in self.bound if n == 52], [FINISH_A, FINISH_B, FINISH_C])
        view = view_of(self.f)
        whole = (view[0], view[0] + VIEW_W - 1, view[1], view[1] + VIEW_H - 1)
        for a, b in walk_ins(self.f):
            self.assertFalse(overlap(box(a, JR_BOX), whole), a)        # out of view when it appears
            self.assertTrue(a[0] == b[0] or a[1] == b[1], (a, b))     # one axis
            self.assertTrue(in_arena(swept(a, b, JR_BOX)), (a, b))

    def test_the_jrs_surround_gohan_above_left_and_right(self):
        """v7 my words: "The Jrs should surround Gohan, not walk to a designated spot"."""
        self.assertEqual(FINISH_C[1] < MIDDLE[1], True)
        self.assertEqual((FINISH_B[0] < MIDDLE[0], FINISH_A[0] > MIDDLE[0]), (True, True))
        self.assertEqual((FINISH_A[1], FINISH_B[1]), (MIDDLE[1], MIDDLE[1]))
        starts = dict((b, a) for a, b in walk_ins(self.f))
        self.assertEqual(starts[FINISH_C][0], FINISH_C[0])             # C comes down from the top edge
        self.assertLess(starts[FINISH_B][0], FINISH_B[0])              # B in from the left edge
        self.assertGreater(starts[FINISH_A][0], FINISH_A[0])           # A in from the right edge
        for spot in (FINISH_A, FINISH_B, FINISH_C):
            self.assertLess(abs(spot[0] - MIDDLE[0]) + abs(spot[1] - MIDDLE[1]), 96, spot)

    def test_each_jr_takes_its_own_attack(self):
        hits = [(n, j) for n, a, j in self.bound if n in (96, 60, 112, 95)]
        self.assertEqual([j for n, j in hits if n == 112], [FINISH_A, FINISH_B, FINISH_C])
        self.assertEqual([(n, j) for n, j in hits if n in (96, 60)], [(96, FINISH_B), (60, FINISH_B)])
        k = self.f.index((96, (0, JR_SET, 100)))
        self.assertEqual(self.f[k + 1], (60, (JR_SET,)))               # nothing spawns between shot and wait

    def test_only_the_blast_waits_on_a_hit(self):
        self.assertEqual([a for n, a in self.f if n == 60], [(JR_SET,)])
        melee = [k for k, c in enumerate(self.f) if c == (57, (0, 7))]
        self.assertEqual(len(melee), 2)
        for k in melee:
            self.assertEqual(self.f[k + 1:k + 3], [(69, (8,)), (112, (JR_SET, 34))])

    def test_no_jr_is_knocked_down(self):
        self.assertFalse([a for n, a in self.f if n in (57, 121) and a[0] == JR_SET and a[1] != 2])

    def test_gohan_teleports_north_of_the_last_jr(self):
        """v8 my words: "have him teleport behind the top cell jr instead of flying". Behind = north: the Jr
        faces Gohan, so he lands above it, faces south (0) and punches south."""
        k = self.f.index((42, (TP_FLASH,)))
        self.assertEqual(self.f[k:k + 5], [(42, (TP_FLASH,)), (62, (0, *GOHAN_TELEPORTS_TO)), (55, (0, 0)),
                                           (43, (TP_FLASH,)), (69, (TP_HOLD,))])
        self.assertEqual(self.f[k + 5:k + 7], [(63, ()), (57, (0, 7))])          # the melee follows at once
        self.assertEqual(GOHAN_TELEPORTS_TO[0], FINISH_C[0])
        self.assertLess(GOHAN_TELEPORTS_TO[1], FINISH_C[1])
        knock = [a[1:3] for n, a in self.f if n == 136 and a[0] == JR_SET][-1]
        self.assertEqual(knock, TELE_KNOCK_SPOT)                                 # C is knocked south, not sideways
        self.assertEqual(knock[0], FINISH_C[0])
        self.assertGreater(knock[1], FINISH_C[1])

    def test_the_finish_has_no_fly_and_moves_only_the_jrs(self):
        """The v6 fly pose and the Gohan glide are gone: no ext 121 or ext 136 on the player in F."""
        self.assertFalse([a for n, a in self.f if n == 121 and a[0] == 0])
        self.assertFalse([a for n, a in self.f if n == 136 and a[0] == 0])
        self.assertEqual([a for n, a in self.f if n == 62], [(0, *MIDDLE), (0, *GOHAN_TELEPORTS_TO)])

    def test_the_teleport_is_the_games_own_effect(self):
        """Goku's vanish, table rom:0x3E6078 word 83 (the record before "#Instant transmission..."): a white
        flash pair holds the actor change, then a hold. The module copies its two values from those bytes."""
        goku, _ = calls(self.before, GOKU_TP_AT)
        self.assertEqual(goku, [(42, (TP_FLASH,)), (52, (60,)), (43, (TP_FLASH,)), (69, (TP_HOLD,))])
        self.assertEqual(self.before[GOKU_TP_AT:GOKU_TP_AT + 20], self.rom[GOKU_TP_AT:GOKU_TP_AT + 20])
        k = self.f.index((42, (TP_FLASH,)))                            # ext 62 for the scene's ext 52: Gohan is
        self.assertEqual([n for n, _ in self.f[k:k + 5]], [42, 62, 55, 43, 69])   # the player, not an NPC set

    def test_finish_spots_fit_the_view_and_clear_cell_and_gohan(self):
        view = view_of(self.f)
        self.assertEqual(view, MIDDLE_VIEW)
        moved = [a[1:3] for n, a in self.f if n == 136 and a[0] == JR_SET]
        for spot in [FINISH_A, FINISH_B, FINISH_C] + moved:
            j = box(spot, JR_BOX)
            self.assertTrue(in_view(j, view), spot)
            self.assertFalse(overlap(j, box(CELL_STANDS, CELL_BOX)), spot)
            self.assertFalse(overlap(j, box(MIDDLE, GOHAN_BOX)), spot)
            self.assertTrue(in_arena(j), spot)
        for start, end in zip((FINISH_A, FINISH_B, FINISH_C), moved):  # knock-backs and Gohan's flight
            self.assertTrue(in_arena(swept(start, end, JR_BOX)), (start, end))
        g = box(GOHAN_TELEPORTS_TO, GOHAN_BOX)                         # v8: he appears there, so no swept path
        self.assertTrue(in_view(g, view))
        self.assertTrue(in_arena(g))
        self.assertFalse(overlap(g, box(CELL_STANDS, CELL_BOX)))
        self.assertFalse(overlap(g, box(FINISH_C, JR_BOX)))
        self.assertFalse(overlap(g, box(TELE_KNOCK_SPOT, JR_BOX)))

    def test_finish_goes_to_n(self):
        self.assertEqual(self.rom[self.notes["finish"]], 29)


class CellFacesGohanTests(unittest.TestCase):
    """v2 change 1: during the Jr fight Cell is an NPC whose step turns him to the player every frame."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.x, _ = calls(cls.rom, cls.notes["fight"])

    def test_vanilla_14_3_spectators_use_the_face_player_step(self):
        for n in SPECTATORS:
            item = spawn_item(self.before, n)
            factory, _, _, _, _, count, step = struct.unpack_from("<IIhhIII", self.before, item)
            self.assertEqual((factory, count), (NPC_FACTORY, 1), n)
            self.assertEqual(u32(self.before, step - ROM_BASE), FACE_STEP, n)

    def test_item_17_is_an_npc_cell_with_the_face_player_step(self):
        item, step = self.notes["cell_npc"], self.notes["cell_step"]
        self.assertEqual(spawn_item(self.rom, CELL_NPC_ITEM), item)
        self.assertEqual(struct.unpack_from("<IIhhIII", self.rom, item),
                         (NPC_FACTORY, 1, *CELL_STANDS, CELL_SET, 1, step + ROM_BASE))  # cond 1: not at map load
        self.assertEqual(self.rom[step:step + 8], self.before[PICCOLO_STEP:PICCOLO_STEP + 8])
        self.assertEqual(u32(self.rom, step), FACE_STEP)

    def test_x_turns_cell_north_right_after_it_builds_him(self):
        """v10: the step cannot run in a scene, so X turns him itself. The ext 55 follows the ext 84, because
        before it no set 30 actor exists for a find by set to bind."""
        self.assertEqual(self.x.index((52, (CELL_SET,))) + 1, self.x.index((84, (CELL_NPC_ITEM,))))
        self.assertEqual(self.x.index((84, (CELL_NPC_ITEM,))) + 1, self.x.index((55, (CELL_SET, FACE_UP))))
        self.assertFalse([a for n, a in self.x if n in (51, 62) and a[0] == CELL_SET])   # X never moves him


class CellFacingInEverySceneTests(unittest.TestCase):
    """v10 my words: in X "cell should move to follow gohan by looking north not south"; in the 1 v 3 start
    and the finish "he should be facing to the left". The FACE_PLAYER step does not run while a scene plays, so
    each scene turns him itself with ext 55."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.recs = {k: calls(cls.rom, cls.notes[k])[0] for k in CELL_FACES}

    def test_each_scene_turns_cell_once_to_the_owners_facing(self):
        for name, want in CELL_FACES.items():
            turns = [a for n, a in self.recs[name] if n == 55 and a[0] == CELL_SET]
            self.assertEqual(turns, [(CELL_SET, want)], name)

    def test_k1_and_f_turn_cell_under_the_black(self):
        """I see these two scenes "after the fade", so the turn sits inside the fade pair."""
        for name in ("one_v_one_end", "finish"):
            got = self.recs[name]
            turn = got.index((55, (CELL_SET, FACE_LEFT)))
            self.assertLess(got.index((40, (30,))), turn, name)
            self.assertLess(turn, got.index((41, (30,))), name)

    def test_north_in_x_and_the_tie_in_the_middle(self):
        """X: Gohan stands 96 px north and 64 px east of Cell, so north is the longer axis. K1 and F: he stands
        80 px west and 80 px north, an exact diagonal, and I chose left."""
        dx, dy = GOHAN_AT[0] - CELL_STANDS[0], GOHAN_AT[1] - CELL_STANDS[1]
        self.assertLess(dy, 0)
        self.assertGreater(abs(dy), abs(dx))
        self.assertEqual((MIDDLE[0] - CELL_STANDS[0], MIDDLE[1] - CELL_STANDS[1]), (-80, -80))

    def test_only_x_and_n_build_a_cell_so_every_turn_binds_item_17(self):
        """A find by set binds the newest actor, so each ext 55 (30, d) must bind item 17's NPC. Across the four
        records of the Jr fight, X removes the type 24 Cell and builds item 17, and N removes item 17 and builds
        the type 24 Cell again. K1 and F touch no set 30 actor, and no record spawns one with ext 51. So from X
        to N the NPC Cell is the only set 30 actor alive, and every turn above binds it."""
        c = [arg for _, op, arg in ops(self.rom, self.notes["counter"] + 3) if op == 2]
        self.assertFalse([n for n in c if n in (51, 52, 55, 84)])      # C only counts; it holds no actor op
        builds, removes = {}, {}
        for name in ("fight", "one_v_one_end", "finish", "restore"):
            got, _ = calls(self.rom, self.notes[name])
            self.assertFalse([a for n, a in got if n == 51 and a[0] == CELL_SET], name)
            for item in (a[0] for n, a in got if n == 84 and a[0] in (CELL_ITEM, CELL_NPC_ITEM)):
                builds.setdefault(name, []).append(item)
            for _ in (a for n, a in got if n == 52 and a == (CELL_SET,)):
                removes.setdefault(name, []).append(CELL_SET)
        self.assertEqual(builds, {"fight": [CELL_NPC_ITEM], "restore": [CELL_ITEM]})
        self.assertEqual(removes, {"fight": [CELL_SET], "restore": [CELL_SET]})

    def test_every_scripted_facing_is_the_one_the_step_picks(self):
        """The step tick `@0x08010038` turns horizontally when |dx| >= |dy| (right when the player is east, else
        left) and vertically otherwise (down when he is south, else up). Its compare is `cmp r4,r5 ; blt`, so an
        exact diagonal falls to the horizontal branch. Each scripted facing is the one the step would pick for
        the scene's own player spot. The step reads the live player, so it decides again once the scene ends and
        I move Gohan; this test pins the scripted value, not what happens after the scene."""
        self.assertEqual(self.before[STEP_RULE_AT:STEP_RULE_AT + len(STEP_RULE)], STEP_RULE)

        def step_picks(player):
            dx, dy = player[0] - CELL_STANDS[0], player[1] - CELL_STANDS[1]
            if abs(dx) >= abs(dy):
                return FACE_RIGHT if dx > 0 else FACE_LEFT
            return FACE_DOWN if dy > 0 else FACE_UP

        self.assertEqual(step_picks(GOHAN_AT), CELL_FACES["fight"])
        self.assertEqual(step_picks(MIDDLE), CELL_FACES["one_v_one_end"])
        self.assertEqual(step_picks(MIDDLE), CELL_FACES["finish"])

    def test_a_vanilla_scene_turns_an_npc_spawn_item_by_set(self):
        """Gate 4 precedent: item 17 is an NPC_FACTORY spawn item, the shape of map 14,3 item 1 (Vegeta, set
        137), and the vanilla seq 50 record turns that one with ext 55 (137, 3) while its scene plays."""
        factory, _, _, _, set_id = struct.unpack_from("<IIhhI", self.before, VEGETA_NPC_ITEM)
        self.assertEqual((factory, set_id), (NPC_FACTORY, VEGETA_SET))
        self.assertEqual(self.before[SEQ50_TURN:SEQ50_TURN + len(TURN_VEGETA)], TURN_VEGETA)
        self.assertEqual(self.before[SEQ50:SEQ50 + 0x91].count(TURN_VEGETA), 1)


class CellStaysWhereHeStandsTests(unittest.TestCase):
    """v3 change 1: the NPC Cell (item 17) is built on the spot where the type 24 Cell stands when X runs."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_item_17_stands_on_item_11s_spot(self):
        self.assertEqual(struct.unpack_from("<hh", self.before, ITEM11 + 0xC), CELL_STANDS)
        self.assertEqual(struct.unpack_from("<hh", self.rom, self.notes["cell_npc"] + 8), CELL_STANDS)
        self.assertEqual(self.rom[ITEM11:ITEM11 + 0x20], self.before[ITEM11:ITEM11 + 0x20])

    def test_nothing_places_cell_between_his_build_and_x(self):
        """Gohan's seq 1 builds item 11, then words 1-29 run before X. Seq 19's ext 99 and ext 100 name (616,384)
        but place no actor: the v1 ss2 state (seq 24) shows Cell at (512,472) after them."""
        found = []
        for k in range(30):
            rec = record(self.before, GOHAN_TABLE, k)
            if self.before[rec + 2] == 0:                             # type 0: code, not text
                found += [(k, c) for c in placed(self.before, rec) if c[1][:1] == (CELL_SET,)]
        self.assertEqual(found, [(0, (52, (CELL_SET,)))])             # seq 1 removes the type 22 Cell, no more
        seq1 = record(self.before, GOHAN_TABLE, 0)
        self.assertIn(bytes([0, 11, 2, 84]), self.before[seq1:seq1 + 0x60])    # push 11 ; ext 84


class MovedJrsStandInTheOwnersCirclesTests(unittest.TestCase):
    """v4: of the 4 Jrs after "My children!", the pair that v2 put in front and v3 put at the right edge now
    stands in my two circles, behind the first row, inside the view and clear of every other actor."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        got, _ = calls(cls.rom, cls.notes["seq31"])
        cls.extra = [a[1:] for n, a in got if n == 51 and a[0] == JR_SET]
        cls.cell = struct.unpack_from("<hh", cls.before, ITEM0 + 0xC)

    def test_the_moved_pair_stands_in_the_owners_circles(self):
        self.assertEqual(self.extra[:2], [(384, 408), (480, 408)])    # extras 1 and 2 stay
        for spot in V2_FRONT_JRS + V3_EDGE_JRS:
            self.assertNotIn(spot, self.extra)
        for spot, (cx, cy, pen) in zip(self.extra[2:], CIRCLES):
            x0, x1, y0, y1 = box(spot, JR_BOX)
            self.assertLessEqual(abs((x0 + x1) / 2 - cx), 1, spot)    # box centre on the circle centre
            self.assertLessEqual(abs((y0 + y1) / 2 - cy), 1, spot)
            self.assertTrue(pen[0] < x0 and x1 < pen[1] and pen[2] < y0 and y1 < pen[3], spot)

    def test_the_moved_pair_stands_behind_gohan_cell_and_the_first_row(self):
        self.assertEqual(self.cell, (500, 440))
        tops = [box(self.cell, CELL_BOX)[2], box(SPAWN_GOHAN_AT, GOHAN_BOX)[2]]
        for spot in self.extra[2:]:
            self.assertLess(box(spot, JR_BOX)[3], min(tops))          # whole box above both: not in front
            self.assertLess(spot[1], min(y for _, y in self.extra[:2]))

    def test_every_jr_fits_the_view_and_clears_cell_gohan_and_the_others(self):
        cam = [a for n, a in calls(self.before, SEQ24)[0] if n == 31]
        self.assertEqual(cam, [(328, 312, 2)])
        x0, y0 = cam[0][:2]
        jrs = [box(s, JR_BOX) for s in VANILLA_JRS + self.extra]
        others = [box(self.cell, CELL_BOX), box(SPAWN_GOHAN_AT, GOHAN_BOX)] + [box(a, ALLY_BOX) for a in ALLIES]
        for k, j in enumerate(jrs):
            self.assertTrue(x0 <= j[0] and j[1] < x0 + VIEW_W and y0 <= j[2] and j[3] < y0 + VIEW_H, j)
            self.assertFalse([o for o in jrs[k + 1:] + others if overlap(j, o)], j)

    def test_the_check_rejects_the_v2_front_pair(self):
        self.assertTrue(overlap(box(V2_FRONT_JRS[0], JR_BOX), box(SPAWN_GOHAN_AT, GOHAN_BOX)))   # stood on Gohan


class JrsComeFromTheTopTests(unittest.TestCase):
    """v2 change 2, v6: X walks 1 Jr down and K1 walks 3, as NPCs, then each becomes its enemy item in place."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.notes = b["rom"], b["notes"]
        cls.parts = {}
        for name, items in (("fight", (ONE,)), ("one_v_one_end", GROUP)):
            got, _ = calls(cls.rom, cls.notes[name])
            names = [n for n, _ in got]
            first_spawn = names.index(51)
            opened, closed = names.index(63, 0, first_spawn), names.index(64, first_spawn)
            cls.parts[name] = (got, items, got[opened + 1:closed], got[closed + 1:])

    def test_each_walk_follows_its_own_spawn(self):
        for name, (_, items, group, _) in self.parts.items():
            self.assertEqual([n for n, _ in group], [51, 53] * len(items), name)   # find by set: the newest

    def test_the_1v1_jr_walks_down_from_above_the_view_to_its_item_spot(self):
        view_top = FIGHT_VIEW[1]
        x, _ = calls(self.rom, self.notes["fight"])
        self.assertEqual([a[:2] for n, a in x if n == 31], [FIGHT_VIEW])
        _, items, group, _ = self.parts["fight"]
        spots = [struct.unpack_from("<hh", self.rom, spawn_item(self.rom, n) + 0xC) for n in items]
        for k in range(len(items)):
            (_, spawn), (_, walk_to) = group[2 * k], group[2 * k + 1]
            self.assertEqual((spawn[0], walk_to[0]), (JR_SET, JR_SET))
            self.assertEqual(spawn[1], walk_to[1])                     # straight down
            self.assertEqual(walk_to[1:], spots[k])
            self.assertLess(spawn[2], view_top - 16)                   # out of view when it appears
            self.assertGreater(walk_to[2], view_top)

    def test_the_group_walks_in_from_the_view_edges_to_its_item_spots(self):
        """v7: under K1's own view on Gohan in the middle, each Jr starts fully out of view, walks along one axis
        and stops fully in view on its item spot; the swept box stays on open arena bands."""
        got, items, group, _ = self.parts["one_v_one_end"]
        view = view_of(got)
        self.assertEqual(view, MIDDLE_VIEW)
        spots = [struct.unpack_from("<hh", self.rom, spawn_item(self.rom, n) + 0xC) for n in items]
        walks = walk_ins(group)
        self.assertEqual([b for _, b in walks], spots)
        sides = set()
        for a, b in walks:
            self.assertFalse(overlap(box(a, JR_BOX), (view[0], view[0] + VIEW_W - 1, view[1], view[1] + VIEW_H - 1)), a)
            self.assertTrue(in_view(box(b, JR_BOX), view), b)
            self.assertTrue(a[0] == b[0] or a[1] == b[1], (a, b))     # one axis
            self.assertTrue(in_arena(swept(a, b, JR_BOX)), (a, b))
            sides.add("above" if b[1] < MIDDLE[1] else "left" if b[0] < MIDDLE[0] else "right")
            self.assertLess(abs(b[0] - MIDDLE[0]) + abs(b[1] - MIDDLE[1]), 64, b)   # around him, not away
        self.assertEqual(sides, {"left", "right", "above"})

    def test_every_npc_jr_goes_before_the_first_jr_enemy(self):
        for name, (_, items, _, tail) in self.parts.items():
            removes = [k for k, c in enumerate(tail) if c == (52, (JR_SET,))]
            builds = [k for k, c in enumerate(tail) if c[0] == 84]
            self.assertEqual(len(removes), len(items), name)
            self.assertEqual([tail[k][1] for k in builds], [(n,) for n in items])
            self.assertLess(max(removes), min(builds))
            self.assertEqual(tail[0], (42, (5,)))                       # a flash covers the swap
            self.assertEqual(tail[max(builds) + 1], (43, (5,)))

    def test_no_record_flies_or_knocks_down_set_31(self):
        if anim_count(self.rom, JR_SET) > 12:
            self.skipTest("set 31 now has anim 12 (a fly pose): a record may use ext 54")
        for name, rec in new_records(self.notes).items():
            got, _ = calls(self.rom, rec)
            self.assertFalse([a for n, a in got if n == 54 and a[0] == JR_SET], name)
            self.assertFalse([a for n, a in got if n in (57, 121) and a[0] == JR_SET and a[1] in (3, 4, 12)], name)

    def test_no_record_plays_the_flying_sound(self):
        """v9 my words: "we just need that flying sprite we do not yet have ... just need to drop the flying
        sound effect". Every arrival is a walk, so sound 26 belongs to none of the new records."""
        for name, rec in new_records(self.notes).items():
            got, _ = calls(self.rom, rec)
            self.assertNotIn((46, (FLY_SOUND,)), got, name)

    def test_every_flash_is_a_pair_outside_a_group(self):
        """ext 42 fades to white and ext 43 fades back (VS5 row); ext 43 in a group would block the script."""
        for name, rec in new_records(self.notes).items():
            got, _ = calls(self.rom, rec)
            depth, open_flash = 0, None
            for n, a in got:
                depth += (n == 63) - (n == 64)
                if n in (42, 43):
                    self.assertEqual(depth, 0, name)
                if n == 42:
                    self.assertIsNone(open_flash, name)
                    open_flash = a
                elif n == 43:
                    self.assertEqual(open_flash, a, name)
                    open_flash = None
            self.assertIsNone(open_flash, name)


class SuperPerfectFacingTests(unittest.TestCase):
    """v2 change 3: Gohan faces Super Perfect Cell, not down, while Goku talks to him (seq 58-64)."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_seq_58_copy_faces_gohan_right_with_the_same_next_index(self):
        rec = self.notes["seq58"]
        self.assertEqual(record(self.rom, SPC_TABLE, 57), rec)
        self.assertEqual((self.rom[rec], self.before[SEQ58]), (58, 58))
        got, left = calls(self.rom, rec)
        self.assertEqual((got, left), ([(55, (0, 3))], []))
        self.assertEqual(self.rom[SEQ58:SEQ58 + 10], self.before[SEQ58:SEQ58 + 10])

    def test_right_is_toward_super_perfect_cell(self):
        x, y = struct.unpack_from("<hh", self.before, ITEM12 + 0xC)
        self.assertEqual(y, SPC_GOHAN_AT[1])
        self.assertGreater(x, SPC_GOHAN_AT[0])
        seq52, _ = calls(self.before, SEQ52)
        self.assertIn((62, (0,) + SPC_GOHAN_AT), seq52)
        self.assertLess(seq52.index((62, (0,) + SPC_GOHAN_AT)), seq52.index((55, (0, 3))))
        self.assertIn((84, (12,)), seq52)
        self.assertEqual(calls(self.before, SEQ58)[0], [(55, (0, 0))])   # vanilla: down
        self.assertEqual(calls(self.before, SEQ65)[0][0], (55, (0, 3)))  # vanilla: right again for the fight


class TrialAiTests(unittest.TestCase):
    """v5 (final, 2026-10-29: "just the AI changes, not the stats"): the fight Jrs use a trial type (type 26's
    bytes, +8 = a copy of AI 21) with a 30-frame wait after each punch and a 2.5 % blast roll. v6: only the 1 v 3
    group uses it, at HP 1550; the 1 v 1 Jr is type 26 with AI 21."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.ai, cls.type_id = cls.notes["ai_id"], cls.notes["type_id"]
        cls.trial, cls.vanilla = walk(cls.rom, cls.ai), walk(cls.before, 21)

    def row(self, k: int, hit: bool = False) -> int:
        return u32(self.rom, AI_TABLE + 8 * (self.ai + k - 21) + 4 * hit)

    def test_ai_21_and_the_node_block_are_unchanged_and_type_26_only_at_its_descriptor(self):
        for lo, hi in (NODE_BLOCK, (AI_TABLE, AI_TABLE + 8 * 163)):
            self.assertEqual(self.rom[lo:hi], self.before[lo:hi], f"rom:0x{lo:X}")
        lo, hi = ENEMY_TABLE, ENEMY_TABLE + 24 * 163
        self.assertEqual([lo + i for i in range(hi - lo) if self.rom[lo + i] != self.before[lo + i]],
                         [i for i in range(TYPE26_DESC_AT, TYPE26_DESC_AT + 4)
                          if self.rom[i] != self.before[i]])
        self.assertEqual(self.before[TYPE26_AT:TYPE26_AT + 24], TYPE26)
        self.assertEqual(self.rom[TYPE26_AT:TYPE26_AT + 24], TYPE26[:20] + struct.pack("<I", BOSS_DESC))
        self.assertEqual(u32(self.rom, ROLL_NODE + 12), ROLL_BEFORE)
        self.assertEqual(walk(self.rom, 21), self.vanilla)

    def test_the_trial_type_is_type_26_with_hp_1550_the_trial_ai_and_the_normal_descriptor(self):
        t, rows = self.notes["type_entry"], self.notes["ai_rows"]
        self.assertEqual((t - ENEMY_TABLE) % 24, 0)
        self.assertEqual(ENEMY_TABLE + 24 * self.type_id, t)
        self.assertEqual((rows - AI_TABLE) % 8, 0)
        self.assertEqual(AI_TABLE + 8 * self.ai, rows)
        self.assertGreaterEqual(min(t, rows), 0x800000)
        self.assertEqual(self.rom[t:t + 24], TYPE26[:4] + struct.pack("<2I", GROUP_HP, self.ai) + TYPE26[12:])
        self.assertEqual(u32(self.rom, t + 0x14), NORMAL_DESC)

    def test_the_group_uses_the_trial_type_and_the_relay_and_1v1_jrs_keep_26(self):
        for n in GROUP:                                                # found through the spawn list, not notes
            self.assertEqual(u32(self.rom, spawn_item(self.rom, n) + 8), self.type_id, n)
        for item in (ITEM8, ITEM9, ITEM10, spawn_item(self.rom, ONE)):
            self.assertEqual(u32(self.rom, item + 8), JR_TYPE)

    def test_the_copy_is_rows_21_to_28_with_only_the_two_changes(self):
        copied = {a for a in self.trial if a - ROM_BASE >= 0x800000}
        size = sum(16 + 4 * len(kids(self.rom, a)) if SHAPES.get(f) in ("SEQ", "OR", "COMP")
                   else {"DIST": 24, "RANDOM": 20}.get(SHAPES.get(f), 16) for a, f in self.trial.items() if a in copied)
        self.assertEqual((len(copied), size), (COPIED, COPIED_BYTES + 4))
        shared = {a for a in self.trial if NODE_BLOCK[0] <= a - ROM_BASE < NODE_BLOCK[1]}
        self.assertEqual(shared, SHARED_IN_BLOCK | {WAIT_NODE})
        self.assertEqual({a for a in self.trial if a not in copied} - shared,
                         {a for a in self.vanilla if not NODE_BLOCK[0] <= a - ROM_BASE < NODE_BLOCK[1]})
        for a in copied:
            self.assertIn(self.trial[a], SHAPES, f"{a:#x}")
        seen = {}

        def same(v: int, t: int) -> None:
            if v in seen:
                self.assertEqual(seen[v], t)
                return
            seen[v] = t
            if t not in copied:
                self.assertEqual(t, v)                                  # shared node: the same address
                return
            ov, ot = v - ROM_BASE, t - ROM_BASE
            self.assertEqual(self.rom[ot:ot + 12], self.before[ov:ov + 12])   # factory and its 2 methods
            shape, kv = SHAPES[self.trial[t]], kids(self.before, v)
            if shape in ("PUSH", "JUMP"):
                row = u32(self.before, ov + 12)
                self.assertEqual(u32(self.rom, ot + 12), self.ai + row - 21 if row in AI21_ROWS else row)
            elif ov == ROLL_NODE:
                self.assertEqual((u32(self.before, ov + 12), u32(self.rom, ot + 12)), (ROLL_BEFORE, ROLL_AFTER))
            elif v == u32(self.before, AI_TABLE + 8 * 26):
                kv = kv[:1] + [WAIT_NODE] + kv[1:]
                self.assertEqual((u32(self.before, ov + 12), u32(self.rom, ot + 12)), (2, 3))
            elif shape not in ("SEQ", "OR", "COMP", "GUARD"):
                self.assertEqual(self.rom[ot + 12:ot + 16], self.before[ov + 12:ov + 16])   # d2 or p
            kt = kids(self.rom, t)
            self.assertEqual(len(kt), len(kv))
            for x, y in zip(kv, kt):
                same(x, y)

        for r in AI21_ROWS:
            for hit in (0, 4):
                same(u32(self.before, AI_TABLE + 8 * r + hit), self.row(r, bool(hit)))

    def test_row_26_waits_30_frames_after_the_punch_and_row_22_rolls_2_5_percent(self):
        main = self.row(26) - ROM_BASE
        self.assertEqual(SHAPES[u32(self.rom, main)], "SEQ")
        self.assertEqual(kids(self.rom, self.row(26))[:2], [PUNCH_LEAF, WAIT_NODE])
        self.assertEqual(struct.unpack_from("<4I", self.rom, WAIT_NODE - ROM_BASE), (WAIT_F, 0, 0, 30))
        self.assertEqual(u32(self.rom, PUNCH_LEAF - ROM_BASE), PUNCH_F)
        rolls = [a for a, f in self.trial.items() if SHAPES.get(f) == "RANDOM" and a - ROM_BASE >= 0x800000
                 and u32(self.rom, kids(self.rom, a)[0] - ROM_BASE + 12) == self.ai + 2]   # child: PUSH row 23'
        self.assertEqual(len(rolls), 1)
        p = u32(self.rom, rolls[0] - ROM_BASE + 12)
        self.assertEqual(p, ROLL_AFTER)
        self.assertAlmostEqual(100 * p / 65536, 2.5, delta=0.01)
        self.assertAlmostEqual(100 * ROLL_BEFORE / 65536, 5.0, delta=0.01)

    def test_the_punch_leaf_is_reached_only_through_row_26(self):
        for nodes, rom, row26 in ((self.trial, self.rom, self.row(26)),
                                  (self.vanilla, self.before, u32(self.before, AI_TABLE + 8 * 26))):
            self.assertEqual({a for a, f in nodes.items() if f == PUNCH_F}, {PUNCH_LEAF})
            parents = {a for a in nodes if PUNCH_LEAF in kids(rom, a)}
            self.assertEqual(parents, {row26})

    def test_a_hit_returns_to_the_trial_ai(self):
        for k in range(22, 29):
            self.assertEqual(self.row(k, True), SHARED_HIT)
        self.assertEqual(u32(self.rom, AI_TABLE + 8 * 22 + 4), SHARED_HIT)       # vanilla shares it too
        hit = self.row(21, True)
        steps = kids(self.rom, hit)
        self.assertEqual([SHAPES[u32(self.rom, a - ROM_BASE)] for a in steps], ["PUSH", "JUMP"])
        self.assertEqual([u32(self.rom, a - ROM_BASE + 12) for a in steps], [self.ai, 18])
        for off, want in CODE_PINS:
            self.assertEqual(self.rom[off:off + len(want) // 2].hex(), want, f"rom:0x{off:X}")
        seen, ids = set(), set()
        todo = [u32(self.rom, AI_TABLE + 8 * r + k) for r in range(16, 21) for k in (0, 4)]
        while todo:                                                    # every word that points into the block
            a = todo.pop()
            if a in seen or not NODE_BLOCK[0] <= a - ROM_BASE < NODE_BLOCK[1]:
                continue
            seen.add(a)
            w = struct.unpack_from("<10I", self.rom, a - ROM_BASE)
            todo += [x for x in w[1:] if NODE_BLOCK[0] <= x - ROM_BASE < NODE_BLOCK[1]]
            if w[0] in (0x0801AB65, 0x0801B511, 0x0801A71D):
                ids.add(w[3])
        self.assertEqual(ids, HIT_PATH_IDS)

    def test_a_changed_ai_byte_refuses_before_writing(self):
        b = built()
        for off in (ROLL_NODE + 12, 0x6D2630 + 12, WAIT_NODE - ROM_BASE + 12, AI_TABLE + 8 * 26, TYPE26_AT + 8):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                celljr_fight.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)


if __name__ == "__main__":
    unittest.main()
