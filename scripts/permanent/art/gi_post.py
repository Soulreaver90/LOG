r"""
gi_post.py - Post-process the gi art: SSJ2 golden heads, golden idle slots, body rules, SSJ to SSJ2 step, one body.

Usage:   py -3 -I scripts\permanent\art\gi_post.py all      (from the LOG root, after gi_art.py all)
         Commands: all | transplant | finish | body | step | one_body   (all = the five, in that order)
Input:   art\gi_ssj\, gi_ssj2\, gi_base\ (gi_art.py output) and art\golden\golden_gi_ssj2_d0-3.png
         (read only).
Output:  art\gi_ssj2_v2\ (frames, manifest.json, transplant.json) and art\gi_ssj_v2\ (copy of gi_ssj
         plus the 3 step frames). The source folders are not touched. gohan_gi reads both folders by default.
         Step 5 (gi_one_body.py) writes gi_ssj_v4\ and gi_ssj2_v4\: sets 158 and 159 on the base body (one body,
         me, 2026-10-22 and 2026-10-23); gi_aura.py bakes the bolts of gi_ssj2_aura_v4\. LOG_GI_SSJ / LOG_GI_SSJ2 select them.
API:     transplant_heads(art) -> report      finish_golden_slots(art) -> status counts
         body_rules(art, apply) -> {"gate": {dir: pixels}, "applied": bool, "pixels": int}
         ssj2_step_frames(art) -> None        rules(img, front_back, front) -> (img, pixels)      run_all(art) -> None
         one_body(art) -> {out: report}
Method:  1. transplant_heads: the old head of each gi_ssj2 frame is found by matching the old idle head of each
            direction; the golden SSJ2 head goes on at that offset. Pixels that differ from the old head stay on top.
         2. finish_golden_slots: the 3 idle frames become the SSJ2 goldens, the powered-down frames go back to the source.
         3. body_rules: crotch line (R1) and arm line (R2) on front and back frames. A golden gate runs first: if a
            rule would change any golden frame, no frame is changed. Frames on the shared gi_ssj body (manifest
            "body": "gi_ssj", gi_art.py) are skipped: the rules change the SSJ goldens (d0 2 px, d1 3 px), so
            they may not run on the SSJ body, and SSJ and SSJ2 stay one body.
         4. ssj2_step_frames: set 158 anim 9 frames 1-3 take the golden SSJ2 head with the game face, a sway and a
            flash ring. Last, the reviewed hand frames of set 158 (hand_frames.HAND["gi_ssj_v2"]) replace theirs.
         5. one_body: gi_one_body.run_all (base body plus the form head; see its header).
Rules:   The golden files are never written. Every step reads the output of the step before it, so run all in order.
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from art import gi_one_body  # noqa: E402
from art import hand_frames  # noqa: E402
import log_paths  # noqa: E402
from rom.log2_sprites import OBJ_SHAPES  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART

# -- transplant
BODY = {88, 89, 211, 72, 195, 26, 27, 34, 35, 1}       # gi, belt, wristbands, boots, shadow: never part of a head
EYES = {49: 64, 50: 65}                                  # green to game teal
HEAD_ROWS = 17
OCCLUDERS = (20, 21, 36, 37, 38, 39, 44, 46, 2, 9, 120)  # old pixels of these colors never hide the new head

# -- finish
GOLDEN = {"frame_2A15DC.png": 0, "frame_2A1878.png": 1, "frame_2A19AC.png": 2}    # idle frame: golden direction
KEEP = {"frame_2A39F4.png", "frame_2A3AD0.png",           # anim 3 frames 2-3: black hair, powered down
        "frame_2B667C.png", "frame_2B6794.png", "frame_2B68A0.png"}   # anim 21 frames 1-3: hair turning back to black

# -- body rules
GI, LINE, ARM = {88, 89}, 211, 23

# -- step frames
FACE_ROWS, FACE_X = range(14, 17), range(10, 23)          # shifted rows: closed eyes, brows (game face)
FACE = {20, 21, 23, 113, 114, 115, 116, 117}
FLASH = {46: 37, 37: 2, 38: 46, 39: 46, 44: 37}                     # frame 1: fills one step brighter
SWAY_ROWS = 13                                                        # hair rows above the forehead lean
STEP_FRAMES = {"frame_2B1D0C.png": (FLASH, (120,), -2),               # index 1: 1 px ring 120, tips lean left
               "frame_2B1E50.png": ({}, (46, 38), 0),                 # index 2: inner 46, outer 38, upright
               "frame_2B1FB0.png": ({}, (37, 120), 2)}                # index 3: inner 37, outer 120, lean right
RING_2_TO_3 = {46: 37, 38: 120}                                       # index 3 belt rows copy index 2 in its ring colors
BELT_ROWS = (23, 24, 25)


# ===== step 1: transplant_heads =====

def px_of(img):
    w, h = img.size
    b = img.tobytes()
    return {(x, y): b[y * w + x] for y in range(h) for x in range(w) if b[y * w + x]}


def head_of(px):
    return {p: v for p, v in px.items() if p[1] < HEAD_ROWS and v not in BODY}


def flip(d, w=32):
    return {(w - 1 - x, y): v for (x, y), v in d.items()}


def best(px, cands, mask, old):
    """Align by head shape: IoU of the frame's head mask against each old idle head mask, plus pixel agreement."""
    top = (-1, 0, 0, 0, 0)
    for d in cands:
        T = old[d]
        tm = set(T)
        for oy in range(-14, 15):
            for ox in range(-14, 15):
                moved = {(x + ox, y + oy) for x, y in tm}
                inter = len(moved & mask)
                iou = inter / len(moved | mask)
                if iou <= top[0] - .15:
                    continue
                agree = sum(px.get((x + ox, y + oy)) == v for (x, y), v in T.items()) / len(T)
                s = iou + .25 * agree
                if s > top[0]:
                    top = (s, d, ox, oy, iou)
    return top


