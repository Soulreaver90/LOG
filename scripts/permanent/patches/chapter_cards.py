r"""
chapter_cards.py - Trial patch: a chapter title card ("Chapter N" and a title) at each chapter's story point, on a
                   new game and when a save is continued, in the style of Buu's Fury's chapter cards (me
                   2026-10-25 10:42 AM: "YES! I love chapter titles"; v5 me, 2026-10-29: 8 chapters, own titles).

Usage:   py -3 -P scripts\permanent\log2_build.py --list scripts\permanent\build_list_trial_chapters.txt
                --out <new .gba>
Input:   any ROM whose file select vtable word, Continue body, image scene vtable, ext op table pool words and
         STORY records are vanilla (the padded base or r39), and (v8) whose landing item rom:0x3FBC5C, its region
         word rom:0x3FBE54, the landing script rom:0x3FBC50 and the scene item, activate and ext 23 bodies are
         vanilla. Run it after relay_cooldown (it copies the live ext table). No earlier patch notes are needed.
API:     apply(rom, alloc) -> None; addresses in alloc.notes["chapter_cards"], every write as (offset, length, name)
         in its "sites". bf_rom() -> the checked BF ROM bytes; render_card(bf, number, title) -> 240x160 palette
         indices; card_lines(bf, number, title) -> the text lines; text_width(bf, text) -> px; backdrop(bf) ->
         (pixels, BG palette bytes); chapter_for(flag_bytes) -> CHAPTERS row (the same rule as the Thumb code);
         story_ops(card) -> the script bytes a story point gets; record_ops(rom, rec) -> (op starts, length);
         level_rule(n) -> (mul, shift) of the fade level (v7); landing_records() -> {index: record bytes} and
         landing_blob(at) -> (item, table, records) bytes of the card 4 landing scene (v8).
Method:  1. Continue (file select vtable 0x08023B0C +0x2C, vanilla 0x0800180D) is a base-relative vtable word; it
            names a wrapper in free space. For slot 0-2 with the slot image +1 bit 0 set (0x080019F6), the wrapper
            reads the slot image's story flags (file select object +0x14 + 0x164 x slot + 0xB4), picks the last
            CHAPTERS row whose start flag is set (v8: a VISITED row also needs its map visited bit, image +0xE7),
            allocates a 20-byte scene (0x0801F08C) and runs it with
            scene_push 0x0801F2F4 (a nested frame loop). Then it calls the vanilla Continue, which copies the slot,
            sets the field scene and loads the map. So the card shows between file select and map load, as in
            Buu's Fury (fade out, card, map load). v5: for an empty slot the wrapper shows card 1, because the
            vanilla Continue starts a new game there (0x08001842 beq 0x080018CE: save init, map 0x08409410).
         1b. STORY POINTS (v5, design B of the trial report, the BF ext 183 model): a new ext op CARD_OP pops a
            chapter number and runs the same card scene, then the script goes on. The ext table 0x083B5D28 is full
            (145 code words, then data), so a 146-word copy of the live table (word 145 = the card op) is named by
            both pool words that name the table (rom:0x921C op 2, rom:0x92DC ops 21-26). The vanilla table is
            listed in "sites" though no byte changes, so a later module that writes a word there (relay_cooldown)
            refuses. Each STORY record is copied with `push N ; ext CARD_OP` inserted after the scene's fade out
            (npc_gi.relocate re-encodes the jumps; the +0 next index is kept) and its one live table word names
            the copy; the old record stays unchanged and unreferenced. Card 7's word is in the chamber exit table
            that the two type 5 words name (piccolo_gi_scene's copy in r39). Every story card is followed by a map
            load, which reloads the map graphics and (map_load_core 0x0800C4E0-0x0800C50E) the map's music.
         1c. CARD 4 LANDING SCENE (v8, card-4-scene-report.md, me, 2026-10-30 8:00 PM): card 4 plays on the first
            landing on the Northern Mountains (map 8,1), then the team flies in, talks and flies north. The world
            map landing item rom:0x3FBC5C (script item 0x0800C2C3) is copied as a scene item (factory 0x0800D7E1,
            the same A-press trigger, rect and region condition) whose data names LANDING table; region word
            rom:0x3FBE54 (its only name) names the copy. The scene item activate (0x0800D7A0) runs the table in a
            nested frame loop from index 0, so the table goes on across the map load (vanilla: 14 scene item
            records load a map with ext 38 or 39 mid-table, c4b_probe.txt section 3). Record 0 tests the 8,1
            visited bit (push 8,1 ; ext 23); set = the vanilla landing (ext 38) and END; clear = fade 60, card 4,
            map load without fade (ext 39, which sets the bit), then the scene under black and a fade in. The
            vanilla post-Android 20 record (the v5-v7 card 4 point) is live again. v12: that ext 39 puts the
            player on LAND, the same spot every later landing uses, so both arms of record 0 carry one spot.
         2. The card scene copies the vanilla image scene (vtable 0x080237C0, the copyright screen 0x0801EDFA):
            BG3 8bpp, char base 0, screenblock 0x0600F800, BG3CNT 0x1F83, DISPCNT 0x0800 (OBJ off), BLDCNT 0.
            Slots +4 enter, +8 leave and +0x14 tick are new; the other slots are the image scene's. Enter makes
            the BG palette black, copies the BACKDROP base tiles, then the card's screenblock and its own tiles
            after the base tiles, and starts the ported BF song with music_play 0x08020A4C unless it already
            plays (the title_enter check). Tick (v2, BF timing, no skip): FADE_IN frames in, WAIT frames, FADE_OUT
            frames out, then 1 (scene end). FADE (v7, card-fade-report.md option B, variant B8): on each fade
            frame the tick writes the 256 BG palette words as BF does. In: L = (frame << 8) / FADE_IN, channel =
            BF's RGB888 fade table (rom:0x701B0, 247/248 from its OBJ 1/2 rows) x L >> 11 (BF ext 121,
            0x08007074). Out: L = 256 - ((frame - HOLD_END) << 8) / FADE_OUT, channel = the BACKDROP palette's
            5-bit channel x L >> 8 (BF ext 120, 0x080176D6). The divide is an exact multiply (level_rule, checked
            for every frame); L 256 copies the BACKDROP bytes; the hold writes nothing. v2-v6 faded with BLDALPHA
            EVA (17 levels, a 6-frame staircase). Enter keeps DISPCNT, BG3CNT, BLDCNT
            and BLDALPHA in the object; leave stops the music (as BF ext 36), makes the BG palette black, puts the
            four back and frees the object, so vanilla Continue starts from the registers file select left.
         3. SONG PORT (v2): BF song 37 (the BF card music) is copied from the BF ROM (SHA-1 checked) with its
            pattern pointers, order bytes, mask table, the directory entries it uses and their sample bytes; every
            pointer is rebased, unused directory entries name 16 silent bytes. The song is checked before any
            write: notes < 120 or 0xFF, effects < 32, instruments inside the directory.
         4. CARD LOOK (v3, BF's, me, 2026-10-25 6:46 PM): each card is pre-rendered here from the BF ROM.
            Backdrop: BF map entry 29 (card script 0x0879B004 map load), screenblock codec frame rom:0x29B988,
            raw cell 0 = bank 0 tile 0, 1-3 = RAW_TILES, 4-599 = global 8bpp tile RAW_BASE + raw (256 per bank,
            bank table rom:0x179764), no flips; BG palette rom:0x5632C (BF copies it to 0x05000000, literal
            0x0802CAAC). Text: BF ext 178 draws a string at run time with the font at 0x087548DC (glyph table
            0x08753A20: u16 index per char, then u16 width and one u16 column per pixel, bit 0 at the top);
            fill where a column bit is set, outline where a 4-neighbour bit is set, column c at pen + c, advance
            width + 1, centred on x 120 with pen = 120 - (width + 1) // 2, bit b at y centre - 6 + b; lines at
            y 65 and 85 (0x0802BECC, 0x0803F70C). Colours: OBJ palette rom:0x5652C bank 0 (1 = 0x0000 outline,
            2 = 0xFFFF white fill, bit 15 unused), copied to two BG palette entries the backdrop does not use.
            BF's '.' and "'" glyphs are blank, so EXTRA_GLYPHS draws those two. A line wider than BF's screen
            allows is wrapped at the space that gives the narrower widest line; the block stays centred on
            y 75 with BF's 20 px pitch. Stored: one BACKDROP {BG palette, base tiles}; per card u32 tile
            bytes, the 32x32 screenblock (0x800 bytes), then the card's own 8bpp tiles (ids after the base tiles).
            v7: the 0x300-byte fade table is its own data chunk, allocated after the v6 ones; every entry >> 3
            must equal the BACKDROP palette channel (checked).
Rules:   Source: docs\tasks\2026-10-25-chapter-cards\chapter-cards-trial.md and chapter-cards-report.md. Every vanilla
         word and body the code calls or copies is checked before the first write; the new space must be 0xFF; the
         code chunk must be named by no ROM word (a named chunk stays unused, notes "skipped"); a data chunk must
         be named by no real pointer word an earlier patch wrote (v3, _pointer_words: an aligned ROM-range word
         in a site below 8 MB, or a pool word a Thumb `ldr rd,[pc,#imm]` in any site loads). Packed data in the
         expansion area is not a pointer (beam_struggle 0x08926D91 at rom:0x910C94). A pointer kept in another
         module's data table, or one outside every "sites" entry, is not seen by that check. No earlier module
         may list the hook word in its "sites"; a second run raises. Hand-assembled Thumb through
         ssj2_form.assemble; tests\test_chapter_cards.py decodes it with thumb_dis and runs it with
         tests.test_ssj2.Cpu. v5: every STORY record (SHA-1), the words that name it, the ext table words
         (vanilla, or inside an earlier module's site) and both pool words are checked before the first write.
         Source v5: docs\tasks\2026-10-25-chapter-cards\chapter-cards-trial-v5.md, chapter-placement-report.md.
         Source v6: chapter-cards-trial-v6.md: card 5 moves from the flag 127 fade to the flag 129 fade (end of the
         Kami scene, before the map 2,20 load); the 127 record and its word stay vanilla.
         Source v7: card-fade-fix.md and card-fade-report.md (option B): the palette fade replaces the EVA fade;
         timing, song and leave are unchanged; OBJ palette untouched.
         Source v8: card-4-scene-build.md and card-4-scene-report.md: card 4 leaves the post-20 scene (and the
         in-field map reload goes with it) for the landing scene; Continue option c (flag 86 and visited bit 211).
         Source v9: card-4-scene-v9.md: the row, the player's first-landing spot and the camera move to an open
         patch of map 8,1 (c4v_patch.py, c4v_row_plan.py in scripts\one-time\2026-10-25-chapter-cards\).
         Source v10: card-4-scene-v10.md: the row becomes three groups with their own facings, off the save point
         (SPOTS, GROUPS, PLAYER_FACE; c4w_space.py, c4w_plan.py in scripts\one-time\2026-10-30-card-4-v10\).
         Source v11: card-4-scene-v11.md, the play test of v10: the Gohan branch stops forcing the player's
         facing (PLAYER_FACE), Gohan faces north where he is an NPC, Tien and Krillin look at Piccolo
         (AT_PLAYER, facing_to), and every sprite box keeps CLEAR floor from the save point rect.
         Source v12: card-4-scene-v12-spec.md: the first landing becomes the vanilla LAND, the camera becomes
         the map clamp, and the whole scene moves into the clearing around that landing (SPOTS, GROUPS,
         CAMERA, SOUTH_LIMIT; c4y_areas.py, c4y_plan.py in scripts\one-time\2026-10-31-card-4-v12\).
"""
import hashlib
import struct
from pathlib import Path

