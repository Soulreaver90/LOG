r"""
gi_aura.py - SSJ2 lightning aura, outline family: bolts baked into the gi SSJ2 (set 159) and gi Rage (set 160) frames.

Usage:   py -3 -I scripts\permanent\art\gi_aura.py all          (from the LOG root, after gi_post.py all; all = OUTPUTS,
                                                              then V4_OUTPUTS)
         py -3 -I scripts\permanent\art\gi_aura.py reference    (prints the frame compare with my GIFs)
Input:   art\gi_ssj2_v2\ (set 159 body), art\gi_rage\ (set 160 body, r12 gi_ssj2_v2 copy),
         art\golden\golden_gi_ssj2std_d0-3.png (set 159 idle body), golden_gi_ssj2_d0-2.png (reference body),
         the base ROM (set 58 layout). All read only.
Output:  art\gi_ssj2_aura\ and gi_rage_aura\ (manifest.json plus PNGs). gohan_gi reads them for sets 159, 160.
         V4_OUTPUTS: gi_ssj2_aura_v4\ from the derived body gi_ssj2_v4\ (gi_one_body.py), same seeds as
         gi_ssj2_aura, bolt start points from the gi_ssj2_v2 frames (ring), so today's bolts keep their place.
API:     outline(rng, px, w, h) -> {(x, y): index}      bake(px, pattern, palette, w, h) -> bytes
         face_box(px, w) -> set      reference_patterns() -> [[pattern per dir 0-2] per column 0-5]
         aura_folder(body, out, idle_body, tag, layout, ring) -> manifest      run_all(art) -> None
         ring_pattern(ring, rec, tag, key) -> pattern
Method:  Port of the outline family of art\golden\work_r3\aura2\bolts.py (final, 2026-10-18 3:23 PM, "outline
         d0-d2"), same RNG call order: 2-3 short branched bolts that start on the transparent ring around the body.
         1. Idle (anim 0): 6 records per dir, index = body * 3 + shape (the ssj2_idle hook). Body 0 and 1 are the
            vanilla idle frames 0 and 1; one pattern per (dir, shape) goes on both bodies.
            Set 160 shapes 0-2 = reference columns 0-2 (seed 22): its idle body is the reference body.
            Set 159 idle body = the std goldens (both bodies; no blink art exists), patterns seeded per (dir, shape).
         2. Walk (1), run (13), ki charge (4): each frame its own pattern, seeded by (set tag, anim, dir, index).
         3. Dir 3 keys that flip a dir 2 frame keep the flip, so their bolts mirror dir 2.
         4. Last, the reviewed hand frames of the folder (hand_frames.HAND, gi_ssj2_aura only) replace theirs.
Rules:   No bolt pixel on the face box (iris 64/65 box grown 3 px, 5 rows up, 3 down). White core is index 2, glow
         is 191; a white bolt pixel over a bright body pixel (r + g + b > 450) becomes 191. Deterministic: fixed
         seeds only. No palette change. The goldens and the body folders are never written.
"""
import json
import random
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from art import hand_frames  # noqa: E402
import log_paths  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
ART = log_paths.ART
GOLDEN = ART / "golden"
REF_DIR = GOLDEN / "work_r3" / "aura2"                        # My approved mockups
BASE_ROM = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
BLUE, WHITE = 191, 2
IRIS = {64, 65}
BRIGHT = 450                                                  # r + g + b above this: white would vanish
REF_SEED, REF_COLUMNS, REF_SCALE = 22, 6, 6                   # bolts.py main(): outline family
AURA_ANIMS = (1, 4, 13)                                       # walk, ki charge, run (idle is handled apart)
IDLE_SHAPES, IDLE_BODIES = 3, 2
HFLIP = 0x1000
OUTPUTS = {"gi_ssj2_aura": ("gi_ssj2_v2", "golden_gi_ssj2std", None),     # out: (body folder, idle golden, layout)
           "gi_rage_aura": ("gi_rage", None, 58)}
