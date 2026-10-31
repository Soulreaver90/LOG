# Portrait remaster: Gohan Super Saiyan, Super Saiyan 2 and base gi (2026-10-18)

Labels: **CONFIRMED** = proved here with data or a script check. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

Brief: `docs\tasks\2026-10-18-portrait-gohan\portrait-gohan.md`. Version A only: existing OBJ palette colors, no palette change. No ROM build, no patch. I wrote files only in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`.

---

## Compare sheet

`art\portrait-sources\remaster\compare_gohan.png`: 4x on lime (191, 255, 7). One row per form (Super Saiyan 115, Super Saiyan 2 117, base gi 119). Columns: OLD (r16) | ours A | status twin of A. Goku A v2 sits in the top right corner as the style reference. Made by `scripts\one-time\2026-10-19-portrait-from-anime\h9_compare.py`.

---

## 1. Gohan dialog portrait ids in r16

Read from `archive\builds\log2_poc_r16.gba` by `h1_unpack.py` (log `gohan_census.txt`). Portrait block `rom:0x894EAC`, 122 words (ids 0-121). Appearance table `rom:0x88DC54`. **CONFIRMED** (bytes).

| Id | What | Appearance entry (+2 / +3) | Made by this hack |
|---|---|---|---|
| 56 | Kid, Demon clothes | 0 (56 / 8) | No |
| 57 | Future Gohan (cutscenes only) | none | No |
| 58 | Kid, blue shirt | 1 (58 / 9) | No |
| 59 | Teen armor, base | none in r16 (vanilla entry 2); cutscene raw id | No |
| 60 | Armor variant | 3 (60 / 11) | No |
| 61 | Rage, armor | 4 (61 / 12); entry 4 now uses gi `set:160` | No |
| 62 | Super Saiyan, armor | none in r16 (vanilla entry 5) | No |
| **115** | **gi Super Saiyan dialog** | 5 (115 / 116) | Yes: sheet `122601.png` row 1 column 4 |
| **117** | **gi Super Saiyan 2 dialog** | 22 (117 / 118) | Yes: sheet row 1 column 5 |
| **119** | **gi base dialog** | 2 (119 / 120) | Yes: approved drawing `gi_base_dialog_src.png` |
| 116, 118, 120 | Status twins of 115, 117, 119 | | Yes: made by the pairing map |
| 121 | Copy of armor 59 (chamber exit, `npc_gi`) | none | Yes: pixels equal USA id 59 |

- **CONFIRMED:** 115-120 equal `art\portrait-sources\gi_*_{dialog,status}.png` byte for byte. Ids below 115 equal the USA ROM.
- **CONFIRMED (bytes), LIKELY (in game):** while Gohan is in entry 4 (gi Rage), the `cutscene_portraits` hook maps 61 to 117. So the Super Saiyan 2 repaint is also the gi Rage dialog portrait.
  - The hook is `rom:0x894E74`-`0x894EAB` in r16.
  - It holds `cmp r0,#0x3D` and `cmp r3,#4`, then `mov r0,#0x75`.
  - It also maps 59 to 119 and 62 to 115, for entries 2, 5 and 22.
  - Its pool word is `0x08894EAC`, the r16 block.
- Unpacked (indexed, OBJ palette): `old_gohan_56.png` to `old_gohan_62.png`, `old_gohan_115.png`, `old_gohan_117.png`, `old_gohan_119.png`. Shipped status twins: `old_gohan_116_status.png`, `old_gohan_118_status.png`, `old_gohan_120_status.png`.

---

## 2. Why 115 and 117 look flat

**Cause: the source art, not a remap. CONFIRMED.**
- `h4_flat.py` compares the sheet cell with the shipped dialog colors on every skin, hair and line pixel. 115: 2543 pixels, 0 differ. 117: 2201 pixels, 0 differ.
- The per-form recolor in `gohan_portraits.py` (`{96: 97}`, `{80: 233, 215: 97}`) touches only gi indices (108 and 499 px).
- So the International sheet cells are copied faithfully. The flat look is in those drawings.

**What is flat (CONFIRMED, `h4_flat.txt`):**

