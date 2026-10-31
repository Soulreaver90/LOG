r"""
test_rage_stats.py - Tests for patches.rage_stats: Rage adds +20 to STR, POW and END, as Super Saiyan 2 does.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_rage_stats.py -v
Builds the r19 patch list in memory ("before"), then rage_stats ("rom"). The apply tests run the vanilla and the
new Rage apply in the test_status interpreter on a leader record and a player in RAM, so they check what the
code writes, not its text. The status rows run the status_bonus page on the values the new apply wrote.
Source:  docs\tasks\2026-10-19-r20-build\r20-build.md (me: Rage Gohan level 40 shows 70+30, 58+42, 71+29 in r19).
"""
import copy
import importlib
import struct
import unittest

import log2_build
from rom.rom_space import Allocator
from tests.test_ssj2 import RET, read_form
from tests.test_status import PageCpu, page_state, run_page, stat_rows
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE

# ===== constants =====
R19 = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle", "cutscene_portraits", "npc_gi",
       "rage_text")
RAGE_ENTRY, SSJ2_ENTRY, RAGE_OBJECT, RAGE_SET = 4, 22, 0x030021E4, 160
VTABLE, VTABLE_WORD, OLD_APPLY = 0x08024E4C, 0x24E4C, 0x080170D8
SPEED_SET = 0x080265C4
STRUCT, PLAYER, STACK = 0x03000E90, 0x02002000, 0x03007E00
LEVEL40 = (70, 58, 71)                           # My r19 screenshot: Rage Gohan level 40
_CACHE = {}


def built() -> dict:
    if not _CACHE:
        rom = bytearray(log2_build.BASE.read_bytes()) + b"\xFF" * (log2_build.ROM_SIZE - log2_build.BASE_SIZE)
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        for name in R19:
            importlib.import_module(f"patches.{name}").apply(rom, alloc)
        _CACHE["before"], _CACHE["alloc"] = bytes(rom), copy.deepcopy(alloc)
        importlib.import_module("patches.rage_stats").apply(rom, alloc)
        _CACHE["rom"], _CACHE["notes"] = bytes(rom), alloc.notes
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def words_to(rom: bytes, value: int) -> list:
    """Aligned offsets of every ROM word equal to value."""
    pat, out, i = struct.pack("<I", value), [], rom.find(struct.pack("<I", value))
    while i >= 0:
        if i % 4 == 0:
            out.append(i)
        i = rom.find(pat, i + 1)
    return out


def rage_apply(rom: bytes) -> int:
    return (VTABLE + struct.unpack_from("<i", rom, VTABLE_WORD)[0]) & 0xFFFFFFFF & ~1


def run_apply(rom: bytes, stats: tuple, leader: int = 0) -> tuple:
    """(player bytes +0x100..+0x200, speed calls, cpu) after the Rage apply the vtable names."""
    cpu = PageCpu(rom)
    cpu.store(STRUCT, 1, leader)
    rec = STRUCT + 0xC + 0x1C * leader
    for i, v in enumerate(stats):
        cpu.store(rec + 0xA + 2 * i, 2, v << 8 | 0xA5)       # a fraction byte the apply must drop
    for i in range(0x100):
        cpu.store(PLAYER + 0x100 + i, 1, 0x5A)              # every byte the apply does not write stays 0x5A
    calls = []
    cpu.r[:8] = [0, PLAYER, 0, 0, 0x44444444, 0x55555555, 0x66666666, 0x77777777]
    cpu.r[13], cpu.r[14] = STACK, RET | 1
    stops = {SPEED_SET: lambda c: calls.append((c.r[0] - PLAYER, c.r[1])) or 0, RET: "exit"}
    if cpu.run(rage_apply(rom), stops, limit=200) != "exit":
        raise AssertionError("apply did not return")
    if cpu.r[13] != STACK or cpu.r[4:8] != [0x44444444, 0x55555555, 0x66666666, 0x77777777]:
        raise AssertionError("apply did not restore sp and r4-r7")
    return bytes(cpu.load(PLAYER + 0x100 + i, 1) for i in range(0x100)), calls, cpu


# ===== tests =====

class RageStatsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]["rage_stats"]

    # bytes

    def test_vtable_word_old_and_new(self):
        self.assertEqual(self.before[VTABLE_WORD:VTABLE_WORD + 4].hex(), "8d22ffff")     # 0x080170D9 - vtable
        self.assertEqual(rage_apply(self.before), OLD_APPLY)
        self.assertEqual(rage_apply(self.rom), self.notes["apply"] + ROM_BASE)
        self.assertEqual(u32(self.rom, VTABLE_WORD), (self.notes["apply"] + ROM_BASE + 1 - VTABLE) & 0xFFFFFFFF)

    def test_old_apply_quoted_and_kept(self):
        self.assertEqual([t for _, t in listing(self.rom, OLD_APPLY, 7)][4:],
                         ["add r0,#0x61", "mov r1,#0x64", "strb r1,[r0,#0x0]"])
        self.assertEqual(self.rom[OLD_APPLY - ROM_BASE:OLD_APPLY - ROM_BASE + 0x36],
                         self.before[OLD_APPLY - ROM_BASE:OLD_APPLY - ROM_BASE + 0x36])

    def test_rom_differs_only_at_the_word_and_new_code(self):
        new = range(self.notes["code"], self.notes["code"] + self.notes["size"])
        diff = [i for i in range(len(self.rom)) if self.rom[i] != self.before[i]]
        self.assertEqual([hex(i) for i in diff if i not in new and not VTABLE_WORD <= i < VTABLE_WORD + 4], [])
        self.assertGreaterEqual(self.notes["code"], log2_build.BASE_SIZE)
        self.assertEqual(set(self.before[self.notes["code"]:self.notes["code"] + self.notes["size"]]), {0xFF})

    def test_other_rage_methods_unchanged(self):
        for i in range(1, 8):
            self.assertEqual(u32(self.rom, VTABLE_WORD + 4 * i), u32(self.before, VTABLE_WORD + 4 * i), i)

    # behavior

    def test_level40_gives_90_78_91(self):
        new, calls, _ = run_apply(self.rom, LEVEL40)
        self.assertEqual(tuple(new[0x60:0x63]), (90, 78, 91))
        old, old_calls, _ = run_apply(self.before, LEVEL40)
        self.assertEqual(tuple(old[0x60:0x63]), (100, 100, 100))                       # vanilla flat 100
        self.assertEqual(calls, old_calls)
        self.assertEqual(calls, [(0x188, 0x40000000), (0x18C, 0x40500000)])            # Rage speeds kept
        self.assertEqual(new[:0x60] + new[0x63:], old[:0x60] + old[0x63:])             # +0x163/4 0x80, +0x184 0
        self.assertEqual((new[0x63], new[0x64], new[0x84:0x88]), (0x80, 0x80, b"\0\0\0\0"))

    def test_reads_the_leader_record(self):
        new, _, _ = run_apply(self.rom, (12, 34, 56), leader=2)
        self.assertEqual(tuple(new[0x60:0x63]), (32, 54, 76))

    def test_status_page_shows_plus_20(self):
        new, _, _ = run_apply(self.rom, LEVEL40)
        rows = stat_rows(run_page(self.rom, page_state(self.rom, LEVEL40, tuple(new[0x60:0x63]), where="menu")))
        self.assertEqual([r[0] for r in rows], ["70+20", "58+20", "71+20"])
        old, _, _ = run_apply(self.before, LEVEL40)
        rows = stat_rows(run_page(self.before, page_state(self.before, LEVEL40, tuple(old[0x60:0x63]), where="menu")))
        self.assertEqual([r[0] for r in rows], ["70+30", "58+42", "71+29"])            # My r19 screen

    def test_same_bonus_as_super_saiyan_2(self):
        rage, ssj2 = read_form(self.rom, RAGE_ENTRY), read_form(self.rom, SSJ2_ENTRY)
        self.assertEqual((rage.str_bonus, rage.pow_bonus, rage.end_bonus, rage.flat), (20, 20, 20, False))
        self.assertEqual((rage.str_bonus, rage.pow_bonus, rage.end_bonus, rage.flat),
                         (ssj2.str_bonus, ssj2.pow_bonus, ssj2.end_bonus, ssj2.flat))
        self.assertLessEqual(100 + rage.end_bonus, 127)                                 # damage uses 0x80 - END
        self.assertEqual(rage.methods[1:], read_form(self.before, RAGE_ENTRY).methods[1:])
        self.assertEqual(rage.ki_drain, 0)

    def test_rage_object_only_in_entry_4(self):
        t = u32(self.rom, 0x886C) - ROM_BASE                                            # form_reapply's table
        users = [e for e in range(23) if u32(self.rom, t + 20 * e + 0x10) == RAGE_OBJECT]
        self.assertEqual(users, [RAGE_ENTRY])
        self.assertEqual(self.rom[t + 20 * RAGE_ENTRY + 1], RAGE_SET)
        self.assertEqual([e for e in range(23) if self.rom[t + 20 * e + 4] == RAGE_ENTRY], [])   # no transform
        self.assertEqual(len(words_to(self.rom, RAGE_OBJECT)), 3)   # entry 4: vanilla, reverse-lookup, live table
        self.assertEqual(words_to(self.rom, VTABLE), [0x2330C])     # form object init pool only

    def test_apply_fails_closed(self):
        from patches import rage_stats
        b = built()
        for off in (VTABLE_WORD, OLD_APPLY - ROM_BASE + 0xA, 0x2330C, 0x17268):
            rom = bytearray(b["before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=hex(off)):
                rage_stats.apply(rom, copy.deepcopy(b["alloc"]))
            self.assertEqual(bytes(rom), snap)


if __name__ == "__main__":
    unittest.main()
