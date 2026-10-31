# Portrait remaster study: report (2026-10-18)

Labels: **CONFIRMED** = proved here with data or a script result. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

Scope: my corrections of 6:44 PM and 6:50 PM apply.
- The example is a recolor and reshade of the same drawing.
- The example is a compressed JPEG.

I kept every outline and drawing pixel. I read the example for intent only.

---

## Verdict

**Yes, if** we accept a color and shading pass rather than a match of the example's busier hair.

- Version A uses only colors that the OBJ palette already holds. It gets the skin and shadow look with zero palette risk, but its hair shine is thinner than the example's.
- Version B adds 6 colors in OBJ palette slots that no portrait or sprite uses. B also gets a darker line and a cleaner skin ramp.
- The status twin of A comes free from the game's own pairing map. B needs status palette slots too, or its status twin falls back to the nearest colors.

---

## 1. The Goku portrait

- **CONFIRMED:** The OLD panel is dialog portrait **id 63** (base Goku). The panel sits at (25,38) in the example at 1x, frame included. Mean RGB error is 15.2 for id 63, 44.1 for the runner-up id 64 (Goku with halo), and 77 or more at any 1 px offset (`scripts\one-time\2026-10-19-portrait-from-anime\s1_find.py`).
- **CONFIRMED:** 3837 of 4096 OLD panel pixels match the ROM index exactly by nearest color. The rest are JPEG edge bleed (`s2_study.py`).
- Appearance entry 19 (set 60) gives +2 = 63 and +3 = 14. Unpacked: `art\portrait-sources\remaster\old_goku_63.png` (64x64 indexed, OBJ palette `rom:0x1DA6C8`, 23 colors).

---

## 2. What changed in the example (no pixels taken)

**Method:** The same JPEG compressed both panels. For each ROM index, I compared its mean color in the OLD panel against the REMASTERD panel. The OLD panel reproduces the ROM colors within about 5 per channel, so a large shift in REMASTERD is a real edit, not compression.

| Change | Kind | Evidence | Label |
|---|---|---|---|
| Hair: grey rims and streaks inside the black mass. They follow the clump contours: around the bangs, along the right silhouette, short strokes in the upper-left mass, and wisps at the right. Hair interior pixels average (1,1,2) in OLD and (17,17,18) in REMASTERD | Added shade boundary | About 400 of 1639 black pixels are now grey, at about 2 levels near (50,50,50) and (75,75,75), with a few near (140,140,140) | CONFIRMED (rims exist), LIKELY (levels) |
| Hair edge against the background: some outer hair pixels look grey, not black | Color swap of outline pixels | Blurred by the JPEG at those edges | SPECULATIVE |
| Skin hue: pink to peach and tan. Old light 114 (248,184,168) becomes about (246,219,175). Old mid 115 (224,152,128) becomes about (218,149,110) | Color swap, same pixels | Large flat areas, interior pixels only | CONFIRMED |
| Skin shade count: OLD has 3 (114, 115, 116). REMASTERD has about 4-5: a lit peach, a second lighter peach, a mid tan, a shadow tan, and a deep tone near the ear and jaw | Partly a swap, partly added boundaries | Old 114 splits into two peaches, and old 115 into two tans | LIKELY (count) |
| Under-eye band: rows 38-39 under both eyes become a hard mid shadow. Row 38 x 28-36 is lit index 114 in the ROM. In REMASTERD it measures luminance 150-180, against 205-220 for its own lit rows 40-44 | Moved shade boundary | Per-pixel luminance table in my run | CONFIRMED |
| Lit face, right side and neck: the old lit/shadow split at about x 35 stays. The right side reads tan, darker toward the ear and jaw | Mostly a swap, small boundary moves | Means per index | LIKELY |
| Line color: brown 113 (104,48,16) becomes a darker brown, most pixels near (72-95, 24-47, 0-23) | Color swap, same pixels | 113 measures (105,47,19) in OLD | CONFIRMED (darker), LIKELY (exact value) |
| Eyes: the four iris greys 15 (64,64,64) become black. The whites are unchanged | Color swap, same pixels | 4 px: (66,60,67) to (20,20,22) | CONFIRMED |
| Gi orange: a few 33 pixels look brighter | Swap or highlight | 39 px, edge pixels | SPECULATIVE |
| Mid-tone texture: the cheek and chest show a checker texture | Dither or JPEG blocks | Cannot separate from 8x8 JPEG blocks | SPECULATIVE |
| Frame and background | Unchanged | Equal within noise | CONFIRMED |

