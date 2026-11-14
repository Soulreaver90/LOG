# Suite baseline, 2026-11-13 7:38 PM Eastern

Ran 2121 tests. 21 failures, 1 expected failure, 0 errors.
Every failure below is known and is owned by other work. A failure NOT on this list is yours.

Five are the master SHA-1 re-pin, which happens once, later:

- FAIL: test_before_and_the_dev_master_are_pinned (tests.test_celljr_fight.ListTests.test_before_and_the_dev_master_are_pinned)
- FAIL: test_before_is_the_dev_master (tests.test_gi_base_audit.ListTests.test_before_is_the_dev_master)
- FAIL: test_dev_builds_to_its_pinned_sha1 (tests.test_golden.BuildTests.test_dev_builds_to_its_pinned_sha1)
- FAIL: test_golden_builds_to_its_pinned_sha1 (tests.test_golden.BuildTests.test_golden_builds_to_its_pinned_sha1)
- FAIL: test_the_dev_list_still_rebuilds_to_the_dev_master (tests.test_sprite_lab.ListTests.test_the_dev_list_still_rebuilds_to_the_dev_master)

Sixteen compare a fresh build against a frozen ROM file in builds. Group 3 owns them:

- FAIL: test_before_is_r38 (tests.test_bf_hud.BaseTests.test_before_is_r38)
- FAIL: test_every_v2b_run_has_its_counterpart (tests.test_bf_hud.EquivalenceTests.test_every_v2b_run_has_its_counterpart)
- FAIL: test_mockup_files (tests.test_bf_hud.EquivalenceTests.test_mockup_files)
- FAIL: test_r39_is_v2b_relocated (tests.test_bf_hud.EquivalenceTests.test_r39_is_v2b_relocated)
- FAIL: test_v2_to_r39_is_the_state_46_word_and_stub (tests.test_bf_hud.EquivalenceTests.test_v2_to_r39_is_the_state_46_word_and_stub)
- FAIL: test_r38_to_r39_files_differ_at_the_named_sites_only (tests.test_bf_hud.FileTests.test_r38_to_r39_files_differ_at_the_named_sites_only)
- FAIL: test_r39_file_equals_the_build (tests.test_bf_hud.FileTests.test_r39_file_equals_the_build)
- FAIL: test_new_space_follows_r38_and_skips_a_named_chunk (tests.test_bf_hud.PlacementTests.test_new_space_follows_r38_and_skips_a_named_chunk)
- FAIL: test_before_is_r36 (tests.test_chamber_spar.BaseTests.test_before_is_r36)
- FAIL: test_r37_file_equals_the_build_and_differs_from_r36_at_the_sites (tests.test_chamber_spar.DiffTests.test_r37_file_equals_the_build_and_differs_from_r36_at_the_sites)
- FAIL: test_r38_file_equals_the_build_and_differs_from_r37_in_type_25_stats_only (tests.test_chamber_spar.DiffTests.test_r38_file_equals_the_build_and_differs_from_r37_in_type_25_stats_only)
- FAIL: test_r32_file_holds_this_scene (tests.test_piccolo_gi_scene.DiffTests.test_r32_file_holds_this_scene)
- FAIL: test_r32_to_r33_is_the_name_only (tests.test_superperfect_cell.DiffTests.test_r32_to_r33_is_the_name_only)
- FAIL: test_r33_to_r34_is_the_name_string_only (tests.test_superperfect_cell.DiffTests.test_r33_to_r34_is_the_name_string_only)
- FAIL: test_r34_to_r35_is_the_text_its_pointer_and_the_stats (tests.test_superperfect_cell.DiffTests.test_r34_to_r35_is_the_text_its_pointer_and_the_stats)
- FAIL: test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only (tests.test_superperfect_cell.DiffTests.test_r36_file_equals_the_build_and_r35_differs_by_portrait_52_only)
