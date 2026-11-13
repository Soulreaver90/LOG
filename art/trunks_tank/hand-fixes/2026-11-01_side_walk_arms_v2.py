r"""
Hand fix v2, by eye: thin the arms to the owner's own width, and give the torso back.

What he said, looking at stills:
  "frame 4, the farther arm in the back, you basically filled the frames of the jacket making his arm thick"
  "and the arm is still wrong in frame 2. Look at the jacket in frame one"

Measured off frame 1, his approved idle:

  row   jacket sleeve   HIS arm
  y16   7 px            3 px   (he CUT 4)
  y17   7 px            3 px   (he CUT 1, 2 became tank)
  y18   6 px            4 px   (2 became tank)
  y19   6 px            4 px   (2 became tank)
  y20   6 px            3 px
  y21   5 px            3 px

So a bare arm is 3 px, 4 at the widest. A sleeve is 6 to 8. I had filled the sleeve outline with skin and
cut nothing, which is the rule I wrote in the guide and then only ever applied at the collar: A GARMENT ADDS
BULK, SO REMOVING IT MUST SHRINK THE SILHOUETTE. A sleeve is bulk too.

Second error, in frame 2 only. The hands are the anchor that is never ambiguous, because vanilla already
draws them bare. Frame 2 has hands at x0-2 and at x12-14. NOTHING anchors an arm at x8-9, yet my fixed
column band painted x8-9 as skin down five rows. That is his torso. It becomes tank.

Run: py -3.14 -P art\trunks_tank\hand-fixes\2026-11-01_side_walk_arms_v2.py
"""
import sys
from pathlib import Path

from PIL import Image

ART = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\art\trunks_tank")
W, H = 16, 32
SKIN = {0x11, 0x12, 0x13, 0x15, 0x17, 0x18}
JACKET = {0x51, 0x50, 0x4F, 0x4E}
LINE, MID, LIT, TANK, TROUSER, CLEAR = 0x17, 0x13, 0x11, 0x01, 0x0D, 0x00

# Frame 2 (walk 0). Hands at x0-2 and x12-14. x8-9 is torso, not arm.
WALK0 = {
    (8, 16): TANK, (9, 16): TANK,
    (8, 17): TANK, (9, 17): TANK,
    (8, 18): TANK, (9, 18): TANK,
    (8, 19): TANK, (9, 19): TANK,
    (8, 20): TROUSER, (9, 20): 0x0F,
}

# Frame 4 (walk 2). The back arm tapers shoulder to hand, 3 px wide, and the sleeve bulk is cut.
# Columns kept: y16-17 x10-12, y18-19 x11-13, y20-21 x12-14.
WALK2 = {
    (10, 16): LINE, (11, 16): LIT, (12, 16): LINE, (13, 16): CLEAR,
    (8, 17): TANK, (9, 17): TANK,
    (10, 17): LINE, (11, 17): LIT, (12, 17): LINE,
    (9, 18): CLEAR, (10, 18): CLEAR,
    (11, 18): LINE, (12, 18): LIT, (13, 18): LINE,
    (9, 19): CLEAR, (10, 19): CLEAR, (14, 19): CLEAR,
    (11, 19): LINE, (12, 19): LIT, (13, 19): LINE,
    (10, 20): CLEAR, (11, 20): CLEAR,
    (12, 20): LINE, (13, 20): LIT, (14, 20): LINE,
    (11, 21): CLEAR, (14, 21): LINE,
}

FIXES = {"trunks_tank_base_side_walk_0.png": WALK0, "trunks_tank_base_side_walk_2.png": WALK2}


def main() -> int:
    for name, edits in FIXES.items():
        path = ART / name
        im = Image.open(path)
        pal, d = im.getpalette(), bytearray(im.tobytes())
        for (x, y), v in edits.items():
            d[y * W + x] = v
        out = Image.frombytes("P", (W, H), bytes(d))
        out.putpalette(pal)
        out.save(path, transparency=0)

        print(f"  {name}: {len(edits)} px hand edited")
        for y in range(15, 23):
            run = [x for x in range(W) if d[y * W + x] in SKIN]
            groups, cur = [], []
            for x in run:
                if cur and x != cur[-1] + 1:
                    groups.append(cur)
                    cur = []
                cur.append(x)
            if cur:
                groups.append(cur)
            wide = [g for g in groups if len(g) > 4]
            print(f"    y{y}: skin runs {[f'{g[0]}-{g[-1]}({len(g)})' for g in groups]}"
                  f"{'   <-- still over 4 px' if wide else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
