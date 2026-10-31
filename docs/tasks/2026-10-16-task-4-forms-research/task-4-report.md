# Task 4 report: forms, transform input and HUD

Status: DONE_WITH_CONCERNS. The form system is data-driven, so BLOCKED does not apply. Full evidence: `docs\research\re-forms.md`.

## Findings

**(a) Form table. CONFIRMED.**
- Appearance +0x10 points to a form object: one word, a base-relative vtable. Live methods: +0 apply, +4 per-frame tick, +8 enter (sound), +0xC leave.
- Apply writes u8 effective stats to player +0x160/+0x161/+0x162 and speeds to +0x188/+0x18C.
- Super Saiyan (vtable 0x08024C58): +10 STR/POW/END (`080172ce add r2,#0xa` x3), speed 1.75/3.0. Drain: accumulator +0xCCD per frame, EP -1 per overflow (every 20 frames). At EP 0 it sends message 0x24 (revert).
- Rage (vtable 0x08024E4C): flat 100/100/100 (`080170e2 mov r1,#0x64`), speed 2.0/3.25. Its tick has no EP code and regenerates 1 % max HP per 20 frames.
- Others: Super Vegeta/Trunks +15/+10/+15 (slower, 1 EP per 40 frames). Super Namek +6 each. Base: no bonus, regenerates EP and HP.
- Sprite set = appearance +1. HUD icon = per ability, not per form (see d).

**(b) Transform input. CONFIRMED.**
- The "Z button" is B with the transform ability selected. L cycles the ability slots.
- Chain: KEYINPUT at 0x0801EEFC, input object 0x0300229C +0x14 bit 1, then 0x08007EDA. That routine takes `ability = record[0x18 + slot]` from the table at rom:0x1D9900 (icon, dim icon, test, action) and calls the test, then the action.
- Ability 12 (Saiyan transform): test 0x080134F2, action 0x0801353C. The action sends message 0x23 (160-frame transform state, cooldown +8 per frame) or 0x24 (revert state).
- The states end in 0x0801563C, transform(player,1), or 0x080157AE, transform(player,0). 0x08014D58 then: old form leave, record +8 = +4 or +5, sprite = get_set(+1), apply the new form, enter it.
- Entry 5 +4 = 4 (Rage) is never read in play: +4 has one reader, and transform(1) is reached only from untransformed forms.
- Super Saiyan has no story flag gate. It needs record +0x14 bit 5, cooldown struct +0x08 = 0, EP >= 10, and `[0x03002080+0xC] != 0` (meaning SPECULATIVE).

**(c) Rage in the Cell event. CONFIRMED.**
- ext 73 (0, 58) handler 0x0800A8EC runs this order: leave old form, record +8 = 4, player sprite = raw set 58, apply Rage (flat 100), enter Rage.
- No drain: the Rage tick has no EP code.
- No exit or transform: entry 4 +0 bit 1 makes test 0x080134F2 return 0.
- Set 58 lacks anims 9 (transform) and 21 (revert).

**(d) HUD icon. CONFIRMED.**
- HUD routine 0x08008BEE builds 0x500 bytes of 8bpp OBJ tiles: frame from 0x086D7B54, then the selected ability's icon (`test ? +0 : +4`), then the bar pixels. It DMAs the result to 0x06010000.
- The "Z" is a raw 0x200-byte 32x16 8bpp image: 0x086DAE7C (usable) and 0x086DB07C (dim), shared by abilities 11 and 12.
- HP, EP and EXP bar pixels overwrite part of the icon area.
- Buu's Fury "Z3" not traced: SPECULATIVE (Z panel plus a separate "3"). Three search shapes found nothing; one hit was a jump table.

**(e) RAM.** See the next section.

**(f) Patch sites.** See the patch sites section below.

## Recommended Task 6 approach (with costs)

Relocate the appearance table to the expansion area and add entry 22 = Super Saiyan 2. Set entry 5 +4 = 22. Put the flag 195 gate on the ability 12 action pointer. Add a new ROM form object (+20, drain 0x199A). Add an in-place HUD hook for "Z2".

