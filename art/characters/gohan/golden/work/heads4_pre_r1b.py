# throwaway (golden fix r1): Super Saiyan 2 heads, taller than wide. Front and back: the set 59 head (golden SSJ,
# shifted +8) plus up-pointing spikes (vertical to 45 degrees out) inside x5-26. Side: drawn from spans so every spike
# sweeps up and back and nothing points forward past the face. Colors: set 59 ramp h=20 c=120 L=46 W=2, brows 21.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from heads3 import spans_v, mir, grid

W = Path(__file__).parent
EYES = {"t": "v", "T": "V"}
HAIR = set("LWcYlo")


def compose(layers, base_txt, base_rows, body_txt, out, edits, top=17, shift=8):
    body = grid(body_txt)
    g = {}
    for spans in layers["behind"]:
        dark = isinstance(spans, tuple)
        if dark:
            spans = spans[0]
        before = dict(g)
        spans_v(g, spans)
        if dark:                                                # the crown is the shadow between spikes
            for p, c in g.items():
                if c != "h" and before.get(p) != c:
                    g[p] = "c"
    if base_txt:
        base = grid(base_txt)
        for y in base_rows:
            for x, c in enumerate(base[y]):
                if c != ".":
                    g[(x + shift, y)] = EYES.get(c, c)
    for spans in layers.get("front", []):
        spans_v(g, spans)
    g.update(edits)
    rows = [["."] * 32 for _ in range(32)]
    for (x, y), c in g.items():
        if c != "." and 0 <= x < 32 and 0 <= y < top:
            rows[y][x] = c
        elif c == "." and 0 <= y < top:
            rows[y][x] = "."
    for y in range(top, 32):
        rows[y] = body[y]
    for y in range(top):                                        # every hair pixel on the silhouette is outline
        for x in range(32):
            if rows[y][x] in HAIR and any(not (0 <= x + dx < 32 and 0 <= y + dy < 32) or rows[y + dy][x + dx] == "."
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                rows[y][x] = "h"
    (W / out).write_bytes(("\n".join("".join(r) for r in rows) + "\n").encode())
    return rows


def edits_from(rows, x0=0):
    return {(x0 + i, y): c for y, r in rows.items() for i, c in enumerate(r) if c != " "}


# ---- front and back: extra up-pointing spikes behind the set 59 head ----
TALL_L = {0: (11, 11), 1: (10, 12), 2: (10, 12), 3: (10, 13), 4: (10, 14)}
TALL_R = {0: (22, 22), 1: (21, 23), 2: (21, 23), 3: (20, 23)}
OUT_L = {1: (8, 8), 2: (8, 9), 3: (8, 10), 4: (9, 11), 5: (9, 12), 6: (10, 12)}
FRONT_BEHIND = [OUT_L, mir("v", OUT_L)[1], TALL_L, TALL_R]

FRONT_EDITS = edits_from({                                       # one bang left of center, brows 21
    11: "             hLh",
    12: "         hLchhLh2223hcLh",
    13: "        hLe2iihi2ii23ehh",
})

# ---- side (dir 2, faces left): face x11-21; spikes lean back (right) ----
CROWN = {9: (11, 26), 10: (11, 25), 11: (11, 25), 12: (12, 24)}
NAPE = {12: (19, 25), 13: (19, 24), 14: (20, 23), 15: (21, 22)}
SIDE_SPIKES = [                                                  # back to front; roots run into the dark crown
    {1: (26, 26), 2: (25, 26), 3: (24, 26), 4: (23, 26), 5: (22, 26), 6: (21, 25), 7: (20, 25), 8: (19, 24), 9: (19, 24)},
    {0: (23, 23), 1: (22, 24), 2: (22, 24), 3: (21, 24), 4: (20, 23), 5: (19, 23), 6: (18, 22), 7: (17, 21), 8: (16, 21),
     9: (16, 20)},
    {0: (17, 17), 1: (16, 18), 2: (16, 18), 3: (15, 18), 4: (15, 19), 5: (14, 19), 6: (14, 19), 7: (13, 18), 8: (13, 18),
     9: (13, 17)},
    {1: (12, 12), 2: (11, 13), 3: (11, 13), 4: (11, 14), 5: (11, 14), 6: (11, 14), 7: (11, 15), 8: (11, 15), 9: (11, 14)},
]
SIDE_EDITS = edits_from({                                        # forehead, brow, bang in front of the face
    11: "           hLh",
    12: "           hLhe2223h",
    13: "           ehiih23hLh",
})

if __name__ == "__main__":
    compose({"behind": FRONT_BEHIND}, "g_gi_ssj_d0.txt", range(17), "g_gi_ssj2_d0.txt", "head_d0.txt", FRONT_EDITS)
    compose({"behind": FRONT_BEHIND}, "g_gi_ssj_d1.txt", range(17), "g_gi_ssj2_d1.txt", "head_d1.txt", {})
    compose({"behind": [(CROWN,), NAPE] + SIDE_SPIKES}, "g_gi_ssj_d2.txt", range(14, 17), "g_gi_ssj2_d2.txt",
            "head_d2.txt", SIDE_EDITS)
