# Cell Jr hitboxes: study report

Date: 2026-10-25. Brief: `docs\tasks\2026-10-25-celljr-hitbox\celljr-hitbox-study.md`. Study only: no patch, no build, no build-list change, `docs\RE-BIBLE.md` not edited.

| SHIPPED | Where |
|---|---|
| How a melee hit and a ki blast are tested, with addresses | "The hit test" |
| Jr numbers next to Gohan, the relay players, Android 17/18 and the tiger bandit | "Numbers" and `hitbox_study.txt` |
| Renders of the boxes on the sprites | `scripts\one-time\2026-10-25-celljr-hitbox\*.png` |
| Vanilla or ours, checked on base, r39 and trial v3 bytes | "Vanilla or ours" |
| Fix options with bytes, scope and risk, and a recommendation | "Fix options" |
| Bible rows, tag `CJH` | `scripts\one-time\2026-10-25-celljr-hitbox\bible_rows.md` |

| PENDING | Why |
|---|---|
| Which far hits are blasts and which are punches, in play | Needs states from the 4-Jr fight ("Emulator steps") |
| Enemy knockback direction and the no-hit window in frames | Same |
| Gohan's set during the fight, read at run time | Script bytes say `set:160`; a state would prove it |
| Gohan's B-button abilities (states 44-51: charged ball, beams) | Not measured. Only the punch, the hold special and the state 34 ki blast were measured |
| The AI 45 row 48 move (leaf `0x0801CCA9`, state object `0x0300226C`, vtable `0x080247FC`) | Not traced; it matters only for option 1b with AI 45 |

Housekeeping: test suite run once, `Ran 805 tests ... OK` (`scripts\one-time\2026-10-25-celljr-hitbox\suite.txt`). To run it from the root, the PowerShell call used `Push-Location` (a directory change inside that one call); no other call changed directory.

---

## Short answer

