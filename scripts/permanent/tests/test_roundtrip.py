r"""
test_roundtrip.py - Tests for map-editor\roundtrip.py: a real map out of the ROM and back in.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_roundtrip.py -v
Nothing here writes a ROM file. Every ROM is built in memory, every document goes to a temporary
folder, and nothing is written under data\.

WHY A BUILD AND NOT THE BASE ROM. Map 14,4 of build_list_dev.txt names its OWN chunk table at
0x0890A92C, not the shared pool 0x084DF574. The base ROM cannot show that, because all 336 base
layouts name the pool. A round trip that compared tile PAIRS would pass on that map and put the
wrong pixels in the game, which is the one failure in this file that has no symptom.

WHY PIXELS AND NOT PAIRS. A pair is (chunk, tile) in some table. Equality of pairs says only that
two documents index the same way, never that they name the same art.
"""
import struct
import sys
import tempfile
import unittest
from pathlib import Path

import log2_build
from scene import map_view
from scene import scene_probe

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import import_map                                                          # noqa: E402
import map_file                                                            # noqa: E402
import roundtrip                                                           # noqa: E402
import tile_stream                                                         # noqa: E402

DEV_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_dev.txt"
PRIVATE_TABLE = 0x0890A92C          # map 14,4's own chunk table in every current build
PRIVATE_MAP = (14, 4)
_CACHE = {}


def padded_base() -> bytes:
    """The base ROM filled out to 16 MB, the shape every build has and `apply` needs."""
    if "base" not in _CACHE:
        _CACHE["base"] = bytes(log2_build.assemble(log2_build.BASE, [])[0])
    return _CACHE["base"]


def dev_build() -> bytes:
    """The dev master. Its map 14,4 carries a private chunk table, which the base ROM cannot."""
    if "dev" not in _CACHE:
        names = log2_build.read_build_list(DEV_LIST)
        _CACHE["dev"] = bytes(log2_build.assemble(log2_build.BASE, names)[0])
    return _CACHE["dev"]


def layout_of(rom: bytes, zone: int, area: int, var: int = 1) -> int:
    _index, entry = scene_probe.map_entry(rom, zone, area)
    return map_view.layout_of(rom, entry, var) - map_view.ROM_BASE


class FieldTests(unittest.TestCase):
    """The comparison must cover the whole document, so a new field cannot slip past unchecked."""

    def test_the_carried_and_skipped_fields_are_exactly_a_documents_keys(self):
        doc = map_file.read_map(padded_base(), 7, 15)
        self.assertEqual(set(doc), set(roundtrip.CARRIED) | set(roundtrip.SKIPPED))

    def test_a_document_with_an_unknown_field_is_reported_not_ignored(self):
        doc = map_file.read_map(padded_base(), 7, 15)
        doc["loudness"] = 11
        self.assertIn("loudness", " ".join(roundtrip.unknown_fields(doc)))

    def test_only_dropped_is_skipped(self):
        self.assertEqual(("dropped",), roundtrip.SKIPPED)


class DifferenceTests(unittest.TestCase):
    """`differences` must be able to go red. A comparison that cannot fail proves nothing."""

    def setUp(self):
        self.rom = padded_base()
        self.doc = map_file.read_map(self.rom, 7, 15)

    def test_a_document_compared_with_itself_has_no_difference(self):
        self.assertEqual([], roundtrip.differences(self.doc, self.doc, self.rom, self.rom))

    def test_a_changed_layer_offset_is_reported(self):
        """Bible B1082: a layer's +0x0C scrolls its art by offset >> 10 px. Map 7,15's bg1 carries
        64 px. Losing it moves the whole layer, and no field but this one would say so."""
        after = map_file.read_map(self.rom, 7, 15)
        self.assertEqual([65536, 65536], after["layers"]["bg1"]["offset"])
        after["layers"]["bg1"]["offset"] = [0, 0]
        self.assertIn("bg1", " ".join(roundtrip.differences(self.doc, after, self.rom, self.rom)))

    def test_a_changed_camera_world_is_reported(self):
        after = map_file.read_map(self.rom, 7, 15)
        after["world"] = [1280, 1024]
        self.assertIn("world", " ".join(roundtrip.differences(self.doc, after, self.rom, self.rom)))

    def test_a_changed_cell_is_reported(self):
        after = map_file.read_map(self.rom, 7, 15)
        after["layers"]["bg1"]["cells"][0] ^= 1
        self.assertIn("bg1", " ".join(roundtrip.differences(self.doc, after, self.rom, self.rom)))

    def test_a_changed_chunk_table_is_reported_even_when_the_pairs_match(self):
        after = map_file.read_map(self.rom, 7, 15)
        after["chunk_table"] = PRIVATE_TABLE
        self.assertEqual(self.doc["tiles"], after["tiles"])
        self.assertIn("chunk_table",
                      " ".join(roundtrip.differences(self.doc, after, self.rom, dev_build())))

    def test_a_changed_tile_pair_is_caught_by_the_pixel_comparison(self):
        """`differences` never compares the pairs, so only the pixels can report this."""
        after = map_file.read_map(self.rom, 7, 15)
        after["tiles"][5] = after["tiles"][600]
        self.assertNotEqual(roundtrip.pixels(self.rom, self.doc)[5],
                            roundtrip.pixels(self.rom, after)[5])
        problems = " ".join(roundtrip.differences(self.doc, after, self.rom, self.rom))
        self.assertIn("pixels differ", problems)


