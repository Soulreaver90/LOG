# throwaway (golden fix r2): rough out an SSJ2 front head from hand-placed clump polygons, then dump it as a text
# grid for pixel-by-pixel hand edits. Only the rough silhouette and first shade pass come from here.
#   python -I rough.py <name>   writes rough_<name>.txt (rows 0-16 head over the golden body rows 17-31)
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
sys.path.insert(0, str(W.parent / "work"))
import gold

BASE = [r for r in (W.parent / "work" / "g_gi_ssj2_d0.txt").read_text().splitlines() if r]
HAIR = set("hYyoOLlWc")
# tone: (light, base, shade) per depth; back clumps sit one step darker
TONE = {"front": ("L", "Y", "o"), "mid": ("y", "Y", "o"), "back": ("Y", "o", "O")}

# face rows 11-14 (x9-21) redrawn: bare forehead, brows in h/i slanting down to the centre
FACE = {11: "e22222222222e", 12: "e22222222222e", 13: "e32h22222h23e", 14: "e322ii2ii223e"}


def clumps_A():
    """Tall fan (fnv): broad flames fanning up and out, widest in the upper third."""
    return [
        ("back", [(6, 11), (5, 6), (9, 3), (15, 1), (21, 3), (25, 6), (24, 11)]),         # scalp volume
        ("back", [(9, 7), (4.5, 1.5), (12, 4)]),
        ("back", [(18, 4), (25.5, 1.5), (22, 7)]),
        ("back", [(6, 10), (0.5, 8.5), (7, 6)]),
        ("back", [(24, 6), (30.5, 8.5), (25, 10)]),
        ("mid", [(5, 12), (1, 13.5), (4, 9), (8, 9)]),                                      # low side flares
        ("mid", [(23, 9), (27, 9), (30, 13.5), (26, 12)]),
        ("mid", [(6, 9), (1.5, 4), (7, 5), (10, 8)]),
        ("mid", [(21, 8), (24, 5), (29.5, 4), (25, 9)]),
        ("front", [(8, 10), (7, 4), (8.5, 0.5), (12, 5), (13, 9)]),
        ("front", [(18, 9), (19, 5), (22.5, 0.5), (24, 4), (23, 10)]),
        ("front", [(12, 9), (12.5, 3), (15.5, -0.5), (18, 3), (19, 9)]),
    ]


def rough(clumps):
    lab = Image.new("L", (32, 17), 0)
    d = ImageDraw.Draw(lab)
    for k, (_, shape) in enumerate(clumps, 1):
        if isinstance(shape, dict):                     # hand spans {row: (x0, x1)}
            for y, (x0, x1) in shape.items():
                d.line((x0, y, x1, y), fill=k)
        else:
            d.polygon(shape, fill=k)
    L = lab.load()
    rows = [list(r) for r in BASE]
    for y in range(15):
        rows[y] = ["." if c in HAIR else c for c in rows[y]]
    for y, s in FACE.items():
        rows[y][9:22] = list(s)
    depth = {k: ("back", "mid", "front").index(t) for k, (t, _) in enumerate(clumps, 1)}
    for y in range(17):
        for x in range(32):
            k = L[x, y]
            if not k:
                continue
            light, base, shade = TONE[clumps[k - 1][0]]
            at = lambda dx, dy: L[x + dx, y + dy] if 0 <= x + dx < 32 and 0 <= y + dy < 17 else 0
            nb = [at(-1, 0), at(1, 0), at(0, -1), at(0, 1)]
            if 0 in nb:
                rows[y][x] = "h"                                            # silhouette and hairline
            elif any(n != k and depth[n] > depth[k] for n in nb):
                rows[y][x] = "O"                                            # tucked under a nearer clump
            elif any(n != k and depth[n] == depth[k] and n > k for n in nb):
                rows[y][x] = "h"                                            # same depth: a real split line
            elif at(-1, 0) != k or at(-2, 0) != k:
                rows[y][x] = light
            elif at(1, 0) != k or at(2, 0) != k:
                rows[y][x] = shade
            else:
                rows[y][x] = base
    return ["".join(r) for r in rows]


