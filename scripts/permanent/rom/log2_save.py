"""
log2_save.py - Read, check and write Dragon Ball Z: The Legacy of Goku II (USA, ALFE) EEPROM saves (mGBA .sav).

Usage:   py -3 -I log2_save.py info    <file.sav> [--flags]
         py -3 -I log2_save.py journal <file.sav> <rom.gba>
         py -3 -I log2_save.py build   <base.sav> <out.sav> [--set cellgames|cellgames2|cellgames2_arena|postcell]
         py -3 -I log2_save.py set     <in.sav> <out.sav> <slot 1-3> key=value [key=value ...]
Keys:    leader=0-5  map=zone,area,var  pos=x,y  flag+=N  flag-=N  item=id,count  visited=all|none
Prints:  info: options block, then each slot: checksum, header, map, position, party, flags, items.
         journal: each slot's quests as the Journal shows them (quest table run on the slot's flags and items).
Writes:  build: a level 40 test save (3 slots, see PRESET_SETS). Default set "cellgames"; "postcell" rebuilds
         the first test save byte for byte; "cellgames2" is the flag 191 slot 3 with the arena maps unvisited
         (log2_lv40_cellgames_v2.sav). set: one slot edited, checksum redone.
         Bytes the game never writes (0x008-0x00F, 0x448 onward) are copied from the input file.
         Refuses to write under a data folder or over an existing file.
Layout:  docs\research\re-save-format.md. Addresses below are GBA addresses in the USA ROM (SHA-1 18e0715d...).
Labels:  CONFIRMED = read from the game code. LIKELY = strong evidence, my test pending.
"""
import struct
import sys
import zlib
from pathlib import Path

# ===== EEPROM layout (CONFIRMED: 0x08001E3C-0x08001EF4 options, 0x08003F90-0x0800409C slots) =====
SAV_SIZE = 0x2000            # IdentifyEeprom(64) at 0x0802145A: 64 Kbit part, whole image read at boot
OPT_OFF = 0x000              # 4 option bytes + u32 check
OPT_MAGIC = 0x12345678       # added to the options Adler-32 (0x08001E44)
SLOT_OFF = 0x010             # slot n at 0x10 + n * 0x168 (0x08003FB8)
SLOT_SIZE = 0x168            # 0x164 data bytes + u32 Adler-32 (no constant added, 0x08003FCA)
SLOT_DATA = 0x164
SLOT_COUNT = 3               # file select loops 0..2 (0x080019EE)
OPT_DEFAULT = bytes([4, 6, 4, 0])  # game defaults when the options check fails (0x08001E98)

# ===== Slot struct offsets (RAM copy at IWRAM 0x03000E90) =====
O_LEADER, O_FLAGS, O_ZONE, O_AREA, O_VAR = 0x00, 0x01, 0x02, 0x03, 0x04
O_CHARS, CHAR_SIZE = 0x0C, 28            # six 28-byte records (default table ROM 0x081D9548)
O_STORY, STORY_BITS = 0xB4, 400          # story flags, get/set 0x08003E42/0x08003E5E
O_VISITED, VISITED_BITS = 0xE7, 297      # map visited bits, table 0x086F6D8C (0x080040EE)
O_SCOUTER, SCOUTER_BITS = 0x11A, 128     # Scouter database entries, table 0x086F8E40
O_ITEMS, ITEM_COUNT = 0x12B, 50          # item counts, item table 0x086ADE24
O_POS = 0x160                            # s16 x, s16 y (read by ldsh at 0x0800C58A)

CHAR_NAMES = ["Gohan", "Piccolo", "Vegeta", "Trunks", "Goku", "Hercule"]
# Level n needs EXP >= LEVEL_EXP[n - 1]; level 50 is the cap (ROM 0x081D9834, code 0x08004214).
LEVEL_EXP = [0, 50, 150, 325, 600, 1000, 1550, 2275, 3200, 4350, 5775, 7550, 10225, 13500, 17525,
             22450, 28475, 35750, 44425, 54750, 66975, 81400, 98825, 119750, 144750, 175250, 212875,
             259000, 314625, 382750, 467625, 572525, 701900, 855775, 1045400, 1270775, 1531900,
             1853025, 2245900, 2727775, 3335510, 4090385, 5030260, 6195885, 7646510, 9442210,
             11663685, 14520185, 18138435, 22965105]
