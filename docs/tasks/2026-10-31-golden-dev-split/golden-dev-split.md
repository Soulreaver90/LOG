# Golden master and dev master: the plan, with the evidence

2026-10-31, while stepping away:

> Main is the golden master, it should use finished products. The gi is not a finished product so it
> shouldnt hit the master build. We work on that locally in a dev build.
> So we will have two roms, the golden master with the sprites/data posted, and our dev master which uses
> local data as well as golden masters, such as the gohan gi.
> Work on this after the two tasks are done.

Status: **ready to build, waiting on the two tasks.** Nothing in the build lists is edited yet.

---

## 1. The shape of the split

The gi art is **not** a separate feature. It is an overlay on vanilla sprite sets. `gohan_gi.apply()`
already builds each new set from a vanilla source set, then paints the work-in-progress art over it:

```python
src = rom_ptr(rom, SET_TABLE + 4 * (layout - FIRST_ID))   # the vanilla set it is laid out from
records, frames = art_records(folder)                      # the overlay
offsets[set_id] = build_set(rom, src, records, frames, alloc, counts={0: idle})
```

`SETS = {157: ("gi_base", 56), 158: ("gi_ssj_v2", 59), 159: ("gi_ssj2_aura", 59), 160: ("gi_rage_aura", 58)}`

So the seam already exists. The golden master runs the same module and relocates the same sets, but
without the overlay. The dev master adds the overlay back from art on your disk.

> [!NOTE]
> `gohan_gi` already reads `LOG_GI_SSJ` and `LOG_GI_SSJ2` from the environment to swap art folders
> (`gohan_gi.py:41-42`). The art source is already a parameter, not a constant.

**Dev stays byte-identical to r40.** Today's r40 is exactly "golden code plus local gi art", so the dev
build must still produce `14d6b831`. That is the gate for the dev side. Only the golden master gets a new
SHA-1.

**Consequence for the trials in flight:** card 4 v12 and Cell Jr v9 were built on r40 and remain valid dev
trials. They need **no** rebuild, as long as dev reproduces `14d6b831`.

## 2. Why removing the module was never the answer

I parsed every `alloc.notes[...]` read in the 23 main-list modules and computed the closure from `gohan_gi`:
**17 of 23 depend on it.** But every one of them reads its *structure*, never its pixels.

| Module | What it reads from `gohan_gi` | Line |
|---|---|---|
| `ssj2_form` | the notes dict, for the relocated table | `ssj2_form.py:391` |
| `ssj2_idle` | `set_159`, `set_160` offsets | `ssj2_idle.py:84-86` |
| `npc_gi` | `appearance_copy` | `npc_gi.py:91` |
| `cellgames_ssj` | `appearance_copy` | `cellgames_ssj.py:96` |
| `superperfect_cell` | the notes dict, plus `ssj2_idle` | `superperfect_cell.py:126` |

Dropping the module from the golden list would therefore cut Super Saiyan 2, every portrait, the HUD, the
ki pool, the full-power system, Super Perfect Cell and the Vegeta scene. Keeping the module and dropping
only the overlay costs nothing. `piccolo_gi_scene` stays in golden: it is approved and nothing depends on it.

## 3. The art is a complete overlay, so a vanilla golden build is sound

| folder | frames | keys | vanilla sources | frames with no source |
|---|---|---|---|---|
| `gi_base` | 162 | 288 | set56 | **0** |
| `gi_ssj_v2` | 159 | 276 | set59 | **0** |
| `gi_ssj2_aura` | 163 | 292 | set58, set59, golden | **0** |
| `gi_rage_aura` | 139 | 220 | set58 | **0** |

Every frame names its vanilla origin, so nothing in the overlay is art without a vanilla counterpart.

**The one risk left:** the overlay may define anim/dir/index keys that the vanilla set does not have. If it
does, a no-overlay golden build gives sets 157 to 160 fewer records, and `ssj2_idle` or `superperfect_cell`
could fail. This is testable, not arguable: build golden and run the full suite. That is the first gate in
the work below.

## 4. The repository side is already proven

The `.gitignore` now carries only finished art plus proven build inputs. The proof is an end-to-end rebuild
from the git index, not a reading of the code:

