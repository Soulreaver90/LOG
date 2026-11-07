r"""
future_androids.py - Trial patch: the ending's scripted beatings of FUTURE Android 18 and FUTURE
                     Android 17 become two real player fights, one after the other, on a clone of
                     map 1,2. Trunks is the player from the moment the scene reaches that map.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_future.txt --out <new .gba>
Input:   the ROM after build_list_trial_ending.txt (dev r41, battle_arena, ending_fight). It must run
         AFTER battle_arena, whose map table copy it appends to, and AFTER ending_fight, which checks
         that ending words 0, 4, 6, 8 and 11 are still vanilla when it runs.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["future_androids"], every write as
         (offset, length, name) in its "sites".
Method:  Ending scene table rom:0x3B8140. Word 8 is the scripted beating of set 11 (Android 18) and
         word 11 the scripted beating of set 9 (Android 17), the same shape as word 23, which
         ending_fight already turned into a real fight. The owner's sequencing, 2026-11-07: "make sure
         they are individual fights, he fights 18 first, then cutscene, then 17, then cutscene, then
         fades to the cell sequence we just made".
         1. Map 1,2 is CLONED into a new entry, map 1,100. Map 1,2 itself is never written, because the
            PROLOGUE plays on it: its one region rom:0x3ED7DC has condition 0 and a step trigger over
            rect (-15,-7)-(360,584) that fires scene table rom:0x3B7ADC. A real fight lets the player
            walk, and crossing x 360 would fire the prologue. The clone carries 0 regions, so it holds
            no path to that table at all. See _check_prologue.
         2. The clone also drops map 1,2's one layout door to map 2,22 (rect (144,280)-(273,305)) and
            its banner. A map carries doors in TWO carriers: entry +0x10 and layout +0x40/+0x44. The
            clone zeroes both, which is what the arena learned after shipping three times with doors.
         3. The clone's items are map 1,2's NPC Android 18 (set 11) and NPC Android 17 (set 9), each
            at condition 0, plus TWO enemy items at condition 1: Android 18 (type 4) and Android 17
            (type 3). Condition 1 is "never at load", so neither enemy exists until its own fight
            record runs `ext 104`. During fight 1 Android 17 is still the NPC and is not attackable.
            That pairing is VANILLA, not a design of ours: map 11,4 is a combat map carrying NPC set 9
            (item 0, cond 0) beside enemy type 3 set 9 (item 1, cond 1), while NPC set 11 and NPC
            set 8 stand through the whole Piccolo fight as plain NPCs.
         4. TWO of map 1,2's four NPC items are DROPPED, by the same mechanism: the item is never
            built, and the clone's own item indices close up behind it.
            NPC Trunks (item 3, set 132) goes because the PLAYER replaces him. Two actors of one set
            would make every op that names set 132 or 133 ambiguous (blocker B2), so the clone carries
            exactly one Trunks and it is the player.
            NPC Future Gohan (item 0, set 54, at (216,368)) goes because the owner asked for him off
            this map on 2026-11-07: he stands in the street and nothing drives him. Two independent
            searches of the whole ending span rom:0x3B7B08 to rom:0x3B8140 found no op naming set 54,
            a decode of the 13 code records and a raw byte scan for `push 54 ; ext N` and a zigzag 54
            push_list head. His step struct only parks him. A record outside that span, or an op that
            computes 54 instead of pushing it, would not appear in either search.
         5. Word 0 is repointed at a copy that keeps every vanilla op and changes six things: the map
            load becomes `ext 39` on the clone so a player is built, `ext 73` and `ext 70` in front of
            it make Trunks the leader in his BASE set, the three ops that drove NPC set 132 now drive
            set 0, and a camera park plus `fade_in` replace the reveal that `ext 35` used to do by
            itself. See arrive().
         6. Word 4 is the transformation. Vanilla removes NPC 132 and spawns NPC 133; the copy poses the
            PLAYER in state 9 and changes his body with `ext 73 (3, 133)` under a white flash. The shape
            is `cellgames_ssj.GOKU_TRANSFORM`, which already ships and which the owner approved.
            `ext 57` BLOCKS: `sub_08009FC4` ends in `BL Queue_Append @0x0800E04C`, and Queue_Append runs
            `BL 0x0801F2F4`, the frame loop, whenever the group flag is 0 (bible B0604, B1775). So all
            160 frames of state 9 (B0605) play, the state plays sound 23 itself when it ends, and only
            then do the flash and the swap run. `ext 42` and `ext 43` are a fade to white and a fade back
            from it (B1978), so the body changes while the screen is white. Vanilla's closing `sound(23)`
            is DROPPED, because state 9 has just played it. The swap is CONFIRMED in `sub_0800A8EC`: the
            handler writes the new set into the character record and then, when the live player object
            pointer is not null (`CMP r4,#0 ; BEQ loc_0800A96C`), rebuilds that object's body in place.
            The same guard is why the `ext 73` in word 0 only writes the record: no player exists yet.
         7. Words 8 and 11 become the four op battle start `scene_lib.battle_start()` emits, the shape
            25 of the 25 vanilla bar records use. No fade and no map load: the talk already stands on
            the fight's own ground, which is the defect the owner rejected on 2026-11-06.
         7a. THE DEATH BEATS (rung 4, 2026-11-07). Each death record now carries the owner's own beat:
            "18 fight -> she collapses -> Trunks blasts her, NO transition". The record poses her down,
            holds, turns Trunks to her, fires `ext 96` with the PLAYER as attacker, polls `ext 60`
            until the blast lands and removes her. It carries NO fade, NO camera op, NO `ext 62` and
            no map load, so the scene never leaves the ground the fight ended on. Android 18's record
            then brings Android 17 in. The engine has no "is this actor on screen" op, so the record
            unpacks the player's spot (`ext 143`), works out where the view is, and either leaves 17
            standing, walks him from where he stands, or drops him just outside the left edge of the
            view with `ext 62` and walks him 96 px in. See approach(), blast() and death().
         8. Each enemy's death event table is a COPY OF THE LIVE 27 WORD ENDING TABLE with word 0 set
            to its own death record. The copy is taken AFTER words 8 and 11 are written, so Android
            18's table carries the real Android 17 fight at word 11, and both carry ending_fight's own
            words 13 and 23. Every record's next index then resolves to the record the ending would
            have run. 18's death record hands back at word 9 and 17's at word 12.
         9. The map table is relocated a SECOND time. battle_arena already moved it and appended map
            6,100; this module reads the LIVE base from the literal rom:0xEBD8 and the LIVE count from
            rom:0xE0AE, copies every live entry and appends map 1,100.
Rules:   Every source byte is checked before the first write; a second run raises. No vanilla map
         entry, item, enemy item, event struct or enemy type is written, so the main game's Android 17
         and 18 fights on maps 11,4 to 11,6 and map 8,49 keep every byte. The two enemy items are
         fresh copies with their OWN event struct and tail, so writing a death table cannot reach the
         vanilla struct the main game names.
         The four base writes are ending table words 0, 4, 6, 8 and 11, the four map table literals
         and the map count byte. The literals and the count byte are the ONE overlap with battle_arena
         and are excluded from the overlap guard by name; everything else must be untouched.
         No loss handling is added: a loss runs the vanilla game-over table, as the ending fight does.
"""
import hashlib
import struct

from scene.scene_lib import (battle_start, call, camera, code, ext, fade_in, leader, face, pose, push,
                             record_end, relocate, remove, wait, walk_to, words_naming)

# ===== constants: the map table, read LIVE (battle_arena has already moved it) =====
ROM_BASE = 0x08000000
MAP_SIZE = 56
MAP_BASE_LITERAL, MAP_COUNT_BYTE = 0xEBD8, 0xE0AE   # where a build's own table base and count live
BASE_LITERALS = (0x5ADC, 0x5D5C, 0xEBD8)            # the 3 words that name the table base
ENTRY3_LITERAL, ENTRY3 = 0x195C, 3                  # a 4th literal names entry 3 (map 1,4) directly
COUNT_FN = 0xE0AC                                   # sub_0800E0AC: MOV r0,#0xFF ; ADD r0,#n ; BX lr
# The count byte rom:0xE0AE is the `n` INSIDE that code, so the pin is split around it: two bytes
# before it and three after, and the byte itself is checked against the live entry count instead.
COUNT_CODE_HEAD, COUNT_CODE_TAIL = bytes.fromhex("ff20"), bytes.fromhex("307047")
# The 4 literals and the count byte are the ONE place battle_arena and this module write the same
# bytes, by design: each relocation hands the table on through them. They are not in the guard list.

