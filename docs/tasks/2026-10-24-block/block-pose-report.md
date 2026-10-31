# Block mockup v3: the LoG II hurt frame as the block pose (report)

Date: 2026-10-24. Brief: `docs\tasks\2026-10-24-block\block-pose.md`.

Labels: **C** = CONFIRMED (code, bytes or a test quoted here). **L** = LIKELY. **S** = SPECULATIVE. Addresses are r37 (`builds\log2_poc_r37.gba`, SHA-1 `3877033c65d724a299a364f66a4c3d75a4df4566`). Bible rows: `scripts\one-time\2026-10-24-block\pose\bible_rows.md` (tag BLP).

---

## Verdicts

| Question | Answer | Label |
|---|---|---|
| Block pose | **Anim 2 (hurt) frame 2.** The game already shows this frame during a hit (ticks 16-23 of the 32-frame hurt state) | C (data, code) |
| What it shows | Goku crouches, head down, **both forearms crossed in front of his chest and face**, knees bent | L (by eye) |
| Shown the same in all 4 dirs as the hurt state | Yes. The draw takes flips, dx and dy from the record, and BLOCK writes the same row as the hurt enter | C (code, tests) |
| Exists in every player set | Yes. 23 live player sets, 4 records per dir in anim 2, no fallback needed | C |
| v3 built | `mockups\log2_poc_r37_block3.gba`, 2 bytes from v2, 562 bytes in 9 named runs from r37 | C |
| Tests | 25 OK (18 v2 tests + 7 pose tests) | C |
| Goku test pair | `log2_poc_r37_block3_goku.gba` and `.sav`: slot 1 Goku on map 7,1 near 5 tiger bandits | C (bytes), L (in game) |

---

## 1. The chosen frame (task 1)

Each heading below gives one result, then the evidence.

### 1.1 Renders (all in `scripts\one-time\2026-10-24-block\pose\`)

| File | What |
|---|---|
| `a2_s60.png` | Goku (set 60), anim 2, dirs 0-3, frames 0-3, scale 4 |
| `a2_s60_x8.png` | the same at scale 8 |
| `guard_candidates_s60_x12.png` | Goku frames 0-2 of dirs 0 and 2, frames 1-2 of dir 1, scale 12 |
| `a2_s61.png` | Super Saiyan Goku (set 61), anim 2 |
| `a2_s56.png`, `a2_s157.png` | armor Gohan (set 56) and gi Gohan (set 157), anim 2 |
| `a2_i2_player_sets.png` | anim 2 frame 2, dirs 0-3, of the 23 live player sets and set 56 |
| `enemy_sets_18_146.png` | the test enemy (set 18, tiger bandit) and the wolf (set 146) |

- `a2_i2_all_sets.png` is superseded. It used the vanilla appearance table, so it holds set 58 (Cell), whose art spills into the set 57 row.
- The Goku sets in the appearance table are 60 (entry 19) and 61 (entry 20). Entry 21 is set 72 (Hercule) (C).

### 1.2 Frame data (C)

- Sets 56, 60, 61 and 157: anim 2 has 4 records per dir. Each record is 16x32 at dx 0, dy -24.
- Dir 3 uses the dir 2 frame headers with the h-flip bit (attr1 0x1000). Dirs 0, 1 and 2 have no flip.
- Set 60 frame 2 headers: d0 `0x2B7DEC`, d1 `0x2B813C`, d2 and d3 `0x2B8498`.

### 1.3 Why frame 2 (L, by eye)

| Frame | Goku pose | Hurt stars (white pixels above the head, set 60) |
|---|---|---|
| 0 | Dir 0: arms in front, flinch. Dir 2: upright, one forearm out, eye open | d0 6, d2 2 (eye) |
| 1 | Deepest recoil, arms crossed, body thrown back | d0 3, d2 6 |
| **2** | **Crouched, head tucked, both forearms crossed in front of chest and face** | **d0 0, d1 0, d2 and d3 3** |
| 3 | Like frame 0, recovering, eyes wide | d0 0 (4 white = eyes), d2 2 (eye) |

- Frame 2 is the clearest guard: both arms cross in front, and it has the fewest stars.
- **It is still a hurt frame.** In dirs 2 and 3 three star pixels stay above the head. Dir 1 is the back view, so the arms do not show.
- Super Saiyan Goku (set 61) frame 2 shows the same crouch.
- Gohan (sets 56 and 157) frame 2: hunched, hands up in front of the face, with stars. It reads as a flinch more than a guard. The same frame index serves all sets, so Gohan shows this.

---

## 2. Per-dir display and the per-set check (task 2)

