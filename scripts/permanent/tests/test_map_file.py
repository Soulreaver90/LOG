r"""
test_map_file.py - Tests for the map editor's document format, map-editor\map_file.py.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_map_file.py -v
Nothing here writes a ROM. Documents are written to a temporary folder, never under data\.

Two rules get a patched ROM COPY rather than a base ROM read, because the base ROM cannot show
that a reader FOLLOWS a value a build can move: the camera pair at layout +0x08, and the layer
priority at layout +0x04. A test that reads the base value proves only that the constant is the
constant.

Map 7,15 is the main witness on purpose. Its world is 952 x 768 inside a 1280 x 1024 block grid,
so a reader that computes the camera pair from the grid passes a formula test and still breaks the
map. Its BG1 is priority 1, the canopy over the player, so a defaulted priority also shows here.
Its one animated group sits at slots 894 and 895, past its 633 static tiles, so a document that
drops the group leaves a cell naming a slot the map never loads.
"""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

from scene import map_view
from scene import scene_probe

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import map_file                                                            # noqa: E402
import tile_stream                                                         # noqa: E402

ROM = map_file.BASE_ROM.read_bytes()

# Map 7,15, measured from the base ROM and re-measured here by the tests that use them.
W15_PAIR = (713, 609)                   # the +0x08 and +0x0A words the ROM stores
W15_WORLD = (952, 768)                  # that pair plus 239 and 159
W15_GRID = (5, 4)                       # the widest BG block grid: 1280 x 1024 px, NOT the world
W15_STATIC = 633                        # static tiles in the +0x48 stream
W15_PRIORITIES = {"bg0": 3, "bg1": 1, "bg2": 3, "bg3": 3}   # layout bytes +0x04 to +0x07

SAMPLE_MAPS = ((6, 1), (7, 15), (4, 50), (14, 3), (8, 36), (9, 1), (14, 1), (6, 4), (6, 70), (4, 6))


def layout_offset(zone: int, area: int, var: int = 1) -> int:
    _index, entry = scene_probe.map_entry(ROM, zone, area)
    return map_view.layout_of(ROM, entry, var) - map_view.ROM_BASE


def rom_with(offset: int, fmt: str, value: int) -> bytes:
    """A ROM COPY with one field overwritten. In memory only: no ROM file is ever written."""
    copy = bytearray(ROM)
    struct.pack_into(fmt, copy, offset, value)
    return bytes(copy)


def small_doc(**over) -> dict:
    """A tiny valid document: one block, one layer, one loaded tile. Cheap enough to mutate freely."""
    doc = map_file.blank(blocks=(1, 1), world=(256, 256))
    doc.update(over)
    return doc


class CameraPairTests(unittest.TestCase):
    """The pair is computed from the world, and the world is not the block grid."""

    def test_camera_pair_is_width_minus_239_and_height_minus_159(self):
        self.assertEqual(map_file.camera_pair(1024, 1024), (785, 865))

    def test_camera_pair_of_map_7_15_matches_the_pair_stored_in_the_rom(self):
        stored = struct.unpack_from("<HH", ROM, layout_offset(7, 15) + 0x08)
        doc = map_file.read_map(ROM, 7, 15)
        self.assertEqual(stored, W15_PAIR)
        self.assertEqual(map_file.camera_pair(*doc["world"]), stored)

    def test_the_block_grid_of_map_7_15_would_give_a_different_pair(self):
        """The plateau fault, pinned. A reader that takes the grid as the width passes the formula
        test above and still widens this map's camera by 328 px."""
        doc = map_file.read_map(ROM, 7, 15)
        grid_px = (doc["blocks"][0] * 256, doc["blocks"][1] * 256)
        self.assertEqual(tuple(doc["blocks"]), W15_GRID)
        self.assertEqual(tuple(doc["world"]), W15_WORLD)
        self.assertNotEqual(grid_px, tuple(doc["world"]))
        self.assertNotEqual(map_file.camera_pair(*grid_px), map_file.camera_pair(*doc["world"]))

    def test_read_map_follows_a_camera_pair_that_a_build_moved(self):
        moved = rom_with(layout_offset(7, 15) + 0x08, "<H", W15_PAIR[0] + 64)
        self.assertEqual(map_file.read_map(moved, 7, 15)["world"][0], W15_WORLD[0] + 64)


