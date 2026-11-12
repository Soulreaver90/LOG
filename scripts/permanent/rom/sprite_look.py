r"""
sprite_look.py - Put any number of frames side by side, big, with the palette index in every cell.

Why:     the guide's primary instrument is LOOKING, and on 2026-11-02 I rebuilt this same renderer ten
         times in scratch to do it. Every art round needs the same picture: his approved frame, vanilla,
         and mine, at a zoom where a single pixel can be judged, with rulers so a coordinate can be named.
Usage:   py -3.14 -I scripts\permanent\rom\sprite_look.py <out.png> <frame.png> [<frame.png>...]
                  [--rows 12-26] [--zoom 34] [--plain] [--small] [--palette <png>] [--shift i,dy]
Flags:   --rows    the row band to show, inclusive. Default: the whole frame.
         --zoom    pixels per cell. Default 34, which is large enough to read a two digit index.
         --plain   no index text, so SHAPE reads instead of numbers. Run both; they answer different
                   questions, and the guide says to look at the picture before reading the grid.
         --small   append each frame at 3x and at game size under its column.
         --palette force one palette on every frame. A set's own embedded palette is often NOT the one
                   the game draws it with: set 104 renders Piccolo with red arms from its own.
         --shift   i,dy  push frame i down dy rows. THIS is the one that matters. A walk extreme can sit
                   a row below the stand, and comparing at offset 0 reports that they share nothing.
                   On 2026-11-02 that cost a round: at +1 the jaw and band rows differed by 2 px each.
API:     load(path) -> (bytes, w, h)      shift(data, w, h, dy) -> bytes
         look(frames, rows, zoom, indices, palette, small) -> PIL image
         frames is [(label, data, w, h)], already shifted.
Rules:   reads only. Frames may differ in size; the sheet uses the widest and tallest.
Source:  the method and the lessons behind it are in docs\sprite-guide.md.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# ===== CONFIG =====
BG = (104, 104, 112)          # mid tone: grey hides nothing, lime fights skin
ZOOM = 34
RULER = (170, 170, 185)
LABEL = (245, 245, 255)
PAPER = (24, 24, 30)
SMALL = (3, 1)


# ===== frames =====

def load(path: Path) -> tuple:
    with Image.open(path) as img:
        if img.mode != "P":
            raise ValueError(f"{path.name}: expected an indexed image, got {img.mode}")
        return img.tobytes(), img.width, img.height


def shift(data: bytes, w: int, h: int, dy: int) -> bytes:
    """Push a frame down dy rows, so a stand can be laid against a walk extreme that sits lower."""
    out = bytearray(w * h)
    for y in range(h):
        src = y - dy
        if 0 <= src < h:
            out[y * w:(y + 1) * w] = data[src * w:(src + 1) * w]
    return bytes(out)


def _rgb(data: bytes, w: int, h: int, pal: list) -> Image.Image:
    im = Image.frombytes("P", (w, h), data)
    im.putpalette(pal)
    out = im.convert("RGB")
    px = out.load()
    for y in range(h):
        for x in range(w):
            if not data[y * w + x]:
                px[x, y] = BG
    return out


# ===== sheet =====

def look(frames: list, rows: tuple = None, zoom: int = ZOOM, indices: bool = True,
         palette: list = None, small: bool = False) -> Image.Image:
    w = max(f[2] for f in frames)
    h = max(f[3] for f in frames)
    y0, y1 = rows if rows else (0, h - 1)
    band = y1 - y0 + 1
    gut, top = 30, 44
    cw = w * zoom + gut + 8
    tail = (h * sum(SMALL) + 20) if small else 0
    im = Image.new("RGB", (len(frames) * cw + 16, top + band * zoom + tail + 14), PAPER)
    d = ImageDraw.Draw(im)

    if not palette:
        raise ValueError("look() needs one palette for every frame: a set's own may not be the live one")
    pal = palette
    for i, (label, data, fw, fh) in enumerate(frames):
        ox = 8 + gut + i * cw
        for y in range(y0, y1 + 1):
            for x in range(w):
                v = data[y * fw + x] if (y < fh and x < fw) else 0
                c = BG if not v else tuple(pal[v * 3:v * 3 + 3])
                px, py = ox + x * zoom, top + (y - y0) * zoom
                d.rectangle([px, py, px + zoom - 1, py + zoom - 1], fill=c)
                if v and indices:
                    ink = (0, 0, 0) if sum(c) > 330 else (245, 245, 245)
                    d.text((px + zoom // 4, py + zoom // 3), f"{v:02X}", ink)
            d.text((ox - gut + 2, top + (y - y0) * zoom + zoom // 3), f"{y:02d}", RULER)
        for x in range(0, w, 2):
            d.text((ox + x * zoom + zoom // 3, top - 16), f"{x}", RULER)
        d.text((ox, 10), label, LABEL)

        if small:
            sx, sy = ox, top + band * zoom + 12
            for s in SMALL:
                im.paste(_rgb(data, fw, fh, pal).resize((fw * s, fh * s), Image.NEAREST), (sx, sy))
                sx += fw * s + 10
    return im


# ===== cli =====

def _main(argv: list) -> int:
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    rows, zoom, indices, small, pal_src, shifts, paths = None, ZOOM, True, False, None, {}, []
    args = list(argv)
    out = Path(args.pop(0))
    while args:
        a = args.pop(0)
        if a == "--rows":
            lo, hi = args.pop(0).split("-")
            rows = (int(lo), int(hi))
        elif a == "--zoom":
            zoom = int(args.pop(0))
        elif a == "--plain":
            indices = False
        elif a == "--small":
            small = True
        elif a == "--palette":
            pal_src = Path(args.pop(0))
        elif a == "--shift":
            i, dy = args.pop(0).split(",")
            shifts[int(i)] = int(dy)
        else:
            paths.append(Path(a))

    if not paths:
        print("no frames given")
        return 2
    with Image.open(pal_src if pal_src else paths[0]) as src:
        palette = src.getpalette()
    frames = []
    for i, p in enumerate(paths):
        data, w, h = load(p)
        dy = shifts.get(i, 0)
        label = p.stem if not dy else f"{p.stem}  {dy:+d} rows"
        frames.append((label, shift(data, w, h, dy) if dy else data, w, h))

    look(frames, rows, zoom, indices, palette, small).save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
