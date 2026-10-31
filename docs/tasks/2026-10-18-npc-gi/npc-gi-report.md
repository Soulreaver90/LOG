# NPC gi report (2026-10-18)

Brief: `docs\tasks\2026-10-18-npc-gi\npc-gi.md` (my rule 2026-10-18 6:29 PM). Base: r14 patch list.

Labels: **CONFIRMED** = proved here with bytes, code or a test. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

## Status

| Item | Result |
|---|---|
| Patch | `scripts\permanent\patches\npc_gi.py` (new), runs after `cutscene_portraits` |
| Tests | `scripts\permanent\tests\test_npc_gi.py`: **17 new**. Whole suite before the build: **266 OK** (249 from r15 + 17) |
| r16 | `archive\builds\log2_poc_r16.gba`, SHA-1 **`1adfa726be51b69c4ffcd24fe1e968ac70fbdd1b`**, patches `gohan_gi,ssj2_form,gohan_portraits,status_bonus,ssj2_idle,cutscene_portraits,npc_gi` (the r15 list plus mine), no env vars. Built after `r12fix-intake-report.md` appeared (r15 `34e3e3de`) |
| r16 extras | `log2_poc_r16.sav` = copy of `log2_poc_r15.sav` (SHA-1 `c755acf0`), `log2_poc_r16.ss1` = copy of `log2_poc_r15.ss1` (`47f898f3`); both new, nothing overwritten. r15 unchanged (`34e3e3de`). Build line plus a descriptive line in `docs\build-log.md` |
| r16 against r15 | `scripts\one-time\2026-10-18-npc-gi\r16_diff.py`: **PASS**. 1450 bytes differ: 36 in the base 8 MB (section 3d), the reverse-copy byte `rom:0x800029`, the hook pool word `rom:0x894EA8`, and new data `rom:0x894EAC`-`0x895430` (all 0xFF in r15). Nothing else (CONFIRMED, byte diff). The in-memory test build of the r15 list gives r15's SHA-1 and, with `npc_gi`, r16's: the tests ran on the exact r16 bytes |
| Mutation check | `scripts\one-time\2026-10-18-npc-gi\mutate.py`: dropping one site, one map object or the chamber-exit ext 73 edit, or undoing the reverse-copy edit, each fails 2-4 tests |

---

## 1. Where "control" returns (CONFIRMED)

The chamber exit is one scene table, `rom:0x3DBDD4` (34 records). It runs from seq 1 to seq 34 without a break:

- seq 1 sets `flag:154`; seq 2 "Goku and Gohan had emerged from ... the Hyperbolic Time Chamber".
- seq 3 spawns NPC Gohan `set:56` and runs ext 73 (0, 56): Gohan's record goes to entry 2.
- seq 27 runs ext 70 (4) (Goku leads) and ext 80 (0) (Gohan selectable); seq 31 "You are now playing as Goku."
- seq 32 walks NPC Gohan off (ext 54/52 on 56) and sets `flag:158`; seq 34 ends the scene.

So the player gets control after seq 34. Gohan is first controllable from there (Switch Characters). Everything in this table is **before control**. Every Cell Games and post-Cell scene is **after control**: the Cell Games Arena landing needs `flag:191`, set long after `flag:158` (SAV row "Party and outfits at flag:191").

## 2. Timeline table

Search shapes for set sites (`scripts\one-time\2026-10-18-npc-gi\sites.py` on r14): **A** = decode every type 0 record that a scene-table word points at, constant stack; **B** = every `02 N` pair in `rom:0x3B5000`-`0x420000`, back-decoded. A and B agree on the same 19 hits. B-only hits (7) are not set ids: ext 33/100 "1" at `@0x083E3C65`, `@0x083E3E83`, `@0x083F3B8B` are text records (OUT); ext 112 at `@0x084011CB` is a map record (OUT); "160" at `@0x083F1DCB`, `@0x083F1E13`, `@0x08402E77` is data (set 160 did not exist in vanilla). A run-time set id appears in neither shape. Map objects: `scripts\one-time\2026-10-16-task-3-outfit-research\mapsets.py` (1984 records), only entries 323 and 325 hold a Gohan set (others are enemy types or trigger coordinates, OUT section 5).

