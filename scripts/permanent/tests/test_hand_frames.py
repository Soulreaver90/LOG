r"""
test_hand_frames.py - Tests for the r15, r17, r18 and r19 intakes: the reviewed r12fix hand frames placed by key
(hand_frames.py).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Reads the snapshots art\hand-fixes\snap_r19\out\ (all 64 keys) and snap_r18\out\ (the keys before r19), the
goldens, the final art folders gi_base, gi_ssj_v2 and gi_ssj2_aura (gi_art.py, gi_post.py and gi_aura.py all) and
builds\log2_poc_r18.gba. Against r18 the only keys that may differ are the r19 keys (new, or revised with an
r19 REVISION golden) and the dir 3 records that h-flip a changed listed dir 2 frame (none in r19).
"""
import json
import unittest
from pathlib import Path

from PIL import Image

from art import frame_lock
from art import hand_frames
import log_paths
from rom.log2_sprites import PALETTE_LEN, PALETTE_OFF, set_records, tiles_to_image
from rom.rom_sheet import live_set_offset
from rom.webfoot_decompress import unpack_frame

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
SNAP = log_paths.HAND_FIXES / "snap_r19"
SNAP18 = log_paths.HAND_FIXES / "snap_r18"
R18 = log_paths.BUILDS / "log2_poc_r18.gba"
SET_OF = {"gi_base": 157, "gi_ssj_v2": 158, "gi_ssj2_aura": 159}
TWINS = [(1, 3, 0), (3, 3, 3), (8, 3, 2), (16, 3, 1), (16, 3, 4)]
MIRRORS = {f: TWINS for f in SET_OF}                                               # unlisted dir 3 h-flip twins
R19_MIRRORS = {"gi_base": [], "gi_ssj_v2": [], "gi_ssj2_aura": []}                # anim 12 has no dir 3
BOLT = (120, 208, 248)                                                             # r13 aura bolt blue


# ===== helpers =====

def snapshot_keys(snap: Path = SNAP) -> list:
    """(set, anim, dir, index) of each snapshot out\\ frame; at intake out\\ held exactly the EDITS keys."""
    keys = []
    for p in (snap / "out").glob("*.png"):
        s, a, d, i = p.stem.split("_")
        keys.append((int(s), int(a[1:]), int(d[1:]), int(i[1:])))
    return sorted(keys)


def r19_keys(folder: str) -> list:
    """Listed keys with an r19 golden: new in snap_r19, or revised in r19 (hand_frames.REVISION)."""
    old = {k[1:] for k in snapshot_keys(SNAP18) if k[0] == SET_OF[folder]}
    return [k for k in hand_frames.HAND[folder]
            if k not in old or hand_frames.REVISION.get(folder, {}).get(k) == "r19"]


