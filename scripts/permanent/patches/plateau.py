r"""
plateau.py - Trial patch: map 7,100, the OWNER'S OWN plateau map, and the ending's round 2 on it.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt --out <new .gba>
Input:   the ROM after build_list_trial_future.txt (dev r41, battle_arena, ending_fight, future_androids),
         and art\plateau\map_142.json, the repo copy of the map the owner composed in the map editor.
         It must run LAST of the four: it appends to the map table a THIRD time, and it reads the live
         table base from the literal rom:0xEBD8 and the live count from rom:0xE0AE. Its six base-ROM
         writes are the 5 table hand-offs and ending table word 23. Everything else it changes, table D
         word 0 and the android copies of the ending table, is in the expansion area.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["plateau"], every write as
         (offset, length, name) in its "sites". `document()` returns the map document the patch lays,
         so a render, a test and the ROM can never drift apart.

THE MAP IS THE OWNER'S. He composed map 7,100 in the editor and saved it as "map 142" on 2026-11-08.
         Nothing here authors a tile, a collision bit, a layer priority or a camera bound.
         1. THE SOURCE IS A REPO COPY, art\plateau\map_142.json, byte for byte his saved file. The
            build never reads scripts\permanent\map-editor\maps\, which is his LIVE folder: a build has
            to be reproducible, and his next edit may not change a ROM behind our back.
         2. map-editor\import_map.py LAYS IT, so this project keeps ONE map importer and this is not a
            second one. Its round trip is proved on 334 of 336 vanilla layouts. It writes the four BG
            layer records, one frame per DISTINCT block, the collision and terrain frames, the tile
            stream, the animated tile groups, the 0x50 byte layout and the appended map table.
         3. THE CAMERA IS COMPUTED FROM HIS WORLD, never from the block grid. His grid is 5 x 4 blocks,
            1280 x 1024 px, and his world is 864 x 816 px, so the layout pair is (625, 657). A pair
            taken from the grid is the fault that stopped the camera 170 px short of walkable ground.
            import_map.layout_struct computes it; this module reads it back and checks it.
         4. HIS LAYER PRIORITIES ARE KEPT. BG0 and BG1 are priority 1 here, so they draw OVER the
            player, and BG2 and BG3 are priority 3 and draw behind him. Measured on the document
            2026-11-08, counting a cell as drawing only when its tile holds a non-zero pixel and
            shifting each layer by its own scroll offset: BG0 draws NO cell anywhere, and BG1 draws
            1100 cells, 477 of them over reachable walkable ground in 11 clusters. So the player walks
            BEHIND scenery in those places, which is what a priority 1 layer is for.
         5. HIS COLLISION IS KEPT. 4987 cells are open, 4848 of them reachable from Cell's own cell,
            and one sealed pocket of 139 cells sits inside the rock ring, cell origins px (488,536) to
            (616,608). No open cell touches the world edge. Both fight spots stand on reachable open
            ground, which this module proves before it writes a byte.
         6. THE ENTRY IS THE LIVE 6,100 ENTRY with three words changed: +0x00 to zone 7, +0x14 to the
            plateau's OWN two item list, and +0x2C to the layout array import_map wrote. It carries
            combat 1, banner 0xDD, music 38 and 0 regions. import_map builds the same 56 bytes from
            zeros, and this module overwrites them with the arena's own, so the two have to agree.
         7. THE ROUND SPLIT (rung 5, the owner 2026-11-07 and 2026-11-08). The Cell fight is ONE fight
            in TWO ROUNDS, and the plateau is round 2's ground, not the whole fight's. His words:
            "Cell: Trunks starts NOT Super Saiyan / half way: white flash + ping -> cutscene, Cell
            punched off screen, Trunks flies after him" and "then half way we do the scene where he
            punches cell of screen and trunks flies after him which takes him to our placeholder
            plateue". Record A is NOT touched any more: the talk and round 1 stay on the arena,
            map 6,100, which he play tested and approved.
        7a. Round 1 is record R, ending table word 23, in place of ending_fight's own record F:
            `ext 104 (28, 1) ; ext 90 (28, 50, 100) ; ext 86 (1) ; ext 33 (0)`. The only change from F
            is the bar: `ext 85` draws the whole bar and `ext 90` draws one display SEGMENT of it.
        7b. The boundary is record S, word 0 of the table battle_arena's enemy names, so it runs when
            round 1's Cell reaches HP 0. Its head is celljr_fight's own relay head, which the owner has
            play tested: sound 60, the white flash pair, a hold. The staging, the punch and the fly
            follow, then the plateau loads and round 2 arms. See split().
        7c. Round 2 is the SAME bar, bottom half, and Cell RE-ARMED by `ext 104`, which is vanilla's own
            multi-round wiring (bible B0832). It needs its own death event, or Cell's death on the
            plateau would run the split again and the fight would never end, so the plateau carries its
            OWN item list: an NPC Cell on the fight spot and an enemy Cell whose event struct names
            table D2. D2 is the live 27 word table with word 0 left at ending_fight's record K, the
            collapse, the vanilla blast and the vanilla tail. Vanilla does the same: Perfect Cell's two
            rounds are two different items with two different death tables (B0981).
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla map entry,
         item, layout, layer record or tile is written. The ONE base overlap with the earlier modules is
         the 4 map table literals and the count byte, which is how each relocation hands the table on.
         This module writes ONE base word of its own, ending table word 23, and ONE word inside
         ending_fight's own table D. Both are declared hand-offs. Record A is left alone.
"""
import hashlib
import struct
import sys
from pathlib import Path

import log_paths
from rom.webfoot_decompress import unpack_frame
from scene.scene_lib import (battle_start, call, code, ext, fade_in, fade_out, record_end, wait,
                             walk_to, words_naming)

# map-editor\ carries a hyphen, so it is not an importable package: its folder goes on sys.path, the
# way scripts\permanent\tests\test_import_map.py already reaches it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import import_map                                                       # noqa: E402
import map_file                                                         # noqa: E402

