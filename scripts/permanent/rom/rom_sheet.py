r"""
rom_sheet.py - Draw what a built ROM holds for one or more sprite sets: one sheet, one row per (set, anim, dir).

Usage:   py -3 -I scripts\permanent\rom\rom_sheet.py <rom.gba> <set>[,<set>...] <out.png> [--anims 0,1,9] [--dirs 0,1,2,3] [--scale 4] [--gif]
         py -3 -I scripts\permanent\rom\rom_sheet.py <rom.gba> <set>[,<set>...] [<out.png>] --frames <out_dir> [--anims 0,1]
Prints:  per row the frame count, and every record whose w x h is over SLOT_BYTES. Writes out.png (and the GIFs).
         --frames writes every record of each set as its own transparent PNG at 1x and 3x:
         <out_dir>\<set>_a<anim:02>_d<dir>_i<index>.png and ..._3x.png, and prints the count.
API:     live_set_offset(rom, set_id) -> file offset of the set through the table the ROM points at
         row_frames(rom, set_off, anim, dir) -> [(record, tile bytes or None)]
         build_sheet(rom, set_ids, anims, dirs, scale) -> (PIL image, notes)
         row_gif_frames(rom, set_off, anim, dir, scale) -> [PIL image]
         write_frames(rom, set_ids, out_dir, anims) -> [written paths]
Rules:   Set id N resolves through the u32 at rom:0x959C (the table address), entry N - 7. A ROM that moved the
         table (gohan_gi, sets 157-159) resolves through its copy. The base ROM gives the same offsets as SET_TABLE.
         Rows go anim, then dir, then set, so the same anim and dir of each set sit on adjacent rows.
         Every cell has one size and one anchor; each frame sits at its record dx, dy, so an offset jump shows.
         The background is the lime of gi_review (palette index 13 is gray, so gray hides pixels). Color 0 is transparent.
         The palette is the shared OBJ palette of the given ROM. GIF frame time is 150 ms: the real time is not known.
         --frames skips a dir 3 record that reuses the frame header of the dir 2 record of the same index: dir 3 is
         dir 2 drawn with the OBJ h-flip bit (attr1 0x1000), or drawn as is in the front-facing anims (9, 11, 14,
         17, 21). A dir 3 record with its own frame header (anim 20 in sets 56, 59, 157-159) is written. A frame
         PNG is the record's w x h with its flips applied, color 0 transparent, no background and no anchor mark.
Source:  Set layout in docs\research\re-sprite-decompression.md. Reads through log2_sprites and webfoot_decompress. Read-only.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from PIL import Image, ImageDraw

from art.gi_review import BACKGROUND
from rom.log2_sprites import PALETTE_LEN, PALETTE_OFF, SLOT_BYTES, set_records, tiles_to_image
from rom.webfoot_decompress import ROM_BASE, rom_ptr, unpack_frame

# ===== constants =====
TABLE_LITERAL = 0x959C        # u32 at this file offset: GBA address of the set table
FIRST_ID = 7                  # entry 0 of the table is set id 7
LABEL = (0, 0, 0)
GRID = (150, 200, 0)          # cell border, darker than the lime
LABEL_W, TITLE_H, PAD = 120, 14, 4
GIF_MS = 150
FRAME_SCALE = 3               # --frames writes 1x and this scale
MIRROR_DIR, SOURCE_DIR = 3, 2


# ===== set lookup =====

def live_set_offset(rom: bytes, set_id: int) -> int:
    """File offset of set `set_id`, read through the table the ROM points at."""
    table = struct.unpack_from("<I", rom, TABLE_LITERAL)[0] - ROM_BASE
    off = rom_ptr(rom, table + 4 * (set_id - FIRST_ID))
    if off is None:
        raise ValueError(f"set {set_id}: table word at rom:0x{table + 4 * (set_id - FIRST_ID):X} is not a ROM address")
    return off


# ===== frames =====

def row_frames(rom: bytes, set_off: int, anim: int, direction: int) -> list:
    """(record dict, tile bytes) for each frame of one animation direction; tile bytes is None if the frame is unreadable."""
    out = []
    for r in set_records(rom, set_off):
        if r["anim"] == anim and r["dir"] == direction:
            try:
                data = unpack_frame(rom, r["header"])[2]
                data = data if len(data) == r["w"] * r["h"] else None
            except Exception:
                data = None
            out.append((r, data))
    return out


def _sprite(rom: bytes, r: dict, data: bytes):
    img = tiles_to_image(data, r["w"], r["h"], rom[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN]).convert("RGBA")
    if r["attr1"] & 0x1000:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if r["attr1"] & 0x2000:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


def _anchor_box(rom: bytes, set_ids: list, anims, dirs):
    """(min x, min y, width, height) that holds every selected record at its dx, dy."""
    recs = [r for sid in set_ids for r in set_records(rom, live_set_offset(rom, sid))
            if r["anim"] in anims and r["dir"] in dirs]
    if not recs:
        raise ValueError("no frames for these sets, anims and dirs")
    x0, y0 = min(r["dx"] for r in recs), min(r["dy"] for r in recs)
    x1, y1 = max(r["dx"] + r["w"] for r in recs), max(r["dy"] + r["h"] for r in recs)
    return x0, y0, x1 - x0, y1 - y0


def _cell(rom: bytes, r: dict, data, box: tuple, scale: int):
    x0, y0, w, h = box
    cell = Image.new("RGBA", (w, h), BACKGROUND + (255,))
    if data is not None:
        cell.alpha_composite(_sprite(rom, r, data), (r["dx"] - x0, r["dy"] - y0))
    cell = cell.resize((w * scale, h * scale), Image.NEAREST)
    d = ImageDraw.Draw(cell)
    d.rectangle((0, 0, cell.width - 1, cell.height - 1), outline=GRID)
    ax, ay = -x0 * scale, -y0 * scale
    d.line((ax - 3, ay, ax + 3, ay), fill=LABEL)
    d.line((ax, ay - 3, ax, ay + 3), fill=LABEL)
    return cell


# ===== sheet =====

def _selected(rom: bytes, set_ids: list, anims, dirs) -> list:
    """(set id, set offset, anim, dir, frames) for each non-empty row, in sheet order."""
    offs = {sid: live_set_offset(rom, sid) for sid in set_ids}
    present = {(sid, r["anim"], r["dir"]) for sid in set_ids for r in set_records(rom, offs[sid])}
    keys = sorted({(a, d) for _, a, d in present if a in anims and d in dirs})
    return [(sid, offs[sid], a, d, row_frames(rom, offs[sid], a, d)) for a, d in keys for sid in set_ids
            if (sid, a, d) in present]


def build_sheet(rom: bytes, set_ids: list, anims, dirs, scale: int):
    """(image, notes). Notes are the printed lines: frame count per row and any over-slot record."""
    box = _anchor_box(rom, set_ids, anims, dirs)
    rows = _selected(rom, set_ids, anims, dirs)
    cw, ch = box[2] * scale, box[3] * scale
    cols = max(len(f) for *_, f in rows)
    sheet = Image.new("RGB", (LABEL_W + cols * (cw + PAD), len(rows) * (ch + TITLE_H + PAD)), BACKGROUND)
    d = ImageDraw.Draw(sheet)
    notes = []
    for i, (sid, off, a, direction, frames) in enumerate(rows):
        y = i * (ch + TITLE_H + PAD)
        label = f"set {sid} a{a} d{direction}"
        d.text((2, y + TITLE_H), label, fill=LABEL)
        d.text((2, y + TITLE_H + 12), f"{len(frames)} frames", fill=LABEL)
        slot = struct.unpack_from("<H", rom, off)[0]
        line = f"{label}: {len(frames)} frames"
        for n, (r, data) in enumerate(frames):
            x = LABEL_W + n * (cw + PAD)
            d.text((x + 2, y), f"{n}", fill=LABEL)
            sheet.paste(_cell(rom, r, data, box, scale).convert("RGB"), (x, y + TITLE_H))
            if r["w"] * r["h"] > SLOT_BYTES:
                line += f" | frame {n} {r['w']}x{r['h']} over slot {SLOT_BYTES}"
            elif r["w"] * r["h"] > slot:
                line += f" | frame {n} {r['w']}x{r['h']} over this set's slot {slot}"
            if data is None:
                line += f" | frame {n} unreadable"
        notes.append(line)
    return sheet, notes


def row_gif_frames(rom: bytes, set_off: int, anim: int, direction: int, scale: int, box: tuple) -> list:
    return [_cell(rom, r, data, box, scale).convert("RGB") for r, data in row_frames(rom, set_off, anim, direction)]


# ===== individual frames =====

def write_frames(rom: bytes, set_ids: list, out_dir: Path, anims=range(256)) -> list:
    """Each record of each set as a transparent PNG at 1x and FRAME_SCALE x. Returns the written paths."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for sid in set_ids:
        recs = [r for r in set_records(rom, live_set_offset(rom, sid)) if r["anim"] in anims]
        header = {(r["anim"], r["dir"], r["index"]): r["header"] for r in recs}
        for r in recs:
            if r["dir"] == MIRROR_DIR and header.get((r["anim"], SOURCE_DIR, r["index"])) == r["header"]:
                continue                                        # the dir 2 frame again (h-flipped or as is)
            data = unpack_frame(rom, r["header"])[2]
            if len(data) != r["w"] * r["h"]:
                raise ValueError(f"set {sid} {r['anim']}.{r['dir']}.{r['index']}: frame unreadable")
            img = _sprite(rom, r, data)
            one = out_dir / f"{sid}_a{r['anim']:02}_d{r['dir']}_i{r['index']}.png"
            big = one.with_name(f"{one.stem}_{FRAME_SCALE}x.png")
            img.save(one)
            img.resize((img.width * FRAME_SCALE, img.height * FRAME_SCALE), Image.NEAREST).save(big)
            written += [one, big]
    return written


