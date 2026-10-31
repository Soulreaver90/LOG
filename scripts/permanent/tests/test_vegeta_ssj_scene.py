r"""
test_vegeta_ssj_scene.py - Tests for patches.vegeta_ssj_scene (trial 2026-10-24): Vegeta goes Super Saiyan when he
                           attacks Super Perfect Cell (table rom:0x3EB704 seq 50, table rom:0x3EC758 seq 17).
                           v2 (2026-10-25): in seq 50 he fires 3 blasts and Cell's 3 blasts knock him down.
                           v3 (2026-10-25): Cell walks up fast and punches him back and out, Gohan steps in and
                           takes Cell's blast; both copies stop the aura loop (sound 55).
                           v4 (2026-10-25): Cell flies past Vegeta and punches him far right, the camera stops on
                           the fight, Cell's blast flies at Vegeta and Gohan runs in front of him and takes it.
                           v5 (2026-10-29): Gohan flies in (state 12) in place of the run; set 160 borrows set 159's
                           anim 12 row, the only fly row it lacks.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_vegeta_ssj_scene.py -v
Builds build_list_trial_vegeta.txt in memory (from r40 an alias of build_list.txt): "before" = the list up to
vegeta_ssj_scene (r39 + relay_cooldown + fullpower_hud + beam_struggle), "rom" = with it (= r40); both pinned. The old
trial order (celljr_fight first) refuses from celljr_fight v6, which needs this patch's fly row. Scripts are decoded by
test_cellgames_ssj's decoder. Expected values are restated from docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-report.md
and the r39 bytes (scripts\one-time\2026-10-24-vegeta-ssj\s1_scene_r39.txt), never imported from the patch module.
"""
import copy
import hashlib
import struct
import unittest

import log2_build
from patches import vegeta_ssj_scene
from tests.test_cellgames_ssj import POS, diff, ext_sequence, u32, words_naming
from rom.rom_sheet import live_set_offset, row_frames
from rom.webfoot_decompress import ROM_BASE

# ===== constants (report, r39 reads) =====
LISTS = log2_build.ROOT / "scripts" / "permanent"
TRIAL_LIST, VEGETA_LIST = LISTS / "build_list_trial.txt", LISTS / "build_list_trial_vegeta.txt"
BEFORE_SHA1 = "9256a6ba861e03743c1d971a3f054bea1bcc6aae"   # r39 + relay_cooldown + fullpower_hud + beam_struggle
R40_SHA1 = "14d6b8314f5f418f80021fe60ef8d052b5dcf2be"      # build_list.txt r40 (2026-10-30)
VEGETA, VEGETA_SSJ, CELL = 137, 140, 58
SPC_TABLE, DEATH_TABLE = 0x3EB704, 0x3EC758
SEQ50, SEQ50_WORD = 0x3EB134, 0x3EB7C8                 # word 49: the attack after "He will pay!!!!"
SEQ52, SEQ52_BYTE = 0x3EB21C, 0x3EB232                 # word 51: removes Vegeta
SEQ17, SEQ17_WORD = 0x3EBD7C, 0x3EC798                 # word 16: Vegeta's blast in the beam struggle
SEQ20_WORD = DEATH_TABLE + 4 * 19                      # respawns base 137 after the struggle
SEQ50_SPOT, ITEM1_SPOT = (376, 416), (112, 272)        # seq 50 ext 53 destination; map 14,4 item 1
ITEM1 = 0x409218
VANILLA_GOKU = 0x3D35D4                                 # Southern Continent: NPC Goku 60 to 61
APPEARANCE_ENTRY = 20
ENTRY_VEGETA, ENTRY_VEGETA_SSJ, SSJ_FORM = 8, 11, 0x030021EC
SPC_SITES = {SEQ50: (0x16, 0x20, 0x26, 0x2B, 0x30, 0x39, 0x42, 0x4B), SEQ17: (0x37, 0x3D, 0x65)}
MOVES = (53, 54, 62, 99, 100)                           # ext ops that move an actor
LEADER_OPS = (70, 73, 82, 83, 115)                      # leader, record entry, unlock ops
ANIMS_USED = (0, 1, 2, 3, 5, 12)      # stand, walk (53), hurt (57 n=2), down (57 n=3), ki (96, 142), fly (54)
# v2 (docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-trial-v2.md, s4_knockdown_base.txt)
VOLLEY, VEGETA_N, CELL_N = 3, 100, 120                  # Cell's vanilla volley count; ext 96 n of each in seq 50
SEQ40 = 0x3EACD0                                        # Cell knocks Trunks (132) down: ext 57 (132, 2), (132, 3)
STATE3_TICK_END = (0xE150, "402902d3f9f798fa")          # cmp r1,#0x40 ; bcc ; bl 0x08007688
HOLD_LOAD = (0x7830, "3c1f0003")                        # sub_08007688's literal: hold state 0x03001F3C
HOLD_VT_SLOTS = ((0x260C0, "7047"), (0x26094, "7047"))  # vtable 0x08024188 enter and tick: bx lr
# v3 (docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-trial-v3.md, s5_v3_ops_base.txt, s6_reach_r39.txt)
GOHAN, AURA, LEFT, RIGHT = 0, 55, 2, 3
CELL_END, VEGETA_END, GOHAN_FROM = (428, 408), (376, 416), (432, 464)  # seq 40, seq 50 and seq 8 walk targets
# v4 (docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-trial-v4.md, s9_v4_camera_r39.txt, s10_v4_blast.py,
# s11_v4_boxes_r39.txt, s12_v4_layout_r39.txt)
PUNCH_SPOT, KNOCKED_TO, GOHAN_WAITS, GOHAN_BLOCKS = (341, 408), (456, 424), (468, 444), (431, 425)
CAMERA, BLAST_N, GOHAN_WAIT, FLY = (248, 328), 80, 16, 12
EXCHANGE = [(121, (CELL, FLY)), (136, (CELL, *PUNCH_SPOT, 500)), (31, (*CAMERA, 4)), (55, (CELL, RIGHT)),
            (55, (VEGETA_SSJ, LEFT)), (57, (CELL, 6)),
            (63, ()), (112, (VEGETA_SSJ, 34)), (95, (VEGETA_SSJ,)), (121, (VEGETA_SSJ, 2)),
            (136, (VEGETA_SSJ, *KNOCKED_TO, 600)), (57, (VEGETA_SSJ, 3)), (53, (GOHAN, *GOHAN_WAITS)),
            (55, (GOHAN, LEFT)), (47, (AURA,)), (64, ()),
            (63, ()), (96, (CELL, GOHAN, BLAST_N)), (69, (GOHAN_WAIT,)), (121, (GOHAN, FLY)),
            (136, (GOHAN, *GOHAN_BLOCKS, 500)), (60, (GOHAN,)), (112, (GOHAN, 34)), (95, (GOHAN,)),
            (57, (GOHAN, 2)), (64, ()), (55, (GOHAN, LEFT))]