| Option | Cost | Verdict |
|---|---|---|
| A. Relocate table, entry 22 | 460-byte copy, 17 literal words, no code for the table | Recommended |
| B. Reuse unused entry | None free: all 22 reached (defaults, ext 73 sets, debug, chains). LIKELY complete | Rejected |
| C. Rage entry 4 as Super Saiyan 2 after flag 195 | Flag-conditional apply, tick, test and sprite. Set 58 lacks transform and revert anims. Touches Rage | Rejected |
| D. Entry 5 +4 only after flag 195 | +4 is ROM data. Needs the same new entry plus a hook inside 0x08014D58, which has no pointer hook | Folded into A (gate in the action) |

- New code: apply and tick (copies of 0x080172B0 and 0x08017306, about 0xC0 bytes), step gate (about 20 instructions), HUD icon routine (about 25 instructions), and the Z2 icon pair (0x400 bytes).
- Thumb BL cannot reach the expansion area. Entry is only through absolute pointers. Exit is through local `bx` stubs.
- No assembler is installed: hand-encode, then verify with thumb.py or the Ghidra assembler.

## Patch sites (original bytes)

| Site | Original | New |
|---|---|---|
| rom:0x1954, 0x1B3C, 0x3B30, 0x414C, 0x854C, 0x886C, 0x8B04, 0xA77C, 0xAA04, 0xB050, 0xC804, 0x10F18, 0x112BC, 0x13574, 0x14FF4, 0x26458, 0x26474 | `7C 96 1D 08` each | relocated table address |
| rom:0x42F0 | `7C 96 1D 08` | stays on Task 5's unchanged copy |
| relocated entry 5 +4 (orig rom:0x1D96E4) | `04` | `16` |
| relocated entry 22 | none | `01 SS 3E 0D 02 02 06 00 14 00 00 00 00 01 00 00` + form object ptr |
| rom:0x1D99CC (ability 12 action) | `3D 35 01 08` | step gate\|1 (falls through to 0x0801353D) |
| rom:0x8E8C (HUD literal) | `00 99 1D 08` | HUD icon routine\|1 |
| rom:0x8D14-0x8D1D | `40 19 00 7E 00 01 46 18 B1 68` | `28 1C 19 F0 08 F8 01 1C 07 E0` (`add r0,r5,#0 ; bl 0x8021d2a ; add r1,r0,#0 ; b 0x8008d2e`, verified by disassembly) |

## RAM addresses for my memory check

| What | Address |
|---|---|
| Gohan current EP / max EP | 0x03000EA0 / 0x03000EA2 (u16) |
| Gohan appearance index (2 base, 5 Super Saiyan, 4 Rage) | 0x03000EA4 (u8) |
| Gohan base STR / POW / END (unchanged in a form) | 0x03000EA6 / 0x03000EA8 / 0x03000EAA (u16, value / 256) |
| Player object pointer | 0x03001FA8 (u32; object moves between maps) |
| Live STR / POW / END with form bonus | `[0x03001FA8]` + 0x160 / +0x161 / +0x162 (u8) |
| Current form object, drain accumulator | `[0x03001FA8]` + 0x180, + 0x184 |
| Transform cooldown | 0x03000E98 (u32) |
| Flag 195 | 0x03000F5C bit 3 (save check: struct +0xCC = 0x0F in the test save) |

## Files changed

- Created `docs\research\re-forms.md`.
- `docs\RE-BIBLE.md`: source `FRM`; updated the form lines (Super Saiyan, Super Vegeta/Trunks, Namek, Rage and input lines from O to C); added 17 fact lines (forms, HUD, ability table, messages, set 58 anims, Task 6 plan, RAM, record +0x18, struct +0x08, tools); closed 3 open rows; added 2 of my questions.
- `docs\research\re-outfit.md` (Ruling 9):
  - Section 1 adds the +7 read (0x0800850C) and the +0xC word reads (0x0800843C, 0x08008448).
  - Section 2 states the 17-site BL list with four search shapes.
  - Section 5 dismisses ext_112 at 0x084011CB (map record bytes quoted).
  - The Task 6 note now points to re-forms.md.
