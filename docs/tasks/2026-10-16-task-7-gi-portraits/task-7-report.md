# Task 7 report: gi portraits

Status: **DONE_WITH_CONCERNS**

I review it and approves the art.

## Summary

- Step 1 reached CONFIRMED in this run. Portraits use the sprite codec: 64x64, 8bpp, row order, one table of 115 ids. Full detail: `docs\research\re-portraits.md`.
- Step 2: two gi portraits come from `data\reference\122601.png`, each in a dialog and a status version (4 new ids). The sheet has no gi base portrait for teen Gohan, so entry 2 keeps the armor portraits.
- Step 3: `scripts\permanent\patches\gohan_portraits.py` builds `builds\log2_poc.gba` = gohan_gi + ssj2_form + gohan_portraits, SHA-1 `345ae98c1145f669d936cad62cad8635467f3824`.
- Tests: 74 OK (15 new in `scripts\permanent\tests\test_portraits.py`).

## CONFIRMED facts (quotes)

1. **Lookup.** `portrait(id)` at 0x0800BDCC: `cmp r0,#0x0` (none), `cmp r0,#0x1` (leader, then `bl 0x8026440` = appearance +2), `cmp r0,#0x7 ; bgt` (ids 2-7 = party records through +2), else `ldr r1,=0x083ec9d0 ; lsl r0,r0,#2 ; add r1,#0x4 ; ldr r0,[r1,r0]`. No upper bound on the id.
2. **Table.** Pool rom:0xBE10 = `d0 c9 3e 08`. Block rom:0x3EC9D0: word 0 `0x03000E90` (read for ids 1-7), then ids 0-114 (0-7 are 0). rom:0x3ECBA0 = `0x03001120`, and 0x083ECBA4 is the fade routine's RGB table (`0800be1c ldr r4,=0x083ecba4`). An aligned scan of the whole ROM finds rom:0xBE10 as the only word that points into the block.
3. **Format.** rom:0x6AF6A4 `01 00 00 00 00 10 00 00` (type 1, 0x1000 bytes). All 107 portraits decode to 64x64 and render as clean faces in row order. Tile order renders noise.
4. **Unpack.** The four consumers all call 0x0801F394 (r0 = header, r1 = destination): 0x08003A94, 0x0800BB3E, 0x08018CE4, 0x08019500. Type 0 copies through 0x08021DF0, an ARM memcpy that handles any alignment (`08021dfc ands r12,r0,#0x3`, `08021e28 ands r3,r1,#0x3`).
5. **+2 = dialog.** `0802644e ldrb r0,[r0,#0x2] ; bl 0x800bdcc`. The dialog copies to OBJ VRAM (`0800bb44 ldr r1,=0x06010000`, `bl 0x80236cc`), so it uses the shared OBJ palette rom:0x1DA6C8.
6. **+3 = status screen.** `08003a8c ldrb r0,[r0,#0x3] ; bl 0x800bdcc ; ... bl 0x801f394`, in the status page 0x0800379C (HP, EP, STR, POW and END bars). It draws to BG VRAM 0x06006940.
7. **Status palette.** Status ids 8-25 render correctly with rom:0x1D4F50 and wrongly with the OBJ palette. Each one is the same drawing as its dialog pair with the indices remapped: pairs 58/9 and 60/11 agree on 4093 of 4096 pixels. rom:0x1D4F50 is DMA'd to BG palette RAM at 0x08011046 (`ldr r1,=0x081d4f50 ; ldr r0,=0x040000d4 ; str r1,[r0] ; mov r1,#5 ; lsl r1,r1,#24 ; str r1,[r0,#4]`). LIKELY: that init runs before the status page (not traced).
8. **Gohan ids (+2/+3).** Entry 2 armor 59/10, entry 4 Rage 61/12, entry 5 Super Saiyan 62/13, entry 22 (Task 6) 61/12.
9. **Patch bytes in log2_poc.gba.** rom:0xBE10 = `00 3F 86 08`. Block rom:0x863F00 has word 0 `0x03000E90`, then ids 0-114 byte-identical to the original. New raw portraits: 115 at rom:0x8640E0, 116 at rom:0x8650E8, 117 at rom:0x8660F0, 118 at rom:0x8670F8. Relocated appearance table rom:0x8637AC: entry 5 `01 9e 73 74 16 02`, entry 22 `01 9f 75 76 02 02`, entry 2 `00 9d 3b 0a 05 05` (unchanged).

## Source tiles (122601.png, cell x = 4 + 68 x col, y = 4 + 68 x row)

