# r12fix: controller hand fixes of r12 gi frames for owner review (owner 2026-10-18 4:03 PM).
# Usage:  py -3 -I fix.py [key ...]        apply edits.py, write out\<set>_aNN_dD_iI.png (1x RGBA, palette colors)
#         py -3 -I fix.py --zoom KEY       write zoom\KEY.png: armor | r12 | fix at 12x with a pixel grid
#         py -3 -I fix.py --sheet          write r12fix_review.png: armor | r12 | r12fix for every edited key
# KEY = set.anim.dir.index, e.g. 157.13.0.3. Edits live in edits.py; this file never touches the build tree.
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import view  # noqa: E402
from edits import EDITS  # noqa: E402

OUT, ZOOM = HERE / "out", HERE / "zoom"
R14 = view.ROOT / "scratch" / "art" / "review" / "frames_r14"   # rom_sheet --frames of r14 set 159 (aura bolts)
LIME, GRID = (191, 255, 7), (150, 200, 0)
LETTER = {"K": 1, "P": 89, "Q": 88, "R": 87, "N": 211, "r": 26, "x": 27, "B": 72, "b": 195,
          "S": 114, "s": 115, "t": 116, "u": 117, "d": 113, "W": 2, "h": 23, "j": 20,
          "o": 35, "O": 34, "H": 15, ".": 0}


# ===== Frames =====
def parse(key):
    s, a, d, i = map(int, key.split("."))
    return s, a, d, i


def frames(key, pal):
    s, a, d, i = parse(key)
    gdir, adir, aset = view.DIRS[s]
    arm = view.load(view.F / adir / view.name(aset, a, d, i), pal)
    gi = view.load(view.F / gdir / view.name(s, a, d, i), pal)
    return arm, gi


def apply(key, gi):
    """Ops: ("row", y, x, "letters") overwrites a run.
    ("copy", src_key, y0, y1, dx, dy, mirror) copies rows y0-y1 of another frame (its r12fix if edited, else r12);
    mirror flips the source first (x -> w-1-x), then dx/dy shift it. Source transparent pixels clear the target.
    ("armor", y, x, "mask", {armor index: letter}) recolors each '#' pixel of the mask from the armor pixel there."""
    out = [row[:] for row in gi]
    arm = frames(key, view.palette())[0]
    for op in EDITS[key]:
        if op[0] == "row":
            _, y, x, text = op
            for k, ch in enumerate(text):
                if ch != "_":
                    out[y][x + k] = LETTER[ch]
        elif op[0] == "copy":
            _, src, y0, y1, dx, dy, mirror = op
            if src.startswith("file:"):
                sg = view.load(HERE / src[5:], view.palette())
            else:
                sg = load_fix(src) if src in EDITS and src != key else frames(src, view.palette())[1]
            sw = len(sg[0])
            for y in range(y0, y1 + 1):
                for x in range(len(out[0])):
                    sx, sy = x - dx, y - dy
                    if mirror:
                        sx = sw - 1 - sx
                    out[y][x] = sg[sy][sx] if 0 <= sy < len(sg) and 0 <= sx < sw else 0
        elif op[0] == "delta":
            # carry a base fix to another form: move only pixels the base fix changed, at the best body offset,
            # and only where this form's r12 pixel equals base r12 there (so hair and other form-only art stay)
            _, base = op
            pal = view.palette()
            b12, bfx, me = frames(base, pal)[1], load_fix(base), frames(key, pal)[1]
            dx, dy = body_offset(b12, me)
            for y in range(len(b12)):
                for x in range(len(b12[0])):
                    tx, ty = x + dx, y + dy
                    if bfx[y][x] != b12[y][x] and 0 <= ty < len(out) and 0 <= tx < len(out[0]) \
                            and me[ty][tx] == b12[y][x]:
                        out[ty][tx] = bfx[y][x]
        elif op[0] == "bolts":
            # r13 aura: lay back every pixel where the r14 ROM frame differs from r12 (the bolts)
            s, a, d, i = parse(key)
            r12 = frames(key, view.palette())[1]
            r14 = view.load(R14 / view.name(s, a, d, i), view.palette())
            for y in range(len(out)):
                for x in range(len(out[0])):
                    if r14[y][x] != r12[y][x]:
                        out[y][x] = r14[y][x]
        elif op[0] == "armorc":
            _, y0, y1, x0, x1, cmap = op       # recolor every pixel in the box whose armor index is in cmap
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if arm[y][x] in cmap:
                        out[y][x] = LETTER[cmap[arm[y][x]]]
        elif op[0] == "armor":
            _, y, x, mask, cmap = op
            for r, line in enumerate(mask.split("/")):
                for k, ch in enumerate(line):
                    if ch == "#":
                        a = arm[y + r][x + k]
                        out[y + r][x + k] = LETTER[cmap[a]] if a in cmap else out[y + r][x + k]
    return out


