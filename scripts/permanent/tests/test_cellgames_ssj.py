r"""
test_cellgames_ssj.py - Tests for patches.cellgames_ssj and patches.scene_drain_pause (r27).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_cellgames_ssj.py -v
Builds build_list.txt in memory: "before" = the list up to cellgames_ssj (the r26 bytes), "mid" = after
cellgames_ssj, "rom" = after scene_drain_pause. Scripts are decoded here with an own decoder; the reverse lookup,
ext 73, appearance_revert, portrait() and both ticks run as thumb_dis text in the test_status interpreter.
Expected sites are restated from docs\tasks\2026-10-20-cellgames-ssj\cellgames-ssj-report.md (tables 3b, 6, 7) and the brief
docs\tasks\2026-10-20-r27-build\cellgames-build.md, never imported from the patch modules.
"""
import copy
import struct
import unittest

import log2_build
from tests.test_cutscene import frame, portrait
from tests.test_ssj2 import MSG, RET, read_form
from tests.test_status import PageCpu
from rom.webfoot_decompress import ROM_BASE

# ===== constants =====
STRUCT, STACK, PLAYER, PLAYER_VT = 0x03000E90, 0x03007F00, 0x02000200, 0x02000300
SCRIPT_STACK, IN_STATE = 0x02000600, 0x0EEE2000
SCENE_FLAG, SCENE_DEPTH = 0x03001FDC, 0x03000E24
CALL_R1, CALL_R2, GET_SET, FORM_REAPPLY, ASSERT = 0x08021D2A, 0x08021D2C, 0x08009324, 0x080086A2, 0x0801F878
APPEARANCE_OF_SET, EXT73, REVERT = 0x080042BC, 0x0800A8EC, 0x08003ED4
VANILLA_SSJ_TICK = 0x08017306
FORM_VTABLES = {0x030021E0: 0x08024004, 0x030021E4: 0x08024E4C, 0x030021E8: 0x0802526C,
                0x030021EC: 0x08024C58, 0x030021F0: 0x08024ABC}          # form object init @0x080232E4
SSJ_VTABLE, RAGE_VTABLE, BASE_VTABLE = 0x08024C58, 0x08024E4C, 0x08024004
GOHAN, GOKU = 0, 4

# report 3b and 7 (rows 2, 7, 9), with my 14,1 NPC Goku (brief decision 3)
GOHAN_BYTES = (0x408CA0, 0x408F8C, 0x3E8C2C, 0x3E8D1E, 0x3E8D41, 0x3E921C, 0x3E9226)
GOKU_VARINT = (0x3E946B, 0x3E9807, 0x3E982C, 0x3EA679, 0x3EA698, 0x3EA6D0, 0x3EA793, 0x3EA7ED, 0x3EA7F3,
               0x3EA7FA, 0x3EA801, 0x3EA808, 0x3EA80F, 0x3EA816, 0x3EA891, 0x3EA89F, 0x3EA8A5, 0x3EA8AC,
               0x3EA8B3, 0x3EA8BA, 0x3EA8C1, 0x3EA8C8, 0x3EA8CD, 0x3EA8D8, 0x3EA8E2, 0x3EA951)
GOKU_OP0 = (0x3EA9CA, 0x408D54)
GOHAN_PORTRAITS = (0x3E8170, 0x3E81A0, 0x3E9230, 0x3E934C)               # record offsets, +3 = 59 to 62
GOKU_PORTRAITS = (0x3E9704, 0x3E977C, 0x3E9832, 0x3EA79C, 0x3EA820, 0x3EA8EC, 0x3EA95C, 0x3E8508)
REVERSE_BYTE = 0x800065
WORDS = {0x3E8D98: "entry_seq1", 0x3E9438: "fight_cell_seq21", 0x3EA400: "cell_fight_seq1"}
OLD_RECORDS = {0x3E9438: (0x3E9384, 0x61), 0x3EA400: (0x3E9E8C, 0x5E)}

# scene tables of the stretch (report table 2 and the 14,1 tables): offset: word count
STRETCH = {0x3E81D4: 6, 0x3E8530: 1, 0x3E8084: 2, 0x3E814C: 2, 0x3E8500: 1, 0x3E844C: 1, 0x3E83EC: 3,
           0x3E8310: 1, 0x3E85FC: 2, 0x3E84A4: 1, 0x3E82BC: 1, 0x3E8D98: 28, 0x3E8F50: 5, 0x3E93E8: 21,
           0x3E9D4C: 31, 0x3E9E24: 1, 0x3E9E84: 1, 0x3EA400: 32, 0x3EB704: 65}