# Entry fields (bible OVW). A count byte is zero exactly when its list word is zero, in all 327.
F_VARIATIONS, F_REGION_COUNT, F_ITEM_COUNT = 2, 3, 4
F_COMBAT, F_BANNER, F_REGIONS, F_ITEMS = 8, 0x0C, 0x10, 0x14
F_SWAPS, F_PICKUPS, F_MARKERS, F_MUSIC = 0x18, 0x1C, 0x20, 0x24
F_VAR_SCRIPT, F_LAYOUTS, F_ENTER, F_LEAVE = 0x28, 0x2C, 0x30, 0x34

# ===== constants: map 1,2, the source (base bytes, 01_probe.py) =====
SOURCE_ZONE, SOURCE_AREA = 1, 2
SOURCE_ENTRY = bytes.fromhex("01020101" "04000000" "01000000" "e5000000" "f0d73e08" "ccd73e08"
                             "00000000" "00000000" "00000000" "3cd73e08" "00000000" "48d73e08"
                             "00000000" "00000000")
SOURCE_MUSIC = 0x083ED73C          # +0x24: a SCRIPT, `test_flag(196) ; jz(3) ; push 38 ; end`, so it
                                   # returns song 38 under flag 196. The clone must NOT copy it. See
                                   # WALK_IN_MUSIC: vanilla's ext 35 load never reads +0x24 at all.
WALK_IN_MUSIC = 42                 # the song record 0 starts at rom:0x3B7B0B and the one playing at the
                                   # load. CONFIRMED that vanilla never changes it here: `Map_Load`
                                   # @0x0800C664, the ext 35 path, does not call `sub_0800C390` and so
                                   # never reaches the +0x24 read at `loc_0800C4D6`. Only `sub_0800C584`,
                                   # the ext 38 and ext 39 path, calls it (`BL loc_0800C390`). So an
                                   # ext 39 load DOES read +0x24, and naming the script would start the
                                   # Android theme under the black, 11 ops before vanilla's own cue.
                                   # Naming 42 instead makes the read a no-op: `loc_0800C4F4` runs
                                   # `LDRB r2,[r0,#0x5] ; CMP r2,#1 ; BNE` and `LDR r2,[r0,#0xC] ;
                                   # CMP r2,r1 ; BEQ`, which skips `music_play` when that exact record
                                   # is already playing. Record 0's closing `music(38)` then cues on time.
SOURCE_LAYOUTS, SOURCE_LAYOUT = 0x3ED748, 0x6ACB68
LAYOUT_SIZE = 0xCC                 # battle_arena's measure: the closest pair of layout addresses is 204
L_BG0, L_BG1, L_BG2, L_BG3 = 0x14, 0x18, 0x1C, 0x20
L_PROP_COUNT, L_PROP_LIST, L_COLLISION = 0x24, 0x28, 0x34
L_WARP_COUNT, L_WARP_LIST = 0x40, 0x44
SOURCE_LAYERS = (0x6A9800, 0x6AA638, 0x6AB2E4, 0x6AC72C)      # BG0 to BG3
SOURCE_PROPS, SOURCE_PROP_LIST, SOURCE_COLLISION = 1, 0x6AC960, 0x6AC7BC
SOURCE_WARPS, SOURCE_WARP_LIST, SOURCE_DOOR = 1, 0x6ACB64, 0x6ACB4C   # -> map 2,22 at (128,116)

# The PROLOGUE chain, one word at each link. The clone breaks it by carrying no region list at all.
PROLOGUE_TABLE, SOURCE_REGION_ITEM, SOURCE_REGION_LIST = 0x3B7ADC, 0x3ED7DC, 0x3ED7F0
REGION_ITEM_TABLE_AT, REGION_LIST_POINTER_AT = 0x10, 4        # item +0x10 names the table; list +4 the item

# Map 1,2's four NPC items and the step struct each one names at +0x14. An NPC item is 0x18 bytes:
# u32 factory, u32 condition, s16 x, s16 y, u32 set, u32 step count, u32 step struct.
NPC_FACTORY = 0x0800D6DF
NPC_ITEM_SIZE, N_COND, N_AT, N_SET, N_STEPS, N_STEP = 0x18, 4, 8, 0xC, 0x10, 0x14
SOURCE_NPCS = (                    # (item offset, item bytes, step offset, step bytes)
    (0x3ED754, bytes.fromhex("dfd60008" "00000000" "d8007001" "36000000" "01000000" "4cd73e08"),
     0x3ED74C, bytes.fromhex("0fcb0008" "007d0100")),         # set 54, Future Gohan: DROPPED
    (0x3ED774, bytes.fromhex("dfd60008" "c4000100" "d8019801" "0b000000" "01000000" "6cd73e08"),
     0x3ED76C, bytes.fromhex("0fcb0008" "007d0000")),         # set 11, Android 18, at (472,408)
    (0x3ED794, bytes.fromhex("dfd60008" "c4000100" "08029801" "09000000" "01000000" "8cd73e08"),
     0x3ED78C, bytes.fromhex("0fcb0008" "007d0000")),         # set 9, Android 17, at (520,408)
    (0x3ED7B4, bytes.fromhex("dfd60008" "c4000100" "f0018802" "84000000" "01000000" "acd73e08"),
     0x3ED7AC, bytes.fromhex("0fcb0008" "007d0100")),         # set 132, NPC Trunks: DROPPED
)
GOHAN, A18, A17, TRUNKS_NPC = 0, 1, 2, 3                      # indices into SOURCE_NPCS
# GOHAN and TRUNKS_NPC are checked and guarded like the rest, and never built onto the clone.
COND_ALWAYS, COND_NEVER_AT_LOAD = 0, 1                        # condition_eval @0x08003F06

# celljr_fight's step: face the player, 32000 frames. The owner: "17 will face the player like Cell
# did in the cell jr fight". It does not run while a scene plays, and it reads the LIVE player, so it
# decides again once he takes control; 17 may turn during his own fight. That limit is celljr's too.
FACE_PLAYER = bytes.fromhex("99000108" "007d0000")            # step @0x08010098 (tick @0x08010038)

# ===== constants: the two vanilla enemy items, copied as TEMPLATES and never written =====
# An enemy item is 0x20 bytes: u32 factory, u32 condition, u32 type, s16 x, s16 y, u32 set,
# u32 event struct, u32, u32 step struct. The event struct is {event runner, death scene table}.
ENEMY_FACTORY, EVENT_RUNNER = 0x0800E77F, 0x080106B3
ITEM_SIZE, ITEM_COND, ITEM_TYPE, ITEM_AT, ITEM_SET, ITEM_EVENT, ITEM_TAIL = 0x20, 4, 8, 0xC, 0x10, 0x14, 0x1C
EVENT_TABLE_AT = 4
A18_TYPE, A17_TYPE = 4, 3
TEMPLATES = {                      # set: (item offset, item bytes, event offset, event bytes, tail offset, tail bytes)
    11: (0x4033A4, bytes.fromhex("7fe70008" "01000000" "04000000" "18010801"
                                 "0b000000" "9c334008" "01000000" "94334008"),
         0x40339C, bytes.fromhex("b3060108" "ac983d08"),
         0x403394, bytes.fromhex("0fcb0008" "007d0000")),     # map 8,49 item 0, Android 18, type 4
    9: (0x406494, bytes.fromhex("7fe70008" "01000000" "03000000" "0801c000"
                                "09000000" "8c644008" "01000000" "84644008"),
        0x40648C, bytes.fromhex("b3060108" "f0493e08"),
        0x406484, bytes.fromhex("0fcb0008" "007d0300")),      # map 11,4 item 1, Android 17, type 3
}
ENEMY_TABLE, ENEMY_ENTRY = 0x6D56AC, 24
TYPES = {4: bytes.fromhex("00000000" "5e0b0000" "15000000" "1d221b80" "80000000" "c4f36f08"),   # HP 2910 AI 21
         3: bytes.fromhex("00000000" "de0d0000" "15000000" "20272280" "80000000" "c4f36f08")}   # HP 3550 AI 21

