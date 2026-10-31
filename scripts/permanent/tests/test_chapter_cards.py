r"""
test_chapter_cards.py - Tests for patches.chapter_cards (trial 2026-10-25, v8): a chapter title card when a save is
                        continued from file select, on a new game and at each chapter's story point (a new ext op
                        in copied scene records), with Buu's Fury's timing, its ported song 37, its backdrop
                        (map 29, BG palette rom:0x5632C), its title font, (v7) its palette fades and (v8) the
                        card 4 landing scene on map 8,1 with Continue option c ((v9) on an open patch).

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_chapter_cards.py -v
Builds build_list_trial_chapters.txt in memory: "before" = the list up to chapter_cards (the main list, pinned to
r40 by SHA-1), "rom" = with it. The code is decoded with thumb_dis (never with the encoder) and run with
tests.test_ssj2.Cpu (plus mul and the I/O, palette and VRAM regions). Expected values are restated from
docs\tasks\2026-10-25-chapter-cards\chapter-cards-report.md, chapter-cards-trial-v5.md, chapter-cards-trial-v6.md,
the probe listings scripts\one-time\2026-10-25-chapter-cards\v5_records_probe.txt and v6_probe.txt, the v7 fade rules
of card-fade-report.md (option B, variant B8), the v8 card-4-scene-report.md and card-4-scene-build.md (my
words, c4s_draft.txt, c4b_probe.txt), the v9 card-4-scene-v9.md (c4v_patch.txt) and the base ROM bytes, never
imported from the module. Script records are walked with this file's own op-length rule (bible DS8 "Script grammar" row).
Picture hashes are pinned from scripts\one-time\2026-10-25-chapter-cards\v3_render_cards.py, which compares the
module's BF text with my screenshot (PIL stays out of these tests).
"""
import copy
import hashlib
import re
import struct
import unittest

import log2_build
from patches import chapter_cards
from rom.rom_space import Allocator
from tests.test_ssj2 import Cpu
from rom.thumb_dis import dis, listing

# ===== constants (report, base ROM reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_chapters.txt"
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"        # build_list.txt r40 (2026-10-30; r39 was aa51dc16)
HOOK, FS_VTABLE, VANILLA_CONTINUE = 0x23B38, 0x08023B0C, 0x0800180D          # file select vtable +0x2C
SLOT_VALID, ALLOC, FREE, SCENE_PUSH, MUSIC_PLAY = 0x080019F7, 0x0801F08D, 0x0801F111, 0x0801F2F5, 0x08020A4D
IMAGE_VTABLE = 0x080237C0
PLAYER = 0x030026C8
KEYS_NEW = 0x030022B0
BF_PATH = log2_build.ROOT / "data" / "roms" / "Dragon Ball Z - Buu's Fury (USA).gba"
BF_SONG37 = 0x083BB78C + 20 * 37                         # BF ext 35 table + 20 x song
BF_SONG37_RECORD = (0x083A618C, 0x083A5DFC, 0x0836D18C, 0x0836D540, 0x473)   # patterns, orders, dir, masks, 115/4
BF_SONG37_INSTRUMENTS = [7, 17, 18, 19, 22, 26, 29, 32, 43, 62]               # v2_song_decode.txt
BF_BG_PALETTE, BF_OBJ_PALETTE, BF_STRINGS = 0x5632C, 0x5652C, 0x6BCE8          # BF ROM offsets
BACKDROP_PX_SHA1 = "20b7eb0c4026d63265e2f0a81f237177fb9b4c50"   # map 29 render, matched to the screenshot
BF_CH2_PX_SHA1 = "722ee0a9dadf0127ffc76b54a9e610a10dbbd481"     # BF strings 1452/1453 at y 65/85 (8 band px off)
BF_LINE_WIDTHS = {"Chapter 2": 100, "Great Saiyaman": 164}        # sum (w + 1), BF glyph table 0x08753A20
WANT_LINES = {}                                                     # every one of my titles fits one line (9:14 PM)
WRAP_CASES = {"A Warning from the Future": ["A Warning from", "the Future"],     # earlier titles, too wide: wrap
              "Birth of a Super Namekian": ["Birth of a", "Super Namekian"]}
SCRIPT_REGION = (0x3B5000, 0x420000)
# v5 brief table (final, 2026-10-29), card 5 flag from the v6 brief (final, 2026-10-30): (number, title, Continue flag)
WANT_CHAPTERS = [(1, "The Mysterious Youth", None), (2, "Preparation", 26), (3, "The Androids Appear", 68),
                 (4, "Into Gero's Lab", 86), (5, "A New Horror", 129), (6, "Perfection", 148),
                 (7, "The Cell Games", 158), (8, "The Champion's Hour", 195)]
SET_SITES = {26: 0x3BFDBF, 68: 0x3B8571, 86: 0x3D542A, 129: 0x3DF28F, 148: 0x3E605A,
             158: 0x3DBDAA, 195: 0x3EC6A2}                          # `00 NN 02 1B` (push NN ; ext 27 SET)
# Story points (v5_records_probe.txt; card 5 v6_probe.txt): card: (record, length, table word in r39, op start the
# card goes before). Card 4 left the post-20 record in v8 (V7_CARD4) for the landing scene.
STORY_WANT = {2: (0x3BFDB4, 0x27, 0x3BFF38, 0x3BFDBF), 3: (0x3B8566, 0xA6, 0x3B88BC, 0x3B8571),
              5: (0x3DF28C, 0x82, 0x3DF764, 0x3DF297),
              6: (0x3E5ED4, 0x47, 0x3E61CC, 0x3E5EDB), 7: (0x3DB4B0, 0x20, 0x89B158, 0x3DB4BF),
              8: (0x3EC678, 0x4D, 0x3EC81C, 0x3EC683)}
FADE_BEFORE = {2: (0x3BFDBB, 120), 3: (0x3B856D, 240), 5: (0x3DF293, 90), 6: (0x3E5ED7, 180), 7: (0x3DB4BB, 240),
               8: (0x3EC67F, 240)}                                  # `00 VV 02 28` (push VV ; ext 40 fade out)
# Real word 0 of each story table and the word that names it (v6_probe.txt; the word before word 0 can be a stray
# small word, bible CH6 trap row). Card 7: the r39 chamber exit copy, named by the two type 5 words.
TABLE0 = {2: (0x3BFDDC, 0x3F1E80), 3: (0x3B88A0, 0x3EDD64), 4: (0x3D5524, 0x3FD7A4), 5: (0x3DF720, 0x404478),
          6: (0x3E6078, 0x4066E0), 7: (0x89B158, 0x3CF7E4), 8: (0x3EC758, 0x4090F4)}
V5_CARD5 = (0x3D9864, 0x30, 0x3D9968)                                # v5 card 5 point (flag 127 fade): vanilla in v6
A19_TABLE, A19_RECORDS = (0x3D40C8, 0xA8), (0x3D3810, 0x8B8)        # Android 19 table (vegeta_19_reveal), 42 words
CARD_OP, EXT_TABLE, EXT_POOLS = 145, 0x3B5D28, (0x921C, 0x92DC)      # bible DS8: 145 code words, two names
CHAMBER_VANILLA, CHAMBER_TYPE5 = 0x3DBDD4, (0x3CF7E4, 0x3D1530)
V7_CARD4 = (0x3D540A, 0xFF, 0x3D55DC)                               # post-20 record, length, word: vanilla in v8
VISITED_AT, BIT_8_1 = 0xE7 - 0xB4, 211          # log2_save O_VISITED - O_STORY; map 8,1 bit (c4b_probe.txt section 4)
# v8 landing (bible CH8 rows, c4b_probe.txt section 1): world map 6,99 region 11 = {cond 86 set, item}
LANDING_REGION_WORD, LANDING_ITEM, LANDING_SCRIPT = 0x3FBE54, 0x3FBC5C, 0x3FBC50
LANDING_ITEM_HEX = "c3c2000839d80008000ae803710a610450bc3f08"     # script item, A-press, rect, script
LANDING_SCRIPT_HEX = "1d0510020284208200022611"                   # push 8,1,1,272,128 ; ext 38 ; end
SCENE_ITEM, SCENE_VTABLE, ITEM_INIT = 0x0800D7E1, 0x08023E44, 0x08004FF9   # scene item factory (map 9,6 0x404468)
CARD_POINTS = {2, 3, 5, 6, 7, 8}                # chapters with a story point; 4 plays in the landing scene
# Landing record 0, restated (card-4-scene-build.md, v12 card-4-scene-v12-spec.md): next 1; push 8,1 ; ext 23
# (visited) ; jz +14 ; [visited: push 8,1,1,272,128 ; ext 38 ; push 16 ; end] [first: push 60 ; ext 40 ; push 4 ;
# ext 145 ; push 8,1,1,272,128 ; ext 39 ; end]. v12 lands the first visit on the vanilla spot, so the two pushes
# are the same bytes. The compact push is `1d <count>` then a zigzag varint a value (scene_lib.zigzag): u = v * 2
# for v >= 0 and (-v) * 2 + 1 for v < 0, then 7 bits a byte, most significant group first, every group but the
# last carrying 0x80. So 272 gives u 544 = 84 20 and 128 gives u 256 = 82 00. The jz span covers the visited arm
# only, which this change does not touch, so it stays 14.
REC0_HEX = ("010000" "1d021002" "0217" "130e" "1d0510020284208200" "0226" "0010" "11"
            "003c" "0228" "0004" "0291" "1d0510020284208200" "0227" "11")
# v12 groups (c4y_areas.txt, c4y_plan.txt and c4y_plan_<leader>.png in scripts\one-time\2026-10-31-card-4-v12\):
# groups with their own facings, inside the one clearing that holds the vanilla landing (x 176-308, y 84-124).
# The player lands on the vanilla LAND spot in every branch. Spawn y 260 and fly-off y -40 are off the view at
# camera (137, 41). Map 8,1 collision = layout 0x0858CB30 +0x34 frame 0x0858C0E4 (bible CSV row: 1 bit per 8x8
# cell, 32 bytes a row, set = open); exit region = region 0 rect, save point = region 1.
PLAYER_SPOT, FROM_Y, OFF_Y, CAMERA = (272, 128), 260, -40, (137, 41, 255)
COLLISION_8_1, LAYOUT_8_1, FLIGHT_PAD = 0x0858C0E4, 0x0858CB30, (249, 89, 296, 144)
CLAMP = (137, 41)                                   # layout +8/+0xA: the largest camera top-left on this map
SAVE_RECT, NEAR, APART = (56, 48, 105, 97), 32, 40
# The dialog box starts at screen row 88, measured on a real frame (c4y_textbox.txt). v10 and v11 kept every NPC's
# feet at screen row 84 or above, which lets the bottom 4 px of his 16x32 frame go behind the box. v12 keeps that
# number and reads it as a screen row, so the world row it stands for follows the camera.
BOX_TOP, SOUTH_SCREEN = 88, 84
SOUTH_LIMIT = CAMERA[1] + SOUTH_SCREEN              # the world row an NPC may not pass: 125
# The player is the one deliberate exception, and it is forced. The vanilla landing is y 128 and the camera y
# clamp is 41, so his feet sit at screen row 87 whatever camera the scene sets. PLAYER_EXCEPTION pins that, and
# PLAYER_CLOSED pins the two closed cells of the rock above the landing, so neither exception can grow.
PLAYER_EXCEPTION, PLAYER_CLOSED = 87, ((272, 120), (280, 120))
# Save point clearance (11:55 PM: they "stand too close to the save point"). The drawn frame is 16x32 at
# (x, y - 24) (bible CJ3 OAM rows). Every actor of the Vegeta and Piccolo branches keeps CLEAR px of floor between
# that frame and the rect, or POCKET_CLEAR when he stands wholly west of it. v12 moves the whole scene away from
# the rect, so the worst margin is SAVE_WORST px and the pocket rule binds nobody.
SPRITE, CLEAR, POCKET_CLEAR, SAVE_WORST = (0, 16, -24, 8), 8, 0, 78
MARGIN_BRANCHES = ("Piccolo", "Vegeta")
BG1_LAYER, MAP_8_1 = 0x18, (376, 200)           # layout +0x18 = BG1, the canopies drawn over the actors
DOWN, UP, LEFT, RIGHT = 0, 1, 2, 3              # actor facing byte (bible PGS and CJ2 rows)
LANDING_WORDS = 17                              # records 0-15, word 16 = 0 (END)
LEADERS = {0: "Gohan", 1: "Piccolo", 2: "Vegeta"}
NPC = {"Gohan": 53, "Piccolo": 103, "Vegeta": 3, "Krillin": 76, "Tien": 121, "Trunks": 128}
ROWS = {"Gohan": ["Krillin", "Tien", "Trunks", "Vegeta", "Piccolo"],      # who flies in, per leader (v8 me)
        "Piccolo": ["Krillin", "Trunks", "Vegeta", "Gohan", "Tien"],
        "Vegeta": ["Krillin", "Tien", "Gohan", "Piccolo", "Trunks"]}
