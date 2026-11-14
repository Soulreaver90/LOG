r"""
test_scouter_future.py - The three future enemies are scannable, they appear in the database list,
                         and nothing else in the database or its menu moved.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_scouter_future.py -v
Builds build_list_trial_plateau.txt in memory three ways: whole, WITHOUT this module, and truncated
just BEFORE it. Every claim is read as a difference between those ROMs rather than out of the
module's own constants.
Menu:    the 14 grow sites are DECODED with rom\thumb_dis, never with the module's own encoder, so a
         wrong encoding cannot agree with itself. Three controls perturb a real build and prove each
         check goes red.
What it cannot read: whether the allocator really grants a 0x6E0 object at run time, whether the
menu renders 131 rows, whether the text box renders a 587-character bio on real hardware, and
whether anything the game writes also uses save byte 0x12A. All four are play-test or report items.
"""
import re
import struct
import unittest

import log2_build
import log_paths
from patches import scouter_future as sf
from rom import thumb_dis

ROM_BASE = 0x08000000
LIST = log_paths.BUILD_LISTS / "build_list_trial_plateau.txt"
ENEMY_TABLE, ENEMY_ENTRY = 0x6D56AC, 24
MENU_CODE = (0x19000, 0x19B30)          # the region the 14 sites were enumerated over, scouter-sites.md


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def _cstr(rom, off):
    return bytes(rom[off:bytes(rom).index(b"\0", off)]).decode("ascii")


# ===== the menu object, read back out of the instructions themselves =====

def _pair(rom, mov_at, lsl_at):
    """The constant the `mov rX,#imm8 ; lsl rX,rX,#imm5` pair builds, DECODED with the project's own
    disassembler. The module's encoder is deliberately not used: it would agree with itself."""
    mov, _ = thumb_dis.dis(rom, mov_at + ROM_BASE)
    lsl, _ = thumb_dis.dis(rom, lsl_at + ROM_BASE)
    m = re.fullmatch(r"mov (r\d+),#(0x[0-9a-f]+)", mov)
    s = re.fullmatch(r"lsl (r\d+),(r\d+),#(\d+)", lsl)
    if not m or not s or {m[1]} != {s[1], s[2]}:
        raise AssertionError(f"rom:0x{mov_at:X} and rom:0x{lsl_at:X} decode as {mov!r} and {lsl!r},"
                             f" which is not one register building one constant")
    return int(m[2], 16) << int(s[3])


def _imm(rom, at):
    """The immediate of the `add rX,#imm8` or `cmp rX,#imm8` at this offset."""
    text, _ = thumb_dis.dis(rom, at + ROM_BASE)
    found = re.fullmatch(r"(add|cmp) r\d+,#(0x[0-9a-f]+)", text)
    if not found:
        raise AssertionError(f"rom:0x{at:X} decodes as {text!r}, not an immediate add or compare")
    return int(found[2], 16)


def _decode_layout(rom):
    """The three layout values the ROM's own code builds. Raises when the sites of one family
    disagree, which is the whole risk of a 14-site edit, or when the add chain lands elsewhere."""
    out = {}
    for key in ("size", "header", "block"):
        seen = {_pair(rom, mov, lsl) for mov, lsl, which, _w in sf.MENU_SITES if which == key}
        if len(seen) != 1:
            raise AssertionError(f"the {key} sites build {sorted(hex(v) for v in seen)}, not one value")
        out[key] = seen.pop()
    folded = _pair(rom, sf.CHAIN_MOV, sf.CHAIN_LSL) + _imm(rom, sf.CHAIN_ADD)
    if folded != out["header"]:
        raise AssertionError(f"the folded add chain gives 0x{folded:X}, not the header 0x{out['header']:X}")
    return out


def _fits(layout, entries):
    """(list 1 end, list 2 end, block end) for `entries` rows, or an AssertionError. The bases are
    DERIVED from the decoded layout, so a moved header moves list 2's base with it."""
    ends = (("list 1", sf.LIST1_AT + sf.LIST1_ENTRY * entries, layout["header"]),
            ("list 2", layout["header"] + 4 + sf.LIST2_ENTRY * entries, layout["block"]),
            ("the block", layout["block"] + sf.BLOCK_LEN, layout["size"]))
    for what, end, limit in ends:
        if end > limit:
            raise AssertionError(f"{what} ends at +0x{end:X}, past +0x{limit:X}, at {entries} entries")
    return tuple(end for _w, end, _l in ends)


