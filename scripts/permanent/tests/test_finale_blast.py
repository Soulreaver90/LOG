r"""
test_finale_blast.py - The finale blast: a GOLD beam that no vanilla beam sees, and the owner's own
                       section 5, read back out of the built ROM.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_finale_blast.py -v

Builds build_list_trial_plateau.txt in memory once, and also the list WITHOUT this module, so every
claim is a difference between two ROMs rather than a repeat of the module's own arithmetic. The two
copied Thumb bodies are read back TWO ways: disassembled against the vanilla listing instruction for
instruction, and RUN on the test_ssj2 interpreter, which is the only way to prove that the copy
passes argument 6 = 1 where vanilla passes 0.

What it cannot read: how the gold beam looks on screen, how long the beam takes to cross the 64 px
to Cell, and whether the arm raise reads as a shot. Those are the owner's eye and they are in the
report, not here.
"""
import struct
import unittest

import log2_build
from patches import finale_blast as FB
from patches import plateau
from rom import thumb_dis
from rom.webfoot_decompress import set_offset as _set_offset
from rom.rom_space import Allocator
from scene import scene_lib as S
from tests.test_ssj2 import Cpu

ROM_BASE = 0x08000000
LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_plateau.txt"
# The dialog box: 4 lines of 144 px a page (bible C4S and B2095), on the font at rom:0x2CC64. The
# widest box the ending talk renders in vanilla is 294 px, ending word 3.
DIALOG_FONT, DIALOG_WIDTH, BOX_LINES, WIDEST_VANILLA_BOX = 0x2CC64, 0x90, 4, 294
BEAM_BUILDER = 0x080143A8                 # the beam object, where both builders stop
OBJ, POS, ACTOR, STACK, RET = 0x02001000, 0x02002000, 0x02003000, 0x03004000, 0x01000000
# The tick run: the command object, the beam it owns, the actor that fires it, and the two base
# routines the run stops at. `sub_08007A26` is the spawn point and `sub_08014478` is the fire call.
CMD, BEAM, SHOOTER = 0x02004000, 0x02005000, 0x02006000
SPAWN_CALL, FIRE_CALL = 0x08007A26, 0x08014478
CMD_BEAM, CMD_LEFT, CMD_FIRE_AT = 8, 0xC, 0x10     # the command's own words, read by the tick
ACTOR_FACING = 0x10
# Trunks' own point in the test world, and his measured direction 1 hurtbox, relative to that point.
# The rect is the one read out of the owner's save state finale_poses_wip1.ss3 (bible B2319), and
# `sub_08007A26` returns its CENTRE for facing 1 (B1964), which is his point - 8 in y.
SHOOTER_POINT = (0x300, 0x200)
DIR1_RECT = (-2, -26, 17, 10)
# Where the beam has to leave him, in his own coordinates. -8 is his hurtbox centre, which is where
# the vanilla tick fires from and is the bottom row of his sprite. -37 is 29 px above it, the top
# row of his raised hands. The owner judges this by eye; these two numbers are what the eye saw.
VANILLA_FIRE_DY, HANDS_FIRE_DY = -8, -37
MUZZLE_TABLE, MUZZLE_BYTES = 0x701DF0, 32          # the vanilla offset table both beams read
# The gold beam's own frame records: 8 a direction, dir 1 is UP (bible FBM). The set id word is
# 0x08704604 and the owner's beam fires along direction 1.
GOLD_BEAM, BEAM_RUN = 0x704604, 8
# Rect_FromDefinition @0x080079B8 reads the actor's box from set + 0xC + 16 * direction, four signed
# words: left, top, right, bottom, each relative to the actor's own point.
BOX_AT, BOX_STRIDE = 12, 16


def _beam_records(rom, direction):
    """One direction's run of the gold beam, as 12 byte frame records."""
    at = GOLD_BEAM + 12 * BEAM_RUN * direction
    return [struct.unpack_from("<bbBB", rom, at + 12 * k) for k in range(BEAM_RUN)]


def _actor_box(rom, set_off, direction):
    """(left, top, right, bottom) of one direction's box, the rect gb_start takes its centre of."""
    return struct.unpack_from("<4i", rom, set_off + BOX_AT + BOX_STRIDE * direction)


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def _dialog_wrap(rom, box):
    """Lines of one box as the dialog line counter breaks them: past 144 px, at the last space.

    The same model test_plateau and test_chapter_cards use, which reproduces every vanilla box."""
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


def _listing(rom, at, size):
    """[(GBA address, text)] of a Thumb body, straight out of the ROM it was built into."""
    out, o = [], at
    while o < at + size:
        text, step = thumb_dis.dis(rom, o + ROM_BASE)
        out.append((o + ROM_BASE, text))
        o += step
    return out


def _calls_folded(listing, trampolines):
    """The copy's texts with every trampoline call folded back into the plain `bl` it stands for.

    A Thumb `bl` reaches about 4 MB and this code sits about 8 MB from the base ROM, so each call
    became `ldr r3,=SYM ; bl via_r3` or, where r3 is an argument, `ldr r0,=SYM ; mov r12,r0 ; ... ;
    bl via_r12`. Folding those back is what lets the copy be compared with the vanilla listing.
    The setup line that fed a folded call is dropped with it; every other `ldr` of a literal stays."""
    out, held, setup = [], {}, {}
    for at, text in listing:
        if text.startswith("ldr r3,=") or text.startswith("ldr r0,="):
            reg = text.split(",")[0].split()[1]
            held[reg], setup[reg] = int(text.split("=")[1], 16), len(out)
            out.append((at, text))
            continue
        if text == "mov r12,r0":
            out[setup.pop("r0")] = None                   # the ldr that fed r12 goes with it
            held["r12"], setup["r12"] = held.pop("r0"), len(out)
            out.append((at, text))
            continue
        if text.startswith("bl "):
            via = trampolines.get(int(text.split()[1], 16))
            if via == "via_r2":                           # vanilla's own `bx r2` helper, no setup
                out.append((at, "bl 0x8021d2c"))
                continue
            if via is not None:
                reg = via.split("_")[1]
                out[setup.pop(reg)] = None
                out.append((at, f"bl {held.pop(reg) & ~1:#x}"))
                continue
        out.append((at, text))
    return [row for row in out if row is not None]


