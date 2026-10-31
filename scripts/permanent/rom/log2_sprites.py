r"""
log2_sprites.py - Export LoG II sprite sets to indexed PNGs, and clone a set with replaced frames.

Usage:   py -3 -I log2_sprites.py export <rom.gba> <set_id|0xSET_OFF> <out_dir>
Prints:  the manifest path and the frame count of each animation.
API:     tiles_to_image(data, w, h, palette) -> PIL "P" image; image_to_tiles(img) -> bytes (exact inverse)
         set_records(rom, set_off) -> [{anim, dir, index, rec, dx, dy, w, h, attr0, attr1, header}]
         export_set(rom, set_off, out_dir) -> manifest path
         clone_set(rom, src_set_off, frames, alloc) -> new set file offset
         build_set(rom, src_set_off, records, frames, alloc, counts=None) -> new set file offset (each record its
         own geometry; counts = {anim: records per dir} for a list longer than the source set)
Rules:   Pixels are 8bpp tiles in 1D order (w/8 tiles per row, 64 bytes a tile). Palette is the 512-byte
         shared OBJ palette at rom:0x1DA6C8 (BGR555); color 0 is transparent.
         A clone writes only into space handed out by the Allocator. New frames are raw type 0
         ({u32 0, u32 len, data}; dispatcher @0x0801F394 copies `size` bytes from header + 8).
         Every pointer written into a clone is a GBA address (file offset + 0x08000000).
Source:  Set layout in docs\research\re-sprite-decompression.md "Sprite indexing". Reads through webfoot_decompress.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from rom.rom_space import Allocator
from rom.webfoot_decompress import ROM_BASE, SET_TABLE, frames_of, read_record, read_set, rom_ptr, unpack_frame

# ===== constants =====
PALETTE_OFF = 0x1DA6C8
PALETTE_LEN = 512
RECORD_SIZE = 12
OBJ_SHAPES = {(8, 8): (0, 0), (16, 16): (0, 1), (32, 32): (0, 2), (64, 64): (0, 3),
              (16, 8): (1, 0), (32, 8): (1, 1), (32, 16): (1, 2), (64, 32): (1, 3),
              (8, 16): (2, 0), (8, 32): (2, 1), (16, 32): (2, 2), (32, 64): (2, 3)}   # (w, h) -> attr0, attr1 bits 14-15
SLOT_BYTES = 0x400        # Gohan sets' header u16 +0: the player's OBJ VRAM slot (@0x080075B0); no frame may exceed it


# ===== tiles <-> image =====

def tiles_to_image(data: bytes, w: int, h: int, palette: bytes):
    """8bpp 1D-order tiles to a mode P image. `palette` is 256 BGR555 entries (512 bytes)."""
    from PIL import Image
    if w % 8 or h % 8 or len(data) != w * h:
        raise ValueError(f"{len(data)} bytes do not make {w}x{h} tiles")
    rows = [bytearray(w) for _ in range(h)]
    tiles_x = w // 8
    for t in range(len(data) // 64):
        x0, y0 = (t % tiles_x) * 8, (t // tiles_x) * 8
        for r in range(8):
            rows[y0 + r][x0:x0 + 8] = data[t * 64 + r * 8:t * 64 + r * 8 + 8]
    img = Image.frombytes("P", (w, h), b"".join(rows))
    rgb = []
    for c in struct.unpack_from("<256H", palette, 0):
        rgb += [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
    img.putpalette(rgb)
    img.info["transparency"] = 0
    return img


def image_to_tiles(img) -> bytes:
    """Exact inverse of tiles_to_image. The image must be mode P with sides that are multiples of 8."""
    if img.mode != "P":
        raise ValueError(f"image mode {img.mode} is not P (indexed)")
    w, h = img.size
    if w % 8 or h % 8:
        raise ValueError(f"{w}x{h} is not a multiple of 8")
    px = img.tobytes()
    tiles_x = w // 8
    out = bytearray()
    for t in range((w // 8) * (h // 8)):
        x0, y0 = (t % tiles_x) * 8, (t // tiles_x) * 8
        for r in range(8):
            start = (y0 + r) * w + x0
            out += px[start:start + 8]
    return bytes(out)


# ===== set walking =====

def _lists(rom: bytes, s: dict):
    """(table index, list start) for each non-null animation entry."""
    return [(i, p) for i, p in enumerate(s["ptrs"]) if p is not None]


def set_records(rom: bytes, set_off: int) -> list:
    """Every record frames_of() reaches, in table order."""
    s = read_set(rom, set_off)
    starts = {p for _, p in _lists(rom, s)}
    out = []
    for i, start in _lists(rom, s):
        anim, d = divmod(i, s["dirs"])
        for n, (rec, r) in enumerate(frames_of(rom, start, starts - {start})):
            out.append({"anim": anim, "dir": d, "index": n, "rec": rec, "dx": r["dx"], "dy": r["dy"],
                        "w": r["w"], "h": r["h"], "attr0": r["attr0"], "attr1": r["attr1"], "header": r["hdr"]})
    return out


# ===== export =====

def export_set(rom: bytes, set_off: int, out_dir: Path) -> Path:
    """One indexed PNG per unique frame header, plus manifest.json. Returns the manifest path."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    palette = bytes(rom[PALETTE_OFF:PALETTE_OFF + PALETTE_LEN])
    pngs = {}
    manifest = []
    for r in set_records(rom, set_off):
        hdr = r["header"]
        if hdr not in pngs:
            _, _, data, _ = unpack_frame(rom, hdr)
            name = f"frame_{hdr:06X}.png"
            tiles_to_image(data, r["w"], r["h"], palette).save(out_dir / name, transparency=0)
            pngs[hdr] = name
        manifest.append({"anim": r["anim"], "dir": r["dir"], "index": r["index"], "dx": r["dx"], "dy": r["dy"],
                         "w": r["w"], "h": r["h"], "attr0": r["attr0"], "attr1": r["attr1"],
                         "header": hdr, "png": pngs[hdr]})
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=1), encoding="ascii")
    return path


