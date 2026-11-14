r"""Shape E: `mov rX,#imm` then `lsl rD,rX,#sh` with a GAP between the two instructions.

WHY THIS TOOL EXISTS. `scripts\one-time\2026-11-13-journal-menu\imagewide.py` decodes ADJACENT
halfword pairs only. The compiler interleaves an unrelated instruction between the mov and the lsl
whenever a register is free, and every such site is invisible to that scan. On 2026-11-13 this tool
found FOUR scouter menu sites that imagewide.py could not see, three of them readers of the live
block the menu grow has to move. Four moved sites and four left behind is the silent overrun the
whole menu grow exists to prevent.

Three things it does that imagewide.py does not:
  1. allows up to WINDOW halfwords between the mov and the lsl, and drops the candidate if anything
     in between writes the mov's register. Every drop is PRINTED, so a drop is never silent.
  2. accepts `lsl rD,rX,#sh` with rD different from rX, not only the in-place form.
  3. watches RANGES, not single values. A site that folds a field offset into the base constant
     (`+0x6A8` rather than `+0x680` plus `#0x28`) carries a value no exact match would catch.

What it still cannot see: a value built by an add chain, loaded from a literal pool, or formed from
another register. Use the listing by eye, and poolrefs.py, for those. Its count is a FLOOR.

Promoted to a permanent tool on 2026-11-13. It was written in a one-time folder, which `.gitignore`
excludes, so nothing tracked it and nothing indexed it. A shape this blind spot needs must be
findable, or the next search writes a third scanner.

Run: py -3.14 -P scripts\permanent\rom\gapscan.py <rom.gba> [lo] [hi]
"""
import struct
import sys
from pathlib import Path

# (first, last, name). Inclusive at both ends, because the last byte of a block is a real offset.
WATCHED = ((0x154, 0x15C, "journal active list header"),
           (0x280, 0x290, "scouter list 2 header and its first entries"),
           (0x2B0, 0x2C0, "journal done list header"),
           (0x400, 0x41C, "journal tail fields"),
           (0x444, 0x444, "journal object size"),
           (0x680, 0x6B0, "scouter live block and its fields"),
           (0x6B0, 0x6B0, "scouter object size"))
WINDOW = 10


def watched(value: int) -> str:
    for lo, hi, name in WATCHED:
        if lo <= value <= hi:
            return name
    return ""


def writes(hw: int, reg: int) -> bool:
    """True if this halfword CAN write `reg`. Deliberately over-broad: a false yes only drops a
    candidate, and main() prints every drop, so an over-broad rule can never hide a site."""
    d3, d8 = hw & 7, (hw >> 8) & 7
    if hw & 0xF800 in (0x2000, 0x3000, 0x3800):             # mov / add / sub rd,#imm8
        return d8 == reg
    if hw & 0xF800 == 0x2800:                               # cmp rd,#imm8 writes nothing
        return False
    if hw & 0xE000 == 0x0000:                               # lsl / lsr / asr / add / sub rd,...
        return d3 == reg
    if hw & 0xFFC0 in (0x4200, 0x4280, 0x42C0):             # tst / cmp / cmn rd,rs: no write
        return False
    if hw & 0xFF00 == 0x4500:                               # cmp rd,hs: no write
        return False
    if hw & 0xFC00 == 0x4000:                               # ALU rd,rs
        return d3 == reg
    if hw & 0xFC00 == 0x4400:                               # add / mov rd,hs (high register forms)
        return (d3 | ((hw >> 4) & 8)) == reg
    if hw & 0xFF80 == 0x4700:                               # bx: the callee owns r0-r3
        return reg < 4
    if hw & 0xF800 == 0x4800:                               # ldr rd,[pc,#imm]
        return d8 == reg
    if hw & 0xF000 in (0x5000, 0x6000, 0x7000, 0x8000):     # the ldr / str forms
        return bool(hw & 0x0800) and d3 == reg
    if hw & 0xF000 == 0x9000:                               # ldr / str rd,[sp,#imm]
        return bool(hw & 0x0800) and d8 == reg
    if hw & 0xF000 == 0xA000:                               # add rd,pc/sp,#imm
        return d8 == reg
    if hw & 0xFE00 == 0xBC00:                               # pop
        return bool(hw & (1 << reg))
    if hw & 0xF800 == 0xC800:                               # ldmia rb!,{...}
        return bool(hw & (1 << reg)) or d8 == reg
    if hw & 0xF800 in (0xF000, 0xF800):                     # bl: the callee owns r0-r3
        return reg < 4
    return False


def main() -> int:
    rom = Path(sys.argv[1]).read_bytes()
    lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else len(rom)
    hw = struct.unpack_from(f"<{len(rom) // 2}H", rom, 0)
    hits, drops = [], []
    for i in range(lo // 2, min(hi // 2, len(hw) - 1)):
        a = hw[i]
        if a & 0xF800 != 0x2000:                            # MOV rd,#imm8
            continue
        src, imm = (a >> 8) & 7, a & 0xFF
        for g in range(1, WINDOW + 1):
            if i + g >= len(hw):
                break
            b = hw[i + g]
            sh = (b >> 6) & 0x1F
            if b & 0xF800 == 0x0000 and ((b >> 3) & 7) == src and sh:
                name = watched(imm << sh)
                row = (i * 2, (i + g) * 2, g, imm << sh, src, b & 7, imm, sh, name)
                (hits if name else drops).append(row)
                break
            if writes(b, src):
                # EVERY shift, 1 to 31. An earlier version tested 1 to 3 only, which made a dropped
                # `mov rX,#0xd` before an `lsl #7` silent: that is the exact shape of the scouter
                # block sites, so the tool could have hidden the very sites it exists to find.
                reach = sorted({imm << s for s in range(1, 32) if watched(imm << s)})
                if reach:
                    drops.append((i * 2, (i + g) * 2, g, reach[0], src, -1, imm, 0,
                                  f"dropped: r{src} is rewritten by 0x{b:04x} before any lsl"
                                  f" (it could have reached {', '.join(hex(v) for v in reach)})"))
                break

    print(f"== mov ; lsl with a gap, rom:0x{lo:X} to rom:0x{hi:X}, window {WINDOW} halfwords ==")
    for mv, ls, g, v, src, dst, imm, sh, name in hits:
        tag = "ADJACENT" if g == 1 else f"GAP {g - 1}"
        into = "" if dst == src else f" INTO r{dst}"
        print(f"  mov rom:0x{mv:X}  lsl rom:0x{ls:X}  0x{v:<5X} {name:<44}"
              f" mov r{src},#0x{imm:x} ; lsl r{dst},r{src},#{sh}{into}   [{tag}]")
    print(f"\n{len(hits)} site(s) building a watched value.")
    print("== candidates DROPPED whose immediate could still have reached a watched value ==")
    for mv, _ls, _g, _v, src, _d, imm, _s, why in drops:
        if isinstance(why, str) and why.startswith("dropped"):
            print(f"  rom:0x{mv:X}  mov r{src},#0x{imm:x}  {why}")
    print("A value built by an add chain, a pool word or another register is not visible here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
