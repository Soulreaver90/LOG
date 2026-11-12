# Vegeta Z+ : report

Trial ROM `builds\mockups\2026-11-12-vegeta-zplus\log2_zplus_v1.gba`, SHA-1
`48975f27eff63a394773bbb8a1bce9deccaf04dc`. The build seeded its save from **`log2_poc_r40.sav`**, and
`log2_zplus_v1.sav` sits beside the ROM.

Press B as post-Cell Super Vegeta with 10 EP or more and he becomes Z+. Press B again and he drops to base.
The HUD shows a `Z+` icon, the dialog and status pages show your new portrait, and the form carries the
ascended grade stats.

---

## 1. Your four measured entries all matched the ROM

I re-read the live table of the dev master before I wrote anything. Every byte of your table was right.

| Entry | Live bytes `+0..+5` | Reading | Form object |
|---|---|---|---|
| 8 | `00 89 6A 18 0B 0B` | base, `set:137`, portrait 106, `+4` = 11, `+5` = 11 | `@0x030021E0` |
| 9 | `00 8A 6A 18 0A 0A` | base, `set:138`, portrait 106, `+4` = 10, `+5` = 10 | `@0x030021E0` |
| 10 | `01 8B 6B 19 09 09` | super, `set:139`, portrait 107, `+4` = 9, `+5` = 9 | `@0x030021E8` |
| 11 | `01 8C 6B 19 08 08` | super, `set:140`, portrait 107, `+4` = 8, `+5` = 8 | `@0x030021EC` |

CONFIRMED (live table bytes of the dev master, `rom:0x88DC54`). No disagreement to report there.

---

## 2. Three places where the design met something the ROM does differently

### 2.1 Portrait id 121 is NOT free. I used 122 instead. CONFIRMED

This is the one I would most like you to read.

`npc_gi` did not grow the block to 0-121 to leave a spare. It built id 121 **on purpose**: it copies word
59 (the armored Gohan frame) into word 121, then writes `121` into the dialog byte of the two chamber exit
lines `rom:0x3DB930` and `rom:0x3DBABC`. Those lines must stay armored, and the `cutscene_portraits` hook
remaps raw 59 to the gi, so npc_gi gave them an id the hook never touches. Both records still read
`10 00 02 79` and `15 00 02 79` in the dev build, and `79` is 121.

`art\tables\portraits.json` lists only the ids we override, so an id missing from it is not proof that the
id is unused. That is why 121 looked free.

Wiring your portrait to 121 would have put Vegeta's face on armored Gohan in those two chamber exit lines,
**and `art_inject` is in `build_list_core.txt`, so it would have done that to both masters, not only to the
trial.**

What I did instead:

- Your portrait is dialog id **122**, a brand new id.
- `art\tables\portraits.json` is **untouched**, so `art_inject` writes nothing new and both master SHA-1s
  are unchanged. The trial module does the whole portrait job itself.
- The module grows the live block by one word (ids 0-122), copies it, writes your frame into the fixed
  `art_inject` slot `rom:0xF7A3D0`, and repoints the two words that name the block.
- npc_gi's id 121 and its two records are left exactly as they were, and a test proves it.
- The file is now `art\tables\portraits\122_vegeta_grade2.png`. It decodes clean: 30 colors, every one an
  OBJ index, and its outer 3 px frame matches the existing portrait border to the pixel.

**Your decision, not mine:** if you would rather the portrait be id 121 on the normal `portraits.json`
route, say so and I will move npc_gi's armor copy to its own new id in the same pass. That edits a core
module, so it changes both master SHA-1s, which is why I did not do it unasked.

### 2.2 A table edit alone would have put Z+ behind `flag:195` and shown Gohan's Z2 icon. CONFIRMED

`ssj2_form`'s `step_ok` (`@0x0888E306`) reads: transformed, **`+4` differs from `+5`**, `flag:195` set, EP
at least 10. It is the predicate both the ability 12 gate and the HUD hook call.

So the moment entry 11 gets `+4` = 23, three things follow on their own:

1. Vegeta's step would need `flag:195`, which is a gate, and decision 4 says there is none.
2. The HUD would show **Gohan's Z2 icon** on Super Vegeta.
3. Entry 23, whose `+4` = 23 and `+5` = 8, also reads as "has a step", so B would transform it into itself
   instead of reverting. Vegeta would be stuck in Z+ whenever he held 10 EP.

