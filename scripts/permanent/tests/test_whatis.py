r"""
test_whatis.py - Tests for rom\whatis.py, the address lookup tool.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_whatis.py -v
The shape tests build a synthetic ROM buffer, so they prove the three shapes without the base ROM.
The known-answer tests read the base ROM and the disassembly repo, and skip when either is missing.
Source: docs\tasks\2026-11-05-whatis-tool\brief.md.
"""
import struct
import unittest
from pathlib import Path

from rom import whatis

ROM_BASE = 0x08000000

# ===== the synthetic ROM =====
SIZE = 0x40000
TABLE = 0x08400000                                   # a table base in the data region
STRIDE, COUNT = 16, 8                                # span 0x80
BASE_LDR, BASE_LIT = 0x20F0, 0x2100                  # ldr r0,[pc,#0xc] reading the BASE
MID_LDR, MID_LIT = 0x2000, 0x2014                    # ldr r4,[pc,#0x10] reading ENTRY 2, the trap shape
DATA_WORD = 0x30000                                  # a data-region word pointing at entry 3


def synthetic() -> bytes:
    buf = bytearray(SIZE)
    struct.pack_into("<H", buf, MID_LDR, 0x4C04)     # 0x4Cxx: Rd is r4, so a 0x48xx-only match misses it
    struct.pack_into("<I", buf, MID_LIT, TABLE + 2 * STRIDE)
    struct.pack_into("<H", buf, BASE_LDR, 0x4803)    # 0x48xx: Rd is r0
    struct.pack_into("<I", buf, BASE_LIT, TABLE)
    struct.pack_into("<I", buf, DATA_WORD, TABLE + 3 * STRIDE)
    return bytes(buf)


class Shapes(unittest.TestCase):
    def setUp(self):
        self.rom = synthetic()
        self.s = whatis.shapes(TABLE, self.rom, STRIDE * COUNT, STRIDE, COUNT, declared=True)

    def test_shape_a_sees_only_the_base_word(self):
        self.assertEqual(self.s.a_gba, [BASE_LIT])
        self.assertEqual(self.s.a_thumb, [])

    def test_shape_c_sees_the_words_shape_a_cannot(self):
        self.assertEqual([o for o, _ in self.s.c], [MID_LIT, DATA_WORD])
        self.assertNotIn(MID_LIT, self.s.a_gba)

    def test_shape_b_matches_every_destination_register(self):
        sites = {a: v for a, _, v in self.s.b}
        self.assertEqual(sites, {MID_LDR: TABLE + 2 * STRIDE, BASE_LDR: TABLE})

    def test_the_verdict_names_the_disagreement_and_the_entry(self):
        text = "\n".join(whatis.verdict(self.s, TABLE))
        self.assertIn("SHAPES DISAGREE", text)
        self.assertIn(f"rom:{MID_LIT:#x}", text)
        self.assertIn("entry 2", text)
        self.assertIn("would have reported 1 references, not 2", text)

    def test_a_guessed_span_states_that_it_is_a_guess(self):
        loose = whatis.shapes(TABLE, self.rom, STRIDE * COUNT, declared=False)
        text = "\n".join(whatis.verdict(loose, TABLE))
        self.assertIn("GUESSED", text)
        self.assertNotIn("SHAPES DISAGREE", text)

    def test_a_word_one_past_the_end_is_counted_and_named(self):
        buf = bytearray(self.rom)
        struct.pack_into("<I", buf, 0x31000, TABLE + STRIDE * COUNT)
        s = whatis.shapes(TABLE, bytes(buf), STRIDE * COUNT, STRIDE, COUNT, declared=True)
        self.assertEqual(s.c_end, [0x31000])
        self.assertNotIn(0x31000, [o for o, _ in s.c])    # it is NOT inside: the range ends one word short
        text = "\n".join(whatis.verdict(s, TABLE))
        self.assertIn("one past the end", text)
        self.assertNotIn("BUG:", text)                    # the end bucket must not read as a lost literal

    def test_the_shapes_agree_when_nothing_points_inside(self):
        s = whatis.shapes(TABLE + 0x10000, self.rom, 0x100, declared=True)
        self.assertIn("The three shapes agree", "\n".join(whatis.verdict(s, TABLE + 0x10000)))

    def test_a_skipped_shape_c_never_reads_as_three_shapes_agreeing(self):
        s = whatis.shapes(TABLE + 0x10000, self.rom, None)
        text = "\n".join(whatis.verdict(s, TABLE + 0x10000))
        self.assertIn("Shape C did not run", text)
        self.assertNotIn("The three shapes agree", text)


