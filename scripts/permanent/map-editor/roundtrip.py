r"""
roundtrip.py - Prove a map leaves the ROM, passes through the editor's file, and comes back whole.

Usage:   py -3.14 -P scripts\permanent\map-editor\roundtrip.py --rom <a 16 MB build> [--map 7,15]
         As a module: sys.path must hold scripts\permanent\map-editor (the folder name has a
         hyphen, so it is not an importable package), then `import roundtrip`.
         check(rom, zone, area) -> {"ok", "problems", "lost", "skipped"}
         trip(rom, doc) -> (new rom, the document read back, zone, area)
         differences(before, after, rom_before, rom_after) -> ["problem", ...]
Writes:  one JSON document per map into a folder the caller names, and nothing else. No ROM file is
         written, nothing goes under data\, and the ROM passed in is never changed.

CONTENT, NOT BYTES. The trip is read_map -> save -> load -> apply -> read_map, and the two ends are
         compared as DECODED documents. A byte comparison of the blob cannot work: maps 6,1 and 4,50
         share one frame pointer, so re-encoding loses frame bytes without losing a single pixel.
PIXELS, NOT PAIRS. A tile is (chunk, tile) in SOME chunk table, and a document that did not record
         which one resolved its pairs against the shared pool. On every current build map 14,4 names
         its own table at 0x0890A92C, so 72 of its tiles came back as another map's art with no
         error anywhere. So `differences` resolves both sides to 64 byte PIXELS, each through its own
         document's `chunk_table` in its own ROM, and a pair comparison is never enough.
WHOLE DOCUMENT. `CARRIED` plus `SKIPPED` must equal a document's keys, and `unknown_fields` reports
         anything else. A field added later and compared by nobody is how a round trip goes green
         while losing something.
LOST, NOT FAILED. A map whose layout carried props, doors or a non-tilemap layer comes back without
         them: the editor does not hold them, `read_map` says so in `dropped`, and the trip reports
         them under "lost". That is a real loss in the game and it is counted apart from a failure.
Skipped: map 1,7 has no tilemap layer at all, so `read_map` refuses it, and map 6,99's 1 x 1 art grid
         cannot cover its 4096 x 3328 px world, so `validate` refuses the document. Both are true of
         the map and not of the reader, so they are reported as skipped and never as a pass.
"""
import argparse
import json
import sys
from pathlib import Path

