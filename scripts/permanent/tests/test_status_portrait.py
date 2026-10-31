r"""
test_status_portrait.py - Tests for the status page dialog portrait patch (patches.status_portrait).

Run (from the LOG root):
  py -3 -I -m unittest tests.test_status_portrait -v      (with -s scripts\permanent -t scripts\permanent: discover)
Builds the r19 patch list in memory (no ROM file): gohan_gi, ssj2_form, gohan_portraits, status_bonus, ssj2_idle,
cutscene_portraits, npc_gi, rage_text, then status_portrait. "before" is that list (r19 SHA-1 edd3df2e; the
hand frames move it), "rom" is "before" + the patch.
Source:  docs\tasks\2026-10-19-status-portrait\status-same-report.md. render() runs the whole status page (through the entry stub)
in the test_status interpreter. The real portrait() and cutscene hook run; every other base call is a Python
model: canvas create, frame unpack (real codec), the portrait blit 0x080211C8, the canvas copy 0x080236B4. BG
palette RAM starts as the menu palette rom:0x1D4F50 and logs every halfword write, so the color tests check what
the screen would show, not code text.
"""
import copy
import struct
import unittest
from pathlib import Path
from unittest import mock

import log2_build
import log_paths
from rom.rom_space import Allocator
from tests.test_status import EXIT, PageCpu, page_state, u32
from rom.thumb_dis import dis, listing
from rom.webfoot_decompress import ROM_BASE, decompress, unpack_frame

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE_ROM = (ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba").read_bytes()
R19 = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle", "cutscene_portraits", "npc_gi",
       "rage_text")
REMASTER = log_paths.PORTRAIT_SOURCES / "remaster"
MENU_PAL, OBJ_PAL = 0x1D4F50, 0x1DA6C8
PORTRAIT, BLOCK_LITERAL = 0x0800BDCC, 0xBE10
CREATE, UNPACK, PBLIT, COPY = 0x08020E5C, 0x0801F394, 0x080211C8, 0x080236B4
TEXT, PRINTF, BLIT, QUERY = 0x0801F636, 0x0801F6D8, 0x08021188, 0x08006E0A
QUIET = {0x08021F18: 0, 0x0802130A: 0, 0x0801F508: 0, 0x08020EAA: 0, 0x0801F110: 0, 0x08004214: 12,
         0x08021F30: 60, 0x08004230: 99, 0x0801F08C: 0x02030000, TEXT: 0, PRINTF: 0, BLIT: 0}
RECT = 0x081D94E4                         # page: ldr r2,=0x081d94d0 ; add r2,#0x14
SENTINEL = 0x08003B70                     # an address the nested portrait() run stops at (inside the dispatcher)
GI = {2: {59: 119, 62: 115}, 5: {59: 119, 62: 115}, 22: {59: 119, 62: 115}, 4: {61: 117}}  # cutscene_portraits
# The character menu art the census found (s3_slots.py), re-read here from the ROM: frames, tables, constants.
MENU_FRAMES = (0x080E18B0, 0x081D90AC, 0x081D9638, 0x086F869C, 0x081D99E0, 0x086FF614, 0x081D5D78, 0x081D918C,
               0x081D944C, 0x081D948C, 0x081D9BC0, 0x081D9BE4, 0x081D9C14, 0x081D9C48, 0x081D9834)
TAB_TABLE, ABILITY_TABLE, ITEM_TABLE, WIDGET_TABLE = 0x1D8F94, 0x1D9504, 0x6ADE24, 0x1D8FD4
MENU_CONSTANTS = {0, 1, 2, 4, 5, 8, 0x29, 0x95}   # clears, font shadow and text, HP and EP fills, level line


# ===== build (once, in memory) =====

_CACHE = {}


def built() -> dict:
    if _CACHE:
        return _CACHE
    import importlib
    rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
    alloc = Allocator(len(rom), log2_build.EXPANSION)
    for name in R19:
        importlib.import_module(f"patches.{name}").apply(rom, alloc)
    before, alloc_before = bytes(rom), copy.deepcopy(alloc)
    from patches import status_portrait
    status_portrait.apply(rom, alloc)
    _CACHE.update(before=before, alloc=alloc_before, rom=bytes(rom), notes=alloc.notes)
    return _CACHE


