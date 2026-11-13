# Carry-over sheet: per anim.dir.index key, 157 r12 | 157 r12fix | 158 now | 159 now at 6x on lime.
# "now" = r12fix output when the key is edited, else r12. Usage: py -3 -I carry_sheet.py out.png 5.0.2 8.0.3 ...
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import view  # noqa: E402
import fix  # noqa: E402
from edits import EDITS  # noqa: E402

LIME, SCALE, CELL = (191, 255, 7), 6, 6 * 32 + 10
pal = view.palette()
inv = fix.rgb_of(pal)


def grid(key, edited):
    if edited and key in EDITS:
        return fix.load_fix(key)
    return fix.frames(key, pal)[1]


rows = []
for k in sys.argv[2:]:
    cells = [("157 r12", grid("157." + k, False)), ("157 fix", grid("157." + k, True)),
             ("158", grid("158." + k, True)), ("159", grid("159." + k, True))]
    rows.append((k, cells))
sheet = Image.new("RGB", (60 + 4 * CELL, len(rows) * (CELL + 14)), LIME)
dr = ImageDraw.Draw(sheet)
for r, (k, cells) in enumerate(rows):
    y = r * (CELL + 14)
    dr.text((4, y + 20), k, fill=(0, 0, 0))
    for c, (label, g) in enumerate(cells):
        im = fix.to_image(g, inv)
        im = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
        sheet.paste(im, (60 + c * CELL, y + 14), im)
        dr.text((60 + c * CELL, y + 2), label, fill=(0, 0, 0))
sheet.save(sys.argv[1])
print(sys.argv[1], len(rows))