# ===== clone =====

def _gba(off: int) -> int:
    return off + ROM_BASE


def clone_set(rom: bytearray, src_set_off: int, frames: dict, alloc: Allocator) -> int:
    """Copy header, animation table and record lists into allocated space.
    `frames` maps an original frame header offset to new tile bytes (w*h long). Records using that
    header get one shared new raw frame. Other records keep their original header pointer."""
    s = read_set(rom, src_set_off)
    table_end = s["table"] + 4 * len(s["ptrs"])
    starts = {p for _, p in _lists(rom, s)}
    new_hdr = {}                        # original header offset -> GBA address of the new raw frame
    new_list = {}                       # original list start -> GBA address of the cloned list
    pending = []                        # (list start, new offset), written after frames exist

    for start in sorted(starts):
        recs = list(frames_of(rom, start, starts - {start}))
        if not recs:
            continue
        at = alloc.alloc(RECORD_SIZE * len(recs))
        new_list[start] = _gba(at)
        for k, (rec, r) in enumerate(recs):
            dst = at + k * RECORD_SIZE
            rom[dst:dst + 8] = rom[rec:rec + 8]
            ptr = struct.unpack_from("<I", rom, rec + 8)[0]
            if r["hdr"] in frames:
                if r["hdr"] not in new_hdr:
                    data = bytes(frames[r["hdr"]])
                    if len(data) != r["w"] * r["h"]:
                        raise ValueError(f"frame 0x{r['hdr']:06X}: {len(data)} bytes, record needs {r['w'] * r['h']}")
                    f = alloc.alloc(8 + len(data))
                    rom[f:f + 8 + len(data)] = struct.pack("<II", 0, len(data)) + data
                    new_hdr[r["hdr"]] = _gba(f)
                ptr = new_hdr[r["hdr"]]
            struct.pack_into("<I", rom, dst + 8, ptr)

    unknown = set(frames) - set(new_hdr)
    if unknown:
        raise ValueError("frame keys no record uses: " + ", ".join(f"0x{k:06X}" for k in sorted(unknown)))

    head = alloc.alloc(table_end - src_set_off)
    rom[head:head + table_end - src_set_off] = rom[src_set_off:table_end]
    tbl = head + (s["table"] - src_set_off)
    for i, p in _lists(rom, s):
        if p in new_list:
            struct.pack_into("<I", rom, tbl + 4 * i, new_list[p])
    return head


