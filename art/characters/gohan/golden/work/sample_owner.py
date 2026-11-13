# Sample the owner's mockup onto the 32x32 grid (scale 11.8, origin 76,34), quantized to the frame palette.
from PIL import Image
from collections import Counter
S, X0, Y0 = 11.8, 76, 34
m = Image.open('owner/owner_mock_ssj2_d0_1000.png').convert('RGB'); mp = m.load(); W, H = m.size
g = Image.open('golden_gi_ssj2_d0.png'); pal = g.getpalette()
used = sorted(set(g.getdata()) | {20, 21})
cols = {i: tuple(pal[i*3:i*3+3]) for i in used}

def nearest(c):
    if sum(abs(c[k] - 150) for k in range(3)) < 12:
        return 0
    return min((i for i in used if i), key=lambda i: sum((c[k] - cols[i][k]) ** 2 for k in range(3)))

grid = {}
for y in range(-3, 32):
    for x in range(32):
        votes = Counter()
        for fy in (0.3, 0.5, 0.7):
            for fx in (0.3, 0.5, 0.7):
                cx, cy = int(X0 + (x + fx) * S), int(Y0 + (y + fy) * S)
                votes[nearest(mp[cx, cy]) if 0 <= cx < W and 0 <= cy < H else 0] += 1
        grid[x, y] = votes.most_common(1)[0][0]
gp = g.load()
print('palette', {i: cols[i] for i in used})
for y in range(-3, 22):
    print('%3d ' % y + ' '.join('%3d' % grid[x, y] for x in range(4, 28)) + ('   ' + ' '.join('%3d' % gp[x, y] for x in range(4, 28)) if y >= 0 else ''))