### 2.1 How the game shows a frame (C)

```
0x08007A84 (player vtable +0xC, frame select):
  record = [[obj+0x4C] + 4 x facing(+0x10)] + 12 x frame(+0x14)  -> obj+0x3C   (no bound on the frame)
  x += record dx (0x08007AA0), y += record dy (0x08007AAC)
0x08007784 (vtable +0x10): OAM word = record +4 (attr0, attr1: the flip bits)
```

- No state code flips or offsets per dir. The record decides.
- Hurt enter `0x0800E210`: +0x12 = 0, +8 = 0x28, +0x14 = 0, +0x4C = `set + 0x6C` (`add r0,#0x6c`), no branch on the set.
- Hurt anim tick `0x0800E222`: +0x12 += 1; at 0x20 it ends; else +0x14 = +0x12 >> 3. So frame 2 shows at ticks 16-23.
- The hurt move `0x080082C8` changes only the position, not the frame.

### 2.2 BLOCK uses the same layout for every set (C)

- `block_enter` writes `+0x4C = [+0x48] + BLOCK_ROW` with `BLOCK_ROW = 0x4C + 16 x 2 = 0x6C`, and `+0x14 = 2`. No branch on the set.
- `block_anim` never writes +0x14, so frame 2 stays.
- That is the hurt enter row and the hurt state's frame 2. Test `test_same_row_as_vanilla_hurt_enter` runs both enters on real set 60 and compares +0x4C and +8.
- Test `test_frame_select_shows_the_anim2_frame2_record_each_facing` runs the vanilla `0x08007A84` on the v3 ROM for facings 0-3. The record it picks is the anim 2 frame 2 record of that dir, and only facing 3 has the h-flip bit.

### 2.3 Every player set has the frame (C)

`pose\pose_check.py 2 2` reads the **live** appearance table. The 17 literals that `ssj2_form` repoints all name `0x0888DC54` (23 entries, set id at +1).

| Check | Result |
|---|---|
| Live player sets | 53, 55, 157, 57, 160, 158, 103, 104, 137, 138, 139, 140, 128, 129, 130, 132, 133, 134, 135, 60, 61, 72, 159 |
| Anim count byte (+2) > 2 | all 23 (lowest: set 135 with 14) |
| 4 dir pointers of row `set + 0x6C` are ROM addresses | all 23 |
| More than 2 records in each dir, frame 2 unpacks | all 23 (4 records each) |
| Record at index 2 = row pointer + 24 | all 23 |
| Result | **23 OK, 0 FAIL** |

