r"""
test_bible_ids.py - The bible's stable row ids: shape, uniqueness, and the stability property itself.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_bible_ids.py -v
Why: a bible "row N" was a FILE LINE NUMBER, so every merge silently re-pointed every citation at a
different fact (docs\tasks\2026-11-07-bible-row-ids\finding.md). The id is the fix, and the stability
test below is the whole point of the change: it inserts a row near the top of the real bible in memory,
re-runs the one assigner, and proves no pre-existing row moved to a different id.
Source: docs\tasks\2026-11-07-bible-row-ids\brief.md.
"""
import re
import sys
import unittest
from pathlib import Path
import log_paths  # noqa: E402

PERMANENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PERMANENT))

sys.path.insert(0, str(log_paths.DISASM))
import symbols  # noqa: E402

ID_FORM = re.compile(r"^B\d{4}$")
BIBLE = log_paths.BIBLE
# A row shaped like a real fact row, inserted near the top where it moves every line below it.
NEW_ROW = "| A test row that is never written to disk | #tool | C | TEST |"


def bible_lines() -> list:
    return BIBLE.read_text(encoding="utf-8").split("\n")


def first_data_line(lines: list) -> int:
    return next(i for i, l in enumerate(lines) if symbols.is_data_row(symbols.cells_of(l)))


class Shape(unittest.TestCase):
    def setUp(self):
        self.rows = symbols.bible_rows()

    def test_every_data_row_has_an_id(self):
        missing = [r.line_no for r in self.rows if not r.id]
        self.assertEqual(missing, [], f"{len(missing)} data row(s) carry no id")
        self.assertEqual(sum(1 for r in self.rows if r.id), len(self.rows))

    def test_the_ids_are_unique(self):
        ids = [r.id for r in self.rows]
        self.assertEqual(len(set(ids)), len(ids))

    def test_every_id_matches_the_form(self):
        bad = [r.id for r in self.rows if not ID_FORM.match(r.id)]
        self.assertEqual(bad, [])

    def test_no_row_cell_holds_an_id(self):
        """A parser that did not know the Id cell would read it as Src on a 3-column row."""
        bad = [(r.id, r.tags, r.label, r.src) for r in self.rows
               if ID_FORM.match(r.tags) or ID_FORM.match(r.label) or ID_FORM.match(r.src)]
        self.assertEqual(bad, [])

    def test_a_three_column_decision_row_keeps_its_own_cells(self):
        row = next(r for r in self.rows if r.id == "B1554")
        self.assertEqual(row.text, "Base ROM is LoG II USA; English HP and ki scale")
        self.assertEqual(row.tags, "#decision")
        self.assertEqual(row.label, "2026-10-16")
        self.assertEqual(row.src, "")


class Citation(unittest.TestCase):
    """An id must name one row and only one row, or it is no better than a line number."""

    def test_every_id_finds_exactly_its_own_row(self):
        from rom import whatis
        bad = []
        for row in symbols.bible_rows():
            hits = whatis._bible_hits(whatis.parse(row.id))
            if [h.id for h in hits] != [row.id]:
                bad.append((row.id, [h.id for h in hits]))
        # A substring search returned 2 rows for 13 of the 2030 ids, because an id also appears inside
        # another row's hex byte string. The whole-cell match is the reason this list is empty.
        self.assertEqual(bad, [])


class Stability(unittest.TestCase):
    """The property the whole change exists for. Nothing here writes to disk."""

    def setUp(self):
        self.lines = bible_lines()
        self.before = {r.id: r.text for r in symbols.parse_rows(self.lines)}
        self.assertTrue(self.before)

    def _after_insert(self, at_offset=0):
        at = first_data_line(self.lines) + at_offset
        grown = self.lines[:at] + [NEW_ROW] + self.lines[at:]
        out, assigned = symbols.assign_ids(grown)
        return symbols.parse_rows(out), assigned

    def test_an_insert_near_the_top_moves_no_existing_id(self):
        rows, _ = self._after_insert()
        after = {r.id: r.text for r in rows}
        for row_id, text in self.before.items():
            self.assertIn(row_id, after, f"{row_id} vanished after an insert above it")
            self.assertEqual(after[row_id], text, f"{row_id} now names a different fact")

    def test_the_inserted_row_gets_the_next_free_id(self):
        _, assigned = self._after_insert()
        self.assertEqual(len(assigned), 1)
        self.assertEqual(assigned[0][1], f"B{symbols.highest_id(self.lines) + 1:04d}")

    def test_the_line_number_does_move_so_it_cannot_be_an_identity(self):
        """The negative half of the proof: the thing the id replaces really is unstable."""
        rows, _ = self._after_insert()
        by_id = {r.id: r.line_no for r in rows}
        old = {r.id: r.line_no for r in symbols.parse_rows(self.lines)}
        moved = [i for i in old if by_id.get(i) != old[i]]
        self.assertGreater(len(moved), len(old) // 2,
                           "most rows must change line number, or this test proves nothing")

    @unittest.expectedFailure
    def test_an_id_is_never_reused_after_its_row_is_deleted(self):
        """The requirement, asserted. It fails today, so the suite prints "expected failures=1" and the
        gap stays visible: assign_ids counts from the highest id in the FILE, so deleting the newest
        row frees its id again. A real fix needs a high-water mark stored outside the rows."""
        top = f"B{symbols.highest_id(self.lines):04d}"
        shrunk = [l for l in self.lines if symbols.split_id(l)[1] != top]
        _, assigned = symbols.assign_ids(shrunk + [NEW_ROW])
        self.assertNotEqual(assigned[0][1], top, f"{top} was handed out a second time")


class Idempotence(unittest.TestCase):
    def test_a_second_run_assigns_nothing_and_changes_nothing(self):
        lines = bible_lines()
        out, assigned = symbols.assign_ids(lines)
        self.assertEqual(assigned, [])
        self.assertEqual(out, lines)


if __name__ == "__main__":
    unittest.main()
