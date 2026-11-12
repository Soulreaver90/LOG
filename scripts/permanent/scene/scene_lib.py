r"""
scene_lib.py - One place for the LoG II scene VM: encode, decode, walk tables, name records, copy and redirect.

Usage:   from scene import scene_lib                       (patches and tests; scripts\permanent is on sys.path)
         from scene.scene_lib import code, ext, push, text, relocate
Why:     the encoders lived in patches\piccolo_gi_scene.py and the record walker in patches\npc_gi.py, so every
         new scene module imported a patch to write a scene. Those modules now import these definitions, and
         both names keep working for the modules that already import them.
Gate:    this file must never change what a module writes. The encoders and relocate() moved here byte for byte.
         Add new helpers; never change how push() picks op 0 or op 29, never change an _op_end length, and never
         tighten relocate(). Every build list rebuilds byte-identical or the change is wrong.

API:     encode   zigzag(v) push(*vals) ext(n, *args) code(nxt, *ops) text(nxt, portrait, line)
                  named ext ops: spawn(), walk(), fly(), pose(), sound(), ... -> the same bytes as ext(n, ...)
                  battle_start(...) -> the standard battle start, four ops: the enemy, the bar, the HUD,
                  the camera back. battle_start_that_opens_a_scene(...) -> the other shape, for a fight
                  that really begins on another map: cover, load, form, frame, reveal, hold, HUD, bar.
                  scene_harness and tests\test_battle_start.py check the same two shapes.
         decode   op_end(rom, o) ops(rom, start, end) listing(rom, start, end)
                  record_end(rom, at) decode_record(rom, at, length) -> Record (with .code of Op)
         tables   table_words(...) table_length(rom, at) [table_end = floor] walk(...) records(...)
                  is_end_entry(word) stray_before(rom, at)
         namers   words_naming(rom, target, lo, hi) copy_and_redirect(rom, alloc, src, length, namers, ...)

Record:  the scene runner @0x0800B520 reads table[index]. An entry below 0x10000 ends the scene and is stored as
         the resume index; else it is a record pointer whose u16 at +0 is the next index, and the handler comes
         from type at +2 (@0x083EC84C). Type 0 is code (@0x0800B19C): the ops run, and when exactly one value is
         left on the stack it replaces the next index. Types 1-4 carry a portrait id at +3: 1 plain text
         (@0x0800B438), 2 a webfoot stream at +4 4-aligned (@0x0800B304), 3 format pointer +4 and script +8
         (@0x0800B33E), 4 script pointer +4 and stream +8 (@0x0800B396). Type 5 (@0x0800B494) jumps to the table
         at record +4, index 0. All CONFIRMED (bible section 8, tags SS3 and CSP).

Trap:    a scene table often carries a small stray word before word 0 (0x2164 before rom:0x3DF720, rom:0x3DAE70
         and rom:0x3E6078; 0x1156 before rom:0x3D9F5C; 0x11 before rom:0x3D5E68). A backward walk reads it as an
         END and shifts every index by one. A table starts at the word an item or an event names, never at a
         word found by walking back. walk() takes the start address and never searches backward. CONFIRMED (CH6).
Rules:   base ops and ext ops are two numberings. In `02 1B` the 02 is base op 2 (run ext) and the 1B is ext 27.
         BASE_OPS names the first, EXT_OPS the second. Every EXT_OPS row carries its label and its bible tag.
"""
import struct

# ===== constants =====
ROM_BASE = 0x08000000
END_LIMIT = 0x10000                     # a table entry below this ends the scene (it is the resume index)
TYPE_CODE, TYPE_TEXT, TYPE_STREAM, TYPE_FORMAT, TYPE_SCRIPT, TYPE_JUMP = 0, 1, 2, 3, 4, 5
PORTRAIT_TYPES = (TYPE_TEXT, TYPE_STREAM, TYPE_FORMAT, TYPE_SCRIPT)     # portrait id at +3
STRAY_WORDS = (0x2164, 0x1156, 0x11)    # seen before word 0 of a table; never walk a table backward (CH6)


# ===== script encoding (moved from patches\piccolo_gi_scene.py, byte for byte) =====

def zigzag(v: int) -> bytes:
    """Op 1/29 varint: v * 2 (negative: -v * 2 + 1), 7 bits a byte, MSB first."""
    u, groups = (v << 1) if v >= 0 else ((-v) << 1) | 1, []
    while True:
        groups.insert(0, u & 0x7F)
        u >>= 7
        if not u:
            break
    return bytes(g | 0x80 for g in groups[:-1]) + bytes(groups[-1:])


def push(*vals: int) -> bytes:
    if len(vals) == 1 and 0 <= vals[0] <= 0xFF:
        return bytes([0, vals[0]])                                # op 0: one zero-extended byte
    return bytes([29, len(vals)]) + b"".join(zigzag(v) for v in vals)