- Sets 56, 58 and 59 of the base table also pass, but they are not player sets in r37.
- Second shape for the set source: no patch in `scripts\permanent\patches\` stores to obj +0x48 (`ssj2_idle` only reads it). A writer of +0x48 by another shape would not show (L for completeness).
- No fallback to the stand frame is needed.

---

## 3. Build v3 (task 3)

### 3.1 Files

| File | SHA-1 | What |
|---|---|---|
| `scripts\one-time\2026-10-24-block\build_mock3.py` | `8184e38f4d3569220ee2b7b42c7b66cab7db9213` | copy of `build_mock.py`; only `OUT` and `BLOCK_ANIM, BLOCK_FRAME = 2, 2` differ (difflib: 2 lines) |
| `scripts\one-time\2026-10-24-block\test_block3.py` | `28ebf33f4d34b210ed80ec732cc554f32bf8b2a7` | v2 tests on v3 plus 7 pose tests |
| `scripts\one-time\2026-10-24-block\diff_proof3.py` | `b64aa578b6e2a31586d5708f737b7d382009ea69` | diff proof writer |
| `scripts\one-time\2026-10-24-block\listing_block3.txt` | `181ccee25692a68d7a85d249a3d292f8d5d6868f` | thumb_dis listing of the v3 code |
| `mockups\log2_poc_r37_block3.gba` | `709063263b999de86b85bd6b56f591ee86f78042` | r37 + block, pose anim 2 frame 2 |
| `mockups\log2_poc_r37_block3.sav` | `159601a376596afbd9d4124845a3b1355b46a839` | byte copy of `log2_poc_r37.sav` |
| `mockups\log2_poc_r37_block3_goku.gba` | `709063263b999de86b85bd6b56f591ee86f78042` | byte copy of v3 |
| `mockups\log2_poc_r37_block3_goku.sav` | `260e4861d110e6de701539575a8902c9c4b8a8c5` | slot 1: Goku on map 7,1 |
| `mockups\diff_proof3.txt` | `041a941b9ecc17ec193b2c3b4a049c56db476f46` | the proof below |
| `pose\pose_render.py` | `a505bb7fa696fe72a1c5dc82aeb080783541ec21` | renders and record list |
| `pose\pose_check.py` | `0db6c3ce0a979eb852879d665f5bb38f42c39483` | per-set check |
| `pose\map_pick.py` | `749d47c9e09c47c7cc0bd31262170b706cd81cd7` | landings on combat maps with enemies |
| `pose\bible_rows.md` | `970c942659883ff455c30a8ed471ba955108e8d8` | bible rows, tag BLP |
| `pose\a2_s60.png` | `ee9ae6400390b98e36e46abccb9ff642b68a7324` | render |
| `pose\a2_s60_x8.png` | `2dc49ace8eef3b22e5db63efc87ca023ec0e6a66` | render |
| `pose\guard_candidates_s60_x12.png` | `fbe9d2d494a9262c34d1e0de54315aaa15543385` | render |
| `pose\a2_s61.png` | `ba9e9b29487a69120866fdcfd58305903670c1c3` | render |
| `pose\a2_s56.png` | `d618b25288af42cf1d0fecca6f942141b6ed0138` | render |
| `pose\a2_s157.png` | `c18d302266ef7e840913c0766dba16c068b1076c` | render |
| `pose\a2_i2_player_sets.png` | `eeb1d05d5fdef194d7d086458116e747c0c71bd7` | render |
| `pose\a2_i2_all_sets.png` | `3a882fd36699ee5a16e7eb7fb60be2df90077b78` | superseded render (section 1.1) |
| `pose\enemy_sets_18_146.png` | `394f0d91314fb477c9684f07f0a03dd59db6b00f` | render |
| `scripts\one-time\2026-10-24-block\__pycache__\build_mock3.cpython-314.pyc` | `bf960ae5132d524f54dc08b6588257322d2f6a3e` | bytecode written by the `build_mock3` import |
| scratchpad `make_test3.py` | `7a44555a017377c8b76e03a5edda18ba855fa8f5` | generator of `test_block3.py` (session temp folder, section 5) |

- v2 is untouched: `log2_poc_r37_block2.gba` and its spar and scouter copies still hash `c5c654fb...`, the v2 saves keep their study hashes, and `build_mock.py`, `test_block.py`, `diff_proof.py` were not edited.
- Every ROM, save and proof file was made by exclusive create (`open(..., "x")`, or `log2_save.py`, which refuses to overwrite).

### 3.2 Diff proof (`mockups\diff_proof3.txt`, C)

Verbatim:

```
r37 3877033c65d724a299a364f66a4c3d75a4df4566
mockup log2_poc_r37_block3.gba 709063263b999de86b85bd6b56f591ee86f78042
built file equals build_mock3.plan applied to r37: True

== v3 against r37 ==
run rom:0x0238ac-0x0238af (4 bytes) 2914feff -> 4931de00  field scene vtable 0x08023884 +0x28 (menu buttons) -> block_menu
run rom:0x025628-0x02562b (4 bytes) 4133feff -> b912de00  player vtable 0x08025604 +0x24 (message handler) -> block_msg
run rom:0x0258e4-0x0258e7 (4 bytes) 5527feff -> 610fde00  state 1 (walk) vtable 0x080258DC +8 (logic tick) -> block_walk
run rom:0x025a8c-0x025a8f (4 bytes) b124feff -> b50dde00  state 0 (idle) vtable 0x08025A84 +8 (logic tick) -> block_idle
run rom:0xe06800-0xe06812 (19 bytes) ffffffffffffffff -> 0468e0086f000000  BLOCK state object word, its 5-word vtable, push table (4 x 8 bytes)
run rom:0xe06814-0xe06816 (3 bytes) ffffff -> bdfc21  BLOCK state object word, its 5-word vtable, push table (4 x 8 bytes)
run rom:0xe06818-0xe06825 (14 bytes) ffffffffffffffff -> 0000000000020000  BLOCK state object word, its 5-word vtable, push table (4 x 8 bytes)
run rom:0xe06828-0xe06829 (2 bytes) ffff -> 00fe  BLOCK state object word, its 5-word vtable, push table (4 x 8 bytes)
run rom:0xe0682c-0xe06a27 (508 bytes) ffffffffffffffff -> 0000000000020000  BLOCK state object word, its 5-word vtable, push table (4 x 8 bytes) + new Thumb code and literal pool (listing_block3.txt)
562 bytes differ in 9 runs; 0 bytes outside a named region (0xFF bytes that the new data happens to keep equal do not count as runs)

