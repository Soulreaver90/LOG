r"""
test_sprite_lab.py - Tests for patches.sprite_lab (trial 2026-10-31): the sprite lab. Gohan on a flat
                     colour field, no HUD, no enemies, no scene.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_sprite_lab.py -v
Builds build_list_trial_spritelab.txt in memory: "r40" = the dev master (pinned by SHA-1) and "rom" = that
list plus sprite_lab. The trial includes the dev master, so it carries the gi art. The wrapper is decoded with thumb_dis, never with the encoder. The enter script is
decoded with scene_lib's own op walker. Expected values are restated from
docs\tasks\2026-10-31-sprite-lab\sprite-lab.md and from the ROM reads in
scripts\one-time\2026-10-31-sprite-lab\, never imported from the patch module except where the test says so.
"""
import hashlib
import struct
import unittest

import log2_build
from scene import scene_lib
from patches import sprite_lab
from rom.thumb_dis import listing

# ===== constants (brief, the task probes, the base and r40 bytes) =====
ROM_BASE = 0x08000000
ROOT = log2_build.ROOT
DEV_LIST = log2_build.DEV_LIST                                  # the trial list includes this, not golden
TRIAL_LIST = ROOT / "scripts" / "permanent" / "build_list_trial_spritelab.txt"
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"
# The hook: vt_player (symbols.py) slot +8, whose only reference the codemap names "vt_player+0x8".
VT_PLAYER, HOOK, VANILLA_PLAYER_UPDATE = 0x08025604, 0x2560C, 0x08008767
# The lab map: zone 8 area 36, entry rom:0x40C778 (s7_spots.txt). Its name index +0xC is 222.
LAB_ZONE, LAB_AREA, LAB_VAR, LAB_ENTRY = 8, 36, 1, 0x40C778
MAP_TABLE, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56
LIST_FIELDS = {0x10: 3, 0x14: 4, 0x18: 5, 0x1C: 6, 0x20: 7}     # list word offset -> count byte
SCRIPT_FIELDS = (0x28, 0x30, 0x34)                              # variation, enter, leave
ENTER_SCRIPT = 0x30
# The backdrop colours. Lime is the Ruling 49 review-sheet lime (191,255,7) as BGR555.
LIME, MAGENTA, WHITE, BLACK = 0x03F7, 0x7C1F, 0x7FFF, 0x0000
# The map view clamps the camera to 0..+0x5C by 0..+0x5E, read (72,80) from IWRAM on this map, so the
# camera must not exceed it. LAB_CAMERA was (116,96) at first, which is outside the clamp.
LAB_CLAMP, LAB_CAMERA, LAB_SPOT = (72, 80), (72, 80), (236, 180)
LAB_FLAG = 350
SAVE, O_STORY = 0x03000E90, 0xB4
IO, PAL = 0x04000000, 0x05000000
# Measured in the capture runs under scratch\capture\. Gate on (lab slot, flag 350 set) and gate off
# (Ginger Town slot, flag 350 clear).
LIVE_DISPCNT, LIVE_BACKDROP = 0x1040, 0x03F7
OFF_DISPCNT, OFF_BACKDROP = 0x1F40, 0x0000
GINGER_MAP, GINGER_SPOT, GINGER_SPAWN = (10, 1, 1), (352, 488), (432, 488)


def _u32(rom, at):
    return struct.unpack_from("<I", rom, at)[0]


class Built(unittest.TestCase):
    """One build of each list, shared by every test: a build is slow."""

    @classmethod
    def setUpClass(cls):
        cls.r40, _ = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(DEV_LIST))
        cls.rom, cls.alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(TRIAL_LIST))
        cls.note = cls.alloc.notes["sprite_lab"]
        cls.base = log2_build.BASE.read_bytes()


