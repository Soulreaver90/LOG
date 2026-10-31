r"""
test_tools.py - Tests for rom_sheet.py and frame_lock.py.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"
Reads builds\log2_poc.gba and the base ROM. Every write goes to a temp folder.
"""
import json
import struct
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from art import frame_lock
import log_paths
from rom.log2_sprites import set_records
from rom.rom_sheet import TABLE_LITERAL, build_sheet, live_set_offset, write_frames
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, rom_ptr

ROOT = Path(__file__).resolve().parents[3]
BASE_ROM = (ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba").read_bytes()
POC_ROM = (log_paths.BUILDS / "log2_poc.gba").read_bytes()


def _png(path: Path, pixels: list, w: int = 8, h: int = 8, compress: int = 6, palette_shift: int = 0) -> None:
    img = Image.new("P", (w, h))
    img.putpalette([(i * 3 + palette_shift) % 256 for i in range(768)])
    img.putdata(pixels)
    img.save(path, compress_level=compress)


class LiveSetOffsetTests(unittest.TestCase):
    def test_matches_set_table_on_poc_for_old_ids(self):
        for set_id in (7, 56, 156):
            self.assertEqual(live_set_offset(POC_ROM, set_id), rom_ptr(POC_ROM, SET_TABLE + 4 * (set_id - 7)))

    def test_matches_set_table_on_base_for_all_old_ids(self):
        for set_id in range(7, 157):
            self.assertEqual(live_set_offset(BASE_ROM, set_id), rom_ptr(BASE_ROM, SET_TABLE + 4 * (set_id - 7)))

    def test_moved_table_resolves_through_copy(self):
        rom = bytearray(BASE_ROM)
        copy = 0x7FE600
        rom[copy:copy + 600] = rom[SET_TABLE:SET_TABLE + 600]
        struct.pack_into("<I", rom, copy + 4 * (56 - 7), rom_ptr(rom, SET_TABLE + 4 * (59 - 7)) + ROM_BASE)
        struct.pack_into("<I", rom, TABLE_LITERAL, copy + ROM_BASE)
        self.assertEqual(live_set_offset(rom, 56), rom_ptr(BASE_ROM, SET_TABLE + 4 * (59 - 7)))
        self.assertEqual(live_set_offset(rom, 57), rom_ptr(BASE_ROM, SET_TABLE + 4 * (57 - 7)))

    def test_sheet_has_one_row_per_set_anim_dir(self):
        _, notes = build_sheet(BASE_ROM, [56, 59], [0], [0, 1], 2)
        self.assertEqual([n.split(":")[0] for n in notes], ["set 56 a0 d0", "set 59 a0 d0", "set 56 a0 d1", "set 59 a0 d1"])


class FrameExportTests(unittest.TestCase):
    def test_names_sizes_and_the_d3_skip(self):             # a0 d3 mirrors d2 (h-flip); a20 d3 has its own frames
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            written = write_frames(BASE_ROM, [56], out, anims=[0, 20])
            names = sorted(p.name for p in out.iterdir())
            self.assertEqual(sorted(p.name for p in written), names)
            self.assertIn("56_a00_d0_i0.png", names)
            self.assertIn("56_a00_d0_i0_3x.png", names)
            self.assertFalse([n for n in names if n.startswith("56_a00_d3")], "a0 d3 is d2 h-flipped: skipped")
            self.assertEqual(len([n for n in names if n.startswith("56_a20_d3") and "_3x" not in n]), 4)
            self.assertEqual(len(names), 2 * (6 + 16))       # a0: 3 dirs x 2 frames; a20: 4 dirs x 4 frames
            recs = {(r["anim"], r["dir"], r["index"]): r for r in set_records(BASE_ROM, live_set_offset(BASE_ROM, 56))}
            r = recs[(0, 2, 1)]
            with Image.open(out / "56_a00_d2_i1.png") as one, Image.open(out / "56_a00_d2_i1_3x.png") as big:
                self.assertEqual(one.size, (r["w"], r["h"]))
                self.assertEqual(big.size, (3 * r["w"], 3 * r["h"]))
                self.assertEqual(one.mode, "RGBA")
                self.assertEqual(one.getpixel((0, 0))[3], 0, "color 0 is transparent")


class FrameLockTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.art, self.locks = self.tmp / "art", self.tmp / "locks"
        self.art.mkdir()
        self.locks.mkdir()
        _png(self.art / "a.png", [1] * 64)
        _png(self.art / "b.png", [2] * 64)
        (self.art / "manifest.json").write_text(json.dumps(
            [{"png": "a.png", "keys": [{"anim": 0, "dir": 1, "index": 2}]}]), encoding="ascii")

    def tearDown(self):
        self._tmp.cleanup()

    def test_fingerprint_ignores_png_encoding(self):
        _png(self.tmp / "x.png", [1] * 64, compress=0)
        _png(self.tmp / "y.png", [1] * 64, compress=9)
        self.assertNotEqual((self.tmp / "x.png").read_bytes(), (self.tmp / "y.png").read_bytes())
        self.assertEqual(frame_lock.fingerprint(self.tmp / "x.png"), frame_lock.fingerprint(self.tmp / "y.png"))

    def test_fingerprint_catches_one_pixel(self):
        px = [1] * 64
        px[9] = 5
        _png(self.tmp / "x.png", [1] * 64)
        _png(self.tmp / "y.png", px)
        self.assertNotEqual(frame_lock.fingerprint(self.tmp / "x.png"), frame_lock.fingerprint(self.tmp / "y.png"))

    def test_check_exit_codes(self):
        frame_lock.lock_folder(self.art, "t", self.locks)
        lock = json.loads((self.locks / "art" / "lock.json").read_text())
        self.assertEqual(lock["frames"]["a.png"]["keys"], [[0, 1, 2]])
        self.assertTrue((self.locks / "art" / "png" / "b.png").exists())
        self.assertEqual(sum(len(v) for v in frame_lock.check_folder(self.art, self.locks).values()), 0)
        px = [2] * 64
        px[0] = 3
        _png(self.art / "b.png", px)
        _png(self.art / "c.png", [4] * 64)
        (self.art / "a.png").unlink()
        result = frame_lock.check_folder(self.art, self.locks)
        self.assertEqual((list(result["changed"]), list(result["added"]), list(result["removed"])), (["b.png"], ["c.png"], ["a.png"]))
        self.assertEqual(result["removed"]["a.png"], [[0, 1, 2]])

    def test_cli_exit_codes_and_sheet(self):
        old_locks = frame_lock.LOCKS
        frame_lock.LOCKS = self.locks
        try:
            self.assertEqual(frame_lock._main(["check", str(self.art)]), 2)
            self.assertEqual(frame_lock._main(["lock", str(self.art), "--note", "n"]), 0)
            self.assertEqual(frame_lock._main(["check", str(self.art)]), 0)
            with self.assertRaises(FileExistsError):
                frame_lock._main(["lock", str(self.art)])
            _png(self.art / "b.png", [3] * 64)
            sheet = self.tmp / "s.png"
            self.assertEqual(frame_lock._main(["check", str(self.art), "--sheet", str(sheet)]), 1)
            self.assertTrue(sheet.exists())
            self.assertEqual(frame_lock._main(["lock", str(self.art), "--replace"]), 0)
            self.assertEqual(len(list(self.locks.iterdir())), 2)
            self.assertEqual(frame_lock._main(["check", str(self.art)]), 0)
        finally:
            frame_lock.LOCKS = old_locks

    def test_only_list_limits_lock_and_check(self):
        frame_lock.lock_folder(self.art, "t", self.locks, only=["a.png"])
        _png(self.art / "c.png", [4] * 64)
        self.assertEqual(sum(len(v) for v in frame_lock.check_folder(self.art, self.locks).values()), 0)


if __name__ == "__main__":
    unittest.main()
