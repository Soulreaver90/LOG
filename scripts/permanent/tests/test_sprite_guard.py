r"""
test_sprite_guard.py - Tests for rom\sprite_guard.py, the outfit swap guard.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds nothing and reads no ROM: every frame here is made in memory.
"""
import unittest

from PIL import Image

from rom.sprite_guard import (changed, garment_mask, palette_reuse, review_sheet,
                              violations)

W, H = 16, 32
GARMENT = {0x51, 0x50}          # the two jacket indices these frames use
SKIN, TANK = 0x11, 0x01


def frame(cells: dict) -> Image.Image:
    """A 16x32 indexed frame. cells maps (x, y) to an index; everything else is 0."""
    data = bytearray(W * H)
    for (x, y), i in cells.items():
        data[y * W + x] = i
    im = Image.frombytes("P", (W, H), bytes(data))
    im.putpalette([v for i in range(256) for v in (i, i, i)])
    return im


class GarmentMaskTests(unittest.TestCase):

    def test_mask_is_every_pixel_holding_a_garment_index(self):
        van = frame({(2, 16): 0x51, (3, 16): 0x50, (8, 15): SKIN})
        self.assertEqual(garment_mask(van, GARMENT), {(2, 16), (3, 16)})

    def test_a_non_garment_index_is_not_in_the_mask(self):
        van = frame({(8, 15): SKIN})
        self.assertEqual(garment_mask(van, GARMENT), set())

    def test_an_rgb_image_is_refused_because_its_indices_are_gone(self):
        with self.assertRaises(ValueError):
            garment_mask(frame({(2, 16): 0x51}).convert("RGB"), GARMENT)

    def test_body_from_keeps_the_eyes_out_of_the_mask(self):
        """Trunks' jacket blues are also his irises. A whole-frame mask would call the eyes garment."""
        van = frame({(7, 13): 0x51, (9, 13): 0x51, (3, 16): 0x51})      # two irises and one sleeve
        self.assertEqual(len(garment_mask(van, GARMENT)), 3)
        self.assertEqual(garment_mask(van, GARMENT, body_from=15), {(3, 16)})

    def test_painting_an_eye_is_a_violation_once_the_head_is_excluded(self):
        van = frame({(7, 13): 0x51, (3, 16): 0x51})
        edit = frame({(7, 13): TANK, (3, 16): 0x51})
        mask = garment_mask(van, GARMENT, body_from=15)
        self.assertEqual(violations(van, edit, mask), [(7, 13, 0x51, TANK)])
        # and the hole this closes: the whole-frame mask lets it through
        self.assertEqual(violations(van, edit, garment_mask(van, GARMENT)), [])


class ViolationTests(unittest.TestCase):

    def setUp(self):
        # a jaw across x5-x11 on row 15, and jacket either side on row 16
        self.jaw = {(x, 15): SKIN for x in range(5, 12)}
        self.van = frame(self.jaw | {(3, 16): 0x51, (4, 16): 0x50})
        self.mask = garment_mask(self.van, GARMENT)

    def test_painting_the_garment_is_allowed(self):
        edit = frame(self.jaw | {(3, 16): SKIN, (4, 16): SKIN})
        self.assertEqual(violations(self.van, edit, self.mask), [])

    def test_painting_the_mouth_is_a_violation(self):
        """The real 2026-11-01 mistake: a redraw started at row 15 and covered the jaw."""
        edit = frame({(x, 15): TANK for x in range(5, 12)} | {(3, 16): 0x51, (4, 16): 0x50})
        bad = violations(self.van, edit, self.mask)
        self.assertEqual(len(bad), 7)
        self.assertEqual({y for _, y, _, _ in bad}, {15})
        self.assertEqual(bad[0], (5, 15, SKIN, TANK))

    def test_an_allowed_pixel_is_not_a_violation(self):
        edit = frame(self.jaw | {(3, 16): 0x51, (4, 16): 0x50, (0, 20): SKIN})
        self.assertEqual(len(violations(self.van, edit, self.mask)), 1)
        self.assertEqual(violations(self.van, edit, self.mask, allow={(0, 20)}), [])

    def test_violations_come_back_in_reading_order(self):
        edit = frame({(9, 15): TANK, (5, 15): TANK} | {(x, 15): SKIN for x in (6, 7, 8, 10, 11)}
                     | {(3, 16): 0x51, (4, 16): 0x50})
        self.assertEqual([(x, y) for x, y, _, _ in violations(self.van, edit, self.mask)],
                         [(5, 15), (9, 15)])

    def test_sizes_that_differ_raise_rather_than_compare(self):
        other = Image.frombytes("P", (8, 8), bytes(64))
        other.putpalette([0] * 768)
        with self.assertRaises(ValueError):
            changed(self.van, other)


