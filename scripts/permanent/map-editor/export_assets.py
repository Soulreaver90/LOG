r"""
export_assets.py - Write the tiles and palette the map editor loads, from the ROM, once.

Usage:   py -3.14 -P export_assets.py [OUT_DIR]      (default: map-editor\assets, must be empty or absent)
         or import and call export(rom, out_dir) -> the dict it wrote to assets.json.
Output:  chunks\<n>.png   one 8bpp indexed atlas per chunk, 16 tiles across, palette attached
         palettes.png     256x1 swatch of the BG palette, one pixel per colour
         assets.json      {"chunks": [{"index", "tiles", "png"}], "palettes": [[rgb x 256]], "tile_budget",
                           "transparent_index": 0}
         sprites\<set>.png  one standing character each, and sprites\sprites.json beside them
SPRITES: a STEP OF ITS OWN, and export() calls it. The reason is the "never overwrites" rule below:
         export() refuses a folder that already holds something, so a machine whose assets were
         written before sprites existed could never gain them. serve.ensure_assets() therefore
         calls export_sprites() alone when sprites\sprites.json is the only thing missing.
         A sprite does NOT draw through the BG palette. It carries the shared 256 colour OBJ
         palette at rom:0x1DA6C8 (bible B0036, B0250), which the PNG carries itself, so the page
         needs no palette of its own. "palettes" in assets.json stays the BG one.
         THE ANCHOR IS THE ACTOR'S POINT, never the image corner. A frame record's dx and dy are
         the offsets from that point to the frame's top left corner, so the page draws the PNG at
         (point + dx, point + dy). Imperfect Cell's stand is a 64 x 64 box at dx -20, dy -56: by
         its corner he would stand 20 px right and 8 px low, and every comparison with him would
         be wrong by that much.
PALETTE: there is exactly ONE palette. These tiles are 8bpp, so the GBA ignores the 0xF000 palette
         bits of a BG tile entry and every tile draws through the one shared 256 colour BG palette.
         "palettes" is a list of one on purpose. Build NO per-tile palette picker: it would do nothing.
Output dir is gitignored (ROM-derived art). The default is that gitignored folder, so a default run
         cannot reach a commit.
Scope:   the whole 168 chunk pool, not one map's stream, so every tile the game owns is here. Atlas
         cell N holds tile N of the chunk. Colour 0 is the GBA transparent entry and is marked so.
Read-only on the ROM. This is the one door from ROM art to the browser: nothing downstream re-reads it.
"""
import json
import sys
from pathlib import Path

from PIL import Image

