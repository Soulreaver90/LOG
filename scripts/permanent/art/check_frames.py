r"""Check hand drawn sprite frames against the ROM: size, palette and transparency.

Why: the ROM stores a palette INDEX per pixel, not a colour. A frame drawn in an editor and saved as
RGBA is fine to work in, but every one of its colours has to exist in the LoG II shared OBJ palette
or it cannot be written back. This says, per frame, whether it can, and names the exact pixels that
cannot before any of them reach a build.

It never writes a frame and never touches the ROM. Read only.

What it checks, per file:
  1. the size matches the vanilla frame of the same name
  2. every opaque colour exists in the shared OBJ palette (rom:0x1DA6C8)
  3. transparency is all-or-nothing per pixel: the ROM has no partial alpha

Run: py -3.14 -P scripts\permanent\art\check_frames.py <folder with your frames> [--set 128]
     py -3.14 -P scripts\permanent\art\check_frames.py <folder> --set 128 --quiet
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder
import log_paths  # noqa: E402

ROM = log_paths.BASE_ROM
SETS = log_paths.SPRITES
OBJ_PAL, ENTRIES = 0x1DA6C8, 256
RUNTIME = {0, 168}            # index 0 is transparent, 168 is written at run time (bible B0250)


def palette(rom: bytes) -> dict:
    """{(r, g, b): [index, ...]} for the shared OBJ palette, 5 bit channels scaled to 8."""
    out = {}
    for i in range(ENTRIES):
        c = rom[OBJ_PAL + i * 2] | (rom[OBJ_PAL + i * 2 + 1] << 8)
        out.setdefault(((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8), []).append(i)
    return out


def check(path: Path, pal: dict, vanilla: Path) -> list:
    """Problems with one frame, as plain sentences. Empty means it is ready to import."""
    bad = []
    img = Image.open(path).convert("RGBA")
    if vanilla.is_file():
        want = Image.open(vanilla).size
        if img.size != want:
            bad.append(f"size is {img.size[0]}x{img.size[1]}, vanilla is {want[0]}x{want[1]}")
    else:
        bad.append(f"no vanilla frame named {vanilla.name} to compare against")

    px = img.load()
    partial, unknown = 0, Counter()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if a != 255:
                partial += 1
                continue
            if (r, g, b) not in pal:
                unknown[(r, g, b)] += 1
    if partial:
        bad.append(f"{partial} pixel(s) are part transparent. The ROM has no partial alpha")
    for colour, n in unknown.most_common(6):
        bad.append(f"colour #{colour[0]:02X}{colour[1]:02X}{colour[2]:02X} is not in the OBJ "
                   f"palette ({n} pixel(s))")
    if len(unknown) > 6:
        bad.append(f"...and {len(unknown) - 6} more colours not in the palette")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder", help="folder of frames, searched recursively")
    ap.add_argument("--set", default="128", help="vanilla set to compare names against")
    ap.add_argument("--quiet", action="store_true", help="list only the frames with problems")
    a = ap.parse_args()

    folder = Path(a.folder)
    if not folder.is_dir():
        raise SystemExit(f"not a folder: {folder}")
    van = SETS / f"set{a.set}"
    if not van.is_dir():
        raise SystemExit(f"no vanilla export for set {a.set}: {van}")

    pal = palette(ROM.read_bytes())
    files = sorted(p for p in folder.rglob("*.png") if "_strip" not in p.name)
    ready, problems = 0, 0
    for p in files:
        # A laid-out frame is named <index>_frame_<addr>.png; the vanilla export drops the prefix.
        name = p.name.split("_", 1)[1] if p.name[:2].isdigit() and "_" in p.name else p.name
        bad = check(p, pal, van / name)
        if bad:
            problems += 1
            print(f"{p.relative_to(folder)}")
            for line in bad:
                print(f"    {line}")
        else:
            ready += 1
            if not a.quiet:
                print(f"{p.relative_to(folder)}  OK")
    print(f"\n{ready} frame(s) ready to import, {problems} with problems, {len(files)} checked.")
    print("OK means every colour exists in the palette. It does NOT mean the drawing is right:")
    print("that is the owner's eye, on the strips.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
