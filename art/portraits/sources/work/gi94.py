"""Throwaway: colors in Piccolo 94's gi shoulder (bottom right) and the status twin."""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")
import gohan_portraits as gp
rom = gp.BASE.read_bytes()
obj, stat = gp.palette(rom, gp.OBJ_PAL), gp.palette(rom, gp.STATUS_PAL)
px = gp.portrait(rom, 94)
c = Counter(px[y * 64 + x] for y in range(44, 62) for x in range(36, 62))
for k, n in c.most_common(): print(k, obj[k], n)
print("pairs", gp.pairs(rom))
for y in range(40, 64):
    print("".join(f"{px[y*64+x]:4d}" for x in range(30, 64)))