# ===== constants: the ending (base bytes, 01_probe.py) =====
TABLE, TABLE_WORDS = 0x3B8140, 27
ARRIVE_INDEX, TRANSFORM_INDEX, NAME_INDEX = 0, 4, 6
FIGHT18_INDEX, AFTER18_INDEX = 8, 9
FIGHT17_INDEX, AFTER17_INDEX = 11, 12
END_INDEX = 26                                                # word 26 is END: the record hands control back
EDITED = (ARRIVE_INDEX, TRANSFORM_INDEX, NAME_INDEX, FIGHT18_INDEX, FIGHT17_INDEX)
RECORDS = {ARRIVE_INDEX: (0x3B7B08, "7e3656e7e865f08e5c51e39c43e6200bbde5536e"),
           TRANSFORM_INDEX: (0x3B7C1C, "187c73d2daaf5c9033b7645271924a3f3f6ca310"),
           NAME_INDEX: (0x3B7C6A, "e90bb11734eee488742f51c26532f4ac2e5c069c"),
           FIGHT18_INDEX: (0x3B7C96, "cfc1f6333ea5f82465738e3a05a15900df017cc1"),
           FIGHT17_INDEX: (0x3B7D6E, "65ddfc45540d206fb0248ece4349b01ca002e73e")}

# Record 0's op starts, read with scene_lib.ops in 01_probe.py. relocate() checks every one of them.
R0_LOAD = (0x3B7B64, "1d05020402860088500223")            # load_map(1,2,1,384,552), ext 35: no player
R0_FACE = (0x3B7B6F, "1d028208020237")                    # face(132,1)
R0_FOLLOW = (0x3B7B7A, "00840221")                        # camera_follow(132)
R0_WALK = (0x3B7B7E, "1d038208876087700235")              # walk(132,496,504)
# Record 4's op starts. Vanilla: wait(40) ; face(132,0) ; sound(55) ; pose(132,9) ; remove(132) ;
# spawn(133,496,504) ; sound(23). The copy keeps the pose and the two sounds and changes who they name.
R4_FACE = (0x3B7C23, "1d028208000237")                    # face(132,0)
R4_POSE = (0x3B7C2E, "1d028208120239")                    # pose(132,9), the transformation pose
R4_REMOVE = (0x3B7C35, "00840234")                        # remove(132): DELETED, the player stays
R4_SPAWN = (0x3B7C39, "1d03820a876087700233")             # spawn(133,496,504): becomes ext 73 on the player
R4_SOUND23 = (0x3B7C43, "0017022e")                       # sound(23): DELETED, state 9 plays it at its end
R6_FACE = (0x3B7C6D, "1d02820a020237")                    # face(133,1)

# ===== constants: the design =====
CLONE_ZONE, CLONE_AREA, CLONE_VARIATIONS = 1, 100, 1      # zone 1 uses areas 1 to 7, so 100 is free
CLONE_ITEMS = 4
NPC_18_ITEM, NPC_17_ITEM = 0, 1                           # item indices are POSITIONAL: a dropped NPC
ENEMY_18_ITEM, ENEMY_17_ITEM = 2, 3                       # closes the gap, and `ext 104` names these
PLAYER, TRUNKS = 0, 3                                     # set 0 is the player; Trunks' party id (ext 70)
TRUNKS_BASE, TRUNKS_SSJ = 132, 133                        # his base and Super Saiyan appearance sets
A18_SET, A17_SET = 11, 9
DOWN, UP = 0, 1                                           # ext 55 facings (celljr_fight and chapter_cards agree)
POWER_UP = 9                                              # player state 9: the power up animation, 160 frames
AURA_SOUND, FLASH = 55, 10                                # vanilla's own aura sound; GOKU_TRANSFORM's flash length
NO_BANNER = 0xDD                                          # entry +0x0C: `CMP r0,#0xDD ; BEQ` skips the banner
PLAYER_START = (496, 648)                                 # map 1,2 item 3's own spot: where NPC Trunks stood
TRUNKS_SPOT = (496, 504)                                  # where the vanilla walk leaves him, beside the pair
REVEAL_VIEW = (384, 552)                                  # vanilla's own ext 35 pair, read as the view origin
VIEW_SPEED = 2                                            # vanilla record 0's own camera speed
REVEAL = 180                                              # == record 0's own vanilla fade_out
COLLAPSE_HOLD = 60                                        # frames the body holds before the blast
DOWN_STATE = 3                                            # Android 18's own death record opens with pose(11,3)
HANDBACK_HOLD = 60                                        # the wait each vanilla beating ends on

# ===== constants: the death beats (rung 4) =====
A17_SPOT = (520, 408)                                     # SOURCE_NPCS[A17] +8: where NPC 17 stands and waits
BLAST_SPEED = 100                                         # vanilla's own n for a PLAYER blast, rom:0x3E523F

# ----- the approach: one path, measured in SCREEN space, not in map space -----
# The follow camera puts its origin at the player minus (112,80) and clamps it to the map (B1143,
# B1144), so every screen coordinate below is computable from the player's spot alone.
CAM_OFFSET, SCREEN = (112, 80), (240, 160)
# Android 17 enters ENTRY_INSET px OUTSIDE the left edge of the view and stops STOP_INSET px inside
# it. Both are measured from the camera origin, so the walk is the SAME 96 px every time, it always
# comes from the same side, and it always ends at the same point on screen: screen x 72, level with
# Trunks at screen x 112. That is the owner's "specific path or limited area", 2026-11-07.
ENTRY_INSET, STOP_INSET = 24, 72
A17_BOX = (8, 32)                 # his drawn box: 8 px either side of the anchor, 32 px above it
# The "he is already beside Trunks, so he just speaks" box. Unchanged from the build the owner
# play-tested. Deliberately smaller than the view, so the test errs toward bringing him in.
TALK_X, TALK_Y = 88, 52
# The player spots from which Android 17's DRAWN BOX has no pixel on screen, derived from A17_SPOT,
# A17_BOX, CAM_OFFSET and SCREEN. He is teleported only from inside this band, so the reposition can
# never be seen. Outside it he walks from where he stands, which is what the owner already approved.
GONE_X = (A17_SPOT[0] - A17_BOX[0] - SCREEN[0] + CAM_OFFSET[0] + 1,      # 385
          A17_SPOT[0] + A17_BOX[0] + CAM_OFFSET[0] - 1)                  # 639
GONE_Y = (A17_SPOT[1] - A17_BOX[1] - SCREEN[1] + CAM_OFFSET[1] + 1,      # 297
          A17_SPOT[1] + CAM_OFFSET[1] - 1)                               # 487

# The scene VM's four registers. `set_var n` (base op 3) writes slot n and `ext n` (n = 0 to 3) pushes
# it back: both resolve to 0x03001FB0 + 4n. CONFIRMED from sub_0800B058 to sub_0800B06A (the set_var
# slot table rom:0x3B5F70) and from sub_08009392 to sub_080093C8 (the ext 0 to ext 3 handlers).
# There are FOUR and no more: set_var 4 (sub_0800B070) writes through 0x03001FAC instead.
V_SPOT, V_PY, V_PX, V_FLAG = 0, 1, 2, 3
V_GONE = V_SPOT                   # the packed spot is finished with once V_PX and V_PY hold it
SIDE_STEP = 2 * 40                # the swing from the player's left to his right, 40 px either way
OR, ADD, SUB, MUL, DIV, GT, LT = (bytes([n]) for n in (5, 7, 8, 9, 10, 13, 15))
HALF = 1 << 16                                            # the packed spot's x multiplier


# ===== the new records =====

