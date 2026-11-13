# Lists the r14 aura bolt pixels (r14 minus r12) of a set 159 key, and where they land on the r12fix frame.
# Usage: py -3 -I bolts_check.py 159.1.0.0 ...
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import view  # noqa: E402
import fix  # noqa: E402

R14 = view.ROOT / "scratch" / "art" / "review" / "frames_r14"

for key in sys.argv[1:]:
    s, a, d, i = fix.parse(key)
    pal = view.palette()
    r12 = fix.frames(key, pal)[1]
    r14 = view.load(R14 / view.name(s, a, d, i), pal)
    fx = fix.load_fix(key)
    print(key, "size r12", len(r12[0]), "x", len(r12), "r14", len(r14[0]), "x", len(r14))
    bolts = [(x, y, r14[y][x]) for y in range(len(r14)) for x in range(len(r14[0])) if r14[y][x] != r12[y][x]]
    over = [(x, y, c, fx[y][x]) for x, y, c in bolts if fx[y][x] != r12[y][x]]
    print("  bolt px", len(bolts), "colors", sorted({c for _, _, c in bolts}))
    print("  bolt px over my edits", len(over), over[:20])
