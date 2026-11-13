r"""
test_piccolo_powerup_art.py - Tests for patches.piccolo_powerup_art (trial 2026-11-12): the power-up
                              animation the owner drew for set 104, Super Namek.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_piccolo_powerup_art.py -v
Builds the dev master in memory once, keeps it as "before", then applies the module to the same ROM, so
every test sees both sides and the notes. Expected values are restated from
docs\tasks\2026-11-12-powerup-art\brief.md and the live set bytes, never imported from the patch module.
The frame test compares the built ROM against the four PNGs he saved, not against our indexed copies.
"""
import struct
import unittest
from pathlib import Path

import log2_build
import log_paths
from patches import piccolo_powerup_art, vegeta_zplus
from rom.rom_space import Allocator
from rom.webfoot_decompress import ROM_BASE, read_record, read_set
from tests.test_vegeta_zplus import assert_row_is_his_art, assert_step_set_can_power_up

# ===== constants (brief, live set bytes) =====
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_piccolo_art.txt"
NAMEK_SET, BASE_SET = 104, 103
POWER_UP, REVERT = 9, 21
SHAPE = (32, 32, -8, -24)                        # bible B2389: an anim 9 frame is 32x32
RECORDS, SLOT = 4, 0x400
KIT = log_paths.PICCOLO_POWERUP_KIT
HIS_PNGS = tuple(KIT / f"P_Frame{n}.png" for n in (1, 2, 3, 4))
UNTOUCHED_SETS = (133, 61, 139, 140)             # Trunks, Goku and both Vegeta super sets keep their hole

_CACHE = {}


def built() -> dict:
    """{"before": the dev master, "rom": after the module, "notes": its notes}."""
    if _CACHE:
        return _CACHE
    rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(log2_build.DEV_LIST))
    before = bytes(rom)
    piccolo_powerup_art.apply(rom, alloc)
    _CACHE.update(before=before, rom=bytes(rom), notes=alloc.notes["piccolo_powerup_art"], all_notes=alloc.notes)
    return _CACHE


class PiccoloPowerUpArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]

    # ===== the hole this fills =====

    def test_super_namek_had_no_power_up_at_all(self):
        """Set 104 anim 9 is four null pointers in the dev master. The record lookup @0x0800775A
        indexes the row by number with no existence test (bible B0041), so a power-up on this set
        follows a null record list and the game crashes."""
        self.assertEqual(vegeta_zplus.anim_row(self.before, NAMEK_SET, POWER_UP)[1], (0, 0, 0, 0))
        assert_step_set_can_power_up(self, self.rom, NAMEK_SET)

    def test_the_row_names_one_new_record_list_in_all_four_directions(self):
        """One list of four records for up, down, left and right, which is what every anim 9 measured
        does (bible B2388), so his one front view covers all four."""
        at, ptrs = vegeta_zplus.anim_row(self.rom, NAMEK_SET, POWER_UP)
        self.assertEqual(at, self.notes["row"])
        self.assertEqual(ptrs, (self.notes["list"] + ROM_BASE,) * 4)
        self.assertGreaterEqual(self.notes["list"], log2_build.BASE_SIZE)        # appended, nothing moved
        start, recs = vegeta_zplus.shared_list(self.rom, NAMEK_SET, POWER_UP)
        self.assertEqual(len(recs), RECORDS)
        self.assertEqual([r["hdr"] + ROM_BASE for r in recs], self.notes["headers"])

    def test_the_row_decodes_back_to_his_own_pixels(self):
        """His drawings are the point. Each frame is decoded from the built ROM and compared against
        the file he saved, so a conversion that changed one pixel fails here."""
        assert_row_is_his_art(self, self.rom, NAMEK_SET, HIS_PNGS)

    def test_the_frames_match_the_geometry_super_namek_already_draws(self):
        """Same OBJ slot and the same record shape as set 104's own revert row, or the frames tear."""
        for sid in (NAMEK_SET, BASE_SET):
            self.assertEqual(read_set(self.rom, vegeta_zplus.set_at(self.rom, sid))["slot"], SLOT, sid)
        shapes = set()
        for row in (vegeta_zplus.anim_row(self.rom, NAMEK_SET, POWER_UP)[1],
                    vegeta_zplus.anim_row(self.rom, NAMEK_SET, REVERT)[1],
                    vegeta_zplus.anim_row(self.rom, BASE_SET, POWER_UP)[1]):
            for word in row:
                r = read_record(self.rom, word - ROM_BASE)
                shapes.add((r["w"], r["h"], r["dx"], r["dy"]))
        self.assertEqual(shapes, {SHAPE})

    # ===== what must not change =====

    def test_base_piccolos_cape_drop_is_byte_for_byte_unchanged(self):
        """Set 103 anim 9 is the turban and cape drop, his vanilla Z transformation (bible B2387)."""
        at, ptrs = vegeta_zplus.anim_row(self.rom, BASE_SET, POWER_UP)
        self.assertEqual(vegeta_zplus.anim_row(self.before, BASE_SET, POWER_UP), (at, ptrs))
        start = ptrs[0] - ROM_BASE
        self.assertEqual(self.rom[start:start + 12 * RECORDS], self.before[start:start + 12 * RECORDS])

    def test_no_other_set_with_a_null_row_is_touched(self):
        """The owner chose set 104. Trunks, Goku and both Vegeta super sets keep their own hole."""
        for sid in UNTOUCHED_SETS:
            self.assertEqual(vegeta_zplus.anim_row(self.rom, sid, POWER_UP)[1], (0, 0, 0, 0), sid)

    def test_the_base_8mb_differs_only_at_super_nameks_own_row(self):
        """Every differing byte INSIDE the row, not every row byte differing: a pointer byte that
        already held the value it needs stays equal, and a list address ending in 0x00 does that
        four times over."""
        row = self.notes["row"]
        self.assertTrue(row < log2_build.BASE_SIZE)
        self.assertEqual(self.before[row:row + 16], bytes(16))
        diff = [i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]]
        self.assertTrue(diff)
        self.assertEqual([hex(i) for i in diff if not row <= i < row + 16], [])

    def test_it_builds_no_form_only_the_art(self):
        """Piccolo Z+ is a separate task. This module adds no appearance entry, no form object, no
        portrait and no unlock, so its note names a row, a list and four frames and nothing else."""
        self.assertEqual(set(self.notes), {"row", "like", "anim", "list", "ptrs", "headers"})
        self.assertEqual(set(built()["all_notes"]) - set(log2_build.read_build_list(log2_build.DEV_LIST)),
                         {"piccolo_powerup_art"})

    # ===== the trial list and failing closed =====

    def test_the_trial_list_is_the_dev_master_plus_this_module(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["piccolo_powerup_art"])
        for master in (log2_build.BUILD_LIST, log2_build.DEV_LIST,
                       log2_build.BUILD_LIST.parent / "build_list_core.txt"):
            self.assertNotIn("piccolo_powerup_art", master.read_text(encoding="utf-8"), master.name)

    def test_apply_fails_closed(self):
        """Twice, and on a row that is already filled. Each refusal happens before any write."""
        rom, alloc = bytearray(self.rom), Allocator(len(self.rom), log2_build.EXPANSION)
        alloc.notes["piccolo_powerup_art"] = dict(self.notes)
        with self.assertRaisesRegex(ValueError, "already ran"):
            piccolo_powerup_art.apply(rom, alloc)
        self.assertEqual(bytes(rom), self.rom)
        rom, alloc = bytearray(self.rom), Allocator(len(self.rom), log2_build.EXPANSION)
        with self.assertRaisesRegex(ValueError, "nothing to fill"):
            piccolo_powerup_art.apply(rom, alloc)
        self.assertEqual(bytes(rom), self.rom)

    def test_it_refuses_a_frame_that_is_not_his(self):
        """A frame of the wrong size, an unknown colour or a reserved index stops the build and is
        named. Never snapped: a snapped pixel is his art changed without him seeing it."""
        rom = bytearray(self.before)
        with self.assertRaisesRegex(ValueError, "the record needs 1024"):
            vegeta_zplus.plan_anim_frames(rom, NAMEK_SET, BASE_SET, [b"\0" * 16] * RECORDS, POWER_UP)
        frames = vegeta_zplus.hand_frames(rom, HIS_PNGS)
        with self.assertRaisesRegex(ValueError, "the frame count is in code"):
            vegeta_zplus.plan_anim_frames(rom, NAMEK_SET, BASE_SET, frames[:3], POWER_UP)
        with self.assertRaisesRegex(ValueError, "not in the OBJ palette"):
            vegeta_zplus.hand_frames(rom, [KIT / "his_vs_vanilla_strip.png"])
        struct.pack_into("<H", rom, vegeta_zplus.set_at(rom, NAMEK_SET), 0x1000)
        with self.assertRaisesRegex(ValueError, "the OBJ buffer would not fit"):
            vegeta_zplus.plan_anim_frames(rom, NAMEK_SET, BASE_SET, frames, POWER_UP)
        self.assertEqual(vegeta_zplus.anim_row(rom, NAMEK_SET, POWER_UP)[1], (0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
