# throwaway: draw the new Super Saiyan 2 heads from spike polygons (back to front), then a hand-set face.
# Each spike: (tip, base_a, base_b). Outline 20 (h), dark 38 (o) at the root, mid 37 (Y), light 46 (L) on the lit
# (upper left) side, highlight 44 (l) along the axis near the tip. Output: <name>.txt grids (32x32, body kept).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import gold

W = Path(__file__).parent


def inside(p, poly):
    x, y = p
    n, ok = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ok = not ok
    return ok


def spike(grid, tip, a, b, light=-1):
    poly = [tip, a, b]
    cells = {(x, y) for y in range(32) for x in range(32) if inside((x + 0.5, y + 0.5), poly)}
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax, ay = tip[0] - mx, tip[1] - my
    ln = (ax * ax + ay * ay) ** 0.5
    half = (((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5) / 2
    for (x, y) in cells:
        px, py = x + 0.5 - mx, y + 0.5 - my
        t = (px * ax + py * ay) / ln ** 2                     # 0 root, 1 tip
        s = (px * -ay + py * ax) / ln / max(half * (1 - t), 0.5)   # -1..1 across the spike
        edge = any(q not in cells for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        if edge:
            c = "h"
        elif t < 0.22:
            c = "o"
        elif t > 0.45 and abs(s) < 0.35:
            c = "l"
        elif s * light > 0:
            c = "L"
        else:
            c = "Y"
        grid[y][x] = c
    return cells


def shade(cells, tip, a, b, light):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    ax, ay = tip[0] - mx, tip[1] - my
    ln = (ax * ax + ay * ay) ** 0.5
    half = (((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5) / 2
    out = {}
    for (x, y) in cells:
        px, py = x + 0.5 - mx, y + 0.5 - my
        t = (px * ax + py * ay) / ln ** 2
        s = (px * -ay + py * ax) / ln / max(half * (1 - t), 0.5)
        out[(x, y)] = "o" if t < 0.2 else "l" if t > 0.5 and abs(s) < 0.4 else "L" if s * light > 0 else "Y"
    return out


def ellipse(cx, cy, rx, ry):
    return {(x, y) for y in range(32) for x in range(32) if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1}


def draw(spikes, face, body_txt, out_name, top_rows=17, skull=None):
    body = [list(r) for r in (W / body_txt).read_text().splitlines() if r]
    grid = [["."] * 32 for _ in range(32)]
    owner, color = {}, {}
    shapes = []
    if skull:
        cells = ellipse(*skull)
        shapes.append((cells, {p: ("o" if p[1] > skull[1] + 1 else "Y") for p in cells}))
    for sp in spikes["back"] + spikes.get("mid", []):
        tip, a, b, light = sp
        cells = {(x, y) for y in range(32) for x in range(32) if inside((x + 0.5, y + 0.5), [tip, a, b])}
        shapes.append((cells, shade(cells, tip, a, b, light)))
    for i, (cells, col) in enumerate(shapes):
        for p in cells:
            owner[p] = i; color[p] = col[p]
    front = []
    for sp in spikes["front"]:
        tip, a, b, light = sp
        cells = {(x, y) for y in range(32) for x in range(32) if inside((x + 0.5, y + 0.5), [tip, a, b])}
        front.append((cells, shade(cells, tip, a, b, light)))
    def paint(owner, color):
        for p, i in owner.items():
            x, y = p
            nb = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(q not in owner for q in nb):
                grid[y][x] = "h"
            elif any(owner[q] > i for q in nb):
                grid[y][x] = "h"
            else:
                grid[y][x] = color[p]
    paint(owner, color)
    for (x, y), c in face.items():
        grid[y][x] = c
    for cells, col in front:
        o2 = {p: 0 for p in cells}
        for p in cells:
            x, y = p
            nb = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            grid[y][x] = "h" if any(q not in cells for q in nb) else col[p]
    for y in range(top_rows, 32):                               # the body rows stay as they are
        grid[y] = body[y]
    for y in range(top_rows):                                   # keep body pixels the head does not cover
        for x in range(32):
            if grid[y][x] == "." and body[y][x] != "." and y >= 16:
                grid[y][x] = body[y][x]
    (W / out_name).write_bytes(("\n".join("".join(r) for r in grid) + "\n").encode())


def face_from(rows, x0, y0):
    out = {}
    for j, r in enumerate(rows):
        for i, c in enumerate(r):
            if c != " ":
                out[(x0 + i, y0 + j)] = c
    return out


FRONT = {
    "back": [((2, 13), (8, 16), (9, 8), -1), ((29, 13), (22, 8), (23, 16), 1),
             ((2, 5), (8, 12), (11, 5), -1), ((29, 5), (20, 5), (23, 12), 1),
             ((8, 0), (9, 8), (15, 4), -1), ((23, 0), (16, 4), (22, 8), 1),
             ((15, 0), (11, 7), (20, 7), -1)],
    "front": [((13, 15), (11, 9), (17, 9), -1)],
}
FRONT_SKULL = (15.5, 10, 8.5, 6.5)
FRONT_FACE = face_from([
    " e3222222223e ",
    " e2222222222e ",
    "e42iih2hii24e",
    "e422Wv2vW224e",
    " e42WV3Vw24e ",
], 9, 12)

if __name__ == "__main__":
    draw(FRONT, FRONT_FACE, "gi_ssj2_d0.txt", "head_d0.txt", skull=FRONT_SKULL)
