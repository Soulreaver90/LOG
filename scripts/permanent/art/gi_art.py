r"""
gi_art.py - Make Gohan's purple gi sprite frames (base, Super Saiyan, Super Saiyan 2) and the draft "Z2" HUD icon.

Usage:   py -3 -I scripts\permanent\art\gi_art.py all      (from the LOG root; needs art\vanilla-sets\set53,56,58,59 and,
         for compare, set60,61,129,130,137,140)
         Commands: all | frames | sheets | anim | compare | z2   (all = frames, sheets, anim, compare; z2 on request)
Output:  art\gi_base\, gi_ssj\, gi_ssj2\ (one indexed PNG per frame header, plus manifest.json with the
         geometry and the checks of every frame), contact sheets art\gi_*_sheet.png, gi_overview.png,
         gi_ssj_9_2_test_cases.png, flipbook strips and GIFs under art\anim\<form>\, the transform
         comparison art\anim\compare_transform.png with GIFs in anim\compare\, and (z2) hud_z2*.
API:     make_gi_set(name, layout, out_dir, palette, fixes) -> None      form_layout(name) -> {key: (geometry, source)}
         armor_to_gi(px, mask, parts, key, sash_anchor, sash_cap) -> (pixels, notes)   sash_rows(name) -> dict
         finish(px, mask, key, keep, arms) -> (V, notes)
         gi_rules(px, mask, fixed, key, parts, lean, torso, orig) -> notes   (shoes, gap_folds, shade, v_lines,
         straps, golden_torso, torso_shift: the golden rules, each callable alone)
         armor_body_diff(own, other) -> pixels   shared_body(px, top, body, body_head) -> pixels
         stray_pinks(px) -> pixels changed       chest(px, mask, k, arms) -> (skin, gi, ok)
         frame_checks(px, mask, orig, rec, key, keep, old_head, arms) -> dict   failing(entry) -> [check names]
         torso_split(px, body, chest, gloves, waist_y, back_cols, walk, boots) -> (torso, plate, span)
         part_map(orig, mask, parts, keep) -> {pixel: part}   check_parts(px, orig, mask, parts, keep, key) -> dict
         feet(boots, edge) -> [foot]   shoe_top(foot, raised) -> row   loose_white(px, body) -> pixels
         make_z2_icons(rom, out_dir) -> None
Method:  (final, 2026-10-16, Rulings 25-27) The pose and the record geometry of every gi frame are the original frame
         of the same form: set 56 for base, 59 for Super Saiyan, 58 for Super Saiyan 2 (59 where 58 has no frame).
         The head, hair, eyes, aura, sparks and attack arcs stay as they are. The armor body is repainted as the gi:
         jumpsuit and chest plate to Piccolo purple (88, 89, outline 211), arms to skin (the gi is sleeveless),
         gloves to skin fists with blue wristbands (195, 72), the lowest BOOT_ROWS rows of each boot to brown
         (34, 35) and the boot shaft to trouser purple, a red sash (26, 27) at the waist. Then armor whites left in
         the body are repainted, bare chest is covered, front frames get a V-neck centred on the gi under the
         collar (3 over 1) and side frames a quarter-angle neck opening (2 over 1), as on the golden frames.
         Shape rules sort the white parts into hands, boots and chest; a white part on the ground shadow is a
         raised knee or boot, never a fist (final, 2026-10-17). PART_HINTS and PART_SPLITS override the few parts
         they miss (found in the strip review). Set 53 (the purple Demon Clothes) is the color and style reference.
         A glove whose forearm is hidden gets a band across the end facing the shoulder, never more than half
         the fist. The lit charge frames (anim 18, index 2 and up) read their parts from the unlit frame 1 of
         the same dir and keep their own lit head. Skin joined to the face is neck whatever the hair height.
         The sash keeps frame 0's row of its (anim, dir) when only the torso stretches, and the base sash never
         sits below the Super Saiyan sash of the same pose (SASH_MATCH; me, 2026-10-17, 10:38 and 10:56 PM).
         Super Saiyan 2 keys that set 58 lacks take the set 59 body and one set 58 head per (anim, dir), placed by
         the eyes; arms in front of the hair and an aura ring stay; the revert keeps its base head. HEAD_TURN
         turns the head 90 degrees on lying frames, HEAD_NUDGE lifts it on flying frames to show the torso,
         and arms-up frames (anim 11) lower the hair top to the fists. Stand-in hair then loses rows or columns,
         spread between its tip and the eyes, until the frame fits the 32x32 player slot (SLOT_BYTES, Ruling 35).
         Golden rules (mine, 2026-10-17/18, art\golden\golden_gi_{base,ssj,ssj2}_d0-3.png) then run on
         every frame: shoes are the 2 boot rows nearest the sole with a 211 hem under the trouser (along the legs
         from the hip on lying and flying frames); gi under the sash over a gap between the legs is 211; rule C
         shades each horizontal gi run (base 89, lit 88, light from the image left); a torso whose armor equals
         the idle torso of its dir takes the golden's pixels, any other front torso gets the V's 211 lines, and
         a front or back torso gets the strap over each shoulder (the golden torso goes on each frame on its own;
         a strap holds for a whole animation and dir or not at all, and a golden torso frame carries the golden
         strap); anim 9 frames 1-3 light one step further (88 to 87, 89 beside a lit pixel to 88).
         The idle slots of gi_base and gi_ssj are the goldens byte for byte, and gi_base walk 1.0.0-1.0.3 my
         drawn frames (OWNER_FRAMES, me, 2026-10-18 9:48 AM). The reviewed r12fix hand frames of gi_base
         (hand_frames.HAND) win the same way; gi_post and gi_aura place those of sets 158 and 159.
         Parts by shape (me, 2026-10-18 9:52 AM to 11:03 AM): torso_split finds the torso of an upright front or
         back frame from the chest plate down to the waist (the golden back's width in back views); suit outside
         it that reaches a glove is arm (skin, its own outline), a torso pixel beside an arm is 211, the sash runs
         on the torso columns only, and a dark line parts walking legs. Each foot (feet(): fill blobs, stacked
         blobs joined, column soles) gets its shoe from where it widens, a hem only under a leg that comes down,
         a raised back foot one row. A boot inside the swoosh arc is a boot; white touching only white is effect.
         The golden torso never covers an arm or glove below the strap rows. check_parts (manifest "parts")
         maps the armor into head, effect, shadow, glove, boot, arm, torso and leg and asks each for its gi
         colors; PARTS_REVIEW lists the frames left for me. SASH_NUDGE holds reviewed sash rows.
         One body (final, 2026-10-18): where the armor of sets 58 and 59 is the same under the chin, gi_ssj2 takes
         the finished gi_ssj body with its own head and sparks on top (manifest "body": "gi_ssj"), unless the
         chest check then fails (a stand-in head that sits higher shows a second neck opening). Pink strays
         239 and 240 of set 58 are cleared outside the outline, else take their most common neighbour.
Rules:   Only palette indices of the shared OBJ palette (rom:0x1DA6C8). Every check is in the manifest per frame.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from art import hand_frames  # noqa: E402
import log_paths  # noqa: E402
from rom.log2_sprites import OBJ_SHAPES, PALETTE_LEN, PALETTE_OFF, SLOT_BYTES, image_to_tiles, tiles_to_image  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE_ROM = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
SPRITES = log_paths.SPRITES
ART = log_paths.ART
WORK = ART / "work"                                        # old-method frames kept for before and after sheets
HFLIP = 0x1000
Key = tuple                                                # (anim, dir, index)

FORMS = {"gi_base": "set56", "gi_ssj": "set59", "gi_ssj2": "set58"}   # gi folder: the form's original set
FALLBACK = {"gi_ssj2": "set59"}                            # record list and keys the original set lacks
SHARE = {"gi_ssj2": "gi_ssj"}                              # one gi body where the armor bodies match (final, 2026-10-18)
BACK_DIR = 1                                               # dir 1 shows Gohan's back
TRANSFORM_ANIM = 9                                         # faces front in every dir
SASH_MATCH = {"gi_base": "gi_ssj"}                         # same poses: the base sash never sits below the SSJ one
# Reviewed sash rows: {folder: {"anim.dir.index": rows to move}}. Base 16.0.2 (11:03 AM, 74.png): the kick's
# sash sat on the narrow hip row under the torso; one row up it spans the full waist, as on the SSJ frame.
SASH_NUDGE = {"gi_base": {"16.0.2": -1}}

# Palette groups (indices of the shared OBJ palette)
RED = {24, 25, 26, 27}
SKIN = {113, 114, 115, 116, 117}                           # 114 lightest, then 115, 116, 117, 113 darkest
GI = {88, 89, 211}                                         # Piccolo purple, dark purple, outline
WRISTBAND = {72, 195, 77}
BOOT_EDGE, BOOT_FILL = 35, 34
BOOT_ROWS = 3                                              # gi boot height; armor boot rows above it become trouser leg
GOLD = {18, 19, 20, 21, 22, 36, 37, 38, 39, 44, 45, 46, 120, 121}    # Super Saiyan hair, its outline and aura
EYES = {48, 49, 50, 64, 65, 203}
HAIR_BLACK = {1, 15}
HAIR_BLACK_ID = 1                                             # stands for 'already head' in rim counts
SHADOW = 1                                                 # the ground shadow under the feet (black)
FACE_EXTRA = {2, 9, 11, 12}                                # eye whites and shine, only inside the head rows
HEAD_ROWS = 16                                             # a head is at most this tall, from its top pixel
NECK_SEED = 2                                              # the neck flood starts this many rows above the zone edge
LIGHT = {2, 9, 10, 11, 12, 43}                             # white and light grey: max channel >= 136, spread <= 48
SUIT = {77, 79, 80, 81}                                    # armor jumpsuit blues; 81 is its outline and shade
TRIM = {16, 40, 41, 42, 46, 128, 131, 142}                 # armor yellows (straps, trim, belt)
ARMOR_WHITE = {2, 9, 10, 11, 12, 13, 14}                   # plate, gloves and boots; 13 and 14 outline them
ARM_HALF = 1.5                                             # half the width of a bare arm, in pixels
SPARK_MAX = 4                                              # a lightning spark is a small white part off the body
SPARK_BLUE = 191                                           # light blue (Ruling 19); the core stays white (2)

# (dx, dy below the chin, skin). Front: centred under the neck, 3 over 1 (golden fronts, me, 2026-10-17).
# Side: the quarter-angle neck opening, 2 over 1 at the neck's front end; dx counts toward the back of the head.
V_NECK = ((-1, 1, 116), (0, 1, 115), (1, 1, 116), (0, 2, 116))
SIDE_NECK = ((0, 1, 116), (1, 1, 116), (0, 2, 116))
V_LIMIT = {"front": len(V_NECK), "side": len(SIDE_NECK), "back": 0}   # most chest skin a frame may show
CHEST_ROWS = 6                                             # rows under the chin where a bare chest would show

SLOT_SIDE = 32            # the largest legal 8bpp shape that fits the SLOT_BYTES player slot is 32x32 (Ruling 35)

# ===== frames in object space =====

def key_str(k: Key) -> str:
    return f"{k[0]}.{k[1]}.{k[2]}"

def load_manifest(d: Path) -> list:
    return json.loads((Path(d) / "manifest.json").read_text(encoding="ascii"))

def by_key(d: Path) -> dict:
    """{key: record} for an exported set folder (log2_sprites.export_set) or a gi folder."""
    out = {}
    for m in load_manifest(d):
        for k in m.get("keys", [m]):
            out[(k["anim"], k["dir"], k["index"])] = {**m, **k, "dir_path": Path(d)}
    return out

def frame_pixels(rec: dict) -> dict:
    """{(x, y) in object space: index} for the non-transparent pixels of a record's image."""
    return image_pixels(Image.open(rec["dir_path"] / rec["png"]), rec)

def image_pixels(img: Image.Image, rec: dict) -> dict:
    """Object-space pixels of an image shown through a record (dx, dy, H-flip)."""
    w, h = img.size
    data = img.tobytes()
    flip = rec["attr1"] & HFLIP
    out = {}
    for y in range(h):
        for x in range(w):
            v = data[y * w + x]
            if v:
                out[(rec["dx"] + (w - 1 - x if flip else x), rec["dy"] + y)] = v
    return out

def render(pixels: dict, rec: dict, palette: list) -> Image.Image:
    """Object-space pixels into an image of the record (its w, h, dx, dy and flip). Clips outside."""
    w, h, flip = rec["w"], rec["h"], rec["attr1"] & HFLIP
    buf = bytearray(w * h)
    for (ox, oy), v in pixels.items():
        x, y = ox - rec["dx"], oy - rec["dy"]
        if flip:
            x = w - 1 - x
        if 0 <= x < w and 0 <= y < h:
            buf[y * w + x] = v
    img = Image.frombytes("P", (w, h), bytes(buf))
    if palette:
        img.putpalette(palette)
    img.info["transparency"] = 0
    return img

def neighbours(p, diag=False):
    x, y = p
    yield from ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
    if diag:
        yield from ((x + 1, y + 1), (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1))

def components(points: set, diag=False) -> list:
    left, out = set(points), []
    while left:
        stack = [left.pop()]
        comp = set(stack)
        while stack:
            for q in neighbours(stack.pop(), diag):
                if q in left:
                    left.discard(q)
                    comp.add(q)
                    stack.append(q)
        out.append(comp)
    return out

def touching(comp: set, px: dict, diag=True) -> set:
    """Indices of the pixels next to a component (outside it)."""
    return {px[q] for p in comp for q in neighbours(p, diag) if q in px and q not in comp}

# ===== heads and effects =====

def head_mask(px: dict) -> set:
    """The head of an armor-set frame: hair joined to the top, face and neck skin, eyes, and gold aura on the
    sprite edge. Attack arcs and the armor are left out."""
    hair_pts = {p for p, v in px.items() if v in HAIR_BLACK | GOLD}
    if not hair_pts:
        return set()
    top = min(y for _, y in hair_pts)
    zone = top + HEAD_ROWS + 2
    mask = set()
    for comp in components(hair_pts, diag=True):
        on_edge = sum(1 for p in comp if any(q not in px for q in neighbours(p)))
        if min(y for _, y in comp) < top + 6 or all(px[p] in GOLD for p in comp) and on_edge:
            mask |= comp                                        # hair from the top, or aura on the sprite edge
    armor = {p for p, v in px.items() if v in SUIT}            # an aura round the body encloses the armor too
    armor |= set().union(set(), *(c for c in components({p for p, v in px.items() if v in ARMOR_WHITE}, diag=True)
                                  if any(q in armor for p in c for q in neighbours(p, diag=True))))
    mask |= {p for p in px if p not in mask and p not in armor and p[1] < top + HEAD_ROWS and _enclosed(p, mask)}
    for comp in components({p for p, v in px.items() if v in LIGHT and p not in mask and p[1] < zone}):
        rim = [HAIR_BLACK_ID if q in mask else px.get(q) for p in comp for q in neighbours(p) if q not in comp]
        bright = sum(px[p] in (2, 9, 43) for p in comp) * 2 > len(comp)   # shine is white; a glove is grey shaded
        if bright and sum(v in HAIR_BLACK | GOLD for v in rim) >= 0.6 * len(rim) and not set(rim) & (SUIT | {13, 14}):
            mask |= comp                                        # a shine blob ringed by hair (a glove has a grey rim)
    for _ in range(2):                                          # shine on the hair's rim: 2+ hair sides
        mask |= {p for p, v in px.items() if v in LIGHT | {13, 14} and p not in mask and p[1] < zone
                 and sum(q in mask and px[q] in HAIR_BLACK | GOLD for q in neighbours(p)) >= 2}
    mask |= {p for p, v in px.items() if v in SKIN | {23} and p[1] < zone} | {p for p, v in px.items() if v in EYES}
    mask |= _neck(px, mask, zone)
    mask |= {p for p, v in px.items() if v in TRIM and p[1] < zone                 # nose and cheek shine in the face
             and sum(px.get(q) in SKIN for q in neighbours(p, diag=True)) >= 5}
    face = {p for p, v in px.items() if v in SKIN}
    pupils = {p for p, v in px.items() if v in EYES} | {p for p in mask if px[p] in HAIR_BLACK and p[1] < zone
                                                      and any(px.get(q) in SKIN for q in neighbours(p))}
    for _ in range(2):                                          # eye whites and pupils sit in the face, under hair
        mask |= {p for p, v in px.items() if v in FACE_EXTRA | HAIR_BLACK and p[1] < zone and p not in mask
                 and any(q in face or q in pupils for q in neighbours(p, diag=True))
                 and px.get((p[0], p[1] - 1)) in SKIN | HAIR_BLACK | EYES | FACE_EXTRA | GOLD}
    for comp in components({p for p in mask if px[p] in ARMOR_WHITE}, diag=True):
        rim = [px.get(q) for p in comp for q in neighbours(p) if q not in comp]
        eyes = any(q in pupils for p in comp for q in neighbours(p, diag=True))
        if set(rim) & SUIT and not eyes and sum(v in HAIR_BLACK | GOLD for v in rim) * 2 < len(rim):
            mask -= comp                                        # a glove at the chin joins its sleeve: not the face
    outside = {p for p, v in px.items() if v in ARMOR_WHITE and p not in mask}
    for comp in components({p for p in mask if px[p] in ARMOR_WHITE}, diag=True):
        near = {q for p in comp for q in neighbours(p, diag=True)} & outside
        eyes = any(q in pupils for p in comp for q in neighbours(p, diag=True))
        if len(comp) <= 4 and near and not eyes and max(len(c) for c in components(outside, diag=True) if c & near) >= 4:
            mask -= comp                                        # the last row of a fist held against the hair
    return mask

