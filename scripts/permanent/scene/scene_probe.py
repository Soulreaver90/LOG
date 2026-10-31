r"""
scene_probe.py - Print a scene table, a record, a map's scene items or the uses of a line, as a readable listing.

Usage:   py -3.14 -P scripts\permanent\scene\scene_probe.py --table 0x3DBDD4
         py -3.14 -P scripts\permanent\scene\scene_probe.py --record 0x3DB59C --len 0xCC
         py -3.14 -P scripts\permanent\scene\scene_probe.py --map 6,4
         py -3.14 -P scripts\permanent\scene\scene_probe.py --find-text "You look great"
         Add --rom <path> to read a build instead of the base ROM, and --count N to cap a table walk.
Output:  stdout. The tool never writes to the ROM and never writes a file.
Reads:   scene_lib for the op names, the decoder and the table walker. Map facts are the bible rows in
         section 9: map table rom:0x409368 (327 entries of 56 bytes), entry +0x10 region list (pairs of
         {condition, item}), +0x14 item list (the ext 84 spawn items), +0x2C layout per variation.
         An item is {factory, trigger, s16 x0 y0, s16 x1 y1, data}: a warp (factory @0x0800C233 or
         @0x0800D9C3) carries {dir, zone, area, var, s16 x, s16 y}, a scene item (@0x0800D7E1) a table
         pointer, a script region (@0x0800C2C3) a script. All CONFIRMED (bible SAV, CSV, SPC).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from scene import scene_lib as S                                         # noqa: E402

# ===== CONFIG =====
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
MAP_TABLE, MAP_COUNT, MAP_SIZE = 0x409368, 327, 56
WARP_FACTORIES = (0x0800C233, 0x0800D9C3)
SCENE_FACTORY, SCRIPT_FACTORY, GROUP_FACTORY = 0x0800D7E1, 0x0800C2C3, 0x0800E77F
TALK_FACTORIES = (0x0800B710, 0x0800B711)       # interactive object; the Thumb bit may be set
ITEM_SIZE, REGION_SIZE = 0x18, 8
SCRIPT_REGION = (0x3B0000, 0x420000)


def u32(rom: bytes, at: int) -> int:
    return struct.unpack_from("<I", rom, at)[0]


def _is_code(word: int) -> bool:
    """An item's first word is its factory, a Thumb entry point in the first 64 KB of code."""
    return 0x08000000 <= word < 0x08020000


# ===== tables and records =====

def show_table(rom: bytes, at: int, count: int = None) -> list:
    """The whole table: one block a record, with the ops named and the text shown."""
    count = count or S.table_end(rom, at)
    out = [f"table rom:0x{at:X}  {count} words"]
    stray = S.stray_before(rom, at)
    if stray is not None:
        out.append(f"  note: the word before word 0 is 0x{stray:X}, a known stray. "
                   f"This listing walks forward from the address you gave, so no index shifts (CH6).")
    for i, word in S.walk(rom, at, count).items():
        if S.is_end_entry(word):
            out.append(f"  [{i:2d}] END, resume index {word}")
            continue
        out += ["  " + line for line in show_record(rom, word - S.ROM_BASE, index=i)]
    return out


def show_record(rom: bytes, at: int, length: int = None, index: int = None) -> list:
    """One record: its header, then the named ops or the line."""
    rec = S.decode_record(rom, at, length)
    tag = f"[{index:2d}] " if index is not None else ""
    head = f"{tag}rom:0x{at:X}  type {rec.kind}  next {rec.nxt}"
    if rec.portrait is not None:
        head += f"  portrait {rec.portrait}"
    out = [head]
    if rec.kind == S.TYPE_CODE:
        out += ["    " + line for line in S.listing(rom, at + 3, rec.end - 1)]
    elif rec.kind == S.TYPE_TEXT:
        out.append(f'    "{rec.line}"')
    elif rec.target:
        what = "table" if rec.kind == S.TYPE_JUMP else "payload"
        out.append(f"    {what} rom:0x{rec.target - S.ROM_BASE:X}"
                   + ("  (a type 2 stream: pass --len to show its length)" if rec.kind == S.TYPE_STREAM else ""))
    return out


# ===== maps =====

def map_entry(rom: bytes, zone: int, area: int) -> tuple:
    for k in range(MAP_COUNT):
        at = MAP_TABLE + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the map table")


