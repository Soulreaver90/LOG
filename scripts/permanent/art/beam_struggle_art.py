r"""
beam_struggle_art.py - The beam struggle mockup v2 art (approved 2026-10-25 4:22 PM: "Go with the map tiles"),
                       made again from the Buu's Fury ROM for patches.beam_struggle.

Usage:   from art import beam_struggle_art as art    a = art.build(log2_rom)    (scripts\permanent on sys.path)
API:     build(rom) -> dict: frames (144 dicts world (x, y) -> LoG II BG index), cells (sorted world cells),
         tiles {cell: [144 x 64 B]}, remap, dim, bright. bf_screen(bf) -> {(x, y): BF index} of the 240x160 BF
         intro screen. load_bf() -> the BF ROM bytes (SHA-1 checked). flips(tile) -> [same, h, v, h+v].
Source:  a port of scripts\one-time\2026-10-25-beam-mockup\ (sphere_frames.py cut_remap and ramp_maps; mockup_v2.py
         templates, beams, frame_art and the count cell rule), with the BF screen read from the BF ROM instead of the
         study render bf_map3_bg3.png. scripts\one-time\2026-10-25-beam-trial\bridge.py proves both give the same
         frames, cell for cell. Every constant below is the mockup's.
Method:  1. BF map 3 layout 0x082B5E94, BG3 record (+0x20) 0x082B5E5C: tile list +0x48 (delta coded), chunk table
            +0x4C, one 32x32 block, GBA text entries; screen = layer pixels 0-239 x 0-159. BF BG palette rom:0x5632C.
         2. Cut the light BF indices in BF x 64-177, trim the beam tips, map each BF colour to the nearest LoG II BG
            index 1-255 (rom:0x1DA4C8), place at world = BF + (315, 280).
         3. 144 frames of 5 ticks: pulse 0-1-2-1, 8 orb rays, the -3..+3 px sway (beam body runs under the
            sphere), 3 soft flashes with a halo ring. Cell bytes = art pixel, else 0.
         4. v2: the sphere is the disk minus the two BF orbs that cross its edge (SLICED_ORBS), a clean cut.
Rules:   Pure function of the two ROMs: lists and sorted keys only, no set or dict order places data.
"""
import hashlib
import math
import struct
from pathlib import Path

from rom.webfoot_decompress import unpack_frame

# ===== sources =====
ROM_BASE = 0x08000000
BF_PATH = Path(__file__).resolve().parents[3] / "data" / "roms" / "Dragon Ball Z - Buu's Fury (USA).gba"
BF_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"
BF_LAYOUT, BF_BG3_REC, BF_FACTORY, BF_BG_PAL = 0x082B5E94, 0x082B5E5C, 0x08008087, 0x5632C
LOG2_BG_PAL = 0x1DA4C8
SCREEN = (240, 160)

# ===== cut and colours (sphere_frames.py) =====
LIGHT = sorted({2, 9, 10, 11, 12, 48, 50, 51, 54, 55, 56, 72, 73, 74, 80, 81, 82} | set(range(166, 197)))
TRIM_IDX, TRIM_Y = (9, 10, 11, 12, 166), (100, 115)
CUT_X = (64, 178)
OFFSET = (315, 280)
CANDIDATES = [2, 9, 10, 11, 12, 45, 52, 66, 67, 72, 73, 74, 143, 148, 149, 153, 154, 159,
              164, 169, 181, 184, 187, 193, 198, 214]
MAX_STEP = 60

# ===== motion (mockup_v2.py) =====
CX, CY = 128, 108                       # BF sphere centre; world (443, 388)
DISK_R = 25
STEP, NFRAMES = 5, 144                  # 5 ticks a frame, 12 s a cycle
PULSE_SEQ = (0, 1, 2, 1)                # dim, normal, bright, normal; 2 frames (10 ticks) a step
RAYS = (45, 75, 105, 135, 225, 255, 285, 315)          # degrees, counterclockwise from +x
PHASES = (0, 5, 2, 7, 4, 1, 6, 3)
R_AGE = (16, 24, 32, 39, 45, 50, 54, 57)
SIZE_AGE = ("L", "L", "L", "M", "M", "S", "S", "T")
DIM_AGE = (0, 0, 0, 0, 0, 0, 1, 2)
SWAY = ((0, 4), (1, 3), (2, 5), (3, 4), (2, 2), (1, 3), (0, 2), (-1, 3), (-2, 6), (-1, 2), (-2, 3), (-3, 4),
        (-2, 3), (-1, 2), (0, 5), (1, 2), (2, 4), (1, 3), (0, 3), (-1, 4), (0, 2), (1, 5), (2, 3), (3, 3),
        (2, 4), (3, 2), (2, 3), (1, 4), (0, 3), (-1, 2), (-2, 4), (-3, 3), (-2, 5), (-1, 3), (0, 2), (1, 3),
        (0, 4), (-1, 3), (0, 2), (1, 4), (2, 3), (1, 4), (0, 6))          # (offset px, hold frames)
