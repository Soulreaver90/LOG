r"""
test_map_editor_layers.py - Which layer a stamp lands on, and the box that landing records.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_editor_layers.py -v

WHY NODE. map-editor\editor\state.js owns the layer order, the per layer scroll offset and now
the landing rule. A Python copy of that arithmetic would be a second implementation, and a green
suite over the copy would say nothing about the editor. So these tests run the real module, and
the records they produce go back through map_file.validate, which is the gate a save must pass.

THE DEFECT THESE TESTS PIN. A stamp used to land on the layer it was GRABBED from, so grass taken
from BG3 could not be painted onto the BG1 a cliff is drawn on. A stamp's layer names are
provenance, exactly as its [chunk, tile] pairs are art and not VRAM slots, so a single layer stamp
now lands on the layer being painted on and a multi layer stamp slides along the draw order.

THE DEFECT THAT CHANGE CAN CAUSE. Commit 615ff3b clamps a stamp's record to its own layer's grid,
because a layer at a 24 cell offset runs out of grid 24 cells before the canvas does. That clamp
has to be recomputed for the layer the stamp LANDS on. On map 7,15 BG1 sits at 8 cells and BG3 at
24, so one drop records two different boxes, and keeping the source layer's numbers writes a span
past the block grid that map_file._check_stamps refuses. ClampTests proves both directions.

Read-only on the ROM. Nothing here writes under data\, and nothing touches the owner's own
map-editor\maps\, library\ or autosave\.
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

import log2_build                                                          # noqa: E402
import map_file                                                            # noqa: E402

EDITOR = log_paths.MAP_EDITOR_EDITOR
STATE = EDITOR / "state.js"
CELLS = EDITOR / "cells.js"
NODE = shutil.which("node")

# Map 7,15 is the map the owner is composing on, and the one that makes this test able to fail:
# its four layers carry three different priorities AND four different scroll offsets.
PLATEAU = map_file.read_map(log2_build.BASE.read_bytes(), 7, 15)
ACROSS = PLATEAU["blocks"][0] * map_file.BLOCK_TILES
DOWN = PLATEAU["blocks"][1] * map_file.BLOCK_TILES

# The driver: it imports the editor's own module, runs one job, and prints the answer as JSON.
DRIVER = """
import { drawOrder, layerShiftCells, stampLanding, stampRecord } from "STATE_URL";
import { readFileSync, writeFileSync } from "node:fs";

const job = JSON.parse(readFileSync(process.argv[2], "utf-8"));
const out = { error: null, order: [], shifts: {}, landing: null, records: {} };
try {
  out.order = drawOrder(job.doc);
  for (const name of Object.keys(job.doc.layers)) out.shifts[name] = layerShiftCells(job.doc, name);
  out.landing = stampLanding(job.doc, job.selected, job.names);
  for (const name of job.probe || []) {
    out.records[name] = stampRecord(job.doc, name, job.drop[0], job.drop[1], job.drop[2],
                                    job.drop[3]);
  }
} catch (problem) {
  out.error = problem.message;
}
writeFileSync(process.argv[3], JSON.stringify(out));
"""


def run_state(doc: dict, selected: str, names: list, drop: list = None,
              probe: list = None) -> dict:
    """One landing through the editor's real module."""
    with tempfile.TemporaryDirectory() as folder:
        here = Path(folder)
        driver = here / "driver.mjs"
        driver.write_text(DRIVER.replace("STATE_URL", STATE.as_uri()), encoding="utf-8")
        job = here / "job.json"
        answer = here / "out.json"
        job.write_text(json.dumps({"doc": doc, "selected": selected, "names": names,
                                   "drop": drop or [0, 0, 1, 1], "probe": probe or []}),
                       encoding="utf-8")
        done = subprocess.run([NODE, str(driver), str(job), str(answer)],
                              capture_output=True, text=True, check=False)
        if done.returncode:
            raise AssertionError(f"node exited {done.returncode}:\n{done.stdout}\n{done.stderr}")
        return json.loads(answer.read_text(encoding="utf-8"))


