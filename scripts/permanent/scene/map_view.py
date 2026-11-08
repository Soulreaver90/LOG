r"""
map_view.py - Render a map to a PNG: BG layers, collision, BOTH door carriers, props and actor spots.

Usage:   py -3.14 -P scripts\permanent\scene\map_view.py --map 8,1 --out <path>.png
         py -3.14 -P scripts\permanent\scene\map_view.py --map 9,1 --var 1 --layers ground --out ground.png
         py -3.14 -P scripts\permanent\scene\map_view.py --map 9,1 --actor 312,400,Piccolo --actor 344,400,Gohan \
             --out plan.png
         --layers full (default), ground (BG2+BG3), over (BG0+BG1). --no-collision leaves the red tint off.
         --no-items leaves the door, region and prop boxes off. --rom <path> reads a build.
Output:  the PNG you name, and a short report on stdout. The tool never writes to the ROM.
Reads:   every map structure through scene_probe, the section 9 reader, so one decoder serves both tools.
         scene_probe resolves the map table from the literal at rom:0xEBD8 and its count from rom:0xE0AE,
         so `--rom <a build>` reads THAT build's table and finds an appended map such as 6,100.
         Then entry +0x2C layout per variation, layout +0x14 to +0x20 the four BG layer records, +0x24
         and +0x28 the props, +0x34 the collision frame, +0x40 and +0x44 the door list, +0x48 and +0x4C
         the tile stream and table, +0x0C and +0x10 the ANIMATED tile groups. A group DMAs its tiles
         to its own VRAM slots, usually past the static stream, and the render draws each group's
         FIRST frame there. Drawing the stream alone left 509 false cells on one map alone.
         Collision is 1 bit an 8x8 cell, set = open (collision_test
         @0x08005D6C). BG0 and BG1 carry priority 1 and draw over the actors; BG2 and BG3 carry 3.
         All CONFIRMED (bible CSV, BMG, WRP, EFX rows).
Boxes:   BLUE a door from the LAYOUT door list, CYAN a door from the REGION list, YELLOW a scene or
         script region, MAGENTA a layout prop, GREEN an actor spot you named. A map carries doors in two
         places and this tool draws both, each in its own colour, so the two can never be confused.
Size:    a layer record's +4 and +8 are a SCROLL FACTOR, 0x400 = 1.0, NOT a width and height. The map
         bounds come from the block grid of the layers that scroll 1 to 1 (scene_probe.map_bounds).
Offset:  +0x0C and +0x10 are a scroll OFFSET, and the picture is in WORLD pixels, so each layer is
         drawn at minus its own (layer_shift). Map layers 0 to 3 usually carry 0x10000 x n, which is
         64 n px, on 364 of the 1294 vanilla tilemap layers. Collision, doors, regions, props and the
         actor spots are already in world pixels and do not move. Without this every picture this
         project made put BG1 64 px, BG2 128 px and BG3 192 px right and down of the game, which the
         owner saw as art that did not sit inside its own collision (maps 2,7, 3,11, 4,72).
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
# No map table constant lives here on purpose: scene_probe.map_entry resolves it from the ROM it is
# given, so a build whose table has moved reads its own. A copy of the base address would read a dead one.
TOOL_INDEX_NOTE = ("**It draws BOTH door carriers, each in its own colour**: blue a door from the LAYOUT "
                   "list (`+0x40`/`+0x44`), cyan a door from the REGION list (entry `+0x10`), yellow a "
                   "scene or script region, magenta a layout PROP (`+0x24`/`+0x28`). The map bounds come "
                   "from the block grid, never from the layer `+4`/`+8` scroll factor. It reads every "
                   "structure through `scene_probe`, and `--rom <a build>` finds an appended map.")
LAYER_OFFSETS = scene_probe.L_LAYERS                      # BG0, BG1, BG2, BG3
LAYER_VTABLE = scene_probe.LAYER_TILEMAP                  # a layer record whose first word is this one draws
GROUND, OVER, FULL = (3, 2), (1, 0), (3, 2, 1, 0)
COLLISION_TINT, COLLISION_ALPHA = (255, 0, 0), 110
LAYOUT_DOOR_BOX, REGION_DOOR_BOX = (0, 120, 255), (0, 240, 255)
SCENE_BOX, PROP_BOX, ACTOR_DOT = (255, 200, 0), (255, 0, 220), (0, 255, 120)
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
    """The layout ADDRESS of one variation (1-based). scene_probe.layouts walks the chain; this tool
    works in addresses, so it adds the base back. One walker, so two tools cannot read one build apart."""
    chain = scene_probe.layouts(rom, entry)
    if not chain or var > len(chain) or chain[var - 1] is None:
        raise ValueError(f"map entry rom:0x{entry:X} has no layout for variation {var}")
    return chain[var - 1] + ROM_BASE


def tiles(rom: bytes, layout: int) -> list:
    """Every VRAM tile slot this layout loads, indexed by the slot a BG cell names.

    The static +0x48 stream fills slots 0 upward and each animated group fills its own span, which
    usually sits past the stream. An unloaded slot in between is b"". The decode is
    scene_probe.loaded_tiles, the section 9 reader's own, so no second copy can read a map apart."""
    return scene_probe.loaded_tiles(rom, layout - ROM_BASE)


