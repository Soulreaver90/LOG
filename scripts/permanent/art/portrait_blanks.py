r"""Export portrait FRAMES and complete BACKGROUNDS as 64x64 layers, to sandwich your own art between.

The working method this serves:

    top     frames\frame_0.png        the border, interior transparent
    middle  your portrait, drawn with NO background
    bottom  backgrounds\bg_<n>.png    a complete 64x64 field

A dialog portrait is a 64x64 8bpp image in row order (bible B0325), so the frame and the background
are pixels inside it and not separate assets. This pulls them back out.

## How a background is recovered

A vanilla background is two to four NEARLY IDENTICAL shades in nested circular bands, each band
solid, with an ORDERED DITHER between one band and the next (bible B2380). Its centre sits LOW,
behind the character, not in the middle of the picture: the blue field is centred at (31,52) and
the purple at (32,56). The character covers that middle, so no single portrait shows a whole
background, and the innermost shade is never visible on any of them.

  1. GROUP. Portraits that share a background are found by MEASUREMENT, not by colour. Two belong
     together only when their top corners agree at least MATCH of the time. Grouping by the corner
     colour alone is wrong: only 7 of the 136 red pairs actually match.
  2. PALETTE. Pixels where every portrait in the group agrees are certainly background, because the
     characters differ and the background does not. The colours among them that reach across the
     picture are the background's palette; a blob they happen to share does not reach and is cut.
  3. GATHER. Take every pixel ANY portrait shows in that palette. A pixel one head covers is still
     readable from another, and demanding all of them agree threw away most of the disc.
  4. FIT THE CIRCLE. Search for the centre that makes the colour a function of the radius alone,
     then fill each radius from its measured MIX through an ordered dither. The centre must be
     found, never assumed: about a wrong centre every band smears across every radius, every radius
     comes out mixed, and the whole field stipples. A radius with fewer than MIN_SAMPLES measured
     pixels takes the nearest trusted one, because near the centre almost everything is covered and
     a character wearing a background colour would win that vote alone.

Every background carries its measured percentage in its own FILE NAME, so a mostly invented one is
obvious without opening the README.

It never writes a ROM and never touches art\tables, and it deletes only its own previous output.

Run: py -3.14 -P scripts\permanent\art\portrait_blanks.py
     py -3.14 -P scripts\permanent\art\portrait_blanks.py --rom <a build> --out <folder>
"""
import argparse
import sys
from collections import Counter, deque
from itertools import combinations
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # run it straight, not only as a module

from art import art_tables as A        # noqa: E402
import log_paths  # noqa: E402

BASE_ROM = log_paths.BASE_ROM
SIDE, RING = A.SIDE, A.RING
INNER = range(RING, SIDE - RING)
TOLERANCE = 56          # RGB distance a flood fill may step; an outline jumps much further
MATCH = 0.95            # top corner agreement before two portraits count as the same background
STRAY = 16              # a ring differing by this many pixels or fewer is the same frame, slipped
MIN_GROUP = 3           # under three portraits a background has too few independent characters
CORNERS = [(x, y) for y in range(RING, 13)
           for x in list(range(RING, 13)) + list(range(52, SIDE - RING))]
GENERATED = {log_paths.PORTRAIT_KIT_FRAMES.name: "frame_*.png",
             log_paths.PORTRAIT_KIT_BACKGROUNDS.name: "bg_*.png",
             log_paths.PORTRAIT_KIT_PROOF.name: "*.png"}
CLEAR = (0, 0, 0, 0)


# ===== reading =====

def read_portraits(rom: bytes, block: int = A.VANILLA_BLOCK, ids: range = A.DIALOG_IDS) -> dict:
    """Every portrait a block holds. Another release needs its own block and its own id range.

    The Europe ROM's block is at `rom:0x6A97B0` and its dialog ids run 18 higher, so they are 44 to
    132. All 89 are BYTE IDENTICAL to the USA ones, so Europe yields no backdrop the USA lacks.

    Stay inside the dialog range. The entries below it are not dialog portraits and do not use the
    OBJ palette, so rendering them through it invents colours: ids 33, 39, 40 and 43 came out as a
    green field that does not exist, which read as a new backdrop until the range was checked.
    """
    out = {}
    for pid in ids:
        try:
            _, px = A.live_frame(rom, block, pid)
        except Exception:
            continue
        if px and len(px) == SIDE * SIDE:
            out[pid] = px
    return out


