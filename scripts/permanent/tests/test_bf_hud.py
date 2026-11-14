r"""
test_bf_hud.py - Tests for patches.bf_hud and patches.bf_ki_pool (r39): the HUD v2b mockup baked into the build.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_bf_hud.py -v
Builds build_list_dev.txt in memory: "before" = the list up to bf_hud (r38), "hud" = before + bf_hud,
"rom" = hud + bf_ki_pool (r39). Expected values are restated from the mockup builders
(scripts\one-time\2026-10-24-hud-ki\build_mock1.py, proto\build_proto_b.py) and the r38 bytes, not imported from the patches.
Equivalence: the approved v2b mockup has two halves. The HUD half still ships byte for byte, and EquivalenceTests
holds that guard. The ki pool half was superseded by the ORANGE Super Saiyan bar, which the owner approved later
(game-status.md, PRS-3), so the window grew and its code was rewritten. The class docstring carries the measurement.
The two mockups and the r38 and r39 files are frozen INPUTS. Their SHA-1s are pinned, and a test skips without them.
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
import log_paths
from rom import log2_save
from patches import bf_hud, bf_ki_pool

# ===== constants (mockup builders, r38 reads) =====
ROM_BASE, M32 = 0x08000000, 0xFFFFFFFF
BUILD = log_paths.MASTER_BUILDS
MOCKS = log_paths.HUD_KI_MOCKUPS
V2B, V2, MOCK1 = MOCKS / "log2_poc_r38_bfhud2b.gba", MOCKS / "log2_poc_r38_bfhud2.gba", MOCKS / "log2_poc_r36_bfhud.gba"
V2B_SHA1, V2_SHA1 = "f5f5ee730346695c25035871378efebc084165b1", "5f17f8fc9c31e7c60b44543c8868d02b18b8fd6c"
R38_SHA1 = "7a7cb85fa5873c4a44d360b33b6755d4e71e18e3"   # v2b's OWN base: a frozen input of every v2b row
R38_LAST = "chamber_spar"                              # the last module of the r38 list (build-lists r-tags)
R38, R39 = log_paths.build_file("log2_poc_r38.gba"), log_paths.build_file("log2_poc_r39.gba")
BF = log_paths.BF_ROM

MOCK_WINDOW, MOCK_SIZE, YELLOW_LEN = 0xE11000, 0x824, 0x500
V2B_FIX_STUB = 0xE1181C                                # the 8 byte state 46 stub v2b added inside its window
HUD_REGION_BYTES, V2B_HUD_BYTES = 17888, 13854         # the bf_hud regions, and the part of them v2b changed
RAM = 0x03003A00
PAL, BF_PAL = 0x1DA6C8, 0x5652C
SKIP_IDX, LIVE_PAL_SKIP = frozenset({0, 172, 174, 178, 218, 239}), frozenset({168})
EP_TABLE, ABILITY_TABLE = 0x083B5658, 0x1D9900
WRAP_ABILITIES = (0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 13)
# The r38 target of a hook that an earlier module already took sits in expansion and MOVES, so
# r38_target() re-reads those two from the notes that module wrote. Every other target is vanilla.
EXPANSION_TARGETS = {"ssj_tick": ("fullpower_ssj", "tick"), "ssj2_tick": ("scene_drain_pause", "tick_ssj2")}
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
    "asc_tick": (0x0802526C, 0x04, 0x080171E5, "tick_ssj"),   # the ascended grade, added with the red ki bar
    "xform_tick": (0x08025D9C, 0x04, 0x080155E5, "tick_xform"),   # the cooldown freeze, added with the Z meter
}
HOOK_OFFSETS = sorted(vt - ROM_BASE + slot for vt, slot, _, _ in HOOKS.values())
ABILITY_WORDS = sorted(ABILITY_TABLE + 16 * n + k for n in WRAP_ABILITIES for k in (8, 12))
# The ten hooks the v2b mockup itself installed, named. LATER_HOOKS came after it, so v2b never names them.
V2B_HOOKS = ("hud_draw", "ssj_tick", "ssj2_tick", "transform_end", "revert_end",
             "ki_blast", "beam48", "beam49", "ball51", "hold46")
LATER_HOOKS = ("asc_tick", "xform_tick")               # the ascended grade, then the Z meter
MOCK1_REGIONS = ((0x8E80, 4), (0x8E88, 4), (0x6D7B54, 0x300), (0x3B5358, 0x300), (0x3B5658, 0x310),
                 (0x3B5968, 0x228), (0x3B5B90, 0x50), (0x3B5BE0, 0x14))
BOSS = ((0x6D60F4, 0x3C0), (0x6D64B4, 0x200))
NAMED_WORD = (0x5851EC, 0x0890989C)                    # vanilla data word naming the first chunk the allocator gave
MAX_CHUNK_TRIES = 8                                    # the test's own ceiling on the candidate walk

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


def r38_target(name: str, typed: int) -> int:
    """The GBA address a hook's vtable word held before bf_ki_pool, derived where a module owns it."""
    key = EXPANSION_TARGETS.get(name)
    if not key:
        return typed
    return (built()["alloc_before"].notes[key[0]][key[1]] + ROM_BASE) | 1