### 2a. Portrait records with raw 59 (CONFIRMED placement)

| Record | Bytes r14 | Scene | Control | Change |
|---|---|---|---|---|
| `@0x083DB930` | `10 00 02 3B` | chamber exit seq 16 "Hey Dende, ... three wishes" | before | `10 00 02 79` (id 121 = armor) |
| `@0x083DBABC` | `15 00 02 3B` | chamber exit seq 21 "Wow! That's great ..." | before | `15 00 02 79` |
| `@0x083DBFDC`, `@0x083DC1AC`, `@0x083DC870`, `@0x083DCE54`, `@0x083DCECE` | `NN 00 0T 3B` | post-Cell Lookout list `rom:0x3DD044` (`flag:195` set) | after | none (hook: gi 119) |
| `@0x083E8170`, `@0x083E81A0` | `02 00 01 3B`, `04 00 01 3B` | Cell Games Arena NPC talk `rom:0x3E81D4` (map 14,1 object) | after | none |
| `@0x083E9230`, `@0x083E934C` | `0F 00 01 3B`, `13 00 01 3B` | "Me? Fight Cell?" table `rom:0x3E93E8` seq 15, 19 | after | none |

### 2b. Script set sites (set-id push bytes; `@` = the ext call)

| Call | Push bytes r14 | Scene | Control | Change |
|---|---|---|---|---|
| ext 51 `@0x083DB5D7` | `1D 03 70 8D 10 86 60` (56,840,432) at `rom:0x3DB5D0` | chamber exit seq 3, spawn | before | none |
| ext 55 `@0x083DB5DD` | `1D 02 70 02` (56,1) | chamber exit seq 3 | before | none |
| ext 73 `@0x083DB62B` | `1D 02 00 70` (0,56) at `rom:0x3DB627` | chamber exit seq 3 | before | `00 00 00 9D` (0,157): record write only, see 3c |
| ext 54 `@0x083DBD6A` | `1D 03 70 8D 10 87 40` | chamber exit seq 32, walk off | before | none |
| ext 52 `@0x083DBD6E` | `00 38` | chamber exit seq 32 | before | none |
| ext 51 `@0x083E8673` | `1D 03 70 87 40 8C 50` (56,480,808) | Cell Games entry `rom:0x3E8D98` seq 1, spawn (map 14,2, sets `flag:193`) | after | relocated: `00 9D 1D 02 87 40 8C 50` |
| ext 53 `@0x083E8688` | `1D 03 70 87 40 8B 00` | same seq 1 | after | relocated: `00 9D 1D 02 87 40 8B 00` |
| ext 55 `@0x083E8C2F` | `1D 02 70 00` at `rom:0x3E8C2B` | same, seq 22 | after | `00 9D 00 00` |
| ext 56 `@0x083E8D21` | `1D 02 70 00` at `rom:0x3E8D1D` | same, seq 26 | after | `00 9D 00 00` |
| ext 56 `@0x083E8D44` | `1D 02 70 00` at `rom:0x3E8D40` | same, seq 26 | after | `00 9D 00 00` |
| ext 55 `@0x083E921F` | `1D 02 70 06` (56,3) at `rom:0x3E921B` | "Me? Fight Cell?" `rom:0x3E93E8` seq 14 | after | `00 9D 00 03` |
| ext 55 `@0x083E9229` | `1D 02 70 00` at `rom:0x3E9225` | same, seq 14 | after | `00 9D 00 00` |
| ext 52 `@0x083E939C` | `00 38` at `rom:0x3E939A` | same, seq 21 (removes the 14,3 map object) | after | `00 9D` |
| ext 73 `@0x083EA369` | `00 00 00 A0` | Rage, `rom:0x3EA400` seq 27 | after | none (gi Rage 160 since r13) |
| ext 73 `@0x083EBFFC` | `1D 02 00 70` (0,56) | post-Cell `rom:0x3EC758` seq 20 | after | relocated: `00 00 00 9D` |
| ext 51 `@0x083EC021` | `1D 03 70 86 60 86 70` (56,432,440) | same seq 20, spawn | after | relocated: `00 9D 1D 02 86 60 86 70` |
| ext 55 `@0x083EC027` | `1D 02 70 02` | same seq 20 | after | relocated: `00 9D 00 01` |
| ext 54 `@0x083EC2D2` | `1D 03 70 86 00 88 30` | same table seq 37, walk off | after | relocated: `00 9D 1D 02 86 00 88 30` |
| ext 52 `@0x083EC2D6` | `00 38` | same seq 37 | after | relocated: `00 9D` |

