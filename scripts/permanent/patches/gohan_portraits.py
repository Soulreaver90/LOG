r"""
gohan_portraits.py - Patch: gi portraits for playable Gohan in base form, Super Saiyan and Super Saiyan 2 (Task 7).

Usage:   py -3 -I scripts\permanent\patches\gohan_portraits.py art      (from the LOG root: makes the PNGs)
         py -3 -I scripts\permanent\log2_build.py --out builds\log2_poc.gba gohan_gi ssj2_form gohan_portraits
Input:   art: data\reference\122601.png (read only), art\portrait-sources\src\gi_base_dialog_src.png (read only)
         and the base ROM palettes. apply: art\portrait-sources\*.png and alloc.notes["ssj2_form"] (the
         relocated appearance table).
Output:  art: art\portrait-sources\<name>_dialog.png, <name>_status.png (indexed, ROM palette), manifest.json,
         art\portraits_review.png. apply: file offsets in alloc.notes["gohan_portraits"].
API:     make_art(base_rom) -> manifest    convert(base_rom, cell_rgb, recolor) -> (dialog, status, report)
         form_art(base_rom, name) -> (dialog, status, report, source rgb)
         load_art(name) -> (dialog bytes, status bytes)    apply(rom, alloc) -> None
Method:  1. Sources: 122601.png row 1, column 4 (Super Saiyan, purple gi) and column 5 (Super Saiyan 2). The base
            gi (entry 2) has no sheet cell: its dialog art is approved drawing
            art\portrait-sources\src\gi_base_dialog_src.png, indices as drawn (source art, never regenerated).
         2. Dialog version (appearance +2, OBJ VRAM): each sheet color to an OBJ palette index that a USA dialog
            portrait (ids 26-114) already uses; exact color first, then nearest. Never index 0 or 168. Then the
            per-form RECOLOR map moves gi indices to Piccolo's gi colors: body 97 (88,0,120), lit folds 233
            (168,32,224). Piccolo's portrait (id 94) draws his gi with them. gi_ssj: 96 to 97. gi_ssj2: 80 to
            233 and 215 to 97.
         3. Status version (appearance +3, BG): each recolored dialog index to the status index the game itself
            pairs it with (the 18 appearance +2/+3 pairs), else the nearest status index ids 8-25 use. The game
            pairs 97 to status 232 and 233 to 234, so the gi status uses 232 and 234.
         4. Copy the portrait table block (rom:0x3EC9D0, struct word + ids 0-114) to the expansion area, add ids
            115-120 as raw type 0 frames, point rom:0xBE10 at the copy, and set +2/+3 of entries 5, 22 and 2 in
            the relocated appearance table.
Rules:   Source: docs\research\re-portraits.md. No palette is written. Every site is checked against its old bytes first.
         Old ids 0-114 are copied unchanged. Cutscenes pass raw speaker ids (59 = armor), so this patch alone
         keeps them armor; patches.cutscene_portraits maps them by Gohan's appearance entry.
         New ids follow FORMS order: gi_ssj 115/116, gi_ssj2 117/118, gi_base 119/120.
"""
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # isolated mode (-I) drops the script folder

import log_paths  # noqa: E402
from rom.webfoot_decompress import ROM_BASE, unpack_frame  # noqa: E402

# ===== constants =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
REFERENCE = ROOT / "data" / "reference" / "122601.png"
ART = log_paths.PORTRAIT_SOURCES
REVIEW = log_paths.ART / "portraits_review.png"

