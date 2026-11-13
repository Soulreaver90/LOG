# Review sheet for set 158 anim 9 (the GIF is transform_gif.py): old (gi_ssj) on top, new (gi_ssj_v2) below, placed by dx/dy.
import sys; print(r'promoted to scripts\permanent\gi_review.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json
from pathlib import Path
from PIL import Image, ImageDraw
ART = Path(__file__).resolve().parents[2]
S = 6
def frames(folder):
    man = json.loads((folder / "manifest.json").read_text())
    out = {}
    for e in man:
        for k in e["keys"]:
            if k["anim"] == 9 and k["dir"] == 0:
                out[k["index"]] = (Image.open(folder / e["png"]).convert("RGBA"), k["dy"])
    return [out[i] for i in sorted(out)]
rows = [frames(ART / "gi_ssj"), frames(ART / "gi_ssj_v2")]
sheet = Image.new("RGB", (4 * 40 * S, 2 * 40 * S + 20), (191, 255, 7))
gif = []
for r, fr in enumerate(rows):
    for i, (im, dy) in enumerate(fr):
        big = im.resize((32 * S, 32 * S), Image.NEAREST)
        sheet.paste(big, (i * 40 * S + 4 * S, 20 + r * 40 * S + (dy + 28) * S), big)
        if r == 1:
            g = Image.new("RGBA", (48 * S, 44 * S), (191, 255, 7, 255))
            g.paste(big, (8 * S, (dy + 30) * S), big)
            gif.append(g.convert("RGB"))
ImageDraw.Draw(sheet).text((4, 4), "set 158 anim 9 (SSJ to SSJ2 step), dir 0. Top: old. Bottom: new (golden SSJ2 head)", fill=(0, 0, 0))
sheet.save(ART / "anim" / "ssj_to_ssj2_step.png")
print("ok")
