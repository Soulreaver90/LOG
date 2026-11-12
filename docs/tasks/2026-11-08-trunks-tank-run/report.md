# Report: the Trunks tank run (anim 13), and the armour-review cleanups

Date: 2026-11-08. Every claim is labelled CONFIRMED, MEASURED, LIKELY or SPECULATIVE.

---

## 1. What I did

| Ask | State |
|---|---|
| Say what state `run_anim13.png` is in | Done. Section 3 |
| Build the run, anim 13, base and Super Saiyan | **The FRONT row is built, pass one: 8 drawings.** The back and side rows are not. Sections 4 and 5 |
| Remove the cyan baldric across all 32 frames | **Done in part, and I deviated.** 48 of the 110 pixels are strap and are gone. 62 read as BELT and stay. Section 2 is the evidence, and section 11 is the question |
| The 44 scabbard reveal pixels | Done, and the review's count was wrong. Section 6 |
| The 18 leftover jacket pixels | **Done, all 18.** Section 7 |
| Finding A, the sword in the Super Saiyan back head | **Done for the back idle, 20 px.** Section 8 |
| Finding E, the Super Saiyan hair tip | **Done, 3 frames.** Section 8 |
| Findings D, F, G, H | D and F left on purpose, G has nothing to apply, H applied. Section 8 |
| Run `sprite_guard.py` with `--body-from` | Done. Section 9. 0 violations over 32 frames |

