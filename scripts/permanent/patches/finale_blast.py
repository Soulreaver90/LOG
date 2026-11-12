r"""
finale_blast.py - Trial patch: the last beat of the future Trunks finale. Trunks fires a GOLD beam
                  straight up, Cell takes three hits with explosions and screen rumble, then explodes.

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_plateau.txt
                --out <new .gba>
Input:   the ROM after build_list_trial_plateau.txt (dev r41, battle_arena, ending_fight,
         future_androids, scouter_future, plateau). It runs LAST: it reads plateau's table D2 and the
         LIVE ext op table, which chapter_cards already relocated.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["finale_blast"], every write as
         (offset, length, name) in its "sites". stage(), kamehame(), shout(), blast(),
         last_words() and credits() hold the design, so a check, a test and the report read it once.
         gold_source(vtable_at) -> the Thumb source of the gold entry point.
Design:  docs\design\2026-11-08-finale-dialogue.md section 5, "The blast, settled" and "Build state".
         Every line of dialogue is the owner's, quoted character for character.

Method:  1. THE GOLD BEAM IS A NEW EXT OP, all in expansion space. The beam object `@0x080143A8`
            picks its colour from ARGUMENT 6: 0 is the blue set, non-zero is the gold set the owner
            chose ("teh blast was yellow so just use the existing middle one"). `ext 137`'s builder
            `@0x0801D84C` hardcodes that argument to 0 at `rom:0x1D870`. That byte may NOT be flipped
            globally: `ext 137` has exactly two vanilla sites and one is Gohan's Cell Games
            Kamehameha, which stays blue. So the module copies the whole entry point instead:
              - `gb_build`, a copy of `@0x0801D84C` whose `mov r2,#0x0` is `mov r2,#0x1`;
              - `gb_start`, a copy of `@0x0801D788` whose builder call names `gb_build` and whose
                spawn y is lifted by `BEAM_RISE`, so the CHARGE starts at Trunks' hands;
              - `gb_tick`, a copy of the command tick `@0x0801D7DC` whose FIRE y is lifted by the
                same `BEAM_RISE`, so the fired beam starts there too. The tick recomputes the point
                from the actor and ignores what the start stored, so without this copy the start's
                lift moves nothing. See BEAM_RISE;
              - `gb_handler`, a copy of the `ext 137` handler `@0x0800A3A2`, loading the new vtable;
              - a 5 word copy of the command vtable `0x0802521C`, every slot REBASED, with slot 1
                naming `gb_start` and slot 2 naming `gb_tick`.
            Nothing vanilla is written. Every vanilla beam keeps its colour.
         1a. THE COPIES ARE RE-AUTHORED, NOT BYTE COPIED, and both reasons are measured. Every one of
            the four bodies loads a literal from a pool OUTSIDE its own extent (`rom:0xA418` and
            `rom:0xA430` for the handler, `rom:0x1D848` for the start and the tick, `rom:0x1D9CC`
            for the builder),
            so a flat copy aims its `ldr rX,[pc,#imm]` at whatever follows it in expansion. And every
            `bl` back into the base ROM is out of range: a Thumb `bl` reaches about 4 MB and the
            expansion area is about 8 MB away. So each body is re-typed instruction for instruction
            through `ssj2_form.assemble`, which lays its own pool, and each call goes through a local
            `bx` trampoline. `gb_handler`'s one deviation is `stmia r0!,{r1,r2}` plus `sub r0,#0x8`
            written as two `str`, which writes the same two words and leaves r0 the same.
         1b. THE VTABLE COPY IS REBASED. A command vtable stores offsets RELATIVE to its own address,
            with the Thumb bit (bible FBM). A verbatim copy breaks every slot, so each word becomes
            `old + 0x0802521C - new_vtable`, and slot 1 becomes `(gb_start | 1) - new_vtable`.
            The vtable is FIVE words: the next vtable is `0x08025230`, named by `rom:0xA740`.
         1c. THE EXT TABLE IS COPIED LIVE. `chapter_cards` already moved the 145 word table
            `0x083B5D28` into a 146 word copy, so this module reads the live base out of pool
            `rom:0x921C`, finds the module that owns it, copies all of its words and appends one.
            Both pool words that name the table (`rom:0x921C` op 2, `rom:0x92DC` ops 21-26) move to
            the new copy. THERE IS NO BOUND TO RAISE: op 2 `@0x08008F8E` and base ops 21 to 26
            (`@0x08009130`, `@0x08009160`, `@0x08009190`, `@0x080091BC`, `@0x080091EC`,
            `@0x08009224`) all read `[table + 4n]` with no `cmp` on n. All seven listings read.
         2. THE SCENE IS TABLE D2, the plateau enemy's own death event. Word 0 held ending_fight's
            record K; it now holds record B1 and the chain runs 0, 1, 2, 3, 4, 5, 6 and then 24,
            which is the vanilla "The End." text, and 25, the vanilla exit. Words 1 to 6 were END.
         2a. THE STAGING IS A VERTICAL PAIR, Cell ABOVE and Trunks BELOW, because the beam fires
            along the ACTOR'S OWN FACING and direction 1 is UP (bible FBM, record geometry). Both
            spots are measured on the owner's map 142, in `_check_design`, before a byte is written:
            open, reachable from the fight spot, and clear of the BG1 art that draws over the player.
            The beam column above Trunks is checked the same way, because BG1 would cover the beam.
         2b. THE DEATH LOOP IS VANILLA'S OWN. Perfect Cell's death, record `0x083EBE1C`, runs five
            blocks after its Kamehameha: four hit loops and a final explosion. The owner's ruling is
            "lets do 3 loops isntead of 4 for future cell", so this record runs hit blocks 1, 2 and 3
            and then the FIFTH block, the explosion, which removes Cell. Every op, every camera value
            and every effect offset is vanilla's, with set 28 in place of set 30.
         3. THE CREDITS MUSIC IS VANILLA'S OWN. The owner asked for "back to the credits music that
            normally plays". The ending's own tail plays `music(15)` at `rom:0x3B80DD`, and this
            record runs that tail unchanged through `ending_fight.tail`. 37 is Perfect Cell's cue,
            not this ending's.
Rules:   Every source body, word and table entry is checked before the first write; a second run
         raises. No vanilla byte is written at all: the only base-ROM writes are the TWO ext table
         pool words, which are chapter_cards' own declared sites and are handed on the way the map
         table and the scouter table are handed on. The shared OBJ palette is not touched and no new
         art is made: the gold beam ships in the ROM already.
"""
import struct

from patches.ending_fight import tail
from patches.ssj2_form import assemble
from rom.log2_sprites import clone_set, set_records
from rom.webfoot_decompress import read_set, set_offset
from scene.scene_lib import (call, code, ext, fade_in, fade_out, text, wait)

import patches.plateau as plateau

# ===== constants: the ext op table, read LIVE =====
ROM_BASE = 0x08000000
BASE_EXT_TABLE, BASE_EXT_OPS = 0x3B5D28, 145      # the vanilla table and its code word count
EXT_POOLS = (0x921C, 0x92DC)                      # every ROM word that names the table (bible s6)
SECOND_POOLS = (0x9220, 0x92E0)                   # the PARALLEL table 0x083B5F70 ops 21-26 also index
SECOND_TABLE = 0x3B5F70                           # = BASE_EXT_TABLE + 4 x 146, and it never moves

# ===== constants: the vanilla bodies the gold entry point copies =====
# Each is (file offset, the whole body as hex). A wrong address raises instead of writing.
HANDLER_AT = 0xA3A2                               # the ext 137 handler @0x0800A3A2, 0x46 bytes
HANDLER_BYTES = ("38b5016801398a0001601218546801390160890008184068fef7d9ff051c142014f063fe002807d0"
                 "1949002206c00838c4608260083c0461011c0e482a1cc06803f033fe38bd")
START_AT = 0x1D788                                # the command start @0x0801D788, 0x54 bytes
START_BYTES = ("30b5051c89b003a80c1ceaf711f90398059a069b821804980192c01802905210401001920792002202"
               "900890231c002007a900f047f8011ca86021480068e9f777f82168201c8a6a52181e2104f0aafa09b0"
               "30bd")
TICK_AT = 0x1D7DC                                 # the command tick @0x0801D7DC, 0x5C bytes
TICK_BYTES = ("30b5041cc0680d1c002887b01ed00138e060216988421bd1291c03a8eaf715f9287c12490431c0"
              "004018039902688918049a4068019110180290081c029905900691297ca06805aaf6f728fe07b0"
              "30bd0028fbd1a068f6f773fef7e7")
