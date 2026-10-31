# HUD and ki study: the Buu's Fury HUD on LoG II, and the Buu's Fury Super Saiyan ki (report)

Date: 2026-10-24. Brief: `docs\tasks\2026-10-24-hud-ki\hud-ki-study.md`.

Labels: **C** = CONFIRMED (code, bytes or a test quoted here). **L** = LIKELY. **S** = SPECULATIVE. Buu's Fury is "BF". LoG II addresses are r36 (`builds\log2_poc_r36.gba`, SHA-1 `eb4a1b41...`) unless marked vanilla. Work files: `scripts\one-time\2026-10-24-hud-ki\`. Bible rows: `scripts\one-time\2026-10-24-hud-ki\bible_rows.md` (tag HKS).

**How I read the ask.** "Inject that system into buus fury" is read as: bring the BF Super Saiyan ki system into LoG II, because the merged game runs on the LoG II engine. The evidence supports this reading: BF already has the system (section 1), so an injection into BF would change nothing.

---

## Verdicts

| Question | Verdict | Label |
|---|---|---|
| BF Super Saiyan has its own ki on top of the regular ki | **Yes.** Each character record has two form ki pools: +0x1E (Super Saiyan) and +0x20 (Super Saiyan 3). A transform fills the pool to max ki. In the form, ki moves spend the pool, not the regular ki. The pool drains over time, and at 0 the form reverts. The regular ki stays and still regenerates. The HUD draws the pool in yellow (orange for Super Saiyan 3) over the same ki row. | C |
| HUD swap (BF look on LoG II) | **S for the look, data only** (built and proved as mockup 1). **M for full parity** (exact bar lengths, all 28 cooldown pixels, final icon art, the pool overlay). | C (mockup bytes), L (in game) |
| Ki system port to LoG II | **M for the smallest prototype** (Super Saiyan and Super Saiyan 2 drain their own pool, fill on transform, overlay on the EP row). **L for BF parity** (ki moves spend the pool, regen in forms, all r27/r28 hooks agree). Not built: it needs code I cannot prove by reading. Spec in section 6. | L |
| "A second ki bar" (brief example) | BF has **no second bar**. It overlays the pools on the one ki row. A pool larger than the regular ki hides the regular ki. | C |

> [!WARNING]
> **My conflict, not resolved.** BF steps to Super Saiyan 3 with a **second ability** (ability 22, "Z3"), not with the same B press. Our decision row "The transform icon shows what B does next" uses one Z that steps base, Super Saiyan, Super Saiyan 2. The design doc 8.2 "My call" assumed BF steps on the same input. That assumption is refuted. I decide which input LoG II keeps.

---

## 1. BF Super Saiyan ki (task 1)

Our disassembly (`scripts\one-time\2026-10-24-hud-ki\q.py bf dis`) is the evidence. The decomp has names only for branch targets, so I give the decomp line of each routine (`decomp_line.py`, label-checked). The Z and Z3 tests are raw INCBIN bytes in the decomp (`buu.s:1934`, `:1940`), so for them only our disassembly applies.

### 1.1 Where the pools live (C)

- Character record (0x68 bytes): +0x16 HP, +0x18 max HP, +0x1A ki, +0x1C max ki, **+0x1E Super Saiyan pool, +0x20 Super Saiyan 3 pool**, +0x56 ki cost scale.
- Appearance table `rom:0x6B82EC` (54 x 24 bytes, decomp `unk_086B82EC`). +0 flags: **bit 0 = use pool +0x1E, bit 1 = use pool +0x20**. +0x16 transform target, +0x17 revert target. Goku: entry 0 > 3 (Super Saiyan, flags 0x51) > 5 (Super Saiyan 3, flags 0x52) > 0.

### 1.2 Ki moves spend the pool (C)

The three ki helpers pick the pool from the current entry flags (`slice_000158.s:40605`, `:40626`, `:40673`):