FLASH_STARTS = (26, 66, 112)
HALO = ((26.5, 2), (27.5, 72))          # (outer radius, index): white inner ring, blue-white outer
BEAM_ROWS, TIP_ROWS = (105, 110), (102, 113)
TIP_LEFT, TIP_RIGHT = 81, 168
# v2 (final, 2026-10-25 6:40 PM, "it should be a clean cut of the center orb"): the two 13 px BF orbs that cross the
# disk edge (BF rows 85-97 x 144-156, rows 120-132 x 97-110; orb_find and sphere_cut_view in the beam-trial folder).
# No pixel within ORB_CUT_R of their centres joins the sphere, so no slice of either orb stays on it.
SLICED_ORBS = ((150, 91), (103.5, 126))
ORB_CUT_R = 7


# ===== ROM readers =====

def load_bf() -> bytes:
    bf = BF_PATH.read_bytes()
    if hashlib.sha1(bf).hexdigest() != BF_SHA1:
        raise ValueError(f"{BF_PATH.name}: SHA-1 is not {BF_SHA1}")
    return bf


def _u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE)[0]


def _frame(rom: bytes, a: int) -> bytes:
    return unpack_frame(rom, a - ROM_BASE)[2]


def palette(rom: bytes, off: int) -> list:
    """256 (r, g, b) from BGR555 words, 3 bits shifted in (the mockup's render_map.palette)."""
    return [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)
            for c in struct.unpack_from("<256H", rom, off)]


