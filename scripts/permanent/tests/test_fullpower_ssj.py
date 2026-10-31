r"""
test_fullpower_ssj.py - Tests for patches.fullpower_ssj (r28) and the r28 chamber test save.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_fullpower_ssj.py -v
Builds build_list.txt in memory: "before" = the list up to fullpower_ssj (the r27 bytes), "rom" = with it.
New code runs as thumb_dis text in the test_status interpreter; scripts use the test_cellgames_ssj decoder.
Expected sites and values are restated from docs\tasks\2026-10-22-r28-build\fullpower-ssj.md and r28-build-report.md,
never imported from the patch module.
"""
import copy
import struct
import unittest
from pathlib import Path

import log2_build
from rom import log2_save
import log_paths
from tests.test_cellgames_ssj import (STRUCT, PLAYER, PLAYER_VT, IN_STATE, SCENE_FLAG, SCENE_DEPTH, CALL_R1,
                                      CALL_R2, REVERT, GOHAN, GOKU, cpu_with, diff, ext_sequence, run_ext73,
                                      set_hits, u32, vt_method, words_naming)
from tests.test_ssj2 import MSG, RET
from rom.webfoot_decompress import ROM_BASE

# ===== constants (brief and report) =====
START_FLAG, END_FLAG = 149, 195                                         # flag n: struct +0xB4 + n/8, bit n&7
SSJ_VTABLE, DEATH_VTABLE, ABILITY_12 = 0x08024C58, 0x080254D8, 0x1D99C0
VANILLA_DEATH = 0x0800833E
ICON_Z, ICON_Z_DIM, HUD_LITERAL = 0x086DAE7C, 0x086DB07C, 0x8E8C
B_ROUTINE, SOUND_START, CONTINUE_RET = 0x08007EDA, 0x0801FC9C, 0x0800185D
ENTRY_HELPER = 0x0800E130                                               # first call of the knockout enter
VEGETA, TRUNKS = 2, 3
SET_195 = 0x3EC6A2                                                      # push 195 ; ext 27 (post-Cell scene)

# rom offset: (r27 byte, r28 byte)
NPC_GOKU = {0x3DB5C3: (0x78, 0x7A), 0x3DB5CC: (0x78, 0x7A), 0x3DBBED: (0x3C, 0x3D), 0x3DD238: (0x78, 0x7A),
            0x3DD241: (0x78, 0x7A), 0x3DD320: (0x78, 0x7A), 0x3DD328: (0x3C, 0x3D)}
PORTRAITS = {0x3DB6AF: (63, 65), 0x3DB723: (63, 65), 0x3DB783: (63, 65), 0x3DD27F: (63, 65)}
GOHAN_EXIT = {0x3DB62A: (157, 158)}
WORDS = {0x3DE774: "door_seq33", 0x3E8D98: "entry_seq1", 0x3EC7A4: "post_cell_seq20"}
CHAMBER_EXIT, DENDE = {0x3DBDD4: 36}, {0x3DD380: 10}                   # scene tables: word count
GOKU_POWER_UP = [(46, (55,)), (57, (0, 9)), (42, (10,)), (47, (55,)), (73, (4, 61)), (43, (10,))]
LOG = Path(__file__).resolve().parents[3]
CHAMBER_SAVE = log_paths.BUILDS / "log2_poc_r28_chamber.sav"
R27_SAVE = log_paths.BUILDS / "log2_poc_r27.sav"

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list()
        i = names.index("fullpower_ssj")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["fullpower_ssj"])     # r28 only; later patches have their own tests
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


# ===== interpreter helpers =====

ON, OFF_BEFORE, OFF_AFTER = {START_FLAG}, set(), {START_FLAG, END_FLAG}


def cpu_at(rom: bytes, who: int, entry: int, flags: set, ep: int = 100):
    """cpu_with plus the two story flags and the record EP; slot 2 selected, holding ability 12."""
    cpu = cpu_with(rom, who, {who: entry})
    for n in (START_FLAG, END_FLAG):
        a, b = STRUCT + 0xB4 + n // 8, n & 7
        cpu.store(a, 1, cpu.load(a, 1) & ~(1 << b) | ((n in flags) << b))
    rec = STRUCT + 0xC + 28 * who
    cpu.store(rec, 2, 100)
    cpu.store(rec + 4, 2, ep)
    cpu.store(rec + 9, 1, 2)
    cpu.store(rec + 0x18 + 2, 1, 12)
    return cpu, rec


