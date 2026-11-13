r"""
test_gameover_card.py - Tests for patches.gameover_card (trial 2026-11-07): a loss to Cell in the final arena,
                        map 7,100, shows the owner's two caption boxes instead of "@^You have died!".

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_gameover_card.py -v
Builds build_list_trial_gameover.txt in memory: "before" = the list up to gameover_card (the plateau trial),
"rom" = before plus gameover_card. Nothing is pinned by SHA-1, because the four trial modules below this one
are still moving. Every expected value is restated from the base ROM and the handlers, never imported from
the patch module: the branch shape from vanilla record 0 rom:0x3B6104, the wrap rule from the dialog line
counter @0x0801F7FC (width 0x90, 4 lines, bible C4S), and the map ids from the two arena modules.
"""
import copy
import struct
import unittest

import log2_build
import log_paths
from patches import gameover_card
from scene import scene_lib as S

# ===== constants (base ROM reads and the handlers, not the module) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_gameover.txt"
PLATEAU_LIST = log_paths.BUILD_LISTS / "build_list_trial_plateau.txt"
LITERAL = 0x8870                                 # the one ROM word that names the game-over table
VANILLA_TABLE, VANILLA_WORDS = 0x3B63B4, 24
VANILLA_RECORD0, VANILLA_RECORD0_END = 0x3B6104, 0x3B6139
AFTER_TABLE = 0x3B6414                           # the "@Game Saved!" record: the table cannot grow in place
DEATH_BOX = 0x3B613A                             # table word 1, "@^You have died!"
TAIL_INDEX = 2
PLATEAU_MAP, ARENA_MAP, ANDROID_MAP = (7, 100), (6, 100), (1, 100)
#   ext 8 ; push 7 ; eq ; ext 9 ; push 100 ; eq ; and ; jz 3 ; push 24 ; end
#   the same 16-byte shape as the vanilla 6,70 test at rom:0x3B6107, with 7, 100 and index 24
EXPECTED_TEST = bytes.fromhex("020800070b020900640b041303001811")
CARD_ONE = "@^Cell takes the time machine into the past..."
CARD_TWO = "@^The nightmare is just beginning."
DIALOG_FONT, DIALOG_WIDTH, BOX_LINES = 0x2CC64, 0x90, 4      # bible C4S: wrap past 144 px, 4 lines a box

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("gameover_card")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["gameover_card"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["gameover_card"])
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def runs(a: bytes, b: bytes) -> list:
    """(offset, length) of every run of bytes that differ between two ROMs of the same length."""
    out, start = [], None
    for i in range(len(a)):
        if a[i] != b[i]:
            start = i if start is None else start
        elif start is not None:
            out.append((start, i - start))
            start = None
    return out + ([(start, len(a) - start)] if start is not None else [])


def dialog_wrap(rom: bytes, box: bytes) -> list:
    """Lines of one box as the dialog line counter breaks them (bible C4S: past 144 px, at the last space)."""
    def adv(c):
        glyph = struct.unpack_from("<H", rom, DIALOG_FONT + 2 * c)[0]
        return struct.unpack_from("<H", rom, DIALOG_FONT + 2 * glyph)[0] + 1

    out, p = [], 0
    while p < len(box):
        while p < len(box) and box[p] == 0x20:
            p += 1
        if p >= len(box):
            break
        q, w, brk = p, 0, None
        while q < len(box):
            if box[q] == 0x20:
                brk = q
            w += adv(box[q])
            if w > DIALOG_WIDTH:
                q = brk if brk is not None else q
                break
            q += 1
        out.append((box[p:q].decode(), sum(adv(c) for c in box[p:q])))
        p = q
    return out


def table(rom: bytes) -> tuple:
    """(file offset, words) of the table the live literal names."""
    at = u32(rom, LITERAL) - ROM_BASE
    return at, [u32(rom, at + 4 * i) for i in range(VANILLA_WORDS + 3)]


# ===== the list =====

class ListTests(unittest.TestCase):
    def test_the_trial_list_is_the_plateau_list_plus_this_module(self):
        plateau = log2_build.read_build_list(PLATEAU_LIST)
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), plateau + ["gameover_card"])

    def test_the_module_is_in_no_master_list(self):
        for path in (log2_build.BUILD_LIST, log2_build.DEV_LIST):
            self.assertNotIn("gameover_card", log2_build.read_build_list(path))


