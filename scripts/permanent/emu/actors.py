r"""
actors.py - Read the live actors (position, facing, sprite set) out of a capture run's RAM dumps.

Usage:   py -3.14 -P scripts\permanent\emu\actors.py <run folder> <rom.gba> [dump tag]
Input:   <run>\iwram.bin  (0x03000000, 32 KB) and <run>\ewram.bin (0x02000000, 256 KB), written by the
         capture job's `read` steps, plus the ROM the run used.
API:     Mem(dumps) -> u8/u16/u32/s32    set_ids(rom) -> {set header address: set id}
         walk(mem, rom) -> [Actor]       table(actors) -> the printable rows
Facts:   world object 0x03001120: +4 count, +8 active list of 128 pointers, +0x40C the second list (bible OVW).
         actor object: +0x10 facing (0 down, 1 up, 2 left, 3 right), +0x48 the sprite set, +0x158/+0x15C the
         anchor x and y as fixed point, so the world spot is the value >> 8 (bible CJH, PGS).
         The live set table address is the ROM word at rom:0x959C; its entry i is set id i + 7 (bible OUT).
         The player object pointer is the word at 0x03001FA8 (bible RSS).
"""
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

# ===== addresses =====
WORLD = 0x03001120
W_COUNT = WORLD + 0x04
W_LIST = WORLD + 0x08
W_LIST2 = WORLD + 0x40C
LIST_LEN = 128
PLAYER_PTR = 0x03001FA8

OBJ_FACING = 0x10
OBJ_SET = 0x48
OBJ_X = 0x158
OBJ_Y = 0x15C

SET_TABLE_LITERAL = 0x959C        # the ROM word that names the live set table
ROM_BASE = 0x08000000
EWRAM = (0x02000000, 0x40000)
IWRAM = (0x03000000, 0x8000)
FACING = {0: "down", 1: "up", 2: "left", 3: "right"}
SET_NAME = {53: "Gohan", 55: "Gohan", 56: "Gohan", 103: "Piccolo", 104: "Piccolo", 137: "Vegeta",
            140: "Vegeta", 128: "Trunks", 135: "Trunks", 76: "Krillin", 121: "Tien", 60: "Goku"}

@dataclass
class Actor:
    ptr: int
    set_addr: int
    set_id: int
    name: str
    x: int
    y: int
    facing: int
    is_player: bool

    @property
    def face_name(self):
        return FACING.get(self.facing, str(self.facing))

class Mem:
    """The dumped regions, addressed the way the GBA addresses them."""

    def __init__(self, regions):
        self.regions = list(regions)          # [(base, bytes)]

    @classmethod
    def from_run(cls, run, tag=""):
        """tag names one pair of dumps, so a job may read RAM at more than one frame."""
        run = Path(run)
        return cls([(EWRAM[0], (run / f"ewram{tag}.bin").read_bytes()),
                    (IWRAM[0], (run / f"iwram{tag}.bin").read_bytes())])

    def slice(self, addr, width):
        for base, data in self.regions:
            if base <= addr and addr + width <= base + len(data):
                return data[addr - base: addr - base + width]
        return None

    def has(self, addr, width=1):
        return self.slice(addr, width) is not None

    def u8(self, addr):
        return self.slice(addr, 1)[0]

    def u16(self, addr):
        return struct.unpack("<H", self.slice(addr, 2))[0]

    def u32(self, addr):
        return struct.unpack("<I", self.slice(addr, 4))[0]

    def s32(self, addr):
        return struct.unpack("<i", self.slice(addr, 4))[0]

def set_ids(rom: bytes) -> dict:
    """{set header address: set id} from the live set table the ROM word at rom:0x959C names."""
    table = struct.unpack_from("<I", rom, SET_TABLE_LITERAL)[0]
    out = {}
    off = table - ROM_BASE
    i = 0
    while off + 4 * i + 4 <= len(rom):
        word = struct.unpack_from("<I", rom, off + 4 * i)[0]
        if word < ROM_BASE or word >= ROM_BASE + len(rom):
            break
        out.setdefault(word, i + 7)
        i += 1
    return out

def _pointers(mem: Mem) -> list:
    """Every object pointer in the world's two lists, in list order, with no repeats."""
    seen, out = set(), []
    for base in (W_LIST, W_LIST2):
        for i in range(LIST_LEN):
            if not mem.has(base + 4 * i, 4):
                continue
            ptr = mem.u32(base + 4 * i)
            if ptr and mem.has(ptr, OBJ_Y + 4) and ptr not in seen:
                seen.add(ptr)
                out.append(ptr)
    return out

def walk(mem: Mem, rom: bytes) -> list:
    """Every world object that carries a sprite set, as an Actor. Objects with no set are skipped."""
    ids = set_ids(rom)
    player = mem.u32(PLAYER_PTR) if mem.has(PLAYER_PTR, 4) else 0
    out = []
    for ptr in _pointers(mem):
        set_addr = mem.u32(ptr + OBJ_SET)
        if set_addr not in ids:
            continue
        set_id = ids[set_addr]
        out.append(Actor(ptr=ptr, set_addr=set_addr, set_id=set_id,
                         name=SET_NAME.get(set_id, f"set {set_id}"),
                         x=mem.s32(ptr + OBJ_X) >> 8, y=mem.s32(ptr + OBJ_Y) >> 8,
                         facing=mem.u8(ptr + OBJ_FACING), is_player=(ptr == player)))
    out.sort(key=lambda a: (a.y, a.x))
    return out

def table(actors) -> list:
    rows = ["| Actor | Object | set | Spot | Faces | Player |", "|---|---|---|---|---|---|"]
    for a in actors:
        rows.append(f"| {a.name} | 0x{a.ptr:08X} | {a.set_id} | ({a.x},{a.y}) | {a.face_name} | "
                    f"{'yes' if a.is_player else ''} |")
    return rows

def main():
    run, rom_path = Path(sys.argv[1]), Path(sys.argv[2])
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    mem = Mem.from_run(run, tag)
    rom = rom_path.read_bytes()
    actors = walk(mem, rom)
    print(f"world count {mem.u32(W_COUNT)}  player 0x{mem.u32(PLAYER_PTR):08X}  actors {len(actors)}")
    for line in table(actors):
        print(line)

if __name__ == "__main__":
    main()
