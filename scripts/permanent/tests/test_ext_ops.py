r"""
test_ext_ops.py - Pin scene_lib.EXT_OPS against the handlers themselves.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_ext_ops.py -v
Why:     on 2026-11-06 four entries in EXT_OPS were wrong and nobody could see it. `ext 23 visited` took
         one argument and the handler pops two. `ext 131`, `132` and `133` were setters taking an amount,
         and the handlers take nothing and PUSH a byte. Each would have encoded a corrupt record.
Source:  docs\research\scene-vm-ext-ops.json, generated from the byte-exact disassembly by
         scripts\permanent\disasm\ext_ops.py. Regenerate the page, never hand-edit it.
Also:    table_length() against table_end(), because the first-END rule truncated 229 of 303 tables.
Build:   dev_build() assembles the dev list up to fullpower_ssj IN MEMORY. The moved table tests need a
         build, because only a build moves a table word. No ROM file is written.
"""
import json
import unittest
from pathlib import Path
from unittest import mock

import log2_build
import log_paths
from scene import op_usage
from scene import scene_lib as S

PROFILE = log_paths.RESEARCH / "scene-vm-ext-ops.json"
HANDLER_COUNT = 145                 # ext 0 to 144. Word 145 is 0x03000E90, IWRAM, not a handler.
NOT_AN_OP = {145}                   # named by us (the chapter card) and past the end of the table
ROM_BASE = 0x08000000
BASE_ROM = log2_build.BASE.read_bytes()
DENDE_TABLE, DENDE_FIRST_END = 0x3DD380, 3
DENDE_LOOSE, DENDE_EXACT = 12, 11       # the 12th word is the next record's header
PICCOLO_TABLE, PICCOLO_EXACT = 0x3E47F8, 8   # decoded by hand: 8 words, word 7 is END
# The vanilla death table. fullpower_ssj copies the post-Cell seq 20 record into expansion and repoints
# word 19, so this table is the live proof that a build moves a table word. The record ADDRESS is read
# from the build's own notes, never typed: the allocator moves it whenever an earlier module changes size.
MOVED_TABLE, MOVED_WORD, MOVED_LENGTH = 0x3EC758, 19, 56
MOVED_RECORD = ("fullpower_ssj", "post_cell_seq20")
EXIT_RECORD = ("fullpower_ssj", "exit_seq3")

_BUILD = {}


def dev_build() -> tuple:
    """(rom, alloc) of the dev list up to and with fullpower_ssj, built in memory. No file is written."""
    if not _BUILD:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:names.index("fullpower_ssj") + 1])
        _BUILD.update(rom=bytes(rom), alloc=alloc)
    return _BUILD["rom"], _BUILD["alloc"]


def moved_record(key: tuple) -> int:
    """The GBA address a build gave one of fullpower_ssj's record copies."""
    module, name = key
    return dev_build()[1].notes[module]["records"][name] + ROM_BASE


def profile() -> dict:
    return {r["ext"]: r for r in json.loads(PROFILE.read_text(encoding="utf-8"))}


class ProfileTests(unittest.TestCase):

    def test_the_profile_covers_every_handler(self):
        rows = profile()
        self.assertEqual(len(rows), HANDLER_COUNT)
        self.assertEqual(sorted(rows), list(range(HANDLER_COUNT)))


class ArityTests(unittest.TestCase):
    """Every named op's argument list, against the pops its handler makes."""

    def test_each_named_op_matches_its_handler(self):
        rows = profile()
        for ext, entry in sorted(S.EXT_OPS.items()):
            if ext in NOT_AN_OP:
                continue
            with self.subTest(ext=ext, name=entry[0]):
                row = rows[ext]
                # A predicate replaces its argument in place, so depth does not fall. It still
                # consumes that one value, so it is compared as one argument.
                found = 1 if row.get("predicate") else row["arity"]
                self.assertEqual(found, len(entry[1]))

    def test_the_four_entries_that_were_wrong(self):
        self.assertEqual(len(S.EXT_OPS[23][1]), 2)          # visited(zone, area), not visited(map)
        for ext in (131, 132, 133):
            self.assertEqual(S.EXT_OPS[ext][1], ())         # getters: they push, they do not take

    def test_we_name_nothing_past_the_handler_table(self):
        past = {n for n in S.EXT_OPS if n >= HANDLER_COUNT}
        self.assertEqual(past, NOT_AN_OP)


class TableLengthTests(unittest.TestCase):
    """An END entry carries a resume index. It does not end a table."""

    def test_table_length_reads_past_the_first_end_entry(self):
        self.assertEqual(S.table_end(BASE_ROM, DENDE_TABLE), DENDE_FIRST_END)
        self.assertEqual(S.table_length(BASE_ROM, DENDE_TABLE), DENDE_LOOSE)

    def test_the_record_set_makes_the_length_exact(self):
        """A record header below 0x10000 is indistinguishable from an END entry, so a walk with
        no record set reads one word too far. The hand-decoded Piccolo table is the check: its
        length is 8, the loose walk says 9, and the exact walk reproduces 8."""
        records = op_usage.record_addresses(BASE_ROM)
        self.assertEqual(S.table_length(BASE_ROM, DENDE_TABLE, records=records), DENDE_EXACT)
        self.assertEqual(S.table_length(BASE_ROM, PICCOLO_TABLE, records=records), PICCOLO_EXACT)
        self.assertEqual(S.table_length(BASE_ROM, PICCOLO_TABLE), PICCOLO_EXACT + 1)

    def test_table_length_is_never_shorter_than_table_end(self):
        for at in (DENDE_TABLE, 0x3DBDD4, 0x3E47F8):
            with self.subTest(table=hex(at)):
                self.assertGreaterEqual(S.table_length(BASE_ROM, at), S.table_end(BASE_ROM, at))