def ext(n: int, *args: int) -> bytes:
    return (push(*args) if args else b"") + bytes([2, n])


def code(nxt: int, *ops: bytes) -> bytes:
    """Type 0 record: {next index, 0, 0}, ops, end (op 17)."""
    return bytes([nxt, 0, 0]) + b"".join(ops) + b"\x11"


def text(nxt: int, portrait: int, line: str) -> bytes:
    """Type 1 record: {next index, 0, 1, portrait}, text, 00."""
    return bytes([nxt, 0, 1, portrait]) + line.encode("ascii") + b"\0"


# ===== record walking (moved from patches\npc_gi.py, byte for byte) =====

def _varint_end(rom: bytes, o: int) -> int:
    while rom[o] & 0x80:
        o += 1
    return o + 1


def _op_end(rom: bytes, o: int) -> int:
    op = rom[o]
    if op in (0, 2, 3, 18, 19, 28) or 21 <= op <= 26:
        return o + 2
    if op == 1:
        return _varint_end(rom, o + 1)
    if op == 29:
        end = o + 2
        for _ in range(rom[o + 1]):
            end = _varint_end(rom, end)
        return end
    if 4 <= op <= 17 or op in (20, 27):
        return o + 1
    raise ValueError(f"rom:0x{o:X}: unknown script op {op}")


def relocate(rom: bytes, rec: int, length: int, edits: dict) -> bytes:
    """Record rec with each edit applied at its op start; jz/jmp (forward) and loop (back) offsets re-encoded."""
    starts, o = [], rec + 3
    while o < rec + length:
        starts.append(o)
        o = _op_end(rom, o)
    if o != rec + length or set(edits) - set(starts):
        raise ValueError(f"rom:0x{rec:X}: ops do not end at +0x{length:X} or an edit is not on an op start")
    new_at, out = {}, bytearray(rom[rec:rec + 3])
    for s in starts:
        new_at[s] = rec + len(out)                   # address in record coordinates (rec + new offset)
        if s in edits:
            old, new = edits[s]
            end = s + len(bytes.fromhex(old))
            if rom[s:end].hex() != old or end not in starts + [rec + length]:
                raise ValueError(f"rom:0x{s:X} is {rom[s:end].hex()}, expected {old}")
            out += bytes.fromhex(new)
        elif not any(e < s < e + len(bytes.fromhex(v[0])) for e, v in edits.items()):
            out += rom[s:_op_end(rom, s)]
    new_at[rec + length] = rec + len(out)
    for s in starts:
        op = rom[s]
        if op in (18, 19, 28) and s in new_at:
            target = s + 2 + (rom[s + 1] if op != 28 else -rom[s + 1])
            delta = new_at[target] - (new_at[s] + 2)
            off = delta if op != 28 else -delta
            if not 0 <= off <= 0xFF:
                raise ValueError(f"rom:0x{s:X}: jump offset {off} out of range")
            out[new_at[s] - rec + 1] = off
    return bytes(out)


op_end = _op_end            # the public spelling; _op_end stays for the modules that import it
varint_end = _varint_end


# ===== op names =====
# Base ops and ext ops are two numberings: in `02 1B` the 02 is base op 2 (run ext) and the 1B is ext 27.
# Each row: number: (name, (argument names), label). C = a handler address or bytes in the bible; L = one
# consistent reading across our modules; S = a guess.
# Every row is read from its handler in the base op table rom:0x3B5C00. Ops 4-16 pop two values and push
# one (op 6 is unary); see scene_harness.BINARY for the handler address of each.
BASE_OPS = {
    0: ("push_u8", ("value",), "C"),            # @0x08008F45, one zero-extended byte
    1: ("push_varint", ("value",), "C"),        # @0x08008F5B
    2: ("ext", ("op",), "C"),                   # @0x08008F8F, runs the ext op named by the next byte
    3: ("set_var", ("slot",), "C"),             # @0x08008FA5, pops into a variable
    4: ("and", (), "C"), 5: ("or", (), "C"), 6: ("neg", (), "C"), 7: ("add", (), "C"),
    8: ("sub", (), "C"), 9: ("mul", (), "C"), 10: ("div", (), "C"), 11: ("eq", (), "C"),
    12: ("ne", (), "C"), 13: ("gt", (), "C"), 14: ("ge", (), "C"), 15: ("lt", (), "C"),
    16: ("le", (), "C"),
    17: ("end", (), "C"),                       # table word 17 is 0: the interpreter ends the record itself
    18: ("jmp", ("forward",), "C"),             # @0x080090FF, unconditional: it touches no stack value
    19: ("jz", ("forward",), "C"),              # @0x0800910B, pops one and jumps forward when it is zero
    20: ("drop", (), "C"),                      # @0x08009129, pops one and discards it
    27: ("loop_begin", (), "C"),                # @0x08009251, pops a count onto the loop area at +0x44
    28: ("loop_end", ("back",), "C"),           # @0x0800926D, counts down and jumps back while non-zero
    29: ("push_list", ("count",), "C"),         # @0x0800929B, count zigzag varints
}