def _by_index(rows, subs=()):
    """Each instruction as text, with every branch target written as an INSTRUCTION distance.

    Two bodies at two addresses cannot be compared line by line while their branches carry absolute
    targets. `subs` is the list of (seen, write as) pairs a copy is allowed to differ by."""
    starts = [at for at, _ in rows]
    out = []
    for i, (_at, text) in enumerate(rows):
        for seen, instead in subs:
            if text == seen:
                text = instead
        head, _, rest = text.partition(" ")
        if head in ("b", "bl") or (head.startswith("b") and len(head) == 3):
            target = int(rest, 16) if rest.startswith("0x") else None
            # A folded setup line leaves a hole, so a branch lands on the first SURVIVING
            # instruction at or after its target, which is the same instruction either way.
            landing = next((k for k, a in enumerate(starts) if a >= target), None) if target else None
            if landing is not None and starts[0] <= target <= starts[-1]:
                text = f"{head} {landing - i:+d}"
        out.append(text)
    return out


def _ops(rom, at):
    """[(ext number, pushed arguments)] of a type 0 record, which is how these records are written."""
    out, stack, o = [], [], at + 3
    end = S.record_end(rom, at) - 1
    while o < end:
        op = rom[o]
        nxt = S.op_end(rom, o)
        if op == 0:
            stack.append(rom[o + 1])
        elif op in (1, 29):
            at_v = o + 2 if op == 29 else o + 1
            for _ in range(rom[o + 1] if op == 29 else 1):
                v, at_v = S.unzigzag(rom, at_v)
                stack.append(v)
        elif op == 2:
            out.append((rom[o + 1], tuple(stack)))
            stack = []
        else:
            raise AssertionError(f"rom:0x{o:X} carries base op {op}, which _ops cannot read")
        o = nxt
    return out


def _run_builder(rom, entry, colour_at_sp=4):
    """(r0, r1, r2, r3, [sp], [sp+4]) where a beam builder calls the beam object.

    r0 is non-zero, so the allocate arm is never taken and the run needs no stub."""
    cpu = Cpu(rom)
    cpu.r[0], cpu.r[1], cpu.r[2], cpu.r[3] = OBJ, POS, 0, ACTOR
    cpu.r[13], cpu.r[14] = STACK, RET | 1
    cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
    where = cpu.run(entry, {BEAM_BUILDER: "beam", RET: "returned"})
    assert where == "beam", where
    return (cpu.r[0], cpu.r[1], cpu.r[2], cpu.r[3],
            cpu.load(cpu.r[13], 4), cpu.load(cpu.r[13] + colour_at_sp, 4))


