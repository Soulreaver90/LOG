# throwaway: golden PNGs, lightning variants, checks and the golden sheet (scratch\art\golden\golden_sheet.png).
import sys
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
G = W.parent
L = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG")
sys.path.insert(0, str(L / "scripts" / "permanent"))
sys.path.insert(0, str(W))
import gold
import gi_art as g

FORMS = {"gi_base": ("Base", "set56"), "gi_ssj": ("Super Saiyan", "set59"), "gi_ssj2": ("Super Saiyan 2", "set58")}
FINAL = {("gi_base", d): f"g_gi_base_d{d}.txt" for d in range(3)}
FINAL.update({("gi_ssj", d): f"g_gi_ssj_d{d}.txt" for d in range(3)})
FINAL.update({("gi_ssj2", d): f"head_d{d}.txt" for d in range(3)})


def bolt(points):
    return {(x, y): c for x, y, c in points}


LEFT_BOLT = [(4, 12, "s"), (3, 13, "s"), (2, 14, "W"), (3, 15, "s"), (4, 16, "s"), (3, 17, "s"), (2, 18, "W"),
             (3, 19, "s"), (4, 20, "s"), (3, 21, "s")]
PATTERNS = {
    "bolts": bolt(LEFT_BOLT + [(30 - x, y + 2, c) for x, y, c in LEFT_BOLT]),
    "crackle": bolt([(3, 2, "s"), (4, 3, "W"), (5, 3, "s"), (4, 4, "s"), (28, 14, "s"), (27, 15, "W"), (28, 16, "s"),
                     (5, 27, "s"), (6, 26, "W"), (7, 27, "s"), (25, 25, "s"), (26, 24, "W"), (26, 26, "s"),
                     (27, 6, "s"), (28, 7, "W"), (29, 6, "s")]),
    "arcs": bolt([(5, 17, "s"), (4, 18, "s"), (5, 19, "W"), (4, 20, "s"), (6, 21, "s"), (7, 22, "s"),
                  (26, 17, "s"), (27, 18, "s"), (26, 19, "W"), (27, 20, "s"), (25, 21, "s"), (24, 22, "s"),
                  (10, 30, "."), (11, 25, "s"), (10, 26, "W"), (11, 27, "s"), (20, 25, "s"), (21, 26, "W"),
                  (20, 27, "s")]),
}


def rec_of(form, d):
    return gold.rec(L / "scratch/art" / form, d)[1]


def place(img, rec):
    return g.image_pixels(img, rec)


def checks(form, d, img, rec):
    px = place(img, rec)
    orig = g.frame_pixels(g.by_key(g.SPRITES / FORMS[form][1])[(0, d, 0)])
    mask = g.head_mask(px)
    old = None
    if form == "gi_ssj2":
        om = g.head_mask(orig)
        old = {p for p in om if p[1] <= g.chin_of(orig, om)[1]}
    keep = set().union(set(), *g.floating(orig)) | g.swoosh(orig)
    c = g.frame_checks(px, mask, orig, rec, (0, d, 0), keep, old)
    sash_rows = {y for (x, y), v in px.items() if v in (26, 27)}
    brows = {v for p, v in px.items() if p in mask and v in g.HAIR_BLACK and any(px.get(q) in g.SKIN for q in g.neighbours(p, True))}
    return c, sorted(sash_rows), brows


def cell(img, rec, s, box=True):
    """Object space x -8..23, y -24..7 (the 32x32 slot) at s x on grey, with the slot box drawn faintly."""
    out = Image.new("RGB", (32 * s, 32 * s), (150, 150, 150))
    d = ImageDraw.Draw(out)
    pal = gold.PAL
    for (x, y), v in place(img, rec).items():
        X, Y = (x + 8) * s, (y + 24) * s
        d.rectangle((X, Y, X + s - 1, Y + s - 1), fill=tuple(pal[3 * v:3 * v + 3]))
    if box:
        d.rectangle((0, 0, 32 * s - 1, 32 * s - 1), outline=(175, 175, 175))
    return out


