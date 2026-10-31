# File select report: unselected slots draw the gi through the menu dim table

Date: 2026-10-18. Brief: `docs\tasks\2026-10-18-file-select\file-select.md`. ROM: `archive\builds\log2_poc_r17.gba` (SHA-1 `eee5eb35`), read only. Code was traced on the base ROM copy `scratch\ghidra\log2.gba`; every traced range is byte-equal in r17 except three pool words (appearance table literals `0x08001B3C`, `0x08010F18`, and the `ssj2_idle` vtable word `0x08024BA4`).

Labels: **CONFIRMED** = proved from ROM bytes, code, a test or a pixel match. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

## Result

| Item | Value |
|---|---|
| Cause | The menu sprite dim table `0x086D0ED0` maps skin `pal:114` to 124 (olive gray) and `pal:115` to 244 (mauve). The gi shows skin on the shoulders, arms and chest V, so the dimmed gi reads as purple shoulders, an orange V and a gray face. CONFIRMED |
| Not the cause | No separate frame, set or graphic: the unselected sprite is `set:157` anim 0 dir 0 frame 0 (the golden idle). No other palette bank: one 256-color OBJ palette `rom:0x1DA6C8`, unchanged in r17. CONFIRMED |
| Fix | `scripts\permanent\patches\file_select_dim.py`: dim entry 114 to 116 and 115 to 117, in place (`rom:0x6D0F42`-`0x6D0F43`, `7C F4` to `74 75`). Not in the build list. No ROM built |
| Tests | `scripts\permanent\tests\test_file_select_dim.py`: **8 OK**. Whole suite once at the end: **293 OK** |
| Proof image | `archive\2026-10-18-art-review-renders\file_select_fix.png` (lime) |

## 1. Draw path (all CONFIRMED by code unless marked)

| Step | Address | What it does |
|---|---|---|
| Title scene enter | `0x080005A4` | DMAs the shared OBJ palette `rom:0x1DA6C8` (256 entries) to `0x05000200`. No other palette write on this path |
| Title choice 0 | `0x08000580` | Calls the file select constructor `0x08000CD8` |
| Slot data | `0x08001960` | Loads the 3 slots with `0x08003F9C`; stores each in-party record pointer at slot +0x42C |
| Per slot, per party member | `0x08000D96`-`0x08000E1C` | `set = 0x08001AB8(slots, slot, i)`: appearance table (r17: relocated `0x0888DC54`) entry of record +8, byte +1, through `get_set 0x08009324` |
| Sprite object | `0x08007C70(0, set, x = 0x30 + 16 i, y = 0x38 + 0x28 slot)` | Sprite root `0x080075A8` with state `0x03001F34` (state 38, anim 0 idle); vtable `0x08025C30`; then `0x080076EE(obj, 0x086D0ED0)`: every sprite starts dimmed |
| Gray variant | `0x08000DE4`-`0x08000DFC` | Record +0x14 bit 1 clear: dir 1 (back view) and gray table `0x086D0DD0`. Meaning of bit 1 not traced (SPECULATIVE: not switchable) |
| Highlight | `0x08000F50`-`0x08000F9A` | Old highlighted sprite: vtable +0x28 with arg 0. New one: the selected slot's leader only (`0x08001A8A` = leader position among party members), vtable +0x28 with arg 1 |
| vtable +0x28 | `0x08007CB6(obj, n)` | State `[0x081DA978 + 4n]`: n 0 = `0x03001F34` (state 38, anim 0, 2 frames), n 1 = `0x03001F30` (vtable `0x08024A00`, anim 1 walk, 4 frames). Table: `0x086D0ED0` for n 0, none for n 1 |
| Table store | `0x080076EE(obj, table)` | obj+0x28 = table. obj+0x24 = table when the set remap obj+0x2C (set word +8) is 0, else a composed copy at obj+0x50 (`table[remap[i]]`). All 23 sets of the r17 appearance table (53, 55, 57, 60, 61, 72, 103, 104, 128-130, 132-135, 137-140, 157-160) and base sets 54, 56, 58, 59 have +8 = 0 (read; the test asserts it for the base party sets) |
| Frame upload | `0x080077E6` | obj+0x24 != 0: `0x0801F3BA(header, buffer, obj+0x24)`. Type 0 (our raw gi frames) via ARM `0x0300029C`: each nonzero byte becomes `table[byte]`, 0 stays 0. Type 1 (vanilla) via `0x03000958`. Type 2 is not unpacked on this path, but `0x08007802` still copies the stale stack buffer |
| Blending | `0x080005FA`, `0x08000608`, `0x08000548` | Global BLDCNT `0x284D` and BLDY fades. Same for all slots, so not a per-slot effect |