class ValidateTests(unittest.TestCase):
    """validate reports problems and never raises. Each test breaks exactly one rule."""

    def test_a_blank_document_is_valid(self):
        self.assertEqual(map_file.validate(small_doc()), [])

    def test_validate_rejects_more_than_896_tiles(self):
        doc = small_doc(tiles=[[0, n % 256] for n in range(map_file.TILE_BUDGET + 1)])
        problems = " ".join(map_file.validate(doc))
        self.assertIn(str(map_file.TILE_BUDGET + 1), problems)
        self.assertIn(str(map_file.TILE_BUDGET), problems)

    def test_validate_accepts_exactly_the_tile_budget(self):
        doc = small_doc(tiles=[[0, n % 256] for n in range(map_file.TILE_BUDGET)])
        self.assertEqual(map_file.validate(doc), [])

    def test_validate_rejects_a_layer_whose_cell_count_is_not_the_block_grid(self):
        doc = small_doc()
        doc["layers"]["bg0"]["cells"].pop()
        self.assertTrue(any("bg0" in p for p in map_file.validate(doc)))

    def test_every_layer_carries_a_priority(self):
        doc = small_doc()
        del doc["layers"]["bg0"]["priority"]
        self.assertTrue(any("priority" in p and "bg0" in p for p in map_file.validate(doc)))

    def test_validate_rejects_a_priority_outside_the_two_bits_the_hardware_has(self):
        doc = small_doc()
        doc["layers"]["bg0"]["priority"] = 4
        self.assertTrue(any("priority" in p for p in map_file.validate(doc)))

    def test_validate_rejects_a_block_grid_too_small_for_the_world(self):
        doc = small_doc(world=[512, 256])
        self.assertTrue(any("world" in p and "block" in p for p in map_file.validate(doc)))

    def test_validate_rejects_a_world_smaller_than_one_screen(self):
        doc = small_doc(world=[200, 256])
        self.assertTrue(any("240" in p for p in map_file.validate(doc)))

    def test_validate_rejects_a_missing_world_and_never_falls_back_to_the_grid(self):
        """A document with no world is broken, not a document whose world is its grid. Defaulting
        here is the plateau fault with extra steps."""
        doc = small_doc()
        del doc["world"]
        problems = map_file.validate(doc)
        self.assertTrue(any("world" in p for p in problems))

    def test_validate_rejects_a_cell_naming_a_tile_slot_the_map_never_loads(self):
        doc = small_doc()
        doc["layers"]["bg0"]["cells"][0] = 500
        self.assertTrue(any("500" in p for p in map_file.validate(doc)))

    def test_a_cell_in_an_animated_group_slot_is_loaded(self):
        """The silent hole. A tile past the static stream is real when a group covers it, and the
        same cell with the group removed must be reported."""
        doc = small_doc()
        doc["layers"]["bg0"]["cells"][0] = 300
        doc["animated"] = [{"first": 300, "frames": [{"duration": 20, "pixels": [0] * 64}]}]
        self.assertEqual(map_file.validate(doc), [])
        doc["animated"] = []
        self.assertTrue(any("300" in p for p in map_file.validate(doc)))

    def test_validate_rejects_an_animated_group_that_runs_past_the_tile_budget(self):
        doc = small_doc(animated=[{"first": 895, "frames": [{"duration": 20, "pixels": [0] * 128}]}])
        self.assertTrue(any(str(map_file.TILE_BUDGET) in p for p in map_file.validate(doc)))

    def test_validate_accepts_an_animated_group_ending_exactly_at_the_budget(self):
        """Vanilla reaches slot 896 exactly, so an off-by-one guard here would reject real maps."""
        doc = small_doc(animated=[{"first": 894, "frames": [{"duration": 20, "pixels": [0] * 128}]}])
        self.assertEqual(map_file.validate(doc), [])

    def test_validate_rejects_an_animated_group_over_64_tiles(self):
        pixels = [0] * (65 * map_file.TILE_BYTES)
        doc = small_doc(animated=[{"first": 100, "frames": [{"duration": 20, "pixels": pixels}]}])
        self.assertTrue(any("64" in p for p in map_file.validate(doc)))

    def test_validate_rejects_animated_frames_of_unequal_length(self):
        doc = small_doc(animated=[{"first": 100, "frames": [{"duration": 20, "pixels": [0] * 64},
                                                            {"duration": 20, "pixels": [0] * 128}]}])
        self.assertTrue(any("frame" in p for p in map_file.validate(doc)))

    def test_validate_rejects_more_than_sixteen_animated_groups(self):
        one = {"first": 100, "frames": [{"duration": 20, "pixels": [0] * 64}]}
        doc = small_doc(animated=[dict(one) for _ in range(map_file.GROUP_MAX + 1)])
        self.assertTrue(any(str(map_file.GROUP_MAX) in p for p in map_file.validate(doc)))

    def test_validate_rejects_an_open_collision_cell_the_camera_can_never_reach(self):
        """The plateau in one assertion: walkable ground inside the art grid and past the world."""
        doc = map_file.read_map(ROM, 7, 15)
        self.assertEqual(map_file.validate(doc), [])
        cx, cy = 1000 // 8, 100 // 8            # inside the 1280 px grid, past the 952 px world
        doc["collision"][cy * 32 + (cx >> 3)] |= 1 << (cx & 7)
        self.assertTrue(any("1000" in p or "camera" in p for p in map_file.validate(doc)))