# ===== command line =====

def _ints(text: str) -> list:
    return [int(v) for v in text.split(",") if v != ""]


def _main(argv: list) -> int:
    pos, opts, i = [], {"--anims": None, "--dirs": "0,1,2,3", "--scale": "4", "--frames": None}, 0
    gif = False
    while i < len(argv):
        if argv[i] == "--gif":
            gif = True
        elif argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 1
        else:
            pos.append(argv[i])
        i += 1
    if len(pos) != 3 and not (len(pos) == 2 and opts["--frames"]):
        print(__doc__)
        return 1
    rom = Path(pos[0]).read_bytes()
    set_ids, scale, dirs = _ints(pos[1]), int(opts["--scale"]), _ints(opts["--dirs"])
    anims = _ints(opts["--anims"]) if opts["--anims"] else range(256)
    if opts["--frames"]:
        print(len(write_frames(rom, set_ids, Path(opts["--frames"]), anims)), "frame PNGs in", opts["--frames"])
        if len(pos) == 2:
            return 0
    out = Path(pos[2])
    sheet, notes = build_sheet(rom, set_ids, anims, dirs, scale)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(out)
    print("\n".join(notes))
    if gif:
        box = _anchor_box(rom, set_ids, anims, dirs)
        for sid, off, a, d, _ in _selected(rom, set_ids, anims, dirs):
            frames = row_gif_frames(rom, off, a, d, scale, box)
            path = out.with_name(f"{out.stem}_s{sid}_a{a}_d{d}.gif")
            frames[0].save(path, save_all=True, append_images=frames[1:], duration=GIF_MS, loop=0)
            print(path)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