BUILD_AT = 0x1D84C                                # the beam builder @0x0801D84C, 0x3E bytes
BUILD_BYTES = ("f0b5171c0e1c1d1c041c002883b007d1502001f015fc041c02d1201c03b0f0bd0121890200220192"
               "0091311c3a1c2b1c201cf6f793fd52482060201ceee7")
COLOUR_BYTE = 0x1D870                             # the `mov r2,#0x0` immediate: argument 6, the colour
BLUE, GOLD = 0x00, 0x01

VTABLE_AT, VTABLE_WORDS = 0x2521C, 5              # the ext 137 command vtable, five slots
NEXT_VTABLE = 0x25230                             # the vtable that follows it, named by rom:0xA740
VANILLA_VTABLE = (0x2455, 0xFFFF856D, 0xFFFF85C1, 0xFFFF861D, 0xF01)
VTABLE_START_SLOT, VTABLE_TICK_SLOT = 1, 2        # slot 1 is start, 2 is tick, 3 is done (bible FBM)

# ===== THE ONE NUMBER THE OWNER NUDGES: where the gold beam starts =====
# He played finale_poses_wip1 and said "it needs to start where trunks hands are, right above it"
# and "overshooting cell is fine ... the complaint is the starting position of the beam". So the
# beam is not shortened and neither fighter moves. Only its start moves, and every number is
# measured, not assumed:
#   THE SPAWN POINT IS THE CENTRE OF HIS COLLISION RECT, NOT HIS OWN POINT. `gb_start` calls
#   `Rect_FromDefinition` @0x080079B8, which reads the actor's 24.8 position at +0x158, shifts it
#   to pixels and builds {x + left, y + top, x + right, y + bottom} from the 4 words at +0xC of
#   block [+0x10] of the set at +0x48. `gb_start` then averages the two corners. Trunks' direction
#   1 rect is (-2, -26) to (+17, +10), read out of the owner's own save state
#   finale_poses_wip1.ss3, so the spawn point sits 8 px ABOVE his point.
#   THE BEAM ENDS 16 PX BELOW THE SPAWN POINT. The gold dir 1 run `0x08704604 + 96` extends dy -32
#   to +16 (beam_extent.py), so its bottom row sat on his point + 8. That is the bottom row of his
#   16x32 firing frame, drawn at dy -24: his feet, which is exactly what he saw.
#   HIS RAISED HANDS TOP OUT ON ROW 3 OF THAT FRAME. A pixel diff of the firing frame 0x36AE4C
#   against the hands-down frame 0x36AD44 shows both arms raised up the outside of his hair and
#   ending on row 3, which is his point - 21.
# So the lift is (point + 8) - (point - 21) = 29 px. IT IS MEASURED FROM THE BOTTOM ROW OF HIS
# SPRITE, WHERE THE BEAM USED TO START, TO THE TOP ROW OF HIS RAISED HANDS. Raise it to lift the
# beam clear of him; lower it to drop it back toward his waist. Format 3 holds 0 to 255.
# The two measurements are re-runnable: scripts\one-time\2026-11-08-beam-start\actor_box.py reads
# the rect out of his save state and frame_diff.py finds the arms, and prove.py reads all of it
# back out of a built ROM.
# The vanilla muzzle offset table 0x08701DF0 is NOT touched. Its dir 1 entry is (0, 0) and the blue
# beam, which is Gohan's Cell Games Kamehameha, reads the same table.
#   THE LIFT HAS TO RUN TWICE, because the beam is positioned TWICE. `gb_start` places the CHARGE
#   when the command object is built. The TICK then recomputes the point from the actor at the tick
#   the beam FIRES, through `sub_08007A26` plus the muzzle table, and hands that pair to
#   `sub_08014478`, which stores it into the beam's own +0x1C and +0x20. The fire pair is ABSOLUTE
#   and overwrites whatever the start left, so the start's lift alone moves nothing the player sees.
#   That is why wip1 still fired from his feet. Both copies therefore carry the SAME immediate, and
#   this one constant is the only place to nudge it.
BEAM_RISE = 29

# The symbols the three copies name. Each address carries its Thumb bit. All read from the listings.
SYMS = {"BEAM_RISE": BEAM_RISE,                   # not an address: the immediate BOTH copies carry
        "FIND_ACTOR": 0x08009371,                 # find_actor_by_set @0x08009370
        "ALLOC": 0x0801F08D,                      # @0x0801F08C
        "SCRIPT_GLOBALS": 0x083B5C78,
        "ACTOR_QUEUE": 0x0800E04D,                # @0x0800E04C
        "ACTOR_BOX": 0x080079B9,                  # @0x080079B8, reads r0 and r1 only
        "SPAWN_POINT": 0x08007A27,                # @0x08007A26, the tick's own spawn point
        "BEAM_FIRE": 0x08014479,                  # @0x08014478, r3 is written before it is read
        "BEAM_DONE": 0x0801451D,                  # @0x0801451C, reads r0 only
        "WORLD_HEAD": 0x08701DEC,                 # +4 is the vanilla muzzle offset table
        "WORLD_ADD": 0x080068B9,                  # @0x080068B8
        "BEAM_BUILD": 0x080143A9,                 # the beam object @0x080143A8
        "BEAM_VTABLE": 0x08025830,
        "VTABLE": 0xFFFF0001}                     # placeholder: the new command vtable's address

# ===== constants: THE TWO FINALE-ONLY SETS (the owner's section 7 ruling) =====
# He rejected wip3's poses: "you are not using the sprite I told you to use ... trunks is waving his
# hands around and doing slashes". The measured cause is ONE fact, bible B0149: state 30 is not a
# held pose. Its tick @0x0801CB24 shows frame 0 for 8 ticks and then ALTERNATES frames 1 and 2 every
# 8, for ever, and `ext 137` forces state 30 on whoever fires.
#
# A HELD POSE THEREFORE NEEDS A ROW WHOSE FRAMES ARE ALL THE SAME PICTURE, and the two rows the
# design wants are both LIVE IN THIS BUILD, so neither may be written:
#   set 28 anim 18  is Imperfect Cell's own vanilla Kamehameha, driven by `ext 137` at rom:0x3E1484,
#                   the main game's Cell fight on map 10,20 (bible B2228).
#   set 133 anim 18 is Trunks' sword special, and `future_androids` ships the fights he uses it in.
# So this module CLONES instead. `clone_set` copies a set's header, its animation table and every
# record list into expansion space and leaves the frame pixels where they are, so a clone costs a few
# kB of records and no art at all. Not one byte of set 28 or set 133 is written: `_check` reads both
# vanilla set table words back after the clones land and refuses if either moved.
#
# THE ROWS THE CLONES HOLD, each one read out of the ROM before it is written (see `hold_row`):
#   CELL_HOLD   anim 18 dir 0, 7 records, all made record 0: header 0x21E25C, the cupped-hands charge.
#               State 30 then holds that one picture for ever and Cell NEVER reaches the release
#               frames 0x21E50C and 0x21E7D8, which is what he asked for.
#   TRUNKS_HOLD anim  0 dir 1, 2 records, both made set 133 anim 4 dir 1 index 2: header 0x36AD44,
#               "his hands down". State 0 is the state an `ext 51` spawn stands in, so he shows that
#               frame, held, from the moment the fade lifts and all through Cell's two boxes and his
#               own shout.
#   TRUNKS_HOLD anim 18 dir 1, 7 records, all made set 133 anim 4 dir 1 index 3: header 0x36AE4C,
#               "his hands up, he shoots the blast". The beam op forces state 30, which reads anim
#               18, so the hands-up frame is held for the WHOLE beam and the whole death loop.
# The frame identity is the controller's render, not the wip3 report, which had the two the wrong way
# round. Both frames are 16x32 with dx 0 and dy -24, and a record carries its own geometry, so the
# 16x32 hands-up record sits in a 32x32 row without trouble: 512 bytes against set 133's 1024 byte
# OBJ slot.
#
# WHY NPCs AND NOT THE PLAYER. `ext 73` is the only op that changes the player's body, and it reverse
# looks the set id up in the appearance table (`appearance_of_set` @0x080042BC): an id with no entry
# hits the assert @0x0801F878 and the game HANGS (bible B0423, B0456). Every appearance entry 0-21 is
# in use (B0440) and entry 16 has to keep naming set 133, because `future_androids` runs
# `ext 73 (3, 133)` earlier in the same play through. So a cloned set can never be given to the
# player, and the finale stands an NPC on his mark and steps the player off the parked view instead.
SET_TABLE_LITERAL, FIRST_SET_ID = 0x959C, 7       # set id N is word N - 7 of the LIVE table
GI_SETS, GI_LAST = "gohan_gi", 160                # the module that relocated it, and its last id
LIVE_SET_IDS = GI_LAST - FIRST_SET_ID + 1         # 154 words: ids 7 to 160
CELL_HOLD_ID, TRUNKS_HOLD_ID = GI_LAST + 1, GI_LAST + 2        # 161 and 162, appended to that table
SSJ_TRUNKS = plateau.SSJ_TRUNKS                                # 133, the clone's source
# (anim, dir) of the row that is held, and (anim, dir, index) of the record that fills it.
CELL_HOLD_ROW, CELL_CHARGE = (18, 0), (18, 0, 0)
TRUNKS_IDLE_ROW, TRUNKS_HANDS_DOWN = (0, 1), (4, 1, 2)
TRUNKS_BEAM_ROW, TRUNKS_HANDS_UP = (18, 1), (4, 1, 3)
# The frame header each of those three records points at, read on the base ROM 2026-11-08. A wrong
# header raises instead of writing, so a set that ever moves cannot be posed by accident.
CHARGE_HEADER, HANDS_DOWN_HEADER, HANDS_UP_HEADER = 0x21E25C, 0x36AD44, 0x36AE4C
RECORD_BYTES = 12                                 # one frame record: dx, dy, w, h, attr0, attr1, ptr

