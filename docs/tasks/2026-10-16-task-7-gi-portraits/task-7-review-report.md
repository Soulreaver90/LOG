# Task 7 review: gi portraits

Read only. Base `base-T7` to live. ROMs checked: `log2_poc.gba` SHA-1 `345ae98c1145f669d936cad62cad8635467f3824`, `log2_poc_t6.gba` SHA-1 `86ae697b9b061480bbe3ffebab6e2b63b8e0a524`, base `18e0715dec419f3501c301511530d2edcd590f8b` (all three re-hashed, match). Scripts: scratchpad `t7rev\c1.py`-`c8.py`, `py -3 -I`.

### Spec Compliance

Pass, with one documented deviation that the dispatch allows (entry 2, check 6).

- Step 1 CONFIRMED in this run: yes. I re-read `portrait()` at 0x0800BDCC and the dispatcher 0x0801F394. Type 0 goes to `ldr r2,[r2,#0x4] ; bl 0x8021df0`, a copy of `size` bytes from header + 8.
- Step 2: gi Super Saiyan (row 1 c4) and gi Super Saiyan 2 (row 1 c5) are converted, each in a dialog and a status version. Final approval is pending, as the brief says.
- Step 3: the patch exists. The build is logged in `docs\build-log.md` (02:24 line and the Task 7 section). The SHA-1 matches the file.
- Dispatch tests: all four are present in `scripts\permanent\tests\test_portraits.py`. "Entry 2 holds a new id" is replaced by `test_gi_base_keeps_armor_portraits`, per the "do not invent one" rule.
- Review sheet `art\portraits_review.png`: present, 4x, new / armor / source per row.
- Headers, LF, no BOM, no em or en dashes: checked on the 7 new or changed files.

Cannot verify (read only, no emulator):
- In-game display of 115-118 on the status screen and in dialog.
- What the menu consumers 0x08018C8A (`ldr r0,[r4,#0x8] ; ldr r0,[r0,#0xc]`) and 0x080194F6 (`ldr r0,[r7,#0xc]`) pass. Any id they pass resolves inside `portrait()`, so a new id cannot read past a table there. Only a palette mismatch is possible, and that is vanilla behavior.
- A +2/+3 reader my sweep shape in check 2 misses (see the limit there).

#### The six named checks

1. **Check "old table references".**
   - Literal: an aligned scan of the base 8 MB finds one word into rom:0x3EC9D0-0x3ECBA3, at rom:0xBE10. An unaligned scan adds rom:0x290361 and rom:0x559577. Both are unaligned and inside data, so neither is a literal pool word.
   - PC-relative: both `ldr r1,=` in `portrait()` (0x0800BDD4, 0x0800BE06) use the one pool word. In the built ROM, both decode as `ldr r1,=0x08863f00`. No ARM `ldr [pc]` within 4 KB reaches the block.
   - Thumb-shaped `ldr [pc]` halfwords that reach the block: 5, at rom:0x3EC66A, 0x3EC97A, 0x3ECA48, 0x3ECA4C and 0x3ECB44. Three of them (0x3ECA48, 0x3ECA4C, 0x3ECB44) lie inside the block itself. The other two lie in the script pointer table and script data before it. None is code.
   - BL-shaped pairs into rom:0x3EC000-0x3ECBFF: 2, at rom:0x10535A (to rom:0x3ECB52) and rom:0x647FF2 (to rom:0x3EC660). Both targets are the middle of a pointer or data table (0x3ECB52 is inside the portrait block), so neither pair is a real call. No odd (Thumb entry) word points into the region.
   - Base plus offset: these readers use addresses next to the block, and the implementer did not list them. 0x0800BBB4 runs `ldr r1,=0x083ec9a0 ; lsl r0,r0,#2 ; add r1,#0x1c ; ldr r0,[r1,r0]`. That is a table at 0x083EC9BC with an index from `[sp,#0x38]`. An index of 5 or more lands in the block. 0x0800B86E reads a byte table at 0x083EC9B0 with a loop counter. 0x0800BDB8 runs `ldr r0,=0x083ec9cc ; ldr r0,[r0,#0x0]`. None of them reads a portrait id. All are harmless, because the old block stays byte-identical in `log2_poc.gba` (verified rom:0x3EC9D0-0x3ECBA3).
   - Copy: the new block rom:0x863F00 equals base rom:0x3EC9D0 for 4 + 4 x 115 bytes. Word 0 is `0x03000E90`.
   - Bound: the only compares in `portrait()` are `cmp r0,#0x0`, `#0x1` and `#0x7` (`bgt`). There is no compare against 115 and no length.
2. **Check "id width and parallel tables".**
   - Sweep of `log2_poc.gba`: 18 aligned words equal `0x088637AC` (the 17 Task 6 code literals plus the gate pool rom:0x863EE8). 0 words equal the vanilla `0x081D967C`. rom:0x42F0 holds `0x08800000` (the gohan_gi copy). That value also appears in 64 data words, and only the rom:0x42F0 pool has a code user (0x080042BE).
   - For each pool I took every `ldr rX,=` user and disassembled 12 instructions. Only two `ldrb ...,#0x2` or `#0x3` reads appear: `0802644e ldrb r0,[r0,#0x2]` and `08003a8c ldrb r0,[r0,#0x3]`. This matches the Task 3 list.
   - Limit of this shape: a reader that keeps the table address and reads +2 more than 12 instructions later, or uses a register offset, would not appear. A reader of the vanilla or gi-copy table sees the old ids and shows the armor, which is fail safe.
   - Both readers use r0 only as the `bl 0x800bdcc` argument. The status caller passes the returned header to `0x801f394`, and 0x08026440 returns the header. The resolved id never leaves `portrait()`, so nothing indexes a name or palette table by it. Byte width is fine for 118.
   - `portrait()` callers: 0x08003A8E, 0x0800B2B2 (raw speaker id from the script), 0x08018C8A, 0x080194F6 and 0x08026450.
