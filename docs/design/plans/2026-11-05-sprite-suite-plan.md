# Sprite suite, slice 1: the gold master and the down run

> Work through this plan one task at a time. Steps use checkbox (`- [ ]`) syntax for tracking.

Author: Joseph Gonzalez.

**Goal:** One command takes `(set, anim, dir)` and returns outfit swap frames, a GIF and a short report,
with the pose read forced and every check from `docs\sprite-guide.md` run, so a bad frame never reaches
the owner.

**Architecture:** The suite is assembled from the tools in `scripts\permanent\rom\`, not written fresh.
A new `regions.py` library owns the hand lettered region map, which stays the primary instrument. A new
`project.py` carries an already lettered frame's naming onto a new frame, but only outside the garment
mask, because that is the only place it was measured to be trustworthy. A new `checks.py` holds one
function per named past failure, each returning MINOR or MAJOR. A new `sprite_pass.py` drives the step
list and refuses to go on when a gate fails. A project skill makes the harness load the method.

**Tech Stack:** Python 3.14 with Pillow (`py -3.14 -P`), stdlib `unittest`, the existing
`scripts\permanent\rom\` tools, mGBA 0.10.5 for the owner's eye.

**Spec:** `docs\design\2026-11-05-sprite-suite-design.md`. Method: `docs\sprite-guide.md`. The down run's
known answer: `docs\tasks\2026-11-05-trunks-run\pose.md` and `regions.txt`. Measurements behind this
plan: `scripts\one-time\2026-11-05-sprite-suite-plan\probe_*.py`.

---

## Global Constraints

- Base ROM `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`, SHA-1
  `18e0715dec419f3501c301511530d2edcd590f8b`. **Never write anything under `data\`.** Never overwrite a
  ROM, a save or a state: check absence, then create exclusively.
- Python is `py -3.14 -P` everywhere. `py -3` is 3.15 and has no Pillow.
- **Absolute paths only.** Never `cd`, `Set-Location` or `Push-Location`. Agents share the working folder.
- **Never put a Windows path inside a `python -c` argument, a bash heredoc, `printf`, `echo -e` or sed
  replacement text.** Each runs its own escape pass, and `\t`, `\r` and `\2` have corrupted files here
  four times. Write a `.py` file and run it, or build paths from forward slashes.
- **Never pipe a test or script run into `tail` or `head`.** The pipe reports the pipe's exit code. A red
  1152 test suite once read as green that way.
- Suite: `py -3.14 -P -m unittest discover -s C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\tests -t C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent`
  All tests pass before a task is done.
- **No colour rule may name a body part.** Four automatic body finders were tried and all four failed,
  because the artist reuses palette ramps. A task that tries a fifth is a rejected task. Geometry rules
  and region map lookups are allowed; index, hue and ramp rules are not.
- Art rules bind the suite: Buu's Fury art may be ported, other modders' art never, and the Z Hack is
  clean-room inspiration only. Nothing from `zhack\` reaches `art\`, a module or a build.
- **No task in this plan ends in a ROM.** Finished art goes on the approved queue. Two builds are
  pre-approved: one when the initial walking animation is done, one when all animations are done. Any
  other build is the owner's call at the time.
- **A harness hook is a change to `settings.json` and needs the owner's explicit approval before it is
  built.** Task 8 therefore delivers a skill and a drafted hook, never a written hook.
- No git steps. LOG git is on hold. `docs\build-log.md` and `docs\ledger\progress.md` replace commits.
- Every new tool carries a header block like the existing scripts, and
  `py -3.14 -P C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\make_tool_index.py`
  re-runs in the same task.
- No em dash, no en dash, in any file. No byte order mark.
- Every claim is labelled CONFIRMED, LIKELY or SPECULATIVE. Code builds only on CONFIRMED claims.
- Files go where `README.md` says: tools in `scripts\permanent\`, probes in
  `scripts\one-time\<date>-<task>\`, briefs and reports in `docs\tasks\<date>-<task>\`, SQL nowhere.

---

## What the measurements changed, before any task

Nine probes ran before this plan was written, all under
`scripts\one-time\2026-11-05-sprite-suite-plan\`. Every number below came from one of them, on set 128,
measured over 7 frame pairs of one character. Three results change the design.

| Measured | Result | What it changes |
|---|---|---|
| Projecting a region naming by best translation, blind | 47% to 78% of lit pixels get the right role | Blind projection is unusable. CONFIRMED |
| Same projection, accepted only where the palette index also matches | 96% to 100% role right, on 25% to 82% of the frame | The index gate is the mechanism. CONFIRMED |
| The same gate, **inside the garment mask** | accepts 12% to 53%, and 11% to 22% of those are **wrong** | The projection fails exactly where a swap decides. CONFIRMED |
| The **gold master** as the projection source | accepts 26% to 33% of a run frame | The gold master is the **worst** source. CONFIRMED |
| The **nearest already lettered frame** as the source | accepts 70% to 76% | Project from the neighbour, not the master. CONFIRMED |
| Hand lettering bill per down run frame | 58 to 68 pixels of 303 to 341 lit | The eye bill is about 20% of a frame. CONFIRMED |
| Every tool run on a 32x32 frame | `sprite_look`, both `sprite_guard` modes, `sprite_stats` and `sprite_loop` all pass | The tool fix for 32 wide is one file, not a rewrite. CONFIRMED |
| `show_regions.py` at 32 wide | `W, H = 16, 32` at source line 29, and `ljust(W)[:W]` truncates every row to 16 characters with no error | It misreads a wide map silently, which is worse than failing. CONFIRMED by reading the source, not by a run. **FIXED 2026-11-06, outside this plan: the size now comes from the frame. See the note under Task 1.** |
| Set 128's records by size | 114 at 16x32 and **174 at 32x32**, so 60% | The design said "half the work". It is more. CONFIRMED |
| `dx` on the wide records | mostly -8, but anim 18 dir 2 is **-16** and dir 3 is **0**, sharing one header | The design's "32x32, dx -8" is not a constant. `dx` comes from the manifest per record. CONFIRMED |

> [!NOTE]
> The projection rates come from 7 pairs of one character in one outfit. They are CONFIRMED for Trunks
> and the tank, and **LIKELY** for any other character. Task 2's tests pin the measured values, so a new
> character that scores differently shows up as a failing test rather than as a surprise.

> [!IMPORTANT]
> **The design's affordability claim is half right, and this plan takes the half that measured true.**
> Section 3b says "letter the gold master once, project it onto the rest". Projection carries the
> structure (hair, face, trousers, boots) at 96% to 100%, which removes the slow half of the read. It
> does **not** carry the garment, and its mistakes there are the Failure A error itself: index `0x51`
> called torso where the truth is arm, which is the down run's second rejected draft exactly. So the
> garment mask and the bare hands stay hand lettered in every frame, and the gold master becomes the
> **feature reference for Failure B**, not the region source.

---

## Review Focus

Five input classes the spec implies and no task's main test exercises. Each line names the task that owns
its test.

1. **A frame with no already lettered neighbour.** The first frame of a new direction has nothing to
   project from. The pass must letter it by hand and say so, never project from an unrelated pose.
   Owned by Task 2 (`test_no_source_means_no_projection`).
2. **A projected letter that is confidently wrong inside the garment.** Measured at 11% to 22% of
   accepted garment pixels. The projector must refuse the garment mask outright. Owned by Task 2
   (`test_garment_mask_is_never_projected`).
3. **A limb run that crosses the body centre.** The read-only pass separates a chest from a limb by the
   centre column, which the down run's crossing forearm breaks. A check with a region map must use the
   map, and only the mapless pass may use the proxy. Owned by Task 5
   (`test_highlight_check_uses_the_region_map_when_there_is_one`).
4. **Two byte-identical frames in one row.** `sprite_loop.py` raises `EOFError` on them at any width,
   because Pillow drops the duplicate and the decode check seeks past the end. Dir 3 reuses dir 2's
   header, so this is reachable. Owned by Task 6 (`test_gif_survives_repeated_frames`).
   **CLOSED 2026-11-06, outside this plan.** Our frame index maps to the GIF's own index, so every
   frame is still compared. Four held-pose shapes are pinned in `tests\test_sprite_loop.py`.
   Task 6 keeps the row, because the plan's own test name is not yet in the tree.
5. **A 32 wide frame reaching a region map.** `show_regions.py` hardcodes `W, H = 16, 32` and silently
   truncates every row to 16 characters. Owned by Task 1 (`test_region_map_reads_a_32_wide_frame`).
   **CLOSED 2026-11-06, outside this plan.** The size comes from the frame, every frame in one file
   must share a size, and a short map is refused by row count. Eight cases are pinned in
   `tests\test_show_regions.py`, which did not exist before. Task 1's OTHER half is still open: the
   parser does not yet move to a shared `regions.py`.

---

## Scope: this is one plan of three

The design is three independent subsystems. This plan is the first, properly. The other two are named
here with what they would need, and neither blocks this one.

| Plan | Covers | Why it is separate |
|---|---|---|
| **1, this one** | region map library, projection, the gold master artefact, the declared feature answers, the check list, the pass driver, the skill, the read-only audit, the down run through the pipeline | Ships working software on its own: a down run pass that the owner can judge |
| **2, the feature ledger's verification half** | one automatic verifier per garment feature type (exposed area, strap, hem, collar), so "shown" and "hidden by the pose" are checked rather than declared | Needs plan 1's declared answers to exist first, and needs a second outfit to generalise from. Declaring the answer already stops the silent omission that caused both named Failure B cases |
| **3, the 32 wide swap path** | manifest rows at 32x32, the dx that is not constant, the dir 2 and dir 3 pair that share one header at dx -16 and dx 0, and the art for **174 of set 128's 288 records, which is 60%** | Blocks no part of plan 1. The gold master idles and the down and up runs are all 16x32 dx 0. Plan 1 fixes only the region map's width assumption, because Task 1 touches that file anyway. The art is the large part, and it is not tooling |

---

## File structure

| File | Responsibility |
|---|---|
| `scripts\permanent\rom\regions.py` | Read, write and check a region map, at any frame size. The alphabet and the role families live here |
| `scripts\permanent\rom\show_regions.py` | Unchanged purpose: render a map back over its frames. Loses its own parser to `regions.py` and its hardcoded size |
| `scripts\permanent\rom\project.py` | Carry one frame's naming onto another under the index gate, refuse the garment mask, report the eye bill |
| `scripts\permanent\rom\goldmaster.py` | Load and validate a gold master folder: three idle maps, the feature list, the per-feature gold answers |
| `scripts\permanent\rom\checks.py` | One function per named past failure. Each returns MINOR or MAJOR findings |
| `scripts\permanent\rom\sprite_pass.py` | The step list, the gates, the handback report |
| `art\gold\trunks_tank\` | The gold master artefact: `master.json`, `regions_front.txt`, `regions_back.txt`, `regions_side.txt` |
| `<frames dir>\regions.txt`, `features.json`, `drawing.json`, `pose.md` | The four per-row artefacts a pass consumes. Each one is a gate in Task 6's step list |
| `Projects\.claude\skills\log-sprite-pass\SKILL.md` | The method the harness loads |
| `scripts\permanent\tests\test_regions.py`, `test_project.py`, `test_goldmaster.py`, `test_checks.py`, `test_sprite_pass.py` | One test file per new module |

---

### Task 1: The region map library, at any frame size

**Files:**
- Create: `scripts\permanent\rom\regions.py`
- Modify: `scripts\permanent\rom\show_regions.py` (replace `load`, `check` and the `W, H = 16, 32` at line 29)
- Modify: `scripts\one-time\2026-11-01-trunks-side-walk\regions.txt` (add its missing `#png` lines)
- Create: `scripts\permanent\tests\test_regions.py`

