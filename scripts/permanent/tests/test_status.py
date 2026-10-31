r"""
test_status.py - Tests for the status page gold bonus patch (patches.status_bonus), slice 2.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds scratch\test-roms\status.gba once (gohan_gi, ssj2_form, gohan_portraits, status_bonus; log:
scratch\test-roms\build-log-test.md) and the same patches in memory, so the tests see the ROM before and
after status_bonus.
Source:  docs\research\research-status-screen.md sections 1, 2.3 and 5. Readers take every address from the ROM: the
entry stub @0x0800379C names the page copy, each BL in the copy names a stub, each stub names its target.
PageCpu runs the vanilla page (ROM before the patch) and the patched page (through the entry stub) with every
base call stubbed and traced, so the width, gold and text tests check behavior, not code text.
"""
import copy
import struct
import unittest
from pathlib import Path
from unittest import mock

import log2_build
import log_paths
from rom.rom_space import Allocator
from tests.test_ssj2 import M32, REGNO, Cpu
from rom.thumb_dis import dis, listing
from rom.webfoot_decompress import ROM_BASE, unpack_frame

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
BASE_ROM = BASE.read_bytes()
OUT = log_paths.TEST_ROMS / "status.gba"

PAGE, PAGE_END, CODE_END = 0x0800379C, 0x08003B44, 0x08003AFE  # RSS 1: code to 0x08003AFD, pool to 0x08003B43
SPLICE = (0x08003902, 0x08003A1C)          # vanilla stat rows: STR, POW, END label, number and bar
ENTRY_STUB, PLAYER_STUB = 0x0800379C, 0x080037AC
ITEM_SITES = (0x0800F4AA, 0x0800F512, 0x0800F57A)   # RSS 2.2: `ldr r0,=0x03001fa8` before `bl 0x80086a2`
ITEM_HANDLERS = ((0x0800F45A, 2, 0xA), (0x0800F4C2, 5, 0xC), (0x0800F52A, 8, 0xE))   # (handler, +1 item, field)
STUB_TEXT = ["push {r7}", "ldr r7,=", "mov r12,r7", "pop {r7}", "bx r12"]
TEXT, PRINTF, BLIT, QUERY, REAPPLY = 0x0801F636, 0x0801F6D8, 0x08021188, 0x08006E0A, 0x080086A2
ITEM_TEXT = 0x0801FC9C
ONE_ARG = {0x0801F110, 0x08004230, 0x08004214, 0x0801F08C, 0x0800BDCC}
PAGE_TARGETS = {0x08020E5C, 0x0801F394, 0x08004214, 0x08021F18, 0x0801F6D8, 0x0801F636, 0x08021F30, 0x0802130A,
                0x0801F08C, 0x08021188, 0x0801F110, 0x08004230, 0x0800BDCC, 0x080211C8, 0x0801F508, 0x080236B4,
                0x08020EAA}                # RSS 2.3: "about 15 others" plus the blit and the query
STRUCT, PLAYER_PTR, LIST_PTR = 0x03000E90, 0x03001FA8, 0x03001D18
THIS, PLAYER, LIST, BAR_BUF, EXIT = 0x02001000, 0x02002000, 0x02003000, 0x02030000, 0x08003B62
MENU_PAL, OBJ_PAL = 0x1D4F50, 0x1DA6C8
BAR_FRAME, FONT = 0x6F869C, 0x08028724      # bar image (75x8); menu font (page pool 0x08003B04)
GOLD_INDICES = {58, 69, 34}                # the report's contrast choice, menu palette rom:0x1D4F50


def spec_px(value: int) -> int:
    """Final decisions 2 (brief): w = min(v, 125) / 5 * 3, integer."""
    return min(value, 125) // 5 * 3


def vanilla_px(value: int) -> int:
    return 75 if value > 100 else (value >> 2) * 3


# ===== build (once) =====

_CACHE = {}


