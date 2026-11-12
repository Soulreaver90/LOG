r"""
sprite_guard.py - Hold an outfit swap to the garment, and show what changed.

Why:     an outfit swap is the same sprite without the garment, so every pixel outside the garment must still
         be vanilla. On 2026-11-01 a Trunks tank swap painted over his mouth and three chest pixels, and the
         owner had to find both by eye. This turns that class of mistake into an error before he sees it.

Usage:   py -3 -I scripts\permanent\rom\sprite_guard.py check <vanilla.png> <edited.png> --garment 51,50,4F,4E
                  [--allow x,y ...] [--allow-rows 22-31]
         py -3 -I scripts\permanent\rom\sprite_guard.py sheet <vanilla.png> <edited.png> <out.png> [--crop 11-25]
Checks:  every changed pixel is either inside the garment mask or explicitly allowed. Exit 1 names the rest.
API:     garment_mask(img, indices, body_from=0, protect=True) -> {(x, y)}   changed(a, b) -> {(x, y)}
         palette_reuse(img, indices) -> {(x, y)}      components(img, indices) -> [{(x, y)}]
         violations(vanilla, edited, mask, allow) -> [(x, y, from_index, to_index)]
         review_sheet(vanilla, edited, crop) -> PIL image
Sheet:   vanilla, edited, and a map marking every changed pixel, at review zoom, 3x and 1x on a mid tone.
         The map is what says at a glance whether a drawing strayed outside the garment.
Rules:   reads only. Both images must be the same size and carry the same palette.
         Head reuse of a garment index is protected AUTOMATICALLY, by connectivity, and always named in the
         output. Trunks' jacket blues 4F and 51 are also his iris and its shadow. --body-from CANNOT save
         them, because the eye is on rows 13-14, inside any floor low enough to catch the collar. On
         2026-11-01 a swap repainted his eye and passed every check, and he shipped with a dark smear for a
         face. Pass --no-protect only to reproduce that old behaviour on purpose.
Source:  the method and the lessons behind it are in docs\sprite-guide.md.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# ===== CONFIG =====
BG = (104, 104, 112)          # mid tone: grey hides nothing, lime fights skin
ZOOM, SMALL = 15, (1, 3)
MARK = (255, 64, 64)
ISLAND_MAX = 4                # a garment island this small, above the garment mass, is head reuse


# ===== mask and diff =====

def _pixels(img: Image.Image) -> tuple:
    if img.mode != "P":
        raise ValueError(f"expected an indexed image, got {img.mode}")
    return img.tobytes(), img.size


def components(img: Image.Image, indices: set) -> list:
    """4-connected runs of the garment indices, largest first."""
    data, (w, h) = _pixels(img)
    seen, out = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or data[y * w + x] not in indices:
                continue
            stack, group = [(x, y)], set()
            seen.add((x, y))
            while stack:
                px, py = stack.pop()
                group.add((px, py))
                for qx, qy in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if 0 <= qx < w and 0 <= qy < h and (qx, qy) not in seen \
                            and data[qy * w + qx] in indices:
                        seen.add((qx, qy))
                        stack.append((qx, qy))
            out.append(group)
    return sorted(out, key=len, reverse=True)


def palette_reuse(img: Image.Image, indices: set, island_max: int = ISLAND_MAX) -> set:
    """Garment-index pixels that are NOT the garment: a small island sitting above the garment mass.

    A garment index is almost always reused on the head. Trunks' jacket blues 4F and 51 are also his iris
    and its shadow. A row floor CANNOT separate them, because the eye is on rows 13-14, inside any floor low
    enough to catch the collar: --body-from 13 lets a swap repaint his eye and still pass. On 2026-11-01 it
    did exactly that, and he shipped with a dark smear for a face.

    Connectivity does separate them. Measured over 12 vanilla Trunks frames: every real garment component
    holds 27 px or more, every eye is an isolated 2 px component ending above the garment's top row, and
    every genuine 1 px garment speck overlaps the garment's own rows. Zero misses, zero false alarms.

    Always PRINT what this protected. A silent mask that eats a real garment piece is the same class of bug."""
    groups = components(img, indices)
    if not groups:
        return set()
    top = min(y for _, y in groups[0])
    return {p for g in groups[1:] if len(g) <= island_max and max(y for _, y in g) < top for p in g}


def garment_mask(img: Image.Image, indices: set, body_from: int = 0, protect: bool = True) -> set:
    """Every pixel of the vanilla frame that holds one of the garment's palette indices, on body rows only.

    Take the mask from VANILLA. A part-edited frame has already lost the indices that define it.

    protect drops head reuse of a garment index, such as an iris. See palette_reuse. Leave it on."""
    data, (w, h) = _pixels(img)
    mask = {(x, y) for y in range(body_from, h) for x in range(w) if data[y * w + x] in indices}
    return mask - palette_reuse(img, indices) if protect else mask


def changed(vanilla: Image.Image, edited: Image.Image) -> set:
    a, (w, h) = _pixels(vanilla)
    b, size = _pixels(edited)
    if size != (w, h):
        raise ValueError(f"sizes differ: {(w, h)} and {size}")
    return {(x, y) for y in range(h) for x in range(w) if a[y * w + x] != b[y * w + x]}


def violations(vanilla: Image.Image, edited: Image.Image, mask: set, allow: set = frozenset()) -> list:
    """Changed pixels that are neither garment nor allowed, as (x, y, from, to), reading order."""
    a, (w, _) = _pixels(vanilla)
    b, _ = _pixels(edited)
    out = changed(vanilla, edited) - mask - set(allow)
    return [(x, y, a[y * w + x], b[y * w + x]) for y, x in sorted((y, x) for x, y in out)]


# ===== review sheet =====

def _panel(img: Image.Image, zoom: int, crop: tuple = None) -> Image.Image:
    im = img.convert("RGBA")
    if crop:
        im = im.crop((0, crop[0], im.width, crop[1]))
    big = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
    out = Image.new("RGB", big.size, BG)
    out.paste(big, (0, 0), big)
    return out


def review_sheet(vanilla: Image.Image, edited: Image.Image, crop: tuple = None) -> Image.Image:
    """Vanilla, edited, and a map of every changed pixel, plus 3x and 1x of the edited frame."""
    diff = changed(vanilla, edited)
    panels = [("vanilla", _panel(vanilla, ZOOM, crop)), ("edited", _panel(edited, ZOOM, crop))]

    marked = _panel(edited, ZOOM, crop)
    d = ImageDraw.Draw(marked)
    top = crop[0] if crop else 0
    for x, y in diff:
        if crop and not (crop[0] <= y < crop[1]):
            continue
        px, py = x * ZOOM, (y - top) * ZOOM
        d.rectangle([px, py, px + ZOOM - 1, py + ZOOM - 1], outline=MARK, width=2)
    panels.append((f"changed: {len(diff)} px", marked))

    pw, ph = panels[0][1].size
    cw = pw + 20
    sheet = Image.new("RGB", (cw * len(panels), ph + 44 + edited.height * max(SMALL) + 20), (30, 30, 36))
    t = ImageDraw.Draw(sheet)
    for i, (label, p) in enumerate(panels):
        t.text((i * cw + 10, 10), label, fill=(240, 240, 240))
        sheet.paste(p, (i * cw + 10, 30))
    y = ph + 40
    t.text((10, y), "game size and 3x", fill=(170, 170, 180))
    x = 10
    for s in SMALL:
        sheet.paste(_panel(edited, s), (x, y + 16))
        x += edited.width * s + 18
    return sheet


# ===== cli =====

def _main(argv: list) -> int:
    if not argv:
        print(__doc__.strip())
        return 2
    cmd, args = argv[0], argv[1:]
    garment, allow, allow_rows, crop, paths, body_from = set(), set(), [], None, [], 0
    protect = True
    while args:
        a = args.pop(0)
        if a == "--garment":
            garment = {int(v, 16) for v in args.pop(0).split(",")}
        elif a == "--body-from":
            body_from = int(args.pop(0))
        elif a == "--no-protect":
            protect = False
        elif a == "--allow":
            x, y = args.pop(0).split(",")
            allow.add((int(x), int(y)))
        elif a == "--allow-rows":
            lo, hi = args.pop(0).split("-")
            allow_rows.append((int(lo), int(hi)))
        elif a == "--crop":
            lo, hi = args.pop(0).split("-")
            crop = (int(lo), int(hi))
        else:
            paths.append(Path(a))

    vanilla, edited = Image.open(paths[0]), Image.open(paths[1])
    for lo, hi in allow_rows:
        allow |= {(x, y) for y in range(lo, hi + 1) for x in range(vanilla.width)}

    if cmd == "sheet":
        review_sheet(vanilla, edited, crop).save(paths[2])
        print(paths[2])
        return 0

    if cmd != "check":
        print(f"unknown command: {cmd}")
        return 2

    mask = garment_mask(vanilla, garment, body_from, protect=protect)
    reuse = palette_reuse(vanilla, garment) if protect else set()
    if reuse:
        cells = ", ".join(f"(x{x},y{y})" for x, y in sorted(reuse, key=lambda p: (p[1], p[0])))
        print(f"PROTECTED {len(reuse)} px of head reuse, almost always an eye: {cells}")
        print("  These hold a garment index but are not the garment. An edit here is a violation.")
    elif protect:
        print("No head reuse of a garment index found in this frame.")
    bad = violations(vanilla, edited, mask, allow)
    n = len(changed(vanilla, edited))
    print(f"garment mask: {len(mask)} px | changed: {n} px | outside the garment: {len(bad)} px")
    if not bad:
        print("OK: every change is inside the garment or allowed.")
        return 0
    for x, y, f, t in bad:
        print(f"  OUTSIDE THE GARMENT  (x{x:2d}, y{y:2d})  {f:02X} -> {t:02X}")
    print("\nEach line is a vanilla pixel this edit overwrote. Restore it, or allow it on purpose.")
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
