# Brief: make the FUTURE 18 and FUTURE 17 fights playable

Agent: study and build in one. Read `docs\tasks\global.md` first. Absolute paths only. Never `cd`.
Deliverable: a TRIAL ROM the owner can play, with its `.sav` beside it.

## What he asked for, in his words

"I wanted you to make the future 18 and future 17 fights playable, those are the cutscenes before the
future cell fight we just worked on. We do not touch any earlier 18 and 17 fights."

Plus, from his earlier message: "replace the npc with a player and have 18 and 17 fightable. 17 will face
the player like Cell did in the cell jr fight. To make it simple, end of the fight can just fade to the
cutscene then starts the 17 fight. We will fix all that up much better later."

**Do NOT touch the main-game Android 17 or 18 fights on maps 11,4-11,6 or the flag 127 scenes.** He ruled
those out explicitly. This is the ENDING sequence only.

## Where the fights are. I decoded this myself this morning, so do not re-derive it.

Ending scene table **`rom:0x3B8140`**, 27 words. This is the table the arena work already edits.

| word | record | what it is |
|---|---|---|
| 0 | `rom:0x3B7B08` | `load_map(6,23,...)` then `load_map(1,2, var 1, 384, 552)`, `camera_follow(132)`, `camera(384,368,2)` |
| 4 | `rom:0x3B7C1C` | `spawn(set=133, 496, 504)`, Trunks |
| **8** | **`rom:0x3B7C96`** | **the FUTURE ANDROID 18 beating**: two blocks of `attack(attacker=133, target=11, n=100)`, then `ext94(11,12,12)`, `hit(set=11, sound=20)`, `face_target(set=11)`, **`remove(set=11)`** at `rom:0x3B7D1B` |
| 9, 10 | | dialogue, portraits 28 and 101 |
| **11** | **`rom:0x3B7D6E`** | **the FUTURE ANDROID 17 beating**, the same shape, `remove(set=9)` at `rom:0x3B7DF9` |
| 12 | | dialogue |
| 13 | `rom:0x3B7E4A` | `load_map(6,1, var 1, 136, 432)`. **`ending_fight.py` already replaces this with the arena load.** |
| 23 | `rom:0x3B8016` | the Cell beating, already converted into the real arena fight |

**So words 8 and 11 are the same scripted-beating shape as word 23.** Word 23 is the one
`ending_fight.py` and `battle_arena.py` already converted into a real fight. Copy that method.

## The map, read with `scene_probe --map 1,2` this morning

```
  +0x08 combat 1 (already on)        +0x0C banner index 229
  region list rom:0x3ED7F0, 1 region;  item list rom:0x3ED7CC, 4 items
  DOOR CARRIER A: region 0 rom:0x3ED7DC  cond 0x00000000  scene  rect (-15,-7,360,584) -> rom:0x3B7ADC
  DOOR CARRIER B: 1 door rom:0x6ACB4C  rect (144,280,273,305) -> map 2,22 var 1 at (128,116) facing 1
  ITEMS: 0 npc set 54 (216,368) | 1 npc set 11 (472,408) | 2 npc set 9 (520,408) | 3 npc set 132 (496,648)
  COLLISION rom:0x6AC7BC type 1, 5683 of 20480 open inside bounds 1024x1280
  PROPS 1;  BG1/BG3 blocks 4x5 = 1024x1280, BG2 4x4
```

**Three hazards he does not know about, and one is serious:**

1. **The region is the prologue and it is ALWAYS ON.** `rom:0x3ED7DC` has condition `0x00000000` and a
   step trigger over rect (-15,-7)-(360,584), firing scene table `rom:0x3B7ADC`, which is the prologue
   beating of `set:54` by sets 11 and 9. The bible (tag CH-prologue row on map 1,2) records that this
   scene **undoes the party**: it carries the `ext 91 (3)` that REMOVES Trunks. The fighters start at
   x 472-520, outside the rect, but a real fight lets Trunks move, and crossing x 360 would fire the
   prologue and delete the player mid-fight.
