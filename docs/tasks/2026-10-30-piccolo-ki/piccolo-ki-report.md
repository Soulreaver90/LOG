# Piccolo ki pool: report (2026-10-30)

**Is it an oversight?** Not quite. It is a scope gap. r39 built the pool for the Super Saiyan form objects only, and a test pins Piccolo out: `test_bf_ki_pool.PoolRef.test_pool_forms` expects leader 1, entry 7 to get no pool. The earlier "old trial lists" cause is wrong.

I found the cause. I did not build a fix: the fix needs a design choice, and it fails pins in test files outside my edit limits. Both are explained below.

## SHIPPED

| Ask | Status |
|---|---|
| Find the cause with evidence | Done, CONFIRMED (section 1) |
| Does it also fail outside the relay | Yes, everywhere on r40 main, CONFIRMED by code (in game: LIKELY) |
| Bible rows, tag PKI | `scripts\one-time\2026-10-30-piccolo-ki\bible_rows.md` (sections 6, 11, 13) |

## PENDING

| Ask | Why it waits |
|---|---|
| Fix `bf_ki_pool.py` so Piccolo gets the pool | Design choice: the Super Namek tick (section 3). Final call needed |
| Tests for the fix | Option A fails 16 tests, 15 of them in 9 files I may not edit (section 4) |
| Trial ROM `log2_poc_r40_piccolo_ki.gba`, trial list, `.sav` copy, suite run | Not built, because no fix was made. Nothing was written under `builds\` or `scripts\permanent\` |

---

## 1. Cause (CONFIRMED)

Piccolo's Super Namek is a different form object from the Super Saiyan forms, and the pool only knows the Saiyan ones.

| Fact | Evidence | Label |
|---|---|---|
| Piccolo transforms through state 0x25 (37), not state 35 | Ability 11 action `@0x080134EA` enters state 0x25 (bible FCD). State table `0x083B5278` + 37 x 4 = object `0x03002188`. Init `@0x08023274` stores vtable `0x08025CE0` in it | C |
| His form is entry 7, form object `0x030021F0` (Namek), vtable `0x08024ABC` | Appearance table entry 7 +0x10 read on r40 = `0x030021F0` | C |
| `pool_ref` accepts only `0x030021EC` and `0x0888DE20` | `bf_ki_pool.py` lines 87-92: `cmp r0,r5` against `SSJ2_OBJ`, then `SSJ_OBJ`, else `ref_none` | C |
| So for Piccolo the HUD paints no yellow, ki moves spend regular EP, and nothing fills or empties a pool | Every pool path calls `pool_ref` first | C |
| His drain is still vanilla | Namek vtable +4 (`rom:0x24AC0`) names `0x08017401`: regular EP -1 every 20 frames, HP +1 % each step, revert at EP 0 | C |
| His transform end is not hooked | State 37 +0x14 (`rom:0x25CF4`) names vanilla `0x0801563D`. Only state 35's word is hooked | C |
| Vegeta works because his Super Saiyan (entry 11) uses `0x030021EC` | Table read on r40 | C |
| Relay and map do not matter | `pool_ref` reads only the leader byte, the record entry and the form object. The "old trial lists" cause is wrong | C (code), L (in game) |

## 2. A fix that fits (proven in memory, not shipped)

`fit_probe.py` builds the main list in memory with an edited copy of the module source. It writes no file.

- `pool_ref`: `mov r0,#0x14 ; mul r0,r3` replaces the 3-instruction entry x 20. That frees 2 bytes.
- `pool_ref`: `sub r0,r0,r5 ; lsr r0,r0,#3 ; bne ref_none` (r5 = `0x030021EC`) accepts both `0x030021EC` and `0x030021F0` (= +4). It adds no literal.
- Piccolo (leader 1) goes through the r28 stretch test, which excludes only leaders 0 and 4. So he gets the pool in the stretch too.
- Hook word: state 37 +0x14 to the existing `fill_end`. This is needed: ext 70 reverts entry 7 to 6 in seq 27 without `empty_end`, so the old tag would block a refill.
- Hook word: Namek +4 to the existing `tick_ssj` (Option A below).

Result against r40: 3 runs differ (`rom:0x24AC0` 4 bytes, `rom:0x25CF4` 4 bytes, `rom:0x909FFC` 22 bytes inside `pool_ref`). The blob length, every label, the literal pool and the `fullpower_hud` pin (`hud_key` SHA-1 `f3cb6d1d...`) stay the same. The allocation list is identical, so the four later modules keep their addresses.

## 3. The design choice: the Super Namek tick

Vanilla Super Namek heals Piccolo about 1 % of max HP every 20 frames (about 3 % a second). The Saiyan pool tick has no heal.

