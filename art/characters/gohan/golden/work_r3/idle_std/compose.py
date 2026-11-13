# SSJ2 standard idle mockup (owner 2026-10-18 12:40 PM): the SSJ2 golden head on the standard SSJ golden idle body,
# to compare with the SSJ2 power-pose idle. Head = rows 0..HEAD_END of the SSJ2 golden, aligned by the iris (64/65).
# Writes ssj2_std_d0..d3.png and compare.png (lime). Mockup only; goldens untouched.
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
G = W.parents[1]
BG, S = (191, 255, 7), 8


def iris(px):
    pts = [(i % 32, i // 32) for i, v in enumerate(px) if v in (64, 65)]
    return (min(p[0] for p in pts), min(p[1] for p in pts)) if pts else None


def neck_row(px):
    """First row below the face where the gi or a strap starts (the body begins there)."""
    for y in range(12, 32):
        if any(px[y * 32 + x] in (88, 89, 211, 87) for x in range(32)):
            return y
    return 17


out = {}
for d in (0, 1, 2):
    narrow, head = Image.open(G / f"golden_gi_ssj_d{d}.png"), Image.open(G / f"golden_gi_ssj2_d{d}.png")
    body = Image.new("P", (32, 32), 0)                      # 16x32 records sit at dx 0, 32x32 at dx -8: pad by 8
    body.putpalette(narrow.getpalette())
    body.paste(narrow, (8, 0))
    body.info["transparency"] = 0
    pb, ph = body.tobytes(), head.tobytes()
    ib, ih = iris(pb), iris(ph)
    dx, dy = (ib[0] - ih[0], ib[1] - ih[1]) if ib and ih else (0, 0)       # back view: no eyes, no shift
    cut_b, cut_h = neck_row(pb), neck_row(ph)
    px = bytearray(pb)
    keep_from = cut_h + dy                                                  # SSJ chin and neck below the new head stay
    for y in range(keep_from):                                              # clear the SSJ head
        for x in range(32):
            px[y * 32 + x] = 0
    for y in range(cut_h):                                                  # SSJ2 head, shifted onto the body
        for x in range(32):
            v = ph[y * 32 + x]
            ty, tx = y + dy, x + dx
            if v and 0 <= tx < 32 and 0 <= ty < 32 and (ty < keep_from or px[ty * 32 + tx] == 0):
                px[ty * 32 + tx] = v
    im = Image.frombytes("P", (32, 32), bytes(px)); im.putpalette(body.getpalette()); im.info["transparency"] = 0
    im.save(W / f"ssj2_std_d{d}.png", transparency=0)
    out[d] = (body, im, head)
    print(f"d{d}: shift ({dx},{dy}) neck rows body {cut_b} head {cut_h}")
ImageOps = __import__("PIL.ImageOps", fromlist=["mirror"])
d3 = ImageOps.mirror(out[2][1]); d3.save(W / "ssj2_std_d3.png", transparency=0)
sheet = Image.new("RGB", (3 * 34 * S + S, 3 * 34 * S + 24), BG)
dr = ImageDraw.Draw(sheet)
dr.text((4, 4), "columns: SSJ idle | SSJ2 head on SSJ idle body (new) | SSJ2 power pose (current); rows front, back, side", fill=(0, 0, 0))
for r, d in enumerate((0, 1, 2)):
    for c, im in enumerate(out[d]):
        big = im.convert("RGBA").resize((32 * S, 32 * S), Image.NEAREST)
        sheet.paste(big, (S + c * 34 * S, 24 + r * 34 * S), big)
sheet.save(W / "compare.png")
