# Capture loop: see the game without me (final, 2026-10-30 11:00 PM: "the most unattended way possible")

**Read `docs\tasks\2026-10-30-tooling\capture-loop-findings.md`
first: it holds what I already proved by running BizHawk, so do not re-derive it.** Then read
`scripts\permanent\rom\log2_save.py`, `scripts\permanent\patches\chapter_cards.py` (the card 4 scene block only), and
`docs\tasks\2026-10-25-chapter-cards\card-4-scene-v10-report.md`. Search `docs\RE-BIBLE.md` for the actor record
layout before you read the ROM.

## Why

Every scene report this month ends "no emulator run, so every in-game claim is L or S". I pay for that with
a play test each time. This loop turns those claims into CONFIRMED before he is asked to look.

## Already proved, build on it, do not retest

- `EmuHawk.exe --config=<copy> --chromeless --lua=<script> <rom.gba>` runs with no window and exits 0 on `client.exit()`.
- The GBA core is `dll\mgba.dll`. Screenshots are native 240x160 RGB.
- **`console.log` does not reach stdout under `--chromeless`. A result file written with Lua `io.open` is the only channel.**
- `memory.read_u16_le`, `emu.framecount()` and `joypad.set({Start=true}, 1)` all work.
- **`savestate.load` on an mGBA `.ss1` returns false.** BizHawk cannot use my states.
- A config copy is not enough on its own. Set the GBA **`Base`** path entry to an absolute project path, or BizHawk
  writes into my install. Proved: an absolute Base left the install untouched.
- Boot to the title menu is about 2100 frames. It runs at real time, 3000 frames in 53 s.

BizHawk install (one constant, do not move it, do not modify it):
`%USERPROFILE%\Downloads\BizHawk-2.11.1-win-x64\EmuHawk.exe`

## Task

1. **`scripts\permanent\emu\capture.py`** (permanent): the wrapper. Takes a job file, writes a per-run scratch folder
   (config copy with an absolute GBA `Base`, the Lua script, the job, the outputs), launches BizHawk with a timeout,
   kills it if the timeout passes, and returns the exit code, the run time and the artifact paths. It must refuse to
   run if the job names a ROM outside `builds\`. **It never builds a ROM and never writes into the BizHawk install.**
2. **`scripts\permanent\emu\capture.lua`**: the Lua side. Reads the job (a simple line format or JSON you parse in
   Lua), runs its steps in order, and writes one result file. Steps to support, no more: `wait <frames>`,
   `press <button> <frames>`, `shot <name>`, `read <addr> <width> <label>`, `savestate <path>`, `end`.
   Every step appends a line to the result file with the frame number.
3. **Solve the speed problem.** It runs at real time today. Try `client.speedmode(<percent>)` and the config speed
   key. Report the fastest setting that still produces correct frames, with the measured frames per second. If neither
   works, say so plainly: the loop is still useful, just slow.
4. **Story-point states** (`tooling.md` item 4, now with a real job): a command that boots from a project `.sav`
   placed as `<rom name>.SaveRAM`, drives input to a named story point, and writes a **BizHawk** state there. First
   prove BizHawk reads one of our 8192-byte `.sav` files at all: that is untested. Build states for the story points
   the current trials need. If input driving proves unreliable, report it rather than fake it.
5. **Acceptance test, the one that proves the loop is real.** Capture the card 4 arrival scene of the already built
   `builds\mockups\2026-10-25-chapter-cards\log2_poc_r40_chapters_v10.gba` on all three branches: a screenshot of the
   row, plus each actor's position and facing read from RAM. I have already play tested that exact ROM, and my
   screenshots are in this session, so the loop's output must agree with what I saw. Put the three PNGs and the RAM
   table in the report. **This is the gate: if the loop cannot reproduce a scene I have already seen, it is not
   working.**
6. **Tests**: unit-test the wrapper logic only (job parsing, the config rewrite, the refusal on a ROM outside
   `builds\`, the timeout path). **No test may launch an emulator.** A suite that needs a desktop session is not
   unattended.
7. **`docs\playbooks\capture-playbook.md`**: one page. How to run a capture, the job format, the traps above.

## Report

Short. `docs\tasks\2026-10-30-tooling\capture-loop-report.md`: SHIPPED and PENDING tables, one usage line per tool,
the measured speed, the three acceptance screenshots and the RAM table, the test count, and a plain answer on whether
BizHawk reads our `.sav` files. Label every claim C, L or S. Bible rows (tag CAP) as `## Section N` table blocks in
`scripts\one-time\2026-10-30-capture-loop\bible_rows.md`.

## Limits

- Create new files under `scripts\permanent\emu\`, `scripts\one-time\2026-10-30-capture-loop\` and the one playbook.
  You may edit `scripts\permanent\rom\log2_save.py`. **Touch no patch module and no build list.**
- Never write inside the BizHawk install. Never write under `data\`. Never overwrite a ROM, save or state: check
  absence, then create. Python: `py -3.14 -P`.
- Never `cd`, `Set-Location` or `Push-Location`. Use absolute paths in every command and in every script that opens a
  file. This was broken by the last two tasks: do not repeat it.
- Do not touch `docs\RE-BIBLE.md`, `docs\ledger\`, `zhack\` or anything under `builds\` except by reading. Do not. Do not run the full suite.

