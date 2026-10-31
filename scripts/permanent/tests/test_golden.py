r"""
test_golden.py - Tests for the golden master and dev master split: patches.gohan_gi_vanilla, build_list.txt
                 (golden), build_list_dev.txt (dev) and the shared tail build_list_core.txt.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_golden.py -v
Builds both masters in memory, once. Golden relocates sets 157-160 exactly as dev does and leaves the pixels
vanilla, so the two ROMs may differ only inside the gi block and in the words that name sets 159 and 160.
Expected frames are read from the base ROM here, never from the patch module.
Source: docs\tasks\2026-10-31-golden-dev-split\split-brief.md (ADDENDUM: I picked the vanilla fill).
"""
import hashlib
import struct
import unittest
from collections import Counter
from unittest import mock

import log2_build
from patches import gohan_gi, gohan_gi_vanilla
from rom.log2_sprites import set_records
from rom.rom_space import Allocator
from rom.webfoot_decompress import SET_TABLE, rom_ptr, unpack_frame

# ===== constants =====
ROM_BASE = 0x08000000
SET_TABLE_LITERAL, FIRST_ID = 0x959C, 7
GOLDEN_SHA1 = "232fcceb9292adddbbf567bee8c1b8fc4d229551"      # build_list.txt, the golden master (2026-10-31)
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"        # build_list_dev.txt r40, byte for byte
NOTE_KEYS = ["appearance_copy", "set_157", "set_158", "set_159", "set_160", "set_table"]
LAYOUTS = {157: 56, 158: 59, 159: 59, 160: 58}               # new set id: the vanilla set it is laid out from
IDLE = {157: 2, 158: 2, 159: 6, 160: 6}                      # anim 0 records per dir each set publishes
MOVED = (159, 160)                                           # the only sets whose golden address differs
APPEARANCE_LEN = 22 * 20

_CACHE = {}


def built() -> dict:
    """{"golden": bytes, "dev": bytes, "golden_notes": dict, "dev_notes": dict}, built once."""
    if not _CACHE:
        for key, path in (("golden", log2_build.BUILD_LIST), ("dev", log2_build.DEV_LIST)):
            rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(path))
            _CACHE[key] = bytes(rom)
            _CACHE[f"{key}_notes"] = alloc.notes["gohan_gi"]
    return _CACHE


