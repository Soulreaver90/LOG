r"""
bf_hud.py - Patch: the Buu's Fury player HUD look and boss bar look on LoG II, data only (r39, HUD v2b part 1).

Usage:   py -3 -P scripts\permanent\log2_build.py --list --out builds\log2_poc_r39.gba
Input:   the ROM after chamber_spar (the r38 list); the Buu's Fury USA ROM in data\roms (read only, SHA-1 checked).
API:     apply(rom, alloc) -> None; regions in alloc.notes["bf_hud"]. remap, load_bf, t_bf and u32 are shared
         with patches.bf_ki_pool (the yellow pool image).
Method:  All writes are in place. No code byte, no repoint. Steps 1-4 are mockup 1 (approved), step 5 is v2:
         1. OAM pool words rom:0x8E80 and rom:0x8E88 trade places: the icon (buffer 0x300) shows left, as in BF.
         2. HUD frame rom:0x6D7B54 (0x300) = BF frame 0x087137D8 bytes 0x100-0x2FF then 0x000-0x0FF, remapped;
            EXP steps 69-71 painted empty (index 1).
         3. Bar tables with the BF pixel paths moved to the LoG II buffer (t_bf): HP 48 steps on BF HP 41,
            EP 49 on the BF ki row 41, EXP 69 on BF EXP 0-68, cooldown offsets 20 and counts 0, 7, 13, 18, 20.
         4. The 27 icon images (ability table +0 and +4 words, and ssj2_form's Z2 pair): the remapped BF empty
            icon 0x087148D8 with the LoG II picture (rows 2-9, columns 13-28) pasted at rows 2-9, columns 3-18.
         5. Boss bar (same class in both games): image rom:0x6D64B4 (0x200) = BF 0x087196E4 remapped; table
            rom:0x6D60F4 (60 steps x 4 offsets) = BF steps 0x087198E4, step i -> BF step i x 53 / 60.
         Remap: BF_TO_LOG2, frozen. It is the nearest LoG II OBJ index (r38 rom:0x1DA6C8) by CIELAB distance
         (CIE76), skipping 0, the never-drawn 172, 174, 178, 218 and the reserved 239 (boss bar and pool image
         also 168, which the Cell fight palette RAM changes); test_bf_hud.py re-derives it. Frozen, so a later
         palette edit recolors the HUD like every other OBJ and never reshuffles its indices.
Rules:   Source: docs\tasks\2026-10-24-r39-build\r39.md, hud-ki-study-report.md section 5, hud-ki-proto-report.md; the mockup
         builders scripts\one-time\2026-10-24-hud-ki\build_mock1.py and proto\build_proto_b.py (r39 equals v2b, test_bf_hud.py).
         Every region is checked against its r38 bytes (SHA-1) before the first write; a second run raises.
"""
import hashlib
import struct
from pathlib import Path

# ===== constants =====
ROM_BASE = 0x08000000
BF_PATH = Path(__file__).resolve().parents[3] / "data" / "roms" / "Dragon Ball Z - Buu's Fury (USA).gba"
BF_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"
BF_TO_LOG2 = {0: 0, 1: 1, 3: 5, 5: 8, 6: 4, 26: 41, 27: 40, 28: 46, 29: 131, 30: 123, 32: 26, 33: 25, 34: 24,
              35: 30, 48: 58, 49: 57, 50: 56, 52: 151, 75: 68, 95: 216, 96: 3, 97: 197, 98: 76, 99: 202, 100: 177,
              108: 32, 109: 38, 110: 37, 114: 14, 115: 13, 116: 12, 117: 11, 118: 10, 119: 9}