def arrive(rom: bytes, zone: int, area: int) -> bytes:
    """Word 0, the arrival on the androids' street: the CLONE loads here, with a player on it.

    Vanilla record rom:0x3B7B08 ends like this, and every op is kept:

        ... fade_out(180) ; load_map(1,2,1,384,552) ; face(132,1) ; wait(120) ; camera_follow(132)
        walk(132,496,504) ; camera(384,368,2) ; wait(60) ; face(9,2) ; wait(30) ; music(38)

    Four edits, each load bearing:

      1. `ext 39`, never `ext 35`. Only `ext 38` and `ext 39` reach `sub_0800C584` and through it the
         player constructor `sub_080086D4`; `ext 35` reaches `Map_Load @0x0800C664` only and builds no
         player at all, which is why the vanilla ending had none. `ext 73` and `ext 70` go in FRONT of
         the load, because `ext 70` writes the party roster and the map load is what builds the body
         from it. `ext 73` goes first because `appearance_revert` @0x08003ED4 skips the record whose
         index equals the leader byte `set_leader` has just written, so a form set on the character who
         BECOMES leader survives his own leader change. The form is TRUNKS_BASE: he is not Super
         Saiyan until word 4, which is the beat the vanilla scene plays.
         The load's pair is the PLAYER's position, not a view origin (`sub_08009A88`, CONFIRMED by
         ending_fight), so it is PLAYER_START, map 1,2 item 3's own spot, and the walk that follows is
         the walk vanilla gave the NPC.
      2. `face(132,1)` MOVES to behind vanilla's own wait(120) and becomes `face(0,1)`. Vanilla could
         face its NPC straight after the load because `ext 35` blocks until the load is done; `ext 39`
         does not, so an actor op in that gap runs before the player exists and is wiped (the v4
         finding ending_fight records). The wait is therefore the settle, and every actor op waits
         behind it.
      3. A camera park and a `fade_in` go in front of `camera_follow`. `ext 35` faded in by itself
         (`Map_LoadFromQueue @0x08009852`); `ext 39`'s handler has no such call, so the record must
         reveal itself. The park is vanilla's own (384,552), the pair `ext 35` was given, so the reveal
         frames the street the way vanilla framed it whatever that pair meant to `Map_Load`. `ext 31`
         BLOCKS (`sub_0800977A` publishes with `Scene_Publish` then runs `Handler_RunScoped`), so the
         travel finishes under the black and no travel wait is needed.
      4. `camera_follow(132)` and `walk(132,496,504)` become `camera_follow(0)` and `walk(0,496,504)`.
         There is no NPC Trunks on the clone to drive, and ops that name his set would bind the player
         anyway (blocker B2). The rest of the record, including `camera(384,368,2)`, `face(9,2)` and
         `music(38)`, is untouched vanilla."""
    rec, sha = RECORDS[ARRIVE_INDEX]
    length = record_end(rom, rec) - rec
    load = (call("header_bit1", 0) + ext(73, TRUNKS, TRUNKS_BASE) + leader(TRUNKS)
            + call("load_map_at", zone, area, CLONE_VARIATIONS, *PLAYER_START))
    reveal = (face(PLAYER, UP) + camera(*REVEAL_VIEW, VIEW_SPEED)
              + fade_in(REVEAL) + call("camera_follow", PLAYER))
    return relocate(rom, rec, length, {
        R0_LOAD[0]: (R0_LOAD[1], load.hex()),
        R0_FACE[0]: (R0_FACE[1], ""),
        R0_FOLLOW[0]: (R0_FOLLOW[1], reveal.hex()),
        R0_WALK[0]: (R0_WALK[1], walk_to(PLAYER, *TRUNKS_SPOT).hex()),
    })


def transform(rom: bytes) -> bytes:
    """Word 4, the Super Saiyan beat: the PLAYER powers up and changes form, where vanilla swapped NPCs.

    Vanilla rom:0x3B7C1C is `wait(40) ; face(132,0) ; sound(55) ; pose(132,9) ; remove(132) ;
    spawn(133,496,504) ; sound(23)`. The copy keeps the wait, the aura sound and the face, points the
    face and the pose at the PLAYER, deletes the remove, the spawn and the closing sound, and writes
    `cellgames_ssj.GOKU_TRANSFORM`'s own tail in their place:

        sound(55) ; pose(0,9) ; palette_fx(10) ; sound_stop(55) ; appearance(3,133) ; flash_wait(10)

    That shape already ships in the Cell Games entry and the owner approved it. Only the appearance op
    is retargeted, from Goku's (4,61) to Trunks' (3,133).

    `ext 57` BLOCKS. `sub_08009FC4` resolves the actor through `find_actor_by_set` @0x08009370,
    allocates a 0xC command and ends in `BL Queue_Append @0x0800E04C`. Queue_Append appends the
    command, then runs `LDR r0,[r0,#0] ; CMP r0,#0 ; BNE loc_0800E076 ; BL loc_0800DE20 ;
    BL loc_0801F2F4`: outside an ext 63/64 group the flag is 0 and the script enters the frame loop.
    So the script waits until the actor leaves the state (bible B0604; B1775 has the world ticking
    through that wait, and B1677 records the same reading). An earlier reading of this module called
    `ext 57` non-blocking because @0x0801F2F4 is not named inside @0x08009FC4. The call is one level
    down, in Queue_Append.

    Because it blocks, all 0xA0 = 160 frames of player state 9 play (B0605: enter @0x08011D38 sets
    anim 9, tick @0x08011D4A runs 160 frames, then plays sound 23 and the state ends). The state IS
    the animation, and dropping this op is what made Trunks change form in one frame. Vanilla's
    closing `sound(23)` is therefore deleted: state 9 has just played sound 23 itself, so keeping the
    op would ping it twice about 20 frames apart.

    The flash is not decoration, it is the cover. `ext 42 (10)` fades to white and `ext 43 (10)` fades
    back from it (B1978), so the body swap happens while the screen is white. The swap also has to
    land AFTER the pose: set 132 carries anim 9 and set 133 does not, so a swap during the state would
    leave the power up with no frames. Goku's pair is the same, 60 with anim 9 and 61 without, which
    is why the shipped record orders the ops this way. No extra `ext 69` hold is added: the record
    already holds 40 + 160 + 20 frames, and a wait after the fade from white would be dead air.

    `remove(132)` cannot stay: the player's own appearance set is 132 at this point, and an op that
    names a set binds the player object when his set matches (blocker B2), so the record would delete
    the player. `spawn(133)` cannot stay either: a second Super Saiyan Trunks would make every later
    op that names set 133 ambiguous.

    `ext 73` on a live leader is CONFIRMED, not assumed. `sub_0800A8EC` writes the new set into the
    character record through `loc_080042BC`, and then `CMP r4,#0 ; BEQ loc_0800A96C` guards a block
    that rebuilds the LIVE object: it resolves the new set, stores it at the object's +0x48, calls the
    object's own +0x28 vtable entry and then `loc_080086A2`. r4 is the live player pointer, loaded only
    when the character being changed is the current leader. Trunks is the leader from word 0 and the
    player object exists, so both conditions hold and the body changes on the spot."""
    rec, sha = RECORDS[TRANSFORM_INDEX]
    length = record_end(rom, rec) - rec
    power_up = pose(PLAYER, POWER_UP) + call("palette_fx", FLASH) + call("sound_stop", AURA_SOUND)
    swap = ext(73, TRUNKS, TRUNKS_SSJ) + call("flash_wait", FLASH)
    return relocate(rom, rec, length, {
        R4_FACE[0]: (R4_FACE[1], face(PLAYER, DOWN).hex()),
        R4_POSE[0]: (R4_POSE[1], power_up.hex()),
        R4_REMOVE[0]: (R4_REMOVE[1], ""),
        R4_SPAWN[0]: (R4_SPAWN[1], swap.hex()),
        R4_SOUND23[0]: (R4_SOUND23[1], ""),
    })


def name_line(rom: bytes) -> bytes:
    """Word 6, "...and this is for Gohan!!!": the one op turns the PLAYER, not the removed NPC."""
    rec, sha = RECORDS[NAME_INDEX]
    length = record_end(rom, rec) - rec
    return relocate(rom, rec, length, {R6_FACE[0]: (R6_FACE[1], face(PLAYER, UP).hex())})


def fight(enemy_set: int, enemy_item: int) -> bytes:
    """Word 8 or word 11: the four op battle start, and nothing else.

        ext104(set, item) ; bar_show(set) ; header_bit1(1) ; camera_follow(0)

    `ext 104` removes the live NPC of that set and builds the map's enemy item at his position and his
    facing, so Android 18 becomes hostile exactly where she stood. CONFIRMED from
    `Sprite_ReplaceWithEntry` @0x0800AAC6 and `Object_SpawnFromEntry` @0x0800C75C: the item is built by
    its OWN +0 factory with its own bytes, the only bound tested is the map's item count, and the
    item's condition is never read on this path. That is why the enemy items sit at condition 1 and
    the NPCs at condition 0.

    The bar is `ext 85 bar_show`, not `ext 90 bar_set`: each android is one round against her whole
    vanilla HP, and `ext 90`'s two extra values are a display segment for one round of a multi-round
    boss. No fade, no map load, no wait and nobody placed: word 0 settled the form, the leader, the
    spots and the camera, and nothing has moved since. Next 26 = END gives control."""
    return code(END_INDEX, battle_start(enemy_set=enemy_set, enemy_item=enemy_item, bar=enemy_set))


def var_read(slot: int) -> bytes:
    """Push scene variable `slot` (ext 0 to ext 3, reading 0x03001FB0 + 4n)."""
    return ext(slot)


def var_write(slot: int) -> bytes:
    """Pop the top value into scene variable `slot` (base op 3)."""
    return bytes([3, slot])


def jz(skip: int) -> bytes:
    """Base op 19: pop one value and jump `skip` bytes forward when it is zero."""
    if not 0 <= skip <= 0xFF:
        raise ValueError(f"a jz offset is one byte; {skip} does not fit")
    return bytes([19, skip])