# Per-level STR, POW, END gain as (min, max) in 1/256 units (ROM 0x081D95F0, code 0x08003C6E).
GROWTH = [((318, 518), (302, 502), (256, 456)), ((224, 424), (245, 445), (208, 408)),
          ((234, 434), (219, 419), (245, 445)), ((287, 487), (172, 372), (182, 382)),
          ((255, 455), (255, 455), (198, 398)), ((64, 192), (64, 192), (64, 192))]
BASE_STATS = [(3, 5, 3), (4, 4, 5), (6, 4, 6), (6, 3, 4), (5, 7, 6), (8, 1, 6)]  # default table
BASE_HP = [85, 95, 105, 110, 100, 50]    # default table; base EP is 20 for all six
HP_STEP = (0xE14, 0xE14 + 0x51E)         # per level HP += HP * step >> 16 (0x08003D02)
EP_STEP = (2, 4)                         # per level EP += 2 + rand(3) (0x08003D1A)
# Appearance table (ROM 0x081D967C, 20-byte entries): entry -> sprite set id.
APPEARANCE_SET = [53, 55, 56, 57, 58, 59, 103, 104, 137, 138, 139, 140, 128, 129, 130, 132, 133,
                  134, 135, 60, 61, 72]

# ===== Story presets =====
# Level 40 records as the debug teleport (0x08005C0A) wrote them: it calls the game's own level-up
# routine 0x08003CA0 from level 1 to 40, then sets EXP to LEVEL_EXP[39]. Source: capture 02
# (IWRAM 0x03000E9C). Byte +8 (appearance) is then set to the story outfit.
LV40_RECORDS = [
    "8a038a038600860000038f46483a64475f9f29007f00000004030c02",
    "1c041c048a008a0006039b403e3830405f9f29007f00000009080b02",
    "770477048a008a0008030b47993fac3c5f9f29007f00000000070c02",
    "9d049d04870087000c030835f2279f285f9f29007f000000010d0c02",
    "020402048b008b001303542f1332fe415f9f29007f000000030a0c02",
    "d601d6018d008d00150397240810ac1e5f9f29004300000006060606",
]
# Hercule before he joins: the ROM default record (0x081D9548 + 5 * 28), +0x14 = 0x40 (not in party).
# He joins only after flag 195, by ext 79 (5) and ext 98 (5, 40) at 0x083EC6C9. CONFIRMED.
HERCULE_DEFAULT = "32003200140014001503000800010006000000004000000006060606"
# Outfits by story flag order: Vegeta set 137 and Trunks set 132 at flag 151 (0x083E7789), Gohan set 56
# at the chamber exit (0x083DB62B, flag 154). No later ext 73 for them before Cell. LIKELY.
POSTCELL_APPEARANCE = [2, 6, 8, 15, 19, 21]
# Story flags with a script SETFLAG site, up to 195 (set when Cell is beaten, 0x083EC6A2),
# minus flags a later script clears again. Flag 196 (final goodbye) stays clear. LIKELY.
POSTCELL_FLAGS = [(0, 9), (11, 20), (22, 23), (26, 26), (28, 31), (33, 70), (73, 100), (108, 113),
                  (117, 132), (134, 134), (136, 146), (148, 158), (162, 164), (171, 171),
                  (176, 176), (181, 181), (185, 195)]
