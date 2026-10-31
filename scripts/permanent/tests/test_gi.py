r"""
test_gi.py - Tests for the gi art (gi_art.py) and the gi outfit patch (patches.gohan_gi), Task 5.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Art tests read the generated folders art\gi_base, gi_ssj, gi_ssj2 and the Z2 icon files.
Generate them first: py -3 -I scripts\permanent\art\gi_art.py frames
Geometry (Ruling 27, my direction k): every gi frame keeps the record of the same form's original frame
(set 56 base, set 59 Super Saiyan, set 58 Super Saiyan 2, set 59 where set 58 has no frame), or a larger
legal OBJ size that still holds the original box ("enlarged").
The patch tests build scratch\test-roms\gi.gba once (log: scratch\test-roms\build-log-test.md).
"""
import json
import struct
import unittest
from pathlib import Path

from PIL import Image

from art import gi_art
import log_paths
from rom.log2_sprites import PALETTE_LEN, PALETTE_OFF, SLOT_BYTES, set_records, tiles_to_image
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, rom_ptr, unpack_frame

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
ART = log_paths.ART
BASE_ROM = BASE.read_bytes()
SETS = {53: 0x285234, 56: 0x299C48, 58: 0x2AB508, 59: 0x2B69C8}
GEOMETRY = {"gi_base": (56,), "gi_ssj": (59,), "gi_ssj2": (58, 59)}   # first set that has the key wins
KEYS_FROM = {"gi_base": 56, "gi_ssj": 59, "gi_ssj2": 59}              # the key list each folder covers
EXTRA = {34, 35, 87, 88, 89, 211, 26, 72, 195, 191}        # gi colors named by me and the briefs; 191 = spark
                                                           # blue, 87 = the step light (gi-rules-night rule 4)
RECORD = ("dx", "dy", "w", "h", "attr0", "attr1")
APPEARANCE = 0x1D967C                                      # 22 entries of 20 bytes; +1 = set id
SET_TABLE_LITERAL = 0x959C                                 # the only literal of the set table (re-outfit.md section 6)
Z_USABLE, Z_DIM, ICON_LEN = 0x6DAE7C, 0x6DB07C, 0x200
BAR_TABLES = (0x3B5358, 0x3B5C00)                          # HP, EP, EXP, cooldown offset tables (re-forms.md section 4)


# ===== helpers =====

def _records(set_id: int) -> dict:
    return {(r["anim"], r["dir"], r["index"]): r for r in set_records(BASE_ROM, SETS[set_id])}


RECS = {s: _records(s) for s in SETS}
ALLOWED_INDICES = set().union(*(set(unpack_frame(BASE_ROM, h)[2]) for s in (53, 56, 58, 59)
                                for h in {r["header"] for r in RECS[s].values()})) | EXTRA


def manifest(name: str) -> list:
    return json.loads((ART / name / "manifest.json").read_text(encoding="ascii"))


def load(path: Path) -> Image.Image:
    with Image.open(path) as img:
        img.load()
        return img.copy()


def gi_entries():
    """(folder, manifest entry, image) for every generated gi frame."""
    for name in GEOMETRY:
        for m in manifest(name):
            yield name, m, load(ART / name / m["png"])


def hand(m: dict) -> bool:
    """A reviewed r12fix hand frame (hand_frames.py): it replaces the converter's frame, so rule tests skip it."""
    return any(n.startswith("hand frame") for n in m.get("notes", []))


def source_record(name: str, k: tuple) -> dict:
    return next(RECS[s][k] for s in GEOMETRY[name] if k in RECS[s])


def object_mask(m: dict, field: str = "head") -> set:
    """The manifest's head (or arm) pixels in object space (the first key's record)."""
    g = m["keys"][0]
    flip = g["attr1"] & gi_art.HFLIP
    return {(((g["w"] - 1 - x) if flip else x) + g["dx"], y + g["dy"]) for x, y in m[field]}


def bar_icon_bytes() -> set:
    """Icon byte offsets that the HUD bars overwrite: buffer offsets 0x300-0x4FF minus 0x300."""
    lo, hi = BAR_TABLES
    words = struct.unpack_from(f"<{(hi - lo) // 4}I", BASE_ROM, lo)
    return {w - 0x300 for w in words if 0x300 <= w < 0x500}


def set_offset(rom: bytes, set_id: int) -> int:
    """Set id >= 7 through the set table the code reads (its literal may be relocated by a patch)."""
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    return rom_ptr(rom, table + 4 * (set_id - 7))


