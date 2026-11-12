r"""
test_battle_arena.py - Tests for patches.battle_arena (trial 2026-11-05): a new map, 6,100, that is a
                       battle arena for the ending fight. It carries no door in either carrier, it
                       lists an NPC Cell and an enemy Cell, and its collision, props and BG2 are copies
                       of map 6,1's with the changes the owner asked for: the building recess is closed,
                       the map post and the save point are gone with the block one of them stood on, and
                       the two drawn-in shadows are gone.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_battle_arena.py -v
Builds build_list_trial_ending.txt in memory: "before" = the dev master (r41), "rom" = before plus
battle_arena only, so every check reads the arena BEFORE ending_fight fills in the death event. Every
expected value is restated from docs\tasks\2026-11-05-ending-arena\brief.md and the base bytes read in
scripts\one-time\2026-11-05-ending-arena\01_probe.txt to 07_cell_event.txt. Nothing is imported from the
patch module except apply() and the builders the design lives in.
"""
import copy
import struct
import unittest

import log2_build
from patches import battle_arena
from rom.rom_space import Allocator
from rom.webfoot_decompress import unpack_frame
from scene import scene_lib as S
from tests.test_cellgames_ssj import diff, ext_sequence

# ===== constants (brief, base reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_ending.txt"
MAPS, MAP_SIZE, MAP_COUNT = 0x409368, 56, 327
NEXT_TABLE = MAPS + MAP_SIZE * MAP_COUNT                      # rom:0x40DAF0: a second table, not padding
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)
ENTRY3_LITERAL, ENTRY3 = 0x195C, 3                            # names map 1,4's entry directly
COUNT_FN, COUNT_BYTE = 0xE0AC, 0xE0AE
COUNT_CODE_HEX = "ff2048307047"                               # MOV r0,#0xFF ; ADD r0,#0x48 ; BX lr
SOURCE_AT = MAPS + MAP_SIZE * 145                             # map 6,1, rom:0x40B320
ARENA_ZONE, ARENA_AREA, ARENA_INDEX = 6, 100, 327
CELL_ITEM = 0x4058A4
CELL_ITEM_HEX = ("7fe70008" "88000200" "3c000000" "08018000" "1c000000" "9c584008" "01000000" "94584008")
CELL_EVENT_AT, CELL_EVENT_HEX = 0x40589C, "b3060108a0243e08"
CELL_TAIL_AT, CELL_TAIL_HEX = 0x405894, "0fcb0008007d0000"
ENEMY_FACTORY, EVENT_RUNNER = 0x0800E77F, 0x080106B3
TYPE_TABLE, TYPE_SIZE, CELL_TYPE = 0x6D56AC, 24, 60
TYPE60_HEX = ("00000000" "5a140000" "50000000" "20202580" "80000000" "c4f36f08")
CELL_SPOT, CELL_SET = (244, 504), 28                          # the spots the CONVERSATION leaves them on
TRUNKS_SPOT = (248, 568)                                      # (his v3 states 1 and 2; see battle_arena)
# Where each walk STARTS, both of them map 6,1's own NPC spots, so the arena plays the vanilla talk
# move for move: item 6 is the NPC Cell and item 5 the NPC Super Saiyan Trunks.
CELL_START, TRUNKS_START = (288, 392), (248, 624)
NPC_FACTORY, NPC_ITEM_SIZE = 0x0800D6DF, 0x18
SOURCE_CELL_NPC_AT = 0x3F9C28                                 # map 6,1 item 6: the NPC Imperfect Cell
SOURCE_CELL_NPC_HEX = "dfd60008" "c4000100" "20018801" "1c000000" "01000000" "209c3f08"
NPC_STEP_AT, NPC_STEP_HEX = 0x3F9C20, "0fcb0008007d0000"      # the stand step both NPC items name
NPC_COND_VANILLA = 0x000100C4                                 # Script_TestFlag: "flag 196 set"
ARENA_ITEMS, NPC_INDEX, ENEMY_INDEX = 2, 0, 1
V3_SPOTS = ((244, 616), (248, 680))                           # the v3 pair, 112 px lower: the jump he saw
EXPANSION = (0x800000, 0xF00000)
NO_BANNER = 0xDD                                              # entry +0x0C: LIKELY "no name", 5 carriers
# Map 6,1's layout chain, read from the base ROM in p1_probe.py and v2_layout.py. The arena copies the
# layout struct, so every link of the REAL map must still read vanilla after the build.
SOURCE_LAYOUTS, SOURCE_LAYOUT, SOURCE_FRAME = 0x3F9B2C, 0x5F209C, 0x5F164C
LAYOUT_SIZE, L_COLLISION = 0xCC, 0x34
# The layout's own door list, measured in v3_census.py and decoded with scene_probe's item reader:
# map 6,1 carries 3 warps there, one of them the Capsule Corp front door to map 6,2 at (144,276).
L_WARP_COUNT, L_WARP_LIST = 0x40, 0x44
SOURCE_WARPS, SOURCE_WARP_LIST = 3, 0x5F2090                  # +0x44 is a list of POINTERS, 3 of them
SOURCE_DOOR, SOURCE_DOOR_RECT = 0x5F2078, (224, 88, 273, 105)  # list[2]: the Capsule Corp front door
SEALED_MAP = (14, 3)                                          # the Cell Games arena: 0 regions, 0 warps
# The arena's own collision frame. collision_test @0x08005D6C: byte cy x 32 + (cx >> 3), bit cx & 7, SET
# = OPEN, 8 px cells. The building is an 8 cell corridor cx 28 to 35, cy 9 to 11, and the courtyard starts
# at cy 12. His state 5 stands at (246,72), inside; his state 4 at (246,94), in front.
FRAME_STRIDE, FRAME_SIZE, MAP_CELLS = 32, 0x2000, 128
# v6 closed rows 9 and 10 and left 11, which made a one row pocket the owner walked into and stood in:
# "its like I run into a wall, but I can walk into it". His state 4 at (246,94) is cell (30,11), that row.
INSIDE_BAND = (28, 9, 35, 11)
INSIDE_PX, FRONT_PX = (246, 72), (246, 94)
FIRST_COURTYARD_ROW = 12                                      # the wall is now flush with this row
POST_FOOT = (32, 28)                                          # the one closed cell under the map post
# The arena's own BG2. A layer record is 0x38 bytes: +0x14 blocks across, +0x15 down, +0x18 one frame
# pointer per block. BG3's first block frame starts at BG2's record +0x38, which is what bounds the size.
L_BG2, SOURCE_BG2, BG2_SIZE = 0x1C, 0x5F1434, 0x38
BG2_PTRS, BG2_GRID, BLOCK_TILES, BLOCK_SIZE = 0x18, (2, 4), 32, 0x800
SHADOW_INDEX, SHADOW_TILES = 73, 28                           # BG palette (144,200,248); 10 + 18 tiles
SHADOW_BOXES = ((30, 43, 34, 44), (52, 86, 59, 92))           # in TILES; the owner's boxes in px below
# Map 6,1's layout props, bible row 1119: +0x24 count, +0x28 entries of 24 bytes whose first four u32
# are the rectangle. Each one was DRAWN from the sheet at +0x2C and named by eye in p3_props.py.
L_PROP_COUNT, L_PROP_LIST, PROP_SIZE = 0x24, 0x28, 24
SOURCE_PROPS, SOURCE_PROP_LIST = 5, 0x5F16DC
SOURCE_PROP_RECTS = ((224, 64, 288, 96),                      # 0 the glass front door
                     (240, 200, 272, 232),                    # 1 the MAP POST, cut
                     (408, 556, 472, 620),                    # 2 the SAVE POINT, cut
                     (198, 95, 214, 127),                     # 3 the west entrance pillar
                     (294, 95, 310, 127))                     # 4 the east entrance pillar