def body_offset(base, other, y0=18):
    """(dx, dy) that best lays base rows y0+ onto other: most equal opaque pixels."""
    best, at = -1, (0, 0)
    for dy in range(-6, 7):
        for dx in range(-10, 11):
            n = 0
            for y in range(y0, len(base)):
                for x in range(len(base[0])):
                    if base[y][x]:
                        tx, ty = x + dx, y + dy
                        if 0 <= ty < len(other) and 0 <= tx < len(other[0]) and other[ty][tx] == base[y][x]:
                            n += 1
            if n > best:
                best, at = n, (dx, dy)
    return at


def rgb_of(pal):
    return {v: k for k, v in pal.items()}


def to_image(grid, inv):
    h, w = len(grid), len(grid[0])
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            if grid[y][x]:
                im.putpixel((x, y), inv[grid[y][x]] + (255,))
    return im


def out_path(key):
    s, a, d, i = parse(key)
    return OUT / view.name(s, a, d, i)


def load_fix(key):
    return view.load(out_path(key), view.palette())


# ===== Renders =====
def panel(grid, inv, scale, grid_lines):
    im = to_image(grid, inv).resize((len(grid[0]) * scale, len(grid) * scale), Image.NEAREST)
    bg = Image.new("RGB", im.size, LIME)
    bg.paste(im, (0, 0), im)
    if grid_lines:
        dr = ImageDraw.Draw(bg)
        for x in range(0, im.width, scale):
            dr.line([(x, 0), (x, im.height)], fill=GRID)
        for y in range(0, im.height, scale):
            dr.line([(0, y), (im.width, y)], fill=GRID)
    return bg


def strip(key, pal, scale, grid_lines):
    inv = rgb_of(pal)
    arm, gi = frames(key, pal)
    fixed = apply(key, gi) if key in EDITS else gi
    ps = [panel(g, inv, scale, grid_lines) for g in (arm, gi, fixed)]
    w, h = max(p.width for p in ps), max(p.height for p in ps)
    out = Image.new("RGB", (3 * w + 4 * 12, h + 30), LIME)
    dr = ImageDraw.Draw(out)
    for k, (p, label) in enumerate(zip(ps, ("armor", "r12", "r12fix"))):
        out.paste(p, (12 + k * (w + 12), 26))
        dr.text((12 + k * (w + 12), 6), f"{key}  {label}" if k == 0 else label, fill=(0, 0, 0))
    return out


def seq(pal, inv, specs):
    """Frames at screen position (record dx, dy from r12), one row per spec "set.anim.dir:i0,i1+set.anim.dir:i".
    Writes seq.png at 8x; a red line marks each frame's sash top row so a jump shows."""
    sys.path.insert(0, str(view.ROOT / "scripts" / "permanent"))
    from rom_sheet import live_set_offset, row_frames
    rom = (view.ROOT / "scratch" / "build" / "log2_poc_r12.gba").read_bytes()
    rows = []
    for spec in specs:
        cells = []
        for part in spec.split("+"):
            sad, idx = part.split(":")
            s, a, d = map(int, sad.split("."))
            recs = row_frames(rom, live_set_offset(rom, s), a, d)
            for i in map(int, idx.split(",")):
                key = f"{s}.{a}.{d}.{i}"
                g = load_fix(key) if key in EDITS else frames(key, pal)[1]
                cells.append((key, recs[i][0]["dx"], recs[i][0]["dy"], g))
        rows.append(cells)
    S, CW, CH = 8, 40, 40
    out = Image.new("RGB", (max(len(r) for r in rows) * CW * S, len(rows) * (CH * S + 20)), LIME)
    dr = ImageDraw.Draw(out)
    for ry, cells in enumerate(rows):
        for cx, (key, dx, dy, g) in enumerate(cells):
            ox, oy = cx * CW * S + (dx + 12) * S, ry * (CH * S + 20) + 20 + (dy + 30) * S
            im = to_image(g, inv).resize((len(g[0]) * S, len(g) * S), Image.NEAREST)
            out.paste(im, (ox, oy), im)
            sash = [y for y, row in enumerate(g) if 26 in row]
            if sash:
                yy = oy + sash[0] * S
                dr.line([(cx * CW * S, yy), ((cx + 1) * CW * S - 4, yy)], fill=(255, 0, 0))
            dr.text((cx * CW * S + 4, ry * (CH * S + 20) + 4), f"{key}  sash row {dy + sash[0] if sash else '-'}", fill=(0, 0, 0))
    out.save(HERE / "seq.png")


