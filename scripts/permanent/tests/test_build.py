r"""
test_build.py - Tests for rom_space.py and log2_build.py (Task 1), and the build list include rule (r40).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Each test that needs a built ROM builds it itself. Builds write only under scratch\.
"""
import contextlib
import hashlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import log2_build
from log2_build import build as _build
import log_paths
from rom.rom_space import Allocator, find_free

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
BASE_SHA1 = "18e0715dec419f3501c301511530d2edcd590f8b"
PADDED_SHA1 = "11616203341e2eabc82527c43b823b3e868c34b9"  # play-tested 16 MB padded ROM
OUT_DIR = log_paths.TEST_ROMS
TEST_LOG = OUT_DIR / "build-log-test.md"
BASE_SIZE = 8388608
FULL_SIZE = 16777216


def build(*args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):  # keep the suite output clean
        return _build(*args, **kwargs)


def put(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


class BuildTests(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(log2_build, "BUILD_LOG", TEST_LOG)  # keep the real log clean
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_build_without_patches_is_padded_base(self):
        out = OUT_DIR / "nopatch.gba"
        sha = build(BASE, out, [])
        data = out.read_bytes()
        self.assertEqual(data[:BASE_SIZE], BASE.read_bytes())
        self.assertEqual(data[BASE_SIZE:], bytes([0xFF]) * (FULL_SIZE - BASE_SIZE))
        self.assertEqual(sha, hashlib.sha1(data).hexdigest())
        self.assertEqual(sha, PADDED_SHA1)

    def test_build_never_writes_under_data(self):
        target = ROOT / "data" / "x.gba"
        with self.assertRaises(ValueError):
            build(BASE, target, [])
        self.assertFalse(target.exists())

    def test_base_has_no_free_space(self):
        self.assertEqual(find_free(BASE.read_bytes()), [])  # recorded Task 1 finding

    def test_build_rejects_modified_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.gba"
            data = bytearray(BASE.read_bytes())
            data[0x100] ^= 0xFF
            bad.write_bytes(data)
            with self.assertRaises(ValueError):
                build(bad, OUT_DIR / "bad.gba", [])

    def test_command_line_runs_isolated(self):
        out = OUT_DIR / "cli.gba"
        script = ROOT / "scripts" / "permanent" / "log2_build.py"
        res = subprocess.run([sys.executable, "-I", str(script), "--out", str(out),
                              "--log", str(TEST_LOG)], capture_output=True, text=True,
                             cwd=str(ROOT))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn(PADDED_SHA1, res.stdout)
        self.assertEqual(len(out.read_bytes()), FULL_SIZE)

    def test_list_option_reads_the_main_list_or_a_named_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            trial = Path(tmp) / "trial_list.txt"
            trial.write_text("gohan_gi\n# note\nssj2_form   # comment\n", encoding="utf-8", newline="\n")
            cases = {("--list", "--out", "x.gba"): log2_build.read_build_list(),
                     ("--list", str(trial), "--out", "x.gba"): ["gohan_gi", "ssj2_form"],
                     ("--out", "x.gba", "--list", str(trial), "_probe"): ["gohan_gi", "ssj2_form", "_probe"]}
            for argv, want in cases.items():
                with mock.patch.object(log2_build, "build") as fake:
                    log2_build._main(list(argv))
                base, out, names = fake.call_args.args
                self.assertEqual((names, out), (want, Path("x.gba")), argv)

    def test_include_expands_in_place_and_nests(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "sub").mkdir()
            put(d / "main.txt", "a\n\n# comment\nb   # note\n")
            put(d / "trial.txt", "# trial\ninclude main.txt\nc\n")
            put(d / "sub" / "inner.txt", "x\ninclude ../trial.txt   # relative to sub\nd\n")
            self.assertEqual(log2_build.read_build_list(d / "trial.txt"), ["a", "b", "c"])
            self.assertEqual(log2_build.read_build_list(d / "sub" / "inner.txt"), ["x", "a", "b", "c", "d"])

    def test_include_cycle_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            put(d / "one.txt", "a\ninclude two.txt\n")
            put(d / "two.txt", "b\ninclude one.txt\n")
            put(d / "self.txt", "include self.txt\n")
            for name in ("one.txt", "two.txt", "self.txt"):
                with self.assertRaisesRegex(ValueError, "cycle", msg=name):
                    log2_build.read_build_list(d / name)

    def test_include_of_a_missing_file_names_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            put(d / "trial.txt", "include nope.txt\nc\n")
            put(d / "empty.txt", "include   # no file\n")
            with self.assertRaises(FileNotFoundError) as caught:
                log2_build.read_build_list(d / "trial.txt")
            self.assertIn("nope.txt", str(caught.exception))
            self.assertIn("trial.txt", str(caught.exception))
            with self.assertRaisesRegex(ValueError, "line 1"):
                log2_build.read_build_list(d / "empty.txt")

    def test_a_name_listed_twice_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            put(d / "main.txt", "a\nb\n")
            put(d / "trial.txt", "include main.txt\nb\n")
            put(d / "flat.txt", "a\nc\na\n")
            put(d / "double.txt", "include main.txt\ninclude main.txt\n")
            for name in ("trial.txt", "flat.txt", "double.txt"):
                with self.assertRaisesRegex(ValueError, "listed twice", msg=name):
                    log2_build.read_build_list(d / name)

    def test_every_trial_list_is_dev_plus_its_own_lines(self):
        """A trial carries the work-in-progress gi art, so it includes the dev master, not the golden one."""
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        lists = sorted(log2_build.BUILD_LIST.parent.glob("build_list_trial*.txt"))
        self.assertLessEqual({"build_list_trial.txt", "build_list_trial_chapters.txt",
                              "build_list_trial_vegeta19.txt"}, {p.name for p in lists})
        for path in lists:
            lines = [ln.split("#", 1)[0].strip() for ln in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([ln for ln in lines if ln][0], "include build_list_dev.txt", path.name)
            names = log2_build.read_build_list(path)
            self.assertEqual(names[:len(dev)], dev, path.name)
            self.assertFalse(set(names[len(dev):]) & set(dev), path.name)

    def test_the_two_masters_share_one_tail(self):
        """Only line 1 may differ, or dev stops rebuilding to r40 and every trial SHA-1 moves."""
        golden = log2_build.read_build_list(log2_build.BUILD_LIST)
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual((golden[0], dev[0]), ("gohan_gi_vanilla", "gohan_gi"))
        self.assertEqual(golden[1:], dev[1:])

    def test_find_free_skips_pointed_runs_and_unaligned(self):
        rom = bytearray(b"\x00\x01" * 0x4000)  # noise, no fill runs
        rom[0x2000:0x3000] = b"\xFF" * 0x1000
        rom[0x5001:0x6001] = b"\xFF" * 0x1000  # unaligned start
        self.assertEqual(find_free(bytes(rom)), [(0x2000, 0x1000)])
        rom[0x100:0x104] = (0x08000000 + 0x2800).to_bytes(4, "little")
        self.assertEqual(find_free(bytes(rom)), [])

    def test_allocator_never_overlaps(self):
        a = Allocator(8388608, [(0x700000, 0x100)])
        x, y = a.alloc(0x80), a.alloc(0x80)
        self.assertGreaterEqual(y, x + 0x80)
        with self.assertRaises(MemoryError):
            a.alloc(0x10)
        self.assertEqual(a.used(), [(x, 0x80), (y, 0x80)])
        self.assertEqual(a.notes, {})

    def test_patch_runs_with_shared_allocator(self):
        out = OUT_DIR / "patched.gba"
        sha = build(BASE, out, ["_probe"])
        data = out.read_bytes()
        self.assertEqual(sha, hashlib.sha1(data).hexdigest())
        self.assertNotEqual(sha, BASE_SHA1)
        self.assertEqual(len(data), FULL_SIZE)
        self.assertEqual(data.count(b"PROBE"), 1)
        self.assertEqual(data[BASE_SIZE:BASE_SIZE + 5], b"PROBE")  # lands in the expansion


if __name__ == "__main__":
    unittest.main()


class SavePairingTests(unittest.TestCase):
    r"""A ROM with no .sav beside it opens as a new game, so a trial build with no save loses the file.
    log2_build pairs one itself. These pin the three behaviours (2026-10-31)."""

    def test_pair_save_seeds_a_rom_that_has_no_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            rom, seed = Path(tmp) / "trial.gba", Path(tmp) / "seed.sav"
            rom.write_bytes(b"\0")
            seed.write_bytes(b"PROGRESS")
            with contextlib.redirect_stdout(io.StringIO()):
                log2_build.pair_save(rom, seed)
            self.assertEqual(rom.with_suffix(".sav").read_bytes(), b"PROGRESS")

    def test_pair_save_never_replaces_a_save_that_is_already_there(self):
        with tempfile.TemporaryDirectory() as tmp:
            rom, seed = Path(tmp) / "trial.gba", Path(tmp) / "seed.sav"
            rom.write_bytes(b"\0")
            seed.write_bytes(b"SEED")
            rom.with_suffix(".sav").write_bytes(b"MY REAL PROGRESS")
            with contextlib.redirect_stdout(io.StringIO()):
                log2_build.pair_save(rom, seed)
            self.assertEqual(rom.with_suffix(".sav").read_bytes(), b"MY REAL PROGRESS")

    def test_seed_save_picks_the_highest_main_build_and_skips_scenario_saves(self):
        seed = log2_build.seed_save()
        self.assertIsNotNone(seed, "no builds\log2_poc_r<N>.sav to seed from")
        self.assertRegex(seed.name, r"^log2_poc_r\d+\.sav$")
        numbers = [int(p.stem[len("log2_poc_r"):]) for p in (ROOT / "builds").glob("log2_poc_r*.sav")
                   if p.stem[len("log2_poc_r"):].isdigit()]
        self.assertEqual(int(seed.stem[len("log2_poc_r"):]), max(numbers))

    def test_the_save_option_reaches_build_as_a_keyword(self):
        with mock.patch.object(log2_build, "build") as fake:
            log2_build._main(["--list", "--out", "x.gba", "--save", "seed.sav"])
        base, out, names = fake.call_args.args
        self.assertEqual(fake.call_args.kwargs["save"], Path("seed.sav"))
