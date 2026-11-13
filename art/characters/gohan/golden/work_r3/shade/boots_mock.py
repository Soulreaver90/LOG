# Throwaway mock: Piccolo-size shoes on a copy of golden base d0 (golden untouched). Rows 27-29: trouser hem
# row, then 2-row shoes with the toes turned out, like Piccolo set 104. Sheet: armor | Piccolo | now | mock.
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
ART = W.parents[2]
sys.path.insert(0, str(ART / "golden" / "work"))
import gold
SPR = ART.parents[1] / "scratch" / "sprites"
src = Image.open(ART / "golden" / "golden_gi_base_d0.png")
rows = gold.to_txt(src).splitlines()
rows[27] = "....xxxx.xxxx..."
rows[28] = "...KBbbBKBbbBK.."
rows[29] = "..KBbbBKKKBbbBK."
(W / "boots_base_d0.txt").write_text("\n".join(rows) + "\n", newline="\n")
mock = gold.from_txt(W / "boots_base_d0.txt")
mock.save(W / "boots_base_d0.png", transparency=0)
def idle(folder):
    for e in json.loads((folder / "manifest.json").read_text()):
        if (e["anim"], e["dir"], e["index"]) == (0, 0, 0):
            return Image.open(folder / e["png"])
S = 12
imgs = [("armor set 56", idle(SPR / "set56")), ("Piccolo set 104", idle(SPR / "set104")), ("gi now", src), ("gi mock", mock)]
sheet = Image.new("RGB", (len(imgs) * 18 * S, 34 * S + 20), (112, 112, 112))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(imgs):
    big = im.convert("RGBA").resize((im.width * S, im.height * S), Image.NEAREST)
    sheet.paste(big, (i * 18 * S + S, 20), big)
    d.text((i * 18 * S + S, 4), t, fill=(255, 255, 255))
sheet.save(W / "boots_mock.png")
print("ok")
