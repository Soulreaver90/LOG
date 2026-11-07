r"""
test_tile_stream.py - Tests for the BG tile stream codec, map-editor\tile_stream.py.

Run (absolute paths, because no tool in this project may cd):
  py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent ^
      -p test_tile_stream.py -v
The codec is read against the base ROM only. Nothing here builds or writes a ROM.
Map 6,99 is in the round trip on purpose: its stream repeats a tile with a 0xFFFF delta, so an
encoder that assumes an ascending list passes the other three maps and corrupts that one.
"""
import struct
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
MAP_ENTRY_BYTES, MAP_ENTRY_COUNT = 56, 327      # the base ROM's map table, walked end to end
LAYOUT_COUNT = 336              # distinct layouts those 327 entries reach, counted by walking the table
CHUNK_COUNT = 168               # chunk frames in the shared table (bible B1080)
SWAPPED_CHUNKS = (4, 80)        # two chunks map 14,1 loads, swapped to prove a moved table is followed
SHORT_CHUNK = (167, 167)        # (chunk, tiles) of the one chunk that is not a full 256 tile frame


def layout_of(zone: int, area: int) -> int:
    _index, entry = scene_probe.map_entry(ROM, zone, area)
    return map_view.layout_of(ROM, entry, 1)


def payload_of(layout: int) -> bytes:
    """The raw +0x48 frame payload, read the way map_view reads it."""
    return map_view.frame(ROM, map_view.u32(ROM, layout + 0x48 - map_view.ROM_BASE))


def moved_chunk_table(layout: int, left: int, right: int) -> tuple:
    """(a ROM copy, the new table address) where `layout` names its own table with two chunks swapped.

    The new table is appended past the end of the copy, so no real ROM byte moves and the only
    edited word is the layout's +0x4C. In memory only: nothing here writes a ROM to disk."""
    rom = bytearray(ROM)
    table = bytearray(rom[tile_stream.CHUNK_TABLE - map_view.ROM_BASE:][:4 * CHUNK_COUNT])
    for a, b in ((left, right), (right, left)):
        table[4 * a:4 * a + 4] = ROM[tile_stream.CHUNK_TABLE - map_view.ROM_BASE + 4 * b:][:4]
    moved = map_view.ROM_BASE + len(rom)
    rom += table
    struct.pack_into("<I", rom, layout + 0x4C - map_view.ROM_BASE, moved)
    return bytes(rom), moved


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

    def test_the_decode_is_the_section_9_readers_own(self):
        """One decoder, by identity. A second copy is how two tools come to read one build apart."""
        self.assertIs(tile_stream.decode_payload, scene_probe.tile_pairs)
        self.assertIs(tile_stream.TILE_BUDGET, scene_probe.TILE_BUDGET)

    def test_the_address_form_matches_the_offset_form_tile_for_tile(self):
        """A count alone would restate the implementation, so every tile's pixels are compared.

        This module works in ROM ADDRESSES and the section 9 reader in FILE OFFSETS. The decode is
        now one function, so what this checks is the conversion between the two forms, which is the
        real trap: a stray ROM_BASE reads a plausible stream from the wrong end of the file.

        map_view.tiles is no longer the comparison. It returns the VRAM SLOT list, the static
        stream plus every animated group, and on map 6,99 five groups overwrite slots 1 to 49.
        test_map_view owns that shape."""
        for zone, area in ROUND_TRIP_MAPS:
            with self.subTest(map=f"{zone},{area}"):
                layout = layout_of(zone, area)
                pairs = tile_stream.decode_stream(ROM, layout)
                expected = scene_probe.static_tiles(ROM, layout - map_view.ROM_BASE)
                self.assertEqual(len(expected), len(pairs))
                self.assertEqual(expected,
                                 tile_stream.tiles_of(ROM, pairs,
                                                      tile_stream.chunk_table_of(ROM, layout)))

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
        expected = [scene_probe.static_tiles(ROM, layout_of(*m) - map_view.ROM_BASE)[i]
                    for m, positions, _chunk in runs for i in positions]
        # Through the codec, not around it: the payload is what a built map would really carry.
        shipped = tile_stream.decode_payload(tile_stream.encode_stream(mixed))
        self.assertEqual(mixed, shipped)
        self.assertEqual(expected, tile_stream.tiles_of(ROM, shipped, tile_stream.CHUNK_TABLE))

    def test_every_layout_the_base_map_table_reaches_names_the_one_chunk_table(self):
        """A per map chunk table would sink mixing, so the claim is checked on all of them.

        The populations are pinned too, because a sweep that quietly stopped finding layouts would
        otherwise pass on the handful it still reached. The walk is the map table itself, not a
        guess at which zone and area numbers exist."""
        table, count = scene_probe.map_table(ROM)
        layouts = set()
        for k in range(count):
            layouts.update(l for l in scene_probe.layouts(ROM, table + MAP_ENTRY_BYTES * k) or []
                           if l is not None)
        self.assertEqual(MAP_ENTRY_COUNT, count)
        self.assertEqual(LAYOUT_COUNT, len(layouts))
        self.assertEqual({tile_stream.CHUNK_TABLE},
                         {tile_stream.chunk_table_of(ROM, layout + map_view.ROM_BASE)
                          for layout in layouts})

    def test_a_moved_chunk_table_is_followed_through_to_the_pixels(self):
        """The base ROM cannot show this: every layout on it names CHUNK_TABLE, so a reader that
        ignored the layout and returned the constant would pass any test run against the base.

        r40 map 14,4 really does name its own table at 0x0890A92C, and the first version of this
        test could not have caught that. So the move is made here instead, in a ROM copy held in
        memory, with two chunk pointers swapped. Nothing is written to disk."""
        layout = layout_of(*MIXED_MAPS[0])
        pairs = tile_stream.decode_stream(ROM, layout)
        left, right = SWAPPED_CHUNKS
        self.assertTrue({left, right} <= {chunk for chunk, _tile in pairs},
                        "the swap must touch chunks this map really loads")

        rom, moved = moved_chunk_table(layout, left, right)

        self.assertEqual(moved, tile_stream.chunk_table_of(rom, layout))
        self.assertNotEqual(tile_stream.CHUNK_TABLE, tile_stream.chunk_table_of(rom, layout))

        swap = {left: right, right: left}
        expected = tile_stream.tiles_of(ROM, [(swap.get(c, c), t) for c, t in pairs],
                                        tile_stream.CHUNK_TABLE)
        through_the_layout = tile_stream.tiles_of(rom, pairs,
                                                  tile_stream.chunk_table_of(rom, layout))
        self.assertEqual(expected, through_the_layout)
        self.assertNotEqual(tile_stream.tiles_of(ROM, pairs, tile_stream.CHUNK_TABLE),
                            through_the_layout, "the swap must change the pixels, or it proves nothing")


