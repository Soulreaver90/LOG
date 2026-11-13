r"""
test_map_editor_cells.py - What a stamp cell means, run through the editor's own JavaScript.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_cells.py -v

WHY NODE. map-editor\editor\cells.js is the step that decides which VRAM slot every cell of a
placement lands in, and whether the destination map must gain a tile or a whole animated group.
A Python copy of that rule would be a second implementation, and a green suite over the copy
would say nothing about the editor. So these tests run the real module, and the documents they
produce go back through map_file.validate, which is the gate a map must pass to be saved.

THE DEFECT THESE TESTS PIN. A grab used to store null wherever a cell named an animated group,
because a group slot has no [chunk, tile] pair. Vanilla map 7,15 names its group's slots in 57
cells and the map the owner is composing from it names them in 224, which is its waving grass, so
a grab of a field came back with 224 holes in it. A cell of a group
is now {g, t, f} and the stamp carries the group's PIXELS, so it can be placed into a map that
has never held that group.

EVERY STAMP ALREADY ON DISK MUST STILL LOAD. The three-element form is untouched, and
OldStampFormatTests is the test that says so.

Read-only on the ROM. Nothing here writes under data\, and nothing touches the owner's own
map-editor\maps\ or map-editor\library\.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import log_paths  # noqa: E402

sys.path.insert(0, str(log_paths.MAP_EDITOR))

import map_file                                                            # noqa: E402

EDITOR = log_paths.MAP_EDITOR_EDITOR
CELLS = EDITOR / "cells.js"
NODE = shutil.which("node")
LIMITS = {"budget": map_file.TILE_BUDGET, "groupMax": map_file.GROUP_MAX,
          "groupMaxTiles": map_file.GROUP_MAX_TILES}

# The driver: it imports the editor's own module, runs one job, and prints the answer as JSON.
# `plan` is the whole deciding step, and `apply` is the mutation the editor makes with it, so a
# job that asks for both runs exactly what a placement runs.
DRIVER = """
import { planPlacement, applyPlan } from "CELLS_URL";
import { readFileSync, writeFileSync } from "node:fs";

const job = JSON.parse(readFileSync(process.argv[2], "utf-8"));
const out = { error: null, slots: {}, addTiles: [], addGroups: [], refusals: [] };
try {
  const plan = planPlacement(job.doc, job.patch, job.limits);
  out.addTiles = plan.addTiles;
  out.addGroups = plan.addGroups.map((entry) => entry.first);
  out.refusals = plan.refusals;
  for (const [layer, cells] of Object.entries(job.patch.layers)) {
    out.slots[layer] = cells.map((cell) => plan.slotOf(cell));
  }
  applyPlan(job.doc, plan);
} catch (problem) {
  out.error = problem.message;
}
out.doc = job.doc;
writeFileSync(process.argv[3], JSON.stringify(out));
"""


def run_cells(doc: dict, patch: dict, limits: dict = None) -> dict:
    """One placement through the editor's real module. Returns the plan and the document after."""
    with tempfile.TemporaryDirectory() as folder:
        here = Path(folder)
        driver = here / "driver.mjs"
        driver.write_text(DRIVER.replace("CELLS_URL", CELLS.as_uri()), encoding="utf-8")
        job = here / "job.json"
        answer = here / "out.json"
        job.write_text(json.dumps({"doc": doc, "patch": patch, "limits": limits or LIMITS}),
                       encoding="utf-8")
        done = subprocess.run([NODE, str(driver), str(job), str(answer)],
                              capture_output=True, text=True, check=False)
        if done.returncode:
            raise AssertionError(f"node exited {done.returncode}:\n{done.stdout}\n{done.stderr}")
        return json.loads(answer.read_text(encoding="utf-8"))


def a_group(tiles: int = 4, first: int = 892, fill: int = 7) -> dict:
    """An animated group of `tiles` tiles and two frames, in the document's own shape."""
    return {"first": first,
            "frames": [{"duration": 20, "pixels": [fill] * (tiles * map_file.TILE_BYTES)},
                       {"duration": 20, "pixels": [fill + 1] * (tiles * map_file.TILE_BYTES)}]}