def render(px: bytes, pal: list) -> Image.Image:
    img = Image.new("RGBA", (SIDE, SIDE))
    out = img.load()
    for i, v in enumerate(px):
        out[i % SIDE, i // SIDE] = (*pal[v], 255)
    return img


# ===== frames =====

def ring_of(px: bytes) -> list:
    return [px[i] for i in A.RING_IDX]


def group_frames(portraits: dict) -> tuple:
    """A ring differing by at most STRAY pixels is the SAME frame with a slip, not a new frame.

    82 of the 89 vanilla portraits share one ring exactly and most of the rest differ by ONE pixel,
    so exact grouping reports six frames and says something false about the game.
    """
    counts = Counter(bytes(ring_of(px)) for px in portraits.values())
    bases, strays = [], {}
    for key, _ in counts.most_common():
        ring = list(key)
        members = [pid for pid, px in portraits.items() if bytes(ring_of(px)) == key]
        for n, (base, ids) in enumerate(bases):
            diff = [k for k in range(len(base)) if base[k] != ring[k]]
            if len(diff) <= STRAY:
                ids.extend(members)
                for pid in members:
                    if diff:
                        strays[pid] = (n, len(diff))
                break
        else:
            bases.append((ring, list(members)))
    return bases, strays


def frame_png(ring: list, pal: list) -> Image.Image:
    img = Image.new("RGBA", (SIDE, SIDE), CLEAR)
    out = img.load()
    for k, i in enumerate(A.RING_IDX):
        out[i % SIDE, i // SIDE] = (*pal[ring[k]], 255)
    return img


# ===== segmenting one portrait's background =====

# The TOP two rows and the upper part of both side columns. The BOTTOM is deliberately left out:
# it is shoulders and chest on nearly every portrait, so including it put skin and clothing into the
# background palette and selected the whole character.
BORDER = ([(x, y) for y in (RING, RING + 1) for x in INNER]
          + [(x, y) for y in range(RING + 2, 42) for x in (RING, RING + 1,
                                                           SIDE - RING - 2, SIDE - RING - 1)])
BORDER_SHARE = 0.85     # of the border ring the background palette must cover
BORDER_FLOOR = 0.80     # below this the portrait has no readable background at all
MIDDLE = [(x, y) for y in range(20, 45) for x in range(20, 45)]
MIDDLE_MAX = 0.20       # a real background is ABSENT from the middle, because the face is there
MIN_SHARE = 0.05        # of the agreed pixels a colour needs before it counts as background
MIN_SAMPLES = 10        # measured pixels a ring needs before its colour is trusted


def segment(px: bytes, pal: list) -> tuple:
    """({(x, y): index} background pixels, share of the border ring they cover).

    NOT a flood fill and NOT the corner window. Both were tried and both failed:

      - a flood fill steps pixel to pixel, and a character outline is a chain of small steps, so it
        walks around the head and reports the hair as background;
      - the top corner window IS the character on a portrait whose face fills the frame, such as the
        cat and the pig, so it selected the character and scored highest of all 89.

    The background instead OWNS THE BORDER RING. Its palette is the few indices that cover
    BORDER_SHARE of the two pixel ring just inside the frame. A character can touch that ring, but on
    a portrait with a readable background it cannot dominate it.
    """
    counts, spread = Counter(), {}
    for x, y in BORDER:
        c = px[y * SIDE + x]
        counts[c] += 1
        lo, hi = spread.get(c, (x, x))
        spread[c] = (min(lo, x), max(hi, x))
    total = len(BORDER)
    palette, seen = set(), 0
    for colour, n in counts.most_common():
        # A background colour SPANS the border. Hair sits at the top centre and spans a fraction of
        # it, and without this test the hair entered the palette, and the hole fill then spread hair
        # colour through the middle of the picture.
        lo, hi = spread[colour]
        palette.add(colour)
        seen += n
        if seen / total >= BORDER_SHARE:
            break
    covered = sum(n for c, n in counts.items() if c in palette) / total
    return ({(x, y): px[y * SIDE + x]
             for y in INNER for x in INNER if px[y * SIDE + x] in palette}, covered)


# ===== clustering portraits that share a background =====

def clusters(portraits: dict) -> list:
    """Groups whose top corners agree at least MATCH of the time. Measured, never assumed."""
    ids = sorted(portraits)
    parent = {p: p for p in ids}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in combinations(ids, 2):
        same = sum(1 for x, y in CORNERS
                   if portraits[a][y * SIDE + x] == portraits[b][y * SIDE + x])
        if same / len(CORNERS) >= MATCH:
            parent[find(a)] = find(b)
    out = {}
    for p in ids:
        out.setdefault(find(p), []).append(p)
    return sorted(out.values(), key=lambda v: (-len(v), v[0]))


# ===== the background's shape =====

SEARCH_X, SEARCH_Y = range(20, 45), range(20, 57)
STEP = 96               # RGB distance from the seed shade a candidate may sit at
USE_FLOOR = 60          # pixels a colour needs across the group before it can be a background shade
PEAK = 0.50             # share a real background shade reaches at SOME radius
SCATTER = 0.85          # share of a dither shade's pixels that have no neighbour of its own colour
SCATTER_FLOOR = 40      # pixels a scattered shade needs before its scatter is believed
HOME = 0.50             # of its own best share, the level that still counts as a shade's own band
REACH = 3               # radii a shade may stray beyond its own band before it is read as a leak
SOFTEN = 0              # extra radii to spread a hard band boundary over; 0 copies the ROM exactly
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def radius(x: int, y: int, cx: int, cy: int) -> int:
    return round(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5)


def family(group: list, portraits: dict, pal: list) -> set:
    """The background's candidate shades: the NEARLY IDENTICAL colours that make a group a group.

    Seeded from the commonest index in the top band just inside the frame, which is background on
    every portrait with a readable one. Unanimity across the group cannot seed this, because the
    INNERMOST shade sits behind a character on every member and so never reaches unanimity. The old
    MIN_SHARE filter over the unanimous pixels dropped it for exactly that reason, and the blue
    field came out missing its lighter blue, index 74.

    This is only a CANDIDATE set, deliberately generous. It lets in a character colour that happens
    to sit near the family, such as the skin in the pink group, and `bands` prunes those out by the
    structural test: a background shade owns a radius, a stray colour never does. Nothing here tries
    to be exact, because colour distance alone cannot separate these. Chaining shade to shade was
    tried and is worse: it walks the whole palette, the same way a flood fill walks an outline.
    """
    top = Counter()
    for pid in group:
        for y in (RING, RING + 1, RING + 2):
            for x in INNER:
                top[portraits[pid][y * SIDE + x]] += 1
    seed = pal[top.most_common(1)[0][0]]
    use = Counter()
    for pid in group:
        use.update(portraits[pid][y * SIDE + x] for y in INNER for x in INNER)
    return {i for i, n in use.items()
            if n >= USE_FLOOR and max(abs(a - b) for a, b in zip(pal[i], seed)) <= STEP}


def dithered(group: list, portraits: dict, palette: set) -> set:
    """Family shades laid down as a SCATTER: almost every pixel alone, with no neighbour of its own.

    A band shade and a character both come in solid runs, so `bands` can tell them apart by which
    one owns a radius. A dither shade owns nothing: the cyan field's two brightest shades hold about
    15 percent of their radii and never more, and PEAK alone threw them away, which is why the cyan
    came out with a thin crisp ring instead of the ROM's broad speckle. Scatter is what they do have:
    68 is 100 percent isolated pixels and 165 is 92, against 16 for the grey in the blue group and
    69 for the grey in the red one.
    """
    out = set()
    for colour in palette:
        total = alone = 0
        for pid in group:
            px = portraits[pid]
            for y in INNER:
                for x in INNER:
                    if px[y * SIDE + x] != colour:
                        continue
                    total += 1
                    if all(px[(y + dy) * SIDE + x + dx] != colour
                           for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                        alone += 1
        if total >= SCATTER_FLOOR and alone / total >= SCATTER:
            out.add(colour)
    return out


def bands(known: dict, keep: set = frozenset()) -> tuple:
    """((cx, cy), {radius: [(colour, share), ...]}) measured about the BEST FITTING centre.

    The centre is the one that makes the colour depend on the radius alone, and it is NOT the middle
    of the picture: the blue field sits at (31,52) and the purple at (32,56), low and behind the
    character. Taking the middle was the whole bug. About a wrong centre every band smears across
    every radius, so every radius comes out mixed and the fill stipples the WHOLE field. That is the
    background the owner rejected twice.

    Each radius keeps its MIX, not its winner, because a vanilla background really does dither. The
    blue field runs 97/2, 86/13, 70/27, 61/36, 43/55, 23/76, 4/95 over ten radii between its lighter
    blue and its mid blue, and the cyan field dithers a brighter shade in at the corners at 8, 23,
    66, 70 and 100 percent. Where a band is solid its mix is already 100 percent and no dither
    appears, which is why vanilla measures 87 to 98 percent solid overall.
    """
    best = None
    for cy in SEARCH_Y:
        for cx in SEARCH_X:
            rings = {}
            for (x, y), colour in known.items():
                rings.setdefault(radius(x, y, cx, cy), Counter())[colour] += 1
            score = sum(c.most_common(1)[0][1] for c in rings.values())
            if best is None or score > best[0]:
                best = (score, cx, cy, rings)
    _, cx, cy, rings = best

    # A radius under MIN_SAMPLES is not trusted: near the centre almost everything is covered by a
    # character, and one wearing a background colour would win that radius on its own.
    share = {}
    for r, c in rings.items():
        n = sum(c.values())
        if n >= MIN_SAMPLES:
            share[r] = {colour: k / n for colour, k in c.items()}

    # A colour that never OWNS a radius is not background. A character colour close enough in RGB to
    # join the family, such as the grey in the blue group, holds a steady few percent across many
    # radii and peaks nowhere; every real shade reaches PEAK somewhere.
    # A shade is background when it OWNS a radius, or when `keep` saw it laid down as a dither.
    real = {colour for s in share.values() for colour, v in s.items() if v >= PEAK} | keep
    mix = {}
    for r, s in share.items():
        keep = [(colour, v) for colour, v in s.items() if colour in real]
        total = sum(v for _, v in keep)
        if total:
            mix[r] = {colour: v / total for colour, v in keep}
    return (cx, cy), soften(unleak(mix))


def unleak(mix: dict) -> dict:
    """Drop a shade from a radius that is far from its OWN band, then renormalise what is left.

    A character can wear the background's own index. Piccolo's cape is the purple field's outermost
    shade and sits dead centre, so that shade leaked inward at 3 to 12 percent from r16 to r30, far
    from its band at r34 to r47, and the dither scattered single dark pixels deep inside the light
    circles. The red field leaks the same way at r16 to r20. The owner caught both immediately.

    A shade's own band is the radii where it reaches HOME of its own best share, so this works for a
    scatter shade too, which peaks low and owns nothing. Anything within REACH of that band is kept,
    which leaves every genuine boundary dither alone: those sit right beside the band they belong to.
    """
    best = {s: max(m.get(s, 0) for m in mix.values()) for m in mix.values() for s in m}
    home = {s: [r for r, m in mix.items() if m.get(s, 0) >= HOME * v] for s, v in best.items()}
    out = {}
    for r, m in mix.items():
        near = {s: v for s, v in m.items()
                if home[s] and min(abs(r - q) for q in home[s]) <= REACH}
        total = sum(near.values())
        if total:
            out[r] = {s: v / total for s, v in near.items()}
    return out


def soften(mix: dict) -> dict:
    """Spread a hard band boundary over SOFTEN extra radii. At SOFTEN 0 it returns the ROM's own mix.

    Vanilla's own boundaries vary. The blue field fades over ten radii and the purple over six, but
    the cyan field turns over in ONE, at 54/46, which the eye reads as a hard circle. Softening it
    is a drawing choice, not a measurement, so the default copies the ROM and `--soften` is the
    owner's knob. It only ever touches a radius that is PURE and sits beside a different band, so a
    field that already fades gradually barely moves: at `--soften 2` the red changes by 0 pixels of
    3364, the blue by 3 and the purple by 8, against the cyan's 32.
    """
    if SOFTEN < 1:
        return {r: sorted(m.items(), key=lambda kv: -kv[1]) for r, m in mix.items()}
    have = sorted(mix)
    pure = {r for r in have if max(mix[r].values()) > 0.99}
    out = {}
    for r in have:
        near = [k for k in have if abs(k - r) <= SOFTEN]
        sharp = r in pure and any(max(mix[k], key=mix[k].get) != max(mix[r], key=mix[r].get)
                                  for k in near)
        if not sharp:
            out[r] = sorted(mix[r].items(), key=lambda kv: -kv[1])
            continue
        blend, weight = Counter(), 0.0
        for k in near:
            w = SOFTEN + 1 - abs(k - r)
            weight += w
            for colour, v in mix[k].items():
                blend[colour] += w * v
        out[r] = sorted(((c, v / weight) for c, v in blend.items()), key=lambda kv: -kv[1])
    return out


# ===== building one complete background =====

def combine(group: list, portraits: dict, pal: list) -> tuple:
    """(picture, measured) for a group of portraits that share a background.

    A pixel is background when EVERY portrait in the group has the same index there. The characters
    differ and the background does not, so agreement IS the test. No palette, no flood fill, no
    geometry.

    Four heuristics were tried before this and all four failed, each in its own way:

      - flood fill from the frame: the shoulders touch the bottom edge, so it started inside the
        character;
      - flood fill from the top corners: an outline is a chain of small colour steps, so it walked
        around the head;
      - the palette of the top corners: on a portrait whose face fills the frame that window IS the
        character;
      - the palette of the border ring, even requiring a colour to span the border: wide hair spans
        it too, and the hole fill then spread hair colour through the middle.

    Agreement needs no guess about what a character looks like. Its cost is that it works only where
    portraits genuinely share a background, which is why the groups are measured first.
    """
    # STEP 1. The candidate shades, seeded from the top band. Earlier versions learned the palette
    # from the pixels the whole group AGREES on, which cannot see the innermost shade at all,
    # because a character covers it on every member.
    palette = family(group, portraits, pal)

    # STEP 2. Now take every pixel ANY member shows in that palette. This is what recovers the
    # light disc: it sits behind a head in some portraits and in the open in others, and
    # unanimity alone dropped it and let the fill paint the outer colour straight over it.
    def gather(shades: set) -> dict:
        out = {}
        for y in INNER:
            for x in INNER:
                v = Counter(c for c in (portraits[p][y * SIDE + x] for p in group) if c in shades)
                if v:
                    out[(x, y)] = v.most_common(1)[0][0]
        return out

    known = gather(palette)
    if not known:
        return None, 0

    # STEP 3. Fit, which also prunes the palette to the shades that own a radius, then gather AGAIN
    # from the pruned set. Gathering once would leave a character colour that merely sits near the
    # family in `known`, and the middle test below would then read that character as the background.
    (cx, cy), mix = bands(known, dithered(group, portraits, palette))
    if not mix:
        return None, 0
    known = gather({shade for m in mix.values() for shade, _ in m})
    measured = len(known)
    if sum(1 for xy in MIDDLE if xy in known) / len(MIDDLE) > MIDDLE_MAX:
        return None, 0          # the background reaches the middle, so it is the same character
    have = sorted(mix)

    # Ordered dither, so a radius whose mix is 100 percent one shade comes out solid by itself.
    img = Image.new("RGBA", (SIDE, SIDE), CLEAR)
    out = img.load()
    for y in INNER:
        for x in INNER:
            r = radius(x, y, cx, cy)
            m = mix[r] if r in mix else mix[min(have, key=lambda k: abs(k - r))]
            threshold, run, colour = BAYER[y % 4][x % 4] / 16, 0.0, m[0][0]
            for shade, s in m:
                run += s
                if threshold < run:
                    colour = shade
                    break
            out[x, y] = (*pal[colour], 255)
    return img, measured


# ===== output =====

def clear_old(out: Path) -> int:
    n = 0
    for sub, pattern in GENERATED.items():
        for f in (out / sub).glob(pattern):
            f.unlink()
            n += 1
    return n


def write_readme(out: Path, bases: list, strays: dict, rows: list, singles: list) -> None:
    lines = [
        "# Portrait layers: a frame, your art, a background", "",
        "Draw your portrait with NO background and stack three layers:", "",
        "| Layer | File |", "| --- | --- |",
        "| top | `frames/frame_0.png` |", "| middle | your portrait, transparent background |",
        "| bottom | a file from `backgrounds/` |", "",
        "**Never draw on the frame.** The art table rejects an imported portrait whose outer 3 px",
        "ring does not match the ring that id already had.", "",
        f"## Frames ({len(bases)})", "",
        "Nearly every portrait uses one frame. A ring differing by at most "
        f"{STRAY} pixels is counted as",
        "that frame with a slip rather than as a separate frame.", "",
        "| Frame | Portraits | Ids |", "| --- | --- | --- |",
    ]
    for n, (_, ids) in enumerate(bases):
        lines.append(f"| `frames/frame_{n}.png` | {len(ids)} | "
                     f"{', '.join(str(i) for i in sorted(ids))} |")
    if strays:
        lines += ["", f"{len(strays)} portraits slip a few ring pixels: "
                  + ", ".join(f"{p} ({n} px)" for p, (_, n) in sorted(strays.items())) + "."]

    lines += ["", f"## Backgrounds ({len(rows)})", "",
              "Every file is a complete 64x64 field, so it works as a bottom layer. The percentage in",
              "the name is how much of it was READ from the ROM. The rest is the fitted circle",
              "carried on through the middle, where your drawing goes.", "",
              "A background is a few nearly identical shades in solid circular bands, with an",
              "ordered dither between one band and the next. Its centre sits LOW, behind the",
              "character, not in the middle of the picture. Keep both when you paint over it.", "",
              "`proof/` shows each background beside the real portraits it came from. Look there",
              "before trusting one.", "",
              "| Background | Measured | Portraits it came from |", "| --- | --- | --- |"]
    for name, pct, group in rows:
        lines.append(f"| `backgrounds/{name}` | {pct}% | {', '.join(str(i) for i in group)} |")

    lines += ["", f"## The {len(singles)} portraits with a background of their own", "",
              f"Fewer than {MIN_GROUP} portraits share these, so too few independent characters can",
              "corroborate what is background and what is not. No background file is written for",
              "them on purpose. Use the",
              "portrait itself as your reference:", "",
              "    " + ", ".join(str(p) for p in sorted(singles)), "",
              "## Why these are not grouped by colour", "",
              "The portraits do not share a handful of backgrounds. Measured on the top corners,",
              "where a head almost never reaches, only 43 of 394 same-colour pairs actually match.",
              "Most portraits have a background of their own, so a background here is built only from",
              f"portraits that agree at least {int(MATCH * 100)} percent."]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rom", help="a ROM to read (default: the base USA ROM)")
    ap.add_argument("--out", help="where to write (default: art\\portrait-kit)")
    ap.add_argument("--block", help="portrait block offset, hex (default the USA 0x3EC9D0; "
                                    "the Europe ROM is 0x6A97B0)")
    ap.add_argument("--ids", help="id range LO-HI to scan (default 26-114; Europe needs 0-139)")
    ap.add_argument("--soften", type=int, default=SOFTEN, metavar="N",
                    help="spread each hard band boundary over N extra radii (default 0, the ROM)")
    a = ap.parse_args()
    globals()["SOFTEN"] = max(0, a.soften)

    rom_path = Path(a.rom) if a.rom else BASE_ROM
    out = Path(a.out) if a.out else log_paths.PORTRAIT_KIT
    rom = rom_path.read_bytes()
    pal = A.obj_palette(rom)

    block = int(a.block, 16) if a.block else A.VANILLA_BLOCK
    lo, hi = (int(v) for v in a.ids.split("-")) if a.ids else (A.DIALOG_IDS.start, A.DIALOG_IDS.stop)
    portraits = read_portraits(rom, block, range(lo, hi))
    if not portraits:
        raise SystemExit(f"no portraits read from {rom_path}")
    for sub in GENERATED:
        (out / sub).mkdir(parents=True, exist_ok=True)
    gone = clear_old(out)

    bases, strays = group_frames(portraits)
    for n, (ring, _) in enumerate(bases):
        frame_png(ring, pal).save(out / log_paths.PORTRAIT_KIT_FRAMES.name / f"frame_{n}.png")

    rows, inner, singles = [], len(INNER) ** 2, []
    for group in clusters(portraits):
        if len(group) < MIN_GROUP:
            singles.extend(group)
            continue
        img, measured = combine(group, portraits, pal)
        if img is None:
            continue
        pct = measured * 100 // inner
        name = f"bg_{pct:02d}pct_id{group[0]:03d}.png"
        img.save(out / log_paths.PORTRAIT_KIT_BACKGROUNDS.name / name)
        rows.append((name, pct, sorted(group)))
        shots = [img] + [render(portraits[p], pal) for p in group[:6]]
        sheet = Image.new("RGBA", (len(shots) * SIDE * 3, SIDE * 3), (40, 40, 40, 255))
        for i, im in enumerate(shots):
            sheet.alpha_composite(im.resize((SIDE * 3, SIDE * 3), Image.NEAREST), (i * SIDE * 3, 0))
        sheet.save(out / log_paths.PORTRAIT_KIT_PROOF.name / f"{name[:-4]}_vs_real.png")
    rows.sort(key=lambda r: -r[1])

    write_readme(out, bases, strays, rows, singles)
    best = sum(1 for _, pct, _ in rows if pct >= 70)
    print(f"  removed {gone} file(s) from the previous run")
    print(f"  {len(portraits)} portraits read from {rom_path.name}")
    print(f"  {len(bases)} frames, {len(rows)} backgrounds ({best} are 70% measured or better)")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
