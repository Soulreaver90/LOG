r"""
test_bf_ki_pool.py - Interpreter tests of the ki pool code (patches.bf_ki_pool, r39) on the r39 build in memory.

Run (from the LOG root):
  py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_bf_ki_pool.py -v
Ported from scripts\one-time\2026-10-24-hud-ki\proto\test_proto_b.py (classes PoolRef, Ticks, FillEmpty, Swap, Hud, State46) with
the same inputs and expected values; only the ROM (r39 instead of the v2b mockup) and the label source (the
bf_ki_pool notes) change. Layout, equivalence and file tests are in test_bf_hud.py.
Method:  test_ssj2.Cpu, extended with mul, asr, OBJ VRAM and a log of byte stores to VRAM, runs the new code.
         Vanilla code runs for real where the interpreter can (the base form tick, stretch_on, ability tests and
         actions 0 and 2, state 46 +8); the rest (sound, transform, the vanilla HUD draw, the ARM divide, other
         state methods, the state 46 release calls) are stubs at their addresses. The tests do not run the frame
         loop, the scene manager, sound or DMA timing.
"""
import unittest

from tests.test_bf_hud import HOOKS, built, labels, u32
from tests.test_ssj2 import M32, REGNO, Cpu
from rom.thumb_dis import listing

# ===== constants (proto\test_proto_b.py) =====
ROM_BASE = 0x08000000
RET, STACK = 0x0EEE0000, 0x03007E00
SET_STATE, IN_STATE = 0x0EEE2000, 0x0EEE3000
PLAYER, PLAYER_VT, HUD, OAM = 0x02010000, 0x02010400, 0x02011000, 0x02011100
STRUCT, RAM = 0x03000E90, 0x03003A00
BASE_TICK, DIV, HUD_VANILLA = 0x08017028, 0x08021F30, 0x08008BEE
TRANSFORM_END, REVERT_END = 0x0801563C, 0x080157AE
TABLE = 0x0888DC54 - ROM_BASE
EP_TABLE = 0x083B5658
HUD_TILE = 0x200
ST46_OBJ, MOVE_OBJ = 0x0300219C, 0x02012000
INPUT_RELEASED = 0x0300229C + 0x16
ST46_TICK, ST46_FIRE, ST46_RAND, ST46_SOUND = 0x08015078, 0x08014160, 0x0802141C, 0x0801FC9C
VEGETA, VEGETA_BASE = 2, 8
REGS = [0x44444444, 0x55555555, 0x66666666, 0x77777777]


def rom() -> bytes:
    return built()["rom"]


class Cpu2(Cpu):
    """test_ssj2.Cpu plus mul, asr, OBJ VRAM (0x06) and IO (0x04); VRAM byte stores are logged, not dropped."""

    def __init__(self, data: bytes):
        super().__init__(data)
        self.ram[0x06], self.ram[0x04] = bytearray(0x18000), bytearray(0x400)
        self.vram_bytes = []

    def store(self, a, size, v):
        if a >> 24 == 0x06 and size == 1:
            self.vram_bytes.append(a)
        super().store(a, size, v)

    def _step(self, nxt, text):
        op, _, rest = text.partition(" ")
        a = rest.split(",")
        if op == "mul":
            d = REGNO[a[0]]
            self.r[d] = self._nz(self.r[d] * self.r[REGNO[a[1]]])
            return nxt
        if op == "asr":
            d, x, k = REGNO[a[0]], self.r[REGNO[a[1]]], int(a[2][1:], 0)
            sx = x - (1 << 32) if x >> 31 else x
            self.r[d] = self._nz((sx >> k) & M32)
            return nxt
        return super()._step(nxt, text)


def rec(i: int) -> int:
    return STRUCT + 0xC + 28 * i


def form_obj(entry: int) -> int:
    return u32(rom(), TABLE + 20 * entry + 0x10)