def run_tick(rom: bytes, who: int, entry: int, flags: set, ep: int, acc: int) -> tuple:
    """(EP, accumulator, messages) after one Super Saiyan tick with `who` leading, no scene running."""
    cpu, rec = cpu_at(rom, who, entry, flags, ep)
    cpu.store(PLAYER + 0x184, 4, acc)
    cpu.store(SCENE_FLAG, 4, 0)
    cpu.store(SCENE_DEPTH, 4, 0)
    cpu.store(PLAYER_VT + 0x28, 4, (MSG | 1) - PLAYER_VT)
    cpu.store(PLAYER_VT + 0x2C, 4, (IN_STATE | 1) - PLAYER_VT)
    msgs = []
    stops = {MSG: lambda c: msgs.append(c.r[1]) or 0, IN_STATE: lambda c: 0, RET: "ret"}
    cpu.r[0], cpu.r[1] = 0x030021EC, PLAYER
    if cpu.run(vt_method(rom, SSJ_VTABLE, 4), stops, 400) != "ret":
        raise AssertionError("tick did not return")
    return cpu.load(rec + 4, 2, signed=True), cpu.load(PLAYER + 0x184, 4), msgs


def run_test(rom: bytes, who: int, entry: int, flags: set, ep: int = 100) -> int:
    """Ability 12 test(record) through the ability table word, as B and the HUD call it."""
    cpu, rec = cpu_at(rom, who, entry, flags, ep)
    cpu.r[0] = rec
    if cpu.run(u32(rom, ABILITY_12 + 8), {RET: "ret"}, 200) != "ret":
        raise AssertionError("test did not return")
    return cpu.r[0]


def run_hud(rom: bytes, who: int, entry: int, flags: set, ep: int = 100) -> int:
    """Icon pointer the HUD hook picks for the selected slot (ability 12); the real test runs."""
    cpu, rec = cpu_at(rom, who, entry, flags, ep)
    cpu.r[0] = rec
    if cpu.run(u32(rom, HUD_LITERAL), {RET: "ret"}, 400) != "ret":
        raise AssertionError("hud did not return")
    return cpu.r[0]


def run_b(rom: bytes, who: int, entry: int, flags: set, ep: int = 100) -> str:
    """'action' when B reaches the ability 12 action, 'refused' when it starts the refusal sound."""
    cpu, _ = cpu_at(rom, who, entry, flags, ep)
    cpu.r[0] = PLAYER
    return cpu.run(B_ROUTINE, {CALL_R2: "action", SOUND_START: "refused", RET: "ret"}, 400)


def run_revert(rom: bytes, leader: int, entries: dict, flags: set, caller: int = RET, bits: dict = None) -> dict:
    """Entries after appearance_revert(struct) returning to `caller` (Continue lr or a plain caller)."""
    cpu, _ = cpu_at(rom, leader, entries.get(leader, 6), flags)
    for ch, e in entries.items():
        cpu.store(STRUCT + 0xC + 28 * ch + 8, 1, e)
    for ch, b in (bits or {}).items():
        cpu.store(STRUCT + 0xC + 28 * ch + 0x14, 1, b)
    cpu.r[0], cpu.r[14] = STRUCT, caller | 1
    if cpu.run(REVERT, {caller & ~1: "ret"}, 600) != "ret":
        raise AssertionError("appearance_revert did not return")
    return {ch: cpu.load(STRUCT + 0xC + 28 * ch + 8, 1) for ch in entries}


