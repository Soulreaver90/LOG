r"""
test_piccolo_gi_scene.py - Tests for patches.piccolo_gi_scene (r29-r32): Piccolo gives Gohan the gi on the Lookout.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_piccolo_gi_scene.py -v
Builds build_list_dev.txt in memory: "before" = the list up to piccolo_gi_scene with the art tables minus id 52 (the r28 bytes), "rom" = with it
alone (later patches have their own tests). The scene is walked from the type 5 words by each record's next
index, as scene_run 0x0800B520 does. Lines are laid out by the game's line breaker (test_rage_text.lines);
portraits run through portrait() and the cutscene hook (test_cutscene.portrait). Expected texts, ids, sets and
sites are restated from docs\tasks\2026-10-22-piccolo-gi-scene\piccolo-gi-scene.md, piccolo-gi-scene-report.md, r30.md (walk-ins, the
period), r31.md (Piccolo and Gohan stay, fly off after the last line, no cut back) and r32.md (the "Goku is
playable" lines after the fly-off), never imported from the patch module.
"""
import copy
import hashlib
import struct
import unittest
from pathlib import Path

import log2_build
import log_paths
from patches import piccolo_gi_scene
from tests.test_art_inject import art_input_without
from tests.test_cellgames_ssj import POS, diff, ext_sequence, ops, u32, words_naming
from tests.test_cutscene import portrait
from tests.test_rage_text import lines
from rom.log2_sprites import set_records
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, decompress, read_set

# ===== constants (brief and report) =====
R28_SHA1 = "eef01cf6aa37f660bbe0f07b87694d058252499c"
OLD_TABLE, OLD_WORDS, TYPE5 = 0x3DBDD4, 35, (0x3CF7E4, 0x3D1530)
REPLACED = {2: 0x3DB59C, 15: 0x3DB930, 20: 0x3DBABC, 31: 0x3DBD5C}      # index: old record (seq 3, 16, 21, 32)
WALK = list(range(0, 30)) + list(range(35, 45)) + [30, 31, 32, 33]      # indexes run in order; 34 is END
# r32: word 29 names the walk-offs copy (index 28 skips the lines), word 31 the new tail (SET 158, sound 62)
WALK_OFFS_AT, LINES_AT, TAIL_AT = 29, 30, 31
CHIME_RECORD, LINES_RECORD = 0x3DBD10, 0x3DBD18                         # vanilla words 29 and 30 (seq 30, 31)
PLAYABLE = "@^Goku is now an available character!\x0bYou are now playing as Goku."
SET_LITERAL, REVERSE_LITERAL, BLOCK_LITERAL, PLUS2_LITERAL = 0x959C, 0x42F0, 0xBE10, 0x26458
ARMOR_SSJ, GI_SSJ, PICCOLO = 59, 158, 103
GOHAN_SETS = {56, 57, 58, 59, 157, 158, 159, 160}
LINES = [(62, "Piccolo, can I have a new outfit just like yours?"), (3, "..."),
         (62, "You were my first teacher."), (3, "Yeah kid, it will make you look really sharp."),
         (115, "Thank you, it's awesome!"), (65, "You look great Gohan")]   # storyboard, "it's", r30 period
BLUE = (72, 160, 248)
CODE = {
    35: [(40, (30,)), (62, (0, 520, 400)), (55, (0, 2)), (31, (232, 320, 40)), (62, (103, 312, 400)),
         (55, (103, 3)), (62, (59, 496, 400)), (55, (59, 2)), (41, (30,)), (53, (59, 344, 400))],
    40: [(63, ()), (57, (103, 11))] + [(135, (59, *BLUE, 32))] * 3 + [
        (64, ()), (52, (59,)), (51, (158, 344, 400)), (55, (158, 2)), (55, (103, 3)), (73, (0, 158)),
        (57, (158, 4))],
    42: [(53, (0, 384, 400)), (55, (158, 3))],
    44: [(46, (26,)), (63, ()), (54, (103, 312, 504)), (52, (103,)), (54, (158, 344, 504)), (52, (158,)),
         (64, ()), (33, (0,)), (46, (28,))],
    31: [(27, (158,)), (46, (62,))]}
# r31: the walk-offs keep only Trunks (132) and Vegeta (137); r30 record slots (address, size) stay
WALK_OFFS = [(46, (26,)), (63, ()), (54, (132, 720, 488)), (52, (132,)), (54, (137, 736, 472)), (52, (137,)),
             (64, ())]
R30_SLOTS = {31: (0x89AF38, 75), 35: (0x89AF84, 77), 44: (0x89B118, 61)}
R30_TABLE = 0x89B158
# r32: r30's record 31 slot holds the walk-offs (40 bytes) and the tail (12 bytes in a 35-byte slot)
R32_SLOTS = {29: (0x89AF38, 40), 31: (0x89AF60, 35), 35: (0x89AF84, 77), 44: (0x89B118, 61)}
R32_LENGTHS = {29: 40, 31: 12, 44: 48}
SCENE_CAMERA, GOKU_SPOT, PICCOLO_SPOT, GOHAN_SPOT = (232, 320), (384, 400), (312, 400), (344, 400)
ARGS = {27: 1, 31: 3, 33: 1, 40: 1, 41: 1, 43: 1, 46: 1, 51: 3, 52: 1, 53: 3, 54: 3, 55: 2, 57: 2, 62: 3, 63: 0,
        64: 0, 73: 2, 135: 5}                                           # values each handler pops (listings)