class Parsing(unittest.TestCase):
    def test_every_address_form_resolves(self):
        for raw, gba, kind in [("rom:0x3B8140", 0x083B8140, "rom"), ("0x3B8140", 0x083B8140, "rom"),
                               ("0x083B8140", 0x083B8140, "rom"), ("0x03001FA8", 0x03001FA8, "ram"),
                               ("sub_0800a680", 0x0800A680, "rom"), ("loc_0800A6E8", 0x0800A6E8, "rom")]:
            with self.subTest(raw=raw):
                q = whatis.parse(raw)
                self.assertEqual((q.gba, q.kind), (gba, kind))

    def test_a_symbol_name_resolves_to_its_address(self):
        q = whatis.parse("map_table")
        self.assertEqual(q.gba, 0x08409368)
        self.assertIn("symbols", q.note)

    def test_a_plain_word_stays_text(self):
        q = whatis.parse("combat")
        self.assertIsNone(q.gba)
        self.assertEqual(q.kind, "text")

    def test_a_bible_tag_matches_only_its_own_number(self):
        q = whatis.parse("set:5")
        self.assertEqual(q.kind, "tag")
        pat = q.pattern()
        self.assertIsNone(pat.search("the gi clone of `set:56` and `set:59`"))
        self.assertIsNotNone(pat.search("Gohan uses `set:5` here"))

    def test_an_odd_data_address_keeps_its_low_bit(self):
        self.assertEqual(whatis.parse("0x083E9DFB").gba, 0x083E9DFB)   # a script byte, not a Thumb pointer
        self.assertEqual(whatis.parse("0x0800A681").gba, 0x0800A680)   # inside the code region: a pointer

    def test_the_right_boundary_stops_a_short_address_matching_a_longer_one(self):
        pat = whatis.parse("rom:0x195").pattern()
        self.assertIsNone(pat.search("the 4th literal `rom:0x195C` names entry 3"))
        self.assertIsNotNone(pat.search("a word at `rom:0x195` holds it"))

    def test_text_matching_is_a_plain_substring(self):
        pat = whatis.parse("combat").pattern()
        self.assertIsNotNone(pat.search("the combatant record"))       # a hex boundary would drop this
        self.assertIsNotNone(pat.search("#combat #map"))


class Sources(unittest.TestCase):
    def test_nothing_found_names_every_source_it_searched(self):
        text = "\n".join(whatis.answer("zzzznotathinginthisproject", refs=False))
        self.assertIn("the search returned nothing", text)
        self.assertIn("Sources searched:", text)
        for name, _ in whatis.SOURCES:
            self.assertIn(name + ":", text)
        self.assertNotIn("does not exist", text.replace("does not exist.", ""))

    def test_the_bible_rows_come_from_the_one_parser(self):
        rows = whatis._bible_hits(whatis.parse("rom:0x409368"))
        self.assertGreaterEqual(len(rows), 5)
        self.assertTrue(any("FOUR literals" in r.text for r in rows))

    def test_our_modules_are_searched_and_the_blind_spot_is_stated(self):
        text = "\n".join(whatis.answer("rom:0x409368", refs=False))
        self.assertIn("battle_arena.py", text)
        self.assertIn("cannot show in a static search", text)

    def test_the_tool_never_writes(self):
        src = Path(whatis.__file__).read_text(encoding="utf-8")
        for forbidden in ("write_text", "write_bytes", "mkdir", "unlink", '"w"', "'w'"):
            self.assertNotIn(forbidden, src)


