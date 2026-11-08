r"""
test_map_editor_io.py - The editor's writes: a saved map, the stamp library, and the autosave.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_io.py -v

Everything here writes into a temporary folder. Nothing writes under data\, and no ROM is opened
except the one read map_file already does at import.

These are the helpers serve.py's POST routes call. The HTTP layer is a handful of lines around
them; the rules that matter, which are that a saved map is VALIDATED, that no file is ever lost
and that a name can never carry a path, live here.

A saved map of a name he already holds is a QUESTION and not a refusal, because composing one map
is a run of saves under one name. Nothing is written until he answers yes, and his yes MOVES the
old file into maps\older\ rather than over it.

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
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import map_file                                                            # noqa: E402
import serve                                                              # noqa: E402

STAMP = {"name": "boulder", "w": 2, "h": 2,
         "cells": {"bg3": [[4, 7, 0], None, None, [4, 8, 0x400]]},
         "collision": [1, 0, 0, 1]}

# A stamp grabbed from a map with waving grass in it. An animated cell is {"g", "t", "f"}, naming
# tile "t" of the stamp's OWN group "g", and the group travels as PIXELS so the stamp can place
# that grass into a map which has never held it. map-editor\editor\cells.js owns this format and
# test_map_editor_cells.py runs it.
WAVING = {"name": "grass patch", "w": 2, "h": 1,
          "cells": {"bg3": [[4, 7, 0], {"g": 0, "t": 1, "f": 0}]},
          "animated": [{"first": 892,
                        "frames": [{"duration": 20, "pixels": [7] * 128},
                                   {"duration": 20, "pixels": [9] * 128}]}],
          "collision": None}


class SavedMapTests(unittest.TestCase):
    """A map the owner composed, on its way to disk and back."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.doc = map_file.blank((2, 2), (512, 512))

    def test_save_then_load_returns_the_same_document(self):
        serve.save_map(self.doc, "first field", self.folder)
        self.assertEqual(serve.saved_maps(self.folder), ["first field"])
        self.assertEqual(serve.load_map("first field", self.folder), self.doc)

    def test_a_second_save_of_one_name_asks_rather_than_writing(self):
        """Saving one map again is how he works on it, so a taken name is a QUESTION. Without the
        flag the server writes NOTHING: the page asks him, and only his yes sends the flag."""
        serve.save_map(self.doc, "field", self.folder)
        other = map_file.blank((3, 3), (768, 768))
        with self.assertRaises(serve.NameTaken) as caught:
            serve.save_map(other, "field", self.folder)
        self.assertIn("field", str(caught.exception))
        self.assertEqual(serve.load_map("field", self.folder)["blocks"], [2, 2])
        self.assertFalse((self.folder / serve.MAPS_IN / serve.OLDER_IN).exists())

    def test_replacing_puts_the_new_map_in_place_and_keeps_the_old_one(self):
        """The old copy MOVES into maps\\older\\ and is never unlinked, so a wrong yes costs a
        trip to a folder rather than the map."""
        serve.save_map(self.doc, "field", self.folder)
        other = map_file.blank((3, 3), (768, 768))
        _path, moved = serve.save_map(other, "field", self.folder, replace=True)
        self.assertEqual(serve.load_map("field", self.folder)["blocks"], [3, 3])
        self.assertEqual(serve.saved_maps(self.folder), ["field"])
        older = sorted((self.folder / serve.MAPS_IN / serve.OLDER_IN).glob("*.json"))
        self.assertEqual([p.name for p in older], [moved])
        self.assertEqual(json.loads(older[0].read_text(encoding="utf-8"))["blocks"], [2, 2])

    def test_an_unsound_replacement_moves_nothing_and_changes_nothing(self):
        """Validate FIRST. If an unsound document retired the good file and then failed, his saved
        map would have left its place for a save that never happened."""
        serve.save_map(self.doc, "field", self.folder)
        broken = map_file.blank((2, 2), (512, 512))
        broken["world"] = [4096, 4096]
        with self.assertRaises(ValueError) as caught:
            serve.save_map(broken, "field", self.folder, replace=True)
        self.assertIn("cannot cover", str(caught.exception))
        self.assertEqual(serve.load_map("field", self.folder), self.doc)
        self.assertFalse((self.folder / serve.MAPS_IN / serve.OLDER_IN).exists())

    def test_an_unsound_document_under_a_taken_name_is_refused_before_the_question(self):
        """He must never be asked to replace a good map with one that cannot be saved."""
        serve.save_map(self.doc, "field", self.folder)
        broken = map_file.blank((2, 2), (512, 512))
        broken["world"] = [4096, 4096]
        with self.assertRaises(ValueError):
            serve.save_map(broken, "field", self.folder)

    def test_nothing_under_older_is_ever_offered_as_a_saved_map(self):
        """saved_maps() globs maps\\*.json, which is not recursive. This pins that it stays so."""
        serve.save_map(self.doc, "field", self.folder)
        older = self.folder / serve.MAPS_IN / serve.OLDER_IN
        older.mkdir(parents=True, exist_ok=True)
        (older / "field.json").write_text(json.dumps(self.doc), encoding="utf-8")
        (older / "an old one.json").write_text(json.dumps(self.doc), encoding="utf-8")
        self.assertEqual(serve.saved_maps(self.folder), ["field"])

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

    def test_a_second_stamp_of_one_name_asks_rather_than_writing(self):
        """He grabs one piece of art twice while composing, so a taken name is a QUESTION. Without
        the flag nothing is written and nothing moves: the page asks, and only his yes sends it."""
        serve.save_stamp(STAMP, self.folder)
        with self.assertRaises(serve.NameTaken) as caught:
            serve.save_stamp({**STAMP, "collision": None}, self.folder)
        self.assertIn("boulder", str(caught.exception))
        self.assertEqual(serve.stamps(self.folder), [STAMP])
        self.assertFalse((self.folder / serve.STAMPS_IN / serve.DELETED_IN).exists())

    def test_replacing_a_stamp_keeps_the_old_one_in_deleted(self):
        serve.save_stamp(STAMP, self.folder)
        _path, moved = serve.save_stamp({**STAMP, "collision": None}, self.folder, replace=True)
        self.assertEqual(serve.stamps(self.folder), [{**STAMP, "collision": None}])
        old = sorted((self.folder / serve.STAMPS_IN / serve.DELETED_IN).glob("*.json"))
        self.assertEqual([p.name for p in old], [moved])
        self.assertEqual(json.loads(old[0].read_text(encoding="utf-8"))["collision"], [1, 0, 0, 1])

    def test_a_stamp_without_cells_is_refused(self):
        with self.assertRaises(ValueError):
            serve.save_stamp({"name": "empty", "w": 1, "h": 1}, self.folder)

    def test_an_unsound_replacement_moves_nothing_and_changes_nothing(self):
        """The shape check runs before anything moves, so a bad grab cannot cost him the stamp."""
        serve.save_stamp(STAMP, self.folder)
        with self.assertRaises(ValueError):
            serve.save_stamp({"name": "boulder", "w": 1, "h": 1}, self.folder, replace=True)
        self.assertEqual(serve.stamps(self.folder), [STAMP])
        self.assertFalse((self.folder / serve.STAMPS_IN / serve.DELETED_IN).exists())

    def test_a_file_that_will_not_parse_is_left_out_rather_than_fatal(self):
        serve.save_stamp(STAMP, self.folder)
        (self.folder / serve.STAMPS_IN / "half written.json").write_text("{", encoding="utf-8")
        self.assertEqual([s["name"] for s in serve.stamps(self.folder)], ["boulder"])

    def test_the_library_is_empty_before_the_first_grab(self):
        self.assertEqual(serve.stamps(self.folder), [])


