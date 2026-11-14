r"""
test_make_status.py - Tests for the tracker generator (make_status.feature_codes).

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v

Why this file exists. make_status.py generates docs\status.md, and its Cross-reference health section
is the guard that is supposed to stop a feature code going missing. On 2026-11-14 the guard was found
to have a gap of its own: CODE_ROW accepted only [a-z0-9_, ] in the module cell, so ONE stray bracket
made the whole row fail to match and that code vanished from every health line at once. It was not
reported as built, not as unbuilt, and not as naming a missing module. It simply was not there.

The invariant these tests pin: EVERY code in the Reference table lands in exactly one bucket.
"""
import unittest
from unittest import mock

import make_status

# ===== fixtures =====
TABLE = "\n".join((
    "| Code | Module |",
    "| --- | --- |",
    "| ABC-1 | alpha_mod |",            # built
    "| ABC-2 | beta_mod, gamma_mod |",  # built, two modules
    "| ABC-3 | |",                      # no module yet, a legitimate state
    "| ABC-4 | (no module yet) |",      # malformed: the exact shape that used to vanish
    "| ABC-5 | Capital_Mod |",          # malformed: a capital used to break the whole row
    "not a row at all",
))


def codes_from(text):
    """Run feature_codes() against `text` instead of the real game-status.md."""
    with mock.patch.object(make_status, "GAME") as game:
        game.read_text.return_value = text
        return make_status.feature_codes()


class ReferenceTableTests(unittest.TestCase):
    def setUp(self):
        self.out = codes_from(TABLE)
        self.unbuilt = self.out.pop("__unbuilt__")
        self.malformed = self.out.pop("__malformed__")

    def test_a_well_formed_row_maps_its_code_to_its_module(self):
        self.assertEqual(self.out["alpha_mod"], ["ABC-1"])

    def test_two_modules_in_one_cell_both_claim_the_code(self):
        self.assertEqual(self.out["beta_mod"], ["ABC-2"])
        self.assertEqual(self.out["gamma_mod"], ["ABC-2"])

    def test_an_empty_cell_marks_the_feature_unbuilt(self):
        self.assertEqual(self.unbuilt, ["ABC-3"])

    def test_a_malformed_cell_is_REPORTED_not_dropped(self):
        """The regression test for 2026-11-14. Both shapes used to vanish silently."""
        self.assertEqual(self.malformed, ["ABC-4 -> '(no module yet)'", "ABC-5 -> 'Capital_Mod'"])

    def test_every_code_lands_in_exactly_one_bucket(self):
        """The invariant the old regex broke. A code in no bucket is the silent gap."""
        built = {c for codes in self.out.values() for c in codes}
        reported = {m.split(" -> ")[0] for m in self.malformed}
        for code in ("ABC-1", "ABC-2", "ABC-3", "ABC-4", "ABC-5"):
            hits = [n for n, group in
                    (("built", built), ("unbuilt", set(self.unbuilt)), ("malformed", reported))
                    if code in group]
            self.assertEqual(len(hits), 1, f"{code} landed in {hits}, must land in exactly one")

    def test_the_old_narrow_pattern_would_have_dropped_two_of_these(self):
        """Non-vacuous proof: without the fix this fixture loses ABC-4 and ABC-5 entirely."""
        import re
        old = re.compile(r"^\|\s*([A-Z]{3}-\d+)\s*\|\s*([a-z0-9_, ]*)\s*\|$")
        seen = {m.group(1) for line in TABLE.splitlines() if (m := old.match(line.strip()))}
        self.assertNotIn("ABC-4", seen)
        self.assertNotIn("ABC-5", seen)
        self.assertIn("ABC-1", seen)


class LiveTableTests(unittest.TestCase):
    def test_the_real_reference_table_has_no_malformed_row(self):
        out = make_status.feature_codes()
        self.assertEqual(out["__malformed__"], [])

    def test_the_real_reference_table_names_at_least_one_unbuilt_feature(self):
        """Guards the fixture style: an all-empty result would make the test above vacuous."""
        out = make_status.feature_codes()
        self.assertTrue(out["__unbuilt__"])


if __name__ == "__main__":
    unittest.main()