# ===== constants: the actors and the staging =====
PLAYER, CELL_SET = plateau.PLAYER, plateau.CELL_SET          # 0 and 28
DOWN, UP = plateau.DOWN, plateau.UP                          # ext 55 facings; 1 is UP, and the beam
                                                             # flies along the actor's own facing
TRUNKS_PARTY, BASE_TRUNKS = plateau.TRUNKS_PARTY, plateau.BASE_TRUNKS      # 3 and 132
GAP = plateau.PLATEAU_GAP                                    # 64 px, the approved arena gap, turned
FINALE_CELL_SPOT = (424, 416)                                # Cell ABOVE
FINALE_TRUNKS_SPOT = (FINALE_CELL_SPOT[0], FINALE_CELL_SPOT[1] + GAP)      # Trunks BELOW, (424, 480)
FINALE_VIEW = (FINALE_CELL_SPOT[0] - plateau.VIEW[0] // 2,
               FINALE_CELL_SPOT[1] - 72, 40)                 # (304, 344) at plateau's own speed 40
BEAM_WIDTH = 32                                              # the widest beam body record (bible FBM)
# Measured on his map 2026-11-08 by _check_design, every number proved before a write:
#   the walkable centre is (424,448) and the pair's own centre is (424,448), dead on it.
#   1830 vertical pairs pass every check; this is the one nearest that centre.
#   the beam column is 90 cells from Trunks' point up to the view top, and no BG1 cell is in it.
FINALE_SPOTS = ((FINALE_CELL_SPOT, plateau.ENVELOPE_LR, "Cell above"),
                (FINALE_TRUNKS_SPOT, plateau.TRUNKS_ENVELOPE_LR, "Trunks below"))
# WHERE THE PLAYER WAITS. An NPC stands on Trunks' mark, so the player steps off the parked view and
# stands there until the credits. `ext 62` writes a position and touches nothing else, no camera, no
# facing and no animation (bible B2146), and the view is parked by `ext 31` in the same record, so he
# is simply not in frame. 128 px below his mark puts his sprite top at y 584 against a view bottom of
# y 503. `_check_design` proves the spot is open, reachable and below the frame before a byte is
# written. He is NOT removed: `ext 52` on the player object is in no vanilla record and this module
# does not invent one.
HIDE_SPOT = (FINALE_TRUNKS_SPOT[0], FINALE_TRUNKS_SPOT[1] + 128)

# ===== constants: the table the scene is written into =====
TABLE_WORDS = plateau.TABLE_WORDS                            # 27, table D2's own word count
# Word 2 used to carry record B3, "Trunks raises his arms". The owner's section 7 ruling takes the
# motion out: both of his frames are HELD, the hands-down one is already on screen from record B1 and
# the hands-up one is the beam's own pose. So word 2 keeps its END and the chain skips it.
STAGE_INDEX, KAMEHAME_INDEX = 0, 1
SHOUT_INDEX, BLAST_INDEX, WORDS_INDEX, CREDITS_INDEX = 3, 4, 5, 6
CHAIN = (STAGE_INDEX, KAMEHAME_INDEX, SHOUT_INDEX, BLAST_INDEX, WORDS_INDEX, CREDITS_INDEX)
END_TEXT_INDEX = 24                                          # the vanilla "@^The End." record

# ===== constants: the beats =====
STAGE_FADE = 30                                   # record K's own fade, which covers the same swap
KAMEHAME_STATE = 30                               # state 30 = anim 18, Cell's Kamehameha pose (B0149)
HURT_STATE = 2                                    # state 2 = anim 2, "set28 a2 d0" (B2156)
BEAM_FRAMES = 140                                 # the ext 137 second argument, both vanilla sites'
BEAM_REACH = 20                                   # LIKELY: the hold before the first hit. The beam's
                                                  # travel time is NOT measured; this is a beat.
HIT_BEAT, BOOM_BEAT = 20, 80                      # vanilla's own waits between the death blocks
WHITE = plateau.WHITE                             # 10, the flash length GOKU_TRANSFORM uses
# The power down may not run while the beam object still holds the actor: `ext 73` rebuilds the
# player. The scripted waits before it are BEAM_REACH + 2 x WHITE + 3 x HIT_BEAT + BOOM_BEAT = 180
# frames, and the beam runs BEAM_FRAMES = 140, so the beam is gone first. Arithmetic on the ops' own
# frame counts, not a guess: `ext 69` is frames, and `ext 42` and `ext 43` are frames (bible B1978).
# The blocks' own frames are not counted, so the real margin is larger than the number below.
POWER_DOWN_MARGIN = BEAM_REACH + 2 * WHITE + 3 * HIT_BEAT + BOOM_BEAT

# ===== constants: THE OWNER'S OWN WORDS (docs\design\2026-11-08-finale-dialogue.md section 5) =====
# Every character below is his. The only byte added is the box break 0x0B, which ends a box and opens
# the next one on an A press (bible B0650), and it is only ever placed at a full stop he wrote.
# Measured on the ROM font rom:0x2CC64 with the game's own wrap rule: the widest box here is 141 px
# over 1 line, and the widest the ending talk renders in vanilla is 294 px over 4 (bible B2095).
BOX = "\x0b"
CELL_PORTRAIT = plateau.CELL_PORTRAIT                        # 38
TRUNKS_BASE_PORTRAIT = plateau.TRUNKS_BASE_PORTRAIT          # 100
TRUNKS_SSJ_PORTRAIT = plateau.TRUNKS_SSJ_PORTRAIT            # 101
# HIS SECTION 7 RULING: "I just want the held pose of him charging the kamehameha, not shooting it.
# It should be a tense Kame.. hame.." and "so split the cell dialgoue to two". Two boxes in one
# record, his two dots each, and the box break is the only byte added.
KAMEHAME_LINE = "Kame.." + BOX + "hame.."                    # 2 boxes, 1 line each
SHOUT_LINE = "THE NIGHTMARE IS OVER CELL!"                   # 185 px, 2 lines. ONE bang: the early
                                                             # copy at rom:0x3B7FF6 has five, and his
                                                             # section 5 line is written with one.
# HIS LOCKED TEXT, 2026-11-08: he took both vocative commas and the closing full stop.
LAST_LINE = ("Now I can finally say that it's really over." + BOX       # 205 px, 2 lines
             + "Thanks to you, father, and to you, Gohan." + BOX        # 209 px, 2 lines
             + "And especially to you, Goku.")                          # 142 px, 2 lines