**Who is dimmed:** every party sprite except the selected slot's leader. So Piccolo (never the leader in these saves) is dimmed in every slot, which is why he "looks the same in all slots". Selected Gohan is drawn plain, anim 1 (walk).

**Pixel match (CONFIRMED).** My screenshot was sampled back to 1x (scale 8.25) and matched against model renders (`scripts\one-time\2026-10-18-file-select\match.py`):

| Screenshot sprite | Best model | Match |
|---|---|---|
| Slot 1 (selected) Gohan | `set:157` anim 1 dir 0 frame 1, no table | 1.000 of 299 px |
| Slot 3 Gohan | `set:157` anim 0 dir 0 frame 0, dim table | 1.000 of 330 px |
| Slot 1 and slot 3 Piccolo | `set:103` anim 0 dir 0 frame 0, dim table | 1.000 of 414 and 436 px |
| Slot 2 Gohan, Piccolo | same models as slot 3 | 0.861, 0.929: my red box is drawn over the sprites. Not a model error |

## 2. Cause

**Candidate 1, a dim table with bad entries for gi indices: CONFIRMED, for 114 and 115 only.** Sweep of every index sets 157-160 show in anims 0 and 1 (all frames, all dirs; `scripts\one-time\2026-10-18-file-select\sweep_gi.txt`). Test: hue shift above 15 degrees on a colored entry, or luma ratio outside 0.55-1.05.

| Index | Gi use | Dim now | Result |
|---|---|---|---|
| 88-89, 211, 26-27, 34-35, 72, 195 | gi purple, outline, sash, shoes, wristband | 89, 97, 211, 27, 35, 113, 73, 193 | same hue, luma 0.63-1.04. These are Piccolo's own dims. Index 87 (anim 9 step light) does not appear in anims 0 and 1, so not on these screens |
| 116, 117 | skin, mid and dark | 21, 23 | hue shift 11.5 and 12.3 degrees, luma 0.78 and 0.76 |
| 20-23, 37-39, 44, 46, 120, 191 and the rest | hair, gold, aura | same ramps | pass |
| **114** | skin light: face, shoulders, arms | **124 (168,160,120)** | **hue 12 to 50 degrees, low saturation: olive gray** |
| **115** | skin: shoulders, chest V, face | **244 (168,96,120)** | **hue 15 to 340 degrees: mauve** |

My words, mapped: "dark purple shoulders" = 115 to mauve 244 next to the dimmed purple 97. "Darker face" = 114 to olive 124 and 115 to mauve. "Large orange V" = the V's 116 to 21 and the collar line 23 to 113, framed by the mauve and olive around it.

**Candidate 2, a separate frame or set: ruled out (CONFIRMED).** The unselected sprite is the same `set:157` (appearance entry 2 +1 = 157 in the relocated table) anim 0 frame 0 that the game uses for the idle; it is my golden base front. It only looks like an "earlier sprite" because of the remap.

**Candidate 3, a different palette bank: ruled out (CONFIRMED).** All sprites are 8bpp on one OBJ palette; the title enter loads `rom:0x1DA6C8`; r17 has the vanilla bytes there.

**Why vanilla armor Gohan looks right.** It goes through the same table with the same bad entries. The armor covers the arms and chest (suit 79-81, whites 2 and 9-13, trim 40-42, all with clean dims), so skin shows on the face only: `set:56` 0.0.0 has 13 px of 114 and 115, the gi `set:157` 0.0.0 has 22 px, spread over shoulders, arms and chest. The vanilla face is also olive and mauve when unselected (proof image, row 3). Vanilla Goku (`set:60`, bare arms) shows the same defect on his arms (row 4).

**Why no gi-only fix.** The palette has no duplicate of color 114 or 115 (only `pal:28` is near 114), so the gi cannot move to other indices with good dims. A set remap (+8) composes with the table but also applies to the plain draw. A gi-only dim needs new code in `0x08007CB6` and `0x08007C70` (per-set table), which is far larger than the table edit.

## 3. Fix and blast radius

**Patch** `scripts\permanent\patches\file_select_dim.py` (`apply(rom, alloc)`, `_expect` checks, notes in `alloc.notes["file_select_dim"]`):

