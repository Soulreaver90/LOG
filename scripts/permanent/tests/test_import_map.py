r"""
test_import_map.py - Tests for map-editor\import_map.py, the bridge from a saved map to a real map.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_import_map.py -v
Nothing here writes a ROM file. Every ROM is built in memory and nothing is written under data\.

Map 7,15 is the witness for the camera, on purpose. Its world is 952 x 768 inside a 1280 x 1024
block grid, so an `apply` that took the grid as the width would write (1041, 865) where the ROM
must hold (713, 609). That is the plateau fault, and it is the one fault a full-map render hides.

The relocated-table test builds build_list_trial_ending.txt in memory, because the BASE ROM cannot
show that a reader FOLLOWS the table base. On that build the table is already at a moved address and
the count is already 328, so a reader pinned to the base constants finds the wrong table and still
reads 327 plausible entries.
"""
import hashlib
import struct
import sys
import unittest
from pathlib import Path

import log2_build
from scene import map_view
from scene import scene_probe
from scene.scene_lib import words_naming
import log_paths  # noqa: E402

sys.path.insert(0, str(log_paths.MAP_EDITOR))

import import_map                                                          # noqa: E402
import map_file                                                            # noqa: E402

ROM_BASE = map_view.ROM_BASE
TRIAL_ENDING = log_paths.BUILD_LISTS / "build_list_trial_ending.txt"

# Map 7,15, re-measured below by the tests that use them.
W15_PAIR = (713, 609)                   # the +0x08 and +0x0A words map 7,15 stores
W15_GRID_PAIR = (1041, 865)             # what a grid-derived pair would write instead
NEW_ZONE, NEW_AREA = 7, 101             # zone 7 uses areas 1 to 26; plateau took 100

_CACHE = {}


def padded_base() -> bytes:
    """The base ROM filled out to 16 MB, which is the shape every build has and `apply` needs."""
    if "base" not in _CACHE:
        _CACHE["base"] = bytes(log2_build.assemble(log2_build.BASE, [])[0])
    return _CACHE["base"]


def relocated_build() -> bytes:
    """A build whose map table has ALREADY moved: dev plus battle_arena and ending_fight."""
    if "moved" not in _CACHE:
        names = log2_build.read_build_list(TRIAL_ENDING)
        _CACHE["moved"] = bytes(log2_build.assemble(log2_build.BASE, names)[0])
    return _CACHE["moved"]


def map_7_15() -> dict:
    """Map 7,15 as a document. Read once: it carries 633 tiles and an animated group."""
    if "7,15" not in _CACHE:
        _CACHE["7,15"] = map_file.read_map(padded_base(), 7, 15)
    return _CACHE["7,15"]


def small_doc(**over) -> dict:
    """A tiny valid document: one block, one loaded tile. Cheap enough to mutate freely."""
    doc = map_file.blank(blocks=(1, 1), world=(256, 256))
    doc.update(over)
    return doc


def layout_of(rom: bytes, zone: int, area: int, var: int = 1) -> int:
    """The file offset of one map's layout, read through THIS rom's own table."""
    _index, entry = scene_probe.map_entry(rom, zone, area)
    return map_view.layout_of(rom, entry, var) - ROM_BASE


def camera_in_rom(rom: bytes, zone: int, area: int) -> tuple:
    return struct.unpack_from("<HH", rom, layout_of(rom, zone, area) + 0x08)


class CameraTests(unittest.TestCase):
    """The pair is computed from the world. It is never inherited and never derived from the grid."""

    def test_apply_writes_the_computed_camera_pair_not_the_documents(self):
        doc = map_7_15()
        self.assertEqual(tuple(doc["world"]), (952, 768))
        self.assertEqual((doc["blocks"][0] * 256, doc["blocks"][1] * 256), (1280, 1024))
        new = import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)
        self.assertEqual(camera_in_rom(new, NEW_ZONE, NEW_AREA), W15_PAIR)
        self.assertNotEqual(camera_in_rom(new, NEW_ZONE, NEW_AREA), W15_GRID_PAIR)

    def test_apply_refuses_a_document_whose_stored_camera_pair_disagrees_with_its_world(self):
        """The plateau shipped a donor's 449 on a 1024 px world. A document may not carry one."""
        doc = small_doc()
        doc["camera"] = [449, 449]
        with self.assertRaisesRegex(ValueError, "449"):
            import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)

    def test_apply_accepts_a_stored_camera_pair_that_agrees(self):
        doc = small_doc()
        doc["camera"] = list(map_file.camera_pair(*doc["world"]))
        new = import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)
        self.assertEqual(camera_in_rom(new, NEW_ZONE, NEW_AREA), (17, 97))