from rom import webfoot_decompress
from patches.bf_ki_pool import words_naming
from patches.npc_gi import _op_end, relocate
from patches.piccolo_gi_scene import code, ext, push, text
from patches.ssj2_form import assemble

# ===== chapter titles: (number, title, Continue flag or None = from the new game). Edit freely (ASCII only). =====
# Continue shows the last row whose flag is set in the save; STORY plays each card at its story point. Rows go in
# story order (chapter-placement-report.md); the module checks that the flag numbers rise. Me, 2026-10-29.
CHAPTERS = [
    (1, "The Mysterious Youth", None),          # new game
    (2, "Preparation", 26),                     # the Trunks warning scene ends: fade 120, SET 26, map 2,1,1
    (3, "The Androids Appear", 68),             # "Three years later...": fade 240, SET 68
    (4, "Into Gero's Lab", 86),                 # v8: first landing on the Northern Mountains (8,1), see LANDING
    (5, "A New Horror", 129),                   # v6: Kami says wait: SET 129, fade 90, map 2,20 (time machine)
    (6, "Perfection", 148),                     # Roshi's Island to the Lookout after Cell absorbs 17: fade 180
    (7, "The Cell Games", 158),                 # chamber exit time skip: SET 154, fade 240; 158 ends that scene
    (8, "The Champion's Hour", 195),            # after Cell: fade 240, Capsule Corp 6,3, SET 195
]

# ===== story points (v5): card: (live table word, record, length, SHA-1 of the base and r39 record, op start the
# card goes before, that op's bytes). Each card goes right after the fade out op. Word None = the chamber exit table
# word 0, found through CHAMBER_TYPE5. Bytes from scripts\one-time\2026-10-25-chapter-cards\v5_records_probe.txt;
# card 5 (v6, me, 2026-10-30 10:40 AM) from v6_probe.txt: index 17 of the Kami table rom:0x3DF720 (map 9,6).
# Card 4 (v8) plays in the landing scene (LANDING_CARD), not at a story point. =====
STORY = {
    2: (0x3BFF38, 0x3BFDB4, 0x27, "38e280433e6d56b9eebeea98e22b29ceec571a74", 0x3BFDBF, "001a"),      # SET 26
    3: (0x3B88BC, 0x3B8566, 0xA6, "c6b5a335a700037f83f4589e1ff33f7ffae57832", 0x3B8571, "0044"),      # SET 68
    5: (0x3DF764, 0x3DF28C, 0x82, "46ba206e3b3614e94d6394336f17a794d2cc648a", 0x3DF297,
        "1d0504280282408410"),                                                                        # map 2,20
    6: (0x3E61CC, 0x3E5ED4, 0x47, "b9e7a2fa12bd50ddf260eea17e111a81f45e7b8e", 0x3E5EDB,
        "1d051202028b408640"),                                                                        # map 9,1
    7: (None, 0x3DB4B0, 0x20, "1f0e417ccce9a650fe1de25c4f19c68b8d6a339c", 0x3DB4BF, "1d0402080260"),  # map 1,4
    8: (0x3EC81C, 0x3EC678, 0x4D, "0ec2a0cf758e9968d7c5468397342eb424bfe145", 0x3EC683, "0001"),      # HUD on
}
CHAMBER_TYPE5, CHAMBER_VANILLA = (0x3CF7E4, 0x3D1530), 0x3DBDD4   # +4 of the two type 5 records; vanilla table

# ===== card 4 landing scene (v8): my design and words (card-4-scene-study.md, me, 2026-10-30 6:45-8:00
# PM). Leader (ext 11) 0 Gohan, 1 Piccolo, 2 Vegeta (Trunks cannot lead there; any other value plays Gohan's).
# Everyone else flies north at the end. v9 (9:40 PM "they fly in being blocked"): the actors land on the one
# open patch of 8,1 (376x200): no BG1 canopy, BG2 rock or closed collision cell in any actor box (c4v_patch.txt).
# v10 (card-4-scene-v10.md, 11:20 PM "I dont like them standing in a straight line like that facing the same
# direction, especially ontop of the capsule corp switcher"): three groups with their own facings, all clear of the
# save point rect (56,48)-(105,97) and of the text box area south of y 84 (c4w_space.txt, c4w_plan.txt).
# v11 (card-4-scene-v11.md, me, 2026-10-30 11:55 PM, after playing all three branches): the Gohan branch keeps
# the DOWN the arrival sets under black (no forced turn); Gohan faces UP where he lands as an NPC; Tien and Krillin
# look at the player in the Piccolo branch; and every sprite box keeps real floor between itself and the save
# point rect.
# v12 (card-4-scene-v12-spec.md, me, 2026-10-31 "card 4 is a mess. Lets use the default landing location, not the
# save point since its complicating everything"): the first landing is the vanilla LAND, so the save point and its
# pocket leave the problem. The camera goes to the clamp (137, 41), which is the view the game itself gives at
# that landing. One clearing holds the whole scene: x 176-308, y 84-124, found as a connected component of the
# clear-spot grid (c4y_areas.txt), and it has three parts my three boxes map onto. FAR LEFT is its west
# arm, one row at y 100, x 176-208. TOP is its wide top, x 232-264 at y 84 down to x 216-280 at y 96. BESIDE is
# its two south prongs, x 232-248 and x 296-308, which flank the landing. The spots below sit in those parts
# (c4y_plan.txt, one picture a leader). =====
LANDING_CARD = 4
VISITED = {4: 211}                              # Continue option c: chapter 4 also needs map 8,1's visited bit
LANDING_ITEM, LANDING_REGION_WORD, LANDING_SCRIPT = 0x3FBC5C, 0x3FBE54, 0x3FBC50   # world map region 11
LANDING_ITEM_BYTES = "c3c2000839d80008000ae803710a610450bc3f08"   # script item, A-press, rect, script 0x083FBC50
LANDING_SCRIPT_BYTES = "1d0510020284208200022611"   # push 8,1,1,272,128 ; ext 38 ; end
SCRIPT_ITEM, SCENE_ITEM = 0x0800C2C3, 0x0800D7E1   # factories; scene item as map 9,6 item rom:0x404468
LAND = (8, 1, 1, 272, 128)                      # the vanilla landing: zone, area, var, x, y. v12: the first
#                                                 landing uses it too, so both arms of record 0 carry one spot.
#                                                 Record 0 runs before the leader pick, so it serves all three
#                                                 branches. (272,128) is inside region 0 (249,89)-(296,144), the
#                                                 world map exit rect, which is where the game puts the player.
GOHAN, PICCOLO, VEGETA = 0, 1, 2                # ext 11 leader values (post-20 branches rom:0x3D48B6)
EQ, JZ, END_OP = 11, 19, 17                     # ops: eq (rom:0x3D5482), skip when zero, end (pops the next index)
ID = {"Gohan": 53, "Piccolo": 103, "Vegeta": 3, "Krillin": 76, "Tien": 121, "Trunks": 128}   # Vegeta: party id
FROM_Y, OFF_Y = 260, -40                        # spawn and fly-off rows, both off the view
CLAMP = (137, 41)                               # map 8,1 layout 0x0858CB30 +8/+0xA: the largest camera top-left
CAMERA = (137, 41, 255)                         # view top-left, speed; set under black. v12: the clamp itself,
#                                                 which is the view the game gives at LAND. A smaller y only
#                                                 pushes the landing further down the screen, and a smaller x
#                                                 buys ground the scene does not use. Every actor fits: the
#                                                 widest sprite spans x - 9 to x + 25 and y - 26 to y + 10
#                                                 (bible CJH hurtboxes), so x 176 reads at screen 30 and x 296
#                                                 at screen 184.
FADE, FLY_SOUND = 60, 26
DOWN, UP, LEFT, RIGHT = 0, 1, 2, 3              # actor facing byte (bible PGS and CJ2 rows)
LANDING_END = 16                                # table word 16 = 0 ends the scene
SAVE_RECT = (56, 48, 105, 97)                   # map 8,1 region 1: the save point ("the capsule corp switcher")
BOX_TOP = 88                                    # the dialog box starts at this screen row (measured on a real
#                                                 frame, c4y_textbox.txt)
SOUTH_SCREEN = 84                               # the lowest screen row an NPC's feet may take. v10 and v11 used
#                                                 the same number against a camera at y 0, so it is unchanged.
SOUTH_LIMIT = CAMERA[1] + SOUTH_SCREEN          # the world row it becomes at this camera: 125
SPRITE = (0, 16, -24, 8)                        # the drawn 16x32 frame around (x, y): bible CJ3 OAM rows
CLEAR, POCKET_CLEAR = 8, 0                      # floor an actor's sprite box keeps from SAVE_RECT. An actor
#                                                 wholly west of the rect keeps POCKET_CLEAR, every other actor
#                                                 keeps CLEAR. v12 stands nobody near it: the worst is 78 px.
NEAR, APART = 32, 40                            # a group member has a mate within NEAR; other groups are APART
AT_PLAYER = None                                # a facing worked out from the spot: look at the player
# v12 spots. The player lands at LAND (272,128) in every branch. FAR LEFT is the clearing's west arm (y 100,
# x 176-208), TOP is its wide top (y 84-96), BESIDE is its two south prongs beside the landing. My
# layout: the trio talks in the TOP box with Piccolo a bit lower, Gohan stands alone in the FAR LEFT box, and
# the leader's own group stands at the landing.
SPOTS = {                                       # branch: actor -> (x, y, facing); the player stands at LAND
    "gohan": {"Krillin": (264, 84, LEFT), "Tien": (232, 84, RIGHT), "Piccolo": (248, 92, UP),
              "Trunks": (176, 100, RIGHT), "Vegeta": (192, 100, LEFT)},
    "piccolo": {"Krillin": (248, 124, AT_PLAYER), "Tien": (296, 120, AT_PLAYER), "Gohan": (184, 100, UP),
                "Trunks": (236, 84, RIGHT), "Vegeta": (256, 84, LEFT)},
    "vegeta": {"Krillin": (264, 84, LEFT), "Tien": (232, 84, RIGHT), "Piccolo": (248, 92, UP),
               "Gohan": (184, 100, UP), "Trunks": (296, 120, AT_PLAYER)},
}
PLAYER_FACE = {"piccolo": UP, "vegeta": RIGHT}  # the leader's own facing. A branch with no row keeps the DOWN the
#                                                 arrival already sets under black, so the player never turns on
#                                                 screen (v11 gohan, 11:55 PM "just leave it that way").
GROUPS = {                                      # branch: group -> members ("player" = actor 0, at LAND)
    "gohan": {"top": ["Tien", "Piccolo", "Krillin"], "farleft": ["Trunks", "Vegeta"], "landing": ["player"]},
    "piccolo": {"top": ["Trunks", "Vegeta"], "farleft": ["Gohan"], "landing": ["Krillin", "Tien", "player"]},
    "vegeta": {"top": ["Tien", "Piccolo", "Krillin"], "farleft": ["Gohan"], "landing": ["Trunks", "player"]},
}
LINES = {                                       # index: (next, portrait, text); 0x0B starts a new box (<= 4 lines)
    5: (6, 3, "Now we better get moving, we don't have much time!"),
    6: (7, 95, "Okay, let's do it.\x0bI'll head a little further north to see what I find out there."),
    8: (9, 4, "Would you stop following me, boy?\x0bYou're getting on my nerves!"),
    9: (10, 98, "Sorry, but there's no way I am planning to let you fight the androids on your own!"),
    10: (11, 4, "And just what are you planning to do to stop me?\x0bIt's going to take more than that little "
                "sword of yours to stand in my way!"),
    11: (12, 98, "How many times do I have to tell you before it sinks into your thick skull?\x0bNever "
                 "underestimate the power of the androids!"),
    12: (15, 4, "Hah!\x0bAnd never underestimate the power of a real super saiyan who loves to take on a "
                "challenge!\x0bWell, if you're going to stay, you can at least help me find Dr. Gero's lab!"),
}
SLOT_VISITED = 0xE7 - 0xB4                      # visited bits after the story flags (save +0xE7, 0x080041E2)