| Portrait | Skin shades | Largest skin class | Skin luminance range | Skin spread (sd) | Hair shades |
|---|---|---|---|---|---|
| Goku 63 vanilla | 3 (114, 115, 116) | 115, 51 % | 55 | 17.8 | |
| **Goku A v2 (target)** | 4 (44, 16, 116, 117) | 116, 48 % | **125** | **40.2** | |
| Gohan 59 / 62 vanilla | 3 | 114 (lit), 44-50 % | 55 | 18-20 | 62: 43, 44, 128, 133 (range 96) |
| **Gohan 115 (hack)** | 3, the third only 8 % | **115 mid, 63 %** | 55 | 16.4 | 43, 45, 38 (range 65) |
| **Gohan 117 (hack)** | 2 real (116 1 %, 117 2 %) | **115 mid, 55 %** | 86 (the 2 % accent) | 17.9 | 43, 45, 38 (range 65) |

- **The odd tone:** most of the face is the salmon mid tone 115 (224,152,128). Vanilla Gohan portraits keep the lit pink 114 as the largest class.
- **No contrast:** the face is two tones 55 luminance apart, with no hard cel shadow. There is no under-eye band, no cast shadow under the chin, and no deep tone.
- **Bare hair:** pale lemon 45 fills 61-69 % of the hair. There is no gold shadow tone (vanilla Super Saiyan art uses 128 and 133). Only 6-8 % is the orange 38.

---

## 3. What changed per portrait (version A)

**Shared ramp (one constant, `s7_paint.A_MAP`): H 44, L 16, M 116, S 117, D 21, the same as Goku A.** Gold hair: W 43 (shine), Y 45 (lit), G 36 (gold), O 38 (shadow). Black hair (base only): G 13, g 14, k 15, as Goku A v2.

**Light rule:** the key light sits in front of the face, on the side the face turns to. The front plane is lit, and the ear side and far plane are in shade. This is how Goku A is lit.
- 115 turns right, so the light is from the upper right. This keeps the drawing's own lit front plane.
- 117 faces front with the head tilted down to the left, so the light is from the upper left. 119 faces front, not tilted, and its drawn split is already lit from the upper left. Both keep the drawing's own split.
- A single world light for both would flip 115's planes against its drawn accents, so I did not do it.

**Method (`h6_paint.py`, `h7_base.py`):**
- **Skin:** every 114 and 115 pixel starts as its ROM class (L, M). Then hand patches set letters per pixel: `PATCH_115` has 95 runs, `PATCH_117` 60 and `PATCH_119` 47. The 116 and 117 accents beside the lines are drawing and never change.
- **Gold hair:** the fill (45, 43, 38) inside the drawn strand lines. Eyebrows and eye whites are cut out by hand seeds. Per pixel:
  - next to a line, skin or background on the side away from the light, or below: shadow 38;
  - next to one on the lit side, or above: lit 45;
  - both: gold 36;
  - the drawn orange 38 stays;
  - the drawn white shine 43 stays, except where it touches a strand edge on its away side only. There it becomes 38. CONFIRMED by a direct count: 10 shine pixels in 115 and 26 in 117 became 38;
  - the rest: gold 36.
  - The frame crop is not a strand edge.
- **Honest note:** the hair is a per-pixel rule inside each strand, with hand-chosen light and exclusions. It is not typed by hand.
- **Black hair (base):** 5 hairlib strands from hand boxes and 10 hand legs, checked by hairlib. The legs are 0-23 degrees off their contours.