def _neck(px: dict, mask: set, zone: int) -> set:
    """Skin joined to the face that lies below the zone: the neck. The zone counts from the hair top, so taller
    hair lifts it over the neck (final, 2026-10-17, 157 9.0.2: the chin turned purple). The flood starts NECK_SEED
    rows above the zone edge, so a skin piece the zone cuts (a hand by the chin, 8.0.3) is not taken as neck."""
    seen = {p for p in mask if px[p] in SKIN and p[1] <= zone - NECK_SEED}
    edge = set(seen)
    while edge:
        edge = {q for p in edge for q in neighbours(p) if q not in seen and px.get(q) in SKIN}
        seen |= edge
    return {p for p in seen if p[1] >= zone}

def _enclosed(p: tuple, region: set, reach: int = 3, reach_x: int = 8) -> bool:
    """True when `region` lies within `reach` pixels of p up and down and `reach_x` pixels left and right
    (a band of hair shine can run across the whole head)."""
    return all(any((p[0] + dx * d, p[1] + dy * d) in region for d in range(1, (reach_x if dx else reach) + 1))
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))

def swoosh(px: dict) -> set:
    """Attack arcs: white lines on the sprite edge. Short arcs: most pixels with at most 2 white neighbours.
    Long arcs (10+ pixels, often a staircase joined to a glove or boot or drawn over the hair): almost no
    pixel with 4 white sides, and at least half the rim open. A glove is a blob; hair shine has a closed rim."""
    light = {p for p, v in px.items() if v in (2, 9)}
    arc = set()
    for comp in components(light, diag=True):
        xs, ys = [x for x, _ in comp], [y for _, y in comp]
        if not any(q not in px for p in comp for q in neighbours(p, diag=True)):
            continue
        thin = sum(1 for p in comp if sum(q in comp for q in neighbours(p, diag=True)) <= 2) / len(comp)
        core = sum(1 for p in comp if all(q in comp for q in neighbours(p)))
        rim = [q for p in comp for q in neighbours(p) if q not in comp]
        open_rim = sum(q not in px for q in rim) / max(len(rim), 1)
        span = max(max(xs) - min(xs), max(ys) - min(ys))
        # a glove's white dots sit inside a grey rim, so a short thin line needs an open rim (or 10+ pixels)
        short = len(comp) >= 3 and span >= 3 and thin >= 0.7 and (open_rim >= 0.4 or len(comp) >= 10)
        line = len(comp) >= 3 and (len(set(xs)) == 1 or len(set(ys)) == 1) and open_rim >= 0.6  # a straight speed line
        long_arc = len(comp) >= 10 and core <= len(comp) // 6 and open_rim >= 0.6
        edged = len(comp) >= 5 and open_rim >= 0.45                 # a short arc with grey edges
        if short or long_arc or edged or line:
            arc |= comp
    return arc

def floating(px: dict) -> list:
    """Light and grey parts that touch no other color: arcs, sparks, dust. They are effects, not armor. A part
    of at most SPARK_MAX pixels may also touch hair when it has an open side (a spark on the hair's rim)."""
    grey = {p for p, v in px.items() if v in LIGHT | {13, 14}}
    out = []
    for c in components(grey, diag=True):
        other = touching(c, px) - LIGHT - {13, 14}
        if not other or len(c) <= SPARK_MAX and not other - GOLD - HAIR_BLACK                 and any(q not in px for p in c for q in neighbours(p)):
            out.append(c)
    return out

def sparks(px: dict, mask: set) -> set:
    """Super Saiyan 2 lightning: small floating white parts near the head."""
    if not mask:
        return set()
    x0, x1 = min(x for x, _ in mask) - 6, max(x for x, _ in mask) + 6
    y0, y1 = min(y for _, y in mask) - 6, min(y for _, y in mask) + HEAD_ROWS + 4
    out = set()
    for c in floating(px):
        cx, cy = sum(x for x, _ in c) / len(c), sum(y for _, y in c) / len(c)
        if len(c) <= SPARK_MAX and x0 <= cx <= x1 and y0 <= cy <= y1 and not c & mask:
            out |= c
    return out

