r"""
test_trunks_tank.py - Tests for patches.trunks_tank (trial 2026-11-01): Trunks wears the tank top, as
                      base Trunks (set 128) and as Super Saiyan Trunks (set 134).

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_trunks_tank.py -v
Builds build_list_trial_trunkstank.txt in memory: "before" = the spritelab trial list and "rom" = that list
plus trunks_tank. Expected values are restated from docs\tasks\2026-11-01-trunks-tank-lab\brief.md,
docs\tasks\2026-11-02-trunks-ssj\brief.md and the base ROM's own records, never imported from the patch
module except where a test says so.
The manifest is the proved source: these tests check the ROM against it, not the other way round.
"""
import json
import struct
import unittest

from PIL import Image

import log2_build
import log_paths
from patches import trunks_tank
from rom.log2_sprites import image_to_tiles, set_records
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, rom_ptr, unpack_frame

# ===== constants (the briefs, the manifest and the base ROM) =====
LISTS = log_paths.PERMANENT
TRIAL_LIST = LISTS / "build_list_trial_trunkstank.txt"
SPRITELAB_LIST = LISTS / "build_list_trial_spritelab.txt"
ART = log_paths.TRUNKS_TANK
FIRST_ID, SET_TABLE_LITERAL = 7, 0x959C
BASE_SET, SSJ_SET = 128, 134
VANILLA = {BASE_SET: 0x35BBE0, SSJ_SET: 0x37FB74}       # both read out of the base ROM with set_records
GEOMETRY = ("dx", "dy", "w", "h", "attr0", "attr1")
# Source of truth is manifest.json, NOT the 2026-11-01 lab brief, which predates the walks.
# Base art (set 128) is the complete walk in all four directions plus the idles: 17 pngs, 20 headers,
# 28 keys. Super Saiyan art (set 134) adds the side row and the front walk: 10 pngs, 11 headers,
# 18 keys. The Super Saiyan back row and front facing idles are deliberately absent, see
# test_the_super_saiyan_back_and_front_idles_are_not_in_the_manifest.
PNG_COUNT, HEADER_COUNT, KEY_COUNT = 32, 37, 53
BODY_FROM = 16                         # rows 16-31 are the shared body (bible row 262)
H_FLIP = 0x1000                        # OBJ attr1 bit 12: dir 3 draws the dir 2 frame mirrored
# Set 134 keys that stay vanilla on purpose. The owner's back art fills the removed collar with BASE
# hair, which cannot go on a gold head, and the front facing idles carry a Super Saiyan arm the base
# art has no answer for. docs\tasks\2026-11-02-trunks-ssj\brief.md.
SSJ_HELD = [(0, 0, 0), (0, 0, 1), (4, 0, 2)]                          # front facing idles only
# The back idle and the back walk shipped 2026-11-05 once the owner chose the collar fill rule.
# COLLAR_FILL is that rule: where his base art draws hair over the removed collar, the Super Saiyan
# frame takes the gold of the same ROLE. It is the project's own map, in art/trunks_tank/trail/.
COLLAR_FILL = {0xE5: 0x14, 0x64: 0x2E, 0x62: 0x78}
JACKET_IDX = {0x4E, 0x4F, 0x50, 0x51}


def _xy(i, w):
    """A tile order byte index back to (x, y), so a failure names a pixel and not an offset."""
    tile, rem = divmod(i, 64)
    r, c = divmod(rem, 8)
    return (tile % (w // 8)) * 8 + c, (tile // (w // 8)) * 8 + r


def _records(rom, set_id):
    off = rom_ptr(rom, rom_ptr(rom, SET_TABLE_LITERAL) + 4 * (set_id - FIRST_ID))
    return off, {(r["anim"], r["dir"], r["index"]): r for r in set_records(rom, off)}


class Built(unittest.TestCase):
    """One build of each list, shared by every test: a build is slow."""

    @classmethod
    def setUpClass(cls):
        cls.before, _ = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(SPRITELAB_LIST))
        cls.rom, cls.alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(TRIAL_LIST))
        cls.note = cls.alloc.notes["trunks_tank"]
        cls.base = log2_build.BASE.read_bytes()
        cls.manifest = json.loads((ART / "manifest.json").read_text(encoding="ascii"))
        cls.drawn = {}
        for m in cls.manifest:
            with Image.open(ART / m["png"]) as img:
                cls.drawn[m["png"]] = image_to_tiles(img)


