r"""
test_piccolo_z_start.py - Tests for patches.piccolo_z_start (trial 2026-11-12, phase 1 of two): Super Namek
                          from the start, with the Super Namek HP heal removed.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_piccolo_z_start.py -v
Builds build_list_trial_piccolo.txt in memory. "dev" is the dev master, "rom" is dev plus the module, so
every expected value is a measured difference, not a restatement of the module's own constants.
Method:  tests.test_ssj2.Cpu (through tests.test_bf_ki_pool.Cpu2) runs the real ROM code: slot cycling
         0x08004284, the ability 11 test 0x080134F2, the vanilla Super Namek tick 0x08017400 and the ki
         pool tick. The base form tick, the ARM divide and the player state methods are stubs. The tests do
         not run the frame loop, sound or DMA timing.
Sources: docs\tasks\2026-11-12-piccolo-z-start\brief.md; bible B0460 (ext 82 sets record +0x14 bit 5),
         B0452 (the Super Namek heal), B0541 (a vtable word is an offset from the vtable start).
"""
import copy
import struct
import unittest

import log2_build
import log_paths
from rom import log2_save as ls
from tests.test_bf_ki_pool import PLAYER, RAM, STOPS, STRUCT, Cpu2, cpu, rec
from tests.test_bf_hud import labels
from tests.test_ssj2 import M32, REGNO

# ===== constants (read on the dev master and the base ROM, never imported from the patch) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_piccolo.txt"
RET, STACK = 0x0EEE0000, 0x03007E00
BASE_TICK = 0x08017028

DEFAULT_RECORDS, RECORD, PICCOLO = 0x1D9548, 0x1C, 1
PICCOLO_FLAGS = DEFAULT_RECORDS + RECORD * PICCOLO + 0x14
FLAGS_DEV, FLAGS_TRIAL = 0x40, 0x60                      # slot 3 alone, then slot 3 and slot 2
NAMEK_SLOT, NAMEK_ABILITY, PICCOLO_ENTRY, SUPER_NAMEK = 2, 11, 6, 7
SLOT_CYCLE, ABILITY_TEST = 0x08004284, 0x080134F2
ABILITY_TABLE = 0x1D9900
MAP_INFO, COMBAT_WORD = 0x03002080, 0x03004100           # [[0x03002080 + 8] + 0xC] must not be 0

