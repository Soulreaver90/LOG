# Report: arena v5, the scene runs on the player actor

Build task, 2026-11-06. Brief: `brief.md` beside this. The agent could not write this file, so its report is
saved below. Everything under "My verification" is mine.

## My verification

**CONFIRMED by my own reads of the built ROM.**

- ROM `builds\mockups\2026-11-06-arena-v5\log2_poc_r41_arena_v5.gba`, SHA-1
  `a0a81e6f0c83e555f1133f1f4c0612306788d1f4`, matching the agent's figure.
- The paired `.sav` is byte identical to v4's, SHA-1 `d2fa5e1a016ae40fe3b264eb21008b807d391a1f`, so progress
  carries over.
- **The conversation runs on whoever already leads, not on Trunks.** I decoded the whole ending table from
  the built ROM. The ONLY `leader()` and `appearance()` ops in all 27 words are the two at word 23:
  `rom:0x9405F4 appearance(character=3, set=133)` and `rom:0x9405F8 leader(who=3)`. Words 0 to 22 never set a
  leader. The agent's headline finding is real.
- **`appearance_revert` is replaced in our build.** `rom:0x3ED4` in the built ROM holds
  `004b1847 07a98908`, which is `LDR r3,[pc] ; BX r3` to `0x0889A906`, `fullpower_ssj`'s hook. The base ROM
  holds `30b49d4c 00210278` at the same place, the real prologue. So the vanilla revert does not run, and the
  owner's pending `fullpower_ssj` decision turns on what that hook does, not on what the vanilla function
  does.

**What record 0 actually is, read by me and not covered by the agent's report.** The opening is NPC base
Trunks' whole arrival, not just a spawn:

```
music(42) ; load_map(6,23,1,0,192)        the sunny Capsule Corp, the time machine
camera_follow(132) ; walk(132,288,280) ; wait(120) ; walk(132,312,216) ; walk(132,352,216)
face(132,0) ; wait(80) ; face(132,1) ; wait(80) ; face(132,0) ; wait(40)
fade_out(180) ; load_map(1,2,1,384,552)   the android fight map
face(132,1) ; wait(120) ; camera_follow(132) ; walk(132,496,504)
camera(384,368,2) ; wait(60) ; face(9,2) ; wait(30) ; music(38)
```

So vanilla's structure is: **base Trunks (set 132) walks in and is the camera subject for the entire
opening, and `spawn(133)` in record 4 is the moment he TRANSFORMS to Super Saiyan for the android fight.**
That is why deleting the spawn leaves the player standing at record 0's load point (384,552) instead of the
NPC's spot (496,504).

**Not verified by me:** the save's leader byte per slot, the per-op set census, the hook's `CMP r5,#0x14`
body, and whether `ext 53 walk` works on a player object.

**Suite:** my own run is recorded at the end of this file.

---

## The agent's report

### 0. The conversation shows the current leader, not Trunks

The design moves the conversation's actor ops onto set 0, the player, and the player's body is whoever the
save says leads. No record in words 0 to 22 runs `ext 70`, and all three slots of the paired save hold a
leader who is not Trunks: leader 0, Gohan, in slots 1 and 2, and leader 4, Goku, in slot 3. CONFIRMED.
That the ending always starts with one of those is LIKELY, since the player can switch before triggering it.

So from record 4 through the android fight and the whole talk with Cell, the current leader walks Trunks'
path and speaks Trunks' lines. Trunks appears at the fight start, where `ext 70 (3)` runs.

Not fixed, because the brief did not cover it and two things are unknown:

- The leader change only installs a body when a map load follows it. The last map load before the talk is
  record 0's `load_map(1,2,1,384,552)` at `rom:0x3B7B6D`, so the form and leader would have to go in front of
  THAT, inside record 0.
- Record 0 also walks NPC set 132 around that map, and the brief says to leave every 132 op alone. Making the
  player Trunks there would put two Trunkses on map 1,2 at once.

The edit the agent would make, on the owner's word: `ext 73 (3,133) ; ext 70 (3)` in front of the load at
`rom:0x3B7B6D`, and `move_to(0, 496, 504)` where the deleted spawn stood.

### 1. Result

| Ask | State |
|---|---|
| `test_map_load_is_covered` | GREEN. Record F covers its load with a fade. |
| `test_control_record_shows_the_hud` | GREEN after the scoping. |
| `test_form_survives_the_leader_change` | RED, one finding, `rom:0x89A9C0` in `fullpower_ssj`, as asked. |
| Every other test | green |

