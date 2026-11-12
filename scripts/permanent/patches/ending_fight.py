r"""
ending_fight.py - Trial patch: the ending's scripted kill of Imperfect Cell becomes a real player fight.
                  Trunks is the player, Cell keeps his vanilla stats, and the vanilla ki blast still
                  finishes him (the owner's design, docs\tasks\2026-11-05-trunks-boss-fights\design.md,
                  section 7; brief docs\tasks\2026-11-05-ending-fight-1\brief.md).

Usage:   py -3.14 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_ending.txt --out <new .gba>
Input:   the ROM after build_list_dev.txt (r41) AND battle_arena, whose notes this module reads. Run it
         last, so no earlier allocation moves.
API:     apply(rom, alloc) -> None; file offsets in alloc.notes["ending_fight"], every write as
         (offset, length, name) in its "sites". arrive(), fight_start(), death(), death_table() and
         blast()/tail() hold the design, so the tests read it from one place.
Method:  Ending scene table rom:0x3B8140, words 13 and 23, and the arena map battle_arena builds.
         Study: docs\tasks\2026-11-05-trunks-boss-fights\report.md, blockers B2, B3, B4 and B10,
         docs\tasks\2026-11-05-ending-arena\report.md for the arena, and
         docs\tasks\2026-11-06-vanilla-battle-starts\report.md for the battle-start census.
         0. THE 17/18 FIGHT IS VANILLA. The owner scoped the work on 2026-11-06: "there are two
            sections, the scene against 17/18, which we are NOT doing at this time. And the future cell
            scene". The boundary is the map load at rom:0x3B7E5E, inside record 13: every record of the
            fight itself stays byte for byte, and so do record 13's own first two ops.
            ONE record before the boundary moves, and he asked for it himself on 2026-11-08: word 12,
            the line that closes the androids. Its VANILLA RECORD is still untouched; only the table
            word moves, so a save state paused inside it still runs to its end. See LINE12.
         0a. HIS WORDS, SECTIONS 1 TO 3 (docs\design\2026-11-08-finale-dialogue.md). Word 12 and word
            22 carry his own replacement lines, a new caption box says "Three years later..." between
            the androids and Capsule Corp, and the fight opens on track 28. Every character is his.
         0b. THE TRANSITION IS VANILLA'S OWN FASTEST. He called it "very very long", then "stil
            soooooo long", and asked "what is the normal transition length in vanilla???". The
            census of every vanilla map-load transition answers him: the fastest is rom:0x3E424A,
            fade_out(30), no wait, fade_in(30), 60 frames of black. Record A and record A2 run those
            two numbers and spend no wait between them. See REVEAL.
         1. Word 13 names record A instead of the vanilla arrival rom:0x3B7E4A. A opens with the cut
            pair wait(60) and fade_out(30), gives the player the BASE Trunks body, set 132, refills
            him, loads the ARENA with ext 39, takes the HUD away, steps the player off the bottom of
            the frame, starts track 42, parks the view on the fight pair and lights the sprites
            again. No wait runs between the load and the end of the record. See arrive(). The
            LOAD MOVING HERE
            is the whole of v7: the owner played v6 and said "There should not be a fade at all after
            the diague!". The BASE body is rung 5: "Cell: Trunks starts NOT Super Saiyan"
            (owner, 2026-11-07).
         1a. Word 24 names record C, the caption, and word 25 names record A2, which puts the player
            back, gives the HUD back, fades in and walks him. Those two indices are free in this build and
            _check_spare_indices proves it before a byte is written. The vanilla records they named,
            "The End." and the ext 97 exit, keep every byte and are still named BY ADDRESS from table D
            and table D2, so Cell's death still ends the game the way it did.
         2. Word 23 names record F instead of the vanilla scripted kill rom:0x3B8016. F is four ops,
            the shape Piccolo's fight against Android 17 uses and the shape 25 of the 25 vanilla bar
            records in our own build use: ext 104 turns the NPC into the enemy, the bar comes up, the
            HUD comes back, and camera_follow(0) pans the view onto the player. See fight_start().
         3. The enemy is the arena's item 1, condition 1, which only ext 104 builds. This module spawns
            nobody: it gives that enemy its death event by writing table D into the event struct
            battle_arena placed. Vanilla type 60 is not touched: the arena enemy is retyped instead.
         3a. THE FUTURE CELL IS 25 PERCENT WEAKER (the owner, 2026-11-08: "this is cell before he
            absorbs people ... Weaker stats, like 25%"). Vanilla type 60 also spawns on map 10,20,
            the main game's own Imperfect Cell, so the type entry may not be edited in place. A fresh
            entry is allocated on the enemy table's 24-byte stride (celljr_fight's own method), HP,
            STR, POW and END are weakened, and the ARENA ITEM's type word names it. See weak_type().
         4. The enemy's event table D is 27 words, the shape of the ending table, because the event
            runner starts every death event at word 0 and records 24 and 25 carry their own next
            indices (blocker B4). D word 0 = record K, word 24 = the vanilla "The End." text, word 25 =
            the vanilla ext 97 record, every other word = END.
         5. Record K: bar and HUD off, Cell collapses (ext 57 (28, 3), the shape of Android 18's own
            death record rom:0x3D8BC4), then a fade covers the restore of the vanilla geometry: the
            player back on TRUNKS_SPOT facing up, the beaten enemy swapped for an NPC Cell on CELL_SPOT,
            and a fixed view on the pair at DEATH_VIEW, which is VIEW's point at speed 40 because this
            record parks from wherever the follow camera was and may run on a 1280 px map. Then the VANILLA blast block and the VANILLA tail run.
Rules:   Sources: the brief, the design, and the base bytes read in
         scripts\one-time\2026-11-05-ending-fight-1\01_probe.txt and 03_slices.txt, and
         scripts\one-time\2026-11-06-arena-v7\ for the fade census and the ending talk.
         Every source byte, word and record is checked before the first write; a second run raises.
         The blast is the vanilla block with ONE edit, its attacker push, because record A makes the
         player Trunks and no set:133 actor follows him into the arena map. ext 96 with the player as
         the attacker is the shape celljr_fight's finish record already ships. The tail keeps every
         vanilla op except the four that name set:132 and set:133: a power-down pose, the Super Saiyan
         remove, the base respawn and the last remove. Those would bind the player object, whose set is
         Trunks' own (blocker B2), and set:132 has no anim 21.
         No vanilla enemy type entry is written, so every main game fight keeps its own stats. No
         vanilla map entry, item list or item is touched either: the arena owns both Cells. The base
         writes are ending table words 12, 13, 22, 23, 24 and 25, and the PORTRAIT BYTE of the three
         Cell talk records 14, 16 and 20 (the owner, 2026-11-08: "the portrait for trunks when talking
         to cell should use base"). Word 22's portrait moves with its text, onto the new record that
         carries the owner's own line. A portrait id is one byte at a record's +3, so each record keeps
         its address and its length and a save state paused inside one still runs to its end. Every
         record this module adds is a new copy in the expansion area; every vanilla record stays
         where it is.
         No loss handling is added: a loss runs the vanilla game-over table, as the owner decided.
         NOT READ, and flagged for the play test: the vanilla ending built no player at all, so nothing
         in the game ever showed what the HUD does during this talk. Record A builds the player before
         word 14, and whether his HUD shows through records 14 to 22 is unknown. No op is added for it.
"""
import hashlib
import struct

from scene.scene_lib import (TYPE_TEXT, battle_start, call, camera, code, ext, fade_in, fade_out,
                             leader, push, record_end, text, wait, walk_to, words_naming)