# Before the Cell Games: the post-Cell set minus 192-195, whose only SET sites are Cell Games scripts
# (193 0x083E8D92, 192 0x083E93E0, 194 0x083E9BBB, 195 0x083EC6A2). 191 is set at 0x083DD32B. LIKELY.
CELLGAMES_FLAGS = POSTCELL_FLAGS[:-1] + [(185, 191)]
# Story items that keep the journal consistent: Dragon Radar (quest "Get the Dragon Radar" is done
# only while item 45 is held, given at 0x083CF62B) and Scouter (item 22, given at 0x083CF4A3 and 0x083D0C4B).
# The Dragon Balls 29-35 are gone at flag 191 (ext 76 = count - 1, record 0x083DD2F0). LIKELY.
POSTCELL_ITEMS = {45: 1, 22: 1}
# Flag 191 just set (save-slot3 study, docs\tasks\2026-10-18-save-slot3\save-slot3-report.md): a walk of every map-owned
# script finds no flag, party, outfit or item op that runs between flag 191 and flag 192 or only after it,
# except the Cell Games ops (flags 192-195, Rage and post-Cell ext 73, Hercule joins, Goku leaves). So the
# flags, records and items stay as in "cellgames". Only the arena maps 14,1-14,3 (visited bits 294-296,
# table 0x086F6D8C) are unvisited: the arena landing needs flag 191 (world map region 25). CONFIRMED (walk).
ARENA_VISITED = (294, 295, 296)
# ===== Sprite lab (patches\sprite_lab.py, me, 2026-10-30 11:15 PM) =====
# The lab slot is the post-Cell story, so flag 195 is set and Super Saiyan 2 is reachable, plus the lab
# gate flag. LAB_FLAG has no script op and no map condition word in the base ROM (two shapes, task s6),
# so only this preset sets it; a slot without it plays as any other save.
LAB_FLAG = 350
# Forms drain the Buu's Fury ki pool, which is filled to the character's max EP at the transform end and
# falls 1 every 10 frames in Super Saiyan 2 (bible R39). So the form lasts max EP x 10 frames: at 9999 EP
# that is about 28 minutes, far past any capture. Current EP is raised with it so ki moves work at once.
LAB_EP = 9999
# Record +9 is the attack slot, the ability B fires (bible section 7: "HP, max HP, EP, max EP, appearance,
# attack slot, STR/POW/END, EXP, flags"). The four ability ids are +0x18..+0x1B. The level 40 records leave
# Gohan on slot 3, the ki blast, so B never reaches the transform. The lab points every character at its
# own transform: ability 12 is the Saiyan transform, 11 is Piccolo's Super Namek (bible section 6).
O_REC_EP, O_REC_SLOT, O_REC_ABILITIES = 4, 9, 0x18
TRANSFORM_ABILITIES = (12, 11)
LAB_RECORDS = []
for _hexrec in LV40_RECORDS:
    _rec = bytearray.fromhex(_hexrec)
    struct.pack_into("<HH", _rec, O_REC_EP, LAB_EP, LAB_EP)     # +4 current EP, +6 max EP
    _abilities = list(_rec[O_REC_ABILITIES:O_REC_ABILITIES + 4])
    for _want in TRANSFORM_ABILITIES:
        if _want in _abilities:
            _rec[O_REC_SLOT] = _abilities.index(_want)
            break
    LAB_RECORDS.append(_rec.hex())