# The v12 spots, restated here and not imported: the module must build exactly these. Order = the op order. The
# facings are the resolved bytes, including the ones the module works out from the spot (AT_PLAYER), so this table
# pins the result of that rule and not the rule itself.
SPOTS = {"Gohan": {"Krillin": (264, 84, LEFT), "Tien": (232, 84, RIGHT), "Piccolo": (248, 92, UP),
                   "Trunks": (176, 100, RIGHT), "Vegeta": (192, 100, LEFT)},
         "Piccolo": {"Krillin": (248, 124, RIGHT), "Tien": (296, 120, LEFT), "Gohan": (184, 100, UP),
                     "Trunks": (236, 84, RIGHT), "Vegeta": (256, 84, LEFT)},
         "Vegeta": {"Krillin": (264, 84, LEFT), "Tien": (232, 84, RIGHT), "Piccolo": (248, 92, UP),
                    "Gohan": (184, 100, UP), "Trunks": (296, 120, LEFT)}}
# The leader's own facing. Gohan has no row: he keeps the DOWN the arrival sets under black, so he never turns on
# screen (11:55 PM "just leave it that way").
PLAYER_FACE = {"Piccolo": UP, "Vegeta": RIGHT}
# Who looks at the player because of where he stands, not because a byte was typed in (11:55 PM: Tien and
# Krillin face Piccolo). The expected byte is worked out here from the restated spots, by this file's own rule.
LOOKS_AT_PLAYER = {"Piccolo": ["Krillin", "Tien"], "Vegeta": ["Trunks"]}
FACES_NORTH = {"Piccolo": ["Gohan"], "Vegeta": ["Gohan"]}      # me: Gohan lands facing up, he flew from below
GROUPS = {"Gohan": {"top": ["Tien", "Piccolo", "Krillin"], "farleft": ["Trunks", "Vegeta"], "landing": ["player"]},
          "Piccolo": {"top": ["Trunks", "Vegeta"], "farleft": ["Gohan"],
                      "landing": ["Krillin", "Tien", "player"]},
          "Vegeta": {"top": ["Tien", "Piccolo", "Krillin"], "farleft": ["Gohan"],
                     "landing": ["Trunks", "player"]}}
# My words (card-4-scene-study.md, 6:45-6:59 PM; "lets" -> "let's"), one inner list per box
SPEECH_GP = [(3, ["Now we better get moving, we don't have much time!"]),
             (95, ["Okay, let's do it.", "I'll head a little further north to see what I find out there."])]
SPEECH_V = [(4, ["Would you stop following me, boy?", "You're getting on my nerves!"]),
            (98, ["Sorry, but there's no way I am planning to let you fight the androids on your own!"]),
            (4, ["And just what are you planning to do to stop me?",
                 "It's going to take more than that little sword of yours to stand in my way!"]),
            (98, ["How many times do I have to tell you before it sinks into your thick skull?",
                  "Never underestimate the power of the androids!"]),
            (4, ["Hah!", "And never underestimate the power of a real super saiyan who loves to take on a challenge!",
                 "Well, if you're going to stay, you can at least help me find Dr. Gero's lab!"])]
DIALOG_FONT, DIALOG_WIDTH, BOX_LINES = 0x2CC64, 0x90, 4    # bible C4S: wrap past 144 px, 4 lines a box
EXACT_144 = {"to see what I find out there.", "saiyan who loves to take on", "Well, if you're going to stay,"}
OP2 = 0x08008F8E                                                    # the plain ext call (bible DS8)
FADE_IN, WAIT, FADE_OUT = 100, 250, 100                  # BF card script: ext 121 100, ext 136 250, ext 120 100
OBJ, FS_OBJ, STACK, RET = 0x02000100, 0x02001000, 0x03007E00, 0x08000001
DISPCNT, BG3CNT, BLDCNT, BLDALPHA = 0x04000000, 0x0400000E, 0x04000050, 0x04000052
FILE_SELECT_REGS = [(DISPCNT, 0x1E40), (BG3CNT, 0x1F82), (BLDCNT, 0x00C4), (BLDALPHA, 0x0A06)]   # 0x1E40: 0x080013E4
# v7 fades (card-fade-report.md): BF ext 121 in = fade table row x L >> 11, L = (f << 8) / 100; BF ext 120 out =
# 5-bit channel x L >> 8, L = 256 - (k << 8) / 100. Table rom:0x701B0: RGB888, BG rows 0-255, then OBJ rows 256-511
BF_FADE_TABLE = 0x701B0
TEXT_FROM_OBJ = {247: 1, 248: 2}                         # card text entries: BF OBJ bank 0 entries 1 and 2
BF_STEPS = {"in": (97, 1), "out": (94, 1)}               # BF: frames with a change (of 100), largest jump (report)

_CACHE = {}
_FADE = {}                                               # one v7 tick run, shared by the fade tests


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def padded() -> bytearray:
    base = log2_build.BASE.read_bytes()
    return bytearray(base) + b"\xFF" * (log2_build.ROM_SIZE - len(base))


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("chapter_cards")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, names[i:])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["chapter_cards"])
    return _CACHE


def flags_of(*flags, visited=()) -> bytes:
    """Slot image bytes from +0xB4: story flags (50 bytes), then the map visited bits at +0x33 (save +0xE7)."""
    out = bytearray(0x60)
    for f in flags:
        out[f >> 3] |= 1 << (f & 7)
    for v in visited:
        out[VISITED_AT + (v >> 3)] |= 1 << (v & 7)
    return bytes(out)


def card_palette(bf: bytes) -> bytes:
    """The card BG palette: BF rom:0x5632C, entries 247 and 248 from BF OBJ bank 0 entries 1 and 2."""
    pal = bytearray(bf[BF_BG_PALETTE:BF_BG_PALETTE + 0x200])
    for i, e in TEXT_FROM_OBJ.items():
        pal[2 * i:2 * i + 2] = bf[BF_OBJ_PALETTE + 2 * e:BF_OBJ_PALETTE + 2 * e + 2]
    return bytes(pal)


def channels(pal: bytes) -> list:
    """(r, g, b) 5-bit channels of 256 palette words (bit 15 dropped)."""
    return [(v & 31, v >> 5 & 31, v >> 10 & 31) for v in struct.unpack("<256H", pal)]


def fade_rows(bf: bytes) -> list:
    """BF fade table rows for BG entries 0-255; 247 and 248 take OBJ rows 256 + 1 and 256 + 2 (report, B8)."""
    rows = [256 + TEXT_FROM_OBJ[i] if i in TEXT_FROM_OBJ else i for i in range(256)]
    return [tuple(bf[BF_FADE_TABLE + 3 * r:BF_FADE_TABLE + 3 * r + 3]) for r in rows]


def steps(frames: list, start: list, entries: list) -> tuple:
    """(frames on which an entry changes, largest channel jump) over the given entries."""
    prev, changed, jump = [start[i] for i in entries], 0, 0
    for fr in frames:
        cur = [fr[i] for i in entries]
        d = max(abs(a - b) for p, q in zip(prev, cur) for a, b in zip(p, q))
        changed, jump, prev = changed + (d > 0), max(jump, d), cur
    return changed, jump


class Gba(Cpu):
    """Cpu with mul, the I/O, palette and VRAM regions, and a decode cache (speed only: the same thumb_dis text)."""

    def __init__(self, rom: bytes):
        super().__init__(rom)
        self.ram.update({0x04: bytearray(0x400), 0x05: bytearray(0x400), 0x06: bytearray(0x18000)})
        self.texts = {}

    def run(self, addr: int, stops: dict, limit: int = 400) -> str:
        pc = addr & ~1
        for _ in range(limit):
            if pc in stops:
                if not callable(stops[pc]):
                    return stops[pc]
                self.r[0] = stops[pc](self) & 0xFFFFFFFF
                pc = self.r[14] & ~1
                continue
            if pc not in self.texts:
                self.texts[pc] = dis(self.rom, pc)
            text, size = self.texts[pc]
            pc = self._step(pc + size, text)
        raise AssertionError("no exit within the step limit")

    def _step(self, nxt: int, text: str) -> int:
        m = re.fullmatch(r"(mul|lsl|lsr|and) (r\d),(r\d)", text)    # register forms (ext 23's 0x080041EA-EC)
        if m:
            d, s = int(m.group(2)[1:]), int(m.group(3)[1:])
            x, y = self.r[d], self.r[s]
            v = {"mul": x * y, "lsl": x << y if y < 32 else 0, "lsr": x >> y, "and": x & y}[m.group(1)]
            self.r[d] = self._nz(v & 0xFFFFFFFF)
            return nxt
        return super()._step(nxt, text)

    def call(self, addr: int, r0: int, stops: dict = None, limit: int = 400) -> str:
        self.r[0], self.r[13], self.r[14] = r0, STACK, RET
        return self.run(addr, {**(stops or {}), RET & ~1: "done"}, limit)


# ===== list, source checks, second run =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_main_list_plus_the_trial_line(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        if "chapter_cards" in dev:
            self.skipTest("approved: the line is in build_list_core.txt, so build_list_trial_chapters.txt is retired")
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["chapter_cards"])

    def test_before_is_r40(self):
        self.assertEqual(hashlib.sha1(built()["before"]).hexdigest(), R40_SHA1)

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["chapter_cards"] = {}
        with self.assertRaises(ValueError):
            chapter_cards.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                          # the hook word is no longer vanilla either
        with self.assertRaises(ValueError):
            chapter_cards.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        offs = (HOOK, HOOK + 3, 0x180C, 0x181B, 0x19F6, 0x1A0B, 0x1F2F4, 0x1F08C, 0x1F110, 0x20A4C,
                IMAGE_VTABLE - ROM_BASE + 0xC, IMAGE_VTABLE - ROM_BASE + 0x2F, 0x1D4EF8,
                0x20820, 0x2085F, 0x1FE72, 0x1FE89, 0x9CBA,
                0x921C, 0x92DF, 0x8F9B,                                            # v5: pools, op 2
                EXT_TABLE + 4 * 33, CHAMBER_TYPE5[1],                              # a vanilla ext word; type 5 word
                LANDING_REGION_WORD, LANDING_REGION_WORD + 3, LANDING_ITEM, LANDING_ITEM + 19,   # v8 landing
                LANDING_SCRIPT, LANDING_SCRIPT + 11, 0xD7E0, 0xD80F, 0xD7A0, 0x9628, 0x9647)
        offs += tuple(rec + k for rec, length, _, _ in STORY_WANT.values() for k in (2, length - 1))
        offs += tuple(w for _, _, w, _ in STORY_WANT.values() if w < 0x800000)
        for off in offs:
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                chapter_cards.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_the_hook_word_refuses(self):
        for site in ((HOOK + 2, 1, "other"), HOOK + 3):      # triple shape and bare-offset shape
            rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
            alloc.notes["other_module"] = {"sites": [site]}
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(site)):
                chapter_cards.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_bad_chapter_table_refuses(self):
        good = chapter_cards.CHAPTERS
        bad_tables = ([(1, "A", 5)] + good[1:],                       # row 1 must be the new game
                      good[:2] + [(3, "B", 20)] + good[3:],           # flags must rise (row 2 is 26)
                      good[:2] + [(4, "B", 90)] + good[3:])           # numbers 1..N
        try:
            for t in bad_tables:
                chapter_cards.CHAPTERS = t
                rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
                with self.assertRaises(ValueError):
                    chapter_cards.apply(rom, alloc)
        finally:
            chapter_cards.CHAPTERS = good

    def test_padded_base_gets_the_same_code(self):
        rom, alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        chapter_cards.apply(rom, alloc)
        n = alloc.notes["chapter_cards"]
        self.assertEqual(u32(rom, HOOK), (n["labels"]["cc_continue"] + 1 - FS_VTABLE) & 0xFFFFFFFF)
        self.assertEqual(len(n["cards"]), len(WANT_CHAPTERS))


# ===== chapter table and story flags =====