def mask_of(img: Image.Image) -> Image.Image:
    """An L mask from the palette INDEX (0 = transparent). Image.point would go through the palette."""
    return Image.frombytes("L", img.size, bytes(255 if v else 0 for v in img.tobytes()))


def layer_shift(offset: tuple) -> tuple:
    """The pixels a layer record's +0x0C and +0x10 move its art LEFT and UP, as the handler does it.

    The layer update `sub_080055A4` loads rec +0x0C at `0x080055B2` and adds it to the camera
    product at `0x080055B4`; the Y side loads rec +0x10 at `0x080055C4` and adds it at `0x080055C8`.
    Each sum is stored `asr #10` to REG_BGxHOFS at `0x08005610` and REG_BGxVOFS at `0x08005614`, and
    the screen-block DMA `sub_080054A4` indexes from the SAME two accumulators, so the shift does not
    cancel. Raising a scroll register moves the view right, so the art at grid (gx, gy) is shown at
    world (gx - x, gy - y). Bible B1082: layer pixel = world pixel + 64 n.
    ASR is signed, so this is. All 1294 vanilla tilemap layers store a whole multiple of 1024 and
    none is negative, and a build or a hand edit may store either."""
    return tuple(((v - (1 << 32) if v & 0x80000000 else v) >> 10) for v in offset)