# Stories whose slots start with the HUD off: slot +1 bit 1 is the HUD bit that ext 86 toggles
# (@0x0800AB82 through @0x080040AA, which builds the HUD object on 1). CONFIRMED (bible section 6).
HUD_OFF_STORIES = {"spritelab"}
STORIES = {
    "postcell": (POSTCELL_FLAGS, LV40_RECORDS),
    "cellgames": (CELLGAMES_FLAGS, LV40_RECORDS[:5] + [HERCULE_DEFAULT]),
    "cellgames2": (CELLGAMES_FLAGS, LV40_RECORDS[:5] + [HERCULE_DEFAULT]),
    "spritelab": (POSTCELL_FLAGS + [(LAB_FLAG, LAB_FLAG)], LAB_RECORDS),
}
UNVISITED = {"cellgames2": ARENA_VISITED}   # story -> visited bits left clear
PRESET_SETS = {
    # (label, story, leader, zone, area, variation, x, y)
    "postcell": [   # first test save, test-data\saves\log2_lv40_postcell.sav as built (SHA-1 3ecf1e40...)
        ("Capsule Corporation save point (map 6,1)", "postcell", 0, 6, 1, 1, 432, 613),
        ("East District 439 save point (map 2,29)", "postcell", 0, 2, 29, 1, 248, 285),
        ("Capsule Corporation, post-Cell arrival (map 6,3)", "postcell", 0, 6, 3, 1, 376, 408),
    ],
    "cellgames": [
        # y 591: the slot 1 position in the .sav I loaded (log2_poc_r12.sav).
        ("Capsule Corporation save point (map 6,1)", "postcell", 0, 6, 1, 1, 432, 591),
        # World map landing script 0x083FBC84: push 11,1,1,416,160 ; ext 38. CONFIRMED.
        ("Master Roshi's Island, world-map arrival (map 11,1)", "postcell", 0, 11, 1, 1, 416, 160),
        # World map landing script 0x083FBBFC: push 9,1,1,768,832 ; ext 38. Goku leads: the Cell Games
        # barrier on map 14,1 opens only for leader 4 at level 40 or more (0x08408DD4). CONFIRMED.
        ("Dende's Lookout, world-map arrival (map 9,1), before the Cell Games", "cellgames", 4, 9, 1, 1, 768, 832),
    ],
}
# Slots 1 and 2 byte for byte as in "cellgames" (SHA-1 c755acf0...); slot 3 is the flag 191 state.
PRESET_SETS["cellgames2"] = PRESET_SETS["cellgames"][:2] + [
    ("Dende's Lookout, world-map arrival (map 9,1), flag 191 just set", "cellgames2", 4, 9, 1, 1, 768, 832)]
# Option, not built by default: slot 3 at the Cell Games Arena door. World map landing (region 25, flag 191):
# map 14,1,1 at 264,304. Goku leads, so the barrier scene (cond 0x08408DB0: leader not 4) does not start.
PRESET_SETS["cellgames2_arena"] = PRESET_SETS["cellgames"][:2] + [
    ("Cell Games Arena, world-map arrival (map 14,1), flag 191 just set", "cellgames2", 4, 14, 1, 1, 264, 304)]
# The sprite lab save. Slot 1 is the lab; slot 2 is the same Gohan on real scenery, for the comparison the
# I asked for, and leaves LAB_FLAG clear so that slot draws normally.
# Map 8,36: all five list words and all five list count bytes are 0 and the variation, enter and leave
# script words are 0, so the map builds no enemy, no NPC and no region (entry rom:0x40C778, task s7).
# (236,180) is the centre of its largest clear square, 88 px across (collision frame, task s4).
# Map 10,1 is "Outside Gingertown". Its world-map landing script rom:0x3FBB2C is
# `push 10,1,1,432,488 ; ext 38`, the spawn point. The white road runs down world x 304-374 on that row:
# blue-grey asphalt with a dashed centre line at 304-334, then the pale white strip at 336-374. (352,488)
# is the middle of the pale strip, 80 px left of the spawn point, on open collision with room all round.
# Measured off the captured frame with the live camera (task s9), not off a renderer.
PRESET_SETS["spritelab"] = [
    ("Sprite lab: flat field, HUD off, fixed camera (map 8,36)", "spritelab", 0, 8, 36, 1, 236, 180),
    ("Ginger Town white road, real scenery (map 10,1)", "postcell", 0, 10, 1, 1, 352, 488),
    ("Sprite lab, second slot (map 8,36)", "spritelab", 0, 8, 36, 1, 236, 180),
]
DEFAULT_SET = "cellgames"