# ===== card look and timing (v2: Buu's Fury's, me, 2026-10-25 4:25 PM "Card length should match BF") =====
FADE_IN, WAIT, FADE_OUT = 100, 250, 100  # BF card script 0x0879B004: ext 121 (100), ext 136 (250), ext 120 (100)
MAX_SHIFT = 24                           # level rule search: k x mul >> shift, shift 0-24 (see level_rule)
BF_SONG = 37                             # BF card music: push 37 ; ext 35 at 0x0879B011 (ported, see SONG PORT)
CENTRE_X, BLOCK_Y, LINE_PITCH = 120, 75, 20   # BF lines at (120, 65) and (120, 85): ext 4/5 + ext 178
TEXT_OUTLINE, TEXT_FILL = 247, 248       # BG palette entries the backdrop does not use (checked)
TEXT_FROM_OBJ = {TEXT_OUTLINE: 1, TEXT_FILL: 2}   # BF OBJ palette rom:0x5652C bank 0: 1 = 0x0000, 2 = 0xFFFF (white)

# ===== constants: sources (base and r39 bytes, read 2026-10-25) =====
ROM_BASE = 0x08000000
FS_VTABLE, FS_SLOT = 0x08023B0C, 0x2C
HOOK = FS_VTABLE - ROM_BASE + FS_SLOT                    # rom:0x23B38
ORIG_CONTINUE = 0x0800180D
IMAGE_VTABLE = 0x080237C0                                # copyright image scene (enter 0x0801EDFB)
IMAGE_SLOTS = (0x2F45, 0xFFFFB63B, 0xFFFFB6F3, 0x2D51, 0x2D21, 0xFFFFB6BF, 0x2D09, 0x2F3D, 0x28C9, 0x2BE5,
               0xFFFF4027, 0x2D05)                       # +0x00..+0x2C base-relative words
NEW_SLOTS = {0x4: "card_enter", 0x8: "card_leave", 0x14: "card_tick"}
BODIES = {                                               # GBA address: first bytes (vanilla)
    0x0800180C: "f0b5041c006983b0032805d10020fef7",      # Continue (file select +0x2C)
    0x080019F6: "ff2365335943081840780121c007c0170130081a7047",   # slot used: image +1 bit 0
    0x0801F2F4: "70b5224c051ca0682268411c80000019",      # scene_push
    0x0801F08C: "f0b55e4903300d6801218010",              # alloc
    0x0801F110: "f0b5002828d0041c083c0021",              # free
    0x08020A4C: "70b501258570057000224270",              # music_play(player, record)
    0x08020820: "10b44178002201310906090e41708378994213d3036901330361c1684c68e35cff2b00d1"
                "02614b68046909681b5d9b00c95842704b1c43610978817000214b00",   # row decoder (record +0, +4, +0xC)
    0x0801FE72: "9c4bd27a043b1b68097adb689d6853009a189200aa188262",   # note: sample entry = record +8 + 12 x ins
    0x08009CBA: "55484168002048717047",                  # ext 50 music stop: player +5 = 0 (as BF ext 36)
    0x08008F8E: "08b50b681a7801330b609100a04a515818f0c4fe08bd",   # op 2: ext n = [pool rom:0x921C + 4n](ctx)
    0x0800D7E0: "38b5051c182011f051fc041c01d1201c38bd291c201cf7f7fffb044820602869606100202082201cf2e70000"
                "443e0208",                              # v8 scene item factory: vtable 0x08023E44, +0x14 = data
    0x0800D7A0: "30b50a1cff3289b091320092021c1032416902ac201c164bfdf779fe082011f065fc002802d01349",  # activate
    0x08009628: "10b5041c006801388100206009194a68013820608000001941687c48006afaf7",   # v8 ext 23 visited test
}
PLAYER, PLAYER_WORD = 0x030026C8, 0x081D4EF8             # title_enter: ldr r0,[0x081D4EEC,#0xc]
EXT_TABLE, EXT_OPS, CARD_OP = 0x3B5D28, 145, 145         # ext op words 0-144; word 145 is data (bible DS8)
EXT_TABLE_SHA1 = "eb19e2afaec1dc9324fb66d4ebe889216ef7a699"   # the 145 base words
EXT_POOLS = (0x921C, 0x92DC)                             # every ROM word naming 0x083B5D28 (op 2, ops 21-26)
RETIRED = "vanilla ext op table, retired: no byte changes; a later write there refuses"   # a "sites" name
CODE_REGION = (0x0, 0x28724)
MAX_TRIES = 32                                           # v8: 8 ran out on r39 (0x9304C0 on: stray words name it)
VRAM_TILES_MAX = 0xF800 // 64                            # 8bpp tiles below the screenblock at 0x0600F800
SYMS = {"SLOT_VALID": 0x080019F7, "ORIG_CONTINUE": ORIG_CONTINUE, "ALLOC": 0x0801F08D, "FREE": 0x0801F111,
        "SCENE_PUSH": 0x0801F2F5, "MUSIC_PLAY": 0x08020A4D, "PLAYER": PLAYER, "LAST_ROW": len(CHAPTERS) - 1,
        "VISIT_BYTE": 0xFF, "VISIT_LSL": 0x1F,                                        # set from VISITED
        "IO": 0x04000000, "PAL_RAM": 0x05000000, "VRAM": 0x06000000,
        "VRAM_MAP": 0x0600F800, "SLOT_SIZE": 0x164, "BG3_CNT": 0x1F83,
        "FADE_IN": FADE_IN, "HOLD_END": FADE_IN + WAIT, "FADE_OUT": FADE_OUT,
        "TABLE": 0xFFFF0001, "TABLE_END": 0xFFFF0002, "VTABLE": 0xFFFF0003, "SONG": 0xFFFF0004,
        "BACKDROP": 0xFFFF0005, "BASE_BYTES": 0xFFFF0006, "VRAM_EXTRA": 0xFFFF0007,
        "FADE_TABLE": 0xFFFF0008}                                                     # placeholders

# ===== CARD LOOK (v3): Buu's Fury's backdrop and title font, read from the BF ROM (SHA-1 checked) =====
BF_SOURCE_WORDS = {0x753A1C: 0x087548DC,                 # [0x08753A18 + 4]: the font object ext 178 measures with
                   0x7548DC: 0x08753A20,                 # font object +0: the glyph table
                   0x2CAAC: 0x0805632C,                  # BG palette copy source (to 0x05000000)
                   0x2CAB0: 0x0805652C,                  # OBJ palette copy source (to 0x05000200)
                   0x7164: 0x080701B0}                   # v7: ext 121's table blend 0x08007074 reads this table
BF_GLYPHS, BF_BG_PALETTE, BF_OBJ_PALETTE = 0x753A20, 0x5632C, 0x5652C
BF_FADE_TABLE = 0x701B0                                  # 512 x RGB888 (BG then OBJ); >> 3 = the BF palette
BF_SCREEN, BF_BANKS = 0x29B988, 0x179764                 # map 29 screenblock codec frame; tile bank pointer table
RAW_TILES = {0: (0, 0), 1: (20, 89), 2: (55, 92), 3: (111, 73)}   # raw cell -> (bank, tile)
RAW_BASE = 37756                                         # raw 4-599 -> global tile RAW_BASE + raw (banks 147-149)
BACKDROP_PX_SHA1 = "20b7eb0c4026d63265e2f0a81f237177fb9b4c50"   # v3_bf_text.py matches it to my screenshot
# BF's card font has blank '.' and "'" glyphs (width 2, no bits): BF titles use neither. Ours (not BF art, me
# review pending): drawn the BF way from these columns; the BF width is kept, so wrapping does not change.
EXTRA_GLYPHS = {".": (0x3000, 0x3000), "'": (0x001E, 0x000E)}   # dot on rows 12-13; tick on rows 1-4