def transplant_heads(art: Path = ART) -> list:
    """Golden SSJ2 head on every gi_ssj2 frame; writes gi_ssj2_v2 (frames, manifest.json, transplant.json)."""
    src_dir, out, gold = art / "gi_ssj2", art / "gi_ssj2_v2", art / "golden"
    out.mkdir(exist_ok=True)
    man = json.loads((src_dir / "manifest.json").read_text())
    idle = {}
    for e in man:
        for k in e["keys"]:
            if k["anim"] == 0 and k["index"] == 0 and not (k["attr1"] & 0x1000):
                idle[k["dir"]] = px_of(Image.open(src_dir / e["png"]))
    old = {0: head_of(idle[0]), 1: head_of(idle[1]), 2: head_of(idle[2])}
    old[3] = flip(old[2])
    new = {d: head_of(px_of(Image.open(gold / f"golden_gi_ssj2_d{d}.png"))) for d in (0, 1, 2, 3)}

    report, out_man = [], []
    for e in man:
        img = Image.open(src_dir / e["png"])
        pal = img.getpalette()
        px = px_of(img)
        stored = {k["dir"] if not (k["attr1"] & 0x1000) else {3: 2, 2: 3}.get(k["dir"], k["dir"]) for k in e["keys"]}
        mask = {tuple(p) for p in e["head"]}
        score, d, ox, oy, iou = best(px, sorted(stored), mask, old)
        status = "ok" if iou >= .7 else "flag"
        newpx = dict(px)
        if status == "ok":
            T, N = old[d], new[d]
            top = min(y for _, y in N) + oy
            if top < 0:                                       # keep the head inside the 32-row slot
                status += f"+shift{-top}"
                oy -= top
            for (x, y), v in T.items():                       # clear old head pixels still unchanged
                q = (x + ox, y + oy)
                if px.get(q) == v:
                    newpx.pop(q, None)
            for (x, y), v in N.items():                       # new head, under anything that was not old head
                q = (x + ox, y + oy)
                t = (x, y)
                occluder = q in px and (T.get(t) != px[q]) and px[q] not in OCCLUDERS
                if not occluder:
                    newpx[q] = v
        for q, v in list(newpx.items()):
            if v in EYES:
                newpx[q] = EYES[v]
        xs = [x for x, _ in newpx]
        ys = [y for _, y in newpx]
        x0, y0 = min(0, min(xs)), min(0, min(ys))
        x1, y1 = max(e["w"] - 1, max(xs)), max(e["h"] - 1, max(ys))
        W, H = x1 - x0 + 1, y1 - y0 + 1
        if (W, H) != (e["w"], e["h"]):
            W2, H2 = (32 if W > 16 else 16) if W <= 32 else W, 32 if H <= 32 else H
            if H > 32:                                        # body plus head taller than the slot: drop to 32 from the top
                y0 = y1 - 31
                H = 32
            status += "+grow" if W2 <= 32 and H2 <= 32 else "+overflow"
            x0 -= (W2 - W) // 2 if W < W2 and x0 < 0 and x1 < e["w"] else 0
            W, H = W2, H2
        canvas = Image.new("P", (W, H), 0)
        canvas.putpalette(pal)
        cp = canvas.load()
        for (x, y), v in newpx.items():
            if 0 <= x - x0 < W and 0 <= y - y0 < H:
                cp[x - x0, y - y0] = v
        rec = {k: v for k, v in e.items() if k not in ("head", "checks", "arms")}
        rec["w"], rec["h"] = W, H
        rec["keys"] = []
        for k in e["keys"]:
            k = dict(k)
            flipped = bool(k["attr1"] & 0x1000)
            k["dx"] += (x0 if not flipped else (e["w"] - 1 - x1)) if (W, H) == (e["w"], e["h"]) else (x0 if not flipped else -(W - e["w"]) - x0)
            k["dy"] += y0
            k["w"], k["h"] = W, H
            if (W, H) != (e["w"], e["h"]):                     # OBJ shape/size bits must match the new size
                sh, sz = OBJ_SHAPES[W, H]
                k["attr0"] = (k["attr0"] & 0x3FFF) | (sh << 14)
                k["attr1"] = (k["attr1"] & 0x3FFF) | (sz << 14)
            rec["keys"].append(k)
        canvas.save(out / e["png"], transparency=0)
        out_man.append(rec)
        report.append({"png": e["png"], "score": round(score, 3), "iou": round(iou, 3), "dir": d, "off": [ox, oy], "status": status,
                       "keys": [f'{k["anim"]}.{k["dir"]}.{k["index"]}' for k in e["keys"]], "size": [W, H]})
    (out / "manifest.json").write_text(json.dumps(out_man, indent=1))
    (out / "transplant.json").write_text(json.dumps(report, indent=1))
    print("transplant:", dict(Counter(r["status"] for r in report)))
    return report


