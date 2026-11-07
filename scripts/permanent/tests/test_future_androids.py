r"""
test_future_androids.py - Tests for patches.future_androids (trial 2026-11-07): the ending's scripted
                          beatings of FUTURE Android 18 (word 8) and FUTURE Android 17 (word 11) become
                          two individual player fights on a clone of map 1,2.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_future_androids.py -v
Builds build_list_trial_future.txt in memory: "before" = the ending trial (dev r41, battle_arena,
ending_fight) and "rom" = before plus future_androids. Every expected value is restated here from
docs\tasks\2026-11-07-future-androids\brief.md, the owner's sequencing of 2026-11-07, and the base
bytes read in scripts\one-time\2026-11-07-future-androids\01_probe.py. Nothing is taken from the patch
module except apply() and the record builders the design lives in.
"""
import copy
import struct
import unittest

import log2_build
from patches import future_androids as F
from scene import scene_probe as P
from scene.scene_lib import record_end, words_naming, zigzag
from tests.test_cellgames_ssj import ext_sequence, ops as raw_ops

# ===== constants (the brief, the owner's words, and the base reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_future.txt"
BASE_MAPS, BASE_COUNT, MAP_SIZE = 0x409368, 327, 56
TABLE, TABLE_WORDS = 0x3B8140, 27
PLAYER, TRUNKS, TRUNKS_BASE, TRUNKS_SSJ = 0, 3, 132, 133
A18_SET, A17_SET, GOHAN_SET = 11, 9, 54
A18_TYPE, A17_TYPE = 4, 3
A18_HP, A17_HP, ANDROID_AI = 2910, 3550, 21
CLONE_ZONE, CLONE_AREA, CLONE_ITEMS = 1, 100, 4
NPC_18, NPC_17, ENEMY_18, ENEMY_17 = 0, 1, 2, 3   # positional: the two dropped NPCs close the gap
PLAYER_START, TRUNKS_SPOT = (496, 648), (496, 504)
A18_AT, A17_AT, GOHAN_AT = (472, 408), (520, 408), (216, 368)
REVEAL_VIEW, TALK_VIEW, SPEED, REVEAL = (384, 552), (384, 368), 2, 180
NO_BANNER, MUSIC_SCRIPT, WALK_IN_MUSIC = 0xDD, 0x083ED73C, 42
COLLAPSE_HOLD, HANDBACK = 60, 60
DOWN, UP = 0, 1
POWER_UP, AURA_SOUND, FLASH = 9, 55, 10
END_INDEX, AFTER18, AFTER17 = 26, 9, 12
EDITED = (0, 4, 6, 8, 11)
PROLOGUE_TABLE, REGION_LIST, REGION_ITEM = 0x3B7ADC, 0x3ED7F0, 0x3ED7DC
FACE_PLAYER = bytes.fromhex("99000108" "007d0000")      # celljr_fight's step: face the player
EVENT_RUNNER, ENEMY_FACTORY, NPC_FACTORY = 0x080106B3, 0x0800E77F, 0x0800D6DF
COND_ALWAYS, COND_NEVER_AT_LOAD = 0, 1

# Word 0: every vanilla op is kept and five things change. The load becomes ext 39 so a player is built,
# ext 73 and ext 70 go in front of it, the three ops that drove NPC set 132 drive set 0, and a camera
# park plus a fade_in replace the reveal ext 35 used to do by itself.
ARRIVE_TAIL = [(40, (REVEAL,)),
               (86, (0,)), (73, (TRUNKS, TRUNKS_BASE)), (70, (TRUNKS,)),
               (39, (CLONE_ZONE, CLONE_AREA, 1) + PLAYER_START),
               (69, (120,)),
               (55, (PLAYER, UP)), (31, REVEAL_VIEW + (SPEED,)), (41, (REVEAL,)), (33, (PLAYER,)),
               (53, (PLAYER,) + TRUNKS_SPOT),
               (31, TALK_VIEW + (SPEED,)), (69, (60,)), (55, (A17_SET, 2)), (69, (30,)), (49, (38,))]
# Word 4, the Super Saiyan beat: cellgames_ssj.GOKU_TRANSFORM's own shape with the appearance op
# retargeted at Trunks. ext 57 blocks (sub_08009FC4 ends in BL Queue_Append, which runs the frame loop
# at 0x0801F2F4 when the group flag is 0), so all 160 frames of player state 9 play and the state
# plays sound 23 itself at its end. Vanilla's closing sound(23) is dropped as a duplicate. ext 42 and
# ext 43 fade to white and back, so the ext 73 body swap lands while the screen is white.
TRANSFORM_OPS = [(69, (40,)), (55, (PLAYER, DOWN)), (46, (AURA_SOUND,)),
                 (57, (PLAYER, POWER_UP)), (42, (FLASH,)), (47, (AURA_SOUND,)),
                 (73, (TRUNKS, TRUNKS_SSJ)), (43, (FLASH,))]
NAME_OPS = [(55, (PLAYER, UP))]
# Words 8 and 11: the four op battle start, the shape 25 of the 25 vanilla bar records use.
FIGHT18_OPS = [(104, (A18_SET, ENEMY_18)), (85, (A18_SET,)), (86, (1,)), (33, (PLAYER,))]
FIGHT17_OPS = [(104, (A17_SET, ENEMY_17)), (85, (A17_SET,)), (86, (1,)), (33, (PLAYER,))]
# ===== the death beats (rung 4, the owner's words of 2026-11-07) =====
# "18 fight -> she collapses -> Trunks blasts her, NO transition" and "if 17 is already on screen, he
# just goes to his dialogue. If he is offscreen, then he walks onscreen, facing trunks".
# Every number here is restated from the brief and the disassembly, never imported from the module.
A17_SPOT, BLAST_SPEED = (520, 408), 100       # 17's own item spot; the n of vanilla's rom:0x3E523F
CAM_X, CAM_Y = 112, 80                        # the follow camera's offset from the player (B1144)
SCREEN_W, SCREEN_H = 240, 160
ENTRY_INSET, STOP_INSET = 24, 72              # how far outside, and inside, the left edge of the view
A17_HALF_W, A17_TOP = 8, 32                   # his drawn box, from his anchor
TALK_X, TALK_Y = 88, 52                       # half extents of the "already beside Trunks" box
# The player spots from which 17's drawn box has NO pixel on screen. Restated from the geometry, not
# imported: his box spans x 512-528 and y 376-408, and the view is the player minus (112,80).
GONE_X = (A17_SPOT[0] - A17_HALF_W - SCREEN_W + CAM_X + 1, A17_SPOT[0] + A17_HALF_W + CAM_X - 1)
GONE_Y = (A17_SPOT[1] - A17_TOP - SCREEN_H + CAM_Y + 1, A17_SPOT[1] + CAM_Y - 1)
HALF = 1 << 16
V_SPOT, V_PY, V_PX, V_FLAG = 0, 1, 2, 3       # scene variables: set_var n writes 0x03001FB0 + 4n
V_GONE, SIDE_STEP = V_SPOT, 80                # the packed spot's slot, reused; and the left-to-right swing
JZ, END_OP = 19, 17
# No death record may carry one of these: a camera move, a camera hand-off, a map load, a fade or a
# flash. "NO transition" is the owner's emphasis and this is the list that enforces it. ext 62 is NOT
# on the list: it is the reposition that puts 17 outside the left edge of the view, it runs only when
# his drawn box has no pixel on screen, and its command writes nothing but +0x158/+0x15C
# (`sub_0800A44E`, start `@0x0800E1DC`, done `@0x08026498` = `mov r0,#1 ; bx lr`).
NO_TRANSITION_OPS = (31, 33, 35, 38, 39, 40, 41, 42, 43)