def built() -> dict:
    """{"before": ROM after gohan_portraits, "rom": after status_bonus, "alloc": allocator before, "notes", "file"}."""
    if _CACHE:
        return _CACHE
    from patches import gohan_gi, gohan_portraits, ssj2_form, status_bonus
    from tests.test_build import TEST_LOG, build
    rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
    alloc = Allocator(len(rom), log2_build.EXPANSION)
    for patch in (gohan_gi, ssj2_form, gohan_portraits):
        patch.apply(rom, alloc)
    before, alloc_before = bytes(rom), copy.deepcopy(alloc)
    status_bonus.apply(rom, alloc)
    with mock.patch.object(log2_build, "BUILD_LOG", TEST_LOG):
        build(BASE, OUT, ["gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus"])
    _CACHE.update(before=before, alloc=alloc_before, rom=bytes(rom), notes=alloc.notes, file=OUT.read_bytes())
    return _CACHE


def rebuild(**patches) -> bytes:
    """status_bonus applied to the cached before-ROM with module constants patched."""
    from patches import status_bonus
    b = built()
    rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc"])
    with mock.patch.multiple(status_bonus, **patches):
        status_bonus.apply(rom, alloc)
    return bytes(rom)


def u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE)[0]


# ===== readers (from the ROM) =====

def stub_target(rom: bytes, a: int) -> int:
    texts = [t for _, t in listing(rom, a, 5)]
    if [t.split("=")[0] + ("=" if "=" in t else "") for t in texts] != STUB_TEXT:
        raise AssertionError(f"{a:#x} is not a long-call stub: {texts}")
    return int(texts[1].split("=")[1], 16)


def page_of(rom: bytes) -> int:
    return stub_target(rom, ENTRY_STUB) & ~1


def code_bls(rom: bytes, start: int, end: int) -> list:
    """[(address, target)] of the BLs in [start, end), decoded in instruction order."""
    out, a = [], start
    while a < end:
        text, size = dis(rom, a)
        if text.startswith("bl "):
            out.append((a, int(text[3:], 16)))
        a += size
    return out


def splice_texts(rom: bytes) -> list:
    page = page_of(rom)
    return [t for _, t in listing(rom, page + SPLICE[0] - PAGE, 7)]


def stats_of(rom: bytes) -> int:
    return int(splice_texts(rom)[3][3:], 16)


def rebased(text: str, delta: int) -> str:
    """A relative branch in the copy, written with the target the vanilla page would branch to."""
    op, _, arg = text.partition(" ")
    if op[0] == "b" and op not in ("bl", "bx") and arg.startswith("0x"):
        return f"{op} {int(arg, 16) - delta:#x}"
    return text


def cstr(cpu: Cpu, a: int) -> bytes:
    out = bytearray()
    while (c := cpu.load(a + len(out), 1)):
        out.append(c)
    return bytes(out)


def font_width(rom: bytes, s: str) -> int:
    """Width 0x0801F636 measures: sum of glyph width + 1 (font table at FONT, column glyphs)."""
    h = lambda o: struct.unpack_from("<H", rom, FONT - ROM_BASE + 2 * o)[0]   # noqa: E731
    return sum(h(h(ord(c))) + 1 for c in s)


# ===== interpreter (the ssj2 Cpu plus the ops the page uses) =====

class PageCpu(Cpu):
    def _cond(self, cc: str) -> bool:
        if cc in ("hi", "ls"):
            hi = self.c and not self.z
            return hi if cc == "hi" else not hi
        return super()._cond(cc)

    def _step(self, nxt: int, text: str) -> int:
        r = self.r
        op, _, rest = text.partition(" ")
        a = rest.split(",")
        if op == "mul":
            r[REGNO[a[0]]] = self._nz(r[REGNO[a[0]]] * r[REGNO[a[1]]])
        elif op == "asr":
            x, k = r[REGNO[a[1]]], int(a[2][1:], 0)
            r[REGNO[a[0]]] = self._nz((x - (1 << 32) if x >> 31 else x) >> k)
        elif op == "add" and len(a) == 3 and a[1] == "pc":            # format 12: no flags
            r[REGNO[a[0]]] = ((nxt - 2 + 4) & ~3) + int(a[2][1:], 0)
        elif op == "add" and len(a) == 3 and a[1] == "sp":
            r[REGNO[a[0]]] = (r[13] + int(a[2][1:], 0)) & M32
        elif op in ("add", "sub") and a[0] == "sp":                    # format 13: no flags
            r[13] = (r[13] + (1 if op == "add" else -1) * int(a[1][1:], 0)) & M32
        else:
            return super()._step(nxt, text)
        return nxt