# ext op: (name, (argument names), label)
EXT_OPS = {
    19: ("test_flag", ("flag",), "C"),          # bible section 8 flag ops
    20: ("test_flag_alt", ("flag",), "C"),
    21: ("item_count", ("item",), "C"),         # @0x080095E4 ext21_item_count
    23: ("visited", ("zone", "area"), "C"),     # @0x08009628, pops TWO and pushes the answer.
                                                # Was ("map",): the handler pops twice, and
                                                # chapter_cards already emits `push 8,1 ; ext 23`.
    27: ("set_flag", ("flag",), "C"),           # `00 C3 02 1B` = push 195 ; SETFLAG
    28: ("clear_flag", ("flag",), "C"),
    29: ("party_add", ("who",), "C"),           # @0x08009740, broadcast message 4 with 2n+1
    30: ("party_remove", ("who",), "C"),        # @0x0800975E, with 2n
    31: ("camera", ("x", "y", "speed"), "C"),   # @0x0800DF1C ext31_move; our scenes pass speed or leave it
    33: ("camera_follow", ("who",), "L"),       # record 44 hands the view back to the player (PGS)
    35: ("load_map", ("zone", "area", "var", "x", "y"), "C"),   # 5 pushes; rom:0x3EC690 = 6,3,1,376,408
    38: ("load_map_fade", ("zone", "area", "var", "x", "y"), "L"),  # 5 pushes x3, 1 push x6: a second form
    39: ("load_map_at", ("zone", "area", "var", "x", "y"), "L"),    # chamber exit seq 3 runs 9,1,1 at 760,440
    86: ("header_bit1", ("value",), "L"),     # bible section 8: op 86 sets header +1 bit 1
    40: ("fade_out", ("frames",), "L"),
    41: ("fade_in", ("frames",), "L"),
    42: ("palette_fx", ("value",), "C"),        # @0x08009B5E; "screen flash" is L (T6)
    43: ("flash_wait", ("frames",), "L"),
    46: ("sound", ("id",), "C"),                # @0x08009BF8 ext46_sound_start
    47: ("sound_stop", ("id",), "C"),           # @0x08009C54
    49: ("music", ("id",), "C"),                # @0x08009C8A
    51: ("spawn", ("set", "x", "y"), "C"),      # @0x0800D6DE
    52: ("remove", ("set",), "C"),
    53: ("walk", ("set", "x", "y"), "C"),       # anim 1, 1 px a frame (PGS)
    54: ("fly", ("set", "x", "y"), "C"),        # anim 12 (state 12), 2 px a frame (PGS)
    55: ("face", ("set", "dir"), "L"),          # dir 2 left, 3 right: from our module constants only
    56: ("face_alt", ("set", "dir"), "L"),
    57: ("pose", ("set", "state"), "C"),        # @0x08009FC4 ext57_set_state
    62: ("move_to", ("set", "x", "y"), "C"),    # places an actor with no walk (PGS r31)
    63: ("block_begin", (), "L"),               # our scenes bracket parallel work in 63 ... 64
    64: ("block_end", (), "L"),
    69: ("wait", ("frames",), "L"),
    70: ("leader", ("who",), "C"),              # @0x0800A784; also reverts other forms
    73: ("appearance", ("character", "set"), "C"),      # @0x0800A8EC
    76: ("item_dec", ("item",), "C"),           # @0x080096CA
    77: ("item_sub", ("item", "count"), "C"),   # @0x080096E8
    79: ("party_join", ("who",), "C"),          # @0x0800A9B6
    80: ("bit1_set", ("who",), "C"),            # @0x0800AA10
    81: ("bit1_clear", ("who",), "C"),          # @0x0800AA34
    82: ("bit5_set", ("who",), "C"),            # @0x0800AA58
    85: ("bar_show", ("set",), "L"),            # boss bar (CJ2)
    90: ("bar_set", ("set", "lo", "hi"), "L"),
    91: ("party_leave", ("who",), "C"),         # @0x0800A9DA
    95: ("face_target", ("set",), "L"),         # self-destruct seq 40 runs it before a knock-down (VS2)
    96: ("attack", ("attacker", "target", "n"), "L"),   # VS3 counts the sites; no handler read yet
    112: ("hit", ("set", "sound"), "L"),
    115: ("leader_alt", ("who",), "C"),         # @0x0800A680
    121: ("fly_pose", ("set", "state"), "L"),
    # 131-133 take NO argument. Each pushes one byte of 0x03001FC0, the level-up stat gains at
    # +1, +2 and +3 (bible row 1904). They are GETTERS: the handlers raise the stack depth. The
    # names were right and the arity was wrong, which is how they read as setters taking an amount.
    131: ("gain_str", (), "C"),                 # @0x08009466, pushes [0x03001FC1]
    132: ("gain_pow", (), "C"),                 # @0x08009478, pushes [0x03001FC2]
    133: ("gain_end", (), "C"),                 # @0x0800948A, pushes [0x03001FC3]
    135: ("flash", ("set", "r", "g", "b", "frames"), "L"),      # RGB888 pulse (PGS r29)
    136: ("walk_fast", ("set", "x", "y", "n"), "L"),            # speed n x 0x290 >> 8 (CJ2)
    145: ("card", ("id",), "L"),                # chapter card (C4T). NOT a real ext op: the handler
                                                # table rom:0x3B5D28 has 145 entries, 0 to 144,
                                                # and word 145 is 0x03000E90, IWRAM, not code.
}
EXT_BY_NAME = {row[0]: n for n, row in EXT_OPS.items()}