class RoundTripTests(unittest.TestCase):
    """The plan's own test: a real map leaves the ROM, passes through a file, and comes back."""

    def test_a_vanilla_map_survives_export_import_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            result = roundtrip.check(padded_base(), 7, 15, folder=folder)
        self.assertEqual([], result["problems"])
        self.assertTrue(result["ok"])

    def test_the_round_trip_really_goes_through_a_saved_file(self):
        """Through the editor means through map_file.save and map_file.load, not a dict copy."""
        with tempfile.TemporaryDirectory() as folder:
            doc = map_file.read_map(padded_base(), 7, 15)
            written = roundtrip.through_a_file(doc, Path(folder))
            self.assertTrue(list(Path(folder).glob("*.json")))
            self.assertEqual([], roundtrip.differences(doc, written, padded_base(),
                                                       padded_base()))

    def test_two_maps_that_share_a_frame_pointer_both_survive(self):
        """Maps 6,1 and 4,50 name one frame. A byte comparison of the blob would fail here."""
        with tempfile.TemporaryDirectory() as folder:
            for zone, area in ((6, 1), (4, 50)):
                result = roundtrip.check(padded_base(), zone, area, folder=folder)
                self.assertEqual([], result["problems"], f"map {zone},{area}")

    def test_the_round_trip_writes_the_computed_camera_pair(self):
        with tempfile.TemporaryDirectory() as folder:
            doc = map_file.read_map(padded_base(), 7, 15)
            new, _back, zone, area = roundtrip.trip(padded_base(), doc, folder=Path(folder))
        pair = struct.unpack_from("<HH", new, layout_of(new, zone, area) + 0x08)
        self.assertEqual((713, 609), pair)

    def test_a_map_the_reader_refuses_is_reported_as_skipped_not_as_a_pass(self):
        """Map 1,7's four records are all the overlay class, so it has no editable art."""
        with tempfile.TemporaryDirectory() as folder:
            result = roundtrip.check(padded_base(), 1, 7, folder=folder)
        self.assertFalse(result["ok"])
        self.assertTrue(result["skipped"])


class ChunkTableTests(unittest.TestCase):
    """Finding 2: a document that does not name its chunk table resolves to the wrong pixels."""

    def test_the_dev_build_really_gave_map_14_4_a_private_chunk_table(self):
        """The precondition. Without it the test below would pass for the wrong reason."""
        rom = dev_build()
        word = scene_probe.u32(rom, layout_of(rom, *PRIVATE_MAP) + 0x4C)
        self.assertEqual(PRIVATE_TABLE, word)
        self.assertNotEqual(tile_stream.CHUNK_TABLE, word)

    def test_map_14_4_loads_a_chunk_that_its_private_table_alone_holds(self):
        """What the private table IS, measured rather than assumed. It copies the shared pool's 168
        entries and adds a 169th at 0x0890ACF4. Map 14,4 loads from that one, and the pool's word
        at the same index is 0x00000001, the next structure. So the shared pool cannot draw this
        map: it raises. A table that REPLACED an entry would draw the wrong art in silence, and no
        build has one today."""
        rom = dev_build()
        doc = map_file.read_map(rom, *PRIVATE_MAP)
        self.assertIn(168, {chunk for chunk, _tile in doc["tiles"]})
        self.assertEqual(605, len(roundtrip.pixels(rom, doc)))
        doc["chunk_table"] = tile_stream.CHUNK_TABLE
        with self.assertRaises((ValueError, struct.error)):
            roundtrip.pixels(rom, doc)

    def test_a_document_carries_the_chunk_table_it_was_read_from(self):
        rom = dev_build()
        self.assertEqual(PRIVATE_TABLE, map_file.read_map(rom, *PRIVATE_MAP)["chunk_table"])
        self.assertEqual(tile_stream.CHUNK_TABLE, map_file.read_map(rom, 7, 15)["chunk_table"])

    def test_a_new_map_names_the_shared_pool(self):
        self.assertEqual(tile_stream.CHUNK_TABLE,
                         map_file.blank((1, 1), (256, 256))["chunk_table"])

    def test_a_private_chunk_table_map_survives_the_round_trip(self):
        """The pixels, not the pairs. Before the document carried its table this put map 14,4's
        indices against the shared pool and wrote 72 tiles of another map's art, with no error."""
        with tempfile.TemporaryDirectory() as folder:
            result = roundtrip.check(dev_build(), *PRIVATE_MAP, folder=folder)
        self.assertEqual([], result["problems"])

    def test_apply_refuses_a_document_whose_chunk_table_this_rom_has_not_got(self):
        """The base ROM has no table at 0x0890A92C: that address is 0xFF fill there."""
        doc = map_file.read_map(dev_build(), *PRIVATE_MAP)
        with self.assertRaisesRegex(ValueError, "890A92C"):
            import_map.apply(padded_base(), doc, 7, 101)

    def test_validate_reports_a_document_with_no_chunk_table(self):
        doc = map_file.blank((1, 1), (256, 256))
        del doc["chunk_table"]
        self.assertIn("chunk_table", " ".join(map_file.validate(doc)))

    def test_load_refuses_a_document_from_the_schema_that_had_no_chunk_table(self):
        """Schema 1 documents carry no provenance, so loading one is a guess, not a read."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "old.json"
            path.write_text('{"schema": 1, "blocks": [1, 1]}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "1"):
                map_file.load(path)


if __name__ == "__main__":
    unittest.main()