def run_knockout(rom: bytes, leader: int, entry: int, flags: set) -> tuple:
    """(entry after, virtual calls) for the player state 0x21 enter (knockout)."""
    cpu, rec = cpu_at(rom, leader, entry, flags)
    virt = []
    stops = {ENTRY_HELPER: lambda c: 0, CALL_R1: lambda c: virt.append(c.r[1] & ~1) or 0, RET: "ret"}
    cpu.r[0], cpu.r[1] = 0x03001F58, PLAYER
    if cpu.run(vt_method(rom, DEATH_VTABLE, 0), stops, 400) != "ret":
        raise AssertionError("knockout enter did not return")
    return cpu.load(rec + 8, 1), virt


def record_of(rom: bytes, word: int) -> int:
    return u32(rom, word) - ROM_BASE


# ===== tests =====

class StretchFlagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom, cls.before = built()["rom"], built()["before"]

    def test_build_list_ends_with_fullpower_ssj(self):
        names = built()["names"]
        i = names.index("fullpower_ssj")
        self.assertEqual(names[i - 2:i + 1], ["cellgames_ssj", "scene_drain_pause", "fullpower_ssj"])

    def test_flag_window_on_the_tick(self):
        for flags, on in ((OFF_BEFORE, False), (ON, True), (OFF_AFTER, False), ({END_FLAG}, False)):
            with self.subTest(flags=sorted(flags)):
                ep, _, msgs = run_tick(self.rom, GOKU, 20, flags, 1, 0xFFF0)
                self.assertEqual((ep, msgs), (1, []) if on else (0, [0x24]))

    def test_start_flag_set_with_gokus_record_at_the_door(self):
        seq = ext_sequence(self.rom, record_of(self.rom, 0x3DE774))
        i = seq.index((27, (START_FLAG,)))
        self.assertEqual(seq[i + 1], (73, (4, 61)))
        self.assertLess(i, seq.index((70, (2,))))                       # before the leader goes to Vegeta

    def test_end_flag_site_unchanged_and_goku_base_when_cell_is_beaten(self):
        self.assertEqual(self.rom[SET_195:SET_195 + 4], bytes([0, END_FLAG, 2, 27]))
        self.assertEqual(self.rom[SET_195 - 0x20:SET_195 + 0x20], self.before[SET_195 - 0x20:SET_195 + 0x20])
        seq = ext_sequence(self.rom, record_of(self.rom, 0x3EC7A4))
        i = seq.index((73, (0, 157)))
        self.assertEqual(seq[i + 1], (73, (4, 60)))
        self.assertLess(i, seq.index((70, (1,))))


class DrainAndRevertTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom, cls.before = built()["rom"], built()["before"]

    def test_no_drain_and_no_revert_at_zero_for_goku_and_gohan(self):
        for who, entry in ((GOKU, 20), (GOHAN, 5)):
            for ep, acc in ((50, 0xFFF0), (0, 0xFFF0), (1, 0), (1, 0xFFF0)):
                with self.subTest(who=who, ep=ep, acc=acc):
                    self.assertEqual(run_tick(self.rom, who, entry, ON, ep, acc), (ep, acc, []))

    def test_two_hundred_frames_cost_nothing(self):
        ep, acc = 30, 0
        for _ in range(200):
            ep, acc, msgs = run_tick(self.rom, GOKU, 20, ON, ep, acc)
            self.assertEqual(msgs, [])
        self.assertEqual(ep, 30)

    def test_other_characters_drain_as_in_r27(self):
        for who, entry in ((VEGETA, 11), (TRUNKS, 16), (TRUNKS, 17)):
            for flags in (ON, OFF_BEFORE, OFF_AFTER):
                for ep, acc in ((50, 0xFFF0), (1, 0xFFF0), (0, 0xFFF0)):
                    with self.subTest(who=who, entry=entry, flags=sorted(flags), ep=ep):
                        self.assertEqual(run_tick(self.rom, who, entry, flags, ep, acc),
                                         run_tick(self.before, who, entry, flags, ep, acc))

    def test_goku_and_gohan_drain_as_in_r27_outside_the_stretch(self):
        for who, entry in ((GOKU, 20), (GOHAN, 5)):
            for flags in (OFF_BEFORE, OFF_AFTER):
                for ep, acc in ((50, 0xFFF0), (1, 0xFFF0)):
                    with self.subTest(who=who, flags=sorted(flags), ep=ep):
                        got = run_tick(self.rom, who, entry, flags, ep, acc)
                        self.assertEqual(got, run_tick(self.before, who, entry, flags, ep, acc))
        self.assertEqual(run_tick(self.rom, GOKU, 20, OFF_AFTER, 1, 0xFFF0)[2], [0x24])   # revert at 0

    def test_slots_and_old_code(self):
        n = built()["notes"]["fullpower_ssj"]
        self.assertEqual(vt_method(self.rom, SSJ_VTABLE, 4), n["tick"] + ROM_BASE)
        self.assertEqual(vt_method(self.before, SSJ_VTABLE, 4),
                         built()["notes"]["scene_drain_pause"]["tick_ssj"] + ROM_BASE)
        self.assertEqual(vt_method(self.rom, DEATH_VTABLE, 0), n["death"] + ROM_BASE)
        self.assertEqual(vt_method(self.before, DEATH_VTABLE, 0), VANILLA_DEATH)
        self.assertEqual(u32(self.rom, ABILITY_12 + 8), n["test"] + ROM_BASE + 1)
        for vt, slots in ((SSJ_VTABLE, (0, 8, 0xC)), (DEATH_VTABLE, (4, 8, 0xC))):
            for slot in slots:
                self.assertEqual(vt_method(self.rom, vt, slot), vt_method(self.before, vt, slot), (hex(vt), slot))
        for off in (ABILITY_12, ABILITY_12 + 4, ABILITY_12 + 0xC):           # icons and the ssj2 gate action
            self.assertEqual(self.rom[off:off + 4], self.before[off:off + 4])


class ButtonAndIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom, cls.before = built()["rom"], built()["before"]

    def test_test_is_zero_for_super_saiyan_goku_and_gohan_in_the_stretch(self):
        self.assertEqual(run_test(self.rom, GOKU, 20, ON), 0)
        self.assertEqual(run_test(self.rom, GOHAN, 5, ON), 0)
        self.assertNotEqual(run_test(self.rom, GOKU, 20, OFF_AFTER), 0)
        self.assertNotEqual(run_test(self.rom, GOHAN, 5, OFF_BEFORE), 0)

    def test_other_entries_keep_the_vanilla_test(self):
        for who, entry in ((VEGETA, 11), (VEGETA, 8), (TRUNKS, 17), (GOKU, 19), (GOHAN, 2), (GOHAN, 4)):
            for flags in (ON, OFF_AFTER):
                for ep in (100, 5):
                    with self.subTest(who=who, entry=entry, flags=sorted(flags), ep=ep):
                        self.assertEqual(run_test(self.rom, who, entry, flags, ep),
                                         run_test(self.before, who, entry, flags, ep))

    def test_hud_shows_the_dim_z_in_the_stretch(self):
        self.assertEqual(run_hud(self.rom, GOKU, 20, ON), ICON_Z_DIM)
        self.assertEqual(run_hud(self.rom, GOHAN, 5, ON), ICON_Z_DIM)
        self.assertEqual(run_hud(self.before, GOKU, 20, ON), ICON_Z)           # r27: bright, B reverts
        self.assertEqual(run_hud(self.rom, VEGETA, 11, ON), run_hud(self.before, VEGETA, 11, ON))

    def test_hud_after_the_stretch_as_in_r27(self):
        for who, entry in ((GOKU, 20), (GOHAN, 5), (GOKU, 19), (GOHAN, 2)):
            for flags in (OFF_BEFORE, OFF_AFTER):
                with self.subTest(who=who, entry=entry, flags=sorted(flags)):
                    self.assertEqual(run_hud(self.rom, who, entry, flags), run_hud(self.before, who, entry, flags))
        self.assertEqual(run_hud(self.rom, GOKU, 20, OFF_AFTER), ICON_Z)

    def test_b_refuses_in_the_stretch_and_works_after(self):
        self.assertEqual(run_b(self.rom, GOKU, 20, ON), "refused")
        self.assertEqual(run_b(self.rom, GOHAN, 5, ON), "refused")
        self.assertEqual(run_b(self.before, GOKU, 20, ON), "action")
        for flags in (OFF_BEFORE, OFF_AFTER):
            self.assertEqual(run_b(self.rom, GOKU, 20, flags), "action")
            self.assertEqual(run_b(self.rom, GOHAN, 5, flags), "action")
        self.assertEqual(run_b(self.rom, VEGETA, 11, ON), "action")
        self.assertEqual(run_b(self.rom, GOKU, 19, ON), run_b(self.before, GOKU, 19, ON))


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom, cls.before = built()["rom"], built()["before"]

    def test_ext70_and_switch_keep_super_saiyan_in_the_stretch(self):
        got = run_revert(self.rom, 1, {GOHAN: 5, GOKU: 20, VEGETA: 11}, ON)
        self.assertEqual(got, {GOHAN: 5, GOKU: 20, VEGETA: 8})
        self.assertEqual(run_revert(self.rom, GOHAN, {GOHAN: 5, GOKU: 20}, ON), {GOHAN: 5, GOKU: 20})
        self.assertEqual(run_revert(self.before, 1, {GOHAN: 5, GOKU: 20}, ON), {GOHAN: 2, GOKU: 19})

    def test_revert_is_vanilla_outside_the_stretch(self):
        for flags in (OFF_BEFORE, OFF_AFTER):
            for leader, entries in ((1, {GOHAN: 5, GOKU: 20, VEGETA: 11}), (GOHAN, {GOHAN: 5, GOKU: 20}),
                                    (1, {GOHAN: 4, GOKU: 19, TRUNKS: 17})):
                for caller in (RET, CONTINUE_RET):
                    with self.subTest(flags=sorted(flags), leader=leader, caller=hex(caller)):
                        self.assertEqual(run_revert(self.rom, leader, entries, flags, caller),
                                         run_revert(self.before, leader, entries, flags, caller))

    def test_continue_restores_super_saiyan_in_the_stretch(self):
        got = run_revert(self.rom, GOKU, {GOHAN: 2, GOKU: 19}, ON, CONTINUE_RET, {GOHAN: 0x7F})
        self.assertEqual(got, {GOHAN: 5, GOKU: 20})                            # the leader too
        got = run_revert(self.rom, VEGETA, {GOHAN: 2, GOKU: 19}, ON, CONTINUE_RET, {GOHAN: 0x5F})
        self.assertEqual(got, {GOHAN: 2, GOKU: 20})                            # Gohan without Super Saiyan
        got = run_revert(self.rom, GOHAN, {GOHAN: 0, GOKU: 19}, ON, CONTINUE_RET, {GOHAN: 0x7F})
        self.assertEqual(got, {GOHAN: 0, GOKU: 20})                            # Demon Clothes stay
        got = run_revert(self.rom, GOKU, {GOHAN: 2, GOKU: 19}, ON, RET, {GOHAN: 0x7F})
        self.assertEqual(got, {GOHAN: 2, GOKU: 19})                            # only Continue restores

    def test_knockout_keeps_super_saiyan_in_the_stretch(self):
        leave = vt_method(self.rom, SSJ_VTABLE, 0xC)
        for who, entry, base in ((GOKU, 20, 19), (GOHAN, 5, 2)):
            with self.subTest(who=who):
                self.assertEqual(run_knockout(self.rom, who, entry, ON), (entry, [leave]))
                self.assertEqual(run_knockout(self.rom, who, entry, OFF_AFTER), (base, [leave]))
                self.assertEqual(run_knockout(self.before, who, entry, ON), (base, [leave]))
        for who, entry in ((VEGETA, 11), (GOHAN, 4), (GOKU, 19)):
            for flags in (ON, OFF_AFTER):
                self.assertEqual(run_knockout(self.rom, who, entry, flags),
                                 run_knockout(self.before, who, entry, flags), (who, entry))

    def test_rage_still_gives_super_saiyan_2_and_its_text(self):
        for rom in (self.rom, self.before):
            result, cpu, _, _ = run_ext73(rom, GOHAN, 160, GOHAN, {GOHAN: 5})
            self.assertEqual((result, cpu.load(STRUCT + 0xC + 8, 1)), ("ret", 4))
        self.assertEqual(self.rom[0x3EA300:0x3EA400], self.before[0x3EA300:0x3EA400])    # Rage scene
        self.assertEqual(self.rom[0x3EA365:0x3EA36B], bytes.fromhex("000000a00249"))
        for ep in (100, 5):
            self.assertEqual(run_test(self.rom, GOHAN, 4, ON, ep), run_test(self.before, GOHAN, 4, ON, ep))


