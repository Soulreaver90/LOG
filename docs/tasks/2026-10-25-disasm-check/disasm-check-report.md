# Disasm check report: 9374b08 to 075b23c

Study only. Source tag `DS8`.

The disasm clone `GitHub\legacyofgoku2-disasm` is at `075b23c` and was read only. The proof listing is `scripts\one-time\2026-10-25-disasm-check\disasm_check.txt` (sections A to J), made by `disasm_check.py` in the same folder. The bible rows are in `scripts\one-time\2026-10-25-disasm-check\bible_rows.md`.

Labels: **C** = CONFIRMED (bytes or listing quoted), **L** = LIKELY, **S** = SPECULATIVE.

> [!IMPORTANT]
> The disasm "transform slot descriptors" are **sound entries**, not forms. All 34 rows sit on the SFX table grid or the music sample directory grid (C). In form code, the only new disasm rows are run-time block labels and the ext and setter label-word runs. They add no field and no meaning to the form, cooldown or `relay_cooldown` rows (C by one intersection shape, `disasm_check.txt` J).

---

## SHIPPED and PENDING

| Ask (brief) | Status | Where |
|---|---|---|
| 1. Conflicts first, both sides quoted, bytes checked | SHIPPED | "Conflicts" below; `disasm_check.txt` A-I |
| 2. Facts that touch live work (FRM, FCD, CJT, CJ2, VSJ, BMS, BFP) | SHIPPED | "Live-work impact" below |
| 3. New names, short table, no bible rename | SHIPPED | "New names" below |
| 4. Tools worth reusing, no code copied | SHIPPED | "Tools" below |
| 5. Bible rows (tag DS8) as `## Section N` blocks with merge notes | SHIPPED | `bible_rows.md`: 9 merge notes, 27 rows, 3 open questions |
| Tests (global rule) | SHIPPED | 744 tests, OK (I changed no permanent file) |

