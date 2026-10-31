r"""
test_sprites.py - Tests for log2_sprites.py (Task 2).

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Works on an in-memory copy of the base ROM padded to 16 MB. Writes nothing to disk except under a temp folder.
"""
import json
import struct
import tempfile
import unittest
from pathlib import Path

from rom.log2_sprites import PALETTE_OFF, clone_set, export_set, image_to_tiles, set_records, tiles_to_image
from rom.rom_space import Allocator
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, read_set, rom_ptr, unpack_frame

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
FULL = 16777216
SET_53, SET_56, SET_59 = 0x285234, 0x299C48, 0x2B69C8
BASE_ROM = BASE.read_bytes()
PALETTE = BASE_ROM[PALETTE_OFF:PALETTE_OFF + 512]


def fresh():
    rom = bytearray(BASE_ROM) + bytearray(b"\xFF" * (FULL - len(BASE_ROM)))
    return rom, Allocator(FULL, [(0x800000, 0x800000)])


def unique_frames(rom, set_off):
    out = {}
    for r in set_records(rom, set_off):
        out.setdefault(r["header"], (unpack_frame(rom, r["header"])[2], r["w"], r["h"]))
    return out


def decoded_frames(rom, set_off):
    return [(r["anim"], r["dir"], r["index"], r["dx"], r["dy"], r["w"], r["h"], r["attr0"], r["attr1"],
             unpack_frame(rom, r["header"])[2]) for r in set_records(rom, set_off)]


