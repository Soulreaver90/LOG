r"""
test_scene_probe.py - Tests for the section 9 MAP READER in scene_probe.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_scene_probe.py -v
Why:  the battle arena shipped three times carrying doors nobody could see, because every tool read one
      of the two door carriers. Each test below pins the reader against a bible row, never against the
      reader's own output, so a decoder that drifts disagrees with the ROM fact and not with itself.
Source: docs\tasks\2026-11-07-map-reader\brief.md, bible section 9 (WRP, OPS, SAV, CSV, RAIN, AR7, TBF).
"""
import unittest

import log2_build
import log_paths
from scene import scene_probe as P
from scene.scene_probe import show_table

BASE_ROM = log2_build.BASE.read_bytes()
ARENA = (log_paths.BUILDS / "mockups" / "2026-11-05-ending-arena" / "log2_poc_r41_arena_v7.gba")

# bible tag OPS: map 6,1 +0x40 = 3, +0x44 = 0x085F2090, items rom:0x5F2048, 0x5F2060, 0x5F2078.
CC_LAYOUT, CC_DOOR_LIST = 0x5F209C, 0x5F2090
CC_DOORS = (0x5F2048, 0x5F2060, 0x5F2078)
# bible tag OPS: the front door leads to 6,2 var 1, rect (224,88)-(273,105), landing (144,276), dir 1.
CC_FRONT = {"at": 0x5F2078, "rect": (224, 88, 273, 105), "to": (6, 2, 1), "landing": (144, 276), "dir": 1}
# bible tag RAIN: map 6,1 enter script rom:0x3F9B0A, leave rom:0x3F9B1F; tag OPS: music a script.
CC_MUSIC, CC_ENTER, CC_LEAVE = 0x3F9AF0, 0x3F9B0A, 0x3F9B1F


class ChainTests(unittest.TestCase):
    """One walker for entry +0x2C, so two tools cannot read one build apart."""

    def test_layout_chain_of_capsule_corp(self):
        _, entry = P.map_entry(BASE_ROM, 6, 1)
        self.assertEqual(P.layouts(BASE_ROM, entry), [CC_LAYOUT])

    def test_every_map_resolves_a_layout(self):
        """Bible tag ARN: entry +0x2C is a pointer in all 327 entries."""
        table, count = P.map_table(BASE_ROM)
        resolved = sum(1 for k in range(count)
                       if P.layouts(BASE_ROM, table + P.MAP_SIZE * k)[:1] != [None])
        self.assertEqual((count, resolved), (327, 327))


class DoorCarrierTests(unittest.TestCase):
    """DOOR CARRIER B, the layout door list. It holds 586 of the game's 655 doors."""

    def test_capsule_corp_layout_door_list_matches_the_bible_row(self):
        doors = P.layout_doors(BASE_ROM, CC_LAYOUT)
        self.assertEqual(doors["count"], 3)
        self.assertEqual(doors["list"], CC_DOOR_LIST + 0x08000000)
        self.assertEqual(tuple(d["at"] for d in doors["doors"]), CC_DOORS)
        self.assertEqual([d["to"] for d in doors["doors"]], [(4, 6, 1), (6, 21, 1), (6, 2, 1)])

    def test_the_capsule_corp_front_door_decodes_field_by_field(self):
        front = [d for d in P.layout_doors(BASE_ROM, CC_LAYOUT)["doors"] if d["at"] == CC_FRONT["at"]][0]
        self.assertEqual(front["rect"], CC_FRONT["rect"])
        self.assertEqual(front["to"], CC_FRONT["to"])
        self.assertEqual(front["landing"], CC_FRONT["landing"])
        self.assertEqual(front["direction"], CC_FRONT["dir"])

    def test_the_cell_games_arena_pair_carry_no_layout_doors(self):
        """Bible tag WRP: maps 14,3 and 14,4 both carry +0x40 = 0 and +0x44 = 0."""
        for zone, area in ((14, 3), (14, 4)):
            _, entry = P.map_entry(BASE_ROM, zone, area)
            doors = P.layout_doors(BASE_ROM, P.layouts(BASE_ROM, entry)[0])
            self.assertEqual((doors["count"], doors["list"], doors["doors"]), (0, 0, []),
                             f"map {zone},{area}")

    def test_the_whole_population_reconciles_with_the_bible(self):
        """Bible tag WRP: 283 layouts carry a door list and 44 do not, and 283 + 44 = 327.
        Bible tag OPS: 655 doors in all, 586 in layout lists and 69 in region lists."""
        table, count = P.map_table(BASE_ROM)
        with_list = region = layout = 0
        for k in range(count):
            entry = table + P.MAP_SIZE * k
            lay = P.layouts(BASE_ROM, entry)[0]
            doors = P.layout_doors(BASE_ROM, lay)
            with_list += bool(doors["count"])
            layout += len(doors["doors"])
            region += sum(1 for _c, it in P.map_items(BASE_ROM, BASE_ROM[entry],
                                                      BASE_ROM[entry + 1])["regions"]
                          if it["kind"] == "warp")
        self.assertEqual((with_list, count - with_list), (283, 44))
        self.assertEqual((layout, region, layout + region), (586, 69, 655))


