r"""
gi_one_body.py - One body: derive the gi Super Saiyan (set 158) and Super Saiyan 2 (set 159) frames from the base gi
body (set 157) plus the form's head (me, 2026-10-22; collar, step and revert fix 2026-10-23).

Usage:   py -3 -I scripts\permanent\art\gi_one_body.py all      (from the LOG root; gi_post.py all runs it as its last step)
         Commands: all | table (prints the per-key class: derived, exception, vanilla pose, box, no base)
Input:   art\gi_base\ (set 157, the body I edit, hand frames included), gi_ssj_v2\ (158 heads, the
         anim 9 step frames with the golden SSJ2 head), gi_ssj2_v2\ (159 heads, no bolts), art\vanilla-sets\set56,
         set58, set59 (vanilla head masks and body shifts). All read only.
Output:  art\gi_ssj_v4\ (set 158) and gi_ssj2_v4\ (set 159 body; gi_aura.py bakes its bolts into
         gi_ssj2_aura_v4\): the source folder's manifest (same PNG names, sizes, keys and geometry) with derived
         pixels, an "one_body" field per entry, and one_body.json (per key: class, base key, shift, pixel counts).
API:     derive_folder(art, out) -> report      classify(key, out, base, vanilla) -> (class, shift, residual)
         base_key(out, key) -> key               form_head(form_px, vanilla_px) -> set   torso(base_px, base_head) -> set
         compose(base_px, base_head, form_px, head, shift) -> (px, counts, head)
         fit_box(px, rec) -> (dx, dy, clipped)  context(art, out) -> tables    derive_key(ctx, key) -> (row, px, head)
         run_all(art) -> {out: report}
Classes: derived | exception | vanilla pose | box (KEPT_BOX, or a derived frame that does not fit its record size) |
         no base (anim 21 keys without a POSE_MATCH) | shared (another key of the PNG stays as today).
Method:  Per key (anim, dir, index) with a base key (the same key, or POSE_MATCH for the revert), in object space
         (record dx, dy and h-flip applied):
         1. Shift: the vanilla form body (set 59; set 58, else 59, for SSJ2) is aligned onto the vanilla base body
            (set 56) within 2 px, heads left out. The form head moves by that shift, so it sits on the base neck
            as it sits on the form's own neck in vanilla. HEAD_ANCHOR adds a fixed move for the rows where the
            form frame's head sits off its vanilla place (the golden SSJ2 head transplant, gi_post step 1).
         2. Class: the shape residual after the shift (a body pixel in one frame only) is POSE_LIMIT or more: the
            vanilla poses differ, and the frame stays as today. EXCEPTIONS and KEPT_BOX stay as today too.
         3. Head: the vanilla head mask (gi_art.head_mask) of each frame, the form's grown through its hair colors
            (the golden SSJ2 head is larger than the set 58 head), plus the form's SSJ2 sparks.
         4. Compose (head rule): the form wins only inside its head, and only with its hair and face.
            - on top: form head pixels in ON_TOP (hair, shine, sparks, the step flash ring, the irises) win over
              everything but the base sash, so the hair and the eyes stay whole;
            - base gi (torso): BODY-color parts (gi, sash, wristband, boots, outlines) that reach below the base
              head stay, collar included; only ON_TOP pixels cover them, never the sash (flight: my
              diagonal sash sits right under the collar);
            - face: the other form head pixels, except the form's own body (BODY colors; a wristband blue beside
              an iris is an eye, as in 18.x), win over every other base pixel, as before;
            - base body: every other base pixel outside the base head stays where the form head is not;
            - base head pixels the form head does not cover are cleared; a form pixel there shows (leak). Where it
              is the form's body, the base neck skin stays instead; where base hair covered the body (the collar,
              an arm by the head), the form body fills the gap (gi_under_hair). A cleared base pixel that the new frame encloses on 4 sides stays.
         5. Box: each record keeps its size and moves up to 2 px (dx, dy) to hold the frame, so the body stays where
            base has it and the build's allocations stay as they are. A frame that would need a bigger box stays
            as today (class "box"): the slot allows 32x32 at most (log2_sprites.SLOT_BYTES), and a bigger frame
            would move every later allocation. Only a floating effect speck (gi_art.floating, SPARK_MAX px or
            less) may fall off the box edge; the report counts it (clipped_specks).
         6. Last, the hand frames of the derived set (hand_frames.DERIVED) replace theirs.
Rules:   The source folders are never written. Every key of a shared PNG must give the same bytes, else the PNG
         stays as today and the report names it. Deterministic.
"""
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from art import gi_art  # noqa: E402
from art import hand_frames  # noqa: E402
import log_paths  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
SPRITES = log_paths.SPRITES
BASE = "gi_base"
VANILLA_BASE = "set56"
OUTPUTS = {"gi_ssj_v4": ("gi_ssj_v2", ("set59",)),                     # out: (head source, vanilla sets in order)
           "gi_ssj2_v4": ("gi_ssj2_v2", ("set58", "set59"))}
