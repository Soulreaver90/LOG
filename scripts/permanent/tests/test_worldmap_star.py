r"""
test_worldmap_star.py - Capsule Corp carries the GOAL star on the world map once the main story
                        is over.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_worldmap_star.py -v

Builds build_list_trial_plateau.txt in memory once, and the same list WITHOUT this module, so every
claim is a difference between two ROMs instead of a repeat of the module's own arithmetic.

The strongest test here is test_the_copy_is_the_vanilla_script_with_the_insert_spliced_in. It is a
byte for byte splice, so it proves in one assertion that the other twelve places on the world map
keep their exact bytes, that every jump offset is unchanged, and that the insert lands in exactly
one place. The icon census and the per-place marker list then say the same thing a second way.

Why there is no script VM in this file: the goal condition reaches `ext 29` behind a branch and
this file does not read that op's stack effect. It does not have to. The insert appends
`test_flag(196) ; or` AFTER the condition's own closing `or`, so it reads the one value that `or`
just produced and leaves one value in its place. The `jz` that follows still tests the top of the
stack. Whatever `ext 29` leaves below that top is untouched either way.

What this file cannot read: whether the star SPRITE looks right at (193,25), and whether the owner
wants the star there before he has done the Capsule Corp side quest itself. Those are his eye.
"""
import struct
import unittest

import log2_build
import log_paths
from patches import worldmap_star as WS
from rom.rom_space import Allocator
from scene import scene_lib as S

ROM_BASE = 0x08000000
LIST = log_paths.BUILD_LISTS / "build_list_trial_plateau.txt"

# Capsule Corp's own block in the VANILLA script, read op for op 2026-11-09.
BLOCK_AT, BLOCK_END = 0x3FB8EF, 0x3FB927     # from after the previous place's icon to after its own
JZ_SKIP, JMP_SKIP = 9, 13                    # the two offsets inside the block, which must not move
PLACES = 13                                  # the world map draws thirteen places

# The flag that ends the main story, and the four op shapes that could touch it.
SET_BYTES = (S.push(WS.STORY_OVER) + S.ext(27)).hex()
CLEAR_BYTES = (S.push(WS.STORY_OVER) + S.ext(28)).hex()
SET_SITES, CLEAR_SITES = 2, 0
BASE_END = 0x800000                          # the vanilla ROM; expansion holds our own modules


def _padded():
    base = log2_build.BASE.read_bytes()
    return bytearray(base) + bytes([0xFF]) * (log2_build.ROM_SIZE - len(base))


def _build():
    names = log2_build.read_build_list(LIST)
    assert "worldmap_star" in names, "the trial list must carry worldmap_star"
    before, _ = log2_build.assemble(log2_build.BASE,
                                    [n for n in names if n != "worldmap_star"])
    rom, alloc = log2_build.assemble(log2_build.BASE, names)
    return bytes(before), rom, alloc.notes["worldmap_star"]


def _icons(rom, start, end):
    """[(icon ext, x, y)] in script order. Pushes feed the ext op that follows them."""
    out, stack = [], []
    for op in S.ops(rom, start, end):
        if op.ext is None:
            if op.op in (0, 1, 29):
                stack += list(op.args)
            continue
        if op.ext in (WS.GOAL_ICON, WS.NORMAL_ICON):
            out.append((op.ext, *stack))
        stack = []
    return out


def _flags_tested(rom, start, end):
    """Every flag number reached by ext 19 or ext 20 in one script, in order."""
    out, stack = [], []
    for op in S.ops(rom, start, end):
        if op.ext is None:
            if op.op in (0, 1, 29):
                stack += list(op.args)
            continue
        if op.ext in (19, 20):
            out += list(stack)
        stack = []
    return out


def _sites(rom, pattern):
    """Every offset of one byte pattern in the VANILLA half of the ROM."""
    out, o = [], rom.find(pattern)
    while o != -1 and o < BASE_END:
        out.append(o)
        o = rom.find(pattern, o + 1)
    return out


class WorldMapStarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before, cls.rom, cls.notes = _build()
        cls.base = log2_build.BASE.read_bytes()
        cls.copy = bytes(cls.rom[cls.notes["script"]:cls.notes["script"] + cls.notes["script_size"]])

    # ----- the copy -----

    def test_the_vanilla_world_map_script_is_not_written(self):
        self.assertEqual(bytes(self.rom[WS.SCRIPT_AT:WS.SCRIPT_END]),
                         self.base[WS.SCRIPT_AT:WS.SCRIPT_END],
                         "the module must copy the script, never edit it in place")

    def test_the_copy_is_the_vanilla_script_with_the_insert_spliced_in(self):
        """One assertion for the whole script: vanilla, cut after the `or`, with five bytes added.

        Nothing else in 0x2C0 bytes may differ, so no other place's condition, marker or jump can
        have moved."""
        cut = WS.OR_AT + 1
        want = (self.base[WS.SCRIPT_AT:cut] + WS.insert() + self.base[cut:WS.SCRIPT_END])
        self.assertEqual(self.copy, want)
        self.assertEqual(len(self.copy), WS.SCRIPT_LEN + 5)

    def test_map_6_99_runs_the_copy_and_nothing_else_names_it(self):
        entry = self.notes["entry"]
        self.assertEqual((self.rom[entry], self.rom[entry + 1]), (WS.WORLD_ZONE, WS.WORLD_AREA))
        self.assertEqual(struct.unpack_from("<I", self.rom, entry + WS.F_ENTER)[0] - ROM_BASE,
                         self.notes["script"])
        self.assertEqual(struct.unpack_from("<I", self.before, entry + WS.F_ENTER)[0] - ROM_BASE,
                         WS.SCRIPT_AT, "before this module the entry names the vanilla script")

    def test_the_copy_lands_in_free_expansion_space(self):
        where, size = self.notes["script"], self.notes["script_size"]
        self.assertGreaterEqual(where, BASE_END)
        self.assertEqual(set(self.before[where:where + size]), {0xFF},
                         "the module must not land on another module's data")

    # ----- the insert -----

    def test_the_insert_is_test_flag_196_then_or(self):
        at = self.notes["script"] + (WS.OR_AT + 1 - WS.SCRIPT_AT)
        got = [(op.op, op.ext, tuple(op.args)) for op in S.ops(self.rom, at, at + 5)]
        self.assertEqual(got, [(0, None, (WS.STORY_OVER,)), (2, WS.TEST_FLAG, ()), (WS.OR_OP, None, ())])

    def test_the_insert_sits_between_the_condition_and_its_own_jz(self):
        """The `or` it follows closes Capsule Corp's vanilla condition; the `jz` it precedes is the
        one that skips the star. So the gate becomes `(vanilla condition) or flag 196`."""
        at = self.notes["script"] + (WS.OR_AT - WS.SCRIPT_AT)
        got = [(op.op, op.ext, tuple(op.args)) for op in S.ops(self.rom, at, at + 8)]
        self.assertEqual(got[0], (WS.OR_OP, None, ()), "the condition's own closing or")
        self.assertEqual(got[-1], (19, None, (JZ_SKIP,)), "Capsule Corp's jz, still skipping 9")

    def test_the_jz_still_skips_exactly_the_star_and_its_jmp(self):
        """If the insert had been folded onto the `jz` instead of the `or`, this offset would be
        wrong and the star would be drawn on both branches."""
        at = self.notes["script"] + (WS.JZ_AT + 5 - WS.SCRIPT_AT)
        got = [(op.op, op.ext, tuple(op.args)) for op in S.ops(self.rom, at, at + 2 + JZ_SKIP)]
        self.assertEqual(got[0], (19, None, (JZ_SKIP,)))
        self.assertEqual(got[1][2], WS.MARKER, "the push the star reads")
        self.assertEqual(got[2][1], WS.GOAL_ICON, "ext 102, the star")
        self.assertEqual(got[3], (18, None, (JMP_SKIP,)), "its jmp over the plain icon")

    # ----- FAIL THEN PASS: the star itself -----

    def test_capsule_corp_now_tests_the_story_over_flag_and_did_not_before(self):
        """The proof the owner asked for. The vanilla world map script never reads flag 196; after
        this module Capsule Corp's own block reads it, and no other block does."""
        vanilla = _flags_tested(self.base, WS.SCRIPT_AT, WS.SCRIPT_END)
        self.assertNotIn(WS.STORY_OVER, vanilla,
                         "the vanilla world map must not already gate on flag 196")
        where, size = self.notes["script"], self.notes["script_size"]
        after = _flags_tested(self.rom, where, where + size)
        self.assertEqual(after.count(WS.STORY_OVER), 1, "exactly one new flag 196 test")
        block = _flags_tested(self.rom, where + (BLOCK_AT - WS.SCRIPT_AT),
                              where + (BLOCK_END + 5 - WS.SCRIPT_AT))
        self.assertIn(WS.STORY_OVER, block, "and it is inside Capsule Corp's own block")

    def test_every_other_flag_the_world_map_reads_is_unchanged(self):
        vanilla = _flags_tested(self.base, WS.SCRIPT_AT, WS.SCRIPT_END)
        where, size = self.notes["script"], self.notes["script_size"]
        after = _flags_tested(self.rom, where, where + size)
        after.remove(WS.STORY_OVER)
        self.assertEqual(after, vanilla)

    # ----- no other place moves -----

    def test_the_world_map_still_draws_thirteen_places_with_the_same_markers(self):
        vanilla = _icons(self.base, WS.SCRIPT_AT, WS.SCRIPT_END)
        where, size = self.notes["script"], self.notes["script_size"]
        self.assertEqual(_icons(self.rom, where, where + size), vanilla)
        self.assertEqual(sum(1 for i in vanilla if i[0] == WS.GOAL_ICON), PLACES)
        self.assertEqual(sum(1 for i in vanilla if i[0] == WS.NORMAL_ICON), PLACES)

    def test_capsule_corps_star_is_the_vanilla_star_and_not_a_new_one(self):
        """The module adds no icon. Capsule Corp already had both icons; only the gate widened."""
        self.assertEqual(self.base[WS.GOAL_AT:WS.GOAL_AT + 2], S.ext(WS.GOAL_ICON))
        self.assertEqual(self.base[WS.NORMAL_AT:WS.NORMAL_AT + 2], S.ext(WS.NORMAL_ICON))
        self.assertIn((WS.GOAL_ICON, *WS.MARKER), _icons(self.base, BLOCK_AT, BLOCK_END))
        self.assertIn((WS.NORMAL_ICON, *WS.MARKER), _icons(self.base, BLOCK_AT, BLOCK_END))

    def test_the_copied_script_walks_to_its_own_end(self):
        where, size = self.notes["script"], self.notes["script_size"]
        o, count = where, 0
        while o < where + size:
            o = S.op_end(self.rom, o)
            count += 1
        self.assertEqual(o, where + size)
        self.assertEqual(count, self.notes["ops"])
        self.assertEqual(self.rom[where + size - 1], 17, "the copy still ends on op 17")

    # ----- THE GATE -----

    def test_flag_196_is_set_only_by_the_two_endings_and_is_never_cleared(self):
        """Why the star cannot appear during the main story.

        Two shapes, so one of them does not just enumerate itself. Shape A is the byte pattern
        `push 196 ; set_flag`. Shape B walks every `ext 27` and `ext 28` in the vanilla ROM and
        reads the push in front of it, which also catches a varint push. A flag written by ARM code
        instead of by a script op would appear in neither, and this file does not look for that."""
        self.assertEqual(sorted(_sites(self.base, bytes.fromhex(SET_BYTES))),
                         sorted(WS.SETTERS))
        self.assertEqual(_sites(self.base, bytes.fromhex(CLEAR_BYTES)), [])

        found = {27: [], 28: []}
        for extno in (27, 28):
            for at in _sites(self.base, S.ext(extno)):
                if at >= 2 and self.base[at - 2] in (0, 1) and self.base[at - 1] == WS.STORY_OVER:
                    found[extno].append(at)
        self.assertEqual(len(found[27]), SET_SITES, "shape B must agree with shape A on the setters")
        self.assertEqual(found[28], [], "nothing in the game clears flag 196")

    def test_both_setters_are_still_the_records_this_module_read(self):
        for at in WS.SETTERS:
            self.assertEqual(self.base[at:at + 4], bytes.fromhex(WS.SETTER_BYTES))
            self.assertEqual(bytes(self.rom[at:at + 4]), bytes.fromhex(WS.SETTER_BYTES),
                             "no module in this list may move an ending's set_flag(196)")

    # ----- the module's own guards -----

    def test_a_second_run_raises(self):
        rom = _padded()
        alloc = Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        WS.apply(rom, alloc)
        with self.assertRaises(ValueError):
            WS.apply(rom, alloc)

    def test_a_changed_source_byte_raises_before_any_write(self):
        rom = _padded()
        rom[WS.JZ_AT] = 0x18                       # turn Capsule Corp's jz into a jmp
        alloc = Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        with self.assertRaises(ValueError):
            WS.apply(rom, alloc)
        self.assertNotIn("worldmap_star", alloc.notes)


if __name__ == "__main__":
    unittest.main()
