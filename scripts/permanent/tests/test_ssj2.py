r"""
test_ssj2.py - Tests for the usable Super Saiyan 2 patch (patches.ssj2_form), Task 6.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v
Builds scratch\test-roms\ssj2.gba once (gohan_gi, ssj2_form; log: scratch\test-roms\build-log-test.md) and
the same two patches in memory, so the tests see the ROM before and after ssj2_form and its notes.
Source:  docs\research\re-forms.md sections 1, 2 and 7 (patch sites, original bytes, Rulings 10-16).
read_form reads the form behavior from code, never from the patch module: bonuses from the apply
routine (add #imm or mov #imm before strb to player +0x160..+0x162), ki drain from the tick routine
(the accumulator step loaded before `add r0,r0,rN`, counted only when the tick sends message 0x24).
Cpu runs the gate and the HUD hook as thumb_dis text over a scripted record and flag 195, so the icon
tests check behavior, not code text. It is checked against the vanilla icon pick on the base ROM.
"""
import re
import struct
import unittest
from collections import namedtuple
from pathlib import Path
from unittest import mock

import log2_build
import log_paths
from rom.log2_sprites import set_records
from rom.rom_space import Allocator
from rom.thumb_dis import dis, listing
from rom.webfoot_decompress import ROM_BASE, rom_ptr

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
BASE_ROM = BASE.read_bytes()
ART = log_paths.ART
OUT = log_paths.TEST_ROMS / "ssj2.gba"

APPEARANCE, ENTRY, ENTRIES = 0x1D967C, 20, 22
RAGE_FORM_ID, SSJ_FORM_ID, SSJ2_FORM_ID, BASE_FORM_ID = 4, 5, 22, 2   # appearance entries (re-forms.md 1)
TABLE_LITERALS = (0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050,
                  0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474)       # re-forms.md 7 item 1
REVERSE_LITERAL = 0x42F0
ABILITY_12_ACTION, VANILLA_ACTION = 0x1D99CC, 0x0801353D                             # item 5
HUD_LITERAL, ABILITY_TABLE = 0x8E8C, 0x081D9900                                       # item 6
HUD_SITE, HUD_OLD, HUD_NEW = 0x8D14, "4019007e00014618b168", "281c19f008f8011c07e0"  # item 7
FORM_INIT = 0x080232E4          # stores the five IWRAM form objects' vtables (0x030021E0 + 4 * i)
PLAYER_STATS = 0x161            # apply: `add r0,#0xff ; add r0,#0x61` = player +0x160, then strb [r0,#0..2]
FLAG_BASE = 0x03000E90 + 0xB4   # flag n = byte FLAG_BASE + n / 8, bit n & 7 (@0x08003E42)
SET_TABLE_LITERAL = 0x959C

Form = namedtuple("Form", "entry methods code str_bonus pow_bonus end_bonus flat ki_drain")


# ===== build (once) =====

_CACHE = {}


def built() -> dict:
    """{"gi": ROM after gohan_gi, "rom": after ssj2_form, "notes": alloc.notes} built in memory and to OUT."""
    if _CACHE:
        return _CACHE
    from patches import gohan_gi, ssj2_form
    from tests.test_build import TEST_LOG, build
    rom = bytearray(BASE_ROM) + b"\xFF" * (log2_build.ROM_SIZE - len(BASE_ROM))
    alloc = Allocator(len(rom), log2_build.EXPANSION)
    gohan_gi.apply(rom, alloc)
    gi = bytes(rom)
    ssj2_form.apply(rom, alloc)
    with mock.patch.object(log2_build, "BUILD_LOG", TEST_LOG):
        build(BASE, OUT, ["gohan_gi", "ssj2_form"])
    _CACHE.update(gi=gi, rom=bytes(rom), notes=alloc.notes, file=OUT.read_bytes())
    return _CACHE


def built_rom(names=None) -> bytes:
    return built()["rom"]


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


# ===== readers (from code and data, not from the patch) =====

def table_of(rom: bytes) -> int:
    """File offset of the appearance table the game reads (literal rom:0x1954)."""
    return u32(rom, TABLE_LITERALS[0]) - ROM_BASE


def entry_of(rom: bytes, e: int) -> bytes:
    t = table_of(rom)
    return rom[t + ENTRY * e:t + ENTRY * e + ENTRY]