def set_bytes(rom: bytes, set_id: int) -> list:
    """Every record of a set with its decoded pixels, plus the set table word."""
    off = rom_ptr(rom, SET_TABLE + 4 * (set_id - 7))
    return [off] + [(r["dx"], r["dy"], r["w"], r["h"], r["attr0"], r["attr1"], unpack_frame(rom, r["header"])[2])
                    for r in set_records(rom, off)]


# ===== art tests (Steps 1-5) =====

class GiArtTests(unittest.TestCase):
    def test_gi_uses_only_allowed_indices(self):           # palette rule
        for name, m, img in gi_entries():
            extra = set(img.tobytes()) - ALLOWED_INDICES
            self.assertFalse(extra, f"{name} {m['source']}: {sorted(extra)}")

    def test_gi_frames_keep_record_geometry(self):         # Ruling 27 and direction k
        for name, m, img in gi_entries():
            self.assertEqual(img.size, (m["w"], m["h"]), f"{name} {m['source']}")
            for g in m["keys"]:
                k = (g["anim"], g["dir"], g["index"])
                src = source_record(name, k)
                if m["geometry"] != "enlarged":
                    self.assertEqual({f: g[f] for f in RECORD}, {f: src[f] for f in RECORD}, f"{name} {k}")
                    continue
                self.assertIn((g["w"], g["h"]), gi_art.OBJ_SHAPES, f"{name} {k}")
                shape, size = gi_art.OBJ_SHAPES[(g["w"], g["h"])]
                self.assertEqual((g["attr0"] >> 14, g["attr1"] >> 14), (shape, size), f"{name} {k}")
                self.assertEqual((g["attr0"] & 0x3FFF, g["attr1"] & 0x3FFF),
                                 (src["attr0"] & 0x3FFF, src["attr1"] & 0x3FFF), f"{name} {k}")
                self.assertTrue(g["dx"] <= src["dx"] and g["dy"] <= src["dy"]
                                and g["dx"] + g["w"] >= src["dx"] + src["w"]
                                and g["dy"] + g["h"] >= src["dy"] + src["h"], f"{name} {k}: box lost")

    def test_gi_covers_every_key(self):                    # an empty folder must not pass
        for name, set_id in KEYS_FROM.items():
            got = [(g["anim"], g["dir"], g["index"]) for m in manifest(name) for g in m["keys"]]
            self.assertEqual(len(got), len(set(got)), name)
            self.assertEqual(set(got), set(RECS[set_id]), name)
            self.assertEqual(len({m["png"] for m in manifest(name)}), len(manifest(name)), name)
        self.assertEqual([len(manifest(n)) for n in GEOMETRY], [162, 159, 159])

    def test_gi_frames_are_indexed(self):
        for name, m, img in gi_entries():
            self.assertEqual(img.mode, "P", f"{name} {m['source']}")

    def test_gi_frames_differ_from_armor(self):            # the art was actually made
        for name in GEOMETRY:
            same = sum(1 for m in manifest(name)
                       if load(ART / name / m["png"]).tobytes() == unpack_frame(BASE_ROM, m["header"])[2])
            self.assertLess(same, 5, name)

    def test_manifest_checks_pass_or_have_a_reason(self):  # directions f, g, h, j, k
        for name, m, _ in gi_entries():
            bad = gi_art.failing(m)
            self.assertTrue(not bad or m["check_exception"], f"{name} {m['source']}: {bad}")

    def test_torso_skin_recomputed_from_png(self):         # Ruling 25, independent of the manifest numbers
        for name, m, img in gi_entries():
            px = gi_art.image_pixels(img, m["keys"][0])
            skin = len(gi_art.chest_skin(px, object_mask(m), arms=object_mask(m, "arms")))
            limit = gi_art.V_LIMIT[m["view"]]
            self.assertTrue(skin <= limit or m["check_exception"], f"{name} {m['source']}: {skin} > {limit}")

    def test_no_armor_white_below_the_chin(self):          # Ruling 26, recomputed from the PNG
        for name, m, img in gi_entries():
            px = gi_art.image_pixels(img, m["keys"][0])
            mask = object_mask(m)
            chin = gi_art.chin_of(px, mask)
            set_name, key = m["source"].split()
            orig = gi_art.frame_pixels(gi_art.by_key(gi_art.SPRITES / set_name)[tuple(map(int, key.split(".")))])
            keep = set().union(set(), *gi_art.floating(orig)) | gi_art.swoosh(orig)
            omask = gi_art.head_mask(orig)
            keep |= gi_art.loose_white(orig, {p for p, v in orig.items() if p not in omask | keep and v != 1})
            hits = [p for p, v in px.items() if v in gi_art.LIGHT and p not in mask and p not in keep
                    and chin and p[1] > chin[1] and not any(px.get(q) == gi_art.SPARK_BLUE
                                                          for q in gi_art.neighbours(p, True))]
            self.assertFalse(hits, f"{name} {m['source']}: {hits[:5]}")


