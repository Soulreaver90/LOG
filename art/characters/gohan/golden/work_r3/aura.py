# Blue lightning aura on set 159 (gi SSJ2): the 3 approved overlays (arcs, bolts, crackle, lifted from the
# golden d0 lightning drafts: index 191 plus the white cores unique to each draft) cycle by frame index
# on the stand, walk, idle and run anims, placed by each frame's body centre and feet. Sparks only fill
# transparent pixels, so the body always wins.
# Output: scratch\art\gi_ssj2_v3\ (copy of gi_ssj2_v2 plus the overlays). The source set is not touched.
import json, shutil
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
SRC, OUT, GOLD = ART / "gi_ssj2_v2", ART / "gi_ssj2_v3", ART / "golden"
ANIMS = {0, 1, 4, 13}                                   # stand, walk, idle variant, run
NAMES = ("arcs", "bolts", "crackle")
SPARK, CORE = 191, 2

drafts = {n: Image.open(GOLD / f"golden_gi_ssj2_d0_lightning_{n}.png").tobytes() for n in NAMES}
common = {i for i in range(1024) if len({drafts[n][i] for n in NAMES}) == 1}
OVER = [{i: b[i] for i in range(1024) if b[i] == SPARK or (b[i] == CORE and i not in common)}
        for b in (drafts[n] for n in NAMES)]



def anchor(b):
    """(body centre x, feet row) of a 32x32 frame: the overlay follows the body, not the frame box."""
    xs = [i % 32 for i in range(1024) if b[i] and b[i] not in (SPARK,)]
    ys = [i // 32 for i in range(1024) if b[i] and b[i] not in (SPARK,)]
    return (min(xs) + max(xs)) // 2, max(ys)


BASE = anchor(Image.open(GOLD / "golden_gi_ssj2_d0.png").tobytes())

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
man = json.loads((OUT / "manifest.json").read_text())
done, skipped = 0, []
for e in man:
    keys = [k for k in e["keys"] if k["anim"] in ANIMS]
    if not keys:
        continue
    if (e["w"], e["h"]) != (32, 32):
        skipped.append(e["png"])
        continue
    k = min(keys, key=lambda k: (k["anim"], k["dir"], k["index"]))
    img = Image.open(OUT / e["png"])
    px = bytearray(img.tobytes())
    cx, fy = anchor(px)
    ox, oy = cx - BASE[0], fy - BASE[1]
    for i, v in OVER[k["index"] % 3].items():
        x, y = i % 32 + ox, i // 32 + oy
        if 0 <= x < 32 and 0 <= y < 32 and px[y * 32 + x] == 0:
            px[y * 32 + x] = v
    out = Image.frombytes("P", (32, 32), bytes(px))
    out.putpalette(img.getpalette())
    out.save(OUT / e["png"], transparency=0)
    e.setdefault("notes", []).append(f"aura {NAMES[k['index'] % 3]} (aura.py)")
    done += 1
(OUT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", newline="\n")
print("frames with aura", done, "skipped (not 32x32)", skipped)