def changed_ranges(before, after):
    out, i = [], 0
    while i < len(before):
        if before[i] != after[i]:
            j = i
            while j < len(before) and before[j] != after[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


class SpriteTests(unittest.TestCase):
    def test_tiles_image_round_trip(self):                 # set 53, every frame
        for hdr, (data, w, h) in unique_frames(BASE_ROM, SET_53).items():
            self.assertEqual(image_to_tiles(tiles_to_image(data, w, h, PALETTE)), data, hex(hdr))

    def test_image_pixel_order(self):
        data = bytes(range(64)) + bytes(64)                # 16x8: tile 0 left, tile 1 right
        img = tiles_to_image(data, 16, 8, PALETTE)
        self.assertEqual(img.getpixel((1, 0)), 1)
        self.assertEqual(img.getpixel((0, 1)), 8)
        self.assertEqual(img.getpixel((8, 0)), 0)

    def test_clone_unchanged_is_identical(self):           # set 56 cloned with no new frames
        rom, alloc = fresh()
        new = clone_set(rom, SET_56, {}, alloc)
        self.assertEqual(decoded_frames(rom, new), decoded_frames(rom, SET_56))
        a, b = read_set(rom, new), read_set(rom, SET_56)
        self.assertEqual((a["dirs"], a["anims"]), (b["dirs"], b["anims"]))
        self.assertEqual(rom[new:new + 12], rom[SET_56:SET_56 + 12])

    def test_clone_every_record_decodes(self):             # Review Focus 5
        rom, alloc = fresh()
        frames = {h: bytes(len(d)) for h, (d, _, _) in unique_frames(rom, SET_59).items()}
        new = clone_set(rom, SET_59, frames, alloc)
        recs = set_records(rom, new)
        self.assertEqual(len(recs), len(set_records(rom, SET_59)))
        for rec in recs:
            kind, size, data, _ = unpack_frame(rom, rec["header"])
            self.assertEqual(kind, 0)
            self.assertEqual(size, rec["w"] * rec["h"])
            self.assertEqual(len(data), size)

    def test_clone_replaces_only_chosen_frame(self):
        rom, alloc = fresh()
        src = unique_frames(rom, SET_59)
        hdr = next(iter(src))
        data, w, h = src[hdr]
        marker = bytes([7]) * len(data)
        new = clone_set(rom, SET_59, {hdr: marker}, alloc)
        old_recs, new_recs = set_records(rom, SET_59), set_records(rom, new)
        for o, n in zip(old_recs, new_recs):
            got = unpack_frame(rom, n["header"])[2]
            want = marker if o["header"] == hdr else unpack_frame(rom, o["header"])[2]
            self.assertEqual(got, want)
            if o["header"] != hdr:
                self.assertEqual(n["header"], o["header"])  # untouched records keep the original pointer
        self.assertEqual(len({n["header"] for o, n in zip(old_recs, new_recs) if o["header"] == hdr}), 1)

    def test_read_set_uses_four_directions(self):          # Ruling 35: byte +1 is the slot size high byte
        sizes = set()
        for i in range(150):
            off = rom_ptr(BASE_ROM, SET_TABLE + 4 * i)
            s = read_set(BASE_ROM, off)
            self.assertEqual(s["dirs"], 4, i + 7)
            self.assertEqual(s["slot"], struct.unpack_from("<H", BASE_ROM, off)[0], i + 7)
            self.assertEqual(s["table"], off + 12 + 64, i + 7)
            sizes.add(s["slot"])
            for r in set_records(BASE_ROM, off):           # no frame is larger than its slot
                self.assertLessEqual(r["w"] * r["h"], s["slot"], f"set {i + 7}")
        self.assertTrue({0x200, 0x400, 0x1000} <= sizes)
        self.assertEqual(len(set_records(BASE_ROM, rom_ptr(BASE_ROM, SET_TABLE + 4 * (136 - 7)))), 24)

    def test_clone_pointers_are_gba_addresses(self):
        rom, alloc = fresh()
        new = clone_set(rom, SET_59, {}, alloc)
        s = read_set(rom, new)
        for i in range(s["anims"] * s["dirs"]):
            raw = struct.unpack_from("<I", rom, s["table"] + 4 * i)[0]
            self.assertTrue(raw == 0 or ROM_BASE <= raw < ROM_BASE + FULL)
        for r in set_records(rom, new):
            self.assertTrue(ROM_BASE <= struct.unpack_from("<I", rom, r["rec"] + 8)[0] < ROM_BASE + FULL)

    def test_clone_rejects_wrong_length_and_unused_key(self):
        rom, alloc = fresh()
        hdr = next(iter(unique_frames(rom, SET_59)))
        with self.assertRaises(ValueError):
            clone_set(rom, SET_59, {hdr: b"\0"}, alloc)
        with self.assertRaises(ValueError):
            clone_set(rom, SET_59, {0x123450: b"\0"}, alloc)

    def test_clone_writes_only_allocated_space(self):
        rom, alloc = fresh()
        frames = {h: bytes([1]) * len(d) for h, (d, _, _) in unique_frames(rom, SET_59).items()}
        before = bytes(rom)
        clone_set(rom, SET_59, frames, alloc)
        used = alloc.used()
        covered = bytearray(len(before))                  # adjacent allocations make one changed run
        for o, n in used:
            covered[o:o + n] = b"\x01" * n
        for a, b in changed_ranges(before, rom):
            self.assertTrue(all(covered[a:b]), f"0x{a:X}-0x{b:X} outside allocation")
        self.assertGreaterEqual(min(o for o, _ in used), 0x800000)

    def test_export_writes_manifest_and_pngs(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            path = export_set(BASE_ROM, SET_56, Path(tmp))
            man = json.loads(path.read_text())
            self.assertEqual(len(man), len(set_records(BASE_ROM, SET_56)))
            self.assertEqual(set(man[0]), {"anim", "dir", "index", "dx", "dy", "w", "h", "attr0", "attr1", "header", "png"})
            self.assertEqual(len({m["png"] for m in man}), len({m["header"] for m in man}))
            m = man[0]
            img = Image.open(Path(tmp) / m["png"])
            self.assertEqual((img.mode, img.size), ("P", (m["w"], m["h"])))
            self.assertEqual(image_to_tiles(img), unpack_frame(BASE_ROM, m["header"])[2])


if __name__ == "__main__":
    unittest.main()
