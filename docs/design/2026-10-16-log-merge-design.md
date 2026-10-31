# LOG: design

Author: Joseph Gonzalez. Status: **approved 2026-10-16.** Slice 1 is cut to a proof of concept: the gi, Super Saiyan 2 as a usable form, and its stats. Portraits are a bonus if they come easily.

This document is the source of truth for what gets built. Research facts live in `research-notes.md`, `re-sprite-decompression.md` and `re-save-format.md`. Each decision below says how firm it is: **final** (settled in conversation) or **my call** (a default I can still change).

---

## 1. Intent

I want one continuous Dragon Ball Z game on the GBA: The Legacy of Goku II (LoG II, Androids and Cell) flows into Buu's Fury (Buu saga), with one save and one progression.

- The two games share a Webfoot engine, but each has flaws the other fixed. The merged game keeps the better part of each.
- Faithfulness to the source matters to me. Gohan's outfit, the forms each character can use, and when they unlock follow the story.
- Balance matters as much as content. A change that makes fights trivial (for example, pinning an enemy against a wall) is a defect.
- This is personal and never distributed. I dumped the cartridges. The game only needs to run in an emulator (mGBA).

## 2. Goals

1. One ROM, one save: LoG II, a short transition, then Buu's Fury.
2. Character progress carries from the LoG II half into the Buu saga in a way that keeps the Buu saga balanced.
3. One combat feel across both halves: LoG II knockback and wall bounce, with the Buu's Fury block and special moves.
4. Story-faithful forms and outfits, including Super Saiyan 2 and Gohan's purple gi.
5. Work ships in slices. Each slice gives me a playable build to test.

## 3. Non-goals

- Distribution, patches for other people, or real-cartridge support.
- The International (Japanese) balance. The game uses the English HP and ki scale (mine).
- LoG1 in this project. A rebuild of LoG1 on the LoG II engine is a separate project, judged after this one (mine).
- Equipment in the LoG II half. Equipment exists only in the Buu saga (mine).

## 4. Anti-goals (a build that does these has failed, even if it runs)

- Gohan in Saiyan armor after the Hyperbolic Time Chamber.
- The wall-pin trick works on any enemy.
- A character's stats after the bridge make the early Buu saga trivial, or erase the player's LoG II progress.
- The anti-piracy check sends the player to the title screen.
- An old save of the base game no longer loads in a build that claims save compatibility.

## 5. Constraints

