# Task 6 dispatch: usable Super Saiyan 2

Where this fits: slice 1 proof of concept for a personal LoG II ROM hack. Task 5 put Gohan's gi sprites into the ROM (sets 157-159). Task 6 makes Super Saiyan 2 a playable form.

## Read first, in this order

1. `docs\tasks\2026-10-16-task-6-ssj2\task-6-brief.md`: your requirements, with Global Constraints and Review Focus.
2. `docs\research\re-forms.md`, all of it, and section 7 above all: the confirmed approach, the patch sites with original bytes, and the Task 6 requirements (Rulings 15 and 16).
3. `docs\RE-BIBLE.md`: search it before you search the ROM.
4. `docs\ledger\progress.md`: Rulings 10-19, 31, 35 and 36 bind this task.

## Decisions from earlier tasks the brief cannot know

- **Set 159 offset.** `alloc.notes["gohan_gi"]["set_159"]` (Ruling 36). Set ids: 157 gi base, 158 gi Super Saiyan, 159 gi Super Saiyan 2. `ssj2_form` runs after `gohan_gi`. Entry 22 +1 = 159 (0x9F).
- **Appearance table.** `gohan_gi` already edited rom:0x1D96A5 (157) and rom:0x1D96E1 (158) in place. It also pointed rom:0x42F0 at an unchanged copy at rom:0x800000. Your relocated table copies the live (edited) table, adds entry 22, and leaves rom:0x42F0 alone (Ruling 14).
- **Stepping (Ruling 10).** Base to Super Saiyan as vanilla. Super Saiyan to Super Saiyan 2 only when flag 195 is set. Base never jumps to Super Saiyan 2. Speed as Super Saiyan, step EP cost 10 (Ruling 11; never below 9, Ruling 15). Revert from Super Saiyan 2 goes to base (entry 22 +5 = 2), as Super Saiyan does.
- **Z2 icon (Rulings 12 and 17).** Approved by me as drawn: `art\hud_z2_usable.bin` and `hud_z2_dim.bin` (raw 0x200-byte 32x16 8bpp). Do not redraw. Brief Step 3 is done. Show Z2 while Gohan is in Super Saiyan 2.
- **Lightning (Rulings 19 and 31).** The set 159 sprite already carries blue spark pixels in anim 4. Find whether Rage also uses a separate aura or effect object, CONFIRM it with addresses, and if Super Saiyan 2 should show it, use blue with existing palette indices. Rage stays unchanged. If the aura is a large separate system, report it as a concern with a cost estimate instead of building it.
- **Portraits (Ruling 13).** Entry 22 uses Rage's `3D 0C` until Task 7.
- **VRAM.** Set 159's slot is 0x400, the same as 157 and 158, so the step keeps a valid slot (Task 5 part 2 fact 2).
- **No assembler is installed.** Hand-encode Thumb, then verify every new routine by disassembly (Ghidra headless works through `scripts\one-time\2026-10-16-task-5-gi-art\gh.sh`, which sets JAVA_HOME). Entry to the expansion area only through absolute pointers, exit through local `bx` stubs. Never patch 0x080174A0 (shared Super Saiyan tick pool).

## Tests

Pass the brief's three tests, plus:
- END ceiling: 100 + bonus <= 127 for every playable form (Ruling 15).
- Every repointed literal (17 sites plus rom:0x1D99CC and rom:0x8E8C) holds the new value, and the old value existed before the write (fail closed, as `gohan_gi._expect` does).
- Every new routine disassembles to the expected instruction list (store the expected text in the test).
- The base 8 MB differs from the gohan_gi build only at the listed patch sites.

## Build and report

- Build `builds\log2_poc.gba` with `gohan_gi ssj2_form`. Log the SHA-1 in `docs\build-log.md`.
- Make my test save state plan, not a save state: list the steps I take in mGBA to test Review Focus 3 and 4 with `test-data\saves\log2_lv40_postcell.sav`, and the RAM addresses to watch (from the Task 4 report).
- Add RE-BIBLE lines for every confirmed fact. Use LF line endings in every file you write.
- Write `docs\tasks\2026-10-16-task-6-ssj2\task-6-report.md`. It covers status, confirmed facts with quotes, test count, SHA-1 and concerns.

Never write under `data\`.
