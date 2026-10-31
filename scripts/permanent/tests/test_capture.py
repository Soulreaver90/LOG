r"""
test_capture.py - Tests for emu.capture (the BizHawk capture wrapper) and emu.actors (the RAM actor walk).

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_capture.py -v
No test starts an emulator. The timeout path is tested by making subprocess.run raise, and the actor walk by
a synthetic RAM dump built here, so the suite runs with no desktop session and no BizHawk install.
Expected values are restated here, never imported from the module under test.
"""
import json
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from emu import actors as actors_mod
from emu import capture

ROOT = Path(__file__).resolve().parents[3]
BUILDS = ROOT / "builds"
GOOD_ROM = BUILDS / "mockups" / "2026-10-25-chapter-cards" / "log2_poc_r40_chapters_v10.gba"

JOB = f"""
# a comment
name probe
rom {str(GOOD_ROM).replace(chr(92), '/')}
speed 400
timeout 120
wait 2100
press A 8
shot title
read 0x03000E90 8 head
savestate C:/tmp/none.State
end
"""


class TestJobParsing(unittest.TestCase):
    def test_a_good_job_parses_to_its_keys_and_steps(self):
        job = capture.parse_job(JOB)
        self.assertEqual(job.name, "probe")
        self.assertEqual(job.speed, 400)
        self.assertEqual(job.timeout, 120)
        self.assertEqual(Path(job.rom), GOOD_ROM)
        self.assertEqual([w for w, _ in job.steps],
                         ["wait", "press", "shot", "read", "savestate", "end"])
        self.assertEqual(job.steps[0][1], [2100])
        self.assertEqual(job.steps[1][1], ["A", 8])
        self.assertEqual(job.steps[3][1], [0x03000E90, 8, "head"])

    def test_a_comment_and_a_blank_line_are_ignored(self):
        job = capture.parse_job("# all comment\n\n   \nrom x.gba\nwait 1\nend\n")
        self.assertEqual(len(job.steps), 2)

    def test_the_steps_file_holds_one_step_a_line_with_forward_slashes(self):
        job = capture.parse_job(JOB)
        text = capture.job_steps_text(job)
        self.assertEqual(text.splitlines(),
                         ["wait 2100", "press A 8", "shot title", "read 50335376 8 head",
                          "savestate C:/tmp/none.State", "end"])
        self.assertNotIn("\\", text)

    def test_every_bad_job_is_refused_with_a_reason(self):
        bad = {
            "unknown word": "rom x.gba\nfly 3\nend\n",
            "unknown button": "rom x.gba\npress Jump 4\nend\n",
            "press needs two arguments": "rom x.gba\npress A\nend\n",
            "wait needs a count": "rom x.gba\nwait 0\nend\n",
            "read needs three arguments": "rom x.gba\nread 0x100 4\nend\n",
            "read width": "rom x.gba\nread 0x100 0 label\nend\n",
            "shot name": "rom x.gba\nshot a name\nend\n",
            "no rom": "wait 1\nend\n",
            "no end": "rom x.gba\nwait 1\n",
            "line after end": "rom x.gba\nwait 1\nend\nwait 1\n",
            "end takes nothing": "rom x.gba\nend now\n",
            "speed not a number": "rom x.gba\nspeed fast\nwait 1\nend\n",
            "speed too low": "rom x.gba\nspeed 0\nwait 1\nend\n",
        }
        for why, text in bad.items():
            with self.subTest(why=why):
                with self.assertRaises(ValueError):
                    capture.parse_job(text)