class ListTests(Built):
    def test_the_trial_list_is_the_spritelab_list_plus_trunks_tank(self):
        lab = log2_build.read_build_list(SPRITELAB_LIST)
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), lab + ["trunks_tank"])

    def test_trunks_tank_is_in_no_master(self):
        """The art is a work in progress, so it stays out of the golden and the dev masters."""
        self.assertNotIn("trunks_tank", log2_build.read_build_list(log2_build.BUILD_LIST))
        self.assertNotIn("trunks_tank", log2_build.read_build_list(log2_build.DEV_LIST))


class ManifestTests(Built):
    """The manifest was generated from the ROM. These tests hold the ROM to it."""

    def test_the_manifest_covers_the_frames_the_briefs_name(self):
        views = sorted((m["form"], m["view"], m["pose"]) for m in self.manifest)
        self.assertEqual(views, [("base", "back", "idle"),
                                 ("base", "back", "walk 0"), ("base", "back", "walk 1"),
                                 ("base", "back", "walk 2"), ("base", "back", "walk 3"),
                                 ("base", "front", "idle"), ("base", "front", "stand 1"),
                                 ("base", "front", "walk 0"), ("base", "front", "walk 1"),
                                 ("base", "front", "walk 2"), ("base", "front", "walk 3"),
                                 ("base", "side", "idle"), ("base", "side", "stand 1"),
                                 ("base", "side", "walk 0"), ("base", "side", "walk 1"),
                                 ("base", "side", "walk 2"), ("base", "side", "walk 3"),
                                 ("ssj", "back", "idle"),
                                 ("ssj", "back", "walk 0"), ("ssj", "back", "walk 1"),
                                 ("ssj", "back", "walk 2"), ("ssj", "back", "walk 3"),
                                 ("ssj", "front", "walk 0"), ("ssj", "front", "walk 1"),
                                 ("ssj", "front", "walk 2"), ("ssj", "front", "walk 3"),
                                 ("ssj", "side", "idle"), ("ssj", "side", "stand 1"),
                                 ("ssj", "side", "walk 0"), ("ssj", "side", "walk 1"),
                                 ("ssj", "side", "walk 2"), ("ssj", "side", "walk 3")])
        self.assertEqual(len(self.manifest), PNG_COUNT)
        self.assertEqual(sum(len(m["headers"]) for m in self.manifest), HEADER_COUNT)
        self.assertEqual(sum(len(m["keys"]) for m in self.manifest), KEY_COUNT)

    def test_every_manifest_entry_names_a_set_this_module_builds(self):
        self.assertEqual({m["set"] for m in self.manifest}, {BASE_SET, SSJ_SET})

    def test_form_and_set_agree_on_every_row(self):
        """"form" is what separates the two forms in a sorted (view, pose) list, so it must not drift."""
        for m in self.manifest:
            self.assertEqual(m["form"], "base" if m["set"] == BASE_SET else "ssj", m["png"])
            self.assertIn(m["form"], m["png"], m["png"])

    def test_the_super_saiyan_front_idles_are_not_in_the_manifest(self):
        """They need a decision only the owner can make, so no row may quietly appear."""
        painted = {tuple(k) for m in self.manifest if m["set"] == SSJ_SET for k in m["keys"]}
        self.assertEqual(sorted(painted & set(SSJ_HELD)), [])

    def test_every_header_serves_exactly_the_keys_the_manifest_lists(self):
        """Read straight out of the BASE ROM, with no help from the module."""
        for set_id, off in VANILLA.items():
            serves = {}
            for r in set_records(self.base, off):
                serves.setdefault(r["header"], []).append((r["anim"], r["dir"], r["index"]))
            for m in self.manifest:
                if m["set"] != set_id:
                    continue
                got = sorted(k for h in m["headers"] for k in serves[int(h, 16)])
                self.assertEqual(got, sorted(tuple(k) for k in m["keys"]), m["png"])

    def test_the_vanilla_sets_are_where_the_module_pins_them(self):
        for set_id, off in VANILLA.items():
            self.assertEqual(rom_ptr(self.base, SET_TABLE + 4 * (set_id - FIRST_ID)), off, set_id)

    def test_dir_3_reuses_the_dir_2_record_with_the_flip_bit(self):
        """So patching dir 2 covers dir 3, and dir 3 needs no drawing of its own. True in both sets."""
        for set_id in VANILLA:
            _, recs = _records(self.base, set_id)
            for anim, index in [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]:
                left, right = recs[(anim, 2, index)], recs[(anim, 3, index)]
                self.assertEqual(left["header"], right["header"], (set_id, anim, index))
                self.assertEqual(right["attr1"] & H_FLIP, H_FLIP, (set_id, anim, index))
                self.assertEqual(left["attr1"] & H_FLIP, 0, (set_id, anim, index))

    def test_every_png_is_the_size_the_manifest_gives_it(self):
        for m in self.manifest:
            with Image.open(ART / m["png"]) as img:
                self.assertEqual(img.size, (m["w"], m["h"]), m["png"])
            self.assertEqual(len(self.drawn[m["png"]]), m["w"] * m["h"], m["png"])


