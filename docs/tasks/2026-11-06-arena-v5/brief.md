# Brief: arena v5, the scene runs on player-controlled Super Saiyan Trunks

Build task. Build a trial ROM and run the full suite once at the end. Follow `docs\tasks\global.md`.
**The design is the owner's and is decided. Do not redesign it. Do not change the fighter spots.**

## The owner's design, in his words

> "Why are we not starting the scene with player control trunks. Its no different from what we did with the
> cell games, the play control character can talk. Just kick the NPC out from the start, never load it in,
> just load the player control trunks, have it follow the same path as the NPC, no hand off needed."

So: NPC set 133 never spawns. The player IS Super Saiyan Trunks, from the scene's first frame, through the
conversation and into the fight. There is no actor swap and no camera hand-off.

## Read these first, they are the specification

- `docs\tasks\2026-11-06-vanilla-battle-starts\report.md`, the vanilla shape and the census.
- `docs\tasks\2026-11-06-battle-start-tooling\report.md`, the checker and what it already catches.
- `scripts\permanent\patches\cellgames_ssj.py`, the working precedent for a player-controlled transformed
  character.

Facts you may rely on, all CONFIRMED and re-verified by me from the bytes or the handler:

- **Trunks' Super Saiyan party appearance is entry 16, set 133.** Appearance table `0x081D967C`, 20 bytes an
  entry. Entry 16 is flags `0x01`, set 133, revert target entry 15 (set 132). Entries 12-17 are byte identical
  in our build, so Trunks needs NO reverse-lookup patch, unlike Gohan.
- **`ext 73` before `ext 70` survives.** `appearance_revert @0x08003ED4` skips the record whose index equals
  the leader byte, and `set_leader` has already written the new leader. It also skips any entry whose flags
  bit 0 is clear, so only transformed entries are ever reverted.
- **Set 0 reaches the player in every actor op except `spawn`.** `Sprite_Select @0x08009370` special-cases
  set 0. `ext 51 spawn`'s handler `@0x08009CC4` calls `npc_factory @0x0800D6DE`, which never looks an actor
  up, so `spawn` cannot address the player.
- **A map load is itself a camera hand-back, and it never eases.** `map_load @0x0800C584` writes the new
  player into `0x030020C0 + 4` and stores that object in `0x03000FF4`. **So the jump the owner saw is not a
  missing `ext 33`. It is an uncovered map load.** The fix is a cover, not a camera op.

## What to change

### 1. The conversation: move it onto the player

The ending table is `rom:0x3B8140`. Eight ops name set 133, listed with addresses in the battle-start report's
section 2. Repoint the six that take set 0 (`face` x2, `attack` x4, `walk`) to set 0, and DELETE the two that
cannot: `spawn(133, 496, 504)` at `rom:0x3B7C41`, and the `remove(133)` in the tail, which would otherwise
find the player and delete him.

**`walk(133, 248, 568)` at `rom:0x3B7E6C` is the NPC's path to the fight spot.** The owner asked that the
player "follow the same path as the NPC", so keep that walk on set 0 rather than teleporting him.

Set 132 is NOT part of this. It is the plain NPC Trunks other scenes still use. Leave every 132 op alone,
including the two `camera_follow` ops that name it.

### 2. Record F: use the helper, and cover the load

Record F today is
`leader(3) ; load_map_at(6,100,1,248,568) ; face(0,1) ; header_bit1(1) ; bar_show(28)`.

Rebuild it with `scene_lib.battle_start(...)`, which emits the vanilla template's order. It must:

- cover the map load with a fade, which is the whole defect;
- set the form with `appearance=(3, 133)` so it emits `ext 73 (3, 133)` before `leader(3)`;
- keep the player at **(248,568)** and Cell at **(244,504)**. These are settled. Do not move them.

Pick the fade and hold lengths from the vanilla template (`fade_out(120)`, `fade_in(120)`, `wait(60)`), and
say in the report if you deviate and why.

### 3. Two test-rule corrections, my decision, with the evidence

Both are false-positive fixes grounded in the handler, not design changes.

- `test_form_survives_the_leader_change`: read the appearance table and flag ONLY an entry whose flags bit 0
  is set. `appearance_revert` provably skips the rest. This clears 4 of its 5 findings.
- `test_control_record_shows_the_hud`: scope to a record that shows a bar AND either loads a map or sits in a
  table that ran `header_bit1(0)`. The 12 vanilla hits all raise a bar in a scene that never hid the HUD.

### 4. What you must NOT do

- Do not touch `fullpower_ssj`. Its `rom:0x89A9C0` finding is a real candidate defect and the owner has not
  yet ruled on the one-line reorder. **`test_form_survives_the_leader_change` is therefore EXPECTED TO STAY
  RED with exactly one finding after your narrowing.** That is correct. Do not declare an exception for it and
  do not make it pass.
- Do not touch `chamber_spar`.
- Do not add `BATTLE_START_EXCEPTIONS` to any module.

## Expected end state

- `test_map_load_is_covered`: GREEN. Record F now covers its load.
- `test_control_record_shows_the_hud`: GREEN, after the scoping.
- `test_form_survives_the_leader_change`: RED, one finding, `rom:0x89A9C0` in `fullpower_ssj`.
- Every other test green. Report the exact `Ran N tests` and `FAILED (failures=N)` lines.

## Build and rules

- Build the trial to `builds\mockups\2026-11-06-arena-v5\`, from a trial list that includes the core list plus
  this module, the way `build_list_trial_ending.txt` already does. Print and report the SHA-1. Pair a `.sav`.
- Run the suite once at the end. **Redirect it to a file and read the file**: a pipe or a compound command
  reports the LAST command's exit code, and on 2026-11-06 that showed "exit code 0" on a run with 3 failures.
- Every source byte, word and record is checked before the first write; a second run raises. That is the
  existing contract in `ending_fight.py` and it stays.
- Python header block on every file, no em or en dashes, no byte order mark.
- Label every reverse-engineering claim CONFIRMED, LIKELY or SPECULATIVE.
- Write `docs\tasks\2026-11-06-arena-v5\report.md` and, if you learn a ROM fact, `rows.md` with tag `AR5`.

One report message, then stop. Do not add a byte order mark.
