r"""
test_superperfect_cell.py - Tests for patches.superperfect_cell (r30-r38): Super Perfect Cell after the self-destruct.

Run (from the LOG root):
  py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_superperfect_cell.py -v
Builds build_list_dev.txt in memory: "before" = the list up to superperfect_cell (r29 plus the r30 scene edits) with the
art tables minus id 52 (the r35 state: 52 vanilla), "rom" = the list up to and with superperfect_cell, with the
tables as they are now (r36: my portrait 52, so "before" to "rom" also shows art_inject's word and slot for
52; later patches such as r37's chamber_spar have their own tests). Scripts are decoded with test_cellgames_ssj's own decoder (a second shape to the patch's byte
list); the idle tick runs as thumb_dis text in the test_status interpreter (test_idle.run_ticks). Expected sites,
records and ids are restated from docs\tasks\2026-10-22-superperfect-study\superperfect-study-report.md, superperfect-aura-report.md,
r30.md, r31.md, r33.md (the scouter), r35.md (text and stats) and scripts\one-time\2026-10-23-r30-build\cell_sites_r29.txt, never imported
from the patch module. The scouter screens are restated from the r33 listings (scripts\one-time\2026-10-23-r33-build\listings\): the enemy
type match @0x080190D4, the database rows @0x08019204 and the name field of @0x0801790E; the text page from the r35
listings (scripts\one-time\2026-10-23-r35-build\listings\): the line counter @0x0801F7FC and text_wrapped @0x0801F702.
"""
import copy
import json
import unittest
from collections import Counter
from pathlib import Path

from PIL import Image

from art import art_tables as at
import log2_build
import log_paths
from rom.log2_sprites import image_to_tiles, set_records
from patches import art_inject, superperfect_cell
from tests.test_art_inject import art_input_without
from tests.test_cellgames_ssj import POS, calls, diff, ops, u32, words_naming
from tests.test_idle import HOOKED, formula, run_ticks, tick_target, vanilla
from rom.thumb_dis import listing
from rom.webfoot_decompress import ROM_BASE, read_set, unpack_frame

# ===== constants (study, aura report, brief) =====
SET_LITERAL, BLOCK_LITERAL = 0x959C, 0xBE10
CELL_HEADER, DEAD_58 = 0x242DBC, 0x2AB508
RETURN_TABLE, DEATH_TABLE = 0x3EB704, 0x3EC758
SITE_RECORDS = {0x3EACD0: 4, 0x3EB134: 8, 0x3EB21C: 2, 0x3EB6E8: 1, 0x3EB80C: 2, 0x3EBA4C: 1, 0x3EBC7E: 1,
                0x3EBD7C: 3, 0x89AB4C: 46}                       # record: actor bytes (cell_sites_r29.txt, 68)
SET_WORDS = (0x409108, 0x409204)                                 # type 25 spawn +0x10, map 14,4 NPC +0xC
PORTRAIT_RECORDS = (0x3EAD70, 0x3EADF8, 0x3EB1C6, 0x3EB264, 0x3EB3D0,
                    0x3EB89E, 0x3EBA2A, 0x3EBC58, 0x3EBD68, 0x3EBDF0)   # study 4c: +3 = 40
SELF_DESTRUCT = (0x3EA534, 0x3EA5A8, 0x3EA5D0)                   # seq 2, 5, 7: Semi-Perfect 39, unchanged
EXT121_PARAMS = (0x3EB864, 0x3EB86D)                             # push 0,30 and the second 30 of push 30,30
TYPE25_STATS = (0x6D5904, 24)                                    # this fight's enemy type entry
STATS_OLD, STATS_NEW = (8230, 60, 59, 65), (9876, 72, 71, 78)    # r38 brief: HP, STR, POW, END +20% over vanilla
STATS_R35 = (9050, 66, 65, 72)                                   # r35 and r36 files (+10%), before r38
STAT_SITES = ((0x6D5904 + 4, 4), (0x6D5904 + 0xC, 3))           # HP u32; STR, POW, END bytes
SCOUTER, ENTRY = 0x6F8E40, 20                                    # 128 entries: name, text, set, portrait, type
ENEMY_TYPES = 0x6D56AC                                           # 24 B: HP u32 +4, STR +0xC, POW +0xD, END +0xE
SCOUTER_19 = (0x6F8FBC + 8, 0x6F8FBC + 0xC)                       # r31: set 30 -> 58, portrait 40 -> 52
NAME_19 = 0x6F8FBC                                               # r33: entry 19 +0 names the new string
TEXT_19 = NAME_19 + 4                                            # r35: entry 19 +4 names the new text
PERFECT_AT, PERFECT, SUPER = 0x6FA859, 'Cell, "Perfect"', 'Cell, "S. Perfect"'
PERFECT_TEXT_AT, PERFECT_TEXT_LEN = 0x6FA869, 415               # the shared text of 13-19 (vanilla), kept by 13-18
TEXT_FONT, WRAP = 0x2CC64, 0xA0                                  # @0x08018AAC, @0x08018ABA: font, 160 px
BRIEF = log_paths.R35_BRIEF
CELL_SPAWNS = {0x406F78: (79, 14), 0x406FF0: (78, 13), 0x408E4C: (21, 15), 0x408F18: (22, 16),
               0x408FC8: (23, 17), 0x4090C8: (24, 18), 0x4090F8: (25, 19)}   # spawn: (enemy type, entry)
ENEMY_FACTORY = 0x0800E77F                                       # spawn record +0; +8 type, +0x10 set
MENU_FONT, NAME_FIELD, LIST_WIDTH = 0x28724, (73, 166), 160      # info name ink between the frame borders
VANILLA_52 = 0x6BAF30
ART = log_paths.ART / "cell_aura" / "scale_15"
BUILD = log_paths.BUILDS
OWNER_52 = log_paths.PORTRAIT_SOURCES / "remaster" / "superperfect" / "owner" / "sp52_owner_v3.png"
OTHER_SETS = (30, 157, 158, 56, 59, 60, 61, 137)                 # vanilla tick, as before r30
SEEDS = (0, 0x7B, 0xEE, 0xFFF0)

_CACHE = {}


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(log2_build.DEV_LIST)
        i = names.index("superperfect_cell")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i], {"art_input": art_input_without(52)})
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc), names=names)
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i + 1])   # r36: the art tables hold 52
        _CACHE.update(rom=bytes(rom), notes=alloc.notes, used=alloc.used())
    return _CACHE


