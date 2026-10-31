# Status screen gold bonus: report (slice 2, tasks 2, 3, 5, 4)

Date: 2026-10-18. Brief: `docs\tasks\2026-10-17-status-gold\status-gold.md`.

Labels: **CONFIRMED** = proved here with bytes, a test or quoted code. **LIKELY** = strong evidence, not proved in game. **SPECULATIVE** = a guess.

## Status

| Item | Result |
|---|---|
| Tasks 2, 3, 5, 4 (relocation, Europe lookup, item reapply, gold on a 125 scale) | Built in `status_bonus`, tested in the interpreter, not played in game |
| Check ROM | `archive\builds\log2_poc_r9.gba`, SHA-1 `f61fd3b7c978d12dc7e05b1ba5723c4bf238bcc7` |
| Save state | `archive\builds\log2_poc_r9.ss1` (copy of `log2_poc_r7.ss1`, see concern 1) |
| Tests | 140 OK (113 before, 27 new in `test_status.py`) |
| Mock | `scripts\one-time\2026-10-17-status-screen-research\mock_status_gold.png` (not game output) |
| r9 against r8 | Equal except the veneer site, the 3 item sites and the new data (CONFIRMED, section 6) |

---

## 1. Changes

| File | Lines | Change |
|---|---|---|
| `scripts\permanent\patches\status_bonus.py` | new, 307 lines | Header 1-23. Constants 29-47 (`ITEM_SITES` 38, `GOLD_ROWS` 45, `BONUS_TEXT` 46). Stub, splice and new Thumb code 49-196 (`find_player` 69, `width` 84, `stats` 96). Helpers 200-243 (`gold_image` 211, `page_bls` 216). `apply` 246-307 |
| `scripts\permanent\tests\test_status.py` | new, 524 lines | 27 tests. Readers 99-150, `PageCpu` 153, page runner 180-245, tests 248-511 |
| `scripts\permanent\patches\ssj2_form.py` | 7, 297-337, 354-368 | The shared assembler gets formats 13 (`add/sub sp`), 12 (`add rd,sp`), 11 (`ldr/str [sp]`), 7 (`[rb,ro]`), a general format 5 `mov` and `bx` with high registers, and branch targets from symbols. Old encodings do not change: the in-memory build before `status_bonus` equals r8 byte for byte (CONFIRMED, `r9_diff.py` line 1) |
| `docs\research\research-status-screen.md` | 3, 192-203, 211-216, 232-234, 241-288 | Intro, a status column for section 5, decisions 1, 2 and the new 6, files, new section 8 (what is built) |
| `docs\RE-BIBLE.md` | 27, 190-197, 402 | `SGR` source, 8 rows in section 5b, 1 open question |
| `docs\build-log.md` | last 2 lines | Build line (written by the tool) and the annotated line |
| `scripts\one-time\2026-10-17-status-screen-research\mock_status.py`, `r9_diff.py`, `listing_check.py` | new | Mock, the r8/r9 proof and the listing proof (throwaway) |
| `archive\builds\log2_poc_r9.gba`, `log2_poc_r9.ss1` | new | Check ROM and its save state |

---

## 2. Addresses (r9)

| Part | Address | Label |
|---|---|---|
| Entry veneer | `@0x0800379C`-`@0x080037AB`: `push {r7} ; ldr r7,=0x0886F93D ; mov r12,r7 ; pop {r7} ; bx r12`, pool word at +12 | CONFIRMED (`test_entry_veneer_bytes`: bytes `80b4024fbc4680bc60470000` + word) |
| find_player veneer | `@0x080037AC`-`@0x080037BB`, same shape, target `0x08870065` | CONFIRMED |
| Relocated page | `rom:0x86F93C`-`rom:0x86FCE3` (0x3A8 bytes, 4-aligned) | CONFIRMED |
| Long-call stubs | 18 x 16 bytes, `rom:0x86FCE4`-`rom:0x86FE03` | CONFIRMED |
| Bonus format `"%d+%d"` | `rom:0x86FE04` | CONFIRMED |
| Gold image | `rom:0x86FE0C`, 600 bytes | CONFIRMED |
| Code | `rom:0x870064` find_player, `rom:0x870080` width, `rom:0x870092` stats, pool to `rom:0x87017B` | CONFIRMED |
| Item sites | `@0x0800F4AA`, `@0x0800F512`, `@0x0800F57A`: `bl 0x80037ac` | CONFIRMED (`test_item_sites_call_find_player_stub`) |
| +3 portrait literal the game reads | `rom:0x86FCD0` (copy pool). `rom:0x3B30` is dead | CONFIRMED (`test_relocated_page_integrity`) |

