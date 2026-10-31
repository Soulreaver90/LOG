r"""
codemap.py - Whole-ROM code map: every function found, Thumb or ARM, callers, and code vs data coverage.

Usage:   (from scripts\permanent) py -3 -I disasm\codemap.py [--game usa|eu|bf] [--rom PATH] [--out DIR] [--no-symbols]
Output:  <out>\functions.csv (address, size, extent, mode, name, callers = BL sites, caller_funcs, ptr_refs =
         aligned ROM words holding start+1, vt_refs, found_by, flags, bible), <out>\coverage.txt and
         <out>\codemap.json (listing.py and the Ghidra seeding read it). Default out: scripts\permanent\disasm\data\ for usa,
         scripts\permanent\disasm\data\<game>\ for the others. size = contiguous bytes from the start (code, its pools, switch
         tables); extent = last instruction end (a shared tail far away makes it larger).
         scripts\permanent\disasm\data\ is a committed snapshot of the USA run; tests\test_re_tools.py rebuilds the map and fails
         when codemap.json differs, so re-run this after a change to codemap.py or symbols.py.
API:     Image(data), explore(img, start, mode, starts) -> Body; build(img, syms) -> Map; arm_text(img, a),
         thumb_text(img, a), thumb_flow / arm_flow(img, a) -> (size, kind, target).
Method:  Stages, each run to a fixed point before the next (confident seeds first, guesses last):
         1. Hard seeds: the header branch (ARM crt0), main from the crt0 words at rom:0x140, the IRQ handler
            stored to 0x03007FFC; recursive descent per function: b and bcc stay inside, BL targets become
            functions, bx / call_via / ldr pc targets come from tracked `ldr rX,=` values, `add pc` byte
            switch tables are read; odd literal-pool values, self-relative lists (`ldr ; add rX,pc`: the
            static constructor vector), symbols.py functions and pointer tables.
         2. Base-relative vtables: an even literal into the code range whose words give base + word = Thumb
            code; each new entry must decode clean and look like a start (push within 8 instructions, a
            leaf or a tail stub).
         3. ROM words: aligned odd words anywhere in the ROM into the code range, same checks.
         4. Prologue search in the bytes still unclassified (as Ghidra's function start search).
Rules:   Reads ROMs only, never writes under data\. A path that hits an invalid ARMv4T encoding marks the
         function "bad"; a pointer candidate that does so is dropped. Disassembly text comes from
         scripts\permanent\rom\thumb_dis.py (imported, not changed). Stages 2-4 are heuristics: LIKELY.
         Adopted from scripts\one-time\2026-10-18-disasm-study\ (study 2026-10-18); this copy is the maintained one.
"""
import argparse
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # scripts\permanent\disasm
ROOT = HERE.parents[2]                             # the LOG root
OUT_DIR = HERE / "data"                            # committed outputs (not the LOG data\ folder)
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from rom import thumb_dis  # noqa: E402

# ===== constants =====
ROM_BASE = 0x08000000
CRT0_WORDS = 0x140            # [fill dst, fill size, copy src, copy dst, copy size, main | 1]
IRQ_VECTOR = 0x03007FFC
HEADER_END = 0x080000C0       # cartridge header (branch word, logo, title, checksum); crt0 starts here
ROMS = ROOT / "data" / "roms"
GAMES = {"usa": "Dragon Ball Z - The Legacy of Goku II (USA).gba",
         "eu": "Dragon Ball Z - The Legacy of Goku II (Europe) (En,Fr,De,Es,It).gba",
         "bf": "Dragon Ball Z - Buu's Fury (USA).gba"}
REG = thumb_dis.REG
COND = thumb_dis.COND
MAX_ROUNDS = 400               # each round reaches one call level deeper


# ===== image: ROM plus the IWRAM overlay =====

class Image:
    def __init__(self, data: bytes):
        self.data = data
        fill, fill_size, src, dst, size, main = struct.unpack_from("<6I", data, CRT0_WORDS)
        if not (ROM_BASE <= src < ROM_BASE + len(data) and dst == 0x03000000 and main & 1):
            raise ValueError("crt0 words at rom:0x140 are not {fill, size, src, 0x03000000, size, main|1}")
        self.iw_src, self.iw_dst, self.iw_size = src - ROM_BASE, dst, size & ~3
        self.main = main
        self.sha1 = hashlib.sha1(data).hexdigest()

    def off(self, a: int):
        if ROM_BASE <= a < ROM_BASE + len(self.data):
            return a - ROM_BASE
        if self.iw_dst <= a < self.iw_dst + self.iw_size:
            return self.iw_src + a - self.iw_dst
        return None

    def u16(self, a):
        return struct.unpack_from("<H", self.data, self.off(a))[0]

    def u32(self, a):
        return struct.unpack_from("<I", self.data, self.off(a))[0]

    def ok(self, a, n=2):
        o = self.off(a)
        return o is not None and self.off(a + n - 1) == o + n - 1


# ===== Thumb flow decoder =====
# kind: op, ldr (lit), bl, b, bcc, bx, bxpc, movpc, addpc, ret, bad

def _thumb_written(h: int) -> set:
    """Low registers an instruction writes (for literal tracking)."""
    top = h >> 11
    if top < 4 or (h >> 10 == 0x10 and (h >> 6) & 15 not in (8, 10, 11)):
        return {h & 7}
    if top < 8:
        return set() if top == 5 else {(h >> 8) & 7}
    if h >> 10 == 0x11 and (h >> 8) & 3 in (0, 2):
        return {(h & 7) | ((h >> 4) & 8)}
    if h >> 12 == 5:
        return {h & 7} if h & 0x800 or (h & 0x200 and (h >> 10) & 3) else set()
    if h >> 13 == 3 or h >> 12 == 8:
        return {h & 7} if h & 0x800 else set()
    if h >> 12 in (9, 10):
        return {(h >> 8) & 7} if h >> 12 == 10 or h & 0x800 else set()
    if h >> 12 == 0xB and (h >> 9) & 3 == 2 and h & 0x800:
        return {i for i in range(8) if h >> i & 1}
    if h >> 12 == 0xC:
        return {(h >> 8) & 7} | ({i for i in range(8) if h >> i & 1} if h & 0x800 else set())
    return set()


