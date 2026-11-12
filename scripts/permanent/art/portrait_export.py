r"""Export every vanilla dialog portrait from a ROM to 64x64 PNGs, as the reference to draw against.

One file per id, `<id>_vanilla.png`, in the OBJ palette's real colours. These are the pictures the
game shows, pulled straight out of the ROM, so they are what a remaster is measured against.

It never writes a ROM and never touches `art\tables`. Read only, except for the PNGs it writes.

Another release needs its own block and id range, because neither is the same twice (bible B2383,
B2384):

    USA     block 0x3EC9D0   ids  26-114   (the default)
    Europe  block 0x6A97B0   ids  44-132   all 89 byte identical to the USA ones
    Japan   block 0x42EEBC   ids  58-146   54 of the 89 differ from the USA art

Stay inside the dialog range. The entries below it are not dialog portraits and do not use the OBJ
palette, so they come out in invented colours.

Run: py -3.14 -P scripts\permanent\art\portrait_export.py
     py -3.14 -P scripts\permanent\art\portrait_export.py --rom <a rom> --block 0x42EEBC --ids 58-147
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # run it straight, not only as a module

import log_paths                       # noqa: E402
from art import art_tables as A        # noqa: E402

BASE_ROM = log_paths.ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
PATTERN = "*_vanilla.png"              # what this tool owns, and all it will ever delete


def render(px: bytes, pal: list) -> Image.Image:
    img = Image.new("RGBA", (A.SIDE, A.SIDE))
    out = img.load()
    for i, v in enumerate(px):
        out[i % A.SIDE, i // A.SIDE] = (*pal[v], 255)
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rom", help="a ROM to read (default: the base USA ROM)")
    ap.add_argument("--out", help="where to write (default: art\\portraits)")
    ap.add_argument("--block", help="portrait block offset, hex (default the USA 0x3EC9D0)")
    ap.add_argument("--ids", help="id range LO-HI to export (default 26-115)")
    a = ap.parse_args()

    rom_path = Path(a.rom) if a.rom else BASE_ROM
    out = Path(a.out) if a.out else log_paths.ART / "portraits"
    block = int(a.block, 16) if a.block else A.VANILLA_BLOCK
    lo, hi = ((int(v) for v in a.ids.split("-")) if a.ids
              else (A.DIALOG_IDS.start, A.DIALOG_IDS.stop))

    rom = rom_path.read_bytes()
    pal = A.obj_palette(rom)
    out.mkdir(parents=True, exist_ok=True)
    gone = 0
    for f in out.glob(PATTERN):        # only ever its own output, never a hand drawn file
        f.unlink()
        gone += 1

    written, skipped = 0, []
    for pid in range(lo, hi):
        try:
            _, px = A.live_frame(rom, block, pid)
        except Exception:
            skipped.append(pid)
            continue
        if not px or len(px) != A.SIDE * A.SIDE:
            skipped.append(pid)
            continue
        render(px, pal).save(out / f"{pid:03d}_vanilla.png")
        written += 1

    print(f"  removed {gone} file(s) from the previous run (only {PATTERN})")
    print(f"  {written} portraits written from {rom_path.name}, ids {lo}-{hi - 1}")
    if skipped:
        print(f"  {len(skipped)} id(s) did not decode as a portrait: "
              f"{', '.join(str(p) for p in skipped)}")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