# ===== SONG PORT: Buu's Fury song 37 into the expansion area (data only; the player code is the same) =====
# Both games run one Webfoot tracker player: music_play, row decoder, 32 effect handlers, note table and mixer
# match instruction for instruction (report v2, v2_sound_diff*.txt). A song is a 20-byte record {+0 pattern
# pointers, +4 order bytes (0xFF = loop), +8 sample directory (12-byte entries: u32 data, u16 flags, u16 loop,
# u16 length, u16 rate), +0xC mask table (14 bytes), +0x10 tempo, +0x11 ticks per row}, and the player reads all
# of it through the record. So the port copies the record's data, rebases its pointers and plays the new record.
BF_PATH = Path(__file__).resolve().parents[3] / "data" / "roms" / "Dragon Ball Z - Buu's Fury (USA).gba"
BF_SHA1 = "f1c4b07554d2a3b1ad2f325307051e775ce68087"
LG_PATH = BF_PATH.with_name("Dragon Ball Z - The Legacy of Goku II (USA).gba")   # vanilla ext words (read only)
BF_MUSIC_TABLE = 0x083BB78C                              # BF ext 35 0x080008BC: table + 20 x song
BF_RECORD = "8c613a08fc5d3a088cd1360840d5360873040000"   # song 37: patterns, orders, directory, masks, 115, 4
SAMPLE_TAIL = 16                                         # bytes copied past each sample end (mixer read-ahead margin)
SILENT_RATE = 16000                                      # unused directory entries: 16 silent bytes

# ===== new code (ARMv4T Thumb) =====
CODE = """
; ===== 1. Continue hook: file select vtable +0x2C, r0 = file select object
cc_continue:
    push {r4,r5,lr}
    add r4,r0,#0x0
    ldr r5,[r4,#0x10]       ; slot index; 3 is not a save
    cmp r5,#0x3
    beq cc_orig
    add r0,r4,#0x0
    add r0,#0x14            ; slot images, 0x164 bytes each
    add r1,r5,#0x0
    ldr r3,=SLOT_VALID
    bl via_r3               ; 1 when the slot holds a save
    cmp r0,#0x0
    beq cc_new              ; an empty slot: vanilla Continue starts a new game (0x08001842)
    ldr r0,=SLOT_SIZE
    mul r0,r5
    add r0,r0,r4
    add r0,#0x14
    add r0,#0xb4            ; the slot image's story flags
    bl cc_pick
    b cc_show
cc_new:
    ldr r0,=TABLE
    ldr r0,[r0,#0x4]        ; row 1: the new game card
cc_show:
    bl cc_run
cc_orig:
    add r0,r4,#0x0
    ldr r3,=ORIG_CONTINUE
    bl via_r3               ; vanilla Continue: slot copy, field scene, map load
    pop {r4,r5,pc}
via_r3:
    bx r3

; ===== 2. pick: r0 = flag bytes; r0 = card of the last row whose flag is set (row 0 always matches);
;          v8: a row with +3 bit 1 also needs the VISITED map bit (Continue option c)
cc_pick:
    push {r4,r5,lr}
    ldr r4,=TABLE_END
    ldr r5,=TABLE
pick_next:
    sub r4,#0x8
    ldrb r1,[r4,#0x3]
    lsl r1,r1,#0x1f         ; bit 0: from the new game
    bmi pick_hit
    ldrh r1,[r4,#0x0]       ; flag >> 3
    ldrb r2,[r0,r1]
    ldrb r1,[r4,#0x2]       ; flag & 7
pick_shift:
    cmp r1,#0x0
    beq pick_test
    lsr r2,r2,#0x1
    sub r1,#0x1
    b pick_shift
pick_test:
    lsl r2,r2,#0x1f
    bpl pick_miss
    ldrb r1,[r4,#0x3]
    lsl r1,r1,#0x1e         ; bit 1: the map visited bit too
    bpl pick_hit
    mov r1,#VISIT_BYTE      ; past ldrb's 31-byte immediate
    ldrb r2,[r0,r1]
    lsl r2,r2,#VISIT_LSL
    bmi pick_hit
pick_miss:
    cmp r4,r5
    bne pick_next
pick_hit:
    ldr r0,[r4,#0x4]
    pop {r4,r5,pc}

; ===== 3. run: r0 = card; a 20-byte scene {vtable, frame, card, 4 saved registers} through scene_push
cc_run:
    push {r4,lr}
    add r4,r0,#0x0
    mov r0,#0x14
    ldr r3,=ALLOC
    bl via_r3
    cmp r0,#0x0
    beq run_done
    ldr r1,=VTABLE
    str r1,[r0,#0x0]
    mov r1,#0x0
    str r1,[r0,#0x4]
    str r4,[r0,#0x8]
    ldr r3,=SCENE_PUSH
    bl via_r3
run_done:
    pop {r4,pc}

; ===== 4. enter (+4): BG3 card, image scene registers, song
card_enter:
    push {r4,r5,r6,lr}
    add r4,r0,#0x0
    ldr r5,=IO
    add r2,r5,#0x0
    add r2,#0x50
    ldrh r1,[r5,#0x0]       ; keep DISPCNT, BG3CNT, BLDCNT, BLDALPHA as file select left them
    strh r1,[r4,#0xc]
    ldrh r1,[r5,#0xe]
    strh r1,[r4,#0xe]
    ldrh r1,[r2,#0x0]
    strh r1,[r4,#0x10]
    ldrh r1,[r2,#0x2]
    strh r1,[r4,#0x12]
    mov r0,#0x0
    strh r0,[r5,#0x0]       ; DISPCNT 0 while VRAM changes: black backdrop
    strh r0,[r2,#0x0]       ; BLDCNT 0: no blend effect (v7: the tick fades the BG palette)
    strh r0,[r2,#0x2]       ; BLDALPHA 0
    ldr r1,=BG3_CNT
    strh r1,[r5,#0xe]
    strh r0,[r5,#0x1c]      ; BG3 scroll 0,0
    strh r0,[r5,#0x1e]
    bl scale                ; r0 = L 0: BG palette black, so the first card frame shows no colour
    ldr r0,=VRAM
    ldr r1,=BACKDROP        ; BF BG palette (0x200 bytes), then the base tiles
    ldr r2,=0x200
    add r1,r1,r2
    ldr r2,=BASE_BYTES
    bl copy
    ldr r6,[r4,#0x8]        ; card: u32 tile bytes, screenblock, tiles
    ldr r0,=VRAM_MAP
    add r1,r6,#0x4
    ldr r2,=0x800
    bl copy
    ldr r0,=VRAM_EXTRA      ; the card's own tiles go after the base tiles
    ldr r1,=0x804
    add r1,r1,r6
    ldr r2,[r6,#0x0]
    bl copy
    ldr r1,=0x800
    strh r1,[r5,#0x0]       ; DISPCNT: mode 0, BG3 only
    ldr r0,=PLAYER
    ldr r1,=SONG
    ldrb r2,[r0,#0x5]
    cmp r2,#0x1
    bne enter_play
    ldr r2,[r0,#0xc]
    cmp r2,r1
    beq enter_done          ; already playing (title_enter check)
enter_play:
    ldr r3,=MUSIC_PLAY
    bl via_r3
enter_done:
    pop {r4,r5,r6,pc}
copy:                       ; r0 dst, r1 src, r2 bytes (a nonzero multiple of 4); word writes (VRAM safe)
    ldr r3,[r1,#0x0]
    str r3,[r0,#0x0]
    add r0,#0x4
    add r1,#0x4
    sub r2,#0x4
    bne copy
    bx lr

; ===== 5. tick (+0x14): BF timing, no skip: FADE_IN frames in, WAIT frames, FADE_OUT frames out; 1 = end.
;          v7: the BG palette fades as BF ext 121 and ext 120 fade theirs, a new level every frame
card_tick:
    push {r4,lr}
    ldr r1,[r0,#0x4]
    add r1,#0x1
    str r1,[r0,#0x4]
    ldr r3,=FADE_IN
    cmp r1,r3
    bgt tick_hold
    ldr r0,=IN_MUL
    mul r0,r1
    lsr r0,r0,#IN_SHIFT     ; L = (frame << 8) / FADE_IN
    bl rise
    b tick_more
tick_hold:
    ldr r3,=HOLD_END
    sub r4,r1,r3            ; k = frames into the fade out
    ble tick_more           ; hold: no write, the palette is full from frame FADE_IN
    mov r0,#0x0             ; L 0 from k = FADE_OUT on
    ldr r3,=FADE_OUT
    cmp r4,r3
    bge tick_out
    ldr r0,=OUT_MUL
    mul r0,r4
    lsr r0,r0,#OUT_SHIFT    ; (k << 8) / FADE_OUT
    ldr r1,=0x100
    sub r0,r1,r0            ; L = 256 - (k << 8) / FADE_OUT
tick_out:
    bl scale
    ldr r3,=FADE_OUT
    cmp r4,r3
    blt tick_more
    mov r0,#0x1             ; scene end on the last fade frame, black (as BF ext 120 ends)
    pop {r4,pc}
tick_more:
    mov r0,#0x0
    pop {r4,pc}

; ===== 5b. BG palette at level r0 = L (0-256). L 256: the BACKDROP bytes as stored (bit 15 kept).
;           rise: each 8-bit channel of the fade table x L >> 11 (BF ext 121's blend 0x08007074)
;           scale: each 5-bit channel of the BACKDROP palette x L >> 8 (BF ext 120's loop 0x080176D6)
rise:
    push {r4,r5,r6,lr}
    ldr r1,=FADE_TABLE
    ldr r2,=PAL_RAM
    ldr r3,=0x100
    cmp r0,r3
    bge level_full
    add r6,r0,#0x0          ; L
    add r0,r3,#0x0          ; 256 entries
rise_next:
    ldrb r4,[r1,#0x0]
    mul r4,r6
    lsr r4,r4,#0xb          ; red
    ldrb r5,[r1,#0x1]
    mul r5,r6
    lsr r5,r5,#0xb
    lsl r5,r5,#0x5          ; green
    add r4,r4,r5            ; no orr in the assembler; the fields do not overlap
    ldrb r5,[r1,#0x2]
    mul r5,r6
    lsr r5,r5,#0xb
    lsl r5,r5,#0xa          ; blue
    add r4,r4,r5
    strh r4,[r2,#0x0]
    add r1,#0x3
    add r2,#0x2
    sub r0,#0x1
    bne rise_next
    pop {r4,r5,r6,pc}
scale:
    push {r4,r5,r6,lr}
    ldr r1,=BACKDROP
    ldr r2,=PAL_RAM
    ldr r3,=0x100
    cmp r0,r3
    blt scale_part
level_full:
    ldr r1,=BACKDROP
    add r0,r2,#0x0
    ldr r2,=0x200
    bl copy
    pop {r4,r5,r6,pc}
scale_part:
    add r6,r0,#0x0          ; L
    add r0,r3,#0x0          ; 256 entries
scale_next:
    ldrh r3,[r1,#0x0]
    lsl r4,r3,#0x1b
    lsr r4,r4,#0x1b         ; red
    mul r4,r6
    lsr r4,r4,#0x8
    lsl r5,r3,#0x16
    lsr r5,r5,#0x1b         ; green
    mul r5,r6
    lsr r5,r5,#0x8
    lsl r5,r5,#0x5
    add r4,r4,r5
    lsl r5,r3,#0x11
    lsr r5,r5,#0x1b         ; blue
    mul r5,r6
    lsr r5,r5,#0x8
    lsl r5,r5,#0xa
    add r4,r4,r5
    strh r4,[r2,#0x0]
    add r1,#0x2
    add r2,#0x2
    sub r0,#0x1
    bne scale_next
    pop {r4,r5,r6,pc}

; ===== 6. leave (+8): music stop, black BG palette, file select's registers back, then free the object
card_leave:
    push {r4,lr}
    add r4,r0,#0x0
    mov r0,#0x0
    ldr r1,=PLAYER
    strb r0,[r1,#0x5]       ; music stop, as BF ext 36 ends its card (LoG ext 50 does the same)
    ldr r1,=PAL_RAM
    ldr r2,=0x200
leave_zero:
    str r0,[r1,#0x0]        ; BG palette black: file select layers stay dark until the map loads
    add r1,#0x4
    sub r2,#0x4
    bne leave_zero
    ldr r1,=IO
    add r2,r1,#0x0
    add r2,#0x50
    ldrh r0,[r4,#0x12]      ; the four registers back as file select left them (vanilla state for Continue)
    strh r0,[r2,#0x2]
    ldrh r0,[r4,#0x10]
    strh r0,[r2,#0x0]
    ldrh r0,[r4,#0xe]
    strh r0,[r1,#0xe]
    ldrh r0,[r4,#0xc]
    strh r0,[r1,#0x0]
    add r0,r4,#0x0
    ldr r3,=FREE
    bl via_r3
    pop {r4,pc}

; ===== 7. story card, ext CARD_OP (r0 = script context): pop chapter N, show its card, the script goes on.
;          A map load follows every card (v8), and it reloads the map graphics and music
cc_story:
    push {r4,lr}
    ldr r1,[r0,#0x0]        ; pop, as every ext handler (ext 69 0x0800A65E)
    sub r1,#0x1
    str r1,[r0,#0x0]
    lsl r1,r1,#0x2
    add r0,r1,r0
    ldr r4,[r0,#0x4]
    sub r4,#0x1             ; row index; 0 or past the table: no card
    bmi story_done
    cmp r4,#LAST_ROW
    bgt story_done
    lsl r4,r4,#0x3
    ldr r0,=TABLE
    add r4,r4,r0
    ldr r0,[r4,#0x4]
    bl cc_run
story_done:
    pop {r4,pc}
"""