def thumb_flow(img: Image, a: int):
    """(size, kind, target) for the Thumb instruction at a. target: branch target, literal address or reg."""
    if not img.ok(a, 2):
        return 2, "bad", None
    h = img.u16(a)
    top = h >> 11
    if top == 0x1E:
        if not img.ok(a + 2, 2) or img.u16(a + 2) >> 11 != 0x1F:
            return 2, "bad", None
        off = ((h & 0x7FF) << 12) | ((img.u16(a + 2) & 0x7FF) << 1)
        off -= 0x800000 if off & 0x400000 else 0
        return 4, "bl", a + 4 + off
    if top in (0x1D, 0x1F):                       # lone BL suffix, ARMv5 BLX: invalid on ARMv4T
        return 2, "bad", None
    if top == 0x1C:
        off = h & 0x7FF
        off -= 0x800 if off & 0x400 else 0
        return 2, "b", a + 4 + off * 2
    if h >> 12 == 0xD:
        c = (h >> 8) & 15
        if c == 15:
            return 2, "op", None                  # swi
        if c == 14:
            return 2, "bad", None
        off = h & 0xFF
        off -= 0x100 if off & 0x80 else 0
        return 2, "bcc", a + 4 + off * 2
    if h >> 10 == 0x11:
        op, d, s = (h >> 8) & 3, (h & 7) | ((h >> 4) & 8), (h >> 3) & 15
        if op == 3:
            if h & 0x87:                          # bx with H1 or SBZ bits set
                return 2, "bad", None
            return 2, ("bxpc" if s == 15 else "bx"), s
        if not h & 0xC0:                          # add/cmp/mov with two low registers: undefined on v4T
            return 2, "bad", None
        if d == 15 and op == 2:
            return 2, ("ret" if s == 14 else "movpc"), s
        if d == 15 and op == 0:
            return 2, "addpc", s
        return 2, "op", None
    if top == 9:
        return 2, "ldr", ((a + 4) & ~3) + (h & 0xFF) * 4
    if h >> 12 == 0xB:
        sub = (h >> 8) & 15
        if sub == 0 or sub in (4, 5, 0xC, 0xD):
            return 2, ("ret" if sub == 0xD else "op"), None
        return 2, "bad", None                     # cbz, bkpt, cps etc. are not ARMv4T
    return 2, "op", None


# ===== ARM flow decoder and text =====

def _sext(v: int, bits: int) -> int:
    return v - (1 << bits) if v >> (bits - 1) & 1 else v


def arm_flow(img: Image, a: int):
    """(size, kind, target) for the ARM instruction at a; same kinds as thumb_flow."""
    if a & 3 or not img.ok(a, 4):
        return 4, "bad", None
    w = img.u32(a)
    cond = w >> 28
    if cond == 15:
        return 4, "bad", None
    always = cond == 14
    if w & 0x0FFFFFF0 == 0x012FFF10:
        return 4, ("bx" if always else "op"), w & 15
    if w & 0x0E000000 == 0x0A000000:
        t = a + 8 + (_sext(w & 0xFFFFFF, 24) << 2)
        if w >> 24 & 1:
            return 4, "bl", t
        return 4, ("b" if always else "bcc"), t
    if w & 0x0F7F0000 == 0x051F0000:              # ldr rd,[pc,#+-imm]
        lit = a + 8 + ((w & 0xFFF) if w & 0x800000 else -(w & 0xFFF))
        if (w >> 12) & 15 == 15 and always:
            return 4, "ldrpc", lit
        return 4, "ldr", lit
    if w & 0x0E108000 == 0x08108000 and always:   # ldm with pc
        return 4, "ret", None
    if w & 0x0C000000 == 0 and (w >> 12) & 15 == 15 and always and not w & 0x0F900000 == 0x01000000:
        if w & 0x0FE00090 != 0x00000090 and (w >> 21) & 15 not in (8, 9, 10, 11):
            return 4, "ret", None                 # mov pc,lr and other writes to pc
    if w & 0x0C100000 == 0x04100000 and (w >> 12) & 15 == 15 and always:
        return 4, "ret", None                     # ldr pc,[...]
    return 4, "op", None


SHIFT = ["lsl", "lsr", "asr", "ror"]
DP = ["and", "eor", "sub", "rsb", "add", "adc", "sbc", "rsc", "tst", "teq", "cmp", "cmn", "orr", "mov", "bic", "mvn"]


def _op2(w: int) -> str:
    if w & 0x02000000:
        rot = ((w >> 8) & 15) * 2
        v = ((w & 0xFF) >> rot | (w & 0xFF) << (32 - rot)) & 0xFFFFFFFF if rot else w & 0xFF
        return f"#{v:#x}"
    rm, st = REG[w & 15], SHIFT[(w >> 5) & 3]
    if w & 0x10:
        return f"{rm},{st} {REG[(w >> 8) & 15]}"
    n = (w >> 7) & 31
    if n == 0 and st == "lsl":
        return rm
    if n == 0 and st == "ror":
        return f"{rm},rrx"
    return f"{rm},{st} #{n or 32}"


