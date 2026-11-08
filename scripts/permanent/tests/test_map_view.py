r"""
test_map_view.py - Tests for the map renderer, which draws BOTH door carriers and the layout props.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_map_view.py -v
Why:  the picture is how the owner checks a map by eye, and it carried three defects. It called every
      region box a warp, it drew no layout door and no prop at all, and it took the layer scroll factor
      for a size, so every map was cut or padded to 1024x1024.
Needs: Pillow (py -3.14 has it; py -3 does not).
Source: docs\tasks\2026-11-07-map-reader\brief.md, bible section 9 (OPS, WRP, EFX, PGS).
"""
import struct
import unittest

import log2_build
from rom.webfoot_decompress import decompress
from scene import map_view
from scene import scene_probe as P

BASE_ROM = log2_build.BASE.read_bytes()
# Bible tag PGS: map 9,1's right edge script region is (1217,385)-(1264,424). A 1024 px crop cut it.
LOOKOUT_RIGHT_EDGE = (1217, 385, 1264, 424)


class BoundsTests(unittest.TestCase):
    """A layer record's +4 and +8 are a SCROLL FACTOR, 0x400 = 1.0, not a width and height."""

    def test_capsule_corp_renders_at_its_real_size(self):
        """Map 6,1's ground layer is 2 x 4 blocks = 512x1024. The scroll factor said 1024x1024, which
        padded the picture with 512 px of black the map does not have."""
        img, _lines = map_view.render(BASE_ROM, 6, 1, show_collision=False)
        self.assertEqual(img.size, (512, 1024))

    def test_the_lookout_is_not_cut_at_1024_px(self):
        """Map 9,1 is 1536x1280. At 1024 its right edge region fell outside the picture entirely."""
        img, lines = map_view.render(BASE_ROM, 9, 1, show_collision=False)
        self.assertEqual(img.size, (1536, 1280))
        self.assertLess(LOOKOUT_RIGHT_EDGE[2], img.size[0])
        self.assertIn("map 1536x1280", lines[0])

    def test_the_report_calls_the_scroll_words_a_scroll_factor(self):
        _img, lines = map_view.render(BASE_ROM, 6, 1, show_collision=False)
        self.assertTrue(any("scroll 0x400/0x400" in ln for ln in lines))
        self.assertFalse(any("bg2: 1024x1024" in ln for ln in lines))


class CarrierTests(unittest.TestCase):
    """Both door carriers are drawn, each labelled, so the two can never be confused again."""

    def setUp(self):
        self.img, self.lines = map_view.render(BASE_ROM, 6, 1, show_collision=False)
        self.text = "\n".join(self.lines)

    def test_the_layout_door_list_is_drawn_and_reported(self):
        """Bible tag OPS: map 6,1 carries 3 layout doors. No render ever showed one."""
        self.assertIn("LAYOUT door list (layout +0x40/+0x44): 3 door(s) of a declared 3", self.text)
        self.assertIn("-> map 6,2 var 1 at (144, 276)", self.text)

    def test_the_region_list_is_reported_as_regions_not_as_warps(self):
        self.assertIn("REGION list (entry +0x10): 6 region(s), 2 of them door(s)", self.text)
        self.assertNotIn("item rect (408, 568, 457, 617) ->", self.text)

    def test_the_props_are_drawn_and_reported(self):
        """Bible tag EFX: map 6,1 has 5 props, which the old tool drew none of."""
        self.assertIn("layout props (layout +0x24/+0x28): 5", self.text)
        self.assertIn("rect (408, 556, 472, 620)", self.text)

    def test_a_layout_door_box_is_painted_in_its_own_colour(self):
        """The front door rect (224,88)-(273,105) must carry the blue outline, not the region cyan."""
        x0, y0, x1, _y1 = 224, 88, 273, 105
        edge = [self.img.getpixel((x, y0)) for x in range(x0, x1 + 1)]
        self.assertIn(map_view.LAYOUT_DOOR_BOX, edge)
        self.assertNotIn(map_view.REGION_DOOR_BOX, edge)

    def test_a_prop_box_is_painted_in_its_own_colour(self):
        row = [self.img.getpixel((x, 556)) for x in range(408, 473)]
        self.assertIn(map_view.PROP_BOX, row)


