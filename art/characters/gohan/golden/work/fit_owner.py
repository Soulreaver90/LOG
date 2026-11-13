# Fit the owner's upscaled mockup to the 32x32 grid by matching the unchanged lower body.
from PIL import Image
m = Image.open('owner/owner_mock_ssj2_d0_1000.png').convert('RGB'); mp = m.load(); W, H = m.size
gp = Image.open('golden_gi_ssj2_d0.png').convert('RGBA').load()
BG = (150, 150, 150)

def score(s, X0, Y0):
    hit = 0
    for y in range(22, 32):
        for x in range(32):
            r, g, b, a = gp[x, y]
            cx, cy = int(X0 + (x + 0.5) * s), int(Y0 + (y + 0.5) * s)
            if not (0 <= cx < W and 0 <= cy < H):
                c = BG
            else:
                c = mp[cx, cy]
            t = (r, g, b) if a else BG
            hit += sum(abs(c[i] - t[i]) for i in range(3)) < 40
    return hit

best = (0,)
for s100 in range(1150, 1351, 5):
    s = s100 / 100
    for X0 in range(-40, 120, 2):
        for Y0 in range(-60, 40, 2):
            v = score(s, X0, Y0)
            if v > best[0]:
                best = (v, s, X0, Y0)
print(best)
