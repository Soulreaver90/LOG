r"""
test_chamber_spar.py - Tests for patches.chamber_spar (r37): Gohan (Demon Clothes) vs Goku sparring in map 6,70.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_chamber_spar.py -v
Builds build_list_dev.txt in memory: "before" = the list up to chamber_spar (r36), "rom" = before + chamber_spar (r37).
Scripts are decoded with test_cellgames_ssj's decoder (ops, ext_sequence); the loss picker runs in a small flag
evaluator here. Expected values are restated from docs\tasks\2026-10-24-chamber-proto\chamber-proto.md, chamber-fights-study-report.md
(sections 2 and 11) and the r36 bytes read in scripts\one-time\2026-10-24-chamber-proto\ (verify_r36.txt, decode_new.txt), never
imported from the patch module, except I placeholder LINES (one source for the text).
"""
import copy
import hashlib
import struct
import unittest
from pathlib import Path

import log2_build
from rom import log2_save
import log_paths
from patches import chamber_spar
from tests.test_cellgames_ssj import diff, ext_sequence, ops, u32, words_naming
from tests.test_superperfect_cell import STATS_NEW, STATS_R35, TYPE25_STATS, with_stats
from rom.webfoot_decompress import ROM_BASE

# ===== constants (study, brief, r36 reads) =====
R36_SHA1 = "eb4a1b4155eca4fa408bafe8c47949c67f85aa3d"
ENTRY_6_70 = 0x409368 + 56 * 175                       # map table entry 175
OLD_REGIONS, OLD_SPAWNS = 0x3FB80C, 0x3FB7A4           # 4 {cond, item} pairs; 6 item words
TIEN_NPC, TIEN_ENEMY, TIEN_REGION = 0x3FB6FC, 0x3FB784, 0x3FB7F8
ENEMY_TABLE, TYPE = 0x6D56AC, 95
TYPE95 = ENEMY_TABLE + 24 * TYPE
BOSS_DEATH, EVENT_RUNNER = 0x086FF3C4, 0x080106B3
GAME_OVER = 0x3B63B4
SEQ5, SEQ7, GOKU_LINE = 0x3B615C, 0x3B61A8, 0x3B627E
SCOUTER = 0x6F8E40
REVERSE_LITERAL = 0x42F0
WARP_6_3 = (6, 3, 1, 272, 336)                         # Tien's win warp
BUILD = log_paths.BUILDS
R37, R37_SPAR_GBA, R37_SPAR_SAV = BUILD / "log2_poc_r37.gba", BUILD / "log2_poc_r37_spar.gba", \
    BUILD / "log2_poc_r37_spar.sav"