class ReuseTests(unittest.TestCase):
    """One decoder. A second copy is how two tools come to read one build apart."""

    def test_the_collision_model_is_scene_probes_own(self):
        self.assertIs(map_view.is_open, P.is_open)

    def test_the_layout_walker_is_scene_probes_own(self):
        _, entry = P.map_entry(BASE_ROM, 6, 1)
        self.assertEqual(map_view.layout_of(BASE_ROM, entry, 1),
                         P.layouts(BASE_ROM, entry)[0] + 0x08000000)

    def test_an_absent_variation_raises_rather_than_reading_a_stray_word(self):
        _, entry = P.map_entry(BASE_ROM, 6, 1)
        with self.assertRaises(ValueError):
            map_view.layout_of(BASE_ROM, entry, 9)


class CollisionTests(unittest.TestCase):

    def test_the_closed_count_is_measured_inside_the_map_bounds(self):
        """At 1024x1024 the tint counted 16384 cells for a map that holds 8192."""
        _img, lines = map_view.render(BASE_ROM, 6, 1)
        self.assertTrue(any("of 8192 (red tint)" in ln for ln in lines), lines)
        info = P.collision(BASE_ROM, P.layouts(BASE_ROM, P.map_entry(BASE_ROM, 6, 1)[1])[0])
        closed = info["cells_in_bounds"] - info["open_in_bounds"]
        self.assertTrue(any(f"collision: {closed} closed cells of 8192" in ln for ln in lines), lines)


class LayerOffsetTests(unittest.TestCase):
    """A BG layer record's +0x0C and +0x10 move its art, and every render ignored them.

    `sub_080055A4` is the layer object's update. It loads rec +0x0C at `0x080055B2`, adds it to the
    scroll product at `0x080055B4`, loads rec +0x10 at `0x080055C4`, adds it at `0x080055C8`, then
    stores each sum `asr #10` to REG_BGxHOFS at `0x08005610` and REG_BGxVOFS at `0x08005614`. The
    screen-block DMA `sub_080054A4` indexes from the same two accumulators, so the shift does not
    cancel. Bible B1082 already said so: layer pixel = world pixel + 64 n.

    The witnesses are measured, not assumed. Map 2,7 (world 584x536) draws BG1 over x 64 to 647 and
    y 64 to 599, and BG3 over x 192 to 775 and y 192 to 727: each ends exactly at world + offset - 1
    on both axes. Map 2,2 (world 768x512) ends BG1 at x 831, BG2 at 895 and BG3 at 959. Map 2,38
    carries offset 0 on all four layers and is the control: its picture must not move one pixel.
    """

    def extent(self, zone: int, area: int, bg: int) -> tuple:
        """(first x, last x, first y, last y) of the pixels this one layer draws, or None when it
        draws nothing. Black is the compose background, so a black column carries no art."""
        img, _lines = map_view.render(BASE_ROM, zone, area, which=(bg,), show_collision=False,
                                      show_items=False)
        width, height = img.size
        pixel = img.load()
        seen = [(x, y) for y in range(height) for x in range(width) if pixel[x, y] != (0, 0, 0)]
        if not seen:
            return None
        return (min(x for x, _ in seen), max(x for x, _ in seen),
                min(y for _, y in seen), max(y for _, y in seen))

    def test_map_2_7_draws_every_layer_inside_its_own_world(self):
        """The owner's own witness: he called 2,7's collision and art out of line by eye."""
        for bg, want in ((1, (0, 583, 0, 535)), (3, (0, 583, 0, 535))):
            with self.subTest(bg=bg):
                self.assertEqual(self.extent(2, 7, bg), want)
        first_x, last_x, first_y, last_y = self.extent(2, 7, 2)
        self.assertLessEqual(last_x, 583)
        self.assertLessEqual(last_y, 535)
        self.assertGreaterEqual(min(first_x, first_y), 0)

    def test_map_2_2_ends_all_three_ground_layers_at_the_world_edge(self):
        """Unfixed this reads 831, 895 and 959: the staircase in the proof picture."""
        for bg in (1, 2, 3):
            with self.subTest(bg=bg):
                self.assertEqual(self.extent(2, 2, bg)[1], 767)

    def test_map_2_38_carries_no_offset_and_must_not_move(self):
        """The control. Every one of its layers stores offset 0, so the fix is a no-op here."""
        layout = map_view.layout_of(BASE_ROM, P.map_entry(BASE_ROM, 2, 38)[1], 1) - map_view.ROM_BASE
        for rec in P.layout_layers(BASE_ROM, layout):
            if rec["at"] is not None:
                self.assertEqual(rec["offset"], (0, 0), f"bg{rec['bg']} of map 2,38")
        for bg in (0, 1, 3):
            with self.subTest(bg=bg):
                self.assertEqual(self.extent(2, 38, bg), (0, 511, 0, 471))

    def test_the_shift_helper_mirrors_the_handlers_arithmetic_shift(self):
        """ASR is signed, so the helper must be. No vanilla tilemap layer stores a negative word,
        and a build or a hand edit may."""
        self.assertEqual(map_view.layer_shift((0x10000, 0x30000)), (64, 192))
        self.assertEqual(map_view.layer_shift((0, 0)), (0, 0))
        self.assertEqual(map_view.layer_shift((0xFFFF0000, 0)), (-64, 0))

    def test_the_report_names_each_layers_offset_in_pixels(self):
        _img, lines = map_view.render(BASE_ROM, 2, 7, show_collision=False, show_items=False)
        self.assertTrue(any("offset 64,64 px" in ln for ln in lines), lines)
        self.assertTrue(any("offset 192,192 px" in ln for ln in lines), lines)


