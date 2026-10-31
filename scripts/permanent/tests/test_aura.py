r"""
test_aura.py - Tests for gi_aura.py: the outline aura on the gi SSJ2 (set 159) and gi Rage (set 160) frames.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Needs art\gi_ssj2_aura\ and gi_rage_aura\ (py -3 -I scripts\permanent\art\gi_aura.py all).
The reference test reads my approved mockups aura2_outline_d0..d2.gif (6x, lime). A GIF quantizes and
the mask resize blends edge pixels, so each 6x6 cell is read at its center and classed to the nearest color the
baked frame uses (lime for 0). Columns 0-3 match in every dir; d0 columns 4 and 5 differ only on rows 9-11,
which the current bolts.py face box (5 rows up, edited after the GIFs were made) keeps free.
"""
import json
import random
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from art import gi_aura
from art.gi_review import BACKGROUND
import log_paths

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
GOLDEN = ART / "golden"
OUTS = {"gi_ssj2_aura": "gi_ssj2_v2", "gi_rage_aura": "gi_rage"}
BOLT = {gi_aura.BLUE, gi_aura.WHITE}


def manifest(name: str) -> list:
    return json.loads((ART / name / "manifest.json").read_text(encoding="ascii"))


def hand(e: dict) -> bool:
    """A reviewed r12fix hand frame (hand_frames.py, r15): it replaces the baked frame, bolts and all."""
    return any(n.startswith("hand frame") for n in e.get("notes", []))


def px_of(path: Path) -> tuple:
    with Image.open(path) as im:
        return im.tobytes(), im.getpalette(), im.size


def body_path(out: str, entry: dict) -> Path:
    src = entry["aura"]["body"]
    return GOLDEN / src if src.startswith("golden_") else ART / OUTS[out] / src