@unittest.skipUnless(whatis.RAM_LEDGER.exists(), "the disassembly repo is not on this machine")
class DisassemblySources(unittest.TestCase):
    def test_the_ram_ledger_names_the_sprite_directory_word(self):
        text = "\n".join(whatis.answer("0x03001FA8", refs=False))
        self.assertIn("Sprite_CurrentDirectory", text)
        self.assertIn("behaviour-test", text)

    def test_our_name_matches_the_behaviour_tested_one(self):
        """`player_ptr` was OUR wrong name for this word and it cost hours on 2026-11-05. An agent
        and a cross-model review each repeated it back, and the whole diagnosis built on "the player
        pointer is NULL" was wrong: zero is its normal resting value during play. The
        behaviour-tested name is Sprite_CurrentDirectory. This guards the rename, so the misnomer
        cannot come back through our own symbol table."""
        theirs = [r["new"] for r in whatis._ram_ledger() if int(r["address"], 16) == 0x03001FA8]
        text = "\n".join(whatis.answer("0x03001FA8", refs=False))
        self.assertIn(theirs[0], text)                    # read from the ledger, never hardcoded
        self.assertNotIn("player_ptr", text)

    def test_a_function_start_names_its_generated_file(self):
        text = "\n".join(whatis.answer("0x0800A680", refs=False))
        # The disassembly repo renames functions, so assert the shape of the answer, not a name.
        self.assertIn("0x0800a680 is the start of", text)
        self.assertIn(".s", text)
        self.assertIn("contained by", text)

    def test_a_missing_indexed_file_falls_back_to_the_address_name(self):
        """The index may name Foo.s while the emitter has only written code_<addr>.s. The address is
        READ FROM THE TREE, never hardcoded. 0x0800A680 was address-named in the stale gnu tree and is
        Character_SetActiveIndex.s in the real one, so a literal here rots on the next rename."""
        ondisk = sorted(whatis.GENERATED_CODE.glob("code_0*.s"))
        self.assertTrue(ondisk, f"no address-named file under {whatis.GENERATED_CODE}")
        addr = int(ondisk[0].stem[len("code_"):], 16)
        self.assertIn(ondisk[0].name, whatis._sfile("Not_A_Real_File.s", addr))
        self.assertIn("NOT on disk under either name", whatis._sfile("Not_A_Real_File.s", 0x08000000))

    def test_an_address_inside_a_function_names_the_function(self):
        hold = whatis.containing(0x0800A6B8)
        self.assertEqual(hold[0], 0x0800A680)


@unittest.skipUnless(whatis.BASE_ROM.exists(), "the base ROM is not on this machine")
class KnownAnswers(unittest.TestCase):
    """The map table case of 2026-11-05: a one-shape sweep reported 3 literals and missed the 4th."""

    @classmethod
    def setUpClass(cls):
        cls.rom = whatis.BASE_ROM.read_bytes()
        cls.s = whatis.shapes(0x08409368, cls.rom, 56 * 327, 56, 327, declared=True)

    def test_shape_a_finds_the_three_base_literals(self):
        self.assertEqual(self.s.a_gba, [0x5ADC, 0x5D5C, 0xEBD8])

    def test_shape_b_finds_seven_load_sites_including_the_fourth_literal(self):
        # Six name the base or entry 3; the seventh, rom:0xE178, names the byte after the last entry.
        self.assertEqual([a for a, _, _ in self.s.b],
                         [0x18D6, 0x5778, 0x598C, 0x5A6E, 0x5C18, 0xE178, 0xEB8A])
        self.assertIn((0x18D6, 0x195C, 0x08409410), self.s.b)

    def test_shape_c_finds_the_fourth_literal_that_names_entry_3(self):
        code = [(o, v) for o, v in self.s.c if o < self.s.code_hi]
        self.assertEqual(code, [(0x195C, 0x08409410)])
        self.assertEqual((0x08409410 - 0x08409368) // 56, 3)
        self.assertEqual(len(self.s.c), 52)

    def test_one_word_names_the_byte_after_the_last_map_entry(self):
        """rom:0xE1D0, loaded at rom:0xE178. No base-keyed shape and no inside-range shape sees it."""
        self.assertEqual(self.s.c_end, [0xE1D0])
        self.assertIn((0xE178, 0xE1D0, 0x0840DAF0), self.s.b)
        self.assertNotIn("BUG:", "\n".join(whatis.verdict(self.s, 0x08409368)))

    def test_the_ending_table_has_exactly_the_two_type_5_records(self):
        s = whatis.shapes(0x083B8140, self.rom, 0x1000)
        self.assertEqual(s.a_gba, [0x3C4E94, 0x3DD040])
        self.assertEqual(s.b, [])


if __name__ == "__main__":
    unittest.main()
