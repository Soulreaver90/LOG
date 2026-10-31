# r20: Rage stats +20, status portraits match the dialog art, mid remaster portraits

Base: r19 `edd3df2e`. Result: `archive\builds\log2_poc_r20.gba`, SHA-1 `9b52833447b38db0e2b3b2c7b374b5ce389cc5a7`. The whole suite runs 345 tests, and all pass.

Labels: CONFIRMED means proven by script output, a byte compare or a code run in this session. LIKELY means inferred. SPECULATIVE means not checked.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| Ask | State | Evidence |
|---|---|---|
| "keep it as a +20 for the Cell [fight]" | Done: `patches\rage_stats.py` | Sections 2, 5 |
| "The portrait is what I meant" (Rage status page showed the armor portrait) | Done: `status_portrait` in the build, Rage shows gi SSJ2 117 | Sections 3, 5 |
| "mid is great": five mid portraits as dialog art | Done: `patches\portrait_remaster.py`, SSJ2 with the 10:02 AM chest shading | Sections 4, 5 |
| Build, save, states | Done | Sections 6, 7 |
| Diff proof r19 to r20 | PASS | Section 8 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check | The proof is code runs and bytes. Test plan in section 9. |
| Status twins 116, 118, 120 cleanup | Dead data now (section 4). Not removed, as the brief says. |

---

## 2. Task 1: Rage bonus (CONFIRMED code, LIKELY in game)

**Vanilla Rage apply** (`vt_form_rage` `@0x08024E4C` +0, word `rom:0x24E4C` = `8D 22 FF FF`, base-relative to `0x080170D9`):

```
080170d8  push {r4,lr}
080170da  add r4,r1,#0          ; r4 = player
080170dc  add r0,r4,#0
080170de  add r0,#0xff
080170e0  add r0,#0x61          ; player +0x160
080170e2  mov r1,#0x64          ; 100
080170e4  strb r1,[r0,#0x0]     ; STR = 100
080170e6  strb r1,[r0,#0x1]     ; POW = 100
080170e8  strb r1,[r0,#0x2]     ; END = 100
080170ea  mov r1,#0x80
080170ec  strb r1,[r0,#0x3]
080170ee  strb r1,[r0,#0x4]
080170f0  lsl r1,r1,#23         ; 0x40000000
080170f2  add r0,#0x28
080170f4  bl 0x80265c4          ; +0x188 walk speed
080170f8  add r0,r4,#0
080170fa  add r0,#0xff
080170fc  add r0,#0x8d          ; player +0x18C
080170fe  ldr r1,=0x40500000    ; pool rom:0x17268
08017100  bl 0x80265c4          ; run speed
08017104  mov r0,#0x0
08017106  add r4,#0xff
08017108  add r4,#0x81
0801710a  str r0,[r4,#0x4]      ; +0x184 = 0
0801710c  pop {r4,pc}
```

**Nothing else fills to max (CONFIRMED by listing):**
- Tick `@0x0801710E`: HP regen only (1 % of max per 0xCCD overflow). No stat write.
- Enter `@0x08017158` and leave `@0x08017174`: start and stop sound 55 only.
- Menu: message 8 calls only vtable +0xC, message 9 only +8 (`@0x080089DC`, `@0x08008A04`). Neither calls apply.

**Change:**
- New apply at `rom:0x89A55C` (0x68 bytes). It reads the leader record STR, POW, END (+0x0A/+0x0C/+0x0E >> 8), adds 20 and stores each as a u8. This is the same code shape and cap rule as `ssj2_form`'s apply: no clamp, and END 100 + 20 = 120 stays <= 127.
- Kept from vanilla Rage: 0x80 at +0x163/+0x164, walk `0x40000000`, run `0x40500000` (through `0x080265C4` via `bx r2`), +0x184 = 0.
- `rom:0x24E4C` is repointed to the new apply. The IWRAM form object `0x030021E4` keeps the same vtable. So tick, enter, leave, the sound, the forced form in the Cell script and HP regen stay vanilla.
- The old apply stays in the ROM, with no reference.
- The status page needs no change: `status_bonus` shows live - base, so it reads "70+20".

