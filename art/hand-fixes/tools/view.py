# r12fix viewer: armor and gi frames of one key as index-class text grids, side by side.
# Usage: py -3 -I view.py <gi set> <anim> <dir> <index> [fix]   (fix = show the r12fix frame as a third grid)
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "permanent"))
from log2_sprites import PALETTE_OFF  # noqa: E402

F = ROOT / "scratch" / "art" / "review" / "frames_r12"
FIX = Path(__file__).parent / "out"
DIRS = {157: ("gi_base_157", "armor_56", 56), 158: ("gi_ssj_158", "armor_59", 59), 159: ("gi_ssj2_159", "armor_59", 59)}
CLASS = {0: ".", 1: "K", 89: "P", 88: "Q", 87: "R", 211: "N", 26: "r", 27: "x", 72: "B", 195: "b",
         114: "S", 115: "s", 116: "t", 117: "u", 113: "d", 2: "W", 43: "W", 44: "w",
         9: "g", 10: "g", 11: "g", 12: "G", 13: "G", 14: "G", 15: "H",
         23: "h", 20: "j", 21: "j", 22: "j", 19: "j", 16: "j", 18: "j",
         79: "A", 80: "A", 81: "a", 64: "e", 65: "e", 34: "o", 35: "o",
         36: "y", 37: "y", 38: "y", 39: "y", 40: "y", 41: "y", 42: "y", 45: "y", 46: "y", 120: "y", 121: "y", 191: "c"}


def palette():
    rom = (ROOT / "scratch" / "build" / "log2_poc_r12.gba").read_bytes()
    pal = {}
    for i in range(1, 256):
        c = int.from_bytes(rom[PALETTE_OFF + 2 * i:PALETTE_OFF + 2 * i + 2], "little")
        pal.setdefault(((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3), i)
    return pal


def load(path, pal):
    im = Image.open(path).convert("RGBA")
    px = [0 if a < 128 else pal[(r & 0xF8, g & 0xF8, b & 0xF8)] for r, g, b, a in im.getdata()]
    return [px[y * im.width:(y + 1) * im.width] for y in range(im.height)]


def name(s, a, d, i):
    return f"{s}_a{a:02}_d{d}_i{i}.png"


def main():
    s, a, d, i = map(int, sys.argv[1:5])
    pal = palette()
    gdir, adir, aset = DIRS[s]
    grids = [load(F / adir / name(aset, a, d, i), pal), load(F / gdir / name(s, a, d, i), pal)]
    if len(sys.argv) > 5:
        grids.append(load(FIX / name(s, a, d, i), pal))
    w = len(grids[0][0])
    head = "    " + "   ".join("".join(str(x % 10) for x in range(w)) for _ in grids)
    print(head)
    for y in range(len(grids[0])):
        print(f"{y:2d}  " + "   ".join("".join(CLASS.get(v, "?") for v in g[y]) for g in grids))


if __name__ == "__main__":
    main()