### 2.1 Relocation proof (task 2)

- The vanilla page has 42 BLs to 17 base targets. Evidence: `test_old_page_bls_counted`, decoded with `thumb_dis` from `0x0800379C` to `0x08003AFD`. CONFIRMED.
- Each BL in the copy goes to a stub whose `ldr r7,=` names the vanilla target. Every other instruction is byte-equal and decodes to the same text, so each `ldr =` literal and `add rX,pc` string agrees. The pool `0x08003AFE`-`0x08003B43` is byte-equal (with the ssj2 table word). Evidence: `test_relocated_page_integrity`. CONFIRMED.
- Against the listing `scripts\one-time\2026-10-17-status-screen-research\status_usa_379c.txt` (`listing_check.py`, run on the r9 file): outside the splice, "BL targets equal through stubs: 33; ldr = values equal: 18; add pc strings equal: 4". The one difference is `('0x8003a82', 'ldr r1,=0x081d967c', 'ldr r1,=0x08868fac')`: the +3 portrait literal holds the relocated appearance table from `ssj2_form` (RE-BIBLE row "relocated appearance table `rom:0x868FAC`"). CONFIRMED.
- No computed branch exists in the page. Its only exits are BLs and `pop {r4,r5,r6,r7,pc}` at `0x08003AFC`. The only caller is `0x08003B5E bl 0x800379c`: the test tries every halfword in `0x08000000`-`0x0802FFFF` as a BL prefix, so a misaligned decode cannot hide a caller. No ROM word points into `0x0800379C`-`0x080037BB`. After the patch the callers are `0x08003B5E` and the 3 item sites. Evidence: `test_only_one_caller_enters_the_veneer_site`. CONFIRMED.
- Behavior: the interpreter runs the vanilla page and the patched page (through the veneer and every stub) with all base calls stubbed. The call traces are equal, call for call and argument for argument, except the three bar widths, which follow the 125 scale. Evidence: `test_page_trace_matches_vanilla_without_bonus`. CONFIRMED in the interpreter, LIKELY in game.
- Stubs keep r0-r7, sp and lr. Evidence: `test_stubs_keep_registers` runs all 18. CONFIRMED.
- Stage 1 (copy without the splice) is proved by these tests. No separate stage-1 ROM was built (concern 4).

### 2.2 Splice

The stat rows `0x08003902`-`0x08003A1B` become, at copy +0x166:

```
ldr r0,[sp,#0xd8] ; ldr r1,[r0,#0x0] ; add r0,sp,#0x9c ; bl stats ; mov r6,#0x57 ; add r7,sp,#0x9c ; b copy+0x280
```

The rest of the rows is zero. The page reads r4 (record), r5 (bar image), r6 = 0x57 and r7 = canvas after the rows (`0x08003A1C add r0,r5,#0 ; bl 0x801f110`, `0x08003A3C str r6,[sp,#0xa4]`). No branch outside the rows lands inside them (`test_no_branch_enters_the_splice`). CONFIRMED.

---

## 3. Bar formula

`w = min(v, 125) / 5 * 3` (integer). The Thumb routine `width` subtracts 5 and adds 3 until 75 px. Base part = vanilla image columns 0 to w(base). Gold part = gold image columns w(base) to w(live), drawn only when w(live) > w(base). Source pointer = gold + w(base), so the 2-on, 1-off segment pattern stays in phase.

| v | 0 | 4 | 5 | 99 | 100 | 120 | 125 | 126 | 127 |
|---|---|---|---|---|---|---|---|---|---|
| px | 0 | 0 | 3 | 57 | 60 | 72 | 75 | 75 | 75 |

CONFIRMED: `test_bar_width_formula` runs the page for each value and reads the blit rect.

---

## 4. Number text

- **Recommended and built: "100+20"** (`BONUS_TEXT = "split"`, format `"%d+%d"`, base then bonus). Without a bonus the vanilla "100/100" stays.
- Why: it shows the trained base and the form bonus, as the bar does (base part, gold part). It has no "/100", which a 125 scale would contradict. "120/100" reads like an error (mine).
- Alternative: "120" (`BONUS_TEXT = "live"`, format `"%d"`). Both are in the mock. `test_text_mode_live` builds and runs it.
- Font and color: vanilla (the page font `@0x08028724`, canvas +0x29 = 2, +0x28 = 1, right-aligned at x 136). The font has a '+' glyph, 3 px wide (column data `0x100, 0x380, 0x100`). CONFIRMED.
- Box: width = sum of (glyph width + 1) (`0x0801F66A add r0,r3,r0 ; add r0,#0x1`). "100/100" = 34 px, "100+20" = 28 px. No "base+bonus" text for base 0-100 and live to 255 is wider than 34 px (`test_bonus_text_fits_the_vanilla_box`). CONFIRMED.

