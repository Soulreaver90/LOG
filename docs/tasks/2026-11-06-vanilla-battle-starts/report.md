# Report: how vanilla starts a battle, and the standard we should build

Agent study, 2026-11-06. The agent could not write this file itself, so its report is saved below.
Everything under "My verification" is mine. Treat the agent's text as unverified except where I say otherwise.

## My verification, before any of this is used

**CONFIRMED by my own read of the ROM bytes.** Appearance table `0x081D967C`, 20 bytes an entry, 22 entries.
Entry 16 raw `018565150f0f07026000000000010000ec210003`: `+0` = `0x01` so bit 0 (transformed) is set, `+1` =
set **133**, `+5` = revert target 15, and entry 15 is set 132. Trunks' entries 12-17 are **byte identical**
between the base ROM and the arena v4 build. Exactly 3 entries differ from base: 2, 4 and 5, all Gohan's,
which is what `gohan_gi` and `cellgames_ssj` are documented to change. So `ext 73 (3, 133)` is the argument,
and Trunks needs no reverse-lookup patch.

**CONFIRMED by my own read of the handler.** `Sprite_Select` `@0x08009370`, the whole function, from the
disasm repo's own `build\code\Sprite_Select.s`:

```
ADD  r1, r0, #0x0          ; r1 = the set argument
BNE  loc_0800937E          ; non-zero: look it up by set
LDR  r0, [pc, #0x220]      ; Sprite_CurrentDirectory
LDR  r0, [r0, #0x0]
CMP  r0, #0x0
BNE  loc_08009390          ; non-zero: RETURN IT, the player
loc_0800937E:
ADD  r0, r1, #0x0
BL   loc_08009324          ; get_set
LDR  r0, [pc, #0x20C] ; MOV r1, #0x5 ; LDR r0, [r0, #0x8]
BL   loc_08006E0A          ; world_query, message 5
```

Set 0 is special-cased, as the agent says.

**The guard the agent understates.** It calls the zero branch "no player body yet". Bible row 1049 says
`0x03001FA8` is `Sprite_CurrentDirectory` and **zero is its NORMAL resting value during play**, measured in
four save states. So during play, set 0 normally takes the FALLBACK path, `get_set(0)` then `world_query`,
not the direct return. The conclusion still holds, for a reason the agent did not give: our own shipped arena
ROM already runs `face(set=0, dir=1)` in record F and the player does face up in the owner's screenshot. So
set 0 reaches the player down either branch. Keep the nuance. "Returns the player directly with no world
query" is true only when `Sprite_CurrentDirectory` is non-zero.

**Corroborated independently.** The agent's finding that `0x030020C0` (vtable `0x08025A6C`) is the follow
camera and `0x030020F4` (vtable `0x08025034`) is not matches my own measurement of the owner's two states,
made before the agent reported. Bible row 1048 is wrong; rows 774, 887 and 1038 are right.

**Not verified by me, and still the agent's claim alone:** the `ext 70` and `appearance_revert` order rule,
the 8-op table in section 2, `ext 51 spawn` being the only op that cannot take set 0, the census figures, the
template record `rom:0x3E9384`, the Piccolo against Android 17 identification (which it labels LIKELY itself),
and `map_load @0x0800C584` replacing the camera.

---

## The agent's report

### 0. The owner's design works. One blocking order rule.

`ext 73 (3, 133)` then `push 3 ; ext 70` gives player-controlled Super Saiyan Trunks. CONFIRMED from the
handlers, and the order is not optional.

`ext70_set_leader @0x0800A784` runs `set_leader` and then `appearance_revert @0x08003ED4`. That function loops
the 6 party records and skips the one whose index equals the save struct's leader byte:

```
08003eda  ldrb r2,[r0,#0x0]    ; leader byte
08003edc  cmp r2,r1            ; against the loop index 0..5
08003ede  beq 0x8003efc        ; equal: SKIP this record
```

