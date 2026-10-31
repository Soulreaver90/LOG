# r19: Rage text says Super Saiyan 2, plus a small frame intake (final, 2026-10-19 7:44 AM)

Personal GBA ROM hack (Legacy of Goku II, USA). Base: r18 (`builds\log2_poc_r18.gba`, SHA-1 046e51ec). Read first: `docs\tasks\2026-10-18-r18-intake\r18-intake-report.md` (intake mechanism), `docs\RE-BIBLE.md` section 8 rows on cutscene records (`{u8 seq, 0, u8 type, payload}`, type 1 = portrait byte then text) and section 5a row on record types, two patch files in `scripts\permanent\patches\` for style.

## Task 1: new patch `patches\rage_text.py`

Me: "It says Gohan has entered Super Saiyan Rage, can we change it to Super Saiyan 2? Maybe Super Saiyan 2 on the next line."

Facts I checked in r18 (verify each with `_expect`):
- The record is at `rom:0x3EA388`: `1E 00 01 00`, then the text `40 5E` + "Gohan has entered Super Saiyan Rage!" + `00`, then one `00` pad. The next record starts at `rom:0x3EA3B4` (`1F 00 01 28`, Cell's "You wretched child!!!").
- Each record has its own pointer in the scene list: `rom:0x3EA474` holds `0x083EA388`, `rom:0x3EA478` holds `0x083EA3B4`.
- `0x0B` is a line break inside text: Cell's next line uses it ("You wretched child!!!" `0B` "NOW TASTE MY TRUE POWER!!!").
- It is the only ASCII copy of "Super Saiyan Rage!" in the ROM.

8:05 AM wording: "Gohan has transformed into Super Saiyan 2!" New text: `40 5E` + "Gohan has transformed" + `0B` + "into Super Saiyan 2!" + `00` (45 bytes). Each line is at most 21 characters; the vanilla box showed 23 on one line.

It does not fit the old space (`rom:0x3EA38C`-`0x3EA3B3`, 40 bytes). So relocate the record: write a new record `1E 00 01 00` + the new text into the expansion area through `alloc` (4-aligned), and change the scene list word at `rom:0x3EA474` from `0x083EA388` to the new address. Leave the old record bytes as they are. `patches\npc_gi.py` already relocated three scene records this way; follow its method and its notes.

Before writing it, confirm from the type 1 handler (`@0x0800B438`) and the box (`@0x0800B1E2`) that the reader takes the record only through that pointer, reads text up to the first `00`, and handles a record outside the script region (the npc_gi precedent says it does). Check that no other word in the ROM points at `0x083EA388` (I found only `rom:0x3EA474`). Use `scripts\one-time\2026-10-18-disasm-study\listing.py` to read code by name. If any check fails, stop and report instead of patching.

Tests: the old record untouched, the new record bytes, the pointer word, the next record and its pointer untouched.

## Task 2: frame intake

Take in from a new snapshot `art\hand-fixes\snap_r19\` (copy `out\` and `edits.py` first) every key whose frame differs from its current golden. Expected: 158.12.0.1, 158.12.0.2, 158.12.0.3 (4 armor-gray boot pixels recolored to shoe and pants, r18 concern 1). Same mechanism as r18: new golden files only, lock updated, `check --golden` exits 0, the hand frame test baseline moves to r18.

## Build

- Build `archive\builds\log2_poc_r19.gba` from the r18 patch list plus `rage_text`, no env vars. Do not add `file_select_dim` or any status screen patch; they wait for me.
- Copy `log2_poc_r18.sav` to `log2_poc_r19.sav`. Never overwrite. Append the build line.
- **my save states (7:47 AM: "make sure the save states I made are compatible").** I made `log2_poc_r18.ss1`, `.ss2` and `.ss3` (7:32-7:41 AM) in `builds\`. Copy each to the r19 name (`log2_poc_r19.ss1` to `.ss3`); never edit or overwrite the r18 files. Then prove compatibility:
  - Parse each state (mGBA 0.10.5 format; it may be a PNG with the state in a chunk, possibly compressed). Show that the game title and game code stored in it equal r19's cartridge header (r19 must not change the header), and report the stored ROM CRC32 against r19's.
  - Show that r19 changes no code that a state holds in RAM (IWRAM code copies, hook stubs) and no RAM layout: r19 differs from r18 only in ROM data that is read at use time.
  - Say what I will see when loading a state made before the change: text or frames already in RAM or VRAM at save time show the old version until the game reloads them (for example, until the next scene or animation).
- Prove r19 differs from r18 only at the pointer word `rom:0x3EA474`, the new record in the expansion area, and the frame data of the listed keys. List the diff regions.
- Review sheet `archive\2026-10-18-art-review-renders\r19_intake.png` (r18 row over r19 row, 6x, lime). Look at it.
- My test: Cell fight in slot 3; the Rage message should read "Gohan has transformed" then "into Super Saiyan 2!" on the next line.

## Parallel run

- A portrait task works in `art\portrait-sources\remaster\` and `scripts\one-time\2026-10-19-portrait-from-anime\`. A status screen task writes `scripts\one-time\2026-10-19-status-portrait\`, one new patch and its test in `scripts\permanent\`. Do not touch their files. Do not edit `docs\RE-BIBLE.md`; put bible rows in your report.
- Run your own tests while you work and the whole suite once before the build, from the `scripts\permanent` root. Report any failure in another task's files; do not fix it.

## Limits

- Never write under `data\`. Never overwrite a ROM or .sav. Never edit an existing `golden_*.png`. Do not edit `fix.py`, `view.py` or `edits.py`.
- Install nothing. Python: LF, no byte order mark, no em or en dashes. Never `cd`; absolute paths. A shell heredoc collapses backslashes: write files with Python (no heredocs, no `sed -i`), and check them for control characters.
- Scripts in your own folder `scripts\one-time\2026-10-19-r19-build\`.

## Report

Save it as `docs\tasks\2026-10-19-r19-build\r19-build-report.md`: the reader evidence, the patch (file:line) and test count, the frame keys, the r19 SHA-1, the diff proof and the review path. Label findings CONFIRMED, LIKELY or SPECULATIVE. Then reply with status, the r19 SHA-1, the test count and concerns only.

