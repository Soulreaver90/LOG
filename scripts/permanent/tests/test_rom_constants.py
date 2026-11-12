r"""
test_rom_constants.py - Pin the ROM table addresses the readers hold, on the base ROM AND on a build.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_rom_constants.py -v
Why:     webfoot_decompress.SET_TABLE is the BASE ROM's sprite set table. gohan_gi copies that table into
         the expansion area, appends ids 157-160 and repoints the literal rom:0x959C at the copy. A reader
         that keeps SET_TABLE then reads a DEAD copy, returns vanilla art and says nothing. set_table() and
         set_offset() resolve the live table instead, and these tests fail if a reader goes back.
Also:    the item, string, character, visited, scouter and quest tables are held as bare constants that
         nothing pinned. Each one is checked here on both ROMs, through the literals that name it.
Builds:  the dev master (build_list_dev.txt) once in memory, about 3 seconds.
Limit:   the literal counts come from an aligned-word search of the base ROM. A reader that forms a table
         address by arithmetic would not appear in that search and is not covered.
"""
import contextlib
import io
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import log2_build
from rom import item_index, log2_save, log2_sprites, webfoot_decompress
from rom.webfoot_decompress import FIRST_ID, ROM_BASE, SET_TABLE, read_set, rom_ptr, set_offset, set_table

# ===== constants =====
GI_IDS = (157, 158, 159, 160)                  # the sets gohan_gi appends past the vanilla end
VANILLA_IDS = range(FIRST_ID, 157)             # the ids the vanilla table holds
CHANGED_ID = 58                                # superperfect_cell repaints Rage, so its entry moves
CODE_END = 0x800000                            # the base ROM; the expansion area holds no literal pool

# (what holds it, GBA address, aligned words in the base ROM that name it)
TABLES = [
    ("item_index.TABLE and the log2_save item table", 0x086ADE24, 5),
    ("item_index.STRING_TABLE", 0x080E2840, 20),
    ("log2_save default character records", 0x081D9548, 1),
    ("log2_save visited table", 0x086F6D8C, 2),
    ("log2_save scouter table", 0x086F8E40, 5),
    ("log2_save.QUEST_TABLE", 0x086D68DC, 1),
]

_CACHE = {}


def built() -> dict:
    """{"rom": bytes, "notes": the gohan_gi allocator notes} for the dev master, built once."""
    if not _CACHE:
        rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(log2_build.DEV_LIST))
        _CACHE["rom"], _CACHE["notes"] = bytes(rom), alloc.notes["gohan_gi"]
    return _CACHE


def literal_sites(rom: bytes, value: int) -> list:
    """Every 4-aligned word in the base ROM image that holds this GBA address."""
    needle = struct.pack("<I", value)
    out, at = [], 0
    while True:
        at = rom.find(needle, at)
        if at < 0 or at >= CODE_END:
            return out
        if at % 4 == 0:
            out.append(at)
        at += 1


class SetTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = log2_build.BASE.read_bytes()
        cls.dev, cls.notes = built()["rom"], built()["notes"]

    def test_the_base_rom_resolves_to_the_base_constant(self):
        self.assertEqual(set_table(self.base), SET_TABLE)

    def test_the_build_moved_the_table(self):
        self.assertNotEqual(set_table(self.dev), SET_TABLE)
        self.assertEqual(set_table(self.dev), self.notes["set_table"])

    def test_the_build_resolves_the_gi_sets(self):
        for set_id in GI_IDS:
            self.assertEqual(set_offset(self.dev, set_id), self.notes[f"set_{set_id}"], set_id)

    def test_the_base_constant_cannot_reach_the_gi_sets(self):
        """The vanilla table ends at id 156, so SET_TABLE reads the next table instead of set 157."""
        for set_id in GI_IDS:
            through_constant = rom_ptr(self.dev, SET_TABLE + 4 * (set_id - FIRST_ID))
            self.assertNotEqual(through_constant, self.notes[f"set_{set_id}"], set_id)

    def test_a_vanilla_id_the_build_repainted_differs_from_the_dead_copy(self):
        live = set_offset(self.dev, CHANGED_ID)
        dead = rom_ptr(self.dev, SET_TABLE + 4 * (CHANGED_ID - FIRST_ID))
        self.assertNotEqual(live, dead)
        self.assertEqual(dead, rom_ptr(self.base, SET_TABLE + 4 * (CHANGED_ID - FIRST_ID)))

    def test_every_live_id_decodes_as_a_set(self):
        for set_id in list(VANILLA_IDS) + list(GI_IDS):
            off = set_offset(self.dev, set_id)
            self.assertIsNotNone(off, set_id)
            self.assertGreater(read_set(self.dev, off)["anims"], 0, set_id)

    def test_the_base_rom_reads_the_same_through_both_routes(self):
        """Base behaviour is unchanged: set_offset equals the old SET_TABLE expression for every vanilla id."""
        for set_id in VANILLA_IDS:
            self.assertEqual(set_offset(self.base, set_id),
                             rom_ptr(self.base, SET_TABLE + 4 * (set_id - FIRST_ID)), set_id)


class ReaderCallSiteTests(unittest.TestCase):
    """The helpers are not enough: each reader's own command must resolve through the live table."""

    @classmethod
    def setUpClass(cls):
        cls.dev, cls.notes = built()["rom"], built()["notes"]
        cls.dir = tempfile.TemporaryDirectory()
        cls.rom_path = Path(cls.dir.name) / "dev.gba"
        cls.rom_path.write_bytes(cls.dev)

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()

    def test_webfoot_set_command_resolves_a_gi_set(self):
        seen = {}

        def fake_read_set(rom, off):
            seen["off"] = off
            return {"anims": 0, "dirs": 4, "slot": 0, "table": off, "ptrs": []}

        with mock.patch.object(webfoot_decompress, "read_set", fake_read_set), \
                contextlib.redirect_stdout(io.StringIO()):
            webfoot_decompress.cmd_set(self.dev, ["157"])
        self.assertEqual(seen["off"], self.notes["set_157"])

    def test_sprites_export_resolves_a_gi_set(self):
        seen = {}

        def fake_export_set(rom, off, out_dir):
            seen["off"] = off
            return out_dir

        with mock.patch.object(log2_sprites, "export_set", fake_export_set), \
                mock.patch.object(log2_sprites, "set_records", return_value=[]), \
                contextlib.redirect_stdout(io.StringIO()):
            code = log2_sprites._main(["export", str(self.rom_path), "157", self.dir.name])
        self.assertEqual(code, 0)
        self.assertEqual(seen["off"], self.notes["set_157"])


class TableConstantTests(unittest.TestCase):
    """Nothing moves these tables today. These tests say so, and fail the day a patch does."""

    @classmethod
    def setUpClass(cls):
        cls.base = log2_build.BASE.read_bytes()
        cls.dev = built()["rom"]

    def test_the_modules_still_hold_the_pinned_addresses(self):
        self.assertEqual(item_index.TABLE + ROM_BASE, 0x086ADE24)
        self.assertEqual(item_index.STRING_TABLE + ROM_BASE, 0x080E2840)
        self.assertEqual(log2_save.QUEST_TABLE, 0x086D68DC)

    def test_the_base_rom_names_each_table_the_pinned_number_of_times(self):
        for name, value, count in TABLES:
            self.assertEqual(len(literal_sites(self.base, value)), count, name)

    def test_the_build_keeps_every_literal(self):
        for name, value, _ in TABLES:
            for at in literal_sites(self.base, value):
                self.assertEqual(struct.unpack_from("<I", self.dev, at)[0], value, f"{name} at rom:0x{at:X}")


if __name__ == "__main__":
    unittest.main()