# ===== Journal (quest table, CONFIRMED: loop 0x08004A86-0x08004AE4) =====
QUEST_TABLE, QUEST_COUNT, QUEST_SIZE = 0x086D68DC, 43, 16  # {u32 category, done script, active script, text}
ROM_BASE = 0x08000000
EXT_FLAG, EXT_NOTFLAG, EXT_COUNT = 19, 20, 21   # ext 21 also adds an on-map pickup count: not in a save
CMP_OPS = {11: lambda a, b: a == b, 12: lambda a, b: a != b, 13: lambda a, b: a > b,
           14: lambda a, b: a >= b, 15: lambda a, b: a < b, 16: lambda a, b: a <= b,
           4: lambda a, b: bool(a and b), 5: lambda a, b: bool(a or b),       # logical (0x08008FC6)
           7: lambda a, b: a + b, 8: lambda a, b: a - b}

# ===== Codec =====
def swap_blocks(data: bytes) -> bytes:
    """EEPROM file order <-> RAM order: the game stores each 8-byte block reversed (0x08021B3C)."""
    return b"".join(data[i:i + 8][::-1] for i in range(0, len(data), 8))

def adler32(data: bytes) -> int:
    """The game's checksum at 0x0802153E: Adler-32, mod 65521 every 5552 bytes."""
    a, b = 1, 0
    for i in range(0, len(data), 5552):
        for byte in data[i:i + 5552]:
            a += byte
            b += a
        a %= 65521
        b %= 65521
    return (b << 16) | a

def read_ram(sav: bytes) -> bytearray:
    if len(sav) != SAV_SIZE:
        sys.exit(f"Expected {SAV_SIZE} bytes, got {len(sav)}.")
    return bytearray(swap_blocks(sav))

def slot_range(n: int) -> slice:
    start = SLOT_OFF + n * SLOT_SIZE
    return slice(start, start + SLOT_SIZE)

def seal_slot(ram: bytearray, n: int) -> None:
    s = slot_range(n).start
    struct.pack_into("<I", ram, s + SLOT_DATA, adler32(bytes(ram[s:s + SLOT_DATA])))

def seal_options(ram: bytearray, opts: bytes) -> None:
    ram[OPT_OFF:OPT_OFF + 4] = opts
    struct.pack_into("<I", ram, OPT_OFF + 4, (adler32(opts) + OPT_MAGIC) & 0xFFFFFFFF)

# ===== Field helpers =====
def bit(buf, base, n):
    return buf[base + (n >> 3)] >> (n & 7) & 1

def set_bit(buf, base, n, on=True):
    if on:
        buf[base + (n >> 3)] |= 1 << (n & 7)
    else:
        buf[base + (n >> 3)] &= ~(1 << (n & 7)) & 0xFF

def level_of(exp: int) -> int:
    lvl = 1
    for i, need in enumerate(LEVEL_EXP):
        if exp >= need:
            lvl = i + 1
    return lvl

def ranges(nums):
    out, start, prev = [], None, None
    for x in nums:
        if start is None:
            start = prev = x
        elif x == prev + 1:
            prev = x
        else:
            out.append(f"{start}-{prev}" if prev > start else str(start))
            start = prev = x
    if start is not None:
        out.append(f"{start}-{prev}" if prev > start else str(start))
    return ",".join(out) or "-"

