# Card 4 arrival scene study: report (2026-10-30)

Brief: `card-4-scene-study.md` in this folder, with my Vegeta update (6:49 PM and 6:59 PM) and the 7 PM speed request (lean report). Study only: no module, list or ROM changed. Labels: CONFIRMED (C) = ROM bytes or listing, LIKELY (L) = strong evidence, no emulator run, SPECULATIVE (S) = a guess. Base ROM addresses unless the text says r40.

---

## SHIPPED

| Ask | Result |
|---|---|
| 1. Roster | Leader at the landing: Gohan, Piccolo or Vegeta. Trunks cannot lead. Section "Roster" |
| 2. Actors | All six NPC sets fly in all 4 directions, base and r40. No gaps. Portraits: Piccolo 3, Tien 95, Vegeta 4, Trunks 98. Section "Actors" |
| 3. Trigger | The world map landing item becomes a scene item. Its table tests bit 211, then plays the card, the landing and the scene. Section "Trigger" |
| 4. Script | Byte-level draft, 17 table words, 1673 record bytes, decoded back. Section "Script draft" |
| 5. Text | Type 1 records, 0x0B box breaks, every box at most 4 lines. Section "Text boxes" |
| 6. Continue | Option c (86 and bit 211) advised, option a as the fallback. Test save plan. Section "Continue and test" |
| Bible rows | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_card4_scene.md`, tag C4S |

## PENDING

| Ask | Why | My step |
|---|---|---|
| The scene in play | No emulator run. The start on the world map is new (S) | Test plan below, after a build |
| Positions and camera | The 8,1 map size and camera clamp are not read (speed request) | Check by eye in the first build |
| Full suite | Not run (speed request; nothing changed) | None |

---

## Roster

| Fact | Label |
|---|---|
| Party bit 1 goes on for Gohan (0) and Piccolo (1) at `rom:0x3D482A` and `rom:0x3D4826`, in the post-Android 19 record with SET 85. Vegeta (2) has it since the "Meanwhile" record `rom:0x3CCA53` | C (`presave_party.txt`) |
| Nothing turns it off before flag 113 (`rom:0x3D7F38`) or flag 127 (`rom:0x3D9885`) | C (same listing) |
| Trunks (3) left at `rom:0x3B7ABA` (map 1,2) and joins again only at `rom:0x3DF2A8` (flag 129). The two "?op" join hits `rom:0x3D0AF0` and `rom:0x3D29AB` are bytes inside type 4 and type 2 text records | C (decode from record starts), L (a computed join would not show) |
| The vanilla post-Android 20 scene has exactly three leader branches (0, 1, 2) | C (`rom:0x3D48B6`-`0x3D4900`) |

| Leader | Branch |
|---|---|
| Gohan | Piccolo and Tien lines, Gohan farthest right |
| Piccolo | Piccolo and Tien lines, Piccolo farthest right |
| Vegeta | The Vegeta and Trunks exchange, Vegeta farthest right |
| Any other value (not reachable) | The Gohan branch (the draft's default) |

---

## Actors

The template is the vanilla post-Android 20 table `rom:0x3D5524`. It spawns this same cast as NPCs, flies them in with ext 54, and flies them off with `ext 112 (id, 26)`, ext 54 and ext 52 (C).

| Character | NPC id | Fly row (anim 12), 4 dirs, base and r40 | Portrait |
|---|---|---|---|
| Piccolo | 103 | Yes | 3 (party: resolves to his current look) |
| Krillin | 76 | Yes | not needed |
| Tien | 121 | Yes | 95 (8 lines near the landing, e.g. `rom:0x3CB254`) |
| Gohan | 53 | Yes | not needed |
| Vegeta | 3 = party id: his current appearance, `set:137` or `set:140` (`get_set` `@0x0800934C`) | Yes, both sets | 4 (party) |
| Trunks | 128 | Yes | 98 (absolute, as `rom:0x3D4C34`) |

- **No gaps (C, `c4s_probe.txt` section 4).** Every fly row is set in all 4 directions in base and r40.
- **Cast count.** I count six, the player included: five NPCs and the player. The brief's "seven" would add one more. The leader's NPC is never spawned.
- **OBJ VRAM (L).** Each NPC set is 0x400 (16 units): 80 units for five. The text box with a portrait is 224 units of the 492 pool (CJR row). Map 8,1 builds no spawn at load (C, entry +4 = 0). The vanilla post-20 scene shows the same five sets plus Bulma and Android 20 with a text box, so this cast is a subset of a vanilla scene.

---

## Trigger

### Choice: the landing item becomes a scene item (first choice)

| Step | Proof | Label |
|---|---|---|
| Copy item `rom:0x3FBC5C` (20 bytes) to the expansion area with factory `0x0800D7E1` in place of `0x0800C2C3`. Its data word names the new table. Region word `rom:0x3FBE54` (its only namer) names the copy. The old item and script stay | The 8,50 scene item `rom:0x4035B4` has the same shape and the same A-press trigger `0x0800D839` | C (bytes) |
| Record 0 tests the guard before the load: `push 8,1 ; ext 23`. Set = an old landing: the vanilla `ext 38` bytes, then END. Clear = HUD off, fade 60, card 4, `ext 38`, then record 1 | Bit 211 is set inside `map_load_core` (`@0x0800C430`), so a test before ext 38 sees "not visited" only on the first landing (CH8 rows) | C (code), L (play) |
| Order: card before the map load, scene after the fade in | The card runs inside record 0 before `ext 38`. ext 38 fades out, loads 8,1 and fades in. Record 1 starts after it | C (bytes), L (fade-in blocks) |
| A scene runs on the world map | Record `rom:0x3D9864` loads 6,99 with ext 39 and then runs ext 70, ext 81 and ext 41 there | C |
| A scene loads a map with ext 38 and goes on | Flag 113 records and `rom:0x3B9032` (CH8) | C |
| The card op in a scene record | Cards 2, 3, 5-8 run ext 145 in scene records | C (module) |
| **Not vanilla:** a scene item started on 6,99. None of the 27 world map regions holds one | Region list `rom:0x3FBDF8` | C (none), S (works) |

On every later landing the table runs only the vanilla landing bytes and ends (L: a scene run in place of a bare script, same ops).

### Second choice: a new region on 8,1

The landing script sets a VM var on the first landing. A new walk-in region on 8,1, with a condition script that reads that var, starts the scene. It has more unproven parts: the var must survive the map load, the 8,1 region list and count byte need a copy, and no vanilla condition reads a var. Use it only if the first choice fails in play.

---

## Script draft

Built with the `piccolo_gi_scene` encoders and decoded back (`c4s_draft.py`, `c4s_draft.txt`). Op codes: eq 11 and ne 12 as the post-20 record uses them (`rom:0x3D5482`, `rom:0x3D48BA`), jz 19.

| Index | Next | Content |
|---|---|---|
| 0 | 1 | `push 8,1 ; ext 23 ; jz +14 ;` **old landing:** `push 8,1,1,272,128 ; ext 38 ; push 16 ; end ;` **first:** `push 0 ; ext 86 ; push 60 ; ext 40 ; push 4 ; ext 145 ; push 8,1,1,272,128 ; ext 38 ; end` |
| 1 | 2 | Leader pick: 2 (Vegeta) leaves 4, 1 (Piccolo) leaves 3, else 2 |
| 2, 3, 4 | 5, 5, 8 | Arrival per leader: `ext 86 (0)`, player faces down, `ext 31 (92,44,4)`, `ext 46 (26)`, one group of five `ext 51 (id, x, 300) ; ext 54 (id, x, 128)`, then each faces down. Record 4 adds: player faces left, Trunks faces right |
| 5 | 6 | Type 1, portrait 3: Piccolo line |
| 6 | 7 | Type 1, portrait 95: Tien lines |
| 7 | 13 | Exit pick: Piccolo leads leaves 14, else 13 |
| 8-12 | 9, 10, 11, 12, 15 | Type 1: Vegeta 4, Trunks 98, Vegeta 4, Trunks 98, Vegeta 4 |
| 13, 14, 15 | 16 | Exit per leader: one group of five `ext 112 (id, 26) ; ext 54 (id, x, -40)`, then five `ext 52 (id)`, `ext 33 (0)` (camera on the player), `ext 86 (1)` |
| 16 | | END word 0 |

Rows, left to right, 24 px apart at y 128, the player at x 272 (S, check by eye):

| Leader | x 152 | 176 | 200 | 224 | 248 |
|---|---|---|---|---|---|
| Gohan | Krillin | Tien | Trunks | Vegeta | Piccolo |
| Piccolo | Krillin | Trunks | Vegeta | Gohan | Tien |
| Vegeta | Krillin | Tien | Gohan | Piccolo | Trunks |

- Fly in: 172 px at 2 px a frame, about 86 frames. Fly off to y -40: about 84 frames. Vanilla flies to a negative y (8,48 pad, `push 0,536,-32`).
- The camera: a follow camera on the player at x 272 shows x 152-392, so Krillin at 152 would be cut. `ext 31 (92,44,4)` centres the row (S: the map clamp is not read).
- Size: 1673 record bytes, 68 table bytes, 20 item bytes.

---

## Text boxes

- **Record type:** type 1 `{next, 0, 1, portrait}`, ASCII, 00 end (the rage_text shape). Type 1 records already hold 0x0B (`rom:0x3D2F0C`).
- **Box limit (C, listing):** lines wrap at 144 px (`@0x0800B92A`, `mov r1,#0x90`; the counter keeps a line while width <= limit, `@0x0801F862` `cmp r4,r2 ; ble`), 4 lines a box (`@0x0800B976`, `@0x0800B9A0`). 0x0B starts a new box. Each split below is at most 4 lines (`c4s_probe.txt` 5d).
- **Prefix bytes:** `!`, `@` or `#` at the text start moves the box, `^` shows it at once. No box below starts with one.
- **Words:** my words only, with "let's" fixed. Vanilla starts a speaker's turn with "NAME: " (my question 1). With names, the same splits still fit in 4 lines (`c4s_probe.txt` 5c). Boxes without a name are vanilla too (`rom:0x3D4CBC`).