# ===== step 2: finish_golden_slots =====

def finish_golden_slots(art: Path = ART) -> dict:
    """Golden frames replace the idle frames, powered-down frames go back to the source; transplant.json follows."""
    src_dir, v2, gold = art / "gi_ssj2", art / "gi_ssj2_v2", art / "golden"
    man = {e["png"]: e for e in json.loads((v2 / "manifest.json").read_text())}
    src = {e["png"]: e for e in json.loads((src_dir / "manifest.json").read_text())}
    rep = json.loads((v2 / "transplant.json").read_text())
    for r in rep:
        p = r["png"]
        if p in GOLDEN:
            Image.open(gold / f"golden_gi_ssj2_d{GOLDEN[p]}.png").save(v2 / p, transparency=0)
            man[p]["w"] = man[p]["h"] = 32
            man[p]["keys"] = [dict(k) for k in src[p]["keys"]]
            r["status"] = "golden"
        elif p in KEEP:
            shutil.copyfile(src_dir / p, v2 / p)
            e = {k: v for k, v in src[p].items() if k not in ("head", "checks", "arms")}
            man[p] = e
            r["status"] = "kept"
    (v2 / "manifest.json").write_text(json.dumps(list(man.values()), indent=1))
    (v2 / "transplant.json").write_text(json.dumps(rep, indent=1))
    counts = {s: sum(r["status"] == s for r in rep) for s in sorted({r["status"] for r in rep})}
    print("finish:", counts)
    return counts


