r"""
test_powerup_fx.py - Tests for patches.powerup_fx (trial 2026-11-12): the Buu's Fury power-up aura
                     as a spawned effect object, and the Buu's Fury ground dust in his own frames.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_powerup_fx.py -v
Builds the Vegeta trial list in memory once and keeps the ROM before the module as "before". Expected
values are restated from the handlers and from docs\tasks\2026-11-12-powerup-fx\brief.md, never
imported from the patch module.
"""
import struct
import unittest

import log2_build
from art.to_indexed import OBJ_PAL
import log_paths
from patches import powerup_fx
from patches.vegeta_zplus import POWER_UP, set_at, shared_list
from rom.webfoot_decompress import ROM_BASE
from tests.test_bf_ki_pool import Cpu2

# ===== constants (handlers read 2026-11-12, and the brief) =====
VEGETA_LIST = log_paths.BUILD_LISTS / "build_list_trial_vegeta_fx.txt"
PICCOLO_LIST = log_paths.BUILD_LISTS / "build_list_trial_piccolo_fx.txt"
XFORM_VTABLE, XFORM_SLOT = 0x08025D9C, 0x04
LEAVE_SLOT, VANILLA_LEAVE = 0x0C, 0x080155F7     # state vtable +0xC is the leave (bible B1842)
EFFECT_VTABLE = 0x080245C0                       # the word the ctor stores at object +0 (@0x08013610)
WORLD_REMOVE, WORLD_LIST = 0x080068CB, 0x086DB34C    # the pair the effect tick uses on itself @0x08013672
AURA_RAM, AURA_LIVE = 0x03003A1C, 0x5A03
RECORDS_LEFT = 0x34                              # effect object +0x34: records still to play (bible B2411)
RET, STACK = 0x0EEE0000, 0x03007E00
ACTOR, STATE, AURA_OBJ = 0x02010000, 0x02010400, 0x02010800
EFFECT_CTOR, WORLD_ADD, WORLD_PTR = 0x080135E1, 0x080068B9, 0x086DB354
SPAWN_AT, RECORDS, STEP, VRAM, LAYER = 0x20, 8, 0x1000, 0x400, 0x28
RECORD, GEOMETRY = 12, (8, 24, 32, 32, 0x2000, 0x8000)      # dx, dy, w, h, attr0, attr1
ORDER = (0, 1, 2, 0, 1, 2, 0, 1)
VEGETA_SET, PICCOLO_SET = 140, 104
GOLD = ((0xF8, 0xD0, 0x40), (0xF8, 0xF8, 0x00), (0xF8, 0xF8, 0x78), (0xF8, 0xF8, 0xF0))
DUST = (0xD8, 0xA8, 0x60)
STATE_FRAMES = 0xA0                                          # powerup_tick @0x08011D4A ends at 0xA0

_CACHE = {}


def built() -> dict:
    if _CACHE:
        return _CACHE
    modules = log2_build.read_build_list(VEGETA_LIST)
    # ki_ramp hooks the same state 35 word and runs after this module, so it is left out here too.
    rom, alloc = log2_build.assemble(log2_build.BASE, [m for m in modules if m not in ("powerup_fx", "ki_ramp")])
    before = bytes(rom)
    powerup_fx.apply(rom, alloc)
    _CACHE.update(before=before, rom=bytes(rom), notes=alloc.notes["powerup_fx"], all_notes=alloc.notes)
    return _CACHE


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def vtable_target(rom, vtable, slot):
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & 0xFFFFFFFF


class PowerUpFxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]

    # ===== the hook =====

    def test_the_state_35_tick_now_runs_the_new_code_and_still_chains_the_old_one(self):
        """The one hook. bf_ki_pool owned state 35 +4 before this module, and its tick must still run
        first, because it is what holds the Z charge meter full through the transformation."""
        was = vtable_target(self.before, XFORM_VTABLE, XFORM_SLOT)
        now = vtable_target(self.rom, XFORM_VTABLE, XFORM_SLOT)
        self.assertNotEqual(now, was)
        self.assertEqual(now & ~1, self.notes["labels"]["fx_tick"] + ROM_BASE)
        self.assertEqual(self.notes["chained"], was)

    def test_no_other_vtable_word_and_no_vanilla_code_byte_changed(self):
        """Pointer level only. Every byte that differs is one of the two hook words, the state 35
        tick and the state 35 leave, or it is past the base ROM."""
        allowed = (self.notes["hook"], self.notes["leave_hook"])
        stray = [i for i in range(log2_build.BASE_SIZE)
                 if self.rom[i] != self.before[i] and not any(a <= i < a + 4 for a in allowed)]
        self.assertEqual(stray, [], f"{len(stray)} base ROM bytes changed outside the two hook words")

    def test_a_second_run_raises(self):
        rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(VEGETA_LIST))
        with self.assertRaises(ValueError):
            powerup_fx.apply(rom, alloc)

    # ===== the aura records =====

    def test_the_record_list_is_eight_records_cycling_three_frames(self):
        """Eight records at 16 ticks each is 128 ticks, which is exactly what is left of the 0xA0
        frame state after the spawn at 0x20, so the object removes itself as the form lands."""
        self.assertEqual(RECORDS * (0x10000 // STEP), STATE_FRAMES - SPAWN_AT)
        at = self.notes["lists"]["gold"]
        pix = []
        for k in range(RECORDS):
            dx, dy, w, h, a0, a1 = struct.unpack_from("<bbBBHH", self.rom, at + RECORD * k)
            self.assertEqual((dx, dy, w, h, a0, a1), GEOMETRY)
            pix.append(_u32(self.rom, at + RECORD * k + 8))
        self.assertEqual([pix.index(p) for p in pix], list(ORDER))

    def test_the_aura_box_lands_exactly_on_his_own_frame_box(self):
        """The effect class draws at (pos - dx, pos - dy) and the actor draw at (anchor + dx, dy), so
        the aura's pair is his anim 9 pair negated. Any other pair puts the ring off him."""
        _, recs = shared_list(self.rom, VEGETA_SET, POWER_UP)
        his = {(r["dx"], r["dy"], r["w"], r["h"]) for r in recs}
        self.assertEqual(his, {(-8, -24, 32, 32)})
        dx, dy, w, h = struct.unpack_from("<bbBB", self.rom, self.notes["lists"]["gold"])
        self.assertEqual((dx, dy, w, h), (8, 24, 32, 32))

    def test_every_aura_pixel_names_a_colour_this_rom_really_holds(self):
        """The gold is drawn on four entries the palette already holds, so no shared index is
        repainted. A pixel on an index whose colour is not one of those four is a silent recolour."""
        pal = self.rom[OBJ_PAL:OBJ_PAL + 512]
        want = set()
        for rgb in GOLD:
            bgr = (rgb[0] >> 3) | (rgb[1] >> 3) << 5 | (rgb[2] >> 3) << 10
            want |= {i for i in range(256) if struct.unpack_from("<H", pal, 2 * i)[0] == bgr}
        seen = set()
        for k in range(3):
            at = _u32(self.rom, self.notes["lists"]["gold"] + RECORD * k + 8) - ROM_BASE
            seen |= set(self.rom[at:at + 32 * 32])
        self.assertTrue(seen - {0} <= want, f"aura indices {sorted(seen - {0} - want)} are off the gold ramp")

    def test_the_palette_is_untouched(self):
        """Taking the three missing Buu's Fury golds would repaint shared indices. Nothing is taken."""
        self.assertEqual(self.rom[OBJ_PAL:OBJ_PAL + 512], self.before[OBJ_PAL:OBJ_PAL + 512])

    # ===== the gate =====

    def test_the_spawn_is_gated_on_the_sets_that_hold_his_drawn_frames(self):
        """Without the gate every power-up in the game would grow a gold aura."""
        self.assertEqual(self.notes["sets"]["gold"], set_at(self.rom, VEGETA_SET) + ROM_BASE)
        self.assertEqual(self.notes["sets"]["white"], 0xFFFFFFFF)   # no Piccolo module in this list
        self.assertEqual(self.notes["lists"]["white"], 0)

    def test_the_code_names_the_ctor_the_world_and_nothing_else_new(self):
        """Every address the spawn needs is a literal in its own pool, because a Thumb BL cannot
        reach the expansion area."""
        at, n = self.notes["code"], self.notes["code_len"]
        pool = {_u32(self.rom, o) for o in range(at, at + n, 4)}
        for want in (EFFECT_CTOR, WORLD_ADD, WORLD_PTR, STEP, VRAM, self.notes["chained"]):
            self.assertIn(want, pool, f"0x{want:08X} is not in the code's literal pool")

    # ===== the interruption: the aura must leave with the state =====

    def _leave(self, stamp=AURA_LIVE, obj=AURA_OBJ, vtable=EFFECT_VTABLE, records=3):
        """Run the state 35 leave over one aura object and return (the CPU, the world_remove calls)."""
        cp = Cpu2(self.rom)
        cp.store(AURA_RAM, 4, obj)
        cp.store(AURA_RAM + 4, 4, stamp)
        if obj:
            cp.store(obj, 4, vtable)
            cp.store(obj + RECORDS_LEFT, 4, records)
        cp.r[0], cp.r[1] = STATE, ACTOR
        cp.r[13], cp.r[14] = STACK, RET | 1
        taken = []
        stops = {RET: "done",
                 VANILLA_LEAVE & ~1: lambda c: taken.append(("vanilla", c.r[0], c.r[1])) or 0,
                 WORLD_REMOVE & ~1: lambda c: taken.append(("remove", c.r[0], c.r[1])) or 0}
        self.assertEqual(cp.run((self.notes["labels"]["fx_leave"] + ROM_BASE) & ~1, stops, limit=600), "done")
        return cp, taken

    def test_the_state_35_leave_runs_the_new_code_and_still_chains_the_vanilla_one(self):
        """Buu's Fury takes its aura back in the +0xC slot of the transform vtable (BF 0x0801C552),
        and LoG II carries the leave in the same slot. The vanilla leave stops the power-up sound,
        so it must still run."""
        was = vtable_target(self.before, XFORM_VTABLE, LEAVE_SLOT)
        self.assertEqual(was, VANILLA_LEAVE)
        self.assertEqual(vtable_target(self.rom, XFORM_VTABLE, LEAVE_SLOT) & ~1,
                         self.notes["labels"]["fx_leave"] + ROM_BASE)
        self.assertEqual(self.notes["chained_leave"], was)

    def test_the_spawn_leaves_the_aura_where_the_leave_can_find_it(self):
        """Nothing else knows the object: the ctor hands it back once and the world keeps no name
        this module can read."""
        cp = Cpu2(self.rom)
        cp.store(ACTOR + 0x12, 2, SPAWN_AT)
        cp.store(ACTOR + 0x48, 4, self.notes["sets"]["gold"])
        cp.store(ACTOR + 4, 4, 0x180)
        cp.store(AURA_RAM, 4, 0)
        cp.store(AURA_RAM + 4, 4, 0)
        cp.r[0], cp.r[1] = STATE, ACTOR
        cp.r[13], cp.r[14] = STACK, RET | 1
        stops = {RET: "done", self.notes["chained"] & ~1: lambda c: 0,
                 EFFECT_CTOR & ~1: lambda c: AURA_OBJ, WORLD_ADD & ~1: lambda c: 0}
        self.assertEqual(cp.run((self.notes["labels"]["fx_tick"] + ROM_BASE) & ~1, stops, limit=900), "done")
        self.assertEqual(cp.load(AURA_RAM, 4), AURA_OBJ)
        self.assertEqual(cp.load(AURA_RAM + 4, 4), AURA_LIVE)

    def test_an_interrupted_transform_takes_the_aura_out_of_the_world(self):
        """The defect: the aura ran its own 128 ticks and nothing took it back, so a hit mid
        transform cleared the ki bar and left the aura spinning."""
        cp, taken = self._leave()
        self.assertIn(("remove", 0x03001120, AURA_OBJ), taken,
                      "the aura was not removed from the world the effect tick itself uses")
        self.assertEqual([k for k, *_ in taken], ["remove", "vanilla"], "the vanilla leave must still run last")
        self.assertEqual(cp.load(AURA_RAM, 4), 0)
        self.assertEqual(cp.load(AURA_RAM + 4, 4), 0)

    def test_a_landing_leaves_the_object_alone_because_it_removed_itself(self):
        """Eight records at 16 ticks end exactly on the landing frame, where the effect tick calls
        world_remove on itself. Removing it a second time could reach another object's block."""
        cp, taken = self._leave(records=0)
        self.assertEqual([k for k, *_ in taken], ["vanilla"])
        self.assertEqual(cp.load(AURA_RAM, 4), 0, "the word is cleared on every leave, landing or not")

    def test_uninitialised_iwram_removes_nothing(self):
        """The crt0 fill stops at 0x0300391C (bible B1632), so the stamp is a magic value."""
        for junk in (0, 0xFFFFFFFF, 0x5A02, 0x00005A00, 0xA55A5A03):
            cp, taken = self._leave(stamp=junk)
            self.assertEqual([k for k, *_ in taken], ["vanilla"], f"stamp {junk:#010x} removed an object")

    def test_a_block_that_is_no_longer_an_effect_is_left_alone(self):
        """A removed object's heap block can be handed to something else, and that something else
        must not be taken out of the world."""
        for obj, vtable in ((AURA_OBJ, EFFECT_VTABLE - 4), (AURA_OBJ, 0), (0, EFFECT_VTABLE)):
            cp, taken = self._leave(obj=obj, vtable=vtable)
            self.assertEqual([k for k, *_ in taken], ["vanilla"], f"object {obj:#x} vtable {vtable:#x}")

    def test_the_leave_hands_the_vanilla_one_the_state_and_the_actor_unchanged(self):
        cp, taken = self._leave()
        self.assertIn(("vanilla", STATE, ACTOR), taken)

    def test_both_trial_lists_carry_the_leave(self):
        """Vegeta's gold aura and Piccolo's white one are the same object on the same state."""
        for path in (VEGETA_LIST, PICCOLO_LIST):
            rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(path))
            note = alloc.notes["powerup_fx"]
            self.assertEqual(note["chained_leave"], VANILLA_LEAVE, f"{path.name}")
            self.assertEqual(vtable_target(bytes(rom), XFORM_VTABLE, LEAVE_SLOT) & ~1,
                             note["labels"]["fx_leave"] + ROM_BASE, f"{path.name}")

    # ===== the dust =====

    def test_the_dust_is_in_frames_two_three_and_four_and_not_in_frame_one(self):
        """Buu's Fury keeps the ground still until he powers up, and the owner approved that on the
        sheet. Frames 3 and 4 are the pair the game alternates, so they carry the two shapes."""
        pal = self.rom[OBJ_PAL:OBJ_PAL + 512]
        bgr = (DUST[0] >> 3) | (DUST[1] >> 3) << 5 | (DUST[2] >> 3) << 10
        tan = min(i for i in range(1, 256) if i != 168 and struct.unpack_from("<H", pal, 2 * i)[0] == bgr)
        frames = [(self.before[at:at + 32 * 32], self.rom[at:at + 32 * 32])
                  for at in self.notes["dust"]["vegeta_zplus"]]
        added = [[i for i in range(32 * 32) if was[i] != now[i]] for was, now in frames]
        self.assertEqual(added[0], [], "frame 1 must keep the still ground")
        for k, moved in enumerate(added[1:], 2):
            self.assertTrue(moved, f"frame {k} carries no dust")
            self.assertTrue(all(frames[k - 1][1][i] == tan for i in moved),
                            f"frame {k} gained a colour that is not his tan")
        self.assertNotEqual(added[2], added[3], "frames 3 and 4 must carry different dust shapes")

    def test_the_dust_never_lands_on_him(self):
        """It may take clear canvas or his own black shadow and nothing else, which is the rule the
        approved sheet used."""
        pal = self.rom[OBJ_PAL:OBJ_PAL + 512]
        black = min(i for i in range(1, 256) if struct.unpack_from("<H", pal, 2 * i)[0] == 0)
        for at in self.notes["dust"]["vegeta_zplus"]:
            was, now = self.before[at:at + 32 * 32], self.rom[at:at + 32 * 32]
            moved = [i for i in range(32 * 32) if was[i] != now[i]]
            off = [i for i in moved if was[i] not in (0, black)]
            self.assertEqual(off, [], f"{len(off)} pixels of his drawing were painted over at rom:0x{at:X}")