def arm_text(img: Image, a: int) -> str:
    """Text for the ARM instruction at a (ARMv4T subset the game uses; anything else prints .word)."""
    w = img.u32(a)
    c = "" if w >> 28 == 14 else COND[w >> 28]
    rd, rn = (w >> 12) & 15, (w >> 16) & 15
    if w & 0x0FFFFFF0 == 0x012FFF10:
        return f"bx{c} {REG[w & 15]}"
    if w & 0x0E000000 == 0x0A000000:
        return f"b{'l' if w >> 24 & 1 else ''}{c} {a + 8 + (_sext(w & 0xFFFFFF, 24) << 2):#x}"
    if w & 0x0F000000 == 0x0F000000:
        return f"swi{c} {w & 0xFFFFFF:#x}"
    if w & 0x0FC000F0 == 0x00000090:
        acc = f",{REG[rd]}" if w & 0x200000 else ""
        s = "s" if w & 0x100000 else ""
        return f"{'mla' if acc else 'mul'}{c}{s} {REG[rn]},{REG[w & 15]},{REG[(w >> 8) & 15]}{acc}"
    if w & 0x0F8000F0 == 0x00800090:
        op = ["umull", "umlal", "smull", "smlal"][(w >> 21) & 3]
        return f"{op}{c} {REG[rd]},{REG[rn]},{REG[w & 15]},{REG[(w >> 8) & 15]}"
    if w & 0x0FB00FF0 == 0x01000090:
        return f"swp{c}{'b' if w & 0x400000 else ''} {REG[rd]},{REG[w & 15]},[{REG[rn]}]"
    if w & 0x0FBF0FFF == 0x010F0000:
        return f"mrs{c} {REG[rd]},{'spsr' if w & 0x400000 else 'cpsr'}"
    if w & 0x0DB0F000 == 0x0120F000:
        src = _op2(w) if w & 0x02000000 else REG[w & 15]
        return f"msr{c} {'spsr' if w & 0x400000 else 'cpsr'}_{w >> 16 & 15:x},{src}"
    if w & 0x0E000090 == 0x00000090 and w & 0x60:
        op = {1: "strh" if not w & 0x100000 else "ldrh", 2: "ldrsb", 3: "ldrsh"}[(w >> 5) & 3]
        off = ((w >> 4) & 0xF0 | w & 15) if w & 0x400000 else REG[w & 15]
        sign = "" if w & 0x800000 else "-"
        off = f"#{sign}{off:#x}" if isinstance(off, int) else f"{sign}{off}"
        return f"{op}{c} {REG[rd]},[{REG[rn]},{off}]{'!' if w & 0x200000 else ''}" if w & 0x1000000 \
            else f"{op}{c} {REG[rd]},[{REG[rn]}],{off}"
    if w & 0x0C000000 == 0:
        op = (w >> 21) & 15
        s = "s" if w & 0x100000 and op not in (8, 9, 10, 11) else ""
        if op in (8, 9, 10, 11):
            return f"{DP[op]}{c} {REG[rn]},{_op2(w)}"
        if op in (13, 15):
            return f"{DP[op]}{c}{s} {REG[rd]},{_op2(w)}"
        return f"{DP[op]}{c}{s} {REG[rd]},{REG[rn]},{_op2(w)}"
    if w & 0x0C000000 == 0x04000000:
        op = ("ldr" if w & 0x100000 else "str") + ("b" if w & 0x400000 else "")
        if rn == 15 and not w & 0x02000000 and w & 0x1000000:
            lit = a + 8 + ((w & 0xFFF) if w & 0x800000 else -(w & 0xFFF))
            val = img.u32(lit) if img.ok(lit, 4) else 0
            return f"{op}{c} {REG[rd]},={val:#010x}"
        sign = "" if w & 0x800000 else "-"
        off = f"#{sign}{w & 0xFFF:#x}" if not w & 0x02000000 else f"{sign}{_op2(w & ~0x02000000)}"
        return f"{op}{c} {REG[rd]},[{REG[rn]},{off}]{'!' if w & 0x200000 else ''}" if w & 0x1000000 \
            else f"{op}{c} {REG[rd]},[{REG[rn]}],{off}"
    if w & 0x0E000000 == 0x08000000:
        mode = ["da", "ia", "db", "ib"][(w >> 23) & 3]
        regs = ",".join(REG[i] for i in range(16) if w >> i & 1)
        wb, user = "!" if w & 0x200000 else "", "^" if w & 0x400000 else ""
        return f"{'ldm' if w & 0x100000 else 'stm'}{c}{mode} {REG[rn]}{wb},{{{regs}}}{user}"
    return f".word {w:#010x}"


def thumb_text(img: Image, a: int) -> str:
    """Text for the Thumb instruction at a, from thumb_dis (IWRAM addresses are mapped through the overlay)."""
    o = img.off(a)
    text, _ = thumb_dis.dis(img.data, ROM_BASE + o)
    delta = a - (ROM_BASE + o)
    op = text.split(" ")[0]
    if delta and op in {"b", "bl"} | {"b" + x for x in COND}:
        text = f"{op} {int(text.split(' ')[1], 16) + delta:#x}"
    return text


# ===== one function body =====