**Interfaces:**
- Produces: `class RegionMap(key: str, grid: list[str], w: int, h: int)` with `at(x, y) -> str` and
  `pixels(letter: str) -> set[tuple[int, int]]`.
- Produces: `load(path: Path) -> tuple[dict[str, Path], Path | None, dict[str, RegionMap], dict[str, list]]`
  returning the `#png` map, the optional `#palette`, the maps by key and the `#bone` lists. Frame size
  comes from each key's own PNG, never from a constant.
- Produces: `ALPHABET: dict[str, str]`, letter to role family, and `family(letter: str) -> str`. The
  families are `hair, face, eye, skin, arm, hand, garment, trouser, boot, gear, unknown`.
- Produces: `transcription(m: RegionMap, data: bytes, w: int) -> tuple[list, list, list]` returning
  unlabelled lit pixels, labelled dead pixels and unknown letters. **A `?` counts as unlabelled**, so a
  map that is still partly projected can never pass.
- Produces: `write(path: Path, maps: dict[str, RegionMap], pngs: dict, bones: dict) -> None`.
- Produces: `head_rows(m: RegionMap) -> int`, the last row holding `H`, `F` or `E`. The head and body
  split is **per frame, from the map**, never a constant. Measured on the down run: the head reaches row
  18 in run0 and run2, and row 16 in run1 and run3, so the rows 0 to 15 split that `trunks_tank.py` uses
  for the stand and the walk would put base hair and base eyes on a Super Saiyan body in all four frames.
  CONFIRMED by `probe_facts.py`, and `pose.md` gives the cause: the head bobs 4 rows down in the contact
  frames and 2 in the pass frames.

