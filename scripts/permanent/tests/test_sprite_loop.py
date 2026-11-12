r"""Tests for rom.sprite_loop. Fixtures are built in a temp dir, never read from art\."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from rom import sprite_loop

W, H = 16, 32


def frame(tmp, name, fill, w=W, h=H):
    pal = []
    for i in range(256):
        pal += [i, (i * 7) % 256, (i * 13) % 256]
    im = Image.frombytes("P", (w, h), bytes([fill]) * (w * h))
    im.putpalette(pal)
    p = Path(tmp) / name
    im.save(p)
    return p


class SpriteLoopTests(unittest.TestCase):
    def test_writes_gif_and_strip_and_the_decode_check_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [str(frame(tmp, f"f{n}.png", 10 + n)) for n in range(4)]
            stem = str(Path(tmp) / "out")
            self.assertEqual(0, sprite_loop.main([stem] + paths))
            self.assertTrue(Path(f"{stem}.gif").is_file())
            self.assertTrue(Path(f"{stem}_strip.png").is_file())

    def test_gif_holds_one_image_per_frame(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [str(frame(tmp, f"f{n}.png", 20 + n)) for n in range(3)]
            stem = str(Path(tmp) / "out")
            sprite_loop.main([stem] + paths)
            with Image.open(f"{stem}.gif") as g:
                n = 0
                while True:
                    try:
                        g.seek(n)
                    except EOFError:
                        break
                    n += 1
            self.assertEqual(3, n)

    def test_index_zero_is_drawn_as_the_sheet_background_not_black(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = frame(tmp, "clear.png", 0)
            with Image.open(p) as im:
                data, pal = im.tobytes(), im.getpalette()
            got = sprite_loop.shot(data, W, H, pal, 1)
            self.assertEqual(sprite_loop.BG, got.getpixel((0, 0)))

    def test_too_few_arguments_prints_usage_and_returns_two(self):
        self.assertEqual(2, sprite_loop.main(["only_the_stem"]))

    def test_frames_of_different_sizes_are_refused_before_any_write(self):
        """A FALSE PASS before 2026-11-06: a 16 wide frame first made a 32 wide frame report
        "0 px differ" and exit 0, with half of the wide frame never compared, because one gif has
        one canvas and the decode check used frame 0's size for every frame."""
        for order in ((16, 32), (32, 16)):
            with self.subTest(first=order[0]), tempfile.TemporaryDirectory() as tmp:
                a = frame(tmp, "a.png", 50, w=order[0])
                b = frame(tmp, "b.png", 60, w=order[1])
                stem = str(Path(tmp) / "out")
                self.assertEqual(2, sprite_loop.main([stem, str(a), str(b)]))
                self.assertFalse(Path(f"{stem}.gif").exists())
                self.assertFalse(Path(f"{stem}_strip.png").exists())

    def test_a_held_pose_still_passes_the_decode_check(self):
        """Pillow writes no gif frame for a frame identical to the one before it. A held pose is
        ordinary in an animation, and before the index mapping the check raised EOFError."""
        for name, fills in (("middle", [1, 2, 2, 3]), ("start", [4, 4, 5]),
                            ("end", [6, 7, 7]), ("all three", [8, 8, 8])):
            with self.subTest(held=name), tempfile.TemporaryDirectory() as tmp:
                paths = [str(frame(tmp, f"f{n}.png", v)) for n, v in enumerate(fills)]
                stem = str(Path(tmp) / "out")
                self.assertEqual(0, sprite_loop.main([stem] + paths))

    def test_the_gif_drops_a_held_frame_and_the_count_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [str(frame(tmp, f"f{n}.png", v)) for n, v in enumerate([30, 31, 31, 32])]
            stem = str(Path(tmp) / "out")
            self.assertEqual(0, sprite_loop.main([stem] + paths))
            with Image.open(f"{stem}.gif") as g:
                self.assertEqual(3, g.n_frames)        # four sent, one held

    def test_holds_counts_only_a_frame_that_repeats_the_one_before_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            shots = []
            for v in (40, 41, 41, 40):
                with Image.open(frame(tmp, f"h{v}{len(shots)}.png", v)) as im:
                    shots.append(sprite_loop.shot(im.tobytes(), W, H, im.getpalette(), 1))
            self.assertEqual(1, sprite_loop.holds(shots))   # the 40 at the end repeats nothing
            self.assertTrue(sprite_loop.same(shots[1], shots[2]))
            self.assertFalse(sprite_loop.same(shots[2], shots[3]))


if __name__ == "__main__":
    unittest.main()
