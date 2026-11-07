# A test path to the finale, 2026-11-07

Two tools so a finale rung stops costing the owner a full playthrough: a `loadstate` step in the capture
harness, and a save that sits one A press from the ending. Both are built, and the harness then drove
itself from a cold boot to the Cell fight on map 7,100 and photographed both game-over cards.

| | |
|---|---|
| Harness | `scripts\permanent\emu\capture.py`, `scripts\permanent\emu\capture.lua` |
| Save tool | `scripts\permanent\rom\log2_save.py`, presets `farewell` and `farewell_test` |
| The owner's ROM and save | `builds\mockups\2026-11-07-finale\` |
| Tests | `test_capture.py` 46 tests, `test_save.py` 36 tests, all green |
| Throwaway | `scripts\one-time\2026-11-07-finale-testpath\` |
| Capture runs | `scratch\capture\finale*`, `job_0*`, `job_1*`, `job_2*`, `drive_*` |

---

## 1. The owner's steps to the Cell fight

Open this ROM. Its save sits beside it under the same name, so mGBA pairs them.

```
builds\mockups\2026-11-07-finale\log2_gameover_v1.gba
builds\mockups\2026-11-07-finale\log2_gameover_v1.sav
```

1. **Continue, slot 1.** Gohan stands on Dende's Lookout, 32 px below Dende. Slot 2 is the same spot,
   the spare run. Slot 3 is the Capsule Corp save point.
2. **Hold Up for about half a second, then press A.** The farewell starts at once.
3. **Tap A** through the farewell, the Shenron wishes, Goku's goodbye and Gohan's flight home.
4. **Tap A** through the credits. They roll over East District 439 and they are long.
5. Trunks arrives in the future and fights **Android 18**, then **Android 17** (EXPECTED: I never saw
   17's fight, see section 5), then **Cell on the plateau**. No save point lies between the farewell and
   the ending (B0985), so a loss costs the whole run.
6. To see the game-over cards, lose to Cell.

Measured under capture, with A tapped for 3 frames in every 18 and no human waiting: boot to control on
map 9,1 is about **3,400 frames**, and the A press on Dende to Trunks arriving on the android map is
about **23,400 more**, roughly **6 and a half minutes** of game time.

> [!WARNING]
> **Take a save state the moment the Android 18 fight starts, as well as when Cell's does.** Every macro
> run on the real-strength save lost that fight, and there is no save point behind it. Section 5 holds
> the numbers.

---

## 2. `loadstate`, the mirror of `savestate`

```
loadstate <path>        # a BizHawk .State, normally the first step of a job
```

`capture.lua` calls `savestate.load` and **raises unless it returns true**. That matters more than it
reads: the 2026-10-30 probe `scratch\capture\probestate\state.txt` measured that `savestate.load`
answers a missing file and an mGBA `.ss1` with a plain `false` and raises nothing. An unchecked load
would run the job from a cold boot while every later step reported a confident wrong picture.

`check_loadstates` refuses three things before `EmuHawk.exe` starts, and `--dry-run` runs the checks.

| Fault | Message |
|---|---|
| the source does not exist | `the loadstate source does not exist: <path>` |
| not a BizHawk state | `not a BizHawk state: <path>. BizHawk cannot load an mGBA .ssN state, and it reports the refusal as a false return, not as an error.` |
| made on another ROM | `the state belongs to another ROM: <path> carries crc32 0x1c7733dc and log2_gameover_v1.gba is crc32 0x2d3f7aab. A state loads only on the ROM that made it.` |

All three were fired live, not only in tests. A `loadstate` as step 1 of a job loads correctly, so no
warm-up frames are needed: nine runs did it.

### The ROM mismatch IS detectable, and here is where the answer lives

The brief asked whether the tool can tell that a state came from a different trial build. It can, from
the state file alone. A BizHawk `.State` is a zip of four entries, and `Core.bin.zst` is Zstandard,
which `compression.zstd` in Python 3.14 reads. **The u32 at offset 12 of the decompressed core is
`zlib.crc32` of the whole `.gba` file**, and the 12 byte ROM title sits at offset 20.

| State | crc32 it carries | ROM | crc32 of the file |
|---|---|---|---|
| `card4_gohan_arrival.State` | `0x1c7733dc` | `log2_poc_r40_chapters_v10.gba` | `0x1c7733dc` |
| `scratch\capture\states\after3200.State`, written by this task | `0x2d3f7aab` | `log2_gameover_v1.gba` | `0x2d3f7aab` |
| | | `log2_plateau_v4.gba` | `0x3a484edb` |

CONFIRMED. Two states, three ROMs, every pairing agrees, so the guard is a comparison and not a guess.
No sidecar file is needed. The words before offset 12 are NOT identified: offset 8 is not the mGBA BIOS
checksum, so read nothing into them.

### What the harness still cannot do

The owner's mGBA `.ss1` states can **never** be loaded. mGBA writes a PNG and BizHawk writes a zip, and
the 2026-10-30 probe measured BizHawk returning false on one of his states. The two emulators share the
`.sav` and nothing else, which is why the shortcut below is a save file and not a state.

---

## 3. What gates the ending, and what fires it

The ending is a script sequence, so **no save can start inside it**. The last point a save can hold is
the step before the trigger, and the `farewell` preset is that step.

| | |
|---|---|
| The gate | story flag 195 set (Cell beaten) and flag 196 clear (B0596) |
| The trigger | map 9,1 item 4 `rom:0x403F60`, Dende `set:36` at (760,416), condition `0x000100C3` = "flag 195 set" |
| What it starts | talk table `rom:0x3DD044`, 91 words |
| Where 196 is set | record 87 `rom:0x3DCEDC`, the op at `rom:0x3DCEF9` |
| The hand-off | record 88 `rom:0x3DD03C`, a type 5 jump into the ending table `rom:0x3B8140` |

Record 87 is one record that sets flag 196, flies Gohan home across a chain of `load_map_fade` ops, and
ends `fade_out(300) ; ext125`. So ONE A press runs everything after it. CONFIRMED: the item bytes, the
table decoded end to end, and the whole chain then played under capture.

**Flag 196 is deliberately NOT set in the preset.** Setting it spawns the ending's map NPCs and nothing
else (B1174, B1205) and leaves the ending script unrun. That is exactly the preset that looks right and
plays wrong.

### The order inside the ending, measured

Map 9,7 for the Lookout gathering, about 7,000 frames. Then record 87's flight, whose sampled maps
include 9,1, 4,79, 3,3, 8,32, 11,1 and 2,1. Then **the credits**, which roll for about 11,000 frames
while the map still reads 2,1. Only then comes map 1,100, the `future_androids` clone that holds the
Android 18 fight.

The credits run BEFORE the Trunks epilogue. That is worth knowing before anyone waits on a dark screen
and calls it a hang.

### The shortest real path from a cold boot

```
title -> A -> file select -> A (slot 1) -> chapter card -> map 9,1 -> Up -> A
```

There is no shorter honest path. The farewell, the credits and the two android fights all sit inside
the one sequence that the A press starts.

---

## 4. The two presets

`log2_save.py build <base.sav> <out.sav> --set farewell` and `--set farewell_test`.

| Preset | Slots | For |
|---|---|---|
| `farewell` | 1 and 2 at map 9,1 (760,448), 3 the Capsule Corp save point | the owner's play test |
| `farewell_test` | all three the same spot, party at 9999 HP, 9999 EP, STR and POW 200.00 | capture runs only |

(760,448) is 32 px below Dende. Every collision cell in a 160 px square around Dende is open except two
prop cells at y 360, so the spot cannot trap him.

Slots 1 and 2 hold the same state on purpose. No save point lies between the farewell and the ending
(B0985), so a lost run costs the whole thing and a spare slot is the only cure.

> [!NOTE]
> **END is left at its level 40 value in `farewell_test`, and that was learned the hard way.** The first
> try raised all three stats to 200.00, and the ending's Android 18 then took Trunks from 9999 HP to 0
> inside about 1,300 frames (`scratch\capture\job_16_tbrawl`). A defence stat that kills you is the
> shape of an incoming damage value going negative and then being read as unsigned. The fix was to
> raise only the two attack stats. The cause is NOT measured and no handler was read.

**`farewell_test` is not a play test.** A run on it proves the chain and the cards, never the balance.

---

## 5. The automated run: map 7,100 reached, both cards photographed

**Reached.** `0x03002080` reads `0764`, zone 7 area 100. Proof in
`scratch\capture\finale19_proof-20261107-160215`.

| Proof | Value |
|---|---|
| map info word | `0764`, three reads across one run |
| screenshot | `shots\p3_fight.png`, Super Saiyan Trunks facing Imperfect Cell on the grassy plateau |
| actor walk | `set 28` (Imperfect Cell, B1207) at (244,504), player `set 133` at (248,568) |
| the fight live | `scratch\capture\job_21_cellbar-20261107-160354\shots\y_last.png`, the boss bar up |

**The Android 17 fight was never observed.** `set 9` was still on the map at frame 67,719 with the boss
bar at 0 px, gone by frame 68,007, and the map read `0764` by frame 68,295. No shot and no bar reading
shows a fight with him. What removed him is unmeasured, so owner step 5 names him as EXPECTED.

**Both game-over cards, in play.** `scratch\capture\finale22_loss-20261107-160637`.

| Shot | What it holds |
|---|---|
| `L5_card1.png` | `Cell takes the time machine` / `into the past...`, two lines, the break after "machine" |
| `L6_card2.png` | `The nightmare is just beginning.` |

The loss happened on map 7,100, the map then read `0107` (the death screen), and the two cards came up
in place of `@^You have died!`. That closes the one thing the game-over task could not close, and it
also closes its open link: nothing overwrote `0x03002080` between HP 0 and the table run.

> [!WARNING]
> This run is **ASSISTED**. It used the `farewell_test` party and one `write` step. It proves the chain,
> the map test and the two cards. It proves nothing about whether any fight is fair.

### What it took, and what that says about the fights

| Try | Result |
|---|---|
| A-mash from a cold boot, real save | reaches map 1,100 at about frame 26,800, then Trunks dies to Android 18 |
| hold one direction and punch | the player walks PAST her and punches the wall. She does not chase |
| punch in all four directions | the player never moves at all. A punch lasts 16 frames and swallows the direction press that follows it |
| walk, then punch, 48 punches at STR 200.00 | the boss bar moved **0 pixels** of 212 |
| walk, then **ki blast (B)**, about 24 presses | the bar emptied and `set 11` left the world |

**The ki blast killed her. CONFIRMED**: about 24 B presses at POW 200.00 took the bar's red pixel count
from 212 to 0 and removed `set 11` from the world.

**The punch result is a measurement, not a cause.** 48 punch presses at STR 200.00 moved the bar 0 px of
212, and that is all it says. Three causes are still open and my data separates none of them:

1. **Contact.** She knocks the player back, so each round ended 63 to 147 px away against a 26 px reach.
   How many of the 48 presses were made in contact is unknown.
2. **A STR overflow.** STR 200.00 could wrap the same way END 200.00 appears to.
3. **The punch doing no damage to her.**

The ki blast worked from range, which fits all three. **Nothing here was tried at the level 40 stats**,
so this is not yet a finding about `future_androids`, and I changed nothing in it.

Two more things showed on the real-strength save, and both are flagged, not fixed.

- Trunks drops from 1181 HP to 0 in about 2,000 frames of toe to toe fighting with Android 18
  (1181, 736, 375, 0 at 40-cycle samples, `scratch\capture\job_13_brawl`).
- **Super Saiyan Trunks reverts to base form mid-fight**: `set 133` at cycle 90 and `set 132` at cycle
  170 of one run. The ki pool at EP 135 is the likely cause and it is NOT measured. The 9999 EP of
  `farewell_test` hides this, so the owner will meet it and I will not.

### The driver

`scripts\one-time\2026-11-07-finale-testpath\drive.py` is the closed loop: load a state, read where
everyone stands, walk toward the nearest enemy, attack, save a new state, repeat. One round costs about
10 seconds, because `loadstate` resumes at the fight instead of booting. It is one-time code. If the
next rung needs it again it is worth promoting into `scripts\permanent\emu\`.

---

## 6. `write`, the assisted lever

```
write <addr> <width> <hex>        # width 1 to 8, hex exactly two digits a byte
```

`check_writes` refuses any address that does not lie wholly inside EWRAM (`0x02000000`, 256 KB) or
IWRAM (`0x03000000`, 32 KB), so a job can change a game value but never a register, the ROM or the
BIOS. The Lua side reads every write back and prints both, because a write to a word the game rewrites
each frame looks exactly like a write that never landed.

It exists because a 9999 HP Trunks cannot lose, and the game-over card can only be seen by losing. The
one write of this task was `write 0x03000EF0 2 0100`, Trunks to 1 HP, run after the Cell bar was up.
It has to run after the bar is up, because the ending's `ext 70 (3)` refills him from the save record.

`0x03000EF0` is Trunks' live HP. It is `0x03000E90 + 0x0C + 3 * 28`, it tracked every hit across four
runs, and death followed it reaching 0.

**Any run that uses `write` is an assisted run and has to be reported as one.**

---

## 7. Tests

`test_capture.py`, 46 tests, 15 new.

- `loadstate`: it parses and emits forward slashes, two paths are refused, a missing source is refused,
  a PNG `.ss1` is refused, a state from another ROM is refused, a state from this ROM is returned, a
  job with no `loadstate` reads no ROM, `rom_crc` is the zlib crc of the whole file, and the real
  `card4_gohan_arrival.State` names its own ROM.
- `write`: IWRAM and EWRAM writes are returned, a write that runs off the end of IWRAM is refused,
  writes to a register, the ROM, palette RAM and address 0 are refused, and six malformed forms are
  refused.

`test_save.py`, 36 tests, 6 new: slots 1 and 2 stand 32 px below Dende on map 9,1, flag 195 is set and
196 clear in both presets, slot 3 is the Capsule Corp save point, `farewell_test` is three copies of
one spot, its party is out of the level 40 range on purpose while its END is NOT raised, and the play
preset carries the ordinary level 40 party.

Two capture tests check BizHawk's own file format rather than my code: the real state's crc32 and the
zip entry names. If BizHawk changes either, those tests fail instead of the guard going quiet.

**Full suite: 1632 tests, 365 s, exit 1.** One failure, three skips, one expected failure. The failure
is `test_battle_start.BattleStartTests.test_form_survives_the_leader_change`, the known one named in my
brief. The `test_future_androids` death-table failure that my brief also named PASSED on this run. Three
other agents were editing the tree while it ran, so read the result with that in mind.

---

## 8. What I could not prove, and the next levers

| Open question | State |
|---|---|
| Whether the punch can hurt Android 18 | Open. 48 presses moved the bar 0 px, but contact and a STR 200.00 overflow are both unruled out, and level 40 stats were never tried |
| The Android 17 fight | Never observed. `set 9` left the world with the bar at 0 px and 7,100 followed about 288 frames later |
| Why Super Saiyan reverts mid-fight | Not measured. The ki pool at EP 135 is a guess |
| Why END 200.00 got Trunks killed | Not measured. The unsigned-damage reading fits and no handler was read |
| The Cell fight at real strength | Never played. Every run past Android 18 used the boosted party |
| The enemy HP field in RAM | Not found. The boss bar red pixel count was used instead |
| `emu\` in `docs\tool-index.md` | The index has no `emu` section, so `capture.py` and `actors.py` are not listed. Fixing it means editing `make_tool_index.py`, which is outside my lane today |

---

## 9. Files

| File | What |
|---|---|
| `scripts\permanent\emu\capture.py` | the `loadstate` and `write` steps, `rom_crc`, `state_rom_crc`, `check_loadstates`, `check_writes` |
| `scripts\permanent\emu\capture.lua` | the `loadstate` handler, which raises unless the load returns true, and the `write` handler, which reads every write back |
| `scripts\permanent\rom\log2_save.py` | presets `farewell` and `farewell_test`, story `farewell_test` |
| `scripts\permanent\tests\test_capture.py` | 15 new tests |
| `scripts\permanent\tests\test_save.py` | 6 new tests |
| `scripts\one-time\2026-11-07-finale-testpath\dende_floor.py` | the collision cells around Dende |
| `scripts\one-time\2026-11-07-finale-testpath\make_job.py` | build a long A-macro capture job |
| `scripts\one-time\2026-11-07-finale-testpath\make_fight.py` | build a two-phase approach-then-brawl job |
| `scripts\one-time\2026-11-07-finale-testpath\drive.py` | the closed-loop fight driver |
| `docs\tasks\2026-11-07-finale-testpath\rows.md` | bible rows, tag `FTP` |
