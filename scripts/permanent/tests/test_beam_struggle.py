r"""
test_beam_struggle.py - Tests for patches.beam_struggle (trial 2026-10-25): the mockup v2 beam struggle as map 14,4
                        BG0 tile art (BF sphere, orbs, sway, soft flash).

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_beam_struggle.py -v
Builds build_list_trial_beam.txt in memory (from r40 an alias of build_list.txt): "before" = the list up to
beam_struggle (r39 + relay_cooldown + fullpower_hud, pinned by SHA-1), "rom" = before + beam_struggle only (pinned).
One test also builds r39 + beam_struggle, the trial ROM I played (pinned). Every record is decoded from
the ROM with webfoot_decompress (never with the module's encoder). Expected values are restated from the base
ROM, the bible BMS and BMG rows, beam-mockup-report.md and scripts\one-time\2026-10-25-beam-trial\bridge.txt (the
mockup_v2 frames digest, computed by the mockup scripts themselves), never imported from the module.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
from patches import beam_struggle
from rom.webfoot_decompress import decompress, unpack_frame

# ===== constants (base ROM reads, BMS and BMG rows, bridge.txt) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_beam.txt"
BEFORE_SHA1 = "60572a84bf91fcfaa2c0690c9a5dc47bec0d2c88"       # r39 + relay_cooldown + fullpower_hud (r40 order)
ROM_SHA1 = "9256a6ba861e03743c1d971a3f054bea1bcc6aae"          # before + beam_struggle (r40 order, 2026-10-30)
TRIAL_SHA1 = "d7eed3c3b90a789edb935544dc261d01e6b69217"        # r39 + beam_struggle v2 (v1 05318b4e...), 2026-10-25
LAYOUT_WORD, VANILLA_LAYOUT = 0x4091EC, 0x084E2E7C
VANILLA_GROUPS = (0x084E2BE0, 0x084E2E64)                     # k0 starburst (BG1), k1 spark (BG0)
VANILLA_GROUP_BYTES = {0x084E2BE0: (2, 53, 843), 0x084E2E64: (3, 12, 831)}
VANILLA_BG0, VANILLA_TABLE, VANILLA_BLOCK5 = 0x084E0090, 0x084DF574, 0x084DFB74
VANILLA_TILES, FREE, SPARK = 596, (596, 830), (831, 842)
NEW_CHUNK = 168                                              # vanilla table words 0-167 (word 168 = block 0 frame type)
BEAM_IDX = {2, 67, 73, 74, 169}
FRAMES, DURATION = 144, 5
# bridge.txt: mockup_v2 frames with the v2 clean cut (the two edge-crossing BF orbs left out of the sphere), cells in
# sorted order, 64 B a cell, g = 0..143 (v1 without the cut: 3348b7f5615399666e87a2c5ea46bb4337395a4b)
MOCKUP_SHA1 = "86ee47d69c03b591bb0142772b6f693cf0e061f7"
# BF orbs the radius-25 disk at BF (128, 108) crosses (sphere_cut_view.txt, orb_find: rows 85-97 x 144-156 and rows
# 120-132 x 97-110), 6:40 PM "it should be a clean cut of the center orb"
SLICED_ORBS = ((150, 91), (103.5, 126))
BF_CENTRE, BF_DISK_R, BF_TO_WORLD = (128, 108), 25, (315, 280)
MOCKUP_CELLS, MOCKUP_DISTINCT = 124, 54
STATIC_CELLS = [(48, 47), (48, 48), (48, 49), (49, 47), (49, 48), (49, 49), (50, 48), (59, 48), (60, 47), (60, 48),
                (60, 49), (61, 47), (61, 48), (61, 49)]
STATIC_TILES = 9
GROUP_TILES = (64, 46)

_CACHE = {}


def u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE if a >= ROM_BASE else a)[0]


def entries(raw: bytes) -> list:
    """Delta-decoded u16 tile list (loader @0x080050C8: e[i] += e[i-1] + 1)."""
    e = list(struct.unpack("<%dH" % (len(raw) // 2), raw))
    for i in range(1, len(e)):
        e[i] = (e[i] + e[i - 1] + 1) & 0xFFFF
    return e


def hflip(t: bytes) -> bytes:
    return b"".join(t[8 * r:8 * r + 8][::-1] for r in range(8))


def vflip(t: bytes) -> bytes:
    return b"".join(t[8 * r:8 * r + 8] for r in range(7, -1, -1))


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("beam_struggle")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["beam_struggle"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["beam_struggle"], names=names)
        r = _CACHE["rom"]
        lay = u32(r, LAYOUT_WORD)
        _CACHE.update(layout=lay, groups=[u32(r, u32(r, lay + 0x10) + 4 * k) for k in range(u32(r, lay + 0xC))])
    return _CACHE


def decode_groups(rom: bytes, recs: list) -> list:
    """[(frames, tiles, first, [(duration, payload)])] of the new group records, decoded from the ROM."""
    out = []
    for rec in recs:
        nf, nt, first = rom[rec - ROM_BASE], rom[rec - ROM_BASE + 1], struct.unpack_from("<H", rom, rec - ROM_BASE + 2)[0]
        frames = []
        for f in range(nf):
            fp = u32(rom, rec + 4 + 4 * f)
            data, _ = decompress(rom, fp - ROM_BASE + 4)
            frames.append((u32(rom, fp), data))
        out.append((nf, nt, first, frames))
    return out


def screen_cells(rom: bytes) -> dict:
    """{world cell: [144 x 64 B]} as the hardware shows BG0 block (1,1) over the new tiles, frame g of both groups."""
    lay = u32(rom, LAYOUT_WORD)
    block = unpack_frame(rom, u32(rom, u32(rom, lay + 0x14) + 0x18 + 4 * 5) - ROM_BASE)[2]
    idx = entries(unpack_frame(rom, u32(rom, lay + 0x48) - ROM_BASE)[2])
    table = u32(rom, lay + 0x4C)
    vram = {}
    for slot in range(VANILLA_TILES, len(idx)):
        chunk = unpack_frame(rom, u32(rom, table + 4 * (idx[slot] >> 8)) - ROM_BASE)[2]
        vram[slot] = chunk[64 * (idx[slot] & 0xFF):64 * (idx[slot] & 0xFF) + 64]
    groups = decode_groups(rom, [u32(rom, u32(rom, lay + 0x10) + 4 * k) for k in (2, 3)])
    out = {}
    for t in range(1024):
        e = struct.unpack_from("<H", block, 2 * t)[0]
        n = e & 0x3FF
        if not FREE[0] <= n <= FREE[1]:
            continue
        cell = (32 + t % 32, 32 + t // 32)
        seq = []
        for g in range(FRAMES):
            if n in vram:
                tile = vram[n]
            else:
                _, nt, first, frames = next(x for x in groups if x[2] <= n < x[2] + x[1])
                tile = frames[g][1][64 * (n - first):64 * (n - first) + 64]
            if e & 0x400:
                tile = hflip(tile)
            if e & 0x800:
                tile = vflip(tile)
            seq.append(tile)
        out[cell] = seq
    return out


# ===== list, source checks, second run =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "beam_struggle" in dev:                           # approved in r40: the trial list is an alias of dev
            self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev)
            self.assertLess(dev.index("beam_struggle"), dev.index("vegeta_ssj_scene"))   # My order rule
            return
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["beam_struggle"])

    def test_before_and_the_rom_are_pinned(self):
        b = built()
        self.assertEqual(hashlib.sha1(b["before"]).hexdigest(), BEFORE_SHA1)
        self.assertEqual(hashlib.sha1(b["rom"]).hexdigest(), ROM_SHA1)

    def test_on_r39_alone_it_is_the_trial_rom_the_owner_played(self):
        names = built()["names"]
        r39 = names[:names.index("bf_ki_pool") + 1]
        rom, _ = log2_build.assemble(log2_build.BASE, r39 + ["beam_struggle"])
        self.assertEqual(hashlib.sha1(rom).hexdigest(), TRIAL_SHA1)

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["beam_struggle"] = {}
        with self.assertRaises(ValueError):
            beam_struggle.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                           # the layout word is no longer vanilla either
        with self.assertRaises(ValueError):
            beam_struggle.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        r = b["before"]
        offs = (LAYOUT_WORD, VANILLA_LAYOUT - ROM_BASE + 0xC, VANILLA_LAYOUT - ROM_BASE + 0x4F, 0x4E2E74, 0x4E2E7B,
                VANILLA_BG0 - ROM_BASE + 0x18 + 4 * 5, VANILLA_TABLE - ROM_BASE + 4 * 166,
                u32(r, VANILLA_LAYOUT + 0x48) - ROM_BASE + 8, VANILLA_BLOCK5 - ROM_BASE + 8, 0x1DA4C8 + 2 * 73)
        for off in offs:
            rom, alloc = bytearray(r), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(Exception, msg=f"rom:0x{off:X}"):
                beam_struggle.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_the_layout_word_refuses(self):
        b = built()
        for site in ((LAYOUT_WORD + 2, 1, "other"), LAYOUT_WORD + 3):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            alloc.notes["other_module"] = {"sites": [site]}
            with self.assertRaises(ValueError, msg=str(site)):
                beam_struggle.apply(rom, alloc)
            self.assertEqual(bytes(rom), b["before"])

    def test_two_runs_give_the_same_bytes(self):
        b = built()
        rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
        beam_struggle.apply(rom, alloc)
        self.assertEqual(bytes(rom), b["rom"])


# ===== where the module writes =====

class SiteTests(unittest.TestCase):
    def test_base_rom_changes_only_at_the_layout_word(self):
        b = built()
        diff = [i for i in range(0x800000) if b["rom"][i] != b["before"][i]]
        self.assertTrue(set(diff) <= set(range(LAYOUT_WORD, LAYOUT_WORD + 4)), [hex(i) for i in diff[:8]])
        self.assertEqual(u32(b["before"], LAYOUT_WORD), VANILLA_LAYOUT)

    def test_expansion_writes_stay_in_the_noted_block(self):
        b = built()
        n = b["notes"]
        lo, hi = n["block"], n["block"] + n["size"]
        r, s = b["rom"], b["before"]
        self.assertTrue(r[0x800000:lo] == s[0x800000:lo] and r[hi:] == s[hi:])
        self.assertEqual(set(s[lo:hi]), {0xFF})
        self.assertEqual(n["sites"], [(LAYOUT_WORD, 4, "map 14,4 layout word"),
                                      (lo, n["size"], "beam struggle layout, groups, tiles")])
        self.assertTrue(lo <= b["layout"] - ROM_BASE < hi)


# ===== the decoded records =====

class RecordTests(unittest.TestCase):
    def test_layout_copy_changes_only_the_five_words(self):
        b = built()
        r, lay = b["rom"], b["layout"]
        new, old = r[lay - ROM_BASE:lay - ROM_BASE + 0x50], r[VANILLA_LAYOUT - ROM_BASE:VANILLA_LAYOUT - ROM_BASE + 0x50]
        changed = [k for k in range(0, 0x50, 4) if new[k:k + 4] != old[k:k + 4]]
        self.assertEqual(changed, [0xC, 0x10, 0x14, 0x48, 0x4C])
        self.assertEqual(u32(r, lay + 0xC), 4)

    def test_group_list_keeps_the_vanilla_groups_first(self):
        b = built()
        r = b["rom"]
        self.assertEqual(tuple(b["groups"][:2]), VANILLA_GROUPS)
        for rec, (nf, nt, first) in VANILLA_GROUP_BYTES.items():
            self.assertEqual((r[rec - ROM_BASE], r[rec - ROM_BASE + 1], struct.unpack_from("<H", r, rec - ROM_BASE + 2)[0]),
                             (nf, nt, first))
            self.assertEqual(r[rec - ROM_BASE:rec - ROM_BASE + 4 + 4 * nf], b["before"][rec - ROM_BASE:rec - ROM_BASE + 4 + 4 * nf])

    def test_new_groups_decode_to_their_tiles_and_fit_the_buffer(self):
        b = built()
        dec = decode_groups(b["rom"], b["groups"][2:])
        self.assertEqual([(nf, nt, first) for nf, nt, first, _ in dec],
                         [(FRAMES, GROUP_TILES[0], FREE[0] + STATIC_TILES),
                          (FRAMES, GROUP_TILES[1], FREE[0] + STATIC_TILES + GROUP_TILES[0])])
        for nf, nt, first, frames in dec:
            self.assertLessEqual(nt, 64)                     # 0x1000 B stack buffer @0x0800501E
            self.assertLessEqual(first + nt - 1, FREE[1])
            for dur, data in frames:
                self.assertEqual(dur, DURATION)
                self.assertEqual(len(data), 64 * nt)

    def test_every_stream_sets_literal_mode_first(self):
        """Bits 001 0000 0 1 lead every stream, so the decoder's entry r3 (0 or the frame type) does not matter."""
        b = built()
        r = b["rom"]
        lay = b["layout"]
        starts = [u32(r, rec + 4 + 4 * f) + 4 for rec in b["groups"][2:] for f in range(FRAMES)]
        starts += [u32(r, lay + 0x48) + 8, u32(r, u32(r, lay + 0x4C) + 4 * NEW_CHUNK) + 8,
                   u32(r, u32(r, lay + 0x14) + 0x18 + 4 * 5) + 8]
        for s in starts:
            self.assertEqual(u32(r, s) >> 23, 0b001000001, hex(s))     # first word, MSB first: 9 bits

    def test_index_list_adds_the_static_chunk(self):
        b = built()
        r, lay = b["rom"], b["layout"]
        kind, size, raw, _ = unpack_frame(r, u32(r, lay + 0x48) - ROM_BASE)
        new = entries(raw)
        old = entries(unpack_frame(r, u32(r, VANILLA_LAYOUT + 0x48) - ROM_BASE)[2])
        self.assertEqual(len(old), VANILLA_TILES)
        self.assertEqual(new[:VANILLA_TILES], old)
        self.assertEqual(new[VANILLA_TILES:], [(NEW_CHUNK << 8) | t for t in range(STATIC_TILES)])
        self.assertLessEqual(size, 0x700)                    # loader stack buffer @0x080050C8
        table = u32(r, lay + 0x4C)
        self.assertEqual(r[table - ROM_BASE:table - ROM_BASE + 4 * NEW_CHUNK], r[VANILLA_TABLE - ROM_BASE:VANILLA_TABLE - ROM_BASE + 4 * NEW_CHUNK])
        self.assertEqual(len(unpack_frame(r, u32(r, table + 4 * NEW_CHUNK) - ROM_BASE)[2]), 64 * STATIC_TILES)

    def test_bg0_record_changes_only_block_1_1(self):
        b = built()
        r = b["rom"]
        rec = u32(r, b["layout"] + 0x14)
        new, old = r[rec - ROM_BASE:rec - ROM_BASE + 0x58], r[VANILLA_BG0 - ROM_BASE:VANILLA_BG0 - ROM_BASE + 0x58]
        self.assertEqual([k for k in range(0, 0x58, 4) if new[k:k + 4] != old[k:k + 4]], [0x18 + 4 * 5])
        for off in (0x18, 0x1C, 0x20):                        # BG1-BG3 records stay vanilla
            self.assertEqual(u32(r, b["layout"] + off), u32(r, VANILLA_LAYOUT + off))

    def test_block_cells_outside_the_footprint_stay_vanilla(self):
        b = built()
        r, lay = b["rom"], b["layout"]
        new = unpack_frame(r, u32(r, u32(r, lay + 0x14) + 0x18 + 4 * 5) - ROM_BASE)[2]
        old = unpack_frame(r, VANILLA_BLOCK5 - ROM_BASE)[2]
        changed = [t for t in range(1024) if new[2 * t:2 * t + 2] != old[2 * t:2 * t + 2]]
        self.assertEqual(len(changed), MOCKUP_CELLS)
        names = [struct.unpack_from("<H", new, 2 * t)[0] & 0x3FF for t in changed]
        self.assertTrue(all(FREE[0] <= n <= FREE[0] + STATIC_TILES + sum(GROUP_TILES) - 1 for n in names))