class TestRomGuard(unittest.TestCase):
    def test_a_rom_under_builds_is_accepted(self):
        self.assertEqual(capture.check_rom(GOOD_ROM), GOOD_ROM.resolve())

    def test_a_rom_outside_builds_is_refused(self):
        for path in (ROOT / "data" / "roms" / "base.gba", ROOT / "scratch" / "x.gba",
                     Path("C:/Temp/x.gba"), ROOT / "builds" / ".." / "data" / "x.gba"):
            with self.subTest(path=str(path)):
                with self.assertRaises(ValueError):
                    capture.check_rom(path)

    def test_a_file_under_builds_that_is_not_a_gba_is_refused(self):
        with self.assertRaises(ValueError):
            capture.check_rom(BUILDS / "log2_poc_r40.sav")

    def test_the_guard_can_be_pointed_at_another_builds_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "builds"
            root.mkdir()
            self.assertEqual(capture.check_rom(root / "a.gba", builds=root), (root / "a.gba").resolve())
            with self.assertRaises(ValueError):
                capture.check_rom(Path(tmp) / "a.gba", builds=root)


class TestConfigRewrite(unittest.TestCase):
    BASE = json.dumps({
        "PathEntries": {"Paths": [
            {"Type": "Base", "Path": "./GBA", "System": "GBA"},
            {"Type": "Save RAM", "Path": "./SaveRAM", "System": "GBA"},
            {"Type": "Base", "Path": "./NES", "System": "NES"}]},
        "SpeedPercent": 100, "ClockThrottle": True, "Unthrottled": False,
        "SoundEnabled": True, "KeepThisKey": 7})

    def rewrite(self, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "bizbase"
            out = json.loads(capture.rewrite_config(self.BASE, base, 400, Path(tmp), **kw))
            return out, base

    def test_the_gba_base_path_becomes_an_absolute_project_path(self):
        cfg, base = self.rewrite()
        gba = [e for e in cfg["PathEntries"]["Paths"] if e["System"] == "GBA" and e["Type"] == "Base"][0]
        self.assertEqual(gba["Path"], str(base.resolve()))
        self.assertTrue(Path(gba["Path"]).is_absolute())

    def test_no_other_system_and_no_other_key_is_touched(self):
        cfg, _ = self.rewrite()
        nes = [e for e in cfg["PathEntries"]["Paths"] if e["System"] == "NES"][0]
        self.assertEqual(nes["Path"], "./NES")
        self.assertEqual(cfg["KeepThisKey"], 7)

    def test_the_throttle_is_off_by_default_and_kept_when_asked(self):
        fast, _ = self.rewrite()
        self.assertTrue(fast["Unthrottled"])
        self.assertFalse(fast["ClockThrottle"])
        slow, _ = self.rewrite(throttled=True)
        self.assertFalse(slow["Unthrottled"])
        self.assertTrue(slow["ClockThrottle"])
        self.assertEqual(slow["SpeedPercent"], 400)

    def test_a_config_with_no_gba_base_entry_is_refused(self):
        text = json.dumps({"PathEntries": {"Paths": [{"Type": "ROM", "Path": ".", "System": "GBA"}]}})
        with self.assertRaises(ValueError):
            capture.rewrite_config(text, Path("C:/x"), 100, Path("C:/y"))


class TestSaveRamSeed(unittest.TestCase):
    def test_bizhawk_names_the_file_after_the_rom_with_spaces(self):
        self.assertEqual(capture.biz_saveram_name(Path("C:/a/log2_poc_r40_chapters_v10.gba")),
                         "log2 poc r40 chapters v10.SaveRAM")

    def test_the_seed_is_copied_byte_for_byte_under_that_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            seed = tmp / "s.sav"
            seed.write_bytes(bytes(range(256)) * 32)
            out = capture.seed_saveram(seed, Path("C:/a/log2_poc_r40.gba"), tmp / "bizbase")
            self.assertEqual(out.name, "log2 poc r40.SaveRAM")
            self.assertEqual(out.read_bytes(), seed.read_bytes())

    def test_padding_fills_with_ff_and_never_shortens(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            seed = tmp / "s.sav"
            seed.write_bytes(b"\x01\x02")
            out = capture.seed_saveram(seed, Path("C:/a/r.gba"), tmp / "b", pad_to=8)
            self.assertEqual(out.read_bytes(), b"\x01\x02" + b"\xff" * 6)
            out2 = capture.seed_saveram(seed, Path("C:/a/r.gba"), tmp / "b", pad_to=1)
            self.assertEqual(out2.read_bytes(), b"\x01\x02")


class TestSavestateGuard(unittest.TestCase):
    def test_an_existing_savestate_target_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a.State"
            target.write_bytes(b"x")
            job = capture.parse_job(f"rom {str(GOOD_ROM).replace(chr(92), '/')}\n"
                                    f"savestate {str(target).replace(chr(92), '/')}\nend\n")
            with self.assertRaises(FileExistsError):
                capture.check_savestates(job)

    def test_a_free_savestate_target_is_returned(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "new.State"
            job = capture.parse_job(f"rom {str(GOOD_ROM).replace(chr(92), '/')}\n"
                                    f"savestate {str(target).replace(chr(92), '/')}\nend\n")
            self.assertEqual(capture.check_savestates(job), [target])


class TestInstallWatch(unittest.TestCase):
    def test_a_file_written_after_the_marker_is_reported_and_an_old_one_is_not(self):
        import os
        import time
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            old = tmp / "old.txt"
            old.write_text("old")
            os.utime(old, (1000, 1000))
            marker = time.time() - 1
            self.assertEqual(capture.install_writes(marker, install=tmp), [])
            new = tmp / "sub" / "new.txt"
            new.parent.mkdir()
            new.write_text("new")
            self.assertEqual(capture.install_writes(marker, install=tmp), [new])


class TestResultParsing(unittest.TestCase):
    GOOD = ("# speed 400\n"
            "1 2101 wait 2100\n"
            "2 2101 shot title shots/title.png\n"
            "3 2101 read head 0x03000E90 0001066301000000\n"
            "4 2101 read ewram 0x02000000 file:ewram.bin:262144\n"
            "5 2101 end\n"
            "# frames 2100 seconds 2.25 fps 933.3\n"
            "# done ok=true\n")

    def write(self, tmp, text):
        path = Path(tmp) / "result.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def test_shots_and_reads_are_pulled_out_of_the_result_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            lines, shots, reads, ok, ended = capture.parse_result(self.write(tmp, self.GOOD))
            self.assertEqual(len(lines), 8)
            self.assertEqual(shots, ["title"])
            self.assertEqual(reads["head"], "0001066301000000")
            self.assertEqual(reads["ewram"], "file:ewram.bin:262144")
            self.assertTrue(ok)
            self.assertTrue(ended)

    def test_a_lua_error_is_reported_although_bizhawk_exits_zero(self):
        broken = ("1 2101 wait 2100\n"
                  "# error capture.lua:60: unknown step: fly\n"
                  "# frames 2100 seconds 2.25 fps 933.3\n"
                  "# done ok=false\n")
        with tempfile.TemporaryDirectory() as tmp:
            _lines, _shots, _reads, ok, ended = capture.parse_result(self.write(tmp, broken))
            self.assertFalse(ok)
            self.assertFalse(ended)

    def test_a_run_that_stops_before_its_end_step_is_not_clean(self):
        cut = "1 2101 wait 2100\n2 2101 shot a shots/a.png\n"
        with tempfile.TemporaryDirectory() as tmp:
            _lines, _shots, _reads, ok, ended = capture.parse_result(self.write(tmp, cut))
            self.assertFalse(ok)
            self.assertFalse(ended)

    def test_a_missing_result_file_gives_empty_artifacts(self):
        self.assertEqual(capture.parse_result(Path("C:/no/such/result.txt")), ([], [], {}, False, False))

    def test_a_result_is_good_only_when_every_signal_agrees(self):
        base = dict(exit_code=0, timed_out=False, lua_ok=True, ended=True)
        self.assertTrue(capture.Result(**base).good)
        for key, bad in (("exit_code", 1), ("timed_out", True), ("lua_ok", False), ("ended", False)):
            with self.subTest(key=key):
                self.assertFalse(capture.Result(**{**base, key: bad}).good)
        self.assertFalse(capture.Result(**base, install_writes=[Path("x")]).good)


class TestTimeoutPath(unittest.TestCase):
    def test_a_timeout_is_reported_and_the_process_is_killed(self):
        job = capture.parse_job(JOB)
        job.timeout = 1
        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "", "")

        class FakePopen:
            pid = 4242

            def __init__(self, cmd, **kw):
                self.calls = 0

            def communicate(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired("EmuHawk.exe", 1)
                return ("", "")

            returncode = None

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(capture.subprocess, "Popen", FakePopen), \
                 mock.patch.object(capture.subprocess, "run", side_effect=fake_run), \
                 mock.patch.object(capture, "install_writes", return_value=[]):
                res = capture.run(job, run_dir=Path(tmp) / "run")
            self.assertTrue(res.timed_out)
            self.assertIsNone(res.exit_code)
            self.assertFalse(res.good)
            kill = [c for c in calls if "taskkill" in c[0]]
            self.assertEqual(len(kill), 1)
            self.assertIn("/PID", kill[0])
            self.assertIn(str(FakePopen.pid), kill[0])
            self.assertNotIn("/IM", kill[0])        # never kill every EmuHawk on the machine
            self.assertTrue((Path(res.run_dir) / "steps.txt").exists())
            self.assertTrue((Path(res.run_dir) / "config.ini").exists())
            self.assertTrue((Path(res.run_dir) / "run.lua").exists())
            self.assertEqual(res.lines, [])


# ===== the actor walk, on a synthetic dump =====
SET_LITERAL = 0x959C
TABLE_AT = 0x08800000
ROM_LEN = 0x810000
FIRST_SET = 0x08000100
SET_STEP = 0x40


def fake_rom():
    rom = bytearray(b"\x00" * ROM_LEN)
    struct.pack_into("<I", rom, SET_LITERAL, TABLE_AT)
    for i in range(154):                                   # ids 7 to 160
        struct.pack_into("<I", rom, TABLE_AT - 0x08000000 + 4 * i, FIRST_SET + SET_STEP * i)
    return bytes(rom)


def set_addr(set_id):
    return FIRST_SET + SET_STEP * (set_id - 7)


def fake_mem(objects, player=0):
    """objects: [(pointer, set id, x, y, facing)] in the world's first list.

    IWRAM offsets: world 0x03001120 is offset 0x1120, so the count is 0x1124, the list 0x1128, the second
    list 0x152C, and the player pointer 0x03001FA8 is offset 0x1FA8.
    """
    ewram = bytearray(0x40000)
    iwram = bytearray(0x8000)
    struct.pack_into("<I", iwram, 0x1124, len(objects))
    for i, (ptr, _sid, _x, _y, _f) in enumerate(objects):
        struct.pack_into("<I", iwram, 0x1128 + 4 * i, ptr)
    struct.pack_into("<I", iwram, 0x1FA8, player)
    for ptr, sid, x, y, f in objects:
        off = ptr - 0x02000000
        ewram[off + 0x10] = f
        struct.pack_into("<I", ewram, off + 0x48, set_addr(sid))
        struct.pack_into("<i", ewram, off + 0x158, x << 8)
        struct.pack_into("<i", ewram, off + 0x15C, y << 8)
    return actors_mod.Mem([(0x02000000, bytes(ewram)), (0x03000000, bytes(iwram))])


class TestActorWalk(unittest.TestCase):
    def test_the_set_table_maps_an_address_to_its_set_id(self):
        ids = actors_mod.set_ids(fake_rom())
        self.assertEqual(ids[set_addr(7)], 7)
        self.assertEqual(ids[set_addr(53)], 53)
        self.assertEqual(ids[set_addr(160)], 160)
        self.assertEqual(len(ids), 154)

    def test_each_actor_decodes_to_its_spot_facing_set_and_name(self):
        objs = [(0x02031984, 103, 120, 44, 1), (0x02032238, 53, 120, 84, 3),
                (0x02032BA4, 137, 44, 84, 2), (0x02033120, 128, 24, 84, 3),
                (0x02031AF8, 121, 96, 44, 1), (0x02031C6C, 76, 136, 32, 2)]
        found = actors_mod.walk(fake_mem(objs, player=0x02032238), fake_rom())
        got = {a.name: (a.x, a.y, a.face_name, a.is_player) for a in found}
        self.assertEqual(got, {"Piccolo": (120, 44, "up", False), "Gohan": (120, 84, "right", True),
                               "Vegeta": (44, 84, "left", False), "Trunks": (24, 84, "right", False),
                               "Tien": (96, 44, "up", False), "Krillin": (136, 32, "left", False)})

    def test_the_spot_is_the_anchor_shifted_down_eight_bits(self):
        mem = fake_mem([(0x02010000, 53, 255, 1, 0)])
        actor = actors_mod.walk(mem, fake_rom())[0]
        self.assertEqual((actor.x, actor.y), (255, 1))
        self.assertEqual(mem.u32(0x02010000 + 0x158), 255 << 8)

    def test_an_object_with_no_sprite_set_is_skipped(self):
        mem = fake_mem([(0x02010000, 53, 10, 10, 0)])
        ewram = bytearray(mem.regions[0][1])
        struct.pack_into("<I", ewram, 0x11000 + 0x48, 0x08123456)        # not a set table address
        iwram = bytearray(mem.regions[1][1])
        struct.pack_into("<I", iwram, 0x1128 + 4, 0x02011000)
        struct.pack_into("<I", iwram, 0x1124, 2)
        mem2 = actors_mod.Mem([(0x02000000, bytes(ewram)), (0x03000000, bytes(iwram))])
        self.assertEqual([a.name for a in actors_mod.walk(mem2, fake_rom())], ["Gohan"])

    def test_a_null_or_out_of_range_list_entry_is_skipped(self):
        mem = fake_mem([(0x02010000, 53, 10, 10, 0)])
        iwram = bytearray(mem.regions[1][1])
        struct.pack_into("<I", iwram, 0x1128 + 4, 0x00000000)
        struct.pack_into("<I", iwram, 0x1128 + 8, 0x0FFFFFF0)
        struct.pack_into("<I", iwram, 0x1124, 3)
        mem2 = actors_mod.Mem([(0x02000000, mem.regions[0][1]), (0x03000000, bytes(iwram))])
        self.assertEqual(len(actors_mod.walk(mem2, fake_rom())), 1)

    def test_the_same_object_in_both_lists_is_reported_once(self):
        mem = fake_mem([(0x02010000, 53, 10, 10, 0)])
        iwram = bytearray(mem.regions[1][1])
        struct.pack_into("<I", iwram, 0x152C, 0x02010000)                # world + 0x40C, the second list
        mem2 = actors_mod.Mem([(0x02000000, mem.regions[0][1]), (0x03000000, bytes(iwram))])
        self.assertEqual(len(actors_mod.walk(mem2, fake_rom())), 1)

    def test_the_rows_name_every_actor_and_mark_the_player(self):
        found = actors_mod.walk(fake_mem([(0x02010000, 53, 10, 10, 3)], player=0x02010000), fake_rom())
        rows = actors_mod.table(found)
        self.assertEqual(len(rows), 3)
        self.assertIn("Gohan", rows[2])
        self.assertIn("(10,10)", rows[2])
        self.assertIn("right", rows[2])
        self.assertTrue(rows[2].rstrip().endswith("yes |"))


if __name__ == "__main__":
    unittest.main()