if __name__ == "__main__":
    s = 10
    gold_imgs, report = {}, []
    for (form, d), txt in FINAL.items():
        img = gold.from_txt(W / txt)
        rec = rec_of(form, d)
        start = gold.rec(L / "scratch/art" / form, d)[0]
        assert img.size == start.size, (form, d, img.size, start.size)
        gold_imgs[(form, d)] = img
        for dd, flip in ((d, False), (3, True)) if d == 2 else ((d, False),):
            out = img.transpose(Image.FLIP_LEFT_RIGHT) if flip else img
            out.save(G / f"golden_{form}_d{dd}.png", transparency=0)
        c, sash, brows = checks(form, d, img, rec)
        bad = [k for k in ("light", "lost", "edge_hair") if c.get(k)] + (["chest"] if c.get("chest_ok") is False else [])
        report.append(f"{form} d{d}: size {img.size}, checks {c}, sash rows {sash}, black brows {sorted(brows)}, fail {bad}")
    # lightning variants on the Super Saiyan 2 front golden frame
    base = gold_imgs[("gi_ssj2", 0)]
    variants = {}
    for name, pat in PATTERNS.items():
        v = base.copy()
        for (x, y), ch in pat.items():
            if ch != "." and v.getpixel((x, y)) == 0:
                v.putpixel((x, y), gold.IX[ch])
        v.save(G / f"golden_gi_ssj2_d0_lightning_{name}.png", transparency=0)
        variants[name] = v
    # the sheet
    cw = 32 * s
    pad, lab = 12, 18
    rows_h = 32 * s + lab + pad
    width = 4 * (2 * cw + 3 * pad) + 160
    head_h = 18 * s + lab + pad
    sheet = Image.new("RGB", (width, 5 * rows_h + head_h + 60), (120, 120, 120))
    dr = ImageDraw.Draw(sheet)
    dr.text((8, 8), "Golden sheet 2026-10-17 (owner approval). Fix round 1: new SSJ2 heads. Each cell: original | golden at 10x on one anchor; faint box = "
            "32x32 slot. Dir 3 is dir 2 mirrored (same frame, H-flip). AI-generated art (Claude), for owner review.",
            fill=(0, 0, 0))
    y0 = 40
    for r, form in enumerate(FORMS):
        dr.text((8, y0 + r * rows_h + lab + 10), FORMS[form][0], fill=(0, 0, 0))
        for d in range(4):
            sd = 2 if d == 3 else d
            rec = dict(rec_of(form, sd))
            if d == 3:
                rec["attr1"] ^= g.HFLIP
            o_rec = g.by_key(g.SPRITES / FORMS[form][1])[(0, sd, 0)]
            o_img = Image.open(o_rec["dir_path"] / o_rec["png"])
            x0 = 160 + d * (2 * cw + 3 * pad)
            dr.text((x0, y0 + r * rows_h), f"dir {d}{' (mirror of dir 2)' if d == 3 else ''}: original | golden", fill=(0, 0, 0))
            sheet.paste(cell(o_img, rec, s), (x0, y0 + r * rows_h + lab))
            sheet.paste(cell(gold_imgs[(form, sd)], rec, s), (x0 + cw + pad, y0 + r * rows_h + lab))
    # row 4: the four new heads (head rows only) next to a reference crop
    r = 3
    yr = y0 + r * rows_h
    dr.text((8, yr + lab + 10), "New SSJ2 heads", fill=(0, 0, 0))
    ref = Image.open(W / "ref" / "GohanSuperSaiyanIINV.png").convert("RGB")
    ref = ref.crop((95, 0, 315, 200)).resize((int(220 * cw / 200), cw))
    sheet.paste(ref, (160, yr + lab))
    dr.text((160, yr), "reference (anime, data\\reference\\GohanSuperSaiyanIINV.webp)", fill=(0, 0, 0))
    hx = 160 + ref.width + pad
    for d in range(4):
        sd = 2 if d == 3 else d
        rec = dict(rec_of("gi_ssj2", sd))
        if d == 3:
            rec["attr1"] ^= g.HFLIP
        c = cell(gold_imgs[("gi_ssj2", sd)], rec, s).crop((0, 0, cw, 18 * s))
        sheet.paste(c, (hx + d * (cw + pad), yr + lab))
        dr.text((hx + d * (cw + pad), yr), f"head dir {d}", fill=(0, 0, 0))
    # row 5: Super Saiyan golden head next to the new Super Saiyan 2 head, per direction (structure check)
    yr = y0 + 4 * rows_h
    dr.text((8, yr + lab + 10), "SSJ vs SSJ2 heads", fill=(0, 0, 0))
    for d in range(4):
        sd = 2 if d == 3 else d
        x0 = 160 + d * (2 * cw + 3 * pad)
        dr.text((x0, yr), f"dir {d}: SSJ golden head | new SSJ2 head", fill=(0, 0, 0))
        for k, form in enumerate(("gi_ssj", "gi_ssj2")):
            rec = dict(rec_of(form, sd))
            if d == 3:
                rec["attr1"] ^= g.HFLIP
            sheet.paste(cell(gold_imgs[(form, sd)], rec, s).crop((0, 0, cw, 18 * s)), (x0 + k * (cw + pad), yr + lab))
    # row 6: lightning patterns on the SSJ2 golden front frame, then the SSJ2 frames at 1x and 3x (game scale check)
    yr = y0 + 4 * rows_h + head_h
    dr.text((8, yr + lab + 10), "Lightning", fill=(0, 0, 0))
    rec = rec_of("gi_ssj2", 0)
    for i, (name, v) in enumerate(variants.items()):
        x0 = 160 + i * (cw + pad)
        dr.text((x0, yr), f"pattern {i + 1}: {name}", fill=(0, 0, 0))
        sheet.paste(cell(v, rec, s), (x0, yr + lab))
    for k, sc in enumerate((1, 3)):
        x0 = 160 + 3 * (cw + pad) + k * (4 * 32 + 4 * pad)
        dr.text((x0, yr), f"SSJ2 dirs 0-3 at {sc}x", fill=(0, 0, 0))
        for d in range(4):
            sd = 2 if d == 3 else d
            rec = dict(rec_of("gi_ssj2", sd))
            if d == 3:
                rec["attr1"] ^= g.HFLIP
            sheet.paste(cell(gold_imgs[("gi_ssj2", sd)], rec, sc, box=False),
                        (x0 + (d * (32 * sc + 4) if sc == 1 else (d % 2) * (32 * sc + 4)),
                         yr + lab + (0 if sc == 1 else (d // 2) * (32 * sc + 4))))
    sheet.save(G / "golden_sheet.png")
    print("\n".join(report))
    print("sheet", sheet.size)