# ===== constants: the map table, read LIVE =====
ROM_BASE = 0x08000000
MAP_SIZE = 56
MAP_BASE_LITERAL, MAP_COUNT_BYTE = 0xEBD8, 0xE0AE
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)
ENTRY3, ENTRY3_LITERAL = 3, 0x195C
COUNT_FN = 0xE0AC
COUNT_CODE_HEAD, COUNT_CODE_TAIL = bytes.fromhex("ff20"), bytes.fromhex("307047")
MAP_COUNT_CAP = 0xFF + 0xFE

F_ZONE, F_AREA, F_VARIATIONS, F_REGION_COUNT, F_ITEM_COUNT = 0, 1, 2, 3, 4
F_COMBAT, F_BANNER, F_REGIONS, F_ITEMS = 8, 0x0C, 0x10, 0x14
F_MARKERS, F_MUSIC, F_LAYOUTS, F_ENTER, F_LEAVE = 0x20, 0x24, 0x2C, 0x30, 0x34

L_CLAMP, L_ANIM_COUNT, L_ANIM_LIST = 0x08, 0x0C, 0x10
L_BG0, L_BG1, L_BG2, L_BG3 = 0x14, 0x18, 0x1C, 0x20
L_PROP_COUNT, L_PROP_LIST, L_COLLISION, L_TERRAIN = 0x24, 0x28, 0x34, 0x38
L_WARP_COUNT, L_WARP_LIST, L_TILE_STREAM, L_TILE_TABLE = 0x40, 0x44, 0x48, 0x4C

LAYER_CLASS = 0x080056A1
LAYER_GRID = 0x14
BLOCK_TILES = 32

# ===== constants: the owner's map =====
PLATEAU_ZONE, PLATEAU_AREA, PLATEAU_VARIATIONS = 7, 100, 1      # zone 7 uses areas 1..26
MAP_DOC = log_paths.ART / "plateau" / "map_142.json"            # his "map 142", copied byte for byte
VIEW = (240, 160)

# bible B0246: set 28 reaches 20 px left, 44 right, 56 up and 8 down of its own point.
ENVELOPE = (20, 44, 56, 8)

# The collision frame: 256 x 256 cells of 8 px, one BIT a cell, a SET bit OPEN (collision_test
# @0x08005D6C). The document carries the same 0x2000 bytes the ROM frame holds.
FRAME_STRIDE, FRAME_SIZE, FRAME_CELLS = 32, 0x2000, 256
NEAR4 = ((1, 0), (-1, 0), (0, 1), (0, -1))

# ===== constants: the modules this one composes on =====
ARENA = "battle_arena"
ENDING = "ending_fight"
FUTURE = "future_androids"
ARENA_ZONE, ARENA_AREA = 6, 100
ARENA_MUSIC, ARENA_BANNER, ARENA_ITEMS, ARENA_COMBAT = 38, 0xDD, 2, 1
MAP_VARIATION = 1
TRUNKS_START = (248, 624)
# Record A's own load, which rung 5 LEAVES ALONE: the talk and round 1 stay on the arena. The module
# still reads it, to prove that the record ending_fight placed is the record this module expects.
ARENA_LOAD = ext(39, ARENA_ZONE, ARENA_AREA, MAP_VARIATION, *TRUNKS_START)

# ===== constants: the round split (rung 5) =====
# The ending table and the two words this module writes into the chain. TABLE itself is vanilla and is
# never moved; only word 23 changes, from ending_fight's record F to this module's record R.
TABLE, TABLE_WORDS = 0x3B8140, 27
FIGHT_INDEX, END_INDEX = 23, 26
FIGHT_WORD = TABLE + 4 * FIGHT_INDEX
EVENT_RUNNER, EVENT_TABLE_AT = 0x080106B3, 4

# The two item shapes, as battle_arena reads them.
ITEM_SIZE, ITEM_TYPE, ITEM_AT, ITEM_EVENT, ITEM_TAIL = 0x20, 8, 0x0C, 0x14, 0x1C
NPC_ITEM_SIZE, N_AT, N_STEP_LIST = 0x18, 8, 0x14
NPC_INDEX, ENEMY_INDEX = 0, 1                   # the plateau list keeps battle_arena's own order

PLAYER, CELL_SET = 0, 28                        # set 0 is the player; 28 is IMPERFECT Cell, not 30
DOWN, UP = 0, 1                                 # ext 55 facings (celljr_fight and chapter_cards agree)
CELL_SPOT, TRUNKS_SPOT = (244, 504), (248, 568)  # battle_arena's own fight pair, 64 px apart

# The bar. ext 90 (set, lo, hi) is ONE DISPLAY SEGMENT of the 60 px boss bar: Sprite_NewSpan
# @0x080104C0 stores f(lo) at +0x15 as the segment start and f(hi) - f(lo) at +0x16 as its width.
# lo = 0 is not a new value: ext 85 bar_show @0x0800AB1A calls the SAME builder with r2 = 0 and
# r3 = 0x64, so (0, 100) IS the whole bar. So an even split is legal and reads as two true halves.
# Vanilla's own slices are uneven ((30,75,100), (30,50,75), (9,75,100), (9,50,75), (9,25,50)), but
# nothing in the handler prefers them. CONFIRMED, both handlers read.
ROUND1_BAR, ROUND2_BAR = (50, 100), (0, 50)

# Record S's head: celljr_fight's own relay head, which the owner play tested (bible B0898, B0938).
PING, PING_HOLD, SPLIT_FLASH = 60, 40, 10

# The punch, op for op celljr_fight's `_melee` with set 28 in place of set 31 (bible B0900). Set 28
# has anims 0-3, 5-10, 12, 18 and 19 (bible B0244), so it has state 2 (hurt) and state 12 (fly) and no anim 4 is
# asked for. Set 132 has 0-9, 11-14, 16-18 and 20, so the player has state 7 (attack) and state 12.
PUNCH_STATE, HIT_FRAME, HIT_SOUND, HURT_STATE, FLY_STATE = 7, 8, 34, 2, 12
KNOCK_N, FLY_N = 600, 500                       # celljr's own speeds for a knock-back and a flight
BEAT = 20                                       # frames between the punch, the flight and the fade