class ValidateTests(unittest.TestCase):
    """Everything map_file.validate refuses, apply refuses too, before it writes a byte."""

    def test_apply_rejects_a_document_that_fails_validate(self):
        """An EXTRA cell, not a missing one: a writer drops extras in silence and raises on a gap."""
        doc = small_doc()
        doc["layers"]["bg0"]["cells"].append(0)
        with self.assertRaisesRegex(ValueError, "bg0"):
            import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)

    def test_apply_rejects_a_document_over_the_tile_budget(self):
        doc = small_doc(tiles=[[0, n % 256] for n in range(map_file.TILE_BUDGET + 1)])
        with self.assertRaises(ValueError) as caught:
            import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)
        self.assertIn(str(map_file.TILE_BUDGET + 1), str(caught.exception))
        self.assertIn(str(map_file.TILE_BUDGET), str(caught.exception))

    def test_apply_rejects_layers_that_disagree_on_the_block_grid(self):
        """The other half of the plateau fault. The format cannot say it, so this is the check."""
        doc = small_doc()
        doc["layers"]["bg1"]["cells"] = doc["layers"]["bg1"]["cells"] * 4
        with self.assertRaisesRegex(ValueError, "bg1"):
            import_map.apply(padded_base(), doc, NEW_ZONE, NEW_AREA)

    def test_apply_refuses_a_zone_and_area_the_rom_already_holds(self):
        with self.assertRaisesRegex(ValueError, "7,15"):
            import_map.apply(padded_base(), map_7_15(), 7, 15)

    def test_apply_refuses_a_rom_that_was_never_padded_to_16_mb(self):
        base = log2_build.BASE.read_bytes()
        with self.assertRaises(ValueError):
            import_map.apply(base, small_doc(), NEW_ZONE, NEW_AREA)


class CountByteTests(unittest.TestCase):
    """The map count lives in one byte of code at rom:0xE0AE. Appending past it must fail closed."""

    @staticmethod
    def rom_with_count_byte(value: int) -> bytes:
        rom = bytearray(padded_base())
        rom[import_map.MAP_COUNT_BYTE] = value
        return bytes(rom)

    def test_apply_refuses_when_the_map_count_byte_would_overflow(self):
        with self.assertRaises(ValueError) as caught:
            import_map.apply(self.rom_with_count_byte(0xFE), small_doc(), NEW_ZONE, NEW_AREA)
        self.assertIn(str(import_map.MAP_COUNT_CAP), str(caught.exception))
        self.assertIn(f"0x{import_map.MAP_COUNT_BYTE:X}", str(caught.exception))

    def test_one_below_the_cap_fails_for_some_other_reason(self):
        """The discriminator. Without it the overflow test would pass on any raise at all."""
        with self.assertRaises(ValueError) as caught:
            import_map.apply(self.rom_with_count_byte(0xFD), small_doc(), NEW_ZONE, NEW_AREA)
        self.assertNotIn(str(import_map.MAP_COUNT_CAP), str(caught.exception))


