r"""
test_art_inject.py - Tests for patches.art_inject and art_tables: table portraits and palette entries in the ROM.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_art_inject.py -v
Builds build_list_dev.txt in memory up to art_inject ("pre"), then the rest ("rom"). Portraits are read back through
the live block (rom:0xBE10); the status page runs in the test_status_portrait renderer. Ports the checks of the
r20-r22 test_portrait_remaster that still hold. Source: docs\tasks\2026-10-20-inject-tool\inject-tool.md.
"""
import copy
import hashlib
import struct
import unittest

from PIL import Image

from art import art_tables as at
import log2_build
import log_paths
from patches import art_inject
from tests.test_status_portrait import BASE_ROM, render
from rom.webfoot_decompress import ROM_BASE, unpack_frame

# ===== constants =====
LIST = ["gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle", "cutscene_portraits", "npc_gi",
        "rage_text", "art_inject", "status_portrait", "rage_stats", "cellgames_ssj", "scene_drain_pause",
        "fullpower_ssj", "piccolo_gi_scene", "superperfect_cell", "chamber_spar",   # r37: chamber_spar
        "bf_hud", "bf_ki_pool",                                                    # r39: the HUD v2b
        "relay_cooldown", "fullpower_hud", "beam_struggle", "vegeta_ssj_scene"]    # r40: four approved trials
R22_NOTES = {   # what r22 (portrait_remaster twice) gave each patch; art_inject must not move any of it
    "npc_gi": {"block": 0x894EAC, "pool": 0x894EA8, "pre_id": 121},
    "rage_text": {"record": 0x895434, "size": 0x31},
    "status_portrait": {"pool": 0x89A490, "code": 0x89A4D0, "paint": 0x89A4D0, "plus_byte": 0x8948D4,
                        "copy_site": 0x89491C},
    "rage_stats": {"code": 0x89A55C, "size": 0x68, "apply": 0x89A55C, "vtable_word": 0x24E4C},
}
R22_FIRST_FRAME, R22_CURSOR = 0x895468, 0x89A5C4      # r20 frame 63; rage_stats end (r22 late frames followed)
OLD_BLOCK, OLD_65_FRAME, OLD_40_FRAME = 0x3EC9D0, 0x6BDE20, 0x6B7904
OWNER = {65: ("final_r24", "goku_ssj_65_owner_dl7.png", 23),     # My art since r24-r26
         40: ("final_r24", "cell_40_owner_v2.png", 21)}
CELL_SHA1 = "f087e9429597774be1330c63b4cf42fb7fb907f2"
SHOWN = {19: 63, 20: 65, 8: 106, 9: 106, 5: 115, 22: 117, 4: 117, 2: 119}   # appearance entry: dialog id
SKIN = (172, (248, 224, 208))                          # palette-slot-report.md
_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        i = names.index("art_inject")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(pre=bytes(rom), alloc=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, names[i:])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes)
        pal, ok = at.obj_palette(rom), at.allowed_indices(rom, {})
        _CACHE["png"] = {pid: at.png_pixels(at.ART_DIR / e["png"], pal, ok) for pid, e in at.load_portraits().items()}
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def art_only(palette: dict, portraits: dict) -> tuple:
    """(rom, alloc) of pre + art_inject alone with staged tables."""
    b = built()
    rom, alloc = bytearray(b["pre"]), copy.deepcopy(b["alloc"])
    alloc.notes["art_input"] = {"palette": palette, "portraits": portraits}
    art_inject.apply(rom, alloc)
    return bytes(rom), alloc


def full(palette: dict, portraits: dict) -> bytes:
    rom, _ = log2_build.assemble(log2_build.BASE, built()["names"],
                                 {"art_input": {"palette": palette, "portraits": portraits}})
    return bytes(rom)


def art_input_without(pid: int) -> dict:
    """The art tables as staged input minus one id: builds that name an older state (the id still vanilla)."""
    base, palette = log2_build.BASE.read_bytes(), at.load_palette()
    pal, ok = at.obj_palette(base, palette), at.allowed_indices(base, palette)
    return {"palette": palette, "portraits": {p: at.png_pixels(at.ART_DIR / e["png"], pal, ok)
                                              for p, e in at.load_portraits().items() if p != pid}}