PORTRAIT_LITERAL = 0xBE10                    # pool of portrait() @0x0800BDCC, the block's only reference
BLOCK, STRUCT_WORD = 0x3EC9D0, 0x03000E90    # word 0 (read for ids 1-7), then ids 0-114
OLD_IDS, END_WORD = 115, 0x03001120          # rom:0x3ECBA0 holds END_WORD: the table cannot grow in place
SIDE, SIZE = 64, 0x1000                      # 64x64, 8bpp, row order
OBJ_PAL, STATUS_PAL = 0x1DA6C8, 0x1D4F50
DIALOG_IDS, STATUS_IDS = range(26, OLD_IDS), range(8, 26)
NEVER = {0, 168}                             # transparent; set at run time (RE-BIBLE section 5)
BASE_SRC = ART / "src" / "gi_base_dialog_src.png"      # approved drawing: source art, never regenerated
APPEARANCE, ENTRY, ENTRIES = 0x1D967C, 20, 22
PLUS2_LITERAL, PLUS3_LITERAL = 0x26458, 0x3B30   # @0x08026440 (+2) and @0x08003A8C (+3) table pools
CELL = (4, 4, 68)                            # 122601.png: cell x = 4 + 68 * col, y = 4 + 68 * row
MIN_VOTES = 4                                # a game pairing below this many pixels is noise
# Piccolo's gi (portrait id 94): body OBJ 97, lit folds 233. The game pairs 97 to status 232, 233 to 234.
RECOLOR_SSJ, RECOLOR_SSJ2 = {96: 97}, {80: 233, 215: 97}
# name: (source, appearance entry, old +2/+3 (the armor portraits), new +2/+3, dialog recolor)
# source: (sheet column, row) in 122601.png, or the drawn PNG whose pixels are dialog indices
FORMS = {
    "gi_ssj":  ((4, 1), 5, (0x3E, 0x0D), (115, 116), RECOLOR_SSJ),
    "gi_ssj2": ((5, 1), 22, (0x3D, 0x0C), (117, 118), RECOLOR_SSJ2),
    "gi_base": (BASE_SRC, 2, (0x3B, 0x0A), (119, 120), {}),
}


# ===== ROM readers =====

def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def palette(rom: bytes, off: int) -> list:
    return [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)
            for c in struct.unpack_from("<256H", rom, off)]


def portrait(rom: bytes, pid: int, block: int = BLOCK) -> bytes:
    """Pixels of portrait id pid (> 7) read through a table block like the one at rom:0x3EC9D0."""
    hdr = u32(rom, block + 4 + 4 * pid) - ROM_BASE
    data = unpack_frame(rom, hdr)[2]
    if len(data) != SIZE:
        raise ValueError(f"portrait {pid} unpacked to {len(data)} bytes")
    return data


def pairs(rom: bytes) -> list:
    """(+2 dialog id, +3 status id) of every vanilla appearance entry."""
    return [tuple(rom[APPEARANCE + ENTRY * e + 2:APPEARANCE + ENTRY * e + 4]) for e in range(ENTRIES)]


# ===== conversion =====

def _nearest(rgb: tuple, pal: list, allowed: set, use: Counter) -> int:
    return min(allowed, key=lambda k: (sum((a - b) ** 2 for a, b in zip(rgb, pal[k])), -use[k], k))


def _error(a: tuple, b: tuple) -> int:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _use(rom: bytes) -> tuple:
    use_obj, use_stat = Counter(), Counter()
    for pid in DIALOG_IDS:
        use_obj.update(portrait(rom, pid))
    for pid in STATUS_IDS:
        use_stat.update(portrait(rom, pid))
    return use_obj, use_stat


def _status_of(rom: bytes, dialog: bytes) -> tuple:
    """(status pixels, {dialog index: status index}, {dialog index: rule}) through the game's +2/+3 pairing."""
    obj, stat = palette(rom, OBJ_PAL), palette(rom, STATUS_PAL)
    _, use_stat = _use(rom)
    ok_stat = set(use_stat) - NEVER
    votes = defaultdict(Counter)
    for d, s in pairs(rom):
        for a, b in zip(portrait(rom, d), portrait(rom, s)):
            votes[a][b] += 1
    to_stat, how = {}, {}
    for k in set(dialog):
        best = votes[k].most_common(1)
        if best and best[0][1] >= MIN_VOTES and best[0][0] in ok_stat:
            to_stat[k], how[k] = best[0][0], "game pair"
        else:
            to_stat[k], how[k] = _nearest(obj[k], stat, ok_stat, use_stat), "nearest"
    return bytes(to_stat[k] for k in dialog), to_stat, how


