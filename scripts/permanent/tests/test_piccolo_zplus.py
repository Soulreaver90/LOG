r"""
test_piccolo_zplus.py - Tests for patches.piccolo_zplus (trial 2026-11-12): a grade above Super
                        Namek, reached FROM Super Namek, with +10 and the HP heal.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_piccolo_zplus.py -v
Builds the Piccolo trial list in memory once and keeps the ROM before the module as "before".
Expected values are restated from the live table bytes and the handlers, never imported from the
patch module.
"""
import struct
import unittest

import log2_build
from art import art_tables as at
import log_paths
from patches import piccolo_zplus
from rom.webfoot_decompress import ROM_BASE

# ===== constants (live table bytes and handlers read 2026-11-12) =====
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_piccolo_fx.txt"
ENTRY = 20
PICCOLO_BASE, NAMEK, VEGETA_ZPLUS, ZPLUS = 6, 7, 23, 24
NAMEK_BYTES = bytes.fromhex("01685e12")                 # super flag, set 104, portrait 94, status 18
ZPLUS_BYTES = bytes.fromhex("01687b12")                 # the same, with dialog portrait 123 of its own
ZPLUS_PORTRAIT, REF_ID = 123, 121                       # the new dialog id; 121 carries the shared border
BLOCK_LITERAL, HUD_LITERAL = 0xBE10, 0x8E8C
ABILITY_TABLE, ABILITY_11 = 0x1D9900, 11
ICON_LEN, PICTURE = 0x200, (3, 2, 18, 9)                # bf_hud's icon picture box
NAMEK_FORM_OBJECT = 0x030021F0
TABLE_LITERAL = 0x1954
ABILITY_11_ACTION, VANILLA_ACTION = 0x1D99BC, 0x080134C1
NAMEK_VTABLE, VANILLA_APPLY = 0x08024ABC, 0x080173AB
HEAL_RATE, HEAL_STEP = 0x290, 0x0CCD                    # the vanilla Namek tick's own constants
TRANSFORM_MESSAGE = 0x23                                # state 35, not the Namek state 0x25

_CACHE = {}


def built() -> dict:
    if _CACHE:
        return _CACHE
    modules = log2_build.read_build_list(TRIAL_LIST)
    keep = [m for m in modules if m not in ("piccolo_zplus", "powerup_fx")]
    rom, alloc = log2_build.assemble(log2_build.BASE, keep)
    before = bytes(rom)
    piccolo_zplus.apply(rom, alloc)
    _CACHE.update(before=before, rom=bytes(rom), notes=alloc.notes["piccolo_zplus"], all_notes=alloc.notes)
    return _CACHE


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def entry_at(rom, index):
    table = _u32(rom, TABLE_LITERAL) - ROM_BASE
    return rom[table + ENTRY * index:table + ENTRY * (index + 1)]


def vtable_target(rom, vtable, slot):
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & 0xFFFFFFFF


def _bl_target(body, i, base):
    """GBA address a Thumb bl at body[i] names, or None when those two halfwords are not a bl."""
    hi, lo = struct.unpack_from("<HH", body, i)
    if hi & 0xF800 != 0xF000 or lo & 0xF800 != 0xF800:
        return None
    off = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
    if off & 0x400000:
        off -= 0x800000
    return base + ROM_BASE + i + 4 + off


