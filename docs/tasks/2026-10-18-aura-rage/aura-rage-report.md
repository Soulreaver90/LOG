# Aura and Rage report (aura-rage pass, 2026-10-18)

Brief: `docs\tasks\2026-10-18-aura-rage\aura-rage.md`. Built on r12 (SHA-1 `50a9f95d`, unchanged).

Labels: **CONFIRMED** = proved here with bytes, code or a test. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

## Status

| Item | Result |
|---|---|
| r13 | `archive\builds\log2_poc_r13.gba`, SHA-1 `2f8de78738f386f5db29e9378fb0cfe389aaae1e`, patches `gohan_gi,ssj2_form,gohan_portraits,status_bonus,ssj2_idle`, no env vars |
| r13 extras | `log2_poc_r13.ss1` = copy of `log2_poc_r12.ss1` (the newest); `log2_poc_r13.sav` = copy of `test-data\saves\log2_lv40_cellgames.sav` (it existed at build time, SHA-1 `c755acf0`, mtime 4:26 PM; the source still had the same SHA-1 at handback) |
| Tests | Whole suite **222 OK** (176 before + 27 new = 203 sprite and patch tests, plus 19 in `test_save.py` from the parallel save task). `frame_lock.py check --golden` exits 0 (20 names) |
| Part A | Done: set 160, three Rage sites repointed, Rage form code unchanged |
| Part B | Done: `gi_aura.py`, aura on anims 0, 1, 4, 13 of sets 159 and 160, 6 idle records per dir |
| Part C | Done, with one correction to the brief: the player's idle is vtable `@0x08025A84`, not `@0x08024BA0` (see C1) |

---

## Part A: gi Rage set 160

### A1. Set 160 (CONFIRMED, tests)

