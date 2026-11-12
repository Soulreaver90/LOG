r"""
battle_arena.py - Trial patch: a NEW map, 6,100, that is nothing but a battle arena for the ending fight.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_ending.txt --out <new .gba>
Input:   the ROM after build_list_dev.txt (r41). It must run AFTER every module that edits a map entry in
         place (chamber_spar edits 6,70) and BEFORE ending_fight, which fills in the arena enemy's death
         event. A module that writes a map entry after this one would write into the dead old table.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["battle_arena"], every write as
         (offset, length, name) in its "sites". arena_entry(), arena_props(), cell_npc_item(),
         cell_item() and the notes keys "event", "item_index", "zone", "area", "cell_start" and
         "trunks_start" are the interface ending_fight reads, so the design lives in one place.
Method:  The map table rom:0x409368 holds 327 entries of 56 bytes. The bytes after entry 326 are another
         table (rom:0x40DAF0, named by the literal rom:0xE1D0), not padding, so a 328th entry needs the
         whole table moved. Study: scripts\one-time\2026-11-05-ending-arena\01_probe.txt to 07_cell_event.txt.
         1. Copy all 327 entries, AS THEY ARE IN THIS BUILD, into the expansion area and append entry 327.
            The copy reads the live ROM, so an earlier module's edit of a map entry is carried over.
         2. Entry 327 is map 6,100: combat on, no regions, no NPCs, no markers, no enter or leave
            script, NO name banner, and the ending's own song (step 2c). The courtyard stays walkable, his
            call of 2026-11-06: "Keep Capsule Corp, block nothing". A collision bound was "a invisible wall"
            that "was too restrictive", so the arena's collision is map 6,1's own frame with ONE change:
            the two cell rows inside the building are closed (step 2d).
         2b. A map carries its doors in TWO places, and an empty region list only empties one of them.
            The arena's layout is therefore a copy of map 6,1's with the warp count +0x40 and the warp
            list +0x44 zeroed, and nothing else changed. Study: scripts\one-time\2026-11-06-arena-v3.
            Map 6,1's two carriers, read with scene_probe's own item decoder:
              entry +0x10, 6 regions: 2 warps on the west strip (0,176)-(9,481) to maps 6,20 and 6,22,
                plus 2 scripts and a scene. All of these the empty region list already removes.
              layout +0x44, 3 warps: (0,512)-(9,689) to map 4,6, (488,176)-(497,481) to map 6,21, and
                the Capsule Corp front door (224,88)-(273,105) to map 6,2 at (144,276).
            The west strip (0,512)-(9,689) overlaps the courtyard the fight stands in, so the player
            could walk off the map. Map 6,2's own layout warps straight back to map 6,1, not 6,100, so
            returning dropped him on the real town map with the fight gone: his "if you exit the area
            and go back, it breask everything". Map 14,3, the game's own sealed arena, carries +0x40 = 0
            and +0x44 = 0, and so do 18 vanilla entries, so an empty warp list is a vanilla shape.
         2c. The music word +0x24 names song 38, the song the ending itself started. The map load then
            finds that record already playing and never calls `music_play`, so the track runs on with
            no restart. His words: "the music should not change ... right now its a very abrupt
            transition". There is no "leave the music alone" value: 0 is song 0 and 0xFF is silence.
         2d. Killing the warps left the Capsule Corp doorway as open floor, so the player walked into the
            building, where there is no ground art and BG1 hides him. His words: "the glass door has no
            collision". The arena gets its OWN copy of map 6,1's 0x2000 byte collision frame with the
            building recess closed, cells (28,9) to (35,11), and the map post's one foot cell opened.
            All three doorway rows go, not two: v6 closed rows 9 and 10 and left row 11, which made a one
            row pocket the owner walked into and stood in, behind the BG1 glass, invisible. His words:
            "its like I run into a wall, but I can walk into it", and his v3 state 4 is (246,94), which is
            cell (30,11), the open row. Closing row 11 puts the wall flush with the building face at row
            12. Nothing in the arena ever arrives from inside, because the warps are gone. See INSIDE_BAND.
         2e. The save point and the map post are layout PROPS, and the map's own lists never held them.
            v4 removed their floor SHADOWS and left the objects standing, which is what he saw: "why are
            the map post and save spots STILL THERE!??? I Thought we agreed to remove them, you only
            removed the shadows". The arena gets its own prop list of three entries, map 6,1's props 0,
            3 and 4, which are the glass front door and the two entrance pillars. Props 1 and 2, the map
            post and the save point, are dropped. Each prop was DRAWN from the sheet and identified by
            eye before it was cut (scripts\one-time\2026-11-06-arena-v7\p3_props.py). See ARENA_PROPS.
            The shadow work of 2e stays: the arena keeps its own BG2 layer record and its own copies of
            blocks 2, 3 and 5, with each of the 28 shadow tiles swapped for the clean floor entry of its
            own row at its own tile x parity. The floor repeats every two columns, so the pattern and the
            flip bits come with it. The other five blocks are shared: read only frames no box touches.
         3. Its item list is a PAIR, which is the vanilla shape of every fight that starts out of a talk:
            item 0 is an NPC Imperfect Cell with condition 0, so the map load builds him and the vanilla
            conversation's `walk(28, 244, 504)` plays as written; item 1 is the enemy, condition 1, so
            the load leaves him alone until the fight record's `ext 104 (28, 1)` replaces the NPC with
            him. Map 11,4 carries exactly this pair for Android 17, and its word 6 is the four op record
            the owner pointed at. Condition 0 is "always" and condition 1 is "never at load"
            (`condition_eval` @0x08003F06). `ending_fight` writes the death event onto item 1.
         4. Four literals move to the new base: rom:0x5ADC, rom:0x5D5C and rom:0xEBD8 name the table,
            and rom:0x195C names entry 3 (map 1,4) directly. The count getter sub_0800E0AC returns
            0xFF + 0x48; the byte rom:0xE0AE goes to 0x49, which makes 328.
         5. The OLD table is left byte for byte, so any word that still names it reads vanilla data.
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla map entry,
         item or enemy type is changed, so every other map keeps its own behaviour.
         The arena enemy's event struct is a fresh copy of the vanilla one. ending_fight overwrites its
         table word with the ending's own death table, and must never touch the vanilla struct.
"""
import hashlib
import struct

