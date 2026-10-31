# Build the golden master and dev master split

Read `golden-dev-split.md` in this folder first. It holds my words, the dependency map and the
evidence. This brief gives you the gates. You choose the mechanism.

## The goal

`build_list.txt` becomes the **golden master**: finished products only. The work-in-progress Gohan gi art
must not reach it. `build_list_dev.txt` becomes the **dev master**: the golden list plus the gi art overlay,
read from art folders that stay on my disk.

All 23 modules stay in the golden master. The gi dependency is structural, not artistic: 17 of 23 modules
read `gohan_gi`'s relocation work and none reads its pixels. Do not remove any module from any list.

## The gates, in order. Each one is pass or fail, not a judgement

1. **Dev rebuilds to `14d6b8314f5f418f80021fe60ef8d052b5dcf2be`.** Today's r40 is exactly "golden code plus
   local gi art", so the dev master must reproduce it byte for byte. If it does not, your mechanism is
   wrong. Fix the mechanism, never the gate.
2. **Golden builds, and every published `alloc.notes["gohan_gi"]` key is unchanged in name and meaning:**
   `appearance_copy`, `set_table`, `set_157`, `set_158`, `set_159`, `set_160`.
3. **The full suite passes once**, at the end. Golden's SHA-1 changes, so SHA pins that name the main build
   will move. Update those pins. A pin that names the dev or trial ROMs must NOT move, because of gate 1.
4. **The trial lists build.** `build_list_trial.txt` (Cell Jr) and `build_list_trial_chapters.txt` (card 4)
   must include the dev list, not the golden one, and must still produce their current SHA-1s.
5. **A clean clone builds golden.** Run this, which is how the repository was proven earlier today:
   - `git -C <LOG> checkout-index -a --prefix=<your scratch>\export\`
   - copy the two ROM dumps from `data\roms\` into `<export>\data\roms\`
   - build the golden list from the export
   - If a file is missing, it is a build input that the `.gitignore` drops. Report it. Do not edit
     `.gitignore` yourself.

## What to know before you design

`gohan_gi.apply()` already builds each set from a vanilla source set and then paints the art over it:

```python
src = rom_ptr(rom, SET_TABLE + 4 * (layout - FIRST_ID))
records, frames = art_records(folder)
offsets[set_id] = build_set(rom, src, records, frames, alloc, counts={0: idle})
```

`SETS = {157: ("gi_base", 56), 158: ("gi_ssj_v2", 59), 159: ("gi_ssj2_aura", 59), 160: ("gi_rage_aura", 58)}`,
and lines 41 to 42 already read `LOG_GI_SSJ` and `LOG_GI_SSJ2` from the environment. The art source is
already a parameter.

Every gi frame names a vanilla origin, and none lacks one. I checked all four manifests.

**The risk to settle first, before you build anything.** The overlay may define anim, dir and index keys
that the vanilla set does not have. If it does, a golden build without the overlay gives sets 157 to 160
fewer records, and `ssj2_idle` or `superperfect_cell` may fail. Measure this first and report the number.
If keys are lost, stop and report. Do not invent placeholder art.

**Do not use an environment variable as the golden or dev switch.** A clone must build golden with no
environment set up. The existing `LOG_GI_SSJ` vars may stay as they are.

## Files you may edit

`scripts\permanent\patches\gohan_gi.py`, the build lists under `scripts\permanent\`, and the tests whose
SHA pins move. Name any other file you need to touch in your report before you touch it.

## Report

Give: the key-count measurement, the mechanism you chose and why, golden's new SHA-1, dev's SHA-1 against
gate 1, the trial SHA-1s, the suite count and exit code, the result of gate 5, and every pin you changed.

---

# ADDENDUM 2026-10-31: I decided. Option 1, the vanilla fill

I picked **vanilla fill**, after seeing the measured key counts and the cost.

> Golden fills the 4 extra idle slots from vanilla's own idle frames, so `ssj2_idle` keeps its structure and
> no pixel is invented. Cost: in the golden master there is no aura cycle, and Gohan looks vanilla in every
> form.

So: in the golden master, sets 157 to 160 are relocated exactly as today, and their pixels are vanilla.
Sets 159 and 160 still publish **6 anim 0 records per direction**, so `ssj2_idle` and `superperfect_cell`
keep working untouched and `test_idle.py:test_anim_0_has_6_records_per_dir` keeps passing unchanged. Fill
indexes 2 to 5 from the vanilla idle records. Index `k` taking vanilla record `k // 3` is a sound rule.

**Invent no pixels. Draw nothing. Copy nothing out of `art\golden\`.** If a vanilla record you need does
not exist, stop and report.

## Constraints that are now settled, do not re-derive them

1. **Do not change `ssj2_idle.py`, `superperfect_cell.py` or `test_idle.py`.** I rejected the guard
   option. If your mechanism needs them edited, the mechanism is wrong.
2. **`gohan_gi.apply()` must keep the overlay as its default.** Thirteen test modules call it directly with
   the default art folders: `test_gi.py`, `test_ssj2.py`, `test_portraits.py`, `test_status.py`,
   `test_idle.py`, `test_npc_gi.py`, `test_cutscene.py`, `test_rage_text.py`, `test_rage_stats.py`,
   `test_status_portrait.py`, `test_art_inject.py`, `test_gi_base_audit.py`, `test_gi_post.py`.
3. **The switch lives at the build-list level**, as a separate patch name. Not an argument to `apply`, and
   not an environment variable, because a clone must build golden with nothing set up.
4. **`gohan_gi` is line 1 of the list.** Whatever structure you choose, the dev list must apply the same
   modules in the same order as today's `build_list.txt`, or gate 1 cannot pass.
5. The golden module must publish `alloc.notes["gohan_gi"]` under that exact key, with the same six
   sub-keys, because 17 modules read it.

## The gates are unchanged, and gate 1 is the arbiter

Dev must still rebuild to `14d6b8314f5f418f80021fe60ef8d052b5dcf2be`. If it does not, your mechanism is
wrong. Fix the mechanism, never the gate.

Also unchanged: the trial lists must still produce `ca397c4c2bee32b913ef0b4bf44ff8320df9f6ea` (Cell Jr) and
`b1743beb4bb73217ae0474d3e1ef25e08efa8da1` (chapters). The approved card 4 v12 today, so that SHA-1
is now a shipped artefact and must not move.