def page_state(rom: bytes, stats: tuple, live: tuple = None, where: str = "menu", leader: bool = True) -> PageCpu:
    """Leader Gohan (char 0) with base STR/POW/END stats; live values on a player that is reachable through the
    pointer ("field"), the suspended list ("menu"), or neither ("none")."""
    cpu = PageCpu(rom)
    rec = bytearray(28)
    struct.pack_into("<hhhhBB", rec, 0, 85, 100, 20, 30, 2, 0)
    struct.pack_into("<HHHI", rec, 0xA, stats[0] << 8, stats[1] << 8, stats[2] << 8, 1234)
    cpu.store(STRUCT, 1, 0 if leader else 1)
    for i, b in enumerate(rec):
        cpu.store(STRUCT + 0xC + i, 1, b)
    cpu.store(THIS + 0x158, 4, 0)                 # page 0 shows char 0
    for i, v in enumerate(live or stats):
        cpu.store(PLAYER + 0x160 + i, 1, v)
    cpu.store(PLAYER_PTR, 4, PLAYER if where == "field" else 0)
    cpu.store(LIST_PTR, 4, LIST if where == "menu" else 0)
    cpu.r[0], cpu.r[1], cpu.r[13], cpu.r[14] = THIS, 0, 0x03007E00, EXIT | 1
    return cpu


def run_page(rom: bytes, cpu: PageCpu) -> list:
    """Run the page from 0x0800379C to its return; every base call is stubbed and traced."""
    trace = []

    def call(t):
        def handler(c):
            r = c.r
            if t == TEXT:
                trace.append(("text", r[0], cstr(c, r[1]), c.load(r[0] + 4, 4), c.load(r[0] + 8, 4)))
            elif t == PRINTF:
                fmt = cstr(c, r[1])
                trace.append(("printf", r[0], fmt % tuple(r[2:2 + fmt.count(b"%d")]),
                              c.load(r[0] + 4, 4), c.load(r[0] + 8, 4)))
            elif t == BLIT:
                trace.append(("blit", r[0], r[1], tuple(c.load(r[2] + 4 * i, 4) for i in range(4)), r[3]))
            elif t == QUERY:
                trace.append(("query", r[0], r[1], r[2]))
                return PLAYER if (r[0], r[1], r[2]) == (LIST, 7, 0) else 0
            else:
                trace.append((t, r[0]) if t in ONE_ARG else (t, r[0], r[1], r[2]))
            return {0x0801F08C: BAR_BUF, 0x08004214: 12, 0x08021F30: 60, 0x08004230: 99}.get(t, 0)
        return handler

    stops = {t: call(t) for t in PAGE_TARGETS | {QUERY}}
    stops[EXIT] = "exit"
    sp, saved = cpu.r[13], cpu.r[4:8]
    if cpu.run(PAGE, stops, limit=5000) != "exit":
        raise AssertionError("page did not return")
    if cpu.r[13] != sp or cpu.r[4:8] != saved:
        raise AssertionError("page did not restore sp and r4-r7")
    return trace


def stat_rows(trace: list) -> list:
    """Per stat row: (number text, [(src, x0, x1)] blits)."""
    rows, i = [], 0
    prints = [e for e in trace if e[0] == "printf" and e[3] == 0x88 and e[4] in (55, 71, 87)]
    for n in prints:
        i = trace.index(n, i)
        blits, j = [], i + 1
        while j < len(trace) and trace[j][0] == "blit":
            blits.append((trace[j][2], trace[j][3][0], trace[j][3][2]))
            j += 1
        rows.append((n[2].decode(), blits))
    return rows


# ===== tests =====

class StatusBonusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]["status_bonus"]
        cls.page = page_of(cls.rom)
        cls.gold = u32(cls.rom, stats_gold_literal(cls.rom)) + 0x3E

    # base ROM

    def test_entry_veneer_bytes(self):
        for site, target in ((ENTRY_STUB, self.page | 1), (PLAYER_STUB, self.notes["find_player"] + ROM_BASE | 1)):
            off = site - ROM_BASE
            self.assertEqual(self.rom[off:off + 12].hex(), "80b4024fbc4680bc60470000", hex(site))
            self.assertEqual(u32(self.rom, site + 12), target, hex(site))
            self.assertEqual(stub_target(self.rom, site), target)
        self.assertEqual(self.page % 4, 0)                    # pool alignment kept: ldr = and add pc stay valid
        self.assertGreaterEqual(self.page, ROM_BASE + log2_build.BASE_SIZE)

    def test_base_8mb_differs_only_at_veneer_and_item_sites(self):
        sites = {ENTRY_STUB: 32, **{s: 4 for s in ITEM_SITES}}
        inside = {a - ROM_BASE for s, n in sites.items() for a in range(s, s + n)}
        diff = {i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]}
        self.assertFalse(sorted(hex(i) for i in diff - inside))
        for s in sites:
            self.assertTrue(diff & set(range(s - ROM_BASE, s - ROM_BASE + 4)), hex(s))

    def test_only_one_caller_enters_the_veneer_site(self):
        # every halfword is tried as a BL prefix, so a misaligned decode cannot hide a caller
        def callers(rom):
            out = []
            for a in range(ROM_BASE, 0x08030000, 2):
                hi, lo = struct.unpack_from("<HH", rom, a - ROM_BASE)
                if hi >> 11 == 0x1E and lo >> 11 == 0x1F:
                    t = a + 4 + ((hi & 0x7FF) << 12 | (lo & 0x7FF) << 1) - ((hi & 0x400) << 13)
                    if ENTRY_STUB <= t < ENTRY_STUB + 32:
                        out.append(a)
            return out
        self.assertEqual(callers(self.before), [0x08003B5E])  # RSS 1: page dispatcher, page 0
        self.assertEqual(callers(self.rom), [0x08003B5E, *ITEM_SITES])
        words = {u32(self.before, ROM_BASE + i) for i in range(0, log2_build.BASE_SIZE, 4)}
        self.assertFalse({w for w in words if ENTRY_STUB <= w & ~1 < ENTRY_STUB + 32})

    def test_item_sites_call_find_player_stub(self):
        for site in ITEM_SITES:
            texts = [t for _, t in listing(self.rom, site, 4)]
            self.assertEqual(texts[0], f"bl {PLAYER_STUB:#x}")
            self.assertEqual(texts[1:3], ["cmp r0,#0x0", f"beq {site + 0xC:#x}"])
            self.assertEqual(texts[3], f"bl {REAPPLY:#x}")
            self.assertEqual([t for _, t in listing(self.before, site, 2)], ["ldr r0,=0x03001fa8", "ldr r0,[r0,#0x0]"])

    def test_palette_unchanged(self):
        for off in (MENU_PAL, OBJ_PAL):
            self.assertEqual(self.rom[off:off + 512], BASE_ROM[off:off + 512])
        new_code = range(self.notes["code"], self.notes["code"] + 0x200, 4)
        pool = {struct.unpack_from("<I", self.rom, o)[0] for o in new_code}
        self.assertFalse({w for w in pool if 0x05000000 <= w < 0x07000000})   # no palette or VRAM address

    # relocated page

    def test_relocated_page_integrity(self):
        old_bls = dict(code_bls(self.before, PAGE, CODE_END))
        a, seen = PAGE, set()
        while a < CODE_END:
            text, size = dis(self.before, a)
            new = self.page + a - PAGE
            if SPLICE[0] <= a < SPLICE[1]:
                a += size
                continue
            if a in old_bls:
                target = int(dis(self.rom, new)[0][3:], 16)
                self.assertEqual(stub_target(self.rom, target) & ~1, old_bls[a], hex(a))
                seen.add(old_bls[a])
            else:
                self.assertEqual(self.rom[new - ROM_BASE:new - ROM_BASE + size],
                                 self.before[a - ROM_BASE:a - ROM_BASE + size], hex(a))
                self.assertEqual(rebased(dis(self.rom, new)[0], self.page - PAGE), text, hex(a))   # literals agree
            a += size
        self.assertEqual(seen, PAGE_TARGETS - {BLIT})        # the blit is called only in the stat rows
        new_pool = self.page - ROM_BASE + CODE_END - PAGE
        self.assertEqual(self.rom[new_pool:new_pool + PAGE_END - CODE_END],
                         self.before[CODE_END - ROM_BASE:PAGE_END - ROM_BASE])   # strings, literals, +3 table word
        self.assertEqual(u32(self.rom, self.page + 0x394), u32(self.before, 0x08003B30))
        self.assertEqual(self.notes["plus3_literal"], self.page - ROM_BASE + 0x394)

    def test_old_page_bls_counted(self):
        bls = code_bls(self.before, PAGE, CODE_END)
        self.assertEqual(len(bls), 42)
        self.assertEqual({t for _, t in bls}, PAGE_TARGETS)

    def test_every_new_bl_lands_on_new_code_or_a_stub(self):
        page, code = self.page, stub_target(self.rom, PLAYER_STUB) & ~1
        end = next(a for a, t in listing(self.rom, stats_of(self.rom), 200) if t == "pop {r4,r5,r6,r7,pc}")
        in_page, in_code = code_bls(self.rom, page, page + CODE_END - PAGE), code_bls(self.rom, code, end)
        self.assertEqual((len(in_page), len(in_code)), (42 - 9 + 1, 8))   # stat rows: 9 BLs became `bl stats`
        new = in_page + in_code
        stubs = {a + ROM_BASE for a in self.notes["stubs"].values()}
        for at, t in new:
            if t in stubs:
                self.assertIn(stub_target(self.rom, t) & ~1, PAGE_TARGETS | {QUERY}, hex(at))
            else:
                self.assertGreaterEqual(t, ROM_BASE + log2_build.BASE_SIZE, hex(at))

    def test_stubs_keep_registers(self):
        for target, at in self.notes["stubs"].items():
            cpu = PageCpu(self.rom)
            cpu.r[:8] = [0x11111111 * (i + 1) & M32 for i in range(8)]
            cpu.r[13], cpu.r[14] = 0x03007E00, EXIT | 1
            seen = {}
            cpu.run(at + ROM_BASE, {target: lambda c: seen.update(r=list(c.r)) or c.r[0], EXIT: "exit"})
            self.assertEqual(seen["r"][:8], [0x11111111 * (i + 1) & M32 for i in range(8)], hex(target))
            self.assertEqual(seen["r"][13:15], [0x03007E00, EXIT | 1], hex(target))

    def test_splice(self):
        texts = splice_texts(self.rom)
        self.assertEqual(texts[:3], ["ldr r0,[sp,#0xd8]", "ldr r1,[r0,#0x0]", "add r0,sp,#0x9c"])
        self.assertEqual(texts[4:6], ["mov r6,#0x57", "add r7,sp,#0x9c"])
        self.assertEqual(texts[6], f"b {self.page + SPLICE[1] - PAGE:#x}")
        rest = self.page - ROM_BASE + SPLICE[0] - PAGE + 16
        self.assertEqual(set(self.rom[rest:self.page - ROM_BASE + SPLICE[1] - PAGE]), {0})
        old = [t for _, t in listing(self.before, SPLICE[1], 6)]   # the page reads r4-r7 after the rows
        self.assertEqual(old[:2], ["add r0,r5,#0", "bl 0x801f110"])

    def test_no_branch_enters_the_splice(self):
        a = PAGE
        while a < CODE_END:
            text, size = dis(self.before, a)
            if text.split(" ")[0] in ("b", "beq", "bne", "bgt", "blt", "bge", "ble", "bcc", "bcs", "bls", "bhi"):
                t = int(text.split(" ")[1], 16)
                if not SPLICE[0] <= a < SPLICE[1]:
                    self.assertFalse(SPLICE[0] < t < SPLICE[1], f"{a:#x} {text}")
            a += size

    # behavior (PageCpu)

    def test_page_trace_matches_vanilla_without_bonus(self):
        for stats in ((3, 5, 3), (100, 64, 99), (0, 4, 5)):
            old = run_page(self.before, page_state(self.before, stats, where="none"))
            new = run_page(self.rom, page_state(self.rom, stats, where="none"))
            self.assertEqual(len(old), len(new))
            bars = 0
            for o, n in zip(old, new):
                if o[0] == "blit":
                    v = stats[bars]
                    self.assertEqual((o[1], o[2], o[3][:2], o[3][3], o[4]), (n[1], n[2], n[3][:2], n[3][3], n[4]))
                    self.assertEqual((o[3][2], n[3][2]), (0x3E + vanilla_px(v), 0x3E + spec_px(v)))
                    bars += 1
                else:
                    self.assertEqual(o, n)
            self.assertEqual(bars, 3)

    def test_bar_width_formula(self):
        for v in (0, 4, 5, 99, 100, 120, 125, 126, 127):
            rows = stat_rows(run_page(self.rom, page_state(self.rom, (v, 50, 50), where="none")))
            self.assertEqual(rows[0][1], [(BAR_BUF, 0x3E, 0x3E + spec_px(v))], v)
        self.assertEqual([spec_px(v) for v in (0, 4, 5, 99, 100, 120, 125, 126, 127)],
                         [0, 0, 3, 57, 60, 72, 75, 75, 75])

    def test_gold_segment_from_base_to_live_in_menu(self):
        trace = run_page(self.rom, page_state(self.rom, (100, 100, 100), (120, 110, 100), where="menu"))
        self.assertIn(("query", LIST, 7, 0), trace)
        self.assertEqual(stat_rows(trace), [
            ("100+20", [(BAR_BUF, 62, 122), (self.gold + 60, 122, 134)]),
            ("100+10", [(BAR_BUF, 62, 122), (self.gold + 60, 122, 128)]),
            ("100/100", [(BAR_BUF, 62, 122)])])

    def test_live_from_pointer_outside_menu(self):
        trace = run_page(self.rom, page_state(self.rom, (40, 41, 42), (50, 51, 52), where="field"))
        self.assertFalse([e for e in trace if e[0] == "query"])
        self.assertEqual(stat_rows(trace)[2], ("42+10", [(BAR_BUF, 62, 86), (self.gold + 24, 86, 92)]))

    def test_no_player_shows_base_only(self):
        trace = run_page(self.rom, page_state(self.rom, (40, 41, 42), (50, 51, 52), where="none"))
        self.assertEqual([r[0] for r in stat_rows(trace)], ["40/100", "41/100", "42/100"])
        self.assertTrue(all(len(r[1]) == 1 for r in stat_rows(trace)))

    def test_not_leader_shows_base_only(self):
        trace = run_page(self.rom, page_state(self.rom, (40, 41, 42), (50, 51, 52), where="menu", leader=False))
        self.assertFalse([e for e in trace if e[0] == "query"])
        self.assertEqual([r[0] for r in stat_rows(trace)], ["40/100", "41/100", "42/100"])

    def test_bonus_never_below_zero(self):
        trace = run_page(self.rom, page_state(self.rom, (60, 60, 60), (50, 60, 70), where="menu"))
        rows = stat_rows(trace)
        self.assertEqual(rows[0], ("60/100", [(BAR_BUF, 62, 98)]))
        self.assertEqual(rows[1], ("60/100", [(BAR_BUF, 62, 98)]))
        self.assertEqual(rows[2], ("60+10", [(BAR_BUF, 62, 98), (self.gold + 36, 98, 104)]))

    def test_rage_flat_100_on_low_base(self):                 # RSS 2: Rage sets live to a flat 100
        rows = stat_rows(run_page(self.rom, page_state(self.rom, (30, 3, 100), (100, 100, 100), where="menu")))
        self.assertEqual(rows[0], ("30+70", [(BAR_BUF, 62, 80), (self.gold + 18, 80, 122)]))
        self.assertEqual(rows[1], ("3+97", [(BAR_BUF, 62, 62), (self.gold, 62, 122)]))
        self.assertEqual(rows[2], ("100/100", [(BAR_BUF, 62, 122)]))

    def test_text_mode_live(self):
        rom = rebuild(BONUS_TEXT="live")
        rows = stat_rows(run_page(rom, page_state(rom, (100, 100, 100), (120, 110, 100), where="menu")))
        self.assertEqual([r[0] for r in rows], ["120", "110", "100/100"])

    def test_bonus_text_fits_the_vanilla_box(self):
        widest = font_width(self.rom, "100/100")
        for base in range(101):
            for live in range(base + 1, 256):
                self.assertLessEqual(font_width(self.rom, f"{base}+{live - base}"), widest, (base, live))
        self.assertEqual(font_width(self.rom, "100+20"), 28)
        self.assertEqual(u32(self.rom, self.page + 0x368), FONT)   # the font word the page stores at canvas +0xC

    def test_gold_image(self):
        bar = unpack_frame(BASE_ROM, BAR_FRAME)[2]
        gold = self.rom[self.gold - ROM_BASE:self.gold - ROM_BASE + 600]
        self.assertEqual([p == 0 for p in gold], [p == 0 for p in bar])   # same 2-on 1-off segments
        self.assertEqual(set(gold) - {0}, GOLD_INDICES)
        for row in range(8):
            self.assertEqual(len(set(gold[row * 75:row * 75 + 75]) - {0}), 1)

    # stat items (task 5)

    def test_item_reapplies_form_in_menu(self):
        for handler, item, field in ITEM_HANDLERS:
            for where, want in (("menu", [("query", LIST, 7, 0), ("reapply", PLAYER)]),
                                ("field", [("reapply", PLAYER)]), ("none", [])):
                cpu = page_state(self.rom, (40, 41, 42), where=where)
                calls = []
                stops = {ITEM_TEXT: lambda c: 0,
                         REAPPLY: lambda c: calls.append(("reapply", c.r[0])) or 0,
                         QUERY: lambda c: calls.append(("query", c.r[0], c.r[1], c.r[2])) or PLAYER,
                         EXIT: "exit"}
                cpu.r[0] = item
                self.assertEqual(cpu.run(handler, stops, limit=400), "exit")
                self.assertEqual(cpu.r[0], 1)                   # item used
                self.assertEqual(calls, want, (hex(handler), where))
                self.assertEqual(cpu.load(STRUCT + 0xC + field, 2) >> 8, 40 + (field - 0xA) // 2 + 1)

    def test_item_vanilla_skips_reapply_in_menu(self):     # the bug the patch fixes (RSS 2.2)
        cpu = page_state(self.before, (40, 41, 42), where="menu")
        calls = []
        cpu.r[0] = 2
        cpu.run(ITEM_HANDLERS[0][0], {ITEM_TEXT: lambda c: 0, REAPPLY: lambda c: calls.append(1) or 0,
                                      EXIT: "exit"}, limit=400)
        self.assertEqual(calls, [])

    # patch hygiene

    def test_apply_fails_closed(self):
        from patches import status_bonus
        b = built()
        for off, junk in ((PAGE + 0x40 - ROM_BASE, b"\0"), (0x3B30, b"\0\0\0\0"), (0xF512 + 8, b"\0")):
            rom = bytearray(b["before"])
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                status_bonus.apply(rom, copy.deepcopy(b["alloc"]))
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run ssj2_form first"):
            status_bonus.apply(bytearray(b["before"]), Allocator(len(b["before"]), [(0xF00000, 0x100000)]))

    def test_new_data_in_expansion(self):
        for key in ("page", "text", "gold", "code"):
            self.assertGreaterEqual(self.notes[key], 0x800000, key)
        self.assertTrue(all(at >= 0x800000 for at in self.notes["stubs"].values()))
        self.assertEqual(self.gold - ROM_BASE, self.notes["gold"])

    def test_file_build_matches_memory_build(self):
        self.assertEqual(built()["file"], self.rom)


def stats_gold_literal(rom: bytes) -> int:
    """Address of the pool word stats loads before the gold blit: `ldr r0,=X ; add r1,r1,r0`."""
    texts = listing(rom, stats_of(rom), 120)
    for (a, t), (_, nxt) in zip(texts, texts[1:]):
        if t.startswith("ldr r0,=") and nxt == "add r1,r1,r0":
            return ((a + 4) & ~3) + 4 * (struct.unpack_from("<H", rom, a - ROM_BASE)[0] & 0xFF)
    raise AssertionError("no gold literal in stats")


if __name__ == "__main__":
    unittest.main()
