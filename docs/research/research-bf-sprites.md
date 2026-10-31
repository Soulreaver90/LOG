# Research 1: Buu's Fury Goku and Piccolo sprites in LoG II

This page answers the five questions in `docs\tasks\2026-10-17-bf-sprites-research\research-1-bf-sprites.md` (my idea, design 6.7). It is research only: no patch and no ROM was built.

Labels: **C** = CONFIRMED (evidence given), **L** = LIKELY, **S** = SPECULATIVE. Scope (Ruling 34): data only. No Buu's Fury code was disassembled. Every Buu's Fury layout fact below comes from data scans, so a layout fact is at most L unless the bytes alone prove it.

> [!NOTE]
> **Short answer.** Every Buu's Fury player frame fits the 1024-byte slot. The Buu's Fury colors almost all exist in the LoG II OBJ palette. Goku can be ported for 17 of his 19 LoG II animations. Piccolo cannot: the Buu's Fury Piccolo is an NPC with 12 of 20 animations and no frame without the cape.

---

## 1. Method and evidence

This section says how the Buu's Fury data was read, so the later numbers can be checked.

| Fact | Evidence | Label |
|---|---|---|
| Buu's Fury uses the LoG II frame codec | 12,457 of 12,471 aligned `{type 1 or 2, size}` headers decode to exactly `size` bytes with `webfoot_decompress.decompress` (LoG II: 12,325 of 12,334) | C |
| Buu's Fury OBJ palette is at `rom:0x5652C` (256 BGR555 entries) | Every index the four sheets use (32 to 40 per character) equals the sheet color shifted right by 3, at this one offset only | C |
| Buu's Fury sprite set layout | See the next table. Found by data scans; the BF code that reads it was not read | L |
| Buu's Fury Goku = set `rom:0x6AD1CC` (copy `rom:0x6AD30C`), Super Saiyan = `rom:0x6AD3B8` (copy `rom:0x6AD464`), Super Saiyan 3 = `rom:0x6AD510` (copy `rom:0x6AD5B4`), Piccolo = `rom:0x6B2860` | Every cell of each of my sheet (232, 200, 173, 120 cells) matches a frame of that set by exact silhouette. Colors then match `rom:0x5652C` | C |
| The two copies of each Goku set share all anim pointers and differ only in header bytes +12 to +83 (the boxes) | Byte compare | C (bytes), S (why two copies; which one the player uses needs code) |
| Same object anchor in both games: 32x32 frames at dx -8, dy -24; 16x32 at dx 0, dy -24 | Record counts in both games (for example BF Goku 290 of 320 keys at -8, -24) | C (data), L (same meaning) |
| Same direction order: dir 0 faces down, dir 1 up, dir 2 left, dir 3 right; dir 3 is mostly the H-flip of dir 2 | Contact sheets; dir 3 reuses the dir 2 header in 75 of 79 (LoG set 60) and 76 of 80 (BF Goku) keys | C (flip counts), L (facing, by eye) |

Buu's Fury set layout (L, data scans; 290 sets found this way):

| Part | Layout |
|---|---|
| Set header, 84 bytes | u16 anim count, u16 slot bytes (0x400 for all four characters), u32 0, u32 `0x040A0810`, then 72 bytes of boxes (4 x 16 bytes plus 2 words) |
| Anim table | One u32 pointer per anim (null allowed), right after the header. LoG II has one pointer per anim per direction |
| Anim block | u32 frame count, then count x 4 record pointers, frame-major (f0 d0-d3, f1 d0-d3) |
| Record, 20 bytes | u32 (1 in all four sets, meaning unknown, S: timing or flag), s8 x, s8 y, u8 w, u8 h (a box, equal to the draw box here), then the LoG II 12-byte record (dx, dy, w, h, attr0, attr1, frame header pointer) |

Two layout differences matter for a port (L). Buu's Fury keeps the frame count in data; LoG II keeps it in code (RE-BIBLE section 4). Buu's Fury has a box per record; LoG II has 4 boxes per set.

