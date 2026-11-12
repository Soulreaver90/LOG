r"""
test_sprite_look.py - Tests for rom.sprite_look, the side-by-side frame renderer.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_sprite_look.py -v

The shift tests are the ones that earn their keep: comparing a stand against a walk extreme at offset 0
reported that they share no row, when at +1 their jaw and band rows differ by 2 px each.

The fixtures are BUILT HERE, not read from art\. Both art\trunks_tank\ and scripts\one-time\ are
gitignored, so a test that loads them fails on any checkout that lacks the working folders.
"""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from rom import sprite_look

W, H = 16, 32


def _palette() -> list:
    """768 ints. Index 0 is the transparent slot, 1 upward are distinguishable colours."""
    pal = [0, 0, 0]
    for i in range(1, 256):
        pal += [(i * 7) % 256, (i * 13) % 256, (i * 29) % 256]
    return pal


class SpriteLookTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.pal = _palette()

        im = Image.new("P", (W, H), 0)
        im.putpalette(self.pal)
        for x in range(2, 6):                       # a small solid block, rows 16-19
            for y in range(16, 20):
                im.putpixel((x, y), 0x11)
        im.putpixel((8, 16), 0x4F)                  # one bright pixel for the light-ink branch
        self.indexed = self.dir / "indexed.png"
        im.save(self.indexed)

        self.rgb = self.dir / "truecolour.png"
        Image.new("RGB", (W, H), (10, 20, 30)).save(self.rgb)

    def tearDown(self):
        self._tmp.cleanup()

    def _frames(self, n=2):
        data, w, h = sprite_look.load(self.indexed)
        return [(f"f{i}", data, w, h) for i in range(n)]

    # ----- load -----

    def test_load_returns_indexed_bytes_and_size(self):
        data, w, h = sprite_look.load(self.indexed)
        self.assertEqual((w, h), (W, H))
        self.assertEqual(len(data), W * H)
        self.assertEqual(data[16 * W + 2], 0x11)

    def test_load_rejects_a_non_indexed_image_with_ValueError(self):
        """The RGB branch, not PIL's own UnidentifiedImageError. An earlier version of this test fed
        it a .json file, so PIL refused the file before load() ever reached its mode check."""
        with self.assertRaises(ValueError) as caught:
            sprite_look.load(self.rgb)
        self.assertIn("indexed", str(caught.exception))

    # ----- shift -----

    def test_shift_moves_rows_down_and_keeps_the_size(self):
        data, w, h = sprite_look.load(self.indexed)
        out = sprite_look.shift(data, w, h, 1)
        self.assertEqual(len(out), len(data))
        self.assertEqual(out[17 * w:18 * w], data[16 * w:17 * w])

    def test_shift_accepts_a_negative_offset(self):
        data, w, h = sprite_look.load(self.indexed)
        out = sprite_look.shift(data, w, h, -1)
        self.assertEqual(out[15 * w:16 * w], data[16 * w:17 * w])

    def test_shift_clears_the_rows_it_vacates(self):
        data, w, h = sprite_look.load(self.indexed)
        self.assertEqual(set(sprite_look.shift(data, w, h, 2)[0:2 * w]), {0})

    def test_shift_zero_is_the_identity(self):
        data, w, h = sprite_look.load(self.indexed)
        self.assertEqual(sprite_look.shift(data, w, h, 0), data)

    def test_a_shift_off_the_frame_empties_it(self):
        data, w, h = sprite_look.load(self.indexed)
        self.assertEqual(set(sprite_look.shift(data, w, h, H)), {0})

    # ----- look -----

    def test_look_renders_a_column_per_frame(self):
        one = sprite_look.look(self._frames(1), palette=self.pal)
        two = sprite_look.look(self._frames(2), palette=self.pal)
        self.assertGreater(two.width, one.width)
        self.assertEqual(two.height, one.height)

    def test_a_row_band_shortens_the_sheet(self):
        whole = sprite_look.look(self._frames(), palette=self.pal)
        band = sprite_look.look(self._frames(), rows=(16, 20), palette=self.pal)
        self.assertLess(band.height, whole.height)

    def test_look_needs_a_palette(self):
        with self.assertRaises(ValueError):
            sprite_look.look(self._frames(), palette=None)

    def test_plain_and_indexed_differ(self):
        a = sprite_look.look(self._frames(), rows=(16, 20), indices=True, palette=self.pal)
        b = sprite_look.look(self._frames(), rows=(16, 20), indices=False, palette=self.pal)
        self.assertEqual(a.size, b.size)
        self.assertNotEqual(a.tobytes(), b.tobytes())

    def test_small_adds_a_strip_below(self):
        plain = sprite_look.look(self._frames(), rows=(16, 20), palette=self.pal)
        with_strip = sprite_look.look(self._frames(), rows=(16, 20), palette=self.pal, small=True)
        self.assertGreater(with_strip.height, plain.height)

    def test_frames_of_different_sizes_use_the_largest(self):
        data, w, h = sprite_look.load(self.indexed)
        narrow = bytes(8 * 12)
        wide = sprite_look.look([("a", data, w, h), ("b", narrow, 8, 12)], palette=self.pal)
        only_narrow = sprite_look.look([("b", narrow, 8, 12)], palette=self.pal)
        self.assertGreater(wide.height, only_narrow.height)


if __name__ == "__main__":
    unittest.main()