class Body:
    def __init__(self, start, mode):
        self.start, self.mode = start, mode
        self.insns = {}          # addr -> (size, mode)
        self.calls = {}          # BL target -> mode
        self.bl_sites = []       # (site, target) for every BL
        self.tails = {}          # b into another known start -> mode
        self.lits, self.adrs, self.tables = set(), set(), []
        self.seeds = []          # (value, how): bx, call_via, ldr pc, IRQ vector and pc-relative values
        self.flags = set()
        self.returns = 0

    @property
    def end(self):
        return max(a + s for a, (s, _) in self.insns.items()) if self.insns else self.start

    def span(self, img) -> int:
        """Contiguous bytes from the start: own instructions, pools, switch tables and 0x0000 pads."""
        own = set()
        for a, (s, _) in self.insns.items():
            own.update(range(a, a + s))
        for lit in self.lits:
            own.update(range(lit, lit + 4))
        for tab, n in self.tables:
            own.update(range(tab, tab + n))
        x = self.start
        while x in own or (img.ok(x, 1) and img.data[img.off(x)] == 0 and any(x + d in own for d in (1, 2, 3))):
            x += 1
        return x - self.start


def _switch_table(hist, reg):
    """`add rT,pc,#n ; [cmp rI,#N ; bcs] ; ldrb|ldrh rX,[rT,rI] ; lsl rX,#1 ; add pc,rX` -> (table, size, n)."""
    back = list(reversed(hist[:-1]))
    load = next(((ad, h) for ad, h in back[:4] if h >> 12 == 5 and (h >> 9) & 7 in (5, 6) and h & 7 == reg), None)
    if load is None:
        return None
    esize = 1 if (load[1] >> 9) & 7 == 6 else 2
    rb, ro = (load[1] >> 3) & 7, (load[1] >> 6) & 7
    addpc = next(((ad, h) for ad, h in back if ad < load[0] and h >> 11 == 0x14 and (h >> 8) & 7 in (rb, ro)), None)
    if addpc is None:
        return None
    table = ((addpc[0] + 4) & ~3) + (addpc[1] & 0xFF) * 4
    idx = ro if (addpc[1] >> 8) & 7 == rb else rb
    for i in range(len(hist) - 2, 0, -1):
        ad, h = hist[i - 1]
        if h >> 11 == 5 and (h >> 8) & 7 == idx and hist[i][1] >> 8 in (0xD2, 0xD8):
            return table, esize, (h & 0xFF) + (1 if hist[i][1] >> 8 == 0xD8 else 0)
    return None


def explore(img: Image, start: int, mode: str, starts, noreturn=frozenset(), call_via=None) -> Body:
    """Recursive descent of one function; a path stops at another known start (tail call)."""
    body = Body(start, mode)
    call_via = call_via or {}
    work = [(start, mode, {}, [])]
    while work:
        a, m, regs, hist = work.pop()
        while True:
            if a in body.insns:
                break
            if a != start and a in starts:
                body.tails[a] = m
                break
            size, kind, tgt = (thumb_flow if m == "T" else arm_flow)(img, a)
            if kind == "bad":
                body.flags.add(f"bad@{a:#x}")
                break
            body.insns[a] = (size, m)
            # literal tracking: compute the new value before the written registers are dropped
            new = None
            if m == "T":
                h = img.u16(a)
                hist = hist[-10:] + [(a, h)]
                if kind == "ldr" and img.ok(tgt, 4):
                    new = ((h >> 8) & 7, img.u32(tgt))
                elif h >> 8 == 0x44 and (h >> 3) & 15 == 15 and (h & 7 | (h >> 4) & 8) in regs:
                    d = h & 7 | (h >> 4) & 8                                  # add rX,pc
                    new = (d, (regs[d] + a + 4) & 0xFFFFFFFF)
                    body.seeds.append((new[1], "pcrel"))
                elif h >> 11 == 0x14:                                         # add rX,pc,#n (adr)
                    new = ((h >> 8) & 7, ((a + 4) & ~3) + (h & 0xFF) * 4)
                    body.adrs.add(new[1])
                if h >> 11 == 0xC and (h >> 3) & 7 in regs and h & 7 in regs:  # str rX,[rY,#n]
                    if (regs[(h >> 3) & 7] + ((h >> 6) & 31) * 4) & 0xFFFFFFFF == IRQ_VECTOR:
                        body.seeds.append((regs[h & 7], "irq"))
                for r in _thumb_written(h):
                    regs.pop(r, None)
            else:
                w = img.u32(a)
                if kind == "ldr" and img.ok(tgt, 4):
                    new = ((w >> 12) & 15, img.u32(tgt))
                if w & 0x0E000000 == 0x08000000 and w & 0x100000:
                    for r in range(16):
                        if w >> r & 1:
                            regs.pop(r, None)
                regs.pop((w >> 12) & 15, None)
            if new:
                regs[new[0]] = new[1]
            if kind in ("ldr", "ldrpc"):
                body.lits.add(tgt)
            # control flow
            if kind == "bl":
                body.calls[tgt] = m
                body.bl_sites.append((a, tgt))
                if tgt in noreturn:
                    break
                if tgt in call_via and call_via[tgt] in regs:
                    body.seeds.append((regs[call_via[tgt]], "call_via"))
                for r in (0, 1, 2, 3, 12, 14):
                    regs.pop(r, None)
            elif kind == "b":
                if m == "A" and (abs(tgt - a) > 0x1000 or "veneer" in body.flags):   # crt0 or a veneer: tail
                    body.tails[tgt] = m
                    break
                a = tgt
                continue
            elif kind == "bcc":
                work.append((tgt, m, dict(regs), list(hist)))
            elif kind == "bx":
                if m == "A" and img.ok(a - 4, 4) and img.u32(a - 4) in (0xE1A0E00F, 0xE28FE000):
                    a += size                                                # mov lr,pc ; bx rX = call
                    continue
                if tgt != 14 and tgt in regs:
                    body.seeds.append((regs[tgt], "bx"))
                else:
                    body.returns += 1
                break
            elif kind == "ldrpc":
                if img.ok(tgt, 4):
                    body.seeds.append((img.u32(tgt), "ldrpc"))
                break
            elif kind == "bxpc":
                if a & 3:
                    body.flags.add(f"bxpc_unaligned@{a:#x}")
                    break
                a, m = a + 4, "A"
                body.flags.add("veneer")
                continue
            elif kind == "addpc":
                sw = _switch_table(hist, tgt)
                if sw is None:
                    body.flags.add(f"switch?@{a:#x}")
                    break
                tab, esize, n = sw
                body.tables.append((tab, esize * n))
                for i in range(n):
                    e = img.data[img.off(tab) + i] if esize == 1 else img.u16(tab + 2 * i)
                    work.append((a + 4 + e * 2, m, {}, []))
                break
            elif kind == "movpc":
                body.flags.add(f"movpc@{a:#x}")
                break
            elif kind == "ret":
                body.returns += 1
                break
            a += size
            if len(body.insns) > 20000:
                body.flags.add("runaway")
                work = []
                break
    return body


