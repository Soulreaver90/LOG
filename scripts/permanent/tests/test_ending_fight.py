r"""
test_ending_fight.py - Tests for patches.ending_fight (trial 2026-11-05): the ending's scripted kill of
                       Imperfect Cell becomes a real player fight, with Trunks as the player and the
                       vanilla ki blast still finishing Cell.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_ending_fight.py -v
Builds build_list_trial_ending.txt in memory: "before" = the dev master (r41) plus battle_arena, "rom" =
before plus ending_fight. Scripts are decoded with test_cellgames_ssj's decoder. Every expected value is
restated from docs\tasks\2026-11-05-ending-fight-1\brief.md, docs\tasks\2026-11-05-ending-arena\brief.md,
the design, and the base bytes read in scripts\one-time\2026-11-05-ending-fight-1\01_probe.txt and
03_slices.txt. Nothing is imported from the patch module except apply() and the record builders the
design lives in. The arena map, its item and its enemy belong to test_battle_arena.py.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
import log_paths
from patches import ending_fight
from scene.scene_lib import record_end
from tests.test_cellgames_ssj import diff, ext_sequence

# ===== constants (brief, design, base reads) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_ending.txt"
TABLE, TABLE_WORDS = 0x3B8140, 27
FIGHT_WORD = TABLE + 4 * 23
REC23, REC23_LEN = 0x3B8016, 0xFF
REC23_SHA1 = "96d07a4392ea2f35f876503e45cf0f28df20a8ec"
REC24, REC25 = 0x3B8116, 0x3B813A
BLAST_AT, BLAST_LEN = 0x3B80AC, 0x2B
TAIL_AT, TAIL_LEN = 0x3B80D7, 0x3D
EVENT_RUNNER = 0x080106B3
FREE_SPOT = 0xEF0000                                    # inside the allocator's region, far past its cursor
EXPANSION = (0x800000, 0xF00000)

PLAYER, TRUNKS, SSJ_TRUNKS, NPC_TRUNKS, CELL = 0, 3, 133, 132, 28
BASE_TRUNKS = NPC_TRUNKS     # set 132 under its other hat: the body record A gives the PLAYER
TRUNKS_SPOT, CELL_SPOT = (248, 568), (244, 504)   # where the CONVERSATION leaves them (his v3 states)
TRUNKS_START, CELL_START = (248, 624), (288, 392)  # map 6,1 items 5 and 6: where each walk STARTS
V3_SPOTS = ((244, 616), (248, 680))    # the v3 pair, 112 px lower: "the start still transitions both"
VANILLA_SPOT = (248, 568)              # the vanilla tail's own respawn point, in bytes we only DELETE
GRASS_SPOT = (136, 432)                # where v6's load_map_at put the player: a grass strip, the defect
ARENA_ZONE, ARENA_AREA, ENEMY_INDEX = 6, 100, 1
MAP_RELOAD = (ARENA_ZONE, ARENA_AREA, 1) + TRUNKS_START
PLACE_OPS = (62, 51, 136, 35)          # every op that sets an actor's position; F may carry none of them
VIEW = (TRUNKS_SPOT[0] - 112, (CELL_SPOT[1] + TRUNKS_SPOT[1]) // 2 - 80, 40)  # both fighters in frame
VANILLA_WAITS = (60, 120, 100)                     # record 13's own three waits, which IT still keeps
# THE RECORD USES THE HOUSE VALUES (the owner, 2026-11-08: "why are we reinvintng the wheel, the
# game has loads of transitions, find out the length of time, etc, and thats what we use"). Bible
# B1017 counts every vanilla fade: 120 is the commonest `fade_out` (17 of 44) and the commonest
# `fade_in` (12 of 28), and 26 of the 28 records carrying both run the same number in each. Bible
# B2170 decodes a vanilla map-load transition op for op and it spends NO settle wait between the
# load and the fade in: the staging sits there instead. So the copy opens on vanilla's own wait(60),
# fades out, loads, stages, parks the camera, and fades back in in record A2.
# Not one byte of the VANILLA record moves, and the module still reads and checks its opening pair.
# THE TWO FADES ARE NOT PINNED TO A NUMBER THIS PROJECT PICKED. They are read out of the BASE ROM
# by vanilla_transition(), from rom:0x3E424A, vanilla's own fastest map-load transition. The owner
# asked "what is the normal transition length in vanilla???" and then said twice more that this one
# was still too long, so the test asks the ROM instead of holding a constant.
OPEN_WAIT = 60


def vanilla_transition() -> dict:
    """The fade pair of vanilla's fastest map-load transition, read out of the BASE ROM.

    `ending_fight.FAST_TRANSITION` names the record. `waits` totals every blocking wait between the
    two fades, which is the number the census shows vanilla usually spends nothing on."""
    rom = log2_build.BASE.read_bytes()
    at = ending_fight.FAST_TRANSITION
    seen, out = ext_sequence(rom, at), {"out": None, "in": None, "waits": 0}
    for n, args in seen:
        if n == 40 and out["out"] is None:
            out["out"] = args[0]
        elif n == 69 and out["out"] is not None and out["in"] is None:
            out["waits"] += args[0]
        elif n == 41 and out["out"] is not None and out["in"] is None:
            out["in"] = args[0]
    return out


VANILLA_FADE = vanilla_transition()
FADE_OUT, FADE_IN = VANILLA_FADE["out"], VANILLA_FADE["in"]
ARRIVED = VANILLA_WAITS[2]
REFILL, HP_REFILL, KI_REFILL = 5000, 109, 110      # bible B0576, and chamber_spar's own pair
# The caption the owner asked for, section 2 of the design, and the two music cues of sections 2 and 3.
CAPTION_INDEX, REVEAL_INDEX = 24, 25
CAPTION_WORD, REVEAL_WORD = TABLE + 4 * CAPTION_INDEX, TABLE + 4 * REVEAL_INDEX
CAPTION_TEXT, CAPTION_AT = b"@^Three years later...", 0x3B8610
CAPTION_MUSIC, FIGHT_MUSIC = 42, 28
CAPTION_SPOT = (TRUNKS_START[0], TRUNKS_START[1] + 40)    # 24 px below the view, for the caption
TRUNKS_UP, CELL_DOWN = 24, 8                       # bible B0246: how far each set reaches

MOVED_WORDS = (12, 13, 22, 23, 24, 25)             # every ending word this module repoints
DIALOG_FONT, DIALOG_WIDTH, BOX_LINES = 0x2CC64, 0x90, 4   # bible C4S and B2095: 144 px, 4 lines

# Record A, ending word 13: the arena loads HERE, under vanilla's own fade, and the player is given the
# BASE Trunks body before it so the load builds that body. The form is 132 and not 133 because of the
# owner's flow of 2026-11-07, "Cell: Trunks starts NOT Super Saiyan"; the two android fights before this
# record still run in 133. Vanilla's wait(60) and fade_out(180) open it unchanged, vanilla's wait(120)
# settles the load under the black, and vanilla's wait(100) ends it.
# Record A now ENDS on the caption, so the arrival is two records. A loads the arena, parks the view on
# an empty corner and lights the sprites again; the caption box runs; A2 frames the pair and reveals it.
ARRIVE_OPS = [(69, (OPEN_WAIT,)), (40, (FADE_OUT,)),
              (73, (TRUNKS, BASE_TRUNKS)), (70, (TRUNKS,)),
              (HP_REFILL, (TRUNKS, REFILL)), (KI_REFILL, (TRUNKS, REFILL)),
              (39, MAP_RELOAD),
              (86, (0,)), (62, (PLAYER,) + CAPTION_SPOT),
              (49, (CAPTION_MUSIC,)), (31, VIEW), (45, ())]
# Record A2 moves nobody and gives no HUD back. The player is still on CAPTION_SPOT, wholly below the
# parked view, and he WALKS up into frame, which is the vanilla NPC's own entrance and the owner's
# finding 3. The HUD comes back at word 23, where every other fight in the game brings it back, which
# is his finding 4: "it should appear whent he dialgue ends".
REVEAL_OPS = [(41, (FADE_IN,)), (53, (PLAYER,) + TRUNKS_SPOT), (69, (ARRIVED,))]
# Record F, ending word 23: four ops, and the owner named the model himself. Piccolo against Android 17,
# rom:0x3E47DC, runs ext104(9,1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0). "There should
# not be a fade at all after the diague! Dialogue ends fight begins with a camera pan to the user and the
# hud appearing, like every single fight int he game." The bar is ext 85, not ext 90, because ext 90's
# two extra values are a display segment for one round of a multi-round boss and this fight is one round.
PICCOLO_RECORD = 0x3E47DC
FIGHT_OPS = [(49, (FIGHT_MUSIC,)),
             (104, (CELL, ENEMY_INDEX)), (85, (CELL,)), (86, (1,)), (33, (PLAYER,))]
# The 17/18 scene is VANILLA (the owner's scope: "the scene against 17/18, which we are NOT doing at this
# time"). These four words name the four records that carry every set 133 actor op of that scene. They
# must not move and the records must stay byte for byte. CONV_VANILLA_OPS is what each record still says.
# Word 13 is NOT here: it straddles the boundary, so it is repointed at a copy and checked on its own.
CONV_WORDS = (4, 6, 8, 11)
CONV_VANILLA_OPS = [(51, (SSJ_TRUNKS, 496, 504)), (55, (SSJ_TRUNKS, 1)),
                    (96, (SSJ_TRUNKS, 11, 100)), (96, (SSJ_TRUNKS, 11, 100)),
                    (96, (SSJ_TRUNKS, 9, 100)), (96, (SSJ_TRUNKS, 9, 100)),
                    (55, (SSJ_TRUNKS, 0))]
NPC_TRUNKS_KEPT = [(55, (NPC_TRUNKS, 0)), (57, (NPC_TRUNKS, 9)), (52, (NPC_TRUNKS,))]
REC13, REC13_SHA1 = 0x3B7E4A, "9da3bdb83ae64c84f6a61d02abf00a83176accd9"
ARRIVE_WORD = TABLE + 4 * 13
CONV_LOAD = (35, (6, 1, 1, 136, 432))  # vanilla word 13's own load, which the copy must NOT carry
# The two camera parks. Record A and record K park the SAME point and differ only in speed, and the
# difference is deliberate. `ext 31` blocks for distance/speed + 1 frames (bible B0766). Record A
# parks from a position the map load has just set, so its pan is a known short one and speed 2 is
# what the owner approved. Record K parks from wherever the FOLLOW camera left the view when the
# enemy died, which is wherever the player was standing, and once the plateau carries round 2 that
# record runs on a 1280 x 1280 map: up to about 770 px, about 385 frames, 6.4 seconds of black at
# speed 2. Speed 40 makes it about 5 frames. Both pushes are one byte, so no record changes length.
VIEW_POINT = (TRUNKS_SPOT[0] - 112, (CELL_SPOT[1] + TRUNKS_SPOT[1]) // 2 - 80)
ARRIVE_SPEED, DEATH_SPEED = 40, 40

# Record K's head, before the two vanilla slices.
DEATH_HEAD = [(88, ()), (86, (0,)), (57, (CELL, 3)), (69, (60,)), (40, (30,)),
              (62, (PLAYER,) + TRUNKS_SPOT), (55, (PLAYER, 1)),
              (52, (CELL,)), (51, (CELL,) + CELL_SPOT), (55, (CELL, 0)), (57, (CELL, 3)),
              (31, VIEW_POINT + (DEATH_SPEED,)), (41, (30,))]
# The two vanilla slices of record 23 the death record reuses, and the only edit each one carries.
BLAST_FIRST = (63, ())                                  # the third attack group opens with ext 63
ATTACKER_WAS, ATTACKER_NOW = (96, (SSJ_TRUNKS, CELL, 100)), (96, (PLAYER, CELL, 100))
FACE_WAS, FACE_NOW = (55, (SSJ_TRUNKS, 0)), (55, (PLAYER, 0))
TAIL_DROPPED = [(57, (SSJ_TRUNKS, 21)), (52, (SSJ_TRUNKS,)),
                (51, (NPC_TRUNKS,) + VANILLA_SPOT), (52, (NPC_TRUNKS,))]

_CACHE = {}


def u32(rom: bytes, off: int) -> int:
    return struct.unpack_from("<I", rom, off)[0]


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("ending_fight")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc),
                      arena=copy.deepcopy(alloc.notes["battle_arena"]))
        log2_build.apply_patches(rom, alloc, ["ending_fight"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["ending_fight"])
    return _CACHE


def staged() -> tuple:
    """(rom, alloc) exactly as ending_fight receives them: the dev master plus battle_arena."""
    b = built()
    return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])


def body(rom: bytes, rec: int) -> list:
    """[(ext n, args)] of a type 0 record, base ops dropped: the shape the design is written in."""
    return ext_sequence(rom, rec)


def arrival(b: dict) -> list:
    """Record A then record A2, as one op list: the arrival the caption box now sits inside."""
    return body(b["rom"], b["notes"]["arrive"]) + body(b["rom"], b["notes"]["reveal"])


def text_of(rom: bytes, rec: int) -> bytes:
    """The text of a type 1 record, box breaks and all."""
    return bytes(rom[rec + 4:bytes(rom).index(b"\x00", rec + 4)])


def dialog_wrap(rom: bytes, box: bytes) -> list:
    """Lines of one box as the dialog line counter breaks them (bible C4S: past 144 px, at the last
    space). The same model test_chapter_cards uses, which reproduces every vanilla box."""
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


def vanilla(b: dict) -> list:
    return body(b["before"], REC23)


def vanilla_blast(b: dict) -> list:
    """The third attack group of the vanilla scripted kill: the last ext 63 to its ext 64."""
    ops = vanilla(b)
    start = len(ops) - 1 - ops[::-1].index(BLAST_FIRST)
    return ops[start:start + ops[start:].index((64, ())) + 1]


def vanilla_tail(b: dict) -> list:
    ops = vanilla(b)
    start = len(ops) - 1 - ops[::-1].index(BLAST_FIRST)
    return ops[start + ops[start:].index((64, ())) + 1:]


def blast_ops(b: dict) -> list:
    got = body(b["rom"], b["notes"]["death"])
    start = len(got) - 1 - got[::-1].index(BLAST_FIRST)
    return got[start:start + got[start:].index((64, ())) + 1]


def tail_ops(b: dict) -> list:
    got = body(b["rom"], b["notes"]["death"])
    start = len(got) - 1 - got[::-1].index(BLAST_FIRST)
    return got[start + got[start:].index((64, ())) + 1:]


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


# ===== the build list =====

class ListTests(unittest.TestCase):
    def test_trial_list_is_the_dev_master_plus_the_two_trial_lines(self):
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual(log2_build.read_build_list(TRIAL_LIST), dev + ["battle_arena", "ending_fight"])

    def test_the_module_is_in_no_master_list(self):
        for path in (log2_build.BUILD_LIST, log2_build.DEV_LIST):
            for name in ("battle_arena", "ending_fight"):
                self.assertNotIn(name, log2_build.read_build_list(path))


# ===== fail closed =====

class FailClosedTests(unittest.TestCase):
    def test_the_arena_notes_are_required(self):
        """The record loads map 6,100 and the enemy is the arena's own item, so there is nothing to
        build without battle_arena. The module must say so rather than write a half fight."""
        rom, alloc = staged()
        alloc.notes.pop("battle_arena")
        snap = bytes(rom)
        with self.assertRaises(ValueError) as caught:
            ending_fight.apply(rom, alloc)
        self.assertIn("battle_arena", str(caught.exception))
        self.assertEqual(bytes(rom), snap)

    def test_second_run_raises(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["ending_fight"] = {}
        with self.assertRaises(ValueError):
            ending_fight.apply(rom, alloc)
        rom2 = bytearray(b["rom"])                       # ending word 23 is no longer vanilla either
        with self.assertRaises(ValueError):
            ending_fight.apply(rom2, copy.deepcopy(b["alloc_before"]))
        self.assertEqual(bytes(rom2), b["rom"])

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        sites = [rec + 4 for _, rec, _ in ending_fight.VANILLA_CONVERSATION.values()]
        for off in (FIGHT_WORD, FIGHT_WORD + 3, REC23, REC23 + 0x98, REC23 + REC23_LEN - 1,
                    TABLE + 4 * 24, TABLE + 4 * 26, b["arena"]["event"], b["arena"]["item"] + 0x14,
                    *[TABLE + 4 * k for k in CONV_WORDS], *sites, 0x3B7C1C + 4, 0x3B7E4A + 4):
            rom, alloc = staged()
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                ending_fight.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap, f"rom:0x{off:X} wrote before it refused")

    def test_a_second_namer_of_the_scripted_kill_refuses(self):
        rom, alloc = staged()
        rom[FREE_SPOT:FREE_SPOT + 4] = struct.pack("<I", REC23 + ROM_BASE)
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            ending_fight.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_a_module_that_writes_a_guarded_site_refuses(self):
        for site in ((FIGHT_WORD + 2, 1, "other"), (REC23 + 0x90, 4, "other"), (REC24 + 4, 4, "other")):
            rom, alloc = staged()
            alloc.notes["other"] = {"sites": [site]}
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(site)):
                ending_fight.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)


# ===== the fight start =====

class ArriveTests(unittest.TestCase):
    """Record A, ending word 13. The whole of v7 is that the arena loads HERE and not at the fight."""

    def test_word_13_names_the_new_record_and_the_vanilla_record_is_untouched(self):
        b = built()
        self.assertEqual(u32(b["rom"], ARRIVE_WORD), b["notes"]["arrive"] + ROM_BASE)
        self.assertEqual(u32(b["before"], ARRIVE_WORD), REC13 + ROM_BASE)
        length = record_end(b["before"], REC13) - REC13
        self.assertEqual(b["rom"][REC13:REC13 + length], b["before"][REC13:REC13 + length])
        self.assertEqual(hashlib.sha1(b["rom"][REC13:REC13 + length]).hexdigest(), REC13_SHA1)

    def test_record_a_runs_the_brief_in_order(self):
        b = built()
        self.assertEqual(body(b["rom"], b["notes"]["arrive"]), ARRIVE_OPS)

    def test_record_a2_finishes_the_arrival_in_order(self):
        b = built()
        self.assertEqual(body(b["rom"], b["notes"]["reveal"]), REVEAL_OPS)

    def test_the_opening_pair_is_vanillas_wait_and_vanillas_fastest_fade(self):
        """The copy opens wait(60) ; fade_out(30). The wait is vanilla's own beat. The fade is read
        out of the BASE ROM, from rom:0x3E424A, vanilla's own fastest map-load transition, so no
        number here is one this project picked. The MODULE still reads and checks the vanilla pair
        before it writes, so the 17/18 boundary cannot drift, and the vanilla record keeps every
        byte."""
        b = built()
        self.assertEqual(VANILLA_FADE, {"out": 30, "in": 30, "waits": 0},
                         f"rom:0x{ending_fight.FAST_TRANSITION:X} is no longer the fast transition")
        self.assertEqual(b["before"][0x3B7E4D:0x3B7E55],
                         ending_fight.wait(60) + ending_fight.fade_out(180))
        self.assertEqual(body(b["rom"], b["notes"]["arrive"])[:2],
                         [(69, (OPEN_WAIT,)), (40, (FADE_OUT,))])
        self.assertEqual(OPEN_WAIT, VANILLA_WAITS[0], "the opening beat is vanilla's own")
        self.assertEqual(ending_fight.HEAD_FADE, FADE_OUT, "the cover is vanilla's own fade_out")
        self.assertEqual(ending_fight.REVEAL, FADE_IN, "the reveal is vanilla's own fade_in")

    def test_the_arena_loads_under_the_vanilla_fade(self):
        """The owner's v6 finding: "There should not be a fade at all after the diague!". The load is
        what moves, not the cover. A map load replaces the camera in one frame, so it needs a cover,
        and vanilla record 13 already carries one."""
        ops = arrival(built())
        self.assertLess(ops.index((40, (FADE_OUT,))), ops.index((39, MAP_RELOAD)))
        self.assertLess(ops.index((39, MAP_RELOAD)), ops.index((41, (FADE_IN,))))
        self.assertEqual([op for op in ops if op[0] in (35, 36, 38, 39)], [(39, MAP_RELOAD)])
        self.assertNotIn(CONV_LOAD, ops, "the vanilla ext 35 load does not come along")

    def test_the_load_is_ext_39_because_only_ext_38_and_39_build_a_player(self):
        """ext 35's handler Map_LoadFromQueue @0x08009852 reaches Map_Load @0x0800C664, which never
        calls the player constructor @0x080086D4. Only sub_0800C584 does, and only ext 38 and ext 39
        reach it. Bible row 1579 once said otherwise and that error cost a build."""
        ops = body(built()["rom"], built()["notes"]["arrive"])
        self.assertIn((39, MAP_RELOAD), ops)
        self.assertEqual([op for op in ops if op[0] == 35], [])

    def test_the_form_and_the_leader_are_set_in_front_of_the_load(self):
        """ext 70 writes the party roster, but the block that installs the leader's BODY is guarded
        (sub_0800A680: CMP r4,#0 then BEQ on Sprite_CurrentDirectory 0x03001FA8, zero all through the
        ending), so the map load is what builds the player. ext 73 goes first because appearance_revert
        @0x08003ED4 skips the record whose index equals the leader byte set_leader has just written."""
        ops = body(built()["rom"], built()["notes"]["arrive"])
        self.assertLess(ops.index((73, (TRUNKS, BASE_TRUNKS))), ops.index((70, (TRUNKS,))))
        self.assertLess(ops.index((70, (TRUNKS,))), ops.index((39, MAP_RELOAD)))

    def test_the_load_puts_the_player_where_the_npc_trunks_started(self):
        """The x and y of ext 39 are the PLAYER's position: sub_08009A88 hands the pair to
        sub_0800C584, which passes the SAME pair to the constructor at loc_0800C608. TRUNKS_START is
        map 6,1 item 5's own spot, where the vanilla map load builds the NPC Super Saiyan Trunks, so
        the player then walks the walk vanilla gave that NPC."""
        b = built()
        load = next(op for op in body(b["rom"], b["notes"]["arrive"]) if op[0] == 39)
        self.assertEqual(load[1][3:], TRUNKS_START)
        self.assertEqual(TRUNKS_START, tuple(b["arena"]["trunks_start"]))
        self.assertNotEqual(load[1][3:], GRASS_SPOT)
        self.assertNotIn(load[1][3:], V3_SPOTS)

    def test_the_player_walks_the_npcs_own_path(self):
        """His call on 2026-11-05: "have it follow the same path as the NPC, no hand off needed". The
        vanilla record walks set 133 from (248,624) to (248,568); the copy walks set 0 the same way."""
        b = built()
        ops = arrival(b)
        self.assertIn((53, (PLAYER,) + TRUNKS_SPOT), ops)
        self.assertIn((53, (SSJ_TRUNKS,) + TRUNKS_SPOT), body(b["before"], REC13))
        self.assertEqual([op for op in ops if op[1][:1] == (SSJ_TRUNKS,)], [])
        self.assertGreater(TRUNKS_START[1], TRUNKS_SPOT[1], "the walk goes up the courtyard")

    def test_the_view_is_parked_on_the_pair_before_the_screen_comes_back(self):
        """Piccolo's record 0 parks camera(152,96,3) and the whole talk runs on it; record F's
        camera_follow(0) is then the pan the owner asked for. ext 31 takes the view TOP LEFT (bible
        row 1000) and it BLOCKS (sub_0800977A publishes the move, then runs Handler_RunScoped
        @0x0801F2F4 until it reports done), so the travel finishes under the black."""
        ops = arrival(built())
        self.assertIn((31, VIEW), ops)
        self.assertLess(ops.index((31, VIEW)), ops.index((41, (FADE_IN,))))
        self.assertLessEqual(VIEW[0], CELL_SPOT[0])
        self.assertLessEqual(VIEW[1], CELL_SPOT[1])
        self.assertLess(CELL_SPOT[0], VIEW[0] + 240)
        self.assertLess(TRUNKS_SPOT[1], VIEW[1] + 160, "both fighters are inside the 240x160 view")

    def test_the_record_fades_back_in_itself_because_ext_39_carries_no_fade(self):
        """ext 35's handler runs @0x0802664C and the blocking loop twice, once each side of the load,
        so vanilla needed no fade_in. ext 39's sub_08009A88 has neither call, so without this op the
        screen would stay black. 180 is vanilla's own pairing: 26 of the 28 records that carry both ops run
        the same number in each, and 3 of the 4 that fade out at 180 fade back in at 180."""
        ops = arrival(built())
        self.assertIn((41, (FADE_IN,)), ops)
        self.assertEqual(FADE_OUT, next(a[0] for n, a in ops if n == 40))
        self.assertLess(ops.index((41, (FADE_IN,))), ops.index((53, (PLAYER,) + TRUNKS_SPOT)))

    def test_there_is_no_settle_wait_because_vanilla_spends_none(self):
        """Bible B2170 decodes a vanilla map-load transition op for op and the load is followed
        straight away by its staging, with the camera last and the fade in after it. B0748 and B0877
        say the same from two more records. So this record holds exactly two waits, vanilla's own
        opening beat and vanilla's own wait after the walk, and the staging fills the space the
        settle used to spend."""
        ops = arrival(built())
        self.assertEqual([a[0] for n, a in ops if n == 69], [OPEN_WAIT, ARRIVED])
        self.assertEqual([a[0] for n, a in body(built()["before"], REC13) if n == 69],
                         list(VANILLA_WAITS))
        after = body(built()["rom"], built()["notes"]["arrive"])
        load = after.index((39, MAP_RELOAD))
        self.assertEqual([n for n, _ in after[load + 1:] if n == 69], [],
                         "no wait runs between the load and the end of the record")
        self.assertEqual(ARRIVED, VANILLA_WAITS[2], "the wait after the walk is vanilla's own")

    def test_record_a_costs_vanillas_own_beat_and_vanillas_fastest_fade(self):
        """Counted on the record's own frame ops, out of the built ROM.

        The black the player sits through is the fade out plus the fade in, 60 frames, 1.0 second,
        with no wait between them. The opening 60 runs BEFORE the cover, so it is a beat on a lit
        screen and not part of the black."""
        ops = body(built()["rom"], built()["notes"]["arrive"])
        frames = sum(a[0] for n, a in ops if n in (69, 40, 41, 42, 43) and a)
        self.assertEqual(frames, OPEN_WAIT + FADE_OUT)
        self.assertEqual(frames, 90)
        self.assertEqual(FADE_OUT + VANILLA_FADE["waits"] + FADE_IN, 60,
                         "the whole black is vanilla's own fastest, 1.0 second")

    def test_the_three_year_skip_refills_trunks(self):
        """The owner: "trunks ssj ki is drained after the 3 year split, it should be refrsehed for
        the cell fight". ext 109 sets HP and ext 110 sets EP to min(n, max), and vanilla scripts use
        5000 (bible B0576). chamber_spar runs the same pair. The yellow Super Saiyan ki row IS the
        EP row, so ext 110 is the op he means."""
        ops = body(built()["rom"], built()["notes"]["arrive"])
        self.assertIn((HP_REFILL, (TRUNKS, REFILL)), ops)
        self.assertIn((KI_REFILL, (TRUNKS, REFILL)), ops)
        self.assertLess(ops.index((KI_REFILL, (TRUNKS, REFILL))), ops.index((39, MAP_RELOAD)),
                        "the refill runs under the fade, before the arena comes up")

    def test_the_hud_is_not_given_back_before_the_dialogue(self):
        """His finding 4: "the hud for trunks is visible, when it shouldnt be, it should appear whent
        he dialgue ends". Record A2 hands on to word 14, the first line of the Cell talk, so a
        header_bit1(1) here put the HUD up for the whole conversation. It is gone; word 23's battle
        start is where the HUD comes back, as it does in every other fight in the game."""
        b = built()
        self.assertIn((86, (0,)), body(b["rom"], b["notes"]["arrive"]))
        self.assertNotIn((86, (1,)), body(b["rom"], b["notes"]["reveal"]))
        self.assertIn((86, (1,)), body(b["rom"], b["notes"]["fight"]))
        self.assertEqual(b["rom"][b["notes"]["reveal"]], 14,
                         "A2 really does hand on to the first line of the talk")

    def test_the_player_arrives_wholly_below_the_frame_and_walks_into_it(self):
        """His finding 3: "you see his sprite in the very bottom, not sure if in vanilla hes there or
        if he is supposed to aarrive off screen". He is. Record A2 used to put him back on
        TRUNKS_START (248,624), where the 16x32 sprite with dy -24 spans y 600 to 632 against a view
        bottom of y 616, so his top 16 px sat in the frame. He now stays on CAPTION_SPOT and walks
        up. The arithmetic holds at ANY fade length, so the fix cannot depend on the transition."""
        b = built()
        back = body(b["rom"], b["notes"]["reveal"])
        self.assertEqual([op for op in back if op[0] == 62], [], "nobody is repositioned")
        self.assertGreater(TRUNKS_START[1] - TRUNKS_UP, VIEW[1],
                           "TRUNKS_START's own sprite top is inside the parked view")
        self.assertLess(TRUNKS_START[1] - TRUNKS_UP, VIEW[1] + 160, "which is why he showed")
        self.assertGreaterEqual(CAPTION_SPOT[1] - TRUNKS_UP, VIEW[1] + 160,
                                "and CAPTION_SPOT is wholly below it")
        self.assertLess(back.index((41, (FADE_IN,))), back.index((53, (PLAYER,) + TRUNKS_SPOT)))


class FightStartTests(unittest.TestCase):
    def test_word_23_names_the_new_record_and_only_the_six_named_words_moved(self):
        """SIX words of the ending table move: the two lines the owner rewrote, the arrival, the fight
        start, and the two spare indices the caption chain takes."""
        b = built()
        self.assertEqual(u32(b["rom"], FIGHT_WORD), b["notes"]["fight"] + ROM_BASE)
        for k in range(TABLE_WORDS):
            if k not in MOVED_WORDS:
                self.assertEqual(u32(b["rom"], TABLE + 4 * k), u32(b["before"], TABLE + 4 * k), f"word {k}")
        for k in MOVED_WORDS:
            self.assertNotEqual(u32(b["rom"], TABLE + 4 * k), u32(b["before"], TABLE + 4 * k), f"word {k}")

    def test_the_vanilla_scripted_kill_is_untouched(self):
        b = built()
        self.assertEqual(hashlib.sha1(b["rom"][REC23:REC23 + REC23_LEN]).hexdigest(), REC23_SHA1)

    def test_record_f_runs_the_brief_in_order(self):
        b = built()
        self.assertEqual(body(b["rom"], b["notes"]["fight"]), FIGHT_OPS)

    def test_record_f_is_the_piccolo_record_op_for_op(self):
        """rom:0x3E47DC, map 11,4 word 6, which the owner named himself. Only the set, the item index
        and the bar op differ, and the bar op differs because that fight has two rounds and this has
        one. Order is not part of the shape, so the two are compared as op numbers."""
        b = built()
        his = [n for n, _ in body(b["before"], PICCOLO_RECORD)]
        mine = [n for n, _ in body(b["rom"], b["notes"]["fight"])]
        self.assertEqual(his, [104, 90, 86, 33])
        self.assertEqual(mine, [49, 104, 85, 86, 33])
        self.assertEqual(mine[1:], [104, 85, 86, 33], "four ops, no more, after the owner's cue")

    def test_record_f_ends_at_the_tables_end_word_so_the_player_gets_control(self):
        b = built()
        self.assertEqual(b["rom"][b["notes"]["fight"]], 26)
        self.assertEqual(u32(b["rom"], TABLE + 4 * 26), 0)

    def test_record_f_loads_no_map_and_opens_no_fade(self):
        """The owner's v6 finding, as an assertion: "Why is it fading!??? Look at how EVERY OTHER FIGHT
        WORKS! There should not be a fade at all after the diague!". Record A did the load and the
        cover, so nothing is left here to cover."""
        ops = body(built()["rom"], built()["notes"]["fight"])
        self.assertEqual([op for op in ops if op[0] in (35, 36, 38, 39)], [])
        self.assertEqual([op for op in ops if op[0] in (40, 41, 42, 43)], [])
        self.assertEqual([op for op in ops if op[0] == 69], [], "and no wait either")

    def test_record_f_sets_no_form_no_leader_and_no_camera(self):
        """Record A settled all three. A second ext 73 or ext 70 here would be noise, and an ext 31
        would fight the camera_follow that follows it."""
        ops = body(built()["rom"], built()["notes"]["fight"])
        self.assertEqual([op for op in ops if op[0] in (70, 73, 31)], [])

    def test_the_record_places_nobody_so_there_is_only_one_position(self):
        """His call on 2026-11-06: "They should start at the exact point where they load in from the
        start, they should not be moving at all". ext 104 spawns the enemy at the NPC's own point and
        facing, so the fight starts exactly where the talk left the pair."""
        ops = body(built()["rom"], built()["notes"]["fight"])
        self.assertEqual([op for op in ops if op[0] in PLACE_OPS], [])
        self.assertEqual([op for op in ops if op[0] == 53], [])

    def test_the_fight_starts_where_the_conversation_left_the_pair(self):
        """His v8 play test: "the start still transitions both cell and trunks to different points on
        the map". Nothing in record F moves anybody, and the two modules must agree on both spots."""
        b = built()
        self.assertEqual((CELL_SPOT, TRUNKS_SPOT), (tuple(b["arena"]["cell_spot"]),
                                                    tuple(b["arena"]["trunks_spot"])))
        self.assertEqual(TRUNKS_SPOT[1] - CELL_SPOT[1], 64, "the 64 px separation is kept")
        self.assertIn((51, (NPC_TRUNKS,) + TRUNKS_SPOT), vanilla(b),
                      "the vanilla ending puts a Trunks on this exact spot")

    def test_ext_104_names_the_enemy_item_the_arena_built(self):
        """Sprite_ReplaceWithEntry @0x0800AAC6 destroys the actor of the pushed SET and calls
        Object_SpawnFromEntry @0x0800C75C with the pushed INDEX. That bounds the index against the map
        entry's item count and calls the item's own +0 factory, so the index must be the enemy's."""
        b = built()
        op = next(op for op in body(b["rom"], b["notes"]["fight"]) if op[0] == 104)
        self.assertEqual(op[1], (CELL, b["arena"]["item_index"]))
        self.assertEqual(b["arena"]["item_index"], ENEMY_INDEX)
        self.assertNotEqual(b["arena"]["item_index"], b["arena"]["npc_item_index"])
        self.assertEqual(u32(b["rom"], b["arena"]["item"] + 4), 1, "the enemy item is condition 1")
        self.assertEqual(u32(b["rom"], b["arena"]["npc_item"] + 4), 0, "the NPC item is condition 0")
        self.assertEqual(b["arena"]["cell_set"], CELL)

    def test_the_death_event_rides_on_the_item_so_ext_104_carries_it(self):
        """The enemy factory @0x0800E77E reaches @0x0800E280, which runs LDR r2,[r6,#0x14] ;
        STR r2,[r5,#0x4]: the item's own event struct. Nothing on the ext 104 path overwrites it."""
        b = built()
        self.assertEqual(u32(b["rom"], b["arena"]["item"] + 0x14), b["notes"]["event"] + ROM_BASE)
        self.assertEqual(u32(b["rom"], b["notes"]["event"] + 4), b["notes"]["table"] + ROM_BASE)

    def test_the_hud_and_the_boss_bar_are_there(self):
        ops = body(built()["rom"], built()["notes"]["fight"])
        self.assertIn((86, (1,)), ops)
        self.assertIn((85, (CELL,)), ops)
        self.assertEqual([op for op in ops if op[0] == 90], [], "ext 90 is a round segment, not a bar")


