r"""
test_cutscene.py - Tests for the cutscene portrait hook (patches.cutscene_portraits) and the records it serves.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds the r13 patch list in memory (gohan_gi, ssj2_form, gohan_portraits, status_bonus, ssj2_idle) and the r14
list (the same plus cutscene_portraits). portrait() 0x0800BDCC runs in the test_status interpreter (PageCpu) as
thumb_dis text, never through the encoder: ids 1-7 go through the real 0x08026440 and the relocated appearance
table, so speaker 1 in Rage reaches the hook as 61. The block and the table come from the ROM literals
(rom:0xBE10, rom:0x26458), never from the patch notes.
Source:  docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits-report.md, docs\research\re-portraits.md sections 1 and 3.
"""
import importlib
import struct
import unittest

import log2_build
from rom.rom_space import Allocator
from tests.test_status import PageCpu
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, decompress

# ===== constants =====
BASE_ROM = log2_build.BASE.read_bytes()
R13 = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle")
PORTRAIT, SITE, BLOCK_LITERAL, PLUS2_LITERAL = 0x0800BDCC, 0x0800BE06, 0xBE10, 0x26458
STRUCT, STACK, RET = 0x03000E90, 0x03007F00, 0x0EEE0000
GOHAN_IDS = range(56, 63)
ARMOR_ENTRIES, GI_ENTRIES, RAGE = (0, 1, 3), (2, 5, 22), 4
GI_MAP, RAGE_MAP = {59: 119, 62: 115}, {61: 117}               # the brief's mapping (report "Fix")
# Shape C (scene-table pointers): every record with a raw Gohan portrait byte 59 (report "Records")
POST_CHAMBER_59 = (0x3DB930, 0x3DBABC, 0x3DBFDC, 0x3DC1AC, 0x3DC870, 0x3DCE54, 0x3DCECE, 0x3E8170,
                   0x3E81A0, 0x3E9230, 0x3E934C)
OWNER_LINE = 0x3DBFDC                                           # Kami's lookout, post-Cell (my screenshot)
SCRIPT_REGION = (0x3B5000, 0x420000)

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        for name in R13:
            importlib.import_module(f"patches.{name}").apply(rom, alloc)
        _CACHE["before"] = bytes(rom)
        importlib.import_module("patches.cutscene_portraits").apply(rom, alloc)
        _CACHE["rom"], _CACHE["notes"] = bytes(rom), alloc.notes
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def frame(rom: bytes, pid: int) -> int:
    """The table word for pid, read through the ROM's own block literal."""
    return u32(rom, u32(rom, BLOCK_LITERAL) - ROM_BASE + 4 + 4 * pid)


def portrait(rom: bytes, pid: int, gohan_entry: int, leader: int = 0, others: int = 6) -> tuple:
    """portrait(pid) with Gohan's record (record 0) in gohan_entry; returns (r0, cpu)."""
    cpu = PageCpu(rom)
    cpu.store(STRUCT, 1, leader)
    for rec in range(6):
        cpu.store(STRUCT + 0xC + 28 * rec + 8, 1, gohan_entry if rec == 0 else others)
    cpu.r[0], cpu.r[2], cpu.r[13], cpu.r[14] = pid, 0x22222222, STACK, RET | 1
    cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
    if cpu.run(PORTRAIT | 1, {RET: "ret"}) != "ret":
        raise AssertionError("portrait() did not return")
    return cpu.r[0], cpu


def want_id(pid: int, entry: int) -> int:
    if entry in GI_ENTRIES:
        return GI_MAP.get(pid, pid)
    return RAGE_MAP.get(pid, pid) if entry == RAGE else pid


def pointed_records(rom: bytes) -> dict:
    """Shape C: {record offset: portrait byte} for aligned words that point at a dialog record header."""
    lo, hi = SCRIPT_REGION
    out = {}
    for o in range(0, log2_build.BASE_SIZE, 4):
        p = u32(rom, o) - ROM_BASE
        if lo <= p < hi and rom[p + 1] == 0 and 1 <= rom[p + 2] <= 4:
            out[p] = rom[p + 3]
    return out


class HookSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.hook = cls.notes["cutscene_portraits"]["hook"] + ROM_BASE

    def test_site_is_a_long_jump_to_the_hook(self):
        o = SITE - ROM_BASE
        self.assertEqual(BASE_ROM[o:o + 10].hex(), "0249800004310858e0e7")     # ldr ; lsl ; add ; ldr ; b
        self.assertEqual([t for _, t in listing(self.rom, SITE, 2)], [f"ldr r1,={self.hook | 1:#010x}", "bx r1"])
        self.assertEqual(u32(self.rom, o + 6), self.hook | 1)
        self.assertEqual(self.rom[BLOCK_LITERAL:BLOCK_LITERAL + 4], self.before[BLOCK_LITERAL:BLOCK_LITERAL + 4])
        self.assertEqual(self.rom[PORTRAIT - ROM_BASE:o], BASE_ROM[PORTRAIT - ROM_BASE:o])

    def test_only_the_site_changes_in_the_base_8mb(self):
        diff = [i for i in range(log2_build.BASE_SIZE) if self.before[i] != self.rom[i]]
        self.assertEqual(diff, [i for i in range(SITE - ROM_BASE, SITE - ROM_BASE + 10) if i != 0xBE07])
        self.assertEqual(self.rom[0xBE07], 0x49)                     # ldr r1 keeps its high byte

    def test_expansion_adds_only_the_hook(self):
        n = self.notes["cutscene_portraits"]
        diff = [i for i in range(log2_build.BASE_SIZE, log2_build.ROM_SIZE) if self.before[i] != self.rom[i]]
        self.assertTrue(diff and n["code"] <= diff[0] and diff[-1] < n["code"] + n["size"])
        self.assertTrue(all(b == 0xFF for b in self.before[n["code"]:n["code"] + n["size"]]))

    def test_only_the_bgt_enters_the_site(self):              # shapes: BL, B, Bcc in base code; aligned words
        site = range(SITE, SITE + 10)
        h = lambda a: struct.unpack_from("<H", BASE_ROM, a - ROM_BASE)[0]   # noqa: E731
        found = []
        for a in range(ROM_BASE, ROM_BASE + 0x30000, 2):
            v, t = h(a), None
            if v & 0xF800 == 0xF000 and h(a + 2) & 0xF800 == 0xF800:
                off = (v & 0x7FF) << 12 | (h(a + 2) & 0x7FF) << 1
                t = a + 4 + off - ((1 << 23) if off & (1 << 22) else 0)
            elif v & 0xF800 == 0xE000:
                t = a + 4 + ((v & 0x7FF) << 1) - (0x1000 if v & 0x400 else 0)
            elif v & 0xF000 == 0xD000 and (v >> 8) & 0xF < 0xE:
                t = a + 4 + ((v & 0xFF) << 1) - (0x200 if v & 0x80 else 0)
            if t in site:
                found.append((a, t))
        self.assertEqual(found, [(0x0800BDF0, SITE)])
        words = [o for o in range(0, log2_build.BASE_SIZE, 4) if (u32(BASE_ROM, o) & ~1) in site]
        self.assertEqual(words, [])

    def test_hook_disassembles_as_expected(self):
        h, block = self.hook, u32(self.rom, BLOCK_LITERAL)
        want = [f"ldr r1,={block:#010x}", "ldr r3,[r1,#0x0]", "ldrb r3,[r3,#0x14]", "cmp r0,#0x3d",
                f"bne {h + 0x12:#x}", "cmp r3,#0x4", f"bne {h + 0x2a:#x}", "mov r0,#0x75", f"b {h + 0x2a:#x}",
                "cmp r3,#0x2", f"beq {h + 0x1e:#x}", "cmp r3,#0x5", f"beq {h + 0x1e:#x}", "cmp r3,#0x16",
                f"bne {h + 0x2a:#x}", "cmp r0,#0x3b", f"bne {h + 0x24:#x}", "mov r0,#0x77", "cmp r0,#0x3e",
                f"bne {h + 0x2a:#x}", "mov r0,#0x73", "lsl r0,r0,#2", "add r1,#0x4", "ldr r0,[r1,r0]",
                "pop {r3,pc}"]
        self.assertEqual([t for _, t in listing(self.rom, h, len(want))], want)
        self.assertGreaterEqual(self.notes["cutscene_portraits"]["code"], 0x800000)

    def test_apply_fails_closed(self):
        from patches import cutscene_portraits
        table = u32(self.before, PLUS2_LITERAL) - ROM_BASE
        for off, junk in ((SITE - ROM_BASE, b"\0"), (BLOCK_LITERAL, b"\0"), (table + 20 * RAGE + 1, bytes([58])),
                          (table + 20 * 2 + 1, bytes([56]))):
            rom = bytearray(self.before)
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes.update({k: dict(v) for k, v in self.notes.items() if k != "cutscene_portraits"})
            with self.assertRaises(ValueError, msg=hex(off)):
                cutscene_portraits.apply(rom, alloc)
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run them first"):
            cutscene_portraits.apply(bytearray(self.before), Allocator(len(self.before), [(0xF00000, 0x100000)]))


class HookBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]

    def test_vanilla_interpreter_reads_the_table(self):        # the interpreter against the original code
        for pid in (59, 61, 94, 12):
            self.assertEqual(portrait(BASE_ROM, pid, 2)[0], frame(BASE_ROM, pid), pid)
        self.assertEqual(portrait(BASE_ROM, 0, 2)[0], 0)

    def test_gohan_ids_follow_his_record(self):                # brief test step 5, every Gohan id and entry
        for pid in GOHAN_IDS:
            for entry in ARMOR_ENTRIES + GI_ENTRIES + (RAGE,):
                got = portrait(self.rom, pid, entry)[0]
                self.assertEqual(got, frame(self.rom, want_id(pid, entry)), (pid, entry))
                if want_id(pid, entry) == pid:
                    self.assertEqual(got, portrait(self.before, pid, entry)[0], (pid, entry))

    def test_armor_entry_keeps_the_armor_frame(self):
        for pid in GOHAN_IDS:
            self.assertEqual(portrait(self.rom, pid, 1)[0], frame(BASE_ROM, pid), pid)   # vanilla header

    def test_gi_entries_show_the_gi_frames(self):
        notes = built()["notes"]["gohan_portraits"]["frames"]
        for entry in GI_ENTRIES:
            self.assertEqual(portrait(self.rom, 59, entry)[0], notes[119] + ROM_BASE, entry)
            self.assertEqual(portrait(self.rom, 62, entry)[0], notes[115] + ROM_BASE, entry)
        self.assertEqual(portrait(self.rom, 61, RAGE)[0], notes[117] + ROM_BASE)

    def test_speaker_ids_resolve_through_the_record(self):     # Rage lines use speaker 1 (leader Gohan)
        for sid in (1, 2):
            self.assertEqual(portrait(self.before, sid, RAGE)[0], frame(self.rom, 61), sid)   # r13: armor Rage
            self.assertEqual(portrait(self.rom, sid, RAGE)[0], frame(self.rom, 117), sid)
            self.assertEqual(portrait(self.rom, sid, 2)[0], frame(self.rom, 119), sid)
            self.assertEqual(portrait(self.rom, sid, 1)[0], frame(self.rom, 58), sid)
        for entry in ARMOR_ENTRIES + GI_ENTRIES + (RAGE,):            # leader Piccolo (record 1, entry 6)
            self.assertEqual(portrait(self.rom, 1, entry, leader=1)[0], frame(self.rom, 90), entry)

    def test_other_ids_unchanged(self):                        # Piccolo 94, status ids, the gi ids, the rest
        ids = [pid for pid in range(8, 121) if pid not in GOHAN_IDS]
        for entry in (1, 2, RAGE, 22):
            for pid in ids:
                self.assertEqual(portrait(self.rom, pid, entry)[0], portrait(self.before, pid, entry)[0],
                                 (pid, entry))
        self.assertEqual(portrait(self.rom, 94, 2)[0], frame(BASE_ROM, 94))

    def test_registers_and_stack_kept(self):
        for pid, entry in ((59, 2), (61, RAGE), (94, 2), (1, RAGE), (56, 1)):
            _, cpu = portrait(self.rom, pid, entry)
            self.assertEqual((cpu.r[2], cpu.r[13]), (0x22222222, STACK), (pid, entry))
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], (pid, entry))


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = built()["rom"]
        cls.records = pointed_records(cls.rom)

    def test_owner_line_is_a_type_2_record_with_portrait_59(self):
        self.assertEqual(self.rom[OWNER_LINE:OWNER_LINE + 8].hex(), "0300023be7630020")
        text, _ = decompress(self.rom, OWNER_LINE + 4)
        self.assertTrue(text.rstrip(b"\0").endswith(b"That was how I was able to beat Cell!  My dad helped me."))

    def test_raw_gohan_ids_by_scene_pointer(self):
        by_id = {pid: sorted(o for o, p in self.records.items() if p == pid) for pid in GOHAN_IDS}
        self.assertEqual(tuple(by_id[59]), POST_CHAMBER_59)
        self.assertEqual({pid: len(by_id[pid]) for pid in (58, 60, 61, 62)}, {58: 0, 60: 0, 61: 0, 62: 0})
        self.assertEqual((len(by_id[56]), len(by_id[57])), (15, 14))

    def test_script_region_is_vanilla_but_the_rage_push(self):    # fix A edits no record byte
        lo, hi = SCRIPT_REGION
        diff = [i for i in range(lo, hi) if self.rom[i] != BASE_ROM[i]]
        self.assertEqual(diff, [0x3EA365, 0x3EA366, 0x3EA368])

    def test_chamber_and_post_cell_scripts_set_entry_2_first(self):   # ext 73 (0, 56) before the 59 lines
        for off in (0x3DB627, 0x3EBFF8):
            self.assertEqual(self.rom[off:off + 6].hex(), "1d0200700249", hex(off))
        copy = u32(self.rom, 0x42F0) - ROM_BASE                       # reverse lookup copy: 56 is entry 2
        self.assertEqual(next(e for e in range(22) if self.rom[copy + 20 * e + 1] == 56), 2)


if __name__ == "__main__":
    unittest.main()
