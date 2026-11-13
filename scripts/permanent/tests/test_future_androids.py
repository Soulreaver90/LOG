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
import log_paths
from patches import future_androids as F
from scene import scene_probe as P
from scene.scene_lib import record_end, words_naming, zigzag
from tests.test_cellgames_ssj import ext_sequence, ops as raw_ops

# ===== constants (the brief, the owner's words, and the base reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_future.txt"
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
NO_BANNER, MUSIC_SCRIPT = 0xDD, 0x083ED73C
# The track Gohan flies home on, and the one that must now carry unbroken into the ending.
# The Dende farewell rom:0x3DCEDC opens with music(18), sets flag 196, and then loads nine maps
# whose +0x24 scripts all return 18 while that flag is set. See the module's WALK_IN_MUSIC.
FAREWELL_AT, FAREWELL_MUSIC, WALK_IN_MUSIC = 0x3DCEDC, 18, 42
ANDROID_THEME = 38                                # record 0's own closing cue, untouched vanilla
OPENING_THEME = 42                                # record 0's opening cue, reverted to vanilla
MUSIC_OP, LOAD_READS_0X24 = 49, (38, 39)          # ext 35 never reads +0x24 (bible B1554)
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
SPARK_AT, BOOM, SPARK_HOLD = (0, 0), 31, 12   # ext 94's offset, the poof sound, the hold before the remove
CAM_X, CAM_Y = 112, 80                        # the follow camera's offset, READ OUT OF RAM, not assumed
SCREEN_W, SCREEN_H = 240, 160
ENTRY_INSET, STOP_REACH = 24, 40
A17_HALF_W, A17_TOP = 8, 32                   # his drawn box, from his anchor
ENTRY_WEST, ENTRY_EAST = -ENTRY_INSET, SCREEN_W + ENTRY_INSET          # -24, 264, from the camera
ENTRY_MID, ENTRY_SWING = (ENTRY_EAST + ENTRY_WEST) // 2, (ENTRY_EAST - ENTRY_WEST) // 2
ENTRY_UP = SCREEN_H + A17_TOP - CAM_Y + ENTRY_INSET   # 136: one constant for both signs, so it takes
#                                                      the stricter one, which is entering from the south
# The player spots from which 17's drawn box has NO pixel on screen. This is the WHOLE test now:
# inside it he speaks where he stands. Restated from the geometry, not imported: his box spans
# x 512-528 and y 376-408, and the view is the player minus (112,80).
GONE_X = (A17_SPOT[0] - A17_HALF_W - SCREEN_W + CAM_X + 1, A17_SPOT[0] + A17_HALF_W + CAM_X - 1)
GONE_Y = (A17_SPOT[1] - A17_TOP - SCREEN_H + CAM_Y + 1, A17_SPOT[1] + CAM_Y - 1)
VERT_BAND, VERT_GAP = (440, 700), (440, 520)  # where a vertical approach is rejected, and the way through
HALF = 1 << 16
V_SPOT, V_PY, V_PX, V_HX = 0, 1, 2, 3         # scene variables: set_var n writes 0x03001FB0 + 4n
JZ, END_OP = 19, 17
# No death record may carry one of these: a camera move, a camera hand-off, a map load or a fade.
# "NO transition" is the owner's emphasis and this is the list that enforces it. ext 62 is NOT
# on the list: it is the reposition that puts 17 outside the left edge of the view, it runs only when
# his drawn box has no pixel on screen, and its command writes nothing but +0x158/+0x15C
# (`sub_0800A44E`, start `@0x0800E1DC`, done `@0x08026498` = `mov r0,#1 ; bx lr`).
# ext 42 and ext 43 LEFT this list on 2026-11-09, when the owner asked for the explosion's white
# flash by name. They are not unguarded: the test below allows the pair ONLY as the explosion's own
# cover, wrapped around the remove, so a stray flash anywhere else in these records still fails.
NO_TRANSITION_OPS = (31, 33, 35, 38, 39, 40, 41)
BOOM_FLASH, BOOM_FLASH_WAIT = 5, 5            # celljr's own pair; NOT the transform's FLASH of 10