# ===== the conversation, left VANILLA (the v6 scope correction) =====

class VanillaConversationTests(unittest.TestCase):
    """The owner scoped the work on 2026-11-06: "there are two sections, the scene against 17/18,
    which we are NOT doing at this time. And the future cell scene". v5 edited both. v6 edits neither,
    so every record of the talk is the base record and the table still names it.

    The Cell scene is not moved onto the player either, and that is a READ, not a choice. Record 13
    loads with ext 35, whose handler reaches Map_Load @0x0800C664, and Map_Load never calls the player
    constructor player_ctor @0x080086D4. Only sub_0800C584 does, and only ext 38 and ext 39 reach it.
    Map 6,1 also spawns its own set 133 NPC from item rom:0x3F9C08 whenever flag 196 is set."""

    def test_the_five_words_still_name_the_vanilla_records(self):
        b = built()
        for name, (index, rec, _) in ending_fight.VANILLA_CONVERSATION.items():
            self.assertEqual(u32(b["rom"], TABLE + 4 * index), rec + ROM_BASE, name)
            self.assertEqual(u32(b["before"], TABLE + 4 * index), rec + ROM_BASE, name)

    def test_not_one_byte_of_the_five_records_changes(self):
        b = built()
        for name, (_, rec, sha) in ending_fight.VANILLA_CONVERSATION.items():
            length = record_end(b["before"], rec) - rec
            self.assertEqual(b["rom"][rec:rec + length], b["before"][rec:rec + length], name)
            self.assertEqual(hashlib.sha1(b["rom"][rec:rec + length]).hexdigest(), sha, name)

    def test_every_vanilla_op_on_set_133_is_still_there(self):
        """v5 moved these onto set 0 and deleted one of them. Every one of the 17/18 scene is back.
        Record 13's own walk(133, 248, 568) is not here: that record is past the boundary and its copy
        walks the player instead, which the ArriveTests check."""
        b = built()
        got = [op for _, rec, _ in ending_fight.VANILLA_CONVERSATION.values()
               for op in body(b["rom"], rec) if op[1][:1] == (SSJ_TRUNKS,)]
        self.assertEqual(got, CONV_VANILLA_OPS)

    def test_no_record_of_the_talk_acts_on_the_player(self):
        """Set 0 reaches the player through Sprite_Select @0x08009370, and the ending builds no player
        object, so an op on set 0 inside the talk would address nothing."""
        b = built()
        for name, (_, rec, _) in ending_fight.VANILLA_CONVERSATION.items():
            for n, args in body(b["rom"], rec):
                self.assertNotEqual(args[:1], (PLAYER,), f"{name} ext {n}")

    def test_the_plain_npc_trunks_is_left_alone(self):
        """Set 132 is the Trunks the Cell Games and Lookout scenes still use."""
        b = built()
        now = body(b["rom"], ending_fight.VANILLA_CONVERSATION["transform"][1])
        for op in NPC_TRUNKS_KEPT:
            self.assertIn(op, now)

    def test_the_vanilla_record_13_is_left_in_place_with_its_ext_35_load(self):
        """The record itself is never written: only the table word moves. A save state paused inside
        the vanilla record still runs it to its end, and its ext 35 load is still an ext 35."""
        b = built()
        ops = body(b["rom"], REC13)
        self.assertIn(CONV_LOAD, ops)
        self.assertEqual([op for op in ops if op[0] in (70, 73)], [])
        self.assertEqual(body(b["rom"], REC13), body(b["before"], REC13))


