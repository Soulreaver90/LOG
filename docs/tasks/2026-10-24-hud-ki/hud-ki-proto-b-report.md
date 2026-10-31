# HUD and ki mockup v2b report (state 46 on the ki pool)

Brief: `docs\tasks\2026-10-24-hud-ki\hud-ki-proto-b.md` (my ask, 2026-10-24 11:11 AM). Work files: `scripts\one-time\2026-10-24-hud-ki\proto\`. Bible rows (tag HKB): `scripts\one-time\2026-10-24-hud-ki\proto\bible_rows_b.md`.

I check it in mGBA.

Labels: C = CONFIRMED (bytes, listings or tests), L = LIKELY, S = SPECULATIVE.

---

## 1. Verdicts

| Item | Result | Label |
|---|---|---|
| Vegeta's hold move (ability 0, state 46) spends the pool | Built in v2b. One vtable word and one 8-byte stub | C (tests), L (in game) |
| Drain rates | Not changed. They stay as v2 for me review | C |
| v2 files | Not touched. v2b is a new set of files | C |
| v2 to v2b | 12 bytes in 2 runs, each byte named | C |
| r38 to v2b | 16,031 bytes in 1,892 runs, 0 outside a named region | C |
| Tests | 45 of 45 pass (31 v2, 13 state 46, 1 file test) | C |

---

## 2. The fix, proved by reading

### 2.1 What state 46 spends, and where

State 46 is the hold state that ability 0 starts. Its logic tick is vtable `0x080258B4` +8 = `@0x08015078`.

| Step | Address | What it does | Label |
|---|---|---|---|
| Entry | `@0x08015078` | r0 = state object, r1 = actor | C |
| Hold test | `@0x0801509E`-`@0x080150AE` | Reads input `@0x0300229C` +0x16 (released) bit 1 (B) | C |
| Release | `@0x080150B0`-`@0x080150DE` | B released: fires (`bl 0x08014160`), sound. No EP access | C |
| Scene gate | `@0x080150E0`-`@0x080150E6` | `[0x03000E1C +4]` bits 0-1 set: no drain | C |
| Record | `@0x080150E8`-`@0x080150F4` | Leader record from `[0x086E3614 +0xC]` = `0x03000E90` | C |
| Spend | `@0x080150F8`-`@0x08015106` | EP -1, clamp at 0 | C |
| Stop | `@0x08015108`-`@0x08015110` | At EP 0: move object (state +4) +0x48 = 0 | C |

- The method takes 1 EP for each call. It has no frame counter of its own (C).
- I did not trace how often the state machine calls +8. The older HKP row says "every 4 frames". That figure is not verified (S).
- The only `mov r1,#0x2e` in the code region and the hook area is the ability 0 action `@0x08013188`. A script state set (ext 57) would not show in that shape (C, one shape).

### 2.2 Why the v2 stub applies unchanged

| Check | Evidence | Label |
|---|---|---|
| Same record | `[0x086E3614 +0xC]` = `0x03000E90` = `[0x086F7E50 +4]` (the pool code `SAVE_PTR`). So the record that `swap_state` swaps is the record that state 46 spends from | C |
| Same signature | Slot +8, r0 = state, r1 = actor, as states 48, 49 and 51. The method reads no r2 or r3 on entry | C |
| Same code shape | The EP block `@0x080150E8`-`@0x08015112` matches state 51 `@0x080156D2`-`@0x080156FA` instruction for instruction. v2 wraps state 51 with the same stub | C |
| Nested calls | The release and state-0 paths run inside the swap, as in state 51. The guard byte stops a second swap | C |
| Vegeta uses the pool | Vegeta (record 2) holds ability 0 in slot 0 in every test slot. Base entry 8 +4 (transform target) = 11. Entry 11 form object = `0x030021EC`. No stretch rule applies to Vegeta | C |

### 2.3 The v2b change

- Vtable word `rom:0x258BC` (`0x080258B4` +8): `0x08015079` to stub `st46` (`0x08E1181D`), base-relative.
- New stub at `rom:0xE1181C`: `ldr r3,=0x08015079 ; b swap_state` plus its literal word.
- The stub is a second blob after the v2 blob. So no v2 code byte or literal moves.
- The builder refuses to write unless the result equals v2 in every byte outside these two regions.