from rom.webfoot_decompress import decompress, unpack_frame
from rom.webfoot_lz_pack import pack
from scene.scene_lib import words_naming

# ===== constants: the map table (base bytes, 01_probe.txt, 02_literal_loads.txt, 04_table_interior.txt) =====
ROM_BASE = 0x08000000
MAPS, MAP_SIZE, MAP_COUNT = 0x409368, 56, 327
NEXT_TABLE = MAPS + MAP_SIZE * MAP_COUNT           # rom:0x40DAF0, a second table, not padding (literal rom:0xE1D0)
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)           # the 3 words that name the table base
ENTRY3_LITERAL, ENTRY3 = 0x195C, 3                 # a 4th literal names entry 3 (map 1,4) directly
COUNT_FN, COUNT_BYTE = 0xE0AC, 0xE0AE              # sub_0800E0AC: MOV r0,#0xFF ; ADD r0,#0x48 ; BX lr
COUNT_CODE = bytes.fromhex("ff2048307047")
COUNT_OLD, COUNT_NEW = 0x48, 0x49                  # 0xFF + 0x48 = 327; 0xFF + 0x49 = 328

# Entry fields (bible OVW). A count byte is zero exactly when its list word is zero, in all 327.
F_VARIATIONS, F_REGION_COUNT, F_ITEM_COUNT = 2, 3, 4
F_COMBAT, F_BANNER, F_REGIONS, F_ITEMS = 8, 0x0C, 0x10, 0x14
F_SWAPS, F_PICKUPS, F_MARKERS, F_MUSIC = 0x18, 0x1C, 0x20, 0x24
F_VAR_SCRIPT, F_LAYOUTS, F_ENTER, F_LEAVE = 0x28, 0x2C, 0x30, 0x34

SOURCE_INDEX = 145                                 # map 6,1, Capsule Corp in the future
SOURCE_AT = MAPS + MAP_SIZE * SOURCE_INDEX         # rom:0x40B320
SOURCE_ZONE_AREA = bytes([6, 1])
SOURCE_ENTRY = bytes.fromhex("06010106" "07000000" "00000000" "be000000" "f89c3f08" "409c3f08" "00000000"
                             "00000000" "00000000" "f09a3f08" "00000000" "2c9b3f08" "0a9b3f08" "1f9b3f08")

# ===== constants: map 6,1's layout chain (base bytes, v2_layout.py and v3_census.py) =====
# Entry +0x2C is a LIST of layout pointers, one per variation. Map 6,1 has one variation, so its list
# is one word. Exactly one aligned word names each link of the chain, so a copy is unambiguous.
SOURCE_LAYOUTS = 0x3F9B2C                          # entry 145 +0x2C names this list
SOURCE_LAYOUT = 0x5F209C                           # list[0]: the layout struct
LAYOUT_SIZE = 0xCC                                 # the closest pair of layout addresses is 204 bytes
L_COLLISION = 0x34                                 # apart, so the engine reads no more than that
SOURCE_FRAME = 0x5F164C                            # layout +0x34: the collision frame, type 1, 0x2000
L_WARP_COUNT, L_WARP_LIST = 0x40, 0x44             # the layout's own door list: a count and a pointer
SOURCE_WARPS, SOURCE_WARP_LIST = 3, 0x5F2090       # map 6,1 has 3 doors; +0x44 is a list of POINTERS
SOURCE_DOOR = 0x5F2078                             # list[2]: the Capsule Corp front door, rect
SOURCE_DOOR_RECT = (224, 88, 273, 105)             # (224,88)-(273,105) to map 6,2 at (144,276)

# ===== constants: map 6,1's layout PROPS (bible row 1119, read in p1_probe.py and p3_props.py) =====
# +0x24 is the prop count, +0x28 the entries, 24 bytes each: u32 x0, y0, x1, y1, then the OBJ attribute
# pair and {u16 tile, u8 priority, u8}. attr0 bits 14-15 are the OBJ shape and attr1 bits 14-15 the size,
# and all five agree with their own rectangle. The sheet at +0x2C is 8 BITS a pixel; the tile field is a
# GBA OBJ tile number, which counts 32 byte units at any depth, so prop k starts at 32 * tile and reads
# 64 bytes an 8x8 tile. The five props then tile the 7680 byte sheet end to end with no gap, which is how
# the depth was settled: a 4 bit reading leaves four holes and draws noise.
L_PROP_COUNT, L_PROP_LIST, L_PROP_SHEET = 0x24, 0x28, 0x2C
PROP_SIZE, SOURCE_PROPS, SOURCE_PROP_LIST = 24, 5, 0x5F16DC
SOURCE_PROP_RECTS = ((224, 64, 288, 96),           # 0 the Capsule Corp glass front door, 64x32
                     (240, 200, 272, 232),         # 1 the MAP POST, a map on a post with a red X, 32x32
                     (408, 556, 472, 620),         # 2 the SAVE POINT, the blue Capsule Corp disc, 64x64
                     (198, 95, 214, 127),          # 3 the west entrance pillar, 16x32
                     (294, 95, 310, 127))          # 4 the east entrance pillar, 16x32, the same art
ARENA_PROPS = (0, 3, 4)                            # the door and the two pillars stay; the owner's call
                                                   # on 2026-11-06 cuts the map post and the save point