- **Base ROM:** LoG II (USA), SHA-1 `18e0715d...`, No-Intro verified (mine). Every address in the notes is for this ROM. The Europe ROM is a reference only, for its status screen code.
- **Second ROM:** Buu's Fury (USA), SHA-1 `f1c4b075...`, No-Intro verified.
- **Size:** each ROM is 8 MB. The GBA maximum is 32 MB.
- **Save:** both games use EEPROM, 8 KB at most. The merged save must fit.
- **Anti-piracy:** LoG II checks something (probably the save type) when Gohan first leaves East District 439 for the world map. Any change to ROM size, save type or save layout must be tested against it.
- **Graphics:** all sprites are 8bpp with one shared 256-color OBJ palette (ROM `0x1DA6C8`). Frames are compressed with Webfoot's codec. The decompressor exists and is verified. A compressor does not exist yet.
- **Files:** original ROMs and my files under `data\` are never changed. Builds go to `builds\`. Reusable tools go to `scripts\permanent\`.
- **Tools:** mGBA 0.10.5, Ghidra 12.1.4 (headless), JDK 21, Python 3 with Pillow. Install nothing else without me.

---

## 6. The full game: decisions

### 6.1 Structure (mine)

- LoG II plays as normal to the end of the Cell Games.
- The Buu's Fury opening recap is cut.
- A simple transition leads from the LoG II ending to Goku in Other World, where Buu's Fury starts. Details of the transition are designed later.

### 6.2 Level bridge (mine)

- LoG II caps at level 50. Buu's Fury starts each character at a fixed level (Goku about 50).
- One data table sets each character's level at the start of the Buu saga. The Buu's Fury start levels are the floor.
- A character below 50 in LoG II starts the Buu saga at the Buu's Fury base level. A character who maxed out gets a small bonus above the base.
- A character who joins late (for example Vegeta) gets a fixed level bump for the story time the player did not see.
- Characters new in the Buu saga (Goten, kid Trunks) start at their Buu's Fury levels.
- When each character first joins in the Buu saga, a "level gained" prompt appears. It uses the Buu's Fury level-up dialog box ("Goten has reached level 80!"), as in my screenshot (mine).
- The bridge is data, not code, so a later LoG1 chapter can rescale it.

### 6.3 Stats (mine)

- Both halves use the Buu's Fury rule: each level up gives a fixed number of points, and the player assigns them. I believe Buu's Fury gives 3 points per level. Confirm in the ROM.
- The random LoG II stat gains are removed.
- The status screen shows a transformation's bonus. The bonus part of each stat bar is gold, so the player can see it is temporary. The USA ROM lacks this display; the Europe ROM has it and is the reference.

### 6.4 Combat (mine unless marked)

- Every hit pushes the target back, LoG II style, in both halves.
- Enemies bounce off walls in both halves. The wall pin is gone.
- The Buu's Fury block button stays. Blocking reduces damage and reduces knockback, so the player still moves back a little.
- The player keeps the LoG II player knockback behavior as it is (mine). Revisit in play.
- The LoG II hold-attack special stays, and it also works in the Buu saga.
- A special move that both games share unlocks in the LoG II half and carries over.
- **My call:** a move that only Buu's Fury has unlocks in the Buu saga, unless it fits the LoG II story.

### 6.5 Forms (mine unless marked)

| Form | Who | Unlock | Effect |
|---|---|---|---|
| Super Saiyan | Goku, Gohan, Vegeta, Trunks | As in LoG II | +10 to each core stat (LoG II, from my screenshot) |
| Super Vegeta / Super Trunks | Vegeta, Trunks | As in LoG II | About +15 (my memory). Read the real value from the ROM. |
| Super Namek | Piccolo | As in LoG II | About +5 or +6. Read the real value from the ROM. |
| Super Saiyan 2 | Gohan | Cell Games (Rage) | LoG II half: +20 to each core stat, stronger than Super Vegeta / Super Trunks (mine). Buu saga: between Super Saiyan and Super Saiyan 3 for stats and ki drain |
| Super Saiyan 2 | Goku | Majin Vegeta fight | Same |
| Super Saiyan 2 | Vegeta | Next time playable after his death against Fat Buu (I believe a side story; confirm) | Same |
| Super Saiyan 3 | As in Buu's Fury | As in Buu's Fury | As in Buu's Fury |

- Goten and kid Trunks use Super Saiyan 1 only. Gotenks goes directly to Super Saiyan 3.
- Gohan keeps Super Saiyan 2 in the Buu saga until his Ultimate form, which then replaces his transformations.
- Super Saiyan 2 has the lightning aura. If Super Saiyan 3 has no lightning, add it.
- All numbers are tuned in play.

### 6.6 Gohan's outfit (mine)

After his Hyperbolic Time Chamber training, Gohan wears the purple Piccolo-style gi in every form once he is playable again (mine).

- In LoG II the player loses Gohan before the training (in the Demon Clothes) and gets him back after it in armor.
- The cutscenes between the training and the point where Gohan is playable keep the armor. From the moment he is playable, he wears the gi.
- A later slice may add a short scene where Gohan changes into the gi. Not in slice 1.
- 2026-10-16: once Gohan has the gi (from the first moment he is playable after the chamber), every later cutscene and NPC appearance uses the gi too. This includes the Cell Games Arena NPC and the post-Cell scene (`docs\research\re-outfit.md` section 5). Slice 1 leaves these in armor on purpose; change them in the slice after my test slice 1.

- Method (Rulings 27 and 35, 2026-10-17): each gi frame is the same-form original (set 56 base, 59 Super Saiyan, 58 Super Saiyan 2) with its armor repainted as the gi. The pose, head, hair and record geometry stay the original's. Set 53 is a style reference only. Every frame fits the player's 1024-byte VRAM slot (32x32 or smaller).
- Hair (final, 2026-10-16): base-form Gohan keeps the shorter hair of the armor sprites (set 56), not the longer Android saga hair of the Demon Clothes set 53.
- Chest (final, 2026-10-16): all three gi forms open the collar into a small V-neck, like Piccolo. A hint only, never a bare chest: the gi covers the torso. Front frames: a narrow V at most 2 pixels deep. Side frames: at most 1 skin pixel at the collar, or none. Back frames: no torso skin. Existing skin palette indices only.
- Gi details (the first plan edited set 53; superseded by the method line above, details still apply):
  - Remove the white neck piece.
  - Boots match Piccolo's sprite (brown, palette 34 and 35).
  - The purple moves toward Piccolo's gi (palette 88 and 89).
  - Red sash. Blue wristbands.
- References: `data\reference\D6FHgvhUIAATrwf.jpg` (manga, Cell Games), `images.jpg`, the Piccolo sprite.
- Portraits: the International portrait sheet appears to show Super Saiyan Gohan in the gi. Port those portraits for every form.

### 6.7 Backlog candidates (not agreed)

- My idea (2026-10-16), after slice 1 proves the art pipeline: bring the Buu's Fury Piccolo and Goku sprites into LoG II. Sheets are in `data\sprites\`.
  - Piccolo risk (mine): in LoG II, Piccolo's transform removes his turban and cape. Buu's Fury has no such frames, and its cape is larger. The transform and the caped and uncaped frame sets must be planned.
  - My scope (2026-10-16): no patch to Buu's Fury and no Buu's Fury code work. Read-only asset extraction is allowed (Ruling 34).
- My idea (2026-10-16): look at the Buu's Fury stat screen look for LoG II.
- My idea (2026-10-16): make Super Vegeta / Super Trunks (Grade 2) a Cell-saga-only form that uses the unused prototype sprites. Only down and side poses exist, so most frames must be rebuilt. Sheets: `... Prototype - Super Vegeta.png`, `... Prototype - Super Trunks.png`.
- Restore the unused Super Vegeta and Super Trunks sprites, so the buffed forms look different.
- Draw Sword Blast frames for armor Trunks and Super Saiyan Trunks.
- Fix the Goku Spirit Bomb frame that faces down and shows his old gi.

---

## 7. Slices

| # | Slice | Result I can test |
|---|---|---|
| 1 | LoG II: Gohan's gi and playable Super Saiyan 2 | Section 8 |
| 2 | LoG II: stat points, gold bonus bars, form values, new moves | A LoG II build with the new progression |
| 3 | Buu's Fury: knockback, block, hold-attack special, Super Saiyan 2 | A Buu's Fury build with the new combat |
| 4 | Merge: one ROM, one save, bridge, prompts, transition | The continuous game |
| 5 | LoG1 feasibility | A report, not a build |

Risk for slices 3 and 4 (added 2026-10-16): a modder working on these games (Reddit, AceofheartsDev) reports that LoG II and Buu's Fury are sibling engines with their own quirks, not one engine. Before slice 3, run a short comparison: the sprite codec, sprite set and record layout, appearance table, form objects and save format in Buu's Fury, against `RE-BIBLE.md`. The merge plan depends on how much differs.

Order is mine: one thing at a time, slice 1 first.

---

## 8. Slice 1 in detail

### 8.1 Result

A patched LoG II (USA) ROM and a test save. In it, Gohan wears the gi after the Time Chamber, and he can transform into Super Saiyan 2 at will after the Cell Games.

### 8.2 Parts

**A. Tools**
- A compressor for the Webfoot codec, or proof that the game accepts raw (type 0) frames. The simplest valid encoder is sketched in `re-sprite-decompression.md`. Round-trip test: every original frame must decompress, recompress and decompress again to the same bytes.
- A frame export and import tool: sprite set to indexed PNGs (shared palette) and back.
- A ROM build script: copies the base ROM to `builds\`, applies each change from source files, and prints the SHA-1 of the result. The base ROM is never edited.

**B. Gi art**
- Gi base: set 53 frames with the edits in 6.6.
- Gi Super Saiyan: the gi bodies from the gi base, with the gold hair and face from set 59, frame by frame.
- Gi Super Saiyan 2: **my call:** start from the gi Super Saiyan frames and take the hair shape from set 58 (Rage). Set 58 has fewer animations than set 59, so frames it lacks get its hair drawn onto the Super Saiyan frame.
- All art uses colors that already exist in the shared OBJ palette. No palette entry changes.
- I review every frame as a contact sheet before it goes into a build.

**C. Outfit switch**
- **My call:** replace the graphics of Gohan's armor sets (55, 56, 59, and 58 for the playable Super Saiyan 2) with the gi art, and keep set ids and frame records the same. The game already shows these sets only after the Time Chamber, so no code change is needed for the switch. Confirm in the code which events use sets 55 and 56 before replacing them.
- Frame size and box (w, h, dx, dy) stay the same where possible, so hit boxes do not change.
- My rule: cutscene Gohan keeps the armor until Gohan is playable (6.6). So the armor art must stay available for those cutscenes. If cutscenes and playable Gohan share one set, replacing the art is not enough, and the switch must go through the playable appearance id. Two armor sets exist (55 and 56); one may be the cutscene copy. Confirm first.
- Save-format finding (`re-save-format.md`): each character record stores an appearance id (Gohan's post-Cell value is 2, which maps to set 56). So the outfit is chosen by story data, not fixed per character. Changing what the post-Time-Chamber appearance id points to is an alternative to replacing the armor art. The builder picks the option that changes the least.

**D. Playable Super Saiyan 2**
- Find the form system in the code: how the player transforms, how each form's stat bonus and ki drain are stored, and how Rage is forced on in the Cell fight.
- Add Super Saiyan 2 as a form Gohan can select, after the Super Saiyan step.
- **My call (recommended by the reviewer):** gate it on the story flag the game already sets when Cell is defeated. Add no new save field. This keeps old saves loading and keeps clear of the anti-piracy check.
- Stats (mine): +20 to each core stat, double the Super Saiyan +10 and above Super Vegeta / Super Trunks. Ki drain higher than Super Saiyan as a starting point (mine). Tune in play.
- Rage in the Cell fight never drains ki; that is story intent. The usable Super Saiyan 2 drains ki (mine).
- Input (mine): Super Saiyan uses the Z transform in LoG II. Buu's Fury shows a "Z" with a 3 on the HUD for Super Saiyan 3. Super Saiyan 2 gets the same treatment: a HUD icon of a "Z" with a 2, drawn to match the LoG II HUD. References: `data\sprites\... The Legacy of Goku II - Miscellaneous - Player HUD.png` and `... Buu's Fury - Miscellaneous - HUD.png`. **My call:** the transform input steps base, Super Saiyan, Super Saiyan 2, the way Buu's Fury steps to Super Saiyan 3. Confirm against the Buu's Fury input in the code.
- Visuals: the gi Super Saiyan 2 set (set 159). Its lightning is blue spark pixels in the sprite frames. Rage has no separate aura object (Task 6, CONFIRMED).
- Rage in the Cell fight (mine): unchanged. It keeps its current stats (I believe all stats at 100) and its event behavior. Playable Super Saiyan 2 is a second form entry. Winning the Cell fight (flag 195) unlocks it.
- **Superseded (Ruling 31, Global Constraints):** the build keeps Rage on armor set 58. In the Cell fight, gi Gohan becomes armored Rage, then armor again after Cell. Switching Rage to the gi art (set 159) is my call (see my questions in `docs\ledger\progress.md`).

