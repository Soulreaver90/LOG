r"""
test_one_body.py - Tests for gi_one_body.py (one body: sets 158 and 159 from the base body) and the v4 aura.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent
Needs art\gi_ssj_v4\, gi_ssj2_v4\ (gi_post.py all, step 5) and gi_ssj2_aura_v4\ (gi_aura.py all).
The key lists below are explicit on purpose: a key that changes class must show up as a test failure.
"""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from art import gi_art
from art import gi_aura
from art import gi_one_body
from art import hand_frames
import log_paths

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
SPR = log_paths.SPRITES
OUTS = {"gi_ssj_v4": ("gi_ssj_v2", ["set59"]), "gi_ssj2_v4": ("gi_ssj2_v2", ["set58", "set59"])}


def keys(text: str) -> set:
    return {tuple(int(n) for n in k.split(".")) for k in text.split()}


ANIM16 = keys("16.0.1 16.0.2 16.0.3 16.1.1 16.1.2 16.1.3 16.1.4 16.2.1 16.2.2 16.2.3 16.2.4 16.3.1 16.3.2 16.3.3 "
              "16.3.4")
REVERT_KEPT = {(21, d, i) for d in range(4) for i in range(3)}      # power-down pose: no clear base body
REVERT_MATCH = {(21, d, 3): (0, 0, 0) for d in range(4)}            # standing: the base idle body
ANCHOR_159 = {(20, d, i): (0, 2) for d in (0, 2) for i in range(4)}   # 159 flight head placed high by the transplant
STEP = {(9, d, i) for d in range(4) for i in (1, 2, 3)}              # 158 SSJ to SSJ2 step: golden SSJ2 head
KEPT = {   # every key that is not derived, by class (my rules 2026-10-22 and 2026-10-23)
    "gi_ssj_v4": {"vanilla pose": ANIM16,
                  "box": keys("4.1.3 6.0.0 7.0.0 13.0.3"),
                  "no base": REVERT_KEPT},
    "gi_ssj2_v4": {"exception": {(0, d, i) for d in range(4) for i in range(2)},     # SSJ2 idle (std golden)
                   "vanilla pose": ANIM16 | {(4, d, i) for d in range(4) for i in range(4)},   # 4: SSJ2 rage stance
                   "box": keys("6.0.0 7.0.0"),
                   "no base": REVERT_KEPT}}
NO_COLLAR = {(3, d, i) for d in range(4) for i in (2, 3)}            # lying down: no gi under the head
BOLT = {gi_aura.BLUE, gi_aura.WHITE}


# ===== helpers =====

def report(out: str) -> dict:
    return json.loads((ART / out / "one_body.json").read_text(encoding="ascii"))["keys"]


def tables(out: str) -> dict:
    src, sets = OUTS[out]
    return {"base": gi_art.by_key(ART / "gi_base"), "now": gi_art.by_key(ART / src), "new": gi_art.by_key(ART / out),
            "v56": gi_art.by_key(SPR / "set56"), "vform": [gi_art.by_key(SPR / s) for s in sets]}


def derived(out: str):
    """(key, base key, report row) of every derived key."""
    for ks, r in report(out).items():
        if r["class"] == "derived":
            k = tuple(int(n) for n in ks.split("."))
            yield k, gi_one_body.base_key(out, k), r


def chin_row(t: dict, k: tuple, bk: tuple, shift: tuple) -> int:
    """The lowest row of the vanilla base head and the vanilla form head moved by the head shift."""
    base = gi_art.head_mask(gi_art.frame_pixels(t["v56"][bk]))
    form = gi_art.head_mask(gi_art.frame_pixels(gi_one_body.vanilla_form(k, t["vform"])))
    return max(max(y for _, y in base), max(y + shift[1] for _, y in form))


def eye(px: dict, p: tuple) -> bool:
    return px[p] in gi_art.WRISTBAND and any(px.get(q) in gi_one_body.IRIS for q in gi_art.neighbours(p, diag=True))


