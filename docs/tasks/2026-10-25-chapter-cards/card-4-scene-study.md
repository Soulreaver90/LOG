# Card 4: our own arrival scene at the Northern Mountains landing (final, 2026-10-30 6:45 PM)

Read `LOG\README.md`, `docs\tasks\global.md`,
`card-4-break-report.md` (the landing, the bit 211 guard, the arrival line notes), `chapter-cards-v6-report.md`,
`scripts\permanent\patches\chapter_cards.py`, our scene modules `vegeta_ssj_scene.py`, `vegeta_19_reveal.py` and
`celljr_fight.py` (actor spawn, fly, walk and text patterns), the r19 `rage_text` work, and the bible rows tagged CH8,
CHP, CH5, CH6, CH7, V19, VS4, VS5, K18, CJR, CJP, R40.

## My design (word for word, keep the dialogue text exact)

"When the player lands, fade to the card, then fade to the team flying in, the player to the farthest right. Team
consists of Piccolo, Krillin, Tien, Gohan, Vegeta and Trunks."

If Piccolo lands:
- Piccolo: "Now we better get moving, we don't have much time!"
- Tien: "Okay, let's do it." / "I'll head a little further north to see what I find out there."
- Everyone flies north except the player.

If Vegeta lands (6:49 PM, the full exchange; quotes and the "said Vegeta" narration removed):
- Vegeta: "Would you stop following me, boy?" / "You're getting on my nerves!"
- Trunks: "Sorry, but there's no way I am planning to let you fight the androids on your own!"
- Vegeta: "And just what are you planning to do to stop me? It's going to take more than that little sword of yours to
  stand in my way!"
- Trunks: "How many times do I have to tell you before it sinks into your thick skull? Never underestimate the power of
  the androids!"
- Vegeta: "Hah!" / "And never underestimate the power of a real super saiyan who loves to take on a challenge! Well, if
  you're going to stay, you can at least help me find Dr. Gero's lab!" (6:59 PM: the earlier "Hah!" line is
  right; only the words after "challenge!" are added)
- Exit (6:59 PM): everyone flies north except Vegeta, the same result as the other branches. Only the Vegeta
  branch has its own dialogue; Piccolo and Gohan share the Piccolo and Tien lines.
- Split each line into text boxes at the game's box limit; give the box splits in the report.

If Gohan lands: the Piccolo and Tien lines, the team flies off, Gohan is the farthest right. Only the sprite places change.

## Task (study only: no module, list or ROM change)

1. **Roster.** Which characters can lead at the landing (flags 86-90): read the party data and the save presets. For
   each possible leader, which branch plays. If a leader I did not name is possible (for example Trunks), say
   so and propose the Gohan branch as the default.
2. **Actors.** For each of the six: the NPC sprite set, whether it has fly rows (anim 12 for `ext 54`, or the `ext 121`
   rows we used), per direction, and the portrait id for the speakers (Piccolo, Tien, Trunks, Vegeta). Name every gap
   (no fly row, no portrait) with the cheapest fix from existing or official BF art. OBJ VRAM and actor count with seven
   actors on screen: compare with the largest vanilla scene.
3. **Trigger.** How the scene plays after the map loads, only the first time: the card 4 report says no script runs on
   arrival. Options: a map item on 8,1 with a condition, a script chained after ext 38, or another way. Prove the guard
   (bit 211 or a flag we own) and the order (the card before the map load, the scene after the fade in).
4. **Script.** A byte-level draft: fade out, card 4 (`push 4 ; ext 145`), map load with fade in, the team flies in
   from the south and lands in a row with the player farthest right, the text boxes per branch, the team flies north
   off the screen (Vegeta branch: same exit unless the report shows a reason not to), the actors are removed, control
   returns. Positions on map 8,1 from the landing point (272,128).
5. **Text.** How the new lines get in (the text record type, portraits, line breaks, length limits, the expansion).
   Keep my words; the only edit is "lets" to "let's".
6. **Continue.** Which flag Continue reads for card 4 (the card 4 report options a and c), and a test save plan (a slot
   with bit 211 cleared, via `log2_save.py`).
7. Risk, the work size, and a test plan.

## Report

`docs\tasks\2026-10-25-chapter-cards\card-4-scene-report.md`: SHIPPED and PENDING tables, the roster, the actor table,
the trigger, the script draft, my questions. Label claims CONFIRMED, LIKELY or SPECULATIVE with addresses. Bible rows
(tag C4S) as `## Section N` table blocks in `scripts\one-time\2026-10-25-chapter-cards\bible_rows_card4_scene.md`.

## Limits

- Read only, except your report, rows file and scripts in `scripts\one-time\2026-10-25-chapter-cards\` with names
  starting `c4s_`. Python: `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
  Never write under `data\`. LF, no em or en dashes. Never `cd`, `Set-Location` or `Push-Location`: absolute paths in
  every command, including scripts that open files.
- Another task edits `chapter_cards.py` and `tests\test_chapter_cards.py` (the fade fix, `fadefix_` files). Do not
  touch them, any patch module, `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.

