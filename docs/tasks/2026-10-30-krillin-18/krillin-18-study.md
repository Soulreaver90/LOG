# Krillin catches Android 18: scene plan (approved the idea 2026-10-30)

Read `LOG\README.md`, `docs\tasks\global.md`,
`docs\tasks\2026-10-29-design-ideas\design-ideas-report.md` (idea 1 and its note), the Cell Jr plan
`docs\tasks\2026-10-30-celljr-rework-plan\plan-report.md`, the guides in `docs\research\sources\guides-2026-10-29\`
(guide 1 lines 1230-1240), the modules `scripts\permanent\patches\vegeta_ssj_scene.py` and `vegeta_19_reveal.py` (our
scene copy and walk patterns), and the bible rows tagged CJR, CJP, CH6, VS4, VS5, V19.

## My words

"Krillin catches 18: yes." Today, after Gohan's kick makes Cell spit 18 out, the guide says "18 WALKS away... Krillin
doesn't go pick her up". In the show Krillin catches her.

## Task (study only: no module, list or ROM change)

1. Find the spit stretch on map 14,3: the record, the bytes, the text "He spit out Android 18!" `rom:0x3EA567`, how 18
   appears and walks off, where Krillin (`set:76`) stands, and what plays next.
2. Plan the catch with existing art only: Krillin moves to 18 (walk or the fly ext ops we used for Gohan, `ext 121`),
   a face turn, one or two short lines (I pick the words; offer 2 drafts from the show), both stand aside. Name the
   exact insert point, the copy-and-redirect method we use (copied record, one word changed), every op and its args.
3. Check what the later lines assume ("Great! And I'll take 18!" `rom:0x3EC1ED`) and any position 18 must hold later.
4. Conflicts: the Cell Jr rework also changes map 14,3 tables (relay tables, Gohan's table). List each shared table or
   record and say how the two modules can stack (order in the build list, disjoint words).
5. Risk and a test plan (unit tests on the copied record; a presave near the spit with `log2_save.py` if a slot can
   reach it; say which flag).

## Report

`docs\tasks\2026-10-30-krillin-18\krillin-18-report.md`: SHIPPED and PENDING tables, the scene as it is, the plan,
the conflicts, my questions. Label claims CONFIRMED, LIKELY or SPECULATIVE with addresses. Bible rows (tag K18) as
`## Section N` table blocks in `scripts\one-time\2026-10-30-krillin-18\bible_rows.md`.

## Limits

- Read only, except your report, rows file and scripts in `scripts\one-time\2026-10-30-krillin-18\`. Python:
  `py -3.14 -P`. LoG II base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`. Never write under
  `data\`. LF, no em or en dashes. Never `cd` or `Push-Location`; absolute paths only.
- Other tasks: r40 (edits `log2_build.py`, build lists, tests), a card 4 study and a style study. Do not touch their
  files, any patch module, `docs\RE-BIBLE.md`, `docs\ledger\` or `LOG\zhack\`.

