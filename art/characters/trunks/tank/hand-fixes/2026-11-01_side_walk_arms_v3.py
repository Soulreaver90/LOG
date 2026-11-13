r"""
Hand fix v3, by eye: give frame 2's forward arm a shoulder.

After v2 the forward arm in side walk 0 started at row 20, so it sprouted from his hip. Rows 17 to 19 at
x4-6 were still black tank. In a side view an arm swung FORWARD passes in front of the torso, so those rows
are arm, and the tank keeps x7-9, which is the 3 px width his approved idle uses.

Arm widths after this, measured: forward arm 3 px, back arm 3 px, both inside the 3 to 4 px his idle uses.

Run: py -3.14 -P art\trunks_tank\hand-fixes\2026-11-01_side_walk_arms_v3.py
"""
import sys
from pathlib import Path

from PIL import Image

ART = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\art\trunks_tank")
W, H = 16, 32
SKIN = {0x11, 0x12, 0x13, 0x15, 0x17, 0x18}

EDITS = {
    (4, 17): 0x17,
    (4, 18): 0x17, (5, 18): 0x11, (6, 18): 0x13,
    (4, 19): 0x17, (5, 19): 0x11, (6, 19): 0x13,
}


def main() -> int:
    path = ART / "trunks_tank_base_side_walk_0.png"
    im = Image.open(path)
    pal, d = im.getpalette(), bytearray(im.tobytes())
    for (x, y), v in EDITS.items():
        d[y * W + x] = v
    out = Image.frombytes("P", (W, H), bytes(d))
    out.putpalette(pal)
    out.save(path, transparency=0)

    print(f"  {path.name}: {len(EDITS)} px hand edited")
    for y in range(16, 24):
        skin = [x for x in range(W) if d[y * W + x] in SKIN]
        tank = [x for x in range(W) if d[y * W + x] == 0x01]
        print(f"    y{y}: skin x{skin}  tank x{tank}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
