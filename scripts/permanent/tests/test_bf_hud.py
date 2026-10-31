r"""
test_bf_hud.py - Tests for patches.bf_hud and patches.bf_ki_pool (r39): the HUD v2b mockup baked into the build.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_bf_hud.py -v
Builds build_list_dev.txt in memory: "before" = the list up to bf_hud (r38), "hud" = before + bf_hud,
"rom" = hud + bf_ki_pool (r39). Expected values are restated from the mockup builders
(scripts\one-time\2026-10-24-hud-ki\build_mock1.py, proto\build_proto_b.py) and the r38 bytes, not imported from the patches.
Equivalence: r39 = the v2b mockup with its window moved from rom:0xE11000 to the allocated window, every word that
names the old window moved by the same delta (relocate). The mockup files are read only; a test skips without them.
The interpreter tests of the pool code are in test_bf_ki_pool.py (ported from proto\test_proto_b.py).
"""
import copy
import hashlib
import math
import struct
import unittest
from pathlib import Path
from unittest import mock

import log2_build
from rom import log2_save
import log_paths
from patches import bf_hud, bf_ki_pool

# ===== constants (mockup builders, r38 reads) =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF
BUILD = log_paths.BUILDS
MOCKS = log_paths.HUD_KI_MOCKUPS
V2B, V2, MOCK1 = MOCKS / "log2_poc_r38_bfhud2b.gba", MOCKS / "log2_poc_r38_bfhud2.gba", MOCKS / "log2_poc_r36_bfhud.gba"
V2B_SHA1, V2_SHA1 = "f5f5ee730346695c25035871378efebc084165b1", "5f17f8fc9c31e7c60b44543c8868d02b18b8fd6c"
R38_SHA1 = "7a7cb85fa5873c4a44d360b33b6755d4e71e18e3"
R38, R39 = BUILD / "log2_poc_r38.gba", BUILD / "log2_poc_r39.gba"
BF = log2_build.ROOT / "data" / "roms" / "Dragon Ball Z - Buu's Fury (USA).gba"

MOCK_WINDOW, MOCK_SIZE, YELLOW_LEN = 0xE11000, 0x824, 0x500
RAM = 0x03003A00
PAL, BF_PAL = 0x1DA6C8, 0x5652C
SKIP_IDX, LIVE_PAL_SKIP = frozenset({0, 172, 174, 178, 218, 239}), frozenset({168})
EP_TABLE, ABILITY_TABLE = 0x083B5658, 0x1D9900
WRAP_ABILITIES = (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 13)
HOOKS = {                                              # build_proto_b.HOOKS: (vtable, slot, r38 target | 1, label)
    "ssj_tick": (0x08024C58, 0x04, 0x0889A8C7, "tick_ssj"),
    "ssj2_tick": (0x0888DE24, 0x04, 0x0889A81D, "tick_ssj2"),
    "transform_end": (0x08025D9C, 0x14, 0x0801563D, "fill_end"),
    "revert_end": (0x080256AC, 0x14, 0x080157AF, "empty_end"),
    "hud_draw": (0x0802408C, 0x10, 0x08008BEF, "hud_draw"),
    "ki_blast": (0x08025D48, 0x04, 0x08014DF5, "st34"),
    "beam48": (0x08025CB8, 0x08, 0x08015249, "st48"),
    "beam49": (0x08025F70, 0x08, 0x0801539B, "st49"),
    "ball51": (0x08025CCC, 0x08, 0x080156B7, "st51"),
    "hold46": (0x080258B4, 0x08, 0x08015079, "st46"),
}
HOOK_OFFSETS = sorted(vt - ROM_BASE + slot for vt, slot, _, _ in HOOKS.values())
ABILITY_WORDS = sorted(ABILITY_TABLE + 16 * n + k for n in WRAP_ABILITIES for k in (8, 12))
MOCK1_REGIONS = ((0x8E80, 4), (0x8E88, 4), (0x6D7B54, 0x300), (0x3B5358, 0x300), (0x3B5658, 0x310),
                 (0x3B5968, 0x228), (0x3B5B90, 0x50), (0x3B5BE0, 0x14))
