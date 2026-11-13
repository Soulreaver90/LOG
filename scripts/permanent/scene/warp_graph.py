r"""
warp_graph.py - Every door in the game: the full map-to-map connectivity graph, from BOTH carriers.

Usage:   py -3.14 -P scripts\permanent\scene\warp_graph.py
         --rom <path> reads a build. --from 6,1 or --to 6,2 filters. --orphans lists unreachable maps.
Output:  docs\research\warp-graph.md and .json. Reads only; writes no ROM.
Why:     a map carries its doors in TWO places and reading one of them is a documented trap. The arena
         emptied the region list, kept the layout list, and the owner walked off the map: "if you exit
         the area and go back, it breask everything". Nothing in the project could list a map's exits.
Reads:   carrier A, map entry +0x10, the REGION list: pairs of {condition, item pointer}, no count,
         ending at the first pair whose item does not open with a code factory (bible row 1018).
         carrier B, LAYOUT +0x40 count and +0x44 list: the map's own door list, decoded by
         scene_probe.layout_doors. The list holds POINTERS to items, not inline items, the same shape
         as the map entry's +0x14. Reading it as inline items finds zero doors in the whole game while
         +0x40 says 283 maps have them, which is how that error shows itself.
         A warp item is {factory, trigger, s16 x0 y0 x1 y1, then {u8 dir, zone, area, var, s16 x, y}},
         factory @0x0800C233 or @0x0800D9C3 (bible row 718).
Limits:  a map reached only by a script `ext 35/38/39` is NOT an edge here. The op index
         (scene-op-usage.md) lists those separately, and the two together are still a floor.
"""
TOOL_INDEX_NOTE = ("**A map carries doors in TWO places.** The region list holds 69 of the game's "
                   "655 doors; the other 586 are in the layout door list at `+0x40`/`+0x44`, which "
                   "holds POINTERS to items, not items. This graph is every map at once; for ONE map "
                   "end to end, with both carriers labelled, run `scene_probe --map`.")

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
WARP_FACTORIES = (0x0800C233, 0x0800D9C3)
REGION_SIZE = 8
# No layout door offsets here on purpose: scene_probe.layout_doors owns that decode, and a second copy
# of +0x40 and +0x44 is how two tools come to report different doors for one map.


def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def is_pointer(word: int) -> bool:
    return 0x08000000 <= word < 0x08000000 + 0x2000000


def warp_at(rom: bytes, at: int):
    """One warp item, or None when the item at this offset is not a warp."""
    factory = u32(rom, at)
    if (factory & ~1) not in (f & ~1 for f in WARP_FACTORIES):
        return None
    x0, y0, x1, y1 = struct.unpack_from("<4h", rom, at + 8)
    direction, zone, area, var = rom[at + 0x10:at + 0x14]
    x, y = struct.unpack_from("<2h", rom, at + 0x14)
    return {"at": at, "rect": (x0, y0, x1, y1), "to": (zone, area, var),
            "landing": (x, y), "dir": direction}


def layout_of(rom: bytes, entry: int, var: int = 1):
    """The layout file offset of one variation, through the one chain walker in scene_probe."""
    chain = scene_probe.layouts(rom, entry)
    return chain[var - 1] if chain and var <= len(chain) else None


def doors(rom: bytes, entry: int) -> list:
    """Every warp of one map, from both carriers, each tagged with which list it came from.

    Both carriers are decoded by scene_probe, the section 9 reader, so this graph and a single
    `scene_probe --map` listing can never disagree about one map's doors."""
    out = []
    region_list = u32(rom, entry + 0x10)
    if is_pointer(region_list):
        base = region_list - ROM_BASE
        for i in range(64):
            cond, pointer = u32(rom, base + REGION_SIZE * i), u32(rom, base + REGION_SIZE * i + 4)
            if not is_pointer(pointer):
                break
            w = warp_at(rom, pointer - ROM_BASE)
            if w:
                out.append({**w, "carrier": "region", "condition": cond})
    lay = layout_of(rom, entry)
    if lay is not None:
        for it in scene_probe.layout_doors(rom, lay)["doors"]:
            out.append({"at": it["at"], "rect": it["rect"], "to": it["to"], "landing": it["landing"],
                        "dir": it["direction"], "carrier": "layout", "condition": 0})
    return out



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

    graph, edges = {}, 0
    for k in range(count):
        at = table + scene_probe.MAP_SIZE * k
        key = f"{rom[at]},{rom[at + 1]}"
        graph[key] = doors(rom, at)
        edges += len(graph[key])

    def want(key: str, w: dict) -> bool:
        if "--from" in argv and key != argv[argv.index("--from") + 1]:
            return False
        if "--to" in argv and f"{w['to'][0]},{w['to'][1]}" != argv[argv.index("--to") + 1]:
            return False
        return True

    if "--from" in argv or "--to" in argv:
        for key, ws in sorted(graph.items()):
            for w in ws:
                if want(key, w):
                    print(f"  {key:8s} -> {w['to'][0]},{w['to'][1]} var {w['to'][2]}  "
                          f"at {w['landing']} dir {w['dir']}  rect {w['rect']}  [{w['carrier']}]")
        return

    reached = {f"{w['to'][0]},{w['to'][1]}" for ws in graph.values() for w in ws}
    orphans = sorted(k for k in graph if k not in reached)
    if "--orphans" in argv:
        print(f"{len(orphans)} maps no door leads to:")
        print(", ".join(orphans))
        return

    OUT.mkdir(parents=True, exist_ok=True)
    out_name(rom_path, "warp-graph", "json").write_text(json.dumps(graph, indent=1), encoding="utf-8")
    by_carrier = {"region": 0, "layout": 0}
    for ws in graph.values():
        for w in ws:
            by_carrier[w["carrier"]] += 1
    out = [f"# Warp graph, every door in the game", "",
           f"Source: `{rom_path.name}`. **{edges}** doors across **{len(graph)}** maps: "
           f"{by_carrier['layout']} in layout door lists, {by_carrier['region']} in region lists.", "",
           "> A map carries doors in TWO places. Reading only the region list misses most of them.",
           "> A map entered only by a script `ext 35/38/39` has no edge here, so this is a FLOOR.", "",
           f"**{len(orphans)} maps have no door leading to them** and are reached by script, by the world",
           "map, or not at all: " + (", ".join(orphans) or "none"), "",
           "| map | doors | leads to |", "| --- | --- | --- |"]
    for key, ws in sorted(graph.items(), key=lambda kv: [int(x) for x in kv[0].split(",")]):
        if not ws:
            continue
        dests = sorted({f"{w['to'][0]},{w['to'][1]}" for w in ws})
        out.append(f"| **{key}** | {len(ws)} | {', '.join(dests)} |")
    out_name(rom_path, "warp-graph", "md").write_text("\n".join(out), encoding="utf-8")
    print(f"{edges} doors across {len(graph)} maps "
          f"({by_carrier['layout']} layout, {by_carrier['region']} region), {len(orphans)} orphan maps")
    print(f"wrote {out_name(rom_path, "warp-graph", "md")}")


if __name__ == "__main__":
    main(sys.argv[1:])