`set_leader` has already written the new leader, so the new leader is the one record the revert leaves alone.
`ext 73` before `ext 70` survives, and `ext 73` after `ext 70` is fine too, but `ext 73` on a character who is
not and does not become the leader is reverted. This is why `cellgames_ssj` works.

### 1. Trunks' Super Saiyan party appearance id

CONFIRMED: entry 16, set id 133. The `ext 73` argument is 133.

Appearance table `0x081D967C`: `+0` flags (bit 0 = transformed form), `+1` sprite set id, `+5` revert target,
`+0x10` vtable for form enter and leave.

| Entry | `+0` | `+1` set | `+5` revert |
|---|---|---|---|
| 12 | `0x00` | 128 | 17 |
| 13 | `0x00` | 129 | 14 |
| 14 | `0x01` | 130 | 13 |
| 15 | `0x00` | 132 base Saiyan armor | 16 |
| 16 | `0x01` | 133 | 15 |
| 17 | `0x01` | 134 | 12 |

Groups: 0-5 Gohan (53, 55, 56, 57, 58, 59), 6-7 Piccolo (103, 104), 8-11 Vegeta (137-140), 12-17 Trunks,
18 set 135, 19-20 Goku (60, 61), 21 set 72.

The premise in the re-scope does not hold for Trunks. Gohan's 59 and 158 differ only because our own
`gohan_gi` relocated his sets, and `cellgames_ssj` patches entry 5's `+1` from 59 to 158 to match. Vanilla
entry 5 is 59. Trunks has no such relocation, and `trunks_tank` changes no appearance byte. So the party
appearance set id and the NPC set id are the same number, 133.

`ext73_appearance @0x0800A8EC` confirms the argument is a SET id, not an entry index: on a non-leader it jumps
to `@0x0800A936` and calls `appearance_of_set @0x080042BC` with the raw set id to find the entry, then skips
the body build because `Sprite_CurrentDirectory` is zero.

### 2. Can the conversation run on the player actor? Yes, except `spawn`.

From `find_actor_by_set @0x08009370`, 34 bytes, 31 callers. Set 0 is special-cased and returns the player
object, whatever character the player is. Its 31 callers are the actor ops.

The 8 ops that name set 133 in the ending table `rom:0x3B8140`:

| Op | Address | Set 0 legal? |
|---|---|---|
| `spawn(133, 496, 504)` | `rom:0x3B7C41` | NO |
| `face(133, 1)` | `rom:0x3B7C72` | yes, ext 55 `0x08009EFC` is a caller |
| `attack(attacker=133, target=11, 100)` | `rom:0x3B7CA2` | yes |
| `attack(attacker=133, target=11, 100)` | `rom:0x3B7CDE` | yes |
| `attack(attacker=133, target=9, 100)` | `rom:0x3B7D80` | yes |
| `attack(attacker=133, target=9, 100)` | `rom:0x3B7DBC` | yes |
| `face(133, 0)` | `rom:0x3B7E06` | yes |
| `walk(133, 248, 568)` | `rom:0x3B7E6C` | yes, ext 53 `0x08009D4A` is a caller |

`ext 51 spawn` is the only op that cannot address the player. Its handler `@0x08009CC4` calls
`npc_factory @0x0800D6DE`, which never calls `find_actor_by_set` and builds a new NPC instead. So the design
drops the `spawn(133)` rather than repointing it. Vanilla continues past record F with three more `attack`, a
`face`, `pose(133,21)` and `remove(133)`; `remove` would find the player and delete him, so it goes too.

`face` and `walk` are CONFIRMED by slot against the caller list. `attack` (ext 96 `0x0800A158`), `pose`
(ext 57) and `move_to` (ext 62 `0x0800A44E`) fall past the truncated part of the 31-name list, but our own
arena scene `rom:0x94060C` already runs `move_to(set=0, 248, 568)`, `face(set=0, 0)` and
`attack(attacker=0, target=28, 100)`, and record F already runs `face(set=0, 1)` with leader 3. So set 0 on
those is proven in our shipped ROM.