EXCEPTIONS = {                                                          # kept as today (final, 2026-10-22)
    "gi_ssj_v4": {},
    "gi_ssj2_v4": {(0, d, i): "SSJ2 idle: std golden body, aura idle records" for d in range(4) for i in range(2)}}
KEPT_BOX = {                                                            # need more than 32x32: kept (final, 2026-10-23)
    "gi_ssj_v4": {(4, 1, 3), (6, 0, 0), (7, 0, 0), (13, 0, 3)},
    "gi_ssj2_v4": {(6, 0, 0), (7, 0, 0)}}
# Anim 21 (the revert) has no base counterpart. Index 3 (standing, hair black) has the vanilla body of the base idle
# 0.0.0 (shape residual 1); indices 0-2 (power-down pose, residual 26 or more) have no clear match and stay.
POSE_MATCH = {out: {(21, d, 3): (0, 0, 0) for d in range(4)} for out in OUTPUTS}
# The 159 flight head sits 2 rows above the vanilla form head on the same body (irises, all indices; 158 sits at 0):
# the transplant placed it, and the base chin showed under it, so it moves back down. 159 12.0.x sits 1 row high
# too, but there the taller golden face needs that row: moved down, its mouth covers the base collar. It stays.
HEAD_ANCHOR = {"gi_ssj_v4": {},
               "gi_ssj2_v4": {(20, d, i): (0, 2) for d in (0, 2) for i in range(4)}}
SPAN = 2                                                                # body shift search, pixels
POSE_LIMIT = 25                                                         # shape residual: vanilla anim 16 starts at 28
HAIR = gi_art.GOLD | {16, 43, 45, 131, 142}                             # SSJ hair, its shine and the golden head's
SHINE = gi_art.LIGHT | {13, 14}
IRIS = {64, 65, 203}
ON_TOP = HAIR | SHINE | IRIS | {gi_art.SPARK_BLUE}                      # hair, effects, irises: over the body too
FACE = gi_art.SKIN | {23} | gi_art.EYES | gi_art.HAIR_BLACK | gi_art.FACE_EXTRA
BODY = gi_art.GI | gi_art.RED | gi_art.WRISTBAND | {87, 167, 215, 34, 35}   # gi, sash, wristbands, boots: never a head
NECK = gi_art.SKIN | {23}
Key = tuple


# ===== vanilla: shift and class =====

def _body(rec: dict) -> tuple:
    px = gi_art.frame_pixels(rec)
    head = gi_art.head_mask(px)
    return {p: v for p, v in px.items() if p not in head}, head


def _residual(form: tuple, base: tuple, sx: int, sy: int) -> tuple:
    (fb, fh), (bb, bh) = form, base
    moved = {(x + sx, y + sy): v for (x, y), v in fb.items()}
    heads = {(x + sx, y + sy) for x, y in fh} | bh
    shape = sum((p in moved) != (p in bb) for p in (set(moved) | set(bb)) - heads)
    color = sum(moved[p] != bb[p] for p in set(moved) & set(bb) - heads)
    return shape, color