def _push(*vals):
    """The push op the encoder emits: base op 0 for one small byte, base op 29 otherwise."""
    if len(vals) == 1 and 0 <= vals[0] <= 0xFF:
        return [(0, [vals[0]])]
    return [(29, list(vals))]


def _ext(n, *vals):
    return (_push(*vals) if vals else []) + [(2, n)]


def blast_ops(enemy_set):
    """Trunks turns to the body, fires ext 96 as the PLAYER, ext 60 waits for the hit, the body blows up."""
    return (_ext(56, PLAYER, enemy_set) + _ext(63)
            + _ext(96, PLAYER, enemy_set, BLAST_SPEED) + _ext(60, enemy_set) + _ext(64)
            + explode_ops(enemy_set))


def explode_ops(enemy_set):
    """The spark, the poof sound, a hold, then the white flash that covers the remove.

    celljr_fight's own `_explode()` with ONE thing added: the `ext 69` hold stays in front of the
    flash, so the spark plays in the clear for its 12 frames before the screen goes white."""
    return (_ext(94, enemy_set, *SPARK_AT) + _ext(46, BOOM) + _ext(69, SPARK_HOLD)
            + _ext(42, BOOM_FLASH) + _ext(52, enemy_set) + _ext(43, BOOM_FLASH_WAIT))


def read_player_ops():
    """ext 143 pushes the player's spot PACKED as (x << 16) | (y & 0xFFFF). Multiplying by 65536
    shifts the x half out in 32 bits, so one divide gives y; subtracting y and dividing again gives x."""
    return (_ext(143, PLAYER) + [(3, V_SPOT)]
            + _ext(V_SPOT) + _push(HALF) + [(9, None)] + _push(HALF) + [(10, None), (3, V_PY)]
            + _ext(V_SPOT) + _ext(V_PY) + [(8, None)] + _push(HALF) + [(10, None), (3, V_PX)])


def outside_ops(slot, lo, hi):
    """Leave 1 when variable `slot` is below `lo` or above `hi`. lt and gt test SECOND against TOP."""
    return _ext(slot) + _push(lo) + [(15, None)] + _ext(slot) + _push(hi) + [(13, None), (5, None)]


def cam_x_ops():
    """max(px - 112, 0), written as (px - 112) * (px > 112): no register and no jump."""
    return (_ext(V_PX) + _push(CAM_X) + [(8, None)]
            + _ext(V_PX) + _push(CAM_X) + [(13, None), (9, None)])


def sign_ops(slot, here):
    """1 - 2 * (value > here): +1 when 17's own spot is at or beyond the player on this axis."""
    return _push(1) + _push(2) + _ext(slot) + _push(here) + [(13, None), (9, None), (8, None)]


def horizontal_ops():
    """The approach axis. |dx| >= |dy| squared into (dx - dy) * (dx + dy) >= 0, OR the one measured
    window where a vertical approach would cross the band that narrows the street to x 440-520."""
    geometry = (_push(A17_SPOT[0] - A17_SPOT[1]) + _ext(V_PX) + [(8, None)] + _ext(V_PY) + [(7, None)]
                + _push(A17_SPOT[0] + A17_SPOT[1]) + _ext(V_PX) + [(8, None)] + _ext(V_PY) + [(8, None)]
                + [(9, None)] + _push(-1) + [(13, None)])
    blocked = (_ext(V_PY) + _push(VERT_BAND[0] - 1) + [(13, None)]
               + _ext(V_PY) + _push(VERT_BAND[1] + 1) + [(15, None), (4, None)]
               + _ext(V_PX) + _push(VERT_GAP[0]) + [(15, None)]
               + _ext(V_PX) + _push(VERT_GAP[1]) + [(13, None), (5, None), (4, None)])
    return geometry + blocked + [(5, None)]


def along_ops(slot, here, reach, horizontal_axis):
    """reach * sign * axis: the offset from the player along the chosen axis, or 0."""
    axis = _ext(V_HX) if horizontal_axis else _push(1) + _ext(V_HX) + [(8, None)]
    return _push(reach) + sign_ops(slot, here) + [(9, None)] + axis + [(9, None)]