# ===== constants: the death blocks, measured from vanilla =====
# Perfect Cell's death, record 0x083EBE1C, decoded through the table walk. Each row is one block:
# (the ext 134 camera value, the ops inside it). The ops are (ext number, arguments) with set 30
# replaced by set 28. Vanilla's FOURTH hit loop is dropped, because the owner ruled three ("lets do
# 3 loops isntead of 4 for future cell"); its camera value was 20.
# ONE op is ADDED, to block 1, and the reason is measured. Vanilla's block 1 carries no `ext 57`
# because the 32 iteration loop in front of it already left Cell in the hurt pose. This record has
# no such loop: Cell is holding the Kamehameha pose when the beam lands, and state 30 never ends, so
# without a pose op he would take the whole first loop still charging. The owner asked for the
# opposite: "imperfect cell does the set28 a2 d0 animation, EACH loop with the smoke effect
# explosion". So block 1 takes the same `ext 57 (28, 2)` that vanilla's blocks 2 and 3 carry, in the
# same place in the block.
HIT_BLOCKS = (
    (30, ((112, 31), (95,), (57, HURT_STATE), (94, 10, -10), (112, 20), (94, -8, 10),
          (112, 21), (94, -4, 16))),
    (30, ((112, 31), (95,), (57, HURT_STATE), (94, 16, -16), (112, 21), (94, 20, -8),
          (112, 20), (94, -12, -4))),
    (40, ((112, 31), (95,), (57, HURT_STATE), (94, -10, -16), (112, 20), (94, 10, 16),
          (112, 21), (94, -16, 8))),
)
BOOM_BLOCK = (80, ((95,), (57, HURT_STATE), (112, 21), (94, 0, 0), (94, 16, 16), (94, -16, -16),
                   (94, 16, -16), (94, -16, 16), (52,)))
CAMERA_OP, EFFECT_OP = 134, 94                    # ext 134 pushes a camera command (the rumble, B0756
                                                  # neighbour row); ext 94 builds an effect (B0793)
CAMERA_ARGS = (0, 20)                             # every vanilla ext 134 site carries (0, 20, n)


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v & 0xFFFFFFFF)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytes, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def _written(notes: dict) -> list:
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)[:2]))
    return out


# ===== the gold entry point =====

def gold_source() -> str:
    r"""The Thumb source of the gold beam entry point: handler, command start, builder and tick.

    Each body is the vanilla listing re-typed instruction for instruction. Five things change and
    nothing else does:
      - every `bl` into the base ROM becomes `ldr r3,=SYM ; bl via_r3`, because a Thumb `bl` reaches
        about 4 MB and this code sits about 8 MB from the base. r3 is dead at each of those sites,
        and `@0x080079B8` (`push {r4,r5}` then r0 and r1 only) does not read it either;
      - the beam call has r0 to r3 all live, so its target is parked in r12 FIRST and called through
        `via_r12`. r12 is written before the four argument moves and nothing between touches it;
      - `mov r2,#0x0` in the builder is `mov r2,#0x1`. That is argument 6, and non-zero picks the
        gold record set `0x08703B60` and `0x08704604` (bible FBM);
      - ONE instruction is ADDED to `gb_start`, `sub r0,#BEAM_RISE`, between the `asr` that halves
        the rect's two y corners and the `str` that hands the pair to the builder. It lifts the
        beam's start to Trunks' raised hands. Nothing else reads r0 between those two points, and
        `mov r0,#0x0` later overwrites it, so the lift reaches the spawn y and nothing else. The
        flags it writes are dead: no conditional branch follows it in this body. See BEAM_RISE;
      - ONE instruction is ADDED to `gb_tick`, the SAME `sub r0,#BEAM_RISE`, straight after the
        `add r0,r2,r0` that forms the fire y from the spawn y and the muzzle dy, and before the
        `str r0,[sp,#0x8]` that keeps it. Both the `[sp,#0x8]` copy and the `[sp,#0x18]` copy that
        `add r2,sp,#0x14` hands to the fire call therefore carry the lifted y, while `add r1,r0,#0`
        leaves the fire x alone. The flags are dead again: nothing between the lift and the call
        branches on them.
    The lift is applied for EVERY facing, in the tick as in the start, instead of cloning the muzzle
    offset table and lifting direction 1 only. That keeps ONE number for the owner to nudge, keeps
    the two copies symmetric, and leaves the vanilla table `0x08701DF0` with no copy to drift from.
    `gb_handler`'s `stmia r0!,{r1,r2}` plus `sub r0,#0x8` is written as two `str`: the same two words
    at the same two offsets, and r0 unchanged either way.
    The forced state 30 at the end of `gb_start` is KEPT, byte for byte in meaning, because both
    vanilla `ext 137` sites keep it and override it on their very next op. This scene does the same.
    """
    return r"""
; ===== the handler: ext GOLD_OP (set, n), a copy of @0x0800A3A2 =====
gb_handler:
    push {r3,r4,r5,lr}
    ldr r1,[r0,#0x0]
    sub r1,#0x1
    lsl r2,r1,#2
    str r1,[r0,#0x0]
    add r2,r2,r0
    ldr r4,[r2,#0x4]            ; the second argument, n
    sub r1,#0x1
    str r1,[r0,#0x0]
    lsl r1,r1,#2
    add r0,r1,r0
    ldr r0,[r0,#0x4]            ; the first argument, the shooter's set
    ldr r3,=FIND_ACTOR
    bl via_r3
    add r5,r0,#0
    mov r0,#0x14
    ldr r3,=ALLOC
    bl via_r3
    cmp r0,#0x0
    beq gb_queue
    ldr r1,=VTABLE              ; the REBASED copy of the ext 137 command vtable
    mov r2,#0x0
    str r1,[r0,#0x0]
    str r2,[r0,#0x4]
    str r4,[r0,#0xc]
    str r2,[r0,#0x8]
    sub r4,#0x8
    str r4,[r0,#0x10]
gb_queue:
    add r1,r0,#0
    ldr r0,=SCRIPT_GLOBALS
    add r2,r5,#0
    ldr r0,[r0,#0xc]
    ldr r3,=ACTOR_QUEUE
    bl via_r3
    pop {r3,r4,r5,pc}

; ===== the command start: vtable slot 1, a copy of @0x0801D788 =====
gb_start:
    push {r4,r5,lr}
    add r5,r0,#0
    sub sp,#0x24
    add r0,sp,#0xc
    add r4,r1,#0
    ldr r3,=ACTOR_BOX
    bl via_r3
    ldr r0,[sp,#0xc]
    ldr r2,[sp,#0x14]
    ldr r3,[sp,#0x18]
    add r2,r0,r2
    ldr r0,[sp,#0x10]
    str r2,[sp,#0x4]
    add r0,r0,r3
    str r0,[sp,#0x8]
    asr r2,r2,#1
    asr r0,r0,#1
    sub r0,#BEAM_RISE           ; THE BEAM STARTS AT HIS HANDS, not his feet. See BEAM_RISE.
    str r2,[sp,#0x4]
    str r2,[sp,#0x1c]
    mov r2,#0x0
    str r0,[sp,#0x8]
    str r0,[sp,#0x20]
    add r3,r4,#0
    mov r0,#0x0
    add r1,sp,#0x1c
    bl gb_build                 ; the GOLD builder, not @0x0801D84C
    add r1,r0,#0
    str r0,[r5,#0x8]
    ldr r0,=WORLD_HEAD
    ldr r0,[r0,#0x0]
    ldr r3,=WORLD_ADD
    bl via_r3
    ldr r1,[r4,#0x0]
    add r0,r4,#0
    ldr r2,[r1,#0x28]
    add r2,r2,r1
    mov r1,#0x1e                ; state 30, exactly as vanilla forces it
    bl via_r2
    add sp,#0x24
    pop {r4,r5,pc}

; ===== the builder: a copy of @0x0801D84C with argument 6 = 1 =====
gb_build:
    push {r4,r5,r6,r7,lr}
    add r7,r2,#0
    add r6,r1,#0
    add r5,r3,#0
    add r4,r0,#0
    cmp r0,#0x0
    sub sp,#0xc
    bne gb_have
    mov r0,#0x50
    ldr r3,=ALLOC
    bl via_r3
    add r4,r0,#0
    bne gb_have
    add r0,r4,#0
gb_done:
    add sp,#0xc
    pop {r4,r5,r6,r7,pc}
gb_have:
    ldr r0,=BEAM_BUILD
    mov r12,r0
    mov r1,#0x1
    lsl r1,r1,#10               ; argument 5 = 0x400
    mov r2,#0x1                 ; argument 6 = 1: THE GOLD SET. Vanilla is 0.
    str r2,[sp,#0x4]
    str r1,[sp,#0x0]
    add r1,r6,#0
    add r2,r7,#0
    add r3,r5,#0
    add r0,r4,#0
    bl via_r12
    ldr r0,=BEAM_VTABLE
    str r0,[r4,#0x0]
    add r0,r4,#0
    b gb_done

; ===== the command tick: vtable slot 2, a copy of @0x0801D7DC =====
; It counts the command's +0xC down, and on the tick that equals +0x10 it recomputes the point FROM
; THE ACTOR and fires. Nothing it uses comes from gb_start, which is why the beam needs its own lift.
gb_tick:
    push {r4,r5,lr}
    add r4,r0,#0
    ldr r0,[r0,#0xc]
    add r5,r1,#0
    cmp r0,#0x0
    sub sp,#0x1c
    beq gb_tick_out
    sub r0,#0x1
    str r0,[r4,#0xc]
    ldr r1,[r4,#0x10]
    cmp r0,r1
    bne gb_tick_spent
    add r1,r5,#0
    add r0,sp,#0xc
    ldr r3,=SPAWN_POINT
    bl via_r3                   ; the spawn point, rebuilt from the actor's own hurtbox
    ldrb r0,[r5,#0x10]          ; the actor's facing
    ldr r1,=WORLD_HEAD
    add r1,#0x4                 ; the VANILLA muzzle offset table 0x08701DF0, read, never written
    lsl r0,r0,#3
    add r0,r0,r1
    ldr r1,[sp,#0xc]
    ldr r2,[r0,#0x0]
    add r1,r1,r2                ; the fire x
    ldr r2,[sp,#0x10]
    ldr r0,[r0,#0x4]
    str r1,[sp,#0x4]
    add r0,r2,r0                ; the fire y is formed HERE
    sub r0,#BEAM_RISE           ; THE FIRED BEAM STARTS AT HIS HANDS, not his feet. See BEAM_RISE.
    str r0,[sp,#0x8]
    add r0,r1,#0
    ldr r1,[sp,#0x8]
    str r0,[sp,#0x14]
    str r1,[sp,#0x18]           ; the pair the fire call stores into the beam
    ldrb r1,[r5,#0x10]
    ldr r0,[r4,#0x8]
    add r2,sp,#0x14
    ldr r3,=BEAM_FIRE
    bl via_r3
gb_tick_out:
    add sp,#0x1c
    pop {r4,r5,pc}
gb_tick_spent:
    cmp r0,#0x0
    bne gb_tick_out
    ldr r0,[r4,#0x8]
    ldr r3,=BEAM_DONE
    bl via_r3
    b gb_tick_out

; ===== the trampolines: a Thumb bl cannot reach the base ROM from here =====
via_r3:
    bx r3
via_r2:
    bx r2
via_r12:
    bx r12
"""


