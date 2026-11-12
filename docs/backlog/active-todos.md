# LOG active todos

## 2026-10-31: flat imports broken by the rom\ move

This morning's reorg moved 13 modules into `scripts\permanent\rom\`. **193 scripts under
`scripts\one-time\` still import them flatly and now fail**, measured, not estimated:

| module | scripts that import it flatly |
|---|---|
| `webfoot_decompress` | 163 |
| `log2_sprites` | 89 |
| `thumb_dis` | 70 |
| `rom_sheet` | 47 |
| `log2_save` | 35 |
| `state_dump` | 31 |
| `rom_space` | 24 |
| `re_sym` | 1 |

Confirmed in practice, not in theory: `scripts\one-time\2026-10-25-chapter-cards\c4v_patch.py` raises
`ModuleNotFoundError: No module named 'webfoot_decompress'`. The card 4 v10, v11 and v12 tools all import
it, so the card 4 tool chain carries the fault. The v12 task restated the rule in its own `c4y_lib.py`
rather than repair another task's folder, which was the right call for its brief.

This is fallout from my own reorg, so it is mine to fix, not a pre-existing defect.

**Final decisions, not urgent.** One-time scripts are historical records that already ran. Three ways:

1. Leave them. They are records. Repair one only when a task needs it, as the v12 task did.
2. Add 13 one-line shim modules at `scripts\permanent\` that re-export from `rom\`. Cheap, and it undoes
   some of the reorg's point.
3. Rewrite the 193 import lines. Thorough, mechanical, and touches a lot of history for little gain.

My recommendation is 1, because nothing in `permanent\` is affected and the suite is green.

## Split the live repo from the scratch repo (owner, 2026-11-02, for next week)

Owner's idea: keep one repo for final work, which is all he wants uploaded, and a separate
LOCAL git for working material, so the untracked work finally has history.

Measured on 2026-11-02, the material with NO history at all:

| Path | Size | State |
|---|---|---|
| `art\trunks_tank\` | 36 pngs | 0 tracked. `.gitignore:62` is `art/*` and this folder is never named back in |
| `scripts\one-time\` | 217 MB, 1076 py | gitignored whole (`.gitignore:42`) |
| `builds\` | 1.9 GB | gitignored, ROMs, must stay out |
| `data\` | 240 MB | gitignored, supplied read-only, must stay out |
| `scratch\` | 2.3 GB | throwaway by design |

His hand drawn frames therefore exist in exactly one place on disk. On 2026-11-02 two of
them were overwritten and only a manual backup made it reversible.

Note for the discussion: `art\` and `scripts\one-time\` are ALREADY ignored by the live
repo, so a nested `.git` inside either one is invisible to the parent and needs no submodule.
Exclude the 4 `.gba` files (64 MB) and the two large mockup gifs (27 MB) from any such repo.

---

## FIXED 2026-11-06: `sprite_loop.py` crashed on a held frame

`scripts\permanent\rom\sprite_loop.py` exits 1 with `EOFError: no more images in GIF file` whenever two
consecutive frames are byte identical. Found by the sprite suite plan agent at 32 wide, and I isolated
it: **the width has nothing to do with it.** My own run on the approved 16 wide tank walk:

| Input | Result |
|---|---|
| four different frames | exit 0, decode check 0 of 2048 px differ |
| two different frames | exit 0, decode check 0 of 1024 px differ |
| **the same frame twice** | **exit 1, `EOFError`** |

Cause: Pillow's GIF encoder drops a frame identical to the one before it and extends that frame's
duration instead. The file then holds fewer frames than `len(shots)`, so the decode check at line 71,
`g.seek(n)` over `range(len(shots))`, walks off the end.

Why it matters: the decode check is the whole point of this tool, and an animation that HOLDS a pose for
two frames is ordinary. Today no shipped row has two identical adjacent frames, so nothing is blocked.

**Fixed 2026-11-06.** Our frame index now maps to the GIF's own index, so every frame is still
compared and the check is not weakened. Two helpers carry it: `same(left, right)` and `holds(shots)`.
The tool also asserts the GIF's frame count equals the frames sent minus the held ones, and it fails
with a plain line when the encoder collapses anything else. The output line now counts the held
frames.

Proof: 8 held-pose shapes all exit 0 with 0 px differing, including a hold at the start, in the
middle, at the end, three of the same frame, and two separate holds. Four of those shapes are pinned
in `scripts\permanent\tests\test_sprite_loop.py`, which runs 7 tests, real exit code 0.

---

## 2026-11-06 documentation and tooling sweep

Raised by the owner: "make sure all is documented, clean and organized. Anything we need to add to the bible
or dissam, any tools we need to create or update". This is the full list, with what is DONE and what is OPEN.

### Done this session

- **Bible, 13 rows merged.** `ARN3` 5 rows (the music carriers and two cleared dead ends), `ARN3B` 2 rows
  (the music continuity closed in CODE, the script op and the starter), `ARN4` 6 rows (the two shadows, the
  map post with no collision, the open doorway, the WRAM anchor scan, the `obj+0x48` trap, the `map_view`
  caveats). Bible is 1943 rows.
- **`docs\design\2026-11-06-one-reader-per-section.md`**, the decision: one bible, one READER per section, a
  reader holds no copy of a ROM fact, a reader resolves live structures rather than hardcoding them.
- **`docs\tasks\2026-11-06-arena-v4\measurements.md`**, every number in the v4 brief with its source.
- **`rom\state_dump.py` extended**: prints the current map and every actor spot, found by the anchor scan.
  It had NO test; it now has `tests\test_state_dump.py`, 11 tests, and three of them read the owner's real
  states and pin the (244,504), (248,568) and (248,680) measurements the v4 brief rests on.
- **`rom\whatis.py`** pointed off the stale gnu tree and at the disasm repo's own `build\code`.
- **`log2_build.py`**: `--log PATH` no longer REPLACES `docs\build-log.md`. Three missing builds backfilled.
- **`docs\tool-index.md`**: caveats recorded on `map_view.py`, `scene_probe.py` and `state_dump.py`.

### Open: tools to create

1. **The map reader, section 9.** The real gap, and the reason the arena shipped three times with inherited
   doors. Extend `scene\scene_probe.py --map`; do NOT write a third tool. It must print the entry fields by
   name, the layout chain, BOTH door carriers decoded side by side, the collision frame with its container
   type and open counts, and the BG layer records. Resolve the map table from the literal at `rom:0xEBD8`.
   The full specification is in the design doc above.

### Open: tools to update

2. **`scene\map_view.py`**, ONE defect, not two. **Half of this entry was already false when it was
   written and I corrected it on 2026-11-07.** The tool does NOT hardcode the map table: lines 40-41 carry
   a comment saying no map table constant lives there on purpose, and line 177 reads the entry through
   `scene_probe.map_entry`, which resolves this ROM's own table from the literal at `rom:0xEBD8`. So
   `--rom <a build>` finds an appended map correctly. The REAL defect stands: its boxes labelled "warp"
   are REGION records from entry `+0x10` and never the layout's door list at `+0x40`/`+0x44`, its own line
   prints `region cond ... warp rect ...`, and it draws no layout PROPS (`+0x24`/`+0x28`). **In flight
   2026-11-07**, with item 3 below, under `docs\tasks\2026-11-07-map-reader\brief.md`.
3. **`scene\scene_probe.py --map`** stops one pointer short: it resolves `+0x2C` to the layout and never
   reads `+0x40`/`+0x44`. It already owns the decoder, so this is a few lines.
4. **`rom\show_regions.py` and `rom\sprite_loop.py`** were fixed earlier today. No action.

### Open: the disassembly repo

The naming branch is local only, never pushed. These came out of today's reading and are worth a rename pass:

5. **`Table_InitRing` @0x08020A4C is misnamed.** It is the MUSIC STARTER: it stores the song record pointer
   at player `+0xC` and sets player `+5` to 1. Every caller that starts music goes through it. The current
   name sends a reader looking for a ring buffer.
6. **`sub_08009C8A` is the script `music` op.** It pops the id, forms `id * 20` off `0x081D4B2C`, applies the
   already-playing skip test and calls the starter.
7. **`sub_0800EB58` is the map music getter.** It reads entry `+0x24` and returns it as a song id when it is
   under `0x10000`, or runs it as a script and returns the result.
8. **`sub_0800D8AE`** is a two instruction constant getter and **`sub_0800D9C2`** a 0x18 byte object
   constructor. Both were guessed to be region trigger tests while hunting the arena's exits. Naming them
   stops the next reader repeating that.
9. Nothing to do about `0x08003AFE` and `0x080042EA`. They are data the STALE gnu tree mis-decoded as code,
   with zero references anywhere in the disasm tree, and the disasm repo is right to omit them.

### Open: the arena itself

10. **Trunks starts in base form, not Super Saiyan.** Reported by the owner on arena v3 and deliberately kept
    out of the v4 brief so no cause is guessed at. Needs its own task. Start by asking the owner for a state
    on each side of the load, because the question is about runtime state.
11. **The bible `EF1` row still describes the old map 6,1 route** for the ending fight, which the arena
    replaced. Mark it superseded.
12. **Bible row 1210 restates row 708** without citing it, so the bible now holds the warp answer twice in
    two places. Cross reference them, since the duplicate is what the one-reader decision is meant to stop
    mattering.
13. **The save point and the map post still SPAWN, with collision.** v4 painted out their shadows only. My
    claim that they were "drawn in, not spawned" was too broad, and the owner disproved it by loading the
    ROM. Which layout field spawns them is unknown. Five probe ROMs made with `rom\poke_rom.py`, one
    candidate word zeroed each, wait in `builds\mockups\2026-11-06-arena-probe\` for him to load.
14. **STRUCK 2026-11-06, this was wrong.** The blue at px (224-287, 200-223) is floor reflection art
    in the plaza tiles, open in vanilla too, and it is NOT a door. The real opening is the doorway recess
    at cells (28-35, row 11), left open on purpose by `DOOR_MOUTH_ROW`. See the v7 brief, part 4.
    OLD TEXT: the glass panels at px (224-287, 200-223) are still open floor, 72 px south of the arch. v4 closed
    the dome entrance at (224,72)-(287,87). If the panels are what the owner meant by "the glass door",
    fix 2 aimed at the wrong opening. Ask him which one he walked through before changing any cell.
15. **A third drawn-in shadow, the gate's own**, px (200,272)-(207,327), 376 pixels of palette index 73. The
    v4 brief covered the save point and the dome only. Both fighters stand beside this one.
16. **Waiting on the owner, not a deferral: the Cell spawn trade.** (244,504) gives "no movement at fight
    start" and puts 1894 BG1 pixels of the CAPSULE CORPORATION arch over his sprite box. (244,616) gives 0
    and costs a jump on the first frame. There is no middle row, because BG1 clears only from y 552 down and
    his box reaches 56 px above his feet. Sheet: `scripts\one-time\2026-11-06-arena-v4\sheet_spots.png`.

## 2026-11-07: the FUTURE Android 18 and 17 fights (`future_androids`, trial v1)

Deferred from the trial build `log2_poc_r41_future_v1.gba`. Each item below will be its own task.

1. **The live `ext 73` body change at ending word 4 is measured in the handler, not on screen.**
   `sub_0800A8EC` rebuilds the leader's live body only when `Sprite_CurrentDirectory` `0x03001FA8` is
   non zero, and `ending_fight` recorded that word as zero all through the VANILLA ending, where no
   player exists. This build makes a player at word 0, so the word should be set by word 4. If it is
   not, Trunks stays in base armour for both fights and the transformation pose plays with no colour
   change. It is cosmetic, it cannot crash, and the play test settles it.
2. **Android 17 may turn away during his own fight.** His NPC carries celljr's FACE_PLAYER step, which
   does not run while a scene plays and re-decides once the player has control. The same limit the
   Cell Junior fight ships.
3. **CLOSED in v3.** The HUD gap is settled, not deferred. The VBS Section 9 row has `map_load`
   building the HUD only when the save's `+1` bit 1 is set, which is the bit `ext 86` writes, so an
   `ext 39` load could have put a HUD over words 1 to 7. Word 0 now runs `header_bit1(0)` under the
   black, in front of the form, and the op is a no-op when the bit is already clear. Each fight record
   still raises it with `header_bit1(1)`, which keeps the owner's "the hud appearing" beat.
   `ending_fight` flagged the same gap for words 14 to 22 and it is still open there.
4. **Neither fight handles a loss.** A loss runs the vanilla game-over table, which is the call
   `ending_fight` already made for the Imperfect Cell fight.
5. **The reveal view is vanilla's `ext 35` pair read as a view origin.** Word 0 parks `camera(384,552,2)`
   under the black because `ext 39` centres on the player instead. That the vanilla pair was a top left
   is LIKELY, from the framing it gives NPC Trunks at (496,648). `Map_Load @0x0800C664` has since been
   read for the music question and it hands the pair to `@0x08006152`, which was not followed. The park
   makes the reading moot for this build, but the bible row should say which it is.

7. **Settled in v3, recorded so it is not re-litigated: the music.** `ext 35` never reads a map's `+0x24`
   and `ext 38`/`ext 39` do, so moving this scene to `ext 39` would have cued the Android theme under
   the black, 11 ops early. The clone's `+0x24` names song 42, the one already playing, which the load's
   own "already playing" test skips. See the FUT rows.

8. **Settled in v3: the pose at word 4 is dropped, not aimed at the player.** `ext57_set_state` does not
   block, and vanilla destroyed the posed NPC one op later, so the pose never played. Aiming it at the
   player would have left him in an unverified state 9. If the play test wants a visible transformation
   beat beyond the sound and the form change, that is a new task with a state that has been read.
6. **The clone keeps map 1,2's whole walkable floor.** No collision cell was changed, per "change who
   fights, not the staging". The prologue region is gone, so crossing x 360 is now harmless, but nothing
   stops the player walking far from the fight. Watch for it in the play test.

9. **The BG layer art can hide an actor on ground the collision frame calls open (map 1,100).** At the
   far west of the android street the map draws a tree canopy and a grass verge over open cells. In the
   `v8_kill_edge` capture the player stood at (16,569) and Android 17 walked to (45,569) and then
   (72,569), both read out of RAM, and neither actor appears in any frame. Every keep-out census this
   project has (props, break records, items, regions, doors, pickups, markers, collision) misses it,
   because it is tilemap art. A reader that answers "is this cell DRAWN over" needs the BG layers, and
   until one exists the finale claim is "inside the view", never "visible".

---

## 2026-11-07: both renderers draw an offset BG layer 64 n px out of place

**CONFIRMED, and it is not the map editor alone.** A BG layer record's `+0x0C` and `+0x10` are a
scroll offset in 22.10 fixed point. The layer object's update `@0x080055A4` adds `+0x0C` at
`0x080055B4`, shifts the sum right by 10 and stores it to `REG_BGxHOFS` at `0x08005610` and to
`REG_BGxVOFS` at `0x08005614`. So the game draws layer n's art shifted back by `offset >> 10` px,
and bible row B1082 is right as written.

364 vanilla tilemap layer records carry a nonzero offset, almost always `0x10000 * n` = 64 n px (7
overlay and 3 unknown-class records carry one too and are not map art). The art is
authored to match: over every vanilla layer that scrolls 1 to 1 and carries an offset, 289 fit only
the shifted reading, 0 fit only the plain reading, 0 fit neither, and 56 are too small to tell.
Map 2,2 is the witness: world 768 px wide, bg1 art in grid x 64 to 831, bg2 in 264 to 895 and bg3
in 192 to 959, each ending exactly at `world + offset - 1`.

Neither `scripts\permanent\scene\map_view.py` nor `map-editor\editor\render.js` holds the word
`offset`, or any other shape of the correction. So every full-map render this project has made
draws bg1 64 px, bg2 128 px and bg3 192 px to the right and down of where the game draws them.

Three things to fix, in this order:

1. `map_view.py`: draw layer n at `-offset` and re-pin whatever hashes move.
2. `render.js`: the same, so the owner composes against what the game shows.
3. The truth panel: shade layer n outside `[offset_n, world + offset_n)`, not outside `[0, world)`.

**This corrects the Task 6 ruling.** Map 7,15's 328 px band from x 952 to 1280 is not unreachable
art. Its bg1 holds art to x 1015, bg2 to 1047 and bg3 to 1143, and the camera shows every one of
those once the offset is applied: bg1's last pixel lands on screen at world x 951. Only grid x 1144
and up, 136 px, is empty on every layer. The collision alarm is untouched, because no vanilla layout
has open collision past its world, which is also the evidence that collision reads in world
coordinates rather than in any layer's.

**One more consequence for the editor.** A document read from a vanilla map draws its collision over
its art in grid coordinates. Collision painted to match bg1 by eye lands 64 px off in the game.

## 2026-11-07: layout +0x30 is a position pair with no handler found

LIKELY, not confirmed. It is never zero in any of the 336 vanilla layouts, and read as two u16 it
is a point inside that map's own world on 332 of them (maps 1,7, 8,42, 8,63 and 8,65 are the four
that are not). Map 1,3 is a 240 x 160 world storing (120, 80), its exact centre.

`map_file.blank` writes 0 there, so a map composed from scratch stores (0, 0), which no vanilla map
does. `read_map` and `import_map` carry a real map's value verbatim, so the round trip keeps it.

Two search shapes found no reader: every `build\code` function that loads `#0x30]` and also loads
`#0x34]`, `#0x38]`, `#0x48]` or `#0x4C]`, and the two functions that hold a layout pointer,
`Scene_BuildLayers` and `Map_Load`. `Map_Load`'s `[r0,#0x30]` is the map ENTRY's enter script
(bible B1715), a different struct. A reader that reaches the layout through a RAM copy would not
appear in either shape. Until one is found, `blank` keeps 0.

## 2026-11-07: layout +0x3C is named in the bible, and map_file calls it unread

Bible row B1081 already says it: BGxCNT is the table `rom:0x1DA8EC` plus 8 times layout `+0x3C`,
plus the layout bytes `+0x04` to `+0x07`. `Scene_BuildLayers` loads `[r5,#0x3C]` and branches on it.
One vanilla layout of 336 carries 1 there and the other 335 carry 0, which is row 0.

`map_file` carries the word verbatim under `doc["unread"]["0x3C"]`, so nothing is lost today and
`blank` writes row 0, which the plan already picked. Rename the field to `bgcnt_row` and say what it
is. I did not search the bible for `+0x3C` before calling it unread, which is the rule CLAUDE.md
puts second.

## 2026-11-07: plateau.py reserves 0xCC for a 0x50 byte layout

CONFIRMED and deliberately left alone. Every one of the 336 vanilla layouts has a ROM word naming
its `+0x50`, where the next structure starts. Map 7,15's layout `0x085A1324` has `+0x50` =
`0x085A1374`, named by `rom:0x5A1480`. `plateau.py` copies 0xCC, so it carries 0x7C bytes of its
donor's neighbour along. It is harmless, because it allocates its own copy, and changing the
constant cannot give a byte identical ROM: every later allocation in the build moves by 0x7C. Fix it
only in a wave that re-pins the plateau build's SHA-1 on purpose.

## 2026-11-07: the editor cannot open a map whose chunk table is not the base pool

Not a silent fault. `serve.py`'s `borrowed_pool` already compares a map's `+0x4C` against the pool
the atlases were exported from and returns a problem on `/api/map`, so the page says so. The
document now carries `chunk_table` as well, and `import_map` refuses a ROM that has not got it.

What is still missing is the ability to OPEN such a map. The atlases hold the base pool's 168
chunks, and map 14,4 of every build list loads from a 169th at `0x0890ACF4` that no atlas holds.
`export_assets.export` reads `tile_stream.CHUNK_TABLE` directly. Give it a `--rom` and a chunk table
to export from, and have the page ask for the atlas set that matches the document's `chunk_table`.

## The future androids do not explode (owner, 2026-11-08)

His words on the v10 play test: "17 walking and trunks turning to him is great, keep it. The only
thing is that the androids do not explode (no smoke) if we can add that. But that isnt worth a whole
new build."

So rung 4 is APPROVED and this rides along with the next build rather than earning one of its own.

**It should be cheap, because the helper already exists.** `patches\celljr_fight.py` `_explode()` is
`ext 94 (set, 0, 0)` spark, `ext 46 (31)` sound, `ext 42` flash, remove, `ext 43` wait, and bible row
`B0900` records that each Cell Jr already ends with it in play. The death beats in
`patches\future_androids.py` remove each android with no effect at all.

**BUILT, and both checks are answered.** `future_androids.explode()` now runs on each android, from
`blast()` at the end of each death beat: `ext 94` spark, `ext 46 (31)` sound, `ext 69 (12)` hold,
then the remove.

1. **The spark id and the sound are set independent** (bible B2209, from B0793, B2007 and B2014).
   `ext 94` builds ONE fixed effect, id 0x27, at the actor's own centre, and nothing in that path
   reads the actor's set. Sound 31 is one of the two the engine's own enemy poof picks. The real
   smoke, effect 0x28, has no script path at all, for any actor.
2. **The boss descriptor suppresses nothing, because it never builds a poof to suppress**
   (B2208, B2004, B2006). Enemy types 3 and 4 carry `0x086FF3C4`, whose release runs the EXP task
   and the event task only. So the scripted explosion is the ONLY way an android can explode, and
   it is not competing with an engine effect.

It also drops celljr's white flash, because the owner's "NO transition" rule covers these two
records. The hold does the covering instead, and it is 12 frames against celljr's roughly 0, so the
spark is on screen LONGER here, not shorter. **Open, one question for him:** he may still want the
white flash. Ask when he next plays it.

Not yet seen in play: this has never been built. It rides along with the next build.

## Owner's five updates after the rung 5 play test (2026-11-08)

His words: "the portrait for trunks when talking to cell should use base / The stats for future 17
and 18 should be weaker than vanilla, that is actually canon. Same for cell, this is cell before he
absorbs people / Do we have no spots for new scouter entries? Future 17, Future 18, Future Cell.
Weaker stats, like 25% / And new bio entries. / For the cutscene, trunks should walk to cell and
punch him, not punch him a mile away. Otherwise much better."

So rung 5 is APPROVED in shape. These are refinements on top of it.

1. **Trunks' portrait in the Cell talk must be BASE, not Super Saiyan.** He now starts that fight in
   base form, so the portrait disagrees with the sprite.
2. **Future 18, future 17 and future Cell get weaker stats, about 25 percent.** His reason is canon:
   this is Cell before he absorbs anyone. MY READING, which he can correct: 25 percent WEAKER than
   vanilla, not reduced to 25 percent of it.
3. **Scouter entries for future 18, future 17 and future Cell**, with their own bios.
4. **The punch must land in close.** Trunks walks to Cell and punches him, rather than punching from
   across the map.

**The scouter table, measured on the base ROM 2026-11-08:**

| Fact | Value |
| --- | --- |
| Table | `rom:0x6F8E40` to `rom:0x6F983F`, 20 bytes an entry |
| Entries | exactly 128 |
| Entry shape | `+0x00` name pointer, `+0x04` BIO pointer, `+0x08` set id, `+0x0C` portrait id, `+0x10` save bit |
| What follows the table | its own string pool, at `rom:0x6F9840`, starting "Alligator" |
| Save bits the game reads | 0 to 127 (`@0x0801923A`, bible `B0676`) |
| Save bits actually used | 97 distinct, highest 108 |
| **Free save bits** | **31**, including 13, 15, 36, 41, 43, 46, 49, 52, 82, 87, 93, 95, and 109 to 127 |

So the save has room for 31 more discoveries, but the table is full at 128 and its strings sit
immediately behind it, so adding an entry means relocating the table. That is the same move
`battle_arena.py` already makes for the map table, so the pattern is proven here.

Duplicate entries are normal: "Cell, Perfect" appears 6 times under different save bits, Android 20
and Wolf twice each. So an entry maps one set id to a name, a bio, a portrait and a bit.

## 2026-11-08: the three new scouter entries do NOT show in the database list menu

`scouter_future` ships in `build_list_trial_plateau.txt` (future_v2). Entries 128, 129 and 130 are
Future 17, Future 18 and Future Cell, and they SCAN in battle, which is what the owner asked for.
They do not appear in the scouter DATABASE LIST menu, and that is deliberate.

**Why, measured from `sub_08019204`, the menu that builds the list:**

| Fact | Value |
| --- | --- |
| The menu object | `0x6B0` bytes (`mov r0,#0x6b ; lsl r0,r0,#4` `@0x0801920A`) |
| List 1, one 4-byte entry index per SCANNED entry | base `+0x80`, its 128th entry ends at `+0x280` |
| What sits at `+0x280` | list 2's own COUNT word (`mov r0,#5 ; lsl r0,r0,#7` `@0x0801922E`) |
| List 2, 8 bytes per distinct NAME | base `+0x284`, its 128th entry ends at `+0x684` |
| What sits at `+0x680` | a live block the menu writes at `@0x080192A8` (`+0x4`, `+0x8`, `+0x1C`, `+0x20`, `+0x24`) |

Both lists are exactly full at 128 entries, with no spare byte. Raising the list loop's bound at
`rom:0x19260` from 128 to 131 corrupts the object as soon as 129 entries are scanned, which is a
defect that passes every test and only shows on a late game save.

**To close it**, the menu object has to grow and both inner bases have to move: `0x6B0` to `0x6E0`,
list 2's base from `0x280` to `0x290` (`mov r0,#0x52 ; lsl r0,r0,#3`, the same two instructions) and
the block at `0x680` to `0x6B0` (`mov r1,#0xd6 ; lsl r1,r1,#3`). **Not attempted.** Those offsets are
also read by `sub_08019320` and `sub_0801963C`, the draw and scroll sides, so every site that names
`+0x280` or `+0x680` has to be found first. That is its own task, and it is cosmetic: a wrong tick in
a menu, not a crash and not a lost save.

**Also noted:** the scouter table above says `+0x10` is the save bit. It is NOT. `+0x10` is the ENEMY
TYPE INDEX (bible `B1793`), and the save bit is the ENTRY INDEX, set at `@0x08018A6E` with no upper
bound. The "free save bits" row above counts entry indices, which is still the right number, but the
entry-shape row is wrong and anything built on it would name the wrong field.

## Scouter database list: get the three future entries into the menu

Owner, 2026-11-08: "the scouter etnries are good. would be good to add to cpmputer but put that in
the backlog."

The three new entries (128 `Future 17`, 129 `Future 18`, 130 `Future Cell`) **scan in battle**, which
is what he asked for and what v2 delivers. They do **not** appear in the scouter database list menu.

**Why, measured by the v2 agent and worth re-checking before anyone starts:** `sub_08019204`
allocates `0x6B0` bytes for the menu. List 1 holds 4 bytes per scanned entry from base `+0x80`, and
its 128th entry ends exactly on list 2's count word at `+0x280`. List 2 holds 8 bytes per distinct
name from base `+0x284`, and its 128th entry ends at `+0x684`, inside the live block at `+0x680`.
**Zero headroom in either list.** So the list bound at `rom:0x19260` must NOT simply be raised: that
writes past live memory.

A fix has to grow the allocation and move both list bases, which is a bigger job than the scan was.
The scan needed one code byte; this needs the menu's own memory layout changed.

Not blocking anything. The entries are scannable today.

- **Ascended Super Saiyan for Trunks and Vegeta.** The GRADE is already wired: entry 14 (Trunks set
  130) and entry 10 (Vegeta set 139) carry form object `0x030021E8`, which gives +15 STR, +10 POW,
  +15 END and slower movement. Both currently point at art byte identical to the ordinary grade, so
  the feature needs new bulked sprites and a two byte set id swap, not new form code. Owner named
  this as a plan 2026-11-08. Design note: `docs\design\2026-11-08-ascended-super-saiyan.md`.
  Open first: measure which appearance pair playable Trunks and Vegeta actually use today.

## 2026-11-08: the finale beam should fire from the REAL player, not an NPC

**Tabled by the owner**, 2026-11-08, when he reviewed `finale_poses_wip1.gba`:

> "Keep the beam on your real player ... For the second option, maybe a new sprite with that up pose
> but lit up like shooting a ki blast, we can table that for later"

**What ships today.** The finale holds its poses with two clone sets, `set:161` (Cell's charge) and
`set:162` (Trunks' hands down and hands up). A clone set can never be given to the player, so the
scene stands NPC bodies on both marks and steps the player off the parked view. On screen it looks
right. The actor firing the beam is not his save's Trunks.

**What he wants instead.** The beam fires from his real player object. His own idea for how to get
there, and it is the better one: **draw a NEW frame, the arms-up pose lit up like a ki blast is
leaving the hands.** A purpose-drawn firing frame removes the reason the hold needed a clone at all,
because the pose would then be a real animation frame rather than a frozen idle frame.

**Why it is not free.** A held pose needs every frame of its row to carry the same picture, and the
rows that could carry it on set 133 are both reached by other live scenes: anim 18 is Trunks' sword
special in the future androids fight, and anim 4 is the idle used in the plateau transform. So this
waits on the new art, not on a code trick.

**Art note, when he draws it.** His own art rule stands: he draws it, I build the tool. The source
row is set 133 anim 4 dir 1, the back view, index 3 header `0x36AE4C`. Export it for him with
`frames_by_anim.py --set 133`.


## 2026-11-09: the journal entry, re-measured. NOT built, and it is not a four byte job

The owner asked for a full journal entry at the Capsule Corp beat: "then it fades to trunks at
capsule corp with the journael entry update". **His wording never arrived, so nothing was written
and no placeholder was built.** Two measurements below change the price. Read both before anyone
starts.

### Routing: SOLVED, with one hard ordering rule

The box is a TYPE 1 record and needs its own word in the ending table `rom:0x3B8140`. Walked from
word 0 in the built trial ROM, the ORIGINAL table reaches only words 0 to 8 and then the END, so
these words are dead IN THE ORIGINAL and can carry a record:

    9, 10, 14, 15, 16, 17, 18, 19, 20, 21

Words 12, 13, 22, 23, 24 and 25 are excluded: `ending_fight` and `plateau` already write them.
Re-run `scripts\one-time\2026-11-09-beam-tick-music\ending_words.py` before trusting the list.

**The ordering rule.** This table has MORE THAN ONE CARRIER. `future_androids` cuts a 27 word COPY
for each android's death event, and those copies reach words the original cannot: 18's copy runs
9, 10, 11 and 17's copy runs 12, 13, 24, 25 and then 14 to 23. `plateau` cuts D2 the same way. So a
module that rewrites an original word BEFORE a copy is cut hands that change to the copy. **Any
module that takes one of these words must run LAST, after `finale_blast`, and must refuse to run in
any other order.** Its test has to prove every copy carrier is byte identical with and without it.

Beware the trap that caught the first attempt: counting every literal a record pushes as a next
index marks almost the whole table reached. Only the header byte at `+0` and a literal left on the
stack at `op 17` hand on. In this table 9 and 11 are the two android SETS and 0 to 3 are the player,
the facings and the party id.

### The quest table: the real price is a RAM menu object sized for EXACTLY 43

The addendum's two numbers are both right, and both are a trap on their own:

- the table base `0x086D68DC` is named ONCE in the whole 8 MB, by the pool word `rom:0x4C80`;
- the entry count is one byte, `cmp r6,#0x2b` at `rom:0x4AE2`.

**The texts do not move.** Each entry carries an absolute text pointer at `+0xC`, read as
`ldr r1,[r5,#0xc]`. Entry 0's pointer equals `table + 688` only because the pool was laid right
after the table. So a 704 byte copy in expansion keeps all 43 texts working.

**What blocks it is the menu object.** `sub_080049FC` allocates `0x444` bytes
(`ldr r0,=0x00000444 ; bl 0x801F08C`, literal at `rom:0x4C64`) and parks TWO list headers in it:

| Field | Offset | Room to the next field |
| --- | --- | --- |
| list A header | `+0x154` | `0x15C` = 4 + 43 * 8 |
| list B header | `+0x2B0` | `0x15C` = 4 + 43 * 8 |
| a sub-object | `+0x40C` | `0x38` to the end of the object |

The fill loop reads quest `r6` at `0x086D68DC + 16 * r6`, runs its done script through the scene VM,
and appends an 8 byte item at `header + 4 + 8 * count` to list A when that script returns non-zero
and to list B when the active script does. Both capacities are exact, so **quest 44 writes one item
past list A and lands on list B's count word.**

Growing list A moves list B to `+0x2B8`, the sub-object to `+0x41C`, and the allocation to `0x454`.
`+0x2B0` is built at `rom:0x4A52`, `rom:0x4AF2` and `rom:0x4CA2` as `mov rX,#0x2b ; lsl rX,rX,#4`,
and `0x2B8` is not 16 times any 8 bit immediate, so each of those three needs an extra instruction
it has no room for. `+0x40C` is built at `rom:0x4A5C` as `add r0,#0xff ; add r0,#0x5d`.

Do not read those three `0x2b` immediates as the quest count. `0x2B0` does not fit a Thumb 8 bit
immediate, so the compiler builds it with `mov` plus `lsl`, exactly as it builds `0x11C` from
`add #0xff ; add #0x1d` two instructions earlier. That it equals `43 * 16` is a coincidence, and it
is what makes this look like a count bump.

**So the next attempt picks one of these, and the owner decides:**

1. Relocate the whole function, or re-code the three sites to load `+0x2B8` from a literal. Real
   work, and it is not a last-minute change.
2. REPLACE a vanilla quest entry instead of appending one. No bound, no offsets, no allocation: the
   table stays 43 entries and the menu object is untouched. It costs one existing journal entry.
3. Ship the box alone, with no journal entry behind it. Cheapest, and it loses what he asked for.

Option 2 is the one worth pricing first.

### What is still cheap and unchanged

The box itself. Bible B0706: sound 62 is the vanilla "Journal Updated!" chime and all 48 vanilla
`@^Journal Updated!` records carry `ext 46 (62)` in the 24 bytes before the box. Follow that shape
and keep `test_vanilla_plays_62_right_before_every_journal_box` green. Flag 196 is confirmed set by
farewell record 87 at its `ext 27 (196)`, before the ending begins, so it is a sound driver for the
entry's done and active scripts.