OAM_WORDS = ((0x8E80, 0x80086000), (0x8E88, 0x80386000))
FRAME, BF_FRAME = 0x6D7B54, 0x087137D8
HP, EP, EXP, CD, CD_COUNTS = 0x3B5358, 0x3B5658, 0x3B5968, 0x3B5B90, 0x3B5BE0
BF_HP, BF_KI, BF_EXP, BF_CD = 0x08071CB0, 0x08071F40, 0x080721D0, 0x08072410
COUNTS = (0, 7, 13, 18, 20)
ABILITY_TABLE, ABILITIES = 0x1D9900, 14
BF_ICON, ICON_LEN = 0x087148D8, 0x200
BOSS_TABLE, BOSS_IMAGE, BOSS_LITERALS = 0x6D60F4, 0x6D64B4, ((0x1068C, 0x086D64B4), (0x1067C, 0x086D60F0))
BF_BOSS_IMAGE, BF_BOSS_TABLE, BOSS_STEPS, BF_BOSS_STEPS = 0x087196E4, 0x087198E4, 60, 53

# (offset, length, name): r38 SHA-1 of the bytes each step replaces or reads
PINS = {(FRAME, 0x300, "HUD frame"): "40deca0eaea4bfcab2abd947eebeb48dd5e59a18",
        (HP, 0x300, "HP table 48 x 16"): "96259752748f88223b67bf632f7ed83bf1e9b6a0",
        (EP, 0x310, "EP table 49 x 16"): "2aa4f0d044d4329195c84250aae4c820b3683f2d",
        (EXP, 0x228, "EXP table 69 x 8"): "223e83fac8738a76aeb10206cc844b409d7b9bd3",
        (CD, 0x50, "cooldown offsets 20 x 4"): "cfc9b4aada516d5b12e7eff4d64392a44525fd1a",
        (CD_COUNTS, 0x14, "cooldown counts 5 x 4"): "de631f8dccd07ac368ba7509baa1274ad2a597cc",
        (ABILITY_TABLE, 16 * ABILITIES, "ability table"): "61be615ceced76d9ab0da7baf1e7eabe83e9e568",
        (BOSS_TABLE, 16 * BOSS_STEPS, "boss bar table 60 x 16"): "81ed8bf9d1ba739659ec78a86644a9a1ada969d5",
        (BOSS_IMAGE, 0x200, "boss bar image"): "0e37ad08769696d001343809398f77ce8f6e5be7"}
ICONS_COUNT, ICONS_SHA1 = 27, "e3af453542bd718c7615d9bccdcc270e59d72cae"   # sorted by address, 0x200 each


# ===== shared helpers =====

def u32(rom: bytes, a: int) -> int:
    return struct.unpack_from("<I", rom, a - ROM_BASE if a >= ROM_BASE else a)[0]


def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def load_bf() -> bytes:
    bf = BF_PATH.read_bytes()
    if hashlib.sha1(bf).hexdigest() != BF_SHA1:
        raise ValueError(f"{BF_PATH.name}: SHA-1 is not {BF_SHA1}")
    return bf


def t_bf(o: int) -> int:
    """BF player-HUD buffer offset -> LoG II buffer offset (icon 0x000 <-> 0x300, frame 0x200 -> 0x000)."""
    return o + 0x300 if o < 0x200 else (o if o < 0x300 else o - 0x300)


def remap(data: bytes) -> bytes:
    missing = set(data) - set(BF_TO_LOG2)
    if missing:
        raise ValueError(f"BF indices without a LoG II index: {sorted(missing)}")
    return bytes(BF_TO_LOG2[v] for v in data)


def icons(rom: bytes, alloc) -> list:
    """GBA addresses of every icon image: ability table +0 and +4 words, then ssj2_form's Z2 pair; sorted."""
    found = {u32(rom, ABILITY_TABLE + 16 * n + k) for n in range(ABILITIES) for k in (0, 4)}
    z2 = alloc.notes["ssj2_form"]
    return sorted(found | {z2["z2"] + ROM_BASE, z2["z2_dim"] + ROM_BASE})


# ===== checks =====