def diff(a: bytes, b: bytes) -> list:
    return [i for c in range(0, len(a), 0x1000) if a[c:c + 0x1000] != b[c:c + 0x1000]
            for i in range(c, c + 0x1000) if a[i] != b[i]]


def edited(pid: int, index: int = None, where: int = 32 * 64 + 32) -> bytes:
    """Pixels of id pid as the pre build shows it, the pixel at where set to index (None: 2 or 9, a change)."""
    b = built()
    px = bytearray(at.live_frame(b["pre"], b["notes"]["npc_gi"]["block"], pid)[1])
    px[where] = index if index is not None else (9 if px[where] == 2 else 2)
    return bytes(px)


# ===== tests =====

class ArtInjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.pre, cls.rom, cls.notes, cls.png = b["pre"], b["rom"], b["notes"], b["png"]
        cls.block = cls.notes["npc_gi"]["block"]

    def test_build_list_replaces_both_portrait_remaster_calls(self):
        self.assertEqual(built()["names"], LIST)

    def test_each_table_portrait_reads_back_equal_to_its_png(self):
        self.assertEqual(sorted(self.png), [40, 52, 63, 65, 106, 115, 117, 119])   # r36: 52
        for pid, e in at.load_portraits().items():
            with self.subTest(pid=pid), Image.open(at.ART_DIR / e["png"]) as img:
                self.assertEqual((img.mode, img.size), ("P", (64, 64)))
                hdr, px = at.live_frame(self.rom, self.block, pid)
                self.assertEqual(px, img.tobytes())                       # read here, not through art_tables
                self.assertEqual(hdr, art_inject.slot(pid))
                self.assertEqual(self.rom[hdr:hdr + 8], bytes.fromhex("0000000000100000"))
                self.assertNotEqual(at.live_frame(self.pre, self.block, pid)[1], px)

    def test_owner_art_copies_are_the_files_the_owner_made(self):
        pal, ok = at.obj_palette(self.rom), at.allowed_indices(self.rom, {})
        for pid, (folder, name, colors) in OWNER.items():
            src = log_paths.PORTRAIT_SOURCES / "remaster" / folder / name
            self.assertIn(name, at.load_portraits()[pid]["note"])
            with Image.open(src) as img:                     # inject stores RGB art indexed (--snap for 40)
                self.assertEqual(at.to_pixels(img, pal, ok, snap=True)[0], self.png[pid], pid)
            self.assertEqual(len(set(self.png[pid])), colors)
        self.assertEqual(hashlib.sha1((at.ART_DIR / "portraits" / "040_cell_40.png").read_bytes()).hexdigest(),
                         CELL_SHA1)
        src = (log_paths.PORTRAIT_SOURCES / "remaster" / "superperfect" / "owner"
               / "sp52_owner_v3.png")                                   # r36: Super Perfect Cell, my final v3
        with Image.open(src) as img:
            self.assertEqual(at.to_pixels(img, pal, ok, snap=True), (self.png[52], [], []))
        self.assertEqual(len(set(self.png[52])), 24)
        self.assertIn("owner final v3", at.load_portraits()[52]["note"])

    def test_ring_equals_the_frame_before_the_table(self):
        for pid, px in self.png.items():
            ref = at.live_frame(self.pre, self.block, pid)[1]
            self.assertEqual([i for i in at.RING_IDX if px[i] != ref[i]], [], pid)
        self.assertEqual(len(at.RING_IDX), 732)
        for pid, old in ((65, OLD_65_FRAME), (40, OLD_40_FRAME)):
            self.assertEqual(u32(self.pre, self.block + 4 + 4 * pid), old + ROM_BASE)

    def test_rgb_copies_of_the_table_pngs_map_to_the_same_pixels(self):
        pal, ok = at.obj_palette(BASE_ROM), at.allowed_indices(BASE_ROM, {})
        for pid, e in at.load_portraits().items():
            with Image.open(at.ART_DIR / e["png"]) as img:
                rgb = img.convert("RGB")
            self.assertFalse(at.is_canonical(rgb, pal, ok))
            self.assertEqual(at.to_pixels(rgb, pal, ok), (self.png[pid], [], []), pid)

    def test_png_indices_follow_the_rule(self):
        ok = at.dialog_indices(BASE_ROM)
        for pid, px in self.png.items():
            self.assertEqual(set(px) - ok, set(), pid)
            self.assertFalse(set(px) & {0, 168})
            self.assertLessEqual(len(set(px)), 64)

    def test_code_addresses_equal_r22(self):
        for patch, want in R22_NOTES.items():
            self.assertEqual({k: self.notes[patch][k] for k in want}, want, patch)
        n = self.notes["art_inject"]
        self.assertEqual((n["gap"], n["block"]), (R22_FIRST_FRAME, self.block))
        self.assertEqual(n["gap"] + art_inject.LEGACY_GAP, R22_NOTES["status_portrait"]["pool"])
        used = built()["alloc"].used()
        self.assertTrue(all(off + size <= log2_build.ART_REGION[0] for off, size in used))
        self.assertEqual(n["frames"], {pid: art_inject.slot(pid) for pid in self.png})

    def test_art_alone_changes_only_slots_and_block_words(self):
        rom, _ = art_only({}, self.png)
        sites = [(art_inject.slot(p), art_inject.slot(p) + art_inject.FRAME) for p in self.png] + \
                [(self.block + 4 + 4 * p, self.block + 8 + 4 * p) for p in self.png]
        self.assertEqual([hex(i) for i in diff(self.pre, rom) if not any(a <= i < b for a, b in sites)], [])
        for pid in range(122):
            if pid not in self.png:
                self.assertEqual(u32(rom, self.block + 4 + 4 * pid), u32(self.pre, self.block + 4 + 4 * pid))

    def test_disk_tables_and_staged_tables_build_the_same_rom(self):
        self.assertEqual(full(at.load_palette(), self.png), self.rom)

    def test_adding_a_portrait_moves_nothing(self):
        """Id 94 (Piccolo) added: only its slot and its block word change; every other byte, code included, equal."""
        new = full(at.load_palette(), {**self.png, 94: edited(94)})
        slot = art_inject.slot(94)
        sites = [(slot, slot + art_inject.FRAME), (self.block + 4 + 4 * 94, self.block + 8 + 4 * 94)]
        changed = diff(self.rom, new)
        self.assertTrue(changed)
        self.assertEqual([hex(i) for i in changed if not any(a <= i < b for a, b in sites)], [])
        self.assertEqual(at.live_frame(new, self.block, 94)[1], edited(94))

    def test_replacing_a_portrait_changes_only_its_frame(self):
        px = bytearray(self.png[63])
        px[40 * 64 + 20] = 2 if px[40 * 64 + 20] != 2 else 9
        new = full(at.load_palette(), {**self.png, 63: bytes(px)})
        self.assertEqual(diff(self.rom, new), [art_inject.slot(63) + 8 + 40 * 64 + 20])

    def test_palette_writer_writes_both_copies(self):
        index, rgb = SKIN
        rom = full({index: rgb}, self.png)
        self.assertEqual([hex(i) for i in diff(full({}, self.png), rom)],
                         ["0x1da820", "0x1da821", "0x3ed0a8", "0x3ed0a9", "0x3ed0aa"])
        self.assertEqual(rom[0x1DA820:0x1DA822], bytes.fromhex("9F6B"))
        self.assertEqual(rom[0x3ED0A8:0x3ED0AB], bytes.fromhex("F8E0D0"))
        self.assertEqual(at.obj_palette(rom)[index], rgb)

    def test_empty_palette_table_writes_no_palette_byte(self):
        rom = full({}, self.png)                           # the disk table holds my entries since r24
        self.assertEqual(rom[at.OBJ_PAL:at.OBJ_PAL + 512], BASE_ROM[at.OBJ_PAL:at.OBJ_PAL + 512])
        self.assertEqual(rom[at.RGB_TABLE:at.RGB_TABLE + 1536], BASE_ROM[at.RGB_TABLE:at.RGB_TABLE + 1536])

    def test_a_palette_entry_makes_its_index_usable(self):
        index, rgb = SKIN
        px = edited(65, index)
        with self.assertRaisesRegex(ValueError, "not dialog portrait colors"):
            art_only({}, {**self.png, 65: px})
        rom, _ = art_only({index: rgb}, {**self.png, 65: px})
        self.assertEqual(at.live_frame(rom, self.block, 65)[1], px)

    def test_status_page_shows_the_table_art(self):
        table = self.notes["ssj2_form"]["table"]
        for entry, pid in SHOWN.items():
            with self.subTest(entry=entry, pid=pid):
                r = render(self.rom, entry)
                self.assertEqual(r["portrait_id"], self.rom[table + 20 * entry + 2])
                self.assertEqual(r["portrait_px"], self.png[pid])
                self.assertEqual(r["rgb"], [at.obj_palette(BASE_ROM)[k] for k in self.png[pid]])

    def test_old_frames_twins_and_vanilla_block_kept(self):
        for pid, hdr in self.notes["gohan_portraits"]["frames"].items():
            self.assertEqual(self.rom[hdr:hdr + 0x1008], self.pre[hdr:hdr + 0x1008], pid)
        for pid in (116, 118, 120, 15, 121):
            self.assertEqual(at.live_frame(self.rom, self.block, pid), at.live_frame(self.pre, self.block, pid))
        self.assertEqual(self.rom[OLD_BLOCK:OLD_BLOCK + 4 * 116], BASE_ROM[OLD_BLOCK:OLD_BLOCK + 4 * 116])
        for old in (OLD_65_FRAME, OLD_40_FRAME):
            self.assertEqual(self.rom[old:old + 0x400], BASE_ROM[old:old + 0x400])
        gap = self.notes["art_inject"]["gap"]
        self.assertEqual(set(self.rom[gap:gap + art_inject.LEGACY_GAP]), {0xFF})

    def test_apply_fails_closed(self):
        b = built()
        cases = [({}, {**self.png, 63: edited(63, 168)}, "not dialog portrait colors"),
                 ({}, {**self.png, 63: edited(63, where=0)}, "frame"),
                 ({}, {**self.png, 116: edited(116)}, "dialog id"),
                 ({}, {**self.png, 5: bytes(4096)}, "dialog id"),
                 ({}, {**self.png, 63: self.png[63][:4095]}, "pixels"),
                 ({168: (248, 224, 208)}, self.png, "never 0"),
                 ({172: (250, 224, 208)}, self.png, "multiple of 8"),
                 ({172: (248, 248, 248)}, self.png, "already belongs")]
        for palette, portraits, msg in cases:
            rom, alloc = bytearray(b["pre"]), copy.deepcopy(b["alloc"])
            alloc.notes["art_input"] = {"palette": palette, "portraits": portraits}
            with self.subTest(msg=msg), self.assertRaisesRegex(ValueError, msg):
                art_inject.apply(rom, alloc)
            self.assertEqual(bytes(rom), b["pre"])
            self.assertEqual(alloc.used(), b["alloc"].used())
        for pid in self.png:                                            # a block word someone else changed
            rom, alloc = bytearray(b["pre"]), copy.deepcopy(b["alloc"])
            rom[self.block + 4 + 4 * pid] ^= 0x04
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=pid):
                art_inject.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_second_run_and_missing_notes_raise(self):
        b = built()
        rom, alloc = art_only({}, self.png)
        with self.assertRaisesRegex(ValueError, "already ran"):
            art_inject.apply(bytearray(rom), alloc)
        with self.assertRaisesRegex(ValueError, "run them first"):
            art_inject.apply(bytearray(b["pre"]), type(b["alloc"])(len(b["pre"]), log2_build.EXPANSION))

    def test_unpack_reads_slot_frames_as_raw(self):
        hdr = art_inject.slot(40)
        kind, size, data, _ = unpack_frame(self.rom, hdr)
        self.assertEqual((kind, size, data), (0, 0x1000, self.png[40]))


if __name__ == "__main__":
    unittest.main()
