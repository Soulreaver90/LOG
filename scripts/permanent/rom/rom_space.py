r"""
rom_space.py - Find free ROM space and hand it out without overlap.

Usage:   py -3 -I rom_space.py <rom.gba> [min_len_hex]
Prints:  every free run (offset, length) and the total. Never writes to the ROM.
API:     find_free(rom, min_len=0x1000) -> [(offset, length)]
         Allocator(rom_len, regions): alloc(size, align=4) -> file offset, used(), notes
Rules:   a free run is one fill byte (0xFF or 0x00), starts 4-aligned, and no 4-aligned
         ROM word (little-endian u32) equals an address inside it (0x08000000 + offset).
"""
import re
import sys
from bisect import bisect_left
from pathlib import Path

# ===== constants =====
ROM_BASE = 0x08000000
FILL_BYTES = (b"\xFF", b"\x00")


def _rom_pointers(rom: bytes) -> list:
    """Sorted file offsets that some 4-aligned ROM word points at."""
    words = memoryview(rom[: len(rom) & ~3]).cast("I")  # host is little-endian
    limit = ROM_BASE + len(rom)
    return sorted({w - ROM_BASE for w in words if ROM_BASE <= w < limit})


def find_free(rom: bytes, min_len: int = 0x1000) -> list:
    pointers = _rom_pointers(rom)
    runs = []
    for fill in FILL_BYTES:
        for m in re.finditer(re.escape(fill) + b"{%d,}" % min_len, rom):
            start = (m.start() + 3) & ~3
            length = m.end() - start
            if length < min_len:
                continue
            i = bisect_left(pointers, start)
            if i < len(pointers) and pointers[i] < start + length:
                continue
            runs.append((start, length))
    return sorted(runs)


class Allocator:
    """Bump allocator over free regions. `notes` carries data between patches."""

    def __init__(self, rom_len: int, regions: list):
        self.rom_len = rom_len
        self._regions = [(o, n) for o, n in sorted(regions) if o + n <= rom_len]
        self._cursor = [o for o, _ in self._regions]
        self._used = []
        self.notes = {}

    def alloc(self, size: int, align: int = 4) -> int:
        for idx, (start, length) in enumerate(self._regions):
            at = -(-self._cursor[idx] // align) * align
            if at + size <= start + length:
                self._cursor[idx] = at + size
                self._used.append((at, size))
                return at
        raise MemoryError(f"no free region holds 0x{size:X} bytes")

    def used(self) -> list:
        return list(self._used)


if __name__ == "__main__":
    data = Path(sys.argv[1]).read_bytes()
    found = find_free(data, int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x1000)
    for off, n in found:
        print(f"rom:0x{off:06X} len 0x{n:X} @0x{ROM_BASE + off:08X}")
    print(f"total 0x{sum(n for _, n in found):X} in {len(found)} runs")
