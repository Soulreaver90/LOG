r"""Turn hand drawn RGBA frames into indexed frames that carry the LoG II shared OBJ palette.

Why: the owner draws in an editor and saves RGBA. Every review tool here wants an indexed frame,
because the ROM stores a palette INDEX per pixel. `sprite_loop.py` and `sprite_look.py` both refuse
an RGBA file, so an art round used to stall on a format, not on the drawing.

Each opaque colour must already exist in the OBJ palette, which `check_frames.py` proves. A colour
that sits at several indices takes the LOWEST index that is not reserved at run time. A colour that
is not in the palette stops the run and is named, because guessing a near match changes his art.

Alpha is all or nothing in the ROM, so a part transparent pixel is refused, never rounded.

Some editors export a KEY COLOUR instead of an alpha channel. Piskel uses magenta. `--key` names
that colour and treats it as clear. Without it those pixels are refused as an unknown colour,
which is the safe default: a key colour guessed wrong erases part of the drawing.

Reads the base ROM and the frames. Writes only the files it names, and never over one that exists.

API: index_of(rom) -> {(r, g, b): index}; flat_palette(rom) -> 768 RGB bytes for a mode P image;
     frame_indices(src, want, pal, key=None) -> ((w, h), one index per pixel), which raises with the
     exact reason. A patch that puts his drawing in the ROM reads it through frame_indices, so the
     build and this tool refuse the same frame for the same reason.

Run: py -3.14 -P scripts\permanent\art\to_indexed.py <out folder> <frame.png> [<frame.png> ...]
"""
import argparse
from pathlib import Path

from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder
import log_paths  # noqa: E402

LOG = Path(__file__).resolve().parents[3]
ROM = log_paths.BASE_ROM
OBJ_PAL, ENTRIES = 0x1DA6C8, 256                    # the shared OBJ palette, as check_frames.py reads it
RUNTIME = {0, 168}                                  # 0 is transparent, 168 is written at run time (B0250)
MAX_NAMED = 6                                       # off-palette colours listed before the message stops


def index_of(rom: bytes) -> dict:
    """{(r, g, b): index}, lowest usable index per colour."""
    out = {}
    for i in range(ENTRIES):
        if i in RUNTIME:
            continue
        c = rom[OBJ_PAL + i * 2] | (rom[OBJ_PAL + i * 2 + 1] << 8)
        out.setdefault(((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8), i)
    return out


def flat_palette(rom: bytes) -> list:
    pal = []
    for i in range(ENTRIES):
        c = rom[OBJ_PAL + i * 2] | (rom[OBJ_PAL + i * 2 + 1] << 8)
        pal += [(c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8]
    return pal


def frame_indices(src: Path, want: dict, pal: list, key: tuple = None) -> tuple:
    """((w, h), one palette index per pixel) for one hand drawn frame. Raises with the exact reason.

    A frame this tool already wrote is mode P, and its own indices are taken as they stand, once its
    embedded palette is proved to be the OBJ palette. Reading it back through the colour map instead
    would return the LOWEST index of each colour, which is a different index for the same picture.
    Any other mode goes through the colour map, which refuses an unknown colour and partial alpha.
    """
    with Image.open(src) as img:
        w, h = img.size
        if img.mode == "P":
            held = list(img.getpalette() or [])
            held += [0] * (len(pal) - len(held))
            data = img.tobytes()
            reserved = sorted(set(data) & (RUNTIME - {0}))
            if reserved:
                raise ValueError(f"{src.name}: uses index {reserved[0]}, which the game writes at run time")
            # Only the indices the drawing USES have to agree. A build may repaint an entry the
            # drawing never touches, and refusing the whole palette would reject a frame over it.
            moved = [i for i in sorted(set(data)) if held[i * 3:i * 3 + 3] != pal[i * 3:i * 3 + 3]]
            if moved:
                i = moved[0]
                raise ValueError(f"{src.name}: index {i} is {tuple(held[i * 3:i * 3 + 3])} in the frame and "
                                 f"{tuple(pal[i * 3:i * 3 + 3])} in this ROM, so {len(moved)} of its colours "
                                 f"would change")
            return (w, h), data
        px = img.convert("RGBA").load()
    data, bad, partial = bytearray(), {}, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0 or (key and (r, g, b) == key):
                data.append(0)
            elif a != 255:
                partial += 1
                data.append(0)
            elif (r, g, b) in want:
                data.append(want[(r, g, b)])
            else:
                bad[(r, g, b)] = bad.get((r, g, b), 0) + 1
                data.append(0)
    if partial:
        raise ValueError(f"{src.name}: {partial} pixel(s) are part transparent. The ROM has no partial alpha")
    if bad:
        named = ", ".join(f"#{c[0]:02X}{c[1]:02X}{c[2]:02X} x{n}" for c, n in sorted(bad.items())[:MAX_NAMED])
        raise ValueError(f"{src.name}: {len(bad)} colour(s) not in the OBJ palette: {named}")
    return (w, h), bytes(data)


def convert(src: Path, want: dict, pal: list, out: Path, key: tuple = None) -> str:
    try:
        (w, h), data = frame_indices(src, want, pal, key)
    except ValueError as problem:
        return str(problem).split(": ", 1)[-1]
    if out.is_file():
        return f"{out} already exists. I never overwrite a frame"
    im = Image.new("P", (w, h))
    im.putpalette(pal)
    im.putdata(list(data))
    im.save(out)
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("outdir", help="where the indexed copies go")
    ap.add_argument("frames", nargs="+", help="RGBA frames to convert")
    ap.add_argument("--key", help="hex colour the editor used for clear, such as F800F8 from Piskel")
    a = ap.parse_args()

    key = None
    if a.key:
        h = a.key.lstrip("#")
        key = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    rom = ROM.read_bytes()
    want, pal = index_of(rom), flat_palette(rom)
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fails = 0
    for f in a.frames:
        src = Path(f)
        problem = convert(src, want, pal, outdir / src.name, key)
        if problem:
            fails += 1
            print(f"{src.name}\n    {problem}")
        else:
            print(f"{src.name} -> {outdir / src.name}")
    print(f"\n{len(a.frames) - fails} converted, {fails} refused.")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
