"""Throwaway: side-by-side 4x of ROM ids and portrait PNGs."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")
sys.path.insert(0, r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")
import gohan_portraits as gp
rom = gp.BASE.read_bytes()
obj, stat = gp.palette(rom, gp.OBJ_PAL), gp.palette(rom, gp.STATUS_PAL)
out, items = sys.argv[1], sys.argv[2:]
S = 4
sheet = Image.new("RGB", (len(items) * (64 * S + 8) + 8, 64 * S + 28), (48, 48, 48))
d = ImageDraw.Draw(sheet)
for i, it in enumerate(items):
    if it.isdigit():
        pid = int(it); img = gp._indexed(gp.portrait(rom, pid), stat if pid < 26 else obj)
    else:
        img = Image.open(it)
    sheet.paste(img.convert("RGB").resize((64 * S, 64 * S), Image.NEAREST), (8 + i * (64 * S + 8), 20))
    d.text((8 + i * (64 * S + 8), 4), Path(it).stem, fill=(255, 255, 255))
sheet.save(out)