- `gohan_gi.py` builds set 160 from `art\gi_rage_aura\` (the aura pass over the r12 `gi_rage` copy) in the set 58 layout: 12 anims (0-8, 13, 16, 18), 204 records plus 16 more idle records = 220. Header and the 64 box bytes are a copy of set 58 (`test_set_160_has_the_set_58_layout`).
- `gi_rage_aura` keeps only the (anim, dir) rows of set 58 (read from the base ROM), so keys for anims 9, 11, 12, 20, 21 drop out.
- The set table copy now holds ids 7-160 (154 words). Set 58 and its table word stay as they are.
- `log2_sprites.build_set` takes an opt-in `counts={anim: n}` for a list longer than the source (anim 0 = 6). The default is unchanged.

| r13 offset | What |
|---|---|
| `rom:0x800000` | reverse lookup copy (entry 4 +1 = 160) |
| `rom:0x869C7C` | set 159 header (moved from r12 `rom:0x86339C`: its frames grew) |
| `rom:0x88D870` | set 160 header (its raw frames `rom:0x869E28`-`rom:0x88CA78`) |
| `rom:0x88D9EC` | set table copy (154 words), literal `rom:0x959C` |
| `rom:0x88DC54` | ssj2_form appearance table (literal `rom:0x1954` and 16 more) |
| `rom:0x894E24` | ssj2_idle hook (0x50 bytes) |

### A2. Every site that selects Rage's sprite (CONFIRMED unless marked)

Three sites change. Each one is needed, or the game hangs or shows the armor.

| # | Site | r12 | r13 | Proof |
|---|---|---|---|---|
| 1 | Cell script `rom:0x3EA365` (before ext 73 at `@0x083EA369`) | `1D 02 00 74 02 49` = `push 0,58 ; call ext_73` | `00 00 00 A0 02 49` = `push 0 ; push 160 ; call ext_73` | op 29 uses zigzag varints, so 160 (`82 40`) would grow the script. Op 0 pushes one byte, zero-extended: handler `[@0x083B5C00]` = `@0x08008F44`: `ldr r2,[r1,#0x0] ; add r3,r2,#1 ; str r3,[r1,#0x0] ; ldr r1,[r0,#0x0] ; ldrb r3,[r2,#0x0] ; ... ; str r3,[r0,#0x4] ; bx lr`. Same 4 bytes, same stack. The script record `@0x083EA33A`-`@0x083EA36F` has no jump op, so no branch can land inside the rewritten bytes (listing below) |
| 2 | Appearance entry 4 +1, live table | 58 (`3A`) | 160 (`A0`) | Player refresh `@0x080085FC`, map load `@0x0800C5CE`, the menus read +1 (OUT section 2). Set at `rom:0x1D96CD` before ssj2_form copies the table, so the relocated table holds it too |
| 3 | Reverse lookup copy (literal `rom:0x42F0`) entry 4 +1 | 58 | 160 | ext 73 calls `@0x080042BC` with the raw id. No entry with +1 = 160 would hang on the CharacterData.cpp assert (`@0x0801F878`). Now ext 73 (0, 160) finds entry 4, as (0, 58) did |

Script listing (`scripts\one-time\2026-10-18-save-slots\sdis.py`, base ROM):

```
083ea33a  0000      push 0
083ea33c  1b        loop_begin
083ea33d  0000      push 0
083ea33f  0014      push 20
083ea341  0231      call ext_49
083ea343  0037      push 55
083ea345  022e      call ext_46
083ea347  1d020012  push 0,9
083ea34b  0239      call ext_57
083ea34d  000a      push 10
083ea34f  022a      call ext_42
...
083ea361  0037      push 55
083ea363  022f      call ext_47
083ea365  1d020074  push 0,58      -> r13: 0000 push 0 ; 00a0 push 160
083ea369  0249      call ext_73
083ea36b  000a      push 10
083ea36d  022b      call ext_43
083ea36f  11        end
```

Search shapes for other `set:58` users of the player Gohan. A site that computes 58 at run time would not appear.

| Shape | Hits | Verdict |
|---|---|---|
| ext 73 calls with constant args (`ext73.txt`, all 41 calls) | 1: `@0x083EA369` | the Rage site. CONFIRMED |
| 34 ext ops that take a set id (`setargs.py extset.txt 58`) | 0 | no script names actor 58. CONFIRMED |
| Map object records (`mapsets.py 58`) | 3: map 8,12 records `@0x083FF77C`, `@0x083FF800`, `@0x083FF89C`, factory `0x0800E77F` +8 = 58 | +8 of that factory is an enemy type, not a set id (OUT section 5). Not set 58. CONFIRMED |
| Aligned words = set 58 header `0x082AB508` | 1: `rom:0x3B4F5C` | the set table word itself. CONFIRMED |
| `mov rN,#0x3A` in code `0x08000000`-`0x0802FFFF` | 7 (`@0x08005AC6`, `@0x08005AF0`, `@0x08005AFC`, `@0x080179A2`, `@0x080179E0`, `@0x08022E98`, `@0x0802F206`) | none feeds `get_set` (data or stores to +8/+0x54). CONFIRMED |
| ext 73 calls with run-time args (`'?'`, `'r'`) | 20 | cannot be excluded by a static scan. LIKELY none passes 58 |

NPC and cutscene uses of set 58 that stay: none found by these shapes. Set 58 itself stays in the ROM, unchanged.

### A3. Rage behavior unchanged (CONFIRMED, tests)

- Entry 4 equals vanilla in all 20 bytes except +1: +0 = 3 (bit 1 locks the ability), +5 = 2, +0x10 = `0x030021E4` (Rage form object). `test_rage_form_and_entry_unchanged_but_the_set`, `test_rage_unchanged` (`test_ssj2.py`, updated: compares all but +1).
- `read_form` (apply and tick read from code) gives flat 100/100/100, no ki drain, same methods as the base ROM.
- `rom:0x17000`-`0x174FF` (every form method and pool) equals the base ROM.

### A4. Portraits (not changed)

- Rage's portrait (entry 4 +2/+3 = 61/12, `3D 0C`) stays. In the ROM it is a 2-byte swap to 117/118 (`75 76`) in the relocated table.
- In code it is not one line: `gohan_portraits.FORMS` makes new art for each row, so entry 4 needs a new mapping that reuses ids 117/118 without art. Not done; my choice.

---

## Part B: the aura

### B1. `scripts\permanent\art\gi_aura.py` (CONFIRMED, tests)

Rules (file:line in `gi_aura.py`):

| Rule | Where |
|---|---|
| Face box: iris 64/65 box grown 3 px each side, 5 rows up, 3 rows down | `face_box`, line 54 |
| No bolt on the face box; bolts clip to the frame | `bake`, line 109 (`not in face` at line 113) |
| White core index 2, glow 191; white over a bright pixel (r+g+b > 450) becomes 191 | `bake` line 116; constants lines 41, 43 |
| Outline family: 2-3 short branched bolts from the transparent ring, trunk white every third pixel | `outline` line 93; `silhouette` line 81; `walk` line 63 |
| Deterministic: seed 22 in bolts.py order (reference), string seeds per frame elsewhere | `reference_patterns` line 122, `_seeded` line 159 |

- Not ported: the cross family and the `mix.py` trim.
- **Reference match:** the port, run in the bolts.py order (seed 22, column by column, each column d0, d1, d2), reproduces `aura2_outline_d0..d2.gif` on the golden SSJ2 bodies. Each 6x6 GIF cell is read at its center and classed to the nearest color (the GIF quantizes and the mask resize blends edges).
  - d1 and d2: all 6 columns match exactly.
  - d0: columns 0-3 match exactly. Column 4 differs in 1 px and column 5 in 7 px, all on rows 9-11 (forehead and brow).
  - Why: the GIFs are dated 12:22 AM, and bolts.py was edited at 10:55 AM. Its face box now reaches 5 rows above the iris, so it keeps those pixels free. I kept the current bolts.py rule. LIKELY cause (timestamps; a -3 row box leaves 3 px, so the old rule is not known exactly).
  - The sets use columns 0-2 only (below), and these match in all three dirs.
- Test `test_port_matches_the_owner_gifs` holds this result.

### B2-B3. Frames

| Set | Idle anim 0 (6 records per dir, index = body * 3 + shape) | Walk 1, ki charge 4, run 13 |
|---|---|---|
| 159 gi SSJ2 | Body 0 and body 1 = `golden_gi_ssj2std_d{dir}` (one std mockup per dir, so no blink frame exists; see concerns). Shapes: own seeded patterns on the std body | each frame its own seeded pattern on the r12 `gi_ssj2_v2` frame |
| 160 gi Rage | Body 0 = the r12 idle frame 0 (= `golden_gi_ssj2_d*`), body 1 = the r12 idle frame 1. Shapes 0-2 = **my reference columns 0-2**, byte for byte (`test_rage_idle_shapes_are_the_owner_columns`) | same, on the r12 `gi_rage` frames |

- Dir 3 keeps the h-flip of the dir 2 frame (as in r12), so its bolts mirror dir 2.
- Frames of other anims are the body PNGs, byte for byte.
- Bodies untouched: every changed pixel is 2 or 191 and off the face box (`test_bolts_only_add_bolt_colors_off_the_face`).
- `gi_aura.py all` reproduces both folders byte for byte (`test_folders_reproduce`).

### Goldens and locks (CONFIRMED)

- New goldens `art\golden\golden_gi_ssj2std_d0..d3.png`, byte copies of `work_r3\idle_std\ssj2_std_d0..d3.png` (SHA-1 equal). No existing golden file was written.
- `frame_lock.GOLDEN_IDLE` adds `ssj2std`: 20 names. `lock --golden --replace` moved the old lock to `locks\golden_20261018-1636`. The 16 old fingerprints are equal in the new lock.
- Aura-free bodies locked: `locks\gi_rage\` and `locks\gi_ssj2_v2\` (both check 0 differences). The aura folders are not locked.
- How the tests now tie the goldens:
  - `golden_gi_ssj2_d0..d3` = the Rage idle: `test_rage_idle_shapes_are_the_owner_columns` bakes them into set 160.
  - `test_gi_post` still checks that `gi_ssj2_v2`'s idle slots equal them. That folder is the aura-free body source of set 160's art (`gi_rage` is its r12 copy).
  - `golden_gi_ssj2std_d*` = set 159: `test_ssj2_idle_body_is_the_std_golden`.
  - `test_gi.GI_IDS` now maps 159 to `gi_ssj2_aura` and 160 to `gi_rage_aura`. The ROM decode test checks both sets against their manifests.
  - Defaults test: `test_gi_post.test_defaults_read_the_v2_and_aura_folders`.

---

## Part C: the idle hook

### C1. Vtables (CONFIRMED)

Vtable words are offsets from the vtable base (`target = base + word`). Search shape: every aligned word w at A where `(A - 4k) + w = 0x08007571` for k 0-39, plus absolute words and BLs.

| Vtable | Pool ref | State (OVW `states.txt`) | +4 word r12 | Decision |
|---|---|---|---|---|
| `0x08025A84` | `@0x08023020` | **0 = the player's idle with control** (enter `@0x08007F26` calls `@0x08007554`) | `0xFFFE1AED` | **hooked**: `0x0086F3A1` |
| `0x08024BA0` | `@0x08022FA0` | 38 (the brief's vtable) | `0xFFFE29D1` | **hooked**: `0x00870285` |
| `0x0802588C` | `@0x08022FA8` | 22, enter `@0x08007588` sets row `set + 0x1AC` (anim 22) | unchanged | left vanilla: never the anim 0 row |
| `0x08025874` (k 6), `0x08024814` (k 34) | none / not a vtable start | - | - | false positives (overlap of 0x0802588C +0; no vtable base at `0x08024898`) |

> [!WARNING]
> The brief named only `@0x08024BA0` (state 38). Hooking only that one leaves the everyday idle unchanged, because the player's idle is state 0 with vtable `@0x08025A84`. Both are hooked.

Caller (CONFIRMED): `@0x0800772A` `ldr r0,[r0,#0x1c]` ... `ldr r0,[r4,#0x18] ; ldr r1,[r0,#0x0] ; ldr r2,[r1,#0x4] ; add r2,r2,r1 ; add r1,r4,#0 ; bl 0x8021d2c`. So r0 = state and r1 = obj. After the call it reloads r0-r2, so r2 and r3 are free (ATPCS scratch).

### C2. Hook listing (r13, `@0x08894E24`, `patches\ssj2_idle.py`)

```
08894e24  ldr r2,[r1,#0x48]          ; set pointer
08894e26  ldr r3,=0x08869c7c         ; set 159
08894e28  cmp r2,r3
08894e2a  beq 0x8894e36
08894e2c  ldr r3,=0x0888d870         ; set 160
08894e2e  cmp r2,r3
08894e30  beq 0x8894e36
08894e32  ldr r2,=0x08007571         ; vanilla tick: r0, r1, lr, sp as at entry
08894e34  bx r2
08894e36  add r2,#0x4c
08894e38  ldr r3,[r1,#0x4c]
08894e3a  cmp r2,r3
08894e3c  bne 0x8894e32              ; not the anim 0 row: vanilla
08894e3e  ldrh r0,[r1,#0x12]
08894e40  add r0,#0x1
08894e42  strh r0,[r1,#0x12]         ; tick += 1, as vanilla
08894e44  lsl r2,r0,#16
08894e46  lsr r2,r2,#18              ; (tick & 0xFFFF) >> 2
08894e48  ldr r3,=0x00005556
08894e4a  mul r3,r2
08894e4c  lsr r3,r3,#16              ; / 3, exact below 0x8000
08894e4e  sub r2,r2,r3
08894e50  sub r2,r2,r3
08894e52  sub r2,r2,r3               ; shape 0-2
08894e54  lsl r0,r0,#24
08894e56  lsr r0,r0,#24
08894e58  cmp r0,#0xf1
08894e5a  blt 0x8894e5e              ; body 0 while (tick & 0xFF) <= 0xF0
08894e5c  add r2,#0x3                ; body 1
08894e5e  strh r2,[r1,#0x14]
08894e60  bx lr
```

- The row guard (`obj+0x4C == obj+0x48 + 0x4C`) is an addition to the brief. Without it, a state that shares this tick on another row would read past a 2-record list, and the upload has no bounds check.
- The ssj2_form assembler gained `mul` (format 4, `0x4340`). Every existing encoding is unchanged (test_ssj2 EXPECTED still passes).

### C3. Tests (CONFIRMED)

`tests\test_idle.py` runs the code as `thumb_dis` text in `test_status.PageCpu`:

- Sets 159 and 160 through both hooked vtables, 4 seeds (one wraps past 0xFFFF), 512 ticks: equal to the formula, all 6 indices seen.
- Sets 157, 158, 56, 58, 60, 137: equal to the vanilla sequence. The vanilla sequence is checked against the base ROM `@0x08007570` run in the same interpreter.
- Sets 159 and 160 on row 22: vanilla.
- r1, sp, r4-r7 kept on every call.
- Anim 0 record count: 6 per dir in 159 and 160, 2 in 157 and 158.
- Base 8 MB without and with ssj2_idle: only the 8 vtable bytes differ.
- Fails closed on a wrong vtable word or tick byte, and on missing notes.

---

## Build and review

### r13 against r12 (`scripts\one-time\2026-10-18-aura-rage\r13_diff.py`, CONFIRMED)

- **Base 8 MB:** the 17 appearance literals, `rom:0x959C`, `rom:0x8E8C`, `rom:0xBE10`, `rom:0x1D99CC` (moved targets), the status stub pool words `rom:0x37A8` and `rom:0x37B8` (moved targets), the 2 vtable words, `rom:0x1D96CD` (58 to 160) and `rom:0x3EA365`-`0x3EA368`. Nothing else.
- **Sets:** 7-158 decode equal (records and pixels). Set 159 differs in anims 0, 1, 4, 13 only (72 keys; records 276 to 292). Set 160 is new (220 records).
- **Appearance tables:** live table differs at entry 4 +1 and entry 22 +0x10 (the moved form object). The copy differs at entry 4 +1 only.
- **ssj2_form, gohan_portraits, status_bonus region:** r12 `rom:0x868FAC`-`0x87017C` against r13 `rom:0x88DC54` (+0x24CA8). 15 pointer words moved by the shift. The 5 other words are the entry 4 +1 word and the 4 base-relative vtable words that point into base code (they change by -0x24CA8, as they must).
- **r13 tail:** `rom:0x894E24`-`0x894E73`, the hook.

### Review images (I looked at them)

- `archive\2026-10-18-art-review-renders\aura_r13\r13_159_160.png`: sets 159 and 160, anims 0, 1, 4, 13, all dirs, 4x, lime.
- `archive\2026-10-18-art-review-renders\aura_r13\r13_159_160_s<set>_a<anim>_d<dir>.gif` (32 GIFs, rom_sheet 150 ms).
- `archive\2026-10-18-art-review-renders\aura_r13\idle_emu_s159_d0..2.gif`, `idle_emu_s160_d0..2.gif`: the hook from r13 run for 120 ticks (seed 0xB0, so the body 1 window falls inside), equal neighbors merged, 67 ms shows as 70 ms (GIF 10 ms unit). Tool: `scripts\one-time\2026-10-18-aura-rage\idle_gif.py`.
- Seen:
  - Bolts hug hair, shoulders, hands and feet, and never touch the face.
  - Rage idle frames 0-2 are my approved columns.
  - Walk and run change shape on every frame.
  - Set 159 idle stands in the standard pose with the SSJ2 head.

---

## My test plan

1. Load `log2_poc_r13.gba` with `log2_poc_r13.sav` in mGBA (no cheats). The .sav is the parallel task's new `log2_lv40_cellgames.sav`. `log2_save.py info` reads it as follows:
   - Slot 1: Capsule Corp 6,1. Gohan leads. Flag 195 set.
   - Slot 2: map 11,1. Gohan leads. Flag 195 set.
   - Slot 3: map 9,1. Goku leads. Flag 195 clear (before the Cell Games).
2. **SSJ2 (set 159):**
   - Load slot 1. Press L until the "Z" icon shows. Press B: Super Saiyan (gi SSJ).
   - The icon turns to "Z2" (EP >= 10). Press B again: the step plays, then SSJ2.
   - Stand still. You see the standard SSJ idle pose with the SSJ2 hair. Blue and white bolts hug the outline and change shape about 15 times a second (every 4 frames). They never cross the face.
   - Every 256 frames the vanilla "frame 1" window comes (15 frames). For 159 it shows the same body, so you see only the shapes keep cycling.
   - Walk: each of the 4 walk frames has its own bolts. Double-tap a direction to run: the same.
   - Check all 4 facings. Left and right show mirrored bolts.
3. **Rage (set 160):**
   - The Rage scene is the Cell Games fight, ext 73 at `@0x083EA369`. Only a save before the fight reaches it.
   - Slot 3 of the new .sav is the parallel task's pre-Cell-Games save. I did not check that it reaches the fight: its route belongs to the save-rebuild report.
   - If it does: play to the fight. When Gohan turns Rage he shows the gi SSJ2 power pose with the approved outline bolts (idle), and bolts on walk and run. Stats stay flat 100, no ki drain, and the transform ability stays locked.
   - If no save reaches it, an old save before the Cell Games or the debug menu (Cell Games Arena) is the way in. `log2_lv40_postcell.sav` cannot reach it, because flag 195 is set.
4. Report anything that looks frozen or flickers, and any frame with a bolt over the face.

---

## Files

| File | Change |
|---|---|
| `scripts\permanent\art\gi_aura.py` | new |
| `scripts\permanent\patches\ssj2_idle.py` | new |
| `scripts\permanent\patches\gohan_gi.py` | set 160, Rage sites, aura folders, anim 0 count |
| `scripts\permanent\patches\ssj2_form.py` | assembler `mul` only |
| `scripts\permanent\rom\log2_sprites.py` | `build_set(counts=None)` |
| `scripts\permanent\art\frame_lock.py` | 20 golden names |
| `scripts\permanent\tests\test_aura.py`, `test_idle.py` | new (13 + 14 tests) |
| `tests\test_gi.py`, `test_gi_post.py`, `test_ssj2.py`, `test_portraits.py`, `test_owner_walk.py` | point to sets 159/160, the aura folders, Rage +1 = 160, 20 goldens |
| `art\gi_ssj2_aura\`, `gi_rage_aura\` | new art (gi_aura.py all) |
| `art\golden\golden_gi_ssj2std_d0..d3.png` | new goldens |
| `art\locks\golden\` (replaced, old kept), `locks\gi_rage\`, `locks\gi_ssj2_v2\` | locks |
| `scripts\one-time\2026-10-18-aura-rage\r13_diff.py`, `idle_gif.py` | review tools |
| `docs\build-log.md`, `docs\RE-BIBLE.md` | build line; 10 rows tagged `AUR`, plus `AUR` in the shared source-doc list (line 27) |

## Concerns

1. **Brief vtable** (CONFIRMED): `@0x08024BA0` is state 38. The player's idle is state 0, `@0x08025A84`. Both are hooked, and state 22 (`@0x0802588C`) is left vanilla.
2. **Set 159 has no blink frame** (decision): there is one std mockup per dir, so body 0 = body 1. The vanilla 15-frame "frame 1" window shows no change except the bolts. A std blink frame needs my art.
3. **Reference d0 columns 4-5** differ by 1 and 7 px on rows 9-11. The current bolts.py face box blocks them, and the GIFs predate that edit (LIKELY). The sets use only columns 0-2, which match.
4. **Idle timing:** the hook changes shape every 4 game frames (67 ms). My GIFs play at 100 ms. The brief fixed the formula; say if it should be slower.
5. **Other ticks on anim 0** (LIKELY minor): a code path that shows anim 0 index 1 with its own tick (not this hook) would now show body 0 shape 1 instead of frame 1. No such path is known.
6. **State 14** (SPECULATIVE): after 0x400 idle frames, state 0 goes to state 14. Its anim was not traced. If it is anim 4, it has bolts too.
7. **Save:** `log2_poc_r13.sav` is the parallel task's work in progress (mtime 4:26 PM, copied at about 4:39 PM). Its slot 3 route to the Cell fight is not verified here. Also, `log2_lv40_postcell.sav` now has SHA-1 `1973041f`, not the `3ecf1e40` in the bible. I did not touch it, so it may be the other task's work.
8. **Save state:** `log2_poc_r13.ss1` (copied from r12) has no player object (`[0x03001FA8]` = 0), so it holds no stale set pointer. Set 159 moved to `rom:0x869C7C`. A state saved in r12 while in SSJ2 would point at stale data in r13.
9. **Rage portrait** stays the armor Rage portrait (61/12). It is a 2-byte ROM swap, but not a one-line code change.
10. **Whole suite:** 222 OK, including the 19 save tests.
11. **RE-BIBLE line 27:** I added `AUR` to the shared source-doc list, as the bible rule asks. It is the one shared line I edited. All my other edits are my own rows.