**Intended palette, as I read it:** black hair plus 2 greys (OBJ 15 (64,64,64), 14 (88,88,88), maybe 13), 4-5 skin tones, a darker line brown, and black irises. The literal color count is about 74 clusters, which is JPEG noise. I do not report it as a count.

**Colors that exist in the OBJ palette:**
- Lit peach: 16 (240,216,168).
- Shadow tan: 116 (200,128,96).
- Deep tan: 117 (176,96,56).
- Hair greys: 13, 14 and 15.

**Colors that do not exist in the OBJ palette:**
- A second light peach, about (240,192,144). The nearest is pink 114.
- A mid tan, about (216,144,104). The nearest are 115 and 116.
- A brown darker than 113.

---

## 3. References (`art\portrait-sources\remaster\refs\`, data only, nothing run)

| File | Source URL | What it shows and what I took |
|---|---|---|
| `r1_kanzenshuu_goku_color_design.png` | https://i.imgur.com/G9nzriM.png (posted in https://www.kanzenshuu.com/forum/viewtopic.php?p=1751634) | Fan **reconstruction** (user lansing) of Goku's anime color design sheet. It is not a Toei original. Skin X-20 (255,215,202), shadow R-2 (226,151,137), deep R-3 (191,117,103), hair BL (16,25,28). Took: the anime skin has 3 tones and is pinker than the example's tan |
| `r2_kanzenshuu_cellgame_goku.png` | https://i.imgur.com/DwaWzni.png (https://www.kanzenshuu.com/forum/viewtopic.php?p=1757900) | Clean Cell Games screenshot. **Super Saiyan**, not base. Took: one hard shadow tone on the face and neck, and a cast shadow under the jaw |
| `r3_kanzenshuu_venny_compare.jpg` | https://i.imgur.com/c0VYQsV.jpg (https://www.kanzenshuu.com/forum/viewtopic.php?p=1751634) | Base Goku face, Movie 7 frame "matched to cel". Lit skin about (248,208,200), shadow about (224,144,136), hair (16,24,32). Took: shadow under the bangs, on the far side of the face and under the jaw. Anime base hair has no grey shine |
| `r4_fandom_vegeta_bulma_ep124.webp` | https://static.wikia.nocookie.net/dragonball/images/e/e8/VegetaBulmaEp124.png/revision/latest?cb=20101018171245 | Episode 124 screenshot, Vegeta in bed. **Weak face reference** (small, bandaged). Took nothing useful |
| `r5_fandom_vegeta_original_armor.webp` | https://static.wikia.nocookie.net/dragonball/images/5/57/Vegeta_Original_Armor.png/revision/latest?cb=20260203002135 | Clean full-body anime screenshot of base Vegeta in Saiyan armor. Took: peach skin, one shadow tone under the jaw and on the face side, blue-black hair (about (32,24,40)) |

- Downloads r4 and r5 were WEBP served with a .png name. I renamed them to .webp.
- No official Toei model sheet for Vegeta was found. The Dragon Ball fandom wiki pages return HTTP 402 to WebFetch, so I used its file API to find the image URLs.

---

## 4. Our attempt (`art\portrait-sources\remaster\`)

| File | What |
|---|---|
| `goku_A.png` | Version A, OBJ palette as in the ROM. 22 colors. Skin: H 44, L 16, M 116, S 117, D 21. Hair rims 13 and 14. Line 113 kept |
| `goku_B.png` | Version B. New colors in free slots (listed below). Skin: H 59, L 16, l 60, M 62, S 82, D 83. Hair rims 13 and 14. Line 86 |
| `goku_A_status.png`, `goku_B_status.png` | Status twins (menu palette `rom:0x1D4F50`) through the game pairing map |
| `compare_goku.png` | 4x on lime: OLD (ROM) / example REMASTERD / ours A / ours B |