# ===== the death event =====

class TalkPortraitTests(unittest.TestCase):
    """The owner, 2026-11-08: "the portrait for trunks when talking to cell should use base".

    Record A gives the player the BASE body, set 132, so a Super Saiyan face over base pixels is the
    picture disagreeing with the sprite. A type 1 to 4 record carries its portrait id at +3, and the
    pair comes from the appearance table: entry 15 is set 132 and dialog 100, entry 16 is set 133
    and dialog 101."""

    # Word 22's text is replaced, so its portrait moves with it onto the new record instead of being
    # written in place. These three are the records that keep their address and take a one byte edit.
    CELL_TALK = {14: 0x3B7E74, 16: 0x3B7EB0, 20: 0x3B7F10}
    SSJ_TALK = {5: 0x3B7C48, 7: 0x3B7C76, 10: 0x3B7D3C}

    def test_the_two_ids_are_the_appearance_table_pair_for_sets_132_and_133(self):
        b = built()
        for entry, set_id, portrait in ((15, BASE_TRUNKS, 100), (16, SSJ_TRUNKS, 101)):
            at = ending_fight.APPEARANCE + ending_fight.APPEARANCE_ENTRY * entry
            self.assertEqual(b["rom"][at + 1], set_id, f"appearance entry {entry}")
            self.assertEqual(b["rom"][at + ending_fight.APPEARANCE_DIALOG], portrait)
        self.assertEqual((ending_fight.BASE_PORTRAIT, ending_fight.SSJ_PORTRAIT), (100, 101))

    def test_the_cell_talk_records_show_base_trunks(self):
        b = built()
        self.assertEqual({i: rec for i, rec, _ in ending_fight.TALK_PORTRAITS}, self.CELL_TALK)
        for index, rec in sorted(self.CELL_TALK.items()):
            self.assertEqual(b["before"][rec + 3], 101, f"word {index} was not Super Saiyan to start")
            self.assertEqual(b["rom"][rec + 3], 100, f"word {index}")
            self.assertEqual(u32(b["rom"], TABLE + 4 * index), rec + ROM_BASE)

    def test_the_17_18_talk_keeps_super_saiyan(self):
        """He really is Super Saiyan there, so those four records may not move. The boundary is the
        map load at rom:0x3B7E5E inside record 13, and every one of these sits before it."""
        b = built()
        for index, rec in sorted(self.SSJ_TALK.items()):
            self.assertLess(rec, 0x3B7E5E, f"word {index} is not on the 17/18 side")
            self.assertEqual(b["rom"][rec + 3], 101, f"word {index}")
            self.assertEqual(b["rom"][rec:rec + 0x10], b["before"][rec:rec + 0x10], f"word {index}")

    def test_only_the_portrait_byte_of_each_record_moves(self):
        """A one-byte edit keeps the record's address and its length, so a save state paused inside
        one still runs to its end and no table word has to move.

        A type 2 record's +4 word is NOT a pointer and its payload is inline, so a per-record length
        would have to be guessed. The span from record 14 to the start of vanilla record 23 holds
        the whole Cell talk, so it is compared WHOLE instead."""
        b = built()
        span = (0x3B7E74, REC23)
        changed = [i for i in range(*span) if b["rom"][i] != b["before"][i]]
        self.assertEqual(changed, sorted(rec + 3 for rec in self.CELL_TALK.values()),
                         "only the three portrait bytes may differ across the whole Cell talk")
        for index, rec in sorted(self.CELL_TALK.items()):
            self.assertIn(b["before"][rec + 2], (1, 2), f"word {index}")
            self.assertEqual(b["rom"][rec:rec + 2], b["before"][rec:rec + 2], f"word {index} next")