> [!IMPORTANT]
> **Nothing is live.** Every frame I changed is in `art\trunks_tank\proposed\2026-11-08\`. The 32 live
> PNGs and `manifest.json` are byte identical to how I found them. Section 10 says why, and what
> promotion needs.

---

## 2. The baldric: 48 pixels are strap, 62 read as belt

Your ruling was "remove the cyan baldric pixels, palette 47 and 4D, across all 32 frames", and you
said the chest should open by about 9 px in each front frame. I opened 3, and I need you to settle
why before the rest goes.

**Index `4D` is the strap AND the belt's highlight. Index `47` is the strap AND the belt's shadow.**
The sprite guide's own rule covers this: a palette index is a colour, never a role.

**Sheet: `art\trunks_tank\proposed\2026-11-08\sheets\07a_belt_question_front.png`.** Four panels, rows
15 to 23: the vanilla jacket frame, the live tank frame, my staged frame, and set 129 in armour.

Three measurements say the waist pixels are belt.

1. **The motif repeats and it moves with the hips.** The front view draws `4D 21 4D` on the belt's top
   row and `25 4D 02 4D 27` on the buckle row, in the idle and in all four front walk frames. The pair
   sits at rows 19 and 21 in the idle, and at rows 20 and 22 in walk 0 and walk 2. It is one rigid unit
   and it tracks the hips. MEASURED over 5 frames, read by eye.
2. **The armour draws its own belt at the same coordinates.** Sets 129 and 130 wear a belt and no strap
   of any kind. At the front idle's (9,20), (7,21) and (9,21), which are three of the disputed pixels,
   set 129 draws its belt olive `28` and `29` over grey. Panel 4 of the sheet. MEASURED.
3. **You drew the belt there yourself.** `art\trunks_tank\trail\owner_side_v1.png` and
   `owner_side_v2.png` both put `25`, the belt's yellow, at (7,20) of the side idle. A later pass
   overwrote it with `4D`, and `rebuild_side.py` records the reason in its own POST dict:
   "(7, 20): (0x4D, baldric continuity, to match walks 0, 1 and 2)". CONFIRMED, from our own trail.

A fourth thing turned up while I was fixing the last jacket pixel, and it is the strongest of the four.
The belt's cool pixel at (5,20) of the side idle is `4D` in set 134 and `4E` in set 128. **The palette
holds no cool tone near the belt that is not the strap index or the jacket.** So a belt with no `4D`
cannot be drawn without redesigning it.

So the strap I removed is the diagonal above the waist, and nothing else:

| Frames | Strap pixels removed | What each becomes |
|---|---|---|
| 6 front frames with the full strap, plus `ssj_front` | (4,16), (4,17), (5,18) | mid skin, lit skin, black tank |
| `base_front_walk_0`, `ssj_front_walk_0` | (5,18), (6,19) | lit skin, black tank |
| `base_front_walk_2`, `ssj_front_walk_2` | (5,17), (5,18) | black tank, black tank |
| 8 side frames with the idle geometry | (5,19), (7,20) | black tank, your own belt yellow `25` |
| `base_side_walk_0`, `ssj_side_walk_0` | (7,20) | belt yellow `25` |
| `base_side_walk_2`, `ssj_side_walk_2` | (5,19), (7,20) | black tank, black tank |
| **Total** | **48 in the manifest, 51 with `ssj_front`** | |

Counted back out of the staged PNGs: strap-index pixels **110 before, 70 after**. The 70 is 62 belt
pixels plus the 8 at (5,20) that section 7 converts from jacket to set 134's own `4D`. MEASURED.

### A real defect this turned up, and it is the guide's own trap

> [!WARNING]
> **The earlier pass revealed (7,20) in the side idle by copying a screen coordinate from side walk 2,
> and the two frames do not share a grid.** The buckle `25` sits at (6,20) in the idle and at (8,21) in
> walk 2, so walk 2 is one row lower. In the idle's body space, walk 2's (7,20) is row **19**, not 20.
> So the pixel that proved the strap passes through sits on the idle's chest row, and the reveal put it
> on the idle's BELT row. LIKELY, from one landmark, the buckle. The sprite guide names this exact
> failure under "Once you know the offsets, CONVERT to body coordinates".

---

## 3. What state `run_anim13.png` was in

**It was a reference sheet of VANILLA frames and nothing else. No tank art for the run existed.**
CONFIRMED by reading it. It shows 12 rows: sets 128, 134, 129 and 130, for dirs 0, 1 and 2, 4 frames
each, all straight out of the ROM. It was made for the armour review, and that review's section 10
says plainly that it covered anims 0 and 1 only.

---

## 4. The run: the front row is built, the other two are not

### 4.1 What the run actually is. CONFIRMED

Anim 13 dir 2 and dir 3 are **32x32 at dx = -8**, in all four sets. Dirs 0 and 1 are 16x32 at dx = 0,
like everything the tank work has touched. Dir 3 reuses the dir 2 header with the h-flip bit, so anim
13 is **12 drawings per form, 24 in all**, and the jacket over those 24 is **1045 pixels**. The whole
existing tank job, all 32 idle and walk frames, holds less than half of that.

### 4.2 The head does not end at row 15 in the run, and that is good news. CONFIRMED

The run leans forward and the head tips down, so the face sits low. The head's last row is **18** in
d0 i0 and d0 i2, **16** in d0 i1 and d0 i3, and **17** in d2 i0 and d2 i2.

Split head from body at the usual row 16 and set 128 and set 134 appear to differ by 15 px in d0 i0 and
17 px in d0 i2. Nearly all of that is the face and the EYES: **the Super Saiyan iris is `31` and `32`,
two greens, where the base iris is `4F` and `51`, which are also the jacket.** Split at the frame's own
head row instead and the two sets are **byte identical below it in every front key**, so the one-body
rule costs **zero pixels** in the front run. My build prints that check and it reads 0 for all four.

### 4.3 Set 130 is a much weaker reference in the run than in anim 0. MEASURED

| Key | Head rows 0-14 agreement, 134 against 130 | Best row shift |
|---|---|---|
| a13 d0 i0, i2 | 76.7%, 77.1% | 0 |
| a13 d0 i1, i3 | 95.0%, 95.0% | 0 |
| a13 d1 i0, i2 | 27.5%, 27.1% | **+2 rows lifts them to 67.5% and 69.2%** |
| a13 d1 i1, i3 | 45.8%, 43.3% | **+1 row lifts them to 76.7% and 82.1%** |
| a13 d2 i0 to i3 | 83.1% to 88.5% | 0 |

The armour review measured 100% in the side idle and 96.7% in the front idle, on anim 0 only. That
verdict does not carry into the run, and the back run needs a per-frame row shift before set 130 can
be read at all.

### 4.4 Why only the front row

- **The back run (d1) is blocked on Finding B.** Open `art\trunks_tank\edit-kit\RUN_base_d1.png`. The
  sword and the scabbard cover the whole upper back in all four frames. The brief put the bulk sword
  and scabbard removal out of scope. Until it runs, a back run frame has nowhere to put the torso.
  The base form's back head is also unanswered: set 129 wears a different hairstyle.
- **The side run (d2) is the view that failed four times before**, on a canvas nobody has drawn on, and
  it is the view where a sleeveless top lives or dies. I would rather you judged the front row first
  and told me whether the method reads, than hand you 24 frames at once.

---

## 5. The front run, pass one

`art\trunks_tank\proposed\2026-11-08\run\`, 8 PNGs. Built by
`art\trunks_tank\hand-fixes\2026-11-08_run_front_pass1.py`, which holds every call with its reason.

**Sheets, and please look at the first two head to foot before anything else:**

| Sheet | What it shows |
|---|---|
| `sheets\03_run_front_base.png` | vanilla then mine, all four base frames, whole figure, plus 3x and game size |
| `sheets\04_run_front_ssj.png` | the same for the Super Saiyan form |
| `sheets\05_run_front_both_1x.png` | all 8 frames together at 12x, 3x and game size |

What I read in each frame before touching a pixel, which is the part worth checking:

| Frame | Both hands, already bare in vanilla | The jacket |
|---|---|---|
| i0 | x0-x1 rows 16-18, and x4-x7 rows 21-24 | a thin diagonal x1 to x6 rows 15-21, which is an arm, and a mass x7-x14 rows 18-24 which is the shoulder above and the coat skirt below |
| i1 | x0-x3 rows 18-20, and x10-x13 rows 20-23 | the sleeve lies along rows 16-17 either side of the head |
| i2 | x8-x11 rows 21-24 | the mass x3-x8 rows 20-24 is the coat skirt |
| i3 | both forearms are already bare: x2-x5 rows 19-21 and x12-x15 rows 18-20 | the smallest mask of the four, 34 px |

Per frame: **the silhouette shrinks by 10, 10, 13 and 14 px**, against your own front idle's 10. Every
call landed on a jacket pixel in both vanilla frames, and the eye is never touched.

### Two things in it that are mine, and that you should veto if they are wrong

1. **The coat skirt.** In i0 and i2 the jacket flares out over the hip. I filled it with trouser grey
   where a leg is below it, and cut it where it flared into open air, which is the guide's rule. That
   is 9 cut pixels in i0 and 10 in i2, and it is the biggest silhouette change in the row.
2. **A black pixel where the arm passes the face.** With the jacket gone the bare arm touches the
   cheek or the jaw, and skin against skin merges into one blob. I put one black tank pixel at each
   contact: (1,16), (2,17), (4,18) and (5,19) in i0, and the matching pixel in the other three. The
   first render without them read as a tan smear at game size, so they earned their place, but the
   exact pixel is a judgement.

I could not tell **which** arm is which in i0. The swap does not need it, because both readings make
that band an arm, but the shading direction does.

---

## 6. Finding C: the review's 44 was two numbers short

I re-derived the reveals by comparing each frame against its own vanilla record, rather than trusting
the review's table.

| Class | Pixels carrying that index that vanilla does not | The review said |
|---|---|---|
| Scabbard orange `21 22 23 25 27` | **46** | 44 "scabbard reveal pixels" |
| Sword grey `09` to `0F` | **42** | not counted at all |
| Strap blue `47 4D` | **44** | "a net 40" |

MEASURED, in `scripts\one-time\2026-11-08-trunks-tank-run\reveals.txt`. The review's own Finding C
table sums to 36, not to the 44 it states, so the table and its total already disagreed.

**Not all 42 greys are sword.** Read by eye: 6 are sword metal at (12,22), 26 are the 3 px crossguard,
and 10 are hip and trouser fill that happens to share the sword's grey ramp. Only the 6 are reveals.

So I removed **40 orange and 6 grey inside the 32 manifest frames**, 46 in all:

| Frames | Reveal pixels removed | Becomes |
|---|---|---|
| 6 front frames, plus `ssj_front` | (11,21), (12,21) scabbard, (12,22) sword metal | cut to clear, which restores the vanilla hip width |
| 8 side frames, idle geometry | (11,20), (11,21) scabbard behind the hip | cut to clear; vanilla starts the scabbard at row 22 |
| `base_side_walk_2`, `ssj_side_walk_2` | (11,20), (11,21) | dark skin, which joins the far arm back to the body |
| `base_back_walk_0`, `ssj_back_walk_0` | (9,14) scabbard in the collar gap, plus (8,21), (9,21), (10,21) scabbard painted over vanilla's trouser grey | the form's own hair, then vanilla's `0F` |

Counted back out of the staged PNGs: orange 922 before, 892 after. The drop is 30 and not 40, because
10 of the strap fills are themselves the belt's orange `25`. Grey is unchanged at 1592, because the 6
removed are matched by the 6 restored at (8,21), (9,21) and (10,21). MEASURED.

---

## 7. Finding I: all 18 removed, and the two halves needed different fills

The review labels this LIKELY. Both pixels hold `4E`, the jacket ramp's top step, and **no reading of
the frame keeps a jacket index**, so both go. The fills are not the same, and that is the whole reason
the guide says to work frame by frame.

- **(4,17), in 10 side frames.** In vanilla its neighbours at x3, x6 and x7 are all jacket `51`, so it
  is a jacket highlight inside the jacket mass. CONFIRMED by the vanilla neighbourhood. In 8 frames
  row 16 at x4 is already clear, so it **cuts**. In `side_walk_2` row 16 at x4 is **skin**, so it
  fills with skin instead.
- **(5,20), in 8 side frames.** It sits inside your own belt motif, `09 4E 25` at x4, x5 and x6 of row
  20, so a cut would punch a hole in the belt. It becomes **`4D`, which is what set 134 draws there**.
  That is the belt's cool tone, and it is also the strap index, which is section 11's question.

Counted back out: `4E` 18 before, 0 after. The whole jacket ramp is 48 before and 30 after. MEASURED.

---

## 8. The other findings

| Finding | Action | Detail |
|---|---|---|
| **A**, the sword in the Super Saiyan back head | **Applied to the back idle: 20 px** | 11 lifted from set 130, 6 of them hair and 5 the nape, and 9 cut because the hilt stands outside the armour's whole silhouette. I left (10,15), where set 130 draws bodysuit, which is not a lift. I left row 16, which is a body row and would force the base frames. I left the 4 back WALK frames until anim 1 dir 1 is measured the way section 4.3 measured anim 13. Sheet: `sheets\06_findingA_back.png` |
| **B**, the bulk scabbard and sword | **Not applied, out of scope** | **The run and the walk will disagree until it runs:** the front run I built carries no sword, and the walk still does |
| **D**, the 3 px crossguard | **Left on purpose** | Two of the three are yours: your 11 px edit of 2026-11-01 cleared (1,15), moved the guard right and widened it to `0D 0B 0D` at x2 to x4. The third, (2,16), came from my own BODY grid in `rebuild.py`, which already drew a 2 px guard at (1,15) and (2,15). Removing the guard while the sword stays leaves a worse hilt |
| **E**, the Super Saiyan hair tip | **Applied, 3 frames, 2 px each** | Set 130 hangs gold hair `14` at (4,15) and (12,15), either side of the jaw, where set 134's collar covers it. CONFIRMED from both index grids. **This overwrites one pixel of your crossguard, in the Super Saiyan frames only.** Your guard keeps (2,15) and (3,15), and every base frame keeps all three |
| **F**, the front shoulder | **Left** | The review labels it LIKELY and the brief says to leave LIKELY |
| **G**, the side arm | **Nothing to apply** | The review states it as a confirmed negative |
| **H**, the magenta key | **Applied** | Every staged PNG is written with `transparency=0`, so the kit opens the same way every time. Index 0 and the palette are unchanged, so no build is affected |

---

## 9. The checks

Full text: `scripts\one-time\2026-11-08-trunks-tank-run\guard.txt` and `verify.txt`.

```
===== pass 1: live frame against staged frame, gear as the garment =====
-- trunks_tank_base_front.png
   garment mask: 71 px | changed: 6 px | outside the garment: 0 px
