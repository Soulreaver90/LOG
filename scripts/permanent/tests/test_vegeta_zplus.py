r"""
test_vegeta_zplus.py - Tests for patches.vegeta_zplus (trial 2026-11-12): Vegeta's Z+ grade, gated on the
                       Time Chamber exit the game already has, with no flag and no unlock code.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_vegeta_zplus.py -v
Builds the dev master in memory once, keeps it as "before", then applies vegeta_zplus to the same ROM, so
every test sees both sides and the notes. The gate and the HUD hook are run as thumb_dis text in
test_ssj2's Thumb interpreter over a scripted record, so the icon tests check behavior, not code text.
Expected values are restated from docs\tasks\2026-11-12-zplus-unlock\brief.md and the live table bytes, never
imported from the patch module.

The design under test:

    before the chamber   base entry 8   Z = entry 11 (set 140, +10)   Z+ unreachable
    after the chamber    base entry 9   Z = entry 23 (set 140, +10)   Z+ = entry 10 (set 139, +15)
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
from scene import scene_lib as sl
from tests.test_ssj2 import (ABILITY_12_ACTION, ENTRY, HUD_LITERAL, entry_of, read_form, run_gate, run_hud,
                             table_of, u32, vanilla_icon)

# ===== constants (brief, live table bytes) =====
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_vegeta_zplus.txt"
ENTRIES = 24                                   # 23 live entries plus the new one
PRE_BASE, POST_BASE, ZPLUS, PRE_Z, POST_Z = 8, 9, 10, 11, 23
VEGETA_ENTRIES = (PRE_BASE, POST_BASE, ZPLUS, PRE_Z, POST_Z)
GOHAN_SSJ, GOHAN_SSJ2 = 5, 22
ASCENDED, ORDINARY = 0x030021E8, 0x030021EC
ZPLUS_SET, Z_SET, ZPLUS_PORTRAIT, Z_PORTRAIT, REF_ID = 139, 140, 122, 107, 121
Z_ICONS = (0x6DAE7C, 0x6DB07C)                 # ability 12's icon pair, usable and dim
STEP_EP = 10
BLOCK_LITERAL, BLOCK_IDS = 0xBE10, 122
PRE_CONTROL_RECORDS = (0x3DB930, 0x3DBABC)     # npc_gi's two chamber exit lines, which own portrait id 121
FLAG_195_WORD = 0x03000F5C                     # ssj2_form's story flag byte: this module must not read it
EXIT_TABLE_WORD = 0x3DE774                     # scene table word of the chamber exit record (seq 33)
EXIT_VEGETA = bytes.fromhex("1d02048214" "0249")   # ext 73 (2, 138): Vegeta to entry 9. THE unlock
EXIT_TRUNKS = bytes.fromhex("1d02068202" "0249")   # ext 73 (3, 129): Trunks' mirror, 7 bytes earlier
EXIT_UNDO = bytes.fromhex("1d02048212" "0249")     # ext 73 (2, 137): the only one, and it is BEFORE the chamber
TABLE_LITERALS = (0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050,
                  0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474)
MODULE_LITERALS = (0x88E3B4, 0x894978, 0x89A9B4, 0x90A250, 0x90A3E0)   # ssj2_form, status_bonus, fullpower_ssj,
EXPANSION = (0x800000, 0xF00000)                                       # bf_ki_pool, fullpower_hud
ART_REGION = (0xF00000, 0x1000000)
ICONS = ("hud_zplus_usable.bin", "hud_zplus_dim.bin")
PNG = log_paths.ART_TABLES / "portraits" / "122_vegeta_grade2.png"

EXPECTED = {
    "zplus_ok": """ldrb r2,[r0,#0x8]|cmp r2,#0x17|bne +0x12|mov r3,#0x4|ldsh r2,[r0,r3]|cmp r2,#0xa|blt +0x12
        |mov r2,#0x1|bx lr|mov r2,#0x0|bx lr""",
    "gate": """push {lr}|ldrb r2,[r0,#0x8]|cmp r2,#0xa|beq +0x20|bl ZPLUS_OK|pop {r3}|mov lr,r3|cmp r2,#0x0
        |beq +0x28|ldr r2,[r1,#0x0]|ldr r3,[r2,#0x28]|add r3,r3,r2|add r0,r1,#0|mov r1,#0x23|bx r3|pop {r3}
        |mov lr,r3|ldr r2,=0x0801353d|bx r2|ldr r2,=SSJ2_GATE|bx r2""",
    "hud": """push {r4,r5,r6,lr}|add r4,r0,#0|ldrb r0,[r4,#0x9]|add r0,r0,r4|ldrb r5,[r0,#0x18]|cmp r5,#0xc
        |bne +0x36|ldrb r0,[r4,#0x8]|cmp r0,#0xa|beq +0x1e|add r0,r4,#0|bl ZPLUS_OK|cmp r2,#0x0|beq +0x36
        |lsl r0,r5,#4|ldr r1,=0x081d9900|add r6,r0,r1|ldr r1,[r6,#0x8]|add r0,r4,#0|bl STUB_R1|ldr r1,=ICON_OK
        |cmp r0,#0x0|bne +0x40|ldr r1,=ICON_DIM|b +0x40|add r0,r4,#0|ldr r1,=SSJ2_HUD|bl STUB_R1
        |pop {r4,r5,r6,pc}|add r0,r1,#0|pop {r4,r5,r6,pc}""",
    "stub_r1": "bx r1",
}