class RegionTests(unittest.TestCase):
    """scene_lib names the expansion area by value, because it must not import log2_build."""

    def test_the_expansion_region_matches_the_build_script(self):
        start, size = log2_build.EXPANSION[0]
        self.assertEqual(S.EXPANSION_REGION, (start, start + size))
        self.assertEqual(start, log2_build.BASE_SIZE)
        self.assertEqual(start + size, log2_build.ART_REGION[0])

    def test_a_moved_record_is_still_a_table_word(self):
        """A build moves records into expansion. A walker that knows only the vanilla script
        region stops at the first moved word and under-reads the table with no error."""
        exit_seq3 = moved_record(EXIT_RECORD)                 # fullpower_ssj's chamber exit copy
        self.assertGreaterEqual(exit_seq3 - ROM_BASE, log2_build.BASE_SIZE)
        self.assertTrue(S.is_record_pointer(exit_seq3))
        self.assertTrue(S.is_record_pointer(0x083EA3EC))      # vanilla, in the script region
        self.assertFalse(S.is_record_pointer(0x08F00000))     # the art region, never a record
        self.assertFalse(S.is_record_pointer(0x03001FC0))     # IWRAM

    def test_the_vanilla_table_the_build_moves_a_word_of(self):
        """The premise is CHECKED here, not stated: this build really does move word MOVED_WORD.

        fullpower_ssj copies the post-Cell seq 20 record into expansion and repoints the word. Base
        and build must then agree on the table's length, or a walker that knows only the vanilla
        script region under-reads the table with no error.
        """
        rom = dev_build()[0]
        record = moved_record(MOVED_RECORD)
        self.assertGreaterEqual(record - ROM_BASE, log2_build.BASE_SIZE)
        self.assertEqual(S.table_words(rom, MOVED_TABLE, MOVED_LENGTH)[MOVED_WORD], record)
        self.assertNotEqual(S.table_words(BASE_ROM, MOVED_TABLE, MOVED_LENGTH)[MOVED_WORD], record)
        self.assertEqual(S.table_length(BASE_ROM, MOVED_TABLE), MOVED_LENGTH)
        self.assertEqual(S.table_end(BASE_ROM, MOVED_TABLE), MOVED_LENGTH)
        self.assertEqual(S.table_length(rom, MOVED_TABLE), MOVED_LENGTH)
        self.assertEqual(S.table_end(rom, MOVED_TABLE), MOVED_LENGTH)

    def test_a_walker_blind_to_expansion_under_reads_the_moved_table(self):
        """The control. A walker that knows only the vanilla script region stops at the moved word,
        so the table reads 19 words instead of 56 and every op site past it is lost."""
        rom, lo_hi = dev_build()[0], S.EXPANSION_REGION
        with mock.patch.object(S, "EXPANSION_REGION", (lo_hi[1], lo_hi[1])):
            self.assertFalse(S.is_record_pointer(moved_record(MOVED_RECORD)))
            self.assertEqual(S.table_length(rom, MOVED_TABLE), MOVED_WORD)
        self.assertEqual(S.table_length(rom, MOVED_TABLE), MOVED_LENGTH)


class OverRunTests(unittest.TestCase):
    """The walk reads past an END entry, so the thing to measure is how far it over-runs.

    Vanilla puts a scene's records just BEFORE its table, so the bytes after a table are the next
    scene's records, not padding. Measured on the base ROM: 150 of the 302 readable tables walk one
    word too far, and in ALL 150 that word is the last of the walk and is a record header that reads
    as an END entry. Every walker skips END entries, so no op site is gained or lost: only the
    length is wrong, and the record set fixes it."""

    def test_the_over_run_is_one_word_at_the_tail_and_never_a_site(self):
        tables = sorted(t for t in op_usage.scene_tables(BASE_ROM) if 0 <= t < len(BASE_ROM))
        self.assertGreater(len(tables), 290)
        records = op_usage.record_addresses(BASE_ROM, tables)
        over = []
        for at in tables:
            loose = S.table_length(BASE_ROM, at)
            exact = S.table_length(BASE_ROM, at, records=records)
            self.assertIn(loose - exact, (0, 1), hex(at))
            if loose != exact:
                over.append(at)
                last = S.table_words(BASE_ROM, at, loose)[-1]
                self.assertTrue(S.is_end_entry(last), hex(at))
        self.assertEqual(len(over), 150)

    def test_no_table_span_swallows_another_tables_start(self):
        """Weaker than the check above and kept because it answers a different question: a table
        that reached INTO another table would double-count every site in it. None does."""
        starts = sorted(t for t in op_usage.scene_tables(BASE_ROM) if 0 <= t < len(BASE_ROM))
        records = op_usage.record_addresses(BASE_ROM, starts)
        bad = []
        for at in starts:
            hi = at + 4 * S.table_length(BASE_ROM, at, records=records)
            bad += [(hex(at), hex(u)) for u in starts if at < u < hi]
        self.assertEqual(bad, [], "a table span reaches into another table")


if __name__ == "__main__":
    unittest.main()