# ===== my review 2026-10-17 (gi-fix-1125): legs vs arms, front V, side neck opening =====

GOLDEN = ART / "golden"
V_ROWS = (19, 20)                                          # first two gi rows under the collar on the idle goldens
GOLDEN_V = {"gi_base": (6, 10), "gi_ssj": (5, 9), "gi_ssj2": (13, 17)}   # gi columns between the collar outlines
GOLDEN_SIDE = ("gi_ssj2", (13, 15))                        # the golden side shows the opening (base and SSJ: arm)
SKIN = gi_art.SKIN
BAND = {72, 195}
BOOT = {gi_art.BOOT_EDGE, gi_art.BOOT_FILL}
# My marks (11:31 and 11:43 AM), object space boxes (x0, y0, x1, y1): a leg is gi trouser and a brown boot with
# no skin or band; an arm shows skin (and a band where its fist is in view).
LEGS = {(5, 0, 0): (9, -1, 14, 3), (5, 1, 1): (9, -1, 15, 2), (6, 1, 1): (11, -2, 15, 1),
        (7, 0, 1): (9, 1, 14, 3), (7, 1, 2): (1, -1, 6, 2), (1, 2, 0): (13, 2, 15, 4)}
FEET = {(7, 0, 1): (2, 5, 7, 7)}                           # the boot under the arm hung across the sash
ARMS = {(5, 0, 0): (9, -8, 14, -5), (5, 1, 1): (1, -5, 4, -2), (6, 1, 1): (1, -6, 4, -3),
        (7, 0, 1): (2, -5, 6, 1), (7, 1, 2): (9, -6, 13, -2), (1, 2, 0): (11, -1, 14, 1), (1, 2, 2): (11, -6, 15, -2)}
ARM_ONLY = {(5, 1, 1): (10, -7, 13, -5), (6, 1, 1): (11, -8, 14, -4)}   # the arm piece beside the head


def gi_pixels(name: str, k: tuple) -> dict:
    return gi_art.frame_pixels(gi_art.by_key(ART / name)[k])


def box(px: dict, b: tuple) -> set:
    x0, y0, x1, y1 = b
    return {v for (x, y), v in px.items() if x0 <= x <= x1 and y0 <= y <= y1}


class OwnerReviewTests(unittest.TestCase):
    def test_owner_legs_are_trouser_and_boot(self):          # 5.0.0 leg is not skin, and the 11:43 AM marks
        for name in GEOMETRY:
            for k, b in {**LEGS, **FEET}.items():
                got = box(gi_pixels(name, k), b)
                self.assertFalse(got & (SKIN | BAND), f"{name} {k}: skin or band in a leg")
                self.assertTrue(got & BOOT, f"{name} {k}: no brown boot")

    def test_owner_arms_are_skin_with_a_band(self):
        for k, b in ARMS.items():
            got = box(gi_pixels("gi_ssj2", k), b)
            self.assertTrue(got & SKIN and got & BAND, f"gi_ssj2 {k}: arm without skin and band")
        for k, b in ARM_ONLY.items():
            for name in ("gi_ssj", "gi_ssj2"):
                self.assertTrue(box(gi_pixels(name, k), b) & SKIN, f"{name} {k}: arm piece is not skin")

    def test_front_v_matches_golden(self):                   # 3 over 1 with 211 lines; idle frame 1 by the torso rule
        for name, (x0, x1) in GOLDEN_V.items():
            want = load(GOLDEN / f"golden_{name}_d0.png")
            for k in ((0, 0, 0), (0, 0, 1)):
                got = load(ART / name / gi_art.by_key(ART / name)[k]["png"])
                for y in V_ROWS:
                    self.assertEqual([got.getpixel((x, y)) for x in range(x0, x1 + 1)],
                                     [want.getpixel((x, y)) for x in range(x0, x1 + 1)], f"{name} {k} row {y}")

    def test_side_opening_matches_golden(self):
        name, (x0, x1) = GOLDEN_SIDE
        want = load(GOLDEN / f"golden_{name}_d2.png")
        got = load(ART / name / gi_art.by_key(ART / name)[(0, 2, 0)]["png"])
        for y in V_ROWS:
            self.assertEqual([got.getpixel((x, y)) for x in range(x0, x1 + 1)],
                             [want.getpixel((x, y)) for x in range(x0, x1 + 1)], f"{name} row {y}")

    def test_every_opening_has_its_shape(self):              # front: 116 115 116 over 116; side: 116 116, 116 under
        for name, m, img in gi_entries():
            if m["v_neck"] != "yes" or hand(m):                # r15: base 8.0.3 hand frame draws its own bare-chest V
                continue
            px = gi_art.image_pixels(img, m["keys"][0])
            chin = gi_art.chin_of(px, object_mask(m))
            spots = [p for p in px if chin[1] < p[1] <= chin[1] + 4]
            if m["view"] == "front":
                hit = [(x, y) for x, y in spots if px[(x, y)] == 115 and px.get((x - 1, y)) == 116
                       and px.get((x + 1, y)) == 116 and px.get((x, y + 1)) == 116]
            else:
                hit = [(x, y) for x, y in spots if px[(x, y)] == 116 and px.get((x + 1, y)) == 116
                       and 116 in (px.get((x, y + 1)), px.get((x + 1, y + 1)))]
            self.assertTrue(hit, f"{name} {m['source']}: {m['view']} opening missing its shape")


