# Body rules from the owner's golden edits, applied to every gi_ssj2_v2 frame:
#   Both rules apply to front and back views only (side legs and arms overlap the torso).
#   R1 crotch: on the first row of the gap between the legs, the gi pixels on both sides of the gap become 211.
#   R2 arm line: a gi pixel beside the arm outline (23) on its row becomes 211, from 2 rows below the gi top
#      (the collar rows touch the neck outline, not an arm).
# Test: the rules must not change any golden frame; if they do, they contradict the owner and are not applied.
import sys; print(r'promoted to scripts\permanent\gi_post.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json, sys
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
V2, GOLD = ART / "gi_ssj2_v2", ART / "golden"
GI, LINE, ARM = {88, 89}, 211, 23


def rules(img, front_back=True):
    w, h = img.size; b = bytearray(img.tobytes()); src = bytes(b); n = 0
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
                r2 = y >= gi_top + 2 and (at(x - 1, y) == ARM or at(x + 1, y) == ARM)
                if r1 or r2:
                    b[y * w + x] = LINE; n += 1
    out = Image.frombytes("P", img.size, bytes(b)); out.putpalette(img.getpalette()); return out, n


bad = {d: rules(Image.open(GOLD / f"golden_gi_ssj2_d{d}.png"), d in (0, 1))[1] for d in (0, 1, 2, 3)}
print("golden changes per rule set (must be 0):", bad)
if "--apply" in sys.argv and not any(bad.values()):
    tot = 0; view = {r["png"]: r["dir"] for r in json.loads((V2 / "transplant.json").read_text())}
    for p in sorted(V2.glob("frame_*.png")):
        out, n = rules(Image.open(p), view.get(p.name) in (0, 1)); tot += n
        if n:
            out.save(p, transparency=0)
    print("frames fixed, pixels changed:", tot)
