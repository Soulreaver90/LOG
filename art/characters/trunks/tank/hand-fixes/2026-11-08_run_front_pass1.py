r"""
2026-11-08_run_front_pass1.py - PASS ONE of the tank run, front row only: anim 13 dir 0, 4 frames,
                                both forms. Staged, not shipped.

Reads  the BASE ROM's own set 128 and set 134 records for a13 d0 i0 to i3.
Writes art\trunks_tank\proposed\2026-11-08\run\trunks_tank_<form>_run_front_<i>.png

Run:   py -3.14 -P art\trunks_tank\hand-fixes\2026-11-08_run_front_pass1.py

> This is PASS ONE and it is for the owner's eye, not for a build. The sprite guide says to hand over
> an editable base after the FIRST pass, not the ninth. Every call below is a hand call with a reason,
> and the ones I am unsure of say so.

Method, from docs\sprite-guide.md:
  * The jacket mask is read from the vanilla frame by index, `4E 4F 50 51`.
  * The eye is NEVER touched. In set 128 the iris is `4F` and `51`, which are jacket indices, and in
    set 134 it is `31` and `32`, which are green. No call below names an eye pixel.
  * Each masked pixel becomes one of four things: bare body, new garment, the next layer down, or it
    is cut to transparent. The reason column says which.
  * One body: the SAME dict runs over both vanilla frames, so the two forms cannot drift. The head row
    is per frame, because in anim 13 the face reaches row 18, not row 15.

What I read in each frame, before any pixel. The run leans forward and the head is tipped down, so
the hair fills the top, the face sits low, and the torso is nearly hidden between the jaw and the belt.
Both sleeves frame the head.

  i0  both hands are bare in vanilla: one at x0-x1 rows 16-18, one at x4-x7 rows 21-24. The thin
      diagonal x1 to x6, rows 15 to 21, is an arm. The mass at x7-x14 rows 18-24 is the shoulder above
      and the coat skirt below. The legs come out at row 25, x4-x9.
  i1  hands at x0-x3 rows 18-20 and x10-x13 rows 20-23. The sleeve lies along rows 16-17.
  i2  the hand is at x8-x11 rows 21-24. The mass at x3-x8 rows 20-24 is the coat skirt. The legs come
      out at row 25, x6-x10.
  i3  both forearms are already bare: x2-x5 rows 19-21 and x12-x15 rows 18-20. This is the easiest
      frame and the smallest mask.

Not settled, and marked on the sheet:
  * In i0 I could not tell WHICH arm is which. The swap does not need it, because both readings make
    the band an arm, but the shading direction does.
  * The belt keeps vanilla's own pixels, including the `4D` and `4E` inside the belt band. See the
    report's section 2: those indices are the belt as well as the strap. No strap is drawn.
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

OUT = ROOT / "art" / "trunks_tank" / "proposed" / "2026-11-08" / "run"
REF = ROOT / "art" / "trunks_tank" / "trunks_tank_base_front.png"
JACKET = {0x4E, 0x4F, 0x50, 0x51}

CUT = 0x00
TANK = 0x01
D, M, L = 0x17, 0x13, 0x11          # skin: dark, mid, lit
TR_D, TR_M = 0x0F, 0x0D             # trouser: dark, mid

# The head row per frame: the LAST row the form's own head owns. Measured from where set 128 and set
# 134 stop differing. Below it the two forms are byte identical in vanilla, so one body costs nothing.
HEAD_ROW = {0: 18, 1: 16, 2: 18, 3: 16}

# ===== the hand calls, per frame =====
# (x, y): (new index, why). Every key must be a jacket pixel in BOTH vanilla frames.

I0 = {
    # the thin diagonal band, x1 to x6, rows 15-21: an arm, already 1 to 3 px, so almost no slack
    (1, 15): (CUT, "the collar top in open air beside the head"),
    (1, 16): (TANK, "black separates the hand at x0 from the face at x2"),
    (1, 17): (D, "arm"), (2, 17): (TANK, "black separates the arm from the face at x3"),
    (2, 18): (D, "arm"), (3, 18): (M, "arm"),
    (4, 18): (TANK, "black separates the arm from the face at x5"),
    (3, 19): (D, "arm"), (4, 19): (M, "arm"),
    (5, 19): (TANK, "black separates the arm from the jaw at x6"),
    (4, 20): (D, "arm"), (5, 20): (M, "arm"),
    (6, 20): (TANK, "the tank's left edge, joining vanilla's black at x7"),
    (4, 21): (CUT, "the coat hem in open air beside the hand: no leg below it"),
    # the right shoulder, rows 18-20: 3 px of bare arm, the slack becomes tank
    (12, 18): (D, "shoulder"), (13, 18): (M, "shoulder"),
    (11, 19): (TANK, "the tank's right edge, beside the jaw at x10"),
    (12, 19): (D, "arm"), (13, 19): (M, "arm"), (14, 19): (D, "arm, outer edge"),
    (10, 20): (TANK, "tank"), (11, 20): (TANK, "tank"),
    (12, 20): (D, "arm"), (13, 20): (M, "arm"), (14, 20): (D, "arm, outer edge"),
    # the coat skirt, rows 21-24: trouser where a leg is below (x4 to x9 at row 25), else cut
    (7, 21): (TR_D, "skirt over the hip: trouser, a leg is below"),
    (8, 21): (TR_M, "trouser"), (9, 21): (TR_D, "trouser"),
    (10, 21): (CUT, "the skirt flaring into open air: no leg below"),
    (11, 21): (CUT, "the same"), (12, 21): (CUT, "the same"),
    (8, 22): (TR_D, "trouser"), (9, 22): (TR_M, "trouser"),
    (10, 22): (CUT, "flare"), (11, 22): (CUT, "flare"), (12, 22): (CUT, "flare"),
    (8, 23): (TR_D, "trouser"), (9, 23): (TR_M, "trouser"),
    (10, 23): (CUT, "flare"), (11, 23): (CUT, "flare"),
    (7, 24): (TR_D, "trouser"), (8, 24): (TR_M, "trouser"), (9, 24): (TR_D, "trouser"),
    (10, 24): (CUT, "flare"),
}

I1 = {
    (1, 15): (CUT, "the collar standing in open air beside the head"),
    (0, 16): (CUT, "sleeve slack: slope the shoulder"),
    (1, 16): (D, "arm"), (2, 16): (M, "arm"), (3, 16): (M, "arm"),
    (4, 16): (TANK, "black separates the arm from the face at x5"),
    (0, 17): (D, "arm, toward the hand at x0-x3 of row 18"),
    (1, 17): (M, "arm"), (2, 17): (L, "arm, lit"), (3, 17): (L, "arm, lit"),
    (4, 17): (M, "arm"),
    (5, 17): (TANK, "black separates the arm from the jaw at x6"),
    (4, 18): (TANK, "tank, and it separates the hand at x3 from the belt at x7"),
    (5, 18): (TANK, "tank"), (6, 18): (TANK, "tank, up to vanilla's belt orange at x7"),
    (4, 19): (TR_D, "below the belt: trouser"), (5, 19): (TR_D, "trouser"),
    (4, 20): (TR_D, "trouser, joining vanilla's grey at x5"),
    (12, 16): (CUT, "collar in open air beside the face"), (13, 16): (CUT, "the same"),
    (11, 17): (TANK, "the tank's right edge, beside the jaw at x10"),
    (12, 17): (D, "arm"), (13, 17): (M, "arm"), (14, 17): (D, "arm, outer edge"),
    (10, 18): (TANK, "tank, joining vanilla's black at x8 and x9"), (11, 18): (TANK, "tank"),
    (12, 18): (D, "arm"), (13, 18): (M, "arm"), (14, 18): (D, "arm, outer edge"),
    (9, 19): (TANK, "tank, at the belt's right end"), (10, 19): (TANK, "tank"),
    (11, 19): (TANK, "tank"),
    (12, 19): (D, "arm"), (13, 19): (M, "arm"), (14, 19): (D, "arm, outer edge"),
    (15, 19): (CUT, "sleeve slack at the frame edge, outboard of the arm"),
    (10, 20): (TR_D, "trouser, joining vanilla's grey at x9"),
    (13, 20): (CUT, "outboard of the hand at x11 and x12, so it is the sleeve tail"),
    (14, 20): (CUT, "the same"), (15, 20): (CUT, "the same"),
    (14, 21): (CUT, "outboard of the forearm"), (14, 22): (CUT, "the same"),
}

I2 = {
    (3, 18): (D, "left shoulder"),
    (4, 18): (TANK, "black separates the shoulder from the face at x5"),
    (2, 19): (D, "arm"), (3, 19): (M, "arm"), (4, 19): (L, "arm, lit"),
    (5, 19): (TANK, "the tank's left edge, beside the jaw at x6"),
    (2, 20): (D, "arm"), (3, 20): (M, "arm"), (4, 20): (L, "arm, lit"),
    (5, 20): (TANK, "tank"), (6, 20): (TANK, "tank"),
    (7, 20): (TANK, "tank, up to vanilla's belt orange at x8"),
    (3, 21): (CUT, "the skirt flaring: the legs come out at x6 to x10"),
    (4, 21): (CUT, "flare"), (5, 21): (CUT, "flare"),
    (6, 21): (TR_D, "trouser, a leg is below"), (7, 21): (TR_M, "trouser"),
    (8, 21): (TR_D, "trouser"),
    (3, 22): (CUT, "flare"), (4, 22): (CUT, "flare"), (5, 22): (CUT, "flare"),
    (6, 22): (TR_D, "trouser"), (7, 22): (TR_M, "trouser"),
    (4, 23): (CUT, "flare"), (5, 23): (CUT, "flare"),
    (6, 23): (TR_D, "trouser"), (7, 23): (TR_M, "trouser"),
    (5, 24): (CUT, "flare"),
    (6, 24): (TR_D, "trouser"), (7, 24): (TR_M, "trouser"), (8, 24): (TR_D, "trouser"),
    (12, 18): (CUT, "collar in open air beside the face"), (13, 18): (CUT, "the same"),
    (11, 19): (TANK, "the tank's right edge, beside the jaw at x10"),
    (12, 19): (D, "the shoulder's outer edge"),
    (11, 20): (TANK, "tank"),
    (11, 21): (CUT, "outboard of the hand at x9 and x10, so it is the sleeve tail"),
    (12, 21): (CUT, "the same"),
}

I3 = {
    (1, 16): (CUT, "sleeve slack outboard of the arm line"), (2, 16): (CUT, "the same"),
    (3, 16): (D, "arm, at the shoulder"),
    (4, 16): (TANK, "black separates the arm from the face at x5"),
    (1, 17): (CUT, "sleeve slack"), (2, 17): (CUT, "sleeve slack"),
    (3, 17): (D, "arm"), (4, 17): (M, "arm"),
    (5, 17): (TANK, "black separates the arm from the jaw at x6"),
    (0, 18): (CUT, "sleeve slack"), (1, 18): (CUT, "sleeve slack"), (2, 18): (CUT, "sleeve slack"),
    (3, 18): (D, "arm"), (4, 18): (M, "arm"), (5, 18): (L, "arm, lit"),
    (6, 18): (TANK, "the tank's left edge, up to vanilla's belt orange at x7"),
    (0, 19): (CUT, "sleeve slack"), (1, 19): (CUT, "sleeve slack"),
    (2, 19): (D, "arm, joining vanilla's bare skin at x3 and x4"),
    (5, 19): (TANK, "tank, between the arm and vanilla's black at x6"),
    (1, 20): (CUT, "sleeve slack beside the bare forearm"), (1, 21): (CUT, "the same"),
    (12, 16): (CUT, "collar in open air beside the face"), (13, 16): (CUT, "the same"),
    (11, 17): (TANK, "black separates the jaw at x10 from the arm at x12"),
    (12, 17): (D, "arm, joining vanilla's bare skin at x13 and x14"),
    (11, 18): (TANK, "the tank's right edge, between the black at x10 and the arm at x12"),
    (10, 19): (TANK, "tank, at the belt's right end"),
    (11, 19): (D, "arm, joining vanilla's bare skin at x12"),
    (11, 20): (CUT, "sleeve slack beside the trousers, outboard of nothing"),
}

PLAN = {0: I0, 1: I1, 2: I2, 3: I3}


def raster(tiles: bytes, w: int, h: int) -> bytes:
    rows = [bytearray(w) for _ in range(h)]
    for t in range(len(tiles) // 64):
        x0, y0 = (t % (w // 8)) * 8, (t // (w // 8)) * 8
        for r in range(8):
            rows[y0 + r][x0:x0 + 8] = tiles[t * 64 + r * 8:t * 64 + r * 8 + 8]
    return b"".join(bytes(r) for r in rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rom = log2_build.BASE.read_bytes()
    with Image.open(REF) as ref:
        pal = ref.getpalette()
    recs = {}
    for s in (128, 134):
        off = rom_ptr(rom, SET_TABLE + 4 * (s - 7))
        recs[s] = {(r["anim"], r["dir"], r["index"]): r for r in set_records(rom, off)}

    bad, drawn = [], {}
    for i, calls in PLAN.items():
        for s, form in ((128, "base"), (134, "ssj")):
            rec = recs[s][(13, 0, i)]
            w, h = rec["w"], rec["h"]
            van = raster(unpack_frame(rom, rec["header"])[2], w, h)
            data = bytearray(van)
            for (x, y), (new, why) in sorted(calls.items(), key=lambda kv: (kv[0][1], kv[0][0])):
                got = van[y * w + x]
                if got not in JACKET:
                    bad.append(f"set {s} i{i} ({x},{y}): holds {got:02X}, which is not jacket: {why}")
                    continue
                data[y * w + x] = new
            name = f"trunks_tank_{form}_run_front_{i}.png"
            img = Image.frombytes("P", (w, h), bytes(data))
            img.putpalette(pal)
            img.save(OUT / name, transparency=0)
            drawn[(s, i)] = bytes(data)
            cut = sum(1 for v in van if v) - sum(1 for v in data if v)
            print(f"{name:40s} mask {sum(1 for v in van if v in JACKET):3d}  "
                  f"changed {len(calls):3d}  silhouette {-cut:+3d}")

    print()
    print("one body: rows below the head row, base against Super Saiyan")
    for i in PLAN:
        w = 16
        lo = (HEAD_ROW[i] + 1) * w
        diff = sum(1 for a, b in zip(drawn[(128, i)][lo:], drawn[(134, i)][lo:]) if a != b)
        print(f"  i{i}: head rows 0-{HEAD_ROW[i]}, body from {HEAD_ROW[i] + 1}: {diff} px differ")

    if bad:
        print("\nSTOP: a call names a pixel that is not jacket in vanilla.")
        for line in bad:
            print("  " + line)
        return 1
    print("\nevery call named a jacket pixel in both vanilla frames")
    return 0


if __name__ == "__main__":
    sys.exit(main())
