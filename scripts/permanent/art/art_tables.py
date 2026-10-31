r"""
art_tables.py - The art tables: dialog portraits (id -> PNG) and OBJ palette entries (index -> color).

Usage:   imported by patches\art_inject.py and inject.py (no command line).
Tables:  art\tables\portraits.json  {"<id>": {"png": "portraits/<file>.png", "note": "..."}}
         art\tables\palette.json    {"<index>": [r, g, b]}  (8-bit channels, each a multiple of 8)
API:     load_portraits(path) / save_portraits(table, path)    load_palette(path) / save_palette(table, path)
         obj_palette(rom, palette=None) -> 256 RGB    allowed_indices(rom, palette) -> set    valid_id(pid)
         to_pixels(img, pal, allowed, snap=False) -> (pixels or None, problems, snapped)    is_canonical(img, ...)
         check_pixels(pid, px, ref, allowed) -> problems    png_pixels(path, pal, allowed) -> pixels
         check_palette_entry(rom, palette, index, rgb) -> (problems, warnings)
         live_frame(rom, block, pid) -> (header offset, pixels)
Rules:   A portrait is 64x64. Each color maps by value to an OBJ index that a USA dialog portrait (ids 26-114)
         uses or that the palette table sets; never 0 or 168. The OBJ palette has no duplicate color, and
         check_palette_entry keeps it so, which makes the map one to one. The outer 3 px ring must equal the
         frame the id had before the table. At most 64 colors (the status_portrait pool).
"""
import json
import struct
from collections import Counter
from pathlib import Path

import log_paths
from rom.webfoot_decompress import ROM_BASE, unpack_frame

# ===== constants =====
ART_DIR = log_paths.ART_TABLES
PORTRAITS_JSON, PALETTE_JSON = ART_DIR / "portraits.json", ART_DIR / "palette.json"
SIDE, SIZE, RING = 64, 0x1000, 3
OBJ_PAL, RGB_TABLE = 0x1DA6C8, 0x3ECBA4         # BGR555 x 256; fade table RGB888 x 512 (OBJ half at +768)
VANILLA_BLOCK = 0x3EC9D0                        # struct word, then ids 0-114 (never written)
DIALOG_IDS, NEVER = range(26, 115), {0, 168}
MAX_ID, STATUS_TWINS = 121, {116, 118, 120}      # npc_gi block holds ids 0-121; twins use the BG palette
MAX_COLORS = 64                                 # status_portrait pool
MAX_LISTED = 10                                 # off-palette colors listed by name
RING_IDX = [y * SIDE + x for y in range(SIDE) for x in range(SIDE) if min(x, y, SIDE - 1 - x, SIDE - 1 - y) < RING]


# ===== tables =====

def load_portraits(path: Path = PORTRAITS_JSON) -> dict:
    return {int(k): v for k, v in json.loads(Path(path).read_text(encoding="utf-8")).items()}


def save_portraits(table: dict, path: Path = PORTRAITS_JSON) -> None:
    _save({str(k): table[k] for k in sorted(table)}, path)


def load_palette(path: Path = PALETTE_JSON) -> dict:
    return {int(k): tuple(v) for k, v in json.loads(Path(path).read_text(encoding="utf-8")).items()}


def save_palette(table: dict, path: Path = PALETTE_JSON) -> None:
    _save({str(k): list(table[k]) for k in sorted(table)}, path)


def _save(data: dict, path: Path) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="ascii", newline="\n")


def valid_id(pid: int) -> bool:
    return pid in DIALOG_IDS or (DIALOG_IDS.stop <= pid <= MAX_ID and pid not in STATUS_TWINS)


# ===== palette =====