-- trunks_tank_base_side.png
   garment mask: 61 px | changed: 5 px | outside the garment: 0 px
...
pass 1 violations over the 32 manifest frames: 0
```

The command behind each line, with `--body-from 15` as the guide's outfit-swap rule asks:

```
py -3.14 -I scripts\permanent\rom\sprite_guard.py check <live.png> <staged.png>
    --garment 47,4D,21,22,23,25,27,09,0A,0B,0C,0D,0E,0F,4E --body-from 15
    --allow <each declared coordinate>
```

27 coordinates are declared with `--allow`, in two groups. The guard protects any 1 to 4 px island of
a garment index as head reuse, because `4F` and `51` are also the iris, and a lone strap or jacket
pixel on the chest is such an island. Findings A and E both work in head rows 10 to 15, which
`--body-from 15` keeps out of the mask on purpose. Every allowed coordinate is a hand call with a
reason in its script.

Three more checks, in `verify.txt`:

- **One body: 0 differing pixels in rows 16 to 31**, over every paired pose. The edits are symmetric by
  construction, so this check was free to fail and did not.
- **Distance from vanilla outside the jacket mask: 92 before, 116 after.** Every frame that rose is
  named. `ssj_back` rises by 20, which is Finding A taking the sword out, and 8 side frames rise by 1
  or 2, which are the vanilla strap pixels your ruling removes. No other frame rose.
- **Silhouette**, live against staged, per frame.

The run build prints its own two checks: every call landed on a jacket pixel in both vanilla frames,
and the two forms agree on 0 body pixels below each frame's own head row.

---

## 10. Promotion is blocked on a test, and I was told not to edit a test

`scripts\permanent\tests\test_trunks_tank.py` pins the live frames. Two tests stand in the way, and
neither is wrong: they are doing their job.

| Test | What it pins | Why the staged frames fail it |
|---|---|---|
| `test_every_super_saiyan_pixel_comes_from_vanilla_134_or_the_base_tank_png` | every Super Saiyan pixel is vanilla 134's, the base tank PNG's, or a COLLAR_FILL of the base PNG's | Findings A and E take pixels from set 130, a third source. It also asserts 16x32 and splits head from body at 16 times 16, so a 32x32 side run row would fail it twice |
| `test_the_manifest_covers_the_frames_the_briefs_name` | the exact 32 view and pose tuples, and the counts 32, 37 and 53 | a run row in the manifest fails all three counts |

Two other agents were building the ROM while I worked, so writing the live frames would have reddened
their suite mid-flight. That is why everything is staged.
`art\trunks_tank\proposed\2026-11-08\README.md` has the promotion steps.

---

## 11. The one question

**Does the BELT keep its `4D` and `47` pixels?**

You said the strap goes and the chest should open by about 9 px in each front frame. I opened 3,
because the other 6 are the belt and its buckle wearing the strap's two palette indices. Section 2
gives four measurements, and
`art\trunks_tank\proposed\2026-11-08\sheets\07a_belt_question_front.png` shows it in four panels.

The reason I did not just do as you said: the palette has no cool tone near the belt that is not the
strap index or the jacket, so a belt without `4D` has to be redrawn in warm tones, not just recoloured.
The edit kit's own README also treats rows 19 to 21 at x6 to x10 as belt.

- **If the belt keeps them**, the staged frames are finished as they stand.
- **If every `47` and `4D` must go**, say so and I will redraw the belt in the orange ramp. That is 70
  pixels over 32 frames and a new look for the buckle, so it is a design decision, not a cleanup.

Next after that, in the order I would take them: Finding B across all 32 frames, then the back and side
run rows, then the 4 Super Saiyan back walk frames of Finding A.

---

## 12. Files

| Path | What it is |
|---|---|
| `art\trunks_tank\proposed\2026-11-08\` | 33 staged PNGs, a README, the run folder and the sheets |
| `art\trunks_tank\proposed\2026-11-08\run\` | the 8 front run frames, pass one |
| `...\sheets\01_whole_front_base.png`, `02_whole_side_base.png` | whole figure, live beside staged |
| `...\sheets\03_run_front_base.png`, `04_run_front_ssj.png`, `05_run_front_both_1x.png` | the run, every frame, both forms, at 12x, 3x and game size |
| `...\sheets\06_findingA_back.png` | Finding A: live, staged, and set 130 |
| `...\sheets\07a_belt_question_front.png`, `07b_belt_question_side.png` | the question in section 11 |
| `...\sheets\cmp_*.png` | 12 frames, each as vanilla, live, staged, whole figure plus 3x and game size |
| `art\trunks_tank\hand-fixes\2026-11-08_drop_strap_and_reveals.py` | the strap and the gear reveals |
| `art\trunks_tank\hand-fixes\2026-11-08_armour_head_fixes.py` | Findings A and E, and the last jacket pixel |
| `art\trunks_tank\hand-fixes\2026-11-08_run_front_pass1.py` | the front run |
| `art\trunks_tank\edit-kit\RUN_base_d0.png`, `RUN_base_d1.png`, `RUN_base_d2.png` | the vanilla base run, indices shown |
| `art\trunks_tank\edit-kit\RUN_ssj_d0_vs_armour.png` and d1, d2 | set 134's run beside set 130's |
| `scripts\one-time\2026-11-08-trunks-tank-run\facts.py`, `.txt` | anim 13 records, and the gear in all 32 frames |
| `...\a13_trust.py`, `.txt` | the set 130 trust re-measure, the one-body cost, the gear per run frame |
| `...\a13_job.py`, `.txt` | the 1045 px job size, the row shift test, the head row per frame |
| `...\reveals.py`, `.txt` | every gear pixel we added over vanilla, by class |
| `...\mask.py` | a frame's jacket mask, row by row, with each run's neighbours |
| `...\grid.py` | a frame's indices as text, with a ruler |
| `...\dump.py` | write any vanilla record to a PNG on the tank palette |
| `...\guard_all.py`, `guard.txt` | the sprite_guard runs |
| `...\verify.py`, `.txt` | one body, distance from vanilla, silhouette |

---

## 13. One measurement bug of my own, recorded because it nearly shipped

My first `facts.py` read a PNG with `img.tobytes()` and treated the result as TILE order. A PNG is
RASTER order and a ROM frame is tile order. **The counts came out right and every coordinate was
wrong**, which is the worst kind of failure, because the counts matched the review and looked like
confirmation. The scattered coordinates are what gave it away. Every script in this task now converts
the ROM frame to raster first, and `grid.py` exists so a coordinate is read from text and never from a
picture.