def _icon_xy(i):
    """(x, y) of byte i in a 32x16 8bpp 1D-order tile image."""
    tile, rest = divmod(i, 64)
    row, col = divmod(rest, 8)
    return (tile % 4) * 8 + col, (tile // 4) * 8 + row


class PiccoloZplusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]

    # ===== the form =====

    def test_entry_24_is_super_namek_again_with_its_own_step_and_revert(self):
        """Z+ keeps set 104, status portrait 18 and the Namek form object, so his drawn power-up
        frames and the ki pool both still reach it, and it takes dialog portrait 123 of its own.
        +4 is itself, because Z+ steps no further; +5 is base."""
        e = entry_at(self.rom, ZPLUS)
        self.assertEqual(e[:4], ZPLUS_BYTES)
        self.assertEqual(entry_at(self.rom, NAMEK)[:4], NAMEK_BYTES)
        self.assertEqual((e[4], e[5]), (ZPLUS, PICCOLO_BASE))
        self.assertEqual(_u32(e, 0x10), NAMEK_FORM_OBJECT)
        self.assertEqual(self.notes["entry"], ZPLUS)

    def test_super_namek_now_steps_up_and_everything_else_is_unchanged(self):
        """Entry 7 is the only entry whose bytes move, and only its +4."""
        was = _u32(self.before, TABLE_LITERAL) - ROM_BASE
        now = _u32(self.rom, TABLE_LITERAL) - ROM_BASE
        self.assertNotEqual(was, now)
        self.assertEqual(entry_at(self.rom, NAMEK)[4], ZPLUS)
        for k in range(ZPLUS):
            old = self.before[was + ENTRY * k:was + ENTRY * (k + 1)]
            new = entry_at(self.rom, k)
            if k == NAMEK:
                old = bytearray(old)
                old[4] = ZPLUS
            self.assertEqual(bytes(new), bytes(old), f"appearance entry {k} changed")

    def test_vegeta_keeps_entry_23_so_the_two_trials_can_merge(self):
        self.assertEqual(entry_at(self.rom, VEGETA_ZPLUS), entry_at(self.before, VEGETA_ZPLUS))

    # ===== the gate =====

    def test_ability_11_is_the_one_that_is_hooked_not_ability_12(self):
        """Ability 11 is the Namek transform and 12 is the Saiyan one, so Vegeta's gate is untouched."""
        self.assertEqual(_u32(self.before, ABILITY_11_ACTION), VANILLA_ACTION)
        self.assertEqual(_u32(self.rom, ABILITY_11_ACTION), self.notes["gate"] + ROM_BASE + 1)
        self.assertEqual(_u32(self.rom, 0x1D99CC), _u32(self.before, 0x1D99CC))

    def test_the_gate_sends_the_saiyan_transform_message(self):
        """Message 0x23 lands in state 35, which runs 0xA0 frames, shares its end with the Namek
        state, and is the state bf_ki_pool and powerup_fx already hook. The Namek state 0x25 runs
        0x40 frames and neither of them hooks it."""
        at = self.notes["gate"]
        body = self.rom[at:at + 0x30]
        self.assertIn(struct.pack("<H", 0x2000 | (1 << 8) | TRANSFORM_MESSAGE), body)

    # ===== the stats and the heal =====

    def test_the_apply_and_the_tick_are_wrapped_and_still_chain_what_was_there(self):
        self.assertEqual(vtable_target(self.before, NAMEK_VTABLE, 0x00), VANILLA_APPLY)
        self.assertEqual(vtable_target(self.rom, NAMEK_VTABLE, 0x00), self.notes["apply_zp"] + ROM_BASE + 1)
        self.assertEqual(vtable_target(self.rom, NAMEK_VTABLE, 0x04), self.notes["tick_zp"] + ROM_BASE + 1)
        self.assertEqual(self.notes["chained"], vtable_target(self.before, NAMEK_VTABLE, 0x04))
        pool = {_u32(self.rom, o) for o in range(self.notes["code"], self.notes["code"] + self.notes["code_len"], 4)}
        self.assertIn(VANILLA_APPLY, pool)
        self.assertIn(self.notes["chained"], pool)

    def test_the_heal_uses_the_vanilla_period_and_the_vanilla_rate(self):
        """The owner asked for the healing back in Z+ only. The numbers are the ones the vanilla
        Super Namek tick used before piccolo_z_start took the whole tick off."""
        pool = {_u32(self.rom, o) for o in range(self.notes["code"], self.notes["code"] + self.notes["code_len"], 4)}
        self.assertIn(HEAL_RATE, pool)
        self.assertIn(HEAL_STEP, pool)
        self.assertIn(self.notes["heal_ram"], pool)

    def test_no_vanilla_code_byte_changed_outside_the_three_hook_words(self):
        """Pointer level only: the two Namek vtable words, the ability 11 action word, and the
        table literals vegeta_zplus already repoints."""
        allowed = {self.notes["apply_word"], self.notes["tick_word"], ABILITY_11_ACTION, HUD_LITERAL}
        allowed |= set(self.notes["table_namers"]) | set(self.notes["block_namers"])
        stray = [i for i in range(log2_build.BASE_SIZE)
                 if self.rom[i] != self.before[i] and not any(a <= i < a + 4 for a in allowed)]
        self.assertEqual(stray, [], f"{len(stray)} base ROM bytes changed outside the hook words")

    # ===== the icon and the portrait =====

    def test_the_hud_hook_chains_the_one_that_was_there(self):
        """One word picks the icon of the selected slot. vegeta_zplus owns it before this module,
        so the Z+ icon for ability 12 must still be reachable through the chain."""
        self.assertEqual(_u32(self.rom, HUD_LITERAL), self.notes["hud"] + ROM_BASE + 1)
        self.assertEqual(self.notes["chained_hud"], _u32(self.before, HUD_LITERAL))
        pool = {_u32(self.rom, o) for o in range(self.notes["code"], self.notes["code"] + self.notes["code_len"], 4)}
        self.assertIn(self.notes["chained_hud"], pool)
        self.assertIn(self.notes["zplus"] + ROM_BASE, pool)
        self.assertIn(self.notes["zplus_dim"] + ROM_BASE, pool)

    def test_the_gate_and_the_hud_share_one_test(self):
        """A separate copy of the EP test could drift, and then the icon would say yes while B said
        no. Both call zplus_ok, which is the ssj2_form rule."""
        body = self.rom[self.notes["code"]:self.notes["code"] + self.notes["code_len"]]
        call = self.notes["zplus_ok"] + ROM_BASE
        hits = [i for i in range(0, len(body) - 3, 2) if _bl_target(body, i, self.notes["code"]) == call]
        self.assertGreaterEqual(len(hits), 2, "zplus_ok is called fewer than twice")

    def test_the_zplus_icon_is_the_live_ability_11_icon_with_the_picture_pasted(self):
        """The pair is built from whatever icon the build holds, so it keeps the HUD look bf_hud
        gave it. Only the picture box differs from the live icon."""
        for key, word in (("zplus", 0), ("zplus_dim", 4)):
            live = _u32(self.before, ABILITY_TABLE + 16 * ABILITY_11 + word) - ROM_BASE
            new = self.notes[key]
            old_px = self.before[live:live + ICON_LEN]
            new_px = self.rom[new:new + ICON_LEN]
            self.assertNotEqual(bytes(old_px), bytes(new_px), f"{key} is the plain Z icon")
            changed = {_icon_xy(i) for i in range(ICON_LEN) if old_px[i] != new_px[i]}
            x0, y0, x1, y1 = PICTURE
            outside = [p for p in changed if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1)]
            self.assertEqual(outside, [], f"{key} changed pixels outside the picture box")

    def test_the_portrait_is_the_owners_own_drawing_at_its_own_id(self):
        """Id 123's block word names the art slot, the slot holds a raw type 0 frame, and the
        pixels are what his PNG reads as through the ROM's own palette. Id 94 is untouched."""
        block = self.notes["block"]
        frame = self.notes["frame"]
        self.assertEqual(_u32(self.rom, BLOCK_LITERAL), block + ROM_BASE)
        self.assertEqual(_u32(self.rom, block + 4 + 4 * ZPLUS_PORTRAIT), frame + ROM_BASE)
        self.assertEqual(self.rom[frame:frame + 8], struct.pack("<II", 0, at.SIZE))
        old_block = _u32(self.before, BLOCK_LITERAL) - ROM_BASE
        self.assertEqual(self.rom[block + 4:block + 4 + 4 * ZPLUS_PORTRAIT],
                         self.before[old_block + 4:old_block + 4 + 4 * ZPLUS_PORTRAIT])
        palette = at.load_palette()
        pal, allowed = at.obj_palette(self.rom, palette), at.allowed_indices(self.rom, palette)
        px = at.png_pixels(piccolo_zplus.PORTRAIT_PNG, pal, allowed)
        self.assertEqual(bytes(self.rom[frame + 8:frame + 8 + at.SIZE]), bytes(px))
        self.assertLessEqual(len(set(px)), at.MAX_COLORS)
        ref = at.live_frame(self.rom, block, REF_ID)[1]
        self.assertEqual([i for i in at.RING_IDX if px[i] != ref[i]], [])

    def test_a_second_run_raises(self):
        rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(TRIAL_LIST))
        with self.assertRaises(ValueError):
            piccolo_zplus.apply(rom, alloc)