| New id | Use | Source | How sure |
|---|---|---|---|
| 115 / 116 | Entry 5, gi Super Saiyan (dialog / status) | Row 1, column 4: teen Super Saiyan Gohan with a purple gi shoulder | High |
| 117 / 118 | Entry 22, gi Super Saiyan 2 (dialog / status) | Row 1, column 5: spiky hair with one bang, angry, purple gi | LIKELY Super Saiyan 2. It could be the International Rage portrait, but it shows the same gi either way |
| none | Entry 2, gi base | No cell fits. Row 1 columns 0-3 are kid Gohan. Column 2 is the kid Demon clothes with the white neck piece, which I ruled out | Checked all 59 left-grid cells against the USA portraits (`scripts\one-time\2026-10-16-task-7-gi-portraits\p11.py`) and by eye |

- None of these International drawings exists in the USA ROM (best match under 2500 of 4096 pixels).
- **Dialog versions:** each color maps to an OBJ index that a USA dialog portrait already uses, never 0 or 168. Every color is exact except a light green, (200,248,168), with error 1280 (sum of squared RGB).
- **Status versions:** each dialog index takes the status index the game pairs it with (18 appearance pairs, at least 4 pixels). Otherwise it takes the nearest index that status portraits use. The worst errors are dark greens, 5952 on 6 and 54 pixels, and a purple, 4800 on 68 pixels (gi Super Saiyan). All errors are in `art\portrait-sources\manifest.json`.
- Review sheet: `art\portraits_review.png`. Each row shows the new portrait at 4x, the armor portrait it replaces, and the source cell.
- No palette is written.

## Tests (74 OK, 15 new)

- Each new id decodes from the built ROM, through rom:0xBE10, to its PNG (type 0, 0x1000 bytes, 4-aligned).
- Ids 8-114 decode the same as before the patch. The block keeps word 0 and ids 0-114 byte for byte.
- Entries 5 and 22 hold the new ids and held `3E 0D` and `3D 0C` before. Entry 2 keeps `3B 0A`. No other entry changes.
- `apply` fails closed with the ROM untouched on 7 broken sites, on an art index 0 or 168, and on an index outside the portrait colors. It also fails without ssj2_form.
- In the base 8 MB, the only change from the gohan_gi + ssj2_form build is at rom:0xBE10. The expansion changes only in the new block, the new frames and the 4 entry bytes. Both palettes are unchanged.
- The PNGs regenerate from 122601.png byte for byte. The file build equals the in-memory build.

## Files

- New: `scripts\permanent\patches\gohan_portraits.py`, `scripts\permanent\tests\test_portraits.py`, `docs\research\re-portraits.md`, `art\portrait-sources\` (4 PNGs, manifest.json), `art\portraits_review.png`, throwaway scans `scripts\one-time\2026-10-16-task-7-gi-portraits\`.
- Changed: `docs\RE-BIBLE.md` (section 5a with 11 lines, source docs POR and T7, open row answered; backup `scripts\one-time\2026-10-16-task-7-gi-portraits\RE-BIBLE.before-t7.md`), `docs\build-log.md` (Task 7 section).
- `builds\log2_poc.gba` is rebuilt with all three patches. The Task 6 ROM is kept as `builds\log2_poc_t6.gba` (SHA-1 `86ae697b9b061480bbe3ffebab6e2b63b8e0a524`). The other ROMs are not touched.

## Concerns

1. **Entry 2 (gi base) still shows the armor portraits.** The dispatch test "entry 2 holds a new id" is not met. "Do not invent" took priority. My options: (a) accept the armor portrait in base form; (b) use the kid Demon clothes cell with the neck piece; (c) approve a hand-made edit.
2. **Status colors.** Greens and one purple shift in the status versions. The palette is not the only cause. For (48,168,0) the game-pair rule gives error 5952, but the nearest status index gives 4416 (59 pixels). For (0,168,24) it gives 4224 against 2688. Only (16,120,0) has no closer color. Review note (me, 2026-10-17): the rule copies the game's own dialog-to-status remap and keeps three green shades; "nearest wins" would merge two of them, so it is withdrawn. My look: the gi Super Saiyan source cell has a light green background, where the USA armor Super Saiyan portrait uses pale yellow.
3. **Gi hue.** The International gi is blue-violet (48,16,168). The gi sprites use the Piccolo purple `pal:88`/`pal:89`. The art stays as ripped until I decide.
4. **Not tested in game.** These facts are LIKELY until I check them: the status screen palette order; the two menu consumers (0x08018C8A, 0x080194F6), which take ids from an object field that was not traced; and that no cutscene dialog shows Gohan while his record is in entry 5 or 22. No ext 73 call passes set 59.
5. **My test.** Use the post-Cell save, transform to Super Saiyan and to Super Saiyan 2, then open the status screen and start a dialog with Gohan speaking.