def cpu(leader: int = 0, entry: int = 5, hp: int = 900, ep: int = 120, mep: int = 134, pool=None, tag=None,
        f149: bool = False, f195: bool = False, depth: int = 0, scene: int = 0, cooldown: int = 0,
        in_revert: int = 0, data: bytes = None) -> Cpu2:
    cp = Cpu2(rom() if data is None else data)
    cp.store(STRUCT, 1, leader)
    cp.store(STRUCT + 8, 4, cooldown)
    for i in range(6):
        cp.store(rec(i), 2, 500)
        cp.store(rec(i) + 2, 2, 1000)
        cp.store(rec(i) + 4, 2, 50)
        cp.store(rec(i) + 6, 2, 100)
    r = rec(leader)
    cp.store(r, 2, hp)
    cp.store(r + 2, 2, 906)
    cp.store(r + 4, 2, ep)
    cp.store(r + 6, 2, mep)
    cp.store(r + 8, 1, entry)
    cp.store(STRUCT + 0xB4 + 149 // 8, 1, 0x20 if f149 else 0)
    cp.store(STRUCT + 0xB4 + 195 // 8, 1, 0x08 if f195 else 0)
    cp.store(0x03001FD8 + 4, 4, scene)
    cp.store(0x03000E1C + 8, 4, depth)
    if pool is not None:
        cp.store(RAM, 2, pool)
        cp.store(RAM + 2, 2, 0x8000 | leader << 8 | entry if tag is None else tag)
    cp.store(PLAYER, 4, PLAYER_VT)
    cp.store(PLAYER_VT + 0x28, 4, ((SET_STATE | 1) - PLAYER_VT) & M32)
    cp.store(PLAYER_VT + 0x2C, 4, ((IN_STATE | 1) - PLAYER_VT) & M32)
    cp.r[13], cp.r[14] = STACK, RET | 1
    cp.r[4:8] = list(REGS)
    cp.in_revert, cp.states = in_revert, []
    return cp


def set_state(cp):
    cp.states.append((cp.r[0], cp.r[1]))
    return 0


def in_state(cp):
    return cp.in_revert


def div(cp):
    return (cp.r[1] // cp.r[0]) if cp.r[0] else 0


STOPS = {RET: "ret", SET_STATE: set_state, IN_STATE: in_state, DIV: div}


def pool(cp) -> tuple:
    return cp.load(RAM, 2), cp.load(RAM + 2, 2), cp.load(RAM + 8, 4)


class PoolRef(unittest.TestCase):
    def run_ref(self, cp):
        out = cp.run(labels()["pool_ref"], STOPS)
        self.assertEqual((out, cp.r[13], cp.r[4:8]), ("ret", STACK, REGS))
        return cp.r[0], cp.r[1]

    def test_pool_forms(self):
        self.assertEqual((form_obj(5), form_obj(22), form_obj(20), form_obj(17)),
                         (0x030021EC, 0x0888DE20, 0x030021EC, 0x030021EC))
        for leader, entry, want in ((0, 5, RAM), (0, 22, RAM), (4, 20, RAM), (3, 17, RAM), (0, 2, 0), (0, 4, 0),
                                    (1, 7, 0), (2, 10, 0)):
            cp = cpu(leader=leader, entry=entry)
            self.assertEqual(self.run_ref(cp), (want, rec(leader)), (leader, entry))

    def test_stale_tag_fills_to_max_ep(self):
        cp = cpu(entry=5, ep=40, mep=134, pool=7, tag=0x8002)
        cp.store(RAM + 8, 4, 0x1234)
        cp.store(RAM + 0xD, 1, 1)
        self.run_ref(cp)
        self.assertEqual(pool(cp), (134, 0x8005, 0))
        self.assertEqual((cp.load(RAM + 0xD, 1), cp.load(rec(0) + 4, 2)), (0, 40))   # regular EP untouched

    def test_matching_tag_keeps_the_pool(self):
        cp = cpu(entry=22, pool=33)
        cp.store(RAM + 8, 4, 0x8000)
        self.run_ref(cp)
        self.assertEqual(pool(cp), (33, 0x8016, 0x8000))

    def test_full_power_stretch_is_not_a_pool_form(self):
        for leader, entry, want in ((0, 5, 0), (4, 20, 0), (3, 17, RAM)):
            cp = cpu(leader=leader, entry=entry, f149=True)
            self.assertEqual(self.run_ref(cp)[0], want, leader)
        cp = cpu(leader=0, entry=5, f149=True, f195=True)
        self.assertEqual(self.run_ref(cp)[0], RAM)
        cp = cpu(leader=0, entry=22, f149=True)
        self.assertEqual(self.run_ref(cp)[0], RAM)                   # Super Saiyan 2 has no stretch rule


class Ticks(unittest.TestCase):
    def tick(self, cp, which="tick_ssj"):
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = 0x030021EC, PLAYER, STACK, RET | 1
        out = cp.run(labels()[which], STOPS, limit=2000)
        self.assertEqual((out, cp.r[13], cp.r[4:8]), ("ret", STACK, REGS))

    def test_rate_one_every_20_frames(self):
        cp = cpu(pool=50)
        cp.store(RAM + 8, 4, 0)
        for n in range(1, 41):
            self.tick(cp)
            self.assertEqual(cp.load(RAM, 2), 50 - n // 20, n)
        self.assertEqual(cp.load(rec(0) + 4, 2), 120)                # regular EP not drained
        cp = cpu(entry=22, pool=50)
        cp.store(RAM + 8, 4, 0)
        for n in range(1, 21):
            self.tick(cp, "tick_ssj2")
        self.assertEqual(cp.load(RAM, 2), 48)

    def test_regular_ep_regenerates_and_cooldown_is_kept(self):
        cp = cpu(pool=50, ep=60, mep=134, cooldown=0x300)
        cp.store(PLAYER + 0x184, 4, 0x10000 - 0x6E)                  # the base tick overflows this frame
        self.tick(cp)
        self.assertEqual(cp.load(rec(0) + 4, 2), 60 + (134 * 0x7AE >> 16))   # +3 % of max EP
        self.assertEqual(cp.load(rec(1) + 4, 2), 50 + (100 * 0xCCD >> 16))   # others +5 %
        self.assertEqual(cp.load(STRUCT + 8, 4), 0x300)
        self.assertEqual(cp.load(PLAYER + 0x184, 4), 0)

    def test_revert_at_pool_0(self):
        cp = cpu(pool=0)
        cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
        self.tick(cp)
        self.assertEqual(cp.states, [(PLAYER, 0x24)])
        self.assertEqual(pool(cp)[2], 0)
        cp = cpu(pool=1)
        cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
        self.tick(cp)
        self.assertEqual((cp.states, cp.load(RAM, 2)), ([], 0))     # BF order: the revert is one overflow later
        cp = cpu(pool=0, hp=0)
        cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
        self.tick(cp)
        self.assertEqual(cp.states, [])

    def test_gates(self):
        for kw in (dict(scene=1, depth=1), dict(in_revert=1), dict(f149=True)):
            cp = cpu(pool=0, **kw)
            cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
            self.tick(cp)
            self.assertEqual((cp.states, cp.load(RAM, 2)), ([], 0), kw)
            self.assertEqual(cp.load(RAM + 8, 4), 0x10000 - 0xCCD, kw)
        cp = cpu(pool=9, scene=1, depth=0)                          # flag without depth: no pause
        cp.store(RAM + 8, 4, 0x10000 - 0xCCD)
        self.tick(cp)
        self.assertEqual(cp.load(RAM, 2), 8)


class FillEmpty(unittest.TestCase):
    def end(self, cp, label, new_entry):
        def vanilla(cc):
            cc.store(rec(cc.load(STRUCT, 1)) + 8, 1, new_entry)
            return 0
        cp.r[0], cp.r[1] = 0x03002184, PLAYER
        stops = {**STOPS, TRANSFORM_END: vanilla, REVERT_END: vanilla}
        self.assertEqual(cp.run(labels()[label], stops), "ret")
        self.assertEqual((cp.r[13], cp.r[4:8]), (STACK, REGS))

    def test_transform_fills_to_max_ep(self):
        cp = cpu(entry=2, ep=30, mep=134)
        self.end(cp, "fill_end", 5)
        self.assertEqual(pool(cp), (134, 0x8005, 0))
        self.assertEqual(cp.load(rec(0) + 4, 2), 30)

    def test_step_to_ssj2_refills(self):
        cp = cpu(entry=5, pool=12, mep=134)
        self.end(cp, "fill_end", 22)
        self.assertEqual(pool(cp)[:2], (134, 0x8016))

    def test_same_entry_again_refills(self):
        cp = cpu(entry=2, pool=3, tag=0x8005)                     # an old tag for entry 5 must not survive
        self.end(cp, "fill_end", 5)
        self.assertEqual(cp.load(RAM, 2), 134)

    def test_revert_empties(self):
        cp = cpu(entry=5, pool=40)
        self.end(cp, "empty_end", 2)
        self.assertEqual(pool(cp)[:2], (0, 0))


class Swap(unittest.TestCase):
    def run_ab(self, cp, n, kind, r0=None):
        cp.r[0], cp.r[1] = rec(0) if r0 is None else r0, PLAYER
        cp.r[13], cp.r[14] = STACK, RET | 1
        out = cp.run(labels()[f"ab{n}{kind}"], STOPS, limit=600)
        self.assertEqual((out, cp.r[13]), ("ret", STACK))
        self.assertEqual(cp.r[4:8], REGS)
        return cp.r[0]

    def test_ki_move_spends_the_pool(self):
        cp = cpu(entry=5, ep=7, pool=30)
        cp.store(0x03002080 + 0xC, 4, 1)                          # combat map word
        self.assertEqual(self.run_ab(cp, 0, "t"), 1)              # pool 30 >= 20 although EP is 7
        self.run_ab(cp, 0, "a")
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(0) + 4, 2)), (20, 7))
        self.assertEqual(cp.states, [(PLAYER, 0x2E)])
        self.assertEqual(cp.load(RAM + 0xD, 1), 0)

    def test_pool_too_low_dims_the_move(self):
        cp = cpu(entry=5, ep=120, pool=5)
        cp.store(0x03002080 + 0xC, 4, 1)
        self.assertEqual(self.run_ab(cp, 0, "t"), 0)
        self.assertEqual(self.run_ab(cp, 2, "t"), 1)

    def test_real_hud_icon_hook_follows_the_pool(self):
        """The r36 HUD icon hook 0x0888E356 calls the ability test through the table: bright or dim by the pool."""
        icons = (u32(rom(), 0x081D9900), u32(rom(), 0x081D9904))
        for pool_v, ep, entry, want in ((5, 120, 5, icons[1]), (25, 3, 5, icons[0]), (25, 3, 2, icons[1])):
            cp = cpu(entry=entry, ep=ep, pool=pool_v, tag=0x8005)
            cp.store(0x03002080 + 0xC, 4, 1)
            cp.store(rec(0) + 9, 1, 0)                            # selected slot 0
            cp.store(rec(0) + 0x18, 1, 0)                         # slot 0 = ability 0 (test: EP >= 20)
            cp.r[0], cp.r[13], cp.r[14] = rec(0), STACK, RET | 1
            self.assertEqual(cp.run(0x0888E356, STOPS, limit=800), "ret")
            self.assertEqual(cp.r[0], want, (pool_v, ep, entry))
            self.assertEqual((cp.load(RAM, 2), cp.load(rec(0) + 4, 2)), (pool_v, ep))

    def test_base_form_spends_regular_ep(self):
        cp = cpu(entry=2, ep=50, pool=30, tag=0x8005)
        cp.store(0x03002080 + 0xC, 4, 1)
        self.run_ab(cp, 2, "a")
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(0) + 4, 2)), (30, 48))

    def test_other_record_is_not_swapped(self):
        cp = cpu(entry=5, ep=50, pool=30)
        self.run_ab(cp, 2, "a", r0=rec(1))
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(1) + 4, 2)), (30, 48))

    def test_state_spend_and_guard(self):
        def beam(cc):
            r = rec(cc.load(STRUCT, 1)) + 4
            cc.store(r, 2, cc.load(r, 2) - 3)
            return 0x99
        for guard, want in ((0, (27, 120)), (1, (30, 117))):
            cp = cpu(entry=5, ep=120, pool=30)
            cp.store(RAM + 0xD, 1, guard)
            cp.r[0], cp.r[1] = 0x030021C0, PLAYER
            out = cp.run(labels()["st48"], {**STOPS, 0x08015248: beam})
            self.assertEqual((out, cp.r[0], cp.r[13]), ("ret", 0x99, STACK))
            self.assertEqual((cp.load(RAM, 2), cp.load(rec(0) + 4, 2)), want, guard)
            self.assertEqual(cp.load(RAM + 0xD, 1), guard)

    def test_not_swapped_keeps_args_and_lr(self):
        seen = {}

        def beam(cc):
            seen["regs"] = (cc.r[0], cc.r[1], cc.r[14], cc.r[13], cc.r[4], cc.r[5])
            return 0
        cp = cpu(entry=2)
        cp.r[0], cp.r[1] = 0x030021CC, PLAYER
        self.assertEqual(cp.run(labels()["st49"], {**STOPS, 0x0801539A: beam}), "ret")
        self.assertEqual(seen["regs"], (0x030021CC, PLAYER, RET | 1, STACK, 0x44444444, 0x55555555))