class SaveAndLoadTests(unittest.TestCase):

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="map_file_"))

    def test_load_refuses_a_document_from_another_schema(self):
        path = self.dir / "future.json"
        doc = small_doc()
        doc["schema"] = 2
        path.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            map_file.load(path)
        self.assertIn("2", str(caught.exception))
        self.assertIn(str(map_file.SCHEMA), str(caught.exception))

    def test_save_then_load_returns_an_equal_document(self):
        doc = map_file.read_map(ROM, 7, 15)
        path = self.dir / "map.json"
        map_file.save(doc, path)
        self.assertEqual(map_file.load(path), doc)

    def test_save_never_overwrites_an_existing_file(self):
        path = self.dir / "map.json"
        map_file.save(small_doc(), path)
        with self.assertRaises(FileExistsError):
            map_file.save(small_doc(), path)

    def test_save_refuses_an_invalid_document(self):
        doc = small_doc()
        doc["layers"]["bg0"]["cells"].pop()
        with self.assertRaises(ValueError):
            map_file.save(doc, self.dir / "broken.json")


class ReadMapTests(unittest.TestCase):

    def test_read_map_of_7_15_validates_and_reports_its_real_tile_count(self):
        layout = layout_offset(7, 15) + map_view.ROM_BASE
        doc = map_file.read_map(ROM, 7, 15)
        self.assertEqual(map_file.validate(doc), [])
        self.assertEqual(map_file.tile_count(doc), len(tile_stream.decode_stream(ROM, layout)))
        self.assertEqual(map_file.tile_count(doc), W15_STATIC)

    def test_read_map_never_modifies_the_rom(self):
        before = bytes(ROM)
        map_file.read_map(ROM, 7, 15)
        self.assertEqual(ROM, before)

    def test_read_map_reads_every_layer_priority_from_the_rom(self):
        doc = map_file.read_map(ROM, 7, 15)
        got = {name: layer["priority"] for name, layer in doc["layers"].items()}
        self.assertEqual(got, W15_PRIORITIES)
        self.assertGreater(len(set(got.values())), 1)       # a defaulted priority fails here

    def test_read_map_follows_a_layer_priority_that_a_build_moved(self):
        moved = rom_with(layout_offset(7, 15) + 0x05, "<B", 2)
        self.assertEqual(map_file.read_map(moved, 7, 15)["layers"]["bg1"]["priority"], 2)

    def test_read_map_pads_every_layer_to_one_block_grid(self):
        doc = map_file.read_map(ROM, 7, 15)
        expected = doc["blocks"][0] * 32 * doc["blocks"][1] * 32
        self.assertEqual({len(layer["cells"]) for layer in doc["layers"].values()}, {expected})

    def test_read_map_carries_the_animated_tile_group_of_7_15(self):
        doc = map_file.read_map(ROM, 7, 15)
        self.assertEqual(len(doc["animated"]), 1)
        group = doc["animated"][0]
        self.assertEqual(group["first"], 894)
        self.assertEqual(map_file.group_tiles(group), 2)
        self.assertEqual([f["duration"] for f in group["frames"]], [20, 20])
        self.assertNotEqual(group["frames"][0]["pixels"], group["frames"][1]["pixels"])

    def test_the_animated_slots_of_7_15_are_named_by_a_real_cell(self):
        """Proof that dropping the group would break the map, not just shrink the file."""
        doc = map_file.read_map(ROM, 7, 15)
        named = {cell & 0x3FF for layer in doc["layers"].values() for cell in layer["cells"]}
        self.assertTrue(named & {894, 895})
        self.assertGreaterEqual(max(named), W15_STATIC)

    def test_read_map_of_4_50_carries_both_groups_in_list_order(self):
        """Order is the tick offset: group k starts at countdown k + 1 (bible B1078)."""
        doc = map_file.read_map(ROM, 4, 50)
        self.assertEqual([g["first"] for g in doc["animated"]], [892, 890])
        self.assertEqual([map_file.group_tiles(g) for g in doc["animated"]], [4, 2])

    def test_read_map_of_14_3_drops_its_overlay_layer_out_loud(self):
        doc = map_file.read_map(ROM, 14, 3)
        self.assertNotIn("bg0", doc["layers"])
        self.assertTrue(any("bg0" in note for note in doc["dropped"]))

    def test_read_map_refuses_a_layout_with_no_tilemap_layer(self):
        """Map 1,7 is four overlay records and no art grid, so there is no document to write."""
        with self.assertRaises(ValueError):
            map_file.read_map(ROM, 1, 7)

    def test_the_world_map_reads_but_is_reported_rather_than_accepted(self):
        """Map 6,99 is the hard case: a 1 x 1 art grid under a 4096 x 3328 px world. The document
        must say so out loud, because a reader that shrank the world to fit would hide it."""
        doc = map_file.read_map(ROM, 6, 99)
        self.assertEqual(tuple(doc["world"]), (4096, 3328))
        self.assertTrue(any("4096" in p for p in map_file.validate(doc)))

    def test_read_map_carries_the_blend_words_of_14_3(self):
        off = layout_offset(14, 3)
        doc = map_file.read_map(ROM, 14, 3)
        self.assertEqual(doc["blend"]["bldcnt"], struct.unpack_from("<H", ROM, off)[0])
        self.assertEqual(doc["blend"]["alpha"], [ROM[off + 2], ROM[off + 3]])

    def test_every_sampled_vanilla_map_reads_and_validates(self):
        for zone, area in SAMPLE_MAPS:
            with self.subTest(map=f"{zone},{area}"):
                self.assertEqual(map_file.validate(map_file.read_map(ROM, zone, area)), [])


if __name__ == "__main__":
    unittest.main()