# THE PUNCH LANDS IN CLOSE (the owner, 2026-11-08: "trunks should walk to cell and punch him, not
# punch him a mile away"). The staging drops him on TRUNKS_SPOT, 64 px below Cell, so the punch used
# to fire across that whole gap. He now WALKS the last stretch, straight north, and punches from 24
# px below Cell's point. 24 px is celljr_fight's own melee gap, twice over: MIDDLE (432,392) to
# PUNCH_AT (456,392), and GOHAN_TELEPORTS_TO (456,344) to TELE_AT (456,368).
# `ext 53` BLOCKS on its own, so the punch waits for the walk and needs no group. BOTH handlers
# were opened for this: `sub_08009D4A` (ext 53) ends in `BL Queue_Append @0x0800E04C` with the same
# four instruction tail as `sub_08009FC4` (ext 57), the op this module already relies on to block,
# and Queue_Append appends the command and then runs `BL 0x0800DE20 ; BL 0x0801F2F4`, the frame
# loop, whenever the group flag word is 0. Its command tick is the shared mover `@0x0801090A`,
# which runs until the actor arrives (bible B0691, B0787). An `ext 63` group is what makes several
# moves run in PARALLEL, which is why celljr's arrivals use one and this does not.
# Walk, then punch, is also vanilla's own shape: table rom:0x3E6F30 seq 18 runs
# `ext 53 (29,176,192)` then `ext 57 (29,6)` (bible B0789).
# The walk is 40 px at ext 53's own 1 px a frame (bible B0691), so about 40 frames.
PUNCH_FROM = (248, 528)                         # 24 px below CELL_SPOT, on TRUNKS_SPOT's own column

# Where the punch throws him, and where Trunks follows. SPLIT_VIEW's top is 432, so an actor whose
# lowest pixel sits at 400 is wholly above the frame. Cell reaches 8 px BELOW his own point (bible
# B0246), so y 392 puts his feet at 400 and his head at 336: off the top of the view, which is the
# owner's "punched off screen". y 392 is also map 6,1 item 6's own row, so it is open ground.
PUNCHED_TO, FLIES_TO = (244, 392), (248, 392)

# The two parked views, each proved by arithmetic against bible B0246's envelopes, which are the same
# numbers plateau's own ENVELOPE carries: set 28 reaches 20 left, 44 right, 56 up and 8 down, and the
# Trunks sets 8, 24, 24 and 8. A view is 240 x 160 from its TOP LEFT (bible B0959, B0766).
#   Cell at (244,504)   -> x 224..288, y 448..512
#   Trunks at (248,568) -> x 240..272, y 544..576
#   the view (136,432)  -> x 136..376, y 432..592, which holds both whole, with 16 px over Cell's head
# ending_fight's own VIEW, (136,456,2), would cut 8 px off the top of Cell's tallest frames.
#
# THE SPEEDS ARE NOT THE SAME, and the reason is measured. `ext 31` BLOCKS until the move reports
# done, in distance/speed + 1 frames (bible B0766). Round 1 ends with the FOLLOW camera on the
# player, who may stand anywhere inside map 6,100's clamp (273, 553), so the pan to (136,432) can be
# about 180 px. At speed 2 that is roughly 90 frames of solid white, because the screen holds white
# between `ext 42` and `ext 43`. Speed 40 makes it about 5 frames, which the flash hides. celljr's
# record N parks vanilla seq 11's camera at speed 40 for the same reason.
# ARRIVE_VIEW keeps speed 2: the load has just centred the camera at (248 - 112, 568 - 76), which is
# (136, 492), so its pan is a known 60 px, about 31 frames, and it runs under a fade and not a flash.
SPLIT_VIEW, ARRIVE_VIEW = (136, 432, 40), (136, 432, 2)
TRUNKS_UP, TRUNKS_DOWN = 24, 8               # bible B0246: sets 132 and 133 reach 24 up, 8 down
TRUNKS_ENVELOPE = (8, 24, TRUNKS_UP, TRUNKS_DOWN)   # bible B0246, in ENVELOPE's own order

# The only two spots that stand on HIS map: round 2 opens with the pair already placed there.
# PUNCH_FROM and TRUNKS_START are ARENA spots and are proved against map 6,100's own collision
# frame, never against his. Checking an arena spot on his map would fail on a wall he meant to draw.
PLATEAU_SPOTS = ((CELL_SPOT, ENVELOPE, "Cell"), (TRUNKS_SPOT, TRUNKS_ENVELOPE, "Trunks"))
SPLIT_FADE, LOAD_SETTLE, ARRIVE_HOLD = 30, 120, 60

BATTLE_START_EXCEPTIONS = {
    "split": "the round boundary really does open a scene: it loads map 7,100 behind its own fade and "
             "arms round 2 there, which is the template shape rom:0x3E9384 and rule 6's exception",
}


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _frame(rom: bytes, address: int) -> bytes:
    return unpack_frame(rom, address - ROM_BASE)[2]


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


def map_table(rom: bytes) -> tuple:
    return _u32(rom, MAP_BASE_LITERAL) - ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]


def map_entry(rom: bytes, zone: int, area: int) -> tuple:
    table, count = map_table(rom)
    for k in range(count):
        at = table + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the live map table rom:0x{table:X} ({count} entries)")


# ===== the owner's document =====

def document() -> dict:
    """The owner's map 7,100, read from the REPO copy. His live editor folder is never opened."""
    return map_file.load(MAP_DOC)


def map_tiles(doc: dict) -> tuple:
    """(across, down) in 8 px cells of the document's BLOCK GRID, which is larger than its world."""
    return doc["blocks"][0] * BLOCK_TILES, doc["blocks"][1] * BLOCK_TILES


def open_cells(doc: dict) -> set:
    """Every walkable (cell x, cell y) of the document, inside its own block grid."""
    bits = doc["collision"]
    across, down = map_tiles(doc)
    return {(cx, cy) for cy in range(min(down, FRAME_CELLS))
            for cx in range(min(across, FRAME_CELLS))
            if bits[cy * FRAME_STRIDE + (cx >> 3)] >> (cx & 7) & 1}


def reachable(cells: set, seed: tuple) -> set:
    """The cells a walker reaches from one of them. His map holds one sealed pocket, by design."""
    out, stack = set(), [seed]
    while stack:
        c = stack.pop()
        if c in out or c not in cells:
            continue
        out.add(c)
        stack += [(c[0] + dx, c[1] + dy) for dx, dy in NEAR4]
    return out