def read_player() -> bytes:
    """Put the player's x and y in V_PX and V_PY, and the left-clamp flag in V_FLAG.

    `ext 143 (set)` resolves the actor through `Sprite_Select @0x08009370`, calls
    `Point_LoadScaled @0x0800791A` and pushes the two halves PACKED as `(x << 16) | (y & 0xFFFF)`.
    CONFIRMED from `sub_08009E80`. `Sprite_Select` answers set 0 with the live player object itself,
    and the player is a `mover` subclass, so his spot is at +0x158/+0x15C like every NPC's (B1710).

    Unpacking needs `div`, and the operand order is now CONFIRMED, not assumed. `sub_0800904A`
    fetches its two operands exactly as `sub_08009022` (sub) does, r0 from the TOP slot and r1 from
    the one below, and `@0x08021F30` returns r1 / r0 (B0502, B1966). So `a ; b ; div` is a / b, the
    same reading order as `a ; b ; sub`.

      V_PY = (spot * 65536) / 65536. The multiply is 32-bit, so the x half shifts straight out.
      V_PX = (spot - V_PY) / 65536. The low half is now zero, so no borrow can reach the high half.

    V_FLAG is 1 exactly when the camera is clamped against the LEFT map edge, which is the one clamp
    that can bite here: the camera origin is the player minus (112,80) held inside the map (B1143),
    map 1,100 is 1024x1280, and its open cells run x 16-744 and y 264-960, so the right clamp needs
    x >= 896 and the bottom clamp y >= 1200 and neither is reachable."""
    return (ext(143, PLAYER) + var_write(V_SPOT)
            + var_read(V_SPOT) + push(HALF) + MUL + push(HALF) + DIV + var_write(V_PY)
            + var_read(V_SPOT) + var_read(V_PY) + SUB + push(HALF) + DIV + var_write(V_PX)
            + var_read(V_PX) + push(CAM_OFFSET[0]) + LT + var_write(V_FLAG))


def outside(slot: int, lo: int, hi: int) -> bytes:
    """Leave 1 when variable `slot` is below `lo` or above `hi`, and 0 when it is inside.

    `lt` and `gt` test SECOND against TOP (`sub_080090CA`, `sub_08009096`), so the variable is
    pushed first and the bound second."""
    return (var_read(slot) + push(lo) + LT
            + var_read(slot) + push(hi) + GT + OR)


def screen_x(back: int, floor_x: int) -> bytes:
    """Leave `max(px - back, floor_x)` on the stack: a screen x turned back into a map x.

    The camera origin is `max(px - 112, 0)` here, so a point `k` px inside the left edge of the view
    is at map x `max(px - 112 + k, k)`, which is this with `back = 112 - k` and `floor_x = k`. The
    maximum is taken WITHOUT a jump, as `a + (floor - a) * flag`, because V_FLAG is already the one
    comparison both of this record's two call sites need: `px < 112` is the same test as
    `px - 112 + k < k` for every k."""
    a = var_read(V_PX) + push(back) + SUB
    return a + push(floor_x) + a + SUB + var_read(V_FLAG) + MUL + ADD


def own_side() -> bytes:
    """Leave `80` when Android 17 must stop on the player's RIGHT instead of his left, else 0.

    THE WALK MUST NOT CROSS TRUNKS. The stop is `px - 40`, which is Trunks' left, and on the arm
    where 17 is NOT teleported he starts from his own spot at x 520. So whenever the player stands
    left of 520 that walk goes straight through him. Measured on the v8 build: of the 177 open cells
    that take the walk-from-his-own-spot arm, the straight line passes within a sprite box of the
    player on 77. v7 had the mirror fault on 285 of its 5,476 walking cells.

    So that arm stops on the side he is already on: `px - 40 + 80 * (px < 520)`. The teleport arm
    always comes from the left edge of the view and always stops at `px - 40`, so the term is
    multiplied by `1 - V_GONE` and vanishes there."""
    return (push(SIDE_STEP) + var_read(V_PX) + push(A17_SPOT[0]) + LT + MUL
            + push(1) + var_read(V_GONE) + SUB + MUL)


def approach(npc_set: int) -> bytes:
    """Bring Android 17 to the same place on screen beside Trunks, from the same side, every time.

    THE OWNER'S DEFECT, 2026-11-07: "android 17 almost seemed to have walked off screen. When he
    approaches trunks, it should follow a specific path or limited area."

    The measured cause is NOT the stopping point. Over all 5,683 open cells of map 1,100 the build he
    played stopped 17 inside the view on every single one, even with a 24 px inset. What he saw was
    the WALK: it started at A17_SPOT and ran to the player wherever he was, a median of 304 frames,
    up to 552, and only 29 % of that straight line was ever inside the view. Android 17 spent about
    three and a half seconds of a five second walk outside the picture and then arrived at its edge.

    So the walk now starts just outside the left edge of the view and ends 72 px inside it:

      ENTRY  map x `max(px - 136, -24)`, the player's own row     (24 px outside the left edge)
      STOP   map x `max(px -  40,  72)`, the player's own row     (72 px inside it, 40 px from him)

    Both are camera-relative, so the walk is 96 px and about one and a half seconds every time, 17 is
    inside the view for all but the first 16 px of it, and he always comes from Trunks' left. When he
    is NOT teleported he keeps his own spot as the start, and `own_side()` moves the stop to whichever
    side of Trunks he is already on, so that walk never crosses him.

    The record branches twice, and both tests are on the player's spot, because Android 17 never
    moves off A17_SPOT until this record runs:

      1. `outside(TALK_X, TALK_Y)` - he is already beside Trunks, so he just speaks and does not
         move. That is the owner's rule of 2026-11-07 and the build he played already honoured it.
      2. `outside(GONE_X, GONE_Y)` - his DRAWN BOX has no pixel on screen, so `ext 62` may place him
         at the entry without anyone seeing it. When he IS on screen but not yet beside Trunks he
         walks from where he stands, which is a short walk inside one view and needs no teleport.

    `ext 62 (set, x, y)` is back in this record and it is NOT a transition. `sub_0800A44E` queues a
    16-byte command on the actor's own queue; its start `@0x0800E1DC` calls the actor's virtual +0x30,
    writes `x << 8` and `y << 8` to +0x158 and +0x15C, and calls +0x34. Its done slot is
    `@0x08026498`, `mov r0,#1 ; bx lr`, so it costs one frame and blocks nothing. It touches no
    camera, no fade, no facing and no animation, and it only ever runs while 17 is invisible.

    `ext 144` pops a set and a PACKED point and queues the very command `ext 53 walk` queues:
    `sub_08009EBA` and `sub_08009D4A` both end in `Record_NewFromWords(0, {x,y})` then
    `Queue_Append @0x0800E04C`, and the only difference is where the pair comes from. CONFIRMED.
    `sub_08009EBA` reads the pair with `asr r2,r1,#16` and `lsl r1,#16 ; asr r1,#16`, so the high
    half is a SIGNED x and the low half a signed y, which is why the stop is packed as
    `stop_x * 65536 + py` and never as a bit-wise or.

    Trunks turns to him at the end, on both paths. He has just fired at Android 18 and would
    otherwise be facing her death spot while 17 speaks from the other side."""
    enter = push(npc_set) + screen_x(CAM_OFFSET[0] + ENTRY_INSET, -ENTRY_INSET) + var_read(V_PY) + ext(62)
    walk = (push(npc_set)
            + screen_x(CAM_OFFSET[0] - STOP_INSET, STOP_INSET) + own_side() + ADD
            + push(HALF) + MUL + var_read(V_PY) + ADD + ext(144))
    gone = (outside(V_PX, *GONE_X) + outside(V_PY, *GONE_Y) + OR
            + var_write(V_GONE) + var_read(V_GONE))
    away = (outside(V_PX, A17_SPOT[0] - TALK_X, A17_SPOT[0] + TALK_X)
            + outside(V_PY, A17_SPOT[1] - TALK_Y, A17_SPOT[1] + TALK_Y) + OR)
    move = gone + jz(len(enter)) + enter + walk
    return (read_player()
            + away + jz(len(move)) + move
            + call("face_alt", npc_set, PLAYER)
            + call("face_alt", PLAYER, npc_set))