```
08013492 get:   flags bit 1 ? [r0+0x20] : flags bit 0 ? [r0+0x1e] : (s16)[r0+0x1a]
080134b8 test:  cost = (char[0x56] * n) >> 4 ; return active_pool >= cost
08013504 spend: active_pool -= n, clamp at 0
```

- Callers: 24 of the test, 22 of the spend (with the scaled spend `0x08013598`). They include the ability tests and actions (`0x08019D3C` to `0x0801A61E`).
- So a ki blast in Super Saiyan spends the Super Saiyan pool. The regular ki +0x1A is not touched.

### 1.3 Drain and revert (C)

| Form | Tick | Drain | At 0 |
|---|---|---|---|
| Super Saiyan (form object `0x03001B78`, state vtable `0x0804B348`) | `0x0800E3E6` (`slice_000158.s:30133`) | +0xCCD per frame; 1 from +0x1E per overflow (1 every 20 frames, the same rate as LoG II) | `0800e458`: state 0x18 when HP is not 0 |
| Super Saiyan 3 (`0x03001B80`, `0x0804B9A4`) | `0x0800E4C4` (`:30243`) | max ki x 0x16 + 0x3333 per frame; the overflow comes off +0x20 | pool 0, state 0x18 |
| Entries 17, 30, 37 (`0x03001B7C`) and 7, 8, 38 (`0x03001B84`) | base tick only | none | none |
| Entry 25 (`0x03001B8C`) | `0x0800E5F4` | frame timer | state 0x18 |

- State 0x18 is the revert: state table `0x0807273C` + 0x60 = `0x03002BB4` (static constructor `0x08048520`), vtable `0x0804CC58` +0x24 = `0x0801C206`. That routine writes the +0x17 entry and **zeroes both pools** (`buu.s:5377`). C.
- The drain only runs when the current state object's vtable +0x18 returns nonzero and the player's vtable +0x34 (10) returns 0. What those states are is not traced. S.

### 1.4 Regular ki regenerates in a form (C)

- Both drain ticks start with `bl 0x0800E1D0`, the base tick (`slice_000158.s:29870`).
- The base tick decrements the transform cooldown only when the entry has neither pool bit (`0800e1fe`-`0800e218`).
- Every 596 frames it adds 3 % of max to the leader's regular ki and 5 % HP and ki to the other members.
- LoG II differs: Super Saiyan replaces the base tick, so no regen runs in a form (bible row "Super Saiyan has no base-form tick").

### 1.5 Pool life cycle (C for the writers read, L for completeness)

1. Z (ability 20) or Z3 (ability 22) builds the transform state (vtable `0x0804E2B0`).
2. During the animation, +8 `0x0801C4F4` raises the pool: max ki x frame / count (`slice_01c3f2.s:125`). L for the frame fields.
3. At the end, +0x24 `0x0801C312` (`buu.s:5471`) writes the +0x16 entry, sets the leader cooldown to 0x37FFF, and sets **pool = max ki** (+0x20 for a bit 1 entry, else +0x1E; `buu.s:5539`).
4. An interrupted transform (`0x0801C552`) zeroes the pool.
5. Super Saiyan to Super Saiyan 3 keeps +0x1E. Super Saiyan 3 reverts to base (entry 5 +0x17 = 0), so both pools go to 0.
6. The transform spends no ki: no spend call in the transform methods by the BL-caller shape. The test only needs the active pool >= 10 x scale. L.
7. **Other pool writers (all read):**
   - Script ops: `0x080004BA` pushes the leader's active ki, and `0x0800051A` sets it, clamped to 0 and max ki (handler words `rom:0x550D0`, `rom:0x554B0`). So a script ki refill in a form refills the **pool**, not the regular ki.
   - `0x0801058A`: when the leader's entry has flags bit 6, it zeroes both pools and writes the +0x17 entry (a revert with no animation). No BL or pointer reference by two shapes.
   - `0x080229B0`: builds a 0x68-byte record from a template (two calls in one routine; L: a scene or fusion setup). For a bit 0 entry it copies a halfword into +0x1E.
   - Shapes used (`bf_pool_writes.py`): A `strh [rb,#0x1e]` or `#0x20`; B `add rb,#imm` then `strh [rb,#0]`. Of the 45 A sites, only the spend helper and one stack variable sit in functions that load the appearance table. The rest are other structures (not all read).
   - Direct writes of the regular ki +0x1A (`bf_ki1a_writes.txt`, same two shapes): 41 sites, **none** in the ability and ki-move code `0x08019D00`-`0x0801C6FF`. Writers I read: level-up growth (`0x08013726`), a two-record merge (`0x08013832`, ki = (a + b) x 0x9A >> 8) and a full refill (`0x080139B6`). These raise the regular ki, not the pool.
   - Label: C for the writers read; L that the list is complete. A write through another offset or a register index would not show. Whether a save keeps the pools is not traced (S).