R36_SAV = BUILD / "log2_poc_r36.sav"

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        i = names.index("chamber_spar")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["chamber_spar"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


def entry_lists(rom: bytes) -> tuple:
    """(region pairs [(cond, item)], spawn items) of map 6,70, as file offsets (cond 0 = always)."""
    e = ENTRY_6_70
    regions, spawns = u32(rom, e + 0x10) - ROM_BASE, u32(rom, e + 0x14) - ROM_BASE
    pairs = [(u32(rom, regions + 8 * k), u32(rom, regions + 8 * k + 4) - ROM_BASE) for k in range(rom[e + 3])]
    return [(c - ROM_BASE if c else 0, it) for c, it in pairs], [u32(rom, spawns + 4 * k) - ROM_BASE
                                                                 for k in range(rom[e + 4])]


def table_records(rom: bytes, table: int) -> list:
    """Record offsets of a scene table up to its first END word, checked to chain 0, 1, 2, ... by +0."""
    out = []
    while u32(rom, table + 4 * len(out)) >= 0x10000:
        out.append(u32(rom, table + 4 * len(out)) - ROM_BASE)
    return out


def pick(rom: bytes, rec: int, flags: set):
    """Run a flag-only type 0 record: the value left at `end` (the next index), or None (falls to +0)."""
    body = {at: (op, arg) for at, op, arg in ops(rom, rec + 3)}
    at, st = rec + 3, []
    while True:
        op, arg = body[at]
        nxt = min(a for a in body if a > at) if any(a > at for a in body) else None
        if op in (0, 1, 29):
            st += arg
        elif op == 2:
            n = st.pop()
            st.append(int(n in flags) if arg == 19 else int(n not in flags) if arg == 20 else None)
        elif op == 4:
            b, a = st.pop(), st.pop()
            st.append(int(a and b))
        elif op == 19:
            if not st.pop():
                at = arg
                continue
        elif op == 17:
            return st[-1] if len(st) == 1 else None
        else:
            raise AssertionError(f"op {op} at 0x{at:X} is not modelled")
        at = nxt


def cond_flags(rom: bytes, cond: int) -> list:
    """The (ext, flag) pairs of a condition script and its final op list, for `flag a and flag b ; end`."""
    return [(op, arg) for _, op, arg in ops(rom, cond)]


# ===== tests =====

class BaseTests(unittest.TestCase):
    def test_before_is_r36(self):
        before = with_stats(built()["before"], STATS_R35)       # r38 raised type 25's stats; r36 has the r35 values
        self.assertEqual(hashlib.sha1(before).hexdigest(), R36_SHA1)

    def test_build_list_has_chamber_spar_after_superperfect_cell(self):       # r39 appends bf_hud, bf_ki_pool
        names = built()["names"]
        i = names.index("chamber_spar")
        self.assertEqual(names[i - 1:i + 1], ["superperfect_cell", "chamber_spar"])


class EnemyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]

    def test_type_95_was_a_placeholder_and_is_goku(self):
        old, new = self.before[TYPE95:TYPE95 + 24], self.rom[TYPE95:TYPE95 + 24]
        self.assertEqual(struct.unpack("<3I3B2B3xI", old), (0, 5, 8, 1, 1, 1, 0x80, 0x80, BOSS_DEATH))
        self.assertEqual(struct.unpack("<3I3B2B3xI", new), (0, 3500, 98, 34, 36, 34, 0x80, 0x80, BOSS_DEATH))

    def test_ai_98_is_the_krillin_and_tien_sparring_ai(self):
        for t in (64, 98):
            self.assertEqual(u32(self.rom, ENEMY_TABLE + 24 * t + 8), 98)

    def test_type_95_is_used_only_by_the_new_spawn(self):
        for rom, want in ((self.before, 0), (self.rom, 1)):
            spawns = [o for o in range(0, len(rom) - 0x20, 4)
                      if u32(rom, o) == 0x0800E77F and u32(rom, o + 8) == TYPE]                 # shape A
            self.assertEqual(len(spawns), want)
            lo, hi = TYPE95 + ROM_BASE, TYPE95 + 24 + ROM_BASE
            words = memoryview(rom[:len(rom) & ~3]).cast("I")
            self.assertEqual([4 * k for k, w in enumerate(words) if lo <= w < hi], [])             # shape B
            self.assertEqual([e for e in range(128) if u32(rom, SCOUTER + 20 * e + 0x10) == TYPE], [])  # shape C
        self.assertEqual(spawns, [built()["notes"]["chamber_spar"]["enemy"]])

    def test_96_and_97_are_not_free(self):          # correction to the study: scouter entries name them
        self.assertEqual([e for e in range(128) if u32(self.rom, SCOUTER + 20 * e + 0x10) in (96, 97)], [107, 111])


class MapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]["chamber_spar"]
        cls.regions, cls.spawns = entry_lists(cls.rom)
        cls.old_regions, cls.old_spawns = entry_lists(cls.before)

    def test_entry_counts_and_lists(self):
        e = ENTRY_6_70
        self.assertEqual((self.before[e:e + 2], self.before[e + 3], self.before[e + 4]), (bytes([6, 70]), 4, 6))
        self.assertEqual((self.rom[e + 3], self.rom[e + 4], self.rom[e + 8]), (5, 8, 1))
        self.assertEqual((u32(self.before, e + 0x10), u32(self.before, e + 0x14)),
                         (OLD_REGIONS + ROM_BASE, OLD_SPAWNS + ROM_BASE))
        self.assertEqual(self.regions[:4], self.old_regions)
        self.assertEqual(self.spawns[:6], self.old_spawns)
        self.assertEqual(self.rom[OLD_REGIONS:OLD_REGIONS + 32], self.before[OLD_REGIONS:OLD_REGIONS + 32])
        self.assertEqual(self.rom[OLD_SPAWNS:OLD_SPAWNS + 24], self.before[OLD_SPAWNS:OLD_SPAWNS + 24])

    def test_only_entry_175_named_the_old_lists(self):
        for addr, field in ((OLD_REGIONS, 0x10), (OLD_SPAWNS, 0x14)):
            self.assertEqual(words_naming(self.before, addr + ROM_BASE), [ENTRY_6_70 + field])
            self.assertEqual(words_naming(self.rom, addr + ROM_BASE), [])
        self.assertEqual(words_naming(self.rom, self.n["regions"] + ROM_BASE), [ENTRY_6_70 + 0x10])
        self.assertEqual(words_naming(self.rom, self.n["spawns"] + ROM_BASE), [ENTRY_6_70 + 0x14])

    def test_new_items_are_tiens_with_goku(self):
        npc, enemy = self.spawns[6], self.spawns[7]
        cond, region = self.regions[4]
        want_npc = bytearray(self.rom[TIEN_NPC:TIEN_NPC + 0x18])
        want_npc[4:8], want_npc[0xC:0x10] = struct.pack("<I", cond + ROM_BASE), struct.pack("<I", 60)
        self.assertEqual(self.rom[npc:npc + 0x18], bytes(want_npc))
        want_enemy = bytearray(self.rom[TIEN_ENEMY:TIEN_ENEMY + 0x20])
        want_enemy[8:0xC], want_enemy[0x10:0x14] = struct.pack("<I", TYPE), struct.pack("<I", 60)
        want_enemy[0x14:0x18] = self.rom[enemy + 0x14:enemy + 0x18]
        self.assertEqual(self.rom[enemy:enemy + 0x20], bytes(want_enemy))
        self.assertEqual(u32(self.rom, enemy + 4), 1)                           # never built at map load
        self.assertEqual(self.rom[region:region + 0x10], self.rom[TIEN_REGION:TIEN_REGION + 0x10])  # walk-in, rect
        self.assertEqual(u32(self.rom, region + 0x10) - ROM_BASE, self.n["pre_table"])

    def test_npc_and_region_condition_is_flag_214_and_flag_195(self):
        cond = self.regions[4][0]
        self.assertEqual(u32(self.rom, self.spawns[6] + 4) - ROM_BASE, cond)
        self.assertEqual(cond_flags(self.rom, cond), [(0, [214]), (2, 19), (0, [195]), (2, 19), (4, None),
                                                      (17, None)])
        for flags, want in (({214, 195}, 1), ({214}, 0), ({195}, 0), (set(), 0)):
            self.assertEqual(pick(self.rom, cond - 3, flags), want)             # cond has no 3-byte header
        for c, _ in self.old_regions[1:]:                                      # the vanilla partners are off then
            self.assertEqual(pick(self.rom, c - 3, {212, 213, 214, 195}), 0)


class SceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.n = b["rom"], b["notes"]["chamber_spar"]
        cls.pre = table_records(cls.rom, cls.n["pre_table"])
        cls.win = table_records(cls.rom, cls.n["win_table"])

    def test_pre_fight_scene(self):
        r = self.rom
        self.assertEqual(len(self.pre), 4)
        self.assertEqual(u32(r, self.n["pre_table"] + 16), 0)                    # END, resume 0
        self.assertEqual([r[p] for p in self.pre], [1, 2, 3, 4])
        self.assertEqual(ext_sequence(r, self.pre[0]), [(46, (50,)), (40, (30,)), (73, (0, 53)), (70, (0,)),
                                                         (41, (30,))])
        self.assertEqual([r[p + 2:p + 4] for p in self.pre[1:3]], [bytes([1, 63]), bytes([1, 56])])
        self.assertEqual(ext_sequence(r, self.pre[3]), [(104, (60, 7)), (85, (60,))])

    def test_ext_104_builds_goku_from_the_npc(self):
        _, spawns = entry_lists(self.rom)
        npc, enemy = spawns[6], spawns[7]                                       # item 7 is ext 104's n
        self.assertEqual((u32(self.rom, npc + 0xC), u32(self.rom, enemy + 0x10), u32(self.rom, enemy + 8)),
                         (60, 60, TYPE))
        self.assertEqual(u32(self.rom, enemy) & ~1, 0x0800E77E)

    def test_win_event(self):
        r = self.rom
        _, spawns = entry_lists(r)
        event = u32(r, spawns[7] + 0x14) - ROM_BASE
        self.assertEqual((u32(r, event), u32(r, event + 4) - ROM_BASE), (EVENT_RUNNER, self.n["win_table"]))
        self.assertEqual([r[p] for p in self.win], [1, 2, 3, 4])
        self.assertEqual(u32(r, self.n["win_table"] + 16), 0)
        self.assertEqual(ext_sequence(r, self.win[0]), [(69, (30,)), (57, (60, 4)), (88, ()), (46, (50,))])
        self.assertEqual([r[p + 2:p + 4] for p in self.win[1:3]], [bytes([1, 63]), bytes([1, 56])])
        self.assertEqual(ext_sequence(r, self.win[3]), [(69, (30,)), (40, (120,)), (109, (0, 5000)),
                                                         (110, (0, 5000)), (73, (0, 157)), (38, WARP_6_3)])

    def test_win_is_tiens_with_goku_and_no_flag(self):
        r = self.rom
        tien_head, tien_warp = 0x3D2F54, 0x3D2FE0
        self.assertEqual(ext_sequence(r, tien_head), [(69, (30,)), (57, (121, 4)), (88, ()), (46, (50,))])
        self.assertEqual(ext_sequence(r, tien_warp), [(69, (30,)), (40, (120,)), (38, WARP_6_3), (27, (214,))])
        for rec in self.pre + self.win + [self.n["seq5"], self.n["loss"]]:
            if r[rec + 2] == 0:
                self.assertNotIn(27, [n for n, _ in ext_sequence(r, rec)])      # no SET: the fight repeats

    def test_placeholder_lines(self):
        r = self.rom
        texts = [r[p + 4:r.index(b"\0", p + 4)].decode("ascii") for p in self.pre[1:3] + self.win[1:3]]
        self.assertEqual(texts, [t for k in ("pre", "win") for _, t in chamber_spar.LINES[k]])
        for t in texts:
            self.assertTrue(t.startswith(("GOKU: ", "GOHAN: ")) and len(t) <= 60, t)
            self.assertFalse(set(t.encode("ascii")) & {0x0A, 0x0B})

    def test_portraits_and_appearance_sets_exist(self):
        rev = u32(self.rom, REVERSE_LITERAL) - ROM_BASE
        self.assertEqual((self.rom[rev + 1], self.rom[rev + 20 * 2 + 1]), (53, 157))   # ext 73 needs an entry
        line = self.rom[GOKU_LINE:GOKU_LINE + 4]
        self.assertEqual(line, bytes([15, 0, 1, 63]))                          # the vanilla Goku portrait id


class LossTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]["chamber_spar"]

    def test_only_words_4_and_15_change(self):
        old = [u32(self.before, GAME_OVER + 4 * k) for k in range(24)]
        new = [u32(self.rom, GAME_OVER + 4 * k) for k in range(24)]
        self.assertEqual([k for k in range(24) if old[k] != new[k]], [4, 15])
        self.assertEqual((old[4], old[14], old[15], old[3]), (SEQ5 + ROM_BASE, GOKU_LINE + ROM_BASE, 14, 0))
        self.assertEqual((new[4] - ROM_BASE, new[15] - ROM_BASE), (self.n["seq5"], self.n["loss"]))
        self.assertEqual(words_naming(self.rom, GAME_OVER + ROM_BASE), [0x8870])

    def test_picker_matches_vanilla_except_goku(self):
        for bits in range(16):
            flags = {f for i, f in enumerate((212, 213, 214, 195)) if bits >> i & 1}
            old, new = pick(self.before, SEQ5, flags), pick(self.rom, self.n["seq5"], flags)
            with self.subTest(flags=sorted(flags)):
                self.assertEqual(new, 14 if {214, 195} <= flags else old)
        self.assertEqual((pick(self.before, SEQ5, set()), pick(self.before, SEQ5, {212}),
                          pick(self.before, SEQ5, {212, 213})), (None, 19, 16))   # Yamcha (+0 = 5), Krillin, Tien
        self.assertEqual(self.rom[self.n["seq5"]], 5)

    def test_goku_line_then_the_loss_warp(self):
        r = self.rom
        self.assertEqual(r[GOKU_LINE], 15)                                      # line -> word 15 -> loss warp
        loss = self.n["loss"]
        self.assertEqual(r[loss:loss + 3], bytes([3, 0, 0]))                    # next index 3 = END
        yamcha = ext_sequence(self.before, SEQ7)
        self.assertEqual(yamcha, [(69, (60,)), (40, (120,)), (14, ()), (38, (2, 6, 3, 1, 264, 336))])  # 2: the div
        self.assertEqual(ext_sequence(r, loss), yamcha[:2] + [(73, (0, 157))] + yamcha[2:])
        tail = [(op, arg) for _, op, arg in ops(r, loss + 3)]
        self.assertEqual([x for x in tail if x[0] in (10, 3)], [(10, None), (3, 13)])   # div ; set var13

    def test_every_path_restores_the_gi(self):
        r = self.rom
        pre = table_records(r, self.n["pre_table"])
        win = table_records(r, self.n["win_table"])
        self.assertIn((73, (0, 53)), ext_sequence(r, pre[0]))
        self.assertIn((73, (0, 157)), ext_sequence(r, win[-1]))
        self.assertIn((73, (0, 157)), ext_sequence(r, self.n["loss"]))


class PlacementTests(unittest.TestCase):
    def test_new_data_follows_r36(self):
        b = built()
        n = len(b["alloc_before"].used())
        self.assertEqual(b["used"][:n], b["alloc_before"].used())
        end = max(a + s for a, s in b["alloc_before"].used())
        new = b["used"][n:]
        self.assertTrue(new and all(a >= end and a + s <= log2_build.ART_REGION[0] for a, s in new))
        self.assertTrue(all(set(b["before"][a:a + s]) == {0xFF} for a, s in new))


def named_sites(notes: dict, used_new: list) -> list:
    e = ENTRY_6_70
    return ([(TYPE95 + 4, 11), (e + 3, 2), (e + 0x10, 8), (GAME_OVER + 16, 4), (GAME_OVER + 60, 4)]
            + list(used_new))


class DiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom = b["before"], b["rom"]
        cls.sites = named_sites(b["notes"]["chamber_spar"], b["used"][len(b["alloc_before"].used()):])

    def assert_only_sites(self, a: bytes, b: bytes) -> None:
        changed = diff(a, b)
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + n for s, n in self.sites)], [])
        for s, n in self.sites:
            self.assertTrue(any(s <= i < s + n for i in changed), hex(s))

    def test_only_named_sites_change(self):
        self.assert_only_sites(self.before, self.rom)

    def test_r37_file_equals_the_build_and_differs_from_r36_at_the_sites(self):
        r36 = BUILD / "log2_poc_r36.gba"
        if not (R37.exists() and r36.exists()):
            self.skipTest("r36 or r37 not built")
        r37_rom = with_stats(self.rom, STATS_R35)               # r38 raised type 25's stats; r37 has the r35 values
        self.assertEqual(R37.read_bytes(), r37_rom)
        self.assert_only_sites(r36.read_bytes(), r37_rom)

    def test_r38_file_equals_the_build_and_differs_from_r37_in_type_25_stats_only(self):
        r38 = BUILD / "log2_poc_r38.gba"
        if not (R37.exists() and r38.exists()):
            self.skipTest("r37 or r38 not built")
        self.assertEqual(r38.read_bytes(), self.rom)
        off = TYPE25_STATS[0]
        self.assertEqual([i - off for i in diff(R37.read_bytes(), self.rom)], [4, 5, 0xC, 0xD, 0xE])
        self.assertEqual(self.rom[off + 4:off + 8], STATS_NEW[0].to_bytes(4, "little"))
        self.assertEqual(self.rom[off + 0xC:off + 0xF], bytes(STATS_NEW[1:]))