BOSS = ((0x6D60F4, 0x3C0), (0x6D64B4, 0x200))
NAMED_WORD = (0x5851EC, 0x0890989C)                    # vanilla data word naming the first chunk the allocator gave
SKIPPED = 0x9092C0

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        i = names.index("bf_hud")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["bf_hud"])
        _CACHE.update(hud=bytes(rom), alloc_hud=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["bf_ki_pool"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


def u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE if a >= ROM_BASE else a)[0]


def diff(a: bytes, b: bytes) -> list:
    return [i for x, y in runs_of(a, b) for i in range(x, y)]


def runs_of(a: bytes, b: bytes) -> list:
    """[(start, end)] of the byte runs that differ; equal 4 KB chunks are skipped whole."""
    out, n = [], len(a)
    for c in range(0, n, 0x1000):
        if a[c:c + 0x1000] == b[c:c + 0x1000]:
            continue
        for i in range(c, min(c + 0x1000, n)):
            if a[i] != b[i]:
                if out and out[-1][1] == i:
                    out[-1] = (out[-1][0], i + 1)
                else:
                    out.append((i, i + 1))
    return out


def labels() -> dict:
    return built()["notes"]["bf_ki_pool"]["labels"]


def window() -> tuple:
    """(file offset, size) of the r39 pool window."""
    n = built()["notes"]["bf_ki_pool"]
    return n["window"], n["size"]


def relocate(mockup: bytes, before: bytes, at: int, size: int = MOCK_SIZE) -> tuple:
    """The mockup with its window moved to `at`; words naming the old window move by the same delta.
    Returns (bytes, [file offsets of moved words inside the new window])."""
    delta, lo, hi = at - MOCK_WINDOW, ROM_BASE + MOCK_WINDOW, ROM_BASE + MOCK_WINDOW + size
    out = bytearray(mockup)
    out[MOCK_WINDOW:MOCK_WINDOW + size] = before[MOCK_WINDOW:MOCK_WINDOW + size]
    out[at:at + size] = mockup[MOCK_WINDOW:MOCK_WINDOW + size]
    moved = []
    for p in range(at, at + size, 4):
        if lo <= u32(out, p) < hi:
            struct.pack_into("<I", out, p, u32(out, p) + delta)
            moved.append(p)
    for vt, slot, _, _ in HOOKS.values():
        p = vt - ROM_BASE + slot
        if lo <= (vt + u32(out, p)) & M32 < hi:
            struct.pack_into("<I", out, p, (u32(out, p) + delta) & M32)
    for p in ABILITY_WORDS:
        if lo <= u32(out, p) < hi:
            struct.pack_into("<I", out, p, u32(out, p) + delta)
    return bytes(out), moved


# ===== shared models (ported from scripts\one-time\2026-10-24-hud-ki: common.py, hudsim.py, proto\bossim.py) =====

def pal5(rom: bytes, off: int) -> list:
    return [(c & 31, (c >> 5) & 31, (c >> 10) & 31) for c in struct.unpack_from("<256H", rom, off)]


def lab(c: tuple) -> tuple:
    def lin(v):
        v = (v * 255 / 31) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c)
    x, y, z = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047, 0.2126 * r + 0.7152 * g + 0.0722 * b, \
        (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = [t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116 for t in (x, y, z)]
    return 116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])


class Remap:
    """BF OBJ index -> nearest LoG II OBJ index by CIELAB (build_mock1.py method), skipping the given indices."""

    def __init__(self, rom: bytes, bf: bytes, extra_skip: frozenset = frozenset()):
        self.pl, self.pb = pal5(rom, PAL), pal5(bf, BF_PAL)
        self.ll = {i: lab(self.pl[i]) for i in range(256) if i not in SKIP_IDX | extra_skip}
        self.map = {0: 0}

    def __call__(self, v: int) -> int:
        if v not in self.map:
            lb = lab(self.pb[v])
            self.map[v] = min(self.ll, key=lambda i: math.dist(self.ll[i], lb))
        return self.map[v]


def bf_rom() -> bytes:
    if "bf" not in _CACHE:
        _CACHE["bf"] = BF.read_bytes()
    return _CACHE["bf"]