class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_in_place_bytes_old_and_new(self):
        for off, (old, new) in {**NPC_GOKU, **PORTRAITS, **GOHAN_EXIT}.items():
            self.assertEqual((self.before[off], self.rom[off]), (old, new), hex(off))

    def test_relocated_records_have_one_word_each(self):
        moved = self.notes["fullpower_ssj"]["records"]
        for word, name in WORDS.items():
            old = record_of(self.before, word)
            with self.subTest(name=name):
                self.assertEqual(record_of(self.rom, word), moved[name])
                self.assertEqual(words_naming(self.before, old + ROM_BASE), [word])
                self.assertEqual(words_naming(self.rom, moved[name] + ROM_BASE), [word])
                self.assertEqual(self.rom[old:old + 0x80], self.before[old:old + 0x80])   # old one unchanged

    def test_door_record_is_old_plus_gokus_record(self):
        a = ext_sequence(self.before, record_of(self.before, 0x3DE774))
        b = ext_sequence(self.rom, record_of(self.rom, 0x3DE774))
        i = a.index((27, (START_FLAG,)))
        self.assertEqual(b, a[:i + 1] + [(73, (4, 61))] + a[i + 1:])

    def test_arena_entry_without_gokus_power_up(self):
        a = ext_sequence(self.before, record_of(self.before, 0x3E8D98))
        b = ext_sequence(self.rom, record_of(self.rom, 0x3E8D98))
        i = a.index(GOKU_POWER_UP[0])
        self.assertEqual(a[i:i + 6], GOKU_POWER_UP)
        self.assertEqual(b, a[:i] + a[i + 6:])
        self.assertNotIn((57, (0, 9)), b)

    def test_post_cell_record_is_old_plus_gokus_base(self):
        a = ext_sequence(self.before, record_of(self.before, 0x3EC7A4))
        b = ext_sequence(self.rom, record_of(self.rom, 0x3EC7A4))
        i = a.index((73, (0, 157)))
        self.assertEqual(b, a[:i + 1] + [(73, (4, 60))] + a[i + 1:])

    def test_gohan_super_saiyan_from_the_chamber_exit(self):
        seq = ext_sequence(self.rom, record_of(self.rom, 0x3DBDD4 + 8))
        self.assertIn((73, (0, 158)), seq)
        self.assertNotIn((73, (0, 157)), seq)
        self.assertLess(seq.index((73, (0, 158))), seq.index((82, (0,))))

    def test_npc_goku_is_61_in_the_chamber_exit_and_dende_talk(self):
        tables = {**CHAMBER_EXIT, **DENDE}
        before = sorted(s for _, _, s in set_hits(self.before, tables, {60, 61}))
        after = sorted(s for _, _, s in set_hits(self.rom, tables, {60, 61}))
        self.assertTrue(before)
        self.assertEqual((set(before), after), ({60}, [61] * len(before)))

    @staticmethod
    def portraits(rom: bytes) -> dict:
        """{raw portrait id: [text record]} in the chamber exit and Dende tables."""
        out = {}
        for t, n in {**CHAMBER_EXIT, **DENDE}.items():
            for k in range(n):
                rec = u32(rom, t + 4 * k) - ROM_BASE
                if 0 <= rec < len(rom) and rom[rec + 1] == 0 and rom[rec + 2] in (1, 2):
                    out.setdefault(rom[rec + 3], []).append(rec)
        return out

    def test_goku_lines_use_the_adult_portrait(self):
        before, after = self.portraits(self.before), self.portraits(self.rom)
        self.assertNotIn(63, after)
        self.assertEqual(sorted(after[65]), sorted(before[63] + before.get(65, [])))
        self.assertEqual(after.get(121), before.get(121))                     # Gohan lines unchanged

    def test_r27_gohan_inserts_and_refill_stay(self):
        for word in (0x3E9438, 0x3EA400):
            self.assertEqual(u32(self.rom, word), u32(self.before, word), hex(word))


class DiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]
        cls.new_used = b["used"][len(b["alloc_before"].used()):]
        cls.changed = diff(cls.before, cls.rom)

    def sites(self) -> list:
        s = [(o, o + 1, "byte") for o in list(NPC_GOKU) + list(PORTRAITS) + list(GOHAN_EXIT)]
        s += [(w, w + 4, "table word") for w in WORDS]
        s += [(0x3ED4, 0x3EDC, "revert jump"), (0x24C5C, 0x24C60, "tick slot"), (0x254D8, 0x254DC, "knockout slot"),
              (ABILITY_12 + 8, ABILITY_12 + 0xC, "test word")]
        return s + [(a, a + n, "new data") for a, n in self.new_used]

    def outside(self, sites: list) -> list:
        return [hex(i) for i in self.changed if not any(a <= i < e for a, e, _ in sites)]

    def test_earlier_allocations_unchanged(self):
        n = len(built()["alloc_before"].used())
        self.assertEqual(built()["used"][:n], built()["alloc_before"].used())
        self.assertTrue(all(a >= 0x89A8B0 and a + s <= 0xF00000 for a, s in self.new_used))

    def test_only_expected_sites_change(self):
        sites = self.sites()
        self.assertEqual(self.outside(sites), [])
        for a, e, name in sites:
            if name != "new data":
                self.assertTrue(any(a <= i < e for i in self.changed), (hex(a), name))

    def test_dropping_any_site_is_caught(self):
        sites = self.sites()
        for k, (a, _, name) in enumerate(sites):
            if name != "new data":
                with self.subTest(site=hex(a)):
                    self.assertTrue(self.outside(sites[:k] + sites[k + 1:]))

    def test_art_block_and_palette_unchanged(self):
        block = self.notes["npc_gi"]["block"]
        self.assertEqual(self.rom[0xF00000:], self.before[0xF00000:])                       # portrait slots
        self.assertEqual(self.rom[block:block + 4 + 4 * 122], self.before[block:block + 4 + 4 * 122])
        self.assertEqual(self.rom[0x1DA6C8:0x1DA6C8 + 512], self.before[0x1DA6C8:0x1DA6C8 + 512])   # incl. 172
        self.assertEqual(self.rom[0x3ECBA4:0x3ECBA4 + 3 * 512], self.before[0x3ECBA4:0x3ECBA4 + 3 * 512])