Agent's run: `Ran 1358 tests in 288.130s`, `FAILED (failures=1)`. The failure in full:

```
record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
appearance(character=4, set=61), entry 20, before leader(2), so appearance_revert undoes it
```

The agent notes the shell reported "exit code 0" for that run, the compound-command trap the brief names,
and that it read the file instead.

### 2. What changed

**The conversation moved onto the player.** Seven of the eight set 133 actor ops now name set 0. The eighth,
`spawn(133, 496, 504)` at `rom:0x3B7C41`, is deleted, because `ext 51` builds a new NPC and cannot address
the player.

| Op | Address | Now |
|---|---|---|
| `spawn(133, 496, 504)` | `rom:0x3B7C41` | DELETED |
| `face(133, 1)` | `rom:0x3B7C72` | `face(0, 1)` |
| `attack(133, 11, 100)` | `rom:0x3B7CA2` | `attack(0, 11, 100)` |
| `attack(133, 11, 100)` | `rom:0x3B7CDE` | `attack(0, 11, 100)` |
| `attack(133, 9, 100)` | `rom:0x3B7D80` | `attack(0, 9, 100)` |
| `attack(133, 9, 100)` | `rom:0x3B7DBC` | `attack(0, 9, 100)` |
| `face(133, 0)` | `rom:0x3B7E06` | `face(0, 0)` |
| `walk(133, 248, 568)` | `rom:0x3B7E6C` | `walk(0, 248, 568)` |

The walk is kept so the player follows the NPC's path. **LIKELY, not CONFIRMED:** `ext 53` reaching the
player is confirmed from the caller list, but no shipped ROM of ours has run a scripted walk on a player
object. The set-0 ops proven in our own ROM are `move_to`, `face` and `attack`.

The brief said "the six that take set 0" then listed seven. Seven is right; the count was the only error. The
brief's second deletion, the `remove(133)` in the tail, was already done in `DROPS` since v1.

**Why copies, not byte pokes.** `zigzag(133)` is two bytes and `zigzag(0)` is one, so every push gets shorter
and a record cannot shrink in place. Each of the five records is relocated whole with `scene_lib.relocate()`
and its single table word repointed, the shape `cellgames_ssj` already uses. The vanilla records are left
untouched, so a save state paused inside one still runs it to the end. Each has exactly one namer, checked
across the ROM, and none carries a base jump op.

**Set 132 is untouched**, its 11 actor ops and both `camera_follow(132)` ops.

**Record F is now the vanilla shape:**

```
fade_out(120) ; appearance(character=3, set=133) ; leader(who=3)
load_map_at(zone=6, area=100, var=1, x=248, y=568) ; face(set=0, dir=1)
camera(x=136, y=492, speed=2) ; fade_in(120) ; wait(60)
camera_follow(who=0) ; header_bit1(1) ; bar_show(set=28)
```

The fade is the fix. Spots untouched: player (248,568), Cell (244,504).

### 3. Two deliberate deviations

**The leader change stays IN FRONT of the map load.** `battle_start` puts form and leader after the load, per
the template, but `ext 70`'s body install is guarded (`sub_0800A680`: `CMP r4,#0` then `BEQ` on
`Sprite_CurrentDirectory`), and the map load is what builds the player from the roster. Arena v2 proved it:
it changed the leader with no load behind it and drew no Trunks at all. A new opt-in keyword
`form_before_load=False` leaves the default output unchanged byte for byte, pinned by a test, and record F
passes `True`.

The agent checked whether `cellgames_ssj` proves the template order and says it does NOT: its working start
runs `leader(0)`, so if Gohan already leads there the leader never really changes. Labelled LIKELY.

**The frame op names the view the load already set.** `map_load` builds the camera from the load point minus
`(0x70, 0x4C)`, so from (248,568) the view is already (136,492). The frame names that same point, so the
hand-back has nothing to move. The module's older `VIEW` of (136,456) would have panned 36 px on the reveal.

**Timing warning from the agent:** `fade_out(120)` plus `fade_in(120)` plus `wait(60)` is 300 frames, about
5 seconds, between the last line and first input. The owner cut a 120-frame wait earlier the same day for
being a long pause. Each is one constant in the module.

### 4. The two test-rule corrections

**Rule 3 now reads the appearance table** and flags only an entry whose flags bit 0 is set, because
`appearance_revert` skips the rest. Four of five findings were false alarms.