| Portrait | Pixels changed | Skin letters | Hair | What the hand patches do |
|---|---|---|---|---|
| `gohan_ssj_A.png` (for 115) | 1441 | L 228, M 401, S 182, D 18, H 12 | G 434, O 256, W 326, Y 91 | Temple shadow under the hair. Forehead shine (x 43). Under-eye band (rows 37-38). Hollow under the cheekbone line (row 36). Cheekbone and chin shine. Nose cast shadow. Ear bowl. Neck under ear and jaw (S, D). Throat under the jaw (S, D). Shoulder by the neck. A 1 px shadow under the collarbone |
| `gohan_ssj2_A.png` (for 117) | 1360 | L 308, M 396, S 139, D 2, H 10 | G 325, O 223, W 179, Y 80 | Right temple and far side (S). Forehead shine (diagonal). Under-eye band under both eyes. Nose shine and nose cast shadow. Right ear bowl. Chin shine. Cast shadow under the jaw curve (S, D). Left neck under the chin. Right edge of the neck by the collar |
| `gohan_base_A.png` (for 119, proposal) | 474 | L 159, M 188, S 72, D 1, H 6 | g 15, G 14, k 19 | Shine on the left skin gap. Shade on the right gap's edge. Under-eye band. Right ear bowl. Far cheek and jaw. Chin shine. Neck under the chin (S, D). Lit inner and far outer right pec. Grey strand strokes |

After the pass (CONFIRMED, `h4_flat.txt`):
- **Skin:**
  - 115: range 126, sd 38.2.
  - 117: range 125, sd 40.4.
  - 119: range 102, sd 37.9.
  - Goku A: range 125, sd 40.2.
- **Gold hair:** 36 is now the largest class (38-39 %). The spread rose from 16.7 / 14.2 to 23.8 / 23.9. The darkest tone is still 38, so the hair range stays 65.

---

## 4. Base gi Gohan

**Clear mismatch, so I made a base proposal. CONFIRMED by the numbers, LIKELY by eye.**
- 119 keeps the pink ramp 114/115/116 (range 55). The new Super Saiyan forms use the peach and tan of Goku A.
- In game, a transform would switch skin color as well as hair.
- `gohan_base_A.png` is a new file only. I-approved drawing `gi_base_dialog_src.png` and `gi_base_dialog.png` are untouched.
- The line here is 35, not 113. It stays.

---

## 5. Status twins

Made by `h8_status.py` through `gohan_portraits._status_of` (log `h8_status.txt`). Files: `gohan_ssj_A_status.png`, `gohan_ssj2_A_status.png`, `gohan_base_A_status.png`.

- **CONFIRMED:** the pairing map rebuilds the shipped twins from the shipped dialog art: 115 to 116, 117 to 118 and 119 to 120, each 4096/4096.
- **CONFIRMED:** game pair or nearest per form:
  - Super Saiyan A: 22 game pairs, 2 nearest. 146 is the sheet's light green (as shipped). 38 maps to status 73 (200,184,64), RGB error 54.
  - Super Saiyan 2 A: 22 game pairs, 3 nearest (146, 38, and the mouth pink 248, as shipped).
  - Base A: 21 game pairs, 0 nearest.
- **CONFIRMED:** on the status screen, skin S 117 and D 21 merge into status 32. D is rare (1-18 px). Gold hair W, Y, G and O stay four status colors.
- **LIKELY (by eye):** each twin's shade side is redder than the dialog art. 116 pairs with status 33 (208,104,72), error 35, the same as Goku's twin. The hair shadow 38 reads a little olive on the status screen.

---

## 6. Checks (every run; the script stops on a failure)

- **CONFIRMED:** only skin fill pixels (114/115) and hair mask pixels change. So every line (23, 113, 35), accent (116, 117), eye, eyebrow, mouth, gi, background and frame pixel stays the same.
- **CONFIRMED:** every index used is one that USA dialog portraits use, never 0 or 168. This is the rule `gohan_portraits.apply()` enforces.
- **CONFIRMED (gold hair):** every shadow pixel touches a strand edge on its away side. Every lit pixel touches a strand edge on its lit side. No stroke floats, and none crosses a line, because no line pixel changes.
- **CONFIRMED (black hair, base):** hairlib checks each stroke pixel:
  - the pixel is in its own strand;
  - it is at most 3 steps from the contour;
  - it is not an outline pixel;
  - each leg is within 30 degrees of the contour.
- **CONFIRMED:** some accent pixels end up with all four neighbours in their own color, so they no longer show:
  - 115: 2, the ear (20,29) and the under-eye soft line (37,37).
  - 117: 1, (33,42).
  - 119: 9. Four are on the sternum line (x 29-30, rows 54-57). Five sit at the shoulder edges.
  - The pixels are unchanged. Only the contrast around them is gone.

