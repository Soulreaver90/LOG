# Throwaway mock: Piccolo-style gi shading on copies of the golden frames (goldens are not touched).
# Rule A: every gi pixel (88, 89) becomes the base 89; in each horizontal run of gi pixels the centre
# pixel (two for runs of 6+) becomes the lit 88. Flash variant (transformation lighting): lit 88 -> 87,
# base 89 next to a lit pixel -> 88.
import json
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
ART = W.parents[2]
GOLD = ART / "golden"
GI, BASE, LIT, FLASH_LIT = {88, 89}, 89, 88, 87


def shade(px, w, h, flash=False):
    out = bytearray(px)
    for y in range(h):
        x = 0
        while x < w:
            if px[y * w + x] in GI:
                s = x
                while x < w and px[y * w + x] in GI:
                    x += 1
                n = x - s
                lit = set()
                if n >= 3:
                    lit = {s + (n - 1) // 2} | ({s + n // 2} if n >= 6 else set())
                for i in range(s, x):
                    out[y * w + i] = LIT if i in lit else BASE
                if flash:
                    for i in range(s, x):
                        if i in lit:
                            out[y * w + i] = FLASH_LIT
                        elif (i - 1 in lit or i + 1 in lit):
                            out[y * w + i] = LIT
            else:
                x += 1
    return bytes(out)


S = 8
names = [f"golden_gi_{f}_d{d}.png" for f in ("base", "ssj", "ssj2") for d in (0, 2, 1)]
m = json.loads((ART.parents[1] / "scratch" / "sprites" / "set104" / "manifest.json").read_text())
pic = [e for e in m if (e["anim"], e["dir"], e["index"]) == (0, 0, 0)][0]
picimg = Image.open(ART.parents[1] / "scratch" / "sprites" / "set104" / pic["png"])
cols = 1 + len(names)
sheet = Image.new("RGB", (cols * 34 * S, 3 * 34 * S + 30), (112, 112, 112))
d = ImageDraw.Draw(sheet)
d.text((4, 4), "Row 1: now (flat). Row 2: Piccolo-style shading. Row 3: transformation flash. Col 1: Piccolo set 104", fill=(255, 255, 255))
for r in range(3):
    sheet.paste(picimg.convert("RGBA").resize((16 * S, 32 * S), Image.NEAREST), (8 * S, 20 + r * 34 * S), picimg.convert("RGBA").resize((16 * S, 32 * S), Image.NEAREST))
for c, n in enumerate(names, 1):
    img = Image.open(GOLD / n)
    px = img.tobytes()
    w, h = img.size
    for r, data in enumerate((px, shade(px, w, h), shade(px, w, h, flash=True))):
        o = Image.frombytes("P", (w, h), data)
        o.putpalette(img.getpalette())
        o.info["transparency"] = 0
        big = o.convert("RGBA").resize((w * S, h * S), Image.NEAREST)
        sheet.paste(big, (c * 34 * S, 20 + r * 34 * S), big)
        if r == 1:
            o.save(W / n.replace("golden_", "shadeA_"), transparency=0)
sheet.save(W / "shade_mock_A.png")
print("ok")
