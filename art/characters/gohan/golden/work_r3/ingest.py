# Read an owner 3x edit (96x96) back into palette indices and diff it against our frame.
import sys
from pathlib import Path
from PIL import Image
G = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(G / "work"))
from gold import CH, PAL, to_txt, from_txt
RGB = {}
for i in range(256):
    RGB.setdefault(tuple(PAL[3 * i:3 * i + 3]), i)


def ingest(path: Path) -> list:
    im = Image.open(path).convert("RGBA"); px = im.load(); out = []
    for y in range(32):
        row = ""
        for x in range(32):
            r, g, b, a = px[x * 3 + 1, y * 3 + 1]
            if a < 128 or (r, g, b) == (248, 0, 248):
                row += "."
            else:
                i = RGB.get((r, g, b))
                if i is None or i not in CH:
                    i = min((k for k in CH if k), key=lambda k: sum((v - w) ** 2 for v, w in zip((r, g, b), PAL[3 * k:3 * k + 3])))
                    row += CH[i].upper() if False else CH[i]
                    print("approx", (x, y), (r, g, b), "->", i)
                else:
                    row += CH[i]
        out.append(row)
    return out


def diff(a: list, b: list, dx: int = 0) -> list:
    d = []
    for y in range(32):
        for x in range(len(b[0])):
            ca = a[y][x + dx] if 0 <= x + dx < 32 else "."
            if ca != b[y][x]:
                d.append((x, y, b[y][x], ca))
    return d


if __name__ == "__main__":
    own = ingest(Path(sys.argv[1]))
    ours = to_txt(Image.open(sys.argv[2])).splitlines() if sys.argv[2].endswith(".png") else Path(sys.argv[2]).read_text().splitlines()
    best = min(range(-16, 17), key=lambda dx: len(diff(own, ours, dx)))
    print("offset", best)
    for y, r in enumerate(own):
        print("%2d %s   %s" % (y, r, ours[y]))
    for x, y, was, now in diff(own, ours, best):
        print("  (%d,%d) %s -> %s" % (x, y, was, now))
    Path(sys.argv[3]).write_text("\n".join(r[best:best + len(ours[0])] if best >= 0 else ("." * -best + r)[:len(ours[0])] for r in own) + "\n")