def blast(enemy_set: int) -> bytes:
    """Trunks blasts the body: he turns to it, fires, the script waits for the hit, the body goes.

    `ext 96 (attacker, target, n)` is the scene blast (bible B1963): at the fire tick it builds a
    projectile whose velocity is fixed toward the target's hurtbox centre, and `ext 60 (target)`
    polls until that blast overlaps that target (B1965). THE PLAYER AS ATTACKER IS VANILLA, not an
    inference: record rom:0x3E5224 (map 11,6, table rom:0x3E6078 word 31) fires
    `attack(0, 28, 100)` three times and polls `ext 60 (28)`. BLAST_SPEED is that record's own n.

    A beaten enemy still acting is vanilla too. Android 18's OWN death record rom:0x3D8BC4 poses her
    down, stands her back up and has HER fire `attack(11, 0, 100)` at the player, with `ext 60 (0)`
    polling a target whose distance the player chose. So the poll is not new ground.

    `ext 56 face_alt (a, b)` turns a toward b's +0x158/+0x15C once (B0741). It runs first because the
    blast spawns at the attacker's hurtbox edge BY FACING (B1964), so a Trunks facing away would fire
    from behind himself. LIKELY, not confirmed: B0741 found no vanilla site with an enemy as b.

    NO FADE and NO CAMERA OP. The whole beat stands on the ground the fight ended on."""
    return (call("face_alt", PLAYER, enemy_set)
            + call("block_begin")
            + call("attack", PLAYER, enemy_set, BLAST_SPEED)
            + ext(60, enemy_set)
            + call("block_end")
            + remove(enemy_set))


def death(enemy_set: int, nxt: int, entrance: int = None) -> bytes:
    """Word 0 of an enemy's own death table: the bar and the HUD go, the android collapses, Trunks
    blasts her, and the cutscene picks up with NO TRANSITION of any kind.

    The owner's flow, 2026-11-07: "18 fight -> she collapses -> Trunks blasts her, NO transition".
    So this record carries no `fade_out`, no `fade_in`, no `ext 31` camera park, no `ext 62` and no
    map load. The v5 record had all four, and their only job was to snap the scene back to vanilla's
    staging, which is the architecture the finale design says not to inherit. Nothing downstream
    needs that staging: words 9, 10 and 12 are text records, word 11's `ext 104` builds Android 17
    wherever he is standing, and word 13 opens with vanilla's own fade.

    The enemy types are not written, so both androids keep the BOSS death descriptor rom:0x086FF3C4,
    which leaves a beaten boss standing at HP 0 with no AI instead of removing him. The record
    therefore poses him down itself and holds, which is what Android 18's own vanilla death record
    rom:0x3D8BC4 opens with, and the blast is what removes him.

    `entrance` is Android 17's set on Android 18's record and None on his own. When it is given, the
    record calls `approach()`, which carries the owner's rule of 2026-11-07, "if 17 is already on
    screen, he just goes to his dialogue. If he is offscreen, then he walks onscreen, facing
    trunks", and his correction of the same day, that the walk must follow one path. Both `face_alt`
    calls run on EVERY path, because the face-the-player step struct does not tick during a scene.

    He speaks VANILLA'S OWN LINE. `nxt` is 9, and ending word 9 rom:0x3B7D2A is
    "It can't be!" on portrait 28, the portrait word 1 gives "ANDROID 17". Word 10 is Trunks'
    "And this is for all the people you've killed!". No line is invented and none is moved.

    After Android 17 the hand-back is 12, Trunks' "Now there's just one more thing that needs to be
    done.", and he turns to the camera for it as the vanilla beating's closing `face(133,0)` did."""
    beat = (ext(88) + call("header_bit1", 0)
            + pose(enemy_set, DOWN_STATE) + wait(COLLAPSE_HOLD)
            + blast(enemy_set))
    if entrance is None:
        return code(nxt, beat, face(PLAYER, DOWN), wait(HANDBACK_HOLD))
    return code(nxt, beat, approach(entrance), wait(HANDBACK_HOLD))


def death_table(rom: bytes, death_at: int) -> bytes:
    """An enemy's event table: the LIVE ending table with word 0 replaced by its own death record.

    The event runner starts every death event at word 0, so word 0 cannot be the ending's own opening
    record. Nothing ever jumps to index 0: words 0 to 25 run 1, 2, ... 26 in order and word 26 is END.

    Every other word is COPIED LIVE, which is the whole point. Taken after this module writes words 8
    and 11, Android 18's table carries the real Android 17 fight at word 11, so beating 18 leads to the
    cutscene and then to a second real fight, not to the vanilla scripted beating whose attacker is a
    set 133 NPC that no longer exists. The copy also carries ending_fight's word 13 and word 23, so the
    arena load and the Imperfect Cell fight follow on exactly as they do in the ending itself."""
    words = [_u32(rom, TABLE + 4 * k) for k in range(TABLE_WORDS)]
    words[0] = death_at + ROM_BASE
    return b"".join(_word(w) for w in words)


# ===== the clone =====

def clone_entry(rom: bytes, source: int, items_at: int, layouts_at: int) -> bytes:
    """Map 1,100: map 1,2 with no regions, no banner, five items and its own layout.

    An empty region list is what removes the prologue. Map 1,2's one region rom:0x3ED7DC carries
    condition 0, which `condition_eval` @0x08003F06 reads as "always", and a step trigger over rect
    (-15,-7)-(360,584) that fires scene table rom:0x3B7ADC, the prologue beating of set 54. The
    fighters start east of x 360, but a real fight lets the player walk, and the clone must hold no
    path back to that table at all. Region count and region list go to zero together, which is how all
    327 vanilla entries carry them.

    The banner is NOT copied. Map 1,2's 0xE5 would draw its name over the fight; 0xDD is "show none",
    CONFIRMED in `sub_0800EBB6` and its caller (`CMP r0,#0xDD ; BEQ` skips the banner call).

    The music word is NOT copied. Map 1,2's own +0x24 is the script rom:0x3ED73C, which returns song
    38 under flag 196, and vanilla never runs it: `Map_Load` @0x0800C664, the ext 35 path this scene
    uses, does not call `sub_0800C390` and so never reaches the +0x24 read. Only the ext 38 and ext 39
    path does. The clone is loaded with ext 39, so copying the script would start the Android theme
    under the black while vanilla is still playing song 42 through the whole walk-in. +0x24 names 42
    instead, the song already playing, which the load's own "already playing" test skips. See
    WALK_IN_MUSIC."""
    entry = bytearray(MAP_SIZE)
    entry[0], entry[1] = CLONE_ZONE, CLONE_AREA
    entry[F_VARIATIONS], entry[F_REGION_COUNT] = CLONE_VARIATIONS, 0
    entry[F_ITEM_COUNT] = CLONE_ITEMS
    entry[F_COMBAT:F_COMBAT + 4] = _word(1)
    entry[F_BANNER:F_BANNER + 4] = _word(NO_BANNER)
    entry[F_ITEMS:F_ITEMS + 4] = _word(items_at + ROM_BASE)
    entry[F_MUSIC:F_MUSIC + 4] = _word(WALK_IN_MUSIC)
    entry[F_LAYOUTS:F_LAYOUTS + 4] = _word(layouts_at + ROM_BASE)
    return bytes(entry)


def clone_layout(source: bytes) -> bytes:
    """Map 1,2's layout struct with its door count and door list zeroed and every other byte copied.

    A map carries doors in TWO carriers, and an empty region list only empties one of them. Map 1,2's
    layout holds one door, rom:0x6ACB4C, rect (144,280)-(273,305) to map 2,22 at (128,116). On the
    clone that door would drop the player into the town with the fight gone, and map 2,22's own way
    back names map 1,2, not the clone, so he could never return. +0x40 and +0x44 go to zero as a pair,
    which is how every vanilla layout carries them.

    Nothing else changes. The collision frame, the one prop, the four BG layer records, the tile
    stream and the tile table are SHARED with map 1,2, because the clone reads them and never writes
    them. The courtyard keeps map 1,2's own walkable shape, which is the staging the owner asked to
    keep."""
    out = bytearray(source)
    out[L_WARP_COUNT:L_WARP_COUNT + 4] = _word(0)
    out[L_WARP_LIST:L_WARP_LIST + 4] = _word(0)
    return bytes(out)


def npc_item(source: bytes, step_at: int) -> bytes:
    """One of map 1,2's NPC items with condition "always" and its own copy of its step struct.

    Vanilla gives the two androids condition 0x000100C4, which `Script_TestFlag` @0x08003F06 reads as
    "flag 196 set". The ending is the one place flag 196 is set, so the two readings agree here, and 0
    is the simpler of the two and cannot be wrong. This is the same call battle_arena made for its own
    NPC."""
    item = bytearray(source)
    item[N_COND:N_COND + 4] = _word(COND_ALWAYS)
    item[N_STEP:N_STEP + 4] = _word(step_at + ROM_BASE)
    return bytes(item)


