"""
webfoot_decompress.py - Decompress LoG II (Webfoot) bitstream graphics, and walk the character sprite sets.

Usage:   py -3 -I webfoot_decompress.py frame <rom.gba> <hdr_off> [out.bin]
         py -3 -I webfoot_decompress.py find  <rom.gba> <probe.bin>
         py -3 -I webfoot_decompress.py set   <rom.gba> <set_index|0xSET_OFF> [png_dir palette.bin]
Prints:  frame: header type, sizes and SHA-1 of the unpacked bytes (writes out.bin if given).
         find:  every 4-aligned stream whose output contains the probe (brute force, about 15 seconds).
         set:   a sprite set's animations, frame records and unpacked sizes; with png_dir, one PNG per frame.
Source:  the codec mirrors the ARM routine the game copies to IWRAM 0x03000000 (ROM 0x7FD6BC).
         Frame headers are {u32 type, u32 size, stream}, read by the dispatcher at 0x0801F394.
Read-only on the ROM. Offsets are file offsets (ROM address minus 0x08000000).
"""
import hashlib
import struct
import sys
from pathlib import Path

ROM_BASE = 0x08000000
SET_TABLE = 0x3B4E90       # sprite set pointers; set id N >= 7 uses entry N - 7 (code 0x08009364)
SET_COUNT = 200            # walk stops early at the first entry that is not a valid set
SET_DIRS = 4               # the game hardcodes 4 directions (row 0 at set+0x4C, @0x08007568)
MASK = 0xFFFFFFFF


class StreamError(Exception):
    """The bytes are not a valid stream (bad back-reference, literal before mode, end of ROM)."""


# ===== Codec =====

class BitReader:
    """32-bit little-endian words, consumed MSB first (r6 = word, r10 = bits left in the ARM code)."""

    def __init__(self, data: bytes, pos: int):
        if pos & 3:
            raise StreamError("stream must be 4-byte aligned")
        self.data, self.pos, self.word, self.left = data, pos, 0, 0

    def _load(self) -> int:
        if self.pos + 4 > len(self.data):
            raise StreamError("ran off the end of the data")
        value = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return value

    def bit(self) -> int:
        self.left -= 1
        if self.left < 0:
            self.word, self.left = self._load(), 31
        b = self.word >> 31
        self.word = (self.word << 1) & MASK
        return b

    def bits(self, n: int) -> int:
        """Subroutine 0x0300024C. Loads a word first when empty, even for n = 0."""
        if n > 32:  # only a 6-bit offset width can ask for this; the ARM shifts go undefined, real data never does it
            raise StreamError(f"read of {n} bits")
        if self.left == 0:
            self.word, self.left = self._load(), 32
        k = min(n, self.left)
        value = self.word >> (32 - k) if k else 0
        self.word = (self.word << k) & MASK
        self.left -= k
        n -= k
        if n:
            self.word = self._load()
            self.left = 32 - n
            value = (value << n) + (self.word >> (32 - n))
            self.word = (self.word << n) & MASK
        return value

    def gamma(self) -> int:
        """Elias-gamma style: start at 1, then (value bit, continue bit) pairs."""
        value = 1
        while True:
            value = value * 2 + self.bit()
            if not self.bit():
                return value
            if value > 0xFFFFFF:
                raise StreamError("runaway gamma code")


def decompress(data: bytes, pos: int, limit: int = 0x40000) -> tuple[bytes, int]:
    """Decode one stream at data[pos]. Returns (output, packed length in bytes)."""
    r = BitReader(data, pos)
    out = bytearray()
    last_offset, offset_bits = 1, 8      # r12, r5
    lit_bits = lit_base = None           # r3, r4: undefined until the stream sets them

    def copy(offset: int, count: int):
        if not 0 < offset <= len(out):
            raise StreamError(f"back-reference {offset} before start of output")
        for _ in range(count):
            out.append(out[-offset])

    while len(out) <= limit:
        if r.bit():                                       # 1: literal
            if lit_bits is None:
                raise StreamError("literal before literal mode is set")
            out.append((r.bits(lit_bits) + lit_base) & 0xFF)
        elif r.bit():                                     # 01: long match
            high = r.gamma()
            if high == 2:                                 # repeat the last offset
                copy(last_offset, r.gamma())
                continue
            high -= 3
            offset = (r.bits(offset_bits) + ((high << offset_bits) if offset_bits < 32 else 0)) & MASK
            last_offset = offset
            count = r.gamma()
            if offset >= 0x10000:
                count += 3
            elif offset >= 0x37FF:
                count += 2
            elif offset >= 0x27F:
                count += 1
            elif offset <= 0x7F:
                count += 4
            copy(offset, count)
        elif not r.bit():                                 # 000: short match or control
            offset = r.bits(7)
            if offset:
                last_offset = offset
                copy(offset, r.bits(2) + 2)
                continue
            width = r.bits(2)
            if width == 0:                                # 000 0000000 00: end of stream
                return bytes(out), r.pos - pos
            offset_bits = r.bits(width + 3)               # new long-match offset width
        else:                                             # 001: nibble code
            nib = r.bits(4)
            if nib == 1:
                out.append(0)
            elif nib > 1:
                copy(nib - 1, 1)
            elif r.bit():                                 # raw 8-bit runs of 256 bytes
                while True:
                    out.extend(r.bits(8) for _ in range(256))
                    if not r.bit():
                        break
            else:                                         # literal mode: 8 bits, or 7 bits + base
                lit_bits, lit_base = 7 + r.bit(), 0
                if lit_bits == 7:
                    lit_base = r.bits(8)
    raise StreamError("output exceeds limit")


