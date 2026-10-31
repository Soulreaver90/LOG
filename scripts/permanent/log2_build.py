r"""
log2_build.py - Build the LoG II hack ROM from the base ROM plus named patches.

Usage:   py -3 -I scripts/permanent/log2_build.py [--out PATH] [--log PATH] [--save PATH]
                  [--list [FILE.txt] | <patch> ...]
         (no patches = base padded to 16 MB; --list = the patches in build_list.txt, --list FILE.txt = the
         patches in that list, for example build_list_trial.txt; run from the LOG root)
Lists:   one patch name a line, '#' starts a comment. 'include <file>' (path relative to the list's folder)
         expands that list in place, so a trial list is 'include build_list_dev.txt' plus its own lines and
         follows dev. A missing file, an include cycle or a name listed twice (after expansion) raises.
Masters: build_list.txt is the GOLDEN master and the default of --list. build_list_dev.txt is the DEV master.
         They differ in line 1 only (gohan_gi_vanilla against gohan_gi) and both include build_list_core.txt.
Output:  builds\log2_hack.gba, SHA-1 printed, one line appended to docs\build-log.md.
Saves:   a ROM with no .sav beside it opens as a new game, so every build pairs one. The seed is the save
         of the highest numbered main build (builds\log2_poc_r<N>.sav), or --save PATH. Suffixed builds
         (_spar, _computer) are skipped: they hold scenario saves. An existing .sav is never replaced.
API:     assemble(base, patch_names, notes=None) -> (rom, alloc)    build(base, out, patch_names) -> sha1
         apply_patches(rom, alloc, patch_names)    read_build_list(path=BUILD_LIST) -> [patch name]
Patches: module patches.<name> with apply(rom: bytearray, alloc: Allocator) -> None.
         One Allocator serves the whole build; patches share data via alloc.notes.
Rules:   never writes under data\. Output is 16 MB: base, 0xFF fill, then patches.
         New data goes in the expansion area rom:0x800000-0xFFFFFF (approved 2026-10-16). The allocator
         gets rom:0x800000-0xEFFFFF; ART_REGION rom:0xF00000-0xFFFFFF holds the fixed portrait slots of
         patches.art_inject, so no allocation can reach them.
"""
import hashlib
import importlib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I omits the script folder

import log_paths  # noqa: E402
from rom.rom_space import Allocator  # noqa: E402

# ===== CONFIG =====
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data" / "roms" / "Dragon Ball Z - The Legacy of Goku II (USA).gba"
OUT = log_paths.BUILDS / "log2_hack.gba"
BUILD_LOG = ROOT / "docs" / "build-log.md"
BUILD_LIST = ROOT / "scripts" / "permanent" / "build_list.txt"       # the golden master, and the --list default
DEV_LIST = BUILD_LIST.parent / "build_list_dev.txt"                  # the dev master, which every trial includes
BASE_SIZE = 8388608
BASE_SHA1 = "18e0715dec419f3501c301511530d2edcd590f8b"
ROM_SIZE = 16777216
ART_REGION = (0xF00000, 0x100000)                  # (offset, length): art_inject portrait slots
EXPANSION = [(BASE_SIZE, ART_REGION[0] - BASE_SIZE)]


# ===== build =====

def read_build_list(path: Path = BUILD_LIST) -> list:
    """Patch names, one per line; '#' starts a comment. 'include <file>' (relative to the list's folder) puts that
    list's names in place. A missing file, an include cycle or a name listed twice raises."""
    names = _expand_list(Path(path), ())
    twice = sorted({name for name in names if names.count(name) > 1})
    if twice:
        raise ValueError(f"{Path(path).name}: listed twice (after includes): {', '.join(twice)}")
    return names


def _expand_list(path: Path, chain: tuple) -> list:
    path = path.resolve()
    if path in chain:
        raise ValueError(f"build list include cycle: {' -> '.join(p.name for p in chain + (path,))}")
    if not path.is_file():
        raise FileNotFoundError(f"build list not found: {path}"
                                + (f" (included from {chain[-1]})" if chain else ""))
    names = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        words = line.split(None, 1)
        if words and words[0] == "include":
            if len(words) < 2:
                raise ValueError(f"{path.name} line {number}: include names no file")
            names += _expand_list(path.parent / words[1], chain + (path,))
        elif line:
            names.append(line)
    return names


def apply_patches(rom: bytearray, alloc: Allocator, patch_names: list) -> None:
    for name in patch_names:
        importlib.import_module(f"patches.{name}").apply(rom, alloc)


def assemble(base: Path, patch_names: list, notes: dict = None) -> tuple:
    """(rom, alloc) in memory: the checked base, 0xFF fill to 16 MB, then each patch. notes seed alloc.notes."""
    rom = bytearray(Path(base).read_bytes())
    if hashlib.sha1(rom).hexdigest() != BASE_SHA1:
        raise ValueError(f"base ROM SHA-1 is not {BASE_SHA1}: {base}")
    rom += bytes([0xFF]) * (ROM_SIZE - len(rom))
    alloc = Allocator(len(rom), EXPANSION)
    alloc.notes.update(notes or {})
    apply_patches(rom, alloc, patch_names)
    if len(rom) != ROM_SIZE:
        raise ValueError(f"ROM size is {len(rom)}, expected {ROM_SIZE}")
    return rom, alloc


def seed_save() -> Path:
    """The save of the highest numbered main build, which is the one that holds real progress.

    Suffixed builds (_spar, _computer) hold their own scenario saves, so the name must match exactly."""
    saves = [(int(m.group(1)), p) for p in (ROOT / "builds").glob("log2_poc_r*.sav")
             if (m := re.fullmatch(r"log2_poc_r(\d+)", p.stem))]
    return max(saves)[1] if saves else None


def pair_save(out: Path, src: Path = None) -> None:
    """Put a .sav beside the ROM, or the emulator opens it as a new game. Never replaces an existing save."""
    dst = out.with_suffix(".sav")
    if dst.exists():
        print(f"save kept: {dst.name}")
        return
    src = src or seed_save()
    if src is None or not Path(src).exists():
        print("no seed save found: this ROM will start a new game")
        return
    shutil.copyfile(src, dst)
    print(f"save seeded from {Path(src).name}")


def build(base: Path, out: Path, patch_names: list, save: Path = None) -> str:
    out = Path(out).resolve()
    if (ROOT / "data").resolve() in out.parents:
        raise ValueError(f"refusing to write under the data folder: {out}")
    rom, _ = assemble(base, patch_names)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(rom)
    sha = hashlib.sha1(rom).hexdigest()
    print(f"{out.name} sha1={sha}")
    pair_save(out, save)
    BUILD_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BUILD_LOG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} build {out.name} patches="
                f"{','.join(patch_names) or 'none'} sha1={sha}\n")
    return sha


def _main(argv: list) -> None:
    global BUILD_LOG
    out, names, save = OUT, [], None
    while argv:
        arg = argv.pop(0)
        if arg == "--out":
            out = Path(argv.pop(0))
        elif arg == "--log":
            BUILD_LOG = Path(argv.pop(0))
        elif arg == "--save":
            save = Path(argv.pop(0))
        elif arg == "--list":
            names += read_build_list(Path(argv.pop(0)) if argv and argv[0].endswith(".txt") else BUILD_LIST)
        else:
            names.append(arg)
    build(BASE, out, names, save=save)


if __name__ == "__main__":
    _main(sys.argv[1:])