class ChapterTests(unittest.TestCase):
    def test_table_is_the_report_table(self):
        self.assertEqual(chapter_cards.CHAPTERS, WANT_CHAPTERS)

    def test_lines_fit_the_screen_with_their_outline(self):
        bf, n = chapter_cards.bf_rom(), built()["notes"]
        for (num, title, _), lines in zip(WANT_CHAPTERS, n["lines"]):
            self.assertTrue(title.isascii(), title)
            self.assertEqual(lines, WANT_LINES.get(num, [f"Chapter {num}", title]))
            for text in lines:
                w = chapter_cards.text_width(bf, text)
                pen = 120 - (w + 1) // 2                        # BF 0x0802BECC: centred on x 120
                self.assertTrue(pen - 1 >= 0 and pen + w - 1 <= 239, f"{text!r} {w} px")

    def test_wrap_keeps_the_widest_line_narrowest(self):
        bf = chapter_cards.bf_rom()
        for title, lines in WRAP_CASES.items():
            self.assertGreater(chapter_cards.text_width(bf, title), 238, title)   # too wide on one line
            self.assertEqual(chapter_cards.card_lines(bf, 5, title), ["Chapter 5"] + lines)
            words = title.split(" ")
            best = min(max(chapter_cards.text_width(bf, " ".join(words[:k])),
                           chapter_cards.text_width(bf, " ".join(words[k:]))) for k in range(1, len(words)))
            self.assertEqual(max(chapter_cards.text_width(bf, t) for t in lines), best)

    def test_each_start_flag_has_one_set_site_and_no_clear_site(self):
        base = log2_build.BASE.read_bytes()
        lo, hi = SCRIPT_REGION
        for flag, site in SET_SITES.items():
            sets = [m.start() for m in re.finditer(re.escape(bytes([0, flag, 2, 0x1B])), base[lo:hi])]
            clrs = [m.start() for m in re.finditer(re.escape(bytes([0, flag, 2, 0x1C])), base[lo:hi])]
            self.assertEqual([lo + s for s in sets], [site], f"flag {flag}")
            self.assertEqual(clrs, [], f"flag {flag}")

    def test_chapter_3_start_is_the_time_skip(self):
        base = log2_build.BASE.read_bytes()
        # music 25 ; fade out 240 ; SET 68, then "Three years later..." (rom:0x3B8569)
        self.assertEqual(base[0x3B8569:0x3B8575].hex(), "00190231" + "00f00228" + "0044021b")

    def test_eight_rows_with_rising_flags(self):
        flags = [f for _, _, f in chapter_cards.CHAPTERS]
        self.assertEqual(len(chapter_cards.CHAPTERS), 8)
        self.assertEqual([n for n, _, _ in chapter_cards.CHAPTERS], list(range(1, 9)))
        self.assertIsNone(flags[0])
        self.assertTrue(all(a < b for a, b in zip(flags[1:], flags[2:])), flags)

    def test_stored_table_rows(self):
        b = built()
        rom, n = b["rom"], b["notes"]
        for i, (num, _, flag) in enumerate(WANT_CHAPTERS):
            f = 0 if flag is None else flag
            kind = int(flag is None) | (2 if num == 4 else 0)            # v8 bit 1: card 4 also needs bit 211
            row = struct.unpack_from("<HBBI", rom, n["table"] + 8 * i)
            self.assertEqual(row, (f >> 3, f & 7, kind, ROM_BASE + n["cards"][i]))


# ===== code =====

class CodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.lab = cls.n["labels"]

    def test_hook_word_names_the_wrapper(self):
        self.assertEqual(u32(self.before, HOOK), (VANILLA_CONTINUE - FS_VTABLE) & 0xFFFFFFFF)
        self.assertEqual((u32(self.rom, HOOK) + FS_VTABLE) & 0xFFFFFFFF, self.lab["cc_continue"] | 1)
        self.assertEqual(self.n["block"] % 4, 0)

    def test_vanilla_continue_has_no_other_name(self):
        words = memoryview(self.before[: len(self.before) & ~3]).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(words) if w in (VANILLA_CONTINUE, VANILLA_CONTINUE - 1)], [])
        rel = [(v, k) for v in range(0, 0x60000, 4) for k in range(0, 0x40, 4)
               if v + k + 4 <= 0x60000 and (u32(self.before, v + k) + ROM_BASE + v) & 0xFFFFFFFF == VANILLA_CONTINUE]
        self.assertEqual(rel, [(FS_VTABLE - ROM_BASE, 0x2C)])          # one vtable slot (slots 0-15) names it

    def test_vanilla_continue_copies_the_slot_image_the_wrapper_reads(self):
        texts = [t for _, t in listing(self.before, 0x08001844, 9)]        # 0x164 bytes from obj+0x14+0x164 x slot
        self.assertEqual(texts, ["mov r3,#0xff", "ldr r0,[r4,#0x10]", "add r3,#0x65", "mul r0,r3", "add r1,r0,r7",
                                 "ldr r0,[r5,#0xc]", "add r2,r3,#0", "bl 0x8021ea8", "ldr r0,[r5,#0xc]"])
        self.assertEqual([t for _, t in listing(self.before, 0x08001834, 2)], ["add r0,r4,#0", "add r0,#0x14"])

    def test_new_keys_are_inverted_keyinput(self):
        texts = [t for _, t in listing(self.before, 0x0801EEFE, 12)]       # input_read: +0x14 = pressed & changed
        self.assertEqual(texts, ["ldr r1,=0x04000120", "ldrh r4,[r0,#0x12]", "ldrh r1,[r1,#0x10]", "add r2,r4,#0",
                                 "mvn r1,r1", "lsl r1,r1,#16", "lsr r1,r1,#16", "eor r2,r1", "add r3,r1,#0",
                                 "and r3,r2", "and r4,r2", "strh r3,[r0,#0x14]"])
        self.assertEqual([t for _, t in listing(self.before, 0x0801F2B6, 2)], ["ldr r0,[r4,#0x8]", "bl 0x801eefc"])
        self.assertEqual(u32(self.before, 0x7FBDAC + 8) + 0x14, KEYS_NEW)  # frame_loop r4 = 0x087FBDAC

    def test_card_vtable(self):
        vt = self.n["vtable"]
        new = {0x4: "card_enter", 0x8: "card_leave", 0x14: "card_tick"}
        for k in range(12):
            target = (u32(self.rom, vt + 4 * k) + ROM_BASE + vt) & 0xFFFFFFFF
            image = (u32(self.rom, IMAGE_VTABLE - ROM_BASE + 4 * k) + IMAGE_VTABLE) & 0xFFFFFFFF
            self.assertEqual(target, self.lab[new[4 * k]] | 1 if 4 * k in new else image, f"+0x{4 * k:X}")
        self.assertEqual((u32(self.rom, IMAGE_VTABLE - ROM_BASE + 0xC) + IMAGE_VTABLE) & 0xFFFFFFFF, 0x08026511)
        self.assertEqual(self.rom[0x26510:0x26512].hex(), "7047")          # update +0xC is bx lr

    def test_wrapper_decodes_to_the_design(self):
        texts = [t for _, t in listing(self.rom, self.lab["cc_continue"], 12)]
        self.assertEqual(texts[:5], ["push {r4,r5,lr}", "add r4,r0,#0", "ldr r5,[r4,#0x10]", "cmp r5,#0x3",
                                     f"beq {self.lab['cc_orig']:#x}"])
        tail = [t for _, t in listing(self.rom, self.lab["cc_orig"], 5)]
        self.assertEqual(tail[:2], ["add r0,r4,#0", "ldr r3,=0x0800180d"])
        self.assertEqual(tail[3:5], ["pop {r4,r5,pc}", "bx r3"])

    def test_main_to_new_diff_is_the_declared_sites(self):
        chunks = [c for c in range(0, len(self.rom), 0x10000) if self.rom[c:c + 0x10000] != self.before[c:c + 0x10000]]
        changed = [i for c in chunks for i in range(c, c + 0x10000) if self.rom[i] != self.before[i]]
        sites = [(s, n) for s, n, _ in self.n["sites"]]
        retired = [(s, n) for s, n, name in self.n["sites"] if "retired" in name]
        self.assertEqual(retired, [(EXT_TABLE, 4 * CARD_OP)])
        self.assertEqual([i for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        words = {HOOK, LANDING_REGION_WORD} | set(EXT_POOLS) | {w for _, _, w, _ in STORY_WANT.values()}
        for s, n in sites:
            if (s, n) in retired:                                   # listed so a later writer refuses; unchanged
                self.assertEqual(self.rom[s:s + n], self.before[s:s + n])
                continue
            self.assertTrue(any(s <= i < s + n for i in changed), f"rom:0x{s:X}")
            if s in words:
                self.assertEqual(n, 4)
            else:
                self.assertEqual(set(self.before[s:s + n]), {0xFF}, f"rom:0x{s:X}")
                self.assertGreaterEqual(s, log2_build.EXPANSION[0][0])

    def test_new_space_was_free_and_only_the_hook_names_the_code(self):
        lo, hi = ROM_BASE + self.n["block"], ROM_BASE + self.n["block"] + self.n["size"]
        words = memoryview(self.before[: len(self.before) & ~3]).cast("I")
        named = [4 * i for i, w in enumerate(words) if lo <= w < hi]
        self.assertEqual(named, [])


# ===== interpreter runs =====

class RunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.n = b["rom"], b["notes"]
        cls.lab = cls.n["labels"]

    def pick(self, flag_bytes: bytes) -> int:
        cpu = Gba(self.rom)
        cpu.ram[0x02][0x200:0x200 + len(flag_bytes)] = flag_bytes
        self.assertEqual(cpu.call(self.lab["cc_pick"], 0x02000200), "done")
        return cpu.r[0]

    def test_pick_returns_the_last_set_chapter(self):
        cards = [ROM_BASE + a for a in self.n["cards"]]
        v = (BIT_8_1,)
        cases = [((), (), 1), ((26,), (), 2), ((26, 68), (), 3), ((26, 68, 86), v, 4),
                 ((26, 68, 86, 125, 127), v, 4), ((26, 68, 86, 125, 127, 129), v, 5),
                 ((26, 68, 86, 125, 127, 129, 148), (), 6), ((26, 68, 86, 127, 148, 154, 158, 191), v, 7),
                 ((26, 68, 86, 127, 148, 158, 191, 195), v, 8), ((195,), (), 8), ((25, 27, 125, 154), v, 1),
                 ((26, 68, 86, 125, 126, 127, 128, 129, 130, 148, 149, 150, 151, 154, 156, 157), (), 6)]
        for flags, visited, chapter in cases:
            fb = flags_of(*flags, visited=visited)
            self.assertEqual(self.pick(fb), cards[chapter - 1], f"{flags}")
            self.assertEqual(chapter_cards.chapter_for(fb)[0], chapter, f"{flags}")

    def test_continue_option_c_chapter_4_needs_flag_86_and_bit_211(self):
        """v8 final decisions: Continue shows chapter 4 only after the first 8,1 landing (bit 211); before it, 3.
        Other visited bits, and bits next to 211, change nothing."""
        cards = [ROM_BASE + a for a in self.n["cards"]]
        cases = [((26, 68, 86), (), 3), ((26, 68, 86), (BIT_8_1,), 4), ((26, 68), (BIT_8_1,), 3),
                 ((26, 68, 86, 87, 125), (210, 212, 203, 219), 3), ((26, 68, 86), tuple(range(297)), 4),
                 ((26, 68, 86, 87), tuple(v for v in range(297) if v != BIT_8_1), 3)]
        for flags, visited, chapter in cases:
            fb = flags_of(*flags, visited=visited)
            self.assertEqual(self.pick(fb), cards[chapter - 1], f"{flags} {len(visited)} bits")
            self.assertEqual(chapter_cards.chapter_for(fb)[0], chapter, f"{flags} {len(visited)} bits")
        texts = [t for _, t in listing(self.rom, self.lab["pick_test"], 10)]
        self.assertEqual(texts[4:8], ["bpl " + hex(self.lab["pick_hit"]), "mov r1,#0x4d", "ldrb r2,[r0,r1]",
                                      "lsl r2,r2,#28"])                    # +0x33 + 211 >> 3, bit 211 & 7 = 3

    def continue_run(self, slot: int, valid: int, flags: tuple, visited: tuple = ()) -> tuple:
        cpu, seen = Gba(self.rom), {"push": [], "orig": [], "valid": []}
        cpu.store(FS_OBJ + 0x10, 4, slot)
        if slot < 3:
            img = FS_OBJ + 0x14 + 0x164 * slot + 0xB4
            data = flags_of(*flags, visited=visited)
            cpu.ram[0x02][img & 0xFFFFFF:(img & 0xFFFFFF) + len(data)] = data

        def push(c):
            seen["push"].append((c.r[0], c.load(c.r[0], 4), c.load(c.r[0] + 4, 4), c.load(c.r[0] + 8, 4)))
            return 1

        def valid_fn(c):
            seen["valid"].append((c.r[0], c.r[1]))
            return valid

        def alloc(c):
            seen["alloc"].append(c.r[0])
            return OBJ

        seen["alloc"] = []
        cpu.r[4] = 0x4444
        stop = cpu.call((u32(self.rom, HOOK) + FS_VTABLE) & 0xFFFFFFFF, FS_OBJ,
            {SLOT_VALID & ~1: valid_fn, ALLOC & ~1: alloc, SCENE_PUSH & ~1: push,
             VANILLA_CONTINUE & ~1: lambda c: seen["orig"].append(c.r[0]) or 0x77})
        self.assertEqual(stop, "done")
        self.assertEqual((cpu.r[0], cpu.r[4], cpu.r[13]), (0x77, 0x4444, STACK))
        return seen

    def test_continue_shows_the_slot_card_then_runs_vanilla(self):
        for slot in range(3):
            seen = self.continue_run(slot, 1, (26, 68, 86, 125), (BIT_8_1,))
            self.assertEqual(seen["valid"], [(FS_OBJ + 0x14, slot)])
            self.assertEqual(seen["alloc"], [0x14])                           # vtable, frame, card, 4 registers
            self.assertEqual(seen["push"], [(OBJ, ROM_BASE + self.n["vtable"], 0, ROM_BASE + self.n["cards"][3])])
            self.assertEqual(seen["orig"], [FS_OBJ])

    def test_an_empty_slot_shows_card_1_then_the_vanilla_new_game(self):
        for slot in (0, 2):
            seen = self.continue_run(slot, 0, (26, 68, 195))                 # stale flags in an empty slot: ignored
            self.assertEqual(seen["push"], [(OBJ, ROM_BASE + self.n["vtable"], 0, ROM_BASE + self.n["cards"][0])])
            self.assertEqual(seen["orig"], [FS_OBJ])

    def test_vanilla_continue_starts_a_new_game_for_an_empty_slot(self):
        before = built()["before"]
        texts = [t for _, t in listing(before, 0x0800183C, 4)]             # slot used? else 0x080018CE
        self.assertEqual(texts, ["bl 0x80019f6", "cmp r0,#0x0", "beq 0x80018ce", "mov r3,#0xff"])
        texts = [t for _, t in listing(before, 0x080018CE, 4)]             # save init, start map
        self.assertEqual(texts, ["ldr r5,=0x081d4f14", "ldr r0,[r5,#0xc]", "bl 0x8003c24", "ldr r4,=0x08409410"])

    def test_no_card_for_slot_3(self):
        seen = self.continue_run(3, 1, ())
        self.assertEqual(seen["push"], [])
        self.assertEqual(seen["orig"], [FS_OBJ])

    def card_object(self, cpu: Gba, chapter: int) -> None:
        cpu.store(OBJ, 4, ROM_BASE + self.n["vtable"])
        cpu.store(OBJ + 4, 4, 0)
        cpu.store(OBJ + 8, 4, ROM_BASE + self.n["cards"][chapter - 1])

    def test_enter_draws_the_card_and_starts_the_ported_song(self):
        song = ROM_BASE + self.n["song"]["record"]
        for playing in (False, True):
            cpu, songs = Gba(self.rom), []
            self.card_object(cpu, 5)
            for a, v in FILE_SELECT_REGS:
                cpu.store(a, 2, v)
            if playing:
                cpu.store(PLAYER + 5, 1, 1)
                cpu.store(PLAYER + 0xC, 4, song)
            cpu.ram[0x05][:0x400] = b"\x5a" * 0x400                            # colours file select left
            stop = cpu.call(self.lab["card_enter"], OBJ,
                            {MUSIC_PLAY & ~1: lambda c: songs.append((c.r[0], c.r[1])) or 0}, limit=200000)
            self.assertEqual(stop, "done")
            self.assertEqual(songs, [] if playing else [(PLAYER, song)])
            self.assertEqual([cpu.load(a, 2) for a in (DISPCNT, BG3CNT, BLDCNT, BLDALPHA)], [0x0800, 0x1F83, 0, 0])
            self.assertEqual([cpu.load(OBJ + k, 2) for k in (0xC, 0xE, 0x10, 0x12)], [v for _, v in FILE_SELECT_REGS])
            self.assertEqual(bytes(cpu.ram[0x05][:0x200]), bytes(0x200))         # v7: BG palette black, no blend
            self.assertEqual(bytes(cpu.ram[0x05][0x200:0x400]), b"\x5a" * 0x200)  # OBJ palette not touched
            px = self.picture(cpu)
            want = chapter_cards.render_card(chapter_cards.bf_rom(), 5, "A New Horror")
            self.assertEqual(bytes(px), want)
            for _ in range(FADE_IN):                                            # the fade in ends at full colour
                self.assertEqual(cpu.call(self.lab["card_tick"], OBJ, limit=20000), "done")
            self.check_palette_and_text(cpu, px)
            n_tiles = self.n["base_tiles"] + u32(self.rom, self.n["cards"][4]) // 64
            self.assertLessEqual(n_tiles * 64, 0xF800)                         # tiles end below the screenblock

    @staticmethod
    def picture(cpu: Gba) -> bytearray:
        """240x160 palette indices BG3 shows: screenblock 0x0600F800, 8bpp tiles from 0x06000000."""
        px, vram = bytearray(240 * 160), cpu.ram[0x06]
        for ty in range(20):
            for tx in range(30):
                t = struct.unpack_from("<H", vram, 0xF800 + 2 * (ty * 32 + tx))[0]
                for y in range(8):
                    row = (ty * 8 + y) * 240 + tx * 8
                    px[row:row + 8] = vram[t * 64 + y * 8:t * 64 + y * 8 + 8]
        return px

    def check_palette_and_text(self, cpu: Gba, px: bytearray) -> None:
        """BG palette = BF rom:0x5632C except two entries the backdrop never uses, which hold BF OBJ bank 0
        entries 1 (0x0000) and 2 (0x7FFF); the picture differs from the BF backdrop only in those two entries."""
        bf, back = chapter_cards.bf_rom(), chapter_cards.backdrop(chapter_cards.bf_rom())[0]
        self.assertEqual(hashlib.sha1(back).hexdigest(), BACKDROP_PX_SHA1)
        pal = bytes(cpu.ram[0x05][:0x200])
        changed = [i for i in range(256) if pal[2 * i:2 * i + 2] != bf[BF_BG_PALETTE + 2 * i:BF_BG_PALETTE + 2 * i + 2]]
        self.assertEqual(len(changed), 2)
        self.assertEqual(set(changed) & set(back), set())
        self.assertEqual(sorted(u32(pal + bytes(2), 2 * i) & 0xFFFF for i in changed),
                         sorted(u32(bf, BF_OBJ_PALETTE + 2 * e) & 0xFFFF for e in (1, 2)))
        bank0 = sorted(u32(bf, BF_OBJ_PALETTE + 2 * e) & 0x7FFF for e in (1, 2))   # bit 15 is unused
        self.assertEqual(bank0, [0x0000, 0x7FFF])
        diff = [i for i in range(len(px)) if px[i] != back[i]]
        self.assertTrue(diff)
        self.assertEqual({px[i] for i in diff}, set(changed))
        self.assertTrue(all(40 <= i // 240 < 112 for i in diff))                # the text block only

    def ticks(self, keys: int = 0) -> tuple:
        """(the frame on which the tick returns 1, BG palette bytes after each tick, OBJ palette after the last);
        the palette starts black, as card_enter leaves it, and the OBJ half holds other colours."""
        cpu, pals = Gba(self.rom), []
        self.card_object(cpu, 1)
        cpu.ram[0x05][0x200:0x400] = b"\x5a" * 0x200
        for frame in range(1, 600):
            cpu.store(KEYS_NEW, 2, keys)
            self.assertEqual(cpu.call(self.lab["card_tick"], OBJ, limit=20000), "done")
            pals.append(bytes(cpu.ram[0x05][:0x200]))
            if cpu.r[0]:
                return frame, pals, bytes(cpu.ram[0x05][0x200:0x400])
        self.fail("the card never ends")

    def fade(self) -> tuple:
        if "fade" not in _FADE:
            _FADE["fade"] = self.ticks()
        return _FADE["fade"]

    def test_tick_has_bf_timing(self):
        """v7: the BF fades, frame by frame (card-fade-report.md option B, B8): in = BF ext 121 on its table, out =
        BF ext 120 on the card palette, full and unchanged in the hold, black on the last frame."""
        end, pals, obj = self.fade()
        bf = chapter_cards.bf_rom()
        full, rows = card_palette(bf), fade_rows(bf)
        self.assertEqual(end, FADE_IN + WAIT + FADE_OUT)                        # 450 frames, as the BF card script
        for f, pal in enumerate(pals, 1):
            if f < FADE_IN:
                lv = (f << 8) // FADE_IN
                want = [tuple(t * lv >> 11 for t in row) for row in rows]
            elif f <= FADE_IN + WAIT:
                self.assertEqual(pal, full, f"frame {f}")                       # the stored bytes, bit 15 kept
                continue
            else:
                lv = 256 - ((f - FADE_IN - WAIT) << 8) // FADE_OUT
                want = [tuple(c * lv >> 8 for c in rgb) for rgb in channels(full)]
            self.assertEqual(channels(pal), want, f"frame {f}")
        self.assertEqual(pals[-1], bytes(0x200))                                # BF ext 120 ends at black
        rise = [channels(p) for p in pals[:FADE_IN]]
        for a, b in zip(rise, rise[1:]):                                        # the fade in never steps back
            self.assertTrue(all(x <= y for p, q in zip(a, b) for x, y in zip(p, q)))
        self.assertEqual(obj, b"\x5a" * 0x200)                                  # OBJ palette not touched

    def test_first_card_frame_is_black_and_full_colour_waits_for_the_last_fade_in_frame(self):
        _, pals, _ = self.fade()
        full = card_palette(chapter_cards.bf_rom())
        self.assertEqual(pals[0], bytes(0x200))                                 # frame 1: no full-colour flash
        self.assertEqual(next(f for f, p in enumerate(pals, 1) if p == full), FADE_IN)
        for f, pal in enumerate(pals[:FADE_IN - 1], 1):
            self.assertTrue(all(x <= y for p, q in zip(channels(pal), channels(full)) for x, y in zip(p, q)), f)
            self.assertNotEqual(channels(pal), channels(full), f"frame {f}")

    def test_fades_step_on_bf_frames_by_one_level(self):
        """On the 105 shown entries (the backdrop's palette entries and the two text entries), the fades change
        on the same number of frames as BF's card fades, never by more than 1 level (card-fade-report.md table)."""
        _, pals, _ = self.fade()
        bf = chapter_cards.bf_rom()
        shown = sorted(set(chapter_cards.backdrop(bf)[0])) + sorted(TEXT_FROM_OBJ)
        self.assertEqual(len(shown), 105)
        frames = [channels(p) for p in pals]
        self.assertEqual(steps(frames[:FADE_IN], [(0, 0, 0)] * 256, shown), BF_STEPS["in"])
        self.assertEqual(steps(frames[FADE_IN + WAIT:], channels(card_palette(bf)), shown), BF_STEPS["out"])

    def test_no_button_skips_the_card(self):
        for keys in (0x0001, 0x0002, 0x0008, 0x03FF):                           # A, B, Start, every key held new
            self.assertEqual(self.ticks(keys)[0], FADE_IN + WAIT + FADE_OUT, hex(keys))

    def test_leave_restores_file_select_registers_and_frees_the_object(self):
        cpu, freed = Gba(self.rom), []
        self.card_object(cpu, 1)
        cpu.store(PLAYER + 5, 1, 1)                                             # song playing
        cpu.ram[0x05][:0x400] = b"\x55" * 0x400
        for a, v in ((DISPCNT, 0x800), (BG3CNT, 0x1F83), (BLDCNT, 0), (BLDALPHA, 0)):   # v7 card registers
            cpu.store(a, 2, v)
        for k, (_, v) in zip((0xC, 0xE, 0x10, 0x12), FILE_SELECT_REGS):
            cpu.store(OBJ + k, 2, v)
        stop = cpu.call(self.lab["card_leave"], OBJ, {FREE & ~1: lambda c: freed.append(c.r[0]) or 0}, limit=2000)
        self.assertEqual(stop, "done")
        self.assertEqual(freed, [OBJ])
        self.assertEqual([(a, cpu.load(a, 2)) for a, _ in FILE_SELECT_REGS], FILE_SELECT_REGS)
        self.assertEqual(bytes(cpu.ram[0x05][:0x200]), bytes(0x200))
        self.assertEqual(bytes(cpu.ram[0x05][0x200:0x400]), b"\x55" * 0x200)  # OBJ palette not touched
        self.assertEqual(cpu.r[13], STACK)
        self.assertEqual(cpu.load(PLAYER + 5, 1), 0)                            # music stopped, as BF ext 36


# ===== story points (v5) =====

def op_end(rom: bytes, o: int) -> int:
    """End of the script op at o (bible DS8 grammar): ops 0, 2, 3, 18, 19, 21-26, 28 one operand byte, op 1 a
    varint, op 29 a counted varint list, the rest none."""
    op = rom[o]
    if op in (0, 2, 3, 18, 19, 28) or 21 <= op <= 26:
        return o + 2
    if op in (1, 29):
        n, o = (1, o + 1) if op == 1 else (rom[o + 1], o + 2)
        for _ in range(n):
            while rom[o] & 0x80:
                o += 1
            o += 1
        return o
    if op <= 17 or op in (20, 27):
        return o + 1
    raise ValueError(f"op {op} at 0x{o:X}")


def walk(rom: bytes, rec: int) -> list:
    """[(offset, op bytes)] of a type 0 record from +3 to the op 17 that no forward jump passes."""
    ops, o, reach = [], rec + 3, 0
    while True:
        e = op_end(rom, o)
        ops.append((o, bytes(rom[o:e])))
        if rom[o] in (18, 19):
            reach = max(reach, e + rom[o + 1])
        if rom[o] == 17 and e > reach:
            return ops
        o = e


def jump_targets(ops: list) -> dict:
    """{op index: target op index} of every jz, jmp and loop (target = len(ops) for the record end)."""
    at = {o: i for i, (o, _) in enumerate(ops)}
    end = ops[-1][0] + len(ops[-1][1])
    out = {}
    for i, (o, b) in enumerate(ops):
        if b[0] in (18, 19, 28):
            t = o + 2 + (b[1] if b[0] != 28 else -b[1])
            out[i] = at[t] if t in at else (len(ops) if t == end else None)
    return out


def card_ops(card: int) -> list:
    """The inserted ops, restated: push N ; ext 145."""
    return [bytes([0, card]), bytes([2, CARD_OP])]


class StoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.lab = cls.n["labels"]
        cls.base = log2_build.BASE.read_bytes()

    def test_sources_are_base_bytes_and_fades_sit_right_before_the_insert(self):
        for card, (rec, length, _, at) in STORY_WANT.items():
            self.assertEqual(self.before[rec:rec + length], self.base[rec:rec + length], f"card {card}")
            ops = walk(self.before, rec)
            self.assertEqual(ops[-1][0] + 1 - rec, length, f"card {card}")
            self.assertIn(at, [o for o, _ in ops], f"card {card}")
            if card in FADE_BEFORE:
                fade, frames = FADE_BEFORE[card]
                self.assertEqual(self.before[fade:fade + 4], bytes([0, frames, 2, 40]), f"card {card}")
                self.assertEqual(fade + 4, at, f"card {card}")

    def test_v7_card_4_point_is_vanilla_again(self):
        """v8: the post-Android 20 record (SET 86, the fly-offs) and its table word are vanilla; no site covers
        them; only the landing scene shows card 4 (its one story op lives there)."""
        rec, length, word = V7_CARD4
        self.assertEqual(self.before[rec + 0x20:rec + 0x24].hex(), "0056021b")         # SET 86 in the record
        self.assertEqual(self.before[0x3D5500:0x3D5509].hex(), "00010256" "003e022e" "11")   # HUD on, chime 62, end
        self.assertEqual(u32(self.base, word), ROM_BASE + rec)
        self.assertEqual(u32(self.rom, word), ROM_BASE + rec)
        self.assertEqual(self.rom[rec:rec + length], self.base[rec:rec + length])
        sites = [(s, n) for s, n, _ in self.n["sites"]]
        self.assertEqual([(s, n) for s, n in sites if s < word + 4 and word < s + n], [])
        self.assertEqual([(s, n) for s, n in sites if s < rec + length and rec < s + n], [])
        self.assertNotIn(4, self.n["story"])
        card4 = bytes([0, 4, 2, CARD_OP])
        hits = [m.start() for m in re.finditer(re.escape(card4), self.rom[0x900000:])]
        land = self.n["landing"]
        self.assertEqual([0x900000 + h for h in hits], [land["records"] + bytes.fromhex(REC0_HEX).index(card4)])

    def test_each_copy_is_its_source_plus_the_card_ops_with_jumps_re_encoded(self):
        for card, (rec, length, _, at) in STORY_WANT.items():
            copy = self.n["story"][card]["copy"]
            src, new = walk(self.before, rec), walk(self.rom, copy)
            k = [o for o, _ in src].index(at)
            ins = card_ops(card)
            self.assertEqual(self.rom[copy:copy + 3], self.before[rec:rec + 3], f"card {card}: next index, type")
            self.assertEqual([b for _, b in new[k:k + len(ins)]], ins, f"card {card}")
            rest = new[:k] + new[k + len(ins):]
            self.assertEqual([b[0] for _, b in rest], [b[0] for _, b in src], f"card {card}")
            self.assertEqual([b for _, b in rest if b[0] not in (18, 19, 28)],
                             [b for _, b in src if b[0] not in (18, 19, 28)], f"card {card}")
            mapped = {i: (i if i < k else i + len(ins)) for i in range(len(src) + 1)}
            mapped[k] = k                                                          # a jump to the insert runs the card
            want = {mapped[i]: mapped[t] for i, t in jump_targets(src).items()}
            self.assertEqual(jump_targets(new), want, f"card {card}")

    def test_each_copy_ends_where_its_ops_end(self):
        for card, (rec, length, _, _) in STORY_WANT.items():
            s = self.n["story"][card]
            ops = walk(self.rom, s["copy"])
            end = ops[-1][0] + 1
            self.assertEqual(end - s["copy"], s["length"], f"card {card}")
            self.assertEqual(s["length"], length + sum(map(len, card_ops(card))), f"card {card}")
            self.assertEqual(ops[-1][1], b"\x11")
            self.assertEqual(set(self.before[end:end + 1]), {0xFF})               # nothing past it was free space

    def test_the_live_word_names_the_copy_and_the_old_record_stays(self):
        words = memoryview(self.rom[: len(self.rom) & ~3]).cast("I")
        for card, (rec, length, word, _) in STORY_WANT.items():
            copy = ROM_BASE + self.n["story"][card]["copy"]
            self.assertEqual(self.n["story"][card]["word"], word)
            self.assertEqual(u32(self.before, word), ROM_BASE + rec)
            self.assertEqual(u32(self.rom, word), copy)
            self.assertEqual([4 * i for i, w in enumerate(words) if w == copy], [word], f"card {card}")
            old = [4 * i for i, w in enumerate(words) if w == ROM_BASE + rec]
            self.assertEqual(old, [CHAMBER_VANILLA] if card == 7 else [], f"card {card}")
            self.assertEqual(self.rom[rec:rec + length], self.before[rec:rec + length])
        self.assertEqual({u32(self.rom, w) for w in CHAMBER_TYPE5}, {ROM_BASE + STORY_WANT[7][2]})

    def test_each_record_ends_where_its_next_word_says(self):
        """+0 next index = the record's table index + 1; that word names the record right after the source end
        (0-3 zero pad bytes between), or holds no ROM pointer (the table's last record: card 2)."""
        for card, (rec, length, word, _) in STORY_WANT.items():
            t0, holder = TABLE0[card]
            self.assertEqual(u32(self.before, holder), ROM_BASE + t0, f"card {card}: real word 0")
            index, rem = divmod(word - t0, 4)
            self.assertEqual((rem, u32(self.before, word)), (0, ROM_BASE + rec), f"card {card}")
            self.assertFalse(t0 <= holder < word + 4, f"card {card}: the holder is not a table word")
            nxt = struct.unpack_from("<H", self.before, rec)[0]
            self.assertEqual(nxt, index + 1, f"card {card}")
            target = u32(self.before, t0 + 4 * nxt)
            self.assertEqual(u32(self.rom, t0 + 4 * nxt), target, f"card {card}: next word unchanged")
            if not ROM_BASE + SCRIPT_REGION[0] <= target < ROM_BASE + SCRIPT_REGION[1]:
                self.assertEqual(card, 2, f"card {card}: only card 2 ends its table")
                continue
            gap = target - ROM_BASE - (rec + length)
            self.assertTrue(0 <= gap <= 3, f"card {card}: gap {gap}")
            self.assertEqual(set(self.before[rec + length:rec + length + gap]) | {0}, {0}, f"card {card}")

    def test_v5_card_5_point_is_vanilla_again(self):
        rec, length, word = V5_CARD5
        self.assertEqual(self.base[rec + 3:rec + 11].hex(), "005a0228" "00010256")    # fade 90, HUD on (v5 point)
        self.assertEqual(u32(self.base, word), ROM_BASE + rec)
        self.assertEqual(u32(self.rom, word), ROM_BASE + rec)
        self.assertEqual(self.rom[rec:rec + length], self.base[rec:rec + length])
        sites = [(s, n) for s, n, _ in self.n["sites"]]
        self.assertEqual([(s, n) for s, n in sites if s < word + 4 and word < s + n], [])
        self.assertEqual([(s, n) for s, n in sites if s < rec + length and rec < s + n], [])

    def test_card_5_is_the_kami_scene_end_before_the_time_machine_map(self):
        rec = STORY_WANT[5][0]
        self.assertEqual(self.before[rec + 3:rec + 0x16].hex(),
                         "0081021b" "005a0228" "1d0504280282408410" "0227")   # SET 129, fade 90, push 2,20,.. ; ext 39
        copy = self.n["story"][5]["copy"]
        self.assertEqual(self.rom[copy + 3:copy + 0x1A].hex(),
                         "0081021b" "005a0228" "00050291" "1d0504280282408410" "0227")

    def test_android_19_table_is_untouched(self):
        self.assertEqual(u32(self.before, 0x3FD4F4), ROM_BASE + A19_TABLE[0])      # the word that names it
        ranges = [A19_TABLE, A19_RECORDS]
        mine = [(s, n) for s, n, _ in self.n["sites"]]
        mine += [(w, 4) for _, _, w, _ in STORY_WANT.values()] + [(r, k) for r, k, _, _ in STORY_WANT.values()]
        for s, n in ranges:
            self.assertEqual([m for m in mine if m[0] < s + n and s < m[0] + m[1]], [], f"rom:0x{s:X}")
            self.assertEqual(self.rom[s:s + n], self.before[s:s + n], f"rom:0x{s:X}")

    def test_ext_table_copy_and_its_two_names(self):
        ext = self.n["ext_table"]
        self.assertEqual([u32(self.rom, ext + 4 * k) for k in range(CARD_OP)],
                         [u32(self.before, EXT_TABLE + 4 * k) for k in range(CARD_OP)])
        self.assertEqual(u32(self.rom, ext + 4 * CARD_OP), self.lab["cc_story"] | 1)
        self.assertEqual(u32(self.before, EXT_TABLE + 4 * CARD_OP), 0x03000E90)   # the data word the copy steps over
        words = memoryview(self.rom[: len(self.rom) & ~3]).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(words) if w == ROM_BASE + ext], list(EXT_POOLS))
        self.assertEqual([4 * i for i, w in enumerate(words) if w == ROM_BASE + EXT_TABLE], [])
        before = memoryview(self.before[: len(self.before) & ~3]).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(before) if w == ROM_BASE + EXT_TABLE], list(EXT_POOLS))
        self.assertEqual(self.rom[EXT_TABLE:EXT_TABLE + 4 * CARD_OP], self.before[EXT_TABLE:EXT_TABLE + 4 * CARD_OP])

    def dispatch(self, n: int, stops: dict) -> tuple:
        """Op 2 (ROM code) run on `02 n`: (stop, r0) where the handler word sends it."""
        cpu, ctx = Gba(self.rom), 0x02000400
        cpu.store(0x02000500, 4, 0x02000600)
        cpu.ram[0x02][0x600] = n
        cpu.r[1] = 0x02000500
        return cpu.call(OP2, ctx, stops), cpu.r[0]

    def test_op_2_reaches_the_card_op_and_the_vanilla_ops_through_the_copy(self):
        self.assertEqual(self.dispatch(CARD_OP, {self.lab["cc_story"]: "story"}), ("story", 0x02000400))
        self.assertEqual(self.dispatch(70, {0x0800A784: "ext70"})[0], "ext70")
        self.assertEqual(self.dispatch(69, {0x0800A65C: "ext69"})[0], "ext69")

    def story(self, n: int, playing: int) -> dict:
        cpu, seen, ctx = Gba(self.rom), {"push": [], "song": []}, 0x02000400
        cpu.store(ctx, 4, 1)
        cpu.store(ctx + 4, 4, n)
        cpu.store(PLAYER + 5, 1, playing)
        cpu.store(PLAYER + 0xC, 4, 0x081D4D20)                                     # song 25's record
        stops = {ALLOC & ~1: lambda c: OBJ,
                 SCENE_PUSH & ~1: lambda c: seen["push"].append(c.load(c.r[0] + 8, 4)) or 1,
                 MUSIC_PLAY & ~1: lambda c: seen["song"].append((c.r[0], c.r[1])) or 0}
        cpu.r[4], cpu.r[5], cpu.r[6] = 0x44, 0x55, 0x66
        self.assertEqual(cpu.call(self.lab["cc_story"], ctx, stops, limit=2000), "done")
        self.assertEqual((cpu.load(ctx, 4), cpu.r[4], cpu.r[5], cpu.r[6], cpu.r[13]), (0, 0x44, 0x55, 0x66, STACK))
        return seen

    def test_card_op_pops_n_and_shows_card_n(self):
        """Every card (4 too, v8: a map load follows it in the landing scene) shows and the script goes on; the
        op never touches the music (the map load restarts it, map_load_core 0x0800C4E0-0x0800C50E)."""
        cards = [ROM_BASE + a for a in self.n["cards"]]
        for n in range(1, 9):
            for playing in (0, 1):
                self.assertEqual(self.story(n, playing), {"push": [cards[n - 1]], "song": []}, f"card {n}")
        for n in (0, 9, 200):
            self.assertEqual(self.story(n, 1), {"push": [], "song": []}, f"card {n}")

    def test_a_map_load_plays_the_map_music_after_the_card_stopped_it(self):
        texts = [t for _, t in listing(self.before, 0x0800C4FA, 10)]
        self.assertEqual(texts, ["ldr r2,=0x081d4b2c", "lsl r1,r1,#2", "ldr r0,[r7,#0x0]", "add r1,r1,r2",
                                 "ldrb r2,[r0,#0x5]", "cmp r2,#0x1", "bne 0x800c50e", "ldr r2,[r0,#0xc]",
                                 "cmp r2,r1", "beq 0x800c512"])               # plays unless +5 = 1 and the same song
        self.assertEqual([t for _, t in listing(self.before, 0x0800C50E, 1)], ["bl 0x8020a4c"])


