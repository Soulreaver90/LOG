# LoG II portraits (USA, ALFE)

Date: 2026-10-17. ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Addresses are GBA addresses. "rom:0x..." is a file offset (address minus 0x08000000).

Labels: **CONFIRMED** = proved here with quoted bytes or disassembly. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.


## Result in one paragraph

Portraits use the sprite codec. Each one is a frame header `{u32 type, u32 size = 0x1000}` and a stream that unpacks to 64x64 pixels, 8 bits per pixel, in plain row order (not 8x8 tiles). One table of 115 words maps a portrait id to its header. Ids 1-7 are not table entries: id 1 is the party leader and ids 2-7 are party records 0-5, and both resolve through appearance +2. Appearance +2 is the dialog portrait (OBJ, shared OBJ palette rom:0x1DA6C8). Appearance +3 is the status screen portrait (BG, palette rom:0x1D4F50). Ids 8-25 are the 18 status portraits, ids 26-114 are dialog portraits. No portrait carries its own palette.

---

## 1. Lookup (CONFIRMED)

`portrait(id)` at 0x0800BDCC returns a frame header pointer:

```
0800bdce  cmp r0,#0x0 ; bne         ; id 0 = none
0800bdd4  ldr r1,=0x083ec9d0        ; pool rom:0xBE10 = d0 c9 3e 08
0800bdd6  cmp r0,#0x1 ; bne
0800bdda  ldr r0,[r1,#0x0]          ; word 0 = 0x03000E90 (save struct)
0800bddc  ldrb r1,[r0,#0x0] ...     ; leader record
0800bde8  bl 0x8026440              ; appearance +2 of the leader, then portrait() again
0800bdee  cmp r0,#0x7 ; bgt
0800bdf2  sub r0,#0x2 ...           ; ids 2-7 = record id-2
0800be00  bl 0x8026440
0800be06  ldr r1,=0x083ec9d0
0800be08  lsl r0,r0,#2
0800be0a  add r1,#0x4
0800be0c  ldr r0,[r1,r0]            ; id > 7: word at 0x083EC9D4 + 4 * id
```

- There is no upper bound on the id (`cmp r0,#7 ; bgt` only).
- 0x08026440 reads appearance +2: `0802644e ldrb r0,[r0,#0x2] ; bl 0x800bdcc`. Its table literal is rom:0x26458.
- Table block rom:0x3EC9D0-0x3ECB9F: word 0 `0x03000E90`, then ids 0-114 (ids 0-7 are 0). The next word, rom:0x3ECBA0, is `0x03001120`, and rom:0x3ECBA4 is an RGB table read by the fade routine at 0x0800BE14 (`ldr r4,=0x083ecba4`). So the table cannot grow in place.
- rom:0xBE10 is the only ROM word in 0x083EC9D0-0x083ECBA3 (aligned word scan of the whole ROM). A reader that computes the address another way would not appear.
- The old block stays unchanged in every build (Task 7 review). Readers at 0x0800BBB4, 0x0800B86E and 0x0800BDB8 use nearby base addresses. At 0x0800BBB4 (`ldr r1,=0x083ec9a0 ; add r1,#0x1c ; ldr r0,[r1,r0]`), an index of 5 or more reaches the block. Never free or reuse rom:0x3EC9D0-0x3ECBA3.

## 2. Format (CONFIRMED)

- Every id 8-114 has a type 1 header with size 0x1000, for example rom:0x6AF6A4 `01 00 00 00 00 10 00 00`. Each stream ends where the next header starts (id 8: 860 packed bytes, next at rom:0x6AFA08).
- The data is 64x64 linear 8bpp. All 107 decode with `webfoot_decompress.unpack_frame` and render as clean faces in row order. A 1D tile order renders noise. Render: `scripts\one-time\2026-10-16-task-7-gi-portraits\all_linear_1DA6C8.png`.
- No index 0 pixel appears in any portrait (index 0 is transparent).
- Every consumer unpacks through the dispatcher 0x0801F394 (r0 = header, r1 = destination): 0x08003A94 (status), 0x0800BB3E (dialog), 0x08018CE4 and 0x08019500 (two menu screens, ids from an object field). Type 0 copies `size` bytes from header + 8 through 0x08021DF0, an ARM memcpy that handles any alignment (`08021dfc ands r12,r0,#0x3`, `08021e28 ands r3,r1,#0x3`). So a raw type 0 portrait `{0, 0x1000, 4096 bytes}` works on all four paths.

