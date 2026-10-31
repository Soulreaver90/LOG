# Chapter card placement study: report (2026-10-29)

Brief: `chapter-placement-study.md` in this folder. This is a study only. No module, build list or build changed.

Labels: CONFIRMED (C) = read from ROM bytes or quoted from a guide line. LIKELY (L) = strong evidence, no emulator run. SPECULATIVE (S) = a guess. LoG II addresses are the base ROM. "g1" = `LOG2_Guide.txt`, "g2" = `LOG2_Guide_2.txt`, "BF guide" = `buusfury_guide.txt` (all in `docs\research\sources\guides-2026-10-29\`).

---

## SHIPPED

| Ask (brief) | Result |
|---|---|
| 1. Buu's Fury spacing: every chapter, its card point, what it covers, the pattern | Done. Section "Buu's Fury spacing" |
| 2. LoG II story map from the two guides, with the places they disagree | Done. Section "LoG II section map" |
| 3. Proposal: number of chapters, title, story point, flag and set site with bytes, why it is a section start | Done. 9 cards recommended, one optional 10th. Section "Proposed chapters" |
| 3. "What card 8 should become or whether to drop it" | Keep a card at the chamber exit time skip. Retitle it: the chamber title no longer fits there |
| 3. "How to space cards 3 and 4" | Merge them into one card at flag 86. The measured tight run is cards 4, 5 and 6, and the merge removes all of it |
| 3. One alternative where the choice is close | Card 5 at flag 129 instead of 127. Also the optional chamber card at flag 144 |
| 4. Story points with no clean flag, and what finding one would take | Section "Points with no clean flag" |
| 5. Bible rows, tag CHP | `scripts\one-time\2026-10-25-chapter-cards\bible_rows_placement.md` (sections 8, 11, 12, 13) |
| Label every claim and quote the proof | Done in each table |

## PENDING

| Ask | Why pending | My step |
|---|---|---|
| Final card list | A proposal only. The brief forbids module changes | Pick the rows in "Open questions" |
| Card 7 title (old card 8) | Two candidates. I did not pick for you | Pick "A New Guardian", "The Dragon Balls", or give your own |
| Cards 4 and 8 open at a scene end with no fade in the script | The card fades in from black itself (100 frames, BF timing). Whether the cut from the field looks clean needs an emulator run | Check in the first story-point build |
| In-game check of any story point | No emulator run in this study | None now |

---

## Short answer

1. **Nine cards.** Buu's Fury has 12, but its last one covers only the ending, and LoG II has fewer story turns.
2. **Card 8 ("Room of Spirit and Time").** Keep the card at the chamber exit. It is a clean time skip: fade out 240, a narration caption, then Goku brings Dende home. Rename it, because the section after it is Dende and the Dragon Ball hunt, not the chamber.
3. **Cards 3 and 4.** Merge them at flag 86, "The Secret of Dr. Gero". The guides do not show 3 and 4 as back to back (they are 7-11 percent apart). They do show that cards 4, 5 and 6 sit within 4 percent of g1. The merge and the next fix remove that run.
4. **Cards 5 and 6 are the tightest pair today.** Between flag 127 and flag 129 there is only one Lookout visit (g1 lines 719-736). Merge them into one card at flag 127.
5. **A correction to the trial report.** LoG II does not put the Kami fusion before the Cell reveal. Flag 127 is set after the Android 18 fight. The fusion comes after flag 129. The order is the anime order.
6. **A new card 2 at flag 26** ("Three Years to Prepare", your own placeholder title from 2026-10-25). Today chapter 1 covers 29 percent of g1 and 41 percent of g2. That is more than any Buu's Fury chapter (largest: 23.8 percent).

---

## Buu's Fury spacing

The BF guide has a header for each chapter. Share = guide lines in the chapter / 2571 lines (C, `placement_guides.txt`). Guide lines are a weak measure, because side quests and boss write-ups add lines. The second measure is areas and boss boxes.

| Ch | Title | Card plays (story point) | Areas | Boss boxes | Share | Label |
|---|---|---|---|---|---|---|
| 1 | The Other World | New game. Bytes: card, then music 15, map load (0,2,0,0,0), fade in (`rom:0x780433`) | Snakeway, Grand Kai's Planet, Cave of the Ancients, Other World Stadium | Olibu, Pikkon | 5.9% | C (bytes, guide 1) |
| 2 | Great Saiyaman | After the Goku and Pikkon draw cutscene ("After that, the chapter will end.", line 148). Next: Gohan on Earth (line 160). Bytes after the card: map load ext 119 (2,1,0,136,112), fade in 100, wait 60 (`rom:0x78291F`) | East District 439, Hercule City, West City, Capsule Corp, Musuka Circus | none boxed | 11.2% | C (guide, bytes after the card) |
| 3 | World Tournament | After Goku's return and the Janemba hint ("Then, the chapter will end.", line 436). Next: outside Gohan's house (line 447). The card is the last op of its record (`rom:0x780C6F`) | East District 439, Gravity Chamber, West City, Papaya Island, Stadium, Kami's Lookout | Goten, Idasa, Goten, Spopovich, Spopovich and Yamu (and two crowd boxes) | 12.4% | C (guide), L (bytes before the card do not decode cleanly) |
| 4 | Babidi | After Gohan and the Z-Fighters catch up (line 755). Next: landing in the Southwest Forest (line 765) | Southwest Forest, Babidi's Ship (3 stages), Yakon's Planet, Demon World | Pui Pui, Yakon, Dabura | 10.1% | C (guide), no card site found |
| 5 | Majin Vegeta | After Vegeta turns Majin ("Vegeta asking if they are afraid, signifies the end of the chapter.", lines 1014-1015). Next: arrival at the stadium (line 1025). Site `rom:0x78F32B` | Stadium, Rocky Canyon, Southwest Forest, Giant Crater | Majin Vegeta, Majin Buu and Babidi | 4.5% | C (guide), L (bytes) |
| 6 | Dragonballs | After Buu reforms ("The chapter then ends.", lines 1129-1130). Next: Goku wakes in Rocky Canyon (line 1140) | Rocky Canyon, Lookout, West City, 7 Dragon Ball sites | Pilaf's Guardian, Airship Warlord, Ninja Boss, Totenhotep, Broly | 23.8% | C (guide), no site found |
| 7 | Majin Buu | After the flight to Bulma's airship ("That will finish off the chapter.", line 1740). Next: the dragon is summoned (line 1751) | Capsule Corp, Kami's Lookout, West City | 2 Buu fights (not boxed by my shape) | 4.0% | C (guide), no site found |
| 8 | Janemba | After Gotenks escapes and is scolded ("the chapter ends as well.", line 1845). Next: play as Hercule at Buu's house (line 1855) | Buu's House, Snakeway, HFIL | Janemba, Super Janemba | 7.5% | C (guide), no site found |
| 9 | Super Buu | After the Super Buu birth cutscene (lines 2030-2037). Bytes: waits, fade out 100, card, then ext 117 and music 15 (`rom:0x77EA84`) | Snakeway, Planet of the Kais, Lookout, Capsule Corp, Chamber, Southwest Forest, Great Crater, Barren Wasteland | Goten, Super Buu (x3), Super Buu 2 | 10.5% | C (bytes, guide) |
| 10 | Fusion | After the prompt "ready to confront Majin Buu?": "Select yes, and the fight will be on -- the Chapter will end, first, though." (lines 2305-2307). Next: the Super Buu 3 fight starts (lines 2318-2321) | Great Crater, Buu's Stomach, Intestines, Brain | Super Buu 3, Z-Fighter Clones, Super Buu Clone | 6.1% | C (guide), no site found |
| 11 | Kid Buu | After Buu turns into Kid Buu (lines 2459-2463). Next: Supreme Kai's Planet cutscene (line 2475). The card is the last op of its record (`rom:0x79818B`) | Supreme Kai's Planet, Barren Wasteland, Planet of the Kais | Kid Buu | 3.7% | C (guide), L (bytes) |
| 12 | A New Beginning | Entry to Capsule Corp for the ending (line 2567) | Capsule Corp | none | 0.3% | C (guide), no site found |

**The pattern (C, from the 12 rows above).**

- **What starts a chapter.** A closing cutscene ends, often on a turn of the plot (Majin Vegeta, Buu reforms, Super Buu, Kid Buu). The card plays at that cut. The next chapter opens in a new place, often with a new playable character or a new goal.
- **Before a fight is allowed.** Chapter 10 opens after a yes/no prompt and right before the Super Buu 3 fight.
- **Typical gap.** The median share is 6.8 percent (12 chapters) and the range is 3.7-23.8 percent, without the ending. Most chapters have 3-8 areas and 2 bosses.
- **What never gets a card.** A fight in progress, a transformation inside a fight (Goku's Super Saiyan in the Pikkon fight, the Kid Buu phases), the middle of a dungeon, and a Dragon Ball wish inside a chapter.
- **Proof limits.** Bytes prove the card point for ch 1 and 9 (C). For ch 2, 3, 5 and 11 the site is known, but the bytes before the card do not decode cleanly in `bf_chapter_sites.txt`. So "after a fade out" rests on the guide (L). The other 6 sites were not found (trial report).

---

## LoG II section map

Order from g1, checked against the ROM scene tables. Shares are guide lines from one point to the next (C, `placement_guides.txt`; g1 = lines 1-1285, g2 = lines 108-880).

| # | Section | Areas | Main events and fights | Time skip or fade at its start | g1 | g2 |
|---|---|---|---|---|---|---|
| A | Prologue and Trunks | Future (Pepper Town), Goku's house, East District 439, Northern Wastelands | Future Gohan dies; Frieza dream fight; Trunks kills Frieza; Goku returns; Trunks warns Goku | New game | 9.1% | 12.8% |
| B | West City | Goku's house, West City, Capsule Corp, highway, Triceratops Jungle, Warlord's Domain | Scouter, Newman (Wolf), Hercule parade, Triceratops King, Cooler cameo, city key | Fade out 120, map change (flag 26) | 19.8% | 28.5% |
| C | Androids 19 and 20 | Roshi's Island, Amenbo Island, Vegeta's asteroid, Capsule Corp, Southern Continent | 19 and 20 appear; Goku's heart virus; Android 19; Android 20 | "Three years later..." fade out 240 (flag 68) | 12.5% | 12.7% |
| D | Dr. Gero's lab | Northern Mountains, Gero's lab | Gero (20) chase, 3 generators; 16, 17 and 18 wake (flag 125); Android 18 | End of the post-20 scene (flag 86) | 14.1% | 9.4% |
| E | Cell emerges | Lookout, Goku's house, Gingertown, lab, Roshi's Island | Kami says wait; Trunks finds the time machine (flag 129); Kami fusion (flags 133, 132); Cell in Gingertown; lab destroyed; Vegeta and Trunks enter the chamber (flag 144); Android 17; Cell absorbs 17 | Fade out 90, world map (flag 127) | 17.0% | 11.4% |
| F | Perfect Cell | Lookout, Tropical Islands, Capsule Corp | Vegeta and Trunks leave the chamber, Goku and Gohan go in (flag 149); Semi-Perfect Cell; Perfect Cell (flag 150, mid-fight); Trunks vs Perfect Cell; Cell's TV announcement | Fade out 180, Lookout (flag 148) | 10.9% | 7.8% |
| G | Dende and the Dragon Balls | Lookout, 7 Dragon Ball sites, optional Cooler | Goku and Gohan leave the chamber; Dende makes a new dragon; Tao Pai Pai; Dragon Balls back to Dende (flag 191) | Fade out 240, narration caption (flag 154, Continue 158) | 5.8% | 10.6% |
| H | The Cell Games | Cell Games Arena | Goku vs Cell; Gohan vs Cell; 3 Cell Jr; Gohan's rage (flag 194, mid-fight); final Cell | End of the Dende scene (flag 191) | 8.9% | 5.6% |
| I | Ending | Capsule Corp, Lookout or ZZTV | Hercule joins; wishes or the Hercule ending | Fade out 240, Capsule Corp (flag 195) | 1.4% | 0.9% |

**Where the guides disagree (C, quoted lines).**

| Topic | g1 | g2 | ROM |
|---|---|---|---|
| Kami scenes | Kami refuses (XIV, lines 731-735), then fuses after the exoskeleton (line 796) | Not described: "After the conversation between Gohan and Trunks, you get to control Trunks" (line 611) | Agrees with g1: tables `rom:0x3DF71C` and `rom:0x3E0DBC` (C) |
| Cooler | Cameo only, after the Triceratops King: "enter COOLER! ... waiting for him on New Namek" (lines 309-310) | Optional fight after the Dragon Balls: "have to fight Cooler" (line 810) | Not checked |
| Android 18 EXP | Not given | "+ 8,875" (line 591) | `push 8000 ; ext 139` in table `rom:0x3D98A8` seq 1 (C). The other EXP values match g2: 20 = 5000 (`rom:0x3D4874`), Cell = 12000 (`rom:0x3E12EC`), 17 = 15000 (`rom:0x3E4B6C`), Perfect Cell = 40000 (`rom:0x3E7110`) |
| Perfect Cell vs Trunks HP | 5500 (line 1015) | 5,160 (line 721) | Not checked |
| Dragon Ball star numbers | Gingertown = 6-star (lines 1140-1141) | Gingertown = 5-star (line 789) | Not checked |
| After Perfect Cell | Fly to Capsule Corp (line 1040) | Side trip to East District 439 first (line 729) | Not a story difference |
| Tao | "Tao Pai Pai" (line 1131) | "General Tao" (line 770) | Same boss |

---

## Placement test: every candidate

One test for each candidate: where its record sits in the scene table, the fade, the map change and the leader change. "End" = no bytecode record follows before the table's END word. Bytes from `placement_bytes.txt` (C). Shape counts from `placement_flagcheck.txt` (C): one SET and no CLR by shapes A (`00 NN 02 1B`), V (op 1 varint) and L (op 29 list) for every flag below except 133 (CLR at `rom:0x3E0D85`) and 154 (two SET sites).

| Flag | Story point | SET bytes | Fade bytes | Table place | Map, leader | Section start? |
|---|---|---|---|---|---|---|
| 26 | Northern Wastelands scene ends: "Yeah dad, let's head home." | `rom:0x3BFDBF` `00 1A 02 1B` | `rom:0x3BFDBB` `00 78 02 28` (120, before) | End (seq 87) | Map (2,1,1,576,672) | Yes (C) |
| 68 | "Three years later..." | `rom:0x3B8571` `00 44 02 1B` | `rom:0x3B856D` `00 F0 02 28` (240, before) | Mid (caption and Gohan follow) | Map (2,1,2,592,584) | Yes, time skip (C) |
| 86 | Post-20 scene ends: "Alright, let's go find that lab!" | `rom:0x3D542A` `00 56 02 1B` | None near. The scene's fade is at its start: `rom:0x3D4890` `00 78 02 28` (120, right after the fight) | End (seq 46) | None; world map next | Yes, scene end (C); look of a no-fade cut (L) |
| 125 | Lab scene starts; 17 and 18 wake | `rom:0x3D9FDB` `00 7D 02 1B` | None | Start (seq 1, 24 records follow) | None | No: a cut into a cutscene right before the 18 fight (C) |
| 127 | Post-18 scene ends; Piccolo flies to Kami | `rom:0x3D986F` `00 7F 02 1B` | `rom:0x3D9867` `00 5A 02 28` (90, before) | End (seq 48) | World map (6,99), leader Piccolo | Yes (C) |
| 129 | Kami says wait; cut to Trunks | `rom:0x3DF28F` `00 81 02 1B` | `rom:0x3DF293` `00 5A 02 28` (90, after) | Mid (seq 18, 8 records follow) | Map (2,20,1,160,264), music 14 | Yes, but a cut inside one cutscene (C) |
| 133 | Exoskeleton scene cuts to Kami | `rom:0x3E042F` `00 85 02 1B` | `rom:0x3E042B` `00 28 02 28` (40, before) | Mid (seq 11) | Lookout (9,4), leader Piccolo | Cut inside a cutscene; flag cleared later (C) |
| 132 | Fusion ends | `rom:0x3E0D89` `00 84 02 1B` | None (flash) | End (seq 48) | World map (6,99) | After the event it would name (C) |
| 136 | Post-Gingertown-Cell scene ends | `rom:0x3E2480` `00 88 02 1B` | `rom:0x3E244B` `00 5A 02 28` (90, before) | End (seq 57) | Leader Trunks, fade in | Yes (C) |
| 144 | Vegeta and Trunks enter the chamber | `rom:0x3DDDC8` `00 90 02 1B` | `rom:0x3DDDCC` `00 B4 02 28` (180, after) | End (seq 21) | Map (9,3), leader Piccolo | Yes (C) |
| 148 | After Cell absorbs 17; Lookout | `rom:0x3E605A` `00 94 02 1B` | `rom:0x3E5ED7` `00 B4 02 28` (180, seq 86 of the same table) | End (seq 89) | Lookout (9,1,1,736,416) | Yes (C) |
| 149 | Goku and Gohan enter the chamber | `rom:0x3DE69C` `00 95 02 1B` | `rom:0x3DE6A0` `00 B4 02 28` (180, after) | Mid (1 record follows) | Map (9,1), leader Vegeta | Yes (C) |
| 150 | Perfect Cell appears | `rom:0x3E6237` `00 96 02 1B` | None | Inside the fight sequence | None | No (C) |
| 154 | Chamber exit: time skip | `rom:0x3DB4B3` `00 9A 02 1B` | `rom:0x3DB4BB` `00 F0 02 28` (240, after) | Start (seq 0) | Map (1,4), then Lookout (9,1) | Yes, time skip (C); caption (L) |
| 158 | Chamber exit table ends | `rom:0x3DBDAA` `00 9E 02 1B` | None | Seq 31 of the same table | None | Continue flag for 154 (C) |
| 191 | Dragon Balls back to Dende | `rom:0x3DD32B` `00 BF 02 1B` | None | End (seq 6) | None (stays on 9,1) | Yes, scene end (C); look of a no-fade cut (L) |
| 193 | First Cell Games fight | `rom:0x3E8D92` `00 C1 02 1B` | None | After `ext 104` (fight) | None | No: set after the fight starts (C) |
| 195 | After Cell | `rom:0x3EC6A2` `00 C3 02 1B` | `rom:0x3EC67F` `00 F0 02 28` (240, before) | Mid (Hercule joins after) | Capsule Corp (6,3) | Yes (C) |

The chamber exit caption: record [1] of table `rom:0x3DBDD4` is a type 2 text record of 0xCC bytes that is not plain ASCII. g1 quotes a narration at this point: "Goku and Gohan emerge from the rigors of the HTC with newfound power. Using his Instant Transmission, Goku paid a quick visit to New Namek." (lines 1076-1080). So this is LIKELY the caption.

---

## Proposed chapters

Nine cards. Every card plays at a cut between two sections, never inside a fight. Continue reads the flag. A story-point trigger (trial design B: `push N ; ext X` after the fade) goes at the "insert after" bytes.

| New # | Title | Story point (insert after) | Continue flag (SET site) | Why it is a section start | Covers (g1 / g2) | Label |
|---|---|---|---|---|---|---|
| 1 | The Mysterious Youth (keep) | New game | none | Game start, as BF ch 1 | 9.1% / 12.8% | C |
| 2 | Three Years to Prepare (new; your 2026-10-25 placeholder) | Fade 120 `rom:0x3BFDBB`, before SET 26 | 26 (`rom:0x3BFDBF`) | The Trunks scene table ends ("...and so we have three years to train!", "Yeah dad, let's head home."), fade, new map | 19.8% / 28.5% | C |
| 3 | The Androids Appear (keep) | Fade 240 `rom:0x3B856D` | 68 (`rom:0x3B8571`) | Time skip, as you set on 2026-10-25 | 12.5% / 12.7% | C |
| 4 | The Secret of Dr. Gero (old 3; old 4 merged in) | End of the post-20 scene, after SET 86 `rom:0x3D542A` | 86 | Closing cutscene ends ("Alright, let's go find that lab!"); the next play is a new area | 14.1% / 9.4% | C (place), L (look: no fade) |
| 5 | His Name is Cell (old 6's title at old 5's point) | Fade 90 `rom:0x3D9867` | 127 (`rom:0x3D986F`) | Post-18 scene ends; world map; leader Piccolo. The section's main fight is Cell | 17.0% / 11.4% | C |
| 6 | Bow to the Prince (keep) | Fade 180 `rom:0x3E5ED7` (Roshi's Island to the Lookout) | 148 (`rom:0x3E605A`) | Cell absorbs 17, Goku teleports out, fade, new place. Vegeta's chamber reveal opens the chapter | 10.9% / 7.8% | C |
| 7 | A New Guardian, or The Dragon Balls (old 8, retitled) | Fade 240 `rom:0x3DB4BB` | 158 (`rom:0x3DBDAA`) | Time skip with a caption, after Cell's TV announcement | 5.8% / 10.6% | C (bytes), L (caption) |
| 8 | The Cell Games (keep) | End of the Dende scene, after SET 191 `rom:0x3DD32B` | 191 | Closing cutscene ends; next goal is the arena. BF ch 11 also leaves free training after its card | 8.9% / 5.6% | C (place), L (look: no fade) |
| 9 | The Champion's Hour (keep) | Fade 240 `rom:0x3EC67F` | 195 (`rom:0x3EC6A2`) | After Cell; new map. The ending card, as BF ch 12 | 1.4% / 0.9% | C |

Flags rise in table order (26, 68, 86, 127, 148, 158, 191, 195), as the module requires. The story order is g1's order and the ROM tables' order (L: no save from every point was tested).

**Old to new.**

| Old (module today) | New |
|---|---|
| 1 The Mysterious Youth | 1 |
| none | 2 Three Years to Prepare (new) |
| 2 The Androids Appear | 3 |
| 3 The Secret of Dr. Gero | 4 |
| 4 Nightmare Comes True (125) | Dropped, merged into 4 |
| 5 Birth of a Namekian (127) | 5: same point, title "His Name is Cell" (or keep "Birth of a Namekian") |
| 6 His Name is Cell (129) | Dropped, merged into 5 |
| 7 Bow to the Prince | 6 |
| 8 Room of Spirit and Time (158) | 7, retitled |
| 9 The Cell Games | 8 |
| 10 The Champion's Hour | 9 |

**Your notes, one by one.**

- **"Cannot place title cards ... in the middle of fights."** No proposed card is inside a fight. Card 5 at 127 and card 6 at 148 come after a fight's closing cutscene and a fade (C, table ends and fade bytes above).
- **"The 3-year jump means the next card is The Androids Appear."** Kept at flag 68 (C).
- **"There would not be a 12."** No card at Gohan's rage (flag 194 is set inside the fight, `rom:0x3E9BBB`) (C).
- **"Room of Spirit and Time after Goku and Gohan leave the chamber, but the chamber is long gone at this point."** Agreed. After the exit the play is Dende, the new dragon and the Dragon Ball hunt. So keep the card at that time skip (one of the cleanest cuts in the game) and rename it. If you want the chamber title, the only clean chamber cut that is not taken is flag 144 (Vegeta and Trunks go in). See "Option" below.
- **"3 and 4 are basically back to back."** Measured, cards 3 and 4 are 11.4 percent apart in g1 and 6.9 percent in g2 (C). That is not back to back by guide lines. But card 4 (125) is a cut into the lab cutscene, with no fade, right before the 18 fight. Cards 4, 5 and 6 (125, 127, 129) all sit within g1 lines 684-737, which is 4 percent of g1 (C). One story beat, the hunt for Gero's lab, runs from 86 to 127. So: merge 3 and 4 at 86, and merge 5 and 6 at 127.
- **"Buu's Fury has proper chapter spacing."** Proposed shares, without the ending: g1 5.8-19.8 percent, g2 5.6-28.5 percent. BF: 3.7-23.8 percent (C). Card 2 in g2 is above BF's largest chapter. g2 spends many lines on the West City side quests. I found no clean story cut inside that section (one flag sweep, see "Points with no clean flag").

**Alternative (close call): card 5 at flag 129 instead of 127.**

| | 127 (proposed) | 129 (alternative) |
|---|---|---|
| Cut | Table end, fade 90, world map, leader Piccolo | Mid-table cut, fade 90, map 2,20, music 14; the cutscene goes on with Trunks |
| Card 4 covers | Northern Mountains, lab, 18 fight | The same plus one Lookout visit (1.4 percent of g1) |
| Title fit | Section opens with Piccolo's trip to Kami, then Cell | Section opens with Trunks and the time machine, then Cell |

I recommend 127, because BF cards sit at the end of a closing cutscene (BF ch 3 and 11: the card is the last op of its record), and 127 is a table end.

**Option (10th card): "Room of Spirit and Time" at flag 144.** Story point: fade 180 `rom:0x3DDDCC` after SET 144 `rom:0x3DDDC8`, table end, leader Piccolo (C). It covers Piccolo vs 17 and Cell absorbing 17: g1 4.2 percent, g2 2.7 percent. That is as short as BF ch 7 (4.0) and ch 11 (3.7). You called a 7-11 percent gap "back to back", so I expect this one to feel too close (S). Card 5 then shrinks to g1 12.8 percent.

---

## Points with no clean flag

| Point | Why not clean | What finding one would take | Label |
|---|---|---|---|
| Perfection (Perfect Cell) | Flag 150 is set inside the fight sequence (`rom:0x3E6237`); 151 is set in the post-fight table (`rom:0x3E7766`) | No section start exists there: Semi-Perfect Cell, the absorption of 18, Perfect Cell and the Trunks fight form one chain. Drop it, as the trial did | C |
| Kami fusion as its own card | 133 is set at the cut to Kami (fade 40, `rom:0x3E042F`) but cleared at `rom:0x3E0D85`. 132 is set after the fusion (`rom:0x3E0D89`) | A story-point trigger at the 133 fade, with Continue reading 132. No save point is inside one cutscene (L). It would make a short chapter after 129 (5 percent of g1), so I do not propose it | C (bytes), L (save) |
| Arena arrival | The arena entry table (`rom:0x3E8D98`, seq 0 `rom:0x3E8610`) sets no flag before the fight. 193 is set after `ext 104` (`rom:0x3E8D92`) | A story-point trigger (design B) needs no flag. For Continue: the arena visited bits 294-296 (bible SAV row) could mark it, but the module only reads story flags in rising order. A new flag is not allowed (save format fixed). Using an unused existing flag bit needs proof that no code reads it (S) | C |
| Gohan's Fury | 194 is set inside the fight (`rom:0x3E9BBB`) | None. You ruled it out | C |
| A cut inside West City (new card 2) | In the SET sweep (`placement_sites.txt`) only two West City quest steps load a map, and neither has a fade: 29 (`rom:0x3B9041`, leave home for the world map) and 66 (`rom:0x3C6A97`, city key returned, map 4,3). Flag 58 (`rom:0x3CD545`, after Piccolo reports the Triceratops King) has no fade or map load | A walk of every West City scene table for a fade at a story turn. Not done. A cut written without a flag SET would not appear in my sweep | C (the three sites), S (no other cut exists) |
| Card 4 and card 8 starts | Each scene ends with no fade (86, 191). The player stays on the same map | None for the flag. The card's own fade in hides the cut (L). An emulator check decides | L |

---

## Corrections to earlier work

| Earlier claim | Correction | Label |
|---|---|---|
| Trial report and CHC bible row: "LoG II order puts the Kami fusion (flag 127) before the Cell reveal (flag 129)" | Flag 127 is set when the post-18 scene ends (table `rom:0x3D98A8`: EXP 8000, Piccolo flies off, "I bet he's going to Kami's Lookout!", fade 90, SET 127). Table `rom:0x3DF71C` opens with "KAMI: Piccolo. You've returned." and sets 129 at seq 18. The fusion ("No longer am I Kami or Piccolo...") is table `rom:0x3E0DBC`, after the exoskeleton. LoG II keeps the anime order | C |
| Trial report: "flag 132 at `rom:0x3E0D62` (Gingertown)" | `rom:0x3E0D62` is the record start. The SET is `rom:0x3E0D89`, at the end of the fusion. Piccolo then flies to Gingertown | C |
| Trial report: flag 86 record [0] decode "ext 28 CLR ..." | The study decoders start type 0 bytecode at record +4. It starts at +3, after `{u16 next, u8 type}`. Record `rom:0x3D4874` is `01 00 00 | 1D 02 1C 06 02 39` = push (14,3) ; ext 57, not a CLR. A first push `00 VV` shows as `opVV` | C |
| Module comment on row 3: "after the Android 19 fight" | The fight before flag 86 is Android 20 (EXP 5000 at `rom:0x3D4874`, `01 CE 10 02 8B`; g2 "EXP: +5,000" for Android 20, line 522) | C |

---

## Open questions for me

1. Take the 9-card table? Or add the 10th card "Room of Spirit and Time" at flag 144?
2. Card 2 "Three Years to Prepare" at flag 26: yes or no? Without it, chapter 1 runs to the 3-year skip (29 percent of g1).
3. Card 5 title: "His Name is Cell" (names the boss, the BF way) or "Birth of a Namekian"? Card 5 point: 127 (recommended) or 129?
4. Card 7 title (old card 8): "A New Guardian", "The Dragon Balls", or your own?
5. Cards 3 and 4: merge at 86 as "The Secret of Dr. Gero" (recommended)? Or keep only 125 as "Nightmare Comes True"? Then card 3 "The Androids Appear" runs 68-125 (about 24 percent of g1).

---

## Files

- `scripts\one-time\2026-10-25-chapter-cards\placement_sites.py` and `.txt`: every SET and CLR site of flags 0-200 in ROM order.
- `placement_probe.py`: record and scene table decoder (wraps the earlier tools). Outputs `placement_probe_ch1_split.txt`, `placement_probe_sites.txt`.
- `placement_bytes.py` and `.txt`: raw bytes, fades and table place for each candidate.
- `placement_flagcheck.py` and `.txt`: SET and CLR counts by three shapes.
- `placement_guides.py` and `.txt`: guide shares, areas and bosses for BF and both LoG II guides (run with `-I`).
- `bible_rows_placement.md`: rows tagged CHP.
