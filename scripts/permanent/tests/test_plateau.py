r"""
test_plateau.py - The plateau trial: map 7,100, the map the OWNER composed in the map editor.

The module is built once for the whole class, on top of the trial chain it needs, and every test
reads the RESULT. A test that only re-ran the module's own arithmetic would prove nothing.

The strongest test here is test_the_rom_gives_his_document_back: map_file.read_map on the built ROM
has to equal art\plateau\map_142.json field for field. That one proves the patch lays HIS map, and
it is why no test in this file describes a tile, a lip or a rock formation any more.
"""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "map-editor"))

import log2_build  # noqa: E402
from patches import plateau  # noqa: E402

import map_file  # noqa: E402
import tile_stream  # noqa: E402
from scene import map_view  # noqa: E402
from scene import scene_probe  # noqa: E402
import scene.scene_lib as S  # noqa: E402
from scene.scene_lib import ext  # noqa: E402

ROM_BASE = 0x08000000
MAP_SIZE = 56
# The dialog box: 4 lines of 144 px a page (bible C4S and B2095), on the font at rom:0x2CC64. The
# widest box the ending talk renders in vanilla is 294 px, ending word 3.
DIALOG_FONT, DIALOG_WIDTH, BOX_LINES, WIDEST_VANILLA_BOX = 0x2CC64, 0x90, 4, 294


def _dialog_wrap(rom, box):
    """Lines of one box as the dialog line counter breaks them: past 144 px, at the last space.

    The same model test_chapter_cards uses, which reproduces every vanilla box."""
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


def _ops(rom, at):
    """[(ext number, pushed arguments)] of a type 0 record, which is how these records are written.

    Every op of a record this module writes is a push or an ext op, so the stack before each ext op
    is exactly that op's own arguments. A record with a branch would need the evaluator
    test_future_androids carries; none here has one."""
    out, stack = [], []
    for op in S.ops(rom, at + 3, S.record_end(rom, at)):
        if op.ext is not None:
            out.append((op.ext, tuple(stack)))
            stack = []
        elif op.op in (0, 1, 29):
            stack += list(op.args)
        elif op.op == 17:
            break
        else:
            raise AssertionError(f"rom:0x{at:X} carries base op {op.op}, which _ops cannot read")
    return out


def _vanilla_transition() -> dict:
    """The fade pair of vanilla's own fastest map-load transition, read out of the BASE ROM.

    `plateau.FAST_TRANSITION` names the record. The walk stops at its fade in, because what follows
    carries base ops this file's reader has no reason to understand. `waits` totals every blocking
    wait between the two fades, and vanilla spends none here."""
    rom = log2_build.BASE.read_bytes()
    at = plateau.FAST_TRANSITION
    out, stack = {"out": None, "in": None, "waits": 0}, []
    for op in S.ops(rom, at + 3, S.record_end(rom, at)):
        if op.ext is None:
            if op.op in (0, 1, 29):
                stack += list(op.args)
            continue
        args, stack = tuple(stack), []
        if op.ext == 40 and out["out"] is None:
            out["out"] = args[0]
        elif op.ext == 69 and out["out"] is not None:
            out["waits"] += args[0]
        elif op.ext == 41 and out["out"] is not None:
            out["in"] = args[0]
            break
    return out


CHAIN = ["battle_arena", "ending_fight", "future_androids", "plateau"]


def _build():
    before, _ = log2_build.assemble(log2_build.BASE, CHAIN[:-1])
    rom, alloc = log2_build.assemble(log2_build.BASE, CHAIN)
    return bytes(before), rom, alloc.notes["plateau"]


class PlateauTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before, cls.rom, cls.notes = _build()

    # ----- the map entry -----

    def test_the_entry_is_map_7_100_with_one_variation(self):
        at = self.notes["entry"]
        self.assertEqual((self.rom[at], self.rom[at + 1], self.rom[at + 2]), (7, 100, 1))

    def test_the_entry_carries_no_region_and_no_door(self):
        at = self.notes["entry"]
        self.assertEqual(self.rom[at + 3], 0, "region count")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x10)[0], 0, "region list")
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + 0x40)[0], 0, "layout door count")
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + 0x44)[0], 0, "layout door list")

    def test_the_entry_carries_combat_the_blank_banner_the_music_and_its_own_items(self):
        at = self.notes["entry"]
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x08)[0], 1, "combat")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x0C)[0], 0xDD, "banner")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x24)[0], plateau.ROUND1_MUSIC,
                         "music: the song round 1 is playing, so the load does not restart it")
        self.assertEqual(self.rom[at + 4], 2, "item count")
        self.assertEqual(struct.unpack_from("<I", self.rom, at + 0x14)[0] - ROM_BASE,
                         self.notes["items"])

    def test_the_entry_is_the_live_arena_entry_with_four_words_changed(self):
        """The zone, the ITEM LIST, the layout array and the music. The item list may not be shared:
        an item carries its own death event, and the two rounds have to end differently."""
        at = self.notes["entry"]
        _, arena_at = plateau.map_entry(self.rom, 6, 100)
        ours = bytearray(self.rom[at:at + MAP_SIZE])
        theirs = bytearray(self.rom[arena_at:arena_at + MAP_SIZE])
        self.assertNotEqual(ours[0x14:0x18], theirs[0x14:0x18], "the item list must be its own")
        self.assertNotEqual(ours[0x24:0x28], theirs[0x24:0x28], "the music must be its own")
        ours[0] = theirs[0]
        ours[0x14:0x18] = theirs[0x14:0x18]
        ours[0x24:0x28] = theirs[0x24:0x28]
        ours[0x2C:0x30] = theirs[0x2C:0x30]
        self.assertEqual(bytes(ours), bytes(theirs))

    # ----- the layout -----

    def test_the_layout_writes_the_camera_pair_his_world_asks_for(self):
        """The pair is `world - 239` and `world - 159`, COMPUTED from his 864 x 816 px world, never
        taken from his 1280 x 1024 px block grid. A grid pair is the fault that once stopped the
        camera 170 px short of walkable ground."""
        doc = plateau.document()
        got = struct.unpack_from("<HH", self.rom, self.notes["layout"] + plateau.L_CLAMP)
        self.assertEqual(got, map_file.camera_pair(*doc["world"]))
        self.assertEqual(got, self.notes["clamp"])
        grid = (doc["blocks"][0] * 256, doc["blocks"][1] * 256)
        self.assertNotEqual(got, map_file.camera_pair(*grid),
                            "the block grid is not the world, and only the world sets the camera")

    def test_the_layout_carries_his_own_animated_tile_groups(self):
        doc = plateau.document()
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_ANIM_COUNT)[0],
                         len(doc["animated"]))
        groups = scene_probe.layout_groups(self.rom, lay)
        self.assertEqual([g["first"] for g in groups], [g["first"] for g in doc["animated"]])
        for got, want in zip(groups, doc["animated"]):
            self.assertEqual([f["duration"] for f in got["frames"]],
                             [f["duration"] for f in want["frames"]])
            self.assertEqual([bytes(f["pixels"]) for f in got["frames"]],
                             [bytes(f["pixels"]) for f in want["frames"]])

    def test_the_layout_names_his_chunk_table_and_writes_his_own_tile_stream(self):
        """The chunk table is the one HIS document names, so every (chunk, tile) pair means the art
        he drew with. The +0x48 stream is this map's own, written from his pairs in his order."""
        doc = plateau.document()
        lay = self.notes["layout"]
        self.assertEqual(struct.unpack_from("<I", self.rom, lay + plateau.L_TILE_TABLE)[0],
                         doc["chunk_table"])
        self.assertEqual([list(p) for p in tile_stream.decode_stream(self.rom, lay + ROM_BASE)],
                         [list(p) for p in doc["tiles"]])

    def test_the_layout_drops_the_doors_and_the_props(self):
        lay = self.notes["layout"]
        for off in (plateau.L_PROP_COUNT, plateau.L_PROP_LIST,
                    plateau.L_WARP_COUNT, plateau.L_WARP_LIST):
            self.assertEqual(struct.unpack_from("<I", self.rom, lay + off)[0], 0)

    def test_all_four_layers_carry_his_own_block_grid(self):
        doc = plateau.document()
        for off in (plateau.L_BG0, plateau.L_BG1, plateau.L_BG2, plateau.L_BG3):
            rec = struct.unpack_from("<I", self.rom, self.notes["layout"] + off)[0] - ROM_BASE
            self.assertEqual([self.rom[rec + plateau.LAYER_GRID],
                              self.rom[rec + plateau.LAYER_GRID + 1]], doc["blocks"])
            self.assertEqual(struct.unpack_from("<I", self.rom, rec)[0], plateau.LAYER_CLASS)

    def test_his_layer_priorities_are_written_exactly_as_he_set_them(self):
        """BG0 and BG1 are priority 1 on his map, so what they draw stands IN FRONT of the player,
        and BG2 and BG3 are priority 3 and draw behind him. All four are kept: it is his map."""
        doc = plateau.document()
        lay = self.notes["layout"]
        for bg, name in enumerate(map_file.LAYER_NAMES):
            self.assertEqual(self.rom[lay + map_file.L_PRIORITY + bg],
                             doc["layers"][name]["priority"], name)
        self.assertEqual(self.notes["priorities"], {"bg0": 1, "bg1": 1, "bg2": 3, "bg3": 3})

    # ----- the collision -----

    def test_the_collision_frame_is_his_own_cell_for_cell(self):
        doc = plateau.document()
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        self.assertEqual(len(bits), plateau.FRAME_SIZE)
        self.assertEqual(bits, bytes(doc["collision"]))
        self.assertEqual(len(plateau.open_cells(doc)), self.notes["open_cells"])

    def test_the_terrain_frame_is_his_own_too(self):
        terrain = plateau._frame(self.rom, self.notes["terrain"] + ROM_BASE)
        self.assertEqual(terrain, bytes(plateau.document()["terrain"]))

    def test_no_walkable_cell_touches_the_world_edge(self):
        """The camera stops at the world edge, so walkable ground there would show him the void."""
        doc = plateau.document()
        world = doc["world"]
        edge = [c for c in plateau.open_cells(doc)
                if c[0] == 0 or c[1] == 0
                or (c[0] + 1) * 8 >= world[0] or (c[1] + 1) * 8 >= world[1]]
        self.assertEqual(edge, [])

    def test_both_round_two_spots_stand_on_reachable_open_ground(self):
        """His map seals one pocket inside the rock ring on purpose, so the rule is that the pair
        shares ONE walkable region, not that every open cell is reachable."""
        doc = plateau.document()
        bits = plateau._frame(self.rom, self.notes["collision"] + ROM_BASE)
        opened = plateau.open_cells(doc)
        reach = plateau.reachable(opened, (plateau.PLATEAU_CELL_SPOT[0] // 8,
                                           plateau.PLATEAU_CELL_SPOT[1] // 8))
        self.assertEqual(len(reach), self.notes["reachable"])
        self.assertEqual(len(opened) - len(reach), self.notes["pocket_cells"])
        for spot, env, who in plateau.PLATEAU_SPOTS:
            for cx, cy in plateau.envelope_cells(spot, env):
                self.assertTrue(plateau.is_open(bits, cx, cy),
                                f"{who} at {spot} draws into the closed cell ({cx},{cy})")
                self.assertIn((cx, cy), reach, f"{who} at {spot} is sealed off at ({cx},{cy})")

    def test_his_arena_gives_more_room_than_the_cell_games_arena(self):
        # Map 14,3 holds 4810 open cells in a 696 x 632 px box (22_arena_size.txt).
        x0, y0, x1, y1 = self.notes["open_box"]
        self.assertGreater(self.notes["open_cells"], 4810)
        self.assertGreaterEqual(x1 - x0 + 1, 696)
        self.assertGreaterEqual(y1 - y0 + 1, 632)

    # ----- the round split (rung 5) -----

    def test_record_a_still_loads_the_arena(self):
        """Rung 5 moved the plateau off ending word 13. The talk and round 1 stay on map 6,100, which
        the owner play tested: "we already built that whole thing"."""
        self.assertEqual(self.rom.count(plateau.ARENA_LOAD), self.before.count(plateau.ARENA_LOAD),
                         "no copy of the arena load was rewritten")
        self.assertEqual(self.rom.count(ext(39, 7, 100, 1, *plateau.TRUNKS_START)), 0,
                         "nothing loads the plateau at the old spot any more")

    def test_every_word_that_named_record_f_now_names_round_1(self):
        """Three words name it, not one: future_androids gives each android enemy a COPY of the live
        ending table, and after a real fight the scene runs out of THAT copy's word 23."""
        want = struct.pack("<I", self.notes["round1"] + ROM_BASE)
        self.assertGreaterEqual(len(self.notes["fight_words"]), 1)
        for word in self.notes["fight_words"]:
            self.assertEqual(bytes(self.rom[word:word + 4]), want, hex(word))

    def test_round_1_is_the_standard_battle_start_with_the_top_half_of_the_bar(self):
        """Track 28 opens it. The owner, design section 3: "Track 28 plays when the battle starts"."""
        self.assertEqual(_ops(self.rom, self.notes["round1"]),
                         [(49, (plateau.ROUND1_MUSIC,)),
                          (104, (28, 1)), (90, (28, 50, 100)), (86, (1,)), (33, (0,))])
        self.assertEqual(plateau.ROUND1_MUSIC, 28)

    def test_the_split_is_round_1s_death_and_opens_the_plateau_arrival(self):
        """The owner's beat: ping, white flash, Cell punched off screen, Trunks flies after him, then
        the plateau loads and the arrival scene plays."""
        self.assertEqual(struct.unpack_from("<I", self.rom, self.notes["arena_table"])[0],
                         self.notes["split"] + ROM_BASE, "table D word 0 is the split")
        ops = _ops(self.rom, self.notes["split"])
        names = [n for n, _ in ops]
        self.assertEqual(ops[:4], [(88, ()), (86, (0,)), (46, (60,)), (42, (10,))])
        self.assertIn((39, (7, 100, 1) + plateau.PLATEAU_FLY_FROM), ops)
        self.assertIn((136, (28,) + plateau.PUNCHED_TO + (plateau.KNOCK_N,)), ops)
        self.assertIn((121, (0, plateau.FLY_STATE)), ops)
        self.assertIn((136, (0,) + plateau.FLIES_TO + (plateau.FLY_N,)), ops)
        self.assertLess(names.index(40), names.index(39), "the load runs under a fade")
        self.assertLess(names.index(39), names.index(41), "and the screen comes back after it")
        self.assertNotIn(104, names, "round 2 arms in its own record, after the talk")

    def test_the_arrival_shows_cell_down_then_trunks_flies_in_from_the_west(self):
        """The owner, 2026-11-08: "with cell in a down state, trunks flies in (from the left), cell
        stands up, placeholder convo, then fight continues".

        Order is the whole test. `ext 136` blocks outside a group (handler @0x0800A346 ends in
        BL actor_queue @0x0800E04C), so Trunks really lands before Cell stands."""
        ops = _ops(self.rom, self.notes["split"])
        flat = [(n, a) for n, a in ops]
        load = flat.index((39, (7, 100, 1) + plateau.PLATEAU_FLY_FROM))
        after = flat[load:]
        want = [(52, (28,)),
                (51, (28,) + plateau.PLATEAU_CELL_SPOT),
                (55, (28, plateau.WEST)),
                (57, (28, plateau.DOWN_STATE)),
                (55, (0, plateau.EAST)),
                (121, (0, plateau.FLY_STATE)),
                (31, plateau.PLATEAU_VIEW),
                (41, (plateau.SPLIT_FADE,))]
        here = [after.index(op) for op in want]
        self.assertEqual(here, sorted(here), "the staging has to finish before the fade in")
        reveal = after.index((41, (plateau.SPLIT_FADE,)))
        land = after.index((136, (0,) + plateau.PLATEAU_TRUNKS_SPOT + (plateau.ARRIVE_SPEED,)))
        stand = after.index((121, (28, plateau.STAND_STATE)))
        self.assertLess(reveal, land, "the screen is back before he flies in")
        self.assertLess(land, stand, "he lands before Cell stands up")
        self.assertLess(plateau.PLATEAU_TRUNKS_SPOT[0], plateau.PLATEAU_CELL_SPOT[0],
                        "Trunks on the left, Cell on the right")
        self.assertEqual(plateau.PLATEAU_TRUNKS_SPOT[1], plateau.PLATEAU_CELL_SPOT[1], "one row")
        self.assertLess(plateau.PLATEAU_FLY_FROM[0], plateau.PLATEAU_TRUNKS_SPOT[0], "from the west")
        self.assertLess(plateau.PLATEAU_FLY_FROM[0] + plateau.TRUNKS_ENVELOPE_LR[1],
                        plateau.PLATEAU_VIEW[0], "and from off screen")

    def test_the_hand_off_runs_vanillas_fastest_transition_and_no_settle_wait(self):
        """The owner: "what is the normal transition length in vanilla???" and, twice more, that
        this one is still too long. The answer is not a number this project picked. It is read out
        of the BASE ROM here: rom:0x3E424A is vanilla's fastest map-load transition, and both of
        this hand-off's fades have to equal its own two.

        No wait may run between the load and the fade in, because 0x3E424A spends none either, and
        `ext 57 (28, 3)` is staging, not a load margin: the cover finishes before the load runs."""
        want = _vanilla_transition()
        self.assertEqual(want, {"out": 30, "in": 30, "waits": 0},
                         f"rom:0x{plateau.FAST_TRANSITION:X} is no longer the fast transition")
        ops = _ops(self.rom, self.notes["split"])
        flat = [(n, a) for n, a in ops]
        load = flat.index((39, (7, 100, 1) + plateau.PLATEAU_FLY_FROM))
        reveal = flat.index((41, (plateau.SPLIT_FADE,)))
        self.assertEqual(plateau.SPLIT_FADE, want["out"], "the cover is vanilla's own fade_out")
        self.assertEqual(plateau.SPLIT_FADE, want["in"], "the reveal is vanilla's own fade_in")
        self.assertEqual(flat[load - 1], (40, (plateau.SPLIT_FADE,)), "the cover is the same value")
        self.assertEqual([n for n, _ in flat[load + 1:reveal] if n == 69], [],
                         "no wait runs between the load and the fade in")
        self.assertFalse(hasattr(plateau, "LOAD_SETTLE"), "the settle is deleted, not shrunk")
        self.assertIn((57, (28, plateau.DOWN_STATE)), flat,
                      "Cell is posed down, and his 64 frames are staging under the black")

    def test_the_arrival_talk_is_the_owners_own_lines_then_round_2(self):
        """A type 0 record cannot carry text, so the split hands on to table D words 1 to 7. Table D
        already runs vanilla TEXT records from words 24 and 25.

        The chain runs in index order, 0 to 7, and each record hands on to the next index."""
        table = self.notes["arena_table"]
        spots = {0: self.notes["split"], plateau.TRANSFORM_INDEX: self.notes["transform"],
                 plateau.ROUND2_INDEX: self.notes["round2"]}
        spots.update(dict(zip(plateau.TALK_WORDS, self.notes["talk"])))
        for index in sorted((0,) + plateau.TALK_CHAIN):
            at = spots[index]
            self.assertEqual(struct.unpack_from("<I", self.rom, table + 4 * index)[0], at + ROM_BASE,
                             f"table D word {index}")
            want = plateau.END_INDEX if index == plateau.ROUND2_INDEX else index + 1
            self.assertEqual(struct.unpack_from("<H", self.rom, at)[0], want,
                             f"table D word {index} hands on to word {want}")

    def test_every_talk_record_carries_his_own_words_and_the_right_face(self):
        """Every character is his, quoted from the design of 2026-11-08, section 4. The only byte
        added is the box break 0x0B, and it only ever sits at a mark he wrote himself."""
        for at, (index, portrait, line) in zip(self.notes["talk"], plateau.TALK):
            self.assertEqual(self.rom[at + 2], 1, "a type 1 text record")
            self.assertEqual(self.rom[at + 3], portrait, f"table D word {index}")
            end = bytes(self.rom).index(b"\0", at + 4)
            self.assertEqual(bytes(self.rom[at + 4:end]).decode("ascii"), line)
            self.assertNotIn("PLACEHOLDER", line, "the placeholders are gone")
        said = [line for _, _, line in plateau.TALK]
        self.assertEqual(said[1], "Enough!")
        self.assertEqual(said[4], "But count me as the last!")

    def test_every_talk_box_stays_inside_the_widest_box_the_talk_renders(self):
        """The dialog box holds 4 lines of 144 px a page (bible B2095), and the widest box the ending
        talk renders in vanilla is 294 px. Three of his segments ran past that as one box and were
        split into two boxes at a mark he wrote, so the text is the same text."""
        for _index, _portrait, line in plateau.TALK:
            for box in line.split("\x0b"):
                lines = _dialog_wrap(self.before, box.encode("ascii"))
                self.assertLessEqual(sum(w for _, w in lines), WIDEST_VANILLA_BOX, box)
                self.assertLessEqual(len(lines), BOX_LINES, f"{box!r} pages on")

    def test_the_portrait_turns_super_saiyan_only_after_the_transform(self):
        """He is base Trunks until word 3 changes his body, so a Super Saiyan face before it would
        disagree with the sprite on screen."""
        before = [p for i, p, _ in plateau.TALK if i < plateau.TRANSFORM_INDEX]
        after = [p for i, p, _ in plateau.TALK if i > plateau.TRANSFORM_INDEX]
        self.assertEqual([p for p in before if p != plateau.CELL_PORTRAIT],
                         [plateau.TRUNKS_BASE_PORTRAIT])
        self.assertEqual([p for p in after if p != plateau.CELL_PORTRAIT],
                         [plateau.TRUNKS_SSJ_PORTRAIT, plateau.TRUNKS_SSJ_PORTRAIT])

    def test_the_transform_sets_the_base_body_before_it_poses_the_power_up(self):
        """Only the base set carries anim 9 (bible B2179), and the player may have transformed by
        hand in round 1. No scene op reads his form, so the record makes the body certain instead:
        ext 73 (3,132) in front, then the aura, the pose, the white flash and ext 73 (3,133)."""
        ops = _ops(self.rom, self.notes["transform"])
        self.assertEqual(ops, [(73, (3, 132)), (46, (55,)), (57, (0, 9)), (42, (10,)), (47, (55,)),
                               (73, (3, 133)), (43, (10,)), (55, (0, plateau.EAST))])
        self.assertLess(ops.index((57, (0, 9))), ops.index((73, (3, 133))),
                        "the power up has to play on the body that owns anim 9")
        self.assertLess(ops.index((42, (10,))), ops.index((73, (3, 133))))
        self.assertLess(ops.index((73, (3, 133))), ops.index((43, (10,))),
                        "the body swap hides under the white flash")

    def test_round_2_is_the_standard_battle_start_with_the_bottom_half_of_the_bar(self):
        """Track 35 opens it. The owner, design section 4: "Track 35 starts as the fight starts",
        and he changed the number himself: "track 35 instead of 15"."""
        self.assertEqual(_ops(self.rom, self.notes["round2"]),
                         [(49, (plateau.ROUND2_MUSIC,)),
                          (104, (28, 1)), (90, (28, 0, 50)), (86, (1,)), (33, (0,))])
        self.assertEqual(plateau.ROUND2_MUSIC, 35)
        self.assertEqual(struct.unpack_from("<H", self.rom, self.notes["round2"])[0], 26, "then END")

    def test_the_music_runs_unbroken_from_round_1_to_the_moment_round_2_starts(self):
        """His complaint: "the music transitions to a different track between capsule corp and the
        arena, that should not be the case", and his ruling: "yes it should be 28, no transition
        until 35 when the round 2 starts."

        `ext 39` reads the new map's +0x24 and restarts the music unless the new map names the
        record already playing (bible B1191, B2176, B2028). So the whole chain is read here, in the
        order it runs, and three things have to hold together:
          1. the plateau map's +0x24 is the song playing at the moment the split loads it, which is
             the last music op before that load;
          2. nothing between that load and the end of the arrival talk plays music or loads a map;
          3. round 2's own battle start plays 35, the ONE transition he asked to hear.
        Part 1 is what failed: the entry carried the arena's 38 and he heard 28, then 38, then 35."""
        music, load = 49, 39
        before = [args[0] for op, args in _ops(self.rom, self.notes["round1"]) if op == music]
        self.assertEqual(before, [plateau.ROUND1_MUSIC], "round 1 opens the chain with one cue")

        split = _ops(self.rom, self.notes["split"])
        loads = [k for k, (op, _a) in enumerate(split) if op in (38, load)]
        self.assertEqual(len(loads), 1, "the split loads exactly one map")
        self.assertEqual(split[loads[0]][1][:2], (plateau.PLATEAU_ZONE, plateau.PLATEAU_AREA))
        self.assertEqual([op for op, _a in split[:loads[0]] if op == music], [],
                         "nothing in the split changes the track before the load,"
                         " so round 1's cue is still what is playing")

        entry = struct.unpack_from("<I", self.rom, self.notes["entry"] + 0x24)[0]
        self.assertEqual(entry, plateau.ROUND1_MUSIC,
                         "the plateau map has to NAME the song playing, or the load restarts it")
        self.assertEqual(self.notes["plateau_music"], entry)

        after = list(split[loads[0] + 1:]) + _ops(self.rom, self.notes["transform"])
        for at in self.notes["talk"]:
            self.assertEqual(self.rom[at + 2], 1,
                             "each of his five lines is a TEXT record, which runs no script op")
        self.assertEqual([op for op, _a in after if op == music], [],
                         "the arrival and the transform leave the music alone")
        self.assertEqual([op for op, _a in after if op in (38, load)], [],
                         "and neither loads a map, which would read a +0x24 of its own")

        self.assertEqual([args[0] for op, args in _ops(self.rom, self.notes["round2"])
                          if op == music], [plateau.ROUND2_MUSIC],
                         "round 2's battle start is the one transition he wants")
        self.assertNotEqual(plateau.ROUND2_MUSIC, plateau.ROUND1_MUSIC, "and it is audible")

    def test_trunks_walks_to_cell_before_the_punch(self):
        """The owner, 2026-11-08: "trunks should walk to cell and punch him, not punch him a mile
        away". The staging drops him 64 px below Cell; the walk closes that to 24 px, which is
        celljr_fight's own melee gap. `ext 53` BLOCKS, so the punch cannot start early."""
        ops = _ops(self.rom, self.notes["split"])
        names = [n for n, _ in ops]
        self.assertIn((53, (0,) + plateau.PUNCH_FROM), ops, "the player walks in")
        walk = ops.index((53, (0,) + plateau.PUNCH_FROM))
        self.assertEqual(ops[walk + 1], (55, (0, plateau.UP)), "and is held facing Cell")
        self.assertLess(names.index(43), walk, "the walk is seen, so it runs after the white flash")
        self.assertLess(walk, names.index(63), "and it finishes before the punch group opens")
        self.assertEqual(plateau.PUNCH_FROM[0], plateau.TRUNKS_SPOT[0], "a straight walk north")
        self.assertEqual(plateau.PUNCH_FROM[1] - plateau.CELL_SPOT[1], 24, "celljr's own melee gap")
        self.assertLess(plateau.CELL_SPOT[1], plateau.PUNCH_FROM[1], "he stays south of Cell")
        self.assertLess(plateau.PUNCH_FROM[1], plateau.TRUNKS_SPOT[1], "and closer than the staging")

    def test_the_punch_spot_is_open_ground_on_the_arena_and_inside_the_parked_view(self):
        """The punch happens on map 6,100, not on the plateau, so the ground under the walk is the
        ARENA's own collision frame. His whole 32 px frame also has to stay inside SPLIT_VIEW."""
        _, arena = plateau.map_entry(self.rom, 6, 100)
        layout = struct.unpack_from("<I", self.rom,
                                    struct.unpack_from("<I", self.rom, arena + plateau.F_LAYOUTS)[0]
                                    - ROM_BASE)[0] - ROM_BASE
        bits = plateau._frame(self.rom, struct.unpack_from("<I", self.rom,
                                                           layout + plateau.L_COLLISION)[0])
        for y in range(plateau.PUNCH_FROM[1], plateau.TRUNKS_SPOT[1] + 1, 8):
            for cx, cy in plateau.envelope_cells((plateau.TRUNKS_SPOT[0], y), plateau.TRUNKS_ENVELOPE):
                self.assertTrue(plateau.is_open(bits, cx, cy), f"arena cell ({cx},{cy}) at y {y}")
        top = plateau.PUNCH_FROM[1] - plateau.TRUNKS_UP
        bottom = plateau.PUNCH_FROM[1] + plateau.TRUNKS_DOWN
        self.assertGreaterEqual(top, plateau.SPLIT_VIEW[1])
        self.assertLessEqual(bottom, plateau.SPLIT_VIEW[1] + plateau.VIEW[1])

    def test_the_two_halves_are_a_true_half_each_and_meet_at_50(self):
        """ext 85 bar_show calls the SAME builder with (0, 100), so lo = 0 is the engine's own full
        bar value and an even split is as legal as vanilla's uneven slices."""
        lo1, hi1 = plateau.ROUND1_BAR
        lo2, hi2 = plateau.ROUND2_BAR
        self.assertEqual((hi1 - lo1, hi2 - lo2), (50, 50))
        self.assertEqual(hi2, lo1, "the two halves meet")
        self.assertEqual((lo2, hi1), (0, 100), "and together they are the whole bar")

    def test_round_2_has_its_own_actors_and_its_own_death_event(self):
        """Sharing battle_arena's item list would share the enemy ITEM, and an item carries its death
        table at +0x14, so Cell's death on the plateau would split the fight again for ever."""
        _, arena = plateau.map_entry(self.rom, 6, 100)
        self.assertNotEqual(struct.unpack_from("<I", self.rom, self.notes["entry"] + 0x14),
                            struct.unpack_from("<I", self.rom, arena + 0x14))
        enemy = struct.unpack_from("<I", self.rom, self.notes["items"] + 4)[0] - ROM_BASE
        self.assertEqual(enemy, self.notes["item"])
        event = struct.unpack_from("<I", self.rom, enemy + 0x14)[0] - ROM_BASE
        self.assertEqual(event, self.notes["event"])
        self.assertEqual(struct.unpack_from("<I", self.rom, event)[0], plateau.EVENT_RUNNER)
        table = struct.unpack_from("<I", self.rom, event + 4)[0] - ROM_BASE
        self.assertEqual(table, self.notes["death_table"])
        self.assertNotEqual(table, self.notes["arena_table"])

    def test_round_2s_death_runs_the_collapse_the_blast_and_the_vanilla_tail(self):
        """Table D2 word 0 is ending_fight's own record K, unchanged, and words 24 and 25 still name
        the vanilla end text and the vanilla exit."""
        d2, d1 = self.notes["death_table"], self.notes["arena_table"]
        self.assertEqual(struct.unpack_from("<I", self.rom, d2)[0],
                         struct.unpack_from("<I", self.before, d1)[0], "word 0 is still record K")
        for w in (24, 25):
            self.assertEqual(struct.unpack_from("<I", self.rom, d2 + 4 * w)[0],
                             struct.unpack_from("<I", self.before, d1 + 4 * w)[0], f"word {w}")

    def test_the_npc_cell_the_plateau_builds_stands_on_the_fight_spot(self):
        npc = struct.unpack_from("<I", self.rom, self.notes["items"])[0] - ROM_BASE
        self.assertEqual(struct.unpack_from("<I", self.rom, npc + 4)[0], 0, "condition 0: built at load")
        self.assertEqual(struct.unpack_from("<hh", self.rom, npc + 8), plateau.PLATEAU_CELL_SPOT)
        self.assertEqual(struct.unpack_from("<I", self.rom, npc + 0xC)[0], plateau.CELL_SET)

    def test_both_parked_views_hold_both_fighters_whole(self):
        """Bible B0246: set 28 reaches 56 px above his own point and the Trunks sets 24. A view is
        240 x 160 from its TOP LEFT, so the pair has to fit inside it or a frame is cut."""
        pairs = ((plateau.SPLIT_VIEW, ((plateau.CELL_SPOT, plateau.ENVELOPE),
                                       (plateau.TRUNKS_SPOT, plateau.TRUNKS_ENVELOPE))),
                 (plateau.PLATEAU_VIEW, ((plateau.PLATEAU_CELL_SPOT, plateau.ENVELOPE_LR),
                                         (plateau.PLATEAU_TRUNKS_SPOT, plateau.TRUNKS_ENVELOPE_LR))))
        for view, spots in pairs:
            for spot, env in spots:
                self.assertGreaterEqual(spot[1] - env[2], view[1], f"{spot} head above {view}")
                self.assertLessEqual(spot[1] + env[3], view[1] + plateau.VIEW[1], f"{spot} feet")
                self.assertGreaterEqual(spot[0] - env[0], view[0], f"{spot} left of {view}")
                self.assertLessEqual(spot[0] + env[1], view[0] + plateau.VIEW[0], f"{spot} right")
        self.assertLess(plateau.PUNCHED_TO[1] + plateau.ENVELOPE[3], plateau.SPLIT_VIEW[1])
        self.assertLess(plateau.FLIES_TO[1] + plateau.TRUNKS_DOWN, plateau.SPLIT_VIEW[1])

    # ----- the map table -----

    def test_the_table_grew_by_one_and_every_earlier_map_came_across(self):
        table, count = plateau.map_table(self.rom)
        self.assertEqual(table, self.notes["table"])
        self.assertEqual(count, self.notes["old_count"] + 1)
        old = bytes(self.rom[self.notes["old_table"]:
                             self.notes["old_table"] + MAP_SIZE * self.notes["old_count"]])
        self.assertEqual(bytes(self.rom[table:table + MAP_SIZE * self.notes["old_count"]]), old)

    def test_the_three_appended_maps_are_all_present(self):
        for zone, area in ((6, 100), (1, 100), (7, 100)):
            plateau.map_entry(self.rom, zone, area)

    def test_the_only_base_rom_bytes_this_module_changes_are_the_named_hand_offs(self):
        spans = []
        for start, size, name in self.notes["sites"]:
            if start < len(self.before) and start < 0x800000:
                spans.append((start, size, name))
        changed = {i for start, size, _ in spans for i in range(start, start + size)
                   if self.rom[i] != self.before[i]}
        allowed = set()
        for lit in plateau.BASE_LITERALS:
            allowed |= set(range(lit, lit + 4))
        allowed |= set(range(plateau.ENTRY3_LITERAL, plateau.ENTRY3_LITERAL + 4))
        allowed.add(plateau.MAP_COUNT_BYTE)
        for word in self.notes["fight_words"]:
            allowed |= set(range(word, word + 4))
        self.assertTrue(changed <= allowed, f"unexpected base writes: {sorted(changed - allowed)}")

    def test_a_second_run_raises(self):
        rom = bytearray(self.rom)
        alloc = log2_build.Allocator(len(rom), log2_build.EXPANSION)
        alloc.notes.update({"battle_arena": {}, "ending_fight": {}, "plateau": {}})
        with self.assertRaises(ValueError):
            plateau.apply(rom, alloc)

    # ----- his document, read back out of the ROM -----

    def test_the_rom_gives_his_document_back(self):
        """THE test of this module. map_file.read_map on the built ROM has to equal the repo copy of
        his map, field for field, or the patch did not lay the map he composed.

        `stamps` and `dropped` are editor notes and never reach the ROM, so they are not compared."""
        doc = plateau.document()
        back = map_file.read_map(self.rom, plateau.PLATEAU_ZONE, plateau.PLATEAU_AREA)
        self.assertEqual(map_file.validate(back), [], "the map read back is not even sound")
        for field in ("world", "blocks", "chunk_table", "blend", "unread", "collision", "terrain"):
            self.assertEqual(back[field], doc[field], field)
        self.assertEqual([list(p) for p in back["tiles"]], [list(p) for p in doc["tiles"]])
        self.assertEqual(sorted(back["layers"]), sorted(doc["layers"]))
        for name, layer in doc["layers"].items():
            for field in ("priority", "scroll", "offset", "cells"):
                self.assertEqual(back["layers"][name][field], layer[field], f"{name} {field}")
        self.assertEqual(len(back["animated"]), len(doc["animated"]))
        for got, want in zip(back["animated"], doc["animated"]):
            self.assertEqual(got, want)

    def test_no_over_layer_was_blanked_and_bg1_really_stands_over_him(self):
        """BG0 and BG1 are priority 1, so what they draw is IN FRONT of the player. This measures
        the result out of the ROM, not out of the plan.

        A cell draws only when its TILE holds a non-zero pixel: a non-null cell can name a blank
        slot, so a null test would report that every layer draws everywhere. Each layer is shifted
        by its own scroll offset first (layer pixel = world pixel + 64 n, bible B1082), or every
        count would be 64 px out. Measured 2026-11-08: BG0 draws NO cell anywhere, so nothing was
        blanked away from it either, and BG1 stands over 488 cells of walkable ground, which is
        where he walks behind scenery. 488 was 477 before the owner moved his overhead cliff from
        BG3 to BG1 on 2026-11-08, and the new number was READ out of this build, never reached by
        trying values. BG0 at 0 is the other half of the test: BG0 drawing over walkable ground
        would be a defect to report, not a number to update."""
        lay = self.notes["layout"]
        draws = {n: any(px) for n, px in enumerate(scene_probe.static_tiles(self.rom, lay))}
        for group in scene_probe.layout_groups(self.rom, lay):
            for n in range(group["tiles"]):
                draws[group["first"] + n] = any(any(f["pixels"][64 * n:64 * n + 64])
                                                for f in group["frames"])
        doc = plateau.document()
        reach = plateau.reachable(plateau.open_cells(doc),
                                  (plateau.PLATEAU_CELL_SPOT[0] // 8,
                                   plateau.PLATEAU_CELL_SPOT[1] // 8))
        across = doc["blocks"][0] * plateau.BLOCK_TILES
        drawn = {}
        for name in ("bg0", "bg1"):
            layer = doc["layers"][name]
            sx, sy = map_view.layer_shift(tuple(layer["offset"]))
            drawn[name] = {(n % across - sx // 8, n // across - sy // 8)
                           for n, cell in enumerate(layer["cells"])
                           if draws.get(cell & map_file.TILE_INDEX, False)}
        self.assertEqual({name: len(cells & reach) for name, cells in drawn.items()},
                         {"bg0": 0, "bg1": 488})
        for spot, env, who in plateau.PLATEAU_SPOTS:
            box = set(plateau.envelope_cells(spot, env))
            for name, cells in drawn.items():
                self.assertEqual(box & cells, set(), f"{name} would hide {who} at {spot}")


if __name__ == "__main__":
    unittest.main()
