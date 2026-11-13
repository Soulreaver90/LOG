# Review: candidate side heads at 12x next to SSJ side golden and set 58 side at 12x, plus all at 3x and 1x.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import from_txt, zoom
out = Path(sys.argv[1]); refs = [Image.open(G / "golden_gi_ssj_d2.png"), from_txt(G / "work/gi_ssj2_d2.txt"), Image.open(G / "golden_gi_ssj2_d0.png")]
cands = [from_txt(Path(p)) for p in sys.argv[2:]]
big = refs[:2] + cands
s = 12; W = sum(i.width * s + 16 for i in big); H = 20 * s + 32 * 3 + 20
c = Image.new("RGB", (max(W, 600), H), (150, 150, 150)); x = 0
for im in big:
    c.paste(zoom(im, s).crop((0, 0, im.width * s, 20 * s)), (x, 0)); x += im.width * s + 16
x = 0
for im in refs + cands:
    c.paste(zoom(im, 3), (x, 20 * s + 10)); c.paste(zoom(im, 1), (x + im.width * 3 + 4, 20 * s + 50)); x += im.width * 4 + 20
c.save(out)
