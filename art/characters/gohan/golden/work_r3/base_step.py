# Base to SSJ step (anim 9 of the base set, dir 0): armor set 56 (game) on top, gi set 157 below, placed by
# dx/dy at 6x like ssj_to_ssj2_step.png. GIFs use the same loop as transform_gif.py (frame 0 held, 1-3 x4).
import sys; print(r'promoted to scripts\permanent\gi_review.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json
from pathlib import Path
from PIL import Image, ImageDraw
ART = Path(__file__).resolve().parents[2]
ROOT = ART.parents[1]
S = 6
def seq(folder):
    man = json.loads((folder / "manifest.json").read_text())
    out = {}
    for e in man:
        for k in e.get("keys", [e]):
            if k["anim"] == 9 and k["dir"] == 0:
                out[k["index"]] = (Image.open(folder / e["png"]).convert("RGBA"), k)
    return [out[i] for i in sorted(out)]
rows = {"armor": seq(ROOT / "scratch" / "sprites" / "set56"), "gi": seq(ART / "gi_base")}
sheet = Image.new("RGB", (4 * 40 * S, 2 * 40 * S + 20), (191, 255, 7))
for r, (name, fr) in enumerate(rows.items()):
    gif = []
    for i, (im, k) in enumerate(fr):
        big = im.resize((im.width * S, im.height * S), Image.NEAREST)
        sheet.paste(big, (i * 40 * S + (k["dx"] + 12) * S, 20 + r * 40 * S + (k["dy"] + 28) * S), big)
        g = Image.new("RGBA", (48 * S, 44 * S), (191, 255, 7, 255))
        g.paste(big, ((k["dx"] + 16) * S, (k["dy"] + 34) * S), big)
        gif.append(g.convert("RGB"))
    loop = [gif[0]] * 2 + gif[1:] * 4
    loop[0].save(ART / "anim" / f"base_to_ssj_step_{name}.gif", save_all=True, append_images=loop[1:], duration=167, loop=0)
ImageDraw.Draw(sheet).text((4, 4), "base to SSJ step (anim 9), dir 0. Top: armor set 56 (game). Bottom: gi set 157", fill=(0, 0, 0))
sheet.save(ART / "anim" / "base_to_ssj_step.png")
print({n: len(f) for n, f in rows.items()})
