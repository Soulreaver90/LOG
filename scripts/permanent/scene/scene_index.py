r"""
scene_index.py - One line per scene: what every vanilla scene table actually DOES.

Usage:   py -3.14 -P scripts\permanent\scene\scene_index.py
         --rom <path> indexes a build. --does fight|load|camera|form|flag filters to scenes with that
         capability. --table 0x3E47F8 prints one scene's capability line.
Output:  docs\research\scene-index.md and .json. Reads only; writes no ROM.
Why:     "where does vanilla already do X" was answered by writing new code seven times in one day. With
         this page it is a filter. `--does fight` lists every fight start in the game.
Reads:   the same map-owned tables as op_usage.py, through scene_probe, which resolves THIS ROM's map
         table. Capabilities are read from the folded ops of every kind 0 record in the table.
Limits:  a table named only by code, by another table's next index, or by a script region's script is
         NOT reached. The ending table rom:0x3B8140 is one of those. Counts here are a FLOOR.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder

import log_paths  # noqa: E402
from scene import op_usage                                              # noqa: E402
from scene import scene_lib as S                                        # noqa: E402

# ===== CONFIG =====
BASE = log_paths.BASE_ROM
OUT = log_paths.RESEARCH

# capability: the ext ops that prove it
CAPABILITY = {
    "fight": (104,),                 # Sprite_ReplaceWithEntry: an NPC becomes the fightable enemy
    "bar": (85, 90),                 # a boss bar is raised
    "hud": (86,),                    # the header bit that shows the HUD
    "load": (35, 38, 39),            # a map load
    "camera": (31,),                 # a fixed camera is parked
    "follow": (33, 37, 119),         # the camera is handed back
    "cover": (40, 41, 42, 43),       # a fade or flash
    "form": (73,),                   # an appearance change
    "leader": (70, 115),             # the controlled character changes
    "party": (29, 30, 79, 91),
    "spawn": (51,),
    "attack": (96, 112),
}
FLAG_SET, FLAG_TEST = (27, 28), (19, 20)


def capabilities(rom: bytes) -> dict:
    """{table: {...}} summarising every map-owned scene table."""
    tables = op_usage.scene_tables(rom)
    records = op_usage.record_addresses(rom, tables)   # pass 1: exact lengths in pass 2
    out = {}
    for table, owners in sorted(tables.items()):
        try:
            words = S.walk(rom, table, S.table_length(rom, table, records=records))
        except Exception:
            continue
        seen, flags_set, flags_tested, loads, records = set(), set(), set(), [], 0
        for i, word in words.items():
            if S.is_end_entry(word):
                continue
            try:
                rec = S.decode_record(rom, word - S.ROM_BASE)
            except Exception:
                continue
            if rec.kind != 0:
                continue
            records += 1
            for _, ext_n, args in op_usage.record_ops(rom, rec):
                seen.add(ext_n)
                if ext_n in FLAG_SET and args:
                    flags_set.add(args[-1])
                if ext_n in FLAG_TEST and args:
                    flags_tested.add(args[-1])
                if ext_n in CAPABILITY["load"] and len(args) >= 2:
                    loads.append(f"{args[0]},{args[1]}")
        has = sorted(name for name, ops in CAPABILITY.items() if seen & set(ops))
        out[table] = {
            "table": table, "map": f"{owners[0][0]},{owners[0][1]}" if owners else "?",
            "owners": sorted({f"{z},{a}" for z, a, _ in owners}),
            "words": len(words), "records": records, "does": has,
            "flags_set": sorted(flags_set), "flags_tested": sorted(flags_tested),
            "loads": sorted(set(loads)), "ops": sorted(o for o in seen if o is not None),
        }
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
    index = capabilities(rom)

    if "--table" in argv:
        at = int(argv[argv.index("--table") + 1], 0)
        row = index.get(at)
        print(json.dumps(row, indent=1) if row else f"rom:0x{at:X} is not a map-owned table")
        return

    if "--does" in argv:
        want = argv[argv.index("--does") + 1]
        hits = [r for r in index.values() if want in r["does"]]
        for r in sorted(hits, key=lambda r: r["table"]):
            print(f"  rom:0x{r['table']:X}  map {r['map']:8s} {r['records']:3d} records  "
                  f"{', '.join(r['does'])}")
        print(f"{len(hits)} scenes do '{want}' (of {len(index)} reached)")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    out_name(rom_path, "scene-index", "json").write_text(
        json.dumps({f"0x{k:X}": v for k, v in sorted(index.items())}, indent=1), encoding="utf-8")

    counts = {name: sum(1 for r in index.values() if name in r["does"]) for name in CAPABILITY}
    out = [f"# What every vanilla scene does", "",
           f"Source: `{rom_path.name}`. **{len(index)}** map-owned scene tables reached.", "",
           "> A table named only by code, by another table's next index, or by a script region's script",
           "> is NOT reached. The ending table `rom:0x3B8140` is one of those. These counts are a FLOOR.", "",
           "## How many scenes do each thing", "",
           "| capability | ops that prove it | scenes |", "| --- | --- | --- |"]
    for name, ops in CAPABILITY.items():
        out.append(f"| {name} | {', '.join(f'ext {o}' for o in ops)} | **{counts[name]}** |")
    out += ["", "## Every scene", "",
            "| table | map | records | does | loads | flags set |", "| --- | --- | --- | --- | --- | --- |"]
    for r in sorted(index.values(), key=lambda r: r["table"]):
        out.append(f"| `0x{r['table']:X}` | {r['map']} | {r['records']} | {', '.join(r['does']) or '-'} | "
                   f"{', '.join(r['loads']) or '-'} | {', '.join(str(f) for f in r['flags_set']) or '-'} |")
    out_name(rom_path, "scene-index", "md").write_text("\n".join(out), encoding="utf-8")
    print(f"{len(index)} scenes indexed")
    print("  " + ", ".join(f"{k}:{v}" for k, v in counts.items()))
    print(f"wrote {out_name(rom_path, "scene-index", "md")}")


if __name__ == "__main__":
    main(sys.argv[1:])
