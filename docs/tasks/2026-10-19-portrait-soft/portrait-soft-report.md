# Portrait remaster v2: mid and soft shading, version A (2026-10-19)

Labels: **CONFIRMED** = proved here with data or a script check. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

Brief: `docs\tasks\2026-10-19-portrait-soft\portrait-soft.md`, plus my 8:07 AM feedback through the coordinator: "the soft versions look like the original, needs a middle ground". Version A only. No ROM build, no patch, no status twin. I wrote files only in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. Every earlier file is unchanged. The soft files stay as they were.

---

## 0. Mid A (the middle ground)

**Map.** Mid keeps A's peach lit 16 and moves every shade one step lighter. Skin: H and L 16 (218), M 115 (171), S 116 (146), D 117 (115). Vegeta: H and L 16, M 17, S 18, D 20 (his A neck shadow stays; the cream stripes go). Black hair: G 13 (112), g 15 (64), k 15 (64). Gold hair: W 44, Y 45, G 36, O 38 (the white glare goes; A's orange shadow stays). The accent guard and the skip fix of section 1 run as for soft.

**Luma gap, all three versions (CONFIRMED, `k1_soft.py`). Main lit = L index, main shadow = M index.**

| Portrait | A gap | **Mid gap** | Soft gap | Halfway A to soft | Mid ratio to A | Weighted gap A / mid / soft | Skin range A / mid / soft |
|---|---|---|---|---|---|---|---|
| Goku 63 | 71.8 (16 / 116) | **46.9 (16 / 115)** | 30.5 (114 / 115) | 51.2 | 0.65 | 79.4 / 51.7 / 35.3 | 126.3 / 102.3 / 86.0 |
| Vegeta 106 | 20.5 (16 / 17) | **20.5 (16 / 17)** | 20.5 (16 / 17) | 20.5 | 1.00 | 27.7 / 26.4 / 25.1 | 113.6 / 90.6 / 43.6 |
| Gohan 115 | 71.8 | **46.9** | 30.5 | 51.2 | 0.65 | 83.2 / 54.3 / 37.9 | 126.3 / 102.3 / 86.0 |
| Gohan 117 | 71.8 | **46.9** | 30.5 | 51.2 | 0.65 | 80.6 / 53.0 / 36.6 | 126.3 / 102.3 / 86.0 |
| Gohan 119 | 71.8 | **46.9** | 30.5 | 51.2 | 0.65 | 81.2 / 51.2 / 34.8 | 126.3 / 71.8 / 55.4 |

- 46.9 is the nearest gap the palette offers to the halfway value 51.2. The other candidate, pink 114 lit with tan 116 shade (gap 55.4), clashed in hue in the working view (`k_trial.png`), so I dropped it.
- Vegeta's main gap is fixed by his ROM pair (see section 2). His mid sits between A and soft in skin range: 113.6, 90.6, 43.6.

**Mid counts (CONFIRMED).** Shapes and edge fixes are the same as soft (same letters), so the S and D counts equal the soft ones in section 3.

| Portrait | Px changed vs A | Px changed vs OLD | Drawing edges merged (A to mid) |
|---|---|---|---|
| Goku | 599 | 506 | 0 to 0 |
| Vegeta | 34 | 153 | 0 to 0 |
| Gohan 115 | 945 | 1354 | 50 to 0 |
| Gohan 117 | 728 | 1164 | 13 to 0 |
| Gohan 119 | 291 | 277 | 52 to 0 |

**Mid rating (my judgment, LIKELY).** Mid is the best of the three against my words.
- Goku, Gohan 115 and 117: they keep the remaster's peach and tan look, the cel shapes read clearly (under-eye band, neck and throat shadows, the 115 temple), and the face no longer looks lit by a studio lamp. Goku mid differs from the ROM in 506 px, against 155 for soft, so it no longer reads as the original.
- Gohan 119: matches the other forms. Its cheek shading stays small, because the accent guard keeps its drawn lines visible.
- Vegeta: mid is A without the cream forehead stripes, with the hair core kept. It is close to A (34 px). Vegeta was always closest to the ROM, because A kept his ROM skin pair.
- Hair: the grey strand cores (112) still show on black hair. The gold hair keeps its orange shadow rims without the white glare.

**Mid files:** `art\portrait-sources\remaster\goku_mid_A.png`, `vegeta_mid_A.png`, `gohan_ssj_mid_A.png`, `gohan_ssj2_mid_A.png`, `gohan_base_mid_A.png`. The checks of section 3 pass for every mid file.

