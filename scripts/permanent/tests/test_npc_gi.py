r"""
test_npc_gi.py - Tests for patches.npc_gi: armor before the player controls Gohan after the chamber, gi after.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_npc_gi.py -v
Builds the r14 patch list in memory, then npc_gi. Scripts are decoded here with an own decoder (not the patch's
relocate()), and portrait() runs in the test_status interpreter through test_cutscene.portrait.
Source:  docs\tasks\2026-10-18-npc-gi\npc-gi-report.md (timeline table), docs\research\re-outfit.md section 5.
"""
import importlib
import struct
import unittest

import log2_build
from rom.rom_space import Allocator
from tests.test_cutscene import frame, portrait
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE

# ===== constants =====
BASE_ROM = log2_build.BASE.read_bytes()
R14 = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle", "cutscene_portraits")
SCRIPT_REGION = (0x3B5000, 0x420000)
ACTOR_OPS = {51: -3, 52: -1, 53: -3, 54: -3, 55: -2, 56: -2, 57: -2, 62: -3}   # ext op: set-id stack slot
EXT73 = 73
CHAMBER_EXIT, CELL_ENTRY, FIGHT_CELL, POST_CELL = 0x3DBDD4, 0x3E8D98, 0x3E93E8, 0x3EC758   # scene tables
PRE_59, PRE_ID = (0x3DB930, 0x3DBABC), 121
POST_59 = (0x3DBFDC, 0x3DC1AC, 0x3DC870, 0x3DCE54, 0x3DCECE, 0x3E8170, 0x3E81A0, 0x3E9230, 0x3E934C)
ALL_ENTRIES = (0, 1, 2, 3, 4, 5, 22)
# site: (old, new) restated from the report timeline table
IN_PLACE = {0x3DB627: "1d020070:0000009d", 0x3E8C2B: "1d027000:009d0000", 0x3E8D1D: "1d027000:009d0000",
            0x3E8D40: "1d027000:009d0000", 0x3E921B: "1d027006:009d0003", 0x3E9225: "1d027000:009d0000",
            0x3E939A: "0038:009d", 0x408CA0: "38000000:9d000000", 0x408F8C: "38000000:9d000000"}
MOVED = {0x3E8610: (0x3E8D98, {0x3E866C: "1d037087408c50:009d1d0287408c50",
                               0x3E8681: "1d037087408b00:009d1d0287408b00"}),
         0x3EBE1C: (0x3EC7A4, {0x3EBFF8: "1d020070:0000009d", 0x3EC01A: "1d037086608670:009d1d0286608670",
                               0x3EC023: "1d027002:009d0001"}),
         0x3EC298: (0x3EC7E8, {0x3EC2CB: "1d037086008830:009d1d0286008830", 0x3EC2D4: "0038:009d"})}
_CACHE = {}


def built() -> dict:
    if not _CACHE:
        rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        for name in R14:
            importlib.import_module(f"patches.{name}").apply(rom, alloc)
        _CACHE["before"], _CACHE["mark"] = bytes(rom), max(a + n for a, n in alloc.used())
        _CACHE["before_notes"] = {k: dict(v) for k, v in alloc.notes.items()}
        importlib.import_module("patches.npc_gi").apply(rom, alloc)
        _CACHE["rom"], _CACHE["notes"] = bytes(rom), alloc.notes
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


# ===== script decoder (own copy: the patch's relocate() is under test) =====

def varint(rom: bytes, o: int) -> tuple:
    v = 0
    while True:
        c, o = rom[o], o + 1
        v = (v << 7) | (c & 0x7F)
        if not c & 0x80:
            return (-(v >> 1) if v & 1 else v >> 1), o


def ops(rom: bytes, o: int) -> list:
    """[(offset, op, values or jump target or ext n)] of the bytecode at o, to its last `end`."""
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


def set_calls(rom: bytes, o: int) -> list:
    """[(call offset, ext n, set id)] for actor ops and ext 73 with a constant set argument."""
    st, out = [], []
    for at, op, arg in ops(rom, o):
        if op in (0, 1, 29):
            st += arg
        elif op == 2:
            slot = -1 if arg == EXT73 else ACTOR_OPS.get(arg)
            if slot is not None and len(st) >= -slot and isinstance(st[slot], int):
                out.append((at, arg, st[slot]))
            st.append("r")
        elif op == 17 or op in (18, 19, 28):
            st = []
        else:
            st.append("?")
    return out