def _push(*vals):
    """The push op the encoder emits: base op 0 for one small byte, base op 29 otherwise."""
    if len(vals) == 1 and 0 <= vals[0] <= 0xFF:
        return [(0, [vals[0]])]
    return [(29, list(vals))]


def _ext(n, *vals):
    return (_push(*vals) if vals else []) + [(2, n)]


def blast_ops(enemy_set):
    """Trunks turns to the body, fires ext 96 as the PLAYER, ext 60 waits for the hit, the body goes."""
    return (_ext(56, PLAYER, enemy_set) + _ext(63)
            + _ext(96, PLAYER, enemy_set, BLAST_SPEED) + _ext(60, enemy_set) + _ext(64)
            + _ext(52, enemy_set))


def read_player_ops():
    """ext 143 pushes the player's spot PACKED as (x << 16) | (y & 0xFFFF). Multiplying by 65536
    shifts the x half out in 32 bits, so one divide gives y; subtracting y and dividing again gives
    x. V_FLAG is then `px < 112`, the one camera clamp map 1,100's open cells can reach."""
    return (_ext(143, PLAYER) + [(3, V_SPOT)]
            + _ext(V_SPOT) + _push(HALF) + [(9, None)] + _push(HALF) + [(10, None), (3, V_PY)]
            + _ext(V_SPOT) + _ext(V_PY) + [(8, None)] + _push(HALF) + [(10, None), (3, V_PX)]
            + _ext(V_PX) + _push(CAM_X) + [(15, None), (3, V_FLAG)])


def outside_ops(slot, lo, hi):
    """Leave 1 when variable `slot` is below `lo` or above `hi`. lt and gt test SECOND against TOP."""
    return _ext(slot) + _push(lo) + [(15, None)] + _ext(slot) + _push(hi) + [(13, None), (5, None)]


def screen_x_ops(back, floor_x):
    """max(px - back, floor_x), written without a jump as a + (floor - a) * V_FLAG."""
    a = _ext(V_PX) + _push(back) + [(8, None)]
    return a + _push(floor_x) + a + [(8, None)] + _ext(V_FLAG) + [(9, None), (7, None)]


def approach_ops(npc_set):
    """17 is left standing, walks from where he stands, or is dropped just outside the left edge of
    the view with ext 62 and walks 96 px in. Both face ops run on every path."""
    enter = _push(npc_set) + screen_x_ops(CAM_X + ENTRY_INSET, -ENTRY_INSET) + _ext(V_PY) + _ext(62)
    side = (_push(SIDE_STEP) + _ext(V_PX) + _push(A17_SPOT[0]) + [(15, None), (9, None)]
            + _push(1) + _ext(V_GONE) + [(8, None), (9, None)])
    walk = (_push(npc_set) + screen_x_ops(CAM_X - STOP_INSET, STOP_INSET) + side + [(7, None)]
            + _push(HALF) + [(9, None)] + _ext(V_PY) + [(7, None)] + _ext(144))
    gone = (outside_ops(V_PX, *GONE_X) + outside_ops(V_PY, *GONE_Y) + [(5, None), (3, V_GONE)]
            + _ext(V_GONE))
    away = (outside_ops(V_PX, A17_SPOT[0] - TALK_X, A17_SPOT[0] + TALK_X)
            + outside_ops(V_PY, A17_SPOT[1] - TALK_Y, A17_SPOT[1] + TALK_Y) + [(5, None)])
    return (read_player_ops() + away + [(JZ, None)] + gone + [(JZ, None)] + enter + walk
            + _ext(56, npc_set, PLAYER) + _ext(56, PLAYER, npc_set))


def death_ops(enemy_set, entrance=None):
    """The whole death record, op by op, with the jz offset left out (it is pinned on its own)."""
    beat = (_ext(88) + _ext(86, 0) + _ext(57, enemy_set, 3) + _ext(69, COLLAPSE_HOLD)
            + blast_ops(enemy_set))
    if entrance is None:
        return beat + _ext(55, PLAYER, DOWN) + _ext(69, HANDBACK) + [(END_OP, None)]
    return beat + approach_ops(entrance) + _ext(69, HANDBACK) + [(END_OP, None)]


def record_ops(rom, rec):
    """[(op, arg)] of a type 0 record body, with every jz and jmp offset blanked to None."""
    return [(op, None if op in (JZ, 18) else arg) for _, op, arg in raw_ops(rom, rec + 3)]


# ===== a 32-bit evaluator for the branch, because pinning the bytes does not run the decision =====
# scene_harness cannot do this job: its ext handling clears the whole stack, so a record that reads
# a value back with ext 0 to ext 3 loses it. This models only what the branch uses, in 32 bits,
# because the exact-dy trick depends on the engine's multiply wrapping.
BINARY_32 = {5: lambda a, b: int(bool(a) or bool(b)), 7: lambda a, b: a + b,
             8: lambda a, b: a - b, 9: lambda a, b: a * b,
             10: lambda a, b: int(a / b), 13: lambda a, b: int(a > b), 15: lambda a, b: int(a < b)}
