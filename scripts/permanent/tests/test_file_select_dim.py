r"""
test_file_select_dim.py - Tests for patches.file_select_dim: the menu dim table keeps skin skin-colored.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_file_select_dim.py -v
Applies the patch to the padded base ROM. The hue and luma test is an own implementation (not the scratch
sweep). GI_INDICES restates the sweep of r17 sets 157-160, anims 0 and 1 (scripts\one-time\2026-10-18-file-select\sweep_gi.txt).
Source:  docs\tasks\2026-10-18-file-select\file-select-report.md.
"""
import colorsys
import struct
import unittest

import log2_build
from rom.log2_sprites import PALETTE_OFF, set_records
from patches import file_select_dim
from rom.rom_space import Allocator
from rom.thumb_dis import dis
from rom.webfoot_decompress import SET_TABLE, rom_ptr, unpack_frame

# ===== constants =====
BASE_ROM = log2_build.BASE.read_bytes()
TABLE, LITERAL = 0x6D0ED0, 0x7D1C
LOAD_SITES = (0x08007C9A, 0x08007CCE)                       # ldr r1,=0x086D0ED0 in 0x08007C70 and 0x08007CB6
NEW = {114: 116, 115: 117}
GI_INDICES = (1, 2, 9, 11, 12, 13, 15, 20, 21, 22, 23, 26, 27, 34, 35, 37, 38, 39, 44, 46, 64, 65, 72, 88, 89,
              113, 114, 115, 116, 117, 120, 167, 191, 195, 211)
SKIN_SETS = (53, 55, 57, 60, 61)                            # vanilla party sets with pixels 114 or 115
OTHER_SETS = (72, 103, 104, 128, 129, 130, 132, 133, 134, 135, 137, 138, 139, 140)
MAX_HUE, LUMA = 15.0, (0.55, 1.05)


def padded() -> bytearray:
    return bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))


def patched() -> tuple:
    rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
    file_select_dim.apply(rom, alloc)
    return rom, alloc


def color(rom: bytes, i: int) -> tuple:
    c = struct.unpack_from("<H", rom, PALETTE_OFF + 2 * i)[0]
    return (c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8


def breaks(rom: bytes, i: int) -> bool:
    """True when dim[i] moves a colored entry's hue past MAX_HUE or its luma ratio out of LUMA."""
    src, dst = color(rom, i), color(rom, rom[TABLE + i])
    luma = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    (h0, s0, _), (h1, _, _) = (colorsys.rgb_to_hsv(*[v / 255 for v in c]) for c in (src, dst))
    shift = min(abs(h0 - h1), 1 - abs(h0 - h1)) * 360
    ratio = luma(dst) / luma(src) if luma(src) else 1.0
    return (s0 >= 0.25 and shift > MAX_HUE) or not LUMA[0] <= ratio <= LUMA[1]


def pixels(rom: bytes, set_id: int, index_set: set) -> int:
    off = rom_ptr(rom, SET_TABLE + 4 * (set_id - 7))
    return sum(sum(1 for p in unpack_frame(rom, r["header"])[2] if p in index_set)
               for r in set_records(rom, off) if r["anim"] in (0, 1))


class FileSelectDimTests(unittest.TestCase):

    def test_changes_exactly_two_bytes(self):
        before = padded()
        rom, alloc = patched()
        diff = [o for o in range(len(rom)) if rom[o] != before[o]]
        self.assertEqual(diff, [TABLE + 114, TABLE + 115])
        self.assertEqual((rom[TABLE + 114], rom[TABLE + 115]), (116, 117))
        self.assertEqual(alloc.notes["file_select_dim"], {"table": TABLE, "entries": NEW})

    def test_refuses_a_changed_entry_before_writing(self):
        rom = padded()
        rom[TABLE + 115] = 0
        snapshot = bytes(rom)
        with self.assertRaises(ValueError):
            file_select_dim.apply(rom, Allocator(len(rom), log2_build.EXPANSION))
        self.assertEqual(bytes(rom), snapshot)

    def test_refuses_a_moved_table(self):
        rom = padded()
        rom[LITERAL:LITERAL + 4] = struct.pack("<I", 0x08900000)
        snapshot = bytes(rom)
        with self.assertRaises(ValueError):
            file_select_dim.apply(rom, Allocator(len(rom), log2_build.EXPANSION))
        self.assertEqual(bytes(rom), snapshot)

    def test_table_has_one_pool_word_and_two_loads(self):
        words = [o for o in range(0, len(BASE_ROM) - 3, 4) if struct.unpack_from("<I", BASE_ROM, o)[0] == 0x086D0ED0]
        self.assertEqual(words, [LITERAL])
        for site in LOAD_SITES:
            self.assertEqual(dis(BASE_ROM, site)[0], "ldr r1,=0x086d0ed0")

    def test_only_skin_114_115_break_before(self):
        self.assertEqual([i for i in GI_INDICES if breaks(BASE_ROM, i)], [114, 115])

    def test_no_gi_index_breaks_after(self):
        rom, _ = patched()
        self.assertEqual([i for i in GI_INDICES if breaks(rom, i)], [])

    def test_new_entries_are_darker_skin(self):
        rom, _ = patched()
        for i, j in NEW.items():
            self.assertIn(rom[TABLE + i], (114, 115, 116, 117))
            self.assertLess(sum(color(rom, j)), sum(color(rom, i)))

    def test_blast_radius_is_gohan_and_goku(self):
        for s in SKIN_SETS + OTHER_SETS:                        # no set remap (+8) composes into the table
            off = rom_ptr(BASE_ROM, SET_TABLE + 4 * (s - 7))
            self.assertEqual(struct.unpack_from("<I", BASE_ROM, off + 8)[0], 0, f"set {s}")
        for s in SKIN_SETS:
            self.assertGreater(pixels(BASE_ROM, s, {114, 115}), 0, f"set {s}")
        for s in OTHER_SETS:
            self.assertEqual(pixels(BASE_ROM, s, {114, 115}), 0, f"set {s}")


if __name__ == "__main__":
    unittest.main()