class OwnerLinesTests(unittest.TestCase):
    """The owner's own words, the design of 2026-11-08, sections 1, 2 and 3.

    Every character of a line is his and no word was re-written. Each box is measured against the
    widest box the ending talk renders in vanilla, 294 px (word 3), and against the 4 line page the
    dialog box holds (bible B2095). The three segments that ran past 294 px as one box were split
    into two boxes at a mark HE wrote, so the text is the same text."""

    # HIS LOCKED TEXT, 2026-11-09. He played the build and said "the new dialogue is missing period
    # punctuations", so the three boxes that ended bare now end on a full stop. He refused a trailing
    # ELLIPSIS on word 12 box 2 the day before; a full stop is a different mark and is what he asked
    # for. That box now opens a sentence of its own, so "but" is "But". Word 12 box 3 keeps its bare
    # "... Cell" and word 22 box 2 keeps its bang, because both already carry a mark he wrote.
    LINES = {12: ("line12", 101, ["I wish I could say that it's all over.",
                                  "But there is one more thing that has to be done.",
                                  "... Cell"]),
             22: ("line22", 100, ["If you can get past me, then you can get to the past.",
                                  "But I won't let you!"])}
    WIDEST_VANILLA_BOX = 294
    VANILLA_LINES = {12: (0x3B7E0E, 0x3B), 22: (0x3B7FE0, 0x36)}

    def test_each_rewritten_word_names_a_new_record_with_his_text(self):
        b = built()
        for index, (note, portrait, boxes) in sorted(self.LINES.items()):
            at = b["notes"][note]
            self.assertEqual(u32(b["rom"], TABLE + 4 * index), at + ROM_BASE, f"word {index}")
            self.assertEqual(b["rom"][at + 2], 1, "a type 1 text record")
            self.assertEqual(b["rom"][at + 3], portrait, f"word {index} portrait")
            self.assertEqual(struct.unpack_from("<H", b["rom"], at)[0], index + 1, "hands on as before")
            self.assertEqual(text_of(b["rom"], at),
                             b"\x0b".join(x.encode("ascii") for x in boxes))

    def test_the_vanilla_records_the_words_left_behind_keep_every_byte(self):
        """Only the table word moves, so a save state paused inside one still runs to its end."""
        b = built()
        for index, (rec, length) in sorted(self.VANILLA_LINES.items()):
            self.assertEqual(b["rom"][rec:rec + length], b["before"][rec:rec + length], f"word {index}")

    def test_every_box_fits_the_page_and_stays_inside_the_widest_vanilla_box(self):
        b = built()
        boxes = [box for note, _, _ in self.LINES.values()
                 for box in text_of(b["rom"], b["notes"][note]).split(b"\x0b")]
        for box in boxes:
            lines = dialog_wrap(b["before"], box)
            self.assertLessEqual(sum(w for _, w in lines), self.WIDEST_VANILLA_BOX, repr(box))
            self.assertLessEqual(len(lines), BOX_LINES, f"{box!r} pages on")

    # The boxes he asked a full stop for, 2026-11-09: "the new dialogue is missing period
    # punctuations". Word 12 box 3 is his own "... Cell" and word 22 box 2 ends on his own bang, so
    # neither is in his ask and neither is listed here.
    HIS_PERIODS = {12: (0, 1), 22: (0,)}

    def test_the_three_bare_boxes_now_end_on_the_full_stop_he_asked_for(self):
        """Read back out of the built ROM, so a box that loses its mark again fails here."""
        b = built()
        for index, wanted in sorted(self.HIS_PERIODS.items()):
            note = self.LINES[index][0]
            boxes = text_of(b["rom"], b["notes"][note]).split(b"\x0b")
            for k in wanted:
                self.assertTrue(boxes[k].endswith(b"."),
                                f"word {index} box {k + 1} ends bare: {boxes[k]!r}")

    def test_the_caption_reuses_the_vanilla_string_and_the_vanilla_mechanism(self):
        """The string is read out of rom:0x3B8610, the time skip's own caption, and the record is a
        plain type 1 record whose text opens with the two prefix bytes. A NEW record was needed only
        because the vanilla one at rom:0x3B860C carries the time skip table's own next index."""
        b = built()
        at = b["notes"]["caption"]
        self.assertEqual(u32(b["rom"], CAPTION_WORD), at + ROM_BASE)
        self.assertEqual(b["rom"][at + 2], 1, "a type 1 text record, like every vanilla caption")
        self.assertEqual(b["rom"][at + 3], 0, "a caption shows no face")
        self.assertEqual(text_of(b["rom"], at), CAPTION_TEXT)
        self.assertEqual(b["before"][CAPTION_AT:CAPTION_AT + len(CAPTION_TEXT)], CAPTION_TEXT)
        self.assertEqual(b["rom"][0x3B860C:0x3B860C + 0x1B], b["before"][0x3B860C:0x3B860C + 0x1B],
                         "the vanilla caption record is untouched")
        self.assertEqual(struct.unpack_from("<H", b["before"], 0x3B860C)[0], 9,
                         "and it hands on to word 9 of ITS table, which is why it cannot be reused")

    def test_the_caption_chain_runs_arrival_caption_reveal_then_the_cell_talk(self):
        b = built()
        self.assertEqual(struct.unpack_from("<H", b["rom"], b["notes"]["arrive"])[0], CAPTION_INDEX)
        self.assertEqual(struct.unpack_from("<H", b["rom"], b["notes"]["caption"])[0], REVEAL_INDEX)
        self.assertEqual(struct.unpack_from("<H", b["rom"], b["notes"]["reveal"])[0], 14)
        self.assertEqual(u32(b["rom"], REVEAL_WORD), b["notes"]["reveal"] + ROM_BASE)

    def test_the_two_spare_indices_were_really_spare(self):
        """Vanilla chains 0 to 26 in order, so index 24 is reached only from record 23 and index 25
        only from record 24. Record 23 becomes record F, whose next is 26, so nothing in the ending
        table reaches either index any more."""
        b = built()
        reached = {}
        for k in range(TABLE_WORDS):
            word = u32(b["before"], TABLE + 4 * k)
            if word < 0x10000:
                continue
            nxt = struct.unpack_from("<H", b["before"], word - ROM_BASE)[0]
            if nxt in (CAPTION_INDEX, REVEAL_INDEX):
                reached[k] = nxt
        self.assertEqual(reached, {23: CAPTION_INDEX, 24: REVEAL_INDEX})
        self.assertEqual(struct.unpack_from("<H", b["rom"], b["notes"]["fight"])[0], 26,
                         "record F ends the scene, so index 24 is free")

    def test_the_vanilla_end_text_is_still_reached_by_address_from_the_death_table(self):
        """Repointing ending words 24 and 25 may not cost Cell's death its ending. Table D names the
        two vanilla RECORDS, not the ending table's words."""
        b = built()
        table = b["notes"]["table"]
        self.assertEqual(u32(b["rom"], table + 4 * 24), REC24 + ROM_BASE)
        self.assertEqual(u32(b["rom"], table + 4 * 25), REC25 + ROM_BASE)
        self.assertEqual(b["rom"][REC24:REC24 + 0x24], b["before"][REC24:REC24 + 0x24])
        self.assertEqual(b["rom"][REC25:REC25 + 6], b["before"][REC25:REC25 + 6])

    def test_the_caption_is_lit_on_black_with_nothing_else_on_the_screen(self):
        """fade_out ends in Palette_LoadScaled @0x0800DA96, which DMAs the scaled snapshot over all
        512 palette halfwords, and no dialog box function writes palette RAM, so a box opened after a
        fade is black on black. ext 45 @0x08009BE4 is one DMA3 of the shared OBJ palette, and the
        ending's own tail runs it immediately before "@^The End.". It lights every sprite, so the
        view is parked on a corner of map 6,100 that holds neither actor first, and the HUD goes away
        and comes back."""
        b = built()
        ops = body(b["rom"], b["notes"]["arrive"])
        self.assertEqual(ops[-1], (45, ()), "the palette comes back last, just before the box")
        self.assertLess(ops.index((86, (0,))), ops.index((45, ())))
        self.assertLess(ops.index((39, MAP_RELOAD)), ops.index((49, (CAPTION_MUSIC,))),
                        "ext 39 reads the new map's own music word (B2176), so the cue goes AFTER it")
        self.assertLess(ops.index((62, (PLAYER,) + CAPTION_SPOT)), ops.index((45, ())))
        self.assertGreaterEqual(CAPTION_SPOT[1] - TRUNKS_UP, VIEW[1] + 160,
                                "Trunks has to be below the parked view while the box is up")
        self.assertLessEqual(CELL_START[1] + CELL_DOWN, VIEW[1],
                             "and the NPC Cell is already above it")

    def test_the_music_cues_are_his_own_numbers(self):
        """Track 42 on the caption box, track 28 when the Capsule Corp battle starts."""
        b = built()
        self.assertIn((49, (CAPTION_MUSIC,)), body(b["rom"], b["notes"]["arrive"]))
        self.assertEqual(body(b["rom"], b["notes"]["fight"])[0], (49, (FIGHT_MUSIC,)))
        self.assertEqual(body(b["rom"], b["notes"]["fight"])[0], (49, (FIGHT_MUSIC,)),
                         "the song changes as the bar comes up, not after it")


