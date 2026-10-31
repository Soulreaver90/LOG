r"""
test_rage_text.py - Tests for patches.rage_text: the Rage message says "Gohan has transformed" / "into Super Saiyan 2!".

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_rage_text.py -v
Builds the r18 patch list in memory, then rage_text. The layout tests run the game's own line breaker
0x0801F7FC (the test_status interpreter plus stmia) on the record text the scene list now points at.
Source:  docs\tasks\2026-10-19-r19-build\r19-build.md, r19-build-report.md (reader evidence).
"""
import importlib
import struct
import unittest

import log2_build
from rom.rom_space import Allocator
from tests.test_ssj2 import REGNO
from tests.test_status import PageCpu
from rom.webfoot_decompress import ROM_BASE

# ===== constants =====
R18 = ("gohan_gi", "ssj2_form", "gohan_portraits", "status_bonus", "ssj2_idle", "cutscene_portraits", "npc_gi")
RECORD, LIST_WORD, NEXT_RECORD, NEXT_WORD = 0x3EA388, 0x3EA474, 0x3EA3B4, 0x3EA478
OLD = bytes.fromhex("1e000100405e") + b"Gohan has entered Super Saiyan Rage!" + b"\0\0" + bytes.fromhex("1f000128")
NEW = bytes.fromhex("1e000100405e") + b"Gohan has transformed\x0ainto Super Saiyan 2!\0"
NEXT = bytes.fromhex("1f000128") + b"You wretched child!!!\x0bNOW TASTE MY TRUE POWER!!!"
BREAK, FONT, WIDTH = 0x0801F7FC, 0x0802CC64, 0x90     # line breaker, dialog font (canvas +0xC), line width
CANVAS, OUT, STACK, RET = 0x03001000, 0x03001100, 0x03007E00, 0x0EEE0000
_CACHE = {}


def built() -> dict:
    if not _CACHE:
        rom = bytearray(log2_build.BASE.read_bytes()) + b"\xFF" * (log2_build.ROM_SIZE - log2_build.BASE_SIZE)
        alloc = Allocator(len(rom), log2_build.EXPANSION)
        for name in R18:
            importlib.import_module(f"patches.{name}").apply(rom, alloc)
        _CACHE["before"], _CACHE["mark"] = bytes(rom), max(a + n for a, n in alloc.used())
        importlib.import_module("patches.rage_text").apply(rom, alloc)
        _CACHE["rom"], _CACHE["notes"] = bytes(rom), alloc.notes
    return _CACHE


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def words_to(rom: bytes, target: int) -> list:
    pat, out, i = struct.pack("<I", target), [], rom.find(struct.pack("<I", target))
    while i >= 0:
        out.append(i)
        i = rom.find(pat, i + 1)
    return out


# ===== the game's line breaker =====

class TextCpu(PageCpu):
    def _step(self, nxt: int, text: str) -> int:
        op, _, rest = text.partition(" ")
        if op != "stmia":
            return super()._step(nxt, text)
        base, regs = rest.split(",", 1)
        b = REGNO[base.rstrip("!")]
        for n in sorted(REGNO[x] for x in regs.strip("{}").split(",")):
            self.store(self.r[b], 4, self.r[n])
            self.r[b] += 4
        return nxt


def lines(rom: bytes, text: int) -> list:
    """[(line bytes, width, done, end byte)] as sub_0800B8B6 walks the text at GBA address `text` to its 00."""
    cpu, out, at = TextCpu(rom), [], text
    cpu.store(CANVAS + 0xC, 4, FONT)
    for _ in range(8):
        cpu.r[0], cpu.r[1], cpu.r[2], cpu.r[3] = CANVAS, at, WIDTH, OUT
        cpu.r[13], cpu.r[14] = STACK, RET | 1
        if cpu.run(BREAK | 1, {RET: "ret"}, limit=5000) != "ret":
            raise AssertionError("line breaker did not return")
        s, e, w, done = (cpu.load(OUT + 4 * i, 4) for i in range(4))
        out.append((bytes(cpu.load(a, 1) for a in range(s, e)), w, done, cpu.load(e, 1)))
        if cpu.load(e, 1) == 0:
            return out
        at = e
    raise AssertionError("text has no 00 within 8 lines")


class RecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes, cls.mark = b["rom"], b["before"], b["notes"], b["mark"]
        cls.new = cls.notes["rage_text"]["record"]

    def test_old_record_untouched(self):
        self.assertEqual(self.before[RECORD:RECORD + len(OLD)], OLD)
        self.assertEqual(self.rom[RECORD:RECORD + len(OLD)], OLD)

    def test_new_record_bytes(self):
        self.assertEqual(len(NEW), 49)
        self.assertEqual(self.new % 4, 0)
        self.assertGreaterEqual(self.new, log2_build.BASE_SIZE)
        self.assertEqual(self.rom[self.new:self.new + len(NEW)], NEW)
        self.assertEqual(self.before[self.new:self.new + len(NEW)], b"\xFF" * len(NEW))

    def test_pointer_word(self):
        self.assertEqual(u32(self.before, LIST_WORD), RECORD + ROM_BASE)
        self.assertEqual(u32(self.rom, LIST_WORD), self.new + ROM_BASE)
        self.assertEqual(words_to(self.before, RECORD + ROM_BASE), [LIST_WORD])     # the only reference
        self.assertEqual(words_to(self.rom, RECORD + ROM_BASE), [])
        self.assertEqual(words_to(self.rom, self.new + ROM_BASE), [LIST_WORD])

    def test_next_record_and_its_pointer_untouched(self):
        for rom in (self.before, self.rom):
            self.assertEqual(rom[NEXT_RECORD:NEXT_RECORD + len(NEXT)], NEXT)
            self.assertEqual(words_to(rom, NEXT_RECORD + ROM_BASE), [NEXT_WORD])
        self.assertEqual(self.rom[LIST_WORD - 8:LIST_WORD], self.before[LIST_WORD - 8:LIST_WORD])
        self.assertEqual(self.rom[NEXT_WORD:NEXT_WORD + 8], self.before[NEXT_WORD:NEXT_WORD + 8])

    def test_diff_only_at_the_word_and_the_record(self):
        diff = [i for i in range(len(self.rom)) if self.rom[i] != self.before[i]]
        allowed = set(range(LIST_WORD, LIST_WORD + 4)) | set(range(self.new, self.new + len(NEW)))
        self.assertTrue(set(diff) <= allowed, [hex(i) for i in diff[:8]])
        self.assertEqual(self.new, -(-self.mark // 4) * 4)

    def test_apply_fails_closed(self):
        from patches import rage_text
        for off in (RECORD, RECORD + 0x1E, RECORD + 0x2A, NEXT_RECORD + 3, LIST_WORD, NEXT_WORD + 1):
            rom = bytearray(self.before)
            rom[off] ^= 0x01
            before = bytes(rom)
            with self.assertRaises(ValueError, msg=hex(off)):
                rage_text.apply(rom, Allocator(len(rom), [(0xF00000, 0x100000)]))
            self.assertEqual(bytes(rom), before, hex(off))


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]

    def test_font_is_the_dialog_canvas_font(self):        # sub_0800BAB4 stores it at canvas +0xC
        self.assertEqual(u32(self.rom, 0xBDA0), FONT)

    def test_vanilla_rage_wraps_after_super(self):        # calibrates the run: the box showed 23 characters
        text = u32(self.before, LIST_WORD) + 5             # dialog_box skips the 40 prefix
        got = [(t, d) for t, _, d, _ in lines(self.before, text)]
        self.assertEqual(got, [(b"^Gohan has entered Super", 0), (b"Saiyan Rage!", 1)])

    def test_new_text_is_two_lines_in_one_box(self):
        got = lines(self.rom, u32(self.rom, LIST_WORD) + 5)
        self.assertEqual([(t, d, e) for t, _, d, e in got],
                         [(b"^Gohan has transformed", 0, 0x0A), (b"into Super Saiyan 2!", 1, 0)])
        self.assertTrue(all(w <= WIDTH for _, w, _, _ in got), got)

    def test_0b_ends_the_box(self):                       # why the break is 0x0A: Cell's 0x0B gives a new box
        got = lines(self.rom, NEXT_RECORD + ROM_BASE + 4)
        self.assertEqual((got[0][0], got[0][2], got[0][3]), (b"You wretched child!!!", 1, 0x0B))


if __name__ == "__main__":
    unittest.main()