def _undeclared(rom, without, sites):
    """Every byte in the scouter code region that differs between the two builds and does NOT lie
    inside a declared site. This is the check a 4-byte write at a gapped site fails."""
    covered = {a for at, length, _what in sites for a in range(at, at + length)}
    return [hex(a) for a in range(*MENU_CODE) if rom[a] != without[a] and a not in covered]


class ScouterFutureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = log2_build.read_build_list(LIST)
        cls.rom, cls.alloc = log2_build.assemble(log2_build.BASE, names)
        cls.notes = cls.alloc.notes["scouter_future"]
        cls.base = bytearray(log2_build.BASE.read_bytes())
        cls.without, cls.alloc_without = log2_build.assemble(
            log2_build.BASE, [n for n in names if n != "scouter_future"])
        # The list truncated just BEFORE this module: the only state in which apply() may run, and
        # the one a control needs to perturb.
        cls.before, cls.alloc_before = log2_build.assemble(
            log2_build.BASE, names[:names.index("scouter_future")])
        cls.base_sites = sorted((at, n, w) for at, n, w in cls.notes["sites"] if at < 0x800000)

    # ----- the table -----

    def test_the_table_moved_and_every_literal_came_with_it(self):
        table = self.notes["table"]
        self.assertNotEqual(table, sf.TABLE)
        for lit in sf.BASE_LITERALS:
            self.assertEqual(_u32(self.rom, lit), table + ROM_BASE, f"literal rom:0x{lit:X}")

    def test_the_128_live_entries_came_across_byte_for_byte(self):
        """The copy is of the LIVE table, not the base one. superperfect_cell already rewrites entry
        19 in place (its own SCOUTER_19 constant), so a copy of the base bytes would silently undo
        Super Perfect Cell's scouter row. The build WITHOUT this module gives the right answer,
        because every module that writes the table runs before this one."""
        want = bytes(self.without[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES])
        got = bytes(self.rom[self.notes["table"]:self.notes["table"] + sf.ENTRY * sf.ENTRIES])
        self.assertEqual(got, want)
        self.assertEqual(bytes(self.rom[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES]), want,
                         "and the table at its old address is left exactly as it stood")
        self.assertNotEqual(want, bytes(self.base[sf.TABLE:sf.TABLE + sf.ENTRY * sf.ENTRIES]),
                            "the live table really does differ from the base one")

    def test_the_string_pool_is_untouched(self):
        end = sf.POOL + 0x2000
        self.assertEqual(bytes(self.rom[sf.POOL:end]), bytes(self.base[sf.POOL:end]))

    def test_nothing_still_points_into_the_old_table(self):
        """A pointer left behind would read a vanilla entry that the game no longer indexes."""
        lo, hi = sf.TABLE + ROM_BASE, sf.TABLE + sf.ENTRY * sf.ENTRIES + ROM_BASE
        words = memoryview(bytes(self.rom)).cast("I")
        self.assertEqual([4 * i for i, w in enumerate(words) if lo <= w < hi], [])

    # ----- the one code byte -----

    def test_every_base_rom_byte_it_writes_is_one_of_its_own_declared_sites(self):
        """Read out of its own declared sites, not out of a ROM diff: removing the module moves every
        later allocation, so a diff of the two builds says nothing about this module. The allowed
        addresses are taken from the module's OWN tables, never from a list typed here."""
        allowed = (set(sf.BASE_LITERALS) | set(sf.RAISED_BOUNDS) | {sf.CHAIN_ADD}
                   | {at for mov, lsl, _k, _w in sf.MENU_SITES for at in (mov, lsl)})
        self.assertEqual([at for at, _n, _w in self.base_sites if at not in allowed], [])
        for at in sf.BASE_LITERALS:
            self.assertIn((at, 4), [(a, n) for a, n, _w in self.base_sites])

    def test_no_menu_site_is_written_wider_than_a_halfword(self):
        """THE rule of this grow. Four sites are gapped, and rom:0x19324 carries the `add sp,r3`
        that builds the 0x1080 stack frame between its two halves, so a 4-byte write there would
        destroy live code."""
        menu = {at for mov, lsl, _k, _w in sf.MENU_SITES for at in (mov, lsl)}
        for at, n, what in self.base_sites:
            if at in menu:
                self.assertEqual(n, 2, f"rom:0x{at:X} is written {n} bytes wide: {what}")
        self.assertEqual({n for at, n in self.notes["menu_sites"] if at in menu}, {2})
        self.assertEqual({n for at, n in self.notes["menu_sites"] if at not in menu}, {1},
                         "the add chain and the list bound are single bytes")

    def test_nothing_in_the_scouter_code_changed_outside_a_declared_site(self):
        """The check a 4-byte write fails. Its control is below."""
        self.assertEqual(_undeclared(self.rom, self.without, self.base_sites), [])

    def test_every_declared_site_really_moved(self):
        """A site list that claims a change which did not happen is a lie the report would repeat."""
        for at, n, what in self.base_sites:
            self.assertNotEqual(bytes(self.rom[at:at + n]), bytes(self.without[at:at + n]),
                                f"rom:0x{at:X} is declared but unchanged: {what}")

    def test_the_unchanged_shift_of_the_size_site_is_left_alone(self):
        """rom:0x1920C still builds 0x6E0 as `lsl r0,r0,#4`, so the module does not write it. An
        instruction that does not have to change must not appear in the site list."""
        mov_at, lsl_at, which, _w = sf.MENU_SITES[0]
        self.assertEqual(which, "size")
        self.assertEqual(bytes(self.rom[lsl_at:lsl_at + 2]), bytes(self.base[lsl_at:lsl_at + 2]))
        self.assertNotIn(lsl_at, [at for at, _n, _w in self.base_sites])
        self.assertNotEqual(bytes(self.rom[mov_at:mov_at + 2]), bytes(self.base[mov_at:mov_at + 2]))

    def test_both_raised_bounds_are_131_and_the_compares_themselves_are_intact(self):
        for at in sf.RAISED_BOUNDS:
            self.assertEqual(self.rom[at], sf.NEW_BOUND, f"rom:0x{at:X}")
            self.assertEqual(self.rom[at + 1], sf.BOUND_SITES[at][0][1],
                             f"rom:0x{at:X}: the CMP itself is unchanged, only its immediate moved")
            self.assertEqual(_imm(self.rom, at), sf.NEW_BOUND, f"rom:0x{at:X} decoded")
        self.assertEqual(sf.NEW_BOUND, sf.ENTRIES + len(self.notes["new"]))
        self.assertEqual(self.notes["list_slots"], sf.NEW_BOUND)

    def test_the_set_matcher_bound_is_still_128(self):
        """Measured, not assumed. Raising it could not change one scan: the set matcher returns the
        FIRST entry whose set id matches, and our three sets are already carried by vanilla entries."""
        self.assertEqual(self.rom[sf.SET_MATCH_BOUND], sf.OLD_BOUND)

    # ----- the grown list menu object -----

    def test_the_menu_object_decodes_as_one_value_per_family(self):
        """Decoded with thumb_dis, not with the module's encoder. All 8 block sites must agree, all
        4 header sites must agree, and the folded add chain must land on the same header."""
        got = _decode_layout(self.rom)
        self.assertEqual(got, {"header": self.notes["menu_header"],
                               "block": self.notes["menu_block"],
                               "size": self.notes["menu_object"]})
        self.assertEqual(_decode_layout(self.without),
                         {"header": sf.OLD_HEADER, "block": sf.OLD_BLOCK, "size": sf.OLD_SIZE},
                         "and the build without this module still holds the vanilla layout")

    def test_the_grown_object_holds_131_entries(self):
        """The capacity arithmetic, every base DERIVED from the decoded layout. List 2 starts at the
        NEW header plus its count word, never at the old 0x284."""
        got = _decode_layout(self.rom)
        list1_end, list2_end, block_end = _fits(got, sf.NEW_BOUND)
        self.assertLessEqual(list1_end, got["header"])
        self.assertLessEqual(list2_end, got["block"])
        self.assertEqual(block_end, got["size"], "the block ends exactly on the object size")
        self.assertEqual(got["block"], sf.OLD_SIZE,
                         "the new block starts where the vanilla object ended")

    def test_the_vanilla_object_could_not_have_held_131(self):
        """The control on the capacity check itself: the same arithmetic over the vanilla layout has
        to fail, or it would pass for any object and prove nothing."""
        vanilla = {"header": sf.OLD_HEADER, "block": sf.OLD_BLOCK, "size": sf.OLD_SIZE}
        with self.assertRaises(AssertionError):
            _fits(vanilla, sf.NEW_BOUND)

    def test_every_gap_instruction_survived(self):
        """Read back from the ROM, instruction by instruction. These are the bytes a 4-byte write at
        a gapped `mov` would have eaten."""
        for at in range(0x19326, 0x19330, 2):
            self.assertEqual(bytes(self.rom[at:at + 2]), bytes(self.without[at:at + 2]),
                             f"rom:0x{at:X} sits between the two halves of the rom:0x19324 site")
        self.assertEqual(thumb_dis.dis(self.rom, 0x19326 + ROM_BASE)[0], "add sp,r3")
        for at in (0x1922C, 0x197BE, 0x199A2):
            self.assertEqual(bytes(self.rom[at:at + 2]), bytes(self.without[at:at + 2]),
                             f"rom:0x{at:X} sits inside a gapped site")

    def test_the_add_chains_own_pair_is_untouched(self):
        """rom:0x19724 `add r7,r2,r1` uses the 0x24C that pair builds, with a ROM address in r1, so
        moving the pair would move that pointer too. Only the add immediate may change."""
        for at in (sf.CHAIN_MOV, sf.CHAIN_LSL, 0x19724):
            self.assertEqual(bytes(self.rom[at:at + 2]), bytes(self.without[at:at + 2]),
                             f"rom:0x{at:X}")
        self.assertEqual(_pair(self.rom, sf.CHAIN_MOV, sf.CHAIN_LSL), 0x24C)
        self.assertEqual(_imm(self.without, sf.CHAIN_ADD) + 0x24C, sf.OLD_HEADER)

    # ----- controls: each check is shown going red on a real build -----

    def test_control_a_four_byte_write_at_the_gapped_site_is_caught(self):
        """A test that cannot fail is not a test. This is the exact mistake the brief forbids."""
        spoiled = bytearray(self.rom)
        spoiled[0x19324:0x19328] = bytes(self.rom[0x19324:0x19326]) + bytes(self.rom[0x19330:0x19332])
        self.assertNotEqual(bytes(spoiled), bytes(self.rom))
        self.assertEqual(_undeclared(self.rom, self.without, self.base_sites), [])
        self.assertEqual(_undeclared(spoiled, self.without, self.base_sites), ["0x19326", "0x19327"])
        self.assertNotEqual(thumb_dis.dis(spoiled, 0x19326 + ROM_BASE)[0], "add sp,r3")

    def test_control_b_one_stale_shift_is_caught(self):
        """Revert a single `lsl` to its vanilla #7 and the family check has to go red."""
        _mov_at, lsl_at, which, _w = [s for s in sf.MENU_SITES if s[2] == "block"][0]
        spoiled = bytearray(self.rom)
        spoiled[lsl_at:lsl_at + 2] = bytes(self.without[lsl_at:lsl_at + 2])
        _decode_layout(self.rom)
        with self.assertRaises(AssertionError) as caught:
            _decode_layout(spoiled)
        self.assertIn(which, str(caught.exception))

    def test_control_c_a_perturbed_site_stops_the_module_before_it_writes(self):
        """The module checks every site before the first write, so a surprise leaves the ROM whole."""
        rom = bytearray(self.before)
        mov_at = sf.MENU_SITES[-1][0]
        rom[mov_at:mov_at + 2] = struct.pack(
            "<H", struct.unpack_from("<H", self.before, mov_at)[0] ^ 1)   # one bit of the immediate
        unspoiled = bytes(rom)
        with self.assertRaises(ValueError) as caught:
            sf.apply(rom, self.alloc_before)
        self.assertIn(f"0x{mov_at:X}", str(caught.exception))
        self.assertEqual(bytes(rom), unspoiled, "it raised BEFORE it wrote anything")
        self.assertNotIn("scouter_future", self.alloc_before.notes)

    # ----- the three new entries -----

    def test_each_new_entry_names_its_own_weakened_type(self):
        """This is the whole defect: an enemy scans by TYPE ENTRY POINTER (bible B2297), so an entry
        whose +0x10 does not name the live type cannot be found at all."""
        types = {}
        for key, sub in (("future_androids", "types"), ("ending_fight", "cell_type")):
            value = self.alloc.notes[key][sub]
            types.update(value if isinstance(value, dict) else {28: value})
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            self.assertEqual(_u32(self.rom, at + sf.F_TYPE), detail["type"])
            self.assertEqual(detail["type"], types[detail["set"]],
                             f"{detail['name']} must name the live weakened type of set {detail['set']}")
            self.assertNotEqual(detail["type"], 0, "a 0 type makes the scan show ???")

    def test_the_type_each_entry_names_resolves_to_a_real_enemy_entry(self):
        for detail in self.notes["new"]:
            at = ENEMY_TABLE + ENEMY_ENTRY * detail["type"]
            hp = _u32(self.rom, at + 4)
            self.assertTrue(0 < hp < 100000, f"{detail['name']} HP {hp}")
            self.assertNotEqual(bytes(self.rom[at:at + ENEMY_ENTRY]), b"\xFF" * ENEMY_ENTRY)

    def test_round_2_fights_the_enemy_future_cell_scans_as(self):
        """The plateau's own round 2 item has to carry the same type the Future Cell entry names, or
        the owner scans one Cell and fights another."""
        item = self.alloc.notes["plateau"]["item"]
        cell = [d for d in self.notes["new"] if d["set"] == 28][0]
        self.assertEqual(_u32(self.rom, item + 8), cell["type"])

    def test_the_names_and_portraits_are_the_ones_he_asked_for(self):
        self.assertEqual(sf.names(), ("Future 17", "Future 18", "Future Cell"))
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            self.assertEqual(_cstr(self.rom, _u32(self.rom, at + sf.F_NAME) - ROM_BASE), detail["name"])
            self.assertEqual(_u32(self.rom, at + sf.F_SET), detail["set"])
            self.assertEqual(_u32(self.rom, at + sf.F_PORTRAIT), detail["portrait"])
            self.assertEqual(_u32(self.base, sf.TABLE + sf.ENTRY * detail["from"] + sf.F_PORTRAIT),
                             detail["portrait"], "the portrait is the vanilla entry's own")

    def test_each_bio_is_the_vanilla_text_plus_the_one_shared_closing_line(self):
        for k, detail in zip(sf.NEW_ENTRIES, self.notes["new"]):
            at = self.notes["table"] + sf.ENTRY * k
            text = _cstr(self.rom, _u32(self.rom, at + sf.F_BIO) - ROM_BASE)
            vanilla = _cstr(self.base, _u32(self.base, sf.TABLE + sf.ENTRY * detail["from"]
                                            + sf.F_BIO) - ROM_BASE)
            self.assertTrue(text.endswith(sf.TAIL), detail["name"])
            body = text[:-len(sf.TAIL)]
            self.assertEqual(body, vanilla.replace(sf.CELL_CUT, "", 1) if detail["set"] == 28
                             else vanilla)
            self.assertEqual(len(text), detail["bio_len"])

    def test_the_lengths_are_the_measured_ones(self):
        """581, 582 and 587 against the vanilla table's own 582 ceiling. Cell is 5 over, which is
        why the module drops a sentence rather than keeping the whole vanilla bio."""
        self.assertEqual([d["bio_len"] for d in self.notes["new"]], [581, 582, 587])
        self.assertEqual(self.notes["longest_bio"], 587)
        self.assertNotIn(sf.CELL_CUT.strip(), _cstr(
            self.rom, _u32(self.rom, self.notes["table"] + sf.ENTRY * 130 + sf.F_BIO) - ROM_BASE))

    def test_the_save_bits_are_the_spare_byte_and_nothing_past_it(self):
        self.assertEqual(self.notes["save_bits"], [(0x12A, 0), (0x12A, 1), (0x12A, 2)])
        self.assertEqual(sf.O_SCOUTER + (sf.SCOUTER_BITS - 1 >> 3), sf.SAVE_SPARE_BYTE - 1,
                         "the documented field ends on the byte before the spare one")

    # ----- order and re-runs -----

    def test_a_second_run_raises(self):
        with self.assertRaises(ValueError):
            sf.apply(bytearray(self.rom), self.alloc)

    def test_it_refuses_to_run_after_plateau(self):
        """plateau relocates the MAP table and must stay last, so this module declares the order."""
        notes = dict(self.alloc.notes)
        notes.pop("scouter_future")
        rom, alloc = log2_build.assemble(
            log2_build.BASE, [n for n in log2_build.read_build_list(LIST) if n != "scouter_future"])
        with self.assertRaises(ValueError):
            sf.apply(rom, alloc)                       # alloc.notes already holds "plateau"


if __name__ == "__main__":
    unittest.main()