# ===== step 3: body_rules =====
# Why: my golden edits show two body lines. They apply to front and back views only (side legs and arms
# overlap the torso). R1 crotch: on the first row of the gap between the legs, the gi pixels on both sides of the
# gap become 211. R2 arm line: a gi pixel beside the arm outline (23) on its row becomes 211, from 2 rows below the
# gi top (the collar rows touch the neck outline, not an arm). Exemption (final, 2026-10-18): in a front view the
# first R2 row (gi top + 2) keeps a gi pixel whose image-left neighbor is the arm outline: my rounder chest
# (golden SSJ2 d0 pixel (12, 19) stays 89). The golden gate proves it: all four SSJ2 goldens change by 0 pixels.
# Shared bodies (final, 2026-10-18): on golden_gi_ssj the rules change d0 by 2 px and d1 by 3 px, so they never run
# on a frame that carries the gi_ssj body; they run on the SSJ2 frames that keep their own body.

def rules(img, front_back=True, front=False):
    w, h = img.size
    b = bytearray(img.tobytes())
    src = bytes(b)
    n = 0
    if not front_back:
        return img, 0
    gi_top = min((i // w for i, v in enumerate(src) if v in GI | {LINE}), default=h)

    def at(x, y):
        return src[y * w + x] if 0 <= x < w and 0 <= y < h else 0
    for y in range(h):
        for x in range(w):
            if src[y * w + x] in GI:
                r1 = any(at(x + dx, y) == 0 and at(x + dx, y - 1) != 0 and at(x + 2 * dx, y) in GI | {LINE}
                         for dx in (1, -1))
                r1 = r1 or any(at(x + dx, y) == 0 and at(x + dx, y - 1) != 0 and at(x + dx + dx, y) == 0
                               and at(x + 3 * dx, y) in GI | {LINE} for dx in (1, -1))
                armpit = front and y == gi_top + 2
                r2 = y >= gi_top + 2 and (at(x + 1, y) == ARM or (at(x - 1, y) == ARM and not armpit))
                if r1 or r2:
                    b[y * w + x] = LINE
                    n += 1
    out = Image.frombytes("P", img.size, bytes(b))
    out.putpalette(img.getpalette())
    return out, n


def body_rules(art: Path = ART, apply: bool = True) -> dict:
    """Run the golden gate, then (if no golden changes and apply) the rules on every gi_ssj2_v2 frame."""
    v2, gold = art / "gi_ssj2_v2", art / "golden"
    gate = {d: rules(Image.open(gold / f"golden_gi_ssj2_d{d}.png"), d in (0, 1), d == 0)[1] for d in (0, 1, 2, 3)}
    print("golden changes per rule set (must be 0):", gate)
    result = {"gate": gate, "applied": False, "pixels": 0}
    if apply and not any(gate.values()):                      # a rule that contradicts a golden is not applied
        view = {r["png"]: r["dir"] for r in json.loads((v2 / "transplant.json").read_text())}
        shared = {e["png"] for e in json.loads((v2 / "manifest.json").read_text()) if e.get("body", "own") != "own"}
        for p in sorted(v2.glob("frame_*.png")):
            if p.name in KEEP or p.name in shared:            # powered-down frames stay equal to the source; a
                continue                                      # shared body stays equal to gi_ssj (SSJ gate fails)
            out, n = rules(Image.open(p), view.get(p.name) in (0, 1), view.get(p.name) == 0)
            result["pixels"] += n
            if n:
                out.save(p, transparency=0)
        result["applied"] = True
        print("frames fixed, pixels changed:", result["pixels"])
    else:
        print("body rules not applied")
    return result


# ===== step 4: ssj2_step_frames =====
# Why: set 158 anim 9 is the Super Saiyan to Super Saiyan 2 step. Frame content moves down 1 row (dy -1, so the body
# stays put) to fit the taller head; the golden head (rows 0-16, front d0) goes on 1 px right; the game's face (closed
# eyes, mouth shaded for the head tilted back) stays. Frame 1 hair gets the flash colors. The flash ring is redrawn in
# each frame's own ring colors. Frame 0 (start, SSJ hair) stays.

def ssj2_step_frames(art: Path = ART) -> None:
    """gi_ssj_v2 = copy of gi_ssj plus anim 9 frames 1-3 with the golden SSJ2 head."""
    src_dir, out, gold_dir = art / "gi_ssj", art / "gi_ssj_v2", art / "golden"
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(src_dir, out)
    gb = Image.open(gold_dir / "golden_gi_ssj2_d0.png").tobytes()
    man = json.loads((out / "manifest.json").read_text())
    for e in man:
        if e["png"] not in STEP_FRAMES:
            continue
        recolor, ring, lean = STEP_FRAMES[e["png"]]
        img = Image.open(src_dir / e["png"])
        src = img.tobytes()
        px = bytearray(32 * 32)
        for y in range(31):                                          # down 1 row; row 31 of the source is empty
            px[(y + 1) * 32:(y + 2) * 32] = src[y * 32:(y + 1) * 32]
        assert not any(src[31 * 32:]), e["png"]
        px[:HEAD_ROWS * 32] = bytes(HEAD_ROWS * 32)
        for y in range(HEAD_ROWS):
            for x in range(31):
                k = gb[y * 32 + x]
                if k:
                    px[y * 32 + x + 1] = recolor.get(k, k)
        for y in range(SWAY_ROWS):                                   # shear: the top row moves the most
            dx = round(lean * (SWAY_ROWS - y) / SWAY_ROWS)
            row = px[y * 32:(y + 1) * 32]
            px[y * 32:(y + 1) * 32] = bytes(row[x - dx] if 0 <= x - dx < 32 else 0 for x in range(32))
        for y in FACE_ROWS:                                          # the game's strained face, head tilted back
            for x in FACE_X:
                k = src[(y - 1) * 32 + x]
                if k in FACE:
                    px[y * 32 + x] = k
        for color in ring:                                           # one outside ring layer per color
            outside = set()
            todo = [(x, y) for x in range(32) for y in (0, 31)] + [(x, y) for y in range(32) for x in (0, 31)]
            while todo:                                              # flood from the border: gaps between spikes stay open
                x, y = todo.pop()
                if 0 <= x < 32 and 0 <= y < 32 and (x, y) not in outside and px[y * 32 + x] == 0:
                    outside.add((x, y))
                    todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            layer = [(x, y) for x, y in outside if y <= HEAD_ROWS and any(
                0 <= x + a < 32 and 0 <= y + b < 32 and px[(y + b) * 32 + x + a] and (x + a, y + b) not in outside
                for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
            for x, y in layer:
                px[y * 32 + x] = color
        res = Image.frombytes("P", (32, 32), bytes(px))
        res.putpalette(img.getpalette())
        res.info["transparency"] = 0
        res.save(out / e["png"], transparency=0)
        for k in e["keys"]:
            k["dy"] -= 1
        e.setdefault("notes", []).append("SSJ2 golden head (transform158.py), dy -1")
    # 10:24 PM, index 3 matches indices 1-2: belt back up (rows 23-25 from index 2 in index 3's ring
    # colors) and skin, not brown, between the eyes.
    two = Image.open(out / "frame_2B1E50.png").tobytes()
    three_img = Image.open(out / "frame_2B1FB0.png")
    three = bytearray(three_img.tobytes())
    for y in BELT_ROWS:
        three[y * 32:(y + 1) * 32] = bytes(RING_2_TO_3.get(k, k) for k in two[y * 32:(y + 1) * 32])
    three[14 * 32 + 16] = 115
    fixed = Image.frombytes("P", (32, 32), bytes(three))
    fixed.putpalette(three_img.getpalette())
    fixed.save(out / "frame_2B1FB0.png", transparency=0)
    for note in hand_frames.place(out, man):                         # reviewed hand frames of set 158 win last
        print("hand frame", note)
    (out / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", newline="\n")
    print("step frames written", out)


# ===== CLI =====

def one_body(art: Path = ART) -> dict:
    """Step 5: sets 158 and 159 from the base body plus their heads (gi_one_body.py): gi_ssj_v4, gi_ssj2_v4."""
    return gi_one_body.run_all(art)


def run_all(art: Path = ART) -> None:
    transplant_heads(art)
    finish_golden_slots(art)
    body_rules(art)
    ssj2_step_frames(art)
    one_body(art)


COMMANDS = {"all": run_all, "transplant": transplant_heads, "finish": finish_golden_slots,
            "body": body_rules, "step": ssj2_step_frames, "one_body": one_body}


def main(argv: list) -> int:
    if len(argv) != 1 or argv[0] not in COMMANDS:
        print(__doc__.split("Input:")[0])
        return 2
    COMMANDS[argv[0]]()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
