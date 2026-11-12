r"""
test_pool_refill.py - Tests for patches.pool_refill (trial 2026-11-09): a scripted form change (ext 73) gives
                      the leader a FULL Super Saiyan ki pool.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_pool_refill.py -v
Builds build_list_trial_plateau.txt in memory twice: "before" is the list up to pool_refill, "rom" is before
plus pool_refill only. The wrapper is decoded with thumb_dis (never with the encoder) and run with
tests.test_bf_ki_pool.Cpu2, which executes thumb_dis text. bf_ki_pool's pool_ref runs for real; the vanilla
ext 73 handler is a stub at its own address, and the stub is what writes the new appearance entry.
Expected values are restated from the base ROM and the owner's defect report, never imported from the patch.
"""
import copy
import struct
import unittest

import log2_build
from rom.thumb_dis import listing
from tests.test_bf_ki_pool import Cpu2

# ===== constants (base ROM reads and bible rows B0418, B0423, B0243) =====
ROM_BASE = 0x08000000
TRIAL_LIST = log2_build.ROOT / "scripts" / "permanent" / "build_list_trial_plateau.txt"
EXT73 = 73
VANILLA_EXT73 = 0x0800A8ED                        # the handler, Thumb; its even address is the stub key
EXT_POOLS = (0x921C, 0x92DC)                      # every ROM word naming the ext op table
STRUCT, RAM = 0x03000E90, 0x03003A00
SAVE_PTR_WORD, SAVE = 0x6F7E54, 0x03000E90
RET, STACK = 0x0EEE0000, 0x03007E00
RESULT = 0x12345678                               # what the stubbed handler hands back
TRUNKS, BASE_ENTRY, SSJ_ENTRY = 3, 15, 16         # his party id and his two appearance entries
STALE_TAG = 0x8000 | TRUNKS << 8 | SSJ_ENTRY      # the tag the android fights leave behind
DRAINED, MAX_EP = 5, 120
WRAPPER_LINES = 28                                # code lines before the literal pool

_CACHE = {}


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def built() -> dict:
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        i = names.index("pool_refill")
        rom, alloc = log2_build.assemble(log2_build.BASE, names[:i])
        _CACHE.update(before=bytes(rom), alloc_before=copy.deepcopy(alloc))
        log2_build.apply_patches(rom, alloc, ["pool_refill"])
        _CACHE.update(rom=bytes(rom), notes=alloc.notes["pool_refill"],
                      pool_ref=alloc.notes["bf_ki_pool"]["labels"]["pool_ref"],
                      table=alloc.notes["ssj2_form"]["table"])
    return _CACHE


def hook_offset(data: bytes) -> int:
    """The file offset of the live ext 73 table word, found the way the VM finds the table."""
    return u32(data, EXT_POOLS[0]) - ROM_BASE + 4 * EXT73


def rec(i: int) -> int:
    return STRUCT + 0xC + 28 * i


