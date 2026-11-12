r"""
show_regions.py - Draw a hand written region map back over its frames, so I can look at my own reading.

Why:     the guide's method is to name every region by eye and write it down one letter per pixel, THEN
         place the joints. A colour rule cannot do it: the eye white is also a hair highlight, the iris
         blue is also the jacket, the belt orange is also the scabbard. This tool makes the picture big
         enough to judge and proves the transcription, nothing more.
Usage:   py -3.14 -P scripts\permanent\rom\show_regions.py <regions.txt> [<key> ...] [--zoom 26]
                  [--out <png>] [--palette <png>]
Size:    taken from the frames themselves, so 16x32 and 32x32 both work. Every frame in one regions
         file must share one size, because the sheet uses one panel size; a mismatch is reported.
Format:  the regions file carries its own frame list.
           #png <key> <path to the indexed png>      one per frame, path relative to the regions file
           #palette <path>                           optional, else the first frame's own palette
           #bone <key> <limb> <joint>,<joint>,...    optional, each joint "x,y" in pixels; draws a 4th
                                                     panel with the limb chained over the sprite
           [<key>]                                   then one line per pixel row, one character
                                                     per pixel column, both from the frame
         "." is a dead pixel. Any other character names a part. Unknown letters are reported, not drawn.
Prints:  per frame: lit pixels with no letter, dead pixels with a letter, and any unknown letter.
         That is a TRANSCRIPTION check. It cannot tell me an arm is really a scabbard. Only looking does.
Panels:  the sprite, what I named it, and body against gear, which is where a wrong call shows.
Rules:   reads only, except the one output png.
Source:  docs\sprite-guide.md, "Name every region by eye, THEN place the joints".
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# ===== CONFIG =====
ZOOM = 26
PAPER = (18, 18, 24)
DEAD = (26, 26, 34)

TINT = {"H": (190, 70, 230), "F": (245, 200, 130), "E": (70, 120, 255), "J": (150, 100, 60),
        "N": (200, 150, 95), "C": (255, 235, 170), "T": (60, 60, 75), "B": (245, 215, 70),
        "P": (150, 150, 165), "K": (45, 45, 55), "G": (250, 185, 60), "X": (90, 200, 255),
        "A": (90, 220, 120), "D": (40, 255, 180), "O": (120, 85, 55),
        "L": (40, 190, 90), "l": (120, 255, 150),
        "R": (235, 90, 60), "r": (255, 170, 120),
        "a": (235, 140, 55), "d": (255, 205, 120), "o": (185, 130, 80),
        "S": (235, 235, 245)}
GEAR = set("STXBGKLR")          # worn, not body: the third panel asks whether this call is right


# ===== regions file =====

def load(path: Path) -> tuple:
    png, pal, maps, bones, key = {}, None, {}, {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("#png "):
            k, rel = s[5:].split(None, 1)
            png[k] = (path.parent / rel).resolve()
        elif s.startswith("#bone "):
            k, limb, pts = s[6:].split(None, 2)
            xy = [tuple(float(v) for v in j.split(",")) for j in pts.split()]
            bones.setdefault(k, []).append((limb, xy))
        elif s.startswith("#palette "):
            pal = (path.parent / s[9:].strip()).resolve()
        elif s.startswith("#") or not s:
            continue
        elif s.startswith("["):
            key = s.strip("[]").strip()
            maps[key] = []
        elif key is not None:
            maps[key].append(line)
    if not png:
        raise ValueError(f"{path.name}: no #png line, so the frame size is unknown")
    sizes = {}
    for k, p in png.items():
        with Image.open(p) as im:
            sizes[k] = im.size
    w, h = sizes[next(iter(png))]
    odd = {k: s for k, s in sizes.items() if s != (w, h)}
    if odd:
        raise ValueError(f"{path.name}: every frame must be {w}x{h}, these are not: {odd}")
    maps = {k: [line.ljust(w)[:w] for line in v] for k, v in maps.items()}
    short = {k: len(v) for k, v in maps.items() if len(v) != h}
    if short:
        raise ValueError(f"{path.name}: these maps are not {h} lines: {short}")
    return png, pal, maps, bones, w, h


def check(name: str, grid: list, data: bytes, w: int, h: int) -> int:
    missing = [(x, y) for y in range(h) for x in range(w) if data[y * w + x] and grid[y][x] == "."]
    extra = [(x, y) for y in range(h) for x in range(w) if not data[y * w + x] and grid[y][x] != "."]
    bad = sorted({grid[y][x] for y in range(h) for x in range(w)} - set(TINT) - {"."})
    print(f"  {name}: unlabelled lit px {len(missing)}  labelled dead px {len(extra)}"
          + (f"  unknown letters {bad}" if bad else ""))
    for lab, pts in (("unlabelled", missing), ("labelled dead", extra)):
        if pts:
            print(f"    {lab}: {pts[:14]}")
    return len(missing) + len(extra) + len(bad)


# ===== drawing =====

def panel(d: ImageDraw.ImageDraw, grid: list, data: bytes, pal: list, ox: int, oy: int,
          mode: str, zoom: int, w: int, h: int) -> None:
    for y in range(h):
        for x in range(w):
            v, c = data[y * w + x], grid[y][x]
            if mode == "raw":
                col = DEAD if not v else tuple(pal[v * 3:v * 3 + 3])
            elif mode in ("named", "bones"):
                col = TINT.get(c, DEAD) if c != "." else DEAD
                if mode == "bones" and c != ".":
                    col = tuple(int(v * 0.42 + 26) for v in col)
            else:
                col = DEAD if c == "." else ((235, 70, 70) if c in GEAR else (90, 200, 235))
            d.rectangle([ox + x * zoom, oy + y * zoom,
                         ox + x * zoom + zoom - 1, oy + y * zoom + zoom - 1], fill=col)
            if mode == "named" and c != ".":
                lum = sum(col)
                d.text((ox + x * zoom + zoom // 3, oy + y * zoom + zoom // 4), c,
                       (0, 0, 0) if lum > 400 else (255, 255, 255))


BONE = [(255, 70, 70), (70, 255, 170), (255, 220, 60), (120, 180, 255)]


def skeleton(d: ImageDraw.ImageDraw, limbs: list, ox: int, oy: int, zoom: int) -> None:
    """Chain each limb's joints over the sprite, so a wandering joint shows as a kinked bone."""
    def at(p):
        return ox + (p[0] + 0.5) * zoom, oy + (p[1] + 0.5) * zoom
    for i, (limb, pts) in enumerate(limbs):
        col = BONE[i % len(BONE)]
        for a, b in zip(pts, pts[1:]):
            d.line([at(a), at(b)], fill=col, width=max(2, zoom // 8))
        for j, p in enumerate(pts):
            x, y = at(p)
            r = zoom // 3 if j in (0, len(pts) - 1) else zoom // 4
            d.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(10, 10, 14))
        d.text(at(pts[-1]), limb, fill=(255, 255, 255))


def main(argv: list) -> int:
    if not argv:
        print(__doc__)
        return 2
    zoom = int(argv[argv.index("--zoom") + 1]) if "--zoom" in argv else ZOOM
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    pal_arg = Path(argv[argv.index("--palette") + 1]) if "--palette" in argv else None
    plain = [a for i, a in enumerate(argv)
             if not a.startswith("--") and not (i and argv[i - 1].startswith("--"))]
    src = Path(plain[0])
    png, pal_path, maps, bones, w, h = load(src)
    names = plain[1:] or list(maps)
    missing = [n for n in names if n not in maps or n not in png]
    if missing:
        print(f"  no map or no #png for: {missing}")
        return 2
    with Image.open(pal_arg or pal_path or png[names[0]]) as im:
        pal = im.getpalette()

    modes = [("the sprite", "raw"), ("what I named it", "named"), ("body vs GEAR", "split")]
    if bones:
        modes.append(("the limbs", "bones"))
    cw, ch = w * zoom + 22, h * zoom + 30
    im = Image.new("RGB", (len(names) * len(modes) * cw + 20, ch + 24), PAPER)
    d = ImageDraw.Draw(im)
    print("transcription coverage:")
    faults = 0
    for i, n in enumerate(names):
        with Image.open(png[n]) as frame_im:
            data = frame_im.tobytes()
        faults += check(n, maps[n], data, w, h)
        for j, (lab, mode) in enumerate(modes):
            ox = 10 + (i * len(modes) + j) * cw
            panel(d, maps[n], data, pal, ox, 30, mode, zoom, w, h)
            if mode == "bones":
                skeleton(d, bones.get(n, []), ox, 30, zoom)
            d.text((ox, 10), f"{n}  {lab}", (240, 240, 250))
    dest = out or src.with_suffix(".png")
    im.save(dest)
    print(f"wrote {dest}")
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
