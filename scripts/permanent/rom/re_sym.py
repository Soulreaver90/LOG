r"""
re_sym.py - Names for patches: sym("idle_tick") instead of a raw address.

Usage:   from rom.re_sym import sym, sym_rom, sym_ptr      (scripts\permanent on sys.path, as for every patch)
API:     sym(name) -> GBA address (0x08007570); sym_rom(name) -> file offset (0x7570);
         sym_ptr(name) -> the value code stores for a function (0x08007571 for Thumb, start for ARM);
         SYMBOLS -> the loaded scripts\permanent\disasm\symbols.py module (list, bible tags, name_of).
Rules:   Loads scripts\permanent\disasm\symbols.py by file path. re\ cannot be a package: "re" is the standard
         regex module. An unknown name raises KeyError with the closest known names.
"""
import difflib
import importlib.util

import log_paths

_SPEC = importlib.util.spec_from_file_location("re_symbols", log_paths.DISASM / "symbols.py")
SYMBOLS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(SYMBOLS)


def _known(name: str) -> str:
    if name not in SYMBOLS._BY_NAME:
        close = difflib.get_close_matches(name, SYMBOLS._BY_NAME, n=3)
        raise KeyError(f"no symbol {name!r} in re\\symbols.py; close: {', '.join(close) or 'none'}")
    return name


def sym(name: str) -> int:
    return SYMBOLS.addr(_known(name))


def sym_rom(name: str) -> int:
    return SYMBOLS.rom(_known(name))


def sym_ptr(name: str) -> int:
    return SYMBOLS.ptr(_known(name))