class WeakCellTests(unittest.TestCase):
    """The owner, 2026-11-08: "Same for cell, this is cell before he absorbs people ... Weaker
    stats, like 25%". 25 percent WEAKER than vanilla, not 25 percent of vanilla.

    Vanilla type 60 also spawns on map 10,20, the main game's own Imperfect Cell, so the entry may
    not be edited in place. The arena enemy names a FRESH entry instead, allocated on the enemy
    table's own 24-byte stride, which is celljr_fight's method and has shipped since r41."""

    def test_the_rule_is_25_percent_weaker_and_rounds_half_up(self):
        self.assertEqual(ending_fight.WEAKER_PERCENT, 25)
        self.assertEqual([ending_fight.weaken(v, 10) for v in (5210, 3550, 2910)], [3910, 2660, 2180])
        self.assertEqual([ending_fight.weaken(v) for v in (32, 32, 37)], [24, 24, 28])

    def test_vanilla_type_60_is_not_written(self):
        b = built()
        at = ending_fight.ENEMY_TABLE + ending_fight.ENEMY_ENTRY * 60
        self.assertEqual(b["rom"][at:at + 24], b["before"][at:at + 24])
        self.assertEqual(b["rom"][at:at + 24], ending_fight.TYPE60)

    def test_the_new_entry_sits_on_the_table_stride_and_only_the_four_stats_move(self):
        b = built()
        at, type_id = b["notes"]["cell_type_entry"], b["notes"]["cell_type"]
        self.assertGreaterEqual(at, EXPANSION[0])
        self.assertEqual(ending_fight.ENEMY_TABLE + ending_fight.ENEMY_ENTRY * type_id, at)
        new, old = b["rom"][at:at + 24], ending_fight.TYPE60
        self.assertEqual(u32(new, 4), 3910)                       # HP 5210 less 25 percent, to a 10
        self.assertEqual((new[0xC], new[0xD], new[0xE]), (24, 24, 28))     # STR, POW, END
        for off in (0, 8, 0x10, 0x14):                            # EXP, AI, the factors, the descriptor
            self.assertEqual(new[off:off + 4], old[off:off + 4], f"+0x{off:X}")
        self.assertEqual(u32(new, 0x14), 0x086FF3C4, "the boss descriptor has to stay")

    def test_the_arena_enemy_names_the_new_type(self):
        b = built()
        item = b["notes"]["item"]
        self.assertEqual(u32(b["before"], item + ending_fight.ITEM_TYPE), 60)
        self.assertEqual(u32(b["rom"], item + ending_fight.ITEM_TYPE), b["notes"]["cell_type"])

    def test_the_main_games_imperfect_cell_still_names_type_60(self):
        """Its item is vanilla rom:0x4058A4 (bible B1151), and nothing here may reach it."""
        b = built()
        self.assertEqual(u32(b["rom"], 0x4058A4 + ending_fight.ITEM_TYPE), 60)
        self.assertEqual(b["rom"][0x4058A4:0x4058A4 + 0x20], b["before"][0x4058A4:0x4058A4 + 0x20])