def plateau_shaped() -> dict:
    """A sound empty document carrying map 7,15's OWN geometry: its block grid, its world, its
    per layer priorities and its per layer scroll offsets, all read from the ROM above. The cells
    are left empty because no rule under test reads one, and 81,920 of them through a JSON file
    would buy nothing."""
    doc = map_file.blank(tuple(PLATEAU["blocks"]), tuple(PLATEAU["world"]))
    for name, layer in PLATEAU["layers"].items():
        doc["layers"][name]["priority"] = layer["priority"]
        doc["layers"][name]["offset"] = list(layer["offset"])
        doc["layers"][name]["scroll"] = list(layer["scroll"])
    return doc


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class TheMapItselfTests(unittest.TestCase):
    """The facts the rest of the file rests on, read from the ROM rather than assumed."""

    def test_the_four_layers_carry_three_priorities_and_four_offsets(self):
        got = {name: (layer["priority"], layer["offset"][0])
               for name, layer in PLATEAU["layers"].items()}
        self.assertEqual(got, {"bg0": (3, 0), "bg1": (1, 65536),
                               "bg2": (3, 131072), "bg3": (3, 196608)})

    def test_bg1_and_bg3_sit_at_different_cell_offsets(self):
        """The whole reason the clamp has to follow the destination layer."""
        answer = run_state(plateau_shaped(), "bg1", ["bg3"])
        self.assertEqual(answer["shifts"]["bg1"], [8, 8])
        self.assertEqual(answer["shifts"]["bg3"], [24, 24])

    def test_the_draw_order_is_not_the_bg_numbers(self):
        """BG1 is priority 1, so it draws in FRONT of the other three. A slide by BG number would
        reverse a stack here; the landing rule slides by draw order for exactly this reason."""
        answer = run_state(plateau_shaped(), "bg1", ["bg3"])
        self.assertEqual(answer["order"], ["bg3", "bg2", "bg0", "bg1"])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class OneLayerTests(unittest.TestCase):
    """His words: "I grabed something from BG3, but it wont let me use that to paint in BG1"."""

    def test_grass_from_bg3_lands_on_whichever_layer_he_is_painting_on(self):
        for selected in ("bg0", "bg1", "bg2", "bg3"):
            with self.subTest(selected=selected):
                answer = run_state(plateau_shaped(), selected, ["bg3"])
                self.assertIsNone(answer["landing"]["problem"])
                self.assertEqual(answer["landing"]["map"], {"bg3": selected})

    def test_a_layer_the_destination_map_has_not_got_is_still_no_obstacle(self):
        """One layer is unambiguous, so its own name never has to mean anything here."""
        doc = plateau_shaped()
        del doc["layers"]["bg0"]
        answer = run_state(doc, "bg1", ["bg0"])
        self.assertIsNone(answer["landing"]["problem"])
        self.assertEqual(answer["landing"]["map"], {"bg0": "bg1"})

    def test_a_selected_layer_this_map_has_not_got_is_refused(self):
        doc = plateau_shaped()
        del doc["layers"]["bg0"]
        answer = run_state(doc, "bg0", ["bg3"])
        self.assertIsNone(answer["landing"]["map"])
        self.assertIn("has not got a layer BG0", answer["landing"]["problem"])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class StackTests(unittest.TestCase):
    """A multi layer stamp keeps its stack. Six of the fifteen stamps in the owner's library are
    drawn across two or three layers, so this is not a corner: BG1+BG2, BG0+BG1, BG0+BG2+BG3,
    BG0+BG1+BG3, BG1+BG3 and BG1+BG2+BG3."""

    def test_dropping_a_stack_back_on_its_own_front_layer_changes_nothing(self):
        """The common case: restamping the same map. The front layer is the stamp's own layer
        that this map draws nearest the front, so the slide is the identity and every layer of
        the stack goes back where it came from. A compacting rule would move them."""
        for names in (["bg1", "bg2"], ["bg0", "bg2", "bg3"], ["bg1", "bg3"],
                      ["bg1", "bg2", "bg3"], ["bg0", "bg1"]):
            with self.subTest(names=names):
                order = run_state(plateau_shaped(), "bg1", names)["order"]
                front = max(names, key=order.index)
                answer = run_state(plateau_shaped(), front, names)
                self.assertIsNone(answer["landing"]["problem"])
                self.assertEqual(answer["landing"]["map"], {n: n for n in names})

    def test_a_stack_slides_whole_and_keeps_its_order(self):
        """BG1+BG2 with BG0 selected: BG1 is the front layer, so it takes BG0, and BG2 keeps its
        two places behind it, which on this map's draw order is BG3."""
        answer = run_state(plateau_shaped(), "bg0", ["bg1", "bg2"])
        self.assertEqual(answer["landing"]["map"], {"bg1": "bg0", "bg2": "bg3"})

    def test_a_slide_never_brings_a_stack_back_reversed(self):
        """A slide by BG NUMBER would put a BG2+BG3 stamp on BG1+BG2 with BG1 selected, and BG1
        draws in front of BG2 here, so the back half would come out in front."""
        order = run_state(plateau_shaped(), "bg1", ["bg2", "bg3"])["order"]
        landed = run_state(plateau_shaped(), "bg1", ["bg2", "bg3"])["landing"]["map"]
        self.assertLess(order.index(landed["bg3"]), order.index(landed["bg2"]))

    def test_a_stack_with_no_room_behind_it_places_nothing_and_names_the_layers(self):
        answer = run_state(plateau_shaped(), "bg3", ["bg1", "bg2"])
        self.assertIsNone(answer["landing"]["map"])
        problem = answer["landing"]["problem"]
        self.assertIn("BG1, BG2", problem)
        self.assertIn("no room for that stack at or behind BG3", problem)
        self.assertIn("Nothing was placed", problem)

    def test_the_refusal_names_a_selection_that_would_hold_it(self):
        answer = run_state(plateau_shaped(), "bg3", ["bg1", "bg2"])
        self.assertIn("Select BG0 or a layer in front of it", answer["landing"]["problem"])
        held = run_state(plateau_shaped(), "bg0", ["bg1", "bg2"])
        self.assertIsNone(held["landing"]["problem"])

    def test_a_stack_layer_the_destination_map_has_not_got_places_nothing(self):
        doc = plateau_shaped()
        del doc["layers"]["bg2"]
        answer = run_state(doc, "bg1", ["bg1", "bg2"])
        self.assertIsNone(answer["landing"]["map"])
        self.assertIn("has not got BG2", answer["landing"]["problem"])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class ClampTests(unittest.TestCase):
    """615ff3b, recomputed for the layer the stamp LANDS on. The drop is a 12 x 10 stamp, which is
    the owner's own "tall rock", at world cell 130, 102: past the right edge of BG3's grid and
    past the bottom edge of it, and inside BG1's."""

    DROP = [130, 102, 12, 10]

    def test_the_destination_layer_decides_the_record_not_the_source(self):
        answer = run_state(plateau_shaped(), "bg1", ["bg3"], self.DROP, ["bg1", "bg3"])
        self.assertEqual(answer["landing"]["map"], {"bg3": "bg1"})
        # BG1 is at 8 cells: 130 + 8 = 138, and 138 + 12 = 150, inside the 160 cell grid.
        self.assertEqual(answer["records"]["bg1"], {"x": 138, "y": 110, "w": 12, "h": 10})
        # What the SOURCE layer would have recorded, which is a different box entirely.
        self.assertEqual(answer["records"]["bg3"], {"x": 154, "y": 126, "w": 6, "h": 2})

    def test_the_record_the_landing_writes_passes_validate(self):
        answer = run_state(plateau_shaped(), "bg1", ["bg3"], self.DROP, ["bg1"])
        doc = plateau_shaped()
        doc["stamps"] = [{"name": "tall rock", "layer": "bg1", **answer["records"]["bg1"]}]
        self.assertEqual(map_file.validate(doc), [])

    def test_a_landing_near_its_own_edge_is_clamped_or_the_save_fails(self):
        """The other direction, which is the one that breaks. A BG1 stamp dropped on BG3 at the
        same cell: BG3 sits 16 cells further along its own grid, so it reaches the right and
        bottom edges of that grid first and the recorded span has to shrink to 6 x 2."""
        answer = run_state(plateau_shaped(), "bg3", ["bg1"], self.DROP, ["bg3"])
        self.assertEqual(answer["landing"]["map"], {"bg1": "bg3"})
        self.assertEqual(answer["records"]["bg3"], {"x": 154, "y": 126, "w": 6, "h": 2})

        good = plateau_shaped()
        good["stamps"] = [{"name": "tall rock", "layer": "bg3", **answer["records"]["bg3"]}]
        self.assertEqual(map_file.validate(good), [])

        # The same drop with the clamp NOT recomputed for the layer it landed on: that layer's
        # own grid cell carrying the stamp's full 12 x 10. This is the save that 615ff3b fixed,
        # and it must still fail, or the clamp has quietly stopped doing anything.
        bad = plateau_shaped()
        bad["stamps"] = [{"name": "tall rock", "layer": "bg3", "x": 154, "y": 126,
                          "w": self.DROP[2], "h": self.DROP[3]}]
        problems = map_file.validate(bad)
        self.assertEqual(len(problems), 1)
        self.assertIn(f"runs past the {ACROSS} x {DOWN} cell grid", problems[0])

    def test_a_layer_with_no_room_at_the_drop_records_nothing(self):
        """BG3 is at 24 cells, so a drop at world cell 136 is already past its 160 cell grid."""
        answer = run_state(plateau_shaped(), "bg1", ["bg1"], [136, 10, 4, 4], ["bg1", "bg3"])
        self.assertIsNone(answer["records"]["bg3"])
        self.assertEqual(answer["records"]["bg1"], {"x": 144, "y": 18, "w": 4, "h": 4})

    def test_every_landing_of_a_stack_is_clamped_to_its_own_layer(self):
        """BG1+BG3 is the owner's "stamp 42". The two layers sit 16 cells apart, so one drop
        records a full 12 x 10 on BG1 and a clamped 6 x 2 on BG3."""
        answer = run_state(plateau_shaped(), "bg1", ["bg1", "bg3"], self.DROP, ["bg1", "bg3"])
        self.assertEqual(answer["landing"]["map"], {"bg1": "bg1", "bg3": "bg3"})
        doc = plateau_shaped()
        doc["stamps"] = [{"name": "tall rock", "layer": name, **answer["records"][name]}
                         for name in ("bg1", "bg3")]
        self.assertEqual([(s["w"], s["h"]) for s in doc["stamps"]], [(12, 10), (6, 2)])
        self.assertEqual(map_file.validate(doc), [])