The alphabet is the union of the two region files that exist, with one letter per role and the second
limb in lower case: `H` hair, `F` face, `E` eye, `J` neck shadow, `N` neck, `C` chest skin, `T` garment,
`X` garment trim, `B` belt, `P` trousers, `K` boot, `G` boot cuff, `S` gear, `L`/`l` screen left arm and
its hand, `R`/`r` screen right arm and its hand, `?` not yet named. `A`/`D` and `a`/`d` from the side
walk file are aliases of `L`/`l` and `R`/`r`.

- [ ] **Step 1: Write the failing tests**

```python
def test_region_map_reads_a_32_wide_frame():          # Review Focus 5
    pngs, _, maps, _ = load(TMP / "wide.txt")         # one key, a 32x32 PNG, 32 lines of 32 chars
    assert (maps["a"].w, maps["a"].h) == (32, 32)
    assert maps["a"].at(31, 31) == "K"

def test_a_short_line_is_an_error_not_a_pad():
    with self.assertRaises(ValueError):               # 16 chars under a 32 wide png
        load(TMP / "short.txt")

def test_down_run_transcription_is_clean():           # the known answer
    for key in ("run0", "run1", "run2", "run3"):
        missing, extra, bad = transcription(maps[key], data[key], 16)
        assert (missing, extra, bad) == ([], [], [])

def test_side_walk_file_declares_its_frames():
    pngs, _, maps, _ = load(SIDE_REGIONS)
    assert set(pngs) == {"idle", "walk2"} and all(p.exists() for p in pngs.values())

def test_alias_letters_map_to_one_family():
    assert family("A") == family("L") == "arm" and family("d") == family("r") == "hand"

def test_a_question_mark_counts_as_unlabelled():
    missing, _, bad = transcription(partly_projected, data["run2"], 16)
    assert missing and not bad                        # "?" is unlabelled, never an unknown letter

def test_head_rows_are_read_per_frame():
    assert [head_rows(maps[k]) for k in ("run0", "run1", "run2", "run3")] == [18, 16, 18, 16]
```

- [ ] **Step 2: Run the tests and see them fail** (module not found).
- [ ] **Step 3: Implement `regions.py`.** Parse the same `#png`, `#palette`, `#bone` and `[key]` format
  `show_regions.py` already defines in its docstring. Take `w` and `h` from the key's PNG and validate
  the grid against them.
- [ ] **Step 4: Change `show_regions.py` to import `regions.load`, `transcription` and `family`,** and
  to draw at the PNG's own size. Its `GEAR` set becomes `family(c) == "gear"`. Its output and its printed
  counts do not change for a 16 wide file.
- [ ] **Step 5: Add the four missing `#png` lines to the side walk regions file.** The frames are set 128
  anim 0 dir 2 index 0 and anim 1 dir 2 index 2; `art\vanilla-sets\set128\manifest.json` gives the PNG
  names. The side idle and side walk 2 maps each hold 10 lit pixels with no letter: fix them by eye at
  30x with `sprite_look.py`, or mark them `?`. Do not guess them from colour.
- [ ] **Step 6: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 7: Re-run `make_tool_index.py`,** and add one line to `docs\build-log.md`.

---

### Task 2: The projection, as a labour saver with a hard refusal

**Files:**
- Create: `scripts\permanent\rom\project.py`
- Create: `scripts\permanent\tests\test_project.py`

**Interfaces:**
- Consumes: `regions.RegionMap`, `regions.family`, `rom.sprite_guard.garment_mask`.
- Produces: `best_shift(src: bytes, tgt: bytes, size: tuple) -> tuple[int, int]`, the translation with the
  highest `len(moved & lit) - 0.25 * len(moved ^ lit)`.
- Produces: `project(src_map: RegionMap, src: bytes, tgt: bytes, size: tuple, refuse: set) -> tuple[RegionMap, dict]`.
  The returned map holds `?` everywhere the projection did not accept. The dict reports
  `{"accepted": int, "refused": int, "eye": int, "shift": (dx, dy), "source": str}`.
  **A pixel is accepted only when the source and target palette index are equal and non-zero, the source
  letter is not `?`, and the pixel is not in `refuse`.**
- Produces: `pick_source(candidates: dict[str, tuple[RegionMap, bytes]], tgt: bytes, size: tuple) -> str | None`,
  the candidate with the highest accept rate, or `None` when the best accept rate is under 0.35.

`refuse` is built by the caller and is always three sets together:

1. `garment_mask(vanilla_target_image, garment_indices)`, which measured 11% to 22% wrong.
2. The source map's `l` and `r` pixels, moved by the same shift.
3. **The target frame's own hand pixels**, which the caller takes from `pose.md`. Set 2 alone is not
   enough: at `(13,17)` of run3 the source said `F` and the truth is `r`, so the error sat on a pixel the
   source does not call a hand at all. Pose.md section 4 lists both hands of every frame by column and
   row, so this set is read, not derived.

The eye bill of 58 to 68 pixels per down run frame already assumes all three.

- [ ] **Step 1: Write the failing tests.** Every expected number below was measured by
  `scripts\one-time\2026-11-05-sprite-suite-plan\probe_garment_real.py` on the down run's known answer.

```python
def test_garment_mask_is_never_projected():           # Review Focus 2
    out, stats = project(run0_map, run0, run2, (16, 32), refuse=garment_mask(run2_img, JACKET))
    assert all(out.at(x, y) == "?" for x, y in garment_mask(run2_img, JACKET))
    assert stats["refused"] == 42                     # measured mask size of run2

def test_target_hands_are_never_projected():
    hands = {(x, y) for x in range(8, 12) for y in range(21, 25)}     # pose.md run2 near fist
    out, _ = project(run0_map, run0, run2, (16, 32),
                     refuse=garment_mask(run2_img, JACKET) | hands)
    assert all(out.at(x, y) == "?" for x, y in hands if run2_img.getpixel((x, y)))

def test_accepted_letters_are_right_outside_the_garment():
    out, stats = project(run0_map, run0, run2, (16, 32), refuse=garment_mask(run2_img, JACKET))
    named = [(x, y) for x, y in lit(run2) if out.at(x, y) != "?"]
    right = sum(1 for x, y in named if family(out.at(x, y)) == family(run2_map.at(x, y)))
    assert len(named) >= 190 and right / len(named) >= 0.97     # measured 210 at 98%

def test_the_nearest_phase_mate_wins():
    # measured: run2 accepts 76% of run0, run1 accepts 28%. Nothing from Task 3 is used here.
    assert pick_source({"run2": (run2_map, run2), "run1": (run1_map, run1)}, run0, (16, 32)) == "run2"

def test_no_source_means_no_projection():             # Review Focus 1
    assert pick_source({"run1": (run1_map, run1)}, run0, (16, 32)) is None   # measured 28%, under 0.35

def test_the_eye_bill_is_reported():
    _, stats = project(run0_map, run0, run2, (16, 32), refuse=garment_mask(run2_img, JACKET))
    assert stats["eye"] == len(lit(run2)) - stats["accepted"]
```