class LayoutFieldTests(unittest.TestCase):

    def test_props_are_32_bit_coordinates(self):
        """Bible tag EFX gives 24-byte prop entries. Read as s16 every second field is zero, and
        prop 2 would not land on the save point the SAV row puts at (408,568)-(457,617)."""
        props = P.layout_props(BASE_ROM, CC_LAYOUT)
        self.assertEqual(len(props), 5)
        save = props[2]
        self.assertEqual(save["rect"], (408, 556, 472, 620))
        x0, y0, x1, y1 = save["rect"]
        self.assertTrue(x0 <= 408 and y0 <= 568 and x1 >= 457 and y1 >= 617,
                        "the save point prop must cover the save region")

    def test_collision_frame_and_its_container_type(self):
        """Bible tag CSV: the frame is a 256x256 grid of 8 px cells, set = open."""
        info = P.collision(BASE_ROM, CC_LAYOUT)
        self.assertEqual(info["at"], 0x5F164C)
        self.assertEqual(info["type"], 1)
        self.assertEqual((info["bytes"], info["cells"]), (8192, 65536))
        self.assertEqual(info["bounds"], (512, 1024))
        self.assertEqual(info["cells_in_bounds"], (512 // 8) * (1024 // 8))

    def test_the_capsule_corp_doorway_is_open_ground(self):
        """Bible tag ARN4: the doorway at (224,88)-(273,105) is 21 open cells of 21. The warp
        fires first, which is why a sealed clone of this map needs its own collision."""
        _at, _kind, bits = P.collision_bits(BASE_ROM, CC_LAYOUT)
        cells = [(x, y) for y in range(88, 106, 8) for x in range(224, 274, 8)]
        self.assertTrue(all(P.is_open(bits, x, y) for x, y in cells))

    def test_map_bounds_come_from_the_block_grid_not_the_scroll_factor(self):
        """A layer's +4 and +8 are a scroll factor, 0x400 = 1.0 (bible tag BMS). Reading them as a
        size gave every map 1024x1024, which cut map 9,1's right edge region at x 1217-1264 off."""
        _, entry = P.map_entry(BASE_ROM, 9, 1)
        lay = P.layouts(BASE_ROM, entry)[0]
        self.assertEqual(P.map_bounds(BASE_ROM, lay), (1536, 1280))
        right = [it for _c, it in P.map_items(BASE_ROM, 9, 1)["regions"] if it["rect"][0] == 1217][0]
        self.assertLess(right["rect"][2], 1536, "the right edge region must fit inside the bounds")

    def test_the_overlay_layer_class_is_named_not_dropped(self):
        """Bible tag RAIN: map 6,1's BG0 is the overlay class 0x08004FCD, the ending's rain."""
        layers = P.layout_layers(BASE_ROM, CC_LAYOUT)
        self.assertEqual(layers[0]["class"], P.LAYER_OVERLAY)
        self.assertEqual(layers[0]["kind"], "overlay")
        self.assertEqual([lay["kind"] for lay in layers[1:]], ["tilemap"] * 3)


class EntryFieldTests(unittest.TestCase):

    def test_music_and_the_enter_and_leave_scripts_of_capsule_corp(self):
        _, entry = P.map_entry(BASE_ROM, 6, 1)
        self.assertEqual(P.u32(BASE_ROM, entry + 0x24), CC_MUSIC + 0x08000000)
        self.assertEqual(P.u32(BASE_ROM, entry + 0x30), CC_ENTER + 0x08000000)
        self.assertEqual(P.u32(BASE_ROM, entry + 0x34), CC_LEAVE + 0x08000000)

    def test_a_music_word_of_zero_is_song_0_and_not_silence(self):
        """Bible tag ARN3: there is no leave-the-music-alone value, so a clone left at 0 cuts."""
        self.assertIn("SONG 0", P._music(BASE_ROM, 0))
        self.assertIn("SCRIPT", P._music(BASE_ROM, CC_MUSIC + 0x08000000))
        self.assertIn("song id 38", P._music(BASE_ROM, 38))

    def test_the_banner_field_is_a_script_in_14_maps(self):
        """Measured 2026-11-07 over all 327 entries. Bible tag LAB read map 9,1's banner as index
        64 and called it a puzzle: the word is a POINTER, so its low byte was never an index."""
        table, count = P.map_table(BASE_ROM)
        pointers = [k for k in range(count)
                    if P.is_pointer(P.u32(BASE_ROM, table + P.MAP_SIZE * k + 0x0C))]
        self.assertEqual((count, len(pointers)), (327, 14))
        index, _at = P.map_entry(BASE_ROM, 9, 1)
        self.assertIn(index, pointers)


class ItemTests(unittest.TestCase):

    def test_the_ending_actors_on_map_6_1_decode_as_npcs(self):
        """Bible tag TBF: item 5 is set 133 at (248,624) and item 6 is set 28 at (288,392)."""
        items = P.map_items(BASE_ROM, 6, 1)["items"]
        self.assertEqual((items[5]["kind"], items[5]["set_id"], items[5]["at_xy"]), ("npc", 133, (248, 624)))
        self.assertEqual((items[6]["kind"], items[6]["set_id"], items[6]["at_xy"]), ("npc", 28, (288, 392)))

    def test_the_vanilla_imperfect_cell_item_keeps_its_group_kind(self):
        """Bible tag EF1: rom:0x4058A4 is enemy type 60, set 28, at (264,128)."""
        it = P.item(BASE_ROM, 0x4058A4)
        self.assertEqual(it["kind"], "group")
        self.assertEqual((it["enemy_type"], it["set_id"], it["at_xy"]), (60, 28, (264, 128)))


class ShowMapTests(unittest.TestCase):
    """The listing itself. A reader that prints one carrier is the bug this tool exists to end."""

    def test_both_carriers_are_printed_and_labelled(self):
        text = "\n".join(P.show_map(BASE_ROM, 6, 1))
        self.assertIn("DOOR CARRIER A, the REGION list", text)
        self.assertIn("DOOR CARRIER B, the LAYOUT door list", text)
        self.assertIn("DOORS IN ALL: 5  (2 region, 3 layout, 0 item)", text)

    def test_no_region_is_called_a_door_unless_its_factory_says_so(self):
        """The old listing printed `region cond ... warp rect ...` for every region box."""
        text = "\n".join(P.show_map(BASE_ROM, 9, 1))
        self.assertIn("4 region(s), 0 of them door(s)", text)
        self.assertNotIn("DOOR    rect", text)

    def test_the_listing_names_the_entry_fields_rather_than_raw_words(self):
        text = "\n".join(P.show_map(BASE_ROM, 6, 1))
        for name in ("region list", "item list", "music", "enter script", "leave script",
                     "layout array", "banner", "combat"):
            self.assertIn(name, text)

    def test_the_reader_opens_every_map_and_every_variation(self):
        """The design says any of the 327 maps. Three worked examples do not prove 327, and the maps
        most likely to break a reader are the odd ones: 1,7 and 6,99 carry no scroll-1.0 layer, and 12
        carry an all-open collision frame. Every listing must also hold BOTH carrier headers."""
        table, count = P.map_table(BASE_ROM)
        opened = variations = 0
        for k in range(count):
            at = table + P.MAP_SIZE * k
            zone, area = BASE_ROM[at], BASE_ROM[at + 1]
            for var in range(1, max(BASE_ROM[at + 0x02], 1) + 1):
                variations += 1
                text = "\n".join(P.show_map(BASE_ROM, zone, area, var))
                self.assertIn("DOOR CARRIER A, the REGION list", text, f"map {zone},{area} var {var}")
                self.assertIn("DOOR CARRIER B", text, f"map {zone},{area} var {var}")
                self.assertIn("DOORS IN ALL:", text, f"map {zone},{area} var {var}")
            opened += 1
        self.assertEqual((opened, variations), (327, 336))

    def test_a_map_with_no_scroll_one_layer_says_so_rather_than_printing_zero(self):
        """Maps 1,7 and 6,99 have no scroll-1.0 BG layer, so there is no world extent to count inside.
        Printing "0 of 0 open inside the map bounds 0x0 px" would read as a sealed map."""
        for zone, area in ((1, 7), (6, 99)):
            text = "\n".join(P.show_map(BASE_ROM, zone, area))
            self.assertIn("no scroll-1.0 BG layer", text, f"map {zone},{area}")
            self.assertNotIn("bounds 0x0 px", text, f"map {zone},{area}")


@unittest.skipUnless(ARENA.is_file(), "the arena v7 trial ROM is not in builds\\mockups")
class ArenaTests(unittest.TestCase):
    """Map 6,100 is the map that caused this tool. Bible tag AR7 is what it must read back."""

    @classmethod
    def setUpClass(cls):
        cls.rom = ARENA.read_bytes()

    def test_the_reader_resolves_the_builds_own_map_table(self):
        """The arena moves the table into the expansion area and appends entry 327. A reader that
        hardcoded 0x409368 and 327 would read the dead copy and never see map 6,100."""
        table, count = P.map_table(self.rom)
        self.assertEqual(count, 328)
        self.assertNotEqual(table, P.MAP_TABLE)
        index, _at = P.map_entry(self.rom, 6, 100)
        self.assertEqual(index, 327)

    def test_the_arena_shows_zero_doors_in_both_carriers(self):
        _, entry = P.map_entry(self.rom, 6, 100)
        self.assertEqual(self.rom[entry + 0x03], 0)
        self.assertEqual(P.u32(self.rom, entry + 0x10), 0)
        self.assertEqual(P.map_items(self.rom, 6, 100)["regions"], [])
        doors = P.layout_doors(self.rom, P.layouts(self.rom, entry)[0])
        self.assertEqual((doors["count"], doors["list"], doors["doors"]), (0, 0, []))

    def test_the_arena_names_song_38_so_the_track_is_not_cut(self):
        """Bible tag ARN3: song 38 is playing when the ending loads the arena."""
        _, entry = P.map_entry(self.rom, 6, 100)
        self.assertEqual(P.u32(self.rom, entry + 0x24), 38)

    def test_the_arena_has_its_own_props_and_collision(self):
        """Bible tag AR7: three props of map 6,1's five, and its own collision frame."""
        _, entry = P.map_entry(self.rom, 6, 100)
        lay = P.layouts(self.rom, entry)[0]
        self.assertEqual(len(P.layout_props(self.rom, lay)), 3)
        self.assertNotEqual(P.collision(self.rom, lay)["at"], 0x5F164C)

    def test_the_listing_says_zero_doors_in_all(self):
        text = "\n".join(P.show_map(self.rom, 6, 100))
        self.assertIn("DOORS IN ALL: 0  (0 region, 0 layout, 0 item)", text)

    def test_the_reader_opens_every_map_of_the_build_including_the_appended_one(self):
        """A build is the only ROM that can show a reader reading an appended map, or reading short."""
        table, count = P.map_table(self.rom)
        for k in range(count):
            at = table + P.MAP_SIZE * k
            text = "\n".join(P.show_map(self.rom, self.rom[at], self.rom[at + 1]))
            self.assertIn("DOOR CARRIER B", text, f"entry {k}")
        self.assertEqual(count, 328)

    def test_no_script_on_the_arena_loads_another_map(self):
        """A door count is a floor: a script ext 35, 38 or 39 is a way out that no carrier shows. The
        arena's variation, enter and leave words are 0, and its one script is the enemy death table."""
        _, entry = P.map_entry(self.rom, 6, 100)
        for off in (0x28, 0x30, 0x34):
            self.assertEqual(P.u32(self.rom, entry + off), 0, f"entry +0x{off:02X}")
        death = [it["table"] for it in P.map_items(self.rom, 6, 100)["items"] if "table" in it]
        self.assertEqual(death, [0x940744])
        listing = "\n".join(show_table(self.rom, death[0]))
        for op in ("ext35(", "ext38(", "ext39("):
            self.assertNotIn(op, listing)


if __name__ == "__main__":
    unittest.main()
