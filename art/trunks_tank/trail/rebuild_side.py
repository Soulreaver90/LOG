r"""
rebuild_side.py - Rebuild the Trunks tank SIDE frames, and prove they are ours.

The side is the owner's drawing, not a swap of mine. My four mask-driven attempts all failed the same way:
I filled the torso with tank and buried the near arm. On a sleeveless top seen from the side the bare arm is
the nearest thing to the viewer and the largest skin area in the frame, and the arm hangs over the BACK half
of the torso silhouette, because the shoulder joint sits toward the back of the chest.

Steps, all from files in this folder:
  1. owner_side_v1.png    the owner's side, drawn from scratch over vanilla      (his)
  2. owner_side_v2.png    his adjustment, 7 px more tank                         (his)
  3. v3 = v2 with the shoulder row 16 put back to v1 at x8, x9, x10              (his call, my 3 px edit)
  4. compose the Super Saiyan form as its head over the one shared body
  5. compare to ..\trunks_tank_base_side.png and ..\trunks_tank_ssj_side.png

Run: py -3.14 -I art\trunks_tank\trail\rebuild_side.py
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SHIP = HERE.parent
HEAD_ROWS = 15
SHOULDER = [(8, 16), (9, 16), (10, 16)]      # v2 made these tank; the owner said that went too far

# Edits made after his drawing, each approved by him on 2026-11-01. They all sit below the head, so the
# Super Saiyan form inherits them through the one shared body. Record them HERE, not only in the shipped
# PNG: this script is the provenance proof, and an edit it does not know about reads as a stale frame.
POST = {
    (9, 18): (0x11, "hold the arm's lit column at x9"),
    (10, 18): (0x13, "the highlight had wandered one to the right"),
    (9, 19): (0x11, "hold the arm's lit column at x9"),
    (10, 19): (0x13, "the highlight had wandered one to the right"),
    (7, 20): (0x4D, "baldric continuity, to match walks 0, 1 and 2"),
}


def indexed(png: Path, pal: list, w: int, h: int) -> bytearray:
    """Re-index an RGBA export against the set palette. Off-palette is a hard error."""
    legal = {}
    for i in range(256):
        legal.setdefault(tuple(pal[i * 3:i * 3 + 3]), i)
    out = bytearray()
    for p in Image.open(png).convert("RGBA").get_flattened_data():
        if p[3] == 0:
            out.append(0)
        elif p[:3] in legal:
            out.append(legal[p[:3]])
        else:
            raise SystemExit(f"{png.name}: rgb{p[:3]} is not in the set palette")
    if len(out) != w * h:
        raise SystemExit(f"{png.name}: {len(out)} px, expected {w * h}")
    return out


def main() -> int:
    van = Image.open(HERE / "vanilla_base_side.png")
    pal, (w, h) = van.getpalette(), van.size

    v1 = indexed(HERE / "owner_side_v1.png", pal, w, h)
    v2 = indexed(HERE / "owner_side_v2.png", pal, w, h)
    base = bytearray(v2)
    for x, y in SHOULDER:
        base[y * w + x] = v1[y * w + x]

    for (x, y), (val, _why) in POST.items():
        base[y * w + x] = val

    ssj = bytearray(base)
    ssj[:HEAD_ROWS * w] = Image.open(HERE / "vanilla_ssj_side.png").tobytes()[:HEAD_ROWS * w]

    v = van.tobytes()
    print(f"step 1  his v1 over vanilla:  {sum(1 for a, b in zip(v, v1) if a != b)} px   (his)")
    print(f"step 2  his v2:               {sum(1 for a, b in zip(v1, v2) if a != b)} px more   (his)")
    print(f"step 3  shoulder back to v1:  {len(SHOULDER)} px   (his call)")
    print(f"step 3b approved later edits: {len(POST)} px   (his call, my hand)")
    print(f"step 4  one body: ssj identical below row {HEAD_ROWS}: "
          f"{bytes(base[HEAD_ROWS * w:]) == bytes(ssj[HEAD_ROWS * w:])}")

    write = "--write" in sys.argv
    ok = True
    for data, name in ((base, "trunks_tank_base_side.png"), (ssj, "trunks_tank_ssj_side.png")):
        same = bytes(data) == Image.open(SHIP / name).tobytes()
        if not same and write:
            out = Image.frombytes("P", (w, h), bytes(data))
            out.putpalette(pal)
            out.save(SHIP / name, transparency=0)
            print(f"step 5  {name}: WROTE the rebuilt frame")
            same = True
        else:
            print(f"step 5  {name}: rebuilt matches shipped = {same}")
        ok &= same
    print("\nOK: the shipped side frames rebuild from vanilla plus his drawing."
          if ok else "\nMISMATCH: shipped side frames are stale.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
