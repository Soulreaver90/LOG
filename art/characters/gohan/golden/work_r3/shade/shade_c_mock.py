# Throwaway mock: rule C, Piccolo set 104 shading, on copies of the 9 golden views with the shoe rule
# (goldens untouched). Per horizontal run of gi pixels (88, 89): base 89; lit 88 at
#   n = 1: none, n = 2: the left pixel (light from the left), n = 3-4: the left-centre pixel,
#   n >= 5: even rows the centre pixel, odd rows the n - 2 middle pixels (Piccolo's PPpPP / PpppP folds).
# Deep folds 211: gi pixels on the row above a gap between the legs, at the gap columns (Piccolo row 22).
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
GOLD = W.parents[1]
SPR = W.parents[3] / "sprites"
sys.path.insert(0, str(W))
from shoes_shade_mock import shoes                             # noqa: E402
GI, BASE, LIT, DEEP = {88, 89}, 89, 88, 211


def shade_c(px, w, h):
    out = bytearray(px)
    for y in range(h):
        x = 0
        while x < w:
            if px[y * w + x] not in GI:
                x += 1
                continue
            s = x
            while x < w and px[y * w + x] in GI:
                x += 1
            n = x - s
            if n == 2:
                lit = {s}
            elif n in (3, 4):
                lit = {s + (n - 1) // 2}
            elif n >= 5:
                lit = {s + n // 2} if y % 2 == 0 else set(range(s + 1, x - 1))
            else:
                lit = set()
            for i in range(s, x):
                out[y * w + i] = LIT if i in lit else BASE
    for y in range(h - 1):                                     # crotch: gi above a transparent gap flanked by gi
        for x in range(1, w - 1):
            i = y * w + x
            if px[i] in GI and px[i + w] == 0 and px[i + w - 1] and px[i + w + 1]:
                out[i] = DEEP
    return bytes(out)


S = 8
names = [f"golden_gi_{f}_d{d}.png" for f in ("base", "ssj", "ssj2") for d in (0, 2, 1)]
pic = Image.open(SPR / "set104" / "frame_312804.png")
sheet = Image.new("RGB", (11 * 34 * S, 2 * 34 * S + 120), (112, 112, 112))
d = ImageDraw.Draw(sheet)
d.text((4, 4), "Row 1: gi now. Row 2: rule C + shoes. Col 1: Piccolo set 104. Bottom strip: all at 1x and 2x", fill=(255, 255, 255))
small = []
big = pic.convert("RGBA").resize((16 * S, 32 * S), Image.NEAREST)
for r in range(2):
    sheet.paste(big, (8 * S, 20 + r * 34 * S), big)
small.append(pic.convert("RGBA"))
for c, n in enumerate(names, 1):
    img = Image.open(GOLD / n)
    w, h = img.size
    px = img.tobytes()
    new = shade_c(shoes(px, w, h), w, h)
    for r, data in enumerate((px, new)):
        o = Image.frombytes("P", (w, h), data)
        o.putpalette(img.getpalette())
        o.info["transparency"] = 0
        rgba = o.convert("RGBA")
        b = rgba.resize((w * S, h * S), Image.NEAREST)
        sheet.paste(b, (c * 34 * S, 20 + r * 34 * S), b)
        if r == 1:
            o.save(W / n.replace("golden_", "shadeC_"), transparency=0)
            small.append(rgba)
x = 8
for sc in (1, 2):
    for im in small:
        t = im.resize((im.width * sc, im.height * sc), Image.NEAREST)
        sheet.paste(t, (x, 2 * 34 * S + 40), t)
        x += im.width * sc + 6
sheet.save(W / "shade_c_mock.png")
print("written shade_c_mock.png")
