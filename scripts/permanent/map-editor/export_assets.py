r"""
export_assets.py - Write the tiles and palette the map editor loads, from the ROM, once.

Usage:   py -3.14 -P export_assets.py [OUT_DIR]      (default: map-editor\assets, must be empty or absent)
         or import and call export(rom, out_dir) -> the dict it wrote to assets.json.
Output:  chunks\<n>.png   one 8bpp indexed atlas per chunk, 16 tiles across, palette attached
         palettes.png     256x1 swatch of the BG palette, one pixel per colour
         assets.json      {"chunks": [{"index", "tiles", "png"}], "palettes": [[rgb x 256]], "tile_budget"}
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
import tile_stream                                            # noqa: E402

# ===== CONFIG =====
CHUNK_COUNT = 168               # frames in the shared pool (bible B1080), measured in Task 1
ATLAS_COLUMNS = 16              # tiles across one atlas
TILE_PIXELS = 8
DEFAULT_OUT = Path(__file__).resolve().parent / "assets"


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
        _save_new(_atlas(data, flat), out_dir / png, transparency=0)
        chunks.append({"index": chunk, "tiles": len(data) // tile_stream.TILE_BYTES, "png": png})

    swatch = Image.new("P", (len(rgb), 1))
    swatch.putdata(range(len(rgb)))
    swatch.putpalette(flat)
    _save_new(swatch, out_dir / "palettes.png")

    manifest = {"chunks": chunks, "palettes": [rgb], "tile_budget": tile_stream.TILE_BUDGET}
    with open(out_dir / "assets.json", "x", encoding="utf-8") as handle:
        json.dump(manifest, handle)
    return manifest


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    done = export(map_view.BASE.read_bytes(), target)
    print(f"wrote {len(done['chunks'])} chunk atlases to {target}")