def live_remap() -> Remap:
    if "live" not in _CACHE:
        _CACHE["live"] = Remap(built()["before"], bf_rom(), LIVE_PAL_SKIP)
    return _CACHE["live"]


def log2_fills(rom: bytes, hpf: int, epf: int, exp_fill: int, icon: int, cd_idx: int = 0) -> bytearray:
    """The LoG II HUD draw @0x08008BEE from the HUD object's cached fills (hudsim.log2_fills)."""
    buf = bytearray(rom[0x6D7B54:0x6D7B54 + 0x300] + rom[icon - ROM_BASE:icon - ROM_BASE + 0x200])
    for base, fill, steps, n, stride in ((0x3B5358, hpf, 48, 3, 16), (0x3B5658, epf, 49, 3, 16)):
        for i in range(fill, steps):
            for k in range(n):
                buf[u32(rom, base + stride * i + 4 * k)] = 1
    for i in range(u32(rom, 0x3B5B90 + 0x50 + 4 * cd_idx)):
        buf[u32(rom, 0x3B5B90 + 4 * i)] = 1
    for i in range(exp_fill, 69):
        for k in range(2):
            buf[u32(rom, 0x3B5968 + 8 * i + 4 * k)] = 1
    return buf


def log2_bar(rom: bytes, fill: int) -> bytearray:
    """The LoG II boss bar draw @0x0801055C: image 0x086D64B4, steps fill..59 blanked (bossim.log2_bar)."""
    buf = bytearray(rom[0x6D64B4:0x6D66B4])
    for i in range(fill, 60):
        for k in range(4):
            buf[u32(rom, 0x6D60F4 + 16 * i + 4 * k)] = 1
    return buf