**For the status task:** mid fills use 16, 115, 116, 117 (Goku, Gohan), 16, 17, 18, 20 (Vegeta), 13, 15 (black hair) and 44, 45, 36, 38 (gold hair). 38 has no status game pair (as in A).

---

## Compare sheet

`art\portrait-sources\remaster\compare_soft.png`: 4x on lime (191, 255, 7). One row per portrait. Columns: OLD | current A | mid A | soft A.
- OLD is the USA ROM for Goku 63 and Vegeta 106.
- OLD is r16 for Gohan 115, 117 and 119 (the hack's own art).

---

## Files

| File | What |
|---|---|
| `art\portrait-sources\remaster\goku_soft_A.png` | Goku 63, from the strand-hair A (`goku_A_v2.png`) |
| `art\portrait-sources\remaster\vegeta_soft_A.png` | Vegeta 106, from `vegeta_A.png` |
| `art\portrait-sources\remaster\gohan_ssj_soft_A.png` | Gohan Super Saiyan 115, from `gohan_ssj_A.png` |
| `art\portrait-sources\remaster\gohan_ssj2_soft_A.png` | Gohan Super Saiyan 2 117, from `gohan_ssj2_A.png` |
| `art\portrait-sources\remaster\gohan_base_soft_A.png` | Gohan base gi 119, from `gohan_base_A.png` |
| `art\portrait-sources\remaster\compare_soft.png` | The compare sheet |
| `scripts\one-time\2026-10-19-portrait-from-anime\k0_layers.py` | Rebuilds the letter layers of the five current A portraits from their paint scripts |
| `art\portrait-sources\remaster\*_mid_A.png` | The five mid versions (section 0) |
| `scripts\one-time\2026-10-19-portrait-from-anime\k1_soft.py` | The mid and soft passes (`VARIANTS`), their checks and the luma tables |
| `scripts\one-time\2026-10-19-portrait-from-anime\k2_compare.py` | The compare sheet (`--zoom` adds the 8x working view `k_zoom.png`) |
| `scripts\one-time\2026-10-19-portrait-from-anime\k0_trial.py`, `k_trial.png` | Working view of the candidate ramps. It now shows the mid candidates (peach mid, pink-tan mid) |

All files are 64x64 indexed PNGs with the OBJ palette. Run with `py -3 -I -B`.

---

## 1. Method

**The shapes stay. Only the colors and a few edge pixels change. CONFIRMED.**
- `k0_layers.py` rebuilds each current A from its paint script (`s7`/`g2`, `v2`, `h6`, `h7`). Each rebuild equals the A PNG on disk, byte for byte.
- Each skin and hair pixel keeps its A letter (H, L, l, M, S, D for skin; G, g, k or W, Y, G, O for hair). The soft pass changes the letter-to-index map.
- So the cel shadow placement, the strand hair strokes and the light side of each drawing stay as in A. 115 keeps its light from the upper right. The others keep the upper left.

**Soft maps (luma is Rec. 601):**

| Ramp | H | L | M | S | D |
|---|---|---|---|---|---|
| A, Goku and Gohan | 44 (241) | 16 (218) | 116 (146) | 117 (115) | 21 (114) |
| **Soft, Goku and Gohan ("pink")** | 114 (201) | 114 (201) | 115 (171) | 116 (146) | 117 (115) |
| A, Vegeta | 44 (241) | 16 (218) | 17 (197) | 18 (174) | 20 (127) |
| **Soft, Vegeta (his own ramp)** | 16 (218) | 16 (218) | 17 (197) | 18 (174) | 19 (151) |

| Hair | A | Soft |
|---|---|---|
| Black (Goku, Vegeta, Gohan base): G, g, k | 13 (112), 14 (88), 15 (64) | 14 (88), 15 (64), 15 (64) |
| Gold (Gohan 115, 117): W, Y, G, O | 43 (247), 45 (233), 36 (220), 38 (182) | 44 (241), 45 (233), 36 (220), 37 (204) |

- The lit side is now 114, the ROM's normal skin for Goku and Gohan. For Vegeta it stays 16, which is his normal ROM skin.
- H merges into L. So the soft art has no pale or yellow highlight. (The cream 44 stripes on Vegeta's forehead are gone.)
- Each step is the next step down one ramp.

**Edge fixes in `k1_soft.py` (rule, applied after the map):**
1. **Accent guard.** In the Gohan art, the drawn accents beside the lines are 116 and 117. Soft S and D use those same indices. A shadow pixel beside an accent of its own index would hide that accent. Such a pixel steps up one step (S to M, D to S). The same rule hits Vegeta: soft D 19 equals the jaw edge accent 19, so those 10 D pixels became S.
2. **Skip fix.** Where two touching skin pixels are two steps apart (L next to S, or anything next to D), the pass closes the gap by one step. D always steps up. In a thick shadow the S pixel steps up to M, so the shadow shrinks by 1 px. A 1 px S line keeps its pixel, and its L neighbour steps down to M.
- I made no hand trims. The `TRIM` table is empty. The two rules already make the shadows a little smaller where they met a line or the lit side.

---

## 2. Luma gap table (CONFIRMED, `k1_soft.py` output)

Main lit = the L index. Main shadow = the most used of M, S, D (M in all five). Weighted gap = mean luma of all lit pixels minus mean luma of all shadow pixels. Range = brightest minus darkest skin index used.

| Portrait | A: lit / shadow | A gap | Soft: lit / shadow | Soft gap | Ratio | Weighted gap A to soft | Skin range A to soft |
|---|---|---|---|---|---|---|---|
| Goku 63 | 16 / 116 | 71.8 | 114 / 115 | **30.5** | **0.42** | 79.4 to 35.3 | 126.3 to 86.0 |
| Vegeta 106 | 16 / 17 | 20.5 | 16 / 17 | **20.5** | **1.00** | 27.7 to 25.1 | 113.6 to 43.6 |
| Gohan 115 | 16 / 116 | 71.8 | 114 / 115 | **30.5** | **0.42** | 83.2 to 37.9 | 126.3 to 86.0 |
| Gohan 117 | 16 / 116 | 71.8 | 114 / 115 | **30.5** | **0.42** | 80.6 to 36.6 | 126.3 to 86.0 |
| Gohan 119 | 16 / 116 | 71.8 | 114 / 115 | **30.5** | **0.42** | 81.2 to 34.8 | 126.3 to 55.4 |

- Goku and Gohan: the gap falls to 42 % of A. 30.5 is the nearest gap the palette offers to half (36). **CONFIRMED.**
- **Vegeta's main gap cannot be halved. CONFIRMED.** His A already used his own ROM pair 16 and 17, 20.5 apart, and no OBJ color lies between them. His contrast came from the cream 44 stripes, the D 20 neck shadow and the hair greys. The soft pass removes the stripes, moves D to S and dims the greys. So the skin range falls from 113.6 to 43.6.

---

## 3. What changed per portrait (CONFIRMED counts)

| Portrait | Px changed vs A | Px changed vs OLD | Skin letters A to soft | Edge fixes | Drawing edges merged (A to soft) |
|---|---|---|---|---|---|
| Goku | 950 | 155 | S 97 to 102, D 6 to 1, M 432 to 436 | skip 9, guard 0 | 0 to 0 |
| Vegeta | 58 | 153 | S 60 to 70, D 10 to 0 | guard 10 | 0 to 0 |
| Gohan 115 | 1423 | 1211 | S 182 to 149, D 18 to 14, M 401 to 444 | guard 34, skip 13 | 50 to 0 |
| Gohan 117 | 1257 | 891 | S 139 to 129, D 2 to 1, M 396 to 409 | guard 8, skip 6 | 13 to 0 |
| Gohan 119 | 455 | 129 | S 72 to 46, D 1 to 0, M 188 to 224 | guard 26, skip 11 | 52 to 0 |

- "Drawing edges merged" counts drawing pixels that lost a neighbour of a different color. In A, M 116 hid some Gohan accents (115: 2 swallowed, 117: 1, 119: 9). The soft art hides none. **CONFIRMED.**
- Gold hair: the drawn orange 38 marks and the drawn white shines 43 are hair fill in `h6_paint`, so they change too (38 to 37, 43 to 44). The hair lines 23 do not change.
- Black hair: the strokes keep their pixels. Only their grey is one step darker.

**Checks (every run; the script stops on a failure). CONFIRMED:**
- Changed pixels lie in the skin fill, the hair mask or Goku's 4 iris pixels. The paint scripts' own checks also run (`s7.check`, `v2.check`, `h6.check`).
- No outline pixel changes. No line pixel changes (113 for Goku and Vegeta; 23 and 113 for Gohan 115 and 117; 35 for 119).
- Outside skin and hair, each soft file equals its A file.
- Every index is one that USA dialog portraits use, never 0 or 168.
- No skin skip pair is left. No S or D pixel touches an accent of its own index.

---

## 4. Honest rating against my words (my judgment, LIKELY)

I looked at `compare_soft.png` at 4x and at the 8x working view.

| My words | Result |
|---|---|
| "Contrast a bit strong" | Fixed. Lit and shade now sit one step apart on every face |
| "Shading, not studio lighting" | Mostly met. The faces read as evenly lit skin with soft cel shapes. No face has a bright plane next to a dark one any more |
| Lit side = normal skin | Met. Goku and Gohan are on the ROM pink 114, Vegeta on his 16 |
| Shadows stay clear shapes | Partly. The shapes are there, but at one step they are quiet. The Gohan 115 neck and temple read best. The Goku under-eye band and chin shadow are faint |
| Hair highlights present, not glaring | Met. The grey strands still show on black hair. The gold hair lost its white glare and reads warm gold |

| Portrait | Rating | Why |
|---|---|---|
| Goku | **Soft, but close to the ROM** | Only 155 px differ from OLD: the hair strands, the black irises and the cel edges. It reads like a cleaner vanilla Goku, not a remaster |
| Vegeta | **Good** | Calm, keeps his yellow peach. The forehead stripes are gone. It is close to OLD as well (153 px), plus the hair strands |
| Gohan 115 | **Best of the set** | Soft temple, neck and throat shadows, gold hair without glare |
| Gohan 117 | **Good** | The chin and neck shadows read as shading. The face matches 115 |
| Gohan 119 | **Good, quiet** | Matches the Super Saiyan forms in skin. Its cheek shading is now small |

All five now share one skin ramp per character, so a transform no longer changes Gohan's skin color. **CONFIRMED** (115, 117 and 119 all use 114, 115, 116 and 117).

---

## 5. Concerns

1. **The soft Goku is nearly the ROM Goku. CONFIRMED (155 px differ).** Most of A's look came from a hue swap: pale peach 16 lit and tan 116 shade. The OBJ palette has no tone between 16 and 116 in that hue (the study found the same). So a soft ramp in version A must fall back to the ROM pink. I may feel the remaster look is lost on Goku and Vegeta. A peach-to-tan soft look needs the new colors of version B, which I dropped. (LIKELY that I notice.)
2. **Vegeta's main gap is unchanged by nature. CONFIRMED.** See section 2.
3. **The accent guard shrinks Gohan 119's shadows the most** (S 72 to 46). This keeps the drawn lines visible. The base cheek shading is now small. (CONFIRMED count, LIKELY by eye.)
4. **For the status task (not acted on):**
   - 37 (gold shadow) has no status game pair, as 38 had none. Its nearest status color may read olive. (CONFIRMED in `h2_palette.txt`: 37 "no pair".)
   - 19 pairs with status 34, 44 with 51, 114 with 23 and 115 with 27 (from `h2_palette.txt`).
   - Soft S 116 pairs with status 33 (error 35), so the status shade side may read redder. (LIKELY, from the earlier reports.)
5. **No in-game test.** Nothing was built.
6. **Process.** All files were written with the Write and Edit tools. Python ran with `-I -B`. Each new `.py` file has 0 CR, 0 other control bytes, 0 non-ASCII bytes and no byte order mark. The scripts import `gohan_portraits` and `webfoot_decompress` read-only.

---

## Bible rows (for me to add; I did not edit `docs\RE-BIBLE.md`)

| Topic | Fact | Label |
|---|---|---|
| OBJ palette skin ramps | Pink ramp 114 (201), 115 (171), 116 (146), 117 (115). Peach ramp 16 (218), 17 (197), 18 (174), 19 (151), 20 (127). Luma Rec. 601. No OBJ color lies between 16 and 116 in the peach-to-tan hue | CONFIRMED |
| OBJ palette gold ramp | 43 (247), 44 (241), 45 (233), 36 (220), 37 (204), 38 (182), 39 (161). All are used by USA dialog portraits | CONFIRMED |
| Gohan gi accents | Portraits 115, 117 and 119 draw skin accents in 116 and 117. A fill in the same index hides them | CONFIRMED |
