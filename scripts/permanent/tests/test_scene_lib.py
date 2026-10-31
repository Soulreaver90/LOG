r"""
test_scene_lib.py - Tests for scene_lib, scene_harness and scene_probe.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_scene_lib.py -v
The gate for this task is that no module changes its output, so the encoder tests pin the exact bytes the
modules wrote before the move, and the re-export tests prove the old import paths still work.
Cross-check: the decoder is checked against lengths the patch modules declare for themselves, so a decoder
that drifts disagrees with piccolo_gi_scene.SOURCES rather than with a number this file made up.
Source: docs\tasks\2026-10-30-tooling\tooling-part2.md, bible section 8 (SS3, CSP, PGS, CH6).
"""
import struct
import unittest

import log2_build
from scene import scene_lib as S
from scene import scene_probe
from scene.scene_harness import State, run_record, run_table

BASE_ROM = log2_build.BASE.read_bytes()
CHAMBER_EXIT, TABLE_WORDS = 0x3DBDD4, 35
WALK_OFFS, SEQ3 = 0x3DBD5C, 0x3DB59C
DENDE_OBJECT, DENDE_TABLE, DENDE_SET, DENDE_AT = 0x403F60, 0x3DD044, 36, (760, 416)


class EncoderTests(unittest.TestCase):
    """The encoders moved from piccolo_gi_scene byte for byte. These pin the bytes."""

    def test_push_picks_op_0_for_one_small_value(self):
        self.assertEqual(S.push(56), bytes([0, 56]))
        self.assertEqual(S.push(255), bytes([0, 255]))

    def test_push_picks_op_29_for_a_list_or_a_big_value(self):
        self.assertEqual(S.push(56, 1), bytes.fromhex("1d027002"))
        self.assertEqual(S.push(56, 840, 432), bytes.fromhex("1d03708d108660"))
        self.assertEqual(S.push(256)[:2], bytes([29, 1]))

    def test_ext_and_code_and_text_bytes(self):
        self.assertEqual(S.ext(52, 56), bytes.fromhex("0038") + bytes([2, 52]))
        self.assertEqual(S.ext(63), bytes([2, 63]))
        self.assertEqual(S.code(32, S.ext(27, 158)), bytes([32, 0, 0]) + bytes.fromhex("009e021b") + b"\x11")
        self.assertEqual(S.text(30, 62, "Hi"), bytes([30, 0, 1, 62]) + b"Hi\0")

    def test_zigzag_round_trips(self):
        for v in list(range(-3000, 3001)) + [70000, -70000]:
            self.assertEqual(S.unzigzag(S.zigzag(v), 0)[0], v, v)

    def test_seq32_tail_bytes_match_the_module_constant(self):
        """piccolo_gi_scene states this tail as a hex literal; the encoders must produce the same bytes."""
        built = S.ext(33, 0) + S.ext(27, 158) + S.ext(46, 62) + b"\x11"
        self.assertEqual(built.hex(), "00000221009e021b003e022e11")


class NamedOpTests(unittest.TestCase):

    def test_named_op_is_the_same_bytes_as_the_number(self):
        self.assertEqual(S.spawn(158, 344, 400), S.ext(51, 158, 344, 400))
        self.assertEqual(S.remove(56), S.ext(52, 56))
        self.assertEqual(S.set_flag(158), S.ext(27, 158))
        self.assertEqual(S.camera(232, 320, 40), S.ext(31, 232, 320, 40))
        self.assertEqual(S.camera(232, 320), S.ext(31, 232, 320))

    def test_call_works_by_name_and_by_number(self):
        self.assertEqual(S.call("spawn", 158, 344, 400), S.ext(51, 158, 344, 400))
        self.assertEqual(S.call(57, 103, 11), S.ext(57, 103, 11))

    def test_an_unknown_op_stays_usable_by_number(self):
        self.assertEqual(S.call(200, 1, 2), S.ext(200, 1, 2))
        self.assertEqual(S.op_name(200), "ext200")
        self.assertEqual(S.op_label(200), "S")

    def test_call_refuses_too_many_arguments_for_a_named_op(self):
        with self.assertRaises(ValueError):
            S.call("remove", 1, 2, 3)

    def test_base_op_names_match_their_handlers(self):
        """Ops 18 and 19 are easy to swap: 18 is the unconditional jump (its handler reads no stack value)
        and 19 pops one and jumps when it is zero."""
        self.assertEqual(S.BASE_OPS[18][0], "jmp")
        self.assertEqual(S.BASE_OPS[19][0], "jz")
        self.assertEqual(S.BASE_OPS[20][0], "drop")
        self.assertEqual([S.BASE_OPS[n][0] for n in range(11, 17)],
                         ["eq", "ne", "gt", "ge", "lt", "le"])
        self.assertEqual(S.op_name(11, base=True), "eq")

    def test_every_named_op_carries_a_label(self):
        for n, (name, args, label) in S.EXT_OPS.items():
            self.assertIn(label, ("C", "L", "S"), f"ext {n} ({name})")
            self.assertIsInstance(args, tuple)