POWER_UP, REVERT = 9, 21
CHAIN_SETS = (137, 138, 140, 139)              # base pre, base post, Z, Z+: every set the chain walks
BORROWED_SETS = (140, 139)                     # the two that have no anim 9 of their own
OWN_ANIM9_SETS = (137, 138)                    # the two that carry one in vanilla
VEG_BASE_SET = 137
TRUNKS_SSJ_SET, TRUNKS_BASE_SET = 133, 132     # the next pair in the family, and a legal borrow today
NULL_ANIM9_SETS = (133, 61, 104)               # Trunks, Goku, Piccolo: this module must NOT touch them


def _px(x: int, y: int) -> int:
    return (y // 8) * 256 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)


def assert_step_set_can_power_up(case, rom, set_id, anim=POWER_UP):
    """The prerequisite a transform INTO or OUT OF a set needs on that set.

    Reusable for the rest of the family: Trunks steps from 133, Goku from 61, Piccolo from 104. The
    record lookup indexes the row by animation number with no existence test (bible B0041), so a row
    of zeros is followed as a record list and the game crashes.
    """
    row, ptrs = vegeta_zplus.anim_row(rom, set_id, anim)
    case.assertEqual(len(ptrs), 4, set_id)
    case.assertTrue(all(ptrs), f"set {set_id} animation {anim} row at rom:0x{row:X} is {ptrs}")
    for d, word in enumerate(ptrs):
        rec = read_record(rom, word - ROM_BASE)
        case.assertTrue(rec["w"] and rec["h"], (set_id, d))
        case.assertIsNotNone(rec["hdr"], (set_id, d))


def reachable(rom: bytes, start: int, flag: bool, ep: int) -> set:
    """Every appearance entry B can reach from `start`, walked the way the game walks it.

    A base entry (flag bit 0 clear) transforms to its +4, which is what the vanilla action does. A
    transformed entry steps to its +4 only when the ability 12 action sends message 0x23; otherwise B
    reverts, which reaches nothing the walk has not already seen.
    """
    seen, queue = {start}, [start]
    while queue:
        here = queue.pop()
        entry = entry_of(rom, here)
        steps = not entry[0] & 1 or run_gate(rom, here, flag, ep)[0] == "message"
        if steps and entry[4] not in seen:
            seen.add(entry[4])
            queue.append(entry[4])
    return seen


def live_exit_record(rom: bytes) -> tuple:
    """(offset, bytes) of the chamber exit record the game runs, through its scene table word.

    Never read rom:0x3DE620 directly: fullpower_ssj relocates that record and repoints this word, so
    the vanilla address holds a dead copy in every build of the two masters.
    """
    at_ = u32(rom, EXIT_TABLE_WORD) - ROM_BASE
    return at_, bytes(rom[at_:sl.record_end(rom, at_)])


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

    # ===== the gate is the chamber, and it is data (brief "Done means" 1) =====

    def test_before_the_chamber_he_reaches_z_and_stops(self):
        """Entry 11's +4 is still 8, so B out of pre-chamber Z reverts. Z+ is not in that chain at all."""
        for flag in (True, False):
            self.assertEqual(reachable(self.rom, PRE_BASE, flag, 0x7FFF), {PRE_BASE, PRE_Z}, flag)
        self.assertEqual(entry_of(self.rom, PRE_BASE)[4], PRE_Z)
        self.assertEqual(entry_of(self.rom, PRE_Z)[4], PRE_BASE)

    def test_after_the_chamber_he_reaches_z_then_zplus(self):
        for flag in (True, False):
            self.assertEqual(reachable(self.rom, POST_BASE, flag, 0x7FFF), {POST_BASE, POST_Z, ZPLUS}, flag)
        self.assertEqual(entry_of(self.rom, POST_BASE)[4], POST_Z)
        self.assertEqual(entry_of(self.rom, POST_Z)[4], ZPLUS)

    def test_the_two_chains_share_nothing(self):
        pre = reachable(self.rom, PRE_BASE, True, 0x7FFF)
        post = reachable(self.rom, POST_BASE, True, 0x7FFF)
        self.assertEqual(pre & post, set())

    def test_entry_11_is_byte_identical_to_the_dev_master(self):
        """Pre-chamber Z is the gate, and the gate is one entry this module does not write."""
        self.assertEqual(entry_of(self.rom, PRE_Z), entry_of(self.before, PRE_Z))
        self.assertEqual((entry_of(self.rom, PRE_Z)[4], entry_of(self.rom, PRE_Z)[5]), (PRE_BASE, PRE_BASE))

    # ===== no flag, no ability bit, no unlock code (brief "Done means" 2) =====

    def test_the_live_chamber_exit_record_still_holds_the_vanilla_unlock(self):
        at_, body = live_exit_record(self.rom)
        self.assertEqual(body.count(EXIT_VEGETA), 1, f"rom:0x{at_:X}")
        self.assertEqual(body.count(EXIT_TRUNKS), 1, f"rom:0x{at_:X}")
        self.assertLess(body.index(EXIT_TRUNKS), body.index(EXIT_VEGETA))   # Trunks first, 7 bytes earlier

    def test_this_module_writes_nothing_in_the_chamber_exit_record(self):
        self.assertEqual(live_exit_record(self.rom), live_exit_record(self.before))

    def test_the_vanilla_ops_are_where_the_brief_measured_them(self):
        """The base ROM addresses the brief names, and the count that makes the unlock one way only.
        In a BUILD these are a dead copy, because fullpower_ssj relocates the record, so the test
        above is the one that proves what the game runs."""
        base = log2_build.BASE.read_bytes()
        self.assertEqual(base[0x3DE6BB:0x3DE6BB + len(EXIT_VEGETA)], EXIT_VEGETA)
        self.assertEqual(base[0x3DE6B4:0x3DE6B4 + len(EXIT_TRUNKS)], EXIT_TRUNKS)
        self.assertEqual(base.count(EXIT_VEGETA), 1)
        self.assertEqual(base.count(EXIT_TRUNKS), 1)
        self.assertEqual(base[0x3E778B:0x3E778B + len(EXIT_UNDO)], EXIT_UNDO)
        self.assertEqual(base.count(EXIT_UNDO), 1)          # Android 16, BEFORE the chamber: nothing undoes it

    def test_the_module_reads_no_story_flag(self):
        """ssj2_form's step_ok reads flag 195. Nothing this module adds may name that byte."""
        self.assertEqual(words_naming(self.rom, FLAG_195_WORD), words_naming(self.before, FLAG_195_WORD))

    def test_the_step_gives_the_same_answer_with_the_flag_set_and_clear(self):
        for entry in VEGETA_ENTRIES:
            for ep in (-1, 0, 9, 10, 100, 0x7FFF):
                self.assertEqual(run_gate(self.rom, entry, True, ep)[0],
                                 run_gate(self.rom, entry, False, ep)[0], (entry, ep))

    # ===== the three entries the design writes (brief "Done means" 3) =====

    def test_entry_10_is_zplus(self):
        e10 = entry_of(self.rom, ZPLUS)
        self.assertEqual((e10[0], e10[1], e10[2], e10[5]), (1, ZPLUS_SET, ZPLUS_PORTRAIT, POST_BASE))
        self.assertEqual(u32(e10, 0x10), ASCENDED)
        form = read_form(self.rom, ZPLUS)
        self.assertEqual((form.str_bonus, form.pow_bonus, form.end_bonus, form.flat), (15, 10, 15, False))

    def test_entry_10_changed_only_its_portrait(self):
        before, after = bytearray(entry_of(self.before, ZPLUS)), entry_of(self.rom, ZPLUS)
        self.assertEqual(before[2], Z_PORTRAIT)          # the vanilla Super Vegeta portrait
        before[2] = ZPLUS_PORTRAIT
        self.assertEqual(bytes(before), after)

    def test_the_new_entry_is_the_post_chamber_z(self):
        e23, e11 = entry_of(self.rom, POST_Z), entry_of(self.rom, PRE_Z)
        self.assertEqual((e23[0], e23[1], e23[2]), (1, Z_SET, Z_PORTRAIT))
        self.assertEqual((e23[4], e23[5]), (ZPLUS, POST_BASE))
        self.assertEqual(u32(e23, 0x10), ORDINARY)       # the plain Super Saiyan form: +10, and the ki pool
        self.assertEqual(read_form(self.rom, POST_Z).methods, read_form(self.rom, PRE_Z).methods)
        copied = bytearray(e23)
        copied[4], copied[5] = e11[4], e11[5]
        self.assertEqual(bytes(copied), e11)             # entry 11 in every byte but its chain

    def test_entry_9_steps_into_the_new_entry(self):
        before, after = bytearray(entry_of(self.before, POST_BASE)), entry_of(self.rom, POST_BASE)
        self.assertEqual(before[4], ZPLUS)               # vanilla sent entry 9 straight to the +15 grade
        before[4] = POST_Z
        self.assertEqual(bytes(before), after)

    def test_portrait_122_decodes_to_the_owners_pixels(self):
        palette = at.load_palette()
        want = at.png_pixels(PNG, at.obj_palette(self.rom, palette), at.allowed_indices(self.rom, palette))
        block = block_of(self.rom)
        header, pixels = at.live_frame(self.rom, block, ZPLUS_PORTRAIT)
        self.assertEqual(header, self.notes["frame"])
        self.assertEqual(pixels, want)
        self.assertEqual(entry_of(self.rom, ZPLUS)[2], ZPLUS_PORTRAIT)
        self.assertLessEqual(len(set(want)), at.MAX_COLORS)

    # ===== the step itself =====

    def test_the_step_costs_the_same_ep_as_gohans(self):
        for ep in (STEP_EP - 1, 0, -1):
            self.assertEqual(run_gate(self.rom, POST_Z, True, ep)[0], "vanilla", ep)
        for ep in (STEP_EP, 100, 0x7FFF):
            self.assertEqual(run_gate(self.rom, POST_Z, True, ep)[0], "message", ep)

    def test_pre_chamber_z_never_steps(self):
        for flag in (True, False):
            for ep in (-1, 0, 9, 10, 100, 0x7FFF):
                self.assertEqual(run_gate(self.rom, PRE_Z, flag, ep)[0], "vanilla", (flag, ep))

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
        for args, want in (((POST_Z, False, 10), "message"), ((ZPLUS, True, 100), "vanilla"),
                           ((PRE_Z, True, 100), "vanilla"), ((GOHAN_SSJ, True, 10), "message"),
                           ((PRE_BASE, True, 100), "vanilla"), ((POST_BASE, True, 100), "vanilla")):
            exit_, cpu = run_gate(self.rom, *args)
            self.assertEqual(exit_, want, args)
            self.assertEqual(cpu.r[13], 0x03007F00, args)
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], args)

    # ===== the HUD icon =====

    def test_hud_shows_zplus_in_zplus_and_when_b_steps_up(self):
        for entry in (ZPLUS, POST_Z):
            for flag in (True, False):
                for test, key in ((1, "zplus"), (0, "zplus_dim")):
                    self.assertEqual(run_hud(self.rom, entry, flag, 100, test=test)[0],
                                     self.notes[key] + ROM_BASE, (entry, flag, test))

    def test_hud_shows_the_vanilla_icon_in_pre_chamber_z(self):
        """B reverts there at any ki, so the icon must never promise a step."""
        for ep in (0x7FFF, 100, 10, 0, -1):
            for test in (1, 0):
                self.assertEqual(run_hud(self.rom, PRE_Z, True, ep, test=test)[0],
                                 vanilla_icon(self.rom, 12, test), (ep, test))

    def test_hud_shows_the_vanilla_icon_in_post_chamber_z_with_no_ki(self):
        for ep in (9, 0, -1):
            for test in (1, 0):
                self.assertEqual(run_hud(self.rom, POST_Z, True, ep, test=test)[0],
                                 vanilla_icon(self.rom, 12, test), (ep, test))

    def test_hud_never_shows_the_z2_icon_for_vegeta(self):
        for entry in VEGETA_ENTRIES:
            for flag in (True, False):
                for ep in (-1, 10, 100, 0x7FFF):
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
            for entry in (POST_Z, ZPLUS, GOHAN_SSJ2):
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
                    self.assertEqual(mine, (steps and entry == POST_Z) or entry == ZPLUS, (entry, flag, ep))

    def test_hud_keeps_r4_to_r7_and_sp(self):
        for entry in VEGETA_ENTRIES + (GOHAN_SSJ,):
            _, cpu = run_hud(self.rom, entry, True, 100)
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], entry)
            self.assertEqual(cpu.r[13], 0x03007F00, entry)

    # ===== the power-up animation every set in the chain needs (brief "Done means" 4) =====

    def test_every_set_in_the_chain_can_power_up(self):
        """The chain walks sets 137, 138, 140 and 139. A transform plays animation 9 and the record
        lookup @0x0800775A indexes the row by number with no existence test (bible B0041), so one null
        row anywhere in the chain crashes the game. 137 and 138 carry one; 140 and 139 borrow."""
        for set_id in CHAIN_SETS:
            assert_step_set_can_power_up(self, self.rom, set_id)
        for set_id in BORROWED_SETS:
            self.assertEqual(vegeta_zplus.anim_row(self.before, set_id, POWER_UP)[1], (0, 0, 0, 0), set_id)
        for set_id in OWN_ANIM9_SETS:
            self.assertEqual(vegeta_zplus.anim_row(self.before, set_id, POWER_UP),
                             vegeta_zplus.anim_row(self.rom, set_id, POWER_UP), set_id)

    def test_the_zplus_set_is_the_one_stepped_into(self):
        """v1 only stepped OUT of set 140. The design steps INTO set 139, so its row is load bearing."""
        self.assertEqual(entry_of(self.rom, ZPLUS)[1], ZPLUS_SET)
        self.assertEqual(entry_of(self.rom, POST_Z)[1], Z_SET)
        assert_step_set_can_power_up(self, self.rom, ZPLUS_SET)

    def test_both_borrowed_rows_are_base_vegetas_own_list(self):
        donor = vegeta_zplus.anim_row(self.rom, VEG_BASE_SET, POWER_UP)[1]
        self.assertEqual(len(self.notes["anim_rows"]), 2)
        for note, sid in zip(self.notes["anim_rows"], BORROWED_SETS):
            row, after = vegeta_zplus.anim_row(self.rom, sid, POWER_UP)
            self.assertEqual(after, donor, sid)
            self.assertEqual(note, {"row": row, "from": VEG_BASE_SET, "anim": POWER_UP,
                                    "ptrs": list(donor)}, sid)
        self.assertEqual(vegeta_zplus.anim_row(self.rom, VEG_BASE_SET, POWER_UP),
                         vegeta_zplus.anim_row(self.before, VEG_BASE_SET, POWER_UP))   # the donor is untouched

    def test_the_borrowed_frames_match_the_geometry_the_set_already_draws(self):
        """Same OBJ slot and the same record shape as the set's own revert row, or the frames tear."""
        for sid in CHAIN_SETS:
            self.assertEqual(read_set(self.rom, vegeta_zplus.set_at(self.rom, sid))["slot"], 0x400, sid)
        shapes = set()
        for sid in BORROWED_SETS:
            for anim in (POWER_UP, REVERT):
                for word in vegeta_zplus.anim_row(self.rom, sid, anim)[1]:
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
        for sid in BORROWED_SETS:                                          # both were given their row
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
        row = vegeta_zplus.anim_row(rom, TRUNKS_SSJ_SET, REVERT)[1][0] - ROM_BASE
        rom[row + 2] = 16                                                  # the record's width
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

    def test_the_new_table_copies_the_live_one_apart_from_the_two_edits(self):
        old, new = table_of(self.before), table_of(self.rom)
        copied = bytearray(self.rom[new:new + ENTRY * (ENTRIES - 1)])
        self.assertEqual(copied[ENTRY * POST_BASE + 4], POST_Z)
        self.assertEqual(copied[ENTRY * ZPLUS + 2], ZPLUS_PORTRAIT)
        copied[ENTRY * POST_BASE + 4], copied[ENTRY * ZPLUS + 2] = ZPLUS, Z_PORTRAIT
        self.assertEqual(bytes(copied), self.before[old:old + ENTRY * (ENTRIES - 1)])
        self.assertEqual(self.rom[old:old + ENTRY * (ENTRIES - 1)],
                         self.before[old:old + ENTRY * (ENTRIES - 1)])   # the old table is left as it is

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
        exit_at, exit_body = live_exit_record(self.before)
        unlock = exit_at + exit_body.index(EXIT_VEGETA)               # the live ext 73 (2, 138)
        for off, junk in ((TABLE_LITERALS[5], b"\0\0\0\0"), (ABILITY_12_ACTION, b"\1\0\0\0"),
                          (HUD_LITERAL, b"\0\0\0\0"), (BLOCK_LITERAL, b"\0\0\0\0"),
                          (unlock + 4, b"\x7F"),                      # one byte of the pushed set id
                          (EXIT_TABLE_WORD, b"\0\0\0\0")):            # the word that names the record
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
