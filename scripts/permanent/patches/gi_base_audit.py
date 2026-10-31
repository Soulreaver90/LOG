r"""
gi_base_audit.py - Trial patch: base gi Gohan (set 157) shows approved base-audit frames
                   (art\base-audit\approved\, my approvals 2026-10-23 to 2026-10-25).

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_gi_base.txt --out <new .gba>
Input:   the ROM after the main list (set 157 built by gohan_gi from art\gi_base). Run it last.
API:     apply(rom, alloc) -> None; alloc.notes["gi_base_audit"]: set_157, keys, frames, changed, and "sites" as
         (offset, length, name), one per frame data range written.
         approved_frames(folder) -> {(anim, dir, index): Frame}
Method:  An approved PNG 157_a{A}_d{D}_i{I}.png holds key (A, D, I) in stored order (flips undone), mode P, in the
         shared OBJ palette (ba_edit.py, ba_owner_carry.py). gohan_gi wrote one raw type 0 frame ({u32 0, u32 len,
         data}) per gi_base PNG, and every key of that PNG points at it. The approved bytes overwrite that frame's data
         in place: nothing is allocated and no pointer moves. Keys that share the frame (a mirror dir, the 4 dirs of a
         front view) are all approved with the same bytes, or the patch raises.
Rules:   Source: docs\tasks\2026-10-30-gi-base-ingest\gi-base-ingest.md. Pixels are copied as drawn, never changed.
         Checked for every frame before the first write: each key that shows it is approved, with the same bytes; PNG
         size = the record's w x h; w*h <= the set slot; attr shape bits match; index 0 is clear; each used index has
         the PNG color = the OBJ palette color; the header reads {0, w*h}; the data equals what gohan_gi wrote from
         art\gi_base; the only patch-written ROM words naming the frame header are set 157 record pointers (a
         word equal to the base ROM, or one naming the frame's inside, is code or data, not a frame pointer); no
         earlier module lists it in its "sites". A second run raises.
"""
import re
import struct
from collections import defaultdict
from typing import NamedTuple

from PIL import Image

import log_paths
from log2_build import BASE, BASE_SIZE
from rom.log2_sprites import OBJ_SHAPES, PALETTE_OFF, image_to_tiles, read_set, set_records
from patches.bf_ki_pool import words_naming
from patches.gohan_gi import art_records

# ===== constants =====
APPROVED = log_paths.ART / "base-audit" / "approved"
NAME = re.compile(r"157_a(\d+)_d(\d+)_i(\d+)\.png")
ROM_BASE = 0x08000000
SET_ID, FIRST_ID, SET_TABLE_LITERAL = 157, 7, 0x959C       # gohan_gi's set table copy, ids 7-160


class Frame(NamedTuple):
    size: tuple
    tiles: bytes
    palette: list        # RGB triples flat, as PIL gives them
    clear: bool          # index 0 marked transparent