class DecoderTests(unittest.TestCase):
    """The decoder is checked against the lengths the patch modules declare, not against new numbers."""

    def test_type_0_record_length_matches_the_module_constants(self):
        import patches.piccolo_gi_scene as pgs
        for index, (at, length, _sha) in pgs.SOURCES.items():
            if BASE_ROM[at + 2] != S.TYPE_CODE:
                continue
            self.assertEqual(S.decode_record(BASE_ROM, at).length, length,
                             f"table index {index} at rom:0x{at:X}")

    def test_walk_offs_record_decodes_to_the_documented_ops(self):
        rec = S.decode_record(BASE_ROM, WALK_OFFS)
        self.assertEqual(rec.kind, S.TYPE_CODE)
        self.assertEqual(rec.nxt, 32)
        names = [S.op_name(o.ext) for o in rec.code if o.ext is not None]
        self.assertEqual(names.count("fly"), 4)
        self.assertEqual(names.count("remove"), 4)
        self.assertIn("set_flag", names)

    def test_text_record_decodes_its_line(self):
        rec = S.decode_record(BASE_ROM, 0x3D3ADC)
        self.assertEqual(rec.kind, S.TYPE_TEXT)
        self.assertEqual(rec.portrait, 65)
        self.assertIn("I feel so weak", rec.line)

    def test_a_branching_record_is_not_cut_at_its_first_end(self):
        """Record rom:0x3EC678 (post-Cell table index 49) sets flag 195, then tests flags 302, 303, 305 and
        306 and branches: jz to `push 53 ; end`, else `push 50 ; end`. The first op 17 sits 3 bytes before
        the real end, so a decoder that stops there loses the second branch. The two addresses checked here
        are the ones the bible already pins: SET 195 at rom:0x3EC6A2 and the map load at rom:0x3EC690."""
        self.assertEqual(S.record_end(BASE_ROM, 0x3EC678), 0x3EC678 + 77)
        rec = S.decode_record(BASE_ROM, 0x3EC678)
        self.assertEqual(rec.length, 77)
        # The body keeps the inner branch end and the push after it. The record's own terminating end is
        # excluded, the same way code() appends it. A decoder that stopped early would lose both.
        self.assertEqual([o.at for o in rec.code if o.op == 17], [0x3EC6C1])
        self.assertEqual([(o.at, o.args[0]) for o in rec.code if o.op == 0 and o.args[0] in (50, 53)],
                         [(0x3EC6BF, 50), (0x3EC6C2, 53)])
        self.assertEqual([o.at for o in rec.code if o.ext == 27], [0x3EC6A4])
        self.assertEqual([o.at for o in rec.code if o.ext == 35], [0x3EC690])

    def test_unknown_op_raises(self):
        with self.assertRaises(ValueError):
            S._op_end(bytes([30]), 0)


class TableTests(unittest.TestCase):

    def test_chamber_exit_table_length_and_end(self):
        self.assertEqual(S.table_end(BASE_ROM, CHAMBER_EXIT), TABLE_WORDS)
        words = S.walk(BASE_ROM, CHAMBER_EXIT, TABLE_WORDS)
        self.assertTrue(S.is_end_entry(words[TABLE_WORDS - 1]))
        self.assertFalse(any(S.is_end_entry(w) for i, w in words.items() if i < TABLE_WORDS - 1))

    def test_walk_refuses_an_unaligned_table(self):
        with self.assertRaises(ValueError):
            S.walk(BASE_ROM, CHAMBER_EXIT + 1, 4)

    def test_stray_word_is_reported_not_walked(self):
        """Bible CH6: table rom:0x3E6078 carries the stray 0x2164 before word 0. A backward walk would read
        it as an END and shift every index; walk() takes the start address and never searches backward."""
        self.assertEqual(S.stray_before(BASE_ROM, 0x3E6078), 0x2164)
        self.assertIsNone(S.stray_before(BASE_ROM, CHAMBER_EXIT))

    def test_records_skips_the_end_entry(self):
        recs = S.records(BASE_ROM, CHAMBER_EXIT, TABLE_WORDS)
        self.assertNotIn(TABLE_WORDS - 1, recs)
        self.assertEqual(recs[31].at, WALK_OFFS)