def op_name(n: int, base: bool = False) -> str:
    """spawn for a named op, ext57 or op12 for one the tables do not name."""
    table, prefix = (BASE_OPS, "op") if base else (EXT_OPS, "ext")
    return table[n][0] if n in table else f"{prefix}{n}"


def op_args(n: int) -> tuple:
    """The argument names of a named ext op; an empty tuple for one the table does not name."""
    return EXT_OPS[n][1] if n in EXT_OPS else ()


def op_label(n: int) -> str:
    """C, L or S for a named ext op; S for one the table does not name."""
    return EXT_OPS[n][2] if n in EXT_OPS else "S"


def call(name_or_number, *args: int) -> bytes:
    """ext bytes by name or by number: call("spawn", 158, 344, 400) == ext(51, 158, 344, 400).
    An unknown op stays usable by number: call(57, a, b) and ext(57, a, b) are the same bytes."""
    if isinstance(name_or_number, str):
        if name_or_number not in EXT_BY_NAME:
            raise KeyError(f"no ext op named {name_or_number!r}")
        n = EXT_BY_NAME[name_or_number]
        want = EXT_OPS[n][1]
        if len(args) > len(want):
            raise ValueError(f"{name_or_number} takes at most {len(want)} args {want}, got {len(args)}")
        return ext(n, *args)
    return ext(name_or_number, *args)


# The ops our scenes write most. Each is ext(n, ...) and nothing else, so the bytes cannot drift.

def spawn(s, x, y):
    return ext(51, s, x, y)


def remove(s):
    return ext(52, s)


def walk_to(s, x, y):
    return ext(53, s, x, y)


def fly_to(s, x, y):
    return ext(54, s, x, y)


def face(s, direction):
    return ext(55, s, direction)


def pose(s, state):
    return ext(57, s, state)


def move_to(s, x, y):
    return ext(62, s, x, y)


def camera(x, y, speed=None):
    return ext(31, x, y, speed) if speed is not None else ext(31, x, y)


def sound(i):
    return ext(46, i)


def music(i):
    return ext(49, i)


def wait(frames):
    return ext(69, frames)


def fade_out(frames):
    return ext(40, frames)


def fade_in(frames):
    return ext(41, frames)


def flash(s, r, g, b, frames):
    return ext(135, s, r, g, b, frames)


def set_flag(f):
    return ext(27, f)


def clear_flag(f):
    return ext(28, f)


def appearance(character, s):
    return ext(73, character, s)


def leader(who):
    return ext(70, who)


# ===== the standard battle start =====
# THE DEFAULT IS FOUR OPS AND NOTHING ELSE. Of the 30 records that raise a boss bar in our own trial
# build, 25 are vanilla and every one of those 25 loads no map and runs no fade: the talk ends and the
# fight begins on the spot. The model is Piccolo against Android 17, rom:0x3E47DC (map 11,4 word 6):
#   ext104(9, 1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0)
# Record 0 of that same table parked camera(152,96,3) for the whole conversation, so camera_follow(0)
# is what glides the view onto the player. battle_start() emits those four ops.
#
# The owner, 2026-11-06: "There should not be a fade at all after the diague! Dialogue ends fight begins
# with a camera pan to the user and the hud appearing, like every single fight int he game."
#
# battle_start_that_opens_a_scene() is the OTHER shape, for a record that really does open a scene on a
# new map. Its template is the Cell Games start, rom:0x3E9384 (map 14,3), the only vanilla record that
# both shows a bar and loads a map:
#   fade_out(120) ; load_map_at(14,3,1,368,440) ; ext84(5) ; leader(0) ; face(30,2) ; face(0,3)
#   camera(328,344,10) ; spawn(60,552,96) ; fade_in(120) ; wait(60) ; camera_follow(0)
#   header_bit1(1) ; bar_set(30,60,100) ; set_flag(192)
# It emits that order, less ext84 and set_flag, which belong to the scene and not to the shape.
COVER_KINDS = ("fade", "flash")         # fade_out / fade_in, or palette_fx / flash_wait


