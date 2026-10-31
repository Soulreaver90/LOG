# r27 build: Super Saiyan Gohan and Goku through the Cell Games, no ki drain during scenes (2026-10-20)

Brief: `docs\tasks\2026-10-20-r27-build\cellgames-build.md`. Base: r26 `archive\builds\log2_poc_r26.gba`, SHA-1 `1a381ac7947cdaa2e9fdf0afaa44331a9b524dbf` (the file hashes to it, and the current build list rebuilds it byte for byte). Result: `builds\log2_poc_r27.gba`, SHA-1 **`5c4befd8feb8a8840730882c330f3c1ed5d1e51c`**, CRC32 `07E13B7E`. Whole suite: **406 tests, all OK**.

Labels: **CONFIRMED** = proved here by code quotes, bytes, a two-shape sweep, or a test run. **LIKELY** = strong evidence, not seen in game. **SPECULATIVE** = a guess.

---

## 1. SHIPPED and PENDING

**SHIPPED**

| My ask | State | Section |
|---|---|---|
| "NPC Gohan uses the gi Super Saiyan set 158 and the Super Saiyan gi portrait (115) through the stretch" | Done: 7 bytes in place, 3 in record copies, 4 portrait bytes | 3 |
| "Playable Gohan starts in Super Saiyan at both leader points. Rage still works. Base after Cell" | Done: ext 73 (0, 158) before both ext 70 (0); reverse copy byte; Rage and post-Cell untouched | 3, 5 |
| "Fill Gohan's ki (EP) to full at the start of his Cell fight" | Done: ext 110 (0, 5000) in the Cell fight seq 1 copy | 3 |
| "Playable Goku transforms on arrival ... power-up animation before ext 73 (4,61)" | Done: entry scene seq 1 | 3 |
| "Every NPC Goku in the stretch is Super Saiyan (set 61) with portrait 65, including the 14,1 NPC" | Done: 29 set bytes, 8 portrait bytes | 3 |
| "If the player can switch leader on the arena maps ... say what form Goku has then" | Answered: the player cannot switch on maps 14,1-14,4 | 4 |
| "No ki drain while any scene plays, everywhere in the game" | Done: own patch `scene_drain_pause` | 2 |
| Marker proof with two search shapes | Done: scene flag `@0x03001FDC` and scene depth `@0x03000E24` | 2 |
| Build r27, copy the states, diff proof, tests, my test plan | Done | 6-9 |

**PENDING (mine)**

| Item | Why |
|---|---|
| In-game check of r27 | All proof is bytes, code runs in the test interpreter and state reads. Section 9 has the plan |
| Goku can still drop to base in the two Cell fights | Drain runs in fights as you asked. At level 40 his EP lasts about 46 s of fight. B also reverts. Section 8, point 1 |

---

## 2. The scene marker and its proof (CONFIRMED)

The drain pause skips the tick when **both** of these words are nonzero:

| Word | What it is | Writers |
|---|---|---|
| `[0x03001FDC]` (`0x03001FD8` +4), the **scene flag** | 1 while a scene table runs | Scene setup `@0x0800B4AE` writes 1. Scene cleanup `@0x0800B4FC` writes 0. No other writer by shapes A and B (limits under "Not covered") |
| `[0x03000E24]` (`scene_manager` +8), the **scene depth** | Number of pushed scenes | `scene_push` `@0x0801F2F4` (+1, then -1) and the scene reset `@0x0801F346` (to 0). No other writer by shapes A and B |

**Code quotes:**

```
0800b4e0  ldr r1,=0x03001fd8      ; scene setup (9 callers)
0800b4ea  mov r0,#0x1
0800b4ec  str r0,[r1,#0x4]        ; scene flag = 1
...
0800b502  ldr r1,=0x03001fd8      ; scene cleanup (the same 9 callers)
0800b504  mov r0,#0x0
0800b506  str r0,[r1,#0x4]        ; scene flag = 0

0801f2fa  ldr r0,[r4,#0x8]        ; scene_push, r4 = 0x03000e1c
0801f2fe  add r1,r0,#1
0801f304  str r1,[r4,#0x8]        ; depth + 1, then frame_loop runs the pushed scene
0801f334  ldr r0,[r4,#0x8]
0801f336  sub r0,#0x1
0801f338  str r0,[r4,#0x8]        ; depth - 1 when the scene ends
```