def enemy_item(source: bytes, at: tuple, event_at: int, tail_at: int) -> bytes:
    """One android's enemy item: the vanilla bytes with condition 1, the NPC's spot, and a FRESH
    event struct and step struct of its own.

    The event struct is where a death table is written, so it MUST be a new copy. The vanilla items
    name rom:0x40339C (Android 18) and rom:0x40648C (Android 17), and writing a table into either
    would change the main game's own Android fights, which the owner ruled out.

    Condition 1 is "never at load": the map build leaves the item alone and only the fight record's
    `ext 104` turns it into a live enemy. The type word is untouched, so Android 18 keeps type 4
    (HP 2910, AI 21) and Android 17 type 3 (HP 3550, AI 21), both with the boss death descriptor.
    The spot is kept at the NPC's own spot so the item reads right, although `ext 104` overwrites it
    with the replaced NPC's position and facing."""
    item = bytearray(source)
    item[ITEM_COND:ITEM_COND + 4] = _word(COND_NEVER_AT_LOAD)
    item[ITEM_AT:ITEM_AT + 4] = struct.pack("<hh", *at)
    item[ITEM_EVENT:ITEM_EVENT + 4] = _word(event_at + ROM_BASE)
    item[ITEM_TAIL:ITEM_TAIL + 4] = _word(tail_at + ROM_BASE)
    return bytes(item)


def new_table(rom: bytes, table: int, count: int, entry: bytes) -> bytes:
    """Every LIVE entry followed by the clone. Live, not base: battle_arena has already appended one."""
    return bytes(rom[table:table + MAP_SIZE * count]) + entry


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def map_table(rom: bytes) -> tuple:
    """(file offset, entry count) of THIS ROM's map table, from the literal rom:0xEBD8 and the count
    getter rom:0xE0AC. battle_arena has already moved both, so neither base value may be assumed."""
    return _u32(rom, MAP_BASE_LITERAL) - ROM_BASE, 0xFF + rom[MAP_COUNT_BYTE]


def map_entry(rom: bytes, zone: int, area: int) -> tuple:
    """(index, file offset) of one map's entry in THIS ROM's live table."""
    table, count = map_table(rom)
    for k in range(count):
        at = table + MAP_SIZE * k
        if rom[at] == zone and rom[at + 1] == area:
            return k, at
    raise ValueError(f"no map {zone},{area} in the live map table rom:0x{table:X} ({count} entries)")


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


# ===== checks =====

def _check_prologue(rom: bytearray) -> None:
    """The prologue chain is one word at each link, and every word that reaches it belongs to a map
    1,2 entry. The clone carries no region list, so it joins no part of this chain.

    Walked from the table backwards: the scene table rom:0x3B7ADC is named only by the region item's
    +0x10; the region item rom:0x3ED7DC is named only by the region list's +4; and the region list
    rom:0x3ED7F0 is named only by +0x10 words of entries whose first two bytes are 1 and 2. That last
    one is a LIST, not a single word, because battle_arena's table copy gives map 1,2 one entry per
    live table and the dead table keeps its own."""
    _expect(rom, SOURCE_REGION_ITEM + REGION_ITEM_TABLE_AT, _word(PROLOGUE_TABLE + ROM_BASE))
    _expect(rom, SOURCE_REGION_LIST + REGION_LIST_POINTER_AT, _word(SOURCE_REGION_ITEM + ROM_BASE))
    namers = words_naming(rom, PROLOGUE_TABLE)
    if namers != [SOURCE_REGION_ITEM + REGION_ITEM_TABLE_AT]:
        raise ValueError(f"the prologue table rom:0x{PROLOGUE_TABLE:X} is named by"
                         f" {[hex(x) for x in namers]}, expected only the region item's +0x10")
    namers = words_naming(rom, SOURCE_REGION_ITEM)
    if namers != [SOURCE_REGION_LIST + REGION_LIST_POINTER_AT]:
        raise ValueError(f"the prologue region rom:0x{SOURCE_REGION_ITEM:X} is named by"
                         f" {[hex(x) for x in namers]}, expected only the region list's +4")
    for word in words_naming(rom, SOURCE_REGION_LIST):
        entry = word - F_REGIONS
        if (rom[entry], rom[entry + 1]) != (SOURCE_ZONE, SOURCE_AREA):
            raise ValueError(f"the prologue region list is named by rom:0x{word:X}, which is not the"
                             f" +0x10 of a map {SOURCE_ZONE},{SOURCE_AREA} entry: stop and report")


def _check_layout_chain(rom: bytearray, source: int) -> None:
    """Map 1,2's entry names one layout array, the array names one layout, and the layout's own
    pointers are pinned, so the copy refuses if the map ever gains or loses a door, a prop or a layer."""
    _expect(rom, source + F_LAYOUTS, _word(SOURCE_LAYOUTS + ROM_BASE))
    _expect(rom, SOURCE_LAYOUTS, _word(SOURCE_LAYOUT + ROM_BASE))
    for off, want in ((L_BG0, SOURCE_LAYERS[0]), (L_BG1, SOURCE_LAYERS[1]),
                      (L_BG2, SOURCE_LAYERS[2]), (L_BG3, SOURCE_LAYERS[3]),
                      (L_PROP_LIST, SOURCE_PROP_LIST), (L_COLLISION, SOURCE_COLLISION),
                      (L_WARP_LIST, SOURCE_WARP_LIST)):
        _expect(rom, SOURCE_LAYOUT + off, _word(want + ROM_BASE))
    _expect(rom, SOURCE_LAYOUT + L_PROP_COUNT, _word(SOURCE_PROPS))
    _expect(rom, SOURCE_LAYOUT + L_WARP_COUNT, _word(SOURCE_WARPS))
    _expect(rom, SOURCE_WARP_LIST, _word(SOURCE_DOOR + ROM_BASE))