def vtable_of(rom: bytes, obj: int) -> int:
    """Vtable address of a form object: a ROM word, or an IWRAM object set by FORM_INIT."""
    if obj >= ROM_BASE:
        return u32(rom, obj - ROM_BASE)
    lines = [t for _, t in listing(rom, FORM_INIT, 15)]
    vtables = [int(t.split("=")[1], 16) for t in lines if t.startswith("ldr r0,=")]
    return vtables[(obj - 0x030021E0) // 4]


def routine(rom: bytes, addr: int, limit: int = 120) -> list:
    """Instruction texts from addr through the last exit (bx, pop {..pc} or b) past every branch target."""
    out, far = [], addr
    for a, text in listing(rom, addr, limit):
        out.append(text)
        m = re.match(r"b[a-z]{0,2} (0x[0-9a-f]+)$", text)
        if m and not text.startswith("bl "):
            far = max(far, int(m[1], 16))
        if text.startswith(("bx ", "b ")) or text.startswith("pop") and "pc" in text:
            if a >= far:
                break
    return out


def read_form(rom: bytes, e: int) -> Form:
    entry = entry_of(rom, e)
    vt = vtable_of(rom, u32(entry, 0x10))
    methods = tuple(((vt + struct.unpack_from("<i", rom, vt - ROM_BASE + 4 * i)[0]) & 0xFFFFFFFF) & ~1
                    for i in range(4))
    apply_code, tick_code = routine(rom, methods[0]), routine(rom, methods[1])
    last, stats, flat = {}, [0, 0, 0], False
    for text in apply_code:
        m = re.match(r"(add|mov|lsr) (r\d),(#0x[0-9a-f]+|r\d,#\d+)$", text)
        if m:
            last[m[2]] = (m[1], int(m[3][1:], 16) if m[3].startswith("#") else 0)
        m = re.match(r"strb (r\d),\[r0,#0x([0-2])\]$", text)
        if m and m[1] in last:
            op, imm = last[m[1]]
            stats[int(m[2])] = imm if op in ("add", "mov") else 0
            flat |= op == "mov"
    drain = 0
    if "mov r1,#0x24" in tick_code:
        for a, b in zip(tick_code, tick_code[1:]):
            m = re.match(r"ldr (r\d),=(0x[0-9a-f]+)$", a)
            if m and b == f"add r0,r0,{m[1]}":
                drain = int(m[2], 16)
    return Form(entry, methods, (tuple(apply_code), tuple(tick_code)), *stats, flat, drain)


def gate_parts(rom: bytes) -> dict:
    """The step gate's exits, and the table, flag address, flag bit and EP threshold of the predicate it calls."""
    gate = u32(rom, ABILITY_12_ACTION) & ~1
    code = routine(rom, gate, 40)
    pred = int(next(t for t in code if t.startswith("bl "))[3:], 16)
    pred_code = routine(rom, pred, 40)
    lits = [int(t.split("=")[1], 16) for t in pred_code if "=" in t]
    shift = next(int(t.split("#")[1]) for t in pred_code if re.match(r"lsl r\d,r\d,#(2[4-9]|3[01])$", t)
                 and not t.endswith("#31"))
    ep = next(int(t.split("#")[1], 16) for t in pred_code if re.match(r"cmp r\d,#0x", t))
    vanilla = [int(t.split("=")[1], 16) for t in code if "=" in t]
    return {"addr": gate, "code": code, "pred": pred, "pred_code": pred_code, "table": lits[0] - ROM_BASE,
            "flag_addr": lits[1], "bit": 31 - shift, "ep": ep, "vanilla": vanilla[0]}


def transform_step_condition(rom: bytes, from_form: int) -> tuple:
    """("flag", n) when B in this form steps only with story flag n, else ("vanilla", None)."""
    g = gate_parts(rom)
    e = rom[g["table"] + ENTRY * from_form:g["table"] + ENTRY * from_form + ENTRY]
    if not (e[0] & 1 and e[4] != e[5]):
        return ("vanilla", None)
    return ("flag", (g["flag_addr"] - FLAG_BASE) * 8 + g["bit"])


# ===== expected disassembly (branch targets as +offset from the routine, named literals) =====

EXPECTED = {
    "apply": """push {r4,lr}|add r4,r1,#0|ldr r0,=0x086f7e50|ldr r0,[r0,#0x4]|ldrb r1,[r0,#0x0]|lsl r3,r1,#3
        |sub r1,r3,r1|lsl r1,r1,#2|add r1,r1,r0|add r1,#0xc|ldrh r0,[r1,#0xa]|lsr r2,r0,#8|add r0,r4,#0
        |add r0,#0xff|add r0,#0x61|add r2,#0x14|strb r2,[r0,#0x0]|ldrh r2,[r1,#0xc]|lsr r2,r2,#8|add r2,#0x14
        |strb r2,[r0,#0x1]|ldrh r1,[r1,#0xe]|lsr r1,r1,#8|add r1,#0x14|strb r1,[r0,#0x2]|mov r1,#0x80
        |strb r1,[r0,#0x3]|strb r1,[r0,#0x4]|ldr r1,=0x3fe00000|add r0,#0x28|ldr r2,=0x080265c5|bl STUB_R2
        |add r0,r4,#0|add r0,#0xff|add r0,#0x8d|ldr r1,=0x40400000|ldr r2,=0x080265c5|bl STUB_R2|mov r0,#0x0
        |add r4,#0xff|add r4,#0x81|str r0,[r4,#0x4]|pop {r4,pc}""",
    "tick": """push {r3,r4,r5,lr}|add r5,r1,#0|add r0,r1,#0|ldr r1,[r1,#0x0]|ldr r2,[r1,#0x2c]|add r2,r2,r1
        |mov r1,#0x24|bl STUB_R2|cmp r0,#0x0|bne +0x6e|add r4,r5,#0|add r4,#0xff|add r4,#0x81|ldr r0,[r4,#0x4]
        |ldr r1,=0x0000199a|add r0,r0,r1|str r0,[r4,#0x4]|lsr r0,r0,#16|beq +0x6e|ldr r0,=0x086f7e50
        |ldr r0,[r0,#0x4]|ldrb r1,[r0,#0x0]|lsl r3,r1,#3|sub r1,r3,r1|lsl r1,r1,#2|add r0,r1,r0|add r0,#0xc
        |mov r3,#0x4|ldsh r2,[r0,r3]|add r1,r0,#4|cmp r2,#0x1|bge +0x48|mov r2,#0x0|strh r2,[r1,#0x0]|b +0x4c
        |sub r2,#0x1|strh r2,[r1,#0x0]|ldrh r1,[r0,#0x4]|cmp r1,#0x0|bne +0x66|ldrh r0,[r0,#0x0]|cmp r0,#0x0
        |beq +0x66|ldr r1,[r5,#0x0]|add r0,r5,#0|ldr r2,[r1,#0x28]|add r2,r2,r1|mov r1,#0x24|bl STUB_R2
        |ldr r0,[r4,#0x4]|lsl r0,r0,#16|lsr r0,r0,#16|str r0,[r4,#0x4]|pop {r3,r4,r5,pc}""",
    "step_ok": """ldrb r2,[r0,#0x8]|lsl r3,r2,#2|add r2,r3,r2|lsl r2,r2,#2|ldr r3,=TABLE|add r2,r2,r3
        |ldrb r3,[r2,#0x0]|lsl r3,r3,#31|beq +0x2e|ldrb r3,[r2,#0x4]|ldrb r2,[r2,#0x5]|cmp r2,r3|beq +0x2e
        |ldr r2,=0x03000f5c|ldrb r2,[r2,#0x0]|lsl r2,r2,#28|bpl +0x2e|mov r3,#0x4|ldsh r2,[r0,r3]|cmp r2,#0xa
        |blt +0x2e|mov r2,#0x1|bx lr|mov r2,#0x0|bx lr""",
    "gate": """push {lr}|bl STEP_OK|pop {r3}|mov lr,r3|cmp r2,#0x0|beq +0x1a|ldr r2,[r1,#0x0]|ldr r3,[r2,#0x28]
        |add r3,r3,r2|add r0,r1,#0|mov r1,#0x23|bx r3|ldr r2,=0x0801353d|bx r2""",
    "hud": """push {r4,r5,r6,lr}|add r4,r0,#0|ldrb r0,[r4,#0x9]|add r0,r0,r4|ldrb r5,[r0,#0x18]|lsl r0,r5,#4
        |ldr r1,=0x081d9900|add r6,r0,r1|ldr r1,[r6,#0x8]|add r0,r4,#0|bl STUB_R1|cmp r5,#0xc|bne +0x3a
        |ldrb r1,[r4,#0x8]|cmp r1,#0x16|beq +0x30|add r5,r0,#0|add r0,r4,#0|bl STEP_OK|add r0,r5,#0|cmp r2,#0x0
        |beq +0x3a|ldr r1,=Z2|cmp r0,#0x0|bne +0x42|ldr r1,=Z2_DIM|b +0x42|ldr r1,[r6,#0x0]|cmp r0,#0x0
        |bne +0x42|ldr r1,[r6,#0x4]|add r0,r1,#0|pop {r4,r5,r6,pc}""",
    "stub_r1": "bx r1",
    "stub_r2": "bx r2",
}


def normalized(rom: bytes, notes: dict, name: str, count: int) -> list:
    """Disassemble a new routine; local targets become +offset, known addresses become names."""
    start = notes[name] + ROM_BASE
    names = {notes["table"] + ROM_BASE: "TABLE", notes["z2"] + ROM_BASE: "Z2", notes["z2_dim"] + ROM_BASE: "Z2_DIM",
             notes["stub_r1"] + ROM_BASE: "STUB_R1", notes["stub_r2"] + ROM_BASE: "STUB_R2",
             notes["step_ok"] + ROM_BASE: "STEP_OK"}
    end = start + 2 * count + 4

    def sub(m):
        v = int(m[0], 16)
        if v in names:
            return names[v]
        return f"+{v - start:#x}" if start <= v < end and m.string.startswith("b") else m[0]
    return [re.sub(r"0x[0-9a-f]+", sub, t) for _, t in listing(rom, start, count)]


# ===== Thumb interpreter: runs thumb_dis text (never the encoder) over ROM, EWRAM and IWRAM =====

M32 = 0xFFFFFFFF
REGNO = {**{f"r{i}": i for i in range(13)}, "sp": 13, "lr": 14, "pc": 15}
RET, MSG = 0x0EEE0000, 0x0EEE1000             # sentinel addresses no code lives at
RECORD, PLAYER, PLAYER_VT, STACK = 0x02000100, 0x02000200, 0x02000300, 0x03007F00
FLAG_195_BYTE = FLAG_BASE + 195 // 8           # 0x03000F5C, bit 3


class Cpu:
    def __init__(self, rom: bytes):
        self.rom, self.r = rom, [0] * 16
        self.ram = {0x02: bytearray(0x40000), 0x03: bytearray(0x8000)}
        self.n = self.z = self.c = self.v = False

    def _at(self, a: int, size: int) -> tuple:
        if a >> 24 == 0x08:
            return self.rom, a - ROM_BASE
        buf, off = self.ram[a >> 24], a & 0xFFFFFF
        if off + size > len(buf):
            raise AssertionError(f"access past RAM end at {a:#x}")
        return buf, off

    def load(self, a: int, size: int, signed: bool = False) -> int:
        buf, off = self._at(a, size)
        return int.from_bytes(buf[off:off + size], "little", signed=signed) & M32

    def store(self, a: int, size: int, v: int) -> None:
        buf, off = self._at(a, size)
        if buf is self.rom:
            raise AssertionError(f"store to ROM at {a:#x}")
        buf[off:off + size] = (v & ((1 << 8 * size) - 1)).to_bytes(size, "little")

    def _nz(self, v: int) -> int:
        v &= M32
        self.n, self.z = bool(v >> 31), v == 0
        return v

    def _addsub(self, a: int, b: int, sub: bool) -> int:
        res = (a - b if sub else a + b) & M32
        self.c = a >= b if sub else a + b > M32
        self.v = bool((((a ^ b) if sub else ~(a ^ b)) & (a ^ res)) >> 31 & 1)
        return self._nz(res)

    def _cond(self, cc: str) -> bool:
        n, z, v = self.n, self.z, self.v
        return {"eq": z, "ne": not z, "mi": n, "pl": not n, "cs": self.c, "cc": not self.c, "ge": n == v,
                "lt": n != v, "gt": not z and n == v, "le": z or n != v}[cc]

    def run(self, addr: int, stops: dict, limit: int = 400) -> str:
        """Run from addr until pc reaches a stop. A stop is a name (returned) or a function (a stubbed
        call: its value goes to r0, then execution returns to lr)."""
        pc = addr & ~1
        for _ in range(limit):
            if pc in stops:
                if not callable(stops[pc]):
                    return stops[pc]
                self.r[0] = stops[pc](self) & M32
                pc = self.r[14] & ~1
                continue
            text, size = dis(self.rom, pc)
            pc = self._step(pc + size, text)
        raise AssertionError("no exit within the step limit")

    def _step(self, nxt: int, text: str) -> int:
        r = self.r
        op, _, rest = text.partition(" ")
        a = re.split(r",(?![^\[]*\])", rest)
        val = lambda s: int(s[1:], 0) if s.startswith("#") else r[REGNO[s]]   # noqa: E731
        if op in ("push", "pop"):
            regs = sorted(REGNO[x] for x in rest.strip("{}").split(","))
            if op == "push":
                r[13] -= 4 * len(regs)
            for i, n in enumerate(regs):
                if op == "push":
                    self.store(r[13] + 4 * i, 4, r[n])
                elif n == 15:
                    nxt = self.load(r[13] + 4 * i, 4) & ~1
                else:
                    r[n] = self.load(r[13] + 4 * i, 4)
            if op == "pop":
                r[13] += 4 * len(regs)
            return nxt
        if op == "bl":
            r[14] = nxt | 1
            return int(a[0], 16)
        if op == "bx":
            if not r[REGNO[a[0]]] & 1:
                raise AssertionError(f"bx {a[0]} to ARM state")
            return r[REGNO[a[0]]] & ~1
        if op == "b":
            return int(a[0], 16)
        if op[0] == "b" and len(op) == 3:
            return int(a[0], 16) if self._cond(op[1:]) else nxt
        d = REGNO[a[0]]
        if op == "ldr" and a[1].startswith("="):
            r[d] = int(a[1][1:], 16)
        elif op in ("ldr", "ldrh", "ldrb", "ldsh", "str", "strh", "strb"):
            base, off = a[1].strip("[]").split(",")
            addr = (r[REGNO[base]] + val(off)) & M32
            size = {"ldr": 4, "str": 4, "ldrh": 2, "strh": 2, "ldsh": 2}.get(op, 1)
            if op.startswith("st"):
                self.store(addr, size, r[d])
            else:
                r[d] = self.load(addr, size, signed=op == "ldsh")
        elif op in ("add", "sub"):
            x, y = (r[d], val(a[1])) if len(a) == 2 else (val(a[1]), val(a[2]))
            r[d] = self._addsub(x, y, op == "sub")
        elif op == "cmp":
            self._addsub(r[d], val(a[1]), True)
        elif op == "mov" and a[1].startswith("#"):
            r[d] = self._nz(val(a[1]))
        elif op == "mov":
            r[d] = r[REGNO[a[1]]]                          # hi-register mov: flags unchanged
        elif op in ("lsl", "lsr"):
            x, k = r[REGNO[a[1]]], val(a[2])
            if k:
                self.c = bool(x >> (32 - k) & 1) if op == "lsl" else bool(x >> (k - 1) & 1)
            r[d] = self._nz(x << k if op == "lsl" else x >> k)
        else:
            raise AssertionError(f"interpreter cannot run: {text}")
        return nxt


def cpu_state(rom: bytes, entry: int, flag: bool, ep: int, ability: int = 12) -> Cpu:
    """Leader record in EWRAM (slot 2 selected), flag 195 byte, player with a message vtable, a fresh stack."""
    cpu = Cpu(rom)
    rec = bytearray(28)
    rec[4:6] = ep.to_bytes(2, "little", signed=True)
    rec[8], rec[9], rec[0x18:0x1C] = entry, 2, bytes([4, 3, ability, 2])
    cpu.ram[0x02][RECORD & 0xFFFFFF:(RECORD & 0xFFFFFF) + 28] = rec
    cpu.store(FLAG_195_BYTE, 1, 0xFF if flag else 0xF7)      # only bit 3 may matter
    cpu.store(PLAYER, 4, PLAYER_VT)
    cpu.store(PLAYER_VT + 0x28, 4, (MSG | 1) - PLAYER_VT)     # vtable words are offsets from the base
    cpu.r[13], cpu.r[14] = STACK, RET | 1
    cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
    return cpu


def run_gate(rom: bytes, entry: int, flag: bool, ep: int) -> tuple:
    """("message" or "vanilla", cpu at the exit) for B with ability 12."""
    cpu = cpu_state(rom, entry, flag, ep)
    cpu.r[0], cpu.r[1] = RECORD, PLAYER
    return cpu.run(u32(rom, ABILITY_12_ACTION), {MSG: "message", VANILLA_ACTION & ~1: "vanilla"}), cpu


def run_hud(rom: bytes, entry: int, flag: bool, ep: int, ability: int = 12, test: int = 1) -> tuple:
    """(icon pointer, cpu after return) from the HUD hook; every ability test returns `test`."""
    cpu = cpu_state(rom, entry, flag, ep, ability)
    stops = {u32(rom, ABILITY_TABLE - ROM_BASE + 16 * i + 8) & ~1: lambda _c: test for i in range(14)}
    stops[RET] = "ret"
    cpu.r[0] = RECORD
    if cpu.run(u32(rom, HUD_LITERAL), stops) != "ret":
        raise AssertionError("hud did not return")
    return cpu.r[0], cpu


def vanilla_icon(rom: bytes, ability: int, test: int) -> int:
    return u32(rom, ABILITY_TABLE - ROM_BASE + 16 * ability + (0 if test else 4))


# ===== tests =====

class Ssj2FormTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.gi, cls.rom, cls.notes = b["gi"], b["rom"], b["notes"]["ssj2_form"]
        cls.gi_notes = b["notes"]["gohan_gi"]

    # brief Step 1 tests

    def test_ssj2_form_values(self):
        f = read_form(self.rom, SSJ2_FORM_ID)
        self.assertEqual((f.str_bonus, f.pow_bonus, f.end_bonus, f.flat), (20, 20, 20, False))
        self.assertEqual(read_form(self.rom, SSJ_FORM_ID).ki_drain, 0xCCD)
        self.assertEqual(f.ki_drain, 2 * read_form(self.rom, SSJ_FORM_ID).ki_drain)

    def test_ssj2_gate_reads_flag_195(self):                # Review Focus 3
        self.assertEqual(transform_step_condition(self.rom, from_form=SSJ_FORM_ID), ("flag", 195))
        self.assertEqual(transform_step_condition(self.rom, from_form=BASE_FORM_ID), ("vanilla", None))
        self.assertEqual(transform_step_condition(self.rom, from_form=SSJ2_FORM_ID), ("vanilla", None))
        g = gate_parts(self.rom)
        self.assertEqual((g["flag_addr"], g["bit"]), (0x03000F5C, 3))
        self.assertEqual(g["vanilla"], VANILLA_ACTION)

    def test_rage_unchanged(self):                           # only the sprite set (+1) moves to gi Rage 160
        self.assertEqual(read_form(self.rom, RAGE_FORM_ID)._replace(entry=None),
                         read_form(BASE_ROM, RAGE_FORM_ID)._replace(entry=None))
        want = bytearray(BASE_ROM[APPEARANCE + 80:APPEARANCE + 100])
        want[1] = 160
        self.assertEqual(entry_of(self.rom, RAGE_FORM_ID), bytes(want))
        rage = read_form(self.rom, RAGE_FORM_ID)
        self.assertEqual((rage.str_bonus, rage.flat, rage.ki_drain), (100, True, 0))

    # Rulings 10, 11, 15 and 16

    def test_end_ceiling_every_playable_form(self):         # Ruling 15: damage uses 0x80 - END
        for e in range(ENTRIES + 1):
            f = read_form(self.rom, e)
            top = max(f.str_bonus, f.pow_bonus, f.end_bonus) if f.flat else 100 + f.end_bonus
            self.assertLessEqual(top, 127, f"entry {e}")

    def test_gate_reads_relocated_table_and_ep(self):       # Rulings 11 and 15
        g = gate_parts(self.rom)
        self.assertEqual(g["table"], table_of(self.rom))
        self.assertNotEqual(g["table"], APPEARANCE)
        self.assertEqual(g["ep"], 10)
        self.assertGreaterEqual(g["ep"], 9)

    def test_gate_keeps_lr(self):                            # Ruling 15: both exits tail-jump with entry lr, sp
        self.assertEqual([t for t in gate_parts(self.rom)["code"] if t.startswith("bx")], ["bx r3", "bx r2"])
        for args, want in (((SSJ_FORM_ID, True, 10), "message"), ((SSJ_FORM_ID, False, 10), "vanilla")):
            exit_, cpu = run_gate(self.rom, *args)
            self.assertEqual(exit_, want)
            self.assertEqual((cpu.r[13], cpu.r[14]), (STACK, RET | 1), want)
            self.assertEqual((cpu.r[0], cpu.r[1]), (PLAYER, 0x23) if want == "message" else (RECORD, PLAYER))
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777])

    def test_gate_does_not_test_map_word(self):              # Ruling 16
        g = gate_parts(self.rom)
        self.assertFalse([t for t in g["code"] + g["pred_code"] if "0x086db27c" in t or "0x03002080" in t])

    # HUD icon shows what B does next (final, 2026-10-17)

    def test_gate_and_hud_share_one_predicate(self):
        g = gate_parts(self.rom)
        hud_calls = [t for t in routine(self.rom, self.notes["hud"] + ROM_BASE, 60) if t.startswith("bl ")]
        self.assertEqual(g["pred"], self.notes["step_ok"] + ROM_BASE)
        self.assertIn(f"bl {g['pred']:#x}", hud_calls)

    def test_gate_steps_only_with_flag_and_ep(self):
        cases = {(SSJ_FORM_ID, True, 10): "message", (SSJ_FORM_ID, True, 0x7FFF): "message",
                 (SSJ_FORM_ID, True, 9): "vanilla", (SSJ_FORM_ID, True, -1): "vanilla",
                 (SSJ_FORM_ID, False, 100): "vanilla", (SSJ2_FORM_ID, True, 100): "vanilla",
                 (BASE_FORM_ID, True, 100): "vanilla", (RAGE_FORM_ID, True, 100): "vanilla"}
        for args, want in cases.items():
            self.assertEqual(run_gate(self.rom, *args)[0], want, args)

    def test_hud_z2_in_ssj_when_b_steps_up(self):
        for ep in (10, 11, 100):
            for test, key in ((1, "z2"), (0, "z2_dim")):
                icon, _ = run_hud(self.rom, SSJ_FORM_ID, True, ep, test=test)
                self.assertEqual(icon, self.notes[key] + ROM_BASE, (ep, test))

    def test_hud_z_in_ssj_when_flag_clear(self):
        for test in (1, 0):
            self.assertEqual(run_hud(self.rom, SSJ_FORM_ID, False, 100, test=test)[0],
                             vanilla_icon(self.rom, 12, test))

    def test_hud_z_in_ssj_when_ep_under_step_cost(self):
        for ep in (9, 0, -1):
            for test in (1, 0):
                self.assertEqual(run_hud(self.rom, SSJ_FORM_ID, True, ep, test=test)[0],
                                 vanilla_icon(self.rom, 12, test), (ep, test))

    def test_hud_z2_in_ssj2(self):                           # entry 22 needs neither the flag nor EP
        for flag, ep in ((True, 100), (False, 0)):
            for test, key in ((1, "z2"), (0, "z2_dim")):
                self.assertEqual(run_hud(self.rom, SSJ2_FORM_ID, flag, ep, test=test)[0],
                                 self.notes[key] + ROM_BASE, (flag, ep, test))

    def test_hud_vanilla_for_other_forms_and_abilities(self):
        for e in range(ENTRIES + 1):                         # other characters' forms, base, Rage
            if e not in (SSJ_FORM_ID, SSJ2_FORM_ID):
                for test in (1, 0):
                    self.assertEqual(run_hud(self.rom, e, True, 100, test=test)[0],
                                     vanilla_icon(self.rom, 12, test), (e, test))
        for ability in (a for a in range(14) if a != 12):
            for e in (SSJ_FORM_ID, SSJ2_FORM_ID, BASE_FORM_ID):
                for test in (1, 0):
                    self.assertEqual(run_hud(self.rom, e, True, 100, ability, test)[0],
                                     vanilla_icon(self.rom, ability, test), (ability, e, test))

    def test_hud_matches_vanilla_pick_on_the_base_rom(self):   # the interpreter against the original code
        for e in (BASE_FORM_ID, SSJ_FORM_ID):
            for ability, test in ((12, 1), (12, 0), (4, 1)):
                cpu = cpu_state(BASE_ROM, e, True, 100, ability)
                stops = {u32(BASE_ROM, ABILITY_TABLE - ROM_BASE + 16 * i + 8) & ~1: lambda _c: test
                         for i in range(14)}
                stops[0x08008D2E] = "picked"
                cpu.r[5] = RECORD
                self.assertEqual(cpu.run(0x08008D10, stops), "picked")
                self.assertEqual(cpu.r[1], vanilla_icon(BASE_ROM, ability, test))

    def test_hud_keeps_r4_to_r7_and_sp(self):
        for e, flag in ((SSJ_FORM_ID, True), (SSJ_FORM_ID, False), (SSJ2_FORM_ID, False), (BASE_FORM_ID, True)):
            _, cpu = run_hud(self.rom, e, flag, 100)
            self.assertEqual(cpu.r[4:8], [0x44444444, 0x55555555, 0x66666666, 0x77777777], e)
            self.assertEqual(cpu.r[13], STACK, e)

    def test_hud_icon_never_disagrees_with_b(self):         # Z2 exactly when B steps up or reverts from 22
        for e in range(ENTRIES + 1):
            for flag in (True, False):
                for ep in (-1, 0, 9, 10, 100):
                    steps = run_gate(self.rom, e, flag, ep)[0] == "message"
                    icon, _ = run_hud(self.rom, e, flag, ep)
                    self.assertEqual(icon == self.notes["z2"] + ROM_BASE, steps or e == SSJ2_FORM_ID,
                                     (e, flag, ep))

    def test_only_entry_5_steps(self):                       # the shared ability 12 action passes for others
        rom, t = self.rom, table_of(self.rom)
        steps = [e for e in range(ENTRIES + 1) if rom[t + ENTRY * e] & 1 and rom[t + ENTRY * e + 4] != rom[t + ENTRY * e + 5]]
        self.assertEqual(steps, [SSJ_FORM_ID])

    def test_entry5_plus4_is_22_and_entry22_reverts_to_2(self):
        e5, e22 = entry_of(self.rom, SSJ_FORM_ID), entry_of(self.rom, SSJ2_FORM_ID)
        self.assertEqual((e5[4], e5[5]), (22, 2))
        self.assertEqual((e22[0], e22[1], e22[4], e22[5]), (1, 159, 2, 2))
        self.assertEqual(e22[2:4], bytes([0x3D, 0x0C]))         # Ruling 13: Rage portraits until Task 7
        self.assertEqual(e22[6:16], e5[6:16])

    def test_entry22_set_is_gi_ssj2_with_anims_9_and_21(self):
        table = u32(self.rom, SET_TABLE_LITERAL) - ROM_BASE
        off = rom_ptr(self.rom, table + 4 * (159 - 7))
        self.assertEqual(off, self.gi_notes["set_159"])
        anims = {r["anim"] for r in set_records(self.rom, off)}
        self.assertTrue({9, 21} <= anims)
        self.assertEqual(struct.unpack_from("<H", self.rom, off)[0], 0x400)   # same slot as 157 and 158

    def test_relocated_table_copies_live_table(self):        # Ruling 14
        t, live = table_of(self.rom), self.gi[APPEARANCE:APPEARANCE + ENTRY * ENTRIES]
        new = bytearray(self.rom[t:t + ENTRY * ENTRIES])
        self.assertEqual(new[ENTRY * SSJ_FORM_ID + 4], 22)
        new[ENTRY * SSJ_FORM_ID + 4] = 4
        self.assertEqual(bytes(new), live)
        self.assertEqual((live[ENTRY * 2 + 1], live[ENTRY * 5 + 1]), (157, 158))
        self.assertEqual(self.rom[APPEARANCE:APPEARANCE + ENTRY * ENTRIES], live)   # old table kept as is

    def test_reverse_lookup_still_finds_rage(self):          # Cell fight still forces Rage (ext 73 (0, 160))
        copy = u32(self.rom, REVERSE_LITERAL) - ROM_BASE
        self.assertEqual(copy, self.gi_notes["appearance_copy"])
        self.assertEqual(next(e for e in range(ENTRIES) if self.rom[copy + ENTRY * e + 1] == 160), RAGE_FORM_ID)

    def test_ssj2_form_object_and_vtable(self):
        obj = u32(entry_of(self.rom, SSJ2_FORM_ID), 0x10)
        self.assertEqual(obj, self.notes["form_object"] + ROM_BASE)
        f, ssj = read_form(self.rom, SSJ2_FORM_ID), read_form(self.rom, SSJ_FORM_ID)
        self.assertEqual(f.methods[:2], (self.notes["apply"] + ROM_BASE, self.notes["tick"] + ROM_BASE))
        self.assertEqual(f.methods[2:], ssj.methods[2:])        # enter and leave: the Super Saiyan sound
        vt = vtable_of(self.rom, obj) - ROM_BASE
        words = struct.unpack_from("<6I", self.rom, vt)
        self.assertEqual([(vt + ROM_BASE + w) & 0xFFFFFFFF for w in words],
                         [self.notes["apply"] + ROM_BASE + 1, self.notes["tick"] + ROM_BASE + 1,
                          0x08017377, 0x08017393, 0x080271E1, 0x08026391])

    def test_ssj_tick_pool_untouched(self):                  # never patch the shared pool 0x080174A0
        self.assertEqual(self.rom[0x17000:0x17500], BASE_ROM[0x17000:0x17500])
        self.assertEqual(read_form(self.rom, SSJ_FORM_ID), read_form(BASE_ROM, SSJ_FORM_ID)._replace(
            entry=entry_of(self.rom, SSJ_FORM_ID)))

    # repointed literals and patch sites (fail closed)

    def test_literals_repointed_from_old_values(self):
        new_table = table_of(self.rom) + ROM_BASE
        for off in TABLE_LITERALS:
            self.assertEqual(u32(self.gi, off), APPEARANCE + ROM_BASE, f"rom:0x{off:X} before")
            self.assertEqual(u32(self.rom, off), new_table, f"rom:0x{off:X} after")
        self.assertEqual(len(set(TABLE_LITERALS)), 17)
        self.assertEqual((u32(self.gi, ABILITY_12_ACTION), u32(self.rom, ABILITY_12_ACTION)),
                         (VANILLA_ACTION, self.notes["gate"] + ROM_BASE + 1))
        self.assertEqual((u32(self.gi, HUD_LITERAL), u32(self.rom, HUD_LITERAL)),
                         (ABILITY_TABLE, self.notes["hud"] + ROM_BASE + 1))
        self.assertEqual(self.gi[HUD_SITE:HUD_SITE + 10].hex(), HUD_OLD)
        self.assertEqual(self.rom[HUD_SITE:HUD_SITE + 10].hex(), HUD_NEW)
        self.assertEqual(u32(self.rom, REVERSE_LITERAL), u32(self.gi, REVERSE_LITERAL))

    def test_apply_fails_closed(self):
        from patches import ssj2_form
        set_159_word = u32(self.gi, SET_TABLE_LITERAL) - ROM_BASE + 4 * (159 - 7)
        for off, junk in ((TABLE_LITERALS[5], b"\0\0\0\0"), (ABILITY_12_ACTION, b"\1\0\0\0"),
                          (HUD_LITERAL, b"\0\0\0\0"), (HUD_SITE + 4, b"\xFF"), (set_159_word, b"\0\0\0\0")):
            rom = bytearray(self.gi)
            rom[off:off + len(junk)] = junk
            before = bytes(rom)
            alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
            alloc.notes["gohan_gi"] = dict(self.gi_notes)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                ssj2_form.apply(rom, alloc)
            self.assertEqual(bytes(rom), before)
        with self.assertRaisesRegex(ValueError, "run gohan_gi first"):
            ssj2_form.apply(bytearray(self.gi), Allocator(len(self.gi), [(0xF00000, 0x100000)]))

    def test_wrong_order_names_the_patch_to_run_first(self):    # review Minor 7
        from patches import ssj2_form
        rom = bytearray(self.gi)
        with self.assertRaisesRegex(ValueError, "run gohan_gi first"):
            ssj2_form.apply(rom, Allocator(len(rom), [(0xF00000, 0x100000)]))
        self.assertEqual(bytes(rom), self.gi)

    def test_assembler_range_checks(self):                  # review Minor 2: each limit raises
        from patches.ssj2_form import _encode
        pc = 0x08900000
        with self.assertRaises(ValueError):                 # pool word 256
            _encode(pc, "ldr", ["r0", "=0x5"], {}, {}, [5], pc + 4 + 4 * 256)
        with self.assertRaises(ValueError):                 # pool behind the load
            _encode(pc, "ldr", ["r0", "=0x5"], {}, {}, [5], pc - 4)
        self.assertEqual(len(_encode(pc, "ldr", ["r0", "=0x5"], {}, {}, [5], pc + 4 + 4 * 255)), 2)
        for halfwords, ok in ((1023, True), (1024, False), (-1024, True), (-1025, False)):
            labels = {"x": pc + 4 + 2 * halfwords}
            if ok:
                self.assertEqual(len(_encode(pc, "b", ["x"], labels, {}, [], 0)), 2)
            else:
                self.assertRaises(ValueError, _encode, pc, "b", ["x"], labels, {}, [], 0)
        for off, ok in ((0x3FFFFE, True), (0x400000, False), (-0x400000, True), (-0x400002, False)):
            labels = {"x": pc + 4 + off}
            if ok:
                self.assertEqual(len(_encode(pc, "bl", ["x"], labels, {}, [], 0)), 4)
            else:
                self.assertRaises(ValueError, _encode, pc, "bl", ["x"], labels, {}, [], 0)

    def test_code_size_mismatch_raises(self):               # review Minor 1: no shifted ROM bytes
        from patches import ssj2_form
        rom = bytearray(self.gi)
        alloc = Allocator(len(rom), [(0xF00000, 0x100000)])
        alloc.notes["gohan_gi"] = dict(self.gi_notes)
        real = ssj2_form.assemble
        with mock.patch.object(ssj2_form, "assemble",
                               side_effect=lambda src, base, syms: (real(src, base, syms)[0] + b"\0\0",
                                                                    real(src, base, syms)[1]) if base != ROM_BASE
                               else real(src, base, syms)):
            with self.assertRaises(ValueError):
                ssj2_form.apply(rom, alloc)
        self.assertEqual(bytes(rom), self.gi)

    def test_base_8mb_differs_only_at_patch_sites(self):
        sites = {off: 4 for off in TABLE_LITERALS} | {ABILITY_12_ACTION: 4, HUD_LITERAL: 4, HUD_SITE: 10}
        inside = {o for off, n in sites.items() for o in range(off, off + n)}
        diff = [i for i in range(log2_build.BASE_SIZE) if self.gi[i] != self.rom[i]]
        self.assertTrue(diff)
        self.assertFalse([hex(i) for i in diff if i not in inside])

    def test_new_data_in_expansion(self):
        for key in ("table", "form_object", "vtable", "code", "z2", "z2_dim"):
            self.assertGreaterEqual(self.notes[key], 0x800000, key)

    def test_file_build_matches_memory_build(self):
        self.assertEqual(built()["file"], self.rom)

    # new code

    def test_new_routines_disassemble_as_expected(self):
        for name, text in EXPECTED.items():
            want = [t.strip() for t in text.split("|")]
            self.assertEqual(normalized(self.rom, self.notes, name, len(want)), want, name)

    def test_hud_site_disassembles_as_expected(self):
        self.assertEqual([t for _, t in listing(self.rom, 0x08008D10, 6)],
                         ["ldrb r0,[r5,#0x9]", f"ldr r1,={self.notes['hud'] + ROM_BASE + 1:#010x}",
                          "add r0,r5,#0", "bl 0x8021d2a", "add r1,r0,#0", "b 0x8008d2e"])

    def test_z2_icons_in_rom(self):                          # approved art, unchanged (Rulings 12, 17)
        for key, name in (("z2", "hud_z2_usable.bin"), ("z2_dim", "hud_z2_dim.bin")):
            off = self.notes[key]
            self.assertEqual(off % 4, 0, key)                # the HUD copies it with 32-bit DMA (@0x08008DA4)
            self.assertEqual(self.rom[off:off + 0x200], (ART / name).read_bytes(), key)


if __name__ == "__main__":
    unittest.main()