3. **Check "palettes and color mapping".**
   - rom:0x1D4F50 (512 bytes) and rom:0x1DA6C8 (512 bytes) equal base in `log2_poc.gba`.
   - New pixel indices: 115 and 117 use only indices that USA dialog portraits 26-114 use. 116 and 118 use only indices that status portraits 8-25 use. None uses 0 or 168. All four decode to their PNGs byte for byte.
   - The two greens are not a defect. The game itself remaps them that way. In the 18 vanilla +2/+3 pairs, dialog 49 (48,168,0) goes to status 108 on 265 pixels against 33 for 106. Dialog 57 (0,168,24) goes to 108 on 505 against 26. Dialog 50 (16,120,0) goes to 106 on 313.
   - The rule keeps the dialog ramp 48/49/50 as three status shades (112/108/106). "Nearest" would put 49 and 50 both on 106. Both occur in gi_ssj2 (54 and 6 pixels), so one shade would be lost. See Minor 1.
4. **Check "8 MB diff and expansion diff".** I compared `log2_poc.gba` with `log2_poc_t6.gba` over all 16 MB. The changes are:
   - rom:0xBE10-0xBE12: 3 bytes, `d0c93e08` to `003f8608`.
   - rom:0x863812-0x863813: entry 5 +2/+3, `3e 0d` to `73 74`.
   - rom:0x863966-0x863967: entry 22 +2/+3, `3d 0c` to `75 76`.
   - rom:0x863F00-0x8680FF: the block plus four 0x1008-byte frames at 0x8640E0, 0x8650E8, 0x8660F0 and 0x8670F8. All are 4-aligned, type 0, size 0x1000.
   - Nothing else changes. Entries 2 and 4 are unchanged.
5. **Check "fail closed and tests".**
   - Before the first write, `apply` checks the literal, word 0, the end word at rom:0x3ECBA0, both table literals, the entry 2, 5 and 22 bytes, and the art indices.
   - `test_apply_fails_closed` corrupts 7 sites and asserts that the ROM is untouched.
   - A wrong id fails `test_entries_point_at_new_ids` and `test_other_entries_unchanged`.
   - A wrong pixel fails `test_new_ids_decode_to_the_pngs` and `test_pngs_reproduce_from_reference`.
   - A moved or damaged table fails `test_relocated_block_keeps_struct_word_and_old_ids`, `test_every_old_id_decodes_unchanged` and `test_base_8mb_differs_only_at_portrait_literal`.
6. **Check "entry 2 decision".** Consistent with the dispatch. I viewed row 1 c1-c5 at 4x. c1 is kid armor. c2 is the kid with the white neck piece, which I ruled out. c3 is the kid in armor colors. c4 and c5 are teen Super Saiyan and Super Saiyan 2 in the gi. No teen gi base cell exists. The implementer kept `3B 0A`, tested it, and gave me options.

### Strengths

- The old block stays in place, unchanged. This is the strongest mitigation against an unseen reader, even though the docs do not say so.
- Status art follows the game's own dialog-to-status pairing, with a vote threshold. This is better than a blind nearest match.
- The tests read the table and entries from the ROM literals, not from the patch notes. A patch that writes correct notes but wrong bytes still fails.
- The art regenerates byte for byte from the reference, so the PNGs cannot drift away from the converter.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. `docs\tasks\2026-10-16-task-7-gi-portraits\task-7-report.md:58` (concern 2) and `docs\research\re-portraits.md:93`.
   - What: they say the game-pair rule gives a worse color, and they offer "let the nearest color win".
   - Why: the vote data in check 3 shows that the rule copies the game's own remap. "Nearest" would merge two shades in gi_ssj2. I could pick the worse option because of this text.
   - Fix: reword both lines. The per-pixel error is higher, but the rule keeps the game's ramp. Remove the "nearest wins" option, or label it "loses a shade".
2. `docs\research\re-portraits.md:38` and `docs\RE-BIBLE.md:146`.
   - What: they record the limit of the literal scan. They do not record the base-plus-offset readers next to the block (0x0800BBB4, 0x0800B86E, 0x0800BDB8). They also do not state the mitigation: the old block stays byte-identical.
   - Why: a later task that reuses or clears rom:0x3EC9D0 would break those readers silently.
   - Fix: add this text to both: "The old block stays unchanged. Readers at 0x0800BBB4, 0x0800B86E and 0x0800BDB8 use nearby base addresses. At 0x0800BBB4, an index of 5 or more reaches the block. Never free or reuse rom:0x3EC9D0-0x3ECBA3."
3. My review note, no code change.
   - What: the source gi Super Saiyan cell has a light green background (593 pixels, mapped to OBJ (168,232,168)). The USA Super Saiyan armor portrait 62 uses pale yellow (248,248,184).
   - Why: this is source art, and the review sheet shows it, but the report does not name it.
   - Fix: add it to my checklist next to the gi hue (concern 3).

### Assessment

Task quality: **Approved**. The patch, the build and the tests match the dispatch, and every named risk checks out at the byte level. The two Minor doc items can go into the next edit of those files.