# r30 walk-ins (listings, docs\tasks\2026-10-23-r30-build\r30-build-report.md section 1)
EXT_TABLE = 0x3B5D28                                                    # ext n handler = word EXT_TABLE + 4n
WALK_CTOR, FLY_CTOR = 0x0800D584, 0x0800D5B8                           # move states of ext 53 and ext 54
SET_STATE_CALL = "bl 0x8021d2c"                                         # actor vtable +0x28 (set state)
# r30 camera hand-off: follow update @0x0800D9F8 aims at the box centre minus (120, 84) and closes 3/64 of the x
# gap and 9/128 of the y gap each frame, in 1/1024 px; the player box is 16x8 (+0x154/+0x155 in the r29 states)
FOLLOW_OFFSET, PLAYER_BOX, VIEW = (120, 84), (16, 8), (240, 160)
LEFT_EDGE = (257, 385, 304, 424)            # map 9,1 region 1 rect (the Lookout's left edge), map item 0x08403FE8
VIEW_W = 240
LOG = Path(__file__).resolve().parents[3]
BUILD = log_paths.BUILDS

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        i = names.index("piccolo_gi_scene")
        staged = {"art_input": art_input_without(52)}      # r36: art_inject's table holds 52; the r28 bytes do not
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i], staged)
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        log2_build.apply_patches(rom, alloc, ["piccolo_gi_scene"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


# ===== scene helpers =====

def table_of(rom: bytes) -> int:
    return u32(rom, TYPE5[0]) - ROM_BASE


def walk(rom: bytes) -> list:
    """[(index, record offset)] from index 0, by each record's u16 next index, to the first END word."""
    t, out, i = table_of(rom), [], 0
    for _ in range(80):
        w = u32(rom, t + 4 * i)
        if w < 0x10000:
            return out
        rec = w - ROM_BASE
        out.append((i, rec))
        i = struct.unpack_from("<H", rom, rec)[0]
    raise AssertionError("scene does not end")


def text_lines(rom: bytes, rec: int) -> list:
    return lines(rom, rec + 4 + ROM_BASE)


def set_header(rom: bytes, set_id: int) -> int:
    return u32(rom, u32(rom, SET_LITERAL) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE


def frame_word(rom: bytes, pid: int) -> int:
    return u32(rom, u32(rom, BLOCK_LITERAL) - ROM_BASE + 4 + 4 * pid)


def entry_of(rom: bytes, set_id: int) -> int:
    """Appearance entry ext 73 stores for set_id (reverse lookup copy, entries 0-22)."""
    rev = u32(rom, REVERSE_LITERAL) - ROM_BASE
    return next(e for e in range(23) if rom[rev + 20 * e + 1] == set_id)


def events(rom: bytes) -> list:
    """[(index, 'ext', n, args) or (index, 'text', portrait, text)] along the walk."""
    out = []
    for i, rec in walk(rom):
        if rom[rec + 2] == 0:
            out += [(i, "ext", n, args) for n, args in ext_sequence(rom, rec)]
        elif rom[rec + 2] == 1:
            end = rom.index(b"\0", rec + 4)
            out.append((i, "text", rom[rec + 3], rom[rec + 4:end].decode("latin1")))
        elif rom[rec + 2] == 2:                                          # webfoot stream at +4
            out.append((i, "text", rom[rec + 3], decompress(rom, rec + 4)[0].rstrip(b"\0").decode("latin1")))
        else:
            out.append((i, "type", rom[rec + 2], rom[rec + 3]))
    return out


# ===== tests =====

class SceneTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.table = table_of(cls.rom)

    def test_before_is_r28(self):
        self.assertEqual(hashlib.sha1(self.before).hexdigest(), R28_SHA1)

    def test_both_type5_words_name_the_new_table(self):
        self.assertEqual([u32(self.before, w) for w in TYPE5], [OLD_TABLE + ROM_BASE] * 2)
        self.assertEqual([u32(self.rom, w) for w in TYPE5], [self.table + ROM_BASE] * 2)
        self.assertEqual(words_naming(self.before, OLD_TABLE + ROM_BASE), list(TYPE5))
        self.assertEqual(words_naming(self.rom, OLD_TABLE + ROM_BASE), [])
        self.assertEqual(words_naming(self.rom, self.table + ROM_BASE), list(TYPE5))
        self.assertTrue(log2_build.BASE_SIZE <= self.table < 0xF00000)

    def test_new_table_keeps_every_other_word(self):
        new = [u32(self.rom, self.table + 4 * i) for i in range(45)]
        old = [u32(self.before, OLD_TABLE + 4 * i) for i in range(OLD_WORDS)]
        for i in range(OLD_WORDS):
            with self.subTest(index=i):
                if i in REPLACED:
                    self.assertEqual(old[i], REPLACED[i] + ROM_BASE)
                    self.assertNotEqual(new[i], old[i])
                elif i == WALK_OFFS_AT:                                 # r32: the chime record drops out
                    self.assertEqual((old[i], new[i]), (CHIME_RECORD + ROM_BASE, R32_SLOTS[i][0] + ROM_BASE))
                else:
                    self.assertEqual(new[i], old[i])
        self.assertEqual(new[34], 0)                                    # END, resume index 0
        self.assertTrue(all(w >= ROM_BASE + log2_build.BASE_SIZE for w in new[35:]))

    def test_old_table_and_records_unchanged(self):
        self.assertEqual(self.rom[OLD_TABLE:OLD_TABLE + 4 * OLD_WORDS],
                         self.before[OLD_TABLE:OLD_TABLE + 4 * OLD_WORDS])
        for rec in REPLACED.values():
            self.assertEqual(self.rom[rec:rec + 0x60], self.before[rec:rec + 0x60], hex(rec))

    def test_walk_order(self):
        self.assertEqual([i for i, _ in walk(self.before)], list(range(34)))
        self.assertEqual([i for i, _ in walk(self.rom)], WALK)


class StoryboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]
        cls.recs = dict(walk(cls.rom))

    def test_lines_in_order_with_portraits(self):
        got = [(p, t) for i, kind, p, t in events(self.rom) if kind == "text" and i >= 35]
        self.assertEqual(got, LINES)

    def test_apostrophe_has_a_glyph_and_no_control_bytes(self):
        a = text_lines(self.rom, self.recs[41])
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0][0], b"Thank you, it's awesome!")
        self.assertIn(b"'", self.before[0x3DBB60:0x3DBBAA])           # vanilla "Here's the Dragon Model"
        for i in (36, 37, 38, 39, 41, 43):
            body = self.rom[self.recs[i] + 4:self.rom.index(b"\0", self.recs[i] + 4)]
            self.assertFalse(set(body) & {0x0A, 0x0B}, i)

    def test_each_line_is_one_box_that_fits(self):
        vanilla = [len(text_lines(self.before, r)) for i, r in walk(self.before)
                   if self.before[r + 2] == 1 and self.before[r + 3] != 0]
        for i in (36, 37, 38, 39, 41, 43):
            with self.subTest(index=i):
                got = text_lines(self.rom, self.recs[i])
                self.assertTrue(all(w <= 0x90 for _, w, _, _ in got))
                self.assertEqual(got[-1][3], 0)                         # ends at 00, no box break
                self.assertLessEqual(len(got), max(vanilla))

    def test_code_records(self):
        for i, want in CODE.items():
            with self.subTest(index=i):
                self.assertEqual(self.rom[self.recs[i] + 1:self.recs[i] + 3], b"\0\0")
                self.assertEqual(ext_sequence(self.rom, self.recs[i]), want)

    def test_code_records_end_with_an_empty_stack(self):
        for i in CODE:
            depth = 0
            for _, op, arg in ops(self.rom, self.recs[i] + 3):
                if op in (0, 1, 29):
                    depth += len(arg)
                elif op == 2:
                    self.assertGreaterEqual(depth, ARGS[arg], (i, arg))
                    depth -= ARGS[arg]
                elif op != 17:
                    self.fail(f"record {i}: op {op}")
            self.assertEqual(depth, 0, i)

    def test_seq3_copy_is_armor_ssj_and_entry_0(self):
        a = ext_sequence(self.before, REPLACED[2])
        b = ext_sequence(self.rom, self.recs[2])
        swap = {(51, (56, 840, 432)): (51, (59, 840, 432)), (55, (56, 1)): (55, (59, 1)),
                (73, (0, 158)): (73, (0, 53))}
        self.assertEqual(b, [swap.get(x, x) for x in a])
        self.assertTrue(all(k in a for k in swap))

    def test_seq32_copy_is_the_trunks_and_vegeta_walk_offs_then_the_new_scene(self):
        a = ext_sequence(self.before, REPLACED[31])
        b = ext_sequence(self.rom, self.recs[WALK_OFFS_AT])
        tail = [(33, (0,)), (27, (158,)), (46, (62,))]
        self.assertEqual(a[-3:], tail)
        self.assertEqual(a[3:10], WALK_OFFS)                              # vanilla: sound, group Trunks, Vegeta
        self.assertEqual(b, WALK_OFFS)
        self.assertEqual(self.rom[self.recs[WALK_OFFS_AT]], 35)
        # r32: the tail is split around the lines, each op once and in r28 order
        self.assertEqual(ext_sequence(self.rom, self.recs[44])[-2:], [tail[0], (46, (28,))])
        self.assertEqual(ext_sequence(self.rom, self.recs[TAIL_AT]), tail[1:])

    def test_gohan_line_copies_change_only_the_portrait(self):
        for i, length in ((15, 0x64), (20, 0x54)):
            old, new = self.before[REPLACED[i]:REPLACED[i] + length], self.rom[self.recs[i]:self.recs[i] + length]
            self.assertEqual((old[3], new[3]), (121, 62))
            self.assertEqual(old[:3] + old[4:], new[:3] + new[4:])
            self.assertEqual(self.recs[i] % 4, 0)                      # type 2 stream must stay 4-aligned

    def test_staging_left_edge_and_off_screen_entries(self):
        x0, y0, x1, y1 = LEFT_EDGE
        piccolo, gohan, goku = (103, 312, 400), (59, 496, 400), (0, 520, 400)
        self.assertTrue(x1 < piccolo[1] <= x1 + 16 and y0 <= piccolo[2] <= y1)
        camera_x = CODE[35][3][1][0]
        self.assertGreaterEqual(gohan[1], camera_x + VIEW_W)
        self.assertGreaterEqual(goku[1], camera_x + VIEW_W + 8)          # 32 px frames sit at dx -8


class ActorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = built()["rom"]

    def test_every_commanded_actor_exists(self):
        alive, spawned = {0}, set()
        for i, kind, n, args in events(self.rom):
            if kind != "ext":
                continue
            if n == 51:
                set_id = args[-3]                                       # seq 3 and 27 spawn by leader branch
                if i >= 35 or set_id in GOHAN_SETS:
                    self.assertNotIn(set_id, alive, (i, n, args))
                alive.add(set_id)
                spawned.add(set_id)
                continue
            for p in POS.get(n, []):
                if args and len(args) >= -p and args[p] in spawned:
                    self.assertIn(args[p], alive, (i, n, args))
            if n == 52:
                alive.discard(args[0])
            self.assertLessEqual(len(alive & GOHAN_SETS), 1, (i, n, args))
        self.assertFalse({PICCOLO, ARMOR_SSJ, GI_SSJ} & alive)            # nothing of the new scene stays

    def test_gohan_look_per_line(self):
        alive, looks = set(), []
        for i, kind, n, args in events(self.rom):
            if kind == "ext" and n == 51:
                alive.add(args[0])
            elif kind == "ext" and n == 52:
                alive.discard(args[0])
            elif kind == "text" and i >= 35 and n in (62, 115):
                looks.append((n, sorted(alive & GOHAN_SETS)))
        self.assertEqual(looks, [(62, [59]), (62, [59]), (115, [158])])

    def test_sets_and_animations(self):
        vanilla_59 = u32(log2_build.BASE.read_bytes(), 0x3B4E90 + 4 * (59 - 7)) - ROM_BASE
        self.assertEqual(set_header(self.rom, ARMOR_SSJ), vanilla_59)     # armor Super Saiyan, untouched art
        for set_id, anims in ((PICCOLO, (0, 1, 11)), (ARMOR_SSJ, (0, 1)), (GI_SSJ, (0, 4))):
            s = read_set(self.rom, set_header(self.rom, set_id))
            self.assertEqual(s["slot"], 0x400, set_id)
            for a in anims:
                self.assertTrue(all(s["ptrs"][4 * a + d] for d in range(4)), (set_id, a))


class PortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom = b["rom"]
        cls.base = log2_build.BASE.read_bytes()

    def gohan_entry_at_each_line(self) -> list:
        entry, out = None, []
        for i, kind, n, args in events(self.rom):
            if kind == "ext" and n == 73 and args[0] == 0:
                entry = entry_of(self.rom, args[1])
            elif kind == "text" and n in (62, 115):
                out.append((i, n, entry))
        return out

    def test_gohan_record_entry_at_each_line(self):
        self.assertEqual(self.gohan_entry_at_each_line(),
                         [(15, 62, 0), (20, 62, 0), (36, 62, 0), (38, 62, 0), (41, 115, 5)])

    def test_armor_ssj_portrait_shows_before_the_flash(self):
        armor = u32(self.base, 0x3EC9D0 + 4 + 4 * 62)                   # vanilla block word 62
        self.assertEqual(portrait(self.rom, 62, 0)[0], armor)
        self.assertEqual(portrait(self.rom, 62, 5)[0], frame_word(self.rom, 115))   # why entry 0 is needed

    def test_gi_goku_and_piccolo_portraits(self):
        self.assertEqual(portrait(self.rom, 115, 5)[0], frame_word(self.rom, 115))
        self.assertEqual(portrait(self.rom, 65, 5)[0], frame_word(self.rom, 65))
        table = u32(self.rom, PLUS2_LITERAL) - ROM_BASE
        self.assertEqual(self.rom[table + 20 * 6 + 2], 90)              # Piccolo entry 6 (set 103) +2
        self.assertEqual(portrait(self.rom, 3, 0, others=6)[0], frame_word(self.rom, 90))


class FlagAndControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ev = events(built()["rom"])

    def test_flag_158_once_after_the_new_scene(self):
        sets = [i for i, kind, n, args in self.ev if kind == "ext" and n == 27 and args == (158,)]
        self.assertEqual(sets, [TAIL_AT])
        order = list(dict.fromkeys(i for i, *_ in self.ev))                # record indexes, each once
        self.assertEqual(order[-5:], [44, LINES_AT, TAIL_AT, 32, 33])

    def test_goku_leads_and_the_end_matches_r28(self):
        self.assertIn((26, "ext", 70, (4,)), self.ev)
        self.assertEqual(self.ev[-2], (32, "text", 0, "@^Journal Updated!"))
        self.assertEqual(self.ev[-1], (33, "ext", 86, (1,)))
        last73 = [args for _, kind, n, args in self.ev if kind == "ext" and n == 73 and args[0] == 0][-1]
        self.assertEqual(last73, (0, 158))                               # Gohan's record ends as in r28


class DiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom = b["before"], b["rom"]
        cls.new_used = b["used"][len(b["alloc_before"].used()):]
        cls.changed = diff(cls.before, cls.rom)

    def test_build_list_runs_piccolo_gi_scene_after_fullpower_ssj(self):
        names = built()["names"]
        i = names.index("piccolo_gi_scene")
        self.assertEqual(names[i - 1:i + 2], ["fullpower_ssj", "piccolo_gi_scene", "superperfect_cell"])

    def test_earlier_allocations_unchanged(self):
        n = len(built()["alloc_before"].used())
        self.assertEqual(built()["used"][:n], built()["alloc_before"].used())
        self.assertTrue(all(a >= 0x89ADB3 and a + s <= 0xF00000 for a, s in self.new_used))

    def test_only_named_sites_change(self):
        sites = [(w, w + 4) for w in TYPE5] + [(a, a + n) for a, n in self.new_used]
        self.assertEqual([hex(i) for i in self.changed if not any(a <= i < e for a, e in sites)], [])
        for a, e in sites:
            self.assertTrue(any(a <= i < e for i in self.changed), hex(a))

    def test_r32_file_holds_this_scene(self):              # superperfect_cell writes none of these bytes
        path = BUILD / "log2_poc_r32.gba"
        if not path.exists():
            self.skipTest("r32 not built")
        r32 = path.read_bytes()
        for a, n in [(w, 4) for w in TYPE5] + self.new_used:
            self.assertEqual(r32[a:a + n], self.rom[a:a + n], hex(a))

    def test_r32_keeps_every_r30_address(self):           # r30's record 31 slot now holds two records
        recs, notes = dict(walk(self.rom)), built()["notes"]["piccolo_gi_scene"]
        self.assertEqual(notes["table"], R30_TABLE)
        for i, (at, size) in R32_SLOTS.items():
            self.assertEqual(recs[i], at, i)
            self.assertIn((at, size), self.new_used, i)
        self.assertEqual(sum(R32_SLOTS[i][1] for i in (WALK_OFFS_AT, TAIL_AT)), R30_SLOTS[31][1])
        self.assertEqual(R32_SLOTS[WALK_OFFS_AT][0], R30_SLOTS[31][0])
        for i, length in R32_LENGTHS.items():
            at, size = R32_SLOTS[i]
            self.assertEqual(self.rom[at + length - 1], 0x11, i)            # end op, then the unused tail
            self.assertEqual(set(self.rom[at + length:at + size]), {0xFF} if size > length else set(), i)

    def test_r30_to_r31_changes_only_records_31_35_44(self):
        r30, r31 = BUILD / "log2_poc_r30.gba", BUILD / "log2_poc_r31.gba"
        if not (r30.exists() and r31.exists()):
            self.skipTest("r30 or r31 missing")
        a, b = r30.read_bytes(), r31.read_bytes()
        scene = [(at, at + size) for at, size in R30_SLOTS.values()]
        changed = [i for i in diff(a, b) if any(s <= i < e for s, e in scene)]
        self.assertTrue(changed)
        rec35 = [i - R30_SLOTS[35][0] for i in changed if R30_SLOTS[35][0] <= i < sum(R30_SLOTS[35])]
        self.assertEqual([(o, a[R30_SLOTS[35][0] + o], b[R30_SLOTS[35][0] + o]) for o in rec35],
                         [(0x28, 51, 62), (0x38, 51, 62)])                   # spawn op bytes become move