No new op is needed. It is a byte swap plus two deletions. The two `camera_follow` ops in that table name 132,
not 133, so they are untouched.

### 3. The standard battle start and its checker (PRIMARY)

With the player present from frame one, the hand-off drops out and the shape is five obligations:

1. Cover the map load: `fade_out(n)` before it, or `palette_fx(n)`, or `load_map_fade`.
2. Set the form before or at the leader change: `ext 73 (c, set)` with `push c ; ext 70`.
3. Frame the fight under the cover with `camera(x, y, speed)`.
4. Reveal and hold: `fade_in(n)` then `wait(n)`.
5. Give control back: `header_bit1(1)` and the bar, plus `camera_follow(0)` when and only when a fixed camera
   is still current.

**Which existing tool validates it:** `scripts\permanent\scene\scene_harness.py`. It already runs a record or
table op by op and reports the ops, spawns, end positions, flags, sounds and next index, and records an
unknown ext op with its arguments. It models no camera today and should learn two fields:

- `camera_owner`: which object owns `0x03000FF4` at the end of the run.
- `screen_covered`: whether a fade or flash is open at each op.

`scene_probe.py` stays a printer. A new file is not right, because `scene_lib` already owns the op vocabulary
and `scene_harness` already owns the execution model, so a third module would split both.

For composing rather than checking, add `battle_start(...)` to `scene_lib.py`:

```python
def battle_start(*, leader_who, zone, area, var, player_xy, facing,
                 frame_xy, frame_speed=10, hold=60, cover=("fade", 120),
                 bar=None, bar_range=None, spawn_list=None,
                 appearance=None, follow=0) -> bytes:
    """Emit a vanilla shaped battle start: cover, load, form, frame, reveal, hold, HUD, bar."""
```

Test file `scripts\permanent\tests\test_battle_start.py`, each test running `scene_harness.run_table` over the
live build:

1. `test_map_load_is_covered`: for every record that loads a map and then shows a bar, a fade or flash is open
   across the load.
2. `test_camera_is_handed_back`: if any op before the control record set a fixed camera, the table reclaims it
   after the LAST `ext 31`, by `ext 33`, `ext 37` or a map load.
3. `test_form_survives_the_leader_change`: a record that runs `ext 73` and `ext 70` either names the same
   character in both, or runs `ext 73` after `ext 70`.
4. `test_player_ops_address_the_player`: a record our modules own names no NPC set that the design moved onto
   set 0.
5. `test_control_record_shows_the_hud`: a record that shows a bar also runs `header_bit1(1)`.

**What the check cannot know:** whether a story flag makes a form legal (Super Saiyan 2 is gated on flag 195),
whether `frame_xy` survives the map view clamp (bible rows 1168, 1507), the boss's real set and bar range,
which `map_load` branch a map takes (layout `+0x3C`), or anything about timing, animation or combat. It also
reads WALK order, which is not execution order where a `jz` or a next index branches.

**Declaring a deviation:** in the patch module, not the test. Each module gains an optional
`BATTLE_START_EXCEPTIONS = {record_offset: "one line of why"}`. The test reads it, asserts the record is
actually in the module, and fails on a stale entry.

**Why this would have caught the arena:** assertion 1 fails record F today, because it loads a map and shows a
bar with no cover. Assertion 2 fails table `rom:0x3B8140` today, because `camera(384,368,2)` at `rom:0x3B7B8F`
is never reclaimed before record F gives control. Neither needs the camera study to run.

### 4. The vanilla survey

Walked all 327 map entries and the 303 scene tables they own. 302 walked clean, 1 is a null pointer. 27
records show a boss bar, 28 hand the camera back, 54 turn the HUD back on. **The 27 is a floor:** this shape
misses a battle run from a script region item (`0x0800C2C3`), from a map enter script (entry `+0x30`), from a
table named only by another table or by code, or with a bar drawn by code.