def item(rom: bytes, at: int) -> dict:
    """One region, warp or scene item: {factory, trigger, s16 rect, data}."""
    factory, trigger = u32(rom, at), u32(rom, at + 4)
    x0, y0, x1, y1 = struct.unpack_from("<4h", rom, at + 8)
    out = {"at": at, "factory": factory, "trigger": trigger, "rect": (x0, y0, x1, y1), "kind": "item"}
    if factory in WARP_FACTORIES:
        direction, zone, area, var = rom[at + 0x10:at + 0x14]
        x, y = struct.unpack_from("<2h", rom, at + 0x14)
        out.update(kind="warp", to=(zone, area, var), landing=(x, y), direction=direction)
    elif factory == SCENE_FACTORY:
        out.update(kind="scene", table=u32(rom, at + 0x10) - S.ROM_BASE)
    elif factory == SCRIPT_FACTORY:
        out.update(kind="script", script=u32(rom, at + 0x10) - S.ROM_BASE)
    elif factory in TALK_FACTORIES:
        # An interactive object: +0x08 s16 position, +0x0C its scene table, +0x10 its sprite set. CONFIRMED
        # on the map 9,1 Dende object rom:0x403F60 (table 0x3DD044, set 36 at 760,416; bible CSP).
        x, y = struct.unpack_from("<2h", rom, at + 8)
        out.update(kind="talk", at_xy=(x, y), table=u32(rom, at + 0x0C) - S.ROM_BASE, set_id=u32(rom, at + 0x10))
    elif factory == GROUP_FACTORY:
        # +0x14 points at a sub-struct {@0x080106B3, scene table}. The Cell Games scenes are owned this way,
        # so a tool that reads only the region list misses them (bible SS3). CONFIRMED on map 14,3.
        sub = u32(rom, at + 0x14)
        out.update(kind="group")
        if sub >> 24 == 0x08 and u32(rom, sub - S.ROM_BASE) == 0x080106B3:
            out["table"] = u32(rom, sub - S.ROM_BASE + 4) - S.ROM_BASE
    return out


def map_items(rom: bytes, zone: int, area: int) -> dict:
    """{'regions': [(condition, item)], 'items': [item]} for one map."""
    _, at = map_entry(rom, zone, area)
    regions, items = [], []
    region_list, item_list, count = u32(rom, at + 0x10), u32(rom, at + 0x14), rom[at + 4]
    if region_list:
        base = region_list - S.ROM_BASE
        for i in range(64):
            cond, pointer = u32(rom, base + REGION_SIZE * i), u32(rom, base + REGION_SIZE * i + 4)
            # The list carries no count, so it ends at the first pair that is not {condition, item}. An item
            # always opens with a code factory, so a word outside the code area ends the walk. Without this
            # the walk runs past the end of map 9,1 and invents a region.
            if not pointer or pointer >> 24 != 0x08 or not _is_code(u32(rom, pointer - S.ROM_BASE)):
                break
            regions.append((cond, item(rom, pointer - S.ROM_BASE)))
    if item_list:
        base = item_list - S.ROM_BASE                 # a list of pointers to items, not inline items
        for i in range(count):
            pointer = u32(rom, base + 4 * i)
            if pointer >> 24 == 0x08:
                items.append(item(rom, pointer - S.ROM_BASE))
    return {"entry": at, "regions": regions, "items": items, "count": count}


def show_map(rom: bytes, zone: int, area: int) -> list:
    """Which tables run on this map, plus its warps."""
    info = map_items(rom, zone, area)
    out = [f"map {zone},{area}  entry rom:0x{info['entry']:X}  {len(info['regions'])} region(s), "
           f"{len(info['items'])} item(s)"]
    for cond, it in info["regions"]:
        out.append(f"  region cond 0x{cond:08X}  rect {it['rect']}  rom:0x{it['at']:X}  {it['kind']}")
        if it["kind"] == "warp":
            out.append(f"    warp to map {it['to'][0]},{it['to'][1]} var {it['to'][2]} "
                       f"at {it['landing']} facing {it['direction']}")
        elif it["kind"] == "scene":
            out.append(f"    scene table rom:0x{it['table']:X}")
        elif it["kind"] == "script":
            out.append(f"    script rom:0x{it['script']:X}")
        elif it["kind"] == "talk":
            out.append(f"    talk set {it['set_id']} at {it['at_xy']} table rom:0x{it['table']:X}")
    for n, it in enumerate(info["items"]):
        extra = ""
        if it["kind"] == "warp":
            extra = f" -> map {it['to'][0]},{it['to'][1]} var {it['to'][2]} at {it['landing']}"
        elif it["kind"] == "scene":
            extra = f" -> table rom:0x{it['table']:X}"
        if it['kind'] == 'talk':
            extra = f"  set {it['set_id']} at {it['at_xy']} -> table rom:0x{it['table']:X}"
        if it['kind'] == 'group':
            extra = f"  -> table rom:0x{it['table']:X}" if 'table' in it else '  (no scene sub-struct)'
        # The rect is only proven for a region, warp, scene or script item, so other kinds do not show one.
        shape = f"  rect {it['rect']}" if it['kind'] in ('warp', 'scene', 'script') else ''
        out.append(f"  item {n:2d}  rom:0x{it['at']:X}  factory @0x{it['factory']:08X}  "
                   f"{it['kind']}{shape}{extra}")
    if not info["regions"] and not info["items"]:
        out.append("  no region list and no item list. A scene owned through the +0x14 group factory "
                   "@0x0800E77F sub-struct would not appear here (bible SS3).")
    return out


