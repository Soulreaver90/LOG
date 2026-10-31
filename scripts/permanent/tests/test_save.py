r"""
test_save.py - Tests for log2_save.py: the build sets, slot contents, journal evaluation, write guards.

Run (any folder):
  py -3 -I -m unittest discover -s <LOG>\scripts\permanent -p "test_*save*.py"
Reads my .sav and the base ROM under data\ (read only) and test-data\saves\log2_lv40_postcell.sav.
Every write goes to a temp folder.
"""
import hashlib
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from rom import log2_save as ls
import log_paths

ROOT = Path(__file__).resolve().parents[3]
BASE_SAV = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).sav"
BASE_ROM = (ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba").read_bytes()
LOADED_SAV = log_paths.SAVES / "log2_lv40_postcell.sav"   # the file I loaded (r12)
CELLGAMES_SAV = log_paths.SAVES / "log2_lv40_cellgames.sav"  # SHA-1 c755acf0..., slots 1-2 must stay
POSTCELL_SHA1 = "3ecf1e40b2267cc2cb63c3f64bafe6a010afac0d"         # build output recorded in the bible
LOADED_SLOT1_CHECK = 0x31C65A32                                     # slot 1 Adler-32 in the file I loaded
GOKU, HERCULE = 4, 5


def _slot(ram: bytearray, n: int) -> bytes:
    return bytes(ram[ls.slot_range(n)])


def _rec(slot: bytes, c: int) -> bytes:
    return slot[ls.O_CHARS + c * ls.CHAR_SIZE:ls.O_CHARS + (c + 1) * ls.CHAR_SIZE]


def _flags(slot: bytes) -> set:
    return {f for f in range(ls.STORY_BITS) if ls.bit(slot, ls.O_STORY, f)}


def _rom(addr: int, size: int) -> bytes:
    return BASE_ROM[addr - ls.ROM_BASE:addr - ls.ROM_BASE + size]


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        cls.post_path, cls.cg_path = tmp / "postcell.sav", tmp / "cellgames.sav"
        ls.build(BASE_SAV, cls.post_path, "postcell")
        ls.build(BASE_SAV, cls.cg_path)
        cls.post = ls.read_ram(cls.post_path.read_bytes())
        cls.cg = ls.read_ram(cls.cg_path.read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_postcell_set_is_byte_for_byte_the_first_build(self):
        self.assertEqual(hashlib.sha1(self.post_path.read_bytes()).hexdigest(), POSTCELL_SHA1)

    def test_default_set_is_cellgames(self):
        self.assertEqual(ls.DEFAULT_SET, "cellgames")

    def test_every_slot_and_options_check(self):
        for ram in (self.post, self.cg):
            self.assertEqual(struct.unpack_from("<I", ram, 4)[0], (ls.adler32(ls.OPT_DEFAULT) + ls.OPT_MAGIC) & 0xFFFFFFFF)
            for n in range(ls.SLOT_COUNT):
                s = _slot(ram, n)
                self.assertEqual(struct.unpack_from("<I", s, ls.SLOT_DATA)[0], zlib.adler32(s[:ls.SLOT_DATA]))
                self.assertEqual(s[ls.O_FLAGS] & 1, 1)

    def test_bytes_the_game_never_writes_come_from_the_base(self):
        base = ls.read_ram(BASE_SAV.read_bytes())
        self.assertEqual(self.cg[0x008:0x010], base[0x008:0x010])
        self.assertEqual(self.cg[0x448:], base[0x448:])

    def test_write_refuses_an_existing_file(self):
        with self.assertRaises(SystemExit):
            ls.build(BASE_SAV, self.cg_path)

    def test_write_refuses_a_data_folder(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(SystemExit):
                ls.write(Path(t) / "data" / "x.sav", bytearray(ls.SAV_SIZE))


class CellGamesSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name) / "cellgames.sav"
        ls.build(BASE_SAV, out)
        ram = ls.read_ram(out.read_bytes())
        cls.s1, cls.s2, cls.s3 = (_slot(ram, n) for n in range(3))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_slot1_is_the_slot_the_owner_loaded(self):
        self.assertEqual(struct.unpack_from("<I", self.s1, ls.SLOT_DATA)[0], LOADED_SLOT1_CHECK)
        if LOADED_SAV.exists():                                  # scratch: may be deleted
            self.assertEqual(self.s1, _slot(ls.read_ram(LOADED_SAV.read_bytes()), 0))

    def test_slot2_is_roshis_island_at_the_world_map_arrival(self):
        self.assertEqual((self.s2[ls.O_ZONE], self.s2[ls.O_AREA], self.s2[ls.O_VAR]), (11, 1, 1))
        self.assertEqual(struct.unpack_from("<hh", self.s2, ls.O_POS), (416, 160))
        self.assertEqual(_rom(0x083FBC84, 12), bytes.fromhex("1d0516020286408240022611"))  # push list ; ext 38 ; end
        self.assertEqual(ls.push_list(BASE_ROM, 0x083FBC84), [11, 1, 1, 416, 160])

    def test_slot2_keeps_the_post_cell_story(self):
        self.assertEqual(self.s2[:ls.O_ZONE], self.s1[:ls.O_ZONE])
        self.assertEqual(self.s2[ls.O_VAR + 1:ls.O_POS], self.s1[ls.O_VAR + 1:ls.O_POS])

    def test_slot3_flags_are_post_cell_minus_192_to_195(self):
        flags = _flags(self.s3)
        self.assertIn(191, flags)
        self.assertFalse(flags & {192, 193, 194, 195, 196})
        self.assertEqual(flags, _flags(self.s1) - {192, 193, 194, 195})

    def test_slot3_journal_shows_enter_the_cell_games_active(self):
        states = dict(ls.journal(self.s3, BASE_ROM))
        self.assertEqual(states["Enter the Cell Games"], "active")
        self.assertEqual(states["Return the Dragon Balls to Dende on the Lookout"], "finished")
        self.assertEqual(states["Talk to Dende on the Lookout"], "hidden")

    def test_post_cell_journal_shows_talk_to_dende_active(self):
        states = dict(ls.journal(self.s1, BASE_ROM))
        self.assertEqual(states["Talk to Dende on the Lookout"], "active")
        self.assertEqual(states["Enter the Cell Games"], "finished")

    def test_slot3_is_the_lookout_arrival(self):
        self.assertEqual((self.s3[ls.O_ZONE], self.s3[ls.O_AREA], self.s3[ls.O_VAR]), (9, 1, 1))
        self.assertEqual(struct.unpack_from("<hh", self.s3, ls.O_POS), (768, 832))
        self.assertEqual(ls.push_list(BASE_ROM, 0x083FBBFC), [9, 1, 1, 768, 832])

    def test_slot3_goku_leads_at_level_40_for_the_arena_barrier(self):
        self.assertEqual(self.s3[ls.O_LEADER], GOKU)
        self.assertGreaterEqual(ls.level_of(struct.unpack_from("<I", _rec(self.s3, GOKU), 0x10)[0]), 40)

    def test_slot3_hercule_has_not_joined(self):
        self.assertEqual(_rec(self.s3, HERCULE), _rom(0x081D9548 + HERCULE * 28, 28))
        for c in range(6):
            in_party = struct.unpack_from("<I", _rec(self.s3, c), 0x14)[0] & 1
            self.assertEqual(in_party, int(c != HERCULE), ls.CHAR_NAMES[c])

    def test_slot3_outfits_and_items(self):
        self.assertEqual([_rec(self.s3, c)[8] for c in range(6)], ls.POSTCELL_APPEARANCE)
        self.assertEqual(ls.APPEARANCE_SET[_rec(self.s3, 0)[8]], 56)
        items = {i: self.s3[ls.O_ITEMS + i] for i in range(ls.ITEM_COUNT) if self.s3[ls.O_ITEMS + i]}
        self.assertEqual(items, {22: 1, 45: 1})


def _literal_sets(flag: int) -> list:
    """GBA addresses of 'push flag ; call ext 27' (op 0 or op 1 push) in the script region."""
    out, enc = [], bytes([0, flag]) if flag < 256 else None
    lo, hi = 0x3B0000, 0x409368
    pat1 = bytes([1]) + bytes([0x80 | (flag * 2) >> 7, (flag * 2) & 0x7F]) + bytes([2, 27])
    for pat in ([enc + bytes([2, 27])] if enc else []) + [pat1]:
        i = BASE_ROM.find(pat, lo, hi)
        while i >= 0:
            out.append(ls.ROM_BASE + i + len(pat) - 2)
            i = BASE_ROM.find(pat, i + 1, hi)
    return sorted(out)


class CellGames2SetTests(unittest.TestCase):
    """save-slot3 study: slot 3 = flag 191 just set; slots 1 and 2 unchanged."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls.tmp.name)
        ls.build(BASE_SAV, tmp / "cg.sav", "cellgames")
        ls.build(BASE_SAV, tmp / "cg2.sav", "cellgames2")
        ls.build(BASE_SAV, tmp / "arena.sav", "cellgames2_arena")
        cls.cg = ls.read_ram((tmp / "cg.sav").read_bytes())
        cls.cg2 = ls.read_ram((tmp / "cg2.sav").read_bytes())
        cls.arena = ls.read_ram((tmp / "arena.sav").read_bytes())
        cls.s3 = _slot(cls.cg2, 2)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_slots_1_and_2_are_byte_for_byte_the_cellgames_save(self):
        for n in (0, 1):
            self.assertEqual(_slot(self.cg2, n), _slot(self.cg, n))
        if CELLGAMES_SAV.exists():                                   # scratch: may be deleted
            disk = ls.read_ram(CELLGAMES_SAV.read_bytes())
            for n in (0, 1):
                self.assertEqual(_slot(self.cg2, n), _slot(disk, n))
        self.assertEqual(self.cg2[:ls.SLOT_OFF], self.cg[:ls.SLOT_OFF])
        self.assertEqual(self.cg2[ls.slot_range(2).stop:], self.cg[ls.slot_range(2).stop:])

    def test_old_presets_unchanged(self):
        self.assertEqual(ls.DEFAULT_SET, "cellgames")
        self.assertEqual(ls.PRESET_SETS["cellgames"][2][1], "cellgames")
        self.assertNotIn("cellgames", ls.UNVISITED)

    def test_slot3_differs_from_the_old_slot3_only_in_the_arena_visited_bits(self):
        old, new = _slot(self.cg, 2), self.s3
        diff = [i for i in range(ls.SLOT_DATA) if old[i] != new[i]]
        self.assertEqual(diff, sorted({ls.O_VISITED + (b >> 3) for b in ls.ARENA_VISITED}))
        for v in range(ls.VISITED_BITS):
            self.assertEqual(ls.bit(new, ls.O_VISITED, v), int(v not in ls.ARENA_VISITED), v)

    def test_arena_visited_bits_are_maps_14_1_to_14_3(self):
        u32 = lambda a: struct.unpack_from("<I", BASE_ROM, a - ls.ROM_BASE)[0]   # noqa: E731
        found = {}
        for i in range(u32(0x086F6D8C)):
            e = u32(u32(0x086F6D8C + 4) + 4 * i)
            for j in range(u32(e + 0x14)):
                p = u32(e + 0x18 + 4 * j) - ls.ROM_BASE
                found[struct.unpack_from("<H", BASE_ROM, p + 2)[0]] = (BASE_ROM[p], BASE_ROM[p + 1])
        self.assertEqual([found[b] for b in ls.ARENA_VISITED], [(14, 1), (14, 2), (14, 3)])

    def test_slot3_flags_191_set_192_to_196_clear(self):
        flags = _flags(self.s3)
        self.assertIn(191, flags)
        self.assertFalse(flags & set(range(192, 197)))
        self.assertEqual(flags, _flags(_slot(self.cg, 2)))

    def test_late_flags_have_one_literal_set_site_each(self):
        expect = {191: [0x083DD32D], 192: [0x083E93E2], 193: [0x083E8D94], 194: [0x083E9BBD], 195: [0x083EC6A4]}
        for f, sites in expect.items():
            self.assertEqual(_literal_sets(f), sites, f)

    def test_dende_reads_good_luck_in_the_cell_games(self):
        # Talk table 0x083DD380 (map 9,1 object 0x08403F3C) entry 0: 'push 191 ; flag ; jz ; push 9 ; end'.
        self.assertEqual(_rom(0x083DD1AC + 3, 9), bytes.fromhex("00bf02131303000911"))
        entry9 = struct.unpack_from("<I", BASE_ROM, 0x3DD380 + 9 * 4)[0]
        self.assertEqual(entry9, 0x083DD34C)
        self.assertIn(b"DENDE: Good luck in the Cell Games", _rom(entry9, 0x40))
        self.assertTrue(ls.bit(self.s3, ls.O_STORY, 191))

    def test_journal_enter_the_cell_games_active(self):
        states = dict(ls.journal(self.s3, BASE_ROM))
        self.assertEqual(states["Enter the Cell Games"], "active")
        self.assertEqual(states["Talk to Dende on the Lookout"], "hidden")

    def test_slot3_party_outfits_items_leader_place(self):
        old = _slot(self.cg, 2)
        self.assertEqual(self.s3[ls.O_CHARS:ls.O_STORY], old[ls.O_CHARS:ls.O_STORY])
        self.assertEqual(self.s3[ls.O_ITEMS:ls.O_POS], old[ls.O_ITEMS:ls.O_POS])
        self.assertEqual(self.s3[ls.O_LEADER], GOKU)
        self.assertEqual((self.s3[ls.O_ZONE], self.s3[ls.O_AREA], self.s3[ls.O_VAR]), (9, 1, 1))
        self.assertEqual(struct.unpack_from("<hh", self.s3, ls.O_POS), (768, 832))

    def test_slot_load_reads_the_ram_shadow_not_the_chip(self):
        # 0x08003F9C copies a slot with 0x08021526: DMA from [0x03003898] (= 0x0203E000, filled at boot) + offset.
        # So a save state taken after boot carries its own slot image.
        self.assertEqual(_rom(0x08003FBE, 4), bytes.fromhex("1df0b2fa"))
        self.assertEqual(_rom(0x08021526, 4), bytes.fromhex("1c480068"))
        pool = (0x08021526 + 4 + 0x1C * 4) & ~3                     # ldr r0,[pc,#0x70]
        self.assertEqual(struct.unpack_from("<I", BASE_ROM, pool - ls.ROM_BASE)[0], 0x03003898)

    def test_arena_option_is_the_world_map_landing(self):
        a3 = _slot(self.arena, 2)
        self.assertEqual(ls.push_list(BASE_ROM, 0x083FBDC4), [14, 1, 1, 264, 304])
        self.assertEqual((a3[ls.O_ZONE], a3[ls.O_AREA], a3[ls.O_VAR]), (14, 1, 1))
        self.assertEqual(struct.unpack_from("<hh", a3, ls.O_POS), (264, 304))
        self.assertEqual(a3[ls.O_LEADER], GOKU)
        self.assertEqual(a3[ls.O_VISITED:ls.O_SCOUTER], self.s3[ls.O_VISITED:ls.O_SCOUTER])


class JournalEvaluatorTests(unittest.TestCase):
    def test_quest_table_has_43_entries_with_text(self):
        names = [n for n, _ in ls.journal(bytes(ls.SLOT_SIZE), BASE_ROM)]
        self.assertEqual(len(names), 43)
        self.assertEqual(names[1], "Enter the Cell Games")

    def test_unknown_op_raises(self):
        rom = bytearray(BASE_ROM[:0x100])
        rom[0x80] = 6                                     # neg: not part of the quest subset
        with self.assertRaises(ValueError):
            ls.run_cond(bytes(rom), ls.ROM_BASE + 0x80, bytes(ls.SLOT_SIZE))

    def test_empty_slot_shows_no_quest(self):
        self.assertTrue(all(st == "hidden" for _, st in ls.journal(bytes(ls.SLOT_SIZE), BASE_ROM)[:28]))


if __name__ == "__main__":
    unittest.main()