**Shape A (writers):** `marker_proof.py` follows the base register in every function that loads `0x03001FD8` (9) or `0x03000E1C` (24). Only setup and cleanup touch +4. Only `scene_push` and `@0x0801F346` touch +8. No pool word holds `0x03001FDC` or `0x03000E24` itself.

**Shape B (scene starts):** the 9 functions that build a cutscene scene object (vtable `0x08023E88`) each call setup, then `scene_push`, then cleanup. These 9 are exactly the callers of setup and of cleanup. `scene_run` `@0x0800B520` has one caller, `@0x0800BDB4`, which is that vtable's slot +0x2C. So every scene table runs inside one pushed scene, with the flag at 1 from start to end.

**Shape C (states, `states_marker.txt`):**

| State | Scene | Depth | Flag |
|---|---|---|---|
| r27 ss2 ("Me? Fight Cell?" index 15, text box up) | cutscene `0x08023E88`, handler `0x08023FC8` (type 1 text) | 1 | 1 |
| r27 ss3 (Cell fight index 22, text box up) | cutscene, handler `0x08023FC8` | 1 | 1 |
| `log2_pad16.ss1`, captures 01 and 02 (free play) | field `0x08023884` | 0 | 0 |

**Text boxes:** the flag stays 1 through them (ss2, ss3). The world also runs during them: the cutscene vtable +0xC is `field_update` `@0x08004EA8`, which runs `world_update`, the player update and the form tick. So in r26 the drain ran during every dialog box. This closes the study's open point 1.

**Fights:** a fight that a scene starts runs with flag 0 and depth 0. Example: the entry scene `rom:0x3E8D98` seq 28 runs `push 30,1 ; ext 104` (the fight) and ends. `scene_run` returns 1 through the cutscene vtable +0x14 > +0x28 > +0x2C. Then the nested frame loop exits, `scene_push` pops, and cleanup clears the flag. Enemy event scenes in a fight (the Cell type 21-25 events) push their own scene, so the pause covers only their dialog. Code: CONFIRMED. No in-fight state exists to read: LIKELY in game.

**Why both words:** ext 97 (`@0x0800A3E8`, "You have died!" to the title) calls the scene reset and `scene_set` but never cleanup. The flag stays 1 after it, with depth 0. The depth term lets drain run after that until the next scene. Depth alone is too wide: menus, fades after a map load (`0x08023990`) and ext op waits also push scenes (63 `scene_push` sites in 40 functions, `push_callers.txt`). With the flag alone, the ext 97 case would stop drain until the next scene.

**Not covered:** a marker base passed through a register or memory (register tracking is per function); a scene started only by Thumb code that does not use setup.

---

## 3. Patch changes with addresses

Both patches are new files at the end of `scripts\permanent\build_list.txt`, so no earlier byte or allocation moves (CONFIRMED: the r26 allocation list is a prefix of the r27 list; `test_earlier_allocations_unchanged`).

### 3a. `scripts\permanent\patches\cellgames_ssj.py`

| # | Change | Sites | Bytes |
|---|---|---|---|
| 1 | Reverse lookup copy entry 5 +1 | `rom:0x800065` | `3B` to `9E` (59 to 158) |
| 2 | NPC Gohan 157 to 158 | map objects `rom:0x408CA0` (14,1), `0x408F8C` (14,3); entry seq 22 `0x3E8C2C`; seq 26 `0x3E8D1E`, `0x3E8D41`; "Me? Fight Cell?" seq 14 `0x3E921C`, `0x3E9226`; and 3 bytes in copies (row 6) | `9D` to `9E` |
| 3 | NPC Goku 60 to 61 | `rom:0x3E946B`, `0x3E9807`, `0x3E982C`, `0x3EA679`, `0x3EA698`, `0x3EA6D0`, `0x3EA793`, `0x3EA7ED`, `0x3EA7F3`, `0x3EA7FA`, `0x3EA801`, `0x3EA808`, `0x3EA80F`, `0x3EA816`, `0x3EA891`, `0x3EA89F`, `0x3EA8A5`, `0x3EA8AC`, `0x3EA8B3`, `0x3EA8BA`, `0x3EA8C1`, `0x3EA8C8`, `0x3EA8CD`, `0x3EA8D8`, `0x3EA8E2`, `0x3EA951`; and 1 byte in a copy | `78` to `7A` |
| 3b | NPC Goku remove (seq 23, the teleport) and the 14,1 object | `rom:0x3EA9CA`, `rom:0x408D54` | `3C` to `3D` |
| 4 | NPC Gohan portraits | `rom:0x3E8173`, `0x3E81A3`, `0x3E9233`, `0x3E934F` | `3B` to `3E` (59 to 62; the hook shows 115) |
| 5 | NPC Goku portraits | `rom:0x3E850B` (14,1 talk), `0x3E9707`, `0x3E977F`, `0x3E9835`, `0x3EA79F`, `0x3EA823`, `0x3EA8EF`, `0x3EA95F` | `3F` to `41` (63 to 65) |
| 6 | Records copied and repointed (old ones unchanged) | see the next table | |

