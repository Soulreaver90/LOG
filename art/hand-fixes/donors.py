# r12fix donor finder: for each bad key, the good keys whose armor body (rows from R down) equals the bad key's
# armor body, as is or mirrored, with an x/y shift. A match means the donor's gi body can be copied or mirrored in.
# Usage: py -3 -I donors.py
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import view  # noqa: E402

BAD = {
    157: ["13.0.0", "13.0.2", "13.0.3", "8.0.3", "8.2.2", "16.2.4", "3.0.3", "3.1.3", "3.2.3", "2.2.0", "2.2.2",
          "2.2.3", "12.0.0", "12.0.1", "12.0.2", "12.0.3", "2.0.3", "5.0.2"],
    158: ["13.0.0", "13.0.2", "13.0.3", "8.0.3", "8.2.2", "16.2.4", "3.0.3", "3.1.3", "3.2.3", "2.2.0", "2.2.2",
          "2.2.3", "1.0.0", "1.0.2", "21.0.3", "21.1.3", "21.2.3"],
}


def keys(aset):
    out = {}
    for p in (view.F / view.DIRS[{56: 157, 59: 158}[aset]][1]).glob(f"{aset}_a*_d*_i*.png"):
        if p.stem.endswith("3x"):
            continue
        _, a, d, i = p.stem.split("_")
        out[f"{int(a[1:])}.{d[1:]}.{i[1:]}"] = p
    return out


def body(grid, r0):
    return {(x, y): v for y, row in enumerate(grid) for x, v in enumerate(row) if y >= r0 and v}


def score(tb, db, w, mirror, dx, dy):
    moved = {((w - 1 - x if mirror else x) + dx, y + dy): v for (x, y), v in db.items()}
    keys_ = set(tb) | set(moved)
    return sum(1 for k in keys_ if tb.get(k) != moved.get(k)), len(tb)


def main():
    pal = view.palette()
    for s, aset in ((157, 56), (158, 59)):
        allk = keys(aset)
        grids = {k: view.load(p, pal) for k, p in allk.items()}
        for bad in BAD[s]:
            t = grids[bad]
            w = len(t[0])
            r0 = 17
            tb = body(t, r0)
            best = []
            for k, g in grids.items():
                if k in BAD[s] or len(g[0]) != w or len(g) != len(t):
                    continue
                for mirror in (False, True):
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            d, n = score(tb, body(g, r0 - dy), w, mirror, dx, dy)
                            best.append((d, k, mirror, dx, dy, n))
            best.sort()
            top = [f"{k}{' M' if m else ''} dx{dx} dy{dy}: {d}/{n}" for d, k, m, dx, dy, n in best[:3]]
            print(f"{s} {bad:7}  " + " | ".join(top))


if __name__ == "__main__":
    main()
