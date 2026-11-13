r"""
test_battle_start.py - The standard battle start, checked over the live build: cover the map load, keep the
                       form across the leader change, hand the camera back, address the player, show the HUD.

Run (from the LOG root):
  py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent -p test_battle_start.py -v
Builds build_list_trial_ending.txt in memory, once, applying one module at a time so each record can be
traced to the module that wrote it. Every record is run through scene.scene_harness, and the five tests read
only run.calls, run.camera_owner and run.screen_covered.
Source:  docs\tasks\2026-11-06-vanilla-battle-starts\report.md section 3 is the specification. The vanilla
         template is rom:0x3E9384 (map 14,3, the Cell Games start), the only vanilla record that both shows a
         bar and loads a map. scene_lib.battle_start() emits that shape; these tests check it.

ORDER IS NOT PART OF THE SHAPE. The three control ops appear in three orders across rom:0x3D40B2,
rom:0x3EA3EC and rom:0x3EB6E8, so no test here asserts the order of camera_follow, header_bit1 and the bar.

What this checker reads, and what it cannot:
  - It reads WALK order, not execution order. Across a table it reads word 0 to the last word; inside a
    record scene_harness follows jz, jmp and the loop ops. Where a jz or a next index branches, the game may
    run another order, so a record named here is a candidate and a record not named is not cleared.
  - THE SCREEN COVER IS READ PER RECORD, and the camera owner per TABLE. A fade is a one-shot transition,
    not a latch a later record inherits, and carrying it across records reads table rom:0x3B8140 wrongly:
    two earlier records run fade_out, so record F's naked load would read as covered. The owner SAW that
    load snap, so the screen was clear when it ran, and the per-record reading is the one that matches the
    game. It also matches the census those 43-of-55 and zero-exception counts came from. The camera is the
    other way round, because our record F sets no camera of its own and the stuck view came from an EARLIER
    record of the same table.
  - The record census is a FLOOR, not a complete set. Two shapes reach it: the tables every map entry owns,
    and the tables in EXTRA_TABLES. A table named only by code, by a script region item (0x0800C2C3) or by a
    map enter script, and not declared here, does not appear. The LENGTH half of that floor is fixed:
    the census walks with S.table_length(), which reads past an END word, so a declared word count in
    EXTRA_TABLES now states a table only for reachability, not to rescue its length.
  - It cannot know whether a story flag makes a form legal (Super Saiyan 2 is flag 195), whether frame_xy
    survives the map view clamp (bible rows 1168 and 1507), the boss's real set or bar range, which
    map_load branch a map takes (layout +0x3C), or anything about timing, animation or combat.
"""
import struct
import unittest

import log2_build
import log_paths
from scene import scene_harness as H
from scene import scene_lib as S
from scene import scene_probe as P

# ===== constants =====
TRIAL_LIST = log_paths.BUILD_LISTS / "build_list_trial_ending.txt"
TEMPLATE = 0x3E9384                             # the vanilla template, map 14,3, the Cell Games start

# Scene tables no map entry owns, so the map walk cannot reach them.
# table offset -> (word count, or None to let S.table_length() read it; how it is reached).
# A module's own table is looked up from alloc.notes, because the allocator picks its address.
EXTRA_TABLES = {0x3B8140: (27, "the ending sequence, named by code, not by a map entry (test_ending_fight)")}
EXTRA_FROM_NOTES = [("piccolo_gi_scene", "table", "words",
                     "the chamber exit, started by the two type 5 records rom:0x3CF7E0 and rom:0x3D152C; "
                     "its appended records 35-44 sit PAST the END word at index 34")]

# Ops whose FIRST argument is a sprite set id. Every one is a caller of find_actor_by_set @0x08009370 or is
# proven on set 0 in our own shipped ROM (report section 2), except ext 51 spawn, which builds a new NPC.
SET_OPS = {51: "spawn", 52: "remove", 53: "walk", 54: "fly", 55: "face", 56: "face_alt", 57: "pose",
           62: "move_to", 85: "bar_show", 90: "bar_set", 95: "face_target", 96: "attack", 112: "hit",
           121: "fly_pose", 135: "flash", 136: "walk_fast"}
# NPC sets the design moved onto set 0, so a record our modules own must no longer name them. Set 132 is
# NOT here: it is the plain NPC Trunks the Cell Games scenes and the Lookout scene still use, and the report
# says the two camera_follow ops naming 132 are untouched. Only 133 was replaced by the player.
MOVED_ONTO_PLAYER = {133: "Super Saiyan Trunks: the ending fight makes him the player, so set 0 names him"}

BAR_OPS = (85, 90)                              # bar_show, bar_set
HUD_ON = 86                                     # header_bit1(1) gives the player HUD back, (0,) takes it away
FIXED_CAMERA = 31
FADE_OUT = 40                                   # ext 40: the op that OPENS a cover
APPEARANCE, LEADER = 73, 70