| Record | Old | New (length) | Table word | Change |
|---|---|---|---|---|
| Entry seq 1 | the npc_gi copy `rom:0x895098` (read from `alloc.notes["npc_gi"]["records"][0x3E8610]`) | `rom:0x89A5C4` (0xF0) | `rom:0x3E8D98` | 2 Gohan bytes 157 to 158; Goku's 28-byte transform before `push 50 ; ext 46`: `push 55 ; ext 46` (aura sound), `push 0,9 ; ext 57` (power up, set 60 has anim 9), `push 10 ; ext 42` (flash), `push 55 ; ext 47`, `push 4 ; push 61 ; ext 73`, `push 10 ; ext 43` |
| "Me? Fight Cell?" seq 21 | `rom:0x3E9384` | `rom:0x89A6B4` (0x67) | `rom:0x3E9438` | remove 157 to 158; spawn Goku 60 to 61; `push 0 ; push 158 ; ext 73` before `push 0 ; ext 70` |
| Cell fight seq 1 | `rom:0x3E9E8C` | `rom:0x89A71C` (0x6B) | `rom:0x3EA400` | `push 0 ; push 158 ; ext 73 ; push 0,5000 ; ext 110` before `push 0 ; ext 70` |

**Design notes:**
- Goku's transform sits at the end of seq 1, after he stands on his mark (`push 0,448,680 ; ext 53`) and the others arrive, and before the arena sound (sound 50) starts. ext 57 actor 0 is the player: `find_actor_by_set` `@0x08009370` returns `[0x03001FA8]` for 0 (CONFIRMED).
- The first Goku line, seq 2 "I'll fight Cell first.", now shows 65 (he leads in entry 20).
- Gohan is not the leader at either ext 73 (0, 158), so it only writes his record. ext 70 then builds the player from entry 5 (CONFIRMED by the interpreter, section 5).
- I did not apply in-place bytes to the three old records. A state paused inside one keeps running the old bytes. No r27 state holds a pointer into them (section 7).
- The patch checks every old byte, each record's SHA-1 and each table word before any write. A second run raises.

### 3b. `scripts\permanent\patches\scene_drain_pause.py`

| Item | Address | Detail |
|---|---|---|
| SSJ tick | `rom:0x89A788` (0x94 bytes) | The `ssj2_form` tick re-encoding with step 0xCCD (vanilla SSJ), plus the scene check in front |
| SSJ2 tick | `rom:0x89A81C` (0x94 bytes) | Same with step 0x199A (as `ssj2_form`) |
| Vanilla SSJ vtable `0x08024C58` +4 | `rom:0x24C5C` | `AF 26 FF FF` (`0x08017307`) to `31 5B 87 00` (`0x0889A789`) |
| `ssj2_form` vtable +4 | `rom:0x88DE28` | to `0x0889A81D` |

**My call:** the pause is its own patch, not an edit of `ssj2_form`. A bigger `ssj2_form` code block would move every later allocation (npc_gi block, rage_text, status_portrait, rage_stats) and break old states. The new ticks keep the `ssj2_form` shape, so `read_form` still reads each drain (0xCCD for entries 5 and 20, 0x199A for entry 22). The vtables are ROM, so a loaded state uses the new ticks at once.

**Scope (CONFIRMED, all 23 entries of the r27 live table `rom:0x88DC54` read at +0x10):** the vanilla SSJ vtable is the class of the one form object `@0x030021EC` (form object init `@0x080232E4`). Five entries name that object: 5 (Gohan, set 158), 11 (Vegeta, set 140), 16 (Trunks, set 133), 17 (Trunks jacket, set 134) and 20 (Goku, set 61). Entry 22 (Gohan Super Saiyan 2, set 159) names the `ssj2_form` object. So these six forms pause in scenes. Rage (entry 4), Super (entries 10 and 14, `@0x030021E8`), Namek (entry 7) and base ticks are unchanged. The old SSJ tick `@0x08017306` and the `ssj2_form` tick stay in the ROM, unreferenced.

