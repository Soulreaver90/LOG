# Head transplant: put the approved SSJ2 golden heads (front d0, back d1, side d2, mirrored side d3) on every
# gi_ssj2 frame. Each frame's old head is found by matching the old idle head of each direction; the new head
# goes on at that offset. Pixels that differ from the old head (arms in front, open mouth) stay on top.
# Output: scratch\art\gi_ssj2_v2\ (frames, manifest.json, transplant.json). The source set is not touched.
import sys; print(r'promoted to scripts\permanent\gi_post.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json, sys
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ART.parents[1] / "scripts" / "permanent"))
from log2_sprites import OBJ_SHAPES
SRC, OUT, GOLD = ART / "gi_ssj2", ART / "gi_ssj2_v2", ART / "golden"
BODY = {88, 89, 211, 72, 195, 26, 27, 34, 35, 1}       # gi, belt, wristbands, boots, shadow: never part of a head
EYES = {49: 64, 50: 65}                                  # green to game teal
HEAD_ROWS = 17


def px_of(img):
    w, h = img.size; b = img.tobytes()
    return {(x, y): b[y * w + x] for y in range(h) for x in range(w) if b[y * w + x]}


def head_of(px):
    return {p: v for p, v in px.items() if p[1] < HEAD_ROWS and v not in BODY}


def flip(d, w=32):
    return {(w - 1 - x, y): v for (x, y), v in d.items()}


man = json.loads((SRC / "manifest.json").read_text())
idle = {}
for e in man:
    for k in e["keys"]:
        if k["anim"] == 0 and k["index"] == 0 and not (k["attr1"] & 0x1000):
            idle[k["dir"]] = px_of(Image.open(SRC / e["png"]))
OLD = {0: head_of(idle[0]), 1: head_of(idle[1]), 2: head_of(idle[2])}
OLD[3] = flip(OLD[2])
NEW = {d: head_of(px_of(Image.open(GOLD / f"golden_gi_ssj2_d{d}.png"))) for d in (0, 1, 2, 3)}
FULLGOLD = {d: px_of(Image.open(GOLD / f"golden_gi_ssj2_d{d}.png")) for d in (0, 1, 2, 3)}


def best(px, cands, mask):
    """Align by head shape: IoU of the frame's head mask against each old idle head mask, plus pixel agreement."""
    top = (-1, 0, 0, 0, 0)
    for d in cands:
        T = OLD[d]; tm = set(T)
        for oy in range(-14, 15):
            for ox in range(-14, 15):
                moved = {(x + ox, y + oy) for x, y in tm}
                inter = len(moved & mask); iou = inter / len(moved | mask)
                if iou <= top[0] - .15:
                    continue
                agree = sum(px.get((x + ox, y + oy)) == v for (x, y), v in T.items()) / len(T)
                s = iou + .25 * agree
                if s > top[0]:
                    top = (s, d, ox, oy, iou)
    return top


report, out_man = [], []
for e in man:
    img = Image.open(SRC / e["png"]); pal = img.getpalette(); px = px_of(img)
    stored = {k["dir"] if not (k["attr1"] & 0x1000) else {3: 2, 2: 3}.get(k["dir"], k["dir"]) for k in e["keys"]}
    mask = {tuple(p) for p in e["head"]}
    score, d, ox, oy, iou = best(px, sorted(stored), mask)
    status = "ok" if iou >= .7 else "flag"
    newpx = dict(px)
    if status == "ok":
        T, N = OLD[d], NEW[d]
        top = min(y for _, y in N) + oy
        if top < 0:                                       # keep the head inside the 32-row slot
            status += f"+shift{-top}"; oy -= top
        for (x, y), v in T.items():                       # clear old head pixels still unchanged
            q = (x + ox, y + oy)
            if px.get(q) == v:
                newpx.pop(q, None)
        for (x, y), v in N.items():                       # new head, under anything that was not old head
            q = (x + ox, y + oy)
            t = (x, y)
            occluder = q in px and (T.get(t) != px[q]) and px[q] not in (20, 21, 36, 37, 38, 39, 44, 46, 2, 9, 120)
            if not occluder:
                newpx[q] = v
    for q, v in list(newpx.items()):
        if v in EYES:
            newpx[q] = EYES[v]
    xs = [x for x, _ in newpx]; ys = [y for _, y in newpx]
    x0, y0 = min(0, min(xs)), min(0, min(ys)); x1, y1 = max(e["w"] - 1, max(xs)), max(e["h"] - 1, max(ys))
    W, H = x1 - x0 + 1, y1 - y0 + 1
    if (W, H) != (e["w"], e["h"]):
        W2, H2 = (32 if W > 16 else 16) if W <= 32 else W, 32 if H <= 32 else H
        if H > 32:                                        # body plus head taller than the slot: drop to 32 from the top
            y0 = y1 - 31; H = 32
        status += "+grow" if W2 <= 32 and H2 <= 32 else "+overflow"
        x0 -= (W2 - W) // 2 if W < W2 and x0 < 0 and x1 < e["w"] else 0
        W, H = W2, H2
    canvas = Image.new("P", (W, H), 0); canvas.putpalette(pal)
    cp = canvas.load()
    for (x, y), v in newpx.items():
        if 0 <= x - x0 < W and 0 <= y - y0 < H:
            cp[x - x0, y - y0] = v
    rec = {k: v for k, v in e.items() if k not in ("head", "checks", "arms")}
    rec["w"], rec["h"] = W, H
    rec["keys"] = []
    for k in e["keys"]:
        k = dict(k); flipped = bool(k["attr1"] & 0x1000)
        k["dx"] += (x0 if not flipped else (e["w"] - 1 - x1)) if (W, H) == (e["w"], e["h"]) else (x0 if not flipped else -(W - e["w"]) - x0)
        k["dy"] += y0; k["w"], k["h"] = W, H
        if (W, H) != (e["w"], e["h"]):                     # OBJ shape/size bits must match the new size
            sh, sz = OBJ_SHAPES[W, H]
            k["attr0"] = (k["attr0"] & 0x3FFF) | (sh << 14); k["attr1"] = (k["attr1"] & 0x3FFF) | (sz << 14)
        rec["keys"].append(k)
    canvas.save(OUT / e["png"], transparency=0)
    out_man.append(rec)
    report.append({"png": e["png"], "score": round(score, 3), "iou": round(iou, 3), "dir": d, "off": [ox, oy], "status": status,
                   "keys": [f'{k["anim"]}.{k["dir"]}.{k["index"]}' for k in e["keys"]], "size": [W, H]})
(OUT / "manifest.json").write_text(json.dumps(out_man, indent=1))
(OUT / "transplant.json").write_text(json.dumps(report, indent=1))
from collections import Counter
print(Counter(r["status"] for r in report))
for r in sorted(report, key=lambda r: r["iou"])[:40]:
    print(r)
