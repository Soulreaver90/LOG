# Brief: the owner's finale dialogue, his music picks, and the transition cut

You build the owner's own words and music into the future Trunks finale, and you shorten the long
black transition he complained about. You do NOT touch the finale blast or Cell's death: another
agent owns those.

## Read first, in this order

1. `docs\tasks\global.md` - the standing constraints. They all apply.
2. `docs\design\2026-11-08-finale-dialogue.md` - **this is your spec.** His lines are quoted exactly.
   Do not improve his wording, fix his typos, or re-punctuate. Ask nothing; build what it says.
3. `docs\RE-BIBLE.md` - search it before you search the ROM. Search for what you are BUILDING, not
   only for background: captions, `ext 49` music, fade and transition ops, the ending records.

## The files you own

- `scripts\permanent\patches\plateau.py` - the plateau arrival and talk. Section 4 of the spec.
- `scripts\permanent\patches\ending_fight.py` - the ending records. Sections 1, 2, 3 and the cut.
- `scripts\permanent\tests\test_plateau.py` and the other tests those two modules own.

## What to build

Work section by section through the spec's sections 1 to 4, plus the transition cut in the
"Build state" section near the end. Every value you need is in the spec. In particular:

- Section 2 asks for a NEW caption box, "Three years later...", dismissed by a button, with
  **track 42**. The spec notes `@^Three years later...` may already exist at `rom:0x3B8610`.
  **Measure that before you build it.** Say in your report whether you reused the vanilla string and
  its dismiss mechanism, or built a new record, and why.
- `... Cell` gets its own box. That is settled in the spec.
- Music: **track 42** on the caption, **track 28** when the Capsule Corp battle starts, **track 35**
  when the plateau fight starts. He changed 15 to 35; 35 is correct.
- The transition cut: four values, each with its precedent, in the spec's table.
  **Do not touch `REC13_SETTLE` (`wait(120)`).**

## Two traps

1. **His map is already copied in and audited.** `art\plateau\map_142.json` is his live file byte
   for byte. **Do not copy it again and do not edit it.**
2. **`test_no_over_layer_was_blanked_and_bg1_really_stands_over_him` will go red**, because his
   cliff edit changes the BG1 count that test pins at 477. This is expected and is not a defect.
   Build first, read the REAL measured number, then update the constant and the docstring to it.
   Never reach the number by trying values. Also fix the stale numbers in the plateau docstring:
   1100 is now 1109, 4987 is now 4988, 4848 is now 4849, and 139 is unchanged.
   **If `bg0` is anything but 0, that IS a defect: report it, do not update it.**

## Width check

Each of his new lines must render inside the dialog box. The widest free segment the talk has been
seen to render is 294 px. Measure every new line. If one is over, insert `\x0b` after the speaker
tag so it wraps, and say in your report which lines you wrapped and how wide each one was.

## Build and verify

- Build list: `scripts\permanent\build_list_trial_plateau.txt`. Unchanged; add no module.
- Build to a SCRATCH name under `builds\mockups\future\`, something like `future_v3_wip.gba`.
  **Do NOT name anything `future_v3`.** The controller names and ships the final ROM.
- Run the full suite ONCE, at the end, after your edits are finished.
  `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests -t <LOG>\scripts\permanent`
  **Never pipe a test run into `head` or `tail`**: the pipe reports the pipe's exit code and a red
  suite reads as green. Redirect to a file instead, and quote the real exit code.
- `test_battle_start.test_form_survives_the_leader_change` is ALREADY red and predates your work.
  Leave it. Say so in your report. Any OTHER failure is yours.
- Verify your own claims out of the BUILT ROM, not out of your plan: decode each record you wrote
  and quote the ops.

## Rules that bite here

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`.
- No em or en dashes in any file you write. No byte order mark.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- Label every reverse-engineering claim CONFIRMED (with address and bytes or disassembly), LIKELY or
  SPECULATIVE. Build only on CONFIRMED.

## Deliverables

- The code changes, building green apart from the one known failure.
- `docs\tasks\2026-11-08-finale-dialogue-build\report.md` - what you built, the measured widths, the
  caption decision with evidence, the old and new BG1 numbers, and anything you could not do.
- `docs\tasks\2026-11-08-finale-dialogue-build\rows.md` - new bible rows, as `## Section N` table
  blocks, tag `FDB`. Follow the row shape in the bible's section 1.

One report message, then stop. Do not add a byte order mark.