ARENA_PROPS, CUT_PROPS = (0, 3, 4), (1, 2)
SHADOW_BOXES_PX = (((246, 344), (274, 359)), ((420, 694), (474, 739)))
SHADOW_PX_BEFORE = (270, 602)                                 # index 73 pixels he counted in each box
COPIED_BLOCKS = (2, 3, 5)                                     # the only blocks a shadow box touches
# The music. sub_0800EB58 reads entry +0x24 as the song id when it is under 0x10000. The map load at
# loc_0800C4D6 skips music_play when the player already plays that record, so naming the ending's own
# song keeps the track running. 0xFF stops the player; the table at 0x081D4B2C holds 44 songs.
ENDING_TABLE, MUSIC_OP, MUSIC_STOP_OP = 0x3B8140, 49, 50
ENDING_MUSIC, MUSIC_SONGS, MUSIC_STOP = 38, 44, 0xFF

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def padded() -> bytearray:
    base = log2_build.BASE.read_bytes()
    return bytearray(base) + b"\xFF" * (log2_build.ROM_SIZE - len(base))


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("battle_arena")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["battle_arena"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["battle_arena"])
    return _CACHE


def entry(rom: bytes, table: int, index: int) -> bytes:
    return rom[table + MAP_SIZE * index:table + MAP_SIZE * (index + 1)]


def named_by(rom: bytes, target: int) -> list:
    want = struct.pack("<I", target + ROM_BASE)
    out, at = [], 0
    while True:
        at = rom.find(want, at)
        if at < 0:
            return out
        if at % 4 == 0:
            out.append(at)
        at += 1


# ===== reading the arena's art back out of the ROM =====

def frame(rom: bytes, address: int) -> bytes:
    return unpack_frame(rom, address - ROM_BASE)[2]


def collision_bits(rom: bytes, layout: int) -> bytes:
    return frame(rom, u32(rom, layout + L_COLLISION))


def is_open(bits: bytes, cx: int, cy: int) -> bool:
    return bool(bits[cy * FRAME_STRIDE + (cx >> 3)] >> (cx & 7) & 1)


def band_cells(band: tuple) -> set:
    cx0, cy0, cx1, cy1 = band
    return {(cx, cy) for cy in range(cy0, cy1 + 1) for cx in range(cx0, cx1 + 1)}


def reachable(bits: bytes, start: tuple) -> set:
    """Every open cell a walker reaches from start, 4 way, over the 128 x 128 cells the map really has."""
    seen, stack = {start}, [start]
    while stack:
        cx, cy = stack.pop()
        for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if 0 <= n[0] < MAP_CELLS and 0 <= n[1] < MAP_CELLS and n not in seen and is_open(bits, *n):
                seen.add(n)
                stack.append(n)
    return seen


