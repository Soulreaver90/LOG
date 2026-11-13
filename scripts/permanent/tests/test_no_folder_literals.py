r"""
test_no_folder_literals.py - No file under scripts\permanent\ may spell a folder name, except log_paths.py.

Why:     a folder name spelled at the use site is what kept this tree impossible to reorganise. 29 of the
         34 art folders are live build inputs, so a rename meant editing dozens of files and hoping the
         grep was complete, which is how a build breaks quietly. With every name in log_paths.py, a move
         is a one-line change there.
Shapes:  the test reads each file's syntax tree, so it sees a name a text search would miss, and it
         checks three shapes.
         1. In a PATH JOIN, meaning a / "x", Path("x"), .joinpath("x") or os.path.join(a, "x"), a literal
            may hold NO owned folder name. This shape has no exceptions: it is the one that moves a read.
         2. Anywhere else, a BARE literal equal to an owned folder name is an error, because the code
            joins such a name to a root later (SETS, FORMS and GI_FOLDERS all do). ALSO_A_DATA_WORD
            excuses a word this project uses as data in three files or more; EXCEPTIONS pins the rest to
            one file each. Both carry a reason, and both are checked for rot below.
         3. A path under the user profile, hardcoded, is an error in both shapes.
Limits:  it reads .py only, so the map editor's .js and .mjs, and the emulator's .lua, are NOT covered.
         It knows only the folders log_paths.py names, so a NEW folder that log_paths does not hold is
         not caught: name a folder in log_paths when you make it, and this test covers it from then on.
         It cannot see a name built at run time, and it skips the constant parts of an f-string.
         An excused word is excused as a bare literal only: ART / "anim" is still an error.
         Docstrings are skipped, because a docstring names a folder to tell the reader where files live.
         scripts\one-time\ is history and is not swept.
Run:     py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent \
           -p test_no_folder_literals.py -v
"""
import ast
import re
import tempfile
import unittest
from pathlib import Path

import log_paths

SKIP_FILES = {"log_paths.py", "test_no_folder_literals.py"}
USER_PATH = re.compile(r"^[A-Za-z]:[\\/]+Users[\\/]", re.I)

# A folder name this project also uses as data, in three files or more.
ALSO_A_DATA_WORD = {
    "anim": "the frame record's animation index: a key of every manifest.json entry",
    "art": "a section of the beam struggle plan, and a tool folder note",
    "frames": "a count and a JSON field through the art and map tools",
    "golden": "a transplant status in gi_post, and the gate name in the gi tests",
    "owner": "a portrait source, against vanilla and against mine",
    "plateau": "the alloc.notes key patches.plateau writes",
    "portraits": "the alloc.notes key art_inject reads",
    "scene": "a map item kind, and a tool folder note",
    "tables": "the alloc.notes key future_androids writes",
}

# The same, pinned to the one or two files that use it. (file, literal) -> why.
EXCEPTIONS = {
    ("art/gi_art.py", "compare"): "an argparse command of gi_art.py",
    ("art/gi_aura.py", "aura"): "the effect kind, against the body it is drawn on",
    ("art/gi_aura.py", "reference"): "an argparse command of gi_aura.py",
    ("emu/capture.py", "capture"): "the default job name",
    ("make_tool_index.py", "disasm"): "one note per tool folder, keyed as the index prints it",
    ("make_tool_index.py", "map-editor"): "one note per tool folder, keyed as the index prints it",
    ("make_tool_index.py", "patches"): "one note per tool folder, keyed as the index prints it",
    ("make_tool_index.py", "review"): "one note per tool folder, keyed as the index prints it",
    ("make_tool_index.py", "tests"): "one note per tool folder, keyed as the index prints it",
    ("map-editor/serve.py", "deleted"): "a field of the delete response",
    ("map-editor/serve.py", "maps"): "a field of the map list response",
    ("patches/powerup_fx.py", "dust"): "the effect kind, against the aura",
    ("patches/trunks_tank.py", "trunks_tank"): "the patch name and its alloc.notes key, not the art folder",
    ("tests/test_aura.py", "aura"): "the effect kind, against the body it is drawn on",
    ("tests/test_make_tool_index.py", "map-editor"): "it checks the note the index prints for that folder",
    ("tests/test_make_tool_index.py", "tests"): "it checks that the index leaves the suite out",
    ("tests/test_map_editor_io.py", "maps"): "a field of the map list response",
    ("tests/test_powerup_fx.py", "dust"): "the effect kind, against the aura",
    ("tests/test_trunks_tank.py", "trunks_tank"): "the patch name and its build list entry, not the art folder",
}


def owned_names() -> set:
    """Every path segment of every log_paths constant under the LOG root. A FILE constant gives its
    folders only. The set follows log_paths, so a new constant starts policing itself."""
    names = set()
    for key, value in vars(log_paths).items():
        if not key.isupper() or not isinstance(value, Path):
            continue
        try:
            parts = value.relative_to(log_paths.ROOT).parts
        except ValueError:
            continue                                   # a repo or a tool outside the LOG root
        names |= set(parts[:-1] if value.suffix else parts)
    return names


def _docstring_ids(tree: ast.AST) -> set:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                    and isinstance(first.value.value, str):
                out.add(id(first.value))
    return out


