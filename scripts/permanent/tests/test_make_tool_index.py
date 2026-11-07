"""Tests for make_tool_index. The index must not rot, so its parser is pinned."""
import tempfile
import unittest
from pathlib import Path

import make_tool_index


def write(tmp, name, text):
    p = Path(tmp) / name
    p.write_text(text, encoding="utf-8")
    return p


class PurposeTests(unittest.TestCase):
    def test_takes_the_first_docstring_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "a.py", '"""Do the thing.\n\nMore prose.\n"""\n')
            self.assertEqual(("Do the thing.", ""), make_tool_index.purpose(p))

    def test_strips_a_leading_filename_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "a.py", '"""a.py - Do the thing."""\n')
            self.assertEqual("Do the thing.", make_tool_index.purpose(p)[0])

    def test_reports_no_docstring(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "a.py", "x = 1\n")
            self.assertEqual("(no docstring)", make_tool_index.purpose(p)[0])

    def test_a_file_that_will_not_parse_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write(tmp, "a.py", "def (:\n")
            self.assertEqual(("(will not parse)", ""), make_tool_index.purpose(p))

    def test_superseded_by_is_read_from_the_assignment_not_the_prose(self):
        """The word SUPERSEDED in a docstring must NOT retire a tool: make_tool_index's own
        docstring explains the convention, and an earlier version retired itself."""
        with tempfile.TemporaryDirectory() as tmp:
            prose = write(tmp, "a.py", '"""Explains what SUPERSEDED means."""\n')
            self.assertEqual("", make_tool_index.purpose(prose)[1])
            real = write(tmp, "b.py", '"""Old thing."""\nSUPERSEDED_BY = "new.py"\n')
            self.assertEqual("new.py", make_tool_index.purpose(real)[1])

    def test_the_real_index_generator_is_not_marked_retired(self):
        here = Path(make_tool_index.__file__)
        self.assertEqual("", make_tool_index.purpose(here)[1])


class FolderTests(unittest.TestCase):
    """Every folder of tools must reach the index. One that does not is invisible to the search
    CLAUDE.md tells every agent to run before writing a script, which is how a second tool for a
    job that already has one gets written."""

    def text(self) -> str:
        return "\n".join(make_tool_index.build())

    def test_every_permanent_subfolder_that_holds_tools_is_in_the_index(self):
        index = self.text()
        missing = [folder.name for folder in make_tool_index.tool_folders()
                   if f"\\{folder.name}\\`" not in index]
        self.assertEqual([], missing)

    def test_the_map_editor_folder_and_its_tools_are_listed(self):
        """The regression: the folder was absent from the index from the day it was created."""
        index = self.text()
        self.assertIn(r"`scripts\permanent\map-editor\`", index)
        for name in ("roundtrip.py", "map_file.py", "import_map.py", "tile_stream.py"):
            self.assertIn(f"`{name}`", index)

    def test_the_folder_list_is_read_from_disk_and_not_a_fixed_tuple(self):
        """A fixed tuple is what hid map-editor, emu, review and ghidra for a week."""
        names = [folder.name for folder in make_tool_index.tool_folders()]
        self.assertIn("map-editor", names)
        self.assertNotIn("tests", names)
        self.assertNotIn("__pycache__", names)


if __name__ == "__main__":
    unittest.main()