class FailClosedTests(unittest.TestCase):
    def fresh(self) -> tuple:
        b = built()
        return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])

    def assert_refused(self, rom: bytearray, alloc) -> None:
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            chamber_spar.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_each_checked_site_refuses(self):
        e = ENTRY_6_70
        for off in (0xEBD8, 0x5ADC, e + 1, e + 3, e + 4, e + 8, e + 0x10, e + 0x14, OLD_SPAWNS + 8,
                    OLD_SPAWNS + 20, OLD_REGIONS + 28, TIEN_NPC + 0xC, TIEN_ENEMY + 8, TIEN_REGION + 0x10,
                    0x3FB77C, TYPE95 + 4, TYPE95 + 8, TYPE95 + 0xC, 0x8870, GAME_OVER + 12, GAME_OVER + 16,
                    GAME_OVER + 56, GAME_OVER + 60, GOKU_LINE + 3, SEQ5 + 5, SEQ7 + 0x15, 0x3D2F5C, 0x3D2FEC):
            with self.subTest(off=hex(off)):
                rom, alloc = self.fresh()
                rom[off] ^= 0x01
                self.assert_refused(rom, alloc)

    def test_second_run_and_missing_notes_refuse(self):
        rom, alloc = self.fresh()
        chamber_spar.apply(rom, alloc)
        self.assert_refused(rom, alloc)
        rom, alloc = self.fresh()
        del alloc.notes["superperfect_cell"]
        self.assert_refused(rom, alloc)


class SaveTests(unittest.TestCase):
    """My test save: r36.sav slot 1 with flags 212-214 and the player below the 6,70 door on map 6,3."""

    def test_spar_rom_is_a_copy_and_the_save_differs_in_slot_1_only(self):
        if not (R37.exists() and R37_SPAR_GBA.exists() and R37_SPAR_SAV.exists() and R36_SAV.exists()):
            self.skipTest("r37 files not made")
        self.assertEqual(R37_SPAR_GBA.read_bytes(), R37.read_bytes())
        old, new = log2_save.read_ram(R36_SAV.read_bytes()), log2_save.read_ram(R37_SPAR_SAV.read_bytes())
        s1 = log2_save.slot_range(0)
        self.assertEqual(old[:s1.start] + old[s1.stop:], new[:s1.start] + new[s1.stop:])
        a, b = old[s1], new[s1]
        data = log2_save.SLOT_DATA
        self.assertEqual(struct.unpack_from("<I", b, data)[0], log2_save.adler32(bytes(b[:data])))
        self.assertEqual((b[log2_save.O_ZONE], b[log2_save.O_AREA], b[log2_save.O_VAR]), (6, 3, 1))
        self.assertEqual(struct.unpack_from("<hh", b, log2_save.O_POS), (272, 336))
        story = log2_save.O_STORY
        for f in (212, 213, 214):
            self.assertEqual((log2_save.bit(a, story, f), log2_save.bit(b, story, f)), (0, 1))
        self.assertEqual((log2_save.bit(b, story, 195), b[log2_save.O_LEADER]), (1, 0))
        changed = [i for i in range(data) if a[i] != b[i]]
        allowed = set(range(log2_save.O_ZONE, log2_save.O_VAR + 1)) | {story + 26} | set(
            range(log2_save.O_POS, log2_save.O_POS + 4))
        self.assertEqual([i for i in changed if i not in allowed], [])


if __name__ == "__main__":
    unittest.main()