# How many values each plain ext op in a death record pops, from docs\research\scene-vm-ext-ops.md.
EXT_ARITY = {52: 1, 55: 2, 56: 2, 57: 2, 60: 1, 63: 0, 64: 0, 69: 1, 86: 1, 88: 0, 96: 3}


def _signed(v):
    v &= 0xFFFFFFFF
    return v - (1 << 32) if v & 0x80000000 else v


def run_branch(rom, rec, player):
    """Run the death record's VM ops with ext 143 answering `player`. Returns a dict with `walked`
    (did the walk-in arm run), `target` (the (x, y) ext 144 unpacks), `entry` (the (x, y) ext 62
    places him at, or None when no teleport ran), and `left` (the stack depth at the record's end
    op, which MUST be 0: one leftover value becomes the next table index)."""
    body = {at: (op, arg) for at, op, arg in raw_ops(rom, rec + 3)}
    order = sorted(body)
    stack, var, out, at = [], {}, {"walked": False, "target": None, "entry": None}, order[0]
    for _ in range(400):
        op, arg = body[at]
        step = [a for a in order if a > at]
        nxt = step[0] if step else None
        if op in (0, 1):
            stack.append(arg[0])
        elif op == 29:
            stack += list(arg)
        elif op == 3:
            var[arg] = stack.pop()
        elif op == 2 and arg in (0, 1, 2, 3):
            stack.append(var.get(arg, 0))
        elif op == 2 and arg == 143:
            stack[-1] = (player[0] << 16) | (player[1] & 0xFFFF)     # pops the set, pushes the spot
        elif op == 2 and arg == 62:
            y, x, _set = stack.pop(), stack.pop(), stack.pop()       # ext 62 (set, x, y)
            out["entry"] = (x, y)
        elif op == 2 and arg == 144:
            packed, _set = stack.pop(), stack.pop()
            out["target"] = (_signed(packed) >> 16, _signed((packed & 0xFFFF) << 16) >> 16)
            out["walked"] = True
        elif op == 2:
            # Pop the documented arity, never "clear the stack": clearing would hide exactly the
            # leftover value that op 17 would turn into a table index.
            for _ in range(EXT_ARITY[arg]):
                stack.pop()
        elif op in BINARY_32:
            b, a = stack.pop(), stack.pop()
            stack.append(_signed(BINARY_32[op](a, b)))
        elif op == JZ:
            if not stack.pop():
                nxt = arg                                            # raw_ops gives jz an ABSOLUTE target
        elif op == END_OP:
            out["left"] = len(stack)
            return out
        else:
            raise AssertionError(f"rom:0x{at:X}: op {op} is not modelled by run_branch")
        at = nxt
    raise AssertionError(f"rom:0x{rec:X}: the record did not reach its end op")


# The main game's own Android fights, which the owner ruled out of this work.
MAIN_GAME_MAPS = ((11, 4), (11, 5), (11, 6), (8, 49))

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("future_androids")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), order=names, alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["future_androids"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["future_androids"],
                      base=log2_build.BASE.read_bytes())
    return _CACHE


def staged() -> tuple:
    """(rom, alloc) exactly as future_androids receives them: the ending trial, before this module."""
    b = built()
    return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])


def clone(rom: bytes) -> int:
    return F.map_entry(rom, CLONE_ZONE, CLONE_AREA)[1]


def clone_items(rom: bytes) -> list:
    at = clone(rom)
    lst = u32(rom, at + F.F_ITEMS) - ROM_BASE
    return [u32(rom, lst + 4 * k) - ROM_BASE for k in range(rom[at + F.F_ITEM_COUNT])]


def body(rom: bytes, word: int) -> list:
    return ext_sequence(rom, u32(rom, TABLE + 4 * word) - ROM_BASE)


class BuildOrder(unittest.TestCase):
    def test_future_androids_runs_last(self):
        """It appends to the table battle_arena moved, and ending_fight checks that words 0, 4, 6, 8
        and 11 are still vanilla when it runs. Either one out of order is a silent wrong build."""
        order = built()["order"]
        self.assertEqual(order[-1], "future_androids")
        self.assertLess(order.index("battle_arena"), order.index("future_androids"))
        self.assertLess(order.index("ending_fight"), order.index("future_androids"))

    def test_the_two_masters_do_not_carry_this_module(self):
        for name in ("build_list.txt", "build_list_core.txt", "build_list_dev.txt"):
            names = log2_build.read_build_list(log2_build.ROOT / "scripts" / "permanent" / name)
            self.assertNotIn("future_androids", names, name)

    def test_a_second_run_raises(self):
        rom, alloc = staged()
        F.apply(rom, alloc)
        with self.assertRaises(ValueError):
            F.apply(rom, alloc)


