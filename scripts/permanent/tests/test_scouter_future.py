r"""
test_scouter_future.py - The three future enemies are scannable, and nothing else in the database moved.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_scouter_future.py -v
Builds build_list_trial_plateau.txt in memory once, and also the list WITHOUT this module, so every
claim is read as a difference between the two ROMs rather than out of the module's own constants.
What it cannot read: whether the text box renders a 587-character bio on real hardware, and whether
anything the game writes also uses save byte 0x12A. Both are stated in the report, not tested here.
"""
import struct
import unittest

import log2_build
from patches import scouter_future as sf

ROM_BASE = 0x08000000
LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_plateau.txt"
ENEMY_TABLE, ENEMY_ENTRY = 0x6D56AC, 24


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def _cstr(rom, off):
    return bytes(rom[off:bytes(rom).index(b"\0", off)]).decode("ascii")


class ScouterFutureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = log2_build.read_build_list(LIST)
        cls.rom, cls.alloc = log2_build.assemble(log2_build.BASE, names)
        cls.notes = cls.alloc.notes["scouter_future"]
        cls.base = bytearray(log2_build.BASE.read_bytes())
        cls.without, cls.alloc_without = log2_build.assemble(
            log2_build.BASE, [n for n in names if n != "scouter_future"])

    # ----- the table -----

    def test_the_table_moved_and_every_literal_came_with_it(self):
        table = self.notes["table"]
        self.assertNotEqual(table, sf.TABLE)
        for lit in sf.BASE_LITERALS:
            self.assertEqual(_u32(self.rom, lit), table + ROM_BASE, f"literal rom:0x{lit:X}")

    def test_the_128_live_entries_came_across_byte_for_byte(self):
        """The copy is of the LIVE table, not the base one. superperfect_cell already rewrites entry
        19 in place (its own SCOUTER_19 constant), so a copy of the base bytes would silently undo
        Super Perfect Cell's scouter row. The build WITHOUT this module gives the right answer,
        because every module that writes the table runs before this one."""
        want = bytes(self.without[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES])
        got = bytes(self.rom[self.notes["table"]:self.notes["table"] + sf.ENTRY * sf.ENTRIES])
        self.assertEqual(got, want)
        self.assertEqual(bytes(self.rom[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES]), want,
                         "and the table at its old address is left exactly as it stood")
        self.assertNotEqual(want, bytes(self.base[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES]),
                            "the live table really does differ from the base one")

    def test_the_string_pool_is_untouched(self):
        end = sf.POOL + 0x2000
        self.assertEqual(bytes(self.rom[sf.POOL:end]), bytes(self.base[sf.POOL:end]))

    def test_nothing_still_points_into_the_old_table(self):
        """A pointer left behind would read a vanilla entry that the game no longer indexes."""
        lo, hi = sf.TABLE + ROM_BASE, sf.TABLE + sf.ENTRY * sf.ENTRIES + ROM_BASE
        words = memoryview(bytes(self.rom)).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(words) if lo <= w < hi], [])

    # ----- the one code byte -----

    def test_the_only_base_rom_bytes_it_writes_are_the_literals_and_one_bound_byte(self):
        """Read out of its own declared sites, not out of a ROM diff: removing the module moves every
        later allocation, so a diff of the two builds says nothing about this module."""
        base_writes = sorted((at, n, what) for at, n, what in self.notes["sites"] if at < 0x800000)
        self.assertEqual([(at, n) for at, n, _w in base_writes],
                         sorted([(lit, 4) for lit in sf.BASE_LITERALS]
                                + [(sf.TYPE_MATCH_BOUND, 1)]))
        self.assertEqual(self.rom[sf.TYPE_MATCH_BOUND], sf.NEW_BOUND)
        self.assertEqual(self.rom[sf.TYPE_MATCH_BOUND + 1], sf.BOUND_SITES[sf.TYPE_MATCH_BOUND][0][1],
                         "the CMP itself is unchanged: only its immediate moved")
        self.assertEqual(sf.NEW_BOUND, sf.ENTRIES + len(self.notes["new"]))

    def test_the_other_two_bounds_are_still_128(self):
        """Measured, not assumed. The set matcher cannot reach a new entry, because our three sets
        are already carried by vanilla entries. The database LIST menu object is sized for exactly
        128 entries, so raising its bound would corrupt it; see LIST_BOUND in the module."""
        for at in (sf.SET_MATCH_BOUND, sf.LIST_BOUND):
            self.assertEqual(self.rom[at], sf.OLD_BOUND, f"rom:0x{at:X}")
        self.assertEqual(self.notes["list_slots"], sf.ENTRIES)

    # ----- the three new entries -----

    def test_each_new_entry_names_its_own_weakened_type(self):
        """This is the whole defect: an enemy scans by TYPE ENTRY POINTER (bible B2297), so an entry
        whose +0x10 does not name the live type cannot be found at all."""
        types = {}
        for key, sub in (("future_androids", "types"), ("ending_fight", "cell_type")):
            value = self.alloc.notes[key][sub]
            types.update(value if isinstance(value, dict) else {28: value})
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            self.assertEqual(_u32(self.rom, at + sf.F_TYPE), detail["type"])
            self.assertEqual(detail["type"], types[detail["set"]],
                             f"{detail['name']} must name the live weakened type of set {detail['set']}")
            self.assertNotEqual(detail["type"], 0, "a 0 type makes the scan show ???")

    def test_the_type_each_entry_names_resolves_to_a_real_enemy_entry(self):
        for detail in self.notes["new"]:
            at = ENEMY_TABLE + ENEMY_ENTRY * detail["type"]
            hp = _u32(self.rom, at + 4)
            self.assertTrue(0 < hp < 100000, f"{detail['name']} HP {hp}")
            self.assertNotEqual(bytes(self.rom[at:at + ENEMY_ENTRY]), b"\xFF" * ENEMY_ENTRY)

    def test_round_2_fights_the_enemy_future_cell_scans_as(self):
        """The plateau's own round 2 item has to carry the same type the Future Cell entry names, or
        the owner scans one Cell and fights another."""
        item = self.alloc.notes["plateau"]["item"]
        cell = [d for d in self.notes["new"] if d["set"] == 28][0]
        self.assertEqual(_u32(self.rom, item + 8), cell["type"])

    def test_the_names_and_portraits_are_the_ones_he_asked_for(self):
        self.assertEqual(sf.names(), ("Future 17", "Future 18", "Future Cell"))
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            self.assertEqual(_cstr(self.rom, _u32(self.rom, at + sf.F_NAME) - ROM_BASE), detail["name"])
            self.assertEqual(_u32(self.rom, at + sf.F_SET), detail["set"])
            self.assertEqual(_u32(self.rom, at + sf.F_PORTRAIT), detail["portrait"])
            self.assertEqual(_u32(self.base, sf.TABLE + sf.ENTRY * detail["from"] + sf.F_PORTRAIT),
                             detail["portrait"], "the portrait is the vanilla entry's own")

    def test_each_bio_is_the_vanilla_text_plus_the_one_shared_closing_line(self):
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            text = _cstr(self.rom, _u32(self.rom, at + sf.F_BIO) - ROM_BASE)
            vanilla = _cstr(self.base, _u32(self.base, sf.TABLE + sf.ENTRY * detail["from"]
                                            + sf.F_BIO) - ROM_BASE)
            self.assertTrue(text.endswith(sf.TAIL), detail["name"])
            body = text[:-len(sf.TAIL)]
            self.assertEqual(body, vanilla.replace(sf.CELL_CUT, "", 1) if detail["set"] == 28
                             else vanilla)
            self.assertEqual(len(text), detail["bio_len"])

    def test_the_lengths_are_the_measured_ones(self):
        """581, 582 and 587 against the vanilla table's own 582 ceiling. Cell is 5 over, which is
        why the module drops a sentence rather than keeping the whole vanilla bio."""
        self.assertEqual([d["bio_len"] for d in self.notes["new"]], [581, 582, 587])
        self.assertEqual(self.notes["longest_bio"], 587)
        self.assertNotIn(sf.CELL_CUT.strip(), _cstr(
            self.rom, _u32(self.rom, self.notes["table"] + sf.ENTRY * 130 + sf.F_BIO) - ROM_BASE))

    def test_the_save_bits_are_the_spare_byte_and_nothing_past_it(self):
        self.assertEqual(self.notes["save_bits"], [(0x12A, 0), (0x12A, 1), (0x12A, 2)])
        self.assertEqual(sf.O_SCOUTER + (sf.SCOUTER_BITS - 1 >> 3), sf.SAVE_SPARE_BYTE - 1,
                         "the documented field ends on the byte before the spare one")

    # ----- order and re-runs -----

    def test_a_second_run_raises(self):
        with self.assertRaises(ValueError):
            sf.apply(bytearray(self.rom), self.alloc)

    def test_it_refuses_to_run_after_plateau(self):
        """plateau relocates the MAP table and must stay last, so this module declares the order."""
        notes = dict(self.alloc.notes)
        notes.pop("scouter_future")
        rom, alloc = log2_build.assemble(
            log2_build.BASE, [n for n in log2_build.read_build_list(LIST) if n != "scouter_future"])
        with self.assertRaises(ValueError):
            sf.apply(rom, alloc)                       # alloc.notes already holds "plateau"


if __name__ == "__main__":
    unittest.main()
