# Aura mix drafts (owner 2026-10-18 8:04 AM: mix of A "cross" and B "outline"; idle hook approved).
# Each shape = 1-2 short outline bolts every frame, plus one long cross bolt on every other shape.
# Idle: 3 shapes cycle every 4 game frames (the planned SSJ2 idle hook: index = body * 3 + (tick >> 2) % 3).
# Walk: one shape baked per walk frame; the game changes walk frames every 8 game frames (133 ms).
# Writes mix_idle_d0..d2.gif, mix_walk_d0..d2.gif, mix_sheet.png on lime. Mockup only, no ROM.
import json, random, sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
sys.path.insert(0, str(W))
from bolts import BG, apply, cross, outline
ART = W.parents[2]
GOLD = ART / "golden"
S = 6


def shape(rng, px, k):
    pat = outline(rng, px)
    pat = dict(list(pat.items())[: max(6, len(pat) * 2 // 3)])     # lighter than family B alone
    if k % 2 == 0:
        pat.update(cross(rng, px))
    return pat


def render(px, pal):
    o = Image.frombytes("P", (32, 32), px)
    o.putpalette(pal)
    g = Image.new("RGB", (32 * S, 32 * S), BG)
    mask = Image.frombytes("L", (32, 32), bytes(255 if v else 0 for v in px)).resize((32 * S, 32 * S))
    g.paste(o.convert("RGB").resize((32 * S, 32 * S), Image.NEAREST), (0, 0), mask)
    return g


def walk_frames(d):
    man = json.loads((ART / "gi_ssj2_v2" / "manifest.json").read_text())
    keys = {(k["anim"], k["dir"], k["index"]): (e["png"], k) for e in man for k in e["keys"]}
    out = []
    for i in range(4):
        png, k = keys[(1, d, i)]
        im = Image.open(ART / "gi_ssj2_v2" / png)
        canvas = Image.new("P", (32, 32), 0)
        canvas.putpalette(im.getpalette())
        canvas.paste(im, ((32 - im.width) // 2, 32 - im.height))
        out.append(canvas)
    return out


rng = random.Random(7)
sheet_rows = []
for d in (0, 1, 2):
    gold = Image.open(GOLD / f"golden_gi_ssj2_d{d}.png")
    pal = gold.getpalette()
    idle = [render(apply(gold.tobytes(), shape(rng, gold.tobytes(), k), pal), pal) for k in range(3)]
    idle[0].save(W / f"mix_idle_d{d}.gif", save_all=True, append_images=idle[1:] * 4 + idle, duration=67, loop=0)
    walk = []
    for k, fr in enumerate(walk_frames(d)):
        walk.append(render(apply(fr.tobytes(), shape(rng, fr.tobytes(), k), pal), pal))
    walk[0].save(W / f"mix_walk_d{d}.gif", save_all=True, append_images=walk[1:], duration=133, loop=0)
    sheet_rows.append(idle + walk)
sheet = Image.new("RGB", (7 * 34 * S + S, 3 * 34 * S + 20), BG)
ImageDraw.Draw(sheet).text((4, 4), "Aura mix: idle shapes 1-3 (cycle every 67 ms) | walk frames 0-3 (133 ms); rows front, back, side", fill=(0, 0, 0))
for r, row in enumerate(sheet_rows):
    for c, img in enumerate(row):
        sheet.paste(img, (S + c * 34 * S, 20 + r * 34 * S))
sheet.save(W / "mix_sheet.png")
print("ok")
