# throwaway: new Super Saiyan 2 heads. Base: the clean set 59 spikes (gi_ssj idle, shifted +8 into the 32 px frame),
# made fuller with extra swept spikes behind it in the same style (outline h=20, dark c=120, mid L=46, light W=2),
# green Super Saiyan 2 eyes, brows 20/21, and the single bang. Body rows stay the Super Saiyan 2 golden body.
from pathlib import Path
W = Path(__file__).parent
EYES = {"t": "v", "T": "V"}


def spans_v(g, spans):
    keys = list(spans)
    for n, y in enumerate(keys):
        x0, x1 = spans[y]
        for x in range(x0, x1 + 1):
            w, i = x1 - x0 - 1, x - x0 - 1
            g[(x, y)] = "h" if n == 0 or x in (x0, x1) else ("L" if i == 0 else "c" if i == w - 1 and w >= 3 else "W" if i == 1 and w >= 4 else "L")


def spans_h(g, spans):
    keys = list(spans)
    for n, x in enumerate(keys):
        y0, y1 = spans[x]
        for y in range(y0, y1 + 1):
            w, i = y1 - y0 - 1, y - y0 - 1
            g[(x, y)] = "h" if n == 0 or y in (y0, y1) else ("L" if i == 0 else "c" if i == w - 1 and w >= 3 else "W" if i == 1 and w >= 4 else "L")


def mir(kind, spans, axis=31):
    return (kind, {y: (axis - b, axis - a) for y, (a, b) in spans.items()}) if kind == "v" else (kind, {axis - x: v for x, v in spans.items()})


def grid(name):
    return [list(r) for r in (W / name).read_text().splitlines() if r]


def build(ssj_txt, body_txt, out, extra, shift=8, top=17, edits=None, flip_axis=31):
    ssj, body = grid(ssj_txt), grid(body_txt)
    g = {}
    for kind, spans in extra:
        (spans_v if kind == "v" else spans_h)(g, spans)
    for y in range(top):
        for x, c in enumerate(ssj[y]):
            if c != ".":
                g[(x + shift, y)] = EYES.get(c, c)
    for (x, y), c in (edits or {}).items():
        g[(x, y)] = c
    rows = [["."] * 32 for _ in range(32)]
    for (x, y), c in g.items():
        if c != "_" and 0 <= x < 32 and 0 <= y < top:
            rows[y][x] = c
    for y in range(top, 32):
        rows[y] = body[y]
    rows[0] = ["."] * 32                                         # no spike touches the slot's top edge
    hair = set("LWcYlo")
    for y in range(top):                                        # every hair pixel on the silhouette is outline
        for x in range(32):
            if rows[y][x] in hair and any(not (0 <= x + dx < 32 and 0 <= y + dy < 32) or rows[y + dy][x + dx] == "."
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                rows[y][x] = "h"
    (W / out).write_bytes(("\n".join("".join(r) for r in rows) + "\n").encode())


SIDE_L = ("h", {2: (3, 3), 3: (3, 5), 4: (4, 7), 5: (4, 9), 6: (5, 10), 7: (5, 11), 8: (6, 12), 9: (7, 12)})
LOW_L = ("h", {4: (12, 12), 5: (11, 13), 6: (11, 14), 7: (10, 14), 8: (10, 15), 9: (10, 15)})
UP_L = ("v", {1: (6, 6), 2: (6, 8), 3: (6, 9), 4: (7, 10), 5: (7, 11), 6: (8, 12), 7: (9, 12)})
TOP_L = ("v", {0: (10, 10), 1: (9, 11), 2: (9, 12), 3: (10, 13), 4: (10, 14)})
FRONT_EXTRA = [LOW_L, mir(*LOW_L), SIDE_L, mir(*SIDE_L), UP_L, mir(*UP_L), TOP_L, mir(*TOP_L)]

def row_edits(rows):
    return {(x, y): c for y, r in rows.items() for x, c in enumerate(r) if c != " "}


FRONT_EDITS = row_edits({                                       # one bang over the forehead, brows 20/21
    12: "        hLchLLh32223hch",
    13: "        hLehLhi2i h3eh",
})

BACK_EXTRA = FRONT_EXTRA                                        # seen from behind the fan is the same
SIDE_EXTRA = [
    ("h", {29: (10, 10), 28: (9, 11), 27: (9, 12), 26: (8, 12), 25: (8, 13), 24: (8, 13), 23: (8, 13)}),
    ("h", {30: (3, 3), 29: (3, 5), 28: (4, 7), 27: (4, 8), 26: (5, 9), 25: (5, 10), 24: (6, 10), 23: (6, 11)}),
    ("v", {0: (25, 25), 1: (24, 26), 2: (23, 26), 3: (22, 26), 4: (21, 25), 5: (20, 24)}),
]

if __name__ == "__main__":
    build("gi_ssj_d0.txt", "g_gi_ssj2_d0.txt", "head_d0.txt", FRONT_EXTRA, edits=FRONT_EDITS)
    build("gi_ssj_d1.txt", "g_gi_ssj2_d1.txt", "head_d1.txt", BACK_EXTRA)
    build("gi_ssj_d2.txt", "g_gi_ssj2_d2.txt", "head_d2.txt", SIDE_EXTRA)