# ===== my review 2026-10-17 10:38 and 10:56 PM: chin and sash in the transform step, base sash vs SSJ =====

STEP = [(9, 0, i) for i in range(4)]                       # anim 9 dir 0: all 4 dirs share these frames
CHIN_ROW = 18                                              # image row of the skin under the chin in 157 9.0.x


def sash_row(px: dict):
    """Object (screen) row with the most sash pixels (26, 27), or None."""
    rows = {}
    for (_, y), v in px.items():
        if v in (26, 27):
            rows[y] = rows.get(y, 0) + 1
    return max(rows, key=rows.get) if rows else None


def same_body(k: tuple) -> bool:
    """Sets 56 and 59 draw the same armored body for key k (every row from 2 under the set 56 chin down)."""
    a, b = (gi_art.frame_pixels(gi_art.by_key(gi_art.SPRITES / s)[k]) for s in ("set56", "set59"))
    chin = gi_art.chin_of(a, gi_art.head_mask(a))
    return bool(chin) and ({p: v for p, v in a.items() if p[1] > chin[1] + 1}
                           == {p: v for p, v in b.items() if p[1] > chin[1] + 1})


class TransformStepTests(unittest.TestCase):
    def test_step_chin_stays_skin(self):                    # 157 9.0.2-3 painted the neck under the chin purple
        armor = gi_art.by_key(gi_art.SPRITES / "set56")
        gi = gi_art.by_key(ART / "gi_base")
        good = load(ART / "gi_base" / gi[STEP[1]]["png"])
        for k in STEP[2:]:
            got = load(ART / "gi_base" / gi[k]["png"])
            src = load(gi_art.SPRITES / "set56" / armor[k]["png"])
            row = [got.getpixel((x, CHIN_ROW)) for x in range(got.width)]
            skin = [x for x in range(src.width) if src.getpixel((x, CHIN_ROW)) in gi_art.SKIN]
            self.assertTrue(skin, k)
            self.assertFalse([x for x in skin if row[x] in gi_art.GI], f"gi_base {k}: gi under the chin")
            self.assertEqual(row, [good.getpixel((x, CHIN_ROW)) for x in range(good.width)], f"gi_base {k}")

    def test_step_sash_keeps_frame_0_row(self):             # the belt must not jump within the step
        for name in GEOMETRY:
            gi = gi_art.by_key(ART / name)
            rows = [sash_row(gi_art.frame_pixels(gi[k])) for k in STEP]
            self.assertIsNotNone(rows[0], name)
            self.assertEqual(rows, [rows[0]] * 4, name)

    def test_base_sash_not_below_ssj(self):                 # 10:56 PM: base belt matches SSJ
        base, ssj = gi_art.by_key(ART / "gi_base"), gi_art.by_key(ART / "gi_ssj")
        checked = 0
        for k in sorted(set(base) & set(ssj)):
            if not same_body(k) or hand(base[k]):              # r17: my flight back views 20.1/20.3 tilt the sash
                continue
            a, b = sash_row(gi_art.frame_pixels(base[k])), sash_row(gi_art.frame_pixels(ssj[k]))
            if a is None or b is None:
                continue
            checked += 1
            self.assertLessEqual(a, b, f"{k}: base sash row {a}, SSJ {b}")
        self.assertGreater(checked, 20)

    def test_idle_sash_row_matches_golden(self):
        for name in ("gi_base", "gi_ssj"):
            gi = gi_art.by_key(ART / name)
            for d in range(4):
                rec = gi[(0, d, 0)]
                want = load(GOLDEN / f"golden_{name}_d{d}.png")
                gold = {(x + rec["dx"], y + rec["dy"]): want.getpixel((x, y))
                        for y in range(want.height) for x in range(want.width) if want.getpixel((x, y))}
                self.assertEqual(sash_row(gi_art.frame_pixels(rec)), sash_row(gold), f"{name} d{d}")