def a_map(groups: list = None) -> dict:
    """A small sound document to place into. 2 x 2 blocks is 512 px, which is a legal world."""
    doc = map_file.blank((2, 2), (512, 512))
    doc["tiles"] = [[0, 0], [1, 2], [1, 3]]
    doc["animated"] = groups or []
    return doc


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class OldStampFormatTests(unittest.TestCase):
    """The twelve stamps in the owner's library were grabbed before animated cells existed.
    Every one of them is a grid of [chunk, tile, flips] and null, and every one must still
    place. A one-off read of all twelve through this same module confirmed it on 2026-11-08."""

    def test_a_three_element_cell_still_resolves_to_a_slot(self):
        doc = a_map()
        patch = {"w": 2, "h": 1, "layers": {"bg3": [[1, 2, 0], [1, 3, 0x400]]}}
        answer = run_cells(doc, patch)
        self.assertIsNone(answer["error"])
        self.assertEqual(answer["slots"]["bg3"], [1, 2])
        self.assertEqual(answer["addTiles"], [])

    def test_a_stamp_with_no_animated_field_at_all_places(self):
        """The old files carry no "animated" key. Reading one must not reach for it."""
        doc = a_map()
        patch = {"w": 2, "h": 1, "layers": {"bg3": [None, [9, 9, 0]]}}
        answer = run_cells(doc, patch)
        self.assertIsNone(answer["error"])
        self.assertEqual(answer["slots"]["bg3"], [None, 3])
        self.assertEqual(answer["addTiles"], [[9, 9]])

    def test_a_null_cell_still_means_leave_what_is_under_me(self):
        answer = run_cells(a_map(), {"w": 1, "h": 1, "layers": {"bg3": [None]}})
        self.assertEqual(answer["slots"]["bg3"], [None])

    def test_the_document_an_old_stamp_leaves_behind_is_sound(self):
        doc = a_map()
        patch = {"w": 1, "h": 1, "layers": {"bg3": [[9, 9, 0]]}}
        self.assertEqual(map_file.validate(run_cells(doc, patch)["doc"]), [])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class AnimatedCellTests(unittest.TestCase):
    """The defect itself: a grab must capture a waving tile, and placing it must keep it waving."""

    def test_a_map_that_carries_the_group_writes_the_group_s_own_slots(self):
        """His case. The map he is composing already holds the group the grab came from, so
        nothing is added and the cell names the slot that map already animates."""
        doc = a_map([a_group()])
        patch = {"w": 2, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}, {"g": 0, "t": 3, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertIsNone(answer["error"])
        self.assertEqual(answer["slots"]["bg3"], [892, 895])
        self.assertEqual(answer["addGroups"], [])
        self.assertEqual(len(answer["doc"]["animated"]), 1)

    def test_a_group_is_matched_by_its_pixels_and_never_by_its_first_slot(self):
        """`first` is a slot, and a slot means nothing outside its own map, which is the same
        reason a stamp stores a chunk pair and not a slot."""
        doc = a_map([a_group(first=800)])
        patch = {"w": 1, "h": 1, "animated": [a_group(first=892)],
                 "layers": {"bg3": [{"g": 0, "t": 2, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["addGroups"], [])
        self.assertEqual(answer["slots"]["bg3"], [802])

    def test_a_map_without_the_group_gains_it_at_the_top_of_the_budget(self):
        """The top of the budget, which is where the game itself puts a group: map 7,15 streams
        633 static tiles and loads its 2 group tiles at 894 and 895, the last two slots. A group
        parked just past the static stream would cap the stream where it sits."""
        doc = a_map()
        patch = {"w": 1, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 1, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["addGroups"], [892])
        self.assertEqual(answer["slots"]["bg3"], [893])
        self.assertEqual(len(answer["doc"]["animated"]), 1)

    def test_the_document_a_new_group_lands_in_is_sound(self):
        """The one check that matters: what the editor wrote must pass the gate that stands
        between a document and the ROM."""
        doc = a_map()
        patch = {"w": 1, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        after = run_cells(doc, patch)["doc"]
        self.assertEqual(map_file.validate(after), [])
        self.assertEqual(map_file.group_tiles(after["animated"][0]), 4)

    def test_the_group_arrives_with_its_pixels_and_its_durations(self):
        doc = a_map()
        patch = {"w": 1, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        landed = run_cells(doc, patch)["doc"]["animated"][0]
        self.assertEqual([f["duration"] for f in landed["frames"]], [20, 20])
        self.assertEqual(landed["frames"][0]["pixels"], a_group()["frames"][0]["pixels"])

    def test_a_second_group_goes_under_the_first_and_never_over_it(self):
        doc = a_map([a_group()])
        patch = {"w": 1, "h": 1, "animated": [a_group(tiles=2, fill=40)],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["addGroups"], [890])
        self.assertEqual(map_file.validate(answer["doc"]), [])

    def test_flips_ride_on_an_animated_cell_too(self):
        doc = a_map([a_group()])
        patch = {"w": 1, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 1, "f": 0x400}]}}
        self.assertEqual(run_cells(doc, patch)["slots"]["bg3"], [893])

    def test_a_mixed_stamp_places_both_kinds_in_one_pass(self):
        doc = a_map()
        patch = {"w": 3, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [[1, 2, 0], {"g": 0, "t": 0, "f": 0}, [7, 7, 0]]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["slots"]["bg3"], [1, 892, 3])
        self.assertEqual(answer["addTiles"], [[7, 7]])
        self.assertEqual(map_file.validate(answer["doc"]), [])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class TheLimitsTests(unittest.TestCase):
    """A group that will not fit places NOTHING in its own cells and says which limit stopped it.
    It never substitutes a static look-alike: the owner asked for the animation by name."""

    def test_a_seventeenth_group_is_refused_and_the_limit_is_named(self):
        doc = a_map([a_group(tiles=1, first=800 + n, fill=n) for n in range(map_file.GROUP_MAX)])
        patch = {"w": 1, "h": 1, "animated": [a_group(tiles=1, fill=200)],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["slots"]["bg3"], [None])
        self.assertEqual(answer["addGroups"], [])
        self.assertIn("16 animated groups", " ".join(answer["refusals"]))

    def test_a_group_past_the_load_buffer_is_refused(self):
        patch = {"w": 1, "h": 1, "animated": [a_group(tiles=map_file.GROUP_MAX_TILES + 1)],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(a_map(), patch)
        self.assertEqual(answer["slots"]["bg3"], [None])
        self.assertIn("load buffer holds 64", " ".join(answer["refusals"]))

    def test_a_group_with_no_free_run_of_slots_is_refused(self):
        """A map whose static stream reaches the budget has no room above it for a group."""
        doc = a_map()
        doc["tiles"] = [[0, n % 256] for n in range(map_file.TILE_BUDGET)]
        patch = {"w": 1, "h": 1, "animated": [a_group()],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["slots"]["bg3"], [None])
        self.assertIn("no free run of 4 slots", " ".join(answer["refusals"]))

    def test_the_static_cells_of_a_refused_stamp_are_still_placed(self):
        """Only the animated cells are held back. A stamp is mostly ground, and dropping the
        whole placement over one group would cost him the ground too."""
        doc = a_map([a_group(tiles=1, first=800 + n, fill=n) for n in range(map_file.GROUP_MAX)])
        patch = {"w": 2, "h": 1, "animated": [a_group(tiles=1, fill=200)],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}, [1, 2, 0]]}}
        answer = run_cells(doc, patch)
        self.assertEqual(answer["slots"]["bg3"], [None, 1])

    def test_a_cell_naming_a_group_the_stamp_does_not_carry_places_nothing(self):
        patch = {"w": 1, "h": 1, "animated": [], "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(a_map(), patch)
        self.assertEqual(answer["slots"]["bg3"], [None])
        self.assertIn("does not carry", " ".join(answer["refusals"]))

    def test_a_stream_that_would_grow_into_a_group_raises_with_the_slot(self):
        """The stream grows upward and a group owns real VRAM, so one slot cannot hold both
        (bible B1078). This is the one failure that stops the whole placement."""
        doc = a_map([a_group(tiles=4, first=4)])
        doc["tiles"] = [[0, 0], [1, 2], [1, 3], [1, 4]]
        patch = {"w": 1, "h": 1, "layers": {"bg3": [[9, 9, 0]]}}
        answer = run_cells(doc, patch)
        self.assertIn("stops at slot 4", answer["error"] or "")

    def test_a_stream_past_the_budget_raises_with_the_budget(self):
        doc = a_map()
        doc["tiles"] = [[0, n % 256] for n in range(map_file.TILE_BUDGET)]
        patch = {"w": 1, "h": 1, "layers": {"bg3": [[200, 200, 0]]}}
        answer = run_cells(doc, patch)
        self.assertIn("896 tiles", answer["error"] or "")


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class RealMapTests(unittest.TestCase):
    """The plateau's own group, read out of the ROM, placed into a map that has never held it."""

    @classmethod
    def setUpClass(cls):
        cls.rom = map_file.BASE_ROM.read_bytes()
        cls.plateau = map_file.read_map(cls.rom, 7, 15)

    def test_the_plateau_carries_a_group_whose_slots_its_cells_name(self):
        """Vanilla 7,15 streams 633 static tiles, loads 2 more at 894 and names them in 57
        cells, on BG1 and BG2 and not on BG3. Every layer is counted here, because which layer
        holds the waving art is the map's business and not this rule's."""
        self.assertEqual(len(self.plateau["animated"]), 1)
        group = self.plateau["animated"][0]
        span = set(range(group["first"], group["first"] + map_file.group_tiles(group)))
        named = sum(1 for layer in self.plateau["layers"].values()
                    for cell in layer["cells"] if (cell & map_file.TILE_INDEX) in span)
        self.assertEqual(named, 57)
        self.assertGreater(group["first"], len(self.plateau["tiles"]))

    def test_its_grass_places_into_a_blank_map_and_the_result_is_sound(self):
        group = self.plateau["animated"][0]
        tiles = map_file.group_tiles(group)
        patch = {"w": tiles, "h": 1, "animated": [group],
                 "layers": {"bg3": [{"g": 0, "t": n, "f": 0} for n in range(tiles)]}}
        answer = run_cells(a_map(), patch)
        self.assertIsNone(answer["error"])
        self.assertEqual(answer["addGroups"], [map_file.TILE_BUDGET - tiles])
        self.assertEqual(answer["slots"]["bg3"],
                         [map_file.TILE_BUDGET - tiles + n for n in range(tiles)])
        self.assertEqual(map_file.validate(answer["doc"]), [])

    def test_placing_it_back_into_the_plateau_adds_nothing(self):
        group = self.plateau["animated"][0]
        patch = {"w": 1, "h": 1, "animated": [group],
                 "layers": {"bg3": [{"g": 0, "t": 0, "f": 0}]}}
        answer = run_cells(self.plateau, patch)
        self.assertEqual(answer["addGroups"], [])
        self.assertEqual(answer["slots"]["bg3"], [group["first"]])


if __name__ == "__main__":
    unittest.main()
