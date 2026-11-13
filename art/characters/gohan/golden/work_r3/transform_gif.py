# GIF of the SSJ to SSJ2 step only: set 158 anim 9, dir 0: frame 0 held, then frames 1-3 cycle 4 times,
# each frame placed by dx/dy at 6x.
import sys; print(r'promoted to scripts\permanent\gi_review.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
S = 6
def seq(folder, anim):
    man = json.loads((ART / folder / "manifest.json").read_text())
    out = {}
    for e in man:
        for k in e["keys"]:
            if k["anim"] == anim and k["dir"] == 0:
                out[k["index"]] = (Image.open(ART / folder / e["png"]).convert("RGBA"), k)
    return [out[i] for i in sorted(out)]
step = seq("gi_ssj_v2", 9)
frames = [step[0]] * 2 + step[1:] * 4                      # start pose held, then the flash frames cycle
gif = []
for im, k in frames:
    big = im.resize((im.width * S, im.height * S), Image.NEAREST)
    g = Image.new("RGBA", (48 * S, 44 * S), (191, 255, 7, 255))
    g.paste(big, ((k["dx"] + 16) * S, (k["dy"] + 34) * S), big)
    gif.append(g.convert("RGB"))
gif[0].save(ART / "anim" / "ssj_to_ssj2_step.gif", save_all=True, append_images=gif[1:], duration=167, loop=0)
print(len(gif), "frames")