def is_open(bits: bytes, cx: int, cy: int) -> bool:
    if not (0 <= cx < FRAME_CELLS and 0 <= cy < FRAME_CELLS):
        return False
    return bool(bits[cy * FRAME_STRIDE + (cx >> 3)] & (1 << (cx & 7)))


def envelope_cells(spot: tuple, env: tuple = ENVELOPE) -> list:
    left, right, up, down = env
    return [(cx, cy) for cy in range((spot[1] - up) // 8, (spot[1] + down) // 8 + 1)
            for cx in range((spot[0] - left) // 8, (spot[0] + right) // 8 + 1)]


def plateau_entry(arena: bytes, layouts_at: int, items_at: int) -> bytes:
    """The live map 6,100 entry with three words changed: the zone, the item list and the layout array.

    The item list must be the plateau's OWN. Sharing battle_arena's would share its enemy item, and an
    item carries its death event at +0x14, so round 2's Cell would die into round 1's death record and
    split again for ever."""
    out = bytearray(arena)
    out[F_ZONE] = PLATEAU_ZONE
    out[F_ITEMS:F_ITEMS + 4] = _word(items_at + ROM_BASE)
    out[F_LAYOUTS:F_LAYOUTS + 4] = _word(layouts_at + ROM_BASE)
    return bytes(out)


# ===== the round split (rung 5) =====

def round1(enemy_item: int) -> bytes:
    """R, ending table word 23: round 1 on the arena, with the TOP HALF of the boss bar.

    It is ending_fight's own record F with one op changed, `ext 85 bar_show` for `ext 90 bar_set`, so
    the talk still ends the way the owner approved: no fade, no map load, nobody placed, the HUD back
    and camera_follow(0) panning the view onto the player.

    The segment is (50, 100). See ROUND1_BAR for why lo and hi mean what they mean and why an even
    split is legal."""
    return code(END_INDEX, battle_start(enemy_set=CELL_SET, enemy_item=enemy_item,
                                        bar=CELL_SET, bar_range=ROUND1_BAR))


def split(enemy_item: int) -> bytes:
    """S, word 0 of the table battle_arena's enemy names: the round boundary.

    It runs when round 1's Cell reaches HP 0 on map 6,100. The owner's beat, 2026-11-07: "half way:
    white flash + ping -> cutscene, Cell punched off screen, Trunks flies after him", and his
    precedent, 2026-11-08: "yeah we did this for cell jr as well".

    1. THE HEAD IS CELLJR'S RELAY HEAD. `ext 88` drops the bar, `header_bit1(0)` drops the HUD, then
       sound 60, the `ext 42` / `ext 43` white flash pair and a 40 frame hold. Those are celljr's own
       DING, RELAY_FLASH and DING_HOLD, byte for byte, and he has play tested them three times
       (bible B0898, B0938). Vanilla's own hand-off, rom:0x3EC758 word 0 (B0748), opens the same way,
       `ext 46 (60)` then `ext 88` then a flash, so the two agree.
    2. THE STAGING HIDES UNDER THE WHITE. A beaten boss keeps the boss descriptor and stays standing
       wherever the fight left him, which is nowhere in particular, so the record puts the pair back
       on the fight spots before anyone sees them. The player goes to TRUNKS_SPOT facing up, the
       beaten enemy is removed and a plain NPC Cell is spawned on CELL_SPOT facing down, and `ext 31`
       parks the view on the pair. That `ext 52` plus `ext 51` swap is ending_fight's record K's own
       shape, and an NPC takes a scripted pose with no AI to argue with it.
    2a. HE WALKS THE LAST 40 PX, so the punch lands in close. The owner, 2026-11-08: "trunks should
       walk to cell and punch him, not punch him a mile away". `ext 53` to PUNCH_FROM, 24 px below
       Cell's own point, then `ext 55` to hold him facing up. The walk BLOCKS, so the punch cannot
       start early, and 24 px is celljr's own melee gap. See PUNCH_FROM.
    3. THE PUNCH IS CELLJR'S MELEE. `ext 63` ... `ext 64` runs the group in parallel: the player takes
       the attack state, the script waits to the hit frame, Cell takes the hit and its sound, turns to
       his attacker, drops into the hurt pose and is thrown to PUNCHED_TO, which is above the top of
       the parked view. LIKELY, not confirmed: celljr drove that group on an ENEMY object and this one
       drives an NPC. If the throw does not play, `ext 54 fly` is the fallback.
    4. TRUNKS FLIES AFTER HIM: `ext 121 (0, 12)` then `ext 136`, celljr's own "fly to C" pair, to the
       same row. The view is still parked, so both of them really do leave the frame.
    5. THE HAND-OFF IS B0748's SHAPE: a cover, the `ext 39` load, the settle, the facing, the camera
       park, the reveal. A death event that loads the next map is vanilla (Cell type 21's death event
       loads map 14,3, bible B0654). `ext 39`, never `ext 35`: only ext 38 and ext 39 reach
       `sub_0800C584` and build a player. The 120 frame settle is record A's own: a load does not
       finish inside its own op. `ext 31` is needed because the load centres the camera on the player
       at (x - 112, y - 76), which from TRUNKS_SPOT is (136, 492) and would cut Cell's head off.
    6. ROUND 2 ARMS LAST, with the standard battle start: `ext 104` re-arms Cell from the plateau's own
       enemy item, the bar shows the BOTTOM HALF, the HUD comes back and camera_follow(0) hands the
       view over. That re-arm is vanilla's own multi-round wiring (B0832).

    Next 26 = END, so the player gets control the moment the record finishes."""
    head = (ext(88) + call("header_bit1", 0)
            + call("sound", PING)
            + call("palette_fx", SPLIT_FLASH)
            + ext(62, PLAYER, *TRUNKS_SPOT) + ext(55, PLAYER, UP)
            + ext(52, CELL_SET) + ext(51, CELL_SET, *CELL_SPOT) + ext(55, CELL_SET, DOWN)
            + ext(31, *SPLIT_VIEW)
            + call("flash_wait", SPLIT_FLASH)
            + wait(PING_HOLD))
    close = walk_to(PLAYER, *PUNCH_FROM) + ext(55, PLAYER, UP)
    punch = (call("block_begin")
             + ext(57, PLAYER, PUNCH_STATE) + wait(HIT_FRAME) + ext(112, CELL_SET, HIT_SOUND)
             + ext(95, CELL_SET) + ext(121, CELL_SET, HURT_STATE)
             + ext(136, CELL_SET, *PUNCHED_TO, KNOCK_N)
             + call("block_end") + wait(BEAT))
    follow = ext(121, PLAYER, FLY_STATE) + ext(136, PLAYER, *FLIES_TO, FLY_N) + wait(BEAT)
    arrive = (fade_out(SPLIT_FADE)
              + call("load_map_at", PLATEAU_ZONE, PLATEAU_AREA, MAP_VARIATION, *TRUNKS_SPOT)
              + wait(LOAD_SETTLE)
              + ext(55, PLAYER, UP)
              + ext(31, *ARRIVE_VIEW)
              + fade_in(SPLIT_FADE)
              + wait(ARRIVE_HOLD))
    return code(END_INDEX, head, close, punch, follow, arrive,
                battle_start(enemy_set=CELL_SET, enemy_item=enemy_item,
                             bar=CELL_SET, bar_range=ROUND2_BAR))


def plateau_npc_item(arena_npc: bytes, step_at: int) -> bytes:
    """The plateau's NPC Imperfect Cell: battle_arena's own item, moved onto the fight spot.

    The arena builds its NPC on CELL_START and the vanilla talk walks him to CELL_SPOT. Nothing walks
    him here, because round 2 opens mid fight, so the item carries CELL_SPOT itself. Condition and set
    are battle_arena's, so the map load builds him and `ext 104` has an actor of set 28 to replace."""
    item = bytearray(arena_npc)
    item[N_AT:N_AT + 4] = struct.pack("<hh", *CELL_SPOT)
    item[N_STEP_LIST:N_STEP_LIST + 4] = _word(step_at + ROM_BASE)
    return bytes(item)


def plateau_enemy_item(arena_enemy: bytes, event_at: int, tail_at: int) -> bytes:
    """The plateau's enemy Imperfect Cell: battle_arena's own item with its OWN event struct.

    Everything else is carried, so round 2 is the same type 60 at HP 5210 with AI 80 and the boss
    descriptor. Only the death event differs, and that is the whole point: round 1's death splits the
    fight and round 2's ends it."""
    item = bytearray(arena_enemy)
    item[ITEM_AT:ITEM_AT + 4] = struct.pack("<hh", *CELL_SPOT)
    item[ITEM_EVENT:ITEM_EVENT + 4] = _word(event_at + ROM_BASE)
    item[ITEM_TAIL:ITEM_TAIL + 4] = _word(tail_at + ROM_BASE)
    return bytes(item)


# ===== checks =====

def _check_design(doc: dict) -> dict:
    """His map, measured where the fight stands on it. Nothing here changes a byte of his work.

    Returns the measurements the notes carry, so a check, a test and a report read the same numbers."""
    problems = map_file.validate(doc)
    if problems:
        raise ValueError(f"{MAP_DOC.name} is not a sound map document, so nothing was written:\n  "
                         + "\n  ".join(problems))
    world = tuple(doc["world"])
    clamp = map_file.camera_pair(*world)
    opened = open_cells(doc)
    if not opened:
        raise ValueError(f"{MAP_DOC.name} opens no cell at all, so nobody could stand on it")

    # One walkable REGION, not every open cell: his map seals a pocket inside the rock ring on
    # purpose, and both fighters have to be in the region the player can walk.
    seed = (CELL_SPOT[0] // 8, CELL_SPOT[1] // 8)
    if seed not in opened:
        raise ValueError(f"Cell's own cell {seed} is closed on {MAP_DOC.name}, so round 2 would open"
                         f" with him standing in a wall")
    reach = reachable(opened, seed)
    for spot, env, who in PLATEAU_SPOTS:
        for cx, cy in envelope_cells(spot, env):
            if (cx, cy) not in reach:
                raise ValueError(f"{who} at {spot} draws into ({cx},{cy}), which is closed or sealed"
                                 f" off on {MAP_DOC.name}")

    # The camera stops at the world edge, so walkable ground there would let him walk into nothing.
    edge = [c for c in opened if c[0] == 0 or c[1] == 0
            or (c[0] + 1) * 8 >= world[0] or (c[1] + 1) * 8 >= world[1]]
    if edge:
        raise ValueError(f"{len(edge)} walkable cells touch the {world[0]} x {world[1]} px world"
                         f" edge, for example {sorted(edge)[:4]}")

    # Both views the split parks have to be inside HIS camera bound, or the clamp moves them and the
    # pair is not framed where it was drawn. The load centres the view at (x - 112, y - 76).
    for view, where in ((ARRIVE_VIEW[:2], "the parked plateau view"),
                        ((TRUNKS_SPOT[0] - 112, TRUNKS_SPOT[1] - 76), "the view the load centres")):
        if not (0 <= view[0] <= clamp[0] and 0 <= view[1] <= clamp[1]):
            raise ValueError(f"{where} {view} is outside his camera bound {clamp}: the clamp would"
                             f" move it, so the pair would not be framed where the record puts them")

    # The rest is the SPLIT's own px arithmetic on map 6,100 and does not read his map at all.
    for spot, who, up, down in ((CELL_SPOT, "Cell", ENVELOPE[2], ENVELOPE[3]),
                                (TRUNKS_SPOT, "Trunks", TRUNKS_UP, TRUNKS_DOWN),
                                (PUNCH_FROM, "Trunks at the punch", TRUNKS_UP, TRUNKS_DOWN)):
        top, bottom = spot[1] - up, spot[1] + down
        for view, where in ((SPLIT_VIEW, "the arena view"), (ARRIVE_VIEW, "the plateau view")):
            if top < view[1] or bottom > view[1] + VIEW[1]:
                raise ValueError(f"{who} at {spot} draws {top}..{bottom}, outside {where} {view[:2]}"
                                 f" plus {VIEW[1]}: his frame would be cut")
    if PUNCHED_TO[1] + ENVELOPE[3] >= SPLIT_VIEW[1] or FLIES_TO[1] + TRUNKS_DOWN >= SPLIT_VIEW[1]:
        raise ValueError(f"the punch sends Cell to {PUNCHED_TO} and Trunks to {FLIES_TO}, which are"
                         f" not above the view top {SPLIT_VIEW[1]}: neither leaves the frame")
    # The walk is one axis and it closes the gap. Both are design, not taste: a diagonal walk would
    # leave him facing sideways, and a punch from further out is what the owner rejected.
    if PUNCH_FROM[0] != TRUNKS_SPOT[0]:
        raise ValueError(f"the walk from {TRUNKS_SPOT} to {PUNCH_FROM} is not straight north, so the"
                         f" mover would leave the player facing sideways at the punch")
    gap = PUNCH_FROM[1] - CELL_SPOT[1]
    if not 0 < gap <= TRUNKS_SPOT[1] - CELL_SPOT[1] - 8:
        raise ValueError(f"the punch fires from {gap} px below Cell, which is not closer than the"
                         f" staging spot {TRUNKS_SPOT} and still south of him")

    xs, ys = [c[0] for c in opened], [c[1] for c in opened]
    return {"world": world, "blocks": tuple(doc["blocks"]), "map_tiles": map_tiles(doc),
            "clamp": clamp, "open_cells": len(opened), "reachable": len(reach),
            "pocket_cells": len(opened) - len(reach),
            "open_box": (min(xs) * 8, min(ys) * 8, max(xs) * 8 + 7, max(ys) * 8 + 7),
            "priorities": {name: doc["layers"][name]["priority"] for name in sorted(doc["layers"])},
            "static_tiles": len(doc["tiles"]), "groups": len(doc.get("animated") or [])}


def _check(rom: bytearray, alloc) -> tuple:
    if "plateau" in alloc.notes:
        raise ValueError("plateau already ran")
    for name in (ARENA, ENDING):
        if name not in alloc.notes:
            raise ValueError(f"{name} has not run: the plateau composes on its notes")
    if not MAP_DOC.is_file():
        raise ValueError(f"{MAP_DOC} is missing: the plateau IS that document, and this module never"
                         f" reads his live map-editor\\maps folder")
    if PLATEAU_VARIATIONS != import_map.VARIATIONS:
        raise ValueError(f"this module says {PLATEAU_VARIATIONS} variation and import_map writes"
                         f" {import_map.VARIATIONS}: the entry and the layout array would disagree")

    table, count = map_table(rom)
    for lit in BASE_LITERALS:
        _expect(rom, lit, _word(table + ROM_BASE))
    _expect(rom, ENTRY3_LITERAL, _word(table + MAP_SIZE * ENTRY3 + ROM_BASE))
    if words_naming(rom, table) != list(BASE_LITERALS):
        raise ValueError(f"the live map table base is named by {words_naming(rom, table)}")
    _expect(rom, COUNT_FN, COUNT_CODE_HEAD)
    _expect(rom, MAP_COUNT_BYTE + 1, COUNT_CODE_TAIL)
    if count >= MAP_COUNT_CAP:
        raise ValueError(f"the live map count is {count}: the count byte cannot hold one more")
    pairs = [(rom[table + MAP_SIZE * k], rom[table + MAP_SIZE * k + 1]) for k in range(count)]
    if len(set(pairs)) != count:
        raise ValueError(f"(zone, area) is not unique across the {count} live map entries")
    if (PLATEAU_ZONE, PLATEAU_AREA) in pairs:
        raise ValueError(f"map {PLATEAU_ZONE},{PLATEAU_AREA} already exists")

    arena_index, arena_at = map_entry(rom, ARENA_ZONE, ARENA_AREA)
    arena = bytes(rom[arena_at:arena_at + MAP_SIZE])
    if arena[F_VARIATIONS] != PLATEAU_VARIATIONS or arena[F_REGION_COUNT] != 0 \
            or arena[F_ITEM_COUNT] != ARENA_ITEMS:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} carries {arena[F_VARIATIONS]} variations,"
                         f" {arena[F_REGION_COUNT]} regions and {arena[F_ITEM_COUNT]} items")
    for off, want, what in ((F_COMBAT, ARENA_COMBAT, "combat"), (F_BANNER, ARENA_BANNER, "the banner"),
                            (F_REGIONS, 0, "the region list"), (F_MUSIC, ARENA_MUSIC, "the music"),
                            (F_MARKERS, 0, "the marker list"), (F_ENTER, 0, "the enter script"),
                            (F_LEAVE, 0, "the leave script")):
        if _u32(arena, off) != want:
            raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} +0x{off:02X} ({what}) is"
                             f" 0x{_u32(arena, off):X}, expected 0x{want:X}")
    if _u32(arena, F_ITEMS) - ROM_BASE != alloc.notes[ARENA]["items"]:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} does not name battle_arena's own item list")

    # Record A keeps its ARENA load: rung 5 moved the plateau off word 13 and onto the round boundary.
    arrive = alloc.notes[ENDING]["arrive"]
    record = bytes(rom[arrive:record_end(rom, arrive)])
    if record.count(ARENA_LOAD) != 1:
        raise ValueError(f"record A rom:0x{arrive:X} holds {record.count(ARENA_LOAD)} copies of the"
                         f" arena load, expected exactly 1: round 1 must open on map"
                         f" {ARENA_ZONE},{ARENA_AREA}")

    # The three ending_fight parts this module re-wires, each checked where it stands today.
    fight, death, table_d = (alloc.notes[ENDING][k] for k in ("fight", "death", "table"))
    # EVERY word that names record F has to move, not just the ending table's own word 23.
    # future_androids gives each android enemy a COPY of the live ending table, so after a fight the
    # scene runs out of THAT copy and reads its word 23, not the ending table's. Repointing one word
    # would leave the whole-bar record F running whenever the player got to Cell through a fight.
    fight_words = [FIGHT_WORD] + [t + 4 * FIGHT_INDEX
                                  for t in sorted(alloc.notes.get(FUTURE, {}).get("tables", {}).values())]
    for word in fight_words:
        _expect(rom, word, _word(fight + ROM_BASE))
    # And nothing ELSE a module wrote may name record F, or a path would keep the one round record.
    # A vanilla address that happens to hold the same 4 bytes is data, not a table word, so only a
    # namer inside a module's own allocation is a finding.
    mine = set(fight_words)
    for word in words_naming(rom, fight):
        if word in mine:
            continue
        who = [name for name, (lo, n) in _written(alloc.notes) if lo <= word < lo + n]
        if who:
            raise ValueError(f"rom:0x{word:X} names ending_fight's record F and belongs to"
                             f" {who}: every namer has to move, so stop and report")
    event = alloc.notes[ARENA]["event"]
    _expect(rom, event, _word(EVENT_RUNNER))
    _expect(rom, event + EVENT_TABLE_AT, _word(table_d + ROM_BASE))
    _expect(rom, table_d, _word(death + ROM_BASE))
    if _u32(rom, alloc.notes[ARENA]["item"] + ITEM_EVENT) != event + ROM_BASE:
        raise ValueError(f"the arena enemy does not name event struct rom:0x{event:X}")
    if arena[F_ITEM_COUNT] != ARENA_ITEMS or ENEMY_INDEX >= ARENA_ITEMS:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} lists {arena[F_ITEM_COUNT]} items, so the"
                         f" enemy index {ENEMY_INDEX} the two battle starts name is out of range")
    theirs = alloc.notes[ARENA]
    if (theirs["npc_item_index"], theirs["item_index"]) != (NPC_INDEX, ENEMY_INDEX):
        raise ValueError(f"battle_arena orders its items {theirs['npc_item_index']} NPC and"
                         f" {theirs['item_index']} enemy: the plateau list copies that order, so the"
                         f" two must agree or ext 104 would name the wrong item")
    if (theirs["cell_set"], tuple(theirs["cell_spot"]), tuple(theirs["trunks_spot"])) \
            != (CELL_SET, CELL_SPOT, TRUNKS_SPOT):
        raise ValueError(f"the fight pair here is set {CELL_SET} at {CELL_SPOT} and {TRUNKS_SPOT},"
                         f" and battle_arena has set {theirs['cell_set']} at"
                         f" {theirs['cell_spot']} and {theirs['trunks_spot']}")
    # Round 2 must fight the SAME Cell as round 1. The plateau's enemy item is a copy of the arena's,
    # taken live, so it inherits ending_fight's weaker future type; this proves the type is there to
    # inherit and is not vanilla's type 60, which the main game's own Cell still carries.
    weak_cell = alloc.notes[ENDING].get("cell_type")
    live_cell = _u32(rom, theirs["item"] + ITEM_TYPE)
    if weak_cell is None or live_cell != weak_cell:
        raise ValueError(f"the arena enemy is type {live_cell} and ending_fight's weaker future Cell"
                         f" is type {weak_cell}: round 1 and round 2 would not fight the same enemy")
    # The two spots round 2 opens on are the ones _check_design proves against HIS collision.
    # PUNCH_FROM and TRUNKS_START are ARENA spots and are proved against map 6,100's own frame below.
    if {CELL_SPOT, TRUNKS_SPOT} != {spot for spot, _env, _who in PLATEAU_SPOTS}:
        raise ValueError(f"PLATEAU_SPOTS is {[s for s, _e, _w in PLATEAU_SPOTS]}, and round 2 opens"
                         f" with Cell at {CELL_SPOT} and Trunks at {TRUNKS_SPOT}")
    # THE PUNCH HAPPENS ON THE ARENA, so the walk needs open ground on map 6,100 and not on the
    # plateau. _check_design proves his map; this proves the arena, out of its own live frame.
    arena_layout = _u32(rom, _u32(arena, F_LAYOUTS) - ROM_BASE) - ROM_BASE
    arena_bits = _frame(rom, _u32(rom, arena_layout + L_COLLISION))
    walk = [(TRUNKS_SPOT[0], y) for y in range(PUNCH_FROM[1], TRUNKS_SPOT[1] + 1, 8)]
    for spot in walk + [PUNCH_FROM]:
        for cx, cy in envelope_cells(spot, TRUNKS_ENVELOPE):
            if not is_open(arena_bits, cx, cy):
                raise ValueError(f"on map {ARENA_ZONE},{ARENA_AREA} the walk to {PUNCH_FROM} draws"
                                 f" {spot} into the closed cell ({cx},{cy})")

    for name, (start, size) in _written(alloc.notes):
        if start < COUNT_FN + 2 and COUNT_FN < start + size:
            raise ValueError(f"the map count getter rom:0x{COUNT_FN:X} is also written by {name}:"
                             f" stop and report")
    return table, count, arena, arena_index, fight_words