def set_state_args(rom: bytes, ctor: int) -> list:
    """The state ids a move-state constructor passes to the actor's set-state method, in order."""
    text = [t for _, t in listing(rom, ctor, 40)]
    end = text.index("pop {r4,r5,r6,pc}", 9)                          # the first pop is the alloc-failed exit
    return [text[k - 1].split("#")[1] for k in range(end) if text[k] == SET_STATE_CALL]


def follow(cam: tuple, target: tuple, frames: int) -> tuple:
    """Camera (x, y) in 1/1024 px after n follow updates, as @0x0800D9F8 eases (asr rounds down)."""
    x, y = cam
    for _ in range(frames):
        x += (3 * (target[0] - x)) >> 6
        y += (9 * (target[1] - y)) >> 7
    return x, y


class WalkInTests(unittest.TestCase):
    """r30: why Gohan and Goku flew in r29, and that they walk now."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.recs = b["rom"], dict(walk(b["rom"]))
        cls.base = log2_build.BASE.read_bytes()

    def test_ext_53_walks_and_ext_54_flies(self):
        self.assertEqual(u32(self.base, EXT_TABLE + 4 * 53), 0x08009D4B)  # ext 53 > 0x0800E004 > 0x08010898
        self.assertEqual(u32(self.base, EXT_TABLE + 4 * 54), 0x08009E31)  # ext 54 > 0x0800E838
        self.assertEqual(set_state_args(self.base, WALK_CTOR), ["0x1"])          # state 1: anim 1, walk
        self.assertEqual(set_state_args(self.base, FLY_CTOR), ["0x1", "0xc"])    # then state 12: anim 12, fly
        walk_speed = [t for _, t in listing(self.base, 0x08010898, 9)][5:7]
        fly_speed = [t for _, t in listing(self.base, 0x0800E838, 7)][5:7]
        self.assertEqual(walk_speed, ["mov r0,#0xff", "add r0,#0x1"])              # 0x100: 1 px a frame
        self.assertEqual(fly_speed, ["mov r0,#0x1", "lsl r0,r0,#9"])               # 0x200: 2 px a frame
        state12 = [t for _, t in listing(self.base, 0x0800E7A0, 9)]
        self.assertEqual(state12[5:8], ["ldr r0,[r1,#0x48]", "add r0,#0xff", "add r0,#0xd"])   # set + 0x10C

    def test_both_walkers_have_a_walk_anim(self):
        for set_id in (ARMOR_SSJ, 61):                                  # the player is Goku Super Saiyan here
            s = read_set(self.rom, set_header(self.rom, set_id))
            self.assertTrue(all(s["ptrs"][4 * 1 + d] for d in range(4)), set_id)

    def test_walk_ins_use_ext_53_and_only_the_fly_off_flies(self):
        moves = [(i, n, args) for i, kind, n, args in events(self.rom) if kind == "ext" and n in (53, 54) and i >= 35]
        self.assertEqual(moves, [(35, 53, (59, 344, 400)), (42, 53, (0, 384, 400)),
                                 (44, 54, (103, 312, 504)), (44, 54, (158, 344, 504))])

    def test_walk_op_bytes_against_r29(self):                       # r29 report section 4: 77 and 20 bytes
        r29 = BUILD / "log2_poc_r29.gba"
        if not r29.exists():
            self.skipTest("r29 missing")
        old = r29.read_bytes()
        for i, length, changes in ((35, 77, {0x28: (51, 62), 0x38: (51, 62), 75: (54, 53)}), (42, 20, {11: (54, 53)})):
            rec = self.recs[i]
            self.assertEqual(rec, u32(old, u32(old, TYPE5[0]) - ROM_BASE + 4 * i) - ROM_BASE)   # same address
            diff_at = {k: (old[rec + k], self.rom[rec + k]) for k in range(length) if old[rec + k] != self.rom[rec + k]}
            self.assertEqual(diff_at, changes, i)                        # r30 walk (75, 11), r31 move (0x28, 0x38)
            self.assertEqual(self.rom[rec + length - 1], 0x11, i)


class StayTests(unittest.TestCase):
    """r31 item 1: Piccolo and Gohan do not leave in the walk-offs; they are moved, not spawned, for the scene."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.recs = b["rom"], b["before"], dict(walk(b["rom"]))
        cls.ev = events(cls.rom)

    def test_walk_offs_are_the_vanilla_trunks_and_vegeta_bytes(self):
        vanilla = self.before[REPLACED[31] + 0x14:REPLACED[31] + 0x38]      # sound 26 ; group 132, 137
        rec = self.recs[WALK_OFFS_AT]
        self.assertEqual(self.rom[rec + 3:rec + 3 + len(vanilla)], vanilla)
        self.assertEqual(self.rom[rec + 3 + len(vanilla)], 0x11)

    def test_piccolo_and_gohan_stay_until_record_44(self):
        stay = {PICCOLO, ARMOR_SSJ}
        removes = [(i, args[0]) for i, kind, n, args in self.ev
                   if kind == "ext" and n == 52 and args[0] in stay | {GI_SSJ}]
        self.assertEqual(removes, [(40, ARMOR_SSJ), (44, PICCOLO), (44, GI_SSJ)])   # 40 is the gi swap, in place
        spawned = [(i, args[-3]) for i, kind, n, args in self.ev if kind == "ext" and n == 51 and args[-3] in stay]
        self.assertEqual(spawned, [(2, ARMOR_SSJ), (2, PICCOLO), (26, PICCOLO)])   # seq 3, or seq 27 if he led

    def test_record_35_moves_them_under_black(self):
        seq = CODE[35]
        moves = [args for n, args in seq if n == 62 and args[0] in (PICCOLO, ARMOR_SSJ)]
        self.assertEqual(moves, [(103, 312, 400), (59, 496, 400)])
        self.assertNotIn(51, [n for n, _ in seq])
        self.assertTrue(seq.index((40, (30,))) < seq.index((62, (103, 312, 400))) < seq.index((41, (30,))))
        self.assertEqual(ext_sequence(self.rom, self.recs[35]), seq)

    def test_ext_62_moves_npcs_in_vanilla(self):                     # vanilla record rom:0x3B8566
        base = log2_build.BASE.read_bytes()
        moved = {args[-3] for n, args in ext_sequence(base, 0x3B8566) if n == 62}
        self.assertEqual(moved, {60, PICCOLO, 53})                         # NPC Goku, Piccolo, Gohan

    def test_old_seq_32_is_named_only_by_the_dead_table(self):
        self.assertEqual(words_naming(self.rom, REPLACED[31] + ROM_BASE), [OLD_TABLE + 4 * 31])
        self.assertEqual(words_naming(self.rom, OLD_TABLE + ROM_BASE), [])


