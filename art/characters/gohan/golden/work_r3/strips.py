# Review strips: per animation, each direction row shows old gi_ssj2 over new gi_ssj2_v2 frames at 3x,
# drawn in sprite space from each key's dx/dy (so a geometry error shows as a jump). Flagged frames get a red box.
import sys; print(r'promoted to scripts\permanent\gi_review.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json
from pathlib import Path
from PIL import Image, ImageDraw
ART = Path(__file__).resolve().parents[2]
OUT = ART / "gi_ssj2_v2" / "review"; OUT.mkdir(exist_ok=True)
S, CW, CH, OX, OY = 3, 48, 44, 24, 36


def load(folder):
    man = json.loads((folder / "manifest.json").read_text()); keys = {}
    for e in man:
        for k in e["keys"]:
            keys[k["anim"], k["dir"], k["index"]] = (folder / e["png"], k)
    return keys


old, new = load(ART / "gi_ssj2"), load(ART / "gi_ssj2_v2")
flags = {r["png"]: r["status"] for r in json.loads((ART / "gi_ssj2_v2/transplant.json").read_text())}


def cell(path, k):
    im = Image.open(path).convert("RGBA")
    if k["attr1"] & 0x1000:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    c = Image.new("RGBA", (CW, CH), (150, 150, 150, 255)); c.alpha_composite(im, (OX + k["dx"], OY + k["dy"]))
    return c.resize((CW * S, CH * S), Image.NEAREST)


for a in sorted({k[0] for k in old}):
    dirs = sorted({k[1] for k in old if k[0] == a}); n = max(k[2] for k in old if k[0] == a) + 1
    sheet = Image.new("RGB", (n * (CW * S + 6) + 40, len(dirs) * (2 * CH * S + 16) + 20), (191, 255, 7)); d = ImageDraw.Draw(sheet)
    d.text((4, 4), f"anim {a}: per direction, top = old, bottom = new (red box = flagged, yellow = shifted)", fill=(0, 0, 0))
    for r, dr in enumerate(dirs):
        y = 20 + r * (2 * CH * S + 16); d.text((4, y + 4), f"d{dr}", fill=(0, 0, 0))
        for i in range(n):
            if (a, dr, i) not in old:
                continue
            x = 40 + i * (CW * S + 6)
            sheet.paste(cell(*old[a, dr, i]), (x, y)); sheet.paste(cell(*new[a, dr, i]), (x, y + CH * S + 4))
            st = flags.get(new[a, dr, i][0].name, "")
            if st.startswith("flag") or "shift" in st:
                d.rectangle((x, y + CH * S + 4, x + CW * S - 1, y + 2 * CH * S + 3), outline=(255, 0, 0) if st.startswith("flag") else (255, 220, 0), width=2)
    sheet.save(OUT / f"a{a:02d}.png")
print(sorted(p.name for p in OUT.glob("*.png")))