NAMEK_VTABLE, TICK_SLOT, VANILLA_NAMEK_TICK = 0x08024ABC, 0x04, 0x08017401
STATE25_VTABLE, END_SLOT, VANILLA_TRANSFORM_END = 0x08025CE0, 0x14, 0x0801563D
VANILLA_NAMEK_TICK_BODY = 0x08017400
FLAG_132 = (STRUCT + 0xB4 + 132 // 8, 1 << (132 % 8))    # the Kami fusion flag (bible B0816)
HEAL_STEP = 0x290                                        # max HP x 0x290 >> 16, about 1 % (bible B0543)
DRAIN_STEP = 0x0CCD                                      # 1 every 20 frames
EXPECTED_RUNS = (0x024AC0, 0x025CF4, 0x1D9578, 0x909FFC)
MOCKUP = log_paths.PICCOLO_Z_MOCKUPS
WEST_CITY, WEST_CITY_POS = (4, 6, 1), (656, 368)     # the 6,1 warp landing, bible B1186

# Save code that must stay byte equal, or an old save stops loading the way it did.
SAVE_PATHS = ((0x1800, 0xD0, "Continue and the slot load 0x0800180C"),
              (0x3C24, 0x4A, "save_defaults 0x08003C24"),
              (0x3E42, 0x32, "flag_test 0x08003E42 (0x1C) and flag_set 0x08003E5E (0x16)"))

_CACHE = {}


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        rom, alloc = log2_build.assemble(log2_build.BASE, dev)
        _CACHE["dev"] = bytes(rom)
        log2_build.apply_patches(rom, alloc, names[len(dev):])
        _CACHE["rom"] = bytes(rom)
        _CACHE["notes"] = copy.deepcopy(alloc.notes["piccolo_z_start"])
    return _CACHE


def target(rom: bytes, vtable: int, slot: int) -> int:
    """A vtable word is an offset from the vtable START, never from the slot (bible B0541)."""
    return (vtable + u32(rom, vtable - ROM_BASE + slot)) & M32


def piccolo(hp: int = 500, ep: int = 120, mep: int = 134, pool=None, flag132: bool = False, **kw) -> Cpu2:
    """A Cpu on the TRIAL ROM with Piccolo (leader 1) leading in Super Namek (entry 7)."""
    cp = cpu(leader=PICCOLO, entry=SUPER_NAMEK, hp=hp, ep=ep, mep=mep, pool=pool, data=built()["rom"], **kw)
    if flag132:
        cp.store(FLAG_132[0], 1, FLAG_132[1])
    return cp


def run_tick(cp: Cpu2, at: int, form_object: int) -> Cpu2:
    cp.r[0], cp.r[1], cp.r[13], cp.r[14] = form_object, PLAYER, STACK, RET | 1
    stops = {**STOPS, BASE_TICK: lambda c: 0}
    assert cp.run(at, stops, limit=4000) == "ret"
    return cp


class Cpu3(Cpu2):
    """Cpu2 plus the two-operand ALU forms slot cycling 0x08004284 uses: `lsl rd,rs` and `and rd,rs`."""

    def _step(self, nxt, text):
        op, _, rest = text.partition(" ")
        a = rest.split(",")
        if op in ("lsl", "lsr") and len(a) == 2 and not a[1].startswith("#"):
            d, k = REGNO[a[0]], self.r[REGNO[a[1]]] & 0xFF
            x = self.r[d]
            self.r[d] = self._nz(((x << k) if op == "lsl" else (x >> k)) & M32)
            return nxt
        if op in ("and", "orr", "eor", "bic") and len(a) == 2:
            d, y = REGNO[a[0]], self.r[REGNO[a[1]]]
            x = self.r[d]
            self.r[d] = self._nz({"and": x & y, "orr": x | y, "eor": x ^ y, "bic": x & ~y}[op] & M32)
            return nxt
        return super()._step(nxt, text)


def cycle_template(which: str) -> tuple:
    """One L press on the record `which` build's own template makes, every story flag clear.

    The gate byte is READ from the build, never chosen here. That is what makes this test exercise the
    deciding mechanism: change the module's constant and this test moves with the ROM, not with the test.
    Returns (result, new slot, the ability that slot fires, the gate byte it ran on)."""
    rom = built()[which]
    at, template = rec(PICCOLO), DEFAULT_RECORDS + RECORD * PICCOLO
    cp = Cpu3(rom)
    for i in range(RECORD):
        cp.store(at + i, 1, rom[template + i])                            # the whole template record
    cp.r[0], cp.r[13], cp.r[14] = at, STACK, RET | 1
    assert cp.run(SLOT_CYCLE, {RET: "ret"}) == "ret"
    assert all(cp.load(STRUCT + 0xB4 + i, 1) == 0 for i in range(50))     # no story flag is set
    slot = cp.load(at + 9, 1)
    return cp.r[0], slot, cp.load(at + 0x18 + slot, 1), u32(rom, template + 0x14)


def cycle_record(rom: bytes, record: bytes) -> list:
    """Every ability id L can select, run on a record's OWN bytes (a save slot's, for instance)."""
    at = rec(PICCOLO)
    cp = Cpu3(rom)
    for i, b in enumerate(record):
        cp.store(at + i, 1, b)
    out = []
    for _ in range(4):
        cp.r[0], cp.r[13], cp.r[14] = at, STACK, RET | 1
        assert cp.run(SLOT_CYCLE, {RET: "ret"}) == "ret"
        out.append(record[0x18 + cp.load(at + 9, 1)])
    return sorted(set(out))


def ability_test(cp: Cpu2, record: int, ability: int) -> int:
    cp.store(MAP_INFO + 8, 4, COMBAT_WORD)
    cp.store(COMBAT_WORD + 0xC, 4, 1)                    # a map in combat
    cp.store(MAP_INFO + 0xC, 4, COMBAT_WORD)
    cp.store(COMBAT_WORD + 8, 4, 0)                      # cooldown 0
    cp.r[0], cp.r[13], cp.r[14] = record, STACK, RET | 1
    word = u32(built()["rom"], ABILITY_TABLE + 16 * ability + 8)
    assert cp.run(word & ~1, {RET: "ret"}) == "ret"
    return cp.r[0]


def ability_action(cp: Cpu2, record: int, ability: int) -> list:
    """Run the ability's ACTION (table +0xC) and return the player states it asked for."""
    cp.r[0], cp.r[1], cp.r[13], cp.r[14] = record, PLAYER, STACK, RET | 1
    word = u32(built()["rom"], ABILITY_TABLE + 16 * ability + 0xC)
    assert cp.run(word & ~1, STOPS) == "ret"
    return [state for _, state in cp.states]


# ===== 1. the gate: Super Namek from the start =====

class Gate(unittest.TestCase):
    def test_the_dev_master_keeps_slot_2_shut(self):
        self.assertEqual(u32(built()["dev"], PICCOLO_FLAGS), FLAGS_DEV)
        self.assertEqual(FLAGS_DEV >> (3 + NAMEK_SLOT) & 1, 0)

    def test_the_trial_opens_slot_2_and_changes_nothing_else_in_the_record(self):
        dev, rom = built()["dev"], built()["rom"]
        at = DEFAULT_RECORDS + RECORD * PICCOLO
        self.assertEqual(u32(rom, PICCOLO_FLAGS), FLAGS_TRIAL)
        self.assertEqual(FLAGS_TRIAL >> (3 + NAMEK_SLOT) & 1, 1)
        self.assertEqual(rom[at:at + 0x14], dev[at:at + 0x14])
        self.assertEqual(rom[at + 0x18:at + RECORD], dev[at + 0x18:at + RECORD])

    def test_slot_2_is_the_namek_transform_and_the_entry_is_unchanged(self):
        at = DEFAULT_RECORDS + RECORD * PICCOLO
        rom = built()["rom"]
        self.assertEqual(rom[at + 0x18 + NAMEK_SLOT], NAMEK_ABILITY)
        self.assertEqual(rom[at + 8], PICCOLO_ENTRY)

    def test_slot_cycling_reaches_the_transform_with_every_story_flag_clear(self):
        """The story flags are all zero here, so this is a new game before the Kami fusion.

        The gate byte comes from the built ROM, so this runs the real cycler on the real patched value."""
        self.assertEqual(cycle_template("rom"), (1, NAMEK_SLOT, NAMEK_ABILITY, FLAGS_TRIAL))

    def test_on_the_dev_master_the_same_press_never_leaves_slot_3(self):
        self.assertEqual(cycle_template("dev"), (0, 3, 2, FLAGS_DEV))

    def test_bit_4_is_not_the_transform_gate(self):
        """Bit 4 opens slot 1, which is ability 8. Clearing it leaves Super Namek reachable, and
        clearing bit 5 is what shuts it. The bit number alone never says which FORM a slot fires."""
        rom = built()["rom"]
        at = DEFAULT_RECORDS + RECORD * PICCOLO
        record = bytearray(rom[at:at + RECORD])
        for flags, expected in ((0x7F, [2, 8, 9, NAMEK_ABILITY]), (0x6F, [2, 9, NAMEK_ABILITY]),
                                (0x5F, [2, 8, 9]), (0x4F, [2, 9])):
            with self.subTest(flags=hex(flags)):
                struct.pack_into("<I", record, 0x14, flags)
                self.assertEqual(cycle_record(rom, bytes(record)), expected)

    def test_the_ability_11_test_does_not_read_the_kami_flag(self):
        out = []
        for flag in (False, True):
            cp = piccolo(flag132=flag)
            at = rec(PICCOLO)
            cp.store(at + 8, 1, PICCOLO_ENTRY)
            cp.store(at + 4, 2, 120)
            out.append(ability_test(cp, at, NAMEK_ABILITY))
        self.assertEqual(out, [1, 1])

    def test_the_action_enters_the_namek_transform_state_with_the_kami_flag_clear(self):
        """The last link of the B path. 0x25 is the Namek transform state (bible B1712)."""
        for flag in (False, True):
            with self.subTest(flag132=flag):
                cp = piccolo(flag132=flag)
                at = rec(PICCOLO)
                cp.store(at + 8, 1, PICCOLO_ENTRY)
                self.assertEqual(ability_action(cp, at, NAMEK_ABILITY), [0x25])

    def test_the_action_reverts_when_he_is_already_super_namek(self):
        cp = piccolo()
        at = rec(PICCOLO)
        cp.store(at + 8, 1, SUPER_NAMEK)
        self.assertEqual(ability_action(cp, at, NAMEK_ABILITY), [0x24])

    def test_the_ability_table_still_names_the_vanilla_test_and_action(self):
        dev, rom = built()["dev"], built()["rom"]
        off = ABILITY_TABLE + 16 * NAMEK_ABILITY
        self.assertEqual(rom[off:off + 16], dev[off:off + 16])


# ===== 2. the tick: no heal, and the drain still ends the form =====

class Tick(unittest.TestCase):
    def test_the_namek_tick_word_moves_from_the_vanilla_tick_to_the_pool_tick(self):
        self.assertEqual(target(built()["dev"], NAMEK_VTABLE, TICK_SLOT), VANILLA_NAMEK_TICK)
        self.assertEqual(target(built()["rom"], NAMEK_VTABLE, TICK_SLOT), labels()["tick_ssj"] | 1)

    def test_the_transform_end_word_moves_to_fill_end(self):
        self.assertEqual(target(built()["dev"], STATE25_VTABLE, END_SLOT), VANILLA_TRANSFORM_END)
        self.assertEqual(target(built()["rom"], STATE25_VTABLE, END_SLOT), labels()["fill_end"] | 1)

    def test_the_vanilla_namek_tick_really_did_heal(self):
        """The baseline the owner asked to remove: about 1 % of max HP at every drain step."""
        cp = piccolo(hp=500, ep=120)
        cp.store(PLAYER + 0x184, 4, 0x10000 - DRAIN_STEP)
        run_tick(cp, VANILLA_NAMEK_TICK_BODY, 0x030021F0)
        self.assertEqual(cp.load(rec(PICCOLO), 2), 500 + (906 * HEAL_STEP >> 16))
        self.assertEqual(cp.load(rec(PICCOLO) + 4, 2), 119)

    def test_the_pool_tick_drains_and_never_touches_hp(self):
        cp = piccolo(hp=500, ep=120, pool=50)
        cp.store(RAM + 8, 4, 0x10000 - DRAIN_STEP)
        run_tick(cp, labels()["tick_ssj"], 0x030021F0)
        self.assertEqual(cp.load(RAM, 2), 49)
        self.assertEqual(cp.load(rec(PICCOLO), 2), 500)

    def test_hp_is_unchanged_over_a_run_of_drain_steps(self):
        cp = piccolo(hp=500, ep=120, pool=50)
        for _ in range(8):
            cp.store(RAM + 8, 4, 0x10000 - DRAIN_STEP)
            run_tick(cp, labels()["tick_ssj"], 0x030021F0)
        self.assertEqual(cp.load(RAM, 2), 42)
        self.assertEqual(cp.load(rec(PICCOLO), 2), 500)

    def test_the_drain_still_ends_the_form(self):
        cp = piccolo(hp=500, ep=120, pool=0)
        cp.store(RAM + 8, 4, 0x10000 - DRAIN_STEP)
        run_tick(cp, labels()["tick_ssj"], 0x030021F0)
        self.assertEqual(cp.states, [(PLAYER, 0x24)])

    def test_a_knocked_out_piccolo_does_not_revert(self):
        cp = piccolo(hp=0, ep=120, pool=0)
        cp.store(RAM + 8, 4, 0x10000 - DRAIN_STEP)
        run_tick(cp, labels()["tick_ssj"], 0x030021F0)
        self.assertEqual(cp.states, [])

    def test_the_transform_end_fills_the_pool(self):
        cp = piccolo(ep=10, mep=134, pool=3, tag=0)
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = 0x03002188, PLAYER, STACK, RET | 1
        seen = {}

        def vanilla(cc):
            seen["ran"] = True
            cc.store(rec(PICCOLO) + 8, 1, SUPER_NAMEK)
            return 0

        stops = {**STOPS, VANILLA_TRANSFORM_END & ~1: vanilla}
        self.assertEqual(cp.run(labels()["fill_end"], stops), "ret")
        self.assertTrue(seen.get("ran"))
        self.assertEqual(cp.load(RAM, 2), 134)
        self.assertEqual(cp.load(RAM + 2, 2), 0x8000 | PICCOLO << 8 | SUPER_NAMEK)


# ===== 3. pool_ref: the Namek accept, and every other form as before =====

class PoolRefAccept(unittest.TestCase):
    def ref(self, entry: int, leader: int = PICCOLO) -> int:
        cp = cpu(leader=leader, entry=entry, data=built()["rom"])
        cp.r[13], cp.r[14] = STACK, RET | 1
        self.assertEqual(cp.run(labels()["pool_ref"], STOPS), "ret")
        return cp.r[0]

    def test_super_namek_now_gets_the_pool(self):
        self.assertEqual(self.ref(SUPER_NAMEK), RAM)

    def test_the_saiyan_forms_are_unchanged(self):
        self.assertEqual(self.ref(5, leader=0), RAM)      # Gohan Super Saiyan
        self.assertEqual(self.ref(22, leader=0), RAM)     # Gohan Super Saiyan 2
        self.assertEqual(self.ref(11, leader=2), RAM)     # Vegeta Super Saiyan

    def test_the_base_and_non_pool_forms_still_get_nothing(self):
        for entry, leader in ((PICCOLO_ENTRY, PICCOLO), (3, 0), (4, 0), (10, 2), (8, 2)):
            with self.subTest(entry=entry):
                self.assertEqual(self.ref(entry, leader=leader), 0)


# ===== 4. old saves =====

class Saves(unittest.TestCase):
    def test_the_patch_writes_four_runs_and_none_of_them_is_save_code(self):
        dev, rom = built()["dev"], built()["rom"]
        runs, i = [], 0
        while i < len(dev):
            if dev[i] != rom[i]:
                j = i
                while j < len(dev) and dev[j] != rom[j]:
                    j += 1
                runs.append((i, j - i))
                i = j
            else:
                i += 1
        self.assertEqual(tuple(at for at, _ in runs), EXPECTED_RUNS)
        for at, size, name in SAVE_PATHS:
            with self.subTest(name=name):
                self.assertEqual(rom[at:at + size], dev[at:at + size])

    def test_the_save_image_layout_is_untouched(self):
        """No new save field: the slot is still 0x164 data bytes of six 28-byte records plus the flags."""
        self.assertEqual((ls.SLOT_DATA, ls.CHAR_SIZE, ls.O_CHARS, ls.O_STORY), (0x164, 28, 0x0C, 0xB4))
        self.assertEqual(ls.O_CHARS + ls.CHAR_SIZE * 6, ls.O_STORY)
        self.assertGreater(PICCOLO_FLAGS, 0x100000)       # the template is ROM, not save data

    def test_a_stored_save_still_decodes_and_keeps_its_own_record_bits(self):
        """The template serves a NEW game only. A slot image overwrites it, so an old save is unchanged.

        It also shows the gate is really record +0x14 bit 5: these are post-fusion saves and every slot
        already carries it, which is why the owner's seeded save shows the tick change, not the gate."""
        ram = ls.read_ram((log_paths.SAVES / "log2_lv40_postcell.sav").read_bytes())
        for n in range(ls.SLOT_COUNT):
            with self.subTest(slot=n):
                slot = bytes(ram[ls.slot_range(n)])
                self.assertEqual(len(slot), ls.SLOT_SIZE)
                at = ls.O_CHARS + ls.CHAR_SIZE * PICCOLO
                record = slot[at:at + ls.CHAR_SIZE]
                self.assertEqual(record[8], PICCOLO_ENTRY)
                self.assertEqual(record[0x18 + NAMEK_SLOT], NAMEK_ABILITY)
                self.assertEqual(struct.unpack_from("<I", record, 0x14)[0], 0x7F)


# ===== 5. the two demo saves beside the trial ROM =====

class DemoSaves(unittest.TestCase):
    """The saves are the deliverable, so they are pinned by running the GAME's cycler on their bytes."""

    def slots(self, name: str) -> list:
        path = MOCKUP / name
        if not path.exists():
            self.skipTest(f"{name} is not built")
        ram = ls.read_ram(path.read_bytes())
        return [bytes(ram[ls.slot_range(n)]) for n in range(ls.SLOT_COUNT)]

    def check(self, name: str, flags: int, abilities: list) -> None:
        rom = built()["rom"]
        for n, slot in enumerate(self.slots(name)):
            with self.subTest(slot=n):
                at = ls.O_CHARS + ls.CHAR_SIZE * PICCOLO
                record = slot[at:at + ls.CHAR_SIZE]
                self.assertEqual(slot[ls.O_LEADER], PICCOLO)
                self.assertEqual((slot[ls.O_ZONE], slot[ls.O_AREA], slot[ls.O_VAR]), WEST_CITY)
                self.assertEqual(struct.unpack_from("<hh", slot, ls.O_POS), WEST_CITY_POS)
                self.assertEqual(struct.unpack_from("<I", record, 0x14)[0], flags)
                self.assertEqual(cycle_record(rom, record), abilities)

    def test_the_control_save_cannot_reach_the_transform(self):
        self.check("log2_piccolo_z_v1_gate_shut.sav", 0x4F, [2, 9])

    def test_the_demo_save_reaches_the_transform(self):
        self.check("log2_piccolo_z_v1_z_from_start.sav", 0x6F, [2, 9, NAMEK_ABILITY])

    def test_neither_save_changes_another_character(self):
        seed = ls.read_ram((log_paths.MASTER_BUILDS / "log2_poc_r40.sav").read_bytes())
        for name in ("log2_piccolo_z_v1_gate_shut.sav", "log2_piccolo_z_v1_z_from_start.sav"):
            for n, slot in enumerate(self.slots(name)):
                was = bytes(seed[ls.slot_range(n)])
                for c in range(len(ls.CHAR_NAMES)):
                    at = ls.O_CHARS + ls.CHAR_SIZE * c
                    with self.subTest(save=name, slot=n, who=ls.CHAR_NAMES[c]):
                        if c == PICCOLO:
                            continue
                        self.assertEqual(slot[at:at + ls.CHAR_SIZE], was[at:at + ls.CHAR_SIZE])


if __name__ == "__main__":
    unittest.main()