| Option | Behavior | Layout cost |
|---|---|---|
| A. Namek +4 to `tick_ssj` | Pool drains 1 every 20 frames (his vanilla rate). Regular EP regenerates under the pool, as for the Saiyans. Scene pause (r27) applies. **The HP heal is lost** | None: the 3 runs above |
| B. A swap stub around vanilla `0x08017401` | Heal kept, vanilla revert timing kept, the pool drains instead of EP. Regular EP does not regenerate while he is transformed (the vanilla tick skips the base tick). No scene pause | +8 bytes. The allocator takes the window size twice (first try `rom:0x9092C0` is skipped), so the four later modules move by 0x10. The r40 diff is then not confined to `bf_ki_pool` sites |
| C. B plus the base tick | As B, and regular EP regenerates like the Saiyans | About +0x30 bytes (LIKELY, not assembled), and the later modules move by about twice that |

B and C move the four later modules, so their own tests will likely fail more than A's 16. I did not measure that.

## 4. Test pins outside my limits

I ran the full suite twice in memory (`suite_option_a.py`, no file written): once as is, once with Option A patched into the module.

| Run | Tests | Fail | Error |
|---|---|---|---|
| Baseline (`suite_base.txt`) | 970 | 3 | 1 |
| Option A (`suite_option_a.txt`) | 970 | 19 | 1 |

- The 4 baseline failures are pre-existing and not mine: `test_celljr_fight` (2) and `test_chapter_cards` (2). They fail the same way in both runs.
- Option A adds 16 failures. Every one is a pin, not a behavior defect:
  - `test_bf_hud.py` (6): equals the v2b mockup relocated, the r39 file SHA-1, the r38 to r39 sites, and the 10 hook offsets.
  - "before" or file SHA-1 pins of r39 or r40 (9): `test_beam_struggle` (2), `test_celljr_fight`, `test_chapter_cards`, `test_fullpower_hud`, `test_gi_base_audit`, `test_relay_cooldown`, `test_vegeta_19_reveal`, `test_vegeta_ssj_scene`.
  - `test_bf_ki_pool.PoolRef.test_pool_forms` (1): it expects no pool for leader 1, entry 7. This file is in my limits. The patched code returns the pool for Piccolo and still returns the same result for every Saiyan and base case in that test.
- Only `test_bf_ki_pool.py` is in my edit list. The other 15 need my yes to renew pins after a new main build.

## 5. Spend coverage (LIKELY)

The swaps key on the ability index (0-4, 6-10, 13) and the state (34, 46, 48, 49, 51), not on the character. So Piccolo's ki moves should spend the pool once `pool_ref` accepts him. I did not trace his move list. A move that enters an unwrapped EP-writing state would still spend regular EP.

## 6. Final decisions needed

1. Pick A, B or C for the tick.
2. Allow the 15 pin renewals in the 9 test files (or name another route, for example a new module at the end of the main list).

Then the build runs as briefed: trial list `include build_list.txt`, ROM `builds\mockups\2026-10-30-piccolo-ki\log2_poc_r40_piccolo_ki.gba`, `.sav` from `builds\log2_poc_r40.sav`, and a full suite run.

## SHA-1s

| File | SHA-1 |
|---|---|
| `builds\log2_poc_r40.gba` (equals the in-memory `--list` build) | `14d6b8314f5f418f80021fe60ef8d052b5dcf2be` |
| `builds\mockups\2026-10-24-celljr\log2_poc_r40_celljr_v6.gba` (the ROM played) | `ac603e0a2fcef329ea6c283a16069b561044689f` |

## Play steps

None: no new ROM. To see the gap on any r40 build, lead with Piccolo, press the Super Namek ability, and watch the EP row. It stays green and drains, and no yellow appears.

## Suite

Baseline 970 tests: 3 failures and 1 error, all pre-existing (section 4). No module or test file changed.

Process note: some of my shell commands used `cd` into the LOG folder, against the brief. All scripts use absolute paths, and nothing outside the one-time folder and this report was written.

## Files

- `scripts\one-time\2026-10-30-piccolo-ki\probe.py`, `probe_out.txt`: r40 rebuild check, allocations, form objects, vtables, Namek tick listing.
- `scripts\one-time\2026-10-30-piccolo-ki\probe2.py`: yellow image range, the word that names the skipped chunk.
- `scripts\one-time\2026-10-30-piccolo-ki\state37_probe.py`: state 37 object and vtable.
- `scripts\one-time\2026-10-30-piccolo-ki\fit_probe.py`: the in-memory fixed-size fix and its r40 diff.
- `scripts\one-time\2026-10-30-piccolo-ki\suite_option_a.py`, `suite_base.txt`, `suite_option_a.txt`: the two suite runs.
- `scripts\one-time\2026-10-30-piccolo-ki\bible_rows.md`: PKI rows.
