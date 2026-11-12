r"""
scene_harness.py - Run a scene record or table the way the interpreter would, and report what it did.

Usage:   from scene.scene_harness import run_record, run_table           (tests and probes)
             run = run_record(rom, 0x3DBD5C)
             self.assertEqual(run.flags_set, {158})
             self.assertEqual(run.positions[103], (800, 472))
Why:     before this, each scene test re-wrote a small interpreter for the ops its own scene used, so a test
         could only check the ops its author thought of. This runs the record once and reports everything:
         the ops run, the spawns, the end position of every actor, the flags, the sounds and the next index.
Name:    it does not start with "test_", so unittest discover never collects it as a test module.

Model:   the runner @0x0800B520 reads table[index]; an entry below 0x10000 ends the scene. A type 0 record
         runs its ops and ends at op 17, and when exactly one value is left on the stack that value replaces
         the next index (@0x0800B19C). A type 1-4 record shows text and goes to its +0 index. CONFIRMED
         (bible SS3). An ext op pops every value pushed since the last ext op; that is how our modules write
         them, and the piccolo_gi_scene header states the same rule.
Camera:  run.camera_owner names which object owns 0x03000FF4 after the last op that wrote it, and
         run.screen_covered says whether a fade or flash was open at each op. Pass ONE Run to run_record()
         for every word of a table and both follow the table's WALK order, which is what the battle-start
         census counted. See the CAMERA_ and COVER_ constants for what each op is claimed to do.
Limits:  it models the stack, the ops in OPS below, and the ext ops it knows how to read. It does not model
         timing, animation, collision or combat. An ext op it does not know is still recorded, with its
         arguments, so a scene that uses one is testable; only its side effect is missing. Pass state=State(...) with the
         leader, the flags and the visited bits when the record branches on any of them.
         Inside a record it follows jz, jmp and the loop ops, so an op on a path not taken is not recorded.
         Across records it reads the order you call it in, not the next-index chain, unless you use
         run_table(). Neither is proof of what the game runs: a jz or a next index can branch either way.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts\permanent: -P and -I omit the script folder

from scene import scene_lib as S                                         # noqa: E402

# ext ops this harness understands as a side effect: op -> (what, how to read its args)
PLACE_OPS = {51: "spawn", 53: "walk", 54: "fly", 62: "move_to", 136: "walk_fast"}
MAX_STEPS = 400

# ===== the camera owner and the screen cover =====
# Who owns 0x03000FF4, the word that names the live camera object. Each op that writes it gets its own
# label, because they do not install the same object: ext 33 installs the player follow camera 0x030020C0
# (vtable 0x08025A6C) and ext 119 installs 0x030020F4 (vtable 0x08025034), which is NOT the follow camera.
# Source: docs\tasks\2026-11-06-vanilla-battle-starts\report.md sections 3 and 5.
CAMERA_FIXED, CAMERA_FOLLOW, CAMERA_EXT37, CAMERA_EXT119 = "fixed", "follow", "ext37", "ext119"
CAMERA_OWNERS = {31: CAMERA_FIXED,          # ext31_move @0x0800DF1C, the scene's own fixed camera
                 33: CAMERA_FOLLOW,         # camera_follow: the player follow camera
                 37: CAMERA_EXT37,          # also writes 0x03000FF4; which object it installs is not read
                 119: CAMERA_EXT119}        # the other object, not the follow camera
# A map load installs the camera and REPLACES it, writing the new player into 0x030020C0 + 4 and storing
# that object in 0x03000FF4, which is what ext 33 (0) does. It never eases, so the view SNAPS.
# LIKELY: read from map_load @0x0800C584 by the study agent, not re-read here (report section 5).
MAP_LOAD_OPS = (35, 38, 39)
# The owners that count as giving the camera back to the player. ext 119 is not one of them.
HANDS_BACK = (CAMERA_FOLLOW, CAMERA_EXT37)

# Is a fade or a flash open? COVER_UNKNOWN is "covered by no op we can name": ext 34 writes something
# whose effect lives in whatever reads [0x03001FC0 + 4], and that reader was never read, so a load behind
# an ext 34 is not proved uncovered either way (report section 6).
COVER_CLEAR, COVER_OPEN, COVER_UNKNOWN = "clear", "open", "unknown"
COVER_OPENS = (40, 42)                      # fade_out, palette_fx (the white flash)
COVER_CLOSES = (41, 43)                     # fade_in, flash_wait
COVER_OWN = 38                              # load_map_fade carries its own cover across the load
COVER_UNREAD = 34                           # LIKELY a screen effect; its reader was never read

# Base ops 21-26: the six get-and-set variable ops. Each runs the ext op named by its operand byte as a
# getter, which pushes the variable, then adds or subtracts 1 and calls the setter rom:0x3B5F70 + 4n.
# They differ only in what they leave on the stack. CONFIRMED from the handlers, read 2026-11-06:
#   21 @0x08009130  var += 1, pops the pushed value      24 @0x080091BC  var -= 1, pops the pushed value
#   22 @0x08009160  var += 1, leaves the NEW value       25 @0x080091EC  var -= 1, leaves the NEW value
#   23 @0x08009190  var += 1, leaves the OLD value       26 @0x08009224  var -= 1, leaves the OLD value
# Ops 21 and 24 decrement the stack count and then read the slot they just freed; 22 and 25 rewrite the
# top slot in place; 23 and 26 leave the top slot alone. Bible row 1894 (CJR) names the same six ops and
# agrees that op 21 pushes nothing. Each row: op -> (step, what stays on the stack)
VAR_STEP_OPS = {21: (1, None), 22: (1, "new"), 23: (1, "old"),
                24: (-1, None), 25: (-1, "new"), 26: (-1, "old")}

# Base ops that pop two values and push one. Every entry is CONFIRMED from its handler in the base op table
# rom:0x3B5C00: each one decrements the stack count, reads the top and the value below it, and stores the
# result in place. Op 6 is the one unary op (neg) and is handled on its own.
#   4 and  @0x08008FC7 (cmp, beq)        10 div @0x0800904B (bl @0x08021F30)   14 ge @0x080090B1 (bge)
#   5 or   @0x08008FE7 (orr)             11 eq  @0x08009063 (beq)              15 lt @0x080090CB (blt)
#   6 neg  @0x08009001 (neg, no pop)     12 ne  @0x0800907D (bne)              16 le @0x080090E5 (ble)
#   7 add  @0x0800900F (add)             13 gt  @0x08009097 (bgt)
#   8 sub  @0x08009023 (sub r1, r2, r1)   9 mul @0x08009037 (mul)
# The divide operand order is LIKELY: the handler passes the top in r0 and the value below it in r1.
BINARY = {
    4: lambda a, b: int(bool(a) and bool(b)),
    5: lambda a, b: int(bool(a) or bool(b)),
    7: lambda a, b: a + b,
    8: lambda a, b: a - b,
    9: lambda a, b: a * b,
    10: lambda a, b: a // b if b else 0,
    11: lambda a, b: int(a == b),
    12: lambda a, b: int(a != b),
    13: lambda a, b: int(a > b),
    14: lambda a, b: int(a >= b),
    15: lambda a, b: int(a < b),
    16: lambda a, b: int(a <= b),
}


class State:
    """What a record may branch on. Give the harness one when the scene reads any of it."""

    def __init__(self, leader: int = 0, flags=None, visited=None, variables=None):
        self.leader = leader
        self.flags = set(flags or ())
        self.visited = set(visited or ())
        self.variables = dict(variables or {})


class Run:
    """What one record or table did."""

    def __init__(self):
        self.calls = []            # [(ext number, (args))] in order
        self.spawns = {}           # set id -> (x, y) at its spawn
        self.positions = {}        # set id -> (x, y) after the last move
        self.removed = []          # set ids passed to ext 52, in order
        self.poses = {}            # set id -> the last ext 57 state
        self.facing = {}           # set id -> the last ext 55 direction
        self.flags_set = set()
        self.flags_cleared = set()
        self.sounds = []
        self.music = []
        self.lines = []            # the text of every type 1 record shown
        self.indexes = []          # the table indexes visited, in order
        self.next_index = None
        self.ended = False
        # Which object owns 0x03000FF4 after the last op that wrote it: one of the CAMERA_* labels, or
        # None when no op in this run touched the camera. Read it after the run to answer "did the scene
        # give the camera back": camera_owner in HANDS_BACK. Pass the same Run to run_record() for every
        # word of a table and this follows the table's WALK order, which is what the census counted.
        self.camera_owner = None
        # COVER_CLEAR, COVER_OPEN or COVER_UNKNOWN as of each entry of calls, same length and same order.
        # The entry for an op is the state AFTER that op's own cover effect, so a fade_out reads
        # COVER_OPEN, a fade_in reads COVER_CLEAR, and a map load reads whatever is current.
        self.screen_covered = []
        # The cover the NEXT op will see. It differs from screen_covered[-1] after a load_map_fade, which
        # covers its own load and then reveals.
        self.cover_state = COVER_CLEAR
        # True when the run had to invent a value: an ext op pushed a result this harness does not model,
        # so a later comparison or branch found the stack short. The ops and the side effects are still
        # real; a branch taken after that point is a guess. Assert it is False in a test that checks a branch.
        self.approximate = False

    @property
    def ops_run(self) -> list:
        """["spawn", "walk", ...] in order, for a test that only cares which ops ran."""
        return [S.op_name(n) for n, _ in self.calls]

    def called(self, which) -> list:
        """Every call of one ext op, by name or by number: run.called("spawn")."""
        n = S.EXT_BY_NAME[which] if isinstance(which, str) else which
        return [args for op, args in self.calls if op == n]

    def cover_at(self, which) -> list:
        """The cover state at every call of one ext op: run.cover_at("load_map_at") -> ["open"]."""
        n = S.EXT_BY_NAME[which] if isinstance(which, str) else which
        return [self.screen_covered[i] for i, (op, _) in enumerate(self.calls) if op == n]

    def __repr__(self) -> str:
        return (f"<Run {len(self.calls)} ops, {len(self.spawns)} spawn(s), "
                f"flags+{sorted(self.flags_set)}, next {self.next_index}>")


def _pop(stack: list, run: Run) -> int:
    """Pop a value, or 0 when the stack is short. A short stack means an ext op pushed a result this
    harness does not model, so the run is marked approximate rather than crashing."""
    if stack:
        return stack.pop()
    run.approximate = True
    return 0


def _record(run: Run, n: int, args: tuple) -> None:
    """Put one ext op on run.calls, with the cover state it ran under and the camera owner it leaves.

    Every path that appends to run.calls goes through here, so calls and screen_covered stay the same
    length and the same order."""
    run.calls.append((n, args))
    if n in COVER_OPENS:
        run.cover_state = COVER_OPEN
        cover = COVER_OPEN
    elif n in COVER_CLOSES:
        run.cover_state = COVER_CLEAR
        cover = COVER_CLEAR
    elif n == COVER_UNREAD:
        run.cover_state = COVER_UNKNOWN
        cover = COVER_UNKNOWN
    elif n == COVER_OWN:
        cover = COVER_OPEN                  # its own fade covers the load, and reveals after it
        run.cover_state = COVER_CLEAR
    else:
        cover = run.cover_state
    run.screen_covered.append(cover)
    if n in CAMERA_OWNERS:
        run.camera_owner = CAMERA_OWNERS[n]
    elif n in MAP_LOAD_OPS:
        run.camera_owner = CAMERA_FOLLOW


def _apply(run: Run, n: int, args: tuple) -> None:
    """Record the side effect of one ext op."""
    _record(run, n, args)
    if n in PLACE_OPS and len(args) >= 3:
        set_id, x, y = args[0], args[1], args[2]
        run.positions[set_id] = (x, y)
        if n == 51:
            run.spawns[set_id] = (x, y)
    elif n == 52 and args:
        run.removed.append(args[0])
    elif n == 55 and len(args) >= 2:
        run.facing[args[0]] = args[1]
    elif n == 57 and len(args) >= 2:
        run.poses[args[0]] = args[1]
    elif n == 27 and args:
        run.flags_set.add(args[0])
    elif n == 28 and args:
        run.flags_cleared.add(args[0])
    elif n == 46 and args:
        run.sounds.append(args[0])
    elif n == 49 and args:
        run.music.append(args[0])


def run_record(rom: bytes, at: int, state: State = None, run: Run = None) -> Run:
    """Run the record at file offset at. Returns the Run (a fresh one unless you pass one to add to)."""
    state = state or State()
    run = run or Run()
    nxt = struct.unpack_from("<H", rom, at)[0]
    kind = rom[at + 2]
    if kind != S.TYPE_CODE:
        rec = S.decode_record(rom, at)
        if kind == S.TYPE_TEXT:
            run.lines.append(rec.line)
        run.next_index = nxt
        return run

    stack, loops, o, steps = [], [], at + 3, 0
    while True:
        steps += 1
        if steps > MAX_STEPS:
            raise AssertionError(f"rom:0x{at:X}: more than {MAX_STEPS} ops; the record may loop forever")
        op, end = rom[o], S._op_end(rom, o)
        if op == 0:
            stack.append(rom[o + 1])
        elif op == 1:
            stack.append(S.unzigzag(rom, o + 1)[0])
        elif op == 29:
            value_at = o + 2
            for _ in range(rom[o + 1]):
                value, value_at = S.unzigzag(rom, value_at)
                stack.append(value)
        elif op == 2:
            n, args = rom[o + 1], tuple(stack)
            stack = []
            if n == 11:                                   # pushes the leader
                _record(run, 11, ())
                stack = [state.leader]
            elif n == 23:                                 # pushes a visited bit
                args = tuple(args[-2:])
                _record(run, 23, args)
                stack = [int(args in state.visited)]
            elif n in (19, 20):                           # pushes a flag
                _record(run, n, args)
                stack = [int(bool(args) and args[0] in state.flags)]
            else:
                _apply(run, n, args)
        elif op == 3:
            state.variables[rom[o + 1]] = stack.pop() if stack else 0
        elif op in VAR_STEP_OPS:
            step, keeps = VAR_STEP_OPS[op]
            slot = rom[o + 1]
            old = state.variables.get(slot, 0)
            state.variables[slot] = old + step
            if keeps is not None:
                stack.append(state.variables[slot] if keeps == "new" else old)
        elif op == 6:
            if stack:
                stack[-1] = -stack[-1]                    # the only unary op: it pops nothing
            else:
                run.approximate = True
        elif op in BINARY:
            b, a = _pop(stack, run), _pop(stack, run)
            stack.append(BINARY[op](a, b))
        elif op == 18:
            end += rom[o + 1]                             # unconditional: its handler touches no stack value
        elif op == 19:
            if not _pop(stack, run):                      # pops one, jumps forward when it is zero
                end += rom[o + 1]
        elif op == 20:
            _pop(stack, run)                              # pops one and discards it
        elif op == 27:
            loops.append(_pop(stack, run))                # a loop count onto the loop area
        elif op == 28:
            if loops:
                loops[-1] -= 1
                if loops[-1] > 0:
                    end -= rom[o + 1]
                else:
                    loops.pop()
            else:
                run.approximate = True
        elif op == 17:
            run.next_index = stack[-1] if len(stack) == 1 else nxt
            return run
        else:
            raise AssertionError(f"rom:0x{o:X}: op {op} is not modelled by scene_harness. "
                                 f"Add it here rather than writing a second interpreter.")
        o = end


def run_table(rom: bytes, table_at: int, start: int = 0, count: int = None,
              state: State = None, max_records: int = 120) -> Run:
    """Run the table from index start until an END entry, following each record's next index."""
    state = state or State()
    # table_length, not table_end: count bounds the index range, and a record whose next index
    # sits past the first END entry is in range. table_end would stop the run early.
    count = count or S.table_length(rom, table_at)
    words = S.table_words(rom, table_at, count)
    run, index = Run(), start
    for _ in range(max_records):
        if not 0 <= index < count:
            raise AssertionError(f"table rom:0x{table_at:X}: index {index} is outside its {count} words")
        run.indexes.append(index)
        word = words[index]
        if S.is_end_entry(word):
            run.ended, run.next_index = True, word
            return run
        run_record(rom, word - S.ROM_BASE, state, run)
        if run.next_index is None:
            raise AssertionError(f"record at index {index} set no next index")
        index = run.next_index
    raise AssertionError(f"table rom:0x{table_at:X}: no END after {max_records} records")