def gold_vtable(vtable_at: int, start_at: int, tick_at: int) -> bytes:
    """The ext 137 command vtable, copied and REBASED, slot 1 the gold start and slot 2 the gold tick.

    A command vtable stores offsets relative to its OWN address with the Thumb bit, so a verbatim
    copy breaks every slot. Each word becomes `old + VTABLE_AT + ROM_BASE - new`, which resolves to
    the same method it always did. Slot 2 matters as much as slot 1: the tick is what positions the
    beam at the moment it FIRES, so a vtable that keeps the vanilla tick keeps the vanilla position
    whatever the start computed."""
    base = vtable_at + ROM_BASE
    mine = {VTABLE_START_SLOT: start_at, VTABLE_TICK_SLOT: tick_at}
    out = []
    for slot, old in enumerate(VANILLA_VTABLE):
        want = (mine[slot] + ROM_BASE) | 1 if slot in mine else (old + VTABLE_AT + ROM_BASE)
        out.append(_word(want - base))
    return b"".join(out)


def resolved(vtable: bytes, vtable_at: int) -> list:
    """What each slot of a copied vtable resolves to, which is how a test reads it back."""
    base = vtable_at + ROM_BASE
    return [(struct.unpack_from("<I", vtable, 4 * k)[0] + base) & 0xFFFFFFFF
            for k in range(VTABLE_WORDS)]


# ===== the two held-pose sets =====

def row_records(rom: bytes, set_off: int, anim: int, direction: int) -> list:
    """Every record of one animation row of one set, in order, as set_records gives them."""
    return [r for r in set_records(rom, set_off)
            if r["anim"] == anim and r["dir"] == direction]


def row_start(rom: bytes, set_off: int, anim: int, direction: int) -> int:
    """The file offset of one row's record list, and proof that no other row shares it.

    A set's animation table often points several rows at ONE list: set 133 gives anims 11 and 21 the
    same list in all four directions. Writing such a list would change every row that names it, so a
    row this module holds has to be its own."""
    s = read_set(rom, set_off)
    entry = anim * s["dirs"] + direction
    start = s["ptrs"][entry]
    if start is None:
        raise ValueError(f"set rom:0x{set_off:X} has no anim {anim} dir {direction}")
    if s["ptrs"].count(start) != 1:
        raise ValueError(f"set rom:0x{set_off:X} anim {anim} dir {direction} shares its record list"
                         f" with {s['ptrs'].count(start) - 1} other row(s): it may not be held")
    return start


def _row_digest(rom: bytes, set_off: int) -> dict:
    """{(anim, dir): [frame header, ...]} for every row of a set, which is how a vanilla set is
    proved untouched: read it before the clones land and read it again afterwards."""
    out = {}
    for r in set_records(rom, set_off):
        out.setdefault((r["anim"], r["dir"]), []).append(r["header"])
    return out


def hold_row(rom: bytearray, src_off: int, clone_off: int, row: tuple, source: tuple,
             header: int) -> dict:
    """Fill one row of a CLONE with copies of one record, so the row shows a single held picture.

    `row` is (anim, dir) in the clone, `source` is (anim, dir, index) in the SOURCE set, and `header`
    is the frame header that record has to carry. The record is copied whole, all twelve bytes, so
    its own dx, dy, size and attribute bits travel with it and a 16x32 frame sits in a 32x32 row
    without a geometry edit.

    The record COUNT is read from the SOURCE set, where the next row's list bounds the walk exactly.
    Nothing is written until both rows are proved to be their own lists and the source record is
    proved to carry `header`."""
    anim, direction = row
    count = len(row_records(rom, src_off, anim, direction))
    if not count:
        raise ValueError(f"the source set has no anim {anim} dir {direction} to size the row")
    row_start(rom, src_off, anim, direction)                 # the source row is its own list too
    at = row_start(rom, clone_off, anim, direction)
    picks = [r for r in row_records(rom, src_off, source[0], source[1]) if r["index"] == source[2]]
    if len(picks) != 1:
        raise ValueError(f"the source set has no record {source}")
    if picks[0]["header"] != header:
        raise ValueError(f"record {source} carries frame 0x{picks[0]['header']:06X},"
                         f" expected 0x{header:06X}")
    want = bytes(rom[picks[0]["rec"]:picks[0]["rec"] + RECORD_BYTES])
    for k in range(count):
        rom[at + k * RECORD_BYTES:at + (k + 1) * RECORD_BYTES] = want
    held = row_records(rom, clone_off, anim, direction)
    if len(held) < count or any(r["header"] != header for r in held[:count]):
        raise ValueError(f"the held row rom:0x{at:X} does not read back as {count} x 0x{header:06X}")
    return {"row": row, "source": source, "header": header, "records": count, "at": at}


# ===== the scene =====

def _block(camera: int, ops: tuple, actor: int = CELL_HOLD_ID) -> bytes:
    """One death block: the camera command, then the hits and effects, bracketed by ext 63 and 64.

    Every op is vanilla's with the finale's own Cell in place of set 30. `ext 95` and `ext 52` take
    the set alone, and `ext 94` takes the set and a signed offset pair."""
    body = b"".join(ext(n, actor, *args) for n, *args in ops)
    return (call("block_begin") + ext(CAMERA_OP, *CAMERA_ARGS, camera) + body + call("block_end"))


def stage(nxt: int = KAMEHAME_INDEX) -> bytes:
    r"""B1, table D2 word 0: the bar and the HUD go, then a fade covers the VERTICAL staging.

    This is ending_fight's record K reshaped for the owner's section 5 and section 7. The bar and the
    HUD come down the same way, the fade covers the same swap of the beaten enemy for a plain NPC
    Cell, and the view is parked on the pair at speed 40 for record K's own reason: it parks from
    wherever the follow camera was, which on his 1280 px map can be a pan of hundreds of px.

    The pair is VERTICAL, Cell above and Trunks below, because the beam flies along the ACTOR'S OWN
    facing and direction 1 is UP. Both spots are proved on his map by `_check_design` before anything
    is written, and so is HIDE_SPOT.

    WHO STANDS WHERE. Both fighters are NPCs on the finale's own cloned sets, and the player steps
    off the parked view to HIDE_SPOT. See the CLONE constants for why the player cannot wear a cloned
    set and why neither vanilla row may be written.

    CELL TAKES HIS CHARGE THROUGH `ext 121`, never `ext 57`. State 30's tick has no end call, so an
    op that waits for the state to finish waits for ever (bible B0688); `ext 121` sets a state and
    does not wait (bible B0750), which is how vanilla's own seq 20 poses both fighters. On
    CELL_HOLD_ID state 30 reads a row whose seven records are all the cupped-hands charge, so the
    pose is held with no flicker and he never reaches a release frame.

    TRUNKS NEEDS NO POSE OP AT ALL. An `ext 51` spawn stands in state 0, which reads anim 0, and on
    TRUNKS_HOLD_ID that row is two copies of his hands-down frame. So he holds "his hands down" from
    the moment the fade lifts, with no op to go wrong.

    The staging order is bible B2170's: every staging op, then the camera park, then the reveal."""
    return code(nxt,
                ext(88), call("header_bit1", 0),
                fade_out(STAGE_FADE),
                ext(62, PLAYER, *HIDE_SPOT),
                ext(52, CELL_SET),
                ext(51, CELL_HOLD_ID, *FINALE_CELL_SPOT), ext(55, CELL_HOLD_ID, DOWN),
                ext(121, CELL_HOLD_ID, KAMEHAME_STATE),
                ext(51, TRUNKS_HOLD_ID, *FINALE_TRUNKS_SPOT), ext(55, TRUNKS_HOLD_ID, UP),
                ext(31, *FINALE_VIEW),
                fade_in(STAGE_FADE))