def check_stats(c: int, rec: bytes) -> str:
    """Check a record against the level-up rule from level 1 (stats 8.8, cap 100; HP compounded per level)."""
    exp = struct.unpack_from("<I", rec, 0x10)[0]
    gained = level_of(exp) - 1
    notes = []
    hp_lo = hp_hi = BASE_HP[c]
    for _ in range(gained):
        hp_lo += hp_lo * HP_STEP[0] >> 16
        hp_hi += hp_hi * HP_STEP[1] >> 16
    hp, ep = struct.unpack_from("<H", rec, 2)[0], struct.unpack_from("<H", rec, 6)[0]
    if not hp_lo <= hp <= hp_hi:
        notes.append(f"max HP out of {hp_lo}-{hp_hi}")
    if not 20 + EP_STEP[0] * gained <= ep <= 20 + EP_STEP[1] * gained:
        notes.append(f"max EP out of {20 + EP_STEP[0] * gained}-{20 + EP_STEP[1] * gained}")
    for k, off in enumerate((0x0A, 0x0C, 0x0E)):
        v = struct.unpack_from("<H", rec, off)[0]
        lo = min(BASE_STATS[c][k] * 256 + GROWTH[c][k][0] * gained, 0x6400)
        hi = min(BASE_STATS[c][k] * 256 + GROWTH[c][k][1] * gained, 0x6400)
        if not lo <= v <= hi:
            notes.append(f"{['STR', 'POW', 'END'][k]} out of {lo / 256:.1f}-{hi / 256:.1f}")
    return "HP, EP and stats in range" if not notes else "; ".join(notes)

# ===== Journal =====
def varint(rom: bytes, i: int):
    """Script VM number: 7-bit groups, high bit continues, bit 0 = sign (base op 1)."""
    v = 0
    while True:
        c = rom[i]
        i += 1
        v = (v << 7) + (c & 0x7F)
        if not c & 0x80:
            return (-(v >> 1) if v & 1 else v >> 1), i

def push_list(rom: bytes, addr: int) -> list:
    """Values of a base op 29 push list at GBA address addr."""
    i = addr - ROM_BASE
    if rom[i] != 29:
        raise ValueError(f"no push list at {addr:#x}")
    vals, i = [], i + 2
    for _ in range(rom[i - 1]):
        v, i = varint(rom, i)
        vals.append(v)
    return vals

def run_cond(rom: bytes, addr: int, slot: bytes) -> int:
    """Run a quest condition script (interpreter 0x080092E4 subset) on a slot's flags and items."""
    i, stack = addr - ROM_BASE, []
    for _ in range(500):
        op = rom[i]
        i += 1
        if op == 0:
            stack.append(rom[i])
            i += 1
        elif op == 1:
            v, i = varint(rom, i)
            stack.append(v)
        elif op == 29:
            stack.extend(push_list(rom, i - 1 + ROM_BASE))
            i = push_list_end(rom, i - 1)
        elif op == 2 and rom[i] in (EXT_FLAG, EXT_NOTFLAG, EXT_COUNT):
            ext, n = rom[i], stack.pop()
            i += 1
            if ext == EXT_COUNT:
                stack.append(slot[O_ITEMS + n])
            else:
                stack.append(bit(slot, O_STORY, n) ^ (ext == EXT_NOTFLAG))
        elif op in CMP_OPS:
            b, a = stack.pop(), stack.pop()
            stack.append(int(CMP_OPS[op](a, b)))
        elif op == 18:
            i += 1 + rom[i]
        elif op == 19:
            i += 1 + (rom[i] if stack.pop() == 0 else 0)
        elif op == 17:
            return stack[-1] if stack else 0
        else:
            raise ValueError(f"op {op} at {i - 1 + ROM_BASE:#x} is not supported by the journal evaluator")
    raise ValueError(f"script at {addr:#x} did not end")

def push_list_end(rom: bytes, i: int) -> int:
    count, i = rom[i + 1], i + 2
    for _ in range(count):
        _, i = varint(rom, i)
    return i

def journal(slot: bytes, rom: bytes) -> list:
    """[(quest text, 'finished' | 'active' | 'hidden')]: done is tested first, as at 0x08004A92."""
    out = []
    for q in range(QUEST_COUNT):
        _, done, active, text = struct.unpack_from("<4I", rom, QUEST_TABLE - ROM_BASE + q * QUEST_SIZE)
        t = text - ROM_BASE
        name = rom[t:rom.index(b"\0", t)].decode("latin1")
        state = "finished" if run_cond(rom, done, slot) else "active" if run_cond(rom, active, slot) else "hidden"
        out.append((name, state))
    return out