class NamerTests(unittest.TestCase):

    def test_words_naming_finds_the_two_type_5_words(self):
        """Bible PGS: only the type 5 words rom:0x3CF7E4 and rom:0x3D1530 name the chamber exit table."""
        found = S.words_naming(BASE_ROM, CHAMBER_EXIT, 0x3B0000, 0x420000)
        self.assertEqual(found, [0x3CF7E4, 0x3D1530])

    def test_copy_and_redirect_refuses_a_namer_that_does_not_name_the_record(self):
        rom = bytearray(BASE_ROM)
        with self.assertRaises(ValueError) as cm:
            S.copy_and_redirect(rom, _FakeAlloc(), WALK_OFFS, 0x57, namers=[0x3CF7E4])
        self.assertIn("does not name", str(cm.exception))

    def test_copy_and_redirect_refuses_a_second_namer_it_was_not_given(self):
        """The chamber exit table has two real namers. Listing one and asking for a proof must fail."""
        rom = bytearray(BASE_ROM)
        with self.assertRaises(ValueError) as cm:
            S.copy_and_redirect(rom, _FakeAlloc(), CHAMBER_EXIT, 4 * TABLE_WORDS, namers=[0x3CF7E4])
        self.assertIn("did not list", str(cm.exception))

    def test_copy_and_redirect_needs_at_least_one_namer(self):
        with self.assertRaises(ValueError):
            S.copy_and_redirect(bytearray(BASE_ROM), _FakeAlloc(), WALK_OFFS, 0x57, namers=[])

    def test_copy_and_redirect_moves_the_record_and_repoints_both_namers(self):
        rom = bytearray(BASE_ROM) + bytearray(b"\xff" * 0x1000)
        alloc = _FakeAlloc(len(BASE_ROM))
        at = S.copy_and_redirect(rom, alloc, CHAMBER_EXIT, 4 * TABLE_WORDS,
                                 namers=[0x3CF7E4, 0x3D1530])
        want = struct.pack("<I", at + S.ROM_BASE)
        for w in (0x3CF7E4, 0x3D1530):
            self.assertEqual(bytes(rom[w:w + 4]), want)
        self.assertEqual(bytes(rom[at:at + 4 * TABLE_WORDS]),
                         BASE_ROM[CHAMBER_EXIT:CHAMBER_EXIT + 4 * TABLE_WORDS])


    def test_copy_and_redirect_accepts_a_namer_listed_as_dead(self):
        """A dead namer is stated, never silent: it stays pointing at the old record."""
        rom = bytearray(BASE_ROM) + bytearray(b"\xff" * 0x1000)
        at = S.copy_and_redirect(rom, _FakeAlloc(len(BASE_ROM)), CHAMBER_EXIT, 4 * TABLE_WORDS,
                                 namers=[0x3CF7E4], dead=[0x3D1530])
        self.assertEqual(bytes(rom[0x3CF7E4:0x3CF7E8]), struct.pack("<I", at + S.ROM_BASE))
        self.assertEqual(bytes(rom[0x3D1530:0x3D1534]), struct.pack("<I", CHAMBER_EXIT + S.ROM_BASE))


class _FakeAlloc:
    """The smallest allocator the helper needs: hand out space and remember nothing else."""

    def __init__(self, start: int = 0x800000):
        self.at = start

    def alloc(self, n: int) -> int:
        out, self.at = self.at, self.at + n
        return out