class FlyOffTests(unittest.TestCase):
    """r31 item 2: after "You look great Gohan", Piccolo and gi Super Saiyan Gohan fly off screen, then leave."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.recs = b["rom"], b["before"], dict(walk(b["rom"]))

    def test_fly_off_follows_the_last_line(self):
        order = [i for i, _ in walk(self.rom)]
        self.assertEqual(order[order.index(43) + 1], 44)
        self.assertEqual([(p, t) for i, kind, p, t in events(self.rom) if kind == "text" and i == 43], [LINES[-1]])

    def test_both_fly_in_one_group_then_leave(self):
        seq = CODE[44]
        group = seq[seq.index((63, ())) + 1:seq.index((64, ()))]
        self.assertEqual(group, [(54, (103, 312, 504)), (52, (103,)), (54, (158, 344, 504)), (52, (158,))])
        self.assertEqual(seq[0], (46, (26,)))                            # the vanilla walk-off sound

    def test_direction_is_the_vanilla_walk_off_direction(self):      # vanilla seq 32: every flight goes down
        starts = {args[-3]: args[-2:] for n, args in ext_sequence(self.before, REPLACED[2]) if n == 51}
        for n, (set_id, x, y) in [(n, a) for n, a in ext_sequence(self.before, REPLACED[31]) if n == 54]:
            sx, sy = starts[set_id]
            self.assertGreater(y - sy, abs(x - sx), set_id)                 # facing 0, down (larger axis)
        here = {PICCOLO: PICCOLO_SPOT, GI_SSJ: GOHAN_SPOT}
        for n, (set_id, x, y) in [(n, a) for n, a in CODE[44] if n == 54]:
            self.assertEqual(x, here[set_id][0])
            self.assertGreater(y - here[set_id][1], 0)

    def test_they_leave_the_view_before_removal(self):
        cam_y = SCENE_CAMERA[1]
        for n, (set_id, _, y) in [(n, a) for n, a in CODE[44] if n == 54]:
            recs = [r for r in set_records(self.rom, set_header(self.rom, set_id)) if r["anim"] == 12 and r["dir"] == 0]
            self.assertTrue(recs, set_id)
            self.assertGreaterEqual(y + min(r["dy"] for r in recs), cam_y + VIEW[1], set_id)   # sprite top below

    def test_fly_sets_have_the_fly_anim_in_every_dir(self):
        for set_id in (PICCOLO, GI_SSJ):
            s = read_set(self.rom, set_header(self.rom, set_id))
            self.assertTrue(all(s["ptrs"][4 * 12 + d] for d in range(4)), set_id)

    def test_gohan_flies_as_gi_super_saiyan(self):
        alive = set()
        for i, kind, n, args in events(self.rom):
            if kind == "ext" and n == 51:
                alive.add(args[-3])
            elif kind == "ext" and n == 52:
                alive.discard(args[0])
            elif kind == "ext" and n == 54 and i == 44:
                self.assertIn(args[0], alive)
                self.assertTrue(args[0] in (PICCOLO, GI_SSJ))
        self.assertEqual(entry_of(self.rom, GI_SSJ), 5)                     # gi Super Saiyan record entry


class HandBackTests(unittest.TestCase):
    """r31 item 3: no cut back. Goku keeps his spot; the follow camera eases from the scene camera."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.recs = b["rom"], dict(walk(b["rom"]))
        cls.base = log2_build.BASE.read_bytes()
        cls.ev = events(cls.rom)

    def after_last_line(self) -> list:
        k = max(j for j, e in enumerate(self.ev) if e[1] == "text" and e[0] == 43)
        return self.ev[k + 1:]

    def test_no_fade_wait_or_camera_jump_after_the_last_line(self):
        ops = [n for i, kind, n, _ in self.after_last_line() if kind == "ext"]
        self.assertFalse({40, 41, 42, 43, 31} & set(ops), ops)
        self.assertEqual(ops.count(33), 1)

    def test_goku_keeps_his_spot(self):
        player = [(i, n, args) for i, kind, n, args in self.ev if kind == "ext" and args and args[0] == 0
                  and n in (53, 54, 55, 62)]
        self.assertEqual(player[-1], (42, 53, (0, *GOKU_SPOT)))           # nothing moves or turns him after
        self.assertFalse([e for e in self.after_last_line() if e[1] == "ext" and e[2] in (53, 54, 55, 62)
                          and e[3][0] == 0])

    def test_follow_starts_from_the_scene_camera(self):
        cams = [(i, args) for i, kind, n, args in self.ev if kind == "ext" and n == 31 and i >= 35]
        self.assertEqual(cams, [(35, (*SCENE_CAMERA, 40))])

    def test_follow_eases_40_px_right_and_0_down(self):
        gx, gy = GOKU_SPOT
        target = ((gx + PLAYER_BOX[0] // 2 - FOLLOW_OFFSET[0]) << 10,
                  (gy + PLAYER_BOX[1] // 2 - FOLLOW_OFFSET[1]) << 10)
        self.assertEqual((target[0] >> 10, target[1] >> 10), (272, 320))
        start = tuple(v << 10 for v in SCENE_CAMERA)
        self.assertEqual(((target[0] - start[0]) >> 10, (target[1] - start[1]) >> 10), (40, 0))
        gaps = [(target[0] - follow(start, target, f)[0]) / 1024 for f in (0, 1, 15, 30, 60, 90)]
        self.assertAlmostEqual(gaps[1], 40 - 40 * 3 / 64, delta=0.01)      # 1.9 px in the first frame
        self.assertTrue(9 < gaps[3] < 10 and 2 < gaps[4] < 2.5 and gaps[5] < 0.6, gaps)
        self.assertEqual(follow(start, target, 90)[1], target[1])

    def test_goku_is_on_screen_through_the_ease(self):
        gx, gy = GOKU_SPOT
        start, target = tuple(v << 10 for v in SCENE_CAMERA), (272 << 10, 320 << 10)
        for frames in range(0, 120):
            x, y = follow(start, target, frames)
            sx, sy = gx - (x >> 10), gy - (y >> 10)
            self.assertTrue(8 <= sx <= VIEW[0] - 24 and 24 <= sy <= VIEW[1] - 8, (frames, sx, sy))

    def test_follow_update_constants_are_the_listing(self):
        text = [t for _, t in listing(self.base, 0x0800D9F8, 46)]
        self.assertEqual(text[18], "sub r1,#0x78")
        self.assertEqual(text[27], "sub r1,#0x54")
        self.assertEqual(text[33:36], ["lsl r3,r1,#1", "add r1,r3,r1", "asr r1,r1,#6"])   # 3/64
        self.assertEqual(text[41:44], ["lsl r3,r1,#3", "add r1,r3,r1", "asr r1,r1,#7"])   # 9/128

    def test_player_box_in_the_states(self):
        path = BUILD / "log2_poc_r29_chamber2.ss3"
        if not path.exists():
            self.skipTest("chamber2 ss3 missing")
        from rom import state_dump
        st = state_dump.load_state(path)
        iw, wr = st[0x19000:0x21000], st[0x21000:0x61000]
        p = u32(iw, 0x1FA8) - 0x02000000
        self.assertEqual((wr[p + 0x154], wr[p + 0x155]), PLAYER_BOX)


class PlayableLinesTests(unittest.TestCase):
    """r32: the "Goku is playable" lines show after the fly-off, as the last box before "Journal Updated!"."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.recs = b["rom"], b["before"], dict(walk(b["rom"]))
        cls.ev, cls.old_ev = events(cls.rom), events(cls.before)
        cls.base = log2_build.BASE.read_bytes()

    def test_the_lines_are_the_vanilla_record(self):
        self.assertEqual(self.recs[LINES_AT], LINES_RECORD)
        self.assertEqual(self.rom[LINES_RECORD:LINES_RECORD + 0x44], self.base[LINES_RECORD:LINES_RECORD + 0x44])
        self.assertEqual([e for e in self.ev if e[0] == LINES_AT], [(LINES_AT, "text", 0, PLAYABLE)])
        self.assertEqual(len(PLAYABLE.split("\x0b")), 2)                    # two boxes
        self.assertEqual(self.rom[LINES_RECORD], TAIL_AT)                     # its next index stays 31

    def test_vanilla_showed_them_before_the_walk_offs(self):
        order = list(dict.fromkeys(i for i, *_ in self.old_ev))
        self.assertEqual(order[-6:], [28, 29, LINES_AT, 31, 32, 33])
        first = [e[0] for e in self.old_ev].index(29)
        self.assertEqual(self.old_ev[first], (29, "ext", 46, (28,)))              # the chime, then the lines

    def test_lines_show_once_between_the_fly_off_and_the_journal(self):
        at = [k for k, e in enumerate(self.ev) if e[1] == "text" and e[3] == PLAYABLE]
        self.assertEqual(len(at), 1)
        fly = max(k for k, e in enumerate(self.ev) if e[:3] == (44, "ext", 54))
        journal = self.ev.index((32, "text", 0, "@^Journal Updated!"))
        last_line = self.ev.index((43, "text", 65, "You look great Gohan"))
        self.assertTrue(last_line < fly < at[0] < journal)

    def test_end_order_fly_off_lines_journal_control(self):
        self.assertEqual(self.ev[-10:], [
            (44, "ext", 54, (158, 344, 504)), (44, "ext", 52, (158,)), (44, "ext", 64, ()), (44, "ext", 33, (0,)),
            (44, "ext", 46, (28,)), (LINES_AT, "text", 0, PLAYABLE), (TAIL_AT, "ext", 27, (158,)),
            (TAIL_AT, "ext", 46, (62,)), (32, "text", 0, "@^Journal Updated!"), (33, "ext", 86, (1,))])
        self.assertEqual(u32(self.rom, table_of(self.rom) + 4 * 34), 0)         # then END: control

    def test_each_chime_stays_right_before_its_box(self):
        for ev in (self.old_ev, self.ev):
            k = [e[3] for e in ev].index(PLAYABLE)
            j = ev.index((32, "text", 0, "@^Journal Updated!"))
            self.assertEqual(ev[k - 1][1:], ("ext", 46, (28,)))
            self.assertEqual(ev[j - 1][1:], ("ext", 46, (62,)))

    def test_vanilla_plays_62_right_before_every_journal_box(self):
        hits = [k - 4 for k in range(len(self.base)) if self.base.startswith(b"@^Journal Updated!\0", k)]
        self.assertEqual(len(hits), 48)
        self.assertTrue(all(b"\x00\x3e\x02\x2e" in self.base[r - 24:r] for r in hits))

    def test_the_party_change_and_lead_stay_before_the_scene(self):
        party = [(i, n, args) for i, kind, n, args in self.ev
                 if kind == "ext" and n in (70, 79, 80, 82, 83, 98) and args[:1] == (4,)]      # Goku's record
        self.assertTrue(party and all(i == 26 for i, _, _ in party), party)
        self.assertIn((26, 70, (4,)), party)
        self.assertEqual(self.recs[26], u32(self.before, OLD_TABLE + 4 * 26) - ROM_BASE)     # vanilla seq 27
        order = [e[0] for e in self.ev]
        self.assertLess(order.index(26), order.index(35))
        self.assertLess(order.index(35), order.index(LINES_AT))

    def test_the_vanilla_chime_record_is_left_unused(self):
        self.assertNotIn(CHIME_RECORD, self.recs.values())
        self.assertEqual(words_naming(self.rom, CHIME_RECORD + ROM_BASE), [OLD_TABLE + 4 * WALK_OFFS_AT])
        self.assertEqual(self.rom[CHIME_RECORD:CHIME_RECORD + 8], self.base[CHIME_RECORD:CHIME_RECORD + 8])

    def test_r31_to_r32_changes_only_two_words_and_two_slots(self):
        r31, r32 = BUILD / "log2_poc_r31.gba", BUILD / "log2_poc_r32.gba"
        if not (r31.exists() and r32.exists()):
            self.skipTest("r31 or r32 missing")
        a, b = r31.read_bytes(), r32.read_bytes()
        sites = [(R30_TABLE + 4 * WALK_OFFS_AT, 4), (R30_TABLE + 4 * TAIL_AT, 4), R32_SLOTS[TAIL_AT], R32_SLOTS[44]]
        changed = diff(a, b)
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        self.assertTrue(all(any(s <= i < s + n for i in changed) for s, n in sites))
        self.assertEqual(len(changed), 24)
        self.assertEqual(u32(a, R30_TABLE + 4 * 32), u32(b, R30_TABLE + 4 * 32))           # Journal word kept


class FailClosedTests(unittest.TestCase):
    def fresh(self) -> tuple:
        b = built()
        return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])

    def assert_refused(self, rom: bytearray, alloc) -> None:
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            piccolo_gi_scene.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_each_checked_site_refuses(self):
        for off in (TYPE5[0], TYPE5[1], OLD_TABLE + 8, REPLACED[2] + 0x40, REPLACED[15] + 3, REPLACED[31] + 0x50,
                    0x3DBDA6, CHIME_RECORD + 4, LINES_RECORD):           # r32: the chime and the lines' next index
            with self.subTest(off=hex(off)):
                rom, alloc = self.fresh()
                rom[off] ^= 0x01
                self.assert_refused(rom, alloc)

    def test_second_run_and_missing_notes_refuse(self):
        rom, alloc = self.fresh()
        piccolo_gi_scene.apply(rom, alloc)
        self.assert_refused(rom, alloc)
        rom, alloc = self.fresh()
        del alloc.notes["fullpower_ssj"]
        self.assert_refused(rom, alloc)

    def test_reverse_lookup_change_refuses(self):
        rom, alloc = self.fresh()
        rev = u32(rom, REVERSE_LITERAL) - ROM_BASE
        rom[rev + 1] = 56                                                # entry 0 no longer names set 53
        self.assert_refused(rom, alloc)


class CopyTests(unittest.TestCase):
    def assert_copies(self, old: str, new: str) -> None:
        pairs = [(f"{old}.sav", f"{new}.sav"), (f"{old}_chamber2.sav", f"{new}_chamber2.sav"),
                 (f"{new}.gba", f"{new}_chamber2.gba")]
        pairs += [(f"{old}.ss{k}", f"{new}.ss{k}") for k in range(1, 6)]
        for src, dst in pairs:
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)

    def test_r29_saves_and_states_are_r28_copies(self):
        self.assert_copies("log2_poc_r28", "log2_poc_r29")

    def test_r30_saves_and_states_are_r29_copies(self):
        self.assert_copies("log2_poc_r29", "log2_poc_r30")

    def test_r32_saves_states_and_rom_pairs_are_copies(self):
        self.assert_copies("log2_poc_r31", "log2_poc_r32")
        for src, dst in (("log2_poc_r31_scouter.sav", "log2_poc_r32_scouter.sav"),
                         ("log2_poc_r32.gba", "log2_poc_r32_scouter.gba")):
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)


if __name__ == "__main__":
    unittest.main()