@unittest.skipUnless(NODE, "node is not on PATH, so the editor's own module cannot be run")
class AnimatedThroughTheMoveTests(unittest.TestCase):
    """A group's slots are per DOCUMENT and not per layer, so waving grass survives the move.
    Measured on vanilla map 7,15 rather than assumed: its one group owns slots 894 and 895, and
    its cells name those slots from TWO different layers, 24 on BG1 and 33 on BG2."""

    def test_the_vanilla_map_names_one_groups_slots_from_two_layers(self):
        group = PLATEAU["animated"][0]
        span = range(group["first"], group["first"] + map_file.group_tiles(group))
        counts = {name: sum(1 for value in layer["cells"] if (value & 0x3FF) in span)
                  for name, layer in PLATEAU["layers"].items()}
        self.assertEqual(counts, {"bg0": 0, "bg1": 24, "bg2": 33, "bg3": 0})

    def test_an_animated_cell_keeps_its_group_slot_on_another_layer(self):
        """The same patch, planned under its source layer name and under its destination name.
        planPlacement takes no layer at all, so the slots must come out identical."""
        doc = map_file.blank((2, 2), (512, 512))
        doc["tiles"] = [[0, 0], [1, 2]]
        group = {"first": 894,
                 "frames": [{"duration": 20, "pixels": [7] * (2 * map_file.TILE_BYTES)},
                            {"duration": 20, "pixels": [8] * (2 * map_file.TILE_BYTES)}]}
        cells = [{"g": 0, "t": 0, "f": 0}, {"g": 0, "t": 1, "f": 0x400}, [1, 2, 0]]
        source = _plan(doc, {"w": 3, "h": 1, "layers": {"bg3": cells}, "animated": [group]})
        landed = _plan(doc, {"w": 3, "h": 1, "layers": {"bg1": cells}, "animated": [group]})
        self.assertIsNone(source["error"])
        self.assertIsNone(landed["error"])
        self.assertEqual(source["slots"]["bg3"], landed["slots"]["bg1"])
        self.assertEqual(landed["addGroups"], source["addGroups"])
        self.assertEqual(map_file.validate(landed["doc"]), [])


