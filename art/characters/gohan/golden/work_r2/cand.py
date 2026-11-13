# throwaway (golden fix r2): the three SSJ2 front head candidates. Each = flame spans (first pass) + hand edits.
#   python -I cand.py        writes cand_<X>.txt and v_cand.png (10x grids) + v_small.png (1x, 2x, 3x vs SSJ)
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
sys.path.insert(0, str(W))
sys.path.insert(0, str(W.parent / "work"))
from flames import sp, flame, paint, apply, save
import gold

# ---------- A: the set 58 outline and height, regrouped into clumps; two tips raised; one bang ----------
A_FLAMES = [
    ("back", sp(3, (10, 21), (9, 22), (8, 22), (8, 22), (8, 23), (7, 23), (8, 22), (8, 22), (7, 23), (8, 22))),
    ("mid", sp(5, (8, 10), (8, 10), (8, 10), (7, 10), (8, 10), (8, 10), (7, 10), (8, 11))),               # LS
    ("mid", sp(2, (21, 21), (20, 22), (20, 22), (20, 22), (20, 22), (20, 23), (20, 23), (20, 22), (20, 22),
               (19, 23), (19, 22))),                                                                     # RS
    ("front", sp(1, (10, 10), (10, 12), (10, 12), (9, 13), (9, 13), (9, 13), (10, 13), (10, 13), (11, 13))),  # UL
    ("front", sp(0, (18, 18), (17, 19), (17, 19), (17, 20), (17, 20), (16, 20), (16, 20), (16, 19), (16, 19),
                 (16, 19))),                                                                             # UR
    ("front", sp(0, (14, 14), (13, 15), (13, 15), (13, 16), (13, 16), (12, 16), (12, 16), (12, 17), (12, 17),
                 (12, 17), (11, 18), (11, 18))),                                                         # C + fringe
]
A_EDITS = {}

CANDS = {"A": (A_FLAMES, A_EDITS)}


def build(name):
    flames, edits = CANDS[name]
    return apply(paint(flames), edits)


def small_view(names, out):
    """SSJ golden front, original set 58 front and each candidate on one anchor at 1x, 2x and 3x (game-scale check)."""
    import compose
    ssj = (Image.open(W.parent / "golden_gi_ssj_d0.png"), compose.rec_of("gi_ssj", 0))
    rec2 = compose.rec_of("gi_ssj2", 0)
    items = [ssj, (gold.from_txt(W.parent / "work" / "g_gi_ssj2_d0.txt"), rec2)]
    items += [(gold.from_txt(W / f"cand_{n}.txt"), rec2) for n in names]
    canvas = Image.new("RGB", (40 + len(items) * 6 * 34, 200), (150, 150, 150))
    canvas = Image.new("RGB", (20 + len(items) * (6 * 32 + 30), 120), (150, 150, 150))
    for i, (img, rec) in enumerate(items):
        x = 10 + i * (6 * 32 + 30)
        for s, dx in ((1, 0), (2, 40), (3, 110)):
            canvas.paste(compose.cell(img, rec, s, box=False), (x + dx, 10))
    canvas.save(out)

if __name__ == "__main__":
    paths = []
    for n in sys.argv[1:] or CANDS:
        rows = build(n)
        paths.append(str(save(f"cand_{n}", rows)))
        print("\n".join(f"{y:2d} {r}" for y, r in enumerate(rows[:18])))
    gold.grid_view([str(W.parent / "work" / "g_gi_ssj2_d0.txt")] + paths, 14).save(W / "v_cand.png")
    small_view(sys.argv[1:] or list(CANDS), W / "v_small.png")

