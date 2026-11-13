# Big review: owner mockup and candidate heads at 12x (rows 0-20), plus set 58 / SSJ / candidates at 4x.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import from_txt, zoom
out = Path(sys.argv[1]); cands = [from_txt(Path(p)) for p in sys.argv[2:]]
own = Image.open(G / "owner/owner_mock_ssj2_d0_1000.png").convert("RGB")
s = 12; top = 3
own = own.crop((76, 34 - top * 11.8, 76 + 32 * 11.8, 34 + 21 * 11.8)).resize((32 * s, (21 + top) * s), Image.NEAREST)
tiles = [own] + [Image.new("RGB", (32 * s, (21 + top) * s), (150, 150, 150)) for _ in cands]
for t, c in zip(tiles[1:], cands):
    t.paste(zoom(c, s).crop((0, 0, 32 * s, 21 * s)), (0, top * s))
small = [Image.open(G / "golden_gi_ssj_d0.png"), from_txt(G / "work/gi_ssj2_d0.txt")] + cands
W = len(tiles) * (32 * s + 10); H = (21 + top) * s + 32 * 4 + 20
c = Image.new("RGB", (W, H), (150, 150, 150))
for i, t in enumerate(tiles):
    c.paste(t, (i * (32 * s + 10), 0))
x = 0
for im in small:
    c.paste(zoom(im, 4), (x, (21 + top) * s + 10)); c.paste(zoom(im, 1), (x + im.width * 4 + 4, (21 + top) * s + 60)); x += im.width * 4 + 50
c.save(out)