def _check(rom: bytearray, alloc) -> None:
    if "future_androids" in alloc.notes:
        raise ValueError("future_androids already ran")

    table, count = map_table(rom)
    for lit in BASE_LITERALS:
        _expect(rom, lit, _word(table + ROM_BASE))
    _expect(rom, ENTRY3_LITERAL, _word(table + MAP_SIZE * ENTRY3 + ROM_BASE))
    if words_naming(rom, table) != list(BASE_LITERALS):
        raise ValueError(f"the live map table base rom:0x{table:X} is named by"
                         f" {[hex(x) for x in words_naming(rom, table)]}, expected {[hex(x) for x in BASE_LITERALS]}")
    if words_naming(rom, table + MAP_SIZE * ENTRY3) != [ENTRY3_LITERAL]:
        named = [hex(x) for x in words_naming(rom, table + MAP_SIZE * ENTRY3)]
        raise ValueError(f"map entry {ENTRY3} is named by {named},"
                         f" expected one word at rom:0x{ENTRY3_LITERAL:X}")
    _expect(rom, COUNT_FN, COUNT_CODE_HEAD)
    _expect(rom, COUNT_FN + 3, COUNT_CODE_TAIL)
    if 0xFF + rom[MAP_COUNT_BYTE] != count or count > 0xFF + 0xFE:
        raise ValueError(f"rom:0x{MAP_COUNT_BYTE:X} is 0x{rom[MAP_COUNT_BYTE]:02X}: the count byte and"
                         f" the live entry count {count} disagree, or the byte would overflow")

    pairs = [(rom[table + MAP_SIZE * k], rom[table + MAP_SIZE * k + 1]) for k in range(count)]
    if len(set(pairs)) != count:
        raise ValueError(f"(zone, area) is not unique across the {count} live map entries")
    if (CLONE_ZONE, CLONE_AREA) in pairs:
        raise ValueError(f"map {CLONE_ZONE},{CLONE_AREA} already exists: pick another free area")

    index, source = map_entry(rom, SOURCE_ZONE, SOURCE_AREA)
    _expect(rom, source, SOURCE_ENTRY)
    _expect(rom, source + F_MUSIC, _word(SOURCE_MUSIC))
    _check_layout_chain(rom, source)
    _check_prologue(rom)

    for item, body, step, step_body in SOURCE_NPCS:
        _expect(rom, item, body)
        _expect(rom, step, step_body)
        if _u32(body, 0) != NPC_FACTORY:
            raise ValueError(f"SOURCE_NPCS rom:0x{item:X} does not open with the NPC factory")
        if _u32(body, N_STEP) - ROM_BASE != step:
            raise ValueError(f"SOURCE_NPCS rom:0x{item:X} does not name its step struct rom:0x{step:X}")
    for set_id, (item, body, event, event_body, tail, tail_body) in TEMPLATES.items():
        _expect(rom, item, body)
        _expect(rom, event, event_body)
        _expect(rom, tail, tail_body)
        if _u32(body, 0) != ENEMY_FACTORY or _u32(body, ITEM_SET) != set_id:
            raise ValueError(f"the enemy template rom:0x{item:X} is not the enemy factory, or not set {set_id}")
        if _u32(body, ITEM_EVENT) - ROM_BASE != event or _u32(body, ITEM_TAIL) - ROM_BASE != tail:
            raise ValueError(f"the enemy template rom:0x{item:X} does not name its own event or step struct")
        if _u32(event_body, 0) != EVENT_RUNNER:
            raise ValueError(f"the event struct rom:0x{event:X} does not open with the event runner")
    for type_id, body in TYPES.items():
        _expect(rom, ENEMY_TABLE + ENEMY_ENTRY * type_id, body)

    guarded = [(SOURCE_REGION_LIST, 8, "map 1,2's region list"),
               (SOURCE_REGION_ITEM, ITEM_SIZE, "the prologue region item"),
               (SOURCE_LAYOUTS, 4, "map 1,2's layout array"),
               (SOURCE_LAYOUT, LAYOUT_SIZE, "map 1,2's layout struct"),
               (SOURCE_WARP_LIST, 4, "map 1,2's layout door list"),
               (ENEMY_TABLE + ENEMY_ENTRY * A18_TYPE, ENEMY_ENTRY, "enemy type 4 (Android 18)"),
               (ENEMY_TABLE + ENEMY_ENTRY * A17_TYPE, ENEMY_ENTRY, "enemy type 3 (Android 17)")]
    guarded += [(item, NPC_ITEM_SIZE, f"map 1,2's NPC item rom:0x{item:X}") for item, _, _, _ in SOURCE_NPCS]
    guarded += [(step, len(body), f"map 1,2's NPC step struct rom:0x{step:X}")
                for _, _, step, body in SOURCE_NPCS]
    for set_id, (item, _, event, event_body, tail, tail_body) in TEMPLATES.items():
        guarded += [(item, ITEM_SIZE, f"the vanilla enemy item of set {set_id}"),
                    (event, len(event_body), f"the vanilla event struct of set {set_id}"),
                    (tail, len(tail_body), f"the vanilla step struct of set {set_id}")]
    for k, (rec, sha) in RECORDS.items():
        word, length = TABLE + 4 * k, record_end(rom, rec) - rec
        _expect(rom, word, _word(rec + ROM_BASE))
        if hashlib.sha1(bytes(rom[rec:rec + length])).hexdigest() != sha:
            raise ValueError(f"ending record rom:0x{rec:X} (word {k}) differs from the base bytes")
        if words_naming(rom, rec) != [word]:
            raise ValueError(f"0x{rec + ROM_BASE:08X} (ending word {k}) is named by"
                             f" {[hex(x) for x in words_naming(rom, rec)]},"
                             f" expected one word at rom:0x{word:X}")
        guarded += [(word, 4, f"ending table word {k}"), (rec, length, f"ending record {k}")]
    for name, (start, size) in _written(alloc.notes):
        for lo, n, what in guarded:
            if start < lo + n and lo < start + size:
                raise ValueError(f"{what} rom:0x{lo:X} is also written by {name}: stop and report")
    return index, source, table, count


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    index, source, table, count = _check(rom, alloc)
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

    # 1. The five ending records, and the three words that must be live before the death tables are cut.
    come = place(arrive(rom, CLONE_ZONE, CLONE_AREA),
                 f"word {ARRIVE_INDEX} (the clone loads with a player on it)")
    turn = place(transform(rom), f"word {TRANSFORM_INDEX} (the player goes Super Saiyan)")
    named = place(name_line(rom), f"word {NAME_INDEX} (the player turns, not the removed NPC)")
    f18 = place(fight(A18_SET, ENEMY_18_ITEM), f"word {FIGHT18_INDEX} (fight 1: Android 18)")
    f17 = place(fight(A17_SET, ENEMY_17_ITEM), f"word {FIGHT17_INDEX} (fight 2: Android 17)")
    for k, at in ((ARRIVE_INDEX, come), (TRANSFORM_INDEX, turn), (NAME_INDEX, named),
                  (FIGHT18_INDEX, f18), (FIGHT17_INDEX, f17)):
        put(TABLE + 4 * k, _word(at + ROM_BASE), f"ending table word {k}")

    # 2. The death records and the two event tables. The tables are cut from the table words AS THEY
    #    NOW STAND, so Android 18's carries the real Android 17 fight at word 11.
    dead18 = place(death(A18_SET, AFTER18_INDEX, entrance=A17_SET),
                   "Android 18's death record (the blast, then the 17 entrance branch, hands back at word 9)")
    dead17 = place(death(A17_SET, AFTER17_INDEX),
                   "Android 17's death record (the blast, hands back at word 12)")
    table18 = place(death_table(rom, dead18), f"Android 18's event table ({TABLE_WORDS} words)")
    table17 = place(death_table(rom, dead17), f"Android 17's event table ({TABLE_WORDS} words)")

    # 3. The clone's items. Each enemy gets its OWN event struct and step struct.
    enemies, events = {}, {}
    for set_id, at, event_table, label in ((A18_SET, SOURCE_NPCS[A18][1], table18, "Android 18"),
                                           (A17_SET, SOURCE_NPCS[A17][1], table17, "Android 17")):
        item_at, body, _, event_body, _, tail_body = TEMPLATES[set_id]
        tail = place(tail_body, f"{label}'s step struct (a fresh copy)")
        event = place(_word(EVENT_RUNNER) + _word(event_table + ROM_BASE),
                      f"{label}'s event struct (a fresh copy, naming her own death table)")
        spot = struct.unpack_from("<hh", at, N_AT)
        enemies[set_id] = place(enemy_item(body, spot, event, tail),
                                f"the enemy {label} (type {_u32(body, ITEM_TYPE)}, condition 1)")
        events[set_id] = event

    # NPC Future Gohan and NPC Trunks are not built, so the item list holds the two androids first,
    # in the order NPC_18_ITEM and NPC_17_ITEM name.
    npcs = []
    for k, label in ((A18, "Android 18 (set 11)"), (A17, "Android 17 (set 9)")):
        _, body, _, step_body = SOURCE_NPCS[k]
        watch = k == A17                                   # only 17 watches the player, the owner's call
        step = place(FACE_PLAYER if watch else step_body,
                     f"the NPC {label}'s step struct" + (" (face the player)" if watch else ""))
        npcs.append(place(npc_item(body, step), f"the NPC {label}, condition 0"))

    order = npcs + [enemies[A18_SET], enemies[A17_SET]]
    if len(order) != CLONE_ITEMS:
        raise ValueError(f"the clone's item list holds {len(order)} items, but the entry's item count"
                         f" and the `ext 104` indices are written for {CLONE_ITEMS}")
    items = place(b"".join(_word(at + ROM_BASE) for at in order),
                  f"the clone's item list ({CLONE_ITEMS} items: 2 NPCs, then the 2 enemies)")

    # 4. The clone's layout, its entry, and the relocated map table.
    layout = place(clone_layout(bytes(rom[SOURCE_LAYOUT:SOURCE_LAYOUT + LAYOUT_SIZE])),
                   "the clone's layout copy (its one door list zeroed)")
    layouts = place(_word(layout + ROM_BASE), f"the clone's layout array ({CLONE_VARIATIONS} variation)")
    entry = clone_entry(rom, source, items, layouts)
    new = place(new_table(rom, table, count, entry), f"the map table copy ({count + 1} entries)")

    for lit in BASE_LITERALS:
        put(lit, _word(new + ROM_BASE), f"map table literal rom:0x{lit:X}")
    put(ENTRY3_LITERAL, _word(new + MAP_SIZE * ENTRY3 + ROM_BASE), f"map entry {ENTRY3} literal")
    put(MAP_COUNT_BYTE, bytes([rom[MAP_COUNT_BYTE] + 1]),
        f"map count getter: {count} becomes {count + 1}")

    alloc.notes["future_androids"] = {
        "table": new, "entry": new + MAP_SIZE * count, "entry_index": count,
        "old_table": table, "old_count": count, "source_index": index,
        "zone": CLONE_ZONE, "area": CLONE_AREA, "variation": CLONE_VARIATIONS,
        "items": items, "npc_items": npcs, "enemies": enemies, "events": events,
        "tables": {A18_SET: table18, A17_SET: table17},
        "deaths": {A18_SET: dead18, A17_SET: dead17},
        "layout": layout, "layouts": layouts,
        "arrive": come, "transform": turn, "name_line": named, "fights": {A18_SET: f18, A17_SET: f17},
        "enemy_item_index": {A18_SET: ENEMY_18_ITEM, A17_SET: ENEMY_17_ITEM},
        "player_start": PLAYER_START, "trunks_spot": TRUNKS_SPOT,
        "sites": sorted(sites)}