# ===== card 4 landing scene (v8) =====

def varints(rom: bytes, o: int, n: int) -> tuple:
    """n op 29 values from o: 7 bits a byte, MSB first, high bit = more; value raw >> 1, negative when odd."""
    out = []
    for _ in range(n):
        raw = 0
        while True:
            raw = raw << 7 | rom[o] & 0x7F
            o += 1
            if not rom[o - 1] & 0x80:
                break
        out.append(-(raw >> 1) if raw & 1 else raw >> 1)
    return tuple(out)


def run_record(rom: bytes, at: int, leader: int, visited: int) -> tuple:
    """(next index, [(ext n, args)]) of a type 0 record, run as the interpreter would for the ops it uses: push,
    eq, skip when zero, end (the next index = the stack top, else +0); ext 11 pushes the leader, ext 23 (zone,
    area) pushes the visited bit of 8,1; every other ext takes all values pushed before it."""
    nxt, o, st, calls = struct.unpack_from("<H", rom, at)[0], at + 3, [], []
    while True:
        op, e = rom[o], op_end(rom, o)
        if op == 0:
            st.append(rom[o + 1])
        elif op == 29:
            st += varints(rom, o + 2, rom[o + 1])
        elif op == 2 and rom[o + 1] == 11:
            st.append(leader)
            calls.append((11, ()))
        elif op == 2 and rom[o + 1] == 23:
            args, st = tuple(st[-2:]), st[:-2]
            calls.append((23, args))
            st.append(visited if args == (8, 1) else None)
        elif op == 2:
            calls.append((rom[o + 1], tuple(st)))
            st = []
        elif op == 11:
            b, a = st.pop(), st.pop()
            st.append(int(a == b))
        elif op == 19:
            e += 0 if st.pop() else rom[o + 1]
        elif op == 17:
            return (st[-1] if st else nxt), calls
        else:
            raise AssertionError(f"op {op} at rom:0x{o:X} is not a landing scene op")
        o = e