**E. Portraits**
- Find how portraits are stored (probably the same codec). Port the International gi portraits for base, Super Saiyan and Super Saiyan 2.
- Source: no International ROM exists in `data\`. The source is my ripped sheet `data\reference\122601.png` (International, labelled "Japanese Version"). `38248.png` is the US sheet. Converting from the image is accepted: slice, fit to the portrait format and palette, and touch up by hand.
- If portraits take more than a short effort, move them to slice 2 and say so.

**Scope of the outfit change (final, option A):** slice 1 covers Gohan's sprites and portraits only. Cutscene stills, ending art, menu icons and any other armored image after the Time Chamber are listed when found, with file and address, and scheduled later. They do not block slice 1.

**F. Test save**
- Done: `test-data\saves\log2_lv40_postcell.sav`. Three slots, after Cell (flag 195 set, flag 196 clear), all six characters at level 40: slot 1 Capsule Corp save point, slot 2 East District 439 save point, slot 3 Capsule Corp post-Cell spawn. I loaded all three in mGBA on 2026-10-16, which also confirms the save byte order. Built by `scripts\permanent\rom\log2_save.py`.

### 8.3 Acceptance tests (final, in mGBA)

1. Load the test save. Gohan wears the gi. Walk in all four directions, attack, use each special, take a hit, and talk to someone.
2. Transform to Super Saiyan. The gi stays, and the hair is gold.
3. Transform to Super Saiyan 2. Spiky hair, blue lightning, the "Z2" HUD icon, and higher stats than Super Saiyan. The lightning is blue spark pixels drawn into the set 159 sprite frames (anim 4 idle and some other animations). It is not a separate aura object, so it shows only in those frames (Task 6, CONFIRMED). Pass: blue sparks show around the head in the idle pose. The USA status screen does not show form bonuses, so the builder proves the stats with a memory readout of the live stat values and a damage comparison against the same enemy (final, option A). The on-screen display comes in slice 2.
4. Leave East District 439 for the world map. The game does not return to the title screen.
5. Load a real early-game save made on the unpatched ROM. It still works. My current `.sav` is blank, so I make this save once before slice 1 testing (one in-game save at the first save point). The same save serves test 4.
6. Play the Time Chamber exit, if a save near it exists. The exit cutscene keeps the armor. The gi shows from the first moment Gohan is playable after it (final, design 6.6). Pass: armor in the cutscene, gi as soon as you control Gohan.

### 8.4 Risks

| Risk | Effect | Response |
|---|---|---|
| No free space for new frames | Must expand the ROM | Look for free space first. Expand only if needed, then test the anti-piracy point first. |
| Set 58 lacks many animations | More hand-drawn hair frames | Measure the gap before the art starts. Report the count to me. |
| The form system is hard-coded per event | Super Saiyan 2 needs more code | Report the finding before building around it. |
| Sets 55 or 56 are used before the Time Chamber | The gi shows too early | Confirm their users in the code first. |
| Post-Cell is not playable in LoG II | The test save is set before the Cell Games | The save task reports this. Test Super Saiyan 2 with a debug unlock instead. |

### 8.5 Left to the builder

- Tool internals, file formats for intermediate art, and script names.
- The exact frame edits, within the look in 6.6, subject to my review.
- How to place new data in the ROM.
