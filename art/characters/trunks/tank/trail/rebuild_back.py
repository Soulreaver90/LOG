r"""
Adopt the owner's BACK frame, and derive the Super Saiyan form from it.

His frame is the base form. The Super Saiyan cannot be a copy of it, because hair is form specific: base hair
is the purple ramp (E5, 64, 62) and Super Saiyan is the gold ramp (14, 2E, 78, 02). Skin, black and grey are
the same in both.

So the Super Saiyan frame is built by replaying his decision for each jacket pixel, with hair mapped by role:
  E5 dark  -> 14 dark
  64 mid   -> 2E mid
Everything he made skin, black or clear is copied as is.

Head and body boundary: his hair now reaches row 15, so rows 0-15 are head and the shared body starts at 16.

Run: py -3.14 -I scratch\trunks\adopt_back.py
"""
import sys
from pathlib import Path

from PIL import Image

S = Path(__file__).resolve().parent
SHIP = S.parent
JACKET = {0x51, 0x50, 0x4F, 0x4E}
BASE_HAIR_TO_SSJ = {0xE5: 0x14, 0x64: 0x2E, 0x62: 0x78}
BODY_FROM = 16


def main() -> None:
    vb = Image.open(S / "vanilla_base_back.png")
    pal, (w, h) = vb.getpalette(), vb.size
    v = vb.tobytes()
    base = bytearray(Image.open(S / "owner_back_indexed.png").tobytes())
    ssj = bytearray(Image.open(S / "vanilla_ssj_back.png").tobytes())

    mapped = copied = 0
    for y in range(13, h):
        for x in range(w):
            if v[y * w + x] not in JACKET:
                continue
            his = base[y * w + x]
            if his in BASE_HAIR_TO_SSJ:
                ssj[y * w + x] = BASE_HAIR_TO_SSJ[his]
                mapped += 1
            else:
                ssj[y * w + x] = his
                copied += 1
    # Below the head the two forms must be the same bytes, so take his body wholesale.
    ssj[BODY_FROM * w:] = base[BODY_FROM * w:]

    vs = Image.open(S / "vanilla_ssj_back.png").tobytes()
    print(f"his jacket decisions replayed: {mapped} hair mapped by role, {copied} copied as is")
    print(f"base changed vs vanilla: {sum(1 for a, b in zip(v, base) if a != b)} px")
    print(f"ssj  changed vs vanilla: {sum(1 for a, b in zip(vs, ssj) if a != b)} px")
    print(f"one body, forms identical below row {BODY_FROM}: "
          f"{bytes(base[BODY_FROM*w:]) == bytes(ssj[BODY_FROM*w:])}")
    print(f"hair stays form specific: base 0x{base[14*w+5]:02X}, ssj 0x{ssj[14*w+5]:02X}")
    print(f"ssj hair rows 0-12 untouched: {vs[:13*w] == bytes(ssj[:13*w])}")

    ok = True
    for data, name in ((base, "trunks_tank_base_back.png"), (ssj, "trunks_tank_ssj_back.png")):
        same = bytes(data) == Image.open(SHIP / name).tobytes()
        ok &= same
        print(f"  {name}: rebuilt matches shipped = {same}")
    print("\nOK: the shipped back frames rebuild from vanilla plus his drawing."
          if ok else "\nMISMATCH: shipped back frames are stale.")
    return 0 if ok else 1


SUPERSEDED_BY = r"scripts\one-time\2026-11-02-trunks-ssj\derive.py"

# Exit guard. This script reads trail\owner_back_indexed.png, which is NINE pixels behind the shipped
# art\trunks_tank\trunks_tank_base_back.png: the owner redrew rows 12 and 13 so the hair rotates with
# the torso. Its own self check already prints MISMATCH for the base frame. Running it would rebuild
# the old hair over his redraw, so it refuses. The replacement derives every tank frame from vanilla
# plus the CURRENT approved art, and guards the result six ways.
if __name__ == "__main__":
    raise SystemExit(
        "rebuild_back.py is superseded and its input art is stale.\n"
        f"Use {SUPERSEDED_BY} instead.\n"
        "Run that with no flags for a report, or --write to create PNGs."
    )