Scripts are in `scripts\one-time\2026-10-17-bf-sprites-research\` (`bf_lib.py`, `match_bf.py`, `bf_palfind.py`, `color.py`, `contact.py`, `inventory.py`). They only read the ROMs and the sheets.

---

## 2. Frame inventory (question 1)

This section lists the LoG II keys, the Buu's Fury poses, and how they map.

### 2.1 LoG II sets (from the appearance table)

| Character | Appearance entry | Set | +0 bit 0 | Keys | Label |
|---|---|---|---|---|---|
| Goku base | 19 (+4 = 20) | `set:60` | 0 | 316 | C (bytes `00 3C 3F 0E 14 14`) |
| Goku Super Saiyan | 20 (+5 = 19) | `set:61` | 1 | 304 | C (bytes `01 3D 41 0F 13 13`) |
| Piccolo with weights | 6 (+4 = 7) | `set:103` | 0 | 324 | C (bytes `00 67 5A 11 07 07`) |
| Piccolo without weights | 7 (+5 = 6) | `set:104` | 1 | 304 | C (bytes `01 68 5E 12 06 06`) |

Every key is `(anim, dir, index)` with dir 0 to 3 and the same frame count in all 4 dirs (C, `set_records`). So each row below lists 4 x n keys: `a.0.0` to `a.3.(n-1)`. The full list with one row per key is `scripts\one-time\2026-10-17-bf-sprites-research\inventory.csv` (1,552 rows: the 1,248 unique keys, with set 61 listed once per BF source).

Pose names come from the frames, by eye (L). "BF" is the matching Buu's Fury anim in the set named in the column head. "none" means Buu's Fury has no such pose.

| LoG anim | Pose | Set 60 n | BF Goku | Set 61 n | BF SSJ | BF SSJ3 | Set 103 n | BF Piccolo | Set 104 n |
|---|---|---|---|---|---|---|---|---|---|
| 0 | stand | 2 | 0 (2) | 2 | 0 (2) | 0 (2) | 2 | 0 (2) | 2 |
| 1 | walk | 4 | 1 (4) | 4 | 1 (4) | 1 (4) | 4 | 1 (4) | 4 |
| 2 | hurt, stars | 4 | 9 (3) | 4 | 9 (3) | 9 (3) | 4 | 9 (3) | 4 |
| 3 | knocked down | 4 | 17 (4) | 4 | 17 (4) | 17 (4) | 4 | 17 (4) | 4 |
| 4 | idle variant (arms up and down in the Goku sets; the design doc calls anim 4 idle) | 4 | 12 (2) | 4 | 12 (2) | 12 (2) | 4 | 12 (4) S | 4 |
| 5 | punch | 3 | 3 (3) | 3 | 3 (3) | 3 (3) | 3 | 3 (3) | 3 |
| 6 | melee 1, arc | 4 | 4 (4) | 4 | 4 (4) | 4 (4) | 4 | 4 (4) | 4 |
| 7 | melee 2, arc | 4 | 5 (4) | 4 | 5 (4) | 5 (4) | 4 | 5 (4) | 4 |
| 8 | melee 3, arc | 4 | 6 (4) | 4 | 6 (4) | 6 (4) | 4 | 6 (4) | 4 |
| 9 | power up (transform) | 4 | 10 (11, front only) | - | - | - | 4 | none | - |
| 10 | knocked out, hair turns black | - | - | 4 | none | none | - | - | - |
| 11 | lift arms overhead | 2 | 13 (2) | 2 | 13 (2) | 13 (2) | 2 | 13 (2) S | 2 |
| 12 | swim, head only | 4 | 15 (4) | 4 | 15 (4) | 15 (4) | 4 | 15 (4) | 4 |
| 13 | run | 4 | 2 (4) | 4 | 2 (4) | 2 (4) | 4 | 2 (4) | 4 |
| 14 | crouch, bobbing | 5 | 8 (4) | - | - | - | 5 | none | - |
| 16 | special 1 (Goku teleport; Piccolo spin) | 7 | 19 (3) | 7 | 19 (3) | 19 (3) | 7 | none | 7 |
| 17 | halo | 2 | none | - | - | - | 2 | none | 2 |
| 18 | charge (special 2) | 7 | 18 (3) | 7 | 18 (3) | 18 (3) | 7 | none | 7 |
| 19 | special 3 | 7 | none | 7 | none | none | 7 | none | 7 |
| 20 | fly | 4 | 16 (4) | 4 | none | none | 4 | none | 4 |
| 21 | revert (form ends) | - | - | 4 | 11 (4) | 11 (4) | - | - | 4 |
| 22 | stand 2 | - | - | - | - | - | 2 | none | 2 |

Labels for the map: every pair is L (silhouette score plus a check by eye on the contact sheets). Two are C: anim 12 to BF 15 for Super Saiyan (14 keys with identical silhouettes) and for Piccolo (4 keys identical in shape and color). Two are S, marked in the table. Set 104 has no Buu's Fury pose at all (see section 5).

### 2.2 LoG II keys with no Buu's Fury pose

| Character | Anims with no pose | Keys | Of total |
|---|---|---|---|
| Goku base (set 60) | 17 halo, 19 special 3 | 36 | 316 |
| Goku Super Saiyan (set 61, from BF SSJ) | 10 knocked out, 19 special 3, 20 fly | 60 | 304 |
| Goku Super Saiyan (set 61, from BF SSJ3) | same three | 60 | 304 |
| Piccolo with weights (set 103) | 9, 14, 16, 17, 18, 19, 20, 22 | 152 | 324 |
| Piccolo without weights (set 104) | all 19 anims | 304 | 304 |

"No pose" means no pose in the four BF character sets. The other 284 sets were checked by two color shapes (L): frames with Goku's gi orange (BF 64, 65, 4) plus black hair or Super Saiyan gold, and small frames (512 bytes or less) that are mostly gold, for a halo. The hits, checked by eye, are Goten, Gohan, Buu and effects; no Goku halo, fly, knock-out or extra attack. A Goku frame in other colors would not appear in this search.

Frame counts differ in these mapped anims (LoG n against BF n). LoG II keeps the count in code, and `build_set` refuses a different count, so a port repeats or drops BF frames to fit (C for the tool rule, L for the fix):

- Goku base: 2 (4 vs 3), 4 (4 vs 2), 9 (4 vs 11, front only), 14 (5 vs 4), 16 (7 vs 3), 18 (7 vs 3).
- Super Saiyan from BF SSJ or SSJ3: 2, 4, 16, 18 (same counts as above).
- Piccolo: 2 (4 vs 3).

### 2.3 What each Buu's Fury sheet shows

Each of my sheet is a grid of 32x32 cells, 4 rows (dir 0 to 3) per pose, plus single-row poses. The sheets show almost every unique ROM frame (C, silhouette match).

| Sheet | Cells | Unique ROM frames shown | BF anims shown | BF anims with no LoG II slot |
|---|---|---|---|---|
| Goku | 232 | 154 of 158 | 0-10, 12-19, 21 | 7 single stand pose, 14 swing (3 frames), 21 scripted sequence (11 frames, front only) |
| Goku (Super Saiyan) | 200 | 135 of 139 | 0-7, 9-15, 17-19, 21 | 7, 10 transform to Super Saiyan 3 (11 frames), 14, 21 |
| Goku (Super Saiyan 3) | 173 | 121 of 126 | 0-7, 9, 11-15, 17-19 | 7, 14 |
| Piccolo (NPC) | 120 | 80 of 86 | 0-7, 9, 12, 13, 15, 17, 18 | 7, 18 turned to stone |

"Anims shown" counts an anim once its frames appear; BF anim 5 (SSJ, SSJ3) and Piccolo anims 2, 5 and 13 reuse frames that the sheet shows under another anim.

---

## 3. Size (question 2)

This section checks the 1024-byte player slot (Ruling 35).

- **No Buu's Fury frame exceeds 1024 bytes.** All 1,016 keys of the four sets are 32x32 (1024 bytes) or 16x32 (512 bytes). The set headers also carry slot 0x400. C (records), L (slot meaning).
- **0 frames over, by 0 bytes.** Each frame is one OBJ record, so no frame is a composite of several OBJs. L (one record pointer per frame and dir).
- **The art is wider, not taller.** Opaque width median: BF Goku 25 px against LoG Goku 19 px; SSJ 19 against 19; SSJ3 23 against 19; Piccolo 25 against 22. Height median is 31 px in all, and feet sit on the same row (median shift 0). C (`metrics.json`).
- **Many LoG II keys are 16x32; the BF art for them needs 32x32.** The BF art leaves the LoG II record box in 146 of 280 paired Goku keys, 32 of 244 SSJ, 128 of 244 SSJ3 and 80 of 172 Piccolo. This is no slot problem: a 32x32 frame is exactly 1024 bytes, and `build_set` gives each record its own geometry. C.
- BF uses dx -16, -12, -4 and 0 for some 32x32 frames. LoG II uses -15, -12 and -4 too, so the anchor range is the same. C.

---

## 4. Color (question 3)

This section maps every Buu's Fury color onto the fixed LoG II OBJ palette `rom:0x1DA6C8`.

Method: nearest color in CIELAB (CIE76 dE) over LoG II indices 1 to 255, without 168 (index 0 and 168 are set at run time). Pixel counts come from the ROM frames, not the sheets. A second pass using only the indices the LoG II character already uses is in `color_report.json` for reference. C (computed).

| Character | BF colors | Exact match (dE 0) | Pixel-weighted dE | Pixels over dE 10 | Collapses |
|---|---|---|---|---|---|
| Goku base | 33 | 19 colors, 90.5 % of pixels | 0.7 | 862 (1.5 %) | 4 |
| Goku Super Saiyan | 40 | 22 colors, 83.0 % | 1.2 | 872 (1.9 %) | 8 |
| Goku Super Saiyan 3 | 33 | 21 colors, 83.1 % | 1.1 | 664 (1.3 %) | 4 |
| Piccolo | 32 | 21 colors, 85.9 % | 0.6 | 36 (0.1 %) | 1 |

Worst errors per character (BF index and color, pixels, nearest LoG II index, dE):

| Character | Worst colors |
|---|---|
| Goku base | 31 (88,0,0) 22 px to `pal:27` dE 16.1; 33 (192,0,0) 1 px to `pal:25` dE 14.0; 21 (216,184,152) 160 px to `pal:16` dE 13.3; 80 (136,72,0) 679 px to `pal:23` dE 11.2 |
| Goku SSJ | 77 (56,32,0) 21 px to `pal:113` dE 20.7; 215 (32,136,88) 115 px to `pal:167` dE 19.3; 31 dE 16.1; 33 dE 14.0; 21 dE 13.3; 66 (248,176,104) 4 px dE 11.5; 80 dE 11.2 |
| Goku SSJ3 | 77 dE 20.7; 215 95 px dE 19.3; 31 dE 16.1; 33 dE 14.0; 66 dE 11.5; 80 dE 11.2 |
| Piccolo | 47 (0,72,0) 25 px to `pal:167` dE 24.0; 31 dE 16.1; 33 dE 14.0 |

A collapse is two BF shades that land on one LoG II index, so one step of shading is lost:

- All Goku forms: BF 16 and 80 (two browns) on `pal:23`; BF 81 and 206 (two tans) on `pal:21`.
- Base and SSJ: BF 157 and 94 (dark blues, 12 px) on `pal:81`; BF 65 and 4 (oranges, 2 px) on `pal:32`.
- SSJ and SSJ3: BF 216 and 215 (the two eye greens) on `pal:167`, so the Super Saiyan eye loses its highlight; BF 200 and 66 (golds, 4 px) on `pal:17`.
- SSJ only: BF 2 and 120 (whites) on `pal:2`; BF 21 and 84 on `pal:16`.
- Piccolo: BF 113 and 114 (greys, 120 px) on `pal:14`.

> [!TIP]
> The palette does not need to change. The one visible loss is the Super Saiyan eye (215 to `pal:167`, dE 19.3, about 100 px). An unused LoG II index could hold that green only if the palette changed, which the brief rules out. A darker or lighter existing green is a choice for me on the contact sheet.

---

## 5. Piccolo (question 4)

This section lists what the Buu's Fury Piccolo lacks for a playable Piccolo.

The Buu's Fury Piccolo set has 19 anim slots, 14 used, 176 keys (C). It covers 12 of the 20 anims of `set:103` (section 2.1).

| Missing in Buu's Fury | LoG II anims | Keys in set 103 |
|---|---|---|
| Power up and the transform (cape off) | 9 | 16 |
| Crouch | 14 | 20 |
| Attacks: special 1 (spin), charge (special 2, fingers at the forehead), special 3 | 16, 18, 19 | 84 |
| Halo | 17 | 8 |
| Fly | 20 | 16 |
| Stand 2 | 22 | 8 |
| Every frame without turban and cape (`set:104`, including revert anim 21) | all | 304 in set 104 |

- **No uncaped Piccolo exists in the Buu's Fury ROM, by this search shape.** All 290 BF sets were scanned for frames with at least 20 px of Piccolo skin (indices 11 to 13) and 20 px of his gi purple. Only the Piccolo set and one 64x64 enemy set pair (`rom:0x6AA9B0`, `rom:0x6AAA2C`, a shelled creature, checked by eye) hit. A Piccolo drawn with other palette indices would not appear in this search. L.
- **The BF anims Piccolo has that LoG II lacks:** 7 (one stand pose) and 18 (turned to stone, one frame). C (frames).
- **Cape size.** In stand, walk, run and hurt, the BF cape spreads the opaque width to a median of 24.5 px (maximum 31) against 16 px (maximum 27) in set 103 and 15.5 px in set 104. In stand 0.0.0 the BF frame spans x -5 to 19 against 0 to 15. 19 BF frames fill the full 32 px width. Everything stays inside a 32x32 OBJ, so the cape fits the slot. C (`metrics.json`).
- **The BF melee frames are close copies of LoG II art.** Anims 4 to 6 match LoG II anims 6 to 8 almost pixel for pixel, and the swim frames are identical (4 keys). L (by eye), C (swim).

---

## 6. Options (question 5)

This section compares the four options for each character. Effort assumes the existing tools: `build_set` (each record its own geometry, raw frames), the appearance +1 repoint used for the gi (`gohan_gi`), and a palette remap like `gi_art`.

### 6.1 Goku

| Option | Effort | Risk | What the player sees |
|---|---|---|---|
| Full port (BF frames for every key) | Not possible as is: 36 keys (base) and 60 keys (Super Saiyan) have no BF pose | - | - |
| Partial port: BF frames for 17 of 19 base anims and 15 of 18 Super Saiyan anims; LoG II frames kept for halo, special 3, Super Saiyan knock-out and Super Saiyan fly | Medium. Remap 33-40 colors, retime 6 anims by repeating or dropping frames, cut the 11-frame front-only transform to 4 frames per dir, build two sets and repoint entries 19 and 20 +1 | Low for the slot and palette (sections 3, 4). Medium for looks: BF Goku is 4 to 6 px wider (median opaque width), so the kept LoG II frames (halo, special 3) look thinner; the transform shows a front view in all dirs; cutscenes that name `set:60` or `set:61` directly keep the LoG II look (same pattern as the gi, RE-BIBLE `set:56`) | BF Goku in nearly every pose; LoG II Goku in the halo and one special move |
| Head-only swap (BF head and hair on LoG II bodies) | High. Every one of 620 keys needs a head pasted and aligned, like `gi_art.py` | Low for the slot. Medium for art: the BF hair is wider, so many 16x32 frames become 32x32 | Every LoG II pose and animation, with the BF face and hair |
| Keep LoG II | None | None | No change |

### 6.2 Piccolo

| Option | Effort | Risk | What the player sees |
|---|---|---|---|
| Full port | Not possible: 152 of 324 keys with weights and all 304 keys without weights have no BF pose | - | - |
| Partial port (BF for 12 anims of set 103, LoG II for the rest and for all of set 104) | Medium. Same pipeline as Goku, retime 1 anim | High for looks: the wide BF cape in walk and punch becomes the narrow LoG II cape in the attacks, the transform and the halo; the transform starts from a cape shape it was not drawn for | A cape that changes width between moves |
| Head-only swap | High | High. The cape is the main difference, not the head, so the result is close to the current sprite | Little change |
| Keep LoG II | None | None | No change. The BF melee frames are close to LoG II art already |

---

## 7. Recommendation

This section gives the recommended path per character. It is a recommendation for me, not a decision.

1. **Goku: partial port** of base and Super Saiyan from the BF sets, with LoG II frames for the 2 base and 3 Super Saiyan anims that BF lacks. Start with a review build of anims 0, 1 and 13 (stand, walk, run) to judge the wider sprite in play. The contact sheets in `scripts\one-time\2026-10-17-bf-sprites-research\goku_*.png` and `ssj_*.png` are the review material.
2. **Piccolo: keep LoG II.** The BF sheet is an NPC set: it lacks the transform, the attacks and every uncaped frame, so a port gives a mixed sprite.
3. **Super Saiyan 3 is a separate idea.** The BF set is complete for the same 15 anims as Super Saiyan and includes its own revert. It would need a new appearance entry and form, like the Super Saiyan 2 work (RE-BIBLE section 6).

Open points for a build task: frame timing (BF record word +0 is 1 everywhere, meaning unknown, S); which copy of each BF set the game uses (needs code, out of scope); my review of the S pairs (anim 4 and 11 for Piccolo).

---

## 8. Outputs

| Output | Path |
|---|---|
| Contact sheets (105 PNGs, one per character and LoG II anim; `*_nobf` = no BF pose; `*_bfonly*` = BF pose with no LoG II slot) | `scripts\one-time\2026-10-17-bf-sprites-research\` |
| Every LoG II key with its BF key, sizes and fit | `scripts\one-time\2026-10-17-bf-sprites-research\inventory.csv` |
| Frame sizes and opaque boxes | `scripts\one-time\2026-10-17-bf-sprites-research\metrics.json` |
| Color map per BF index | `scripts\one-time\2026-10-17-bf-sprites-research\color_report.json` |
| BF set list (290 sets) | `scripts\one-time\2026-10-17-bf-sprites-research\bf_sets.txt` |

Contact sheet key: LoG II rows (orange label) and BF rows (blue label) per dir, 4x, both drawn from the same object origin (record dx and dy, H-flip applied). Red is the 32x32 box at the usual anchor (-8, -24). Yellow is the frame's own OBJ box.
