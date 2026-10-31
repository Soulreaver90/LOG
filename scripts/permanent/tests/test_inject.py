r"""
test_inject.py - Tests for inject.py: the tables, the PNG checks, the build, the verify step and the file rules.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_inject.py -v
Each command test runs inject.main against a temporary folder: a copy of art\tables, a build folder
whose log2_poc_r1.gba is the current build list built in memory (plus a fake .sav and .ss1), and a temporary
build log. The real builds, art tables and docs\build-log.md are never touched.
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from art import art_tables as at
from art import inject
from patches import art_inject
from tests.test_art_inject import BASE_ROM, built, diff, edited

# ===== constants =====
SAV, SS1 = b"S" * 8192, b"T" * 1000
CELL = at.ART_DIR / "portraits" / "040_cell_40.png"


def run(where: inject.Where, *argv) -> tuple:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = inject.main([str(a) for a in argv], where)
    return code, out.getvalue()


def rgb_png(path: Path, px: bytes, size: tuple = (64, 64), extra: dict = None) -> Path:
    """An RGB PNG of OBJ indices px; extra = {pixel index: rgb} overrides."""
    pal = at.obj_palette(BASE_ROM)
    colors = [pal[k] for k in px] + [pal[2]] * (size[0] * size[1] - len(px))
    for i, rgb in (extra or {}).items():
        colors[i] = rgb
    img = Image.new("RGB", size)
    img.putdata(colors[:size[0] * size[1]])
    img.save(path)
    return path


class Folder:
    """A temporary art copy, build folder with r1 (+ .sav, .ss1) and build log."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        shutil.copytree(at.ART_DIR, root / "art")
        (root / "build").mkdir()
        (root / "build" / "log2_poc_r1.gba").write_bytes(built()["rom"])
        (root / "build" / "log2_poc_r1.sav").write_bytes(SAV)
        (root / "build" / "log2_poc_r1.ss1").write_bytes(SS1)
        self.root = root
        self.where = inject.Where(build=root / "build", art=root / "art", log=root / "build-log.md")

    def rom(self, n: int) -> bytes:
        return (self.root / "build" / f"log2_poc_r{n}.gba").read_bytes()

    def files(self) -> dict:
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}


# ===== tests =====

class TableTests(unittest.TestCase):
    def test_tables_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            table, palette = at.load_portraits(), at.load_palette()
            at.save_portraits(table, Path(tmp) / "p.json")
            at.save_palette({172: (248, 224, 208)}, Path(tmp) / "c.json")
            self.assertEqual((Path(tmp) / "p.json").read_text(), at.PORTRAITS_JSON.read_text())
            self.assertEqual(at.load_portraits(Path(tmp) / "p.json"), table)
            self.assertEqual(at.load_palette(Path(tmp) / "c.json"), {172: (248, 224, 208)})
            self.assertEqual(json.loads((Path(tmp) / "c.json").read_text()), {"172": [248, 224, 208]})
        with tempfile.TemporaryDirectory() as tmp:                 # My table (172 since r24) round trips
            at.save_palette(palette, Path(tmp) / "c.json")
            self.assertEqual((Path(tmp) / "c.json").read_text(), at.PALETTE_JSON.read_text())

    def test_latest_build_ignores_other_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("log2_poc_r6_hud.gba", "log2_poc_t6.gba", "log2_poc_r10.gba", "log2_poc_r9.gba",
                         "log2_poc_r9.sav", "log2_poc_r9.ss2", "log2_poc_r10_x.sav"):
                (Path(tmp) / name).write_bytes(b"")
            self.assertEqual(inject.latest_build(Path(tmp))[0], 10)
            self.assertEqual([p.name for p in inject.latest_states(Path(tmp))], ["log2_poc_r9.sav", "log2_poc_r9.ss2"])

    def test_diff_runs_and_classify(self):
        a, b = bytes(0x3000), bytearray(0x3000)
        b[0x10:0x14], b[0x2FFF] = b"\x01\x02\x03\x04", 9
        runs = inject.diff_runs(a, bytes(b))
        self.assertEqual(runs, [(0x10, 0x14), (0x2FFF, 0x3000)])
        hits, stray = inject.classify(runs, [(0x10, 0x14, "word", 1)])
        self.assertEqual((hits, stray), ({0: 4}, [(0x2FFF, 0x3000)]))


