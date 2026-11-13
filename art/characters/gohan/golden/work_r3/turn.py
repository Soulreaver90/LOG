# Turn review: SSJ2 front, side, back, mirrored side at 10x, then the SSJ and SSJ2 turns at 3x and 1x.
import sys
from pathlib import Path
from PIL import Image, ImageDraw
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import zoom
BACK = G / (sys.argv[1] if len(sys.argv) > 1 else "ssj2_back_v2.png")
ss2 = [Image.open(G / "golden_gi_ssj2_d0.png"), Image.open(G / "golden_gi_ssj2_d2.png"), Image.open(BACK), Image.open(G / "golden_gi_ssj2_d3.png")]
names = ["front (owner, approved)", "side (owner, approved)", "back (" + BACK.stem + ", pending)", "side mirrored (dir 3)"]
ssj = [Image.open(G / f"golden_gi_ssj_d{d}.png") for d in (0, 2, 1, 3)]
c = Image.new("RGB", (4 * (32 * 10 + 20) + 20, 32 * 10 + 32 * 3 + 90), (150, 150, 150)); d = ImageDraw.Draw(c)
for i, (n, im) in enumerate(zip(names, ss2)):
    x = 10 + i * (32 * 10 + 20); d.text((x, 2), n, fill=(0, 0, 0)); c.paste(zoom(im, 10), (x, 16))
y = 32 * 10 + 30; d.text((10, y - 12), "turn at 3x and 1x: SSJ golden, then SSJ2", fill=(0, 0, 0)); x = 10
for im in ssj:
    c.paste(zoom(im, 3), (x, y)); x += im.width * 3 + 10
x += 30
for im in ss2:
    c.paste(zoom(im, 3), (x, y)); x += im.width * 3 + 10
x = 10
for im in ssj + ss2:
    c.paste(zoom(im, 1), (x, y + 100)); x += im.width + 6
c.save(G / "ssj2_turn_review.png")