SEQ8 = 0x3EA638                                          # Gohan walks to (432,464), the last move before seq 50
SEQ40_FOLLOW = (0x3EAD62, "003a0221")                    # seq 40: push 58 ; ext 33 (the follow camera on Cell)
GOHAN_SET, VIEW = 160, (240, 160)                        # Gohan's set at "He will pay!!!!" (my v3 ss1)
CELL_REACH, VEGETA_X = 43, (1, 15)          # set 58 anim 6 dir 3 frames 2-3 reach; set 140 anim 0 dir 2 opaque x
CELL_BODY_X = (2, 21)                       # set 58 anim 0 dir 3 frame 0 opaque x
LYING = (-5, -12, 23, 7)                    # set 140 anim 3 dir 2 frame 3 opaque box from the spot
GOHAN_BOX = (-4, -24, 19, 7)                # set 160 anim 0 dir 2, the widest frame
BYSTANDERS = {103: ((488, 408), (1, 15)), 76: ((496, 456), (3, 13)), 121: ((368, 456), (2, 14))}   # ss1, opaque x
BLAST_K, FIRE_TICK, BLAST_HALF = 0x7AE, 16, 8              # n x 0x7AE (@0x08011B66); fire at 0x10; 16 x 16 box
BLAST_TARGET_ONLY = ((0x11CB4, "1168036c994216d1"),       # ldr r1,[r2,#0] ; ldr r3,[r0,#0x40] ; cmp ; bne miss
                     (0x11C02, "2664"), (0x11B8C, "e268"),  # ctor +0x40 = the ext 96 target b
                     (0x11D1E, "1121"))                     # ext 60 done check asks the world, message 0x11
GROUP_WAIT = ((0x3B5D28 + 4 * 69, "5da60008"),           # ext 69 handler @0x0800A65C
              (0xA674, "404912c0083814f0"), (0xA67A, "14f03bfe"),   # wait vtable 0x0802585C, +4 = n; scene_push,
              (0xDEBC, "41680139416001d1"),               # no group flag read; tick: +4 - 1, done at 0 (n frames)
              (0xE066, "11600068002803d1fff7d7fe11f03ff9"))  # actor_queue: append; push the wait only when flag 0
EXT43_FADE = ((0xDC50, "fef713f9"), (0xBE7A, "031cff22ff21ff20"))   # ext 43's tick blends to white: not a wait
WAIT_VTABLES, WORLD_UPDATE = (0x0802585C, 0x08025150, 0x08025A40), 0x08004EA9   # ext 69, group wait, ext 31
FLY_STATE = ((0x3ED21C + 4 * FLY, "30210003"), (0x3B5278 + 4 * FLY, "30210003"))  # NPC and player word 12
EXT121_VT, EXT57_VT = 0x08025ED4, 0x08025BAC
HERCULE_KNOCK = 0x3E8BE2                                 # table rom:0x3E8D98 seq 22: Cell's punch, ext 136 (72, ...)
PLAYER_BLAST = 0x3D8BC4                                  # table rom:0x3D98AC seq 1: ext 96 (11, 0, 100), aura stop
TRUNKS_REVERT = 0x3B8016                                 # table rom:0x3B8140 seq 24: revert, then ext 47 (55)
KI_HOLD = ((0xA19A, "2021"), (0xA1F6, "2021"), (0xA258, "2022"),      # mov r1/r2,#0x20 in ext 96, 142, 99
           (0x11AEE, "1028"), (0x11EB6, "1028"))                      # cmp r0,#0x10: fire frame (ext 96, ext 99)
EXT136 = ((0x3B5D28 + 4 * 136, "47a30008"), (0xA42C, "044c0208"),     # handler @0x0800A346, vtable 0x08024C04
          (0x1D2E0, "2f7c"), (0x1D306, "2f74"),                       # start keeps facing: ldrb/strb r7,[r5,#0x10]
          (0x10934, "8a6a5218002111f0"))                              # shared move tick end: state 0
MELEE_END = ((0xE1A8, "102a"), (0xE1C8, "002113f0"))    # states 6-8: 16 frames (cmp r2,#0x10), then state 0
# v5 (docs\tasks\2026-10-24-vegeta-ssj\vegeta-ssj-trial-v5.md, s13_v5_fly_r39.txt)
GOHAN_RAGE, FLY_DONOR, SET_LITERAL = 160, 159, 0x959C   # Gohan's set at "He will pay!!!!"; gi SSJ2, the donor
VANILLA_PLAYER_FLY = (0x3D3DE4, 0x3D3DF3, "1d0300865086400236")    # record; push 0,424,416 ; ext 54
FLY_CODE = ((0xE7AA, "886cff300d30c864"),    # state 12 enter: ldr r0,[r1,#0x48] ; add #0xff ; add #0xd ; str [r1,#0x4c]
            (0xE842, "01204002"))            # ext 54 start: mov r0,#1 ; lsl r0,r0,#9 (speed 0x200, 2 px a frame)