POST_CELL = {0x3EC758: 55}
# set argument stack slots per ext op (scripts\one-time\2026-10-18-npc-gi\sites.py POS, the shape the study counted with)
POS = {32: [-2], 33: [-1], 51: [-3], 52: [-1], 53: [-3], 89: [-4, -3], 54: [-3], 143: [-1], 144: [-2], 55: [-2],
       140: [-2], 56: [-2, -1], 57: [-2], 121: [-2], 58: [-2], 60: [-1], 96: [-3, -2], 142: [-3, -2], 99: [-4],
       134: [-3], 135: [-5], 136: [-4], 137: [-2], 62: [-3], 93: [-1], 100: [-3], 94: [-3], 95: [-1], 104: [-2],
       85: [-1], 90: [-3], 112: [-2], 124: [-3], 141: [-1], 73: [-1]}

_CACHE = {}


# ===== build (once) =====

def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list()
        i = names.index("cellgames_ssj")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["cellgames_ssj"])
        _CACHE["mid"] = bytes(rom)
        log2_build.apply_patches(rom, alloc, names[i + 1:names.index("scene_drain_pause") + 1])   # r28 on top
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def words_naming(rom: bytes, addr: int) -> list:
    """File offsets of the aligned ROM words equal to addr."""
    words = memoryview(rom[:len(rom) & ~3]).cast("I")
    return [4 * k for k, w in enumerate(words) if w == addr]


def diff(a: bytes, b: bytes) -> list:
    return [i for c in range(0, len(a), 0x1000) if a[c:c + 0x1000] != b[c:c + 0x1000]
            for i in range(c, c + 0x1000) if a[i] != b[i]]


# ===== script decoder (own copy, interpreter @0x080092E4) =====

def varint(rom: bytes, o: int) -> tuple:
    v = 0
    while True:
        c, o = rom[o], o + 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return (-(v >> 1) if v & 1 else v >> 1), o


def ops(rom: bytes, o: int) -> list:
    """[(offset, op, arg)] of a type 0 record body from o to its last `end`; arg = values, ext n or target."""
    out, far = [], 0
    while True:
        start, op = o, rom[o]
        o += 1
        arg = None
        if op == 0:
            arg, o = [rom[o]], o + 1
        elif op == 1:
            v, o = varint(rom, o)
            arg = [v]
        elif op == 29:
            n, o, arg = rom[o], o + 1, []
            for _ in range(n):
                v, o = varint(rom, o)
                arg.append(v)
        elif op in (2, 3) or 21 <= op <= 26:
            arg, o = rom[o], o + 1
        elif op in (18, 19):
            arg, o = start + 2 + rom[o], o + 1
            far = max(far, arg)
        elif op == 28:
            arg, o = start + 2 - rom[o], o + 1
        elif not (4 <= op <= 17 or op in (20, 27)):
            raise ValueError(f"rom:0x{start:X}: op {op}")
        out.append((start, op, arg))
        if op == 17 and o > far:
            return out


def calls(rom: bytes, o: int) -> list:
    """[(call offset, ext n, constant stack before the call)]."""
    st, out = [], []
    for at, op, arg in ops(rom, o):
        if op in (0, 1, 29):
            st += arg
        elif op == 2:
            out.append((at, arg, list(st)))
            st.append("r")
        elif op in (17, 18, 19, 28):
            st = []
        else:
            st.append("?")
    return out


def records(rom: bytes, tables: dict) -> list:
    """(table, record offset) for each word of each table that points at a record."""
    out = []
    for t, n in tables.items():
        for k in range(n):
            w = u32(rom, t + 4 * k)
            if ROM_BASE <= w < ROM_BASE + len(rom):
                out.append((t, w - ROM_BASE))
    return out


def set_hits(rom: bytes, tables: dict, ids: set) -> list:
    """(table, ext n, set id) for every set argument in ids, at the POS slots, in type 0 records."""
    out = []
    for t, rec in records(rom, tables):
        if rom[rec + 1:rec + 3] != b"\0\0":
            continue
        for _, n, st in calls(rom, rec + 3):
            out += [(t, n, st[p]) for p in POS.get(n, []) if len(st) >= -p and st[p] in ids]
    return out