Lines per box in brackets.

| Line | Portrait | Box 1 | Box 2 | Box 3 |
|---|---|---|---|---|
| Piccolo | 3 | Now we better get moving, we don't have much time! (2) | | |
| Tien | 95 | Okay, let's do it. (1) | I'll head a little further north to see what I find out there. (2) | |
| Vegeta 1 | 4 | Would you stop following me, boy? (2) | You're getting on my nerves! (2) | |
| Trunks 1 | 98 | Sorry, but there's no way I am planning to let you fight the androids on your own! (3) | | |
| Vegeta 2 | 4 | And just what are you planning to do to stop me? (2) | It's going to take more than that little sword of yours to stand in my way! (3) | |
| Trunks 2 | 98 | How many times do I have to tell you before it sinks into your thick skull? (3) | Never underestimate the power of the androids! (2) | |
| Vegeta 3 | 4 | Hah! (1) | And never underestimate the power of a real super saiyan who loves to take on a challenge! (4) | Well, if you're going to stay, you can at least help me find Dr. Gero's lab! (3) |

> [!NOTE]
> Three lines are exactly 144 px wide ("to see what I find out there.", "saiyan who loves to take on", "Well, if you're going to stay,"). They fit, because the counter wraps only past 144 px (C, `@0x0801F864` `ble`). One added character would wrap them, and Vegeta 3 box 2 would become 5 lines.