class RelocatedTableTests(unittest.TestCase):
    """A build may have moved the table already. apply reads the live base, never a constant."""

    @classmethod
    def setUpClass(cls):
        cls.before = relocated_build()
        cls.old_table, cls.old_count = scene_probe.map_table(cls.before)
        cls.after = import_map.apply(cls.before, small_doc(), NEW_ZONE, NEW_AREA)
        cls.new_table, cls.new_count = scene_probe.map_table(cls.after)

    def test_the_build_really_had_moved_its_table(self):
        self.assertNotEqual(self.old_table, scene_probe.MAP_TABLE)
        self.assertEqual(self.old_count, 328)

    def test_apply_composes_on_top_of_an_already_relocated_table(self):
        self.assertEqual(self.new_count, self.old_count + 1)
        old = self.before[self.old_table:self.old_table + 56 * self.old_count]
        self.assertEqual(self.after[self.new_table:self.new_table + 56 * self.old_count], old)
        self.assertEqual(self.after[self.new_table + 56 * self.old_count], NEW_ZONE)
        scene_probe.map_entry(self.after, 6, 100)          # battle_arena's arena is still reachable
        scene_probe.map_entry(self.after, NEW_ZONE, NEW_AREA)

    def test_every_word_that_named_the_table_now_names_the_new_one(self):
        """scene_probe reads only rom:0xEBD8. The game also reads rom:0x5ADC and rom:0x5D5C."""
        self.assertEqual(words_naming(self.after, self.new_table), list(import_map.BASE_LITERALS))
        self.assertEqual(words_naming(self.after, self.old_table), [])
        self.assertEqual(scene_probe.u32(self.after, import_map.ENTRY3_LITERAL),
                         self.new_table + 56 * import_map.ENTRY3 + ROM_BASE)

    def test_every_word_that_landed_in_the_dead_table_and_moved_is_one_of_the_four(self):
        """A second search shape, over the whole OLD table and not just its base.

        `words_naming` only finds words naming one address, so it cannot see a literal pointing at
        some other entry inside the table. This sweeps the range. It compares the two ROMs rather
        than demanding an empty set, because 9 words of the base ROM's graphics and script data
        happen to hold a value in this range and are not pointers. They sit in `before` too, where
        the table is live, and they survived battle_arena's and ending_fight's relocations before
        mine. What matters is that apply REMOVES exactly four and ADDS none."""
        def landing_in(rom: bytes) -> set:
            low = self.old_table + ROM_BASE
            high = low + 56 * self.old_count
            words = memoryview(rom[:len(rom) & ~3]).cast("I")
            return {4 * i for i, word in enumerate(words) if low <= word < high}

        was, now = landing_in(self.before), landing_in(self.after)
        self.assertEqual(sorted(was - now),
                         sorted(set(import_map.BASE_LITERALS) | {import_map.ENTRY3_LITERAL}))
        self.assertEqual(sorted(now - was), [])

    def test_a_second_apply_finds_the_map_the_first_one_appended(self):
        again = import_map.apply(self.after, small_doc(), NEW_ZONE, NEW_AREA + 1)
        self.assertEqual(scene_probe.map_table(again)[1], self.old_count + 2)
        scene_probe.map_entry(again, NEW_ZONE, NEW_AREA)
        scene_probe.map_entry(again, NEW_ZONE, NEW_AREA + 1)

    def test_apply_writes_only_free_space_and_the_five_hand_off_sites(self):
        handoff = set(import_map.BASE_LITERALS) | {import_map.ENTRY3_LITERAL}
        sites = {off for lit in handoff for off in range(lit, lit + 4)}
        sites.add(import_map.MAP_COUNT_BYTE)
        stray = [off for off in range(len(self.before))
                 if self.before[off] != self.after[off] and off not in sites
                 and self.before[off] != 0xFF]
        self.assertEqual(stray[:8], [])

    def test_apply_leaves_the_rom_it_was_given_alone(self):
        """A bytearray, so the ROM given COULD be written. bytes could not, and would pass empty."""
        given = bytearray(self.before)
        was = hashlib.sha1(given).hexdigest()
        import_map.apply(given, small_doc(), NEW_ZONE, NEW_AREA)
        self.assertEqual(hashlib.sha1(given).hexdigest(), was)


