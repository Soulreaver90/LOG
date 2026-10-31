r"""
test_gi_base_audit.py - Tests for patches.gi_base_audit (trial 2026-10-30): set 157 (base gi Gohan) shows the
                        approved base-audit frames in art\base-audit\approved\, and nothing else changes.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_gi_base_audit.py -v
Builds build_list_trial_gi_base.txt in memory: "before" = the list up to gi_base_audit (the main list, pinned to r40
by SHA-1), "rom" = with it. Expected frames are read from the approved PNGs here with PIL and from art\gi_base,
never from the patch module. Counts are restated from scripts\one-time\2026-10-30-gi-base-ingest\s1_map.txt.
"""
import copy
import hashlib
import shutil
import struct
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from PIL import Image

import log2_build
import log_paths
from rom.log2_sprites import image_to_tiles, set_records
from patches import gi_base_audit
from rom.webfoot_decompress import unpack_frame

# ===== constants (brief, s1_map.txt) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_gi_base.txt"
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"        # build_list.txt r40 (2026-10-30)
APPROVED = log_paths.ART / "base-audit" / "approved"
GI_BASE = log_paths.ART / "gi_base"
SET_TABLE_LITERAL, FIRST_ID = 0x959C, 7
PER_ANIM = {0: 3, 3: 12, 5: 12, 9: 16, 11: 8, 12: 8, 14: 20, 17: 8, 20: 16}   # 103 approved keys
FRAMES, CHANGED = 39, 1765                               # frame headers written; bytes that differ from r40
SHARED = ((12, 2, 0), (12, 3, 0))                        # dir 3 shows the h-flip of dir 2's frame

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("gi_base_audit")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, names[i:])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["gi_base_audit"])
    return _CACHE


def set_keys(rom: bytes, set_id: int) -> dict:
    """{(anim, dir, index): (geometry, frame bytes)} of a set, read through the ROM's own set table."""
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    off = struct.unpack_from("<I", rom, table + 4 * (set_id - FIRST_ID))[0] - ROM_BASE
    return {(r["anim"], r["dir"], r["index"]): (tuple(r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")),
                                                unpack_frame(rom, r["header"])[2]) for r in set_records(rom, off)}


def approved_png() -> dict:
    out = {}
    for p in sorted(APPROVED.glob("157_*.png")):
        a, d, i = (int(s[1:]) for s in p.stem.split("_")[1:4])
        with Image.open(p) as img:
            out[(a, d, i)] = image_to_tiles(img)
    return out


def diff(a: bytes, b: bytes) -> list:
    return [i for c in range(0, len(a), 0x1000) if a[c:c + 0x1000] != b[c:c + 0x1000]
            for i in range(c, c + 0x1000) if a[i] != b[i]]


def copy_approved(dst: Path) -> Path:
    for p in APPROVED.glob("*.png"):
        shutil.copy2(p, dst / p.name)
    return dst


# ===== tests: list =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "gi_base_audit" in dev:
            self.skipTest("approved: the line is in build_list_core.txt, so build_list_trial_gi_base.txt is retired")
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["gi_base_audit"])

    def test_before_is_r40(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R40_SHA1)


# ===== tests: the frames land, nothing else changes =====

class LandingTests(unittest.TestCase):
    def test_approved_folder_is_the_reviewed_set(self):
        self.assertEqual(Counter(k[0] for k in approved_png()), Counter(PER_ANIM))

    def test_every_approved_frame_lands_byte_for_byte(self):
        b, app = built(), approved_png()
        after = set_keys(b["rom"], 157)
        for k, tiles in app.items():
            self.assertEqual(after[k][1], tiles, k)

    def test_every_other_set_157_frame_and_every_geometry_is_unchanged(self):
        b, app = built(), approved_png()
        before, after = set_keys(b["before"], 157), set_keys(b["rom"], 157)
        self.assertEqual(before.keys(), after.keys())
        for k in before:
            self.assertEqual(after[k][0], before[k][0], k)
            if k not in app:
                self.assertEqual(after[k][1], before[k][1], k)

    def test_sets_158_to_160_are_unchanged(self):
        b = built()
        for set_id in (158, 159, 160):
            self.assertEqual(set_keys(b["rom"], set_id), set_keys(b["before"], set_id), set_id)

    def test_every_changed_byte_is_inside_a_site(self):
        b = built()
        sites = b["notes"]["sites"]
        self.assertEqual(len(sites), FRAMES)
        changed = diff(b["before"], b["rom"])
        self.assertEqual(len(changed), CHANGED)
        outside = [i for i in changed if not any(s <= i < s + n for s, n, _ in sites)]
        self.assertEqual(outside, [])

    def test_changed_bytes_match_approved_against_gi_base(self):
        """Independent count: approved tiles vs the gi_base PNG of the same key, once per gi_base PNG."""
        import json
        app, seen, n = approved_png(), {}, 0
        for m in json.loads((GI_BASE / "manifest.json").read_text(encoding="ascii")):
            keys = [(k["anim"], k["dir"], k["index"]) for k in m["keys"]]
            hits = [k for k in keys if k in app]
            if hits:
                self.assertEqual(hits, keys, m["png"])           # a frame is approved for all its keys or none
                with Image.open(GI_BASE / m["png"]) as img:
                    old = image_to_tiles(img)
                n += sum(a != c for a, c in zip(app[hits[0]], old))
                seen[m["png"]] = hits
        self.assertEqual((len(seen), n), (FRAMES, CHANGED))

    def test_sites_are_set_157_frame_data(self):
        b = built()
        for s, n, name in b["notes"]["sites"]:
            self.assertEqual(struct.unpack_from("<II", b["rom"], s - 8), (0, n), name)
            self.assertIn("set 157 frame", name)