def paint_sparks_blue(px: dict, spots: set) -> None:
    """Ruling 19: light blue body, white core (the pixel nearest each spark's middle)."""
    for c in components(spots, diag=True):
        cx, cy = sum(x for x, _ in c) / len(c), sum(y for _, y in c) / len(c)
        core = min(c, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
        for p in c:
            px[p] = 2 if p == core and len(c) > 1 else SPARK_BLUE

def best_shift(a: dict, b: dict, span: int = 4) -> tuple:
    """(sx, sy) that makes a shifted by it match b in the most pixels of equal index."""
    best, best_hits = (0, 0), -1
    for sy in range(-span, span + 1):
        for sx in range(-span, span + 1):
            hits = sum(1 for (x, y), v in a.items() if b.get((x + sx, y + sy)) == v)
            if hits > best_hits or hits == best_hits and abs(sx) + abs(sy) < abs(best[0]) + abs(best[1]):
                best, best_hits = (sx, sy), hits
    return best

def mask_shift(a: set, b: set, span: int = 4) -> tuple:
    """(sx, sy) that makes shape a shifted by it cover shape b best."""
    best, best_hits = (0, 0), -1
    for sy in range(-span, span + 1):
        for sx in range(-span, span + 1):
            hits = sum(1 for (x, y) in a if (x + sx, y + sy) in b)
            if hits > best_hits or hits == best_hits and abs(sx) + abs(sy) < abs(best[0]) + abs(best[1]):
                best, best_hits = (sx, sy), hits
    return best

def head_score(a: dict, b: dict) -> float:
    """0..1 overlap of two head masks after mask_shift; picks a stand-in head."""
    ma, mb = head_mask(a), head_mask(b)
    sx, sy = mask_shift(ma, mb)
    return sum(1 for (x, y) in ma if (x + sx, y + sy) in mb) / max(len(ma), len(mb), 1)

# ===== armor to gi =====

def chin_of(px: dict, mask: set):
    """(face middle x, chin row): the lowest face pixel of the head mask. None without a face."""
    face = [(x, y) for x, y in mask if px.get((x, y)) in SKIN | {23}]
    if not face:
        return None
    return sum(x for x, _ in face) / len(face), max(y for _, y in face)

def _ring(p: tuple, r: int) -> list:
    """Points within Chebyshev distance r of p."""
    return [(p[0] + dx, p[1] + dy) for dx in range(-r, r + 1) for dy in range(-r, r + 1)]

ARM_REACH = 10                                             # steps from the glove to the shoulder along a sleeve

def _torso(suit: set) -> set:
    """Suit pixels within 2 px of a 5x5 all-suit block: a back or bodysuit too wide to be an arm."""
    core = {p for p in suit if all((p[0] + dx, p[1] + dy) in suit for dx in range(-2, 3) for dy in range(-2, 3))}
    return {(x + dx, y + dy) for x, y in core for dx in range(-2, 3) for dy in range(-2, 3)} & suit

def _sleeve(glove: set, suit: set, reach: int = ARM_REACH) -> set:
    """Suit pixels joined to the glove within ARM_REACH 4-steps, outside any torso-wide block: the sleeve, also
    where it lies across the torso (my review 2026-10-17: the corridor rule missed arms that cross the body)."""
    suit = suit - _torso(suit)
    seen = {q for p in glove for q in neighbours(p) if q in suit}
    edge = set(seen)
    for _ in range(reach - 1):
        edge = {q for p in edge for q in neighbours(p) if q in suit and q not in seen}
        seen |= edge
    return seen

# Why (me, 2026-10-18 9:48-9:52 AM): arms, legs and torso sides are one blue bodysuit, so color cannot tell an arm
# from the torso; the arm corridor and the sleeve flood painted torso blue beside a raised fist (front walk) and the
# back plate trim (back walk) as skin. Shape decides: the torso runs from the chest plate down to the waist, between
# the plate's outer columns widened by the suit run on the waist rows (the belly); an arm is suit outside that.
PLATE_MIN = 4                                              # a plate part is at least this big (smaller: a shine)
WALK_ANIM = 1                                              # walking: the head holds still over the swaying body
BACK_AGREE = 1                                             # golden back this close to the plate: a straight back

def torso_split(px: dict, body: set, chest: set, gloves: list, waist_y: int, back_cols: tuple = None,
                walk: bool = False, boots: set = frozenset()) -> tuple:
    """(torso, plate, (x0, x1)) of an armor frame. plate = the chest whites of the 8-joined part of chest whites
    and trim that holds the most of them (the trim joins plate rows; its columns do not count, since the
    shoulder trim reaches over the arms). torso = suit, trim and 13/14 pixels from the plate top to
    the waist row, in the columns of the plate and of the suit runs on the rows under it (down to the waist) that
    overlap those columns, never widened toward a glove or a boot (a kicking leg, 10:52 AM, 8.0.1). A
    suit part inside those columns that touches a glove and has plate on both sides on each of its rows is an
    arm across the chest: not torso. A back view takes the golden back's columns
    (`back_cols`, placed by the head) in every walk frame (9:55 AM) and wherever they lie within
    BACK_AGREE of the plate's middle (a straight back); a turned back gets no split (the old arm rules)."""
    parts = components({p for p in body if p in chest or px[p] in TRIM}, diag=True)   # trim bands join the plate
    plate = max((c & chest for c in parts), key=len, default=set())
    if len(plate) < PLATE_MIN:
        return set(), set(), None
    top, bottom = min(y for _, y in plate), max(y for _, y in plate)
    x0, x1 = min(x for x, _ in plate), max(x for x, _ in plate)
    hands = set().union(set(), *gloves) | boots                 # a limb's end: glove or boot
    for y in range(bottom + 1, waist_y + 1) or [waist_y]:      # the belly widens the torso, never toward a limb end
        for _, xs in _row_runs({p for p in body if p[1] == y and px[p] in SUIT}):
            if xs[0] <= x1 and xs[-1] >= x0:
                x0 = x0 if (xs[0] - 1, y) in hands else min(x0, xs[0])
                x1 = x1 if (xs[-1] + 1, y) in hands else max(x1, xs[-1])
    if back_cols:                                               # the back: exactly the golden back's columns,
        if not (walk or abs(sum(back_cols) - x0 - x1) <= 2 * BACK_AGREE):   # or no split on a turned back
            return set(), set(), None
        x0, x1 = back_cols
    torso = {p for p in body if top <= p[1] <= waist_y and x0 <= p[0] <= x1 and px[p] in SUIT | TRIM | {13, 14}}
    fills = {p for g in gloves for p in g if px[p] not in (13, 14)}
    for comp in components({p for p in torso if px[p] in SUIT and p[1] <= bottom}):
        rows = {y for _, y in comp}
        between = all(any((x, y) in plate for x in range(x0, min(cx for cx, cy in comp if cy == y))) and
                      any((x, y) in plate for x in range(max(cx for cx, cy in comp if cy == y) + 1, x1 + 1))
                      for y in rows)
        if between and any(q in fills for p in comp for q in neighbours(p)):
            torso -= comp
    return torso, plate, (x0, x1)

# Why (final, 2026-10-18 10:30 AM, base 8.0.2): the swoosh and the boot are both white 2, so swoosh() takes the
# boot fill the arc touches and the boot reads merged into the effect.
def boot_in_arc(px: dict, boots: set, effects: set) -> set:
    """Effect pixels that are boot fill: white, 4-joined to a boot, with boot outline (13/14) on both sides of it
    on its row within 4 pixels (inside the boot's outline, where the arc cannot be)."""
    out, grow = set(), True
    while grow:
        grow = False
        for x, y in effects - out:
            if px[(x, y)] not in ARMOR_WHITE - {13, 14} or not any(q in boots | out for q in neighbours((x, y))):
                continue
            sides = [any((x + s * d, y) in boots and px[(x + s * d, y)] in (13, 14) for d in range(1, 5))
                     for s in (-1, 1)]
            if all(sides):
                out.add((x, y))
                grow = True
    return out

# Why (final, 2026-10-18 9:48 AM, walk a1 d0): each foot has its own sole. A foot coming toward the camera shows
# the top of the shoe: the shoe starts on the first row of the armor boot's greatest width under its shaft:
# 4 rows in front walk frames 0 and 2, 2 rows on the idle goldens; a raised back foot shows 1 row.
FOOT_STEP = 2                                              # a sole this many rows higher is another foot
SHOE_MAX = 4                                               # the tallest shoe: the front foot of walk 1.0.0 and 1.0.2
SHAFT_MIN = 2                                              # boot shaft rows over the foot (golden idle, my walk)

# Why (ssj 4.1.1, 2.0.3): a boot's ankle band or shaft is a fill blob of its own above the foot. Blobs stacked in
# one column run are one foot, or the shoe paints a stripe at the ankle and a second shoe on the shaft.
def _stacked(blobs: list) -> list:
    """Fill blobs merged when they share at least half of the narrower blob's columns (one over the other)."""
    blobs = [set(b) for b in blobs]
    merged = True
    while merged:
        merged = False
        for i in range(len(blobs)):
            for j in range(i + 1, len(blobs)):
                a, b = {x for x, _ in blobs[i]}, {x for x, _ in blobs[j]}
                if 2 * len(a & b) >= min(len(a), len(b)):
                    blobs[i] |= blobs.pop(j)
                    merged = True
                    break
            if merged:
                break
    return blobs

def feet(boots: set, edge: set = frozenset()) -> list:
    """Boot pixels split into feet. Each 8-joined part splits by its fill (pixels not in `edge`, the outline): one
    foot per 8-joined fill blob, each outline pixel going to the nearest blob. Each foot then splits into runs of
    neighbouring columns whose sole rows (the lowest pixel of each column) step by less than FOOT_STEP (a rounded
    toe or heel steps by 1)."""
    out = []
    for part in components(boots, diag=True):
        blobs = components(part - edge, diag=True) or [part]
        blobs = _stacked(blobs)
        own = [set() for _ in blobs]
        for p in part:
            i = min(range(len(blobs)), key=lambda j: min(max(abs(p[0] - q[0]), abs(p[1] - q[1])) for q in blobs[j]))
            own[i].add(p)
        for foot in own:
            sole = {}
            for x, y in foot:
                sole[x] = max(sole.get(x, y), y)
            xs = sorted(sole)
            group = [xs[0]]
            for x in xs[1:] + [None]:
                if x is not None and x == group[-1] + 1 and abs(sole[x] - sole[group[-1]]) < FOOT_STEP:
                    group.append(x)
                    continue
                out.append({p for p in foot if p[0] in group})
                group = [x]
    return out

# Why (11:03 AM, 72.png, base 8.0.1): the hem closes a trouser leg that comes down onto the shoe. A kicking
# leg runs sideways into its boot, so the row over its shoe is shaft, not hem, and stays gi purple.
def _leg_above(p: tuple, body: set, boots: set) -> bool:
    """True when the column over boot pixel `p` meets leg (body that is not boot) before it leaves the body. A
    foot keeps its hem row when any pixel of the row has a leg over it."""
    x, y = p
    for r in range(y - 1, y - 1 - SHOE_MAX * 2, -1):
        if (x, r) not in body:
            return False
        if (x, r) not in boots:
            return True
    return False

def shoe_top(foot: set, raised: bool) -> int:
    """First row of a foot's shoe: the first row of the foot's greatest width, under a narrower shaft of at least
    SHAFT_MIN rows (the foot seen from the front), up to SHOE_MAX rows. Else the lowest SHOE_ROWS rows, or 1 row
    for a `raised` back foot (raised_feet())."""
    rows = sorted({y for _, y in foot})
    width = {y: sum(1 for _, r in foot if r == y) for y in rows}
    top = next(y for y in rows if width[y] == max(width.values()))
    if top - rows[0] >= SHAFT_MIN and rows[-1] - top + 1 <= SHOE_MAX:
        return top
    return rows[-1] - (1 if raised else SHOE_ROWS) + 1

def raised_feet(boots: set, split: list) -> list:
    """For each foot of `split` (feet()): True when it shares its boot part with a foot whose sole is FOOT_STEP or
    more lower (a back foot drawn behind the front one shows one shoe row: my walk 1.0.1, golden sides)."""
    out = []
    for foot in split:
        part = next(c for c in components(boots, diag=True) if foot <= c)
        out.append(max(y for _, y in part) - max(y for _, y in foot) >= FOOT_STEP)
    return out

def _grounded(part: set, px: dict, mask: set, chin_y: int) -> bool:
    """True when a white part (fill and outline) has the black ground shadow right under it, well below the chin."""
    return any(px.get((x, y + 1)) == SHADOW and (x, y + 1) not in mask and y > chin_y + CHEST_ROWS
               for x, y in part)

def body_rows(px: dict, mask: set, body: set, boots: set, feet_y: int) -> tuple:
    """(neck bottom, boot top, feet) rows of an armor frame: the rows a pose keeps when only its torso stretches.
    The neck bottom is the lowest skin or skin outline joined to the face, whatever the hair height."""
    seen = {p for p in mask if px[p] in SKIN}
    edge = set(seen)
    while edge:
        edge = {q for p in edge for q in neighbours(p) if q not in seen and px.get(q) in SKIN | {23}}
        seen |= edge
    return (max((y for _, y in seen), default=None), min((y for _, y in boots), default=None), feet_y)

# Why (10:52 AM, 16.0.4): a swoosh tail drawn over the body is white touching no other color side by side.
def loose_white(px: dict, body: set) -> set:
    """White fill parts of `body` whose 4-neighbours are all white, grey or empty: effect, not armor."""
    whites = components({p for p in body if px[p] in ARMOR_WHITE - {13, 14}})
    return set().union(set(), *(c for c in whites if not touching(c, px, diag=False) - LIGHT))

def armor_to_gi(px: dict, mask: set, parts: dict = None, key: tuple = None, sash_anchor: tuple = None,
                sash_cap: tuple = None, back: tuple = None) -> tuple:
    """Repaint an armor frame (set 56, 58, 59) as the gi; the head and all effects keep their pixels.
    Returns (pixels, notes). `parts`, when given, receives the pixel sets found (for review sheets), the sash row
    (`waist`) and the body rows (`pose`). `sash_anchor` and `sash_cap` are (body rows, sash row) of a reference
    frame: with the same body rows the sash takes the anchor row; with the same leg rows it never sits below the
    cap row (the cap is the same key of another form, so the pose is the same drawing). `back` = back_columns()
    of the form: the golden back's torso columns and the idle chin x."""
    out = dict(px)
    chin = chin_of(px, mask)
    if not chin:
        return out, ["no face: frame unchanged"]
    cx, chin_y = chin
    effects = set().union(set(), *floating(px)) | swoosh(px)
    body = {p for p, v in px.items() if p not in mask and p not in effects and v != 1}
    feet_y = max(y for _, y in body)
    # White parts by their fill (the grey 13/14 outline joins neighbouring parts, so it follows its fill)
    boots, chest, gloves = set(), set(), []
    flying = bool(key) and key[0] == 20                         # body level behind the head: feet need not be low
    xs, ys_all = [x for x, _ in body | mask], [y for _, y in body | mask]
    lying = max(xs) - min(xs) >= 1.4 * (max(ys_all) - min(ys_all)) or bool(key) and key[0] == 3 and key[2] >= 1
    far = max(body, key=lambda p: abs(p[0] - cx))[0] - cx      # lying (or knocked down, anim 3): feet at the far end
    hint = PART_HINTS.get(key_str(key), {}) if key else {}
    hinted, shines = [], []
    whites = components({p for p in body if px[p] in ARMOR_WHITE - {13, 14}})
    loose = loose_white(px, body)
    whites = [c for c in whites if not c <= loose]
    body -= loose
    for seed, last in (PART_SPLITS.get(key_str(key), {}) if key else {}).items():
        part = next((c for c in whites if seed in c), None)  # a fist drawn touching a boot: cut it below row `last`
        if part:
            whites.remove(part)
            whites += [c for c in ({p for p in part if p[1] <= last}, {p for p in part if p[1] > last}) if c]
    for comp in whites:
        ys = [y for _, y in comp]
        mx, my = sum(x for x, _ in comp) / len(comp), sum(ys) / len(ys)
        told = next((hint[p] for p in comp if p in hint), None)
        if told == "hand":
            gloves.append(comp)                                 # reviewed at 4x: the shape rules miss this part
            hinted.append(comp)
        elif told:
            {"boot": boots, "chest": chest}[told].update(comp)
        elif lying and far and (mx - cx) / far >= 0.55:
            boots |= comp
        elif not lying and max(ys) >= feet_y - 3 and (my > chin_y + 3 or flying):
            boots |= comp
        elif abs(mx - cx) <= 3.5 and chin_y < my <= chin_y + 8 and (touching(comp, px) & TRIM or len(comp) >= 10):
            chest |= comp                                       # the plate carries the yellow trim or is big
        elif len(comp) <= 3 and touching(comp, px) & TRIM:
            chest |= comp                                       # a collar or strap bit beside the trim, not a hand
        elif len(comp) == 1 and touching(comp, px) & SUIT and not touching(comp, px) & {13, 14}:
            shines.append(comp)                                 # a lone light pixel with no grey outline is a shine
        else:
            gloves.append(comp)
    while boots:                                                # a boot top beside a boot is the same boot
        near = {q for p in boots for q in _ring(p, 2)}
        top = [g for g in gloves if g & near and g not in hinted
               and (flying or lying or sum(y for _, y in g) / len(g) > chin_y + 3)]
        if not top:
            break
        for g in top:
            gloves.remove(g)
            boots |= g
    near = {q for p in boots for q in _ring(p, 2)}
    for comp in shines:                                         # a shine beside a boot is the knee's, else the chest's
        (boots if comp & near else chest).update(comp)
    fills = [set(g) for g in gloves], set(boots), set(chest)
    for p in (p for p in body if px[p] in (13, 14)):           # each outline pixel joins the part it borders
        near = set(neighbours(p, diag=True))
        hand = next((g for g, f in zip(gloves, fills[0]) if near & f), None)
        if hand is not None:
            hand.add(p)
        elif near & fills[1]:
            boots.add(p)
        elif near & fills[2]:
            chest.add(p)
    if not (lying or flying):                                   # a raised boot still sits on the ground shadow
        for g in [g for g in gloves if g not in hinted and _grounded(g, px, mask, chin_y)]:
            gloves.remove(g)                                    # me, 2026-10-17: a knee or boot, never a fist
            boots |= g
    reclaimed = boot_in_arc(px, boots, effects)                 # 10:30 AM: a boot the swoosh touches
    boots |= reclaimed
    body |= reclaimed
    hands = set().union(set(), *gloves)
    waist_y = max(y for _, y in chest) + 1 if chest else chin_y + 5
    if not (lying or flying):
        waist_y = max(waist_y, chin_y + 5)                      # a collar alone (back views) is not the chest plate
    pose = body_rows(px, mask, body, boots, feet_y)
    if not (lying or flying):
        if sash_anchor and sash_anchor[0] == pose:              # only the torso stretched: frame 0's sash row
            waist_y = sash_anchor[1]
        if sash_cap and sash_cap[0][1:] == pose[1:]:            # the same pose in another form: legs suffice
            waist_y = min(waist_y, sash_cap[1])
        waist_y += (parts or {}).get("nudge", 0)                # a reviewed sash row (SASH_NUDGE)
    torso, plate, span, edged = set(), set(), None, set()
    if not (lying or flying) and key and view(key) != "side":   # shape, not color, splits arm from torso
        cols = None
        if back and view(key) == "back":                        # the golden back moves with the head
            cols = tuple(x + round(cx - back[2]) for x in back[:2])
        torso, plate, span = torso_split(px, body, chest, gloves, waist_y, cols, key[0] == WALK_ANIM, boots)
    if span:
        for g in gloves:                                        # a glove beside the torso: the outline it shares
            if not any(span[0] <= p[0] <= span[1] for p in g if px[p] not in (13, 14)):   # with the plate is the
                moved = {(x, y) for x, y in g & torso if px[(x, y)] in (13, 14)          # torso's edge
                         and ((x - 1, y) in chest or (x + 1, y) in chest)}
                g -= moved
                chest |= moved
                edged |= moved
        hands = set().union(set(), *gloves)
        pads = {p for p in chest - plate if not span[0] <= p[0] <= span[1]}   # a shoulder pad bit: the arm's top
        chest -= pads
    arms = set()
    plate_y = max(y for _, y in chest) + 1 if chest else waist_y
    plate_x = (min(x for x, _ in chest), max(x for x, _ in chest)) if chest else (cx, cx - 1)
    belly = {p for p in body if plate_y <= p[1] < waist_y and plate_x[0] <= p[0] <= plate_x[1]}   # suit under the plate
    if key and view(key) == "back" and chest:                   # seen from behind, arms hang beside the back plate
        top = min(y for _, y in chest)
        belly |= {p for p in body if top <= p[1] < waist_y and plate_x[0] <= p[0] <= plate_x[1]}
    # An arm runs from each glove to its shoulder (beside the neck, on the glove's side); the suit in that
    # 3 px corridor is a bare arm, also where it crosses the torso. The cuff is the glove's side nearest the shoulder.
    edge = {p for p in body if any(q not in px or px[q] == 1 for q in neighbours(p))}
    cuffs = 0
    wrists = []                                                 # (cuff, shoulder point, glove) for the sleeve check
    seeded = []                                                 # reviewed arms (ARM_SEEDS): suit islands
    straight = set()                                            # a fist under the sash: its arm crosses the belly
    if key and key_str(key) in ARM_SEEDS:
        isles = components({p for p in body - hands - boots - chest if px[p] in SUIT and p[1] < waist_y})
        for seed in ARM_SEEDS[key_str(key)]:
            isle = next((c for c in isles if seed in c), set())
            if len(isle) <= ARM_ISLAND_MAX:                     # a torso-sized island is never an arm
                seeded.append(isle)
                arms |= isle
    for comp in gloves:
        gx, gy = sum(x for x, _ in comp) / len(comp), sum(y for _, y in comp) / len(comp)
        sx, sy = cx + max(-3.0, min(3.0, gx - cx)), chin_y + (-2 if flying and gy < chin_y else 2)
        collar = [p for p in body if px[p] in TRIM]
        if flying and key[1] in (1, 3) and collar:             # seen from behind: the arm meets the collar line
            sx, sy = min(collar, key=lambda p: (p[0] - gx) ** 2 + (p[1] - gy) ** 2)
        vx, vy = sx - gx, sy - gy
        length = max((vx * vx + vy * vy) ** 0.5, 1e-6)
        for p in body - comp - boots - chest - torso:
            if px[p] not in SUIT | TRIM | {13, 14}:
                continue
            t = ((p[0] - gx) * vx + (p[1] - gy) * vy) / length ** 2
            off = abs((p[0] - gx) * vy - (p[1] - gy) * vx) / length
            if 0 < t <= 1 and off <= ARM_HALF:
                arms.add(p)
        fill = [p for p in comp if px[p] not in (13, 14)]
        sleeve = set()
        if not lying and ARM_REACH and len(fill) >= 2:         # the sleeve: suit joined to the glove
            reach = SHORT_REACH.get(key_str(key), ARM_REACH) if key else ARM_REACH
            low = min(y for _, y in comp)
            if low > waist_y:                                   # a fist hung below the sash: its arm runs straight
                cols = {x for x, y in comp if y == low}         # up from it, across the sash and the belly
                sleeve = _sleeve(comp, {p for p in body - comp - boots - chest - hands
                                        if px[p] in SUIT and p[1] < low and p[0] in cols}, reach)
                straight |= sleeve
            else:
                sleeve = _sleeve(comp, {p for p in body - comp - boots - chest - hands - belly - torso
                                        if px[p] in SUIT and p[1] < waist_y}, reach)
            arms |= sleeve
        if not sleeve:                                          # a reviewed arm beside the glove is its sleeve
            sleeve = next((i for i in seeded if any(q in i for p in comp for q in neighbours(p, diag=True))), set())
        if sleeve:                                              # the sleeve points to the shoulder better than the guess
            sx, sy = sum(x for x, _ in sleeve) / len(sleeve), sum(y for _, y in sleeve) / len(sleeve)
        dist = {p: (p[0] - sx) ** 2 + (p[1] - sy) ** 2 for p in comp}
        near = min(dist.values())
        forearm = {p for p in comp if any(q in arms or px.get(q) in SUIT for q in neighbours(p))}
        cuff = {p for p in forearm if dist[p] <= near + 2.5}
        if not cuff and forearm:                                # the forearm meets the glove away from the shoulder line
            low = min(dist[p] for p in forearm)
            cuff = {p for p in forearm if dist[p] <= low + 2.5}
        if not cuff and len(comp) >= 4:                         # forearm hidden: a band across the end facing the shoulder
            ys = [y for _, y in comp]
            deep = min(2 if len(comp) >= 8 else 1, (max(ys) - min(ys) + 1) // 2)   # the band never eats the fist
            if sy > max(ys):
                cuff = {p for p in comp if p[1] > max(ys) - deep}
            elif sy < min(ys):
                cuff = {p for p in comp if p[1] < min(ys) + deep}
            else:
                cuff = {p for p in comp if dist[p] <= near + 1.5}
            while len(cuff) * 2 > len(comp) and len({dist[p] for p in cuff}) > 1:   # most of the fist stays skin
                far = max(dist[p] for p in cuff)
                cuff = {p for p in cuff if dist[p] < far}
        cuffs += bool(cuff)
        if cuff:
            wrists.append((frozenset(cuff), (sx, sy), frozenset(comp)))
        # a glove drawn without the 13/14 outline uses 12 on its rim (fists over the head): that rim is the outline
        rim12 = set() if any(px[p] in (13, 14) for p in comp) else \
            {p for p in comp if px[p] == 12 and any(q not in comp for q in neighbours(p))}
        for p in comp:
            v = px[p]
            dark = v in (13, 14) or p in rim12
            if p in cuff:
                out[p] = 72 if dark else 195
            else:
                out[p] = 23 if dark else {2: 114, 9: 114, 10: 115}.get(v, 116)
    arms = (arms - torso) | straight | set().union(set(), *seeded) | (pads if span else set())   # reviewed arms stay
    shin, hem = set(), set()
    if not (lying or flying) and key and view(key) == "side":   # side: BOOT_ROWS of each foot, shoes() cuts later
        for comp in feet(boots, {p for p in boots if px[p] in (13, 14)}):
            low = max(y for _, y in comp)
            shin |= {p for p in comp if p[1] <= low - BOOT_ROWS}
    elif not (lying or flying):                                 # front, back: each foot from where it widens
        split = feet(boots, {p for p in boots if px[p] in (13, 14)})
        for foot, up in zip(split, raised_feet(boots, split)):
            top = shoe_top(foot, up)
            shin |= {p for p in foot if p[1] < top}
            row = {p for p in foot if p[1] == top - 1}
            hem |= row if any(_leg_above(p, body - hands - arms, boots) for p in row) else set()
    legline = set()                                             # 9:48 AM, walk 1 and 3: the legs read apart
    if not (lying or flying) and key and view(key) != "side":   # (side legs overlap: golden SSJ2 d2 has no line)
        legline = {(x, y) for (x, y) in body if y > waist_y and px[(x, y)] == 81 and (x, y) not in arms | hands
                   and px.get((x - 1, y)) in SUIT - {81} and px.get((x + 1, y)) in SUIT - {81}}
    for p in body - hands:
        v = px[p]
        if p in boots and p not in shin:
            out[p] = BOOT_EDGE if v in (13, 14) else BOOT_FILL
        elif p in hem:                                          # the trouser hem over the shoe
            out[p] = GI_LINE
        elif p in shin:                                         # the armor boot's shaft is trouser leg in the gi
            out[p] = (211 if p in edge or v in (13, 14) else 89 if v in (11, 12, 13, 14) else 88)
        elif p in chest:
            out[p] = (211 if p in edge or p in edged else 89) if v in (13, 14) else 88
        elif v in SUIT | TRIM | {13, 14}:                        # a loose 13/14 is a suit outline
            if p in arms:                                       # an arm on the face gets an outline too
                face = any(q in mask and px.get(q) in SKIN for q in neighbours(p))
                out[p] = 23 if p in edge or face else {77: 114, 79: 115, 80: 116}.get(v, 117)
            else:
                out[p] = (211 if p in edge else 89) if v in (81, 41, 42, 46, 13, 14) else 88
                if p in legline:
                    out[p] = GI_LINE                            # the line between the legs
                if p in torso and p[1] < waist_y and any((p[0] + s, p[1]) in body and (p[0] + s, p[1]) not in torso
                                                         and p[0] + s * 1 not in range(span[0], span[1] + 1)
                                                         for s in (-1, 1)):
                    out[p] = 211                                # the torso's own edge beside an arm
    row = {x for (x, y) in body if y == waist_y and (x, y) not in arms | hands | boots
           and px[(x, y)] in SUIT | TRIM | ARMOR_WHITE}
    sash = []
    if span:                                                    # 10:52 AM: the sash spans the waist, not a leg
        row = {x for x in row if span[0] <= x <= span[1]}
    if row:                                                     # the run under the face middle
        x = min(row, key=lambda x: abs(x - cx))
        sash = sorted(c for c in components({(x, 0) for x in row}) if (x, 0) in c)[0]
        sash = sorted(x for x, _ in sash)
    for x in sash:
        out[(x, waist_y)] = 27 if x in (sash[0], sash[-1]) else 26
    if parts is not None:
        parts.update(boots=boots, chest=chest, hands=hands, arms=arms, waist=waist_y, wrists=wrists, pose=pose,
                     upright=not (lying or flying), torso=torso, span=span, reclaimed=reclaimed, loose=loose)
    notes = [f"hands {len(gloves)}, wristbands {cuffs}"] if gloves else []
    return out, notes

# ===== lit frames (anim 18 charge) =====
# Anim 18 frames 2+ are frame 1's pose lit by the charge glow: lit suit 212-214 and 230, shadow suit 211 and 215,
# lit trim 129 and 131, white plate shaded 11-15. In the head, 211 and 215 are the lit black hair and 16 the nose.
LIT_ANIM, LIT_FROM, LIT_TWIN = 18, 2, 1
LIT_HEAD = {211: 1, 215: 1, 16: 114}

def unlit_probe(px: dict, twin: dict) -> tuple:
    """(probe, head mask) for a lit frame: the head found with lit hair read as hair, and every body pixel given
    the index of the unlit twin frame (same pose) so the part rules see plain armor. The output keeps the lit head."""
    look = {p: LIT_HEAD.get(v, v) for p, v in px.items()}
    mask = head_mask(look)
    twin_head = head_mask(twin)
    pairs = {}
    for p, v in px.items():                                     # lit index -> unlit index, by majority on the body
        if p not in mask and p in twin and p not in twin_head:
            pairs.setdefault(v, []).append(twin[p])
    learned = {v: max(set(u), key=u.count) for v, u in pairs.items()}
    probe = {}
    for p, v in px.items():
        if p in mask:
            probe[p] = look[p]
        elif p in twin and p not in twin_head and twin[p] not in HAIR_BLACK | GOLD | SKIN:
            probe[p] = twin[p]
        else:
            probe[p] = learned.get(v, v) if v not in SKIN | HAIR_BLACK else v
    return probe, mask

# ===== body pass: armor whites, bare chest, V-neck =====

def view(k: Key) -> str:
    """front, side or back. The transform (anim 9) faces front in every dir."""
    return "front" if k[0] == TRANSFORM_ANIM or k[1] == 0 else "back" if k[1] == BACK_DIR else "side"

def light_fails(px: dict, mask: set, keep: set = frozenset(), back: bool = False) -> set:
    """White and light grey pixels (armor colors: collar, shoulder, trim, gloves, boots) in the body. Kept: `keep`
    (effects of the original frame), eye whites and mouths (beside an eye, or face skin below them; not in a
    back view) and hair shine (inside hair)."""
    out = set()
    chin = chin_of(px, mask)
    for p, v in px.items():
        if v not in LIGHT or p in keep:
            continue
        x, y = p
        sides = [any((x + s * d, y) in mask and px.get((x + s * d, y)) in SKIN for d in (1, 2)) for s in (-1, 1)]
        if not back and chin and y <= chin[1] and all(sides):
            continue                                            # mouth or eye between face skin, never below the chin
        if p in mask:
            face = any((x, y + d) in mask and px.get((x, y + d)) in SKIN for d in (1, 2, 3))
            if not back and (face or any(px.get(q) in EYES for q in neighbours(p, diag=True))):
                continue                                        # eye white or mouth
            near = [px.get(q) for q in neighbours(p) if q in mask]
            if any(n in HAIR_BLACK | GOLD for n in near) and sum(n in HAIR_BLACK | GOLD | LIGHT for n in near) >= 2:
                continue                                        # hair shine (also on the hair's rim)
        out.add(p)
    return out

def chest_skin(px: dict, mask: set, keep: set = frozenset(), arms: set = frozenset()) -> set:
    """Bare chest: skin outside the head in the rows under the chin near the face middle, in parts not joined
    to a wristband or to `arms` (an arm, also one across the chest). `keep` (a drawn V) does not count."""
    chin = chin_of(px, mask)
    if not chin:
        return set()
    cx, chin_y = chin
    skin = {p for p, v in px.items() if v in SKIN and p not in mask and p not in keep}
    out = set()
    for comp in components(skin):
        if touching(comp, px) & WRISTBAND or comp & arms:
            continue
        if all(chin_y < y <= chin_y + CHEST_ROWS and abs(x - cx) <= 3 for x, y in comp):
            out |= comp
    return out

def _repaint(px: dict, spots: set) -> None:
    """Each spot takes the most common color round it (gi, skin or outline), from the edges inward."""
    spots = set(spots)
    for _ in range(8):
        done = {}
        for p in spots:
            near = [px[q] for q in neighbours(p, diag=True) if q in px and q not in spots and px[q] not in LIGHT]
            if near:
                done[p] = max(set(near), key=lambda v: (near.count(v), v in GI))
        if not done:
            break
        px.update(done)
        spots -= set(done)
    for p in spots:
        px[p] = 89

def neck_run(px: dict, mask: set) -> tuple:
    """(run, chin row, face middle x): the chin-row run of face skin and its outline nearest the face middle (the
    neck's base). None without a face."""
    chin = chin_of(px, mask)
    if not chin:
        return None
    cx, chin_y = chin
    xs = {x for x, y in mask if y == chin_y and px.get((x, y)) in SKIN | {23}}
    run = next(c for c in components({(x, 0) for x in xs}) if (min(xs, key=lambda x: abs(x - cx)), 0) in c)
    return sorted(x for x, _ in run), chin_y, cx

def facing(px: dict, mask: set, k: Key) -> int:
    """-1 when a side-view head faces left in object space, +1 right. Colored eyes sit in front of the hair mass;
    without them (the black-eyed base head) dir 2 faces left and dir 3 right."""
    eyes = _eyes(px, mask)
    off = eyes[0] - sum(x for x, _ in mask) / max(len(mask), 1) if eyes else 0
    if abs(off) >= 1:
        return -1 if off < 0 else 1
    return -1 if k[1] == 2 else 1

def _draw_spots(px: dict, spots: list) -> bool:
    """Draw (point, skin) spots when they all land on gi purple (or are already drawn)."""
    if all(px.get(q) == v for q, v in spots) or all(px.get(q) in (88, 89) for q, _ in spots):
        px.update(dict(spots))
        return True
    return False

NOT_OPEN = "no: no gi under the chin (arm, pose or effect in the way)"

def _collar_rows(px: dict, chin_y: int) -> list:
    """Rows under the chin where the opening's top row may sit: up to 3, and never at or below the sash (a
    flying frame shows its legs right under the head)."""
    sash = min((y for (_, y), v in px.items() if v in RED and y > chin_y), default=chin_y + 9)
    return [top for top in range(chin_y + 1, chin_y + 4) if top + 1 < sash]

def add_v_neck(px: dict, mask: set) -> str:
    """Open the collar into a narrow V of chest skin, centred on the gi between the collar ends on the first gi
    row under the chin (final, 2026-10-17: the golden fronts, 3 over 1). An even gap leans left, as on the
    goldens. Draws only on gi purple, so an arm across the chest keeps it covered. Returns "yes" or "no: why"."""
    neck = neck_run(px, mask)
    if not neck:
        return "no: no face"
    _, chin_y, cx = neck
    for top in _collar_rows(px, chin_y):
        gi = {(x, 0) for (x, y), v in px.items() if y == top and v in (88, 89) and abs(x - cx) <= 4}
        if not gi:
            continue
        near = min(gi, key=lambda q: abs(q[0] - cx))
        gap = sorted(x for x, _ in next(c for c in components(gi) if near in c))
        mid = (gap[0] + gap[-1]) // 2
        if _draw_spots(px, [((mid + dx, top - 1 + dy), v) for dx, dy, v in V_NECK]):
            return "yes"
    return NOT_OPEN

def add_side_opening(px: dict, mask: set, k: Key) -> str:
    """Side views: the quarter-angle neck opening (final, 2026-10-17, golden side): 2 skin pixels on the first gi
    row under the collar, from the front end of the neck skin backward, and 1 under the front one. Draws only on
    gi purple, so an arm or a pose that covers the chest keeps it covered. Returns "yes" or "no: why"."""
    neck = neck_run(px, mask)
    if not neck:
        return "no: no face"
    run, chin_y, _ = neck
    skin = [x for x in run if px.get((x, chin_y)) in SKIN] or run
    f = facing(px, mask, k)
    front = skin[0] if f < 0 else skin[-1]
    for top in _collar_rows(px, chin_y):
        if _draw_spots(px, [((front - f * dx, top - 1 + dy), v) for dx, dy, v in SIDE_NECK]):
            return "yes"
    return NOT_OPEN

def finish(px: dict, mask: set, k: Key, keep: set = frozenset(), arms: set = frozenset()) -> tuple:
    """Last body pass (final, 2026-10-16): armor whites repainted, bare chest covered with gi, then the front V or
    the side neck opening. `keep` = effect pixels of the original frame. Returns (V status, notes)."""
    notes = []
    fixed = 0
    for _ in range(3):                                          # a repaint can unmask a neighbour's shine test
        hits = light_fails(px, mask, keep, view(k) == "back")
        if not hits:
            break
        _repaint(px, hits)
        fixed += len(hits)
    if fixed:
        notes.append(f"{fixed} armor white pixels repainted")
    bare = chest_skin(px, mask, arms=arms)
    if bare:
        for p in bare:
            near = [px.get(q) for q in neighbours(p, diag=True)]
            px[p] = 88 if near.count(88) > near.count(89) else 89
        notes.append(f"{len(bare)} chest skin pixels covered with gi")
    rim = {p for p, v in px.items() if v in (88, 89) and p not in mask
           and any(q in arms and px.get(q) in SKIN for q in neighbours(p))}
    for p in rim:                                               # a dark line parts the bare arm from the gi
        px[p] = 211
    side = view(k)
    if side == "back":
        return f"n.a. ({side})", notes
    return (add_v_neck(px, mask) if side == "front" else add_side_opening(px, mask, k)), notes

# ===== golden rules: shoes, shading, torso, step light (mine, 2026-10-17/18, the 12 golden frames) =====
# They run on every frame after the conversion and never change `fixed` (head, effects, sparks). "Left" is the
# image's left (`lean` = its direction in object space), so a mirrored dir shows the light mirrored, as golden d3.
GOLDEN = ART / "golden"
SHOE_ROWS = 2                                              # a gi shoe is the bottom 2 rows of a boot (set 104)
SOLE_TILT = 1.5                                            # a lying boot points sideways only when clearly so
GI_FILL = {88, 89}
GI_LIT, GI_BASE, GI_LINE = 88, 89, 211
STEP_FRAMES = (1, 2, 3)                                    # anim 9 frames the armor lights with 77 highlights
STEP_LIGHT = {88: 87, 89: 88}                              # one step brighter: lit 88, and 89 beside a lit pixel
TORSO_MARGIN = 2                                           # columns past the golden gi kept with the torso
LOOSE = {v: 79 for v in SUIT}                              # suit shades read as one when torsos are compared
IDLE_GOLDEN = ("gi_base", "gi_ssj")                        # gi_ssj2: finish_v2.py places it (transplant.py reads ours)
OWNER_FRAMES = {"gi_base": {(1, 0, i): f"golden_gi_base_a1_d0_i{i}.png" for i in range(4)}}   # 9:48 AM walk
GOLDEN_CHECKS = {"sleeve", "lost"}                         # checks that read the converter's arms and silhouette
GOLDEN_EXCEPTION = "golden pixels: the owner's torso and straps replace the converter's arm and outline guesses"
HAND_EXCEPTION = "hand frame: the reviewed r12fix frame replaces the converter's; the checks read the armor parts"

def _row_runs(cells: set) -> list:
    """(row, xs) for each horizontal run of 4-joined cells, xs ascending."""
    rows, out = {}, []
    for x, y in cells:
        rows.setdefault(y, []).append(x)
    for y, xs in rows.items():
        xs.sort()
        start = 0
        for i in range(1, len(xs) + 1):
            if i == len(xs) or xs[i] != xs[i - 1] + 1:
                out.append((y, xs[start:i]))
                start = i
    return out

# Why: the armor's tall boots read as Piccolo's small shoes (set 104) on every golden (rule 1).
def shoes(px: dict, fixed: set, hip: tuple = None) -> int:
    """Each boot (4-joined 34/35 part) keeps its SHOE_ROWS rows nearest the sole; on the row above, a pixel under
    trouser becomes the hem (211) and a toe sticking out stays shoe; higher rows become trouser (89, 211 at the
    row ends). Upright frames (no `hip`): the sole is down. Lying and flying frames: the sole points from the hip
    to the boot (the main axis), and each line along it keeps its own SHOE_ROWS, since one part may hold both
    feet. Upright parts are split into feet first (feet(): a raised back foot has its own sole, and keeps 1 shoe
    row, as on the golden sides and my walk). Returns the pixels changed."""
    n = 0
    shoe_px = {p for p, v in px.items() if v in (BOOT_EDGE, BOOT_FILL) and p not in fixed}
    parts = components(shoe_px)
    if not hip:                                                 # upright: each foot keeps its own sole
        parts = [f for c in parts for f in feet(c, {p for p in c if px[p] == BOOT_EDGE})]
    ups = raised_feet(shoe_px, parts) if not hip else [False] * len(parts)
    plan = []
    for i, (part, up) in enumerate(zip(parts, ups)):
        rows = 1 if up else SHOE_ROWS                           # a raised back foot shows one shoe row
        sx, sy = 0, 1
        if hip:
            vx = sum(x for x, _ in part) / len(part) - hip[0]
            vy = sum(y for _, y in part) / len(part) - hip[1]
            sx, sy = ((vx > 0) - (vx < 0), 0) if abs(vx) > SOLE_TILT * abs(vy) else (0, (vy > 0) - (vy < 0) or 1)
        depth = {p: p[0] * sx + p[1] * sy for p in part}
        line = {p: (p[0] * sy - p[1] * sx) if hip else 0 for p in part}
        sole = {}
        for p in part:
            sole[line[p]] = max(sole.get(line[p], depth[p]), depth[p])
        plan += [((i if hip else 0, depth[p]), p, part, depth, sole[line[p]] - rows, sx, sy) for p in part]
    # Knee first: the hem test reads the trouser above, so upright feet run by row across all feet (a toe beside
    # another foot's shoe must see that shoe's hem already painted, or a second run changes it).
    for _, p, part, depth, hem, sx, sy in sorted(plan, key=lambda e: e[0]):
        if depth[p] < hem:
            across = [q[0] * sy - q[1] * sx for q in part if depth[q] == depth[p]]
            px[p] = GI_LINE if p[0] * sy - p[1] * sx in (min(across), max(across)) else GI_BASE
        elif depth[p] == hem and px.get((p[0] - sx, p[1] - sy)) in GI:
            px[p] = GI_LINE
        else:
            continue
        n += 1
    return n

# Why: lying and flying feet do not point down, so the sole is found from the sash.
def hip_of(px: dict, mask: set, parts: dict) -> tuple:
    """The sash middle (else the body middle) of a lying or flying frame; None for an upright one."""
    if parts.get("upright"):
        return None
    pts = [p for p, v in px.items() if v in RED] or [p for p in px if p not in mask and px[p] in GI]
    return (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts)) if pts else None

# Why: Piccolo's deep fold between the legs, kept on every golden (rule 2).
def gap_folds(px: dict, fixed: set, waist_y: int) -> int:
    """A gi pixel under the sash on the row above a gap between the legs becomes 211 (the deep fold, set 104
    row 22). The gap has leg (gi or shoe) on both sides of its row. Returns the pixels changed."""
    legs = GI | {BOOT_EDGE, BOOT_FILL}

    def side(x, y, s):
        return next((px[(x + s * d, y)] for d in range(1, 9) if (x + s * d, y) in px), None)

    hits = [(x, y) for (x, y), v in px.items() if v in GI_FILL and (x, y) not in fixed and y > waist_y
            and (x, y + 1) not in px and side(x, y + 1, -1) in legs and side(x, y + 1, 1) in legs]
    px.update({p: GI_LINE for p in hits})
    return len(hits)

# Why: rule C, Piccolo's run shading, as I approved it on the goldens (rule 2).
def shade(px: dict, fixed: set, lean: int) -> int:
    """Rule C (Piccolo, set 104): per horizontal run of gi (88, 89) all base 89, lit 88 at n = 2 the left pixel,
    n = 3-4 the left-centre one, n >= 5 the centre one on even rows and the n - 2 middle ones on odd rows (object
    rows, so the folds hold still while an animation moves by odd dy). Returns the pixels changed."""
    n = 0
    for y, xs in _row_runs({p for p, v in px.items() if v in GI_FILL and p not in fixed}):
        run = xs if lean < 0 else xs[::-1]                     # run[0] is the image-left pixel
        size = len(run)
        lit = ({0} if size == 2 else {(size - 1) // 2} if size in (3, 4)
               else ({size // 2} if y % 2 == 0 else set(range(1, size - 1))) if size >= 5 else set())
        for i, x in enumerate(run):
            want = GI_LIT if i in lit else GI_BASE
            n += px[(x, y)] != want
            px[(x, y)] = want
    return n

# Why: the golden fronts draw 211 lines beside and under the V tip (rule 3).
def v_lines(px: dict, fixed: set) -> int:
    """Front V (116 115 116 over 116): the gi beside its tip and the gi under it become 211, as on the golden
    fronts. Returns the pixels changed."""
    tips = [(x, y + 1) for (x, y), v in px.items() if v == 115 and (x, y) not in fixed
            and px.get((x - 1, y)) == px.get((x + 1, y)) == px.get((x, y + 1)) == 116]
    hits = {q for x, y in tips for q in ((x - 1, y), (x + 1, y), (x, y + 1)) if px.get(q) in GI_FILL}
    px.update({q: GI_LINE for q in hits})
    return len(hits)

# Why: the golden fronts and backs carry the gi strap over both shoulders and give the arm its own outline.
def straps(px: dict, mask: set, fixed: set, k: Key, lean: int) -> int:
    """Strap edge 211 and strap 89 over each shoulder at the top gi row by the neck (front: top on the chin row;
    back: down over the shoulder); only when both shoulders show. Under the strap, arm skin touching the torso
    outline becomes 23; in front only on the image-left side, where the outline turns gi (rounder chest)."""
    chin = chin_of(px, mask)
    body = {p for p, v in px.items() if v in GI and p not in fixed}
    if not chin or not body or view(k) == "side":
        return 0
    top = min(y for _, y in body)
    row = sorted(x for x, y in body if y == top)
    if not -1 <= top - chin[1] <= 2 or abs((row[0] + row[-1]) / 2 - chin[0]) > 3:
        return 0                                                # the gi top is not a pair of shoulders by the neck
    front, plan = view(k) == "front", []
    for end, s in ((row[0], -1), (row[-1], 1)):
        o, above = end + s, px.get((end + s, top - 1))          # skin above only on the row under the chin
        if front and px.get((o, top)) in SKIN and (above == 23 or above in SKIN and top - chin[1] <= 1):
            plan.append((end, s, {(o, top - 1): GI_LINE, (o, top): GI_LINE, (end, top): GI_BASE}, top + 1))
        elif not front and px.get((o, top)) == 23 and px.get((o, top + 1)) in SKIN:
            spots = {(o, top): GI_LINE, (o, top + 1): GI_LINE, (end, top): GI_BASE}
            if px.get((end - s, top)) in GI_FILL:
                spots[(end - s, top)] = GI_LINE
            if px.get((end, top + 1)) == GI_LINE:
                spots[(end, top + 1)] = GI_LIT
            plan.append((end, s, spots, top + 2))
    if len(plan) < 2:
        return 0                                                # one shoulder only: an arm across the chest
    before = dict(px)
    for end, s, spots, arm_y in plan:
        px.update(spots)
        if front and s != lean:
            continue
        torso = [x for (x, y), v in px.items() if y == arm_y and v in GI and (x, y) not in fixed]
        if not torso:
            continue
        edge = min(torso) if s < 0 else max(torso)
        arm = all(px.get((edge + s * d, arm_y)) in SKIN for d in (1, 2)) and (edge + s, arm_y) not in fixed
        if px[(edge, arm_y)] == GI_LINE and arm:
            px[(edge + s, arm_y)] = 23
            if front:
                px[(edge, arm_y)] = GI_BASE
    return sum(px.get(p) != v for p, v in before.items())

# Why: where the armor torso is the idle one, my drawn torso is the answer (rule 3).
def golden_torso(name: str, rec: dict, d: int) -> tuple:
    """(golden pixels, idle armor pixels, window) of a form's dir in the idle frame's object space. The window is
    the golden torso: from the row above its first gi fill row to the row under the sash, TORSO_MARGIN columns
    past its gi, outline and sash on each row."""
    gold = image_pixels(Image.open(GOLDEN / f"golden_{name}_d{d}.png"), rec)
    idle = frame_pixels(rec)
    sash = max({y for (_, y), v in gold.items() if v in RED}, key=lambda r: sum(
        1 for (_, y), v in gold.items() if y == r and v in RED))
    first = min(y for (_, y), v in gold.items() if v in GI_FILL)
    window = set()
    for y in range(first - 1, sash + 2):
        xs = [x for (x, r), v in gold.items() if r == max(y, first) and v in GI | RED]
        window |= {(x, y) for x in range(min(xs) - TORSO_MARGIN, max(xs) + TORSO_MARGIN + 1)}
    return gold, idle, window

# Why: the golden torso may go only on a torso of the same geometry as the idle frame.
def torso_shift(orig: dict, idle: dict, window: set) -> tuple:
    """(dx, dy) at which the frame's armor equals the idle armor over the torso window (suit shades as one),
    nearest first; None when no shift within 2 pixels fits."""
    want = {p: LOOSE.get(idle.get(p), idle.get(p)) for p in window}
    for sx, sy in sorted(((a, b) for a in range(-2, 3) for b in range(-2, 3)), key=lambda s: abs(s[0]) + abs(s[1])):
        if all(LOOSE.get(orig.get((x + sx, y + sy)), orig.get((x + sx, y + sy))) == v for (x, y), v in want.items()):
            return sx, sy
    return None

# Why: a strap on some frames of an animation only would blink on and off as it plays. A frame that takes the
# golden torso carries the golden strap, so it never blocks its group (final, 2026-10-18, 157 a4: per frame).
def strap_groups(staged: list, torsos: dict) -> set:
    """(anim, dir) groups where the strap rule fits every upright frame without the golden torso (tried on copies
    of the converted frames). `staged` rows hold (header, keys, record, ..., pixels, keep, ...) as make_gi_set
    stages them; `torsos` is {dir: golden_torso(...)}."""
    fits = {}
    for _, keys, rec, _, _, _, _, parts, orig, mask, px, keep, _, _ in staged:
        upright = bool(parts.get("upright"))
        if upright and torso_shift(orig, *torsos[keys[0][1]][1:]) is not None:
            continue                                            # golden torso: its strap is mine
        ok = upright and straps(dict(px), mask, mask | keep, keys[0], 1 if rec["attr1"] & HFLIP else -1) > 0
        for o in keys:
            fits.setdefault(o[:2], []).append(ok)
    return {g for g, ok in fits.items() if all(ok)}

def gi_rules(px: dict, mask: set, fixed: set, k: Key, parts: dict, lean: int, torso: tuple, orig: dict,
             strap: bool = True) -> list:
    """The golden rules on one converted frame, in order: shoes, gap folds, shading, then the torso (the golden's
    own pixels where the armor torso equals the idle one, else the V lines and straps), then the step light.
    Returns notes naming each rule that changed pixels."""
    notes, upright = [], parts.get("upright", False)
    hip = hip_of(px, mask, parts)
    feet_done = upright and view(k) != "side"                  # front and back feet: armor_to_gi
    counts = {"shoes along the legs" if hip else "shoes": 0 if feet_done else shoes(px, fixed, hip),
              "gap folds": gap_folds(px, fixed, parts["waist"]) if upright else 0,
              "shading": shade(px, fixed, lean)}
    shift = torso_shift(orig, torso[1], torso[2]) if torso and upright else None
    if shift is None:
        counts["v lines"] = v_lines(px, fixed) if view(k) == "front" else 0
        counts["straps"] = straps(px, mask, fixed, k, lean) if upright and strap else 0
    else:
        gold, _, window = torso
        chin = chin_of(orig, mask)
        limbs = {q for q in parts.get("arms", set()) | parts.get("hands", set())
                 if chin and q[1] > chin[1] + STRAP_ROWS}
        before = {(x + shift[0], y + shift[1]): px.get((x + shift[0], y + shift[1])) for x, y in window}
        for (x, y) in window:
            q = (x + shift[0], y + shift[1])
            if q in limbs and gold.get((x, y)) not in PART_COLORS["arm"]:
                continue                                        # 11:03 AM: gi never covers an arm
            if (x, y) in gold:
                px[q] = gold[(x, y)]
            else:
                px.pop(q, None)
        counts[f"golden torso (shift {shift[0]},{shift[1]})"] = sum(px.get(q) != v for q, v in before.items())
    if k[0] == TRANSFORM_ANIM and k[2] in STEP_FRAMES:          # 10:45 PM: the step lights the gi up
        lit = {p for p, v in px.items() if v == GI_LIT and p not in fixed}
        near = {(x, y) for (x, y), v in px.items() if v == GI_BASE and (x, y) not in fixed
                and ((x - 1, y) in lit or (x + 1, y) in lit)}
        px.update({p: STEP_LIGHT[px[p]] for p in lit | near})
        counts["step light"] = len(lit | near)
    notes += [f"rule {r}: {n} px" for r, n in counts.items() if n]
    return notes

# ===== Super Saiyan 2 keys that set 58 lacks =====

def _fill(px: dict, holes: set) -> dict:
    """Holes the old head left: gi, sash or skin when the row has it on both sides, else cleared."""
    out = {p: v for p, v in px.items() if p not in holes}
    holes = set(holes)
    for _ in range(8):
        done = {}
        for q in holes:
            sides = []
            for s in (-1, 1):
                for d in (1, 2, 3):
                    v = out.get((q[0] + s * d, q[1]))
                    if v in GI | RED | SKIN:
                        sides.append(v)
                        break
            if len(sides) == 2:
                done[q] = 26 if any(v in RED for v in sides) else 116 if all(v in SKIN for v in sides) else 89
        if not done:
            break
        out.update(done)
        holes -= set(done)
    return out

def _eyes(px: dict, mask: set):
    """Centre of the eye pixels of a head, or None with fewer than 2."""
    e = [p for p in mask if px.get(p) in EYES]
    return (sum(x for x, _ in e) / len(e), sum(y for _, y in e) / len(e)) if len(e) >= 2 else None

REVERT_ANIM = 21
# Set 59 21.x.0 -> 21.x.1 darkens the hair one step (traced at the same pixels): yellows -> 120, 120 -> 20, 20 -> 23.
REVERT_DIM = {2: 120, 9: 120, 36: 120, 37: 120, 44: 120, 45: 120, 46: 120, 120: 20, 121: 20, 38: 20, 39: 20,
              18: 23, 19: 23, 20: 23, 21: 23, 22: 23}
_HEAD_PICK = {}                                                 # (anim, dir) -> the set 58 key whose head it wears
HEAD_TURN = {(12, 2): 1}                                        # (anim, dir): turn the head 90 degrees (lying side view)
HEAD_NUDGE = {(20, 0): (0, -2)}                                 # (anim, dir): (dx, dy) after the eye match
ARMS_UP_ANIM = 11

def stand_in_head(body: dict, body_head: set, ref: dict, hair: dict, k: Key, orig: dict,
                  squeeze: tuple = (0, 0, 0)) -> tuple:
    """A set 58 head on a set 59 body for a key set 58 lacks: the head of the set 58 frame (same dir) whose set
    59 twin wears the head most like this frame's. Only the head rows change; arms in front of the hair and an
    aura ring stay. A black-haired head (the revert ends in base form) stays. `squeeze` = (top rows, left
    columns, right columns) the hair loses between its tip and the eyes, so the frame fits the slot (Ruling 35).
    Returns (pixels, head mask, note, new head?)."""
    chin = chin_of(orig, body_head)
    if sum(orig[p] in HAIR_BLACK for p in body_head) > sum(orig[p] in GOLD for p in body_head):
        return body, body_head, f"set 58 has no {key_str(k)}: base head kept (the revert ends in base form)", False
    rows = {p for p in body_head if p[1] <= chin[1]}
    armor = {p for p, v in orig.items() if v in SUIT | ARMOR_WHITE}
    front = set().union(set(), *(c for c in components(armor, diag=True) if any(orig[p] in SUIT for p in c)))
    fists = [c for c in components({p for p in armor - body_head if orig[p] in ARMOR_WHITE}, diag=True)
             if len(c) >= 4 and min(y for _, y in c) <= chin[1]]
    front |= set().union(set(), *fists)                         # a fist raised by the head stays in front of the hair
    front -= body_head                                          # eye whites beside a sleeve are face, not armor
    ring = {p for p, v in orig.items() if v in GOLD and any(q not in orig for q in neighbours(p, True))}
    aura = [orig[p] for p in ring if p[1] > chin[1]]
    aura = max(set(aura), key=aura.count) if len(aura) >= 20 else None
    cands = [c for c in hair if c in ref and c[1] == k[1]]
    c = _HEAD_PICK.get(k[:2]) or max(cands, key=lambda c: head_score(frame_pixels(ref[c]), body))
    _HEAD_PICK[k[:2]] = c                                       # one head per (anim, dir): no flicker
    src, twin = frame_pixels(hair[c]), frame_pixels(ref[c])
    sx, sy = mask_shift(head_mask(twin), body_head)
    bx, by = best_shift(twin, src)
    eyes_a, eyes_b = _eyes(orig, body_head), _eyes(src, head_mask(src))
    if eyes_a and eyes_b:                                       # the eyes fix the face; shapes only guess it
        sx, sy, bx, by = round(eyes_a[0] - eyes_b[0]), round(eyes_a[1] - eyes_b[1]), 0, 0
    turn = HEAD_TURN.get(k[:2])
    if turn:                                                    # a lying body: the upright head turned to lie with it
        src = {(y, -x): src[(x, y)] for (x, y) in head_mask(src)}  # the head only: the ground shadow is black too
        eyes_b = _eyes(src, head_mask(src))
        sx, sy = round(eyes_a[0] - eyes_b[0]), round(eyes_a[1] - eyes_b[1])
    nx, ny = HEAD_NUDGE.get(k[:2], (0, 0))
    sx, sy = sx + nx, sy + ny
    head_px = {p: src[p] for p in head_mask(src)}
    if k[0] == ARMS_UP_ANIM and fists and eyes_b:                # arms up: the taller hair loses rows mid-height
        top = min(y for _, y in head_px)                        # so its spikes end 1 px above the fists
        need = min(y for c in fists for _, y in c) - 1 - (top + sy - by)
        if need > 0:
            cut = (top + round(eyes_b[1])) // 2 - need // 2
            head_px = {(x, y + need if y < cut else y): v for (x, y), v in head_px.items()
                       if not cut <= y < cut + need}
    head_px = _squeeze(head_px, squeeze, eyes_b)
    new = {(x + sx - bx, y + sy - by): v for (x, y), v in head_px.items()}
    new = {p: v for p, v in new.items() if p not in front and (p in rows or p not in body)}
    holes = rows - set(new) - front
    out = {p: v for p, v in body.items() if p not in holes}
    out.update(new)
    if turn:                                                    # the turned head's neck cut gets the skin outline
        rim = {q for p, v in new.items() if v in SKIN | EYES | LIGHT for q in neighbours(p) if q not in out}
        out.update({q: 23 for q in rim})
        holes -= rim
    if (nx, ny) != (0, 0):                                      # the head moved up: the gap under the chin is torso
        face = [p for p, v in new.items() if v in SKIN]
        nchin, ncx = max(y for _, y in face), sum(x for x, _ in face) / len(face)
        torso = {q for q in holes if q[1] > nchin}
        for q in torso:
            rim = any(n not in out and n not in torso for n in neighbours(q))
            out[q] = 116 if q[1] == nchin + 1 and abs(q[0] - ncx) <= 1 else 211 if rim else 88
        holes -= torso
    for p in front:                                             # an arm or fist over the hair gets a dark rim
        if out.get(p) == 23 and any(out.get(q) in GOLD and q in new for q in neighbours(p)):
            out[p] = 113
    for _ in range(4):                                          # a gap inside the new head takes its neighbours' color
        inner = {}
        for q in holes:
            near = [out[n] for n in neighbours(q, True) if n in out]
            if len(near) >= 6:
                inner[q] = max(set(near), key=near.count)
        out.update(inner)
        holes -= set(inner)
    out = _fill(out, holes)                                     # the rest: gi, sash or skin between body pixels
    head = set(new)
    note = f"set 58 has no {key_str(k)}: set 59 body with the set 58 head of {key_str(c)}"
    if k[0] == REVERT_ANIM and k[2] == 1:                       # the revert's fading frame: hair one step darker
        out.update({p: REVERT_DIM[v] for p, v in new.items() if v in REVERT_DIM and p in out})
        note += ", hair dimmed like set 59 21.x.1"
    if aura is not None:                                        # redraw the aura ring round the new head
        edge = {q for p in out if p[1] <= chin[1] + 1 for q in neighbours(p, True) if q not in out and q[1] <= chin[1] + 1}
        out.update({q: aura for q in edge})
        head |= edge
        note += f", aura ring {aura} redrawn"
    return out, head, note, True

def _drop_lines(lo: int, hi: int, n: int) -> list:
    """n lines spread evenly over lo..hi (the hair between its tip and the eyes)."""
    span = hi - lo + 1
    n = min(n, max(span, 0))
    return sorted({lo + (2 * i + 1) * span // (2 * n) for i in range(n)}) if n else []

def _squeeze(head: dict, squeeze: tuple, eyes) -> dict:
    """Shrink the hair toward the face: drop `top` rows, `left` or `right` columns spread evenly between the hair
    tip and 2 px short of the eyes (the head centre in a back view), so the spikes keep their shape."""
    top, left, right = squeeze
    if not head or not any(squeeze):
        return head
    xs, ys = [x for x, _ in head], [y for _, y in head]
    ex, ey = (round(eyes[0]), round(eyes[1])) if eyes else ((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)
    if top > 0:
        drop = _drop_lines(min(ys) + 1, ey - 2, top)
        head = {(x, y + sum(d > y for d in drop)): v for (x, y), v in head.items() if y not in drop}
    if left > 0:
        drop = _drop_lines(min(x for x, _ in head) + 1, ex - 2, left)
        head = {(x + sum(d > x for d in drop), y): v for (x, y), v in head.items() if x not in drop}
    if right > 0:
        drop = _drop_lines(ex + 2, max(x for x, _ in head) - 1, right)
        head = {(x - sum(d < x for d in drop), y): v for (x, y), v in head.items() if x not in drop}
    return head

def slot_window(rec: dict) -> tuple:
    """(x0, y0, x1, y1): the SLOT_SIDE box that keeps the record's centre column and bottom row."""
    w, h = max(rec["w"], SLOT_SIDE), max(rec["h"], SLOT_SIDE)
    x0 = rec["dx"] - (w - rec["w"]) // 2
    y1 = rec["dy"] + rec["h"] - 1
    return x0, y1 - h + 1, x0 + w - 1, y1

def slot_overflow(rec: dict, px: dict, pad: set) -> tuple:
    """(top, left, right) pixels by which px (and pad, kept 1 px off the edge) leave the slot window."""
    x0, y0, x1, y1 = slot_window(rec)
    pad = pad or set(px)
    top = max(0, y0 - min(y for _, y in px), y0 + 1 - min(y for _, y in pad))
    left = max(0, x0 - min(x for x, _ in px), x0 + 1 - min(x for x, _ in pad))
    right = max(0, max(x for x, _ in px) - x1, max(x for x, _ in pad) - (x1 - 1))
    return top, left, right

def fit_record(rec: dict, px: dict, pad: set = frozenset()) -> dict:
    """The record itself when px fits in it, else the smallest legal OBJ size that holds px, the anchor kept.
    `pad` pixels (a stand-in head's hair) also keep 1 px off the record edge."""
    room = {(x + dx, y + dy) for x, y in pad for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    xs, ys = [x for x, _ in px] + [x for x, _ in room], [y for _, y in px] + [y for _, y in room]
    if rec["dx"] <= min(xs) and max(xs) < rec["dx"] + rec["w"] and rec["dy"] <= min(ys) and max(ys) < rec["dy"] + rec["h"]:
        return rec
    x0, y0 = min(xs + [rec["dx"]]), min(ys + [rec["dy"]])
    x1, y1 = max(xs + [rec["dx"] + rec["w"] - 1]), max(ys + [rec["dy"] + rec["h"] - 1])
    w, h = min((s for s in OBJ_SHAPES if s[0] >= x1 - x0 + 1 and s[1] >= y1 - y0 + 1), key=lambda s: s[0] * s[1])
    shape, size = OBJ_SHAPES[(w, h)]
    return {**rec, "w": w, "h": h, "dx": x0 - (w - (x1 - x0 + 1)) // 2, "dy": y1 - h + 1,
            "attr0": (rec["attr0"] & 0x3FFF) | shape << 14, "attr1": (rec["attr1"] & 0x3FFF) | size << 14,
            "enlarged": True}

# ===== one gi body for Super Saiyan and Super Saiyan 2, stray pinks (final, 2026-10-18 8:53 AM) =====
# Why: the armor bodies of sets 58 and 59 match in most poses, but each form ran the converter on its own, so the
# gi bodies differed. Where the armor matches below the chin, SSJ2 takes the finished gi_ssj body; only the head
# (gi_ssj2's head mask) and the SSJ2 sparks stay its own. Where the armor differs (power-pose idle, ki charge),
# SSJ2 keeps its own body. Head boundary: the chin row (chin_of on head_mask); the body is every row under the
# lower chin of the two armor frames.

def armor_body_diff(own: dict, other: dict) -> int:
    """Pixels where two armor frames (records, object space) differ on the rows under the lower of their chins.
    0 means one body; a missing own frame (set 58 lacks the key) is 0, since gi_ssj2 then uses the other's body."""
    if own is None:
        return 0
    a, b = frame_pixels(own), frame_pixels(other)
    chins = [chin_of(px, head_mask(px)) for px in (a, b)]
    row = max(c[1] for c in chins) if all(chins) else min(y for _, y in set(a) | set(b)) - 1
    return sum(a.get(p) != b.get(p) for p in set(a) | set(b) if p[1] > row)

def shared_body(px: dict, top: set, body: dict, body_head: set) -> dict:
    """SSJ2 frame on the gi_ssj body: gi_ssj pixels outside its head, gi_ssj2 pixels where gi_ssj had its head
    (no SSJ hair left behind), and gi_ssj2's head and sparks (`top`) over all."""
    out = {p: v for p, v in body.items() if p not in body_head}
    out.update({p: px[p] for p in body_head | top if p in px})
    for p in top - set(px):                                     # transparent inside the SSJ2 head stays transparent
        out.pop(p, None)
    return out

def object_mask(rec: dict, field: str = "head") -> set:
    """A gi folder record's (by_key) head or arm mask in object space, through that key's own record."""
    flip = rec["attr1"] & HFLIP
    return {(rec["dx"] + (rec["w"] - 1 - x if flip else x), rec["dy"] + y) for x, y in rec[field]}

PINK = {239, 240}                                            # Rage set 58 strays (248,32,224), (248,32,248)

def stray_pinks(px: dict) -> int:
    """A pink pixel outside the outline (4-joined to the transparent area flooded from the frame border) is
    cleared; one inside takes its most common non-zero 4-neighbour index (ties: the lower index). Returns the
    pixels changed."""
    spots = [p for p, v in px.items() if v in PINK]
    if not spots:
        return 0
    xs, ys = [x for x, _ in px], [y for _, y in px]
    box = (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)
    outside, todo = set(), [(box[0], box[1])]
    while todo:                                                 # transparent pixels joined to the border
        p = todo.pop()
        if p in outside or p in px or not (box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]):
            continue
        outside.add(p)
        todo += list(neighbours(p))
    for p in spots:
        near = [px[q] for q in neighbours(p) if px.get(q, 0) and px[q] not in PINK]
        if any(q in outside for q in neighbours(p)) or not near:
            del px[p]
        else:
            px[p] = max(set(near), key=lambda v: (near.count(v), -v))
    return len(spots)

# ===== per-frame checks =====

def purple_arms(px: dict, arms: set) -> set:
    """Arm pixels (shoulder to wristband, found by armor_to_gi) drawn in gi purple."""
    return {p for p in arms if px.get(p) in (88, 89)}

def purple_forearms(px: dict, wrists: list, orig: dict, torso: set = frozenset()) -> list:
    """Wristbands whose forearm shows gi purple: the gi is sleeveless (final, 2026-10-17). The forearm is the
    armor sleeve (suit blue in `orig`) one step from the band toward the shoulder; purple with no skin there
    fails (a band wider than the arm may touch the torso). `wrists` = (cuff, shoulder
    point, glove) from armor_to_gi. A step onto `torso` (torso_split) does not count: a fist held at the torso's
    edge hides its forearm there (my walk 1.0.0). Returns the failing cuffs."""
    bad = []
    for cuff, (sx, sy), glove in wrists:
        gx, gy = sum(x for x, _ in glove) / len(glove), sum(y for _, y in glove) / len(glove)
        step = ((sx > gx) - (sx < gx), 0) if abs(sx - gx) > abs(sy - gy) else (0, (sy > gy) - (sy < gy))
        side = {(x + step[0], y + step[1]) for x, y in cuff} - glove
        side = {q for q in side if q in px and orig.get(q) in SUIT and q not in torso}
        if any(px[q] in (88, 89) for q in side) and not any(px[q] in SKIN for q in side):
            bad.append(cuff)
    return bad

def silhouette_iou(a: dict, b: dict) -> float:
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)

def edge_hair(px: dict, mask: set, rec: dict) -> set:
    """Hair pixels on the record's edge."""
    x0, y0, x1, y1 = rec["dx"], rec["dy"], rec["dx"] + rec["w"] - 1, rec["dy"] + rec["h"] - 1
    return {(x, y) for (x, y) in mask if px.get((x, y)) in HAIR_BLACK | GOLD and (x in (x0, x1) or y in (y0, y1))}

def dark_brows(px: dict, mask: set) -> int:
    """Black or dark grey pixels in the head that touch face skin (eyebrows, pupils of black-haired heads)."""
    return sum(1 for p in mask if px.get(p) in HAIR_BLACK and any(px.get(q) in SKIN for q in neighbours(p, True)))

def chest(px: dict, mask: set, k: Key, arms: set = frozenset()) -> tuple:
    """(bare chest skin, gi in the chest box, ok): ok is None with neither, else the skin fits the view's opening
    (V_LIMIT) and the gi covers more than twice the skin."""
    skin = len(chest_skin(px, mask, arms=arms))
    chin = chin_of(px, mask)
    box = [p for p in px if p not in mask and chin and chin[1] < p[1] <= chin[1] + CHEST_ROWS and abs(p[0] - chin[0]) <= 3]
    gi = sum(1 for p in box if px[p] in GI)                   # the dark line beside a bare arm is gi too
    return skin, gi, None if skin == gi == 0 else skin <= V_LIMIT[view(k)] and gi > 2 * skin

# Why (me, 10:55 AM): every check before tested the rules, never whether each body part became the right
# thing, so a forearm painted gi passed. check_parts maps the armor by shape (the classifier of armor_to_gi) and
# asks each part for its gi class. A pixel on a part border may take the class of the part it borders (outlines
# belong to either side), shoulder rows may carry the strap, and the front V may open the chest.
PART_COLORS = {"arm": SKIN | {23} | WRISTBAND, "glove": SKIN | {23} | WRISTBAND,
               "torso": GI | {87}, "leg": GI | {87}, "boot": GI | {87, BOOT_EDGE, BOOT_FILL}}
STRAP_ROWS = 2                                             # rows under the chin where the strap covers the shoulder

def part_map(orig: dict, mask: set, parts: dict, keep: set) -> dict:
    """{pixel: class} of an armor frame: head, effect, shadow, glove, boot, arm, torso (chest plate and the
    torso_split torso, or any suit above the sash when no split ran) and leg (suit at or below the sash)."""
    out = {}
    waist = parts.get("waist", 0)
    for p, v in orig.items():
        if p in mask:
            out[p] = "head"
        elif p in keep or p in parts.get("loose", set()):
            out[p] = "effect"
        elif v == SHADOW:
            out[p] = "shadow"
        elif p in parts.get("hands", set()):
            out[p] = "glove"
        elif p in parts.get("boots", set()):
            out[p] = "boot"
        elif p in parts.get("arms", set()):
            out[p] = "arm"
        elif p in parts.get("chest", set()) or p in parts.get("torso", set()) or p[1] < waist:
            out[p] = "torso"
        else:
            out[p] = "leg" if parts.get("upright") else "torso"
    return out

def check_parts(px: dict, orig: dict, mask: set, parts: dict, keep: set, k: Key, where: list = None) -> dict:
    """{class: pixels whose gi color does not fit their armor part} for one frame (object space). Effects and the
    shadow must be unchanged (a blue spark is allowed), the sash (red) may lie only on the waist rows of the torso
    and within the torso_split columns, and every foot must show a shoe pixel. `where` collects (pixel, class,
    armor index, gi index) of each misfit."""
    pm = part_map(orig, mask, parts, keep)
    chin = chin_of(orig, mask)
    span, waist = parts.get("span"), parts.get("waist", 0)
    bad = {}
    for p, cls in pm.items():
        v = px.get(p, 0)
        if cls == "head":
            continue
        near = {pm.get(q) for q in neighbours(p, diag=True)}
        if cls in ("effect", "shadow"):
            ok = v in (orig[p], SPARK_BLUE, 2) or cls == "shadow" and (v == 0 or "boot" in near and v in (34, 35))
        elif orig[p] not in SUIT | TRIM | ARMOR_WHITE and v == orig[p]:
            ok = True                                           # hair or skin the head mask left out, unchanged
        elif v in RED:
            ok = cls in ("torso", "leg") or not span and cls == "arm"   # side: the sash runs on behind the arm
            ok = ok and abs(p[1] - waist) <= 1 and (not span or span[0] <= p[0] <= span[1])
        else:
            allowed = set(PART_COLORS[cls])
            for c in near:                                      # a border pixel may take its neighbour's class
                allowed |= PART_COLORS.get(c, set())
            if cls in ("torso", "leg"):
                allowed -= SKIN                                 # the arm line may lie on the torso, skin fill never
            if chin and p[1] <= chin[1] + STRAP_ROWS:
                allowed |= GI | {23, 0} | (set() if cls == "torso" else SKIN)   # the strap, the neck line, a trim
            if cls == "torso" and chin and p[1] <= chin[1] + 3 and abs(p[0] - chin[0]) <= 3:
                allowed |= SKIN                                 # the front V or the side neck opening
            if cls == "leg":
                allowed |= {0, SHADOW}                          # the gap between the legs
            if view(k) == "side" and orig[p] in (13, 14):
                allowed |= PART_COLORS["arm"]                   # side: the grey cuff of the near arm (golden d2/d3)
            if cls == "boot" and "shadow" in near:
                allowed |= {SHADOW}                             # a sole moved by a pixel (golden sides)
            ok = v in allowed
        if not ok:
            bad[cls] = bad.get(cls, 0) + 1
            if where is not None:
                where.append((p, cls, orig[p], v))
    if parts.get("upright"):
        boots = parts.get("boots", set())
        for foot in feet(boots, {p for p in boots if orig.get(p) in (13, 14)}):
            if not any(px.get(p) in (34, 35) for p in foot):
                bad["foot"] = bad.get("foot", 0) + 1
    return bad

def frame_checks(px: dict, mask: set, orig: dict, rec: dict, k: Key, keep: set, old_head: set = None,
                 arms: set = frozenset()) -> dict:
    """Every check of one finished frame (object space). `orig` = the pose source frame. For a stand-in head,
    `old_head` (the replaced head) leaves the head out of IoU and lost: they then measure the body only."""
    body_px, body_orig = px, orig
    if old_head is not None:
        body_px = {p: v for p, v in px.items() if p not in mask and p not in old_head}
        body_orig = {p: v for p, v in orig.items() if p not in old_head and p not in mask}
    skin, gi, ok = chest(px, mask, k, arms)
    side = view(k)
    return {"iou": round(silhouette_iou(body_px, body_orig), 3),
            "lost": sum(1 for p in body_orig if p not in px),      # hollow shapes: original pixels left empty
            "edge_hair": len(edge_hair(px, mask, rec) - edge_hair(orig, head_mask(orig), rec)),
            "light": len(light_fails(px, mask, keep, side == "back")),
            "chest_skin": skin, "chest_gi": gi, "chest_ok": ok,
            "dark_brows": dark_brows(px, mask)}

# ===== output folders =====

def _palette() -> list:
    """The shared OBJ palette as the sprite export wrote it."""
    first = load_manifest(SPRITES / "set56")[0]
    return Image.open(SPRITES / "set56" / first["png"]).getpalette()

def _key_geometry(o_rec: dict, k_rec: dict, geo: dict) -> dict:
    """Record fields of a key that shares the frame of key k, after k's record was enlarged to `geo`: every
    pixel keeps its place on screen (a flipped twin moves the other way)."""
    if geo is k_rec:
        return {f: o_rec[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")}
    ddx, ddy = k_rec["dx"] - geo["dx"], k_rec["dy"] - geo["dy"]
    twin = (o_rec["attr1"] ^ k_rec["attr1"]) & HFLIP
    dx = o_rec["dx"] + o_rec["w"] - geo["w"] + ddx if twin else o_rec["dx"] - ddx
    return {"dx": dx, "dy": o_rec["dy"] - ddy, "w": geo["w"], "h": geo["h"],
            "attr0": (o_rec["attr0"] & 0x3FFF) | (geo["attr0"] & 0xC000),
            "attr1": (o_rec["attr1"] & 0x3FFF) | (geo["attr1"] & 0xC000)}

def _mask_image_coords(mask: set, rec: dict) -> list:
    w, flip = rec["w"], rec["attr1"] & HFLIP
    out = []
    for ox, oy in sorted(mask):
        x, y = ox - rec["dx"], oy - rec["dy"]
        if 0 <= x < w and 0 <= y < rec["h"]:
            out.append([w - 1 - x if flip else x, y])
    return out

def form_layout(name: str) -> dict:
    """{key: (geometry record, source record or None)} for a gi folder: the form's own frames, and for Super
    Saiyan 2 the set 59 records of the keys set 58 lacks (source None: made by stand_in_head)."""
    own = by_key(SPRITES / FORMS[name])
    if name not in FALLBACK:
        return {k: (r, r) for k, r in own.items()}
    return {k: (own.get(k, r), own.get(k)) for k, r in by_key(SPRITES / FALLBACK[name]).items()}

def back_columns(name: str, set_dir: Path) -> tuple:
    """(x0, x1, chin x): the gi torso columns of golden_{name}_d1 on the row above its sash, in the object space of
    the idle back frame of `set_dir`, and that frame's chin x (the head places the columns on other frames)."""
    rec = by_key(set_dir)[(0, BACK_DIR, 0)]
    gold = image_pixels(Image.open(GOLDEN / f"golden_{name}_d{BACK_DIR}.png"), rec)
    sash = max({y for (_, y), v in gold.items() if v in RED}, key=lambda r: sum(
        1 for (_, y), v in gold.items() if y == r and v in RED))
    xs = [x for (x, y), v in gold.items() if y == sash - 1 and v in GI]
    idle = frame_pixels(rec)
    return min(xs), max(xs), chin_of(idle, head_mask(idle))[0]

def _armor_pass(k: Key, src: dict, own: dict, fallback: dict, parts: dict, anchor: tuple, cap: tuple,
                backs: dict = None) -> tuple:
    """armor_to_gi on the pose source of key k (`src`, or the fallback set's frame when src is None); the lit
    charge frames read their parts from the unlit pose. `backs` = {"own": ..., "fallback": ...} back_columns of
    the two sets. Returns (orig, mask, pixels, notes)."""
    back = (backs or {}).get("own" if src is not None else "fallback")
    orig = frame_pixels(src if src is not None else fallback[k])
    mask = head_mask(orig)
    twin = own.get((LIT_ANIM, k[1], LIT_TWIN))
    if src is not None and k[0] == LIT_ANIM and k[2] >= LIT_FROM and twin:   # the charge glow
        probe, mask = unlit_probe(orig, frame_pixels(twin))
        px, notes = armor_to_gi(probe, mask, parts, key=k, sash_anchor=anchor, sash_cap=cap, back=back)
        parts["source"] = probe                                 # the sleeve check reads the unlit parts
        px.update({p: orig[p] for p in mask})
        notes.append(f"lit frame: parts read from {key_str((LIT_ANIM, k[1], LIT_TWIN))}, lit head kept")
        return orig, mask, px, notes
    px, notes = armor_to_gi(orig, mask, parts, key=k, sash_anchor=anchor, sash_cap=cap, back=back)
    return orig, mask, px, notes

def sash_rows(name: str) -> dict:
    """{key: (body rows, sash row)} of the upright frames of a gi form, after its frame-0 sash anchors."""
    layout = form_layout(name)
    own = by_key(SPRITES / FORMS[name])
    fallback = by_key(SPRITES / FALLBACK[name]) if name in FALLBACK else {}
    anchors, out = {}, {}
    for k in sorted(layout):
        parts = {}
        _armor_pass(k, layout[k][1], own, fallback, parts, anchors.get(k[:2]), None)
        if parts.get("upright"):
            out[k] = (parts["pose"], parts["waist"])
            if k[2] == 0:
                anchors[k[:2]] = out[k]
    return out

def make_gi_set(name: str, layout: dict, out_dir: Path, palette: list, fixes: dict = None) -> None:
    """One PNG per frame header of the layout, plus manifest.json with geometry, notes and checks. The sash of
    each upright frame keeps the row of frame 0 of its (anim, dir) when the body rows match (final, 2026-10-17:
    the belt jumped within the transform step), and in a SASH_MATCH form never sits below the same pose there."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("frame_*.png"):
        old.unlink()
    groups = {}
    for k in sorted(layout):
        groups.setdefault(layout[k][0]["header"], []).append(k)
    fallback = by_key(SPRITES / FALLBACK[name]) if name in FALLBACK else {}
    own = by_key(SPRITES / FORMS[name])
    backs = {"own": back_columns(name, SPRITES / FORMS[name])}
    if name in FALLBACK:                                        # a stand-in body is the other set's back
        twin = next(f for f, s in FORMS.items() if s == FALLBACK[name])
        backs["fallback"] = back_columns(twin, SPRITES / FALLBACK[name])
    caps = sash_rows(SASH_MATCH[name]) if name in SASH_MATCH else {}
    bodies = by_key(out_dir.parent / SHARE[name]) if name in SHARE else {}     # make_frames writes gi_ssj first
    anchors = {}
    torsos = {d: golden_torso(name, own[(0, d, 0)], d) for d in {k[1] for k in layout}}
    manifest, staged = [], []
    for hdr, keys in groups.items():
        k = keys[0]
        rec, src = layout[k]
        notes, old_head, pad, parts = [], None, set(), {"nudge": SASH_NUDGE.get(name, {}).get(key_str(k), 0)}
        orig, mask, px, more = _armor_pass(k, src, own, fallback, parts, anchors.get(k[:2]), caps.get(k), backs)
        notes += more
        if parts.get("upright"):
            anchors.update({o[:2]: (parts["pose"], parts["waist"]) for o in keys if o[2] == 0})
        if src is None:                                         # Super Saiyan 2 key that set 58 lacks
            body = px
            squeeze = (0, 0, 0)
            for _ in range(8):                                  # trim the hair until the frame fits the slot
                px, mask, note, new_head = stand_in_head(body, head_mask(orig), fallback, own, k, orig, squeeze)
                over = slot_overflow(rec, px, {p for p in mask if px.get(p) in GOLD | HAIR_BLACK})
                if not new_head or not any(over):
                    break
                squeeze = tuple(a + b for a, b in zip(squeeze, over))
            if any(squeeze):
                note += f", hair trimmed to fit 32x32 (rows {squeeze[0]}, columns {squeeze[1] + squeeze[2]})"
            notes += [note]
            if new_head:                                        # a new head: check the body only, hair off the edge
                old = head_mask(orig)
                old_head = {p for p in old if p[1] <= chin_of(orig, old)[1]}
                pad = {p for p in mask if px.get(p) in GOLD | HAIR_BLACK}
        keep = ((set().union(set(), *floating(orig)) | swoosh(orig)) - parts.get("reclaimed", set())
                | parts.get("loose", set()))
        arms = parts.get("arms", set()) - mask
        v, more = finish(px, mask, k, keep, arms)
        notes += more
        if name == "gi_ssj2":
            spots = sparks(px, mask)
            if spots:
                paint_sparks_blue(px, spots)
                notes.append(f"{len(spots)} spark pixels blue (Ruling 19)")
                keep |= spots
                parts["sparks"] = spots
        staged.append((hdr, keys, rec, src, notes, old_head, pad, parts, orig, mask, px, keep, arms, v))
    strapped = strap_groups(staged, torsos)
    for hdr, keys, rec, src, notes, old_head, pad, parts, orig, mask, px, keep, arms, v in staged:
        k = keys[0]
        lean = 1 if rec["attr1"] & HFLIP else -1
        notes += gi_rules(px, mask, mask | keep, k, parts, lean, torsos[k[1]], orig, k[:2] in strapped)
        shared = name in SHARE and not any(armor_body_diff(own.get(o), fallback[o]) for o in keys)
        if shared:
            top, body = mask | parts.get("sparks", set()), bodies[k]
            both, body_arms = shared_body(px, top, frame_pixels(body), object_mask(body)), object_mask(body, "arms")
            shared = chest(both, mask, k, body_arms)[2] is not False
            notes.append(f"body: {SHARE[name]} (armor 58 = 59 under the chin), own head and sparks on top" if shared
                         else f"body: own (on the {SHARE[name]} body the head sits higher: a second neck opening)")
        if shared:                                              # the checks read the same composite of the armor
            px, arms, v = both, body_arms, body["v_neck"]
            if src is not None:
                pose = frame_pixels(fallback[k])
                orig = shared_body(orig, top, pose, head_mask(pose))
                keep = ((set().union(set(), *floating(orig)) | swoosh(orig)) - parts.get("reclaimed", set())
                        | parts.get("sparks", set()))
        pinks = stray_pinks(px)
        stray_pinks(orig)                                       # the checks compare with the cleaned source
        if pinks:
            notes.append(f"stray pink: {pinks} px")
        geo = fit_record(rec, px, pad)
        if geo["w"] * geo["h"] > SLOT_BYTES:
            raise ValueError(f"{name} {key_str(k)}: {geo['w']}x{geo['h']} exceeds the {SLOT_BYTES}-byte slot")
        if geo is not rec:
            notes.append(f"record enlarged to {geo['w']}x{geo['h']} (dx {geo['dx']}, dy {geo['dy']}) to hold the head")
        img = render(px, geo, palette)
        fix = (fixes or {}).get(key_str(k), {})
        if fix and FIX_GEOMETRY.get(key_str(k)) != (geo["w"], geo["h"], geo["dx"], geo["dy"]):
            raise ValueError(f"{name} {key_str(k)}: hand fix drawn for {FIX_GEOMETRY.get(key_str(k))}, record is "
                             f"{(geo['w'], geo['h'], geo['dx'], geo['dy'])}")
        for (x, y), val in fix.items():
            img.putpixel((x, y), val)
        if fix:
            notes.append(f"hand edit: {len(fix)} pixels")
        idle = [o for o in keys if o[0] == 0 and o[2] == 0]
        if name in IDLE_GOLDEN and idle:                        # My idle frame wins over every rule
            gold = Image.open(GOLDEN / f"golden_{name}_d{k[1]}.png")
            if gold.size != img.size or geo is not rec:
                raise ValueError(f"{name} {key_str(k)}: golden {gold.size} does not fit the record")
            img.frombytes(gold.tobytes())
            notes.append(f"golden idle frame golden_{name}_d{k[1]}.png")
        drawn = OWNER_FRAMES.get(name, {}).get(k)
        if drawn:                                               # My drawn frame wins over every rule
            gold = Image.open(GOLDEN / drawn)
            if gold.size != img.size or geo is not rec:
                raise ValueError(f"{name} {key_str(k)}: {drawn} {gold.size} does not fit the record")
            img.frombytes(gold.tobytes())
            notes.append(f"golden walk frame {drawn}")
        hand = hand_frames.drawn(name, {o: layout[o][0]["attr1"] for o in keys}, img.size)
        if hand:                                                # a reviewed hand-fixed frame wins over every rule
            if geo is not rec:
                raise ValueError(f"{name} {key_str(k)}: {hand[1]} drawn for the record, the frame was enlarged")
            img.frombytes(hand[0])
            notes.append(f"hand frame {', '.join(hand[1])}")
        png = f"frame_{hdr:06X}.png"
        img.save(out_dir / png, transparency=0)
        final = image_pixels(img, geo)
        if src is not None and shared:                          # the shared body's own swoosh tail (16.0.4)
            keep = keep | loose_white(orig, set(orig) - mask)
        checks = frame_checks(final, mask, orig, geo, k, keep, old_head, arms)
        own_parts = not shared                                  # a shared body is checked on its gi_ssj frame
        forearms = purple_forearms(final, parts.get("wrists", []), parts.get("source", orig),
                                   parts.get("torso", set())) if own_parts else []
        checks["sleeve"] = len(forearms) + len(purple_arms(final, arms if shared else parts.get("arms", set())))
        checks["parts"] = sum(check_parts(final, orig, mask, parts, keep, k).values()) if own_parts else 0
        geo_keys = [{"anim": o[0], "dir": o[1], "index": o[2], **_key_geometry(layout[o][0], rec, geo)}
                    for o in keys]
        manifest.append({"header": hdr, "png": png, "w": geo["w"], "h": geo["h"],
                         "geometry": "enlarged" if geo is not rec else (FORMS[name] if src is not None
                                                                         else FALLBACK[name]),
                         "source": f"{FORMS[name] if src is not None else FALLBACK[name]} {key_str(k)}",
                         "view": view(k), "v_neck": v, "notes": notes, "checks": checks,
                         "check_exception": CHECK_EXCEPTIONS.get(name, {}).get(key_str(k), ""),
                         "head": _mask_image_coords(mask, geo), "arms": _mask_image_coords(arms, geo),
                         "keys": geo_keys})
        if name in SHARE:
            manifest[-1]["body"] = SHARE[name] if shared else "own"
        owner = any(n.startswith(("rule golden", "golden idle", "golden walk")) for n in notes)
        if owner and not manifest[-1]["check_exception"] and set(failing(manifest[-1])) <= GOLDEN_CHECKS:
            manifest[-1]["check_exception"] = GOLDEN_EXCEPTION
        if hand and not manifest[-1]["check_exception"] and failing(manifest[-1]):
            manifest[-1]["check_exception"] = HAND_EXCEPTION
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="ascii")

def failing(m: dict) -> list:
    """Names of the checks a manifest entry fails."""
    c = m["checks"]
    out = [n for n, bad in (("iou", c["iou"] < 0.85), ("lost", c["lost"]), ("edge_hair", c["edge_hair"]),
                            ("light", c["light"]), ("chest", c["chest_ok"] is False),
                            ("sleeve", c.get("sleeve", 0)), ("parts", c.get("parts", 0))) if bad]
    return out

# ===== contact sheets =====

SHEET_SCALE = 4
SHEET_BG = (140, 140, 140)
BROW_SCALE = 8

def _rgba(img: Image.Image) -> Image.Image:
    return img.convert("RGBA")

def _flipped(rec: dict) -> Image.Image:
    img = _rgba(Image.open(rec["dir_path"] / rec["png"]))
    return img.transpose(Image.FLIP_LEFT_RIGHT) if rec["attr1"] & HFLIP else img

def _face_crop(img: Image.Image) -> Image.Image:
    """The top 20 rows of a frame (hair, brows and eyes), cut to the opaque columns."""
    box = img.getbbox() or (0, 0, img.width, img.height)
    return _rgba(img).crop((box[0], box[1], box[2], min(box[1] + 20, box[3])))

def contact_sheet(gi_dir: Path, orig_dirs: list, out_png: Path, title: str, brow_ref: tuple = None) -> None:
    """Every frame of a gi folder at SHEET_SCALE, original | gi, on one anchor. Labels: key, view, checks; red
    marks a failed check, a stand-in head or an enlarged record. `brow_ref` = (sprite dir, key, label): a face
    crop at BROW_SCALE next to the gi face of the same key, for the Super Saiyan eyebrows."""
    font = ImageFont.load_default()
    man = sorted(load_manifest(gi_dir), key=lambda m: (m["keys"][0]["anim"], m["keys"][0]["dir"], m["keys"][0]["index"]))
    origs = [by_key(d) for d in orig_dirs]
    s, per_line, label_h, pad = SHEET_SCALE, 7, 26, 8
    cell_w = 2 * 40 * s + 24
    lines, line = [], []
    for m in man:
        if line and (len(line) == per_line or line[-1]["keys"][0]["anim"] != m["keys"][0]["anim"]):
            lines.append(line)
            line = []
        line.append(m)
    lines.append(line)
    band = 20 * BROW_SCALE + 30 if brow_ref else 0
    sheet = Image.new("RGB", (per_line * cell_w + 20, 40 + band + len(lines) * (label_h + 40 * s + pad)), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 10), f"{title}   (each cell: original | gi, {s}x, same anchor)", fill=(0, 0, 0), font=font)
    y = 40
    if brow_ref:
        ref_dir, ref_key, ref_label = brow_ref
        gi = next(m for m in man if any((o["anim"], o["dir"], o["index"]) == ref_key for o in m["keys"]))
        x = 10
        for label, img in ((ref_label, Image.open(Path(ref_dir) / by_key(Path(ref_dir))[ref_key]["png"])),
                           (f"gi {gi_dir.name} {key_str(ref_key)}", Image.open(gi_dir / gi["png"]))):
            crop = _face_crop(img)
            big = crop.resize((crop.width * BROW_SCALE, crop.height * BROW_SCALE), Image.NEAREST)
            draw.text((x, y), f"eyebrows: {label} ({BROW_SCALE}x)", fill=(0, 0, 0), font=font)
            sheet.paste(big, (x, y + 14), big)
            x += max(big.width, 200) + 40
        y += band
    for line in lines:
        x = 10
        for m in line:
            k0 = m["keys"][0]
            key = (k0["anim"], k0["dir"], k0["index"])
            bad = failing(m)
            flag = bad or m["geometry"] == "enlarged" or any("set 58 has no" in n for n in m["notes"])
            c = m["checks"]
            twins = f" +{len(m['keys']) - 1}" if len(m["keys"]) > 1 else ""
            draw.text((x, y), f"{key_str(key)}{twins} {m['view']} V {m['v_neck'][:3]} iou {c['iou']:.2f} "
                              f"chest {c['chest_skin']}/{c['chest_gi']}{' FAIL ' + ','.join(bad) if bad else ''}",
                      fill=(160, 0, 0) if flag else (0, 0, 0), font=font)
            draw.text((x, y + 12), "; ".join(m["notes"])[:70], fill=(50, 50, 50), font=font)
            o = next((r[key] for r in origs if key in r), None)
            gi_img = _rgba(Image.open(gi_dir / m["png"]))
            if k0["attr1"] & HFLIP:
                gi_img = gi_img.transpose(Image.FLIP_LEFT_RIGHT)
            ax, ay = min(k0["dx"], o["dx"] if o else 0), min(k0["dy"], o["dy"] if o else 0)
            for i, (img, dx, dy) in enumerate(((_flipped(o), o["dx"], o["dy"]) if o else (None, 0, 0),
                                               (gi_img, k0["dx"], k0["dy"]))):
                if img is not None:
                    big = img.resize((img.width * s, img.height * s), Image.NEAREST)
                    sheet.paste(big, (x + i * (40 * s + 6) + (dx - ax) * s, y + label_h + (dy - ay) * s), big)
            x += cell_w
        y += label_h + 40 * s + pad
    sheet.save(out_png)

def overview_sheet(out_png: Path) -> None:
    """Standing frames (anim 0, frame 0) of every dir at 6x: armor next to the gi, for each form."""
    font = ImageFont.load_default()
    s = 6
    rows = [("armor (set 56)", SPRITES / "set56"), ("gi base", ART / "gi_base"),
            ("armor Super Saiyan (set 59)", SPRITES / "set59"), ("gi Super Saiyan", ART / "gi_ssj"),
            ("armor Rage (set 58)", SPRITES / "set58"), ("gi Super Saiyan 2", ART / "gi_ssj2")]
    sheet = Image.new("RGB", (220 + 4 * (32 * s + 12), len(rows) * (32 * s + 16) + 20), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    for i, (label, d) in enumerate(rows):
        recs = by_key(d)
        y = 10 + i * (32 * s + 16)
        draw.text((10, y + 16 * s), label, fill=(0, 0, 0), font=font)
        for dr in range(4):
            big = _flipped(recs[(0, dr, 0)])
            big = big.resize((big.width * s, big.height * s), Image.NEAREST)
            sheet.paste(big, (220 + dr * (32 * s + 12) + (32 * s - big.width) // 2, y), big)
    sheet.save(out_png)

def before_after_sheet(groups: list, out_png: Path, title: str) -> None:
    """[(label, [(caption, PNG path)])] at 4x: one block per label, its images side by side."""
    font = ImageFont.load_default()
    s = 4
    width = 20 + sum(len(imgs) * (32 * s + 8) + 32 for _, imgs in groups)
    sheet = Image.new("RGB", (width, 40 + 64 * s + 30), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 8), title, fill=(0, 0, 0), font=font)
    x = 10
    for label, imgs in groups:
        draw.text((x, 26), label, fill=(0, 0, 0), font=font)
        for caption, path in imgs:
            img = _rgba(Image.open(path))
            big = img.resize((img.width * s, img.height * s), Image.NEAREST)
            draw.text((x, 40 + big.height + 4), caption, fill=(0, 0, 0), font=font)
            sheet.paste(big, (x, 40), big)
            x += max(big.width, 32 * s) + 8
        x += 32
    sheet.save(out_png)

def _png_of(folder: Path, k: Key) -> Path:
    rec = by_key(folder)[k]
    return rec["dir_path"] / rec["png"]

def transform_test_sheet(out_png: Path) -> None:
    """Ruling 25 test cases (my direction n): Super Saiyan 9.2.0-9.2.2, original | old method | gi."""
    old = WORK / "gi_ssj_old_method"
    groups = [(f"9.2.{i}", [("set 59", _png_of(SPRITES / "set59", (9, 2, i))), ("old method", _png_of(old, (9, 2, i))),
                            ("gi", _png_of(ART / "gi_ssj", (9, 2, i)))]) for i in range(3)]
    before_after_sheet(groups, out_png, "Super Saiyan 9.2.0-9.2.2 (Ruling 25 test cases): original | before | after, 4x")

# ===== animation review =====
# Frame timing from re-outfit.md section 7: anim 0 shows frame 1 for 16 of 256 ticks, anims 1 and 16 step every
# 8 ticks (60 ticks a second). Other animations are not traced; they play at 6 frames a second.

ANIM_MS = {0: (4000, 267), 1: 133, 16: 133}
DEFAULT_MS = 167
ANIM_SCALE = 4

def _strip_frames(recs: dict, anim: int, d: int) -> list:
    return [(k, _flipped(recs[k]), recs[k]["dx"], recs[k]["dy"])
            for k in sorted(k for k in recs if k[0] == anim and k[1] == d)]

def _canvas(frames_sets: list) -> tuple:
    xs = [x for fs in frames_sets for _, img, dx, dy in fs for x in (dx, dx + img.width)]
    ys = [y for fs in frames_sets for _, img, dx, dy in fs for y in (dy, dy + img.height)]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

def _place(img, dx, dy, box, under=None):
    x0, y0, w, h = box
    cell = Image.new("RGBA", (w, h), SHEET_BG + (255,))
    if under is not None:
        u_img, u_dx, u_dy = under
        ghost = u_img.copy()
        ghost.putalpha(ghost.getchannel("A").point(lambda a: a * 40 // 100))
        cell.alpha_composite(ghost, (u_dx - x0, u_dy - y0))
    cell.alpha_composite(img, (dx - x0, dy - y0))
    return cell.resize((w * ANIM_SCALE, h * ANIM_SCALE), Image.NEAREST)

def strip_sheet(rows: list, out_png: Path, title: str, labels: list = None) -> None:
    """Rows of (row label, [cell images]) under a title."""
    font = ImageFont.load_default()
    cw = max(f.width for _, r in rows for f in r) + 6
    ch = max(f.height for _, r in rows for f in r) + 14
    sheet = Image.new("RGB", (110 + max(len(r) for _, r in rows) * cw, 24 + len(rows) * ch), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((4, 4), title, fill=(0, 0, 0), font=font)
    for i, (label, row) in enumerate(rows):
        draw.text((4, 24 + i * ch + ch // 2), label, fill=(0, 0, 0), font=font)
        for j, f in enumerate(row):
            if labels:
                draw.text((110 + j * cw, 24 + i * ch), labels[i][j] if j < len(labels[i]) else "", fill=(0, 0, 0), font=font)
            sheet.paste(f, (110 + j * cw, 24 + i * ch + 11))
    sheet.save(out_png)

def save_gif(cells: list, path: Path, anim: int) -> None:
    ms = ANIM_MS.get(anim, DEFAULT_MS)
    durations = list(ms) if isinstance(ms, tuple) and len(ms) == len(cells) else \
        [ms if isinstance(ms, int) else DEFAULT_MS] * len(cells)
    frames = [f.convert("RGB") for f in cells]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0)

def anim_review(form_dir: Path, orig_dirs: list, out_dir: Path, title: str) -> list:
    """For every anim: one strip PNG (per dir a block: gi | original | onion skin, previous frame at 40 %, all on
    the record anchor) and one GIF per (anim, dir). Returns the GIF paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    gi = by_key(form_dir)
    origs = [by_key(d) for d in orig_dirs]
    gifs = []
    for anim in sorted({k[0] for k in gi}):
        rows = {"gi": [], "orig": [], "onion": []}
        labels = {"gi": [], "orig": [], "onion": []}
        for d in sorted({k[1] for k in gi if k[0] == anim}):
            mine = _strip_frames(gi, anim, d)
            orig = next((_strip_frames(o, anim, d) for o in origs if (anim, d, 0) in o), [])
            box = _canvas([mine, orig] if orig else [mine])
            new = [_place(img, dx, dy, box) for _, img, dx, dy in mine]
            old = [_place(img, dx, dy, box) for _, img, dx, dy in orig]
            onion = [_place(img, dx, dy, box, under=mine[i - 1][1:]) for i, (_, img, dx, dy) in enumerate(mine)]
            n = max(len(new), len(old))
            blank = Image.new("RGBA", new[0].size, SHEET_BG + (255,))
            for name, cells, src in (("gi", new, mine), ("orig", old, orig), ("onion", onion, mine)):
                rows[name] += cells + [blank] * (n - len(cells)) + [Image.new("RGBA", (8, 8), SHEET_BG + (255,))]
                labels[name] += [key_str(k) for k, *_ in src] + [""] * (n - len(src)) + [""]
            path = out_dir / f"{form_dir.name}_a{anim:02d}_d{d}.gif"
            save_gif(new, path, anim)
            gifs.append(path)
        strip_sheet([(r, rows[r]) for r in rows], out_dir / f"{form_dir.name}_a{anim:02d}_strip.png",
                    f"{title} anim {anim}: rows = gi | original | onion skin (previous frame at 40 %), "
                    f"blocks = dir 0..3, {ANIM_SCALE}x", [labels[r] for r in rows])
    return gifs

# Transform comparison (my direction i). Base sets play anim 9 (power up), Super Saiyan sets play anim 21
# (revert). Pairs from the appearance table rom:0x1D967C (+1 set id, +4 transform target entry).
COMPARE_ROWS = (("Goku set 60 (entry 19 -> 20)", "set60", 9), ("Goku SSJ set 61 (entry 20)", "set61", 21),
                ("Vegeta set 137 (entry 8 -> 11)", "set137", 9), ("Vegeta SSJ set 140 (entry 11)", "set140", 21),
                ("Trunks set 129 (entry 13 -> 14)", "set129", 9), ("Trunks SSJ set 130 (entry 14)", "set130", 21),
                ("Gohan set 56 (entry 2 -> 5)", "set56", 9), ("gi base", "gi_base", 9),
                ("Gohan SSJ set 59 (entry 5 -> 4)", "set59", 9), ("gi SSJ (SSJ -> SSJ2 step)", "gi_ssj", 9),
                ("Gohan SSJ set 59 revert", "set59", 21), ("gi SSJ revert", "gi_ssj", 21),
                ("gi SSJ2 revert", "gi_ssj2", 21))

def compare_transform(out_png: Path, gif_dir: Path) -> list:
    """One sheet: a row per COMPARE_ROWS entry, all dirs, 4 frames each, one anchor, 4x; a GIF per row (dir 0)."""
    gif_dir.mkdir(parents=True, exist_ok=True)
    folders = {name: by_key(ART / name if name.startswith("gi_") else SPRITES / name) for _, name, _ in COMPARE_ROWS}
    strips = [[_strip_frames(folders[name], anim, d) for d in range(4)] for _, name, anim in COMPARE_ROWS]
    box = _canvas([f for row in strips for f in row])
    rows, labels, gifs = [], [], []
    for (label, name, anim), row in zip(COMPARE_ROWS, strips):
        cells, names = [], []
        for d, frames in enumerate(row):
            cells += [_place(img, dx, dy, box) for _, img, dx, dy in frames] + [Image.new("RGBA", (8, 8), SHEET_BG + (255,))]
            names += [f"{name} {key_str(k)}" if j == 0 else key_str(k) for j, (k, *_) in enumerate(frames)] + [""]
        rows.append((label[:18], cells))
        labels.append(names)
        path = gif_dir / f"compare_{name}_a{anim:02d}_d0.gif"
        save_gif([_place(img, dx, dy, box) for _, img, dx, dy in row[0]], path, anim)
        gifs.append(path)
    strip_sheet(rows, out_png, "Transform comparison, anim 9 (power up) and 21 (revert), blocks = dir 0..3, one anchor, "
                f"{ANIM_SCALE}x. Rows: " + "; ".join(r[0] for r in COMPARE_ROWS), labels)
    return gifs

# ===== HUD "Z2" icon (draft, Ruling 17; approved 2026-10-16, do not change) =====

Z_USABLE, Z_DIM, ICON_LEN = 0x6DAE7C, 0x6DB07C, 0x200
Z_SHIFT = 2                                                # move the Z left to make room for the "2"
Z_PANEL = (13, 3, 28, 8)                                   # x0, y0, x1, y1 of the black panel interior holding the Z
TWO = ("###", "..#", "###", "#..", "###")                  # 3 x 5 glyph, bottom right like the Buu's Fury "3"
TWO_AT = (26, 4)
TWO_COLOR = {"usable": 191, "dim": 23}                     # light blue like the "3"; the dim Z's brown

def make_z2_icons(rom: bytes, out_dir: Path) -> None:
    """Usable and dim "Z2" icons from the "Z" icons: the Z moves left inside its panel and a small "2" sits at the
    bottom right. Pixels outside the panel (the HP, EP and EXP bars draw there) stay as they are."""
    palette = bytes(rom[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN])
    x0, y0, x1, y1 = Z_PANEL
    imgs = {}
    for kind, off in (("usable", Z_USABLE), ("dim", Z_DIM)):
        img = tiles_to_image(bytes(rom[off:off + ICON_LEN]), 32, 16, palette)
        old = img.copy()
        for y in range(y0, y1 + 1):                             # clear the panel to black, then redraw the Z
            for x in range(x0, x1 + 1):
                img.putpixel((x, y), 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                v = old.getpixel((x, y))
                if v != 1 and x0 <= x - Z_SHIFT:
                    img.putpixel((x - Z_SHIFT, y), v)
        for dy, line in enumerate(TWO):
            for dx, c in enumerate(line):
                if c == "#":
                    img.putpixel((TWO_AT[0] + dx, TWO_AT[1] + dy), TWO_COLOR[kind])
        (Path(out_dir) / f"hud_z2_{kind}.bin").write_bytes(image_to_tiles(img))
        imgs[kind] = (old, img)
    s = 10
    sheet = Image.new("RGB", (2 * (32 * s + 20) + 20, 2 * (16 * s + 20) + 30), SHEET_BG)
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 4), "top: LoG II Z (usable, dim)   bottom: draft Z2 (usable, dim)   10x", fill=(0, 0, 0))
    for i, kind in enumerate(("usable", "dim")):
        for j, img in enumerate(imgs[kind]):
            big = img.convert("RGB").resize((32 * s, 16 * s), Image.NEAREST)
            sheet.paste(big, (10 + i * (32 * s + 20), 20 + j * (16 * s + 20)))
    small = Image.new("RGB", (32 * 2 + 12, 16 + 8), SHEET_BG)
    for i, kind in enumerate(("usable", "dim")):
        small.paste(imgs[kind][1].convert("RGB"), (4 + i * 36, 4))
    sheet.paste(small, (sheet.width - small.width - 10, sheet.height - small.height - 4))
    sheet.save(Path(out_dir) / "hud_z2.png")

# ===== hand fixes and check exceptions =====
# Hand fixes are applied last, in the image of the output frame: {folder: {"anim.dir.index": {(x, y): index}}}.
# Index 0 clears a pixel. fix_rows("x,y: i i i") sets pixels from (x, y) to the right.

def fix_rows(*rows: str) -> dict:
    out = {}
    for row in rows:
        at, vals = row.split(":")
        x, y = map(int, at.split(","))
        for i, v in enumerate(vals.split()):
            out[(x + i, y)] = int(v)
    return out

# 7.2.3 (my review fix round 1): the punch arm is drawn back and its fist is hidden; the band marks the forearm end.
_PUNCH_BAND = {"7.2.3": fix_rows("6,19: 195", "6,20: 72")}
# 1.2.2 (my review 2026-10-17, side walk): the back arm swung behind is 1 px of suit in the armor. Drawn as the
# front arm reads: a skin arm with its outline, the band beside the fist.
_WALK_BACK_ARM = {"1.2.2": fix_rows("11,19: 23 116 116 23", "11,20: 23 116 195", "11,21: 23 117 72", "11,22: 23")}
FIXES = {name: {**_PUNCH_BAND, **_WALK_BACK_ARM} for name in ("gi_base", "gi_ssj", "gi_ssj2")}
# Image coordinates hold only for the record a fix was drawn on: (w, h, dx, dy). make_gi_set refuses any other.
FIX_GEOMETRY = {"7.2.3": (32, 32, -8, -24), "1.2.2": (16, 32, 0, -24)}
# White parts the shape rules miss, found in the strip review: {"anim.dir.index": {object point: class}}. The
# poses match in sets 56, 58 and 59, so one point serves all three. "chest" paints gi purple.
PART_HINTS = {
    "16.1.1": {(12, -4): "boot"},                            # back view: the raised knee, not a fist
    "5.1.0": {(2, 3): "boot", (9, -5): "chest", (11, -5): "chest", (14, -1): "hand"},   # back view: knee, collar,
                                                              # shoulder shine, the far fist beside the trim
    "6.1.0": {(2, 3): "boot", (9, -5): "chest"},
    "7.1.0": {(11, 3): "boot", (4, -5): "chest"},
    "8.1.0": {(1, -4): "hand"},                               # back view: the fist at the left edge, not a strap
    "6.1.3": {(11, 0): "boot", (6, -7): "chest"},            # back view kick: raised boot, collar
    "7.1.3": {(2, 1): "boot", (8, -7): "chest", (7, -7): "chest"},
    "13.1.1": {(13, -3): "hand"},                             # back view walk: the far hand sits by a boot
    "13.1.3": {(1, -2): "hand"},
    "13.2.1": {(9, -7): "chest"},                             # side walk: collar under the chin
    "13.3.1": {(5, -7): "chest"},
    "14.0.3": {(12, 2): "hand", (0, 3): "hand"},              # sitting: hands rest on the knees
    "16.2.4": {(-7, -5): "boot", (-7, 1): "boot"},            # flying kick: the kicking boot (set 56 point, sets 58/59 point)
    "16.2.5": {(2, -3): "chest"},                            # hunched: the plate's lower edge, not a fist
    "16.2.6": {(2, -3): "chest"},
    "16.3.4": {(20, -5): "boot", (20, 1): "boot"},
    "14.0.4": {(12, 2): "hand", (0, 3): "hand"},
    "18.1.0": {(12, 2): "boot", (8, -3): "chest"},            # back view charge: the far boot sits high, plate back
    "18.1.1": {(11, 0): "boot"},
    "18.1.2": {(11, 0): "boot"},                              # the lit frames 18.1.2-6 (parts read from 18.1.1)
    "1.2.0": {(13, 0): "hand"},                               # side walk: the back fist swung behind, beside the
                                                              # back boot (final, 2026-10-17: an arm, not a leg)
    "7.0.1": {(4, 2): "hand"},                                # the fist hanging at the left side, on its boot
    "5.0.1": {(11, 1): "hand"},                               # the fist hanging on its boot (10:52 AM: its
    "6.0.1": {(11, 1): "hand"},                               # forearm read as gi); its arm runs straight up
}
# A fist drawn touching a boot is one white part: {"anim.dir.index": {object point: last fist row}} cuts it there
# before the parts are sorted (my review 2026-10-17, 7.0.1: the arm hangs down the left side across the sash).
PART_SPLITS = {"7.0.1": {(4, 2): 3}}
# Suit islands that are bare arms with no glove in view (reviewed at 7x, my review 2026-10-17: arms are skin).
# A seed marks the island; islands over ARM_ISLAND_MAX px are torso and stay gi. Points hold for sets 56, 58, 59.
ARM_ISLAND_MAX = 20
_BACK_CHARGE = [(2, -7), (11, -6)]                             # back view charge: both arms at the sides
_FRONT_CHARGE = [(3, -5)]                                      # front charge: the far arm
ARM_SEEDS = {
    "2.1.0": [(2, -5), (12, -5)], "2.1.2": [(2, -1), (12, -1)], "2.1.3": [(2, -3), (12, -3)],   # hurt, back view
    "13.1.0": [(12, -10)], "13.1.2": [(4, -9), (2, -10)],      # back view walk: the swung arm by the hair
    "16.1.3": [(3, -7), (3, -1)],                             # back view kick: set 56 point, sets 58/59 point
    "6.1.1": [(13, -6)], "7.1.1": [(2, -6)],                  # back view kick: the bent arm by the head (me
                                                              # review 2026-10-17); its fist sits by the waist
    **{f"18.0.{i}": _FRONT_CHARGE for i in range(1, 7)},
    **{f"18.1.{i}": _BACK_CHARGE for i in range(1, 7)},
}
# Hunched poses (reviewed at 8x): the fist sits on a torso too small for the core test, so a full sleeve flood
# would bare the whole torso. Their sleeve is the forearm only.
SHORT_REACH = {"2.0.2": 3, "2.0.3": 3, "6.0.2": 3, "7.0.2": 3}
_LYING_HAND = "knocked down: the box under the chin holds the hand on the ground, not the chest (reviewed at 4x)"
CHECK_EXCEPTIONS = {"gi_base": {"3.0.1": _LYING_HAND}, "gi_ssj": {"3.0.1": _LYING_HAND},
                    "gi_ssj2": {"3.0.1": _LYING_HAND}}                # {folder: {"anim.dir.index": reason}}
# check_parts misfits of 1-3 px left for me to draw (owner-0948 report, review sheets parts_<form>.png):
# the side views have no torso split, so an arm across the side torso reads as torso.
_PARTS_OWNER = "parts: listed for the owner (owner-0948 review sheet)"
PARTS_REVIEW = {"gi_base": ("7.2.3", "16.2.2"),
                "gi_ssj": ("1.0.2", "2.0.2", "2.0.3", "4.1.1", "4.1.3", "7.0.3", "7.2.3", "16.2.1"),
                "gi_ssj2": ("2.0.2", "9.0.3", "11.0.1")}
for _name, _keys in PARTS_REVIEW.items():
    CHECK_EXCEPTIONS[_name].update({_k: _PARTS_OWNER for _k in _keys})

# ===== command line =====

def make_frames() -> None:
    palette = _palette()
    for name in FORMS:
        make_gi_set(name, form_layout(name), ART / name, palette, FIXES[name])

def make_sheets() -> None:
    contact_sheet(ART / "gi_base", [SPRITES / "set56"], ART / "gi_base_sheet.png", "gi base (pose: set 56)")
    contact_sheet(ART / "gi_ssj", [SPRITES / "set59"], ART / "gi_ssj_sheet.png", "gi Super Saiyan (pose: set 59)",
                  brow_ref=(SPRITES / "set61", (0, 0, 0), "Goku Super Saiyan set 61 0.0.0"))
    contact_sheet(ART / "gi_ssj2", [SPRITES / "set58", SPRITES / "set59"], ART / "gi_ssj2_sheet.png",
                  "gi Super Saiyan 2 (pose: set 58; set 59 body where 58 has no frame)")
    overview_sheet(ART / "gi_overview.png")

def make_anim() -> None:
    anim_review(ART / "gi_base", [SPRITES / "set56"], ART / "anim" / "gi_base", "gi base")
    anim_review(ART / "gi_ssj", [SPRITES / "set59"], ART / "anim" / "gi_ssj", "gi Super Saiyan")
    anim_review(ART / "gi_ssj2", [SPRITES / "set58", SPRITES / "set59"], ART / "anim" / "gi_ssj2", "gi Super Saiyan 2")

def make_compare() -> None:
    compare_transform(ART / "anim" / "compare_transform.png", ART / "anim" / "compare")
    transform_test_sheet(ART / "gi_ssj_9_2_test_cases.png")

def _main(argv: list) -> int:
    if not argv or argv[0] not in ("all", "frames", "sheets", "anim", "compare", "z2"):
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd in ("all", "frames"):
        make_frames()
    if cmd in ("all", "sheets"):
        make_sheets()
    if cmd in ("all", "anim"):
        make_anim()
    if cmd in ("all", "compare"):
        make_compare()
    if cmd == "z2":
        make_z2_icons(BASE_ROM.read_bytes(), ART)
    for name in FORMS:
        man = load_manifest(ART / name)
        bad = [(m, failing(m)) for m in man if failing(m) and not m["check_exception"]]
        print(name, len(man), "frames, failing", len(bad), " ".join(
            f'{key_str((m["keys"][0]["anim"], m["keys"][0]["dir"], m["keys"][0]["index"]))}({",".join(f)})'
            for m, f in bad))
    return 0

if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