### 1.6 Input (C)

- Ability table `rom:0x71DAF8` (decomp `unk_0871DAF8`): 24 entries of 24 bytes `{kind, icon usable, icon dim, u16 x2, test, action}`.
- **Z (20):** in Super Saiyan the test returns 1 and the action reverts. In Super Saiyan 3 it returns 0 (dim). In base it needs a combat map, cooldown 0 and ki >= 10 x scale.
- **Z3 (22):** in Super Saiyan 3 it returns 1 and reverts. Otherwise it needs Super Saiyan, a +0x16 target, and Super Saiyan pool >= 10 x scale.
- So Z toggles base and Super Saiyan; Z3 toggles Super Saiyan and Super Saiyan 3.

### 1.7 HUD (C for code, L for the render)

`0x0800B99C` (`slice_000158.s:24724`) computes six fill bytes, then draws the ki row in layers:

```
b0 = HP*41/maxHP   b1 = ki*41/maxKi   b2 = pool1E*41/maxKi   b3 = pool20*41/maxKi
b2 = max(b2,b3) ; b1 = max(b1,b2)
ki row pixel i:  i < b3 orange image 0x08713FD8 | i < b2 yellow image 0x08713AD8 | i < b1 frame green | else index 1
```

Render from ROM data: `scripts\one-time\2026-10-24-hud-ki\huds_compare.png`. Rows show BF base (green), Super Saiyan (yellow over green), Super Saiyan 3 (orange over yellow over green), and the cooldown (the yellow triangle goes dark).

---

## 2. LoG II today (task 2)

### 2.1 EP drain in forms (C, re-checked on r36)

| Form | Tick (r36) | EP |
|---|---|---|
| Super Saiyan (vtable `0x08024C58`) | +4 = `0x0889A8C7` fullpower tick > r27 tick `0x0889A788` | leader EP -1 per 0xCCD overflow (every 20 frames); at EP 0 and HP not 0, state 0x24 (revert). No drain in a scene (r27) or in the r28 stretch for leader 0 or 4 |
| Super Saiyan 2 (`ssj2_form` object `0x0888DE20`, vtable `0x0888DE24`) | +4 = `0x0889A81D` | same shape, 0x199A (1 EP every 10 frames) |
| Rage (vtable `0x08024E4C`) | vanilla tick `0x0801710E` | no EP code; HP regen only |

So in LoG II the form drains the **regular EP**. There is no pool. Ki moves spend EP directly: 11 ability actions (`ldrh [rec,#4] ; sub #cost ; strh`, for example `@0x0801317E`) and the ki blast `@0x08014E2E` (EP -2). List and limits: bible rows, `ep_writes.txt`.

### 2.2 HUD code and graphics (C)