# ===== tiles: only free slots, no vanilla beam or spark left =====

def load_vram(rom: bytes, layout: int) -> list:
    """BG tiles as the loader @0x080050C8 puts them in VRAM: entry i -> tile i; a run of entries with one chunk
    decodes table[chunk] once. None = the entry names a tile past its chunk (the game copies a stale buffer)."""
    ent = entries(unpack_frame(rom, u32(rom, layout + 0x48) - ROM_BASE)[2])
    table, out, chunk, cur = u32(rom, layout + 0x4C), [], None, None
    for e in ent:
        if e >> 8 != cur:
            cur = e >> 8
            chunk = unpack_frame(rom, u32(rom, table + 4 * cur) - ROM_BASE)[2]
        lo = 64 * (e & 0xFF)
        out.append(chunk[lo:lo + 64] if lo + 64 <= len(chunk) else None)
    return out


class LoadTests(unittest.TestCase):
    """The v1 in-game fault (my state log2_poc_r39_beam.ss2): the table copy kept words 0-166 and put the static
    chunk at word 167, which the vanilla list already names for tiles 441-595, so the arena ground showed wrong
    tiles. These tests load VRAM the way the game does and would have failed on v1."""

    def test_vanilla_tiles_load_unchanged(self):
        b = built()
        new, old = load_vram(b["rom"], b["layout"]), load_vram(b["rom"], VANILLA_LAYOUT)
        self.assertEqual(len(old), VANILLA_TILES)
        bad = [i for i in range(VANILLA_TILES) if new[i] != old[i]]
        self.assertEqual(bad, [])

    def test_every_entry_names_a_tile_inside_its_chunk(self):
        b = built()
        self.assertNotIn(None, load_vram(b["rom"], b["layout"]))

    def test_new_chunk_is_past_every_vanilla_chunk(self):
        b = built()
        old = entries(unpack_frame(b["rom"], u32(b["rom"], VANILLA_LAYOUT + 0x48) - ROM_BASE)[2])
        self.assertLess(max(e >> 8 for e in old), NEW_CHUNK)
        self.assertEqual(u32(b["rom"], VANILLA_TABLE + 4 * NEW_CHUNK), 1)    # block 0 frame type: table end
        self.assertEqual(VANILLA_TABLE + 4 * NEW_CHUNK, 0x084DF814)

    def test_new_tiles_load_the_static_art(self):
        b = built()
        new = load_vram(b["rom"], b["layout"])
        cells = screen_cells(b["rom"])
        static = {cells[c][0] for c in STATIC_CELLS}
        stored = new[VANILLA_TILES:VANILLA_TILES + STATIC_TILES]
        for t in static:                                   # every static cell is a stored tile under some flip
            self.assertTrue(any(t in (s, hflip(s), vflip(s), hflip(vflip(s))) for s in stored))