- [ ] **Step 2: Run the tests and see them fail.**
- [ ] **Step 3: Implement `project.py`.** Search `dx` in `-8..8` and `dy` in `-10..10` for `best_shift`;
  that window covered every measured pair, whose best shifts were `dy 0` or `dy 1`.
- [ ] **Step 4: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 5: Re-run `make_tool_index.py`.** Add one `RE-BIBLE.md` row recording the measured accept
  and accuracy rates, tagged per its section 1, and one line in `docs\build-log.md`.

---

### Task 3: The gold master artefact

**Files:**
- Create: `scripts\permanent\rom\goldmaster.py`
- Create: `art\gold\trunks_tank\master.json`
- Create: `art\gold\trunks_tank\regions_front.txt`, `regions_back.txt`, `regions_side.txt`
- Create: `scripts\permanent\tests\test_goldmaster.py`

**Interfaces:**
- Consumes: `regions.load`, `regions.transcription`.
- Produces: `class GoldMaster` with `features: list[Feature]`, `views: dict[str, RegionMap]` keyed
  `front`, `back`, `side`, and `answers: dict[str, dict[str, str]]`, view to feature name to answer.
- Produces: `class Feature(name: str, kind: str, indices: list[int], note: str)` where `kind` is one of
  `area`, `strap`, `hem`, `trim`, `accessory`.
- Produces: `load_master(folder: Path) -> GoldMaster`, which raises when a view's transcription is not
  clean, when a view is missing, or when any feature lacks an answer in any view.
- Produces: `ANSWERS = ("shown", "hidden", "turned")`, the three the design names.

`master.json` carries the outfit name, the set ids, the three chosen idle PNGs, the garment indices, the
feature list, and the three gold answers per feature. The Trunks tank's features, taken from the pixels
the owner already approved and from `docs\sprite-guide.md`: `exposed_chest` (area, the gap the open
jacket left at x6-10 over three rows), `strap_left` and `strap_right` (strap, the 1 px black `01` that
separates arm from chest), `scoop_neck` (trim, 3 skin pixels at row 16 on the back), `baldric`
(accessory), `scabbard` (accessory).

> [!WARNING]
> **`Feature.indices` is a note for a human, never a locator.** `4D` is the baldric in the side view and
> a tank and belt highlight in the front view, by the side walk file's own correction of 2026-11-02.
> Using an index to find a feature is the colour rule that section 7 forbids. A feature is located by its
> region map letters and its gold master answer, and `indices` only tells the reader what to look for.

> [!IMPORTANT]
> **Which three PNGs are the gold master is the owner's first decision, and it comes before the feature
> list.** The design calls locking the Trunks tank gold master the first job, and the art does not name
> itself: there are two front stands (`trunks_tank_base_front.png` and `..._front_stand1.png`), two side
> stands, and a back idle that carries the known highlight defect at y19 x1-x3. 33 PNGs sit in
> `art\trunks_tank\` and 32 are in its manifest, the odd one out being `trunks_tank_ssj_front.png`.
> CONFIRMED by `probe_facts.py`.

- [ ] **Step 0: Ask the owner which three approved PNGs are the gold master**, and whether the back
  idle's two `0x11` highlights at y19 x1-x3 stay as drawn or are fixed first. Show him the three
  candidates rendered at 1x, 3x and 12x beside each other. **Nothing else in this task starts until he
  answers.** Record the answer in `docs\ledger\progress.md`.
- [ ] **Step 1: Write the failing tests**

```python
def test_a_missing_view_is_refused():
    with self.assertRaises(ValueError):
        load_master(TMP / "front_only")

def test_every_feature_has_an_answer_in_every_view():
    gm = load_master(GOLD / "trunks_tank")
    assert all(set(gm.answers[v]) == {f.name for f in gm.features} for v in ("front", "back", "side"))

def test_the_known_front_answer():                    # the Trunks tank case the owner rejected
    assert load_master(GOLD / "trunks_tank").answers["front"]["exposed_chest"] == "shown"

def test_the_known_side_answer():
    gm = load_master(GOLD / "trunks_tank")
    assert gm.answers["side"]["baldric"] == "shown" and gm.answers["side"]["scabbard"] == "shown"

def test_an_unclean_transcription_is_refused():
    with self.assertRaises(ValueError):
        load_master(TMP / "unlettered_pixel")
```

- [ ] **Step 2: Run the tests and see them fail.**
- [ ] **Step 3: Letter the three gold master views by eye.** Render each at 30x with the index in every
  cell using
  `py -3.14 -P ...\rom\sprite_look.py <out.png> <frame.png> --zoom 30`, look at it, and write
  `regions_front.txt`, `regions_back.txt` and `regions_side.txt`. The frames are set 128 anim 0 dirs 0, 1
  and 2, index 0, which are 16x32 dx 0. Render each map back with `show_regions.py` and **look at all
  three panels** before going on. This is the eye spend the whole design buys down, and it is paid once.
- [ ] **Step 4: Implement `goldmaster.py` and write `master.json`.**
- [ ] **Step 5: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 6: Show the owner the three rendered maps and the feature list, and ask him the one open
  question**, which is whether the feature list is complete. This is the second question, after step 0's.
  Do not go on to Task 4 without his answer. Record it in `docs\ledger\progress.md`.

---

### Task 4: The per-frame feature answers

**Files:**
- Modify: `scripts\permanent\rom\goldmaster.py`
- Create: `scripts\permanent\tests\test_goldmaster.py` additions

**Interfaces:**
- Consumes: `GoldMaster`, `regions.RegionMap`.
- Produces: `answers_path(frames_dir: Path) -> Path`, which is `<frames_dir>\features.json`.
- Produces: `load_answers(path: Path, gm: GoldMaster, keys: list[str]) -> dict[str, dict[str, str]]`,
  frame key to feature name to answer, raising when a key or a feature is missing or an answer is not in
  `ANSWERS`.
- Produces: `missing(answers: dict, gm: GoldMaster, keys: list[str]) -> list[tuple[str, str]]`, every
  `(key, feature)` with no answer. The pass gate in Task 6 reads this.

This is the declared half of the ledger. It stops the silent omission that caused both named Failure B
cases: a frame cannot be drawn until it has said in writing what every feature does in it. Plan 2 adds
the verification half, which checks a declared answer against the pixels.

- [ ] **Step 1: Write the failing tests**

```python
def test_a_frame_with_no_answers_is_listed_as_missing():
    assert ("run2", "exposed_chest") in missing({}, gm, ["run0", "run1", "run2", "run3"])

