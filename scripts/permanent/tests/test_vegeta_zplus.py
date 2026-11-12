r"""
test_vegeta_zplus.py - Tests for patches.vegeta_zplus (trial 2026-11-12): Vegeta's second Super Saiyan grade,
                       "Z+", reached FROM Super Saiyan with the ascended grade stats and its own HUD icon.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_vegeta_zplus.py -v
Builds the dev master in memory once, keeps it as "before", then applies vegeta_zplus to the same ROM, so
every test sees both sides and the notes. The gate and the HUD hook are run as thumb_dis text in
test_ssj2's Thumb interpreter over a scripted record, so the icon tests check behavior, not code text.
Expected values are restated from docs\tasks\2026-11-12-vegeta-zplus\brief.md and the live table bytes, never
imported from the patch module.
"""
import re
import struct
import unittest
from pathlib import Path

import log2_build
import log_paths
from art import art_tables as at
from patches import vegeta_zplus
from rom.rom_space import Allocator
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, read_record, read_set
from tests.test_ssj2 import (ABILITY_12_ACTION, ENTRY, HUD_LITERAL, VANILLA_ACTION, entry_of, read_form,
                             run_gate, run_hud, table_of, u32, vanilla_icon)

# ===== constants (brief, live table bytes) =====
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_vegeta_zplus.txt"
ENTRIES = 24                                   # 23 live entries plus the new one
VEG_BASE, VEG_SSJ, ZPLUS = 8, 11, 23
GOHAN_SSJ, GOHAN_SSJ2 = 5, 22
ASCENDED, ORDINARY, ASCENDED_ENTRY = 0x030021E8, 0x030021EC, 10
ZPLUS_SET, ZPLUS_PORTRAIT, REF_ID = 139, 122, 121
Z_ICONS = (0x6DAE7C, 0x6DB07C)                 # ability 12's icon pair, usable and dim
STEP_EP = 10
BLOCK_LITERAL, BLOCK_IDS = 0xBE10, 122
PRE_CONTROL_RECORDS = (0x3DB930, 0x3DBABC)     # npc_gi's two chamber exit lines, which own portrait id 121
TABLE_LITERALS = (0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050,
                  0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474)
MODULE_LITERALS = (0x88E3B4, 0x894978, 0x89A9B4, 0x90A250, 0x90A3E0)   # ssj2_form, status_bonus, fullpower_ssj,
EXPANSION = (0x800000, 0xF00000)                                       # bf_ki_pool, fullpower_hud
ART_REGION = (0xF00000, 0x1000000)
ICONS = ("hud_zplus_usable.bin", "hud_zplus_dim.bin")
PNG = log_paths.ART_TABLES / "portraits" / "122_vegeta_grade2.png"

EXPECTED = {
    "zplus_ok": """ldrb r2,[r0,#0x8]|cmp r2,#0xb|bne +0x12|mov r3,#0x4|ldsh r2,[r0,r3]|cmp r2,#0xa|blt +0x12
        |mov r2,#0x1|bx lr|mov r2,#0x0|bx lr""",
    "gate": """push {lr}|ldrb r2,[r0,#0x8]|cmp r2,#0x17|beq +0x20|bl ZPLUS_OK|pop {r3}|mov lr,r3|cmp r2,#0x0
        |beq +0x28|ldr r2,[r1,#0x0]|ldr r3,[r2,#0x28]|add r3,r3,r2|add r0,r1,#0|mov r1,#0x23|bx r3|pop {r3}
        |mov lr,r3|ldr r2,=0x0801353d|bx r2|ldr r2,=SSJ2_GATE|bx r2""",
    "hud": """push {r4,r5,r6,lr}|add r4,r0,#0|ldrb r0,[r4,#0x9]|add r0,r0,r4|ldrb r5,[r0,#0x18]|cmp r5,#0xc
        |bne +0x36|ldrb r0,[r4,#0x8]|cmp r0,#0x17|beq +0x1e|add r0,r4,#0|bl ZPLUS_OK|cmp r2,#0x0|beq +0x36
        |lsl r0,r5,#4|ldr r1,=0x081d9900|add r6,r0,r1|ldr r1,[r6,#0x8]|add r0,r4,#0|bl STUB_R1|ldr r1,=ICON_OK
        |cmp r0,#0x0|bne +0x40|ldr r1,=ICON_DIM|b +0x40|add r0,r4,#0|ldr r1,=SSJ2_HUD|bl STUB_R1
        |pop {r4,r5,r6,pc}|add r0,r1,#0|pop {r4,r5,r6,pc}""",
    "stub_r1": "bx r1",
}

