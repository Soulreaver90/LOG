"""
find_palettes.py - Find 16-color GBA palettes in a ROM that match the colors of a ripped sprite sheet.

Usage:   py -3 -I find_palettes.py <rom.gba> <sheet.png> [min_hits]
Prints:  ROM offsets of 32-byte aligned palettes where at least min_hits (default 10) of 16 colors
         occur in the sheet, best matches first. Read-only.
Why:     palettes are usually stored uncompressed, so they anchor the search for the sprite tables.
"""
import struct
import sys
from pathlib import Path

from PIL import Image

# Ripper background and cell colors; not part of any sprite palette.
SHEET_BACKGROUND = {(42, 150, 108), (52, 188, 136), (71, 255, 187), (35, 127, 90)}


def sheet_colors(png: Path) -> set[int]:
    """Sheet RGB888 colors as GBA BGR555 values (rippers expand 5-bit as v<<3 | v>>2)."""
    colors = set(Image.open(png).convert("RGB").getdata()) - SHEET_BACKGROUND
    return {(r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10) for r, g, b in colors}


def scan(rom: bytes, wanted: set[int], min_hits: int):
    for off in range(0, len(rom) - 32, 32):
        entries = struct.unpack_from("<16H", rom, off)
        if any(e & 0x8000 for e in entries):  # bit 15 is unused in real palettes
            continue
        hits = len({e for e in entries[1:]} & wanted)  # entry 0 is transparent
        if hits >= min_hits:
            yield off, hits


if __name__ == "__main__":
    rom_path, png_path = Path(sys.argv[1]), Path(sys.argv[2])
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    wanted = sheet_colors(png_path)
    print(f"{png_path.name}: {len(wanted)} sprite colors")
    for off, hits in sorted(scan(rom_path.read_bytes(), wanted, threshold), key=lambda t: -t[1])[:15]:
        print(f"  0x{off:06X} (ROM 0x{0x08000000 + off:08X})  {hits}/15 colors")