FLY_ROW_NAME = "set 160 anim 12 row (set 159's fly records)"


def hits(actor: int) -> list:
    return [(60, (actor,)), (57, (actor, 2)), (95, (actor,))]


def v3_seq50_tail(old: list) -> list:
    """The ops from the first group on: the v2 3-blast volley, then the v3 exchange instead of Cell's answer."""
    return [(63, ())] + [(96, (VEGETA_SSJ, CELL, VEGETA_N))] * VOLLEY + hits(CELL) * VOLLEY + [(64, ())] + EXCHANGE


def v3_seq17_tail(old: list) -> list:
    """The vanilla seq 17 ops after the transform, with 137 as 140 and the aura stop after the remove of 140."""
    tail = [(n, tuple(VEGETA_SSJ if v == VEGETA else v for v in a)) for n, a in old]
    k = tail.index((52, (VEGETA_SSJ,))) + 1
    return tail[:k] + [(47, (AURA,))] + tail[k:]

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(VEGETA_LIST)
        i = names.index("vegeta_ssj_scene")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        vegeta_ssj_scene.apply(rom, alloc)
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["vegeta_ssj_scene"], all_notes=alloc.notes)
    return _CACHE


def set_args(seq: list, ids: set) -> list:
    """(index, ext n, set id) for each set argument in ids, at the POS slots of the args since the last call."""
    return [(i, n, a[p]) for i, (n, a) in enumerate(seq) for p in POS.get(n, []) if len(a) >= -p and a[p] in ids]


def rows(rom: bytes, set_id: int) -> list:
    head = u32(rom, u32(rom, 0x959C) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE
    return [all(u32(rom, head + 0x4C + 16 * a + 4 * d) for d in range(4)) for a in range(rom[head + 2])]


def to_base(seq: list) -> list:
    return [(n, tuple(VEGETA if v == VEGETA_SSJ else v for v in a)) for n, a in seq]


# ===== v4 geometry model (s12_v4_layout.py: the same formulas, restated) =====

def hurtbox(rom: bytes, set_id: int, spot: tuple, face: int) -> tuple:
    """Absolute (x0, y0, x1, y1): set header +0xC + 16 x facing, offsets from the spot (@0x080079B8)."""
    head = u32(rom, u32(rom, 0x959C) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE
    x0, y0, x1, y1 = struct.unpack_from("<4i", rom, head + 0xC + 16 * face)
    return spot[0] + x0, spot[1] + y0, spot[0] + x1, spot[1] + y1


def move_frames(a: tuple, b: tuple, n: int) -> int:
    """ext 136: speed n x 0x290 >> 8 (8.8 px a frame); frames = largest axis x 256 / speed (@0x0800D1AC)."""
    return max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 256 // (n * 0x290 >> 8)


def blast(rom: bytes) -> dict:
    """Cell's blast at Gohan: spawn at the facing-right hurtbox front, centre height (@0x08007A26); velocity toward
    Gohan's hurtbox centre at the fire tick (@0x08011B04-@0x08011B7A); first frame its box overlaps Gohan's box at
    GOHAN_BLOCKS (strict, @0x08011CBC-@0x08011CDC). Frame 0 = the ext 96 start."""
    c = hurtbox(rom, CELL, PUNCH_SPOT, RIGHT)
    spawn = (c[2], (c[1] + c[3]) >> 1)
    g = hurtbox(rom, GOHAN_SET, GOHAN_WAITS, LEFT)
    dx, dy = ((g[0] + g[2]) >> 1) - spawn[0], ((g[1] + g[3]) >> 1) - spawn[1]
    big, k = max(abs(dx), abs(dy)), BLAST_N * BLAST_K
    v = (int(dx * k / (big << 8)), int(dy * k / (big << 8)))
    e = hurtbox(rom, GOHAN_SET, GOHAN_BLOCKS, LEFT)
    px, py, path = spawn[0] << 8, spawn[1] << 8, []
    for f in range(1, 120):
        px, py = px + v[0], py + v[1]
        x, y = px >> 8, py >> 8
        path.append((x, y))
        if x - BLAST_HALF < e[2] and e[0] < x + BLAST_HALF and y - BLAST_HALF < e[3] and e[1] < y + BLAST_HALF:
            return {"spawn": spawn, "v": v, "path": path, "touch": FIRE_TICK + f, "e": e}
    return {"spawn": spawn, "v": v, "path": path, "touch": None, "e": e}


def slot(rom: bytes, vt: int, k: int) -> int:
    """Vtables hold offsets relative to their own base."""
    return (vt + struct.unpack_from("<i", rom, vt - ROM_BASE + 4 * k)[0]) & 0xFFFFFFFF


# ===== tests =====

class ListTests(unittest.TestCase):
    def test_vegeta_list_is_main_and_runs_vegeta_after_the_beam(self):          # approved in r40
        dev = log2_build.read_build_list(log2_build.DEV_LIST)
        self.assertEqual(log2_build.read_build_list(VEGETA_LIST), dev)
        self.assertLess(dev.index("beam_struggle"), dev.index("vegeta_ssj_scene"))   # My order rule
        self.assertNotIn("celljr_fight", dev[:dev.index("vegeta_ssj_scene")])

    def test_before_and_r40_are_pinned(self):
        b = built()
        self.assertEqual(hashlib.sha1(b["before"]).hexdigest(), BEFORE_SHA1)
        self.assertEqual(hashlib.sha1(b["rom"]).hexdigest(), R40_SHA1)

    def test_second_run_and_missing_notes_raise(self):
        b = built()
        rom, alloc = bytearray(b["rom"]), copy.deepcopy(b["alloc_before"])
        alloc.notes["vegeta_ssj_scene"] = {}
        with self.assertRaises(ValueError):
            vegeta_ssj_scene.apply(rom, alloc)
        alloc = copy.deepcopy(b["alloc_before"])
        del alloc.notes["superperfect_cell"]
        with self.assertRaises(ValueError):
            vegeta_ssj_scene.apply(bytearray(b["before"]), alloc)

    def test_a_changed_source_byte_refuses_before_writing(self):
        b = built()
        for off in (SEQ50 + 0x10, SEQ17 + 0x20, SEQ52_BYTE, SEQ50_WORD, SEQ17_WORD, ITEM1 + 8, ITEM1 - 2):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            rom[off] ^= 0x01
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=f"rom:0x{off:X}"):
                vegeta_ssj_scene.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)

    def test_a_shared_write_refuses(self):
        b = built()
        alloc = copy.deepcopy(b["alloc_before"])
        self.assertNotIn("celljr_fight", alloc.notes)            # r40: celljr_fight is a trial after main
        alloc.notes["celljr_fight"] = {"sites": [(SEQ52_BYTE, 1, "a pretend celljr write")]}
        with self.assertRaises(ValueError):
            vegeta_ssj_scene.apply(bytearray(b["before"]), alloc)

    def test_celljr_fight_refuses_to_run_before_this_patch(self):
        """celljr_fight v6 flies Gohan on the set 160 row this patch borrows, so the pre-r40 order refuses."""
        b = built()
        rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
        with self.assertRaises(ValueError):
            log2_build.apply_patches(rom, alloc, ["celljr_fight"])
        self.assertEqual(bytes(rom), b["before"])


class BaseSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]

    def test_three_base_sites_old_and_new(self):
        n = self.notes["records"]
        self.assertEqual((u32(self.before, SEQ50_WORD), u32(self.rom, SEQ50_WORD)),
                         (SEQ50 + ROM_BASE, n["seq50"] + ROM_BASE))
        self.assertEqual((u32(self.before, SEQ17_WORD), u32(self.rom, SEQ17_WORD)),
                         (SEQ17 + ROM_BASE, n["seq17"] + ROM_BASE))
        self.assertEqual((self.before[SEQ52_BYTE], self.rom[SEQ52_BYTE]), (VEGETA, VEGETA_SSJ))
        base = [i for i in diff(self.before, self.rom) if i < 0x800000]
        want = {SEQ52_BYTE} | set(range(SEQ50_WORD, SEQ50_WORD + 4)) | set(range(SEQ17_WORD, SEQ17_WORD + 4))
        self.assertTrue(set(base) <= want)                 # a word byte that already matches does not show
        self.assertIn(SEQ52_BYTE, base)

    def test_every_changed_byte_is_inside_a_named_site(self):
        sites = self.notes["sites"]
        changed = diff(self.before, self.rom)
        self.assertEqual([i for i in changed if not any(s <= i < s + n for s, n, _ in sites)], [])
        self.assertEqual([name for s, n, name in sites if not any(s <= i < s + n for i in changed)], [])

    def test_superseded_records_have_no_name_and_stay_unchanged(self):
        self.assertEqual(words_naming(self.rom, SEQ50 + ROM_BASE), [])
        self.assertEqual(words_naming(self.rom, SEQ17 + ROM_BASE), [])
        self.assertEqual(self.rom[SEQ50:SEQ50 + 0x91], self.before[SEQ50:SEQ50 + 0x91])
        self.assertEqual(self.rom[SEQ17:SEQ17 + 0x74], self.before[SEQ17:SEQ17 + 0x74])

    def test_no_write_on_a_superperfect_site(self):
        """celljr_fight runs after this patch (r40); test_celljr_fight checks it writes no site of this one."""
        taken = {(o, 1) for o in built()["all_notes"]["superperfect_cell"]["sites"]}
        base = [i for i in diff(self.before, self.rom) if i < 0x800000]
        self.assertEqual([i for i in base if any(s <= i < s + n for s, n in taken)], [])

    def test_copies_carry_super_perfect_cell(self):
        # seq 50: v2 adds 2 blasts and 2 x 3 hits; v4 swaps Cell's 3 blasts for fly, move, face, punch and 1 blast
        for name, src, more in (("seq50", SEQ50, (VOLLEY - 1) * 4 - VOLLEY + 5), ("seq17", SEQ17, 0)):
            seq = ext_sequence(self.rom, self.notes["records"][name])
            self.assertNotIn(30, [v for _, _, v in set_args(seq, {30})])
            self.assertEqual(sum(1 for _, _, v in set_args(seq, {CELL}) if v == CELL),
                             sum(1 for _, _, v in set_args(ext_sequence(self.before, src), {CELL})) + more)
            for o in SPC_SITES[src]:
                self.assertIn(self.before[src + o], (0x3A, 0x74))