def _report(rom: bytes, cell: list, dialog: bytes) -> list:
    obj, stat = palette(rom, OBJ_PAL), palette(rom, STATUS_PAL)
    status, to_stat, how = _status_of(rom, dialog)
    counts = Counter(zip(cell, dialog))
    return [{"rgb": list(rgb), "pixels": n, "dialog": k, "dialog_err": _error(rgb, obj[k]),
             "status": to_stat[k], "status_err": _error(rgb, stat[to_stat[k]]), "status_by": how[k]}
            for (rgb, k), n in sorted(counts.items(), key=lambda x: -x[1])]


def convert(rom: bytes, cell: list, recolor: dict = None) -> tuple:
    """(dialog pixels, status pixels, report) for 64x64 RGB pixels. Deterministic.

    recolor maps a dialog index to another one after the nearest-color step. The status follows the recolored dialog.
    """
    recolor = recolor or {}
    obj = palette(rom, OBJ_PAL)
    use_obj, _ = _use(rom)
    ok_obj = set(use_obj) - NEVER
    to_obj = {rgb: _nearest(rgb, obj, ok_obj, use_obj) for rgb in set(cell)}
    dialog = bytes(recolor.get(to_obj[p], to_obj[p]) for p in cell)
    return dialog, _status_of(rom, dialog)[0], _report(rom, cell, dialog)


def drawn(rom: bytes, path: Path) -> tuple:
    """(dialog pixels, status pixels, report) of a drawn 64x64 indexed PNG whose pixels are dialog indices."""
    with Image.open(path) as img:
        if img.mode != "P" or img.size != (SIDE, SIDE):
            raise ValueError(f"{path.name} must be a {SIDE}x{SIDE} indexed PNG")
        dialog = img.tobytes()
    obj = palette(rom, OBJ_PAL)
    return dialog, _status_of(rom, dialog)[0], _report(rom, [obj[k] for k in dialog], dialog)


def form_art(rom: bytes, name: str) -> tuple:
    """(dialog, status, report, source RGB pixels) of a form: a converted sheet cell or a drawn PNG."""
    source, recolor = FORMS[name][0], FORMS[name][4]
    if isinstance(source, Path):
        dialog, status, report = drawn(rom, source)
        obj = palette(rom, OBJ_PAL)
        return dialog, status, report, [obj[k] for k in dialog]
    cell = cell_pixels(*source)
    return (*convert(rom, cell, recolor), cell)


def cell_pixels(col: int, row: int) -> list:
    x, y = CELL[0] + CELL[2] * col, CELL[1] + CELL[2] * row
    with Image.open(REFERENCE) as img:
        return list(img.convert("RGB").crop((x, y, x + SIDE, y + SIDE)).get_flattened_data())


def _indexed(px: bytes, pal: list) -> Image.Image:
    img = Image.frombytes("P", (SIDE, SIDE), px)
    img.putpalette([c for rgb in pal for c in rgb])
    return img


def load_art(name: str) -> tuple:
    """(dialog pixels, status pixels) from the PNGs that make_art wrote."""
    out = []
    for kind in ("dialog", "status"):
        with Image.open(ART / f"{name}_{kind}.png") as img:
            if img.mode != "P" or img.size != (SIDE, SIDE):
                raise ValueError(f"{name}_{kind}.png must be a {SIDE}x{SIDE} indexed PNG")
            out.append(img.tobytes())
    return tuple(out)


def make_art(rom: bytes) -> dict:
    ART.mkdir(parents=True, exist_ok=True)
    obj, stat = palette(rom, OBJ_PAL), palette(rom, STATUS_PAL)
    manifest = {}
    rows = []
    for name, (source, entry, old, new, recolor) in FORMS.items():
        dialog, status, report, cell = form_art(rom, name)
        _indexed(dialog, obj).save(ART / f"{name}_dialog.png")
        _indexed(status, stat).save(ART / f"{name}_status.png")
        where = f"122601.png row {source[1]} column {source[0]}" if isinstance(source, tuple) else \
            f"drawn art {source.name}"
        manifest[name] = {"source": where, "recolor": {str(k): v for k, v in recolor.items()}, "entry": entry,
                          "old_ids": list(old), "new_ids": list(new),
                          "max_dialog_err": max(c["dialog_err"] for c in report),
                          "max_status_err": max(c["status_err"] for c in report), "colors": report}
        src = Image.new("RGB", (SIDE, SIDE))
        src.putdata(cell)
        rows.append((f"{name} dialog: new id {new[0]} | armor id {old[0]} | source", _indexed(dialog, obj),
                     _indexed(portrait(rom, old[0]), obj), src))
        rows.append((f"{name} status: new id {new[1]} | armor id {old[1]} | source", _indexed(status, stat),
                     _indexed(portrait(rom, old[1]), stat), src))
    (ART / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="ascii", newline="\n")
    _review(rows)
    return manifest


