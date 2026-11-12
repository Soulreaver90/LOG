# The Super Saiyan ki pool is not refilled by a scripted transform

The owner, 2026-11-09, after play-testing `builds\mockups\future\future_v3.gba`: "and his ssj ki is
still not reset. When he transforsm against cell, it keeps the wasted ssj ki from the android
battle."

Agent report, verified by the controller. No ROM was built: the owner said "Hold for the next
rebuild".

---

## The cause

`bf_ki_pool` keeps the Super Saiyan pool at RAM `0x03003A00`: `+0` the pool, `+2` a tag
`0x8000 | leader << 8 | entry`. It FILLS the pool in state 35 (the player's own transform) and
EMPTIES it in state 36 (revert). A tag that does not match also fills it.

**The finale does neither.** `plateau.transform()` changes Trunks with `ext 73`, an appearance swap,
which never enters state 35 or 36. `code_0800a8ec.s` calls the player state vtable `+0x28` with
`MOV r1,#0x0`, so neither `fill_end` nor `empty_end` can run from a script op. `bf_ki_pool` hooks
the form vtable `+4` (tick) and not `+8` (enter), so the form enter does not fill it either.

**And the tag matches, so the mismatch path does not save it.** The tag's `entry` field is the
appearance ENTRY INDEX, not the set id (bible B0418, B0423, B0468). Entry 15 is `set:132` and entry
16 is `set:133`, confirmed against the live appearance table `rom:0x88DC54` and the reverse lookup
copy `rom:0x800000`.

The real sequence, decoded from the built plateau trial:

| Where | Op | Effect |
| --- | --- | --- |
| ending word 0 `rom:0x9408D8` | `ext 73 (3,132)`, `ext 70 (3)` | Trunks leads, entry 15 |
| ending word 4 `rom:0x940990` | `ext 73 (3,133)` | fights BOTH androids in entry 16; tag becomes `0x8310`, pool drains |
| ending word 13 `rom:0x94064C` | `ext 73 (3,132)` | back to base for the Cell fight; `pool_ref` takes `ref_none`, which does NOT touch the tag |
| plateau word 3 `rom:0x946A5C` | `ext 73 (3,133)` | computed tag `0x8310` equals the stored tag, so no refill |

A second case the original root cause did not cover: if the player transforms by input in round 1,
`fill_end` rewrites the same tag `0x8310`, and the finale still matches it.

## The fix

New trial module `scripts\permanent\patches\pool_refill.py`, 80 bytes of Thumb, on
`build_list_trial_plateau.txt` **between `plateau` and `finale_blast`**.

It wraps the live `ext 73` table word, the way `relay_cooldown` wraps `ext 70`:

1. read the leader's appearance entry (`0x03000E90 + 0xC + 28 * leader`, `+8`);
2. call the vanilla handler `0x0800A8ED` through `bx r3`, keeping `r0` and its result;
3. read the entry again;
4. **only when it changed**, write 0 to the tag at `0x03003A02` and call `bf_ki_pool`'s `pool_ref`.

The "entry changed" gate is the part that matters. Zeroing on EVERY `ext 73` would refill the
leader's pool whenever a cutscene changes a non-leader's body, and `future_androids` word 0 runs
exactly such a call.

Pointer-level only, and in this placement it changes **zero base-ROM bytes**: both sites are in the
expansion area. `bf_ki_pool.py` and `build_list_core.txt` are untouched, because either would move
every later allocation and both masters' pinned SHA-1s.

**Placement is a trap.** With `pool_refill` AFTER `finale_blast`,
`test_finale_blast.test_the_ext_table_copy_is_the_live_table_plus_one_word` fails: the two builds put
the wrapper at different addresses. Before `finale_blast` is correct.

## Proof

Same assertion, two trees:

```
FAIL: test_A_current_tree_without_pool_refill
AssertionError: Tuples differ: (5, 33552) != (120, 33552)
  (pool, tag); expected the full pool 120
ok:   test_B_with_pool_refill
```

`test_pool_refill.py` carries 14 tests, including both halves of that proof and three negative
guards: entry unchanged, non-leader changed, and leaving the form. `test_only_the_word_and_the_wrapper_change`
walks all 16 MB and proves the only changed ranges are the 4-byte table word and the 80-byte wrapper,
so the player transform, the revert and the drain are byte equal.

Controller's own run: `test_pool_refill`, 14 tests, OK.
Agent's full suite: 1929 tests, 1 failure, which is the known pre-existing
`test_battle_start.test_form_survives_the_leader_change`.

## NOT read or verified

- **No play test and no ROM build.** The owner's eye has not seen this.
- The real `ext 73` handler never ran: the test interpreter stubs it at `0x0800A8EC`. Its
  disassembly was read, the dispatch was not executed.
- The `fullpower_ssj` stretch is reasoned, not tested: inside it `pool_ref` takes `ref_none`, so the
  hook leaves the tag 0 and nothing refills until the stretch ends. No test covers it.
- The HUD repaint after a refill is not exercised.
- **The blast-radius scan is incomplete.** Of 87 raw `02 49` hits in the two script regions, about
  half decoded to a `(character, set)` pair, and an `ext 73` with run-time arguments would not appear
  at all. `cellgames_ssj`, `vegeta_ssj_scene` and `celljr_fight` were not traced site by site.
- The "before" ROM in the proof is the current tree minus `pool_refill`, not `future_v3.gba`
  (`89eaa1dd`) which the owner actually played.
- **The masters still carry the defect.** A scripted `ext 73` into a pool form refills nowhere in
  `build_list.txt` or `build_list_dev.txt`. Moving `pool_refill` into `build_list_core.txt` is a
  separate decision and needs new `GOLDEN_SHA1` and `DEV_SHA1` pins.