def bgr(v: int) -> tuple:
    v &= 0x7FFF                           # bit 15 is not a color bit (OBJ entry 168 is 0xAE24 in ROM)
    return ((v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3)


def palette(rom: bytes, off: int) -> list:
    return [bgr(v) for v in struct.unpack_from("<256H", rom, off)]


def dialog_id(rom: bytes, table: int, entry: int) -> int:
    """What the dialog box shows for a record in this entry: appearance +2, then the cutscene_portraits map."""
    d = rom[table + 20 * entry + 2]
    return GI.get(entry, {}).get(d, d)


def frame_of(rom: bytes, pid: int) -> bytes:
    block = u32(rom, ROM_BASE + BLOCK_LITERAL) - ROM_BASE
    return unpack_frame(rom, u32(rom, ROM_BASE + block + 4 + 4 * pid) - ROM_BASE)[2]


# ===== interpreter with palette RAM and a functional page model =====

class PaintCpu(PageCpu):
    def __init__(self, rom: bytes):
        super().__init__(rom)
        self.ram[0x05] = bytearray(0x400)
        self.ram[0x06] = bytearray(0x18000)
        self.ram[0x05][:0x200] = rom[MENU_PAL:MENU_PAL + 0x200]        # menu enter: rom:0x1D4F50 to BG palette
        self.events = []

    def store(self, a: int, size: int, v: int) -> None:
        if a >> 24 == 0x05:
            if size != 2:
                raise AssertionError(f"palette RAM write of {size} bytes at {a:#x}")
            self.events.append(("pram", (a & 0x3FF) // 2, v & 0xFFFF))
        super().store(a, size, v)


def render(rom: bytes, entry: int, override: bytes = None) -> dict:
    """Run the status page for char 0 (record appearance = entry). override replaces the portrait pixels."""
    cpu = PaintCpu(rom)
    base = page_state(rom, (50, 50, 50), where="none")              # test_status layout: THIS, record, stack
    cpu.ram[0x02][:], cpu.ram[0x03][:] = base.ram[0x02], base.ram[0x03]
    cpu.r[:] = base.r
    cpu.store(0x03000E90 + 0xC + 8, 1, entry)                      # record 0 appearance (STRUCT + 0x14)
    heap, canvases, out = [0x02010000], {}, {}

    def create(c):
        w, h = c.r[1], c.r[2]
        buf = heap[0]
        heap[0] += (w * h + 15) & ~15
        c.store(c.r[0] + 0x24, 4, buf)
        c.store(c.r[0] + 0x2C, 4, w)
        canvases[c.r[0]] = (buf, w, h)
        return 0

    def unpack(c):
        data = unpack_frame(rom, c.r[0] - ROM_BASE)[2]
        if c.r[1] in [b for b, w, h in canvases.values() if (w, h) == (64, 64)]:
            out["portrait_hdr"] = c.r[0]
            data = override if override is not None else data
            out["portrait_px"] = bytes(data)
        buf, off = c._at(c.r[1], len(data))
        buf[off:off + len(data)] = data
        return 0

    def pblit(c):
        cbuf, cw, _ = canvases[c.r[0]]
        x0, y0, x1, y1 = (c.load(c.r[2] + 4 * i, 4) for i in range(4))
        for y in range(y0, y1):
            for x in range(x0, x1):
                v = c.load(c.r[1] + (y - y0) * (x1 - x0) + x - x0, 1)
                if v:
                    c.store(cbuf + y * cw + x, 1, v)
        cpu.events.append(("pblit", c.r[1], (x0, y0, x1, y1)))
        return 0

    def vcopy(c):
        cbuf, cw, ch = canvases[c.r[0]]
        cpu.events.append(("copy", c.r[1], bytes(c.load(cbuf + i, 1) for i in range(cw * ch)) if cw == 208 else b""))
        return 0

    def portrait(c):
        sub = PageCpu(rom)
        sub.ram = c.ram
        sub.r[0], sub.r[13], sub.r[14] = c.r[0], (c.r[13] - 0x40) & 0xFFFFFFFF, SENTINEL | 1
        sub.run(PORTRAIT, {SENTINEL: "exit"}, limit=200)
        out["portrait_id"] = c.r[0]
        return sub.r[0]

    stops = {t: (lambda v: lambda c: v)(v) for t, v in QUIET.items()}
    stops.update({CREATE: create, UNPACK: unpack, PBLIT: pblit, COPY: vcopy, PORTRAIT: portrait,
                  QUERY: lambda c: 0, EXIT: "exit"})
    sp, saved = cpu.r[13], cpu.r[4:8]
    if cpu.run(0x0800379C, stops, limit=200000) != "exit":
        raise AssertionError("page did not return")
    if cpu.r[13] != sp or cpu.r[4:8] != saved:
        raise AssertionError("page did not restore sp and r4-r7")
    copies = [e for e in cpu.events if e[0] == "copy" and e[2]]
    if len(copies) != 1:
        raise AssertionError(f"{len(copies)} main canvas copies")
    canvas = copies[0][2]
    pram = list(struct.unpack_from("<256H", cpu.ram[0x05], 0))
    region = bytes(canvas[(4 + y) * 208 + 144 + x] for y in range(64) for x in range(64))
    out.update(events=cpu.events, region=region, pram=pram, rgb=[bgr(pram[v]) for v in region])
    return out


REMASTER_NAMES = ("goku_A_v2.png", "vegeta_A.png", "gohan_ssj_A.png", "gohan_ssj2_A.png", "gohan_base_A.png",
                  "goku_soft_A.png", "vegeta_soft_A.png", "gohan_ssj_soft_A.png", "gohan_ssj2_soft_A.png",
                  "gohan_base_soft_A.png")   # dialog art (OBJ indices); another task may still be writing the folder


def remaster_png(name: str):
    """64x64 indexed pixels of a remaster dialog PNG, or None when it is missing or unreadable."""
    from PIL import Image
    try:
        with Image.open(REMASTER / name) as img:
            return img.tobytes() if img.mode == "P" and img.size == (64, 64) else None
    except OSError:
        return None


# ===== tests =====

class StatusPortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]
        cls.page = b["notes"]["status_bonus"]["page"] + ROM_BASE
        cls.table = b["notes"]["ssj2_form"]["table"]
        cls.obj = palette(BASE_ROM, OBJ_PAL)

    def test_before_is_the_r19_patch_list(self):        # its SHA-1 moves when hand frames change; check the parts used
        self.assertLessEqual(set(R19), set(self.notes))
        page = self.notes["status_bonus"]["page"]
        self.assertEqual(self.before[page + 0x2F0:page + 0x2F2], bytes.fromhex("c078"))   # ldrb r0,[r0,#0x3]

    def test_rom_differs_only_at_two_page_sites_and_new_data(self):
        n = self.notes["status_portrait"]
        sites = {n["plus_byte"]: 2, n["copy_site"]: 4}
        new = range(n["pool"], n["code"] + 0x100)
        diff = [i for i in range(len(self.rom)) if self.rom[i] != self.before[i]]
        stray = [hex(i) for i in diff if i not in new and not any(s <= i < s + k for s, k in sites.items())]
        self.assertEqual(stray, [])
        self.assertEqual([t for _, t in listing(self.before, n["plus_byte"] + ROM_BASE, 1)], ["ldrb r0,[r0,#0x3]"])
        self.assertEqual([t for _, t in listing(self.rom, n["plus_byte"] + ROM_BASE, 1)], ["ldrb r0,[r0,#0x2]"])
        self.assertEqual(dis(self.rom, n["copy_site"] + ROM_BASE)[0], f"bl {n['paint'] + ROM_BASE:#x}")

    def test_no_rom_palette_or_portrait_frame_changes(self):
        for off in (MENU_PAL, OBJ_PAL):
            self.assertEqual(self.rom[off:off + 512], BASE_ROM[off:off + 512])
        for pid in range(8, 122):
            self.assertEqual(frame_of(self.rom, pid), frame_of(self.before, pid), pid)

    def test_pool_is_free_in_character_menu_art(self):
        from patches.status_portrait import POOL
        rom = self.rom                                               # menu art as the patched ROM holds it
        used = set(MENU_CONSTANTS) | {58, 69, 34}                    # status_bonus gold rows
        frames = list(MENU_FRAMES) + [u32(rom, ROM_BASE + TAB_TABLE + 4 * i) for i in range(1, 11)]
        frames += [u32(rom, ROM_BASE + ABILITY_TABLE + 4 * i) for i in range(10)]
        i = 0
        while ROM_BASE <= u32(rom, ROM_BASE + ITEM_TABLE + 0x38 * i + 0x30) < 0x08030000:
            frames += [u32(rom, ROM_BASE + ITEM_TABLE + 0x38 * i + o) for o in (0x28, 0x2C)]
            i += 1
        self.assertEqual(i, 17)
        for a in frames:
            if a:                                                    # some items have no +0x28 art
                used |= set(unpack_frame(rom, a - ROM_BASE)[2])
        for r in range(12):
            lst, w, h, _ = struct.unpack_from("<4I", rom, WIDGET_TABLE + 16 * r)
            for k in range(u32(rom, lst) if lst else 0):
                used |= set(decompress(rom, u32(rom, lst + 4 + 4 * k) - ROM_BASE, limit=w * h)[0])
        self.assertEqual(sorted(set(POOL) & used), [])
        self.assertEqual(len(POOL), 64)

    def test_every_entry_shows_dialog_art_in_dialog_colors(self):
        from patches.status_portrait import POOL
        for entry in range(23):
            with self.subTest(entry=entry):
                pid = dialog_id(self.rom, self.table, entry)
                r = render(self.rom, entry)
                self.assertEqual(r["portrait_id"], self.rom[self.table + 20 * entry + 2])    # +2, not +3
                self.assertEqual(r["portrait_px"], frame_of(self.rom, pid))
                self.assertEqual(r["rgb"], [self.obj[k] for k in frame_of(self.rom, pid)])
                writes = [e for e in r["events"] if e[0] == "pram"]
                self.assertTrue(writes)
                self.assertLessEqual({w[1] for w in writes}, set(POOL))
                self.assertEqual(len({w[1] for w in writes}), len(set(frame_of(self.rom, pid))))

    def test_palette_written_after_the_canvas_copy(self):
        r = render(self.rom, 19)                                    # Goku
        ev = r["events"]
        main = [i for i, e in enumerate(ev) if e[0] == "copy" and e[1] == 0x06006940]
        self.assertEqual(len(main), 1)
        writes = [i for i, e in enumerate(ev) if e[0] == "pram"]
        self.assertTrue(writes and min(writes) > main[0])
        blits = [e for e in r["events"] if e[0] == "pblit"]
        self.assertEqual([b[2] for b in blits], [(144, 4, 208, 68)] * 2)     # vanilla blit, then the remapped one

    def test_vanilla_status_page_unchanged_in_before(self):
        r = render(self.before, 19)
        self.assertEqual(r["portrait_id"], self.before[self.table + 20 * 19 + 3])   # +3: the status twin
        self.assertFalse([e for e in r["events"] if e[0] == "pram"])
        menu = palette(BASE_ROM, MENU_PAL)
        self.assertEqual(r["rgb"], [menu[k] for k in frame_of(self.before, self.before[self.table + 20 * 19 + 3])])

    def test_remaster_pngs_exact(self):
        for name in REMASTER_NAMES:
            with self.subTest(png=name):
                px = remaster_png(name)
                if px is None:
                    self.skipTest(f"{name} missing or unreadable")
                r = render(self.rom, 2, override=px)
                self.assertEqual(r["rgb"], [self.obj[k] for k in px])

    def test_overflow_reuses_last_slot_and_loads_only_64(self):
        from patches.status_portrait import POOL
        px = bytes((i % 70) + 26 for i in range(4096))             # 70 colors
        r = render(self.rom, 19, override=px)
        writes = {w[1]: w[2] for w in r["events"] if w[0] == "pram"}
        self.assertEqual(sorted(writes), sorted(POOL))
        first = list(dict.fromkeys(px))
        for k in first[:64]:
            self.assertIn(self.obj[k], r["rgb"])
        self.assertEqual({r["region"][i] for i in range(4096) if px[i] in first[64:]}, {POOL[-1]})

    def test_index_zero_stays_transparent(self):
        from patches.status_portrait import POOL
        px = bytes([0] * 64 + [114] * (4096 - 64))                  # top row transparent
        r = render(self.rom, 19, override=px)
        bg = render(self.before, 19, override=px)["region"][:64]     # what the vanilla blit leaves there
        self.assertEqual(r["region"][:64], bg)
        self.assertEqual(set(r["region"][64:]), {POOL[0]})
        self.assertEqual([e[1:] for e in r["events"] if e[0] == "pram"],
                         [(POOL[0], struct.unpack_from("<H", BASE_ROM, OBJ_PAL + 2 * 114)[0])])

    def test_apply_fails_closed(self):
        from patches import status_portrait
        b = built()
        n = b["notes"]["status_portrait"]
        for off in (n["plus_byte"], n["copy_site"], n["copy_site"] - 2):
            rom = bytearray(b["before"])
            rom[off] ^= 0xFF
            before = bytes(rom)
            with self.assertRaises(ValueError, msg=hex(off)):
                status_portrait.apply(rom, copy.deepcopy(b["alloc"]))
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run them first"):
            status_portrait.apply(bytearray(b["before"]), Allocator(len(b["before"]), [(0xF00000, 0x100000)]))
        rom = bytearray(b["before"])
        with mock.patch.object(status_portrait, "POOL", status_portrait.POOL[:20]):
            with self.assertRaisesRegex(ValueError, "more colors than the 20 pool slots"):
                status_portrait.apply(rom, copy.deepcopy(b["alloc"]))
        self.assertEqual(bytes(rom), b["before"])

    def test_new_data_in_expansion(self):
        n = self.notes["status_portrait"]
        self.assertGreaterEqual(n["pool"], 0x800000)
        self.assertGreaterEqual(n["code"], 0x800000)
        from patches.status_portrait import POOL
        self.assertEqual(self.rom[n["pool"]:n["pool"] + 64], bytes(POOL))


if __name__ == "__main__":
    unittest.main()
