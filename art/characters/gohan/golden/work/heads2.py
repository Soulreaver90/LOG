# throwaway: new Super Saiyan 2 heads drawn from hand-set spans (scanline spikes), back to front.
# A spike is ("v", {y: (x0, x1)}) or ("h", {x: (y0, y1)}); the first key is the tip. Shading: outline 20 (h),
# lit edge 44/46 (l, L) on the left or top, mid 37 (Y), shade 38 (o) on the right or bottom.
import sys
from pathlib import Path
W = Path(__file__).parent


def put_v(g, spans, open_end=True):
    keys = list(spans)
    for n, y in enumerate(keys):
        x0, x1 = spans[y]
        for x in range(x0, x1 + 1):
            if n == 0 or x in (x0, x1):
                c = "h"
            else:
                w = x1 - x0 - 1
                i = x - x0 - 1
                c = "l" if i == 0 and w >= 4 else "L" if i <= (0 if w < 4 else 1) else "o" if i == w - 1 and w >= 3 else "Y"
            g[(x, y)] = c
    if not open_end:
        y = keys[-1]
        for x in range(spans[y][0], spans[y][1] + 1):
            g[(x, y)] = "h"


def put_h(g, spans):
    keys = list(spans)
    for n, x in enumerate(keys):
        y0, y1 = spans[x]
        for y in range(y0, y1 + 1):
            if n == 0 or y in (y0, y1):
                c = "h"
            else:
                w = y1 - y0 - 1
                i = y - y0 - 1
                c = "l" if i == 0 and w >= 4 else "L" if i <= (0 if w < 4 else 1) else "o" if i == w - 1 and w >= 3 else "Y"
            g[(x, y)] = c


def mirror(spike, axis):
    kind, spans = spike
    if kind == "v":
        return kind, {y: (axis - b, axis - a) for y, (a, b) in spans.items()}
    return kind, {axis - x: v for x, v in spans.items()}


def face_from(rows, x0, y0):
    return {(x0 + i, y0 + j): c for j, r in enumerate(rows) for i, c in enumerate(r) if c != " "}


def build(layers, body_txt, out_name, top=17):
    body = [list(r) for r in (W / body_txt).read_text().splitlines() if r]
    g = {}
    for kind, item in layers:
        if kind == "v":
            put_v(g, item)
        elif kind == "h":
            put_h(g, item)
        elif kind == "face":
            g.update(item)
        elif kind == "px":
            g.update(item)
    grid = [["."] * 32 for _ in range(32)]
    for (x, y), c in g.items():
        if 0 <= x < 32 and 0 <= y < top:
            grid[y][x] = c
    for y in range(top, 32):
        grid[y] = body[y]
    (W / out_name).write_bytes(("\n".join("".join(r) for r in grid) + "\n").encode())


def both(spike, axis=30):
    return [spike, mirror(spike, axis)]


# ---- front (dir 0): center x 15 ----
S1 = ("h", {2: (11, 11), 3: (10, 12), 4: (10, 12), 5: (9, 13), 6: (9, 13), 7: (8, 14), 8: (8, 15), 9: (8, 15)})
S2 = ("v", {3: (3, 3), 4: (3, 5), 5: (4, 7), 6: (5, 9), 7: (6, 10), 8: (7, 11), 9: (8, 12)})
S3 = ("v", {0: (8, 8), 1: (8, 9), 2: (8, 10), 3: (9, 11), 4: (9, 12), 5: (10, 13), 6: (10, 14), 7: (11, 14)})
S4 = ("v", {0: (15, 15), 1: (14, 16), 2: (14, 16), 3: (13, 17), 4: (13, 17), 5: (12, 18), 6: (12, 18), 7: (12, 18)})
CROWN = ("v", {7: (9, 21), 8: (8, 22), 9: (8, 22), 10: (8, 22), 11: (8, 22)})
SIDE = ("v", {11: (7, 10), 12: (7, 9), 13: (7, 9), 14: (7, 9), 15: (8, 8)})
BANG = ("v", {9: (12, 15), 10: (11, 15), 11: (11, 15), 12: (12, 14), 13: (13, 13)})
FACE0 = face_from([
    "e32222222223e",
    "e42222222224e",
    "e42iih2hii24e",
    "e422Wv2vW224e",
    " e42WV3Vw24e ",
], 9, 12)


def front():
    L = [("v", CROWN[1])]
    for s in both(S1) + both(S2) + both(S3):
        L.append(s)
    L.append(S4)
    L.append(("face", FACE0))
    for s in both(SIDE):
        L.append(s)
    L.append(BANG)
    return L


if __name__ == "__main__":
    build(front(), "gi_ssj2_d0.txt", "head_d0.txt")