# ===== tests: fail closed =====

class FailClosedTests(unittest.TestCase):
    def refuses(self, why: str, folder=None, rom=None, notes=None, msg=""):
        b = built()
        rom = bytearray(rom if rom is not None else b["before"])
        alloc = copy.deepcopy(b["alloc_before"])
        alloc.notes.update(notes or {})
        snap = bytes(rom)
        with mock.patch.object(gi_base_audit, "APPROVED", folder or APPROVED):
            with self.assertRaisesRegex(ValueError, why, msg=msg):
                gi_base_audit.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap, msg)

    def edited(self, key, change) -> tuple:
        tmp = tempfile.TemporaryDirectory()
        d = copy_approved(Path(tmp.name))
        p = d / ("157_a%d_d%d_i%d.png" % key)
        change(p)
        return tmp, d

    def test_second_run_raises(self):
        self.refuses("already ran", notes={"gi_base_audit": {}})
        self.refuses("not the gi_base frame", rom=built()["rom"], msg="frames already written")

    def test_a_shared_frame_missing_one_key_refuses(self):
        tmp, d = self.edited(SHARED[1], lambda p: p.unlink())
        with tmp:
            self.refuses("not approved", folder=d)

    def test_shared_keys_with_different_bytes_refuse(self):
        def poke(p):
            with Image.open(p) as img:
                img.load()
                img.putpixel((0, 0), 1 if img.getpixel((0, 0)) != 1 else 2)
                img.save(p, transparency=0)
        tmp, d = self.edited(SHARED[1], poke)
        with tmp:
            self.refuses("approved bytes differ", folder=d)

    def test_an_off_palette_color_refuses(self):
        def recolor(p):
            with Image.open(p) as img:
                img.load()
                used = max(set(img.tobytes()))
                pal = img.getpalette()
                pal[3 * used] ^= 0x08
                img.putpalette(pal)
                img.save(p, transparency=0)
        tmp, d = self.edited(SHARED[0], recolor)
        with tmp:
            recolor(d / ("157_a%d_d%d_i%d.png" % SHARED[1]))  # both keys, so the shared bytes stay equal
            self.refuses("not the OBJ palette color", folder=d)

    def test_a_wrong_size_or_name_refuses(self):
        def grow(p):
            Image.new("P", (32, 32)).save(p, transparency=0)
        tmp, d = self.edited((0, 0, 1), grow)                # a 16x32 key
        with tmp:
            self.refuses("PNG 32x32, record 16x32", folder=d)
        tmp, d = self.edited((0, 0, 1), lambda p: shutil.copy2(p, p.with_name("157_a0_d0_i1_v2.png")))
        with tmp:
            self.refuses("not a 157_a", folder=d)

    def test_changed_frame_data_refuses(self):
        b = built()
        s = b["notes"]["sites"][5][0]
        rom = bytearray(b["before"])
        rom[s + 3] ^= 0x01
        self.refuses("not the gi_base frame", rom=rom)

    def test_a_second_pointer_to_a_frame_refuses(self):
        b = built()
        hdr = b["notes"]["sites"][0][0] - 8
        rom = bytearray(b["before"])
        spot = 0xEFF000                                      # 0xFF fill at the end of the allocator's range
        self.assertEqual(set(rom[spot:spot + 4]), {0xFF})
        rom[spot:spot + 4] = struct.pack("<I", hdr + ROM_BASE)
        self.refuses("outside the set 157 records", rom=rom)

    def test_an_earlier_module_site_on_a_frame_refuses(self):
        s, n, _ = built()["notes"]["sites"][3]
        for site in ((s + n - 1, 1, "other"), s - 8, (s - 4, 8, "other")):
            self.refuses("also written by other_module", notes={"other_module": {"sites": [site]}}, msg=str(site))


if __name__ == "__main__":
    unittest.main()
