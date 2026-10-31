"""
_probe.py - Test-only patch: allocates 8 bytes and writes b"PROBE". Used by test_build.py.
"""


def apply(rom, alloc):
    off = alloc.alloc(8)
    rom[off:off + 5] = b"PROBE"
    alloc.notes["_probe"] = off