class VanillaUntouched(unittest.TestCase):
    """The owner ruled out every earlier Android fight, and the prologue plays on map 1,2."""

    def test_the_main_game_android_fights_keep_every_byte(self):
        b = built()
        for set_id, (item, item_body, event, event_body, tail, tail_body) in F.TEMPLATES.items():
            self.assertEqual(b["rom"][item:item + 0x20], item_body, f"enemy item of set {set_id}")
            self.assertEqual(b["rom"][event:event + 8], event_body, f"event struct of set {set_id}")
            self.assertEqual(b["rom"][tail:tail + 8], tail_body, f"step struct of set {set_id}")

    def test_the_android_enemy_types_are_not_written(self):
        """No stat change: Android 18 keeps type 4 and Android 17 type 3, both at AI 21."""
        b = built()
        for type_id, hp in ((A18_TYPE, A18_HP), (A17_TYPE, A17_HP)):
            at = F.ENEMY_TABLE + F.ENEMY_ENTRY * type_id
            self.assertEqual(b["rom"][at:at + F.ENEMY_ENTRY], b["base"][at:at + F.ENEMY_ENTRY])
            self.assertEqual(u32(b["rom"], at + 4), hp)
            self.assertEqual(u32(b["rom"], at + 8), ANDROID_AI)

    def test_the_main_game_android_map_entries_keep_every_byte(self):
        b = built()
        for zone, area in MAIN_GAME_MAPS:
            _, live = F.map_entry(b["rom"], zone, area)
            _, orig = P.map_entry(b["base"], zone, area)
            self.assertEqual(b["rom"][live:live + MAP_SIZE], b["base"][orig:orig + MAP_SIZE],
                             f"map {zone},{area}")

    def test_map_1_2_itself_is_never_written(self):
        """The clone exists so that map 1,2 keeps its region, its door, its banner and its four NPCs."""
        b = built()
        _, live = F.map_entry(b["rom"], 1, 2)
        self.assertEqual(b["rom"][live:live + MAP_SIZE], F.SOURCE_ENTRY)
        for at, n in ((F.SOURCE_LAYOUT, F.LAYOUT_SIZE), (F.SOURCE_LAYOUTS, 4), (REGION_LIST, 8),
                      (REGION_ITEM, 0x18), (F.SOURCE_WARP_LIST, 4), (F.SOURCE_DOOR, 0x18)):
            self.assertEqual(b["rom"][at:at + n], b["base"][at:at + n], f"rom:0x{at:X}")
        for item, item_body, step, step_body in F.SOURCE_NPCS:
            self.assertEqual(b["rom"][item:item + 0x18], item_body)
            self.assertEqual(b["rom"][step:step + 8], step_body)

    def test_the_vanilla_records_of_every_edited_word_stay_where_they_are(self):
        """Only the table words move, so a save state paused inside a vanilla record still runs out."""
        b = built()
        for k in EDITED:
            rec, _ = F.RECORDS[k]
            n = record_end(b["base"], rec) - rec
            self.assertEqual(b["rom"][rec:rec + n], b["base"][rec:rec + n], f"record of word {k}")
            self.assertNotEqual(u32(b["rom"], TABLE + 4 * k), rec + ROM_BASE, f"word {k}")


class Prologue(unittest.TestCase):
    """Map 1,2 carries an always-on step trigger over rect (-15,-7)-(360,584) that fires the prologue
    scene table rom:0x3B7ADC. A real fight lets the player walk, so the clone must hold no path to it."""

    def test_the_clone_carries_no_region_list_at_all(self):
        rom = built()["rom"]
        at = clone(rom)
        self.assertEqual(rom[at + F.F_REGION_COUNT], 0)
        self.assertEqual(u32(rom, at + F.F_REGIONS), 0)

    def test_every_word_that_reaches_the_prologue_belongs_to_a_map_1_2_entry(self):
        """Walked backwards: the table is named only by the region item's +0x10, the region item only
        by the region list's +4, and the region list only by +0x10 words of map 1,2 entries. There is
        one such entry per table copy, and the clone is not one of them."""
        rom = built()["rom"]
        self.assertEqual(words_naming(rom, PROLOGUE_TABLE), [REGION_ITEM + 0x10])
        self.assertEqual(words_naming(rom, REGION_ITEM), [REGION_LIST + 4])
        namers = words_naming(rom, REGION_LIST)
        self.assertTrue(namers)
        for word in namers:
            entry = word - F.F_REGIONS
            self.assertEqual((rom[entry], rom[entry + 1]), (1, 2), f"rom:0x{word:X}")
            self.assertNotEqual(entry, clone(rom))

    def test_the_prologue_still_works_on_map_1_2(self):
        rom = built()["rom"]
        _, live = F.map_entry(rom, 1, 2)
        self.assertEqual(u32(rom, live + F.F_REGIONS), REGION_LIST + ROM_BASE)
        self.assertEqual(rom[live + F.F_REGION_COUNT], 1)