# The two appearance tables the game really reads, each resolved from ITS OWN literal, because a build
# moves them and the two literals are different words. appearance_of_set @0x080042BC turns a SET id into
# an entry index: it loads its base with LDR r4,[pc,#0x30] from rom:0x42F0, which gohan_gi repoints at its
# copy, and its loop bound CMP r2,#0x16 is 22 entries. appearance_revert @0x08003ED4 then reads THAT
# entry's flags and revert target from a base it loads with LDR r4,[pc,#0x274] from rom:0x414C, which
# ssj2_form repoints at a 23 entry table. Reading one literal for both jobs would be wrong the day they
# disagree. Both CONFIRMED from the handlers in the disassembly.
SET_LOOKUP_LITERAL, REVERT_LITERAL = 0x42F0, 0x414C
APPEARANCE_ENTRIES, APPEARANCE_SIZE = 22, 20    # the lookup's own bound, and the stride both handlers form
TRANSFORMED = 0x01                              # entry +0 bit 0: LSL r5,r5,#0x1F then BEQ skips the rest

_CACHE = {}


# ===== the appearance table, as the two handlers read it =====

def appearance_table(rom: bytes, literal: int) -> int:
    return struct.unpack_from("<I", rom, literal)[0] - S.ROM_BASE


def entry_of_set(rom: bytes, set_id: int):
    """The appearance entry ext 73 finds for this set id, or None, scanning as sub_080042BC does."""
    at = appearance_table(rom, SET_LOOKUP_LITERAL)
    for e in range(APPEARANCE_ENTRIES):
        if rom[at + APPEARANCE_SIZE * e + 1] == set_id:
            return e
    return None


def is_transformed(rom: bytes, entry: int) -> bool:
    """Entry flags bit 0. appearance_revert reverts an entry that has it and skips every entry without
    it, so an ext 73 that names an untransformed entry is never undone by a leader change."""
    return bool(rom[appearance_table(rom, REVERT_LITERAL) + APPEARANCE_SIZE * entry] & TRANSFORMED)


# ===== the build, and who wrote each byte of it =====

def built() -> dict:
    """{"rom": bytes, "alloc": Allocator, "blocks": {module: [(offset, size)]}}, built once.

    The modules are applied one at a time so alloc.used() can be sliced per module. The call order is the
    build list's own order, so the ROM is the one build_list_trial_ending.txt produces.
    """
    if not _CACHE:
        names = log2_build.read_build_list(TRIAL_LIST)
        rom, alloc = log2_build.assemble(log2_build.BASE, [])
        blocks = {}
        for name in names:
            mark = len(alloc.used())
            log2_build.apply_patches(rom, alloc, [name])
            blocks[name] = alloc.used()[mark:]
        _CACHE.update(rom=bytes(rom), alloc=alloc, blocks=blocks, names=names)
    return _CACHE


def owner_of(at: int) -> str:
    """The module whose own allocation holds this file offset, or None for a vanilla address.

    A module that edits a vanilla record IN PLACE allocates nothing, so its edit reads as vanilla here.
    """
    for name, blocks in built()["blocks"].items():
        if any(start <= at < start + size for start, size in blocks):
            return name
    return None


# ===== the census =====

class Read:
    """One record as the checker read it."""

    __slots__ = ("table", "index", "at", "run", "where", "owner")

    def __init__(self, table, index, at, run, where, owner):
        self.table, self.index, self.at, self.run = table, index, at, run
        self.where, self.owner = where, owner

    def __repr__(self) -> str:
        who = self.owner or "vanilla"
        return f"record rom:0x{self.at:X} (table rom:0x{self.table:X} word {self.index}, {self.where}, {who})"


class TableRead:
    """One scene table, read word 0 to the last word with ONE Run, so camera_owner follows walk order."""

    __slots__ = ("at", "run", "reads", "where")

    def __init__(self, at, run, reads, where):
        self.at, self.run, self.reads, self.where = at, run, reads, where

    @property
    def control_records(self) -> list:
        """Every record of this table that gives the player HUD back."""
        return [r for r in self.reads if (1,) in r.run.called(HUD_ON)]

    def __repr__(self) -> str:
        return f"table rom:0x{self.at:X} ({self.where})"


def scene_tables(rom: bytes, alloc) -> dict:
    """{table offset: (word count or None, how it is reached)} by two independent shapes.

    Shape A walks THIS build's own map table, resolved from the literal rom:0xEBD8, so battle_arena's moved
    table and its new map 6,100 are read. Shape B is EXTRA_TABLES plus EXTRA_FROM_NOTES. Neither shape sees
    a table named only by code and not declared, so the result is a floor.
    """
    table_at, count = P.map_table(rom)
    found = {}
    for k in range(count):
        at = table_at + P.MAP_SIZE * k
        try:
            info = P.map_items(rom, rom[at], rom[at + 1], table_at, count)
        except ValueError:
            continue
        where = f"map {rom[at]},{rom[at + 1]}"
        for _, it in info["regions"]:
            if "table" in it:
                found.setdefault(it["table"], (None, f"{where} region"))
        for it in info["items"]:
            if "table" in it:
                found.setdefault(it["table"], (None, f"{where} {it['kind']}"))
    found.update(EXTRA_TABLES)
    for module, table_key, words_key, why in EXTRA_FROM_NOTES:
        notes = alloc.notes[module]
        found[notes[table_key]] = (notes[words_key], why)
    return found


