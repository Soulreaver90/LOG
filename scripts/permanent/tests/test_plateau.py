r"""
test_plateau.py - The plateau trial: map 7,100, a plateau TOP for the final fight.

The module is built once for the whole class, on top of the trial chain it needs, and every test
reads the RESULT. A test that only re-ran the module's own arithmetic would prove nothing.
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import log2_build  # noqa: E402
from patches import plateau  # noqa: E402

from scene.scene_lib import ext  # noqa: E402

ROM_BASE = 0x08000000
MAP_SIZE = 56


CHAIN = ["battle_arena", "ending_fight", "future_androids", "plateau"]


def _build():
    before, _ = log2_build.assemble(log2_build.BASE, CHAIN[:-1])
    rom, alloc = log2_build.assemble(log2_build.BASE, CHAIN)
    return bytes(before), rom, alloc.notes["plateau"]


class PlateauTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before, cls.rom, cls.notes = _build()

    # ----- the map entry -----

    def test_the_entry_is_map_7_100_with_one_variation(self):
        at = self.notes["entry"]
        self.assertEqual((self.rom[at], self.rom[at + 1], self.rom[at + 2]), (7, 100, 1))

    def test_the_entry_carries_no_region_and_no_door(self):
        at = self.notes["entry"]
        self.assertEqual(self.rom[at + 3], 0, "region count")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x10)[0], 0, "region list")
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + 0x40)[0], 0, "layout door count")
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + 0x44)[0], 0, "layout door list")

    def test_the_entry_carries_combat_the_blank_banner_the_music_and_the_arena_items(self):
        at = self.notes["entry"]
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x08)[0], 1, "combat")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x0C)[0], 0xDD, "banner")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x24)[0], 38, "music")
        self.assertEqual(self.rom[at + 4], 2, "item count")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x14)[0] - ROM_BASE,
                         self.notes["items"])

    def test_the_entry_is_the_live_arena_entry_with_two_words_changed(self):
        at = self.notes["entry"]
        table, count = plateau.map_table(self.rom)
        _, arena_at = plateau.map_entry(self.rom, 6, 100)
        ours = bytearray(self.rom[at:at + MAP_SIZE])
        theirs = bytearray(self.rom[arena_at:arena_at + MAP_SIZE])
        ours[0] = theirs[0]
        ours[0x2C:0x30] = theirs[0x2C:0x30]
        self.assertEqual(bytes(ours), bytes(theirs))

    # ----- the layout -----

    def test_the_layout_writes_its_own_camera_pair(self):
        got = struct.unpack_from("<HH", self.rom, self.notes["layout"] + plateau.L_CLAMP)
        self.assertEqual(got, plateau.CLAMP)
        self.assertEqual(got, (plateau.MAP_PIXELS[0] - 239, plateau.MAP_PIXELS[1] - 159))
        self.assertNotEqual(got, plateau.SOURCE_CLAMP, "map 7,15's pair would hide the east and south")

    def test_the_layout_carries_map_7_15s_animated_tile_group(self):
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_ANIM_COUNT)[0], 1)
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_ANIM_LIST)[0],
                         struct.unpack_from("<I", self.before,
                                            plateau.SOURCE_LAYOUT + plateau.L_ANIM_LIST)[0])

    def test_the_layout_keeps_map_7_15s_tile_stream_and_chunk_table(self):
        lay = self.notes["layout"]
        for off in (plateau.L_TILE_STREAM, plateau.L_TILE_TABLE):
            self.assertEqual(struct.unpack_from("<I", self.rom, lay + off)[0],
                             struct.unpack_from("<I", self.before, plateau.SOURCE_LAYOUT + off)[0])

    def test_the_layout_drops_the_doors_and_the_props(self):
        lay = self.notes["layout"]
        for off in (plateau.L_PROP_COUNT, plateau.L_PROP_LIST,
                    plateau.L_WARP_COUNT, plateau.L_WARP_LIST):
            self.assertEqual(struct.unpack_from("<I", self.rom, lay + off)[0], 0)

    def test_the_ground_and_the_high_ground_are_five_by_five_blocks(self):
        for off in (plateau.L_BG2, plateau.L_BG3):
            rec = struct.unpack_from("<I", self.rom, self.notes["layout"] + off)[0] - ROM_BASE
            self.assertEqual((self.rom[rec + 0x14], self.rom[rec + 0x15]), plateau.GRID)
            self.assertEqual(struct.unpack_from("<I", self.rom, rec)[0], plateau.LAYER_CLASS)

    def test_bg0_and_bg1_point_every_block_at_one_blank_frame(self):
        for off, grid in ((plateau.L_BG0, plateau.SOURCE_GRIDS[0]),
                          (plateau.L_BG1, plateau.SOURCE_GRIDS[1])):
            rec = struct.unpack_from("<I", self.rom, self.notes["layout"] + off)[0] - ROM_BASE
            ptrs = {struct.unpack_from("<I", self.rom, rec + 0x18 + 4 * k)[0]
                    for k in range(grid[0] * grid[1])}
            self.assertEqual(ptrs, {self.notes["blank"] + ROM_BASE})

    # ----- the collision -----

    def test_collision_opens_the_arena_top_and_nothing_else(self):
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        self.assertEqual(len(bits), plateau.FRAME_SIZE)
        got = sum(1 for cy in range(plateau.MAP_TILES[1]) for cx in range(plateau.MAP_TILES[0])
                  if plateau.is_open(bits, cx, cy))
        self.assertEqual(got, self.notes["open_cells"])

    def test_no_walkable_cell_touches_the_map_border(self):
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        w, h = plateau.MAP_TILES
        edge = [(cx, cy) for cx in range(w) for cy in (0, h - 1) if plateau.is_open(bits, cx, cy)]
        edge += [(cx, cy) for cy in range(h) for cx in (0, w - 1) if plateau.is_open(bits, cx, cy)]
        self.assertEqual(edge, [])

    def test_every_fight_spot_envelope_is_open(self):
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        for spot in plateau.FIGHT_SPOTS:
            for cx, cy in plateau.envelope_cells(spot):
                self.assertTrue(plateau.is_open(bits, cx, cy), f"{spot} draws into ({cx},{cy})")

    def test_the_arena_gives_more_room_than_the_cell_games_arena(self):
        # Map 14,3 holds 4810 open cells in a 696 x 632 px box (22_arena_size.txt).
        self.assertGreater(self.notes["open_cells"], 4810)
        self.assertGreaterEqual(self.notes["open_box"][0], 696)
        self.assertGreaterEqual(self.notes["open_box"][1], 632)

    def test_every_closed_cell_he_can_stop_against_draws_something(self):
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        rules = plateau.learn(self.before)
        out = plateau.generate(rules)
        near = ((1, 0), (-1, 0), (0, 1), (0, -1))
        mute = [(cx, cy) for cy in range(plateau.MAP_TILES[1])
                for cx in range(plateau.MAP_TILES[0])
                if not plateau.is_open(bits, cx, cy) and (cx, cy) not in out["raised"]
                and any(plateau.is_open(bits, cx + dx, cy + dy) for dx, dy in near)]
        self.assertEqual(mute, [], "a closed cell faces open ground and draws nothing")

    # ----- the hand-off from the ending -----

    def test_record_a_now_loads_the_plateau(self):
        want = ext(39, 7, 100, 1, *plateau.TRUNKS_START)
        self.assertEqual(bytes(self.rom[self.notes["load_at"]:self.notes["load_at"] + len(want)]),
                         want)

    def test_the_load_is_a_one_byte_change(self):
        at = self.notes["load_at"]
        n = len(plateau.OLD_LOAD)
        diff = [i for i in range(n) if self.rom[at + i] != self.before[at + i]
                or self.rom[at + i] != plateau.NEW_LOAD[i]]
        self.assertEqual(bytes(self.rom[at:at + n]), plateau.NEW_LOAD)
        changed = [i for i in range(n) if plateau.OLD_LOAD[i] != plateau.NEW_LOAD[i]]
        self.assertEqual(changed, [plateau.LOAD_BYTE])
        self.assertEqual(diff, diff)

    # ----- the map table -----

    def test_the_table_grew_by_one_and_every_earlier_map_came_across(self):
        table, count = plateau.map_table(self.rom)
        self.assertEqual(table, self.notes["table"])
        self.assertEqual(count, self.notes["old_count"] + 1)
        old = bytes(self.rom[self.notes["old_table"]:
                             self.notes["old_table"] + MAP_SIZE * self.notes["old_count"]])
        self.assertEqual(bytes(self.rom[table:table + MAP_SIZE * self.notes["old_count"]]), old)

    def test_the_three_appended_maps_are_all_present(self):
        for zone, area in ((6, 100), (1, 100), (7, 100)):
            plateau.map_entry(self.rom, zone, area)

    def test_map_7_15_itself_is_untouched(self):
        _, at = plateau.map_entry(self.before, 7, 15)
        self.assertEqual(bytes(self.rom[at:at + MAP_SIZE]), bytes(self.before[at:at + MAP_SIZE]))
        for rec, grid in zip(plateau.SOURCE_LAYERS, plateau.SOURCE_GRIDS):
            n = 0x18 + 4 * grid[0] * grid[1]
            self.assertEqual(bytes(self.rom[rec:rec + n]), bytes(self.before[rec:rec + n]))
        n = plateau.LAYOUT_SIZE
        self.assertEqual(bytes(self.rom[plateau.SOURCE_LAYOUT:plateau.SOURCE_LAYOUT + n]),
                         bytes(self.before[plateau.SOURCE_LAYOUT:plateau.SOURCE_LAYOUT + n]))

    def test_the_only_base_rom_bytes_this_module_changes_are_the_named_hand_offs(self):
        spans = []
        for start, size, name in self.notes["sites"]:
            if start < len(self.before) and start < 0x800000:
                spans.append((start, size, name))
        changed = {i for start, size, _ in spans for i in range(start, start + size)
                   if self.rom[i] != self.before[i]}
        allowed = set()
        for lit in plateau.BASE_LITERALS:
            allowed |= set(range(lit, lit + 4))
        allowed |= set(range(plateau.ENTRY3_LITERAL, plateau.ENTRY3_LITERAL + 4))
        allowed.add(plateau.MAP_COUNT_BYTE)
        allowed.add(self.notes["load_at"] + plateau.LOAD_BYTE)
        self.assertTrue(changed <= allowed, f"unexpected base writes: {sorted(changed - allowed)}")

    def test_a_second_run_raises(self):
        rom = bytearray(self.rom)
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        alloc.notes.update({"battle_arena": {}, "ending_fight": {}, "plateau": {}})
        with self.assertRaises(ValueError):
            plateau.apply(rom, alloc)

    # ----- the source -----

    def test_the_grass_motif_slot_two_is_map_7_15s_animated_tile(self):
        self.assertIn(0x37E, plateau.GRASS_EVEN)
        self.assertEqual(plateau.GRASS_EVEN.index(0x37E), 2)
        tiles = plateau.source_tiles(self.before)
        self.assertGreaterEqual(0x37E & plateau.ENTRY_TILE, len(tiles),
                                "0x037E is only animated if it is past the static stream")

    def test_every_grass_entry_the_module_writes_is_map_7_15s_own(self):
        raised, tw, th = plateau.slot_reader(self.before, plateau.RAISED_SLOT)
        seen = {raised(tx, ty) for ty in range(th) for tx in range(tw)}
        for e in plateau.GRASS:
            self.assertIn(e, seen, f"entry 0x{e:04X} is not drawn anywhere on map 7,15")


if __name__ == "__main__":
    unittest.main()
