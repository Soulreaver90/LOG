r"""
2026-11-08_drop_strap_and_reveals.py - Take the sword strap off the tank, and undo the gear reveals
                                       an earlier pass added. Staged, not shipped.

Reads  art\trunks_tank\*.png
Writes art\trunks_tank\proposed\2026-11-08\*.png, same file names. The live PNGs are NOT touched,
       because tests\test_trunks_tank.py pins what the live frames may contain. See the task report.

Run:   py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_drop_strap_and_reveals.py

Why:   the owner dropped the scabbard, then the strap: "the tank wears no scabbard AND no strap".
       A strap with no sword on it has nothing to carry.

Method: every pixel below is a HAND call, written as (x, y) -> new index with the reason. Each entry
       also states the index it expects to find, so a frame that has moved on stops the script instead
       of being painted blind. No rule runs over the art.

The one thing this script does NOT do: it keeps every BELT pixel, although the belt shares the strap's
       two palette indices, 47 and 4D. Index 4D is the strap AND the belt's own highlight. Three
       separate measurements say the waist pixels are belt:
       1. The motifs `4D 21 4D` and `25 4D 02 4D 27` appear in the idle and in all four front walk
          frames, and move as one rigid unit with the hips.
       2. Set 129 and set 130 wear a belt and no strap, and they draw their own belt at (9,20),
          (7,21) and (9,21) of the front idle, which are three of those pixels.
       3. The owner's own side drawing, art\trunks_tank\trail\owner_side_v1.png, puts 25 at (7,20),
          where a later pass wrote 4D "for baldric continuity". This script puts his 25 back.
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ART = HERE.parent
OUT = ART / "proposed" / "2026-11-08"

CUT = 0x00          # the garment was bulk standing in open air
TANK = 0x01         # the black tank
SKIN_D, SKIN_M, SKIN_L = 0x17, 0x13, 0x11
BELT_LIT = 0x25     # the belt's yellow, the owner's own value at (7,20)
TROUSER = 0x0F
HAIR_BASE, HAIR_SSJ = 0xE5, 0x14

# ===== the hand calls =====
# Each entry is (x, y): (expected index now, new index, why).

FRONT_IDLE = {
    (4, 16): (0x47, SKIN_M, "strap off the shoulder: the mid skin tone the body grid held before it"),
    (4, 17): (0x47, SKIN_L, "strap off the chest: the arm's lit column, as rows 18 and 19 already are"),
    (5, 18): (0x4D, TANK, "strap off the chest: the tank's left edge, as rows 17 and 19 already are"),
    (11, 21): (0x22, CUT, "scabbard reveal: row 20 is already clear at x11, so the hip narrows"),
    (12, 21): (0x23, CUT, "scabbard reveal: same, and it restores the vanilla hip width"),
    (12, 22): (0x09, CUT, "sword metal reveal beside the hip"),
}

FRONT_WALK_0 = {
    (5, 18): (0x47, SKIN_L, "strap off the chest: the arm's lit column, as row 19 x5 already is"),
    (6, 19): (0x4D, TANK, "strap off the chest: the tank, as rows 18 and 20 at x6 already are"),
}

FRONT_WALK_2 = {
    (5, 17): (0x47, TANK, "strap off the chest: the tank's left edge, down to row 19 x5"),
    (5, 18): (0x47, TANK, "strap off the chest: the same edge"),
}

SIDE_IDLE = {
    (5, 19): (0x4D, TANK, "strap off the chest: x4 and x6 on this row are already tank"),
    (7, 20): (0x4D, BELT_LIT, "the owner drew 25 here; a later pass overwrote it for strap continuity"),
    (4, 17): (0x4E, CUT, "leftover jacket on the chest's front edge, with row 16 x4 already clear"),
    (11, 20): (0x23, CUT, "scabbard reveal behind the hip"),
    (11, 21): (0x21, CUT, "scabbard reveal behind the hip; vanilla starts the scabbard at row 22"),
}

SIDE_WALK_0 = {
    (7, 20): (0x4D, BELT_LIT, "strap reveal on the belt row: the belt runs on to x8 and x9"),
}

SIDE_WALK_2 = {
    (5, 19): (0x4D, TANK, "strap off the chest: x6 to x9 on this row are already tank"),
    (7, 20): (0x4D, TANK, "strap: this frame sits one row low, so this is the idle's chest row"),
    (4, 17): (0x4E, SKIN_D, "leftover jacket, but row 16 x4 is SKIN here, so it fills, not cuts"),
    (11, 20): (0x23, SKIN_D, "scabbard reveal between the tank and the far arm: the arm's dark edge"),
    (11, 21): (0x23, SKIN_D, "the same, and row 19 already carries 17 at x10 and x11"),
}

BACK_WALK_0_BASE = {
    (9, 14): (0x23, HAIR_BASE, "scabbard reveal in the collar gap: the hair reaches down from row 13"),
    (8, 21): (0x22, TROUSER, "scabbard painted over vanilla's trouser grey"),
    (9, 21): (0x27, TROUSER, "the same"),
    (10, 21): (0x22, TROUSER, "the same"),
}

BACK_WALK_0_SSJ = dict(BACK_WALK_0_BASE)
BACK_WALK_0_SSJ[(9, 14)] = (0x23, HAIR_SSJ, "the same, in this form's own gold")

# ===== which call list each frame takes =====
PLAN = [
    ("trunks_tank_base_front.png", FRONT_IDLE),
    ("trunks_tank_base_front_stand1.png", FRONT_IDLE),
    ("trunks_tank_base_front_walk_1.png", FRONT_IDLE),
    ("trunks_tank_base_front_walk_3.png", FRONT_IDLE),
    ("trunks_tank_ssj_front_walk_1.png", FRONT_IDLE),
    ("trunks_tank_ssj_front_walk_3.png", FRONT_IDLE),
    ("trunks_tank_ssj_front.png", FRONT_IDLE),          # on disk, held out of the manifest
    ("trunks_tank_base_front_walk_0.png", FRONT_WALK_0),
    ("trunks_tank_ssj_front_walk_0.png", FRONT_WALK_0),
    ("trunks_tank_base_front_walk_2.png", FRONT_WALK_2),
    ("trunks_tank_ssj_front_walk_2.png", FRONT_WALK_2),
    ("trunks_tank_base_side.png", SIDE_IDLE),
    ("trunks_tank_base_side_stand1.png", SIDE_IDLE),
    ("trunks_tank_base_side_walk_1.png", SIDE_IDLE),
    ("trunks_tank_base_side_walk_3.png", SIDE_IDLE),
    ("trunks_tank_ssj_side.png", SIDE_IDLE),
    ("trunks_tank_ssj_side_stand1.png", SIDE_IDLE),
    ("trunks_tank_ssj_side_walk_1.png", SIDE_IDLE),
    ("trunks_tank_ssj_side_walk_3.png", SIDE_IDLE),
    ("trunks_tank_base_side_walk_0.png", SIDE_WALK_0),
    ("trunks_tank_ssj_side_walk_0.png", SIDE_WALK_0),
    ("trunks_tank_base_side_walk_2.png", SIDE_WALK_2),
    ("trunks_tank_ssj_side_walk_2.png", SIDE_WALK_2),
    ("trunks_tank_base_back_walk_0.png", BACK_WALK_0_BASE),
    ("trunks_tank_ssj_back_walk_0.png", BACK_WALK_0_SSJ),
]
UNTOUCHED = ["trunks_tank_base_back.png", "trunks_tank_base_back_walk_1.png",
             "trunks_tank_base_back_walk_2.png", "trunks_tank_base_back_walk_3.png",
             "trunks_tank_ssj_back.png", "trunks_tank_ssj_back_walk_1.png",
             "trunks_tank_ssj_back_walk_2.png", "trunks_tank_ssj_back_walk_3.png"]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bad, changed = [], 0
    for name, calls in PLAN:
        with Image.open(ART / name) as img:
            data, (w, h), pal = bytearray(img.tobytes()), img.size, img.getpalette()
        for (x, y), (want, new, why) in sorted(calls.items(), key=lambda kv: (kv[0][1], kv[0][0])):
            got = data[y * w + x]
            if got != want:
                bad.append(f"{name} ({x},{y}): holds {got:02X}, the call expects {want:02X}: {why}")
                continue
            data[y * w + x] = new
            changed += 1
        out = Image.frombytes("P", (w, h), bytes(data))
        out.putpalette(pal)
        out.save(OUT / name, transparency=0)
        n = sum(1 for a, b in zip(Image.open(ART / name).tobytes(), bytes(data)) if a != b)
        print(f"{name:40s} {n:3d} px changed")
    for name in UNTOUCHED:
        with Image.open(ART / name) as img:
            img.save(OUT / name, transparency=0)
        print(f"{name:40s}   0 px changed (copied)")

    print(f"\n{changed} pixels changed over {len(PLAN)} frames")
    if bad:
        print("\nSTOP: a call did not find the index it expects. Nothing below is trustworthy.")
        for line in bad:
            print("  " + line)
        return 1
    print("every call found the index it expects")
    return 0


if __name__ == "__main__":
    sys.exit(main())