def census() -> dict:
    """{"tables": [TableRead], "reads": [Read]} over the live build, read once."""
    if "census" not in _CACHE:
        b = built()
        rom = b["rom"]
        tables, reads = [], []
        for at, (words, where) in sorted(scene_tables(rom, b["alloc"]).items()):
            if not 0 < at < len(rom):
                continue
            run, mine = H.Run(), []
            state = H.State()
            for index, word in S.walk(rom, at, words or S.table_length(rom, at)).items():
                if S.is_end_entry(word):
                    continue
                rec = word - S.ROM_BASE
                if not 0 < rec < len(rom):
                    continue
                H.run_record(rom, rec, state, run)                 # the table's own walk-order Run
                mine.append(Read(at, index, rec, H.run_record(rom, rec, H.State()), where, owner_of(rec)))
            tables.append(TableRead(at, run, mine, where))
            reads += mine
        _CACHE["census"] = {"tables": tables, "reads": reads}
    return _CACHE["census"]


# ===== the deviation convention =====

def note_path(name: str, path: str) -> int:
    """The file offset a module's own notes hold under a dotted path: "records.fight_cell_seq21".

    A module's records live where the ALLOCATOR puts them, so a raw offset in a module's source is
    stale the day an earlier module's allocation moves. A path is resolved against this build.
    Each component indexes a dict by its own key, by that key read as a number, or a list by index.
    """
    node = built()["alloc"].notes[name]
    for part in path.split("."):
        if isinstance(node, dict):
            key = part if part in node else next((k for k in node if str(k) == part
                                                  or (isinstance(k, int) and k == _as_int(part))), None)
            if key is None:
                raise KeyError(f"{name} notes have no {part!r} (path {path!r})")
            node = node[key]
        else:
            node = node[_as_int(part)]
    if not isinstance(node, int):
        raise TypeError(f"{name} notes {path!r} is {type(node).__name__}, not a file offset")
    return node


def _as_int(text: str):
    try:
        return int(text, 0)
    except ValueError:
        return None


def declared_exceptions(modules: dict = None) -> dict:
    """{record offset: (module, why)} from every build-list module's optional BATTLE_START_EXCEPTIONS.

    A module declares a record that breaks the shape on purpose:
        BATTLE_START_EXCEPTIONS = {0x9405E8: "one line of why"}
    A key may instead be a dotted path into that module's own alloc.notes, which is what a real entry
    uses, because an allocated record moves whenever an earlier module's allocation does:
        BATTLE_START_EXCEPTIONS = {"records.fight_cell_seq21": "one line of why"}
    Pass modules={name: the dict} to test the support without a module carrying one.
    """
    if modules is None:
        import importlib
        modules = {name: getattr(importlib.import_module(f"patches.{name}"), "BATTLE_START_EXCEPTIONS", None)
                   for name in built()["names"]}
    out = {}
    for name, declared in modules.items():
        for at, why in (declared or {}).items():
            out[note_path(name, at) if isinstance(at, str) else at] = (name, why)
    return out


def stale_exceptions(declared: dict, failing: set) -> list:
    """Why each declared exception is stale, if it is: the module does not own that record, or the record
    no longer breaks any rule. Either way the entry has to go, so the test fails on it."""
    bad = []
    for at, (module, why) in sorted(declared.items()):
        if owner_of(at) != module:
            bad.append(f"rom:0x{at:X} is declared by {module}, but that module did not write it "
                       f"(it belongs to {owner_of(at) or 'vanilla'}): {why!r}")
        elif at not in failing:
            bad.append(f"rom:0x{at:X} is declared by {module}, but the record breaks no rule any more, "
                       f"so the entry is stale: {why!r}")
    return bad


def excused(at: int) -> bool:
    return at in declared_exceptions()


def _lines(rows: list) -> str:
    return "\n  " + "\n  ".join(rows)


def _report(found: list) -> list:
    """The message of every finding a module has not declared an exception for."""
    return [why for at, why in found if not excused(at)]


# ===== the five rules, each as a finder the tests read =====
# A finder returns [(record offset, one line of why)] and does NOT filter the declared exceptions, so
# stale_exceptions() can ask whether a declared record still breaks a rule.

def naked_loads() -> list:
    """Rule 1: a record that loads a map and shows a bar keeps a fade or flash open across the load.

    map_load @0x0800C584 replaces the camera and never eases, so the view SNAPS to the player's spot minus
    (112, 76). The snap is invisible only while the screen is covered. Of 55 vanilla map-load records 43
    are covered, and no vanilla record that shows a bar loads a map without cover. COVER_UNKNOWN passes:
    ext 34's effect was never read, so a load behind it is not proved uncovered either way.
    """
    out = []
    for r in census()["reads"]:
        if not any(r.run.called(n) for n in BAR_OPS):
            continue
        if any(c == H.COVER_CLEAR for n in H.MAP_LOAD_OPS for c in r.run.cover_at(n)):
            out.append((r.at, f"{r!r} shows a bar and loads a map with the screen {H.COVER_CLEAR}"))
    return out