def labels() -> dict:
    return built()["notes"]["bf_ki_pool"]["labels"]


def window() -> tuple:
    """(file offset, size) of the r39 pool window."""
    n = built()["notes"]["bf_ki_pool"]
    return n["window"], n["size"]


def r38_file() -> bytes:
    """The frozen r38 file, which is v2b's OWN base. Cached, because three rows read it."""
    if "r38" not in _CACHE:
        _CACHE["r38"] = R38.read_bytes()
    return _CACHE["r38"]


def hook_word(name: str) -> int:
    """File offset of the vtable word a hook takes."""
    vt, slot, _, _ = HOOKS[name]
    return vt - ROM_BASE + slot


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


def site_problems(a: bytes, b: bytes, sites: list) -> list:
    """What breaks "a to b changes exactly these sites": stray bytes first, then sites that never changed."""
    changed = diff(a, b)
    return ([hex(i) for i in changed if not any(s <= i < s + n for s, n in sites)]
            + [hex(s) for s, n in sites if not any(s <= i < s + n for i in changed)])


def hud_sites() -> list:
    return [(o, ln) for o, ln, _ in built()["notes"]["bf_hud"]["regions"]]


def pool_sites() -> list:
    at, size = window()
    return [(at, size)] + [(p, 4) for p in HOOK_OFFSETS + ABILITY_WORDS]


def v2b_sites() -> list:
    """Every site the v2b mockup changed in its own base: the bf_hud regions (the HUD half), its own
    window and the words naming inside it (the ki pool half)."""
    return (hud_sites() + [(MOCK_WINDOW, MOCK_SIZE)] + [(hook_word(n), 4) for n in V2B_HOOKS]
            + [(p, 4) for p in ABILITY_WORDS])


def hud_half_problems(rom: bytes, v2b: bytes) -> list:
    """bf_hud regions where `rom` no longer carries the mockup's bytes.

    It compares WHOLE regions, so it also reads the 4034 bytes v2b shares with its own base. A check
    anchored on a diff of the two cannot see those.
    """
    return [hex(o) for o, ln in hud_sites() if rom[o:o + ln] != v2b[o:o + ln]]


def need(*paths: Path) -> None:
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise unittest.SkipTest(f"missing {missing}")


# ===== tests =====