class Hud(unittest.TestCase):
    def draw(self, cp):
        seen = {}

        def vanilla(cc):
            seen["args"] = (cc.r[0], cc.r[1])
            base = 0x06010000 + 32 * HUD_TILE
            for o in range(0, 0x500, 2):
                cc.store(base + o, 2, 0x0101)                    # vanilla repaint: index 1 everywhere
            return 0
        cp.store(HUD + 0xC, 2, HUD_TILE)
        cp.store(HUD + 0x15, 1, 3)
        cp.r[0], cp.r[1] = HUD, OAM
        out = cp.run(labels()["hud_draw"], {**STOPS, HUD_VANILLA: vanilla}, limit=6000)
        self.assertEqual((out, cp.r[0], cp.r[13]), ("ret", 0, STACK))
        self.assertEqual(cp.r[4:8], REGS)
        self.assertEqual(seen["args"], (HUD, OAM))
        return bytes(cp.ram[0x06][0x10000 + 32 * HUD_TILE:0x10000 + 32 * HUD_TILE + 0x500])

    def test_overlay_pixels(self):
        cp = cpu(entry=5, ep=10, mep=50, pool=25)
        buf = self.draw(cp)
        fill = 25 * 49 // 50
        at = built()["notes"]["bf_ki_pool"]["yellow"]
        img = rom()[at:at + 0x500]
        want = bytearray([1] * 0x500)
        for i in range(fill):
            for k in range(3):
                o = u32(rom(), EP_TABLE + 16 * i + 4 * k)
                want[o] = img[o]
        self.assertEqual(buf, bytes(want))
        self.assertEqual((cp.load(RAM + 0xC, 1), cp.load(HUD + 0x15, 1)), (fill, 0xFF))
        self.assertEqual(cp.vram_bytes, [])                       # halfword stores only

    def test_no_redraw_key_when_fill_is_unchanged(self):
        cp = cpu(entry=5, ep=10, mep=50, pool=25)
        cp.store(RAM + 0xC, 1, 24)
        self.draw(cp)
        self.assertEqual(cp.load(HUD + 0x15, 1), 3)

    def test_base_form_draws_vanilla(self):
        cp = cpu(entry=2, pool=25, tag=0x8005)
        cp.store(RAM + 0xC, 1, 24)                                # leaving the form: one forced repaint
        buf = self.draw(cp)
        self.assertEqual((buf, cp.load(RAM + 0xC, 1), cp.load(HUD + 0x15, 1)), (b"\x01" * 0x500, 0, 0xFF))
        cp = cpu(entry=2)
        cp.store(RAM + 0xC, 1, 0)
        self.draw(cp)
        self.assertEqual(cp.load(HUD + 0x15, 1), 3)

    def test_full_pool_paints_all_49_steps(self):
        cp = cpu(entry=22, mep=134, pool=134)
        buf = self.draw(cp)
        self.assertEqual(cp.load(RAM + 0xC, 1), 49)
        for i in range(49):
            o = u32(rom(), EP_TABLE + 16 * i)
            self.assertNotEqual(buf[o], 1, i)