def layer(rom: bytes, rec: int, tl: list, pal: list) -> tuple:
    """(image, (scroll x, scroll y, blocks x, blocks y, shift x, shift y)) for one BG layer record.

    +4 and +8 are a SCROLL FACTOR, 0x400 = 1.0 (bible tag BMS), not a width and height. +0x0C and
    +0x10 are a scroll OFFSET, and layer_shift turns them into the pixels compose moves the picture
    by. The picture is as big as the block grid, and the map bounds come from scene_probe.map_bounds."""
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
            if not any(px):            # an unloaded slot is b"", and an all-zero tile is transparent
                continue
            tile = Image.frombytes("P", (8, 8), bytes(px))
            if e & 0x400:
                tile = tile.transpose(Image.FLIP_LEFT_RIGHT)
            if e & 0x800:
                tile = tile.transpose(Image.FLIP_TOP_BOTTOM)
            img.paste(tile, (ox + (t % 32) * 8, oy + (t // 32) * 8))
    shift = layer_shift((_at(rom, rec + 0x0C), _at(rom, rec + 0x10)))
    return img, (w, h, bx, by, shift[0], shift[1])


def layers(rom: bytes, layout: int) -> tuple:
    pal, tl, out = palette(rom), tiles(rom, layout), {}
    for n, off in enumerate(LAYER_OFFSETS):
        rec = _at(rom, layout + off)
        drawn = rec >> 24 == 0x08 and _at(rom, rec) == LAYER_VTABLE
        out[n] = layer(rom, rec, tl, pal) if drawn else None
    return out, pal


def collision(rom: bytes, layout: int) -> bytes:
    """The collision bits of a layout ADDRESS, through the one decoder in scene_probe."""
    return scene_probe.collision_bits(rom, layout - ROM_BASE)[2]


is_open = scene_probe.is_open             # collision_test @0x08005D6C, the one model (bible tag CSV)


# ===== render =====

def compose(ls: dict, which: tuple, size: tuple) -> Image.Image:
    """The layers in world pixels, each moved by its own +0x0C and +0x10 (see layer_shift).

    A scroll-1.0 layer lands exactly where the game draws it. A PARALLAX layer (21 of 1294 vanilla
    tilemap layers scroll off 1.0) moves with the camera, so no single placement in a whole-map
    picture is right for it: this one is the camera-at-(0,0) placement, which is where the handler
    puts it on the first screenful and nowhere else."""
    img = Image.new("RGB", size, (0, 0, 0))
    for n in which:                                       # back to front
        if ls[n] is None:
            continue
        pane, info = ls[n][0], ls[n][1]
        img.paste(pane.convert("RGB"), (-info[4], -info[5]), mask_of(pane))
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
    # The map bounds are the block grid of the layers that scroll 1 to 1. A layer's +4 and +8 are a
    # SCROLL FACTOR (0x400 = 1.0), and reading them as a size cropped every map to 1024x1024: it cut
    # map 9,1's right edge off and padded map 6,1 with 512 px of black.
    bw, bh = scene_probe.map_bounds(rom, layout - ROM_BASE)
    w, h = bw or size[0], bh or size[1]       # 2 of 327 maps have no scroll-1.0 layer: fall back to the art
    img = compose(ls, which, size)
    lines = [f"map {zone},{area} var {var}  entry rom:0x{entry:X}  layout 0x{layout:08X}  map {w}x{h}"]
    for n, v in ls.items():
        lines.append(f"  bg{n}: " + ("not a tilemap layer" if v is None else
                                     f"blocks {v[1][2]}x{v[1][3]} = {v[1][2] * 256}x{v[1][3] * 256} px, "
                                     f"scroll 0x{v[1][0]:X}/0x{v[1][1]:X}, "
                                     f"offset {v[1][4]},{v[1][5]} px"
                                     + (", PARALLAX: drawn at camera 0,0"
                                        if (v[1][0], v[1][1]) != (scene_probe.SCROLL_ONE,) * 2 else "")))
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
        # DOOR CARRIER B first, because it holds 586 of the game's 655 doors and no tool drew it before.
        doors = scene_probe.layout_doors(rom, layout - ROM_BASE)
        lines.append(f"  LAYOUT door list (layout +0x40/+0x44): {len(doors['doors'])} door(s) of a "
                     f"declared {doors['count']} [blue]")
        for n, it in enumerate(doors["doors"]):
            _box(img, it["rect"], LAYOUT_DOOR_BOX)
            lines.append(f"    door {n} rom:0x{it['at']:X} rect {it['rect']} -> map "
                         f"{it['to'][0]},{it['to'][1]} var {it['to'][2]} at {it['landing']}")
        # DOOR CARRIER A. A region is not a door unless its factory says so, which is the label this
        # tool got wrong: every region box used to be called a warp.
        region_doors = sum(1 for _c, it in info["regions"] if it["kind"] == "warp")
        lines.append(f"  REGION list (entry +0x10): {len(info['regions'])} region(s), {region_doors} of "
                     f"them door(s) [cyan door, yellow other]")
        for n, (cond, it) in enumerate(info["regions"]):
            _box(img, it["rect"], REGION_DOOR_BOX if it["kind"] == "warp" else SCENE_BOX)
            lines.append(f"    region {n} cond 0x{cond:08X} {'DOOR' if it['kind'] == 'warp' else it['kind']}"
                         f" rect {it['rect']}"
                         + (f" -> map {it['to'][0]},{it['to'][1]} at {it['landing']}"
                            if it["kind"] == "warp" else
                            f" -> table rom:0x{it['table']:X}" if it["kind"] == "scene" else ""))
        for it in info["items"]:
            if it["kind"] in ("warp", "scene", "script"):
                _box(img, it["rect"], REGION_DOOR_BOX if it["kind"] == "warp" else SCENE_BOX)
            if it["kind"] == "group" and "table" in it:
                lines.append(f"  group item rom:0x{it['at']:X} -> table rom:0x{it['table']:X}")
        props = scene_probe.layout_props(rom, layout - ROM_BASE)
        lines.append(f"  layout props (layout +0x24/+0x28): {len(props)} [magenta]")
        for n, p in enumerate(props):
            _box(img, p["rect"], PROP_BOX)
            lines.append(f"    prop {n} rom:0x{p['at']:X} rect {p['rect']} tile 0x{p['tile']:X}")
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
