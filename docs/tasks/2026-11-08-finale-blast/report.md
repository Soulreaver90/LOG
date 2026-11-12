# Report: the finale blast and Cell's death (rung 7), plus the second transition cut

Agent report, 2026-11-08. The harness blocked the agent from writing this file, so the controller
saved it verbatim from the hand-back message. `rows.md` beside it holds 15 FBL rows, unmerged.

**Trial ROM: `builds\mockups\future\finale_blast_wip3.gba`, SHA-1
`011dad1afea1d6f29f9aa9c22f6bbb10e2b129c9`**, with its `.sav` and `.log` beside it. Not named
`future_v3`, and `INDEX.md` is not edited: that is the controller's call.

**Suite: 1881 tests, 1 failure, the known `test_battle_start.test_form_survives_the_leader_change`**,
which predates all of this. Ran once at the end, redirected to a file, exit code quoted from the run
itself, never piped.

Controller check, same day: the ROM exists and its SHA-1 matches the claim byte for byte.

---

## 1. What it does

Round 2's Cell dies on the plateau. The bar and the HUD drop, a fade covers a new VERTICAL staging,
and the screen comes back on Cell above and Trunks below. Cell holds the Kamehameha pose and says
"Kamehame...". Trunks faces up and raises his arms. He shouts "THE NIGHTMARE IS OVER CELL!". A GOLD
beam fires straight up. A white flash, then three hit loops with explosions and screen rumble, then
the fifth block, the big explosion that removes Cell. A second white flash covers the power down to
base, he says his closing line, and the ending's own tail runs: track 15, the fade and "The End.".

New files: `scripts\permanent\patches\finale_blast.py`,
`scripts\permanent\tests\test_finale_blast.py` (24 tests, all green). Study scripts in
`scripts\one-time\2026-11-08-finale-blast\`.

---

## 2. The gold beam op

| piece | where | note |
| --- | --- | --- |
| gold op number | **146** | the live table held 146 words, 0 to 145 |
| handler, a copy of `@0x0800A3A2` | `rom:0x94D9FC` | loads the new vtable |
| command start, a copy of `@0x0801D788` | `rom:0x94DA48` | its builder call names the copy |
| builder, a copy of `@0x0801D84C` | `rom:0x94DAA0` | `mov r2,#0x1`: argument 6, the gold set |
| three `bx` trampolines and the pool | `rom:0x94DAE4` | the whole blob is 0x118 bytes |
| rebased command vtable | `rom:0x94D9E8` | 5 words |
| ext op table copy | `rom:0x94DB14` | 147 words |

**`chapter_cards` IS in this build list and had already relocated the ext table, so the module copied
the LIVE table, not the base one.** It reads the base out of pool `rom:0x921C`, finds the module whose
notes claim that address, checks that module declares it as one whole site, and copies all 146 live
words before appending one. Live table `rom:0x9399DC`, owner `chapter_cards`, 146 words. Copying the
base table would have silently thrown away the chapter card op.

### The rebased vtable, slot by slot, read back out of the ROM

`new = old + 0x0802521C - 0x0894D9E8`.

| slot | stored | resolves to | what it is |
| --- | --- | --- | --- |
| 0 | `0xFF6D9C89` | `0x08027671` | vanilla |
| 1 | `0x00000061` | `0x0894DA49` | **the gold start** |
| 2 | `0xFF6CFDF5` | `0x0801D7DD` | the vanilla tick |
| 3 | `0xFF6CFE51` | `0x0801D839` | the vanilla done |
| 4 | `0xFF6D8735` | `0x0802611D` | vanilla |

The vtable is FIVE words, not more: the next vtable is `0x08025230`, named by the literal
`rom:0xA740`, and the vtables in that region sit on a 0x14 stride. CONFIRMED.

### There is no bound to raise

The brief asked for the ext dispatch bound. **There is none.** Base op 2 `@0x08008F8E` and base ops
21 to 26 (`@0x08009130`, `@0x08009160`, `@0x08009190`, `@0x080091BC`, `@0x080091EC`, `@0x08009224`)
all read `[table + 4n]` with no `cmp` on n anywhere in the index path. All seven handlers were
disassembled, and a test asserts it on every build. That is also why `chapter_cards` added word 145
without touching a bound. CONFIRMED.

Worth recording: base ops 21 to 26 index TWO tables at the same op number, the handler table and a
PARALLEL table at `0x083B5F70` (which is `0x083B5D28 + 4 x 146`). Only the handler table moves. A new
op is reachable through base op 2 alone, which is the only op our records use. Both parallel pools,
`rom:0x9220` and `rom:0x92E0`, are checked and left alone.

