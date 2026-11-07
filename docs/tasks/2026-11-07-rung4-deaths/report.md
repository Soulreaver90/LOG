# Rung 4: the death beats

Built 2026-11-07. ROM `builds\mockups\2026-11-07-plateau\log2_plateau_v7.gba`,
SHA-1 `5e28c890520e47ef1dccbc2639d49a771e3a7d60`, save paired and byte identical to v5's.

> [!WARNING]
> **v7 cannot be rebuilt from git alone.** Its build list pulls in `plateau.py`, which is still
> UNTRACKED. v7 holds it at SHA-1 `a7aae2d9f8bceea8361fef43192dc7125469fb25`, unchanged since
> 12:21 PM, which is the same file v5 and v6 were built from. A rebuild after that file is
> committed or changed will not match this SHA-1.

> [!NOTE]
> **v6 was built first and is superseded.** Its walk-in landed Android 17 inside a building 20 % of
> the time. The census in section 5 found it, the offset changed, and v7 is the ROM to play.

---

## 1. What changed

Only `scripts\permanent\patches\future_androids.py` and its test. The two death records,
which are word 0 of each android's own event table, were rewritten.

| v5 | v7 |
| --- | --- |
| `ext 88` ; `header_bit1(0)` ; `pose(set,3)` ; `wait(60)` | the same four ops |
| `fade_out(30)` | **gone** |
| `remove(set)` under the fade | the blast removes her |
| `move_to(0, 496, 504)` ; `face(0, dir)` | **gone** |
| `camera(384, 368, 2)` ; `fade_in(30)` | **gone** |
| - | `face_alt(0, set)` ; `block_begin` ; `attack(0, set, 100)` ; `ext 60 (set)` ; `block_end` ; `remove(set)` |
| - | on Android 18's record only: the on-screen test, `jz`, and Android 17's walk-in |
| `wait(60)` | the same |

> [!NOTE]
> No item was added or removed, so every positional `ext 104` index is unchanged and the module's
> own item-count guard still holds.

---

## 2. "NO transition", and the vanilla beat does not transition either

The owner's emphasis is honoured literally. Neither death record carries `ext 31` (camera),
`ext 33` (camera hand-off), `ext 35`/`38`/`39` (map load), `ext 40`/`41` (fade), `ext 42`/`43`
(flash) or `ext 62` (teleport). A test enforces the whole list.

**The vanilla beat I copied does not transition.** Ending word 8 `rom:0x3B7C96` runs two `ext 63`
groups: the first knocks Android 18 down with `pose(11,2) ; pose(11,3)`, the second blasts her with
`attack(133, 11, 100)`, polls `ext 60 (11)`, applies damage and ends `remove(11)`. There is no fade,
no camera op and no map load anywhere in that record. So "she collapses, Trunks blasts her" is
vanilla's own beat with the attacker changed from the removed NPC 133 to the player.

The v5 fade was ours, not vanilla's. Its only job was to hide a snap back to the staging the
cutscene used to have: the player teleported to (496,504) and the camera parked at (384,368).
Nothing downstream needs that staging:

- words 9, 10 and 12 are text records;
- word 11's `ext 104` builds Android 17 wherever he is standing;
- word 13 opens with vanilla's own `wait(60) ; fade_out(180)`, which is rung 3's territory and was
  left alone.

That is the "do not inherit vanilla's architecture" rule applied: the camera hand-off existed only
because the scene had been built on an NPC, and the player does not need it.

---

## 3. "Is Android 17 on screen": the engine cannot answer, so I built the equivalent

### What I checked, in two independent shapes

**Shape A, the stack profile.** All 145 ext handlers are profiled from the byte-exact disassembly in
`docs\research\scene-vm-ext-ops.md`. Eighteen return a value. I opened every one:

| op | what it returns |
| --- | --- |
| 0-3 | the four scene variables at `0x03001FB0` |
| 4-7 | `Opcode_PushOperandOne` to `Four` |
| 8-10 | bytes `+0`, `+1`, `+2` of the struct at `[global + 0x10]` |
| 11, 12, 75 | byte `+0` of the struct at `[global + 0x20]` (the leader), and two table lookups on it |
| 13-16, 105-108, 126, 129 | s16 fields `+0xC`, `+0xE`, `+0x10`, `+0x12` of a 28-byte record |
| 17, 18 | `Random_Scale`, `Random_Below` |
| 19, 20, 21, 22, 23 | the flag bitmap, an item count, `Character_GetLevel`, a visited bit |
| 131-133 | the level-up stat gains |
| 143 | **an actor's spot** |

**Shape B, a literal-pool search.** I searched the whole code region for the five words a camera
reader would need: `0x03001090` (the view struct), `0x083ED65C` (the pointer to it), `0x03000FF4`
(the live camera word), `0x030020C0` (the follow camera) and `0x030020F4`. Every loader is a
WRITER. The only ext handlers among them are ext 31, 33, 34 and 35, and all four are consumers that
push nothing. No getter calls any function that holds one of those literals.

**The two shapes agree: no ext op reads the camera or the view.** So there is no engine answer to
reach from a script. CONFIRMED for the 145 handlers by shapes A and B. Limit: callees more than one
level below a getter were not searched, so an op that reached the camera through two helpers would
not appear in either shape.

### The equivalent I chose, and why

`ext 143 (set)` pops a set, resolves it with `Sprite_Select @0x08009370`, calls
`Point_LoadScaled @0x0800791A` and pushes the spot PACKED as `(x << 16) | (y & 0xFFFF)`.
CONFIRMED from `sub_08009E80`.

Three facts make the test honest:

1. **`Sprite_Select(0)` IS the player.** `ADD r1,r0,#0 ; BNE loc_0800937E` falls through to a global
   player pointer and returns it with no search. CONFIRMED.
2. **The player stores his spot at the same offsets as an NPC.** `Point_LoadScaled` reads `+0x158`
   and `+0x15C`, and the class chain is `sprite root > mover (x/y 8.8 at +0x158/+0x15C) > combatant >
   player` (bible `B1710`). The face-the-player step reads the live player at those offsets too
   (`B1173`). CONFIRMED.
3. **Android 17 never moves.** He is an NPC at his item spot (520,408) whose only step struct turns
   him toward the player. So "is 17 on screen" is entirely a question about where the player is.

The follow camera draws the player at screen (112,80) on a 240x160 view (`B1144`, measured in
pixels). So the test is: is the player inside a box around (520,408)?

```
V0 = ext143(player)                         the packed player spot
V1 = V0 - packed(520,408)                   dx << 16, right to 1 px
V2 = (V0 * 65536) - (408 << 16)             dy << 16, EXACT
off = (V1 > 88<<16) or (V1 < -88<<16) or (V2 > 52<<16) or (V2 < -52<<16)
jz 13                                       on screen: skip the walk-in
```

- **Why no `div`.** The divide's operand order is only LIKELY (`B1966`), so the test never divides.
  The y half is exact because the engine multiplies in 32 bits: `V0 * 65536` shifts the x half
  straight out and leaves `py << 16`.
- **Why the x half is 1 px out.** The low halves can borrow, so the high half of `V0 - Q` is
  `px - qx` or `px - qx - 1`. The box is 88 px wide on each side, so 1 px does not matter.
- **Why the box is smaller than the real view.** 88 and 52 against real half extents near 112 and 80.
  The test errs toward walking him in. An unneeded walk-in reads fine; a skipped one would leave the
  player listening to nobody.

> [!WARNING]
> **Known error band.** The map view clamps the camera at the map edges (`B1143`), so near an edge
> the player is no longer drawn at screen (112,80) and this test is wrong by up to the clamp
> distance. I did not bake map 1,100's clamp extents in, because the error only ever adds a walk-in.

### The branch is RUN, not just pinned

`test_future_androids.run_branch()` executes the record's VM ops in 32 bits with `ext 143` answering
a given spot, and reports which arm ran, the point `ext 144` unpacks, and the stack depth at the end
op. `scene_harness` cannot do this job: its ext handling clears the whole stack, so a record that
reads a value back with `ext 0` to `ext 3` loses it. The 32-bit wrap matters, because the exact-dy
trick depends on the multiply dropping the x half.