class FailClosedTests(unittest.TestCase):
    @staticmethod
    def apply_to(rom: bytearray, alloc) -> None:
        from patches import fullpower_ssj
        fullpower_ssj.apply(rom, alloc)

    def test_any_old_byte_slot_or_record_change_refuses_before_writing(self):
        b = built()
        notes = b["alloc_before"].notes
        sites = list(NPC_GOKU) + list(PORTRAITS) + list(GOHAN_EXIT) + list(WORDS) + [
            0x3ED4, 0x414C, 0x24C5C, 0x254D8, ABILITY_12 + 8, 0x3DE620 + 0x40,
            notes["cellgames_ssj"]["records"]["entry_seq1"] + 0x10, notes["npc_gi"]["records"][0x3EBE1C] + 0x10]
        for off in sites:
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snapshot = bytes(rom)
            with self.subTest(off=hex(off)):
                with self.assertRaises(ValueError):
                    self.apply_to(rom, alloc)
                self.assertEqual(bytes(rom), snapshot)
                self.assertNotIn("fullpower_ssj", alloc.notes)

    def test_second_run_and_missing_notes_raise(self):
        b = built()
        alloc = copy.deepcopy(b["alloc_before"])
        alloc.notes["fullpower_ssj"] = {}
        with self.assertRaisesRegex(ValueError, "already ran"):
            self.apply_to(bytearray(b["before"]), alloc)
        alloc = copy.deepcopy(b["alloc_before"])
        del alloc.notes["scene_drain_pause"]
        with self.assertRaisesRegex(ValueError, "needs"):
            self.apply_to(bytearray(b["before"]), alloc)


