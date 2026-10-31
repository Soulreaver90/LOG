r"""
test_gi_post.py - Tests for gi_post.py (the gi post-processing chain) and the gohan_gi default art folders.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"
Needs art\gi_ssj2_v2\, gi_ssj_v2\, gi_ssj_v4\ and gi_ssj2_v4\ (py -3 -I scripts\permanent\art\gi_art.py all,
then gi_post.py all). The chain test runs the five steps on a copy in a temp folder and compares with those folders.
"""
import importlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from art import gi_post
import log_paths

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
GOLD = ART / "golden"
BELT = {26, 27}                                            # sash indices
STEP = (9, 0)                                              # anim 9, dir 0: the SSJ to SSJ2 step


# ===== helpers =====

def pixels(path: Path) -> tuple:
    with Image.open(path) as img:
        return img.size, img.getpalette(), img.tobytes()


def by_png(folder: Path) -> dict:
    return {e["png"]: e for e in json.loads((folder / "manifest.json").read_text())}


class GiPostTests(unittest.TestCase):
    def test_golden_idle_slots_equal_goldens(self):          # byte for byte, not a rule that comes close
        v2 = ART / "gi_ssj2_v2"
        for png, d in gi_post.GOLDEN.items():
            self.assertEqual(pixels(v2 / png), pixels(GOLD / f"golden_gi_ssj2_d{d}.png"), png)
        man = by_png(v2)
        for png in gi_post.GOLDEN:
            self.assertEqual((man[png]["w"], man[png]["h"]), (32, 32), png)
        status = {r["png"]: r["status"] for r in json.loads((v2 / "transplant.json").read_text())}
        self.assertEqual({status[p] for p in gi_post.GOLDEN}, {"golden"})

    def test_kept_frames_equal_the_source(self):             # powered-down frames keep the black hair
        v2, src = ART / "gi_ssj2_v2", ART / "gi_ssj2"
        man, src_man = by_png(v2), by_png(src)
        self.assertEqual(len(gi_post.KEEP), 5)
        for png in gi_post.KEEP:
            self.assertEqual(pixels(v2 / png), pixels(src / png), png)
            self.assertEqual(man[png]["keys"], src_man[png]["keys"], png)

    def test_body_rules_gate_counts_golden_changes(self):    # a rule that changes a golden frame must show in the gate
        gate = {}
        for d in (0, 1, 2, 3):
            with Image.open(GOLD / f"golden_gi_ssj2_d{d}.png") as img:
                out, n = gi_post.rules(img, d in (0, 1), d == 0)
            gate[d] = n
            self.assertEqual(out.tobytes() != img.tobytes(), n > 0, f"golden d{d}")
        with tempfile.TemporaryDirectory() as tmp, mock.patch("builtins.print"):
            shutil.copytree(GOLD, Path(tmp) / "golden")
            shutil.copytree(ART / "gi_ssj2_v2", Path(tmp) / "gi_ssj2_v2", ignore=shutil.ignore_patterns("review"))
            self.assertEqual(gi_post.body_rules(Path(tmp), apply=False)["gate"], gate)

    def test_gate_passes_on_all_goldens(self):               # the armpit exemption keeps my chest
        for d in (0, 1, 2, 3):
            with Image.open(GOLD / f"golden_gi_ssj2_d{d}.png") as img:
                self.assertEqual(gi_post.rules(img, d in (0, 1), d == 0)[1], 0, f"golden d{d}")

    def test_rules_would_change_the_ssj_goldens(self):       # why a shared gi_ssj body gets no R1/R2 (final, 2026-10-18)
        gate = {}
        for d in (0, 1):
            with Image.open(GOLD / f"golden_gi_ssj_d{d}.png") as img:
                gate[d] = gi_post.rules(img, True, d == 0)[1]
        self.assertEqual(gate, {0: 2, 1: 3})

    def test_body_rules_skip_shared_frames(self):            # SSJ and SSJ2 stay one body; own-body frames still change
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp)
            shutil.copytree(GOLD, art / "golden")
            shutil.copytree(ART / "gi_ssj2", art / "gi_ssj2")
            with mock.patch("builtins.print"):
                gi_post.transplant_heads(art)
                gi_post.finish_golden_slots(art)
                before = {p.name: p.read_bytes() for p in (art / "gi_ssj2_v2").glob("frame_*.png")}
                res = gi_post.body_rules(art)
            self.assertTrue(res["applied"])
            shared = {e["png"] for e in json.loads((art / "gi_ssj2_v2" / "manifest.json").read_text())
                      if e["body"] == "gi_ssj"}
            changed = {n for n, b in before.items() if (art / "gi_ssj2_v2" / n).read_bytes() != b}
            self.assertGreater(len(shared), 100)
            self.assertFalse(changed & shared, "body rules changed a shared gi_ssj body")
            self.assertTrue(changed, "the own-body frames still take R1/R2")

    def test_r2_changes_an_arm_line_and_spares_the_armpit(self):
        cells = {(3, 1): 211, (4, 1): 211}                    # collar: gi top is row 1, so R2 starts on row 3
        for y in (2, 3, 4):
            cells.update({(x, y): 88 for x in range(2, 6)})
        for y in (3, 4):
            cells.update({(1, y): 23, (6, y): 23})            # arm outline both sides

        def run(front):
            img = Image.new("P", (8, 6), 0)
            img.putpalette(list(range(256)) * 3)
            for q, v in cells.items():
                img.putpixel(q, v)
            out, _ = gi_post.rules(img, True, front)
            return out
        front, side = run(True), run(False)
        self.assertEqual(front.getpixel((2, 3)), 88, "armpit: first R2 row, arm on the image left, front view")
        self.assertEqual(side.getpixel((2, 3)), 211, "without the exemption the same pixel changes")
        self.assertEqual(front.getpixel((5, 3)), 211, "image-right arm on the armpit row still changes")
        self.assertEqual(front.getpixel((2, 4)), 211, "the row below the armpit still changes")

    def test_body_rules_gate_decides(self):                  # gate blocked: no byte of gi_ssj2_v2 changes
        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp)
            shutil.copytree(GOLD, art / "golden")
            shutil.copytree(ART / "gi_ssj2_v2", art / "gi_ssj2_v2", ignore=shutil.ignore_patterns("review"))
            with mock.patch("builtins.print"):
                res = gi_post.body_rules(art)
            self.assertEqual(res["applied"], not any(res["gate"].values()))
            if not res["applied"]:
                self.assertEqual(res["pixels"], 0)
                for p in (art / "gi_ssj2_v2").iterdir():
                    self.assertEqual(p.read_bytes(), (ART / "gi_ssj2_v2" / p.name).read_bytes(), p.name)
            for png, d in gi_post.GOLDEN.items():
                self.assertEqual(pixels(art / "gi_ssj2_v2" / png), pixels(GOLD / f"golden_gi_ssj2_d{d}.png"), png)

    def test_step_frames_keep_the_belt_row(self):            # the head grows, the body stays: dy -1 offsets the shift
        folder = ART / "gi_ssj_v2"
        rows = {}
        for e in json.loads((folder / "manifest.json").read_text()):
            for k in e["keys"]:
                if (k["anim"], k["dir"]) == STEP:
                    with Image.open(folder / e["png"]) as img:
                        b, w = img.tobytes(), img.width
                    belt = {i // w for i, v in enumerate(b) if v in BELT}
                    rows[k["index"]] = {k["dy"] + r for r in belt}
        self.assertEqual(sorted(rows), [0, 1, 2, 3])
        self.assertTrue(rows[0])
        for i in (1, 2, 3):
            self.assertEqual(rows[i], rows[0], f"frame {i}: belt left frame 0's screen row")

    def test_step_frames_only_frames_1_to_3_change(self):
        src, out = by_png(ART / "gi_ssj"), by_png(ART / "gi_ssj_v2")
        self.assertEqual(set(src), set(out))
        changed = {p for p in src if pixels(ART / "gi_ssj" / p) != pixels(ART / "gi_ssj_v2" / p)}
        hand = {p for p, e in out.items() if any(n.startswith("hand frame") for n in e.get("notes", []))}
        self.assertEqual(len(hand), 14)                              # r15 4 + r17 1 + r18 9: set 158 hand frames
        self.assertEqual(changed, set(gi_post.STEP_FRAMES) | hand)
        for p in gi_post.STEP_FRAMES:
            for k0, k1 in zip(src[p]["keys"], out[p]["keys"]):
                self.assertEqual(k1["dy"], k0["dy"] - 1, p)

    def test_chain_is_repeatable(self):                      # a fresh run on copies equals the folders on disk
        with tempfile.TemporaryDirectory() as tmp, mock.patch("builtins.print"):
            art = Path(tmp)
            for name in ("golden", "gi_ssj", "gi_ssj2", "gi_base"):          # gi_base: step 5, one body
                shutil.copytree(ART / name, art / name)
            gi_post.run_all(art)
            for name in ("gi_ssj2_v2", "gi_ssj_v2", "gi_ssj_v4", "gi_ssj2_v4"):
                mine = {p.name: p for p in (art / name).iterdir()}
                disk = {p.name: p for p in (ART / name).iterdir() if p.is_file()}
                self.assertEqual(set(mine), set(disk), name)
                for n, p in mine.items():
                    self.assertEqual(p.read_bytes(), disk[n].read_bytes(), f"{name}\\{n}")


class GohanGiDefaultTests(unittest.TestCase):
    def reload(self, env: dict):
        import patches.gohan_gi as gohan_gi
        clean = {k: v for k, v in os.environ.items() if k not in ("LOG_GI_SSJ", "LOG_GI_SSJ2")}
        with mock.patch.dict(os.environ, clean | env, clear=True):
            mod = importlib.reload(gohan_gi)
            sets = dict(mod.SETS)
        self.addCleanup(importlib.reload, gohan_gi)
        return sets

    def test_defaults_read_the_v2_and_aura_folders(self):   # 159 and 160: gi_aura.py output (aura-rage pass)
        sets = self.reload({})
        self.assertEqual(sets[157][0], "gi_base")
        self.assertEqual(sets[158][0], "gi_ssj_v2")
        self.assertEqual(sets[159], ("gi_ssj2_aura", 59))
        self.assertEqual(sets[160], ("gi_rage_aura", 58))

    def test_env_overrides_stay(self):
        sets = self.reload({"LOG_GI_SSJ": "gi_ssj", "LOG_GI_SSJ2": "gi_ssj2"})
        self.assertEqual((sets[158][0], sets[159][0]), ("gi_ssj", "gi_ssj2"))
        self.assertEqual(sets[157][0], "gi_base")


if __name__ == "__main__":
    unittest.main()
