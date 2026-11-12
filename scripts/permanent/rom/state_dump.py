r"""
state_dump.py - Extract GBA memory regions from an mGBA save state, and say what is on screen and in the world.

Usage:   py -3.14 -P state_dump.py <state.ss1> <out_dir>
Writes:  io.bin, palette.bin, oam.bin, vram.bin, iwram.bin, wram.bin into out_dir.
Prints:  the current map, every ACTOR SPOT found in the world, then DISPCNT and every visible OAM entry.
Layout:  mGBA 0.10.5 include/mgba/internal/gba/serialize.h (total state size 0x61000).
Reads:   the current map is the byte pair at 0x03002080, zone then area (bible WRP). An actor's spot is
         {u32 x << 8, u32 y << 8} at obj+0x158, so the object base is the hit minus 0x158 (bible CAP, ARN4).
Why the scan: walking the world object lists at 0x03001120 misses the actors a SCENE owns, and obj+0x48 is
         a set POINTER, not a set id, so reading it as an id prints nonsense (bible row 105). Scanning for
         the anchor shape finds every actor whatever owns it.
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
WRAM_BASE, IWRAM_BASE = 0x02000000, 0x03000000
CURRENT_MAP = 0x03002080                     # zone, then area
ANCHOR = 0x158                               # obj+0x158 x, obj+0x15C y, both 8.8 fixed point
MAP_MAX = 2048                               # the engine's largest map, so the widest sane spot

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


def current_map(iwram: bytes) -> tuple:
    """(zone, area) of the map the game thinks it is on."""
    o = CURRENT_MAP - IWRAM_BASE
    return (iwram[o], iwram[o + 1]) if o + 1 < len(iwram) else (None, None)


def find_actors(buf: bytes, base: int, limit: int = MAP_MAX) -> list:
    """Every {object, x, y} whose anchor pair looks like a spot on a map.

    An anchor is two 8.8 words, so both are multiples of 256, and a real spot is inside the map. Those two
    tests alone cut 0x40000 bytes of WRAM to a handful of candidates. A (2,2) or (4,4) hit is a counter
    pair that happens to fit, so the caller sees the spot and judges it.
    """
    out = []
    for o in range(0, len(buf) - 8, 4):
        x, y = struct.unpack_from("<II", buf, o)
        if x and y and not (x & 0xFF) and not (y & 0xFF) and x >> 8 < limit and y >> 8 < limit:
            out.append({"object": base + o - ANCHOR, "anchor": base + o, "x": x >> 8, "y": y >> 8})
    return out


def summarize_actors(iwram: bytes, wram: bytes) -> None:
    zone, area = current_map(iwram)
    print(f"current map {zone},{area}   (byte pair at {CURRENT_MAP:#010x})")
    for name, buf, base in (("wram", wram, WRAM_BASE), ("iwram", iwram, IWRAM_BASE)):
        hits = find_actors(buf, base)
        print(f"  {name}: {len(hits)} anchor shaped pairs")
        for a in hits[:24]:
            print(f"    object {a['object']:#010x}  spot ({a['x']:>5},{a['y']:>5})")
        if len(hits) > 24:
            print(f"    ... {len(hits) - 24} more, mostly counter pairs in the low numbers")


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
    iwram = state[REGIONS["iwram"][0]:REGIONS["iwram"][0] + REGIONS["iwram"][1]]
    wram = state[REGIONS["wram"][0]:REGIONS["wram"][0] + REGIONS["wram"][1]]
    summarize_actors(iwram, wram)
    print()
    summarize_oam(state[0x400:0x800], state[0xC00:0x1000])