class ListTests(Built):
    def test_the_dev_list_still_rebuilds_to_r40(self):
        """The one test the brief names: sprite_lab must not change the shipped build."""
        self.assertEqual(hashlib.sha1(bytes(self.r40)).hexdigest(), R40_SHA1)

    def test_the_trial_list_is_dev_plus_sprite_lab(self):
        dev = log2_build.read_build_list(DEV_LIST)
        trial = log2_build.read_build_list(TRIAL_LIST)
        self.assertEqual(trial, dev + ["sprite_lab"])

    def test_sprite_lab_is_not_in_a_master(self):
        self.assertNotIn("sprite_lab", log2_build.read_build_list(DEV_LIST))
        self.assertNotIn("sprite_lab", log2_build.read_build_list(log2_build.BUILD_LIST))


class ColourTests(Built):
    def test_the_named_colours_are_the_expected_bgr555_words(self):
        self.assertEqual(sprite_lab.LAB_COLOURS,
                         {"lime": LIME, "magenta": MAGENTA, "white": WHITE, "black": BLACK})

    def test_the_default_colour_is_lime_not_white(self):
        """White hides the gi's white swoosh, light greys and highlights (final, 2026-10-30)."""
        self.assertEqual(sprite_lab.LAB_COLOUR, "lime")
        self.assertEqual(sprite_lab.lab_colour(), LIME)

    def test_lime_is_the_review_sheet_lime(self):
        """Ruling 49 lime (191,255,7): the same five-bit channels the review sheets use."""
        c = LIME
        self.assertEqual((c & 31, (c >> 5) & 31, (c >> 10) & 31), (191 >> 3, 255 >> 3, 7 >> 3))

    def test_the_colour_word_reaches_the_wrapper_pool(self):
        at, size = self.note["wrapper"], self.note["size"]
        pool = [_u32(self.rom, a) for a in range(at, at + size, 4)]
        self.assertIn(sprite_lab.lab_colour(), pool)

    def test_an_unknown_colour_name_is_refused(self):
        old = sprite_lab.LAB_COLOUR
        try:
            sprite_lab.LAB_COLOUR = "chartreuse"
            with self.assertRaises(ValueError):
                sprite_lab.lab_colour()
        finally:
            sprite_lab.LAB_COLOUR = old


class MapTests(Built):
    """No enemies: the lab map builds nothing, in the base ROM and in the trial."""

    def test_the_lab_map_entry_is_where_the_probe_found_it(self):
        self.assertEqual(sprite_lab.map_entry(self.base, LAB_ZONE, LAB_AREA), LAB_ENTRY)
        self.assertEqual((self.base[LAB_ENTRY], self.base[LAB_ENTRY + 1], self.base[LAB_ENTRY + 2]),
                         (LAB_ZONE, LAB_AREA, LAB_VAR))

    def test_every_list_word_and_count_byte_is_zero(self):
        """The spawn list, the region list and the three other lists are all empty, so the map builds
        no enemy, no NPC and no region. This is the 'spawns nothing' proof in the ROM bytes."""
        for rom, name in ((self.base, "base"), (self.rom, "trial")):
            for off, count in LIST_FIELDS.items():
                self.assertEqual(_u32(rom, LAB_ENTRY + off), 0, f"{name} list word +0x{off:X}")
                self.assertEqual(rom[LAB_ENTRY + count], 0, f"{name} count byte +{count}")

    def test_the_spawn_list_count_is_zero_for_the_lab_map_only_among_its_zone(self):
        """A guard against reading the wrong entry: zone 8 does have maps that spawn."""
        spawning = [i for i in range(MAP_COUNT)
                    if self.base[MAP_TABLE + i * MAP_SIZE] == LAB_ZONE
                    and self.base[MAP_TABLE + i * MAP_SIZE + 4]]
        self.assertTrue(spawning, "zone 8 should have maps with spawns, else the field read is wrong")

    def test_the_combat_byte_is_one_so_actions_work(self):
        """`A button @0x08007DE8`: on a no-combat map A only interacts, and the ability 12 transform test
        needs the map combat word too. The lab map must be a combat map (bible section 14, section 6)."""
        self.assertEqual(self.base[LAB_ENTRY + 8], 1)
        self.assertEqual(self.rom[LAB_ENTRY + 8], 1)

    def test_only_the_enter_script_word_changes_on_the_entry(self):
        before = bytearray(self.base[LAB_ENTRY:LAB_ENTRY + MAP_SIZE])
        after = bytearray(self.rom[LAB_ENTRY:LAB_ENTRY + MAP_SIZE])
        self.assertNotEqual(before[ENTER_SCRIPT:ENTER_SCRIPT + 4], after[ENTER_SCRIPT:ENTER_SCRIPT + 4])
        before[ENTER_SCRIPT:ENTER_SCRIPT + 4] = after[ENTER_SCRIPT:ENTER_SCRIPT + 4]
        self.assertEqual(before, after)

    def test_the_variation_and_leave_scripts_stay_zero(self):
        for off in (0x28, 0x34):
            self.assertEqual(_u32(self.rom, LAB_ENTRY + off), 0)