def kamehame(nxt: int = SHOUT_INDEX) -> bytes:
    """B2, word 1: Cell's line, in TWO boxes.

    The owner, section 7: "I just want the held pose of him charging the kamehameha, not shooting it.
    It should be a tense Kame.. hame.." and "so split the cell dialgoue to two". One record carries
    both boxes, the way vanilla word 22 carries two, and the A press between them is the pause. He is
    holding the charge through every frame of it and he never fires."""
    return text(nxt, CELL_PORTRAIT, KAMEHAME_LINE)


def shout(nxt: int = BLAST_INDEX) -> bytes:
    """B4, word 3: 'Trunks: "THE NIGHTMARE IS OVER CELL!"' (the owner, sections 5 and 7).

    "then trunks interupts with the nightmare quote" and "cell never gets a chance to shoot the
    kamehameha". Trunks is still holding his hands-down frame here and Cell is still charging."""
    return text(nxt, TRUNKS_SSJ_PORTRAIT, SHOUT_LINE)


def blast(gold_op: int, nxt: int = WORDS_INDEX) -> bytes:
    """B5, word 4: the gold beam, the three hit loops, the explosion, and the power down.

    1. THE BEAM FIRES UP. `ext 55 (TRUNKS_HOLD_ID, UP)` first, because the tick `@0x0801D7DC` reads
       the actor's facing byte at +0x10 and indexes the direction run with it. Direction 1's body
       pieces sit at dy -16 and dy -32 and carry no V flip, so the beam grows upward (bible FBM).
    2. THE FORCED POSE IS THE POSE WE WANT, and that is the whole of the fix. The op leaves the
       shooter in state 30, anim 18, and state 30 never ends. On TRUNKS_HOLD_ID that row is seven
       copies of his hands-up frame, so "his hands up, he shoots the blast" is held for the whole
       beam and on through the death loop. wip3 overrode the forced state with `ext 121 (0, 4)` and
       that override is GONE: state 4 cycles the arms down, up, down, up over 64 frames and then
       drops to standing, which is the "waving his hands around" he rejected.
    3. THEN VANILLA'S OWN DEATH LOOP, with three hit blocks instead of four and then the fifth
       block, the explosion, which removes Cell. See HIT_BLOCKS and BOOM_BLOCK.
    4. THE POWER DOWN IS AN NPC SWAP UNDER A WHITE FLASH, which is vanilla's own shape: the ending's
       tail removes Super Saiyan Trunks and spawns base Trunks in the same place. `ext 42` fades to
       white, the swap happens under it and `ext 43` fades back (bible B1978), and base Trunks faces
       DOWN, toward the camera, for his closing line. The player's own record follows with
       `ext 73 (3, 132)`, off screen, so his body agrees with the one on the mark.
       The swap runs POWER_DOWN_MARGIN frames of scripted waits after the beam starts, and the beam
       runs BEAM_FRAMES, so the object that holds the shooter is gone before the shooter is."""
    blocks = b"".join(_block(camera, ops) + wait(HIT_BEAT) for camera, ops in HIT_BLOCKS)
    boom = _block(*BOOM_BLOCK) + wait(BOOM_BEAT)
    return code(nxt,
                ext(55, TRUNKS_HOLD_ID, UP),
                ext(gold_op, TRUNKS_HOLD_ID, BEAM_FRAMES),
                wait(BEAM_REACH),
                call("palette_fx", WHITE), call("flash_wait", WHITE),
                blocks, boom,
                call("palette_fx", WHITE),
                ext(52, TRUNKS_HOLD_ID),
                ext(51, BASE_TRUNKS, *FINALE_TRUNKS_SPOT), ext(55, BASE_TRUNKS, DOWN),
                ext(73, TRUNKS_PARTY, BASE_TRUNKS),
                call("flash_wait", WHITE))


def last_words(nxt: int = CREDITS_INDEX) -> bytes:
    """B6, word 5: his closing line, on the BASE portrait, because he has powered down."""
    return text(nxt, TRUNKS_BASE_PORTRAIT, LAST_LINE)


def credits(rom: bytes, nxt: int = END_TEXT_INDEX) -> bytes:
    """B7, word 6: the ending's OWN tail, unchanged, then the vanilla "The End." text.

    `ending_fight.tail` is the vanilla tail of record 23 with the player turned instead of the
    removed NPC and the four set 132 and set 133 ops dropped. It opens with `wait(80)`, plays
    `music(15)`, fades out over 300 frames and ends with `ext 45`, which DMAs the shared OBJ palette
    back so that "The End." is not drawn black on black.

    `music(15)` is the owner's "back to the credits music that normally plays": it is what this
    ending itself plays at `rom:0x3B80DD` the moment Cell dies. Perfect Cell's own death plays 37,
    but that is the Cell Games cue and not this scene's.

    IT KEEPS VANILLA'S OWN `remove(132)`. `ext 45` DMAs the shared OBJ palette back and lights EVERY
    sprite on a black screen, so whoever is still standing there is drawn over "The End." Vanilla
    removes its fighters between the fade out and `ext 45` for that reason, and this scene ends with
    base Trunks on the mark, so `tail(rom, keep_base_remove=True)` leaves that one op in place. The
    player is off the parked view at HIDE_SPOT, so nothing else is in frame."""
    return bytes([nxt, 0, 0]) + tail(rom, keep_base_remove=True) + b"\x11"


# ===== checks =====