### The copies are not byte copies, and a byte copy would have failed silently

Two measured reasons the brief did not name:

1. **Every pool literal sits OUTSIDE the body.** The handler loads from `rom:0xA418` and `rom:0xA430`,
   past its 0x46 bytes. The start loads from `rom:0x1D848`, past its 0x54. The builder loads from
   `rom:0x1D9CC`, past its 0x3E. A flat copy aims each `ldr rX,[pc,#imm]` at whatever follows it.
2. **Every `bl` into the base ROM is out of range.** A Thumb `bl` reaches about 4 MB and this code
   sits about 8 MB away.

So each body is re-typed instruction for instruction through `ssj2_form.assemble`, which lays its own
pool, and each call goes through a local `bx` trampoline. **Proved two ways in the test:**

- the built ROM is disassembled, each trampoline call is folded back into the plain `bl` it stands
  for, branch targets are normalised to instruction distances, and the result is compared with the
  vanilla listing INSTRUCTION FOR INSTRUCTION. Three deviations are declared and nothing else
  differs: the handler loads the new vtable and writes `stmia r0!,{r1,r2} ; sub r0,#0x8` as two
  `str`; the start's builder call names the copy; the builder's `mov r2,#0x0` is `mov r2,#0x1`;
- both builders are RUN on the `test_ssj2` interpreter from the same inputs and stopped where each
  calls the beam object `@0x080143A8`. r0 to r3 are identical, argument 5 is 0x400 for both, and
  argument 6 is **0 for vanilla and 1 for the copy**.

`ssj2_form.assemble` gained one additive branch, `asr` (format 1, the signed shift), and the
`test_ssj2` interpreter gained the matching one. Neither changes an existing encoding path; the
golden test confirms no ROM drift.

### Nothing vanilla moved

The three vanilla bodies, the colour byte `rom:0x1D870` and the vanilla vtable are byte for byte what
they were. A whole-prefix word diff of the build with and without this module says the ONLY base-ROM
words it writes are the two ext pool words, and those are `chapter_cards`' own declared sites, handed
on the way the map table and the scouter table are handed on. **Gohan's Cell Games Kamehameha stays
blue.** The shared OBJ palette is untouched and no art was made.

---

## 3. The scene

Table D2 is the plateau enemy's own death event, `rom:0x946774`. Word 0 held `ending_fight`'s record
K; words 1 to 6 were END. The chain now runs 0, 1, 2, 3, 4, 5, 6 and then 24, the vanilla
"@^The End." record, and 25, the vanilla exit. Words 24 and 25 are untouched.

| word | record | what it does |
| --- | --- | --- |
| 0 | `rom:0x94DD60` | bar off, HUD off, fade out, the vertical staging, Cell takes the Kamehameha pose, the view parks, fade in |
| 1 | `rom:0x94DDA4` | Cell, portrait 38: `Kamehame...` |
| 2 | `rom:0x94DDB4` | Trunks faces up, `pose(0, 4)`: the arm raise |
| 3 | `rom:0x94DDC4` | Trunks, portrait 101: `THE NIGHTMARE IS OVER CELL!` |
| 4 | `rom:0x94DDE4` | the gold beam up, three hit loops, the explosion, the power down |
| 5 | `rom:0x94DF20` | Trunks, portrait 100: his closing line |
| 6 | `rom:0x94DF94` | the ending's own tail, unchanged |

His closing line is one record with two box breaks, each replacing a space he wrote at a full stop:
`Now I can finally say that it's really over.` / `Thanks to you father, and to you Gohan.` /
`And especially to you Goku`. Widest box 205 px over 2 lines, against the 294 px over 4 that the
ending talk already renders. His shout carries ONE bang, which is his section 5 wording; the early
copy at `rom:0x3B7FF6` has five and is not reused.

### The death loop

Vanilla's Perfect Cell death, record `0x083EBE1C`, runs five blocks after its Kamehameha. **Three hit
loops plus the fifth explosion block**, per his ruling. Camera values 30, 30, 40 and then 80, which
are vanilla's own, in vanilla's own order. Vanilla's FOURTH hit loop, camera 20, is the one dropped.
Every `ext 94` effect offset is vanilla's, with set 28 for set 30.

**One op is ADDED to block 1, and it matters.** Vanilla's block 1 carries no `ext 57 (30, 2)` because
the 32-iteration loop in front of it already left Cell in the hurt pose. This record has no such loop:
Cell is holding the Kamehameha pose when the beam lands, and state 30 never ends, so without a pose op
he would take the entire first loop still charging. His words are "imperfect cell does the set28 a2 d0
animation, EACH loop with the smoke effect explosion", so block 1 now takes the same `ext 57 (28, 2)`
that blocks 2 and 3 already carry, in the same place in the block. A test asserts all three loops show
the hit anim. The agent found this itself after the first build and rebuilt for it.