# ===== constants: the arena's own collision frame (base reads, p1_probe.py to p6_warpitems.py) =====
# collision_test @0x08005D6C: byte cy x 32 + (cx >> 3), bit cx & 7, SET = OPEN, 8 px cells.
FRAME_STRIDE, FRAME_SIZE = 32, 0x2000
SOURCE_FRAME_SHA1 = "b97921c62a8f46856d89eba5265d16b9d260a681"     # the DECODED 0x2000 bytes
# The building recess is an 8 cell corridor, cx 28 to 35, walled at cx 27 and cx 36 and closed above at
# cy 8. The courtyard starts at cy 12. Closing all three inner rows seals it and takes no courtyard cell.
# ALL THREE, not two. v6 closed rows 9 and 10 and left row 11 open, and the owner walked up into that one
# row pocket and stood inside it, behind the BG1 glass, out of sight: "its like I run into a wall, but I
# can walk into it". His v3 state 4 at (246,94) is cell (30,11), the row v6 left. Closing row 11 puts the
# wall flush with the building face at cy 12. The old reason for keeping row 11 was that map 6,2's warp
# rom:0x5F0124 lands the player back on map 6,1 at (248,100), cell (31,12), and he walks out through row
# 11. That reason does not apply to the arena: its warps are gone, so nothing ever arrives from inside.
INSIDE_BAND = (28, 9, 35, 11)                      # cells (cx0, cy0, cx1, cy1): px (224,72)-(287,95)
# The map post stands on ONE closed collision cell, its own foot, with open plaza all round it. Cutting
# the prop without opening that cell would leave an invisible 8 px block where the post used to be.
POST_FOOT = (32, 28)                               # px (256,224)-(263,231), under prop 1

# ===== constants: the arena's own BG2 (base reads, p7_shadows.py, p8_boxes.py, p14_pins.py) =====
# A layer record: +0x00 vtable, +0x04 w, +0x08 h, +0x14 blocks across, +0x15 down, +0x18 one frame pointer
# per block. BG3's first block frame starts at BG2's record +0x38, so the record is exactly 0x38 bytes.
L_BG2, L_BG3 = 0x1C, 0x20
SOURCE_BG2, BG2_SIZE = 0x5F1434, 0x38
BG2_PTRS, BG2_GRID = 0x18, (2, 4)                  # +0x14 and +0x15 carry the grid; 8 blocks in all
BLOCK_TILES, BLOCK_SIZE = 32, 0x800                # each block is a 32 x 32 map of u16 entries
ENTRY_TILE = 0x3FF                                 # entry bits: tile 0-0x3FF, 0x400 flip x, 0x800 flip y
L_TILE_INDEX, L_TILE_TABLE = 0x48, 0x4C            # the layout's tile stream and its chunk table
SOURCE_BLOCK_SHA1 = {2: "07b40beee6232aad93c3535191536401c83c4405",   # the DECODED 0x800 bytes of each
                     3: "b76d5541e6057505150727fa1b6e2a4a9791d8c1",   # block a shadow box touches
                     5: "4dbec316a2c265593d0dec366aa89e754439f716"}
SHADOW_INDEX = 73                                  # BG palette (144,200,248); the pale floor is 72
# WHICH box belongs to WHICH prop is UNRESOLVED, and it does not matter here: the arena cuts props 1
# and 2 and paints out both boxes, so the pairing is a label, not a behaviour. Two shapes point the
# same way and one contradicts them. Columns: box 1 stands in the map post's tile columns (30-34
# against the prop's 30-33) and box 2 in the save point's (52-59 against 51-58). Geometry: box 1 is a
# flat 40x16 oval, which suits a thin post, and box 2 is a round 64x56 disc shadow, which suits the
# 64x64 save disc (renders in the v7 one-time render folder). AGAINST both: each box
# sits about 130 px BELOW its prop's rect (135 for the post, 128 for the disc), far too much for a cast
# shadow, and no handler was opened to explain the offset. The bible ARN4 row calls box 1 the save
# point's and box 2 "the dome", which disagrees with the geometry. Do not build on the pairing.
SHADOW_BOXES = ((30, 43, 34, 44),                  # upper box, px (240,344)-(279,359), 10 tiles
                (52, 86, 59, 92))                  # lower box, px (416,688)-(479,743), 18 tiles
SHADOW_TILES = 28                                  # 10 in the upper box and 18 in the lower

# ===== constants: the vanilla Imperfect Cell enemy item (base bytes, 07_cell_event.txt) =====
CELL_ITEM = 0x4058A4                               # map entry 287's item; it is not changed
CELL_ITEM_BYTES = bytes.fromhex("7fe70008" "88000200" "3c000000" "08018000"
                                "1c000000" "9c584008" "01000000" "94584008")
CELL_EVENT = (0x40589C, bytes.fromhex("b3060108" "a0243e08"))   # {event runner, Cell's vanilla death table}
CELL_TAIL = (0x405894, bytes.fromhex("0fcb0008" "007d0000"))    # the stand step struct every enemy item names
ITEM_SIZE, ITEM_COND, ITEM_TYPE, ITEM_AT, ITEM_SET, ITEM_EVENT, ITEM_TAIL = 0x20, 4, 8, 0xC, 0x10, 0x14, 0x1C
COND_ALWAYS, COND_NEVER_AT_LOAD = 0, 1             # condition_eval @0x08003F06: 0 always, 1 never at load
ENEMY_FACTORY, EVENT_RUNNER = 0x0800E77F, 0x080106B3
ENEMY_TABLE, ENEMY_ENTRY, CELL_TYPE, CELL_SET = 0x6D56AC, 24, 60, 28
TYPE60 = bytes.fromhex("00000000" "5a140000" "50000000" "20202580" "80000000" "c4f36f08")   # HP 5210, AI 80

# ===== constants: map 6,1's own NPC items (base bytes, read in this task) =====
# An NPC item is 0x18 bytes: u32 factory, u32 condition, s16 x, s16 y, u32 set, u32 step count,
# u32 steps. Item 6 is the NPC Imperfect Cell the vanilla ending talks to, and item 5 the NPC Super
# Saiyan Trunks the vanilla record 13 walks. Both carry condition 0x000100C4, which Script_TestFlag
# @0x08003F06 reads as "flag 196 set", and both name the same 8 byte stand step rom:0x3F9C20.
NPC_FACTORY = 0x0800D6DF
NPC_ITEM_SIZE, N_COND, N_AT, N_SET, N_STEPS, N_STEP_LIST = 0x18, 4, 8, 0xC, 0x10, 0x14
SOURCE_CELL_NPC = (0x3F9C28, bytes.fromhex("dfd60008" "c4000100" "20018801" "1c000000"
                                           "01000000" "209c3f08"))     # map 6,1 item 6, set 28
SOURCE_TRUNKS_NPC = (0x3F9C08, bytes.fromhex("dfd60008" "c4000100" "f8007002" "85000000"
                                             "01000000" "009c3f08"))   # map 6,1 item 5, set 133
