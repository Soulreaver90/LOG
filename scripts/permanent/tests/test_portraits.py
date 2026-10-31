r"""
test_portraits.py - Tests for the gi portrait patch (patches.gohan_portraits), Task 7.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds scratch\test-roms\portraits.gba once (gohan_gi, ssj2_form, gohan_portraits; log:
scratch\test-roms\build-log-test.md) and the same patches in memory, so the tests see the ROM before and
after gohan_portraits and its notes.
Source:  docs\research\re-portraits.md. The readers below take the table and entries from the ROM (literals rom:0xBE10,
rom:0x26458, rom:0x3B30), never from the patch module's notes.
"""
import hashlib
import struct
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

import log2_build
import log_paths
from rom.rom_space import Allocator
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, unpack_frame

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
BASE_ROM = BASE.read_bytes()
OUT = log_paths.TEST_ROMS / "portraits.gba"

PORTRAIT_FN, PORTRAIT_LITERAL = 0x0800BDCC, 0xBE10       # re-portraits.md 1
OLD_BLOCK, STRUCT_WORD, OLD_IDS = 0x3EC9D0, 0x03000E90, 115
PLUS2_LITERAL, PLUS3_LITERAL = 0x26458, 0x3B30           # re-portraits.md 3
APPEARANCE, ENTRY, ENTRIES = 0x1D967C, 20, 23            # relocated table holds entry 22 (Task 6)
OBJ_PAL, STATUS_PAL = 0x1DA6C8, 0x1D4F50
NEW = {"gi_ssj": (5, (0x3E, 0x0D), (115, 116)), "gi_ssj2": (22, (0x3D, 0x0C), (117, 118)),
       "gi_base": (2, (0x3B, 0x0A), (119, 120))}
GI_STATUS = {232, 234}                                   # Piccolo gi: the game pairs OBJ 97 to 232, 233 to 234
OLD_GI_DIALOG = {96, 80, 215}                            # indices recolored to 97 and 233
MAP_LOAD_LITERAL, SET_TABLE_LITERAL = 0xC804, 0x959C    # one of the 17 table literals; the set table literal
BASE_ENTRY = 2
BASE_SRC_SHA1 = "2bcc68315e4919f872ca9e773e1c24bdeb201ce4"   # approved drawing, source art


# ===== build (once) =====

_CACHE = {}


def built() -> dict:
    """{"before": ROM after ssj2_form, "rom": after gohan_portraits, "notes", "file"} built in memory and to OUT."""
    if _CACHE:
        return _CACHE
    from patches import gohan_gi, gohan_portraits, ssj2_form
    from tests.test_build import TEST_LOG, build
    rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
    alloc = Allocator(len(rom), log2_build.EXPANSION)
    gohan_gi.apply(rom, alloc)
    ssj2_form.apply(rom, alloc)
    before, notes_before = bytes(rom), {k: dict(v) for k, v in alloc.notes.items()}
    gohan_portraits.apply(rom, alloc)
    with mock.patch.object(log2_build, "BUILD_LOG", TEST_LOG):
        build(BASE, OUT, ["gohan_gi", "ssj2_form", "gohan_portraits"])
    _CACHE.update(before=before, notes_before=notes_before, rom=bytes(rom), notes=alloc.notes,
                  file=OUT.read_bytes())
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


# ===== readers (from the ROM) =====

def block_of(rom: bytes) -> int:
    return u32(rom, PORTRAIT_LITERAL) - ROM_BASE


def portrait(rom: bytes, pid: int) -> tuple:
    """(type, size, pixels) of portrait id pid as 0x0800BDCC finds it: word at block + 4 + 4 * id."""
    kind, size, data, _ = unpack_frame(rom, u32(rom, block_of(rom) + 4 + 4 * pid) - ROM_BASE)
    return kind, size, data


def portraits_of(rom: bytes, entry: int, literal: int) -> bytes:
    """+2 and +3 of an appearance entry in the table that literal (a reader's pool) points at."""
    t = u32(rom, literal) - ROM_BASE
    return rom[t + ENTRY * entry + 2:t + ENTRY * entry + 4]


class PortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]["gohan_portraits"]
        cls.notes_before = b["notes_before"]

    # lookup and table

    def test_lookup_has_no_upper_bound(self):                 # new ids 115-120 reach the table word
        texts = [t for _, t in listing(self.rom, PORTRAIT_FN, 32)]
        cmps = [t for t in texts if t.startswith("cmp r0,")]
        self.assertEqual(cmps, ["cmp r0,#0x0", "cmp r0,#0x1", "cmp r0,#0x7"])
        self.assertIn("bgt 0x800be06", texts)
        self.assertEqual(self.rom[0xBDCC:0xBE10], BASE_ROM[0xBDCC:0xBE10])

    def test_relocated_block_keeps_struct_word_and_old_ids(self):
        block = block_of(self.rom)
        self.assertGreaterEqual(block, 0x800000)
        self.assertEqual(u32(self.rom, block), STRUCT_WORD)
        self.assertEqual(self.rom[block:block + 4 + 4 * OLD_IDS], BASE_ROM[OLD_BLOCK:OLD_BLOCK + 4 + 4 * OLD_IDS])

    def test_every_old_id_decodes_unchanged(self):            # cutscenes use raw ids 8-114
        old = bytes(self.before)
        for pid in range(8, OLD_IDS):
            self.assertEqual(portrait(self.rom, pid), portrait(old, pid), pid)

    def test_new_ids_decode_to_the_pngs(self):
        from patches.gohan_portraits import load_art
        for name, (_, _, ids) in NEW.items():
            for pid, px in zip(ids, load_art(name)):
                self.assertEqual(portrait(self.rom, pid), (0, 0x1000, px), pid)
                self.assertEqual(u32(self.rom, block_of(self.rom) + 4 + 4 * pid) % 4, 0)

    # appearance entries

    def test_entries_point_at_new_ids(self):
        for literal in (PLUS2_LITERAL, PLUS3_LITERAL):        # both readers see the same relocated table
            self.assertEqual(u32(self.rom, literal), self.notes_before["ssj2_form"]["table"] + ROM_BASE)
        for name, (entry, old, new) in NEW.items():
            self.assertEqual(tuple(portraits_of(self.before, entry, PLUS2_LITERAL)), old, name)
            self.assertEqual(tuple(portraits_of(self.rom, entry, PLUS2_LITERAL)), new, name)

    def test_gi_base_entry_points_at_119_120(self):            # the drawn base portrait
        self.assertEqual(tuple(portraits_of(self.before, BASE_ENTRY, PLUS3_LITERAL)), (0x3B, 0x0A))
        self.assertEqual(tuple(portraits_of(self.rom, BASE_ENTRY, PLUS2_LITERAL)), (119, 120))
        self.assertEqual(tuple(portraits_of(self.rom, BASE_ENTRY, PLUS3_LITERAL)), (119, 120))

    def test_other_entries_unchanged(self):
        t0, t1 = u32(self.before, PLUS2_LITERAL) - ROM_BASE, u32(self.rom, PLUS2_LITERAL) - ROM_BASE
        changed = [e for e in range(ENTRIES)
                   if self.before[t0 + ENTRY * e:t0 + ENTRY * (e + 1)] != self.rom[t1 + ENTRY * e:t1 + ENTRY * (e + 1)]]
        self.assertEqual(changed, [2, 5, 22])

    def test_apply_fails_closed(self):
        from patches import gohan_portraits
        table = self.notes_before["ssj2_form"]["table"]
        for off, junk in ((PORTRAIT_LITERAL, b"\0\0\0\0"), (OLD_BLOCK, b"\0\0\0\0"),
                          (OLD_BLOCK + 4 + 4 * OLD_IDS, b"\0\0\0\0"), (PLUS3_LITERAL, b"\0\0\0\0"),
                          (table + ENTRY * 5 + 2, b"\x3F"), (table + ENTRY * 22 + 3, b"\x0D"),
                          (table + ENTRY * BASE_ENTRY + 2, b"\x3C")):
            rom = bytearray(self.before)
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes.update({k: dict(v) for k, v in self.notes_before.items()})
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                gohan_portraits.apply(rom, alloc)
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run ssj2_form first"):
            gohan_portraits.apply(bytearray(self.before), Allocator(len(self.before), [(0xF00000, 0x100000)]))

    def test_wrong_order_names_the_patch_to_run_first(self):    # review Minor 7
        from patches import gohan_portraits
        rom = bytearray(self.before)
        with self.assertRaisesRegex(ValueError, "run ssj2_form first"):
            gohan_portraits.apply(rom, Allocator(len(rom), [(0xF00000, 0x100000)]))
        self.assertEqual(bytes(rom), self.before)

    def test_entries_resolve_to_gi_sets_through_code_literals(self):   # review Minor 6
        rom, gi = self.rom, self.notes_before["gohan_gi"]
        table = u32(rom, MAP_LOAD_LITERAL) - ROM_BASE                    # appearance table the map load reads
        set_table = u32(rom, SET_TABLE_LITERAL) - ROM_BASE
        base_set_table = u32(BASE_ROM, SET_TABLE_LITERAL) - ROM_BASE
        for entry, want in ((2, gi["set_157"]), (5, gi["set_158"]), (22, gi["set_159"]), (4, gi["set_160"])):
            set_id = rom[table + ENTRY * entry + 1]
            self.assertEqual(u32(rom, set_table + 4 * (set_id - 7)) - ROM_BASE, want, f"entry {entry}")
        self.assertEqual([rom[table + ENTRY * e + 1] for e in (2, 5, 22, 4)], [157, 158, 159, 160])
        # Task 7 list: the copied set table keeps word 58 (vanilla armor Rage); r30 superperfect_cell repoints it later
        self.assertEqual(u32(rom, set_table + 4 * (58 - 7)), u32(BASE_ROM, base_set_table + 4 * (58 - 7)))

    def test_apply_rejects_index_outside_portrait_colors(self):
        from patches import gohan_portraits
        real = gohan_portraits.load_art
        for bad, side in ((0, 0), (168, 0), (0, 1)):
            def fake(name, bad=bad, side=side):
                art = list(real(name))
                art[side] = bytes([bad]) + art[side][1:]
                return tuple(art)
            rom = bytearray(self.before)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes.update({k: dict(v) for k, v in self.notes_before.items()})
            with mock.patch.object(gohan_portraits, "load_art", fake), self.assertRaises(ValueError):
                gohan_portraits.apply(rom, alloc)
            self.assertEqual(bytes(rom), self.before)

    # art

    def test_pngs_reproduce_from_sources(self):               # sheet cells convert, the base is the drawn PNG
        from patches.gohan_portraits import BASE_SRC, FORMS, form_art, load_art
        self.assertEqual(set(FORMS), set(NEW))
        for name in FORMS:
            self.assertEqual(form_art(BASE_ROM, name)[:2], load_art(name), name)
        self.assertEqual(load_art("gi_base")[0], Image.open(BASE_SRC).tobytes())
        self.assertEqual(hashlib.sha1(BASE_SRC.read_bytes()).hexdigest(), BASE_SRC_SHA1)

    def test_gi_uses_piccolo_colors(self):
        from patches.gohan_portraits import load_art
        for name in NEW:
            dialog, status = load_art(name)
            self.assertFalse(OLD_GI_DIALOG & set(dialog), name)
            self.assertTrue({97, 233} & set(dialog), name)
            self.assertLessEqual(GI_STATUS, set(status), name)
            for d, s in zip(dialog, status):                      # every gi pixel pairs 97 to 232 and 233 to 234
                if d in (97, 233):
                    self.assertEqual(s, {97: 232, 233: 234}[d], name)

    def test_art_uses_only_portrait_colors(self):
        from patches.gohan_portraits import load_art
        used = {}
        for key, ids in (("dialog", range(26, OLD_IDS)), ("status", range(8, 26))):
            used[key] = {k for pid in ids for k in portrait(BASE_ROM, pid)[2]}
        for name in NEW:
            dialog, status = load_art(name)
            self.assertFalse(set(dialog) - used["dialog"], name)
            self.assertFalse(set(status) - used["status"], name)
            self.assertFalse({0, 168} & (set(dialog) | set(status)), name)

    # build

    def test_base_8mb_differs_only_at_portrait_literal(self):
        diff = [i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]]
        self.assertTrue(diff)
        self.assertFalse(set(diff) - set(range(PORTRAIT_LITERAL, PORTRAIT_LITERAL + 4)))

    def test_palettes_unchanged(self):
        for off in (OBJ_PAL, STATUS_PAL):
            self.assertEqual(self.rom[off:off + 0x200], BASE_ROM[off:off + 0x200])

    def test_new_data_only_in_free_expansion(self):
        block = self.notes["block"]
        spans = [(block, 4 + 4 * (OLD_IDS + 6))] + [(h, 8 + 0x1000) for h in self.notes["frames"].values()]
        for start, n in spans:
            self.assertGreaterEqual(start, 0x800000)
            self.assertEqual(self.before[start:start + n], b"\xFF" * n, hex(start))
        diff = [i for i in range(log2_build.BASE_SIZE, log2_build.ROM_SIZE) if self.before[i] != self.rom[i]]
        table = self.notes_before["ssj2_form"]["table"]
        spans += [(table + ENTRY * entry + 2, 2) for entry, *_ in NEW.values()]   # +2/+3 of entries 2, 5 and 22
        inside = {o for s, n in spans for o in range(s, s + n)}
        self.assertFalse([hex(i) for i in diff if i not in inside])

    def test_file_build_matches_memory_build(self):
        self.assertEqual(built()["file"], self.rom)


if __name__ == "__main__":
    unittest.main()
