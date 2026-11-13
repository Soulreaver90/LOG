r"""Tests for rom\state_dump.py, which had none before 2026-11-06.

The actor scan is the part worth pinning: it is what found the conversation's two actors on arena v3 after
walking the world object lists had failed. The shape tests use planted buffers, so they need no save state.
One test reads the owner's real states when they are on this machine, and skips when they are not.
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import log_paths  # noqa: E402
from rom import state_dump                                                # noqa: E402

STATES = (log_paths.ARENA_V3_MOCKUPS)


def planted(pairs: list, size: int = 0x400) -> bytes:
    """A buffer of zeros holding each (offset, x, y) as an 8.8 anchor pair."""
    buf = bytearray(size)
    for off, x, y in pairs:
        struct.pack_into("<II", buf, off, x << 8, y << 8)
    return bytes(buf)


class ActorScan(unittest.TestCase):
    def test_it_finds_a_planted_spot_and_names_the_object(self):
        buf = planted([(0x100, 244, 504)])
        hits = state_dump.find_actors(buf, state_dump.WRAM_BASE)
        self.assertEqual(len(hits), 1)
        self.assertEqual((hits[0]["x"], hits[0]["y"]), (244, 504))
        # The anchor sits at obj+0x158, so the object base is the hit minus that.
        self.assertEqual(hits[0]["anchor"], state_dump.WRAM_BASE + 0x100)
        self.assertEqual(hits[0]["object"], state_dump.WRAM_BASE + 0x100 - state_dump.ANCHOR)

    def test_it_finds_several(self):
        buf = planted([(0x40, 244, 504), (0x200, 248, 568), (0x300, 248, 680)])
        got = {(h["x"], h["y"]) for h in state_dump.find_actors(buf, state_dump.WRAM_BASE)}
        self.assertEqual(got, {(244, 504), (248, 568), (248, 680)})

    def test_a_value_that_is_not_8_8_is_rejected(self):
        """A pair is an anchor only when BOTH words are whole 8.8 values."""
        buf = bytearray(0x400)
        struct.pack_into("<II", buf, 0x100, (244 << 8) + 1, 504 << 8)      # one stray low byte
        self.assertEqual(state_dump.find_actors(bytes(buf), 0), [])

    def test_a_spot_off_the_largest_map_is_rejected(self):
        buf = planted([(0x100, state_dump.MAP_MAX + 8, 504)])
        self.assertEqual(state_dump.find_actors(buf, 0), [])

    def test_zero_is_not_a_spot(self):
        """An unplaced object holds (0,0), and there are hundreds of them."""
        self.assertEqual(state_dump.find_actors(bytes(0x400), 0), [])

    def test_the_limit_is_adjustable(self):
        buf = planted([(0x100, 600, 600)])
        self.assertEqual(state_dump.find_actors(buf, 0, limit=512), [])
        self.assertEqual(len(state_dump.find_actors(buf, 0, limit=1024)), 1)


class CurrentMap(unittest.TestCase):
    def test_it_reads_the_zone_and_area_byte_pair(self):
        iwram = bytearray(0x8000)
        o = state_dump.CURRENT_MAP - state_dump.IWRAM_BASE
        iwram[o], iwram[o + 1] = 6, 100
        self.assertEqual(state_dump.current_map(bytes(iwram)), (6, 100))

    def test_a_short_buffer_answers_none_rather_than_raising(self):
        self.assertEqual(state_dump.current_map(b"\x06\x64"), (None, None))


@unittest.skipUnless(STATES.is_dir() and any(STATES.glob("*.ss2")),
                     "the owner's arena v3 states are not on this machine")
class OwnerStates(unittest.TestCase):
    """The regression this tool exists for: state 2 holds the conversation's spots and state 3 does not.

    Measured by hand on 2026-11-06 and used as the arena v4 specification, so it must stay reproducible."""

    @classmethod
    def regions(cls, path: Path) -> tuple:
        state = state_dump.load_state(path)
        io, ln = state_dump.REGIONS["iwram"]
        iwram = state[io:io + ln]
        wo, wl = state_dump.REGIONS["wram"]
        return iwram, state[wo:wo + wl]

    def spots(self, n: int) -> set:
        iwram, wram = self.regions(next(STATES.glob(f"*.ss{n}")))
        return {(h["x"], h["y"]) for h in state_dump.find_actors(wram, state_dump.WRAM_BASE)}

    def test_state_2_holds_the_conversation_spots(self):
        got = self.spots(2)
        self.assertIn((244, 504), got)
        self.assertIn((248, 568), got)

    def test_state_3_replaced_them_with_the_fight_spot(self):
        got = self.spots(3)
        self.assertNotIn((244, 504), got)
        self.assertNotIn((248, 568), got)
        self.assertIn((248, 680), got)

    def test_every_state_reads_the_arena_as_the_current_map(self):
        for n in (2, 3, 4, 5):
            if not any(STATES.glob(f"*.ss{n}")):
                continue
            iwram, _ = self.regions(next(STATES.glob(f"*.ss{n}")))
            self.assertEqual(state_dump.current_map(iwram), (6, 100), f"state {n}")


if __name__ == "__main__":
    unittest.main()
