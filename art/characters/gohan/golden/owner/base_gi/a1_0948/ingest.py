# Owner a1 d0 edits (2026-10-18 9:48 AM, 3x RGBA 96x96): to 1x indices, aligned to the r10 gi frames, diffed vs gi and armor.
import sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / "scripts" / "permanent"))
from log2_sprites import PALETTE_OFF
HERE = Path(__file__).parent
F = ROOT / "scratch" / "art" / "review" / "frames_r10"
rom = (ROOT / "scratch" / "build" / "log2_poc_r10.gba").read_bytes()
pal = {}
for i in range(1, 256):
    c = int.from_bytes(rom[PALETTE_OFF + 2 * i:PALETTE_OFF + 2 * i + 2], "little")
    pal.setdefault(((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3), i)
def to_idx(path):
    im = Image.open(path).convert("RGBA").resize((32, 32), Image.NEAREST)
    out, off = [], set()
    for (r, g, b, a) in im.getdata():
        if a < 128: out.append(0); continue
        k = (r & 0xF8, g & 0xF8, b & 0xF8)
        if k not in pal:
            off.add(k); k = min(pal, key=lambda p: sum((x - y) ** 2 for x, y in zip(p, k)))
        out.append(pal[k])
    return out, off
def grid(px, w):
    return {(i % w, i // w): v for i, v in enumerate(px) if v}
for i, n in enumerate((62, 63, 64, 65)):
    own, off = to_idx(HERE / f"{n}.png")
    O = grid(own, 32)
    mine = Image.open(F / "gi_base_157" / f"157_a01_d0_i{i}.png"); arm = Image.open(F / "armor_56" / f"56_a01_d0_i{i}.png")
    M = grid(mine.tobytes(), mine.width); A = grid(arm.tobytes(), arm.width)
    best = min(((sum(1 for p in set(O) | {(x + dx, y + dy) for x, y in M} if O.get(p) != M.get((p[0] - dx, p[1] - dy))), dx, dy)
                for dx in range(-2, 20) for dy in range(-3, 4)))
    d, dx, dy = best
    print(f"\n== a1 d0 i{i} (owner {n}.png) off-palette {off or 'none'} align dx={dx} dy={dy} diffs={d}")
    for (x, y) in sorted(set(O) | {(x + dx, y + dy) for x, y in M}, key=lambda p: (p[1], p[0])):
        o, m, a = O.get((x, y), 0), M.get((x - dx, y - dy), 0), A.get((x - dx, y - dy), 0)
        if o != m: print(f"  row {y - dy:2d} x {x - dx:2d}: gi {m:3d} -> owner {o:3d}   (armor {a:3d})")
    Image.frombytes("P", (32, 32), bytes(own)).save(HERE / f"owner_a01_d0_i{i}_32.png")