def unpack_frame(rom: bytes, hdr: int) -> tuple[int, int, bytes, int]:
    """Frame header {u32 type, u32 size}: type 0 = raw, 1 and 2 = compressed (dispatcher 0x0801F394)."""
    kind, size = struct.unpack_from("<II", rom, hdr)
    if kind == 0:
        return kind, size, rom[hdr + 8:hdr + 8 + size], size
    if kind in (1, 2):
        data, packed = decompress(rom, hdr + 8, limit=max(size, 0x100))
        return kind, size, data, packed
    raise StreamError(f"unknown frame type {kind}")


# ===== Sprite sets =====

def rom_ptr(rom: bytes, off: int) -> int | None:
    value = struct.unpack_from("<I", rom, off)[0]
    return value - ROM_BASE if ROM_BASE <= value < ROM_BASE + len(rom) else None


def read_set(rom: bytes, set_off: int) -> dict:
    """Set header: u16 slot (OBJ VRAM and buffer bytes, @0x080075B0), u8 anims, u8 ?; u32 ?; u32 ptr-or-0;
    4 x 16-byte box; anims x 4 pointers. Byte +1 is the slot's high byte, not a direction count."""
    slot, anims = struct.unpack_from("<HB", rom, set_off)
    table = set_off + 12 + 16 * SET_DIRS
    ptrs = [rom_ptr(rom, table + 4 * i) for i in range(anims * SET_DIRS)]
    return {"dirs": SET_DIRS, "anims": anims, "slot": slot, "table": table, "ptrs": ptrs}


def read_record(rom: bytes, rec: int) -> dict:
    """12-byte frame record (code 0x08007772): s8 dx, s8 dy, u8 w, u8 h, u16 attr0, u16 attr1, u32 frame header."""
    dx, dy, w, h, attr0, attr1 = struct.unpack_from("<bbBBHH", rom, rec)
    return {"dx": dx, "dy": dy, "w": w, "h": h, "attr0": attr0, "attr1": attr1, "hdr": rom_ptr(rom, rec + 8)}


def frames_of(rom: bytes, start: int, next_starts: set[int]):
    """Records run until the next direction's list, or until a record stops looking valid."""
    rec = start
    while True:
        r = read_record(rom, rec)
        if r["hdr"] is None or not (r["w"] and r["h"]) or struct.unpack_from("<I", rom, r["hdr"])[0] > 2:
            return
        yield rec, r
        rec += 12
        if rec in next_starts:
            return


def save_png(pixels: bytes, w: int, h: int, palette: bytes, path: Path):
    """Pixels are 8bpp tiles in 1D order (w/8 tiles per row). Color 0 stays transparent."""
    from PIL import Image
    img = Image.new("P", (w, h))
    tiles_x = w // 8
    for i, v in enumerate(pixels[:w * h]):
        t, p = divmod(i, 64)
        img.putpixel(((t % tiles_x) * 8 + p % 8, (t // tiles_x) * 8 + p // 8), v)
    rgb = []
    for c in struct.unpack_from("<256H", palette, 0x200):    # OBJ palette half of palette RAM
        rgb += [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
    img.putpalette(rgb)
    img.save(path, transparency=0)


# ===== Commands =====

def cmd_frame(rom: bytes, args: list[str]):
    hdr = int(args[0], 16)
    kind, size, data, packed = unpack_frame(rom, hdr)
    print(f"0x{hdr:06X} type={kind} size={size} unpacked={len(data)} packed={packed} sha1={hashlib.sha1(data).hexdigest()}")
    if len(args) > 1:
        Path(args[1]).write_bytes(data)


def cmd_find(rom: bytes, args: list[str]):
    probe = Path(args[0]).read_bytes()
    for off in range(0, len(rom) - 8, 4):
        try:
            data, packed = decompress(rom, off, limit=0x10000)
        except StreamError:
            continue
        if probe in data:
            print(f"0x{off:06X} unpacked={len(data)} packed={packed} probe_at={data.find(probe)}")


def cmd_set(rom: bytes, args: list[str]):
    key = args[0]
    set_off = int(key, 16) if key.lower().startswith("0x") else rom_ptr(rom, SET_TABLE + 4 * (int(key) - 7))
    s = read_set(rom, set_off)
    png_dir = Path(args[1]) if len(args) > 2 else None
    palette = Path(args[2]).read_bytes() if png_dir else b""
    if png_dir:
        png_dir.mkdir(parents=True, exist_ok=True)
    print(f"set 0x{set_off:06X}: {s['anims']} animations x {s['dirs']} directions, table 0x{s['table']:06X}")
    starts = {p for p in s["ptrs"] if p is not None}
    for i, start in enumerate(s["ptrs"]):
        if start is None:
            continue
        anim, d = divmod(i, s["dirs"])
        for n, (rec, r) in enumerate(frames_of(rom, start, starts - {start})):
            kind, size, data, packed = unpack_frame(rom, r["hdr"])
            flip = " hflip" if r["attr1"] & 0x1000 else ""
            ok = "ok" if len(data) == size == r["w"] * r["h"] else "SIZE MISMATCH"
            print(f"  anim {anim:2} dir {d} frame {n}: rec 0x{rec:06X} hdr 0x{r['hdr']:06X} {r['w']}x{r['h']} "
                  f"d=({r['dx']},{r['dy']}) type={kind} packed={packed}{flip} {ok}")
            if png_dir:
                save_png(data, r["w"], r["h"], palette, png_dir / f"a{anim:02}_d{d}_f{n}_{r['hdr']:06X}.png")


if __name__ == "__main__":
    command, rom_path, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    rom = Path(rom_path).read_bytes()
    {"frame": cmd_frame, "find": cmd_find, "set": cmd_set}[command](rom, rest)