== v3 against v2 (log2_poc_r37_block2.gba) ==
v2 c5c654fb070a449f781626b9108f6b4123ebc4e6
byte rom:0xe0687a 00 -> 02  block_enter +8 `mov r2,#BLOCK_FRAME` immediate (0 -> 2: frame index)
byte rom:0xe06880 4c -> 6c  block_enter +14 `add r0,#BLOCK_ROW` immediate (0x4C -> 0x6C: set + 0x4C + 16 x anim 2)
2 bytes differ from v2; 0 outside the two named pose immediates

== saves and copies ==
log2_poc_r37_block3.sav byte copy of r37 .sav: True (159601a376596afbd9d4124845a3b1355b46a839)
log2_poc_r37_block3_goku.gba byte copy of the v3 mockup: True
log2_poc_r37_block3_goku.sav 260e4861d110e6de701539575a8902c9c4b8a8c5: RAM-order bytes that differ from the v3 .sav: 0x10 (slot 1 leader), 0x12 (slot 1 zone), 0x170 (slot 1 position), 0x171 (slot 1 position), 0x172 (slot 1 position), 0x173 (slot 1 position), 0x174 (slot 1 Adler-32), 0x176 (slot 1 Adler-32), 0x177 (slot 1 Adler-32)
  0 bytes outside the named slot 1 fields
aligned words outside the window that hold a window address: []
```

- Byte 0x175 of the Adler-32 is equal by chance.

- The code length (0x1F0) and every label are the same as v2, so the 562 bytes in 9 runs match v2.

### 3.3 Tests (`py -3 -P test_block3.py -v`: 25 OK, C)

- The 18 v2 tests, unchanged, on the v3 bytes.
- The 7 pose tests use literal values, not values read back from `build_mock3`:
  1. `BLOCK_ANIM, BLOCK_FRAME == 2, 2` and the output name.
  2. `block_enter` +8 is `0x2202` (`mov r2,#2`) and +14 is `0x306C` (`add r0,#0x6c`).
  3. On real set 60: enter writes +0x4C = set + 0x6C, +0x14 = 2, +8 = 0x28, +0x12 = 16.
  4. Vanilla hurt enter `0x0800E210` writes the same +0x4C and +8.
  5. Vanilla hurt tick `0x0800E222` gives frame (tick + 1) >> 3, so frame 2 at ticks 16-23.
  6. Vanilla frame select `0x08007A84` picks the anim 2 frame 2 record in each facing; h-flip only on dir 3.
  7. v3 differs from the v2 file in exactly the two pose bytes.
- The base calls in the v2 hit tests are stubs. In-game behavior is L until my test.

---

## 4. Goku test pair (task 4)

### 4.1 Slot 1 (C, `log2_save.py info`)

Verbatim slot 1 lines of `log2_save.py info log2_poc_r37_block3_goku.sav --flags` (the other party lines are left out):

```
slot 1: checksum stored 0x39765a76 calc 0x39765a76 valid; in-use bit 1 -> shown
  leader 4 (Goku)  header flags 0x03  map zone 7 area 1 var 1  pos (208,368)  +8 0x0
  Goku     Lv40 EXP  2727775 HP 1026/1026 EP 139/139 STR 47.33 POW 50.07 END 65.99 flags 0x7f appearance 19 (set 60) tech 3 | HP, EP and stats in range
  story flags set: 155  (191 = Dragon Balls returned: 1, 195 = Cell beaten: 1, 196 = final goodbye: 0)
    0-9,11-20,22-23,26,28-31,33-70,73-100,108-113,117-132,134,136-146,148-158,162-164,171,176,181,185-195
  visited maps 297/297  scouter entries 0/128  items {22: 1, 45: 1}
```

- Flag 76 is set: the range `73-100` holds it. A separate Python check (`log2_save.bit(slot 1, O_STORY, 76)`) also printed 1.

- Made by `log2_save.py set log2_poc_r37_block3.sav log2_poc_r37_block3_goku.sav 1 leader=4 map=7,1,1 pos=208,368`.
- Goku's appearance 19 is set 60 in the live table (C). So the test shows set 60.
- Header flags 0x03: the scouter switch is off, so R does nothing else on this save.

### 4.2 Why map 7,1 (C unless marked)