def cameras_not_handed_back() -> list:
    """Rule 2: a table that sets a fixed camera and gives control back reclaims it after the LAST ext 31.

    Of 302 vanilla tables, 48 set a fixed camera; counting only what runs after the last ext 31, the number
    that give control back and reclaim it by nothing is ZERO. ext 33, ext 37 and a map load count; ext 119
    does not, because it installs 0x030020F4, which is not the follow camera. The finding is keyed by the
    table's first control record, so a module declares the deviation on the record it wrote.
    """
    out = []
    for t in census()["tables"]:
        control = t.control_records
        if not t.run.called(FIXED_CAMERA) or not control or t.run.camera_owner in H.HANDS_BACK:
            continue
        cams = ", ".join(str(a) for a in t.run.called(FIXED_CAMERA))
        out.append((control[0].at,
                    f"{t!r} runs camera({cams}) and gives control back at rom:0x{control[0].at:X}, "
                    f"but the camera is still owned by {t.run.camera_owner}"))
    return out


def forms_lost_at_the_leader_change() -> list:
    """Rule 3: a record running ext 73 and ext 70 names the same character in both, or runs ext 73 after.

    ext70_set_leader @0x0800A784 runs set_leader and then appearance_revert @0x08003ED4, which skips only
    the party record whose index equals the save struct's leader byte. So an appearance set on anyone who
    does not become the leader is reverted. CONFIRMED (report section 0). Each ext 73 is judged on its own.

    NARROWED 2026-11-06, with the handler's second gate: appearance_revert also skips any entry whose
    flags bit 0 is CLEAR, so only a TRANSFORMED appearance is ever undone. An ext 73 that names a base
    form survives a leader change whoever it names, and flagging it was a false alarm 4 times out of 5.
    A set the lookup table does not hold is not flagged here: ext 73 never resolves it to an entry, so
    there is nothing for the revert to undo, and that is a different defect from the one this rule reads.
    """
    rom = built()["rom"]
    out = []
    for r in census()["reads"]:
        order = [(i, n, args) for i, (n, args) in enumerate(r.run.calls) if n in (APPEARANCE, LEADER)]
        leaders = [(i, args[0]) for i, n, args in order if n == LEADER and args]
        if not leaders:
            continue
        for i, n, args in order:
            if n != APPEARANCE or len(args) < 2 or any(args[0] == who for _, who in leaders) \
                    or any(j < i for j, _ in leaders):
                continue
            entry = entry_of_set(rom, args[1])
            if entry is None or not is_transformed(rom, entry):
                continue
            out.append((r.at, f"{r!r} runs appearance(character={args[0]}, set={args[1]}), entry {entry}, "
                              f"before leader({leaders[0][1]}), so appearance_revert undoes it"))
    return out


def npc_sets_our_records_still_name() -> list:
    """Rule 4: a record our modules own names no NPC set the design moved onto set 0.

    find_actor_by_set @0x08009370 special-cases set 0 and reaches the player whichever character he is, so
    a scene that hands the fight to the player addresses set 0, not the NPC's own set.
    """
    out = []
    for r in census()["reads"]:
        if r.owner is None:
            continue
        for n, args in r.run.calls:
            if n in SET_OPS and args and args[0] in MOVED_ONTO_PLAYER:
                out.append((r.at, f"{r!r} runs {S.op_name(n)}{args}: set {args[0]} is on set 0 now "
                                  f"({MOVED_ONTO_PLAYER[args[0]]})"))
    return out


def bars_without_the_hud() -> list:
    """Rule 5: a BATTLE START that shows a bar also runs header_bit1(1).

    The template rom:0x3E9384 ends camera_follow(0) ; header_bit1(1) ; bar_set(30,60,100). A bar with no
    HUD leaves the player fighting blind.

    SCOPED 2026-11-06 to a record that shows a bar AND either loads a map or sits in a table that ran
    header_bit1(0). The unscoped rule read 13 records and all 12 vanilla ones were legitimate: each
    raises a bar part way through a scene that never took the HUD away, such as a second boss arriving,
    so there was no HUD to put back and none of their tables runs header_bit1(0) anywhere. Every vanilla
    record that DID sit in a table which hid the HUD already runs header_bit1(1), with no exception. The
    HUD is read per TABLE, like the camera and unlike the cover, because header_bit1(0) is a latch the
    scene holds until something turns it back on, not a one-shot transition.
    """
    out = []
    for t in census()["tables"]:
        hidden = (0,) in t.run.called(HUD_ON)
        for r in t.reads:
            if not any(r.run.called(n) for n in BAR_OPS) or (1,) in r.run.called(HUD_ON):
                continue
            if not hidden and not any(r.run.called(n) for n in H.MAP_LOAD_OPS):
                continue
            shown = ", ".join(f"{S.op_name(n)}{a}" for n in BAR_OPS for a in r.run.called(n))
            why = "its table ran header_bit1(0)" if hidden else "it loads a map"
            out.append((r.at, f"{r!r} runs {shown} and no header_bit1(1), and {why}"))
    return out