def test_an_unknown_answer_word_is_refused():
    with self.assertRaises(ValueError):
        load_answers(TMP / "maybe.json", gm, ["run0"])     # answer "maybe"

def test_the_answer_file_round_trips():
    a = load_answers(RUN / "features.json", gm, ["run0", "run1", "run2", "run3"])
    assert set(a) == {"run0", "run1", "run2", "run3"}
    assert all(v in ANSWERS for frame in a.values() for v in frame.values())
```

- [ ] **Step 2: Run the tests and see them fail.**
- [ ] **Step 3: Implement the three functions.**
- [ ] **Step 3b: Write `docs\tasks\2026-11-05-trunks-run\features.json` BY EYE, one feature at a time.**
  This is an eye step, not a transcription of `pose.md`. Those two files answer some of it and not all of
  it, and the plan must not pretend otherwise:
  - `pose.md` settles the torso: "almost no torso shows in the two contact frames", and "the torso is 3
    or 4 pixels in a contact frame and 7 in a pass frame, at rows 17 to 20". That is a torso count, not
    an `exposed_chest` answer, and the run maps hold **no `C` letter at all**, so the exposed chest is
    still a reading.
  - `preflight.md` says "the down run shows no sword, no scabbard and no baldric", and its own table then
    counts `4D` at 1 px in run1 and 2 px in run3. `4D` has two roles, and the side walk file's correction
    of 2026-11-02 says that in a front view it is a tank and belt highlight, not the baldric. Open the
    frames at 30x and decide which it is here.
  Render each decision back over the frame and look at it before writing the answer down.
- [ ] **Step 4: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 5: Re-run `make_tool_index.py`,** and add a `RE-BIBLE.md` row for the down run's feature
  answers.

---

### Task 5: The check list

**Files:**
- Create: `scripts\permanent\rom\checks.py`
- Create: `scripts\permanent\tests\test_checks.py`

**Interfaces:**
- Consumes: `regions.RegionMap`, `regions.family`, `sprite_guard.garment_mask`, `sprite_guard.violations`,
  `sprite_stats.widest_run`.
- Produces: `class Finding(check: str, level: str, key: str, where: tuple, said: str)` where `level` is
  `"MINOR"` or `"MAJOR"`.
- Produces: `run_all(vanilla: dict, edited: dict, maps: dict, gm: GoldMaster, answers: dict) -> list[Finding]`.
- Produces one function per row of the table below, each with the signature
  `check_<name>(...) -> list[Finding]`.

Every threshold is copied from `docs\sprite-guide.md`. None is invented. The level follows the owner's
gate rule: fix minor, carry on, show the list at the end; stop only for a missing limb or something odd
that cannot be concluded.

| Check | Threshold, verbatim from the guide | Failure it came from | Level |
|---|---|---|---|
| `transcription` | every lit pixel has a letter, no dead pixel does | a map that does not describe the frame | MAJOR |
| `outside_mask` | no changed pixel outside the garment mask, unless declared with `--allow` | the deleted eye, 2026-11-01 | MAJOR |
| `mask_driven` | every changed pixel is inside the mask plus the declared `--allow` set, **and** every mask pixel changed | the four failed side passes | MAJOR |
| `arm_path` | a 4-connected skin path from the deltoid top to the vanilla hand, **started on the BAND row** | walk 2's arm hanging unattached | MAJOR |
| `arm_width` | per row, per arm, a bare skin run that is not a hand is 3 px, 4 at the widest | the filled sleeve, frame 4 at 5, 7, 8, 5 px | MINOR |
| `skin_count` | a frame whose skin count is half its neighbours' has lost an arm | walk 0 read 10 against 21 to 24 | MAJOR |
| `silhouette` | taking the garment off shrinks it: front -13, side -9, back -2 px on his approved frames. Zero shrink is a recolour | the pure recolour | MINOR |
| `highlight_count` | one `0x11` per **limb** run. A chest is not a limb | "randomly splashed skin colors" | MINOR |
| `highlight_offset` | the highlight holds a constant offset from one edge of the run, not a constant x | the wandering highlight, x9, x10, x10, x9, x9 | MINOR |
| `edge_walk` | the outer edge moves about one column every two rows; the elbow turn is at least 2 rows tall; a bow holds one column for three rows, two is too much | "wheres the elbow" | MINOR |
| `accessory_parity` | the accessory's count across the row is expected UNEVEN. An even count per frame is the thing to suspect | the chape, present in three frames of four | MINOR |
| `sleeveless_balance` | in a side view of a sleeveless top, skin must outweigh garment inside the changed set | "its a sleevless tank top with exposed arms" | MAJOR |
| `one_body` | rows below the head are byte-identical across the forms, with the split taken from `regions.head_rows` per frame | the gi forms | MAJOR |
| `feature_answers` | every feature has an answer for every frame | the flat sash, the missing exposed chest | MAJOR |

> [!WARNING]
> **`highlight_count` must read the limb runs from the region map.** Measured on the 33 approved tank
> PNGs: a naive "one `0x11` per skin run" flags 19 of them, because it counts the chest, which the guide
> says shades `M L M L M`. Skipping runs that cover the body centre column isolates the back row, but
> that proxy breaks on the down run, where a forearm crosses the centre. The proxy is allowed only in the
> mapless read-only pass of Task 7. With a map, use the map.

- [ ] **Step 1: Write the failing tests**

```python
def test_highlight_check_uses_the_region_map_when_there_is_one():      # Review Focus 3
    f = check_highlight_count(back_idle, maps["back"], use_centre_proxy=False)
    assert [x.where for x in f] == [(1, 19)]                 # the one documented defect run
    front = check_highlight_count(front_idle, maps["front"], use_centre_proxy=False)
    assert front == []                                       # the chest at y17 x6-x10 is not a limb

def test_the_centre_proxy_finds_the_back_row_and_nothing_else():
    flagged = {p.name for p in approved() if check_highlight_count(p, None, use_centre_proxy=True)}
    assert len(flagged) == 8 and all("back" in n for n in flagged)      # measured, base and ssj

def test_arm_path_starts_on_the_band_row_and_fails_a_detached_arm():
    assert any(f.check == "arm_path" and f.level == "MAJOR"
               for f in check_arm_path(side_walk_2_detached, maps["walk2"], band_row=16))

def test_a_declared_allow_is_not_a_mask_driven_failure():
    f = check_mask_driven(vanilla, sloped_shoulder, mask, allow={(4, 16), (11, 16)})
    assert f == []                                   # a declared change outside the mask is legal

def test_an_unchanged_mask_pixel_is_a_mask_driven_failure():
    assert any(x.level == "MAJOR" for x in check_mask_driven(vanilla, half_done, mask, allow=set()))