# ===== golden rules (mine, 2026-10-17/18): shoes, shading C, torso and straps, step light =====

def grid(*rows: str, x0: int = 0, y0: int = 0) -> dict:
    """Object-space pixels from rows of indices ("." = transparent)."""
    return {(x0 + x, y0 + y): int(v) for y, row in enumerate(rows) for x, v in enumerate(row.split()) if v != "."}


def golden_px(name: str, d: int) -> tuple:
    """(pixels in image space, sash row) of a golden frame."""
    img = load(GOLDEN / f"golden_{name}_d{d}.png")
    px = {(x, y): img.getpixel((x, y)) for y in range(img.height) for x in range(img.width) if img.getpixel((x, y))}
    rows = [y for (_, y), v in px.items() if v in (26, 27)]
    return px, max(set(rows), key=rows.count)


def ruled(name: str, word: str) -> list:
    """(manifest entry, object pixels) of every frame whose notes name the rule `word`."""
    return [(m, gi_art.image_pixels(img, m["keys"][0])) for n, m, img in gi_entries()
            if n == name and any(t.startswith(f"rule {word}") for t in m["notes"])]


class GoldenRuleTests(unittest.TestCase):
    def test_shoe_rows(self):                               # a shoe is the bottom 2 rows of the boot
        px = grid("211 89 89 211", "35 34 34 35", "35 34 34 35", "35 34 34 35", "35 35 35 35")
        self.assertEqual(gi_art.shoes(px, set()), 8)
        self.assertEqual([[px[(x, y)] for x in range(4)] for y in range(1, 5)],
                         [[211, 89, 89, 211], [211, 211, 211, 211], [35, 34, 34, 35], [35, 35, 35, 35]])
        for name in GEOMETRY:                               # the rule holds on every frame it ran on
            for m, fpx in ruled(name, "shoes"):                # lying and flying: along the legs from the hip
                if hand(m):                                    # r15: my 8.2.2 shoe replaces the rule's
                    continue
                hip = gi_art.hip_of(fpx, object_mask(m), {}) if "rule shoes along" in " ".join(m["notes"]) else None
                again = dict(fpx)
                gi_art.shoes(again, object_mask(m), hip)
                moved = {p: (fpx[p], v) for p, v in again.items() if v != fpx[p]}
                if m["view"] == "side" and not hip:     # 10:30 AM (69.png): a side back foot's toe touches
                    moved = {p: c for p, c in moved.items() if c != (35, 211)}   # the near shoe; only the armor
                self.assertEqual(moved, {}, f"{name} {m['source']}")             # split tells them apart

    def test_hem(self):                                     # the hem is only under trouser; a toe stays shoe
        px = grid("211 89 211 . .", "35 34 34 34 35", "35 34 34 34 35", "1 35 35 35 1")
        gi_art.shoes(px, set())
        self.assertEqual([px[(x, 1)] for x in range(5)], [211, 211, 211, 34, 35])
        for name in GEOMETRY:                               # My goldens are already ruled
            for d in range(4):
                gpx, sash = golden_px(name, d)
                self.assertEqual(gi_art.shoes(dict(gpx), {p for p in gpx if p[1] <= sash}), 0, f"{name} d{d}")

    def test_shading_runs(self):                            # rule C, n = 1..6, even and odd rows, light from the left
        want = {(1, 0): [89], (2, 0): [88, 89], (3, 0): [89, 88, 89], (4, 0): [89, 88, 89, 89],
                (5, 0): [89, 89, 88, 89, 89], (6, 0): [89, 89, 89, 88, 89, 89],
                (1, 1): [89], (2, 1): [88, 89], (3, 1): [89, 88, 89], (4, 1): [89, 88, 89, 89],
                (5, 1): [89, 88, 88, 88, 89], (6, 1): [89, 88, 88, 88, 88, 89]}
        for (n, y), row in want.items():
            px = {(x, y): 88 for x in range(n)}
            gi_art.shade(px, set(), -1)
            self.assertEqual([px[(x, y)] for x in range(n)], row, f"n {n} row {y}")
            px = {(x, y): 89 for x in range(n)}             # mirrored record: the image-left end is object right
            gi_art.shade(px, set(), 1)
            self.assertEqual([px[(x, y)] for x in range(n)], row[::-1], f"n {n} row {y} mirrored")
        for name in GEOMETRY:
            for d in range(4):
                gpx, sash = golden_px(name, d)
                legs = {p: v for p, v in gpx.items() if p[1] > sash}
                gi_art.shade(gpx, {p for p in gpx if p[1] <= sash}, 1 if d == 3 else -1)
                self.assertEqual({p: v for p, v in gpx.items() if p[1] > sash}, legs, f"{name} d{d}")

    def test_gap_fold(self):                                # gi over a gap between the legs is 211; not by an arm
        px = grid("211 88 88 88 88 88 211", "211 88 89 . 88 89 211", "23 . 211 . 88 88 211")
        self.assertEqual(gi_art.gap_folds(px, set(), -1), 1)
        self.assertEqual(px[(3, 0)], 211)
        px = grid("211 88 88 88 88 88 211", "211 88 . . . 89 211")
        self.assertEqual(gi_art.gap_folds(px, set(), -1), 3)
        self.assertEqual(gi_art.gap_folds(grid("23 88 88", "23 . 88"), set(), -1), 0)
        self.assertEqual(gi_art.gap_folds(grid("211 88 88 211", "211 . 88 211"), set(), 0), 0)   # at the sash
        for name in GEOMETRY:
            for d in range(4):
                gpx, sash = golden_px(name, d)
                self.assertEqual(gi_art.gap_folds(gpx, {p for p in gpx if p[1] <= sash}, sash), 0, f"{name} d{d}")

    def test_step_light_only_on_anim_9_frames_1_3(self):    # 10:45 PM: the transformation lights the gi up
        for name, m, img in gi_entries():
            steps = {(g["anim"], g["index"]) for g in m["keys"]}
            lit = all(a == gi_art.TRANSFORM_ANIM and i in gi_art.STEP_FRAMES for a, i in steps)
            self.assertEqual(87 in img.tobytes(), lit, f"{name} {m['source']}")
            if lit:
                px = gi_art.image_pixels(img, m["keys"][0])
                bare = [p for p, v in px.items() if v == 89 and p not in object_mask(m)
                        and any(px.get((p[0] + s, p[1])) == 87 for s in (-1, 1))]
                self.assertFalse(bare, f"{name} {m['source']}: 89 beside 87")

    def test_v_lines_and_straps(self):                      # the golden front torso from the converter's pixels
        px = grid(". . . . 23 23 115 114 114 116 117 23 23 . . .",
                  ". . . 23 115 211 23 23 23 23 23 211 115 23 . .",
                  ". . 23 116 116 211 89 116 115 116 89 211 116 23 . .",
                  ". . 23 115 117 211 88 89 116 88 89 211 115 23 . .",
                  ". . 72 195 117 211 89 88 88 88 89 211 117 195 23 .", y0=-7)
        mask = {p for p in px if p[1] < -5}
        self.assertEqual(gi_art.v_lines(px, mask), 3)
        self.assertEqual(gi_art.straps(px, mask, set(), (0, 0, 0), -1), 8)
        want, _ = golden_px("gi_base", 0)
        for y in range(-7, -3):                             # golden rows 17-20 (row 21: the converter misses bands)
            self.assertEqual([px.get((x, y)) for x in range(2, 15)], [want.get((x, y + 24)) for x in range(2, 15)],
                             f"row {y + 24}")

    def test_idle_slots_equal_goldens(self):                # me, 2026-10-18: byte for byte, all 4 dirs
        for name in gi_art.IDLE_GOLDEN:
            gi = gi_art.by_key(ART / name)
            for d in range(4):
                rec = gi[(0, d, 0)]
                img = load(ART / name / rec["png"])
                if rec["attr1"] & gi_art.HFLIP:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                self.assertEqual(img.tobytes(), load(GOLDEN / f"golden_{name}_d{d}.png").tobytes(), f"{name} d{d}")