def body_shift(form_rec: dict, base_rec: dict) -> tuple:
    """((sx, sy), (shape, color)): the shift that best puts the vanilla form body on the base body; (0, 0) wins ties."""
    form, base = _body(form_rec), _body(base_rec)
    top = ((0, 0), _residual(form, base, 0, 0))
    for sy in range(-SPAN, SPAN + 1):
        for sx in range(-SPAN, SPAN + 1):
            r = _residual(form, base, sx, sy)
            if sum(r) < sum(top[1]) or sum(r) == sum(top[1]) and abs(sx) + abs(sy) < sum(map(abs, top[0])):
                top = ((sx, sy), r)
    return top


def vanilla_form(key: Key, sets: list) -> dict:
    return next((s[key] for s in sets if key in s), None)


def base_key(out: str, key: Key) -> Key:
    """The base key whose body the form key takes: the same key, or its POSE_MATCH (anim 21)."""
    return POSE_MATCH[out].get(key, key)


def classify(key: Key, out: str, base: dict, vanilla: dict) -> tuple:
    """(class, shift, residual). vanilla = {"base": set56 by_key, "form": [form sets by_key, in order]}."""
    if key in EXCEPTIONS[out]:
        return "exception", (0, 0), None
    if key in KEPT_BOX[out]:
        return "box", (0, 0), None
    bk = base_key(out, key)
    if bk not in base or bk not in vanilla["base"]:
        return "no base", (0, 0), None
    van = vanilla_form(key, vanilla["form"])
    if van is None:
        return "no vanilla", (0, 0), None
    shift, res = body_shift(van, vanilla["base"][bk])
    return ("vanilla pose" if res[0] >= POSE_LIMIT else "derived"), shift, res


# ===== heads =====

def form_head(form_px: dict, vanilla_px: dict) -> set:
    """The form's head in object space: the vanilla head mask on the form's own pixels, grown through hair colors,
    shine with 2+ hair sides, face pixels the head encloses, and the vanilla SSJ2 sparks."""
    seed = gi_art.head_mask(vanilla_px)
    mask = {p for p in seed if p in form_px}
    edge = set(mask)
    while edge:
        edge = {q for p in edge for q in gi_art.neighbours(p, diag=True)
                if q not in mask and form_px.get(q) in HAIR}
        mask |= edge
    for _ in range(2):
        mask |= {p for p, v in form_px.items() if v in SHINE and p not in mask
                 and sum(q in mask and form_px[q] in HAIR for q in gi_art.neighbours(p)) >= 2}
    low = max((y for _, y in seed), default=0)
    mask |= {p for p, v in form_px.items() if v in FACE and p not in mask and p[1] <= low
             and gi_art._enclosed(p, mask)}
    return mask | (gi_art.sparks(vanilla_px, seed) & set(form_px))


def torso(base_px: dict, base_head: set) -> set:
    """The base gi: BODY-color parts that reach below the base head. A part inside the head rows is face shading
    (anim 18 shades the face with the gi outline color), not gi."""
    low = max((y for _, y in base_head), default=None)
    parts = gi_art.components({p for p, v in base_px.items() if v in BODY}, diag=True)
    return set().union(set(), *(c for c in parts if low is None or max(y for _, y in c) > low))


def _form_body(moved: dict) -> set:
    """The form's own body pixels: BODY colors, except a wristband blue beside an iris (the 18.x eyes use 195)."""
    return {p for p, v in moved.items() if v in BODY and not (
        v in gi_art.WRISTBAND and any(moved.get(q) in IRIS for q in gi_art.neighbours(p, diag=True)))}