class EnterScriptTests(Built):
    def test_the_enter_script_word_names_the_new_record(self):
        self.assertEqual(_u32(self.rom, LAB_ENTRY + ENTER_SCRIPT),
                         self.note["enter_script"] + ROM_BASE)

    def test_the_enter_script_decodes_to_hud_off_camera_end(self):
        """Decoded with scene_lib's own op walker, not with the encoder that wrote it."""
        at = self.note["enter_script"]
        ops, o = [], at
        while True:
            end = scene_lib.op_end(self.rom, o)
            ops.append(bytes(self.rom[o:end]))
            if self.rom[o] == 17:
                break
            o = end
        self.assertEqual(len(ops), 5)
        self.assertEqual(ops[0], bytes([0, 0]))                 # push 0
        self.assertEqual(ops[1], bytes([2, 86]))                # ext 86: HUD off
        self.assertEqual(ops[2][0], 29)                         # push list of 3
        self.assertEqual(ops[3], bytes([2, 31]))                # ext 31: camera
        self.assertEqual(ops[4], bytes([17]))                   # end: control goes back to the player

    def test_the_camera_push_holds_the_lab_camera(self):
        at = self.note["enter_script"]
        o = at
        while self.rom[o] != 29:
            o = scene_lib.op_end(self.rom, o)
        count, i, vals = self.rom[o + 1], o + 2, []
        for _ in range(count):
            v = 0
            while True:
                c = self.rom[i]
                i += 1
                v = (v << 7) + (c & 0x7F)
                if not c & 0x80:
                    break
            vals.append(-(v >> 1) if v & 1 else v >> 1)
        self.assertEqual(vals[:2], list(LAB_CAMERA))

    def test_the_script_ends_so_the_player_keeps_control(self):
        """No action restriction: the record has no wait and no map load, only end."""
        at = self.note["enter_script"]
        o, ext_ops = at, []
        while self.rom[o] != 17:
            if self.rom[o] == 2:
                ext_ops.append(self.rom[o + 1])
            o = scene_lib.op_end(self.rom, o)
        self.assertEqual(sorted(ext_ops), [31, 86])


