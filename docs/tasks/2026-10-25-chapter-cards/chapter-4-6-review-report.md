# Chapter cards 4-6 review: report (2026-10-30)

Brief: `chapter-4-6-review.md` in this folder. This is a study only. No module, list or ROM changed.

Labels: CONFIRMED (C) = read from ROM bytes or quoted from a guide line. LIKELY (L) = strong evidence, no emulator run. SPECULATIVE (S) = a guess. LoG II addresses are the base ROM (USA). "g1" = `LOG2_Guide.txt`, "g2" = `LOG2_Guide_2.txt`, "BF guide" = `buusfury_guide.txt`, all in `docs\research\sources\guides-2026-10-29\`.

---

## SHIPPED

| Ask (brief) | Result |
|---|---|
| 1. Buu's Fury pattern: what follows each BF card. Does any BF card lead into the world map? | No. 0 of 12. Seven lead into a cutscene or dialogue (1, 3, 4, 5, 7, 10, 11), three into a short walk into a scene (8, 9, 12), one into free play (2), one into a wake-up scene and then free play (6). Section "Buu's Fury: what follows the card" |
| 2. Card 4: why it feels odd, better points near the start of the lab section, recommend one | Recommended by elimination: the start of the post-Android 20 scene (fade 120 after the fight). It is not the BF shape: the card comes before the fight's own aftermath. Section "Card 4" |
| 3. Card 5: the Kami scene after flag 127, can the card lead into it | Yes. The world map sits between 127 and Kami. The clean point is the start of the Kami scene in the throne room (map 9,6). Continue then reads flag 129. Section "Card 5" |
| 4. Card 6: the Imperfect Cell line, the fade, the Lookout, the lengths | v5 already plays card 6 there. The line is the record right before the card's record. No change. Section "Card 6" |
| 5. Proposal table for cards 4-6, card 7 spacing | Section "Proposal". Card 7 does not move: 14.8 / 16.2 percent |
| Bible rows, tag CH6 | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_ch46.md` (sections 8, 9, 11, 13) |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| The final points for cards 4 and 5 | A proposal only. The brief forbids module changes | Answer "my questions" 1-3 |
| Card 6 in play | Your notes do not say that card 6 showed. No save reaches cards 2-6 (v5 report) | Question 4 |
| The look of an in-field card at the new points | No emulator run | Check in the next build |

---

## Short answer

1. **Buu's Fury never cuts from a card to the world map** (C, guide; bytes for 6 of 12). The card plays in black. Then a map loads and fades in on a scene (7 of 12), on a short walk into one (3), or on free play (2).
2. **Card 4 feels odd because the scene ends in free play.** The card op adds its own fade out and fade in. After it, you stand on the same field and the game says "Journal Updated!". Nothing new starts (C, bytes).
3. **Card 4: move it to the start of the post-Android 20 scene.** The vanilla script already fades out 120 frames after the fight and fades in 120 frames on the gang flying in. Then Android 20 talks, Trunks arrives, and Bulma names the lab. Continue still reads flag 86, set at the end of the same scene. The chapter shares do not change. The cost: the card comes before the fight's own aftermath (Android 20 is still there), not after a closing cutscene as in BF. It wins because the other points fail.
4. **Card 5: play it when Piccolo enters Kami's throne room.** The scene opens on "KAMI: Piccolo. You've returned." Continue reads flag 129, which the same scene sets. BF ch 7 is the model: you fly the world map to Bulma's airship, the card plays on arrival, and a cutscene follows.
5. **Card 6 already plays after "...I must figure out how he does that!"** The next view is the Lookout, with dialogue. No change is needed, and chapters 6 and 7 keep their lengths (11.3 and 14.8 percent of g1).

---

## Buu's Fury: what follows the card

Bytes from `scripts\one-time\2026-10-25-chapter-cards\ch46_bf_sites.txt` (C). BF record types 4, 5 and 7 are not the LoG II types. A type 7 record's +4 word names the next scene table (seen at ch 3, 5 and 11). I did not decode BF text records (types 4 and 5). That they hold the dialogue is L: they sit where the guide has dialogue.