def battle_start(*, enemy_set, enemy_item, bar=None, bar_range=None, follow=0, hud=True) -> bytes:
    """Emit the standard battle start: the enemy, the bar, the HUD, the camera back. Four ops.

    enemy_set is the set id of the LIVE NPC standing where the fight starts, and enemy_item the index
    of the enemy item in the current map's own item list. ext 104 removes that NPC and builds the item
    at his position and facing. CONFIRMED from Sprite_ReplaceWithEntry @0x0800AAC6 and
    Object_SpawnFromEntry @0x0800C75C: the item is built by its OWN +0 factory, so an enemy item keeps
    its +0x14 death event, and the item's condition is never tested. The vanilla pairing is map 11,4
    item 0 (NPC set 9, condition 0) with item 1 (enemy set 9, condition 1).

    bar is the boss's own set id. bar_range=(lo, hi) picks ext 90 bar_set, which carries a DISPLAY
    SEGMENT for one round of a multi-round boss; without it ext 85 bar_show draws the whole bar. A
    single round fight wants ext 85.

    hud=False leaves header_bit1(1) out, for a record whose table never took the HUD away.
    follow=None leaves camera_follow out, for a table that holds no fixed camera.
    Returns op bytes, not a record: wrap it with code(next_index, battle_start(...)).

    What the emitter cannot know: whether a live actor of enemy_set really stands there, whether the
    item index is inside the map's count, or the boss's real bar range.
    """
    if bar_range is not None and bar is None:
        raise ValueError("bar_range needs the boss set id in bar=")
    if enemy_set == 0:
        raise ValueError("ext 104 needs an NPC to replace: set 0 is the player, who is not the enemy")
    out = [ext(104, enemy_set, enemy_item)]
    if bar is not None:
        out.append(call("bar_set", bar, *bar_range) if bar_range else call("bar_show", bar))
    if hud:
        out.append(call("header_bit1", 1))
    if follow is not None:
        out.append(call("camera_follow", follow))
    return b"".join(out)


def battle_start_that_opens_a_scene(*, leader_who, zone, area, var, player_xy, facing,
                                    frame_xy, frame_speed=10, hold=60, cover=("fade", 120),
                                    bar=None, bar_range=None, spawn_list=None,
                                    appearance=None, follow=0, form_before_load=False) -> bytes:
    """Emit a battle start that OPENS A SCENE: cover, load, form, frame, reveal, hold, HUD, bar.

    Use this only where the fight really begins on another map. Where the talk already stands on the
    fight's own ground, battle_start() is the shape, and a fade there is the defect the owner rejected
    on 2026-11-06. One vanilla record in the whole game uses this shape.

    The five obligations, in the template's order:
      1. cover    (kind, frames), kind "fade" (ext 40 / ext 41) or "flash" (ext 42 / ext 43). None emits
                  no cover, and the map load is then naked, which test_map_load_is_covered fails.
      2. load     load_map_at(zone, area, var, *player_xy). The load places the player, so no ext 62 is
                  needed and none is emitted.
      3. form     appearance=(who, set) emits ext 73 BEFORE the ext 70 leader change. appearance_revert
                  @0x08003ED4 leaves the new leader's record alone, so an ext 73 on the character who
                  becomes leader survives. CONFIRMED (report section 0).
      4. frame    camera(*frame_xy, frame_speed), under the cover.
      5. reveal   the cover's closing op, then wait(hold), then the hand-back: camera_follow(follow) when
                  follow is not None, header_bit1(1), and the bar.

    form_before_load moves the form block (ext 73, then ext 70) in front of the map load. The template
    leaves it after, and the default keeps that order byte for byte. Use True when the leader REALLY
    changes: ext 70 writes the party roster, but the block that installs the new leader's BODY is guarded
    (sub_0800A680: CMP r4,#0 then BEQ on Sprite_CurrentDirectory 0x03001FA8), so a scene that changes the
    leader must let the following map load build the player from the roster. The template's own leader(0)
    names a character who already leads, so it never proved the other order for a real change.

    bar is the boss's own set id. bar_range=(lo, hi) picks ext 90 bar_set; without it ext 85 bar_show.
    spawn_list is [(set, x, y)]; ext 51 is the one op that cannot address the player, so never spawn set 0.
    Returns op bytes, not a record: wrap it with code(next_index, battle_start(...)).

    The emitter writes the shape. It cannot know whether a story flag makes the form legal, whether
    frame_xy survives the map view clamp, or the boss's real set and bar range.
    """
    if cover is not None and (len(cover) != 2 or cover[0] not in COVER_KINDS):
        raise ValueError(f"cover must be None or (kind, frames) with kind in {COVER_KINDS}, got {cover!r}")
    if spawn_list and any(s == 0 for s, _, _ in spawn_list):
        raise ValueError("ext 51 spawn cannot address the player: set 0 builds a new NPC (report section 2)")
    if bar_range is not None and bar is None:
        raise ValueError("bar_range needs the boss set id in bar=")
    kind, frames = cover if cover else (None, 0)

    form = (ext(73, *appearance) if appearance is not None else b"") + leader(leader_who)

    out = [call("palette_fx", frames) if kind == "flash" else fade_out(frames) if kind else b""]
    if form_before_load:
        out.append(form)
    out.append(call("load_map_at", zone, area, var, *player_xy))
    if not form_before_load:
        out.append(form)
    out.append(face(0, facing))                       # set 0 is the player, whoever leads (report section 2)
    out.append(camera(*frame_xy, frame_speed))
    out += [spawn(s, x, y) for s, x, y in (spawn_list or ())]
    out.append(call("flash_wait", frames) if kind == "flash" else fade_in(frames) if kind else b"")
    out.append(wait(hold))
    if follow is not None:
        out.append(call("camera_follow", follow))
    out.append(call("header_bit1", 1))
    if bar is not None:
        out.append(call("bar_set", bar, *bar_range) if bar_range else call("bar_show", bar))
    return b"".join(out)