class CleanCutTests(unittest.TestCase):
    def test_sphere_takes_no_slice_of_a_bf_orb(self):
        """6:40 PM: no part of a BF orb that the disk slices may stay on the sphere (generator rule)."""
        from art import beam_struggle_art as art
        bf = art.load_bf()
        lp = art.palette(log2_build.BASE.read_bytes(), art.LOG2_BG_PAL)
        cut, _ = art.cut_remap(art.bf_screen(bf), art.palette(bf, art.BF_BG_PAL), lp)
        sphere = [k for k in cut if art.in_sphere(*k)]
        for ox, oy in SLICED_ORBS:
            circle = [(x, y) for (x, y) in cut if (x - ox) ** 2 + (y - oy) ** 2 <= 6.5 ** 2]
            inside = [p for p in circle if (p[0] - BF_CENTRE[0]) ** 2 + (p[1] - BF_CENTRE[1]) ** 2 <= BF_DISK_R ** 2]
            self.assertTrue(0 < len(inside) < len(circle), (ox, oy))      # the plain disk would slice it
            self.assertEqual([p for p in sphere if (p[0] - ox) ** 2 + (p[1] - oy) ** 2 <= 6.5 ** 2], [])

    def test_rom_frames_are_not_the_v1_cut(self):
        """The decoded frames differ from the v1 frames (digest in bridge_v1.txt); MockupTests pins the v2 digest."""
        cells = screen_cells(built()["rom"])
        h = hashlib.sha1()
        for g in range(FRAMES):
            h.update(b"".join(cells[c][g] for c in sorted(cells)))
        self.assertNotEqual(h.hexdigest(), "3348b7f5615399666e87a2c5ea46bb4337395a4b")