**B's new colors (6 of the allowed 8):** slot 59 (248,232,200) highlight, 60 (240,192,144) lit 2, 62 (216,144,104) mid, 82 (184,112,80) shadow, 83 (152,88,56) deep, 86 (72,32,8) line.

**Method, stated honestly:**
- Skin: typed by hand per pixel, as per-row runs in `scripts\one-time\2026-10-19-portrait-from-anime\s7_paint.py` (`SKIN`).
  - The script checks that each run starts where the ROM's skin run starts and has the same length.
  - So no skin pixel moves into or out of a line.
  - Letters: H, L, l, M, S, D. Each version maps letters to indices.
- Hair: a distance brush inside 5 hand-chosen boxes (`RIMS`) plus 8 hand strokes (`STREAKS`).
  - The brush paints black pixels at distance 2 (and in some boxes 3) from the skin or the background.
  - This is region-limited, not a global rule.
- Line in B: one palette-level swap of all 196 pixels of 113 to 86. The brief says "no global color rule", but my correction names line color. So I call this out as the one global swap.
- Eyes: the four 15 pixels go to 1 (both versions).
- Checks in the script: no pixel changes outside skin, hair interior, the eye list and (B) the line. A black pixel that touches a non-black pixel never changes. The script stops on any failure.
- Edits: A changes 1121 px, B changes 1318 px (B adds the 196 line pixels).

**Swap or moved boundary, in our versions (CONFIRMED, counted from `s7_paint.py`):**
- Skin: 129 of 899 skin pixels moved shade class by hand: 39 L to l, 33 M to S, 26 L to H, 13 L to M, 8 M to l, 6 S to D and 4 others. The other 770 keep their old class and change by a class-to-color swap. In A, l maps to 16 like L, so the 39 L to l pixels show only in B.
- Hair: all 219 grey pixels are added shade boundaries inside the black mass.
- Eyes (4 px) and the B line (196 px): color swaps of the same pixels.

**How close (looked at `compare_goku.png` and at 7x):**

- **A: about 65 % of the look. LIKELY, my judgment.**
  - Skin hue and the right-side tan match well.
  - The hard under-eye band and the cast shadow under the chin match the intent.
  - The highlight 44 is a cream with a slight yellow cast on the bang strips. It reads as shine, but it is less warm than the example.
  - The line stays the old brown.
- **B: about 75 %. LIKELY, my judgment.**
  - Its skin ramp is cleaner and closer to the example's peach and tan.
  - The darker line gives the face more weight.
- **Still missing in both:**
  1. **Hair shine.** The example's grey is wider and brighter, and it covers more strands, mainly across the bang fronts and in big strokes in the upper-left and right mass. Ours is a 1-2 px rim. This is the biggest visible gap. It is fixable by hand with more strokes and level 12 (144,144,144) accents.
  2. **Grey hair edges against the sky.** The example may grey some outer hair pixels. I kept them black under my "keep every outline" rule. SPECULATIVE that the example does it.
  3. **Texture in the mid-tones.** The example looks dithered on the cheek and chest. That may be JPEG blocks, so I did not copy it.
  4. **Face against the background.** Peach skin 16 is the same color as the background tan 16 on the left. The face separates only by its brown line. The example has the same issue.

---

## 5. Palette audit

**Free OBJ slots: 37. LIKELY.** These are indices that no dialog portrait and no sprite record uses:
3, 7, 53, 59, 60, 62, 82, 83, 86, 87, 93, 94, 102, 103, 108, 126, 127, 145, 147, 148, 151, 157, 162, 164, 172, 173, 174, 175, 177, 178, 179, 180, 201, 216, 218, 235, 246.

They are greens, purples and pure blues. None is a skin tone, so every new color overwrites an unused entry.