# ===== decoding =====

def unzigzag(rom: bytes, o: int) -> tuple:
    """(value, offset after the varint) at o. The inverse of zigzag()."""
    u, end = 0, o
    while True:
        u = (u << 7) | (rom[end] & 0x7F)
        more = rom[end] & 0x80
        end += 1
        if not more:
            break
    return (-(u >> 1) if u & 1 else (u >> 1)), end


class Op:
    """One decoded script op. ext is the ext number for base op 2, else None. args holds the values a push op
    carries; an ext op takes no operand bytes, it reads what the pushes before it left on the stack."""

    __slots__ = ("at", "op", "ext", "args", "end")

    def __init__(self, at, op, ext_n, args, end):
        self.at, self.op, self.ext, self.args, self.end = at, op, ext_n, args, end

    @property
    def name(self) -> str:
        return op_name(self.ext) if self.ext is not None else op_name(self.op, base=True)

    def __repr__(self) -> str:
        shown = ", ".join(str(a) for a in self.args)
        return f"rom:0x{self.at:X} {self.name}({shown})" if self.args else f"rom:0x{self.at:X} {self.name}"


def ops(rom: bytes, start: int, end: int) -> list:
    """Every op from start up to end (exclusive). Raises on an unknown op, exactly like _op_end."""
    out, o = [], start
    while o < end:
        stop = _op_end(rom, o)
        op, ext_n, args = rom[o], None, []
        if op == 0:
            args = [rom[o + 1]]
        elif op == 1:
            args = [unzigzag(rom, o + 1)[0]]
        elif op == 29:
            at = o + 2
            for _ in range(rom[o + 1]):
                value, at = unzigzag(rom, at)
                args.append(value)
        elif op == 2:
            ext_n = rom[o + 1]
        elif op in (3, 18, 19, 28) or 21 <= op <= 26:
            args = [rom[o + 1]]
        out.append(Op(o, op, ext_n, args, stop))
        o = stop
    if o != end:
        raise ValueError(f"rom:0x{start:X}: ops end at 0x{o:X}, not 0x{end:X}")
    return out


def listing(rom: bytes, start: int, end: int) -> list:
    """One readable line an op, with the pushed values folded into the ext op that consumes them."""
    out, pending = [], []
    for item in ops(rom, start, end):
        if item.op in (0, 1, 29):
            pending += item.args
            continue
        if item.ext is not None:
            names = op_args(item.ext)
            shown = ", ".join(f"{names[i]}={v}" if i < len(names) else str(v)
                              for i, v in enumerate(pending))
            out.append(f"rom:0x{item.at:X}  {op_name(item.ext)}({shown})  [{op_label(item.ext)}]")
        else:
            arg = f"({item.args[0]})" if item.args else ""
            out.append(f"rom:0x{item.at:X}  {op_name(item.op, base=True)}{arg}")
        pending = []
    if pending:
        out.append(f"  left on the stack: {pending}  (op 17 turns one value into the next index)")
    return out


class Record:
    """A decoded scene record. nxt is the u16 at +0 (the next table index), kind the byte at +2.
    code holds the ops of a kind 0 record, line the ASCII of a kind 1, target the pointer at +4 of 2-5."""

    __slots__ = ("at", "nxt", "kind", "portrait", "code", "line", "target", "end")

    def __init__(self, at, nxt, kind, portrait, code, line, target, end):
        self.at, self.nxt, self.kind, self.portrait = at, nxt, kind, portrait
        self.code, self.line, self.target, self.end = code, line, target, end

    @property
    def length(self) -> int:
        return self.end - self.at

    def __repr__(self) -> str:
        return f"rom:0x{self.at:X} type {self.kind} next {self.nxt} ({self.length} bytes)"