def battle_starts_that_open_a_scene() -> list:
    """Rule 6: a record that shows a bar loads no map and opens no fade. That is the DEFAULT shape.

    Of the 30 records that raise a boss bar in this build, 22 are still vanilla and every one of those
    22 does neither: the talk ends, ext 104 turns the NPC into the enemy, the bar and the HUD come up and
    camera_follow(0) pans the view. The model is Piccolo against Android 17, rom:0x3E47DC. The owner,
    2026-11-06: "There should not be a fade at all after the diague! Dialogue ends fight begins with a
    camera pan to the user and the hud appearing, like every single fight int he game."

    The one vanilla record that loads a map with a bar is the template rom:0x3E9384, which really does
    open a scene on another map. A record like it declares a BATTLE_START_EXCEPTIONS entry.

    THIS RULE IS NOT ONE OF THE FIVE THE TEMPLATE DEFINES, which is why it lives in its own tuple:
    the template breaks it by design, and test_the_live_template_still_keeps_the_shape reads RULES.
    """
    out = []
    for r in census()["reads"]:
        if not any(r.run.called(n) for n in BAR_OPS):
            continue
        faults = [f"loads a map ({S.op_name(n)})" for n in H.MAP_LOAD_OPS if r.run.called(n)]
        faults += ["opens a fade"] if r.run.called(FADE_OUT) else []
        if faults:
            out.append((r.at, f"{r!r} shows a bar and {' and '.join(faults)}: the standard battle "
                              f"start does neither, so this record opens a scene"))
    return out


RULES = (naked_loads, cameras_not_handed_back, forms_lost_at_the_leader_change,
         npc_sets_our_records_still_name, bars_without_the_hud)
# Rule 6 is kept apart because the template DEFINES the five above and BREAKS this one.
DEFAULT_SHAPE_RULES = (battle_starts_that_open_a_scene,)
ALL_RULES = RULES + DEFAULT_SHAPE_RULES


def failing_records() -> set:
    """Every record offset that breaks a rule today, exceptions included."""
    return {at for rule in ALL_RULES for at, _ in rule()}


# ===== the five assertions =====

class BattleStartTests(unittest.TestCase):
    """One test an assertion, each over every record the census reached."""

    def test_map_load_is_covered(self):
        bad = _report(naked_loads())
        self.assertEqual(bad, [], "a battle start reveals its map load:" + _lines(bad))

    def test_camera_is_handed_back(self):
        bad = _report(cameras_not_handed_back())
        self.assertEqual(bad, [], "a scene that takes the camera gives it back:" + _lines(bad))

    def test_form_survives_the_leader_change(self):
        bad = _report(forms_lost_at_the_leader_change())
        self.assertEqual(bad, [], "an appearance set before a leader change survives it:" + _lines(bad))

    def test_player_ops_address_the_player(self):
        bad = _report(npc_sets_our_records_still_name())
        self.assertEqual(bad, [], "our own records address the player as set 0:" + _lines(bad))

    def test_control_record_shows_the_hud(self):
        bad = _report(bars_without_the_hud())
        self.assertEqual(bad, [], "a record that shows a bar shows the HUD:" + _lines(bad))

    def test_a_battle_start_opens_no_scene(self):
        """The sixth rule, and the one the owner asked for on 2026-11-06: "if anything can be built
        into our tooling so all future battles dont need this trouble again, just a standard battle
        start". A record that really does open a scene declares an exception and says why."""
        bad = _report(battle_starts_that_open_a_scene())
        self.assertEqual(bad, [], "a battle start loads a map or opens a fade:" + _lines(bad))


# ===== the census itself, and the deviation convention =====