**How I checked (`s4_palette_audit.py`, `s5_palette_records.py`):**

| Shape | What it reads | Used | Free |
|---|---|---|---|
| A | Dialog portraits ids 26-114 | 183 | 73 |
| B | All 150 sprite sets: 7673 (frame, remap) pairs, 1755 through a set's remap table, 0 failures | 189 | 67 |
| A+B | | 219 | 37 |
| D | Every 12-byte OBJ frame record in the whole ROM (5918 frame headers, also effects outside the set table) | adds 0 | 37 |
| C | Every frame in the ROM (13174) | 256 | 0, useless: it includes BG art on other palettes |

**Why LIKELY, not CONFIRMED:**
- Runtime writes to OBJ palette RAM exist. `@0x08005F42` DMAs a RAM buffer to `0x05000200` (source not traced). `@0x0800DA84` backs up the OBJ palette, and `@0x0800DB06` and `@0x0800DB9C` write 512 bytes back (LIKELY a fade). Index 168 is set at run time.
- OBJ graphics without a frame record (dialog box, cursor, font, HUD) are not in shapes A, B or D.

**Loaders:** The ROM palette `rom:0x1DA6C8` is loaded by 5 sites (`@0x080005D0`, `@0x08009BE4`, `@0x0801105A`, `@0x0801772C`, `@0x08019AE8`). The two I read in full DMA 0x100 halfwords (512 bytes). So an in-place edit reaches every scene that loads this palette. CONFIRMED for those two sites, LIKELY for the other three.

**What version B needs:**

| Option | Size | Notes |
|---|---|---|
| 1. Write B's colors into free OBJ slots in place | 12 bytes (6 halfwords at `rom:0x1DA6C8` + 2 x slot), no code | Simplest. Skin colors can be shared by the whole cast, so Goku, Vegeta and Gohan together still need about 6-8 of the 37 slots. Risk: a graphic that none of the 3 shapes sees uses a slot |
| 2. Swap entries only while the dialog box is open | About 0x40-0x80 bytes of hook code, plus 12 bytes per portrait palette (SPECULATIVE size) | In 8bpp OBJ mode there is only one OBJ palette, so a "separate portrait palette" means swapping entries at the upload (`@0x0800BB3E`) and restoring at box close. The fade routine at `@0x0800DA84`/`@0x0800DB06` backs up and rewrites palette RAM, so it can undo or keep the swap. Needs tracing |
| 3. 4bpp portraits | Large: new code path | Does not add colors: 4bpp banks are slices of the same 256-entry palette, and a portrait uses 22-35 colors |

**Status twin for A: free to make, but it does not keep A's look exactly (CONFIRMED, `s9_status.txt`).**
- The game pairs 116 with status 33 (208,104,72), RGB error 35, on 422 px. So the right side of the A status twin is visibly redder (`scripts\one-time\2026-10-19-portrait-from-anime\view_status.png`).
- 117 and 21 both pair with status 32, so S and D become one shade on the status screen.

**Status twin for B:**
- The status screen uses the menu BG palette `rom:0x1D4F50`.
- Through the game pairing, A has a real pair for all 22 of its indices. B has 18 real pairs, and its 6 new colors fall back to the nearest status color (RGB error 16-43; the line becomes (112,48,8)).
- To keep B on the status screen, B also needs about 5 status slots. Status index 22 is already (248,232,200), equal to B's highlight.
- In a narrow check, status portraits plus two menu frames use 94 status indices. The menu font, icons and other menu art are not enumerated, so any "free" status slot is SPECULATIVE.

**Storage (from the bible):** Each new or replaced portrait is a raw type 0 frame of 4 KB + 8 bytes for the dialog, and the same for the status twin. The table is already relocated by `gohan_portraits`.

---

## 6. Plan for base Vegeta

**Ids (CONFIRMED from the appearance table):**
- Entries 8 and 9 (sets 137, 138): dialog **106**, status **24**.
- Entries 10 and 11 (Super Saiyan, sets 139, 140): dialog **107**, status **25**.