## 3. Who reads appearance +2 and +3 (CONFIRMED)

| Reader | Byte | Use |
|---|---|---|
| 0x08026440 (`ldrb r0,[r0,#0x2]`), reached only from 0x0800BDCC ids 1-7 | +2 | Dialog speaker 1 (leader) and 2-7 (party records). Dialog unpacks at 0x0800BB3E, then copies to OBJ VRAM (`0800bb44 ldr r1,=0x06010000`, `bl 0x80236cc`) |
| 0x08003A8C (`ldrb r0,[r0,#0x3]`, table literal rom:0x3B30) in status page 0x0800379C | +3 | Status screen: HP, EP, STR, POW, END bars (STR/POW/END from player +0x160 when the record is the leader), portrait to BG VRAM 0x06006940 (`bl 0x80236b4`) |

- These are the only +2 and +3 readers. Source: the Task 3 appearance table sweep (OUT section 3, 18 literal pools and every BL to the table helpers). Both literals rom:0x26458 and rom:0x3B30 were repointed to the relocated table by `ssj2_form`.
- Dialog speaker ids 1-7 resolve through the record's current appearance. So a cutscene shows the gi portrait only when Gohan's record is in a gi entry. No ext 73 call passes set 59 (`scripts\one-time\2026-10-16-task-3-outfit-research\ext73.txt`), so entry 5 and entry 22 are reached only by the player transform. LIKELY: no cutscene dialog shows them. Raw ids > 7 skip the record: cutscene records pass 59 (armor). From r14 the `cutscene_portraits` hook maps them by Gohan's entry (`docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits-report.md`).
- The box style switch at 0x0800B25E tests the speaker id passed in (r5), not the resolved portrait id. New ids never reach it.

## 4. Palettes

| Portraits | Palette | Label | Proof |
|---|---|---|---|
| Ids 26-114 (dialog, appearance +2) | Shared OBJ palette rom:0x1DA6C8 | CONFIRMED | Dialog copies to OBJ VRAM 0x06010000. All 89 render correctly with it |
| Ids 8-25 (status, appearance +3) | rom:0x1D4F50 | CONFIRMED (render and pairing) | All 18 render correctly with it and wrongly with the OBJ palette. Each is the same drawing as a dialog portrait with indices remapped: pairs 58/9 and 60/11 agree on 4093 of 4096 pixels |
| rom:0x1D4F50 is the menu BG palette | DMA to 0x05000000 at 0x08011046 | CONFIRMED (bytes), LIKELY (that this init runs before the status page) | `08011046 ldr r1,=0x081d4f50 ; ldr r0,=0x040000d4 ; str r1,[r0] ; mov r1,#5 ; lsl r1,r1,#24 ; str r1,[r0,#4]`, then the OBJ palette to 0x05000200 |

- Status portraits use 81 indices of rom:0x1D4F50. Dialog portraits use 183 indices of the OBJ palette, and index 168 (set at run time) is among them.
- The status palette is not stored raw or as RGB triplets anywhere else, and no 512-byte compressed resource matches it (searches in `scripts\one-time\2026-10-16-task-7-gi-portraits\p5.py`, `p6.py`).

## 5. Gohan portrait ids (CONFIRMED, from the appearance table)

| Entry | Form | +2 dialog | +3 status |
|---|---|---|---|
| 0 | Demon clothes kid (set 53) | 56 | 8 |
| 1 | Kid, blue shirt (set 55) | 58 | 9 |
| 2 | Gi base, post-chamber (gi set 157; vanilla armor set 56) | 119 | 120 |
| 3 | Armor variant (set 57) | 60 | 11 |
| 4 | Rage (set 58) | 61 | 12 |
| 5 | Super Saiyan (gi set 158; vanilla set 59) | 115 | 116 |
| 22 | Super Saiyan 2 (set 159) | 117 | 118 |

Vanilla +2/+3: entry 2 `3B 0A` (59/10), entry 5 `3E 0D` (62/13), entry 22 `3D 0C` (61/12, the Rage copy). Entries 0, 1, 3 and 4 are unchanged (56/8, 58/9, 60/11, 61/12).

