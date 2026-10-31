# Super Perfect Cell aura: art and previews, session 1 (2026-10-22)

Brief: `docs\tasks\2026-10-22-superperfect-aura\superperfect-aura.md`. Base: r29 `builds\log2_poc_r29.gba` (SHA-1 `7366217278fb7a158ca82fe1cc3d469330f78030`, checked by the script on every read). Read only on every ROM. No ROM built. Nothing changed under `scripts\permanent\` or `data\`.

Labels: **CONFIRMED** = proved here by pixels, bytes or a script check. **LIKELY** = strong evidence, not proved in game. **SPECULATIVE** = a guess.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | Answer | Where |
|---|---|---|
| Export set 30 (Cell) | 99 frames, 160 records, from r29 (set 30 is vanilla there, header `rom:0x242DBC`) | `art\cell_aura\plain\` |
| Bake Gohan-style bolts, about 2x, into every anim Cell uses in the stretch | All 10 rows (0, 1, 2, 3, 5, 6, 7, 8, 12, 18): scenes and the last fight together use every row | Section 2 |
| A Cell face rule, checked by eye | `pal:229` + `pal:248`, grown like Gohan's box. The study's `pal:209` is wrong | Section 3 |
| Three scales with the 3-shape idle flicker | 1.5x, 2x, 2.5x, same bolts at three sizes | Section 4 |
| Previews | 6 GIFs, 2 compare sheets, 1 face sheet | Section 5 |

**PENDING (mine)**

| Item | Why |
|---|---|
| Pick a scale: `scale_15`, `scale_20` or `scale_25` | Art is my call |
| Bolts on every anim, or idle and walk only | Both are possible from these folders (section 6) |
| Bolt line weight | All three scales use 1 px lines, as Gohan's do. A 2 px glow is an option if the bolts read thin on Cell |

---

## 2. Anims covered (CONFIRMED)

The study lists the stretch: NPC Cell in the scenes, enemy type 25 in the last fight (attacks 5-8, 12, 18; hurt 2, 3), and the 14,4 NPC. Together they use every row of set 30, so every row gets bolts.

| Anim | Records per dir | Bolts |
|---|---|---|
| 0 idle | 2 in set 30, **6** in the new folders (index = body x 3 + shape) | One pattern per (dir, shape), on both bodies |
| 1 walk, 2, 3 hurt and knockdown, 5-8 attacks, 12 flying, 18 ki blast | as set 30 (4, 4, 4, 3, 4, 4, 4, 4, 7) | One pattern per distinct source PNG |

- Dir 3 records reuse the dir 2 PNGs with the H-flip bit, so their bolts mirror dir 2. The check confirms it for every dir 3 key.
- Every frame stays 64x64, the single OBJ maximum. Bolts clip at the frame edge.

---

## 3. The face rule (CONFIRMED by pixels and by eye)

**Rule:** take the bounding box of the `pal:229` and `pal:248` pixels, then grow it 3 px each side, 5 rows up and 3 rows down. No bolt pixel lands in that box. On back views (dir 1) no face shows, so the box is empty.

| Index | What it is | Evidence |
|---|---|---|
| `pal:229` (120,32,120) | The purple face stripes | In every distinct frame that shows the face (front, side, blink, knockdown, flying), always a tight cluster (at most 7 x 4 px). Never elsewhere |
| `pal:248` (224,96,168) | The iris, beside `pal:2` sclera | Absent in the blink frames (0.0.1, 0.2.1) and the anim 3 frames, so it cannot be the only anchor |
| `pal:209` (224,208,248) | Pale highlight: mouth, but also hands, knees and plates | Per frame bbox reaches y48. **The study's SPECULATIVE 209 is refuted** |

- Pixel dump of idle dir 0, rows 21-25: `229 10 1 42 1 10 229` (brow), `229 2 248 209 248 2 229` (eyes), mouth and jaw below. The grown box covers x26-38, y16-27 there.
- Check sheet: `archive\2026-10-18-art-review-renders\cell_aura\face_check.png` (every distinct dir 0-2 frame, face box in red).
- Script check: 0 bolt pixels inside the face box in all three folders.

---

## 4. The three scales (CONFIRMED by `cell_aura_check.txt`)

**Method:** `gi_aura.outline()` family. Each frame gets 3-4 bolts (Gohan: 2-3 on a body 1.8x smaller). Each bolt starts on the transparent ring around Cell's body and runs a jagged trunk (`gi_aura.walk`) to a tip up to 5 x 6 units away, plus one branch of 3 units. The path is made in Gohan units, scaled, and joined with 1 px lines. White core `pal:2` on every third trunk pixel, glow `pal:191`. White over a bright body pixel turns 191.

- Seeds leave the scale out, so the three folders hold the **same bolts at three sizes**.
- Bolts do not start on the white swoosh arcs of anims 6-8.

| Folder | Scale | Frames | Keys | Raw bytes | Reach past body: median / max | Errors |
|---|---|---|---|---|---|---|
| `art\cell_aura\scale_15\` | 1.5x | 109 | 176 | 447,336 | 5 / 13 px | 0 |
| `art\cell_aura\scale_20\` | 2x | 109 | 176 | 447,336 | 7 / 15 px | 0 |
| `art\cell_aura\scale_25\` | 2.5x | 109 | 176 | 447,336 | 8 / 17 px | 0 |
| Gohan `set:159` / `set:160` (study) | 1x | - | - | - | 2-3 / 8 px | - |

Each folder passes: key set equals set 30 with anim 0 expanded to 6 per dir; every attr shape matches 64x64; every changed pixel is 2 or 191; no change in the face box; dir 3 flips the dir 2 PNG.

---

## 5. Previews for me

All in `archive\2026-10-18-art-review-renders\cell_aura\`.

| File | What |
|---|---|
| `cell_aura_scale_15_dark.gif`, `_light.gif` | 1.5x. Rows: idle (with flicker), walk, attack 6. Columns: dirs 0, 1, 2. 4x zoom |
| `cell_aura_scale_20_dark.gif`, `_light.gif` | 2x, same layout |
| `cell_aura_scale_25_dark.gif`, `_light.gif` | 2.5x, same layout |
| `compare_dark.png`, `compare_light.png` | Plain Cell next to the three scales, 9 sample frames, 3x |
| `face_check.png` | The face rule on every distinct dir 0-2 frame |

- Idle timing copies the `ssj2_idle` hook at 60 Hz: shape `(tick >> 3) % 3` (133 ms each), body 1 (blink) while `(tick & 0xFF) > 0xF0`. One loop is 768 ticks (12.8 s).
- Walk and attack timing is **approximate** (8 ticks a frame). The game's per-anim timing was not read.
- The white core fades on the light background. That shows how it reads on bright maps.

---

## 6. What session 2 needs

1. **Art folder:** my pick, `art\cell_aura\scale_NN\`. The manifest is the grouped shape that `patches.gohan_gi.art_records` reads (`[{png, w, h, keys: [{anim, dir, index, dx, dy, w, h, attr0, attr1}]}]`), so `records, frames = art_records("cell_aura/scale_NN")` then `build_set(rom, 0x242DBC, records, frames, alloc, counts={0: 6})` builds set 58. CONFIRMED by a dry run into an in-memory r29 copy (nothing written): all three folders build. Read back, the 176 keys equal the manifest keys, every geometry field matches, and every frame's tiles equal the PNG tiles (0 mismatches, `aura_work\dryrun_build.py`). Extra fields (`header`, `source`, `aura`) are for review only.
   - **Manifest shape (my reading of the brief):** the brief says "the `log2_sprites` format". The only manifest `log2_sprites` writes is the flat `export_set` list (one row per record), which no build step reads. I wrote the grouped shape instead, because `gohan_gi.art_records` (the build path session 2 calls) reads it. The flat export is in `aura_work\set30_export\manifest.json` if needed.
2. **Idle and walk only** (if I pick that): take anim 0 and 1 keys from the scale folder and every other key from `art\cell_aura\plain\` (same key schema, plain set 30 PNGs).
3. **Without the hook:** the vanilla tick stores body 0 or 1 as the index. Keep idle index 0 as index 0 and index 3 as index 1 (body 0 and 1, shape 0), and use `counts={0: 2}`. The bolts then stand still.
4. **Slot:** every frame is 64 x 64 = 0x1000 bytes, equal to set 30's slot, so `build_set` accepts it. About 447 KB of raw type 0 frames.
5. **Hook:** set 30's anim table is at header + 0x4C, the same `ANIM0_ROW` the `ssj2_idle` hook tests (CONFIRMED, `read_set` on r29). The chained hook needs only Cell's new header address.
6. **Test 3 restated:** the study's "body pixels unchanged" cannot hold, because bolts cross the body as Gohan's do. Use "every changed pixel is 2 or 191 and outside the Cell face box" (the check in `cell_aura.py`).
7. **Bible rows:** `scripts\one-time\2026-10-22-superperfect-study\aura_bible_rows.md` (5 rows, tag SPC) waits for review and merge into `docs\RE-BIBLE.md`.

---

## 7. Concerns

1. **Bolts cross the body.** At 2x and 2.5x some bolts run over the chest and legs (for example idle dir 2). This is Gohan's family (start on the ring, random direction), but on Cell the longer bolts cover more body. I judge.
2. **Thin lines.** The bolts are 1 px at every scale, so a 2.5x bolt is longer, not thicker. Cell is 1.8x Gohan's size, so the bolts read thinner relative to him.
3. **Anim 18 hold freezes the bolts.** Five records (18.x.2-6) share one PNG, so the bolts stand still during the ki blast hold.
4. **Reach is 2-3x Gohan's** (median 5-8 against 2-3 px). That is the "bumped up in size" ask, but the 64x64 frame clips bolts at its edge: on wide attack frames, and above the head, where idle has only 6 px of room against a 17 px max reach at 2.5x. Look for flat cut-offs at the top edge.
5. **Not seen in game.** Previews emulate the hook timing. Walk and attack timing is approximate.
6. **Brief deviation:** one early read-only Bash call started with `cd ... ; true` (no effect). All other calls used absolute paths.

---

## 8. Files

- Script: `scripts\one-time\2026-10-22-superperfect-study\cell_aura.py` (`all` = export, bake, check, preview).
- Check output: `scripts\one-time\2026-10-22-superperfect-study\cell_aura_check.txt`.
- Work files: `scripts\one-time\2026-10-22-superperfect-study\aura_work\` (set 30 export, `face_scan.py`, `zoom.py`, `dryrun_build.py`, zoom sheets).
- Art: `art\cell_aura\plain\`, `scale_15\`, `scale_20\`, `scale_25\`.
- Previews: `archive\2026-10-18-art-review-renders\cell_aura\`.
- Bible rows: `scripts\one-time\2026-10-22-superperfect-study\aura_bible_rows.md`.
