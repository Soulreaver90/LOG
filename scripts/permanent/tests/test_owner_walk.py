r"""
test_owner_walk.py - Tests for me-0948 pass: my drawn walk frames, the shape classifier
(torso_split), the part check (check_parts) and the rules that came with them.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Reads the generated folders art\gi_base, gi_ssj (gi_art.py all) and the golden PNGs.
Each rule test asserts more than 0 pixels on a real frame, so a rule that stops running fails here.
"""
import unittest
from pathlib import Path

from PIL import Image

from art import frame_lock
from art import gi_art
import log_paths

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
GOLDEN = ART / "golden"
SPRITES = gi_art.SPRITES
FORM_SET = {"base": "set56", "ssj": "set59", "ssj2": "set58"}

# ===== helpers =====

def armor(set_name: str, k: tuple) -> dict:
    return gi_art.frame_pixels(gi_art.by_key(SPRITES / set_name)[k])

def gi(folder: str, k: tuple) -> dict:
    return gi_art.frame_pixels(gi_art.by_key(ART / folder)[k])

def convert(set_name: str, k: tuple, form: str = None) -> tuple:
    """(armor pixels, head mask, converted pixels, parts) of one armor frame."""
    orig = armor(set_name, k)
    mask, parts = gi_art.head_mask(orig), {}
    back = gi_art.back_columns(f"gi_{form}", SPRITES / set_name) if form else None
    px, _ = gi_art.armor_to_gi(dict(orig), mask, parts, key=k, back=back)
    return orig, mask, px, parts

def keep_of(orig: dict, parts: dict) -> set:
    return (set().union(set(), *gi_art.floating(orig)) | gi_art.swoosh(orig)) | parts.get("loose", set())

def truth_frames() -> list:
    """(name, key, set, form, golden pixels): the 12 idle goldens and my 4 walk frames."""
    out = []
    for form, s in FORM_SET.items():
        own = gi_art.by_key(SPRITES / s)
        for d in range(4):
            rec = own[(0, d, 0)]
            shown = {**rec, "attr1": rec["attr1"] & ~gi_art.HFLIP}   # golden d3 is stored as shown
            img = Image.open(GOLDEN / f"golden_gi_{form}_d{d}.png")
            out.append((f"golden_{form}_d{d}", (0, d, 0), s, form, gi_art.image_pixels(img, shown)))
    own = gi_art.by_key(SPRITES / "set56")
    for i in range(4):
        img = Image.open(GOLDEN / f"golden_gi_base_a1_d0_i{i}.png")
        out.append((f"owner_a1_d0_i{i}", (1, 0, i), "set56", "base", gi_art.image_pixels(img, own[(1, 0, i)])))
    return out

# ===== my frames and the golden lock =====

class OwnerFrameTests(unittest.TestCase):
    def test_golden_set_has_84_names(self):                 # 16 idle (ssj2std: aura-rage pass) + 4 of my walk frames
        self.assertEqual(len(frame_lock.GOLDEN_FILES), 84)  # + 64 r12fix hand frames (r15, r17, r18 and r19 intakes)
        self.assertEqual(frame_lock.GOLDEN_WALK, [f"golden_gi_base_a1_d0_i{i}.png" for i in range(4)])
        for name in frame_lock.GOLDEN_FILES:
            self.assertTrue((GOLDEN / name).is_file(), name)

    def test_owner_walk_frames_are_byte_equal_in_gi_base(self):
        base = gi_art.by_key(ART / "gi_base")
        for i in range(4):
            rec = base[(1, 0, i)]
            got = Image.open(rec["dir_path"] / rec["png"])
            want = Image.open(GOLDEN / f"golden_gi_base_a1_d0_i{i}.png")
            self.assertEqual(got.size, want.size, f"1.0.{i}")
            self.assertEqual(got.tobytes(), want.tobytes(), f"1.0.{i}")
            self.assertGreater(sum(1 for b in want.tobytes() if b), 100, f"1.0.{i}")

# ===== the shape classifier and the part check =====

class ClassifierTests(unittest.TestCase):
    def test_torso_split_on_the_owner_frames(self):         # 9:52 AM: arm from torso by shape, not color
        for i in range(4):
            orig, _, _, parts = convert("set56", (1, 0, i), "base")
            self.assertIsNotNone(parts.get("span"), f"1.0.{i}")
            self.assertGreater(len(parts["torso"]), 10, f"1.0.{i}")
            self.assertFalse(parts["torso"] & parts["arms"], f"1.0.{i}: an arm pixel in the torso")

    def test_check_parts_passes_the_16_truth_frames(self):  # if a golden fails, the check is wrong
        for name, k, s, form, gold in truth_frames():
            orig, mask, _, parts = convert(s, k, form)
            bad = gi_art.check_parts(gold, orig, mask, parts, keep_of(orig, parts), k)
            self.assertEqual(bad, {}, name)

    def test_check_parts_catches_an_arm_painted_gi(self):   # 11:03 AM: a golden torso over the near arm
        orig, mask, px, parts = convert("set56", (5, 0, 1), "base")
        chin = gi_art.chin_of(orig, mask)
        limbs = {p for p in parts["arms"] | parts["hands"] if p[1] > chin[1] + gi_art.STRAP_ROWS}
        self.assertGreater(len(limbs), 5)
        pasted = {**px, **{p: gi_art.GI_BASE for p in limbs}}
        bad = gi_art.check_parts(pasted, orig, mask, parts, keep_of(orig, parts), (5, 0, 1))
        self.assertGreater(bad.get("arm", 0) + bad.get("glove", 0), 0)

    def test_parts_review_frames_fail_only_parts(self):     # a listed frame hides no other failure
        for name, keys in gi_art.PARTS_REVIEW.items():
            entries = {gi_art.key_str((q["anim"], q["dir"], q["index"])): m
                       for m in gi_art.load_manifest(ART / name) for q in m["keys"]}
            for ks in keys:
                self.assertLessEqual(set(gi_art.failing(entries[ks])), {"parts"}, f"{name} {ks}")

