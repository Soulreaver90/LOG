# throwaway (golden fix r2): paint a hair mass from hand-placed flame spans, as a first pass for hand edits.
# Rules: silhouette and hairline edge h; a flame's edge against a nearer flame is a split line (h near the tips,
# O lower down so the mass stays soft); inside a row run: light, base..., shade (light from the upper left).
import sys
from pathlib import Path
W = Path(__file__).parent
sys.path.insert(0, str(W.parent / "work"))
import gold

from PIL import Image as _I
# head rows 0-16: the set 58 golden head (work\g_gi_ssj2_d0.txt); body rows 17-31: the current golden PNG
# (controller V-neck fix, 2026-10-17), so a candidate carries the approved body unchanged
_HEAD = [r for r in (W.parent / "work" / "g_gi_ssj2_d0.txt").read_text().splitlines() if r]
BODY_PNG = W.parent / "golden_gi_ssj2_d0.png"
_BODY = gold.to_txt(_I.open(BODY_PNG)).split()
BASE = _HEAD[:17] + _BODY[17:]
HAIR = set("hYyoOLlWci")
TONE = {"front": ("L", "Y", "o"), "mid": ("y", "Y", "o"), "back": ("Y", "o", "O")}
# face rows 11-14 (x9-21): bare forehead, brows in h/i slanting down to the centre (rows 15-17 stay as the base)
FACE = {12: "e22222222222e", 13: "he322222223eh", 14: "e32hii2iih23e"}


def sp(y0, *spans):
    """Spans from row y0 down: sp(3, (5, 5), (5, 7)) -> {3: (5, 5), 4: (5, 7)}."""
    return {y0 + i: s for i, s in enumerate(spans)}


def flame(tip, base, hw, bulge=1.2):
    """A flame polygon: tip, a bulged side each way at 40% of its length, the two base corners."""
    (tx, ty), (bx, by) = tip, base
    dx, dy = bx - tx, by - ty
    n = (dx * dx + dy * dy) ** 0.5
    px, py = -dy / n, dx / n                                      # unit normal
    m = (tx + dx * 0.45, ty + dy * 0.45)
    return [(tx, ty), (m[0] + px * hw * bulge, m[1] + py * hw * bulge), (bx + px * hw, by + py * hw),
            (bx - px * hw, by - py * hw), (m[0] - px * hw * bulge, m[1] - py * hw * bulge)]


FOREHEAD = {(x, y) for y in range(13, 18) for x in range(10, 21)} | {(x, 12) for x in range(12, 19)}


def paint(flames, hard_to=4, soft_to=6, forehead=FOREHEAD):
    from PIL import Image, ImageDraw
    lab = {}
    for k, (_, shape) in enumerate(flames, 1):
        if isinstance(shape, dict):
            pts = {(x, y) for y, (x0, x1) in shape.items() for x in range(x0, x1 + 1)}
        else:
            im = Image.new("1", (32, 17), 0)
            ImageDraw.Draw(im).polygon(shape, fill=1)
            pts = {(x, y) for y in range(17) for x in range(32) if im.getpixel((x, y))}
        for p in pts - forehead:
            lab[p] = k
    rows = [list(r) for r in BASE]
    for y in range(15):
        rows[y] = ["." if c in HAIR else c for c in rows[y]]
    for y, s in FACE.items():
        rows[y][9:22] = list(s)
    top = {k: min(y for (x, y), kk in lab.items() if kk == k) for k in set(lab.values())}
    bot = {k: max(y for (x, y), kk in lab.items() if kk == k) for k in set(lab.values())}
    split = set()
    for (x, y), k in lab.items():
        nb = [lab.get((x + dx, y + dy), 0) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        if 0 in nb:
            rows[y][x] = "h"                                          # silhouette and hairline
            split.add((x, y))
        elif any(n > k for n in nb) and y <= soft_to:
            rows[y][x] = "h" if y <= hard_to else "O"                 # split: hard near the tips, soft below
            split.add((x, y))
    for (x, y), k in lab.items():
        if (x, y) in split:
            continue
        light, base, shade = TONE[flames[k - 1][0]]
        rel = (y - top[k]) / max(1, bot[k] - top[k])
        run_l = (x - 1, y) in split or lab.get((x - 1, y)) != k
        run_r = (x + 1, y) in split or lab.get((x + 1, y)) != k
        under = any(lab.get((x + dx, y + dy), 0) > k for dx, dy in ((-1, 0), (1, 0), (0, -1)))
        if under or (run_r and not run_l):
            c = shade
        elif run_l and rel < 0.7:
            c = light
        else:
            c = shade if rel > 0.85 and flames[k - 1][0] != "front" else base
        rows[y][x] = c
    return ["".join(r) for r in rows]


def apply(rows, edits):
    """Hand edits: {(x, y): char} or row strings {y: (x0, 'chars')}; '_' in chars keeps the pixel."""
    rows = [list(r) for r in rows]
    for y, (x0, s) in edits.items():
        for i, c in enumerate(s):
            if c != "_":
                rows[y][x0 + i] = c
    return ["".join(r) for r in rows]


def save(name, rows):
    assert len(rows) == 32 and all(len(r) == 32 for r in rows), name
    assert rows[17:] == BASE[17:], f"{name}: body rows changed"
    p = W / f"{name}.txt"
    p.write_bytes(("\n".join(rows) + "\n").encode())
    return p
