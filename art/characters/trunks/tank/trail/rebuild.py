r"""
rebuild.py - Rebuild the Trunks tank frames from vanilla, and prove they are ours.

This is the clean-room trail. It runs end to end from the two vanilla frames in this folder, with nothing
from any other hack, and it ends by byte-comparing its output to the frames we ship. If it prints OK, the
shipped frames are exactly what this script makes from vanilla.

Why it matters: an outfit swap made from a vanilla frame will resemble anyone else's swap of the same frame,
because both start from the same pixels. The resemblance is not evidence either way. This running trail is.

Inputs, all in this folder and none of them scratch:
  vanilla_base_front.png                  set 128 anim 0 dir 0, straight from the USA ROM
  vanilla_ssj_front.png                   set 134 anim 0 dir 0, straight from the USA ROM
  2026-11-01_owner_edit_base_front.png    the owner's pass over step 2, 11 px

Steps:
  1. draw the tank body over vanilla, from the BODY grid below          (mine)
  2. apply the owner's edit                                            (his, 11 px)
  3. compose the Super Saiyan form as its head over the one shared body
  4. compare to ..\trunks_tank_base_front.png and ..\trunks_tank_ssj_front.png

Run: py -3.14 -I art\trunks_tank\trail\rebuild.py
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SHIP = HERE.parent
HEAD_ROWS = 15          # rows 0-14 are hair, face and eyes, and stay vanilla

# Step 1. The drawn body. One token a pixel, '..' is transparent, else a palette index in hex.
# Rows 0-14 are not here because they are vanilla and untouched.
# x:        0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
BODY = {
 15: "..   0F   0B   ..   ..   17   12   11   11   13   15   17   ..   ..   ..   ..",   # jaw vanilla; sword hilt in grey
 16: "..   ..   0B   17   13   01   17   17   17   17   17   01   13   17   ..   ..",   # hilt on the shoulder; straps x5 x11
 17: "..   ..   17   13   11   01   13   11   13   11   13   01   11   13   17   ..",   # shoulders slope; chest x6-10 vanilla
 18: "..   ..   17   13   11   01   01   13   13   13   01   01   11   13   17   ..",   # chest x6-10 vanilla
 19: "..   ..   17   13   11   01   4D   21   4D   01   01   01   11   13   17   ..",   # belt vanilla
 20: "..   17   13   11   ..   ..   01   0F   0F   4D   4D   ..   ..   11   13   17",   # arms swing clear of the body
 21: "..   17   13   11   ..   ..   25   4D   02   4D   27   ..   ..   11   13   17",
 22: "15   11   15   ..   ..   ..   0B   0D   0F   0D   0D   ..   ..   15   11   17",   # hands vanilla
 23: "17   11   13   17   ..   0D   0B   0D   0F   0D   0F   0F   17   13   13   17",   # hands vanilla
 24: "..   17   17   ..   0D   0D   0D   0F   0F   0F   0D   0F   ..   17   17   ..",   # vanilla, untouched
}


def draw_body(vanilla: Image.Image) -> Image.Image:
    data, (w, h) = bytearray(vanilla.tobytes()), vanilla.size
    for y, row in BODY.items():
        tok = row.split()
        if len(tok) != w:
            raise SystemExit(f"row {y}: {len(tok)} tokens, expected {w}")
        for x, t in enumerate(tok):
            data[y * w + x] = 0 if t == ".." else int(t, 16)
    out = Image.frombytes("P", (w, h), bytes(data))
    out.putpalette(vanilla.getpalette())
    return out


def apply_edit(drawn: Image.Image, edit_png: Path) -> Image.Image:
    """Re-index the owner's RGBA export against the set palette. Any off-palette colour is a hard error."""
    pal = drawn.getpalette()
    legal = {}
    for i in range(256):
        legal.setdefault(tuple(pal[i * 3:i * 3 + 3]), i)
    data = bytearray()
    for p in Image.open(edit_png).convert("RGBA").get_flattened_data():
        if p[3] == 0:
            data.append(0)
        elif p[:3] in legal:
            data.append(legal[p[:3]])
        else:
            raise SystemExit(f"{edit_png.name}: rgb{p[:3]} is not in the set palette")
    out = Image.frombytes("P", drawn.size, bytes(data))
    out.putpalette(pal)
    return out


def compose(head: Image.Image, body: Image.Image) -> Image.Image:
    w, _ = body.size
    data = bytearray(body.tobytes())
    data[:HEAD_ROWS * w] = head.tobytes()[:HEAD_ROWS * w]
    out = Image.frombytes("P", body.size, bytes(data))
    out.putpalette(body.getpalette())
    return out


def main() -> int:
    van_base = Image.open(HERE / "vanilla_base_front.png")
    van_ssj = Image.open(HERE / "vanilla_ssj_front.png")

    drawn = draw_body(van_base)
    base = apply_edit(drawn, HERE / "2026-11-01_owner_edit_base_front.png")
    ssj = compose(van_ssj, base)

    w = base.size[0]
    mine = sum(1 for a, b in zip(van_base.tobytes(), drawn.tobytes()) if a != b)
    his = sum(1 for a, b in zip(drawn.tobytes(), base.tobytes()) if a != b)
    print(f"step 1  drawn over vanilla: {mine} px changed   (mine)")
    print(f"step 2  owner's edit:       {his} px changed   (his)")
    print(f"step 3  one body: ssj identical to base below row {HEAD_ROWS}: "
          f"{base.tobytes()[HEAD_ROWS * w:] == ssj.tobytes()[HEAD_ROWS * w:]}")

    ok = True
    for built, name in ((base, "trunks_tank_base_front.png"), (ssj, "trunks_tank_ssj_front.png")):
        same = built.tobytes() == Image.open(SHIP / name).tobytes()
        ok &= same
        print(f"step 4  {name}: rebuilt matches shipped = {same}")
    print("\nOK: the shipped frames rebuild from vanilla." if ok else "\nMISMATCH: shipped frames are stale.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