def compose(base_px: dict, base_head: set, form_px: dict, head: set, shift: tuple) -> tuple:
    """(pixels, counts, head): the base body with the shifted form hair and face (head rule in the header)."""
    sx, sy = shift
    moved = {(x + sx, y + sy): v for (x, y), v in form_px.items()}
    fhead = {(x + sx, y + sy) for x, y in head}
    hair = {p for p in fhead if moved[p] in ON_TOP}
    fbody = _form_body(moved)
    face = fhead - hair - fbody
    gi = torso(base_px, base_head)
    out = {p: v for p, v in base_px.items() if p not in base_head or p in gi}
    won = face - gi
    out.update({p: moved[p] for p in won})
    leak = {p for p in base_head - fhead if p in moved and p not in out and p not in fbody}
    out.update({p: moved[p] for p in leak})
    under = {p for p in base_head if p not in out and p in fbody}
    neck = {p for p in under if base_px.get(p) in NECK}
    out.update({p: base_px[p] for p in neck})
    under -= neck                                    # base hair covered the body here: the form body fills it
    out.update({p: moved[p] for p in under})
    sash = {p for p in gi if base_px[p] in gi_art.RED}
    out.update({p: moved[p] for p in hair - sash})
    pits = {p for p in base_head & set(base_px) if p not in out and all(q in out for q in gi_art.neighbours(p))}
    out.update({p: base_px[p] for p in pits})        # a base pixel the new frame encloses stays: no 1 px hole
    skin = gi_art.SKIN | {23}
    counts = {"form_head": len(fhead), "leak": len(leak), "neck_kept": len(neck), "gi_under_hair": len(under),
              "pits_kept": len(pits),
              "face_lost": len(face - won), "form_body_dropped": len(fhead & fbody - hair),
              "hair_over_body": sum(p in base_px and p not in base_head for p in hair),
              "face_diff": sum(base_px[p] != moved[p] for p in fhead & base_head
                               if base_px.get(p) in skin and moved.get(p) in skin),
              "changed_aligned": sum(out.get(p) != moved.get(p) for p in set(out) | set(moved)),
              "changed_screen": sum(out.get(p) != form_px.get(p) for p in set(out) | set(form_px))}
    return out, counts, fhead


# ===== folders =====

def _clipped(px: dict, dx: int, dy: int, w: int, h: int) -> set:
    return {(x, y) for x, y in px if not (dx <= x < dx + w and dy <= y < dy + h)}


def fit_box(px: dict, rec: dict) -> tuple:
    """(dx, dy, clipped pixels): the record's own size placed to hold the most pixels, today's place on ties.
    The size never changes: a bigger frame would move every later allocation of the build."""
    best = None
    for dy in range(rec["dy"] - SPAN, rec["dy"] + SPAN + 1):
        for dx in range(rec["dx"] - SPAN, rec["dx"] + SPAN + 1):
            cut = _clipped(px, dx, dy, rec["w"], rec["h"])
            score = (len(cut), abs(dx - rec["dx"]) + abs(dy - rec["dy"]))
            if best is None or score < best[0]:
                best = (score, dx, dy, cut)
    return best[1], best[2], best[3]


def _stored_bytes(px: dict, rec: dict, palette: list) -> bytes:
    return gi_art.render(px, rec, palette).tobytes()


def context(art: Path, out: str) -> dict:
    """The by_key tables one output needs: base, form (head source) and the vanilla sets."""
    src_name, sets = OUTPUTS[out]
    return {"out": out, "base": gi_art.by_key(art / BASE), "form": gi_art.by_key(art / src_name),
            "vanilla": {"base": gi_art.by_key(SPRITES / VANILLA_BASE),
                        "form": [gi_art.by_key(SPRITES / s) for s in sets]}}


def derive_key(ctx: dict, k: Key) -> tuple:
    """(report row, object-space pixels or None, head). Pixels only for a derived key whose box holds them."""
    cls, shift, res = classify(k, ctx["out"], ctx["base"], ctx["vanilla"])
    bk = base_key(ctx["out"], k)
    row = {"class": cls, "base_key": gi_art.key_str(bk), "shift": list(shift), "residual": list(res) if res else None}
    if cls != "derived":
        return row, None, set()
    bpx, fpx = gi_art.frame_pixels(ctx["base"][bk]), gi_art.frame_pixels(ctx["form"][k])
    vpx = gi_art.frame_pixels(vanilla_form(k, ctx["vanilla"]["form"]))
    bhead = gi_art.head_mask(gi_art.frame_pixels(ctx["vanilla"]["base"][bk]))
    ax, ay = HEAD_ANCHOR[ctx["out"]].get(k, (0, 0))
    hs = (shift[0] + ax, shift[1] + ay)
    row["head_shift"] = list(hs)
    px, counts, head = compose(bpx, bhead, fpx, form_head(fpx, vpx), hs)
    dx, dy, cut = fit_box(px, ctx["form"][k])
    specks = set().union(set(), *(c for c in gi_art.floating(px) if len(c) <= gi_art.SPARK_MAX))
    row |= counts | {"place": [dx, dy], "clipped": len(cut), "clipped_body": len(cut - head - specks),
                     "clipped_specks": len(cut & specks)}
    if cut - specks:                                          # needs a bigger box than the record: stays as today
        row["class"] = "box"
        return row, None, head
    return row, {p: v for p, v in px.items() if p not in cut}, head   # a cut-off effect speck is dropped


