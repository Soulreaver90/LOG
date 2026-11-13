r"""
item_index.py - Every inventory item: its id, name, description and handler.

Usage:   py -3.14 -P scripts\permanent\rom\item_index.py
         --rom <path> reads a build. --find senzu searches names and descriptions.
Output:  docs\research\item-index.md and .json. Reads only; writes no ROM.
Why:     scene records address items by NUMBER (`push 41 ; ext 26` gives the Red Card). Without a table
         every item op in the game has to be traced by hand to find out what it gives.
Reads:   item table `rom:0x6ADE24`, 0x38 bytes an entry (bible row 468 pins the table and the stride
         through the STR, POW and END handlers at +0x30). Entry `+0x04` is a u16 NAME index and `+0x06`
         a u16 DESCRIPTION index into the 260-entry UI string table `rom:0x0E2840`, whose pointers reach
         the string pool `rom:0x0E2C50` (bible row 1102). **`+0x30` is the item's OWN handler** and
         `+0x34` is a handler shared by every real item, so the two must not be swapped: 46 of the 50
         items hold the same value at `+0x34`, while `+0x30` differs per item. Bible row 468 pins this
         by address: the STR handler word for item 2 is `rom:0x6ADEC4`, which is table + 0x38 x 2 + 0x30.
Count:   the table ends at item 49: item 49 is the last entry whose `+0x34` holds a Thumb code pointer.
         So there are 50 items, 0 to 49. Bible row 367 speaks of "97 of 100" icon fields, which read
         past the end; that row needs re-checking against this count.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P omits the script folder
import log_paths  # noqa: E402

# ===== CONFIG =====
BASE = log_paths.BASE_ROM
OUT = log_paths.RESEARCH
TABLE, STRIDE = 0x6ADE24, 0x38
STRING_TABLE = 0x0E2840
F_NAME, F_DESC, F_HANDLER, F_SHARED = 0x04, 0x06, 0x30, 0x34
ROM_BASE, CODE_TOP = 0x08000000, 0x08100000


def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def u16(rom: bytes, at: int) -> int:
    return struct.unpack_from("<H", rom, at)[0]


def string(rom: bytes, index: int) -> str:
    """One UI string by index. The table aliases, so two indexes may give the same text (row 1102)."""
    pointer = u32(rom, STRING_TABLE + 4 * index)
    if not (ROM_BASE <= pointer < ROM_BASE + 0x2000000):
        return ""
    at = pointer - ROM_BASE
    return bytes(rom[at:rom.index(b"\0", at)]).decode("ascii", "replace")


def last_item(rom: bytes, limit: int = 200) -> int:
    """The highest id whose +0x34 is a Thumb code pointer. Walking a fixed 100 reads past the table."""
    last = 0
    for i in range(limit):
        word = u32(rom, TABLE + STRIDE * i + F_SHARED)
        if ROM_BASE <= word < CODE_TOP and word & 1:
            last = i
    return last


def items(rom: bytes) -> list:
    out = []
    for i in range(last_item(rom) + 1):
        at = TABLE + STRIDE * i
        name_i, desc_i = u16(rom, at + F_NAME), u16(rom, at + F_DESC)
        out.append({"id": i, "at": at, "name": string(rom, name_i), "desc": string(rom, desc_i),
                    "name_index": name_i, "desc_index": desc_i,
                    "handler": u32(rom, at + F_HANDLER),
                    "shared": u32(rom, at + F_SHARED)})
    return out


def out_name(rom_path: Path, stem: str, ext: str) -> Path:
    """The page for the BASE ROM keeps its plain name; any other ROM gets its own file.

    Without this a `--rom <build>` run silently overwrites the vanilla reference page with build
    data, and the next reader takes a build's numbers for the game's."""
    if rom_path.resolve() == BASE.resolve():
        return OUT / f"{stem}.{ext}"
    return OUT / f"{stem}--{rom_path.stem}.{ext}"


def main(argv: list) -> None:
    rom_path = Path(argv[argv.index("--rom") + 1]) if "--rom" in argv else BASE
    rom = rom_path.read_bytes()
    rows = items(rom)

    if "--find" in argv:
        needle = argv[argv.index("--find") + 1].lower()
        for r in rows:
            if needle in r["name"].lower() or needle in r["desc"].lower():
                print(f"  item {r['id']:3d}  {r['name']:22s} {r['desc']}")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    out_name(rom_path, "item-index", "json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    out = [f"# Item index, {len(rows)} items (0 to {rows[-1]['id']})", "",
           f"Source: `{rom_path.name}`. Table `rom:0x{TABLE:X}`, 0x{STRIDE:X} bytes an entry.",
           "Scene records address these by number: `push 41 ; ext 26` gives item 41.", "",
           "| id | name | description | own handler +0x30 |", "| --- | --- | --- | --- |"]
    for r in rows:
        out.append(f"| {r['id']} | **{r['name'] or '-'}** | {r['desc'] or '-'} | "
                   f"`0x{r['handler']:08X}` |")
    out_name(rom_path, "item-index", "md").write_text("\n".join(out), encoding="utf-8")
    named = sum(1 for r in rows if r["name"])
    print(f"{len(rows)} items, {named} named")
    print(f"wrote {out_name(rom_path, 'item-index', 'md')}")


if __name__ == "__main__":
    main(sys.argv[1:])