---

## 5. Gold choice

| Option | Rows (menu palette index) | Min CIE76 delta E to any bar color |
|---|---|---|
| Draft | 82 x6, 69 x2 | 15.4 (82 against 40 (248,184,0)) |
| Flat pale | 69 x8 | 31.3 (against 89 (248,216,0)) |
| **Built** | 58, 69 x4, 34 x3 | 29.9 (34 against 40) |

- The built rows give a light top, a gold body and a bronze foot. The vanilla bar is flat per segment, so the vertical shading separates gold from the yellow middle and from the orange start.
- Flat 69 has a slightly higher minimum (31.3) but reads as pale yellow next to index 8 (248,248,0) in the candidate strip. I chose the shaded rows. This is a judgment for me to confirm.
- No palette entry changes. Indices 58 (248,248,168), 69 (248,232,120), 34 (200,160,64) are in `rom:0x1D4F50` (CONFIRMED, `test_palette_unchanged`, `test_gold_image`).
- Mock: `scripts\one-time\2026-10-17-status-screen-research\mock_status_gold.png`. It runs the built page code in the test interpreter and paints the traced texts, fills and blits with the ROM font, bar art and menu palette. Columns: USA vanilla, r9 "100+20", the "120" option. Rows: base 100, Super Saiyan, Super Saiyan 2, mid base (yellow), Gohan 3/5/3 in Super Saiyan, Rage on a low base. Background (191, 255, 7). It is not game output.

---

## 6. Build and diff

- Command: `py -3 -I scripts\permanent\log2_build.py --out archive\builds\log2_poc_r9.gba gohan_gi ssj2_form gohan_portraits status_bonus` (no env vars).
- SHA-1 `f61fd3b7c978d12dc7e05b1ba5723c4bf238bcc7`. r8 is unchanged (`5662dc0224bd5d6e4697d93069e59d9f13fcdfef`).
- `scripts\one-time\2026-10-17-status-screen-research\r9_diff.py` output (CONFIRMED):
  - "in-memory build before status_bonus equals r8: True"
  - "in-memory build with status_bonus equals r9: True"
  - "r8 bytes under the new allocations all 0xFF: True"
  - "base runs: ['0x379C-0x37B6', '0x37B8-0x37BB', '0xF4AA-0xF4AD', '0xF512-0xF515', '0xF57A-0xF57D']"
  - "diff runs outside the veneer site, the 3 item sites and the new allocations: []"
- Tests: `py -3 -I -m unittest discover -s scripts\permanent -p "test_*.py"` gives "Ran 140 tests ... OK".

---

## 7. My test plan

### 7.1 What the states hold (CONFIRMED, dumped with `state_dump.py`, read only)

The page reads live values only for the leader: struct byte `@0x03000E90` (`ldr r1,=0x081d94d0 ; ldr r1,[r1] ; ldrb r1,[r1]`). The bonus shows only on the leader's page.