### Two traps that would have hung the scene

- **`ext 57 (28, 30)` would wait for ever.** State 30's tick has no end call (bible B0688), so an op
  that waits for the state to finish never returns. Cell's Kamehameha pose uses `ext 121`, which sets
  a state and does not wait (B0750), the way vanilla's own seq 20 poses both fighters.
- **`ext 73` rebuilds the player object**, and the beam object holds the actor. The power down runs
  190 frames of scripted waits after the beam, and the beam runs 140. Arithmetic on the ops' own
  frame values, and a test asserts it.

### The music

He asked for "back to the credits music that normally plays". **This ending's own tail plays track
15**, at `rom:0x3B80DD`, the moment Cell dies. 37 is Perfect Cell's cue at `rom:0x3EBFF2`, a different
scene. So the module runs `ending_fight.tail` unchanged and track 15 ships. `ext 45` stays last, or
"The End." would draw black on black. That answers the spec's open question against `music(37)`.

---

## 4. The staging, with its proof

**Cell (424, 416) above. Trunks (424, 480) below. One column, 64 px apart, the approved arena gap
turned 90 degrees. Parked view (304, 344) at speed 40.**

Measured on `art\plateau\map_142.json`, his live file, through `plateau`'s own readers. The agent did
not copy it, edit it, or read his editor folder. The module refuses to write if any check fails, and a
test re-checks every one:

| check | result |
| --- | --- |
| his map | 4988 open cells, 4849 reachable, 1110 cells where BG0 or BG1 draws |
| Cell's envelope (44 left, 44 right, 56 up, 8 down) | every cell open, reachable, free of BG0 and BG1 art |
| Trunks' envelope (24, 24, 24, 8) | every cell open, reachable, free of BG0 and BG1 art |
| the beam column, 32 px wide, Trunks up to the view top | 90 cells, **not one** carries BG0 or BG1 art |
| the parked view | holds Cell head to foot and Trunks head to foot, 16 px margin top and bottom |

1830 vertical pairs pass every check. This pair sits on the walkable centre, (424,448).

---

## 5. The frame hold: what was measured, and the recommendation

**His frames are already on the player's body. No art swap is needed.** Sets 130 and 133 SHARE anim 4
direction 1 frame for frame: headers `0x36AB20`, `0x36AC30`, `0x36AD44`, `0x36AE4C` at records
`0x36B370`, `0x36B37C`, `0x36B388`, `0x36B394`. He named the row off set 130's sheet, and set 133 is
what the player wears here, so `frame_36AD44` is literally what shows. Set 132 does NOT share it.

**Anim 4 does not cycle. It plays once.** State 4's enter `@0x0800E0F8` sets the anim 4 row. Its tick
`@0x0800E10A` adds 1 to +0x12 a frame, stores frame = +0x12 >> 4 while +0x12 < 0x40, and at 0x40 puts
the actor back in state 0:

| ticks | frame |
| --- | --- |
| 0-15 | index 0, arms down |
| 16-31 | index 1 |
| **32-47** | **index 2, `frame_36AD44`, his firing frame** |
| 48-63 | index 3, `frame_36AE4C`, arms at the top |
| 64 on | anim 0, he stands |

So the brief's worry about "arms up and down during the beam" is not what happens: the arms rise once
and stop. His own reading, "we can repurpose it to make it look like he is shooting up", is what the
row does.

### What was built

Record B3 runs `pose(0, 4)`, which BLOCKS for the full 64 frames, so the raise plays out and his line
box opens after it. Record B5 fires the beam and overrides the forced state 30 on the very next op
with `ext 121 (0, 4)`, which is what both vanilla `ext 137` sites do and what the brief asked for. So
during the beam he raises his arms again over 64 frames, passing `frame_36AD44` at beam ticks 32 to
47, and then stands for the beam's remaining 76 ticks.

**That last line is the weak spot, and the only thing here the agent would not defend as finished.**

### The alternatives, measured

| option | what it looks like | cost |
| --- | --- | --- |
| **A, as built** | arms rise over the first 64 ticks of the beam, then he stands for 76 more | none |
| B, re-issue `ext 121 (0, 4)` twice | the raise repeats three times across the beam | the arms snap down at each restart |
| C, drop the override and keep state 30 | anim 18, the game's OWN beam pose, holds the whole beam | state 30 never ends, and both vanilla sites refuse to leave it running |
| **D, clone set 133 anim 18 dir 1 to his frame** | the forced state 30 holds `frame_36AD44` for every frame of the beam, with NO override op at all | set 133's anim 18 changes everywhere. Nothing in this build drives state 30 on set 133, so LIKELY free |
| E, clone set 133 anim 4 dir 1 to four copies of his frame | the raise becomes a hold, in B3 and B5 both | set 133's anim 4 changes everywhere, including the power-up beat in plateau's transform |