class AnimatedGroupTests(unittest.TestCase):
    """A map loads ANIMATED tile groups beside its static stream, and the render must draw them.

    Sprite_LoadTiles @0x0800501E: a group header F holds u8 tile count at F+1, u16 destination slot
    at F+2 and u32 frame pointers from F+4, and the loader DMAs count * 64 bytes to
    0x06000000 + slot * 64. A group usually sits PAST the static stream, so a renderer that stops at
    the stream draws nothing in those cells and shows the layer below. Map 7,15 loads 633 static
    tiles and one group over slots 894 and 895, which 33 of its BG2 cells name.

    The expected pixels are read by walking the header HERE, never through the shared decoder, so a
    wrong decode cannot agree with itself and pass.
    """

    ANIM_CELL = (76, 46)                  # a BG2 cell naming slot 894, with neither flip bit set
    BG2 = 2

    def group_frame_zero(self) -> tuple:
        """(first slot, the frame 0 pixels) of map 7,15's one animated group."""
        layout = map_view.layout_of(BASE_ROM, P.map_entry(BASE_ROM, 7, 15)[1], 1) - map_view.ROM_BASE
        self.assertEqual(P.u32(BASE_ROM, layout + 0x0C), 1, "map 7,15 carries one animated group")
        table = P.u32(BASE_ROM, layout + 0x10) - map_view.ROM_BASE
        header = P.u32(BASE_ROM, table) - map_view.ROM_BASE
        count, first = BASE_ROM[header + 1], struct.unpack_from("<H", BASE_ROM, header + 2)[0]
        at = P.u32(BASE_ROM, header + 4) - map_view.ROM_BASE
        pixels, _packed = decompress(BASE_ROM, at + 4, limit=0x1000)
        self.assertEqual((count, first, len(pixels)), (2, 894, 128))
        return first, pixels

    def cell_entry(self, tx: int, ty: int) -> int:
        """The BG2 tile entry at a cell, read straight out of its block frame."""
        rec = [r for r in P.layout_layers(BASE_ROM, map_view.layout_of(
            BASE_ROM, P.map_entry(BASE_ROM, 7, 15)[1], 1) - map_view.ROM_BASE) if r["bg"] == self.BG2][0]
        across = rec["blocks"][0]
        block = (ty // 32) * across + tx // 32
        frame = map_view.frame(BASE_ROM, P.u32(BASE_ROM, rec["at"] + 0x18 + 4 * block))
        return struct.unpack_from("<H", frame, 2 * ((ty % 32) * 32 + tx % 32))[0]

    def test_an_animated_slot_cell_draws_the_groups_first_frame(self):
        """Before this was fixed the cell drew nothing and the layer below showed through."""
        first, pixels = self.group_frame_zero()
        tx, ty = self.ANIM_CELL
        entry = self.cell_entry(tx, ty)
        self.assertEqual(entry & 0xC00, 0, "the sample cell must carry neither flip bit")
        slot = entry & 0x3FF
        self.assertEqual(slot, first, f"cell ({tx},{ty}) no longer names the group's first slot")

        img, _lines = map_view.render(BASE_ROM, 7, 15, which=(self.BG2,), show_collision=False,
                                      show_items=False)
        pal = map_view.palette(BASE_ROM)
        tile = pixels[64 * (slot - first):64 * (slot - first) + 64]
        self.assertTrue(all(tile), "every pixel of this tile is opaque, so every pixel is comparable")
        # The picture is in WORLD pixels, and map 7,15's BG2 carries offset 128,128, so a cell of the
        # grid is drawn at grid pixel minus the shift. This sample moved with the renderer, by 128 px
        # on both axes; the cell it names and the pixels it expects did not change.
        shift = map_view.layer_shift((0x20000, 0x20000))
        self.assertEqual(shift, (128, 128), "map 7,15 BG2's offset words")
        found = [img.getpixel((tx * 8 - shift[0] + x, ty * 8 - shift[1] + y))
                 for y in range(8) for x in range(8)]
        self.assertEqual(found, [tuple(pal[3 * v:3 * v + 3]) for v in tile])

    def test_the_tile_list_is_indexed_by_vram_slot(self):
        """tiles() is indexed by the slot a BG cell names, so a group's slots carry its pixels."""
        first, pixels = self.group_frame_zero()
        layout = map_view.layout_of(BASE_ROM, P.map_entry(BASE_ROM, 7, 15)[1], 1)
        tl = map_view.tiles(BASE_ROM, layout)
        self.assertEqual(len(tl), first + 2)
        self.assertEqual(bytes(tl[first]), bytes(pixels[:64]))
        self.assertEqual(bytes(tl[first + 1]), bytes(pixels[64:]))
        self.assertEqual(sum(1 for px in tl if not px), first - 633,
                         "the slots between the static stream and the group load nothing")

    def test_a_group_overwrites_the_static_stream_it_overlaps(self):
        """Map 6,99 is the one vanilla layout whose groups overlap the stream, over slots 1 to 49.

        The loader runs the stream first and the groups after, so the group wins. Its 5 groups
        cover 49 slots and not one of them holds the tile the stream put there."""
        layout = map_view.layout_of(BASE_ROM, P.map_entry(BASE_ROM, 6, 99)[1], 1)
        off = layout - map_view.ROM_BASE
        groups = P.layout_groups(BASE_ROM, off)
        static, loaded = P.static_tiles(BASE_ROM, off), map_view.tiles(BASE_ROM, layout)
        self.assertEqual(len(groups), 5)
        self.assertEqual(len(loaded), len(static), "no group of 6,99 reaches past the stream")
        covered = {g["first"] + n for g in groups for n in range(g["tiles"])}
        self.assertEqual(covered, set(range(1, 50)))
        for g in groups:
            for n in range(g["tiles"]):
                self.assertEqual(bytes(loaded[g["first"] + n]),
                                 bytes(g["frames"][0]["pixels"][64 * n:64 * n + 64]))
        self.assertEqual({i for i in range(len(static))
                          if bytes(static[i]) != bytes(loaded[i])}, covered)


if __name__ == "__main__":
    unittest.main()