NPC_STEP = (0x3F9C20, bytes.fromhex("0fcb0008" "007d0000"))             # the stand step both items name

# ===== constants: the design (the owner's call, 2026-11-05) =====
ARENA_ZONE, ARENA_AREA, ARENA_VARIATIONS = 6, 100, 1    # zone 6 uses areas 1..99, so 100 is free
ARENA_INDEX = MAP_COUNT                                 # the new last entry, 327
COMBAT_ON = 1                                           # entry +0x08: map 6,1 has 0, which is why the
ARENA_ITEMS = 2                                         # player could not attack. 248 of 327 maps have 1
NPC_INDEX, ENEMY_INDEX = 0, 1                           # item 0 the NPC Cell, item 1 the enemy Cell:
                                                        # the pair map 11,4 carries for Android 17
# Entry +0x0C is the map NAME, and 0xDD means "show none". CONFIRMED in the handler, 2026-11-06, which
# upgrades what was a LIKELY read off 5 vanilla carriers. `sub_0800C584` runs `LDR r0,[r5,#0x4]` (the map
# entry) into `sub_0800EBB6`, which reads +0x0C and returns it as the id when its high half is zero, or
# runs it as a script when it is not. Back in the caller: `LDRH r1,[r5,#0x8] ; CMP r1,r0 ; BEQ` skips a
# name already shown, then `CMP r0,#0xDD ; BEQ` skips the banner call `sub_0800C978` outright.
NO_BANNER = 0xDD

# Entry +0x24 is the map's song id, or a script that returns one (`sub_0800EB58`: a value under 0x10000
# is the id itself). The map load reads it at `loc_0800C4D6`: 0xFF stops the player, and otherwise it
# calls `music_play` UNLESS the player is already playing that exact record (+5 is 1 and +0xC equal).
# The ending's own record 0 starts song 38 and nothing stops it before the fight, so naming 38 here
# makes the load a no-op and the music runs on. 0 is not "leave it alone": it is song 0.
ENDING_MUSIC = 38                                       # the owner: "the music should not change"

# The two fight spots, in map pixels: the spots the CONVERSATION itself leaves the pair standing on, so
# the fight starts with no jump. His call on 2026-11-06: "the start still transitions both cell and trunks
# to different points on the map". Read out of his own v3 states: object 0x02035078 walks from map 6,1's
# own Cell item (288,392) in state 1 to (244,504) in state 2, and 0x020351EC holds (248,568) in both. The
# vanilla ending tail respawns its own Trunks at (248,568) too, so two sources agree on that one.
# KNOWN COST, measured in p9_bg1.py and already in bible row 1207: BG1 carries the CAPSULE CORPORATION
# banner across rows y 480 to 551 and draws OVER an actor, so 2423 BG1 pixels fall inside Cell's envelope
# at (244,504) and none at the old (244,616). Cell's envelope is 20 left, 44 right, 56 up and 8 down from
# his point. The nearest banner-clear row is y 608, which is the old spot, so no-jump and no-cover cannot
# both hold. Cell's fight AI walks him down out of the banner at once; state 3 caught him 8 px below spawn.
CELL_SPOT = (244, 504)                                  # where the talk leaves Cell standing
TRUNKS_SPOT = (248, 568)                                # 64 px below him, where the talk leaves the player
# Where each of the two walks STARTS, both of them map 6,1's own NPC spots, so the arena plays the vanilla
# conversation move for move. The NPC Cell item stands at map 6,1 item 6's spot and the vanilla record 15
# walks him to CELL_SPOT; the player loads on map 6,1 item 5's spot and ending_fight's record 13 walks him
# to TRUNKS_SPOT, which is the walk vanilla gave the NPC Trunks.
CELL_START = (288, 392)                                 # map 6,1 item 6's own spot
TRUNKS_START = (248, 624)                               # map 6,1 item 5's own spot


# ===== the new entry and the new item =====

def arena_entry(source: bytes, items_at: int, layouts_at: int) -> bytes:
    """Entry 327, map 6,100: combat on, an NPC Cell and an enemy Cell, no regions, no banner.

    An empty region list removes map 6,1's own 2 warps, its 2 scripts and its scene. It does NOT remove
    the 3 doors or the 5 props the LAYOUT carries, which is why the layout is copied. Every other list
    is empty too, which removes the vanilla NPCs; the item list holds only the two Cells. The whole room stays walkable on purpose: the owner play-tested a
    collision bound on 2026-11-06 and called it "a invisible wall" that "was too restrictive".

    The banner is NOT copied. Map 6,1's 0xBE draws "CAPSULE CORPORATION" over the fight, which the owner
    called a fault. +0x0C = 0xDD is LIKELY "no name": 5 vanilla entries carry it, and no handler was
    read to prove the meaning.

    The music word names the song the ending is ALREADY playing, so the load leaves the player alone.
    See ENDING_MUSIC. Map 6,1's own +0x24 is a script pointer, which would pick the town's song."""
    entry = bytearray(MAP_SIZE)
    entry[0], entry[1] = ARENA_ZONE, ARENA_AREA
    entry[F_VARIATIONS], entry[F_REGION_COUNT] = ARENA_VARIATIONS, 0
    entry[F_ITEM_COUNT] = ARENA_ITEMS
    entry[F_COMBAT] = COMBAT_ON
    entry[F_BANNER:F_BANNER + 4] = _word(NO_BANNER)
    entry[F_MUSIC:F_MUSIC + 4] = _word(ENDING_MUSIC)
    entry[F_ITEMS:F_ITEMS + 4] = _word(items_at + ROM_BASE)
    entry[F_LAYOUTS:F_LAYOUTS + 4] = _word(layouts_at + ROM_BASE)
    return bytes(entry)