---

## 4. Switching leader on the arena maps (CONFIRMED)

- **The player cannot switch leader on maps 14,1-14,4.** Switch Characters opens only from the save point menu. `switch_characters` `@0x08011172` is party screen vtable `0x080247A8` +0x24. Only `@0x08010B08` builds that screen, and only `@0x080109EC` calls it (save menu choice 2, vtable `0x08023BCC`). `save_point_factory` `@0x08010AC6` builds the save menu. Its 30 map records are at `rom:0x3EDD18`-`0x40882C`. The zone 14 object lists start at `rom:0x408B9C` and hold no such record (`scripts\one-time\2026-10-20-cellgames-ssj\maps14.txt`).
- **If he could switch:** `switch_characters` calls `appearance_revert` at `@0x080111F6`, so a Goku switched out would revert 20 to 19 and come back in base. A fix would need code. It is not needed, because the switch is not reachable there.
- **Side effect:** a player who arrives on 14,1 with another leader sees NPC Goku in Super Saiyan (final decisions 3). That player must switch to Goku at a save point elsewhere and fly back. Playable Goku walks 14,1 in base and transforms in the 14,2 entry scene.

---

## 5. Tests

New file `scripts\permanent\tests\test_cellgames_ssj.py`: **31 tests**, all OK. Expected sites are restated from the study and the brief, never imported from the patches. Scripts are decoded by an own decoder. Code runs as `thumb_dis` text in the test_status interpreter.

| Study test | What runs |
|---|---|
| 1. In-place bytes | Old and new for all 48 bytes; each old byte, each record hash and each table word, changed one at a time, makes the patch raise with the ROM unchanged; a second run and missing notes raise |
| 2. Reverse lookup | `@0x080042BC` on r27: 158 gives 5, 157 gives 2, 160 gives 4, 61 gives 20, 60 gives 19, 59 reaches the assert |
| 3. ext 73 | `@0x0800A8EC` with stubs for the virtual calls, `get_set` and `form_reapply`: (0, 158) as leader gives entry 5, sprite = set 158 header, base leave then SSJ enter; (0, 158) as non-leader writes only the record; (4, 61) gives entry 20 and SSJ enter; (0, 160) from entry 5 gives entry 4, SSJ leave then Rage enter |
| 4. ext 70 | `appearance_revert` `@0x08003ED4`: Gohan leads, Goku 20 to 19, Gohan stays 5; Piccolo leads, Gohan 5 to 2 and 4 to 2 |
| 5. Relocated records | Each copy decodes as the old record plus the change; the table word points at the copy; the old record is unchanged and was named by one word only; no jump ops; state 9 comes after Goku's last place and before ext 73 (4, 61); the only ext 73 in seq 1 |
| 6. Scene groups | All 19 stretch tables: NPC sets are 61 x28 and 158 x8, none 157 or 60 (r26: 60 x28, 157 x8); ext 73 names 61 once and 158 twice; each scene spawns its NPC; post-Cell tables and records unchanged (157 x5) |
| 7. Portraits | `portrait()` `@0x0800BDCC`: raw 62 with entry 2 gives 115; Gohan leading in entry 5 gives 115; Goku leading in entry 20 gives 65; raw 65 gives 65; raw 64 stays 64. No stretch record uses 59 or 63; 62 and 65 are exactly the 12 records |
| 8. Anim rows | Set 158 has 0, 1, 4, 6, 9; set 61 has 0, 1 and lacks 9; set 60 has 9 |
| 9. No ext 73 names 59 | Shape A (table walk) and shape B (byte scan of the script region and the expansion area) |
| 10. Diff proof | Every r26 to r27 byte lies in a named site; every named site changes; dropping any one site is caught; slots, block and palettes equal |
| 11. Suite | 406 OK (below) |
| 12. Old states | `scripts\one-time\2026-10-20-r27-build\diff_proof.py` (section 7) |
| Drain pause | Both ticks: flag 1 and depth 1 or 2 keeps EP and the accumulator, with no revert even at EP 0; flag and depth (0,0), (1,0) and (0,1) give the same result as the old tick for 4 EP and accumulator cases; 20 frames cost 1 EP outside a scene and 200 frames cost 0 inside; vtable slots and every other slot; Rage, Super, Namek and base vtables unchanged; old tick code unchanged |
| Gohan refill | ext 110 (0, 5000) sits between ext 73 (0, 158) and ext 70 (0) in the Cell fight seq 1 copy |

