"""Throwaway: dump rows of a portrait (id or PNG path) as index grids, plus color legend."""
import sys
from collections import Counter
from PIL import Image
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")
import gohan_portraits as gp
rom = gp.BASE.read_bytes()
obj = gp.palette(rom, gp.OBJ_PAL)
src, y0, y1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
px = gp.portrait(rom, int(src)) if src.isdigit() else Image.open(src).tobytes()
print("    " + "".join(f"{x:4d}" for x in range(64)))
for y in range(y0, y1):
    print(f"{y:3d} " + "".join(f"{px[y*64+x]:4d}" for x in range(64)))
c = Counter(px[y*64+x] for y in range(y0, y1) for x in range(64))
print({k: (obj[k], n) for k, n in c.most_common()})
