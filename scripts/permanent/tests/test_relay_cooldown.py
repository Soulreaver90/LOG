r"""
test_relay_cooldown.py - Tests for patches.relay_cooldown (trial 2026-10-25): a scripted fighter change (ext 70)
                         clears the party transform cooldown; Switch Characters keeps vanilla behavior.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_relay_cooldown.py -v
Builds build_list_trial_cooldown.txt in memory (from r40 an alias of build_list.txt): "before" = the list up to
relay_cooldown (r39, pinned by SHA-1), "rom" = before + relay_cooldown only (later r40 modules are not applied). The wrapper is decoded with thumb_dis (never with the encoder) and run with
tests.test_ssj2.Cpu, which executes thumb_dis text. Expected values are restated from
docs\tasks\2026-10-24-form-cooldown\relay-cooldown-trial.md, form-cooldown-report.md and the r39 bytes, never
imported from the patch module. Function sizes are scripts\permanent\disasm\data\codemap.json's.
"""
import copy
import hashlib
import re
import struct
import unittest

import log2_build
from patches import relay_cooldown
from rom.rom_space import Allocator
from tests.test_ssj2 import Cpu
from rom.thumb_dis import listing

# ===== constants (brief, study report, r39 reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_cooldown.txt"
R39_SHA1 = "aa51dc16da5f6b633c0f50dc566864fe43f89ff0"
HOOK, VANILLA_EXT70 = 0x3B5E40, 0x0800A785               # ext table 0x083B5D28 + 4 x 70
EXT70_BODY = (0xA784, "08b5fff77bff9d48006af9f7a1fb08bd")
EXT_TABLE_POOLS = [0x921C, 0x92DC]                       # every ROM word naming 0x083B5D28 (@0x08009232 reads 0x92DC)
SAVE_PTR_WORD, SAVE, COOLDOWN = 0x6F7E54, 0x03000E90, 0x03000E98
WRAPPER_LEN = 28
EXPANSION = (0x800000, 0xF00000)                         # allocator regions (log2_build: below ART_REGION)
# Menu swap path, byte equal to r39: (rom offset, length, name)
MENU_PATH = ((0x11172, 264, "switch_characters"), (0xA680, 140, "set_leader"), (0x3ED4, 50, "appearance_revert"),
             (0x247A8 + 0x24, 4, "party screen vtable +0x24 (switch_characters)"), (0xA784, 16, "ext 70 body"),
             (0x9224, 44, "ext dispatch @0x08009224"), (0x3B6088, 4, "word rom:0x3B6088 (0x083B5F70 + 4 x 70)"),
             (0x3B5EF4, 4, "ext 115 table word (set_leader, no revert)"))
# Interpreter run (fix_proof.py setup): Vegeta after the relay
TEST_WORD = 0x1D9900 + 12 * 16 + 8                       # ability 12 (Saiyan transform) test word
MAP_INFO, FLAG_BYTES = 0x03002080, SAVE + 0xB4
VEGETA, ENTRY_VEGETA = 2, 9
STACK, RET, CONTEXT = 0x03007E00, 0x08000001, 0x03004321

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def padded() -> bytearray:
    base = log2_build.BASE.read_bytes()
    return bytearray(base) + b"\xFF" * (log2_build.ROM_SIZE - len(base))


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("relay_cooldown")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["relay_cooldown"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["relay_cooldown"])
    return _CACHE


def words(rom: bytes, lo: int, hi: int) -> list:
    """File offsets of the aligned ROM words whose value is in [lo, hi)."""
    vals = memoryview(rom[: len(rom) & ~3]).cast("I")                  # host is little-endian, as rom_space
    return [4 * i for i, w in enumerate(vals) if lo <= w < hi]


def wrapper_lines(rom: bytes, at: int) -> list:
    return listing(rom, at + ROM_BASE, 9)


