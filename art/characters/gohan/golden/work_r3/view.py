# Review view: owner mockup | candidate at 12x, then SSJ golden, set 58 original and candidate at 3x and 1x.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import from_txt, zoom
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name("view.png")
cand = from_txt(Path(sys.argv[1]))
own = Image.open(G / "owner/owner_mock_ssj2_d0_1000.png").convert("RGB")
own = own.crop((76, 34 - 3 * 12, 76 + 32 * 11.8, 34 + 22 * 11.8)).resize((32 * 12, 25 * 12))
big = zoom(cand, 12).crop((0, 0, 32 * 12, 22 * 12))
small = [from_txt(G / "work/g_gi_ssj_d0.txt") if (G / "work/g_gi_ssj_d0.txt").exists() else Image.open(G / "golden_gi_ssj_d0.png"),
         from_txt(G / "work/gi_ssj2_d0.txt"), cand]
W = 32 * 12 * 2 + 60 + 3 * (32 * 3 + 20)
c = Image.new("RGB", (W, 25 * 12 + 10), (150, 150, 150))
c.paste(own, (10, 0)); c.paste(big, (32 * 12 + 30, 36))
x = 32 * 12 * 2 + 50
for im in small:
    z3 = zoom(im if im.mode == "P" else im, 3)
    c.paste(z3, (x, 10)); c.paste(zoom(im, 1), (x + 8, 130)); x += im.width * 3 + 20
c.save(OUT)