# ===== Report =====
def describe(sav: bytes, show_flags: bool) -> None:
    ram = read_ram(sav)
    opts = bytes(ram[0:4])
    oc = struct.unpack_from("<I", ram, 4)[0]
    ok = oc == (adler32(opts) + OPT_MAGIC) & 0xFFFFFFFF
    print(f"options: {opts.hex(' ')} check {oc:#010x} {'valid' if ok else 'INVALID (game uses 4 6 4 0)'}")
    for n in range(SLOT_COUNT):
        s = bytes(ram[slot_range(n)])
        stored = struct.unpack_from("<I", s, SLOT_DATA)[0]
        calc = adler32(s[:SLOT_DATA])
        assert calc == zlib.adler32(s[:SLOT_DATA]), "own Adler-32 disagrees with zlib"
        used = s[O_FLAGS] & 1
        state = "valid" if stored == calc else "BAD CHECKSUM"
        print(f"\nslot {n + 1}: checksum stored {stored:#010x} calc {calc:#010x} {state}; "
              f"in-use bit {used} -> {'shown' if used and stored == calc else 'empty'}")
        if stored != calc:
            continue
        x, y = struct.unpack_from("<hh", s, O_POS)
        print(f"  leader {s[O_LEADER]} ({CHAR_NAMES[s[O_LEADER]] if s[O_LEADER] < 6 else '?'})"
              f"  header flags {s[O_FLAGS]:#04x}  map zone {s[O_ZONE]} area {s[O_AREA]} var {s[O_VAR]}"
              f"  pos ({x},{y})  +8 {struct.unpack_from('<I', s, 8)[0]:#x}")
        for c in range(6):
            r = s[O_CHARS + c * CHAR_SIZE:O_CHARS + (c + 1) * CHAR_SIZE]
            hp, hpm, ep, epm = struct.unpack_from("<4H", r, 0)
            st, pw, en = (v / 256 for v in struct.unpack_from("<3H", r, 0x0A))
            exp, cflags = struct.unpack_from("<II", r, 0x10)
            app = r[8]
            app_s = APPEARANCE_SET[app] if app < len(APPEARANCE_SET) else "?"
            print(f"  {CHAR_NAMES[c]:8} Lv{level_of(exp):2} EXP {exp:8} HP {hp}/{hpm} EP {ep}/{epm} "
                  f"STR {st:.2f} POW {pw:.2f} END {en:.2f} flags {cflags:#04x} appearance {app}"
                  f" (set {app_s}) tech {r[9]} | {check_stats(c, r)}")
        story = [i for i in range(STORY_BITS) if bit(s, O_STORY, i)]
        visited = sum(bit(s, O_VISITED, i) for i in range(VISITED_BITS))
        scouter = sum(bit(s, O_SCOUTER, i) for i in range(SCOUTER_BITS))
        items = {i: s[O_ITEMS + i] for i in range(ITEM_COUNT) if s[O_ITEMS + i]}
        print(f"  story flags set: {len(story)}  (191 = Dragon Balls returned: {bit(s, O_STORY, 191)}, "
              f"195 = Cell beaten: {bit(s, O_STORY, 195)}, 196 = final goodbye: {bit(s, O_STORY, 196)})")
        if show_flags:
            print(f"    {ranges(story)}")
        print(f"  visited maps {visited}/{VISITED_BITS}  scouter entries {scouter}/{SCOUTER_BITS}  items {items or '-'}")

def print_journal(sav: bytes, rom: bytes) -> None:
    ram = read_ram(sav)
    for n in range(SLOT_COUNT):
        s = bytes(ram[slot_range(n)])
        print(f"slot {n + 1}:")
        for name, state in journal(s, rom):
            if state != "hidden":
                print(f"  {state:8} {name}")