| Ch | What follows the card | Class | Proof | Label |
|---|---|---|---|---|
| 1 | `push 15 ; ext 35` music, `push 0,2,0,0,0 ; ext 115` map load, `ext 121` fade in, then type 5 and 4 records. Guide: "Goku will be talking to King Kai" (lines 9-10) | Map load into a dialogue scene | Record `rom:0x780428` | C (bytes, guide) |
| 2 | `push 2,1,0,136,112 ; ext 119`, fade in 100, wait 60. Guide: "you'll be playing as Gohan, back on Earth. Leave the kitchen" (line 160) | Map load into free play | Record `rom:0x78290C` | C (bytes, guide), L (ext 119 = map load) |
| 3 | The card ends its record. A type 7 record names table `rom:0x782E14`: `push 2,8,0,248,248 ; ext 119`, fade in 100, then type 5 records. Guide: "starts outside of Gohan's house. Goten and him will decide to train" (line 447) | Map load into dialogue | Record `rom:0x780C60`, `rom:0x782D9C` | C (bytes, guide) |
| 4 | No site. Guide: "As soon as you land, Supreme Kai will tell you that you have to search for Babidi's space ship" (line 765) | Arrival into dialogue | Guide | C (guide) |
| 5 | `push 4 ; ext 154 ; end`. A type 7 record names table `rom:0x78DB3C`, which starts with a type 4 record. Guide: "When the Z-Fighters and Majin Vegeta arrive at the stadium, everyone is shocked" (line 1025) | Cutscene | Record `rom:0x78F31C` | C (guide), L (bytes: type 4 not decoded) |
| 6 | No site. Guide: "The chapter starts, at Rocky Canyon, with Goku just waking up" (line 1140). Then you walk to a flight pad | Wake-up scene, then free play | Guide | C (guide) |
| 7 | No site. The card plays after a world map flight: "fly to the world map, and fly to an airship that Bulma is flying ... That will finish off the chapter" (lines 1738-1740). Then "a cutscene of the Eternal Dragon being summoned" (line 1751) | World map BEFORE the card, cutscene after | Guide | C (guide) |
| 8 | No site. "You'll be playing as Hercule! ... Just walk forward until you reach a house ... You'll then see a short cutscene" (lines 1856-1859) | Short walk into a cutscene | Guide | C (guide) |
| 9 | `ext 117`, `push 15 ; ext 35` music, `push 0 ; ext 51`, end. Guide: "The chapter starts back in King Yemma's office, with Goku. Walk outside, and Goku will wonder aloud" (lines 2047-2048) | Short walk into dialogue | Record `rom:0x77EA48` | C (bytes, guide), L (ext 117) |
| 10 | No site. The card plays after a yes/no prompt (lines 2305-2307). "As soon as you enter the area, you'll find Vegeta standing up against Buu" (line 2318) | Cutscene, then a fight | Guide | C (guide) |
| 11 | The card ends its record. A type 7 record names table `rom:0x794490`: `push 19,3,1,0,216 ; ext 115` map load, music 35, two walks, fade in 30, then a type 5 record. Guide: "The Supreme Kai and the old Kai talk about Buu, in a cutscene" (line 2475) | Map load into a cutscene | Record `rom:0x79817C`, `rom:0x7941C8` | C (bytes, guide) |
| 12 | No site. "Walk into the Capsule Corp building ... You'll be asked if you won't to continue into the final sequence" (lines 2567-2569) | Walk into the ending | Guide | C (guide) |

**Answer to me (C).** No BF card leads into the world map. Your memory is right: most lead into a cutscene or dialogue. The world map shows up only before a card (ch 7: the flight to the airship). Ch 4 and ch 7 are "arrival" cards: the card plays when you get somewhere, and a scene starts.

---

## Card 4 (Into Gero's Lab)

### Why it feels odd

The v5 card plays at the end of the post-Android 20 scene. That record has no fade and no map load (C, `ch46_table_card4_post20.txt`, record [46] `rom:0x3D540A`). So the module adds a 60-frame fade out, the card, a map reload and a 60-frame fade in (v5 bytes `00 3C 02 28 00 04 02 91 00 3C 02 29` at `rom:0x92FA8E`, C). After it, only `ext 86 (1)` HUD on, sound 62 and "Journal Updated!" run (`rom:0x3D5500`, [47] `rom:0x3D550A`, C). You get control on the same field. Nothing new opens after the card. BF never does that (table above).

### Candidates