class ArtTests(Built):
    """What the Super Saiyan PNGs are allowed to contain, checked against the base ROM."""

    def test_every_super_saiyan_pixel_comes_from_vanilla_134_or_the_base_tank_png(self):
        """The derivation rule, checked per header, not per row: a row may carry two headers.
        HEAD rows: set 134's own frame, plus the owner's edit where the two vanillas agree, so the
        Super Saiyan hair is never redrawn. BODY rows: the base tank frame, which is the one body
        rule of bible row 262. Nothing is drawn, so every pixel is one of those two sources."""
        _, v134 = _records(self.base, SSJ_SET)
        _, v128 = _records(self.base, BASE_SET)
        base_png = {tuple(k): m["png"] for m in self.manifest if m["set"] == BASE_SET
                    for k in m["keys"]}
        # These frames are 16 px wide, so tile order splits at the same byte as row order: tiles 0-3
        # are rows 0-15 and tiles 4-7 are rows 16-31. Every array below is in tile order, so one
        # index names the same pixel in all of them.
        head = BODY_FROM * 16
        for m in self.manifest:
            if m["set"] != SSJ_SET:
                continue
            self.assertEqual((m["w"], m["h"]), (16, 32), m["png"])
            for key in (tuple(k) for k in m["keys"]):
                ours = self.drawn[m["png"]]
                vanilla = unpack_frame(self.base, v134[key]["header"])[2]
                old = unpack_frame(self.base, v128[key]["header"])[2]
                tank = self.drawn[base_png[key]]
                for i, got in enumerate(ours):
                    allowed = {vanilla[i], tank[i]}
                    if i < head and tank[i] in COLLAR_FILL:
                        allowed.add(COLLAR_FILL[tank[i]])
                    self.assertIn(got, allowed, (m["png"], key, i))
                for i in range(head):
                    if vanilla[i] != old[i]:
                        if vanilla[i] in JACKET_IDX and tank[i] not in JACKET_IDX:
                            continue      # garment removal is the point of the swap, not a redraw
                        self.assertEqual(ours[i], vanilla[i], (m["png"], key, i))
                self.assertEqual(ours[head:], tank[head:], (m["png"], key))
                # The point of the swap is that the garment is gone, so this asks the question the
                # other two loops cannot: they key on vanilla 134, which IS the jacket. A jacket
                # pixel that both vanillas share reaches neither. That hole shipped walk 2 (9,13)
                # blue, and only the owner's eye caught it.
                for i in range(len(ours)):
                    if tank[i] not in JACKET_IDX:
                        self.assertNotIn(ours[i], JACKET_IDX, (m["png"], key, i))

    def test_the_one_body_rule_discards_exactly_two_super_saiyan_pixels(self):
        """The cost of the one body rule, pinned so it cannot grow quietly. Over every shipped set
        134 key, the body rows differ from set 128 in vanilla at just (4,17) and (5,20) of the side
        idle and side stand 1, 0x4D against 0x4E. Taking the owner's body overwrites both."""
        _, v134 = _records(self.base, SSJ_SET)
        _, v128 = _records(self.base, BASE_SET)
        head = BODY_FROM * 16
        lost = set()
        for m in self.manifest:
            if m["set"] != SSJ_SET:
                continue
            for key in (tuple(k) for k in m["keys"]):
                new = unpack_frame(self.base, v134[key]["header"])[2]
                old = unpack_frame(self.base, v128[key]["header"])[2]
                for i in range(head, len(new)):
                    if new[i] != old[i]:
                        lost.add((m["png"],) + _xy(i, m["w"]) + (new[i], old[i]))
        self.assertEqual(sorted(lost), [("trunks_tank_ssj_side.png", 4, 17, 0x4D, 0x4E),
                                        ("trunks_tank_ssj_side.png", 5, 20, 0x4D, 0x4E),
                                        ("trunks_tank_ssj_side_stand1.png", 4, 17, 0x4D, 0x4E),
                                        ("trunks_tank_ssj_side_stand1.png", 5, 20, 0x4D, 0x4E)])

    def test_no_super_saiyan_frame_carries_base_hair(self):
        """docs\\sprite-guide.md: revealed hair is form specific. The purple ramp is base only, and a
        collar gap filled from the base frame would put it on a gold head."""
        for m in self.manifest:
            if m["set"] == SSJ_SET:
                self.assertEqual(set(self.drawn[m["png"]]) & {0xE5, 0x64, 0x62}, set(), m["png"])


