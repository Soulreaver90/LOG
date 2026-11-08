r"""
test_map_editor_io.py - The editor's writes: a saved map, the stamp library, and the autosave.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_io.py -v

Everything here writes into a temporary folder. Nothing writes under data\, and no ROM is opened
except the one read map_file already does at import.

These are the helpers serve.py's POST routes call. The HTTP layer is a handful of lines around
them; the rules that matter, which are that a saved map is VALIDATED, that nothing is ever
overwritten and that a name can never carry a path, live here.

THE AUTOSAVE BREAKS TWO OF THOSE RULES ON PURPOSE, and the tests below pin which two. It is not
validated, because work in progress is often not sound yet and refusing to keep it is the failure
the folder exists to stop. It IS overwritten, because its job is to hold the newest state. What
keeps that safe is the session id: a write from another session moves the file aside first.
"""
import json
import os
import sys
import tempfile
import time
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


class StampRemovalTests(unittest.TestCase):
    """Deleting a stamp, and dropping a stamp's collision. Neither is a one-way door."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.deleted = self.folder / "library" / "deleted"
        serve.save_stamp(dict(STAMP), self.folder)

    def test_a_deleted_stamp_moves_into_deleted_and_leaves_the_library(self):
        moved = serve.delete_stamp("boulder", self.folder)
        self.assertEqual(moved.parent, self.deleted)
        self.assertEqual(json.loads(moved.read_text(encoding="utf-8"))["name"], "boulder")
        self.assertEqual(serve.stamps(self.folder), [])
        self.assertFalse((self.folder / "library" / "boulder.json").exists())

    def test_nothing_under_deleted_is_ever_offered_again(self):
        """stamps() globs library\\*.json, which is not recursive. This pins that it stays so."""
        self.deleted.mkdir(parents=True, exist_ok=True)
        (self.deleted / "old one.json").write_text(json.dumps({**STAMP, "name": "old one"}),
                                                   encoding="utf-8")
        self.assertEqual([s["name"] for s in serve.stamps(self.folder)], ["boulder"])

    def test_deleting_a_stamp_that_is_not_there_is_refused(self):
        with self.assertRaises(FileNotFoundError):
            serve.delete_stamp("no such stamp", self.folder)

    def test_a_second_stamp_of_one_name_never_overwrites_the_first_deleted_copy(self):
        first = serve.delete_stamp("boulder", self.folder)
        serve.save_stamp({**STAMP, "collision": [0, 0, 0, 0]}, self.folder)
        second = serve.delete_stamp("boulder", self.folder)
        self.assertNotEqual(first, second)
        self.assertEqual(json.loads(first.read_text(encoding="utf-8"))["collision"], [1, 0, 0, 1])

    def test_stripping_a_stamp_drops_its_collision_and_keeps_the_old_copy(self):
        stamp = serve.strip_stamp("boulder", self.folder)
        self.assertIsNone(stamp["collision"])
        kept = serve.stamps(self.folder)
        self.assertEqual(len(kept), 1)
        self.assertIsNone(kept[0]["collision"])
        self.assertEqual(kept[0]["cells"], STAMP["cells"])          # the art is untouched
        old = list(self.deleted.glob("*.json"))
        self.assertEqual(len(old), 1)
        self.assertEqual(json.loads(old[0].read_text(encoding="utf-8"))["collision"], [1, 0, 0, 1])

    def test_stripping_a_stamp_that_carries_no_collision_keeps_no_extra_copy(self):
        serve.strip_stamp("boulder", self.folder)
        serve.strip_stamp("boulder", self.folder)
        self.assertEqual(len(list(self.deleted.glob("*.json"))), 1)


class AutosaveTests(unittest.TestCase):
    """The net under unsaved work. Nothing here is validated and nothing here is a saved map."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.doc = map_file.blank((2, 2), (512, 512))

    def keep(self, title="map 7,15", session="one", doc=None):
        return serve.autosave_write({"name": title, "session": session,
                                     "doc": self.doc if doc is None else doc}, self.folder)

    def test_an_autosave_comes_back_whole(self):
        self.keep()
        record = serve.autosave_read("map 7 15", self.folder)
        self.assertEqual(record["doc"], self.doc)
        self.assertEqual(record["title"], "map 7,15")

    def test_an_unsound_document_is_kept_anyway(self):
        """The one place in this tool that keeps an unsound map. Refusing it is the lost evening."""
        broken = map_file.blank((2, 2), (512, 512))
        broken["world"] = [4096, 4096]
        self.assertTrue(map_file.validate(broken))
        self.keep(doc=broken)
        self.assertEqual(serve.autosave_read("map 7 15", self.folder)["doc"], broken)

    def test_the_same_session_overwrites_in_place(self):
        self.keep()
        self.keep(doc={**self.doc, "schema": map_file.SCHEMA, "marker": 2})
        self.assertEqual(serve.autosave_read("map 7 15", self.folder)["doc"]["marker"], 2)
        self.assertFalse((self.folder / "autosave" / "older").exists())

    def test_another_session_moves_the_first_aside_before_it_writes(self):
        """A second tab, or a page that was offered this file and did not take it."""
        self.keep(session="one")
        answer = self.keep(session="two", doc={**self.doc, "marker": 2})
        self.assertTrue(answer["moved"])
        older = list((self.folder / "autosave" / "older").glob("*.json"))
        self.assertEqual(len(older), 1)
        self.assertEqual(json.loads(older[0].read_text(encoding="utf-8"))["session"], "one")
        self.assertEqual(serve.autosave_read("map 7 15", self.folder)["doc"]["marker"], 2)

    def test_an_autosave_is_never_a_saved_map(self):
        self.keep()
        self.assertEqual(serve.saved_maps(self.folder), [])

    def test_two_titles_that_differ_only_in_punctuation_stay_apart(self):
        self.assertNotEqual(serve.autosave_key("map 7,15"), serve.autosave_key("map 71,5"))

    def test_a_title_cannot_carry_a_path(self):
        self.keep(title="../../escaped")
        self.assertEqual([p.name for p in (self.folder / "autosave").glob("*.json")],
                         ["escaped.json"])

    def test_one_with_no_saved_map_is_always_offered(self):
        self.keep()
        offered = serve.autosaves(self.folder)
        self.assertEqual([row["name"] for row in offered], ["map 7 15"])
        self.assertIsNone(offered[0]["saved_at"])

    def test_one_older_than_its_saved_map_is_not_offered(self):
        """He saved the map after that autosave, so it holds nothing he does not already have."""
        self.keep(title="field")
        serve.save_map(self.doc, "field", self.folder)
        os.utime(self.folder / "maps" / "field.json", (time.time() + 60, time.time() + 60))
        self.assertEqual(serve.autosaves(self.folder), [])

    def test_one_newer_than_its_saved_map_is_offered(self):
        serve.save_map(self.doc, "field", self.folder)
        os.utime(self.folder / "maps" / "field.json", (time.time() - 60, time.time() - 60))
        self.keep(title="field")
        self.assertEqual([row["name"] for row in serve.autosaves(self.folder)], ["field"])

    def test_a_file_that_will_not_parse_is_left_out_rather_than_fatal(self):
        (self.folder / "autosave").mkdir(parents=True, exist_ok=True)
        (self.folder / "autosave" / "half written.json").write_text("{", encoding="utf-8")
        self.keep()
        self.assertEqual([row["name"] for row in serve.autosaves(self.folder)], ["map 7 15"])

    def test_retiring_moves_the_net_aside_and_stops_the_offer(self):
        self.keep(title="field")
        self.assertTrue(serve.autosave_retire("field", self.folder))
        self.assertEqual(serve.autosaves(self.folder), [])
        self.assertEqual(len(list((self.folder / "autosave" / "older").glob("*.json"))), 1)

    def test_retiring_when_there_is_nothing_to_retire_says_so(self):
        self.assertFalse(serve.autosave_retire("field", self.folder))

    def test_a_save_retires_the_autosave_only_when_the_file_is_written(self):
        """The order the route runs in: save first, retire after. A refused save keeps its net."""
        self.keep(title="field")
        broken = map_file.blank((2, 2), (512, 512))
        broken["world"] = [4096, 4096]
        with self.assertRaises(ValueError):
            serve.save_map(broken, "field", self.folder)
        self.assertEqual([row["name"] for row in serve.autosaves(self.folder)], ["field"])

    def test_reading_an_autosave_that_is_not_there_is_refused(self):
        with self.assertRaises(FileNotFoundError):
            serve.autosave_read("nothing", self.folder)


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