- Checks the pool word `rom:0x7D1C` = `0x086D0ED0` and the old entries `7C F4`, all before any write.
- Writes dim 114 = 116 (luma 0.72, hue 18 degrees) and 115 = 117 (luma 0.68, hue 20 degrees): two skin steps down, inside the band of the vanilla entries (median luma 0.76).
- Independent of every other patch; it applies cleanly to the base ROM and to r17 (diff exactly `rom:0x6D0F42`, `0x6D0F43`, checked).

**Blast radius (CONFIRMED by the shapes named; a reader through a computed address would not appear):**

| Reader | Evidence |
|---|---|
| Only pool word | Aligned word scan of the base ROM: `0x086D0ED0` appears only at `rom:0x7D1C` (test) |
| Its two loads | `0x08007C9A` (constructor `0x08007C70`) and `0x08007CCE` (vtable +0x28 `0x08007CB6`) |
| Objects with that vtable | `0x08025C30` has one literal, `0x08007D18`, in the constructor |
| Constructor callers | File select `0x08000DCC`; party screen `0x08010C5C` in `0x08010BCE` (+0x28 calls at `0x08010CC8`, `0x08011132`, `0x0801114C`). That screen is LIKELY Switch Characters (OVW names `0x08011172` the Switch Characters path; not traced further) |
| Sprites changed | Unselected or non-cursor Gohan sets 53, 55, 57, 157-160 and Goku 60, 61 (pixels 114 or 115 in anims 0 and 1). Piccolo, Vegeta, Trunks and Hercule sets have none (test) |

This is a vanilla change: unselected vanilla Gohan and Goku faces (and Goku's arms) become darker skin instead of olive and mauve. I decide whether that is wanted (proof image rows 3 and 4).

## 4. Proof image

`archive\2026-10-18-art-review-renders\file_select_fix.png`, lime (191, 255, 7), 6x. Columns: my screenshot (slot 3 Gohan, gi row only), plain, unselected now, unselected after the fix. Rows: gi base `set:157` and gi SSJ `set:158` (r17), armor `set:56`, Goku `set:60`, Piccolo `set:103` (base ROM). Anim 0 dir 0 frame 0.

What it shows (looked at, also at 12x):

- Now: olive face, mauve blotches on the cheeks, shoulders and forearms.
- After: face, shoulders and arms are one darker skin. Piccolo is unchanged.
- The chest V stays visible as darker skin (orange brown). It is the vanilla 116 to 21 and 117 to 23 dims, the same color as the dimmed arms. If I still reads it as an orange V, the cause is not 114 or 115, and I did not tune further.

## 5. Files

| File | Change |
|---|---|
| `scripts\permanent\patches\file_select_dim.py` | new |
| `scripts\permanent\tests\test_file_select_dim.py` | new, 8 tests |
| `scripts\one-time\2026-10-18-file-select\` | `look.py` (render plain and dim), `match.py` (screenshot match), `sweep.py` (index sweep), `proof.py` (review image); outputs `sweep_gi.txt`, `sweep_vanilla.txt`, `native_s1..s3.png`, `suite.txt` |
| `archive\2026-10-18-art-review-renders\file_select_fix.png` | new |
| `docs\RE-BIBLE.md` | source `FS` in the list; rows in sections 5 and 14 |

## 6. Concerns

1. **Vanilla change.** The fix also changes the unselected vanilla Gohan and Goku. A gi-only fix needs new code (per-set table); not built.
2. **Not tested in game.** The model matches the screenshot pixel for pixel, but the patched build is not run.
3. **Switch Characters** is the same table and the same defect for the gi; the screen name is LIKELY.
4. **SSJ and SSJ2 saves.** The file select reads the relocated appearance table, so a slot saved in Super Saiyan or Super Saiyan 2 (if the game allows it, open question) draws `set:158` or `set:159`; state 38 carries the `ssj2_idle` hook, so a dimmed `set:159` cycles its aura. Both pass the dim sweep after the fix.
5. **Brief deviation.** My early Bash calls started with `cd` into the LOG root (read-only commands and one scratch render). I stopped once I noticed; nothing outside my files was written.

## 7. Suite

Whole suite once at the end, from the `scripts\permanent` root: **293 OK** (285 others plus the 8 new), output in `scripts\one-time\2026-10-18-file-select\suite.txt`. After the suite I added one assertion inside `test_blast_radius_is_gohan_and_goku` (set +8 = 0 for every party set) and re-ran that file alone: 8 OK. The count stays 8.
