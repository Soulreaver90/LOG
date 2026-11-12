# SUPERSEDED, NEVER BUILT. This brief read the owner's ask wrong.

**Do not build from this file.** The live brief is `docs\tasks\2026-11-07-future-androids\brief.md`.

I read "the 17 and 18 fight" as the MAIN GAME fight, Piccolo against Android 17 on maps 11,4-11,6. He
meant the **FUTURE** 18 and 17, the cutscene beatings in the ENDING table `rom:0x3B8140` at words 8 and
11, just before the future Cell fight the arena already replaced. His correction: "those are the
cutscenes before the future cell fight we just worked on. We do not touch any earlier 18 and 17 fights."

I stopped the agent built from this brief before it wrote anything. It had reached "I'll start by
reading the three required files".

**What is still true and worth keeping** is the measured map data for 11,4-11,6 and the party-window
finding, both recorded in the ledger. The party problem below applies ONLY to the main-game fight and
does NOT apply to the ending, where the arena already proved `ext 70 (3)` works.

---

# Original brief, kept for the record: Trunks fights Android 17 (main game)

Agent: study and build in one. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.
The owner asked for this at 9:50 AM on 2026-11-07. Deliverable: a TRIAL ROM he can play.

## What he asked for, in his words

"The next part will be the 17 and 18 fight. Are we able to do the exact thing? This map should already
not have any items, labels, or warps. So it should be simple as reusing the map, replace the npc with a
player and have 18 and 17 fightable. 17 will face the player like Cell did in the cell jr fight. To make
it simple, end of the fight can just fade to the cutscene then starts the 17 fight. We will fix all that
up much better later."

**This brief covers 17 only.** 18 is blocked on a party question, stated at the end as a study question.

## Facts you do NOT need to re-derive. I took these from the bible this morning.

**A bible rewrite is running right now** (another agent is adding a stable id column to every row). Do
NOT read `docs\RE-BIBLE.md` until that agent is finished, because a read during the rewrite can give you
a half-written file. Work from this brief and from the ROM. I will merge your rows myself.

**The fight already exists. You are changing who fights it, not building a fight.**

- Android 17 is a REAL four-round player fight. Enemy items: `rom:0x406494` (map 11,4, death table
  `rom:0x3E49F0`), `rom:0x40657C` (11,5, no death event), `rom:0x406654` (11,6, death `rom:0x3E4B50`),
  `rom:0x4066E4` (11,6, death `rom:0x3E6078`). All type 3, `set:9`, HP 3550, AI 21, boss descriptor.
- The fight START record is `rom:0x3E47DC`, scene table `rom:0x3E47F8` word 6, map 11,4. It is the whole
  thing, four ops: `ext104(9,1) ; bar_set(9,75,100) ; header_bit1(1) ; camera_follow(0)`. **This is the
  exact record `scene_lib.battle_start()` already emits**, because it is the shape 34 of the 35 vanilla
  bar records use. Record 0 of that table parks a fixed camera with `camera(152,96,3)` for the talk.
- Round 2 is armed by the map 11,5 REGION SCRIPT, not a scene table: item `rom:0x406624`, data script
  `rom:0x4065E8`, which runs sound 26, `ext 54 (0,696,448)`, a map load, `ext 54 (0,160,304)`,
  `ext 55 (0,3)`, `ext 104 (9,0)`, `ext 86 (1)`, `ext 90 (9,50,75)`, end. **It touches no leader.**
- The rematch is `rom:0x3E4B3A` (map 11,6), table `rom:0x3E4B50`: `push 9,4 ; ext 104 ; push 1 ; ext 86 ;
  push 9,25,50 ; ext 90`. EXP is `ext 139 (15000)` at `rom:0x3E4B7F`.
- `set:9` has anims 0-3, 5-8 and 12, with NO anim 4. Check that against whatever you make 17 do.

**The maps, measured from the generated map index, not guessed:**

| map | entry | regions | items | props | warps | banner | combat |
|---|---|---|---|---|---|---|---|
| 11,4 | 296 | 1 | 4 | 4 | 0 | 217 | already on |
| 11,5 | 297 | 1 | 3 | 1 | 0 | 217 | already on |
| 11,6 | 298 | 0 | 6 | 5 | 0 | 217 | already on |

So the owner is right that there are no warps, and wrong that there are no items or labels. Combat is
already on, so no combat flag change is needed.

**The party.** Trunks is out of the party from `ext 91 (3)` at `rom:0x3B7AB8` until `ext 79 (3)` at
`rom:0x3DF2A6`, which is the record that SETS flag 129. The Android 17 fight is after flag 129, so he
should already be in the party and `ext 70 (3)` should promote him. **Verify that before you build on
it**, the same way the arena work verified the window, and say how you verified it.

## Use the reader that landed an hour ago

`scene\scene_probe.py --map <zone>,<area>` is now the section 9 reader. It prints entry fields by name,
the layout chain, BOTH door carriers side by side, the item list, props, the collision frame with its
open counts and bounds, and the BG layers. **Run it on 11,4, 11,5 and 11,6 before you change anything,
and again on your built ROM.** The arena shipped three times with inherited doors because this tool did
not exist. Put both listings in your report.

## Build it the way the arena was built

- Copy the method from `scripts\permanent\patches\ending_fight.py` and `patches\battle_arena.py`.
- `scene_lib.battle_start()` already emits the four-op default. Use it rather than hand bytes.
- "17 faces the player" is the FACE_PLAYER step `patches\celljr_fight.py` already owns. Reuse it, and
  carry its known limit forward: the step decides again once the player takes control, so 17 may turn.
- Trial module on its OWN build list, `build_list_trial_17.txt`. **Do NOT touch `build_list.txt` or
  `build_list_core.txt`.** Both masters must still rebuild to `acf1b15f` and `ffbd2bfc`.
- The build script pairs a `.sav` beside the ROM. Confirm it did, because a trial ROM with no save costs
  the owner his file.

## The one study question, no build

Android 18 is the same idea but her fight ends by setting flag **127**, and Trunks does not rejoin until
flag **129**. So at the 18 fight he is not in the party and `ext 70 (3)` has nothing to promote. Her
approach record `rom:0x3D8B38` already arms a real fight (`ext 84 (0)`, `ext 86 (1)`,
`ext 90 (11,50,100)`), and her death table is `rom:0x3D98AC`.

**Question:** can Trunks be brought back early with the two ops vanilla itself uses at the real rejoin,
`ext 79 (3)` then `ext 80 (3)`, before the 18 fight? Answer with evidence from the handlers and the
scripts. Do NOT build it. Say what would break, especially anything between the prologue leave and flag
129 that assumes he is absent.

## Rules

- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create exclusively.
- Never pipe a test run into `tail` or `head`: the pipe reports the pipe's exit code.
- Run your own test modules and the module tests you touch. Do NOT run the full suite; I run it myself.
- Treat a trial ROM as not real until you read the changed bytes back OUT of the built ROM.
- Give your bible rows as `rows.md` beside this brief, as `## Section N` table blocks, tag `T17`. **Cite
  other bible facts by their TAG and their address, never by a line number**, because line numbers move.
- Report: the before and after reader listings, what you changed, what you read back out of the ROM, the
  SHA-1 of the trial ROM, your test counts with real exit codes, the 18 answer, and anything you could
  not prove.

One report message, then stop. Do not add a byte order mark.