def ext_sequence(rom: bytes, rec: int) -> list:
    """[(ext n, constant args)] of a type 0 record, args = the values pushed since the previous call."""
    out, args = [], []
    for at, op, arg in ops(rom, rec + 3):
        if op in (0, 1, 29):
            args += arg
        elif op == 2:
            out.append((arg, tuple(args)))
            args = []
    return out


# ===== interpreter helpers =====

def cpu_with(rom: bytes, leader: int, entries: dict) -> PageCpu:
    """Save struct with a leader and record entries {char: entry}; form objects; player at PLAYER."""
    cpu = PageCpu(rom)
    cpu.store(STRUCT, 1, leader)
    for ch in range(6):
        cpu.store(STRUCT + 0xC + 28 * ch + 8, 1, entries.get(ch, 2 if ch == GOHAN else 6))
    for obj, vt in FORM_VTABLES.items():
        cpu.store(obj, 4, vt)
    cpu.store(0x03001FA8, 4, PLAYER)                                     # player_ptr
    cpu.store(PLAYER, 4, PLAYER_VT)
    cpu.r[13], cpu.r[14] = STACK, RET | 1
    cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
    return cpu


def set_header(rom: bytes, set_id: int) -> int:
    return u32(rom, u32(rom, 0x959C) - ROM_BASE + 4 * (set_id - 7))


def entry_form_vtable(rom: bytes, entry: int, cpu: PageCpu) -> int:
    table = u32(rom, 0xAA04) - ROM_BASE                                 # ext 73's own table literal
    obj = u32(rom, table + 20 * entry + 0x10)
    return cpu.load(obj, 4)


def run_ext73(rom: bytes, char: int, set_id: int, leader: int, entries: dict) -> tuple:
    """(result, cpu, virtual calls [(slot target)], player +0x48) for ext 73 (char, set_id)."""
    cpu = cpu_with(rom, leader, entries)
    cpu.store(SCRIPT_STACK, 4, 2)
    cpu.store(SCRIPT_STACK + 4, 4, char)
    cpu.store(SCRIPT_STACK + 8, 4, set_id)
    virt = []
    stops = {CALL_R1: lambda c: virt.append(("r1", c.r[1] & ~1, c.r[0])) or 0,
             CALL_R2: lambda c: virt.append(("r2", c.r[2] & ~1, c.r[0])) or 0,
             GET_SET: lambda c: set_header(rom, c.r[0]),
             FORM_REAPPLY: lambda c: virt.append(("reapply", 0, c.r[0])) or 0,
             ASSERT: "assert", RET: "ret"}
    cpu.r[0] = SCRIPT_STACK
    result = cpu.run(EXT73, stops, 600)
    return result, cpu, virt, cpu.load(PLAYER + 0x48, 4)


def vt_method(rom: bytes, vt: int, slot: int) -> int:
    return (vt + struct.unpack_from("<i", rom, vt - ROM_BASE + slot)[0]) & ~1 & 0xFFFFFFFF


def run_tick(rom: bytes, tick: int, flag: int, depth: int, ep: int, acc: int, hp: int = 100) -> tuple:
    """(EP, accumulator, messages) after one tick(form, player) with leader Gohan."""
    cpu = cpu_with(rom, GOHAN, {GOHAN: 5})
    rec = STRUCT + 0xC
    cpu.store(rec, 2, hp)
    cpu.store(rec + 4, 2, ep)
    cpu.store(PLAYER + 0x184, 4, acc)
    cpu.store(SCENE_FLAG, 4, flag)
    cpu.store(SCENE_DEPTH, 4, depth)
    cpu.store(PLAYER_VT + 0x28, 4, (MSG | 1) - PLAYER_VT)
    cpu.store(PLAYER_VT + 0x2C, 4, (IN_STATE | 1) - PLAYER_VT)
    msgs = []
    stops = {MSG: lambda c: msgs.append(c.r[1]) or 0, IN_STATE: lambda c: 0, RET: "ret"}
    cpu.r[0], cpu.r[1] = 0x030021EC, PLAYER
    if cpu.run(tick, stops, 400) != "ret":
        raise AssertionError("tick did not return")
    return cpu.load(rec + 4, 2, signed=True), cpu.load(PLAYER + 0x184, 4), msgs