class HookTests(Built):
    def test_the_hooked_slot_held_the_vanilla_player_update(self):
        """Vtable words are base-relative: vt_player + word = the Thumb target (CHF bible row)."""
        self.assertEqual((VT_PLAYER + _u32(self.base, HOOK)) & 0xFFFFFFFF, VANILLA_PLAYER_UPDATE)
        self.assertEqual(_u32(self.base, HOOK), _u32(self.r40, HOOK), "r40 must leave the slot vanilla")

    def test_the_hook_now_names_the_wrapper(self):
        want = (self.note["wrapper"] + ROM_BASE) | 1
        self.assertEqual((VT_PLAYER + _u32(self.rom, HOOK)) & 0xFFFFFFFF, want)

    def test_the_wrapper_decodes_to_the_gate_the_two_writes_and_the_tail_call(self):
        at, size = self.note["wrapper"], self.note["size"]
        text = [t for _, t in listing(bytes(self.rom), at + ROM_BASE, 24)]
        gate_byte = SAVE + O_STORY + (LAB_FLAG >> 3)
        self.assertEqual(text[0], "push {r4,lr}")
        self.assertIn(f"ldr r1,=0x{gate_byte:08x}", text)
        self.assertIn("ldrb r0,[r1,#0x0]", text)
        self.assertIn(f"lsl r0,r0,#{31 - (LAB_FLAG & 7)}", text)
        self.assertIn("lsr r0,r0,#31", text)
        self.assertIn(f"ldr r1,=0x{IO:08x}", text)
        self.assertIn("ldrh r0,[r1,#0x0]", text)
        self.assertIn(f"ldr r1,=0x{PAL:08x}", text)
        self.assertIn(f"ldr r0,=0x{sprite_lab.lab_colour():08x}", text)
        self.assertIn(f"ldr r3,=0x{VANILLA_PLAYER_UPDATE:08x}", text)
        self.assertIn("bx r3", text)
        self.assertIn("pop {r4,pc}", text)

    def test_the_dispcnt_rebuild_drops_only_the_four_bg_enable_bits(self):
        """The wrapper keeps bits 0-7 and 12-15 and adds them, so bits 8-11 (BG0-BG3) go. Modelled here
        over every halfword, which no single capture frame can prove."""
        for value in range(0x10000):
            low = (value << 24 & 0xFFFFFFFF) >> 24
            high = ((value >> 12) << 12) & 0xFFFF
            self.assertEqual(low + high, value & ~0x0F00 & 0xFFFF)

    def test_the_gate_shift_isolates_the_lab_flag_bit(self):
        left, byte_at = 31 - (LAB_FLAG & 7), LAB_FLAG >> 3
        self.assertEqual(sprite_lab.gate_byte_address(), SAVE + O_STORY + byte_at)
        self.assertEqual(sprite_lab.gate_left_shift(), left)
        for value in range(256):
            got = ((value << left) & 0xFFFFFFFF) >> 31
            self.assertEqual(got, value >> (LAB_FLAG & 7) & 1)


class SiteTests(Built):
    def test_every_differing_byte_is_inside_a_declared_site(self):
        sites = [(s, s + n - 1) for s, n, _ in self.note["sites"]]
        runs, cur = [], None
        for i in range(len(self.rom)):
            if self.rom[i] != self.r40[i]:
                cur = [i, i] if cur is None else cur
                cur[1] = i
            elif cur is not None:
                runs.append(tuple(cur))
                cur = None
        if cur:
            runs.append(tuple(cur))
        self.assertTrue(runs)
        for a, b in runs:
            self.assertTrue(any(s <= a and b <= e for s, e in sites),
                            f"rom:0x{a:X}-0x{b:X} lies outside every declared site")

    def test_only_the_two_hooked_words_are_below_the_expansion_area(self):
        low = [(s, n, name) for s, n, name in self.note["sites"] if s < 0x800000]
        self.assertEqual(sorted((s, n) for s, n, _ in low), [(HOOK, 4), (LAB_ENTRY + ENTER_SCRIPT, 4)])

    def test_the_new_chunks_were_free_and_unnamed(self):
        for key, size_key in (("wrapper", "size"), ("enter_script", "enter_script_size")):
            at, size = self.note[key], self.note[size_key]
            self.assertGreaterEqual(at, 0x800000)
            self.assertEqual(set(self.r40[at:at + size]), {0xFF}, f"{key} chunk was not free in r40")

    def test_a_second_run_raises(self):
        with self.assertRaises(ValueError):
            sprite_lab.apply(bytearray(self.rom), self.alloc)

    def test_the_module_refuses_a_rom_whose_lab_map_spawns(self):
        rom = bytearray(self.base)
        struct.pack_into("<I", rom, LAB_ENTRY + 0x14, 0x08400000)
        rom[LAB_ENTRY + 4] = 3

        class Notes:
            notes = {}

            def alloc(self, n):
                raise AssertionError("it must refuse before it allocates")

        with self.assertRaises(ValueError):
            sprite_lab.apply(rom, Notes())