**Scope (CONFIRMED by aligned-word scan, LIKELY for run-time ext 73 arguments):**
- Form object `0x030021E4` appears only in appearance entry 4: vanilla `rom:0x1D96DC`, reverse lookup copy `rom:0x800060`, live table `rom:0x88DCB4`. The vtable appears only in the init pool `rom:0x2330C`.
- Entry 4 is set 160, the gi Rage. No entry has +4 = 4, so no transform leads to Rage.
- So the change applies to every Rage use, and every Rage use is the gi Rage of the Cell fight (ext 73 (0, 160)). Debug menus could also set entry 4 (SPECULATIVE).

---

## 3. Task 2: `status_portrait` in the build (CONFIRMED by test run, LIKELY in game)

- Added after `status_bonus`, at the end of the list, as its own usage line shows. A middle position would move every later allocation (`ssj2_idle`, the cutscene hook, `npc_gi`, `rage_text`) and break the r19 diff.
- `tests\test_status_portrait.py` now builds the r19 list (with `rage_text`) as "before". No SHA-1 pin. 12 tests pass.
- `patches\status_portrait.py`: only the docstring usage line changed.
- My check, run on the full r20 list: entry 4 (Rage) asks portrait() for +2 = 61. The hook maps it to 117, and the page shows the mid SSJ2 PNG pixel for pixel in the OBJ colors. In r19 the same page showed +3 = 12, the armor Rage twin (test `test_r19_status_page_showed_the_armor_rage_twin`).

---

## 4. Task 3: mid remaster portraits (CONFIRMED bytes, LIKELY in game)