def test_one_body_splits_per_frame_not_at_row_16():
    # run0's head reaches row 18, so a split at 16 compares base hair against gold hair
    assert check_one_body(run0_base, run0_ssj, maps["run0"]) == []

def test_a_pure_recolour_is_minor_not_major():
    f = check_silhouette(vanilla, recoloured, garment_mask(vanilla_img, JACKET))
    assert [x.level for x in f] == ["MINOR"]

def test_a_lost_arm_is_major():
    assert any(f.level == "MAJOR" for f in check_skin_count(row_with_walk0_at_10px))
```

- [ ] **Step 2: Run the tests and see them fail.**
- [ ] **Step 3: Implement `checks.py`.** Reuse `sprite_guard.violations` for `outside_mask` and
  `sprite_stats.widest_run` for `arm_width`. Write no new copy of either.
- [ ] **Step 4: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 5: Re-run `make_tool_index.py`,** and add a `RE-BIBLE.md` row for the back row highlight
  finding, which is new: the defect the guide records in the back idle repeats in all four back walk
  frames of both forms.

---

### Task 6: The pass driver and the handback report

**Files:**
- Create: `scripts\permanent\rom\sprite_pass.py`
- Modify: `scripts\permanent\rom\sprite_loop.py` (the `g.seek(n)` decode check, line 71)
- Create: `scripts\permanent\tests\test_sprite_pass.py`

**Interfaces:**
- Consumes: everything above, plus `rom_sheet` for frame location, `log2_sprites.export_set`,
  `sprite_look`, `sprite_loop`, `sprite_guard`.
- Produces: `frames_of(set_id: int, anim: int, dirn: int) -> list[dict]`, the manifest rows for one
  `(set, anim, dir)` in index order. This is the design's missing single step.
- Produces: `run_pass(set_id: int, anim: int, dirn: int, gold: Path, out: Path, stop_after: str = "") -> Report`.
- Produces: `class Report` with `fixed: list[str]`, `unsure: list[str]`, `findings: list[Finding]`,
  `gif: Path`, `frames: list[Path]`, and `text() -> str`.
- Produces: `load_drawing(path: Path, masks: dict[str, set]) -> dict[str, dict[tuple[int, int], int]]`,
  which reads `<out>\drawing.json` and **asserts that every key is inside that frame's garment mask**.
  It raises on the first key that is not.

`drawing.json` is the artefact the draw step consumes, and its shape comes straight from the guide:
"Write the hand drawing as a dict of `(x, y)` to index, never as a grid. The assert that each key is a
masked pixel is what keeps a hand drawing honest." One object per frame key, each mapping `"x,y"` to a
palette index. A frame drawn by a mask driven function supplies the same dict as its output, so one
artefact serves both the ruled frames and the hand drawn ones.

The step list, and which steps are gates. The design left where the gates sit to this plan.

| # | Step | Gate |
|---|---|---|
| 1 | Locate the frames and export the vanilla PNGs | MAJOR on a missing record |
| 2 | Load the gold master | MAJOR on any `load_master` failure |
| 3 | **Require `pose.md` beside the frames** | **MAJOR. No file, no draw** |
| 4 | Project each frame's naming from its best already lettered neighbour, then stop for hand lettering of the `?` pixels | MAJOR while any `?` remains |
| 5 | Transcription check on every map | MAJOR |
| 6 | Require `features.json` complete for every frame and feature | MAJOR |
| 7 | **Require `drawing.json`**, then apply it | **MAJOR. No file, no frames.** MAJOR on any key outside the mask |
| 8 | Run every check in Task 5 | MAJOR stops, MINOR is fixed and listed |
| 9 | Build the GIF, the labelled strip and the four review views | never a gate |
| 10 | Write the report | never a gate |

> Step 3 is how the fifth builder question is settled without touching `settings.json`. The driver
> refuses to draw until the pose has been read and written down. That is the step that was skipped on the
> down run, and a gate in the code cannot be skipped by forgetting to open a document.

The report is the design's handback: frames, a GIF, and a short list. Its shape is fixed, and it is not a
wall of text.

```
Pass: set 128 anim 13 dir 0, 4 frames.
Fixed on my own call:  <one line each, or "nothing">
Unsure, your call:     <one line each, or "nothing">
Checks:                <n> MINOR, <n> MAJOR, all listed below with the frame and the pixel
Eye spent:             <n> pixels hand lettered of <n> lit, across <n> frames
Files:                 <gif>  <strip>  <frames dir>
```

- [ ] **Step 1: Write the failing tests**

```python
def test_gif_survives_repeated_frames():              # Review Focus 4
    out = build_gif(TMP / "dup", [run0_png, run0_png])            # byte identical pair
    assert out.exists()                                            # today this raises EOFError

def test_no_pose_file_stops_before_drawing():
    r = run_pass(128, 13, 0, GOLD / "trunks_tank", TMP / "nopose")
    assert r.findings[0].check == "pose_read" and r.findings[0].level == "MAJOR"
    assert r.frames == []

def test_an_unnamed_pixel_stops_the_pass():
    r = run_pass(128, 13, 0, GOLD / "trunks_tank", TMP / "partial")   # one "?" left in run2
    assert any(f.check == "transcription" and f.level == "MAJOR" for f in r.findings)

def test_no_drawing_file_stops_before_frames():
    r = run_pass(128, 13, 0, GOLD / "trunks_tank", TMP / "nodrawing")   # maps and features complete
    assert any(f.check == "drawing" and f.level == "MAJOR" for f in r.findings) and r.frames == []

def test_a_drawn_pixel_outside_the_mask_is_refused():
    with self.assertRaises(ValueError):
        load_drawing(TMP / "stray.json", {"run0": mask_run0})           # one key at (8, 13), the eye row

def test_frames_of_finds_the_four_down_run_records():
    assert [f["header"] for f in frames_of(128, 13, 0)] == [0x357690, 0x357784, 0x35788C, 0x35797C]

def test_the_report_is_short():
    assert len(run_pass(...).text().splitlines()) <= 40