class LiveTests(Built):
    """What the capture runs measured on the trial ROM. Restated here so a later change that breaks the
    lab fails a test instead of only looking wrong in a sheet."""

    def test_the_module_constants_match_the_captured_run(self):
        self.assertEqual(sprite_lab.lab_colour(), LIVE_BACKDROP)
        self.assertEqual(LIVE_DISPCNT & 0x0F00, 0, "the captured DISPCNT still had a BG layer on")
        self.assertEqual(LIVE_DISPCNT & 0x1000, 0x1000, "the captured DISPCNT had the OBJ layer off")

    def test_the_gate_off_branch_leaves_the_screen_vanilla(self):
        """The Ginger Town slot leaves flag 350 clear. Captured there: all four BG layers on and the
        vanilla backdrop, so the wrapper changed nothing."""
        self.assertEqual(OFF_DISPCNT & 0x0F00, 0x0F00)
        self.assertNotEqual(OFF_BACKDROP, sprite_lab.lab_colour())

    def test_the_lab_camera_is_inside_the_measured_clamp(self):
        """The first LAB_CAMERA (116,96) was outside the clamp, so the engine held the camera at the
        corner and the frames could not show whether ext 31 had run."""
        self.assertEqual(sprite_lab.LAB_SPOT, LAB_SPOT)
        self.assertEqual(sprite_lab.LAB_CAMERA, LAB_CAMERA)
        self.assertLessEqual(sprite_lab.LAB_CAMERA[0], LAB_CLAMP[0])
        self.assertLessEqual(sprite_lab.LAB_CAMERA[1], LAB_CLAMP[1])

    def test_the_lab_spot_stays_on_screen_from_the_lab_camera(self):
        sx = LAB_SPOT[0] - LAB_CAMERA[0]
        sy = LAB_SPOT[1] - LAB_CAMERA[1]
        self.assertTrue(0 <= sx < 240 and 0 <= sy < 160, f"the lab spot is off screen at ({sx},{sy})")

    def test_the_ginger_town_preset_is_the_measured_road_spot(self):
        """Measured off the captured frame with the live camera, not off a renderer: the pale road strip
        runs world x 336-374 on row y 488, and the preset stands in the middle of it."""
        from rom import log2_save
        row = log2_save.PRESET_SETS["spritelab"][1]
        self.assertEqual(row[1], "postcell", "the Ginger Town slot must leave the lab flag clear")
        self.assertEqual(tuple(row[3:6]), GINGER_MAP)
        self.assertEqual(tuple(row[6:8]), GINGER_SPOT)
        self.assertTrue(336 <= GINGER_SPOT[0] <= 374, "the spot must be on the pale road strip")
        self.assertLess(GINGER_SPOT[0], GINGER_SPAWN[0], "the owner said left of the spawn point")

    def test_the_lab_story_sets_the_gate_flag_and_the_ginger_story_does_not(self):
        from rom import log2_save
        lab_flags = dict(log2_save.STORIES)["spritelab"][0]
        self.assertIn((LAB_FLAG, LAB_FLAG), lab_flags)
        self.assertEqual(log2_save.LAB_FLAG, LAB_FLAG)
        post_flags = dict(log2_save.STORIES)["postcell"][0]
        self.assertFalse([r for r in post_flags if r[0] <= LAB_FLAG <= r[1]])


if __name__ == "__main__":
    unittest.main()