class GuardTests(unittest.TestCase):
    """The three silent wrong answers the codec used to give. Each must now raise."""

    def test_an_odd_payload_is_refused_not_truncated(self):
        with self.assertRaises(ValueError):
            tile_stream.decode_payload(b"\x00\x01\x02")

    def test_a_tile_past_the_end_of_its_chunk_is_refused(self):
        """No vanilla tile does this, measured over all 336 base layouts, so only a written stream
        can. A short slice would reach the game as missing pixels.

        167 of the 168 chunks hold a full 256 tiles, so only the last one can overrun at all."""
        chunk, tiles = SHORT_CHUNK
        self.assertEqual(tiles, len(tile_stream.tiles_of(ROM, [(chunk, t) for t in range(tiles)],
                                                         tile_stream.CHUNK_TABLE)))
        with self.assertRaises(ValueError) as caught:
            tile_stream.tiles_of(ROM, [(chunk, tiles)], tile_stream.CHUNK_TABLE)
        self.assertIn(str(tiles), str(caught.exception))

    def test_a_file_offset_where_an_address_belongs_is_refused(self):
        """scene_probe.layouts yields file offsets and map_view.layout_of yields addresses."""
        layout = layout_of(*MIXED_MAPS[0])
        with self.assertRaises(ValueError):
            tile_stream.decode_stream(ROM, layout - map_view.ROM_BASE)
        with self.assertRaises(ValueError):
            tile_stream.chunk_table_of(ROM, layout - map_view.ROM_BASE)


if __name__ == "__main__":
    unittest.main()