def gif_classes(gif: Image.Image, frame: int, baked: bytes, pal: list) -> list:
    """Per source pixel: True when the GIF cell center is nearest to the color the baked index shows."""
    gif.seek(frame)
    rgb = gif.convert("RGB")
    color = lambda v: BACKGROUND if v == 0 else tuple(pal[3 * v:3 * v + 3])   # noqa: E731
    cands = {color(v) for v in set(baked) | {0}}
    out = []
    for i, v in enumerate(baked):
        c = rgb.getpixel(((i % 32) * 6 + 3, (i // 32) * 6 + 3))
        out.append(min(cands, key=lambda q: sum((a - b) ** 2 for a, b in zip(c, q))) == color(v))
    return out


class AuraPortTests(unittest.TestCase):
    def test_port_matches_the_owner_gifs(self):
        pats = gi_aura.reference_patterns()
        for d in (0, 1, 2):
            px, pal, _ = px_of(GOLDEN / f"golden_gi_ssj2_d{d}.png")
            with Image.open(gi_aura.REF_DIR / f"aura2_outline_d{d}.gif") as gif:
                self.assertEqual(gif.n_frames, gi_aura.REF_COLUMNS)
                oks = [gif_classes(gif, c, gi_aura.bake(px, pats[c][d], pal), pal) for c in range(gi_aura.REF_COLUMNS)]
            for c, ok in enumerate(oks):
                bad = [(i % 32, i // 32) for i, good in enumerate(ok) if not good]
                if d == 0 and c in (4, 5):                   # rows the current face box keeps free (see header)
                    self.assertTrue(all(9 <= y <= 11 for _, y in bad), (d, c, bad))
                    self.assertLessEqual(len(bad), 7, (d, c))
                else:
                    self.assertEqual(bad, [], (d, c))

    def test_face_box_never_gets_a_bolt(self):
        px = bytearray(32 * 32)
        px[14 * 32 + 12] = px[14 * 32 + 18] = 64            # two irises
        face = gi_aura.face_box(bytes(px))
        self.assertEqual((min(face), max(face)), ((9, 9), (21, 17)))
        everywhere = {(x, y): gi_aura.WHITE for x in range(32) for y in range(32)}
        out = gi_aura.bake(bytes(px), everywhere, [0] * 768)
        for x, y in face:
            self.assertEqual(out[y * 32 + x], px[y * 32 + x], (x, y))

    def test_white_over_bright_turns_blue(self):
        pal = [0] * 768
        pal[3 * 2:3 * 2 + 3], pal[3 * 20:3 * 20 + 3], pal[3 * 89:3 * 89 + 3] = [248] * 3, [248, 216, 0], [96, 0, 136]
        px = bytes([20, 89, 0] + [0] * (32 * 32 - 3))
        out = gi_aura.bake(px, {(0, 0): gi_aura.WHITE, (1, 0): gi_aura.WHITE, (2, 0): gi_aura.WHITE}, pal)
        self.assertEqual(out[:3], bytes([gi_aura.BLUE, gi_aura.WHITE, gi_aura.WHITE]))

    def test_outline_is_deterministic_and_starts_on_the_ring(self):
        px, _, _ = px_of(GOLDEN / "golden_gi_ssj2_d0.png")
        a, b = gi_aura.outline(random.Random(5), px), gi_aura.outline(random.Random(5), px)
        self.assertEqual(a, b)
        self.assertTrue(set(gi_aura.silhouette(px)) & set(a))
        self.assertLessEqual(set(a.values()), BOLT)


class AuraFolderTests(unittest.TestCase):
    def test_folders_reproduce(self):                     # gi_aura.py all on disk equals a fresh run
        with tempfile.TemporaryDirectory() as tmp:
            for out, (body, idle, layout) in gi_aura.OUTPUTS.items():
                gi_aura.aura_folder(ART / body, Path(tmp) / out, idle, out, layout)
                mine = {p.name: p.read_bytes() for p in (Path(tmp) / out).iterdir()}
                disk = {p.name: p.read_bytes() for p in (ART / out).iterdir() if p.is_file()}
                self.assertEqual(set(mine), set(disk), out)
                self.assertFalse([n for n in mine if mine[n] != disk[n]], out)

    def test_bolts_only_add_bolt_colors_off_the_face(self):
        for out in OUTS:
            for e in manifest(out):
                if "aura" not in e or hand(e):
                    continue
                got, pal, (w, h) = px_of(ART / out / e["png"])
                body, _, size = px_of(body_path(out, e))
                self.assertEqual(size, (w, h))
                face = gi_aura.face_box(body, w)
                changed = [i for i in range(w * h) if got[i] != body[i]]
                self.assertTrue(changed, e["png"])
                for i in changed:
                    self.assertIn(got[i], BOLT, e["png"])
                    self.assertNotIn((i % w, i // w), face, e["png"])
                    if got[i] == gi_aura.WHITE and body[i]:
                        self.assertLessEqual(sum(pal[3 * body[i]:3 * body[i] + 3]), gi_aura.BRIGHT, e["png"])

    def test_frames_without_aura_are_the_body_bytes(self):
        for out, body in OUTS.items():
            for e in manifest(out):
                if "aura" not in e and not hand(e):
                    self.assertEqual((ART / out / e["png"]).read_bytes(), (ART / body / e["png"]).read_bytes())
                    self.assertFalse({k["anim"] for k in e["keys"]} & {0, 1, 4, 13}, e["png"])

    def test_idle_is_body_times_3_plus_shape(self):
        for out in OUTS:
            keys = {(k["anim"], k["dir"], k["index"]): e for e in manifest(out) for k in e["keys"]}
            for d in range(4):
                self.assertEqual(sorted(i for (a, dd, i) in keys if (a, dd) == (0, d)), list(range(6)), (out, d))
                for b in range(2):
                    for s in range(3):
                        pid = keys[(0, d, b * 3 + s)]["aura"]["pattern"]
                        self.assertEqual(pid, f"idle_d{2 if d == 3 else d}_s{s}", (out, d, b, s))

    def test_rage_idle_shapes_are_the_owner_columns(self):    # set 160 body 0 = the reference body
        pats = gi_aura.reference_patterns()
        keys = {(k["anim"], k["dir"], k["index"]): e for e in manifest("gi_rage_aura") for k in e["keys"]}
        for d in (0, 1, 2):
            gold, pal, _ = px_of(GOLDEN / f"golden_gi_ssj2_d{d}.png")
            for s in range(3):
                got, _, _ = px_of(ART / "gi_rage_aura" / keys[(0, d, s)]["png"])
                self.assertEqual(got, gi_aura.bake(gold, pats[s][d], pal), (d, s))

    def test_ssj2_idle_body_is_the_std_golden(self):          # set 159 idle: std goldens, both bodies
        for e in manifest("gi_ssj2_aura"):
            if any(k["anim"] == 0 for k in e["keys"]):
                self.assertTrue(e["aura"]["body"].startswith("golden_gi_ssj2std_d"), e["png"])

    def test_walk_run_charge_frames_each_own_shape(self):
        for out in OUTS:
            keys = {(k["anim"], k["dir"], k["index"]): (e, k) for e in manifest(out) for k in e["keys"]}
            for a in gi_aura.AURA_ANIMS:
                for d in (0, 1, 2):
                    pngs = [keys[(a, d, i)][0]["png"] for i in range(4)]
                    self.assertEqual(len(set(pngs)), 4, (out, a, d))
                for i in range(4):                             # dir 3 flips the dir 2 frame, bolts included
                    (e3, k3), (e2, k2) = keys[(a, 3, i)], keys[(a, 2, i)]
                    self.assertEqual(e3["png"], e2["png"], (out, a, i))
                    self.assertEqual((k3["attr1"] ^ k2["attr1"]) & gi_aura.HFLIP, gi_aura.HFLIP, (out, a, i))

    def test_rage_has_the_set_58_layout(self):
        rows = gi_aura._layout_rows(58)
        got = {(k["anim"], k["dir"]) for e in manifest("gi_rage_aura") for k in e["keys"]}
        self.assertEqual(got, rows)
        self.assertFalse({a for a, _ in got} & {9, 11, 12, 20, 21})

    def test_geometry_kept(self):                              # aura frames keep the body record geometry
        for out, body in OUTS.items():
            want = {(k["anim"], k["dir"], k["index"]): k for e in manifest(body) for k in e["keys"]}
            for e in manifest(out):
                for k in e["keys"]:
                    src = want[(k["anim"], k["dir"], k["index"] // 3 if k["anim"] == 0 else k["index"])]
                    self.assertEqual({f: k[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")},
                                     {f: src[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")}, (out, k))


if __name__ == "__main__":
    unittest.main()
