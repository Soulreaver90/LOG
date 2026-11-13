# Super Saiyan 2 front head from a silhouette, separator strokes and a fill rule (owner mockup 10:00 AM layout).
# Rows 0-9: generated. Rows 10-13: hand-drawn hairline, bang and brows. Rows 14-31: golden frame.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import to_txt

# ===== SHAPE (edit, then run) =====
SIL = {0: (15, 15), 1: (14, 16), 2: (13, 17), 3: (11, 19), 4: (9, 21), 5: (8, 22), 6: (8, 22), 7: (7, 23), 8: (7, 23), 9: (7, 23)}
TIPS = [(10, 2), (20, 2), (9, 3), (21, 3), (6, 8), (24, 9)]
SEP = [(12, 3), (12, 4), (18, 3), (18, 4),                     # notches under the side tips
       (10, 5), (10, 6), (9, 7), (9, 8),                       # S1 far left, flares out
       (12, 6), (12, 7), (13, 8), (13, 9),                     # S2
       (15, 6), (16, 7), (16, 8), (17, 9),                     # S3 centre
       (19, 5), (19, 6), (20, 7), (20, 8), (20, 9),            # S4
       (22, 7), (22, 8)]                                       # S5 far right
WHITE = [(15, 2), (14, 3), (15, 3), (14, 4), (14, 5), (13, 6)]
HAND = """
.......hoYoYYohLYYohhLYohoh.....
.......hoOohh2hLYh22hYoOoh......
........hoh32hLYh2223hoh........
........hoeiiLh22ii23ehh........
"""
OUT = "front_v3.txt"
# ==================================


def head_rows() -> list:
    g = [["."] * 32 for _ in range(10)]
    for y, (a, b) in SIL.items():
        for x in range(a, b + 1):
            g[y][x] = "h" if x in (a, b) else "?"
    for x, y in TIPS:
        g[y][x] = "h"
    for x, y in SEP:
        g[y][x] = "h"
    for y in range(10):
        x = 0
        while x < 32:
            if g[y][x] != "?":
                x += 1; continue
            e = x
            while e < 32 and g[y][e] == "?":
                e += 1
            n = e - x
            for i in range(n):
                g[y][x + i] = "L" if i == 0 else ("o" if i == n - 1 and n >= 3 else "Y")
            x = e
    for x, y in WHITE:
        g[y][x] = "W"
    return ["".join(r) for r in g]


rows = to_txt(Image.open(G / "golden_gi_ssj2_d0.png")).splitlines()
hand = [r for r in HAND.splitlines() if r]
rows[:10] = head_rows()
rows[10:10 + len(hand)] = hand
assert all(len(r) == 32 for r in rows)
Path(__file__).with_name(OUT).write_text("\n".join(rows) + "\n")
for i, r in enumerate(rows[:17]):
    print("%2d %s" % (i, r))