- The "big reach" is not in the melee box. The Jr punch reaches **less** far than Gohan's punch in every direction (C, model of the listed code; table "Numbers").
- "They hit far" is very likely the **AI 21 ki blast**: a 16 x 16 shot that flies to the screen edge, fired by all 4 Jrs (C for the shot's size and range; L my far hits are shots, until emulator step 2).
- "Hard to hit" has two vanilla causes. The Jr's hurtbox is only 28 px tall, adults 33-36 (C, header bytes). Every hit knocks the Jr back about 36-59 px, and it takes no hit until the knockback ends (C for the no-hit flag, L for the 32-frame length).
- All of this data is vanilla (C, byte compare). The trial adds the count, 4 at once (C), and Gohan's `set:160` box, which is 3-4 px wider than `set:159` (C).

---

## The hit test

All boxes are rectangles in map pixels from the actor anchor (x, y) = +0x158/+0x15C >> 8 (`@0x0800791A`). The anchor is the top-left of a 16 x 8 footprint at the feet.

| Part | Where it comes from | Label |
|---|---|---|
| **Hurtbox** (where a hit must land) | Per set and per facing, fixed: set header +0xC + 16 x facing, four s32 `(x0, y0, x1, y1)`. `@0x080079B8`: `ldrb r3,[r1,#0x10] ; ldr r0,[r1,#0x48] ; lsl r3,#4 ; add r0,r3 ; add r0,#0xc`. Not per frame, not per anim. Uses the current set (+0x48), so a transform changes it | C |
| **Footprint** | Set bytes +3, +4 copied to +0x154/+0x155 at build (`@0x080078F8`); `@0x0800793A` gives anchor .. anchor + (w, h). 16 x 8 for every set here | C |
| **Test** | Strict overlap: `hit.x0 < box.x1`, `box.x0 < hit.x1`, `hit.y0 < box.y1`, `box.y0 < hit.y1`. Player handler `@0x08008A36`-`@0x08008A52`, enemy handler `@0x0800E678`-`@0x0800E696` | C |
| **Gohan's punch** | Fixed per facing, from the anchor: table `rom:0x3B5144` (button_a `@0x08007E6A`-`@0x08007E7A`). Down (0,0,16,16), up (0,-24,16,0), left (-8,-24,0,8), right (16,-24,24,8). It is tested once, on the button press (`@0x08007E36`). Hold special: `rom:0x3B5208`, same except up (0,-16,16,0) | C |
| **Enemy punch** | `@0x0801BD2C` (leaf `0x0801BE8B`, shared by AI 8, 21 and 45). It picks the facing from the two hurtbox centres, then builds the rect from its **own** hurtbox E and footprint F: right `(Ecx, Ecy, E.x1+3, E.y1+3)`, left `(E.x0-4, Ecy, Ecx, E.y1+3)`, down `(F.x0, E.y0, F.x1, E.y1-6)`, up `(F.x0, E.y0, F.x1, F.y0)`. One msg 0 on the enter frame, so like Gohan it lands before the swing shows | C |
| **Punch guard** | Node `0x0801C05B` runs the punch only while `@0x0801BEB8` is true, and `@0x0801BEB8` builds the same rect and tests it on Gohan. A Jr never swings at air | C (code), L (node meaning) |
| **Ki blast** | One object for both sides: `@0x0800E8B0` via `@0x0800EAD8`, whose only callers are Gohan's state 34 (`@0x08014DF4`) and the AI 21 blast state (`@0x0801BC18`). 16 x 16 box centred on its point (`rom:0x40E47C`: dx 8, dy 8, w 16, h 16), 3 px a frame (`rom:0x40E554`), tested every frame, gone off screen (`@0x08013C22`) or on a closed map cell (`@0x0800E9C0`). Spawn point `@0x08007A26`: the hurtbox edge, at centre height | C |

> [!NOTE]
> r39 wraps Gohan's state 34 tick (vtable word `rom:0x25D4C` = `0x0890A23B`, the ki pool stub). The stub loads `0x08014DF5` as its target, so the same projectile code runs (L).

---

## Numbers

Full listing: `scripts\one-time\2026-10-25-celljr-hitbox\hitbox_study.txt`. Reach = the largest gap between the two 16 x 8 footprints on one line that still lands, both actors facing each other (the Jr turns first: leaf `0x0801C0D7`, `@0x0800DF98`). Label: C (model of the listed code); in-game feel is L.

| Actor | Hurtbox (per facing, from the anchor) | Size |
|---|---|---|
| **Cell Jr `set:31`** | (-1,-18,16,10) (0,-18,17,10) (-1,-18,18,10) (-2,-18,17,10) | 17-19 x **28** |
| Gohan Rage gi `set:160` (trial) | (-4,-26,19,10) (-4,-26,19,10) (-3,-26,21,10) (-5,-26,19,10) | 23-24 x 36 |
| Gohan SSJ2 gi `set:159` | (-2,-26,18,10) all | 20 x 36 |
| Piccolo `set:103` (relay) | (-2,-26,18,10) x2, (-3,-26,25,10), (-9,-26,19,10) | 20-28 x 36 |
| Vegeta `set:137`, `set:140` (relay) | (-2,-26,18,10) all | 20 x 36 |
| Trunks `set:129` / `set:130` (relay) | (-2,-23,18,10) / (-1..-2,-26,17..18,10) | 19-20 x 33-36 |
| Android 17 `set:9`, Android 18 `set:11` (AI 21) | (-2,-25,18,10) all | 20 x 35 |
| Tiger bandit `set:18` (AI 45) | (-2,-23,18,10) all | 20 x 33 |

The Jr's anim 0 pixels span y -15..+7, so its hurtbox is larger than its sprite, not smaller (C, opaque bounds in `hitbox_study.txt`). It is short because the sprite is short (C).

| Pair (enemy on player / player on enemy) | Right | Left | Down | Up | Spots only the enemy lands |
|---|---|---|---|---|---|
| **Jr vs Gohan `set:160` (trial)** | 6 / 8 | 7 / 8 | 21 / 25 | 19 / 25 | 150 (12 with no Gohan facing that lands) |
| Jr vs Gohan `set:159` | 5 / 8 | 6 / 8 | 21 / 25 | 19 / 25 | 90 |
| Jr vs Piccolo `set:103` (vanilla relay) | 6 / 8 | 7 / 8 | 21 / 25 | 19 / 25 | 90 |
| Jr vs Vegeta `set:140` (vanilla relay) | 5 / 8 | 6 / 8 | 21 / 25 | 19 / 25 | 90 |
| Jr vs Trunks `set:129` (vanilla relay) | 5 / 8 | 6 / 8 | 19 / 25 | 19 / 25 | 68 |
| Android 17 vs Gohan `set:160` | 7 / 9 | 8 / 9 | 21 / 25 | 26 / 32 | 79 |
| Tiger bandit vs Gohan `set:160` | 7 / 9 | 8 / 9 | 21 / 25 | 24 / 30 | 79 |

| Ki blast (shot along x) | Lateral band that meets the target | Range |
|---|---|---|
| Jr shot on Gohan `set:160` | Gohan's anchor from 21 px above to 29 px below the Jr's (51 rows) | To the screen edge |
| Gohan shot on a Jr | Jr's anchor from 25 above to 17 below (43 rows) | To the screen edge |

**When a Jr shoots (AI 21 tree, C from node bytes).** Farther than 88 px from Gohan (footprint centres) it uses row 22. Between 72 and 120 px it lines up on one axis (`0x0801B15F`) and then has a 5 % roll (`0x086D23D8`, p `0xCCC`) to enter the blast state (`0x03002224`, anim 5, shot at tick 16 of 32). Within 88 px it closes in and punches (rows 24-28) (C). With 4 Jrs spread around, some are usually in the 72-120 px ring (S, not measured).

**After Gohan lands a hit (C code, L duration).** The knockback node `{0x0801ACB7, .., 0x30}` sets enemy +0x168 = 0 at enter (`@0x0801AC00`), so `enemy_message` ignores every hit until the leave (`@0x0801ACAC`, +0x168 = 1) (C). It moves the Jr ((0x60 + rand 0x40) x 0x30 >> 7) = 36-59 px over the hurt state, 32 frames per the BLP row (L). Gohan's side punch reaches 8 px past his footprint, so he cannot chain hits and must walk in again (L, from the numbers). This is the same for every enemy whose hit list runs row 18, among them AI 8 and 21 (C, tree walk).

### Renders

All in `scripts\one-time\2026-10-25-celljr-hitbox\`, 3-4x zoom, lime background. Green = hurtbox, blue = footprint, red = enemy punch rect, orange = Gohan's punch rect, magenta = ki blast box.

| File | Shows |
|---|---|
| `boxes_by_facing.png` | Every actor, 4 facings: hurtbox, footprint, punch rect |
| `reach_jr_vs_gohan160.png` | Map of where Gohan's anchor can stand: red only the Jr lands, blue only Gohan, purple both |
| `reach_jr_vs_piccolo103.png`, `reach_jr_vs_vegeta140.png` | Same for the vanilla relay fights |
| `reach_android17_vs_gohan160.png`, `reach_tiger_vs_gohan160.png` | Same for two ordinary enemies |
| `duel_row_jr_max.png`, `duel_row_gohan_max.png` | Both actors on one row at the Jr's and at Gohan's farthest punch |
| `duel_jr_only_far.png` | Gohan at (-23, 26): the farthest spot where only the Jr lands. The Jr turns by position (down), then `@0x0801BD2C` picks a side punch from the box centres |
| `kiblast_jr.png` | The Jr's shot every 8 frames, meeting Gohan 200 px away at three heights |

---

## Vanilla or ours

| Item | Base vs r39 vs trial v3 | Verdict | Label |
|---|---|---|---|
| Type 26 entry `rom:0x6D591C` (HP 4990, AI 21, 46/50/46) | Equal | Vanilla | C |
| `set:31` header and boxes `rom:0x246D80` | Equal | Vanilla | C |
| AI table `rom:0x6D5194`, nodes `rom:0x6D2000`-`0x6D27FF`, leaves `rom:0x6FF3A0`-`0x6FF4DF` | Equal | Vanilla | C |
| Punch and hold tables `rom:0x3B5144`, `rom:0x3B5208`; blast tables `rom:0x40E47C`, `rom:0x40E554`; move table | Equal | Vanilla | C |
| Hit code: `@0x080079B8`, `@0x0800793A`, `@0x08007A26`, button_a, player and enemy msg, `@0x0800E8B0`-`@0x0800EB20`, `@0x08013BC0`-`@0x08013C7E`, `@0x0801BD2C`, `@0x0801BBC8`-`@0x0801BC7C`, AI dispatch | No r39 code run touches them (44 runs listed by `diffc`) | Vanilla | C |
| Gohan's set in the fight | r39 Cell script `rom:0x3EA365` = `00 00 00 A0` then ext 73 (`push 0 ; push 160`); record X has no ext 73 | Ours: `set:160` | C (bytes), L (no later set change in play) |
| `set:160` hurtbox | Header +2..+0x4B equals base `set:58` (vanilla Rage) | Vanilla data, but vanilla Rage Gohan never fights a Jr. It is 3-4 px wider than `set:159` and raises the Jr-only spots from 90 to 150 and the side reach by 1 px | C |
| 4 Jrs at once, the NPC-to-enemy swap, items 13-16 | Trial records and items only (CJT, CJ2, CJ3 diff proofs) | Ours: 4 shooters and 4 punchers at once | C |

---

## Fix options (not built)

> [!WARNING]
> The punch code, the blast object and the AI 21 tree are shared by every AI 21 enemy (types 3, 4, 26, 29, 41, 106: Androids 17 and 18, the Jrs and three others). The type 26 entry is shared by the vanilla relay Jrs (items 8-10). Only a new type for items 13-16 isolates the trial.

| # | Option | Bytes | Changes vanilla relay Jrs? | Risk |
|---|---|---|---|---|
| 1 | **Trial-only type and AI.** Copy type 26 (24 bytes) and AI rows 21-28 with their nodes to the expansion. Lower the blast roll (`p` at copy of `rom:0x6D23E4`, 0xCCC to e.g. 0x333) or cut row 22's 120 px ring. Point the copied type's +8 at the new row id and the 4 type words at the new type id | `rom:0x90A56C`, `0x90A59C`, `0x90A5CC`, `0x90A5FC` (u32 26); new type entry and node copy in the expansion. Ids are u32 with no bound (`@0x0800E780`, `@0x0801AA98`), so no table moves | No | Medium: every self-reference in the copied nodes (behaviour ids 21-28, the goto 18 node) must be re-pointed. The scouter matches by type, so the trial Jrs show no scouter entry unless one is added |
| 1b | **Trial-only type with a melee-only AI.** One new 24-byte type entry in the expansion (copy of type 26, address with (addr - `0x086D56AC`) a multiple of 24) whose +8 names AI 8 or AI 45, and the 4 type words point at it. No node copy | The same 4 type words; one type entry | No | Low. AI 8 and AI 45 reach the punch leaf and no blast leaf (C, tree walk). `set:31` holds anim rows 0, 1, 2, 5, 6, 7, 8, a superset of `set:18` (AI 45: 0, 1, 2, 6, 7, 8) and `set:44` (AI 8: 0, 1, 2, 6, 7) (C, row pointers). AI 8 is passive (guarded 10 % punch, else a 0xB3 mover) (C). AI 45 adds a row 48 move that was not traced (S). The Jrs no longer shoot at all; no scouter entry |
| 2 | Lower the blast roll in vanilla AI 21 | `rom:0x6D23E4` (u32 `0x00000CCC`) | Yes, and Androids 17, 18 and 3 others | Low code risk, global balance change |
| 3 | Taller Jr hurtbox, e.g. y0 -18 to -24 | `set:31` header `rom:0x246D90`, `0x246DA0`, `0x246DB0`, `0x246DC0` (s32 y0 of each facing) | Yes (set shared) | Low code risk, but the Jr's own punch rect grows with it (its centre moves up) |
| 4 | Smaller enemy punch rect | Code `@0x0801BD2C` (the `+3`, `-4`, `-6` immediates) | Yes, every AI 8, 21, 45 enemy | High value for nothing: the Jr already reaches less than Gohan |
| 5 | Shorter knockback or no no-hit window | Row 16 param `rom:0x6D2138` (0x30) or `@0x0801AC00` | Yes, every row 18 enemy | Changes the feel of every fight |
| 6 | Fewer Jrs at once (2 + 2 waves) | Trial records only | No | Low; changes the planned scene |

**Recommendation:** first run the emulator steps below to prove the far hits are blasts. If they are, I pick between two trial-only fixes that leave the relay fights and the Androids vanilla:
- **Option 1b** (recommended): the smallest change, 4 type words and one type entry. The Jrs fight with punches only. Use AI 45 for an active brawler after its row 48 move is traced, or AI 8 for a passive one.
- **Option 1**: the Jrs still shoot, less often. Use it if I want Jrs that keep the blast. Leave the melee boxes alone; by the numbers Gohan already outreaches the Jr. If I also wants the Jrs easier to hit, add a taller hurtbox to the same trial-only work only if a cloned set is acceptable (a new set id needs the set table moved, SPC row), else accept the vanilla 28 px box.

---

## Emulator steps

Use `builds\mockups\2026-10-24-celljr\log2_poc_r39_celljr_v3.gba` with its `.sav`, slot 3, and play into Gohan's 4-Jr fight.

1. **Gohan's set.** In any fight state, read `[0x03001FA8]` (player) +0x48. Expected `0x0888D870` (`set:160`); `0x08869C7C` would be `set:159`.
2. **Blast or punch.** Take a state each time Gohan is hit from more than 24 px. List world list 1 (`state_actors_v3.py`): a projectile is an object with vtable `0x08024CBC`. A Jr in the blast state has actor +0x18 = `0x03002224`. Expected: most far hits are blasts.
3. **Knockback and the no-hit window.** Take a state on the frame Gohan's punch lands, then one per frame for 40 frames. For the Jr hit, log +0x158/+0x15C (8.8), +0x10 (facing), +0x168. Expected: +0x168 = 0 for about 32 frames, about 36-59 px of travel, away from Gohan (S until seen).
4. **Blast rate.** Over 60 s, count frames where any Jr has +0x18 = `0x03002224`. Compare with one Android 17 fight if a save reaches it.
