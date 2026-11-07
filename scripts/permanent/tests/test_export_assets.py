r"""
test_export_assets.py - Tests for map-editor\export_assets.py, the ROM to editor art export.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest tests.test_export_assets -v      (from scripts\permanent)
Reads the base ROM only. Every export goes to a fresh temp folder that the test removes.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scene import map_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import export_assets                                                        # noqa: E402
import tile_stream                                                          # noqa: E402

ROM = map_view.BASE.read_bytes()
CHUNK_COUNT = 168               # measured in Task 1: the shared pool
SHORT_CHUNK = (167, 167)        # (chunk, tiles): the one partial chunk
PROBES = ((0, 0), (5, 200), (100, 255), (167, 166))     # (chunk, tile) pairs read back pixel by pixel


class ExportAssetsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name) / "assets"
        cls.written = export_assets.export(ROM, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_export_writes_one_atlas_per_chunk_that_holds_tiles(self):
        self.assertEqual(len(self.written["chunks"]), CHUNK_COUNT)
        self.assertEqual([c["index"] for c in self.written["chunks"]], list(range(CHUNK_COUNT)))
        for entry in self.written["chunks"]:
            self.assertTrue((self.out / entry["png"]).is_file(), entry["png"])
        short = self.written["chunks"][SHORT_CHUNK[0]]
        self.assertEqual(short["tiles"], SHORT_CHUNK[1])
        self.assertEqual({c["tiles"] for c in self.written["chunks"]} - {256}, {SHORT_CHUNK[1]})

    def test_assets_json_tile_counts_match_the_atlas_pixel_sizes(self):
        on_disk = json.loads((self.out / "assets.json").read_text())
        self.assertEqual(on_disk, self.written)
        self.assertEqual(on_disk["tile_budget"], tile_stream.TILE_BUDGET)
        for entry in on_disk["chunks"]:
            with Image.open(self.out / entry["png"]) as atlas:
                rows = -(-entry["tiles"] // export_assets.ATLAS_COLUMNS)
                self.assertEqual(atlas.size, (8 * export_assets.ATLAS_COLUMNS, 8 * rows), entry["png"])

    def test_atlas_pixels_are_the_rom_tile_bytes_at_the_right_cell(self):
        table = tile_stream.CHUNK_TABLE
        for chunk, tile in PROBES:
            want = tile_stream.tiles_of(ROM, [(chunk, tile)], table)[0]
            with Image.open(self.out / self.written["chunks"][chunk]["png"]) as atlas:
                col, row = tile % 16, tile // 16
                got = atlas.crop((8 * col, 8 * row, 8 * col + 8, 8 * row + 8)).tobytes()
            self.assertEqual(got, want, (chunk, tile))

    def test_palette_matches_the_game_bg_palette_and_the_atlas_carries_it(self):
        flat = map_view.palette(ROM)
        palette = self.written["palettes"][0]
        self.assertEqual(len(palette), 256)
        self.assertEqual([v for rgb in palette for v in rgb], flat)
        with Image.open(self.out / self.written["chunks"][0]["png"]) as atlas:
            self.assertEqual(atlas.mode, "P")
            self.assertEqual(atlas.getpalette()[:768], flat)
        with Image.open(self.out / "palettes.png") as swatch:
            self.assertEqual(swatch.convert("RGB").getpixel((3, 0)), tuple(palette[3]))

    def test_export_refuses_to_write_into_a_non_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "keep.txt").write_text("mine")
            with self.assertRaises(FileExistsError):
                export_assets.export(ROM, Path(tmp))
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["keep.txt"])

    def test_export_accepts_an_empty_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(export_assets.export(ROM, Path(tmp)), self.written)


if __name__ == "__main__":
    unittest.main()