A new ROM fact the agent hit: the two handlers read their table base from **different literals**, holding
**different tables** in our build.

| Handler | Job | Literal | Table in the build |
|---|---|---|---|
| `appearance_of_set @0x080042BC` | set id to entry (the ext 73 path) | `rom:0x42F0` | `rom:0x800000`, 22 entries, `gohan_gi`'s |
| `appearance_revert @0x08003ED4` | flags and revert (the ext 70 path) | `rom:0x414C` | `rom:0x88DC54`, 23 entries, `ssj2_form`'s |

The tooling report classified against one table and got the right answer because the two agree today on `+0`
and `+1`. The rule now resolves each from its own literal, and a new test pins that they agree.

**Rule 5 is scoped** to a record that shows a bar AND either loads a map or sits in a table that ran
`header_bit1(0)`. All 13 findings are gone; the scope reads 16 records with zero failures, pinned by a test.
The HUD is read per TABLE, because `header_bit1(0)` is a latch, unlike a one-shot fade.

**What the narrowed rule still cannot know:** it models the VANILLA revert, and our build does not run it.
See section 5. It does not model the hook's own skips, so a form the hook protects still reads as lost.

### 5. `fullpower_ssj`: untouched, and a mitigation to weigh

**CONFIRMED from the built ROM.** `rom:0x3ED4` holds `00 4b 18 47` with literal `07 a9 89 08`, so every call
to `appearance_revert` jumps to `fullpower_ssj`'s hook at `rom:0x89A906`. The hook reads its table from its
own pool at `rom:0x89A9B4`, holding `0x0888DC54`, the same value `rom:0x414C` holds.

**CONFIRMED.** The hook's body holds `00 2e 03 d0` (`CMP r6,#0 ; BEQ`), then `05 2d 0a d0` (`CMP r5,#5 ; BEQ`)
and `14 2d 08 d0` (`CMP r5,#0x14 ; BEQ`), where r5 is the record's appearance entry. **Entry 0x14 is 20,
Goku's Super Saiyan, the exact entry in the one red finding.** So when r6 is non-zero the hook reverts neither
entry 5 nor entry 20.

**LIKELY, and this is the gap:** whether r6 is non-zero when `rom:0x89A9C0` runs was not read. If it is, the
module already protects the form and the one-line reorder is unnecessary.

Agent's recommendation: read r6's source before reordering anything. One more handler read, not a play test.

### 6. Not touched, as instructed

`fullpower_ssj`, `chamber_spar`, `BATTLE_START_EXCEPTIONS` (no module carries one), and the fighter spots.

### 7. The agent's own cross-check, independent of the suite

A per-op set census over the BUILT ROM, walking the ending table's reachable records:

| Set | Before `ending_fight` | After |
|---|---|---|
| 133, NPC Super Saiyan Trunks | 14 | **0** |
| 132, plain NPC Trunks | 13 | 11 |
| 0, the player | 0 | 8 |
| 28, Imperfect Cell | 12 | 3 |

Set 133's 14 is 8 in the conversation plus 6 in record 23. Set 0's 8 is the 7 repoints plus record F's
`face(0,1)`. A second shape, a raw byte scan for the `push 133` pairs, returns the same count before and
after, proving the vanilla records were left alone.

**What this does not cover:** nothing was run in mGBA. It cannot say whether set 133 animates correctly as a
player body rather than an NPC puppet.

### 8. For the play test

1. The conversation shows the current leader, not Trunks. Section 0.
2. Does the player WALK on command? Record 13 runs `walk(0, 248, 568)`, the one op never proven on a player.
3. The camera through the talk: the follow camera is on the player, so the view may pan with him.
4. The android fight: the deleted spawn carried the NPC's spot (496,504); the player stands at record 0's
   load point (384,552). Is he off screen, and do the four attacks connect?
5. The fight start: fade out, load behind it, fade back, control after a hold. Watch for any view movement.
6. The 5 second pause. Too long?
7. Trunks is Super Saiyan now, not base.
8. Does the Super Saiyan body animate as a player? Walk, attack, take a hit.
9. Beating Cell should still run the collapse, the ki blast, the tail and "The End."

### 9. Files

`scene_lib.py` (`battle_start` takes `form_before_load`), `patches\ending_fight.py`,
`tests\test_ending_fight.py` (40 tests), `tests\test_battle_start.py` (28 tests), `rows.md` (7 rows, tag
`AR5`), and two listings in `scripts\one-time\2026-11-06-arena-v5\`. No new module, no new build list.