# ===== whole-ROM map =====

class Map:
    def __init__(self, img):
        self.img = img
        self.funcs = {}          # start -> {"mode", "found_by"}
        self.bodies, self.owned, self.starts_insn = {}, {}, set()
        self.pool, self.jt = set(), set()
        self.vtables, self.lists, self.ptr_tables = {}, {}, {}
        self.noret = frozenset()
        self.rejected = {}
        self.code_hi = ROM_BASE
        self.refs, self.callers, self.vt_refs = {}, {}, {}
        self.shared = 0


def _add(mp, a, mode, how):
    """Add a function start; mode "?" takes Thumb for an odd value, ARM for an even one."""
    if mode == "?":
        mode = "T" if a & 1 else "A"
    a &= ~1 if mode == "T" else ~3
    if mp.img.off(a) is None or a in mp.funcs:
        return 0
    mp.funcs[a] = {"mode": mode, "found_by": how}
    return 1


def _in_code(mp, a):
    return ROM_BASE <= a < mp.code_hi or mp.img.iw_dst <= a < mp.img.iw_dst + mp.img.iw_size


def _reject(mp, why):
    mp.rejected[why] = mp.rejected.get(why, 0) + 1
    return False


def _start_like(mp, a):
    """An instruction inside a known body that still looks like a function start: a push, or the
    instruction before it ends a path (pop {pc} or bx). Such a body swallowed a function it tail-jumps to."""
    h = mp.img.u16(a)
    if h >> 9 == 0x5A:
        return True
    prev = mp.img.u16(a - 2) if mp.img.ok(a - 2) else 0
    return a - 2 in mp.starts_insn and (prev >> 8 == 0xBD or prev & 0xFF87 == 0x4700)


def _candidate(mp, a, how, strict=False, inner=False):
    """Pointer candidate check: the code at a must decode clean without touching known bytes. inner=True
    (code literals only) also accepts an instruction start inside a known body and so splits it."""
    if a in mp.funcs:
        return False
    if a in mp.starts_insn:
        return True if inner or _start_like(mp, a) else _reject(mp, how + ":inner")
    if a in mp.owned or a in mp.pool or a in mp.jt:
        return _reject(mp, how + ":mid")
    b = explore(mp.img, a, "T", mp.funcs, mp.noret)
    if any(f.startswith("bad") or f == "runaway" for f in b.flags) or not b.insns:
        return _reject(mp, how + ":bad")
    for x, (s, _) in b.insns.items():
        if any(x + k in mp.owned or x + k in mp.pool or x + k in mp.jt for k in range(s)):
            return _reject(mp, how + ":overlap")
    if strict and not _shape_ok(mp.img, a, b):
        return _reject(mp, how + ":shape")
    return True


def _shape_ok(img, a, b):
    """A function start: a push within the first 8 straight-line instructions (armcc schedules loads before
    it, up to 5 seen at 0x08017174), or a leaf: no BL, a return, no pop {pc} (that is the tail of a body)."""
    x = a
    for _ in range(8):
        size, kind, _ = thumb_flow(img, x)
        if img.u16(x) >> 9 == 0x5A:
            return True
        if kind not in ("op", "ldr"):
            break
        x += size
    pops = any(m == "T" and img.u16(y) >> 8 == 0xBD for y, (s, m) in b.insns.items())
    if b.tails and not b.calls and not pops and not b.returns and len(b.insns) <= 8:
        return True                   # a stub that sets arguments, then `b` to a known start
    return bool(b.returns) and not b.calls and not pops


def _pass(mp):
    """Explore every known start with the current start set; returns the count of new starts."""
    img = mp.img
    call_via = {a: (img.u16(a) >> 3) & 15 for a, f in mp.funcs.items()
                if f["mode"] == "T" and img.ok(a) and img.u16(a) & 0xFFC7 == 0x4700}
    mp.bodies, mp.pool, mp.jt = {}, set(), set()
    for a in sorted(mp.funcs):
        b = explore(img, a, mp.funcs[a]["mode"], mp.funcs, mp.noret, call_via)
        mp.bodies[a] = b
        for lit in b.lits:
            mp.pool.update(range(lit, lit + 4))
        for tab, n in b.tables:
            mp.jt.update(range(tab, tab + n))
    mp.owned, mp.starts_insn = {}, set()
    for a, b in mp.bodies.items():
        for x, (s, _) in b.insns.items():
            mp.starts_insn.add(x)
            for k in range(s):
                mp.owned.setdefault(x + k, a)
    rom_ends = [b.end for a, b in mp.bodies.items() if ROM_BASE <= a < ROM_BASE + len(img.data)]
    mp.code_hi = max([mp.code_hi] + rom_ends)
    new = 0
    pcrel = {val for b in mp.bodies.values() for val, how in b.seeds if how == "pcrel"}
    for b in list(mp.bodies.values()):
        for t, m in list(b.calls.items()) + list(b.tails.items()):
            new += _add(mp, t, m, "bl" if t in b.calls else "tail")
        for val, how in b.seeds:
            if how == "pcrel":
                _self_relative(mp, val, pcrel)
            elif img.off(val & ~1) is not None:
                new += _add(mp, val, "?", how)
    for base, ts in mp.lists.items():
        for t in ts:
            new += _add(mp, t, "T", "ctor_list")
    return new