class AnimatedStampTests(unittest.TestCase):
    """A stamp may carry animated groups, and a cell may name one instead of a pool tile.

    THE DEFECT THIS SHAPE EXISTS FOR. A grab used to store null wherever a cell named an animated
    group, because a group slot has no [chunk, tile] pair behind it. The map the owner was
    composing names its group's slots in 224 cells, which is its waving grass, so a grab of a
    field came back with 224 holes. A null records NOTHING about what was there, so those holes
    are permanent and the stamps that carry them have to be grabbed again.

    EVERY STAMP ALREADY ON DISK MUST STILL LOAD, which is why the three-element form is untouched
    and why nothing is rewritten on the way in. The owner holds twelve of them."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_a_stamp_with_an_animated_cell_round_trips_whole(self):
        serve.save_stamp(WAVING, self.folder)
        self.assertEqual(serve.stamps(self.folder), [WAVING])

    def test_an_old_three_element_stamp_still_loads_beside_a_new_one(self):
        """The library holds both shapes at once, because his twelve stamps are his work."""
        serve.save_stamp(STAMP, self.folder)
        serve.save_stamp(WAVING, self.folder)
        self.assertEqual([s["name"] for s in serve.stamps(self.folder)],
                         ["boulder", "grass patch"])
        self.assertEqual(serve.stamps(self.folder)[0], STAMP)

    def test_a_cell_naming_a_group_the_stamp_does_not_carry_is_refused(self):
        """It would place nothing and say nothing, which is the failure this whole change is
        about. It is caught at the one door every stamp goes through."""
        with self.assertRaises(ValueError) as caught:
            serve.save_stamp({**WAVING, "animated": []}, self.folder)
        self.assertIn("names animated group 0", str(caught.exception))
        self.assertEqual(serve.stamps(self.folder), [])

    def test_a_cell_naming_a_tile_past_the_group_is_refused(self):
        bad = {**WAVING, "cells": {"bg3": [{"g": 0, "t": 9, "f": 0}]}}
        with self.assertRaises(ValueError) as caught:
            serve.save_stamp(bad, self.folder)
        self.assertIn("tile 9", str(caught.exception))

    def test_a_cell_that_is_neither_shape_is_refused(self):
        bad = {**WAVING, "cells": {"bg3": ["grass"]}}
        with self.assertRaises(ValueError):
            serve.save_stamp(bad, self.folder)

    def test_the_check_runs_before_a_replace_moves_anything(self):
        serve.save_stamp(WAVING, self.folder)
        with self.assertRaises(ValueError):
            serve.save_stamp({**WAVING, "animated": []}, self.folder, replace=True)
        self.assertEqual(serve.stamps(self.folder), [WAVING])
        self.assertFalse((self.folder / serve.STAMPS_IN / serve.DELETED_IN).exists())

    def test_stripping_the_collision_of_an_animated_stamp_keeps_its_groups(self):
        serve.save_stamp({**WAVING, "collision": [1, 1]}, self.folder)
        stripped = serve.strip_stamp("grass patch", self.folder)
        self.assertIsNone(stripped["collision"])
        self.assertEqual(stripped["animated"], WAVING["animated"])


class DefaultStampNameTests(unittest.TestCase):
    """The name an unnamed grab proposes. It must never be a name that is already taken.

    Numbering from the library COUNT was the defect he met: he held stamp 4 through stamp 27, the
    count said 24, and the next grab proposed a name that was in the library. The name now runs
    one past the highest number the library has HELD, and library\\deleted\\ counts, so a number
    he deleted is never handed to a different stamp."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def keep(self, number):
        serve.save_stamp({**STAMP, "name": f"stamp {number}"}, self.folder)

    def test_an_empty_library_starts_at_one(self):
        self.assertEqual(serve.next_stamp_name(self.folder), "stamp 1")

    def test_it_skips_every_number_the_library_holds(self):
        for number in range(4, 28):
            self.keep(number)
        self.assertEqual(len(serve.stamps(self.folder)), 24)      # the count he had, and the trap
        self.assertEqual(serve.next_stamp_name(self.folder), "stamp 28")

    def test_it_skips_a_number_whose_file_has_been_retired(self):
        """The case that bit him: the stamp is gone from the library and its number is not free."""
        self.keep(30)
        serve.delete_stamp("stamp 30", self.folder)
        self.assertEqual(serve.stamps(self.folder), [])
        self.assertEqual(serve.next_stamp_name(self.folder), "stamp 31")

    def test_a_name_he_typed_himself_is_never_counted(self):
        serve.save_stamp(STAMP, self.folder)                      # "boulder"
        self.assertEqual(serve.next_stamp_name(self.folder), "stamp 1")


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