def scene_records(rom: bytes, moved: dict) -> dict:
    """{table word offset: record offset} for aligned base words that point at a type 0 record."""
    lo, hi = SCRIPT_REGION
    out = {}
    for w in range(0, log2_build.BASE_SIZE, 4):
        p = u32(rom, w) - ROM_BASE
        if (lo <= p < hi or p in moved) and rom[p + 1] == 0 and rom[p + 2] == 0:
            out[w] = p
    return out


def table_start(rom: bytes, w: int, moved: dict) -> int:
    def ok(o: int) -> bool:
        p = u32(rom, o) - ROM_BASE
        return SCRIPT_REGION[0] <= p < SCRIPT_REGION[1] or p in moved
    while ok(w - 4):
        w -= 4
    return w


def gohan_by_table(rom: bytes, moved: dict, ids=(56, 157)) -> dict:
    """{scene table: sorted [(ext n, set id)]} for Gohan's set ids in actor ops and ext 73."""
    out = {}
    for w, rec in scene_records(rom, moved).items():
        try:
            calls = set_calls(rom, rec + 3)
        except (ValueError, IndexError):
            continue
        hits = [(n, s) for _, n, s in calls if s in ids]
        if hits:
            out.setdefault(table_start(rom, w, moved), []).extend(hits)
    return {t: sorted(h) for t, h in out.items()}


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes, cls.mark = b["rom"], b["before"], b["notes"], b["mark"]
        cls.moved = {v: k for k, v in cls.notes["npc_gi"]["records"].items()}   # new offset: old offset

    def test_in_place_sites_old_and_new(self):
        for off, pair in IN_PLACE.items():
            old, new = (bytes.fromhex(x) for x in pair.split(":"))
            self.assertEqual(self.before[off:off + len(old)], old, hex(off))
            self.assertEqual(self.rom[off:off + len(new)], new, hex(off))

    def test_relocated_records_differ_only_in_the_set_id(self):
        for old, (word, edits) in MOVED.items():
            new = self.notes["npc_gi"]["records"][old]
            self.assertEqual(u32(self.before, word), old + ROM_BASE)
            self.assertEqual(u32(self.rom, word), new + ROM_BASE)
            self.assertEqual([w for w in range(0, log2_build.BASE_SIZE, 4) if u32(self.before, w) == old + ROM_BASE],
                             [word], hex(old))
            self.assertEqual(self.rom[new:new + 3], self.before[old:old + 3])
            a, b = ops(self.before, old + 3), ops(self.rom, new + 3)
            pushed_a = [(157 if at in edits and v == 56 else v) for at, op, arg in a if op in (0, 1, 29) for v in arg]
            pushed_b = [v for _, op, arg in b if op in (0, 1, 29) for v in arg]
            self.assertEqual(pushed_b, pushed_a, hex(old))                 # same values, 56 to 157 at the sites
            self.assertEqual(sum(1 for at, _, arg in a if at in edits for v in arg if v == 56), len(edits))
            rest = lambda lst: [(op, arg) for _, op, arg in lst if op not in (0, 1, 29, 18, 19, 28)]   # noqa: E731
            self.assertEqual(rest(b), rest(a), hex(old))                    # every other op unchanged
            for site, pair in edits.items():                                # the old bytes stay, unreferenced
                o, n = pair.split(":")
                self.assertEqual(self.rom[site:site + len(o) // 2].hex(), o, hex(site))
                self.assertIn(n, self.rom[new:new + 0x300].hex(), hex(site))

    def test_relocated_jump_targets_map(self):              # post-Cell seq 20 has one loop before the edits
        old, new = 0x3EBE1C, self.notes["npc_gi"]["records"][0x3EBE1C]
        a = [(at - old, arg - old) for at, op, arg in ops(self.before, old + 3) if op == 28]
        b = [(at - new, arg - new) for at, op, arg in ops(self.rom, new + 3) if op == 28]
        self.assertEqual(a, b)
        self.assertEqual(len(a), 1)

    def test_push_values_per_site(self):
        for old, (_, edits) in MOVED.items():
            new = self.notes["npc_gi"]["records"][old]
            got = [c for c in set_calls(self.rom, new + 3) if c[2] in (56, 157)]
            want = [c for c in set_calls(self.before, old + 3) if c[2] in (56, 157)]
            self.assertEqual([(n, 157) for _, n, _ in want], [(n, s) for _, n, s in got], hex(old))

    def test_reverse_lookup_finds_157_in_entry_2(self):
        copy = u32(self.rom, 0x42F0) - ROM_BASE
        find = lambda s: next((e for e in range(22) if self.rom[copy + 20 * e + 1] == s), None)   # noqa: E731
        self.assertEqual((find(157), find(160), find(53), find(55), find(56)), (2, 4, 0, 1, None))
        self.assertEqual(self.rom[copy:copy + 440][:41] + self.rom[copy + 42:copy + 440],
                         self.before[copy:copy + 41] + self.before[copy + 42:copy + 440])

    def test_ext73_never_names_set_56(self):               # 56 is no longer in the reverse lookup copy
        moved = set(self.moved)
        found = []
        for w, rec in scene_records(self.rom, moved).items():
            try:
                found += [(rec, s) for _, n, s in set_calls(self.rom, rec + 3) if n == EXT73]
            except (ValueError, IndexError):
                pass
        self.assertNotIn(56, [s for _, s in found])
        self.assertEqual(sorted(s for _, s in found if s in (157, 160)), [157, 157, 160])
        raw = [o for o in range(*SCRIPT_REGION) if self.rom[o:o + 6].hex() in ("1d0200700249", "000000380249")]
        self.assertEqual(raw, [0x3EBFF8])                  # only the dead old post-Cell record keeps the bytes

    def test_gohan_set_by_scene(self):
        got = gohan_by_table(self.rom, set(self.moved))
        self.assertEqual(got, {
            CHAMBER_EXIT: sorted([(51, 56), (55, 56), (73, 157), (54, 56), (52, 56)]),     # pre-control: armor NPC
            CELL_ENTRY: sorted([(51, 157), (53, 157), (55, 157), (56, 157), (56, 157)]),
            FIGHT_CELL: sorted([(55, 157), (55, 157), (52, 157)]),
            POST_CELL: sorted([(73, 157), (51, 157), (55, 157), (54, 157), (52, 157)])})
        before = gohan_by_table(self.before, set())
        self.assertEqual({t: [s for _, s in h] for t, h in before.items()},
                         {t: [56] * len(h) for t, h in got.items()})

    def test_every_addressed_gohan_has_a_spawn(self):      # actor lookup matches by set pointer
        objs = {self.rom[0x408CA0], self.rom[0x408F8C]}
        self.assertEqual(objs, {157})
        for table, hits in gohan_by_table(self.rom, set(self.moved)).items():
            actors = {s for n, s in hits if n != EXT73}
            spawned = {s for n, s in hits if n == 51} or (objs if table == FIGHT_CELL else set())
            self.assertEqual(len(actors), 1, hex(table))
            self.assertEqual(actors, spawned, hex(table))

    def test_set_157_header_matches_56(self):              # NPC slot size comes from the header
        table = u32(self.rom, 0x959C) - ROM_BASE
        h = lambda s: self.rom[u32(self.rom, table + 4 * (s - 7)) - ROM_BASE:][:8]   # noqa: E731
        self.assertEqual(h(157), h(56))

    def test_portrait_bytes_of_the_records(self):
        for rec in PRE_59:
            self.assertEqual(self.before[rec + 1:rec + 4].hex(), "00023b")
            self.assertEqual(self.rom[rec + 1:rec + 4].hex(), "000279")
        for rec in POST_59:
            self.assertEqual(self.rom[rec + 3], 59, hex(rec))

    def test_block_moves_with_id_121(self):
        old, new = self.notes["gohan_portraits"]["block"], self.notes["npc_gi"]["block"]
        self.assertEqual(u32(self.rom, 0xBE10), new + ROM_BASE)
        self.assertEqual(u32(self.rom, self.notes["npc_gi"]["pool"]), new + ROM_BASE)
        self.assertEqual(self.rom[new:new + 4 + 4 * 121], self.before[old:old + 4 + 4 * 121])
        self.assertEqual(u32(self.rom, new + 4 + 4 * 121), u32(self.rom, new + 4 + 4 * 59))
        self.assertEqual(self.rom[old:old + 4 + 4 * 121], self.before[old:old + 4 + 4 * 121])
        self.assertEqual([o for o in range(0, len(self.rom), 4) if u32(self.rom, o) == old + ROM_BASE], [])
        self.assertEqual(sorted(o for o in range(0, len(self.rom), 4) if u32(self.rom, o) == new + ROM_BASE),
                         sorted([0xBE10, self.notes["npc_gi"]["pool"]]))

    def test_diff_only_at_the_sites_and_new_data(self):
        sites = set()
        for off, pair in IN_PLACE.items():
            sites |= set(range(off, off + len(pair.split(":")[0]) // 2))
        for word, _ in MOVED.values():
            sites |= set(range(word, word + 4))
        sites |= {rec + 3 for rec in PRE_59} | set(range(0xBE10, 0xBE14))
        diff = {i for i in range(len(self.rom)) if self.rom[i] != self.before[i]}
        base = {i for i in diff if i < log2_build.BASE_SIZE}
        self.assertEqual(base, {i for i in sites if self.rom[i] != self.before[i]})
        pool, copy = self.notes["npc_gi"]["pool"], u32(self.rom, 0x42F0) - ROM_BASE
        low = sorted(i for i in diff - base if i < self.mark)
        self.assertTrue(set(low) <= {copy + 41} | set(range(pool, pool + 4)), [hex(i) for i in low[:8]])
        self.assertIn(copy + 41, low)

    def test_apply_fails_closed(self):
        from patches import npc_gi
        notes = built()["before_notes"]
        for off in (0x3DB627, 0x3E939A, 0x408F8C, 0x3EC2D0, 0x3DB933, 0xBE10, 0x3EC7E8):
            rom = bytearray(self.before)
            rom[off] ^= 0x01
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes.update({k: dict(v) for k, v in notes.items()})
            with self.assertRaises(ValueError, msg=hex(off)):
                npc_gi.apply(rom, alloc)
            self.assertEqual(bytes(rom), before, hex(off))
        with self.assertRaisesRegex(ValueError, "run them first"):
            npc_gi.apply(bytearray(self.before), Allocator(len(self.before), [(0xF00000, 0x100000)]))


class HookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_pre_control_records_show_the_armor(self):     # chamber exit: entry 2 since seq 3, still armor
        armor = frame(BASE_ROM, 59)
        for entry in ALL_ENTRIES:
            self.assertEqual(portrait(self.rom, PRE_ID, entry)[0], armor, entry)
        self.assertNotEqual(portrait(self.before, 59, 2)[0], armor)                 # r14: gi there

    def test_after_control_records_show_the_gi(self):
        gi = self.notes["gohan_portraits"]["frames"][119] + ROM_BASE
        for rec in POST_59:
            pid = self.rom[rec + 3]
            self.assertEqual(portrait(self.rom, pid, 2)[0], gi, hex(rec))
            self.assertEqual(portrait(self.rom, pid, 1)[0], frame(BASE_ROM, 59), hex(rec))

    def test_every_other_id_unchanged(self):                # the block move is invisible to ids 1-120
        for entry in (1, 2, 4, 22):
            for pid in list(range(1, 8)) + list(range(8, 121)):
                self.assertEqual(portrait(self.rom, pid, entry)[0], portrait(self.before, pid, entry)[0],
                                 (pid, entry))

    def test_dialog_box_treats_121_like_59(self):           # @0x0800B1E2: style switch on the record byte
        text = [t for _, t in listing(self.rom, 0x0800B246, 0x2F)]
        self.assertEqual(text, [t for _, t in listing(BASE_ROM, 0x0800B246, 0x2F)])
        consts = {int(t.split("#")[1], 16) for t in text if t.startswith("cmp r") and "#" in t}
        self.assertEqual(consts, {0x2, 0x5, 0x28, 0xE, 0x46, 0x31, 0x32, 0x35, 0x54, 0x56, 0x60})
        for pid in (59, PRE_ID):
            self.assertNotIn(pid, consts)
            self.assertFalse(26 <= pid < 26 + 14 or 2 <= pid <= 7)


if __name__ == "__main__":
    unittest.main()