def dist(a: tuple, b: tuple) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def map_tiles(rom: bytes) -> list:
    """Map 8,1's 8x8 tile pixels: the layout's tile index is delta coded (each entry + the one before + 1) and
    names a chunk and a tile in it (layout +0x48 the index, +0x4C the chunk table)."""
    from rom import webfoot_decompress

    def frame(addr):
        return webfoot_decompress.unpack_frame(rom, addr - ROM_BASE)[2]

    raw = frame(u32(rom, LAYOUT_8_1 - ROM_BASE + 0x48))
    idx = list(struct.unpack(f"<{len(raw) // 2}H", raw))
    for i in range(1, len(idx)):
        idx[i] = (idx[i] + idx[i - 1] + 1) & 0xFFFF
    table, chunks, out = u32(rom, LAYOUT_8_1 - ROM_BASE + 0x4C), {}, []
    for e in idx:
        hi, lo = e >> 8, e & 0xFF
        if hi not in chunks:
            chunks[hi] = frame(u32(rom, table - ROM_BASE + 4 * hi))
        out.append(chunks[hi][64 * lo:64 * lo + 64])
    return out


def layer_opaque(rom: bytes, off: int) -> set:
    """{(x, y)} map pixels the layer at layout + off draws. Each tile map entry is {tile 0-9, flip x 0x400,
    flip y 0x800}; palette index 0 is transparent, and a tile id past the tile list draws nothing."""
    from rom import webfoot_decompress
    rec = u32(rom, LAYOUT_8_1 - ROM_BASE + off) - ROM_BASE
    tl, out = map_tiles(rom), set()
    bx, by = rom[rec + 0x14], rom[rec + 0x15]
    for k in range(bx * by):
        p = u32(rom, rec + 0x18 + 4 * k)
        if not p:
            continue
        m = webfoot_decompress.unpack_frame(rom, p - ROM_BASE)[2]
        ox, oy = (k % bx) * 256, (k // bx) * 256
        for t in range(1024):
            e = struct.unpack_from("<H", m, 2 * t)[0]
            n = e & 0x3FF
            if n >= len(tl) or not any(tl[n]):
                continue
            px, x0, y0 = tl[n], ox + (t % 32) * 8, oy + (t // 32) * 8
            for yy in range(8):
                for xx in range(8):
                    if px[(7 - yy if e & 0x800 else yy) * 8 + (7 - xx if e & 0x400 else xx)]:
                        out.add((x0 + xx, y0 + yy))
    return out


def dialog_wrap(rom: bytes, box: bytes) -> list:
    """Lines of one box as the dialog line counter breaks them (bible C4S: past 144 px, at the last space)."""
    def adv(c):
        glyph = struct.unpack_from("<H", rom, DIALOG_FONT + 2 * c)[0]
        return struct.unpack_from("<H", rom, DIALOG_FONT + 2 * glyph)[0] + 1

    out, p = [], 0
    while p < len(box):
        while p < len(box) and box[p] == 0x20:
            p += 1
        if p >= len(box):
            break
        q, w, brk = p, 0, None
        while q < len(box):
            if box[q] == 0x20:
                brk = q
            w += adv(box[q])
            if w > DIALOG_WIDTH:
                q = brk if brk is not None else q
                break
            q += 1
        out.append((box[p:q].decode(), sum(adv(c) for c in box[p:q])))
        p = q
    return out


class LandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.n = b["rom"], b["before"], b["notes"]
        cls.land = cls.n["landing"]
        cls.base = log2_build.BASE.read_bytes()

    def word(self, i: int) -> int:
        return u32(self.rom, self.land["table"] + 4 * i)

    def play(self, leader: int, visited: int = 0) -> tuple:
        """([table index], [(ext n, args)], [(portrait, text)]) from index 0 to the END word."""
        idx, path, calls, said = 0, [], [], []
        while self.word(idx):
            path.append(idx)
            at = self.word(idx) - ROM_BASE
            if self.rom[at + 2] == 1:
                end = self.rom.index(b"\0", at + 4)
                said.append((self.rom[at + 3], self.rom[at + 4:end].decode("ascii")))
                idx = self.rom[at]
            else:
                idx, c = run_record(self.rom, at, leader, visited)
                calls += c
            self.assertLess(len(path), 40)
        self.assertEqual(idx, 16)
        return path, calls, said

    def test_item_copy_region_word_and_table(self):
        item, table = self.land["item"], self.land["table"]
        self.assertEqual(self.before[LANDING_ITEM:LANDING_ITEM + 20].hex(), LANDING_ITEM_HEX)
        self.assertEqual(self.before[LANDING_SCRIPT:LANDING_SCRIPT + 12].hex(), LANDING_SCRIPT_HEX)
        self.assertEqual(u32(self.before, LANDING_REGION_WORD), ROM_BASE + LANDING_ITEM)
        self.assertEqual(u32(self.rom, LANDING_REGION_WORD), ROM_BASE + item)
        self.assertEqual(self.rom[LANDING_ITEM:LANDING_ITEM + 20], self.before[LANDING_ITEM:LANDING_ITEM + 20])
        self.assertEqual(self.rom[LANDING_SCRIPT:LANDING_SCRIPT + 12], self.before[LANDING_SCRIPT:LANDING_SCRIPT + 12])
        want = (struct.pack("<I", SCENE_ITEM) + bytes.fromhex(LANDING_ITEM_HEX)[4:16]
                + struct.pack("<I", ROM_BASE + table))
        self.assertEqual(self.rom[item:item + 20], want)                   # same A-press trigger and rect
        self.assertEqual((item % 4, table % 4, table - item), (0, 0, 20))
        words = memoryview(self.rom[: len(self.rom) & ~3]).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(words) if w == ROM_BASE + item], [LANDING_REGION_WORD])
        self.assertEqual([4 * i for i, w in enumerate(words) if w == ROM_BASE + table], [item + 16])
        self.assertEqual([4 * i for i, w in enumerate(words) if w == ROM_BASE + LANDING_ITEM], [])
        self.assertEqual(u32(self.rom, LANDING_REGION_WORD - 4), 0x00010056)   # region 11 cond: flag 86 set
        at = self.land["records"]                                          # records back to back, word 16 = 0
        for i in range(LANDING_WORDS - 1):
            self.assertEqual(self.word(i), ROM_BASE + at, f"word {i}")
            at = (self.rom.index(b"\0", at + 4) + 1) if self.rom[at + 2] == 1 else walk(self.rom, at)[-1][0] + 1
        self.assertEqual((self.word(16), at), (0, self.land["item"] + self.land["size"]))

    def test_scene_item_factory_takes_the_copy_on_the_interpreter(self):
        """The vanilla factory run on the copy: vtable 0x08023E44, +0x10 index 0, +0x14 = the landing table (the
        activate 0x0800D7A0 runs the table from there)."""
        cpu, seen = Gba(self.rom), []
        cpu.ram[0x02][0x100:0x120] = b"\x77" * 0x20
        stop = cpu.call(SCENE_ITEM, ROM_BASE + self.land["item"],
                        {ALLOC & ~1: lambda c: seen.append(c.r[0]) or OBJ, ITEM_INIT & ~1: lambda c: c.r[0]})
        self.assertEqual((stop, seen, cpu.r[0]), ("done", [0x18], OBJ))
        self.assertEqual((cpu.load(OBJ, 4), cpu.load(OBJ + 0x10, 2), cpu.load(OBJ + 0x14, 4)),
                         (SCENE_VTABLE, 0, ROM_BASE + self.land["table"]))
        self.assertEqual(u32(self.rom, 0x23E44 + 4) + 0x08023E44 & 0xFFFFFFFF, 0x0800D7A1)   # +4 = activate
        texts = [t for _, t in listing(self.rom, 0x0800D7A0, 21)]
        self.assertEqual(texts[8], "ldr r1,[r0,#0x14]")                   # the table
        self.assertEqual(texts[20], "bl 0x801f2f4")                       # scene_push: a nested frame loop

    def test_guard_ext_23_reads_the_8_1_visited_bit_on_the_interpreter(self):
        """ext 23 (zone 8, area 1) pushes save +0xE7 bit 211: 1 set, 0 clear; other bits do not count."""
        for byte, want in ((0x08, 1), (0x00, 0), (0xF7, 0), (0xFF, 1)):
            cpu, ctx = Gba(self.rom), 0x02000400
            for k, v in enumerate((2, 8, 1)):
                cpu.store(ctx + 4 * k, 4, v)
            cpu.ram[0x03][0xE90 + 0xE7 + (BIT_8_1 >> 3)] = byte
            self.assertEqual(cpu.call(0x08009629, ctx, limit=20000), "done")
            self.assertEqual((cpu.load(ctx, 4), cpu.load(ctx + 4, 4)), (1, want), hex(byte))

    def test_guard_first_landing_only(self):
        rec = self.word(0) - ROM_BASE
        self.assertEqual(self.rom[rec:rec + len(REC0_HEX) // 2].hex(), REC0_HEX)
        land, arrive = (8, 1, 1, 272, 128), (8, 1, 1) + PLAYER_SPOT
        for leader in (0, 1, 2):
            path, calls, said = self.play(leader, visited=1)                 # a later landing: vanilla, END
            self.assertEqual((path, said), ([0], []))
            self.assertEqual(calls, [(23, (8, 1)), (38, land)])
        nxt, calls = run_record(self.rom, rec, 0, 0)                       # v9: the first landing at the row
        self.assertEqual((nxt, calls), (1, [(23, (8, 1)), (40, (60,)), (145, (4,)), (39, arrive)]))

    def test_branch_per_leader(self):
        for leader in (0, 1, 2, 3, 7):                                     # 3, 7: not reachable, Gohan's branch
            who = LEADERS.get(leader, "Gohan")
            path, calls, said = self.play(leader)
            gp = who != "Vegeta"
            want_path = ([0, 1, 2 if who == "Gohan" else 3, 5, 6, 7, 13 if who == "Gohan" else 14] if gp
                         else [0, 1, 4, 8, 9, 10, 11, 12, 15])
            self.assertEqual(path, want_path, who)
            speech = SPEECH_GP if gp else SPEECH_V
            self.assertEqual(said, [(p, "\x0b".join(boxes)) for p, boxes in speech], who)
            spots = SPOTS[who]
            self.assertNotIn(who, spots)                               # the leader is the player, not an NPC
            self.assertEqual(sorted(spots), sorted(ROWS[who]), who)    # the same cast as my branch list
            row = {NPC[name]: xyf for name, xyf in spots.items()}
            names = [n for n, _ in calls]
            self.assertEqual([a for n, a in calls if n == 51], [(i, x, FROM_Y) for i, (x, _, _) in row.items()], who)
            self.assertEqual([a for n, a in calls if n == 54],
                             [(i, x, y) for i, (x, y, _) in row.items()]
                             + [(i, x, OFF_Y) for i, (x, _, _) in row.items()], who)
            self.assertEqual([a for n, a in calls if n == 52], [(i,) for i in row], who)
            self.assertEqual([a for n, a in calls if n == 112], [(i, 26) for i in row], who)
            first = names.index(51)
            self.assertEqual(calls[first - 3:first], [(86, (0,)), (55, (0, 0)), (31, CAMERA)], who)
            self.assertEqual(calls[first + 5:first + 8], [(41, (60,)), (46, (26,)), (63, ())], who)
            faces = [a for n, a in calls if n == 55][1:]               # [0] is the under-black reset
            want_faces = [(i, f) for i, (_, _, f) in row.items()]
            if who in PLAYER_FACE:                                     # else he keeps the under-black DOWN
                want_faces.append((0, PLAYER_FACE[who]))
            self.assertEqual(faces, want_faces, who)
            self.assertEqual([a for n, a in calls if n == 55 and a[0] == 0],
                             [(0, 0)] + ([(0, PLAYER_FACE[who])] if who in PLAYER_FACE else []), who)
            self.assertGreater(len({f for _, f in faces}), 1, who)     # never one row all facing the same way
            fly = [a for n, a in calls if n == 54][:len(row)]
            self.assertTrue(all(y <= SOUTH_LIMIT for _, _, y in fly), who)
            self.assertEqual(calls[-2:], [(33, (0,)), (86, (1,))], who)
            self.assertEqual(names.count(145), 1, who)

    def spots_of(self, who: str) -> list:
        """[(name, x, y, facing)] for one leader: the five NPCs, then the player at his landing spot. A leader
        with no PLAYER_FACE row keeps the DOWN the arrival sets under black."""
        out = [(n, x, y, f) for n, (x, y, f) in SPOTS[who].items()]
        return out + [("player", PLAYER_SPOT[0], PLAYER_SPOT[1], PLAYER_FACE.get(who, DOWN))]

    def collision(self):
        """The map 8,1 collision frame, with the layout chain it hangs on proved first."""
        from rom import webfoot_decompress
        entry = 0x40BFD0                                                   # map 8,1 (bible CH8 row)
        self.assertEqual(self.base[entry:entry + 2], bytes([8, 1]))
        self.assertEqual(u32(self.base, u32(self.base, entry + 0x2C) - ROM_BASE), LAYOUT_8_1)
        self.assertEqual(u32(self.base, LAYOUT_8_1 - ROM_BASE + 0x34), COLLISION_8_1)
        self.assertEqual(struct.unpack_from("<2H", self.base, LAYOUT_8_1 - ROM_BASE + 8), CLAMP)      # clamp
        return webfoot_decompress.unpack_frame(self.rom, COLLISION_8_1 - ROM_BASE)[2]

    def test_every_spot_is_open_ground_and_the_player_can_walk_off(self):
        """v9 rule, now per actor: every NPC box (x - 8 .. x + 24, y - 28 .. y + 8) is open collision on 8,1
        (trunks, rocks and bushes are closed); the view at the camera holds every sprite at its widest and tallest
        (bible CJH hurtboxes: x - 9 .. x + 25, y - 26 .. y + 10); the spawn and fly-off rows are off the view;
        from the player's spot the 16x8 foot box still reaches the exit region.

        The player is the one exception and it is forced: he lands on the vanilla LAND, and the rock north of it
        closes exactly the two cells of PLAYER_CLOSED inside his box. The test pins those two, so the exception
        cannot grow, and it still holds him to the view and to open ground under his own feet."""
        bits = self.collision()

        def is_open(x, y):
            return (0 <= x < MAP_8_1[0] and 0 <= y < MAP_8_1[1]
                    and bool(bits[(y >> 3) * 32 + (x >> 6)] >> (x >> 3 & 7) & 1))

        cam_x, cam_y = CAMERA[:2]
        self.assertEqual((cam_x, cam_y), CLAMP)                            # v12 sets the camera at the clamp
        self.assertTrue(0 <= cam_x <= CLAMP[0] and 0 <= cam_y <= CLAMP[1])
        for who in SPOTS:
            for name, x, y, _ in self.spots_of(who):
                closed = [(xx, yy) for xx in range(x - 8, x + 24, 4) for yy in range(y - 28, y + 8, 4)
                          if not is_open(xx, yy)]
                want = [c for c in PLAYER_CLOSED] if (x, y) == PLAYER_SPOT else []
                self.assertEqual(sorted({(xx & ~7, yy & ~7) for xx, yy in closed}), sorted(want), (who, name))
                self.assertTrue(cam_x <= x - 9 and x + 25 <= cam_x + 240
                                and cam_y <= y - 26 and y + 10 <= cam_y + 160, (who, name))
        self.assertTrue(FROM_Y - 26 >= cam_y + 160 and OFF_Y + 10 <= cam_y)
        self.assertTrue(is_open(272, 128) and not is_open(272, 120))       # the player spot: the rock above
        foot = lambda x, y: all(is_open(xx, yy) for xx in (x, x + 15) for yy in (y, y + 7))   # noqa: E731
        seen, todo = {PLAYER_SPOT}, [PLAYER_SPOT]
        self.assertTrue(foot(*PLAYER_SPOT))
        while todo:
            x, y = todo.pop()
            for n in ((x + 4, y), (x - 4, y), (x, y + 4), (x, y - 4)):
                if n not in seen and foot(*n):
                    seen.add(n)
                    todo.append(n)
        x0, y0, x1, y1 = FLIGHT_PAD
        self.assertTrue(any(x0 <= x and x + 16 <= x1 and y0 <= y and y + 8 <= y1 for x, y in seen))
        self.assertGreater(len(seen), 1000)                                # not boxed in

    def test_no_actor_stands_on_the_save_point_or_south_of_the_text_box(self):
        """2026-10-30 11:20 PM: nobody on the capsule corp switcher (map 8,1 region 1, the save point) and
        nobody where the text box draws. The actor's own spot is its 16x8 foot box centre. The limit is a screen
        row, so it follows the camera: an NPC's feet stay at SOUTH_SCREEN or above.

        The player is the forced exception. The vanilla landing is y 128, the camera y clamp is 41, so his feet
        sit at screen row PLAYER_EXCEPTION. No legal camera does better, and the test proves it by checking that
        a larger camera y would leave the clamp."""
        x0, y0, x1, y1 = SAVE_RECT
        for who in SPOTS:
            for name, x, y, _ in self.spots_of(who):
                self.assertFalse(x0 <= x + 8 <= x1 and y0 <= y <= y1, (who, name, x, y))
                limit = SOUTH_LIMIT if (x, y) != PLAYER_SPOT else CAMERA[1] + PLAYER_EXCEPTION
                self.assertLessEqual(y, limit, (who, name))
        self.assertEqual(PLAYER_SPOT[1] - CAMERA[1], PLAYER_EXCEPTION)     # his feet, in screen rows
        self.assertGreater(PLAYER_EXCEPTION, SOUTH_SCREEN)                 # he is past the NPC line, by 3 px
        self.assertLess(PLAYER_EXCEPTION, BOX_TOP)                         # his feet still clear the box itself
        self.assertEqual(CAMERA[1], CLAMP[1])                              # and no camera puts him higher

    def test_no_actor_stands_under_a_bg1_canopy(self):
        """BG1 holds the tree canopies and draws over the actors (bible C4V row), so an actor under one is hidden.
        No BG1 pixel falls in any actor's box. The pixels come from the layout's own tiles and tile maps."""
        self.assertEqual(u32(self.base, u32(self.base, LAYOUT_8_1 - ROM_BASE + BG1_LAYER) - ROM_BASE), 0x080056A1)
        canopy = layer_opaque(self.rom, BG1_LAYER)
        self.assertGreater(len(canopy), 10000, "BG1 decoded to almost nothing: the reader is wrong")
        for who in SPOTS:
            for name, x, y, _ in self.spots_of(who):
                hits = [(xx, yy) for xx in range(x - 8, x + 24) for yy in range(y - 28, y + 8)
                        if (xx, yy) in canopy]
                self.assertEqual(hits, [], (who, name, x, y))
        self.assertTrue(any((xx, 128) in canopy for xx in range(152, 216)))   # the v8 row was under canopies

    def test_every_sprite_keeps_floor_between_itself_and_the_save_point(self):
        """2026-10-30 11:55 PM: they "stand too close to the save point". v10 kept every actor's spot out of
        the rect but let the drawn 16x32 frame cross its edge by up to 6 px. Here the frame itself keeps CLEAR px
        of floor in the Vegeta and Piccolo branches, or POCKET_CLEAR when the actor stands wholly west of the rect
        (the west pocket is 32 px of floor wide, so two 16 px sprites leave 16 px and 0 px)."""
        sx0, sx1, sy0, sy1 = SPRITE
        rx0, ry0, rx1, ry1 = SAVE_RECT

        def floor(x, y):
            """px between the sprite box and the rect; 0 touches it, less than 0 stands on it."""
            return max(rx0 - (x + sx1), (x + sx0) - (rx1 + 1), ry0 - (y + sy1), (y + sy0) - (ry1 + 1))

        self.assertEqual(floor(100, 84), -6)                   # the v10 spot I called out, as a yardstick
        self.assertEqual(floor(44, 84), -4)
        worst = {}
        for who in MARGIN_BRANCHES:
            for name, x, y, _ in self.spots_of(who):
                want = POCKET_CLEAR if x + sx1 <= rx0 else CLEAR
                self.assertGreaterEqual(floor(x, y), want, (who, name, x, y))
                worst[who] = min(worst.get(who, 99), floor(x, y))
        self.assertEqual(worst, {"Piccolo": SAVE_WORST, "Vegeta": SAVE_WORST})   # v12 stands nobody near it
        for who in SPOTS:               # every branch, every actor: v12 needs no carve-out at the save point
            for name, x, y, _ in self.spots_of(who):
                self.assertGreaterEqual(floor(x, y), CLEAR, (who, name, x, y))

    def test_no_two_sprites_overlap(self):
        """v10 left Tien standing in the player in the Piccolo branch (8x16 px). No two drawn frames may share a
        pixel in any branch, so a landed actor never reads as a glitch."""
        sx0, sx1, sy0, sy1 = SPRITE
        for who in SPOTS:
            spots = self.spots_of(who)
            for a in range(len(spots)):
                for b in range(a + 1, len(spots)):
                    na, xa, ya, _ = spots[a]
                    nb, xb, yb, _ = spots[b]
                    w = min(xa + sx1, xb + sx1) - max(xa + sx0, xb + sx0)
                    h = min(ya + sy1, yb + sy1) - max(ya + sy0, yb + sy0)
                    self.assertFalse(w > 0 and h > 0, (who, na, nb, w, h))

    def test_tien_and_krillin_look_at_the_player_and_gohan_lands_facing_north(self):
        """2026-10-30 11:55 PM: "have tien and krillin face piccolo", and Gohan "flies from the bottom, have
        him land facing up". The looking facings are worked out from the spots here, by this file's own rule, so a
        hardcoded byte in the module cannot pass. A diagonal spot would leave the direction open, so it fails."""
        px, py = PLAYER_SPOT
        for who, lookers in LOOKS_AT_PLAYER.items():
            spots = {n: (x, y, f) for n, x, y, f in self.spots_of(who)}
            for name in lookers:
                x, y, face = spots[name]
                dx, dy = px - x, py - y
                self.assertNotEqual(abs(dx), abs(dy), (who, name, "diagonal: the facing is not decided"))
                want = (RIGHT if dx > 0 else LEFT) if abs(dx) > abs(dy) else (DOWN if dy > 0 else UP)
                self.assertEqual(face, want, (who, name, x, y))
        for who, north in FACES_NORTH.items():
            for name in north:
                self.assertEqual(SPOTS[who][name][2], UP, (who, name))
                self.assertGreater(SPOTS[who][name][1], 0)             # he flew in from the south, FROM_Y
        self.assertNotIn("Gohan", PLAYER_FACE)                         # ask 1: no forced turn in his own branch

    def test_each_group_holds_together_and_the_groups_stand_apart(self):
        """Me: three groups, not one row. Every actor belongs to exactly one group, has a group mate within
        NEAR px, and no actor of another group within APART px."""
        for who in SPOTS:
            spots = {n: (x, y) for n, x, y, _ in self.spots_of(who)}
            groups = GROUPS[who]
            self.assertEqual(sorted(spots), sorted(n for m in groups.values() for n in m), who)
            self.assertEqual(len([n for m in groups.values() for n in m]), len(spots), who)   # no actor twice
            self.assertGreaterEqual(len(groups), 2, who)
            for g, members in groups.items():
                for name in members:
                    mates = [m for m in members if m != name]
                    others = [n for n in spots if n not in members]
                    if mates:
                        self.assertLessEqual(min(dist(spots[name], spots[m]) for m in mates), NEAR, (who, name))
                    self.assertGreaterEqual(min(dist(spots[name], spots[n]) for n in others), APART, (who, name, g))

    def test_text_records_are_the_owners_words_in_four_line_boxes(self):
        lines_144 = set()
        for i, (portrait, boxes) in zip((5, 6, 8, 9, 10, 11, 12), SPEECH_GP + SPEECH_V):
            at = self.word(i) - ROM_BASE
            nxt = {5: 6, 6: 7, 8: 9, 9: 10, 10: 11, 11: 12, 12: 15}[i]
            self.assertEqual(self.rom[at:at + 4], bytes([nxt, 0, 1, portrait]), f"record {i}")
            end = self.rom.index(b"\0", at + 4)
            body = self.rom[at + 4:end]
            self.assertEqual(body, b"\x0b".join(b.encode("ascii") for b in boxes), f"record {i}")
            for box in body.split(b"\x0b"):
                self.assertNotIn(box[:1], (b"!", b"@", b"#", b"^"), f"record {i}")
                lines = dialog_wrap(self.base, box)
                self.assertLessEqual(len(lines), BOX_LINES, f"record {i}: {lines}")
                self.assertTrue(all(w <= DIALOG_WIDTH for _, w in lines), f"record {i}")
                lines_144 |= {t for t, w in lines if w == DIALOG_WIDTH}
        self.assertEqual(lines_144, EXACT_144)                               # one more char would wrap them


class ClashTests(unittest.TestCase):
    """relay_cooldown writes ext 70's word in the vanilla table: it must run first, and after us it refuses."""

    def test_relay_cooldown_before_is_carried_into_the_copy(self):      # r40: relay_cooldown is in main
        b = built()
        wrapper = b["alloc_before"].notes["relay_cooldown"]["wrapper"]
        self.assertEqual(b["notes"]["ext_changed"], [70])
        self.assertEqual(u32(b["rom"], b["notes"]["ext_table"] + 4 * 70), wrapper + ROM_BASE + 1)

    def test_relay_cooldown_after_refuses(self):
        from patches import relay_cooldown
        names = log2_build.read_build_list(TRIAL_LIST)
        r39 = names[:names.index("relay_cooldown")]             # main before relay_cooldown (r39)
        rom, alloc = log2_build.assemble(log2_build.BASE, r39 + ["chapter_cards"])
        snap = bytes(rom)
        with self.assertRaisesRegex(ValueError, "also written by chapter_cards"):
            relay_cooldown.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)


# ===== BF card look (v3) =====

def bf_string(bf: bytes, i: int) -> str:
    a, t = u32(bf, BF_STRINGS + 4 * i) - ROM_BASE, ""
    while struct.unpack_from("<H", bf, a + 2 * len(t))[0]:
        t += chr(struct.unpack_from("<H", bf, a + 2 * len(t))[0])
    return t


class BfLookTests(unittest.TestCase):
    def test_bf_draws_card_titles_at_run_time_from_its_string_table(self):
        bf = chapter_cards.bf_rom()
        self.assertEqual([bf_string(bf, i) for i in (1452, 1453, 1464, 1465)],
                         ["Chapter 2", "Great Saiyaman", "Chapter 8", "Janemba"])
        ext178 = [t for _, t in listing(bf, 0x08003030, 40)]
        self.assertIn("bl 0x802bfbc", ext178)
        draw = [t for _, t in listing(bf, 0x0802BFBC, 24)]
        for want in ("ldr r1,=0x0806bce8", "ldr r6,=0x08753a18", "bl 0x803ffe8", "bl 0x802becc"):
            self.assertIn(want, draw)
        self.assertEqual((u32(bf, 0x753A1C), u32(bf, 0x7548DC)), (0x087548DC, 0x08753A20))   # font, glyph table

    def test_bf_card_palettes_are_the_ones_bf_loads(self):
        bf = chapter_cards.bf_rom()
        self.assertEqual((u32(bf, 0x2CAAC), u32(bf, 0x2CAB0)), (0x0805632C, 0x0805652C))   # to 0x05000000, +0x200

    def test_module_draws_bf_chapter_2_as_the_screenshot_check_pinned(self):
        bf = chapter_cards.bf_rom()
        for text, w in BF_LINE_WIDTHS.items():
            self.assertEqual(chapter_cards.text_width(bf, text), w, text)
        px = bytearray(chapter_cards.backdrop(bf)[0])
        chapter_cards.draw_line(px, bf, bf_string(bf, 1452), 65)
        chapter_cards.draw_line(px, bf, bf_string(bf, 1453), 85)
        self.assertEqual(hashlib.sha1(px).hexdigest(), BF_CH2_PX_SHA1)

    def test_blank_bf_punctuation_uses_our_glyphs_and_other_blanks_refuse(self):
        bf = chapter_cards.bf_rom()

        def bf_columns(ch: str) -> bytes:                                       # glyph table 0x08753A20
            g = struct.unpack_from("<H", bf, 0x753A20 + 2 * ord(ch))[0]
            w = struct.unpack_from("<H", bf, 0x753A20 + 2 * g)[0]
            return bf[0x753A20 + 2 * g + 2:0x753A20 + 2 * g + 2 + 2 * w]

        for ch in ".'":
            self.assertFalse(any(bf_columns(ch)), ch)                          # blank in BF
            self.assertTrue(any(chapter_cards._glyph(bf, ch)[1]), ch)
        self.assertFalse(any(chapter_cards._glyph(bf, " ")[1]))
        with self.assertRaises(ValueError):
            chapter_cards._glyph(bf, "Ā")                                  # BF draws < 0xFF from this table
        blanks = [chr(c) for c in range(0x21, 0x7F) if not any(bf_columns(chr(c)))]
        for ch in blanks:
            if ch not in ".'":
                with self.assertRaises(ValueError, msg=ch):
                    chapter_cards._glyph(bf, ch)


class DataChunkTests(unittest.TestCase):
    """v3 fix: a data chunk is refused only for a real pointer word, never for packed data (beam_struggle)."""

    def setUp(self):
        self.rom, self.alloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        probe, palloc = padded(), Allocator(log2_build.ROM_SIZE, log2_build.EXPANSION)
        chapter_cards.apply(probe, palloc)
        self.first = palloc.notes["chapter_cards"]["cards"][0]       # where the first data chunk lands

    def test_packed_data_naming_a_data_chunk_does_not_refuse(self):
        site = 0x910C94
        self.rom[site:site + 8] = struct.pack("<II", 0x08926D91, ROM_BASE + self.first + 0x10)
        self.alloc.notes["beam_struggle"] = {"sites": [(site, 8, "packed beam data")]}
        chapter_cards.apply(self.rom, self.alloc)
        self.assertIn("chapter_cards", self.alloc.notes)

    def test_a_pool_word_naming_a_data_chunk_refuses(self):
        site = 0x910C94                                              # ldr r0,[pc,#4] ; bx lr ; pool
        code = struct.pack("<HHI", 0x4801, 0x4770, 0) + struct.pack("<I", ROM_BASE + self.first + 0x10)
        self.rom[site:site + len(code)] = code
        self.alloc.notes["other_module"] = {"sites": [(site, len(code), "code")]}
        snap = bytes(self.rom)
        with self.assertRaises(ValueError):
            chapter_cards.apply(self.rom, self.alloc)
        self.assertEqual(bytes(self.rom), snap)

    def test_a_word_in_a_vanilla_site_naming_a_data_chunk_refuses(self):
        site = 0x1000
        self.rom[site:site + 4] = struct.pack("<I", ROM_BASE + self.first)
        self.alloc.notes["other_module"] = {"sites": [(site, 4, "pool word")]}
        with self.assertRaises(ValueError):
            chapter_cards.apply(self.rom, self.alloc)


# ===== song port =====

def decode(rom: bytes, rec: int) -> dict:
    """Independent read of a song (format restated from the report): events per order entry, as text tuples."""
    pats, ords, sdir, masks = (u32(rom, rec - ROM_BASE + 4 * k) for k in range(4))
    order, i = [], ords - ROM_BASE
    while rom[i] != 0xFF:
        order.append(rom[i])
        i += 1
    mt = rom[masks - ROM_BASE:masks - ROM_BASE + 14]
    out = []
    for p in order:
        i = u32(rom, pats - ROM_BASE + 4 * p) - ROM_BASE
        rows, kept = rom[i], {}
        i += 1
        for row in range(rows):
            while rom[i]:
                code, ch = rom[i] >> 4, rom[i] & 15
                i += 1
                if code == 0:
                    kept[ch] = rom[i]
                    i += 1
                m = kept[ch] if code < 2 else mt[code - 2]
                ev = [row, ch]
                for bit, n in ((0, 1), (1, 1), (2, 1), (3, 2)):
                    ev.append(rom[i:i + n].hex() if m >> bit & 1 else None)
                    i += n if m >> bit & 1 else 0
                out.append(tuple(ev))
            i += 1
    tempo_speed = rom[rec - ROM_BASE + 0x10:rec - ROM_BASE + 0x12]
    return {"order": order, "events": out, "sdir": sdir, "tempo_speed": tempo_speed}


class SongPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.n = b["rom"], b["notes"]
        cls.bf = BF_PATH.read_bytes()
        cls.rec = ROM_BASE + cls.n["song"]["record"]

    def test_bf_record_is_the_card_song(self):
        self.assertEqual(struct.unpack_from("<5I", self.bf, BF_SONG37 - ROM_BASE), BF_SONG37_RECORD)
        self.assertEqual(self.bf[0x79B011:0x79B015].hex(), "00250223")                # card script: push 37 ; ext 35

    def test_ported_song_decodes_to_the_bf_song(self):
        new, old = decode(self.rom, self.rec), decode(self.bf, BF_SONG37)
        self.assertEqual(new["order"], old["order"])
        self.assertEqual(new["events"], old["events"])
        self.assertEqual(new["tempo_speed"], bytes([115, 4]))
        self.assertGreater(len(new["events"]), 100)

    def test_used_samples_are_bf_bytes_and_entries_keep_their_fields(self):
        new_dir, old_dir = u32(self.rom, self.rec - ROM_BASE + 8), BF_SONG37_RECORD[2]
        used = sorted({int(e[3], 16) for e in decode(self.bf, BF_SONG37)["events"] if e[3] is not None})
        self.assertEqual(used, BF_SONG37_INSTRUMENTS)
        for i in used:
            ne = self.rom[new_dir - ROM_BASE + 12 * i:new_dir - ROM_BASE + 12 * i + 12]
            oe = self.bf[old_dir - ROM_BASE + 12 * i:old_dir - ROM_BASE + 12 * i + 12]
            self.assertEqual(ne[4:], oe[4:], f"entry {i}")                     # flags, loop, length, rate
            length = struct.unpack_from("<H", oe, 8)[0]
            a, b = u32(ne, 0) - ROM_BASE, u32(oe, 0) - ROM_BASE
            self.assertEqual(self.rom[a:a + length + 16], self.bf[b:b + length + 16], f"sample {i}")

    def test_unused_entries_are_silent_and_every_pointer_stays_in_the_port(self):
        lo, hi = self.n["song"]["record"], self.n["song"]["record"] + self.n["song_size"]
        new_dir = u32(self.rom, self.rec - ROM_BASE + 8) - ROM_BASE
        for k in range(4):
            self.assertTrue(lo <= u32(self.rom, self.rec - ROM_BASE + 4 * k) - ROM_BASE < hi)
        for i in range(max(BF_SONG37_INSTRUMENTS) + 1):
            ptr, flags_loop, len_rate = struct.unpack_from("<3I", self.rom, new_dir + 12 * i)
            self.assertTrue(lo <= ptr - ROM_BASE < hi, f"entry {i}")
            if i not in BF_SONG37_INSTRUMENTS:
                self.assertEqual((flags_loop, len_rate & 0xFFFF), (0, 16))
                self.assertEqual(self.rom[ptr - ROM_BASE:ptr - ROM_BASE + 16], bytes(16))

    def rows(self, rom: bytes, decoder: int, rec: int, n: int) -> list:
        """Channel row fields (+0x50..+0x5F of 15 channels) after each of n row-decoder calls, run as ROM code."""
        cpu, player, out = Cpu(rom), 0x03001000, []
        cpu.store(player + 0, 1, 1)                                             # music_play's start state
        cpu.store(player + 2, 1, 1)
        cpu.store(player + 0xC, 4, rec)
        cpu.store(player + 0x10, 4, 0xFFFFFFFF)
        for _ in range(n):
            cpu.r[0], cpu.r[13], cpu.r[14] = player, STACK, RET
            self.assertEqual(cpu.run(decoder, {RET & ~1: "done"}, limit=20000), "done")
            out.append(b"".join(cpu.ram[0x03][0x1018 + 0x60 * k + 0x50:0x1018 + 0x60 * k + 0x60] for k in range(15)))
        return out

    def test_lg_row_decoder_reads_the_port_as_bf_reads_the_original(self):
        n = 96 * 2 + 3                                                          # the 96-row pattern, its loop, and more
        new = self.rows(self.rom, 0x08020820, self.rec, n)
        old = self.rows(self.bf, 0x0803EEE4, BF_SONG37, n)
        self.assertEqual(new, old)

    def test_the_two_players_read_songs_the_same_way(self):
        lg = log2_build.BASE.read_bytes()
        same = ((0x20820, 0x3EEE4, 0xEC, "row decoder"), (0x1FE20, 0x3E4E4, 0x90, "note trigger"),
                (0x7FC93C, 0x7B6724, 480, "note table"))
        for a, b, n, name in same:
            self.assertEqual(lg[a:a + n], self.bf[b:b + n], name)
        lg_fx = [u32(lg, 0x7FCB1C + 4 * k) for k in range(32)]
        bf_fx = [u32(self.bf, 0x7B6904 + 4 * k) for k in range(32)]
        self.assertEqual(len(set(lg_fx)), len(set(bf_fx)))                     # the same handler sharing pattern
        self.assertEqual([lg_fx.index(x) for x in lg_fx], [bf_fx.index(x) for x in bf_fx])


if __name__ == "__main__":
    unittest.main()
