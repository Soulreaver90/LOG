r"""
map_view.py - Render a map (BG layers, collision, items, warps) to a PNG, with optional planned actor spots.

Usage:   py -3.14 -P scripts\permanent\scene\map_view.py --map 8,1 --out <path>.png
         py -3.14 -P scripts\permanent\scene\map_view.py --map 9,1 --var 1 --layers ground --out ground.png
         py -3.14 -P scripts\permanent\scene\map_view.py --map 9,1 --actor 312,400,Piccolo --actor 344,400,Gohan \
             --out plan.png
         --layers full (default), ground (BG2+BG3), over (BG0+BG1). --no-collision leaves the red tint off.
         --no-items leaves the warp and scene boxes off. --rom <path> reads a build instead of the base ROM.
Output:  the PNG you name, and a short report on stdout. The tool never writes to the ROM.
Reads:   map table rom:0x409368 (327 entries of 56 bytes), entry +0x2C layout per variation, layout +0x14 to
         +0x20 the four BG layer records, +0x34 the collision frame, +0x48 and +0x4C the tile stream and
         table. Collision is 1 bit an 8x8 cell, set = open (collision_test @0x08005D6C). BG0 and BG1 carry
         priority 1 and draw over the actors; BG2 and BG3 carry 3. All CONFIRMED (bible CSV, BMG rows).
Method:  the geometry is copied from the card 4 scripts (scripts\one-time\2026-10-24-beam-struggle
         render_map.py and the 2026-10-25-chapter-cards presave_lib.py), not imported: a one-time folder is
         not a dependency a permanent tool may take.
Needs:   Pillow (py -3.14 has it; py -3 does not).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from PIL import Image                                         # noqa: E402

from scene import scene_probe                                            # noqa: E402
from rom.webfoot_decompress import unpack_frame                   # noqa: E402

# ===== CONFIG =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
ROM_BASE, BG_PAL = 0x08000000, 0x1DA4C8
MAP_TABLE, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56
LAYER_OFFSETS = (0x14, 0x18, 0x1C, 0x20)        # BG0, BG1, BG2, BG3
LAYER_VTABLE = 0x080056A1                       # a layer record whose first word is this one draws
GROUND, OVER, FULL = (3, 2), (1, 0), (3, 2, 1, 0)
COLLISION_TINT, COLLISION_ALPHA = (255, 0, 0), 110
WARP_BOX, SCENE_BOX, ACTOR_DOT = (0, 160, 255), (255, 200, 0), (0, 255, 120)
ACTOR_R = 4


# ===== ROM reads =====

def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def _at(rom: bytes, address: int) -> int:
    return u32(rom, address - ROM_BASE)


def frame(rom: bytes, address: int) -> bytes:
    return unpack_frame(rom, address - ROM_BASE)[2]


def palette(rom: bytes) -> list:
    out = []
    for c in struct.unpack_from("<256H", rom, BG_PAL):
        out += [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
    return out


def layout_of(rom: bytes, entry: int, var: int = 1) -> int:
    """The layout address of one variation (1-based): entry +0x2C is an array of layout pointers."""
    return _at(rom, u32(rom, entry + 0x2C) + 4 * (var - 1))


def tiles(rom: bytes, layout: int) -> list:
    """The 8x8 tile pixels of this layout, in index order. The index stream is delta coded."""
    stream = frame(rom, _at(rom, layout + 0x48))
    idx = list(struct.unpack(f"<{len(stream) // 2}H", stream))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = _at(rom, layout + 0x4C), {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = frame(rom, _at(rom, table + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def mask_of(img: Image.Image) -> Image.Image:
    """An L mask from the palette INDEX (0 = transparent). Image.point would go through the palette."""
    return Image.frombytes("L", img.size, bytes(255 if v else 0 for v in img.tobytes()))


def layer(rom: bytes, rec: int, tl: list, pal: list) -> tuple:
    """(image, (w, h, blocks x, blocks y)) for one BG layer record."""
    w, h = _at(rom, rec + 4), _at(rom, rec + 8)
    bx, by = rom[rec - ROM_BASE + 0x14], rom[rec - ROM_BASE + 0x15]
    img = Image.new("P", (bx * 256, by * 256), 0)
    img.putpalette(pal)
    for k in range(bx * by):
        p = _at(rom, rec + 0x18 + 4 * k)
        if not p:
            continue
        m = frame(rom, p)
        ox, oy = (k % bx) * 256, (k // bx) * 256
        for t in range(1024):
            e = struct.unpack_from("<H", m, 2 * t)[0]
            n = e & 0x3FF
            if n >= len(tl):
                continue
            px = tl[n]
            if not any(px):
                continue
            tile = Image.frombytes("P", (8, 8), bytes(px))
            if e & 0x400:
                tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
            if e & 0x800:
                tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
            img.paste(tile, (ox + (t % 32) * 8, oy + (t // 32) * 8))
    return img, (w, h, bx, by)


def layers(rom: bytes, layout: int) -> tuple:
    pal, tl, out = palette(rom), tiles(rom, layout), {}
    for n, off in enumerate(LAYER_OFFSETS):
        rec = _at(rom, layout + off)
        drawn = rec >> 24 == 0x08 and _at(rom, rec) == LAYER_VTABLE
        out[n] = layer(rom, rec, tl, pal) if drawn else None
    return out, pal


def collision(rom: bytes, layout: int) -> bytes:
    return frame(rom, _at(rom, layout + 0x34))


def is_open(bits: bytes, x: int, y: int) -> bool:
    """collision_test @0x08005D6C: byte cy x 32 + (cx >> 3), bit cx & 7, set = open, 8 px cells."""
    cx, cy = x >> 3, y >> 3
    return 0 <= cx < 256 and 0 <= cy < 256 and bool(bits[cy * 32 + (cx >> 3)] >> (cx & 7) & 1)


# ===== render =====

def compose(ls: dict, which: tuple, size: tuple) -> Image.Image:
    img = Image.new("RGB", size, (0, 0, 0))
    for n in which:                                       # back to front
        if ls[n] is None:
            continue
        pane = ls[n][0]
        img.paste(pane.convert("RGB"), (0, 0), mask_of(pane))
    return img


def _box(img: Image.Image, rect: tuple, colour: tuple) -> None:
    """A 1 px outline, clipped to the image."""
    x0, y0, x1, y1 = rect
    w, h = img.size
    for x in range(max(x0, 0), min(x1, w - 1) + 1):
        for y in (y0, y1):
            if 0 <= y < h:
                img.putpixel((x, y), colour)
    for y in range(max(y0, 0), min(y1, h - 1) + 1):
        for x in (x0, x1):
            if 0 <= x < w:
                img.putpixel((x, y), colour)


def render(rom: bytes, zone: int, area: int, var: int = 1, which: tuple = FULL,
           show_collision: bool = True, show_items: bool = True, actors: list = None) -> tuple:
    """(image, report lines). actors is [(x, y, label)] in map pixels."""
    _, entry = scene_probe.map_entry(rom, zone, area)
    layout = layout_of(rom, entry, var)
    ls, _pal = layers(rom, layout)
    live = [v for v in ls.values() if v]
    if not live:
        raise ValueError(f"map {zone},{area} var {var}: no BG layer draws anything")
    size = (max(v[0].size[0] for v in live), max(v[0].size[1] for v in live))
    w, h = (ls[2][1][0], ls[2][1][1]) if ls[2] else size
    img = compose(ls, which, size)
    lines = [f"map {zone},{area} var {var}  entry rom:0x{entry:X}  layout 0x{layout:08X}  map {w}x{h}"]
    for n, v in ls.items():
        lines.append(f"  bg{n}: " + ("none" if v is None else f"{v[1][0]}x{v[1][1]} blocks {v[1][2]}x{v[1][3]}"))
    if show_collision:
        bits = collision(rom, layout)
        tint, mask = Image.new("RGB", (8, 8), COLLISION_TINT), Image.new("L", (8, 8), COLLISION_ALPHA)
        closed = 0
        for cy in range(h // 8):
            for cx in range(w // 8):
                if not is_open(bits, cx * 8, cy * 8):
                    img.paste(tint, (cx * 8, cy * 8), mask)
                    closed += 1
        lines.append(f"  collision: {closed} closed cells of {(w // 8) * (h // 8)} (red tint)")
    if show_items:
        info = scene_probe.map_items(rom, zone, area)
        for cond, it in info["regions"]:
            colour = WARP_BOX if it["kind"] == "warp" else SCENE_BOX
            _box(img, it["rect"], colour)
            lines.append(f"  region cond 0x{cond:08X} {it['kind']} rect {it['rect']}"
                         + (f" -> map {it['to'][0]},{it['to'][1]} at {it['landing']}"
                            if it["kind"] == "warp" else
                            f" -> table rom:0x{it['table']:X}" if it["kind"] == "scene" else ""))
        for it in info["items"]:
            if it["kind"] in ("warp", "scene", "script"):
                _box(img, it["rect"], WARP_BOX if it["kind"] == "warp" else SCENE_BOX)
            if it["kind"] == "group" and "table" in it:
                lines.append(f"  group item rom:0x{it['at']:X} -> table rom:0x{it['table']:X}")
    for x, y, label in actors or []:
        for dx in range(-ACTOR_R, ACTOR_R + 1):
            for dy in range(-ACTOR_R, ACTOR_R + 1):
                if dx * dx + dy * dy <= ACTOR_R * ACTOR_R and 0 <= x + dx < img.size[0] and 0 <= y + dy < img.size[1]:
                    img.putpixel((x + dx, y + dy), ACTOR_DOT)
        lines.append(f"  actor {label} at ({x}, {y}): "
                     + ("standing on an open cell" if is_open(collision(rom, layout), x, y)
                        else "standing on a CLOSED cell"))
    return img.crop((0, 0, w, h)), lines


# ===== CLI =====

def _main(argv: list) -> None:
    rom_path, spec, var, out = BASE, None, 1, None
    which, show_collision, show_items, actors = FULL, True, True, []
    while argv:
        a = argv.pop(0)
        if a == "--rom":
            rom_path = Path(argv.pop(0))
        elif a == "--map":
            spec = argv.pop(0)
        elif a == "--var":
            var = int(argv.pop(0), 0)
        elif a == "--out":
            out = Path(argv.pop(0))
        elif a == "--layers":
            which = {"full": FULL, "ground": GROUND, "over": OVER}[argv.pop(0)]
        elif a == "--no-collision":
            show_collision = False
        elif a == "--no-items":
            show_items = False
        elif a == "--actor":
            x, y, label = (argv.pop(0) + ",?").split(",")[:3]
            actors.append((int(x), int(y), label))
        else:
            raise SystemExit(f"unknown argument {a}\n{__doc__}")
    if not spec or not out:
        raise SystemExit(__doc__)
    zone, area = (int(v) for v in spec.split(","))
    rom = rom_path.read_bytes()
    img, lines = render(rom, zone, area, var, which, show_collision, show_items, actors)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("\n".join(lines))
    print(f"wrote {out} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    _main(sys.argv[1:])