def obj_palette(rom: bytes, palette: dict = None) -> list:
    """The OBJ palette as 8-bit RGB (BGR555 << 3), with the palette table entries applied."""
    pal = [((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3) for c in struct.unpack_from("<256H", rom, OBJ_PAL)]
    for k, rgb in (palette or {}).items():
        pal[k] = tuple(rgb)
    return pal


def dialog_indices(rom: bytes) -> set:
    """OBJ indices the USA dialog portraits use, read through the vanilla block (it stays in every build)."""
    used = set()
    for pid in DIALOG_IDS:
        used |= set(unpack_frame(rom, struct.unpack_from("<I", rom, VANILLA_BLOCK + 4 + 4 * pid)[0] - ROM_BASE)[2])
    return used - NEVER


def allowed_indices(rom: bytes, palette: dict) -> set:
    return (dialog_indices(rom) | set(palette)) - NEVER


def check_palette_entry(rom: bytes, palette: dict, index: int, rgb: tuple) -> tuple:
    """(problems, warnings) for a new entry index -> rgb on top of the palette table."""
    problems, warnings = [], []
    if not 1 <= index <= 255 or index in NEVER:
        problems.append(f"index {index}: use 1-255, never 0 (transparent) or 168 (set at run time)")
    if len(rgb) != 3 or any(not 0 <= c <= 255 for c in rgb):
        return problems + [f"color {rgb}: give three channels 0-255"], warnings
    if any(c % 8 for c in rgb):
        problems.append(f"color {tuple(rgb)}: each channel must be a multiple of 8 (BGR555), "
                        f"for example {tuple(c & ~7 for c in rgb)}")
    if problems:
        return problems, warnings
    table = {**palette, index: tuple(rgb)}
    pal = obj_palette(rom, table)
    same = sorted(k for k in allowed_indices(rom, table) if k != index and pal[k] == tuple(rgb))
    if same:
        problems.append(f"color {tuple(rgb)} already belongs to index {same[0]}: "
                        "a portrait color must map to one index")
    if index in dialog_indices(rom):
        warnings.append(f"index {index} is used by vanilla dialog portraits: their colors change too")
    return problems, warnings


# ===== portraits =====

def _lookup(pal: list, allowed: set) -> dict:
    return {pal[k]: k for k in sorted(allowed, reverse=True)}      # lowest index wins (no duplicates expected)


def _nearest(rgb: tuple, pal: list, allowed: set) -> int:
    return min(sorted(allowed), key=lambda k: sum((a - b) ** 2 for a, b in zip(rgb, pal[k])))


def is_canonical(img, pal: list, allowed: set) -> bool:
    """True for a 64x64 indexed PNG whose used indices are allowed and whose palette equals pal at each of them."""
    if img.mode != "P" or img.size != (SIDE, SIDE):
        return False
    ppal = img.getpalette() or []
    return all(k in allowed and tuple(ppal[3 * k:3 * k + 3]) == pal[k] for k in set(img.tobytes()))


def to_pixels(img, pal: list, allowed: set, snap: bool = False) -> tuple:
    """(pixels, problems, snapped) of a PIL image. A canonical indexed PNG keeps its indices; any other image
    maps each color by value. snap maps an off-palette color to the nearest index."""
    if img.size != (SIDE, SIDE):
        return None, [f"size is {img.size[0]}x{img.size[1]}, must be {SIDE}x{SIDE}"], []
    if is_canonical(img, pal, allowed):
        return img.tobytes(), [], []
    rgba = list(img.convert("RGBA").get_flattened_data())
    clear = sum(1 for p in rgba if p[3] != 255)
    if clear:
        return None, [f"{clear} pixels are transparent or partly transparent: use an opaque image"], []
    lookup = _lookup(pal, allowed)
    off = Counter(p[:3] for p in rgba if p[:3] not in lookup)
    near = {c: _nearest(c, pal, allowed) for c in off}
    notes = [f"color {c} x{n} px is not in the OBJ palette; nearest index {near[c]} {pal[near[c]]}"
             for c, n in off.most_common(MAX_LISTED)]
    if len(off) > MAX_LISTED:
        rest = off.most_common()[MAX_LISTED:]
        notes.append(f"{len(rest)} more off-palette colors ({sum(n for _, n in rest)} px)")
    if off and not snap:
        return None, notes, []
    return bytes(lookup.get(p[:3], near.get(p[:3])) for p in rgba), [], notes


def check_pixels(pid: int, px: bytes, ref: bytes, allowed: set) -> list:
    """Problems of portrait pixels for id pid against ref, the frame the id shows without the table (None: skip)."""
    problems = []
    if not valid_id(pid):
        problems.append(f"id {pid}: use a dialog id 26-{MAX_ID} other than the status twins {sorted(STATUS_TWINS)}")
    if len(px) != SIZE:
        return problems + [f"{len(px)} pixels, must be {SIZE}"]
    bad = sorted(set(px) - allowed)
    if bad:
        problems.append(f"indices {bad} are not dialog portrait colors or palette table entries")
    if len(set(px)) > MAX_COLORS:
        problems.append(f"{len(set(px))} colors: the status page pool holds {MAX_COLORS}")
    if ref is not None:
        diff = [i for i in RING_IDX if px[i] != ref[i]]
        if diff:
            problems.append(f"frame (outer {RING} px) differs from id {pid}'s current frame at {len(diff)} of "
                            f"{len(RING_IDX)} px, first at x={diff[0] % SIDE} y={diff[0] // SIDE}")
    return problems


def png_pixels(path: Path, pal: list, allowed: set) -> bytes:
    """Pixels of a table PNG (no snap); raises ValueError with every problem."""
    from PIL import Image
    with Image.open(path) as img:
        px, problems, _ = to_pixels(img, pal, allowed)
    if problems:
        raise ValueError(f"{Path(path).name}: " + "; ".join(problems))
    return px


def live_frame(rom: bytes, block: int, pid: int) -> tuple:
    """(header file offset, pixels) of portrait pid through the block at file offset block."""
    hdr = struct.unpack_from("<I", rom, block + 4 + 4 * pid)[0] - ROM_BASE
    return hdr, unpack_frame(rom, hdr)[2]
