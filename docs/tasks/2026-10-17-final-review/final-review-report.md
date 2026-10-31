# Slice 1 final whole-branch review

Date: 2026-10-17. Read only.
Subject: `builds\log2_poc.gba`, SHA-1 `345ae98c1145f669d936cad62cad8635467f3824` (I recomputed it). Base ROM SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b` (unchanged).
Method: byte reads of the final ROM and the base ROM with `py -3 -I`, `thumb_dis.py` listings, an independent Thumb decode for the gate, and the script decoder `scripts\one-time\2026-10-18-save-slots\sdis.py`. I did not re-run the suite. Scratch scripts are in a scratch folder outside the project, not in the project.

## Deliberate exceptions (do not "fix" these)

1. `rom:0x42F0` points at `rom:0x800000`, an unchanged copy of the vanilla appearance table (22 entries, original +1 values 56 and 59). It does not see sets 157-159 or entry 22. This is by design (re-outfit.md section 6 item 3, re-forms.md section 7 item 2).
2. The reverse lookup `0x080042BC` keeps its `cmp r2,#0x16` bound (22 entries).
3. Rage: appearance entry 4 (`03 3A 3D 0C 02 02`, form object `0x030021E4`) and set 58 stay vanilla (Global Constraints, Ruling 31).
4. The original table at `rom:0x1D967C` still holds the gohan_gi edits (`rom:0x1D96A5` = 0x9D, `rom:0x1D96E1` = 0x9E). After ssj2_form no literal points at it: a scan of every byte offset of the final ROM finds 0 words equal to 0x081D967C and 0 words in 0x081D967D-0x081D9833. Ruling 14 carries the edits into the relocated table.
5. Entry 2 keeps the armor portraits `3B 0A` (no teen gi base cell in 122601.png; my question open).
6. Cutscene and NPC Gohan stay in armor in slice 1 (final decisions 2026-10-16, deferred to the next slice).
7. The shared Super Saiyan tick pool `0x080174A0` is untouched. The ability 12 action is shared by four Saiyans; the gate passes every entry except 5 to the vanilla action.
8. Set 159 uses the set 59 layout (Rulings 13, 18). 16 frames (anim 11) are larger than their source record (16x32 to 32x32), inside the 1024-byte slot (Ruling 35).

## Strengths

- Every patch checks every site against its old bytes before it writes anything. All three fail before the first write on a wrong order.
- The base 8 MB diff matches the plan exactly: 25 runs, all mapped (check 4).
- New code enters only through absolute pointers and leaves through `bx` tail calls. My independent decode of the 28 gate instructions matches `thumb_dis.py` and the test's expected text.
- The tests build their own ROMs (Ruling 2 holds). Each module writes its own file under `scratch\test-roms\`.
- The docs carry addresses that I could check. Every expansion offset in RE-BIBLE lines 155 and 196 matches the final ROM.

## Cross-task checks

### Check 1: reverse lookup inputs (no Critical found)

- Callers of `0x080042BC` in the final 16 MB, by three shapes: Thumb BL at any halfword (3: `0x08005CB2`, `0x08005CBC`, `0x0800A948`), B or Bcc within range (0), pointer words 0x080042BC or 0x080042BD (0).
- `0x08005CB2` and `0x08005CBC` pass constants: `mov r1,#0x35` (53) and `mov r1,#0x80` (128).
- `0x0800A948` (ext 73) passes the script argument r6 unchanged.
- Every decodable ext 73 call in the story scripts pushes a constant: 53, 55, 56, 58, 128, 129, 132, 137 or 138 (`scripts\one-time\2026-10-16-task-3-outfit-research\ext73.txt`).
- The 8 ambiguous hits in the script region are not script code. CONFIRMED by bytes:
  - `0x083D112E` and `0x083DB0DA` follow text strings ("...a robot?", "...rval form.") and the bytes `03 00 02 49 E9/E5`, a text record header.
  - `0x083D86BE` and `0x083C0682` follow an `end`.
  - `0x083B9FCE`, `0x083CBEBE`, `0x083DB46A` and `0x083DF312` decode as `push 0 ; push 0 ; push 0 ; ext 73` or follow a `jz` over nothing.
  - In all 8 the next op is invalid (233 or 229). A real `ext 73 (0, 0)` would hang vanilla too, because no entry has +1 = 0.