class TileTests(unittest.TestCase):
    def test_only_free_tiles_596_to_830_are_used(self):
        b = built()
        cells = screen_cells(b["rom"])
        used = set()
        r, lay = b["rom"], b["layout"]
        block = unpack_frame(r, u32(r, u32(r, lay + 0x14) + 0x18 + 4 * 5) - ROM_BASE)[2]
        for t in range(1024):
            n = struct.unpack_from("<H", block, 2 * t)[0] & 0x3FF
            if (32 + t % 32, 32 + t // 32) in cells:
                used.add(n)
        anim = sorted(n for n in used if n >= FREE[0] + STATIC_TILES)
        self.assertEqual(anim, list(range(FREE[0] + STATIC_TILES, FREE[0] + STATIC_TILES + sum(GROUP_TILES))))
        self.assertTrue(all(FREE[0] <= n <= FREE[1] for n in used))
        self.assertEqual(len(entries(unpack_frame(r, u32(r, lay + 0x48) - ROM_BASE)[2])), FREE[0] + STATIC_TILES)

    def test_no_vanilla_spark_or_beam_cell_shows(self):
        b = built()
        r, lay = b["rom"], b["layout"]
        tiles = []
        old = entries(unpack_frame(r, u32(r, VANILLA_LAYOUT + 0x48) - ROM_BASE)[2])
        for e in old:
            tiles.append(unpack_frame(r, u32(r, VANILLA_TABLE + 4 * (e >> 8)) - ROM_BASE)[2][64 * (e & 0xFF):64 * (e & 0xFF) + 64])
        rec = u32(r, lay + 0x14)
        stubs = []
        for k in range(16):
            p = u32(r, rec + 0x18 + 4 * k)
            if not p:
                continue
            m = unpack_frame(r, p - ROM_BASE)[2]
            for t in range(1024):
                n = struct.unpack_from("<H", m, 2 * t)[0] & 0x3FF
                beam_only = n < VANILLA_TILES and any(tiles[n]) and set(tiles[n]) - {0} <= BEAM_IDX
                if SPARK[0] <= n <= SPARK[1] or beam_only:
                    stubs.append((k, t, n))
        self.assertEqual(stubs, [])


# ===== the frames equal the mockup =====

class MockupTests(unittest.TestCase):
    def test_decoded_frames_equal_the_mockup_cell_for_cell(self):
        cells = screen_cells(built()["rom"])
        order = sorted(cells)
        self.assertEqual(len(order), MOCKUP_CELLS)
        h = hashlib.sha1()
        for g in range(FRAMES):
            h.update(b"".join(cells[c][g] for c in order))
        self.assertEqual(h.hexdigest(), MOCKUP_SHA1)
        self.assertEqual(len({b"".join(cells[c][g] for c in order) for g in range(FRAMES)}), MOCKUP_DISTINCT)

    def test_static_cells_and_flip_folding(self):
        b = built()
        cells = screen_cells(b["rom"])
        self.assertEqual(sorted(c for c, seq in cells.items() if len(set(seq)) == 1), STATIC_CELLS)
        r, lay = b["rom"], b["layout"]
        chunk = unpack_frame(r, u32(r, u32(r, lay + 0x4C) + 4 * NEW_CHUNK) - ROM_BASE)[2]
        self.assertEqual(len({chunk[64 * i:64 * i + 64] for i in range(STATIC_TILES)}), STATIC_TILES)

    def test_group_a_holds_the_sphere(self):
        """Group B (k3, one tick later) changes only with the 8-frame orb cycle: no sway, pulse or flash in it."""
        b = built()
        dec = decode_groups(b["rom"], b["groups"][3:4])
        payloads = [data for _, data in dec[0][3]]
        self.assertEqual(len(set(payloads)), 8)
        self.assertTrue(all(payloads[g] == payloads[g % 8] for g in range(FRAMES)))


if __name__ == "__main__":
    unittest.main()