def _check_overlaps(notes: dict, sites: list, table_d: int, fight_words: list) -> None:
    """Every write of this module that lands on an earlier module's bytes is a DECLARED hand-off.

    There are three kinds: the map table literals and the count byte, which is how each relocation
    hands the table on; ending table word 23, which moves from ending_fight's record F to record R;
    and word 0 of ending_fight's table D, which moves from record K to record S. Record A is NOT
    here any more, because rung 5 leaves it loading the arena."""
    expected = {(lit, 4) for lit in BASE_LITERALS} \
        | {(ENTRY3_LITERAL, 4), (MAP_COUNT_BYTE, 1), (table_d, 4)} \
        | {(word, 4) for word in fight_words}
    for start, size, what in sites:
        for name, (lo, n) in _written(notes):
            if start >= lo + n or lo >= start + size:
                continue
            if (start, size) not in expected:
                raise ValueError(f"this module's write of {what} at rom:0x{start:X} lands on {name}'s"
                                 f" rom:0x{lo:X}, which is not one of the expected hand-offs")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    table, count, arena, arena_index, fight_words = _check(rom, alloc)
    doc = document()
    design = _check_design(doc)
    sites = []

    def place(data: bytes, name: str) -> int:
        at = alloc.alloc(len(data))
        if set(rom[at:at + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{len(data):X} bytes) is not free")
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))
        return at

    def put(at: int, data: bytes, name: str) -> None:
        rom[at:at + len(data)] = data
        sites.append((at, len(data), name))

    # Round 2's own actors and its own death event. The plateau may not share battle_arena's item
    # list: an item carries its death table at +0x14, and round 1 and round 2 must end differently.
    arena_notes = alloc.notes[ARENA]
    ending = alloc.notes[ENDING]
    table_d = ending["table"]
    step = place(bytes(rom[arena_notes["npc_step"]:arena_notes["npc_step"] + 8]),
                 "the plateau NPC Cell's stand step")
    tail = place(bytes(rom[arena_notes["tail"]:arena_notes["tail"] + 8]),
                 "the plateau enemy's step struct")
    table_d2 = place(bytes(rom[table_d:table_d + 4 * TABLE_WORDS]),
                     f"table D2 (round 2's death event: the live {TABLE_WORDS} word table, word 0 left"
                     f" at ending_fight's record K)")
    event2 = place(_word(EVENT_RUNNER) + _word(table_d2 + ROM_BASE),
                   "the plateau enemy's event struct (table D2, so round 2's death ends the ending)")
    npc = place(plateau_npc_item(bytes(rom[arena_notes["npc_item"]:
                                           arena_notes["npc_item"] + NPC_ITEM_SIZE]), step),
                f"the plateau NPC Cell (set {CELL_SET}, cond 0, on {CELL_SPOT})")
    enemy = place(plateau_enemy_item(bytes(rom[arena_notes["item"]:
                                               arena_notes["item"] + ITEM_SIZE]), event2, tail),
                  "the plateau enemy (Imperfect Cell, cond 1, its OWN death event)")
    items = place(_word(npc + ROM_BASE) + _word(enemy + ROM_BASE),
                  f"the plateau item list ({ARENA_ITEMS} items: the NPC, then the enemy)")

    rnd1 = place(round1(ENEMY_INDEX), "record R (round 1 on the arena, the TOP half of the bar)")
    boundary = place(split(ENEMY_INDEX),
                     "record S (ping, flash, Cell punched off screen, Trunks flies after him, the"
                     " plateau loads and round 2 arms with the BOTTOM half of the bar)")

    # THE MAP IS HIS, and import_map lays it: the four BG layer records, one frame per DISTINCT
    # block, the collision and terrain frames, the tile stream, the animated tile groups, the 0x50
    # byte layout with the camera pair COMPUTED from his world, the appended map table and the five
    # table hand-offs. This module writes no tile and no collision bit of its own.
    rom[:] = import_map.apply(bytes(rom), doc, PLATEAU_ZONE, PLATEAU_AREA, music=ARENA_MUSIC,
                              banner=ARENA_BANNER, combat=ARENA_COMBAT, alloc=alloc.alloc,
                              sites=sites)

    new, new_count = map_table(rom)
    if new_count != count + 1:
        raise ValueError(f"the map table went from {count} to {new_count} entries, expected one more")
    entry_at = new + MAP_SIZE * count
    if (rom[entry_at], rom[entry_at + 1]) != (PLATEAU_ZONE, PLATEAU_AREA):
        raise ValueError(f"the appended entry rom:0x{entry_at:X} is map {rom[entry_at]},"
                         f"{rom[entry_at + 1]}, expected {PLATEAU_ZONE},{PLATEAU_AREA}")
    layouts = _u32(rom, entry_at + F_LAYOUTS) - ROM_BASE
    layout = _u32(rom, layouts) - ROM_BASE
    clamp = struct.unpack_from("<HH", rom, layout + L_CLAMP)
    if clamp != design["clamp"]:
        raise ValueError(f"the layout carries the camera pair {clamp}, and his"
                         f" {design['world'][0]} x {design['world'][1]} px world is"
                         f" {design['clamp']}: a pair that is not his world's is the fault that"
                         f" stopped the camera short of walkable ground")

    # The entry becomes the LIVE arena entry with three words changed, so map 7,100 keeps the arena's
    # combat, banner, music and 2 item list, and names its OWN items and the layout import_map wrote.
    put(entry_at, plateau_entry(arena, layouts, items),
        f"the map {PLATEAU_ZONE},{PLATEAU_AREA} entry (the live {ARENA_ZONE},{ARENA_AREA} entry with"
        f" the zone, the item list and the layout array changed)")

    for word in fight_words:
        where = ("the ending table" if word == FIGHT_WORD
                 else "an android's copy of the ending table")
        put(word, _word(rnd1 + ROM_BASE), f"{where} word {FIGHT_INDEX} (record R, round 1)")
    put(table_d, _word(boundary + ROM_BASE),
        "table D word 0 (record S: round 1's death is now the split, not the end of the fight)")
    _check_overlaps(alloc.notes, sites, table_d, fight_words)

    alloc.notes["plateau"] = {
        "table": new, "entry": entry_at, "entry_index": count,
        "old_table": table, "old_count": count, "arena_index": arena_index,
        "zone": PLATEAU_ZONE, "area": PLATEAU_AREA, "variation": PLATEAU_VARIATIONS,
        "doc": str(MAP_DOC), "doc_sha256": hashlib.sha256(MAP_DOC.read_bytes()).hexdigest(),
        "layout": layout, "layouts": layouts,
        "collision": _u32(rom, layout + L_COLLISION) - ROM_BASE,
        "terrain": _u32(rom, layout + L_TERRAIN) - ROM_BASE,
        "tile_stream": _u32(rom, layout + L_TILE_STREAM) - ROM_BASE,
        "chunk_table": _u32(rom, layout + L_TILE_TABLE),
        "bg0": _u32(rom, layout + L_BG0) - ROM_BASE, "bg1": _u32(rom, layout + L_BG1) - ROM_BASE,
        "bg2": _u32(rom, layout + L_BG2) - ROM_BASE, "bg3": _u32(rom, layout + L_BG3) - ROM_BASE,
        "grid": design["blocks"], "map_tiles": design["map_tiles"], "world": design["world"],
        "clamp": clamp, "priorities": design["priorities"],
        "static_tiles": design["static_tiles"], "groups": design["groups"],
        "open_cells": design["open_cells"], "reachable": design["reachable"],
        "pocket_cells": design["pocket_cells"], "open_box": design["open_box"],
        "items": items, "npc_item": npc, "item": enemy, "npc_step": step, "tail": tail,
        "npc_item_index": NPC_INDEX, "item_index": ENEMY_INDEX,
        "event": event2, "death_table": table_d2, "death_words": TABLE_WORDS,
        "round1": rnd1, "split": boundary, "arena_table": table_d,
        "fight_words": sorted(fight_words),
        "round1_bar": ROUND1_BAR, "round2_bar": ROUND2_BAR,
        "cell_spot": CELL_SPOT, "trunks_spot": TRUNKS_SPOT,
        "sites": sorted(sites)}