# One body (gi_one_body.py): the derived set 159 body gets today's bolts. Same seeds (tag gi_ssj2_aura), and the
# start points come from the gi_ssj2_v2 frames (ring), so the bolts stay where they are. out: (body, idle, layout,
# tag, ring)
V4_OUTPUTS = {"gi_ssj2_aura_v4": ("gi_ssj2_v4", "golden_gi_ssj2std", None, "gi_ssj2_aura", "gi_ssj2_v2")}


# ===== bolts (port of aura2\bolts.py, outline family) =====

def face_box(px: bytes, w: int = 32) -> set:
    """Iris bounding box grown 3 px each side, 5 rows up and 3 down: the face the bolts never cover."""
    pts = [(i % w, i // w) for i, v in enumerate(px) if v in IRIS]
    if not pts:
        return set()
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return {(x, y) for x in range(min(xs) - 3, max(xs) + 4) for y in range(min(ys) - 5, max(ys) + 4)}


def walk(rng: random.Random, a: tuple, b: tuple, jag: int = 1) -> list:
    """Jagged 8-connected path from a to b: a sideways kick every 2-3 steps."""
    (x, y), (bx, by) = a, b
    pts, n = [(x, y)], 0
    while (x, y) != (bx, by) and n < 80:
        n += 1
        sx, sy = (bx > x) - (bx < x), (by > y) - (by < y)
        if n % rng.choice((2, 3)) == 0:
            if abs(bx - x) >= abs(by - y):
                y += rng.choice((-jag, jag))
            else:
                x += rng.choice((-jag, jag))
        else:
            x, y = x + sx, y + sy
        pts.append((x, y))
    return pts


def silhouette(px: bytes, w: int = 32, h: int = 32) -> list:
    """Transparent pixels 4-adjacent to the body, sorted."""
    body = {(i % w, i // w) for i, v in enumerate(px) if v}
    ring = set()
    for x, y in body:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < w and 0 <= q[1] < h and q not in body:
                ring.add(q)
    return sorted(ring)


def outline(rng: random.Random, px: bytes, w: int = 32, h: int = 32) -> dict:
    """2-3 short branched bolts from the outline ring: trunk white every third pixel, else blue; one blue branch."""
    out, ring = {}, silhouette(px, w, h)
    for _ in range(rng.choice((2, 3, 3))):
        x, y = rng.choice(ring)
        tip = (x + rng.randint(-5, 5), y + rng.randint(-6, 6))
        trunk = walk(rng, (x, y), tip)
        for j, p in enumerate(trunk):
            out[p] = WHITE if j % 3 == 1 else BLUE
        if len(trunk) > 3:
            bx, by = trunk[len(trunk) // 2]
            for p in walk(rng, (bx, by), (bx + rng.choice((-3, 3)), by + rng.choice((-3, 3)))):
                out.setdefault(p, BLUE)
    return out


def bake(px: bytes, pattern: dict, palette: list, w: int = 32, h: int = 32) -> bytes:
    """Pattern over the frame, clipped to it, never on the face box; white over a bright pixel turns blue."""
    out, face = bytearray(px), face_box(px, w)
    for (x, y), v in pattern.items():
        if 0 <= x < w and 0 <= y < h and (x, y) not in face:
            under = px[y * w + x]
            r, g, b = palette[3 * under:3 * under + 3]
            out[y * w + x] = BLUE if v == WHITE and under and r + g + b > BRIGHT else v
    return bytes(out)


# ===== my reference =====

def reference_patterns() -> list:
    """bolts.py main() order for the outline family: seed 22, column by column, each column dirs 0, 1, 2."""
    rng = random.Random(REF_SEED)
    views = [Image.open(GOLDEN / f"golden_gi_ssj2_d{d}.png").tobytes() for d in (0, 1, 2)]
    return [[outline(rng, v) for v in views] for _ in range(REF_COLUMNS)]


def render(px: bytes, palette: list, w: int = 32, h: int = 32, scale: int = REF_SCALE) -> Image.Image:
    """bolts.py render(): the frame on lime at `scale`, color 0 transparent."""
    from art.gi_review import BACKGROUND
    o = Image.frombytes("P", (w, h), px)
    o.putpalette(palette)
    g = Image.new("RGB", (w * scale, h * scale), BACKGROUND)
    big = o.convert("RGBA").resize((w * scale, h * scale), Image.NEAREST)
    mask = Image.frombytes("L", (w, h), bytes(255 if p else 0 for p in px)).resize((w * scale, h * scale))
    g.paste(big, (0, 0), mask)
    return g


def reference_compare() -> dict:
    """{dir: [differing pixel count per GIF frame]} of the port against aura2_outline_d0..d2.gif."""
    pats, out = reference_patterns(), {}
    for d in (0, 1, 2):
        gold = Image.open(GOLDEN / f"golden_gi_ssj2_d{d}.png")
        px, pal = gold.tobytes(), gold.getpalette()
        gif, diffs = Image.open(REF_DIR / f"aura2_outline_d{d}.gif"), []
        for c in range(REF_COLUMNS):
            gif.seek(c)
            want = gif.convert("RGB").tobytes()
            got = render(bake(px, pats[c][d], pal), pal).tobytes()
            diffs.append(sum(1 for i in range(0, len(want), 3) if want[i:i + 3] != got[i:i + 3]))
        out[d] = diffs
    return out


# ===== folders =====

def _seeded(tag: str, *parts) -> random.Random:
    return random.Random(":".join(str(p) for p in (tag,) + parts))    # str seeds hash with SHA-512: stable


def _layout_rows(set_id: int) -> set:
    """(anim, dir) rows of a base ROM set (set 58 for Rage)."""
    from rom.log2_sprites import set_records
    from rom.webfoot_decompress import SET_TABLE, rom_ptr
    rom = BASE_ROM.read_bytes()
    return {(r["anim"], r["dir"]) for r in set_records(rom, rom_ptr(rom, SET_TABLE + 4 * (set_id - 7)))}


def _load(folder: Path) -> tuple:
    man = json.loads((folder / "manifest.json").read_text(encoding="ascii"))
    keys = {(k["anim"], k["dir"], k["index"]): (e, k) for e in man for k in e["keys"]}
    return man, keys


def _save(img_px: bytes, palette: list, w: int, h: int, path: Path) -> None:
    im = Image.frombytes("P", (w, h), img_px)
    im.putpalette(palette)
    im.save(path, transparency=0)


def ring_pattern(ring: Path, rec: dict, tag: str, key: tuple) -> dict:
    """The bolts of `key` seeded on the frame of the `ring` folder (the body the bolts were made on), moved into
    the record `rec`, so each bolt keeps its screen place when the body under it changes (gi_one_body)."""
    _, ring_keys = _load(ring)
    old_e, old_k = ring_keys[key]
    with Image.open(ring / old_e["png"]) as im:
        px, (w, h) = im.tobytes(), im.size
    if (w, h) != (rec["w"], rec["h"]):
        raise ValueError(f"{key}: ring frame {w}x{h}, record {rec['w']}x{rec['h']}")
    sx = (old_k["dx"] - rec["dx"]) * (-1 if rec["attr1"] & HFLIP else 1)
    sy = old_k["dy"] - rec["dy"]
    return {(x + sx, y + sy): v for (x, y), v in outline(_seeded(tag, *key), px, w, h).items()}


def aura_folder(body: Path, out: Path, idle_body: str = None, tag: str = None, layout: int = None,
                ring: Path = None) -> list:
    """Write `out`: every frame of `body` (rows of `layout` only, when given), anims 1, 4, 13 with bolts, anim 0
    as 6 records per dir. idle_body: golden name prefix that replaces both idle bodies (dir 3 = flipped dir 2).
    ring: the folder whose frames seed the bolt start points (default: `body`)."""
    man, keys = _load(body)
    rows = _layout_rows(layout) if layout else None
    tag = tag or out.name
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    entries, made = {}, {}                                    # png name -> entry; (source, pattern id) -> png name

    def add(png: str, src_entry: dict, key: dict, extra: dict = None) -> None:
        e = entries.get(png)
        if e is None:
            e = {f: v for f, v in src_entry.items() if f != "keys"} | {"png": png, "keys": []} | (extra or {})
            entries[png] = e
        e["keys"].append(key)

    # 1. frames without aura: copied as they are
    for (a, d, i), (e, k) in sorted(keys.items()):
        if rows is not None and (a, d) not in rows or a == 0 or a in AURA_ANIMS:
            continue
        if e["png"] not in entries:
            shutil.copyfile(body / e["png"], out / e["png"])
        add(e["png"], e, dict(k))

    # 2. walk, ki charge, run: one pattern per frame; a dir 3 flip of the dir 2 frame keeps the dir 2 bolts
    for (a, d, i), (e, k) in sorted(keys.items()):
        if a not in AURA_ANIMS or rows is not None and (a, d) not in rows:
            continue
        twin = keys.get((a, 2, i))
        pd = 2 if d == 3 and twin and twin[0]["png"] == e["png"] and (k["attr1"] ^ twin[1]["attr1"]) & HFLIP else d
        pid = f"a{a:02}_d{pd}_i{i}"
        if (e["png"], pid) not in made:
            with Image.open(body / e["png"]) as im:
                px, pal, (w, h) = im.tobytes(), im.getpalette(), im.size
            png = f"aura_{pid}.png"
            if ring is None:
                pattern = outline(_seeded(tag, a, pd, i), px, w, h)
            else:
                pattern = ring_pattern(ring, keys[(a, pd, i)][1], tag, (a, pd, i))
            _save(bake(px, pattern, pal, w, h), pal, w, h, out / png)
            made[e["png"], pid] = png
        add(made[e["png"], pid], e, dict(k), {"aura": {"body": e["png"], "pattern": pid}})

    # 3. idle: index = body * 3 + shape
    ref = reference_patterns() if idle_body is None else None
    for d in range(4):
        pd = 2 if d == 3 else d
        for b in range(IDLE_BODIES):
            e, k = keys[(0, d, b)]
            if idle_body:
                src = GOLDEN / f"{idle_body}_d{pd}.png"
                e = {f: v for f, v in e.items() if f not in ("keys", "png")} | {"source": f"golden {src.name}"}
            else:
                src = body / e["png"]
            with Image.open(src) as im:
                px, pal, (w, h) = im.tobytes(), im.getpalette(), im.size
            if (w, h) != (k["w"], k["h"]):
                raise ValueError(f"{src.name}: {w}x{h}, idle record is {k['w']}x{k['h']}")
            for s in range(IDLE_SHAPES):
                pid = f"idle_d{pd}_s{s}"
                if (src.name, pid) not in made:
                    if ref is not None:
                        pattern = ref[s][pd]                    # My approved columns 0-2
                    else:
                        with Image.open(GOLDEN / f"{idle_body}_d{pd}.png") as im0:
                            pattern = outline(_seeded(tag, 0, pd, s), im0.tobytes(), w, h)
                    png = f"aura_{pid}_b{b}.png"
                    _save(bake(px, pattern, pal, w, h), pal, w, h, out / png)
                    made[src.name, pid] = png
                add(made[src.name, pid], e, dict(k) | {"index": b * IDLE_SHAPES + s},
                    {"aura": {"body": src.name, "pattern": pid}})
    manifest = list(entries.values())
    for e in manifest:
        e["keys"].sort(key=lambda k: (k["anim"], k["dir"], k["index"]))
    manifest.sort(key=lambda e: (e["keys"][0]["anim"], e["keys"][0]["dir"], e["keys"][0]["index"]))
    hand_frames.place(out, manifest)                          # reviewed hand frames (set 159) win over the bolts
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="ascii")
    return manifest


def run_all(art: Path = ART) -> None:
    for name, (body, idle, layout) in OUTPUTS.items():
        man = aura_folder(art / body, art / name, idle, name, layout)
        print(f"{name}: {len(man)} frames, {sum(len(e['keys']) for e in man)} keys")
    for name, (body, idle, layout, tag, ring) in V4_OUTPUTS.items():
        man = aura_folder(art / body, art / name, idle, tag, layout, art / ring)
        print(f"{name}: {len(man)} frames, {sum(len(e['keys']) for e in man)} keys")


def main(argv: list) -> int:
    if argv == ["all"]:
        run_all()
        return 0
    if argv == ["reference"]:
        for d, diffs in reference_compare().items():
            print(f"d{d}: differing pixels per GIF frame {diffs}")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