| player spot | result |
| --- | --- |
| (520,408), standing on 17 | no walk |
| (608,408), inside the right edge | no walk |
| (610,408), outside it | walk to (650,408) |
| (430,408), outside the left edge | walk to (470,408) |
| (520,460), on the bottom edge | no walk |
| (520,461), one px past it | walk to (560,461) |
| (600,400), the borrow case | no walk |
| (496,504), the talk spot | walk to (536,504) |
| (496,648), the player start | walk to (536,648) |

The stack depth at the end op is 0 on every one of those spots and on Android 17's own record. That
is load bearing: `@0x0800B19C` turns a single leftover value into the next table index.

**A negative control is in the suite too**, because a green branch test proves nothing on its own.
It widens the y half extent from 52 to 1000 IN THE BUILT BYTES, using an encoding of the same
length so no later op moves, and asserts that the talk spot stops walking him in. If the branch were
decided by anything other than the box, that control would still walk him.

### The entrance

`ext 144 (set, packed)` walks an actor to a packed point. `sub_08009EBA` and `ext 53 walk`
`sub_08009D4A` end in the same `Record_NewFromWords(0, {x,y})` and the same `Queue_Append`, so
ext 144 IS a walk. CONFIRMED, instruction for instruction. Vanilla pairs it with `ext 143` three
times: `rom:0x3C56D9` (map 4,30, set 101) and two sites on map 4,41 (set 82), each saving a spot,
walking the actor away and walking him back.

He walks from (520,408), which is off screen by hypothesis, to the player's spot plus (40,0), a
single folded constant `40 << 16 = 2621440` added to the packed player spot. That lands him at
screen (152,80): on screen and level with Trunks, 40 px to his right. `ext 56 face_alt (9, 0)` then
turns him to the player, and it runs on BOTH arms of the branch because his face-the-player step
struct does not tick while a scene plays.

### The dialogue is vanilla's own

The record hands back at ending word **9**, `rom:0x3B7D2A`: **"It can't be!"** on **portrait 28**,
the portrait word 1 gives as "ANDROID 17". Word 10 `rom:0x3B7D3C` is Trunks' "And this is for all
the people you've killed!". Nothing was written, moved or invented. After Android 17 the hand-back
is word 12, Trunks' "Now there's just one more thing that needs to be done."

---

## 4. The blast, and its precedents

```
face_alt(0, set) ; block_begin ; attack(0, set, 100) ; ext60(set) ; block_end ; remove(set)
```

- **The player as attacker is vanilla, not an inference.** Record `rom:0x3E5224` (map 11,6, table
  `rom:0x3E6078` word 31) fires `attack(0, 28, 100)` three times and polls `ext 60 (28)`.
  `BLAST_SPEED` is that record's own n. Of the 29 `ext 96` sites the map walk reached, 3 have
  attacker 0. CONFIRMED.
- **A beaten enemy still acting is vanilla too.** Android 18's OWN death record `rom:0x3D8BC4` poses
  her down, hides the bar and the HUD, stands her up and has HER fire `attack(11, 0, 100)` at the
  player with `ext 60 (0)` polling a target at a distance the player chose. CONFIRMED.
- **Why `face_alt` first.** The blast spawns at the attacker's hurtbox edge BY FACING (`B1964`), so
  a Trunks facing away would fire from behind himself. `ext 56 (a, b)` turns a toward b's
  `+0x158/+0x15C` once (`B0741`). LIKELY, not confirmed: `B0741` found no vanilla site with an
  enemy as b, though `Sprite_Select` finds our enemy by its set id exactly as `pose` and `remove`
  already do in this module.
- **What I did NOT copy.** Vanilla word 8 group 2 also applies damage (`ext 17 ; add ; ext 112`) and
  three `ext 94` knock-backs to a target that is an NPC. Our android is a real enemy at HP 0 whose
  death event is already running, and I cannot prove that damaging her again will not re-enter it.
  Dropping those ops costs nothing visible and removes an unprovable risk.

---

## 5. The defect the first build had, and the measurement that found it

The walk-in target is computed from the player's live spot, so nobody hand-checks the line. I read
the walk command end to end to find out what a blocked walk does:

- the walk command's vtable is `0x08024A8C` (`B0691`), its done check is `@0x08010940`
  (`ldr r0,[r0,#0x8] ; bx lr`) and its tick is `@0x0801090A`, which stores the mover's own answer
  into command `+8`;
- the walk move state `@0x0800D584` gives the mover the vtable `0x0802504C`, whose `+8` step is
  **`@0x0800D28C`**. I read it. It adds the fixed velocity at mover `+4` and `+8` to the actor's
  `+0x158` and `+0x15C`, decrements the u16 frame counter at mover `+0x10`, and **tests nothing
  else**. On the frame the counter reaches zero it loads the s16 target at mover `+0xC` and `+0xE`,
  shifts each left 8 and stores them straight into `+0x158` and `+0x15C`, SNAPPING the actor onto
  the target, and returns 1. Every other frame it returns 0;
- the frame count is `max(|dx|,|dy|) * 256 / speed` (`B1917`), and ext 53's speed is 0x100, so the
  walk is 1 px a frame.

Bible row `B0686` says the same thing, but it says it about ext 54. This reading is the ext 53 path,
which is the path `ext 144` queues.

**So a blocked walk cannot freeze: the done answer is the counter, never arrival. It can only END
somewhere closed**, and word 11's `ext 104` would then build enemy Android 17 inside a building,
where the player may not reach him.

`scripts\one-time\2026-11-07-rung4-deaths\landing_census.py` counts that over every one of map
1,100's 5,683 open cells:

| offset | closed landings, whole map | closed landings within 160 px of the talk spot |
| --- | --- | --- |
| (40,-40), the v6 design | 1,120 (19.7 %) | 302 of 1,372 (22.0 %) |
| **(40,0), what v7 ships** | **584 (10.3 %)** | **67 of 1,372 (4.9 %)** |

The street is a vertical corridor lined with buildings, so going UP walks into them. Going level
stays in the corridor. From (40,-40) the talk spot itself, Android 18's spot and Android 17's spot
all landed CLOSED. From (40,0) all four named spots land OPEN.

The residue is honest: 4.9 % of the cells near the fight still land closed, all of them where the
player is hard against the right-hand buildings.

---

## 6. What I could not prove

| claim | level | why |
| --- | --- | --- |
| The blast always reaches a downed android, so `ext 60` always ends | LIKELY | `B1963`: the scene blast's velocity is fixed toward the target's hurtbox centre at the fire tick, it does not home and it is NOT removed off screen. Vanilla already polls `ext 60` on a player-chosen distance (`rom:0x3D8BC4`). But `B1814` records a freeze when a scene blast misses, and I have not play-tested it |
| `ext 56 face_alt` works with an enemy object as b | LIKELY | `B0741` found no vanilla site with an enemy as b |
| Android 17 can land inside a building | CONFIRMED, and measured | 10.3 % of the map, 4.9 % near the fight. Section 5. He walks THROUGH walls on the way, which is vanilla's own behaviour for every scripted walk |
| A far Android 17 arrives in a reasonable time | CONFIRMED by arithmetic | `B1917`: frames = `max(|dx|,|dy|) * 256 / speed`, and ext 53's speed is 0x100, so 1 px a frame. 240 px is 4 seconds |
| The on-screen test near a map edge | known error band | the camera clamp, section 3 |
| Nothing was rendered | - | `map_view` is mid-fix in another agent's hands, so no picture of this map would be right. The census reads the collision frame directly instead |

---

## 7. Evidence the build carries it

Read back OUT of `log2_plateau_v7.gba` with
`scripts\one-time\2026-11-07-rung4-deaths\readback.py`, following the live map table literal
`rom:0xEBD8` to map 1,100, its item list, each enemy item `+0x14`, the event struct `+4` and the
death table's word 0:

```
===== item 2: enemy Android 18 (set 11) rom:0x940A80
  event struct rom:0x940A78 -> death table rom:0x940998 -> word 0 record rom:0x9408D0
  the record hands back at ending word 9
    rom:0x9408D3  ext88()
    rom:0x9408D7  header_bit1(value=0)
    rom:0x9408DD  pose(set=11, state=3)
    rom:0x9408E1  wait(frames=60)
    rom:0x9408E7  ext 56 (0, 11)        face the player at Android 18
    rom:0x9408E9  block_begin()
    rom:0x9408F1  attack(attacker=0, target=11, n=100)
    rom:0x9408F5  ext60(11)
    rom:0x9408F7  block_end()
    rom:0x9408FB  remove(set=11)
    rom:0x9408FF  ext143(0)             the packed player spot
    rom:0x940901  set_var(0)
    ... sub, mul, gt, lt, or over variables 0, 1 and 2 ...
    rom:0x940946  jz(13)                on screen: skip the walk-in
    rom:0x94094A  push 9 ; ext 0 ; push 2621440 ; add ; ext 144
    rom:0x940959  ext 56 (9, 0)         Android 17 faces Trunks, on both arms
    rom:0x94095D  wait(frames=60)
    rom:0x94095F  end

===== item 3: enemy Android 17 (set 9) rom:0x940AB0
  event struct rom:0x940AA8 -> death table rom:0x940A04 -> word 0 record rom:0x940960
  the record hands back at ending word 12
    (the same beat, no branch, and a closing face(0, 0) so Trunks turns to the camera)
```

The push_list values in the built record are
`[34079128, 65536, 26738688, 5767168, -5767168, 3407872, -3407872, 2621440, 9, 0]`, which are
`(520<<16)|408`, `65536`, `408<<16`, `88<<16`, `-(88<<16)`, `52<<16`, `-(52<<16)`, `40<<16`,
and the set and player ids of the closing `ext 56`. Every one is the designed constant.

> [!WARNING]
> `scene_lib.listing()` folds every pushed value into the NEXT ext op and names it from that op's
> own argument list, so `ext 56 (0, 11)` prints as `face_alt(set=0, dir=11)` and the push meant for
> `ext 144` prints as an argument of `ext 0`. The listing above is corrected from the raw bytes.

---

## 8. The suite

`py -3.14 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent`:
**1620 tests, exit code 1, `FAILED (failures=1, skipped=3, expected failures=1)`.**

`test_future_androids` is green at 43 tests, 8 of them new.

> [!WARNING]
> The one failure is NOT mine. It is
> `test_battle_start.test_form_survives_the_leader_change`, which reports
> `record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
> appearance(character=4, set=61) ... before leader(2)`. Nothing in that sweep touches the ending
> table or map 1,100. PROVED, not assumed: I swapped `future_androids.py` back to its committed
> version, ran `test_battle_start.py` alone, got the SAME single failure at the same address, then
> restored my file and checked its SHA-1. `test_battle_start.py` is an untracked file another agent
> added yesterday evening.

---

## 9. What the owner should check when he plays it

Play `log2_plateau_v7.gba`, not v6.

**The 18 beat**

- Android 18 drops where she died, not back at the cutscene spot, and the screen never goes black.
- Trunks turns to her and fires one blast, and she disappears when it lands.
- The camera never jumps: it stays on Trunks from the end of the fight through the whole beat.

**Both arms of the 17 entrance.** The box is 88 px wide and 52 px tall around where 17 stands.

- To see him STAND STILL: finish Android 18 while you are near 17's own row, within about
  50 px above or below it and not more than about 80 px to either side. He should not move, and he
  should just say "It can't be!".
- To see him WALK IN: finish her down by the start spot, or well off to one side. He should walk on
  screen, stop 40 px to Trunks' right and level with him, and only then speak.
- Android 17 is facing Trunks when he speaks, both ways round.
- The second fight starts where 17 is standing, wherever that turned out to be.

**The 17 beat**

- The same beat with no walk-in, then Trunks turns to the camera for "Now there's just one more
  thing that needs to be done."

**Three things that would be defects**

- A freeze after Trunks fires means the blast missed. Tell me where you were standing.
- A freeze while Android 17 walks in should be impossible, because the walk is counted and not
  guided. If it happens anyway, that is a finding worth the whole session.
- Android 17 stopping inside a building or behind a wall. Measured at about 1 landing in 20 near
  the fight. Tell me where you were standing and I will move the spot.