# ===== tests: cellgames_ssj =====

class CellGamesSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]

    def test_build_list_holds_the_r27_patches_in_order(self):
        names = built()["names"]
        i = names.index("rage_stats")
        self.assertEqual(names[i:i + 4], ["rage_stats", "cellgames_ssj", "scene_drain_pause", "fullpower_ssj"])

    def test_npc_set_bytes_old_and_new(self):
        for off in GOHAN_BYTES:
            self.assertEqual((self.before[off], self.rom[off]), (0x9D, 0x9E), hex(off))
        for off in GOKU_VARINT:
            self.assertEqual((self.before[off], self.rom[off]), (0x78, 0x7A), hex(off))
        for off in GOKU_OP0:
            self.assertEqual((self.before[off], self.rom[off]), (0x3C, 0x3D), hex(off))

    def test_portrait_bytes_old_and_new(self):
        for rec in GOHAN_PORTRAITS:
            self.assertEqual((self.before[rec + 3], self.rom[rec + 3]), (59, 62), hex(rec))
        for rec in GOKU_PORTRAITS:
            self.assertEqual((self.before[rec + 3], self.rom[rec + 3]), (63, 65), hex(rec))

    def test_reverse_copy_entry_5_names_158(self):
        copy_at = u32(self.rom, 0x42F0) - ROM_BASE
        self.assertEqual(copy_at + 5 * 20 + 1, REVERSE_BYTE)
        self.assertEqual((self.before[REVERSE_BYTE], self.rom[REVERSE_BYTE]), (59, 158))

    def test_relocated_records_are_old_plus_the_change(self):
        moved = self.notes["cellgames_ssj"]["records"]
        npc_copy = self.notes["npc_gi"]["records"][0x3E8610]
        olds = {0x3E8D98: (npc_copy, 0xD4), **OLD_RECORDS}
        for word, (old, length) in olds.items():
            new = moved[WORDS[word]]
            with self.subTest(word=hex(word)):
                self.assertEqual(u32(self.before, word), old + ROM_BASE)
                self.assertEqual(u32(self.rom, word), new + ROM_BASE)
                self.assertEqual(words_naming(self.before, old + ROM_BASE), [word])
                self.assertEqual(self.rom[old:old + length], self.before[old:old + length])   # old one unchanged
                self.assertEqual(self.rom[new:new + 3], self.before[old:old + 3])
                self.assertFalse([op for _, op, _ in ops(self.rom, new + 3) if op in (18, 19, 28)])
        seq = lambda w: ext_sequence(self.rom, moved[WORDS[w]])                 # noqa: E731
        old_seq = lambda w, o: ext_sequence(self.before, o)                     # noqa: E731
        goku = [(46, (55,)), (57, (0, 9)), (42, (10,)), (47, (55,)), (73, (4, 61)), (43, (10,))]
        a, b = old_seq(0x3E8D98, npc_copy), seq(0x3E8D98)
        self.assertEqual(b, [(n, tuple(158 if v == 157 else v for v in args)) for n, args in a[:-1]] + goku + a[-1:])
        self.assertEqual(a[-1], (46, (50,)))                                     # the insert sits before push 50
        a, b = old_seq(0x3E9438, 0x3E9384), seq(0x3E9438)
        i = a.index((70, (0,)))
        fix = [(n, tuple({157: 158, 60: 61}.get(v, v) if n in (51, 52) else v for v in args)) for n, args in a]
        self.assertEqual(b, fix[:i] + [(73, (0, 158))] + fix[i:])
        a, b = old_seq(0x3EA400, 0x3E9E8C), seq(0x3EA400)
        i = a.index((70, (0,)))
        self.assertEqual(b, a[:i] + [(73, (0, 158)), (110, (0, 5000))] + a[i:])

    def test_goku_power_up_runs_before_his_set_changes(self):
        b = ext_sequence(self.rom, self.notes["cellgames_ssj"]["records"]["entry_seq1"])
        self.assertLess(b.index((57, (0, 9))), b.index((73, (4, 61))))
        last_place = max(i for i, (n, args) in enumerate(b) if n == 53 and args[:1] == (0,))
        self.assertLess(last_place, b.index((57, (0, 9))))                   # Goku stands on his mark first
        self.assertEqual([n for n, _ in b].count(73), 1)

    def test_stretch_names_158_and_61_only(self):
        hits = set_hits(self.rom, STRETCH, {157, 158, 60, 61})
        npc = [(n, s) for _, n, s in hits if n != 73]
        self.assertEqual(sorted(s for _, s in npc), [61] * 28 + [158] * 8)
        self.assertEqual(sorted((n, s) for _, n, s in hits if n == 73), [(73, 61), (73, 158), (73, 158)])
        before = set_hits(self.before, STRETCH, {157, 158, 60, 61})
        self.assertEqual(sorted(s for _, n, s in before if n != 73), [60] * 28 + [157] * 8)
        self.assertEqual(sorted(s for _, _, s in set_hits(self.rom, POST_CELL, {157, 158, 60, 61})), [157] * 5)

    def test_each_scene_spawns_the_npc_it_addresses(self):
        hits = set_hits(self.rom, STRETCH, {158, 61})
        for table, sid in ((0x3E8D98, 158), (0x3E93E8, 61), (0x3E9D4C, 61), (0x3EB704, 61)):
            self.assertIn((table, 51, sid), hits, hex(table))
        self.assertEqual([self.rom[o] for o in (0x408CA0, 0x408F8C, 0x408D54)], [158, 158, 61])

    def test_post_cell_group_keeps_157(self):
        self.assertEqual(self.rom[0x3EC758:0x3EC758 + 4 * 55], self.before[0x3EC758:0x3EC758 + 4 * 55])
        for _, rec in records(self.rom, POST_CELL):
            if self.rom[rec + 1:rec + 3] == b"\0\0":
                self.assertEqual(calls(self.rom, rec + 3), calls(self.before, rec + 3), hex(rec))

    def test_no_ext73_names_59(self):
        shape_a = [s for _, n, s in set_hits(self.rom, {**STRETCH, **POST_CELL}, {59}) if n == 73]
        shape_b = [o for o in range(0x3B5000, 0x420000) if self.rom[o:o + 4] == bytes([0, 59, 2, 73])]
        shape_b += [o for o in range(0x800000, 0xF00000 - 4)
                    if self.rom[o:o + 4] == bytes([0, 59, 2, 73]) and self.rom[o] != 0xFF]
        self.assertEqual((shape_a, shape_b), ([], []))

    def test_dialog_portraits_in_the_stretch(self):
        raw = {}
        for t, rec in records(self.rom, STRETCH):
            if self.rom[rec + 1] == 0 and 1 <= self.rom[rec + 2] <= 4:
                raw.setdefault(self.rom[rec + 3], []).append(rec)
        self.assertNotIn(59, raw)
        self.assertNotIn(63, raw)
        self.assertEqual(sorted(raw[62]), sorted(GOHAN_PORTRAITS))
        self.assertEqual(sorted(raw[65]), sorted(GOKU_PORTRAITS))