def shown(folder: str) -> dict:
    """{key: (record fields, size, index bytes as the record shows them, png name)} of a final art folder."""
    out = {}
    for e in json.loads((ART / folder / "manifest.json").read_text()):
        with Image.open(ART / folder / e["png"]) as im:
            img = im.copy()
        for k in e["keys"]:
            v = img.transpose(Image.FLIP_LEFT_RIGHT) if k["attr1"] & hand_frames.HFLIP else img
            out[(k["anim"], k["dir"], k["index"])] = ({f: k[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")},
                                                      v.size, v.tobytes(), e["png"])
    return out


def rom_shown(rom: bytes, set_id: int) -> dict:
    out = {}
    for r in set_records(rom, live_set_offset(rom, set_id)):
        img = tiles_to_image(unpack_frame(rom, r["header"])[2], r["w"], r["h"], rom[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN])
        if r["attr1"] & hand_frames.HFLIP:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        out[(r["anim"], r["dir"], r["index"])] = ({f: r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")},
                                                   img.size, img.tobytes())
    return out


def palette_rgb(rom: bytes) -> list:
    raw = rom[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN]
    return [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)
            for c in (int.from_bytes(raw[2 * n:2 * n + 2], "little") for n in range(256))]


def flip(entry) -> bytes:
    return Image.frombytes("P", entry[1], entry[2]).transpose(Image.FLIP_LEFT_RIGHT).tobytes()


# ===== tests =====

class HandFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = R18.read_bytes()
        cls.rgb = palette_rgb(cls.rom)

    def test_table_lists_every_snapshot_key(self):
        listed = sorted((SET_OF[f], *k) for f, keys in hand_frames.HAND.items() for k in keys)
        self.assertEqual(listed, snapshot_keys())
        self.assertEqual(len(listed), 64)
        self.assertEqual(sum(len(r19_keys(f)) for f in SET_OF), 3)           # r19: 158 12.0.1-3 revised

    def test_each_listed_key_equals_its_snapshot_frame(self):
        for folder, keys in hand_frames.HAND.items():
            have = shown(folder)
            for a, d, i in keys:
                snap = Image.open(SNAP / "out" / f"{SET_OF[folder]}_a{a:02}_d{d}_i{i}.png").convert("RGBA")
                _, size, px, _ = have[(a, d, i)]
                self.assertEqual(size, snap.size, f"{folder} {a}.{d}.{i}")
                want = [(r, g, b) if al else None for r, g, b, al in snap.get_flattened_data()]
                got = [self.rgb[v] if v else None for v in px]
                self.assertEqual(got, want, f"{folder} {a}.{d}.{i}")
                self.assertGreater(sum(1 for v in px if v), 200, f"{folder} {a}.{d}.{i}")

    def test_goldens_equal_the_placed_frames(self):
        for folder, keys in hand_frames.HAND.items():
            have = shown(folder)
            for k in keys:
                gold = Image.open(hand_frames.GOLDEN / hand_frames.golden_name(folder, k))
                self.assertEqual(gold.mode, "P")
                self.assertEqual((gold.size, gold.tobytes()), have[k][1:3], f"{folder} {k}")

    def test_revised_keys_get_a_new_golden_and_keep_the_old_file(self):
        for folder, revs in hand_frames.REVISION.items():
            for k, rev in revs.items():
                new = hand_frames.golden_name(folder, k)
                a, d, i = k
                old = f"golden_gi_{hand_frames.FORM[folder]}_a{a}_d{d}_i{i}.png"
                self.assertEqual(new, old[:-4] + f"_{rev}.png")
                self.assertTrue((hand_frames.GOLDEN / old).is_file(), old)
                self.assertNotIn(old, frame_lock.GOLDEN_FILES)
                self.assertIn(new, frame_lock.GOLDEN_FILES)
                with Image.open(hand_frames.GOLDEN / old) as o, Image.open(hand_frames.GOLDEN / new) as n:
                    self.assertEqual(o.size, n.size)
                    self.assertNotEqual(o.tobytes(), n.tobytes(), new)

    def test_ssj2_side_walk_keeps_the_aura_bolts(self):     # r17 concern 1: 159 1.2.0 had lost the bolts
        have = shown("gi_ssj2_aura")
        for k in ((1, 2, 0), (1, 3, 0)):
            bolts = sum(1 for v in have[k][2] if v and self.rgb[v] == BOLT)
            self.assertGreaterEqual(bolts, 19, k)

    def test_no_other_key_differs_from_r18(self):
        for folder, set_id in SET_OF.items():
            have, old, listed = shown(folder), rom_shown(self.rom, set_id), set(hand_frames.HAND[folder])
            self.assertEqual(set(have), set(old), folder)
            mirrors = []
            for k in sorted(have):
                self.assertEqual(have[k][0], old[k][0], f"{folder} {k}: geometry")
                if k in listed:
                    continue
                a, d, i = k
                if d == hand_frames.MIRROR_DIR and (a, hand_frames.SOURCE_DIR, i) in listed and have[k][2] != old[k][2]:
                    self.assertEqual(have[k][2], flip(have[(a, hand_frames.SOURCE_DIR, i)]),
                                     f"{folder} {k}: not the mirror of its dir 2 hand frame")
                    mirrors.append(k)
                    continue
                self.assertEqual(have[k][1:3], old[k][1:3], f"{folder} {k}: changed against r18")
            self.assertEqual(mirrors, R19_MIRRORS[folder], folder)

    def test_every_mirror_shows_its_dir_2_frame(self):
        for folder in SET_OF:
            have, listed = shown(folder), set(hand_frames.HAND[folder])
            found = sorted(k for k in have if k not in listed and k[1] == hand_frames.MIRROR_DIR
                           and (k[0], hand_frames.SOURCE_DIR, k[2]) in listed
                           and have[k][3] == have[(k[0], hand_frames.SOURCE_DIR, k[2])][3])
            self.assertEqual(found, MIRRORS[folder], folder)
            for a, d, i in found:
                self.assertEqual(have[(a, d, i)][2], flip(have[(a, hand_frames.SOURCE_DIR, i)]), f"{folder} {a}.{d}.{i}")

    def test_r19_keys_changed_against_r18(self):              # proves the comparison above can see a change
        for folder, set_id in SET_OF.items():
            have, old = shown(folder), rom_shown(self.rom, set_id)
            for k in r19_keys(folder):
                self.assertNotEqual(have[k][2], old[k][2], f"{folder} {k}")

    def test_earlier_keys_equal_r18(self):
        for folder, set_id in SET_OF.items():
            have, old, new = shown(folder), rom_shown(self.rom, set_id), set(r19_keys(folder))
            for k in hand_frames.HAND[folder]:
                if k not in new:
                    self.assertEqual(have[k][1:3], old[k][1:3], f"{folder} {k}")

    def test_flight_dirs_2_and_3_are_listed_flips_of_dirs_0_and_1(self):
        have = shown("gi_base")
        for i in range(4):
            for src, dst in ((0, 2), (1, 3)):
                a, b = have[(20, src, i)], have[(20, dst, i)]
                self.assertEqual(a[3], b[3], (src, dst, i))                         # one PNG, one frame header
                self.assertEqual(b[2], flip(a), (src, dst, i))
                self.assertIn((20, dst, i), hand_frames.HAND["gi_base"])

    def test_golden_lock_holds_the_hand_frames(self):
        self.assertEqual(len(hand_frames.GOLDEN_HAND), 64)
        self.assertEqual(frame_lock.GOLDEN_FILES[-64:], hand_frames.GOLDEN_HAND)
        lock = json.loads((frame_lock.LOCKS / frame_lock.GOLDEN_NAME / "lock.json").read_text(encoding="ascii"))
        for name in frame_lock.GOLDEN_FILES:
            self.assertEqual(lock["frames"][name]["fingerprint"], frame_lock.fingerprint(frame_lock.GOLDEN_DIR / name), name)

    def test_gi_base_notes_and_exception(self):
        man = json.loads((ART / "gi_base" / "manifest.json").read_text())
        for k in hand_frames.HAND["gi_base"]:
            e = next(e for e in man if any((q["anim"], q["dir"], q["index"]) == k for q in e["keys"]))
            self.assertTrue(any(n.startswith("hand frame") for n in e["notes"]), k)

    def test_drawn_refuses_an_unlisted_key_on_a_shared_frame(self):
        with self.assertRaises(ValueError):                   # 4.0.0 is no flip twin of a listed key
            hand_frames.drawn("gi_base", {(3, 0, 3): 0x8000, (4, 0, 0): 0x8000}, (32, 32))
        with self.assertRaises(ValueError):                   # dir 3 without the flip bit is no mirror
            hand_frames.drawn("gi_base", {(8, 2, 2): 0x8000, (8, 3, 2): 0x8000}, (32, 32))
        self.assertIsNotNone(hand_frames.drawn("gi_base", {(8, 2, 2): 0x8000, (8, 3, 2): 0x9000}, (32, 32)))
        with self.assertRaises(ValueError):                   # listed flip pair, flip bit missing: the bytes differ
            hand_frames.drawn("gi_base", {(20, 0, 0): 0x8000, (20, 2, 0): 0x8000}, (32, 32))
        self.assertIsNotNone(hand_frames.drawn("gi_base", {(20, 0, 0): 0x8000, (20, 2, 0): 0x9000}, (32, 32)))

    def test_drawn_refuses_a_wrong_size_and_ignores_unlisted_frames(self):
        with self.assertRaises(ValueError):
            hand_frames.drawn("gi_base", {(5, 0, 2): 0x8000}, (32, 32))
        self.assertIsNone(hand_frames.drawn("gi_base", {(4, 0, 0): 0x8000}, (32, 32)))
        self.assertIsNone(hand_frames.drawn("gi_rage_aura", {(3, 0, 3): 0x8000}, (32, 32)))

    def test_flipped_key_gets_the_golden_flipped_back(self):
        name = hand_frames.golden_name("gi_base", (8, 2, 2))
        plain = hand_frames._stored(name, 0x8000).tobytes()
        flipped = hand_frames._stored(name, 0x9000)
        self.assertEqual(flipped.transpose(Image.FLIP_LEFT_RIGHT).tobytes(), plain)
        self.assertNotEqual(flipped.tobytes(), plain)


if __name__ == "__main__":
    unittest.main()
