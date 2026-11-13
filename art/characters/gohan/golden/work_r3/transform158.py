# Set 158 anim 9 (the Super Saiyan to Super Saiyan 2 step): frames 1-3 get the golden SSJ2 head.
# Frame content moves down 1 row (dy -1, so the body stays put) to fit the taller head; the golden head
# (rows 0-16, front d0) goes on 1 px right; the game's face (closed eyes, mouth shaded for the head tilted
# back) stays. Frame 1 hair gets the flash colors.
# The flash ring around the head is redrawn in each frame's own ring colors. Frame 0 (start, SSJ hair) stays.
# Output: scratch\art\gi_ssj_v2\ (copy of gi_ssj plus the 3 frames). The source set is not touched.
import sys; print(r'promoted to scripts\permanent\gi_post.py'); sys.exit(1)   # exit guard: a run here would write stale output
import json, shutil, sys
from pathlib import Path
from PIL import Image
ART = Path(__file__).resolve().parents[2]
SRC, OUT, GOLD = ART / "gi_ssj", ART / "gi_ssj_v2", ART / "golden"
HEAD_ROWS = 17
FACE_ROWS, FACE_X = range(14, 17), range(10, 23)          # shifted rows: closed eyes, brows (game face)
FACE = {20, 21, 23, 113, 114, 115, 116, 117}
FLASH = {46: 37, 37: 2, 38: 46, 39: 46, 44: 37}                     # frame 1: fills one step brighter
SWAY_ROWS = 13                                                        # hair rows above the forehead lean
FRAMES = {"frame_2B1D0C.png": (FLASH, (120,), -2),                    # index 1: 1 px ring 120, tips lean left
          "frame_2B1E50.png": ({}, (46, 38), 0),                      # index 2: inner 46, outer 38, upright
          "frame_2B1FB0.png": ({}, (37, 120), 2)}                     # index 3: inner 37, outer 120, lean right

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
gold = Image.open(GOLD / "golden_gi_ssj2_d0.png")
gb = gold.tobytes()
man = json.loads((OUT / "manifest.json").read_text())
for e in man:
    if e["png"] not in FRAMES:
        continue
    recolor, ring, lean = FRAMES[e["png"]]
    img = Image.open(SRC / e["png"])
    src = img.tobytes()
    px = bytearray(32 * 32)
    for y in range(31):                                              # down 1 row; row 31 of the source is empty
        px[(y + 1) * 32:(y + 2) * 32] = src[y * 32:(y + 1) * 32]
    assert not any(src[31 * 32:]), e["png"]
    px[:HEAD_ROWS * 32] = bytes(HEAD_ROWS * 32)
    for y in range(HEAD_ROWS):
        for x in range(31):
            k = gb[y * 32 + x]
            if k:
                px[y * 32 + x + 1] = recolor.get(k, k)
    for y in range(SWAY_ROWS):                                       # shear: the top row moves the most
        dx = round(lean * (SWAY_ROWS - y) / SWAY_ROWS)
        row = px[y * 32:(y + 1) * 32]
        px[y * 32:(y + 1) * 32] = bytes(row[x - dx] if 0 <= x - dx < 32 else 0 for x in range(32))
    for y in FACE_ROWS:                                              # the game's strained face, head tilted back
        for x in FACE_X:
            k = src[(y - 1) * 32 + x]
            if k in FACE:
                px[y * 32 + x] = k
    for color in ring:                                               # one outside ring layer per color
        outside, todo = set(), [(x, y) for x in range(32) for y in (0, 31)] + [(x, y) for y in range(32) for x in (0, 31)]
        while todo:                                                  # flood from the border: gaps between spikes stay open
            x, y = todo.pop()
            if 0 <= x < 32 and 0 <= y < 32 and (x, y) not in outside and px[y * 32 + x] == 0:
                outside.add((x, y))
                todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        layer = [(x, y) for x, y in outside if y <= HEAD_ROWS and any(
            0 <= x + a < 32 and 0 <= y + b < 32 and px[(y + b) * 32 + x + a] and (x + a, y + b) not in outside
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        for x, y in layer:
            px[y * 32 + x] = color
    out = Image.frombytes("P", (32, 32), bytes(px))
    out.putpalette(img.getpalette())
    out.info["transparency"] = 0
    out.save(OUT / e["png"], transparency=0)
    for k in e["keys"]:
        k["dy"] -= 1
    e.setdefault("notes", []).append("SSJ2 golden head (transform158.py), dy -1")
# Owner 10:24 PM, index 3 matches indices 1-2: belt back up (rows 23-25 from index 2 in index 3's ring
# colors) and skin, not brown, between the eyes.
two = Image.open(OUT / "frame_2B1E50.png").tobytes()
three_img = Image.open(OUT / "frame_2B1FB0.png")
three = bytearray(three_img.tobytes())
RING_2_TO_3 = {46: 37, 38: 120}
for y in (23, 24, 25):
    three[y * 32:(y + 1) * 32] = bytes(RING_2_TO_3.get(k, k) for k in two[y * 32:(y + 1) * 32])
three[14 * 32 + 16] = 115
fixed = Image.frombytes("P", (32, 32), bytes(three))
fixed.putpalette(three_img.getpalette())
fixed.save(OUT / "frame_2B1FB0.png", transparency=0)
(OUT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n", newline="\n")
print("written", OUT)
