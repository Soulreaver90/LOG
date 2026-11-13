r"""
2026-11-08_armour_head_fixes.py - Findings A and E from the armour review, plus the last jacket pixel
                                  in the side frames. Staged, not shipped.

Reads  art\trunks_tank\proposed\2026-11-08\*.png, the output of
       2026-11-08_drop_strap_and_reveals.py. Run that one FIRST.
Writes the same files, in place, inside the proposed folder. The live frames are never touched.

Run:   py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_armour_head_fixes.py

Why these three together: all of them put a pixel back that a garment or the sword had hidden, and all
of them take their answer from set 130, the Super Saiyan in Saiyan armour. The owner's ruling: "the
trunks sprite with the armor exposes the super saiyan hair from the back".

> Set 130 is a valid stand-in for set 134 in anim 0 ONLY. The armour review measured 100% agreement in
> the side idle, 96.7% in the front idle and 87.9% in the back idle, over head rows 0-14. This task
> measured anim 13 and found 27% to 95%, so nothing here may be copied into another anim without
> measuring that anim first.

Finding A, the back idle. The sword and the scabbard stand in the Super Saiyan head's right quarter.
21 gear pixels sit in rows 10 to 15. Each one is filled by what set 130 draws underneath it:

| Set 130 draws | Count | What this script does |
|---|---|---|
| hair | 6 | lift set 130's own gold |
| skin, the nape | 5 | lift set 130's own skin |
| nothing at all | 9 | cut: the hilt stands outside the armour's whole silhouette |
| bodysuit or plate | 1, at (10,15) | LEFT ALONE. A suit pixel is not a lift, and the review says so |

Row 16 is LEFT ALONE as well. It is a body row, so changing it would force the base back frames too,
and the base form has no armour reference: set 129 wears a different hairstyle.
The 4 back WALK frames are LEFT ALONE until anim 1 dir 1 is measured the way anim 13 was.

Finding E, the front. Set 130 hangs gold hair at (4,15) and (12,15), where set 134's collar covers it.
Our frames put the sword guard at (4,15) and nothing at (12,15).
**This overwrites one pixel of the owner's own crossguard, in the Super Saiyan frames only.** His
guard keeps (2,15) and (3,15), and the base frames keep all three.

The side frames' last jacket pixel. (5,20) holds `4E`, a jacket index, in all 8 side frames with the
idle geometry. No reading keeps a jacket pixel there, so it goes. It becomes set 134's own `4D`,
which is what vanilla draws there in the Super Saiyan form.
**That is the belt's cool tone and 4D is also the strap index.** The palette holds no other cool tone
near the belt that is not a garment or the strap, which is itself evidence that this pixel is belt.
The report's section 11 asks the owner to settle it.
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "permanent"))

import log2_build                                                        # noqa: E402
from rom.log2_sprites import set_records                                 # noqa: E402
from rom.webfoot_decompress import SET_TABLE, rom_ptr, unpack_frame      # noqa: E402

STAGED = ROOT / "art" / "trunks_tank" / "proposed" / "2026-11-08"
CUT = 0x00
GOLD = 0x14

# Finding A: (x, y) -> (expected now, class, why). "lift" takes set 130's own pixel at that spot.
BACK_IDLE = {
    (13, 11): (0x0D, "lift", "set 130 draws hair here"),
    (14, 11): (0x0B, "cut", "the hilt stands outside the armour's silhouette"),
    (15, 11): (0x0D, "cut", "the same"),
    (13, 12): (0x0B, "lift", "set 130 draws the nape here"),
    (14, 12): (0x09, "cut", "outside the silhouette"),
    (15, 12): (0x0B, "cut", "outside the silhouette"),
    (9, 13): (0x0D, "lift", "set 130 draws hair"),
    (10, 13): (0x0D, "lift", "set 130 draws hair"),
    (12, 13): (0x01, "lift", "set 130 draws the nape"),
    (13, 13): (0x01, "lift", "set 130 draws the nape"),
    (14, 13): (0x0B, "cut", "outside the silhouette"),
    (15, 13): (0x0D, "cut", "outside the silhouette"),
    (9, 14): (0x0D, "lift", "set 130 draws hair"),
    (10, 14): (0x0B, "lift", "set 130 draws hair"),
    (11, 14): (0x0D, "lift", "set 130 draws the nape"),
    (12, 14): (0x01, "lift", "set 130 draws the nape"),
    (13, 14): (0x01, "cut", "outside the silhouette"),
    (9, 15): (0x23, "lift", "set 130 draws hair"),
    (11, 15): (0x09, "cut", "outside the silhouette"),
    (12, 15): (0x0D, "cut", "outside the silhouette"),
}
A_LEFT = {(10, 15): "set 130 draws bodysuit here, which is not a lift. The review leaves it open"}

# Finding E: (x, y) -> (expected now, new, why)
FRONT_SSJ = {
    (4, 15): (0x0D, GOLD, "set 130 hangs gold hair here; this overwrites one owner guard pixel"),
    (12, 15): (0x00, GOLD, "set 130 hangs gold hair here; set 134's collar covered it"),
}
E_FRAMES = ["trunks_tank_ssj_front_walk_1.png", "trunks_tank_ssj_front_walk_3.png",
            "trunks_tank_ssj_front.png"]

# The last jacket pixel in the side frames
SIDE_4E = {(5, 20): (0x4E, 0x4D, "a jacket index no reading keeps; set 134 draws 4D, the belt's cool tone")}
SIDE_FRAMES = ["trunks_tank_base_side.png", "trunks_tank_base_side_stand1.png",
               "trunks_tank_base_side_walk_1.png", "trunks_tank_base_side_walk_3.png",
               "trunks_tank_ssj_side.png", "trunks_tank_ssj_side_stand1.png",
               "trunks_tank_ssj_side_walk_1.png", "trunks_tank_ssj_side_walk_3.png"]


def raster(tiles: bytes, w: int, h: int) -> bytes:
    rows = [bytearray(w) for _ in range(h)]
    for t in range(len(tiles) // 64):
        x0, y0 = (t % (w // 8)) * 8, (t // (w // 8)) * 8
        for r in range(8):
            rows[y0 + r][x0:x0 + 8] = tiles[t * 64 + r * 8:t * 64 + r * 8 + 8]
    return b"".join(bytes(r) for r in rows)


def edit(name: str, calls: list) -> int:
    """calls is [(x, y, expected, new, why)]. Returns the number of pixels changed."""
    path = STAGED / name
    with Image.open(path) as img:
        data, (w, h), pal = bytearray(img.tobytes()), img.size, img.getpalette()
    n = 0
    for x, y, want, new, why in calls:
        got = data[y * w + x]
        if got != want:
            print(f"  STOP {name} ({x},{y}): holds {got:02X}, expected {want:02X}: {why}")
            continue
        data[y * w + x] = new
        n += 1
    out = Image.frombytes("P", (w, h), bytes(data))
    out.putpalette(pal)
    out.save(path, transparency=0)
    return n


def main() -> int:
    rom = log2_build.BASE.read_bytes()
    off = rom_ptr(rom, SET_TABLE + 4 * (130 - 7))
    rec = {(r["anim"], r["dir"], r["index"]): r for r in set_records(rom, off)}[(0, 1, 0)]
    armour = raster(unpack_frame(rom, rec["header"])[2], rec["w"], rec["h"])

    calls = []
    for (x, y), (want, kind, why) in sorted(BACK_IDLE.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        new = armour[y * rec["w"] + x] if kind == "lift" else CUT
        calls.append((x, y, want, new, why))
    print("Finding A, trunks_tank_ssj_back.png")
    print(f"  {edit('trunks_tank_ssj_back.png', calls)} px changed, "
          f"{sum(1 for c in BACK_IDLE.values() if c[1] == 'lift')} lifted from set 130, "
          f"{sum(1 for c in BACK_IDLE.values() if c[1] == 'cut')} cut")
    for xy, why in A_LEFT.items():
        print(f"  left alone {xy}: {why}")
    print("  left alone row 16 and the 4 back walk frames: see this script's header")

    print("Finding E")
    for name in E_FRAMES:
        calls = [(x, y, want, new, why) for (x, y), (want, new, why) in FRONT_SSJ.items()]
        print(f"  {name:40s} {edit(name, calls)} px changed")

    print("The side frames' last jacket pixel")
    for name in SIDE_FRAMES:
        calls = [(x, y, want, new, why) for (x, y), (want, new, why) in SIDE_4E.items()]
        print(f"  {name:40s} {edit(name, calls)} px changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