def record_end(rom: bytes, at: int) -> int:
    """The file offset just past a type 0 record's last op.

    A record that branches holds more than one op 17: the documented idiom puts `push N ; end` on one path
    and falls through to another end. So the walk cannot stop at the first op 17. It stops at the first
    op 17 that sits at or past the furthest target of any forward jump seen so far (ops 18 and 19, whose
    target is op + 2 + operand, the same arithmetic relocate() re-encodes)."""
    o, furthest = at + 3, 0
    while True:
        op = rom[o]
        if op in (18, 19):
            furthest = max(furthest, o + 2 + rom[o + 1])
        if op == 17 and o >= furthest:
            return o + 1
        o = _op_end(rom, o)


def decode_record(rom: bytes, at: int, length: int = None) -> Record:
    """Decode the record at file offset at. With no length a type 0 record ends at its op 17 and a type 1 at
    its NUL; the other types need a length, because only their I know where the payload stops."""
    nxt = struct.unpack_from("<H", rom, at)[0]
    kind = rom[at + 2]
    portrait = rom[at + 3] if kind in PORTRAIT_TYPES else None
    body, line, target = [], None, None
    if kind == TYPE_CODE:
        end = record_end(rom, at)
        body = ops(rom, at + 3, end - 1)
    elif kind == TYPE_TEXT:
        stop = bytes(rom).index(b"\0", at + 4)
        line = bytes(rom[at + 4:stop]).decode("ascii", "replace")
        end = stop + 1
    else:
        target = struct.unpack_from("<I", rom, at + 4)[0]
        end = at + 8
    if length is not None:
        end = at + length
    return Record(at, nxt, kind, portrait, body, line, target, end)


# ===== tables =====

def table_words(rom: bytes, at: int, count: int) -> list:
    """The count raw words of the scene table at file offset at."""
    return [struct.unpack_from("<I", rom, at + 4 * i)[0] for i in range(count)]


def is_end_entry(word: int) -> bool:
    """A table entry below 0x10000 ends the scene and is kept as the resume index (@0x0800B520)."""
    return word < END_LIMIT


def stray_before(rom: bytes, at: int) -> int:
    """The word just before the table when it looks like one of the known strays, else None.
    Never move a table start by this. A table starts at the word an item or an event names (CH6)."""
    if at < 4:
        return None
    word = struct.unpack_from("<I", rom, at - 4)[0]
    return word if word in STRAY_WORDS else None


def walk(rom: bytes, at: int, count: int) -> dict:
    """{index: entry word} for the table at file offset at, forward only.

    Forward only on purpose: a backward walk from the END word reads the small stray word that often sits
    before word 0 as an END, and shifts every index by one (bible CH6, the flag 148 correction). Pass the
    address an item or an event names, never one found by walking back."""
    if at % 4:
        raise ValueError(f"rom:0x{at:X}: a scene table is word aligned")
    return dict(enumerate(table_words(rom, at, count)))


# A table word is a record POINTER, or an END entry below 0x10000. A record lives in the vanilla
# script region, or, once a patch has moved it, in the expansion area a build allocates from.
# EXPANSION_REGION mirrors log2_build.BASE_SIZE and ART_REGION[0]. scene_lib must not import
# log2_build, because the patch modules import scene_lib, so test_ext_ops pins the two together.
TOOL_INDEX_NOTE = ("**Call `table_length()`, never `table_end()`.** `table_end()` stops at the "
                   "first END entry, and an END entry is an ordinary table word carrying a resume "
                   "index, not a terminator. Measured 2026-11-06: the first-END rule truncates 229 "
                   "of 303 map-owned tables and loses 1,398 words.")

SCRIPT_REGION = (0x3B0000, 0x420000)
EXPANSION_REGION = (0x800000, 0xF00000)


def is_record_pointer(word: int) -> bool:
    """Does this table word name a record: a vanilla one, or one a patch moved into expansion?
    A walker that only checks SCRIPT_REGION stops at the first moved record. Measured 2026-11-06 on
    log2_poc_r41_arena_v7: table rom:0x3DE6F4 reads 32 words that way and 36 with this test."""
    at = word - ROM_BASE
    return (SCRIPT_REGION[0] <= at < SCRIPT_REGION[1]) or (EXPANSION_REGION[0] <= at < EXPANSION_REGION[1])