- The hits at `0x0842F318` and above were not decoded one by one. The data-flow argument below closes them.
- A run-time set id of 157-159 has one possible source: appearance +1. I listed every `ldrb ..,#0x1]` in the 60 instructions after each of the 23 table `ldr` sites (9 reads). Seven go straight into `get_set` (`ldrb r0,[r0,#0x1] ; bl 0x8009324` at `0x08001ADA`, `0x08008624`, `0x0800C5CE`, `0x08010C4E`, `0x080111E4`, `0x08014D9C`, `0x0802646A`). `get_set` returns a set pointer, not an id. The other two read other structs: `0x08001906` reads a map record (r4 = `0x08409410`), and `0x0800C626` reads `[r6+8]` after the entry was consumed.
- No second reverse-lookup routine exists in `0x0-0x30000`: the only `cmp #0x15-0x17` near a table read is `0x080042D6`.
- Save, map load, menus and transform store the appearance index (record +8), never a set id. The save keeps record +8 (re-save-format.md, record +0x08).
- Result: no input to `0x080042BC` can be 157, 158 or 159. CONFIRMED for the shapes above. A script that computes a set id with arithmetic would not appear; vanilla scripts have no reason to make 157-159.

### Check 2: appearance index bounds for entry 22 (no defect found)

- Shape A: `cmp rX,#0x15/#0x16/#0x17` in `0x0-0x30000`: 13 sites. Only `0x080042D6` is near a table read. The rest are message ids, tile loops (`0x08019D1E`, `0x08019E36`) or data.
- Shape B: `mov rX,#0x15/#0x16`: 22 sites. None compares an appearance index.
- Shape C: every record +8 read found by two address shapes (`ldrb [..,#0x8]`, and `ldrb [..,#0x14]` after the x28 stride) that scales by 20 adds the relocated table base (`0x088637AC`). No parallel table indexed by the appearance index appears.
- No word at any byte offset points into the old table body (my scan of the final ROM; Task 4 did the same on the base, re-forms.md:229).
- ARM code: the existing IWRAM listing `scripts\one-time\2026-10-16-first-probes\dis_iwram.txt` has no table literal and no 22 bound. I did not check its coverage.
- Load path for a saved 22: `0x08003ED4` reads the relocated table (literal `rom:0x414C`). A transformed non-leader goes to +5 = 2. A leader in 22 loads with `get_set(159)` at map load (`0x0800C5C4` literal to `0x0800C5CE`). Entry 22 is at `rom:0x8637AC + 22 * 20`, inside the 23-entry table.
- Residual: a reader that builds the table address from another base with an added constant would not appear (same caveat as re-forms.md section 8).

### Check 3: patch order and hand-offs (holds)

- `gohan_gi` writes `alloc.notes["gohan_gi"]` = appearance_copy, set_table, set_157, set_158, set_159. `ssj2_form` reads appearance_copy and set_159. `gohan_portraits` reads `notes["ssj2_form"]["table"]`. The keys match.
- Wrong orders: `ssj2_form` first raises `KeyError('gohan_gi')`. `gohan_portraits` before `ssj2_form` raises `KeyError('ssj2_form')`. Both are the first statement of `apply`, so nothing is written. `log2_build.build` writes the output file only after every patch returns.
- Duplicates fail closed: gohan_gi on `rom:0x42F0`, ssj2_form on the 17 literals, gohan_portraits on `rom:0xBE10`.
- ssj2_form checks entry 5 = `01 9E 3E 0D 04 02` and entry 2 +1 = 157, so it cannot run on a ROM without the gi edits.
- gohan_portraits checks entry 2 +2 = `3B 0A`, entry 5 = `3E 0D` and entry 22 = `3D 0C` in the relocated table.

### Check 4: base 8 MB map (no unlisted change)

25 changed runs. Each 4-byte word shows 3 changed bytes because the 0x08 top byte is the same.

| rom | Old | New | Task | Ruling or source |
|---|---|---|---|---|
| 17 literals: 0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050, 0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474 | 0x081D967C | 0x088637AC | 6 | re-forms.md 7 item 1, Ruling 14 |
| 0x42F0 | 0x081D967C | 0x08800000 | 5 | re-outfit.md 6 item 3 |
| 0x959C | 0x083B4E90 | 0x08863548 | 5 | Ruling 18 |
| 0x1D96A5 | 0x38 | 0x9D (157) | 5 | re-outfit.md 6 item 1 (now unread, exception 4) |
| 0x1D96E1 | 0x3B | 0x9E (158) | 5 | re-outfit.md 6 item 2 (now unread, exception 4) |
| 0x1D99CC | 0x0801353D | 0x08863E5F (gate) | 6 | re-forms.md 7 item 5, Rulings 10, 15, 16 |
| 0x8E8C | 0x081D9900 | 0x08863E99 (HUD) | 6 | re-forms.md 7 item 6, Ruling 12 |
| 0x8D14-0x8D1D | `4019007e00014618b168` | `281c19f008f8011c07e0` | 6 | re-forms.md 7 item 7 |
| 0xBE10 | 0x083EC9D0 | 0x08863F00 | 7 | re-portraits.md |

