r"""
test_fullpower_hud.py - Tests for patches.fullpower_hud (trial 2026-10-25): the full-power Super Saiyan (r28 stretch)
                        shows the yellow ki row and plays no aura sound loop for Goku and Gohan.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_fullpower_hud.py -v
Builds build_list_trial_fullpower.txt in memory (from r40 an alias of build_list.txt): "before" = the list up to
fullpower_hud (r39 + relay_cooldown, pinned by SHA-1), "rom" = before + fullpower_hud only. New code is decoded with thumb_dis (never with the encoder) and run with
tests.test_bf_ki_pool.Cpu2 (thumb_dis text; stretch_on, pool_ref and bf_ki_pool's hud_draw run for real; the
vanilla Super Saiyan enter, the vanilla HUD draw and the ARM divide are stubs). Expected values are restated from
docs\tasks\2026-10-25-fullpower-hud\fullpower-hud-trial.md, the r39 bytes and the vanilla listings, never imported
from the patch module.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
from patches import fullpower_hud
from rom.rom_space import Allocator
from tests.test_bf_ki_pool import EP_TABLE, HUD, HUD_TILE, OAM, RAM, REGS, RET, STACK, STOPS, cpu
from rom.thumb_dis import listing

# ===== constants (brief, r39 reads, vanilla listings) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_fullpower.txt"
BEFORE_SHA1 = "22943be822a97d279f06d7ad31b02cdc5196f136"    # r39 + relay_cooldown (= the cooldown trial ROM, 2026-10-25)
SSJ_VT, SSJ2_VT, RAGE_VT, HUD_VT, TRANSFORM_VT = 0x08024C58, 0x0888DE24, 0x08024E4C, 0x0802408C, 0x08025D9C
ENTER_WORD, HUD_WORD = 0x24C60, 0x2409C                   # SSJ vtable +8, HUD vtable +0x10
VANILLA_ENTER, VANILLA_LEAVE, RAGE_ENTER = 0x08017377, 0x08017393, 0x08017159
R39_HUD_DRAW, R39_HUD_KEY = 0x0890A0EF, 0x0890A11D         # bf_ki_pool hud_draw | 1, hud_key | 1 in r39
STRETCH_ON = 0x0889A8B1
SOUND_TABLE, AURA = 0x080E15B0, 55
HUD_VANILLA, DIV = 0x08008BEE, 0x08021F30
GOHAN, GOKU, VEGETA = 0, 4, 2
EXPANSION = (0x800000, 0xF00000)

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def slot(rom: bytes, vt: int, k: int) -> int:
    return (vt + u32(rom, vt - ROM_BASE + k)) & 0xFFFFFFFF


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("fullpower_hud")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["fullpower_hud"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["fullpower_hud"])
    return _CACHE


def words(rom: bytes, lo: int, hi: int) -> list:
    """File offsets of the aligned ROM words whose value is in [lo, hi)."""
    vals = memoryview(rom[: len(rom) & ~3]).cast("I")
    return [4 * i for i, w in enumerate(vals) if lo <= w < hi]


def texts(rom: bytes, start: int, end: int) -> list:
    out = []
    for a, t in listing(rom, start, (end - start) // 2):
        if a >= end:
            break
        out.append(t)
    return out


# ===== list, checks, sites =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "fullpower_hud" in dev:                           # approved in r40: the trial list is an alias of dev
            self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev)
            self.assertEqual(dev[dev.index("fullpower_hud") - 1], "relay_cooldown")
            return
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["fullpower_hud"])

    def test_before_is_r39_plus_relay_cooldown(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), BEFORE_SHA1)

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["fullpower_hud"] = {}
        with self.assertRaises(ValueError):
            fullpower_hud.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                                       # the two words are no longer r39 either
        with self.assertRaises(ValueError):
            fullpower_hud.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        stretch = b["alloc_before"].notes["fullpower_ssj"]["stretch_on"]
        for off in (ENTER_WORD, HUD_WORD, 0x17376 + 0x16, 0x21F30, stretch + 3, R39_HUD_KEY - 1 - ROM_BASE + 0x10,
                    0x90A000, 0x88DC54 + 20 * 5 + 0x10, 0x88DC54 + 20 * 20 + 0x13):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                fullpower_hud.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_needs_the_r39_notes(self):
        base = log2_build.BASE.read_bytes()
        rom = bytearray(base) + b"\xFF" * (log2_build.ROM_SIZE - len(base))
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            fullpower_hud.apply(rom, Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION))
        self.assertEqual(bytes(rom), snap)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.at, cls.size, cls.lab = cls.n["code"], cls.n["size"], cls.n["labels"]

    def test_r39_words_are_the_vanilla_enter_and_the_pool_hud(self):
        self.assertEqual(slot(self.before, SSJ_VT, 8), VANILLA_ENTER)
        self.assertEqual(slot(self.before, SSJ_VT, 0xC), VANILLA_LEAVE)
        self.assertEqual(slot(self.before, HUD_VT, 0x10), R39_HUD_DRAW)

    def test_hook_words_name_the_new_code(self):
        self.assertEqual(slot(self.rom, SSJ_VT, 8), self.lab["enter_fp"] | 1)
        self.assertEqual(slot(self.rom, HUD_VT, 0x10), self.lab["hud_fp"] | 1)
        self.assertEqual(slot(self.rom, SSJ_VT, 0xC), VANILLA_LEAVE)               # leave stays vanilla

    def test_ssj2_rage_and_transform_keep_the_loop(self):
        self.assertEqual(slot(self.rom, SSJ2_VT, 8), VANILLA_ENTER)                # Super Saiyan 2 enter
        self.assertEqual(slot(self.rom, SSJ2_VT, 0xC), VANILLA_LEAVE)
        self.assertEqual(slot(self.rom, RAGE_VT, 8), RAGE_ENTER)                   # Rage enter (sound 55 too)
        self.assertEqual(slot(self.rom, TRANSFORM_VT, 0), 0x080155A9)              # state 35 enter: sound 55
        self.assertEqual(slot(self.rom, TRANSFORM_VT, 0xC), 0x080155F7)            # state 35 leave: stop

    def test_r39_to_new_diff_is_two_words_and_the_code(self):
        sites = [(ENTER_WORD, 4), (HUD_WORD, 4), (self.at, self.size)]
        changed = [i for c in range(0, len(self.rom), 0x10000) if self.rom[c:c + 0x10000] != self.before[c:c + 0x10000]
                   for i in range(c, c + 0x10000) if self.rom[i] != self.before[i]]
        self.assertEqual([i for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        for s, n in sites:
            self.assertTrue(any(s <= i < s + n for i in changed), f"rom:0x{s:X}")
        self.assertEqual(sorted((s, n) for s, n, _ in self.n["sites"]), sorted(sites))

    def test_code_was_free_and_only_the_hooks_name_it(self):
        self.assertTrue(EXPANSION[0] <= self.at and self.at + self.size <= EXPANSION[1])
        self.assertEqual(self.at % 4, 0)
        self.assertEqual(set(self.before[self.at:self.at + self.size]), {0xFF})
        lo, hi = ROM_BASE + self.at, ROM_BASE + self.at + self.size
        self.assertEqual(words(self.before, lo, hi), [])
        self.assertEqual(words(self.rom, lo, hi), [])                              # absolute: none
        for vt, k in ((SSJ_VT, 8), (HUD_VT, 0x10)):                                # base-relative: the two hooks
            self.assertTrue(lo <= slot(self.rom, vt, k) < hi)
            self.assertFalse(lo <= slot(self.before, vt, k) < hi)

    def test_sound_55_is_the_looping_aura(self):
        e = SOUND_TABLE - ROM_BASE + 12 * AURA
        self.assertEqual(e, 0xE1844)
        self.assertEqual(u32(self.rom, e + 4) & 0xFF, 1)                           # flags byte: bit 0 = loop
        want = ["push {r4,lr}", "ldr r0,=0x086f7e50", "mov r1,#0xa5", "ldr r2,=0x080e15b0", "lsl r1,r1,#2",
                "add r1,r1,r2", "ldr r4,=0x000005c4", "ldr r0,[r0,#0x0]", "mov r2,#0x40", "mov r3,#0x0",
                "add r0,r0,r4", "bl 0x801fc9c", "pop {r4,pc}"]
        self.assertEqual(texts(self.rom, 0x08017376, 0x08017392), want)            # 0xA5 x 4 = 0x294 = 55 x 12


class DecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.lab = b["rom"], b["notes"]["labels"]

    def test_enter_gate_decodes_to_the_design(self):
        a = self.lab["enter_fp"]
        got = texts(self.rom, a, self.lab["hud_fp"])
        want = ["push {lr}", f"ldr r3,={STRETCH_ON:#010x}", f"bl {self.lab['via_r3']:#x}", "pop {r3}", "mov lr,r3",
                "cmp r2,#0x0", f"beq {self.lab['enter_old']:#x}", "ldr r3,=0x03000e90", "ldrb r3,[r3,#0x0]",
                "cmp r3,#0x0", f"beq {self.lab['enter_quiet']:#x}", "cmp r3,#0x4", f"bne {self.lab['enter_old']:#x}",
                "bx lr", f"ldr r2,={VANILLA_ENTER:#010x}", "bx r2"]
        self.assertEqual(got, want)

    def test_hud_entry_uses_the_hud_draw_frame(self):
        got = texts(self.rom, self.lab["hud_fp"], self.lab["ep_fill"])
        self.assertEqual(got[:3], ["push {r4,r5,r6,r7,lr}", "add r4,r0,#0", "add r5,r1,#0"])
        self.assertIn(f"ldr r3,={R39_HUD_KEY:#010x}", got)
        self.assertIn(f"ldr r3,={R39_HUD_DRAW:#010x}", got)
        self.assertEqual(got[got.index(f"ldr r3,={R39_HUD_KEY:#010x}") - 1], "add r6,r0,#0")

    def test_r39_hud_draw_frame_matches_the_entry(self):
        """bf_ki_pool hud_draw: push {r4-r7,lr}, r4 = HUD, r5 = OAM, r6 = steps; from hud_key on, r0-r3 and r7 are
        written before they are read, and it ends with pop {r4-r7,pc}."""
        rom = self.rom
        head = texts(rom, R39_HUD_DRAW - 1, R39_HUD_DRAW - 1 + 8)
        self.assertEqual(head, ["push {r4,r5,r6,r7,lr}", "add r4,r0,#0", "add r5,r1,#0", "mov r6,#0x0"])
        body = texts(rom, R39_HUD_KEY - 1, 0x0890A166)
        written = set()
        for t in body:
            op, _, rest = t.partition(" ")
            regs = [x.strip("[]{}#") for x in rest.split(",")]
            dst, srcs = (regs[0], regs[1:]) if op not in ("cmp", "push", "pop") and not op.startswith(("st", "b")) \
                else (None, regs)
            if op.startswith("st"):
                srcs = regs
            for s in srcs:
                if s in ("r0", "r1", "r2", "r3", "r7") and op not in ("push", "pop"):
                    self.assertIn(s, written, f"{t}: {s} read before written")
            if dst:
                written.add(dst)
            if op == "bl":
                written |= {"r0", "r1", "r2", "r3"}
        self.assertEqual(body[-2:], ["pop {r0}", "pop {r4,r5,r6,r7,pc}"])


# ===== interpreter =====

def enter_stub(cp):
    cp.entered = True
    return 0x5A5A


class EnterGateTests(unittest.TestCase):
    """New Super Saiyan enter (the vtable +8 word), run as thumb_dis text; the vanilla enter is a stub."""

    def run_enter(self, **kw):
        cp = cpu(data=built()["rom"], **kw)
        cp.entered, cp.r[0], cp.r[1] = False, 0x030021EC, 0x02010000
        out = cp.run(slot(built()["rom"], SSJ_VT, 8), {RET: "ret", VANILLA_ENTER & ~1: enter_stub})
        self.assertEqual((out, cp.r[13], cp.r[4:8]), ("ret", STACK, REGS))
        return cp.entered

    def test_gohan_and_goku_in_the_stretch_get_no_loop(self):
        self.assertFalse(self.run_enter(leader=GOHAN, entry=5, f149=True))
        self.assertFalse(self.run_enter(leader=GOKU, entry=20, f149=True))

    def test_everyone_else_and_every_other_time_is_vanilla(self):
        self.assertTrue(self.run_enter(leader=VEGETA, entry=11, f149=True))
        self.assertTrue(self.run_enter(leader=3, entry=17, f149=True))
        self.assertTrue(self.run_enter(leader=GOHAN, entry=5, f149=True, f195=True))     # Cell beaten
        self.assertTrue(self.run_enter(leader=GOKU, entry=20, f149=False))               # before the chamber
        self.assertTrue(self.run_enter(leader=GOHAN, entry=5))

    def test_vanilla_enter_gets_the_callers_registers(self):
        cp = cpu(data=built()["rom"], leader=VEGETA, entry=11, f149=True)
        seen = {}

        def stub(c):
            seen["r"] = (c.r[0], c.r[1], c.r[14] & ~1)
            return 0
        cp.r[0], cp.r[1] = 0x030021EC, 0x02010000
        cp.run(slot(built()["rom"], SSJ_VT, 8), {RET: "ret", VANILLA_ENTER & ~1: stub})
        self.assertEqual(seen["r"], (0x030021EC, 0x02010000, RET))


class HudTests(unittest.TestCase):
    """New HUD draw (the vtable +0x10 word) and, for comparison, r39's bf_ki_pool hud_draw on the same state."""

    def draw(self, entry_point: int, **kw):
        cp = cpu(data=built()["rom"], **kw)
        seen = {}

        def vanilla(cc):
            seen["args"] = (cc.r[0], cc.r[1])
            base = 0x06010000 + 32 * HUD_TILE
            for o in range(0, 0x500, 2):
                cc.store(base + o, 2, 0x0101)
            return 0
        cp.store(HUD + 0xC, 2, HUD_TILE)
        cp.store(HUD + 0x15, 1, 3)
        cp.r[0], cp.r[1] = HUD, OAM
        out = cp.run(entry_point, {**STOPS, HUD_VANILLA: vanilla, DIV: STOPS[DIV]}, limit=8000)
        self.assertEqual((out, cp.r[0], cp.r[13], cp.r[4:8]), ("ret", 0, STACK, REGS))
        self.assertEqual(seen["args"], (HUD, OAM))
        buf = bytes(cp.ram[0x06][0x10000 + 32 * HUD_TILE:0x10000 + 32 * HUD_TILE + 0x500])
        return buf, cp

    def new(self, **kw):
        return self.draw(slot(built()["rom"], HUD_VT, 0x10), **kw)

    def old(self, **kw):
        return self.draw(R39_HUD_DRAW, **kw)

    def yellow(self, steps: int) -> bytes:
        rom = built()["rom"]
        at = built()["alloc_before"].notes["bf_ki_pool"]["yellow"]
        want = bytearray([1] * 0x500)
        for i in range(steps):
            for k in range(3):
                o = u32(rom, EP_TABLE - ROM_BASE + 16 * i + 4 * k)
                want[o] = rom[at + o]
        return bytes(want)

    def test_stretch_gohan_shows_yellow_at_the_ep_fill(self):
        buf, cp = self.new(leader=GOHAN, entry=5, ep=67, mep=134, f149=True)
        fill = 67 * 49 // 134
        self.assertEqual(buf, self.yellow(fill))
        self.assertEqual((cp.load(RAM + 0xC, 1), cp.load(HUD + 0x15, 1)), (fill, 0xFF))
        self.assertEqual(cp.vram_bytes, [])
        old, _ = self.old(leader=GOHAN, entry=5, ep=67, mep=134, f149=True)
        self.assertEqual(old, b"\x01" * 0x500)                                    # r39: no yellow (root cause)

    def test_stretch_goku_full_ep_paints_49_steps(self):
        buf, cp = self.new(leader=GOKU, entry=20, ep=139, mep=139, f149=True)
        self.assertEqual(buf, self.yellow(49))
        self.assertEqual(cp.load(RAM + 0xC, 1), 49)

    def test_stretch_pool_ram_is_not_touched(self):
        _, cp = self.new(leader=GOHAN, entry=5, ep=67, mep=134, f149=True, pool=11, tag=0x8105)
        self.assertEqual((cp.load(RAM, 2), cp.load(RAM + 2, 2), cp.load(RAM + 8, 4)), (11, 0x8105, 0))

    def test_stretch_zero_ep_shows_no_yellow(self):
        buf, cp = self.new(leader=GOHAN, entry=5, ep=0, mep=134, f149=True)
        self.assertEqual((buf, cp.load(RAM + 0xC, 1)), (b"\x01" * 0x500, 0))

    def test_every_other_case_equals_r39(self):
        cases = [dict(leader=VEGETA, entry=11, pool=25, ep=10, mep=50, f149=True),       # Vegeta's pool
                 dict(leader=GOHAN, entry=5, pool=25, ep=10, mep=50, f149=True, f195=True),   # after Cell
                 dict(leader=GOHAN, entry=22, pool=134, mep=134, f149=True, f195=True),  # Super Saiyan 2
                 dict(leader=GOKU, entry=19, ep=67, mep=134, f149=True),                 # Goku base in the stretch
                 dict(leader=GOHAN, entry=5, pool=25, ep=10, mep=50)]                    # before the chamber
        for kw in cases:
            new, cn = self.new(**kw)
            old, co = self.old(**kw)
            self.assertEqual(new, old, kw)
            self.assertEqual((cn.load(RAM + 0xC, 1), cn.load(HUD + 0x15, 1)),
                             (co.load(RAM + 0xC, 1), co.load(HUD + 0x15, 1)), kw)


if __name__ == "__main__":
    unittest.main()