POWER_UP, REVERT = 9, 21
VEG_SSJ_SET, VEG_BASE_SET = 140, 137
TRUNKS_SSJ_SET, TRUNKS_BASE_SET = 133, 132     # the next pair in the family, and a legal borrow today
NULL_ANIM9_SETS = (133, 61, 104)               # Trunks, Goku, Piccolo: this module must NOT touch them


def _px(x: int, y: int) -> int:
    return (y // 8) * 256 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)


def assert_step_set_can_power_up(case, rom, from_set, anim=POWER_UP):
    """The prerequisite a Super Saiyan to Super Saiyan step needs on the set it steps FROM.

    Reusable for the rest of the family: Trunks steps from 133, Goku from 61, Piccolo from 104. The
    record lookup indexes the row by animation number with no existence test (bible B0041), so a row
    of zeros is followed as a record list and the game crashes.
    """
    at, ptrs = vegeta_zplus.anim_row(rom, from_set, anim)
    case.assertEqual(len(ptrs), 4, from_set)
    case.assertTrue(all(ptrs), f"set {from_set} animation {anim} row at rom:0x{at:X} is {ptrs}")
    for d, word in enumerate(ptrs):
        rec = read_record(rom, word - ROM_BASE)
        case.assertTrue(rec["w"] and rec["h"], (from_set, d))
        case.assertIsNotNone(rec["hdr"], (from_set, d))


_CACHE = {}


def built() -> dict:
    """{"before": the dev master, "rom": after vegeta_zplus, "notes": its notes, "ssj2": ssj2_form's}."""
    if _CACHE:
        return _CACHE
    rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(log2_build.DEV_LIST))
    before = bytes(rom)
    vegeta_zplus.apply(rom, alloc)
    _CACHE.update(before=before, rom=bytes(rom), notes=alloc.notes["vegeta_zplus"],
                  ssj2=alloc.notes["ssj2_form"], npc_gi=alloc.notes["npc_gi"], all_notes=alloc.notes)
    return _CACHE


def block_of(rom: bytes) -> int:
    return u32(rom, BLOCK_LITERAL) - ROM_BASE


def words_naming(rom: bytes, address: int) -> list:
    want = struct.pack("<I", address)
    return [off for off in range(0, len(rom) - 3, 4) if rom[off:off + 4] == want]


def normalized(rom: bytes, notes: dict, name: str, count: int) -> list:
    """Disassemble a new routine; local targets become +offset, known addresses become names."""
    start = notes[name] + ROM_BASE
    names = {notes["zplus_ok"] + ROM_BASE: "ZPLUS_OK", notes["stub_r1"] + ROM_BASE: "STUB_R1",
             notes["zplus"] + ROM_BASE: "ICON_OK", notes["zplus_dim"] + ROM_BASE: "ICON_DIM",
             u32(_CACHE["before"], ABILITY_12_ACTION): "SSJ2_GATE", u32(_CACHE["before"], HUD_LITERAL): "SSJ2_HUD"}
    end = start + 2 * count + 4

    def sub(m):
        v = int(m[0], 16)
        if v in names:
            return names[v]
        return f"+{v - start:#x}" if start <= v < end and m.string.startswith("b") else m[0]
    return [re.sub(r"0x[0-9a-f]+", sub, t) for _, t in listing(rom, start, count)]


class VegetaZplusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes, cls.ssj2 = b["before"], b["rom"], b["notes"], b["ssj2"]

    # ===== the brief's four minimums =====

    def test_entry_11_transforms_into_the_new_entry(self):
        e11 = entry_of(self.rom, VEG_SSJ)
        self.assertEqual((e11[4], e11[5]), (ZPLUS, VEG_BASE))
        self.assertEqual(run_gate(self.rom, VEG_SSJ, True, STEP_EP)[0], "message")

    def test_the_new_entry_reverts_to_entry_8(self):
        e23 = entry_of(self.rom, ZPLUS)
        self.assertEqual((e23[0], e23[1], e23[2], e23[5]), (1, ZPLUS_SET, ZPLUS_PORTRAIT, VEG_BASE))
        self.assertEqual(entry_of(self.rom, VEG_BASE)[0], 0)          # the revert target is a base form

    def test_the_new_entry_carries_the_ascended_form_object(self):
        self.assertEqual(u32(entry_of(self.rom, ZPLUS), 0x10), ASCENDED)
        self.assertEqual(u32(entry_of(self.rom, ASCENDED_ENTRY), 0x10), ASCENDED)
        self.assertEqual(u32(entry_of(self.rom, VEG_SSJ), 0x10), ORDINARY)
        zplus, ascended = read_form(self.rom, ZPLUS), read_form(self.rom, ASCENDED_ENTRY)
        self.assertEqual((zplus.str_bonus, zplus.pow_bonus, zplus.end_bonus, zplus.flat), (15, 10, 15, False))
        self.assertEqual(zplus.methods, ascended.methods)

    def test_portrait_122_decodes_to_the_owners_pixels(self):
        palette = at.load_palette()
        want = at.png_pixels(PNG, at.obj_palette(self.rom, palette), at.allowed_indices(self.rom, palette))
        block = block_of(self.rom)
        header, pixels = at.live_frame(self.rom, block, ZPLUS_PORTRAIT)
        self.assertEqual(header, self.notes["frame"])
        self.assertEqual(pixels, want)
        self.assertEqual(u32(entry_of(self.rom, ZPLUS), 0) >> 16 & 0xFF, ZPLUS_PORTRAIT)
        self.assertLessEqual(len(set(want)), at.MAX_COLORS)

    # ===== no gate: Z+ is available whenever Z is =====

    def test_the_step_needs_no_story_flag(self):
        for flag in (True, False):
            self.assertEqual(run_gate(self.rom, VEG_SSJ, flag, STEP_EP)[0], "message", flag)
            self.assertEqual(run_gate(self.rom, VEG_SSJ, flag, 0x7FFF)[0], "message", flag)

    def test_the_step_costs_the_same_ep_as_gohans(self):
        for ep in (STEP_EP - 1, 0, -1):
            self.assertEqual(run_gate(self.rom, VEG_SSJ, True, ep)[0], "vanilla", ep)

    def test_zplus_always_reverts(self):
        for flag in (True, False):
            for ep in (-1, 0, 9, 10, 100, 0x7FFF):
                self.assertEqual(run_gate(self.rom, ZPLUS, flag, ep)[0], "vanilla", (flag, ep))

    def test_gohans_step_is_untouched(self):
        for flag, ep, want in ((True, 10, "message"), (False, 100, "vanilla"), (True, 9, "vanilla")):
            self.assertEqual(run_gate(self.rom, GOHAN_SSJ, flag, ep)[0], want, (flag, ep))
        self.assertEqual(run_gate(self.rom, GOHAN_SSJ2, True, 100)[0], "vanilla")
        self.assertEqual(entry_of(self.rom, GOHAN_SSJ), entry_of(self.before, GOHAN_SSJ))
        self.assertEqual(entry_of(self.rom, GOHAN_SSJ2), entry_of(self.before, GOHAN_SSJ2))

    def test_the_gate_keeps_lr_sp_and_r4_to_r7(self):
        for args, want in (((VEG_SSJ, False, 10), "message"), ((ZPLUS, True, 100), "vanilla"),
                           ((GOHAN_SSJ, True, 10), "message"), ((VEG_BASE, True, 100), "vanilla")):
            exit_, cpu = run_gate(self.rom, *args)
            self.assertEqual(exit_, want, args)
            self.assertEqual(cpu.r[13], 0x03007F00, args)
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], args)

    # ===== the HUD icon =====

    def test_hud_shows_zplus_in_zplus_and_when_b_steps_up(self):
        for entry in (ZPLUS, VEG_SSJ):
            for flag in (True, False):
                for test, key in ((1, "zplus"), (0, "zplus_dim")):
                    self.assertEqual(run_hud(self.rom, entry, flag, 100, test=test)[0],
                                     self.notes[key] + ROM_BASE, (entry, flag, test))

    def test_hud_shows_the_vanilla_icon_in_super_vegeta_with_no_ki(self):
        for ep in (9, 0, -1):
            for test in (1, 0):
                self.assertEqual(run_hud(self.rom, VEG_SSJ, True, ep, test=test)[0],
                                 vanilla_icon(self.rom, 12, test), (ep, test))

    def test_hud_never_shows_the_z2_icon_for_vegeta(self):
        for entry in (8, 9, 10, 11, ZPLUS):
            for flag in (True, False):
                for ep in (-1, 10, 100):
                    icon = run_hud(self.rom, entry, flag, ep)[0]
                    self.assertNotIn(icon, (self.ssj2["z2"] + ROM_BASE, self.ssj2["z2_dim"] + ROM_BASE),
                                     (entry, flag, ep))

    def test_hud_keeps_gohans_z2_icon(self):
        for entry in (GOHAN_SSJ, GOHAN_SSJ2):
            for test, key in ((1, "z2"), (0, "z2_dim")):
                self.assertEqual(run_hud(self.rom, entry, True, 100, test=test)[0],
                                 self.ssj2[key] + ROM_BASE, (entry, test))
        self.assertEqual(run_hud(self.rom, GOHAN_SSJ, False, 100)[0], vanilla_icon(self.rom, 12, 1))

    def test_hud_vanilla_for_other_abilities(self):
        for ability in (a for a in range(14) if a != 12):
            for entry in (VEG_SSJ, ZPLUS, GOHAN_SSJ2):
                for test in (1, 0):
                    self.assertEqual(run_hud(self.rom, entry, True, 100, ability, test)[0],
                                     vanilla_icon(self.rom, ability, test), (ability, entry, test))

    def test_hud_icon_never_disagrees_with_b(self):
        """Z+ exactly when B steps up to it or reverts out of it, which is ssj2_form's rule for Z2."""
        for entry in range(ENTRIES):
            for flag in (True, False):
                for ep in (-1, 0, 9, 10, 100):
                    steps = run_gate(self.rom, entry, flag, ep)[0] == "message"
                    mine = run_hud(self.rom, entry, flag, ep)[0] == self.notes["zplus"] + ROM_BASE
                    self.assertEqual(mine, (steps and entry == VEG_SSJ) or entry == ZPLUS, (entry, flag, ep))

    def test_hud_keeps_r4_to_r7_and_sp(self):
        for entry in (VEG_SSJ, ZPLUS, GOHAN_SSJ, VEG_BASE):
            _, cpu = run_hud(self.rom, entry, True, 100)
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], entry)
            self.assertEqual(cpu.r[13], 0x03007F00, entry)

    # ===== the power-up animation the step needs (the v1 crash) =====

    def test_the_set_the_step_comes_from_can_power_up(self):
        """v1 crashed here: set 140's anim 9 row was four null pointers, and the record lookup
        @0x0800775A indexes the row by number with no existence test (bible B0041)."""
        assert_step_set_can_power_up(self, self.rom, VEG_SSJ_SET)
        self.assertEqual(vegeta_zplus.anim_row(self.before, VEG_SSJ_SET, POWER_UP)[1], (0, 0, 0, 0))

    def test_the_zplus_set_itself_can_power_up(self):
        """Set 139 is where Vegeta STANDS in Z+. A power-up played there reads its OWN anim 9 row, so a
        null row crashes exactly as set 140's did, whatever sends the power-up."""
        assert_step_set_can_power_up(self, self.rom, ZPLUS_SET)
        self.assertEqual(vegeta_zplus.anim_row(self.before, ZPLUS_SET, POWER_UP)[1], (0, 0, 0, 0))

    def test_both_borrowed_rows_are_base_vegetas_own_list(self):
        donor = vegeta_zplus.anim_row(self.rom, VEG_BASE_SET, POWER_UP)[1]
        self.assertEqual(len(self.notes["anim_rows"]), 2)
        for note, sid in zip(self.notes["anim_rows"], (VEG_SSJ_SET, ZPLUS_SET)):
            at, after = vegeta_zplus.anim_row(self.rom, sid, POWER_UP)
            self.assertEqual(after, donor, sid)
            self.assertEqual(note, {"row": at, "from": VEG_BASE_SET, "anim": POWER_UP,
                                    "ptrs": list(donor)}, sid)
        self.assertEqual(vegeta_zplus.anim_row(self.rom, VEG_BASE_SET, POWER_UP),
                         vegeta_zplus.anim_row(self.before, VEG_BASE_SET, POWER_UP))   # the donor is untouched

    def test_the_borrowed_frames_match_the_geometry_the_set_already_draws(self):
        """Same OBJ slot and the same record shape as set 140's own revert row, or the frames tear."""
        for sid in (VEG_SSJ_SET, ZPLUS_SET, VEG_BASE_SET):
            self.assertEqual(read_set(self.rom, vegeta_zplus.set_at(self.rom, sid))["slot"], 0x400, sid)
        shapes = set()
        for row in (vegeta_zplus.anim_row(self.rom, VEG_SSJ_SET, POWER_UP)[1],
                    vegeta_zplus.anim_row(self.rom, VEG_SSJ_SET, REVERT)[1],
                    vegeta_zplus.anim_row(self.rom, ZPLUS_SET, POWER_UP)[1],
                    vegeta_zplus.anim_row(self.rom, ZPLUS_SET, REVERT)[1]):
            for word in row:
                r = read_record(self.rom, word - ROM_BASE)
                shapes.add((r["w"], r["h"], r["dx"], r["dy"]))
        self.assertEqual(shapes, {(32, 32, -8, -24)})

    def test_only_vegetas_set_is_given_a_power_up(self):
        """The owner chose for the family, but this module wires Vegeta only."""
        for sid in NULL_ANIM9_SETS:
            self.assertEqual(vegeta_zplus.anim_row(self.rom, sid, POWER_UP)[1], (0, 0, 0, 0), sid)
            self.assertEqual(vegeta_zplus.anim_row(self.rom, sid, POWER_UP),
                             vegeta_zplus.anim_row(self.before, sid, POWER_UP), sid)

    def test_the_helper_refuses_a_borrow_that_would_not_work(self):
        """Each guard on its own, on Trunks' pair, which this module leaves alone. The slot and geometry
        guards need a mutated copy, because the sets measured are all slot 0x400 with 32x32 records at
        dx -8 dy -24, so no real pair can trip them."""
        rom = bytearray(self.rom)
        self.assertEqual(vegeta_zplus.plan_anim_borrow(rom, TRUNKS_SSJ_SET, TRUNKS_BASE_SET,
                                                       POWER_UP)["from"], TRUNKS_BASE_SET)  # legal today
        for sid in (VEG_SSJ_SET, ZPLUS_SET):                               # both were given their row
            with self.assertRaisesRegex(ValueError, "nothing to borrow"):
                vegeta_zplus.plan_anim_borrow(rom, sid, VEG_BASE_SET, POWER_UP)
        with self.assertRaisesRegex(ValueError, "nothing to lend"):        # Goku's super set is null too
            vegeta_zplus.plan_anim_borrow(rom, 61, TRUNKS_SSJ_SET, POWER_UP)
        with self.assertRaisesRegex(ValueError, "past the table"):         # set 137 holds rows 0 to 20
            vegeta_zplus.anim_row(rom, VEG_BASE_SET, REVERT)
        struct.pack_into("<H", rom, vegeta_zplus.set_at(rom, TRUNKS_SSJ_SET), 0x1000)
        with self.assertRaisesRegex(ValueError, "the OBJ buffer would not fit"):
            vegeta_zplus.plan_anim_borrow(rom, TRUNKS_SSJ_SET, TRUNKS_BASE_SET, POWER_UP)
        rom = bytearray(self.rom)
        at = vegeta_zplus.anim_row(rom, TRUNKS_SSJ_SET, REVERT)[1][0] - ROM_BASE
        rom[at + 2] = 16                                                   # the record's width
        with self.assertRaisesRegex(ValueError, "would not line up"):
            vegeta_zplus.plan_anim_borrow(rom, TRUNKS_SSJ_SET, TRUNKS_BASE_SET, POWER_UP)

    def test_the_animation_rows_are_the_only_extra_base_rom_sites(self):
        for note in self.notes["anim_rows"]:
            row = note["row"]
            self.assertTrue(row < log2_build.BASE_SIZE)
            self.assertEqual(self.before[row:row + 16], bytes(16))

    # ===== the relocated table and the portrait block =====

    def test_the_table_moved_and_every_namer_followed(self):
        old, new = table_of(self.before), table_of(self.rom)
        self.assertNotEqual(old, new)
        self.assertEqual(new, self.notes["table"])
        self.assertEqual(sorted(words_naming(self.before, old + ROM_BASE)),
                         sorted(TABLE_LITERALS + MODULE_LITERALS))
        self.assertEqual(words_naming(self.rom, old + ROM_BASE), [])
        self.assertEqual(sorted(words_naming(self.rom, new + ROM_BASE)),
                         sorted(TABLE_LITERALS + MODULE_LITERALS))

    def test_the_new_table_copies_the_live_one(self):
        old, new = table_of(self.before), table_of(self.rom)
        copied = bytearray(self.rom[new:new + ENTRY * (ENTRIES - 1)])
        self.assertEqual(copied[ENTRY * VEG_SSJ + 4], ZPLUS)
        copied[ENTRY * VEG_SSJ + 4] = VEG_BASE
        self.assertEqual(bytes(copied), self.before[old:old + ENTRY * (ENTRIES - 1)])
        self.assertEqual(self.rom[old:old + ENTRY * (ENTRIES - 1)],
                         self.before[old:old + ENTRY * (ENTRIES - 1)])   # the old table is left as it is

    def test_the_new_entry_copies_entry_11_apart_from_its_own_fields(self):
        e11, e23 = entry_of(self.rom, VEG_SSJ), entry_of(self.rom, ZPLUS)
        self.assertEqual(e23[3], e11[3])            # the status twin id, which status_portrait does not read
        self.assertEqual(e23[6:0x10], e11[6:0x10])

    def test_the_portrait_block_grew_by_one_id(self):
        old, new = block_of(self.before), block_of(self.rom)
        self.assertNotEqual(old, new)
        self.assertEqual(new, self.notes["block"])
        self.assertEqual(self.rom[new:new + 4 + 4 * BLOCK_IDS], self.before[old:old + 4 + 4 * BLOCK_IDS])
        self.assertEqual(sorted(words_naming(self.rom, new + ROM_BASE)), sorted(self.notes["block_namers"]))
        self.assertEqual(words_naming(self.rom, old + ROM_BASE), [])

    def test_npc_gis_armor_portrait_is_untouched(self):
        """Id 121 is npc_gi's armor copy for the two chamber exit lines, so Z+ took the next id."""
        for record in PRE_CONTROL_RECORDS:
            self.assertEqual(self.rom[record + 3], REF_ID)
            self.assertEqual(self.rom[record:record + 4], self.before[record:record + 4])
        for rom in (self.before, self.rom):
            self.assertEqual(at.live_frame(rom, block_of(rom), REF_ID), at.live_frame(rom, block_of(rom), 59))

    # ===== placement, art and the hooks =====

    def test_new_data_is_in_the_expansion_area(self):
        for key in ("table", "block", "zplus", "zplus_dim", "code"):
            self.assertTrue(EXPANSION[0] <= self.notes[key] < EXPANSION[1], key)
        self.assertTrue(ART_REGION[0] <= self.notes["frame"] < ART_REGION[1])

    def test_the_icons_are_in_the_rom_word_aligned(self):
        for key in ("zplus", "zplus_dim"):
            self.assertEqual(self.notes[key] % 4, 0, key)   # the HUD copies it with 32-bit DMA (@0x08008DA4)
        self.assertNotEqual(self.rom[self.notes["zplus"]:self.notes["zplus"] + 0x200],
                            self.rom[self.notes["zplus_dim"]:self.notes["zplus_dim"] + 0x200])

    def test_each_icon_is_the_live_z_icon_with_the_zplus_picture(self):
        """bf_hud moved every icon picture to the Buu's Fury layout before this module ran, so the art file
        is pasted into the live icon instead of being written in raw."""
        for key, name, z in zip(("zplus", "zplus_dim"), ICONS, Z_ICONS):
            art, live = (log_paths.ART / name).read_bytes(), self.rom[z:z + 0x200]
            built_icon = self.rom[self.notes[key]:self.notes[key] + 0x200]
            self.assertNotEqual(built_icon, art, name)
            self.assertNotEqual(built_icon, live, name)
            for y in range(16):
                for x in range(32):
                    want = art[_px(x + 10, y)] if 3 <= x <= 18 and 2 <= y <= 9 else live[_px(x, y)]
                    self.assertEqual(built_icon[_px(x, y)], want, (name, x, y))

    def test_the_icons_use_existing_obj_palette_indices_only(self):
        """Each Z+ icon is the live Z icon with a glyph, so it adds one index and invents no color."""
        for key, z, glyph in zip(("zplus", "zplus_dim"), Z_ICONS, (191, 23)):
            used = set(self.rom[self.notes[key]:self.notes[key] + 0x200])
            self.assertFalse(used - set(self.rom[z:z + 0x200]) - {glyph}, key)
            self.assertIn(glyph, used, key)

    def test_the_two_hooks_moved_from_ssj2_forms_routines(self):
        self.assertEqual(u32(self.before, ABILITY_12_ACTION), self.ssj2["gate"] + ROM_BASE + 1)
        self.assertEqual(u32(self.before, HUD_LITERAL), self.ssj2["hud"] + ROM_BASE + 1)
        self.assertEqual(u32(self.rom, ABILITY_12_ACTION), self.notes["gate"] + ROM_BASE + 1)
        self.assertEqual(u32(self.rom, HUD_LITERAL), self.notes["hud"] + ROM_BASE + 1)

    def test_the_base_8mb_differs_only_at_the_known_sites(self):
        sites = ({off: 4 for off in TABLE_LITERALS}
                 | {ABILITY_12_ACTION: 4, HUD_LITERAL: 4, BLOCK_LITERAL: 4}
                 | {note["row"]: 16 for note in self.notes["anim_rows"]})
        inside = {o for off, n in sites.items() for o in range(off, off + n)}
        diff = [i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]]
        self.assertTrue(diff)
        self.assertFalse([hex(i) for i in diff if i not in inside])

    def test_the_new_routines_disassemble_as_expected(self):
        for name, text in EXPECTED.items():
            want = [t.strip() for t in text.split("|")]
            self.assertEqual(normalized(self.rom, self.notes, name, len(want)), want, name)

    # ===== the trial list and failing closed =====

    def test_the_trial_list_is_the_dev_master_plus_this_module(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["vegeta_zplus"])
        for master in (log2_build.BUILD_LIST, log2_build.DEV_LIST,
                       log2_build.BUILD_LIST.parent / "build_list_core.txt"):
            self.assertNotIn("vegeta_zplus", master.read_text(encoding="utf-8"), master.name)

    def test_apply_fails_closed(self):
        notes = built()["all_notes"]
        for off, junk in ((TABLE_LITERALS[5], b"\0\0\0\0"), (ABILITY_12_ACTION, b"\1\0\0\0"),
                          (HUD_LITERAL, b"\0\0\0\0"), (BLOCK_LITERAL, b"\0\0\0\0")):
            rom = bytearray(self.before)
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0x800000, 0x100000)])
            alloc.notes.update({k: notes[k] for k in ("ssj2_form", "npc_gi", "art_inject", "bf_hud")})
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                vegeta_zplus.apply(rom, alloc)
            self.assertEqual(bytes(rom), before, f"rom:0x{off:X}")

    def test_it_refuses_to_run_out_of_order_or_twice(self):
        notes = built()["all_notes"]
        rom = bytearray(self.before)
        with self.assertRaisesRegex(ValueError, "run them first"):
            vegeta_zplus.apply(rom, Allocator(len(rom), [(0x800000, 0x100000)]))
        alloc = Allocator(len(rom), [(0x800000, 0x100000)])
        alloc.notes.update({k: notes[k] for k in ("ssj2_form", "npc_gi", "art_inject", "bf_hud")})
        alloc.notes["vegeta_zplus"] = {}
        with self.assertRaisesRegex(ValueError, "already ran"):
            vegeta_zplus.apply(rom, alloc)
        self.assertEqual(bytes(rom), self.before)

    def test_a_stray_namer_of_the_table_raises(self):
        rom = bytearray(self.before)
        stray = 0x7FFFF0                                  # base ROM, not a known literal and not allocated
        rom[stray:stray + 4] = struct.pack("<I", table_of(self.before) + ROM_BASE)
        allowed = [(off, 4) for off in TABLE_LITERALS + MODULE_LITERALS]
        self.assertEqual(vegeta_zplus.namers(self.before, table_of(self.before) + ROM_BASE, allowed),
                         sorted(TABLE_LITERALS + MODULE_LITERALS))
        with self.assertRaisesRegex(ValueError, f"rom:0x{stray:X}"):
            vegeta_zplus.namers(bytes(rom), table_of(self.before) + ROM_BASE, allowed)

    def test_the_owners_png_is_the_one_the_patch_reads(self):
        self.assertTrue(PNG.is_file(), PNG)
        self.assertEqual(Path(vegeta_zplus.PORTRAIT_PNG), PNG)
        self.assertNotIn(ZPLUS_PORTRAIT, at.load_portraits())      # not wired through the normal route


if __name__ == "__main__":
    unittest.main()