class CensusTests(unittest.TestCase):
    def test_the_census_reads_the_builds_own_map_table(self):
        """battle_arena moves the map table, so the base ROM's 0x409368 would read the dead copy."""
        rom = built()["rom"]
        at, count = P.map_table(rom)
        self.assertEqual(at, built()["alloc"].notes["battle_arena"]["table"])
        self.assertEqual(count, P.MAP_COUNT + 1)

    def test_the_census_reaches_the_template_and_the_ending_table(self):
        """The two places the specification is written from must both be in the census, or the counts prove
        nothing. cellgames_ssj copies the vanilla template rom:0x3E9384 into the expansion area and repoints
        the table word, so the LIVE build holds the copy, not the vanilla address."""
        notes = built()["alloc"].notes["cellgames_ssj"]
        key = next(k for k, src in notes["sources"].items() if src == TEMPLATE)
        reads = {r.at for r in census()["reads"]}
        self.assertIn(notes["records"][key], reads, "the Cell Games start is not in the census")
        self.assertIn(0x3B8140, {t.at for t in census()["tables"]}, "the ending table is not in the census")

    def test_the_live_template_still_keeps_the_shape(self):
        """The record the FIVE rules were read from passes all five of them. If this ever fails, those
        rules are wrong, not the record. Rule 6 is not read here and is not one of the five: the
        template is the one vanilla record that loads a map with a bar, so it breaks rule 6 by
        definition and cellgames_ssj declares that."""
        notes = built()["alloc"].notes["cellgames_ssj"]
        key = next(k for k, src in notes["sources"].items() if src == TEMPLATE)
        at = notes["records"][key]
        broken = [why for rule in RULES for bad_at, why in rule() if bad_at == at]
        self.assertEqual(broken, [], "the template breaks a rule it defines:" + _lines(broken))

    def test_the_vanilla_bar_records_all_keep_the_default_shape(self):
        """The claim rule 6 stands on, counted over the live build: every bar record that is still
        vanilla loads no map and opens no fade. The only record of the whole census that does either
        is the template, which one of our own modules now owns a copy of."""
        bars = [r for r in census()["reads"] if any(r.run.called(n) for n in BAR_OPS)]
        broken = {at for at, _ in battle_starts_that_open_a_scene()}
        self.assertEqual([r for r in bars if r.owner is None and r.at in broken], [])
        # 31, not the 22 of 2026-11-06. Nine more are reached because the census now walks with
        # S.table_length(): the old walk stopped at a table's first END entry and never saw them.
        # The claim above is what matters and it held over the wider set: not one of the 31 opens
        # a scene. Counting more records made the rule stronger, not weaker.
        self.assertEqual(len([r for r in bars if r.owner is None]), 31, [repr(r) for r in bars])

    def test_the_two_appearance_literals_point_at_tables_the_build_owns(self):
        """The narrowed rule 3 stands on these two words. If a module ever repoints one and not the
        other, or the stride stops matching, the rule reads the wrong flags and goes quiet."""
        rom = built()["rom"]
        lookup = appearance_table(rom, SET_LOOKUP_LITERAL)
        revert = appearance_table(rom, REVERT_LITERAL)
        self.assertEqual(lookup, built()["alloc"].notes["gohan_gi"]["appearance_copy"])
        for at in (lookup, revert):
            self.assertTrue(0 < at < len(rom))
        for e in range(APPEARANCE_ENTRIES):            # both tables agree on flags and set id today
            self.assertEqual(rom[lookup + APPEARANCE_SIZE * e], rom[revert + APPEARANCE_SIZE * e], e)
            self.assertEqual(rom[lookup + APPEARANCE_SIZE * e + 1],
                             rom[revert + APPEARANCE_SIZE * e + 1], e)

    def test_the_narrowed_rule_3_reads_the_forms_the_design_depends_on(self):
        """Trunks' Super Saiyan is entry 16, set 133, transformed, so an ext 73 on it before a leader
        change that does NOT name him would be undone. Gohan's base entry 0, set 53, is not."""
        rom = built()["rom"]
        self.assertEqual(entry_of_set(rom, 133), 16)
        self.assertTrue(is_transformed(rom, 16))
        self.assertEqual(entry_of_set(rom, 53), 0)
        self.assertFalse(is_transformed(rom, 0))
        self.assertIsNone(entry_of_set(rom, 0xFE))

    def test_the_scoped_rule_5_reads_the_battle_starts_and_not_the_mid_fight_bars(self):
        """The scope is the claim: a record that shows a bar AND either loads a map or sits in a table
        that hid the HUD. Counted over the live build, so a module that adds a bar shows up here."""
        in_scope = []
        for t in census()["tables"]:
            hidden = (0,) in t.run.called(HUD_ON)
            for r in t.reads:
                if any(r.run.called(n) for n in BAR_OPS) and (
                        hidden or any(r.run.called(n) for n in H.MAP_LOAD_OPS)):
                    in_scope.append(r)
        # 17. The ending's own record F is BACK in scope since 2026-11-08, and it came back by the
        # second half of the rule, not the first: it still loads no map, but record A now runs
        # header_bit1(0) so that the owner's "Three years later..." caption box opens on a clean
        # black screen, and that puts every bar record of table rom:0x3B8140 in scope. Record F
        # raises the bar and runs header_bit1(1), so rule 5 reads it and passes.
        # The other 16: celljr_fight's copy of table rom:0x3EA400, allocated at rom:0x93AE74, has
        # its first END entry at index 2, so the old walk read 2 of its 33 words and never checked
        # 31 records of our OWN module. Word 31 still names the vanilla record rom:0x3EA3EC, which
        # is why that one record is in scope under two tables.
        self.assertEqual(len(in_scope), 17, [repr(r) for r in in_scope])

    def test_every_record_the_census_reached_was_read_whole(self):
        """scene_harness raises on an op it does not model, so a silently skipped record cannot happen.
        This pins that nothing in the live build is unreadable, which is what lets the counts mean anything.
        """
        c = census()
        self.assertGreater(len(c["reads"]), 2000)
        for r in c["reads"]:
            self.assertEqual(len(r.run.calls), len(r.run.screen_covered), repr(r))