class CloneMap(unittest.TestCase):
    def test_the_clone_is_appended_and_the_table_is_relocated(self):
        b = built()
        before_table, before_count = F.map_table(b["before"])
        table, count = F.map_table(b["rom"])
        self.assertEqual(count, before_count + 1)
        self.assertNotEqual(table, before_table)
        self.assertEqual(b["rom"][table:table + MAP_SIZE * before_count],
                         b["before"][before_table:before_table + MAP_SIZE * before_count],
                         "every live entry is carried over byte for byte")
        for lit in F.BASE_LITERALS:
            self.assertEqual(u32(b["rom"], lit), table + ROM_BASE)
        self.assertEqual(u32(b["rom"], F.ENTRY3_LITERAL), table + MAP_SIZE * F.ENTRY3 + ROM_BASE)
        self.assertEqual(0xFF + b["rom"][F.MAP_COUNT_BYTE], count)

    def test_the_clone_entry_fields(self):
        rom = built()["rom"]
        at = clone(rom)
        self.assertEqual((rom[at], rom[at + 1]), (CLONE_ZONE, CLONE_AREA))
        self.assertEqual(rom[at + F.F_VARIATIONS], 1)
        self.assertEqual(rom[at + F.F_ITEM_COUNT], CLONE_ITEMS)
        self.assertEqual(u32(rom, at + F.F_COMBAT), 1, "the player must be able to attack")
        self.assertEqual(u32(rom, at + F.F_BANNER), NO_BANNER, "0xDD shows no map name over the fight")
        self.assertEqual(u32(rom, at + F.F_MUSIC), WALK_IN_MUSIC,
                         "the song already playing, so the ext 39 load's music read is a no-op")
        self.assertNotEqual(u32(rom, at + F.F_MUSIC), MUSIC_SCRIPT,
                            "map 1,2's script returns 38, which would cue the Android theme early")
        for field in (F.F_SWAPS, F.F_PICKUPS, F.F_MARKERS, F.F_VAR_SCRIPT, F.F_ENTER, F.F_LEAVE):
            self.assertEqual(u32(rom, at + field), 0, f"+0x{field:02X}")

    def test_the_clone_has_no_doors_in_EITHER_carrier(self):
        """A map carries doors in two places. Map 1,2's layout holds one, to map 2,22, and map 2,22's
        own way back names map 1,2, not the clone, so a player who left could never return."""
        rom = built()["rom"]
        at = clone(rom)
        items = P.map_items(rom, CLONE_ZONE, CLONE_AREA)
        self.assertEqual(items["regions"], [])
        layout = P.layouts(rom, at)[0]
        doors = P.layout_doors(rom, layout)
        self.assertEqual(doors["count"], 0)
        self.assertEqual(doors["doors"], [])
        self.assertEqual(doors["list"], 0)
        self.assertEqual([i for i in items["items"] if i["kind"] == "warp"], [])

    def test_the_layout_copy_changes_only_the_two_door_words(self):
        b = built()
        layout = P.layouts(b["rom"], clone(b["rom"]))[0]
        src = b["base"][F.SOURCE_LAYOUT:F.SOURCE_LAYOUT + F.LAYOUT_SIZE]
        got = b["rom"][layout:layout + F.LAYOUT_SIZE]
        changed = {i // 4 * 4 for i in range(F.LAYOUT_SIZE) if src[i] != got[i]}
        self.assertEqual(changed, {F.L_WARP_COUNT, F.L_WARP_LIST})

    def test_the_clone_shares_map_1_2s_collision_props_and_layers(self):
        """The owner asked to change who fights, not the staging, so the ground is map 1,2's own."""
        rom = built()["rom"]
        layout = P.layouts(rom, clone(rom))[0]
        self.assertEqual(u32(rom, layout + F.L_COLLISION), F.SOURCE_COLLISION + ROM_BASE)
        self.assertEqual(u32(rom, layout + F.L_PROP_LIST), F.SOURCE_PROP_LIST + ROM_BASE)
        for off, want in zip((F.L_BG0, F.L_BG1, F.L_BG2, F.L_BG3), F.SOURCE_LAYERS):
            self.assertEqual(u32(rom, layout + off), want + ROM_BASE)


class CloneItems(unittest.TestCase):
    """The owner, 2026-11-07: "make sure they are individual fights, he fights 18 first, then cutscene,
    then 17". The NPC/enemy pairing is what keeps 17 inert while 18 is being fought, and it is vanilla:
    map 11,4 pairs NPC set 9 (item 0, cond 0) with enemy type 3 set 9 (item 1, cond 1) and leaves NPC
    set 11 and NPC set 8 standing through the whole Piccolo fight."""

    def test_the_two_npcs_are_built_at_load_and_the_two_enemies_are_not(self):
        rom = built()["rom"]
        items = clone_items(rom)
        self.assertEqual(len(items), CLONE_ITEMS)
        for k, (set_id, spot) in enumerate(((A18_SET, A18_AT), (A17_SET, A17_AT))):
            at = items[k]
            self.assertEqual(u32(rom, at), NPC_FACTORY, f"item {k}")
            self.assertEqual(u32(rom, at + F.N_COND), COND_ALWAYS, f"item {k} is built at load")
            self.assertEqual(u32(rom, at + F.N_SET), set_id)
            self.assertEqual(struct.unpack_from("<hh", rom, at + F.N_AT), spot)
        for k, (set_id, type_id, spot) in enumerate(((A18_SET, A18_TYPE, A18_AT),
                                                     (A17_SET, A17_TYPE, A17_AT)), start=ENEMY_18):
            at = items[k]
            self.assertEqual(u32(rom, at), ENEMY_FACTORY, f"item {k}")
            self.assertEqual(u32(rom, at + F.ITEM_COND), COND_NEVER_AT_LOAD,
                             f"item {k} must NOT exist until its own ext 104 builds it")
            self.assertEqual(u32(rom, at + F.ITEM_TYPE), type_id)
            self.assertEqual(u32(rom, at + F.ITEM_SET), set_id)
            self.assertEqual(struct.unpack_from("<hh", rom, at + F.ITEM_AT), spot)

    def test_the_npc_future_gohan_item_is_dropped(self):
        """The owner, 2026-11-07: "gohan has still not been removed". He stood in the street at
        (216,368) doing nothing while Trunks fought. Nothing drives him: no op in the whole ending
        span rom:0x3B7B08 to rom:0x3B8140 names set 54, and his step struct only parks him."""
        rom = built()["rom"]
        npcs = clone_items(rom)[:ENEMY_18]
        self.assertNotIn(GOHAN_SET, [u32(rom, at + F.N_SET) for at in npcs])
        self.assertNotIn(GOHAN_AT, [struct.unpack_from("<hh", rom, at + F.N_AT) for at in npcs])
        self.assertNotIn(GOHAN_SET, [u32(rom, at + F.ITEM_SET)
                                     for at in clone_items(rom)[ENEMY_18:]])

    def test_the_npc_trunks_item_is_dropped(self):
        """The player replaces him. Two actors of one set would make every op that names set 132 or 133
        ambiguous, and the record that turns the player Super Saiyan names set 133."""
        rom = built()["rom"]
        sets = [u32(rom, at + F.N_SET) for at in clone_items(rom)[:ENEMY_18]]
        self.assertNotIn(TRUNKS_BASE, sets)
        self.assertNotIn(TRUNKS_SSJ, sets)

    def test_only_android_17_watches_the_player(self):
        """The owner: "17 will face the player like Cell did in the cell jr fight". The step does not
        run while a scene plays and it reads the live player, so 17 may turn again once he has control."""
        rom = built()["rom"]
        items = clone_items(rom)
        step = u32(rom, items[NPC_17] + F.N_STEP) - ROM_BASE
        self.assertEqual(rom[step:step + len(FACE_PLAYER)], FACE_PLAYER)
        other = u32(rom, items[NPC_18] + F.N_STEP) - ROM_BASE
        self.assertNotEqual(rom[other:other + len(FACE_PLAYER)], FACE_PLAYER, "item 0")

    def test_each_enemy_owns_a_FRESH_event_struct(self):
        """A death table written into a shared struct would change the main game's own Android fight."""
        rom = built()["rom"]
        items = clone_items(rom)
        vanilla_events = {F.TEMPLATES[s][2] for s in F.TEMPLATES}
        vanilla_tails = {F.TEMPLATES[s][4] for s in F.TEMPLATES}
        for k in (ENEMY_18, ENEMY_17):
            event = u32(rom, items[k] + F.ITEM_EVENT) - ROM_BASE
            tail = u32(rom, items[k] + F.ITEM_TAIL) - ROM_BASE
            self.assertNotIn(event, vanilla_events, f"item {k} reuses a vanilla event struct")
            self.assertNotIn(tail, vanilla_tails, f"item {k} reuses a vanilla step struct")
            self.assertEqual(u32(rom, event), EVENT_RUNNER)


class Records(unittest.TestCase):
    def test_word_0_loads_the_clone_with_a_player_on_it(self):
        """ext 39, never ext 35: only ext 38 and ext 39 reach the player constructor, which is why the
        vanilla ending had no player at all. The form and the leader go in FRONT of the load."""
        rom = built()["rom"]
        got = body(rom, 0)
        self.assertEqual(got[-len(ARRIVE_TAIL):], ARRIVE_TAIL)
        self.assertEqual(got[0], (49, (42,)), "the record still opens on vanilla's own music(42)")
        self.assertNotIn((35, (1, 2, 1, 384, 552)), got, "the vanilla map 1,2 load must be gone")
        self.assertEqual([op for op, _ in got].count(39), 1, "exactly one player-building load")

    def test_word_0_drives_the_player_and_not_the_removed_npc(self):
        """Only the three ops that ran on map 1,2 change. The six that walk NPC 132 around map 6,23,
        before the fade, are a different map and stay vanilla."""
        rom = built()["rom"]
        got = body(rom, 0)
        after = got[[op for op, _ in got].index(39):]
        self.assertFalse([a for a in after if TRUNKS_BASE in a[1] and a[0] != 73],
                         f"an op after the load still names set {TRUNKS_BASE}: {after}")
        self.assertIn((33, (PLAYER,)), after)
        self.assertIn((53, (PLAYER,) + TRUNKS_SPOT), after)

    def test_word_0_reveals_itself_because_ext_39_does_not(self):
        """ext 35 faded in by itself; ext 39's handler has no such call, so the copy must fade in, and
        the camera park that frames the reveal must come first and under the black."""
        rom = built()["rom"]
        got = body(rom, 0)
        load = [op for op, _ in got].index(39)
        rest = [op for op, _ in got[load:]]
        self.assertIn(41, rest, "the record must fade in")
        self.assertLess(rest.index(31), rest.index(41), "the camera parks before the fade in")
        self.assertLess(rest.index(69), rest.index(31), "the load settles before the camera moves")

    def test_no_actor_op_sits_between_the_load_and_the_settle(self):
        """ext 35 blocked until its load was done, so vanilla could face its NPC straight after it.
        ext 39 does not block, so an actor op in that gap runs before the player exists and is wiped."""
        got = body(built()["rom"], 0)
        load = [op for op, _ in got].index(39)
        self.assertEqual(got[load + 1], (69, (120,)),
                         f"the op after the load must be the settle wait, not {got[load + 1]}")

    def test_word_4_changes_the_players_body_instead_of_swapping_npcs(self):
        """sub_0800A8EC writes the new set into the character record and then, when the live player
        object pointer is not null, rebuilds that object. remove(132) could not stay: the player's own
        appearance set is 132 here, so the record would have deleted him."""
        rom = built()["rom"]
        self.assertEqual(body(rom, 4), TRANSFORM_OPS)
        self.assertNotIn((52, (TRUNKS_BASE,)), body(rom, 4))
        self.assertNotIn((51, (TRUNKS_SSJ, 496, 504)), body(rom, 4))
        got = [op for op, _ in body(rom, 4)]
        self.assertLess(got.index(57), got.index(73),
                        "the pose must come first: ext 57 blocks for the whole of state 9, and set 133"
                        " has no anim 9, so a swap during the state would leave the power up no frames")
        self.assertNotIn((46, (23,)), body(rom, 4),
                         "state 9 plays sound 23 itself when it ends, so vanilla's closing sound(23)"
                         " would ping it twice")

    def test_word_6_turns_the_player(self):
        self.assertEqual(body(built()["rom"], 6), NAME_OPS)

    def test_words_8_and_11_are_the_four_op_battle_start(self):
        """No fade, no map load, no wait and nobody placed: word 0 settled the form, the leader, the
        spots and the camera. The bar is ext 85, not ext 90, because each android is one round."""
        rom = built()["rom"]
        self.assertEqual(body(rom, 8), FIGHT18_OPS)
        self.assertEqual(body(rom, 11), FIGHT17_OPS)
        for word in (8, 11):
            rec = u32(rom, TABLE + 4 * word) - ROM_BASE
            self.assertEqual(rom[rec], END_INDEX, f"word {word} hands control back")
            self.assertFalse([op for op, _ in body(rom, word) if op in (35, 38, 39, 40, 41, 69)],
                             f"word {word} must carry no load, no fade and no wait")

    def test_the_two_fights_name_different_enemies_and_different_items(self):
        """Two individual fights, not one fight with two enemies: each ext 104 builds its own item."""
        rom = built()["rom"]
        self.assertEqual(body(rom, 8)[0], (104, (A18_SET, ENEMY_18)))
        self.assertEqual(body(rom, 11)[0], (104, (A17_SET, ENEMY_17)))


class DeathTables(unittest.TestCase):
    def test_each_table_is_the_LIVE_ending_table_with_its_own_word_0(self):
        """Taken after words 8 and 11 are written, so Android 18's table carries the REAL Android 17
        fight at word 11, not the vanilla beating whose attacker is an NPC that no longer exists. It
        also carries ending_fight's own words 13 and 23, so the Cell sequence follows on."""
        rom = built()["rom"]
        ending = [u32(rom, TABLE + 4 * k) for k in range(TABLE_WORDS)]
        for set_id in (A18_SET, A17_SET):
            table = built()["notes"]["tables"][set_id]
            mine = [u32(rom, table + 4 * k) for k in range(TABLE_WORDS)]
            self.assertEqual(mine[1:], ending[1:], f"set {set_id}")
            self.assertNotEqual(mine[0], ending[0])
            self.assertEqual(mine[11], ending[11], "the real Android 17 fight")
            self.assertEqual(mine[13], ending[13], "ending_fight's arena load")
            self.assertEqual(mine[23], ending[23], "ending_fight's Imperfect Cell fight")
            self.assertEqual(mine[END_INDEX], 0, "word 26 still ends the scene")

    def test_each_death_record_hands_back_to_the_right_cutscene_word(self):
        """18 at word 9 ("It can't be!") and 17 at word 12 ("Now there's just one more thing")."""
        rom = built()["rom"]
        for set_id, nxt, entrance in ((A18_SET, AFTER18, A17_SET), (A17_SET, AFTER17, None)):
            rec = built()["notes"]["deaths"][set_id]
            self.assertEqual(rom[rec], nxt, f"set {set_id}")
            self.assertEqual(record_ops(rom, rec), death_ops(set_id, entrance), f"set {set_id}")

    def test_each_death_record_removes_its_own_beaten_android(self):
        """Both types keep the BOSS death descriptor, which leaves a beaten boss standing at HP 0, so
        the record poses him down, holds, and the blast is what removes him."""
        rom = built()["rom"]
        for set_id in (A18_SET, A17_SET):
            ops = ext_sequence(rom, built()["notes"]["deaths"][set_id])
            self.assertIn((52, (set_id,)), ops)
            other = A17_SET if set_id == A18_SET else A18_SET
            self.assertNotIn((52, (other,)), ops, "a death record must not remove the other android")

    def test_neither_death_record_transitions(self):
        """The owner's emphasis: "she collapses -> Trunks blasts her, NO transition". So no fade, no
        flash, no camera move, no camera hand-off, no map load and no teleport, in either record."""
        rom = built()["rom"]
        for set_id in (A18_SET, A17_SET):
            used = {n for n, _ in ext_sequence(rom, built()["notes"]["deaths"][set_id])}
            self.assertFalse(used & set(NO_TRANSITION_OPS),
                             f"set {set_id}'s death record transitions: {sorted(used & set(NO_TRANSITION_OPS))}")

    def test_the_player_is_the_one_who_blasts_each_android(self):
        """ext 96 with the PLAYER as attacker is vanilla: rom:0x3E5224 fires attack(0, 28, 100) three
        times and polls ext 60 (28). ext 60 names the same android the attack named, because a blast
        aimed at X can never end an ext 60 (Y)."""
        rom = built()["rom"]
        for set_id in (A18_SET, A17_SET):
            ops = ext_sequence(rom, built()["notes"]["deaths"][set_id])
            self.assertIn((96, (PLAYER, set_id, BLAST_SPEED)), ops, f"set {set_id} is not blasted")
            self.assertIn((60, (set_id,)), ops, f"set {set_id}'s blast is never waited on")
            self.assertIn((56, (PLAYER, set_id)), ops, "Trunks must turn to her before he fires")

    def test_only_android_18s_record_branches_on_the_players_spot(self):
        """18's record carries exactly two jz: one for "he is already beside Trunks" and one for "his
        drawn box has no pixel on screen". 17's own record is the last beat before the vanilla fade
        at word 13 and needs neither."""
        rom = built()["rom"]
        jumps18 = [op for _, op, _ in raw_ops(rom, built()["notes"]["deaths"][A18_SET] + 3)
                   if op in (JZ, 18, 28)]
        self.assertEqual(jumps18, [JZ, JZ], "two branches, both jz: the talk box and the view")
        jumps17 = [op for _, op, _ in raw_ops(rom, built()["notes"]["deaths"][A17_SET] + 3)
                   if op in (JZ, 18, 28)]
        self.assertEqual(jumps17, [], "Android 17's own death record must not branch")

    def test_each_jz_skips_exactly_its_own_arm(self):
        """The outer jz must land on the face ops and the inner one on the walk, so a 17 who is
        already beside Trunks moves at all and a visible 17 is never teleported."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        body = raw_ops(rom, rec + 3)
        spots = [at for at, _, _ in body]
        outer, inner = [i for i, (_, op, _) in enumerate(body) if op == JZ]
        after_outer = spots.index(body[outer][2])
        after_inner = spots.index(body[inner][2])
        enter = _push(A17_SET) + screen_x_ops(CAM_X + ENTRY_INSET, -ENTRY_INSET) + _ext(V_PY) + _ext(62)
        self.assertEqual([(op, arg) for _, op, arg in body[inner + 1:after_inner]], enter,
                         "the inner jz must skip the ext 62 reposition and nothing else")
        self.assertEqual([(op, arg) for _, op, arg in body[after_outer:after_outer + 2]],
                         _ext(56, A17_SET, PLAYER),
                         "every path must end by facing Android 17 at the player")

    def test_the_approach_decides_and_lands_the_way_the_geometry_says(self):
        """RUNS the arithmetic, it does not read the bytes. Every expected value is written out from
        the geometry: he stops at max(px - 40, 72) on the player's own row and enters at
        max(px - 136, -24), and the teleport runs only from inside the GONE band."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        qx, qy = A17_SPOT
        cases = ((qx, qy, False, False, "standing on 17"),
                 (qx + TALK_X, qy, False, False, "on the right edge of the talk box"),
                 (qx + TALK_X + 1, qy, True, False, "one px outside it, and still on screen"),
                 (qx - TALK_X - 1, qy, True, False, "one px outside it on the left"),
                 (qx, qy + TALK_Y, False, False, "on the bottom edge of the talk box"),
                 (qx, qy + TALK_Y + 1, True, False, "one px below it, and still on screen"),
                 (GONE_X[0] - 1, qy, True, True, "one px past the left edge of the view"),
                 (GONE_X[1] + 1, qy, True, True, "one px past the right edge of the view"),
                 (qx, GONE_Y[0] - 1, True, True, "one px above the top edge of the view"),
                 (qx, GONE_Y[1] + 1, True, True, "one px below the bottom edge of the view"),
                 (104, 504, True, True, "against the left map edge, where the camera clamps"),
                 (496, 504, True, True, "the talk spot, where the fight starts"),
                 (496, 648, True, True, "the player start"))
        for px, py, want_walk, want_entry, why in cases:
            run = run_branch(rom, rec, (px, py))
            self.assertEqual(run["walked"], want_walk, f"({px},{py}) {why}: walked")
            self.assertEqual(run["left"], 0,
                             f"({px},{py}) left {run['left']} value(s) on the stack: op 17 would turn"
                             f" one of them into the next table index")
            if want_walk:
                stop = (max(px - CAM_X + STOP_INSET, STOP_INSET) if want_entry
                        else px - 40 + SIDE_STEP * (px < A17_SPOT[0]))
                self.assertEqual(run["target"], (stop, py),
                                 f"({px},{py}) {why}: the ext 144 target")
            else:
                self.assertIsNone(run["target"], f"({px},{py}) {why}: nobody should walk")
            if want_entry:
                self.assertEqual(run["entry"], (max(px - CAM_X - ENTRY_INSET, -ENTRY_INSET), py),
                                 f"({px},{py}) {why}: the ext 62 entry")
            else:
                self.assertIsNone(run["entry"], f"({px},{py}) {why}: nobody should be repositioned")

    def test_17_is_never_repositioned_where_anyone_could_see_it(self):
        """The whole point of the ext 62. Over EVERY open cell of map 1,100 the entry must be at
        least his own half width outside the left edge of the view, the stop must be inside it with
        room for his sprite, and the arm that walks him from his own spot must not take him THROUGH
        Trunks. The camera is the player minus (112,80) held inside the map, which three capture
        runs confirm in RAM: 0x0300109C and 0x030010A0 read (384,435), (0,489) and (384,297) with
        the player at (496,515), (16,569) and (496,377)."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        entry = P.map_entry(rom, CLONE_ZONE, CLONE_AREA)[1]
        layout = P.layouts(rom, entry)[0]
        width, height = P.map_bounds(rom, layout)
        _, _, bits = P.collision_bits(rom, layout)
        seen, off_view, through, cells, walks_himself = [], [], [], 0, 0
        for y in range(0, 2048, 8):
            for x in range(0, 2048, 8):
                if not P.is_open(bits, x, y):
                    continue
                cells += 1
                run = run_branch(rom, rec, (x, y))
                cam = (min(max(x - CAM_X, 0), width - SCREEN_W),
                       min(max(y - CAM_Y, 0), height - SCREEN_H))
                if run["entry"] and run["entry"][0] + A17_HALF_W > cam[0]:
                    seen.append((x, y))
                if run["walked"] and not (cam[0] + A17_HALF_W <= run["target"][0]
                                          <= cam[0] + SCREEN_W - A17_HALF_W):
                    off_view.append((x, y))
                if run["walked"] and run["entry"] is None:
                    walks_himself += 1
                    start, stop = A17_SPOT, run["target"]
                    steps = max(abs(stop[0] - start[0]), abs(stop[1] - start[1])) or 1
                    if any(abs(start[0] + (stop[0] - start[0]) * t // steps - x) <= A17_HALF_W + 4
                           and abs(start[1] + (stop[1] - start[1]) * t // steps - y) <= A17_TOP // 2
                           for t in range(0, steps + 1, 4)):
                        through.append((x, y))
        self.assertGreater(cells, 5000, "the collision frame must really have been read")
        self.assertGreater(walks_himself, 100,
                           "the arm that walks him from his own spot must really be reached")
        self.assertEqual(seen, [], f"{len(seen)} cells show the reposition, first {seen[:1]}")
        self.assertEqual(off_view, [], f"{len(off_view)} cells stop him outside the view")
        self.assertEqual(through, [], f"{len(through)} cells walk him through Trunks, first {through[:1]}")

    def test_the_geometry_is_what_decides_and_not_something_else(self):
        """A negative control, because a green branch test proves nothing on its own. Moving the
        BOTTOM edge of the view out to 8000 IN THE BUILT BYTES must stop the talk spot teleporting,
        while he still walks. 487 and 8000 both zigzag into two varint bytes, so no later op moves."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        self.assertIsNotNone(run_branch(rom, rec, (496, 504))["entry"], "the talk spot teleports")
        old, new = bytes([29, 1]) + zigzag(GONE_Y[1]), bytes([29, 1]) + zigzag(8000)
        self.assertEqual(len(old), len(new), "the control must not move any later op")
        mutant = bytearray(rom)
        at = rom.index(old, rec, rec + 0x100)
        mutant[at:at + len(old)] = new
        run = run_branch(bytes(mutant), rec, (496, 504))
        self.assertIsNone(run["entry"], "a view 8000 px tall must leave him where he stands")
        self.assertTrue(run["walked"], "he must still walk: only the view test moved")

    def test_android_17s_own_death_record_runs_clean_too(self):
        """It has no branch, so the only thing to run is the stack: it must end empty."""
        rom = built()["rom"]
        run = run_branch(rom, built()["notes"]["deaths"][A17_SET], (496, 504))
        self.assertEqual(run["left"], 0)
        self.assertFalse(run["walked"])

    def test_the_view_test_reads_the_player_and_17s_real_spot(self):
        """17 never moves off his item spot, so the question is only where the player is. ext 143
        reads the PLAYER, and every bound in the record is derived from 17's own item spot."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        ops = ext_sequence(rom, rec)
        self.assertIn((143, (PLAYER,)), ops, "the test must read the PLAYER's spot")
        values = {v for _, op, arg in raw_ops(rom, rec + 3) if op == 29 for v in arg}
        for want, name in ((GONE_X[0], "the left edge of the view"),
                           (GONE_X[1], "the right edge of the view"),
                           (GONE_Y[0], "the top edge of the view"),
                           (GONE_Y[1], "the bottom edge of the view"),
                           (A17_SPOT[0] - TALK_X, "the left edge of the talk box"),
                           (A17_SPOT[1] + TALK_Y, "the bottom edge of the talk box")):
            self.assertIn(want, values, name)
        self.assertEqual(A17_SPOT, struct.unpack_from("<hh", rom, clone_items(rom)[NPC_17] + F.N_AT),
                         "A17_SPOT must be the spot the clone's own NPC item carries")

    def test_nothing_in_the_ending_ever_jumps_to_word_0(self):
        """Word 0 of a death table is the death record, so an index 0 anywhere would run it again."""
        rom = built()["rom"]
        for k in range(TABLE_WORDS - 1):
            word = u32(rom, TABLE + 4 * k)
            if word:
                self.assertNotEqual(rom[word - ROM_BASE], 0, f"record of word {k} points at index 0")


class Sites(unittest.TestCase):
    def test_every_base_write_is_declared_and_expected(self):
        """The base writes are the five ending words, the four map table literals and the count byte.
        The literals and the count byte are the one overlap with battle_arena, by design."""
        b = built()
        expected = {TABLE + 4 * k for k in EDITED} | set(F.BASE_LITERALS) \
            | {F.ENTRY3_LITERAL, F.MAP_COUNT_BYTE}
        wrote = {at for at, _, _ in b["notes"]["sites"] if at < 0x800000}
        self.assertEqual(wrote, expected)

    def test_nothing_outside_the_expansion_area_changed_beyond_those_sites(self):
        b = built()
        allowed = set()
        for at, n, _ in b["notes"]["sites"]:
            allowed.update(range(at, at + n))
        changed = [i for i in range(0x800000) if b["rom"][i] != b["before"][i]]
        self.assertTrue(changed)
        self.assertFalse(set(changed) - allowed, f"undeclared writes: {changed[:16]}")


if __name__ == "__main__":
    unittest.main()
