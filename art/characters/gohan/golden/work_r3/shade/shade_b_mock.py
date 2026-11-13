# Throwaway mock: rule B = the old flash row as everyday shading (base 89, beside the lit stripe 88, stripe 87),
# plus a transformation flash one step brighter (beside 87, stripe 86), with the shoe rule, on copies of all 9
# golden views (goldens untouched).
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
GOLD = W.parents[1]
sys.path.insert(0, str(W))
import shade_mock as A                                        # noqa: E402  (prints its own "ok")
from shoes_shade_mock import shoes                            # noqa: E402


def shade_b(px, w, h, stripe=87, side=88):
    flat = A.shade(px, w, h)                                  # rule A: 89 base, 88 centre stripe
    out = bytearray(flat)
    for i, v in enumerate(flat):
        if v == A.LIT:
            out[i] = stripe
    for i, v in enumerate(flat):
        x = i % w
        if v == A.BASE and ((x > 0 and flat[i - 1] == A.LIT) or (x < w - 1 and flat[i + 1] == A.LIT)):
            out[i] = side
    return bytes(out)


S = 8
names = [f"golden_gi_{f}_d{d}.png" for f in ("base", "ssj", "ssj2") for d in (0, 2, 1)]
sheet = Image.new("RGB", (len(names) * 34 * S, 3 * 34 * S + 30), (112, 112, 112))
ImageDraw.Draw(sheet).text((4, 4), "Row 1: rule A + shoes. Row 2: rule B + shoes (everyday). Row 3: rule B transformation flash", fill=(255, 255, 255))
for c, n in enumerate(names):
    img = Image.open(GOLD / n)
    w, h = img.size
    px = shoes(img.tobytes(), w, h)
    for r, data in enumerate((A.shade(px, w, h), shade_b(px, w, h), shade_b(px, w, h, 86, 87))):
        o = Image.frombytes("P", (w, h), data)
        o.putpalette(img.getpalette())
        big = o.convert("RGB").resize((w * S, h * S), Image.NEAREST)
        mask = Image.frombytes("L", (w, h), bytes(255 if v else 0 for v in data)).resize((w * S, h * S), Image.NEAREST)
        sheet.paste(big, (c * 34 * S, 20 + r * 34 * S), mask)
sheet.save(W / "shade_b_mock.png")
print("written shade_b_mock.png")
