r"""
test_plateau.py - The plateau trial: map 7,100, the map the OWNER composed in the map editor.

The module is built once for the whole class, on top of the trial chain it needs, and every test
reads the RESULT. A test that only re-ran the module's own arithmetic would prove nothing.

The strongest test here is test_the_rom_gives_his_document_back: map_file.read_map on the built ROM
has to equal art\plateau\map_142.json field for field. That one proves the patch lays HIS map, and
it is why no test in this file describes a tile, a lip or a rock formation any more.
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import log2_build  # noqa: E402
from patches import plateau  # noqa: E402

import map_file  # noqa: E402
import tile_stream  # noqa: E402
from scene import map_view  # noqa: E402
from scene import scene_probe  # noqa: E402
import scene.scene_lib as S  # noqa: E402
from scene.scene_lib import ext  # noqa: E402

ROM_BASE = 0x08000000
MAP_SIZE = 56


def _ops(rom, at):
    """[(ext number, pushed arguments)] of a type 0 record, which is how these records are written.

    Every op of a record this module writes is a push or an ext op, so the stack before each ext op
    is exactly that op's own arguments. A record with a branch would need the evaluator
    test_future_androids carries; none here has one."""
    out, stack = [], []
    for op in S.ops(rom, at + 3, S.record_end(rom, at)):
        if op.ext is not None:
            out.append((op.ext, tuple(stack)))
            stack = []
        elif op.op in (0, 1, 29):
            stack += list(op.args)
        elif op.op == 17:
            break
        else:
            raise AssertionError(f"rom:0x{at:X} carries base op {op.op}, which _ops cannot read")
    return out


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

    def test_the_entry_carries_combat_the_blank_banner_the_music_and_its_own_items(self):
        at = self.notes["entry"]
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x08)[0], 1, "combat")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x0C)[0], 0xDD, "banner")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x24)[0], 38, "music")
        self.assertEqual(self.rom[at + 4], 2, "item count")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x14)[0] - ROM_BASE,
                         self.notes["items"])

    def test_the_entry_is_the_live_arena_entry_with_three_words_changed(self):
        """The zone, the ITEM LIST and the layout array. The item list may not be shared: an item
        carries its own death event, and the two rounds have to end differently."""
        at = self.notes["entry"]
        _, arena_at = plateau.map_entry(self.rom, 6, 100)
        ours = bytearray(self.rom[at:at + MAP_SIZE])
        theirs = bytearray(self.rom[arena_at:arena_at + MAP_SIZE])
        self.assertNotEqual(ours[0x14:0x18], theirs[0x14:0x18], "the item list must be its own")
        ours[0] = theirs[0]
        ours[0x14:0x18] = theirs[0x14:0x18]
        ours[0x2C:0x30] = theirs[0x2C:0x30]
        self.assertEqual(bytes(ours), bytes(theirs))

    # ----- the layout -----

    def test_the_layout_writes_the_camera_pair_his_world_asks_for(self):
        """The pair is `world - 239` and `world - 159`, COMPUTED from his 864 x 816 px world, never
        taken from his 1280 x 1024 px block grid. A grid pair is the fault that once stopped the
        camera 170 px short of walkable ground."""
        doc = plateau.document()
        got = struct.unpack_from("<HH", self.rom, self.notes["layout"] + plateau.L_CLAMP)
        self.assertEqual(got, map_file.camera_pair(*doc["world"]))
        self.assertEqual(got, self.notes["clamp"])
        grid = (doc["blocks"][0] * 256, doc["blocks"][1] * 256)
        self.assertNotEqual(got, map_file.camera_pair(*grid),
                            "the block grid is not the world, and only the world sets the camera")

    def test_the_layout_carries_his_own_animated_tile_groups(self):
        doc = plateau.document()
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_ANIM_COUNT)[0],
                         len(doc["animated"]))
        groups = scene_probe.layout_groups(self.rom, lay)
        self.assertEqual([g["first"] for g in groups], [g["first"] for g in doc["animated"]])
        for got, want in zip(groups, doc["animated"]):
            self.assertEqual([f["duration"] for f in got["frames"]],
                             [f["duration"] for f in want["frames"]])
            self.assertEqual([bytes(f["pixels"]) for f in got["frames"]],
                             [bytes(f["pixels"]) for f in want["frames"]])

    def test_the_layout_names_his_chunk_table_and_writes_his_own_tile_stream(self):
        """The chunk table is the one HIS document names, so every (chunk, tile) pair means the art
        he drew with. The +0x48 stream is this map's own, written from his pairs in his order."""
        doc = plateau.document()
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_TILE_TABLE)[0],
                         doc["chunk_table"])
        self.assertEqual([list(p) for p in tile_stream.decode_stream(self.rom, lay + ROM_BASE)],
                         [list(p) for p in doc["tiles"]])

    def test_the_layout_drops_the_doors_and_the_props(self):
        lay = self.notes["layout"]
        for off in (plateau.L_PROP_COUNT, plateau.L_PROP_LIST,
                    plateau.L_WARP_COUNT, plateau.L_WARP_LIST):
            self.assertEqual(struct.unpack_from("<I", self.rom, lay + off)[0], 0)

    def test_all_four_layers_carry_his_own_block_grid(self):
        doc = plateau.document()
        for off in (plateau.L_BG0, plateau.L_BG1, plateau.L_BG2, plateau.L_BG3):
            rec = struct.unpack_from("<I", self.rom, self.notes["layout"] + off)[0] - ROM_BASE
            self.assertEqual([self.rom[rec + plateau.LAYER_GRID],
                              self.rom[rec + plateau.LAYER_GRID + 1]], doc["blocks"])
            self.assertEqual(struct.unpack_from("<I", self.rom, rec)[0], plateau.LAYER_CLASS)

    def test_his_layer_priorities_are_written_exactly_as_he_set_them(self):
        """BG0 and BG1 are priority 1 on his map, so what they draw stands IN FRONT of the player,
        and BG2 and BG3 are priority 3 and draw behind him. All four are kept: it is his map."""
        doc = plateau.document()
        lay = self.notes["layout"]
        for bg, name in enumerate(map_file.LAYER_NAMES):
            self.assertEqual(self.rom[lay + map_file.L_PRIORITY + bg],
                             doc["layers"][name]["priority"], name)
        self.assertEqual(self.notes["priorities"], {"bg0": 1, "bg1": 1, "bg2": 3, "bg3": 3})

    # ----- the collision -----

    def test_the_collision_frame_is_his_own_cell_for_cell(self):
        doc = plateau.document()
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        self.assertEqual(len(bits), plateau.FRAME_SIZE)
        self.assertEqual(bits, bytes(doc["collision"]))
        self.assertEqual(len(plateau.open_cells(doc)), self.notes["open_cells"])

    def test_the_terrain_frame_is_his_own_too(self):
        terrain = plateau._frame(self.rom, self.notes["terrain"] + ROM_BASE)
        self.assertEqual(terrain, bytes(plateau.document()["terrain"]))

    def test_no_walkable_cell_touches_the_world_edge(self):
        """The camera stops at the world edge, so walkable ground there would show him the void."""
        doc = plateau.document()
        world = doc["world"]
        edge = [c for c in plateau.open_cells(doc)
                if c[0] == 0 or c[1] == 0
                or (c[0] + 1) * 8 >= world[0] or (c[1] + 1) * 8 >= world[1]]
        self.assertEqual(edge, [])

    def test_both_round_two_spots_stand_on_reachable_open_ground(self):
        """His map seals one pocket inside the rock ring on purpose, so the rule is that the pair
        shares ONE walkable region, not that every open cell is reachable."""
        doc = plateau.document()
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        opened = plateau.open_cells(doc)
        reach = plateau.reachable(opened, (plateau.CELL_SPOT[0] // 8, plateau.CELL_SPOT[1] // 8))
        self.assertEqual(len(reach), self.notes["reachable"])
        self.assertEqual(len(opened) - len(reach), self.notes["pocket_cells"])
        for spot, env, who in plateau.PLATEAU_SPOTS:
            for cx, cy in plateau.envelope_cells(spot, env):
                self.assertTrue(plateau.is_open(bits, cx, cy),
                                f"{who} at {spot} draws into the closed cell ({cx},{cy})")
                self.assertIn((cx, cy), reach, f"{who} at {spot} is sealed off at ({cx},{cy})")

    def test_his_arena_gives_more_room_than_the_cell_games_arena(self):
        # Map 14,3 holds 4810 open cells in a 696 x 632 px box (22_arena_size.txt).
        x0, y0, x1, y1 = self.notes["open_box"]
        self.assertGreater(self.notes["open_cells"], 4810)
        self.assertGreaterEqual(x1 - x0 + 1, 696)
        self.assertGreaterEqual(y1 - y0 + 1, 632)

    # ----- the round split (rung 5) -----

    def test_record_a_still_loads_the_arena(self):
        """Rung 5 moved the plateau off ending word 13. The talk and round 1 stay on map 6,100, which
        the owner play tested: "we already built that whole thing"."""
        self.assertEqual(self.rom.count(plateau.ARENA_LOAD), self.before.count(plateau.ARENA_LOAD),
                         "no copy of the arena load was rewritten")
        self.assertEqual(self.rom.count(ext(39, 7, 100, 1, *plateau.TRUNKS_START)), 0,
                         "nothing loads the plateau at the old spot any more")

    def test_every_word_that_named_record_f_now_names_round_1(self):
        """Three words name it, not one: future_androids gives each android enemy a COPY of the live
        ending table, and after a real fight the scene runs out of THAT copy's word 23."""
        want = struct.pack("<I", self.notes["round1"] + ROM_BASE)
        self.assertGreaterEqual(len(self.notes["fight_words"]), 1)
        for word in self.notes["fight_words"]:
            self.assertEqual(bytes(self.rom[word:word + 4]), want, hex(word))

    def test_round_1_is_the_standard_battle_start_with_the_top_half_of_the_bar(self):
        self.assertEqual(_ops(self.rom, self.notes["round1"]),
                         [(104, (28, 1)), (90, (28, 50, 100)), (86, (1,)), (33, (0,))])

    def test_the_split_is_round_1s_death_and_arms_round_2_on_the_plateau(self):
        """The owner's beat: ping, white flash, Cell punched off screen, Trunks flies after him, then
        the plateau loads and the SAME bar shows its bottom half."""
        self.assertEqual(struct.unpack_from("<I", self.rom, self.notes["arena_table"])[0],
                         self.notes["split"] + ROM_BASE, "table D word 0 is the split")
        ops = _ops(self.rom, self.notes["split"])
        names = [n for n, _ in ops]
        self.assertEqual(ops[:4], [(88, ()), (86, (0,)), (46, (60,)), (42, (10,))])
        self.assertEqual(ops[-4:], [(104, (28, 1)), (90, (28, 0, 50)), (86, (1,)), (33, (0,))])
        self.assertIn((39, (7, 100, 1) + plateau.TRUNKS_SPOT), ops)
        self.assertIn((136, (28,) + plateau.PUNCHED_TO + (plateau.KNOCK_N,)), ops)
        self.assertIn((121, (0, plateau.FLY_STATE)), ops)
        self.assertIn((136, (0,) + plateau.FLIES_TO + (plateau.FLY_N,)), ops)
        self.assertLess(names.index(40), names.index(39), "the load runs under a fade")
        self.assertLess(names.index(39), names.index(41), "and the screen comes back after it")

    def test_trunks_walks_to_cell_before_the_punch(self):
        """The owner, 2026-11-08: "trunks should walk to cell and punch him, not punch him a mile
        away". The staging drops him 64 px below Cell; the walk closes that to 24 px, which is
        celljr_fight's own melee gap. `ext 53` BLOCKS, so the punch cannot start early."""
        ops = _ops(self.rom, self.notes["split"])
        names = [n for n, _ in ops]
        self.assertIn((53, (0,) + plateau.PUNCH_FROM), ops, "the player walks in")
        walk = ops.index((53, (0,) + plateau.PUNCH_FROM))
        self.assertEqual(ops[walk + 1], (55, (0, plateau.UP)), "and is held facing Cell")
        self.assertLess(names.index(43), walk, "the walk is seen, so it runs after the white flash")
        self.assertLess(walk, names.index(63), "and it finishes before the punch group opens")
        self.assertEqual(plateau.PUNCH_FROM[0], plateau.TRUNKS_SPOT[0], "a straight walk north")
        self.assertEqual(plateau.PUNCH_FROM[1] - plateau.CELL_SPOT[1], 24, "celljr's own melee gap")
        self.assertLess(plateau.CELL_SPOT[1], plateau.PUNCH_FROM[1], "he stays south of Cell")
        self.assertLess(plateau.PUNCH_FROM[1], plateau.TRUNKS_SPOT[1], "and closer than the staging")

    def test_the_punch_spot_is_open_ground_on_the_arena_and_inside_the_parked_view(self):
        """The punch happens on map 6,100, not on the plateau, so the ground under the walk is the
        ARENA's own collision frame. His whole 32 px frame also has to stay inside SPLIT_VIEW."""
        _, arena = plateau.map_entry(self.rom, 6, 100)
        layout = struct.unpack_from("<I", self.rom,
                                    struct.unpack_from("<I", self.rom, arena + plateau.F_LAYOUTS)[0]
                                    - ROM_BASE)[0] - ROM_BASE
        bits = plateau._frame(self.rom, struct.unpack_from("<I", self.rom,
                                                           layout + plateau.L_COLLISION)[0])
        for y in range(plateau.PUNCH_FROM[1], plateau.TRUNKS_SPOT[1] + 1, 8):
            for cx, cy in plateau.envelope_cells((plateau.TRUNKS_SPOT[0], y), plateau.TRUNKS_ENVELOPE):
                self.assertTrue(plateau.is_open(bits, cx, cy), f"arena cell ({cx},{cy}) at y {y}")
        top = plateau.PUNCH_FROM[1] - plateau.TRUNKS_UP
        bottom = plateau.PUNCH_FROM[1] + plateau.TRUNKS_DOWN
        self.assertGreaterEqual(top, plateau.SPLIT_VIEW[1])
        self.assertLessEqual(bottom, plateau.SPLIT_VIEW[1] + plateau.VIEW[1])

    def test_the_two_halves_are_a_true_half_each_and_meet_at_50(self):
        """ext 85 bar_show calls the SAME builder with (0, 100), so lo = 0 is the engine's own full
        bar value and an even split is as legal as vanilla's uneven slices."""
        lo1, hi1 = plateau.ROUND1_BAR
        lo2, hi2 = plateau.ROUND2_BAR
        self.assertEqual((hi1 - lo1, hi2 - lo2), (50, 50))
        self.assertEqual(hi2, lo1, "the two halves meet")
        self.assertEqual((lo2, hi1), (0, 100), "and together they are the whole bar")

    def test_round_2_has_its_own_actors_and_its_own_death_event(self):
        """Sharing battle_arena's item list would share the enemy ITEM, and an item carries its death
        table at +0x14, so Cell's death on the plateau would split the fight again for ever."""
        _, arena = plateau.map_entry(self.rom, 6, 100)
        self.assertNotEqual(struct.unpack_from("<I", self.rom, self.notes["entry"] + 0x14),
                            struct.unpack_from("<I", self.rom, arena + 0x14))
        enemy = struct.unpack_from("<I", self.rom, self.notes["items"] + 4)[0] - ROM_BASE
        self.assertEqual(enemy, self.notes["item"])
        event = struct.unpack_from("<I", self.rom, enemy + 0x14)[0] - ROM_BASE
        self.assertEqual(event, self.notes["event"])
        self.assertEqual(struct.unpack_from("<I", self.rom, event)[0], plateau.EVENT_RUNNER)
        table = struct.unpack_from("<I", self.rom, event + 4)[0] - ROM_BASE
        self.assertEqual(table, self.notes["death_table"])
        self.assertNotEqual(table, self.notes["arena_table"])

    def test_round_2s_death_runs_the_collapse_the_blast_and_the_vanilla_tail(self):
        """Table D2 word 0 is ending_fight's own record K, unchanged, and words 24 and 25 still name
        the vanilla end text and the vanilla exit."""
        d2, d1 = self.notes["death_table"], self.notes["arena_table"]
        self.assertEqual(struct.unpack_from("<I", self.rom, d2)[0],
                         struct.unpack_from("<I", self.before, d1)[0], "word 0 is still record K")
        for w in (24, 25):
            self.assertEqual(struct.unpack_from("<I", self.rom, d2 + 4 * w)[0],
                             struct.unpack_from("<I", self.before, d1 + 4 * w)[0], f"word {w}")

    def test_the_npc_cell_the_plateau_builds_stands_on_the_fight_spot(self):
        npc = struct.unpack_from("<I", self.rom, self.notes["items"])[0] - ROM_BASE
        self.assertEqual(struct.unpack_from("<I", self.rom, npc + 4)[0], 0, "condition 0: built at load")
        self.assertEqual(struct.unpack_from("<hh", self.rom, npc + 8), plateau.CELL_SPOT)
        self.assertEqual(struct.unpack_from("<I", self.rom, npc + 0xC)[0], plateau.CELL_SET)

    def test_both_parked_views_hold_both_fighters_whole(self):
        """Bible B0246: set 28 reaches 56 px above his own point and the Trunks sets 24. A view is
        240 x 160 from its TOP LEFT, so the pair has to fit inside it or a frame is cut."""
        for view in (plateau.SPLIT_VIEW, plateau.ARRIVE_VIEW):
            for spot, up, down in ((plateau.CELL_SPOT, plateau.ENVELOPE[2], plateau.ENVELOPE[3]),
                                   (plateau.TRUNKS_SPOT, plateau.TRUNKS_UP, plateau.TRUNKS_DOWN)):
                self.assertGreaterEqual(spot[1] - up, view[1], f"{spot} head above {view}")
                self.assertLessEqual(spot[1] + down, view[1] + plateau.VIEW[1], f"{spot} feet below")
        self.assertLess(plateau.PUNCHED_TO[1] + plateau.ENVELOPE[3], plateau.SPLIT_VIEW[1])
        self.assertLess(plateau.FLIES_TO[1] + plateau.TRUNKS_DOWN, plateau.SPLIT_VIEW[1])

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
        for word in self.notes["fight_words"]:
            allowed |= set(range(word, word + 4))
        self.assertTrue(changed <= allowed, f"unexpected base writes: {sorted(changed - allowed)}")

    def test_a_second_run_raises(self):
        rom = bytearray(self.rom)
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        alloc.notes.update({"battle_arena": {}, "ending_fight": {}, "plateau": {}})
        with self.assertRaises(ValueError):
            plateau.apply(rom, alloc)

    # ----- his document, read back out of the ROM -----

    def test_the_rom_gives_his_document_back(self):
        """THE test of this module. map_file.read_map on the built ROM has to equal the repo copy of
        his map, field for field, or the patch did not lay the map he composed.

        `stamps` and `dropped` are editor notes and never reach the ROM, so they are not compared."""
        doc = plateau.document()
        back = map_file.read_map(self.rom, plateau.PLATEAU_ZONE, plateau.PLATEAU_AREA)
        self.assertEqual(map_file.validate(back), [], "the map read back is not even sound")
        for field in ("world", "blocks", "chunk_table", "blend", "unread", "collision", "terrain"):
            self.assertEqual(back[field], doc[field], field)
        self.assertEqual([list(p) for p in back["tiles"]], [list(p) for p in doc["tiles"]])
        self.assertEqual(sorted(back["layers"]), sorted(doc["layers"]))
        for name, layer in doc["layers"].items():
            for field in ("priority", "scroll", "offset", "cells"):
                self.assertEqual(back["layers"][name][field], layer[field], f"{name} {field}")
        self.assertEqual(len(back["animated"]), len(doc["animated"]))
        for got, want in zip(back["animated"], doc["animated"]):
            self.assertEqual(got, want)

    def test_no_over_layer_was_blanked_and_bg1_really_stands_over_him(self):
        """BG0 and BG1 are priority 1, so what they draw is IN FRONT of the player. This measures
        the result out of the ROM, not out of the plan.

        A cell draws only when its TILE holds a non-zero pixel: a non-null cell can name a blank
        slot, so a null test would report that every layer draws everywhere. Each layer is shifted
        by its own scroll offset first (layer pixel = world pixel + 64 n, bible B1082), or every
        count would be 64 px out. Measured 2026-11-08: BG0 draws NO cell anywhere, so nothing was
        blanked away from it either, and BG1 stands over 477 cells of walkable ground, which is
        where he walks behind scenery."""
        lay = self.notes["layout"]
        draws = {n: any(px) for n, px in enumerate(scene_probe.static_tiles(self.rom, lay))}
        for group in scene_probe.layout_groups(self.rom, lay):
            for n in range(group["tiles"]):
                draws[group["first"] + n] = any(any(f["pixels"][64 * n:64 * n + 64])
                                                for f in group["frames"])
        doc = plateau.document()
        reach = plateau.reachable(plateau.open_cells(doc),
                                  (plateau.CELL_SPOT[0] // 8, plateau.CELL_SPOT[1] // 8))
        across = doc["blocks"][0] * plateau.BLOCK_TILES
        drawn = {}
        for name in ("bg0", "bg1"):
            layer = doc["layers"][name]
            sx, sy = map_view.layer_shift(tuple(layer["offset"]))
            drawn[name] = {(n % across - sx // 8, n // across - sy // 8)
                           for n, cell in enumerate(layer["cells"])
                           if draws.get(cell & map_file.TILE_INDEX, False)}
        self.assertEqual({name: len(cells & reach) for name, cells in drawn.items()},
                         {"bg0": 0, "bg1": 477})
        for spot, env, who in plateau.PLATEAU_SPOTS:
            box = set(plateau.envelope_cells(spot, env))
            for name, cells in drawn.items():
                self.assertEqual(box & cells, set(), f"{name} would hide {who} at {spot}")


if __name__ == "__main__":
    unittest.main()