class BuiltSetTests(Built):
    def test_every_manifest_key_holds_the_drawn_pixels(self):
        recs = {s: _records(self.rom, s)[1] for s in VANILLA}
        for m in self.manifest:
            for key in (tuple(k) for k in m["keys"]):
                self.assertEqual(unpack_frame(self.rom, recs[m["set"]][key]["header"])[2],
                                 self.drawn[m["png"]], (m["png"], key))

    def test_the_anim_4_idle_variant_changes_too(self):
        """Both sets store the stand pose and the anim 4 idle as separate copies of one picture.
        Set 134's side pair differs by 2 px in VANILLA, at (4,17) and (5,20), and the one body rule
        replaces both with the owner's body, so the built pair must come out equal."""
        for set_id, pairs in [(BASE_SET, [((0, 0, 0), (4, 0, 2)), ((0, 1, 0), (4, 1, 2)),
                                          ((0, 2, 0), (4, 2, 2))]),
                              (SSJ_SET, [((0, 2, 0), (4, 2, 2))])]:
            _, recs = _records(self.rom, set_id)
            for stand, idle in pairs:
                self.assertEqual(unpack_frame(self.rom, recs[stand]["header"])[2],
                                 unpack_frame(self.rom, recs[idle]["header"])[2],
                                 (set_id, stand, idle))

    def test_every_other_record_keeps_its_vanilla_pixels(self):
        for set_id in VANILLA:
            _, built = _records(self.rom, set_id)
            _, vanilla = _records(self.base, set_id)
            painted = {tuple(k) for m in self.manifest if m["set"] == set_id for k in m["keys"]}
            for key in sorted(vanilla):
                if key in painted:
                    continue
                self.assertEqual(unpack_frame(self.rom, built[key]["header"])[2],
                                 unpack_frame(self.base, vanilla[key]["header"])[2], (set_id, key))

    def test_the_held_super_saiyan_keys_are_still_vanilla(self):
        """The back row and the front facing idles must come out of the build untouched."""
        _, built = _records(self.rom, SSJ_SET)
        _, vanilla = _records(self.base, SSJ_SET)
        for key in SSJ_HELD:
            self.assertEqual(unpack_frame(self.rom, built[key]["header"])[2],
                             unpack_frame(self.base, vanilla[key]["header"])[2], key)

    def test_no_record_geometry_moves(self):
        for set_id in VANILLA:
            _, built = _records(self.rom, set_id)
            _, vanilla = _records(self.base, set_id)
            self.assertEqual(sorted(built), sorted(vanilla))
            for key in sorted(vanilla):
                self.assertEqual([built[key][f] for f in GEOMETRY],
                                 [vanilla[key][f] for f in GEOMETRY], (set_id, key))

    def test_no_other_sprite_set_moves(self):
        """Trunks' armor sets sit beside these two in the table and must not be touched."""
        for set_id in (129, 130, 132, 133, 135):
            self.assertEqual(_records(self.rom, set_id)[0], _records(self.before, set_id)[0], set_id)