# ===== one test per rule =====

class RuleTests(unittest.TestCase):
    def test_back_width_follows_golden_d1(self):            # 9:55 AM: the gi back keeps the golden width
        x0, x1, _ = gi_art.back_columns("gi_base", SPRITES / "set56")
        self.assertEqual((x0, x1), (4, 10))
        for i in range(4):
            _, _, _, parts = convert("set56", (1, 1, i), "base")
            span = parts.get("span")
            self.assertIsNotNone(span, f"1.1.{i}")
            self.assertEqual(span[1] - span[0], x1 - x0, f"1.1.{i}")

    def test_leg_line_between_walking_legs(self):           # 9:48 AM: the legs read apart
        orig, _, px, parts = convert("set56", (1, 0, 1), "base")
        fill = gi_art.SUIT - {81}
        line = [p for p, v in orig.items() if v == 81 and p[1] > parts["waist"] and px.get(p) == gi_art.GI_LINE
                and orig.get((p[0] - 1, p[1])) in fill and orig.get((p[0] + 1, p[1])) in fill]
        self.assertGreater(len(line), 0)

    def test_stacked_fill_is_one_foot(self):                # ssj 4.1.1: an ankle band is no second foot
        boot = {(x, y) for x in range(4) for y in range(5)}
        edge = {(x, y) for (x, y) in boot if x in (0, 3) or y in (0, 2, 4)}
        self.assertEqual(len(gi_art.feet(boot, edge)), 1)
        px = gi("gi_ssj", (4, 1, 1))
        legs = [y for (x, y), v in px.items() if v in (34, 35) and y > 0]
        self.assertGreater(len(legs), 0)
        self.assertEqual(sorted(set(legs))[-2:], [max(legs) - 1, max(legs)])   # the shoe is the lowest rows only
        self.assertEqual(len(set(legs)), 2)

    def test_front_shoe_and_back_foot_shoe(self):           # 10:30 AM, 69.png: every upright foot shows a shoe
        for k in ((6, 0, 0), (7, 0, 0), (8, 0, 2)):
            orig, _, px, parts = convert("set56", k, "base")
            boots = parts["boots"]
            feet = gi_art.feet(boots, {p for p in boots if orig[p] in (13, 14)})
            self.assertGreater(len(feet), 1, gi_art.key_str(k))
            for foot in feet:
                self.assertTrue(any(px.get(p) in (34, 35) for p in foot), f"{gi_art.key_str(k)}: a foot without a shoe")

    def test_boot_in_the_swoosh_is_reclaimed(self):         # 10:30 AM, 70.png: the boot by the swoosh is a shoe
        _, _, px, parts = convert("set56", (8, 0, 2), "base")
        self.assertGreater(len(parts["reclaimed"]), 0)
        self.assertTrue(any(px.get(p) in (34, 35) for p in parts["reclaimed"]))

    def test_loose_white_stays_effect(self):                # 10:52 AM, 16.0.4: effect white stays white
        orig, _, _, parts = convert("set56", (16, 0, 4), "base")
        self.assertGreater(len(parts["loose"]), 0)
        final = gi("gi_base", (16, 0, 4))
        self.assertTrue(all(final.get(p) == orig[p] for p in parts["loose"]))

    def test_sash_only_on_the_waist_span(self):             # 10:52 AM, 8.0.1: never along the kicking leg
        _, _, px, parts = convert("set56", (8, 0, 1), "base")
        red = [p for p, v in px.items() if v in gi_art.RED]
        self.assertGreater(len(red), 3)
        self.assertTrue(all(parts["span"][0] <= x <= parts["span"][1] for x, _ in red))

    def test_kick_shaft_is_gi_not_hem(self):                # 11:03 AM, 72.png: base 8.0.1 at (-2..-1, -1)
        final = gi("gi_base", (8, 0, 1))
        self.assertEqual([final.get((x, -1)) in (88, 89) for x in (-2, -1)], [True, True])

    def test_golden_torso_never_covers_an_arm(self):        # 11:03 AM: the golden torso replaces torso only
        orig, mask, _, parts = convert("set56", (4, 2, 0), "base")
        final = gi("gi_base", (4, 2, 0))
        chin = gi_art.chin_of(orig, mask)
        limbs = {p for p in parts["arms"] | parts["hands"] if p[1] > chin[1] + gi_art.STRAP_ROWS}
        self.assertGreater(len(limbs), 3)
        self.assertFalse([p for p in limbs if final.get(p) in gi_art.GI])   # the side sash may pass behind it

    def test_kick_8_0_3_keeps_its_arm(self):                # 11:03 AM, 73.png: the near arm is skin
        orig, _, _, parts = convert("set56", (8, 0, 3), "base")
        final = gi("gi_base", (8, 0, 3))
        glove = [p for p in parts["hands"] if p[0] < 6]
        self.assertGreater(len(glove), 4)
        self.assertTrue(all(final.get(p) in gi_art.SKIN | {23} | gi_art.WRISTBAND for p in glove))

    def test_kick_16_0_2_sash_spans_the_waist(self):        # 11:03 AM, 74.png: one row up, full width
        final = gi("gi_base", (16, 0, 2))
        rows = {y for (_, y), v in final.items() if v in gi_art.RED}
        self.assertEqual(len(rows), 1)
        self.assertEqual(sum(1 for (_, y), v in final.items() if v in gi_art.RED), 7)

if __name__ == "__main__":
    unittest.main()