def _self_relative(mp, base, ends=frozenset()):
    """A list of words w with target = word address + w that resolve to Thumb code (static constructors).
    The runner computes its start and end with `ldr ; add rX,pc`, so any other such value ends the list."""
    if base in mp.lists or base & 3 or mp.img.off(base) is None:
        return
    out = []
    for i in range(1024):
        p = base + 4 * i
        if not mp.img.ok(p, 4) or (i and p in ends):
            break
        t = (p + mp.img.u32(p)) & 0xFFFFFFFF
        if not (t & 1 and ROM_BASE <= t - 1 < mp.code_hi):
            break
        out.append(t - 1)
    if len(out) >= 2:
        mp.lists[base] = out


def _literal_seeds(mp):
    """Odd literal-pool values into the code range (function pointers loaded by code)."""
    new = 0
    for b in list(mp.bodies.values()):
        for lit in b.lits:
            if mp.img.ok(lit, 4):
                v = mp.img.u32(lit)
                if v & 1 and ROM_BASE <= v - 1 < mp.code_hi and _candidate(mp, v - 1, "literal", inner=True):
                    new += _add(mp, v, "T", "literal")
    return new


def _vtables(mp):
    """Even literals into the code range whose words resolve base-relative to Thumb code (2 entries or more)."""
    cands = set()
    for b in mp.bodies.values():
        for lit in b.lits:
            if mp.img.ok(lit, 4):
                v = mp.img.u32(lit)
                if not v & 3 and ROM_BASE <= v < mp.code_hi and v not in mp.owned:
                    cands.add(v)
    new, covered = 0, set()
    for base, ts in mp.vtables.items():
        covered.update(range(base, base + 4 * len(ts)))
    for base in sorted(cands):
        if base in covered and base not in mp.vtables:
            continue                  # inside an accepted vtable: its words are relative to that base
        out = []
        for i in range(256):
            p = base + 4 * i
            if p in mp.owned or not mp.img.ok(p, 4) or (i and (p in mp.vtables or p in cands)):
                break                 # another base that code loads starts here: this table ends
            t = (base + mp.img.u32(p)) & 0xFFFFFFFF
            if not (t & 1 and ROM_BASE <= t - 1 < mp.code_hi):
                break
            if t - 1 not in mp.funcs and not _candidate(mp, t - 1, "vtable", strict=True):
                break
            out.append(t - 1)
        if len(out) >= 2:
            mp.vtables[base] = out
            covered.update(range(base, base + 4 * len(out)))
            for t in out:
                new += _add(mp, t, "T", "vtable")
    return new


def _symbol_tables(mp, syms):
    """symbols.py tables {name: (addr, count, stride, [offsets], rel)}, rel "abs", "self" or "base"."""
    new = 0
    for name, (addr, count, stride, offs, rel) in syms.get("ptr_tables", {}).items():
        got = []
        for i in range(count):
            for o in offs:
                p = addr + i * stride + o
                if mp.img.ok(p, 4):
                    v = mp.img.u32(p)
                    t = (v + {"self": p, "base": addr}.get(rel, 0)) & 0xFFFFFFFF
                    if t & 1 and _in_code(mp, t - 1):
                        got.append(t - 1)
                        new += _add(mp, t, "T", "table")
        mp.ptr_tables[name] = got
    for a, mode in syms.get("functions", {}).items():
        new += _add(mp, a, mode, "symbols")
    return new


def _word_refs(mp):
    """{target: [word addresses]} for aligned odd ROM words into the code range."""
    import array
    words = array.array("I")
    words.frombytes(mp.img.data[:len(mp.img.data) & ~3])
    refs = {}
    for i, v in enumerate(words):
        if v & 1 and ROM_BASE < v < mp.code_hi:
            refs.setdefault(v - 1, []).append(ROM_BASE + 4 * i)
    return refs


def _rom_scan(mp):
    """Aligned odd words anywhere in the ROM into the code range: kept when they decode clean and start with
    `push {..,lr}` or return, or when a neighbour word is also a code pointer (a table)."""
    refs, new = _word_refs(mp), 0
    for t in sorted(refs):
        if t in mp.funcs:
            continue
        table = any(mp.img.ok(w + d, 4) and mp.img.u32(w + d) & 1 and ROM_BASE < mp.img.u32(w + d) < mp.code_hi
                    for w in refs[t] for d in (-4, 4))
        if _candidate(mp, t, "rom_ptr", strict=not table):
            new += _add(mp, t, "T", "rom_ptr")
    return new


def _gap_scan(mp):
    """Prologue search in unclassified code-region bytes: the first halfword of a gap, and every push that
    follows a pop {pc} or bx, kept when it decodes clean with the function shape (as Ghidra's start search)."""
    known = mp.owned.keys() | mp.pool | mp.jt
    for base, ts in list(mp.vtables.items()) + list(mp.lists.items()):
        known |= set(range(base, base + 4 * len(ts)))
    new, a = 0, HEADER_END
    while a < mp.code_hi - 2:
        if a in known or mp.img.u16(a) == 0:
            a += 2
            continue
        start = a
        while a < mp.code_hi and a not in known:
            a += 2
        for x in range(start, a, 2):
            h, prev = mp.img.u16(x), mp.img.u16(x - 2)
            first = x == start
            boundary = prev >> 8 == 0xBD or prev & 0xFF87 == 0x4700 or prev >> 11 == 0x1C or not x & 3
            if (first or (boundary and h >> 8 == 0xB5)) and _candidate(mp, x, "prologue", strict=True):
                new += _add(mp, x, "T", "prologue")
                break             # re-run the passes before trusting the rest of this gap
    return new


