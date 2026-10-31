r"""
test_r31_saves.py - Tests for the r31 save, state and ROM copies, and the r31 chamber save (final, 2026-10-23).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_r31_saves.py -v
Checks: the r30 .sav and .ss1-.ss5 copies and the ROM pair are byte copies. log2_poc_r31_chamber2.sav is
log2_poc_r30_chamber2.sav with slot 2 = slot 3 of log2_poc_r30.sav (before the Cell Games): every 0x168 slot
byte is copied, no field changes (a slot holds its own Adler-32 and no slot number), slots 1 and 3 and every
byte outside slot 2 equal the chamber save. Layout from docs\research\re-save-format.md (slot n at 0x10 + n * 0x168).
log2_poc_r31_scouter.sav is that save with slot 2 header +1 bit 2 set (the scouter switch, ext 113) and its
Adler-32 redone; nothing else changes.
"""
import unittest
import zlib

import log2_build
import log_paths
from rom.log2_save import SLOT_DATA, adler32, read_ram, slot_range
from rom.thumb_dis import listing

BUILD = log_paths.BUILDS
CHAMBER_R30, CELLGAMES_R30, CHAMBER_R31 = "log2_poc_r30_chamber2.sav", "log2_poc_r30.sav", "log2_poc_r31_chamber2.sav"
COPIES = [("log2_poc_r30.sav", "log2_poc_r31.sav"), ("log2_poc_r31.gba", "log2_poc_r31_chamber2.gba")]
COPIES += [(f"log2_poc_r30.ss{k}", f"log2_poc_r31.ss{k}") for k in range(1, 6)]
COPIES += [("log2_poc_r31.gba", "log2_poc_r31_scouter.gba")]
SCOUTER_SAV = "log2_poc_r31_scouter.sav"


def ram_of(name: str) -> bytearray:
    path = BUILD / name
    if not path.exists():
        raise unittest.SkipTest(f"{name} missing")
    return read_ram(path.read_bytes())


class CopyTests(unittest.TestCase):
    def test_r31_saves_states_and_rom_pair_are_byte_copies(self):
        for src, dst in COPIES:
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)


class ChamberSaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new, cls.chamber, cls.cellgames = ram_of(CHAMBER_R31), ram_of(CHAMBER_R30), ram_of(CELLGAMES_R30)

    def test_slot_2_is_the_before_the_cell_games_slot(self):
        self.assertEqual(self.new[slot_range(1)], self.cellgames[slot_range(2)])
        s = self.new[slot_range(1)]
        self.assertEqual((s[0], s[2], s[3], s[4]), (4, 9, 1, 1))          # Goku leads, map 9,1 (the Lookout)
        self.assertEqual(s[0xB4 + 195 // 8] >> (195 % 8) & 1, 0)           # Cell not beaten
        self.assertEqual(s[0xB4 + 191 // 8] >> (191 % 8) & 1, 1)           # Dragon Balls returned

    def test_slots_1_and_3_and_the_rest_are_the_chamber_save(self):
        for n in (0, 2):
            self.assertEqual(self.new[slot_range(n)], self.chamber[slot_range(n)], n + 1)
        s2 = slot_range(1)
        self.assertEqual(self.new[:s2.start] + self.new[s2.stop:], self.chamber[:s2.start] + self.chamber[s2.stop:])

    def test_each_checksum_is_valid(self):
        for n in range(3):
            s = slot_range(n).start
            data, stored = bytes(self.new[s:s + SLOT_DATA]), int.from_bytes(self.new[s + SLOT_DATA:s + SLOT_DATA + 4],
                                                                            "little")
            self.assertEqual(adler32(data), stored, n + 1)
            self.assertEqual(zlib.adler32(data), stored, n + 1)
            self.assertEqual(self.new[s + 1] & 1, 1, n + 1)                 # in-use bit: the file select shows it

    def test_slot_offset_comes_from_the_index_not_the_data(self):      # slot load @0x08003F9C
        text = [t for _, t in listing(log2_build.BASE.read_bytes(), 0x08003FAC, 7)]
        self.assertEqual([text[0], text[1], text[2], text[6]], ["mov r2,#0xff", "add r2,#0x69", "mul r2,r6",
                                                               "add r2,#0x10"])   # 0x10 + n * 0x168


class ScouterSaveTests(unittest.TestCase):
    """Select opens the scouter only with save +1 bit 2, which ext 113 sets where the story gives the Scouter."""

    def test_slot_2_differs_only_in_the_bit_and_its_checksum(self):
        new, src = ram_of(SCOUTER_SAV), ram_of(CHAMBER_R31)
        s = slot_range(1).start
        changed = [i for i in range(len(new)) if new[i] != src[i]]
        self.assertEqual(changed[0], s + 1)
        self.assertTrue(all(s + SLOT_DATA <= i < s + SLOT_DATA + 4 for i in changed[1:]))
        self.assertEqual((src[s + 1], new[s + 1]), (0x03, 0x07))
        stored = int.from_bytes(new[s + SLOT_DATA:s + SLOT_DATA + 4], "little")
        self.assertEqual(adler32(bytes(new[s:s + SLOT_DATA])), stored)

    def test_select_needs_bit_2_and_ext_113_sets_it(self):
        base = log2_build.BASE.read_bytes()
        select = [t for _, t in listing(base, 0x08004D68, 9)]
        self.assertEqual(select[1:3] + select[5:8], ["lsl r3,r3,#29", "lsr r3,r3,#31", "ldrb r3,[r3,#0x1]",
                                                     "lsl r3,r3,#29", "lsr r3,r3,#31"])   # Select, then save +1 bit 2
        self.assertEqual([t for _, t in listing(base, 0x08004DAC, 1)], ["bl 0x8018540"])     # the scouter
        self.assertEqual(int.from_bytes(base[0x3B5D28 + 4 * 113:0x3B5D28 + 4 * 114], "little"), 0x0800AEB9)
        ext113 = [t for _, t in listing(base, 0x0800AEB8, 7)]
        self.assertEqual(ext113[1], "mov r2,#0x4")
        self.assertEqual(ext113[3:6], ["ldr r0,[r0,#0x20]", "ldrb r1,[r0,#0x1]", "orr r1,r2"])


if __name__ == "__main__":
    unittest.main()