def table_length(rom: bytes, at: int, limit: int = 256, records: set = None) -> int:
    """How many words the scene table at file offset at really has. USE THIS, not table_end().

    It walks while a word is an END entry or a pointer into the script region, and stops at the
    first word that is neither. An END entry does NOT end a table: it is an ordinary word carrying
    a resume index, and tables interleave them freely.

    Measured over the 302 readable map-owned tables, the first-END rule truncates 229 of them and
    loses 1,398 words. Re-walking with this rule raised the op census from 4,725 sites to 5,304 and
    from 94 to 102 distinct ops.

    WITHOUT records it over-reads by one word on 150 of the 302 readable base-ROM tables. The
    extra word is always the LAST of the walk and is the first word of the next record, whose
    header is below 0x10000 and so reads as an END entry. No site count moves, because every
    walker skips END entries, but the length is one too high. Pass records, a set of file
    offsets other tables name as records, and the walk stops exactly."""
    n = 0
    for i in range(limit):
        if not 0 <= at + 4 * i + 4 <= len(rom):      # a null or stray pointer reaches here
            break
        if records and at + 4 * i in records:       # the next record starts here, not a word
            break
        word = struct.unpack_from("<I", rom, at + 4 * i)[0]
        if is_end_entry(word) or is_record_pointer(word):
            n = i + 1
            continue
        break
    if n >= limit:                                  # never return the limit as a length
        raise ValueError(f"rom:0x{at:X}: no table end in {limit} words")
    return n


def table_end(rom: bytes, at: int, limit: int = 256) -> int:
    """The word count up to and including the first END entry. A FLOOR, never a length.

    Call table_length() instead for any census, sweep or listing. This one stays because a few
    callers want the first break, and because its number is in older reports.
    It reads forward from at, so the stray word before word 0 cannot shift it."""
    for i in range(limit):
        if is_end_entry(struct.unpack_from("<I", rom, at + 4 * i)[0]):
            return i + 1
    raise ValueError(f"rom:0x{at:X}: no END entry in {limit} words")


def records(rom: bytes, at: int, count: int, lengths: dict = None) -> dict:
    """{index: Record} for every table entry that is a record pointer. An END entry is left out."""
    lengths = lengths or {}
    out = {}
    for i, word in walk(rom, at, count).items():
        if not is_end_entry(word):
            out[i] = decode_record(rom, word - ROM_BASE, lengths.get(i))
    return out


# ===== namers =====

def words_naming(rom: bytes, target: int, lo: int = 0, hi: int = None) -> list:
    """File offsets of aligned words equal to target + ROM_BASE, searched in [lo, hi).
    This answers "which words name this record": they are what a copy has to repoint."""
    want = struct.pack("<I", target + ROM_BASE)
    hi = len(rom) if hi is None else hi
    body = bytes(rom)                            # once: a bytearray would be copied on every find
    out, at = [], lo
    while True:
        at = body.find(want, at, hi)
        if at < 0:
            return out
        if at % 4 == 0:
            out.append(at)
        at += 1


def copy_and_redirect(rom: bytearray, alloc, src: int, length: int, namers, edits: dict = None,
                      slot: int = 0, region: tuple = None, dead=()) -> int:
    """Copy the record at src into the expansion area, apply edits through relocate(), and point every namer
    at the copy. Returns the new file offset. The old record stays where it is, so a state paused in the old
    scene still ends.

    namers is the exact set of word offsets this copy may repoint, and the helper refuses to run when any
    other word names the record. It searches the whole ROM by default; region=(lo, hi) narrows that search,
    and search=False turns it off. The set is explicit, not a search, for two reasons: a built ROM keeps
    dead namers (the vanilla chamber-exit table still names its vanilla records), and one live record can
    have two real namers (the chamber exit has two type 5 words rom:0x3CF7E4 and rom:0x3D1530).

    dead= lists word offsets that name the record but must NOT be repointed, such as a vanilla table word
    left behind by an earlier module. Naming one is a decision the caller states, so it does not stop the
    copy, but it is never silent: a word is either repointed, listed dead, or an error."""
    namers = tuple(namers)
    if not namers:
        raise ValueError(f"rom:0x{src:X}: copy_and_redirect needs at least one namer")
    want = struct.pack("<I", src + ROM_BASE)
    for w in namers:
        if bytes(rom[w:w + 4]) != want:
            raise ValueError(f"rom:0x{w:X} does not name rom:0x{src:X}: it is {bytes(rom[w:w + 4]).hex()}")
    if region is not False:
        found = words_naming(rom, src, *(region or ()))
        extra = sorted(set(found) - set(namers) - set(dead))
        if extra:
            raise ValueError(f"rom:0x{src:X} is named by {len(extra)} word(s) the call did not list: "
                             + ", ".join(f"rom:0x{w:X}" for w in extra)
                             + ". Add each to namers= to repoint it, or to dead= to leave it pointing "
                               "at the old record.")
    data = relocate(rom, src, length, edits or {}) if edits else bytes(rom[src:src + length])
    at = alloc.alloc(max(len(data), slot))
    rom[at:at + len(data)] = data
    for w in namers:
        rom[w:w + 4] = struct.pack("<I", at + ROM_BASE)
    return at