# ===== helpers =====

def _u16(rom: bytes, off: int) -> int:
    return struct.unpack_from("<H", rom, off)[0]


def _u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def _expect(rom: bytearray, off: int, want: bytes) -> None:
    if bytes(rom[off:off + len(want)]) != want:
        raise ValueError(f"rom:0x{off:X} is {bytes(rom[off:off + len(want)]).hex()}, expected {want.hex()}")


def level_rule(n: int) -> tuple:
    """(mul, shift): k x mul >> shift == (k << 8) // n for every k in 0..n, and n x mul < 2**32. The card's fade
    level without the ARM divide that BF and LoG ext 40 / ext 41 call (0x08021F30, entered by `bx pc`)."""
    for shift in range(MAX_SHIFT + 1):
        mul = -(-(256 << shift) // n)
        if n * mul < 1 << 32 and all(k * mul >> shift == (k << 8) // n for k in range(n + 1)):
            return mul, shift
    raise ValueError(f"no exact multiply for (k << 8) / {n} with a shift up to {MAX_SHIFT}")


def _written(notes: dict) -> list:
    """(module, (offset, length, ...)) of every earlier module's "sites": triples, or bare offsets."""
    out = []
    for name, n in notes.items():
        for site in n.get("sites", []) if isinstance(n, dict) else []:
            out.append((name, (site, 1) if isinstance(site, int) else tuple(site)))
    return out


# ===== cards =====

_BF = {}


def bf_rom() -> bytes:
    """The BF ROM bytes, SHA-1 checked once (read only)."""
    if "rom" not in _BF:
        bf = BF_PATH.read_bytes()
        if hashlib.sha1(bf).hexdigest() != BF_SHA1:
            raise ValueError(f"{BF_PATH.name}: SHA-1 is not {BF_SHA1}")
        for off, want in BF_SOURCE_WORDS.items():
            if _u32(bf, off) != want:
                raise ValueError(f"BF rom:0x{off:X} is 0x{_u32(bf, off):08X}, expected 0x{want:08X}")
        _BF["rom"] = bf
    return _BF["rom"]


def _tile(bf: bytes, banks: dict, raw: int) -> bytes:
    """64 bytes of the 8bpp tile BF shows for a raw map 29 cell."""
    b, t = RAW_TILES[raw] if raw in RAW_TILES else divmod(RAW_BASE + raw, 256)
    if b not in banks:
        banks[b] = webfoot_decompress.unpack_frame(bf, _u32(bf, BF_BANKS + 4 * b) - ROM_BASE)[2]
    return bytes(banks[b][64 * t:64 * t + 64])


def backdrop(bf: bytes) -> tuple:
    """(240x160 palette indices, BG palette 0x200 bytes with the two text colours) of BF map 29."""
    sb = webfoot_decompress.unpack_frame(bf, BF_SCREEN)[2]
    px, banks = bytearray(240 * 160), {}
    for ty in range(20):
        for tx in range(30):
            tile = _tile(bf, banks, _u16(sb, 2 * (ty * 32 + tx)))
            for y in range(8):
                px[(ty * 8 + y) * 240 + tx * 8:(ty * 8 + y) * 240 + tx * 8 + 8] = tile[8 * y:8 * y + 8]
    if hashlib.sha1(px).hexdigest() != BACKDROP_PX_SHA1:
        raise ValueError("the BF map 29 backdrop does not render to the screenshot-checked picture")
    if set(TEXT_FROM_OBJ) & set(px):
        raise ValueError(f"the backdrop uses text palette entries {sorted(set(TEXT_FROM_OBJ) & set(px))}")
    pal = bytearray(bf[BF_BG_PALETTE:BF_BG_PALETTE + 0x200])
    for i, entry in TEXT_FROM_OBJ.items():                # only entries the backdrop does not use change
        pal[2 * i:2 * i + 2] = bf[BF_OBJ_PALETTE + 2 * entry:BF_OBJ_PALETTE + 2 * entry + 2]
    return bytes(px), bytes(pal)


def _glyph(bf: bytes, ch: str) -> tuple:
    """(width, [u16 column bits, bit 0 at the top]) of one BF card font glyph."""
    g = _u16(bf, BF_GLYPHS + 2 * ord(ch)) if ord(ch) < 0xFF else 0
    if not g:
        raise ValueError(f"{ch!r} has no glyph in the BF card font (BF 0x0803F70C draws nothing)")
    w = _u16(bf, BF_GLYPHS + 2 * g)
    cols = [_u16(bf, BF_GLYPHS + 2 * (g + 1 + k)) for k in range(w)]
    if ch != " " and not any(cols):
        if ch not in EXTRA_GLYPHS or len(EXTRA_GLYPHS[ch]) != w:
            raise ValueError(f"{ch!r} is blank in the BF card font and has no EXTRA_GLYPHS entry of width {w}")
        cols = list(EXTRA_GLYPHS[ch])
    return w, cols


def text_width(bf: bytes, text: str) -> int:
    """Pixel width as BF counts it (0x0803FFE8): sum of (glyph width + 1)."""
    return sum(_glyph(bf, c)[0] + 1 for c in text)


def _fits(bf: bytes, text: str) -> bool:
    w = text_width(bf, text)
    pen = CENTRE_X - (w + 1) // 2
    return pen - 1 >= 0 and pen + w - 1 <= 239            # outline columns pen - 1 .. pen + w - 1


def card_lines(bf: bytes, number: int, title: str) -> list:
    """["Chapter N", title] or, when the title is too wide, the title split at the space that keeps the widest
    part narrowest."""
    lines = [f"Chapter {number}"]
    if _fits(bf, title):
        return lines + [title]
    words = title.split(" ")
    splits = [(" ".join(words[:k]), " ".join(words[k:])) for k in range(1, len(words))]
    best = min(splits, key=lambda s: max(text_width(bf, s[0]), text_width(bf, s[1])), default=None)
    if best is None or not all(_fits(bf, t) for t in best):
        raise ValueError(f"{title!r} does not fit on two BF lines")
    return lines + list(best)


def draw_line(px: bytearray, bf: bytes, text: str, cy: int) -> None:
    """One BF line centred on (CENTRE_X, cy), as 0x0803F70C draws it: fill over outline."""
    pen = CENTRE_X - (text_width(bf, text) + 1) // 2
    for ch in text:
        w, cols = _glyph(bf, ch)
        for c in range(-1, w + 1):
            v = cols[c] if 0 <= c < w else 0
            nb = (cols[c - 1] if 0 < c <= w else 0) | (cols[c + 1] if c + 1 < w else 0) | v << 1 | v >> 1
            for b in range(17):
                at = (cy - 6 + b) * 240 + pen + c
                if v >> b & 1:
                    px[at] = TEXT_FILL
                elif nb >> b & 1 and px[at] != TEXT_FILL:
                    px[at] = TEXT_OUTLINE
        pen += w + 1


def render_card(bf: bytes, number: int, title: str) -> bytes:
    """240x160 palette indices: the BF backdrop, then the card lines in BF's font, centred on y BLOCK_Y."""
    px = bytearray(backdrop(bf)[0])
    lines = card_lines(bf, number, title)
    for k, text in enumerate(lines):
        if not text.isascii():
            raise ValueError(f"{text!r} is not ASCII")
        draw_line(px, bf, text, BLOCK_Y - LINE_PITCH * (len(lines) - 1) // 2 + LINE_PITCH * k)
    return bytes(px)


def _tiles_of(px: bytes) -> list:
    """The 600 8bpp tiles of a 240x160 picture, screen order."""
    return [b"".join(px[(ty * 8 + y) * 240 + tx * 8:(ty * 8 + y) * 240 + tx * 8 + 8] for y in range(8))
            for ty in range(20) for tx in range(30)]


def backdrop_blob(bf: bytes) -> tuple:
    """(BG palette + unique base tiles, {tile bytes: id}) of the BF backdrop."""
    px, pal = backdrop(bf)
    ids = {}
    for t in _tiles_of(px):
        ids.setdefault(t, len(ids))
    return pal + b"".join(ids), ids


def fade_table(bf: bytes, pal: bytes) -> bytes:
    """0x300 bytes (v7): BF's RGB888 fade table rows for BG entries 0-255, the text entries from its OBJ rows
    (TEXT_FROM_OBJ, as backdrop() does for the palette); every channel >> 3 must equal pal's 5-bit channel."""
    out = bytearray()
    for i in range(256):
        row = 256 + TEXT_FROM_OBJ[i] if i in TEXT_FROM_OBJ else i
        rgb = bf[BF_FADE_TABLE + 3 * row:BF_FADE_TABLE + 3 * row + 3]
        if [x >> 3 for x in rgb] != [_u16(pal, 2 * i) >> 5 * k & 31 for k in range(3)]:
            raise ValueError(f"BF fade table row {row} >> 3 is not BG palette entry {i}")
        out += rgb
    return bytes(out)


def card_blob(px: bytes, base: dict) -> bytes:
    """u32 tile bytes, 32x32 screenblock (u16 tile ids), the card's own 8bpp tiles (ids after the base tiles)."""
    extra, sb = {}, bytearray(0x800)
    for i, t in enumerate(_tiles_of(px)):
        tid = base[t] if t in base else len(base) + extra.setdefault(t, len(extra))
        struct.pack_into("<H", sb, 2 * (i // 30 * 32 + i % 30), tid)
    if not extra or len(base) + len(extra) > VRAM_TILES_MAX:
        raise ValueError(f"card tiles {len(base)} + {len(extra)}: none of its own, or past the screenblock")
    data = b"".join(extra)
    return struct.pack("<I", len(data)) + bytes(sb) + data


def _bit(data: bytes, n: int) -> int:
    return data[n >> 3] >> (n & 7) & 1


def chapter_for(image: bytes) -> tuple:
    """The CHAPTERS row the Thumb pick returns for a slot image from its story flags (save struct +0xB4); the
    map visited bits follow at +SLOT_VISITED (v8, VISITED rows)."""
    for num, title, flag in reversed(CHAPTERS):
        if flag is None or _bit(image, flag) and (num not in VISITED or _bit(image[SLOT_VISITED:], VISITED[num])):
            return num, title, flag
    raise ValueError("no row matches")


# ===== song port =====

def pattern_end(data: bytes, off: int, masks: bytes) -> int:
    """File offset after the pattern at off, read as the row decoder 0x08020820 reads it: byte 0 = rows; a row is
    events until 0; event = code << 4 | channel; code 0 = next byte is the mask, 1 = the channel's last mask, else
    masks[code - 2]; mask bits 0-2 = one byte each (note, instrument, volume), bit 3 = two bytes (effect, value)."""
    rows, i, kept = data[off], off + 1, [0] * 16
    for _ in range(rows):
        while data[i]:
            code, ch = data[i] >> 4, data[i] & 15
            i += 1
            if code == 0:
                kept[ch] = data[i]
                i += 1
            m = kept[ch] if code < 2 else masks[code - 2]
            i += (m & 1) + (m >> 1 & 1) + (m >> 2 & 1) + 2 * (m >> 3 & 1)
        i += 1
    return i


def song_events(data: bytes, off: int, masks: bytes) -> list:
    """(note, instrument, effect) of every event in the pattern at off (None where the mask has no field)."""
    rows, i, kept, out = data[off], off + 1, [0] * 16, []
    for _ in range(rows):
        while data[i]:
            code, ch = data[i] >> 4, data[i] & 15
            i += 1
            if code == 0:
                kept[ch] = data[i]
                i += 1
            m = kept[ch] if code < 2 else masks[code - 2]
            f = []
            for bit in range(3):
                f.append(data[i] if m >> bit & 1 else None)
                i += m >> bit & 1
            out.append((f[0], f[1], data[i] if m & 8 else None))
            i += 2 * (m >> 3 & 1)
        i += 1
    return out


def _bf_song() -> dict:
    """BF song 37 parts, checked: record, order bytes, patterns, mask table, used sample entries and data."""
    bf = bf_rom()
    rec_at = BF_MUSIC_TABLE - ROM_BASE + 20 * BF_SONG
    if bf[rec_at:rec_at + 20].hex() != BF_RECORD:
        raise ValueError(f"BF song {BF_SONG} record rom:0x{rec_at:X} is {bf[rec_at:rec_at + 20].hex()}")
    pats, ords, sdir, masks = (_u32(bf, rec_at + 4 * k) - ROM_BASE for k in range(4))
    n_dir = (masks - sdir) // 12                         # the directory ends where the mask table starts
    orders = bf[ords:bf.index(b"\xFF", ords) + 1]
    mask_table = bf[masks:masks + 16]
    patterns, used = [], set()
    for p in range(max(orders[:-1]) + 1):
        at = _u32(bf, pats + 4 * p) - ROM_BASE
        end = pattern_end(bf, at, mask_table)
        for note, ins, eff in song_events(bf, at, mask_table):
            if note is not None and note >= 120 and note != 0xFF:
                raise ValueError(f"BF pattern {p}: note {note} is past the 120-entry note table")
            if eff is not None and eff >= 32:
                raise ValueError(f"BF pattern {p}: effect {eff} is past the 32-entry effect table")
            if ins is not None:
                if ins >= n_dir:
                    raise ValueError(f"BF pattern {p}: instrument {ins} is past the {n_dir}-entry directory")
                used.add(ins)
        patterns.append(bf[at:end])
    entries = {i: bf[sdir + 12 * i:sdir + 12 * i + 12] for i in sorted(used)}
    samples = {}
    for i, e in entries.items():
        ptr, length = _u32(e, 0) - ROM_BASE, _u16(e, 8)
        samples[i] = bf[ptr:ptr + length + SAMPLE_TAIL]
    return {"record": bf[rec_at:rec_at + 20], "orders": orders, "masks": mask_table, "patterns": patterns,
            "entries": entries, "samples": samples, "dir_size": max(used) + 1, "bf_record": rec_at}


def song_blob(song: dict, base: int) -> tuple:
    """(bytes, {part: file offset}) of the ported song at file offset base. Order: record, pattern pointers,
    orders, mask table, directory, patterns, silent sample, samples."""
    at, parts = base + 20, {"record": base}
    for name, size in (("pointers", 4 * len(song["patterns"])), ("orders", len(song["orders"])),
                       ("masks", 16), ("directory", 12 * song["dir_size"])):
        at = (at + 3) & ~3
        parts[name] = at
        at += size
    parts["patterns"] = []
    for p in song["patterns"]:
        parts["patterns"].append(at)
        at += len(p)
    parts["silent"] = at
    at += 16
    parts["samples"] = {}
    for i, data in song["samples"].items():
        parts["samples"][i] = at
        at += len(data)
    out = bytearray(at - base)
    rec = bytearray(song["record"])
    for k, name in enumerate(("pointers", "orders", "directory", "masks")):
        struct.pack_into("<I", rec, 4 * k, ROM_BASE + parts[name])
    out[0:20] = rec                                      # +0x10 tempo 115, +0x11 speed 4 kept
    for k, p in enumerate(parts["patterns"]):
        struct.pack_into("<I", out, parts["pointers"] - base + 4 * k, ROM_BASE + p)
        out[p - base:p - base + len(song["patterns"][k])] = song["patterns"][k]
    out[parts["orders"] - base:parts["orders"] - base + len(song["orders"])] = song["orders"]
    out[parts["masks"] - base:parts["masks"] - base + 16] = song["masks"]
    for i in range(song["dir_size"]):
        e = bytearray(song["entries"].get(i, struct.pack("<IHHHH", 0, 0, 0, 16, SILENT_RATE)))
        struct.pack_into("<I", e, 0, ROM_BASE + parts["samples"].get(i, parts["silent"]))
        out[parts["directory"] - base + 12 * i:parts["directory"] - base + 12 * i + 12] = e
    for i, data in song["samples"].items():
        out[parts["samples"][i] - base:parts["samples"][i] - base + len(data)] = data
    return bytes(out), parts


def _check_chapters() -> None:
    nums = [n for n, _, _ in CHAPTERS]
    if nums != list(range(1, len(CHAPTERS) + 1)):
        raise ValueError(f"chapter numbers {nums} are not 1..N in order")
    flags = [f for _, _, f in CHAPTERS]
    if flags[0] is not None or any(f is None or not 0 <= f < 400 for f in flags[1:]):
        raise ValueError("row 1 starts from the new game (None); the others need a story flag 0-399")
    if flags[1:] != sorted(set(flags[1:])):
        raise ValueError(f"start flags {flags[1:]} do not rise")
    if LANDING_CARD in STORY or set(STORY) | {LANDING_CARD} != set(nums[1:]):
        raise ValueError(f"STORY cards {sorted(STORY)} and landing card {LANDING_CARD} are not chapters "
                         f"2..{len(CHAPTERS)}, each once")
    if len(VISITED) > 1 or not set(VISITED) <= set(nums[1:]) or not all(0 <= b < 297 for b in VISITED.values()):
        raise ValueError(f"VISITED {VISITED}: the pick code holds one row's map bit (0-296)")


# ===== story points (v5) =====

def story_ops(card: int) -> bytes:
    """Script bytes a story point gets: push N ; ext CARD_OP."""
    return push(card) + bytes([2, CARD_OP])


# ===== card 4 landing scene (v8) =====

def _pick(*cases: tuple, default: int) -> bytes:
    """Leave the next index: the first (leader, index) whose leader matches ext 11, else default (rom:0x3CDFD8)."""
    out = b""
    for leader, idx in cases:
        out += ext(11) + push(leader) + bytes([EQ, JZ, 3]) + push(idx) + bytes([END_OP])
    return out + push(default)


def facing_to(x: int, y: int, tx: int, ty: int) -> int:
    """The facing byte that points an actor at (x, y) towards (tx, ty): the longer axis wins. A tie raises, so a
    spot that leaves the direction open is a build error, not a guess (11:55 PM: face Piccolo)."""
    dx, dy = tx - x, ty - y
    if abs(dx) == abs(dy):
        raise ValueError(f"({x},{y}) to ({tx},{ty}) is diagonal: the facing is not decided")
    return (RIGHT if dx > 0 else LEFT) if abs(dx) > abs(dy) else (DOWN if dy > 0 else UP)


def spot_list(branch: str) -> list:
    """[(name, x, y, facing)] of the branch's five NPCs, plus ("player", LAND x, y, his facing). AT_PLAYER is
    worked out here, and a branch with no PLAYER_FACE row keeps the DOWN the arrival set under black."""
    out = [(n, x, y, facing_to(x, y, LAND[3], LAND[4]) if f is AT_PLAYER else f)
           for n, (x, y, f) in SPOTS[branch].items()]
    return out + [("player", LAND[3], LAND[4], PLAYER_FACE.get(branch, DOWN))]


def _guard() -> bytes:
    """Record 0: map 8,1 visited = the vanilla landing, then END; else fade, card 4, map load, record 1. v12:
    both arms land the player on LAND, so the two ext calls carry the same five values."""
    plain = ext(38, *LAND) + push(LANDING_END) + bytes([END_OP])
    first = ext(40, FADE) + story_ops(LANDING_CARD) + ext(39, *LAND)
    return code(1, ext(23, *LAND[:2]), bytes([JZ, len(plain)]), plain, first)


def _arrival(branch: str, nxt: int) -> bytes:
    """Under black: HUD off, camera, NPCs south of the view; fade in; one fly-in group; then every facing. The
    faces come after the flight because ext 54 leaves each actor facing the way it moved (bible PGS row)."""
    at = [a for a in spot_list(branch) if a[0] != "player"]
    spawn = b"".join(ext(51, ID[n], x, FROM_Y) for n, x, _, _ in at)
    fly = b"".join(ext(54, ID[n], x, y) for n, x, y, _ in at)
    face = b"".join(ext(55, ID[n], f) for n, _, _, f in at)
    if branch in PLAYER_FACE:                                  # else he keeps the DOWN set under black
        face += ext(55, 0, PLAYER_FACE[branch])
    return code(nxt, ext(86, 0), ext(55, 0, DOWN), ext(31, *CAMERA), spawn, ext(41, FADE), ext(46, FLY_SOUND),
                ext(63), fly, ext(64), face)


def _exit(branch: str) -> bytes:
    """One fly-off group to the north, remove the NPCs, the camera back on the player, HUD on."""
    at = SPOTS[branch]
    fly = b"".join(ext(112, ID[n], FLY_SOUND) + ext(54, ID[n], x, OFF_Y) for n, (x, _, _) in at.items())
    gone = b"".join(ext(52, ID[n]) for n in at)
    return code(LANDING_END, ext(63), fly, ext(64), gone, ext(33, 0), ext(86, 1))


def landing_records() -> dict:
    """{table index: record bytes}: 0 guard, 1 leader pick, 2-4 arrivals, 5-6 and 8-12 lines, 7 exit pick,
    13-15 exits; word LANDING_END is 0."""
    recs = {0: _guard(), 1: code(2, _pick((VEGETA, 4), (PICCOLO, 3), default=2)),
            2: _arrival("gohan", 5), 3: _arrival("piccolo", 5), 4: _arrival("vegeta", 8),
            7: code(13, _pick((PICCOLO, 14), default=13)),
            13: _exit("gohan"), 14: _exit("piccolo"), 15: _exit("vegeta")}
    for i, (nxt, portrait, line) in LINES.items():
        if not line.isascii():
            raise ValueError(f"line {i} is not ASCII")
        recs[i] = text(nxt, portrait, line)
    if sorted(recs) != list(range(LANDING_END)):
        raise ValueError(f"landing records {sorted(recs)} are not 0..{LANDING_END - 1}")
    return recs


def landing_blob(at: int) -> tuple:
    """(item, table, records) bytes for file offset at: the scene item (20 bytes), then the table (aligned),
    then the records."""
    recs = landing_records()
    table_at = at + 20
    rec_at, words, blob = table_at + 4 * (LANDING_END + 1), [], b""
    for i in range(LANDING_END):
        words.append(ROM_BASE + rec_at + len(blob))
        blob += recs[i]
    table = struct.pack(f"<{LANDING_END + 1}I", *words, 0)
    item = struct.pack("<I", SCENE_ITEM) + bytes.fromhex(LANDING_ITEM_BYTES)[4:16] + struct.pack("<I",
                                                                                                ROM_BASE + table_at)
    return item, table, blob


def record_ops(rom: bytes, rec: int) -> tuple:
    """(op starts, length) of a type 0 record: ops from +3 to the op 17 that no forward jump (op 18, 19) passes."""
    starts, o, reach = [], rec + 3, 0
    while True:
        e = _op_end(rom, o)
        starts.append(o)
        if rom[o] in (18, 19):
            reach = max(reach, e + rom[o + 1])
        if rom[o] == 17 and e > reach:
            return starts, e - rec
        o = e


def _story_word(rom: bytes, card: int) -> tuple:
    """(live table word, words that may also name the record): card 7 through the two type 5 words."""
    word = STORY[card][0]
    if word is not None:
        return word, {word}
    tables = {_u32(rom, w) for w in CHAMBER_TYPE5}
    if len(tables) != 1:
        raise ValueError(f"the chamber exit type 5 words name {sorted(map(hex, tables))}, not one table")
    word = tables.pop() - ROM_BASE
    return word, {word, CHAMBER_VANILLA}                 # the vanilla table is dead once piccolo_gi_scene copies it


def _aligned_words(rom: bytes, values: set) -> dict:
    """{value: [offsets]} of the aligned ROM words equal to each value."""
    out = {v: [] for v in values}
    for i, w in enumerate(memoryview(bytes(rom[:len(rom) & ~3])).cast("I")):
        if w in out:
            out[w].append(4 * i)
    return out


def _story_plan(rom: bytearray) -> dict:
    """{card: (word, record, copy bytes)}, every source checked."""
    plan, wants = {}, {}
    for card, (_, rec, length, sha, at, old) in STORY.items():
        word, allowed = _story_word(rom, card)
        _expect(rom, word, struct.pack("<I", rec + ROM_BASE))
        if hashlib.sha1(rom[rec:rec + length]).hexdigest() != sha or rom[rec + 2] != 0:
            raise ValueError(f"chapter {card} record rom:0x{rec:X} differs from the base bytes")
        if record_ops(rom, rec)[1] != length:
            raise ValueError(f"chapter {card} record rom:0x{rec:X} does not end at +0x{length:X}")
        plan[card] = (word, rec, relocate(rom, rec, length, {at: (old, story_ops(card).hex() + old)}))
        wants[card] = allowed
    found = _aligned_words(rom, {rec + ROM_BASE for _, rec, *_ in STORY.values()})
    for card, (word, rec, _) in plan.items():
        if not {word} <= set(found[rec + ROM_BASE]) <= wants[card]:
            raise ValueError(f"chapter {card} record rom:0x{rec:X} is named at {[hex(a) for a in found[rec + ROM_BASE]]}")
    return plan


def _ext_words(rom: bytearray, alloc) -> tuple:
    """(the 145 live ext op words, the ops whose word is not vanilla); such a word must sit inside an earlier
    module's site (relay_cooldown's ext 70)."""
    vanilla = LG_PATH.read_bytes()[EXT_TABLE:EXT_TABLE + 4 * EXT_OPS]
    if hashlib.sha1(vanilla).hexdigest() != EXT_TABLE_SHA1:
        raise ValueError(f"{LG_PATH.name}: ext table bytes differ from the base")
    sites = [site[:2] for _, site in _written(alloc.notes)]
    words, changed = [], []
    for k in range(EXT_OPS):
        a = EXT_TABLE + 4 * k
        if rom[a:a + 4] != vanilla[4 * k:4 * k + 4]:
            if not any(s <= a and a + 4 <= s + n for s, n in sites):
                raise ValueError(f"ext {k} word rom:0x{a:X} is not vanilla and no earlier module lists it")
            changed.append(k)
        words.append(_u32(rom, a))
    return words, changed


# ===== checks =====

def _check(rom: bytearray, alloc) -> None:
    if "chapter_cards" in alloc.notes:
        raise ValueError("chapter_cards already ran")
    _check_chapters()
    _expect(rom, HOOK, struct.pack("<I", (ORIG_CONTINUE - FS_VTABLE) & 0xFFFFFFFF))
    for addr, want in BODIES.items():
        _expect(rom, addr - ROM_BASE, bytes.fromhex(want))
    for k, w in enumerate(IMAGE_SLOTS):
        _expect(rom, IMAGE_VTABLE - ROM_BASE + 4 * k, struct.pack("<I", w))
    _expect(rom, PLAYER_WORD - ROM_BASE, struct.pack("<I", PLAYER))
    for p in EXT_POOLS:
        _expect(rom, p, struct.pack("<I", EXT_TABLE + ROM_BASE))
    _expect(rom, LANDING_REGION_WORD, struct.pack("<I", ROM_BASE + LANDING_ITEM))          # v8 landing sources
    _expect(rom, LANDING_ITEM, bytes.fromhex(LANDING_ITEM_BYTES))
    _expect(rom, LANDING_SCRIPT, bytes.fromhex(LANDING_SCRIPT_BYTES))
    if _u32(rom, LANDING_ITEM) != SCRIPT_ITEM or _u32(rom, LANDING_ITEM + 16) != ROM_BASE + LANDING_SCRIPT:
        raise ValueError("the landing item is not the script item that names the landing script")
    if _aligned_words(rom, {ROM_BASE + LANDING_ITEM})[ROM_BASE + LANDING_ITEM] != [LANDING_REGION_WORD]:
        raise ValueError(f"the landing item rom:0x{LANDING_ITEM:X} has a name besides its region word")
    mine = [(HOOK, 4, "file select word")] + [(p, 4, "ext table pool word") for p in EXT_POOLS]
    mine += [(LANDING_REGION_WORD, 4, "landing region word"), (LANDING_ITEM, 20, "landing item")]
    mine += [(_story_word(rom, c)[0], 4, f"chapter {c} table word") for c in STORY]
    mine += [(rec, length, f"chapter {c} record") for c, (_, rec, length, *_) in STORY.items()]
    for name, site in _written(alloc.notes):
        s, n = site[:2]
        for a, k, what in mine:
            if s < a + k and a < s + n:
                raise ValueError(f"{what} rom:0x{a:X} is also written by {name} ({site}): stop and report")


# ===== patch =====

def _pointer_words(rom: bytearray, alloc) -> list:
    """(offset, value) of the real pointer words earlier patches wrote (v3): aligned ROM-range words inside their
    "sites" below 8 MB (hooks, vtable and pool words in vanilla code), and every ROM-range pool word a Thumb
    `ldr rd,[pc,#imm]` (0x48xx) inside any of their sites loads. Packed data in the expansion area is not read as a
    pointer: beam_struggle keeps 0x08926D91 at rom:0x910C94, which refused v2 though no code loads it."""
    out = set()
    for _, site in _written(alloc.notes):
        s, n = site[:2]
        if s < 0x800000:
            for a in range(s & ~3, (s + n + 3) & ~3, 4):
                if 0x08000000 <= _u32(rom, a) < 0x0A000000:
                    out.add((a, _u32(rom, a)))
        a = (s + 1) & ~1
        half = memoryview(bytes(rom[a:(s + n) & ~1])).cast("H")   # host is little-endian
        for k, h in enumerate(half):
            if h & 0xF800 == 0x4800:
                pool = ((a + 2 * k + 4) & ~3) + 4 * (h & 0xFF)
                if pool + 4 <= len(rom) and 0x08000000 <= _u32(rom, pool) < 0x0A000000:
                    out.add((pool, _u32(rom, pool)))
    return sorted(out)


def _free_chunk(rom: bytearray, alloc, size: int, skipped: list) -> int:
    """A free code chunk that no ROM word names (rom_space rule); a named chunk stays unused, noted in skipped."""
    for _ in range(MAX_TRIES):
        at = alloc.alloc(size)
        if set(rom[at:at + size]) != {0xFF}:
            raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
        named = words_naming(rom, at + ROM_BASE, at + ROM_BASE + size, (CODE_REGION,))
        if not named:
            return at
        skipped.append((at, size, named))
    raise ValueError(f"no free chunk of 0x{size:X} bytes in {MAX_TRIES} tries")


def _layout(base: int, card_at: list, song_at: int, back_at: int, base_bytes: int, fade_at: int) -> tuple:
    """(blob, labels, offsets): code and pool, vtable, chapter table, for file offset base."""
    syms = dict(SYMS, LAST_ROW=len(CHAPTERS) - 1)
    for name, n in (("IN", FADE_IN), ("OUT", FADE_OUT)):
        syms[f"{name}_MUL"], syms[f"{name}_SHIFT"] = level_rule(n)
    for bit in VISITED.values():                         # one row (checked): its byte and bit past the flags
        syms.update(VISIT_BYTE=SLOT_VISITED + (bit >> 3), VISIT_LSL=31 - (bit & 7))
    code_len = len(assemble(CODE, ROM_BASE + base, syms)[0])
    vt = (base + code_len + 3) & ~3
    table = vt + 4 * len(IMAGE_SLOTS)
    syms.update(TABLE=ROM_BASE + table, TABLE_END=ROM_BASE + table + 8 * len(CHAPTERS), VTABLE=ROM_BASE + vt,
                SONG=ROM_BASE + song_at, BACKDROP=ROM_BASE + back_at, BASE_BYTES=base_bytes,
                VRAM_EXTRA=SYMS["VRAM"] + base_bytes, FADE_TABLE=ROM_BASE + fade_at)
    code, labels = assemble(CODE, ROM_BASE + base, syms)
    if len(code) != code_len:
        raise ValueError("code size changed with the symbol values")
    out = bytearray(b"\xFF" * (table + 8 * len(CHAPTERS) - base))
    out[:code_len] = code
    for k, w in enumerate(IMAGE_SLOTS):
        target = labels[NEW_SLOTS[4 * k]] | 1 if 4 * k in NEW_SLOTS else (w + IMAGE_VTABLE) & 0xFFFFFFFF
        struct.pack_into("<I", out, vt - base + 4 * k, (target - (ROM_BASE + vt)) & 0xFFFFFFFF)
    for i, (num, _, flag) in enumerate(CHAPTERS):
        f, kind = 0 if flag is None else flag, int(flag is None) | 2 * int(num in VISITED)
        struct.pack_into("<HBBI", out, table - base + 8 * i, f >> 3, f & 7, kind, ROM_BASE + card_at[i])
    return bytes(out), labels, {"vtable": vt, "table": table, "code_len": code_len}


def _data_chunk(rom: bytearray, alloc, size: int, pointer_words: list) -> int:
    """A free data chunk that no real pointer word an earlier patch wrote names (v3 rule)."""
    at = alloc.alloc(size)
    if set(rom[at:at + size]) != {0xFF}:
        raise ValueError(f"rom:0x{at:X} (0x{size:X} bytes) is not free")
    named = [hex(o) for o, w in pointer_words if ROM_BASE + at <= w < ROM_BASE + at + size]
    if named:
        raise ValueError(f"data chunk rom:0x{at:X} is named by pointer words at {named}: stop and report")
    return at


def apply(rom: bytearray, alloc) -> None:
    _check(rom, alloc)
    plan = _story_plan(rom)
    ext_words, changed = _ext_words(rom, alloc)
    bf = bf_rom()
    back, base_ids = backdrop_blob(bf)
    cards = [card_blob(render_card(bf, n, t), base_ids) for n, t, _ in CHAPTERS]
    base_bytes = len(back) - 0x200
    fade = fade_table(bf, back[:0x200])
    song = _bf_song()
    skipped = []
    pointer_words = _pointer_words(rom, alloc)
    song_size = len(song_blob(song, 0x800000)[0])
    copies = {c: data for c, (_, _, data) in plan.items()}
    sizes = [len(c) for c in cards] + [song_size, len(back), 4 * (CARD_OP + 1)] + [len(d) for d in copies.values()]
    landing_size = sum(map(len, landing_blob(0x800000)))
    sizes += [len(fade), landing_size]                   # v7 fade table, then the v8 landing scene
    data_at = [_data_chunk(rom, alloc, size, pointer_words) for size in sizes]
    card_at, (song_at, back_at, ext_at) = data_at[:len(cards)], data_at[len(cards):len(cards) + 3]
    copy_at = dict(zip(copies, data_at[len(cards) + 3:-2]))
    fade_at, land_at = data_at[-2:]
    landing = b"".join(landing_blob(land_at))
    if len(landing) != landing_size:
        raise ValueError("the landing scene size changed with its address")
    song_bytes, song_parts = song_blob(song, song_at)
    size = len(_layout(0x800000, card_at, song_at, back_at, base_bytes, fade_at)[0])
    at = _free_chunk(rom, alloc, size, skipped)
    blob, labels, offs = _layout(at, card_at, song_at, back_at, base_bytes, fade_at)
    if len(blob) != size:                                # pool padding depends on the address
        raise ValueError(f"chapter_cards laid out to 0x{len(blob):X} bytes, allocated 0x{size:X}")
    ext_copy = struct.pack(f"<{CARD_OP + 1}I", *ext_words, labels["cc_story"] | 1)   # word CARD_OP = the card op
    for a, c in zip(card_at, cards):                     # first write: every check has passed
        rom[a:a + len(c)] = c
    rom[song_at:song_at + song_size] = song_bytes
    rom[back_at:back_at + len(back)] = back
    for c, data in copies.items():
        rom[copy_at[c]:copy_at[c] + len(data)] = data
    rom[ext_at:ext_at + len(ext_copy)] = ext_copy
    rom[fade_at:fade_at + len(fade)] = fade
    rom[land_at:land_at + landing_size] = landing
    rom[at:at + size] = blob
    rom[LANDING_REGION_WORD:LANDING_REGION_WORD + 4] = struct.pack("<I", ROM_BASE + land_at)
    rom[HOOK:HOOK + 4] = struct.pack("<I", ((labels["cc_continue"] | 1) - FS_VTABLE) & 0xFFFFFFFF)
    for p in EXT_POOLS:
        rom[p:p + 4] = struct.pack("<I", ROM_BASE + ext_at)
    for c, (word, _, _) in plan.items():
        rom[word:word + 4] = struct.pack("<I", ROM_BASE + copy_at[c])
    alloc.notes["chapter_cards"] = {
        "block": at, "size": size, "code_len": offs["code_len"], "vtable": offs["vtable"], "table": offs["table"],
        "fade_table": fade_at, "landing": {"item": land_at, "table": land_at + 20, "records": land_at + 20 + 4 * (
            LANDING_END + 1), "size": landing_size, "region_word": LANDING_REGION_WORD},
        "ext_table": ext_at, "story": {c: {"word": w, "record": r, "copy": copy_at[c],
                                                      "length": len(copies[c])} for c, (w, r, _) in plan.items()},
        "ext_changed": changed,
        "cards": card_at, "card_sizes": [len(c) for c in cards], "labels": dict(labels), "hook": HOOK,
        "skipped": skipped, "song": song_parts, "song_size": song_size, "bf_record": song["bf_record"],
        "backdrop": back_at, "base_tiles": len(base_ids), "lines": [card_lines(bf, n, t) for n, t, _ in CHAPTERS],
        "sites": [(HOOK, 4, "file select vtable +0x2C (Continue)"),
                  (at, size, "chapter card code, vtable, table"),
                  (fade_at, len(fade), "BF fade table rows (v7 fade in)"),
                  (land_at, landing_size, "card 4 landing scene: scene item, table, records (v8)"),
                  (LANDING_REGION_WORD, 4, "world map region 11 item word (v8 landing scene)"),
                  (ext_at, len(ext_copy), f"ext op table copy (word {CARD_OP} = the card op)"),
                  (song_at, song_size, f"BF song {BF_SONG} port"),
                  (back_at, len(back), "BF card backdrop: BG palette, base tiles")]
        + [(a, len(c), f"chapter {i + 1} card") for i, (a, c) in enumerate(zip(card_at, cards))]
        + [(p, 4, "ext op table pool word") for p in EXT_POOLS]
        + [(EXT_TABLE, 4 * EXT_OPS, RETIRED)]
        + [s for c, (w, _, _) in plan.items()
           for s in ((w, 4, f"chapter {c} table word"), (copy_at[c], len(copies[c]), f"chapter {c} story record"))]}
