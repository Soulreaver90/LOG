# Bible rows from the ending fight play test, 2026-11-05

Merge into `docs\RE-BIBLE.md`. Tag: `ESS`.
Source: two mGBA save states the owner took either side of the hang,
`builds\mockups\2026-11-05-ending-fight-1\log2_poc_r41_endingfight.ss1` and `.ss2`, read with
`scripts\permanent\rom\state_dump.py`. State 1 is the frame before the "THE NIGHTMARE IS OVER CELL"
line. State 2 is the hang after record F runs.

## Section 8

| Fact | Tags | Label | Tag |
|---|---|---|---|
| `ext 33 (0)` really does follow the player, and it DISCARDS a fixed camera. `[0x03000FF4]` holds `0x030020C8` (the fixed camera, set by the cutscene's `ext 31` at `rom:0x3B7B8F`) before record F, and `0x030020F4` (a follow object) after it. So any record that ends with `ext 33 (0)` throws away the framing a cutscene set, even when every actor is in the right place. This confirms the EF1 row on the camera object pointer by measurement rather than disassembly | #script #combat | C (two save states) | ESS |
| `ext 62 (0, x, y)` does move the player, and `ext 104 (set, item)` does build the map item as a live enemy. After record F the OAM holds a 16x32 object at screen (112,112) and a 64x64 at screen (88,16) with the camera at x 136, so Trunks stands at map x 248 and Cell's feet sit exactly 64 rows above his, matching the intended (248,568) and (244,504). A scene that looks broken is not proof that its actor ops failed | #script #combat set:28 set:128 | C (OAM and BG scroll) | ESS |
| Ending table word 13 `rom:0x3B7E4A` runs `load_map(zone=6, area=1, var=1, x=136, y=432)`, so the player stands at (136,432) for the whole Cell scene while NPC set 133 walks to (248,568) and word 15 walks set 28 to (244,504). Every camera op in the ending names set 132 or 133, never actor 0. The player takes no part in the vanilla scene | #story #script set:28 set:133 | C (decoded table) | ESS |

## Section 9

| Fact | Tags | Label | Tag |
|---|---|---|---|
| Map 6,1 during the ending blends at two different strengths, and the second one hides the game. `BLDCNT 0x1E41` makes BG0 the first blend target and BG1, BG2, BG3 **and OBJ** the second. While the cutscene runs, `DISPCNT 0x1E40` leaves BG0 OFF and `BLDALPHA 0x0C09` gives EVA 9, EVB 12. When the scene ends and the map resumes, `DISPCNT 0x1F40` turns BG0 ON and `BLDALPHA` becomes `0x1010`, EVA 16 and EVB 16, which is full strength on every target including the sprites. The screen washes out to pale bands and both fighters become invisible although they are correctly placed | #map #script | C (two save states) | ESS |

## Section 11

| Fact | Tags | Label | Tag |
|---|---|---|---|
| An actor's MAP position can be read from an mGBA save state with no knowledge of the actor table. `state_dump.py` writes `oam.bin` and `io.bin`; OAM carries each sprite's screen position and size, and BG1, BG2 and BG3 HOFS carry the camera x. Map x = screen x + HOFS. The VOFS values disagree between layers, so absolute y is not safe, but the y DIFFERENCE between two sprites is exact and can be matched against two known spots. This settled the ending fight after three wrong readings taken from the screenshot alone | #tool #debug | C (used 2026-11-05) | ESS |
| A coordinate that matches a known value may still be a coincidence. The camera x after record F was 136, which equals the `load_map` x in ending word 13, and I twice reported that as proof the camera had jumped to the player's load position. It is simply the camera x that centres an actor standing at 248 on a 240 wide screen. Check the sprite against the camera before concluding that either one moved | #tool #debug | C | ESS |