@unittest.skipUnless(CHAMBER_SAVE.exists() and R27_SAVE.exists(), "chamber save not built")
class ChamberSaveTests(unittest.TestCase):
    """Slot 3 of log2_poc_r28_chamber.sav: the point right before the chamber exit scene."""

    @classmethod
    def setUpClass(cls):
        cls.ram = log2_save.read_ram(CHAMBER_SAVE.read_bytes())
        cls.old = log2_save.read_ram(R27_SAVE.read_bytes())
        cls.slot = bytes(cls.ram[log2_save.slot_range(2)])

    def flag(self, n: int) -> int:
        return log2_save.bit(self.slot, log2_save.O_STORY, n)

    def test_checksums(self):
        for n in range(3):
            s = bytes(self.ram[log2_save.slot_range(n)])
            self.assertEqual(struct.unpack_from("<I", s, 0x164)[0], log2_save.adler32(s[:0x164]), n)

    def test_story_point(self):
        self.assertTrue(all(self.flag(n) for n in (149, 151, 154, 155, 156)))           # chamber entered, Scouter
        self.assertFalse(any(self.flag(n) for n in (157, 158, 191, 192, 195)))          # TV not seen, no exit
        self.assertFalse(any(self.flag(n) for n in (162, 163, 164, 185, 186, 187, 188)))  # no Dragon Balls

    def test_leader_and_map(self):
        s = self.slot
        self.assertEqual((s[0], s[2], s[3], s[4]), (VEGETA, 6, 15, 1))
        self.assertEqual(struct.unpack_from("<hh", s, 0x160), (104, 76))

    def test_only_named_bytes_differ_from_r27(self):
        changed = [i for i in range(len(self.ram)) if self.ram[i] != self.old[i]]
        slot3 = log2_save.slot_range(2)
        self.assertTrue(changed)
        self.assertTrue(all(slot3.start <= i < slot3.stop for i in changed))
        allowed = {0x00, 0x02, 0x03, 0x04, 0x160, 0x161, 0x162, 0x163, 0x164, 0x165, 0x166, 0x167}
        allowed |= {0xB4 + n // 8 for n in (157, 158, 162, 163, 164, 185, 186, 187, 188, 191)}
        self.assertEqual([hex(i - slot3.start) for i in changed if i - slot3.start not in allowed], [])


CHAMBER2 = CHAMBER_SAVE.with_name("log2_poc_r28_chamber2.sav")


@unittest.skipUnless(CHAMBER2.exists() and R27_SAVE.exists(), "chamber2 save not built")
class Chamber2SaveTests(unittest.TestCase):
    """Slot 3 of log2_poc_r28_chamber2.sav: on 6,16 at the TV, party as before the exit scene."""

    def test_slot_3(self):
        ram, old = (log2_save.read_ram(p.read_bytes()) for p in (CHAMBER2, R27_SAVE))
        slot3 = log2_save.slot_range(2)
        s = bytes(ram[slot3])
        self.assertEqual(struct.unpack_from("<I", s, 0x164)[0], log2_save.adler32(s[:0x164]))
        self.assertEqual((s[0], s[2], s[3], s[4], struct.unpack_from("<hh", s, 0x160)), (VEGETA, 6, 16, 1, (200, 236)))
        self.assertEqual((s[0xC + 0x14], s[0xC + 28 * GOKU + 0x14]), (0x5D, 0x40))   # Gohan, Goku before the exit
        flag = lambda n: log2_save.bit(s, log2_save.O_STORY, n)                         # noqa: E731
        self.assertTrue(all(flag(n) for n in (149, 151, 154, 155, 156)))
        self.assertFalse(any(flag(n) for n in (157, 158, 162, 163, 164, 185, 186, 187, 188, 191, 195)))
        changed = {i - slot3.start for i in range(len(ram)) if ram[i] != old[i]}
        allowed = {0x00, 0x02, 0x03, 0x20, 0x90, 0xC7, 0xC8, 0xCB, *range(0x160, 0x168)}
        self.assertTrue(changed <= allowed, sorted(hex(i) for i in changed - allowed))


if __name__ == "__main__":
    unittest.main()