No after-control site uses `set:59` (Super Saiyan) or `set:58` (Rage) as an NPC (shapes A and B). CONFIRMED.

### 2c. Map objects

| Object | Bytes r14 | Scene | Control | Change |
|---|---|---|---|---|
| map 14,1 `@0x08408C90` +0x10 (`rom:0x408CA0`), factory `@0x0800B710`, talk `rom:0x3E81D4` | `38 00 00 00` | Cell Games Arena NPC, condition leader is not 0 and `flag:195` clear | after | `9D 00 00 00` |
| map 14,3 `@0x08408F80` +0xC (`rom:0x408F8C`), factory `@0x0800D6DE` | `38 00 00 00` | Cell ring NPC, `flag:192` clear | after | `9D 00 00 00` |

Both factories pass the field straight to `get_set` (`@0x0800B718`, `@0x0800D6E4`). CONFIRMED (code).

### 2d. Pre-chamber waiting scenes (task 4)

- Chamber entry scene `rom:0x3DDE0C` (Goku: "I'm going in with Gohan, so Vegeta will have to go with Trunks"; Vegeta goes first) addresses Gohan as `set:53` (`push 53,1 ; ext 55` at seq 18). CONFIRMED.
- Lookout talk `rom:0x3DD7EC` (map 9,3 object `@0x08404198`: `+0x10 = 53`): "My dad thinks he can teach me ... in the Hyperbolic Time Chamber", portrait 56 (`01 00 02 38`). CONFIRMED.
- So in r14 Gohan waits in **`set:53` (Demon Clothes) with the kid portrait 56**, not the `set:56` armor. This is the vanilla look. Neither is changed by any patch, and the hook never maps 56. No gi there. CONFIRMED.
- **Changed nothing.** The brief's condition ("confirm Gohan is armor there") is not met as worded: he is in his pre-chamber outfit, not the armor. My question below.
- No scene inside the chamber with Gohan was found (text search "hamber": 12 records, none set inside it). LIKELY there is none.

## 3. The patch (`scripts\permanent\patches\npc_gi.py`)

### 3a. Pre-control portraits (`npc_gi.py:36-37`, `npc_gi.py:170-177`)