# ===== fail closed =====

class FailClosedTests(unittest.TestCase):
    def test_a_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["gameover_card"] = {}
        with self.assertRaises(ValueError):
            gameover_card.apply(rom, alloc)

    def test_a_moved_literal_raises_before_writing(self):
        b = built()
        rom = bytearray(b["before"])
        rom[LITERAL:LITERAL + 4] = struct.pack("<I", 0x08900000)
        with self.assertRaises(ValueError):
            gameover_card.apply(rom, copy.deepcopy(b["alloc_before"]))

    def test_a_changed_record_zero_raises_before_writing(self):
        b = built()
        rom = bytearray(b["before"])
        rom[VANILLA_RECORD0 + 6] ^= 0xFF                      # the `push 6` of the 6,70 test
        with self.assertRaises(ValueError):
            gameover_card.apply(rom, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom[LITERAL:LITERAL + 4]), b["before"][LITERAL:LITERAL + 4])

    def test_a_missing_plateau_map_raises(self):
        """Without map 7,100 the branch could never fire, so the patch must refuse rather than ship dead code."""
        b = built()
        rom = bytearray(b["before"])
        base = u32(rom, 0xEBD8) - ROM_BASE
        for k in range(0xFF + rom[0xE0AE]):
            if (rom[base + 56 * k], rom[base + 56 * k + 1]) == PLATEAU_MAP:
                rom[base + 56 * k + 1] = 99
        with self.assertRaises(ValueError):
            gameover_card.apply(rom, copy.deepcopy(b["alloc_before"]))


# ===== what the build changed =====

class DiffTests(unittest.TestCase):
    def test_only_the_declared_sites_changed(self):
        b = built()
        sites = [(o, n) for o, n, _ in b["notes"]["sites"]]
        for off, length in runs(b["before"], b["rom"]):
            self.assertTrue(any(s <= off and off + length <= s + n for s, n in sites),
                            f"rom:0x{off:X} (0x{length:X} bytes) is outside every declared site")

    def test_the_only_change_below_the_expansion_area_is_the_literal(self):
        """The run is 3 bytes, not 4: both the old and the new table live in bank 0x08."""
        b = built()
        low = [r for r in runs(b["before"], b["rom"]) if r[0] < 0x800000]
        self.assertEqual(len(low), 1)
        off, length = low[0]
        self.assertTrue(LITERAL <= off and off + length <= LITERAL + 4, f"rom:0x{off:X}")
        self.assertNotEqual(u32(b["rom"], LITERAL), u32(b["before"], LITERAL))

    def test_the_vanilla_table_record_and_neighbour_are_untouched(self):
        b = built()
        for lo, hi in ((VANILLA_TABLE, VANILLA_TABLE + 4 * VANILLA_WORDS),
                       (VANILLA_RECORD0, VANILLA_RECORD0_END),
                       (AFTER_TABLE, AFTER_TABLE + 0x14)):
            self.assertEqual(b["rom"][lo:hi], b["before"][lo:hi], f"rom:0x{lo:X}")

    def test_the_death_box_still_reads_you_have_died(self):
        b = built()
        self.assertEqual(b["rom"][DEATH_BOX:DEATH_BOX + 21], b"\x02\x00\x01\x00@^You have died!\0")


# ===== read the built ROM back =====

class BuiltTableTests(unittest.TestCase):
    def test_the_literal_names_a_copy_in_the_expansion_area(self):
        b = built()
        at, _ = table(b["rom"])
        self.assertNotEqual(at, VANILLA_TABLE)
        self.assertGreaterEqual(at, 0x800000)
        self.assertEqual(at % 4, 0)

    def test_the_copy_is_the_only_table_and_keeps_every_word_but_word_zero(self):
        b = built()
        at, words = table(b["rom"])
        self.assertEqual(S.words_naming(b["rom"], at), [LITERAL])
        _, old = table(b["before"])
        self.assertEqual(words[1:VANILLA_WORDS], old[1:VANILLA_WORDS])
        self.assertNotEqual(words[0], old[0])

    def test_the_three_new_words_are_records_in_the_same_chunk(self):
        b = built()
        _, words = table(b["rom"])
        chunk, size = b["notes"]["chunk"], b["notes"]["size"]
        for w in words[VANILLA_WORDS:]:
            self.assertTrue(chunk <= w - ROM_BASE < chunk + size, f"0x{w:08X}")