- Each repointed literal has the `ldr` sites the docs name: 23 for the 17 table literals plus 1 for `0x42F0` (24 in all, as re-outfit.md:70), 1 each for `0x959C` and `0x8E8C`, and 2 for `0xBE10`. Shape: Thumb pc-relative `ldr` in `0x0-0x30000`.
- `0x08021D2A` is `bx r1`, so the HUD hook's `bl` reaches the new routine through r1.

### Check 5: 1024-byte VRAM slot (holds)

- Sets 157, 158 and 159: header u16 +0 = 0x400. The largest record is w*h = 1024. 0 OBJ shape or size mismatches, 0 decode mismatches. All headers, record lists and frame headers are 4-aligned.
- All 23 appearance entries resolve to sets with slot 0x400. So every player object gets a 0x400 slot, whichever character built it.
- The transform `0x08014D58` stores only obj+0x48 and does not reallocate (RE-BIBLE, T5P2 line). So 157 to 158 to 159 and back keeps a valid slot.

### Check 6: Global Constraints (hold)

- OBJ palette `rom:0x1DA6C8` (0x200 bytes): equal to the base.
- Save format: no new field. A new value can appear: record +8 = 22 if a save is made in Super Saiyan 2. The patched ROM loads it (check 2). See Declined.
- Rage: entry 4, set 58, form object and portraits `3D 0C` are equal to the base.
- `data\`: no file newer than the Task 1 brief. Base ROM SHA-1 unchanged. `log2_build.py:35` refuses output under `data\`.
- Size 16777216 bytes. The last non-0xFF byte is `rom:0x8680FF`. 0xFF fills the rest.
- No CR bytes in the scripts, patches, tests or docs I checked.

### Check 7: tests across tasks (no hidden dependency)

- Each test module builds its own ROM: `test\gi.gba`, `test\ssj2.gba`, `test\portraits.gba`, plus the build tests. No test reads a file that another test writes. Ruling 2 holds.
- The inputs in `art\` (gi PNGs, portraits, Z2 icons) come from tools, not from tests.
- Shared author: `thumb_dis.py`, the encoder in `ssj2_form.py`, `EXPECTED` and the `read_form` regexes in `test_ssj2.py` are all Task 6 work. Mitigations: the Ghidra import of the Task 6 ROM (`scripts\one-time\2026-10-16-task-6-ssj2\ghidra_t6.txt`) covers the new routines. Task 7 did not move the code (`test_new_data_only_in_free_expansion`). My own decoder agrees on the gate. Residual risk is a shared wrong idea about meaning, not about encoding.
- See Minor 6 for a coverage gap on the final ROM.

### Check 8: docs drift (Minor 1-5, Important 1-2)

Listed under Issues.

## Issues

### Critical

None.

### Important

1. **Acceptance test text promises behavior the build does not have.** `docs\design\2026-10-16-log-merge-design.md` section 8.3:
   - Test 3 says "lightning aura". Task 6 found that Rage has no aura object (RE-BIBLE line 194). The build has blue spark pixels in the set 159 frames only.
   - Test 6 says "Gohan comes out in the gi" at the Time Chamber exit. The ruled behavior is armor in that cutscene. The gi shows from the next time the player picks Gohan (re-outfit.md section 6 "Effects", design 6.6).
   - Why: I may record a false failure in Task 8, the same class as the Task 6 cooldown finding.
   - Blocking: test 3 is in Task 8 Step 2 (tests 1-5), so it is the live risk. Test 6 is outside Task 8; it is a design doc fix.
   - Fix: amend 8.3 tests 3 and 6 before the play test. Tell I what "lightning" looks like (spark pixels in some animations).
2. **Design 8.2 D drops a requirement with no note.** It says Rage "keeps its current stats ... Only its art changes to the gi", and "the existing Rage lightning aura".
   - Global Constraints, Ruling 31 and the build keep set 58 (armor Rage). In the Cell fight, gi Gohan turns into armored Rage, then armor again after Cell (re-outfit.md line 158).
   - Why: this is visible in the main fight. It is a design requirement that a ruling replaced silently.
   - Blocking: no. The post-Cell test save never enters the Cell fight. It is an open item for me.
   - Fix: add a superseding note to 8.2 D (Rage art stays armor in slice 1, deferred with the cutscenes). Add a backlog line. Ask I.

### Minor

1. `docs\research\re-sprite-decompression.md:153`, `:158`, `:159`, `:162` and the table at `:180` still read set header +1 as a direction count. Ruling 35 disproved this (RE-BIBLE has a superseded mark; this doc does not). Fix: add a superseded note.
2. `docs\research\re-outfit.md`:
   - `:11` says the "second literal" (`0x959C`) prevents the ext 73 hang. The hang guard is `0x42F0`. `0x959C` gives ids 157-159 table words.
   - `:31` "Not traced: Task 4 and Task 6 must settle it" is settled by re-forms.md section 2, last paragraph.
   - Section 8 questions 1 and 2 are answered by me (Ruling 8 answer).
   - Fix: mark each one answered.
3. `docs\RE-BIBLE.md:224` (C, since base-T1): "set at script `@0x083EC67B`, then load Capsule Corp". The SETFLAG is at `0x083EC6A2` (`00 C3 02 1B`, the only byte-push `push 195 ; SETFLAG` in the ROM), after the ext 35 load at `0x083EC690`. `log2_save.py:73` and re-save-format.md:126 have it right. Fix: correct the line.
4. `docs\RE-BIBLE.md:153` (C) lists entry 5 portraits 62/13 and entry 22 61/12. Task 7 changed them to 115/116 and 117/118 (line 155). Fix: mark it as the pre-T7 state.
5. `docs\design\plans\2026-10-16-slice1-poc-plan.md` Tasks 5 and 6 have no inline notes for later rulings:
   - `make_gi_base` and `make_gi_form` (Ruling 36: `make_gi_set`, `form_layout`).
   - "Start from set 53" (Ruling 27).
   - "follows 58 where 58 has the frame" (Rulings 13, 18).
   - "Rage lightning aura" (Rulings 19, 31).
   - `test_gi_frames_keep_record_sizes` (Rulings 30, 35).
   - The ledger has them; the plan does not. Fix: one "Superseded by Ruling N" line per item.
6. Review Focus 1 on the final ROM is only covered transitively.
   - `test_gi.py:212` reads the hard-coded `0x1D967C` on the gohan_gi-only ROM. On the final ROM those bytes are unread, so the test would still pass if the relocation dropped the edit.
   - Today `test_ssj2 test_relocated_table_copies_live_table` plus `test_portraits test_other_entries_unchanged` close the gap.
   - Fix: add one test on the three-patch build. It resolves entries 2, 5 and 22 through a code literal (for example `rom:0xC804`, map load) and `rom:0x959C` to `set_157`, `set_158` and `set_159`.
7. `ssj2_form.py:340` and `gohan_portraits.py:202` fail on a wrong order with a bare `KeyError`. The failure is loud and comes before any write, but the message is terse. Fix: raise `ValueError("run gohan_gi first")` and `ValueError("run ssj2_form first")`.
8. `docs\build-log.md` has no "Task 5" section. The Task 5 build lines sit under "Task 2". The final three-patch build line sits under "Task 6". This is cosmetic.

## Declined to judge

- Art quality of the gi frames and portraits: my art gate decides (Rulings 22-33). Open my items: the SSJ2 lying hair tuft and the gi portrait color.
- The voluntary revert from Super Saiyan when flag 195 is set and EP >= 10: Ruling 10 as approved. It is an open my question (progress.md line 109).
- The stacked transform cooldown after SSJ to SSJ2: already handled by the Task 6 review fix round.
- END 120 near the damage ceiling: my information already relayed (progress.md line 70).
- Saves made in Super Saiyan 2 (record +8 = 22) loaded in an unpatched ROM: the plan protects only old saves loading in the new ROM.
- Vanilla data words equal to 0x08800000 (25 or more, from `rom:0x1DE784`) now point at the appearance copy, not past the ROM end. They look like data, not pointers. Ruling 4 accepted the expansion. I did not trace them.
- Whether a save point allows saving while transformed: vanilla behavior, the same for SSJ and SSJ2.
- The missing teen gi base portrait: an open my question.

## Recommendations

1. Before Task 8, apply Important 1 (test text) and tell me about Important 2 (Rage art).
2. Run acceptance test 4 (East District 439 to the world map) on `log2_poc.gba` itself. My anti-piracy test used a ROM with 0xFF in the whole expansion. The final ROM has data in `rom:0x800000-0x8680FF`.
3. Fix Minor 1-5 in one doc pass. Add the Minor 6 end-to-end test in the next code round.

## Assessment

**Ready for my play test: With fixes.** I found no Critical defect: no hang path into the reverse lookup, no bound on entry 22, and every base 8 MB change maps to a task and a ruling. The one fix before the play test is the test 3 text (Important 1); the Rage art (Important 2) does not block it and goes to me as a decision.