No other Vegeta dialog portrait is in ids 26-114 by eye (`scripts\one-time\2026-10-19-portrait-from-anime\dialog_ids_sheet.png`).

**Status twin: yes, by the existing pairing map.**
- The pairing map reproduces the vanilla status portraits: Goku 63 to 14 at 4096/4096, Vegeta 106 to 24 at 4087/4096 (index 90 has no pair and falls to nearest), and 107 to 25 at 4093/4096. CONFIRMED.
- Every color I would use for a Vegeta version A has a real game pair: 16, 17, 18, 19, 20, 21, 113, 211, 215, 13, 14, 15, 116, 117. CONFIRMED.
- Caveat: 20, 21 and 117 all pair with status 32, so the deepest Vegeta shades merge on the status screen. Pick one of them for the dialog art.

**Starting point is better than Goku's:**
- Portrait 106 already uses the peach ramp 16 (240,216,168) and 17 (240,192,112), with 19 (192,144,80) for dark shadow.
- It also uses 211 (32,32,64) and 215 (32,32,120). LIKELY: 211 is the blue-black hair shading and 215 is the suit.

So the Vegeta pass is mostly shading shapes, hair shine, line and eyes, not a hue change.

**Effort (from the Goku run):**

| Portrait | Effort | Notes |
|---|---|---|
| 106 dialog (base), version A | About 1-2 hours of task time | About 42 rows of hand runs, hair boxes and strokes, then 3-4 render and look rounds |
| 24 status | Minutes | Generated by the pairing map. Look at it once |
| 106 version B | About +15 min | Shares B's skin slots with Goku. Needs the status slot decision of section 5 |
| 107 / 25 (Super Saiyan, optional) | About 1-2 hours | Gold hair needs its own shine rules |

**Recommendation:**
1. Next, do Vegeta 106 as version A.
2. Spend the extra time on the hair shine, which is the gap that remains on Goku.
3. Choose between A and B for the whole cast after I see both in game.

---

## 7. Concerns

- B's new indices break the current portrait rule in `gohan_portraits` and its tests: "dialog art uses only OBJ indices that USA dialog portraits use". Adopting B means changing that rule. Changing it needs a final decision.
- The free slot count is LIKELY only. An unseen OBJ graphic that uses one of B's slots would change color in game. An in-game check of the menus, the dialog box and the effects is needed before B ships.
- The example is another artist's work. No pixel of it is in our art: `s7_paint.py` never opens it. Its panel appears only as a column of `compare_goku.png`. I deleted my study crops of it from `scripts\one-time\2026-10-19-portrait-from-anime\`.
- The hair shine is the main gap. More hand strokes will close part of it. Matching the example's density is a judgment call, because the anime references (r1, r3, r5) show no grey shine on black hair.
- No in-game test was done. No ROM was built. Nothing outside my two folders was written. Later imports of `scripts\permanent` ran with `-B` (no bytecode written there). About five early runs (s1, s2, two inline checks, s4 and s5) ran without `-B`. They imported only `webfoot_decompress`, whose cache there dates from 2026-10-17 and did not change, so they wrote nothing new.
- Process slip: one cleanup Bash call started with `cd /`, against the "never cd" rule. It changed nothing.

---

## Files

- Art: `art\portrait-sources\remaster\` (`old_goku_63.png`, `goku_A.png`, `goku_B.png`, the two `_status.png` files, `compare_goku.png`, `refs\`).
- Scripts and logs: `scripts\one-time\2026-10-19-portrait-from-anime\`.

| Script | Purpose |
|---|---|
| `s1_find.py` | Match the OLD panel to an id |
| `s2_study.py` | Cluster and index study |
| `s4_palette_audit.py`, `s5_palette_records.py` | Palette audit |
| `s6_template.py` | Template of portrait 63 |
| `s7_paint.py` | The repaint |
| `s8_view.py` | Working view |
| `s9_status.py` | Status twins, ids, loaders |
| `s10_compare.py` | Compare sheet |
