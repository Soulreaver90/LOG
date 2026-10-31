"""
rom_info.py - Read-only summary of GBA ROM files.

Usage:   py -3 -I rom_info.py <rom.gba> [<rom.gba> ...]
Prints:  header title, game code, maker, version, size, save type string(s), SHA-1, CRC32.
Never writes to the ROM.
"""
import hashlib
import sys
import zlib
from pathlib import Path

# ===== GBA header offsets =====
TITLE = slice(0xA0, 0xAC)
GAME_CODE = slice(0xAC, 0xB0)
MAKER = slice(0xB0, 0xB2)
VERSION = 0xBC

# Nintendo SDK save library tags; emulators detect save type from these.
SAVE_TAGS = [b"EEPROM_V", b"SRAM_V", b"SRAM_F_V", b"FLASH_V", b"FLASH512_V", b"FLASH1M_V"]


def describe(path: Path) -> None:
    data = path.read_bytes()
    tags = sorted({data[i:i + 12].split(b"\0")[0].decode("ascii", "replace")
                   for tag in SAVE_TAGS
                   for i in _find_all(data, tag)})
    print(f"== {path.name}")
    print(f"   title={data[TITLE].rstrip(b'\0').decode('ascii', 'replace')!r}"
          f" code={data[GAME_CODE].decode('ascii', 'replace')}"
          f" maker={data[MAKER].decode('ascii', 'replace')} version={data[VERSION]}")
    print(f"   size={len(data)} bytes ({len(data) // 1024 // 1024} MB)")
    print(f"   save tags={tags or 'none found'}")
    print(f"   sha1={hashlib.sha1(data).hexdigest()} crc32={zlib.crc32(data) & 0xFFFFFFFF:08x}")


def _find_all(data: bytes, needle: bytes):
    i = data.find(needle)
    while i != -1:
        yield i
        i = data.find(needle, i + 1)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        describe(Path(arg))