- Draw `@0x08008BEE`, every frame (bible row on the HUD caller chain).
- Three 8bpp OBJ from pool words `rom:0x8E80` / `0x8E84` / `0x8E88`: 32x16 at x 8 (buffer 0x000), 16x16 at x 40 (0x200), 32x16 at x 56 (0x300).
- Buffer: frame `rom:0x6D7B54` (0x300 B) at 0, ability icon (0x200 B) at 0x300.
- Bars: HP 48 steps, EP 49, EXP 69, cooldown 5 levels over 20 pixels. Tables and formulas are in the bible rows.
- Form icon: the selected ability's icon. r36 hook `0x0888E356` gives the Z2 pair (`rom:0x88DE3C` / `rom:0x88E03C`) through `step_ok` `0x0888E306`.
- **Model check:** `hudsim.log2_fills` equals the HUD's 0x500 OBJ VRAM bytes in 15 states (`state_hud_check.py`), 0 bytes differ. Two of them have partial fills (HP 46, EP 41, cooldown 4).

---

## 3. HUD swap feasibility (task 3)

| Part | LoG II | BF | Same? |
|---|---|---|---|
| OBJ layout | 3 OBJ, 8bpp, 80x16 at x 8 | same pool words | Yes |
| Buffer order | frame at 0, icon at 0x300 (icon right, x 56) | icon at 0, frame at 0x200 (icon left, x 8) | No: swap the x of two pool words |
| Frame | `rom:0x6D7B54`, 0x300 B | `rom:0x7137D8`, 0x300 B | Same size, different art and palette |
| Icons | 32x16, with LoG II bar tips | 32x16, with the BF left frame piece and the yellow triangle | Same size; every icon must be re-made |
| Bars | HP 48, EP 49, EXP 69, cooldown 20 px | HP 41, ki 41, EXP 72, cooldown 28 px | Step counts are code immediates |
| Pool overlay | none | yellow and orange images | Needs code and RAM |
| Low-HP sound | none | HP x 5 <= max, every 60 frames | Code, optional |

**What a swap needs:** graphics (frame, 27 icon images), layout data (two pool words, four tables), and code only for exact parity.

**Blockers for an exact copy:**

1. Palette: 29 BF colors map to r36 indices with max dE 14.1. Seven are above dE 8 (`mock1_palette.txt`). An exact match needs palette edits (two palette copies, and states keep the old palette RAM). The remap target `rom:0x1DA6C8` equals the live OBJ palette RAM in r36 `.ss2` at all 29 target indices (only 0 and 168 differ there). C.
2. EXP has 69 steps (`mov r7,#0x45` is code). The mock ends the bar 3 px short.
3. The cooldown list holds 20 offsets in place (BF uses 28). At the highest cooldown, 8 triangle pixels stay lit in the mock.
4. Icon art: the mock puts each LoG II picture into the BF box. Final art is my call (BF has close art for about 8 of the 14).
5. The pool overlay needs the ki port (section 4).
6. A state saved before the change shows the old HUD tiles until something forces a redraw.

---

## 4. Ki system port feasibility (task 4)

| What LoG II needs | Kind | Notes |
|---|---|---|
| One pool value | RAM | The 28-byte record is full. Only the leader is transformed outside the r28 stretch, so one u16 is enough. Candidate: free IWRAM in `0x0300391C`-`0x030062FF` (L). It is not cleared at boot, so code must write it before it reads it. |
| Fill on transform | hook | `transform` `@0x08014D58` (entry write `@0x08014D92`). Not the form enter (+8): message 9 (menu close) also calls enter, so a fill there would refill on every menu close. |
| Drain from the pool | hook | The r27 ticks `0x0889A788` and `0x0889A81C`: take from the pool, not record +4; revert at pool 0. Keep the scene pause and the r28 stretch return. |
| HUD overlay | hook and art | After the EP loop (`0x08008DDA`-`0x08008DF8`), before the DMA at `0x08008E42`. The redraw key (`0x08008D44`-`0x08008D78`) must include the pool fill, or a pool change alone does not redraw. HUD +0x16 and +0x17 are not written (L). |
| Spend from the pool | hooks | 11 ability actions and their tests, the ki blast, the charged ball. Not complete by two shapes (bible row). |
| Regen in forms | hook | BF runs the base tick in forms. LoG II's base tick `@0x08017028` also counts down the cooldown, so a port needs a regen-only copy. |
| Agreement | | `step_ok` tests EP >= 10 (should it test the pool, as BF Z3 does?); knockout enter (`rom:0x89A976`), `switch_characters` and `appearance_revert` change the entry without a fill; r28 stretch saves load in Super Saiyan with an unset pool. |