The template, the only vanilla record that both shows a bar and loads a map, `rom:0x3E9384` (map 14,3, the
Cell Games start):

```
fade_out(120) ; load_map_at(14,3,1,368,440) ; ext84(5) ; leader(0)
face(30,2) ; face(0,3) ; camera(328,344,10) ; spawn(60,552,96)
fade_in(120) ; wait(60) ; camera_follow(0) ; header_bit1(1)
bar_set(30,60,100) ; set_flag(192)
```

**The invariant, order-aware.** Of 302 tables, 48 set a fixed camera. Counting only what runs after the LAST
`ext 31`: 42 run `ext 33`, 3 run `ext 37`, 8 run a map load, 0 run `ext 119`. Ten of the 48 never reach
`header_bit1(1)`, so they give no control back. Tables that take the camera, give control back and reclaim it
by nothing: ZERO. The agent's first run said "3 exceptions"; that run used `any()` and ignored order.

**Cover.** Of 55 map-load records, 43 are covered and 12 are not. No vanilla record that shows a bar loads a
map without cover.

**Order is not part of the shape.** The three control ops appear in three orders across `rom:0x3D40B2`,
`rom:0x3EA3EC` and `rom:0x3EB6E8`, so the checker must not test their order.

**The bar argument is not a diff.** It is the boss's own set id (12, 30, 31, 9, 14 across the census). Row
930's 31 and record F's 28 do not disagree.

**Piccolo against Android 17, LIKELY:** `rom:0x3E47DC` (map 11,4), rematch `rom:0x3E4B3A` (map 11,6). Record 0
parks `camera(152,96,3)` for the talk, and word 6 ends
`ext104(9,1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0)`. That parked-then-eased shape is what
the owner saw. Set 9 as Android 17 rests on row 933 and on sets 8, 9 and 11 flying off together in
`rom:0x3E494C`; it is not proven from a character table.

**Search shape B is broken, which explains the brief's miss.** `--find-text` returned nothing for the Piccolo
line and for shorter fragments, and a raw byte search of the whole 8 MB file also returned nothing. A type 2
record carries a compressed payload at `rom:0x18xxxxxx`, outside `SCRIPT_REGION`, and the matcher reads only a
type 1 record's inline text. So no text search can enumerate scenes, and a miss is never evidence of absence.

### 5. The dead camera question

`map_load @0x0800C584` installs the camera and REPLACES it; it never eases. Its walking branch writes the new
player into `0x030020C0 + 4` and stores that object in `0x03000FF4`, which is exactly what `ext 33 (0)` does,
so a map load is itself a hand-back.

Two by-products: `0x030020C0` (vtable `0x08025A6C`) is the follow camera and `0x030020F4` (vtable
`0x08025034`) is not, which settles bible row 1048 against rows 774, 887 and 1038. And `ext 45` is an OBJ
palette DMA, not a map action, so our arena scene's `ext 119 ; ext 45` tail does not reload the map.

### 6. The agent's corrections to its own earlier claims

- The "3 invariant exceptions" is wrong and is replaced by zero.
- "The 13 bar records with no hand-back are free-roam fights" was a record-scope inference and is dropped.
- `ext 34` is not a fade, but its effect lives in whatever reads `[0x03001FC0 + 4]`, which it did not read, so
  a load preceded only by `ext 34` is "covered by no op we can name", not proved uncovered.
- The ss2 view number is scoped to "may be stale": ss2's live camera is `0x030020F4`, and the sprite read for
  ss2 (136,456) equals the arena scene's `camera(136,456,2)`. Only the ss3 read is proof.

## Open for the owner

Trunks' Super Saiyan entry 16 carries set 133, the same set the conversation NPC already uses, and his
screenshot of state 2 shows that set looking right. What is NOT proven is that the set animates correctly as
a PLAYER body (walk, attack, hit) rather than as an NPC puppet. The agent asks whether to confirm that by eye
first or to bank the spec and let the owner check it in the trial build.