class WriteTests(Built):
    def test_the_only_changes_outside_the_allocation_are_the_two_set_table_words(self):
        words = {s: self.note["sets"][s]["word"] for s in VANILLA}
        differ = [i for i in range(len(self.before)) if self.before[i] != self.rom[i]]
        at, size = self.note["alloc"]
        outside = set(i for i in differ if not at <= i < at + size)
        allowed = set()
        for word in words.values():
            allowed |= set(range(word, word + 4))
        self.assertTrue(outside, "no set table word changed")
        self.assertEqual(outside - allowed, set())
        for set_id, word in words.items():
            self.assertNotEqual(struct.unpack_from("<I", self.before, word)[0],
                                struct.unpack_from("<I", self.rom, word)[0], set_id)

    def test_each_set_table_word_names_that_set_s_clone(self):
        for set_id, vanilla in VANILLA.items():
            got = self.note["sets"][set_id]
            self.assertEqual(struct.unpack_from("<I", self.rom, got["word"])[0],
                             got["clone"] + ROM_BASE, set_id)
            self.assertEqual(got["source"], vanilla, set_id)
        self.assertNotEqual(self.note["sets"][BASE_SET]["clone"],
                            self.note["sets"][SSJ_SET]["clone"])

    def test_the_sites_list_names_both_words(self):
        self.assertEqual(sorted(s[:2] for s in self.note["sites"]),
                         sorted((self.note["sets"][s]["word"], 4) for s in VANILLA))

    def test_the_clones_live_in_the_expansion_area(self):
        at, size = self.note["alloc"]
        self.assertGreaterEqual(at, 0x800000)
        self.assertGreater(size, 0)
        for set_id in VANILLA:
            self.assertGreaterEqual(self.note["sets"][set_id]["clone"], 0x800000, set_id)

    def test_the_live_table_is_the_relocated_one(self):
        """gohan_gi moves the set table, so the module must write into that copy, not rom:0x3B4E90."""
        self.assertNotEqual(self.note["table"], SET_TABLE)
        self.assertEqual(rom_ptr(self.rom, SET_TABLE_LITERAL), self.note["table"])

    def test_the_module_refuses_a_second_run(self):
        rom = bytearray(self.rom)
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        alloc.notes.update(self.alloc.notes)
        with self.assertRaises(ValueError):
            trunks_tank.apply(rom, alloc)

    def test_the_module_refuses_an_unrelocated_set_table(self):
        """On the bare base ROM the table is still rom:0x3B4E90, which this module must never write."""
        rom = bytearray(self.base) + bytes([0xFF]) * (log2_build.ROM_SIZE - len(self.base))
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        with self.assertRaises(ValueError):
            trunks_tank.apply(rom, alloc)

    def test_the_module_refuses_a_set_another_module_already_rebuilt(self):
        """Set 134 gets its own guard, not set 128's. Move only the 134 word and it must stop."""
        rom = bytearray(self.before)                 # table relocated, both sets still vanilla
        table = rom_ptr(rom, SET_TABLE_LITERAL)
        word = table + 4 * (SSJ_SET - FIRST_ID)
        struct.pack_into("<I", rom, word, 0x900000 + ROM_BASE)
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        with self.assertRaises(ValueError) as caught:
            trunks_tank.apply(rom, alloc)
        self.assertIn(str(SSJ_SET), str(caught.exception))


if __name__ == "__main__":
    unittest.main()