**Existing tests (changed files):**
- `test_npc_gi.py` and the other tests that pin Cell Games bytes build their own prefix lists (`R14` + npc_gi, `R13`, and so on). They keep testing 157 and need no change.
- 8 tests in `test_art_inject.py` and `test_inject.py` already failed before r27: `scripts\one-time\2026-10-20-r27-build\suite_before.txt` shows 375 run, 8 failures. The cause is my r24-r26 table edits (palette 172 = (248, 200, 192), my art for 40 and 65 from `final_r24`). I changed the tests, not the art files:
  - The disk-versus-staged, add and replace tests build with the disk palette.
  - The palette writer and empty-palette tests compare against a build with an empty table.
  - I-art test checks each table note names the `final_r24` file and that the stored pixels equal that file (snapped, as inject stored it).
  - The round-trip test round-trips the real palette file in place of "the table is empty".
  - The palette command test uses (240, 216, 208), which differs from the stored 172 in all three channels.
- `test_art_inject.LIST` now ends with `cellgames_ssj`, `scene_drain_pause`.

**Suite:** `py -3 -P -m unittest discover -s scripts\permanent\tests -t scripts\permanent` ran **406 tests, OK** (`scripts\one-time\2026-10-20-r27-build\suite_after.txt`).

---

## 6. Build and files copied (CONFIRMED)

- Command (LOG root): `py -3 -I scripts\permanent\log2_build.py --list --out builds\log2_poc_r27.gba`. Output SHA-1 `5c4befd8feb8a8840730882c330f3c1ed5d1e51c`. One line added to `docs\build-log.md`.
- Copies (exclusive create, byte-equal to the source): `log2_poc_r26.sav` to `log2_poc_r27.sav`, `.ss1`, `.ss2`, `.ss3` to the r27 names. No ROM, `.sav` or state was overwritten.

---

## 7. Diff proof (CONFIRMED, `scripts\one-time\2026-10-20-r27-build\diff_proof.txt`)

- r26 to r27: **806 bytes in 58 runs**. 0 bytes outside the named sites. Every named site changed.
  - 48 single bytes (section 3a rows 1-5).
  - 3 table words (`rom:0x3E8D98`, `0x3E9438`, `0x3EA400`) and 2 tick slots (`rom:0x24C5C`, `0x88DE28`).
  - New data `rom:0x89A5C4`-`0x89A8AF`: three record copies and two ticks (was 0xFF, free since r23).
- Portrait slots `rom:0xF00000`-`0xFFFFFF`, the live block `rom:0x894EAC`, palette copies `rom:0x1DA6C8` and `rom:0x3ECBA4` (including 172): equal.
- The in-memory build of the list equals the r27 file.
- States: the r27 `.sav` and `.ss1`-`.ss3` equal the r26 files. One RAM word names a changed byte: ss3 IWRAM `0x03007D70` = `0x083EA400`, the base of the Cell fight table. That state is at index 22, and word 0 (seq 1) already ran, so it should not read the new copy (LIKELY harmless). No RAM word names an old record. The stored ROM CRC32 is still r18's `8656B1E5`, so mGBA shows its "different version" warning, as before.

---

## 8. Open points

1. **Goku in the fights.** Drain runs in fights, as decided. Goku has full EP at seq 1, but a long fight against Cell can drain him to base (about 46 s at 1 EP per 20 frames), and B reverts him. He stays base until "Me? Fight Cell?" seq 21 in that case. A refill or a no-drain rule for him in fights would be a new decision.
2. **Gohan and the B button.** Gohan can still press B to go to base during his fights, as the study said. Rage still forces the gi Super Saiyan 2 form.
3. **Every Super Saiyan pauses in scenes**, not only Gohan and Goku: entries 11 (Vegeta), 16 and 17 (Trunks) too. This follows "everywhere in the game". Super Vegeta and Super Trunks (+15, entries 10 and 14) still drain in scenes, because the brief limits the change to Super Saiyan and Super Saiyan 2.
4. **Old states mid-record.** A state saved inside one of the three old records (during a walk or wait in that record) keeps running the old bytes. The three r27 states are not in one.