def arena_layout(source: bytes, collision_at: int, bg2_at: int, props_at: int) -> bytes:
    """Map 6,1's layout struct with SIX words changed and every other byte copied.

    +0x40 and +0x44, its door count and door list, go to zero as a pair, which is how all 327 vanilla
    layouts carry them: v3_census.py found no layout where one is zero alone.
    +0x24 and +0x28, its prop count and prop list, name the arena's own three prop list. The count and
    the list move together for the same reason the warps do. The prop SHEET at +0x2C is shared and
    unchanged: the three props that stay read tiles out of it, and an unused tile costs nothing.
    +0x34 names the arena's own collision frame and +0x1C its own BG2 layer record.
    Everything else is copied, so the arena keeps map 6,1's BG0, BG1 and BG3, its tiles, its palette and
    its blend words. Those pointers are read only, so sharing them changes nothing."""
    out = bytearray(source)
    out[L_WARP_COUNT:L_WARP_COUNT + 4] = _word(0)
    out[L_WARP_LIST:L_WARP_LIST + 4] = _word(0)
    out[L_PROP_COUNT:L_PROP_COUNT + 4] = _word(len(ARENA_PROPS))
    out[L_PROP_LIST:L_PROP_LIST + 4] = _word(props_at + ROM_BASE)
    out[L_COLLISION:L_COLLISION + 4] = _word(collision_at + ROM_BASE)
    out[L_BG2:L_BG2 + 4] = _word(bg2_at + ROM_BASE)
    return bytes(out)


# ===== the arena's own prop list =====

def arena_props(rom: bytes) -> bytes:
    """Map 6,1's prop entries 0, 3 and 4, copied byte for byte and in order.

    Prop 0 is the glass front door, props 3 and 4 the two entrance pillars. The owner asked for the map
    post (prop 1) and the save point (prop 2) to go, and for nothing else to go with them, so the three
    that stay are COPIED, not rebuilt: every attribute, tile number and priority comes across.
    Every prop was drawn from the sheet and named by eye before any entry was cut; the pictures are in
    scripts\\one-time\\2026-11-06-arena-v7\\render\\prop_<k>.png."""
    at = SOURCE_PROP_LIST
    return b"".join(bytes(rom[at + PROP_SIZE * k:at + PROP_SIZE * (k + 1)]) for k in ARENA_PROPS)


# ===== the arena's own collision frame =====

def inside_cells() -> list:
    """The building interior cells the arena closes, as (cx, cy)."""
    cx0, cy0, cx1, cy1 = INSIDE_BAND
    return [(cx, cy) for cy in range(cy0, cy1 + 1) for cx in range(cx0, cx1 + 1)]


def arena_collision(source: bytes) -> bytes:
    """Map 6,1's own collision bits with the building recess closed, the map post's foot opened, and no
    other cell touched.

    A set bit is OPEN, so closing a cell clears it and opening one sets it. The courtyard, the grass and
    the walls all keep the value map 6,1 gives them, which is the owner's "block nothing" for the room.
    The one opened cell is the foot the map post stood on: the prop goes, so the block under it must go
    too, or he walks into an invisible 8 px post."""
    if len(source) != FRAME_SIZE:
        raise ValueError(f"the collision frame decoded to {len(source)} bytes, expected 0x{FRAME_SIZE:X}")
    out = bytearray(source)
    for cx, cy in inside_cells():
        at, bit = cy * FRAME_STRIDE + (cx >> 3), 1 << (cx & 7)
        if not out[at] & bit:
            raise ValueError(f"cell ({cx},{cy}) is already closed in map 6,1: the band has moved")
        out[at] &= ~bit & 0xFF
    cx, cy = POST_FOOT
    at, bit = cy * FRAME_STRIDE + (cx >> 3), 1 << (cx & 7)
    if out[at] & bit:
        raise ValueError(f"the map post's foot ({cx},{cy}) is already open in map 6,1: the prop has moved")
    out[at] |= bit
    return bytes(out)


# ===== the arena's own BG2 =====