def gif(pal, inv, specs):
    """Per spec "set.anim.dir": an animated GIF at 6x, r12 on the left and r12fix on the right, each frame at its
    record dx, dy from r12, 150 ms per frame (rom_sheet's review speed). Writes anim/<spec>.gif."""
    sys.path.insert(0, str(view.ROOT / "scripts" / "permanent"))
    from rom_sheet import live_set_offset, row_frames
    rom = (view.ROOT / "scratch" / "build" / "log2_poc_r12.gba").read_bytes()
    (HERE / "anim").mkdir(exist_ok=True)
    S, CW, CH = 6, 48, 44
    for spec in specs:
        s, a, d = map(int, spec.split("."))
        recs = row_frames(rom, live_set_offset(rom, s), a, d)
        frames_out = []
        for i, (r, _) in enumerate(recs):
            key = f"{s}.{a}.{d}.{i}"
            pair = (frames(key, pal)[1], load_fix(key) if key in EDITS else frames(key, pal)[1])
            im = Image.new("RGB", (2 * CW * S + 8, CH * S + 18), LIME)
            dr = ImageDraw.Draw(im)
            for k, g in enumerate(pair):
                sp = to_image(g, inv).resize((len(g[0]) * S, len(g) * S), Image.NEAREST)
                im.paste(sp, (k * (CW * S + 8) + (r["dx"] + 16) * S, 18 + (r["dy"] + 36) * S), sp)
                dr.text((k * (CW * S + 8) + 4, 2), f"{spec} {'r12' if k == 0 else 'r12fix'}  i{i}", fill=(0, 0, 0))
            frames_out.append(im)
        frames_out[0].save(HERE / "anim" / f"{spec}.gif", save_all=True, append_images=frames_out[1:], duration=150, loop=0)


def main():
    pal = view.palette()
    inv = rgb_of(pal)
    OUT.mkdir(exist_ok=True)
    ZOOM.mkdir(exist_ok=True)
    args = sys.argv[1:]
    if args and args[0] == "--zoom":
        for key in args[1:]:
            strip(key, pal, 12, True).save(ZOOM / f"{key}.png")
        return
    if args and args[0] == "--gif":
        gif(pal, inv, args[1:])
        return
    if args and args[0] == "--seq":
        seq(pal, inv, args[1:])
        return
    if args and args[0] == "--sheet":
        strips = [strip(k, pal, 6, False) for k in EDITS]
        w, h, cols = max(s.width for s in strips), max(s.height for s in strips), 3
        rows = -(-len(strips) // cols)
        sheet = Image.new("RGB", (cols * (w + 24), rows * h), LIME)
        dr = ImageDraw.Draw(sheet)
        for k, s in enumerate(strips):
            sheet.paste(s, ((k % cols) * (w + 24), (k // cols) * h))
            dr.line([((k % cols) * (w + 24) + w + 10, (k // cols) * h), ((k % cols) * (w + 24) + w + 10, (k // cols + 1) * h)], fill=(0, 0, 0))
        sheet.save(HERE / "r12fix_review.png")
        return
    for key in args or EDITS:
        _, gi = frames(key, pal)
        to_image(apply(key, gi), inv).save(out_path(key))


if __name__ == "__main__":
    main()
