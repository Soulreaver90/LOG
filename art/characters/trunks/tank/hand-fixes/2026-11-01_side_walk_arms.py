r"""
Hand fix, by eye: restore the arm the rule painted over, in side walk frames 0 and 2.

The owner found both, looking at stills:
  "the issue with frame 2 is the closest arm, its drawn over with gray sprites"
  "frame 4 has black tank drawn over the farther arm"
(his frame 2 is walk 0, his frame 4 is walk 2, counting the idle as frame 1.)

Both are ONE mistake. My drawing rule knows about a single arm, the one at or behind column 8. A walking
figure has TWO, and the other swings forward into LOW x, exactly where the rule says "not arm". So the
forward sleeve fell through to whatever branch came next: trouser grey below the belt in walk 0, black tank
at the chest rows in walk 2.

Why this is a hand fix and not a rule change. I tried to make the rule find it, by flood filling the garment
from the bare skin of a hand. It leaks: the tank and the sleeve are one contiguous garment mass, so the fill
runs straight through the tank. Depth, not connectivity, separates them, and nothing in the frame encodes
depth. docs\sprite-guide.md section 4: fixes are made by eye, frame by frame, and rule passes over art are
not allowed.

Shading follows the owner's own convention, read off his approved idle: dark 17 at the limb edges, 11 on the
lit side, 13 between.

Run: py -3.14 -P art\trunks_tank\hand-fixes\2026-11-01_side_walk_arms.py
"""
import sys
from pathlib import Path

from PIL import Image

ART = Path(r"C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\art\trunks_tank")
W, H = 16, 32
JACKET = {0x51, 0x50, 0x4F, 0x4E}
GREY = {0x0B, 0x0D, 0x0F}

# walk 0: the near arm swings FORWARD. Sleeve x3-6 running down to the hand already drawn at x0-2.
# x5 and x6 on row 20 are hip, not arm, so they take trouser grey instead of the jacket left behind there.
WALK0 = {
    (2, 20): 0x17, (3, 20): 0x11, (4, 20): 0x13,
    (5, 20): 0x0F, (6, 20): 0x0D,
    (3, 21): 0x17, (4, 21): 0x11, (5, 21): 0x13, (6, 21): 0x17,
    (3, 22): 0x17, (4, 22): 0x11, (5, 22): 0x17,
    (3, 23): 0x17, (4, 23): 0x17,
}

# walk 2: the FAR arm's sleeve, x3-4, sitting above the hand already drawn at x0-3.
WALK2 = {
    (3, 18): 0x17, (4, 18): 0x13,
    (3, 19): 0x17, (4, 19): 0x11,
    (4, 20): 0x11,
    (4, 21): 0x13,
    (3, 22): 0x17, (4, 22): 0x13,
}

FIXES = {"trunks_tank_base_side_walk_0.png": WALK0, "trunks_tank_base_side_walk_2.png": WALK2}


def main() -> int:
    for name, edits in FIXES.items():
        path = ART / name
        im = Image.open(path)
        pal, d = im.getpalette(), bytearray(im.tobytes())
        before = bytes(d)
        for (x, y), v in edits.items():
            d[y * W + x] = v
        out = Image.frombytes("P", (W, H), bytes(d))
        out.putpalette(pal)
        out.save(path, transparency=0)

        skin = sum(1 for i, v in enumerate(d) if v in (0x11, 0x13, 0x15, 0x17, 0x18))
        changed = sum(1 for a, b in zip(before, d) if a != b)
        left = sum(1 for y in range(13, 24) for x in range(W) if d[y * W + x] in JACKET)
        grey = sum(1 for y in range(17, 24) for x in range(W) if d[y * W + x] in GREY)
        print(f"  {name}: {changed} px hand edited | skin now {skin} | grey rows17-23 {grey} | "
              f"jacket left {left}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