# The cells.js driver, reused from test_map_editor_cells.py's shape rather than copied in full:
# only the one job this file needs.
PLAN_DRIVER = """
import { planPlacement, applyPlan } from "CELLS_URL";
import { readFileSync, writeFileSync } from "node:fs";

const job = JSON.parse(readFileSync(process.argv[2], "utf-8"));
const out = { error: null, slots: {}, addGroups: [] };
try {
  const plan = planPlacement(job.doc, job.patch, job.limits);
  out.addGroups = plan.addGroups.map((entry) => entry.first);
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


def _plan(doc: dict, patch: dict) -> dict:
    limits = {"budget": map_file.TILE_BUDGET, "groupMax": map_file.GROUP_MAX,
              "groupMaxTiles": map_file.GROUP_MAX_TILES}
    with tempfile.TemporaryDirectory() as folder:
        here = Path(folder)
        driver = here / "plan.mjs"
        driver.write_text(PLAN_DRIVER.replace("CELLS_URL", CELLS.as_uri()), encoding="utf-8")
        job = here / "job.json"
        answer = here / "out.json"
        job.write_text(json.dumps({"doc": json.loads(json.dumps(doc)), "patch": patch,
                                   "limits": limits}), encoding="utf-8")
        done = subprocess.run([NODE, str(driver), str(job), str(answer)],
                              capture_output=True, text=True, check=False)
        if done.returncode:
            raise AssertionError(f"node exited {done.returncode}:\n{done.stdout}\n{done.stderr}")
        return json.loads(answer.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
