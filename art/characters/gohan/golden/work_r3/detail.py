# Detail pass in the Buu's Fury style: keep every outline/separator pixel; re-shade each hair clump with a
# highlight streak on its lit (left) third, white/pale at the tip, mid-tone body, shaded right edge, darker base.
HAIR = set("LlYoOWyc")


def clumps(rows, ymax):
    seen, out = set(), []
    for y in range(ymax + 1):
        for x in range(32):
            if rows[y][x] in HAIR and (x, y) not in seen:
                stack, comp = [(x, y)], []
                seen.add((x, y))
                while stack:
                    p = stack.pop(); comp.append(p)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        q = (p[0] + dx, p[1] + dy)
                        if 0 <= q[0] < 32 and 0 <= q[1] <= ymax and q not in seen and rows[q[1]][q[0]] in HAIR:
                            seen.add(q); stack.append(q)
                out.append(comp)
    return out


def detail(rows, ymax, keep=()):
    g = [list(r) for r in rows]
    for comp in clumps(rows, ymax):
        if any(p in keep for p in comp):
            continue
        ys = [y for _, y in comp]; top, bot = min(ys), max(ys); hgt = bot - top + 1
        for y in range(top, bot + 1):
            xs = sorted(x for x, yy in comp if yy == y)
            if not xs:
                continue
            a, b = xs[0], xs[-1]; n = b - a + 1
            hi = a + (n - 1) // 3
            depth = (y - top) / max(1, hgt - 1)
            for x in xs:
                if x == hi:
                    c = "W" if (y == top and hgt >= 5) else ("l" if depth < .35 else "L")
                elif x == b and n >= 3:
                    c = "o" if depth < .7 else "O"
                elif x < hi:
                    c = "L" if depth < .5 else "Y"
                else:
                    c = "Y" if depth < .7 else "o"
                g[y][x] = c
    return ["".join(r) for r in g]
