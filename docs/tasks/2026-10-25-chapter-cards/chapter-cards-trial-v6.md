# Chapter cards trial v6: card 5 moves to the Kami cut (final, 2026-10-30 10:40 AM)

Read `LOG\README.md`, `docs\tasks\global.md`, the v5
brief and report, `chapter-4-6-review-report.md`, the module `scripts\permanent\patches\chapter_cards.py` and its tests,
and the bible rows tagged CH5, CH6 and CHP.

## Final decisions

- Card 5 "A New Horror": "after Kami talks to Piccolo and saying how there is something else going on and then it
  transitions to Gohan and Trunks, it is already a transition with dialogue and a fade." That is the flag 129 point:
  SET 129 at `rom:0x3DF28F` (`00 81 02 1B`), fade 90 at `rom:0x3DF293` (`00 5A 02 28`), then the map load to 2,20 (the
  time machine). The card plays after the fade and before the map load. Continue flag for card 5 becomes 129.
- Card 4: on hold (I review gameplay footage). Keep the v5 card 4 as it is.
- Cards 1, 2, 3, 6, 7, 8: unchanged (2 and 3 confirmed "perfect" in play; 6 is at Imperfect Cell's line).

## Task

1. Move card 5: remove the v5 card 5 insert at the 127 fade (the record goes back to vanilla bytes) and insert the
   card at the 129 point. Update `CHAPTERS` (row 5 flag 129) and the tests: flags still rise, the 127 record equals the
   base, the new insert decodes, every record ends where its `next` word says. Note that table words before word 0 can
   hold a stray small word (CH6 trap row): decode from the real word 0.
2. Keep the clash check with the other trial modules and the r40 order rule (`relay_cooldown` before
   `chapter_cards`). A new trial module `vegeta_19_reveal` is being written now on the Android 19 table `rom:0x3D40C8`;
   make sure card inserts do not touch that table.
3. Tests green, full suite once at the end. `--list` gives r39 `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`.
4. Build `builds\mockups\2026-10-25-chapter-cards\log2_poc_r39_chapters_v6.gba` with a copy of
   `log2_poc_r39_chapters_v5_pre_b2.sav` as `log2_poc_r39_chapters_v6.sav` (exclusive create). Its slot 1 (Vegeta before
   the Android 18 fight) now leads to card 5 after the fight, the world map flight and Kami's scene. Give play steps.
5. Diff runs v5 to v6; all inside declared sites. Bible rows (tag CH7) as `## Section N` table blocks in
   `scripts\one-time\2026-10-25-chapter-cards\bible_rows_v6.md`.

## Report

`docs\tasks\2026-10-25-chapter-cards\chapter-cards-v6-report.md`: SHIPPED and PENDING tables, the card 5 insert (bytes
before and after), SHA-1s, diff runs, test counts, play steps. Label claims CONFIRMED, LIKELY or SPECULATIVE.

## Limits

- Python: `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`.
- Never write under `data\`. Never overwrite a ROM, save or state: exclusive create. LF, no em or en dashes. Never `cd`
  or `Push-Location`; absolute paths only. Scripts go in `scripts\one-time\2026-10-25-chapter-cards\`
  (names starting `v6_`).
- Do not edit any other module, its tests or any list. Another task writes `vegeta_19_reveal.py` and its own list now.
  A study task works in `LOG\zhack\`. I am editing `docs\RE-BIBLE.md` and `docs\ledger\`.

