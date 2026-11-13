# Aura v2 drafts (owner references 2026-10-18). Two families, 6 patterns each, a new shape every frame:
#   A "cross" (220162.gif): 1 long 1 px zigzag bolt crossing the body; white 2, blue 191 at bends and forks.
#   B "outline" (images (7).jpg): 2-3 short branched bolts hugging the silhouette (hair, shoulder, fist, feet);
#     blue 191 with white 2 hot spots.
# Bolts never cover the face box. Writes aura2_<family>.png sheets and aura2_<family>_d<n>.gif loops.
import random
from pathlib import Path
from PIL import Image, ImageDraw
W = Path(__file__).parent
GOLD = W.parents[1]
BLUE, WHITE = 191, 2
BG = (191, 255, 7)
N, S = 6, 6


def face_box(px):
    """Iris (64, 65) bounding box grown 3 px each side, 3 rows down: the face the bolts never cover (23 is all skin outline)."""
    pts = [(i % 32, i // 32) for i, v in enumerate(px) if v in {64, 65}]
    if not pts:
        return set()
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return {(x, y) for x in range(min(xs) - 3, max(xs) + 4) for y in range(min(ys) - 5, max(ys) + 4)}


def walk(rng, a, b, jag=1):
    """Jagged 8-connected path from a to b: step toward b, with a sideways kick every 2-3 steps."""
    (x, y), (bx, by) = a, b
    pts = [(x, y)]
    n = 0
    while (x, y) != (bx, by) and n < 80:
        n += 1
        sx = (bx > x) - (bx < x)
        sy = (by > y) - (by < y)
        if n % rng.choice((2, 3)) == 0:
            if abs(bx - x) >= abs(by - y):
                y += rng.choice((-jag, jag))
            else:
                x += rng.choice((-jag, jag))
        else:
            x, y = x + sx, y + sy
        pts.append((x, y))
    return pts


def line(a, b):
    """Bresenham line from a to b, 8-connected."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
    err, pts = dx + dy, []
    while True:
        pts.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def cross(rng, px):
    """One long 1 px bolt: a 4-6 vertex zigzag from one side to the other across the body. White core,
    blue at each vertex (where the bolt bends) and on a short fork."""
    out = {}
    left = rng.random() < 0.5
    xs = sorted(rng.sample(range(3, 29), rng.randint(2, 4)))
    xs = [1] + xs + [30]
    if not left:
        xs = [31 - x for x in xs]
    y = rng.randint(17, 24)                             # below the chin: a long bolt never crosses the face
    verts = []
    for x in xs:
        verts.append((x, y))
        y = max(16, min(29, y + rng.randint(-4, 5)))
    path = []
    for a, b in zip(verts, verts[1:]):
        path += line(a, b)[:-1]
    path.append(verts[-1])
    for p in path:
        out[p] = WHITE
    for v in verts:
        out[v] = BLUE
    if rng.random() < 0.7:
        x, y = verts[rng.randint(1, len(verts) - 2)]
        tip = (x + rng.choice((-4, -3, 3, 4)), y + rng.choice((-5, -4, 4, 5)))
        for p in line((x, y), tip)[1:]:
            out.setdefault(p, BLUE)
    return out


def silhouette(px):
    """Transparent pixels next to the body (outline ring), with their row."""
    body = {(i % 32, i // 32) for i, v in enumerate(px) if v}
    ring = set()
    for x, y in body:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < 32 and 0 <= q[1] < 32 and q not in body:
                ring.add(q)
    return sorted(ring)


def outline(rng, px):
    """2-3 short branched bolts that start on the outline ring and run along or across the body edge."""
    out = {}
    ring = silhouette(px)
    for _ in range(rng.choice((2, 3, 3))):
        x, y = rng.choice(ring)
        tip = (x + rng.randint(-5, 5), y + rng.randint(-6, 6))
        trunk = walk(rng, (x, y), tip)
        for j, p in enumerate(trunk):
            out[p] = WHITE if j % 3 == 1 else BLUE
        if len(trunk) > 3:                              # a branch
            bx, by = trunk[len(trunk) // 2]
            for p in walk(rng, (bx, by), (bx + rng.choice((-3, 3)), by + rng.choice((-3, 3)))):
                out.setdefault(p, BLUE)
    return out


def apply(px, pat, pal):
    """Bolt over the frame, never on the face box; white over a bright pixel (hair, skin) turns blue to stay seen."""
    out = bytearray(px)
    face = face_box(px)
    for (x, y), v in pat.items():
        if 0 <= x < 32 and 0 <= y < 32 and (x, y) not in face:
            under = px[y * 32 + x]
            r, g, b = pal[3 * under:3 * under + 3]
            out[y * 32 + x] = BLUE if v == WHITE and under and r + g + b > 450 else v
    return bytes(out)


def render(o):
    g = Image.new("RGB", (32 * S, 32 * S), BG)
    big = o.convert("RGBA").resize((32 * S, 32 * S), Image.NEAREST)
    mask = Image.frombytes("L", (32, 32), bytes(255 if p else 0 for p in o.tobytes())).resize((32 * S, 32 * S))
    g.paste(big, (0, 0), mask)
    return g


def main():
    views = [Image.open(GOLD / f"golden_gi_ssj2_d{d}.png") for d in (0, 1, 2)]
    for fam, maker, seed in (("cross", cross, 11), ("outline", outline, 22)):
        rng = random.Random(seed)
        sheet = Image.new("RGB", (N * 34 * S + S, 3 * 34 * S + 20), BG)
        ImageDraw.Draw(sheet).text((4, 4), f"Aura v2 family {fam}: one column per frame, rows front / back / side, 6x",
                                   fill=(0, 0, 0))
        gifs = [[] for _ in views]
        for c in range(N):
            for r, v in enumerate(views):
                o = Image.frombytes("P", (32, 32), apply(v.tobytes(), maker(rng, v.tobytes()), v.getpalette()))
                o.putpalette(v.getpalette())
                img = render(o)
                sheet.paste(img, (S + c * 34 * S, 20 + r * 34 * S))
                gifs[r].append(img)
        sheet.save(W / f"aura2_{fam}.png")
        for r, frames in enumerate(gifs):
            frames[0].save(W / f"aura2_{fam}_d{r}.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)
    for old in ("aura2_patterns.png", "patterns.json", "aura2_d0.gif", "aura2_d1.gif", "aura2_d2.gif"):
        (W / old).unlink(missing_ok=True)
    print("ok")


if __name__ == "__main__":
    main()
