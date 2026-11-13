"""Throwaway: render candidate portrait ids at 4x with labels, and list purple indices."""
import sys
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent")))
sys.path.insert(0, str(Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\patches")))
import gohan_portraits as gp
rom = gp.BASE.read_bytes()
obj, stat = gp.palette(rom, gp.OBJ_PAL), gp.palette(rom, gp.STATUS_PAL)
ids = [int(a) for a in sys.argv[1:]]
S = 4
sheet = Image.new("RGB", (len(ids) * (64 * S + 8) + 8, 64 * S + 28), (48, 48, 48))
d = ImageDraw.Draw(sheet)
for i, pid in enumerate(ids):
    px = gp.portrait(rom, pid)
    pal = stat if pid < 26 else obj
    img = gp._indexed(px, pal).convert("RGB").resize((64 * S, 64 * S), Image.NEAREST)
    sheet.paste(img, (8 + i * (64 * S + 8), 20))
    d.text((8 + i * (64 * S + 8), 4), str(pid), fill=(255, 255, 255))
    c = Counter(px)
    purp = [(k, pal[k], n) for k, n in c.most_common() if pal[k][2] > pal[k][1] + 40 and pal[k][0] > pal[k][1] - 10]
    print(pid, "purple/blue:", purp[:8])
sheet.save(Path(__file__).parent / "look.png")