# ===== v2b: state 46 (ability 0, Vegeta hold) =====

def vegeta(entry: int = 11, ep: int = 120, pool_v=30, tag=None, released: int = 0, scene_bits: int = 0,
           count: int = 0, data: bytes = None) -> Cpu2:
    """Vegeta leads in `entry`; state 46 object +4 names a fake move object (+0x48 = 0x1234); actor +0x12 = count."""
    cp = cpu(leader=VEGETA, entry=entry, ep=ep, mep=138, pool=pool_v, tag=tag, data=data)
    cp.store(ST46_OBJ + 4, 4, MOVE_OBJ)
    cp.store(MOVE_OBJ + 0x48, 4, 0x1234)
    cp.store(PLAYER + 0x10, 1, 3)                                 # facing
    cp.store(PLAYER + 0x12, 2, count)
    cp.store(INPUT_RELEASED, 2, released)
    cp.store(0x03000E1C + 4, 4, scene_bits)
    return cp


def fire_stub(cc):
    cc.fired = getattr(cc, "fired", 0) + 1
    return 0


ST46_STOPS = {**STOPS, ST46_FIRE: fire_stub, ST46_RAND: lambda cc: 0, ST46_SOUND: lambda cc: 0}


def hold(cp, label="st46") -> None:
    """One call of state 46 +8 through `label` (st46 = the stub, or an address = the method itself)."""
    cp.r[0], cp.r[1], cp.r[13], cp.r[14] = ST46_OBJ, PLAYER, STACK, RET | 1
    start = labels()[label] if isinstance(label, str) else label
    out = cp.run(start, ST46_STOPS, limit=800)
    assert (out, cp.r[13], cp.r[4:8]) == ("ret", STACK, REGS), (out, hex(cp.r[13]))


