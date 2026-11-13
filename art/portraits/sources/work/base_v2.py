"""Throwaway mockup: base gi portrait from teen face 59, Piccolo purple (96 base, 97 shade, 233 light),
and gi SSJ2 recolored from International blue-violet to the same indices. Writes work/*.png only."""
import sys
from collections import Counter
from pathlib import Path
from PIL import Image
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")
import gohan_portraits as gp
W = Path(__file__).parent
rom = gp.BASE.read_bytes()
obj, stat = gp.palette(rom, gp.OBJ_PAL), gp.palette(rom, gp.STATUS_PAL)
GI, SHADE, LIGHT, EDGE = 97, 97, 233, 1
SKIN, SKIN_L, SKIN_D, SKIN_LINE = 115, 114, 116, 35
NECK = {114, 115, 116, 35}

# ===== base gi from 59 =====
px = bytearray(gp.portrait(rom, 59))
at = lambda x, y: px[y * 64 + x]
def put(x, y, k): px[y * 64 + x] = k
SIL = {50: (18, 43), 51: (15, 46), 52: (12, 49), 53: (9, 52), 54: (7, 54), 55: (5, 56), 56: (4, 58), 57: (3, 59)}
SIL.update({y: (3, 60) for y in (58, 59, 60)})
VHALF = {53: 8, 54: 8, 55: 7, 56: 6, 57: 5, 58: 4, 59: 3, 60: 2}   # chest skin half width around x31
bg_row = [at(x, 47) for x in range(64)]
for y in range(48, 61):
    lo, hi = SIL.get(y, (99, -1))
    for x in range(3, 61):
        inside = lo <= x <= hi
        neck = y <= 52 and 21 <= x <= 41 and at(x, y) in NECK
        vee = y in VHALF and abs(x - 31) <= VHALF[y]
        if not inside:
            if at(x, y) not in NECK or not (21 <= x <= 41):
                put(x, y, bg_row[x] if bg_row[x] in (74, 75) else 75)
        elif neck:
            pass
        elif vee:
            d = abs(x - 31)
            put(x, y, SKIN_LINE if d == VHALF[y] else SKIN_D if x > 31 and d >= VHALF[y] - 1 else SKIN)
        else:
            edge = x in (lo, hi) or y == 50 or (y - 1) in SIL and not (SIL[y - 1][0] <= x <= SIL[y - 1][1])
            lapel = y in VHALF and abs(x - 31) == VHALF[y] + 1
            if edge:
                put(x, y, EDGE)
            elif lapel:
                put(x, y, SHADE)
            elif (y - 1) in SIL and (x - 1 in (SIL[y - 1][0], ) or x + 1 == SIL[y - 1][1] + 0) and y <= 56:
                put(x, y, LIGHT)
            elif y >= 58 or x <= 6 or x >= 57:
                put(x, y, SHADE)
            else:
                put(x, y, GI)
# shoulder highlight: the pixel under each top edge pixel
for y in range(51, 58):
    lo, hi = SIL[y]
    plo, phi = SIL[y - 1]
    for x in list(range(lo + 1, plo + 1)) + list(range(phi, hi)):
        if at(x, y) == GI or at(x, y) == SHADE:
            put(x, y, LIGHT)
base = bytes(px)

# ===== gi SSJ2 recolor =====
ssj2 = bytearray(Image.open(gp.ART / "gi_ssj2_dialog.png").tobytes())
where215 = Counter((i % 64 // 8, i // 64 // 8) for i, k in enumerate(ssj2) if k == 215)
ssj2 = bytes({80: 97, 215: 1}.get(k, k) for k in ssj2)
ssj = bytes({96: 97}.get(k, k) for k in Image.open(gp.ART / 'gi_ssj_dialog.png').tobytes())
print("215 cells (x8,y8):", dict(where215))

# ===== status twins via the patch's own pairing =====
for name, d in (("base", base), ("ssj2", ssj2), ("ssj", ssj)):
    dialog, status, rep = gp.convert(rom, [obj[k] for k in d])
    assert dialog == d or print(name, "dialog index drift", sum(a != b for a, b in zip(dialog, d)))
    gp._indexed(d, obj).save(W / f"gi_{name}_dialog_v2.png")
    gp._indexed(status, stat).save(W / f"gi_{name}_status_v2.png")
    print(name, "status err max", max(c["status_err"] for c in rep))

# ===== v3: Piccolo-style lit folds on the base gi, SSJ2 variant B with lit planes =====
b = bytearray(base)
FOLDS = [(13, 54), (14, 55), (15, 56), (16, 57), (17, 58), (18, 59), (19, 60),      # viewer-left fold
         (49, 54), (48, 55), (47, 56), (46, 57), (45, 58), (44, 59), (43, 60),      # viewer-right fold
         (9, 57), (10, 58), (11, 59), (12, 60)]
for x, y in FOLDS:
    if b[y * 64 + x] == 97:
        b[y * 64 + x] = 233
base3 = bytes(b)
ssj2b = bytes({80: 233, 215: 97}.get(k, k) for k in Image.open(gp.ART / "gi_ssj2_dialog.png").tobytes())
out = {}
for name, d in (("base", base3), ("ssj2A", ssj2), ("ssj2B", ssj2b), ("ssj", ssj)):
    dialog, status, rep = gp.convert(rom, [obj[k] for k in d])
    assert dialog == d
    gp._indexed(d, obj).save(W / f"gi_{name}_dialog_v3.png")
    gp._indexed(status, stat).save(W / f"gi_{name}_status_v3.png")
    out[name] = (gp._indexed(d, obj), gp._indexed(status, stat))

from PIL import ImageDraw
S, P, L = 4, 10, 18
cols = [("Piccolo (game)", gp._indexed(gp.portrait(rom, 94), obj), gp._indexed(gp.portrait(rom, 18), stat)),
        ("Base gi NEW", *out["base"]), ("Base now (armor)", gp._indexed(gp.portrait(rom, 59), obj), gp._indexed(gp.portrait(rom, 10), stat)),
        ("SSJ gi", *out["ssj"]), ("SSJ2 gi A (dark)", *out["ssj2A"]), ("SSJ2 gi B (lit)", *out["ssj2B"])]
sheet = Image.new("RGB", (len(cols) * (64 * S + P) + P, 2 * (64 * S + L + P) + P + L), (40, 40, 40))
d = ImageDraw.Draw(sheet)
d.text((P, 4), "Row 1: dialog (OBJ palette). Row 2: status screen (BG palette). Gi = Piccolo's 97 / 233 / black.", fill=(255, 255, 255))
for i, (t, dl, st) in enumerate(cols):
    x = P + i * (64 * S + P)
    for r, img in enumerate((dl, st)):
        y = L + P + r * (64 * S + L + P)
        d.text((x, y), t, fill=(255, 255, 255))
        sheet.paste(img.convert("RGB").resize((64 * S, 64 * S), Image.NEAREST), (x, y + L))
sheet.save(W.parent.parent / "portraits_gi_review_v3.png")
print("sheet written")