I did not change `ssj2_form`. The trial module puts its own gate and HUD hook in front of his, and each one
tail-calls his for every case it does not own:

- **Entry 23**: straight to the vanilla action `0x0801353D`, which sends message `0x24`, the revert. Your
  `+4` = 23 stays exactly as decision 2 says, and it is now harmless because the wrapper never lets it be
  read as a step.
- **Entry 11 with 10 EP or more**: message `0x23`, the transform. **No story flag.**
- **Everything else**: `ssj2_form`'s gate and HUD hook, unchanged. Gohan's Z2 still works the same way.

The gate and the HUD share one predicate, `zplus_ok`, the way his share `step_ok`, so the icon cannot
disagree with what B does. A test runs all 24 entries against both and proves it.

**The 10 EP cost is my call**, because the brief does not name one. I mirrored `ssj2_form`'s `STEP_EP`, so
Vegeta's step costs what Gohan's costs. Change it with one constant.

**One behavior change worth knowing before you play:** post-Cell Super Vegeta can no longer drop straight
to base while he holds 10 EP. B takes him up to Z+, and the next B takes him to base. That is exactly how
Gohan behaves after Cell, and it is the price of putting the step on the same button. Under 10 EP, B
reverts as it always did.

### 2.3 The live appearance table is named by 22 words, not 17. CONFIRMED

`ssj2_form` repoints 17 base literals. A full ROM scan of the dev build for aligned words equal to the live
table address finds **22**. The other five are literal pool words inside later modules:

