# Review sheet helper: sprites side by side at 10x with labels, plus a 1x and 2x strip.
# Background (191, 255, 7): no palette entry is within 32 steps per channel (owner 2026-10-18: never gray).
#   py -3 -I sheet.py out.png label=path.png [label=path.png ...]
import sys
from pathlib import Path
from PIL import Image, ImageDraw
BG = (191, 255, 7)


def sheet(out: Path, items: list, scale: int = 10) -> None:
    ims = [(t, Image.open(p).convert("RGBA")) for t, p in items]
    cw = max(im.width for _, im in ims) * scale + 2 * scale
    ch = max(im.height for _, im in ims) * scale
    s = Image.new("RGB", (len(ims) * cw + scale, ch + 130), BG)
    d = ImageDraw.Draw(s)
    x = 6
    for i, (t, im) in enumerate(ims):
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        s.paste(big, (scale + i * cw, 20), big)
        d.text((scale + i * cw, 4), t, fill=(0, 0, 0))
        s.paste(im, (x, ch + 60), im)
        two = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        s.paste(two, (x + im.width + 4, ch + 28), two)
        x += im.width * 3 + 16
    s.save(out)


if __name__ == "__main__":
    sheet(Path(sys.argv[1]), [a.split("=", 1) for a in sys.argv[2:]])