# ===== find text =====

def find_text(rom: bytes, needle: str, lo: int = SCRIPT_REGION[0], hi: int = SCRIPT_REGION[1]) -> list:
    """Every record whose ASCII holds needle, with the words that name it."""
    want, out, at = needle.encode("ascii"), [], lo
    while True:
        at = rom.find(want, at, hi)
        if at < 0:
            return out
        rec = _header_before(rom, at)
        namers = S.words_naming(rom, rec, lo, hi) if rec is not None else []
        out.append({"text_at": at, "record": rec,
                    "kind": rom[rec + 2] if rec is not None else None, "namers": namers})
        at += 1


def _header_before(rom: bytes, at: int, window: int = 400) -> int:
    """The type 1 record header that owns the text at at, or None.

    It scans back for the nearest {next, 0, 1, portrait} whose text reaches the hit with printable bytes
    only. A plain backward scan for a NUL is wrong: a line can open with a control byte such as '#' or '@',
    so the NUL before it belongs to the previous record."""
    for rec in range(at - 4, max(at - window, 0) - 1, -1):
        if rom[rec + 1] != 0 or rom[rec + 2] != S.TYPE_TEXT:
            continue
        body = rom[rec + 4:at]
        if all(b == 0x0B or 0x20 <= b < 0x7F or b in (0x23, 0x40, 0x5E) for b in body):
            return rec
    return None


def show_find(rom: bytes, needle: str) -> list:
    hits = find_text(rom, needle)
    out = [f'"{needle}": {len(hits)} hit(s) in rom:0x{SCRIPT_REGION[0]:X}-0x{SCRIPT_REGION[1]:X}']
    for h in hits:
        if h["record"] is None:
            out.append(f"  rom:0x{h['text_at']:X}  text, but the 4 bytes before it are not a type 1 header "
                       f"(type byte {h['kind']}). It may sit inside a type 2 stream or another payload.")
            continue
        out += ["  " + line for line in show_record(rom, h["record"])]
        if h["namers"]:
            out.append("    named by " + ", ".join(f"rom:0x{w:X}" for w in h["namers"]))
        else:
            out.append("    no aligned word names this record in the script region. A table word outside "
                       "the region, or a run-time index, would not show.")
    return out


# ===== CLI =====

def _main(argv: list) -> None:
    rom_path, action, arg, count, length = BASE, None, None, None, None
    while argv:
        a = argv.pop(0)
        if a == "--rom":
            rom_path = Path(argv.pop(0))
        elif a == "--count":
            count = int(argv.pop(0), 0)
        elif a == "--len":
            length = int(argv.pop(0), 0)
        elif a in ("--table", "--record", "--map", "--find-text"):
            action, arg = a, argv.pop(0)
        else:
            raise SystemExit(f"unknown argument {a}\n{__doc__}")
    if not action:
        raise SystemExit(__doc__)
    rom = rom_path.read_bytes()
    if action == "--table":
        lines = show_table(rom, int(arg, 0), count)
    elif action == "--record":
        lines = show_record(rom, int(arg, 0), length)
    elif action == "--map":
        zone, area = (int(v) for v in arg.split(","))
        lines = show_map(rom, zone, area)
    else:
        lines = show_find(rom, arg)
    print("\n".join(lines))


if __name__ == "__main__":
    _main(sys.argv[1:])
