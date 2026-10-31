# Cutscene portraits report (2026-10-18)

Brief: `docs\tasks\2026-10-18-cutscene-portraits\cutscene-portraits.md`. Built on r13 (SHA-1 `2f8de787`, unchanged).

Labels: **CONFIRMED** = proved here with bytes, code or a test. **LIKELY** = strong evidence, not proved. **SPECULATIVE** = a guess.

## Status

| Item | Result |
|---|---|
| r14 | `archive\builds\log2_poc_r14.gba`, SHA-1 `94d3028da6dd0ca762c8099e5e934da303eddefc`, patches `gohan_gi,ssj2_form,gohan_portraits,status_bonus,ssj2_idle,cutscene_portraits`, no env vars |
| r14 against r13 | 65 bytes differ: `rom:0xBE06`, `rom:0xBE08`-`0xBE0F` (the site) and `rom:0x894E74`-`0x894EAB` (the hook). Nothing else (CONFIRMED, byte diff) |
| r14 extras | `log2_poc_r14.sav` = copy of `test-data\saves\log2_lv40_cellgames.sav` (SHA-1 `c755acf0`); `log2_poc_r14.ss1` = copy of `log2_poc_r13.ss1` (newest by mtime, SHA-1 `47f898f3`) |
| Tests | Whole suite **239 OK** (222 before + 17 new in `tests\test_cutscene.py`). `frame_lock.py check --golden` exits 0 |
| Fix | **A** (hook in `portrait()`), by state |
| Review | `archive\2026-10-18-art-review-renders\cutscene_portraits.png` (I looked at it) |

---

## 1. The records

### 1a. My line (CONFIRMED)

- Record `@0x083DBFDC`, bytes `03 00 02 3B E7 63 00 20`: seq 3, **type 2**, portrait **59** (0x3B = entry 2 vanilla, the armor), then a webfoot stream at +4.
- The decoded text: "GOHAN: Don't be sad. He's not! / He told me himself ... / That was how I was able to beat Cell!  My dad helped me." The screenshot shows its last page.
- Correction to the brief: it is **type 2 (compressed text)**, not type 1. That is why a plain text search finds nothing. Handler `@0x0800B474` calls `@0x0800B304`, which unpacks record +4 through `@0x080236A8` and then calls the box `@0x0800B1E2` with `ldrb r2,[r5,#0x3]` (the portrait byte).
- My fact "raw id > 7" is CONFIRMED; the exact id is 59.

### 1b. Record types (CONFIRMED, code)

Handler table `@0x083EC84C`: type 0 `@0x0800B428` (bytecode), 1 `@0x0800B438` (text at +4), 2 `@0x0800B474` (stream at +4), 3 `@0x0800B464` (format pointer +4, script +8), 4 `@0x0800B484` (script pointer +4, stream +8), 5 `@0x0800B494`. Types 1-4 all pass record +3 to `@0x0800B1E2`, which calls `portrait(id)` at `@0x0800B2B2`. So types 2-4 matter as much as type 1.

### 1c. Every record with a Gohan portrait byte (56-62)

Search shapes (tool `scripts\one-time\2026-10-18-cutscene-portraits\reconcile.py`):

| Shape | Hits |
|---|---|
| A: header `{seq, 0, 1-4, id}` plus decodable text (types 2/4 through the codec), `rom:0x3B5000`-`0x420000` | 40 |
| C: every aligned ROM word that points at a record header with a Gohan id | 40, the same set |
| B: raw header bytes, no text filter | 143; the 103 extra are script code bytes (`push`/`call`) and data, and no ROM word points at any of them |

A record reached only through a computed pointer outside the region would appear in none of these.

Per id: **56** x15, **57** x14, **59** x11, **58, 60, 61, 62**: none.

**Raw 59 (all post-chamber)** (CONFIRMED placement):