- Raw id 121 = a new portrait-block word equal to word 59 (the armor frame header; no pixel copy). The two chamber-exit records point at 121. CONFIRMED (tests).
- The block cannot grow in place (the word after it is frame 115's header). A copy with 122 words is allocated; `rom:0xBE10` and the hook's pool word move to it. An aligned-word scan finds exactly these two references before and after; nothing points at the old block afterwards. CONFIRMED (test).
- No other id is the same frame as 59 (word or pixels), so there was no 2-byte fix. CONFIRMED.
- The dialog box `@0x0800B1E2` uses the record +3 byte for the layout (0, 1, 2-7), the style switch at `@0x0800B25E` (0x28, 0x31, 0x32, 0x35, 0x46, 0x54, 0x56, 0x60, jump table 26-39) and `portrait()` only; after `portrait()` it is not read. 121 and 59 take the same path. CONFIRMED (code, test pins the listing).
- No chamber-exit record after seq 3 uses speaker id 1 or 2 (they resolve through the table and bypass the hook). CONFIRMED (dump: ids 0, 3, 6, 46, 59, 63, 82).

### 3b. After-control NPC sprite (`npc_gi.py:40-67`, `npc_gi.py:179-187`)

- Actor lookup matches by set pointer (`@0x08009370`, message 5), so every after-control spawn, address and map object changes as one group to 157. CONFIRMED (test: in each scene the Gohan actor id is single and equals its spawn or map object).
- Two-value pushes become two op 0 pushes in place. Three-value pushes grow by one byte, so their records (`@0x083E8610`, `@0x083EBE1C`, `@0x083EC298`) are copied to the expansion area with the byte inserted, jumps re-encoded (`relocate()`, `npc_gi.py:90-119`), and the one scene-table word repointed (`rom:0x3E8D98`, `rom:0x3EC7A4`, `rom:0x3EC7E8`). Each record had exactly one pointing word and no pointer into its body. The old records stay, unreferenced. CONFIRMED (tests decode old and new op for op).
- Set 157 has the set 56 header (`00 04 15 10 08 ...`, slot 0x400), so the NPC object is sized the same. CONFIRMED (bytes, test).
- In r16: new block `rom:0x894EAC`, records `rom:0x895098`, `rom:0x89516C`, `rom:0x8953D0`.

### 3c. ext 73 and the reverse lookup (`npc_gi.py:35`, `npc_gi.py:41`, `npc_gi.py:188`)

- The post-Cell ext 73 (0, 56) set playable Gohan's sprite to the armor. It becomes (0, 157). The reverse lookup copy entry 2 +1 becomes 157 (`copy + 0x29`, `rom:0x800029` in r16).
- 56 is then in no entry, so the chamber-exit ext 73 must also say 157, else the assert hang. There Gohan is not the leader (seq 3 spawns him unconditionally and tests leader 1, 2, 3 for the others; ext 80 (0) comes only at seq 27), so ext 73 writes his record only: entry 2 either way, no sprite change. LIKELY (no leader trace).
- The eight ext 73 hits with run-time args inside the script region in `ext73.txt` (`@0x083B9FCE` ... `@0x083DF312`) are type 2 record headers `NN 00 02 49`, not calls. CONFIRMED (bytes).

### 3d. Base 8 MB diff (r16 against r15, CONFIRMED)

36 bytes: `rom:0xBE10`-`0xBE12`, `rom:0x3DB627`, `0x3DB628`, `0x3DB62A`, `0x3DB933`, `0x3DBABF`, `0x3E8C2B`-`0x3E8C2D`, `0x3E8D1D`-`0x3E8D1F`, `0x3E8D40`-`0x3E8D42`, `0x3E8D98`-`0x3E8D9A`, `0x3E921B`-`0x3E921E`, `0x3E9225`-`0x3E9227`, `0x3E939B`, `0x3EC7A4`-`0x3EC7A6`, `0x3EC7E8`-`0x3EC7EA`, `0x408CA0`, `0x408F8C`. Expansion: the reverse copy byte, the hook pool word and new data after the last r14 allocation.

## 4. Tests (`tests\test_npc_gi.py`, 17, CONFIRMED)

- Each in-place site's old and new bytes; each relocated record: same pushed values with 56 to 157 at the sites only, every other op equal, old bytes left, table word repointed, the loop target kept.
- Reverse copy: 157 finds entry 2, 160 entry 4, 53 entry 0, 55 entry 1, 56 none; no ext 73 in any scene names 56.
- Gohan set per scene table: chamber exit 56 (4 actor sites) plus ext 73 157; Cell Games entry, "Me? Fight Cell?" and post-Cell 157 only; each addressed id has its spawn or map object.
- Hook (in the `test_status` interpreter): id 121 gives the vanilla armor frame in entries 0, 1, 2, 3, 4, 5, 22; the 9 after-control records give gi frame 119 in entry 2 and the armor in entry 1; ids 1-120 unchanged in entries 1, 2, 4, 22 after the block move.
- Dialog box listing unchanged and 121 outside its compared constants; set 157 header equals set 56; diff only at the sites and new data; fails closed on a wrong byte at 7 sites and without the notes.

## 5. My test plan (r16)

1. Load `log2_poc_r16.gba` with `log2_poc_r16.sav` (copy of r15's, the `log2_lv40_cellgames.sav` set). No cheats.
2. **Slot 3** (flag 191, Goku on Dende's Lookout, save-slots report). Make an mGBA save state.
   - Fly to "The Cell Games Arena" (map 14,1). Expect: NPC Gohan stands in the **purple gi**, not the armor. Talk to him (A): gi portrait on "I know you'll be able to beat Cell!".
   - Walk north through the barrier. Expect "GOKU: I'll fight Cell first." with NPC Gohan in the gi in the crowd.
   - After Goku gives up: "Me? Fight Cell?" and "Okay. I'll do it." show NPC Gohan in the gi with the gi portrait.
   - Play on to Rage (gi Rage) and the end of the fight. After "Gohan, now's your chance!": playable Gohan stays in the **gi** after the Kamehameha (r14 showed the armor here), lies down in the gi, and walks off in the gi with the others.
3. **Slot 1 or 2** (post-Cell): Dende scene on the Lookout, as in r14. Expect the same gi portraits (regression check).
4. **Chamber exit** (armor sprite and armor portrait on "Hey Dende ... three wishes" and "Wow! That's great ..."): not reachable from these saves (`flag:154` is long before). Two type 5 hand-offs start it: `@0x083CF7E0` (Bulma's Capsule Corp talk, seq 24) and `@0x083D152C` (Cell's TV announcement, seq 9, right after it sets `flag:157`). LIKELY condition: `flag:156` (Scouter from Bulma) and `flag:157` (Cell announced) both set. Route: from a save before Cell's announcement with the Scouter already received, or after the announcement without the Scouter, get the other one (watch the announcement, or talk to Bulma). The leader then is Piccolo, Vegeta or Trunks. No current test save has this state, and a hand-made one would need many later flags cleared (154, 158, 191-196) and the party reset: I did not make one. My own pre-chamber save is the safe path.

## Files

| File | Change |
|---|---|
| `scripts\permanent\patches\npc_gi.py` | new |
| `scripts\permanent\tests\test_npc_gi.py` | new (17 tests) |
| `scripts\one-time\2026-10-18-npc-gi\` | `sites.py` (shapes A and B), `scene.py` (scene dump), `mutate.py` (mutation check), `r16_diff.py` (r15 to r16 proof), `fix_buildlog.py` (concern 9) |
| `docs\RE-BIBLE.md` | source `NGI`, rows in 5a, 6, 8, 12 and 13 |
| `docs\build-log.md` | r16 build line and descriptive line |
| `archive\builds\log2_poc_r16.gba`, `.sav`, `.ss1` | new |

## Concerns

1. **Waiting scenes are not armor** (CONFIRMED): pre-chamber Gohan is `set:53` (Demon Clothes) with the kid portrait 56, the vanilla look. Me: keep it, or use the armor there too? Changing it is a pre-chamber story change and was not made.
2. **One pre-control byte changed:** the chamber-exit ext 73 now names 157, forced by the reverse-copy edit. Invisible only if Gohan is not the leader there (LIKELY: both triggers run while Gohan and Goku are in the chamber, and seq 3 spawns NPC Gohan unconditionally).
3. **Relocated scene records** are the first script records outside `rom:0x3B5000`-`0x420000`. The type 0 handler `@0x0800B428` takes the record from a pointer, so LIKELY fine. Not tested in game.
4. **Shared set 157:** NPC and playable Gohan now have the same set, so a lookup on 157 could hit the player if Gohan leads. This is no worse than vanilla: there, playable Gohan in entry 2 is `set:56`, the NPC's set, so r16 restores the vanilla pairing (CONFIRMED, appearance table). Also the 14,1 object excludes Gohan as leader, Goku leads on 14,2 and 14,3 until `flag:192`, and post-Cell Piccolo leads before the spawn.
5. **Chamber exit not testable** from the current saves.
6. **Not tested in game.** All proof is bytes, decoders and the Thumb interpreter.
7. **Search limits:** a run-time set id and scripts outside `rom:0x3B5000`-`0x420000` are not covered.
8. **Brief deviation:** I ran one read-only Bash command with `cd` (an `ls` and `grep` survey). Nothing was written.
9. **Build-log slip, fixed:** my first append of the descriptive line went through a shell string, and `\r`/`\n` in the path became a CR and an LF. `fix_buildlog.py` rewrote only that line (it asserts the damage first). The file now has no CR. The auto line from `log2_build.py` was not touched.