class ReviewSheetTests(unittest.TestCase):

    def test_sheet_renders_and_a_crop_makes_it_shorter(self):
        van = frame({(2, 16): 0x51})
        edit = frame({(2, 16): SKIN})
        full = review_sheet(van, edit)
        cropped = review_sheet(van, edit, crop=(11, 25))
        self.assertEqual(full.mode, "RGB")
        self.assertLess(cropped.height, full.height)


if __name__ == "__main__":
    unittest.main()


class PaletteReuseTests(unittest.TestCase):
    """A garment index reused on the head, such as an iris, must never count as garment.

    --body-from cannot separate them, because Trunks' eye sits on rows 13-14, inside any floor low enough to
    catch his collar. These tests pin the connectivity rule that can."""

    @staticmethod
    def _torso(top: int = 16) -> dict:
        """A solid garment mass, the shape a real jacket makes."""
        return {(x, y): 0x51 for y in range(top, top + 5) for x in range(4, 10)}

    def test_a_small_island_above_the_garment_is_protected(self):
        van = frame({**self._torso(), (5, 13): 0x51, (5, 14): 0x51})
        self.assertEqual(palette_reuse(van, GARMENT), {(5, 13), (5, 14)})

    def test_a_protected_island_is_not_in_the_garment_mask(self):
        van = frame({**self._torso(), (5, 13): 0x51, (5, 14): 0x51})
        mask = garment_mask(van, GARMENT)
        self.assertNotIn((5, 13), mask)
        self.assertNotIn((5, 14), mask)
        self.assertIn((5, 16), mask)

    def test_body_from_alone_does_NOT_protect_the_eye(self):
        """The exact 2026-11-01 hole: the eye is ON the rows a sane floor keeps."""
        van = frame({**self._torso(), (5, 13): 0x51, (5, 14): 0x51})
        unprotected = garment_mask(van, GARMENT, body_from=13, protect=False)
        self.assertIn((5, 13), unprotected)
        self.assertNotIn((5, 13), garment_mask(van, GARMENT, body_from=13))

    def test_two_eyes_are_both_protected(self):
        van = frame({**self._torso(), (7, 13): 0x51, (7, 14): 0x51,
                     (9, 13): 0x51, (9, 14): 0x51})
        self.assertEqual(palette_reuse(van, GARMENT),
                         {(7, 13), (7, 14), (9, 13), (9, 14)})

    def test_a_lone_garment_speck_INSIDE_the_garment_rows_is_kept(self):
        """Trunks really has a 1 px jacket pixel at (5, 20). Protecting it would be a hole."""
        van = frame({**self._torso(), (2, 18): 0x51})
        self.assertEqual(palette_reuse(van, GARMENT), set())
        self.assertIn((2, 18), garment_mask(van, GARMENT))

    def test_a_large_detached_garment_piece_is_kept(self):
        """A far sleeve is detached and big. Size is what separates it from an iris."""
        sleeve = {(x, y): 0x51 for y in range(12, 15) for x in range(12, 15)}
        van = frame({**self._torso(), **sleeve})
        self.assertEqual(palette_reuse(van, GARMENT), set())

    def test_painting_a_protected_eye_is_reported_as_a_violation(self):
        van = frame({**self._torso(), (5, 13): 0x51, (5, 14): 0x51})
        edit = frame({**self._torso(), (5, 13): 0x50})          # eye darkened, lower half deleted
        bad = violations(van, edit, garment_mask(van, GARMENT))
        self.assertEqual([(x, y) for x, y, _f, _t in bad], [(5, 13), (5, 14)])

    def test_no_island_means_nothing_is_protected(self):
        self.assertEqual(palette_reuse(frame(self._torso()), GARMENT), set())