class ExceptionConventionTests(unittest.TestCase):
    """A module may declare a record that breaks the shape on purpose. Four records do, all of them
    scene openings under rule 6; the fixtures below test the support without relying on them."""

    def test_exactly_the_four_scene_openings_are_declared(self):
        """Every declared exception, named and counted. The brief expected ONE record to break rule 6,
        the ending's own record F. Measured over the live build it was five, and the other four are
        legitimate: cellgames_ssj owns the copy of the one vanilla record that loads a map with a bar,
        and celljr_fight's three relay records really do open a scene between Cell Jr rounds. Record F
        is not here: v7 took its load and its fade away, so it keeps the default shape."""
        got = {at: module for at, (module, _) in declared_exceptions().items()}
        self.assertEqual(sorted(got.values()),
                         ["cellgames_ssj", "celljr_fight", "celljr_fight", "celljr_fight"])
        self.assertEqual(set(got), {at for at, _ in battle_starts_that_open_a_scene()})
        self.assertNotIn(built()["alloc"].notes["ending_fight"]["fight"], got)

    def test_a_note_path_resolves_to_this_builds_own_offset(self):
        """A real entry names a note, not a number, because an allocated record moves whenever an
        earlier module's allocation does."""
        notes = built()["alloc"].notes
        self.assertEqual(note_path("celljr_fight", "seq31"), notes["celljr_fight"]["seq31"])
        self.assertEqual(note_path("cellgames_ssj", "records.fight_cell_seq21"),
                         notes["cellgames_ssj"]["records"]["fight_cell_seq21"])
        self.assertEqual(note_path("celljr_fight", "relays.0x3E9E24"),
                         notes["celljr_fight"]["relays"][0x3E9E24])
        with self.assertRaises(KeyError):
            note_path("celljr_fight", "no_such_note")

    def test_a_declared_exception_is_read_from_the_module(self):
        at = built()["alloc"].notes["ending_fight"]["fight"]
        got = declared_exceptions({"ending_fight": {at: "the arena start, pending the cover fix"}})
        self.assertEqual(got, {at: ("ending_fight", "the arena start, pending the cover fix")})

    def test_an_exception_whose_module_did_not_write_the_record_is_stale(self):
        at = built()["alloc"].notes["ending_fight"]["fight"]
        declared = declared_exceptions({"celljr_fight": {at: "not mine"}})
        bad = stale_exceptions(declared, {at})
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("did not write it", bad[0])

    def test_an_exception_for_a_record_that_breaks_no_rule_is_stale(self):
        at = built()["alloc"].notes["ending_fight"]["fight"]
        declared = declared_exceptions({"ending_fight": {at: "fixed long ago"}})
        bad = stale_exceptions(declared, set())
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("breaks no rule any more", bad[0])

    def test_a_live_exception_is_not_stale(self):
        at = built()["alloc"].notes["ending_fight"]["fight"]
        declared = declared_exceptions({"ending_fight": {at: "the arena start, pending the cover fix"}})
        self.assertEqual(stale_exceptions(declared, {at}), [])

    def test_the_build_declares_no_stale_exception(self):
        """The real check, over whatever the modules declare today and whatever still breaks a rule."""
        self.assertEqual(stale_exceptions(declared_exceptions(), failing_records()), [])


# ===== the emitter writes what the checker asks for =====

class DefaultEmitterTests(unittest.TestCase):
    """scene_lib.battle_start() is the DEFAULT shape, four ops, and it must break none of the rules."""

    def _run(self, **kwargs):
        record = S.code(1, S.battle_start(**kwargs))
        pad = bytes(0x100)
        return H.run_record(pad + record + pad, len(pad))

    def test_the_default_is_the_piccolo_record(self):
        """rom:0x3E47DC, map 11,4 word 6, the record the owner pointed at:
        ext104(9,1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0)."""
        run = self._run(enemy_set=9, enemy_item=1, bar=9, bar_range=(75, 100))
        self.assertEqual(run.ops_run, ["ext104", "bar_set", "header_bit1", "camera_follow"])
        self.assertEqual(run.called(104), [(9, 1)])
        self.assertEqual(run.called(90), [(9, 75, 100)])

    def test_the_default_loads_no_map_and_opens_no_fade(self):
        """The whole point of the shape. A record that needs either is a scene opening, and
        battle_start_that_opens_a_scene emits that instead."""
        run = self._run(enemy_set=28, enemy_item=1, bar=28)
        self.assertEqual([n for n in H.MAP_LOAD_OPS if run.called(n)], [])
        self.assertEqual(run.called(FADE_OUT), [])
        self.assertEqual(run.called(41), [])
        self.assertEqual(run.ops_run, ["ext104", "bar_show", "header_bit1", "camera_follow"])

    def test_the_default_hands_the_camera_back_and_shows_the_hud(self):
        run = self._run(enemy_set=28, enemy_item=1, bar=28)
        self.assertIn(run.camera_owner, H.HANDS_BACK)
        self.assertIn((1,), run.called(HUD_ON))

    def test_a_single_round_boss_gets_the_whole_bar(self):
        """ext 85 draws the whole bar; ext 90 adds a display segment for one round of a multi-round
        boss. Without bar_range the emitter must pick ext 85."""
        self.assertEqual(self._run(enemy_set=28, enemy_item=1, bar=28).ops_run[1], "bar_show")
        self.assertEqual(self._run(enemy_set=28, enemy_item=1, bar=28,
                                   bar_range=(50, 100)).ops_run[1], "bar_set")

    def test_the_default_can_leave_the_hud_and_the_camera_out(self):
        run = self._run(enemy_set=28, enemy_item=1, bar=28, hud=False, follow=None)
        self.assertEqual(run.ops_run, ["ext104", "bar_show"])

    def test_the_default_refuses_to_replace_the_player(self):
        """ext 104 destroys the actor it finds. Set 0 is the player, so naming him would delete him."""
        with self.assertRaises(ValueError):
            S.battle_start(enemy_set=0, enemy_item=1, bar=28)

    def test_the_default_refuses_a_bar_range_with_no_boss(self):
        with self.assertRaises(ValueError):
            S.battle_start(enemy_set=28, enemy_item=1, bar_range=(50, 100))


