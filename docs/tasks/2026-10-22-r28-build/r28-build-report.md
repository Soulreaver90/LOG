# r28 build report: "Full Power" Super Saiyan for Goku and Gohan

Brief: `docs\tasks\2026-10-22-r28-build\fullpower-ssj.md`. Base: r27 `5c4befd8feb8a8840730882c330f3c1ed5d1e51c`. Built 2026-10-22 6:41 PM (build-log time). Labels: CONFIRMED (C), LIKELY (L), SPECULATIVE (S).

| SHIPPED | Where |
|---|---|
| Goku and Gohan stay Super Saiyan from the chamber until Cell is beaten | `log2_poc_r28.gba`, patch `fullpower_ssj` |
| No form drain, no revert at 0 EP, B and Z blocked, knockout keeps the form, Rage still gives SSJ2 | same |
| Goku's arena power-up removed | same |
| Both are base after Cell is beaten, and Super Saiyan works as normal | same |
| Other characters behave as in r27 | same, tests |
| Test save right before they leave the chamber | `log2_poc_r28_chamber.sav`, slot 3 |
| r27 `.sav` and five states copied to r28 names | `builds\` |
| Suite passes | 444 tests, 0 failures |

| PENDING | Why |
|---|---|
| In-game check by me | Test plan at the end |
| Party regeneration while Goku or Gohan leads in the stretch | Open point 1, final decisions |
| NPC Goku walk-in before the chamber door is base | Open point 2, my option |
| NPC Gohan in the chamber exit scene keeps his armor look | Open point 2a, my option |

---

## 1. Stretch flags and proof

The stretch is `flag:149` set and `flag:195` clear. Both flags are story flags in the save struct (struct `0x03000E90` + 0xB4 + n/8, bit n&7).

| Flag | Byte, bit | Set by | Meaning | Label |
|---|---|---|---|---|
| 149 | `0x03000F56` bit 5 | V/T exit seq 33, `@0x083DE69E` (table `rom:0x3DE6F4`) | Goku walks into the chamber | C (script decode, flag sweep) |
| 195 | `0x03000F5C` bit 3 | post-Cell scene, `@0x083EC6A4` | Cell is beaten | C |

Proof:
- `scripts\one-time\2026-10-22-r28-build\flag_sites.txt` lists every SET and CLR site of flags 140-196. Flag 149 has one setter. Flag 195 has one setter. C.
- Flag 154 is not usable as the exit marker: the Master Roshi talk on 6,3 (`@0x083CE0FD`) also sets it. C.
- `stretch149.py` (the r27 stretch sweep with the window opened at 149) found two script areas beyond r27 that run in the stretch: the chamber exit (table `rom:0x3DBDD4`) and Dende's ball talk (table `rom:0x3DD380`). Both are patched. C for the shapes it searches. A script that reads the set from a run-time value would not appear. L.
- The map NPC sweep (`map_npcs.py`) found only the zone 14 objects (patched in r27) in the stretch. The 9,3 objects show before 149. The 9,4 NPC Goku and Gohan show only while temporary `flag:147` is set, inside one scene. C.
- The NPC Goku walk-in in V/T exit seq 33 runs before `SET 149`. It stays base (open point 2).

## 2. Gohan's start point

Gohan's stretch starts when he leaves the chamber, in the purple gi. C.

- His chamber outfit is appearance entry 0 (`set:53`, Demon Clothes). Entry 0 has +4 = +5 = 0, so it has no transform.
- The Demon Clothes sets are 53-59 in the bible. None is a Super Saiyan set.
- Chamber exit seq 3 (`rom:0x3DB59C`) now writes his record with ext 73 (0, 158), Super Saiyan gi (r27: 157, base gi). This runs before ext 82 (0), the Super Saiyan unlock.
- NPC Gohan in the exit scene keeps `set:56` and portrait 121, as in r27 (my rule: the look before player control stays).

## 3. Patch changes with addresses

The patch is `scripts\permanent\patches\fullpower_ssj.py`, appended as the last line of `build_list.txt`. No earlier allocation moved (test `test_earlier_allocations_unchanged`). `cellgames_ssj.py` is not edited.

### 3a. Code (Thumb, `rom:0x89A8B0`, 0x110 bytes)

| Routine | rom | Hooked at | Old value | What it does |
|---|---|---|---|---|
| `stretch_on` | `0x89A8B0` | (called) | | r2 = 1 when 149 is set and 195 clear |
| tick | `0x89A8C6` | SSJ vtable `0x08024C58` +4, `rom:0x24C5C` | r27 scene tick `0x0889A789` | In the stretch with leader Gohan (0) or Goku (4): return at once. Else: the r27 tick |
| test | `0x89A8E6` | ability 12 +8, `rom:0x1D99C8` | `0x080134F3` | In the stretch, record entry 5 or 20: return 0. Else: the vanilla test |
| revert | `0x89A906` | `appearance_revert` `rom:0x3ED4`, 8 bytes `ldr r3,=0x0889A907 ; bx r3` | `30 b4 9d 4c 00 21 02 78` | Vanilla loop. In the stretch it skips entries 5 and 20. From the file-select load (lr `0x0800185D`) in the stretch: Goku 19 to 20, Gohan 2 to 5 (only with record +0x14 bit 5) |
| death | `0x89A976` | knockout state vtable `0x080254D8` +0, `rom:0x254D8` | `0x0800833F` | Runs the vanilla enter. Then in the stretch it puts a Goku or Gohan leader back to entry 20 or 5 |

Why the test hook gives both "B disabled" and "Z grayed": B (`@0x08007EDA`) calls the test. A 0 result plays the refusal sound and skips the action. The HUD hook calls the same test and shows the +4 (dim) icon on 0. C (tests run both routines).

### 3b. Script bytes in place

| rom | Old | New | Where |
|---|---|---|---|
| `0x3DB5C3`, `0x3DB5CC` | 78 | 7A | chamber exit seq 3: NPC Goku spawn and face, set 60 to 61 |
| `0x3DBBED` | 3C | 3D | chamber exit seq 27: NPC Goku set 60 to 61 |
| `0x3DD238`, `0x3DD241` | 78 | 7A | Dende talk seq 4: NPC Goku 60 to 61 |
| `0x3DD320` | 78 | 7A | Dende talk seq 7: NPC Goku 60 to 61 |
| `0x3DD328` | 3C | 3D | Dende talk seq 7: remove Goku, 60 to 61 |
| `0x3DB6AF`, `0x3DB723`, `0x3DB783`, `0x3DD27F` | 3F | 41 | Goku lines, raw portrait 63 to 65 |
| `0x3DB62A` | 9D | 9E | chamber exit seq 3: Gohan ext 73 (0, 157) to (0, 158) |

### 3c. Relocated records (one table word each)

| Record | Source | New | Table word | Change |
|---|---|---|---|---|
| V/T exit seq 33 | `rom:0x3DE620` (0xB2) | `rom:0x89A9C0` (0xB8) | `rom:0x3DE774` | ext 73 (4, 61) right after `SET 149`: Goku's record goes Super Saiyan at the door |
| Arena entry seq 1 | r27 copy `rom:0x89A5C4` | `rom:0x89AA78` (0xD4) | `rom:0x3E8D98` | r27 Goku power-up removed (28 bytes) |
| Post-Cell seq 20 | npc_gi copy `rom:0x89516C` (0x261) | `rom:0x89AB4C` (0x267) | `rom:0x3EC7A4` | ext 73 (4, 60) right after Gohan's ext 73 (0, 157): Goku's record goes base |

Each source is checked by SHA-1 before the copy. Every old byte, slot and word is checked before any write. A second run raises. C (fail-closed tests).

## 4. What was removed from r27, and what was kept

| r27 item | Decision | Why | Label |
|---|---|---|---|
| Goku's arena power-up (`push 55 ; ext 46 ; push 0,9 ; ext 57 ; push 10 ; ext 42 ; push 55 ; ext 47 ; push 4 ; push 61 ; ext 73 ; push 10 ; ext 43`, 28 bytes) | Removed | Goku arrives in Super Saiyan, and `set:61` has no anim 9 (transform) | C |
| Gohan Super Saiyan inserts (ext 73 (0, 158) in "Me? Fight Cell?" seq 21 and Cell fight seq 1) | Kept | An r27 state saved with Gohan in base reaches these scenes without a save load, so removal would change what the player sees | L |
| Gohan EP refill ext 110 (0, 5000) in Cell fight seq 1 | Kept | EP still pays for attacks and shows on the HUD | C |
| `scene_drain_pause` | Kept | It still serves Vegeta and Trunks, and the stretch tick calls it for everyone else | C |

## 5. Knockout and continue

- Knockout in the stretch: the vanilla enter runs as before (form leave, death anim 10). Then the hook restores entry 20 or 5. C (test).
- Game over and continue: "You have died!" goes to the title. A slot load runs `appearance_revert` from `@0x08001858`, and the hook gives Goku 20 and Gohan 5. So after a knockout and continue, both are Super Saiyan while the stretch is on. C (code and tests). L (in game).
- Sparring room (map 6,70, no game over): the entry stays Super Saiyan. The form leave already stopped aura sound 55, so the sound may stay off until the next form enter (map change). L, cosmetic.

## 6. Tests

New file `scripts\permanent\tests\test_fullpower_ssj.py`, 38 tests. The new code runs in the suite's Thumb interpreter on the in-memory build.

| Brief item | Tests |
|---|---|
| Stretch start and end flags | flag window on the tick (4 flag combinations); door record `SET 149` then ext 73 (4, 61); SET 195 site unchanged; post-Cell ext 73 (4, 60) after (0, 157) |
| No drain and no revert at 0 | Goku 20 and Gohan 5 at EP 50, 1 and 0: EP, accumulator and messages unchanged; 200 ticks cost nothing; outside the stretch equal to r27, with message 0x24 at 0 |
| B and Z blocked, working after | test returns 0 in the stretch; HUD gives the dim Z (`0x086DB07C`) in the stretch and r27's icon after; B gives the refusal sound in the stretch and the action before and after |
| Other characters unchanged | Vegeta 11, Trunks 16 and 17 tick, test, HUD, B, revert and knockout equal r27 in every flag state |
| Rage still gives SSJ2 | ext 73 (0, 160) from entry 5 gives entry 4; the Rage scene bytes and the Rage test equal r27 |
| Knockout | Goku and Gohan keep 20 and 5 in the stretch, go to 19 and 2 after; others equal r27 |
| Save file | checksums of all slots; flags 149, 151, 154-156 set and 157, 158, 162-164, 185-188, 191, 192, 195 clear; leader, map and position; only named bytes differ from r27 |
| Diff | only the named sites change; dropping any site is caught; art, block and palettes equal |
| Fail closed | a changed byte at any site, slot, word or record source raises before any write; second run and missing notes raise |

Changed tests:
- `test_cellgames_ssj.py`: its "rom" build now stops at `scene_drain_pause` (r27 bytes), and the list test checks the order `rage_stats`, `cellgames_ssj`, `scene_drain_pause`, `fullpower_ssj`.
- `test_art_inject.py`: `LIST` gets `fullpower_ssj`.

Suite: `py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent` ran 444 tests, OK, 0 skipped (`scripts\one-time\2026-10-22-r28-build\suite_after.txt`). r27 ran 406.

Lint (`scripts\one-time\2026-10-20-inject-tool\lint.py` and a byte check): no BOM, CR, control characters, dashes, non-ASCII or lines over 120 in the new and changed files.

## 7. r28 SHA-1

`builds\log2_poc_r28.gba`: `eef01cf6aa37f660bbe0f07b87694d058252499c`. It equals the in-memory build of `build_list.txt`. The build added one line to `docs\build-log.md`.

## 8. Test save

No save or state at the chamber point existed. The search read every 8 KB `.sav` and every loadable state under the LOG folder for `flag:149` set and `flag:158` clear. It found only the new file.

`builds\log2_poc_r28_chamber.sav` was made from `log2_poc_r27.sav` with `log2_save.py set` (exclusive create). **Slot 3** holds the chamber point. Slots 1 and 2 equal r27.

Every changed byte (RAM order; the file stores each 8-byte block reversed):

| RAM | File | Slot 3 field | r27 | r28 chamber |
|---|---|---|---|---|
| `0x02E0` | `0x02E7` | +0x000 leader | 04 (Goku) | 02 (Vegeta) |
| `0x02E2` | `0x02E5` | +0x002 zone | 09 | 06 |
| `0x02E3` | `0x02E4` | +0x003 area | 01 | 0F |
| `0x03A7` | `0x03A0` | +0x0C7 flags 152-159 | 7F | 1F (157, 158 clear) |
| `0x03A8` | `0x03AF` | +0x0C8 flags 160-167 | 1C | 00 (162, 163, 164 clear) |
| `0x03AB` | `0x03AC` | +0x0CB flags 184-191 | FE | 60 (185-188, 191 clear) |
| `0x0440`-`0x0443` | `0x0447`-`0x0444` | +0x160 position | (768, 832) | (104, 76) |
| `0x0444`, `0x0446`, `0x0447` | `0x0443`, `0x0441`, `0x0440` | +0x164 checksum | | `0x8A485316`, valid |

The var byte (+0x004) was already 1. Set flags in slot 3: 0-9, 11-20, 22-23, 26, 28-31, 33-70, 73-100, 108-113, 117-132, 134, 136-146, 148-156, 171, 176, 181, 189-190.

Why this point:
- Map 6,15 position (104, 76) is the arrival point from the 6,16 stairs, inside the stairs warp rectangle (96,56)-(113,89). C (map data).
- On 6,16 the player arrives at (200, 236), inside the TV region (169,193)-(232,248). Its condition is `flag:151` set and `flag:157` clear. The TV scene sets 157. With 156 set, the chamber exit follows. C (decode), L (trigger order in game).

Save artifacts (the brief allows only flags, map and leader):
- Goku and Gohan are in the party (records from r27 slot 3). In the story they are still in the chamber. Do not switch to them before the exit scene.
- The records hold Goku 19 and Gohan 2 with the Super Saiyan bit. The r28 load turns them into 20 and 5 (the stretch is on).
- The items include the Dragon Radar (45) and the Scouter (22), from r27 slot 3.
- Flags 189 and 190 stay set. Their story point is not known.

## 9. Files copied

Exclusive create, byte-equal to the source. No ROM, `.sav` or state was overwritten.

| Source | Copy | SHA-1 |
|---|---|---|
| `log2_poc_r27.sav` | `log2_poc_r28.sav` | `159601a376596afbd9d4124845a3b1355b46a839` |
| `log2_poc_r27.ss1` | `log2_poc_r28.ss1` | `177e917c7fe67ac7c1ff9e011154cfb2f8945548` |
| `log2_poc_r27.ss2` | `log2_poc_r28.ss2` | `4487d1d348f206bf098d1d62a32c1767880e691a` |
| `log2_poc_r27.ss3` | `log2_poc_r28.ss3` | `e04c34dbbbf39c0196b0a3425022f6c55481dd32` |
| `log2_poc_r27.ss4` | `log2_poc_r28.ss4` | `570ba9bb945748fe0599761a4a26d9bb8113bb8e` |
| `log2_poc_r27.ss5` | `log2_poc_r28.ss5` | `8062e3d9b6248d2a6075898dfeb21ea688b8c3b7` |

## 10. Diff proof

Script `scripts\one-time\2026-10-22-r28-build\diff_proof.py`, output `diff_proof.txt`. C.

- 1311 bytes differ from r27 in 28 runs. Every byte is in a named site: 3 code slots (tick, knockout enter, test word), the revert jump, 12 script bytes, 3 table words, and the new code and record copies (`rom:0x89A8B0`-`0x89ADB2`). Bytes outside the named sites: 0. Named sites with no change: none.
- Portrait slots `rom:0xF00000`-`0xFFFFFF`, the live block `rom:0x894EAC`, palette copies `rom:0x1DA6C8` and `rom:0x3ECBA4`: equal. Palette color 172 is `3F 63` in both.
- Do the r27 states work on r28? They load (byte copies). In all five states one RAM word names a changed byte: IWRAM `0x03001F58` = `0x080254D8`, the knockout state object's vtable. The vtable address does not move. Its slot +0 is read at each knockout, so old states get the new knockout enter. No RAM word names a changed script record or `appearance_revert`. C (scan), L (in game).
- A state keeps its RAM records. An r27 state with Goku or Gohan in base keeps them base until B (the vanilla test allows it for a base entry) or a save load. After they transform, the stretch rules hold. L.

## 11. Open points

1. **Regeneration (final decisions).** Super Saiyan has no base tick. The base tick `@0x08017028` gives the leader 3 % EP and the others 5 % HP and EP about every 596 frames. While Goku or Gohan leads in the stretch, that never runs. Option: call the base regeneration from the stretch tick. C (code), L (rate).
   - The same base tick also counts down the transform cooldown, struct +0x08 (`0x03000E98`). Its only reader is the ability 12 test (`@0x08013522`-`@0x08013528`). The other `+0x8` reads through the same pointer tables (`0x086DB27C` +8, for example `@0x08013160`) read the map word `0x03002080`, not the cooldown. No `0x03000E98` literal exists in the code. So attacks do not lock in the stretch. C for these two shapes; a reader that gets the struct from another pointer would not appear.
2. **NPC Goku before the door (my option).** In V/T exit seq 33, NPC Goku walks in before `SET 149`, so he is base there. Option: set 61 for that walk-in.
2a. **NPC Gohan in the chamber exit scene (my option).** He keeps armor `set:56` and portrait 121 while NPC Goku next to him is gold. Decision 2 says "SSJ whenever they show as NPCs". No armor Super Saiyan set exists, so the only way is gi Super Saiyan `set:158` and the gi Super Saiyan portrait in that scene. I kept the earlier my rule (the look before player control stays). My call. It does not block.
3. **"Z cannot be selected".** I read it as "Z is dim and B cannot use it". L still cycles to the Z slot, because cycling reads the slot bits, not the test. A cycle skip would also hide the dim Z. L.
4. **File select.** A save made in the stretch stores entries 5 and 20, so the file select shows Goku and Gohan in Super Saiyan. L, cosmetic.
5. **Aura sound after a sparring-room loss** (section 5). L, cosmetic.
6. **Dead data.** `rom:0x89A5C4` (r27 arena entry copy), `rom:0x89516C` (npc_gi post-Cell copy) and `rom:0x3DE620` (vanilla V/T seq 33) are now unreferenced. Bible tool trap: the table words `rom:0x3DE774`, `rom:0x3E8D98`, `rom:0x3EC7A4` point into the expansion area.
7. **Process deviations.** One Bash call started with `cd /c` (a read-only `wc`). One `log2_build.py --help` call treated `--help` as a patch name and raised before any write; `docs\build-log.md` and `builds\` were unchanged by it.

## 12. My test plan

Use `builds\log2_poc_r28.gba`. Watch: Goku and Gohan gold, Z dim, B makes the refusal sound, EP does not drop over time, attacks still cost EP.

| Step | Start | Do | Expect |
|---|---|---|---|
| 1 | `log2_poc_r28_chamber.sav` (load it as the alternate save, or copy it to a new folder as `log2_poc_r28.sav`), **slot 3** | Vegeta leads on 6,15. Step off the stairs and back on. On 6,16 walk into the TV area | TV announcement, then the chamber exit. NPC Goku gold, Goku lines with the gold portrait 65. Gohan keeps his chamber look in the scene, then "Gohan now has Super Saiyan form!" |
| 2 | after step 1 | Dende's ball talk on the Lookout | NPC Goku gold, portrait 65 |
| 3 | after step 2 | At a save point, Switch Characters to Gohan, then to Goku | Each leads gold. Z dim, B refused, no EP drain. Switch to Vegeta: base, and his Super Saiyan drains as in r27 |
| 4 | `log2_poc_r28.sav` (r27 copy) **slot 3** | Load. Goku leads at the Lookout. Fly to the Cell Games | Goku gold at once (r27: base). On 14,1 and in the arena entry scene Goku is gold with no power-up animation |
| 5 | after step 4 | Play to Cell, let Gohan rage | Rage gives SSJ2 with its text, as in r27 |
| 6 | after Cell | Post-Cell scenes, then any time Goku leads later | Both base. B transforms, Super Saiyan drains and reverts at 0 as normal |
| 7 (optional) | in the stretch | Get knocked out, then continue from the title | Goku or Gohan loads gold |

The plan does not reach the stretch start (the door scene with `SET 149` and Goku's record write). A search of every 8 KB `.sav` and every loadable state under the LOG folder for `flag:148` set and `flag:149` clear found nothing. So the start is covered by tests only (door record decode and the flag window tests).

Quick checks: `log2_poc_r28.ss2` ("Me? Fight Cell?", Goku gold): B refused and no drain, also outside text boxes. `log2_poc_r28.ss3` (Cell fight, Gohan base): B transforms Gohan, then he stays gold.

---

## 13. My tests of the chamber save (follow-up)

I loaded `log2_poc_r28_chamber.sav` slot 3, and the game "starts where I have to collect the dragonballs". This section gives the cause and a corrected save.

### 13a. What decides the story point and the spawn

| Field | Where | What the first save holds | Label |
|---|---|---|---|
| Spawn map and position | struct +0x02 zone, +0x03 area, +0x04 var, +0x160 x, +0x162 y. The slot load `@0x0800180C` passes them to `map_load` `@0x0800C584` (`@0x08001876`-`@0x0800188C`) | 6,15 var 1 at (104, 76): Capsule Corp, at the arrival point of the 6,16 stairs | C |
| Story point | story flags only (struct +0xB4). No chapter or quest byte exists. The Journal runs the quest table `rom:0x6D68DC` on the flags and items | 149-156 set; 157, 158, the Dragon Ball flags and 191 clear | C |
| Journal (quest table run on the slot) | "Collect the seven Dragon Balls": active = `flag:158`, done = all of 162-164 and 185-188. "Meet up ... Cell's announcement": active = 154, done = 157 | Active: "Meet up with the others in the Briefs' residence to hear Cell's announcement". "Collect the seven Dragon Balls" is hidden | C |
| Leader | struct +0x00 | Vegeta | C |
| Party | record +0x14 bit 0 (in party, ext 79/91), bit 1 (available, ext 80/81), bit 5 (Super Saiyan, ext 82) | Gohan and Goku 0x7F (from r27 slot 3) | C |

So the first save loads before the Cell announcement, with the Dragon Ball quest not started. The stored fields are right for "right before they leave the chamber". C.

### 13b. Why I settled on the Dragon Ball quest

LoG II has no playable moment between "Goku and Gohan are in the chamber" and the Dragon Ball quest. C (script decode).

1. On 6,15 the stairs (rect (96,56)-(113,89)) lead to 6,16. The player arrives at (200, 236), inside the TV region (rect (169,193)-(232,248), cond `flag:151` set and `flag:157` clear). The TV scene starts at once.
2. TV seq 7 `rom:0x3D150A`: `SET 157`, then "if `flag:156`" jumps to seq 9 (`rom:0x3D152C`, type 5). That jump runs the chamber exit table `rom:0x3DBDD4` in the same scene.
3. The exit table is one scene of 34 records with no player control: the "Meanwhile... Goku and Gohan had emerged" narration, the Lookout 9,1 scene (NPC Goku gold, Gohan gets Super Saiyan), Dende's dragon, "Goku is now an available character! You are now playing as Goku." (ext 79/80/82 (4), ext 70 (4)), `SET 158`, and "Journal Updated!".
4. Control comes back at the Lookout with Goku leading and "Collect the seven Dragon Balls" active.

My result is this chain. From the save it starts after one step onto the stairs. If the text is skipped, it looks like the game "starts" at the Dragon Ball quest. LIKELY: I cannot see what I saw first.

A second fault is in the party. In the first save Goku is already in the party, and Gohan already has Super Saiyan. In the real story Goku joins only at the exit (`@0x083DBC38`), and Gohan gets Super Saiyan only there (`@0x083DB64B`). C. This does not move the story point. But it lets the player switch to them before the exit, and the load then gives Gohan Super Saiyan at once.

### 13c. Corrected save: `builds\log2_poc_r28_chamber2.sav`

This is a new file, written by `scripts\one-time\2026-10-22-r28-build\make_chamber2.py` (exclusive create). Its source is `log2_poc_r27.sav`. **Slot 3** holds the point. Slots 1 and 2 equal r27.

- Spawn: map 6,16 at (200, 236), the stairs arrival point. It is inside the TV region, so the TV and the exit scene are the first thing after the load. LIKELY: the save load and the warp both use `map_load`, so the region fires on load as it does on arrival. If it does not, step off the spot and back on.
- Party as before the exit scene: Goku not joined, and Gohan not available and without Super Saiyan.

Every byte that differs from `log2_poc_r27.sav` (RAM order; the file stores each 8-byte block reversed):

| RAM | File | Slot 3 field | r27 | chamber2 | Meaning | Label |
|---|---|---|---|---|---|---|
| `0x02E0` | `0x02E7` | +0x000 leader | 04 | 02 | Vegeta leads (Goku and Gohan are in the chamber) | C |
| `0x02E2` | `0x02E5` | +0x002 zone | 09 | 06 | Capsule Corp zone | C |
| `0x02E3` | `0x02E4` | +0x003 area | 01 | 10 | Area 16, the TV room. Var stays 1 (6,16 has one variation) | C |
| `0x0300` | `0x0307` | +0x020 Gohan record +0x14 | 7F | 5D | Bit 1 clear (ext 81 (0) at the chamber door `@0x083DE6A4`), bit 5 clear (ext 82 (0) only at the exit) | C (sites), L (full bit state) |
| `0x0370` | `0x0377` | +0x090 Goku record +0x14 | 7F | 40 | Bits 0-5 clear: Goku never joined. The exit sets bits 0, 1, 5 and 2-4 (ext 79, 80, 82, 83 (4, 0-2)). Bit 6 kept | C (sites), L (bit 6) |
| `0x03A7` | `0x03A0` | +0x0C7 flags 152-159 | 7F | 1F | 157 (Cell's TV announcement) and 158 (Dragon Ball quest start) clear | C |
| `0x03A8` | `0x03AF` | +0x0C8 flags 160-167 | 1C | 00 | Dragon Balls 162, 163, 164 clear | C |
| `0x03AB` | `0x03AC` | +0x0CB flags 184-191 | FE | 60 | Dragon Balls 185-188 and 191 (balls returned) clear | C |
| `0x0440`-`0x0441` | `0x0447`-`0x0446` | +0x160 x | 0x0300 | 0x00C8 | x = 200 | C |
| `0x0442`-`0x0443` | `0x0445`-`0x0444` | +0x162 y | 0x0340 | 0x00EC | y = 236 | C |
| `0x0444`, `0x0446`, `0x0447` | `0x0443`, `0x0441`, `0x0440` | +0x164 checksum | | | `0x2F3553B6`, valid | C |

Kept from r27 slot 3 (LIKELY harmless):
- Goku's record entry stays 19. The r28 load hook makes it 20, which is what the chamber door does in r28.
- Gohan's entry stays 2 (gi). The exit writes 5 before he can be used.
- Levels, items (Dragon Radar 45, Scouter 22) and flags 189 and 190 stay.

Tests: `Chamber2SaveTests` checks the checksum, map, position, leader, the two record bytes, the flags, and that no other byte differs. Suite: 445 tests, OK.

My step: load `log2_poc_r28.gba` with `log2_poc_r28_chamber2.sav` slot 3. Read through the TV and the exit scene without skipping. Expect NPC Goku gold, Goku's lines with portrait 65, then "Gohan now has Super Saiyan form!". After "Journal Updated!", Goku leads in gold at the Lookout. That is the start of the Dragon Ball quest, and it is the first moment Goku and Gohan can be played after the chamber.