class BaseTests(unittest.TestCase):
    def test_before_is_r38(self):
        """The r38 ROM cannot be rebuilt, so check the MODULES: `before` is the r38 set and no more.

        A later module that changes size moves every allocation after it, so the r38 SHA-1 can never
        hold again. The module list and the notes the build recorded both still hold.
        """
        names = built()["names"]
        before_names = names[:names.index("bf_hud")]
        self.assertEqual(before_names[-1], R38_LAST)
        self.assertNotIn("bf_hud", before_names)
        self.assertEqual(sorted(built()["alloc_before"].notes), sorted(before_names))

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
    """What the approved v2b mockup still proves about the build. Measured 2026-11-13.

    v2b has two halves. The HUD half is the 132 bf_hud regions, 17888 bytes, and the build carries
    every one of them byte for byte. That guard is why this class exists. The ki pool half moved
    on, because the owner later approved the ORANGE Super Saiyan bar (game-status.md, PRS-3). The
    window is now 0x10B4 bytes against the mockup's 0x824, the code blob is 0x3AC bytes against
    v2b's 0x324 and shares 76 of them, and the words naming inside the window carry six different
    deltas, because the orange image sits between the yellow one and the code. The yellow image
    itself still matches byte for byte, and one row holds that.
    Against its OWN base, the frozen r38 file, v2b changed 16031 bytes: 13854 in the bf_hud
    regions, 2073 in the window, 38 in ten hooked vtable words and 66 in 22 ability words. Eight
    further pointer bytes hold the same value in the build by coincidence, and every one of them is
    the top byte of a hook word. A split that counts bytes rather than regions therefore reads
    13862 matching bytes, and that number is wrong.
    """

    @classmethod
    def setUpClass(cls):
        need(V2B, V2)
        cls.rom = built()["rom"]
        cls.v2b, cls.v2 = V2B.read_bytes(), V2.read_bytes()
        cls.at = window()[0]

    def test_mockup_files(self):
        """The two mockups are hand made inputs that nobody regenerates, so their SHA-1s are pinned.

        MOCK_SIZE is pinned from both sides here, against the mockup alone: v2b's window page holds
        content up to MOCK_SIZE and 0xFF filler after it.
        """
        self.assertEqual(hashlib.sha1(self.v2b).hexdigest(), V2B_SHA1)
        self.assertEqual(hashlib.sha1(self.v2).hexdigest(), V2_SHA1)
        self.assertNotEqual(self.v2b[MOCK_WINDOW + MOCK_SIZE - 1], 0xFF)
        self.assertEqual(set(self.v2b[MOCK_WINDOW + MOCK_SIZE:MOCK_WINDOW + 0x1000]), {0xFF})

    def test_the_hud_half_of_v2b_still_ships(self):
        """Every byte of the HUD half of the approved mockup still ships, byte for byte.

        This is the part of the old whole ROM compare that is still true, and it is the guard that
        survives the orange Super Saiyan bar. The HUD half is the 132 bf_hud regions, 17888 bytes.
        The compare reads WHOLE regions, so it also reads the 4034 bytes v2b shares with its own
        base, which a diff of the two cannot see. It needs the mockup alone.
        """
        self.assertEqual(hud_half_problems(self.rom, self.v2b), [])
        self.assertEqual(len({i for o, ln in hud_sites() for i in range(o, o + ln)}), HUD_REGION_BYTES)
        self.assertEqual(set(self.rom[MOCK_WINDOW:MOCK_WINDOW + 0x1000]), {0xFF})

    def test_the_yellow_bar_image_still_ships(self):
        """The one part of the ki pool half the orange bar left byte for byte: the yellow bar image.

        It sits first in both windows, so each copy starts at its own window base. The code behind
        it was rewritten to pick a colour, and no row compares that.
        """
        self.assertEqual(self.rom[self.at:self.at + YELLOW_LEN],
                         self.v2b[MOCK_WINDOW:MOCK_WINDOW + YELLOW_LEN])

    def test_v2b_changes_its_own_base_at_named_sites_only(self):
        """v2b against ITS OWN base, the frozen r38 file: the claim 2 form, which no build stales.

        v2b changes the bf_hud regions, its own window and exactly 32 named words: the ten vtable
        words it hooked, and all 22 ability words. A NEW difference is a stray and fails here.
        The site list comes from the bf_hud notes. 130 of the 132 regions sit at vanilla offsets.
        The other two move with the ssj2_form allocation, as the ssj2_tick entry of HOOKS does.
        This row also pins the r38 file, which is the input the 13854 count measures against.
        """
        need(R38)
        r38 = r38_file()
        self.assertEqual(hashlib.sha1(r38).hexdigest(), R38_SHA1)
        sites = v2b_sites()
        self.assertEqual(len(sites), len(hud_sites()) + 1 + len(V2B_HOOKS) + len(ABILITY_WORDS))
        self.assertEqual(site_problems(r38, self.v2b, sites), [])
        regions = {i for o, ln in hud_sites() for i in range(o, o + ln)}
        self.assertEqual(len([x for x in diff(r38, self.v2b) if x in regions]), V2B_HUD_BYTES)
        for name in LATER_HOOKS:                    # these two post-date v2b, so v2b never names them
            self.assertNotIn((hook_word(name), 4), sites)

    def test_v2_to_v2b_is_the_state_46_word_and_stub(self):
        """The v2b fix, measured from the two pinned mockups alone (proto test_v2_to_v2b).

        v2 left the state 46 hold hook at its vanilla handler. v2b points it at a new 8 byte stub
        inside the mockup window.
        """
        vt, _, vanilla, _ = HOOKS["hold46"]
        word = hook_word("hold46")
        self.assertEqual([(a, b - a) for a, b in runs_of(self.v2, self.v2b)],
                         [(word, 4), (V2B_FIX_STUB, 8)])
        self.assertEqual((vt + u32(self.v2, word)) & M32, vanilla)
        self.assertEqual((vt + u32(self.v2b, word)) & M32, (ROM_BASE + V2B_FIX_STUB) | 1)

    def test_the_build_carries_the_state_46_fix(self):
        """The same fix in the build, which bf_ki_pool records as its "fix" note.

        The hold46 vtable word names the st46 stub. The stub loads the vanilla state 46 handler
        address and branches to swap_state. v2b's own stub holds the same vanilla literal.
        """
        from rom.thumb_dis import listing
        vt, _, vanilla, _ = HOOKS["hold46"]
        lb, fix = labels(), built()["notes"]["bf_ki_pool"]["fix"]
        self.assertEqual(fix, lb["st46"] - ROM_BASE)
        self.assertEqual((vt + u32(self.rom, hook_word("hold46"))) & M32, lb["st46"] | 1)
        self.assertEqual([t for _, t in listing(self.rom, lb["st46"], 2)],
                         [f"ldr r3,={vanilla:#010x}", f"b {lb['swap_state']:#x}"])
        self.assertEqual(u32(self.rom, fix + 4), vanilla)
        self.assertEqual(u32(self.v2b, V2B_FIX_STUB + 4), vanilla)

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
            self.assertEqual((vt + u32(self.before, vt + slot)) & M32, r38_target(name, target), name)
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
        self.assertEqual(site_problems(self.before, self.rom, hud_sites() + pool_sites()), [])

    def test_the_hud_and_the_pool_write_disjoint_named_sites(self):
        """r38 to r39 in its two real steps, both built in memory.

        bf_hud writes its own regions and nothing else. bf_ki_pool then writes the window, the hooked
        vtable words and the ability words, and no byte of a bf_hud region. The whole-step check above
        cannot see that split, because it reads the two site lists together.
        """
        hud = built()["hud"]
        self.assertEqual(site_problems(self.before, hud, hud_sites()), [])
        self.assertEqual(site_problems(hud, self.rom, pool_sites()), [])

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
    def test_new_space_follows_r38_and_skips_every_chunk_a_word_names(self):
        """The new space is stated as a RULE, because every address here is a build result.

        The allocator bumps, so the candidates run from the end of the r38 allocations in steps of
        the window size. bf_ki_pool refuses a candidate exactly when a ROM word names a byte inside
        it, and takes the first one no word names. words_into is the test's own second shape for
        that scan, so a disagreement with the patch's own list shows up here.
        """
        b = built()
        n0 = len(b["alloc_before"].used())
        self.assertEqual(b["used"][:n0], b["alloc_before"].used())
        new, at, size = b["used"][n0:], *window()
        end = -(-max(a + s for a, s in b["alloc_before"].used()) // 4) * 4
        want, namers = [], []
        for k in range(MAX_CHUNK_TRIES):
            chunk = end + k * size
            self.assertEqual(set(b["hud"][chunk:chunk + size]), {0xFF}, hex(chunk))
            found = words_into(b["hud"], ROM_BASE + chunk, ROM_BASE + chunk + size)
            want.append((chunk, size))
            if not (found["abs"] or found["rel"]):
                break
            namers.append((chunk, size, found["abs"] + [q for q, _ in found["rel"]]))
        else:
            self.fail(f"no unnamed chunk in {MAX_CHUNK_TRIES} tries")
        self.assertEqual(new, want)
        self.assertEqual(at, want[-1][0])
        self.assertEqual(b["notes"]["bf_ki_pool"]["skipped"], namers)
        for a, s, _ in namers:
            self.assertEqual(set(b["rom"][a:a + s]), {0xFF})                # a refused chunk stays unused
        self.assertTrue(at + size <= log2_build.ART_REGION[0])
        if namers:                                      # today: one refusal, by a vanilla data word
            self.assertEqual(namers, [(end, size, [NAMED_WORD[0]])])
            self.assertEqual(u32(b["hud"], NAMED_WORD[0]), NAMED_WORD[1])
            self.assertEqual(u32(log2_build.BASE.read_bytes(), NAMED_WORD[0]), NAMED_WORD[1])
            self.assertTrue(end <= NAMED_WORD[1] - ROM_BASE < end + size)


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

R39_SHA1 = "aa51dc16da5f6b633c0f50dc566864fe43f89ff0"   # the ROM he played: a record, never a build target
R39_SAV, R39_SPAR, R39_COMPUTER = (log_paths.build_file(f"log2_poc_r39{s}")
                                   for s in (".sav", "_spar", "_computer"))
R38_SCOUTER_SAV, R38_SPAR_SAV, R38_COMPUTER_SAV = (log_paths.build_file(f"log2_poc_r38{s}.sav")
                                                   for s in ("_scouter", "_spar", "_computer"))


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
    def test_r39_file_is_the_pinned_record(self):
        """The r39 file is a frozen INPUT pin, and this row is not a build check.

        It is the ROM the owner played. Later modules changed size, so every allocation after them
        moved and no build reproduces it. Its SHA-1 is pinned the way test_mockup_files pins the two
        mockups. What the mockup still proves about the build lives in EquivalenceTests.
        """
        need(R39)
        self.assertEqual(hashlib.sha1(R39.read_bytes()).hexdigest(), R39_SHA1)

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


class ControlTests(unittest.TestCase):
    """site_problems and hud_half_problems read their site lists from the notes the two patches wrote,
    and the skip rule reads its chunk addresses from the allocator. All three must be shown to go red.
    Every case works on a copy in memory: no ROM file, save or state is written."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.hud, cls.rom = b["before"], b["hud"], b["rom"]

    def test_the_two_steps_report_nothing(self):
        self.assertEqual(site_problems(self.before, self.hud, hud_sites()), [])
        self.assertEqual(site_problems(self.hud, self.rom, pool_sites()), [])

    def test_a_pool_step_byte_inside_a_hud_region_is_reported(self):
        at = hud_sites()[0][0]
        rom = bytearray(self.rom)
        rom[at] ^= 0x01
        self.assertEqual(site_problems(self.hud, bytes(rom), pool_sites()), [hex(at)])

    def test_a_hud_region_left_at_the_r38_bytes_is_reported(self):
        at, ln = hud_sites()[0]
        hud = bytearray(self.hud)
        hud[at:at + ln] = self.before[at:at + ln]
        self.assertEqual(site_problems(self.before, bytes(hud), hud_sites()), [hex(at)])

    def test_a_hud_region_byte_that_leaves_v2b_is_reported(self):
        """The HUD half guard must be shown to have teeth, or the build can decay into agreeing with
        itself. The byte perturbed here is one v2b SHARES with its own base, which proves the whole
        region compare sees more than a diff of the two does."""
        need(R38, V2B)
        v2b, at = V2B.read_bytes(), hud_sites()[0][0]
        self.assertEqual(r38_file()[at], v2b[at])
        self.assertEqual(hud_half_problems(self.rom, v2b), [])
        rom = bytearray(self.rom)
        rom[at] ^= 0x01
        self.assertEqual(hud_half_problems(bytes(rom), v2b), [hex(at)])

    def test_a_word_naming_the_taken_window_is_found(self):
        """The skip rule says no word names the chunk the allocator took. Plant one and read it back."""
        at, size = window()
        before = bytearray(self.before)
        struct.pack_into("<I", before, NAMED_WORD[0], at + ROM_BASE)
        found = words_into(bytes(before), ROM_BASE + at, ROM_BASE + at + size)
        self.assertEqual(found["abs"], [NAMED_WORD[0]])

    def test_without_the_namer_the_pool_takes_the_first_chunk(self):
        """The skip is a rule, not an address. Clear the one word that names the first chunk and the
        patch takes it, which moves the window a whole chunk down."""
        b = built()
        rom, alloc = bytearray(b["hud"]), copy.deepcopy(b["alloc_hud"])
        struct.pack_into("<I", rom, NAMED_WORD[0], 0)
        bf_ki_pool.apply(rom, alloc)
        end = -(-max(a + s for a, s in b["alloc_before"].used()) // 4) * 4
        self.assertEqual(alloc.notes["bf_ki_pool"]["skipped"], [])
        self.assertEqual(alloc.notes["bf_ki_pool"]["window"], end)
        self.assertEqual(window()[0], end + alloc.notes["bf_ki_pool"]["size"])


if __name__ == "__main__":
    unittest.main()
