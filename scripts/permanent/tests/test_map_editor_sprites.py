r"""
test_map_editor_sprites.py - The size ruler: the sprite export, its anchor, and what it must not touch.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_sprites.py -v

WHY THIS FILE EXISTS. The editor's 240 x 160 screen box says what fits on screen and nothing about
how big a person is beside a hill. The ruler stands one standing frame on the map so that question
has an answer. The one thing that decides whether it is useful or decorative is the ANCHOR: a
frame is a padded box and the figure does not fill it, so a sprite dropped by its image corner is
wrong by whatever padding that frame carries. Imperfect Cell's stand is a 64 x 64 picture whose
record reads dx -20, dy -56. By its corner he stands 20 px right and 8 px low.

THE NUMBERS BELOW ARE WRITTEN OUT ON PURPOSE. Recomputing them from the same reader the exporter
uses would only prove that one function agrees with itself. These are the measured values, and
the envelopes are the ones bible B0246 carries, so a reader that starts resolving the wrong set
table, or a frame record whose meaning was misread, fails here.

Read-only on the ROM. Everything written goes to a temporary folder. Nothing writes under data\,
and nothing touches the owner's own map-editor\assets\, maps\ or library\.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

EDITOR = Path(__file__).resolve().parents[1] / "map-editor"
sys.path.insert(0, str(EDITOR))

import export_assets                                                      # noqa: E402
from scene import map_view                                                # noqa: E402

# Boxes are [x0, y0, x1, y1] in pixels FROM THE ACTOR'S POINT, x1 and y1 exclusive.
#   box        the frame record's own box: where the PNG is drawn
#   ink        the pixels this one standing frame really draws
#   envelope   every record of the whole set, which is bible B0246's measure
EXPECTED = {
    60:  {"name": "Goku", "size": (16, 32),
          "box": [0, -24, 16, 8], "ink": [0, -24, 16, 8], "envelope": [-12, -24, 28, 8]},
    132: {"name": "Trunks", "size": (16, 32),
          "box": [0, -24, 16, 8], "ink": [1, -21, 16, 8], "envelope": [-8, -24, 24, 8]},
    133: {"name": "Trunks, Super Saiyan", "size": (16, 32),
          "box": [0, -24, 16, 8], "ink": [1, -24, 16, 8], "envelope": [-8, -24, 24, 8]},
    28:  {"name": "Imperfect Cell", "size": (64, 64),
          "box": [-20, -56, 44, 8], "ink": [-14, -40, 27, 8], "envelope": [-20, -56, 44, 8]},
}

# The one module that may never make the map dirty. The sprite is a reference overlay: it is not
# saved, not exported and never placed as tiles, so a change to it must not start the autosave or
# put the unsaved marker on the owner's tab.
RULER_JS = EDITOR / "editor" / "ruler.js"
FORBIDDEN = ["markDirty", "edit(", "setDoc", "setView", "notify("]


def _rom():
    return map_view.BASE.read_bytes()


class SpriteExportTests(unittest.TestCase):
    """What export_sprites writes, and what it refuses to write over."""

    @classmethod
    def setUpClass(cls):
        cls._temp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._temp.name) / "sprites"
        cls.manifest = export_assets.export_sprites(_rom(), cls.out)
        cls.by_set = {entry["set"]: entry for entry in cls.manifest["sprites"]}

    @classmethod
    def tearDownClass(cls):
        cls._temp.cleanup()

    def test_every_configured_set_is_exported_with_its_png(self):
        self.assertEqual([s["set"] for s in self.manifest["sprites"]],
                         [set_id for set_id, _ in export_assets.SPRITE_SETS])
        for entry in self.manifest["sprites"]:
            self.assertTrue((self.out / entry["png"]).is_file(), entry["png"])

    def test_the_manifest_is_the_json_on_disk(self):
        written = json.loads((self.out / "sprites.json").read_text(encoding="utf-8"))
        self.assertEqual(written, self.manifest)

    def test_the_anchor_is_the_frame_records_own_offsets(self):
        """THE TEST THIS FILE IS FOR. The box is where the page draws the PNG, measured from the
        actor's point. Cell at [-20, -56] is the one that makes a corner drop visibly wrong."""
        for set_id, want in EXPECTED.items():
            self.assertEqual(self.by_set[set_id]["box"], want["box"], f"set {set_id} box")

    def test_the_frame_size_matches_the_box(self):
        for set_id, want in EXPECTED.items():
            entry = self.by_set[set_id]
            self.assertEqual((entry["w"], entry["h"]), want["size"], f"set {set_id} size")
            self.assertEqual(entry["box"][2] - entry["box"][0], entry["w"])
            self.assertEqual(entry["box"][3] - entry["box"][1], entry["h"])

    def test_the_ink_is_the_pixels_really_drawn_and_is_inside_the_box(self):
        """Cell's frame reaches 56 px above the point and his STAND reaches 40. A screenshot check
        of "56 px of headroom" against the stand would be measuring empty padding."""
        for set_id, want in EXPECTED.items():
            entry = self.by_set[set_id]
            self.assertEqual(entry["ink"], want["ink"], f"set {set_id} ink")
            self.assertGreaterEqual(entry["ink"][0], entry["box"][0])
            self.assertGreaterEqual(entry["ink"][1], entry["box"][1])
            self.assertLessEqual(entry["ink"][2], entry["box"][2])
            self.assertLessEqual(entry["ink"][3], entry["box"][3])

    def test_the_envelope_is_the_one_bible_B0246_measured(self):
        """B0246: set 28 is 20 left, 44 right, 56 up, 8 down; sets 132 and 133 are 8, 24, 24, 8."""
        for set_id, want in EXPECTED.items():
            self.assertEqual(self.by_set[set_id]["envelope"], want["envelope"], f"set {set_id}")

    def test_the_stand_is_anim_zero_facing_the_camera(self):
        """Anim 0 index 0 is what standing still looks like: the idle tick @0x08007570 holds index
        0 for 241 of 256 ticks (bible B0101). Dir 0 faces the camera (B0078)."""
        for entry in self.manifest["sprites"]:
            self.assertEqual((entry["anim"], entry["dir"], entry["index"]), (0, 0, 0),
                             f"set {entry['set']}")

    def test_the_png_is_the_size_the_record_declares(self):
        from PIL import Image
        for set_id, want in EXPECTED.items():
            with Image.open(self.out / self.by_set[set_id]["png"]) as image:
                self.assertEqual(image.size, want["size"], f"set {set_id}")
                self.assertEqual(image.mode, "P", f"set {set_id}")

    def test_the_png_draws_nothing_outside_the_ink_the_manifest_reports(self):
        """The page measures a screenshot against "ink", so the PNG's own opaque bounds must be
        it. A drift here would make every live measurement of the figure's height wrong."""
        from PIL import Image
        for set_id in EXPECTED:
            entry = self.by_set[set_id]
            with Image.open(self.out / entry["png"]) as image:
                pixels = image.tobytes()                   # mode P: one palette index per pixel
            width = entry["w"]
            drawn = [(n % width, n // width) for n, value in enumerate(pixels) if value != 0]
            self.assertTrue(drawn, f"set {set_id} draws nothing")
            self.assertEqual(
                [min(x for x, _ in drawn) + entry["box"][0],
                 min(y for _, y in drawn) + entry["box"][1],
                 max(x for x, _ in drawn) + 1 + entry["box"][0],
                 max(y for _, y in drawn) + 1 + entry["box"][1]],
                entry["ink"], f"set {set_id}")

    def test_colour_zero_is_marked_transparent(self):
        """The GBA draws OBJ colour 0 as nothing. Without the tRNS marker the page would stand a
        black rectangle on the map instead of a character."""
        from PIL import Image
        self.assertEqual(self.manifest["transparent_index"], 0)
        for entry in self.manifest["sprites"]:
            with Image.open(self.out / entry["png"]) as image:
                self.assertEqual(image.info.get("transparency"), 0, entry["png"])

    def test_a_folder_that_already_holds_something_is_never_written_over(self):
        with self.assertRaises(FileExistsError):
            export_assets.export_sprites(_rom(), self.out)


class AssetFolderTests(unittest.TestCase):
    r"""The two doors: a first export, and a top-up of an assets folder written before this existed.

    The top-up is the one that matters on the owner's machine. His assets\ already holds
    assets.json, and export() refuses a folder that is not empty, so without a separate step his
    editor could never gain a sprite.
    """

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_a_full_export_writes_the_sprites_beside_the_atlases(self):
        assets = self.folder / "assets"
        export_assets.export(_rom(), assets)
        self.assertTrue((assets / "assets.json").is_file())
        sprites = assets / export_assets.SPRITES_IN / "sprites.json"
        self.assertTrue(sprites.is_file())
        self.assertEqual(len(json.loads(sprites.read_text(encoding="utf-8"))["sprites"]),
                         len(export_assets.SPRITE_SETS))

    def test_the_server_tops_up_an_assets_folder_that_has_no_sprites(self):
        import serve
        assets = self.folder / "assets"
        export_assets.export(_rom(), assets)
        import shutil
        shutil.rmtree(assets / export_assets.SPRITES_IN)         # an assets\ from before the ruler
        original = serve.ASSETS
        try:
            serve.ASSETS = assets
            serve.ensure_assets()
        finally:
            serve.ASSETS = original
        self.assertTrue((assets / export_assets.SPRITES_IN / "sprites.json").is_file())

    def test_the_server_leaves_a_complete_assets_folder_alone(self):
        import serve
        assets = self.folder / "assets"
        export_assets.export(_rom(), assets)
        before = sorted(p.name for p in (assets / export_assets.SPRITES_IN).iterdir())
        stamp = (assets / export_assets.SPRITES_IN / "sprites.json").stat().st_mtime_ns
        original = serve.ASSETS
        try:
            serve.ASSETS = assets
            serve.ensure_assets()
        finally:
            serve.ASSETS = original
        self.assertEqual(sorted(p.name for p in (assets / export_assets.SPRITES_IN).iterdir()),
                         before)
        self.assertEqual((assets / export_assets.SPRITES_IN / "sprites.json").stat().st_mtime_ns,
                         stamp)

    def test_a_half_written_sprites_folder_does_not_stop_the_editor_opening(self):
        """Loud, never fatal. An interrupted export must not block every map he wants to open."""
        import serve
        assets = self.folder / "assets"
        export_assets.export(_rom(), assets)
        (assets / export_assets.SPRITES_IN / "sprites.json").unlink()
        original = serve.ASSETS
        try:
            serve.ASSETS = assets
            serve.ensure_assets()                                # must not raise
        finally:
            serve.ASSETS = original


class NotPartOfTheDocumentTests(unittest.TestCase):
    """A STATIC check, and it is named one. It reads ruler.js and proves the module never reaches
    for the calls that would mark the map dirty. What it cannot prove is what a running page does,
    so the live proof is a drag in the browser with state.dirty read before and after it."""

    def setUp(self):
        self.source = RULER_JS.read_text(encoding="utf-8")

    def test_the_file_is_there_and_carries_no_byte_order_mark(self):
        self.assertTrue(RULER_JS.is_file())
        self.assertFalse(RULER_JS.read_bytes().startswith(b"\xef\xbb\xbf"))

    def test_it_never_calls_anything_that_marks_the_map_dirty(self):
        """The comments are stripped first. The header says the words "markDirty" and "setView"
        while explaining that the module never calls them, and a search of the whole file would
        find its own documentation and report the opposite of the truth."""
        body = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", self.source, flags=re.S))
        for name in FORBIDDEN:
            self.assertNotIn(name, body, f"ruler.js reaches for {name}")

    def test_it_imports_only_what_it_reads_the_map_with(self):
        imports = [line for line in self.source.splitlines() if line.startswith("import ")]
        self.assertEqual(imports, ['import { state, subscribe } from "./state.js";',
                                   'import { layerSize } from "./render.js";'])


if __name__ == "__main__":
    unittest.main()