| State | Leader byte | Player `[@0x03001FA8]` | Flag 195 | Note |
|---|---|---|---|---|
| `archive\builds\log2_poc_r9.ss1` (= `log2_poc_r7.ss1`, same bytes as `data\roms\...ss3` and `.ss8` records) | 3 (Trunks) | 0 | clear | Not in the field: no player object exists |
| `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).ss1` (Gohan's bedroom) | 0 (Gohan) | `0x020319A8`, live 3/5/3 | clear | In the field, Gohan leads. Taken on the vanilla ROM |
| `data\roms\...ss2` | 1 (Piccolo) | `0x0202C8A4`, live 64/56/64 | clear | Piccolo has no transform ability (slot 2 = ability 11) |

- Names follow the character order 0-5 = Gohan, Piccolo, Vegeta, Trunks, Goku, Hercule (LIKELY: Gohan 0 and Piccolo 1 match the live values above, Hercule 5 holds abilities 6, 6, 6, 6).
- Base stats in `log2_poc_r9.ss1`: Gohan 3/5/3, Piccolo 4/4/5, Vegeta 6/4/6, Trunks 6/3/4, Goku 5/7/6, Hercule 8/1/6. Gohan, Vegeta, Trunks and Goku hold ability 12 (transform) in slot 2.
- **No available state can test Super Saiyan 2.** Flag 195 is clear in all five states checked (`log2_poc_r7.ss1`, data `.ss1`, `.ss2`, `.ss3`, `.ss8`).

### 7.2 Steps

Load `archive\builds\log2_poc_r9.gba` in mGBA. Then load `log2_poc_r9.ss1` and play into the field, or load the data `.ss1` state (Gohan in the field) from file. A state taken on the vanilla ROM is LIKELY to load on r9, because only the status page and the item checks differ. Close and reopen the menu after each change.

| # | Do | Screen | Expect |
|---|---|---|---|
| 1 | Gohan leads, base form, open the menu, Gohan's status page | STR, POW, END rows | "3/100" no bar, "5/100" one red segment (3 px), "3/100" no bar. HP, EP, EXP, NEXT, portrait and level look like vanilla |
| 2 | Gohan transforms (Super Saiyan, +10), open the menu | same | "3+10" with 2 gold segments (6 px), "5+10" with 1 red then 2 gold (3 + 6 px), "3+10" with 2 gold |
| 3 | In Super Saiyan, use a STR item (+1) from the menu if one is in the bag, reopen the status page | STR row | "4+10". Vanilla USA leaves live one step behind, which would show "4+9" (RSS 2.2) |
| 4 | If Trunks leads instead (the r9 state's leader byte): Super Trunks (+15/+10/+15, FRM section 1) | same | "6+15" with 1 red then 3 gold (3 + 9 px), "3+10" with 2 gold (6 px), "4+15" with 3 gold (9 px) |
| 5 | Open another character's page (not the leader) | STR, POW, END | "%d/100" and the base bar only, no gold |
| 6 | Any character at base 100 | bar | Base bar 60 px of 75 (20 segments). The 125 scale makes a full base bar shorter than vanilla |
| 7 | Super Saiyan 2 (needs flag 195: no available state) | same | For Gohan 3/5/3: "3+20" with 4 gold (12 px), "5+20" with 1 red then 4 gold, "3+20" with 4 gold |
| 8 | Rage (Cell fight, flat 100), if a state there exists | bar | For base 3: "3+97", gold from 0 to 60 px |

If the menu hangs or the screen is garbage, note the step. The long calls are the risk named in RSS section 5.

---

## 8. Concerns

1. **Save state.** `log2_poc_r8.ss1` does not exist in `builds\`. I copied `log2_poc_r7.ss1` to `log2_poc_r9.ss1` (SHA-1 `47f898f3...` both). r7 and r8 are the same ROM bytes (build log: "whole ROM equals r7", both SHA-1 `5662dc02...`). In that state the leader byte is 3 (Trunks), no player object exists, and flag 195 is clear. Gohan's page shows no bonus unless Gohan leads. No available state can test Super Saiyan 2 (section 7.1). CONFIRMED.
2. **Base diff is wider than "the veneer site".** Task 5 needs a call from the item code. The base ROM differs at `0x379C`-`0x37BB` (two 16-byte stubs in dead page code) and at 3 x 4 bytes at the item sites. The diff test asserts exactly this set (`test_base_8mb_differs_only_at_veneer_and_item_sites`). CONFIRMED.
3. **Gold indices differ from the draft.** The brief named 82 and 69. 82 is only 15.4 delta E from bar color 40. I built 58/69/34 (section 5). I confirm or picks another row set (`GOLD_ROWS`, one line). CONFIRMED (numbers), judgment (look).
4. **No separate stage-1 ROM.** The byte-identical relocation is proved by tests (section 2.1), not by an in-game build of stage 1 alone. LIKELY safe in game.
5. **Stale list pointer.** The resume routine `0x08006FA4` frees the list and does not clear `[0x03001D18]` (no store to `[r6,#0x38]` in `0x08006FA4`-`0x08006FDE`). find_player reads the list only when `[0x03001FA8]` is 0, which is the menu case. LIKELY never read stale.
6. **Stack.** stats draws 44 bytes deeper than the vanilla page (`push {r4,r5,r6,r7,lr} ; sub sp,#0x18`). The system stack starts at `0x03007E00`. LIKELY no effect.
7. **Shared assembler.** `ssj2_form.py` gained encodings. The ssj2 output is unchanged (CONFIRMED by the r8 equality above and the 113 old tests).
8. **Docs gap.** The +3 portrait literal moved to `rom:0x86FCD0`. A later patch that repoints appearance-table literals must also repoint this word (RE-BIBLE row added). CONFIRMED.
9. **My check 1 is still open.** The patch does not depend on it. Step 2 of the test plan answers it for the patched ROM.