def words_into(rom: bytes, lo: int, hi: int, skip: tuple = ()) -> dict:
    """Aligned words naming GBA [lo, hi): 'abs' anywhere; 'rel' (vtable slot 0-15 base-relative) only in the code
    region and the ssj2_form vtable, where those vtables live (common.words_into)."""
    words = memoryview(rom[:len(rom) & ~3]).cast("I")
    out = {"abs": [4 * k for k, w in enumerate(words) if lo <= w < hi and not any(s <= 4 * k < e for s, e in skip)],
           "rel": []}
    for s, e in ((0x0, 0x28724), (0x88DE24, 0x88DE3C)):
        for p in range(s, e, 4):
            if any(a <= p < b for a, b in skip):
                continue
            for slot in range(16):
                if lo <= (ROM_BASE + p - 4 * slot + words[p // 4]) & M32 < hi:
                    out["rel"].append((p, slot))
    return out


def need(*paths: Path) -> None:
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise unittest.SkipTest(f"missing {missing}")


# ===== tests =====

class BaseTests(unittest.TestCase):
    def test_before_is_r38(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R38_SHA1)

    def test_build_list_has_the_hud_after_chamber_spar(self):                  # r40 appends four modules
        names = built()["names"]
        i = names.index("bf_hud")
        self.assertEqual(names[i - 1:i + 2], ["chamber_spar", "bf_hud", "bf_ki_pool"])

    def test_remap_is_the_cielab_remap_of_the_r38_palette(self):
        before, bf = built()["before"], bf_rom()
        hud, live = Remap(before, bf), live_remap()
        hud_idx = set(bf[0x7137D8:0x7137D8 + 0x300]) | set(bf[0x7148D8:0x7148D8 + 0x200])
        live_idx = set(bf[0x7196E4:0x7196E4 + 0x200]) | {
            bf[0x713AD8 + u32(bf, 0x08071F40 + 16 * j + 4 * k)] for j in range(41) for k in range(3)}
        self.assertEqual(set(bf_hud.BF_TO_LOG2), hud_idx | live_idx)
        for v in hud_idx:
            self.assertEqual(bf_hud.BF_TO_LOG2[v], hud(v), v)
        for v in live_idx:
            self.assertEqual(bf_hud.BF_TO_LOG2[v], live(v), v)


class EquivalenceTests(unittest.TestCase):
    """r39 behaves as v2b: the same bytes, the window moved and every word naming it moved with it."""

    @classmethod
    def setUpClass(cls):
        need(V2B, V2)
        b = built()
        cls.before, cls.rom = b["before"], b["rom"]
        cls.v2b, cls.v2 = V2B.read_bytes(), V2.read_bytes()
        cls.at, cls.size = window()

    def test_mockup_files(self):
        self.assertEqual(hashlib.sha1(self.v2b).hexdigest(), V2B_SHA1)
        self.assertEqual(hashlib.sha1(self.v2).hexdigest(), V2_SHA1)
        self.assertEqual(self.size, MOCK_SIZE)
        self.assertEqual(set(self.v2b[MOCK_WINDOW + MOCK_SIZE:MOCK_WINDOW + 0x1000]), {0xFF})

    def test_r39_is_v2b_relocated(self):
        want, moved = relocate(self.v2b, self.before, self.at)
        self.assertEqual(self.rom, want)
        self.assertEqual(len(moved), 1)                        # the YELLOW literal of put_px, nothing else
        self.assertEqual(u32(self.rom, moved[0]), self.at + ROM_BASE)
        self.assertGreater(moved[0], labels()["put_px"] - ROM_BASE)
        self.assertEqual(set(self.rom[MOCK_WINDOW:MOCK_WINDOW + 0x1000]), {0xFF})

    def test_every_v2b_run_has_its_counterpart(self):
        delta = self.at - MOCK_WINDOW
        hooks = {vt - ROM_BASE + slot: vt for vt, slot, _, _ in HOOKS.values()}
        for a, b in runs_of(self.before, self.v2b):
            for x in range(a, b):
                if MOCK_WINDOW <= x < MOCK_WINDOW + MOCK_SIZE:
                    continue                                   # window bytes: test_r39_is_v2b_relocated
                w = x & ~3
                if w in hooks:
                    vt = hooks[w]
                    self.assertEqual((vt + u32(self.rom, w)) & M32, (vt + u32(self.v2b, w) + delta) & M32, hex(w))
                elif w in ABILITY_WORDS:
                    self.assertEqual(u32(self.rom, w), u32(self.v2b, w) + delta, hex(w))
                else:
                    self.assertEqual(self.rom[x], self.v2b[x], hex(x))

    def test_v2_to_r39_is_the_state_46_word_and_stub(self):
        """The v2 mockup relocated the same way differs from r39 only by the v2b fix (proto test_v2_to_v2b)."""
        want, _ = relocate(self.v2, self.before, self.at)
        fix = built()["notes"]["bf_ki_pool"]["fix"]
        self.assertEqual([(a, b - a) for a, b in runs_of(want, self.rom)], [(0x258BC, 4), (fix, 8)])

    def test_rebase_equals_mockup_1(self):
        need(MOCK1)
        mock1 = MOCK1.read_bytes()
        for off, n in MOCK1_REGIONS:
            self.assertEqual(self.rom[off:off + n], mock1[off:off + n], hex(off))
        for p in built()["notes"]["bf_hud"]["icons"]:
            self.assertEqual(self.rom[p:p + 0x200], mock1[p:p + 0x200], hex(p))
        for fills in ((48, 49, 0, 0x086D7754, 0), (46, 41, 0, 0x086D947C, 4), (24, 12, 30, 0x086DAE7C, 2)):
            self.assertEqual(log2_fills(self.rom, *fills), log2_fills(mock1, *fills), fills)


class LayoutTests(unittest.TestCase):
    """Ported from proto\test_proto_b.py class Layout (8 tests), against the r39 build."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom = b["before"], b["rom"]

    def test_hooked_vtable_words_name_new_code(self):
        lb = labels()
        for name, (vt, slot, target, label) in HOOKS.items():
            self.assertEqual((vt + u32(self.before, vt + slot)) & M32, target, name)
            self.assertEqual((vt + u32(self.rom, vt + slot)) & M32, lb[label] | 1, name)

    def test_ability_words_name_stubs_with_vanilla_literals(self):
        from rom.thumb_dis import listing
        lb = labels()
        for n in WRAP_ABILITIES:
            for k, tag in ((8, "t"), (12, "a")):
                stub = lb[f"ab{n}{tag}"]
                self.assertEqual(u32(self.rom, ABILITY_TABLE + 16 * n + k), stub | 1)
                text = [t for _, t in listing(self.rom, stub, 2)]
                self.assertEqual(text[0], f"ldr r3,={u32(self.before, ABILITY_TABLE + 16 * n + k):#010x}")
                self.assertEqual(text[1], f"b {lb['swap_rec']:#x}")
        for n in (5, 11, 12):
            off = ABILITY_TABLE + 16 * n
            self.assertEqual(self.rom[off:off + 16], self.before[off:off + 16])

    def test_only_named_bytes_change(self):
        n = built()["notes"]
        at, size = window()
        sites = [(o, ln) for o, ln, _ in n["bf_hud"]["regions"]] + [(at, size)] + \
            [(p, 4) for p in HOOK_OFFSETS + ABILITY_WORDS]
        changed = diff(self.before, self.rom)
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + ln for s, ln in sites)], [])
        for s, ln in sites:
            self.assertTrue(any(s <= i < s + ln for i in changed), hex(s))

    def test_no_outside_word_names_the_window(self):
        at, size = window()
        lo, hi = ROM_BASE + at, ROM_BASE + at + size
        refs = words_into(self.rom, lo, hi, skip=((at, at + size),))
        self.assertEqual(set(refs["abs"]), set(ABILITY_WORDS))
        self.assertEqual({p for p, _ in refs["rel"]}, set(HOOK_OFFSETS))
        self.assertIn(0x258BC, HOOK_OFFSETS)                   # the v2b word is one of them
        before = words_into(self.before, lo, hi)
        self.assertEqual((before["abs"], before["rel"]), ([], []))

    def test_boss_bar_data(self):
        bf = bf_rom()
        for i in range(60):
            j = i * 53 // 60
            self.assertEqual(self.rom[0x6D60F4 + 16 * i:0x6D6104 + 16 * i], bf[0x7198E4 + 16 * j:0x7198F4 + 16 * j])
        rm = live_remap()
        image = bytearray(rm(v) for v in bf[0x7196E4:0x7198E4])
        self.assertEqual(log2_bar(self.rom, 60), image)
        for f in (0, 1, 12, 30, 59):              # LoG II fill f blanks exactly Buu's Fury steps f x 53 / 60 to 52
            want = bytearray(image)
            for j in range(f * 53 // 60, 53):
                for k in range(4):
                    want[u32(bf, 0x087198E4 + 16 * j + 4 * k)] = 1
            self.assertEqual(log2_bar(self.rom, f), want, f)

    def test_new_pixels_avoid_reserved_and_live_indices(self):
        at, _ = window()
        used = set(self.rom[at:at + YELLOW_LEN]) | set(self.rom[0x6D64B4:0x6D66B4])
        self.assertEqual(used & ((SKIP_IDX - {0}) | LIVE_PAL_SKIP), set())

    def test_yellow_image_on_the_ep_row(self):
        at, _ = window()
        bf, rm = bf_rom(), live_remap()
        img = self.rom[at:at + YELLOW_LEN]
        for i in range(49):
            j = i * 41 // 49
            for k in range(3):
                o = u32(self.rom, EP_TABLE + 16 * i + 4 * k)
                self.assertEqual(img[o], rm(bf[0x713AD8 + u32(bf, 0x08071F40 + 16 * j + 4 * k)]), (i, k))
        self.assertTrue(all(v == 0 or v not in SKIP_IDX for v in img))

    def test_rebase_regions_held_r38_bytes(self):
        """The mockup 1 regions and the boss bar held the r38 bytes the mockup was built on, and now differ."""
        need(R38)
        r38 = R38.read_bytes()
        for off, n in MOCK1_REGIONS + BOSS:
            self.assertEqual(self.before[off:off + n], r38[off:off + n], hex(off))
            self.assertNotEqual(self.rom[off:off + n], r38[off:off + n], hex(off))


class PlacementTests(unittest.TestCase):
    def test_new_space_follows_r38_and_skips_a_named_chunk(self):
        b = built()
        n0 = len(b["alloc_before"].used())
        self.assertEqual(b["used"][:n0], b["alloc_before"].used())
        new = b["used"][n0:]
        at, size = window()
        self.assertEqual(new, [(SKIPPED, size), (at, size)])
        self.assertEqual(b["notes"]["bf_ki_pool"]["skipped"], [(SKIPPED, size, [NAMED_WORD[0]])])
        self.assertEqual(u32(b["before"], NAMED_WORD[0]), NAMED_WORD[1])
        self.assertEqual(u32(log2_build.BASE.read_bytes(), NAMED_WORD[0]), NAMED_WORD[1])   # vanilla data word
        self.assertTrue(SKIPPED <= NAMED_WORD[1] - ROM_BASE < SKIPPED + size)
        end = max(a + s for a, s in b["alloc_before"].used())
        self.assertEqual(SKIPPED, end)
        for a, s in new:
            self.assertEqual(set(b["before"][a:a + s]), {0xFF})
        self.assertEqual(set(b["rom"][SKIPPED:SKIPPED + size]), {0xFF})
        self.assertTrue(at + size <= log2_build.ART_REGION[0])


class FailClosedTests(unittest.TestCase):
    def fresh(self, after_hud: bool = False) -> tuple:
        b = built()
        if after_hud:
            return bytearray(b["hud"]), copy.deepcopy(b["alloc_hud"])
        return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])

    def assert_refused(self, patch, rom: bytearray, alloc) -> None:
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            patch.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_each_bf_hud_site_refuses(self):
        for off in (0x8E80, 0x8E8B, 0x1068C, 0x1067F, 0x6D7B54 + 5, 0x3B5358 + 0x100, 0x3B5658 + 0x30C,
                    0x3B5968 + 1, 0x3B5B90 + 0x4C, 0x3B5BE0 + 0x10, ABILITY_TABLE + 0x20, 0x6D60F4 + 3,
                    0x6D64B4 + 0x1FF, 0x6D7754 + 0x50, 0x705AA4 + 0x1FF, 0x88DE3C + 5, 0x88E03C + 0x100):
            with self.subTest(off=hex(off)):
                rom, alloc = self.fresh()
                rom[off] ^= 0x01
                self.assert_refused(bf_hud, rom, alloc)

    def test_each_bf_ki_pool_site_refuses(self):
        n = built()["alloc_before"].notes
        tb = n["ssj2_form"]["table"]
        for off in (n["fullpower_ssj"]["stretch_on"] + 7, 0x14FF4, tb + 20 * 5 + 0x10, tb + 20 * 22 + 0x10,
                    0x24008, *HOOK_OFFSETS, ABILITY_WORDS[0], ABILITY_WORDS[-1]):
            with self.subTest(off=hex(off)):
                rom, alloc = self.fresh(after_hud=True)
                rom[off] ^= 0x01
                self.assert_refused(bf_ki_pool, rom, alloc)

    def test_window_not_free_refuses(self):
        rom, alloc = self.fresh(after_hud=True)
        rom[window()[0] + 0x10] = 0
        self.assert_refused(bf_ki_pool, rom, alloc)

    def test_second_run_missing_notes_and_wrong_bf_refuse(self):
        rom, alloc = self.fresh()
        bf_hud.apply(rom, alloc)
        self.assert_refused(bf_hud, rom, alloc)
        bf_ki_pool.apply(rom, alloc)
        self.assert_refused(bf_ki_pool, rom, alloc)
        for patch, key, after in ((bf_hud, "chamber_spar", False), (bf_hud, "ssj2_form", False),
                                  (bf_ki_pool, "bf_hud", True), (bf_ki_pool, "fullpower_ssj", True),
                                  (bf_ki_pool, "scene_drain_pause", True)):
            with self.subTest(patch=patch.__name__, key=key):
                rom, alloc = self.fresh(after)
                del alloc.notes[key]
                self.assert_refused(patch, rom, alloc)
        with mock.patch.object(bf_hud, "BF_SHA1", "0" * 40):
            rom, alloc = self.fresh()
            self.assert_refused(bf_hud, rom, alloc)
            rom, alloc = self.fresh(after_hud=True)
            self.assert_refused(bf_ki_pool, rom, alloc)


# ===== the r39 files =====

R39_SAV, R39_SPAR, R39_COMPUTER = (BUILD / f"log2_poc_r39{s}" for s in (".sav", "_spar", "_computer"))
R38_SCOUTER_SAV, R38_SPAR_SAV, R38_COMPUTER_SAV = (BUILD / f"log2_poc_r38{s}.sav" for s in ("_scouter", "_spar",
                                                                                            "_computer"))


def scouter_bits(sav: bytes) -> list:
    ram = log2_save.read_ram(sav)
    return [ram[log2_save.slot_range(n).start + log2_save.O_FLAGS] >> 2 & 1 for n in range(log2_save.SLOT_COUNT)]


def slots_valid(sav: bytes) -> list:
    ram, out = log2_save.read_ram(sav), []
    for n in range(log2_save.SLOT_COUNT):
        s = log2_save.slot_range(n).start
        out.append(struct.unpack_from("<I", ram, s + log2_save.SLOT_DATA)[0] ==
                   log2_save.adler32(bytes(ram[s:s + log2_save.SLOT_DATA])))
    return out


class FileTests(unittest.TestCase):
    def test_r39_file_equals_the_build(self):
        need(R39)
        self.assertEqual(R39.read_bytes(), built()["rom"])

    def test_r38_to_r39_files_differ_at_the_named_sites_only(self):
        need(R38, R39)
        n = built()["notes"]
        at, size = window()
        sites = [(o, ln) for o, ln, _ in n["bf_hud"]["regions"]] + [(at, size)] + \
            [(p, 4) for p in HOOK_OFFSETS + ABILITY_WORDS]
        a, b = R38.read_bytes(), R39.read_bytes()
        self.assertEqual(len(a), len(b))
        changed = diff(a, b)                                   # bytewise: a run can span two adjacent sites
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + ln for s, ln in sites)], [])
        self.assertEqual(changed, diff(built()["before"], built()["rom"]))

    def test_rom_pairs_are_copies(self):
        need(R39, R39_SPAR.with_suffix(".gba"), R39_COMPUTER.with_suffix(".gba"))
        for p in (R39_SPAR, R39_COMPUTER):
            self.assertEqual(p.with_suffix(".gba").read_bytes(), R39.read_bytes(), p.name)

    def test_saves_have_the_scouter_on_in_every_slot(self):
        need(R39_SAV, R39_SPAR.with_suffix(".sav"), R39_COMPUTER.with_suffix(".sav"), R38_SCOUTER_SAV,
             R38_SPAR_SAV, R38_COMPUTER_SAV)
        self.assertEqual(R39_SAV.read_bytes(), R38_SCOUTER_SAV.read_bytes())
        self.assertEqual(R39_COMPUTER.with_suffix(".sav").read_bytes(), R38_COMPUTER_SAV.read_bytes())
        for p in (R39_SAV, R39_SPAR.with_suffix(".sav"), R39_COMPUTER.with_suffix(".sav")):
            sav = p.read_bytes()
            self.assertEqual((scouter_bits(sav), slots_valid(sav)), ([1, 1, 1], [True, True, True]), p.name)

    def test_spar_save_is_r38_spar_with_the_scouter_bit_and_new_checksums(self):
        need(R39_SPAR.with_suffix(".sav"), R38_SPAR_SAV)
        old = log2_save.read_ram(R38_SPAR_SAV.read_bytes())
        new = log2_save.read_ram(R39_SPAR.with_suffix(".sav").read_bytes())
        self.assertEqual(scouter_bits(R38_SPAR_SAV.read_bytes()), [0, 0, 0])
        allowed = set()
        for n in range(log2_save.SLOT_COUNT):
            s = log2_save.slot_range(n).start
            allowed |= {s + log2_save.O_FLAGS} | set(range(s + log2_save.SLOT_DATA, s + log2_save.SLOT_DATA + 4))
            self.assertEqual(new[s + log2_save.O_FLAGS], old[s + log2_save.O_FLAGS] | 0x04)
        self.assertEqual([hex(i) for i in diff(bytes(old), bytes(new)) if i not in allowed], [])


if __name__ == "__main__":
    unittest.main()