class BuiltRecordTests(unittest.TestCase):
    def record(self, index: int) -> int:
        _, words = table(built()["rom"])
        return words[index] - ROM_BASE

    def test_record_zero_opens_with_the_plateau_test_then_the_vanilla_record(self):
        b = built()
        at = self.record(0)
        self.assertEqual(b["rom"][at:at + 3], b["before"][VANILLA_RECORD0:VANILLA_RECORD0 + 3])
        self.assertEqual(b["rom"][at + 3:at + 3 + len(EXPECTED_TEST)], EXPECTED_TEST)
        tail = b["before"][VANILLA_RECORD0 + 3:VANILLA_RECORD0_END]
        self.assertEqual(b["rom"][at + 3 + len(EXPECTED_TEST):at + 3 + len(EXPECTED_TEST) + len(tail)], tail)

    def test_the_plateau_test_runs_before_any_map_load(self):
        """ext 39 writes the map info the test reads, so a test after it would always see map 1,7."""
        b = built()
        at = self.record(0)
        end = S.record_end(b["rom"], at)
        body = b["rom"][at:end]
        self.assertLess(body.index(EXPECTED_TEST), body.index(bytes([0x02, 0x27])))

    def test_the_branch_index_is_the_prelude_word(self):
        b = built()
        self.assertEqual(EXPECTED_TEST[-2], VANILLA_WORDS)        # `push 24`
        self.assertEqual(b["notes"]["indices"]["prelude"], VANILLA_WORDS)

    def test_the_prelude_is_a_byte_copy_of_the_vanilla_death_screen_setup(self):
        b = built()
        at = self.record(VANILLA_WORDS)
        setup = b["before"][VANILLA_RECORD0 + 0x13:VANILLA_RECORD0_END]
        self.assertEqual(b["rom"][at:at + 3], bytes([VANILLA_WORDS + 1, 0, 0]))
        self.assertEqual(b["rom"][at + 3:at + 3 + len(setup)], setup)

    def test_the_two_cards_read_exactly_as_the_owner_wrote_them(self):
        b = built()
        for index, line, nxt in ((VANILLA_WORDS + 1, CARD_ONE, VANILLA_WORDS + 2),
                                 (VANILLA_WORDS + 2, CARD_TWO, TAIL_INDEX)):
            at = self.record(index)
            self.assertEqual(b["rom"][at:at + 4], bytes([nxt, 0, 1, 0]), f"index {index} header")
            end = b["rom"].index(b"\0", at + 4)
            self.assertEqual(b["rom"][at + 4:end].decode(), line)

    def test_the_cards_end_on_the_vanilla_tail_record(self):
        b = built()
        _, words = table(b["rom"])
        self.assertEqual(words[TAIL_INDEX], u32(b["before"], VANILLA_TABLE + 4 * TAIL_INDEX))


class CapacityTests(unittest.TestCase):
    def test_each_card_fits_one_page_of_the_caption_box(self):
        b = built()
        for line in (CARD_ONE, CARD_TWO):
            lines = dialog_wrap(b["rom"], line[2:].encode("ascii"))   # `@` and `^` are eaten @0x0800B224/@0x0800BA98
            self.assertLessEqual(len(lines), BOX_LINES, line)
            for txt, width in lines:
                self.assertLessEqual(width, DIALOG_WIDTH, f"{line}: {txt!r}")

    def test_the_vanilla_death_box_measures_one_line(self):
        """The same rule on a box the owner has seen in play, so a green test is not a green rule."""
        self.assertEqual(len(dialog_wrap(built()["rom"], b"You have died!")), 1)


class ScopeTests(unittest.TestCase):
    def test_the_test_matches_only_the_plateau_and_not_the_other_arenas(self):
        """future_androids fights 18 and 17 on map 1,100 and battle_arena holds 6,100: neither may match."""
        zone, area = EXPECTED_TEST[3], EXPECTED_TEST[8]
        self.assertEqual((zone, area), PLATEAU_MAP)
        self.assertNotIn((zone, area), (ARENA_MAP, ANDROID_MAP))


if __name__ == "__main__":
    unittest.main()
