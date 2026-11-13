# throwaway: golden sheet helper. Frames as text grids (one char per palette index) for hand edits.
#   gold.py dump               write <form>_d<dir>.txt for the current idle frames (dir 0-2) and orig_<form>_d<dir>.txt
#   gold.py zoom <txt> [s]     render one grid at s x (default 12) to <txt>.png for review
import sys, json
from pathlib import Path
from PIL import Image
L = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG")
W = Path(__file__).parent
sys.path.insert(0, str(L / "scripts" / "permanent"))
CH = {0: ".", 1: "K", 2: "W", 9: "w", 11: "g", 12: "G", 13: "m", 14: "M", 15: "D", 20: "h", 21: "i", 22: "j", 23: "e",
      26: "r", 27: "R", 34: "b", 35: "B", 36: "y", 37: "Y", 38: "o", 39: "O", 44: "l", 46: "L", 120: "c", 49: "v",
      50: "V", 64: "t", 65: "T", 72: "N", 195: "n", 88: "p", 89: "P", 211: "x", 113: "1", 114: "2", 115: "3",
      116: "4", 117: "5", 191: "s", 41: "a", 42: "A", 40: "u", 77: "7", 79: "8", 80: "9", 81: "0", 10: "z",
      18: "f", 19: "F", 45: "Q", 121: "C", 16: "q"}
IX = {c: i for i, c in CH.items()}
FORMS = {"gi_base": "set56", "gi_ssj": "set59", "gi_ssj2": "set58"}
PAL = Image.open(L / "scratch/art/gi_ssj2/frame_2A15DC.png").getpalette()


def rec(folder: Path, d: int) -> tuple:
    for e in json.loads((folder / "manifest.json").read_text()):
        for k in e.get("keys", [e]):
            if (k["anim"], k["dir"], k["index"]) == (0, d, 0):
                return Image.open(folder / e["png"]), k


def to_txt(img: Image.Image) -> str:
    w, h = img.size
    b = img.tobytes()
    return "\n".join("".join(CH[b[y * w + x]] for x in range(w)) for y in range(h)) + "\n"


def from_txt(path: Path) -> Image.Image:
    rows = [r for r in path.read_text().splitlines() if r]
    w = len(rows[0])
    assert all(len(r) == w for r in rows), f"{path.name}: ragged rows"
    img = Image.frombytes("P", (w, len(rows)), bytes(IX[c] for r in rows for c in r))
    img.putpalette(PAL)
    img.info["transparency"] = 0
    return img


def zoom(img: Image.Image, s: int) -> Image.Image:
    rgb = Image.new("RGB", img.size, (150, 150, 150))
    b = img.tobytes()
    for y in range(img.height):
        for x in range(img.width):
            v = b[y * img.width + x]
            if v:
                rgb.putpixel((x, y), tuple(PAL[3 * v:3 * v + 3]))
    return rgb.resize((img.width * s, img.height * s), Image.NEAREST)


if __name__ == "__main__":
    if sys.argv[1] == "dump":
        for form, st in FORMS.items():
            for d in range(3):
                img, k = rec(L / "scratch/art" / form, d)
                (W / f"{form}_d{d}.txt").write_bytes(to_txt(img).encode())
                o, ko = rec(L / "scratch/sprites" / st, d)
                (W / f"orig_{form}_d{d}.txt").write_bytes(to_txt(o).encode())
                print(form, d, img.size, (k["dx"], k["dy"]), "orig", o.size, (ko["dx"], ko["dy"]))
    elif sys.argv[1] == "zoom":
        p = Path(sys.argv[2]); s = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        zoom(from_txt(p), s).save(p.with_suffix(".png"))


def grid_view(paths: list, s: int = 14) -> Image.Image:
    """Grids side by side at s x with a faint pixel grid and column/row numbers every 4 px."""
    from PIL import ImageDraw
    ims = [zoom(from_txt(Path(p)), s) for p in paths]
    W_ = sum(i.width + 30 for i in ims) + 30; H_ = max(i.height for i in ims) + 40
    out = Image.new("RGB", (W_, H_), (150, 150, 150)); d = ImageDraw.Draw(out)
    x0 = 30
    for p, im in zip(paths, ims):
        out.paste(im, (x0, 30))
        for gx in range(0, im.width + 1, s):
            d.line((x0 + gx, 30, x0 + gx, 30 + im.height), fill=(120, 120, 120) if (gx // s) % 4 else (60, 60, 60))
        for gy in range(0, im.height + 1, s):
            d.line((x0, 30 + gy, x0 + im.width, 30 + gy), fill=(120, 120, 120) if (gy // s) % 4 else (60, 60, 60))
        for c in range(0, im.width // s, 4):
            d.text((x0 + c * s + 2, 18), str(c), fill=(0, 0, 0))
        for r in range(0, im.height // s, 4):
            d.text((x0 - 18, 30 + r * s + 2), str(r), fill=(0, 0, 0))
        d.text((x0, 2), Path(p).stem, fill=(0, 0, 0))
        x0 += im.width + 30
    return out


if __name__ == "__main__" and sys.argv[1] == "view":
    grid_view(sys.argv[3:], 14).save(sys.argv[2])