---

## 3. Proof

### 3.1 v2 to v2b (every byte)

Source: `proto\proof_proto_b.txt`.

| rom | v2 | v2b | Meaning |
|---|---|---|---|
| `0x258BC`-`0x258BF` | `c5 f7 fe ff` | `69 bf de 00` | State 46 +8 word: vanilla tick to `st46` (base-relative) |
| `0xE1181C`-`0xE1181D` | `ff ff` | `00 4b` | `ldr r3,=0x08015079` |
| `0xE1181E`-`0xE1181F` | `ff ff` | `4b e7` | `b swap_state` (`0x08E116B8`) |
| `0xE11820`-`0xE11823` | `ff ff ff ff` | `79 50 01 08` | Literal `0x08015079` |

- The 8 stub bytes were 0xFF in v2 and in r38 (C).
- Window bytes `rom:0xE11000`-`0xE1181B` equal v2 (C).

### 3.2 r38 to v2b

| Check | Result |
|---|---|
| Built file equals the plan applied to r38 | True |
| Bytes that differ from r38 | 16,031 in 1,892 runs (v2: 16,019 in 1,891) |
| Bytes outside a named region | 0 |
| r38 words naming the window | 0 absolute, 0 base-relative |
| Built words naming the window | 22 ability words and 10 hook words, all named. `0x258BC` is one of them |
| Words naming `st46` | Only `0x258BC` |

### 3.3 Tests

- `py -3 -P scripts\one-time\2026-10-24-hud-ki\proto\test_proto_b.py`: 45 tests, all OK.
- The 31 v2 tests run against the v2b plan. `test_proto.py` on v2 still passes (31 OK).
- The state 46 tests run the real vanilla method `@0x08015078` through `st46` and `swap_state`:
  - A hold takes 1 from the pool for each call. The regular EP stays (pool 30 to 25 in 5 calls, EP 120).
  - Pool 1 or 0: the pool ends at 0, the move object +0x48 = 0, EP stays.
  - Base form (entry 8): the regular EP takes the drain, the pool stays.
  - Guard byte set: no swap.
  - Scene bits set: nothing spent.
  - B released: fire is called once, nothing spent.
  - Count 0x1F: state 0, nothing spent.
  - Ability 0 test and action, then 4 hold calls: pool 30 to 16, EP 7 stays.
  - A/B on v2: the same hold call drops the regular EP (120 to 119) and leaves the pool.
- Limits: the tests do not run the frame loop, so they do not show how often +8 runs.

### 3.4 SHA-1 of every new file