1. `git checkout-index -a --prefix=<scratch>\export\`
2. copy in the two ROM dumps from `data\roms\`
3. build main from the export

Result: `export_main.gba sha1=14d6b8314f5f418f80021fe60ef8d052b5dcf2be`, which matches r40.

| | files | size |
|---|---|---|
| before the art rules | 9,713 | 112.1 MB |
| now | 1,234 | 10.2 MB |

Two defects that test caught, which reading the code had missed:

- `ssj2_form` opens `art\hud_z2_usable.bin` and `art\hud_z2_dim.bin`.
- `superperfect_cell` opens `art\cell_aura\scale_15\`, 110 files.

Both are golden-master modules. Without them a clone cannot build. Both are now whitelisted.

**Correction to record:** a clone alone does not build the ROM. A clone **plus your own two ROM dumps**
does. The dumps are yours and stay out of the repository, which is correct.

## 5. The work, once both tasks report

1. Add a no-overlay mode to `gohan_gi`, keeping every published note key identical.
2. `build_list.txt` becomes the golden master: same 23 modules, no gi overlay.
3. `build_list_dev.txt` becomes the dev master: the golden list plus the overlay. **Gate: SHA-1 must be
   `14d6b831`.**
4. Point the trial lists at the dev list.
5. Run the full suite. Fix the SHA pins that move for golden only.
6. Drop the four `!art/gi_*` whitelist lines, then `git reset` and `git add -A`.
7. Re-run the export build test against the golden list.

Open question for me, which does not block the work: in the golden master Gohan wears the vanilla
outfit while `piccolo_gi_scene` still shows Piccolo giving him a gi. I am keeping the scene in golden. Say
if you would rather it moved to dev. It is a one-line change either way.

---

# CORRECTION, 2026-10-31: the split is blocked, and section 3 above was wrong

> [!WARNING]
> Section 3 says "every frame names a vanilla origin, so nothing in the overlay is art without a vanilla
> counterpart". **That is wrong.** It counted frames, not keys. My own table already showed the gap and I
> did not read it: 292 keys against 276, and 220 against 204.

The split task measured keys and stopped at the gate without editing anything. I verified every number
myself from the manifests and the tests.

## What is actually true

**32 overlay keys have no place in the vanilla set.** All 32 are anim 0, indexes 2 to 5, in all four
directions.

| set | art folder | vanilla layout | anim 0 per dir, vanilla | anim 0 per dir, overlay | extra keys |
|---|---|---|---|---|---|
| 157 | `gi_base` | set 56 | 2 | 2 | 0 |
| 158 | `gi_ssj_v2` | set 59 | 2 | 2 | 0 |
| 159 | `gi_ssj2_aura` | set 59 | 2 | **6** | **16** |
| 160 | `gi_rage_aura` | set 58 | 2 | **6** | **16** |

Sets 157 and 158 are a clean overlay. Only 159 and 160 carry the aura idle cycle.

**Why it breaks a no-overlay golden build.** `ssj2_idle.py` lines 14 to 16 store `obj+0x14 = body * 3 +
((tick >> 3) % 3)`, values 0 to 5, for sets 159 and 160. Its own header names the reason: "the 6 idle
records gohan_gi builds per dir". With 2 records per dir, indexes 2 to 5 run past the end of the list.
`superperfect_cell.py:126` re-assembles the same code and checks it byte for byte, so it inherits the
dependency. The contract is already pinned by `test_idle.py` in `test_anim_0_has_6_records_per_dir`.

**A second correction.** Set 159's 24 anim 0 records do not come from vanilla at all. Every one names
`golden golden_gi_ssj2std_d<N>.png`. `golden` is the art round folder `art\golden\`, not a vanilla set, and
not the "golden master" of this document. The two uses of the word collide, which is worth renaming later.
Set 160's 24 anim 0 records do all name `set58`, so that set has a vanilla fallback and 159 does not.

**A third constraint for whoever builds this.** `gohan_gi.apply()` must keep the overlay as its default.
Thirteen test modules call it directly with the default art folders. The golden switch therefore belongs at
the build-list level, as a separate patch name, not as an argument and not as an environment variable.

## The decision, which is mine and is about art

1. **Vanilla fill.** Golden fills anim 0 indexes 2 to 5 from the vanilla idle records. No pixel is
   invented and `ssj2_idle` keeps its structure. **Cost: the golden master has no aura cycle on the Super
   Saiyan 2 and Rage idles, and Gohan looks vanilla in every form.**
2. **Guard the hook.** `ssj2_idle` and `superperfect_cell` skip the hook when a set has only 2 idle
   records. This changes two proven modules and the pinned test.
3. **Declare the aura idle finished** and move only the gi body art to dev. Set 159 blocks this today,
   because its aura idle bodies come from `art\golden\`, which is a work-in-progress round.
4. **There is no golden master yet.** If the finished products do not exist, main waits. The repository
   still posts the code and the finished art, and dev stays the only buildable ROM.

Nothing is implemented. No build list, no module and no test was touched. The file timestamps confirm it.
