# Quantize the owner's 10:00 AM mockup to the 32-wide grid (scale 11.8, origin 76,34) with the set 58 hair ramp.
import sys
from collections import Counter
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import CH, PAL
S, X0, Y0 = 11.8, 76, 34
m = Image.open(G / "owner/owner_mock_ssj2_d0_1000.png").convert("RGB"); mp = m.load(); W, H = m.size
USE = [2, 9, 20, 21, 23, 36, 37, 38, 39, 44, 46, 49, 50, 113, 114, 115, 116, 117, 11]
col = {i: tuple(PAL[3 * i:3 * i + 3]) for i in USE}


def q(c):
    if max(abs(c[k] - 150) for k in range(3)) < 10:
        return "."
    return CH[min(USE, key=lambda i: sum((c[k] - col[i][k]) ** 2 for k in range(3)))]


for y in range(-3, 17):
    row = ""
    for x in range(32):
        v = Counter(q(mp[int(X0 + (x + fx) * S), int(Y0 + (y + fy) * S)]) for fx in (.35, .5, .65) for fy in (.35, .5, .65))
        row += v.most_common(1)[0][0]
    print("%3d %s" % (y, row))