---

## 9. My test plan

| Step | File | What to see |
|---|---|---|
| 1 | `log2_poc_r27.gba` + `log2_poc_r27.sav` **slot 3** (Goku leads at Dende's Lookout, `flag:191`) | Fly to the Cell Games Arena. On 14,1 Goku is base; the barrier lets him pass |
| 2 | same | 14,2 entry scene: everyone arrives, then Goku powers up (power-up pose, flash) and turns gold. "I'll fight Cell first." shows portrait 65. NPC Gohan is gold, his lines show 115 |
| 3 | same | During the long Hercule scene Goku stays gold: no drain in scenes. When the fight starts, EP is full or nearly full (open the status page early in the fight) |
| 4 | same | Fight Cell: EP drains as before. Ring event, map 14,3, second fight |
| 5 | same | "Me? Fight Cell?": NPC Gohan gold (115). After "Okay. I'll do it." Gohan leads in Super Saiyan; NPC Goku is gold with portrait 65 |
| 6 | same | Android 16, Cell Jr (Piccolo, Vegeta, Trunks lead). Gohan leads again in Super Saiyan. The scene from that point to Rage (seq 27) is one scene, so the status page cannot open in it: check EP when the Rage fight starts (full, as the refill plus the scene pause keep it). Rage gives the gi Super Saiyan 2 form and text |
| 7 | same | Self-destruct: NPC Goku gold until he teleports. Other World lines keep portrait 64. Cell beaten: Gohan base (gi), post-Cell as before |
| Quick A | `log2_poc_r27.ss2` ("Me? Fight Cell?", Goku gold, EP 19) | Wait on each text box for 10 s: Goku stays gold (r26 would drain 19 EP in about 6 s). Seq 21: Gohan leads gold, NPC Goku gold, portrait 65 |
| Quick B | `log2_poc_r27.ss3` (Cell fight scene, Gohan base) | NPC Goku gold and portrait 65 in the self-destruct scene; Rage from base. It cannot test the Super Saiyan start or the refill (seq 1 already ran) |
| Not for this test | `.ss1` (title or debug) | |

---

## 10. Concerns

1. **Not tested in game.** The proof is bytes, interpreter runs and state reads.
2. **Brief deviations:**
   - Two shell calls started with `cd`: a `listing.py` run (into `scripts\permanent`), and the Python edit of `states_marker.py` (into `scripts\one-time\2026-10-20-r27-build`). Both used absolute paths for their work and changed no other file.
   - I edited four files through Python heredocs in Bash, not Python: `test_art_inject.py`, `test_inject.py`, `diff_proof.py`, `states_marker.py`. No replacement string held a backslash. The lint run (`scripts\one-time\2026-10-20-inject-tool\lint.py`) shows no BOM, CR, control character or dash in any touched file.
3. **Changed tests:** 8 failing tests in `test_art_inject.py` and `test_inject.py` failed before r27 because of my r24-r26 art. I changed what they compare, not what they mean (section 5). Please review those edits.
4. **The pause covers every Super Saiyan** (open point 3). Say if Vegeta and Trunks should drain in scenes after all.

---

## 11. Files

- **New:** `scripts\permanent\patches\cellgames_ssj.py`, `scripts\permanent\patches\scene_drain_pause.py`, `scripts\permanent\tests\test_cellgames_ssj.py`.
- **Changed:** `scripts\permanent\build_list.txt` (two lines at the end), `scripts\permanent\tests\test_art_inject.py`, `scripts\permanent\tests\test_inject.py`, `docs\build-log.md` (one build line).
- **New ROM and states:** `builds\log2_poc_r27.gba`, `.sav`, `.ss1`, `.ss2`, `.ss3`.
- **Work scripts and outputs in `scripts\one-time\2026-10-20-r27-build\`:** `states_marker.py`/`.txt`, `marker_proof.py`/`.txt`, `push_callers.py`/`.txt`, `diff_proof.py`/`.txt`, `suite_before.txt`, `suite_after.txt`, `bible_rows.md` (sections 6, 8, 11, 14; tag `R27`).
- **Not touched:** `data\`, `docs\RE-BIBLE.md`, `art\portrait-sources\`, the art tables, every earlier ROM, `.sav` and state. I did not run `inject.py portrait` or `palette`.
