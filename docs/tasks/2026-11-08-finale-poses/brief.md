# Brief: hold the finale poses, split Cell's line, and land the locked text fixes

The owner play-tested `finale_blast_wip3.gba` and rejected the poses. You are fixing that, plus a
set of dialogue text corrections he has already approved word for word.

**Read first, in this order:**

1. `docs\tasks\global.md`
2. `docs\design\2026-11-08-finale-dialogue.md` **section 7**, which supersedes section 5. It holds his
   words, the measured root cause, and the frame identity table.
3. `docs\ledger\queue.md`, the two sections dated 2026-11-08 for the typo pass. The table headed
   **"HIS DECISIONS, 2026-11-08: the final text, locked"** is the exact text to write.
4. `docs\RE-BIBLE.md` rows B0149, B0688, B0750, B0751, B0111. Search the bible before the ROM.

Files you will edit: `scripts\permanent\patches\finale_blast.py` (the poses and Cell's line),
`scripts\permanent\patches\plateau.py` and `scripts\permanent\patches\ending_fight.py` (text only),
and their tests.

---

## Job 1: the poses

**The measured fact that causes both defects.** State 30 is NOT a held pose. Its tick
`@0x0801CB24` (bible B0149) shows frame 0 for 8 ticks, then ALTERNATES frames 1 and 2 every 8 ticks,
for ever. `ext 137` forces the shooter into state 30.

What the owner wants:

1. **Cell holds the charge.** Set 28 anim 18 dir 0 **frame 0**, the cupped-hands Kamehameha charge,
   held with no flicker for the whole beat. He NEVER fires and never reaches the release frames.
2. **Trunks shows exactly two held frames**, set 133 anim 4 dir 1:
   - **index 2, header `0x36AD44`, hands DOWN** first, while he speaks;
   - **index 3, header `0x36AE4C`, hands UP**, HELD for the entire beam.
   No anim 4 cycling. No anim 18 sword slash. The controller rendered the rows and confirmed index 2
   is down and index 3 is up. The wip3 report said the opposite; it was wrong.

**Two rows you may NOT quietly clone**, because this same build reaches both:

- `set 28 anim 18` is Imperfect Cell's own vanilla Kamehameha at `rom:0x3E1484`, map 10,20.
- `set 133 anim 18` is Trunks' sword special, used in the future androids fight that
  `future_androids` ships in this build.

**Prove which rows this build actually reaches before you change any art.** If a row is reached by
another live scene, do not change it: clone a finale-only SET instead (`log2_sprites` clones a set
with replaced frames) or find a row this build never drives. State your proof in the report with the
addresses you read.

Design the hold however the engine allows. Your constraint is the owner's eye, not a mechanism: the
two Trunks frames must be static while they show, and Cell's charge must not flicker or advance.

## Job 2: split Cell's line

`Kamehame...` becomes TWO boxes: `Kame..` then `hame..`. He wants it tense and drawn out. Trunks then
interrupts with `THE NIGHTMARE IS OVER CELL!` while Cell is still charging.

Measure both boxes with the dialog model in `scripts\one-time\2026-11-08-dialogue-typos\measure_lines.py`
and keep them inside 4 lines and the 294 px the ending talk already renders.

## Job 3: the locked text fixes

Write the text in the queue's locked table EXACTLY. It is his approved wording, including the two
vocative commas he chose and the trailing punctuation he refused. Do not re-word anything, do not add
punctuation he did not take, and do not "fix" his phrasing.

Re-run `measure_lines.py` after the edit and confirm every box still fits. One line is already at
exactly 144 px, the line limit: say in your report whether it still fits.

---

## Build and verify

- Build the trial ROM from `scripts\permanent\build_list_trial_plateau.txt` to
  `builds\mockups\future\finale_poses_wip1.gba`. Never touch `build_list.txt` or `build_list_dev.txt`.
- Run the full suite ONCE at the end, redirected to a file. **Never pipe a test run into head or
  tail**: the pipe reports the pipe's exit code. Quote the exit code from the run itself.
- `test_battle_start.test_form_survives_the_leader_change` is a known red that predates this work.
  Every other failure is yours.
- Bank bible rows in `docs\tasks\2026-11-08-finale-poses\rows.md` as `## Section N` table blocks,
  tag `FPS`. Do not edit `docs\RE-BIBLE.md` yourself.

## Hard rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`: agents share the working folder.
- Python is `py -3.14 -P`. Never `py -3`.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- Never put a Windows path inside a Python string literal in `python -c` or a heredoc. Write a `.py`
  file and pass paths as arguments.
- No em dashes or en dashes in any output.
- Never re-word the owner's dialogue.
- The owner's `art\Owner Build - Trunks Tank\` folder is his live art. Do not read from it, write to
  it, or delete anything in it.

One report message, then stop. Do not add a byte order mark.
