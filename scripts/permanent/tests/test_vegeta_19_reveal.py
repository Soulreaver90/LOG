r"""
test_vegeta_19_reveal.py - Tests for patches.vegeta_19_reveal (trial 2026-10-30): after "So, does a machine like
                           yourself ever experience fear?" Vegeta transforms (state 35, flash), then the 19 fight
                           starts with him in the normal Super Saiyan form.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_vegeta_19_reveal.py -v
Builds build_list_trial_vegeta19.txt in memory: "before" = the list up to vegeta_19_reveal (the main list, pinned to
r40 by SHA-1), "rom" = with it. Scripts are decoded with test_cellgames_ssj's decoder. The form proof runs the
ROM's own code (ext 126, ext 11, the state 35 callback chain into transform(player, 1), the pool fill, the pool
tick, ability 12) as thumb_dis text in test_bf_ki_pool's Cpu2; sound and the form methods are stubs at their
addresses. Expected values are restated from docs\tasks\2026-10-30-vegeta-19\vegeta-19-trial.md, plan-report.md
item 11 and the base bytes (scripts\one-time\2026-10-30-vegeta-19\s1_study.txt to s5_state35_sites.txt), never
imported from the patch module.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
from patches import vegeta_19_reveal
from rom.rom_space import Allocator
from tests.test_bf_ki_pool import PLAYER, RAM, RET, SET_STATE, STACK, STOPS, STRUCT, Cpu2, cpu, pool, rec
from tests.test_cellgames_ssj import diff, ext_sequence, ops

# ===== constants (brief, plan item 11, base reads) =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_vegeta19.txt"
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"        # build_list.txt r40 (2026-10-30; r39 was aa51dc16)
TABLE, TABLE_NAMER = 0x3D40C8, 0x3FD4F4                 # Android 19 table, named by map 7,15 region 0 item
WORD40, WORD41 = 0x3D4168, 0x3D416C                     # seq 41 (the line) and seq 42 (the fight start)
SEQ41, SEQ42 = 0x3D4076, 0x3D40B2
SEQ42_BYTES = "2a0000000102561d0218040268000c02550000022111"
LINE = b"@So, does a machine like yourself ever experience fear?\0"
VANILLA_TAIL = [(86, (1,)), (104, (12, 2)), (85, (12,)), (33, (0,))]
SPACE_TRANSFORM = (0x3D1FDF, "1d0200460239")            # space scene seq 7: push 0,35 ; ext 57
CELL_GUARDS = (0x3E65E2, 0x3E6F04)                      # Vegeta and Trunks: ext 126 ; jz ; ... ; push 0,35 ; ext 57
GUARD_18 = (0x3D8C95, "020b00020b027e04")               # 18 death seq 3: leader ; push 2 ; eq ; ext 126 ; and
FLASH_PAIR = [(42, (10,)), (43, (10,))]                 # r27 Goku transform: push 10 ; ext 42 ... push 10 ; ext 43
EXPANSION = (0x800000, 0xF00000)
NO_PERMANENT = (27, 28, 70, 73, 79, 80, 81, 82, 83, 91, 98, 109, 110, 115, 139)   # flags, party, form, level, HP, EP
# Form proof (bible HKP, FRM, SAV rows; s3_form_test.txt, s4_ability12.txt)
EXT_TABLE = 0x3B5D28
EXT126, EXT11 = 0x0800AF73, 0x0800949D
VEGETA, VEGETA_BASE, VEGETA_SSJ = 2, 8, 11              # leader id; appearance entries (set 137, set 140)
SET_SSJ, SET_BASE = 140, 137
SSJ_OBJ, BASE_OBJ = 0x030021EC, 0x030021E0
FORM_VTABLES = {0x030021E0: 0x08024004, 0x030021E4: 0x08024E4C, 0x030021E8: 0x0802526C,
                0x030021EC: 0x08024C58, 0x030021F0: 0x08024ABC}     # form object init @0x080232E4
STATE35_VT, STATE35_DONE = 0x08025D9C, 0x14             # +0x14 = the "animation done" callback (fill_end in r39)
TRANSFORM_CB, TRANSFORM = 0x0801563C, 0x08014D58
SOUND, GET_SET = 0x0801FC9C, 0x08009324
SSJ_VT, TICK = 0x08024C58, 4                           # Super Saiyan form vtable +4 = the tick (pool tick in r39)
ABILITY12 = 0x1D9900 + 12 * 16                          # +8 test, +12 action
REVERT_MSG = 0x24
CTX = 0x02020000                                        # script VM context: +0 count, +4 values

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off - ROM_BASE if off >= ROM_BASE else off)[0]


def padded() -> bytearray:
    base = log2_build.BASE.read_bytes()
    return bytearray(base) + b"\xFF" * (log2_build.ROM_SIZE - len(base))


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("vegeta_19_reveal")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, names[i:])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["vegeta_19_reveal"], labels=alloc.notes["bf_ki_pool"]["labels"])
    return _CACHE


def vt_target(rom: bytes, vt: int, slot: int) -> int:
    """A vtable slot holds an offset from the vtable start (HKP row): target = vt + word."""
    return (vt + u32(rom, vt + slot)) & M32


def words(rom: bytes, lo: int, hi: int) -> list:
    vals = memoryview(rom[: len(rom) & ~3]).cast("I")
    return [4 * i for i, w in enumerate(vals) if lo <= w < hi]


# ===== tests: list and fail-closed =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "vegeta_19_reveal" in dev:
            self.skipTest("approved: the line is in build_list_core.txt, so build_list_trial_vegeta19.txt is retired")
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["vegeta_19_reveal"])

    def test_before_is_r40(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R40_SHA1)


class FailClosedTests(unittest.TestCase):
    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["vegeta_19_reveal"] = {}
        with self.assertRaises(ValueError):
            vegeta_19_reveal.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                          # the word is no longer vanilla either
        with self.assertRaises(ValueError):
            vegeta_19_reveal.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        for off in (WORD41, WORD41 + 3, SEQ42, SEQ42 + 5, SEQ42 + 0x15, SPACE_TRANSFORM[0] + 1):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                vegeta_19_reveal.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_second_namer_of_seq42_refuses(self):
        rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        rom[0x900000:0x900004] = struct.pack("<I", SEQ42 + ROM_BASE)
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            vegeta_19_reveal.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_the_word_or_the_record_refuses(self):
        for site in ((WORD41 + 2, 1, "other"), WORD41, (SEQ42 + 4, 2, "other"), SEQ42 + 0x15):
            rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
            alloc.notes["other_module"] = {"sites": [site]}
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(site)):
                vegeta_19_reveal.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_neighbour_sites_do_not_refuse(self):
        rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        alloc.notes["other_module"] = {"sites": [(WORD40, 4, "word 40"), (SEQ42 - 1, 1, "seq 41 end"),
                                                 (WORD41 + 4, 4, "word 42")]}
        vegeta_19_reveal.apply(rom, alloc)

    def test_padded_base_gets_the_same_record(self):
        rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        vegeta_19_reveal.apply(rom, alloc)
        at, n = alloc.notes["vegeta_19_reveal"]["record"], built()["notes"]
        self.assertEqual(rom[at:at + n["size"]], built()["rom"][n["record"]:n["record"] + n["size"]])
        self.assertEqual(u32(rom, WORD41), ROM_BASE + at)


# ===== tests: the record =====

class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.at, cls.size = cls.n["record"], cls.n["size"]

    def test_source_bytes_are_vanilla_in_main(self):
        self.assertEqual(self.before[SEQ42:SEQ42 + 22].hex(), SEQ42_BYTES)
        self.assertEqual(u32(self.before, WORD41), SEQ42 + ROM_BASE)
        self.assertEqual(u32(self.before, WORD40), SEQ41 + ROM_BASE)
        self.assertEqual(self.before[SEQ41 + 4:SEQ41 + 4 + len(LINE)], LINE)        # type 1, Vegeta's line
        self.assertEqual(self.before[SEQ41:SEQ41 + 4], bytes([41, 0, 1, 1]))         # next 41, type 1, portrait 1
        self.assertEqual(u32(self.before, TABLE_NAMER), TABLE + ROM_BASE)

    def test_word_41_names_the_copy_and_nothing_else_moved(self):
        self.assertEqual(u32(self.rom, WORD41), ROM_BASE + self.at)
        for k in (0, 40, 42, 43):
            self.assertEqual(u32(self.rom, TABLE + 4 * k), u32(self.before, TABLE + 4 * k), k)
        self.assertEqual(self.rom[SEQ42:SEQ42 + 22], self.before[SEQ42:SEQ42 + 22])     # old record unchanged

    def test_copy_was_free_and_only_word_41_names_it(self):
        self.assertTrue(EXPANSION[0] <= self.at and self.at + self.size <= EXPANSION[1])
        self.assertEqual(set(self.before[self.at:self.at + self.size]), {0xFF})
        lo, hi = ROM_BASE + self.at, ROM_BASE + self.at + self.size
        self.assertEqual(words(self.before, lo, hi), [])
        self.assertEqual(words(self.rom, lo, hi), [WORD41])
        self.assertEqual(words(self.rom, SEQ42 + ROM_BASE, SEQ42 + ROM_BASE + 1), [])  # old record unreferenced

    def test_copy_decodes_to_guard_transform_flash_then_the_vanilla_ops(self):
        self.assertEqual(self.rom[self.at:self.at + 3], bytes([42, 0, 0]))           # next 42 = END, as vanilla
        seq = ext_sequence(self.rom, self.at)                  # args = every value pushed since the last call
        self.assertEqual(seq, [(11, ()), (126, (2,)), (57, (0, 0, 35))] + FLASH_PAIR + VANILLA_TAIL)
        self.assertEqual(ext_sequence(self.before, SEQ42), VANILLA_TAIL)

    def test_guard_is_leader_2_and_not_transformed(self):
        body = [(op, arg) for _, op, arg in ops(self.rom, self.at + 3)]
        self.assertEqual(body[:7], [(2, 11), (0, [2]), (11, None), (2, 126), (0, [0]), (11, None), (4, None)])
        self.assertEqual(body[7][0], 19)                                           # jz (target: next test)
        self.assertEqual(self.rom[self.at + 3:self.at + 10].hex(), GUARD_18[1][:14])  # 18 seq 3 guard prefix

    def test_jz_skips_exactly_the_transform_and_the_flash(self):
        listing = ops(self.rom, self.at + 3)
        jz = [(at, arg) for at, op, arg in listing if op == 19]
        self.assertEqual(len(jz), 1)
        target = jz[0][1]
        tail_at = [at for at, op, arg in listing if op == 0 and arg == [1]][0]       # push 1 ; ext 86
        self.assertEqual(target, tail_at)
        skipped = self.rom[jz[0][0] + 2:target]
        self.assertEqual(skipped.hex(), SPACE_TRANSFORM[1] + "000a022a" + "000a022b")

    def test_transform_bytes_equal_the_vanilla_player_transforms(self):
        self.assertEqual(self.before[SPACE_TRANSFORM[0]:SPACE_TRANSFORM[0] + 6].hex(), SPACE_TRANSFORM[1])
        for rec_at in CELL_GUARDS:                                  # ext 126 ; jz +3 ; push n ; end ; transform
            self.assertEqual(self.before[rec_at + 3:rec_at + 5].hex(), "027e")
            self.assertEqual(self.before[rec_at + 10:rec_at + 16].hex(), SPACE_TRANSFORM[1])
        self.assertIn(bytes.fromhex(SPACE_TRANSFORM[1]), self.rom[self.at:self.at + self.size])
        self.assertEqual(self.before[GUARD_18[0]:GUARD_18[0] + 8].hex(), GUARD_18[1])

    def test_tail_is_the_vanilla_seq42_body(self):
        self.assertEqual(self.rom[self.at + self.size - 19:self.at + self.size], self.before[SEQ42 + 3:SEQ42 + 22])

    def test_no_permanent_op(self):
        seq = ext_sequence(self.rom, self.at)
        self.assertEqual([n for n, _ in seq if n in NO_PERMANENT], [])
        self.assertEqual([a[-2:] for n, a in seq if n == 57], [(0, 35)])              # the one state op is 35

    def test_main_to_trial_diff_is_the_word_and_the_copy(self):
        changed = diff(self.before, self.rom)
        sites = [(WORD41, 4), (self.at, self.size)]
        self.assertEqual([i for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        for s, n in sites:
            self.assertTrue(any(s <= i < s + n for i in changed), f"rom:0x{s:X}")
        self.assertEqual(sorted((s, n) for s, n, _ in self.n["sites"]), sorted(sites))


# ===== tests: the form proof (ROM code in the interpreter) =====

class FormTests(unittest.TestCase):
    """The fight starts with Vegeta in the normal pool Super Saiyan form; the player can drop it; ki drains."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.labels = b["rom"], b["labels"]

    def vegeta(self, entry: int, **kw) -> Cpu2:
        cp = cpu(leader=VEGETA, entry=entry, data=self.rom, **kw)
        for obj, vt in FORM_VTABLES.items():
            cp.store(obj, 4, vt)
        cp.store(CTX, 4, 0)
        cp.calls = []
        return cp

    def form_stops(self, cp: Cpu2) -> dict:
        """Stubs: sound, set lookup (returns 0x02030000 + set id) and every form object method slot 0, 8 and 0xC."""
        stops = dict(STOPS)
        stops[SOUND] = lambda c: c.calls.append(("sound", c.r[1])) or 0
        stops[GET_SET] = lambda c: c.calls.append(("set", c.r[0])) or 0x02030000 + c.r[0]
        for obj, vt in FORM_VTABLES.items():
            for slot, name in ((0, "init"), (8, "enter"), (0xC, "leave")):
                target = (vt + u32(self.rom, vt + slot)) & M32 & ~1

                def stub(c, o=obj, n=name):
                    c.calls.append((n, o))
                    return 0
                stops.setdefault(target, stub)
        return stops

    def run_ext(self, cp: Cpu2, handler_word: int) -> int:
        cp.r[0], cp.r[13], cp.r[14] = CTX, STACK, RET | 1
        self.assertEqual(cp.run(u32(self.rom, handler_word), STOPS), "ret")
        n = cp.load(CTX, 4)
        return cp.load(CTX + 4 * n, 4)

    def test_ext_handler_words(self):
        self.assertEqual(u32(self.rom, EXT_TABLE + 4 * 126), EXT126)
        self.assertEqual(u32(self.rom, EXT_TABLE + 4 * 11), EXT11)

    def test_guard_values_for_base_and_super_saiyan_vegeta(self):
        self.assertEqual(self.run_ext(self.vegeta(VEGETA_BASE), EXT_TABLE + 4 * 11), VEGETA)
        self.assertEqual(self.run_ext(self.vegeta(VEGETA_BASE), EXT_TABLE + 4 * 126), 0)   # guard true: transform
        self.assertEqual(self.run_ext(self.vegeta(VEGETA_SSJ), EXT_TABLE + 4 * 126), 1)    # guard false: skip

    def test_state35_done_runs_fill_end(self):
        self.assertEqual(vt_target(self.rom, STATE35_VT, STATE35_DONE), self.labels["fill_end"] | 1)
        self.assertEqual(vt_target(built()["before"], STATE35_VT, STATE35_DONE), self.labels["fill_end"] | 1)

    def test_transform_end_gives_the_pool_super_saiyan(self):
        cp = self.vegeta(VEGETA_BASE, ep=40, mep=138, cooldown=0x500)
        cp.r[0], cp.r[1] = 0x03002184, PLAYER                          # state object, player (bf_ki_pool FillEmpty)
        self.assertEqual(cp.run(vt_target(self.rom, STATE35_VT, STATE35_DONE), self.form_stops(cp), limit=2000),
                         "ret")
        self.assertEqual(cp.r[13], STACK)
        self.assertEqual(cp.load(rec(VEGETA) + 8, 1), VEGETA_SSJ)              # appearance entry 11
        self.assertEqual(cp.load(PLAYER + 0x180, 4), SSJ_OBJ)                  # form object: Super Saiyan
        self.assertEqual(cp.load(PLAYER + 0x48, 4), 0x02030000 + SET_SSJ)      # sprite set 140
        self.assertIn(("leave", BASE_OBJ), cp.calls)
        self.assertIn(("enter", SSJ_OBJ), cp.calls)
        self.assertEqual(cp.states, [(PLAYER, 0)])                              # transform sets state 0
        self.assertEqual(pool(cp), (138, 0x8000 | VEGETA << 8 | VEGETA_SSJ, 0))  # full pool, Vegeta's tag
        self.assertEqual(cp.load(rec(VEGETA) + 4, 2), 40)                      # regular EP not touched
        self.assertEqual(cp.load(STRUCT + 8, 4), 0x500)                        # cooldown not written

    def test_pool_ref_calls_entry_11_a_pool_form(self):
        cp = self.vegeta(VEGETA_SSJ, f149=True)                                # no full-power rule for Vegeta
        self.assertEqual(cp.run(self.labels["pool_ref"], STOPS), "ret")
        self.assertEqual((cp.r[0], cp.r[1]), (RAM, rec(VEGETA)))

    def test_without_the_guard_a_super_saiyan_vegeta_would_drop_to_base(self):
        cp = self.vegeta(VEGETA_SSJ)
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = PLAYER, 1, STACK, RET | 1
        self.assertEqual(cp.run(TRANSFORM, self.form_stops(cp), limit=2000), "ret")
        self.assertEqual(cp.load(rec(VEGETA) + 8, 1), VEGETA_BASE)
        self.assertEqual(cp.load(PLAYER + 0x48, 4), 0x02030000 + SET_BASE)

    def tick(self, cp: Cpu2) -> None:
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = SSJ_OBJ, PLAYER, STACK, RET | 1
        target = vt_target(self.rom, SSJ_VT, TICK)
        self.assertEqual(target, self.labels["tick_ssj"] | 1)
        self.assertEqual(cp.run(target, STOPS, limit=2000), "ret")

    def test_ki_drains_in_the_fight_and_pauses_in_scenes(self):
        cp = self.vegeta(VEGETA_SSJ, pool=138, tag=0x8000 | VEGETA << 8 | VEGETA_SSJ)
        cp.store(RAM + 8, 4, 0)
        for _ in range(40):
            self.tick(cp)
        self.assertEqual(cp.load(RAM, 2), 136)                                 # 1 every 20 frames
        cp = self.vegeta(VEGETA_SSJ, pool=138, tag=0x8000 | VEGETA << 8 | VEGETA_SSJ, scene=1, depth=1)
        cp.store(RAM + 8, 4, 0)
        for _ in range(40):
            self.tick(cp)
        self.assertEqual(cp.load(RAM, 2), 138)                                 # the scene before the fight

    def test_empty_pool_drops_the_form(self):
        cp = self.vegeta(VEGETA_SSJ, pool=0, tag=0x8000 | VEGETA << 8 | VEGETA_SSJ)
        cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
        self.tick(cp)
        self.assertEqual(cp.states, [(PLAYER, REVERT_MSG)])

    def test_b_drops_the_form_with_any_cooldown(self):
        cp = self.vegeta(VEGETA_SSJ, cooldown=0x500)
        cp.r[0], cp.r[13], cp.r[14] = rec(VEGETA), STACK, RET | 1
        self.assertEqual(cp.run(u32(self.rom, ABILITY12 + 8), STOPS, limit=2000), "ret")
        self.assertEqual(cp.r[0], 1)                                           # ability 12 test: allowed
        cp = self.vegeta(VEGETA_SSJ, cooldown=0x500)
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = rec(VEGETA), PLAYER, STACK, RET | 1
        self.assertEqual(cp.run(u32(self.rom, ABILITY12 + 12), STOPS, limit=2000), "ret")
        self.assertEqual(cp.states, [(PLAYER, REVERT_MSG)])                    # ability 12 action: revert


if __name__ == "__main__":
    unittest.main()