| Point | Bytes | Continue | What plays after the card | Shares g1 / g2 (ch 3, ch 4) | Verdict |
|---|---|---|---|---|---|
| A. Start of the post-Android 20 scene | Death event table `rom:0x3D5524` (held by the event struct at `rom:0x3FD7A0`: `0x080106B3`, `0x083D5524`), word 0 = record `rom:0x3D4874`. Ops: `ext 139 (5000)` EXP, `ext 88` bar off, `ext 86 (0)` HUD off, `00 78 02 28` fade out 120 at `rom:0x3D4890`, `00 06 02 31` music 6 at `rom:0x3D4894`, two `move_to`, face, `00 78 02 29` fade in 120 at `rom:0x3D48B0`, then the gang flies in | 86 (one SET `rom:0x3D542A`, record [46] of the same table, no CLR) | Black, then the gang flies in. "VEGETA: What a waste of technology.", Android 20's lines, "PICCOLO: Hey guys look! Trunks is here!", Vegeta learns Trunks is his son, Bulma: "Dr. Gero's lab was hidden in a cave somewhere in the Northern Mountains." | 12.5 / 12.7, 14.9 / 10.6 (unchanged: g1 line 538 "The gang runs in and Future Trunks arrives" is this scene's first line) | **Recommended by elimination.** Cost: Android 20 is still on screen after the card ("ANDROID 20: I don't understand!"), so the card splits the fight from its aftermath |
| B. Lab entrance: Gero wakes 17 and 18 | Table `rom:0x3D9F5C` (held by walk-in items at `rom:0x402DFC` and `rom:0x403B80`), word 0 = record `rom:0x3D99BC`: HUD off, camera, wait 60, `ext 34`, music 7, `push 8,60,1,184,168 ; ext 35` map load to the lab. No vanilla fade | 124 (one SET `rom:0x3D9F4D`, end of the same table) | The lab interior, "DR. GERO: I had hoped to avoid activating them again so soon..." | 23.9 / 19.1, 3.6 / 4.1 | Reject: chapter 3 grows past BF's largest (23.8), chapter 4 is shorter than BF's shortest (3.7). The card would sit 46 g1 lines before card 5 |
| C. Northern Mountains landing | World map item `rom:0x3FBC5C`, condition `0x00010056` (flag 86 set) at `rom:0x3FBE50`; script `rom:0x3FBC50` = `push 8,1,1,272,128 ; ext 38 ; end`. Map 8,1 has two regions only: an A-press script and a save point (`ch46_probe_maps.txt`) | None: the landing sets no flag | Free play on 8,1 (g1 558: "From the first area, save if you want") | Same as A | Reject: the script runs on every landing while 86 is set, so the card would replay. It opens on free play |
| D. First Gero encounter | Table `rom:0x3D5E68` (word for `rom:0x3D5DC4`): sound, SET 90, Gero walks, one line, then `push 14,1 ; ext 104` fight | 90 | "DR. GERO: You're trying to find my secret lab aren't you?", then the fight at once | About 14.9 / 14.5, 12.5 / 8.8 (S: anchors g1 569, g2 542 by hand) | Reject: one line, then a fight. Not a section start |

### Recommendation: A (C for the bytes, L for the look)

- **Why A:** B fails the spacing, C replays on every landing and opens on free play, and D is one line before a fight. A is the only point near the lab section that is a black-to-black cut and opens on a scene with dialogue.
- **The cost (trade-off):** A is not the BF shape. In BF the fight's closing cutscene plays first, then the card (ch 11: the Kid Buu change, then the card). In A the card plays between the Android 20 fight and that fight's aftermath: Android 20 is still there and speaks first after the card.
- **The gain:** the scene sets up the chapter's goal. Trunks arrives, Android 20 turns out to be Dr. Gero, Bulma names the lab, and the scene ends on "Alright, let's go find that lab!"
- Continue does not change. The card and SET 86 run in one scene, and the player gets no control between them (L: by structure, no save op in the table).
- **Insert point:** after the fade out and the music op, before `1d 03 1c 84 10 84 10` (`move_to`) at `rom:0x3D4898`. Then song 6 is already chosen when the card ends.
- **One module change.** No map load follows, so the card op must still reload the map graphics (the v5 `IN_FIELD` path, `0x08005F1A(map, 1)`). It must not add the extra 60-frame fades, because the vanilla fades are there. Today `IN_FIELD` does both. So the row needs a "reload only" mode (C: v5 module `story_ops`, `IN_FIELD = {4}`).
- The old card 4 record `rom:0x3D540A` goes back to vanilla.

---

## Card 5 (A New Horror)

### Where the Kami scene is (C)