**The agent recommends D**, a one-line change once he says so. It uses the engine's own hold instead
of fighting it, keeps anim 4 free for the raise in B3, and puts his chosen frame on screen for every
frame of the beam. One trap for whoever builds it: the state 4 tick never clamps the frame index to
the anim's count, so a clone must keep its frame COUNT and change only the pictures. A `counts=1`
clone would read past the end.

**He decides by eye.** A is in the ROM now so he can see the beam first.

---

## 6. The second transition cut (the folded-in change)

Done, in `ending_fight.py`: `HEAD_WAIT` 30 to **10**, `HEAD_FADE` 90 to **60**, `REC13_SETTLE` 120 to
**20**. The vanilla head pair check still runs: the module reads `wait(60) ; fade_out(180)` at
`rom:0x3B7E4D` and refuses if it moved, and not one byte of the vanilla record changes.

**The agent verified the claim before building on it.** Record A decoded out of the shipped ROM at
`rom:0x94064C`: `wait(30) + fade_out(90) + wait(120)` = **240 scripted frames, 4.02 s**, plus the
camera pan (so "about 244" is right). After the cut: **90 frames, 1.51 s**. A test pins that 90.

**The old comment was wrong and is replaced, not patched.** It claimed the `wait(120)` "covers the map
load". It does not: the FADE covers the load, and the wait runs after it, under black that nothing
draws into, because the fade in lives in record A2. That is written in the constant block, in the
`arrive()` docstring step 4, in the module header note 0b, and in the test's own header. 20 frames of
margin are kept because v4 proved a load does not finish inside its own op and wipes what follows it;
vanilla's own load into a scene keeps no settle at all (B0748, B0877), so 20 is already more than
vanilla asks for. If anything renders half drawn, raise `REC13_SETTLE` alone.

`HEAD_FADE` is at the floor of 60 and the test asserts it never goes below.

**Does this work touch any of the five queued defects? No.** Three frame counts changed and nothing
else in record A. Defect 3 (Trunks' sprite at the bottom during the caption) is `move_to(0, 248, 664)`
and defect 4 (the HUD during the dialogue) is `header_bit1(0)`, both in record A and both untouched.
The later pass will be editing the same record, which is worth knowing, but no value it needs has
moved.

---

## 7. The build list and the shared pin

`finale_blast` is appended LAST to `scripts\permanent\build_list_trial_plateau.txt`, after `plateau`,
and the file's header comment is updated to say so (it still claimed "plateau runs LAST"). It must run
last for three reasons, and it refuses to run otherwise:

1. it copies the LIVE ext op table, so `chapter_cards` has to have run;
2. it reads `plateau`'s notes for table D2 and the enemy's death event;
3. it reads `ending_fight`'s notes for record K and uses its `tail()`.

`build_list.txt` and `build_list_dev.txt` are untouched.

**The `test_battle_start` rule 5 census does NOT move.** It stays at the 17 the dialogue agent set.
Rule 5's scope is a record that raises a boss bar AND either loads a map or sits in a HUD-hiding
table. Every record here drops the bar with `ext 88` and raises none, and table D2 was already a
HUD-hiding table because record K ran `header_bit1(0)`. The suite confirms it.

---

## 8. What was not done, and what is still a claim

- **The beam's travel time is NOT measured.** `BEAM_REACH = 20` frames is the hold between the beam op
  and the first hit. It is a beat, not a measurement, and it is one named constant.
- **Nothing here was seen on screen.** The gold colour, the beam firing up, the rumble, whether the arm
  raise reads as a shot, and whether the cut transition still feels long are all his eye.
- `builds\mockups\future\INDEX.md` has no row for this build. The scratch name is deliberate per the
  brief, and promoting it to `future_v3` is the controller's call.
- `docs\build-log.md` carries lines for `finale_blast_wip1` and `_wip2`, which the agent deleted from
  disk after rebuilding. The log is append-only history, so those lines stand. **`_wip3` is the one
  to play.**
- Files changed beyond the new module and its test: `ssj2_form.py` (+2 lines, `asr`),
  `test_ssj2.py` (+5 lines, `asr`), `ending_fight.py` and `test_ending_fight.py` (the second cut),
  `build_list_trial_plateau.txt` (one module line plus the header comment), `docs\tool-index.md`
  (regenerated, it now lists `finale_blast.py`).