def approach_ops(npc_set):
    """One test, the real view: inside it he speaks, outside it he is repositioned 24 px beyond the
    view's own edge on HIS side and walks 64 or 96 px in. Both face ops run on every path."""
    entry_x = (_ext(V_PX) + cam_x_ops() + _push(ENTRY_MID) + [(7, None)]
               + _push(ENTRY_SWING) + sign_ops(V_PX, A17_SPOT[0]) + [(9, None), (7, None)]
               + _ext(V_PX) + [(8, None)] + _ext(V_HX) + [(9, None), (7, None)])
    entry_y = _ext(V_PY) + along_ops(V_PY, A17_SPOT[1], ENTRY_UP, False) + [(7, None)]
    stop_x = _ext(V_PX) + along_ops(V_PX, A17_SPOT[0], STOP_REACH, True) + [(7, None)]
    stop_y = _ext(V_PY) + along_ops(V_PY, A17_SPOT[1], STOP_REACH, False) + [(7, None)]
    move = (horizontal_ops() + [(3, V_HX)]
            + _push(npc_set) + entry_x + entry_y + _ext(62)
            + _push(npc_set) + stop_x + _push(HALF) + [(9, None)] + stop_y + [(7, None)] + _ext(144))
    gone = outside_ops(V_PX, *GONE_X) + outside_ops(V_PY, *GONE_Y) + [(5, None)]
    return (read_player_ops() + gone + [(JZ, None)] + move
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
BINARY_32 = {4: lambda a, b: int(bool(a) and bool(b)),
             5: lambda a, b: int(bool(a) or bool(b)), 7: lambda a, b: a + b,
             8: lambda a, b: a - b, 9: lambda a, b: a * b,
             10: lambda a, b: int(a / b), 13: lambda a, b: int(a > b), 15: lambda a, b: int(a < b)}
# How many values each plain ext op in a death record pops, from docs\research\scene-vm-ext-ops.md.
EXT_ARITY = {42: 1, 43: 1, 46: 1, 52: 1, 55: 2, 56: 2, 57: 2, 60: 1, 63: 0, 64: 0, 69: 1,
             86: 1, 88: 0, 94: 3, 96: 3}


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


def _music_word(rom: bytes, word: int, flags: set) -> int:
    """The song a map's +0x24 resolves to: a literal under 0x10000, or the script it points at.

    `music_getter @0x0800EB58` does exactly this test: `ldr r1,[r0,#0x24] ; lsr r2,r1,#16 ; bne`,
    and on the non-zero arm it runs the scene VM on that pointer and takes [sp,#8]. The scripts in
    this chain are one shape, `push F ; test_flag ; jz 3 ; push A ; end ; push B ; end`."""
    if word < 0x10000:
        return word
    rows = raw_ops(rom, word - ROM_BASE)
    where = {at: k for k, (at, _op, _arg) in enumerate(rows)}
    stack, k = [], 0
    while k < len(rows):
        _at, op, arg = rows[k]
        k += 1
        if op in (0, 1, 29):
            stack += list(arg)
        elif op == 2 and arg == 19:                              # ext 19 test_flag
            stack = [1 if stack.pop() in flags else 0]
        elif op == 19:                                           # jz: pop, jump forward when zero
            k = where[arg] if not stack.pop() else k
        elif op == 17:
            return stack[-1] if stack else None
    raise AssertionError(f"the music script rom:0x{word - ROM_BASE:X} did not end")


def _farewell_songs(rom: bytes) -> tuple:
    """(the song every music cue and every +0x24-reading load of record 87 gives, the flags it sets).

    `ext 35` is left out on purpose: it never reads +0x24 (bible B1554). `neg` is honoured, because
    one of the loads builds its x with it and a decoder that drops it loses the load's arguments."""
    songs, flags, stack = [], set(), []
    for _o, op, arg in raw_ops(rom, FAREWELL_AT + 3):
        if op in (0, 1, 29):
            stack += list(arg)
        elif op == 6:                                            # neg
            stack.append(-stack.pop())
        elif op == 20:                                           # drop
            stack.pop()
        elif op == 2:
            args, stack = tuple(stack), []
            if arg == 27 and args:                               # ext 27 set_flag
                flags.add(args[0])
            elif arg == MUSIC_OP and args:
                songs.append(args[0])
            elif arg in LOAD_READS_0X24 and len(args) >= 2:
                entry = F.map_entry(rom, args[0], args[1])[1]
                songs.append(_music_word(rom, u32(rom, entry + F.F_MUSIC), flags))
        else:
            stack = []
    return songs, flags


class BuildOrder(unittest.TestCase):
    # What may run AFTER future_androids, and why each one is harmless. A module that relocates the
    # MAP table or writes an ending record must never be added here: it would undo this module.
    MAY_FOLLOW = {"pool_refill": "wraps the ext 73 table word; writes no map entry and no record"}

    def test_future_androids_runs_after_what_it_reads(self):
        """It appends to the table battle_arena moved, and ending_fight checks that words 0, 4, 6, 8
        and 11 are still vanilla when it runs. Either one out of order is a silent wrong build.

        This used to assert that the module ran LAST, which was the position it happened to hold and
        not the rule. Adding one harmless module after it failed a green suite for no defect."""
        order = built()["order"]
        self.assertLess(order.index("battle_arena"), order.index("future_androids"))
        self.assertLess(order.index("ending_fight"), order.index("future_androids"))
        after = order[order.index("future_androids") + 1:]
        unknown = [m for m in after if m not in self.MAY_FOLLOW]
        self.assertEqual(unknown, [], f"these run after future_androids and are not in MAY_FOLLOW,"
                                      f" so each one needs a reason: {unknown}")

    def test_the_two_masters_do_not_carry_this_module(self):
        for name in ("build_list.txt", "build_list_core.txt", "build_list_dev.txt"):
            names = log2_build.read_build_list(log_paths.BUILD_LISTS / name)
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
        """Vanilla type 4 also spawns on map 8,49 and vanilla type 3 on maps 11,4, 11,5 and 11,6, so
        the FUTURE androids get fresh entries and neither vanilla row is touched. The owner drew the
        line himself on 2026-11-07: "We do not touch any earlier 18 and 17 fights"."""
        b = built()
        for type_id, hp in ((A18_TYPE, A18_HP), (A17_TYPE, A17_HP)):
            at = F.ENEMY_TABLE + F.ENEMY_ENTRY * type_id
            self.assertEqual(b["rom"][at:at + F.ENEMY_ENTRY], b["base"][at:at + F.ENEMY_ENTRY])
            self.assertEqual(u32(b["rom"], at + 4), hp)
            self.assertEqual(u32(b["rom"], at + 8), ANDROID_AI)

    def test_each_future_android_has_its_own_weaker_type_entry(self):
        """The owner, 2026-11-08: "The stats for future 17 and 18 should be weaker than vanilla, that
        is actually canon ... Weaker stats, like 25%". 25 percent WEAKER, not 25 percent of vanilla.
        HP rounds onto a multiple of 10 and the three byte stats round half up. The AI id, the two
        damage factors and the BOSS death descriptor all stay: each death record poses the body down
        and removes it itself, which the normal descriptor would fight."""
        b = built()
        want = {A18_SET: (A18_TYPE, 2180, (22, 26, 20)), A17_SET: (A17_TYPE, 2660, (24, 29, 26))}
        self.assertEqual(sorted(b["notes"]["types"]), sorted(want))
        for set_id, (vanilla, hp, stats) in want.items():
            type_id = b["notes"]["types"][set_id]
            at = F.ENEMY_TABLE + F.ENEMY_ENTRY * type_id
            self.assertGreaterEqual(at, 0x800000, "a new type entry lives in the expansion area")
            self.assertEqual((at - F.ENEMY_TABLE) % F.ENEMY_ENTRY, 0, "it must sit on the table stride")
            new, old = b["rom"][at:at + F.ENEMY_ENTRY], F.TYPES[vanilla]
            self.assertEqual(u32(new, 4), hp, f"set {set_id} HP")
            self.assertEqual((new[0xC], new[0xD], new[0xE]), stats, f"set {set_id} STR, POW, END")
            for off in (0, 8, 0x10, 0x14):
                self.assertEqual(new[off:off + 4], old[off:off + 4], f"set {set_id} +0x{off:X}")
            self.assertEqual(u32(new, 8), ANDROID_AI, f"set {set_id} keeps AI 21")

    def test_the_main_game_android_enemy_items_still_name_the_vanilla_types(self):
        """Android 18's one vanilla spawn is map 8,49 item 0 and Android 17's four are map 11,4
        item 1, map 11,5 item 0 and map 11,6 items 0 and 4 (bible B2172). None may be retyped."""
        b = built()
        spawns = ((0x4033A4, A18_TYPE), (0x406494, A17_TYPE), (0x40657C, A17_TYPE),
                  (0x406654, A17_TYPE), (0x4066E4, A17_TYPE))
        for item, type_id in spawns:
            self.assertEqual(u32(b["rom"], item + F.ITEM_TYPE), type_id, f"rom:0x{item:X}")
            self.assertEqual(b["rom"][item:item + 0x20], b["base"][item:item + 0x20], f"rom:0x{item:X}")

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
        b = built()
        rom = b["rom"]
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
            self.assertEqual(u32(rom, at + F.ITEM_TYPE), b["notes"]["types"][set_id],
                             f"item {k} must name the FUTURE android's own weaker type, not"
                             f" vanilla type {type_id}, which the main game still spawns")
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
        self.assertNotIn((35, (1, 2, 1, 384, 552)), got, "the vanilla map 1,2 load must be gone")
        self.assertEqual([op for op, _ in got].count(39), 1, "exactly one player-building load")

    def test_the_opening_music_cue_is_back_to_vanilla(self):
        """REVERTED, and this test pins the revert so it is not quietly undone.

        The owner play-tested `future_v3.gba` on 2026-11-09: "You changed the wrong track, the
        opening is still there and plays over the music that plays when trunks walks to the time
        machine, that needs to be reverted."

        The attempt deleted record 0's opening `music(42)` and made the clone's +0x24 name 18. Both
        are now back to vanilla's numbers. **The attempt is not known to have been wrong about what
        it changed**, only about whether that was the track he hears, so this test asserts the
        vanilla state and nothing about the cause."""
        rom = built()["rom"]
        got = body(rom, 0)
        cues = [args[0] for op, args in got if op == MUSIC_OP]
        self.assertEqual(cues, [OPENING_THEME, ANDROID_THEME],
                         "record 0 opens with its vanilla cue and closes with the Android theme")
        self.assertEqual(WALK_IN_MUSIC, OPENING_THEME,
                         "the clone's +0x24 is vanilla's value again")
        self.assertEqual(u32(rom, clone(rom) + F.F_MUSIC), OPENING_THEME,
                         "and the built clone carries it")
        self.assertNotEqual(WALK_IN_MUSIC, FAREWELL_MUSIC,
                            "if these are equal again, the reverted change has come back")

    def test_the_farewell_really_is_playing_18_when_the_ending_starts(self):
        """Checked, not assumed: the whole farewell is read out of the built ROM.

        Record 87 opens with `music(18)` and sets flag 196 BEFORE its first map load. Every map it
        then loads carries a `+0x24` script of the shape `push F ; test_flag ; jz 3 ; push A ; end`,
        and with 196 set every one of them returns 18, so not one of those loads restarts the
        music. If any map in that chain returned something else, 18 would be the wrong number to
        name on the clone and this test is where that shows."""
        rom = built()["rom"]
        songs, flags = _farewell_songs(rom)
        self.assertEqual(songs[0], FAREWELL_MUSIC, "record 87 opens with music(18)")
        self.assertIn(196, flags, "and sets flag 196 before the loads that read it")
        self.assertEqual(set(songs), {FAREWELL_MUSIC},
                         f"every load in the farewell has to resolve to 18, got {songs}")

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

    def test_the_explosion_flashes_white_over_the_body(self):
        """The owner, 2026-11-09: "Yes the wolrd map and the flash".

        The pair has to WRAP the remove, or it covers nothing: `ext 42` takes the screen to white,
        the body goes while it is white, and `ext 43` brings it back. The hold stays in FRONT of the
        flash, so the spark is seen before the screen turns. Both lengths are celljr_fight's, which
        are vanilla seq 27's and which he has play tested."""
        rom = built()["rom"]
        for set_id in (A18_SET, A17_SET):
            ops = ext_sequence(rom, built()["notes"]["deaths"][set_id])
            names = [n for n, _ in ops]
            self.assertEqual(ops.count((42, (BOOM_FLASH,))), 1, f"set {set_id} flashes once")
            self.assertEqual(ops.count((43, (BOOM_FLASH_WAIT,))), 1, f"set {set_id} comes back once")
            # Every index is taken AFTER the spark: the death record holds an earlier ext 69, the
            # collapse hold, and an index() from the start of the record would find that one.
            spark = names.index(94)
            hold, flash, gone, back = (names.index(n, spark) for n in (69, 42, 52, 43))
            self.assertLess(spark, hold, "the spark comes first")
            self.assertLess(hold, flash, "and is held in the clear before the screen turns")
            self.assertLess(flash, gone, "the body goes UNDER the white")
            self.assertLess(gone, back, "and the screen comes back after it has gone")
            self.assertEqual(ops[flash:back + 1],
                             [(42, (BOOM_FLASH,)), (52, (set_id,)), (43, (BOOM_FLASH_WAIT,))],
                             "nothing else may run inside the flash")

    def test_neither_death_record_transitions(self):
        """The owner's emphasis: "she collapses -> Trunks blasts her, NO transition". So no fade, no
        camera move, no camera hand-off and no map load, in either record.

        The white flash is the ONE exception, added 2026-11-09 at his request, and it is checked on
        its own above: it may appear only as the explosion's cover, wrapped around the remove.

        ext 62 left that list when the approach gained its reposition, so Android 17's OWN record is
        checked for it by name here. Nothing in his record needs to move anybody, and an ext 62 that
        appeared there would be a teleport nobody branched on."""
        rom = built()["rom"]
        for set_id in (A18_SET, A17_SET):
            used = {n for n, _ in ext_sequence(rom, built()["notes"]["deaths"][set_id])}
            self.assertFalse(used & set(NO_TRANSITION_OPS),
                             f"set {set_id}'s death record transitions: {sorted(used & set(NO_TRANSITION_OPS))}")
        own = [op for _, op, arg in raw_ops(rom, built()["notes"]["deaths"][A17_SET] + 3)
               if op == 2 and arg == 62]
        self.assertEqual(own, [], "Android 17's own death record must carry no ext 62")

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
        """ONE branch now, and it is the real view. 17's own record is the last beat before the
        vanilla fade at word 13 and needs none."""
        rom = built()["rom"]
        jumps18 = [op for _, op, _ in raw_ops(rom, built()["notes"]["deaths"][A18_SET] + 3)
                   if op in (JZ, 18, 28)]
        self.assertEqual(jumps18, [JZ], "one branch, a jz: has his drawn box any pixel on screen")
        jumps17 = [op for _, op, _ in raw_ops(rom, built()["notes"]["deaths"][A17_SET] + 3)
                   if op in (JZ, 18, 28)]
        self.assertEqual(jumps17, [], "Android 17's own death record must not branch")

    def test_the_jz_skips_the_whole_approach(self):
        """When Android 17 is on screen the record must land on the face ops, so nothing moves him
        and no reposition can be seen by a player who has been looking straight at him."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        body = raw_ops(rom, rec + 3)
        at = next(i for i, (_, op, _) in enumerate(body) if op == JZ)
        after = [a for a, _, _ in body].index(body[at][2])
        skipped = [(op, arg) for _, op, arg in body[at + 1:after]]
        self.assertIn((2, 62), skipped, "the jz must skip the reposition")
        self.assertIn((2, 144), skipped, "the jz must skip the walk")
        self.assertEqual([(op, arg) for _, op, arg in body[after:after + 2]],
                         _ext(56, A17_SET, PLAYER),
                         "every path must end by facing Android 17 at the player")

    def test_the_approach_decides_and_lands_the_way_the_geometry_says(self):
        """RUNS the arithmetic. Every expected value is written out from the geometry here, not
        imported: the side is Android 17's own side on whichever axis separates him from Trunks the
        most, the vertical approach is rejected inside the measured window, and the entry sits 24 px
        beyond the view's own edge with the left camera clamp folded in."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        qx, qy = A17_SPOT

        def want(px, py):
            dx, dy = qx - px, qy - py
            horizontal = abs(dx) >= abs(dy) or (VERT_BAND[0] <= py <= VERT_BAND[1]
                                                and not VERT_GAP[0] <= px <= VERT_GAP[1])
            if horizontal:
                sx = 1 if dx >= 0 else -1
                return (max(px - CAM_X, 0) + ENTRY_MID + ENTRY_SWING * sx, py), (px + STOP_REACH * sx, py)
            sy = 1 if dy >= 0 else -1
            return (px, py + ENTRY_UP * sy), (px, py + STOP_REACH * sy)

        cases = ((qx, qy, "standing on his spot"),
                 (600, 430, "inside the view, to the south east of him"),
                 (GONE_X[0] - 1, qy, "one px past the left edge of the view"),
                 (GONE_X[1] + 1, qy, "one px past the right edge of the view"),
                 (qx, GONE_Y[0] - 1, "one px above the top edge of the view"),
                 (qx, GONE_Y[1] + 1, "one px below the bottom edge of the view"),
                 (700, 408, "due east of him, so he comes from the west"),
                 (300, 408, "due west of him, so he comes from the east"),
                 (470, 700, "due south in the gap column, so he comes from the north"),
                 (470, 264, "due north in the gap column, so he comes from the south"),
                 (300, 600, "south west, but the vertical approach is rejected"),
                 (104, 504, "against the left map edge, where the camera clamps"),
                 (496, 515, "where the capture runs finish the fight"))
        for px, py, why in cases:
            run = run_branch(rom, rec, (px, py))
            visible = GONE_X[0] <= px <= GONE_X[1] and GONE_Y[0] <= py <= GONE_Y[1]
            self.assertEqual(run["left"], 0,
                             f"({px},{py}) left {run['left']} value(s) on the stack: op 17 would turn"
                             f" one of them into the next table index")
            if visible:
                self.assertFalse(run["walked"], f"({px},{py}) {why}: he is on screen, so he speaks")
                self.assertIsNone(run["entry"], f"({px},{py}) {why}: nothing may move him")
                continue
            entry, stop = want(px, py)
            self.assertEqual(run["entry"], entry, f"({px},{py}) {why}: the ext 62 entry")
            self.assertEqual(run["target"], stop, f"({px},{py}) {why}: the ext 144 stop")

    def test_the_arms_and_the_sides_over_every_open_cell(self):
        """The whole-map proof, and the three things the owner's v9 session turned into rules.

        1. He speaks on EVERY cell where his drawn box has a pixel on screen, and only there.
        2. The reposition is never inside the view, and the stop always is, on both axes.
        3. All four sides are chosen somewhere, so the geometry is really being read.

        The camera is the player minus (112,80) held inside the map, which three capture dumps
        confirm in RAM: 0x0300109C and 0x030010A0 read (384,435), (0,489) and (384,297) with the
        player at (496,515), (16,569) and (496,377)."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        entry_at = P.map_entry(rom, CLONE_ZONE, CLONE_AREA)[1]
        layout = P.layouts(rom, entry_at)[0]
        width, height = P.map_bounds(rom, layout)
        _, _, bits = P.collision_bits(rom, layout)
        seen, off_view, wrong_arm, sides, cells = [], [], [], {}, 0
        for y in range(0, 2048, 8):
            for x in range(0, 2048, 8):
                if not P.is_open(bits, x, y):
                    continue
                cells += 1
                run = run_branch(rom, rec, (x, y))
                visible = GONE_X[0] <= x <= GONE_X[1] and GONE_Y[0] <= y <= GONE_Y[1]
                if visible != (not run["walked"]):
                    wrong_arm.append((x, y))
                if not run["walked"]:
                    continue
                cam = (min(max(x - CAM_X, 0), width - SCREEN_W),
                       min(max(y - CAM_Y, 0), height - SCREEN_H))
                e, t = run["entry"], run["target"]
                # His box spans x anchor-8..anchor+8 and y anchor-32..anchor, so ANY pixel of it is
                # on screen when the anchor is inside these two open ranges.
                inside = (cam[0] - A17_HALF_W < e[0] < cam[0] + SCREEN_W + A17_HALF_W
                          and cam[1] < e[1] < cam[1] + SCREEN_H + A17_TOP)
                if inside:
                    seen.append((x, y))
                if not (cam[0] + A17_HALF_W <= t[0] <= cam[0] + SCREEN_W - A17_HALF_W
                        and cam[1] + A17_TOP <= t[1] <= cam[1] + SCREEN_H):
                    off_view.append((x, y))
                side = ("E" if t[0] > x else "W") if t[1] == y else ("S" if t[1] > y else "N")
                sides[side] = sides.get(side, 0) + 1
        self.assertGreater(cells, 5000, "the collision frame must really have been read")
        self.assertEqual(wrong_arm, [], f"{len(wrong_arm)} cells take the wrong arm, first {wrong_arm[:1]}")
        self.assertEqual(seen, [], f"{len(seen)} cells show the reposition, first {seen[:1]}")
        self.assertEqual(off_view, [], f"{len(off_view)} cells stop him outside the view")
        self.assertEqual(set(sides), {"N", "S", "E", "W"},
                         f"the geometry must choose every side somewhere, not {sides}")

    def test_the_view_is_what_decides_and_not_something_else(self):
        """A negative control, because a green branch test proves nothing on its own. Moving the
        BOTTOM edge of the view out to 8000 IN THE BUILT BYTES must turn a cell that walks him in
        into one that leaves him standing. 487 and 8000 both zigzag into two varint bytes, so no
        later op moves."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        self.assertTrue(run_branch(rom, rec, (496, 504))["walked"], "the talk spot walks him in")
        old, new = bytes([29, 1]) + zigzag(GONE_Y[1]), bytes([29, 1]) + zigzag(8000)
        self.assertEqual(len(old), len(new), "the control must not move any later op")
        mutant = bytearray(rom)
        at = rom.index(old, rec, rec + 0x100)
        mutant[at:at + len(old)] = new
        run = run_branch(bytes(mutant), rec, (496, 504))
        self.assertFalse(run["walked"], "a view 8000 px tall must leave him where he stands")
        self.assertIsNone(run["entry"], "and must move nobody")

    def test_android_17s_own_death_record_runs_clean_too(self):
        """It has no branch, so the only thing to run is the stack: it must end empty."""
        rom = built()["rom"]
        run = run_branch(rom, built()["notes"]["deaths"][A17_SET], (496, 504))
        self.assertEqual(run["left"], 0)
        self.assertFalse(run["walked"])

    def test_the_view_test_reads_the_player_and_17s_real_spot(self):
        """17 never moves off his item spot, so the question is only where the player is. ext 143
        reads the PLAYER, and every bound in the record is derived from 17's own item spot or from
        the one measured collision window."""
        rom = built()["rom"]
        rec = built()["notes"]["deaths"][A18_SET]
        ops = ext_sequence(rom, rec)
        self.assertIn((143, (PLAYER,)), ops, "the test must read the PLAYER's spot")
        values = {v for _, op, arg in raw_ops(rom, rec + 3) if op in (0, 1, 29) for v in arg}
        for want, name in ((GONE_X[0], "the left edge of the view"),
                           (GONE_X[1], "the right edge of the view"),
                           (GONE_Y[0], "the top edge of the view"),
                           (GONE_Y[1], "the bottom edge of the view"),
                           (A17_SPOT[0] - A17_SPOT[1], "the dx minus dy constant"),
                           (A17_SPOT[0] + A17_SPOT[1], "the dx plus dy constant"),
                           (VERT_BAND[0] - 1, "the top of the vertical reject window"),
                           (VERT_BAND[1] + 1, "the bottom of it"),
                           (VERT_GAP[0], "the west side of the way through"),
                           (VERT_GAP[1], "the east side of it")):
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