def _run_tick(rom, entry):
    """(fire x, fire y) where a command tick hands its point to the beam fire call @0x08014478.

    The run starts on the tick BEFORE the beam fires, so the count reaches the fire tick and the
    record's whole fire path runs. Only `sub_08007A26` is stubbed: it walks a live actor through
    `Rect_FromDefinition` and ends in `stmia`, which the interpreter cannot run. Its answer for
    facing 1 is the hurtbox centre, so the stub writes exactly that. The muzzle table lookup, the
    two adds and the lift are all the real code out of the built ROM."""
    cpu = Cpu(rom)
    centre = tuple(SHOOTER_POINT[k] + (DIR1_RECT[k] + DIR1_RECT[k + 2]) // 2 for k in (0, 1))

    def spawn_point(c):
        c.store(c.r[0], 4, centre[0])
        c.store(c.r[0] + 4, 4, centre[1])
        return 0

    cpu.store(CMD + CMD_BEAM, 4, BEAM)
    cpu.store(CMD + CMD_LEFT, 4, 2)                  # one tick left before it fires
    cpu.store(CMD + CMD_FIRE_AT, 4, 1)               # the count it fires on
    cpu.store(SHOOTER + ACTOR_FACING, 1, plateau.UP)
    cpu.r[0], cpu.r[1] = CMD, SHOOTER
    cpu.r[13], cpu.r[14] = STACK, RET | 1
    cpu.r[4:8] = [0x44444444, 0x55555555, 0x66666666, 0x77777777]
    where = cpu.run(entry, {SPAWN_CALL: spawn_point, FIRE_CALL: "fired", RET: "returned"})
    assert where == "fired", where
    assert cpu.r[0] == BEAM, "the fire call takes the command's own beam"
    return cpu.load(cpu.r[2], 4), cpu.load(cpu.r[2] + 4, 4)


class FinaleBlastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = log2_build.read_build_list(LIST)
        cls.rom, cls.alloc = log2_build.assemble(log2_build.BASE, names)
        cls.notes = cls.alloc.notes["finale_blast"]
        cls.without, cls.alloc_without = log2_build.assemble(
            log2_build.BASE, [n for n in names if n != "finale_blast"])
        cls.base = log2_build.BASE.read_bytes()

    # ----- 1. nothing vanilla moved -----

    def test_no_vanilla_beam_byte_changed(self):
        """The whole point of a second entry point: Gohan's Cell Games Kamehameha stays blue."""
        for at, want in ((FB.HANDLER_AT, FB.HANDLER_BYTES), (FB.START_AT, FB.START_BYTES),
                         (FB.TICK_AT, FB.TICK_BYTES), (FB.BUILD_AT, FB.BUILD_BYTES)):
            self.assertEqual(bytes(self.rom[at:at + len(want) // 2]), bytes.fromhex(want),
                             f"rom:0x{at:X}")
        self.assertEqual(self.rom[FB.COLOUR_BYTE], FB.BLUE, "the vanilla colour argument is still 0")
        self.assertEqual(bytes(self.rom[MUZZLE_TABLE:MUZZLE_TABLE + MUZZLE_BYTES]),
                         bytes(self.base[MUZZLE_TABLE:MUZZLE_TABLE + MUZZLE_BYTES]),
                         "the muzzle offset table is shared with the blue beam and is never written")
        for k, want in enumerate(FB.VANILLA_VTABLE):
            self.assertEqual(_u32(self.rom, FB.VTABLE_AT + 4 * k), want, f"vanilla vtable slot {k}")

    def test_the_only_base_rom_writes_are_three_pool_words(self):
        """Every other byte this module changes sits in the expansion area. The three are the two
        ext op table pool words chapter_cards already owns, and gohan_gi's own set table literal,
        which this module repoints at a table with two more ids on the end."""
        mine = memoryview(bytes(self.rom[:0x800000])).cast("I")
        theirs = memoryview(bytes(self.without[:0x800000])).cast("I")
        changed = [4 * i for i in range(len(mine)) if mine[i] != theirs[i]]
        self.assertEqual(changed, sorted(FB.EXT_POOLS + (FB.SET_TABLE_LITERAL,)),
                         [hex(o) for o in changed])

    # ----- 1b. the two held-pose sets -----

    def test_the_clones_hold_one_picture_a_row_and_the_vanilla_rows_do_not(self):
        """The owner's section 7: Cell holds his charge and Trunks holds two frames. A held pose
        needs a ROW whose records all point at one frame, and `clone_set` plus `hold_row` builds
        one without writing a byte of the source set."""
        n = self.notes
        want = {(FB.CELL_HOLD_ID,) + FB.CELL_HOLD_ROW: (7, FB.CHARGE_HEADER),
                (FB.TRUNKS_HOLD_ID,) + FB.TRUNKS_IDLE_ROW: (2, FB.HANDS_DOWN_HEADER),
                (FB.TRUNKS_HOLD_ID,) + FB.TRUNKS_BEAM_ROW: (7, FB.HANDS_UP_HEADER)}
        for (set_id, anim, direction), (count, header) in want.items():
            recs = FB.row_records(self.rom, _set_offset(self.rom, set_id), anim, direction)
            self.assertEqual(len(recs), count, f"set {set_id} anim {anim} dir {direction}")
            self.assertEqual({r["header"] for r in recs}, {header},
                             f"set {set_id} anim {anim} dir {direction} is not one held picture")
        self.assertEqual(n["cell_hold_id"], FB.CELL_HOLD_ID)
        self.assertEqual(n["trunks_hold_id"], FB.TRUNKS_HOLD_ID)

    def test_no_live_vanilla_row_was_written(self):
        """set 28 anim 18 is Imperfect Cell's own vanilla Kamehameha, driven by `ext 137` at
        rom:0x3E1484 on map 10,20, and set 133 anim 18 is Trunks' sword special, which
        future_androids ships. Neither may move, so this reads BOTH sets back against the ROM built
        without this module, record list by record list."""
        for set_id in (FB.CELL_SET, FB.SSJ_TRUNKS):
            mine = _set_offset(self.rom, set_id)
            theirs = _set_offset(self.without, set_id)
            self.assertEqual(mine, theirs, f"set {set_id} moved")
            self.assertEqual([(r["anim"], r["dir"], r["index"], r["header"], r["rec"])
                              for r in FB.set_records(self.rom, mine)],
                             [(r["anim"], r["dir"], r["index"], r["header"], r["rec"])
                              for r in FB.set_records(self.without, theirs)],
                             f"set {set_id} reads differently")
        self.assertEqual(bytes(self.rom[0x3E1460:0x3E14A0]),
                         bytes(self.without[0x3E1460:0x3E14A0]),
                         "Imperfect Cell's vanilla ext 137 site is untouched")

    def test_the_blue_beam_keeps_every_byte_it_ever_had(self):
        """The lift that moves the GOLD beam may not reach the blue one, because `ext 137`'s other
        vanilla site is Gohan's Cell Games Kamehameha. Each range below is read against the BASE
        ROM, not against the build without this module, so a change made anywhere in the chain
        shows up here too.

        The muzzle offset table is the trap: it is 8 bytes a direction, its direction 1 entry is
        (0, 0), and BOTH beams read it. The lift is in the cloned `gb_start` instead."""
        for at, size, name in ((FB.BUILD_AT, len(FB.BUILD_BYTES) // 2, "the vanilla beam builder"),
                               (FB.START_AT, len(FB.START_BYTES) // 2, "the vanilla command start"),
                               (FB.HANDLER_AT, len(FB.HANDLER_BYTES) // 2, "the ext 137 handler"),
                               (0x701DF0, 8 * 4, "the muzzle offset table"),
                               (FB.VTABLE_AT, 4 * FB.VTABLE_WORDS, "the ext 137 command vtable")):
            self.assertEqual(bytes(self.rom[at:at + size]), bytes(self.base[at:at + size]),
                             f"{name} at rom:0x{at:X} was written")
        cell, span = 0x3E1460, 0x40          # the window that holds his ext 137 site, rom:0x3E147E
        self.assertEqual(bytes(self.rom[cell:cell + span]), bytes(self.base[cell:cell + span]),
                         "Imperfect Cell's own ext 137 site rom:0x3E147E was written")
        self.assertEqual(self.rom[FB.COLOUR_BYTE], FB.BLUE,
                         "the vanilla builder still passes argument 6 = 0, the blue set")

    def test_the_set_table_grew_by_two_and_kept_every_old_word(self):
        n = self.notes
        old = n["old_set_table"]
        self.assertEqual(_u32(self.without, FB.SET_TABLE_LITERAL), old + ROM_BASE)
        self.assertEqual(_u32(self.rom, FB.SET_TABLE_LITERAL), n["set_table"] + ROM_BASE)
        self.assertEqual(n["set_table_words"], FB.LIVE_SET_IDS + 2)
        self.assertEqual(bytes(self.rom[n["set_table"]:n["set_table"] + 4 * FB.LIVE_SET_IDS]),
                         bytes(self.without[old:old + 4 * FB.LIVE_SET_IDS]))
        for set_id, key in ((FB.CELL_HOLD_ID, "cell_hold"), (FB.TRUNKS_HOLD_ID, "trunks_hold")):
            self.assertEqual(_u32(self.rom, n["set_table"] + 4 * (set_id - FB.FIRST_SET_ID)),
                             n[key] + ROM_BASE)

    # ----- 2. the gold entry point -----

    def test_the_three_copies_are_the_vanilla_bodies_instruction_for_instruction(self):
        """Folded back through the trampolines, each copy reads as its vanilla original, with the
        deviations the module names and nothing else.

        `gb_start` and `gb_tick` each carry one ADDED instruction, the `sub r0,#BEAM_RISE` that
        lifts the beam to Trunks' hands. A text substitution cannot absorb an inserted line, so that
        one line is lifted out here and checked on its own in the test below. Everything else still
        has to match vanilla line for line."""
        n = self.notes
        trampolines = {n["labels"][name] & ~1: name for name in ("via_r3", "via_r2", "via_r12")}
        ends = (n["start"], n["build"], n["tick"], n["labels"]["via_r3"] - ROM_BASE)
        lift = f"sub r0,#{FB.BEAM_RISE:#x}"
        # (mine, vanilla, its length, the deviations this copy is allowed, the lines it ADDS)
        bodies = (
            (n["handler"], FB.HANDLER_AT, len(FB.HANDLER_BYTES) // 2,
             (("ldr r1,=0x0802521c", f"ldr r1,={n['vtable'] + ROM_BASE:#010x}"),
              ("stmia r0!,{r1,r2}", "str r1,[r0,#0x0]"),
              ("sub r0,#0x8", "str r2,[r0,#0x4]")), ()),
            (n["start"], FB.START_AT, len(FB.START_BYTES) // 2,
             (("bl 0x801d84c", f"bl {n['build'] + ROM_BASE:#x}"),), (lift,)),
            (n["build"], FB.BUILD_AT, len(FB.BUILD_BYTES) // 2,
             (("mov r2,#0x0", "mov r2,#0x1"),), ()),
            (n["tick"], FB.TICK_AT, len(FB.TICK_BYTES) // 2, (), (lift,)),
        )
        for (mine, theirs, size, subs, added), end in zip(bodies, ends):
            rows = _calls_folded(_listing(self.rom, mine, end - mine), trampolines)
            for text in added:
                hits = [k for k, (_at, t) in enumerate(rows) if t == text]
                self.assertEqual(len(hits), 1, f"rom:0x{mine:X} adds {text!r} exactly once")
                rows.pop(hits[0])
            got = _by_index(rows)
            want = _by_index(_listing(self.base, theirs, size), subs)
            self.assertEqual(got, want, f"the copy at rom:0x{mine:X} of rom:0x{theirs:X}")
        # And the deviations really are deviations: each one is in the copy and not in the vanilla.
        start = _by_index(_calls_folded(
            _listing(self.rom, n["start"], ends[1] - n["start"]), trampolines))
        self.assertIn("mov r1,#0x1e", start, "the forced state 30 is kept, as both vanilla sites do")
        build = _by_index(_calls_folded(
            _listing(self.rom, n["build"], ends[2] - n["build"]), trampolines))
        self.assertIn("mov r2,#0x1", build, "argument 6 = 1 is the gold set")
        self.assertNotIn("mov r2,#0x0", build)

    def test_the_beam_starts_at_his_hands_and_not_at_his_feet(self):
        """The owner, with a screenshot: "it needs to start where trunks hands are, right above it".

        Every number below is read out of the BUILT ROM, and the three together decide where the
        beam's bottom row lands:
          the spawn point is the CENTRE of the actor's direction 1 box, which Rect_FromDefinition
          @0x080079B8 builds from set + 0xC + 16 * direction and `gb_start` then halves;
          the gold beam's dir 1 run reaches 16 px BELOW that point;
          the firing frame is drawn at its own dy and is h rows tall.
        Without the lift the beam's bottom row IS the frame's bottom row, which is his feet, and
        that is what he saw. With it, the bottom row has to sit inside his sprite and in its top
        half, where his raised arms are. The exact value is his to nudge, so it is not pinned."""
        n = self.notes
        box = _actor_box(self.rom, n["trunks_hold"], plateau.UP)
        spawn = (box[1] + box[3]) // 2                   # the y gb_start hands the builder
        below = max(dy + h for _dx, dy, _w, h in _beam_records(self.rom, plateau.UP))
        frame = FB.row_records(self.rom, n["trunks_hold"], *FB.TRUNKS_BEAM_ROW)[0]
        top, bottom = frame["dy"], frame["dy"] + frame["h"]
        self.assertEqual(spawn + below, bottom,
                         "without the lift the beam ends on his bottom row, which is his feet")
        landed = spawn - FB.BEAM_RISE + below
        self.assertGreaterEqual(landed, top, "the beam may not start above his sprite")
        self.assertLess(landed, (top + bottom) // 2, "it starts in his top half, at his arms")
        self.assertTrue(0 <= FB.BEAM_RISE <= 0xFF, "a Thumb format 3 immediate holds 8 bits")
        self.assertEqual(n["beam_rise"], FB.BEAM_RISE)

    def test_the_lift_reaches_the_spawn_y_and_nothing_else(self):
        """The added `sub r0,#BEAM_RISE` has to sit between the `asr` that halves the box's two y
        corners and the `str` that writes the pair the builder reads, with nothing in between that
        writes r0. Read off the built ROM's own listing, so a move of the line fails here."""
        n = self.notes
        rows = [text for _at, text in _listing(self.rom, n["start"], n["build"] - n["start"])]
        half = rows.index("asr r0,r0,#1")
        lift = rows.index(f"sub r0,#{FB.BEAM_RISE:#x}")
        store = rows.index("str r0,[sp,#0x20]")
        self.assertLess(half, lift, "the lift comes after the halving")
        self.assertLess(lift, store, "and before the pair is written")
        self.assertEqual([t for t in rows[half + 1:store] if t.startswith(("mov r0", "add r0",
                                                                          "ldr r0", "asr r0",
                                                                          "lsr r0", "lsl r0"))], [],
                         "nothing else writes r0 between the halving and the store")
        self.assertEqual(rows.count(f"sub r0,#{FB.BEAM_RISE:#x}"), 1, "the lift runs once")

    def test_the_copied_builder_really_passes_the_gold_argument(self):
        """Run both builders on the same inputs and stop where each calls the beam object. Every
        argument has to match except argument 6, which is 0 in vanilla and 1 here."""
        mine = _run_builder(self.rom, self.notes["build"] + ROM_BASE)
        theirs = _run_builder(self.rom, FB.BUILD_AT + ROM_BASE)
        self.assertEqual(mine[:5], theirs[:5], "r0-r3 and argument 5 must be vanilla's")
        self.assertEqual(theirs[4], 0x400, "argument 5 is 0x400 in vanilla")
        self.assertEqual(theirs[5], FB.BLUE, "vanilla passes argument 6 = 0, the blue set")
        self.assertEqual(mine[5], FB.GOLD, "the copy passes argument 6 = 1, the gold set")

    def test_the_FIRED_beam_leaves_his_hands_and_not_his_feet(self):
        """The defect the owner saw in beam_start_wip1: the CHARGE moved and the BEAM did not.

        The command positions the beam TWICE. `gb_start` places the charge when the object is built.
        The TICK then rebuilds the point from the actor at the tick the beam FIRES and hands that
        pair to `sub_08014478`, which stores it into the beam's own +0x1C and +0x20. The fire pair
        is absolute, so the start's lift alone moves nothing the player sees.

        The tick under test is resolved out of VTABLE SLOT 2, the way the engine resolves it, and
        never by label. The defect WAS the slot, so a lift that is built but never wired in has to
        fail here.

        -8 is an INPUT, not a finding: it is the centre of the measured direction 1 rect that the
        stub writes, and `sub_08007A26` returns that centre for facing 1 (bible B1964, B2319). What
        the vanilla run proves is that the harness reaches the fire call at all and that direction
        1's muzzle dy adds nothing, so the only difference between the two ticks is the lift."""
        n = self.notes
        slots = FB.resolved(bytes(self.rom[n["vtable"]:n["vtable"] + 4 * FB.VTABLE_WORDS]),
                            n["vtable"])
        vanilla_x, vanilla_y = _run_tick(self.rom, 0x0801D7DD)
        gold_x, gold_y = _run_tick(self.rom, slots[FB.VTABLE_TICK_SLOT])
        point = SHOOTER_POINT[1]
        self.assertEqual(vanilla_y - point, VANILLA_FIRE_DY,
                         "the vanilla tick fires from his hurtbox centre, which is his feet")
        self.assertEqual(gold_y - point, HANDS_FIRE_DY,
                         "the gold tick has to fire from his raised hands")
        self.assertEqual(gold_y, vanilla_y - FB.BEAM_RISE, "and the whole difference is the lift")
        self.assertEqual(gold_x, vanilla_x, "only the y moves: the muzzle x is untouched")
        self.assertEqual(VANILLA_FIRE_DY - HANDS_FIRE_DY, FB.BEAM_RISE)

    def test_the_two_lifts_are_the_same_one_number(self):
        """The owner nudges the beam by eye, so the start and the tick may never disagree.

        Read off the built ROM's own listing: each body carries the lift exactly once, and both
        immediates are `BEAM_RISE`. A second constant is the failure this test exists to stop."""
        n = self.notes
        lift = f"sub r0,#{FB.BEAM_RISE:#x}"
        for name, at, end in (("gb_start", n["start"], n["build"]),
                              ("gb_tick", n["tick"], n["labels"]["via_r3"] - ROM_BASE)):
            rows = [text for _at, text in _listing(self.rom, at, end - at)]
            self.assertEqual(rows.count(lift), 1, f"{name} lifts once, by {lift}")
        self.assertTrue(0 <= FB.BEAM_RISE <= 0xFF, "a Thumb format 3 immediate holds 8 bits")

    def test_the_tick_lift_reaches_the_fire_y_and_nothing_else(self):
        """The added `sub r0,#BEAM_RISE` has to sit between the `add r0,r2,r0` that forms the fire y
        and the `str r0,[sp,#0x8]` that keeps it, with nothing in between that writes r0. One line
        later and the unlifted y is already stored; one line earlier and it lifts the muzzle dy."""
        n = self.notes
        end = n["labels"]["via_r3"] - ROM_BASE
        rows = [text for _at, text in _listing(self.rom, n["tick"], end - n["tick"])]
        form = rows.index("add r0,r2,r0")
        lift = rows.index(f"sub r0,#{FB.BEAM_RISE:#x}")
        store = rows.index("str r0,[sp,#0x8]")
        self.assertLess(form, lift, "the lift comes after the fire y is formed")
        self.assertLess(lift, store, "and before it is stored")
        self.assertEqual(rows[form + 1:store], [f"sub r0,#{FB.BEAM_RISE:#x}"],
                         "the lift is the only instruction between the two")
        self.assertEqual(rows.index("str r1,[sp,#0x18]") > store, True,
                         "the pair handed to the fire call is written after the lift")

    def test_the_vtable_copy_is_rebased_slot_by_slot(self):
        """A command vtable stores offsets from its OWN address, so a verbatim copy breaks it."""
        n = self.notes
        want = [(old + FB.VTABLE_AT + ROM_BASE) & 0xFFFFFFFF for old in FB.VANILLA_VTABLE]
        want[FB.VTABLE_START_SLOT] = (n["start"] + ROM_BASE) | 1
        want[FB.VTABLE_TICK_SLOT] = (n["tick"] + ROM_BASE) | 1
        got = FB.resolved(bytes(self.rom[n["vtable"]:n["vtable"] + 4 * FB.VTABLE_WORDS]), n["vtable"])
        self.assertEqual(got, want)
        self.assertEqual(got[FB.VTABLE_TICK_SLOT], (n["tick"] + ROM_BASE) | 1,
                         "slot 2 is the GOLD tick: the vanilla one would fire from his feet")
        self.assertEqual(got[3], 0x0801D839, "slot 3 is still the vanilla done")
        self.assertNotEqual(bytes(self.rom[n["vtable"]:n["vtable"] + 4 * FB.VTABLE_WORDS]),
                            bytes(self.rom[FB.VTABLE_AT:FB.VTABLE_AT + 4 * FB.VTABLE_WORDS]),
                            "a verbatim copy would be wrong, so the bytes must differ")

    # ----- 3. the ext op table -----

    def test_the_ext_table_copy_is_the_live_table_plus_one_word(self):
        """chapter_cards already moved the table, so a copy of the BASE table would undo its card op."""
        n = self.notes
        live, count = n["old_ext_table"], n["old_ext_words"]
        self.assertEqual(n["ext_table_owner"], "chapter_cards")
        self.assertNotEqual(live, FB.BASE_EXT_TABLE)
        self.assertEqual(bytes(self.rom[n["ext_table"]:n["ext_table"] + 4 * count]),
                         bytes(self.without[live:live + 4 * count]))
        self.assertEqual(n["ext_words"], count + 1)
        self.assertEqual(n["gold_op"], count)
        self.assertEqual(_u32(self.rom, n["ext_table"] + 4 * n["gold_op"]),
                         (n["handler"] + ROM_BASE) | 1)

    def test_both_pool_words_moved_and_the_parallel_table_did_not(self):
        """Base ops 21 to 26 index TWO tables: the handler table and the parallel one at 0x083B5F70.
        Only the handler table moves, which is what chapter_cards did before this module."""
        for p in FB.EXT_POOLS:
            self.assertEqual(_u32(self.rom, p), self.notes["ext_table"] + ROM_BASE, f"rom:0x{p:X}")
        for p in FB.SECOND_POOLS:
            self.assertEqual(_u32(self.rom, p), FB.SECOND_TABLE + ROM_BASE, f"rom:0x{p:X}")

    def test_nothing_else_in_the_rom_names_the_new_ext_table(self):
        """A reader left behind on the old table would never see the gold op."""
        n = self.notes
        lo, hi = n["ext_table"] + ROM_BASE, n["ext_table"] + 4 * n["ext_words"] + ROM_BASE
        words = memoryview(bytes(self.rom[:len(self.rom) & ~3])).cast("I")
        names = [4 * i for i, w in enumerate(words) if lo <= w < hi]
        self.assertEqual(names, sorted(FB.EXT_POOLS), [hex(o) for o in names])

    def test_the_dispatch_has_no_bound_to_raise(self):
        """Op 2 and base ops 21 to 26 read `[table + 4n]` with no `cmp` on n at all, so a 147th word
        needs no code change. Disassembled here, which is the shape a byte scan would miss."""
        for at in (0x8F8E, 0x9130, 0x9160, 0x9190, 0x91BC, 0x91EC, 0x9224):
            texts = []
            for _a, t in _listing(self.rom, at, 0x1C):    # the index path ends at the first call
                texts.append(t)
                if t.startswith("bl "):
                    break
            self.assertTrue(any(t.startswith("ldrb") for t in texts),
                            f"rom:0x{at:X} does not read the op byte: {texts}")
            self.assertTrue(any(t.startswith("ldr ") and "," in t and "[" in t for t in texts),
                            f"rom:0x{at:X} does not index the table: {texts}")
            self.assertEqual([t for t in texts if t.startswith("cmp")], [],
                             f"rom:0x{at:X} compares the op number: {texts}")

    # ----- 4. the scene -----

    def test_the_chain_runs_in_order_and_ends_at_the_vanilla_ending(self):
        n, d2 = self.notes, self.notes["death_table"]
        for index, at in n["records"].items():
            self.assertEqual(_u32(self.rom, d2 + 4 * index), at + ROM_BASE, f"word {index}")
        order = list(FB.CHAIN)
        for a, b in zip(order, order[1:]):
            self.assertEqual(self.rom[n["records"][a]], b, f"word {a} hands on to {b}")
        self.assertEqual(self.rom[n["records"][order[-1]]], FB.END_TEXT_INDEX,
                         "the last record hands on to the vanilla The End.")
        for w in (24, 25):
            self.assertEqual(_u32(self.rom, d2 + 4 * w), _u32(self.without, d2 + 4 * w), f"word {w}")

    def test_word_0_was_ending_fights_record_k_and_is_now_the_finale(self):
        d2 = self.notes["death_table"]
        self.assertEqual(_u32(self.without, d2),
                         self.alloc_without.notes["ending_fight"]["death"] + ROM_BASE)
        self.assertEqual(_u32(self.rom, d2), self.notes["records"][FB.STAGE_INDEX] + ROM_BASE)

    def test_the_staging_is_a_vertical_pair_with_cell_above(self):
        """Both fighters are NPCs on the finale's own cloned sets, and the PLAYER steps off the
        parked view: a cloned set can never be given to him, because `ext 73` reverse looks the set
        id up in the appearance table and an id with no entry hangs the game (bible B0423)."""
        ops = _ops(self.rom, self.notes["records"][FB.STAGE_INDEX])
        self.assertIn((62, (FB.PLAYER,) + FB.HIDE_SPOT), ops, "the player steps off the view")
        self.assertIn((51, (FB.CELL_HOLD_ID,) + FB.FINALE_CELL_SPOT), ops)
        self.assertIn((55, (FB.CELL_HOLD_ID, FB.DOWN)), ops)
        self.assertIn((51, (FB.TRUNKS_HOLD_ID,) + FB.FINALE_TRUNKS_SPOT), ops)
        self.assertIn((55, (FB.TRUNKS_HOLD_ID, FB.UP)), ops)
        self.assertIn((52, (FB.CELL_SET,)), ops, "the beaten round 2 Cell goes")
        self.assertEqual(FB.FINALE_CELL_SPOT[0], FB.FINALE_TRUNKS_SPOT[0], "one column")
        self.assertLess(FB.FINALE_CELL_SPOT[1], FB.FINALE_TRUNKS_SPOT[1], "Cell is ABOVE")
        self.assertEqual(FB.FINALE_TRUNKS_SPOT[1] - FB.FINALE_CELL_SPOT[1], FB.GAP)
        self.assertIn((121, (FB.CELL_HOLD_ID, FB.KAMEHAME_STATE)), ops,
                      "ext 121, because state 30 never ends")
        self.assertNotIn((57, (FB.CELL_HOLD_ID, FB.KAMEHAME_STATE)), ops,
                         "ext 57 on state 30 would wait for ever (bible B0688)")
        self.assertEqual([op for op in ops if op[0] == 57], [],
                         "nothing in the staging blocks on a state")
        self.assertEqual([n for n, _ in ops][-2:], [31, 41],
                         "the camera parks last and then the screen comes back (bible B2170)")
        self.assertIn((31, FB.FINALE_VIEW), ops)
        self.assertGreater(FB.HIDE_SPOT[1] - plateau.TRUNKS_UP, FB.FINALE_VIEW[1] + plateau.VIEW[1],
                           "the player waits below the parked view")

    def test_the_beam_fires_up_and_its_forced_pose_is_the_pose_he_asked_for(self):
        """The beam flies along the actor's own facing and direction 1 is UP (bible FBM). `ext 137`
        leaves the shooter in state 30, which never ends, and on TRUNKS_HOLD_ID state 30 reads a row
        of seven copies of his hands-up frame. So the forced pose IS the held pose and nothing
        overrides it. wip3 took it back with `ext 121 (0, 4)`, which cycles the arms down, up, down,
        up over 64 frames: the "waving his hands around" the owner rejected."""
        ops = _ops(self.rom, self.notes["records"][FB.BLAST_INDEX])
        self.assertEqual(ops[0], (55, (FB.TRUNKS_HOLD_ID, FB.UP)))
        self.assertEqual(ops[1], (self.notes["gold_op"], (FB.TRUNKS_HOLD_ID, FB.BEAM_FRAMES)))
        self.assertEqual([op for op in ops if op[0] == 121], [],
                         "no state override follows the beam op")
        self.assertEqual([op for op in ops
                          if op[1][:1] == (FB.PLAYER,) and op[0] != FB.CAMERA_OP], [],
                         "no ACTOR op names the player: he is off the view and drives nothing."
                         " ext 134's first argument is vanilla's own 0 and is not a set")

    def test_the_death_loop_is_vanillas_with_three_hit_blocks_and_the_explosion(self):
        """Perfect Cell's own record 0x083EBE1C, with set 28 for set 30 and the fourth hit loop
        dropped, which is the owner's ruling: "lets do 3 loops isntead of 4 for future cell".

        ONE op is added: block 1 takes the `ext 57 (28, 2)` that vanilla's blocks 2 and 3 carry,
        because no 32 iteration loop runs in front of it to leave Cell in the hurt pose. His words
        are "EACH loop with the smoke effect explosion", so every loop has to show the hit anim."""
        ops = _ops(self.rom, self.notes["records"][FB.BLAST_INDEX])
        blocks, current = [], None
        for n, args in ops:
            if n == 63:
                current = []
            elif n == 64:
                blocks.append(current)
                current = None
            elif current is not None:
                current.append((n, args))
        self.assertEqual(len(blocks), len(FB.HIT_BLOCKS) + 1, "three hit blocks and the explosion")
        for block, (camera, want) in zip(blocks, FB.HIT_BLOCKS + (FB.BOOM_BLOCK,)):
            self.assertEqual(block[0], (FB.CAMERA_OP, FB.CAMERA_ARGS + (camera,)))
            self.assertEqual(block[1:], [(n, (FB.CELL_HOLD_ID,) + tuple(a)) for n, *a in want])
        self.assertEqual(blocks[-1][-1], (52, (FB.CELL_HOLD_ID,)),
                         "the explosion block removes Cell")
        self.assertEqual([c for c, _ in FB.HIT_BLOCKS] + [FB.BOOM_BLOCK[0]], [30, 30, 40, 80],
                         "vanilla's own camera values, in vanilla's own order")
        for k, block in enumerate(blocks[:-1]):
            self.assertIn((57, (FB.CELL_HOLD_ID, FB.HURT_STATE)), block,
                          f"hit loop {k + 1} does not show the hit anim")

    def test_the_beam_is_gone_before_the_player_is_rebuilt(self):
        """`ext 73` rebuilds the player object, and the beam object holds the actor. Counted on the
        ops' own frame values, which is arithmetic and not a guess."""
        ops = _ops(self.rom, self.notes["records"][FB.BLAST_INDEX])
        frames, seen = 0, False
        for n, args in ops:
            if n == 73:
                seen = True
                break
            if n in (69, 42, 43):
                frames += args[0]
        self.assertTrue(seen, "the record powers him down")
        self.assertGreaterEqual(frames, FB.BEAM_FRAMES, f"{frames} scripted frames before ext 73")
        self.assertEqual(frames, FB.POWER_DOWN_MARGIN + FB.WHITE)

    def test_he_powers_down_to_the_base_body_before_his_last_line(self):
        """The NPC swap under the white flash is vanilla's own shape: the ending tail removes Super
        Saiyan Trunks and spawns base Trunks in the same place."""
        blast = _ops(self.rom, self.notes["records"][FB.BLAST_INDEX])
        self.assertIn((73, (FB.TRUNKS_PARTY, FB.BASE_TRUNKS)), blast)
        self.assertIn((52, (FB.TRUNKS_HOLD_ID,)), blast)
        self.assertIn((51, (FB.BASE_TRUNKS,) + FB.FINALE_TRUNKS_SPOT), blast)
        self.assertLess(blast.index((52, (FB.TRUNKS_HOLD_ID,))),
                        blast.index((51, (FB.BASE_TRUNKS,) + FB.FINALE_TRUNKS_SPOT)))
        at = self.notes["records"][FB.WORDS_INDEX]
        self.assertEqual(self.rom[at + 2], S.TYPE_TEXT)
        self.assertEqual(self.rom[at + 3], FB.TRUNKS_BASE_PORTRAIT, "base portrait, base body")

    def test_the_tail_is_the_endings_own_and_it_keeps_track_15(self):
        """The owner: "back to the credits music that normally plays". This ending plays 15 at
        rom:0x3B80DD the moment Cell dies, and ext 45 puts the OBJ palette back before The End."""
        ops = _ops(self.rom, self.notes["records"][FB.CREDITS_INDEX])
        self.assertIn((49, (15,)), ops)
        self.assertNotIn((49, (37,)), ops, "37 is Perfect Cell's cue, not this ending's")
        self.assertEqual(ops[-1][0], 45, "ext 45 is last, or The End. draws black on black")
        self.assertLess([n for n, _ in ops].index(40), [n for n, _ in ops].index(45),
                        "the fade out still comes before ext 45")
        self.assertEqual(ops[-2], (52, (FB.BASE_TRUNKS,)),
                         "ext 45 lights every sprite, so base Trunks goes first (vanilla's own op)")

    # ----- 5. the owner's words -----

    def test_every_line_is_his_character_for_character(self):
        want = {FB.KAMEHAME_INDEX: (FB.CELL_PORTRAIT, FB.KAMEHAME_LINE),
                FB.SHOUT_INDEX: (FB.TRUNKS_SSJ_PORTRAIT, FB.SHOUT_LINE),
                FB.WORDS_INDEX: (FB.TRUNKS_BASE_PORTRAIT, FB.LAST_LINE)}
        for index, (portrait, line) in want.items():
            at = self.notes["records"][index]
            self.assertEqual(self.rom[at + 2], S.TYPE_TEXT)
            self.assertEqual(self.rom[at + 3], portrait)
            end = bytes(self.rom).index(0, at + 4)
            self.assertEqual(bytes(self.rom[at + 4:end]).decode("ascii"), line)
        self.assertEqual(FB.SHOUT_LINE.count("!"), 1,
                         "his section 5 line has ONE bang; the early copy rom:0x3B7FF6 has five")
        self.assertEqual(FB.LAST_LINE.replace(FB.BOX, " "),
                         "Now I can finally say that it's really over. Thanks to you, father, and to"
                         " you, Gohan. And especially to you, Goku.",
                         "a box break only ever replaces a space he wrote at a full stop")
        self.assertEqual(FB.KAMEHAME_LINE.split(FB.BOX), ["Kame..", "hame.."],
                         'his section 7 ruling: "It should be a tense Kame.. hame.."')

    def test_every_box_fits_the_page(self):
        for line in (FB.KAMEHAME_LINE, FB.SHOUT_LINE, FB.LAST_LINE):
            for box in line.split(FB.BOX):
                rows = _dialog_wrap(self.rom, box.encode("ascii"))
                self.assertLessEqual(len(rows), BOX_LINES, box)
                self.assertLessEqual(sum(w for _, w in rows), WIDEST_VANILLA_BOX, box)

    # ----- 6. the owner's map -----

    def test_both_spots_stand_on_open_reachable_art_free_ground(self):
        """His map 142, measured with plateau's own readers. Nothing here authors a cell of it."""
        doc = plateau.document()
        open_set = plateau.open_cells(doc)
        art = plateau.art_cells(doc)
        reach = plateau.reachable(open_set, (plateau.PLATEAU_CELL_SPOT[0] // 8,
                                             plateau.PLATEAU_CELL_SPOT[1] // 8))
        for spot, env, who in FB.FINALE_SPOTS:
            for c in plateau.envelope_cells(spot, env):
                self.assertIn(c, open_set, f"{who} {spot} cell {c}")
                self.assertIn(c, reach, f"{who} {spot} cell {c}")
                self.assertNotIn(c, art, f"{who} {spot} cell {c} is under BG0 or BG1 art")

    def test_the_beam_column_carries_no_art_that_would_draw_over_it(self):
        doc = plateau.document()
        art = plateau.art_cells(doc)
        half = FB.BEAM_WIDTH // 2
        column = [(cx, cy)
                  for cy in range(FB.FINALE_VIEW[1] // 8, FB.FINALE_TRUNKS_SPOT[1] // 8 + 1)
                  for cx in range((FB.FINALE_TRUNKS_SPOT[0] - half) // 8,
                                  (FB.FINALE_TRUNKS_SPOT[0] + half) // 8 + 1)]
        self.assertEqual(len(column), self.notes["design"]["beam_column_cells"])
        self.assertEqual([c for c in column if c in art], [])

    def test_the_parked_view_holds_both_fighters_whole(self):
        """Bible B0246: set 28 reaches 56 px above its point and the Trunks sets 24. A view is
        240 x 160 from its TOP LEFT, so the pair has to fit inside it or a frame is cut."""
        view = FB.FINALE_VIEW
        for spot, env, who in FB.FINALE_SPOTS:
            self.assertGreaterEqual(spot[1] - env[2], view[1], f"{who} head")
            self.assertLessEqual(spot[1] + env[3], view[1] + plateau.VIEW[1], f"{who} feet")
            self.assertGreaterEqual(spot[0] - env[0], view[0], f"{who} left")
            self.assertLessEqual(spot[0] + env[1], view[0] + plateau.VIEW[0], f"{who} right")

    # ----- 7. the module refuses to run out of order -----

    def test_it_refuses_without_the_modules_it_reads(self):
        for missing in ("ending_fight", "plateau"):
            alloc = Allocator(len(self.without), [(0xF00000, 0x100000)])
            alloc.notes.update({k: v for k, v in self.alloc_without.notes.items() if k != missing})
            with self.assertRaises(ValueError):
                FB.apply(bytearray(self.without), alloc)

    def test_a_second_run_raises(self):
        rom = bytearray(self.rom)
        with self.assertRaises(ValueError):
            FB.apply(rom, self.alloc)


if __name__ == "__main__":
    unittest.main()