class HarnessTests(unittest.TestCase):

    def test_walk_offs_record_runs_as_the_module_describes(self):
        run = run_record(BASE_ROM, WALK_OFFS)
        self.assertFalse(run.approximate)
        self.assertEqual(run.next_index, 32)
        self.assertEqual(run.flags_set, {158})
        self.assertEqual(run.sounds, [26, 26, 26, 62])
        self.assertEqual(run.removed, [56, 132, 137, 103])
        self.assertEqual(run.positions[103], (800, 472))

    def test_called_reads_one_op_by_name(self):
        run = run_record(BASE_ROM, WALK_OFFS)
        self.assertEqual(run.called("fly"), [(56, 840, 480), (132, 720, 488),
                                             (137, 736, 472), (103, 800, 472)])

    def test_seq3_spawns_the_documented_actors(self):
        """Bible R28: chamber exit seq 3 spawns NPC Goku and Gohan. The module's own edit table says the
        set 56 spawn pushes 56, 840, 432."""
        run = run_record(BASE_ROM, SEQ3)
        self.assertEqual(run.spawns[56], (840, 432))
        self.assertIn(60, run.spawns)

    def test_whole_chamber_exit_table_runs_and_ends(self):
        run = run_table(BASE_ROM, CHAMBER_EXIT)
        self.assertTrue(run.ended)
        self.assertEqual(run.indexes, list(range(TABLE_WORDS)))
        self.assertEqual(run.flags_set, {154, 158})       # bible: SET 154 at seq 0, SET 158 at rom:0x3DBDAC

    def test_binary_ops_match_their_handlers(self):
        from scene.scene_harness import BINARY
        self.assertEqual(BINARY[7](5, 3), 8)              # add
        self.assertEqual(BINARY[8](5, 3), 2)              # sub, a - b
        self.assertEqual(BINARY[9](5, 3), 15)             # mul
        self.assertEqual(BINARY[11](3, 3), 1)             # eq
        self.assertEqual(BINARY[12](3, 3), 0)             # ne
        self.assertEqual(BINARY[13](5, 3), 1)             # gt
        self.assertEqual(BINARY[16](5, 3), 0)             # le

    def test_state_carries_the_leader(self):
        self.assertEqual(State(leader=2).leader, 2)


class ProbeTests(unittest.TestCase):

    def test_map_entry_finds_a_known_map(self):
        _, at = scene_probe.map_entry(BASE_ROM, 9, 1)
        self.assertEqual(BASE_ROM[at], 9)
        self.assertEqual(BASE_ROM[at + 1], 1)

    def test_dende_talk_object_matches_the_bible_row(self):
        """Bible CSP: map 9,1 interactive object rom:0x403F60, Dende set 36 at (760,416), table 0x3DD044."""
        it = scene_probe.item(BASE_ROM, DENDE_OBJECT)
        self.assertEqual(it["kind"], "talk")
        self.assertEqual(it["table"], DENDE_TABLE)
        self.assertEqual(it["set_id"], DENDE_SET)
        self.assertEqual(it["at_xy"], DENDE_AT)

    def test_capsule_corp_door_regions_match_the_bible_row(self):
        """Bible CSV: map 6,4 region 0 warps to 6,6 var 1 at (64,216); region 1 runs table 0x3CEDF0."""
        info = scene_probe.map_items(BASE_ROM, 6, 4)
        self.assertEqual(len(info["regions"]), 2)
        warp = info["regions"][0][1]
        self.assertEqual((warp["kind"], warp["to"], warp["landing"]), ("warp", (6, 6, 1), (64, 216)))
        self.assertEqual(info["regions"][1][1]["table"], 0x3CEDF0)

    def test_cell_games_group_scenes_are_found(self):
        """Bible SS3 names three tables owned through the map 14,3 group factory. A tool that reads only the
        region list misses them, so this proves the item walk reaches them."""
        info = scene_probe.map_items(BASE_ROM, 14, 3)
        tables = {it["table"] for it in info["items"] if it["kind"] == "group" and "table" in it}
        self.assertTrue({0x3E93E8, 0x3E9D4C, 0x3EC758} <= tables, sorted(hex(t) for t in tables))

    def test_find_text_locates_a_vanilla_line_and_its_namer(self):
        hits = scene_probe.find_text(BASE_ROM, "I feel so weak")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["record"], 0x3D3ADC)
        self.assertTrue(hits[0]["namers"])


class ReExportTests(unittest.TestCase):
    """The modules that imported the encoders from a patch must keep working after the move."""

    def test_piccolo_gi_scene_still_exports_the_encoders(self):
        import patches.piccolo_gi_scene as pgs
        for name in ("code", "ext", "push", "text", "zigzag"):
            self.assertIs(getattr(pgs, name), getattr(S, name), name)

    def test_npc_gi_still_exports_relocate_and_op_end(self):
        import patches.npc_gi as npc
        self.assertIs(npc.relocate, S.relocate)
        self.assertIs(npc._op_end, S._op_end)
        self.assertIs(npc._varint_end, S._varint_end)

    def test_relocate_round_trips_a_record_with_no_edits(self):
        self.assertEqual(S.relocate(BASE_ROM, WALK_OFFS, 0x57, {}),
                         BASE_ROM[WALK_OFFS:WALK_OFFS + 0x57])


if __name__ == "__main__":
    unittest.main()