---

## Continue and test

**Continue.** Option c: Chapter 4 when flag 86 is set and the slot's bit 211 (slot image +0x101, mask 0x08) is set. It is exact, and it needs a Thumb change in the Continue wrapper and its tests. Option a (flag 86 only) is the fallback: a save between the Android 20 fight and the landing shows card 4 on Continue and again at the landing.

**Test save plan (one-time `c4s_` script, exclusive create, not built).** Base: `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v6_pre_a.sav` slot 3 (7,18, before flag 86). Three slots, one per leader 0, 1, 2:

1. Set flags 86 and 87 (`log2_save set ... flag+=86 flag+=87`).
2. Set map 6,99,1 and a position inside the star rect (2560,1000)-(2673,1121), for example (2616,1060).
3. Clear bit 211 alone with `log2_save.set_bit(slot, O_VISITED, 211, False)`. `set visited=none` would also blank the area map.
4. Reseal each slot.

A Continue onto the world map is not a vanilla save state, so this slot is LIKELY to load, not proven. The slot must not be on 8,1: that map load sets bit 211 (`map_load_core` `@0x0800C430`). If a 6,99 slot fails, put it on 7,18 and fly out through the Southern Continent exit (flag 87 script `rom:0x3FD7D0`).

**Test plan (emulator).**

1. A on the star with each leader: fade, card 4, landing, the team flies in, the right lines, the fly-off, control back, HUD on.
2. Fly back to the world map and land again: a plain landing, no card, no scene.
3. Save at 8,1, then Continue: Chapter 4 (option c or a).
4. Watch: the box style for the speaker who leads, the camera at the row, actors cut at the edges.

---

## Risk and size

| Risk | Label | Fallback |
|---|---|---|
| A scene item started on 6,99 (never vanilla) | S | The second choice (new 8,1 region) |
| The camera or the row sits off the map view | S | Change `ext 31` and x in the draft |
| Vegeta id 3 shows his current form: Super Saiyan if he was left transformed | L | Accept, or force `set:137` |

Work size: about one `chapter_cards` change (STORY[4] becomes the new table, card 4 leaves IN_FIELD, the v5 post-20 copy goes back to vanilla), one item copy and one region word, the table, tests for the bytes, and the option c Thumb change.

---

## My questions

1. Speaker names: show only your words (the draft), or start each turn with "PICCOLO: ", "TIEN: ", "VEGETA: ", "TRUNKS: " as the game does? Both fit the same box splits.
2. The row order and the facing (all face the camera, Vegeta and Trunks face each other): keep, or a different order?
3. Continue: option c (exact, a Thumb change) or option a?

## Process note

One early Bash grep started with `cd` into `docs\tasks`. The brief forbids `cd`. No file changed by it. All other calls used absolute paths.

## Files

- `scripts\one-time\2026-10-25-chapter-cards\c4s_probe.py` and `.txt`, `c4s_draft.py` and `.txt`, `bible_rows_card4_scene.md`.