```

- [ ] **Step 2: Run the tests and see them fail.**
- [ ] **Step 3: Fix `sprite_loop.py`.** Its decode check seeks frame `n` of the written GIF, and Pillow
  drops a frame identical to the one before it, so `g.seek(n)` raises `EOFError`. Compare only the frames
  the GIF actually holds, and print how many were deduplicated. CONFIRMED by running it on two identical
  16x32 frames and on two identical 32x32 frames; both raise, and two different 32x32 frames pass.
- [ ] **Step 4: Implement `sprite_pass.py`** with the step list above.
- [ ] **Step 5: Run the tests and the whole suite, and see them pass.**
- [ ] **Step 6: Re-run `make_tool_index.py`,** and add one line to `docs\build-log.md`.

---

### Task 7: The read-only pass over the 32 approved PNGs

**Files:**
- Create: `scripts\one-time\2026-11-05-sprite-suite-plan\audit_approved.py`
- Create: `docs\tasks\2026-11-05-sprite-suite-plan\approved-audit.md`

**Interfaces:**
- Consumes: `checks.run_all` with `use_centre_proxy=True`, because these frames have no region maps.

This is the owner's call in design section 3b: check all 32, show the list, change nothing. It also
calibrates the checks against art whose answer is known, and it derives and checks the Super Saiyan twin
in the same pass, because the two share one body.

**Drive the audit from `art\trunks_tank\manifest.json`, which holds 32 rows, not from a glob of the
folder, which holds 33 PNGs.** The extra file is `trunks_tank_ssj_front.png`, which `trunks_tank.py`
says is waiting on the owner. All 10 back PNGs are in the manifest, so the 8 the highlight check flags
are all audited. CONFIRMED by `probe_facts.py`.

**Call the existing derivation, do not write a new one.** `patches\trunks_tank.py` and
`scripts\one-time\2026-11-02-trunks-ssj\derive.py` already derive set 134 from set 128, with the collar
role map `E5->14`, `64->2E`, `62->78` the owner settled on 2026-11-05. A simpler rewrite here would make
the audit report its own drift as art defects.

- [ ] **Step 1: Write the failing test**

```python
def test_the_audit_changes_no_file():
    before = {p: p.stat().st_mtime_ns for p in ART.rglob("*.png")}
    audit_approved.main()
    assert {p: p.stat().st_mtime_ns for p in ART.rglob("*.png")} == before