| Fact | Bytes |
|---|---|
| The flag 127 record ends the post-Android 18 scene and loads the world map | `rom:0x3D9864`: `00 5A 02 28` fade 90, `ext 86 (1)`, `00 7F 02 1B` SET 127, `1d05 0c814602a8709040` `push 6,99,1,2616,1056 ; ext 39`, leader Piccolo, fade in 90 |
| The Lookout landing is a world map item. Its condition is flag 127 set. Its script is a plain map load | Condition `0x0001007F` at `rom:0x3FBE38`, item `rom:0x3FBC08` (A-press), script `rom:0x3FBBFC` = `push 9,1,1,768,832 ; ext 38 ; end`. The next pair gates item `rom:0x3FBC28` with the script `rom:0x3FBC1C` = 127 set and 158 clear (L: the star marker) |
| Map 9,1 has no scene region (world map exit, two flight pads, a save point) | `ch46_probe_maps.txt` (region list only; a layout item is not listed) |
| The building door warps to the throne room, map 9,6, at (112,228) | Warp `rom:0x534D4C`: rect (216,176)-(233,201), dir 1, to 9,6 var 1 at (112,228) |
| Map 9,6 (entry 266) region 0: condition flag 129 clear, a walk-in scene item, rect (73,185)-(160,240). The arrival point is inside the rect | `0x00020081`, item `rom:0x404468` (factory `0x0800D7E1`, trigger `0x0800D765`), data `0x083DF720` |
| The scene table starts at `rom:0x3DF720`. Word 0 = record `rom:0x3DECB8`, no fade and no map load. Word 1 = the Kami line | `rom:0x3DECB8`: `00 22 02 31` music 34, `00 00 02 56` HUD off, `00 32 02 2E` sound 50, end. Then `rom:0x3DECC8` "@KAMI: Piccolo.  You've returned." |
| The same table sets 129 at its index 17, then fades out 90 and cuts to Goku's house (2,20) | `rom:0x3DF28F` `00 81 02 1B`, `rom:0x3DF293` `00 5A 02 28`, `push 2,20,1,160,264 ; ext 39` |

So the world map sits between flag 127 and the Kami scene (C). The player flies there, lands on 9,1, walks into the building and through the first door (g1 730-731: "Head straight into the Throne Room. Just go straight into the building and the first door right in front of you is your destination"; g2 610).

### Candidates

| Point | Bytes | Continue | After the card | Shares g1 / g2 (ch 4, ch 5) | Verdict |
|---|---|---|---|---|---|
| a. Kami scene start (throne room) | Record `rom:0x3DECB8` (table word `rom:0x3DF720`, the only word naming it), insert at `rom:0x3DECC3`, after `push 34 ; ext 49` (song 34) and `push 0 ; ext 86` (HUD off), before `push 50 ; ext 46`. In-field: fade out, card, map reload, fade in (the v5 card 4 path, both parts) | 129 (one SET `rom:0x3DF28F` in the script region, same scene run) | "KAMI: Piccolo. You've returned.", then the Kami and Piccolo talk | 14.9 / 10.6, 15.8 / 9.8 | **Recommended** |
| b. Your literal idea: the 127 fade, then load the throne room, not the world map | v5 card point unchanged (`rom:0x3D9867`). Change the push list at `rom:0x3D9873` from `6,99,1,2616,1056` to `9,6,1,112,228` | 127 (as v5) | Black, card, the throne room fades in, the walk-in scene starts | 14.1 / 9.4, 16.7 / 11.0 | Option. Cleanest look, but it removes the flight and the free roam on the Lookout |
| c. Lookout landing | Script `rom:0x3FBBFC` | None set there | Free play on 9,1 | About as a | Reject: the landing runs on every Lookout visit while 127 is set. A card there needs a gate and still replays between 127 and 129 |

### Recommendation: a (C for the bytes, L for the look)