class FreeSpaceTests(unittest.TestCase):
    """Where apply puts new data. Fill and data that ends in 0xFF read the same, so this is a trap."""

    def test_free_space_starts_above_everything_the_build_allocated(self):
        """build_list_dev.txt is the witness: its last allocation ends in 20 bytes of 0xFF, and a
        plain backwards scan for a non-fill byte returns an offset inside it."""
        for name in ("build_list_dev.txt", "build_list_trial_ending.txt"):
            with self.subTest(name):
                rom, alloc = log2_build.assemble(
                    log2_build.BASE, log2_build.read_build_list(log2_build.BUILD_LIST.parent / name))
                high = max(at + size for at, size in alloc.used())
                self.assertGreaterEqual(import_map.free_from(bytes(rom)), high)

    def test_an_untouched_expansion_area_is_free_from_its_start(self):
        self.assertEqual(import_map.free_from(padded_base()), import_map.ALLOC_REGION[0])


class ReadBackTests(unittest.TestCase):
    """The proof is what the ROM carries, read back by the section 9 reader, not by import_map."""

    @classmethod
    def setUpClass(cls):
        cls.doc = map_7_15()
        cls.rom = import_map.apply(padded_base(), cls.doc, NEW_ZONE, NEW_AREA)
        cls.layout = layout_of(cls.rom, NEW_ZONE, NEW_AREA)
        cls.source = layout_of(padded_base(), 7, 15)

    def test_the_appended_map_reads_back_through_scene_probe(self):
        back = map_file.read_map(self.rom, NEW_ZONE, NEW_AREA)
        for key in ("world", "blocks", "collision", "terrain", "tiles"):
            self.assertEqual(back[key], self.doc[key], key)
        self.assertEqual(sorted(back["layers"]), sorted(self.doc["layers"]))
        for name, layer in self.doc["layers"].items():
            for key in ("priority", "scroll", "offset", "cells"):
                self.assertEqual(back["layers"][name][key], layer[key], f"{name} {key}")

    def test_every_bg_layer_carries_the_one_block_grid_and_its_own_class(self):
        grid = tuple(self.doc["blocks"])
        for rec in scene_probe.layout_layers(self.rom, self.layout):
            self.assertEqual(rec["kind"], "tilemap", f"BG{rec['bg']}")
            self.assertEqual(rec["blocks"], grid, f"BG{rec['bg']}")

    def test_the_tile_stream_decodes_to_the_same_pixels_as_map_7_15(self):
        self.assertEqual(scene_probe.static_tiles(self.rom, self.layout),
                         scene_probe.static_tiles(padded_base(), self.source))

    def test_the_animated_group_survives_with_its_slot_and_its_frames(self):
        got = scene_probe.layout_groups(self.rom, self.layout)
        want = scene_probe.layout_groups(padded_base(), self.source)
        self.assertEqual(len(got), len(want))
        self.assertTrue(want, "map 7,15 carries one animated group, at slot 894")
        for a, b in zip(got, want):
            self.assertEqual((a["first"], a["tiles"]), (b["first"], b["tiles"]))
            self.assertEqual([f["pixels"] for f in a["frames"]], [f["pixels"] for f in b["frames"]])

    def test_every_cell_names_a_slot_the_new_map_loads(self):
        """The fault that drew 509 false holes on the plateau: a cell naming a slot nothing fills."""
        loaded = scene_probe.loaded_tiles(self.rom, self.layout)
        named = {c & 0x3FF for layer in self.doc["layers"].values() for c in layer["cells"]}
        empty = sorted(n for n in named if n >= len(loaded) or not loaded[n])
        self.assertEqual(empty, [])

    def test_the_collision_frame_reads_back_cell_for_cell(self):
        _at, _kind, bits = scene_probe.collision_bits(self.rom, self.layout)
        self.assertEqual(list(bits), self.doc["collision"])

    def test_the_new_map_names_no_prop_and_no_door(self):
        self.assertEqual(scene_probe.layout_props(self.rom, self.layout), [])
        self.assertEqual(scene_probe.u32(self.rom, self.layout + scene_probe.L_DOOR_COUNT), 0)


if __name__ == "__main__":
    unittest.main()
