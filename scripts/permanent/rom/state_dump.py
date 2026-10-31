"""
state_dump.py - Extract GBA memory regions from an mGBA save state, and summarize sprites on screen.

Usage:   py -3 -I state_dump.py <state.ss1> <out_dir>
Writes:  io.bin, palette.bin, oam.bin, vram.bin, iwram.bin, wram.bin into out_dir.
Prints:  DISPCNT sprite mapping mode and every visible OAM entry (position, size, tile, palette, 4/8 bpp).
Layout:  mGBA 0.10.5 include/mgba/internal/gba/serialize.h (total state size 0x61000).
"""
import struct
import sys
import zlib
from pathlib import Path

STATE_SIZE = 0x61000
REGIONS = {  # name: (state offset, length)
    "io": (0x00400, 0x400),
    "palette": (0x00800, 0x400),
    "oam": (0x00C00, 0x400),
    "vram": (0x01000, 0x18000),
    "iwram": (0x19000, 0x8000),
    "wram": (0x21000, 0x40000),
}
# OAM shape/size to (width, height) in pixels.
OBJ_SIZES = {
    0: [(8, 8), (16, 16), (32, 32), (64, 64)],
    1: [(16, 8), (32, 8), (32, 16), (64, 32)],
    2: [(8, 16), (8, 32), (16, 32), (32, 64)],
}


def load_state(path: Path) -> bytes:
    """Raw state from a PNG save state (zlib in the 'gbAs' chunk), a zlib blob, or a raw file."""
    data = path.read_bytes()
    if data.startswith(b"\x89PNG"):
        pos = 8
        while pos < len(data):
            length, ctype = struct.unpack_from(">I4s", data, pos)
            if ctype == b"gbAs":
                data = zlib.decompress(data[pos + 8:pos + 8 + length])
                break
            pos += 12 + length
    elif len(data) != STATE_SIZE:
        data = zlib.decompress(data)
    if len(data) < STATE_SIZE:
        sys.exit(f"Unexpected state size {len(data):#x}; expected {STATE_SIZE:#x}.")
    return data


def summarize_oam(io: bytes, oam: bytes) -> None:
    dispcnt = struct.unpack_from("<H", io, 0)[0]
    print(f"DISPCNT={dispcnt:#06x}  OBJ mapping={'1D' if dispcnt & 0x40 else '2D'}  OBJ on={bool(dispcnt & 0x1000)}")
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<3H", oam, i * 8)
        if (a0 >> 8) & 3 == 2:  # disabled
            continue
        shape, size = a0 >> 14, a1 >> 14
        if shape == 3:
            continue
        w, h = OBJ_SIZES[shape][size]
        y, x = a0 & 0xFF, a1 & 0x1FF
        bpp = 8 if a0 & 0x2000 else 4
        print(f"  obj{i:3d} x={x:3d} y={y:3d} {w}x{h} tile={a2 & 0x3FF:4d} pal={a2 >> 12:2d} {bpp}bpp prio={(a2 >> 10) & 3}")


if __name__ == "__main__":
    state = load_state(Path(sys.argv[1]))
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for name, (off, length) in REGIONS.items():
        (out / f"{name}.bin").write_bytes(state[off:off + length])
    summarize_oam(state[0x400:0x800], state[0xC00:0x1000])