def _check_design(doc: dict) -> dict:
    """His map, measured where the finale stands on it. Nothing here changes a byte of his work."""
    open_set = plateau.open_cells(doc)
    art = plateau.art_cells(doc)
    seed = (plateau.PLATEAU_CELL_SPOT[0] // 8, plateau.PLATEAU_CELL_SPOT[1] // 8)
    reach = plateau.reachable(open_set, seed)
    for spot, env, who in FINALE_SPOTS:
        cells = plateau.envelope_cells(spot, env)
        closed = [c for c in cells if c not in open_set]
        unreached = [c for c in cells if c not in reach]
        covered = [c for c in cells if c in art]
        if closed or unreached or covered:
            raise ValueError(f"{who} on {spot} stands on {len(closed)} closed, {len(unreached)}"
                             f" unreachable and {len(covered)} art covered cells of his map")
    # The beam column: BG0 and BG1 are priority 1 on his map, so art there would draw OVER the beam.
    half = BEAM_WIDTH // 2
    column = [(cx, cy)
              for cy in range(FINALE_VIEW[1] // 8, FINALE_TRUNKS_SPOT[1] // 8 + 1)
              for cx in range((FINALE_TRUNKS_SPOT[0] - half) // 8,
                              (FINALE_TRUNKS_SPOT[0] + half) // 8 + 1)]
    hidden = [c for c in column if c in art]
    if hidden:
        raise ValueError(f"the beam column holds {len(hidden)} cells where BG0 or BG1 draws over it")
    # The parked view has to hold both fighters whole, head to foot.
    for spot, env, who in FINALE_SPOTS:
        if spot[1] - env[2] < FINALE_VIEW[1] or spot[1] + env[3] > FINALE_VIEW[1] + plateau.VIEW[1]:
            raise ValueError(f"{who} does not fit the view {FINALE_VIEW} from top to bottom")
        if spot[0] - env[0] < FINALE_VIEW[0] or spot[0] + env[1] > FINALE_VIEW[0] + plateau.VIEW[0]:
            raise ValueError(f"{who} does not fit the view {FINALE_VIEW} from side to side")
    # Where the player waits: open ground, reachable, and wholly below the parked view.
    hide = plateau.envelope_cells(HIDE_SPOT, plateau.TRUNKS_ENVELOPE_LR)
    off = [c for c in hide if c not in open_set or c not in reach]
    if off:
        raise ValueError(f"the player's wait spot {HIDE_SPOT} stands on {len(off)} closed or"
                         f" unreachable cells of his map")
    if HIDE_SPOT[1] - plateau.TRUNKS_UP <= FINALE_VIEW[1] + plateau.VIEW[1]:
        raise ValueError(f"the player's wait spot {HIDE_SPOT} is not below the view {FINALE_VIEW}")
    return {"open_cells": len(open_set), "reachable": len(reach), "art_cells": len(art),
            "beam_column_cells": len(column), "cell_spot": FINALE_CELL_SPOT,
            "trunks_spot": FINALE_TRUNKS_SPOT, "hide_spot": HIDE_SPOT,
            "view": FINALE_VIEW, "gap": GAP}


def live_ext_table(rom: bytes, alloc) -> tuple:
    """(the live table offset, its word count, the module that owns it or None for the vanilla one).

    Both pool words have to agree, or two readers of the same op would run two different tables."""
    at = _u32(rom, EXT_POOLS[0]) - ROM_BASE
    for p in EXT_POOLS[1:]:
        if _u32(rom, p) - ROM_BASE != at:
            raise ValueError(f"ext table pool rom:0x{p:X} names rom:0x{_u32(rom, p) - ROM_BASE:X}"
                             f" and rom:0x{EXT_POOLS[0]:X} names rom:0x{at:X}")
    if at == BASE_EXT_TABLE:
        return at, BASE_EXT_OPS, None
    owner = next((name for name, n in alloc.notes.items()
                  if isinstance(n, dict) and n.get("ext_table") == at), None)
    if owner is None:
        raise ValueError(f"the live ext table rom:0x{at:X} is not the vanilla one and no module's"
                         f" notes claim it: stop and report")
    sizes = [n for s, n, _name in alloc.notes[owner]["sites"] if s == at]
    if len(sizes) != 1 or sizes[0] % 4:
        raise ValueError(f"{owner} does not declare the ext table rom:0x{at:X} as one whole site")
    return at, sizes[0] // 4, owner


def _check(rom: bytearray, alloc) -> tuple:
    if "finale_blast" in alloc.notes:
        raise ValueError("finale_blast already ran")
    for needed in ("ending_fight", "plateau"):
        if needed not in alloc.notes:
            raise ValueError(f"{needed} has not run: this module reads its notes and must come after it")

    # The three bodies the gold entry point is copied from, and the colour byte it changes.
    for at, want in ((HANDLER_AT, HANDLER_BYTES), (START_AT, START_BYTES), (TICK_AT, TICK_BYTES),
                     (BUILD_AT, BUILD_BYTES)):
        _expect(rom, at, bytes.fromhex(want))
    if rom[COLOUR_BYTE] != BLUE:
        raise ValueError(f"rom:0x{COLOUR_BYTE:X} is 0x{rom[COLOUR_BYTE]:02X}, and the beam colour"
                         f" argument has to still be blue for this module's reading to hold")
    for k, want in enumerate(VANILLA_VTABLE):
        _expect(rom, VTABLE_AT + 4 * k, _word(want))
    _expect(rom, 0xA740, _word(NEXT_VTABLE + ROM_BASE))      # the vtable is five words, not more

    # The ext op table, live, and the parallel table that never moves.
    at, count, owner = live_ext_table(rom, alloc)
    for p in SECOND_POOLS:
        _expect(rom, p, _word(SECOND_TABLE + ROM_BASE))
    lo, hi = at + ROM_BASE, at + 4 * count + ROM_BASE
    words = memoryview(bytes(rom[:len(rom) & ~3])).cast("I")
    names = [4 * i for i, w in enumerate(words) if lo <= w < hi]
    if names != sorted(EXT_POOLS):
        raise ValueError(f"the words naming the live ext table are {[hex(o) for o in names]},"
                         f" expected the two pool words: a reader would be left behind")

    # Table D2 is plateau's, and the seven words this module takes have to be what it left.
    d2 = alloc.notes["plateau"]["death_table"]
    if alloc.notes["plateau"]["death_words"] != TABLE_WORDS:
        raise ValueError("table D2 is not the 27 word table this module is written against")
    if _u32(rom, d2) != alloc.notes["ending_fight"]["death"] + ROM_BASE:
        raise ValueError("table D2 word 0 is not ending_fight's record K any more")
    for index in CHAIN[1:]:
        if _u32(rom, d2 + 4 * index):
            raise ValueError(f"table D2 word {index} is rom:0x{_u32(rom, d2 + 4 * index):X},"
                             f" not the END word this module needs")
    if _u32(rom, d2 + 4 * END_TEXT_INDEX) == 0:
        raise ValueError(f"table D2 word {END_TEXT_INDEX} is END, so the chain has no ending to"
                         f" hand on to")

    # The LIVE set table, which gohan_gi relocated, and the two sources this module clones.
    if GI_SETS not in alloc.notes:
        raise ValueError(f"{GI_SETS} has not run: this module appends to the set table it relocated")
    set_table = _u32(rom, SET_TABLE_LITERAL) - ROM_BASE
    if set_table != alloc.notes[GI_SETS]["set_table"]:
        raise ValueError(f"rom:0x{SET_TABLE_LITERAL:X} names rom:0x{set_table:X}, not {GI_SETS}'s"
                         f" own table rom:0x{alloc.notes[GI_SETS]['set_table']:X}")
    _expect(rom, set_table + 4 * (GI_LAST - FIRST_SET_ID),
            _word(alloc.notes[GI_SETS][f"set_{GI_LAST}"] + ROM_BASE))
    for new_id in (CELL_HOLD_ID, TRUNKS_HOLD_ID):
        if new_id - FIRST_SET_ID < LIVE_SET_IDS:
            raise ValueError(f"set id {new_id} is already a word of the live table")
    for src_id, row, source, header in ((CELL_SET, CELL_HOLD_ROW, CELL_CHARGE, CHARGE_HEADER),
                                        (SSJ_TRUNKS, TRUNKS_IDLE_ROW, TRUNKS_HANDS_DOWN,
                                         HANDS_DOWN_HEADER),
                                        (SSJ_TRUNKS, TRUNKS_BEAM_ROW, TRUNKS_HANDS_UP,
                                         HANDS_UP_HEADER)):
        src = set_offset(rom, src_id)
        row_start(rom, src, *row)                            # the row is its own record list
        picks = [r for r in row_records(rom, src, source[0], source[1]) if r["index"] == source[2]]
        if len(picks) != 1 or picks[0]["header"] != header:
            raise ValueError(f"set {src_id} record {source} is not frame 0x{header:06X}")

    # Nothing this module writes in the base ROM may land anywhere but chapter_cards' pool words
    # and gohan_gi's own set table literal.
    mine = [(p, 4) for p in EXT_POOLS] + [(SET_TABLE_LITERAL, 4)]
    allowed = ({owner} if owner else set()) | {GI_SETS}
    for name, (start, size) in _written(alloc.notes):
        for a, n in mine:
            if start < a + n and a < start + size and name not in allowed:
                raise ValueError(f"rom:0x{a:X} is also written by {name}: stop and report")
    return at, count, owner, d2, set_table


# ===== patch =====

def apply(rom: bytearray, alloc) -> None:
    at, count, owner, d2, set_table = _check(rom, alloc)
    design = _check_design(plateau.document())
    gold_op = count
    sites = []

    def place(data: bytes, name: str) -> int:
        where = alloc.alloc(len(data))
        if set(rom[where:where + len(data)]) != {0xFF}:
            raise ValueError(f"rom:0x{where:X} (0x{len(data):X} bytes) is not free")
        rom[where:where + len(data)] = data
        sites.append((where, len(data), name))
        return where

    def put(where: int, data: bytes, name: str) -> None:
        rom[where:where + len(data)] = data
        sites.append((where, len(data), name))

    # The vtable goes first, because the handler loads its address as a literal.
    vtable_at = alloc.alloc(4 * VTABLE_WORDS)
    syms = dict(SYMS, VTABLE=vtable_at + ROM_BASE)
    size = len(assemble(gold_source(), 0x800000, syms)[0])
    code_at = alloc.alloc(size)
    blob, labels = assemble(gold_source(), code_at + ROM_BASE, syms)
    if len(blob) != size:                                    # the pool padding depends on the address
        raise ValueError(f"the gold entry point laid out to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    vtable = gold_vtable(vtable_at, labels["gb_start"] - ROM_BASE, labels["gb_tick"] - ROM_BASE)

    if set(rom[vtable_at:vtable_at + 4 * VTABLE_WORDS]) != {0xFF}:
        raise ValueError(f"rom:0x{vtable_at:X} is not free for the vtable copy")
    put(vtable_at, vtable, "the ext 137 command vtable, copied and rebased"
                           " (slot 1 = the gold start, slot 2 = the gold tick)")
    put(code_at, blob, "the gold beam entry point: handler, command start, builder, tick, pool")

    # THE TWO HELD-POSE SETS. Each clone copies a set's header, animation table and record lists into
    # expansion space and leaves the frame pixels alone, then ONE row of the clone is filled with
    # copies of one record. Nothing in set 28 or set 133 is written: the read back below proves it.
    vanilla_cell = set_offset(rom, CELL_SET)
    vanilla_trunks = set_offset(rom, SSJ_TRUNKS)
    before = {src_id: _row_digest(rom, src)
              for src_id, src in ((CELL_SET, vanilla_cell), (SSJ_TRUNKS, vanilla_trunks))}
    cell_hold = clone_set(rom, vanilla_cell, {}, alloc)
    trunks_hold = clone_set(rom, vanilla_trunks, {}, alloc)
    holds = [hold_row(rom, vanilla_cell, cell_hold, CELL_HOLD_ROW, CELL_CHARGE, CHARGE_HEADER),
             hold_row(rom, vanilla_trunks, trunks_hold, TRUNKS_IDLE_ROW, TRUNKS_HANDS_DOWN,
                      HANDS_DOWN_HEADER),
             hold_row(rom, vanilla_trunks, trunks_hold, TRUNKS_BEAM_ROW, TRUNKS_HANDS_UP,
                      HANDS_UP_HEADER)]
    set_copy = (bytes(rom[set_table:set_table + 4 * LIVE_SET_IDS])
                + _word(cell_hold + ROM_BASE) + _word(trunks_hold + ROM_BASE))
    set_at = place(set_copy, f"the set table copy ({LIVE_SET_IDS + 2} words, {CELL_HOLD_ID} = Cell"
                             f" holding the charge, {TRUNKS_HOLD_ID} = Trunks holding his two frames)")
    put(SET_TABLE_LITERAL, _word(set_at + ROM_BASE), "the set table literal (the grown table)")

    ext_words = [_u32(rom, at + 4 * k) for k in range(count)]
    ext_copy = b"".join(_word(w) for w in ext_words) + _word(labels["gb_handler"] | 1)
    ext_at = place(ext_copy, f"the ext op table copy ({count + 1} words, word {gold_op} = the gold beam)")

    # The scene, in table D2's own word order.
    records = {STAGE_INDEX: (stage(), "record B1 (the bar and the HUD go, the vertical pair is"
                                      " staged under a fade, Cell takes the Kamehameha pose)"),
               KAMEHAME_INDEX: (kamehame(), 'record B2 (Cell: "Kame.." then "hame..")'),
               SHOUT_INDEX: (shout(), 'record B4 (Trunks: "THE NIGHTMARE IS OVER CELL!")'),
               BLAST_INDEX: (blast(gold_op), "record B5 (the gold beam up, three hit loops with"
                                             " explosions and screen rumble, the explosion that"
                                             " removes Cell, then the power down to base)"),
               WORDS_INDEX: (last_words(), "record B6 (Trunks' closing line, base portrait)"),
               CREDITS_INDEX: (credits(rom), "record B7 (the ending's own tail: track 15, the fade"
                                             " and ext 45, then the vanilla The End.)")}
    placed = {index: place(data, name) for index, (data, name) in records.items()}

    for p in EXT_POOLS:
        put(p, _word(ext_at + ROM_BASE), "an ext op table pool word (the relocated table)")
    for index, where in placed.items():
        put(d2 + 4 * index, _word(where + ROM_BASE),
            f"table D2 word {index} (the finale chain, which was"
            f" {'record K' if index == STAGE_INDEX else 'END'})")

    # Read back out of the ROM, not out of the plan.
    if [_u32(rom, ext_at + 4 * k) for k in range(count)] != ext_words:
        raise ValueError("the ext table copy is not the live table word for word")
    if _u32(rom, ext_at + 4 * gold_op) != (labels["gb_handler"] | 1):
        raise ValueError(f"ext word {gold_op} does not name the gold handler")
    slots = resolved(bytes(rom[vtable_at:vtable_at + 4 * VTABLE_WORDS]), vtable_at)
    want = [(old + VTABLE_AT + ROM_BASE) & 0xFFFFFFFF for old in VANILLA_VTABLE]
    want[VTABLE_START_SLOT] = labels["gb_start"] | 1
    want[VTABLE_TICK_SLOT] = labels["gb_tick"] | 1
    if slots != want:
        raise ValueError(f"the rebased vtable resolves to {[hex(s) for s in slots]},"
                         f" expected {[hex(w) for w in want]}")
    for index, where in placed.items():
        if _u32(rom, d2 + 4 * index) != where + ROM_BASE:
            raise ValueError(f"table D2 word {index} did not read back as its record")

    # THE PROOF THAT NO LIVE ROW MOVED. Both vanilla sets have to resolve where they always did, and
    # every record of both vanilla rows has to carry the frame header it carried before the clones.
    if set_offset(rom, CELL_SET) != vanilla_cell or set_offset(rom, SSJ_TRUNKS) != vanilla_trunks:
        raise ValueError("a vanilla set no longer resolves to its own header: stop and report")
    untouched = {}
    for src_id, src in ((CELL_SET, vanilla_cell), (SSJ_TRUNKS, vanilla_trunks)):
        after = _row_digest(rom, src)
        if after != before[src_id]:
            raise ValueError(f"set {src_id} no longer reads as it did before the clones:"
                             f" a vanilla row was written")
        untouched[f"set_{src_id}_rows"] = len(after)
        untouched[f"set_{src_id}_records"] = sum(len(v) for v in after.values())
    for row, name in ((CELL_HOLD_ROW, f"set_{CELL_SET}"), (TRUNKS_BEAM_ROW, f"set_{SSJ_TRUNKS}")):
        src = vanilla_cell if name.endswith(str(CELL_SET)) else vanilla_trunks
        untouched[f"{name}_anim_{row[0]}_dir_{row[1]}"] = [
            f"0x{r['header']:06X}" for r in row_records(rom, src, *row)]
    for set_id, head in ((CELL_HOLD_ID, cell_hold), (TRUNKS_HOLD_ID, trunks_hold)):
        if _u32(rom, set_at + 4 * (set_id - FIRST_SET_ID)) != head + ROM_BASE:
            raise ValueError(f"set table word {set_id} does not name its clone")
    if _u32(rom, SET_TABLE_LITERAL) - ROM_BASE != set_at:
        raise ValueError("the set table literal did not read back as the grown table")

    alloc.notes["finale_blast"] = {
        "ext_table": ext_at, "ext_words": count + 1, "gold_op": gold_op,
        "old_ext_table": at, "old_ext_words": count, "ext_table_owner": owner,
        "code": code_at, "code_size": size, "labels": dict(labels),
        "vtable": vtable_at, "vtable_words": VTABLE_WORDS, "vtable_from": VTABLE_AT,
        "vtable_slots": slots, "handler": labels["gb_handler"] - ROM_BASE,
        "start": labels["gb_start"] - ROM_BASE, "build": labels["gb_build"] - ROM_BASE,
        "tick": labels["gb_tick"] - ROM_BASE, "vanilla_tick": TICK_AT,
        "set_table": set_at, "set_table_words": LIVE_SET_IDS + 2, "old_set_table": set_table,
        "cell_hold": cell_hold, "trunks_hold": trunks_hold,
        "cell_hold_id": CELL_HOLD_ID, "trunks_hold_id": TRUNKS_HOLD_ID,
        "holds": holds, "vanilla_rows": untouched, "hide_spot": HIDE_SPOT, "beam_rise": BEAM_RISE,
        "death_table": d2, "records": placed, "chain": list(CHAIN),
        "end_text_index": END_TEXT_INDEX,
        "cell_spot": FINALE_CELL_SPOT, "trunks_spot": FINALE_TRUNKS_SPOT, "view": FINALE_VIEW,
        "design": design, "beam_frames": BEAM_FRAMES, "power_down_margin": POWER_DOWN_MARGIN,
        "hit_blocks": len(HIT_BLOCKS), "lines": [KAMEHAME_LINE, SHOUT_LINE, LAST_LINE],
        "sites": sorted(sites)}
