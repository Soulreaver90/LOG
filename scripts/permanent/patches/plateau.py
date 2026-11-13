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
            1109 cells, 488 of them over reachable walkable ground. So the player walks
            BEHIND scenery in those places, which is what a priority 1 layer is for.
         5. HIS COLLISION IS KEPT. 4988 cells are open, 4849 of them reachable from Cell's own cell,
            and one sealed pocket of 139 cells sits inside the rock ring, cell origins px (488,536) to
            (616,608). No open cell touches the world edge. Both fight spots stand on reachable open
            ground, which this module proves before it writes a byte.
         6. THE ENTRY IS THE LIVE 6,100 ENTRY with four words changed: +0x00 to zone 7, +0x14 to the
            plateau's OWN two item list, +0x2C to the layout array import_map wrote, and +0x24 to
            the song already playing when the split loads this map, so the load is silent. It
            carries combat 1, banner 0xDD and 0 regions. import_map builds the same 56 bytes from
            zeros, and this module overwrites them with the arena's own, so the two have to agree.
            See PLATEAU_MUSIC for why +0x24 may not be the arena's 38.
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
            follow, then the plateau loads and the ARRIVAL plays. See split().
        7bb. THE ARRIVAL IS A SCENE (the owner, 2026-11-08: "with cell in a down state, trunks flies in
            (from the left), cell stands up, placeholder convo, then fight continues"). The screen comes
            back on Cell already down on the RIGHT, Trunks flies in from off screen to the WEST and
            lands on the LEFT, Cell stands up, and the two face each other along X instead of along Y.
            Round 2 then has its own pair of spots on his map, PLATEAU_TRUNKS_SPOT and
            PLATEAU_CELL_SPOT; the ARENA staging that round 1 and the punch use does not move.
        7c. Round 2 is the SAME bar, bottom half, and Cell RE-ARMED by `ext 104`, which is vanilla's own
            multi-round wiring (bible B0832). It arms in its OWN record, table D word 3, because record
            S ends in the owner's own talk, five text records, and a type 0 record cannot carry text.
            Round 2 needs its own death event, or Cell's death on the
            plateau would run the split again and the fight would never end, so the plateau carries its
            OWN item list: an NPC Cell on the fight spot and an enemy Cell whose event struct names
            table D2. D2 is the live 27 word table with word 0 left at ending_fight's record K, the
            collapse, the vanilla blast and the vanilla tail. Vanilla does the same: Perfect Cell's two
            rounds are two different items with two different death tables (B0981).
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla map entry,
         item, layout, layer record or tile is written. The ONE base overlap with the earlier modules is
         the 4 map table literals and the count byte, which is how each relocation hands the table on.
         This module writes ONE base word of its own, ending table word 23, and FOUR words inside
         ending_fight's own table D: word 0 (record S) and words 1, 2 and 3, which were END words and
         now carry the arrival talk and round 2's battle start. All are declared hand-offs. Record A
         is left alone, and so is every byte of ending_fight itself.
"""
import hashlib
import struct
import sys
from pathlib import Path

from rom.webfoot_decompress import unpack_frame
from scene.scene_lib import (battle_start, call, code, ext, fade_in, fade_out, record_end, text,
                             wait, walk_to, words_naming)
import log_paths  # noqa: E402

# map-editor\ carries a hyphen, so it is not an importable package: its folder goes on sys.path, the
# way scripts\permanent\tests\test_import_map.py already reaches it.
sys.path.insert(0, str(log_paths.MAP_EDITOR))

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
MAP_DOC = log_paths.PLATEAU_ART / "map_142.json"            # his "map 142", copied byte for byte
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
# The words of ending_fight's table D that the plateau arrival uses. D word 0 is record S, words 24
# and 25 are the vanilla ending records and word 26 is the END, so 1 to 23 are spare END words. The
# seven taken here are the lowest of them, and each one is a declared hand-off in _check_overlaps.
# Words 1, 2, 4, 5 and 6 are the owner's five lines, word 3 is the transform and word 7 starts round 2.
# Each record hands on to the NEXT index, so the chain is 1, 2, 3, 4, 5, 6, 7 and then END.
TALK_WORDS, TRANSFORM_INDEX, ROUND2_INDEX = (1, 2, 4, 5, 6), 3, 7
TALK_CHAIN = TALK_WORDS + (TRANSFORM_INDEX, ROUND2_INDEX)
FIGHT_WORD = TABLE + 4 * FIGHT_INDEX
EVENT_RUNNER, EVENT_TABLE_AT = 0x080106B3, 4

# The two item shapes, as battle_arena reads them.
ITEM_SIZE, ITEM_TYPE, ITEM_AT, ITEM_EVENT, ITEM_TAIL = 0x20, 8, 0x0C, 0x14, 0x1C
NPC_ITEM_SIZE, N_AT, N_STEP_LIST = 0x18, 8, 0x14
NPC_INDEX, ENEMY_INDEX = 0, 1                   # the plateau list keeps battle_arena's own order

PLAYER, CELL_SET = 0, 28                        # set 0 is the player; 28 is IMPERFECT Cell, not 30
DOWN, UP, WEST, EAST = 0, 1, 2, 3               # ext 55 facings (celljr_fight and chapter_cards agree;
                                                # the vanilla template rom:0x3E9384 faces the eastern
                                                # actor 2 and the western actor 3, which is the same
                                                # reading: 2 looks WEST and 3 looks EAST)
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

# The ARENA's parked view, proved by arithmetic against bible B0246's envelopes, which are the same
# numbers plateau's own ENVELOPE carries: set 28 reaches 20 left, 44 right, 56 up and 8 down, and the
# Trunks sets 8, 24, 24 and 8. A view is 240 x 160 from its TOP LEFT (bible B0959, B0766).
#   Cell at (244,504)   -> x 224..288, y 448..512
#   Trunks at (248,568) -> x 240..272, y 544..576
#   the view (136,432)  -> x 136..376, y 432..592, which holds both whole, with 16 px over Cell's head
# ending_fight's own VIEW, (136,456,40), would cut 8 px off the top of Cell's tallest frames.
#
# SPEED 40, and the reason is measured. `ext 31` BLOCKS until the move reports done, in
# distance/speed + 1 frames (bible B0766). Round 1 ends with the FOLLOW camera on the player, who may
# stand anywhere inside map 6,100's clamp (273, 553), so the pan to (136,432) can be about 180 px. At
# speed 2 that is roughly 90 frames of solid white, because the screen holds white between `ext 42`
# and `ext 43`. Speed 40 makes it about 5 frames, which the flash hides. celljr's record N parks
# vanilla seq 11's camera at speed 40 for the same reason. PLATEAU_VIEW keeps speed 40 too, for the
# other reason: its pan is a known 240 px and every frame of it is black, so it is dead time.
SPLIT_VIEW = (136, 432, 40)
TRUNKS_UP, TRUNKS_DOWN = 24, 8               # bible B0246: sets 132 and 133 reach 24 up, 8 down
TRUNKS_ENVELOPE = (8, 24, TRUNKS_UP, TRUNKS_DOWN)   # bible B0246, in ENVELOPE's own order

# ===== constants: THE PLATEAU ARRIVAL (the owner, 2026-11-08) =====
# "with cell in a down state, trunks flies in (from the left), cell stands up, placeholder convo,
# then fight continues", and before that: "they face eahc other (left to right, not north to south)".
#
# THE ARENA PAIR DOES NOT MOVE. CELL_SPOT, TRUNKS_SPOT, PUNCH_FROM and SPLIT_VIEW are map 6,100's
# staging, which he play tested and approved, and `_check` compares them against the battle_arena
# notes. Round 2 gets its OWN pair on his map instead.
#
# A FACING MIRRORS THE ENVELOPE, so a spot has to clear the UNION of both facings. Bible B0246 gives
# set 28 as 20 left and 44 right of its point for ONE facing, so the union is 44 and 44; the Trunks
# sets are 8 and 24, so 24 and 24. Up and down do not mirror.
ENVELOPE_LR = (44, 44, ENVELOPE[2], ENVELOPE[3])            # set 28, either facing
TRUNKS_ENVELOPE_LR = (24, 24, TRUNKS_UP, TRUNKS_DOWN)       # sets 132 and 133, either facing
PLATEAU_GAP = 64                                            # the approved arena gap, turned 90 degrees
PLATEAU_TRUNKS_SPOT = (408, 456)                            # he lands on the LEFT and faces EAST
PLATEAU_CELL_SPOT = (PLATEAU_TRUNKS_SPOT[0] + PLATEAU_GAP, PLATEAU_TRUNKS_SPOT[1])   # (472, 456)
PLATEAU_FLY_FROM = (192, 456)                               # off screen to the WEST, on the same row
PLATEAU_VIEW = (320, 380, 40)                               # parked on the pair, under the black
# Measured on his map 2026-11-08, every number out of _check_design and proved there before a write:
#   walkable centre about (444,460); the pair's centre is (440,456), 4 px and 4 px off it.
#   the fly lane is 216 px of walkable, art-free ground from (192,456) east to the landing spot.
#   Trunks' right edge at the start is 216 and the parked view's left edge is 320, so he waits
#   104 px off screen; Cell's right edge is 516 against the view's right edge 560.
#   the sealed pocket px (488,536)-(616,608) and the two big BG1 patches are all south of y 496,
#   and Cell's lowest cell is px 464-471, so nothing here touches them.
PLATEAU_SPOTS = ((PLATEAU_CELL_SPOT, ENVELOPE_LR, "Cell"),
                 (PLATEAU_TRUNKS_SPOT, TRUNKS_ENVELOPE_LR, "Trunks"),
                 (PLATEAU_FLY_FROM, TRUNKS_ENVELOPE_LR, "Trunks at the fly-in start"))

# ROUND 2'S DEATH ALSO RUNS ON HIS MAP, and it is NOT this module's record. Table D2 word 0 is
# ending_fight's record K, which restores the pair on the ARENA spots and parks DEATH_VIEW. Until
# the arrival took over, PLATEAU_SPOTS happened to be those same two spots, so his map was proved
# under them by accident. It is not any more, so they are named and proved here in their own right.
# Nothing in ending_fight changes: this only checks that where record K puts them is standable.
DEATH_SPOTS = ((CELL_SPOT, ENVELOPE, "Cell where record K restores him"),
               (TRUNKS_SPOT, TRUNKS_ENVELOPE, "Trunks where record K restores him"))

# The owner edited map 142 after future_v1 and added an OVERHEAD CLIFF: "I added a overhead clif,
# trunks is meant to go under, so its moved from b3 to b1, where the rest of the cliff overhangs
# are". BG1 is priority 1 here, so that art draws OVER whoever stands in it. The repo copy may not
# carry the edit yet, so the rect is named here and added to the art the checks avoid whether the
# document holds it or not. World px, inclusive.
OVERHEAD_CLIFF = (416, 768, 520, 776)

DOWN_STATE, STAND_STATE = 3, 0        # ext 57 (28, 3) is record K's own collapse; B0749 stands with
                                      # ext 121 state 0, which sets a state and does not wait
ARRIVE_SPEED = 500                    # ext 136 n: 5 px a frame (bible B0786), celljr's own fly speed
# THE HAND-OFF RUNS VANILLA'S OWN FASTEST MAP-LOAD TRANSITION AND NO SETTLE WAIT. The owner,
# 2026-11-08: "why are we reinvintng the wheel, the game has loads of transitions, find out the
# length of time, etc, and thats what we use", then "what is the normal transition length in
# vanilla???", and after the next build, twice more, that it is still too long.
# `vanilla_transition_census.py` answers him. It walks every map-owned scene table and totals the
# BLOCKING frames between each `fade_out` and its `fade_in`, which is what a player sits through.
# Over the 17 records that also LOAD A MAP: the black runs 60 to 600 frames, the median is 240,
# 240 is the commonest value, and only 3 of the 17 spend any wait between the fades.
# THE FASTEST IS rom:0x3E424A, decoded op for op out of the base ROM:
#   fade_out(30) ; load_map_at(11,1,1,528,400) ; camera(440,160,20) ; ext78(0,3) ; fade_in(30)
# 60 frames of black, 1.0 second, and its shape is this record's shape: the cover, the load, the
# staging, the camera, then the fade in. So this record takes its two numbers. The fade CENSUS of
# bible B1017 made 120 look like the house value; it counts how long the screen spends FADING, not
# how long the player waits, which is the number he asked about. `LOAD_SETTLE` stays DELETED:
# bible B2170, B0748 and B0877 each decode a vanilla map-load transition with no settle wait, and
# 0x3E424A spends none either.
# WHAT THE BLACK COSTS NOW, op by op, each number read and not guessed:
#   fade_out(30)                          30 frames, and the screen is FADING, not black
#   load_map_at(7,100,...)                its own load time, which is NOT scripted and not measured.
#                                         It runs with the screen ALREADY fully black, which is how
#                                         0x3E424A covers its own load, so the cut cannot show it.
#   ext 52 ; ext 51 ; ext 55              one frame each
#   ext 57 (28, 3)                        64 frames, and this is now the LARGEST single piece of
#                                         the black. Read out of the base ROM, not from a label:
#                                         state 3's tick @0x0800E142 adds 1 to the u16 at +0x12
#                                         every frame and runs `cmp r1,#0x40 ; bcc` @0x0800E150, so
#                                         it calls @0x08007688 on the 64th frame. `ext 57` BLOCKS,
#                                         so Cell really is down before anything else runs. It is
#                                         STAGING, not a load margin: the load is covered by the
#                                         fade that already finished in front of it.
#   ext 55 ; ext 121                      one frame each
#   ext 31 (PLATEAU_VIEW, speed 40)       about 388 px at speed 40, about 11 frames (bible B0766)
#   fade_in(30)                           30 frames, and the screen is FADING, not black
# So about 140 scripted frames, about 2.3 seconds. The same op count on the build before this one,
# which he played and called too long, gives 120 + 3 + 64 + 2 + 11 + 120 = about 320. The map load's
# own cost is in neither total, so both are FLOORS and the saving between them is the real number.
SPLIT_FADE, ARRIVE_BEAT = 30, 30
FAST_TRANSITION = 0x3E424A                   # the vanilla record SPLIT_FADE is read from

# ===== constants: THE PLATEAU TALK, IN THE OWNER'S OWN WORDS =====
# docs\design\2026-11-08-finale-dialogue.md section 4. This replaces the two placeholder records the
# module used to ship. Every character between the quotation marks is his, typos kept. The only byte
# added is the box break 0x0B, which ends a box and opens the next one on an A press (bible B0650),
# and it is only ever placed at a mark he wrote himself.
# His beat order, which is also the table D word order:
#     Cell gets up                                          <- record S already stands him up
#     Cell:   "Your energy will be refreshing. ..."          word 1
#     Trunks: "Enough!"                                      word 2
#     Trunks transforms to Super Saiyan if he is not already word 3
#     Trunks: "You're overconfident Cell."                   word 4
#     Cell:   "There's no reason not to be, ..."             word 5
#     Trunks: "But count me as the last!"                    word 6
#     the fight starts, on track 35                          word 7
# The portrait ids are the Cell talk's own: 38 is Cell (vanilla ending records 18 and 21), 100 is base
# Trunks and 101 is Super Saiyan Trunks (ending_fight BASE_PORTRAIT and SSJ_PORTRAIT). The portrait
# follows the body on screen, so it turns Super Saiyan at the transform and not before.
# Every box below measures under 294 px on the ROM font rom:0x2CC64, and under the 4 line page the
# dialog box holds (bible B2095).
BOX = "\x0b"
CELL_PORTRAIT, TRUNKS_BASE_PORTRAIT, TRUNKS_SSJ_PORTRAIT = 38, 100, 101
# HIS LOCKED TEXT, 2026-11-08. He took both vocative commas, the "start off", the apostrophes and
# every terminal full stop in the table below, and he refused nothing here. The widest line of the
# five is "A nice treat to start off my" at exactly 144 px, which is the line limit: the breaker
# wraps only PAST 144, so it fits, and it is the tightest line in the finale.
TALK = ((1, CELL_PORTRAIT, "Your energy will be refreshing." + BOX                  # 156 px, 2 lines
         + "A nice treat to start off my journey in the time machine."),            # 285 px, 3 lines
        (2, TRUNKS_BASE_PORTRAIT, "Enough!"),                                       # 41 px, 1 line
        (4, TRUNKS_SSJ_PORTRAIT, "You're overconfident, Cell."),                    # 133 px, 1 line
        (5, CELL_PORTRAIT, "There's no reason not to be." + BOX                     # 142 px, 2 lines
         + "I've come across thousands like you."),                                 # 184 px, 2 lines
        (6, TRUNKS_SSJ_PORTRAIT, "But count me as the last!"))                      # 131 px, 1 line

# The transform, word 3. The owner put it BETWEEN two Trunks lines, so the form change is part of the
# exchange and not a pre-roll.
TRUNKS_PARTY, BASE_TRUNKS, SSJ_TRUNKS = 3, 132, 133   # his party id (ext 73) and his two bodies
POWER_UP = 9                                          # player state 9: the power up, 160 frames (B0605)
AURA_SOUND, WHITE = 55, 10                            # vanilla's own aura sound; GOKU_TRANSFORM's flash

# The two music cues the owner picked by ear. He first said 15 for the plateau, then changed it:
# "track 35 instead of 15". 35 is the one that ships.
ROUND1_MUSIC, ROUND2_MUSIC = 28, 35

# THE PLATEAU MAP NAMES THE SONG THAT IS ALREADY PLAYING, so its load is silent.
# He heard the track change twice on the way to round 2 and said "the music transitions to a
# different track between capsule corp and the arena, that should not be the case", then settled it:
# "yes it should be 28, no transition until 35 when the round 2 starts."
# `ext 39` reads the new map's `+0x24` and restarts the music UNLESS the new map names the record
# that is playing (bible B1191, B2176). There is no "leave it alone" value, and 0 is song 0, not
# silence. B2028 proves a script `music(n)` and a map `+0x24 = n` compute the SAME record pointer,
# so naming the playing song makes the compare equal and the track carries unbroken.
# Record R opens round 1 with `music(28)` and nothing between it and record S's load touches the
# music, so 28 is what plays at the load. The plateau entry therefore carries 28, NOT the arena's
# 38, and round 2's own `music(35)` stays the one transition he wants to hear.
PLATEAU_MUSIC = ROUND1_MUSIC

# No BATTLE_START_EXCEPTIONS any more. Record S used to raise the round 2 bar in the same record as
# the map load, which is the template shape rom:0x3E9384 and needed the exception. The arrival talk
# moved the battle start into its own record T, which loads no map and opens no fade, so record T is
# the plain four-op shape and record S raises no bar at all. Neither breaks a rule, and a declared
# exception that breaks no rule is what test_battle_start.stale_exceptions fails on.


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


def art_cells(doc: dict) -> set:
    """Every world cell where BG0 or BG1 draws, plus the owner's overhead cliff.

    Both layers are priority 1 on his map, so what they draw covers the actor (bible B1182, B2113).
    A layer's cell sits at world_cell = layer_cell - its own scroll offset in cells. A cell counts as
    drawing when its tile index is not 0, which is the BLANK tile: that over-counts against the
    document's own 1109 drawing cells and never under-counts, and a spot check may only err on the
    strict side. OVERHEAD_CLIFF is added whether the document holds it or not; see its own note."""
    across, _down = map_tiles(doc)
    out = set()
    for name in ("bg0", "bg1"):
        layer = doc["layers"].get(name)
        if not layer:
            continue
        shift = [(layer.get("offset") or [0, 0])[k] >> 10 >> 3 for k in (0, 1)]
        for index, tile in enumerate(layer.get("cells") or ()):
            if tile:
                out.add((index % across - shift[0], index // across - shift[1]))
    for cy in range(OVERHEAD_CLIFF[1] // 8, OVERHEAD_CLIFF[3] // 8 + 1):
        for cx in range(OVERHEAD_CLIFF[0] // 8, OVERHEAD_CLIFF[2] // 8 + 1):
            out.add((cx, cy))
    return out


def fly_lane(doc: dict = None) -> list:
    """Every 8 px step of Trunks' westward fly-in, from his start to his landing spot."""
    return [(x, PLATEAU_FLY_FROM[1])
            for x in range(PLATEAU_FLY_FROM[0], PLATEAU_TRUNKS_SPOT[0] + 1, 8)]


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
    """The live map 6,100 entry with FOUR words changed: zone, item list, layout array and music.

    The item list must be the plateau's OWN. Sharing battle_arena's would share its enemy item, and an
    item carries its death event at +0x14, so round 2's Cell would die into round 1's death record and
    split again for ever.

    The music word is the arrival's whole silence. This function is the LAST writer of it, after
    `import_map` has laid the entry, so a value set anywhere else would be overwritten here. See
    PLATEAU_MUSIC."""
    out = bytearray(arena)
    out[F_ZONE] = PLATEAU_ZONE
    out[F_ITEMS:F_ITEMS + 4] = _word(items_at + ROM_BASE)
    out[F_LAYOUTS:F_LAYOUTS + 4] = _word(layouts_at + ROM_BASE)
    out[F_MUSIC:F_MUSIC + 4] = _word(PLATEAU_MUSIC)
    return bytes(out)


# ===== the round split (rung 5) =====

def round1(enemy_item: int) -> bytes:
    """R, ending table word 23: round 1 on the arena, with the TOP HALF of the boss bar.

    It is ending_fight's own record F with one op changed, `ext 85 bar_show` for `ext 90 bar_set`, so
    the talk still ends the way the owner approved: no fade, no map load, nobody placed, the HUD back
    and camera_follow(0) panning the view onto the player.

    The segment is (50, 100). See ROUND1_BAR for why lo and hi mean what they mean and why an even
    split is legal.

    `music(28)` opens it, the way ending_fight's record F does. The owner, design section 3: "Track 28
    plays when the battle starts". Record R replaces record F on every word that named it, so the cue
    has to be here too, or the trial build would lose it."""
    return code(END_INDEX, call("music", ROUND1_MUSIC),
                battle_start(enemy_set=CELL_SET, enemy_item=enemy_item,
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
    5. THE HAND-OFF IS B2170's SHAPE: the cover, the `ext 39` load, every staging op back to back,
       the camera park, the reveal. NO SETTLE WAIT, because vanilla spends none: see SPLIT_FADE for
       the census, the decoded vanilla record and the frame by frame cost of this one. A death event
       that loads the next map is vanilla (Cell type 21's death event loads map 14,3, bible B0654).
       `ext 39`, never `ext 35`: only ext 38 and ext 39 reach `sub_0800C584` and build a player.
       `ext 31` is needed because the load centres the camera on the player at (x - 112, y - 76),
       which from PLATEAU_FLY_FROM is (80, 380) and holds neither fighter.
    5a. THE ARRIVAL IS A SCENE, not a pause (the owner, 2026-11-08: "with cell in a down state,
       trunks flies in (from the left), cell stands up, placeholder convo, then fight continues").
       Everything that used to be dead black time now carries the staging:
         - the load drops the PLAYER at PLATEAU_FLY_FROM, 104 px west of the parked view, already
           facing east and already in the flying pose, so the reveal shows an empty western sky;
         - Cell is rebuilt on PLATEAU_CELL_SPOT facing WEST and posed DOWN, with record K's own
           `ext 52` then `ext 51` then `ext 55` then `ext 57` shape, so the item's stand step cannot
           put him back on his feet before the scene says so;
         - `ext 31` parks the view at speed 40, so its known pan costs about 11 black frames
           instead of about 195;
         - then the fade in, and only then does anything move.
       `ext 136` BLOCKS outside a group: its handler `@0x0800A346` ends in `BL actor_queue
       @0x0800E04C`, the same tail as `ext 53`, and actor_queue runs the frame loop whenever the
       group flag word is 0. So Trunks really has landed before Cell stands, and the order cannot
       race. The move ends in state 0 for the PLAYER (bible B0787), so he lands standing, and
       `ext 136` restores his facing byte (B0786), so he still faces east.
    5b. CELL STANDS with `ext 121 (28, 0)`, which sets a state and does not wait (B0750). Vanilla's
       own seq 20 stands both fighters the same way (B0749). `ext 57` is not used here: state 0 is
       the idle loop, and an op that blocks until an anim reports done has nothing to wait for.
    6. ROUND 2 ARMS IN ITS OWN RECORD, after the owner's own talk. A type 0 record cannot hold text,
       so record S hands on to table D word 1 and the chain runs 1, 2, 3, 4, 5, 6, 7 in order: his
       five lines, the transform between the two Trunks lines, and then word 7, the standard four-op
       battle start on track 35. `ext 104` re-arms Cell from the plateau's own enemy item, the bar
       shows the BOTTOM HALF, the HUD comes back and camera_follow(0) hands the view over. That
       re-arm is vanilla's own multi-round wiring (B0832), and table D already runs vanilla TEXT
       records from words 24 and 25, so a text record in this table is not a new thing. See TALK.

    Next TALK_WORDS[0] = Cell's first line."""
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
    load = (fade_out(SPLIT_FADE)
            + call("load_map_at", PLATEAU_ZONE, PLATEAU_AREA, MAP_VARIATION, *PLATEAU_FLY_FROM))
    stage = (ext(52, CELL_SET) + ext(51, CELL_SET, *PLATEAU_CELL_SPOT)
             + ext(55, CELL_SET, WEST) + ext(57, CELL_SET, DOWN_STATE)
             + ext(55, PLAYER, EAST) + ext(121, PLAYER, FLY_STATE)
             + ext(31, *PLATEAU_VIEW))
    land = (fade_in(SPLIT_FADE) + wait(ARRIVE_BEAT)
            + ext(136, PLAYER, *PLATEAU_TRUNKS_SPOT, ARRIVE_SPEED)
            + ext(55, PLAYER, EAST) + wait(ARRIVE_BEAT)
            + ext(121, CELL_SET, STAND_STATE) + ext(55, CELL_SET, WEST) + wait(ARRIVE_BEAT))
    return code(TALK_WORDS[0], head, close, punch, follow, load, stage, land)


def talk_line(index: int, portrait: int, line: str) -> bytes:
    """One line of the plateau talk, type 1, the shape of the vanilla Cell talk's own lines.

    The words are the owner's, quoted in TALK. The record hands on to the next index, so the five
    lines and the transform run in the order he wrote them."""
    return text(index + 1, portrait, line)


def transform() -> bytes:
    """Word 3: "Trunks transforms to Super Saiyan if he is not already" (the owner, section 4).

    This is future_androids' own word 4, which the owner has already play tested, with ONE op added
    in front. Its shape:

        ext 73 (3, 132) ; sound(55) ; pose(0, 9) ; palette_fx(10) ; sound_stop(55)
        ; ext 73 (3, 133) ; flash_wait(10) ; face(0, EAST)

    `ext 57` BLOCKS (future_androids reads the handler and Queue_Append in full), so all 160 frames
    of player state 9 play before the swap. The white flash is the COVER: `ext 42 (10)` fades to white
    and `ext 43 (10)` fades back, so the body changes while the screen is white (B1978).

    THE LEADING `ext 73 (3, 132)` IS THE "if he is not already". No scene op reads the player's
    current form, so the record cannot branch on it. It does not need to: `ext 73` sets the player
    sprite from the raw set id (B0424), so setting 132 first makes the base body certain whatever the
    player did in round 1. That matters, because **only the base set carries anim 9**: set 132 has
    anims 0-9 and set 133 does not (B2179, walked on the base ROM). A power up posed on 133 would ask
    for an animation that is not there. A player who never transformed sees no change at all, because
    he is already 132; a player who did sees his aura drop for the frames before the pose starts, and
    then power up again, which is the beat the owner asked for either way.

    `ext 73` on a live leader is CONFIRMED: `sub_0800A8EC` writes the new set into the character
    record and then rebuilds the LIVE object when that character leads. Trunks leads here.

    The closing `ext 55` restores the facing by hand. He has faced EAST since he landed, and an op
    that rebuilds the body is not worth trusting with a facing byte."""
    return code(TRANSFORM_INDEX + 1,
                ext(73, TRUNKS_PARTY, BASE_TRUNKS),
                call("sound", AURA_SOUND),
                ext(57, PLAYER, POWER_UP),
                call("palette_fx", WHITE),
                call("sound_stop", AURA_SOUND),
                ext(73, TRUNKS_PARTY, SSJ_TRUNKS),
                call("flash_wait", WHITE),
                ext(55, PLAYER, EAST))


def round2(enemy_item: int) -> bytes:
    """The record that starts round 2: track 35, then the standard four-op battle start.

    It had to leave record S, because record S now ends in a conversation and a type 0 record cannot
    carry text. Nothing is left for this record to do: the load, the staging, the camera and the
    talk all happened before it, which is exactly the state the four-op shape asks for.

    `music(35)` opens it. The owner, section 4: "Track 35 starts as the fight starts", and he changed
    the number himself: "track 35 instead of 15". A music op breaks none of the six battle-start
    rules, which read map loads, fades, the camera, the HUD and the sets a record names."""
    return code(END_INDEX, call("music", ROUND2_MUSIC),
                battle_start(enemy_set=CELL_SET, enemy_item=enemy_item,
                             bar=CELL_SET, bar_range=ROUND2_BAR))


def plateau_npc_item(arena_npc: bytes, step_at: int) -> bytes:
    """The plateau's NPC Imperfect Cell: battle_arena's own item, moved onto the fight spot.

    The arena builds its NPC on CELL_START and the vanilla talk walks him to CELL_SPOT. Nothing walks
    him here, so the item carries PLATEAU_CELL_SPOT itself, the right hand spot of the left to right
    pair. Condition and set are battle_arena's, so the map load builds him. Record S then removes
    this NPC and spawns a plain one on the same spot, because an item carries a step struct and a
    step struct can argue with a scripted pose; the item still stands him in the right place if the
    record is ever skipped, and `ext 104` has an actor of set 28 to replace either way."""
    item = bytearray(arena_npc)
    item[N_AT:N_AT + 4] = struct.pack("<hh", *PLATEAU_CELL_SPOT)
    item[N_STEP_LIST:N_STEP_LIST + 4] = _word(step_at + ROM_BASE)
    return bytes(item)


def plateau_enemy_item(arena_enemy: bytes, event_at: int, tail_at: int) -> bytes:
    """The plateau's enemy Imperfect Cell: battle_arena's own item with its OWN event struct.

    Everything else is carried, so round 2 is the same type 60 at HP 5210 with AI 80 and the boss
    descriptor. Only the death event differs, and that is the whole point: round 1's death splits the
    fight and round 2's ends it."""
    item = bytearray(arena_enemy)
    item[ITEM_AT:ITEM_AT + 4] = struct.pack("<hh", *PLATEAU_CELL_SPOT)
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
    seed = (PLATEAU_CELL_SPOT[0] // 8, PLATEAU_CELL_SPOT[1] // 8)
    if seed not in opened:
        raise ValueError(f"Cell's own cell {seed} is closed on {MAP_DOC.name}, so round 2 would open"
                         f" with him standing in a wall")
    reach = reachable(opened, seed)
    art = art_cells(doc)
    for spot, env, who in PLATEAU_SPOTS + DEATH_SPOTS:
        for cx, cy in envelope_cells(spot, env):
            if (cx, cy) not in reach:
                raise ValueError(f"{who} at {spot} draws into ({cx},{cy}), which is closed or sealed"
                                 f" off on {MAP_DOC.name}")
            if (cx, cy) in art:
                raise ValueError(f"{who} at {spot} draws into ({cx},{cy}), where BG0 or BG1 art"
                                 f" stands OVER him on {MAP_DOC.name}: his body would be hidden")

    # The fly-in lane. He flies west to east along one row, so every step of it has to be walkable,
    # clear of the sealed pocket and clear of the art that draws over him.
    for spot in fly_lane(doc):
        for cx, cy in envelope_cells(spot, TRUNKS_ENVELOPE_LR):
            if (cx, cy) not in reach or (cx, cy) in art:
                raise ValueError(f"the fly-in lane puts Trunks at {spot}, which draws into"
                                 f" ({cx},{cy}): closed, sealed off, or under art that covers him")

    # The camera stops at the world edge, so walkable ground there would let him walk into nothing.
    edge = [c for c in opened if c[0] == 0 or c[1] == 0
            or (c[0] + 1) * 8 >= world[0] or (c[1] + 1) * 8 >= world[1]]
    if edge:
        raise ValueError(f"{len(edge)} walkable cells touch the {world[0]} x {world[1]} px world"
                         f" edge, for example {sorted(edge)[:4]}")

    # Both views the split parks have to be inside HIS camera bound, or the clamp moves them and the
    # pair is not framed where it was drawn. The load centres the view at (x - 112, y - 76).
    for view, where in ((PLATEAU_VIEW[:2], "the parked plateau view"),
                        ((PLATEAU_FLY_FROM[0] - 112, PLATEAU_FLY_FROM[1] - 76),
                         "the view the load centres")):
        if not (0 <= view[0] <= clamp[0] and 0 <= view[1] <= clamp[1]):
            raise ValueError(f"{where} {view} is outside his camera bound {clamp}: the clamp would"
                             f" move it, so the pair would not be framed where the record puts them")

    # LEFT TO RIGHT, and Trunks really off screen at the reveal (the owner, 2026-11-08).
    if PLATEAU_TRUNKS_SPOT[1] != PLATEAU_CELL_SPOT[1]:
        raise ValueError(f"Trunks {PLATEAU_TRUNKS_SPOT} and Cell {PLATEAU_CELL_SPOT} are not on one"
                         f" row, so they would not face each other left to right")
    if not 0 < PLATEAU_CELL_SPOT[0] - PLATEAU_TRUNKS_SPOT[0] == PLATEAU_GAP:
        raise ValueError(f"Cell must stand {PLATEAU_GAP} px EAST of Trunks, and he stands"
                         f" {PLATEAU_CELL_SPOT[0] - PLATEAU_TRUNKS_SPOT[0]} px away")
    if PLATEAU_FLY_FROM[0] >= PLATEAU_TRUNKS_SPOT[0] or PLATEAU_FLY_FROM[1] != PLATEAU_TRUNKS_SPOT[1]:
        raise ValueError(f"the fly-in starts at {PLATEAU_FLY_FROM}, which is not due WEST of"
                         f" {PLATEAU_TRUNKS_SPOT}: he would not fly in from the left")
    if PLATEAU_FLY_FROM[0] + TRUNKS_ENVELOPE_LR[1] >= PLATEAU_VIEW[0]:
        raise ValueError(f"at {PLATEAU_FLY_FROM} Trunks reaches x"
                         f" {PLATEAU_FLY_FROM[0] + TRUNKS_ENVELOPE_LR[1]}, which is not left of the"
                         f" parked view {PLATEAU_VIEW[:2]}: he would already be on screen")
    for spot, env, who in PLATEAU_SPOTS[:2]:
        left, right = spot[0] - env[0], spot[0] + env[1]
        top, bottom = spot[1] - env[2], spot[1] + env[3]
        if (left < PLATEAU_VIEW[0] or right > PLATEAU_VIEW[0] + VIEW[0]
                or top < PLATEAU_VIEW[1] or bottom > PLATEAU_VIEW[1] + VIEW[1]):
            raise ValueError(f"{who} at {spot} draws x {left}..{right} y {top}..{bottom}, outside the"
                             f" parked plateau view {PLATEAU_VIEW[:2]} plus {VIEW}: his frame is cut")

    # The rest is the SPLIT's own px arithmetic on map 6,100 and does not read his map at all.
    for spot, who, up, down in ((CELL_SPOT, "Cell", ENVELOPE[2], ENVELOPE[3]),
                                (TRUNKS_SPOT, "Trunks", TRUNKS_UP, TRUNKS_DOWN),
                                (PUNCH_FROM, "Trunks at the punch", TRUNKS_UP, TRUNKS_DOWN)):
        top, bottom = spot[1] - up, spot[1] + down
        if top < SPLIT_VIEW[1] or bottom > SPLIT_VIEW[1] + VIEW[1]:
            raise ValueError(f"{who} at {spot} draws {top}..{bottom}, outside the arena view"
                             f" {SPLIT_VIEW[:2]} plus {VIEW[1]}: his frame would be cut")
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
            "static_tiles": len(doc["tiles"]), "groups": len(doc.get("animated") or []),
            "art_cells": len(art), "art_over_walkable": len(art & reach),
            "fly_lane_px": PLATEAU_TRUNKS_SPOT[0] - PLATEAU_FLY_FROM[0]}


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
    if ({PLATEAU_CELL_SPOT, PLATEAU_TRUNKS_SPOT, PLATEAU_FLY_FROM}
            != {spot for spot, _env, _who in PLATEAU_SPOTS}):
        raise ValueError(f"PLATEAU_SPOTS is {[s for s, _e, _w in PLATEAU_SPOTS]}, and round 2 opens"
                         f" with Cell at {PLATEAU_CELL_SPOT}, Trunks at {PLATEAU_TRUNKS_SPOT} and"
                         f" the fly-in starting at {PLATEAU_FLY_FROM}")
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

    There are four kinds: the map table literals and the count byte, which is how each relocation
    hands the table on; ending table word 23, which moves from ending_fight's record F to record R;
    word 0 of ending_fight's table D, which moves from record K to record S; and words 1 to 7 of that
    same table, which were END words and now carry the owner's own plateau talk, the transform and
    round 2's battle start. Record A is NOT here any more, because rung 5 leaves it loading the arena."""
    expected = {(lit, 4) for lit in BASE_LITERALS} \
        | {(ENTRY3_LITERAL, 4), (MAP_COUNT_BYTE, 1), (table_d, 4)} \
        | {(table_d + 4 * k, 4) for k in TALK_CHAIN} \
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
                f"the plateau NPC Cell (set {CELL_SET}, cond 0, on {PLATEAU_CELL_SPOT})")
    enemy = place(plateau_enemy_item(bytes(rom[arena_notes["item"]:
                                               arena_notes["item"] + ITEM_SIZE]), event2, tail),
                  "the plateau enemy (Imperfect Cell, cond 1, its OWN death event)")
    items = place(_word(npc + ROM_BASE) + _word(enemy + ROM_BASE),
                  f"the plateau item list ({ARENA_ITEMS} items: the NPC, then the enemy)")

    rnd1 = place(round1(ENEMY_INDEX), "record R (round 1 on the arena, the TOP half of the bar)")
    boundary = place(split(ENEMY_INDEX),
                     "record S (ping, flash, Cell punched off screen, Trunks flies after him, the"
                     " plateau loads, Cell lies down, Trunks flies in from the west and lands, and"
                     " Cell stands up)")
    talk = [place(talk_line(index, portrait, line),
                  f"the owner's line for portrait {portrait} (table D word {index})")
            for index, portrait, line in TALK]
    change = place(transform(),
                   f"record X (Trunks powers up to Super Saiyan, table D word {TRANSFORM_INDEX})")
    rnd2 = place(round2(ENEMY_INDEX),
                 f"record T (round 2 starts: the standard battle start with the BOTTOM half of the"
                 f" bar, table D word {ROUND2_INDEX})")

    # THE MAP IS HIS, and import_map lays it: the four BG layer records, one frame per DISTINCT
    # block, the collision and terrain frames, the tile stream, the animated tile groups, the 0x50
    # byte layout with the camera pair COMPUTED from his world, the appended map table and the five
    # table hand-offs. This module writes no tile and no collision bit of its own.
    rom[:] = import_map.apply(bytes(rom), doc, PLATEAU_ZONE, PLATEAU_AREA, music=PLATEAU_MUSIC,
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

    # The entry becomes the LIVE arena entry with four words changed, so map 7,100 keeps the arena's
    # combat, banner and 2 item list, and names its OWN items, the layout import_map wrote and the
    # song already playing when the split loads it.
    put(entry_at, plateau_entry(arena, layouts, items),
        f"the map {PLATEAU_ZONE},{PLATEAU_AREA} entry (the live {ARENA_ZONE},{ARENA_AREA} entry with"
        f" the zone, the item list, the layout array and the music word changed)")

    for word in fight_words:
        where = ("the ending table" if word == FIGHT_WORD
                 else "an android's copy of the ending table")
        put(word, _word(rnd1 + ROM_BASE), f"{where} word {FIGHT_INDEX} (record R, round 1)")
    put(table_d, _word(boundary + ROM_BASE),
        "table D word 0 (record S: round 1's death is now the split, not the end of the fight)")
    for index, at in zip(TALK_WORDS + (TRANSFORM_INDEX, ROUND2_INDEX), talk + [change, rnd2]):
        put(table_d + 4 * index, _word(at + ROM_BASE),
            f"table D word {index} (the arrival talk, the transform and round 2's battle start,"
            f" which were END)")
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
        "talk": talk, "talk_words": TALK_WORDS, "round2": rnd2, "round2_word": ROUND2_INDEX,
        "transform": change, "transform_word": TRANSFORM_INDEX,
        "round1_music": ROUND1_MUSIC, "round2_music": ROUND2_MUSIC, "plateau_music": PLATEAU_MUSIC,
        "fight_words": sorted(fight_words),
        "round1_bar": ROUND1_BAR, "round2_bar": ROUND2_BAR,
        "cell_spot": CELL_SPOT, "trunks_spot": TRUNKS_SPOT,
        "plateau_cell_spot": PLATEAU_CELL_SPOT, "plateau_trunks_spot": PLATEAU_TRUNKS_SPOT,
        "fly_from": PLATEAU_FLY_FROM, "plateau_view": PLATEAU_VIEW,
        "art_cells": design["art_cells"], "art_over_walkable": design["art_over_walkable"],
        "fly_lane_px": design["fly_lane_px"],
        "sites": sorted(sites)}
