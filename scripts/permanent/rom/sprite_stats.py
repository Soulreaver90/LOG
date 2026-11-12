r"""
sprite_stats.py - Measure the pose signature of an animation row, and name the frame that breaks it.

An outfit swap has a numeric fingerprint per frame: how much bare skin, how much new garment, how much of
the old garment was cut away, and how big the silhouette ended up. Within one animation row those numbers
should move smoothly, because it is the same character in the same clothes from one moment to the next.
A frame whose numbers jump is where the error is.

This is a POINTER, never a verdict. It found two real defects in the Trunks tank side walk:
  10 px of skin where its neighbours had 21 to 24, which was an arm cut off and left floating
  0 px cut where its neighbours cut 10, which was a sleeve outline filled in and a thick boneless arm
It also cannot see a thick arm from the totals alone, because a filled sleeve RAISES the skin count and a
lost arm LOWERS it, so both can land near a plausible total. Read `widest run` for that, and then look.

Usage:
  py -3.14 -I sprite_stats.py --vanilla v0.png v1.png --art a0.png a1.png [--labels idle walk0]
  py -3.14 -I sprite_stats.py --vanilla ... --art ... --garment 51,50,4F,4E --body-from 13 --arm-from 17
"""
import sys
from pathlib import Path

from PIL import Image

# ===== palette roles, Trunks defaults; pass --garment for another character =====
GARMENT = {0x51, 0x50, 0x4F, 0x4E}
SKIN = {0x11, 0x12, 0x13, 0x15, 0x17, 0x18}
DARK = {0x01}                     # the new garment: black tank
BODY_FROM = 13                    # rows above this are head, and no garment swap belongs there
ARM_FROM = 17                     # the widest-run check starts BELOW the jaw; a face is skin and wide
ARM_MAX = 4                       # his bare arm is 3 px, 4 at the widest, measured off his approved idle


# ===== measurement =====

def _px(path: Path) -> tuple:
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path.name}: not an indexed PNG")
    return im.tobytes(), im.size


def widest_run(data: bytes, size: tuple, values: set, body_from: int) -> tuple:
    """(width, row) of the longest horizontal run of `values` on body rows.

    A run that merges an arm with the hand it belongs to is expected and is not a fault, so this
    reports the number and leaves the judgement to the eye."""
    w, h = size
    best = (0, -1)
    for y in range(body_from, h):
        run = 0
        for x in range(w):
            run = run + 1 if data[y * w + x] in values else 0
            if run > best[0]:
                best = (run, y)
    return best


def stats(vanilla: Path, art: Path, garment: set, body_from: int) -> dict:
    v, size = _px(vanilla)
    a, size2 = _px(art)
    if size != size2:
        raise SystemExit(f"{art.name}: {size2} does not match {vanilla.name} {size}")
    w, h = size
    masked = [i for i in range(len(v)) if v[i] in garment and i >= body_from * w]
    run, row = widest_run(a, size, SKIN, max(body_from, ARM_FROM))
    return {
        "garment": len(masked),
        "skin": sum(1 for i in masked if a[i] in SKIN),
        "new": sum(1 for i in masked if a[i] in DARK),
        "cut": sum(1 for i in masked if a[i] == 0),
        "left": sum(1 for i in masked if a[i] in garment),
        "opaque": sum(1 for p in a if p),
        "shrank": sum(1 for p in a if p) - sum(1 for p in v if p),
        "run": run,
        "run_row": row,
    }


def outliers(rows: list, key: str) -> set:
    """Frames whose value sits furthest from the row median, beyond half the median.

    Half the median is deliberately loose. A real walk cycle varies, and a tight threshold would cry
    wolf on every frame and be ignored, which is worse than no check."""
    vals = sorted(r[1][key] for r in rows)
    if len(vals) < 3:
        return set()
    mid = vals[len(vals) // 2]
    return {r[0] for r in rows if abs(r[1][key] - mid) > max(2, mid / 2)}


# ===== report =====

def report(labels: list, pairs: list, garment: set, body_from: int) -> int:
    rows = [(lab, stats(v, a, garment, body_from)) for lab, (v, a) in zip(labels, pairs)]
    head = f"{'frame':14} {'garment':>8} {'->skin':>7} {'->new':>6} {'->cut':>6} {'left':>5} " \
           f"{'opaque':>7} {'vs van':>7} {'widest run':>11}"
    print(head)
    print("-" * len(head))
    for lab, s in rows:
        print(f"{lab:14} {s['garment']:>8} {s['skin']:>7} {s['new']:>6} {s['cut']:>6} {s['left']:>5} "
              f"{s['opaque']:>7} {s['shrank']:>+7} {s['run']:>8} (y{s['run_row']})")

    flagged = {}
    for key in ("skin", "cut", "new"):
        for lab in outliers(rows, key):
            flagged.setdefault(lab, []).append(key)
    print()
    if flagged:
        for lab, keys in flagged.items():
            print(f"  LOOK AT {lab}: {', '.join(keys)} is away from the row. Open the frame, do not trust this.")
    else:
        print("  No frame stands out of the row. That is not a pass; it only means the totals agree.")

    wide = [(lab, s) for lab, s in rows if s["run"] > ARM_MAX]
    if wide:
        print(f"  Widest skin run over {ARM_MAX} px in: "
              f"{', '.join(f'{lab} ({s['run']} px at y{s['run_row']})' for lab, s in wide)}")
        print("  A run that merges an arm with its own hand is expected. A thick filled sleeve is not.")

    grew = [lab for lab, s in rows if s["shrank"] >= 0]
    if grew:
        print(f"  Silhouette did NOT shrink in: {', '.join(grew)}. "
              f"Taking a garment off removes bulk, so this is a recolour, not a swap.")
    return 1 if flagged or grew else 0


def main(argv: list) -> int:
    van, art, labels, garment, body_from, bucket = [], [], [], GARMENT, BODY_FROM, None
    it = iter(argv)
    for tok in it:
        if tok in ("--vanilla", "--art", "--labels"):
            bucket = {"--vanilla": van, "--art": art, "--labels": labels}[tok]
        elif tok == "--garment":
            garment = {int(p, 16) for p in next(it).split(",")}
        elif tok == "--body-from":
            body_from = int(next(it))
        elif tok == "--arm-from":
            globals()["ARM_FROM"] = int(next(it))
        elif bucket is None:
            raise SystemExit(__doc__.strip())
        else:
            bucket.append(tok)
    if not van or len(van) != len(art):
        raise SystemExit(__doc__.strip())
    labels = labels or [Path(p).stem[:14] for p in art]
    return report(labels, list(zip(map(Path, van), map(Path, art))), garment, body_from)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