def _review(rows: list) -> None:
    scale, pad, label = 4, 8, 16
    w = 3 * SIDE * scale + 4 * pad
    sheet = Image.new("RGB", (w, len(rows) * (SIDE * scale + label + pad) + pad), (48, 48, 48))
    draw = ImageDraw.Draw(sheet)
    for i, (text, *imgs) in enumerate(rows):
        y = pad + i * (SIDE * scale + label + pad)
        draw.text((pad, y), text, fill=(255, 255, 255))
        for j, img in enumerate(imgs):
            sheet.paste(img.convert("RGB").resize((SIDE * scale, SIDE * scale), Image.NEAREST),
                        (pad + j * (SIDE * scale + pad), y + label))
    sheet.save(REVIEW)


# ===== patch =====

def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def apply(rom: bytearray, alloc) -> None:
    if "ssj2_form" not in alloc.notes:                              # entry 22 lives in the ssj2_form table
        raise ValueError("gohan_portraits needs the ssj2_form notes: run ssj2_form first")
    table = alloc.notes["ssj2_form"]["table"]
    _expect(rom, PORTRAIT_LITERAL, _word(BLOCK + ROM_BASE))
    _expect(rom, BLOCK, _word(STRUCT_WORD))
    _expect(rom, BLOCK + 4 + 4 * OLD_IDS, _word(END_WORD))
    for off in (PLUS2_LITERAL, PLUS3_LITERAL):
        _expect(rom, off, _word(table + ROM_BASE))
    for _, entry, old, *_ in FORMS.values():
        _expect(rom, table + ENTRY * entry + 2, bytes(old))
    ok_obj = {k for pid in DIALOG_IDS for k in portrait(rom, pid)} - NEVER
    ok_stat = {k for pid in STATUS_IDS for k in portrait(rom, pid)} - NEVER
    art = {name: load_art(name) for name in FORMS}
    for name, (dialog, status) in art.items():
        if set(dialog) - ok_obj or set(status) - ok_stat:
            raise ValueError(f"{name}: an index outside the colors the game uses for portraits")

    ids = [pid for _, _, _, new, _ in FORMS.values() for pid in new]
    if ids != list(range(OLD_IDS, OLD_IDS + len(ids))):
        raise ValueError(f"new ids must follow id {OLD_IDS - 1} in order: {ids}")
    block = alloc.alloc(4 + 4 * (OLD_IDS + len(ids)))
    rom[block:block + 4 + 4 * OLD_IDS] = rom[BLOCK:BLOCK + 4 + 4 * OLD_IDS]
    frames = {}
    for name, (_, entry, _, new, _) in FORMS.items():
        for pid, px in zip(new, art[name]):
            hdr = alloc.alloc(8 + SIZE)
            rom[hdr:hdr + 8 + SIZE] = _word(0) + _word(SIZE) + px      # raw type 0 (@0x0801F394)
            rom[block + 4 + 4 * pid:block + 8 + 4 * pid] = _word(hdr + ROM_BASE)
            frames[pid] = hdr
        rom[table + ENTRY * entry + 2:table + ENTRY * entry + 4] = bytes(new)
    rom[PORTRAIT_LITERAL:PORTRAIT_LITERAL + 4] = _word(block + ROM_BASE)
    alloc.notes["gohan_portraits"] = {"block": block, "frames": frames}


if __name__ == "__main__":
    if sys.argv[1:] != ["art"]:
        sys.exit(__doc__)
    for form, m in make_art(BASE.read_bytes()).items():
        print(f"{form}: ids {m['new_ids']} max error dialog {m['max_dialog_err']} status {m['max_status_err']}")
    print(f"review sheet {REVIEW}")
