r"""
map_index.py - Index every map: its entry fields, its layout fields, and the scene tables it owns.

Usage:   py -3.14 -P scripts\permanent\scene\map_index.py
         Add --rom <path> to index a build, and --audit to print the field-shape census only.
Output:  docs\research\map-index.md and .json. Reads only; writes no ROM.
Why:     "which map has X" and "what does this field hold" should be lookups. The arena work spent four
         builds on a map whose own tools could not open it, and on layout lists nobody had enumerated.
Reads:   THIS ROM's map table, resolved by scene_probe.map_table from the literal at rom:0xEBD8 and the
         count byte at rom:0xE0AE, so an appended map such as 6,100 is indexed like any other.
Fields:  map entry is 56 bytes. Bible tag SAV pins +0x10 regions, +0x14 item POINTER list whose count is
         the low byte of +0x04, and +0x2C the layout array indexed by variation - 1. Row 1124 pins that
         byte +3/+4/+5/+6/+7 is zero exactly when word +0x10/+0x14/+0x18/+0x1C/+0x20 is zero.
         Layout: +0x24 prop count and +0x28 prop entries and +0x2C sheet frame (tag EFX), +0x34 the
         collision frame, +0x40/+0x44 the door list (tag WRP), +0x48/+0x4C the tile stream (tag BMT).
         --audit reports, for every entry word, how many of the maps hold a ROM pointer and how many hold
         a small number, so a field is never described from one example again.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder

import log_paths  # noqa: E402
from scene import scene_probe                                            # noqa: E402

# ===== CONFIG =====
BASE = log_paths.BASE_ROM
OUT = log_paths.RESEARCH
ROM_BASE = 0x08000000
ENTRY_WORDS = 14                                  # 56 bytes
# The layout field offsets live in scene_probe, the section 9 reader. One name, one place.
L_PROP_COUNT, L_COLLISION = scene_probe.L_PROP_COUNT, scene_probe.L_COLLISION
L_WARP_COUNT = scene_probe.L_DOOR_COUNT


def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def is_pointer(word: int) -> bool:
    return 0x08000000 <= word < 0x08000000 + 0x2000000


def layout_of(rom: bytes, entry: int, var: int = 1):
    """The layout record for one variation, or None. scene_probe.layouts is the one chain walker."""
    chain = scene_probe.layouts(rom, entry)
    return chain[var - 1] if chain and var <= len(chain) else None


def audit(rom: bytes) -> list:
    """How every one of the 14 entry words is actually used across all maps, so no field is described
    from a single example. A word that is a pointer in some maps and a small number in others is a
    finding, not a field."""
    table, count = scene_probe.map_table(rom)
    kinds = [{"pointer": 0, "zero": 0, "small": 0, "other": 0} for _ in range(ENTRY_WORDS)]
    for k in range(count):
        at = table + scene_probe.MAP_SIZE * k
        for w in range(ENTRY_WORDS):
            word = u32(rom, at + 4 * w)
            bucket = ("zero" if word == 0 else "pointer" if is_pointer(word)
                      else "small" if word < 0x10000 else "other")
            kinds[w][bucket] += 1
    return kinds



def out_name(rom_path: Path, stem: str, ext: str) -> Path:
    """The page for the BASE ROM keeps its plain name; any other ROM gets its own file.

    Without this a `--rom <build>` run silently overwrites the vanilla reference page with build data,
    and the next reader takes a build's numbers for the game's."""
    if rom_path.resolve() == BASE.resolve():
        return OUT / f"{stem}.{ext}"
    return OUT / f"{stem}--{rom_path.stem}.{ext}"

def main(argv: list) -> None:
    rom_path = Path(argv[argv.index("--rom") + 1]) if "--rom" in argv else BASE
    rom = rom_path.read_bytes()
    table, count = scene_probe.map_table(rom)

    shapes = audit(rom)
    audit_lines = ["| word | zero | ROM pointer | < 0x10000 | other | reading |",
                   "| --- | --- | --- | --- | --- | --- |"]
    for w, k in enumerate(shapes):
        total = sum(k.values())
        reading = ("a pointer field" if k["pointer"] > total * 0.5 else
                   "a count or id field" if k["small"] + k["zero"] > total * 0.9 else
                   "MIXED, not one field")
        audit_lines.append(f"| +0x{w * 4:02X} | {k['zero']} | {k['pointer']} | {k['small']} | "
                           f"{k['other']} | {reading} |")
    if "--audit" in argv:
        print("\n".join(audit_lines))
        return

    rows = []
    for k in range(count):
        at = table + scene_probe.MAP_SIZE * k
        zone, area = rom[at], rom[at + 1]
        lay = layout_of(rom, at)
        try:
            info = scene_probe.map_items(rom, zone, area)
        except Exception:
            info = {"regions": [], "items": []}
        tables = sorted({r.get("table") for _, r in info["regions"] if r.get("table")} |
                        {i.get("table") for i in info["items"] if i.get("table")})
        rows.append({
            "index": k, "zone": zone, "area": area, "entry": at,
            "variations": rom[at + 2], "regions": rom[at + 3], "items": rom[at + 4],
            "combat": u32(rom, at + 8), "banner": u32(rom, at + 0x0C),
            "word24": u32(rom, at + 0x24), "enter": u32(rom, at + 0x30), "leave": u32(rom, at + 0x34),
            "layout": (lay + ROM_BASE) if lay else 0,
            "props": u32(rom, lay + L_PROP_COUNT) if lay else 0,
            "warps": u32(rom, lay + L_WARP_COUNT) if lay else 0,
            "collision": u32(rom, lay + L_COLLISION) if lay else 0,
            "scene_tables": [t for t in tables],
            "region_kinds": sorted({r.get("kind", "?") for _, r in info["regions"]}),
            "item_kinds": sorted({i.get("kind", "?") for i in info["items"]}),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    out_name(rom_path, "map-index", "json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    out = [f"# Map index, {len(rows)} maps", "",
           f"Source: `{rom_path.name}`, table resolved from this ROM's own literal.", "",
           "## Entry field shapes, counted across every map", "",
           "A field is described from the population, never from one example.", ""] + audit_lines + [
           "", "## The maps", "",
           "`combat` non-zero means the player can attack on that map.", "",
           "| # | map | var | reg | item | combat | banner | props | warps | layout | scene tables |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        ts = ", ".join(f"`0x{t:X}`" for t in r["scene_tables"][:3]) or "-"
        out.append(f"| {r['index']} | **{r['zone']},{r['area']}** | {r['variations']} | {r['regions']} | "
                   f"{r['items']} | {r['combat']} | {r['banner']} | {r['props']} | {r['warps']} | "
                   f"`0x{r['layout']:X}` | {ts} |")
    out_name(rom_path, "map-index", "md").write_text("\n".join(out), encoding="utf-8")
    combat = sum(1 for r in rows if r["combat"])
    print(f"{len(rows)} maps indexed, {combat} with combat on, "
          f"{sum(1 for r in rows if r['props'])} with props, {sum(1 for r in rows if r['warps'])} with doors")
    print("\n".join(audit_lines))
    print(f"wrote {out_name(rom_path, "map-index", "md")}")


if __name__ == "__main__":
    main(sys.argv[1:])