class DeathTests(unittest.TestCase):
    def test_the_arena_enemy_now_runs_the_ending_table_on_death(self):
        b = built()
        event = b["arena"]["event"]
        self.assertEqual(u32(b["rom"], event), EVENT_RUNNER, "the runner word is left alone")
        self.assertEqual(u32(b["rom"], event + 4), b["notes"]["table"] + ROM_BASE)
        self.assertNotEqual(u32(b["before"], event + 4), b["notes"]["table"] + ROM_BASE)
        self.assertEqual(u32(b["rom"], b["arena"]["item"] + 0x14), event + ROM_BASE)

    def test_the_event_table_carries_the_rest_of_the_ending(self):
        b = built()
        table = b["notes"]["table"]
        self.assertEqual(u32(b["rom"], table), b["notes"]["death"] + ROM_BASE)
        self.assertEqual(u32(b["rom"], table + 4 * 24), REC24 + ROM_BASE)
        self.assertEqual(u32(b["rom"], table + 4 * 25), REC25 + ROM_BASE)
        for k in list(range(1, 24)) + [26]:
            self.assertEqual(u32(b["rom"], table + 4 * k), 0, f"word {k}")

    def test_the_two_camera_parks_share_a_point_and_not_a_speed(self):
        """Record A keeps the speed the owner approved on the arena; record K is the one that parks
        from the follow camera on a map up to 1280 px wide, so only record K was re-timed."""
        b = built()
        arrive = [a for n, a in body(b["rom"], b["notes"]["arrive"]) if n == 31]
        back = [a for n, a in body(b["rom"], b["notes"]["reveal"]) if n == 31]
        death = [a for n, a in body(b["rom"], b["notes"]["death"]) if n == 31]
        self.assertEqual(arrive, [VIEW_POINT + (ARRIVE_SPEED,)])
        self.assertEqual(back, [], "record A2 sets no camera: nothing moved the one record A parked")
        self.assertEqual(death, [VIEW_POINT + (DEATH_SPEED,)])
        self.assertEqual(ARRIVE_SPEED, DEATH_SPEED, "the cut brought record A up to record K's speed")

    def test_the_death_record_goes_to_the_end_text(self):
        b = built()
        self.assertEqual(b["rom"][b["notes"]["death"]], 24)

    def test_the_death_record_is_the_head_then_the_two_vanilla_slices(self):
        b = built()
        self.assertEqual(body(b["rom"], b["notes"]["death"]), DEATH_HEAD + blast_ops(b) + tail_ops(b))

    def test_the_blast_is_the_vanilla_block_with_only_the_attacker_changed(self):
        b = built()
        self.assertEqual(blast_ops(b)[0], BLAST_FIRST)
        self.assertIn(ATTACKER_NOW, blast_ops(b))
        self.assertNotIn(ATTACKER_WAS, blast_ops(b))
        rest = [op for op in blast_ops(b) if op != ATTACKER_NOW]
        was = [op for op in vanilla_blast(b) if op != ATTACKER_WAS]
        self.assertEqual(rest, was, "every op of the group but the attacker push is reused")

    def test_the_blast_bytes_are_the_vanilla_bytes_but_the_push(self):
        """Byte for byte, so a reused op cannot drift: only the 7 byte push becomes a 6 byte push."""
        b = built()
        old = b["before"][BLAST_AT:BLAST_AT + BLAST_LEN]
        at = b["rom"].find(old[:2] + bytes.fromhex("1d0300"), b["notes"]["death"])
        self.assertGreater(at, 0)
        new = b["rom"][at:at + BLAST_LEN - 1]
        self.assertEqual(new[:2], old[:2], "ext 63 opens the group")
        self.assertEqual(new[2:8], bytes.fromhex("1d0300388148"), "push 0, 28, 100")
        self.assertEqual(new[8:], old[9:], "every byte after the push is the vanilla byte")

    def test_the_tail_keeps_every_vanilla_op_but_the_four_that_name_set_132_or_133(self):
        b = built()
        kept = [op for op in vanilla_tail(b) if op not in TAIL_DROPPED]
        kept = [FACE_NOW if op == FACE_WAS else op for op in kept]
        self.assertEqual(tail_ops(b), kept)
        for op in TAIL_DROPPED:
            self.assertIn(op, vanilla_tail(b), "the drop list must name real vanilla ops")
            self.assertNotIn(op, tail_ops(b))

    def test_no_op_of_the_death_record_acts_on_set_132_or_133(self):
        """After ext 70 the player object carries a Trunks set, so a find by set would bind him (B2)."""
        for n, args in body(built()["rom"], built()["notes"]["death"]):
            self.assertNotIn(args[:1], ((SSJ_TRUNKS,), (NPC_TRUNKS,)), f"ext {n}")