# ===== constants: the ending (base bytes, 01_probe.txt and 03_slices.txt) =====
ROM_BASE = 0x08000000
TABLE, TABLE_WORDS = 0x3B8140, 27                  # the ending scene table and its word count
ARRIVE_INDEX = 13                                  # the record that opens the future Cell scene
FIGHT_INDEX, TEXT_INDEX, EXIT_INDEX, END_INDEX = 23, 24, 25, 26
ARRIVE_WORD = TABLE + 4 * ARRIVE_INDEX             # rom:0x3B8174, the Capsule Corp arrival
FIGHT_WORD = TABLE + 4 * FIGHT_INDEX               # rom:0x3B819C, the scripted kill of set 28
REC23, REC23_LEN = 0x3B8016, 0xFF
REC23_SHA1 = "96d07a4392ea2f35f876503e45cf0f28df20a8ec"   # the whole scripted kill, so every reused slice is vanilla
REC24, REC25 = 0x3B8116, 0x3B813A                  # "@^The End.Thanks for playing!" and ext 97

# ===== constants: the two SPARE ending indices (the owner's caption, 2026-11-08) =====
# The caption needs its own table index, and the ending table is 27 words with no free one. Words 24
# and 25 ARE free in this build, and that is measured, not assumed. Vanilla chains 0 to 26 in order,
# so 24 is reached only from record 23 and 25 only from record 24 (future_androids says the same:
# "words 0 to 25 run 1, 2, ... 26 in order"). This module replaces record 23 with record F, whose next
# is 26, so nothing in the ending table reaches 24 or 25 any more. `_check` proves that before a write.
# The vanilla end text is NOT orphaned: table D and table D2 name records REC24 and REC25 by ADDRESS
# at their own words 24 and 25, so Cell's death still runs "The End." and the vanilla exit.
CAPTION_INDEX, REVEAL_INDEX = TEXT_INDEX, EXIT_INDEX

# The two slices of record 23 the new death record reuses. Offsets read from 03_slices.txt.
BLAST = (0x3B80AC, 0x2B)                           # ext 63 ... ext 64: the third attack group, which removes Cell
TAIL = (0x3B80D7, 0x3D)                            # wait 80 ... ext 45: Trunks powers down and the ending fades
ATTACKER_PUSH = (0x3B80AE, "1d03820a388148")       # push 133, 28, 100 before the blast's ext 96
FACE_PUSH = (0x3B80DF, "1d02820a00")               # push 133, 0 before the tail's ext 55
DROPS = ((0x3B80E6, "1d02820a2a0239"),             # push 133, 21 ; ext 57 (the Super Saiyan power-down pose)
         (0x3B80ED, "00850234"),                   # push 133 ; ext 52
         (0x3B80F1, "1d038208837088700233"),       # push 132, 248, 568 ; ext 51 (the vanilla respawn, and
                                                   # the same point as TRUNKS_SPOT; these bytes are DELETED)
         (0x3B810E, "00840234"))                   # push 132 ; ext 52
SOURCE_BYTES = ((ATTACKER_PUSH[0], bytes.fromhex(ATTACKER_PUSH[1])),
                (FACE_PUSH[0], bytes.fromhex(FACE_PUSH[1]))) + tuple(
                    (at, bytes.fromhex(old)) for at, old in DROPS)

# ===== constants: the 17/18 scene, left VANILLA (the owner's scope, 2026-11-06) =====
# "Remember there are two sections, the scene against 17/18, which we are NOT doing at this time. And
# the future cell scene." The boundary is the map load at rom:0x3B7E5E, inside record 13. Every record
# before it belongs to the 17/18 scene and not one byte of it changes. These four are the records that
# name NPC Super Saiyan Trunks, set 133. v5 relocated them onto the player; they are listed here only
# to be CHECKED: the word must still name the record, the record must still hash to its base value,
# and no other module may write either.
# name: (table index, record offset, SHA-1 of the vanilla record)
VANILLA_CONVERSATION = {
    "transform": (4, 0x3B7C1C, "187c73d2daaf5c9033b7645271924a3f3f6ca310"),    # remove 132, spawn 133
    "name_line": (6, 0x3B7C6A, "e90bb11734eee488742f51c26532f4ac2e5c069c"),    # face(133, 1)
    "kill_17": (8, 0x3B7C96, "cfc1f6333ea5f82465738e3a05a15900df017cc1"),      # two attacks on set 11
    "kill_18": (11, 0x3B7D6E, "65ddfc45540d206fb0248ece4349b01ca002e73e"),     # two attacks on set 9
}

# ===== constants: record 13, the one record that straddles the boundary =====
# Vanilla word 13 rom:0x3B7E4A:
#   wait(60) ; fade_out(180) ; load_map(6,1,1,136,432) ; wait(120) ; walk(133,248,568) ; wait(100)
# Its first two ops are the 17/18 side and its load is where the future Cell scene begins. The word is
# repointed at a copy, so the vanilla record itself is never written and a save state paused inside it
# still runs to its end. The copy is CHECKED against the vanilla bytes of those first two ops before
# anything is written, so the boundary cannot drift, and it then EMITS vanilla's own beat and the
# fade of vanilla's fastest map-load transition in their place: wait(60) and fade_out(30). See
# REVEAL.
REC13, REC13_SHA1 = 0x3B7E4A, "9da3bdb83ae64c84f6a61d02abf00a83176accd9"
REC13_HEAD = (0x3B7E4D, 8)                         # wait(60) ; fade_out(180), the pair that is CHECKED
REC13_LOAD_AT = 0x3B7E5E                           # the ext 35 load: the future Cell scene starts here
REC13_ARRIVED = 100                                # the vanilla wait after the walk. There is NO
                                                   # settle wait: see REVEAL and bible B2170

# ===== constants: the arena enemy (battle_arena's notes and base bytes, 07_cell_event.txt) =====
ARENA = "battle_arena"                                      # the module that builds map 6,100 and its enemy
EVENT_RUNNER = 0x080106B3
EVENT_TABLE_AT = 4                                          # the event struct is {event runner, scene table}