for folder in (Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
    sys.path.insert(0, str(folder))                           # -P omits the script folder; scene\ is one up

from scene import map_view                                    # noqa: E402
from rom import log2_sprites                                  # noqa: E402
from rom.webfoot_decompress import set_offset, unpack_frame   # noqa: E402
import tile_stream                                            # noqa: E402

# ===== CONFIG =====
CHUNK_COUNT = 168               # frames in the shared pool (bible B1080), measured in Task 1
TRANSPARENT_INDEX = 0           # the GBA draws colour 0 as nothing; the PNG tRNS marker says so too
ATLAS_COLUMNS = 16             # tiles across one atlas
TILE_PIXELS = 8
DEFAULT_OUT = Path(__file__).resolve().parent / "assets"

# ===== CONFIG: the sprites the editor stands on a map, so a hill reads next to a person =====
# One line adds another. The id is a sprite set, resolved through THIS ROM's own table (the
# literal rom:0x959C) by set_offset, never through the base constant (bible B0247).
SPRITE_SETS = [(60, "Goku"), (132, "Trunks"), (133, "Trunks, Super Saiyan"), (28, "Imperfect Cell")]
SPRITE_ANIM = 0                 # the stand. The idle tick @0x08007570 holds index 0 for 241 of
SPRITE_INDEX = 0                # 256 ticks and index 1 for 15, so index 0 IS standing still
SPRITE_DIR = 0                  # (bible B0101). Dir 0 faces the camera (B0078), and dirs 2 and 3
                                # share one header with an h-flip, which a still must not inherit
SPRITES_IN = "sprites"          # the subfolder of the assets folder


# ===== atlas =====

def _chunk_tiles(rom: bytes, chunk: int) -> bytes:
    address = tile_stream._pointer_at(rom, tile_stream.CHUNK_TABLE + 4 * chunk)
    data = map_view.frame(rom, address)
    if len(data) % tile_stream.TILE_BYTES:
        raise ValueError(f"chunk {chunk} holds {len(data)} bytes, not a whole tile list")
    return data


def _atlas(data: bytes, flat_palette: list) -> Image.Image:
    tiles = len(data) // tile_stream.TILE_BYTES
    rows = -(-tiles // ATLAS_COLUMNS)
    atlas = Image.new("P", (ATLAS_COLUMNS * TILE_PIXELS, rows * TILE_PIXELS), 0)
    atlas.putpalette(flat_palette)
    for n in range(tiles):
        pixels = data[n * tile_stream.TILE_BYTES:(n + 1) * tile_stream.TILE_BYTES]
        cell = Image.frombytes("P", (TILE_PIXELS, TILE_PIXELS), pixels)
        atlas.paste(cell, (n % ATLAS_COLUMNS * TILE_PIXELS, n // ATLAS_COLUMNS * TILE_PIXELS))
    return atlas


def _save_new(image: Image.Image, path: Path, **options) -> None:
    with open(path, "xb") as handle:            # "x": never overwrite
        image.save(handle, format="PNG", **options)


# ===== sprites, for size next to the art =====

def _record(rom: bytes, set_id: int) -> tuple:
    """The one stand record of a set, and every record of it, for the envelope."""
    offset = set_offset(rom, set_id)
    if offset is None:
        raise ValueError(f"set {set_id} is not a pointer in this ROM's set table")
    records = log2_sprites.set_records(rom, offset)
    want = [r for r in records
            if r["anim"] == SPRITE_ANIM and r["dir"] == SPRITE_DIR and r["index"] == SPRITE_INDEX]
    if not want:
        raise ValueError(f"set {set_id} has no anim {SPRITE_ANIM} dir {SPRITE_DIR} "
                         f"record {SPRITE_INDEX}")
    return offset, want[0], records


def _ink(image: Image.Image, dx: int, dy: int) -> list:
    """The opaque pixels of one frame, as a box from the ACTOR'S POINT.

    The frame box is padding plus figure: Cell's stand is 64 x 64 and his drawn body is far
    smaller. A screenshot is measured against THIS, not against the record's box, or a check of
    "56 px of headroom" is really a check of 64 px of mostly empty frame.
    """
    pixels = image.tobytes()
    width, height = image.size
    left, top, right, bottom = width, height, -1, -1
    for y in range(height):
        row = pixels[y * width:(y + 1) * width]
        for x in range(width):
            if row[x] == TRANSPARENT_INDEX:
                continue
            left, right = min(left, x), max(right, x)
            top, bottom = min(top, y), max(bottom, y)
    if right < 0:
        raise ValueError("this frame draws nothing at all")
    return [left + dx, top + dy, right + 1 + dx, bottom + 1 + dy]


def _envelope(records: list) -> list:
    """Every record of the set, as one box from the actor's point. Bible B0246 is the cross-check:
    set 28 is 20 left, 44 right, 56 up, 8 down, and sets 132 and 133 are 8, 24, 24, 8."""
    return [min(r["dx"] for r in records), min(r["dy"] for r in records),
            max(r["dx"] + r["w"] for r in records), max(r["dy"] + r["h"] for r in records)]


def export_sprites(rom: bytes, out_dir: Path) -> dict:
    """Write one standing frame per SPRITE_SETS entry into OUT_DIR, and return sprites.json.

    Boxes are [x0, y0, x1, y1] in pixels FROM THE ACTOR'S POINT, x1 and y1 exclusive.
      box        the frame record's own box: where the PNG goes, which is (point + dx, point + dy)
      ink        the pixels that are actually drawn in THIS frame
      envelope   every record of the whole set, which is the reach of its attacks and its falls
    """
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"{out_dir} is not empty: export never overwrites")
    out_dir.mkdir(parents=True, exist_ok=True)
    palette = bytes(rom[log2_sprites.PALETTE_OFF:
                        log2_sprites.PALETTE_OFF + log2_sprites.PALETTE_LEN])

    sprites = []
    for set_id, name in SPRITE_SETS:
        offset, record, records = _record(rom, set_id)
        # An h or v flip bit would mean the PNG is not what the game draws here. Dir 0 carries
        # none on any set in the list, and a set that grew one must be seen rather than mirrored.
        if record["attr1"] & 0x3000:
            raise ValueError(f"set {set_id} stand carries flip bits 0x{record['attr1'] & 0x3000:X}")
        _, _, data, _ = unpack_frame(rom, record["header"])
        image = log2_sprites.tiles_to_image(data, record["w"], record["h"], palette)
        png = f"{set_id}.png"
        _save_new(image, out_dir / png, transparency=TRANSPARENT_INDEX)
        sprites.append({
            "set": set_id, "name": name, "png": png,
            "anim": SPRITE_ANIM, "dir": SPRITE_DIR, "index": SPRITE_INDEX,
            "w": record["w"], "h": record["h"],
            "box": [record["dx"], record["dy"],
                    record["dx"] + record["w"], record["dy"] + record["h"]],
            "ink": _ink(image, record["dx"], record["dy"]),
            "envelope": _envelope(records),
            "records": len(records), "header": record["header"], "set_offset": offset,
        })

    manifest = {"sprites": sprites, "transparent_index": TRANSPARENT_INDEX,
                "anchor": "box, ink and envelope are [x0, y0, x1, y1] px from the actor's point"}
    with open(out_dir / "sprites.json", "x", encoding="utf-8") as handle:
        json.dump(manifest, handle)
    return manifest


# ===== export =====

def export(rom: bytes, out_dir: Path = DEFAULT_OUT) -> dict:
    """Write the editor assets into OUT_DIR and return the dict written to assets.json."""
    out_dir = Path(out_dir)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"{out_dir} is not empty: export never overwrites")
    (out_dir / "chunks").mkdir(parents=True, exist_ok=True)

    flat = map_view.palette(rom)
    rgb = [flat[i:i + 3] for i in range(0, len(flat), 3)]
    chunks = []
    for chunk in range(CHUNK_COUNT):
        data = _chunk_tiles(rom, chunk)
        png = f"chunks/{chunk}.png"
        _save_new(_atlas(data, flat), out_dir / png, transparency=TRANSPARENT_INDEX)
        chunks.append({"index": chunk, "tiles": len(data) // tile_stream.TILE_BYTES, "png": png})

    swatch = Image.new("P", (len(rgb), 1))
    swatch.putdata(range(len(rgb)))
    swatch.putpalette(flat)
    _save_new(swatch, out_dir / "palettes.png")

    export_sprites(rom, out_dir / SPRITES_IN)

    manifest = {"chunks": chunks, "palettes": [rgb], "tile_budget": tile_stream.TILE_BUDGET,
                "transparent_index": TRANSPARENT_INDEX}
    with open(out_dir / "assets.json", "x", encoding="utf-8") as handle:
        json.dump(manifest, handle)
    return manifest


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    done = export(map_view.BASE.read_bytes(), target)
    print(f"wrote {len(done['chunks'])} chunk atlases and {len(SPRITE_SETS)} sprites to {target}")