def set_keys(rom: bytes, set_id: int) -> dict:
    """{(anim, dir, index): (geometry, frame bytes)} of a set, read through the ROM's own set table."""
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0] - ROM_BASE
    off = struct.unpack_from("<I", rom, table + 4 * (set_id - FIRST_ID))[0] - ROM_BASE
    return {(r["anim"], r["dir"], r["index"]): (tuple(r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")),
                                                unpack_frame(rom, r["header"])[2]) for r in set_records(rom, off)}


def vanilla_keys(set_id: int) -> dict:
    """The same shape, read from the untouched base ROM for the layout set of `set_id`."""
    base = log2_build.BASE.read_bytes()
    off = rom_ptr(base, SET_TABLE + 4 * (LAYOUTS[set_id] - FIRST_ID))
    return {(r["anim"], r["dir"], r["index"]): (tuple(r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")),
                                                unpack_frame(base, r["header"])[2]) for r in set_records(base, off)}


def expected_keys(set_id: int) -> dict:
    """What golden must publish: every vanilla record, with anim 0 widened to IDLE[set_id] records a dir.
    The tests index by this map, because set_records walks a rebuilt set past the end of a packed list and
    reports records the patch never wrote. It reports the same extra records for dev, which is r40."""
    vanilla = vanilla_keys(set_id)
    shapes = IDLE[set_id] // 2                               # vanilla publishes 2 idle records a dir
    out = {k: v for k, v in vanilla.items() if k[0] != 0}
    out.update({(0, d, k): vanilla[(0, d, k // shapes)] for d in range(4) for k in range(IDLE[set_id])})
    return out


# ===== tests: the two lists =====

class ListTests(unittest.TestCase):
    def test_the_masters_differ_in_the_first_patch_only(self):
        golden = log2_build.read_build_list(log2_build.BUILD_LIST)
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual(golden[0], "gohan_gi_vanilla")
        self.assertEqual(dev[0], "gohan_gi")
        self.assertEqual(golden[1:], dev[1:])

    def test_both_masters_read_the_shared_tail(self):
        for path in (log2_build.BUILD_LIST, log2_build.DEV_LIST):
            lines = [ln.split("#", 1)[0].strip() for ln in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([ln for ln in lines if ln][1:], ["include build_list_core.txt"], path.name)

    def test_the_golden_list_is_the_default(self):
        self.assertEqual(log2_build.read_build_list(), log2_build.read_build_list(log2_build.BUILD_LIST))


# ===== tests: the two builds =====

class BuildTests(unittest.TestCase):
    def test_golden_builds_to_its_pinned_sha1(self):
        self.assertEqual(hashlib.sha1(built()["golden"]).hexdigest(), GOLDEN_SHA1)

    def test_dev_still_rebuilds_to_r40(self):
        """The arbiter of the split: dev is r40 byte for byte, so every trial keeps its SHA-1."""
        self.assertEqual(hashlib.sha1(built()["dev"]).hexdigest(), R40_SHA1)

    def test_both_masters_publish_the_same_six_note_keys(self):
        b = built()
        self.assertEqual(sorted(b["golden_notes"]), NOTE_KEYS)
        self.assertEqual(sorted(b["dev_notes"]), NOTE_KEYS)

    def test_only_sets_159_and_160_move(self):
        """The pad keeps every other address, which superperfect_cell pins and bf_hud digests."""
        b = built()
        moved = [k for k in NOTE_KEYS if b["golden_notes"][k] != b["dev_notes"][k]]
        self.assertEqual(moved, [f"set_{s}" for s in MOVED])

    def test_golden_differs_from_dev_in_the_gi_block_and_the_set_words_only(self):
        b = built()
        golden, dev, gi, di = b["golden"], b["dev"], b["golden_notes"], b["dev_notes"]
        block = range(gi["appearance_copy"] + APPEARANCE_LEN, gi["set_table"])
        swap = {di[f"set_{s}"] + ROM_BASE: gi[f"set_{s}"] + ROM_BASE for s in MOVED}
        words = set()
        for i in range(len(golden)):
            if golden[i] != dev[i] and i not in block:
                words.add(i & ~3)
        for w in sorted(words):
            dev_word = struct.unpack_from("<I", dev, w)[0]
            self.assertIn(dev_word, swap, f"rom:0x{w:X} is not a set 159 or 160 pointer")
            self.assertEqual(struct.unpack_from("<I", golden, w)[0], swap[dev_word], f"rom:0x{w:X}")
        self.assertEqual(len(words), 4)                      # the set table word and the hook literal, each set


# ===== tests: the vanilla fill =====

class FillTests(unittest.TestCase):
    def test_each_golden_set_publishes_the_dev_record_count(self):
        golden, dev = built()["golden"], built()["dev"]
        for set_id in LAYOUTS:
            with self.subTest(set_id=set_id):
                self.assertEqual(sorted(set_keys(golden, set_id)), sorted(set_keys(dev, set_id)))

    def test_sets_159_and_160_keep_six_anim_0_records_per_dir(self):
        """ssj2_idle stores body * 3 + shape, so fewer than 6 would run past the end of the list."""
        golden = built()["golden"]
        for set_id in LAYOUTS:
            per_dir = Counter(d for a, d, _ in set_keys(golden, set_id) if a == 0)
            with self.subTest(set_id=set_id):
                self.assertEqual(sorted(per_dir.values()), [IDLE[set_id]] * 4)

    def test_every_golden_record_is_its_vanilla_record_with_the_body_repeated(self):
        """Index k shows vanilla body k // shapes. Nothing is drawn and nothing comes from art\\golden."""
        golden = built()["golden"]
        for set_id in LAYOUTS:
            live, want = set_keys(golden, set_id), expected_keys(set_id)
            with self.subTest(set_id=set_id):
                self.assertEqual({k: live[k] for k in want}, want)

    def test_golden_invents_no_frame(self):
        golden = built()["golden"]
        for set_id in LAYOUTS:
            pixels = {data for _, data in vanilla_keys(set_id).values()}
            live = set_keys(golden, set_id)
            drawn = {key for key in expected_keys(set_id) if live[key][1] not in pixels}
            with self.subTest(set_id=set_id):
                self.assertEqual(drawn, set())


# ===== tests: the golden module reads no art, and the pad tracks the dev block =====

class IsolationTests(unittest.TestCase):
    def test_the_golden_patch_opens_no_art_folder(self):
        rom = bytearray(log2_build.BASE.read_bytes())
        rom += bytes([0xFF]) * (log2_build.ROM_SIZE - len(rom))
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        with mock.patch.object(gohan_gi, "art_records", side_effect=AssertionError("golden read a gi art folder")):
            gohan_gi_vanilla.apply(rom, alloc)
        self.assertEqual(sorted(alloc.notes["gohan_gi"]), NOTE_KEYS)

    def test_the_dev_gi_block_is_the_padded_size(self):
        """GI_BLOCK is the dev block, measured. A gi art round that changes its size must change it too."""
        rom = bytearray(log2_build.BASE.read_bytes())
        rom += bytes([0xFF]) * (log2_build.ROM_SIZE - len(rom))
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        gohan_gi.apply(rom, alloc)
        table = alloc.notes["gohan_gi"]["set_table"]
        first = alloc.notes["gohan_gi"]["appearance_copy"]
        end = max(at + size for at, size in alloc.used() if at < table)
        self.assertEqual(end - first, gohan_gi.GI_BLOCK,
                         "the gi art changed size: set patches.gohan_gi.GI_BLOCK to this block")


if __name__ == "__main__":
    unittest.main()