# ===== the whole ROM =====

class RomTests(unittest.TestCase):
    def test_every_changed_byte_is_a_declared_site(self):
        b = built()
        declared = {i for at, n, _ in b["notes"]["sites"] for i in range(at, at + n)}
        self.assertEqual(set(diff(b["before"], b["rom"])) - declared, set())

    def test_the_six_words_and_the_three_portrait_bytes_are_the_only_base_sites(self):
        """The arena owns both Cells, so no vanilla map entry, item list, item or enemy type is
        written, and the 17/18 FIGHT is untouched. Six ending table words plus the three one-byte
        portrait ids of the Cell talk are the whole base footprint. Every record this module adds is a
        new copy, and the three it edits keep their address and their length, so a save state paused
        inside a vanilla record still runs it."""
        b = built()
        base = sorted((at, n) for at, n, _ in b["notes"]["sites"] if at < 0x800000)
        self.assertEqual(base, sorted([(TABLE + 4 * k, 4) for k in MOVED_WORDS]
                                      + [(rec + ending_fight.PORTRAIT_AT, 1)
                                         for _, rec, _ in ending_fight.TALK_PORTRAITS]))
        for name, (_, rec, _) in ending_fight.VANILLA_CONVERSATION.items():
            self.assertEqual(b["rom"][rec:rec + 0x20], b["before"][rec:rec + 0x20], name)

    def test_every_new_chunk_is_in_the_expansion_area(self):
        b = built()
        for at, n, name in b["notes"]["sites"]:
            if at >= 0x800000:
                self.assertTrue(EXPANSION[0] <= at and at + n <= EXPANSION[0] + EXPANSION[1], name)

    def test_the_rom_is_still_16_mb(self):
        self.assertEqual(len(built()["rom"]), log2_build.ROM_SIZE)


if __name__ == "__main__":
    unittest.main()