class OneBodyTests(unittest.TestCase):
    def test_kept_keys_are_listed(self):                     # the exception and vanilla-differs lists, explicit
        for out, classes in KEPT.items():
            got = {}
            for k, r in report(out).items():
                got.setdefault(r["class"], set()).add(tuple(int(n) for n in k.split(".")))
            self.assertEqual({c: v for c, v in got.items() if c != "derived"}, classes, out)

    def test_pinned_lists(self):                             # me, 2026-10-23: box keys, revert, head anchors
        self.assertEqual({o: set(v) for o, v in gi_one_body.KEPT_BOX.items()},
                         {o: KEPT[o]["box"] for o in KEPT})
        self.assertEqual(gi_one_body.EXCEPTIONS["gi_ssj_v4"], {})
        self.assertEqual(gi_one_body.HEAD_ANCHOR, {"gi_ssj_v4": {}, "gi_ssj2_v4": ANCHOR_159})
        for out in OUTS:
            self.assertEqual(gi_one_body.POSE_MATCH[out], REVERT_MATCH)
            rep = report(out)
            for k, bk in REVERT_MATCH.items():               # a clear match: shape residual well under POSE_LIMIT
                r = rep[gi_art.key_str(k)]
                self.assertEqual((r["class"], r["base_key"]), ("derived", gi_art.key_str(bk)))
                self.assertLessEqual(r["residual"][0], 8, k)

    def test_body_below_the_head_equals_base(self):          # My rule: the body is the base body
        for out in OUTS:
            t = tables(out)
            for k, bk, r in derived(out):
                row = chin_row(t, k, bk, tuple(r["head_shift"]))
                base = {p: v for p, v in gi_art.frame_pixels(t["base"][bk]).items() if p[1] > row}
                new = {p: v for p, v in gi_art.frame_pixels(t["new"][k]).items() if p[1] > row}
                bad = {p for p in set(base) | set(new) if base.get(p) != new.get(p)
                       and new.get(p) not in gi_one_body.ON_TOP}    # form hair, sparks, irises may hang over
                lost = len(bad) <= r["clipped_specks"] and all(p not in new for p in bad)
                self.assertTrue(not bad or lost, f"{out} {gi_art.key_str(k)}: {sorted(bad)[:6]}")

    def test_collar_and_neck_rows_are_base(self):            # every row, the neck and collar rows included
        for out in OUTS:
            t = tables(out)
            for k, bk, r in derived(out):
                b, new = gi_art.frame_pixels(t["base"][bk]), gi_art.frame_pixels(t["new"][k])
                head = gi_art.head_mask(gi_art.frame_pixels(t["v56"][bk]))
                gi = gi_one_body.torso(b, head)
                low = max(y for _, y in head)
                band = {p for p in gi if low - 2 <= p[1] <= low + 3}       # the collar band under the head
                self.assertEqual(not band, k in NO_COLLAR, f"{out} {gi_art.key_str(k)}: collar band")
                bad = {p for p in gi if new.get(p) != b[p] and new.get(p) not in gi_one_body.ON_TOP}
                bad |= {p for p, v in new.items() if v in gi_one_body.BODY and b.get(p) != v   # no form gi, except
                        and not (p in head and b.get(p) not in gi_one_body.NECK)   # where base hair covered the body
                        and not eye(new, p)}                                         # a 195 eye pixel (18.x)
                self.assertFalse(bad, f"{out} {gi_art.key_str(k)}: {sorted(bad)[:6]}")
                sash = {p for p, v in b.items() if v in gi_art.RED}                  # the sash never changes
                self.assertEqual({p for p in sash if new.get(p) != b[p]}, set(), f"{out} {gi_art.key_str(k)}: sash")

    def test_step_frames_keep_the_golden_head(self):         # 158 anim 9 indices 1-3: base body, golden SSJ2 head
        t, rep = tables("gi_ssj_v4"), report("gi_ssj_v4")
        for k in sorted(STEP):
            r = rep[gi_art.key_str(k)]
            self.assertEqual(r["class"], "derived", k)
            sx, sy = r["head_shift"]
            now, new = gi_art.frame_pixels(t["now"][k]), gi_art.frame_pixels(t["new"][k])
            vf = gi_art.frame_pixels(gi_one_body.vanilla_form(k, t["vform"]))
            hair = {p for p in gi_one_body.form_head(now, vf) if now[p] in gi_one_body.HAIR}
            self.assertGreater(len(hair), 150, k)
            self.assertEqual({p: now[p] for p in hair}, {p: new.get((p[0] + sx, p[1] + sy)) for p in hair}, k)

    def test_flight_has_the_base_sash(self):                 # anim 20: my diagonal sash (r17) everywhere
        for out in OUTS:
            t = tables(out)
            for k in [(20, d, i) for d in range(4) for i in range(4)]:
                sash = {p for p, v in gi_art.frame_pixels(t["base"][k]).items() if v in gi_art.RED}
                new = gi_art.frame_pixels(t["new"][k])
                self.assertTrue(sash)
                self.assertEqual({p for p in sash if new.get(p) in gi_art.RED}, sash, (out, k))

    def test_boot_gray_carries_through_base(self):           # r19 fix: base 12.0.x never had the armor gray
        t = tables("gi_ssj_v4")
        for i in range(4):
            self.assertNotIn(12, gi_art.frame_pixels(t["base"][(12, 0, i)]).values())
            self.assertNotIn(12, gi_art.frame_pixels(t["new"][(12, 0, i)]).values(), i)

    def test_kept_keys_show_todays_frame(self):
        for out, today in (("gi_ssj_v4", "gi_ssj_v2"), ("gi_ssj2_aura_v4", "gi_ssj2_aura")):
            rep = report("gi_ssj_v4" if out == "gi_ssj_v4" else "gi_ssj2_v4")
            a, b = gi_art.by_key(ART / out), gi_art.by_key(ART / today)
            for k in b:
                rk = (0, k[1], k[2] // 3) if out == "gi_ssj2_aura_v4" and k[0] == 0 else k
                if rep[gi_art.key_str(rk)]["class"] != "derived":
                    self.assertEqual(gi_art.frame_pixels(a[k]), gi_art.frame_pixels(b[k]), (out, k))

    def test_frames_keep_size_name_and_order(self):          # no allocation of the build moves
        for out, today in (("gi_ssj_v4", "gi_ssj_v2"), ("gi_ssj2_aura_v4", "gi_ssj2_aura")):
            new, old = gi_art.load_manifest(ART / out), gi_art.load_manifest(ART / today)
            self.assertEqual([e["png"] for e in new], [e["png"] for e in old], out)
            for e, f in zip(new, old):
                with Image.open(ART / out / e["png"]) as a, Image.open(ART / today / f["png"]) as b:
                    self.assertEqual(a.size, b.size, e["png"])
                for k, j in zip(e["keys"], f["keys"]):
                    self.assertEqual({x: k[x] for x in ("anim", "dir", "index", "w", "h", "attr0", "attr1")},
                                     {x: j[x] for x in ("anim", "dir", "index", "w", "h", "attr0", "attr1")})
                    self.assertLessEqual(abs(k["dx"] - j["dx"]) + abs(k["dy"] - j["dy"]), 2 * gi_one_body.SPAN)

    def test_aura_adds_only_bolts_to_the_body(self):          # order: base body, derived SSJ2 body, bolts
        body, aura = gi_art.by_key(ART / "gi_ssj2_v4"), gi_art.by_key(ART / "gi_ssj2_aura_v4")
        rep = report("gi_ssj2_v4")
        for k, rec in aura.items():
            if k[0] == 0 or rep[gi_art.key_str(k)]["class"] != "derived":
                continue
            a, b = gi_art.frame_pixels(rec), gi_art.frame_pixels(body[k])
            self.assertTrue(all(a.get(p) in BOLT for p in set(a) | set(b) if a.get(p) != b.get(p)), k)

    def test_hand_lists(self):
        self.assertEqual(hand_frames.DERIVED["gi_ssj_v4"], [])
        self.assertEqual(set(hand_frames.DERIVED["gi_ssj2_aura_v4"]),
                         {k for k in hand_frames.HAND["gi_ssj2_aura"] if k in KEPT["gi_ssj2_v4"]["vanilla pose"]})
        self.assertEqual(len(hand_frames.GOLDEN_HAND), len(set(hand_frames.GOLDEN_HAND)))


class OneBodyRunTests(unittest.TestCase):
    def test_fresh_run_equals_the_folders(self):             # gi_one_body and the v4 aura are deterministic
        with tempfile.TemporaryDirectory() as tmp, mock.patch("builtins.print"):
            art = Path(tmp)
            for name in ("gi_base", "gi_ssj_v2", "gi_ssj2_v2"):
                shutil.copytree(ART / name, art / name)
            gi_one_body.run_all(art)
            for name, (body, idle, layout, tag, ring) in gi_aura.V4_OUTPUTS.items():
                gi_aura.aura_folder(art / body, art / name, idle, tag, layout, art / ring)
            for name in ("gi_ssj_v4", "gi_ssj2_v4", "gi_ssj2_aura_v4"):
                mine = {p.name: p.read_bytes() for p in (art / name).iterdir()}
                disk = {p.name: p.read_bytes() for p in (ART / name).iterdir() if p.is_file()}
                self.assertEqual(set(mine), set(disk), name)
                self.assertFalse([n for n in mine if mine[n] != disk[n]], name)

    def test_ring_on_its_own_body_changes_nothing(self):     # the ring path gives today's bolts on today's body
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gi_ssj2_aura"
            body, idle, layout = gi_aura.OUTPUTS["gi_ssj2_aura"]
            gi_aura.aura_folder(ART / body, out, idle, "gi_ssj2_aura", layout, ART / body)
            mine = {p.name: p.read_bytes() for p in out.iterdir()}
            disk = {p.name: p.read_bytes() for p in (ART / "gi_ssj2_aura").iterdir() if p.is_file()}
            self.assertEqual(mine, disk)


if __name__ == "__main__":
    unittest.main()