def _join_ids(tree: ast.AST) -> set:
    """ids of the str constants in a path join: a / "x", Path("x"), .joinpath("x"), os.path.join(...)."""
    out = set()
    for node in ast.walk(tree):
        here = []
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            here = [node.left, node.right]
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
            os_join = (name == "join" and isinstance(node.func, ast.Attribute)
                       and getattr(node.func.value, "attr", "") == "path")
            if name in ("Path", "joinpath") or os_join:
                here = node.args
        out |= {id(n) for n in here if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    return out


def offences(path: Path, names: set) -> list:
    """Every folder name this file spells, one line each."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skip, joins = _docstring_ids(tree), _join_ids(tree)
    try:
        rel = path.relative_to(log_paths.PERMANENT).as_posix()
    except ValueError:
        rel = path.name                                # a probe this test wrote
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)) or id(node) in skip:
            continue
        text = node.value
        if USER_PATH.match(text):
            out.append(f"{rel}:{node.lineno}: {text!r} hardcodes a path under the user profile")
        elif id(node) in joins:
            named = sorted(set(re.split(r"[\\/]+", text)) & names)
            if named:
                out.append(f"{rel}:{node.lineno}: the join {text!r} spells the folder "
                           f"{', '.join(named)}: use its log_paths constant")
        elif text in names and text not in ALSO_A_DATA_WORD and (rel, text) not in EXCEPTIONS:
            out.append(f"{rel}:{node.lineno}: {text!r} is a folder name: use log_paths.<NAME>.name")
    return out


def swept() -> list:
    return [p for p in sorted(log_paths.PERMANENT.rglob("*.py"))
            if "__pycache__" not in p.parts and p.name not in SKIP_FILES]


def bare_literals(path: Path) -> set:
    """Every str constant of the file that is neither a docstring nor part of a path join."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    skip, joins = _docstring_ids(tree), _join_ids(tree)
    return {n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in skip and id(n) not in joins}


class NoFolderLiteralsTests(unittest.TestCase):
    def setUp(self):
        self.names = owned_names()

    def test_log_paths_owns_enough_names_to_police(self):
        """A guard on the guard: an empty or tiny name set would let every other check pass."""
        self.assertGreater(len(self.names), 50, "log_paths names too few folders")
        for name in ("art", "gi_base", "golden", "builds", "roms", "vanilla-sets", "map-editor"):
            self.assertIn(name, self.names, name)
        self.assertGreater(len(swept()), 150, "the sweep found almost no files: check the glob")

    def test_no_file_outside_log_paths_spells_a_folder_name(self):
        bad = []
        for path in swept():
            bad += offences(path, self.names)
        self.assertEqual(bad, [], "\n" + "\n".join(bad))

    def test_every_exception_still_fires(self):
        """An exception nothing needs is a stale licence, so it goes."""
        for (rel, text), why in EXCEPTIONS.items():
            path = log_paths.PERMANENT / rel
            self.assertTrue(path.is_file(), f"{rel} is gone: drop its exception ({why})")
            self.assertIn(text, bare_literals(path), f"{rel} no longer holds {text!r}: drop it ({why})")

    def test_every_data_word_still_fires(self):
        """Same for the word list: a word no file uses as data must not stay excused."""
        live = set()
        for path in swept():
            live |= bare_literals(path)
        self.assertEqual(sorted(w for w in ALSO_A_DATA_WORD if w not in live), [])

    def test_every_excused_word_is_a_folder_name(self):
        """A word that names no folder does not belong in either list at all."""
        for word in list(ALSO_A_DATA_WORD) + [text for _, text in EXCEPTIONS]:
            self.assertIn(word, self.names, f"{word!r} names no folder log_paths holds")

    def test_it_catches_a_literal_that_comes_back(self):
        """The check must FAIL on each shape a folder name returns in, or it proves nothing."""
        shapes = ['P = ROOT / "gi_base"\n',
                  'P = Path("art/golden")\n',
                  'P = os.path.join(root, "vanilla-sets")\n',
                  'P = ROOT.joinpath("builds")\n',
                  'NAME = "gi_ssj2_v2"\n',
                  'def f(a="trunks_tank"): pass\n',
                  'P = Path(r"C:\\Users\\someone\\Documents\\GitHub")\n',
                  'P = ART / "anim"\n']                      # an excused word is no excuse in a join
        with tempfile.TemporaryDirectory() as tmp:
            for n, shape in enumerate(shapes):
                probe = Path(tmp) / f"probe_{n}.py"
                probe.write_text('r"""A docstring may say art\\golden and must not fire."""\n' + shape,
                                 encoding="utf-8")
                with self.subTest(shape=shape.strip()):
                    self.assertTrue(offences(probe, self.names), shape)

    def test_it_passes_the_correct_form(self):
        """It must stay quiet on the right form, or it would only teach people to add exceptions."""
        clean = ('r"""The folder art\\gi_base is named in log_paths, and a docstring may say so."""\n'
                 'import log_paths\n'
                 'P = log_paths.GI_BASE / "manifest.json"\n'
                 'Q = log_paths.under(tmp, log_paths.GOLDEN)\n'
                 'R = root / log_paths.ART.name\n'
                 'S = {"anim": 0, "dir": 1}\n')
        with tempfile.TemporaryDirectory() as tmp:
            probe = Path(tmp) / "clean.py"
            probe.write_text(clean, encoding="utf-8")
            self.assertEqual(offences(probe, self.names), [])


if __name__ == "__main__":
    unittest.main()
