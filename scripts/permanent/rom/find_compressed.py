"""
find_compressed.py - Find GBA BIOS-compressed blocks (LZ77 type 0x10, RLE type 0x30) that contain a probe.

Usage:   py -3 -I find_compressed.py <rom.gba> <probe.bin> [--all]
Prints:  every 4-byte aligned block that decompresses cleanly and contains the probe bytes.
         --all lists every clean block instead (offset, packed and unpacked size).
Why:     sprite tiles are not stored raw in LoG II; this tells us if the BIOS formats are used.
Read-only. Invalid back-references abort a candidate early, so random data is cheap to reject.
"""
import sys
from pathlib import Path

MAX_SIZE = 0x40000  # largest unpacked block worth considering (256 KB)


def lz77(rom: bytes, off: int):
    size = int.from_bytes(rom[off + 1:off + 4], "little")
    if not 32 <= size <= MAX_SIZE:
        return None
    out, src = bytearray(), off + 4
    while len(out) < size:
        if src >= len(rom):
            return None
        flags = rom[src]; src += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = rom[src], rom[src + 1]; src += 2
                count, disp = (b1 >> 4) + 3, ((b1 & 0xF) << 8 | b2) + 1
                if disp > len(out):
                    return None
                for _ in range(count):
                    out.append(out[-disp])
            else:
                out.append(rom[src]); src += 1
    return bytes(out[:size]), src - off


def rle(rom: bytes, off: int):
    size = int.from_bytes(rom[off + 1:off + 4], "little")
    if not 32 <= size <= MAX_SIZE:
        return None
    out, src = bytearray(), off + 4
    while len(out) < size:
        if src >= len(rom):
            return None
        flag = rom[src]; src += 1
        if flag & 0x80:
            out += bytes([rom[src]]) * ((flag & 0x7F) + 3); src += 1
        else:
            out += rom[src:src + (flag & 0x7F) + 1]; src += (flag & 0x7F) + 1
    return bytes(out[:size]), src - off


if __name__ == "__main__":
    rom = Path(sys.argv[1]).read_bytes()
    probe = Path(sys.argv[2]).read_bytes() if sys.argv[2] != "-" else b""
    list_all = "--all" in sys.argv
    found = 0
    for off in range(0, len(rom) - 4, 4):
        kind = rom[off]
        decoder = lz77 if kind == 0x10 else rle if kind == 0x30 else None
        if not decoder:
            continue
        result = decoder(rom, off)
        if not result:
            continue
        data, packed = result
        if list_all or (probe and probe in data):
            found += 1
            where = data.find(probe) if probe else -1
            print(f"0x{off:06X} type={kind:#04x} packed={packed} unpacked={len(data)} probe_at={where}")
    print(f"{found} block(s)")
