# Sheet of ROM frames (rom_sheet --frames output) for chosen anims: one row per set.anim.dir, 6x on lime.
# Usage: py -3 -I romsheet.py <frames dir> <out.png> set.anim[,anim...] ...
import sys
from pathlib import Path
from PIL import Image, ImageDraw

LIME, SCALE = (191, 255, 7), 6
src, out = Path(sys.argv[1]), Path(sys.argv[2])
rows = []
for spec in sys.argv[3:]:
    s, anims = spec.split(".")
    for a in map(int, anims.split(",")):
        for d in range(4):
            cells = sorted(src.glob(f"{s}_a{a:02d}_d{d}_i*.png"))
            cells = [c for c in cells if not c.stem.endswith("_3x")]
            if cells:
                rows.append((f"{s}.{a}.{d}", [Image.open(c).convert("RGBA") for c in cells]))
cw = SCALE * 32 + 8
W = 90 + cw * max(len(c) for _, c in rows)
H = (SCALE * 32 + 8) * len(rows)
sheet = Image.new("RGB", (W, H), LIME)
dr = ImageDraw.Draw(sheet)
for r, (label, cells) in enumerate(rows):
    y = r * (SCALE * 32 + 8)
    dr.text((4, y + 4), label, fill=(0, 0, 0))
    for k, im in enumerate(cells):
        big = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
        sheet.paste(big, (90 + k * cw, y), big)
        dr.text((90 + k * cw, y), str(k), fill=(0, 0, 0))
sheet.save(out)
print(out, len(rows), "rows")