| Record | Bytes | Text start | Story point, and how placed |
|---|---|---|---|
| `0x083DB930` | `10 00 02 3B` | "GOHAN: Hey Dende, would it be possible to make these Dragon Balls grant three wishes" | Chamber exit scene (table `rom:0x3DBDD4`): seq 1 sets `flag:154`, seq 2 "Goku and Gohan had emerged from ... the Hyperbolic Time Chamber", seq 3 runs ext 73 (0, 56) unconditionally at `@0x083DB62B`; this is seq 16 |
| `0x083DBABC` | `15 00 02 3B` | "Wow! That's great considering the old Dragon Balls..." | same scene, seq 21 |
| `0x083DBFDC` | `03 00 02 3B` | my line | post-Cell Lookout scene (list `rom:0x3DD044`): seq 1 runs ext 70 (0) (Gohan leads), seq 2 "DENDE: ... sorry about your father", seq 88 sets `flag:196` |
| `0x083DC1AC` | `0D 00 01 3B` | "Krillin, you have a crush on Android 18!" | same scene, seq 13 |
| `0x083DC870` | `2B 00 01 3B` | "You've given us so much, dad. Thank you." | same scene, seq 43 |
| `0x083DCE54` | `51 00 01 3B` | "Will you be staying here Piccolo?" | same scene, seq 81 |
| `0x083DCECE` | `57 00 01 3B` | "Goodbye!" | same scene, seq 87 |
| `0x083E8170` | `02 00 01 3B` | "GOHAN: I know you'll be able to beat Cell!" | Cell Games NPC talk (table `rom:0x3E81D4`, referenced from map data `rom:0x408C9C`; seq 1 picks it when the leader is Goku). Post-chamber by story (Cell Games) |
| `0x083E81A0` | `04 00 01 3B` | "GOHAN: I know my dad will be able to beat Cell!" | same NPC (table `rom:0x3E81E0`) |
| `0x083E9230` | `0F 00 01 3B` | "Me? Fight Cell?" | Cell Games scene (table `rom:0x3E93E8`) seq 15, before ext 70 (0) at `@0x083E93A8` |
| `0x083E934C` | `13 00 01 3B` | "Okay. I'll do it." | same scene, seq 19 |

