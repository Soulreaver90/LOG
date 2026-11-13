r"""Every Path constant in log_paths must name something that is on disk.

Why: a moved folder with a stale constant is invisible. A test that guards on .exists() skips,
and a skip reads as a pass. On 2026-11-13 the builds and art reorganisation left two constants
pointing at folders that no longer existed, and 22 tests quietly stopped running behind them.

The control test below proves this guard fails when a constant goes stale. Without it, a guard
that silently stopped checking would also read as a pass.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import log_paths  # noqa: E402

SKIP = set()  # a constant that is created on demand goes here, with a comment saying why


def missing_in(module) -> list:
    """Every public Path attribute of the module that is not on disk, as "NAME = path" lines."""
    return [f"{name} = {value}" for name, value in sorted(vars(module).items())
            if isinstance(value, Path) and not name.startswith("_")
            and name not in SKIP and not value.exists()]


class RegistryTests(unittest.TestCase):
    def test_every_path_constant_exists(self):
        missing = missing_in(log_paths)
        self.assertEqual([], missing,
                         f"{len(missing)} constant(s) name a path that is not on disk:\n"
                         + "\n".join(missing))


class ControlTests(unittest.TestCase):
    """The guard must FAIL on a stale constant, and must name it."""

    class Stale:
        GOOD = log_paths.ROOT
        BAD = log_paths.ROOT / "no-such-folder-this-is-the-control"

    def test_a_stale_constant_is_reported(self):
        self.assertEqual(1, len(missing_in(self.Stale)))

    def test_the_report_names_the_stale_constant(self):
        self.assertIn("BAD", missing_in(self.Stale)[0])

    def test_a_live_constant_is_not_reported(self):
        self.assertNotIn("GOOD", " ".join(missing_in(self.Stale)))


if __name__ == "__main__":
    unittest.main()