def _sha(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def _check(rom: bytearray, alloc) -> list:
    for need in ("ssj2_form", "chamber_spar"):
        if need not in alloc.notes:
            raise ValueError(f"bf_hud needs the {need} notes: run the r38 list first")
    if "bf_hud" in alloc.notes:
        raise ValueError("bf_hud already ran")
    for off, want in OAM_WORDS + BOSS_LITERALS:
        if u32(rom, off) != want:
            raise ValueError(f"rom:0x{off:X} is 0x{u32(rom, off):08X}, expected 0x{want:08X}")
    for (off, n, name), want in PINS.items():
        if _sha(rom[off:off + n]) != want:
            raise ValueError(f"rom:0x{off:X} {name} differs from r38")
    found = icons(rom, alloc)
    blob = b"".join(rom[p - ROM_BASE:p - ROM_BASE + ICON_LEN] for p in found)
    if len(found) != ICONS_COUNT or _sha(blob) != ICONS_SHA1:
        raise ValueError("icon list or icon images differ from r38")
    return found


# ===== patch =====

def plan(rom: bytes, bf: bytes, found: list) -> dict:
    """{file offset: (bytes, name)} of every write; reads only."""
    writes = {}
    (o0, w0), (o2, w2) = OAM_WORDS
    writes[o0], writes[o2] = (_word(w2), "OAM pool word OBJ0"), (_word(w0), "OAM pool word OBJ2")
    # 2. frame
    bff = bf[BF_FRAME - ROM_BASE:BF_FRAME - ROM_BASE + 0x300]
    frame = bytearray(remap(bff[0x100:0x300] + bff[0x000:0x100]))
    for i in range(69, 72):
        for k in range(2):
            o = t_bf(u32(bf, BF_EXP + 8 * i + 4 * k))
            if o >= 0x300:
                raise ValueError("EXP tail is not in the frame")
            frame[o] = 1
    writes[FRAME] = (bytes(frame), "HUD frame")
    # 3. tables (16-byte HP and EP steps keep their 4th word)
    for base, steps, src, name in ((HP, 48, BF_HP, "HP step"), (EP, 49, BF_KI, "EP step")):
        for i in range(steps):
            j = i * 41 // steps
            writes[base + 16 * i] = (b"".join(_word(t_bf(u32(bf, src + 16 * j + 4 * k))) for k in range(3)),
                                     f"{name} {i}")
    writes[EXP] = (b"".join(_word(t_bf(u32(bf, BF_EXP + 8 * i + 4 * k))) for i in range(69) for k in range(2)),
                   "EXP table 69 x 8")
    writes[CD] = (b"".join(_word(t_bf(u32(bf, BF_CD + 4 * i))) for i in range(20)), "cooldown offsets 20 x 4")
    writes[CD_COUNTS] = (b"".join(_word(n) for n in COUNTS), "cooldown counts 5 x 4")
    # 4. icons
    tmpl = remap(bf[BF_ICON - ROM_BASE:BF_ICON - ROM_BASE + ICON_LEN])

    def px(o, x, y):
        return o + (y // 8) * 256 + (x // 8) * 64 + (y % 8) * 8 + (x % 8)

    for p in found:
        o, new = p - ROM_BASE, bytearray(tmpl)
        for y in range(2, 10):
            for x in range(13, 29):
                new[px(0, x - 10, y)] = rom[px(o, x, y)]
        writes[o] = (bytes(new), f"icon 0x{p:08X}")
    # 5. boss bar
    img = BF_BOSS_IMAGE - ROM_BASE
    writes[BOSS_IMAGE] = (remap(bf[img:img + 0x200]), "boss bar image")
    table = bytearray()
    for i in range(BOSS_STEPS):
        j = i * BF_BOSS_STEPS // BOSS_STEPS
        for k in range(4):
            o = u32(bf, BF_BOSS_TABLE + 16 * j + 4 * k)
            if o >= 0x200:
                raise ValueError("boss bar offset out of the buffer")
            table += _word(o)
    writes[BOSS_TABLE] = (bytes(table), "boss bar table 60 x 16")
    return writes


def apply(rom: bytearray, alloc) -> None:
    found = _check(rom, alloc)
    writes = plan(bytes(rom), load_bf(), found)
    for off, (data, _) in writes.items():
        rom[off:off + len(data)] = data
    alloc.notes["bf_hud"] = {"regions": sorted((off, len(d), name) for off, (d, name) in writes.items()),
                             "icons": [p - ROM_BASE for p in found]}