# ===== constants: the design =====
PLAYER, TRUNKS = 0, 3                              # the player actor; Trunks' party id (ext 70)
SSJ_TRUNKS, BASE_TRUNKS, CELL = 133, 132, 28      # NPC Super Saiyan Trunks, base Trunks, Imperfect Cell
# The owner's flow, 2026-11-07: "Cell: Trunks starts NOT Super Saiyan". Record A therefore gives the
# player the BASE body, set 132. The androids' own fights still run in 133: future_androids' word 4
# transforms him and nothing between word 4 and word 13 changes him back, so word 13 is where the
# form for the Cell fight is decided. See arrive() step 2.
TRUNKS_SPOT = (248, 568)                           # where the talk leaves the player (battle_arena)
TRUNKS_START = (248, 624)                          # where record 13 loads him: map 6,1 item 5's own spot
MAP_VARIATION = 1                                  # ext 39 load_map_at: the variation to load
CELL_SPOT = (244, 504)                             # where the talk leaves Cell, 64 px above the player
DOWN, UP = 0, 1                                    # ext 55 facings (celljr_fight and chapter_cards agree)
DOWN_STATE = 3                                     # Android 18's death record opens with push 11, 3 ; ext 57
COLLAPSE_HOLD, FADE = 60, 30                       # frames: the collapse holds, then the swap hides behind a fade
VIEW_SPEED = 40                 # the transition cut, below. It was 2.
VIEW = (TRUNKS_SPOT[0] - 112, (CELL_SPOT[1] + TRUNKS_SPOT[1]) // 2 - 80, VIEW_SPEED)   # celljr's offsets
# The DEATH record's park is the same point at a different SPEED, and the speed is the only difference.
# `ext 31` BLOCKS for distance/speed + 1 frames (bible B0766), and record K parks from wherever the
# FOLLOW camera left the view when the enemy died, which is wherever the player was standing. On the
# arena, map 6,100, the clamp is (273, 553) and the worst pan is about 170 px: about 85 frames at
# speed 2. Once the plateau carries round 2 the SAME record runs on map 7,100, whose clamp is
# (1041, 1121): about 255 px from the middle of the arena top and about 770 px from its far south
# east, which is about 128 and about 385 frames, so 2.1 to 6.4 seconds of black after the last blow.
# Speed 40 makes every one of those about 5 frames. It stays a constant of its own, although the
# transition cut now runs record A's park at the same speed, because the two parks answer to two
# different things: this one to the follow camera's unknown start, and VIEW's to the owner's cut.
DEATH_SPEED = 40
DEATH_VIEW = VIEW[:2] + (DEATH_SPEED,)
BAR_ON, HUD_ON, HUD_OFF = ext(85, CELL), ext(86, 1), ext(86, 0)

# ===== constants: the Cell talk's portrait (the owner, 2026-11-08) =====
# "the portrait for trunks when talking to cell should use base". Record A gives him the BASE body,
# so a Super Saiyan portrait disagrees with the sprite on screen. A type 1 to 4 record carries its
# portrait id in its +3 byte (scene_lib PORTRAIT_TYPES), and these four are the only records of the
# CELL talk that Trunks speaks. Words 5, 7, 10 and 12 also read 101 and are NOT touched: they are the
# 17/18 side of the boundary, where he really is Super Saiyan.
# The pair comes from the appearance table, which is where ids 1-7 resolve: entry 15 is set 132 and
# dialog portrait 100, entry 16 is set 133 and dialog portrait 101.
# ===== constants: the three year refill (the owner, 2026-11-08) =====
# "trunks ssj ki is drained after the 3 year split, it should be refrsehed for the cell fight".
# ext 109 (char, n) sets HP and ext 110 (char, n) sets EP, each to min(n, max), and vanilla scripts
# use 5000 as the refill value (bible B0576). chamber_spar's win event runs the same pair.
HP_REFILL, KI_REFILL, REFILL = 109, 110, 5000

APPEARANCE, APPEARANCE_ENTRY, APPEARANCE_DIALOG = 0x1D967C, 20, 2
BASE_ENTRY, SSJ_ENTRY = 15, 16
BASE_PORTRAIT, SSJ_PORTRAIT = 100, 101
PORTRAIT_AT = 3                                    # the portrait byte inside a type 1 to 4 record
# (table index, record offset, record type). Read out of the base ROM, 2026-11-08.
# Word 22 is NOT here any more: section 3 of the design replaces its text, so the word is repointed at
# a new record that carries BASE_PORTRAIT itself. The vanilla record keeps every byte it has.
TALK_PORTRAITS = ((14, 0x3B7E74, 1), (16, 0x3B7EB0, 1), (20, 0x3B7F10, 2))
# The dialog box reads the +3 byte for the LAYOUT (cases 0, 1 and 2-7), for the style switch
# @0x0800B25E (cases 0x28, 0x31, 0x32, 0x35, 0x46, 0x54, 0x56, 0x60 and a jump table over 26-39) and
# for portrait(). 100 and 101 are both outside every one of those cases, so the box is unchanged and
# only the face moves (bible B0339).

# ===== constants: THE OWNER'S OWN WORDS (docs\design\2026-11-08-finale-dialogue.md) =====
# Every character below is his, quoted from the design, typos kept. The only thing added is the box
# break 0x0B, which ends a box and opens a new one on the next A press (bible B0650). A break is only
# ever placed at a mark he wrote himself, so no word and no punctuation changes.
# The box is 4 lines of 144 px a page (bible B2095), and the widest box the talk is seen to render is
# 294 px (ending word 3, "ANDROID 18: I guess he wants to die like everyone else."). Every box below
# is measured under that, on the ROM font rom:0x2CC64.
BOX = "\x0b"

# Section 1, ending word 12. Vanilla: "Now there's just one more thing that needs to be done."
# His replacement, then "... Cell" in a box of its own ("Maybe make ... cell its own line").
LINE12_INDEX, LINE12_REC = 12, 0x3B7E0E
LINE12_WAS = b"Now there's just one more thing that needs to be done."
# HIS LOCKED TEXT, 2026-11-09. He played the build and said "the new dialogue is missing period
# punctuations", so boxes 1 and 2 each end on a full stop. He refused a trailing ELLIPSIS on box 2
# on 2026-11-08; a full stop is what he asked for the next day, and the two are not the same mark.
# Box 2 therefore opens a sentence of its own, so "but" is "But". That is the consequence of the
# full stop he asked for, not a re-wording. Box 3 keeps its bare "... Cell", which he wrote.
LINE12 = ("I wish I could say that it's all over." + BOX               # 170 px, 2 lines
          + "But there is one more thing that has to be done." + BOX   # 243 px, 2 lines
          + "... Cell")                                                # 31 px, 1 line

# Section 3, ending word 22. Vanilla: "I don't think so." then "THE NIGHTMARE IS OVER CELL!!!!!".
# Only this EARLY copy is replaced. The Kamehameha pose of section 5 is another agent's work.
LINE22_INDEX, LINE22_REC = 22, 0x3B7FE0
LINE22_WAS = b"I don't think so.\x0bTHE NIGHTMARE IS OVER CELL!!!!!"
# HIS LOCKED TEXT, 2026-11-09. Box 1 is HIS OWN correction and now ends on the full stop he asked
# for. Box 2 takes the apostrophe vanilla spells every one of its 4 "won't" with, and already ends
# on his own bang, so it is untouched.
LINE22 = ("If you can get past me, then you can get to the past." + BOX   # 264 px, 3 lines
          + "But I won't let you!")                                       # 98 px, 1 line

# Section 2, the new caption. The STRING is vanilla's own, read out of rom:0x3B8610, and so is the
# mechanism: a plain type 1 record whose text opens "@^". The prefix loop @0x0800B224 eats "@" (box y
# 0x50) and @0x0800BA98 eats "^" (show the whole box at once), and the box is then dismissed by the
# same A press that ends every dialog box (bible B0893, B2095). A NEW RECORD is still needed, because
# the vanilla one at rom:0x3B860C carries the time-skip table's own next index, 9.
CAPTION_AT, CAPTION_REC = 0x3B8610, 0x3B860C
CAPTION = b"@^Three years later..."
CAPTION_PORTRAIT = 0                               # vanilla's own: a caption shows no face
# "Track 42 plays when the box appears". The cue runs AFTER the map load, and that order is load
# bearing. `ext 39` reads the new map's own +0x24 music word, where `ext 35` does not (bible B2176,
# both listings read), and map 6,100 carries the literal 38. The read skips `music_play` only when
# that exact song is already playing, so a `music(42)` in front of the load would be overwritten by
# 38 the moment the arena came up and the box would open on the wrong song. After the load the cue
# stands, and 42 then plays through the Cell talk until record F or record R starts 28.
CAPTION_MUSIC = 42
FIGHT_MUSIC = 28                                   # "Track 28 plays when the battle starts"

# THE CAPTION SHOWS ON BLACK, so the OBJ palette has to come back first.
# `fade_out` ends with Palette_LoadScaled @0x0800DA96 DMAing the scaled snapshot over all 512 palette
# halfwords, so every colour on screen is black (bible B0270, B0275, and the handler read 2026-11-08).
# No dialog function writes palette RAM: the OBJ palette writer census lists the title, `ext 45`, the
# party screen, the two menu scenes, the two fades and the zero fill, and no box code. So a box opened
# after a fade out would draw in black on black. `ext 45` @0x08009BE4 is one DMA3 of the shared OBJ
# palette rom:0x1DA6C8, and the ending's OWN tail runs it immediately before "@^The End.", which is
# the caption vanilla shows on a black screen. That is the shape copied here.
# `ext 45` lights EVERY sprite, so the screen has to be empty of actors before it runs. Vanilla's own
# "The End." needs no care here because its tail has already removed both fighters. Map 6,100 carries
# two at this point, the player the load builds at TRUNKS_START (248,624) and battle_arena's NPC Cell
# at CELL_START (288,392). Against the parked view, y 456 to 616 (bible B0246's envelopes):
#   Cell  reaches y 336..400, which is 56 px ABOVE the view top. He is already off screen.
#   Trunks reaches y 600..632, so his top 16 px poke into the bottom of the frame.
# So ONE actor has to move, and he moves with `ext 62`, not with a camera op. CAPTION_SPOT is 40 px
# further down the same column: his top is then 640, 24 px below the view bottom. Record A2 puts him
# back on TRUNKS_START before the fade in, so nothing else sees the move.
# A CAMERA OP WOULD BE WRONG HERE, and not only because it costs black frames. The battle-start
# checker reads a table in WALK order, so an `ext 31` at word 25 would read as the table's LAST fixed
# camera, after record F's `camera_follow(0)` at word 23, and the table would read as never handing
# the camera back. `ext 62` moves an actor and touches no camera, so the one park stays at word 13.
CAPTION_SPOT = (TRUNKS_START[0], TRUNKS_START[1] + 40)
OBJ_PALETTE_BACK = 45                              # ext 45: the ROM DMA that lights the sprites again
HUD_BIT = 86                                       # ext 86 header_bit1: the HUD comes off for the box

# ===== constants: the weaker FUTURE enemies (the owner, 2026-11-08) =====
# "The stats for future 17 and 18 should be weaker than vanilla, that is actually canon. Same for
# cell, this is cell before he absorbs people ... Weaker stats, like 25%". Read as 25 percent WEAKER
# than vanilla, not reduced to 25 percent of vanilla.
# The ending's enemies MAY NOT share a vanilla type, because every one of these three types also
# spawns in the main game: type 3 on maps 11,4, 11,5 and 11,6 (Piccolo's fights), type 4 on map 8,49
# and type 60 on map 10,20 (bible B2172, B1151, and the enemy type census). The owner drew that line
# himself on 2026-11-07: "We do not touch any earlier 18 and 17 fights."
# So each future enemy gets its OWN type entry, allocated in the expansion area ON the enemy table's
# 24-byte stride, which makes (entry - table) / 24 a type id the factory resolves. That is
# celljr_fight's own worked example (its trial Jr type), which has shipped in build_list.txt since
# r41, so the engine is known to take a type id of this size.
ENEMY_TABLE, ENEMY_ENTRY = 0x6D56AC, 24            # 109 live records; the base has 3 references image-wide
CELL_TYPE = 60                                     # vanilla Imperfect Cell, which the arena item names
TYPE60 = bytes.fromhex("00000000" "5a140000" "50000000" "20202580" "80000000" "c4f36f08")
ITEM_TYPE = 8                                      # an enemy item's type word (battle_arena's own offset)
WEAKER_PERCENT = 25                                # how much weaker than vanilla, the owner's "like 25%"
T_HP, T_STR, T_POW, T_END = 4, 0xC, 0xD, 0xE       # the four stats the scouter shows (bible B1793)
HP_STEP = 10                                       # vanilla HP for these three is a multiple of 10


def weaken(value: int, step: int = 1) -> int:
    """value less WEAKER_PERCENT, rounded half up onto a multiple of step."""
    return ((value * (100 - WEAKER_PERCENT) + 50 * step) // (100 * step)) * step


def weak_type(entry: bytes) -> bytes:
    """A vanilla enemy type entry with HP, STR, POW and END weakened, and every other byte kept.

    EXP is 0 on all three, so there is nothing to scale there. The AI id and the two damage factors
    stay: the owner asked for weaker stats, not for a different fighter. The death descriptor at
    +0x14 stays the BOSS one, because every death record here poses the body down and removes it
    itself and would break against the normal descriptor's own poof and remove."""
    if len(entry) != ENEMY_ENTRY:
        raise ValueError(f"an enemy type entry is {ENEMY_ENTRY} bytes, got {len(entry)}")
    out = bytearray(entry)
    struct.pack_into("<I", out, T_HP, weaken(struct.unpack_from("<I", entry, T_HP)[0], HP_STEP))
    for at in (T_STR, T_POW, T_END):
        out[at] = weaken(entry[at])
    return bytes(out)


def _alloc_on_stride(alloc, size: int, base: int, stride: int) -> int:
    """Free space for size bytes at an offset with (offset - base) a multiple of stride (a table slot id).

    celljr_fight's own helper, byte for byte: the enemy factory resolves a type with
    `table + 24 x id` and never bounds the id, so an entry on that grid IS a type."""
    at = alloc.alloc(size + stride - 4)
    at += (base - at) % stride
    if (at - base) % stride or at % 4:
        raise ValueError(f"rom:0x{at:X} is not on the 0x{base:X} + {stride} x n grid")
    return at

# Record 13's reveal. ext 35 carries its own fade: Map_LoadFromQueue @0x08009852 runs @0x0802664C with
# r1 = 0x40 and then the blocking frame loop @0x0801F2F4, loads the map, then allocates a 0xC object with
# +0x8 = 0x10 and runs that to completion as well. ext 39's handler sub_08009A88 has NEITHER call, so it
# leaves the screen exactly as the fade_out left it, black. The copy must fade in itself. 180 is the
# vanilla pairing: of the 28 records in the census that carry both ops, 26 run the SAME number in each,
# and of the 4 whose fade_out is 180 and which also fade in, 3 fade in at 180 (rom:0x3C4754,
# rom:0x3E4B6C, rom:0x3E5ED4). The fourth, rom:0x3BB6A2, fades in at 90.
#
# THE RECORD RUNS VANILLA'S OWN FASTEST MAP-LOAD TRANSITION, and it is measured, not picked. The
# owner, 2026-11-08: "why are we reinvintng the wheel, the game has loads of transitions, find out
# the length of time, etc, and thats what we use", then "what is the normal transition length in
# vanilla???", and after the next build, twice more, that it is still too long.
# `vanilla_transition_census.py` totals the blocking frames between each `fade_out` and its
# `fade_in` over every map-owned scene table. Across the 17 records that also LOAD A MAP, which is
# this record's own job, the black runs 60 to 600 frames, the median is 240 and only 3 of the 17
# spend any wait at all. THE FASTEST IS rom:0x3E424A, decoded op for op out of the base ROM:
#   fade_out(30) ; load_map_at(11,1,1,528,400) ; camera(440,160,20) ; ext78(0,3) ; fade_in(30)
# That is 60 frames of black, 1.0 second, and its shape is this record's shape: the cover, the load,
# the staging, the camera last, then the fade in. So this record takes its two numbers. A census
# of FADE LENGTHS alone (bible B1017) made 120 look like the house value; it counts how long the
# screen spends FADING and not how long the player waits, which is the number he asked about.
# THERE IS NO SETTLE WAIT, because vanilla spends none. Bible B2170 decodes a whole vanilla map-load
# transition op for op (rom:0x3E9E8C, the third Cell Junior's death event):
#   ext88 ; ext139 ; header_bit1(0) ; fade_out(120) ; leader(0) ; load_map_at(14,3,1,576,376) ;
#   music(37) ; remove(30) ; ext24(0) ; face(0,0) ; ext84(11) ; spawn(72,640,224) ; face(30,1) ;
#   party_add(0) ; camera(504,152,30) ; fade_in(120)
# The staging sits between the load and the camera, and the camera is the last op before the fade in.
# B0748 and B0877 say the same from two other records. This record now carries that shape: the load,
# then every staging op, then the camera park, and the fade in comes in record A2.
# THE OPENING WAIT IS VANILLA'S OWN 60. It is the beat before the fade and it is the one number this
# record never had a reason to move.
FAST_TRANSITION = 0x3E424A                         # the vanilla record both numbers are read from
REVEAL = 30                                        # the fade in, in record A2: its fade_in
HEAD_WAIT, HEAD_FADE = 60, 30                      # vanilla's own opening beat, then its fade_out


# ===== the new records =====

def blast(rom: bytes) -> bytes:
    """The vanilla third attack group with one edit: the player fires it, not the removed NPC set 133."""
    return _splice(rom, *BLAST, {ATTACKER_PUSH[0]: (ATTACKER_PUSH[1], _push(PLAYER, CELL, 100))})


def tail(rom: bytes, keep_base_remove: bool = False) -> bytes:
    """The vanilla tail with the player turned instead of set 133, and the set 132 and 133 ops dropped.

    `keep_base_remove` keeps ONE of the four, vanilla's own `push 132 ; ext 52`, which sits after the
    fade out and in front of `ext 45`. `ext 45` DMAs the shared OBJ palette back and lights EVERY
    sprite on a black screen, so an actor still standing there is drawn over "The End." That is why
    vanilla removes its fighters in that exact place. This record's own death table has no NPC set
    132 to remove, so it drops the op; `finale_blast` ends on one and keeps it."""
    edits = {FACE_PUSH[0]: (FACE_PUSH[1], _push(PLAYER, DOWN))}
    drops = DROPS[:-1] if keep_base_remove else DROPS
    edits.update({at: (old, b"") for at, old in drops})
    return _splice(rom, *TAIL, edits)


def map_reload(zone: int, area: int) -> tuple:
    """The five ext 39 arguments: the arena map, with the player placed where the NPC Trunks started.

    The x and y of `ext 39` are the PLAYER's position, not a view origin. `sub_08009A88` pops y, x,
    var, area and zone, writes x and y into one {s16 x, s16 y} pair, and hands that pair to
    `sub_0800C584`. There the camera is built from (x - 0x70, y - 0x4C), and the SAME pair is passed
    as r2 to the player constructor `sub_080086D4` at `loc_0800C608`. So the pair places the player
    and the camera is centred on him. CONFIRMED, both handlers read.

    The pair is TRUNKS_START, map 6,1 item 5's own spot, which is where vanilla's NPC Super Saiyan
    Trunks stands when the map load builds him. The record then walks the player the NPC's own walk.
    Loading him on TRUNKS_SPOT instead would open the scene with him already at the end of that walk."""
    return (zone, area, MAP_VARIATION) + TRUNKS_START


def arrive(rom: bytes, zone: int, area: int) -> bytes:
    """Record 13 of the ending, the arrival at Capsule Corp: the ARENA loads here, not at the fight.

    The owner played v6 and rejected its fight start: "Why is it fading!??? Look at how EVERY OTHER
    FIGHT WORKS! There should not be a fade at all after the diague! Dialogue ends fight begins with a
    camera pan to the user and the hud appearing, like every single fight int he game."

    He is right, and the fix is not to drop the cover but to MOVE THE LOAD. A map load replaces the
    camera in one frame (`map_load @0x0800C584`), so it needs a cover, and vanilla record 13 already
    opens this scene behind its own `fade_out(180)`. So the arena loads under THAT fade, and record F
    is left with nothing to cover. Vanilla's own shape, op for op:

        wait(60) ; fade_out(180) ; load_map(6,1,1,136,432) ; wait(120) ; walk(133,248,568) ; wait(100)

    This record now ENDS on the caption, so the arrival is two records. A loads the arena and sets
    the screen up for the box; record A2, ending word 25, finishes the arrival. Steps 5 to 7 below
    live in A2.

    and the copy, with each change load bearing:

      1. `wait(60) ; fade_out(30)`. The wait is vanilla's own beat and is the one number this record
         never had a reason to move. The fade is the fade_out of rom:0x3E424A, vanilla's own fastest
         map-load transition, and record A2 runs its fade_in. See REVEAL for the census.
         The module still READS the vanilla pair `wait(60) ; fade_out(180)` and refuses if it has
         moved, so the 17/18 boundary cannot drift, and the vanilla record keeps every byte.
      2. The form and the leader go in FRONT of the load, and the form is BASE Trunks, set 132.
         The owner's flow: "Cell: Trunks starts NOT Super Saiyan". He fought the two androids in 133,
         and this ext 73 is what puts him back in his base body for the Cell fight. `ext 70` writes the party roster, but the
         block that installs the leader's BODY is guarded (`sub_0800A680`: CMP r4,#0 then BEQ on
         `Sprite_CurrentDirectory` 0x03001FA8, which is zero all through the ending), so the map load
         is what builds the player from the roster. `ext 73` goes first because `appearance_revert`
         @0x08003ED4 skips the record whose index equals the leader byte `set_leader` has just
         written, so a form set on the character who BECOMES leader survives his own leader change.
      2a. THE THREE YEARS REFILL HIM. The owner: "trunks ssj ki is drained after the 3 year split, it
         should be refrsehed for the cell fight". `ext 109 (char, n)` sets HP and `ext 110 (char, n)`
         sets EP to min(n, max), and scripts use 5000 as a refill (bible B0576). `chamber_spar` runs
         the same pair. Both are run for character 3, Trunks, so the fight after the skip starts on a
         full bar and a full ki row. The Super Saiyan ki the owner means IS the EP row: `bf_ki_pool`
         draws it in yellow over the EP row.
      3. `ext 39`, never `ext 35`. Only `ext 38` and `ext 39` reach `sub_0800C584` and through it the
         player constructor `sub_080086D4`; `ext 35` reaches `Map_Load @0x0800C664` only and builds no
         player at all. Bible row 1579 once said `ext 35` reached it, and that error cost a build.
      4. THERE IS NO SETTLE WAIT. Bible B2170 decodes a whole vanilla map-load transition op for op
         and the load is followed straight away by its staging ops, with the camera last and the fade
         in after it. B0748 and B0877 say the same from two more records. So the staging occupies the
         space the settle used to hold, which is what the engine itself does.
      5. `header_bit1(0) ; ext 62 ; music(42) ; camera(136,456,40) ; ext 45`, in that order and for
         that reason. THE PLAYER MOVES BEFORE THE CAMERA PARKS, so nothing can drag the park. `ext 31`
         takes the view TOP LEFT, not its centre (bible row 1000), and it BLOCKS: `sub_0800977A`
         publishes the move with `Scene_Publish` @0x0800DF1C and then runs `Handler_RunScoped`
         @0x0801F2F4, which loops frames until the move reports done. So the travel from the load's
         own (136,548) finishes under the black. `ext 45` is last because it is the DMA that lights
         the sprites and the caption's own letters. See CAPTION_SPOT and CAPTION_MUSIC.
      6. The fade in and the walk are record A2's, because a type 1 caption record cannot carry ops.
         See reveal(). His words on 2026-11-05: "have it follow the same path as the NPC, no hand
         off needed".

    THE PLAYER ARRIVES OFF SCREEN, and that is the whole of the owner's finding 3: "when we
    transtion to trunks going to cpasule corp, you see his sprite in the very bottom, not sure if in
    vanilla hes there or if he is supposed to aarrive off screen". He is supposed to arrive off
    screen. The record used to put him back on TRUNKS_START (248,624) before the reveal, and against
    the parked view, whose bottom edge is y 616, his sprite spans y 600 to 632: the top 16 px of him
    sit inside the frame. That is what he saw. He now stays on CAPTION_SPOT (248,664), where the same
    sprite spans 640 to 672 and is wholly below the frame, and record A2 walks him up into it, which
    is the vanilla NPC's own entrance. The fix holds at ANY fade length, so it does not depend on the
    transition cut."""
    head = bytes(rom[REC13_HEAD[0]:REC13_HEAD[0] + REC13_HEAD[1]])
    if head != wait(60) + fade_out(180):
        raise ValueError(f"record 13 does not open with wait(60) ; fade_out(180): {head.hex()}")
    return code(CAPTION_INDEX,
                wait(HEAD_WAIT), fade_out(HEAD_FADE),
                ext(73, TRUNKS, BASE_TRUNKS), leader(TRUNKS),
                ext(HP_REFILL, TRUNKS, REFILL), ext(KI_REFILL, TRUNKS, REFILL),
                call("load_map_at", *map_reload(zone, area)),
                ext(HUD_BIT, 0), ext(62, PLAYER, *CAPTION_SPOT),
                call("music", CAPTION_MUSIC),
                camera(*VIEW),
                ext(OBJ_PALETTE_BACK))


def caption(rom: bytes) -> bytes:
    """C, ending word 24: the owner's new caption box, "Three years later...".

    His words, design section 2: "A box that says: Three years later... The user presses a button to
    dismiss it. Track 42 plays when the box appears. Then it fades to Trunks arriving at Capsule Corp".

    THE STRING IS VANILLA'S OWN, read out of rom:0x3B8610, so it cannot drift from the one LoG II
    already shows at its own time skip. So is the mechanism: a type 1 record whose text opens "@^".
    The prefix loop @0x0800B224 eats "@" and sets the box y to 0x50, @0x0800BA98 eats "^" and sets the
    show-at-once flag, and the box then waits for the A press that ends every dialog box (B0893,
    B2095). Nothing here is new, and nothing in the engine had to be touched.

    A NEW RECORD was still needed. The vanilla record is rom:0x3B860C, and its +0 word is the next
    index 9, which is an index into the TIME SKIP table rom:0x3B88A0. Pointing an ending word at it
    would hand the ending's own scene on to word 9 of the ending table, which is Cell's "It can't
    be!". So the four byte header is rebuilt and only the text is reused.

    Record A has already run music(42), parked the view on an empty corner and run `ext 45`, so the
    box opens over pure black with its own letters lit. See EMPTY_VIEW."""
    text_bytes = bytes(rom[CAPTION_AT:CAPTION_AT + len(CAPTION)])
    if text_bytes != CAPTION:
        raise ValueError(f"rom:0x{CAPTION_AT:X} is {text_bytes!r}, not the vanilla caption {CAPTION!r}")
    return bytes([REVEAL_INDEX, 0, TYPE_TEXT, CAPTION_PORTRAIT]) + text_bytes + b"\0"


def reveal() -> bytes:
    """A2, ending word 25: the rest of record A, which could not run until the caption was dismissed.

    The caption is a TEXT record, so the arrival had to be cut in two: a type 1 record carries no ops
    and a type 0 record carries no text. This half puts the player back on the spot the map load gave
    him, gives the HUD back, fades in and walks him the NPC's own walk, and then hands on to word 14,
    the Cell talk, exactly where the one-piece record used to.

    IT SETS NO CAMERA. Record A parked the view on the pair before the caption and nothing has moved
    it, so there is nothing to undo. See CAPTION_SPOT for why a camera op here would be wrong.

    IT MOVES NOBODY EITHER. The player is still on CAPTION_SPOT, 24 px below the frame, and he walks
    up into it. Putting him back on TRUNKS_START first is what showed his head at the bottom of the
    screen; see arrive(). The walk is 96 px at `ext 53`'s own 1 px a frame instead of vanilla's 56,
    and every one of those frames is him walking on screen, not a wait.

    IT GIVES NO HUD BACK, and that is the owner's finding 4: "also the hud for trunks is visible,
    when it shouldnt be, it should appear whent he dialgue ends I think." This record runs one record
    BEFORE the talk starts at word 14, so a `header_bit1(1)` here put the HUD up for the whole
    conversation. The HUD comes back where every other fight in the game brings it back, in the
    battle start at word 23 (`fight_start`, and `plateau.round2` on the plateau path), which is the
    op the dialogue ends on."""
    return code(ARRIVE_INDEX + 1,
                fade_in(REVEAL),
                walk_to(PLAYER, *TRUNKS_SPOT), wait(REC13_ARRIVED))


def replaced_line(index: int, portrait: int, line: str) -> bytes:
    """One of the two ending lines the owner rewrote, as a type 1 record that hands on where it did.

    Sections 1 and 3 of the design. His text is copied character for character, and the only byte
    added is 0x0B, which ends a box and opens the next one on an A press (B0650). Vanilla word 22
    already carries two boxes in one record, so this is the table's own shape."""
    return text(index + 1, portrait, line)


def fight_start(enemy_item: int) -> bytes:
    """F, ending word 23: four ops, the shape every other fight in the game uses.

        ext104(28, 1) ; bar_show(28) ; header_bit1(1) ; camera_follow(0)

    The model is Piccolo against Android 17, `rom:0x3E47DC`, map 11,4 word 6, which the owner named
    himself: `ext104(9,1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0)`. No fade, no map
    load, no wait, and nobody placed. Record 13 settled the form, the leader, the spots and the camera,
    and nothing has moved since, so there is nothing left for this record to do but start the fight.

    `ext 104` removes the live NPC Cell the map load built and spawns the arena's enemy item in his
    place, at his position and his facing. CONFIRMED: `Sprite_ReplaceWithEntry` @0x0800AAC6 selects the
    actor of the pushed set, copies its point and its facing, destroys it, and calls
    `Object_SpawnFromEntry` @0x0800C75C, which bounds the index against the map entry's item COUNT,
    reads the item, calls the item's OWN +0 factory through `Thunk_BranchR1` @0x08021D2A, and then
    writes only the position and the facing over the result. The enemy factory @0x0800E77E reaches
    @0x0800E280, which runs `LDR r2,[r6,#0x14] ; STR r2,[r5,#0x4]`: the item's own event struct. So the
    death table this module writes onto that item is what runs when Cell dies, and no condition is
    tested anywhere on this path.

    The bar is `ext 85 bar_show`, not `ext 90 bar_set`. `ext 90`'s two extra values are a DISPLAY
    SEGMENT for one round of a multi-round boss: Android 17 shows (9,75,100) for round 1 and (9,25,50)
    for round 2. The arena fight is one round against the whole of Imperfect Cell's vanilla HP, so a
    segment would claim a split that does not exist.

    `camera_follow(0)` is the pan the owner asked for. Record 13's `ext 31` has held the view fixed
    through the whole talk, so this op is what glides it onto the player, exactly as Piccolo's does.

    `music(28)` opens it. The owner, design section 3: "Track 28 plays when the battle starts". It
    runs in FRONT of the four ops, so the song is already changing as the bar rises. A music op breaks
    none of the six battle-start rules: they read the map loads, the fades, the camera, the HUD and
    the sets a record names, and `ext 49` is none of those.

    Next 26 = END gives control."""
    return code(END_INDEX, call("music", FIGHT_MUSIC),
                battle_start(enemy_set=CELL, enemy_item=enemy_item, bar=CELL))


def death(rom: bytes) -> bytes:
    """K, table D word 0: bar and HUD off, Cell collapses, a fade covers the restore of the vanilla spots and
    the swap of the beaten enemy for an NPC Cell, then the vanilla blast and tail run. Next 24 = "The End."."""
    return (bytes([TEXT_INDEX, 0, 0])
            + ext(88) + HUD_OFF
            + ext(57, CELL, DOWN_STATE) + ext(69, COLLAPSE_HOLD)
            + ext(40, FADE)
            + ext(62, PLAYER, *TRUNKS_SPOT) + ext(55, PLAYER, UP)
            + ext(52, CELL) + ext(51, CELL, *CELL_SPOT) + ext(55, CELL, DOWN) + ext(57, CELL, DOWN_STATE)
            + ext(31, *DEATH_VIEW)
            + ext(41, FADE)
            + blast(rom) + tail(rom)
            + b"\x11")


def death_table(death_at: int) -> bytes:
    """D, the enemy's event table: word 0 is the death record, words 24 and 25 are the vanilla ending
    records, every other word ends the scene. Records 24 and 25 carry their own next indices (B4)."""
    words = [0] * TABLE_WORDS
    words[0] = death_at + ROM_BASE
    words[TEXT_INDEX], words[EXIT_INDEX] = REC24 + ROM_BASE, REC25 + ROM_BASE
    return b"".join(_word(w) for w in words)


# ===== helpers =====

def _word(v: int) -> bytes:
    return struct.pack("<I", v)


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _push(*vals: int) -> bytes:
    """scene_lib's push, held to the push_list form every edited site uses: a one value push would be op 0,
    which is a shorter op than the bytes it replaces."""
    out = push(*vals)
    if out[0] != 29:
        raise ValueError(f"push{vals} is op {out[0]}, not the push_list form")
    return out


def _splice(rom: bytes, at: int, length: int, edits: dict) -> bytes:
    """rom[at:at + length] with each edit applied. An edit is {offset: (old hex, new bytes)}, and the old
    bytes must match, so a wrong offset raises instead of writing a corrupt record."""
    out, cut = bytearray(), at
    for off in sorted(edits):
        old, new = bytes.fromhex(edits[off][0]), edits[off][1]
        if not (at <= off and off + len(old) <= at + length):
            raise ValueError(f"rom:0x{off:X} is outside the slice rom:0x{at:X}+0x{length:X}")
        _expect(rom, off, old)
        out += rom[cut:off] + new
        cut = off + len(old)
    return bytes(out + rom[cut:at + length])


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

def _check_lines(rom: bytes) -> None:
    """The two records the owner's new lines replace still hold the vanilla text he quoted.

    He wrote his replacements against what the game says today, so if either record ever stopped
    holding that text the replacement would be answering a line nobody speaks."""
    for index, rec, was in ((LINE12_INDEX, LINE12_REC, LINE12_WAS), (LINE22_INDEX, LINE22_REC, LINE22_WAS)):
        _expect(rom, TABLE + 4 * index, _word(rec + ROM_BASE))
        _expect(rom, rec + 2, bytes([TYPE_TEXT, SSJ_PORTRAIT]))
        if struct.unpack_from("<H", rom, rec)[0] != index + 1:
            raise ValueError(f"ending record {index} rom:0x{rec:X} does not hand on to word {index + 1}")
        stop = bytes(rom).index(b"\0", rec + 4)
        if bytes(rom[rec + 4:stop]) != was:
            raise ValueError(f"ending record {index} rom:0x{rec:X} says"
                             f" {bytes(rom[rec + 4:stop])!r}, and the owner's line replaces {was!r}")
        if words_naming(rom, rec) != [TABLE + 4 * index]:
            raise ValueError(f"0x{rec + ROM_BASE:08X} is named by {words_naming(rom, rec)},"
                             f" expected one word at rom:0x{TABLE + 4 * index:X}")


def _check_spare_indices(rom: bytes) -> None:
    """Ending words 24 and 25 really are free for the caption chain, PROVED out of the live table.

    Vanilla chains 0 to 26 in order, so index 24 is reached only from record 23 and index 25 only from
    record 24. Record 23 is the scripted kill this module replaces with record F, whose next is 26, so
    after that write no record of the ending table reaches either index. This walks the live table and
    refuses if any OTHER record hands on to one of them."""
    strays = {}
    for k in range(TABLE_WORDS):
        word = _u32(rom, TABLE + 4 * k)
        if word < 0x10000:
            continue
        at = word - ROM_BASE
        nxt = struct.unpack_from("<H", rom, at)[0]
        if nxt in (CAPTION_INDEX, REVEAL_INDEX):
            strays[k] = (at, nxt)
    want = {FIGHT_INDEX: (REC23, CAPTION_INDEX), TEXT_INDEX: (REC24, REVEAL_INDEX)}
    if strays != want:
        raise ValueError(f"ending words {CAPTION_INDEX} and {REVEAL_INDEX} are reached from {strays},"
                         f" expected only {want}: the caption chain cannot take them")


def _check(rom: bytearray, alloc) -> None:
    if ARENA not in alloc.notes:
        raise ValueError(f"ending_fight needs the {ARENA} notes: list {ARENA} before it")
    if "ending_fight" in alloc.notes:
        raise ValueError("ending_fight already ran")
    arena = alloc.notes[ARENA]
    _expect(rom, arena["event"], _word(EVENT_RUNNER))
    if _u32(rom, arena["event"] + EVENT_TABLE_AT) == 0:
        raise ValueError(f"the arena enemy's event struct rom:0x{arena['event']:X} names no table")
    if _u32(rom, arena["item"] + 0x14) != arena["event"] + ROM_BASE:
        raise ValueError(f"the arena enemy rom:0x{arena['item']:X} does not name event struct"
                         f" rom:0x{arena['event']:X}")
    for name, mine, theirs in (("CELL_SPOT", CELL_SPOT, arena.get("cell_spot")),
                               ("TRUNKS_SPOT", TRUNKS_SPOT, arena.get("trunks_spot")),
                               ("TRUNKS_START", TRUNKS_START, arena.get("trunks_start"))):
        if tuple(theirs or ()) != mine:
            raise ValueError(f"{name} is {mine} here and {theirs} in the {ARENA} notes: the two"
                             f" modules must agree, or an actor stands away from the fight")
    if arena.get("cell_set") != CELL:
        raise ValueError(f"the arena NPC is set {arena.get('cell_set')} and record F names set {CELL}:"
                         f" ext 104 would find no actor to replace")
    if arena.get("item_index") in (None, arena.get("npc_item_index")):
        raise ValueError(f"the {ARENA} notes do not separate the NPC item from the enemy item:"
                         f" ext 104 must name the ENEMY item index")
    # The Cell talk's portraits, and the enemy type the arena item names.
    _expect(rom, APPEARANCE + APPEARANCE_ENTRY * BASE_ENTRY + APPEARANCE_DIALOG, bytes([BASE_PORTRAIT]))
    _expect(rom, APPEARANCE + APPEARANCE_ENTRY * SSJ_ENTRY + APPEARANCE_DIALOG, bytes([SSJ_PORTRAIT]))
    for index, rec, kind in TALK_PORTRAITS:
        _expect(rom, TABLE + 4 * index, _word(rec + ROM_BASE))
        _expect(rom, rec + 2, bytes([kind, SSJ_PORTRAIT]))
        if struct.unpack_from("<H", rom, rec)[0] != index + 1:
            raise ValueError(f"ending record {index} rom:0x{rec:X} does not hand on to word {index + 1}:"
                             f" the talk is not the record list this module thinks it is")
    _expect(rom, ENEMY_TABLE + ENEMY_ENTRY * CELL_TYPE, TYPE60)
    if _u32(rom, arena["item"] + ITEM_TYPE) != CELL_TYPE:
        raise ValueError(f"the arena enemy rom:0x{arena['item']:X} is type"
                         f" {_u32(rom, arena['item'] + ITEM_TYPE)}, not the vanilla Cell type {CELL_TYPE}")
    _expect(rom, FIGHT_WORD, _word(REC23 + ROM_BASE))
    _expect(rom, TABLE + 4 * TEXT_INDEX, _word(REC24 + ROM_BASE))
    _expect(rom, TABLE + 4 * EXIT_INDEX, _word(REC25 + ROM_BASE))
    _expect(rom, TABLE + 4 * END_INDEX, _word(0))
    for at, want in SOURCE_BYTES:
        _expect(rom, at, want)
    if hashlib.sha1(bytes(rom[REC23:REC23 + REC23_LEN])).hexdigest() != REC23_SHA1:
        raise ValueError(f"record rom:0x{REC23:X} (the scripted kill) differs from the base bytes")
    if words_naming(rom, REC23) != [FIGHT_WORD]:
        raise ValueError(f"0x{REC23 + ROM_BASE:08X} is named by {words_naming(rom, REC23)},"
                         f" expected one word at rom:0x{FIGHT_WORD:X}")
    # Record 13 is repointed, so its own bytes must still be the vanilla bytes and exactly one word
    # may name it. Its record stays where it is: only the table word moves.
    rec13_len = record_end(rom, REC13) - REC13
    _expect(rom, ARRIVE_WORD, _word(REC13 + ROM_BASE))
    if hashlib.sha1(bytes(rom[REC13:REC13 + rec13_len])).hexdigest() != REC13_SHA1:
        raise ValueError(f"record rom:0x{REC13:X} (the Capsule Corp arrival, ending word"
                         f" {ARRIVE_INDEX}) differs from the base bytes")
    if words_naming(rom, REC13) != [ARRIVE_WORD]:
        raise ValueError(f"0x{REC13 + ROM_BASE:08X} is named by {words_naming(rom, REC13)},"
                         f" expected one word at rom:0x{ARRIVE_WORD:X}")
    if REC13_LOAD_AT <= REC13_HEAD[0] + REC13_HEAD[1]:
        raise ValueError("REC13_HEAD reaches into the load: the 17/18 boundary constant is wrong")
    _check_lines(rom)
    _check_spare_indices(rom)
    guarded = [(FIGHT_WORD, 4, "ending table word 23"), (REC23, REC23_LEN, "ending record 23"),
               (REC24, REC25 - REC24, "the vanilla end text"),
               (REC13, rec13_len, f"ending record {ARRIVE_INDEX} (the Capsule Corp arrival)")] \
        + [(rec + PORTRAIT_AT, 1, f"ending record {index}'s portrait byte")
           for index, rec, _kind in TALK_PORTRAITS] \
        + [(TABLE + 4 * k, 4, f"ending table word {k}")
           for k in (LINE12_INDEX, LINE22_INDEX, CAPTION_INDEX, REVEAL_INDEX)] \
        + [(ENEMY_TABLE + ENEMY_ENTRY * CELL_TYPE, ENEMY_ENTRY, f"enemy type {CELL_TYPE} (Imperfect Cell)")]
    for name, (index, rec, sha) in VANILLA_CONVERSATION.items():
        word, length = TABLE + 4 * index, record_end(rom, rec) - rec
        _expect(rom, word, _word(rec + ROM_BASE))
        if hashlib.sha1(bytes(rom[rec:rec + length])).hexdigest() != sha:
            raise ValueError(f"record rom:0x{rec:X} ({name}, ending word {index}) differs from the"
                             f" base bytes")
        if words_naming(rom, rec) != [word]:
            raise ValueError(f"0x{rec + ROM_BASE:08X} ({name}) is named by {words_naming(rom, rec)},"
                             f" expected one word at rom:0x{word:X}")
        guarded += [(word, 4, f"ending table word {index}"), (rec, length, f"ending record {index}")]
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

    arena = alloc.notes[ARENA]
    come = place(arrive(rom, arena["zone"], arena["area"]),
                 f"record A (the arena loads under the vanilla fade, ending word {ARRIVE_INDEX})")
    card = place(caption(rom), f"record C (the caption \"Three years later...\", ending word"
                               f" {CAPTION_INDEX})")
    back = place(reveal(), f"record A2 (the view, the fade in and the walk, ending word {REVEAL_INDEX})")
    line12 = place(replaced_line(LINE12_INDEX, SSJ_PORTRAIT, LINE12),
                   f"the owner's line for ending word {LINE12_INDEX} (3 boxes)")
    line22 = place(replaced_line(LINE22_INDEX, BASE_PORTRAIT, LINE22),
                   f"the owner's line for ending word {LINE22_INDEX} (2 boxes)")
    fight = place(fight_start(arena["item_index"]), "record F (the fight starts, ending word 23)")
    dead = place(death(rom), "record K (Cell collapses, the vanilla blast, the vanilla tail)")
    table = place(death_table(dead), f"table D (the enemy's event table, {TABLE_WORDS} words)")

    put(ARRIVE_WORD, _word(come + ROM_BASE), f"ending table word {ARRIVE_INDEX} (record A)")
    put(TABLE + 4 * CAPTION_INDEX, _word(card + ROM_BASE),
        f"ending table word {CAPTION_INDEX} (record C, the caption)")
    put(TABLE + 4 * REVEAL_INDEX, _word(back + ROM_BASE),
        f"ending table word {REVEAL_INDEX} (record A2, the rest of the arrival)")
    put(TABLE + 4 * LINE12_INDEX, _word(line12 + ROM_BASE),
        f"ending table word {LINE12_INDEX} (the owner's own line)")
    put(TABLE + 4 * LINE22_INDEX, _word(line22 + ROM_BASE),
        f"ending table word {LINE22_INDEX} (the owner's own line)")
    put(FIGHT_WORD, _word(fight + ROM_BASE), "ending table word 23 (record F)")
    put(arena["event"] + EVENT_TABLE_AT, _word(table + ROM_BASE),
        "the arena enemy's event table (table D, so his death runs the rest of the ending)")

    for index, rec, _kind in TALK_PORTRAITS:
        put(rec + PORTRAIT_AT, bytes([BASE_PORTRAIT]),
            f"ending record {index}'s portrait (base Trunks, not Super Saiyan)")

    cell_type_at = _alloc_on_stride(alloc, ENEMY_ENTRY, ENEMY_TABLE, ENEMY_ENTRY)
    put(cell_type_at, weak_type(bytes(rom[ENEMY_TABLE + ENEMY_ENTRY * CELL_TYPE:][:ENEMY_ENTRY])),
        f"the FUTURE Imperfect Cell type ({WEAKER_PERCENT} percent weaker than type {CELL_TYPE})")
    cell_type = (cell_type_at - ENEMY_TABLE) // ENEMY_ENTRY
    put(arena["item"] + ITEM_TYPE, _word(cell_type),
        "the arena enemy's type word (the weaker future Cell)")

    alloc.notes["ending_fight"] = {"arrive": come, "fight": fight, "death": dead, "table": table,
                                   "caption": card, "reveal": back,
                                   "line12": line12, "line22": line22,
                                   "caption_index": CAPTION_INDEX, "reveal_index": REVEAL_INDEX,
                                   "event": arena["event"], "item": arena["item"],
                                   "item_index": arena["item_index"],
                                   "cell_type": cell_type, "cell_type_entry": cell_type_at,
                                   "sites": sorted(sites)}
