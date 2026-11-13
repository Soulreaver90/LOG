# throwaway (golden fix r2, after the controller reset): hand-drawn SSJ2 front heads on the set 58 outline.
# Each head is rows 0-15 of a 19 px window (x6-24) pasted over work\g_gi_ssj2_d0.txt; rows 16-31 stay as the base.
#   python -I hand.py [A B C]   writes cand_<X>.txt, v_cand.png (20x) and v_small.png (1x/2x/3x vs SSJ and set 58)
import sys
from pathlib import Path
W = Path(__file__).parent
sys.path.insert(0, str(W))
sys.path.insert(0, str(W.parent / "work"))
import gold
from flames import BASE, save
X0 = 6
RULER = "6789012345678901234"

HEADS = {}
# A: set 58 outline; five wedges (three up-pointing top clumps, two down-pointing fringe clumps at the temples),
#    each with a dark outline, one L highlight streak on its lit edge, Y body and one o shade; one bang strand
HEADS["A"] = [
    "........h.....h....",   # 0
    ".......hLh...hLh...",   # 1
    "...h...hLYh.hLYh...",   # 2
    "...hLhhLYYohLYYoh..",   # 3
    "..hLYhLYYYohLYYoh..",   # 4
    "..hLYhLYYohLYYYoh..",   # 5
    "..hLYohLYohLYYYoh..",   # 6
    "..hLYohLYohhYYYYoh.",   # 7
    ".hYYhhLhLYhLhhYYoh.",   # 8
    "..hhLYohLYhLYohhh..",   # 9
    "..hLYYohLYhLYYYoh..",   # 10
    ".hLYYohhLYhhYYYoh..",   # 11
    "..hYoh22Yh222hYoh..",   # 12
    "...he32Yh22223eh...",   # 13
    "...e32Yhi2iih23e...",   # 14
    "...e4ihWv2vW2i4e...",   # 15
]

# B: swept to the viewer's right: four up-pointing wedges (a side wedge flares out right past the set 58 edge),
#    one down-pointing fringe wedge at the left temple; a two-pixel bang that tapers to the left eye
HEADS["B"] = [
    ".........h....h....",   # 0
    "....h...hLh..hLh...",   # 1
    "...hLh.hLYh.hLYh...",   # 2
    "...hLYhLYYohLYYh.h.",   # 3
    "..hLYohLYYohLYYhLh.",   # 4
    "..hLYhLYYYohLYohLYh",   # 5
    "..hLohLYYYohLYohYoh",   # 6
    "..hYhhLYYohLYYohYh.",   # 7
    ".hYYhhLhLYhLYYohYh.",   # 8
    "..hhLYohLYhLYohYh..",   # 9
    "..hLYYohLYhLohLoh..",   # 10
    ".hLYYohhLYhYohYYoh.",   # 11
    "..hYoh22LYh22hYoh..",   # 12
    "...he32LYh2223eh...",   # 13
    "...e32hYh2iih23e...",   # 14
    "...e4ihWv2vW2i4e...",   # 15
]

# C: the rounder set 58 dome: one big centre clump with twin tips raised to row 0 (a short inner shade line
#    under the fork), a long side clump each way down to the temples; the bang drops straight and hooks left
HEADS["C"] = [
    ".......h...h.......",   # 0
    "......hLh.hLh......",   # 1
    "...h..hLYhLYYh.h...",   # 2
    "...hLhLYYoLYohLh...",   # 3
    "..hLYhLYYoYYohLYh..",   # 4
    "..hLYhLYYYYYohLYh..",   # 5
    "..hLYohLYYYohLYoh..",   # 6
    "..hLYohLYYYohLYYoh.",   # 7
    ".hLYYohLYYohLYYYoh.",   # 8
    "..hLYYohLYohLYYoh..",   # 9
    "..hYYYohLYhLYYYoh..",   # 10
    ".hYYohhLYhhLYYYYoh.",   # 11
    "..hYh22Lh2222hYoh..",   # 12
    "...he32Lh22223eh...",   # 13
    "...e32hYh2iih23e...",   # 14
    "...e4ihWv2vW2i4e...",   # 15
]

def build(name):
    rows = [list(r) for r in BASE]
    for y, s in enumerate(HEADS[name]):
        assert len(s) == 19, (name, y, len(s))
        rows[y][X0:X0 + 19] = list(s)
    return ["".join(r) for r in rows]


def view3x(names, out):
    """SSJ golden, set 58 original, then each candidate at 3x on one anchor, all shown 2x again for review."""
    from PIL import Image
    import compose
    rec2 = compose.rec_of("gi_ssj2", 0)
    items = [(Image.open(W.parent / "golden_gi_ssj_d0.png"), compose.rec_of("gi_ssj", 0)),
             (gold.from_txt(W.parent / "work" / "g_gi_ssj2_d0.txt"), rec2)]
    items += [(gold.from_txt(W / f"cand_{n}.txt"), rec2) for n in names]
    o = Image.new("RGB", (10 + len(items) * 106, 140), (150, 150, 150))
    for i, (img, rec) in enumerate(items):
        o.paste(compose.cell(img, rec, 3, box=False), (10 + i * 106, 10))
        o.paste(compose.cell(img, rec, 1, box=False), (10 + i * 106, 106))
    o.resize((o.width * 2, o.height * 2), Image.NEAREST).save(out)


if __name__ == "__main__":
    from cand import small_view
    names = sys.argv[1:] or list(HEADS)
    paths = [str(save(f"cand_{n}", build(n))) for n in names]
    gold.grid_view([str(W.parent / "work" / "g_gi_ssj2_d0.txt")] + paths, 20).save(W / "v_cand.png")
    small_view(names, W / "v_small.png")
    view3x(names, W / "v_3x.png")