def _noreturn(mp):
    """Starts whose every path ends in a self loop, a call to another of these, or a bad decode stop."""
    return frozenset(a for a, b in mp.bodies.items()
                     if b.insns and b.returns == 0 and not b.tails and not b.seeds and not b.tables
                     and not any(f.startswith(("switch?", "movpc", "bad", "veneer")) for f in b.flags))


def build(img: Image, syms: dict) -> Map:
    mp = Map(img)
    entry = img.u32(ROM_BASE)
    if entry >> 24 != 0xEA:
        raise ValueError("the header word is not an ARM branch")
    _add(mp, ROM_BASE + 8 + (_sext(entry & 0xFFFFFF, 24) << 2), "A", "entry")
    _add(mp, img.main, "T", "main")
    # confident seeds first, so the guessed ones (vtables, ROM words) are checked against known code
    stages = [lambda: _literal_seeds(mp) + _symbol_tables(mp, syms), lambda: _vtables(mp), lambda: _rom_scan(mp),
              lambda: _gap_scan(mp)]
    stage = 0
    for _ in range(MAX_ROUNDS):
        n = _pass(mp)
        mp.noret = _noreturn(mp)
        n += sum(f() for f in stages[:stage + 1])
        if n == 0:
            if stage == len(stages) - 1:
                break
            stage += 1
    while _pass(mp):
        pass
    mp.refs = _word_refs(mp)
    for a, b in mp.bodies.items():
        for site, t in b.bl_sites:
            if mp.owned.get(site) == a:          # a site two bodies share counts once, for its owning body
                mp.callers.setdefault(t, []).append((site, a))
    seen = {}
    for a, b in mp.bodies.items():
        for x in b.insns:
            seen[x] = seen.get(x, 0) + 1
    mp.shared = sum(1 for n in seen.values() if n > 1)
    for ts in list(mp.vtables.values()) + list(mp.lists.values()):
        for t in ts:
            mp.vt_refs[t] = mp.vt_refs.get(t, 0) + 1
    return mp


# ===== coverage =====

def coverage(mp) -> dict:
    img = mp.img
    kind = {}
    for b in mp.bodies.values():
        for x, (s, m) in b.insns.items():
            for k in range(s):
                kind[x + k] = "thumb" if m == "T" else "arm"
    for x in mp.pool:
        kind.setdefault(x, "pool")
    for x in mp.jt:
        kind.setdefault(x, "switch")
    for x in range(ROM_BASE, HEADER_END):
        kind.setdefault(x, "header")
    for base, ts in list(mp.vtables.items()) + list(mp.lists.items()):
        for k in range(4 * len(ts)):
            kind.setdefault(base + k, "vtable")
    for a in _data_refs(mp):         # strings the code addresses by adr or by a literal pointer
        n = _cstring(img, a)
        for k in range(n):
            kind.setdefault(a + k, "string")
    counts, gaps, run = {}, [], None
    for a in range(ROM_BASE, mp.code_hi):
        k = kind.get(a)
        if k is None and img.data[a - ROM_BASE] == 0 and any(kind.get(a + d) for d in (1, 2, 3)):
            k = "pad"
        if k is None:
            run = a if run is None else run
        elif run is not None:
            gaps.append((run, a - run))
            run = None
        counts[k or "unknown"] = counts.get(k or "unknown", 0) + 1
    if run is not None:
        gaps.append((run, mp.code_hi - run))
    stray_bl = 0                     # BL-shaped pairs in unclassified bytes that hit a known start
    for g, n in gaps:
        for a in range(g + (g & 1), g + n - 3, 2):
            size, kd, t = thumb_flow(img, a)
            stray_bl += kd == "bl" and t in mp.funcs
    iw = sum(1 for a in kind if img.iw_dst <= a < img.iw_dst + img.iw_size)
    return {"region_bytes": mp.code_hi - ROM_BASE, "counts": counts, "stray_bl": stray_bl,
            "gaps": sorted(gaps, key=lambda g: -g[1]), "iwram_decoded": iw}


def _data_refs(mp) -> set:
    """Addresses in the code region that code reaches as data: adr targets and literal values."""
    out = set()
    for b in mp.bodies.values():
        out |= b.adrs
        for lit in b.lits:
            if mp.img.ok(lit, 4):
                out.add(mp.img.u32(lit))
    return {a for a in out if ROM_BASE <= a < mp.code_hi and a not in mp.owned}


def _cstring(img, a) -> int:
    """Bytes of a printable NUL-terminated string at a, padded to 4; 0 when it is not one."""
    o, n = img.off(a), 0
    while o + n < len(img.data) and (32 <= img.data[o + n] < 127 or img.data[o + n] in (9, 10, 13)):
        n += 1
    if n < 2 or o + n >= len(img.data) or img.data[o + n]:
        return 0
    n += 1
    while (a + n) & 3 and img.data[o + n] == 0:
        n += 1
    return n


def _gap_kind(img, a, n):
    blob = img.data[a - ROM_BASE:a - ROM_BASE + n]
    if not any(blob):
        return "zeros"
    if n >= 8 and sum(32 <= c < 127 or c in (0, 10) for c in blob) > 0.9 * n:
        return "text"
    return "data?"


# ===== output =====

def _count(it):
    d = {}
    for x in it:
        d[x] = d.get(x, 0) + 1
    return d