```

- [ ] **Step 2: Run the test and see it fail.**
- [ ] **Step 3: Implement the audit.** Read only. Import the existing derivation rather than restating
  it, and check both forms. **State what the derivation drops. Do not ask.**
- [ ] **Step 4: Run the audit and write `approved-audit.md`,** one line per disagreeing frame, grouped by
  check. The `highlight_count` section must name the 8 back frames and nothing else; a different count
  means a check changed and the plan's calibration is stale.
- [ ] **Step 5: Run the whole suite and see it pass.**
- [ ] **Step 6: Hand the owner the list.** He decides per frame. **No shipped art moves on the suite's
  word.** Record his decisions in `docs\ledger\progress.md`.

---

### Task 8: The skill, and the hook drafted for the owner

**Files:**
- Create: `log-sprite-pass\SKILL.md`, under the folder the owner picks in step 0
- Create: `docs\tasks\2026-11-05-sprite-suite-plan\hook-proposal.md`
- Modify: `C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\CLAUDE.md` (the sprite line in "Start
  of a session")

The owner chose a skill over a document because `docs\sprite-guide.md` already held the steps that were
skipped, and having it written down did not make anyone open it. The skill's job is to force the pose
read and to restate the contract in every drawing agent's brief.

The skill's structure, in the order it must be worked:

1. **Pre-flight**, the guide's six items, as six checkboxes. Nothing is drawn until all six are ticked.
2. **The pose read**, which writes `pose.md`: name the action from the anim number, say what the body
   must do before looking at a pixel, find the body axis, locate the joints, compare against step 2, then
   render and look.
3. **The region maps**, projected where Task 2 allows it and hand lettered everywhere else.
4. **The feature answers**, one per feature per frame.
5. **The draw**, mask driven, never a hand written grid.
6. **The pass**, `sprite_pass.py`, which gates every one of the above.
7. **The handback**, the Task 6 report, and nothing more.

- [ ] **Step 0: Ask the owner where the skill lives.**
  `C:\Users\josephgonzalez\Documents\Projects\.claude\skills\` already holds eleven HALO skills and is
  shared with his work project. `C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\.claude\skills\`
  keeps a personal project's skill out of that folder. LOG is personal and the NYPL work rules do not
  apply to it, so the second is the cleaner home, but only a run proves it loads. **This task also edits
  LOG's `CLAUDE.md`, so say that in the same question.**
- [ ] **Step 1: Write `SKILL.md`** with YAML frontmatter carrying `name: log-sprite-pass` and a
  description naming its triggers: sprite work, an outfit swap, a frame, an animation row, a region map.
  Follow the shape of `Projects\.claude\skills\halo-code-tidy\SKILL.md`.
- [ ] **Step 2: Add the one sentence every drawing agent's brief must carry** to the skill, and the rule
  that an art agent is briefed with it. This is the part that binds agents without a hook.
- [ ] **Step 3: Add the skill to `CLAUDE.md`'s "Start of a session" sprite line,** beside
  `docs\sprite-guide.md`.
- [ ] **Step 4: Draft `hook-proposal.md` for the owner.** State the event, the exact `settings.json`
  lines, what it would gain over invoking the skill by name, and what it would cost. **Build nothing.**
  The constraint is explicit: a hook needs his approval first.
- [ ] **Step 5: Invoke the skill by name in a fresh session** and confirm that it loads from the folder
  step 0 chose and that its steps run. A skill that does not load from `LOG\.claude\skills\` moves to
  `Projects\.claude\skills\`, and the move is reported, never assumed.

---

### Task 9: The down run through the whole pipeline

**Files:**
- Create: `art\trunks_tank\down-run\` frames, and the pass output under
  `docs\tasks\2026-11-05-sprite-suite-plan\down-run\`
- Modify: `art\trunks_tank\manifest.json` (four base rows, four Super Saiyan rows)

This is the acceptance run. The down run was chosen because its answer is already known: `pose.md` reads
the pose, `regions.txt` letters all four frames, `preflight.md` settles the gear and the alignment, and
the owner has already rejected two drafts of it, so a third bad draft is recognisable.

**This task ends with art on the approved queue. It does not build a ROM.**

- [ ] **Step 1: Copy in only `pose.md` and TWO of the four region maps,** run0 and run1, one per phase,
  from `docs\tasks\2026-11-05-trunks-run\`. **Leave run2 and run3 out.** The whole point of this task is
  that the pass must project them, and a run with all four maps present never exercises the projection
  at all.
- [ ] **Step 2: Run the pass.**
  `py -3.14 -P C:\Users\josephgonzalez\Documents\Projects\Workspace\LOG\scripts\permanent\rom\sprite_pass.py --set 128 --anim 13 --dir 0 --gold art\gold\trunks_tank --out docs\tasks\2026-11-05-sprite-suite-plan\down-run`
  Expected: `pick_source` picks run0 for run2 and run1 for run3, because those are the phase mates. The
  pass then stops at step 4 with `?` pixels left in run2 and run3.
- [ ] **Step 3: Hand letter the `?` pixels of run2 and run3 by eye,** at 30x with the index in every
  cell. Do not open `docs\tasks\2026-11-05-trunks-run\regions.txt` while doing it. It is the answer key
  and step 4 compares against it.
- [ ] **Step 4: Diff the finished run2 and run3 maps against the known answer**, and report the role
  agreement per frame. Expected from the probes: the projection supplied about 210 of 305 pixels on run2
  from run0 and about 219 of 334 on run3 from run1, at 98% to 100% role accuracy, refused all 42 and 34
  garment pixels, and left 58 to 68 pixels per frame for the eye. **A role agreement below 95% on the
  projected pixels means the projection changed and Task 2's tests are stale. A disagreement on a hand
  lettered pixel is a reading to settle by looking, not a bug.**
- [ ] **Step 4b: Write `drawing.json` by hand for all four frames.** `preflight.md` section 3 measured
  that no run frame repeats another: the closest pair differs by 98 pixels of 512 and no pair is close
  enough to copy. By the guide's split, that makes every one of the four a hand drawn frame, so no rule
  is written for this row.
- [ ] **Step 5: Derive the Super Saiyan four** with the existing derivation, splitting head from body at
  `regions.head_rows` per frame, which is row 18 for run0 and run2 and row 16 for run1 and run3. State
  what the derivation drops.
- [ ] **Step 6: View every review sheet yourself, head to foot, at 1x, 3x and large, before measuring
  anything.** The whole figure first. Review the part of the frame you did not touch.
- [ ] **Step 7: Run the whole suite and see it pass.**
- [ ] **Step 8: Hand the owner the report, the GIF and the frames,** with the edit kit, and add the eight
  manifest rows only after he accepts them. `test_trunks_tank.py` pins `PNG_COUNT`, `HEADER_COUNT` and
  `KEY_COUNT` at lines 115 to 117, so those three constants move in the same step as the manifest rows,
  or the suite goes red.
- [ ] **Step 9: Log the pass** in `docs\build-log.md` and `docs\ledger\progress.md`, and add the
  `RE-BIBLE.md` rows the pass learned. **Ask him whether the down run counts as the pre-approved
  "initial walking animation" build, or whether that means anim 1.** Do not build either way until he
  answers.

---

## Open, and only the owner can decide

In the order the plan reaches them.

1. **Which three approved PNGs are the Trunks tank gold master, and does the back idle's highlight defect
   stay?** Two front stands and two side stands exist, and the back idle carries two `0x11` in one arm
   run at y19 x1-x3. Task 3 step 0 asks, and nothing in Task 3 starts before the answer.
2. **Is the Trunks tank feature list complete?** Task 3 step 6 asks, with the three rendered maps.
3. **Where does the skill live, and may LOG's `CLAUDE.md` be edited?**
   `Projects\.claude\skills\` is shared with HALO; `LOG\.claude\skills\` is not. Task 8 step 0 asks.
4. **The harness hook.** Task 8 drafts it. It is a `settings.json` change and needs his explicit yes.
5. **The eight back row frames the highlight check flags.** Task 7 hands him the list. No shipped art
   moves without him.
6. **Is the down run the pre-approved "initial walking animation" build, or is that anim 1?** Anim 1's
   keys are already in the tank manifest, which suggests anim 1. Task 9 step 9 asks.

---

## Self-review

**Spec coverage.** Design section 10's seven open items map to tasks: 1 the step list and its gates, Task
6. 2 the gold master artefact, Task 3. 3 the garment feature ledger, Task 4 for the declared half and
plan 2 for the verification half. 4 the check list and its thresholds, Task 5. 5 where checks live and
minor against major, Task 5 and Task 6. 6 the skill's structure and how it forces the pose read, Task 8
and Task 6 step 3. 7 the report format, Task 6. Section 3b's four decisions: the read-only pass, Task 7.
The Super Saiyan twin in the same pass, Task 7 step 3. No ROM at the end of a pass, Global Constraints
and Task 9. The per-frame eye budget, Task 2, with the design's mechanism corrected by measurement.
Section 9's six gaps: the single step from `(set, anim, dir)`, Task 6 `frames_of`. 32 wide, Task 1 for
the region map and plan 3 for the swap path. The gold master, Task 3. The feature ledger, Task 4. The
cross frame check, Task 5 `skin_count` and `accessory_parity`. The handback, Task 6. The design's own
flagged risk, the projection, is measured in nine probes before Task 1 and proved end to end in Task 9,
where two of the four maps are deliberately withheld so the projection has real work to do.

**Step scan.** Every code step names a signature and a file. Test steps carry the assertions with the
measured values in them. The only numbers that are not from the guide or from a probe are the search
window in Task 2 step 3 and the 0.35 accept floor in Task 2, and both are stated with their evidence.
Four steps are eye steps and say so rather than pretending a file already holds the answer: Task 3 step
3, Task 4 step 3b, Task 9 step 3 and Task 9 step 6.

**Type consistency.** `RegionMap`, `Feature`, `GoldMaster`, `Finding` and `Report` are defined once and
used under those names throughout. `family()` is the single role mapper, used by `regions.py`,
`project.py` and `checks.py`. `head_rows()` is the single head and body split, used by Task 5's
`check_one_body` and Task 9 step 5, and no task writes the constant 16. `garment_mask` is
`sprite_guard`'s, never re-implemented. `project()`'s stats key is `refused`, in its interface and in its
test. Task 2's tests name only run0 to run3, so Task 2 does not wait on Task 3.

**Review Focus.** All five have a named test in a named task. None is a leftover.

**Proportion.** Counted by `scripts\one-time\2026-11-05-sprite-suite-plan\check_plan_file.py`: the spec
is 228 lines and this plan is 833, a ratio of 3.7, split 166 lines of fenced code, 57 table lines and 610
of prose and steps over nine tasks. **That is longer than the skill's guidance likes, and the reason is
in the spec.** Design section 10 leaves seven mechanisms open and section 9 says "most of the build" is
gaps, so the decisions the implementer cannot make alone genuinely outnumber the spec's sentences. The
code blocks hold test names, assertions and signatures only, with no function bodies, and every table row
is one such decision. Re-run the counter after any edit rather than trusting this paragraph.

## Execution handoff

Plan complete. Please review it. Which execution approach would you prefer?

- **Subagent-driven.** A fresh agent implements each task and a fresh reviewer checks it before the next
  starts, then a whole-branch review at the end. Most thorough, and it costs a fresh context per task.
- **Native.** I implement every task in this session, then one fresh reviewer on the strongest model
  checks the whole branch.

**For this plan I recommend subagent-driven**, because Tasks 3, 7 and 9 each spend the owner's eye or
hand off a list to him, so a fresh reviewer between them is the cheapest place to catch a check that was
calibrated wrong. Does the plan capture what you want, and which approach should we use?
