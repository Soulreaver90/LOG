# Throwaway mock: rounded upper torso on copies of the base goldens (front d0, back d1), then the shoe rule and
# shading rule C. Rows 19-20: the torso outline moves out 1 px each side over the arm's inner pixel, so the torso
# reads narrow at the shoulders, full at the chest or lats, narrow at the waist (armor set 56 back: 9, 11, 13 px).
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
GOLD = W.parents[1]
SPR = W.parents[3] / "sprites"
sys.path.insert(0, str(W))
from shoes_shade_mock import shoes                             # noqa: E402
from shade_c_mock import shade_c                               # noqa: E402
OUTLINE, GI = 211, 89


def round_torso(px, w, rows=(19, 20)):
    out = bytearray(px)
    for y in rows:
        xs = [x for x in range(w) if px[y * w + x] == OUTLINE]
        if len(xs) < 2:
            continue
        l, r = min(xs), max(xs)                                # torso outline columns on this row
        for edge, out_x in ((l, l - 1), (r, r + 1)):
            if 0 <= out_x < w and px[y * w + out_x] not in (0, OUTLINE):
                out[y * w + out_x] = OUTLINE                   # outline moves over the arm's inner pixel
                out[y * w + edge] = GI                         # old outline becomes gi
    return bytes(out)


S = 10
pal = Image.open(GOLD / "golden_gi_base_d0.png").getpalette()
def img_of(data, w, h):
    o = Image.frombytes("P", (w, h), data); o.putpalette(pal); o.info["transparency"] = 0
    return o.convert("RGBA")
def spr(s, d):
    import json
    for e in json.loads((SPR / s / "manifest.json").read_text()):
        if (e["anim"], e["dir"], e["index"]) == (0, d, 0):
            return Image.open(SPR / s / e["png"]).convert("RGBA")
cols = []
for d in (0, 1):
    src = Image.open(GOLD / f"golden_gi_base_d{d}.png")
    w, h = src.size
    px = src.tobytes()
    flat = shade_c(shoes(px, w, h), w, h)
    rnd = shade_c(shoes(round_torso(px, w), w, h), w, h)
    cols += [(f"armor d{d}", spr("set56", d)), (f"rule C d{d}", img_of(flat, w, h)), (f"rule C + round d{d}", img_of(rnd, w, h))]
    Image.frombytes("P", (w, h), rnd).save(W / f"round_base_d{d}.png") if False else None
sheet = Image.new("RGB", (len(cols) * 18 * S, 34 * S + 80), (112, 112, 112))
d = ImageDraw.Draw(sheet)
x = 4
for i, (t, im) in enumerate(cols):
    sheet.paste(im.resize((im.width * S, im.height * S), Image.NEAREST), (i * 18 * S + S, 20), im.resize((im.width * S, im.height * S), Image.NEAREST))
    d.text((i * 18 * S + S, 4), t, fill=(255, 255, 255))
    sheet.paste(im, (x, 34 * S + 30), im); sheet.paste(im.resize((32, 64), Image.NEAREST), (x + 20, 34 * S + 14), im.resize((32, 64), Image.NEAREST))
    x += 60
sheet.save(W / "round_mock.png")
print("written round_mock.png")