**Effort:** smallest prototype **M**; full BF parity **L**.

**Smallest prototype:** the Super Saiyan and Super Saiyan 2 ticks drain the pool; the transform fills it to max EP; the HUD draws it in yellow over the EP row. Ki moves still spend EP. This is spec only (section 6).

---

## 5. Mockup 1: the BF HUD look on r36 (built, data only)

**File:** `builds\mockups\2026-10-24-hud-ki\log2_poc_r36_bfhud.gba`, SHA-1 `d2965d3c940b9652393781de52f68cf960c00f58`. `.sav` (SHA-1 `159601a3...`) and `.ss2` (SHA-1 `4487d1d3...`) are byte copies of r36. Every file was made by exclusive create. Not in the build chain: no line in `build_list.txt` or `build-log.md`.

**Changes** (`build_mock1.py`; no code byte, no repoint):

| Region | Change |
|---|---|
| `rom:0x8E80`, `rom:0x8E88` | OAM pool words swapped: buffer 0x300 (icon) at x 8, buffer 0 at x 56 |
| `rom:0x6D7B54` (0x300) | BF frame bytes 0x100-0x2FF, then 0x000-0x0FF, remapped to r36 indices; EXP steps 69-71 painted empty |
| `rom:0x3B5358` HP, `rom:0x3B5658` EP | 48 and 49 steps placed on the BF 41-step paths (step i to BF step i x 41 / 48 or / 49) |
| `rom:0x3B5968` EXP | 69 steps on BF EXP steps 0-68 |
| `rom:0x3B5B90`, `rom:0x3B5BE0` | cooldown: BF triangle pixels 0-19; counts 0, 7, 13, 18, 20 |
| 27 icon images | BF empty box `rom:0x7148D8` (remapped) with the LoG II picture (rows 2-9, columns 13-28) at rows 2-9, columns 3-18; 25 ability images and the Z2 pair |

**Proof** (`proof_mock1.py`, output `mockups\mock1_proof.txt`):
- 13,247 bytes differ in 1,582 runs. **0 changed bytes are outside a named region.**
- RAM scan of the five r36 states: the only words that name a changed byte are HUD icon pointers (`0x086D7754`, `0x086DAE7C`; the address stays, the art changes) and one word `0x086DAE28` in ss3 (not explained; L: stale data).
- Still image `mockups\mock1_hud.png`: rendered by `hudsim` from the mock ROM bytes only. The layout comes from the pool words; the frame, tables and icons come from the addresses the code loads. It shows the r36 vanilla HUD, the mock at the ss2 fills next to the BF HUD from its own ROM, and the mock at partial HP, EP, EXP and cooldown, with Z bright and dim and the Z2 pair.

**My test steps (mGBA):**