class WriteRouteTests(unittest.TestCase):
    """The two POST routes, driven directly. The ORDER lives here and not in the helpers.

    _write reads nothing from the handler but self.root, so a namespace is the whole fixture."""

    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.doc = map_file.blank((2, 2), (512, 512))

    def post(self, path, body):
        return serve.Handler._write(SimpleNamespace(root=self.folder), path, body)

    def test_a_taken_name_answers_the_question_and_keeps_the_net(self):
        """The taken branch RETURNS before autosave_retire. If it fell through, a save that never
        happened would take away the autosave standing under the work."""
        serve.save_map(self.doc, "field", self.folder)
        serve.autosave_write({"name": "field", "session": "one", "doc": self.doc}, self.folder)
        answer = self.post("/api/save", {"name": "field", "doc": self.doc, "retire": "field"})
        self.assertEqual(answer, {"taken": "field"})            # no "error": the page must ASK
        self.assertTrue((self.folder / "autosave" / "field.json").exists())
        self.assertFalse((self.folder / "autosave" / "older").exists())

    def test_a_replace_through_the_route_retires_the_net_and_names_the_old_file(self):
        serve.save_map(self.doc, "field", self.folder)
        serve.autosave_write({"name": "field", "session": "one", "doc": self.doc}, self.folder)
        answer = self.post("/api/save", {"name": "field", "doc": self.doc, "retire": "field",
                                         "replace": True})
        self.assertEqual(answer["saved"], "field")
        self.assertEqual(answer["replaced"], "field.json")
        self.assertTrue(answer["retired"])
        self.assertEqual(answer["maps"], ["field"])             # maps\older\ is never offered

    def test_the_replace_flag_never_reaches_the_stamp_file(self):
        """The body IS the stamp, so the route lifts the flag out before anything is written."""
        self.post("/api/stamp", {**STAMP, "replace": False})
        kept = json.loads((self.folder / "library" / "boulder.json").read_text(encoding="utf-8"))
        self.assertNotIn("replace", kept)
        self.assertEqual(kept, STAMP)

    def test_a_taken_stamp_name_answers_the_question_rather_than_an_error(self):
        self.post("/api/stamp", {**STAMP})
        self.assertEqual(self.post("/api/stamp", {**STAMP, "replace": False}),
                         {"taken": "boulder"})
        answer = self.post("/api/stamp", {**STAMP, "replace": True})
        self.assertEqual(answer, {"kept": "boulder", "replaced": "boulder.json"})


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