## 6. Reference sheet `data\reference\122601.png`

- Cells are 64x64 at x = 4 + 68 x column, y = 4 + 68 x row. Each cell includes the grey frame, as the ROM portraits do.
- Row 1 (Gohan): c0 kid white shirt, c1 kid armor, c2 kid Demon clothes with the white neck piece, c3 kid blue shirt, **c4 Super Saiyan in the purple gi**, **c5 Super Saiyan 2 in the purple gi**, c6 Super Saiyan with an orange gi. None of these drawings exists in the USA ROM (best pixel match under 2500 of 4096, `p8.py`, `p11.py`).
- The International dialog art fits the USA OBJ palette: c4 and c5 use only OBJ colors except one light green, (200,248,168).
- No cell shows teen Gohan in the gi in base form. c2 is the kid face with the neck piece I ruled out. The base gi portrait is a drawing, not a sheet cell (section 7).

## 7. Task 7 patch `gohan_portraits` (CONFIRMED bytes, LIKELY in game)

- Runs after `gohan_gi` and `ssj2_form`. In `log2_poc_r5.gba` (SHA-1 `53f6c51a9082786773f68f1cc10d0f85c9aa028f`, built with `LOG_GI_SSJ2=gi_ssj2_v2`): block rom:0x869700 (word 0 `0x03000E90`, ids 0-114 copied unchanged, ids 115-120 new); rom:0xBE10 = `00 97 86 08`. Offsets move with the size of the earlier patches' data.
- New ids, raw type 0 `{0, 0x1000, 4096 bytes}`, in `FORMS` order: 115 gi Super Saiyan dialog (rom:0x8698E8), 116 gi Super Saiyan status (rom:0x86A8F0), 117 gi Super Saiyan 2 dialog (rom:0x86B8F8), 118 gi Super Saiyan 2 status (rom:0x86C900), 119 gi base dialog (rom:0x86D908), 120 gi base status (rom:0x86E910).
- Relocated appearance table rom:0x868FAC: entry 5 +2/+3 `3E 0D` to `73 74`, entry 22 `3D 0C` to `75 76`, entry 2 `3B 0A` to `77 78`.
- Gi colors follow Piccolo's dialog portrait (id 94): body OBJ 97 (88,0,120), lit folds OBJ 233 (168,32,224), outline OBJ 1. The game pairs 97 to status 232 and 233 to status 234. OBJ 96 has no game pair and falls to a dull mauve on the status screen. A per-form recolor of the dialog art applies this rule, and the status art is derived from the recolored dialog through the game pairing. gi Super Saiyan: dialog 96 to 97. gi Super Saiyan 2: dialog 80 to 233 and 215 to 97. The base art needs no recolor.
- Base gi dialog art (entry 2) is approved drawing `art\portrait-sources\src\gi_base_dialog_src.png` (64x64 indexed, OBJ palette, SHA-1 `2bcc68315e4919f872ca9e773e1c24bdeb201ce4`). It is source art, not taken from `122601.png`, and is never regenerated. `gi_base_dialog.png` holds its indices as drawn.
- Dialog art uses only OBJ indices that USA dialog portraits use (never 0 or 168). Status art takes the game's own +2 to +3 index pairing, else the nearest status index. For (48,168,0) and (0,168,24) the per-pixel error is higher than the nearest status index, but the rule copies the game's own dialog-to-status remap (vanilla pairs vote 265 to 33 and 505 to 26) and keeps the 48/49/50 green ramp as three shades. "Nearest wins" would merge two shades in gi Super Saiyan 2, so it is not offered. Per-color errors are in `art\portrait-sources\manifest.json`.
- The review sheet is `art\portraits_review.png`: per form, new art, the vanilla armor portrait and the source.
- In-game display is not tested yet (my test).

## 8. Tools

| File | Purpose |
|---|---|
| `scripts\one-time\2026-10-16-task-7-gi-portraits\p1.py`-`p11.py` | Throwaway scans: decode, layout, palette search, pairing, sheet matching |
| `scripts\permanent\patches\gohan_portraits.py` | Task 7 patch: relocated portrait table and the new gi portraits (ids 115-120) |