| Word | Module |
|---|---|
| `rom:0x88E3B4` | `ssj2_form` (`step_ok`'s own `ldr`) |
| `rom:0x894978` | `status_bonus` (its status page copy, which `status_portrait` also reads through) |
| `rom:0x89A9B4` | `fullpower_ssj` (its re-encoded `appearance_revert`) |
| `rom:0x90A250` | `bf_ki_pool` (`pool_ref`) |
| `rom:0x90A3E0` | `fullpower_hud` |

Each of the five is proved by the `ldr` that reaches it, not by which module's notes it sits nearest:
`@0x0888E30E`, `@0x088948CA`, `@0x0889A910`, `@0x0890A002` and `@0x0890A392`. All 22 are repointed.

The one that would have bitten hardest is `fullpower_ssj`. It owns the re-encoded `appearance_revert`, so a
stale copy there would index past its own table end on **every leader change**, not only on the status
page. The module refuses to run if a 23rd word turns up that no patch allocated and no known literal
covers.

A second search shape, words pointing **inside** the table rather than at its base, finds exactly one,
`rom:0x27D880`. It is byte identical in the base ROM, so it is data that happens to read as a pointer, not
a reader. I did not repoint it.

---

## 3. The icon had to be built from the live HUD. CONFIRMED

`bf_hud` (r39) rewrites every icon image in place into the Buu's Fury layout, `ssj2_form`'s Z2 pair
included: it takes the BF empty icon and pastes the LoG II picture, rows 2-9 columns 13-28, at rows 2-9
columns 3-18. It runs in core, before this module.

So a static `.bin` drawn from the base ROM would have shipped a Z+ icon in the old LoG II frame next to a
HUD in the BF frame. I caught it only because a test compared the art file with the live icon.

`art\gi_art.py zplus` makes the pair the way the approved `z2` command does: the Z moves 2 px left inside
its panel and a 3x3 `+` sits at the bottom right, OBJ index 191 usable and 23 dim, both already in the
palette. The patch then pastes that picture into the **live** ability 12 icon, so the Z+ icon carries
whatever HUD look the build has. It refuses to run if the paste changes nothing.

See `zplus_icons.png` beside this report: the three pairs as the trial ROM holds them, Z, Z2 and Z+.
`zplus_portrait.png` shows your portrait as the ROM holds it, beside Vegeta's id 106.

---

## 4. What the new entry holds

Entry 23 = `01 8B 7A 19 17 08` plus entry 11's `+6..+0xF`, form object `@0x030021E8`.

| Field | Value | Why |
|---|---|---|
| `+0` | `0x01` | transformed, as decision 2 |
| `+1` | 139 | the ascended grade set, as decision 2 |
| `+2` | 122 | your portrait, see 2.1 |
| `+3` | 25 | entry 11's status twin, kept. `status_portrait` reads `+2`, not `+3`, so the status page shows your portrait |
| `+4` | 23 | its own index, as decision 2. Safe only because the new gate owns entry 23 |
| `+5` | 8 | leaving Z+ returns to post-Cell base Vegeta, as decision 2 |
| `+0x10` | `@0x030021E8` | the ascended form object: +15 STR, +10 POW, +15 END, speed 0.75 / 1.75, 1 EP per 40 frames |

A test reads the stats back out of the form object's own `apply` routine, not out of the patch, and gets
15 / 10 / 15.

---

## 5. Things to expect in play, which I did not change

| | Label |
|---|---|
| **No yellow ki row in Z+.** `pool_ref` counts `@0x030021EC` and `ssj2_form`'s own object as pool forms; `@0x030021E8` is not one (bible B2374). Super Vegeta has the yellow row, Z+ will not. Changing it means a new form object, which decision 2 rules out | LIKELY |
| **Ki keeps draining in Z+ during a cutscene.** `scene_drain_pause` wraps the Super Saiyan and Super Saiyan 2 ticks only. Z+ uses the vanilla ascended tick | LIKELY |
| **Z+ looks the same as Z.** Sets 139 and 140 decode to the same tiles in all 64 rows, which you already said is expected and not mine to fix | CONFIRMED, from your brief |
| **A save made while Vegeta is in Z+ needs a build with this module.** The record holds entry 23, and a ROM whose table stops at 22 would read past its end | CONFIRMED |
| **`ext 73 (2, 139)` still means pre-Cell ascended Vegeta, entry 10.** The reverse lookup copy is the unchanged 22 entry one, and it maps `set:139` to entry 10. No script in the build uses it for Vegeta | LIKELY |
| **Trunks is untouched**, as the brief says. His portrait does not exist yet | CONFIRMED |

---

## 6. Files

| File | What |
|---|---|
| `scripts\permanent\patches\vegeta_zplus.py` | the module |
| `scripts\permanent\tests\test_vegeta_zplus.py` | 33 tests |
| `scripts\permanent\build_list_trial_vegeta_zplus.txt` | `include build_list_dev.txt` plus the one module |
| `scripts\permanent\art\gi_art.py` | new `make_zplus_icons` and a `zplus` command, beside the approved `z2` one, which I did not touch |
| `art\hud_zplus_usable.bin`, `hud_zplus_dim.bin`, `hud_zplus.png` | the icon pair and its review sheet |
| `art\tables\portraits\122_vegeta_grade2.png` | your portrait, moved out of `art\portraits\remastered\` |
| `scripts\one-time\2026-11-12-vegeta-zplus\` | the probes and the review sheet builder |
| `docs\tasks\2026-11-12-vegeta-zplus\zplus_icons.png`, `zplus_portrait.png` | the art as the ROM holds it |

`build_list.txt`, `build_list_core.txt`, `build_list_dev.txt` and `art\tables\portraits.json` are all
untouched.

---

## 7. Tests

`py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`, run to a
file and read by its real exit code, never piped.

**1962 tests, 2 failures, exit code 1. Neither failure is reachable from my change set, and neither
is `test_golden`.**

| Failure | Why my change set cannot reach it |
|---|---|
| `test_art_inject.test_a_palette_entry_makes_its_index_usable` | It expects `check_pixels` to refuse an index outside the dialog palette. `art_tables.allowed_indices` now returns the whole OBJ table, with a comment saying so, and `art_tables.py` was last written 2026-11-11, before this task. That file is already modified and uncommitted on `feature/map-editor`. `test_art_inject.py` does not import `gi_art` and does not read `art\portraits\remastered`, the two things I touched |
| `test_battle_start.test_form_survives_the_leader_change` | It builds `build_list_trial_ending.txt`, which does not list this module, and the record it names belongs to `fullpower_ssj`. Both files were last written in October and early November |

`test_golden` PASSED, so the golden and dev master SHA-1s did not move. Your brief expected them to,
because adding a portrait through `portraits.json` would have. Keeping the portrait inside the trial module
is what saved the pins. Nothing needed to be touched there.

**One caveat on this run, which you should know.** A second agent was writing `piccolo_z_start` into the
same tree while the suite ran, so the run is not a clean snapshot. Neither failure comes from that module
or its test: both failing files predate today. I did not re-run, because the tree was still moving. The 33
tests of this task were also run on their own, green, before and after the trial build.

`piccolo_z_start` wraps ability 11, not ability 12, and writes neither `rom:0x1D99CC` nor `rom:0x8E8C`, so
the two trials do not collide. If you ever put both on one list, this module must run last, because it
relocates the appearance table.

The 33 new tests cover, beyond the four you asked for:

- entry 11 steps with `flag:195` **clear**, which is the proof there is no gate
- entry 23 gives the revert for every flag and EP combination
- the Z+ icon shows in entry 23 and in entry 11 while B steps, and **never** Gohan's Z2 for entries 8-11
- Gohan's entries 5 and 22 behave exactly as before, with his Z2 icon
- the icon never disagrees with B, swept over all 24 entries, two flag states and five EP values
- all 22 words name the new table and none names the old one
- the block grew by one id and npc_gi's id 121 and its two records are unchanged
- each icon is the live Z icon with the Z+ picture, pixel by pixel
- both hooks moved from `ssj2_form`'s own routines, and the base 8 MB differs only at the known sites
- the gate and the HUD keep `r4`-`r7`, `sp` and `lr`
- the module fails closed on four junked sites, refuses to run out of order and refuses to run twice
- a stray namer of the table raises instead of being repointed blindly

---

## 7a. Four more checks, because a wrapper only covers the doors it closes

| Check | Shapes I used | Result |
|---|---|---|
| **Does anything else call `ssj2_form`'s `step_ok`, `gate` or `hud` and so bypass my wrapper?** | (a) a full ROM scan for aligned words equal to each address; (b) a grep of every `patches\*.py` outside `ssj2_form.py` for those three notes keys | `step_ok` is named by NO aligned word, `gate` only by `rom:0x1D99CC` and `hud` only by `rom:0x8E8C`, which are exactly the two words I took over. No other module reads those notes. CONFIRMED. A module that reached `step_ok` by a `bl` from its own code would not show in shape (a), and shape (b) is what covers that |
| **Does the status page index a per-entry table that stops at 23?** | read `status_bonus`'s `stats` routine whole | It reads the LIVE player bytes `+0x160` to `+0x162`, and the record, never a per-entry table. Entry 23 is safe. CONFIRMED |
| **Does any tool enumerate `art\tables\portraits\` and trip over a PNG that is not in `portraits.json`?** | grep every permanent script for a glob, `iterdir` or `listdir` of that folder, and read `art\tables\README.md` | Nothing enumerates it. `inject.py` and `art_tables` go through `portraits.json` only, and my file is not in it. CONFIRMED. One stale line to know about: that README still says "Valid ids are 26-121", which is `art_tables.MAX_ID`. `inject.py portrait 122 ...` would refuse until `MAX_ID` moves, which is part of the id 121 decision in 2.1, not something I changed on my own |
| **Is the ROM on disk the one the tests checked?** | re-assembled the trial list in memory after the other agent's edits and compared SHA-1 | `48975f27eff63a394773bbb8a1bce9deccaf04dc` both ways. MATCH |

`test_golden` was also run on its own, verbose: 14 tests, OK, `test_golden_builds_to_its_pinned_sha1` and
`test_dev_builds_to_its_pinned_sha1` among them. The master pins are shown to hold, not inferred.

Both red tests were re-run alone and failed on the same assertions, so they are deterministic and not an
artifact of the other agent's edits.

I also re-ran `scripts\permanent\make_tool_index.py`, so `docs\tool-index.md` now lists `vegeta_zplus.py`.
It also picked up the other agent's `piccolo_z_start.py` and the three new one-time folders, because those
were already on disk.

---

## 7b. What is proved by code, and what still needs your eye

Everything above is proved by reading bytes and by running the new code in the Thumb interpreter. **Nothing
is play-tested.** The step itself is new ground: Gohan's Super Saiyan 2 keeps the Super Saiyan enter and
leave methods, while Vegeta steps from the pool form `@0x030021EC` to the ascended form `@0x030021E8`
through state `0x23`. That the engine does this cleanly is LIKELY, not CONFIRMED.

Four things to try in mGBA, in this order:

1. Post-Cell Super Vegeta with 10 EP or more: B gives Z+, the `Z+` icon and your portrait.
2. In Z+: B returns him to base Vegeta.
3. In Z+: let the ki run out, and check he drops to base on his own.
4. Gohan: base to Super Saiyan to Super Saiyan 2 and back, unchanged, with the Z2 icon.
---

## 8. What I would ask you next

1. Portrait id: keep 122, or free 121 for it and give npc_gi's armor copy a new id? See 2.1.
2. The 10 EP step cost: same as Gohan's, or something else?
3. The unlock: Z+ is open as soon as Super Vegeta is. Tell me the gate you want and it is one predicate.

---

# CRASH REPORT: the Z+ step. Root cause found, fix needs one decision from you.

`log2_zplus_v1.gba` crashes on the step into Z+. **The wrapper code is not at fault. Vegeta's Super
Saiyan sprite set has no power-up animation, and the engine indexes that animation table with no
existence test.** CONFIRMED, with the bytes below.

## The proving bytes

The record lookup `@0x0800775A` (bible B0041) computes the animation row as
`set + 12 + 16 * dirs + anim * dirs * 4`, then takes `row[direction]`. It never asks whether the
animation exists. The power-up animation is 9.

Anim 9 row, read out of the crashing ROM, all four directions:

| Set | Role | anims | anim 9 row | anim 21 row |
|---|---|---|---|---|
| 137 | Vegeta base | 21 | `0838D944` x4 | past the table |
| **140** | **Vegeta Super Saiyan** | 22 | **`00000000` x4** | `0839D2C4` x4 |
| 139 | Vegeta ascended, the Z+ set | 22 | `00000000` x4 | `0839D2C4` x4 |
| 59 | Gohan armor Super Saiyan | 22 | `082B2110` x4 | `082B6998` x4 |
| 158 | Gohan gi Super Saiyan | 22 | `0883F878` x4 | `0883FDA0` x4 |
| 159 | Gohan gi Super Saiyan 2 | 22 | `08869724` x4 | `08869C4C` x4 |
| 133 | Trunks Super Saiyan | 22 | `00000000` x4 | `08373B00` x4 |
| 61 | Goku Super Saiyan | 22 | `00000000` x4 | `082CEDA4` x4 |

So the engine reads a **null record list**, follows it, and PC lands on data. That is the
`E55EC002` shape you identified.

## Why Gohan works and Vegeta does not

Every vanilla BASE set has anim 9 and no anim 21. Every vanilla SUPER set has anim 21 and no anim 9,
**with exactly one exception: set 59, Gohan's armored Super Saiyan, which has both.** `gohan_gi`
carried that property into sets 158 and 159, and `test_ssj2.test_entry22_set_is_gi_ssj2_with_anims_9_and_21`
pins it to this day.

That is why `ssj2_form` could chain Gohan entry 5 into entry 22 at all. **A Super Saiyan to Super
Saiyan step is only possible on a set that carries the power-up animation, and Gohan's line is the
only one in the game that does.** I missed that prerequisite. It is written in `ssj2_form`'s test, not
in its module, and I read the module.

The animation runs on the OLD body, because `transform` `@0x08014D58` swaps the set at its END:
`@0x08014D9C ldrb r0,[r0,#0x1] ; @0x08014D9E bl 0x8009324 ; @0x08014DA2 str r0,[r4,#0x48]`. So the step
from entry 11 asks **set 140** for anim 9, and set 140's row is null.

## Your four questions, answered against the built ROM

| Question | Answer |
|---|---|
| 1. Trace the `0x23` branch in the built ROM | `@0x0893BDF2 ldr r2,[r1,#0]` to `@0x0893BDFC bx r3`, exactly `ssj2_form`'s own send. `lr` was restored at `@0x0893BDEA pop {r3}` / `@0x0893BDEC mov lr,r3` BEFORE the branch. `r3` is `[player][0x28] + [player]`, a vtable entry, so the mode bit comes from the engine's own word. NOT the fault |
| 2. Can any path fall into the literal pool or the next function? | No. Every exit of `gate` is a `bx` or a `pop {..,pc}`, and all three paths pop the one pushed `lr`: `@0x0893BDEA`, `@0x0893BDFE` and the `gate_chain` path, which falls through the same pop. `hud` ends `pop {r4,r5,r6,pc}` on both exits. The last instruction before the pool is `stub_r1: bx r1`. NOT the fault |
| 3. Does entry 23 exist in the built table? | Yes. Live table `rom:0x93B5F8`, entry 23 = `01 8B 7A 19 17 08 06 00 18 00 00 00 00 01 00 00 E8 21 00 03`, form object `@0x030021E8`, which your state dump shows holds vtable `0x0802526C`. The 20 bytes after entry 23 are my portrait block's struct word `0x03000E90`, not garbage. NOT the fault |
| 4. Is sending `0x23` from the pool form `@0x030021EC` valid? | Yes. The message reaches `transform`, which runs. The crash is downstream of it, in the animation the transform STATE plays on the old body. My LIKELY hedge was on the wrong step: the message is fine, the animation is not |

## What my tests actually executed, and what they never reached

You asked me to say this plainly.

- **Executed** in the Thumb interpreter: both wrappers end to end, for all 24 entries, both flag states
  and five EP values, including the Gohan entry 5 and 22 chains into `ssj2_form`'s gate and HUD. Those
  paths are genuinely covered, which is why hypothesis 2 was dead.
- **Never reached:** anything after the gate sends the message. The interpreter stops at a sentinel the
  moment `0x23` or `0x24` is sent. So `transform`, the state that plays the power-up, the set swap and
  the form enter were **never executed by any test**. A green suite said nothing about them.
- The gap has a shape, not just a name: **no test asserted a prerequisite of the step on the set it
  steps FROM.** `test_ssj2` has exactly that test for Gohan. I did not mirror it for Vegeta.

## The fix, which needs your decision, so I built no v2

The step needs a live anim 9 row on **set 140**, Vegeta's Super Saiyan set. Three ways:

| Option | What you would see | Cost |
|---|---|---|
| **A. Borrow base Vegeta's power-up.** Point set 140's anim 9 row at set 137's list | Vegeta's power-up plays with his BASE body for 4 frames, so black hair flickers in, then Z+ | One word per direction in my module. Geometry already matches: both sets are slot `0x400` and the lists are 4 frames of 32x32 at dx -8 dy -24. Ten minutes, fully reversible |
| **B. Draw a Super Saiyan power-up for Vegeta.** New anim 9 frames on a rebuilt set 140 | Correct: he powers up in his Super Saiyan body | Your art. 4 frames x 4 directions, 32x32, same geometry as the table above |
| **C. No animation.** Change the gate to set the appearance directly, the way `ext 73` does on the leader (B2169), instead of sending `0x23` | Z+ appears instantly, no power-up at all | Code only, in my module. It also changes how Z+ FEELS, so it is a design change, not a repair |

I did not pick, because A and B are art and C changes a user-facing feature.

**The same defect is waiting for Trunks and Goku.** Sets 133 and 61 both have a null anim 9 row. Any Z+
for Trunks needs the same answer, so whichever option you choose, choose it for the family.

`log2_zplus_v1.gba`, its `.sav` and its `.ss2` are untouched.

---

# v2: the crash fix. Option A, and nothing else.

`builds\mockups\2026-11-12-vegeta-zplus\log2_zplus_v2.gba`, SHA-1
`1c7e5e59193024d354a6e63df8a5a41dc76a5f77`, save `log2_zplus_v2.sav` seeded from `log2_poc_r40.sav`.

`log2_zplus_v1.gba`, its save and both save states are untouched.

## What changed, proved by the diff

v2 differs from v1 in exactly 16 bytes, at `rom:0x39D3D0`, which is set 140's anim 9 row:

```
v1:  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
v2:  44 D9 38 08 44 D9 38 08 44 D9 38 08 44 D9 38 08
```

`0x0838D944` is set 137's power up list, base Vegeta's. One word per direction, as planned.

That 16 byte diff is also the proof that nothing else moved, the gate predicate included.

## The form slot 1 bit is out

I had already written it into `zplus_ok` when your correction arrived. It is removed, and the diff
above is the evidence: if any instruction had changed, the code and its literal pool would differ too,
and they do not. `zplus_ok` is byte for byte what v1 shipped: appearance entry 11, then EP of 10 or more.
No ROM FILE was ever written with the bit test in it. A test run may have assembled it in memory, and
I did not check that; the 16 byte diff is what proves the file is clean.

Your correction was right on both counts. The second one is the deeper fact: the transform sits in
slot 2 for all five characters, so its bit is 5, and the four slot cycler leaves no room for a fifth
slot. Z and Z+ cannot be two ability slots. It is in the bible rows, so nobody re-derives it.

## The borrow is a named, reusable helper

In `patches\vegeta_zplus.py`, importable the way `status_portrait` imports `ssj2_form`'s assembler:

| Function | Does |
|---|---|
| `set_at(rom, set_id)` | the set header, through THIS ROM's own relocated set table |
| `anim_row(rom, set_id, anim)` | returns the row offset and the four direction words; raises when the row is past the table |
| `plan_anim_borrow(rom, into_set, from_set, anim)` | every check, no write, so `apply` runs it before the first write |
| `borrow_anim_row(rom, into_set, from_set, anim)` | the plan, then the 16 byte write |

It fails closed on four things: the target row must be empty, the source row must be whole in all four
directions, the two sets must share one OBJ slot, and the borrowed frames must match the geometry the
target already draws. Each guard has its own test. Two of them run on a mutated copy of the ROM,
because the nine sets I measured (60, 61, 103, 104, 132, 133, 137, 139 and 140) are all slot `0x400`
with 32x32 records at dx -8 dy -24, so no real pair of sets can trip those two guards. A playable set
I did not measure could still trip them, which is the guard doing its job.

That last measurement is good news for the family: Trunks `borrow_anim_row(rom, 133, 132)`, Goku
`(61, 60)` and Piccolo `(104, 103)` are all geometrically legal today. Only Vegeta is wired here, as
you asked. A test asserts the other three rows are still null and byte identical to v1.

## The test you asked for

`assert_step_set_can_power_up(case, rom, from_set, anim=9)` in `tests\test_vegeta_zplus.py`. It asserts
a live four direction row on the set the step comes FROM, and that each record has a real size and a
real frame header. A future module calls it with its own set pair. The Vegeta test also asserts the row
was null in v1, so this test would have caught the crash.

## One residual risk I did not fix, because you scoped it out

**Closed in v3**, which the section at the end of this report covers. The text below is what v2
shipped with, kept as the record.

Set 139, the Z+ set itself, still has a null anim 9 row. My gate makes entry 23 always revert, so B
can never ask for it. But a SCRIPT transform (`ext 57` state 35, as `vegeta_19_reveal` and
`vegeta_ssj_scene` use) sent while Vegeta stands in Z+ would ask set 139 for anim 9 and crash the same
way. Those scenes are pre Cell and Cell Games, so he would have to be in Z+ when one runs, which the
story does not do today. One more line, `borrow_anim_row(rom, 139, 137)`, closes it. Say the word.

### Set 139 holds every other row a playable set needs, so the play test can pass

Nobody has ever stood in Z+, because v1 crashed before the form was entered. Every row of set 139 is
therefore unplayed, and a second null row would crash the same way on his first action. I enumerated
all 22 rows of each set in the BUILT v2 ROM. The null rows are:

| Set | Null animation rows |
|---|---|
| 137 Vegeta base, 21 rows | 10, 15, 19 |
| 140 Vegeta Super, in v2 | 10, 14, 15, 17, 19 |
| 139 Vegeta Z+ | 9, 10, 14, 15, 17, 19 |
| 158 Gohan Super | 10, 14, 15, 17, 19 |
| 159 Gohan Super 2 | 10, 14, 15, 17, 19 |

Sets 158 and 159 show a live anim 9 here because `gohan_gi` gave it to them, which is the point the
section above makes. Set 139 is missing exactly one row that set 140 has, and that row is anim 9. Otherwise it matches both
of Gohan's working super sets row for row, and its anim 21 is LIVE, so B in Z+ reverts.
`scripts\one-time\2026-11-12-vegeta-zplus\probe_sets139.py` prints this.

## Tests run, and what is outstanding

I ran `test_vegeta_zplus.py` only, by name: 39 tests, OK, exit code 0. Six of them are new, all about
the borrow.

The full suite is outstanding and I did not run it, because another agent is editing the tree. The two
known failures before this change were `test_art_inject.test_a_palette_entry_makes_its_index_usable`
and `test_battle_start.test_form_survives_the_leader_change`. Both are deterministic, and neither is
reachable from my change set.

## The build log line, for you to append

I did not touch `docs\build-log.md`. The build ran with its log redirected into
`scripts\one-time\2026-11-12-vegeta-zplus\build-log-line.md` by `build_v2.py`, which says why in its
header. The line is:

```
- 2026-11-12 16:09 build log2_zplus_v2.gba patches=gohan_gi,ssj2_form,gohan_portraits,status_bonus,ssj2_idle,cutscene_portraits,npc_gi,rage_text,art_inject,status_portrait,rage_stats,cellgames_ssj,scene_drain_pause,fullpower_ssj,piccolo_gi_scene,superperfect_cell,chamber_spar,bf_hud,bf_ki_pool,relay_cooldown,fullpower_hud,beam_struggle,vegeta_ssj_scene,chapter_cards,vegeta_19_reveal,celljr_fight,vegeta_zplus sha1=1c7e5e59193024d354a6e63df8a5a41dc76a5f77
```

## For his next play test

The v1 save state should still load on v2: the 16 changed bytes are data, no code moved and no RAM
layout changed. That is LIKELY, not proved. If it misbehaves, the paired `log2_zplus_v2.sav` is a
clean start.

mGBA finds a save state by ROM filename, so the slot 2 key on `log2_zplus_v2.gba` looks for
`log2_zplus_v2.ss2`, which does not exist. Use File, then Load State File, and pick
`log2_zplus_v1.ss2`. That state is his own crash reproduction, so the retest is one press of B.

1. Super Vegeta with 10 EP or more, press B. He should power up and become Z+, with the `Z+` icon.
2. Watch the power up. Those four frames are BASE Vegeta's body, so expect black hair to flash in mid
   animation. That is option A working as chosen, not a new defect.
3. B again in Z+ returns him to base Vegeta.
4. Gohan's Super Saiyan and Super Saiyan 2 should be unchanged.

---

# v3: set 139's own power up, so the residual is closed

`builds\mockups\2026-11-12-vegeta-zplus\log2_zplus_v3.gba`, SHA-1
`018daf9ef75ec91bd55343bb5f9ab60cfb1895e1`, save `log2_zplus_v3.sav` seeded from `log2_poc_r40.sav`.
v1, v2, their saves and both save states are untouched.

## The diff from v2 is one row, and it is the right one

v3 differs from v2 in exactly 16 bytes, at `rom:0x3B4820`, which is set 139's anim 9 row:

```
v2:  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
v3:  44 D9 38 08 44 D9 38 08 44 D9 38 08 44 D9 38 08
```

One run, 16 bytes, and `anim_row(v3, 139, 9)` resolves to that offset, so the changed bytes ARE that
row and nothing else. Read back through `read_set`: sets 137, 139 and 140 now all hold
`0x0838D944` in all four directions, all slot `0x400`, all 32x32 at dx -8 dy -24. Sets 133, 61 and
104 are still null, so Trunks, Goku and Piccolo are untouched.
`scripts\one-time\2026-11-12-vegeta-zplus\verify_v3.py` prints all of it.

## What changed in the module

One constant and one loop. `BORROWERS = (VEG_SSJ_SET, ZPLUS_SET)`, the plan runs for both before the
first write, and step 4 is a comprehension over the same tuple. The notes key `anim_row` became
`anim_rows`, a list of two, and every test that read it follows. No other behaviour moved:
`zplus_ok`, the appearance entries, the chain and the portrait are exactly as v2 shipped.

## Tests

`test_vegeta_zplus.py` by name: 40 tests, OK, exit code 0. The new one is
`test_the_zplus_set_itself_can_power_up`, which runs the same
`assert_step_set_can_power_up` helper against set 139 in the built ROM, and asserts the row was null
before the patch. `test_both_borrowed_rows_are_base_vegetas_own_list`,
`test_the_animation_rows_are_the_only_extra_base_rom_sites` and
`test_the_base_8mb_differs_only_at_the_known_sites` now cover both rows, so a third write would fail
the suite. The full suite is yours; I did not run it.

One test had to move its ground. `test_the_helper_refuses_a_borrow_that_would_not_work` used set 139
as its legal control, and 139 now holds its row, so the control would read "nothing to borrow". It
now runs every guard on Trunks' pair, 133 from 132, which this module leaves alone and which is a
legal borrow today. That makes the guard test prove the helper is reusable, which is what it was
for.

## The build log line, for you to append

```
- 2026-11-12 16:26 build log2_zplus_v3.gba patches=gohan_gi,ssj2_form,gohan_portraits,status_bonus,ssj2_idle,cutscene_portraits,npc_gi,rage_text,art_inject,status_portrait,rage_stats,cellgames_ssj,scene_drain_pause,fullpower_ssj,piccolo_gi_scene,superperfect_cell,chamber_spar,bf_hud,bf_ki_pool,relay_cooldown,fullpower_hud,beam_struggle,vegeta_ssj_scene,chapter_cards,vegeta_19_reveal,celljr_fight,vegeta_zplus sha1=018daf9ef75ec91bd55343bb5f9ab60cfb1895e1
```

## Play test, unchanged from v2 apart from the file name

Load `log2_zplus_v1.ss2` through File, then Load State File, because mGBA looks a state up by ROM
file name. Super Vegeta with 10 EP or more, press B: power up, Z+, the `Z+` icon. B again reverts.
Gohan's two steps are unchanged. Expect base Vegeta's black hair in the power up frames, in Z+ as
well as out of Super Vegeta, because both sets borrow the same list.