- The card plays when Piccolo walks in, and the next words are Kami's. That is the BF arrival card (ch 4, ch 7).
- Continue moves from 127 to 129. A save made on the way to the Lookout then shows Chapter 4. That is right, because card 5 has not played yet. After the scene, Continue shows Chapter 5. The flags still rise: 86, 129, 148.
- 129 has three CLR byte hits by shape `00 81 02 1C`: `rom:0x22FB1A`, `0x22FE4E`, `0x47F7DE`. All three are outside the script region (`rom:0x3B5000-0x420000`), so they are LIKELY data, not script (L). The CHP sweep of the script region found one SET and no CLR (C).
- **Insert point:** `rom:0x3DECC3`, after the song and the HUD-off ops, as for card 4. At `rom:0x3DECBB` (before `push 34 ; ext 49`) the card op would replay the map song 31 after the card, and the HUD would show during the fade in.
- With option a, the v5 card 5 copy goes away and record `rom:0x3D9864` (word `rom:0x3D9968`) goes back to vanilla.
- The scene fires when the door puts you at (112,228), inside the rect (C: bytes). That it fires on arrival, before a step, is L. The room shows for a moment before the card's fade out. Check the look in play.
- **Trade-off against b.** Option b gives a black-to-black card like cards 2 and 3 ("perfect"), with no in-field reload. It cuts out the flight, the Lookout roam and Korin's fish trade in that window (g1 725-728). Korin is still there later (L). Whether the walk-in scene fires after a script map load, not a door, is S. It needs an emulator check.

---

## Card 6 (Perfection)

### The line and the cut (C)

| Item | Bytes |
|---|---|
| The line | Type 2 record `rom:0x3E5E80` (table `rom:0x3E6078`, named by `rom:0x4066E0`; word `rom:0x3E61C8`, index 84), portrait 39: "#Instant transmission... `0B` That's quite a move... `0B` ...I must figure out how he does that!" |
| Before it | Index 82 "Be seeing you!" (Goku), index 83 `rom:0x3E5E6A`: `ext 42 (10)` flash, `ext 52 (60)` (an actor command on actor 60; L: Goku leaves), `ext 43 (10)`, `ext 69 (60)` wait |
| Right after it | Index 85 `rom:0x3E5ED4`: `00 B4 02 28` fade out 180 at `rom:0x3E5ED7`, `push 9,1,1,736,416 ; ext 39` (the Lookout), face, three spawns, camera, `00 B4 02 29` fade in 180, wait 60 |
| Then | Index 86 "That was an honorable move, Tien... but it wasn't enough.", index 87 "MR. POPO: Vegeta and Trunks are coming out of the Hyperbolic Time Chamber!", index 88 walks, HUD on, `00 94 02 1B` SET 148 at `rom:0x3E605A`, index 89 "Journal Updated!" |
| v5 today | Word `rom:0x3E61CC` names the copy `0x0892FAD8`. The card op `00 06 02 91` is at `rom:0x92FADF`, right after `00 B4 02 28`. Word `rom:0x3E61C8` still names the vanilla line (v5 ROM `80cf4ab9...`, read) |

So v5 already plays card 6 at the point you describe: after Cell's line, in the fade to the Lookout. The next view is the Lookout with dialogue. Continue reads 148, set at the end of the same scene. **No change is proposed** (C).

### Lengths

| Chapter | g1 | g2 | Against BF |
|---|---|---|---|
| 5, today (127 to the Cell line) | 16.7% (719-932) | 11.0% (601-685) | Inside 3.7-23.8 |
| 5, with card 5 at the Kami scene | 15.8% (730-932) | 9.8% (610-685) | Inside |
| 6 (the Cell line to 158) | 11.3% (933-1077) | 8.2% (686-748) | Inside, above the median |
| 7 (158 to 195) | 14.8% (1078-1267) | 16.2% (749-873) | Inside |

BF median: 6.8 percent with ch 12 (the placement report figure), 7.5 percent for ch 1-11. Range 3.7-23.8 (C, `ch46_guides.txt`). The anchor for card 6 is now g1 line 933 ("Goku uses Instant Transmission to get to Cell") and g2 line 686 (the Lookout header after the Android 17 box). The placement report used g1 938 and g2 689. The difference is 3-5 lines.

**The shorter leap is not a problem (C).** Chapter 6 is 11.3 percent of g1, above BF's median. Only two BF story chapters are longer (ch 3, 12.4 and ch 6, 23.8). It holds two boss fights (Semi-Perfect Cell, Perfect Cell vs Trunks). The card does not move, so chapters 6 and 7 do not get shorter.

---

## Proposal

