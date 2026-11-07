r"""
test_map_editor_io.py - The editor's two writes: a saved map, and the stamp library.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_io.py -v

Everything here writes into a temporary folder. Nothing writes under data\, and no ROM is opened
except the one read map_file already does at import.

These are the helpers serve.py's two POST routes call. The HTTP layer is a handful of lines around
them; the rules that matter, which are that a saved map is VALIDATED, that nothing is ever
overwritten and that a name can never carry a path, live here.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import map_file                                                            # noqa: E402
import serve                                                              # noqa: E402

STAMP = {"name": "boulder", "w": 2, "h": 2,
         "cells": {"bg3": [[4, 7, 0], None, None, [4, 8, 0x400]]},
         "collision": [1, 0, 0, 1]}


class SavedMapTests(unittest.TestCase):
    """A map the owner composed, on its way to disk and back."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.doc = map_file.blank((2, 2), (512, 512))

    def test_save_then_load_returns_the_same_document(self):
        serve.save_map(self.doc, "first field", self.folder)
        self.assertEqual(serve.saved_maps(self.folder), ["first field"])
        self.assertEqual(serve.load_map("first field", self.folder), self.doc)

    def test_a_second_save_of_one_name_is_refused_and_leaves_the_first(self):
        serve.save_map(self.doc, "field", self.folder)
        other = map_file.blank((3, 3), (768, 768))
        with self.assertRaises(FileExistsError) as caught:
            serve.save_map(other, "field", self.folder)
        self.assertIn("field", str(caught.exception))
        self.assertEqual(serve.load_map("field", self.folder)["blocks"], [2, 2])

    def test_an_unsound_document_never_reaches_the_disk(self):
        """The gate the browser must not be able to walk around: validate, then write."""
        self.doc["world"] = [4096, 4096]                 # a 512 px grid cannot cover it
        with self.assertRaises(ValueError) as caught:
            serve.save_map(self.doc, "broken", self.folder)
        self.assertIn("cannot cover", str(caught.exception))
        self.assertEqual(serve.saved_maps(self.folder), [])

    def test_a_name_cannot_carry_a_path(self):
        serve.save_map(self.doc, "../../escaped", self.folder)
        self.assertEqual(serve.saved_maps(self.folder), ["escaped"])
        self.assertTrue((self.folder / serve.MAPS_IN / "escaped.json").is_file())

    def test_a_name_of_punctuation_alone_is_refused(self):
        with self.assertRaises(ValueError):
            serve.save_map(self.doc, "../", self.folder)

    def test_saved_maps_is_empty_before_the_first_save(self):
        self.assertEqual(serve.saved_maps(self.folder), [])


class StampLibraryTests(unittest.TestCase):
    """The library is files, because a stamp grabbed in one map is placed in another."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_a_stamp_round_trips_with_its_cells_and_its_collision(self):
        serve.save_stamp(STAMP, self.folder)
        self.assertEqual(serve.stamps(self.folder), [STAMP])

    def test_a_second_stamp_of_one_name_is_refused(self):
        serve.save_stamp(STAMP, self.folder)
        with self.assertRaises(FileExistsError):
            serve.save_stamp(STAMP, self.folder)

    def test_a_stamp_without_cells_is_refused(self):
        with self.assertRaises(ValueError):
            serve.save_stamp({"name": "empty", "w": 1, "h": 1}, self.folder)

    def test_a_file_that_will_not_parse_is_left_out_rather_than_fatal(self):
        serve.save_stamp(STAMP, self.folder)
        (self.folder / serve.STAMPS_IN / "half written.json").write_text("{", encoding="utf-8")
        self.assertEqual([s["name"] for s in serve.stamps(self.folder)], ["boulder"])

    def test_the_library_is_empty_before_the_first_grab(self):
        self.assertEqual(serve.stamps(self.folder), [])


class StampShapeTests(unittest.TestCase):
    """A placement, which is what the document carries, must pass map_file.validate."""

    def test_a_placement_the_editor_writes_validates(self):
        doc = map_file.blank((2, 2), (512, 512))
        doc["stamps"].append({"name": "boulder", "layer": "bg3", "x": 4, "y": 4, "w": 2, "h": 2})
        self.assertEqual(map_file.validate(doc), [])

    def test_a_placement_past_the_grid_is_reported(self):
        doc = map_file.blank((2, 2), (512, 512))
        doc["stamps"].append({"name": "boulder", "layer": "bg3", "x": 63, "y": 0, "w": 4, "h": 1})
        self.assertTrue(any("runs past" in p for p in map_file.validate(doc)))

    def test_a_saved_map_keeps_its_placements(self):
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        doc = map_file.blank((2, 2), (512, 512))
        doc["stamps"].append({"name": "boulder", "layer": "bg3", "x": 1, "y": 1, "w": 2, "h": 2})
        serve.save_map(doc, "with a stamp", folder)
        self.assertEqual(serve.load_map("with a stamp", folder)["stamps"], doc["stamps"])


if __name__ == "__main__":
    unittest.main()