1. Open `builds\mockups\2026-10-24-hud-ki\log2_poc_r36_bfhud.gba`. mGBA loads `log2_poc_r36_bfhud.sav` beside it.
2. Continue any slot. In the field, look at the top-left HUD. You should see: the ability icon in a black box at the left, a yellow triangle, then the red HP bar over the green EP bar, a thin blue EXP line under them. It should match row 2 of `mock1_hud.png`.
3. Or use File > Load State, slot 2 (Goku, full HP and EP, ki blast). Right after the load, the HUD can look mixed for a moment. Press L once: the HUD redraws.
4. Press L to cycle abilities. Each icon shows in the BF box at the left.
5. Fire a ki blast (B). The green EP bar gets shorter from the right. Take a hit: the red HP bar gets shorter.
6. Press L until the Z icon shows: it is bright in the BF box (state 2: combat map word 1, cooldown 0, EP 139). In state 2, Goku is in the r28 full-power stretch (flag 149 set, flag 195 clear), so after Z he stays Super Saiyan, the Z turns dim, and the triangle does not change.
7. Optional cooldown check, from a save outside that stretch: transform, then revert. The yellow triangle goes dark and fills again in steps over about 21 seconds. Expected mock limit: 8 pixels at its top left stay lit while the cooldown is high.
8. Pass: the HUD matches `mock1_hud.png`, other screens do not change, and the game does not crash.

**Mockup 2 (a second bar or the pool overlay):** not built. It needs new code at three hooks and new RAM. I cannot prove that by reading. See the spec below.

---

## 6. Spec: smallest ki prototype (not built)

Goal: Super Saiyan and Super Saiyan 2 have their own ki pool, as in BF. EP is kept for later.

1. **RAM.** One u16 `form_ki` at a free IWRAM word (candidate `0x03003A00`; zero in 114 states, no code pool word names it). Write before read.
2. **Fill.** Hook `transform` after the entry write `@0x08014D92`. When the new entry's form object is `0x030021EC` (Super Saiyan) or `0x0888DE20` (Super Saiyan 2), set `form_ki` = leader record +6 (max EP). My choice for Super Saiyan to Super Saiyan 2: refill one pool (simple) or keep two pools (BF style).
3. **Drain.** Re-encode the two r27 ticks (`rom:0x89A788`, `rom:0x89A81C`) with the same scene and stretch checks. Take 1 from `form_ki` per overflow. At 0 and HP not 0, set state 0x24. Do not touch record +4.
4. **HUD.** A hook after the EP blanking: when the leader's entry is a pool form, draw `form_ki` x 49 / max EP steps of the EP row in yellow (a yellow copy of the EP pixel colors, or a 0x500-byte overlay image like BF `0x08713AD8`). Put the pool fill in the redraw key (HUD +0x16, L-free).
5. **Agreement.** `step_ok` and the Z gate: decide EP >= 10 or `form_ki` >= 10. Knockout, `switch_characters`, `appearance_revert` and ext 73: the pool is only read while the leader is in a pool form, so stale values are harmless; the r28 stretch load must fill `form_ki`.
6. **Tests.** Interpreter tests in the style of `test_ssj2.py`: fill on step, drain rate, revert at 0, the HUD overlay pixels, and no EP change in a form.
7. **Full parity (L):** a `get_active_ki` helper used by all 11 ability tests and actions, the ki blast and the charged ball; a regen-only base tick in forms.

---

## 7. Risks

- The free IWRAM claim rests on 114 states and one ROM shape. A deeper stack or a computed pointer would not show. L.
- The mock's icon art is mechanical (picture pasted into the BF box). It is not final art.
- BF render rows are from code and ROM bytes; no BF save state was checked. L.
- The BF drain gate states (vtable +0x18, +0x34 (10)) are not traced. S.
- The mock draws new pixels of existing indices (for example `pal:3`, `pal:216`, `pal:25`) in the HUD frame and icons. A real build must rerun the PCN palette census. No NEVER DRAWN index (172, 174, 178, 218, 239) is used.

## 8. Open items

1. Me: one Z that steps (our rule) or BF's Z plus Z3 (section 1.6, warning above).
2. Me: palette accuracy for the HUD (accept dE up to 14.1, or edit palette indices).
3. Me: icon art for the BF frame (keep LoG II pictures, use BF art, or redraw).
4. Me: one pool or two for Super Saiyan 2.
5. Bible: merge `scripts\one-time\2026-10-24-hud-ki\bible_rows.md`; it corrects the FRM row "Buu's Fury Z3 HUD drawing not traced" and `re-forms.md` section 4.
