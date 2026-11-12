r"""
poke_rom.py - Make a test ROM by editing a few bytes of a built one, with no rebuild.

Usage:   py -3.14 -P scripts\permanent\rom\poke_rom.py <src.gba> <out.gba> <addr>=<value>[:<width>] ...
         addr is a ROM address (0x08...) or a file offset. width is 1, 2 or 4 bytes, default 4.
Example: poke_rom.py builds\...\arena_v4.gba builds\...\probe_a.gba 0x0893BD68=0
Output:  the new ROM, a .sav copied beside it, and one line per edit with the before and after bytes.
Rules:   it NEVER overwrites an existing ROM or save, and it refuses to write under data\. It reads the
         source, so the source is never touched.

Why this exists: a full build plus its test suite is about 40 minutes. A one word question, such as "which
layout field spawns this object", is answered by zeroing that word and loading the ROM. Seconds, not an hour.
Use it to find the answer, then make the real change in the patch module and rebuild once.
"""
import shutil
import struct
import sys
from pathlib import Path

ROM_BASE, WIDTHS = 0x08000000, {1: "<B", 2: "<H", 4: "<I"}


def parse(arg: str) -> tuple:
    """'0x0893BD68=0:4' -> (file offset, value, width). An 0x08 address is converted; anything else is raw."""
    where, _, rest = arg.partition("=")
    if not rest:
        sys.exit(f"edit needs addr=value, got {arg!r}")
    value, _, w = rest.partition(":")
    width = int(w) if w else 4
    if width not in WIDTHS:
        sys.exit(f"width must be 1, 2 or 4, got {width}")
    addr = int(where, 0)
    return (addr - ROM_BASE if addr >= ROM_BASE else addr), int(value, 0), width


def poke(src: Path, out: Path, edits: list, save: Path = None) -> None:
    if out.exists():
        sys.exit(f"refusing to overwrite {out}. Pick a new name.")
    if "data" in [p.lower() for p in out.parts]:
        sys.exit(f"refusing to write under a data folder: {out}")
    rom = bytearray(src.read_bytes())
    for off, value, width in edits:
        if off + width > len(rom):
            sys.exit(f"offset {off:#x} is past the end of {src.name}")
        before = bytes(rom[off:off + width])
        struct.pack_into(WIDTHS[width], rom, off, value)
        print(f"  rom:{off:#x} ({off + ROM_BASE:#010x})  {before.hex()} -> "
              f"{bytes(rom[off:off + width]).hex()}   {width} byte(s)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes(rom))
    print(f"wrote {out}")

    # A ROM with no save opens as a new game, which loses the owner's progress.
    dst = out.with_suffix(".sav")
    seed = save or src.with_suffix(".sav")
    if dst.exists():
        print(f"save already beside it, left alone: {dst.name}")
    elif seed.is_file():
        shutil.copyfile(seed, dst)
        print(f"save paired from {seed.name}, {dst.stat().st_size} bytes")
    else:
        print(f"WARNING: no save at {seed}. mGBA will open this as a NEW GAME.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    poke(Path(sys.argv[1]), Path(sys.argv[2]), [parse(a) for a in sys.argv[3:]])