def layout_tiles(rom: bytes, layout: int) -> list:
    """BG tiles in VRAM order: the layout +0x48 u16 list (e[i] += e[i-1] + 1; high byte = chunk in the +0x4C
    table, low byte = 64 B tile), as the loader @0x080050C8 reads it."""
    raw = _frame(rom, _u32(rom, layout + 0x48))
    idx = list(struct.unpack("<%dH" % (len(raw) // 2), raw))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = _u32(rom, layout + 0x4C), {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = _frame(rom, _u32(rom, table + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def bf_screen(bf: bytes) -> dict:
    """{(x, y): BF index != 0} of BF map 3 BG3, layer pixels 0-239 x 0-159 (the study's bf_map3_bg3.png crop)."""
    if _u32(bf, BF_LAYOUT + 0x20) != BF_BG3_REC or _u32(bf, BF_BG3_REC) != BF_FACTORY:
        raise ValueError("BF map 3 layout or BG3 record is not the one the mockup read")
    tl = layout_tiles(bf, BF_LAYOUT) + [bytes(64)] * 1024
    bx = bf[BF_BG3_REC - ROM_BASE + 0x14]
    px = {}
    for k in range(bx * bf[BF_BG3_REC - ROM_BASE + 0x15]):
        p = _u32(bf, BF_BG3_REC + 0x18 + 4 * k)
        if not p:
            continue
        m = _frame(bf, p)
        ox, oy = (k % bx) * 256, (k // bx) * 256
        for t in range(1024):
            e = struct.unpack_from("<H", m, 2 * t)[0]
            tile = tl[e & 0x3FF]
            for i in range(64):
                sx, sy = i % 8, i // 8
                if e & 0x400:
                    sx = 7 - sx
                if e & 0x800:
                    sy = 7 - sy
                x, y = ox + (t % 32) * 8 + i % 8, oy + (t // 32) * 8 + i // 8
                v = tile[sy * 8 + sx]
                if v and x < SCREEN[0] and y < SCREEN[1]:
                    px[(x, y)] = v
    return px


# ===== cut, trim, remap (sphere_frames.py) =====

def lum(c) -> float:
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def dist(a, b) -> float:
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in range(3)))


def cut_remap(screen: dict, bpal: list, lp: list) -> tuple:
    """({(x, y): LoG II index} in BF coordinates, {BF index: LoG II index})."""
    cut = {}
    for y in range(SCREEN[1]):
        for x in range(*CUT_X):
            v = screen.get((x, y), 0)
            if v not in LIGHT:
                continue
            if v in TRIM_IDX and TRIM_Y[0] <= y <= TRIM_Y[1] and (x <= 72 or x >= 177):
                continue
            cut[(x, y)] = v
    remap = {}
    for v in sorted(set(cut.values())):
        remap[v] = min(range(1, 256), key=lambda j: dist(bpal[v], lp[j]))
    return {k: remap[v] for k, v in cut.items()}, remap


def ramp_maps(used: list, lp: list) -> tuple:
    """One step along the light ramp: dimmer = darker toward the beam blue, brighter = toward white."""
    dim, bright = {}, {}
    for i in used:
        c = lp[i]
        t_dim = (c[0] * 0.80, c[1] * 0.90, c[2] * 1.00)
        t_br = tuple(v + 0.35 * (255 - v) for v in c)
        lower = [j for j in CANDIDATES if lum(lp[j]) < lum(c) - 1]
        upper = [j for j in CANDIDATES if lum(lp[j]) > lum(c) + 1]
        dim[i] = min(lower, key=lambda j: dist(t_dim, lp[j])) if lower else i
        bright[i] = min(upper, key=lambda j: dist(t_br, lp[j])) if upper else i
        if dist(t_dim, lp[dim[i]]) > MAX_STEP:          # no hue jump
            dim[i] = i
        if dist(t_br, lp[bright[i]]) > MAX_STEP:
            bright[i] = i
    return dim, bright


# ===== art pieces (mockup_v2.py) =====

def sway_table() -> list:
    out = []
    for off, hold in SWAY:
        out += [off] * hold
    if len(out) != NFRAMES:
        raise ValueError(f"sway table has {len(out)} frames, not {NFRAMES}")
    return out


def flash_table() -> list:
    out = [0] * NFRAMES
    for s in FLASH_STARTS:
        out[s], out[s + 1], out[s + 2] = 1, 2, 1
    return out


def templates(cut: dict) -> dict:
    """Square index grids: L and S are BF orbs, M and T their nearest-neighbour downscales."""
    big = [[cut.get((130 + i, 68 + j), 0) for i in range(13)] for j in range(13)]
    small = [[cut.get((142 + i, 59 + j), 0) for i in range(6)] for j in range(6)]

    def shrink(t, n):
        src = len(t)
        return [[t[int((j + 0.5) * src / n)][int((i + 0.5) * src / n)] for i in range(n)] for j in range(n)]
    return {"L": big, "M": shrink(big, 9), "S": small, "T": shrink(small, 3)}


def beams(cut: dict) -> dict:
    """Beam pixels with the body continued under the sphere (column pattern from each side)."""
    out = {}
    for (x, y), v in cut.items():
        if (x <= TIP_LEFT or x >= TIP_RIGHT) and TIP_ROWS[0] <= y <= TIP_ROWS[1]:
            out[(x, y)] = v
    for y in range(BEAM_ROWS[0], BEAM_ROWS[1] + 1):
        for x in range(TIP_LEFT + 1, TIP_RIGHT):
            if (x - CX) ** 2 + (y - CY) ** 2 > DISK_R ** 2 and (x, y) in cut:
                out[(x, y)] = cut[(x, y)]
            elif x < CX:
                out[(x, y)] = cut[(86 + (x - 86) % 10, y)]
            else:
                out[(x, y)] = cut[(156 + (x - 156) % 10, y)]
    return out


def in_orb(x: float, y: float) -> bool:
    return any((x - ox) ** 2 + (y - oy) ** 2 <= ORB_CUT_R ** 2 for ox, oy in SLICED_ORBS)


def in_sphere(x: int, y: int) -> bool:
    """A BF pixel the sphere takes: inside the disk and in no sliced orb (v2 clean cut)."""
    return (x - CX) ** 2 + (y - CY) ** 2 <= DISK_R ** 2 and not in_orb(x, y)


def check_sliced_orbs(cut: dict) -> None:
    """Each listed orb is in the cut (most of its circle) and crosses the disk edge, or the list is stale."""
    for ox, oy in SLICED_ORBS:
        circle = [(x, y) for y in range(int(oy) - 7, int(oy) + 8) for x in range(int(ox) - 7, int(ox) + 8)
                  if (x - ox) ** 2 + (y - oy) ** 2 <= 6.5 ** 2]
        present = sum(1 for p in circle if p in cut)
        inside = sum(1 for x, y in circle if (x - CX) ** 2 + (y - CY) ** 2 <= DISK_R ** 2)
        if present < 0.85 * len(circle) or not 0 < inside < len(circle):
            raise ValueError(f"orb at BF {(ox, oy)}: {present} of {len(circle)} px in the cut, {inside} inside the disk")


def frame_art(g: int, cut: dict, dim: dict, bright: dict, tpl: dict, beam: dict, sway: list, flash: list) -> dict:
    """World pixels of BG0 art for frame g: beams, then orbs, then the sphere over them, then the halo."""
    pulse = PULSE_SEQ[(g // 2) % 4]
    fl = flash[g]
    if fl == 2:
        def cmap(v):
            return bright.get(bright.get(v, v), bright.get(v, v))
    elif fl == 1 or pulse == 2:
        def cmap(v):
            return bright.get(v, v)
    elif pulse == 0:
        def cmap(v):
            return dim.get(v, v)
    else:
        def cmap(v):
            return v
    dx = sway[g]
    ox, oy = OFFSET
    art = {(x + ox, y + oy): v for (x, y), v in beam.items()}
    for ray, ph in zip(RAYS, PHASES):                 # orbs first: each comes out from behind the sphere edge
        age = (g - ph) % 8
        a = math.radians(ray)
        px, py = CX + R_AGE[age] * math.cos(a), CY - R_AGE[age] * math.sin(a)
        grid = tpl[SIZE_AGE[age]]
        n = len(grid)
        for j in range(n):
            for i in range(n):
                v = grid[j][i]
                if not v:
                    continue
                for _ in range(DIM_AGE[age]):
                    v = dim.get(v, v)
                art[(round(px - n / 2) + i + ox, round(py - n / 2) + j + oy)] = v
    for (x, y), v in cut.items():
        if in_sphere(x, y):
            art[(x + dx + ox, y + oy)] = cmap(v)
    if fl == 2:
        for j in range(-28, 29):
            for i in range(-28, 29):
                r = math.hypot(i, j)
                for outer, idx in HALO:
                    if outer - 1 < r <= outer:
                        art[(CX + dx + i + ox, CY + j + oy)] = idx
    return art


# ===== cells =====

def flips(b: bytes) -> list:
    """[b, h-flip, v-flip, both] of one 8x8 tile (the GBA map entry bits 10 and 11)."""
    rows = [b[8 * r:8 * r + 8] for r in range(8)]
    h = b"".join(r[::-1] for r in rows)
    v = b"".join(rows[::-1])
    return [b, h, v, b"".join(r[::-1] for r in rows[::-1])]


def cell_tile(art: dict, cx: int, cy: int) -> bytes:
    return bytes(art.get((cx * 8 + k % 8, cy * 8 + k // 8), 0) for k in range(64))


def build(rom: bytes, bf: bytes = None) -> dict:
    bf = load_bf() if bf is None else bf
    lp = palette(rom, LOG2_BG_PAL)
    cut, remap = cut_remap(bf_screen(bf), palette(bf, BF_BG_PAL), lp)
    check_sliced_orbs(cut)
    dim, bright = ramp_maps(sorted(set(cut.values())), lp)
    tpl, beam = templates(cut), beams(cut)
    sway, flash = sway_table(), flash_table()
    frames = [frame_art(g, cut, dim, bright, tpl, beam, sway, flash) for g in range(NFRAMES)]
    cells = sorted({(x // 8, y // 8) for fr in frames for (x, y) in fr})
    tiles = {c: [cell_tile(fr, *c) for fr in frames] for c in cells}
    return {"frames": frames, "cells": cells, "tiles": tiles, "remap": remap, "dim": dim, "bright": bright,
            "cut": cut, "lp": lp}