def write(mp, cov, syms, out: Path, game: str) -> list:
    out.mkdir(parents=True, exist_ok=True)
    img, names, tags = mp.img, syms.get("names", {}), syms.get("tags", {})
    rows = []
    for a in sorted(mp.funcs):
        b = mp.bodies[a]
        rows.append({"address": f"{a:#010x}", "size": b.span(img), "extent": b.end - a,
                     "mode": "ARM" if mp.funcs[a]["mode"] == "A" else "Thumb",
                     "name": names.get(a, ""), "callers": len(mp.callers.get(a, [])),
                     "caller_funcs": len({f for _, f in mp.callers.get(a, [])}),
                     "ptr_refs": len(mp.refs.get(a, [])), "vt_refs": mp.vt_refs.get(a, 0),
                     "found_by": mp.funcs[a]["found_by"], "flags": " ".join(sorted(b.flags)),
                     "bible": tags.get(a, "")})
    with (out / "functions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    c, region = cov["counts"], cov["region_bytes"]
    known = region - c.get("unknown", 0)
    data_out = len(img.data) - region - img.iw_size
    flagged = lambda p: sum(any(x.startswith(p) for x in mp.bodies[a].flags) for a in mp.funcs)  # noqa: E731
    lines = [f"codemap {game}: ROM SHA-1 {img.sha1}, {len(img.data):,} bytes",
             f"functions: {len(mp.funcs)} (Thumb {sum(f['mode'] == 'T' for f in mp.funcs.values())}, "
             f"ARM {sum(f['mode'] == 'A' for f in mp.funcs.values())}); named {sum(1 for a in mp.funcs if a in names)}",
             "found by: " + ", ".join(f"{k} {v}" for k, v in sorted(_count(f["found_by"] for f in mp.funcs.values()).items())),
             f"flags: bad {flagged('bad')}, unresolved switch {flagged('switch?')}, mov pc {flagged('movpc')}, "
             f"veneer {flagged('veneer')}; noreturn {len(mp.noret)}; instructions in two bodies {mp.shared}",
             "pointer candidates rejected: " + (", ".join(f"{k} {v}" for k, v in sorted(mp.rejected.items())) or "none"),
             f"vtables (base-relative): {len(mp.vtables)} with {sum(len(v) for v in mp.vtables.values())} entries; "
             f"self-relative lists: {len(mp.lists)} with {sum(len(v) for v in mp.lists.values())} entries; "
             f"switch tables: {len({t for b in mp.bodies.values() for t, _ in b.tables})}",
             "",
             f"code region rom:0x0-rom:{mp.code_hi - ROM_BASE:#x}: {region:,} bytes ({100 * region / len(img.data):.2f} % of the ROM)",
             *[f"  {k:8} {v:9,} bytes  {100 * v / region:6.2f} %" for k, v in sorted(c.items(), key=lambda kv: -kv[1])],
             f"  classified {known:,} of {region:,} = {100 * known / region:.2f} %; BL-shaped pairs to a known start "
             f"inside unclassified bytes: {cov['stray_bl']}",
             f"IWRAM block rom:{img.iw_src:#x} -> {img.iw_dst:#x}, {img.iw_size:#x} bytes: {cov['iwram_decoded']:,} bytes decoded as code",
             f"outside the code region and the IWRAM block: {data_out:,} bytes ({100 * data_out / len(img.data):.2f} % of the ROM)",
             "", "largest unclassified gaps in the code region (address, bytes, look, name):"]
    for a, n in cov["gaps"][:30]:
        lines.append(f"  {a:#010x} {n:7,}  {_gap_kind(img, a, n):6} {names.get(a, '')}")
    (out / "coverage.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    js = {"game": game, "sha1": img.sha1, "code_hi": mp.code_hi,
          "iwram": [img.iw_src, img.iw_dst, img.iw_size],
          "functions": {f"{a:#x}": [mp.funcs[a]["mode"], mp.bodies[a].span(img), mp.bodies[a].end - a]
                        for a in sorted(mp.funcs)},
          "vtables": {f"{k:#x}": [f"{t:#x}" for t in v] for k, v in mp.vtables.items()},
          "lists": {f"{k:#x}": [f"{t:#x}" for t in v] for k, v in mp.lists.items()},
          "switch_tables": sorted({(t, n) for b in mp.bodies.values() for t, n in b.tables}),
          "pool": sorted({lit for b in mp.bodies.values() for lit in b.lits}),
          "coverage": {k: v for k, v in cov.items() if k != "gaps"}}
    (out / "codemap.json").write_text(json.dumps(js, indent=0) + "\n", encoding="utf-8", newline="\n")
    return lines


def load_symbols(game: str) -> dict:
    try:
        import symbols
    except ImportError:
        return {}
    return symbols.for_codemap(game)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="usa", choices=sorted(GAMES))
    ap.add_argument("--rom")
    ap.add_argument("--out")
    ap.add_argument("--no-symbols", action="store_true", help="heuristics only (an independent map for checks)")
    args = ap.parse_args(argv)
    rom = Path(args.rom) if args.rom else ROMS / GAMES[args.game]
    out = Path(args.out) if args.out else (OUT_DIR if args.game == "usa" else OUT_DIR / args.game)
    data_dir = (ROOT / "data").resolve()
    if out.resolve() == data_dir or data_dir in out.resolve().parents:
        raise ValueError("refusing to write under data")
    img = Image(rom.read_bytes())
    syms = {} if args.no_symbols else load_symbols(args.game)
    mp = build(img, syms)
    print("\n".join(write(mp, coverage(mp), syms, out, args.game)[:18]))


if __name__ == "__main__":
    main(sys.argv[1:])
