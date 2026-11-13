# Review for the aura: per anim (0, 1, 4, 13) and dir (0, 1, 2), each frame placed by dx/dy at 5x; also GIFs.
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
ART = Path(__file__).resolve().parents[2]
F = ART / "gi_ssj2_v3"
S = 5
man = json.loads((F / "manifest.json").read_text())
seq = {}
for e in man:
    for k in e["keys"]:
        if k["anim"] in (0, 1, 4, 13) and k["dir"] in (0, 1, 2):
            seq.setdefault((k["anim"], k["dir"]), []).append((k["index"], e["png"], k))
cell = 40 * S
cols = max(len(v) for v in seq.values())
keys = sorted(seq)
sheet = Image.new("RGB", (cols * cell + 120, len(keys) * cell), (191, 255, 7))
d = ImageDraw.Draw(sheet)
gifs = {}
for r, key in enumerate(keys):
    d.text((4, r * cell + 4), f"anim {key[0]} dir {key[1]}", fill=(0, 0, 0))
    for c, (i, png, k) in enumerate(sorted(seq[key], key=lambda t: t[0])):
        im = Image.open(F / png).convert("RGBA")
        if k["attr1"] & 0x1000:
            im = ImageOps.mirror(im)
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        x, y = 120 + c * cell + (k["dx"] + 12) * S, r * cell + (k["dy"] + 30) * S
        sheet.paste(big, (x, y), big)
        g = Image.new("RGBA", (cell, cell), (191, 255, 7, 255))
        g.paste(big, ((k["dx"] + 12) * S, (k["dy"] + 30) * S), big)
        gifs.setdefault(key, []).append(g.convert("RGB"))
sheet.save(ART / "anim" / "ssj2_aura.png")
for (a, dr), fr in gifs.items():
    fr[0].save(ART / "anim" / f"ssj2_aura_a{a:02d}_d{dr}.gif", save_all=True, append_images=fr[1:], duration=167, loop=0)
print({k: len(v) for k, v in sorted(seq.items())})
