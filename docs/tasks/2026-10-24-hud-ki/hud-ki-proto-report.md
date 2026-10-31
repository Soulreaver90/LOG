# HUD and ki prototype report (r38 mockup 2)

Brief: `docs\tasks\2026-10-24-hud-ki\hud-ki-proto.md` (my ask, 2026-10-24 8:13 AM). Work files: `scripts\one-time\2026-10-24-hud-ki\proto\`. Bible rows (tag HKP): `scripts\one-time\2026-10-24-hud-ki\proto\bible_rows.md`.

I check it in mGBA.

Labels: C = CONFIRMED (bytes, listings or tests), L = LIKELY, S = SPECULATIVE.

---

## 1. Verdicts

| Item | Result | Label |
|---|---|---|
| Rebase of the approved mockup 1 HUD onto r38 | Built. All 35 regions held the r36 bytes in r38 before the write and hold the mockup 1 bytes after | C |
| Boss bar in the Buu's Fury look | Built, data only (image and step table). Both games use the same bar class | C (bytes, model), L (in game) |
| Ki pool (study section 6) | Built: transform fill, ki moves spend the pool, revert at 0, regular EP regen keeps running, yellow pool over the EP row, one pool for SSJ and SSJ2 | C (31 interpreter tests), L (in game) |
| Drain rate | SSJ: 1 every 20 frames (BF rate). SSJ2: 1 every 10 frames, the r27 LoG II step 0x199A. This differs from the brief (section 7) | C |
| Ki move in state 46 (ability 0, Vegeta hold) | Spec only. Found after the build: it drains EP and is not wrapped | C (gap), S (fix) |
| Items, scripts and the Senzu | Spec only. They raise the regular EP, not the pool | L |
| Gradual pool raise during the transform (BF style) | Not built. The pool fills at once at the end of the transform animation | C |
| Low-ki sound or flash | Not built | C |

---

## 2. Hooks with evidence

The prototype changes no vanilla code byte. Every hook is one pointer word. Each of the 8 hooked vtable words in the code region has one my table in `codemap.json`. The SSJ2 vtable word and the 22 ability words are outside the codemap.

### 2.1 Pool hooks (LoG II side)

| Hook word | Was | Now | LoG II proof | Label |
|---|---|---|---|---|
| `rom:0x24C5C` (vtable `0x08024C58` +4, SSJ tick) | `0x0889A8C7` (r27 tick) | `tick_ssj 0x08E1158A` | `@0x0889A8C8 bl 0x0889A8B0` (stretch check), then `@0x0889A8E2 ldr r2,=0x0889A789` `bx r2` (the r27 drain body) | C |
| `rom:0x88DE28` (vtable `0x0888DE24` +4, SSJ2 tick) | `0x0889A81D` | `tick_ssj2 0x08E1158E` | `@0x0889A84A ldr r1,=0x0000199A` `@0x0889A84C add r0,r0,r1` `@0x0889A84E str r0,[r4,#0x4]` (r4 = player +0x180) | C |
| `rom:0x25DB0` (vtable `0x08025D9C` +0x14, transform end) | `0x0801563D` | `fill_end` | State 35 anim tick `@0x080155E4` calls `@0x08011D4A`; at frame 0xA0 it calls vtable +0x14 = `@0x0801563C` = `transform(player, 1)` | C |
| `rom:0x256C0` (vtable `0x080256AC` +0x14, revert end) | `0x080157AF` | `empty_end` | State 36 anim tick `@0x0801358C` calls vtable +0x14 = `@0x080157AE` = `transform(player, 0)` at frame 0x40 | C |
| `rom:0x2409C` (HUD vtable `0x0802408C` +0x10, draw) | `0x08008BEF` | `hud_draw 0x08E1160A` | The draw pass `@0x08006BFA` reaches `@0x08008BEE` only through this word. HUD +0x15 = 0xFF forces a repaint (`@0x08008D74`-`@0x08008D78`) | C |
| `rom:0x25D4C` (state 34 +4, ki blast) | `0x08014DF5` | `st34` swap stub | `@0x08014E2A ldrh r0,[r1,#0x4]`, `@0x08014E2E strh r0,[r1,#0x4]` (EP -2 per repeated blast) | C |
| `rom:0x25CC0` (state 48 +8, beam) | `0x08015249` | `st48` | Accumulator +0x56 a frame, EP -= acc >> 8 | C |
| `rom:0x25F78` (state 49 +8, beam) | `0x0801539B` | `st49` | Same shape as state 48 | C |
| `rom:0x25CD4` (state 51 +8, charged ball) | `0x080156B7` | `st51` | EP -1 every 4 frames | C |
| 22 ability words `rom:0x1D9908`-`0x1D99DC` (test and action of abilities 0-4, 6-10, 13) | vanilla functions | swap stubs | Tests read `(s16) EP >= cost`. Actions write EP -= cost (`ep_sweep.txt`, 170 functions) | C |

How a swap works: if the leader is in a pool form and the guard byte is 0, the stub swaps record +4 (EP) with the pool. It calls the vanilla function, then swaps back. So the vanilla code spends the pool and the green EP stays.

### 2.2 Buu's Fury behavior (decomp quotes)

Decomp: `%USERPROFILE%\Documents\GitHub\buusfury-decomp\asm\`, read as data. The bars around decomp labels are left out below.

| BF behavior | Decomp quote | Label |
|---|---|---|
| SSJ tick calls the base tick first (regen keeps running) | `slice_000158.s:30136: BL loc_0800E1D0` | C |
| Accumulator step 0xCCD a frame (1 point per 20 frames) | `:30152: LDR r1, [pc, #0x21c]` `:30154: ADD r0, r0, r1` `:30155: STR r0, [r5, #0x14]` `:30156: LSR r0, r0, #0x10` `:30157: BEQ` | C |
| On overflow: pool (record +0x1E) minus 1 if not 0 | `:30165: ADD r1, #0x1e` `:30166: LDRH r2, [r1]` `:30168: BEQ loc_0800E44E` `:30172: MOV r2, #1` `:30173: SUB r1, r1, r2` | C |
| At pool 0 and HP not 0: switch state through vtable +0x28 | `:30183: ADD r0, #0x16` `:30185: LDRSH r0, [r0, r3]` `:30187: BEQ` `:30190: LDR r2, [r1, #0x28]` | C |
| Revert zeroes the pool | `buu.s:5377: ADD r0, r4, #0` `:5378: ADD r0, #0x1e` `:5379: MOV r1, #0` | C |
| Transform fills the pool from max | `buu.s:5539: ADD r0, r4, #0` `:5540: ADD r0, #0x20` `:5541: SUB r1, r0, #4` `:5542: LDRH r1, [r1]` | C (fill), L (gradual raise in BF) |
| HUD draws the pools against max ki | `slice_000158.s:24852: ADD r6, #0x1c` `:24855: LDRSH r1, [r6, r3]` (max ki) `:24856: ADD r0, r6, #2` `:24857: LDRH r0, [r0]` (pool +0x1E) `:24858: MOV r3, #0x29` `:24859: MUL r0, r3` `:24860: SWI 6`; the same for +0x20 at `:24867`-`:24871` | C |
| One pool for SSJ and SSJ2 | BF has two pool fields and two ticks. `0x0800E4C4` (`:30243`) drains +0x20 by (record +0x1C x 0x16 + a literal) >> 16 a frame (`:30261`-`:30280`). Which BF forms use which tick was not traced. One shared pool follows the brief and study section 6 | L |
| Ki moves spend the pool | No decomp line is quoted. This follows study section 6 | L |
| SSJ2 drains faster | A search of the decomp for the literal 0x199A returned nothing | S |

### 2.3 Prototype logic

- RAM `0x03003A00`: +0 u16 pool, +2 u16 tag (0x8000 + leader x 0x100 + entry), +8 u32 drain accumulator, +0xC HUD fill cache, +0xD swap guard.
- A pool form is a leader entry whose form object is `0x030021EC` (every SSJ) or `0x0888DE20` (SSJ2). Gohan or Goku in the r28 full-power stretch is excluded.
- A tag that does not match fills the pool to max EP and clears the accumulator and the guard. This also covers a leader swap and a save load.
- Tick: the base tick `0x08017029` with the cooldown kept, then the r27 gates (scene words `[0x03001FDC]` and `[0x03000E24]`, "in state" +0x2C), then the BF order: acc += step; on overflow pool -1, or at pool 0 with HP not 0 set state 0x24.
- HUD: fill = pool x 49 / max EP through the divide `0x08021F31`. A changed fill sets HUD +0x15 = 0xFF. After the vanilla draw, halfword writes paint the yellow pool image over the EP steps below the fill.

### 2.4 Boss bar

The two games use the same class. So the port is data only: the bar image and the step table.

| | LoG II (r38) | Buu's Fury |
|---|---|---|
| Constructor | `0x080104C0` (malloc 0x1C, vtable `0x08025748`) | `0x080195A8` (`slice_0153f2.s:8629`, vtable `0x0804CE28`) |
| Steps | 60 (table `0x086D60F4`, 16 B a step) | 53 (table `0x087198E4`, 4 offsets a step) |
| Image | `0x086D64B4` (0x200 B, one literal at `0x0801068C`) | `0x087196E4` (0x200 B) |
| OAM | 2 OBJ 32x8 8bpp at x 160 and 192, priority 0 | the same words, priority 1 |
| Messages | `0x08010628`: 9 repaint, 0xF clear target, 0x10 slide out | `0x0801971E` (`:8817`): 0x20 target, 0x11 clear, 0x12 remove, 0x13 slide out, 0xB repaint |
| Script | ext 85 full bar, ext 90 segment, ext 88 slide out | ext 143 full bar, ext 144 segment, ext 145 slide out |

- Port: the BF image is remapped into the LoG II image slot. The BF 53 steps go into the LoG II 60-step table (steps 53-59 point at pixels that are already cleared). The constructor math (a x 60 / 100) stays.
- Model check: `bossim.log2_bar` equals the live bar in `log2_poc_r34_scouter.ss1` and `.ss2` (Super Perfect Cell) at 512 of 512 bytes (C).
- Neither bar draws a name or a portrait (C for the object code).

Fights that show the bar in r38 (`boss_sites.txt`; 143 byte pairs, 103 decode, 40 do not):

- Full bar (ext 85): Frieza (set 48), General Tao (50, five sites), Wolf (146), Cooler (34, three), the spar partners Yamcha (156), Krillin (76) and Tien (121) on map 6,70, Android 19 (12), Cell Jr (31, three), T-Rex (123), the Goku spar (60, `rom:0x90910B`).
- Segment bar (ext 90): Triceratops King (127), Android 20 (14), Android 18 (11), Android 17 (9), Cell (28), Cell Nonperfect (29), Cell Perfect (30), Super Perfect Cell (58, 20-100 at `rom:0x3EB6F7`).
- Labels: C for Super Perfect Cell, the spar tables, the Goku spar and the Cell Games rows. L for the other decoded sites. S for the 40 pairs that do not decode.

---

## 3. Diff proof

Source: `proto\proof_proto.txt` (run by `proof_proto.py`).

| Check | Result |
|---|---|
| Mockup SHA-1 | `5f17f8fc9c31e7c60b44543c8868d02b18b8fd6c` |
| Built file equals `build_proto.plan` applied to r38 | True |
| Bytes that differ from r38 | 16,019 in 1,891 runs |
| Bytes outside a named region | 0 |
| Rebase regions hold r36 bytes before, mockup 1 bytes after | True, True (35 regions) |
| Window `rom:0xE11000`-`0xE11FFF` all 0xFF in r38 | True |
| r38 words naming the window | 0 absolute, 0 base-relative in the vtable ranges |
| Built words outside the window naming it | 22 ability words (absolute) and 9 hook words (base-relative). Every one is a named hook word |
| Words naming the boss image / table | `0x1068C` only / none |
| IWRAM `0x03003A00`-`0x03003A0F` in 125 save states | zero in 125 of 125 |

Named regions (each run is in the proof file):

- Mockup 1: 2 OAM pool words, the HUD frame, the HP, EP, EXP and cooldown tables, 29 icon images (incl. Z2).
- Boss bar: table `rom:0x6D60F4`-`0x6D64B3`, image `rom:0x6D64B4`-`0x6D66B3`.
- Pool: image `rom:0xE11000`-`0xE114FF`, code and literal pool `rom:0xE11500`-`0xE1181B`.
- 9 vtable words and 22 ability words (section 2.1).

> [!NOTE]
> One proof line is wrong. It says the ROM words naming `0x03003A00`-`0x03003A0F` are all data. `0x3003A00` is the new code's own literal pool word. `0x3003A04` and `0x3003A0F` are r38 data words at `rom:0x2E646C` and `0x2F3F58`.

Palette (`palette_proto.txt`): 15 BF colors remapped. Max dE 14.1 (BF 33 dark red to r38 25, boss bar). Next 12.4 (BF 30 pale yellow to r38 123, pool). Index 168 is excluded because the Cell fight palette RAM differs there.

---

## 4. Tests

- `py -3 -P scripts\one-time\2026-10-24-hud-ki\proto\test_proto.py`: 31 tests, all OK.
- Classes: Layout, PoolRef, Ticks, FillEmpty, Swap (incl. a run of the real HUD icon hook `0x0888E356`), Hud.
- The interpreter is `test_ssj2.Cpu` (read only), extended with mul, asr, OBJ VRAM and a byte-store log.
- The tests do not cover the real frame loop, the scene manager, the sound calls or DMA timing. They run single methods with a built record.
- `build_proto.py --check` and `proof_proto.py` also pass (section 3).

---

## 5. My steps (mGBA)

Files in `builds\mockups\2026-10-24-hud-ki\`:

- `log2_poc_r38_bfhud2_spar.gba` with `log2_poc_r38_bfhud2_spar.sav`
- `log2_poc_r38_bfhud2_scouter.gba` with `log2_poc_r38_bfhud2_scouter.sav`

The two ROMs are byte copies of `log2_poc_r38_bfhud2.gba`. Keep each .gba and its .sav in the same folder with the same base name. mGBA then loads the .sav by itself. "File 1, 2, 3" below are the in-game save files, not mGBA state slots.

### 5.1 HUD look

1. In mGBA, use File > Load ROM and open `log2_poc_r38_bfhud2_spar.gba`.
2. On the title screen, continue and load file 1.
3. Pass: the HUD looks the same as the approved mockup 1 (BF frame, bars and icons).

### 5.2 Ki pool

1. Open `log2_poc_r38_bfhud2_spar.gba`. On the title screen, load file 2 (Gohan at map 11,1).
2. Change the selected ability the same way as in r38 until the HUD shows the Z icon (ability 12). Press B.
3. Pass: at the end of the transform animation (about 160 frames), a yellow bar covers the full ki row at once.
4. Select ability 2 (ki blast) and fire with B a few times.
5. Pass: the yellow gets shorter. The green regular ki under it does not go down.
6. Wait without ki moves.
7. Pass: the yellow goes down by 1 point every 20 frames. From full it takes about 45 s in SSJ (134 points).
8. Pass: about 20 frames after the yellow reaches 0, Gohan reverts. The yellow is gone after the revert.
9. Pass: regular ki keeps regenerating in the form, about 3% every 10 s.
10. Optional: do the same with the Z2 icon (SSJ2). Pass: one yellow pool, the same as SSJ, but it drains in about 22 s.
11. Optional: load file 3 (Goku at 9,1, in the full-power stretch). Pass: no yellow pool. The r28 behavior stays.

### 5.3 Boss bar

1. Open `log2_poc_r38_bfhud2_spar.gba`. Load file 1 (Gohan at 6,3).
2. Walk up into the door and start the Goku spar.
3. Pass: a slanted BF-style bar slides in at the top right. It gets shorter as Goku takes damage.
4. Optional: use File > Load State File... and pick `builds\log2_poc_r34_scouter.ss1` (Super Perfect Cell). The F-key slots look only for a state with the ROM's own base name, so use the menu. Caveat: an old r34 state, so other parts can look wrong. Pass: the BF bar shows.

---

## 6. Risks

- **State 46 gap (C).** Vegeta's hold move (ability 0, state 46 +8 `0x08015078`) spends regular EP in a form. The fix is one word: vtable `0x080258B4` +8 to a `swap_state` stub. It is not built (S).
- **IWRAM boot state (S).** The crt0 fill stops at `0x0300391C`. mGBA zeroes RAM. On hardware a stale guard byte can block the swap until the next pool fill.
- **Behavior changes (L).** Regular EP regen now runs in the full-power stretch and in scenes. The r27 full-power tick is no longer referenced.
- **Items and scripts (L).** Senzu, EP items and scripts raise regular EP, not the pool.
- **Other forms (C).** Super and Namek forms stay on regular EP.
- **Palette (C).** dE 14.1 on one boss bar color. A real build needs the PCN census rerun.
- **Proof text (C).** The `0x3003A00` line (section 3 note).

---

## 7. Final decisions

1. SSJ2 drain rate: keep 0x199A (1 every 10 frames, the r27 rate), or use the brief's 1 every 20 frames.
2. SSJ2 pool color: the same yellow, or orange.
3. Should the step gate test the pool or the regular EP?
4. Should regular regen run in scenes and in the stretch?
5. Should Super and Namek forms use the pool?
6. Transform input: keep Z and Z2.
7. Icon art and the palette remap: accept the dE 14.1 color, or pick another.
8. Build a "b" mockup with the state 46 word?

---

## 8. Deviations from the brief

- I edited `test_proto.py` once with Python `open('w')`. Every other edit was made in place.
- The SSJ2 drain is 1 every 10 frames (the r27 step 0x199A), not the brief's 1 every 20 frames. The mockup cannot be overwritten, so this stays as final decisions 1.
- The state 46 gap was found after the build. It is documented as spec (section 6). No "b" file was built.
- Two BF behaviors (ki moves spend the pool, one pool for both forms) have no decomp quote (section 2.2, L).

---

## 9. Files

Folder: `scripts\one-time\2026-10-24-hud-ki\`

- Mockups (`mockups\`):
  - `log2_poc_r38_bfhud2.gba` (SHA-1 `5f17f8fc...`)
  - `log2_poc_r38_bfhud2_spar.gba` and `.sav` (sav SHA-1 `4ca6f109...`)
  - `log2_poc_r38_bfhud2_scouter.gba` and `.sav` (sav SHA-1 `d2fa5e1a...`)
- Tools (`proto\`): `common.py`, `build_proto.py`, `test_proto.py`, `proof_proto.py`, `bossim.py`, `boss_check.py`, `boss_sites.py`, `ep_sweep.py`, `dbg_trace.py`, `dbg_refs.py`
- Outputs (`proto\`): `proof_proto.txt`, `listing_proto.txt`, `palette_proto.txt`, `boss_check.txt`, `boss_sites.txt`, `ep_sweep.txt`, `proto_hud.png`, `boss_bars.png`, `bible_rows.md`