- **Copies:** `art\portrait-sources\remaster\final_r20\` holds `goku_mid_A.png` (`C008893A`), `vegeta_mid_A.png` (`284CDB8A`), `gohan_ssj_mid_A.png` (`72DFFFA0`), `gohan_ssj2_mid_A.png` (`C96A9E27`), `gohan_base_mid_A.png` (`7088A3D2`). I copied them after the coordinator's "SSJ2 ready". Each copy equals its source by SHA-1. All five sources show 10:04:22 AM, not only SSJ2, so my script rewrote all five.
- **Checks:** 64x64 indexed. Every index is one the USA dialog portraits (ids 26-114) use. None is 0 or 168. The PNG palette equals the ROM OBJ palette at every used index. Colors: 23, 35, 24, 24, 18 (pool limit 64).
- **Patch `patches\portrait_remaster.py`** (one patch for all five, after `rage_text`):
  - It writes raw type 0 frames `{0, 0x1000, pixels}`: 63 `rom:0x895468`, 106 `rom:0x896470`, 115 `rom:0x897478`, 117 `rom:0x898480`, 119 `rom:0x899488`.
  - It repoints those five words in the live block `rom:0x894EAC` (`rom:0xBE10` and the cutscene hook pool both name it).
  - Each block word is checked first: 63 and 106 against the vanilla block, 115/117/119 against `gohan_portraits`' frames.
  - `gohan_portraits` is unchanged. It still reads `art\portrait-sources\*_dialog.png`.
- **Dead data:** the old frames 115, 117, 119 (`rom:0x88E5B4`, `0x8905C4`, `0x8925D4`) and the status twins 116, 118, 120 (12 KB each set). The only +3 reader, `@0x08003A8C`, is in the vanilla page that the `status_bonus` entry stub bypasses. The page copy now reads +2. Old 63 and 106 frames are named only by the vanilla block and the stale `gohan_portraits` block. Neither block is referenced.
- **Blast radius:** all three portrait() users (dialog box, `sub_08018C72`, `sub_08019320` scouter) read the live block, so they show the new art too (CONFIRMED from the callers of `@0x0800BDCC`).

---

## 5. Tests

| File | Tests | What |
|---|---|---|
| `tests\test_rage_stats.py` (new) | 10 | Old word `8d22ffff` and new word; old apply kept and quoted; ROM diff only at the word and new code; other vtable words unchanged; interpreter: base 70/58/71 gives 90/78/91, vanilla gives 100/100/100, same speed calls, all other player bytes equal; leader record used; status page "70+20", "58+20", "71+20" and the r19 calibration "70+30", "58+42", "71+29" (my screenshot); `read_form` equals SSJ2 (20, 20, 20, not flat); Rage object only in entry 4; fails closed on 4 sites |
| `tests\test_portrait_remaster.py` (new) | 7 | Each of the five read back from the ROM equals its PNG; index rule; diff only at five block words and new frames; old frames and twins kept; status page for entries 19, 8, 9, 5, 22, 4, 2 shows the PNG pixels in OBJ colors; r19 Rage showed twin 12; fails closed |
| `tests\test_status_portrait.py` (changed) | 12 | Base is now the r19 list |

Whole suite before the build: **345 tests OK** (`scripts\one-time\2026-10-19-r20-build\suite.txt`). r19 had 316. Mine add 17. The other 12 are `tests\test_re_tools.py` (the tools task's file; run alone it gives 12, all pass). No failure in another task's file.

---

## 6. Build and save (CONFIRMED)

- r19 rebuilt first to `scripts\one-time\2026-10-19-r20-build\r19_repro.gba` (own log): `edd3df2e`, equal. No `LOG_*` env var set.
- Command: `log2_build.py --out archive\builds\log2_poc_r20.gba gohan_gi ssj2_form gohan_portraits status_bonus ssj2_idle cutscene_portraits npc_gi rage_text portrait_remaster status_portrait rage_stats`. No `file_select_dim`.
- r20 SHA-1 **`9b52833447b38db0e2b3b2c7b374b5ce389cc5a7`**. CRC32 `3A164089`.
- `docs\build-log.md`: the auto line and a descriptive line.

---

## 7. States (CONFIRMED bytes, LIKELY in mGBA)

**Copies:** `log2_poc_r19.sav`, `.ss1`, `.ss2`, `.ss3` copied to `log2_poc_r20.*`. SHA-1 pairs equal: `159601a3`, `177e917c`, `d793ca4d`, `e04c34db`. No r20 file existed before. The r19 files are untouched.

**Header (`scripts\one-time\2026-10-19-r20-build\states.py`, `states.txt`):** each state holds version `0x01000007`, title `DBZLGCYGOKU2`, code `ALFE`. These equal the r20 header, and r20's first 0xC0 bytes equal r19's. The stored CRC32 is r18's `8656B1E5`. As in r19, mGBA 0.10.5 loads such a state and logs a "different version" warning only.

**What each state holds:**
- ss1: no player object. ss2: another leader in Super Saiyan. ss3: Gohan leader in entry 2 (gi base), live 70/58/71, in the Cell scene before the Rage message.
- None of the three is in Rage.
- The only RAM word that names changed ROM is the form object `0x030021E4` = `0x08024E4C` (the Rage vtable). That is the mechanism: the next apply reads the new +0 word.

**A state saved during Rage** keeps STR, POW, END = 100 in player +0x160..+0x162 until the form apply runs again. Apply runs only from:
- `form_reapply` `@0x080086A2`: EXP gain with a level-up (`@0x08003D58`), set_leader, ext 73 (for example the post-Cell seq 20 (0, 157) that ends Rage), a STR/POW/END item, Switch Characters, transform;
- player_ctor `@0x0800873A`: a new player object at map load.
- Opening or closing the menu does not run it (message 8 calls leave, message 9 calls enter).
- So in the Cell fight a mid-Rage state shows "+30/+42/+29" until the first of these events. From ss3 or slot 3, the Cell script's ext 73 (0, 160) runs the new apply, so Rage shows +20 at once.

---

## 8. Diff proof r19 to r20 (CONFIRMED, `scripts\one-time\2026-10-19-r20-build\rom_proof.py`, `rom_proof.txt`, PASS)

- The in-memory r19 list equals the r19 file. The in-memory r20 list equals the r20 file. Same size. Header unchanged.
- 20845 bytes differ in 7 regions (gaps of up to 8 equal bytes joined). None is outside the patch sites.

| Region | Bytes differ | What |
|---|---|---|
| `rom:0x024E4C`-`0x024E4F` | 4 | Rage vtable +0 word (`rage_stats`) |
| `rom:0x8948D4` | 1 | status page copy +0x2F0, `ldrb r0,[r0,#0x3]` to `#0x2` |
| `rom:0x89491C`-`0x89491F` | 3 | status page copy +0x338, `bl paint` |
| `rom:0x894FAC`-`0x894FAE` | 3 | live block word id 63 |
| `rom:0x895058`-`0x89505A` | 3 | live block word id 106 |
| `rom:0x89507C`-`0x89508D` | 7 | live block words ids 115, 117, 119 |
| `rom:0x895468`-`0x89A5C3` | 20824 | five new frames, `status_portrait` POOL `0x89A490` and paint `0x89A4D0`, `rage_stats` apply `0x89A55C` (former `FF` space) |

---

## 9. My test plan

1. **Cell fight from save slot 3** (`log2_poc_r20.sav`): play to the Rage message. Gohan stays in the gi. Open Start, then status: STR, POW, END read `base+20` (level 40: "70+20", "58+20", "71+20") with a short gold segment. The portrait is the gi Super Saiyan 2 mid art, the same as the dialog box.
2. **Same from `log2_poc_r20.ss3`**. mGBA may log a ROM CRC warning.
3. **Other characters:** on the status page, flip through the party. Each portrait must equal that character's dialog art (Goku and Vegeta in the new mid art). Gohan base gi shows the mid base art; Super Saiyan shows mid SSJ.
4. **Dialog:** a Goku or Vegeta line and a post-chamber Gohan line show the mid art.
5. **Menu colors:** open an item sub-menu from the status page. Look for a wrong color in the chrome, the item icons and the tabs.
6. **Rage itself:** speed, aura, sound and HP regen as before.

---

## 10. Concerns

1. **Not tested in game.** The proof is code runs and bytes.
2. **Mid-Rage states** keep the old values until the next apply (section 7). None of my states is in that case.
3. **Art timestamps (first concern for the coordinator).** The coordinator said SSJ2 was written at 10:02 AM. All five sources read 10:04:22 AM when I copied them. A re-hash after the build shows each source still equals its `final_r20` copy (CONFIRMED): goku `c008893a`, vegeta `284cdb8a`, ssj `72dfffa0`, ssj2 `c96a9e27`, base `7088a3d2`. SSJ2 went from 1945 bytes (9:05 AM listing) to 1946, so it changed after 9:05 (LIKELY the chest shading; please confirm `c96a9e27` is the shaded file). The other four keep their 9:05 sizes (1555, 1823, 1911, 1577), so they are LIKELY rewritten unchanged; I had no 9:05 hashes to prove it. Not blocking the build; it blocks my test only if `c96a9e27` is not the approved SSJ2.
4. **States carry r18's CRC32**, as in r19.
5. **Dead data:** 24 KB (old Gohan dialog frames and status twins). Harmless. A later cleanup can drop the twins from `gohan_portraits` (its tests read them).
6. **Process slip:** one early read-only Bash call started with `cd "$L"`. The brief says never `cd`. All later calls used absolute paths.

**RE bible rows:** `scripts\one-time\2026-10-19-r20-build\bible_rows.md` (7 rows). I did not edit `docs\RE-BIBLE.md`.

---

## 11. Files

- **New:** `scripts\permanent\patches\rage_stats.py`, `patches\portrait_remaster.py`, `tests\test_rage_stats.py`, `tests\test_portrait_remaster.py`; `art\portrait-sources\remaster\final_r20\` (5 PNGs); `archive\builds\log2_poc_r20.gba`, `.sav`, `.ss1`-`.ss3`.
- **Changed:** `tests\test_status_portrait.py` (r19 base), `patches\status_portrait.py` (docstring usage line), `docs\build-log.md`.
- **Scripts and outputs (mine) in `scripts\one-time\2026-10-19-r20-build\`:** `rom_proof.py`, `rom_proof.txt`, `states.py`, `states.txt`, `append_buildlog.py`, `suite.txt`, `r19_repro.gba`, `repro-log.md`, `bible_rows.md`.
- Not touched: `data\`, `docs\RE-BIBLE.md`, the tools task's folders, any r19 file.