def with_stats(rom: bytes, stats: tuple) -> bytes:
    """rom with enemy type 25's HP (u32), STR, POW and END set to stats: how the r35 and r36 files differ from now."""
    out, off = bytearray(rom), TYPE25_STATS[0]
    out[off + 4:off + 8] = stats[0].to_bytes(4, "little")
    out[off + 0xC:off + 0xF] = bytes(stats[1:])
    return bytes(out)


def set_word(rom: bytes, set_id: int) -> int:
    return u32(rom, u32(rom, SET_LITERAL) - ROM_BASE + 4 * (set_id - 7)) - ROM_BASE


def block_word(rom: bytes, pid: int) -> int:
    return u32(rom, u32(rom, BLOCK_LITERAL) - ROM_BASE + 4 + 4 * pid)


def actor_values(rom: bytes, table: int, seqs: range, value: int) -> int:
    """How many set-arg slots (test_cellgames_ssj POS) hold value in the type 0 records of those seqs."""
    n = 0
    for seq in seqs:
        w = u32(rom, table + 4 * (seq - 1))
        if w < 0x10000 or rom[w - ROM_BASE + 1:w - ROM_BASE + 3] != b"\0\0":
            continue
        for _, ext, st in calls(rom, w - ROM_BASE + 3):
            n += sum(1 for p in POS.get(ext, []) if len(st) >= -p and st[p] == value)
    return n


def finds(rom: bytes, value: int) -> list:
    """File offsets of every copy of the u32 value, at any alignment."""
    pat, out = value.to_bytes(4, "little"), []
    at = rom.find(pat)
    while at >= 0:
        out.append(at)
        at = rom.find(pat, at + 1)
    return out


def records_per_row(rom: bytes, head: int) -> Counter:
    return Counter((r["anim"], r["dir"]) for r in set_records(rom, head))


def manifest() -> dict:
    """{(anim, dir, index): (png, key)} of my pick."""
    out = {}
    for m in json.loads((ART / "manifest.json").read_text(encoding="ascii")):
        for k in m["keys"]:
            out[(k["anim"], k["dir"], k["index"])] = (m["png"], k)
    return out


# ===== tests =====

class SetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]["superperfect_cell"]
        cls.head = set_word(cls.rom, 58)

    def test_set_58_is_new_and_set_30_stays(self):
        self.assertEqual(set_word(self.before, 58), DEAD_58)
        self.assertEqual(self.head, self.notes["set_58"])
        self.assertTrue(log2_build.BASE_SIZE <= self.head < log2_build.ART_REGION[0])
        self.assertEqual(set_word(self.rom, 30), CELL_HEADER)
        self.assertEqual(self.rom[CELL_HEADER:CELL_HEADER + 0x400], self.before[CELL_HEADER:CELL_HEADER + 0x400])
        self.assertEqual(self.rom[self.head:self.head + 0x4C], self.rom[CELL_HEADER:CELL_HEADER + 0x4C])  # slot, boxes

    def test_rows_are_set_30_rows_with_6_idle_records(self):
        new, old = read_set(self.rom, self.head), read_set(self.rom, CELL_HEADER)
        self.assertEqual((new["slot"], new["anims"]), (0x1000, old["anims"]))
        got, want = records_per_row(self.rom, self.head), records_per_row(self.rom, CELL_HEADER)
        self.assertEqual(set(got), set(want))
        for k, n in want.items():
            self.assertEqual(got[k], 6 if k[0] == 0 else n, k)

    def test_every_record_is_the_owner_pick(self):
        art = manifest()
        recs = {(r["anim"], r["dir"], r["index"]): r for r in set_records(self.rom, self.head)}
        self.assertEqual(set(recs), set(art))
        self.assertEqual(len(art), 176)
        tiles = {}
        for k, r in recs.items():
            png, key = art[k]
            self.assertEqual([r[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")],
                             [key[f] for f in ("dx", "dy", "w", "h", "attr0", "attr1")], k)
            if png not in tiles:
                with Image.open(ART / png) as img:
                    tiles[png] = image_to_tiles(img)
            kind, size, data, _ = unpack_frame(self.rom, r["header"])
            self.assertEqual((kind, size), (0, 0x1000), k)
            self.assertEqual(data, tiles[png], k)

    def test_only_the_set_table_and_the_hook_name_the_new_header(self):
        code, size = self.notes["code"], self.notes["size"]
        words = words_naming(self.rom, self.head + ROM_BASE)
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0], u32(self.rom, SET_LITERAL) - ROM_BASE + 4 * 51)
        self.assertTrue(code <= words[1] < code + size)               # the hook's literal pool


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]

    def test_cell_after_the_return_is_58_by_the_decoder(self):   # a second shape: 54 of the 68 (study 2a)
        def after_return(rom: bytes, set_id: int) -> int:
            return actor_values(rom, RETURN_TABLE, range(40, 66), set_id) + actor_values(rom, DEATH_TABLE,
                                                                                          range(1, 56), set_id)
        for rom, n30, n58 in ((self.before, 54, 0), (self.rom, 0, 54)):
            self.assertEqual((after_return(rom, 30), after_return(rom, 58)), (n30, n58))

    def test_cell_before_the_return_stays_30(self):
        for rom in (self.before, self.rom):
            self.assertEqual(actor_values(rom, RETURN_TABLE, range(1, 40), 30), 9)
            self.assertEqual(actor_values(rom, RETURN_TABLE, range(1, 40), 58), 0)

    def test_each_record_changes_only_its_actor_bytes(self):
        total = 0
        for rec, n in SITE_RECORDS.items():
            end = ops(self.before, rec + 3)[-1][0] + 1                  # the record's last `end`
            changed = [i for i in range(rec, end) if self.before[i] != self.rom[i]]
            self.assertEqual(len(changed), n, hex(rec))
            for i in changed:
                self.assertIn((self.before[i], self.rom[i]), ((0x1E, 0x3A), (0x3C, 0x74)), hex(i))
                if self.before[i] == 0x1E:
                    self.assertEqual(self.before[i - 1], 0, hex(i))    # op 0 push
            total += n
        self.assertEqual(total, 68)

    def test_params_that_equal_30_stay(self):
        self.assertEqual(self.rom[EXT121_PARAMS[0]:EXT121_PARAMS[0] + 6].hex(), "1d02003c0279")   # push 0,30
        self.assertEqual(self.rom[EXT121_PARAMS[1] - 3:EXT121_PARAMS[1] + 3].hex(), "1d02743c0279")  # 58 then 30

    def test_spawn_and_map_set_words(self):
        for w in SET_WORDS:
            self.assertEqual((u32(self.before, w), u32(self.rom, w)), (30, 58), hex(w))

    def test_type_25_stats_are_up_20_percent_over_vanilla(self):   # r38 (r35 was +10%)
        self.assertEqual(tuple((v * 12 + 5) // 10 for v in STATS_OLD), STATS_NEW)   # x 1.2, rounded half up
        off, n = TYPE25_STATS
        for rom, want in ((self.before, STATS_OLD), (self.rom, STATS_NEW)):
            self.assertEqual((u32(rom, off + 4), rom[off + 0xC], rom[off + 0xD], rom[off + 0xE]), want)
        changed = [i - off for i in range(off, off + n) if self.rom[i] != self.before[i]]
        self.assertEqual(changed, [4, 5, 0xC, 0xD, 0xE])                 # HP low half, STR, POW, END
        self.assertEqual(self.rom[off + 8:off + 0xC], self.before[off + 8:off + 0xC])   # AI id kept

    def test_type_25_is_only_this_fight(self):                    # r35: shape A data, shape B pointers
        spawns = words_naming(self.rom, ENEMY_FACTORY)
        self.assertEqual(len(spawns), len(finds(self.rom, ENEMY_FACTORY)))   # no unaligned copy
        self.assertEqual([s for s in spawns if u32(self.rom, s + 8) == 25], [0x4090F8])
        self.assertEqual(finds(self.rom, 0x4090F8 + ROM_BASE), [0x409148])   # item 12 of map 14,3's list
        entry = ENEMY_TYPES + 24 * 25 + ROM_BASE
        for v in range(entry, entry + 24):
            self.assertEqual(finds(self.rom, v), [], hex(v))
        self.assertEqual(finds(self.rom, ENEMY_TYPES + ROM_BASE),
                         [0xE79C, 0x17A38, 0x1912C])           # enemy_factory, the info screen, the type match
        self.assertEqual([e for e in range(128) if u32(self.rom, SCOUTER + ENTRY * e + 16) == 25], [19])


class PortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.names = b["rom"], b["before"], b["names"]
        cls.block = u32(cls.rom, BLOCK_LITERAL) - ROM_BASE

    def test_ten_lines_read_52(self):
        for rec in PORTRAIT_RECORDS:
            self.assertIn(self.rom[rec + 2], (1, 2), hex(rec))
            self.assertEqual((self.before[rec + 3], self.rom[rec + 3]), (40, 52), hex(rec))
        for rec in SELF_DESTRUCT:
            self.assertEqual((self.before[rec + 3], self.rom[rec + 3]), (39, 39), hex(rec))

    def test_52_shows_the_owner_portrait(self):                  # r36: not 40's frame any more
        self.assertEqual(block_word(self.before, 52), VANILLA_52 + ROM_BASE)
        old40, old52 = (at.live_frame(self.before, self.block, p)[1] for p in (40, 52))
        self.assertGreater(sum(a != b for a, b in zip(old40, old52)), 3000)     # r29: 52 is the hooded face
        self.assertEqual(block_word(self.rom, 52), art_inject.slot(52) + ROM_BASE)
        self.assertNotEqual(block_word(self.rom, 52), block_word(self.rom, 40))
        pal, ok = at.obj_palette(self.rom), at.allowed_indices(self.rom, {})
        with Image.open(OWNER_52) as img:
            self.assertEqual(at.to_pixels(img, pal, ok, snap=True), (at.live_frame(self.rom, self.block, 52)[1], [], []))
        self.assertNotEqual(at.live_frame(self.rom, self.block, 52)[1], at.live_frame(self.rom, self.block, 40)[1])
        self.assertEqual(at.live_frame(self.rom, self.block, 40), at.live_frame(self.before, self.block, 40))
        self.assertEqual(built()["notes"]["superperfect_cell"]["portrait_52"], "owner")

    def test_owner_art_for_52_is_kept(self):
        pal, ok = at.obj_palette(self.rom), at.allowed_indices(self.rom, {})
        art = {pid: at.png_pixels(at.ART_DIR / e["png"], pal, ok) for pid, e in at.load_portraits().items()}
        px = bytearray(art[40])
        px[32 * 64 + 32] = px[30 * 64 + 20] if px[32 * 64 + 32] != px[30 * 64 + 20] else px[34 * 64 + 40]
        staged = {"art_input": {"palette": at.load_palette(), "portraits": {**art, 52: bytes(px)}}}
        rom, alloc = log2_build.assemble(log2_build.BASE, self.names, staged)
        self.assertEqual(alloc.notes["superperfect_cell"]["portrait_52"], "owner")
        self.assertEqual(block_word(rom, 52), art_inject.slot(52) + ROM_BASE)
        self.assertEqual(at.live_frame(rom, self.block, 52)[1], bytes(px))


class IdleHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before, cls.notes = b["rom"], b["before"], b["notes"]
        cls.hook = cls.notes["superperfect_cell"]["code"] + ROM_BASE
        cls.old = cls.notes["ssj2_idle"]["code"] + ROM_BASE

    def test_both_vtables_name_the_chained_hook(self):
        for vt in HOOKED:
            self.assertEqual(tick_target(self.before, vt), self.old | 1, hex(vt))
            self.assertEqual(tick_target(self.rom, vt), self.hook | 1, hex(vt))
        self.assertEqual(self.rom[self.old - ROM_BASE:self.old - ROM_BASE + 0x48],
                         self.before[self.old - ROM_BASE:self.old - ROM_BASE + 0x48])   # ssj2_idle unchanged

    def test_gohan_flicker_is_unchanged(self):                  # sets 159, 160 through the new entry
        for set_id in (159, 160):
            s = set_word(self.rom, set_id) + ROM_BASE
            for seed in SEEDS:
                for vt in HOOKED:
                    got = run_ticks(self.rom, tick_target(self.rom, vt), s, s + 0x4C, seed)
                    self.assertEqual(got, formula(seed), (set_id, seed, hex(vt)))
                    self.assertEqual(got, run_ticks(self.before, tick_target(self.before, vt), s, s + 0x4C, seed))

    def test_set_58_flickers_like_gohan(self):
        s = set_word(self.rom, 58) + ROM_BASE
        for seed in SEEDS:
            for vt in HOOKED:
                got = run_ticks(self.rom, tick_target(self.rom, vt), s, s + 0x4C, seed)
                self.assertEqual(got, formula(seed), (seed, hex(vt)))
        self.assertEqual(set(run_ticks(self.rom, self.hook | 1, s, s + 0x4C, 0)), set(range(6)))
        self.assertEqual(run_ticks(self.rom, self.hook | 1, s, s + 0x5C, 0xEE), vanilla(0xEE))   # anim 1 row

    def test_other_sets_keep_the_vanilla_tick(self):
        for set_id in OTHER_SETS:
            s = set_word(self.rom, set_id) + ROM_BASE
            for seed in (0, 0xEE):
                self.assertEqual(run_ticks(self.rom, self.hook | 1, s, s + 0x4C, seed), vanilla(seed), set_id)

    def test_hook_disassembles_as_expected(self):
        h, s58 = self.hook, set_word(self.rom, 58) + ROM_BASE
        want = ["ldr r2,[r1,#0x48]", f"ldr r3,={s58:#010x}", "cmp r2,r3", f"bne {h + 0xc:#x}",
                f"ldr r3,={self.old + 0x12 | 1:#010x}", "bx r3", f"ldr r3,={self.old | 1:#010x}", "bx r3"]
        self.assertEqual([t for _, t in listing(self.rom, h, len(want))], want)
        self.assertEqual([t for _, t in listing(self.rom, self.old + 0x12, 2)], ["add r2,#0x4c", "ldr r3,[r1,#0x4c]"])


def scouter_match(rom: bytes, set_id: int) -> int:
    """scouter_match @0x08019102 for a live set id >= 7: the first of 128 entries whose +8 set has its header."""
    want = set_word(rom, set_id)
    for e in range(128):
        sid = u32(rom, SCOUTER + ENTRY * e + 8)
        if sid >= 7 and set_word(rom, sid) == want:                  # ids 0-6 are the player and party records
            return e
    return -1


def name_of(rom: bytes, e: int) -> str:
    at = u32(rom, SCOUTER + ENTRY * e) - ROM_BASE
    return rom[at:rom.index(b"\0", at)].decode("latin1")


def scan_screen(rom: bytes, e: int) -> tuple:
    """(name, portrait, HP, STR, POW, END) the scan info screen draws for entry e (@0x08018A38, @0x0801790E)."""
    _, _, _, pid, kind = (u32(rom, SCOUTER + ENTRY * e + 4 * k) for k in range(5))
    stats = ENEMY_TYPES + 24 * kind
    return name_of(rom, e), pid, u32(rom, stats + 4), rom[stats + 0xC], rom[stats + 0xD], rom[stats + 0xE]


def type_match(rom: bytes, kind: int) -> int:
    """@0x080190D4 for an enemy (message 0x14 in @0x0800E5B8): the first entry whose +0x10 names this type entry."""
    for e in range(128):
        if ENEMY_TYPES + 24 * u32(rom, SCOUTER + ENTRY * e + 16) == ENEMY_TYPES + 24 * kind:
            return e
    return -1


def database_rows(rom: bytes, bits: set) -> list:
    """@0x08019204: entries with a set bit, in table order; a run with an equal name pointer is one row.
    Returns [(name, [entries])]; Left and Right page through a row's entries (@0x08019844)."""
    rows, last = [], 0
    for e in sorted(bits):
        word = u32(rom, SCOUTER + ENTRY * e)
        if word != last:
            rows.append((name_of(rom, e), []))
            last = word
        rows[-1][1].append(e)
    return rows


def font_width(rom: bytes, text: str) -> int:
    """text_draw @0x0801F636 width: sum of (glyph width + 1); glyph = font[font[c]] halfwords."""
    h = lambda o: u32(rom, MENU_FONT + 2 * o) & 0xFFFF    # noqa: E731
    return sum(h(h(ord(c))) + 1 for c in text)


def text_adv(rom: bytes, c: int) -> int:
    """Text font advance in @0x0801F7FC and @0x0801F702: glyph width + 1."""
    h = lambda o: u32(rom, TEXT_FONT + 2 * o) & 0xFFFF    # noqa: E731
    return h(h(c)) + 1


def text_line_count(rom: bytes, s: bytes) -> int:
    """The loop at 0x08018ABA (and 0x080196A8): calls of @0x0801F7FC until its done flag, width 160."""
    s, p, n = s + b"\0", 0, 0
    while True:
        while s[p] in (0x20, 0x0A, 0x0B):                 # leading skip
            p += 1
        n += 1
        brk, w = None, 0
        while True:
            c = s[p]
            if c in (0, 0x0B):                            # done
                return n
            if c == 0x0A:
                break
            if c == 0x20:
                brk = p
            w += text_adv(rom, c)
            if w > WRAP:
                p = p if brk is None else brk
                break
            p += 1


def text_lines(rom: bytes, s: bytes) -> list:
    """text_wrapped @0x0801F702: the lines it draws (leading spaces skipped, break at the last space)."""
    s, p, out = s + b"\0", 0, []
    while True:
        while s[p] == 0x20:
            p += 1
        if s[p] == 0:
            return out
        q, w, brk = p, 0, None
        while s[q] not in (0, 0x0A):
            if s[q] == 0x20:
                brk = q
            w += text_adv(rom, s[q])
            if w > WRAP:
                q = q if brk is None else brk
                break
            q += 1
        out.append(s[p:q])
        p = q + (s[q] == 0x0A)


def text_of(rom: bytes, e: int) -> bytes:
    at = u32(rom, SCOUTER + ENTRY * e + 4) - ROM_BASE
    return rom[at:rom.index(b"\0", at)]


def owner_text() -> str:
    """The approved text, quoted in the r35 brief, final decisions 1."""
    for line in BRIEF.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith('"After self-destructing'):
            return line.strip()[1:-1]
    raise ValueError("r35 brief: approved text not found")


class ScouterTests(unittest.TestCase):
    """r31: Super Perfect Cell scans as entry 19. r33, r34: entry 19 has its own name and row. r35: its own text."""

    @classmethod
    def setUpClass(cls):
        b = built()
        cls.rom, cls.before = b["rom"], b["before"]
        cls.base = log2_build.BASE.read_bytes()

    def test_set_58_matches_entry_19_and_set_30_still_matches_13(self):
        self.assertEqual((scouter_match(self.before, 30), scouter_match(self.before, 58)), (13, -1))
        self.assertEqual((scouter_match(self.rom, 30), scouter_match(self.rom, 58)), (13, 19))

    def test_no_other_set_scans_differently(self):
        for set_id in range(7, 161):
            if set_id != 58:
                self.assertEqual(scouter_match(self.rom, set_id), scouter_match(self.before, set_id), set_id)

    def test_cell_enemies_match_13_to_19_by_type(self):          # 14-19 do show: enemies match by type
        for spawn, (kind, entry) in CELL_SPAWNS.items():
            self.assertEqual(u32(self.rom, spawn), ENEMY_FACTORY, hex(spawn))
            self.assertEqual(u32(self.rom, spawn + 8), kind, hex(spawn))
            self.assertEqual((type_match(self.before, kind), type_match(self.rom, kind)), (entry, entry), kind)
        for kind in range(128):
            self.assertEqual(type_match(self.rom, kind), type_match(self.before, kind), kind)

    def test_what_the_scan_screen_shows(self):
        perfect = (PERFECT, 40, 5160, 44, 46, 50)                         # set 30 actor, type 78 enemy
        self.assertEqual(scan_screen(self.before, 13), perfect)
        self.assertEqual(scan_screen(self.rom, 13), perfect)
        for e in range(15, 19):                                           # Cell Games types 21-24
            self.assertEqual(scan_screen(self.rom, e), (PERFECT, 40, 6500, 50, 55, 60), e)
        self.assertEqual(scan_screen(self.before, 19), (PERFECT, 40, 8230, 60, 59, 65))   # before the patch
        self.assertEqual(scan_screen(self.rom, 19), (SUPER, 52) + STATS_NEW)   # type 25, r38 +20%
        self.assertEqual(u32(self.rom, SCOUTER + ENTRY * 19 + 16), 25)
        self.assertEqual(block_word(self.rom, 52), art_inject.slot(52) + ROM_BASE)   # r36: my portrait

    def test_the_name_is_a_new_string_and_13_18_keep_theirs(self):
        at = u32(self.rom, NAME_19) - ROM_BASE
        self.assertEqual(self.rom[at:at + 19], SUPER.encode("ascii") + b"\0")
        self.assertTrue(log2_build.BASE_SIZE <= at < log2_build.ART_REGION[0])
        self.assertEqual(at, built()["notes"]["superperfect_cell"]["name_19"])
        self.assertEqual(words_naming(self.rom, at + ROM_BASE), [NAME_19])
        for e in range(13, 19):
            self.assertEqual(u32(self.rom, SCOUTER + ENTRY * e), PERFECT_AT + ROM_BASE, e)
        self.assertEqual(self.rom[PERFECT_AT:PERFECT_AT + 16], self.before[PERFECT_AT:PERFECT_AT + 16])
        self.assertEqual(self.rom[PERFECT_AT:PERFECT_AT + 16], PERFECT.encode("ascii") + b"\0")

    def test_only_entry_19_name_and_text_words_and_two_bytes_change(self):
        lo, hi = SCOUTER, SCOUTER + ENTRY * 128
        changed = [i for i in range(lo, hi) if self.rom[i] != self.before[i]]
        self.assertTrue(set(changed) - set(SCOUTER_19) <= set(range(NAME_19, NAME_19 + 8)))
        self.assertEqual([self.rom[i] for i in SCOUTER_19], [58, 52])
        for e in range(128):
            if e != 19:
                self.assertEqual(self.rom[SCOUTER + ENTRY * e:SCOUTER + ENTRY * (e + 1)],
                                 self.before[SCOUTER + ENTRY * e:SCOUTER + ENTRY * (e + 1)], e)
        self.assertEqual(u32(self.before, TEXT_19), PERFECT_TEXT_AT + ROM_BASE)
        self.assertEqual(u32(self.rom, TEXT_19), built()["notes"]["superperfect_cell"]["text_19"] + ROM_BASE)
        self.assertEqual(u32(self.rom, SCOUTER + ENTRY * 19 + 16), 25)   # enemy type kept

    def test_the_text_is_the_owner_text_in_entry_13_format(self):   # r35
        at = u32(self.rom, TEXT_19) - ROM_BASE
        text = owner_text()
        want = text.replace(". ", ".  ").encode("ascii") + b"\0"     # entry 13: two spaces between sentences
        self.assertEqual(self.rom[at:at + len(want)], want)
        self.assertEqual(text_of(self.rom, 19).decode("ascii").replace(".  ", ". "), text)   # words verbatim
        self.assertIn(b".  ", text_of(self.rom, 13))
        self.assertNotIn(b". ", text_of(self.rom, 13).replace(b".  ", b""))    # entry 13 never uses one space
        self.assertFalse(set(want[:-1]) & {0x0A, 0x0B})                        # no break bytes, as in 13
        vanilla = set().union(*(text_of(self.before, e) for e in range(128)))
        self.assertTrue(set(want[:-1]) <= vanilla)                              # every byte a vanilla text uses
        self.assertTrue(all(u32(self.rom, TEXT_FONT + 2 * c) & 0xFFFF for c in want[:-1]))
        name = built()["notes"]["superperfect_cell"]["name_19"]
        self.assertEqual(at, -(-(name + 19) // 4) * 4)                         # the next word after the name
        self.assertTrue(log2_build.BASE_SIZE <= at and at + len(want) <= log2_build.ART_REGION[0])
        self.assertEqual(words_naming(self.rom, at + ROM_BASE), [TEXT_19])

    def test_13_to_18_keep_the_perfect_text(self):                # r35
        lo, n = PERFECT_TEXT_AT, PERFECT_TEXT_LEN + 1
        self.assertEqual(self.rom[lo:lo + n], self.before[lo:lo + n])
        self.assertEqual(self.rom[PERFECT_TEXT_AT + n - 1], 0)
        for e in range(13, 19):
            self.assertEqual(u32(self.rom, SCOUTER + ENTRY * e + 4), PERFECT_TEXT_AT + ROM_BASE, e)
        self.assertEqual(text_of(self.rom, 13)[-29:], b"that it cannot be calculated.")

    def test_text_fits_the_text_page(self):                       # r35: 13 lines, scroll max 152
        texts = {}
        for e in range(128):
            texts.setdefault(u32(self.base, SCOUTER + ENTRY * e + 4), e)
        counts = {}
        for e in texts.values():
            s = text_of(self.base, e)
            counts[e] = text_line_count(self.base, s)
            self.assertEqual(counts[e], len(text_lines(self.base, s)), e)   # the counter and the drawer agree
        self.assertEqual((len(texts), max(counts.values()), counts[13]), (62, 21, 14))   # 21 lines: entry 5
        s = text_of(self.rom, 19)
        lines = text_lines(self.rom, s)
        self.assertEqual((text_line_count(self.rom, s), len(lines)), (13, 13))
        self.assertTrue(all(sum(text_adv(self.rom, c) for c in x) <= WRAP for x in lines))
        self.assertEqual(lines[0], b"After self-destructing, Cell")
        self.assertEqual(lines[-1], b"cannot be calculated.")
        self.assertEqual(max(0, 16 * 13 - 0x38), 152)                          # scroll max (@0x08018ACE)
        self.assertLessEqual(13, max(counts.values()))                         # canvas no taller than vanilla

    def test_text_page_listings(self):                            # r35: what the fit model restates
        count = [t for _, t in listing(self.base, 0x08018AAA, 12)]
        self.assertEqual((count[1], count[7], count[11]), ("ldr r1,=0x0802cc64", "mov r2,#0xa0", "bl 0x801f7fc"))
        self.assertEqual([t for _, t in listing(self.base, 0x08018ACE, 2)], ["lsl r0,r5,#4", "sub r0,#0x38"])
        draw = [t for _, t in listing(self.base, 0x08018B3A, 5)]
        self.assertEqual((draw[0], draw[3]), ("mov r1,#0xe", "mov r0,#0x10"))   # first line y 14, step 16
        self.assertEqual([t for _, t in listing(self.base, 0x08018B52, 4)][::3], ["mov r1,#0xa0", "bl 0x801f702"])
        win = [t for _, t in listing(self.base, 0x080192EA, 5)]
        self.assertEqual((win[0], win[4]), ("mov r0,#0xa0", "add r0,#0x40"))   # a 160 x 64 window
        wrap = [t for _, t in listing(self.base, 0x0801F73A, 10)]
        self.assertEqual((wrap[0], wrap[2], wrap[8]), ("cmp r3,#0x20", "add r2,r5,#0", "add r1,#0x1"))
        self.assertEqual([t for _, t in listing(self.base, 0x0801F74E, 4)],
                         ["ldr r1,[sp,#0xc]", "cmp r0,r1", "ble 0x801f776", "cmp r2,#0x0"])   # break at the last space
        meas = [t for _, t in listing(self.base, 0x0801F838, 4)]
        self.assertEqual(meas, ["cmp r6,#0x20", "bne 0x801f842", "add r5,r1,#0", "ldr r7,[r3,#0x8]"])

    def test_the_database_gives_super_perfect_its_own_row(self):
        everyone = {12, 13, 14, 15, 16, 17, 18, 19, 20}
        self.assertEqual([(n, e) for n, e in database_rows(self.before, everyone)],
                         [('Cell, "Nonperfect"', [12]), (PERFECT, list(range(13, 20))), ("Cell Junior", [20])])
        self.assertEqual([(n, e) for n, e in database_rows(self.rom, everyone)],
                         [('Cell, "Nonperfect"', [12]), (PERFECT, list(range(13, 19))), (SUPER, [19]),
                          ("Cell Junior", [20])])
        self.assertEqual(database_rows(self.rom, {15, 19}), [(PERFECT, [15]), (SUPER, [19])])

    def test_name_fits_the_list_and_the_info_field(self):   # r34: 85 px, ink x 77-161 inside 73-166
        self.assertEqual((font_width(self.rom, PERFECT), font_width(self.rom, SUPER)), (74, 85))
        self.assertLessEqual(font_width(self.rom, SUPER), LIST_WIDTH - 2)
        start = 120 - (font_width(self.rom, SUPER) + 1) // 2                # centred on x 120 (@0x0801F6A2)
        end = start + font_width(self.rom, SUPER) - 1
        self.assertEqual((start, end), (77, 161))
        self.assertTrue(NAME_FIELD[0] <= start and end <= NAME_FIELD[1])

    def test_database_listings(self):
        rows = [t for _, t in listing(self.base, 0x0801927E, 4)]
        self.assertEqual(rows[:3], ["ldr r3,[r3,#0x0]", "cmp r5,r3", "beq 0x8019298"])   # name pointer compare
        bit = [t for _, t in listing(self.base, 0x0801924E, 2)]
        self.assertEqual(bit, ["and r3,r5", "beq 0x801925e"])                 # only entries with a set bit
        page = [t for _, t in listing(self.base, 0x0801988C, 7)]
        self.assertEqual(page, ["ldr r2,[r4,#0x24]", "sub r2,#0x1", "str r2,[r4,#0x24]", "cmp r1,r2",
                                "ble 0x801989a", "ldr r0,[r0,#0x4]", "str r0,[r4,#0x24]"])   # Left wraps in the row
        setter = [t for _, t in listing(self.base, 0x08018A6E, 3)]
        self.assertEqual(setter, ["add r0,#0xff", "add r0,#0x11", "ldrb r1,[r0,#0xa]"])  # info screen sets the bit

    def test_enemy_scan_listings(self):
        vt = 0x080252A4
        self.assertEqual((vt + u32(self.base, vt - ROM_BASE + 0x24)) & 0xFFFFFFFF, 0x0800E5B9)  # message slot
        msg = [t for _, t in listing(self.base, 0x0800E5E8, 4)]
        self.assertEqual(msg, ["mov r0,#0xff", "add r0,#0x81", "ldr r0,[r0,r4]", "bl 0x80190d4"])  # obj +0x180
        ctor = [t for _, t in listing(self.base, 0x0800E2DA, 2)]
        self.assertEqual(ctor, ["sub r5,#0x1c", "str r1,[r5,#0x0]"])         # +0x180 = the type entry argument
        factory = [t for _, t in listing(self.base, 0x0800E780, 6)]
        self.assertEqual((factory[0], factory[1], factory[5]), ("ldr r1,[r0,#0x8]", "ldr r2,=0x086d56ac",
                                                                "add r2,r1,r2"))   # table + 24 x spawn +8
        match = [t for _, t in listing(self.base, 0x080190E6, 6)]
        self.assertEqual((match[0], match[5]), ("ldr r5,[r3,#0x10]", "cmp r3,r1"))  # entry +0x10 type

    def test_listings(self):
        match = [t for _, t in listing(self.base, 0x08019102, 21)]
        self.assertEqual(match[8:12], ["ldr r0,[r0,#0x8]", "bl 0x8009324", "cmp r0,r5", "bne 0x8019120"])
        self.assertEqual(match[14:16], ["add r4,#0x1", "cmp r4,#0x80"])     # first match of 128 wins
        info = [t for _, t in listing(self.base, 0x0801795A, 7)]
        self.assertEqual((info[0], info[5]), ("ldr r0,[r5,#0x10]", "ldr r1,=0x086d56ac"))   # enemy type stats
        marker = [t for _, t in listing(self.base, 0x08018F16, 8)]
        self.assertEqual(marker[6:8], ["ldr r0,[r0,#0x8]", "bl 0x8009324"])  # the scan marker draws the entry's set
        scan = [t for _, t in listing(self.base, 0x08007B2C, 2)]
        self.assertEqual(scan, ["ldr r0,[r4,#0x48]", "bl 0x8019102"])       # match by the actor's header


class DiffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]
        cls.new_used = b["used"][len(b["alloc_before"].used()):]
        cls.changed = diff(cls.before, cls.rom)

    def named_sites(self) -> list:
        set_table = u32(self.rom, SET_LITERAL) - ROM_BASE + 4 * 51
        block = u32(self.rom, BLOCK_LITERAL) - ROM_BASE + 4 + 4 * 52
        n = self.notes["superperfect_cell"]
        return ([(set_table, 4), (block, 4), (art_inject.slot(52), art_inject.FRAME)] + [(w, 4) for w in SET_WORDS] + [(vt + 4 - ROM_BASE, 4) for vt in HOOKED]
                + [(s, 1) for s in n["sites"]] + [(r + 3, 1) for r in PORTRAIT_RECORDS] + self.new_used
                + [(s, 1) for s in SCOUTER_19] + [(NAME_19, 4), (TEXT_19, 4)] + list(STAT_SITES))

    def test_only_named_sites_change(self):
        sites = self.named_sites()
        self.assertEqual([hex(i) for i in self.changed if not any(a <= i < a + n for a, n in sites)], [])
        for a, n in sites:
            self.assertTrue(any(a <= i < a + n for i in self.changed), hex(a))
        self.assertEqual(len(self.notes["superperfect_cell"]["sites"]), 68)

    def test_earlier_allocations_unchanged(self):
        n = len(built()["alloc_before"].used())
        self.assertEqual(built()["used"][:n], built()["alloc_before"].used())
        end = max(a + s for a, s in built()["alloc_before"].used())
        self.assertTrue(all(a >= end and a + s <= log2_build.ART_REGION[0] for a, s in self.new_used))

    def test_build_list_has_superperfect_cell_after_piccolo_gi_scene(self):    # r37 appends chamber_spar
        names = built()["names"]
        i = names.index("superperfect_cell")
        self.assertEqual(names[i - 1:i + 1], ["piccolo_gi_scene", "superperfect_cell"])

    def test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only(self):
        r35, r36 = BUILD / "log2_poc_r35.gba", BUILD / "log2_poc_r36.gba"
        if not (r35.exists() and r36.exists()):
            self.skipTest("r35 or r36 not built")
        r36_rom = with_stats(self.rom, STATS_R35)                           # r38 raised the stats; r35, r36 have +10%
        self.assertEqual(r36.read_bytes(), r36_rom)
        names = built()["names"]
        names = names[:names.index("superperfect_cell") + 1]               # the r36 list (r37 appends a patch)
        old, _ = log2_build.assemble(log2_build.BASE, names, {"art_input": art_input_without(52)})
        self.assertEqual(r35.read_bytes(), with_stats(bytes(old), STATS_R35))   # r35 = the same list, 52 still vanilla
        word = u32(self.rom, BLOCK_LITERAL) - ROM_BASE + 4 + 4 * 52
        sites = [(word, 4), (art_inject.slot(52), art_inject.FRAME)]        # r36 brief: the 2 new sites
        changed = diff(r35.read_bytes(), r36_rom)
        self.assertEqual([hex(i) for i in changed if not any(a <= i < a + n for a, n in sites)], [])
        for a, n in sites:
            self.assertTrue(any(a <= i < a + n for i in changed), hex(a))

    def test_r32_to_r33_is_the_name_only(self):
        r32, r33 = BUILD / "log2_poc_r32.gba", BUILD / "log2_poc_r33.gba"
        if not (r32.exists() and r33.exists()):
            self.skipTest("r32 or r33 missing")
        a, b = r32.read_bytes(), r33.read_bytes()
        name = self.notes["superperfect_cell"]["name_19"]                   # r33 and r34 share the address
        sites = [(NAME_19, 4), (name, 22)]
        changed = diff(a, b)
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        self.assertTrue(set(range(name, name + 22)) <= set(changed))
        self.assertEqual(set(a[name:name + 22]), {0xFF})                    # free space in r32
        end = self.notes["superperfect_cell"]["code"] + self.notes["superperfect_cell"]["size"]
        self.assertEqual(name, -(-end // 4) * 4)                            # the next word after the hook code

    def test_r33_to_r34_is_the_name_string_only(self):
        r33, r34 = BUILD / "log2_poc_r33.gba", BUILD / "log2_poc_r34.gba"
        if not (r33.exists() and r34.exists()):
            self.skipTest("r33 or r34 missing")
        a, b = r33.read_bytes(), r34.read_bytes()
        name = self.notes["superperfect_cell"]["name_19"]
        self.assertEqual(len(a), len(b))
        self.assertEqual([hex(i) for i in diff(a, b) if not name <= i < name + 22], [])
        self.assertEqual(b[name:name + 19], SUPER.encode("ascii") + b"\0")
        self.assertEqual(set(b[name + 19:name + 22]), {0xFF})               # the tail of r33's longer string is free

    def test_r34_to_r35_is_the_text_its_pointer_and_the_stats(self):   # r35 brief: diff proof
        r34, r35 = BUILD / "log2_poc_r34.gba", BUILD / "log2_poc_r35.gba"
        if not (r34.exists() and r35.exists()):
            self.skipTest("r34 or r35 missing")
        a, b = r34.read_bytes(), r35.read_bytes()
        text = self.notes["superperfect_cell"]["text_19"]
        size = len(owner_text()) + 4 + 1                                   # 4 sentence gaps get a second space
        sites = [(text, size), (TEXT_19, 4)] + list(STAT_SITES)
        changed = diff(a, b)
        self.assertEqual(len(a), len(b))
        self.assertEqual([hex(i) for i in changed if not any(s <= i < s + n for s, n in sites)], [])
        self.assertEqual(set(a[text:text + size]), {0xFF})                  # free space in r34
        self.assertEqual(b[text + size - 1], 0)
        self.assertEqual(set(range(text, text + size - 1)) - set(changed), set())   # every text byte is new
        self.assertEqual((u32(a, TEXT_19), u32(b, TEXT_19)), (PERFECT_TEXT_AT + ROM_BASE, text + ROM_BASE))
        off = TYPE25_STATS[0]
        for rom, want in ((a, STATS_OLD), (b, STATS_R35)):
            self.assertEqual((u32(rom, off + 4), rom[off + 0xC], rom[off + 0xD], rom[off + 0xE]), want)

    def test_r30_to_r31_outside_the_scene_is_the_scouter_only(self):   # scene slots: test_piccolo_gi_scene
        build = log_paths.BUILDS
        if not ((build / "log2_poc_r30.gba").exists() and (build / "log2_poc_r31.gba").exists()):
            self.skipTest("r30 or r31 missing")
        a, b = (build / "log2_poc_r30.gba").read_bytes(), (build / "log2_poc_r31.gba").read_bytes()
        outside = [i for i in diff(a, b) if not 0x89AF38 <= i < 0x89B158]  # records 31-44 of piccolo_gi_scene
        self.assertEqual([(hex(i), a[i], b[i]) for i in outside], [("0x6f8fc4", 30, 58), ("0x6f8fc8", 40, 52)])


class FailClosedTests(unittest.TestCase):
    def fresh(self) -> tuple:
        b = built()
        return bytearray(b["before"]), copy.deepcopy(b["alloc_before"])

    def assert_refused(self, rom: bytearray, alloc) -> None:
        snap = bytes(rom)
        with self.assertRaises(ValueError):
            superperfect_cell.apply(rom, alloc)
        self.assertEqual(bytes(rom), snap)

    def test_each_checked_site_refuses(self):
        b = built()
        set_table = u32(b["before"], SET_LITERAL) - ROM_BASE
        block = u32(b["before"], BLOCK_LITERAL) - ROM_BASE
        for off in (0x3EACD5, 0x89AB4C + 0x1C5, 0x3EB86C, SET_WORDS[0], SET_WORDS[1], PORTRAIT_RECORDS[9] + 3,
                    set_table + 4 * 51, set_table + 4 * 23, HOOKED[1] + 4 - ROM_BASE, block + 4 + 4 * 52 + 1,
                    RETURN_TABLE + 4 * 39, SCOUTER_19[0], SCOUTER + ENTRY * 15 + 8, NAME_19, PERFECT_AT + 7,
                    TEXT_19, TYPE25_STATS[0] + 4, TYPE25_STATS[0] + 5, TYPE25_STATS[0] + 0xC,
                    TYPE25_STATS[0] + 0xE):
            with self.subTest(off=hex(off)):
                rom, alloc = self.fresh()
                rom[off] ^= 0x01
                self.assert_refused(rom, alloc)

    def test_second_run_and_missing_notes_refuse(self):
        rom, alloc = self.fresh()
        superperfect_cell.apply(rom, alloc)
        self.assert_refused(rom, alloc)
        for need in ("ssj2_idle", "piccolo_gi_scene"):
            rom, alloc = self.fresh()
            del alloc.notes[need]
            self.assert_refused(rom, alloc)


class CopyTests(unittest.TestCase):
    """r33: saves and states are r32 byte copies; the two ROM pair files are r33 byte copies."""

    def test_r33_saves_states_and_rom_pairs_are_copies(self):
        pairs = [(f"log2_poc_r32{s}", f"log2_poc_r33{s}") for s in (".sav", "_chamber2.sav", "_scouter.sav")]
        pairs += [(f"log2_poc_r32.ss{k}", f"log2_poc_r33.ss{k}") for k in range(1, 6)]
        pairs += [("log2_poc_r33.gba", "log2_poc_r33_chamber2.gba"), ("log2_poc_r33.gba", "log2_poc_r33_scouter.gba")]
        for src, dst in pairs:
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)

    def test_r34_saves_states_and_rom_pairs_are_copies(self):
        pairs = [(f"log2_poc_r33{s}", f"log2_poc_r34{s}") for s in (".sav", "_chamber2.sav", "_scouter.sav")]
        pairs += [(f"log2_poc_r33.ss{k}", f"log2_poc_r34.ss{k}") for k in range(1, 6)]
        pairs += [("log2_poc_r34.gba", "log2_poc_r34_chamber2.gba"), ("log2_poc_r34.gba", "log2_poc_r34_scouter.gba")]
        for src, dst in pairs:
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)

    def test_r35_saves_states_and_rom_pairs_are_copies(self):
        pairs = [(f"log2_poc_r34{s}", f"log2_poc_r35{s}") for s in (".sav", "_chamber2.sav", "_scouter.sav")]
        pairs += [(f"log2_poc_r34.ss{k}", f"log2_poc_r35.ss{k}") for k in range(1, 6)]
        pairs += [("log2_poc_r35.gba", "log2_poc_r35_chamber2.gba"), ("log2_poc_r35.gba", "log2_poc_r35_scouter.gba")]
        for src, dst in pairs:
            if not (BUILD / dst).exists():
                self.skipTest(f"{dst} missing")
            self.assertEqual((BUILD / src).read_bytes(), (BUILD / dst).read_bytes(), dst)


class PinnedTestsNote(unittest.TestCase):
    """test_idle.py:240 and test_portraits.py:179 pin word 58 for the r13 and Task 7 lists only (rebased r30)."""

    def test_pins_hold_for_their_lists_and_the_full_list_repoints_58(self):
        base = Path(log2_build.BASE).read_bytes()
        vanilla58 = u32(base, 0x3B4E90 + 4 * (58 - 7)) - ROM_BASE
        self.assertEqual(vanilla58, DEAD_58)
        self.assertEqual(set_word(built()["before"], 58), DEAD_58)
        self.assertNotEqual(set_word(built()["rom"], 58), DEAD_58)


if __name__ == "__main__":
    unittest.main()
