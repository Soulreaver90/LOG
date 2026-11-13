# Hair from layered triangle spikes: back spikes first, front spikes over them; each spike gets an outline
# where it meets the background or a spike behind it, and is lit from the upper left (L left, Y middle, o right).
def tri_mask(tip, bl, br):
    def inside(x, y):
        def s(a, b, c):
            return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])
        p = (x + .5, y + .5)
        d1, d2, d3 = s(p, tip, bl), s(p, bl, br), s(p, br, tip)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))
    return {(x, y) for y in range(0, 20) for x in range(32) if inside(x, y)}


def render(spikes, rows_max, white=(), dark_rows=()):
    """spikes: list of (tip, base_left, base_right), back to front. Returns {(x,y): char}."""
    owner = {}
    for k, sp in enumerate(spikes):
        for p in tri_mask(*sp):
            if p[1] <= rows_max:
                owner[p] = k
    g = {}
    for (x, y), k in owner.items():
        nb = [owner.get((x + dx, y + dy), -1) for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))]
        if any(n == -1 for n in nb[:3]) or any(n != -1 and n < k for n in nb[:3]):
            g[x, y] = "h"
    for (x, y), k in owner.items():
        if (x, y) in g:
            continue
        xs = [xx for (xx, yy), kk in owner.items() if yy == y and kk == k and (xx, yy) not in g]
        a, b = min(xs), max(xs); t = 0 if b == a else (x - a) / (b - a)
        g[x, y] = "L" if t < .3 else ("Y" if t < .75 else "o")
        if y in dark_rows and g[x, y] != "L":
            g[x, y] = "o" if g[x, y] == "Y" else "O"
    for p in white:
        if g.get(p) in ("L", "Y"):
            g[p] = "l"
    return g