class EmitterTests(unittest.TestCase):
    """scene_lib.battle_start_that_opens_a_scene() must pass the same five assertions it was written
    from. It breaks rule 6 on purpose, which is what an exception is for."""

    def _open(self, **kwargs):
        record = S.code(1, S.battle_start_that_opens_a_scene(**kwargs))
        pad = bytes(0x100)
        return H.run_record(pad + record + pad, len(pad))

    def test_battle_start_emits_the_templates_order(self):
        """The template, less ext84 and set_flag, which belong to the scene and not to the shape."""
        run = self._open(leader_who=0, zone=14, area=3, var=1, player_xy=(368, 440), facing=3,
                        frame_xy=(328, 344), frame_speed=10, hold=60, cover=("fade", 120),
                        bar=30, bar_range=(60, 100), spawn_list=[(60, 552, 96)])
        self.assertEqual(run.ops_run, ["fade_out", "load_map_at", "leader", "face", "camera", "spawn",
                                       "fade_in", "wait", "camera_follow", "header_bit1", "bar_set"])

    def test_battle_start_covers_its_map_load_and_hands_the_camera_back(self):
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 456), bar=28)
        self.assertEqual(run.cover_at("load_map_at"), [H.COVER_OPEN])
        self.assertIn(run.camera_owner, H.HANDS_BACK)
        self.assertIn((1,), run.called(HUD_ON))

    def test_battle_start_sets_the_form_before_the_leader_change(self):
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 456), bar=28, appearance=(3, 133))
        order = [n for n, _ in run.calls if n in (APPEARANCE, LEADER)]
        self.assertEqual(order, [APPEARANCE, LEADER])
        self.assertEqual(run.called(APPEARANCE), [(3, 133)])

    def test_battle_start_can_put_the_form_in_front_of_the_map_load(self):
        """form_before_load=True is for a scene where the leader REALLY changes. ext 70 writes the party
        roster, but the block that installs the new leader's BODY is guarded (sub_0800A680: CMP r4,#0
        then BEQ on Sprite_CurrentDirectory 0x03001FA8), so the following map load is what builds the
        player from the roster. The template's own leader(0) names a character who already leads, so it
        never proved the other order for a real change. The record still covers its load and still hands
        the camera back."""
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 492), frame_speed=2, bar=28, appearance=(3, 133),
                        form_before_load=True)
        self.assertEqual(run.ops_run, ["fade_out", "appearance", "leader", "load_map_at", "face",
                                       "camera", "fade_in", "wait", "camera_follow", "header_bit1",
                                       "bar_show"])
        self.assertEqual(run.cover_at("load_map_at"), [H.COVER_OPEN])
        self.assertIn(run.camera_owner, H.HANDS_BACK)

    def test_form_before_load_does_not_change_the_default_output(self):
        """The gate on scene_lib: a new option must never move what the modules already write."""
        same = dict(leader_who=0, zone=14, area=3, var=1, player_xy=(368, 440), facing=3,
                    frame_xy=(328, 344), frame_speed=10, bar=30, bar_range=(60, 100),
                    appearance=(0, 158))
        same_again = S.battle_start_that_opens_a_scene(**same)
        self.assertEqual(same_again,
                         S.battle_start_that_opens_a_scene(**same, form_before_load=False))
        self.assertNotEqual(same_again,
                            S.battle_start_that_opens_a_scene(**same, form_before_load=True))

    def test_battle_start_with_a_flash_cover_uses_the_flash_ops(self):
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 456), cover=("flash", 40))
        self.assertEqual(run.ops_run[0], "palette_fx")
        self.assertEqual(run.cover_at("load_map_at"), [H.COVER_OPEN])
        self.assertIn("flash_wait", run.ops_run)

    def test_battle_start_without_a_cover_is_what_the_checker_fails(self):
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 456), bar=28, cover=None)
        self.assertEqual(run.cover_at("load_map_at"), [H.COVER_CLEAR])

    def test_battle_start_never_emits_camera_follow_when_follow_is_none(self):
        run = self._open(leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                        frame_xy=(136, 456), follow=None)
        self.assertEqual(run.called("camera_follow"), [])
        self.assertEqual(run.camera_owner, H.CAMERA_FIXED)

    def test_battle_start_refuses_to_spawn_the_player(self):
        """ext 51 is the one actor op that cannot address the player: npc_factory @0x0800D6DE never calls
        find_actor_by_set and builds a new NPC instead."""
        with self.assertRaises(ValueError):
            S.battle_start_that_opens_a_scene(
                leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                frame_xy=(136, 456), spawn_list=[(0, 1, 2)])

    def test_battle_start_refuses_an_unknown_cover(self):
        with self.assertRaises(ValueError):
            S.battle_start_that_opens_a_scene(
                leader_who=3, zone=6, area=100, var=1, player_xy=(248, 568), facing=1,
                frame_xy=(136, 456), cover=("wipe", 10))


if __name__ == "__main__":
    unittest.main()
