# Study: turn the Future Trunks cutscenes into playable 1 v 1 boss fights

The owner wants Future Trunks to FIGHT Android 18, Android 17 and Cell, one on one, at the points where
the game currently plays a cutscene instead. This is a STUDY. Decide whether it can be done, and how.
Write no patch and build no ROM.

## Read these first, in this order

1. `docs\RE-BIBLE.md` section 8 (story and script) and section 4 (sprites). Search it before the ROM.
   Rows already relevant: post-fight EXP per boss (`ext 139`), the boss bar sites (`ext 85` full bar,
   `ext 90` segmented), the Android 18 death table `rom:0x3D98AC`, and the Trunks form entries.
2. `scripts\permanent\patches\celljr_fight.py`. THIS IS THE PRECEDENT and the method to copy. It already
   converts scripted scenes into a staged fight by copying a scene record, redirecting a table word, and
   spawning actors. Read its header block and its `Method:` notes.
3. `scripts\permanent\scene\scene_probe.py` to print a table or a record, and `scene_lib.py` for the VM.

## Answer these, in order

**Q1. Which of the three is already a real fight, and which is only a cutscene?** The bible records
`ext 139` EXP awards for Android 18 (8000, `rom:0x3D8BC4`), Android 17 (15000, `rom:0x3E4B6C`) and
"Perfect Cell vs Trunks" (40000, `rom:0x3E7110`). An EXP award implies a fight happened. Say for each
one WHO fought it in vanilla, because the owner's ask only makes sense for the ones Trunks does not
already fight himself.

**Q2. Is Trunks the player at each of those story points?** A 1 v 1 needs Trunks controllable. Report
the leader and the party at each point, and whether the engine lets the leader be forced. Note that
`celljr_fight` works because Gohan is already the leader there.

**Q3. For each of the three, name the exact scene table, the record, and the seq that plays the
cutscene.** Give addresses. Say which record would be copied and which table word redirected, in the
same shape as `celljr_fight`'s notes.

**Q4. What blocks each one?** Be specific and concrete. Likely candidates to check rather than assume:
the boss descriptor and HP for each set, whether set 9 and set 11 have the animations a fight needs
(the bible says `set:11` has anims 0-8 and 12 only), hurtbox rows, whether a loss is scripted as part
of the story, and whether any story flag gates progression on the cutscene finishing a certain way.

**Q5. Recommend an order.** Which of the three is cheapest to build first, and why.

## Rules

- Label every claim CONFIRMED (address plus bytes or disassembly), LIKELY, or SPECULATIVE. Code is only
  ever built on CONFIRMED.
- Absolute paths. Never `cd`. Python is `py -3.14 -P`. Never write under `data\`.
- Put any listing you print in `scripts\one-time\2026-11-05-trunks-boss-fights\`.
- Write the report to `docs\tasks\2026-11-05-trunks-boss-fights\report.md`, and a
  `bible_rows.md` beside it as `## Section N` table blocks for anything new you confirm.
- Run no test suite. Build no ROM. Change no file outside the two folders named above.

One report message, then stop. Do not add a byte order mark.