| Pending | My action |
|---|---|
| Merge the DS8 rows and the 9 merge notes into `docs\RE-BIBLE.md` | My merge; add `DS8` to the source list |
| `symbols.py` names nothing at `0x086F8E40` (scouter database) or `0x081D9C80` (journal category words), so `listing.py` prints `stat_bar_frame+0x7a4` and `ability_table+0x380` there | A later task; this study could not edit `scripts\permanent\` |
| Codemap misses the IWRAM mixer `0x03000520` and the ARM code at `0x08022C10`, `0x0802493C`, `0x080251A0` | A later codemap task |
| Three open questions (sound flag bits, ext 19 and 21, 504 dispatch rows) | Section 13 rows |
| The EFX report line 57 says "18 frames of `visited_table`"; the bytes give 16 | My fix in `docs\tasks\2026-10-20-effects-trace\effects-trace-report.md` (read only for this study) |

> [!WARNING]
> **Process slip.** One early command began with `cd /tmp 2>/dev/null;`. The brief forbids `cd` in any shell. The command only read the base ROM, and every later command used absolute paths.

---

## Conflicts

Each line quotes the disasm side and the bible side, and says which side the ROM bytes support. Labels are mine.

| # | Disasm says | Bible says | Bytes support | Label |
|---|---|---|---|---|
| 1 | `TRANSFORM_SLOTS.md`: "the transform slot descriptors ... the clip range ... the step"; CHANGELOG: "a RAM colour-transform slot whose descriptor pointer names one of 34 ROM records" | OVW 1079: "Sound effects `@0x080E15B0`, 12-byte `{PCM pointer, u32, u16 length, u16 rate}`"; DCR 1121 and TRV 1123: sample directory `0x0814A8A4`, 12 B | **Bible.** 8 rows sit at `0x080E15B0` + 12n (entries 6, 9, 13, 14, 37, 38, 48, 49), 26 at `0x0814A8A4` + 12n, 0 off grid. `sound_start` `@0x0801FCB2` `str r1,[r0,#0x28]` stores the entry that the initialiser reads at `@0x0801FA1A` `ldr r2,[r0,#0x28]` | C |
| 2 | `IWRAM_COPY_CALLERS.md`: "The IWRAM copy family ... a copy routine ... `ldrsb` ... `mla`" | DIS 1084: "10 ARM functions from `@0x03000000` to `@0x03000BAC`"; no row names `0x03000520` | **Neither fully.** The routine is the sound mixer: 22 `ldrsb` and 21 `mla` in `0x03000520`-`0x03000703`, `ldr r5,[r1] ; mla r5,r6,r0,r5 ; str r5,[r1],#4` at `0x0300054C`. Our codemap stops at `0x03000520` (`0x03000480`, size 160) and has no start there | C |
| 3 | `table_086f6d8c.py`: record `reserved_00_13`, "no reader found" | EFX 781: area map reads record +0x00 (BG frame), +0x08 count, +0x0C icon list, +0x10 OBJ frame | **Bible** on the readers: `@0x08017ACC` loads record +0x00 (`@0x08017D16`, `@0x08017D24` then `bl frame_unpack`), +0x08 (`@0x08017D4C` `ldr r1,[r0,#0x8] ; cmp r1,#0 ; beq`) and +0x10 (`@0x08017D60`). **Neither** on the count: EFX says "(18 records)" and "The 18 OBJ frames", the bytes give 16 (EFX's own `e12_areamap.txt`: 16 uploads, 52 skips) | C |
| 4 | `text/LAYOUT.md`: roster `reserved_0c_0f`, "no reader found" | SPC 395 and R31 1134: scouter entry +0xC = portrait id | **Bible.** `@0x080194F4` `ldr r0,[r7,#0xc]` then `bl 0x0800BDCC` (`portrait`); the byte is at most 0x72 in all 128 rows | C |
| 5 | `records/LAYOUT.md`: quest record `reserved_00_03`, "no reader found" | SAV 623: "`{u32 category, done script, active script, text}`" | **Bible.** `@0x08004AD6` `ldrb r1,[r5,#0x0]`, then `ldr r2,=0x081D9C80 ; lsl r1,r1,#2 ; ldr r1,[r2,r1]`. The disasm's own `text/LAYOUT.md` cites the same read | C |
| 6 | `addr/LAYOUT.md`: "`0x083B5C00` 68 B (the opcode dispatch table)" | SAV 603: "30 base ops at `@0x083B5C00`" | **Bible.** 30 words; word 17 is 0, so the label run breaks there. The second run is 12 words at `0x083B5C48` | C |
| 7 | `addr/LAYOUT.md`: "`0x08009220` (the opcode `0x03` sub-table)" for `0x083B5F70` | FCD 558: "A second per-op table `0x083B5F70` (+0x248) is called after the handler", example `@0x08009224` | **Disasm, and CJR 1202.** `0x083B5F70` is the setter table (17 code words). `@0x08009224` is base op 26 (word 26 = `0x08009225`), a get-and-set op. The plain ext call is op 2 `@0x08008F8E`, which calls no setter | C (listings), L (op 26 = dec) |
| 8 | `FUNCTION_BOUNDS.csv`: 822 start, 427 unreferenced, 1,252 fragment, 930 dispatch | DPT 897: "1,094 function starts (770 `start`, 324 `unreferenced`) plus 1,353 `fragment`; 857 starts equal codemap starts" | **Disasm** (the DPT counts are from `1da4ef2`). Now 938 of 1,249 starts equal a codemap start | C |
| 9 | `NAMING.md`: a `dispatch` row is an entry point "no call, vector, table or prologue limb reaches" | No bible row | **Neither.** 764 of the 768 non-start dispatch rows lie inside codemap bodies, and 260 follow a BL (return points, for example `0x080012AA` after `bl frame_unpack`) | C (counts), L (meaning) |

---

## Live-work impact

New facts by live item. "Raises" means a label can go up; "risk" means a plan should change.

### Forms and party cooldown (FRM, FCD, `relay_cooldown`)

- **No impact.** The "transform slot" family is sound (conflict 1). I intersected the 375 addresses in FRM, FCD, CJT, CJ2, VSJ, BMS and BFP rows with every new disasm row (`disasm_check.txt` J). The only data-row hits are the ext table run and the setter run (7 cited words). Dispatch rows sit inside `form_base_tick` `@0x08017028` (13 rows), `hud_draw` `@0x08008BEE` (18) and `ability_cycle` `@0x08008B88` (6). These are run-time block labels. No new row names a field of the form objects, the cooldown `0x03000E98`, the ability table `rom:0x1D9900` or the player state table `0x083B5278`. C (intersection, one shape: address inside a row extent).
- **Confirms** the `relay_cooldown` hook site. `rom:0x3B5E40` = ext 70 (`(0x083B5E40 - 0x083B5D28) / 4 = 70`), and the word is `0x0800A785` in base and in r39. C (`disasm_check.txt` C).
- **Confirms** the FCD hook rule for the call path that matters. Op 2 reads `[0x083B5D28 + 4n]` from ROM on each call (`@0x08008F9C` `ldr r1,[r2,r1]`), with no RAM copy and no bound. C (listing).
- **Small note, no risk.** Ops 21-26 also call an ext word, as the getter of var n, and then the setter n. The setter table has only 17 entries, so n stays at 16 or below, and ext 70 is never a getter. L (17 setters, C; no script uses n > 16, not swept).
- **Correction** to the FCD 558 wording (merge note 3). Its conclusion stands.

### Script ext ops (CJT, CJ2, VSJ, BMS)

- **Confirms** the operand widths that `celljr_fight` and its stack-model test use. The disasm pins each base op handler to its bytes: op 19 skips one offset byte, op 21 takes one byte, op 15 takes none, op 0 one byte, op 1 a varint. C (`opcode_stream.py` `HANDLERS`; bible rows already C).
- **Confirms** the zigzag push rule (AUR 613). The disasm varint is raw: `74` is raw 116 = 58, `82 40` is raw 320 = 160. C (`disasm_check.txt` D).
- **Confirms** the ext table bound: 145 words (ext 0-144). Every ext op the live trials use (up to ext 142) is inside it. C.
- **Risk for the beam struggle design (BMS).** A new ext op has no free slot in place. Word 145 is `0x03000E90` (its reader is not traced), and ext 146 and higher would read setter words. A new op needs a relocated table and both pool words that name it, `rom:0x921C` and `rom:0x92DC`. C (words), L (no room in place; only two names).
- **VSJ.** The vanilla transform sounds 55 and 23 (`ext 46`) are SFX entries of the same table. The disasm rows hold no entry 55 or 23 (its run-time routes did not play them), so nothing changes. C.
- **Nothing raised** from L or S in CJT, CJ2, VSJ or BMS. The new disasm decodes only the 86 journal streams, not the scene scripts.

### Text storage (BFP `chapter_cards`, `named_supplies`)

- **`chapter_cards`: confirms** the font layout (SGR 429, OVW 1081): 256 u16 offsets, 221 glyphs, advance = width + 1, unchanged in r39. C.
- **`chapter_cards`: new precondition.** The journal builds a text canvas this way: `@0x08020E5C(canvas, 0xD0, 0x58)`, `menu_font` at +0xC (`@0x08004A74`), shadow byte +0x28 = 1, `glyph_draw` `0x08020EC3` at +0x20 (`@0x08004A80`). A chapter card canvas needs the same setup before `text_draw`. C (listing).
- **`named_supplies`: no new fact.** The UI string table `0x080E2840` is in the disasm raw extent `0x0E2840..0x1D5150` (`DATA_CENSUS.md`). No disasm text family covers it. C.
- **Trap.** The disasm "roster" table is the scouter database. Its CSV is base only: `roster_019` already differs in r39 (the R35 edit). C.

---

## New names

The disasm name files did not change in this range (`git diff --stat 9374b08..075b23c` of `names.csv`, `ram.csv` and `NAMING_LEDGER.csv` is empty). The table gives disasm labels for addresses the bible cites without a name. Rows marked **Do not adopt** carry a wrong meaning.

| Address | Disasm label | Bible today | Note | Label |
|---|---|---|---|---|
| `0x08003C6E` | `Counter_StepRandom` | "stat gain helper" (BFP 450) | | C (name file text, bible text) |
| `0x08003D58` | `Character_AwardXp` | ext 139 target, "EXP += n" | | C (name file text, bible text) |
| `0x080040AA` | `Object_SetActive` | ext 86 HUD toggle helper | | C (name file text, bible text) |
| `0x080050C8` | `Map_LoadLayer` | "BG tile loader" (BMS 801) | | C (name file text, bible text) |
| `0x08006152` | `Scene_BuildLayers` | copies BLDCNT to map view (BMS 798) | | C (name file text, bible text) |
| `0x08006274` | `Display_ClearControlBit` | ext 24 BG layer off (BMS 753) | | C (name file text, bible text) |
| `0x0800AC10` | `Character_SetLevel` | ext 98 handler | | C (name file text, bible text) |
| `0x0800AFF0` | `Character_AwardXpToActive` | ext 139 handler | | C (name file text, bible text) |
| `0x0800B4AE` / `0x0800B4FC` | `Object_Register` / `Object_Unregister` | "scene setup" / "scene cleanup" | Meaning differs; bible is from listings | L (disasm meaning not verified) |
| `0x0800D138` | `List_NewNode` | NPC step controller (CJ2 792) | Meaning differs | L (disasm meaning not verified) |
| `0x080104C0` | `Sprite_NewSpan` | boss HP bar object | Meaning differs | L (disasm meaning not verified) |
| `0x0801F412` | `Dma3_CopyChunks` | "chunked DMA3" (EFX 1112) | | C (name file text, bible text) |
| `0x0801F7FC` | `Text_MeasureLine` | "line counter" (R35 1146) | | C (name file text, bible text) |
| `0x08020E5C` | `Surface_New` | "Canvas" ctor (EFX 1112) | | C (name file text, bible text) |
| `0x08021F18` | `__16__rt_memset` | "= memset(dst, byte, n)" | | C (name file text, bible text) |
| `0x08021F30` | `__16__rt_sdiv` | HUD divide | | C (name file text, bible text) |
| `0x03001FAC` | `Opcode_OperandPointer` | VM vars 4-7 pointer (CJR 1202) | | C (name file text, bible text) |
| `0x086F6D8C` | "state table" (`table_086f6d8c.py`) | `visited_table` | **Do not adopt:** clashes with the player state table `0x083B5278` | C (bytes, conflicts 1, 2, 6) |
| `0x080E15B0` + 12n, `0x0814A8A4` + 12n | `slot_000`-`slot_033`, "transform slot" | sound entry, sample directory | **Do not adopt:** sound, not forms | C (bytes, conflicts 1, 2, 6) |
| `0x03000520` | "IWRAM copy routine" | none | **Do not adopt:** it is the sound mixer | C (bytes, conflicts 1, 2, 6) |
| `0x083B5F70` | "opcode `0x03` sub-table" | setter table (CJR 1202) | Agrees | C (name file text, bible text) |
| `0x086D68DC` | `quest_record`, `objective` | journal quest table (SAV 623) | Agrees | C (name file text, bible text) |
| `0x086F8E40` | `roster` | scouter database | Agrees on layout except +0xC (conflict 4) | C (name file text, bible text) |

---

## Tools

None of these tools can read our builds. Each one reads `baserom.gba` and refuses any image whose sha256 is not the retail one (for example `transform_slots.py` line 15 `ROM_SHA256 = "6e6c370c..."`, `iwram_seed.py` line 28 "this image has sha256 %s"). Their CSVs are useful base-ROM reference data.

| Disasm tool | What it does | Our tool it could replace | Verdict | Label |
|---|---|---|---|---|
| `tools\records\opcode_rows.py` (+ `instruction.csv`) | Decodes the 86 journal streams with the pinned op grammar | Part of `extscan.py` (OUT), `sweep.py`, `extcalls.py` (PGS) | **No.** It decodes the journal streams only, its varint is raw (halve it), and it cannot read r39. Use its `HANDLERS` table as a cross-check for our decoders | C (source read), L (verdict) |
| `tools\text\text_rows.py` (+ 4 CSVs) | Reads the scouter database, its strings, the journal texts and the font offsets | The ad hoc scouter readers in R31, R33, R35 studies; part of `text_fit.py` input | **Reference only.** Base only; `text_fit.py` models wrapping, which this does not | C (source read), L (verdict) |
| `tools\records\table_086f6d8c.py` (+ 4 CSVs) | Reads `visited_table`: header, 68 records, 297 entries `{zone, area, bit}` | `e12_areamap.py` (EFX), the SS3 visited-bit lookup | **Reference only.** `entry.csv` is a ready map-to-visited-bit list | C (source read), L (verdict) |
| `tools\records\transform_slots.py` (+ `slot.csv`) | Reads 34 sound entries | None (TRV audio tool transcription covers more) | **No.** 34 of at least 157 entries, misnamed | C (source read), L (verdict) |
| `tools\addr\addr_runs.py` (+ `run.csv`) | Lists 822 runs of label-word tables | `listing.py --refs`, `ptrscan.py` (DIS) | **Reference only.** Good for finding code-pointer tables in base | C (source read), L (verdict) |
| `tools\recomp\iwram_seed.py` | Writes an IWRAM snapshot for a recompiler | None | **No.** No use for the hack | C (source read), L (verdict) |
| `FUNCTION_BOUNDS.csv`, `RUNTIME_LABELS.csv` | Census rows; run-time entries | `symbols.py check`, codemap cross-checks | **Cross-check only.** Do not import `dispatch` rows as starts (conflict 9) | C (source read), L (verdict) |

---

## Method and evidence

- Grid, bytes and r39 equality for the 34 slot rows: `disasm_check.txt` A.
- IWRAM words, `mla` and `ldrsb` counts, codemap IWRAM starts: section B.
- VM table words, ext and setter bounds, `relay_cooldown` word, address runs: section C.
- Varint and zigzag test, journal stream opcodes: section D. I reimplemented the varint rule from `opcode_stream.varint` and did not import clone code.
- Visited table header, bits 294-296, record counts: sections E and I.
- Text tables against r39, census row at `0x28920`: section F.
- Function bounds against the codemap, named addresses: sections G and H.
- Live-work intersection (375 cited addresses against every new disasm row and the dispatch rows): section J.
- Area map record readers: listing of `0x08017ACC`.
- Listings by `scripts\permanent\disasm\listing.py`: `0x0801F9D6`, `0x0801FC9C`, `0x0801FD22`, `0x0801FD38`, `0x08008F8E`, `0x08009224`, `0x080040EE`, `0x080049FC`, `0x08019320`, `0x08020A4C`.
- Tests: `py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent`: "Ran 744 tests in 317.025s", "OK".
