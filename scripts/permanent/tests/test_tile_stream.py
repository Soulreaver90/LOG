r"""
test_tile_stream.py - Tests for the BG tile stream codec, map-editor\tile_stream.py.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_tile_stream.py -v
The codec is read against the base ROM only. Nothing here builds or writes a ROM.
Map 6,99 is in the round trip on purpose: its stream repeats a tile with a 0xFFFF delta, so an
encoder that assumes an ascending list passes the other three maps and corrupts that one.
"""
import sys
import unittest
from collections import Counter
from pathlib import Path

from scene import map_view
from scene import scene_probe

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import tile_stream                                                          # noqa: E402

ROM = map_view.BASE.read_bytes()
ROUND_TRIP_MAPS = ((14, 1), (7, 15), (4, 50), (6, 99))
MIXED_MAPS = ((14, 1), (7, 15))


def layout_of(zone: int, area: int) -> int:
    _index, entry = scene_probe.map_entry(ROM, zone, area)
    return map_view.layout_of(ROM, entry, 1)


def payload_of(layout: int) -> bytes:
    """The raw +0x48 frame payload, read the way map_view reads it."""
    return map_view.frame(ROM, map_view.u32(ROM, layout + 0x48 - map_view.ROM_BASE))


def busiest_foreign_chunk(pairs: list, other_chunks: set) -> tuple:
    """(positions, chunk) of the chunk this map loads most and the other map never loads."""
    counts = Counter(chunk for chunk, _tile in pairs if chunk not in other_chunks)
    chunk = counts.most_common(1)[0][0]
    return [i for i, (c, _tile) in enumerate(pairs) if c == chunk], chunk


class DecodeTests(unittest.TestCase):

    def test_decode_then_encode_reproduces_every_vanilla_stream(self):
        for zone, area in ROUND_TRIP_MAPS:
            with self.subTest(map=f"{zone},{area}"):
                payload = payload_of(layout_of(zone, area))
                pairs = tile_stream.decode_payload(payload)
                self.assertEqual(payload, tile_stream.encode_stream(pairs))

    def test_decode_stream_matches_map_view_tile_for_tile(self):
        """A count alone would restate the implementation, so every tile's pixels are compared."""
        for zone, area in ROUND_TRIP_MAPS:
            with self.subTest(map=f"{zone},{area}"):
                layout = layout_of(zone, area)
                pairs = tile_stream.decode_stream(ROM, layout)
                expected = map_view.tiles(ROM, layout)
                self.assertEqual(len(expected), len(pairs))
                self.assertEqual(expected, tile_stream.tiles_of(ROM, pairs))

    def test_every_vanilla_stream_fits_the_budget(self):
        for zone, area in ROUND_TRIP_MAPS:
            with self.subTest(map=f"{zone},{area}"):
                self.assertLessEqual(len(tile_stream.decode_stream(ROM, layout_of(zone, area))),
                                     tile_stream.TILE_BUDGET)


class EncodeTests(unittest.TestCase):

    def test_encode_refuses_more_than_the_budget(self):
        too_many = [(0, 0)] * (tile_stream.TILE_BUDGET + 1)
        with self.assertRaises(ValueError) as caught:
            tile_stream.encode_stream(too_many)
        self.assertIn(str(tile_stream.TILE_BUDGET + 1), str(caught.exception))
        self.assertIn(str(tile_stream.TILE_BUDGET), str(caught.exception))

    def test_encode_accepts_exactly_the_budget(self):
        self.assertEqual(2 * tile_stream.TILE_BUDGET,
                         len(tile_stream.encode_stream([(0, 0)] * tile_stream.TILE_BUDGET)))

    def test_encode_keeps_an_order_the_loader_allows_but_vanilla_never_uses(self):
        """Map_LoadLayer re-decodes a chunk whenever the high byte changes, so a descending or
        repeating list is legal. The delta is masked to 16 bits, which is what carries it."""
        pairs = [(9, 40), (9, 40), (3, 200), (167, 255), (0, 0)]
        self.assertEqual(pairs, tile_stream.decode_payload(tile_stream.encode_stream(pairs)))

    def test_encode_refuses_a_pair_that_is_not_two_bytes(self):
        for bad in [(256, 0), (0, 256), (-1, 0), (0, -1)]:
            with self.subTest(pair=bad):
                with self.assertRaises(ValueError):
                    tile_stream.encode_stream([bad])


class MixedSourceTests(unittest.TestCase):
    """The question the whole map editor rests on: may one stream load tiles from two source maps?"""

    def test_a_mixed_stream_loads_each_source_maps_own_tiles(self):
        runs = []
        pairs = {m: tile_stream.decode_stream(ROM, layout_of(*m)) for m in MIXED_MAPS}
        chunks = {m: {chunk for chunk, _tile in pairs[m]} for m in MIXED_MAPS}
        self.assertTrue(chunks[MIXED_MAPS[0]] & chunks[MIXED_MAPS[1]],
                        "the two maps must share chunks, or the global pool claim is already wrong")
        for this, other in (MIXED_MAPS, MIXED_MAPS[::-1]):
            positions, chunk = busiest_foreign_chunk(pairs[this], chunks[other])
            self.assertNotIn(chunk, chunks[other])
            runs.append((this, positions[:16], chunk))

        mixed = [pairs[m][i] for m, positions, _chunk in runs for i in positions]
        expected = [map_view.tiles(ROM, layout_of(*m))[i] for m, positions, _chunk in runs
                    for i in positions]
        self.assertEqual(expected, tile_stream.tiles_of(ROM, mixed))

    def test_every_vanilla_layout_names_the_one_chunk_table(self):
        """A per map chunk table would sink mixing, so the claim is checked on all of them."""
        tables = set()
        for zone in range(20):
            for area in range(120):
                try:
                    _index, entry = scene_probe.map_entry(ROM, zone, area)
                    chain = scene_probe.layouts(ROM, entry)
                except (ValueError, IndexError, KeyError):
                    continue
                for layout in chain or []:
                    if layout is not None:
                        tables.add(map_view.u32(ROM, layout + 0x4C))
        self.assertEqual({tile_stream.CHUNK_TABLE}, tables)


if __name__ == "__main__":
    unittest.main()