class SceneTests(unittest.TestCase):
    """Each attack: vanilla until the power-up, the vanilla NPC transform, then the same ops on set 140."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.goku = ext_sequence(cls.before, VANILLA_GOKU)

    def check(self, name: str, src: int, spot: tuple, tail=None) -> list:
        new, old = ext_sequence(self.rom, self.notes["records"][name]), ext_sequence(self.before, src)
        i = new.index((46, (55,)))
        swap = new[i:i + 6]
        self.assertEqual(swap, [(46, (55,)), (57, (VEGETA, 9)), (46, (23,)), (52, (VEGETA,)),
                                (51, (VEGETA_SSJ,) + spot), (55, (VEGETA_SSJ, 3))])
        self.assertEqual(new[:i], old[:i])
        if tail is None:
            self.assertEqual(to_base(new[i + 6:]), old[i:])
        else:
            self.assertEqual(new[i + 6:], tail(old[i:]))
        self.assertEqual(set_args(new[i + 6:], {VEGETA}), [])
        self.assertEqual(self.rom[self.notes["records"][name]], self.before[src])      # same next index
        return swap

    def test_the_transform_is_vanilla_gokus(self):
        goku = [c for c in self.goku if c[0] in (46, 57, 52, 51)]
        self.assertEqual(goku, [(46, (55,)), (57, (60, 9)), (46, (23,)), (52, (60,)), (51, (61, 432, 408))])

    def test_seq_50_powers_up_where_he_walked_to(self):
        old = ext_sequence(self.before, SEQ50)
        self.assertEqual(old[0], (53, (VEGETA,) + SEQ50_SPOT))
        self.check("seq50", SEQ50, SEQ50_SPOT, v3_seq50_tail)

    def test_seq_17_powers_up_at_his_map_spot(self):
        self.assertEqual(struct.unpack_from("<IIhhI", self.before, ITEM1), (0x0800D6DF, 0, *ITEM1_SPOT, VEGETA))
        self.assertEqual(self.before[ITEM1 - 2], 3)                       # stand step facing right
        for k in range(16):
            rec = u32(self.before, DEATH_TABLE + 4 * k) - ROM_BASE
            if self.before[rec + 2] == 0:
                hits = [h for h in set_args(ext_sequence(self.before, rec), {VEGETA}) if h[1] in MOVES]
                self.assertEqual(hits, [], f"word {k}")
        self.check("seq17", SEQ17, ITEM1_SPOT, v3_seq17_tail)

    def test_seq_52_removes_the_super_saiyan_set(self):
        self.assertIn((52, (VEGETA_SSJ,)), ext_sequence(self.rom, SEQ52))
        for k in range(50, 65):
            rec = u32(self.rom, SPC_TABLE + 4 * k) - ROM_BASE
            if self.rom[rec + 2] == 0:
                self.assertEqual(set_args(ext_sequence(self.rom, rec), {VEGETA}), [], f"word {k}")

    def test_base_vegeta_comes_back_after_the_struggle(self):
        rec = u32(self.rom, SEQ20_WORD) - ROM_BASE
        self.assertIn((51, VEGETA), [(n, v) for _, n, v in set_args(ext_sequence(self.rom, rec), {VEGETA})])

    def test_no_leader_record_or_unlock_op(self):
        for name in ("seq50", "seq17"):
            self.assertFalse([n for n, _ in ext_sequence(self.rom, self.notes["records"][name]) if n in LEADER_OPS])


class VolleyAndFallTests(unittest.TestCase):
    """v2 to v4: Vegeta fires 3 blasts; he falls (v3, v4: after Cell's punch) and stays down until seq 52."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.new = ext_sequence(cls.rom, cls.notes["records"]["seq50"])
        cls.old = ext_sequence(cls.before, SEQ50)

    def test_vanilla_seq_50_is_one_blast_answered_by_three(self):
        ki = [a for n, a in self.old if n == 96]
        self.assertEqual(ki, [(VEGETA, CELL, VEGETA_N)] + [(CELL, VEGETA, CELL_N)] * VOLLEY)

    def test_seq_17_has_one_blast_and_no_answer(self):
        ki = [a for n, a in ext_sequence(self.before, SEQ17) if n in (96, 142)]
        self.assertEqual(ki, [(VEGETA, CELL, VEGETA_N)])
        self.assertEqual([n for n, _ in ext_sequence(self.rom, self.notes["records"]["seq17"]) if n == 57],
                         [57])                                            # the power-up only: no fall in seq 17

    def test_volley_mirrors_cells_vanilla_volley(self):
        j = [k for k, c in enumerate(self.old) if c == (63, ())][1]
        self.assertEqual(self.old[j:j + 13],
                         [(63, ())] + [(96, (CELL, VEGETA, CELL_N))] * VOLLEY + hits(VEGETA) * VOLLEY)
        i = self.new.index((55, (VEGETA_SSJ, 3))) + 1
        self.assertEqual(self.new[i:i + 14],
                         [(63, ())] + [(96, (VEGETA_SSJ, CELL, VEGETA_N))] * VOLLEY + hits(CELL) * VOLLEY + [(64, ())])

    def test_fall_after_the_knock_back_and_nothing_after(self):
        k = self.new.index((57, (VEGETA_SSJ, 3)))
        self.assertEqual(self.new[k - 2:k], [(121, (VEGETA_SSJ, 2)), (136, (VEGETA_SSJ, *KNOCKED_TO, 600))])
        self.assertEqual([c for c in self.new if c[0] in (57, 121) and c[1][:1] == (VEGETA_SSJ,)],
                         [(121, (VEGETA_SSJ, 2)), (57, (VEGETA_SSJ, 3))])            # no blast hits him (v3, v4)
        self.assertEqual(set_args(self.new[k + 1:], {VEGETA, VEGETA_SSJ}), [])

    def test_vanilla_knockdown_precedent_trunks(self):
        seq40 = ext_sequence(self.before, SEQ40)
        k = seq40.index((57, (132, 3)))
        self.assertEqual(seq40[k - 1], (57, (132, 2)))
        self.assertIn((96, (CELL, 132, CELL_N)), seq40[:k])
        for w in range(40, 48):                          # seq 41-48: no state op on Trunks before seq 48 removes him
            rec = u32(self.before, SPC_TABLE + 4 * w) - ROM_BASE
            if self.before[rec + 2] == 0:
                ops = [n for _, n, _ in set_args(ext_sequence(self.before, rec), {132})]
                self.assertEqual(ops, [52] if w == 47 else [], f"word {w}")

    def test_state_3_ends_in_the_hold_state(self):
        for off, want in (STATE3_TICK_END, HOLD_LOAD) + HOLD_VT_SLOTS:
            self.assertEqual(self.rom[off:off + len(want) // 2].hex(), want, f"rom:0x{off:X}")

    def test_only_text_between_the_fall_and_the_remove(self):
        rec = u32(self.rom, SPC_TABLE + 4 * 50) - ROM_BASE
        self.assertEqual(self.rom[rec + 2], 1)                            # seq 51: Cell's line, type 1
        self.assertEqual([(n, v) for _, n, v in set_args(ext_sequence(self.rom, SEQ52), {VEGETA, VEGETA_SSJ})],
                         [(52, VEGETA_SSJ)])

    def test_an_edit_inside_another_raises(self):
        saved = copy.deepcopy(vegeta_ssj_scene.SHAPE)
        try:
            vegeta_ssj_scene.SHAPE["seq50"][0x1C] = (b"\x00\x00", b"\x00\x00")
            with self.assertRaises(ValueError):
                vegeta_ssj_scene.record_edits("seq50", SEQ50)
        finally:
            vegeta_ssj_scene.SHAPE.clear()
            vegeta_ssj_scene.SHAPE.update(saved)


class ExchangeTests(unittest.TestCase):
    """v3 and v4: Cell's move and one punch, the knock-out, Gohan takes Cell's blast, the aura stop."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.new = ext_sequence(cls.rom, cls.notes["records"]["seq50"])
        cls.old = ext_sequence(cls.before, SEQ50)

    def test_cells_answer_is_the_exchange(self):
        k = self.new.index((55, (VEGETA_SSJ, 3))) + 15                 # after the transform and the volley group
        self.assertEqual(self.new[k - 1], (64, ()))
        self.assertEqual(self.new[k:], EXCHANGE)
        self.assertEqual([a for n, a in self.new if n == 96 and a[0] == CELL], [(CELL, GOHAN, BLAST_N)])
        self.assertEqual(sum(1 for c in self.new if c == (57, (CELL, 6))), 1)                 # a single punch

    def test_gohan_walks_from_his_seq_8_spot_and_seq_52_places_him(self):
        self.assertIn((53, (GOHAN, *GOHAN_FROM)), ext_sequence(self.before, SEQ8))        # where he walks from
        for w in range(8, 49):                                              # seq 9-49: no move on 0 after seq 8
            rec = u32(self.before, SPC_TABLE + 4 * w) - ROM_BASE
            if self.before[rec + 2] == 0:
                moved = [n for _, n, v in set_args(ext_sequence(self.before, rec), {GOHAN}) if n in MOVES + (136,)]
                self.assertEqual(moved, [], f"word {w}")
        seq52 = ext_sequence(self.rom, SEQ52)                                # seq 52 still places him first
        k = seq52.index((62, (GOHAN, 432, 472)))
        self.assertEqual(set_args(seq52[:k], {GOHAN}), [])

    def test_aura_loop_stops_in_both_copies(self):
        for name, after in (("seq50", (57, (VEGETA_SSJ, 3))), ("seq17", (52, (VEGETA_SSJ,)))):
            seq = ext_sequence(self.rom, self.notes["records"][name])
            starts, stops = [i for i, c in enumerate(seq) if c == (46, (AURA,))], \
                [i for i, c in enumerate(seq) if c == (47, (AURA,))]
            self.assertEqual((len(starts), len(stops)), (1, 1), name)
            self.assertLess(starts[0], stops[0])
            self.assertIn(after, seq[stops[0] - 3:stops[0]], name)
        self.assertNotIn((47, (AURA,)), self.old)

    def test_vanilla_precedents(self):
        herc = ext_sequence(self.before, HERCULE_KNOCK)
        k = herc.index((57, (30, 6)))                                    # Cell's punch, Hercule knocked away
        self.assertEqual(herc[k - 1], (63, ()))
        self.assertIn((136, (72, 448, 850, 1000)), herc[k:])
        blast = ext_sequence(self.before, PLAYER_BLAST)
        k = blast.index((96, (11, GOHAN, 100)))
        self.assertEqual(blast[k:k + 8], [(96, (11, GOHAN, 100)), (60, (GOHAN,)), (112, (GOHAN, 34)), (95, (GOHAN,)),
                                          (57, (GOHAN, 2)), (57, (GOHAN, 3)), (47, (AURA,)), (64, ())])
        trunks = ext_sequence(self.before, TRUNKS_REVERT)
        k = trunks.index((47, (AURA,)))
        self.assertEqual(trunks[k - 2:k], [(52, (133,)), (51, (132, 248, 568))])

    def test_code_behind_the_design(self):
        for off, want in KI_HOLD + EXT136 + MELEE_END:
            self.assertEqual(self.rom[off:off + len(want) // 2].hex(), want, f"rom:0x{off:X}")


class LayoutTests(unittest.TestCase):
    """v4: Vegeta far right, Cell near the centre, the blast flies at Vegeta and Gohan stops in front of him first."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.new = ext_sequence(cls.rom, cls.notes["records"]["seq50"])
        cls.blast = blast(cls.rom)

    def test_vegeta_starts_left_of_cell_so_cell_crosses(self):
        cell_end = [a[1:] for n, a in ext_sequence(self.before, SEQ40) if n == 53 and a[0] == CELL][-1]
        self.assertEqual((cell_end, ext_sequence(self.before, SEQ50)[0][1][1:]), (CELL_END, VEGETA_END))
        off, want = SEQ40_FOLLOW                                         # v3's view: the follow camera on Cell
        self.assertEqual(self.rom[off:off + 4].hex(), want)
        for w in range(40, 50):                                           # seq 41-50: no camera op in vanilla
            rec = u32(self.before, SPC_TABLE + 4 * w) - ROM_BASE
            if self.before[rec + 2] == 0:
                self.assertEqual([n for n, _ in ext_sequence(self.before, rec) if n in (31, 33, 119)], [], f"word {w}")
        self.assertLess(PUNCH_SPOT[0], VEGETA_END[0])                     # Cell flies past him to his left
        self.assertGreater(KNOCKED_TO[0], CELL_END[0])                    # and knocks him right, past Cell's spot
        self.assertLess(self.new.index((31, (*CAMERA, 4))), self.new.index((57, (CELL, 6))))

    def test_the_punch_reaches_from_the_left(self):
        self.assertEqual(PUNCH_SPOT[1], CELL_END[1])                      # Cell's v3 row, so the arc height holds
        reach = PUNCH_SPOT[0] + CELL_REACH
        self.assertTrue(VEGETA_END[0] + VEGETA_X[0] <= reach <= VEGETA_END[0] + VEGETA_X[1])
        self.assertLess(PUNCH_SPOT[0] + CELL_BODY_X[1], VEGETA_END[0] + VEGETA_X[0])   # no overlap at rest
        k = self.new.index((57, (CELL, 6)))
        self.assertEqual(self.new[k - 2:k], [(55, (CELL, RIGHT)), (55, (VEGETA_SSJ, LEFT))])   # face each other

    def test_screen_layout(self):
        cx, cy = CAMERA
        cell = (PUNCH_SPOT[0] + CELL_BODY_X[0] - cx + PUNCH_SPOT[0] + CELL_BODY_X[1] - cx) / 2
        self.assertTrue(VIEW[0] * 0.3 <= cell <= VIEW[0] * 0.5, cell)               # centre, a little left
        lying = (KNOCKED_TO[0] + LYING[0] - cx, KNOCKED_TO[0] + LYING[2] - cx)
        self.assertTrue(VIEW[0] * 0.75 <= lying[0] and lying[1] < VIEW[0], lying)     # far right, all in view
        for spot in (GOHAN_WAITS, GOHAN_BLOCKS):
            x0, x1 = spot[0] + GOHAN_BOX[0] - cx, spot[0] + GOHAN_BOX[2] - cx
            y0, y1 = spot[1] + GOHAN_BOX[1] - cy, spot[1] + GOHAN_BOX[3] - cy
            self.assertTrue(0 <= x0 and x1 < VIEW[0] and 0 <= y0 and y1 < VIEW[1], spot)
        for s, ((x, y), (o0, o1)) in BYSTANDERS.items():
            out = x + o0 - cx >= VIEW[0]
            self.assertEqual(out, s in (103, 76), s)                       # 103 and 76 out of view, 121 in view
            self.assertTrue(x + o1 < KNOCKED_TO[0] + LYING[0] or x + o0 > KNOCKED_TO[0] + LYING[2], s)

    def test_cell_faces_right_when_it_fires(self):
        dx, dy = GOHAN_WAITS[0] - PUNCH_SPOT[0], GOHAN_WAITS[1] - PUNCH_SPOT[1]
        self.assertGreater(dx, abs(dy))                                    # ext 96 start turns him on the larger axis

    def test_the_blast_flies_through_vegeta_and_gohan_blocks_first(self):
        path, e = self.blast["path"], self.blast["e"]
        x0, y0, x1, y1 = (KNOCKED_TO[0] + LYING[0], KNOCKED_TO[1] + LYING[1], KNOCKED_TO[0] + LYING[2],
                          KNOCKED_TO[1] + LYING[3])
        vx, vy = self.blast["v"]
        sx, sy = self.blast["spawn"]
        for x in (x0, (x0 + x1) // 2):                     # the line enters his lying body and is still in it
            y = sy + (x - sx) * vy / vx                    # at the middle (it leaves under his head)
            self.assertTrue(y0 < y < y1, (x, y))
        self.assertLess(e[0], x0)                                            # Gohan's box is in front of him
        self.assertLessEqual(GOHAN_BLOCKS[0] + GOHAN_BOX[2], x0)            # and his sprite clears Vegeta's
        self.assertIsNotNone(self.blast["touch"])
        self.assertLessEqual(path[-1][0], x0)                                # it meets Gohan before Vegeta's body

    def test_gohan_stops_before_the_blast_reaches_him(self):
        k = self.new.index((96, (CELL, GOHAN, BLAST_N)))
        self.assertEqual(self.new[k - 1:k + 4], [(63, ()), (96, (CELL, GOHAN, BLAST_N)), (69, (GOHAN_WAIT,)),
                                                  (121, (GOHAN, FLY)), (136, (GOHAN, *GOHAN_BLOCKS, 500))])
        self.assertEqual(GOHAN_WAIT, FIRE_TICK)                             # his ops queue as the blast leaves
        arrive = GOHAN_WAIT + 1 + move_frames(GOHAN_WAITS, GOHAN_BLOCKS, 500)
        touch = self.blast["touch"]
        self.assertGreaterEqual(touch - arrive, 6, (arrive, touch))          # margin: ext 60 polls after the run
        self.assertGreaterEqual(touch - FIRE_TICK, 12)                        # a visible flight
        (sx, sy), (vx, vy) = self.blast["spawn"], self.blast["v"]
        for spot in (GOHAN_WAITS, GOHAN_BLOCKS):                              # the run lies on the blast's line
            x0, y0, x1, y1 = hurtbox(self.rom, GOHAN_SET, spot, LEFT)
            cx, cy = (x0 + x1) >> 1, (y0 + y1) >> 1
            self.assertLessEqual(abs(sy + (cx - sx) * vy / vx - cy), 2, spot)

    def test_the_blast_binds_to_gohan_and_nothing_waits_on_vegeta(self):
        self.assertEqual([a for n, a in self.new if n == 60 and a[0] in (VEGETA, VEGETA_SSJ)], [])
        self.assertEqual([a for n, a in self.new if n == 60][-1], (GOHAN,))
        for off, want in BLAST_TARGET_ONLY + GROUP_WAIT + EXT43_FADE + FLY_STATE:
            self.assertEqual(self.rom[off:off + len(want) // 2].hex(), want, f"rom:0x{off:X}")

    def test_waits_inside_a_group_run_the_world(self):
        self.assertEqual({slot(self.rom, vt, 3) for vt in WAIT_VTABLES}, {WORLD_UPDATE})
        self.assertEqual(slot(self.rom, EXT121_VT, 1), slot(self.rom, EXT57_VT, 1))   # ext 121 starts like ext 57
        self.assertEqual(slot(self.rom, EXT121_VT, 3), 0x08026499)                    # and does not wait


def fly_row(rom: bytes, set_id: int) -> int:
    """File offset of a set's anim 12 row: header +0x4C + 16 x anim, 4 words (one a dir)."""
    return u32(rom, u32(rom, SET_LITERAL) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE + 0x4C + 16 * FLY


class FlyTests(unittest.TestCase):
    """v5: Gohan flies in front of Vegeta with the pose and move pair of Cell's v4 dash."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.new = ext_sequence(cls.rom, cls.notes["records"]["seq50"])

    def test_vanilla_player_flies_with_ext_54_and_state_12(self):
        rec, at, want = VANILLA_PLAYER_FLY
        self.assertEqual(self.before[at:at + len(want) // 2].hex(), want)
        self.assertIn((54, (GOHAN, 424, 416)), ext_sequence(self.before, rec))
        for off, want in FLY_CODE + FLY_STATE:
            self.assertEqual(self.rom[off:off + len(want) // 2].hex(), want, f"rom:0x{off:X}")

    def test_gohan_flies_where_he_ran(self):
        k = self.new.index((96, (CELL, GOHAN, BLAST_N)))
        self.assertEqual(self.new[k + 2:k + 4], [(121, (GOHAN, FLY)), (136, (GOHAN, *GOHAN_BLOCKS, 500))])
        self.assertEqual([a for n, a in self.new if n == 121 and a[0] == GOHAN], [(GOHAN, FLY)])
        self.assertEqual([c for c in self.new if c[0] == 54], [])        # ext 54 (2 px a frame) would be too slow
        self.assertGreater(move_frames(GOHAN_WAITS, GOHAN_BLOCKS, 200), self.blast_flight())

    def blast_flight(self) -> int:
        return blast(self.rom)["touch"] - FIRE_TICK

    def test_set_160_had_no_fly_row_and_borrows_159s(self):
        self.assertEqual(rows(self.before, GOHAN_RAGE)[FLY], False)
        self.assertEqual(self.before[fly_row(self.before, GOHAN_RAGE):fly_row(self.before, GOHAN_RAGE) + 16], bytes(16))
        row, donor = fly_row(self.rom, GOHAN_RAGE), fly_row(self.rom, FLY_DONOR)
        self.assertEqual(self.rom[row:row + 16], self.rom[donor:donor + 16])
        self.assertIn((row, 16, FLY_ROW_NAME), self.notes["sites"])
        head = row - 0x4C - 16 * FLY
        self.assertEqual([i for i in diff(self.before, self.rom) if head <= i < head + 0x4C + 16 * self.rom[head + 2]],
                         [i for i in range(row, row + 16) if self.before[i] != self.rom[i]])

    def test_every_borrowed_record_decodes_and_fits_the_slot(self):
        off = live_set_offset(self.rom, GOHAN_RAGE)
        slot = struct.unpack_from("<H", self.rom, off)[0]
        self.assertEqual(slot, struct.unpack_from("<H", self.rom, live_set_offset(self.rom, FLY_DONOR))[0])
        donor = live_set_offset(self.rom, FLY_DONOR)
        for d in range(4):
            frames = row_frames(self.rom, donor, FLY, d)                 # set 160's walk runs on past the borrowed
            self.assertEqual(len(frames), 4, d)                         # list; the state 12 tick cycles 4 frames
            self.assertEqual([r["header"] for r, _ in row_frames(self.rom, off, FLY, d)[:4]],
                             [r["header"] for r, _ in frames])
            for r, data in frames:
                self.assertIsNotNone(data, d)
                self.assertEqual(len(data), r["w"] * r["h"])
                self.assertLessEqual(r["w"] * r["h"], slot)

    def test_he_flies_facing_left(self):
        dx, dy = GOHAN_BLOCKS[0] - GOHAN_WAITS[0], GOHAN_BLOCKS[1] - GOHAN_WAITS[1]
        self.assertTrue(dx < 0 and abs(dx) > abs(dy))
        k = self.new.index((121, (GOHAN, FLY)))
        self.assertIn((55, (GOHAN, LEFT)), self.new[:k])               # ext 136 keeps the facing (EXT136 pins)

    def test_a_filled_row_refuses_before_writing(self):
        b = built()
        for set_id in (GOHAN_RAGE, FLY_DONOR):
            rom, alloc = bytearray(b["before"]), copy.deepcopy(b["alloc_before"])
            at = fly_row(rom, set_id) + 4
            rom[at:at + 4] = bytes(4) if set_id == FLY_DONOR else rom[at:at + 3] + b"\x08"
            snap = bytes(rom)
            with self.assertRaises(ValueError, msg=str(set_id)):
                vegeta_ssj_scene.apply(rom, alloc)
            self.assertEqual(bytes(rom), snap)


class SetTests(unittest.TestCase):
    def test_140_is_vegetas_super_saiyan_entry(self):
        b = built()
        rom, t = b["rom"], b["all_notes"]["ssj2_form"]["table"]
        base, ssj = t + APPEARANCE_ENTRY * ENTRY_VEGETA, t + APPEARANCE_ENTRY * ENTRY_VEGETA_SSJ
        self.assertEqual((rom[base + 1], rom[base + 4]), (VEGETA, ENTRY_VEGETA_SSJ))
        self.assertEqual((rom[ssj + 1], rom[ssj + 5], u32(rom, ssj + 0x10)), (VEGETA_SSJ, ENTRY_VEGETA, SSJ_FORM))

    def test_set_140_has_every_anim_the_attacks_use(self):
        rom = built()["rom"]
        r137, r140 = rows(rom, VEGETA), rows(rom, VEGETA_SSJ)
        self.assertTrue(r137[9])                                          # the power-up runs on 137
        self.assertTrue(all(r140[a] for a in ANIMS_USED))

    def test_set_58_has_every_anim_cell_uses(self):
        r58 = rows(built()["rom"], CELL)
        self.assertTrue(all(r58[a] for a in (0, 1, 2, 5, 6, FLY)))   # stand, walk, hurt, ki, punch, fly (v4 dash)

    def test_gohan_set_has_the_stand_fly_and_hurt_anims(self):
        r160 = rows(built()["rom"], GOHAN_SET)
        self.assertTrue(all(r160[a] for a in (0, 2, FLY)))       # stand, hurt, fly (v5: ext 121 (0, 12))


if __name__ == "__main__":
    unittest.main()