| # | Title | Point | Bytes | Continue (rising) | What plays after the card | g1 / g2 | Label |
|---|---|---|---|---|---|---|---|
| 1 | The Mysterious Youth | New game | (hook) | none | First scene | 9.1 / 12.8 | C |
| 2 | Preparation | Fade 120, unchanged | `rom:0x3BFDBB` | 26 | Map 2,1,1 | 19.8 / 28.5 | C |
| 3 | The Androids Appear | Fade 240, unchanged | `rom:0x3B856D` | 68 | "Three years later..." | 12.5 / 12.7 | C |
| 4 | Into Gero's Lab | **Start of the post-Android 20 scene** | Record `rom:0x3D4874` (word `rom:0x3D5524`), insert before `rom:0x3D4898`, after fade 120 `rom:0x3D4890` and music 6 `rom:0x3D4894`. Reload only, no extra fades | 86 | The gang flies in, Android 20 and Trunks talk, Bulma names the lab | 14.9 / 10.6 | C (bytes), L (look) |
| 5 | A New Horror | **Kami scene start, map 9,6** | Record `rom:0x3DECB8` (word `rom:0x3DF720`), insert at `rom:0x3DECC3` (after song 34 and HUD off). Fade out, card, reload, fade in | **129** | "KAMI: Piccolo. You've returned." | 15.8 / 9.8 | C (bytes), L (look) |
| 6 | Perfection | Unchanged: fade 180 after Cell's line | `rom:0x3E5ED7` | 148 | Lookout 9,1: "That was an honorable move, Tien..." | 11.3 / 8.2 | C |
| 7 | The Cell Games | Unchanged | `rom:0x3DB4BB` | 158 | Map 1,4, the caption | 14.8 / 16.2 | C |
| 8 | The Champion's Hour | Unchanged | `rom:0x3EC67F` | 195 | Capsule Corp | 1.4 / 0.9 | C |

**Card 7 spacing: no change.** Card 7 stays at 158 and card 6 stays put.

**Base bytes for a later build (C, `chapter_cards.record_ops` on the base ROM; r39 holds the same bytes and the same table words):**

| Card | Record | Length | SHA-1 | Op the card goes before |
|---|---|---|---|---|
| 4 | `rom:0x3D4874` | 0xD9 | `b14508fcb70dfa4aad2e4d1c8db9da6bc3767e32` | `rom:0x3D4898` `1d031c84108410` |
| 5 | `rom:0x3DECB8` | 0x10 | `86e5f5c86fc20d411c03352f0031cc262eef4ddc` | `rom:0x3DECC3` `0032` |

Record `rom:0x3D4874` has three `jz` jumps after the insert point (`rom:0x3D48BB`, `0x3D48D4`, `0x3D48ED`). They jump forward inside the part after the insert, so `npc_gi.relocate` keeps their offsets (L: not run).

---

## My questions

1. **Card 4:** move it to the start of the post-Android 20 scene (black after the fight, card, then the gang and Trunks arrive)? Continue stays on flag 86. The cost: Android 20 is still there after the card, so the card splits the fight from its aftermath. BF puts the closing cutscene first. The other points fail on spacing or replay.
2. **Card 5:** play it when Piccolo walks into Kami's throne room (option a, Continue 129, keeps the flight)?
3. **Card 5, your literal idea (option b):** or keep the card at the 127 fade and load the throne room straight away, so there is no world map? This removes the flight and the Lookout roam before Kami. Its arrival scene needs an emulator check (S).
4. **Card 6:** did card 6 play in your test? v5 plays it right after "...I must figure out how he does that!", in the fade to the Lookout (C). If you saw it at another place, that is a bug and I need to know where.

---

## Files

- `scripts\one-time\2026-10-25-chapter-cards\ch46_probe.py`: text search over type 1 and type 2 records (webfoot unpack), whole scene tables decoded from +3, map region lists, bare scripts, warps into a zone.
- `ch46_probe_maps.txt`: maps 9,6, 9,1, 8,1, 8,60, the two landing scripts, warps into zone 9, the key records, the words that name them, the two quoted lines.
- `ch46_table_card4_post20.txt`, `ch46_table_card5_kami.txt`, `ch46_table_card6.txt`, `ch46_table_lab_gero.txt`, `ch46_table_lab125.txt`, `ch46_table_card4_gero1.txt`: whole scene tables. Except in `ch46_table_card4_post20.txt`, the "[0] END" line is a stray word before the table, so the bracket numbers run one above the table index (the report gives the table index).
- `ch46_bf_sites.py` and `.txt`: BF card records and what follows them, with type 7 targets.
- `ch46_guides.py` and `.txt`: shares for v5, the proposal and the rejected lab entrance point.
- `bible_rows_ch46.md`: rows tagged CH6.