class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = Folder()
        cls.dir = cls.f.root
        cls.cell = at.live_frame(built()["rom"], built()["notes"]["npc_gi"]["block"], 40)[1]

    @classmethod
    def tearDownClass(cls):
        cls.f.tmp.cleanup()

    def check(self, png: Path, *extra) -> tuple:
        return run(self.f.where, "check", png, *extra)

    def test_check_accepts_the_owner_png_and_its_rgb_twin(self):
        self.assertEqual(self.check(CELL, 40)[0], 0)
        code, out = self.check(rgb_png(self.dir / "c.png", self.cell), 40)          # value-mapped, same pixels
        self.assertEqual(code, 0, out)
        self.assertIn("21 colors, frame equals id 40's frame", out)

    def test_check_refuses_a_wrong_size(self):
        code, out = self.check(rgb_png(self.dir / "s.png", self.cell, (64, 63)), 40)
        self.assertEqual(code, 1)
        self.assertIn("size is 64x63, must be 64x64", out)

    def test_check_refuses_an_off_palette_color_and_snap_maps_it(self):
        png = rgb_png(self.dir / "o.png", self.cell, extra={i: (4, 5, 5) for i in range(2000, 2023)})
        code, out = self.check(png, 40)
        self.assertEqual(code, 1)
        self.assertIn("color (4, 5, 5) x23 px is not in the OBJ palette; nearest index 1 (0, 0, 0)", out)
        code, out = self.check(png, 40, "--snap")
        self.assertEqual(code, 0, out)
        self.assertIn("snap   color (4, 5, 5) x23 px", out)

    def test_check_refuses_a_changed_frame(self):
        px = bytearray(self.cell)
        px[64 * 2 + 30] = 9 if px[64 * 2 + 30] != 9 else 2                # row 2: inside the 3 px ring
        code, out = self.check(rgb_png(self.dir / "f.png", px), 40)
        self.assertEqual(code, 1)
        self.assertIn("frame (outer 3 px) differs from id 40's current frame at 1 of 732 px", out)
        self.assertEqual(self.check(self.dir / "f.png")[0], 0)            # no id: the frame is not checked

    def test_check_refuses_more_than_64_colors(self):
        px, ok = bytearray(self.cell), sorted(at.dialog_indices(BASE_ROM))
        for k in range(65):
            px[(10 + k // 40) * 64 + 10 + k % 40] = ok[k]
        code, out = self.check(rgb_png(self.dir / "m.png", px), 40)
        self.assertEqual(code, 1)
        self.assertIn("the status page pool holds 64", out)

    def test_check_refuses_transparency_and_a_bad_id(self):
        img = Image.open(CELL).convert("RGBA")
        img.putpixel((30, 30), (0, 0, 0, 0))
        img.save(self.dir / "t.png")
        self.assertIn("transparent", self.check(self.dir / "t.png", 40)[1])
        code, out = run(self.f.where, "portrait", 116, CELL)
        self.assertEqual(code, 1)
        self.assertIn("id 116: use a dialog id", out)


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.f = Folder()
        self.addCleanup(self.f.tmp.cleanup)
        self.block = built()["notes"]["npc_gi"]["block"]

    def test_portrait_adds_an_id_and_builds_the_next_rom(self):
        px = edited(94)
        code, out = run(self.f.where, "portrait", 94, rgb_png(self.f.root / "piccolo.png", px), "--note", "test")
        self.assertEqual(code, 0, out)
        r1, r2 = self.f.rom(1), self.f.rom(2)
        slot, word = art_inject.slot(94), self.block + 4 + 4 * 94
        self.assertEqual([hex(i) for i in diff(r1, r2) if not (slot <= i < slot + 0x1008 or word <= i < word + 4)], [])
        self.assertEqual(at.live_frame(r2, self.block, 94)[1], px)
        table = at.load_portraits(self.f.where.portraits_json)
        self.assertEqual(table[94], {"png": "portraits/094_piccolo.png", "note": "test"})
        with Image.open(self.f.root / "art" / "portraits" / "094_piccolo.png") as img:   # stored indexed
            self.assertTrue(at.is_canonical(img, at.obj_palette(BASE_ROM), at.allowed_indices(BASE_ROM, {})))
            self.assertEqual(img.tobytes(), px)
        build = self.f.root / "build"
        self.assertEqual(((build / "log2_poc_r2.sav").read_bytes(), (build / "log2_poc_r2.ss1").read_bytes()),
                         (SAV, SS1))
        log = self.f.where.log.read_text().splitlines()
        self.assertEqual(len(log), 1)
        self.assertIn("inject log2_poc_r2.gba portrait 94 094_piccolo.png sha1=", log[0])
        self.assertIn("art sites only (slot 94; word 94)", log[0])

    def test_replacing_a_portrait_touches_only_its_slot(self):
        px = bytearray(built()["png"][63])
        px[40 * 64 + 20] = 9 if px[40 * 64 + 20] != 9 else 2
        code, out = run(self.f.where, "portrait", 63, rgb_png(self.f.root / "goku.png", px))
        self.assertEqual(code, 0, out)
        self.assertEqual(diff(self.f.rom(1), self.f.rom(2)), [art_inject.slot(63) + 8 + 40 * 64 + 20])
        self.assertIn("portrait pixels changed: [63]", out)

    def test_palette_command_writes_both_copies(self):
        rgb = (240, 216, 208)                    # differs from the table's 172 in all three channels
        self.assertNotIn(at.load_palette(self.f.where.palette_json).get(172), (rgb,))
        code, out = run(self.f.where, "palette", 172, ",".join(map(str, rgb)))
        self.assertEqual(code, 0, out)
        self.assertEqual([hex(i) for i in diff(self.f.rom(1), self.f.rom(2))],
                         ["0x1da820", "0x1da821", "0x3ed0a8", "0x3ed0a9", "0x3ed0aa"])
        self.assertEqual(at.load_palette(self.f.where.palette_json)[172], rgb)

    def test_never_overwrites_and_writes_nothing_when_refused(self):
        (self.f.root / "build" / "log2_poc_r2.sav").write_bytes(b"owner")
        before = self.f.files()
        code, out = run(self.f.where, "portrait", 40, CELL)
        self.assertEqual(code, 1)
        self.assertIn("refusing to overwrite log2_poc_r2.sav", out)
        self.assertEqual(self.f.files(), before)

    def test_a_failed_check_writes_nothing(self):
        before = self.f.files()
        png = rgb_png(self.f.root / "o.png", edited(94), extra={100: (1, 2, 3)})
        before["o.png"] = png.read_bytes()
        self.assertEqual(run(self.f.where, "portrait", 94, png)[0], 1)
        self.assertEqual(run(self.f.where, "palette", 0, "8,8,8")[0], 1)
        self.assertEqual(self.f.files(), before)

    def test_an_unexpected_diff_is_refused(self):
        prev = bytearray(self.f.rom(1))
        prev[0x89A4D0] ^= 0xFF                                              # status_portrait paint code
        (self.f.root / "build" / "log2_poc_r1.gba").write_bytes(prev)
        before = self.f.files()
        code, out = run(self.f.where, "portrait", 40, CELL)
        self.assertEqual(code, 1)
        self.assertIn("unexpected change rom:0x89A4D0-0x89A4D0 (1 bytes): not an art site", out)
        self.assertEqual(self.f.files(), before)

    def test_a_hand_edited_table_png_is_refused(self):
        stored = self.f.root / "art" / "portraits" / "063_goku_mid_A.png"
        with Image.open(stored) as img:
            px, pal = bytearray(img.tobytes()), img.getpalette()
        px[40 * 64 + 20] = 9 if px[40 * 64 + 20] != 9 else 2
        img = Image.frombytes("P", (64, 64), bytes(px))
        img.putpalette(pal)
        img.save(stored)
        before = self.f.files()
        for argv in (("portrait", 40, CELL), ("palette", 172, "248,224,208")):
            code, out = run(self.f.where, *argv)
            self.assertEqual(code, 1, argv)
            self.assertIn("portrait pixels changed for ids [63] that this command does not name", out)
        self.assertEqual(self.f.files(), before)

    def test_refuses_with_a_log_env_var(self):
        with mock.patch.dict(os.environ, {"LOG_GI_SSJ": "x"}):
            code, out = run(self.f.where, "portrait", 40, CELL)
        self.assertEqual(code, 1)
        self.assertIn("unset LOG_GI_SSJ", out)

    def test_list_prints_every_entry(self):
        code, out = run(self.f.where, "list")
        self.assertEqual(code, 0)
        for pid in (40, 63, 65, 106, 115, 117, 119):
            self.assertIn(f"rom:0x{art_inject.slot(pid):06X}", out)
        self.assertIn("next: log2_poc_r2.gba", out)


if __name__ == "__main__":
    unittest.main()