- New tools in `scripts\one-time\2026-10-16-task-4-forms-research\`: `vtfind.py`, `formuse.py`, `appsweep.py` and `icons.py`. Output: `icons.png`, `hud_base.png` and two HUD sheet crops.
- Test suite: 17 tests pass. No file under `data\` was written.

## Concerns

1. **Ruling 9 BL count.** Ruling 9 says 18 BLs to 0x08009324, including 0x08009380. Four independent shapes give 17, and 0x08009380 is already in that list. I wrote 17 with the full site list. I should re-check its 18.
2. **Super Saiyan 2 sprite.** Super Saiyan 2 cannot use set 58 or a plain clone of it. Set 58 lacks anim 9 (the transform animation played on the old set) and anim 21 (the revert animation). A set with set 59's 22-anim layout is required. This affects Task 2/5/6 art planning.
3. **Cooldown.** The step gate must not test the cooldown. It is about 1280 right after Super Saiyan and only falls in base form. The step adds another 1280, so after Super Saiyan 2 the wait is about 43 s.
4. **Task 5 build order.** Task 5 edits rom:0x1D96A5 and rom:0x1D96E1 in place. The relocated table must carry those edits.

## Open questions (mine)

1. From Super Saiyan with flag 195, should B step to Super Saiyan 2 (recommended), or should base go straight to Super Saiyan 2?
2. Show "Z2" only in Super Saiyan 2 (recommended), or also in Super Saiyan when the next press steps up?
3. Super Saiyan 2 speed (default: Super Saiyan's 1.75/3.0) and EP cost of the step (default 10).
4. Which art Super Saiyan 2 shows (set 58 hair on the set 59 layout, or Task 5's gi Super Saiyan clone).
5. Portrait ids for entry 22: Super Saiyan `3E 0D` or Rage `3D 0C` (Task 7).
6. Not traced: whether the game saves while the leader is transformed, the trigger of message 0x21 (revert without animation), the map word `[0x03002080+0xC]`, and the Europe status screen bonus.

## Fix round 1 (doc only)

- `docs\research\re-forms.md` section 7, "New code": apply and tick are now **re-encodings** with their own literal pools, not byte copies. The doc lists the pc-relative pools (0x0801748C, 0x08017498, 0x0801749C, 0x080174A0) and the BLs (0x080172EC, 0x080172F8, 0x08017314, 0x08017368) that would break from 0x088xxxxx. Every BL becomes `ldr rN,=target` (bit 0 set) plus a local BL to a local `bx rN` stub. 0x199A lives in the new pool. Never patch 0x080174A0: the shared Super Saiyan tick uses it for entries 5, 11, 16, 17 and 20. This replaces "copies" in the approach section above.
- New subsection "Task 6 requirements (Rulings 15 and 16)":
  - END test: 100 + bonus <= 127. Damage uses `0x80 - END` (re-checked: `0800f94a ldrb r0,[r6,#0x2] ; mov r1,#0x80 ; sub r0,r1,r0`). END 120 gives about 44 % of Super Saiyan damage taken.
  - Attacker overflow at 0x0800F974: LIKELY only.
  - The gate keeps lr on both exits (pop into a low register, then `mov lr`).
  - The gate reads the relocated table, never 0x081D967C.
  - Step EP cost >= 9 (the Super Saiyan tick drains 8 EP during the 160-frame step).
  - Decision: the gate skips the map word `[[0x086DB284]+0xC]`, as vanilla does while transformed.
- Open question 4 now says the EP cost may not fall below 9.
- `docs\RE-BIBLE.md`: one new line with these Task 6 rules.
- No byte order mark. No dashes.