def _u32(rom, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def approved_frames(folder=APPROVED) -> dict:
    """{(anim, dir, index): Frame} for every PNG in the folder; a PNG with another name raises."""
    out = {}
    for p in sorted(folder.glob("*.png")):
        m = NAME.fullmatch(p.name)
        if not m:
            raise ValueError(f"{p.name}: not a 157_a<anim>_d<dir>_i<index>.png name")
        with Image.open(p) as img:
            if img.mode != "P":
                raise ValueError(f"{p.name}: mode {img.mode}, not P (indexed)")
            out[tuple(int(g) for g in m.groups())] = Frame(img.size, image_to_tiles(img), img.getpalette(),
                                                           img.info.get("transparency") == 0)
    return out


def _obj_palette(rom) -> list:
    return [v for c in struct.unpack_from("<256H", rom, PALETTE_OFF)
            for v in ((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)]


def _written(notes: dict) -> list:
    """(module, offset, length) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            s, length = (site, 1) if isinstance(site, int) else tuple(site)[:2]
            out.append((name, s, length))
    return out


# ===== checks =====

def _set_157(rom, alloc) -> int:
    table = _u32(rom, SET_TABLE_LITERAL) - ROM_BASE
    set_off = _u32(rom, table + 4 * (SET_ID - FIRST_ID)) - ROM_BASE
    if alloc.notes.get("gohan_gi", {}).get("set_157") != set_off:
        raise ValueError(f"set 157 at rom:0x{set_off:X} is not the one gohan_gi built")
    return set_off


def _check_frame(key, f: Frame, r: dict, slot: int, obj: list) -> None:
    if f.size != (r["w"], r["h"]):
        raise ValueError(f"{key}: PNG {f.size[0]}x{f.size[1]}, record {r['w']}x{r['h']}")
    if r["w"] * r["h"] > slot:
        raise ValueError(f"{key}: {r['w']}x{r['h']} exceeds the {slot}-byte slot")
    if OBJ_SHAPES.get((r["w"], r["h"])) != (r["attr0"] >> 14, r["attr1"] >> 14):
        raise ValueError(f"{key}: attr shape and size bits do not match {r['w']}x{r['h']}")
    if not f.clear:
        raise ValueError(f"{key}: index 0 is not marked transparent")
    off = sorted(i for i in set(f.tiles) if i and f.palette[3 * i:3 * i + 3] != obj[3 * i:3 * i + 3])
    if off:
        raise ValueError(f"{key}: PNG color at indices {off} is not the OBJ palette color")


def plan(rom, alloc, frames: dict) -> tuple:
    """(set offset, {header: (tiles, sorted keys)}) after every check; raises before any write."""
    if "gi_base_audit" in alloc.notes:
        raise ValueError("gi_base_audit already ran")
    set_off = _set_157(rom, alloc)
    slot = read_set(rom, set_off)["slot"]
    recs = {(r["anim"], r["dir"], r["index"]): r for r in set_records(rom, set_off)}
    by_hdr = defaultdict(list)
    for k, r in recs.items():
        by_hdr[r["header"]].append(k)
    obj = _obj_palette(rom)
    gi_recs, gi_frames = art_records("gi_base")
    out = {}
    for k, f in sorted(frames.items()):
        if k not in recs:
            raise ValueError(f"{k}: set 157 has no such key")
        _check_frame(k, f, recs[k], slot, obj)
        hdr = recs[k]["header"]
        if hdr in out and out[hdr][0] != f.tiles:
            raise ValueError(f"{k}: frame 0x{hdr:06X} is shared with {out[hdr][1]}, approved bytes differ")
        out[hdr] = (f.tiles, sorted(by_hdr[hdr]))
    for hdr, (tiles, keys) in out.items():
        missing = [k for k in keys if k not in frames]
        if missing:
            raise ValueError(f"frame 0x{hdr:06X} is also shown by {missing}, which are not approved")
        if bytes(rom[hdr:hdr + 8]) != struct.pack("<II", 0, len(tiles)):
            raise ValueError(f"frame 0x{hdr:06X} is not a raw type 0 frame of {len(tiles)} bytes")
        if any(bytes(rom[hdr + 8:hdr + 8 + len(tiles)]) != gi_frames[gi_recs[k]["frame"]] for k in keys):
            raise ValueError(f"frame 0x{hdr:06X} data is not the gi_base frame of {keys[0]}")
    lo, hi = min(out), max(h + 8 + len(t) for h, (t, _) in out.items())
    base = BASE.read_bytes()
    for w in words_naming(rom, lo + ROM_BASE, hi + ROM_BASE, ()):
        v = _u32(rom, w) - ROM_BASE
        if v not in out or (w < BASE_SIZE and rom[w:w + 4] == base[w:w + 4]):
            continue        # a frame pointer names the header; interior hits are code or LZ data (rom:0x20178, 0x90B224)
        if w not in {recs[k]["rec"] + 8 for k in out[v][1]}:
            raise ValueError(f"rom:0x{w:X} names frame 0x{v:06X} outside the set 157 records")
    for name, s, length in _written(alloc.notes):
        for h, (t, _) in out.items():
            if s < h + 8 + len(t) and h < s + length:
                raise ValueError(f"frame 0x{h:06X} is also written by {name} (rom:0x{s:X}, {length}): stop and report")
    return set_off, out


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    frames = approved_frames(APPROVED)
    set_off, out = plan(rom, alloc, frames)
    sites, changed = [], 0
    for hdr, (tiles, keys) in sorted(out.items()):
        at = hdr + 8
        changed += sum(a != b for a, b in zip(rom[at:at + len(tiles)], tiles))
        rom[at:at + len(tiles)] = tiles
        sites.append((at, len(tiles), "set 157 frame 0x%06X data (%s)" % (hdr, " ".join("%d.%d.%d" % k for k in keys))))
    alloc.notes["gi_base_audit"] = {"set_157": set_off, "keys": len(frames), "frames": len(out),
                                    "changed": changed, "sites": sites}
