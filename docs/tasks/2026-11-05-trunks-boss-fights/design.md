# Design: the ending becomes playable (first pass)

The owner's design, given 2026-11-05. He called it "a great first pass" and said he wants to change
things later. Build this, then iterate.

Study and evidence: `report.md` beside this file. Scene table facts verified by me with
`scripts\permanent\scene\scene_probe.py` against the base ROM.

---

## What the ending is today

The ending runs AFTER the credits. It is scene table `rom:0x3B8140`, 27 words, reached from two type 5
records, `rom:0x3DD03C` and `rom:0x3C4E90`. Both jump to word 0. CONFIRMED.

Super Saiyan Trunks (`set:133`) kills Android 18, Android 17 and Imperfect Cell in scripted blocks. No
fight, no health bar, no EXP anywhere in the table.

| Ending word | At | What it does today |
|---|---|---|
| 8 | `rom:0x3B7C96` | Scripted kill of `set:11`, Android 18 |
| 11 | `rom:0x3B7D6E` | Scripted kill of `set:9`, Android 17 |
| 22 | `rom:0x3B7FE0` | Trunks: "I don't think so.THE NIGHTMARE IS OVER CELL!!!!!" |
| 23 | `rom:0x3B8016` | Scripted kill of `set:28`, Imperfect Cell |

---

## The new flow

### 1. Replace the credits trigger

Gohan reaching Chichi triggers the ending. Instead of the credits, cut to Trunks at Capsule Corp.

### 2. Capsule Corp, locked to Trunks

Control is Trunks and nobody else. No character switching.

Press the action button beside the time machine. It plays a sound and runs the departure script.
To stay, walk away and do not press it.

> [!NOTE]
> DECIDED 2026-11-05, owner: no A to stay, B to return menu in the first pass. "Keep it simple for
> this first pass, just press, we will smooth this all out in every revision."
> This needs no new engine code. An interactive object that you press the action button on, which
> plays a sound and runs a scene, is vanilla: 245 of them across 84 maps. CONFIRMED.
> No level requirement either. Nothing found in the engine reads the player's level into a condition.

### 3. The scripted departure

Trunks runs the existing scripted walk to the back, then the fade to the future.

### 4. The future, free movement

Trunks is in an area that is already drawn from the start of the game. The player moves him freely.
Walking to a designated point starts the dialogue.

### 5. Android 18 fight

The existing dialogue plays, including the Gohan line. Then Trunks fights Android 18.

- Android 17 watches, the way Cell watches in the Cell Jr fight.
- Vanilla Android 18 stats.
- Trunks is strong by this point and should win easily.
- On death she COLLAPSES, then the scripted ki blast finishes her, as the cutscene does today.

### 6. Android 17 fight

Trunks and 17 face each other when 18 dies. Trunks' line "And this is for all the people you've killed"
starts the fight.

- Vanilla Android 17 stats.
- Same death: collapse, then the scripted ki blast.

### 7. The Cell portion

In the fade between, a new on-screen card reads **3 years later**.

Then the scripted Cell dialogue plays, with Trunks in the Saiyan armor. When Trunks says
"THE NIGHTMARE IS OVER CELL!!!!!" (ending word 22), the fight begins.

- Vanilla Imperfect Cell stats, `set:28`.
- The fight is at Capsule Corp. It may not be fully drawn. It should look like vanilla, with the rain
  and the filtered view.

---

## Art

The Trunks tank top sprite is for the Android 18 and Android 17 fights. The Cell portion uses the
Saiyan armor.

The Saiyan armor already exists in the game. Trunks has a short hair jacket sprite and a long hair
armor sprite. In the show he wears the armor with SHORT hair, so the armor sprite needs a hair change
only. Vegeta wears the same armor and his hair goes up, so any part of the head that the long hair
hides can be read off the Vegeta sprite and corrected. The owner calls this a very minor change:
literally the hair. DEFERRED, 2026-11-05: "we do that much later." Do not start it with the first pass.

---

## Confirmed mechanisms

| Need | Mechanism | State |
|---|---|---|
| Lock control to Trunks | `leader` ext op 70, with `party_leave` 91 and `party_add` 29 | CONFIRMED, named ops |
| Branch in a scene | Type 0 record: ops run, one value left on the stack becomes the next word index | CONFIRMED, observed |
| The "3 years later" card | `chapter_cards` module, already in `build_list_core.txt` at r41, and `card` ext op 145 | CONFIRMED, we own it |
| Where the Cell fight starts | Ending word 22, `rom:0x3B7FE0` | CONFIRMED, read from the ROM |

---

## Decided

1. **The A/B prompt is cut from the first pass.** Press the time machine, it pings, the script runs.
   Owner, 2026-11-05.
2. **A loss sends the player to the vanilla save point at Capsule Corp**, before going to the future.
   It already exists in vanilla. Owner, 2026-11-05: "this is all new code", so the first pass leans on
   the save point rather than on new loss handling.
3. **No level gate on the time machine** in the first pass. The owner raised a level 40 idea and then
   set it aside. Nothing found in the engine reads the player's level into a condition, so a level gate
   would be new work. Revisit in a later revision.

## Open questions

1. **The rain and the filtered view** at Capsule Corp. Not yet traced. `palette_fx` is ext op 42.

## Deferred ideas

- A level requirement on the time machine, for example level 40.
- An A to stay, B to return choice menu.
- The owner expects to change much of this flow in later revisions. This file is the FIRST PASS.

---

## Traps already paid for

- `--find-text` is CASE SENSITIVE. "nightmare" returns 0 hits; the line is in capitals.
- Never find a scene table start by walking backward. A stray word before word 0 reads as an END and
  shifts every index by one. Reach a table through the item, event or type 5 record that names it.
- The barrier objects do NOT force a character switch. Each gate scene is a sound plus a refusal line.
  The region condition decides who passes. There is NO Trunks gate on any ending map.
