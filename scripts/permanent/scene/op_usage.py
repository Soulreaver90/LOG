r"""
op_usage.py - Reverse index: for every scene-VM ext op, every vanilla record that uses it.

Usage:   py -3.14 -P scripts\permanent\scene\op_usage.py
         --rom <path> indexes a build. --op N prints one op's sites. --flags writes the flag index,
         and --flag N prints every record that sets, clears or tests story flag N.
Output:  docs\research\scene-op-usage.md and .json. Reads only; writes no ROM.
Why:     "does vanilla already do X, and where" should be a lookup, not a study. Seven arena builds went
         out in one day because that question kept being answered by writing new code. The vanilla fight
         start, the camera hand-back and the actor swap were all already in the ROM.
Reads:   every map entry's scene tables, through scene_probe.map_items, which resolves THIS ROM's own map
         table. A map carries scene tables in two places: region list entries of kind `scene`, and item
         list entries of kind `talk` or `group`. Reading only the region list misses the Cell Games
         scenes (bible SS3).
Address: a site's address is the EXT OP itself, not the push before it. Many bible rows cite the push,
         which sits 2 bytes earlier for a one byte push: row 814's Red Card give `0x083D045B` is this
         index's `rom:0x3D045D`. The two are the same site; do not read the difference as a disagreement.
Limits:  this walks tables a MAP owns. It cannot reach a table named only by code, by another table's
         next index, or by a script region's script, so a count here is a FLOOR, never a total. Say "the
         walk found N", never "there are N".
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder

from scene import scene_lib as S                                         # noqa: E402
from scene import scene_probe                                            # noqa: E402

# ===== CONFIG =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
OUT = ROOT / "docs" / "research"
EXAMPLES = 10                       # sites listed per op; the count is always the full one
PUSH_OPS = (0, 1, 29)               # the ops that leave values for an ext op to consume
FLAG_OPS = {27: "set", 28: "clear", 19: "test", 20: "test_alt"}   # each takes the flag as its last value


def table_end_full(rom: bytes, at: int, limit: int = 256, records: set = None) -> int:
    """The real word count of a scene table. Kept as the name this page was first written with;
    the walker itself now lives in scene_lib.table_length(), so one rule serves every tool."""
    return S.table_length(rom, at, limit, records)


def _note_bad(bad: list, table: int) -> None:
    """Record an unreadable table pointer once, however many map entries name it."""
    row = (table, "table: not a readable ROM offset")
    if bad is not None and row not in bad:
        bad.append(row)


def scene_tables(rom: bytes, bad: list = None) -> dict:
    """{table file offset: [(zone, area, how)]} for every table a map owns.
    A pointer that is not a readable ROM offset is left out and appended to bad, if given. Map 6,3
    names a null one. It must be reported, never dropped in silence and never walked."""
    out, table, count = {}, *scene_probe.map_table(rom)
    for k in range(count):
        at = table + scene_probe.MAP_SIZE * k
        zone, area = rom[at], rom[at + 1]
        try:
            info = scene_probe.map_items(rom, zone, area)
        except Exception:
            continue
        for _, region in info.get("regions", []):
            if region.get("kind") == "scene" and region.get("table"):
                if not 0 <= region["table"] < len(rom):
                    _note_bad(bad, region["table"])
                    continue
                out.setdefault(region["table"], []).append((zone, area, "region"))
        for item in info.get("items", []):
            if item.get("table"):
                if not 0 <= item["table"] < len(rom):
                    _note_bad(bad, item["table"])
                    continue
                out.setdefault(item["table"], []).append((zone, area, item["kind"]))
    return out


def record_addresses(rom: bytes, tables=None) -> set:
    """Every file offset a scene table names as a record.

    This is what makes a table length exact. A record header below 0x10000 looks exactly like an
    END entry, so a walk with no record set reads one word too far on 150 of the 302 tables."""
    tables = sorted(tables if tables is not None else scene_tables(rom))
    out = set()
    for at in tables:
        if not 0 <= at < len(rom):
            continue
        for word in S.table_words(rom, at, S.table_length(rom, at)):
            if not S.is_end_entry(word) and S.is_record_pointer(word):
                out.add(word - S.ROM_BASE)
    return out


def record_ops(rom: bytes, rec) -> list:
    """[(op_offset, ext_number, [folded arguments])] for one code record.

    An ext op carries no operands of its own: the values were pushed by the ops before it. Folding them
    is what makes the index say `load_map(6,1,1,136,432)` instead of `ext 35`."""
    out, pending = [], []
    for op in rec.code:
        if op.op in PUSH_OPS:
            pending += op.args
        elif op.op == 2:
            out.append((op.at, op.ext, pending))
            pending = []
        else:
            pending = []
    return out


def index(rom: bytes) -> tuple:
    """({ext: [site]}, stats). A site is {table, record, at, args, map}."""
    uses, broken = {}, []
    tables = scene_tables(rom, broken)
    records = record_addresses(rom, tables)        # pass 1, so pass 2 reads each table exactly
    for table, owners in sorted(tables.items()):
        try:
            words = S.walk(rom, table, S.table_length(rom, table, records=records))
        except Exception as exc:
            broken.append((table, f"table: {exc}"))
            continue
        for i, word in words.items():
            if S.is_end_entry(word):
                continue
            at = word - S.ROM_BASE
            try:
                rec = S.decode_record(rom, at)
            except Exception as exc:
                broken.append((at, f"record: {exc}"))
                continue
            if rec.kind != 0:
                continue
            for off, ext_n, args in record_ops(rom, rec):
                uses.setdefault(ext_n, []).append(
                    {"at": off, "record": at, "table": table, "index": i,
                     "args": args, "map": f"{owners[0][0]},{owners[0][1]}" if owners else "?"})
    return uses, {"tables": len(tables), "broken": broken}



def out_name(rom_path: Path, stem: str, ext: str) -> Path:
    """The page for the BASE ROM keeps its plain name; any other ROM gets its own file.

    Without this a `--rom <build>` run silently overwrites the vanilla reference page with build data,
    and the next reader takes a build's numbers for the game's."""
    if rom_path.resolve() == BASE.resolve():
        return OUT / f"{stem}.{ext}"
    return OUT / f"{stem}--{rom_path.stem}.{ext}"

def flag_sites(uses: dict) -> dict:
    """{flag: {set|clear|test|test_alt: [site]}}. The flag is the LAST value pushed before the op, which
    is what the handler pops first."""
    out = {}
    for ext_n, how in FLAG_OPS.items():
        for s in uses.get(ext_n, []):
            if not s["args"]:
                continue
            out.setdefault(s["args"][-1], {}).setdefault(how, []).append(s)
    return out


def main(argv: list) -> None:
    rom_path, only = BASE, None
    for i, a in enumerate(argv):
        if a == "--rom":
            rom_path = Path(argv[i + 1])
        elif a == "--op":
            only = int(argv[i + 1], 0)
    rom = rom_path.read_bytes()
    uses, stats = index(rom)

    if only is not None:
        for s in uses.get(only, []):
            print(f"  rom:0x{s['at']:X}  map {s['map']:7s} table rom:0x{s['table']:X}[{s['index']}]  "
                  f"{S.op_name(only)}({', '.join(str(v) for v in s['args'])})")
        print(f"{len(uses.get(only, []))} sites for ext {only}")
        return

    flags = flag_sites(uses)
    if "--flag" in argv:
        n = int(argv[argv.index("--flag") + 1], 0)
        for how, sites in sorted(flags.get(n, {}).items()):
            for s in sites:
                print(f"  {how:9s} rom:0x{s['at']:X}  map {s['map']:8s} "
                      f"table rom:0x{s['table']:X}[{s['index']}]")
        print(f"flag {n}: " + (", ".join(f"{h} x{len(v)}" for h, v in sorted(flags.get(n, {}).items()))
                               or "no reached scene touches it"))
        return

    if "--flags" in argv:
        OUT.mkdir(parents=True, exist_ok=True)
        lines = ["# Story flag index", "",
                 f"Source: `{rom_path.name}`. **{len(flags)}** distinct flags are touched by map-owned",
                 "scenes.", "",
                 "> The walk cannot reach a table named only by code, so this is a FLOOR. A flag set only",
                 "> from Thumb code, or pushed as a computed value, does not appear here.", "",
                 "| flag | set | cleared | tested | first setter |", "| --- | --- | --- | --- | --- |"]
        for n in sorted(flags):
            k = flags[n]
            first = k.get("set", [{}])[0].get("at")
            lines.append(f"| {n} | {len(k.get('set', []))} | {len(k.get('clear', []))} | "
                         f"{len(k.get('test', [])) + len(k.get('test_alt', []))} | "
                         + (f"`rom:0x{first:X}`" if first else "-") + " |")
        target = out_name(rom_path, "flag-index", "md")
        target.write_text(chr(10).join(lines), encoding="utf-8")
        never = [n for n in sorted(flags) if "set" not in flags[n]]
        print(f"{len(flags)} flags indexed; {len(never)} are tested but never set by any reached scene")
        print(f"wrote {target}")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    out_name(rom_path, "scene-op-usage", "json").write_text(json.dumps(
        {str(k): v for k, v in sorted(uses.items())}, indent=1), encoding="utf-8")

    total = sum(len(v) for v in uses.values())
    out = [f"# Which vanilla records use which scene op", "",
           f"Source: `{rom_path.name}`. The walk reached **{stats['tables']}** map-owned scene tables and",
           f"**{total}** ext op sites across **{len(uses)}** distinct ops.", "",
           "> This walks tables a MAP owns. A table named only by code, by another table's next index, or",
           "> by a script region's script is NOT reached, so every count here is a FLOOR. Say \"the walk",
           "> found N\", never \"there are N\".", "",
           "| ext | name | sites | example calls |", "| --- | --- | --- | --- |"]
    for n in sorted(uses):
        sites = uses[n]
        shown = []
        for s in sites[:3]:
            shown.append(f"`rom:0x{s['at']:X}` ({', '.join(str(v) for v in s['args'])})")
        out.append(f"| {n} | {S.op_name(n)} | **{len(sites)}** | {'; '.join(shown)} |")

    out += ["", "## Ops the handler table defines but this walk never saw", "",
            "An op with no site here is not unused: it may live in a table the walk cannot reach.", ""]
    unseen = [n for n in range(145) if n not in uses]
    out.append(", ".join(f"ext {n}" for n in unseen) or "none")

    if stats["broken"]:
        out += ["", f"## Records the decoder could not read ({len(stats['broken'])})", ""]
        out += [f"- `rom:0x{a:X}` {why}" for a, why in stats["broken"][:40]]
    out_name(rom_path, "scene-op-usage", "md").write_text("\n".join(out), encoding="utf-8")
    print(f"{stats['tables']} tables, {total} op sites, {len(uses)} distinct ops, "
          f"{len(stats['broken'])} unreadable")
    print(f"wrote {out_name(rom_path, "scene-op-usage", "md")}")


if __name__ == "__main__":
    main(sys.argv[1:])