# ===== tests =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "relay_cooldown" in dev:                          # approved in r40: the trial list is an alias of dev
            self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev)
            self.assertEqual(dev[dev.index("relay_cooldown") - 1], "bf_ki_pool")     # first r40 line
            return
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["relay_cooldown"])

    def test_before_is_r39(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R39_SHA1)

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["relay_cooldown"] = {}
        with self.assertRaises(ValueError):
            relay_cooldown.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                          # the word is no longer vanilla either
        with self.assertRaises(ValueError):
            relay_cooldown.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        for off in (HOOK, HOOK + 3, EXT70_BODY[0] + 4, EXT70_BODY[0] + 15, SAVE_PTR_WORD, SAVE_PTR_WORD + 3):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                relay_cooldown.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_the_hook_word_refuses(self):
        for site in ((HOOK + 2, 1, "other"), HOOK + 3):      # triple shape and bare-offset shape
            rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
            alloc.notes["other_module"] = {"sites": [site]}
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(site)):
                relay_cooldown.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_padded_base_gets_the_same_wrapper(self):
        rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        relay_cooldown.apply(rom, alloc)
        at, r39_at = alloc.notes["relay_cooldown"]["wrapper"], built()["notes"]["wrapper"]
        self.assertEqual(rom[at:at + WRAPPER_LEN], built()["rom"][r39_at:r39_at + WRAPPER_LEN])
        self.assertEqual(u32(rom, HOOK), ROM_BASE + at + 1)


class WrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.at = cls.n["wrapper"]

    def test_table_word_names_the_wrapper(self):
        self.assertEqual(u32(self.before, HOOK), VANILLA_EXT70)
        self.assertEqual(0x083B5D28 - ROM_BASE + 4 * 70, HOOK)
        self.assertEqual(u32(self.rom, HOOK), ROM_BASE + self.at + 1)      # Thumb bit set
        self.assertEqual(self.at % 4, 0)                                    # the pool offsets assume 4-aligned
        self.assertTrue(EXPANSION[0] <= self.at and self.at + WRAPPER_LEN <= EXPANSION[1])
        self.assertEqual(self.n["size"], WRAPPER_LEN)

    def test_every_dispatch_reads_the_hooked_table(self):
        for rom in (self.before, self.rom):
            self.assertEqual(words(rom, 0x083B5D28, 0x083B5D29), EXT_TABLE_POOLS)

    def test_vanilla_ext70_has_no_other_name(self):
        self.assertEqual(words(self.before, VANILLA_EXT70 - 1, VANILLA_EXT70 + 1), [HOOK])
        self.assertEqual(words(self.rom, VANILLA_EXT70 - 1, VANILLA_EXT70 + 1), [self.at + 0x14])   # wrapper pool

    def test_wrapper_was_free_and_only_the_hook_names_it(self):
        self.assertEqual(set(self.before[self.at:self.at + WRAPPER_LEN]), {0xFF})
        lo, hi = ROM_BASE + self.at, ROM_BASE + self.at + WRAPPER_LEN
        self.assertEqual(words(self.before, lo, hi), [])
        self.assertEqual(words(self.rom, lo, hi), [HOOK])

    def test_wrapper_decodes_to_the_design(self):
        a = ROM_BASE + self.at
        want = ["push {r4,lr}", "ldr r3,=0x0800a785", f"bl {a + 0x12:#x}", "ldr r1,=0x086f7e50", "ldr r1,[r1,#0x4]",
                "mov r2,#0x0", "str r2,[r1,#0x8]", "pop {r4,pc}", "bx r3"]
        self.assertEqual([t for _, t in wrapper_lines(self.rom, self.at)], want)
        self.assertEqual(u32(self.rom, self.at + 0x14), VANILLA_EXT70)      # pool words, read raw
        self.assertEqual(u32(self.rom, self.at + 0x18), 0x086F7E50)

    def test_calls_the_vanilla_ext70_with_r0_untouched(self):
        lines = wrapper_lines(self.rom, self.at)
        texts = [t for _, t in lines]
        bl_at = texts.index(next(t for t in texts if t.startswith("bl ")))
        bx_addr = [a for a, t in lines if t == "bx r3"][0]
        self.assertEqual(int(texts[bl_at].split()[1], 16), bx_addr)          # bl lands on bx r3
        for t in texts[:bl_at]:                                             # nothing before the call writes r0
            self.assertIsNone(re.match(r"\w+ r0,", t), t)
        writes_r3 = [t for t in texts[2:bl_at] if re.match(r"\w+ r3,", t)]
        self.assertEqual(writes_r3, [])                                     # r3 still holds 0x0800a785 at bx
        self.assertEqual(self.rom[EXT70_BODY[0]:EXT70_BODY[0] + 16].hex(), EXT70_BODY[1])

    def test_stores_zero_to_the_cooldown_word(self):
        texts = [t for _, t in wrapper_lines(self.rom, self.at)]
        self.assertEqual(texts[3:7], ["ldr r1,=0x086f7e50", "ldr r1,[r1,#0x4]", "mov r2,#0x0", "str r2,[r1,#0x8]"])
        self.assertEqual(u32(self.rom, SAVE_PTR_WORD), SAVE)                # [0x086F7E50 +4] = save struct
        self.assertEqual(SAVE + 8, COOLDOWN)

    def test_returns_with_the_stack_balanced(self):
        texts = [t for _, t in wrapper_lines(self.rom, self.at)]
        self.assertEqual((texts[0], texts[7]), ("push {r4,lr}", "pop {r4,pc}"))
        self.assertEqual([t for t in texts if "sp" in t or t.startswith(("push", "pop"))], [texts[0], texts[7]])

    def test_r39_to_new_diff_is_the_hook_and_the_wrapper(self):
        chunks = [c for c in range(0, len(self.rom), 0x10000) if self.rom[c:c + 0x10000] != self.before[c:c + 0x10000]]
        changed = [i for c in chunks for i in range(c, c + 0x10000) if self.rom[i] != self.before[i]]
        sites = [(HOOK, 4), (self.at, WRAPPER_LEN)]
        self.assertEqual([i for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        for s, n in sites:
            self.assertTrue(any(s <= i < s + n for i in changed), f"rom:0x{s:X}")
        self.assertEqual(sorted((s, n) for s, n, _ in self.n["sites"]), sorted(sites))

    def test_menu_swap_path_is_byte_equal_to_r39(self):
        for off, n, name in MENU_PATH:
            self.assertEqual(self.rom[off:off + n], self.before[off:off + n], name)


class InterpreterTests(unittest.TestCase):
    """The ROM's own code, run as thumb_dis text: wrapper (vanilla ext 70 stubbed), then the ability 12 test."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.at = b["rom"], b["notes"]["wrapper"]

    def vegeta_after_relay(self, cooldown: int) -> Cpu:
        cpu = Cpu(self.rom)
        cpu.store(COOLDOWN, 4, cooldown)
        cpu.store(SAVE, 1, VEGETA)                                          # leader after push 2 ; ext 70
        rec = SAVE + 0xC + 0x1C * VEGETA
        cpu.store(rec + 4, 2, 120)                                          # EP
        cpu.store(rec + 6, 2, 120)                                          # max EP
        cpu.store(rec + 8, 1, ENTRY_VEGETA)
        cpu.store(rec + 0x14, 1, 0x20)                                      # transform slot enabled
        cpu.store(MAP_INFO + 0xC, 4, 1)                                     # in a fight
        cpu.store(FLAG_BYTES + 149 // 8, 1, 1 << (149 & 7))                 # Cell Games: flag 149 set, 195 clear
        return cpu

    def ability_12(self, cpu: Cpu) -> int:
        cpu.r[0], cpu.r[13], cpu.r[14] = SAVE + 0xC + 0x1C * VEGETA, STACK, RET
        cpu.run(u32(self.rom, TEST_WORD), {RET & ~1: "done"})
        return cpu.r[0]

    def test_without_the_wrapper_the_test_refuses(self):
        self.assertEqual(self.ability_12(self.vegeta_after_relay(0x500)), 0)

    def test_wrapper_clears_the_cooldown_and_keeps_registers(self):
        cpu, seen = self.vegeta_after_relay(0x500), []

        def vanilla_ext70(c):
            seen.append(c.r[0])
            return 0x1234

        cpu.r[0], cpu.r[4], cpu.r[13], cpu.r[14] = CONTEXT, 0xBEEF, STACK, RET
        stop = cpu.run(u32(self.rom, HOOK), {VANILLA_EXT70 & ~1: vanilla_ext70, RET & ~1: "done"})
        self.assertEqual(stop, "done")
        self.assertEqual(seen, [CONTEXT])                                   # vanilla ext 70 got the script context
        self.assertEqual((cpu.r[0], cpu.r[4], cpu.r[13]), (0x1234, 0xBEEF, STACK))
        self.assertEqual(cpu.load(COOLDOWN, 4), 0)
        self.assertEqual(cpu.load(SAVE, 1), VEGETA)                         # the leader byte is not touched
        self.assertEqual(self.ability_12(cpu), 1)


if __name__ == "__main__":
    unittest.main()
