r"""Tests for rom.show_regions. Fixtures are built in a temp dir, never read from art\.

The tool hardcoded W, H = 16, 32 until 2026-11-06, which blocked every 32 wide record, and it had no
test at all. These pin the frame size coming from the frame, both widths, and every refusal.
"""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from rom import show_regions

PAL = [v for i in range(256) for v in (i, (i * 7) % 256, (i * 13) % 256)]


def frame(tmp: Path, name: str, w: int, h: int) -> Path:
    """An indexed frame with a lit block inset from the edges, like a real sprite."""
    data = bytearray(w * h)
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            data[y * w + x] = 10
    im = Image.frombytes("P", (w, h), bytes(data))
    im.putpalette(PAL)
    p = tmp / name
    im.save(p)
    return p


def regions(tmp: Path, name: str, frames: list, drop_row: bool = False,
            blank_one: bool = False) -> Path:
    lines = ["# built by the test"]
    lines += [f"#png k{n} {p.name}" for n, p in enumerate(frames)]
    for n, p in enumerate(frames):
        with Image.open(p) as im:
            w, h = im.size
            data = im.tobytes()
        lines.append(f"[k{n}]")
        rows = ["".join("T" if data[y * w + x] else "." for x in range(w)) for y in range(h)]
        if blank_one and n == 0:
            rows[2] = rows[2].replace("T", ".", 1)
        if drop_row and n == 0:
            rows.pop()
        lines += rows
    p = tmp / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


class ShowRegionsTests(unittest.TestCase):
    def test_a_sixteen_wide_sheet_passes(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            src = regions(tmp, "r16.txt", [frame(tmp, f"f{n}.png", 16, 32) for n in range(2)])
            self.assertEqual(0, show_regions.main([str(src), "--out", str(tmp / "o.png")]))
            self.assertTrue((tmp / "o.png").is_file())

    def test_a_thirty_two_wide_sheet_passes(self):
        """The record width the tool used to refuse. 174 of set 128's 288 records are 32 wide."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            src = regions(tmp, "r32.txt", [frame(tmp, f"w{n}.png", 32, 32) for n in range(2)])
            self.assertEqual(0, show_regions.main([str(src), "--out", str(tmp / "o.png")]))
            self.assertTrue((tmp / "o.png").is_file())

    def test_the_size_comes_from_the_frame_not_a_constant(self):
        for w, h in ((16, 32), (32, 32), (32, 64)):
            with self.subTest(size=(w, h)), tempfile.TemporaryDirectory() as t:
                tmp = Path(t)
                src = regions(tmp, "r.txt", [frame(tmp, "a.png", w, h)])
                self.assertEqual((w, h), show_regions.load(src)[4:6])

    def test_a_map_with_the_wrong_row_count_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            src = regions(tmp, "r.txt", [frame(tmp, "a.png", 32, 32)], drop_row=True)
            with self.assertRaises(ValueError) as e:
                show_regions.load(src)
            self.assertIn("not 32 lines", str(e.exception))

    def test_frames_of_different_sizes_in_one_file_are_refused(self):
        """One sheet uses one panel size, so a mixed file would draw a wrong picture silently."""
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            small, big = frame(tmp, "s.png", 16, 32), frame(tmp, "b.png", 32, 32)
            src = regions(tmp, "r.txt", [small])
            src.write_text(src.read_text(encoding="utf-8").replace(
                "#png k0 s.png", "#png k0 s.png\n#png k1 b.png"), encoding="utf-8")
            with self.assertRaises(ValueError) as e:
                show_regions.load(src)
            self.assertIn("must be 16x32", str(e.exception))

    def test_a_regions_file_with_no_png_line_is_refused(self):
        with tempfile.TemporaryDirectory() as t:
            src = Path(t) / "r.txt"
            src.write_text("# nothing but a comment\n", encoding="utf-8")
            with self.assertRaises(ValueError) as e:
                show_regions.load(src)
            self.assertIn("frame size is unknown", str(e.exception))

    def test_an_unlettered_lit_pixel_is_reported_at_thirty_two_wide(self):
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            src = regions(tmp, "r.txt", [frame(tmp, "a.png", 32, 32)], blank_one=True)
            self.assertEqual(1, show_regions.main([str(src), "--out", str(tmp / "o.png")]))

    def test_no_arguments_prints_usage_and_returns_two(self):
        self.assertEqual(2, show_regions.main([]))


if __name__ == "__main__":
    unittest.main()