class State46(unittest.TestCase):
    def test_vtable_word_names_the_stub(self):
        vt, slot, target, _ = HOOKS["hold46"]
        before = built()["before"]
        self.assertEqual((vt + u32(before, vt + slot)) & M32, 0x08015079)          # r38: the vanilla tick
        self.assertEqual((vt + u32(rom(), vt + slot)) & M32, labels()["st46"] | 1)
        text = [t for _, t in listing(rom(), labels()["st46"], 2)]
        self.assertEqual(text, ["ldr r3,=0x08015079", f"b {labels()['swap_state']:#x}"])
        for k in (0, 4, 0xC, 0x10, 0x14):                                           # other state 46 words stay
            self.assertEqual(u32(rom(), vt + k), u32(before, vt + k), k)

    def test_stub_shape_equals_the_v2_state_stubs(self):
        for name in ("st48", "st49", "st51"):
            text = [t for _, t in listing(rom(), labels()[name], 2)]
            self.assertEqual((text[0][:9], text[1]), ("ldr r3,=0", f"b {labels()['swap_state']:#x}"), name)

    def test_vegeta_transform_target_is_a_pool_form(self):
        self.assertEqual(built()["before"][TABLE + 20 * VEGETA_BASE + 4], 11)       # appearance +4 = transform target
        self.assertEqual(form_obj(11), 0x030021EC)
        cp = cpu(leader=VEGETA, entry=11)
        self.assertEqual(cp.run(labels()["pool_ref"], STOPS), "ret")
        self.assertEqual((cp.r[0], cp.r[1]), (RAM, rec(VEGETA)))
        cp = cpu(leader=VEGETA, entry=11, f149=True)                                # no stretch rule for Vegeta
        cp.run(labels()["pool_ref"], STOPS)
        self.assertEqual(cp.r[0], RAM)

    def test_hold_spends_the_pool_not_the_regular_ep(self):
        cp = vegeta(pool_v=30)
        for n in range(1, 6):
            hold(cp)
            self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), (30 - n, 120), n)
        self.assertEqual((cp.load(RAM + 0xD, 1), cp.load(MOVE_OBJ + 0x48, 4)), (0, 0x1234))

    def test_pool_reaching_0_stops_the_move(self):
        cp = vegeta(pool_v=1)
        hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2), cp.load(MOVE_OBJ + 0x48, 4)), (0, 120, 0))
        cp = vegeta(pool_v=0)
        hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2), cp.load(MOVE_OBJ + 0x48, 4)), (0, 120, 0))

    def test_base_form_hold_spends_regular_ep(self):
        cp = vegeta(entry=VEGETA_BASE, pool_v=30, tag=0x820B)
        hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), (30, 119))

    def test_guard_held_spends_regular_ep(self):
        cp = vegeta(pool_v=30)
        cp.store(RAM + 0xD, 1, 1)
        hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2), cp.load(RAM + 0xD, 1)), (30, 119, 1))

    def test_scene_pause_spends_nothing(self):
        cp = vegeta(pool_v=30, scene_bits=1)
        hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), (30, 120))

    def test_release_fires_and_spends_nothing(self):
        cp = vegeta(pool_v=30, released=0x2)                                        # B released this frame
        hold(cp)
        self.assertEqual((getattr(cp, "fired", 0), cp.load(PLAYER + 0x12, 2), cp.load(ST46_OBJ + 4, 4)), (1, 1, 0))
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2), cp.load(RAM + 0xD, 1)), (30, 120, 0))

    def test_after_release_count_ends_in_state_0(self):
        cp = vegeta(pool_v=30, count=0x1F)
        hold(cp)
        self.assertEqual((cp.states, cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), ([(PLAYER, 0)], 30, 120))

    def test_ability_0_then_hold_end_to_end(self):
        cp = vegeta(pool_v=30, ep=7)
        cp.store(0x03002080 + 0xC, 4, 1)                                            # combat map word
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = rec(VEGETA), PLAYER, STACK, RET | 1
        self.assertEqual(cp.run(labels()["ab0t"], STOPS, limit=600), "ret")
        self.assertEqual(cp.r[0], 1)                                                # pool 30 >= 20, EP 7
        cp.r[0], cp.r[1], cp.r[13], cp.r[14] = rec(VEGETA), PLAYER, STACK, RET | 1
        self.assertEqual(cp.run(labels()["ab0a"], STOPS, limit=600), "ret")
        self.assertEqual(cp.states, [(PLAYER, 0x2E)])
        for _ in range(4):
            hold(cp)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), (16, 7))

    def test_without_the_hook_the_hold_spends_regular_ep(self):
        """A/B (proto test_v2_gap): before bf_ki_pool the word names the vanilla tick, which drops the regular EP."""
        vt, slot, _, _ = HOOKS["hold46"]
        hud = built()["hud"]
        self.assertEqual((vt + u32(hud, vt + slot)) & M32, 0x08015079)
        cp = vegeta(pool_v=30, data=hud)
        hold(cp, ST46_TICK)
        self.assertEqual((cp.load(RAM, 2), cp.load(rec(VEGETA) + 4, 2)), (30, 119))


if __name__ == "__main__":
    unittest.main()