for _folder in (Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
    sys.path.insert(0, str(_folder))              # -P omits the script folder; scene\ is one up

from scene import scene_probe                                              # noqa: E402
import import_map                                                          # noqa: E402
import map_file                                                            # noqa: E402

# ===== CONFIG =====
CARRIED = ("schema", "world", "blocks", "chunk_table", "layers", "collision", "terrain",
           "tiles", "animated", "stamps", "blend", "unread")
SKIPPED = ("dropped",)                      # read_map's note of what the editor cannot hold
LAYER_FIELDS = ("priority", "scroll", "offset", "cells")
SLOT_FIRST = 0xC0                           # a free (zone, area) is searched from here: vanilla
SLOT_LAST = 0xFE                            # zones run to 14 and every module so far stays below
SCRATCH = Path(__file__).resolve().parents[3] / "scratch" / "roundtrip"   # never the owner's maps\


# ===== the whole document =====

def unknown_fields(doc: dict) -> list:
    """Keys no comparison covers. A new field must be added to CARRIED, never left to silence."""
    known = set(CARRIED) | set(SKIPPED)
    return [f"{name}: this field is in the document and nothing compares it"
            for name in sorted(set(doc) - known)]


# ===== the comparison =====

def pixels(rom: bytes, doc: dict) -> list:
    """The 64 byte tiles this document's pairs name, through ITS OWN chunk table in THIS rom."""
    table = doc.get("chunk_table")
    if not isinstance(table, int):
        raise ValueError("this document names no chunk_table, so its tile pairs name no art")
    return scene_probe.chunk_tiles(rom, [tuple(p) for p in doc["tiles"]],
                                   scene_probe.rom_offset(rom, table, "the document's chunk table"))


def _bytes_differ(name: str, before: list, after: list, problems: list) -> None:
    """A 8192 byte grid, reported as a count and a first index. Never dumped into a message."""
    if before == after:
        return
    if len(before) != len(after):
        problems.append(f"{name}: {len(before)} bytes became {len(after)}")
        return
    bad = [n for n, (a, b) in enumerate(zip(before, after)) if a != b]
    problems.append(f"{name}: {len(bad)} of {len(before)} bytes differ, the first at {bad[0]}")


def _layers_differ(before: dict, after: dict, problems: list) -> None:
    if set(before) != set(after):
        problems.append(f"layers: {sorted(before)} became {sorted(after)}")
        return
    for name in sorted(before):
        one, two = before[name], after[name]
        for field in LAYER_FIELDS:
            if one.get(field) == two.get(field):
                continue
            if field != "cells":
                problems.append(f"layer {name} {field}: {one.get(field)!r} became {two.get(field)!r}")
                continue
            if len(one["cells"]) != len(two["cells"]):
                problems.append(f"layer {name} cells: {len(one['cells'])} became {len(two['cells'])}")
                continue
            bad = [n for n, (a, b) in enumerate(zip(one["cells"], two["cells"])) if a != b]
            problems.append(f"layer {name} cells: {len(bad)} of {len(one['cells'])} differ, the "
                            f"first at {bad[0]}")


def differences(before: dict, after: dict, rom_before: bytes, rom_after: bytes) -> list:
    """Every way these two documents are not the same map. Empty means the trip lost nothing."""
    problems = unknown_fields(before) + unknown_fields(after)
    for name in CARRIED:
        if name in ("layers", "collision", "terrain", "tiles"):
            continue
        if before.get(name) != after.get(name):
            problems.append(f"{name}: {before.get(name)!r} became {after.get(name)!r}")
    _layers_differ(before.get("layers") or {}, after.get("layers") or {}, problems)
    _bytes_differ("collision", before.get("collision"), after.get("collision"), problems)
    _bytes_differ("terrain", before.get("terrain"), after.get("terrain"), problems)

    one, two = pixels(rom_before, before), pixels(rom_after, after)
    if one != two:
        bad = [n for n, (a, b) in enumerate(zip(one, two)) if a != b]
        problems.append(f"tiles: {len(one)} tiles became {len(two)} and {len(bad)} sets of pixels "
                        f"differ, the first at slot {bad[0] if bad else len(min(one, two, key=len))}")
    return problems


# ===== the trip =====

def free_slot(rom: bytes) -> tuple:
    """A (zone, area) this ROM's map table has not got. `apply` refuses a pair it already holds."""
    table, count = import_map.map_table(rom)
    taken = {(rom[table + import_map.MAP_SIZE * k], rom[table + import_map.MAP_SIZE * k + 1])
             for k in range(count)}
    for zone in range(SLOT_FIRST, SLOT_LAST + 1):
        if (zone, SLOT_FIRST) not in taken:
            return zone, SLOT_FIRST
    raise ValueError("this ROM's map table has no free (zone, area) in the search range")


def through_a_file(doc: dict, folder: Path) -> dict:
    """Save the document and read it back, which is the path the editor's own Save takes.

    map_file.save validates and never overwrites, so a name already used raises here rather than
    quietly reusing an older map."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    name = f"trip_{doc['blocks'][0]}x{doc['blocks'][1]}_{len(doc['tiles'])}_{id(doc):x}.json"
    path = folder / name
    map_file.save(doc, path)
    return map_file.load(path)


def trip(rom: bytes, doc: dict, zone: int = None, area: int = None, folder: Path = None) -> tuple:
    """read_map's document -> a file -> apply -> read_map. Returns (new rom, document, zone, area).

    The ROM given is never changed: `apply` returns a new one."""
    if zone is None or area is None:
        zone, area = free_slot(rom)
    saved = through_a_file(doc, folder or SCRATCH)      # never maps\: that is the owner's
    new = import_map.apply(rom, saved, zone, area)
    return new, map_file.read_map(new, zone, area), zone, area


def check(rom: bytes, zone: int, area: int, var: int = 1, folder: Path = None) -> dict:
    """One map out of this ROM and back. `skipped` names a map the editor cannot hold at all."""
    out = {"map": (zone, area, var), "ok": False, "problems": [], "lost": [], "skipped": None}
    try:
        doc = map_file.read_map(rom, zone, area, var)
    except Exception as exc:                                  # noqa: BLE001 (a census must go on)
        out["skipped"] = f"read_map refused it: {exc}"
        return out
    out["lost"] = list(doc.get("dropped") or [])
    unsound = map_file.validate(doc)
    if unsound:
        out["skipped"] = "the map's own document is not sound: " + "; ".join(unsound)
        return out
    try:
        new, back, into_zone, into_area = trip(rom, doc, folder=folder)
    except Exception as exc:                                  # noqa: BLE001 (a census must go on)
        out["problems"] = [f"the trip raised: {exc}"]
        return out
    out["into"] = (into_zone, into_area)
    out["problems"] = differences(doc, back, rom, new)
    out["ok"] = not out["problems"]
    return out


# ===== every map in a ROM =====

def census(rom: bytes, folder: Path) -> list:
    """Every layout this ROM's map table reaches, out and back. One row per (zone, area, var)."""
    table, count = import_map.map_table(rom)
    rows = []
    for k in range(count):
        off = table + import_map.MAP_SIZE * k
        zone, area = rom[off], rom[off + 1]
        for var in range(1, max(1, rom[off + 2]) + 1):
            rows.append(check(rom, zone, area, var, folder))
    return rows


def _main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Take a map out of a ROM, through a file, and back.")
    ap.add_argument("--rom", required=True, help="a 16 MB build; the 8 MB base has no free space")
    ap.add_argument("--map", help="one map as zone,area; the default is every map in the table")
    ap.add_argument("--out", help=r"the folder the documents go into; the default is scratch\roundtrip")
    args = ap.parse_args(argv)

    rom = Path(args.rom).read_bytes()
    folder = Path(args.out).resolve() if args.out else SCRATCH
    if "data" in (part.lower() for part in folder.parts):
        raise ValueError(f"{folder} is under a data folder, and nothing here writes there")
    if args.map:
        zone, area = (int(v) for v in args.map.split(","))
        rows = [check(rom, zone, area, folder=folder)]
    else:
        rows = census(rom, folder)

    good = [r for r in rows if r["ok"]]
    skipped = [r for r in rows if r["skipped"]]
    bad = [r for r in rows if not r["ok"] and not r["skipped"]]
    lost = [r for r in good if r["lost"]]
    for row in bad:
        print(f"map {row['map'][0]},{row['map'][1]} v{row['map'][2]} FAILED")
        for problem in row["problems"][:6]:
            print(f"    {problem}")
    for row in skipped:
        print(f"map {row['map'][0]},{row['map'][1]} v{row['map'][2]} skipped: {row['skipped'][:110]}")
    print(f"\n{len(good)} of {len(rows)} layouts came back unchanged, {len(bad)} failed, "
          f"{len(skipped)} skipped")
    print(f"{len(lost)} of the {len(good)} passes lost props, doors or a non-tilemap layer")
    print(f"documents written to {folder}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