- **Combat map:** map entry `rom:0x40BA20` +8 = 1. The game copies it to map info `0x03002080` +0xC, the word the block gate reads (RE-BIBLE OVW row).
- **Position from data:** the world-map landing script `0x083FBCEC` is `push 7,1,1,208,368 ; ext 38`. No coordinate was invented.
- **Enemies:** 5 tiger bandits (set 18, enemy type 9, HP 325, AI 45), all with condition 0 (always spawn). They stand at (104,248), (168,200), (208,240), (224,192) and (280,216). The nearest is 128 px straight up from the landing.
- **No scene on load:** no enter, leave or variation script. Region 1 (a walk-in band at y 289-328, script `0x083D37BC`) fires only while flag 76 is clear (condition `0x2004C`). Flag 76 is set in slot 1, so it does not fire.
- The music field is a script that tests flag 76 (L: it only picks music).
- Region 0 is an A-press region over the landing spot (rect 185,329-232,384). Do not press A there.
- `map_pick.py` lists only 5 world-map landings on combat maps with always-spawn enemies. Landings that encode their values another way would not show.

### 4.3 Risks

- **Goku leads a post-Cell slot (L).** The Goku record is in the party (flags 0x7F, Lv40, stats in range). The only vanilla save with Goku as leader is pre-Cell (slot 3).
- **Bandit attack path (L).** The tiger bandit is a melee enemy. I did not trace AI 45 to the punch node (`0x0801BE8A`, enter `0x0801BD2C`) or the dash node. A plain walk of the AI descriptor does not reach them (S: the tree is built another way). The direct-damage path `0x0801DE10` ignores the block. If a front hit while blocking shows a full damage number, note it.
- **Scene depth during play (L).** The gate needs scene depth 0. Nothing on this map starts a scene at load (above).
- Goku at Lv40 kills a bandit fast. Block first, then punch.

### 4.4 My steps (mGBA)

**Test A, the pose with Goku:**

1. Open `builds\mockups\2026-10-24-block\log2_poc_r37_block3_goku.gba`. mGBA loads `log2_poc_r37_block3_goku.sav`.
2. Continue, **slot 1**. **Expect:** Goku stands on map 7,1. Tiger bandits are 120-176 px north of him, maybe off screen. Do not press A on the spot where you start.
3. Hold R while no enemy is near. **Expect:** Goku crouches with both arms crossed in front (the hit frame), and he holds it. The d-pad and A do nothing.
4. Release R. **Expect:** the pose ends at once and Goku stands and walks again.
5. Check each direction: release R, press the direction once, then hold R again. Do this for down, up, left and right. Goku cannot turn while R is held. **Expect:** the pose in every direction. Right is the mirror of left. Up shows his back.
6. Walk up toward the nearest bandit (about 128 px, straight up). Face it, then hold R while it attacks.
7. **Expect** for each blocked hit: a small damage number (about 1/16 of a normal hit, at least 1), a tiny step back (2 px), no hurt slide, and the pose stays.
8. Turn your back to a bandit and let it hit you while you hold R. **Expect:** a normal hit (full number, hurt animation, long slide), and the block ends.
9. Release R and fight normally. **Expect:** walk, A and B as before.

**Pass:** the pose shows while R is held in all four directions, blocked hits give small damage and a short push, the pose ends when R is released, and nothing crashes.

**Also check:**

- Does the pose read as a guard to you? The three small stars above the head in the side views come from the hurt art.
- Gohan's frame 2 is a flinch with hands at the face (`pose\a2_s157.png`). Switch characters only if you want to see it.

**Test B, regression:** open `log2_poc_r37_block3.gba`, load any slot, and check walk, A, B, L, Start and Select as before.

---

## 5. Disclosures

- One Bash command started with `cd /dev/null 2>/dev/null;`. That `cd` failed and changed nothing, but the brief says never `cd`.
- One Bash command started with `cat > /dev/null <<'X'` (an empty heredoc to the null device). It created no file.
- One heredoc attempt to create `test_block3.py` stopped on an assert before it wrote anything, because a shell heredoc changed `\\n`. I then wrote the generator `make_test3.py` with Python in a scratch folder outside the project. It created `test_block3.py` with `open(..., "x")`.
- `enemy_sets_18_146.png` was written by the `rom_sheet.py` command line (`sheet.save`, not an exclusive create). It was a new file.
- `a2_i2_all_sets.png` is my own superseded output (section 1.1). I kept it, and it is not deleted.
- Python wrote `scripts\one-time\2026-10-24-block\__pycache__\build_mock3.cpython-314.pyc` when it imported `build_mock3` (`-P` does not stop bytecode writes).
- `scripts\permanent\` check: the files there that are newer than 7:50 AM are `patches\superperfect_cell.py` (8:08 AM), `tests\test_chamber_spar.py` (8:20 AM), `tests\test_superperfect_cell.py` (8:09 AM) and their `.pyc` files (8:24 AM and 8:34 AM). I did not import or edit these modules, so another session made those changes (L). No `.pyc` of a module I imported is newer than 7:50 AM.