2. **There is a real door** to map 2,22 at rect (144,280)-(273,305).
3. **There is a banner**, index 229. The arena's fix was entry `+0x0C` = `0xDD`, confirmed in the handler
   `sub_0800EBB6` (`CMP r0,#0xDD ; BEQ` skips the banner call).

## The decision I already made, do not revisit it

**Clone map 1,2 into a NEW map entry. Do NOT edit map 1,2 in place.** The PROLOGUE plays on map 1,2, so
stripping its region, its door and its banner in place would break the opening of the game. This is
exactly what `battle_arena.py` already does for map 6,1 to 6,100: a new entry appended to the map table,
with the table relocated. Reuse that module's method, and reuse `scene_probe.map_table()` so the appended
entry is found.

The clone must have: combat on, **0 regions**, **0 doors in BOTH carriers**, banner `0xDD`, and the
collision frame of 1,2.

## What to build

- Items 1 and 2 are **NPCs** (factory `@0x0800D6DF`). They must become **enemy items**, the way the arena
  turned Cell into one: factory `0x0800E77F`, an enemy type, a condition, a set and an event table.
  The enemy type census is already generated at `docs\research\enemy-type-census.txt`, 365 lines, every
  type at `rom:0x6D56AC` + 24 x type with HP, AI and the death descriptor. Pick from it and say why.
  The main-game pairings are Android 18 type 4 `set:11` and Android 17 type 3 `set:9`, HP 3550 AI 21 for
  17. Reuse rather than invent unless you can show a reason.
- Keep Future Gohan (`set:54`) and the scene's framing. He asked to change who fights, not the staging.
- **Two fights in sequence**, 18 at word 8 then 17 at word 11, with the dialogue words 9 and 10 kept
  between them. His words: "end of the fight can just fade to the cutscene then starts the 17 fight."
- "17 faces the player" is the FACE_PLAYER step `patches\celljr_fight.py` already owns. Reuse it, and
  carry its known limit: the step decides again once the player takes control, so 17 may turn.
- `scene_lib.battle_start()` already emits the four-op vanilla default. Use it, do not hand-write bytes.
- Trunks must be the one fighting. The arena uses `ext 70 (3)`. The party window is OPEN in the ending,
  which the arena work already proved, but **the prologue region is what could close it**, so confirm the
  clone really carries no path back to `rom:0x3B7ADC`.

## Rules

- Trial module on its OWN build list, `build_list_trial_future.txt`. **Do NOT touch `build_list.txt` or
  `build_list_core.txt`.** Both masters must still rebuild to `acf1b15f` and `ffbd2bfc`.
- **Run `scene_probe.py --map` on your cloned map in the BUILT ROM** and put the listing in your report.
  It must show 0 doors in both carriers and 0 regions. The arena shipped three times with inherited doors
  because this tool did not exist. It exists now.
- A trial ROM is not real until you read the changed bytes back OUT of the built ROM.
- The build script pairs a `.sav` beside the ROM. Confirm it did: a trial ROM with no save costs him his
  file.
- `py -3.14 -P`. Never put a Windows path inside a Python string literal in a heredoc.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create exclusively.
- Never pipe a test run into `tail` or `head`. Run your own modules and the ones you touch, not the full
  suite; I run that myself.
- **Do NOT read `docs\RE-BIBLE.md` until you have checked that no other agent is rewriting it.** A stable
  id pass may still be running. Work from this brief and the ROM. I merge your rows myself.
- Give your rows as `rows.md` beside this brief, `## Section N` blocks, tag `FUT`. Cite other bible facts
  by TAG and address, never by a line number.

## Report

The before and after `--map` listings, what you changed, what you read back out of the ROM, the trial
ROM's SHA-1, your test counts with real exit codes, and anything you could not prove. Say plainly whether
the prologue region can still be reached from the cloned map.

One report message, then stop. Do not add a byte order mark.
