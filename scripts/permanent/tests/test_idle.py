r"""
test_idle.py - Tests for the SSJ2 idle hook (patches.ssj2_idle) and the gi Rage set 160 (patches.gohan_gi).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds the r13 patch list in memory (gohan_gi, ssj2_form, gohan_portraits, status_bonus, ssj2_idle) and the same
list without ssj2_idle. The hook runs in the test_status interpreter (PageCpu: the test_ssj2 Cpu plus mul and
hi/ls), as thumb_dis text, never through the encoder. The vanilla sequence comes from running 0x08007570 of the
base ROM in the same interpreter.
Source:  docs\research\re-outfit.md section 7, re-forms.md sections 1 and 3, aura-rage-report.md.
"""
import struct
import unittest

import log2_build
from rom.log2_sprites import set_records
from rom.rom_space import Allocator
from tests.test_ssj2 import ENTRY, read_form, table_of
from tests.test_status import PageCpu
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, rom_ptr

# ===== constants =====
BASE_ROM = log2_build.BASE.read_bytes()
PATCHES = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle")
VANILLA_TICK = 0x08007570
HOOKED, LEFT = (0x08025A84, 0x08024BA0), 0x0802588C          # state 0, state 38; state 22 stays vanilla
OBJ, STATE, STACK, RET = 0x02000400, 0x03000100, 0x03007F00, 0x0EEE0000
TICKS = 512
SHAPE_SHIFT = 3                                               # one aura shape per 8 ticks (r17; r13-r16: 2)
RAGE_ENTRY, RAGE_SCRIPT = 4, 0x3EA365
OP_TABLE = 0x3B5C00                                           # script base ops (op 0 = push byte)
SET_TABLE_LITERAL = 0x959C

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        import importlib
        for upto in (len(PATCHES) - 1, len(PATCHES)):
            rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
            alloc = Allocator(len(rom), log2_build.EXPANSION)
            for name in PATCHES[:upto]:
                importlib.import_module(f"patches.{name}").apply(rom, alloc)
            _CACHE[upto] = (bytes(rom), alloc.notes)
    return {"before": _CACHE[len(PATCHES) - 1][0], "rom": _CACHE[len(PATCHES)][0], "notes": _CACHE[len(PATCHES)][1]}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def set_addr(rom: bytes, set_id: int) -> int:
    return u32(rom, u32(rom, SET_TABLE_LITERAL) - ROM_BASE + 4 * (set_id - 7))


def tick_target(rom: bytes, vt: int) -> int:
    return (vt + struct.unpack_from("<i", rom, vt + 4 - ROM_BASE)[0]) & 0xFFFFFFFF


def run_ticks(rom: bytes, entry: int, set_ptr: int, row: int, seed: int, n: int = TICKS) -> list:
    """obj+0x14 after each of n calls of the routine at `entry`, the way 0x0800772A calls a state tick."""
    cpu = PageCpu(rom)
    cpu.store(OBJ + 0x48, 4, set_ptr)
    cpu.store(OBJ + 0x4C, 4, row)
    cpu.store(OBJ + 0x12, 2, seed)
    out = []
    for _ in range(n):
        cpu.r[0], cpu.r[1], cpu.r[13], cpu.r[14] = STATE, OBJ, STACK, RET | 1
        cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
        if cpu.run(entry, {RET: "ret"}) != "ret":
            raise AssertionError("tick did not return")
        assert cpu.r[1] == OBJ and cpu.r[13] == STACK and cpu.r[4:8] == [0x44444444, 0x55555555, 0x66666666,
                                                                          0x77777777]
        out.append(cpu.load(OBJ + 0x14, 2))
    return out


def formula(seed: int, n: int = TICKS) -> list:
    out = []
    for k in range(1, n + 1):
        t = (seed + k) & 0xFFFF
        out.append((1 if (t & 0xFF) > 0xF0 else 0) * 3 + (t >> SHAPE_SHIFT) % 3)
    return out


def vanilla(seed: int, n: int = TICKS) -> list:
    return [1 if ((seed + k) & 0xFF) > 0xF0 else 0 for k in range(1, n + 1)]


class IdleHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.hook = cls.notes["ssj2_idle"]["idle"] + ROM_BASE

    def test_vtable_words_are_base_relative_and_repointed(self):
        for vt in HOOKED + (LEFT,):
            self.assertEqual(tick_target(BASE_ROM, vt), VANILLA_TICK | 1, hex(vt))
        for vt in HOOKED:
            self.assertEqual(tick_target(self.rom, vt), self.hook | 1, hex(vt))
        self.assertEqual(tick_target(self.rom, LEFT), VANILLA_TICK | 1)
        self.assertEqual(self.rom[VANILLA_TICK - ROM_BASE:VANILLA_TICK - ROM_BASE + 0x18],
                         BASE_ROM[VANILLA_TICK - ROM_BASE:VANILLA_TICK - ROM_BASE + 0x18])

    def test_only_two_vtable_words_change_in_the_base_8mb(self):
        diff = [i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]]
        self.assertEqual(diff, sorted(o for vt in HOOKED for o in range(vt + 4 - ROM_BASE, vt + 8 - ROM_BASE)))

    def test_vanilla_interpreter_matches_the_vanilla_rule(self):     # the interpreter against the original code
        for seed in (0, 0xEF, 0xFFF0):
            self.assertEqual(run_ticks(BASE_ROM, VANILLA_TICK | 1, 0, 0, seed), vanilla(seed))

    def test_sets_159_and_160_follow_the_formula(self):
        for set_id in (159, 160):
            s = set_addr(self.rom, set_id)
            self.assertEqual(s, self.notes["gohan_gi"][f"set_{set_id}"] + ROM_BASE)
            for seed in (0, 0x7B, 0xEE, 0xFFF0):
                for vt in HOOKED:
                    got = run_ticks(self.rom, tick_target(self.rom, vt), s, s + 0x4C, seed)
                    self.assertEqual(got, formula(seed), (set_id, seed, hex(vt)))

    def test_every_shape_appears(self):                       # seed 0: body 1 windows 0xF1 and 0x1F1 give 3, 4, 5
        for set_id in (159, 160):
            s = set_addr(self.rom, set_id)
            for vt in HOOKED:
                got = run_ticks(self.rom, tick_target(self.rom, vt), s, s + 0x4C, 0)
                self.assertEqual(set(got), set(range(6)), (set_id, hex(vt)))

    def test_shape_sequence_is_one_shape_per_8_ticks(self):   # r17 (me: "a bit fast"): was 4 ticks
        s = set_addr(self.rom, 159)
        got = run_ticks(self.rom, self.hook | 1, s, s + 0x4C, 0xFFFF, 32)   # ticks 0-31 (0x10000 wraps to 0)
        self.assertEqual(got, [0] * 8 + [1] * 8 + [2] * 8 + [0] * 8)
        got = run_ticks(self.rom, self.hook | 1, s, s + 0x4C, 0xEF, 25)     # ticks 0xF0-0x108, body 1 from 0xF1
        self.assertEqual(got, [0] + [3] * 7 + [4] * 8 + [2] * 8 + [0])

    def test_shift_instruction_bytes(self):                   # lsr r2,r2,#19 = 0x0CD2; r13-r16 had #18 = 0x0C92
        h = self.hook - ROM_BASE
        self.assertEqual(self.rom[h + 0x20:h + 0x24].hex(), "0204" + "d20c")   # lsl r2,r0,#16 ; lsr r2,r2,#19

    def test_divide_by_3_is_exact_over_the_shifted_range(self):   # header note: tick >> 3 < 0x2000
        self.assertTrue(all((x * 0x5556) >> 16 == x // 3 for x in range((0xFFFF >> SHAPE_SHIFT) + 1)))
        self.assertTrue(all((x * 0x5556) >> 16 == x // 3 for x in range(0x8000)))

    def test_other_sets_keep_the_vanilla_tick(self):
        for set_id in (157, 158, 56, 58, 60, 137):            # gi base, gi SSJ, armor, armor Rage, Goku, Vegeta
            s = set_addr(self.rom, set_id)
            for seed in (0, 0xEE):
                self.assertEqual(run_ticks(self.rom, self.hook | 1, s, s + 0x4C, seed), vanilla(seed), set_id)

    def test_other_rows_keep_the_vanilla_tick(self):          # state 22 sets anim row 22 (set + 0x1AC)
        for set_id in (159, 160):
            s = set_addr(self.rom, set_id)
            self.assertEqual(run_ticks(self.rom, self.hook | 1, s, s + 0x1AC, 0xEE), vanilla(0xEE), set_id)
        enter = [t for _, t in listing(BASE_ROM, 0x08007588, 12)]
        self.assertEqual(enter[9:12], ["ldr r0,[r4,#0x48]", "add r0,#0xff", "add r0,#0xad"])

    def test_anim_0_has_6_records_per_dir(self):
        for set_id, want in ((159, 6), (160, 6), (157, 2), (158, 2)):
            recs = set_records(self.rom, set_addr(self.rom, set_id) - ROM_BASE)
            for d in range(4):
                self.assertEqual(sum(1 for r in recs if (r["anim"], r["dir"]) == (0, d)), want, (set_id, d))

    def test_hook_disassembles_as_expected(self):
        n = self.notes["ssj2_idle"]
        s159, s160 = (set_addr(self.rom, s) for s in (159, 160))
        h = self.hook
        want = ["ldr r2,[r1,#0x48]", f"ldr r3,={s159:#010x}", "cmp r2,r3", f"beq {h + 0x12:#x}",
                f"ldr r3,={s160:#010x}", "cmp r2,r3", f"beq {h + 0x12:#x}", "ldr r2,=0x08007571", "bx r2",
                "add r2,#0x4c", "ldr r3,[r1,#0x4c]", "cmp r2,r3", f"bne {h + 0xe:#x}", "ldrh r0,[r1,#0x12]",
                "add r0,#0x1", "strh r0,[r1,#0x12]", "lsl r2,r0,#16", "lsr r2,r2,#19", "ldr r3,=0x00005556",
                "mul r3,r2", "lsr r3,r3,#16", "sub r2,r2,r3", "sub r2,r2,r3", "sub r2,r2,r3", "lsl r0,r0,#24",
                "lsr r0,r0,#24", "cmp r0,#0xf1", f"blt {h + 0x3a:#x}", "add r2,#0x3", "strh r2,[r1,#0x14]", "bx lr"]
        self.assertEqual([t for _, t in listing(self.rom, h, len(want))], want)
        self.assertGreaterEqual(n["code"], 0x800000)

    def test_apply_fails_closed(self):
        from patches import ssj2_idle
        for off, junk in ((HOOKED[0] + 4 - ROM_BASE, b"\0\0\0\0"), (LEFT + 4 - ROM_BASE, b"\1\0\0\0"),
                          (VANILLA_TICK - ROM_BASE, b"\0")):
            rom = bytearray(self.before)
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes.update({k: dict(v) for k, v in self.notes.items() if k != "ssj2_idle"})
            with self.assertRaises(ValueError, msg=hex(off)):
                ssj2_idle.apply(rom, alloc)
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run gohan_gi first"):
            ssj2_idle.apply(bytearray(self.before), Allocator(len(self.before), [(0xF00000, 0x100000)]))


class RageSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.notes = b["rom"], b["notes"]

    def test_cell_script_pushes_160_in_the_same_4_bytes(self):
        self.assertEqual(BASE_ROM[RAGE_SCRIPT:RAGE_SCRIPT + 6].hex(), "1d0200740249")    # push 0,58 ; ext_73
        self.assertEqual(self.rom[RAGE_SCRIPT:RAGE_SCRIPT + 6].hex(), "000000a00249")    # push 0 ; push 160 ; ext_73
        diff = [i for i in range(RAGE_SCRIPT - 0x40, RAGE_SCRIPT + 0x40) if self.rom[i] != BASE_ROM[i]]
        self.assertEqual(diff, [RAGE_SCRIPT, RAGE_SCRIPT + 1, RAGE_SCRIPT + 3])

    def test_script_op_0_pushes_a_zero_extended_byte(self):    # the VM handler of op 0
        handler = u32(BASE_ROM, OP_TABLE) & ~1
        code = [t for _, t in listing(BASE_ROM, handler, 11)]
        self.assertEqual(code[4], "ldrb r3,[r2,#0x0]")           # the byte after the op
        self.assertEqual(code[9:11], ["str r3,[r0,#0x4]", "bx lr"])   # pushed as a word

    def test_rage_entry_and_reverse_lookup_name_160(self):
        live = table_of(self.rom)
        copy = u32(self.rom, 0x42F0) - ROM_BASE
        for t in (live, copy):
            self.assertEqual(self.rom[t + ENTRY * RAGE_ENTRY + 1], 160)
            self.assertEqual(next(e for e in range(22) if self.rom[t + ENTRY * e + 1] == 160), RAGE_ENTRY)
        self.assertEqual(set_addr(self.rom, 160), self.notes["gohan_gi"]["set_160"] + ROM_BASE)

    def test_rage_form_and_entry_unchanged_but_the_set(self):
        got, want = read_form(self.rom, RAGE_ENTRY), read_form(BASE_ROM, RAGE_ENTRY)
        self.assertEqual(got._replace(entry=None), want._replace(entry=None))
        self.assertEqual((got.str_bonus, got.flat, got.ki_drain), (100, True, 0))
        e, base = bytearray(got.entry), BASE_ROM[0x1D967C + ENTRY * RAGE_ENTRY:0x1D967C + ENTRY * (RAGE_ENTRY + 1)]
        self.assertEqual(e[1], 160)
        e[1] = base[1]
        self.assertEqual(bytes(e), base)                         # +0 = 3 (ability lock), form object 0x030021E4
        self.assertEqual(self.rom[0x17000:0x17500], BASE_ROM[0x17000:0x17500])   # every form method and pool

    def test_set_160_has_the_set_58_layout(self):
        base58 = rom_ptr(BASE_ROM, SET_TABLE + 4 * (58 - 7))
        off = set_addr(self.rom, 160) - ROM_BASE
        rows = lambda rom, o: {(r["anim"], r["dir"]): 0 for r in set_records(rom, o)}   # noqa: E731
        self.assertEqual(set(rows(self.rom, off)), set(rows(BASE_ROM, base58)))
        count = lambda rom, o, k: sum(1 for r in set_records(rom, o) if (r["anim"], r["dir"]) == k)   # noqa: E731
        for k in rows(BASE_ROM, base58):
            self.assertEqual(count(self.rom, off, k), 6 if k[0] == 0 else count(BASE_ROM, base58, k), k)
        self.assertEqual(self.rom[off:off + 0x4C], BASE_ROM[base58:base58 + 0x4C])   # header and boxes
        # r13 list: gohan_gi leaves word 58 (vanilla armor Rage). r30 superperfect_cell repoints it (its own test)
        self.assertEqual(set_addr(self.rom, 58), base58 + ROM_BASE)


if __name__ == "__main__":
    unittest.main()