def seeded(data: bytes, entry: int, pool: int = DRAINED, tag: int = STALE_TAG) -> Cpu2:
    """Trunks leads, every record carries MAX_EP, and the pool holds a drained value under a stale tag."""
    cp = Cpu2(data)
    cp.store(STRUCT, 1, TRUNKS)
    for i in range(6):
        cp.store(rec(i), 2, 900)
        cp.store(rec(i) + 4, 2, 50)
        cp.store(rec(i) + 6, 2, MAX_EP)
        cp.store(rec(i) + 8, 1, BASE_ENTRY)
    cp.store(rec(TRUNKS) + 8, 1, entry)
    cp.store(STRUCT + 0xB4 + 149 // 8, 1, 0)            # flag 149 clear: no full-power stretch
    cp.store(STRUCT + 0xB4 + 195 // 8, 1, 0)
    cp.store(RAM, 2, pool)
    cp.store(RAM + 2, 2, tag)
    cp.store(RAM + 8, 4, 0)
    cp.r[13], cp.r[14] = STACK, RET | 1
    return cp


def writes(who: int, new_entry: int):
    """A stub for the vanilla ext 73: it writes one character's appearance entry, as `@0x080042BC` does."""
    def stub(cp):
        cp.store(rec(who) + 8, 1, new_entry)
        return RESULT
    return stub


def run_op(data: bytes, cp: Cpu2, stub) -> Cpu2:
    """Run whatever the live ext 73 word names, then pool_ref, the way the next HUD draw would."""
    stops = {RET: "ret", VANILLA_EXT73 & ~1: stub}
    target = u32(data, hook_offset(data))
    cp.run(target, stops)
    cp.result = cp.r[0] & 0xFFFFFFFF
    cp.r[13], cp.r[14] = STACK, RET | 1
    cp.run(built()["pool_ref"], stops)
    return cp


def state(cp: Cpu2) -> tuple:
    return cp.load(RAM, 2), cp.load(RAM + 2, 2)


# ===== tests =====

class Sources(unittest.TestCase):

    def test_the_live_ext_73_word_was_the_vanilla_handler(self):
        self.assertEqual(u32(built()["before"], hook_offset(built()["before"])), VANILLA_EXT73)

    def test_the_handler_body_is_vanilla(self):
        base = log2_build.BASE.read_bytes()
        self.assertEqual(built()["rom"][0xA8EC:0xA8FC], base[0xA8EC:0xA8FC])

    def test_the_save_pointer_word_is_the_save_struct(self):
        self.assertEqual(u32(built()["rom"], SAVE_PTR_WORD), SAVE)

    def test_trunks_two_entries_are_a_pool_form_and_not(self):
        """Entry 15 is set 132 and entry 16 is set 133; only 16 carries the Super Saiyan form object."""
        table = built()["table"]
        self.assertEqual(built()["rom"][table + 20 * BASE_ENTRY + 1], 132)
        self.assertEqual(built()["rom"][table + 20 * SSJ_ENTRY + 1], 133)
        self.assertNotEqual(u32(built()["rom"], table + 20 * BASE_ENTRY + 0x10), 0x030021EC)
        self.assertEqual(u32(built()["rom"], table + 20 * SSJ_ENTRY + 0x10), 0x030021EC)

    def test_a_second_run_raises(self):
        from patches import pool_refill
        rom, alloc = bytearray(built()["rom"]), copy.deepcopy(built()["alloc_before"])
        alloc.notes["pool_refill"] = built()["notes"]
        with self.assertRaises(ValueError):
            pool_refill.apply(rom, alloc)


class Bytes(unittest.TestCase):

    def test_only_the_word_and_the_wrapper_change(self):
        before, rom, n = built()["before"], built()["rom"], built()["notes"]
        allowed = {range(n["hook"], n["hook"] + 4), range(n["wrapper"], n["wrapper"] + n["size"])}
        for off in range(len(rom)):
            if before[off] != rom[off] and not any(off in r for r in allowed):
                self.fail(f"rom:0x{off:X} changed outside the two declared sites")

    def test_the_word_names_the_wrapper(self):
        n = built()["notes"]
        self.assertEqual(u32(built()["rom"], n["hook"]), (n["wrapper"] + ROM_BASE) | 1)

    def test_the_wrapper_decodes_as_its_source(self):
        n = built()["notes"]
        text = [line for _at, line in listing(built()["rom"], n["wrapper"] + ROM_BASE, WRAPPER_LINES)]
        self.assertEqual(text[0], "push {r4,r5,lr}")
        self.assertIn(f"ldr r3,={VANILLA_EXT73:#010x}", text)
        self.assertIn(f"ldr r3,={built()['pool_ref'] | 1:#010x}", text)
        self.assertIn("strh r1,[r0,#0x2]", text)
        self.assertIn("ldrb r0,[r1,#0x14]", text)
        self.assertEqual(text.count("bx lr"), 1)


class Refill(unittest.TestCase):
    """The owner's defect, 2026-11-09: the Cell finale keeps the pool the android fights drained."""

    def test_the_finale_transform_fills_the_pool(self):
        """Trunks stands in his base body under the stale Super Saiyan tag; ext 73 gives him the form."""
        cp = run_op(built()["rom"], seeded(built()["rom"], BASE_ENTRY), writes(TRUNKS, SSJ_ENTRY))
        self.assertEqual(state(cp), (MAX_EP, STALE_TAG))

    def test_without_the_patch_the_pool_stays_drained(self):
        """The same run on the tree before pool_refill: this is the defect the owner played."""
        cp = run_op(built()["before"], seeded(built()["before"], BASE_ENTRY), writes(TRUNKS, SSJ_ENTRY))
        self.assertEqual(state(cp), (DRAINED, STALE_TAG))

    def test_leaving_the_form_clears_the_tag(self):
        """Ending word 13 puts Trunks back in his base body: the tag it leaves must not match again."""
        cp = run_op(built()["rom"], seeded(built()["rom"], SSJ_ENTRY), writes(TRUNKS, BASE_ENTRY))
        self.assertEqual(state(cp), (DRAINED, 0))

    def test_the_same_body_twice_keeps_the_pool(self):
        """The plateau record sets the base body first. A player already in it keeps what he has."""
        cp = run_op(built()["rom"], seeded(built()["rom"], BASE_ENTRY), writes(TRUNKS, BASE_ENTRY))
        self.assertEqual(state(cp), (DRAINED, STALE_TAG))

    def test_a_non_leader_change_keeps_the_pool(self):
        """A cutscene that changes somebody else's body must not hand the leader a free pool."""
        cp = seeded(built()["rom"], SSJ_ENTRY, pool=DRAINED, tag=STALE_TAG)
        cp = run_op(built()["rom"], cp, writes(0, 5))
        self.assertEqual(state(cp), (DRAINED, STALE_TAG))

    def test_the_handler_result_is_handed_back(self):
        cp = run_op(built()["rom"], seeded(built()["rom"], BASE_ENTRY), writes(TRUNKS, SSJ_ENTRY))
        self.assertEqual(cp.result, RESULT)


if __name__ == "__main__":
    unittest.main()