def _png(ctx: dict, e: dict, src: Path, report: dict) -> tuple:
    """(index bytes, status) for one PNG of the source manifest; moves its keys' dx, dy when derived."""
    with Image.open(src / e["png"]) as im:
        palette, today = im.getpalette(), im.tobytes()
    made, rows = set(), {}
    for kd in e["keys"]:
        k = (kd["anim"], kd["dir"], kd["index"])
        row, px, _ = derive_key(ctx, k)
        rows[k] = row | {"png": e["png"]}
        place = {"dx": row["place"][0], "dy": row["place"][1]} if px is not None else {}
        made.add(_stored_bytes(px, ctx["form"][k] | place, palette) if px is not None else today)
    classes = {r["class"] for r in rows.values()}
    if len(made) == 1 and classes == {"derived"}:
        for kd in e["keys"]:
            kd["dx"], kd["dy"] = rows[(kd["anim"], kd["dir"], kd["index"])]["place"]
        status, data = "derived", made.pop()
    else:
        status, data = ("kept" if "derived" not in classes else "shared: a key of this PNG stays, so all do"), today
        for r in rows.values():
            r["class"] = "shared" if r["class"] == "derived" else r["class"]
    report["keys"].update({gi_art.key_str(k): r for k, r in rows.items()})
    return data, status, palette


def derive_folder(art: Path, out: str) -> dict:
    """Write art/out from art/gi_base plus the form heads of OUTPUTS[out]; returns the report."""
    ctx, src, dst = context(art, out), art / OUTPUTS[out][0], art / out
    man = gi_art.load_manifest(src)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    report = {"keys": {}, "pngs": {}}
    for e in man:
        data, status, palette = _png(ctx, e, src, report)
        with Image.open(src / e["png"]) as im:
            img = Image.frombytes("P", im.size, data)
        img.putpalette(palette)
        img.save(dst / e["png"], transparency=0)
        e["one_body"] = "derived: base body, form head" if status == "derived" else status
        report["pngs"][e["png"]] = status
    for note in hand_frames.place(dst, man):                 # head-only fixes of the derived set (DERIVED)
        print("hand frame", note)
    (dst / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", encoding="ascii", newline="\n")
    (dst / "one_body.json").write_text(json.dumps(report, indent=1) + "\n", encoding="ascii", newline="\n")
    return report


def run_all(art: Path = ART) -> dict:
    out = {}
    for name in OUTPUTS:
        rep = derive_folder(art, name)
        classes = {}
        for row in rep["keys"].values():
            classes[row["class"]] = classes.get(row["class"], 0) + 1
        print(f"{name}: keys {classes}, pngs {sum(s.startswith('derived') for s in rep['pngs'].values())} derived")
        out[name] = rep
    return out


def _table(art: Path = ART) -> None:
    base = gi_art.by_key(art / BASE)
    for name, (_, sets) in OUTPUTS.items():
        vanilla = {"base": gi_art.by_key(SPRITES / VANILLA_BASE), "form": [gi_art.by_key(SPRITES / s) for s in sets]}
        for k in sorted(gi_art.by_key(art / OUTPUTS[name][0])):
            cls, shift, res = classify(k, name, base, vanilla)
            print(name, gi_art.key_str(k), cls, shift, res)


def main(argv: list) -> int:
    if argv == ["all"]:
        run_all()
        return 0
    if argv == ["table"]:
        _table()
        return 0
    print(__doc__.split("Input:")[0])
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
