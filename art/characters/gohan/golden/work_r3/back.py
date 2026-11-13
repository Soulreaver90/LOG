# Super Saiyan 2 back head (dir 1): rows 0-9 reuse the approved front flames (same silhouette, same light),
# rows 10-16 hang the back hair over the skull to the neck, from the SSJ1 back recoloured to the SSJ2 ramp.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import to_txt
OUT = sys.argv[1] if len(sys.argv) > 1 else "back_v1.txt"
front = to_txt(Image.open(G / "golden_gi_ssj2_d0.png")).splitlines()
ssj = to_txt(Image.open(G / "golden_gi_ssj_d1.png")).splitlines()
RAMP = str.maketrans({"W": "L", "L": "Y", "c": "o"})
LOW = """
.......hooOoYYoOYYoOoooh........
"""
rows = to_txt(Image.open(G / "golden_gi_ssj2_d1.png")).splitlines()
rows[:10] = front[:10]
rows[10] = [r for r in LOW.splitlines() if r][0]
for y in range(11, 17):
    rows[y] = ("........" + ssj[y]).translate(RAMP)[:32].ljust(32, ".")
assert all(len(r) == 32 for r in rows)
Path(__file__).with_name(OUT).write_text("\n".join(rows) + "\n")
for i, r in enumerate(rows[:20]):
    print("%2d %s" % (i, r))