Folder: `scripts\one-time\2026-10-24-hud-ki\`

| File | SHA-1 |
|---|---|
| `mockups\log2_poc_r38_bfhud2b.gba` | `f5f5ee730346695c25035871378efebc084165b1` |
| `mockups\log2_poc_r38_bfhud2b_spar.gba` | `f5f5ee730346695c25035871378efebc084165b1` |
| `mockups\log2_poc_r38_bfhud2b_spar.sav` | `4ca6f109e12693512b579262cb11711d2bc68d06` |
| `mockups\log2_poc_r38_bfhud2b_scouter.gba` | `f5f5ee730346695c25035871378efebc084165b1` |
| `mockups\log2_poc_r38_bfhud2b_scouter.sav` | `d2fa5e1a016ae40fe3b264eb21008b807d391a1f` |
| `proto\build_proto_b.py` | `7daa9741d1477849919f0dd90e041abd5e4b93ea` |
| `proto\test_proto_b.py` | `c283ada3e5cf5804ed4d57e36af81301a1f763ec` |
| `proto\proof_proto_b.py` | `4a61ab48e49adbc7438aabb816f0fd0ad199becb` |
| `proto\st46_read.py` | `0c4632a143d7b2e0f690a7f31786a42c5cafddfa` |
| `proto\st46_saves.py` | `7dfd55b7d01ba588d3e45aab631e50ef482dadc0` |
| `proto\st46_maps.py` | `dd6dec42e8cab6d0bc241d36283903fc83ef6b2a` |
| `proto\proof_proto_b.txt` | `d87377a07e8d1ca3d16d0d5d5b4b7cba11ae49a6` |
| `proto\listing_proto_b.txt` | `f9176416079c98df1ad8d1a8bedd3ef11c14d203` |
| `proto\bible_rows_b.md` | `7927b0b25df90f5a544e61fa21c2b73830f36dc1` |

- The two `.sav` files are byte copies of the v2 pair saves, which are byte copies of the r38 `_spar.sav` and `_scouter.sav` (C).

---

## 4. My steps (mGBA)

Files are in `builds\mockups\2026-10-24-hud-ki\`. Keep each .gba and its .sav in the same folder with the same base name. Do not save in the game, so the pair stays reusable.

Facts from the saves (C): Vegeta has ability 0 in slot 0 and the Z icon (ability 12) in slot 2. Only Master Roshi's Island (map 11,1) allows ki moves among the test save spots. Switch Characters opens only from a save point.

### 4.1 Route A (short): Master Roshi's Island

1. In mGBA, use File > Load ROM and open `log2_poc_r38_bfhud2b_spar.gba`.
2. On the title screen, continue and load file 2 (Gohan on Master Roshi's Island, map 11,1).
3. Walk right about 150 pixels to the save point (rect 544-593, 136-185). Label L: the map object list names the save point record as its last (condition 0, pointer) pair before a non-pointer word, but I did not decode the list length.
4. Press A at the save point, choose Switch Characters, and pick Vegeta.
5. If no save point is there, use route B.

### 4.2 Route B (sure): Capsule Corp

1. Open `log2_poc_r38_bfhud2b_scouter.gba`. Load file 1 (Gohan at the Capsule Corp save point, C).
2. Press A on the save point, choose Switch Characters, and pick Vegeta.
3. Leave to the world map and fly to Master Roshi's Island. Its landing flag (68) is set in this file (C).

### 4.3 Test the hold move

How to read the ki row: the yellow pool covers the row from the left up to the pool level. Green regular ki shows only past the yellow end. Green under the yellow is hidden.

1. As Vegeta on Master Roshi's Island, press L until the HUD shows the Z icon. Press B.
2. Pass: at the end of the transform, a yellow bar covers the full ki row.
3. Press L until the HUD shows the ability 0 icon. Press and hold B.
4. Pass: the yellow drops by 10 points at the start (about 3 to 4 of the 49 steps), then gets shorter while you hold B.
5. Pass: past the yellow end, green fills the rest of the row to the right edge, and that green stays full while you hold B.
6. Release B. Pass: the move fires, and the yellow stops its fast drop. The slow form drain (1 every 20 frames) goes on.
7. Optional end case: hold B until the yellow is gone. Pass: the charge stops when the yellow reaches 0, and the whole row is green. Then Vegeta reverts within about 20 frames. Label L: no test runs the form tick while state 46 is active, so the revert during a hold is reasoning, not a test result.
8. A/B check: do the same steps in `log2_poc_r38_bfhud2_spar.gba` (v2). After the first drop of 10, the yellow does not get shorter while you hold B. The thin green strip past the yellow end goes away. On a long hold the charge stops while the yellow is still long, because the regular ki ran out under it. That difference is the fix.

---

## 5. Risks

- **Call rate (S).** The drain is 1 per call of +8. I did not trace how often the state machine calls it. The drain speed in game is the vanilla speed either way.
- **Script state sets (S).** A script (ext 57) that puts the leader in state 46 also spends the pool in a pool form. No such script was searched for.
- **Route A save point (L).** See section 4.1, step 3.
- **Revert during a hold (L).** See section 4.3, step 7.
- **The v2 risks stay.** IWRAM boot state, items and Senzu, regen in scenes, other forms (v2 report, section 6).

---

## 6. Final decisions

1. The drain rates (v2 final decisions 1 and 3) are still open. v2b keeps them as built.
2. Should a later build use v2b as its base?

---

## 7. Deviations from the brief

- None in scope. The fix stub is a second blob after the v2 blob, not a new line in the v2 stub list. A new line would move the v2 literal pool and rewrite every `ldr =` in the v2 code. This keeps "change only what the fix needs".
- I wrote three small read-only helpers (`st46_read.py`, `st46_saves.py`, `st46_maps.py`) for the reading proof and my steps.
- Python wrote `proto\__pycache__\build_proto_b.cpython-314.pyc` on import.
