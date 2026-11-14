r"""
test_ki_ramp.py - Tests for patches.ki_ramp (trial 2026-11-13): the ki bar ramps up over the green
                  bar while the transformation plays, and goes away when it is interrupted.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_ki_ramp.py -v
Builds the Piccolo trial list in memory once and keeps the ROM before the module as "before", and the
Vegeta trial list apart, because that one has no Piccolo pool to land on. Expected values are restated
from the handlers and from the Buu's Fury listings, never imported from the patch module.
"""
import struct
import unittest

import log2_build
import log_paths
from rom.webfoot_decompress import ROM_BASE
from tests.test_bf_ki_pool import Cpu2

# ===== constants (handlers read 2026-11-13) =====
PICCOLO_LIST = log_paths.BUILD_LISTS / "build_list_trial_piccolo_fx.txt"
VEGETA_LIST = log_paths.BUILD_LISTS / "build_list_trial_vegeta_fx.txt"
HUD_VTABLE, HUD_SLOT = 0x0802408C, 0x10
XFORM_VTABLE, NAMEK_VTABLE, TICK_SLOT = 0x08025D9C, 0x08025CE0, 0x04
XFORM_LIMIT, NAMEK_LIMIT = 0xA0, 0x40      # powerup_tick @0x08011D4A ends at 0xA0; @0x0801560E at 0x40
VANILLA_NAMEK_TICK = 0x0801560F
STEPS, LIVE = 0x31, 0x5A02                 # 49 EP steps; the watchdog stamp
RAM, RAMP = 0x03003A00, 0x03003A14
STRUCT, SAVE_PTR = 0x03000E90, 0x086F7E50
DIV, EP_TABLE, VRAM_OBJ = 0x08021F30, 0x083B5658, 0x06010000
RET, STACK = 0x0EEE0000, 0x03007E00
ACTOR, STATE, HUD, OAM = 0x02010000, 0x02010400, 0x02011000, 0x02011100
HUD_TILE = 0x200
PICCOLO_BASE, NAMEK, ZPLUS = 6, 7, 24      # entry 6 is not a super form, 7 and 24 are
SAIYAN_BASE, SUPER_SAIYAN, SSJ2 = 2, 5, 22    # Gohan's chain: base, Super Saiyan, Super Saiyan 2
YELLOW, ORANGE, NO_POOL = 0, 1, 2          # bar_colour's three answers
TABLE_LITERAL = 0x1954

_CACHE = {}


def built(path=PICCOLO_LIST) -> dict:
    key = str(path)
    if key not in _CACHE:
        from patches import ki_ramp
        modules = log2_build.read_build_list(path)
        rom, alloc = log2_build.assemble(log2_build.BASE, [m for m in modules if m != "ki_ramp"])
        before = bytes(rom)
        ki_ramp.apply(rom, alloc)
        _CACHE[key] = dict(before=before, rom=bytes(rom), notes=alloc.notes["ki_ramp"], all=alloc.notes)
    return _CACHE[key]


def _u32(rom, off):
    return struct.unpack_from("<I", rom, off)[0]


def vtable_target(rom, vtable, slot):
    return (vtable + _u32(rom, vtable - ROM_BASE + slot)) & 0xFFFFFFFF


def record(rom, index):
    return STRUCT + 0xC + 28 * index


def cpu(rom, entry=NAMEK, tick=0, leader=0):
    """A CPU with the leader record, the actor and the stack the two transform ticks see."""
    cp = Cpu2(rom)
    cp.store(STRUCT, 1, leader)
    r = record(rom, leader)
    cp.store(r + 2, 2, 906)
    cp.store(r + 6, 2, 134)
    cp.store(r + 8, 1, entry)
    cp.store(ACTOR + 0x12, 2, tick)
    cp.r[13], cp.r[14] = STACK, RET | 1
    cp.r[0], cp.r[1] = STATE, ACTOR
    cp.calls = []
    return cp


class KiRampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b = built()
        cls.before, cls.rom, cls.notes = b["before"], b["rom"], b["notes"]
        cls.labels = {k: v + ROM_BASE for k, v in cls.notes["labels"].items()}

    # ===== the hooks =====

    def test_all_three_hooks_chain_what_was_there(self):
        """Every hook is read live and chained, so powerup_fx's own chain onto state 35 survives and
        fullpower_hud still draws the row underneath."""
        for vtable, slot, label, chain in (
                (XFORM_VTABLE, TICK_SLOT, "tick35", "chain35"),
                (NAMEK_VTABLE, TICK_SLOT, "tick25", "chain25"),
                (HUD_VTABLE, HUD_SLOT, "hud_ramp", "chain_hud")):
            self.assertEqual(vtable_target(self.rom, vtable, slot), self.labels[label] | 1)
            self.assertEqual(self.notes[chain], vtable_target(self.before, vtable, slot))
        pool = {_u32(self.rom, o) for o in range(self.notes["code"], self.notes["code"] + self.notes["code_len"], 4)}
        for chain in ("chain35", "chain25", "chain_hud"):
            self.assertIn(self.notes[chain], pool)

    def test_the_vegeta_trial_leaves_the_namek_state_alone(self):
        """Without piccolo_z_start there is no Namek transform to reach, so only state 35 is hooked
        in that build."""
        v = built(VEGETA_LIST)
        self.assertEqual(vtable_target(v["rom"], NAMEK_VTABLE, TICK_SLOT), VANILLA_NAMEK_TICK)
        self.assertIsNone(v["notes"]["chain25"])
        self.assertNotIn("state25", v["notes"]["hooks"])

    def test_no_base_rom_byte_changed_outside_the_three_hook_words(self):
        allowed = set(self.notes["hooks"].values())
        stray = [i for i in range(log2_build.BASE_SIZE)
                 if self.rom[i] != self.before[i] and not any(a <= i < a + 4 for a in allowed)]
        self.assertEqual(stray, [], f"{len(stray)} base ROM bytes changed outside the hook words")

    def test_a_second_run_raises(self):
        from patches import ki_ramp
        rom, alloc = log2_build.assemble(log2_build.BASE, log2_build.read_build_list(PICCOLO_LIST))
        with self.assertRaises(ValueError):
            ki_ramp.apply(rom, alloc)

    # ===== the schedule =====

    def _tick(self, label, limit, entry, tick, land_as=None):
        """Run one transform tick and return the CPU. `land_as` is the entry the chained tick writes,
        which is what the landing does from inside it."""
        cp = cpu(self.rom, entry=entry, tick=tick)
        chain = self.notes["chain35"] if label == "tick35" else self.notes["chain25"]

        def chained(c):
            c.calls.append((c.r[0], c.r[1]))
            c.store(ACTOR + 0x12, 2, min(tick + 1, limit))
            if land_as is not None:
                c.store(record(self.rom, 0) + 8, 1, land_as)
            return 0

        stops = {RET: "done", DIV: lambda c: c.r[1] // c.r[0], chain & ~1: chained}
        self.assertEqual(cp.run(self.labels[label] & ~1, stops, limit=600), "done")
        return cp

    def test_the_ramp_is_linear_over_the_whole_animation(self):
        """Buu's Fury's transform tick BF 0x0801C4F4 computes max ki x actor +0x12 / (count << 4)
        every tick, with no steps. Ours is 49 x tick / limit on the drawn overlay."""
        for tick in (0, 1, 0x20, 0x50, 0x7F, 0x9F):
            cp = self._tick("tick35", XFORM_LIMIT, NAMEK, tick)
            self.assertEqual(cp.load(RAMP + 2, 1), STEPS * (tick + 1) // XFORM_LIMIT, f"tick {tick}")
            cp = self._tick("tick35", XFORM_LIMIT, SAIYAN_BASE, tick)
            self.assertEqual(cp.load(RAMP + 2, 1), STEPS * (tick + 1) // XFORM_LIMIT, f"saiyan {tick}")

    def test_the_last_tick_is_a_full_bar(self):
        self.assertEqual(self._tick("tick35", XFORM_LIMIT, NAMEK, XFORM_LIMIT - 1).load(RAMP + 2, 1), STEPS)

    def test_the_bar_colour_is_what_pool_ref_will_paint_on_the_form_he_enters(self):
        """transform(player, 1) writes the entry at +4 of the entry he is leaving (bible B0539), so
        that entry's form object is the word pool_ref will read. Super Namek to Z+ is the case that
        moved: the Buu's Fury rule, bit 0 of the entry he is LEAVING, said orange, and pool_ref
        paints the Z+ bar yellow."""
        table = _u32(self.rom, TABLE_LITERAL) - ROM_BASE
        self.assertEqual(self.rom[table + 20 * NAMEK] & 1, 1)       # the old rule would say orange
        self.assertEqual(self.rom[table + 20 * NAMEK + 4], ZPLUS)
        self.assertEqual(self._tick("tick35", XFORM_LIMIT, NAMEK, 8).load(RAMP + 3, 1), YELLOW)
        self.assertEqual(self.rom[table + 20 * SAIYAN_BASE + 4], SUPER_SAIYAN)
        self.assertEqual(self._tick("tick35", XFORM_LIMIT, SAIYAN_BASE, 8).load(RAMP + 3, 1), YELLOW)
        self.assertEqual(self.rom[table + 20 * SUPER_SAIYAN + 4], SSJ2)
        self.assertEqual(self._tick("tick35", XFORM_LIMIT, SUPER_SAIYAN, 8).load(RAMP + 3, 1), ORANGE)

    def test_the_colour_is_latched_before_the_chained_tick_runs(self):
        """The landing writes the new entry from inside the chained tick (bible B2418). Reading the
        entry after it would read the colour of the form he already reached."""
        cp = self._tick("tick35", XFORM_LIMIT, SUPER_SAIYAN, XFORM_LIMIT - 1, land_as=SSJ2)
        self.assertEqual(cp.load(RAMP + 3, 1), ORANGE)

    def _colour(self, leaving):
        """bar_colour's own answer for a leader LEAVING appearance entry `leaving`."""
        cp = cpu(self.rom, entry=leaving)
        cp.r[0] = leaving
        self.assertEqual(cp.run(self.labels["bar_colour"] & ~1, {RET: "done"}, limit=600), "done")
        return cp.r[0]

    def _pool_ref(self, entry, leader=1):
        """YELLOW, ORANGE or NO_POOL from one LIVE pool_ref call on a leader wearing `entry`."""
        cp = cpu(self.rom, entry=entry, leader=leader)
        cp.store(RAM + 0xE, 1, 0xEE)
        at = built()["all"]["bf_ki_pool"]["labels"]["pool_ref"]
        self.assertEqual(cp.run(at & ~1, {RET: "done"}, limit=4000), "done")
        return cp.load(RAM + 0xE, 1) if cp.r[0] else NO_POOL

    def test_bar_colour_agrees_with_pool_ref_on_every_entry_in_the_table(self):
        """The whole point of the change: the ramp and the bar read one word, the form object of
        the entry at +4. Leader 1 runs the pool_ref side, because the r28 full-power stretch is the
        one gate bar_colour does not mirror and it reaches leaders 0 and 4 only."""
        table = _u32(self.rom, TABLE_LITERAL) - ROM_BASE
        seen = set()
        for leaving in range(self.notes["zplus_entry"] + 1):
            want = self._pool_ref(self.rom[table + 20 * leaving + 4])
            self.assertEqual(self._colour(leaving), want, f"leaving entry {leaving}")
            seen.add(want)
        self.assertEqual(sorted(seen), [YELLOW, ORANGE, NO_POOL], f"only {sorted(seen)} appeared")

    def test_a_form_with_no_pool_never_ramps(self):
        """Piccolo's base to Super Namek step. The owner keeps that bar plain green, so pool_ref
        gives entry 7 no pool and a ramp there would fill a bar and then vanish."""
        table = _u32(self.rom, TABLE_LITERAL) - ROM_BASE
        self.assertEqual(self.rom[table + 20 * PICCOLO_BASE + 4], NAMEK)
        for tick in (0, 0x10, 0x3F):
            cp = self._tick("tick25", NAMEK_LIMIT, PICCOLO_BASE, tick)
            self.assertEqual(cp.load(RAMP, 2), 0, f"namek tick {tick} stamped the watchdog")

    def test_a_stale_stamp_is_cleared_by_a_tick_that_has_no_pool_to_land_on(self):
        cp = cpu(self.rom, entry=PICCOLO_BASE, tick=4)
        cp.store(RAMP, 2, LIVE)
        cp.store(RAMP + 2, 1, 20)
        chain = self.notes["chain25"]
        stops = {RET: "done", DIV: lambda c: c.r[1] // c.r[0], chain & ~1: lambda c: 0}
        self.assertEqual(cp.run(self.labels["tick25"] & ~1, stops, limit=600), "done")
        self.assertEqual(cp.load(RAMP, 2), 0)

    def test_the_chained_tick_gets_the_state_and_the_actor_unchanged(self):
        cp = self._tick("tick35", XFORM_LIMIT, NAMEK, 4)
        self.assertEqual(cp.calls, [(STATE, ACTOR)])

    # ===== the watchdog =====

    def test_a_tick_stamps_the_watchdog_and_a_landing_clears_it(self):
        self.assertEqual(self._tick("tick35", XFORM_LIMIT, NAMEK, 4).load(RAMP, 2), LIVE)
        landed = self._tick("tick35", XFORM_LIMIT, NAMEK, XFORM_LIMIT - 1, land_as=ZPLUS)
        self.assertEqual(landed.load(RAMP, 2), 0)

    # ===== the draw =====

    def _draw(self, cp, pool_steps=0):
        """Run one HUD draw and return [(buffer offset, the bar colour put_px would read)]."""
        painted = []
        put = self.all_notes_put_px

        def chained(c):
            c.store(RAM + 0xC, 1, pool_steps)     # hud_key leaves the steps it painted here
            return OAM

        def put_px(c):
            painted.append((c.r[1], c.load(RAM + 0xE, 1)))
            return c.r[0]            # put_px keeps r0, and the loop needs it

        cp.store(HUD + 0xC, 2, HUD_TILE)
        cp.r[0], cp.r[1] = HUD, OAM
        cp.r[13], cp.r[14] = STACK, RET | 1
        stops = {RET: "done", self.notes["chain_hud"] & ~1: chained, put & ~1: put_px}
        self.assertEqual(cp.run(self.labels["hud_ramp"] & ~1, stops, limit=4000), "done")
        return painted

    @property
    def all_notes_put_px(self):
        return built()["all"]["bf_ki_pool"]["labels"]["put_px"]

    def test_the_draw_paints_three_pixels_a_step_in_the_latched_colour(self):
        """The overlay goes ON TOP of the live draw, so the green row and, on a second
        transformation, the yellow pool bar are underneath it."""
        cp = cpu(self.rom)
        cp.store(RAM + 0xE, 1, 0)
        cp.store(RAMP, 2, LIVE)
        cp.store(RAMP + 2, 1, 7)
        cp.store(RAMP + 3, 1, 1)
        painted = self._draw(cp)
        self.assertEqual(len(painted), 21)
        want = [(_u32(self.rom, EP_TABLE - ROM_BASE + 16 * s + w), 1) for s in range(7) for w in (0, 4, 8)]
        self.assertEqual(painted, want)

    def test_the_draw_puts_the_bar_colour_byte_back(self):
        """fullpower_hud enters bf_ki_pool's draw without calling pool_ref, so a colour left behind
        here paints the full-power yellow row orange."""
        for seeded in (0, 1):
            cp = cpu(self.rom)
            cp.store(RAM + 0xE, 1, seeded)
            cp.store(RAMP, 2, LIVE)
            cp.store(RAMP + 2, 1, 5)
            cp.store(RAMP + 3, 1, 1 - seeded)
            self.assertEqual({c for _, c in self._draw(cp)}, {1 - seeded})
            self.assertEqual(cp.load(RAM + 0xE, 1), seeded)

    # ===== Piccolo's own Z+ bar =====

    def test_a_landed_form_is_never_repainted_by_this_module(self):
        """The ramp is the only thing this module draws. pool_ref now paints every landed bar in
        its own colour, so the orange repaint of the Z+ bar is gone with the mismatch it covered."""
        for entry in (PICCOLO_BASE, NAMEK, ZPLUS):
            cp = cpu(self.rom, entry=entry)
            cp.store(RAM + 0xE, 1, 0)
            cp.store(RAMP, 2, 0)
            self.assertEqual(self._draw(cp, pool_steps=9), [], f"entry {entry} was repainted")
            self.assertEqual(cp.load(RAM + 0xE, 1), 0)

    # ===== the whole chain, with nothing stubbed out between us and OBJ VRAM =====

    def _real_draw(self, entry, draws=2, leader=1):
        """One HUD frame with the LIVE chain: this module's draw, then fullpower_hud's, then
        bf_ki_pool's, then its own put_px into OBJ VRAM. Only the vanilla draw and the ARM divide
        are stopped, because neither can run here. Returns the CPU after `draws` frames.

        Every other draw test stubs the chained draw, so none of them can see what colour the bar
        ENDS as. That is the gap the owner's eye found: a module that paints nothing in the landed
        form passes them all and still leaves his Z+ bar the wrong colour.
        """
        cp = cpu(self.rom, entry=entry, leader=leader)
        r = record(self.rom, leader)
        cp.store(r + 4, 2, 134)                      # EP, and +6 max EP: a full pool is 49 steps
        cp.store(RAM, 2, 134)
        cp.store(RAM + 2, 2, 0x8000 | leader << 8 | entry)
        cp.store(RAMP, 2, 0)                         # no ramp live: the landed form, which is the case
        cp.store(HUD + 0xC, 2, HUD_TILE)
        cp.store(HUD + 0x15, 1, 0)
        stops = {RET: "done", 0x08008BEE: lambda c: OAM, DIV: lambda c: c.r[1] // c.r[0]}
        for _ in range(draws):
            cp.r[0], cp.r[1] = HUD, OAM
            cp.r[13], cp.r[14] = STACK, RET | 1
            self.assertEqual(cp.run(self.labels["hud_ramp"] & ~1, stops, limit=200000), "done")
        return cp

    def test_the_landed_zplus_bar_is_the_yellow_image_in_vram(self):
        """End to end, and the owner's own words: the Z+ bar ramps yellow and STAYS yellow. Read
        back from OBJ VRAM, where the screen reads it, not from the calls the draw makes."""
        pool = built()["all"]["bf_ki_pool"]
        yellow, orange = pool["yellow"], pool["orange"]
        base = VRAM_OBJ + HUD_TILE * 32
        cp = self._real_draw(ZPLUS)
        differ = wrong = 0
        for step in range(STEPS):
            for word in (0, 4, 8):
                off = _u32(self.rom, EP_TABLE - ROM_BASE + 16 * step + word)
                got = cp.load(base + off, 1)
                self.assertEqual(got, self.rom[yellow + off],
                                 f"step {step} pixel {off:#x} is not the yellow image")
                if self.rom[orange + off] != self.rom[yellow + off]:
                    differ += 1
                    wrong += got == self.rom[orange + off]
        self.assertGreater(differ, 0, "the two images are the same here, so this proves nothing")
        self.assertEqual(wrong, 0)

    def test_super_namek_writes_no_pool_pixel_at_all(self):
        """The control, and the whole point of the decision: entry 7 carries the same form object
        as entry 24 and still draws no bar, because pool_ref tests the ENTRY."""
        base = VRAM_OBJ + HUD_TILE * 32
        offs = [_u32(self.rom, EP_TABLE - ROM_BASE + 16 * s + w)
                for s in range(STEPS) for w in (0, 4, 8)]
        cp = self._real_draw(NAMEK)
        self.assertEqual([o for o in offs if cp.load(base + o, 1)], [], "Super Namek drew a bar")
        zp = self._real_draw(ZPLUS)
        painted = [o for o in offs if zp.load(base + o, 1)]
        self.assertGreater(len(painted), 0, "Z+ drew nothing either, so this proves nothing")

    def test_the_whole_chain_puts_the_bar_colour_byte_back(self):
        """fullpower_hud enters bf_ki_pool's draw without calling pool_ref, so a colour left behind
        paints Gohan's full-power row orange. pool_ref writes 0 for Piccolo's form object."""
        self.assertEqual(self._real_draw(ZPLUS).load(RAM + 0xE, 1), 0)

    def test_the_vegeta_trial_knows_of_no_zplus_entry(self):
        """Without piccolo_zplus there is no entry 24, so the symbol is an entry nothing holds."""
        self.assertIsNone(built(VEGETA_LIST)["notes"]["zplus_entry"])

    def test_the_draw_paints_nothing_without_a_live_stamp(self):
        cp = cpu(self.rom)
        cp.store(RAMP, 2, 0)
        cp.store(RAMP + 2, 1, 30)
        self.assertEqual(self._draw(cp), [])

    def test_the_bar_goes_away_within_two_draws_when_the_tick_stops(self):
        """An interrupted transformation stops ticking, and Buu's Fury zeroes the ramped pool at
        BF 0x0801C552. The watchdog does the same without a leave word to hook."""
        cp = cpu(self.rom)
        cp.store(RAMP, 2, LIVE)
        cp.store(RAMP + 2, 1, 12)
        self.assertEqual(len(self._draw(cp)), 36)
        self.assertEqual(len(self._draw(cp)), 36)
        self.assertEqual(self._draw(cp), [])

    def test_a_changed_ramp_forces_the_vanilla_repaint(self):
        """Without the key the green row is not redrawn, and a shorter ramp leaves its old pixels."""
        cp = cpu(self.rom)
        cp.store(RAMP, 2, LIVE)
        cp.store(RAMP + 2, 1, 9)
        cp.store(RAMP + 4, 1, 9)
        cp.store(HUD + 0x15, 1, 4)
        self._draw(cp)
        self.assertEqual(cp.load(HUD + 0x15, 1), 4, "nothing changed, so no repaint is forced")
        cp.store(RAMP + 2, 1, 10)
        self._draw(cp)
        self.assertEqual(cp.load(HUD + 0x15, 1), 0xFF)

    def test_uninitialised_iwram_does_not_draw_a_bar(self):
        """The crt0 fill stops at 0x0300391C (bible B1632), so the stamp is a magic value."""
        cp = cpu(self.rom)
        for junk in (0, 0xFFFF, 0x0002, 0x5A00, 0xA55A):
            cp.store(RAMP, 2, junk)
            cp.store(RAMP + 2, 1, 40)
            self.assertEqual(self._draw(cp), [], f"stamp {junk:#06x} drew a bar")


if __name__ == "__main__":
    unittest.main()