def sp(y0, *spans):
    """Spans from row y0 down: sp(3, (5, 5), (5, 7)) -> {3: (5, 5), 4: (5, 7)}."""
    return {y0 + i: s for i, s in enumerate(spans)}


def clumps_A3():
    """Tall fan: seven flame tips, side flicks at the temples, fringe over the forehead."""
    return [
        ("back", sp(2, (12, 18), (10, 20), (8, 22), (7, 23), (6, 24), (6, 24), (6, 24), (7, 23), (7, 23))),
        ("back", sp(1, (10, 10), (9, 11), (9, 12), (8, 12), (8, 12), (8, 12))),
        ("back", sp(1, (20, 20), (19, 21), (18, 21), (18, 22), (18, 22), (18, 22))),
        ("back", sp(5, (2, 2), (2, 4), (2, 5), (3, 6), (3, 7))),
        ("back", sp(5, (29, 29), (27, 29), (26, 29), (25, 28), (24, 28))),
        ("mid", sp(9, (2, 7), (1, 8), (4, 8), (6, 8), (7, 8))),
        ("mid", sp(9, (24, 29), (23, 30), (22, 27), (22, 24), (22, 23))),
        ("front", sp(2, (6, 6), (5, 7), (5, 8), (5, 9), (5, 10), (6, 11), (6, 12))),
        ("front", sp(2, (25, 25), (24, 26), (23, 26), (22, 26), (21, 26), (20, 25), (19, 25))),
        ("front", sp(0, (15, 15), (14, 16), (14, 17), (13, 17), (13, 18), (13, 18), (13, 18), (13, 18), (13, 18))),
        ("front", sp(9, (7, 23), (8, 22), (8, 10), (8, 9))),
    ]


def clumps_A2():
    """Tall fan, hand spans: back scalp and back tips, mid side flares, three front flames, a fringe."""
    return [
        ("back", sp(3, (11, 19), (9, 21), (8, 22), (7, 23), (6, 24), (6, 24), (6, 24), (7, 23), (8, 22))),
        ("back", sp(1, (12, 12), (11, 13), (11, 13), (10, 13))),
        ("back", sp(1, (18, 18), (17, 19), (17, 19), (17, 20))),
        ("back", sp(3, (4, 4), (4, 6), (4, 7), (5, 8), (6, 8))),
        ("back", sp(3, (26, 26), (24, 26), (23, 26), (22, 25), (22, 24))),
        ("mid", sp(4, (2, 2), (2, 4), (3, 6), (3, 7), (4, 8), (5, 8))),
        ("mid", sp(4, (28, 28), (26, 28), (24, 27), (23, 27), (22, 26), (22, 25))),
        ("mid", sp(8, (0, 1), (1, 5), (2, 7), (4, 8), (6, 8))),
        ("mid", sp(8, (29, 30), (25, 29), (23, 28), (22, 26), (22, 24))),
        ("front", sp(1, (8, 8), (7, 9), (7, 10), (7, 11), (7, 11), (8, 12), (8, 12), (8, 12), (9, 12))),
        ("front", sp(1, (22, 22), (21, 23), (20, 23), (19, 24), (19, 24), (19, 23), (19, 23), (18, 22), (18, 22))),
        ("front", sp(0, (15, 15), (14, 16), (13, 17), (13, 17), (12, 18), (12, 18), (12, 18), (13, 18), (13, 18),
                     (13, 18), (14, 17))),
        ("front", sp(9, (8, 13), (8, 12), (8, 10), (8, 9))),
        ("front", sp(9, (17, 22), (18, 22), (20, 22), (21, 22))),
    ]


if __name__ == "__main__":
    name = sys.argv[1]
    out = rough(globals()[f"clumps_{name}"]())
    (W / f"rough_{name}.txt").write_bytes(("\n".join(out) + "\n").encode())
    gold.grid_view([str(W / f"rough_{name}.txt")], 14).save(W / f"rough_{name}.png")
