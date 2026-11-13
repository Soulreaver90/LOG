# Throwaway mock: shoe rule plus shading rule A on copies of all 9 golden views (goldens untouched).
# Shoe rule: each shoe (4-connected boot pixels 34, 35) keeps its bottom 2 rows; the row above them becomes the
# trouser hem (211); higher shoe rows become trouser (89, 211 at the part's left and right edge). Then rule A.
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
GOLD = W.parents[1]
sys.path.insert(0, str(W))
from shade_mock import shade                                   # rule A
BOOT, HEM, TROUSER = {34, 35}, 211, 89


def shoes(px, w, h):
    out = bytearray(px)
    seen = set()
    for start in range(w * h):
        if px[start] not in BOOT or start in seen:
            continue
        part, todo = set(), [start]
        while todo:
            i = todo.pop()
            if i in part or px[i] not in BOOT:
                continue
            part.add(i)
            x, y = i % w, i // w
            todo += [j for j, ok in ((i - 1, x > 0), (i + 1, x < w - 1), (i - w, y > 0), (i + w, y < h - 1)) if ok]
        seen |= part
        bottom = max(i // w for i in part)
        for i in part:
            y = i // w
            if y == bottom - 2:
                out[i] = HEM
            elif y < bottom - 2:
                row = [j % w for j in part if j // w == y]
                out[i] = HEM if i % w in (min(row), max(row)) else TROUSER
    return bytes(out)


S = 8
names = [f"golden_gi_{f}_d{d}.png" for f in ("base", "ssj", "ssj2") for d in (0, 2, 1)]
sheet = Image.new("RGB", (len(names) * 34 * S, 2 * 34 * S + 30), (112, 112, 112))
d = ImageDraw.Draw(sheet)
d.text((4, 4), "Row 1: now. Row 2: Piccolo-size shoes + shading rule A", fill=(255, 255, 255))
for c, n in enumerate(names):
    img = Image.open(GOLD / n)
    w, h = img.size
    px = img.tobytes()
    new = shade(shoes(px, w, h), w, h)
    for r, data in enumerate((px, new)):
        o = Image.frombytes("P", (w, h), data)
        o.putpalette(img.getpalette())
        big = o.convert("RGB").resize((w * S, h * S), Image.NEAREST)
        mask = Image.frombytes("L", (w, h), bytes(255 if v else 0 for v in data)).resize((w * S, h * S), Image.NEAREST)
        sheet.paste(big, (c * 34 * S, 20 + r * 34 * S), mask)
        if r == 1:
            o.save(W / n.replace("golden_", "shoesA_"), transparency=0)
sheet.save(W / "shoes_shade_mock.png")
print("ok")