class CellGamesFailClosedTests(unittest.TestCase):
    def apply_to(self, rom: bytearray, alloc) -> None:
        from patches import cellgames_ssj
        cellgames_ssj.apply(rom, alloc)

    def test_any_old_byte_or_record_change_refuses_before_writing(self):
        b = built()
        npc_copy = b["alloc_before"].notes["npc_gi"]["records"][0x3E8610]
        sites = list(GOHAN_BYTES + GOKU_VARINT + GOKU_OP0 + (REVERSE_BYTE,)) + \
            [r + 3 for r in GOHAN_PORTRAITS + GOKU_PORTRAITS] + [0x3E8D98, 0x3E9438, 0x3EA400, npc_copy + 0x10,
                                                                 0x3E9384 + 0x30, 0x3E9E8C + 0x30]
        for off in sites:
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snapshot = bytes(rom)
            with self.subTest(off=hex(off)), self.assertRaises(ValueError):
                self.apply_to(rom, alloc)
            self.assertEqual(bytes(rom), snapshot, hex(off))
            self.assertNotIn("cellgames_ssj", alloc.notes)

    def test_second_run_and_missing_notes_raise(self):
        b = built()
        rom, alloc = bytearray(b["mid"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["cellgames_ssj"] = {}
        with self.assertRaisesRegex(ValueError, "already ran"):
            self.apply_to(rom, alloc)
        alloc = copy.deepcopy(b["alloc_before"])
        del alloc.notes["npc_gi"]
        with self.assertRaisesRegex(ValueError, "needs"):
            self.apply_to(bytearray(b["before"]), alloc)


class CellGamesCodeTests(unittest.TestCase):
    """Reverse lookup, ext 73, appearance_revert and portrait() run on the built ROM."""

    @classmethod
    def setUpClass(cls):
        cls.rom = built()["rom"]

    def lookup(self, set_id: int):
        cpu = cpu_with(self.rom, GOHAN, {})
        rec = STRUCT + 0xC
        cpu.store(rec + 8, 1, 0xEE)
        cpu.r[0], cpu.r[1] = rec, set_id
        result = cpu.run(APPEARANCE_OF_SET, {RET: "ret", ASSERT: "assert"}, 600)
        return result, cpu.load(rec + 8, 1)

    def test_reverse_lookup_entries(self):
        for set_id, entry in ((158, 5), (157, 2), (160, 4), (61, 20), (60, 19)):
            self.assertEqual(self.lookup(set_id), ("ret", entry), set_id)
        self.assertEqual(self.lookup(59)[0], "assert")

    def test_ext73_gohan_158_as_leader(self):
        result, cpu, virt, sprite = run_ext73(self.rom, GOHAN, 158, GOHAN, {GOHAN: 2})
        self.assertEqual(result, "ret")
        self.assertEqual(cpu.load(STRUCT + 0xC + 8, 1), 5)
        self.assertEqual(sprite, set_header(self.rom, 158))
        self.assertEqual(entry_form_vtable(self.rom, 5, cpu), SSJ_VTABLE)
        self.assertEqual(virt[0][:2], ("r1", vt_method(self.rom, BASE_VTABLE, 0xC)))       # base leave
        self.assertEqual(virt[-1][:2], ("r1", vt_method(self.rom, SSJ_VTABLE, 0x8)))       # SSJ enter
        self.assertIn(("reapply", 0, PLAYER), virt)

    def test_ext73_gohan_158_not_leader_writes_only_the_record(self):
        result, cpu, virt, sprite = run_ext73(self.rom, GOHAN, 158, GOKU, {GOHAN: 2, GOKU: 20})
        self.assertEqual((result, cpu.load(STRUCT + 0xC + 8, 1), virt, sprite), ("ret", 5, [], 0))

    def test_ext73_goku_61_as_leader(self):
        result, cpu, virt, sprite = run_ext73(self.rom, GOKU, 61, GOKU, {GOKU: 19})
        self.assertEqual((result, cpu.load(STRUCT + 0xC + 28 * GOKU + 8, 1)), ("ret", 20))
        self.assertEqual(sprite, set_header(self.rom, 61))
        self.assertEqual(entry_form_vtable(self.rom, 20, cpu), SSJ_VTABLE)
        self.assertEqual(virt[-1][:2], ("r1", vt_method(self.rom, SSJ_VTABLE, 0x8)))

    def test_ext73_rage_from_super_saiyan(self):
        result, cpu, virt, sprite = run_ext73(self.rom, GOHAN, 160, GOHAN, {GOHAN: 5})
        self.assertEqual((result, cpu.load(STRUCT + 0xC + 8, 1)), ("ret", 4))
        self.assertEqual(virt[0][:2], ("r1", vt_method(self.rom, SSJ_VTABLE, 0xC)))        # SSJ leave
        self.assertEqual(virt[-1][:2], ("r1", vt_method(self.rom, RAGE_VTABLE, 0x8)))      # Rage enter
        self.assertEqual(sprite, set_header(self.rom, 160))

    def revert(self, leader: int, entries: dict) -> dict:
        cpu = cpu_with(self.rom, leader, entries)
        cpu.r[0] = STRUCT
        self.assertEqual(cpu.run(REVERT, {RET: "ret"}, 400), "ret")
        return {ch: cpu.load(STRUCT + 0xC + 28 * ch + 8, 1) for ch in entries}

    def test_ext70_reverts(self):
        self.assertEqual(self.revert(GOHAN, {GOHAN: 5, GOKU: 20}), {GOHAN: 5, GOKU: 19})    # Gohan leads
        self.assertEqual(self.revert(1, {GOHAN: 5}), {GOHAN: 2})                           # Piccolo leads
        self.assertEqual(self.revert(1, {GOHAN: 4}), {GOHAN: 2})

    def test_portraits_shown(self):
        rom = self.rom
        self.assertEqual(portrait(rom, 62, 2)[0], frame(rom, 115))           # NPC Gohan, record in gi base
        self.assertEqual(portrait(rom, 1, 5)[0], frame(rom, 115))            # Gohan leads in SSJ
        self.assertEqual(portrait(rom, 1, 2, leader=GOKU, others=20)[0], frame(rom, 65))   # Goku leads in SSJ
        self.assertEqual(portrait(rom, 65, 2)[0], frame(rom, 65))            # NPC Goku
        self.assertEqual(portrait(rom, 64, 2)[0], frame(rom, 64))            # Other World Goku stays

    def test_anim_rows(self):
        def has(set_id: int, anim: int) -> bool:
            h = set_header(self.rom, set_id) - ROM_BASE
            return anim < self.rom[h + 2] and all(u32(self.rom, h + 0x4C + anim * 16 + d * 4) for d in range(4))
        for set_id, anims in ((158, (0, 1, 4, 6, 9)), (61, (0, 1)), (60, (9,))):
            for anim in anims:
                self.assertTrue(has(set_id, anim), (set_id, anim))
        self.assertFalse(has(61, 9))                                          # why state 9 runs before ext 73


# ===== tests: scene_drain_pause =====

class DrainPauseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.mid, cls.notes = b["rom"], b["mid"], b["notes"]
        cls.ssj2_vt = cls.notes["ssj2_form"]["vtable"] + ROM_BASE
        cls.ticks = {"ssj": vt_method(cls.rom, SSJ_VTABLE, 4), "ssj2": vt_method(cls.rom, cls.ssj2_vt, 4)}

    def test_tick_slots_point_at_the_new_ticks(self):
        n = self.notes["scene_drain_pause"]
        self.assertEqual(self.ticks, {"ssj": n["tick_ssj"] + ROM_BASE, "ssj2": n["tick_ssj2"] + ROM_BASE})
        self.assertEqual(vt_method(self.mid, SSJ_VTABLE, 4), VANILLA_SSJ_TICK)
        self.assertEqual(vt_method(self.mid, self.ssj2_vt, 4), self.notes["ssj2_form"]["tick"] + ROM_BASE)
        for vt in (SSJ_VTABLE, self.ssj2_vt):
            for slot in (0, 8, 0xC, 0x10, 0x14):
                self.assertEqual(vt_method(self.rom, vt, slot), vt_method(self.mid, vt, slot), (hex(vt), slot))
        for vt in (0x08024004, 0x08024E4C, 0x0802526C, 0x08024ABC):          # base, Rage, Super, Namek
            off = vt - ROM_BASE
            self.assertEqual(self.rom[off:off + 24], self.mid[off:off + 24], hex(vt))

    def test_read_form_still_sees_each_drain(self):
        self.assertEqual(read_form(self.rom, 5).ki_drain, 0xCCD)             # Gohan Super Saiyan
        self.assertEqual(read_form(self.rom, 20).ki_drain, 0xCCD)            # Goku Super Saiyan
        self.assertEqual(read_form(self.rom, 22).ki_drain, 0x199A)           # Gohan Super Saiyan 2
        self.assertEqual(read_form(self.rom, 4).ki_drain, 0)                 # Rage: no drain, as before

    def test_scene_pauses_the_drain(self):
        for k, tick in self.ticks.items():
            with self.subTest(form=k):
                self.assertEqual(run_tick(self.rom, tick, 1, 1, 50, 0xFFF0), (50, 0xFFF0, []))
                self.assertEqual(run_tick(self.rom, tick, 1, 2, 0, 0xFFF0), (0, 0xFFF0, []))   # no revert either

    def test_free_play_drains_as_before(self):
        steps = {"ssj": 0xCCD, "ssj2": 0x199A}
        olds = {"ssj": VANILLA_SSJ_TICK, "ssj2": self.notes["ssj2_form"]["tick"] + ROM_BASE}
        for k, tick in self.ticks.items():
            for flag, depth in ((0, 0), (1, 0), (0, 1)):        # free play; stale flag after ext 97; menu or fade
                for ep, acc in ((50, 0xFFF0), (50, 0), (1, 0xFFF0), (0, 0xFFF0)):
                    with self.subTest(form=k, flag=flag, depth=depth, ep=ep, acc=acc):
                        got = run_tick(self.rom, tick, flag, depth, ep, acc)
                        self.assertEqual(got, run_tick(self.mid, olds[k], flag, depth, ep, acc))
                        self.assertEqual(got[1], (acc + steps[k]) & 0xFFFF)
        self.assertEqual(run_tick(self.rom, self.ticks["ssj"], 0, 0, 1, 0xFFF0), (0, 0xCBD, [0x24]))

    def test_twenty_frames_cost_one_ep_outside_scenes(self):
        cpu_ep, acc = 50, 0
        for _ in range(20):
            cpu_ep, acc, _ = run_tick(self.rom, self.ticks["ssj"], 0, 0, cpu_ep, acc)
        self.assertEqual(cpu_ep, 49)
        for _ in range(200):
            cpu_ep, acc, _ = run_tick(self.rom, self.ticks["ssj"], 1, 1, cpu_ep, acc)
        self.assertEqual(cpu_ep, 49)

    def test_old_code_stays(self):
        for off, size in ((VANILLA_SSJ_TICK - ROM_BASE, 0x70), (self.notes["ssj2_form"]["tick"], 0x70)):
            self.assertEqual(self.rom[off:off + size], self.mid[off:off + size])


# ===== tests: r26 to r27 diff =====

def expected_sites(notes: dict, used_after: list) -> list:
    """(start, end, name) of every byte r27 may change; new data = allocations after the r26 cursor."""
    sites = [(o, o + 1, "npc set") for o in GOHAN_BYTES + GOKU_VARINT + GOKU_OP0]
    sites += [(r + 3, r + 4, "portrait") for r in GOHAN_PORTRAITS + GOKU_PORTRAITS]
    sites += [(REVERSE_BYTE, REVERSE_BYTE + 1, "reverse copy")]
    sites += [(w, w + 4, "table word") for w in WORDS]
    sites += [(0x24C5C, 0x24C60, "ssj tick slot"), (notes["ssj2_form"]["vtable"] + 4,
                                                    notes["ssj2_form"]["vtable"] + 8, "ssj2 tick slot")]
    sites += [(a, a + n, "new data") for a, n in used_after]
    return sites


def outside(changed: list, sites: list) -> list:
    return [hex(i) for i in changed if not any(a <= i < e for a, e, _ in sites)]


class DiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]
        n_before = len(b["alloc_before"].used())
        cls.new_used = b["used"][n_before:]
        cls.changed = diff(cls.before, cls.rom)

    def test_earlier_allocations_unchanged(self):
        n = len(built()["alloc_before"].used())
        self.assertEqual(built()["used"][:n], built()["alloc_before"].used())
        self.assertTrue(all(a >= 0x89A5C4 and a + s <= 0xF00000 for a, s in self.new_used))

    def test_only_expected_sites_change(self):
        sites = expected_sites(self.notes, self.new_used)
        self.assertEqual(outside(self.changed, sites), [])
        for a, e, name in sites:
            if name != "new data":
                self.assertTrue(any(a <= i < e for i in self.changed), (hex(a), name))

    def test_art_and_palette_unchanged(self):
        block = self.notes["npc_gi"]["block"]
        self.assertEqual(self.rom[0xF00000:], self.before[0xF00000:])                      # portrait slots
        self.assertEqual(self.rom[block:block + 4 + 4 * 122], self.before[block:block + 4 + 4 * 122])
        self.assertEqual(self.rom[0x1DA6C8:0x1DA6C8 + 512], self.before[0x1DA6C8:0x1DA6C8 + 512])
        self.assertEqual(self.rom[0x3ECBA4:0x3ECBA4 + 3 * 512], self.before[0x3ECBA4:0x3ECBA4 + 3 * 512])

    def test_dropping_any_site_is_caught(self):
        sites = expected_sites(self.notes, self.new_used)
        for k, (a, e, name) in enumerate(sites):
            if name == "new data":
                continue
            with self.subTest(site=hex(a)):
                self.assertTrue(outside(self.changed, sites[:k] + sites[k + 1:]))


if __name__ == "__main__":
    unittest.main()