def tile_pixels(rom: bytes, layout: int) -> list:
    """The layout's 8x8 tiles. +0x48 is a delta coded index (entry + the one before + 1), +0x4C the
    chunk table. Rebuilt here, not imported from the patch, so the test does not trust its decoder."""
    raw = frame(rom, u32(rom, layout + 0x48))
    idx = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = u32(rom, layout + 0x4C) - ROM_BASE, {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = frame(rom, u32(rom, table + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def layer_entries(rom: bytes, record: int) -> dict:
    """{(tile x, tile y): u16 entry} of a layer record, over its whole block grid."""
    across, down = rom[record + 0x14], rom[record + 0x15]
    out = {}
    for k in range(across * down):
        block = frame(rom, u32(rom, record + BG2_PTRS + 4 * k))
        ox, oy = (k % across) * BLOCK_TILES, (k // across) * BLOCK_TILES
        for t in range(BLOCK_TILES * BLOCK_TILES):
            out[(ox + t % BLOCK_TILES, oy + t // BLOCK_TILES)] = struct.unpack_from("<H", block, 2 * t)[0]
    return out


def layer_pixels(rom: bytes, record: int, tiles: list) -> dict:
    """{(x, y): palette index} of every pixel a layer draws. Index 0 is transparent and never stored."""
    out = {}
    for (tx, ty), e in layer_entries(rom, record).items():
        tile = e & 0x3FF
        if tile >= len(tiles):
            continue
        for i, v in enumerate(tiles[tile]):
            if not v:
                continue
            dx, dy = i % 8, i // 8
            out[(tx * 8 + (7 - dx if e & 0x400 else dx), ty * 8 + (7 - dy if e & 0x800 else dy))] = v
    return out


# ===== the build list =====

class ListTests(unittest.TestCase):
    def test_the_arena_runs_before_the_ending_fight(self):
        names = log2_build.read_build_list(TRIAL_LIST)
        self.assertLess(names.index("battle_arena"), names.index("ending_fight"))

    def test_the_arena_runs_after_every_module_that_edits_a_map_entry(self):
        """chamber_spar rewrites map 6,70 in place. A module that did that AFTER the move would
        write into the dead old table, and the game would never read it."""
        names = log2_build.read_build_list(TRIAL_LIST)
        self.assertLess(names.index("chamber_spar"), names.index("battle_arena"))

    def test_the_module_is_in_no_master_list(self):
        for path in (log2_build.BUILD_LIST, log2_build.DEV_LIST):
            self.assertNotIn("battle_arena", log2_build.read_build_list(path))

    def test_no_module_after_the_arena_writes_a_map_entry(self):
        """The one hazard the module cannot check itself, because it runs first. A write into the OLD
        table after the move is a write the game never reads. This builds the whole trial list and
        reads every later module's declared sites."""
        names = log2_build.read_build_list(TRIAL_LIST)
        after = names[names.index("battle_arena") + 1:]
        _, alloc = log2_build.assemble(log2_build.BASE, names)
        old = range(MAPS, MAPS + MAP_SIZE * MAP_COUNT)
        for name in after:
            for site in alloc.notes[name]["sites"]:
                at, n = (site, 1) if isinstance(site, int) else tuple(site)[:2]
                self.assertTrue(at + n <= old.start or at >= old.stop,
                                f"{name} writes rom:0x{at:X} inside the dead old map table")


# ===== fail closed =====

class FailClosedTests(unittest.TestCase):
    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["battle_arena"] = {}
        with self.assertRaises(ValueError):
            battle_arena.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                       # the literals and the count byte have moved too
        with self.assertRaises(ValueError):
            battle_arena.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        for off in (BASE_LITERALS[0], BASE_LITERALS[1], BASE_LITERALS[2], ENTRY3_LITERAL,
                    COUNT_FN, COUNT_FN + 5, COUNT_BYTE, SOURCE_AT, SOURCE_AT + 1, SOURCE_AT + 0x2C,
                    CELL_ITEM + 8, CELL_EVENT_AT, CELL_TAIL_AT,
                    TYPE_TABLE + TYPE_SIZE * CELL_TYPE + 4):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                battle_arena.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap, f"rom:0x{off:X} wrote before it refused")

    def test_a_second_namer_of_the_table_or_of_entry_3_refuses(self):
        for target in (MAPS, MAPS + MAP_SIZE * ENTRY3):
            rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
            rom[0x900000:0x900004] = struct.pack("<I", target + ROM_BASE)
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"0x{target:X}"):
                battle_arena.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_map_that_already_uses_the_arena_area_refuses(self):
        b = built()
        rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
        rom[MAPS], rom[MAPS + 1] = ARENA_ZONE, ARENA_AREA
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            battle_arena.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_a_guarded_site_refuses(self):
        for site in ((NEXT_TABLE, 4, "other"),
                     (COUNT_FN, 2, "other"), (CELL_ITEM, 0x20, "other"),
                     (CELL_EVENT_AT, 8, "other"), (BASE_LITERALS[1], 4, "other"),
                     (ENTRY3_LITERAL, 4, "other"), (SOURCE_FRAME, 8, "other"),
                     (SOURCE_BG2, BG2_SIZE, "other"), (0x5F0B3C, 4, "other")):
            rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
            alloc.notes["other"] = {"sites": [site]}
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(site)):
                battle_arena.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)


# ===== the moved table =====

class TableTests(unittest.TestCase):
    def test_every_literal_now_names_the_new_table(self):
        b = built()
        table = b["notes"]["table"]
        for lit in BASE_LITERALS:
            self.assertEqual(u32(b["rom"], lit), table + ROM_BASE, f"rom:0x{lit:X}")
        self.assertEqual(u32(b["rom"], ENTRY3_LITERAL), table + MAP_SIZE * ENTRY3 + ROM_BASE)

    def test_the_four_literals_are_every_word_that_named_the_old_table_or_its_entry_3(self):
        """One grep is one shape. The base scan found 3 words equal to the table base; a word that
        names an entry in the MIDDLE would not appear in it, and rom:0x195C is exactly that."""
        b = built()
        self.assertEqual(named_by(b["before"], MAPS), list(BASE_LITERALS))
        self.assertEqual(named_by(b["before"], MAPS + MAP_SIZE * ENTRY3), [ENTRY3_LITERAL])
        self.assertEqual(named_by(b["rom"], MAPS), [])
        self.assertEqual(named_by(b["rom"], MAPS + MAP_SIZE * ENTRY3), [])

    def test_the_count_getter_returns_328(self):
        b = built()
        self.assertEqual(b["before"][COUNT_FN:COUNT_FN + 6].hex(), COUNT_CODE_HEX)
        self.assertEqual(0xFF + b["before"][COUNT_BYTE], MAP_COUNT)
        self.assertEqual(0xFF + b["rom"][COUNT_BYTE], MAP_COUNT + 1)
        for off in (COUNT_FN, COUNT_FN + 1, COUNT_FN + 3, COUNT_FN + 4, COUNT_FN + 5):
            self.assertEqual(b["rom"][off], b["before"][off], f"rom:0x{off:X}")

    def test_the_old_table_is_left_byte_for_byte(self):
        """So any word that still names the old table reads vanilla data, and the table that starts
        at rom:0x40DAF0 is untouched."""
        b = built()
        old = slice(MAPS, MAPS + MAP_SIZE * MAP_COUNT)
        self.assertEqual(b["rom"][old], b["before"][old])
        self.assertEqual(b["rom"][NEXT_TABLE:NEXT_TABLE + 16], b["before"][NEXT_TABLE:NEXT_TABLE + 16])

    def test_the_new_table_copies_all_327_live_entries(self):
        b = built()
        table = b["notes"]["table"]
        self.assertEqual(b["rom"][table:table + MAP_SIZE * MAP_COUNT], b["before"][MAPS:MAPS + MAP_SIZE * MAP_COUNT])

    def test_the_copy_reads_the_live_rom_not_the_base_rom(self):
        """chamber_spar edits map 6,70 in place, so the copy must carry its edit, or the training
        room loses its sparring fight the moment the table moves."""
        b = built()
        base = log2_build.BASE.read_bytes()
        table, spar = b["notes"]["table"], MAPS + MAP_SIZE * 175
        self.assertNotEqual(b["before"][spar:spar + MAP_SIZE], base[spar:spar + MAP_SIZE])
        self.assertEqual(entry(b["rom"], table, 175), b["before"][spar:spar + MAP_SIZE])

    def test_zone_and_area_stay_unique_and_the_table_is_one_longer(self):
        b = built()
        table = b["notes"]["table"]
        pairs = [(b["rom"][table + MAP_SIZE * m], b["rom"][table + MAP_SIZE * m + 1])
                 for m in range(MAP_COUNT + 1)]
        self.assertEqual(len(set(pairs)), MAP_COUNT + 1)
        self.assertEqual(pairs[ARENA_INDEX], (ARENA_ZONE, ARENA_AREA))


# ===== the arena entry =====

class ArenaEntryTests(unittest.TestCase):
    def test_the_arena_is_map_6_100_with_one_variation(self):
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual((e[0], e[1]), (ARENA_ZONE, ARENA_AREA))
        self.assertEqual(e[2], 1, "+0x02 variation count: 318 vanilla entries use 1")

    def test_combat_is_on(self):
        """Map 6,1 carries 0 here, which is why the v5 play test could move but not attack."""
        b = built()
        self.assertEqual(entry(b["rom"], b["notes"]["table"], ARENA_INDEX)[8], 1)
        self.assertEqual(b["rom"][SOURCE_AT + 8], 0, "map 6,1 is still a non-combat map")

    def test_there_are_no_regions_so_no_exit_no_save_point_and_no_world_map(self):
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual(e[3], 0, "+0x03 region count")
        self.assertEqual(u32(e, 0x10), 0, "+0x10 region list")

    def test_every_other_list_is_empty_so_no_vanilla_npc_stands_in_the_arena(self):
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        for count_byte, list_word, what in ((3, 0x10, "regions"), (5, 0x18, "swaps"),
                                            (6, 0x1C, "pickups"), (7, 0x20, "markers")):
            self.assertEqual(e[count_byte], 0, what)
            self.assertEqual(u32(e, list_word), 0, what)
        for off, what in ((0x28, "variation script"), (0x30, "enter script"), (0x34, "leave script")):
            self.assertEqual(u32(e, off), 0, what)

    def test_the_music_word_names_the_song_the_ending_is_already_playing(self):
        """His call on 2026-11-06: "the music should not change ... right now its a very abrupt
        transition". The map load reads +0x24 through sub_0800EB58 and calls music_play UNLESS the
        player already plays that record (loc_0800C4D6: +5 is 1 and +0xC equal). So the only value that
        continues the track is the song the ending itself started. 0 is song 0, not "leave it alone"."""
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual(u32(e, 0x24), ENDING_MUSIC)
        self.assertLess(ENDING_MUSIC, 0x10000, "a value this small is the id itself, not a script")
        self.assertLess(ENDING_MUSIC, MUSIC_SONGS, "the music table holds 44 songs")
        self.assertNotEqual(ENDING_MUSIC, MUSIC_STOP, "0xFF would stop the player")

    def test_that_song_is_the_one_the_ending_record_0_starts(self):
        """Read the id out of the ending table itself, so the constant cannot drift from the scene."""
        b = built()
        record = u32(b["rom"], ENDING_TABLE) - ROM_BASE
        songs = [args[0] for op, args in ext_sequence(b["rom"], record) if op == MUSIC_OP]
        self.assertEqual(songs[-1], ENDING_MUSIC, "record 0's last music op")
        later = []
        for k in range(1, 23):                       # every record of the conversation, the fight is 23
            at = u32(b["rom"], ENDING_TABLE + 4 * k) - ROM_BASE
            if S.decode_record(b["rom"], at).kind != S.TYPE_CODE:
                continue                             # a text record carries no ops
            later += [op for op, _args in ext_sequence(b["rom"], at) if op in (MUSIC_OP, MUSIC_STOP_OP)]
        self.assertEqual(later, [], "no record before the fight changes or stops the music")

    def test_the_item_count_matches_the_item_list(self):
        """Two items, the NPC first and the enemy second. The order is the interface: ending_fight's
        record F runs ext 104 (28, 1), and Object_SpawnFromEntry @0x0800C75C bounds that index against
        this very count byte, so an item list of one would make the op do nothing at all."""
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual(e[4], ARENA_ITEMS)
        self.assertEqual(u32(e, 0x14), b["notes"]["items"] + ROM_BASE)
        self.assertEqual(u32(b["rom"], b["notes"]["items"] + 4 * NPC_INDEX),
                         b["notes"]["npc_item"] + ROM_BASE)
        self.assertEqual(u32(b["rom"], b["notes"]["items"] + 4 * ENEMY_INDEX),
                         b["notes"]["item"] + ROM_BASE)
        self.assertEqual((b["notes"]["npc_item_index"], b["notes"]["item_index"]),
                         (NPC_INDEX, ENEMY_INDEX))
        self.assertGreater(e[4], ENEMY_INDEX, "ext 104 (28, 1) must be inside the item count")

    def test_the_arena_shows_no_name_banner(self):
        """His v7 play test: the Capsule Corp banner drew over the fight, mid fight. Map 6,1's own id
        is 0xBE. The arena carries 0xDD, which 5 vanilla entries carry and which is LIKELY "no name"."""
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual(u32(e, 0x0C), NO_BANNER)
        self.assertEqual(u32(b["rom"], SOURCE_AT + 0x0C), 0xBE, "map 6,1 keeps its own banner")
        self.assertNotEqual(u32(e, 0x0C), u32(b["rom"], SOURCE_AT + 0x0C))

    def test_the_arena_has_its_own_layout_list_not_map_6_1_s(self):
        """The arena must differ from map 6,1 at the door list, so the layout cannot be shared.
        Sharing it would take the doors out of the real map 6,1 as well."""
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual(u32(e, 0x2C), b["notes"]["layouts"] + ROM_BASE)
        self.assertNotEqual(u32(e, 0x2C), SOURCE_LAYOUTS + ROM_BASE)
        self.assertEqual(u32(b["rom"], b["notes"]["layouts"]), b["notes"]["layout"] + ROM_BASE)

    def test_map_6_1_itself_is_not_changed(self):
        b = built()
        self.assertEqual(b["rom"][SOURCE_AT:SOURCE_AT + MAP_SIZE], b["before"][SOURCE_AT:SOURCE_AT + MAP_SIZE])


# ===== the arena enemy =====

class EnemyTests(unittest.TestCase):
    def test_the_item_is_the_vanilla_cell_item_with_four_fields_changed(self):
        b = built()
        item, vanilla = b["notes"]["item"], bytes.fromhex(CELL_ITEM_HEX)
        got = b["rom"][item:item + 0x20]
        self.assertEqual(u32(got, 0), ENEMY_FACTORY)
        self.assertEqual(u32(got, 4), 1, "cond 1: the load leaves him alone and ext 104 builds him")
        self.assertEqual(u32(got, 8), CELL_TYPE)
        self.assertEqual(struct.unpack_from("<hh", got, 0xC), CELL_SPOT)
        self.assertEqual(u32(got, 0x10), CELL_SET)
        self.assertEqual(u32(got, 0x14), b["notes"]["event"] + ROM_BASE)
        self.assertEqual(u32(got, 0x1C), b["notes"]["tail"] + ROM_BASE)
        for off in (0, 8, 0x10, 0x18):                      # every field that is not one of the four
            self.assertEqual(got[off:off + 4], vanilla[off:off + 4], f"+0x{off:X}")

    def test_the_event_struct_and_the_step_struct_are_fresh_copies(self):
        """ending_fight overwrites the event struct's table word, so it must never be the vanilla one."""
        b = built()
        self.assertEqual(b["rom"][b["notes"]["event"]:b["notes"]["event"] + 8], bytes.fromhex(CELL_EVENT_HEX))
        self.assertEqual(b["rom"][b["notes"]["tail"]:b["notes"]["tail"] + 8], bytes.fromhex(CELL_TAIL_HEX))
        self.assertNotEqual(b["notes"]["event"], CELL_EVENT_AT)
        self.assertNotEqual(b["notes"]["tail"], CELL_TAIL_AT)
        self.assertEqual(u32(b["rom"], b["notes"]["event"]), EVENT_RUNNER)
        self.assertEqual(b["rom"][CELL_EVENT_AT:CELL_EVENT_AT + 8], b["before"][CELL_EVENT_AT:CELL_EVENT_AT + 8])

    def test_the_vanilla_cell_item_is_untouched(self):
        b = built()
        self.assertEqual(b["rom"][CELL_ITEM:CELL_ITEM + 0x20], bytes.fromhex(CELL_ITEM_HEX))

    def test_imperfect_cell_keeps_every_vanilla_stat(self):
        b = built()
        at = TYPE_TABLE + TYPE_SIZE * CELL_TYPE
        self.assertEqual(b["rom"][at:at + TYPE_SIZE], bytes.fromhex(TYPE60_HEX))
        self.assertEqual(b["rom"][at:at + TYPE_SIZE], b["before"][at:at + TYPE_SIZE])
        self.assertEqual(u32(b["rom"], at + 4), 5210)
        self.assertEqual(u32(b["rom"], at + 8), 80)
        self.assertEqual(u32(b["rom"], at + 0x14), 0x086FF3C4, "the boss descriptor holds Cell at HP 0")

    def test_the_arena_item_is_named_only_by_the_arena_list(self):
        b = built()
        self.assertEqual(named_by(b["rom"], b["notes"]["item"]),
                         [b["notes"]["items"] + 4 * ENEMY_INDEX])
        self.assertEqual(named_by(b["rom"], b["notes"]["npc_item"]),
                         [b["notes"]["items"] + 4 * NPC_INDEX])

    def test_the_npc_cell_is_map_6_1_s_own_item_with_its_condition_opened(self):
        """The actor the whole conversation talks to. Vanilla record 15 runs walk(28, 244, 504), which
        needs a set 28 actor already on the map, and in vanilla that actor is map 6,1 item 6. The arena
        copies it and changes the condition from "flag 196 set" to "always": the arena is reached only
        from the ending, which is the one place flag 196 is set, so the two readings agree."""
        b = built()
        got = b["rom"][b["notes"]["npc_item"]:b["notes"]["npc_item"] + NPC_ITEM_SIZE]
        vanilla = bytes.fromhex(SOURCE_CELL_NPC_HEX)
        self.assertEqual(u32(got, 0), NPC_FACTORY)
        self.assertEqual(u32(got, 4), 0, "always, so the map load builds him")
        self.assertEqual(u32(vanilla, 4), NPC_COND_VANILLA, "map 6,1 gates him on flag 196")
        self.assertEqual(struct.unpack_from("<hh", got, 8), CELL_START)
        self.assertEqual(struct.unpack_from("<hh", vanilla, 8), CELL_START, "his own vanilla spot")
        self.assertEqual(u32(got, 0xC), CELL_SET)
        self.assertEqual(u32(got, 0x10), 1, "one step, the stand step")
        self.assertEqual(u32(got, 0x14), b["notes"]["npc_step"] + ROM_BASE)
        self.assertEqual(b["rom"][b["notes"]["npc_step"]:b["notes"]["npc_step"] + 8],
                         bytes.fromhex(NPC_STEP_HEX))
        self.assertNotEqual(b["notes"]["npc_step"], NPC_STEP_AT, "a fresh copy, not map 6,1's own")

    def test_map_6_1_s_own_npc_cell_and_its_step_are_untouched(self):
        b = built()
        self.assertEqual(b["rom"][SOURCE_CELL_NPC_AT:SOURCE_CELL_NPC_AT + NPC_ITEM_SIZE],
                         bytes.fromhex(SOURCE_CELL_NPC_HEX))
        self.assertEqual(b["rom"][NPC_STEP_AT:NPC_STEP_AT + 8], bytes.fromhex(NPC_STEP_HEX))

    def test_the_two_cells_are_the_pair_map_11_4_carries_for_android_17(self):
        """The vanilla shape of every fight that starts out of a talk, and the shape ext 104 needs:
        an NPC item with condition 0 that the load builds, and an enemy item with condition 1 that
        only ext 104 builds. Map 11,4 items 0 and 1 are exactly that pair for set 9, and its word 6
        rom:0x3E47DC is the four op record the owner pointed at."""
        b = built()
        npc, enemy = 0x40646C, 0x406494                       # map 11,4 items 0 and 1, both set 9
        self.assertEqual((u32(b["before"], npc), u32(b["before"], npc + 4)), (NPC_FACTORY, 0))
        self.assertEqual((u32(b["before"], enemy), u32(b["before"], enemy + 4)), (ENEMY_FACTORY, 1))
        self.assertEqual(u32(b["before"], npc + 0xC), u32(b["before"], enemy + 0x10), "the same set")
        mine_npc = b["notes"]["npc_item"]
        mine_enemy = b["notes"]["item"]
        self.assertEqual((u32(b["rom"], mine_npc), u32(b["rom"], mine_npc + 4)), (NPC_FACTORY, 0))
        self.assertEqual((u32(b["rom"], mine_enemy), u32(b["rom"], mine_enemy + 4)), (ENEMY_FACTORY, 1))
        self.assertEqual(u32(b["rom"], mine_npc + 0xC), u32(b["rom"], mine_enemy + 0x10))


# ===== the whole ROM =====

class RomTests(unittest.TestCase):
    def test_every_changed_byte_is_a_declared_site(self):
        b = built()
        declared = {i for at, n, _ in b["notes"]["sites"] for i in range(at, at + n)}
        self.assertEqual(set(diff(b["before"], b["rom"])) - declared, set())

    def test_only_the_four_literals_and_the_count_byte_change_in_the_base(self):
        b = built()
        base = sorted((at, n) for at, n, _ in b["notes"]["sites"] if at < 0x800000)
        self.assertEqual(base, [(ENTRY3_LITERAL, 4), (BASE_LITERALS[0], 4), (BASE_LITERALS[1], 4),
                                (COUNT_BYTE, 1), (BASE_LITERALS[2], 4)])

    def test_every_new_chunk_is_in_the_expansion_area(self):
        b = built()
        for at, n, name in b["notes"]["sites"]:
            if at >= 0x800000:
                self.assertTrue(EXPANSION[0] <= at and at + n <= EXPANSION[0] + EXPANSION[1], name)

    def test_the_rom_is_still_16_mb(self):
        self.assertEqual(len(built()["rom"]), log2_build.ROM_SIZE)


# ===== the doors: the owner's "block off all the transition points" =====

class DoorTests(unittest.TestCase):
    """His call on 2026-11-06: "the goal was to block off all the transition points, not the area".
    A map carries doors in TWO places. The empty region list removes map 6,1's own 2 warps, 2 scripts
    and scene. The layout's +0x40 count and +0x44 list carry 3 more, including the Capsule Corp front
    door to map 6,2. The arena inherited those by copying the layout pointer, so the copy zeroes them."""

    def layout_copy(self):
        b = built()
        return b, b["rom"][b["notes"]["layout"]:b["notes"]["layout"] + LAYOUT_SIZE]

    def test_the_arena_carries_no_door_in_either_carrier(self):
        b = built()
        e = entry(b["rom"], b["notes"]["table"], ARENA_INDEX)
        self.assertEqual((e[3], u32(e, 0x10)), (0, 0), "the entry's region list")
        mine = b["rom"][b["notes"]["layout"]:b["notes"]["layout"] + LAYOUT_SIZE]
        self.assertEqual(u32(mine, L_WARP_COUNT), 0, "the layout's door count")
        self.assertEqual(u32(mine, L_WARP_LIST), 0, "the layout's door list")

    def test_the_copy_differs_from_map_6_1_s_layout_only_at_six_words(self):
        """The layout also carries the tiles, the palettes and the art, so a wrong word blanks the map.
        +0x40 and +0x44 kill the doors, +0x24 and +0x28 name the arena's own three prop list, and
        +0x34 and +0x1C its own collision and BG2. The prop SHEET at +0x2C is shared and unchanged."""
        b, mine = self.layout_copy()
        theirs = b["rom"][SOURCE_LAYOUT:SOURCE_LAYOUT + LAYOUT_SIZE]
        self.assertEqual(len(mine), LAYOUT_SIZE)
        changed = [off for off in range(0, LAYOUT_SIZE, 4) if u32(mine, off) != u32(theirs, off)]
        self.assertEqual(changed, [L_BG2, L_PROP_COUNT, L_PROP_LIST, L_COLLISION,
                                   L_WARP_COUNT, L_WARP_LIST])
        self.assertEqual(u32(mine, L_PROP_COUNT), len(ARENA_PROPS))
        self.assertEqual(u32(mine, L_PROP_LIST), b["notes"]["props"] + ROM_BASE)
        self.assertEqual(u32(mine, 0x2C), u32(theirs, 0x2C), "the prop sheet is shared")
        for off in (L_WARP_COUNT, L_WARP_LIST):
            self.assertEqual(u32(mine, off), 0)
            self.assertNotEqual(u32(theirs, off), 0)
        self.assertEqual(u32(mine, L_COLLISION), b["notes"]["collision"] + ROM_BASE)
        self.assertEqual(u32(mine, L_BG2), b["notes"]["bg2"] + ROM_BASE)

    def test_map_6_1_keeps_all_three_of_its_own_doors(self):
        b = built()
        self.assertEqual(u32(b["rom"], SOURCE_LAYOUT + L_WARP_COUNT), SOURCE_WARPS)
        self.assertEqual(u32(b["rom"], SOURCE_LAYOUT + L_WARP_LIST), SOURCE_WARP_LIST + ROM_BASE)

    def test_the_door_list_is_a_list_of_pointers_and_the_third_is_the_front_door(self):
        """layout +0x44 names a list of POINTERS, not inline 0x18 byte records. Read inline, the records
        land on the pointer list itself and decode as garbage. The rect is what fix 2 reasons from."""
        b = built()
        third = u32(b["rom"], SOURCE_WARP_LIST + 4 * 2)
        self.assertEqual(third, SOURCE_DOOR + ROM_BASE)
        self.assertEqual(struct.unpack_from("<4h", b["rom"], SOURCE_DOOR + 8), SOURCE_DOOR_RECT)
        self.assertEqual((SOURCE_DOOR_RECT[0] // 8, SOURCE_DOOR_RECT[2] // 8), (INSIDE_BAND[0], 34),
                         "the rect stops at cell 34, so cell 35 needs closing too")

    def test_an_empty_door_pair_is_a_shape_the_vanilla_game_already_ships(self):
        """Map 14,3, the Cell Games arena, is the game's own sealed arena: no region and no door.
        Without this the zeroed pair would be a shape no vanilla map proves."""
        b = built()
        at = next(MAPS + MAP_SIZE * m for m in range(MAP_COUNT)
                  if (b["before"][MAPS + MAP_SIZE * m], b["before"][MAPS + MAP_SIZE * m + 1]) == SEALED_MAP)
        layout = u32(b["before"], u32(b["before"], at + 0x2C) - ROM_BASE) - ROM_BASE
        self.assertEqual(b["before"][at + 3], 0, "map 14,3 has no region")
        self.assertEqual(u32(b["before"], layout + L_WARP_COUNT), 0, "map 14,3 has no door count")
        self.assertEqual(u32(b["before"], layout + L_WARP_LIST), 0, "map 14,3 has no door list")


# ===== the glass door: the owner's "he walks into the building" =====

class CollisionTests(unittest.TestCase):
    """His call on 2026-11-06: "the glass door has no collision, so he walks into the building". v3 killed
    the warps, which is what used to gate the doorway, and the floor under it was open. The arena gets its
    own copy of map 6,1's frame with the two interior rows closed and no other cell touched."""

    def arena(self):
        b = built()
        return b, collision_bits(b["rom"], b["notes"]["layout"])

    def test_the_arena_has_its_own_frame_of_the_right_shape(self):
        b, bits = self.arena()
        self.assertEqual(u32(b["rom"], b["notes"]["layout"] + L_COLLISION), b["notes"]["collision"] + ROM_BASE)
        self.assertNotEqual(b["notes"]["collision"], SOURCE_FRAME)
        kind, size, _bits, _packed = unpack_frame(b["rom"], b["notes"]["collision"])
        self.assertEqual((kind, size), (1, FRAME_SIZE), "map 6,1's own frame is type 1, size 0x2000")
        self.assertEqual(len(bits), FRAME_SIZE)

    def test_exactly_the_building_recess_closes_and_the_map_post_foot_opens(self):
        b, bits = self.arena()
        theirs = frame(b["rom"], SOURCE_FRAME + ROM_BASE)
        differ = {(cx, cy) for cy in range(MAP_CELLS) for cx in range(MAP_CELLS)
                  if is_open(bits, cx, cy) != is_open(theirs, cx, cy)}
        self.assertEqual(differ, band_cells(INSIDE_BAND) | {POST_FOOT})
        self.assertEqual(set(b["notes"]["closed_cells"]), band_cells(INSIDE_BAND))
        self.assertEqual([tuple(c) for c in b["notes"]["opened_cells"]], [POST_FOOT])
        for cx, cy in band_cells(INSIDE_BAND):
            self.assertFalse(is_open(bits, cx, cy))
            self.assertTrue(is_open(theirs, cx, cy), "the band must have been open in map 6,1")
        self.assertTrue(is_open(bits, *POST_FOOT), "the map post's foot is open now")
        self.assertFalse(is_open(theirs, *POST_FOOT), "and it was the post's own block in map 6,1")

    def test_he_cannot_reach_the_inside_of_the_building_from_the_courtyard(self):
        """The test the brief asks for, as a walk, not as a cell list. His state 5 sat at (246,72)."""
        b, bits = self.arena()
        seen = reachable(bits, (TRUNKS_SPOT[0] // 8, TRUNKS_SPOT[1] // 8))
        inside = (INSIDE_PX[0] // 8, INSIDE_PX[1] // 8)
        self.assertFalse(is_open(bits, *inside))
        self.assertNotIn(inside, seen)
        for cell in band_cells(INSIDE_BAND):
            self.assertNotIn(cell, seen, f"cell {cell} is still inside the building")

    def test_the_doorway_row_he_stood_in_is_closed_flush_with_the_building_face(self):
        """v6 left row 11 open and he walked up into it and vanished behind the BG1 glass: "its like I
        run into a wall, but I can walk into it". His state 4 at (246,94) is cell (30,11), that row. The
        old reason for keeping it was map 6,2's return landing, and the arena has no way back from map
        6,2 at all, so the reason does not apply. The wall is now flush with the courtyard's first row."""
        b, bits = self.arena()
        front = (FRONT_PX[0] // 8, FRONT_PX[1] // 8)
        self.assertEqual(front[1], INSIDE_BAND[3], "his state 4 row is the row the band now closes")
        self.assertFalse(is_open(bits, *front))
        seen = reachable(bits, (TRUNKS_SPOT[0] // 8, TRUNKS_SPOT[1] // 8))
        self.assertNotIn(front, seen)
        for cx in range(INSIDE_BAND[0], INSIDE_BAND[2] + 1):
            self.assertTrue(is_open(bits, cx, FIRST_COURTYARD_ROW), "the courtyard row stays open")
            self.assertIn((cx, FIRST_COURTYARD_ROW), seen)

    def test_the_courtyard_keeps_every_cell_it_had(self):
        """His call was "Keep Capsule Corp, block nothing": the room itself loses nothing, and no cell
        goes from closed to open either."""
        b, bits = self.arena()
        theirs = frame(b["rom"], SOURCE_FRAME + ROM_BASE)
        opened = [(cx, cy) for cy in range(MAP_CELLS) for cx in range(MAP_CELLS)
                  if is_open(bits, cx, cy) and not is_open(theirs, cx, cy)]
        self.assertEqual(opened, [POST_FOOT], "only the map post's own block opens")
        start = (V3_SPOTS[1][0] // 8, V3_SPOTS[1][1] // 8)
        lost = reachable(theirs, start) - reachable(bits, start)
        self.assertEqual(lost, band_cells(INSIDE_BAND))
        self.assertEqual(len(lost), 24, "the 24 closed cells, and nothing stranded behind them")
        self.assertIn(POST_FOOT, reachable(bits, start) - reachable(theirs, start))

    def test_both_fighters_stand_on_an_open_cell(self):
        b, bits = self.arena()
        for name, spot in (("Cell", CELL_SPOT), ("Trunks", TRUNKS_SPOT)):
            self.assertTrue(is_open(bits, spot[0] // 8, spot[1] // 8), name)


# ===== the props: the owner's "why are the map post and save spots STILL THERE" =====

class PropTests(unittest.TestCase):
    """The map post and the save point are layout PROPS, and no list the arena emptied ever held them.
    v4 painted out their floor shadows and left the objects standing, which is what he saw on 2026-11-06:
    "why are the map post and save spots STILL THERE!??? I Thought we agreed to remove them, you only
    removed the shadows". The arena gets its own prop list of three: the glass door and the two pillars.
    Each prop was drawn from the sheet and named by eye in scripts\\one-time\\2026-11-06-arena-v7."""

    def test_map_6_1_still_carries_all_five_of_its_own_props(self):
        b = built()
        self.assertEqual(u32(b["rom"], SOURCE_LAYOUT + L_PROP_COUNT), SOURCE_PROPS)
        self.assertEqual(u32(b["rom"], SOURCE_LAYOUT + L_PROP_LIST), SOURCE_PROP_LIST + ROM_BASE)
        for k, rect in enumerate(SOURCE_PROP_RECTS):
            at = SOURCE_PROP_LIST + PROP_SIZE * k
            self.assertEqual(struct.unpack_from("<4I", b["rom"], at), rect, f"prop {k}")

    def test_the_arena_keeps_three_props_byte_for_byte_and_cuts_two(self):
        """The three that stay are COPIED, not rebuilt, so every attribute, tile number and priority
        comes across. Nothing the owner did not ask about is touched."""
        b = built()
        props = b["notes"]["props"]
        self.assertEqual(tuple(b["notes"]["prop_source"]), ARENA_PROPS)
        self.assertEqual(len(ARENA_PROPS) + len(CUT_PROPS), SOURCE_PROPS)
        for new, old in enumerate(ARENA_PROPS):
            got = b["rom"][props + PROP_SIZE * new:props + PROP_SIZE * (new + 1)]
            src = SOURCE_PROP_LIST + PROP_SIZE * old
            self.assertEqual(got, b["rom"][src:src + PROP_SIZE], f"arena prop {new} is map 6,1 prop {old}")
            self.assertEqual(struct.unpack_from("<4I", got, 0), SOURCE_PROP_RECTS[old])

    def test_the_map_post_and_the_save_point_are_the_two_that_go(self):
        """Each cut prop sits on the region the owner points at: prop 1 inside map 6,1's A press script
        region (225,193)-(272,248), prop 2 on its save point item region (408,568)-(457,617)."""
        b = built()
        props, kept = b["notes"]["props"], [SOURCE_PROP_RECTS[k] for k in ARENA_PROPS]
        now = [struct.unpack_from("<4I", b["rom"], props + PROP_SIZE * k)
               for k in range(len(ARENA_PROPS))]
        self.assertEqual(now, kept)
        for k in CUT_PROPS:
            self.assertNotIn(SOURCE_PROP_RECTS[k], now, f"prop {k} must be gone")
        post, save = SOURCE_PROP_RECTS[1], SOURCE_PROP_RECTS[2]
        self.assertTrue(225 <= post[0] and post[2] <= 272 and 193 <= post[1] and post[3] <= 248)
        self.assertTrue(save[0] <= 408 and 457 <= save[2] and save[1] <= 568 and 617 <= save[3])

    def test_no_cell_under_either_cut_prop_is_left_closed(self):
        """A prop that goes must take its collision with it, or the owner walks into an invisible
        block. Only the map post had one, a single cell at its foot."""
        b = built()
        bits = collision_bits(b["rom"], b["notes"]["layout"])
        for k in CUT_PROPS:
            x0, y0, x1, y1 = SOURCE_PROP_RECTS[k]
            shut = [(cx, cy) for cy in range(y0 // 8, (y1 + 7) // 8)
                    for cx in range(x0 // 8, (x1 + 7) // 8) if not is_open(bits, cx, cy)]
            self.assertEqual(shut, [], f"prop {k} leaves closed cells behind")
        theirs = frame(b["rom"], SOURCE_FRAME + ROM_BASE)
        self.assertFalse(is_open(theirs, *POST_FOOT), "map 6,1 did block the map post's foot")


# ===== the drawn-in shadows: the owner's "so you can remove them" =====

class Bg2Tests(unittest.TestCase):
    """The save point and the map post went with the map's own lists, but their shadows are floor tiles.
    His call on 2026-11-06: "the shadows for both are drawn in ... so you can remove them". Each shadow
    tile's entry becomes the clean floor entry of its own row at its own tile x parity."""

    def arena_record(self):
        b = built()
        return b, b["notes"]["bg2"]

    def test_the_arena_has_its_own_bg2_record_and_shares_the_five_clean_blocks(self):
        b, record = self.arena_record()
        self.assertEqual(u32(b["rom"], b["notes"]["layout"] + L_BG2), record + ROM_BASE)
        self.assertNotEqual(record, SOURCE_BG2)
        self.assertEqual((b["rom"][record + 0x14], b["rom"][record + 0x15]), BG2_GRID)
        self.assertEqual(sorted(b["notes"]["bg2_blocks"]), list(COPIED_BLOCKS))
        for k in range(BG2_GRID[0] * BG2_GRID[1]):
            mine = u32(b["rom"], record + BG2_PTRS + 4 * k)
            theirs = u32(b["rom"], SOURCE_BG2 + BG2_PTRS + 4 * k)
            if k in COPIED_BLOCKS:
                self.assertEqual(mine, b["notes"]["bg2_blocks"][k] + ROM_BASE, f"block {k}")
                self.assertNotEqual(mine, theirs, f"block {k}")
            else:
                self.assertEqual(mine, theirs, f"block {k} is a read only frame, so it is shared")

    def test_the_record_copy_differs_only_at_the_three_block_pointers(self):
        b, record = self.arena_record()
        changed = [off for off in range(0, BG2_SIZE, 4)
                   if u32(b["rom"], record + off) != u32(b["rom"], SOURCE_BG2 + off)]
        self.assertEqual(changed, [BG2_PTRS + 4 * k for k in COPIED_BLOCKS])

    def test_the_record_is_0x38_bytes_because_bg3_s_first_frame_starts_there(self):
        """Without this the copy length is a guess, and a short copy loses the last block pointers."""
        b = built()
        bg3 = u32(b["rom"], SOURCE_LAYOUT + 0x20)
        self.assertEqual(u32(b["rom"], bg3 - ROM_BASE + BG2_PTRS), SOURCE_BG2 + BG2_SIZE + ROM_BASE)

    def test_exactly_the_shadow_tiles_change_and_each_one_keeps_its_row_and_parity(self):
        b, record = self.arena_record()
        mine, theirs = layer_entries(b["rom"], record), layer_entries(b["rom"], SOURCE_BG2)
        changed = {c for c in theirs if mine[c] != theirs[c]}
        self.assertEqual(len(changed), SHADOW_TILES)
        self.assertEqual(sorted(changed), [tuple(c) for c in b["notes"]["shadow_tiles"]])
        boxes = {(tx, ty) for tx0, ty0, tx1, ty1 in SHADOW_BOXES
                 for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)}
        self.assertTrue(changed <= boxes, "a tile outside the two boxes changed")
        for tx, ty in changed:
            twins = [nx for nx in range(BG2_GRID[0] * BLOCK_TILES)
                     if nx % 2 == tx % 2 and (nx, ty) not in changed and theirs[(nx, ty)] == mine[(tx, ty)]]
            self.assertTrue(twins, f"tile ({tx},{ty}) took an entry no clean tile of its row carries")

    def test_no_shadow_pixel_is_left_in_either_box(self):
        """The owner's own test, by pixel, rendered from the BUILT record and not from the entry list."""
        b, record = self.arena_record()
        tiles = tile_pixels(b["rom"], b["notes"]["layout"])
        mine = layer_pixels(b["rom"], record, tiles)
        theirs = layer_pixels(b["rom"], SOURCE_BG2, tiles)
        for ((x0, y0), (x1, y1)), before in zip(SHADOW_BOXES_PX, SHADOW_PX_BEFORE):
            box = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]
            self.assertEqual(sum(1 for p in box if theirs.get(p) == SHADOW_INDEX), before,
                             "map 6,1 must still carry the shadow the owner counted")
            self.assertEqual(sum(1 for p in box if mine.get(p) == SHADOW_INDEX), 0)

    def test_the_arena_draws_the_same_pixel_count_and_changes_nothing_outside_the_boxes(self):
        """Index 73 is used by 270 BG2 tiles across the whole map, so a zero count in the boxes is not a
        whole-layer claim. This one is: every pixel the arena draws differently lies inside a shadow box."""
        b, record = self.arena_record()
        tiles = tile_pixels(b["rom"], b["notes"]["layout"])
        mine = layer_pixels(b["rom"], record, tiles)
        theirs = layer_pixels(b["rom"], SOURCE_BG2, tiles)
        self.assertEqual(len(mine), len(theirs), "no tile became transparent")
        boxes = {(x, y) for tx0, ty0, tx1, ty1 in SHADOW_BOXES
                 for y in range(ty0 * 8, ty1 * 8 + 8) for x in range(tx0 * 8, tx1 * 8 + 8)}
        differ = {p for p in set(mine) | set(theirs) if mine.get(p) != theirs.get(p)}
        self.assertTrue(differ <= boxes)
        self.assertGreater(len(differ), sum(SHADOW_PX_BEFORE),
                           "a swapped tile also moves its own floor dither, so more than the shadow moves")


# ===== map 6,1 is never edited =====

class SourceMapTests(unittest.TestCase):
    """The hard rule: the arena COPIES, it never edits a real map. His call was "Keep Capsule Corp",
    so map 6,1 must come out of the build byte for byte, art included."""

    def test_map_6_1_s_whole_layout_chain_stays_vanilla(self):
        """Entry, list, struct, the whole collision frame, the BG2 record and the three copied blocks."""
        b = built()
        sources = [("entry 145", SOURCE_AT, MAP_SIZE),
                   ("the layout list", SOURCE_LAYOUTS, 4),
                   ("the layout struct", SOURCE_LAYOUT, LAYOUT_SIZE),
                   ("the collision frame header", SOURCE_FRAME, 8),
                   ("the BG2 record", SOURCE_BG2, BG2_SIZE)]
        for off, length, what in [(s[1], s[2], s[0]) for s in sources]:
            self.assertEqual(b["rom"][off:off + length], b["before"][off:off + length], what)
        self.assertEqual(unpack_frame(b["rom"], SOURCE_FRAME)[0], 1, "map 6,1's frame is still type 1")
        self.assertEqual(frame(b["rom"], SOURCE_FRAME + ROM_BASE),
                         frame(b["before"], SOURCE_FRAME + ROM_BASE), "all 0x2000 collision bytes")
        for k in COPIED_BLOCKS:
            at = u32(b["before"], SOURCE_BG2 + BG2_PTRS + 4 * k) - ROM_BASE
            length = 8 + unpack_frame(b["before"], at)[3]
            self.assertEqual(b["rom"][at:at + length], b["before"][at:at + length], f"BG2 block {k}")
        self.assertEqual(entry(b["rom"], b["notes"]["table"], 145),
                         b["before"][SOURCE_AT:SOURCE_AT + MAP_SIZE])

    def test_a_changed_layout_chain_refuses_before_writing(self):
        """The copy reads map 6,1's layout and its art, so a changed link must stop the build.
        A changed art STREAM must stop it too, which is why each frame is pinned by its decoded SHA-1."""
        b = built()
        blocks = [u32(b["before"], SOURCE_BG2 + BG2_PTRS + 4 * k) - ROM_BASE for k in COPIED_BLOCKS]
        for off in [SOURCE_LAYOUTS, SOURCE_LAYOUT + L_COLLISION, SOURCE_LAYOUT + L_BG2,
                    SOURCE_LAYOUT + L_WARP_COUNT, SOURCE_LAYOUT + L_WARP_LIST,
                    SOURCE_WARP_LIST + 8, SOURCE_FRAME + 12] + [at + 12 for at in blocks]:
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                battle_arena.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap, f"rom:0x{off:X} wrote before it refused")


if __name__ == "__main__":
    unittest.main()
