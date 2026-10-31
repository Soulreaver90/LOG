# r20: Rage stats +20, status portraits match the dialog art, mid remaster portraits (me, 2026-10-19 8:44-9:00 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r19 (`archive\builds\log2_poc_r19.gba`; read its SHA-1 from `docs\tasks\2026-10-19-r19-build\r19-build-report.md`). Read first: `docs\RE-BIBLE.md` section 6 (form objects: base `@0x030021E0`, Rage `@0x030021E4`, vtable +0 apply stats), the headers of `scripts\permanent\patches\ssj2_form.py` and `status_bonus.py` (how playable SSJ2 gets +20 and how the status page shows it), `docs\tasks\2026-10-19-status-portrait\status-same-report.md`, and `scripts\permanent\re\` or `scripts\one-time\2026-10-18-disasm-study\listing.py` to read code by name.

## My ask (verbatim)

- "For consistency, maybe we drop the max stats and keep it as a +20 for the Cell [fight] right." Screenshot: Rage Gohan level 40 shows STR 70+30, POW 58+42, END 71+29 (each filled to 100).
- "The portrait is what I meant": in the same Rage form the status page shows the armor Rage portrait while the sprite is the gi.

## Task 1: new patch `patches\rage_stats.py`

- Find how the Rage form applies its bonus (form object Rage, vtable +0, and anything else that fills to max). Quote the code.
- Change it so Rage adds +20 to STR, POW and END, exactly the way playable SSJ2 does (same cap rule and the same status display through `status_bonus`). Keep every other Rage behavior (the sound, the aura, the forced form in the Cell script, HP/EP handling) unchanged unless it is part of the bonus.
- Say whether the change applies only to gi Rage (set 160) or to every Rage use; in this game Rage appears only in the Cell fight, so check for other users.
- Tests: the old and new bytes, and an interpreter run of the apply step for Gohan level 40 with base 70/58/71 that gives 90/78/91 shown as "+20".

## Task 2: add `status_portrait` to the build

- `patches\status_portrait.py` and `tests\test_status_portrait.py` exist (status-same task). Add the patch to the build list after `status_bonus`, as its report says. Its test once pinned an r18 SHA-1; make sure it passes with r19 as the base.
- My check it fixes: in Rage, the status page shows the gi SSJ2 portrait (117), the same art as the dialog.

## Task 3: the mid remaster portraits (9:00 AM: "mid is great")

- Put the five mid portraits into the ROM as the dialog art: Goku 63 `goku_mid_A.png`, Vegeta 106 `vegeta_mid_A.png`, Gohan SSJ 115 `gohan_ssj_mid_A.png`, Gohan SSJ2 117 `gohan_ssj2_mid_A.png` (fixed 9:05 AM: chest spot removed), Gohan base gi 119 `gohan_base_mid_A.png`, all in `art\portrait-sources\remaster\`. Copy them first to `art\portrait-sources\remaster\final_r20\` and use only those copies.
- Gohan's ids are written by `patches\gohan_portraits.py`; read how it reads its art and either point it at the new files or add a small patch after it. Goku 63 and Vegeta 106 are vanilla ids: a new patch `patches\portrait_remaster.py` writes them the same way. Every pixel index must be one the OBJ palette already has (version A: no palette change).
- With `status_portrait` in the build, the status page shows the same art; do not regenerate status twins. If `gohan_portraits` still writes twins, say whether they become dead data.
- Tests: each written portrait equals its PNG pixel for pixel when read back from the ROM.

## Build

- Build `archive\builds\log2_poc_r20.gba` from the r19 patch list plus `status_portrait`, `rage_stats` and the portrait patch(es), no env vars. Do not add `file_select_dim`.
- Copy `log2_poc_r19.sav` to `log2_poc_r20.sav`, and every `log2_poc_r19.ss*` I have to the r20 name. Never overwrite or edit the r19 files.
- State compatibility: show that a state from r19 loads (header title and code unchanged) and say what it will show: a state saved during Rage keeps the old stat values in RAM until the form is applied again; say exactly when that is.
- Prove r20 differs from r19 only at the patches' sites and data. List the diff regions.
- My test plan: the Cell fight from slot 3 and from my state; Rage status shows +20 on each stat and the gi SSJ2 portrait; the status page of other characters shows their dialog art; open an item sub-menu and check the menu colors.

## Parallel run

- A tools task writes `scripts\permanent\re\`, `tests\test_re_tools.py`, `scratch\ghidra\seeded\` and `scripts\one-time\2026-10-18-disasm-study\`. A toolchain task may write `%USERPROFILE%\Tools\` and `scripts\one-time\2026-10-19-toolchain\`. Do not touch them. Do not edit `docs\RE-BIBLE.md`; put bible rows in `scripts\one-time\2026-10-19-r20-build\bible_rows.md`.
- Run your own tests while you work and the whole suite once before the build, from the `scripts\permanent` root. Report any failure in another task's files; do not fix it.

## Limits

- Never write under `data\`. Never overwrite a ROM, .sav or state file.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Scripts in `scripts\one-time\2026-10-19-r20-build\`. Label findings CONFIRMED, LIKELY or SPECULATIVE.

## Report

Save it as `docs\tasks\2026-10-19-r20-build\r20-build-report.md`: the Rage bonus code and change, the tests, the r20 SHA-1, the states copied, the diff proof and my test plan. Then reply with status, the r20 SHA-1, the test count and concerns only.

