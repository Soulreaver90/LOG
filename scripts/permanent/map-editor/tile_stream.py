r"""
tile_stream.py - The BG tile stream codec: read and write a map layout's +0x48 tile list.

Usage:   sys.path must hold scripts\permanent\map-editor (the folder name has a hyphen, so it is not
         an importable package), then `import tile_stream`.
         decode_stream(rom, layout) -> [(chunk, tile)]   encode_stream(pairs) -> the frame payload
         tiles_of(rom, pairs, chunk_table_of(rom, layout)) -> the 64 byte pixels of each pair
         TILE_BUDGET -> the tile cap a map may not pass
Format:  layout +0x48 is a compressed frame. Its payload is a u16 list, delta coded
         e[i] += e[i-1] + 1, one entry per tile. The entry's high byte picks a chunk in the layout
         +0x4C table, its low byte a 64 byte tile inside that chunk. Entry i is DMAed to
         0x06000000 + 0x40 * i, so a stream position IS the tile number a BG tile entry names.
Source:  Map_LoadLayer @0x080050C8, read in the disassembly (bible B1080, B1098). Two traps it
         settles: the decode buffer is 0x700 bytes, which is the whole tile budget; and the loader
         re-decodes a chunk every time the high byte changes, so a stream may name chunks in any
         order and may repeat one. Map 6,99 does repeat, with a 0xFFFF delta.
Mixing:  all 336 layouts the base ROM's map table reaches point +0x4C at the one table 0x084DF574,
         so the 168 chunks are a global pool and a map may load tiles from any source map. BG art
         draws through the one shared BG palette rom:0x1DA4C8 (bible B0305), so a borrowed tile
         also keeps its colours. Proved in tests\test_tile_stream.py, MixedSourceTests.
Trap:    a BUILD may relocate the chunk table. On r40 map 14,4 names its own table at 0x0890A92C.
         So read a real layout's table with chunk_table_of, and treat CHUNK_TABLE as the pool a
         NEW layout should name, never as the table a layout in hand must have.
One copy: the delta decode and the chunk walk live in `scene\scene_probe`, the section 9 reader, and
         this module is their ADDRESS form plus the ENCODE the editor needs. `decode_payload` IS
         `scene_probe.tile_pairs`, so the editor and the renderer cannot read one stream apart.
Read-only on the ROM.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder

from scene import map_view                                    # noqa: E402
from scene import scene_probe                                 # noqa: E402

# ===== CONFIG =====
TILE_BUDGET = scene_probe.TILE_BUDGET   # Map_LoadLayer decodes the list into a 0x700 byte buffer
CHUNK_TABLE = 0x084DF574        # the shared pool, 168 frames: what a NEW layout names, not a given
TILE_BYTES = scene_probe.TILE_BYTES     # an 8x8 tile at 8bpp
STREAM_PTR, TABLE_PTR = 0x48, 0x4C      # layout +0x48 the compressed tile list, +0x4C its chunk table


def _pointer_at(rom: bytes, address: int) -> int:
    """The ROM word at an ADDRESS, read as an address. map_view keeps the same read as a private.

    The range check is the one guard against a file OFFSET arriving here. scene_probe.layouts
    yields offsets and map_view.layout_of yields addresses, so the two are mixed up easily, and an
    offset would otherwise read a plausible word from the wrong end of the ROM in silence."""
    if not map_view.ROM_BASE <= address < map_view.ROM_BASE + len(rom):
        raise ValueError(f"0x{address:08X} is not a ROM address: pass an address, not a file offset")
    return map_view.u32(rom, address - map_view.ROM_BASE)


# ===== codec =====

decode_payload = scene_probe.tile_pairs   # the one decode, section 9's own; this module adds the encode


def decode_stream(rom: bytes, layout: int) -> list:
    """The same pairs, read from a layout ADDRESS, as map_view.layout_of returns one."""
    return decode_payload(map_view.frame(rom, _pointer_at(rom, layout + STREAM_PTR)))


def encode_stream(pairs: list) -> bytes:
    """The +0x48 frame payload for these pairs, in the order given.

    The delta is masked to 16 bits, which is what lets a stream repeat a tile or step backwards:
    the loader adds in u16 and never checks, so this is the exact inverse of the decode."""
    if len(pairs) > TILE_BUDGET:
        raise ValueError(f"{len(pairs)} tiles is over the {TILE_BUDGET} tile budget of the loader")
    out, previous = [], None
    for chunk, tile in pairs:
        if not (0 <= chunk <= 0xFF and 0 <= tile <= 0xFF):
            raise ValueError(f"chunk {chunk} tile {tile}: each must be a byte, 0 to 255")
        entry = (chunk << 8) | tile
        out.append(entry if previous is None else (entry - previous - 1) & 0xFFFF)
        previous = entry
    return struct.pack(f"<{len(out)}H", *out)


def chunk_table_of(rom: bytes, layout: int) -> int:
    """The chunk table ADDRESS this layout names. A build may move it, so never assume CHUNK_TABLE."""
    return _pointer_at(rom, layout + TABLE_PTR)


def tiles_of(rom: bytes, pairs: list, table: int) -> list:
    """The 64 byte pixels of every pair, in load order. One chunk decode per chunk, as the loader does.

    `table` is named by the caller, never defaulted: a default would be the base ROM's address, and
    a build that moved the table would then read a dead one. map_view keeps no map table constant
    for the same reason.

    The walk itself is scene_probe.chunk_tiles, the one the renderer uses, so a borrowed tile
    cannot look one way here and another in a picture. This wrapper owns the ADDRESS form and the
    range check that catches a file offset arriving where an address belongs."""
    _pointer_at(rom, table)
    return scene_probe.chunk_tiles(rom, pairs, table - map_view.ROM_BASE)