# ===== me, 2026-10-18 8:53 AM: one gi body for SSJ and SSJ2, golden torso per frame, stray pinks =====

GI_FOLDERS = ("gi_base", "gi_ssj", "gi_ssj2", "gi_ssj_v2", "gi_ssj2_v2")
OWN_ANIMS = (0, 4)                                         # power-pose idle and ki charge: the armor bodies differ


class OneBodyTests(unittest.TestCase):
    def test_shared_frames_are_the_gi_ssj_body(self):       # only the SSJ2 head (both head masks) and sparks differ
        ssj, ssj2 = gi_art.by_key(ART / "gi_ssj"), gi_art.by_key(ART / "gi_ssj2")
        shared = [k for k, r in ssj2.items() if r["body"] == "gi_ssj"]
        self.assertGreater(len(shared), 200)
        for k in shared:
            a, b = gi_art.frame_pixels(ssj[k]), gi_art.frame_pixels(ssj2[k])
            head = gi_art.object_mask(ssj[k]) | gi_art.object_mask(ssj2[k])
            spark = {p for p, v in b.items() if v == gi_art.SPARK_BLUE or v == 2 and any(
                b.get(q) == gi_art.SPARK_BLUE for q in gi_art.neighbours(p, diag=True))}
            body = {p for p in set(a) | set(b) if p not in head | spark and a.get(p) != b.get(p)}
            self.assertFalse(body, f"{gi_art.key_str(k)}: body pixels differ from gi_ssj")

    def test_own_body_keys(self):                           # the armor differs, or a shared body fails the chest check
        ssj2 = gi_art.by_key(ART / "gi_ssj2")
        s58, s59 = gi_art.by_key(gi_art.SPRITES / "set58"), gi_art.by_key(gi_art.SPRITES / "set59")
        for k, r in ssj2.items():
            differ = gi_art.armor_body_diff(s58.get(k), s59[k]) > 0
            second_neck = any("second neck opening" in n for n in r["notes"])
            self.assertEqual(r["body"] == "own", differ or second_neck, gi_art.key_str(k))
            if k[0] in OWN_ANIMS:
                self.assertEqual(r["body"], "own", gi_art.key_str(k))
            if k not in s58:
                self.assertFalse(differ, f"{gi_art.key_str(k)}: set 58 lacks it, so the body is set 59's")

    def test_no_pink_in_any_gi_folder(self):                # 239 and 240 came from the Rage set 58
        for name in GI_FOLDERS:
            for m in manifest(name):
                self.assertFalse(set(load(ART / name / m["png"]).tobytes()) & gi_art.PINK, f"{name} {m['png']}")

    def test_stray_pink_rule(self):
        px = grid(". 20 20 .", "20 239 . .", ". . 23 .")              # touches the outside: cleared
        self.assertEqual(gi_art.stray_pinks(px), 1)
        self.assertNotIn((1, 1), px)
        px = grid("20 20 20", "20 240 37", "37 37 20")                # inside: most common neighbour (20: 2, 37: 2)
        gi_art.stray_pinks(px)
        self.assertEqual(px[(1, 1)], 20, "a tie takes the lower index")
        px = grid("20 20 20", "37 239 37", "37 37 20")
        gi_art.stray_pinks(px)
        self.assertEqual(px[(1, 1)], 37)

    def test_golden_torso_per_frame(self):                  # me: 157 a4 back did not match the golden
        base = gi_art.by_key(ART / "gi_base")
        own = gi_art.by_key(gi_art.SPRITES / "set56")
        for d in (0, 1, 2):
            gold, idle, window = gi_art.golden_torso("gi_base", own[(0, d, 0)], d)
            for i in range(4):
                notes = base[(4, d, i)]["notes"]
                torso = any(n.startswith("rule golden torso") for n in notes)
                self.assertEqual(torso, i in (0, 2), f"157 4.{d}.{i}: arms down take the golden torso")
                if torso:
                    px = gi_art.frame_pixels(base[(4, d, i)])
                    arm = gi_art.PART_COLORS["arm"]         # 11:03 AM: an arm pixel keeps its skin
                    torso = [p for p in window if not (px.get(p) in arm and gold.get(p) not in arm)]
                    self.assertEqual({p: px.get(p) for p in torso}, {p: gold.get(p) for p in torso}, f"4.{d}.{i}")
        for i in (1, 3):                                    # arms up: the strap group holds without frames 0 and 2
            self.assertTrue(any(n.startswith("rule straps") for n in base[(4, 0, i)]["notes"]), f"157 4.0.{i}")


