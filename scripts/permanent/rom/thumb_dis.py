r"""
thumb_dis.py - Minimal ARMv4T Thumb disassembler over a ROM buffer (base, padded or patched).

Usage:   py -3 -I scripts\permanent\rom\thumb_dis.py <rom.gba> <hexaddr> [count]
Output:  one line per instruction: address, raw bytes, text. Literal loads show the pool value.
API:     dis(rom, addr) -> (text, size); listing(rom, addr, count) -> [(addr, text)]
Rules:   addr is a GBA address (0x08xxxxxx). Text shapes match scripts\one-time\2026-10-18-save-slots\thumb.py, without
         the pool address. Kept apart from the encoder in patches\ssj2_form.py on purpose: the tests
         check new code with this decoder, so the two must not share code.
"""
import struct
import sys
from pathlib import Path

# ===== constants =====
ROM_BASE = 0x08000000
REG = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "sp", "lr", "pc"]
COND = ["eq", "ne", "cs", "cc", "mi", "pl", "vs", "vc", "hi", "ls", "ge", "lt", "gt", "le", "al", "nv"]
ALU = ["and", "eor", "lsl", "lsr", "asr", "adc", "sbc", "ror", "tst", "neg", "cmp", "cmn", "orr", "mul", "bic", "mvn"]


def _u16(rom: bytes, a: int) -> int:
    return struct.unpack_from("<H", rom, a - ROM_BASE)[0]


def _u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE)[0]


def _rlist(m: int, extra: str = None) -> str:
    regs = [REG[i] for i in range(8) if m >> i & 1] + ([extra] if extra else [])
    return "{" + ",".join(regs) + "}"


# ===== decoder =====

def dis(rom: bytes, a: int) -> tuple:
    """(text, size) for the Thumb instruction at GBA address a."""
    h = _u16(rom, a)
    top = h >> 11
    rd, rs = h & 7, (h >> 3) & 7
    if top < 3:
        return f"{['lsl', 'lsr', 'asr'][top]} {REG[rd]},{REG[rs]},#{(h >> 6) & 31}", 2
    if top == 3:
        rn = (h >> 6) & 7
        src = f"#{rn}" if h & 0x400 else REG[rn]
        return f"{'sub' if h & 0x200 else 'add'} {REG[rd]},{REG[rs]},{src}", 2
    if top < 8:
        return f"{['mov', 'cmp', 'add', 'sub'][top - 4]} {REG[(h >> 8) & 7]},#{h & 0xFF:#x}", 2
    if h >> 10 == 0x10:
        return f"{ALU[(h >> 6) & 15]} {REG[rd]},{REG[rs]}", 2
    if h >> 10 == 0x11:
        op, d, s = (h >> 8) & 3, rd | ((h >> 4) & 8), (h >> 3) & 15
        if op == 3:
            return f"bx {REG[s]}", 2
        return f"{['add', 'cmp', 'mov'][op]} {REG[d]},{REG[s]}", 2
    if top == 9:
        lit = ((a + 4) & ~3) + (h & 0xFF) * 4
        value = _u32(rom, lit) if ROM_BASE <= lit < ROM_BASE + len(rom) - 3 else 0
        return f"ldr {REG[(h >> 8) & 7]},={value:#010x}", 2
    if h >> 12 == 5:
        ro = (h >> 6) & 7
        ops = ["strh", "ldsb", "ldrh", "ldsh"] if h & 0x200 else ["str", "strb", "ldr", "ldrb"]
        return f"{ops[(h >> 10) & 3]} {REG[rd]},[{REG[rs]},{REG[ro]}]", 2
    if h >> 13 == 3:
        byte, load, off = h & 0x1000, h & 0x800, (h >> 6) & 31
        return f"{'ldr' if load else 'str'}{'b' if byte else ''} {REG[rd]},[{REG[rs]},#{off if byte else off * 4:#x}]", 2
    if h >> 12 == 8:
        return f"{'ldrh' if h & 0x800 else 'strh'} {REG[rd]},[{REG[rs]},#{((h >> 6) & 31) * 2:#x}]", 2
    if h >> 12 == 9:
        return f"{'ldr' if h & 0x800 else 'str'} {REG[(h >> 8) & 7]},[sp,#{(h & 0xFF) * 4:#x}]", 2
    if h >> 12 == 10:
        return f"add {REG[(h >> 8) & 7]},{'sp' if h & 0x800 else 'pc'},#{(h & 0xFF) * 4:#x}", 2
    if h >> 8 == 0xB0:
        return f"{'sub' if h & 0x80 else 'add'} sp,#{(h & 0x7F) * 4:#x}", 2
    if h >> 12 == 0xB and (h >> 9) & 3 == 2:
        pop = h & 0x800
        extra = ("pc" if pop else "lr") if h & 0x100 else None
        return f"{'pop' if pop else 'push'} {_rlist(h & 0xFF, extra)}", 2
    if h >> 12 == 0xC:
        return f"{'ldmia' if h & 0x800 else 'stmia'} {REG[(h >> 8) & 7]}!,{_rlist(h & 0xFF)}", 2
    if h >> 12 == 0xD:
        c = (h >> 8) & 15
        if c == 15:
            return f"swi {h & 0xFF:#x}", 2
        off = h & 0xFF
        off -= 0x100 if off & 0x80 else 0
        return f"b{COND[c]} {a + 4 + off * 2:#x}", 2
    if top == 0x1C:
        off = h & 0x7FF
        off -= 0x800 if off & 0x400 else 0
        return f"b {a + 4 + off * 2:#x}", 2
    if top == 0x1E:
        h2 = _u16(rom, a + 2)
        if h2 >> 11 == 0x1F:
            off = ((h & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
            off -= 0x800000 if off & 0x400000 else 0
            return f"bl {a + 4 + off:#x}", 4
    return f".hword {h:#06x}", 2


def listing(rom: bytes, a: int, count: int) -> list:
    out = []
    for _ in range(count):
        text, size = dis(rom, a)
        out.append((a, text))
        a += size
    return out


if __name__ == "__main__":
    data = Path(sys.argv[1]).read_bytes()
    at = int(sys.argv[2], 16)
    for addr, text in listing(data, at, int(sys.argv[3]) if len(sys.argv) > 3 else 40):
        size = 4 if text.startswith("bl ") else 2
        print(f"{addr:08x}  {data[addr - ROM_BASE:addr - ROM_BASE + size].hex():<8}  {text}")
