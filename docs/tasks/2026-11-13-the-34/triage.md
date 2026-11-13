# The 34: one row per failure, classified from its own assertion text

Evidence is the suite's own output, run 2026-11-13 at 4:10 PM, 2102 tests, 0 skips.
Nothing here is carried over from the earlier Fable and Grok consult. That consult said
"33 of 34 are stale pins". The evidence says 32, and it misread two behaviour failures
as address rot.

## Group 1: a pinned SHA-1 (12 rows)

Every row reads `'<hash>' != '<hash>'`. The test types a hash that a later build changed.

| Test | File:line |
|---|---|
| `test_beam_struggle.test_before_and_the_rom_are_pinned` | test_beam_struggle.py:149 |
| `test_beam_struggle.test_on_r39_alone_it_is_the_trial_rom_the_owner_played` | test_beam_struggle.py:156 |
| `test_celljr_fight.test_before_and_the_dev_master_are_pinned` | test_celljr_fight.py:374 |
| `test_chapter_cards.test_before_is_r40` | test_chapter_cards.py:285 |
| `test_fullpower_hud.test_before_is_r39_plus_relay_cooldown` | test_fullpower_hud.py:89 |
| `test_gi_base_audit.test_before_is_the_dev_master` | test_gi_base_audit.py:92 |
| `test_golden.test_dev_builds_to_its_pinned_sha1` | test_golden.py:102 |
| `test_golden.test_golden_builds_to_its_pinned_sha1` | test_golden.py:98 |
| `test_relay_cooldown.test_before_is_r39` | test_relay_cooldown.py:92 |
| `test_sprite_lab.test_the_dev_list_still_rebuilds_to_the_dev_master` | test_sprite_lab.py:69 |
| `test_vegeta_19_reveal.test_before_is_r40_plus_chapter_cards` | test_vegeta_19_reveal.py:106 |
| `test_vegeta_ssj_scene.test_before_and_r40_are_pinned` | test_vegeta_ssj_scene.py:204 |

**Fix:** one shared constant per master, and the trial rows compare MODULE LISTS, not hashes.
Do NOT read the expected hash from the build log. A build compared against the log that same
build writes proves nothing. Re-pinning must stay a deliberate one line act.

## Group 2: an address that moved (14 rows)

The allocator is a bump allocator over one free region, 0x800000 to 0xF00000. A module that
grows moves everything allocated after it. These tests type the address instead of asking.

| Test | Evidence |
|---|---|
| `test_fullpower_hud.test_every_other_case_equals_r39` | KeyError `'0xffff'` (reads fill bytes) |
| `test_fullpower_hud.test_stretch_gohan_shows_yellow_at_the_ep_fill` | KeyError `'0xffff'` |
| `test_fullpower_hud.test_hud_entry_uses_the_hud_draw_frame` | `'ldr r3,=0x0890a11d' not found` |
| `test_fullpower_hud.test_r39_hud_draw_frame_matches_the_entry` | reads `.hword 0xffff` x4 |
| `test_fullpower_hud.test_r39_words_are_the_vanilla_enter_and_the_pool_hud` | `143700405 != 143696111` |
| `test_fullpower_hud.test_a_changed_source_byte_refuses_before_writing` | `ValueError not raised : rom:0x90A12C` |
| `test_roundtrip.test_a_changed_chunk_table_is_reported_even_when_the_pairs_match` | raises in webfoot_decompress.py:154 |
| `test_roundtrip.test_a_document_carries_the_chunk_table_it_was_read_from` | `143698220 != 143702804` |
| `test_roundtrip.test_apply_refuses_a_document_whose_chunk_table_this_rom_has_not_got` | names 0x0890BB14, ROM holds 0xFFFFFFFF |
| `test_roundtrip.test_map_14_4_loads_a_chunk_that_its_private_table_alone_holds` | `168 != 0` |
| `test_roundtrip.test_the_dev_build_really_gave_map_14_4_a_private_chunk_table` | `143698220 != 143702804` |
| `test_vegeta_zplus.test_a_stray_namer_of_the_table_raises` | word 0x0888DC54 named at rom:0x90B368, "no patch allocated" |
| `test_vegeta_zplus.test_the_table_moved_and_every_namer_followed` | address list differs at the tail |
| `test_piccolo_z_start.test_the_patch_writes_four_runs_and_none_of_them_is_save_code` | `(..., 9482380) != (..., 9478140)` |

**Fix:** read the address from `alloc.notes[<module>]`, which every patch already records.
Each converted test needs a MUTATION CONTROL: move the patch's write in a scratch copy and
confirm the test still fails. A test that reads its expectation from the patch it is testing
proves only that the patch agrees with itself.

**Correction to an earlier note:** `test_a_changed_source_byte_refuses_before_writing` was
called a design decision. It is not. The guard did not fire because the address it watches
moved, so it belongs here.

## Group 3: compares against a frozen ROM in builds\ (6 rows)

All six are `test_bf_hud`. They compare a fresh build against r38 and r39 files on disk.

| Test | Evidence |
|---|---|
| `test_every_v2b_run_has_its_counterpart` | `143700405 != 143698303 : 0x2409c` |
| `test_mockup_files` | `4276 != 2084` |
| `test_r38_to_r39_files_differ_at_the_named_sites_only` | a long list of 0x909xxx sites |
| `test_r39_file_equals_the_build` | 57 MB of byte difference |
| `test_r39_is_v2b_relocated` | 57 MB of byte difference |
| `test_v2_to_r39_is_the_state_46_word_and_stub` | run list differs |

**These cannot be made to pass by rebuilding.** The frozen files are the ROMs the owner played.
No core edit can keep a historic ROM reproducible, and overwriting a ROM is a hard rule here.
This group needs a decision, not a code change. OWNER QUESTION.

## Group 4: real behaviour, not address rot (2 rows)

| Test | Evidence |
|---|---|
| `test_battle_start.test_form_survives_the_leader_change` | see below |
| `test_piccolo_z_start.test_the_base_and_non_pool_forms_still_get_nothing(entry=10)` | `50346496 != 0`, which is `0x3003A00`, an IWRAM address |

The Goku row is self describing, and the test already names the cause:

> record rom:0x89A9C0 (table rom:0x3DE6F4 word 32, map 9,3 region, fullpower_ssj) runs
> appearance(character=4, set=61), entry 20, before leader(2), so appearance_revert undoes it

Map 9,3 is the Time Chamber region. The record sets Goku's appearance BEFORE the leader
change, and `appearance_revert` then undoes it. This is the form loss the owner sees.

The Piccolo row returns an IWRAM pointer where it must return 0, so `pool_ref` hands the ki
pool to a form that should get nothing. Check `git log -S` against the Vegeta Z+ work before
calling it a bug: it may have been made a pool form on purpose.

## Counts

12 + 14 + 6 + 2 = 34.