**Raw 56 (all pre-chamber, kid portrait, not mapped)**: `0x083B624C` (early game), `0x083CBD10`, `0x083CBD90` (Androids arrive), `0x083D3AAE`, `0x083D3B4C`, `0x083D3C4C` (Goku's heart virus), `0x083D4738` (after Android 20, sets `flag:85`), `0x083DD6C8`, `0x083DD73C`, `0x083DD790` (Lookout NPC talk: "My dad thinks he can teach me ... in the Hyperbolic Time Chamber"), `0x083DE07C`, `0x083DE50A`, `0x083DE594`, `0x083DE606` (Bulma scene), `0x083DF672` (Trunks scene, seq 18 sets `flag:129` and runs ext 73 (0, 53), entry 0). Placed by text and by the flags in their scenes or triggers (all below `flag:154`, the chamber exit). The Bulma scene table `rom:0x3DE6F4` is run by map 9,3 region `@0x0840426C` (`flag:148` set and `flag:149` clear, `conds.txt`). The Lookout talk `rom:0x3DD7EC` is map 9,3 object `@0x08404198` (`flag:143`, not `flag:148`). CONFIRMED for all but `0x083B624C`, which is LIKELY (early-game region, text only).

**Raw 57 (Future Gohan, not mapped)**: 14 records `0x083B6D38`-`0x083B7666`, the Trunks flashback ("I'm your master", training Trunks). 57 is no appearance entry's +2. Not playable Gohan, so the hook passes 57 through (CONFIRMED by text and the table).

### 1d. Rage lines (step 3)

No record passes raw 61. The Cell-fight Gohan lines use **speaker 1** (leader). After ext 73 (0, 160) at `@0x083EA369`, Gohan's record is in entry 4. `@0x08026440` reads entry 4 +2 = 61 and calls `portrait(61)` again, so r13 shows the armor Rage portrait next to the gi Rage sprite.

| Record | Text |
|---|---|
| `0x083EA370` | "AHHHHHHHHHHH!!!" (seq 28, right after the Rage seq 27) |
| `0x083EA93C` | "What? Dad?" |
| `0x083EAA14` | "DADDY!!!!!!!!!!!" |
| `0x083EAA92` | "It's all my fault. Dad didn't have to sacrifice himself." |
| `0x083EAFA4` | "You don't scare me Cell!!!!" |
| `0x083EB414` | "What's the point? We've lost." |
| `0x083EB4CE` | "Dad!? Where are you?" |
| `0x083EB654` | "But all this is my fault." |
| `0x083EB6DC` | "I will!" |

- Between `@0x083EA369` and `@0x083EBFFC` (post-Cell ext 73 (0, 56)) no code record in the scene tables calls ext 70 or ext 73 (scan of every scene-table pointer into `0x083E9400`-`0x083EC800`). So these lines run in entry 4. CONFIRMED (static); a run-time path that reverts Rage in the fight would not appear (Rage locks the ability, `+0` bit 1).
- `0x083EC07C` onward ("PICCOLO: He did it!") runs after ext 70 (1) at `@0x083EC00F`: speaker 1 is Piccolo there. Not affected.

---

## 2. Fix chosen: A, the hook (CONFIRMED)

Why A:

1. **The state is reliable.** `portrait()` already reads the party records through block word 0 (`0x03000E90`) for ids 1-7. Gohan is record 0, so his appearance entry is `@0x03000EA4` (struct + 0xC + 8; matches the FRM my memory row). The only writer a script uses is ext 73: `@0x0800A936`-`@0x0800A948` passes struct (`[@0x083B5C98]` = `0x03000E90`) + 0xC + 28 x character to the reverse lookup, which does `strb r2,[r0,#0x8]` at `@0x080042D0`. The record is save data, so a loaded save restores it.
2. **Each 59 line runs after its entry 2 write**: chamber exit seq 3 before seq 16/21; post-Cell `@0x083EBFFC` before the Lookout scene; the Cell Games lines come long after the chamber.
3. **No misfire possible on the found records**: every raw 59 is post-chamber and every raw 56 is pre-chamber, and 56 is never mapped. So even a wrong state could not turn a pre-chamber line to gi.
4. **A covers Rage without a table edit.** B (byte repoints) cannot reach speaker-1 lines; it would need entry 4 +2 changed too. A also covers records a static scan cannot see.

### Site (`portrait()` id > 7 path)

```
0800bdee  cmp r0,#0x7
0800bdf0  bgt 0x800be06            ; the only branch into the site (test: BL/B/Bcc scan of base code, aligned words)
0800be06  ldr r1,=0x08894e75       ; r13: ldr r1,=block ; lsl r0,r0,#2 ; add r1,#4 ; ldr r0,[r1,r0] ; b 0x800bdd2
0800be08  bx r1
0800be0a  (2 pad bytes, never run)
0800be0c  .word 0x08894e75
0800be10  .word 0x0888e3cc         ; block literal, unchanged: ids 1-7 (0x0800BDD4) use it
```

### Hook (`rom:0x894E74`, 0x38 bytes, `patches\cutscene_portraits.py`)

```
08894e74  ldr r1,=0x0888e3cc       ; portrait block
08894e76  ldr r3,[r1,#0x0]         ; save struct 0x03000E90 (block word 0)
08894e78  ldrb r3,[r3,#0x14]       ; Gohan's appearance entry (record 0 +8)
08894e7a  cmp r0,#0x3d             ; 61 (armor Rage)
08894e7c  bne 0x8894e86
08894e7e  cmp r3,#0x4              ; entry 4: gi Rage set 160
08894e80  bne 0x8894e9e
08894e82  mov r0,#0x75             ; 117 gi SSJ2
08894e84  b 0x8894e9e
08894e86  cmp r3,#0x2 ; beq        ; gi entries 2, 5, 22
08894e8a  cmp r3,#0x5 ; beq
08894e8e  cmp r3,#0x16 ; bne lookup
08894e92  cmp r0,#0x3b ; bne       ; 59 -> 119 gi base
08894e96  mov r0,#0x77
08894e98  cmp r0,#0x3e ; bne       ; 62 -> 115 gi SSJ
08894e9c  mov r0,#0x73
08894e9e  lsl r0,r0,#2
08894ea0  add r1,#0x4
08894ea2  ldr r0,[r1,r0]           ; table word, as vanilla
08894ea4  pop {r3,pc}              ; the frame portrait() pushed at 0x0800BDCC
```

- Uses r0, r1, r3 only; r3 comes back from the pop, so r2 survives as in vanilla.
- `apply` checks `portrait()` bytes `rom:0xBDCC`-`0xBE0F`, the block literal, struct word, frames 115/117/119, and entries 2/5/22/4 +1 = 157/158/159/160 before any write.
- Not touched: box style switch `@0x0800B25E` (tests the speaker id), palettes, the status +3 path (`rom:0x86FCD0`, ids 8-25 never mapped).
- `portrait()` callers (BL scan): `@0x08003A8E` (status, +3 ids), `@0x0800B2B2` (dialog), `@0x08018C8A`, `@0x080194F6` (menus, ids from an object field), `@0x08026450` (ids 1-7). The menus see the same mapping. LIKELY harmless: a post-chamber 59 or a Rage 61 there would now show gi too.

---

## 3. Tests (`tests\test_cutscene.py`, 17, CONFIRMED)

`portrait()` runs in the `test_status.PageCpu` interpreter as `thumb_dis` text, from `0x0800BDCC`, through the real `0x08026440` and relocated table:

- Every Gohan id 56-62 x entries 0, 1, 3 (armor), 2, 5, 22 (gi), 4 (Rage): equals the mapping; unmapped cases equal r13.
- Entry 1: every Gohan id returns the vanilla armor header. Entries 2/5/22: 59 = frame 119, 62 = frame 115. Entry 4: 61 = frame 117.
- Speakers 1 and 2 with Gohan in entry 4: r13 = 61 frame, r14 = 117 frame; entry 2 = 119; entry 1 = 58. Leader Piccolo: 90 in every Gohan state.
- Ids 8-120 except 56-62 (Piccolo 94, status 10/12/13, gi 115-120) in entries 1, 2, 4, 22: equal r13.
- r2, r4-r7 and sp kept.
- Base 8 MB differs from r13 only at the site; the expansion only at the hook; only the `bgt` enters the site; hook listing; vanilla interpreter equals the table; fails closed on a wrong site byte, block literal, entry 4 set (58) or entry 2 set.
- Records: my line bytes and text; shape C ids (59 = the 11 offsets, 58/60/61/62 = 0, 56 = 15, 57 = 14); script region equals base except the r13 Rage push; ext 73 (0, 56) bytes at `rom:0x3DB627` and `rom:0x3EBFF8`, and 56 = entry 2 in the reverse lookup copy.

Deviation from brief step 5: ids 56, 58 and 60 stay armor in a gi entry by design (no post-chamber record uses them).

---

## 4. Review image

`archive\2026-10-18-art-review-renders\cutscene_portraits.png` on (191, 255, 7), tool `scripts\one-time\2026-10-18-cutscene-portraits\review.py`. Left = armor state (r14, Gohan in entry 1; Rage lines: r13 in entry 4). Right = gi state (r14 in entry 2; Rage lines: r14 in entry 4). Seen:

- All 11 post-chamber 59 records: armor left, purple gi base portrait right.
- The 9 Rage lines: armor Rage left, gi SSJ2 portrait right.
- 56 (kid) and 57 (Future Gohan): the same on both sides.

---

## 5. My test plan

1. Load `log2_poc_r14.gba` with `log2_poc_r14.sav` in mGBA (no cheats). `log2_save.py info`: slots 1 and 2 have `flag:195` set and `flag:196` clear, Gohan in entry 2. Slot 3: `flag:195` clear.
2. **My scene (slot 1 or 2):**
   - Fly to Dende's Lookout (world map landing map 9,1 at 768,832).
   - **Make an mGBA save state first.** Seq 88 sets `flag:196` and seq 89 is a type 5 hand-off to `0x083B8140`, LIKELY the ending.
   - Talk to Dende (A) at about (760, 416). The map object `@0x08403F60` (Dende, `set:36`, condition `flag:195`) points at list `rom:0x3DD044` (CONFIRMED). That the A-press talk starts it is LIKELY (the factory `@0x0800B710` was not traced).
   - Expect the purple gi base portrait on "Don't be sad...That was how I was able to beat Cell!", "Krillin, you have a crush on Android 18!", "You've given us so much, dad.", "Will you be staying here Piccolo?" and "Goodbye!".
   - This scene sets `flag:196` (the farewell). Keep the .sav copy to repeat it.
3. **Rage (slot 3, pre-Cell Games):** the route to the Cell fight is not verified here (aura-rage report concern 7). If it reaches the fight: after "AHHHHH", every Gohan line shows the gi SSJ2 portrait. Before Rage, "Me? Fight Cell?" and "Okay. I'll do it." show the gi base portrait.
4. The chamber exit lines (`flag:154`) are not reachable from these saves.

---

## Files

| File | Change |
|---|---|
| `scripts\permanent\patches\cutscene_portraits.py` | new |
| `scripts\permanent\tests\test_cutscene.py` | new (17 tests) |
| `scripts\permanent\patches\gohan_portraits.py` | header line "Cutscenes keep the armor" updated (docstring only) |
| `scripts\one-time\2026-10-18-cutscene-portraits\` | `records.py`, `scenes.py`, `reconcile.py`, `callers.py`, `review.py`, `docs_edit_csp.py`, `gohan_records_r13.txt`, `gohan_scenes_r13.txt` |
| `docs\build-log.md` | r14 lines |
| `docs\RE-BIBLE.md` | `CSP` in the source list (line 27), 4 rows in 5a, 1 row in section 8 |
| `docs\research\re-portraits.md` | one sentence on raw ids in section 3 |

## Concerns

1. **Gi portrait, armor sprite** (CONFIRMED, by design of A): 6 of the 11 59 lines are spoken by NPC Gohan spawned with raw `set:56` (armor): chamber exit `0x083DB930`, `0x083DBABC`; Cell Games `0x083E8170`, `0x083E81A0`, `0x083E9230`, `0x083E934C`. They now show the gi portrait. RE-BIBLE decision row "every later cutscene and NPC Gohan uses the gi" (deferred) points the same way. Fix B could exclude them, A cannot without a list.
2. **Brief record type:** my line is type 2 (compressed), not type 1.
3. **Rage portrait source:** the Rage lines reach 61 through speaker 1, not a raw id. The status page still shows the armor Rage status portrait (12); the brief kept +3 out of scope.
4. **Menus** `@0x08018C8A` and `@0x080194F6` pass ids from an object field; their ids were not traced. Any 59 or Rage 61 there now maps too (LIKELY harmless).
5. **Not in-game tested.** The hook is tested in the interpreter only.
6. The shared scratchpad held another task's `docs_edit.py`; my first run hit it, failed on its first assert and wrote nothing (RE-BIBLE mtime and content unchanged then). My doc edits use `scripts\one-time\2026-10-18-cutscene-portraits\docs_edit_csp.py` and `docs_fix_csp.py`.
7. **Brief deviation:** I ran `cd` twice in Bash (to run unittest). No harm: no relative path wrote anything.
