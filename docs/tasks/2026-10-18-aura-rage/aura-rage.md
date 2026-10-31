# SSJ2 aura in the ROM with an idle hook, and a gi Rage set for the Cell fight (final, 2026-10-18 3:20 PM)

Personal GBA ROM hack (Legacy of Goku II, USA). Build on r12 (`archive\builds\log2_poc_r12.gba`, SHA-1 50a9f95d). The frame pass shared-body-1240 was cancelled (3:55 PM: "leave r12 as is"), and its task restored the r12 tree. Frame work is on hold: change no frame except those named below. Read first: `docs\RE-BIBLE.md` (sprites section 4, forms section 6, story section 8), `docs\research\re-outfit.md` section 7 (enter/tick pairs), `docs\research\re-forms.md`, the headers of `scripts\permanent\patches\gohan_gi.py`, `ssj2_form.py`, `gi_post.py`, `scripts\permanent\rom\log2_sprites.py` (`build_set`), and the aura drafts `art\golden\work_r3\aura2\bolts.py`, `mix.py`.

## Final decisions

1. Aura: the **outline** family alone (3:23 PM: "outline looks amazing! outline d0-d2"). This replaces the 8:04 AM mix choice: no long cross bolt. Reference: `aura2\aura2_outline_d0..d2.gif` and `aura2_outline.png`, made by the outline family in `aura2\bolts.py`. Match those frames: bolt count, length, placement and timing.
2. Idle hook: approved 8:04 AM. The idle tick `@0x08007570` shows frame 1 only when `(tick & 0xFF) > 0xF0`, so bolts baked into idle frames would look frozen.
3. Playable SSJ2 (set 159, post-Cell only via `flag:195`) uses the standard idle. Rage in the Cell fight becomes a gi SSJ2 with the power-pose idle (3:15 PM). The Rage art is in `art\gi_rage\`, an unchanged copy of the r12 gi_ssj2_v2 with its manifest.
4. Set 159 idle (anim 0) only: its slots take the standard-idle mockups `art\golden\work_r3\idle_std\ssj2_std_d0..d3.png` (the SSJ2 golden head on the SSJ golden idle body). Add them as goldens `golden_gi_ssj2std_d0..d3.png`. The 4 goldens `golden_gi_ssj2_d0..d3.png` become the Rage (set 160) idle goldens: never edit them. Point the lock checks and tests that tie them to set 159 at set 160 or gi_rage, and say how. No other frame of set 159 changes.

## Part A: gi Rage set

1. Build set 160 (gi Rage) from `art\gi_rage\` with `build_set`, in the layout of set 58 (armor Rage), in `gohan_gi.py` (extend the set table copy to id 160).
2. Find every place the Cell fight selects Rage's sprite: `ext 73 (0, 58)` at `@0x083EA369` (script), the Rage appearance entry and anything else that names `set:58` for the player Gohan. Prove each site with the script bytes or code and a quoted listing. Repoint them to 160. NPC or cutscene uses of set 58 that are not the playable Rage stay as they are; list them.
3. Rage stats, EP behavior and the ability lock stay exactly as vanilla. Prove no form code changed.
4. Portraits: Rage's portrait (entry 4, ids 61/12) is out of scope unless the gi SSJ2 portrait (ids 117/118) is a one-line swap; report which, do not change it without saying so.

## Part B: aura in the frames

1. Port the outline family into `scripts\permanent\art\gi_aura.py` (from `aura2\bolts.py`, same rules: no bolt over the face box, white over a bright pixel becomes blue 191, index 2 white core, 191 glow). Do not port the cross family or the `mix.py` trim. Deterministic (fixed seed), tests for the face rule and that the output for my three reference shapes matches `aura2_outline_d0..d2.gif` on the same body (or report each difference).
2. Apply it to set 159 (playable SSJ2) and set 160 (Rage), on the non-attack poses: idle (anim 0), walk (1), run (13), ki charge (4). Each walk and run frame gets its own shape (the game changes those frames every 8 game frames).
3. Idle: give anim 0 of sets 159 and 160 six records per direction: 2 bodies (the vanilla idle frame 0 and frame 1) times 3 bolt shapes, in that order (index = body * 3 + shape).

## Part C: the idle hook

1. A Thumb hook on the idle tick (`@0x08007570`, vtable `@0x08024BA0`; read how the vtable entries are stored, they are offsets from the vtable base): when the object's set pointer (obj+0x48) is set 159 or set 160, store obj+0x14 = body * 3 + ((tick >> 2) % 3), where body is the vanilla result (1 when `(tick & 0xFF) > 0xF0`, else 0). Every other set keeps the vanilla tick, byte for byte in behavior.
2. Follow the register, stack and lr rules of the existing patches (`ssj2_form.py` header and `re-forms.md` section 7). New patch file `scripts\permanent\patches\ssj2_idle.py` in the style of the others (`_expect` checks, `apply(rom, alloc)`, notes), run after `gohan_gi`.
3. Tests: emulate the hook (the existing test interpreter used by `test_ssj2.py` and `test_status.py`) for set 159, set 160, set 157 and a non-Gohan set across 512 ticks: the index sequence equals the formula for 159/160 and the vanilla sequence for the others; the record count of anim 0 in 159/160 is 6 per dir.

## Build and review

1. Whole suite plus new tests; `frame_lock.py check --golden` exits 0 (aura frames are new art, not golden edits; lock the aura-free bodies, not the aura frames).
2. New ROM `archive\builds\log2_poc_r13.gba` (r13 was never built), no env vars, the r12 patch list plus `ssj2_idle`. Copy the newest .ss1 to `log2_poc_r13.ss1`. For the .sav: if `test-data\saves\log2_lv40_cellgames.sav` exists when you build, copy it to `log2_poc_r13.sav`. Otherwise copy `log2_lv40_postcell.sav`. Never overwrite an existing .sav. Append the build line. Prove r13 differs from r12 only where this pass changes it.
3. Review: `rom_sheet.py` GIFs from r13 for sets 159 and 160 anims 0, 1, 4, 13 (all dirs), plus an emulated idle GIF (the hook's index sequence over 120 ticks at 60 fps) for 159 and 160 dir 0-2. Look at them yourself.
4. My test plan in the report: which save slot, how to reach SSJ2 (Z then Z2), what the idle and walk should show; for Rage, which save or state reaches the Cell fight (say if none exists, and how I get there).

## Parallel run

Another task rebuilds the test save at the same time. It edits `scripts\permanent\rom\log2_save.py` and its tests, `docs\research\re-save-format.md` and `test-data\saves\`, and it adds rows to `docs\RE-BIBLE.md` at its end.
- Do not touch those files.
- Keep every module the suite imports importable and green at each save. While you work, run only your own tests and the sprite and patch tests. Run the whole suite once at the end. If a save test fails then, report it, because it may be the other task's work in progress.
- Edit `docs\RE-BIBLE.md` only in your last step, and only your own rows.

## Limits

- Never write under `data\`. Never overwrite an existing ROM or .sav in `builds\`. Never edit `art\golden\golden_*.png`.
- No palette change. Install nothing. Python files: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. Review images on (191, 255, 7), never gray.
- If a Rage site or the vtable form cannot be proven, stop that part and report instead of guessing.

## Report

Save it as `docs\tasks\2026-10-18-aura-rage\aura-rage-report.md`: Rage sites with proof, set 160 offsets, hook listing and the vtable entry, the aura rules (file:line), test count, r13 SHA-1, review paths, my test plan. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r13 SHA-1, the test count and concerns only.