---

## 7. Honest rating (my judgment, LIKELY)

Looked at `compare_gohan.png` at 4x, and at 6x and 10x working views.

| Portrait | Of the Goku A look | Why |
|---|---|---|
| Super Saiyan A | **About 65-70 %** | Peach front, tan ear side, hard under-eye band, throat and neck cast shadows: these read like Goku A. The hair now reads gold, with orange shadow rims along the strand lines. The drawn white shines are large, so the hair still looks bright and busy |
| Super Saiyan 2 A | **About 60 %** | Same skin and style, and it reads as the same person. The lower face and neck are mostly tan, so it looks darker than the Super Saiyan. The odd stylised source drawing limits how clean the forms get |
| Base A | **About 65 %** | Matches the new skin. The grey strand strokes are sparse, like Goku v2 |
| Status twins | **Good** | They look like the dialog art. The shade side is redder, as for Goku |

---

## 8. Concerns

1. **"The darker line where Goku A used it" does not apply to version A. CONFIRMED.**
   - Goku A kept line 113. Only Goku B darkened it, with a new color.
   - Both Gohan Super Saiyan portraits already draw skin lines in 113, and hair lines in 23.
   - Recoloring a line would break "every outline and drawing pixel unchanged", so I changed no line.
2. **Light direction differs between 115 and 117.** Both follow the stated rule, but the key light comes from opposite sides. A single light for both needs a relight that fights 115's drawn planes. That is my call.
3. **Hair contrast.** The darkest hair tone is still 38, so the hair range is 65, against 96 for vanilla Super Saiyan art.
   - A deep root shadow in 120 (224,160,64) or 133 (168,160,64) would add depth.
   - 120 has no game status pair.
   - SPECULATIVE that I want it.
4. **Status hair shadow.** 38 has no game pair, so its status twin uses nearest 73 (olive). 138 has a real pair, but to the same status 73.
5. **The Super Saiyan 2 repaint also replaces the gi Rage portrait** through the `cutscene_portraits` hook. CONFIRMED in r16 bytes, LIKELY in game (see section 1).
6. **Base is a proposal.** It replaces the look of an approved drawing, so it needs my yes before any patch uses it.
7. **Process slip.** I edited `h6_paint.py` once with a Bash heredoc running Python (two seed fixes). Check after all edits: every new `.py` and `.txt` file has 0 CR, 0 other control bytes, 0 non-ASCII bytes and no byte order mark. All Python ran with `-I -B`. The only `.pyc` files I could have written are `gohan_portraits` and `webfoot_decompress`, and their caches date from 18:14 and 01:14, before this run.
8. **No in-game test.** Nothing was built. To ship, a later patch run would point `gohan_portraits` at these PNGs. That is outside this task.

---

## Files

Art (`art\portrait-sources\remaster\`):
- `compare_gohan.png`
- `gohan_ssj_A.png`, `gohan_ssj2_A.png`, `gohan_base_A.png`, and their `_status.png` twins
- `old_gohan_*.png`

Scripts and logs (`scripts\one-time\2026-10-19-portrait-from-anime\`):

| File | Purpose |
|---|---|
| `h1_unpack.py`, `gohan_census.txt` | Id list, unpack, census, templates |
| `h2_palette.py`, `h2_palette.txt` | Warm OBJ colors: use and status pairs |
| `h3_template.py`, `gohan_<id>_template.txt` | Skin fill runs for the hand patches |
| `h4_flat.py`, `h4_flat.txt` | Source check and shade statistics |
| `h5_strands.py`, `h_strands_115.png`, `h_strands_117.png` | Gold hair component maps |
| `h6_paint.py`, `h6_paint.txt` | Super Saiyan and Super Saiyan 2 repaint and checks |
| `h7_base.py`, `h7_base.txt`, `h_strands_119.png` | Base repaint, hairlib strands |
| `h8_status.py`, `h8_status.txt` | Status twins and pairing proof |
| `h9_compare.py` | Compare sheet |
| `h_view.py`, `h_view_*.png`, `h_grid_*.png` | Working views |