def tile_pixels(rom: bytes, layout: int) -> list:
    """The layout's 8x8 tiles, in index order. +0x48 is a delta coded stream (each entry plus the one
    before plus 1) whose entries name a chunk and a tile in it; +0x4C is the chunk table.

    Held here rather than imported from scene.map_view, which needs Pillow. A build must not."""
    raw = _frame(rom, _u32(rom, layout + L_TILE_INDEX))
    idx = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = _u32(rom, layout + L_TILE_TABLE) - ROM_BASE, {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = _frame(rom, _u32(rom, table + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def bg2_blocks(rom: bytes, record: int) -> dict:
    """{block index: its 0x800 decoded entry map}. The grid is +0x14 across by +0x15 down."""
    across, down = rom[record + 0x14], rom[record + 0x15]
    if (across, down) != BG2_GRID:
        raise ValueError(f"BG2 is a {across}x{down} grid, expected {BG2_GRID[0]}x{BG2_GRID[1]}")
    return {k: _frame(rom, _u32(rom, record + BG2_PTRS + 4 * k)) for k in range(across * down)}


def shadow_repairs(blocks: dict, tiles: list) -> dict:
    """{(tile x, tile y): (old entry, clean entry)} for every shadow tile of the two boxes.

    The floor repeats every two columns in each row, so the clean entry is the nearest entry of the SAME
    row at the SAME tile x parity whose tile draws no shadow pixel. Copying the whole u16 carries the
    flip bits with it. A shadow tile with no clean same-parity neighbour in its row raises."""
    width = BG2_GRID[0] * BLOCK_TILES

    def at(tx, ty):
        k = (ty // BLOCK_TILES) * BG2_GRID[0] + tx // BLOCK_TILES
        return struct.unpack_from("<H", blocks[k], 2 * ((ty % BLOCK_TILES) * BLOCK_TILES
                                                        + tx % BLOCK_TILES))[0]

    def shadowed(entry):
        tile = entry & ENTRY_TILE
        return tile < len(tiles) and SHADOW_INDEX in tiles[tile]

    out = {}
    for tx0, ty0, tx1, ty1 in SHADOW_BOXES:
        for ty in range(ty0, ty1 + 1):
            for tx in range(tx0, tx1 + 1):
                if not shadowed(at(tx, ty)):
                    continue
                clean = next((at(nx, ty) for step in range(2, width, 2)
                              for nx in (tx - step, tx + step)
                              if 0 <= nx < width and not shadowed(at(nx, ty))), None)
                if clean is None:
                    raise ValueError(f"tile ({tx},{ty}) has no clean floor entry in its own row")
                out[(tx, ty)] = (at(tx, ty), clean)
    if len(out) != SHADOW_TILES:
        raise ValueError(f"{len(out)} shadow tiles in the two boxes, expected {SHADOW_TILES}")
    return out


def arena_bg2_block(block: bytes, repairs: dict, k: int) -> bytes:
    """One block's entry map with its own share of the repairs applied."""
    out = bytearray(block)
    for (tx, ty), (old, clean) in repairs.items():
        if (ty // BLOCK_TILES) * BG2_GRID[0] + tx // BLOCK_TILES != k:
            continue
        at = 2 * ((ty % BLOCK_TILES) * BLOCK_TILES + tx % BLOCK_TILES)
        if struct.unpack_from("<H", out, at)[0] != old:
            raise ValueError(f"block {k} tile ({tx},{ty}) is not entry 0x{old:04X}")
        struct.pack_into("<H", out, at, clean)
    return bytes(out)


def arena_bg2(source: bytes, block_at: dict) -> bytes:
    """Map 6,1's BG2 layer record with the copied blocks repointed and every other word copied."""
    out = bytearray(source)
    for k, at in block_at.items():
        out[BG2_PTRS + 4 * k:BG2_PTRS + 4 * k + 4] = _word(at + ROM_BASE)
    return bytes(out)


def cell_npc_item(step_at: int) -> bytes:
    """Item 0: map 6,1's own NPC Imperfect Cell, on his own spot, with condition 0 so the load builds him.

    This is the actor the whole conversation talks to. The vanilla record 15 runs `walk(28, 244, 504)`,
    which only works if a set 28 actor already stands on the map, and in vanilla that actor is map 6,1's
    item 6. The arena copies it and changes one word: the condition goes from 0x000100C4, "flag 196 set",
    to 0, "always". The arena is reached only from the ending, and the ending is the one place flag 196
    is set, so the two readings agree; 0 is the simpler of the two and cannot be wrong."""
    item = bytearray(SOURCE_CELL_NPC[1])
    item[N_COND:N_COND + 4] = _word(COND_ALWAYS)
    item[N_AT:N_AT + 4] = struct.pack("<hh", *CELL_START)
    item[N_STEP_LIST:N_STEP_LIST + 4] = _word(step_at + ROM_BASE)
    return bytes(item)


def cell_item(event_at: int, tail_at: int) -> bytes:
    """Item 1: the vanilla Imperfect Cell enemy with condition 1, so the map load leaves him alone.

    The fight record's `ext 104 (28, 1)` is what builds him, by removing the NPC of set 28 and spawning
    THIS item at his position and facing. CONFIRMED from `Sprite_ReplaceWithEntry` @0x0800AAC6 and
    `Object_SpawnFromEntry` @0x0800C75C: the item is built by its own +0 factory with its own bytes, the
    only bound tested is the map's item count, and the condition is never read. So the item keeps its
    +0x14 event struct, which is where `ending_fight` writes the ending's own death table.
    Condition 0 would build him at map load instead, and the conversation would then be talking to an
    armed enemy. Map 11,4 pairs an NPC Android 17 (item 0, condition 0) with an enemy Android 17
    (item 1, condition 1) for exactly this reason, and its word 6 is the four op record the owner named.
    The spot is kept at CELL_SPOT so the item reads right, although ext 104 overwrites it."""
    item = bytearray(CELL_ITEM_BYTES)
    item[ITEM_COND:ITEM_COND + 4] = _word(COND_NEVER_AT_LOAD)
    item[ITEM_AT:ITEM_AT + 4] = struct.pack("<hh", *CELL_SPOT)
    item[ITEM_EVENT:ITEM_EVENT + 4] = _word(event_at + ROM_BASE)
    item[ITEM_TAIL:ITEM_TAIL + 4] = _word(tail_at + ROM_BASE)
    return bytes(item)


def new_table(rom: bytes, entry: bytes) -> bytes:
    """The 327 live entries followed by the arena. Live, not base: an earlier module may have edited one."""
    return bytes(rom[MAPS:MAPS + MAP_SIZE * MAP_COUNT]) + entry


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _frame(rom: bytes, address: int) -> bytes:
    """The decoded payload of the frame an ADDRESS names. Frame header: {u32 type, u32 size}."""
    return unpack_frame(rom, address - ROM_BASE)[2]


def _frame_len(rom: bytes, address: int) -> int:
    """The bytes the frame occupies in the ROM: its 8 byte header plus its stream."""
    return 8 + unpack_frame(rom, address - ROM_BASE)[3]


def _packed_frame(payload: bytes) -> bytes:
    """A type 1 frame of this payload, proven by decoding it back before any caller writes it."""
    out = pack(payload, kind=1)
    if decompress(out, 8)[0] != payload or len(out) % 4:
        raise ValueError(f"the packed frame does not round trip, or is not 4 aligned ({len(out)} bytes)")
    return out


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    """(module, (offset, length)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


def zone_areas(rom: bytes) -> list:
    """(zone, area) of every live entry. The pair is the key find_map_entry sub_0800EB7C compares."""
    return [(rom[MAPS + MAP_SIZE * m], rom[MAPS + MAP_SIZE * m + 1]) for m in range(MAP_COUNT)]


# ===== checks =====

def _check_layout_chain(rom: bytearray) -> None:
    """Entry 145 +0x2C names one list, the list names one layout, and each link is named by exactly one
    aligned word. A copy of a shared link would change another map. The layout's own door fields are
    pinned too, so the copy refuses if map 6,1 ever gains or loses a door."""
    _expect(rom, SOURCE_AT + F_LAYOUTS, _word(SOURCE_LAYOUTS + ROM_BASE))
    _expect(rom, SOURCE_LAYOUTS, _word(SOURCE_LAYOUT + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_COLLISION, _word(SOURCE_FRAME + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_BG2, _word(SOURCE_BG2 + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_WARP_COUNT, _word(SOURCE_WARPS))
    _expect(rom, SOURCE_LAYOUT + L_WARP_LIST, _word(SOURCE_WARP_LIST + ROM_BASE))
    _expect(rom, SOURCE_WARP_LIST + 4 * 2, _word(SOURCE_DOOR + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_PROP_COUNT, _word(SOURCE_PROPS))
    _expect(rom, SOURCE_LAYOUT + L_PROP_LIST, _word(SOURCE_PROP_LIST + ROM_BASE))
    for k, rect in enumerate(SOURCE_PROP_RECTS):            # each prop still stands where it was drawn
        _expect(rom, SOURCE_PROP_LIST + PROP_SIZE * k, b"".join(_word(v) for v in rect))
    for target, want, what in ((SOURCE_LAYOUTS, SOURCE_AT + F_LAYOUTS, "map 6,1's layout list"),
                               (SOURCE_LAYOUT, SOURCE_LAYOUTS, "map 6,1's layout struct")):
        if words_naming(rom, target) != [want]:
            raise ValueError(f"{what} 0x{target + ROM_BASE:08X} is named by"
                             f" {words_naming(rom, target)}, expected one word at rom:0x{want:X}")


def _check_art(rom: bytearray) -> None:
    """The two frames the arena copies. Each is pinned by the SHA-1 of its DECODED bytes, because a
    changed stream can decode to the same map and a changed map must stop the build. The copy reads the
    live ROM, so an earlier module's edit of map 6,1's art would otherwise be carried in silently."""
    bits = _frame(rom, SOURCE_FRAME + ROM_BASE)
    if hashlib.sha1(bits).hexdigest() != SOURCE_FRAME_SHA1:
        raise ValueError(f"map 6,1's collision frame rom:0x{SOURCE_FRAME:X} decodes to"
                         f" {hashlib.sha1(bits).hexdigest()}, expected {SOURCE_FRAME_SHA1}")
    blocks = bg2_blocks(rom, SOURCE_BG2)
    for k, want in SOURCE_BLOCK_SHA1.items():
        got = hashlib.sha1(blocks[k]).hexdigest()
        if got != want or len(blocks[k]) != BLOCK_SIZE:
            raise ValueError(f"map 6,1's BG2 block {k} decodes to {got} ({len(blocks[k])} bytes),"
                             f" expected {want} (0x{BLOCK_SIZE:X})")
    repairs = shadow_repairs(blocks, tile_pixels(rom, SOURCE_LAYOUT))
    touched = {(ty // BLOCK_TILES) * BG2_GRID[0] + tx // BLOCK_TILES for tx, ty in repairs}
    if touched != set(SOURCE_BLOCK_SHA1):
        raise ValueError(f"the shadow boxes touch BG2 blocks {sorted(touched)},"
                         f" expected {sorted(SOURCE_BLOCK_SHA1)}")


def _check(rom: bytearray, alloc) -> None:
    if "battle_arena" in alloc.notes:
        raise ValueError("battle_arena already ran")

    for lit in BASE_LITERALS:
        _expect(rom, lit, _word(MAPS + ROM_BASE))
    _expect(rom, ENTRY3_LITERAL, _word(MAPS + MAP_SIZE * ENTRY3 + ROM_BASE))
    if words_naming(rom, MAPS) != list(BASE_LITERALS):
        raise ValueError(f"the map table base is named by {words_naming(rom, MAPS)},"
                         f" expected {[hex(x) for x in BASE_LITERALS]}")
    if words_naming(rom, MAPS + MAP_SIZE * ENTRY3) != [ENTRY3_LITERAL]:
        raise ValueError(f"map entry {ENTRY3} is named by {words_naming(rom, MAPS + MAP_SIZE * ENTRY3)},"
                         f" expected one word at rom:0x{ENTRY3_LITERAL:X}")

    _expect(rom, COUNT_FN, COUNT_CODE)
    if rom[COUNT_BYTE] != COUNT_OLD or 0xFF + rom[COUNT_BYTE] != MAP_COUNT:
        raise ValueError(f"rom:0x{COUNT_BYTE:X} is 0x{rom[COUNT_BYTE]:02X}, so the map count is not {MAP_COUNT}")

    _expect(rom, SOURCE_AT, SOURCE_ZONE_AREA)
    _expect(rom, SOURCE_AT, SOURCE_ENTRY)
    _check_layout_chain(rom)
    _check_art(rom)
    pairs = zone_areas(rom)
    if len(set(pairs)) != MAP_COUNT:
        raise ValueError("(zone, area) is not unique across the 327 map entries")
    if (ARENA_ZONE, ARENA_AREA) in pairs:
        raise ValueError(f"map {ARENA_ZONE},{ARENA_AREA} already exists: pick another free area")

    _expect(rom, CELL_ITEM, CELL_ITEM_BYTES)
    _expect(rom, *CELL_EVENT)
    _expect(rom, *CELL_TAIL)
    _expect(rom, *SOURCE_CELL_NPC)
    _expect(rom, *SOURCE_TRUNKS_NPC)
    _expect(rom, *NPC_STEP)
    if _u32(SOURCE_CELL_NPC[1], 0) != NPC_FACTORY or _u32(SOURCE_CELL_NPC[1], N_SET) != CELL_SET:
        raise ValueError("SOURCE_CELL_NPC constant: not the NPC factory, or not set 28")
    for name, item, spot in (("SOURCE_CELL_NPC", SOURCE_CELL_NPC[1], CELL_START),
                             ("SOURCE_TRUNKS_NPC", SOURCE_TRUNKS_NPC[1], TRUNKS_START)):
        if struct.unpack_from("<hh", item, N_AT) != spot:
            raise ValueError(f"{name} stands at {struct.unpack_from('<hh', item, N_AT)}, not {spot}")
    if _u32(SOURCE_CELL_NPC[1], N_STEP_LIST) - ROM_BASE != NPC_STEP[0]:
        raise ValueError("map 6,1's NPC Cell does not name the stand step NPC_STEP")
    if _u32(CELL_ITEM_BYTES, 0) != ENEMY_FACTORY or _u32(CELL_ITEM_BYTES, ITEM_TYPE) != CELL_TYPE:
        raise ValueError("CELL_ITEM_BYTES constant: not the enemy factory, or not type 60")
    if _u32(CELL_EVENT[1], 0) != EVENT_RUNNER:
        raise ValueError("CELL_EVENT constant: +0 is not the event runner")
    _expect(rom, ENEMY_TABLE + ENEMY_ENTRY * CELL_TYPE, TYPE60)

    # The map table itself is NOT guarded. An earlier module may edit an entry in place (chamber_spar
    # edits 6,70, celljr_fight edits 14,3), and the copy reads the live ROM, so its edit is carried.
    # The hazard runs the other way: a module that writes a map entry AFTER this one writes into the
    # dead old table. Only the build list order stops that, and test_battle_arena checks it.
    guarded = ((NEXT_TABLE, 4, "the table right after the map table"),
               (COUNT_FN, len(COUNT_CODE), "the map count getter"),
               (CELL_ITEM, ITEM_SIZE, "the Imperfect Cell enemy item"),
               (CELL_EVENT[0], len(CELL_EVENT[1]), "Cell's event struct"),
               (CELL_TAIL[0], len(CELL_TAIL[1]), "Cell's step struct"),
               (SOURCE_AT, MAP_SIZE, "map 6,1's own map entry"),
               (SOURCE_LAYOUTS, 4, "map 6,1's layout list"),
               (SOURCE_LAYOUT, LAYOUT_SIZE, "map 6,1's layout struct"),
               (SOURCE_PROP_LIST, PROP_SIZE * SOURCE_PROPS, "map 6,1's prop list"),
               (SOURCE_CELL_NPC[0], NPC_ITEM_SIZE, "map 6,1's NPC Imperfect Cell item"),
               (NPC_STEP[0], len(NPC_STEP[1]), "map 6,1's NPC stand step"),
               (SOURCE_FRAME, _frame_len(rom, SOURCE_FRAME + ROM_BASE), "map 6,1's collision frame"),
               (SOURCE_BG2, BG2_SIZE, "map 6,1's BG2 layer record")) \
        + tuple((_u32(rom, SOURCE_BG2 + BG2_PTRS + 4 * k) - ROM_BASE,
                 _frame_len(rom, _u32(rom, SOURCE_BG2 + BG2_PTRS + 4 * k)),
                 f"map 6,1's BG2 block {k}") for k in SOURCE_BLOCK_SHA1) \
        + tuple((lit, 4, f"the map table literal rom:0x{lit:X}") for lit in BASE_LITERALS) \
        + ((ENTRY3_LITERAL, 4, f"the map entry {ENTRY3} literal"),)
    for name, (start, size) in _written(alloc.notes):
        for lo, n, what in guarded:
            if start < lo + n and lo < start + size:
                raise ValueError(f"{what} rom:0x{lo:X} is also written by {name}: stop and report")


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
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

    tail = place(CELL_TAIL[1], "the arena enemy's step struct")
    event = place(CELL_EVENT[1], "the arena enemy's event struct (ending_fight repoints its table word)")
    step = place(NPC_STEP[1], "the arena NPC Cell's stand step")
    npc = place(cell_npc_item(step), "the arena NPC Cell (set 28, cond 0, map 6,1 item 6's own spot)")
    item = place(cell_item(event, tail), "the arena enemy (Imperfect Cell, cond 1, vanilla type 60)")
    items = place(_word(npc + ROM_BASE) + _word(item + ROM_BASE),
                  f"the arena item list ({ARENA_ITEMS} items: the NPC, then the enemy)")
    collision = place(_packed_frame(arena_collision(_frame(rom, SOURCE_FRAME + ROM_BASE))),
                      "the arena's collision frame (map 6,1's, with the building recess closed and the"
                      " map post's foot opened)")
    blocks = bg2_blocks(rom, SOURCE_BG2)
    repairs = shadow_repairs(blocks, tile_pixels(rom, SOURCE_LAYOUT))
    block_at = {k: place(_packed_frame(arena_bg2_block(blocks[k], repairs, k)),
                         f"the arena's BG2 block {k} (its shadow tiles swapped for clean floor)")
                for k in sorted(SOURCE_BLOCK_SHA1)}
    bg2 = place(arena_bg2(bytes(rom[SOURCE_BG2:SOURCE_BG2 + BG2_SIZE]), block_at),
                f"the arena's BG2 layer record (blocks {sorted(block_at)} repointed)")
    props = place(arena_props(rom),
                  f"the arena's prop list (map 6,1's props {', '.join(str(k) for k in ARENA_PROPS)}:"
                  f" the glass door and the two pillars; the map post and the save point are cut)")
    layout = place(arena_layout(bytes(rom[SOURCE_LAYOUT:SOURCE_LAYOUT + LAYOUT_SIZE]), collision, bg2,
                                props),
                   "the arena's layout copy (its own collision, BG2 and props, its door list zeroed)")
    layouts = place(_word(layout + ROM_BASE), f"the arena layout list ({ARENA_VARIATIONS} variation)")
    entry = arena_entry(bytes(rom[SOURCE_AT:SOURCE_AT + MAP_SIZE]), items, layouts)
    table = place(new_table(rom, entry), f"the map table copy ({MAP_COUNT + 1} entries)")

    for lit in BASE_LITERALS:
        put(lit, _word(table + ROM_BASE), f"map table literal rom:0x{lit:X}")
    put(ENTRY3_LITERAL, _word(table + MAP_SIZE * ENTRY3 + ROM_BASE), f"map entry {ENTRY3} literal")
    put(COUNT_BYTE, bytes([COUNT_NEW]), f"map count getter: {MAP_COUNT} becomes {MAP_COUNT + 1}")

    alloc.notes["battle_arena"] = {"table": table, "entry": table + MAP_SIZE * ARENA_INDEX,
                                   "entry_index": ARENA_INDEX, "items": items, "item": item,
                                   "item_index": ENEMY_INDEX, "npc_item": npc,
                                   "npc_item_index": NPC_INDEX, "npc_step": step,
                                   "event": event, "tail": tail, "cell_set": CELL_SET,
                                   "zone": ARENA_ZONE, "area": ARENA_AREA, "variation": ARENA_VARIATIONS,
                                   "cell_spot": CELL_SPOT, "trunks_spot": TRUNKS_SPOT,
                                   "cell_start": CELL_START, "trunks_start": TRUNKS_START,
                                   "layout": layout, "layouts": layouts, "props": props,
                                   "prop_source": ARENA_PROPS,
                                   "collision": collision, "bg2": bg2, "bg2_blocks": block_at,
                                   "closed_cells": inside_cells(), "opened_cells": [POST_FOOT],
                                   "shadow_tiles": sorted(repairs),
                                   "sites": sorted(sites)}