def build_set(rom: bytearray, src_set_off: int, records: dict, frames: dict, alloc: Allocator,
              counts: dict = None) -> int:
    """A new set with the header, boxes and animation table of the source set, where every record carries its
    own geometry. `records` maps (anim, dir, index) to {dx, dy, w, h, attr0, attr1, frame}; `frames` maps a
    frame id to its w*h tile bytes (one raw type 0 frame each). Every source key needs a record, with the same
    count per (anim, dir), or the count `counts` gives for that anim ({anim: records per dir}; the frame count
    is in code, so a longer list needs a tick that reads it, as ssj2_idle does for anim 0).
    Each distinct record list is written once; table entries that share it point at it.
    A frame larger than the header slot (u16 +0, the OBJ VRAM bytes) or a wrong shape is refused."""
    s = read_set(rom, src_set_off)
    starts = {p for _, p in _lists(rom, s)}
    rows, wanted = {}, set()                    # table index -> tuple of record keys
    for i, start in _lists(rom, s):
        anim, d = divmod(i, s["dirs"])
        n = (counts or {}).get(anim) or len(list(frames_of(rom, start, starts - {start})))
        keys = tuple((anim, d, k) for k in range(n))
        missing = [k for k in keys if k not in records]
        if missing:
            raise ValueError(f"no record for {missing[0]}")
        rows[i] = keys
        wanted.update(keys)
    extra = set(records) - wanted
    if extra:
        raise ValueError(f"records the source set has no place for: {sorted(extra)[:3]}")
    addr = {}
    for k in sorted(wanted):
        r = records[k]
        data = bytes(frames[r["frame"]])
        if len(data) != r["w"] * r["h"]:
            raise ValueError(f"{k}: {len(data)} bytes, record needs {r['w'] * r['h']}")
        if r["w"] * r["h"] > s["slot"]:
            raise ValueError(f"{k}: {r['w']}x{r['h']} exceeds the {s['slot']}-byte slot")
        if OBJ_SHAPES.get((r["w"], r["h"])) != (r["attr0"] >> 14, r["attr1"] >> 14):
            raise ValueError(f"{k}: attr shape and size bits do not match {r['w']}x{r['h']}")
        if r["frame"] not in addr:
            f = alloc.alloc(8 + len(data))
            rom[f:f + 8 + len(data)] = struct.pack("<II", 0, len(data)) + data
            addr[r["frame"]] = _gba(f)
    lists = {}                                  # record contents -> GBA address of the written list
    for i, keys in rows.items():
        body = b"".join(struct.pack("<bbBBHHI", records[k]["dx"], records[k]["dy"], records[k]["w"], records[k]["h"],
                                    records[k]["attr0"], records[k]["attr1"], addr[records[k]["frame"]])
                        for k in keys)
        if body not in lists:
            at = alloc.alloc(len(body))
            rom[at:at + len(body)] = body
            lists[body] = _gba(at)
        rows[i] = lists[body]
    table_end = s["table"] + 4 * len(s["ptrs"])
    head = alloc.alloc(table_end - src_set_off)
    rom[head:head + table_end - src_set_off] = rom[src_set_off:table_end]
    tbl = head + (s["table"] - src_set_off)
    for i, ptr in rows.items():
        struct.pack_into("<I", rom, tbl + 4 * i, ptr)
    return head


# ===== command line =====

def _main(argv: list):
    if len(argv) != 4 or argv[0] != "export":
        print(__doc__)
        return 1
    rom = Path(argv[1]).read_bytes()
    key = argv[2]
    set_off = int(key, 16) if key.lower().startswith("0x") else rom_ptr(rom, SET_TABLE + 4 * (int(key) - 7))
    path = export_set(rom, set_off, Path(argv[3]))
    print(path)
    counts = {}
    for r in set_records(rom, set_off):
        counts.setdefault((r["anim"], r["dir"]), 0)
        counts[(r["anim"], r["dir"])] += 1
    for (a, d), n in sorted(counts.items()):
        print(f"anim {a} dir {d}: {n} frames")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