class HudZ2Tests(unittest.TestCase):
    def icons(self):
        return [((ART / f"hud_z2_{kind}.bin").read_bytes(), BASE_ROM[off:off + ICON_LEN])
                for kind, off in (("usable", Z_USABLE), ("dim", Z_DIM))]

    def test_z2_format(self):
        for new, old in self.icons():
            self.assertEqual(len(new), ICON_LEN)
            self.assertNotEqual(new, old)
            self.assertLessEqual(set(new), set(old) | set(BASE_ROM[Z_USABLE:Z_USABLE + ICON_LEN]))

    def test_z2_keeps_bar_pixels(self):                     # the HP, EP and EXP bars draw over these bytes
        protected = bar_icon_bytes()
        self.assertGreater(len(protected), 40)
        for new, old in self.icons():
            for i in protected:
                self.assertEqual(new[i], old[i], f"icon byte 0x{i:03X}")


# ===== patch tests (Steps 6-7, part 2) =====

GI_IDS = {157: "gi_base", 158: "gi_ssj_v2", 159: "gi_ssj2_aura", 160: "gi_rage_aura"}   # gohan_gi default folders
REVERSE_LITERAL = 0x42F0
PALETTE = BASE_ROM[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN]


class GiPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):                                   # one build for the class, logged to the test log
        from unittest import mock
        import log2_build
        from tests.test_build import TEST_LOG, build
        out = log_paths.TEST_ROMS / "gi.gba"
        with mock.patch.object(log2_build, "BUILD_LOG", TEST_LOG):
            build(BASE, out, ["gohan_gi"])
        cls.rom = out.read_bytes()
        from patches import gohan_gi                       # the offsets the patch allocated, read apart from the ROM
        from rom.rom_space import Allocator
        rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        gohan_gi.apply(rom, alloc)
        cls.notes = alloc.notes["gohan_gi"]

    def test_appearance_2_resolves_to_gi_clone(self):       # Review Focus 1
        rom = self.rom
        self.assertEqual(rom[APPEARANCE + 20 * 2 + 1], 157)
        self.assertEqual(set_offset(rom, rom[APPEARANCE + 20 * 2 + 1]), self.notes["set_157"])
        self.assertGreaterEqual(self.notes["set_157"], 0x800000)

    def test_super_saiyan_resolves_to_158(self):
        rom = self.rom
        self.assertEqual(rom[APPEARANCE + 20 * 5 + 1], 158)
        self.assertEqual(rom[APPEARANCE + 20 * 2 + 4], 5)  # entry 2 still transforms to entry 5
        self.assertEqual(set_offset(rom, rom[APPEARANCE + 20 * 5 + 1]), self.notes["set_158"])
        self.assertGreaterEqual(self.notes["set_158"], 0x800000)

    def test_armor_sets_untouched(self):                    # Review Focus 2
        rom = self.rom
        for set_id in (55, 56, 58, 59):
            self.assertEqual(set_bytes(rom, set_id), set_bytes(BASE_ROM, set_id), set_id)
            self.assertEqual(set_offset(rom, set_id), set_offset(BASE_ROM, set_id), set_id)

    def test_set_table_words_7_to_156_unchanged(self):
        table = struct.unpack_from("<I", self.rom, SET_TABLE_LITERAL)[0] - ROM_BASE
        self.assertGreaterEqual(table, 0x800000)
        self.assertEqual(self.rom[table:table + 4 * 150], BASE_ROM[SET_TABLE:SET_TABLE + 4 * 150])

    def test_reverse_lookup_reads_original_table(self):    # ext op 73 (0, 56) must still find entry 2
        copy = struct.unpack_from("<I", self.rom, REVERSE_LITERAL)[0] - ROM_BASE
        self.assertGreaterEqual(copy, 0x800000)
        want = bytearray(BASE_ROM[APPEARANCE:APPEARANCE + 440])
        want[20 * 4 + 1] = 160                              # Rage: ext 73 (0, 160) at @0x083EA369
        self.assertEqual(self.rom[copy:copy + 440], bytes(want))
        first = {sid: next(e for e in range(22) if self.rom[copy + 20 * e + 1] == sid) for sid in (53, 56, 160)}
        self.assertEqual(first, {53: 0, 56: 2, 160: 4})
        self.assertNotIn(58, [self.rom[copy + 20 * e + 1] for e in range(22)])

    def test_gi_sets_decode_to_manifest_pixels(self):       # Review Focus 5 and Ruling 35
        for set_id, name in GI_IDS.items():
            off = set_offset(self.rom, set_id)
            slot = struct.unpack_from("<H", self.rom, off)[0]
            self.assertEqual(slot, SLOT_BYTES, set_id)
            want = {}
            for m in manifest(name):
                for g in m["keys"]:
                    want[(g["anim"], g["dir"], g["index"])] = ({f: g[f] for f in RECORD}, m)
            got = set_records(self.rom, off)
            self.assertEqual({(r["anim"], r["dir"], r["index"]) for r in got}, set(want), set_id)
            for r in got:
                k = (r["anim"], r["dir"], r["index"])
                geo, m = want[k]
                self.assertEqual({f: r[f] for f in RECORD}, geo, f"{set_id} {k}")
                self.assertLessEqual(r["w"] * r["h"], slot, f"{set_id} {k}")
                kind, size, data, _ = unpack_frame(self.rom, r["header"])
                self.assertEqual((kind, len(data)), (0, r["w"] * r["h"]), f"{set_id} {k}")
                img = tiles_to_image(data, r["w"], r["h"], PALETTE)
                self.assertEqual(img.tobytes(), load(ART / name / m["png"]).tobytes(), f"{set_id} {k}")

    def test_every_gi_frame_fits_the_slot(self):            # Ruling 35, on the art folders
        for name in GI_IDS.values():
            for m in manifest(name):
                for g in m["keys"]:
                    self.assertLessEqual(g["w"] * g["h"], SLOT_BYTES, f"{name} {m['source']}")


if __name__ == "__main__":
    unittest.main()