# ===== Writers =====
def make_slot(story, leader, zone, area, var, x, y) -> bytearray:
    flags, records = STORIES[story]
    s = bytearray(SLOT_SIZE)
    s[O_LEADER] = leader
    # bit0 in use (0x0800405E), bit1 as in normal play (capture 01). bit1 is the HUD bit, so a lab story
    # starts with the HUD already off and the first captured frame carries no bar.
    s[O_FLAGS] = 0x01 if story in HUD_OFF_STORIES else 0x03
    s[O_ZONE], s[O_AREA], s[O_VAR] = zone, area, var
    for c, hexrec in enumerate(records):
        rec = bytearray.fromhex(hexrec)
        rec[8] = POSTCELL_APPEARANCE[c]
        s[O_CHARS + c * CHAR_SIZE:O_CHARS + (c + 1) * CHAR_SIZE] = rec
    for lo, hi in flags:
        for f in range(lo, hi + 1):
            set_bit(s, O_STORY, f)
    for v in range(VISITED_BITS):
        set_bit(s, O_VISITED, v, v not in UNVISITED.get(story, ()))
    for item, count in POSTCELL_ITEMS.items():
        s[O_ITEMS + item] = count
    struct.pack_into("<hh", s, O_POS, x, y)
    return s

def build(base: Path, out: Path, preset_set: str = DEFAULT_SET) -> None:
    ram = read_ram(base.read_bytes())
    seal_options(ram, OPT_DEFAULT)
    for n, (label, story, leader, zone, area, var, x, y) in enumerate(PRESET_SETS[preset_set]):
        ram[slot_range(n)] = make_slot(story, leader, zone, area, var, x, y)
        seal_slot(ram, n)
        print(f"slot {n + 1}: {label}  [{story}, leader {CHAR_NAMES[leader]}]  "
              f"zone {zone} area {area} var {var} pos ({x},{y})")
    write(out, ram)

def edit(src: Path, out: Path, n: int, pairs) -> None:
    ram = read_ram(src.read_bytes())
    sl = slot_range(n)
    s = ram[sl]
    for p in pairs:
        key, val = p.split("=", 1)
        nums = [int(v, 0) for v in val.split(",")] if key != "visited" else []
        if key == "leader":
            s[O_LEADER] = nums[0]
        elif key == "map":
            s[O_ZONE], s[O_AREA], s[O_VAR] = nums
        elif key == "pos":
            struct.pack_into("<hh", s, O_POS, *nums)
        elif key in ("flag+", "flag-"):
            set_bit(s, O_STORY, nums[0], key == "flag+")
        elif key == "item":
            s[O_ITEMS + nums[0]] = nums[1]
        elif key == "visited":
            for v in range(VISITED_BITS):
                set_bit(s, O_VISITED, v, val == "all")
        else:
            sys.exit(f"Unknown key {key}.")
    ram[sl] = s
    seal_slot(ram, n)
    write(out, ram)

def write(out: Path, ram: bytearray) -> None:
    if "data" in [p.lower() for p in out.resolve().parts]:
        sys.exit("Refusing to write under a data folder.")
    if out.exists():
        sys.exit(f"Refusing to overwrite {out}. Pick a new file name.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(swap_blocks(bytes(ram)))
    print(f"wrote {out} ({SAV_SIZE} bytes)")

def main():
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "info":
        describe(Path(a[1]).read_bytes(), "--flags" in a)
    elif len(a) == 3 and a[0] == "journal":
        print_journal(Path(a[1]).read_bytes(), Path(a[2]).read_bytes())
    elif len(a) in (3, 5) and a[0] == "build":
        chosen = a[4] if len(a) == 5 and a[3] == "--set" else DEFAULT_SET
        if len(a) == 5 and (a[3] != "--set" or chosen not in PRESET_SETS):
            sys.exit(f"--set takes one of {', '.join(PRESET_SETS)}.")
        build(Path(a[1]), Path(a[2]), chosen)
    elif len(a) >= 5 and a[0] == "set":
        edit(Path(a[1]), Path(a[2]), int(a[3]) - 1, a[4:])
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main()
