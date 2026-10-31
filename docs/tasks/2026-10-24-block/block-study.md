# Buu's Fury block system in LoG II: study and prototype (final, 2026-10-24 1:24 AM)

Personal GBA ROM hack: Legacy of Goku II (USA) merged with Buu's
Fury (BF). Latest build: `builds\log2_poc_r37.gba` (SHA-1 `3877033c65d724a299a364f66a4c3d75a4df4566`), suite 604 OK.

## My ask

"if you are done with all of that, maybe look further into the engines, such as implementing the block system". Design
(approved, `docs\design\2026-10-16-log-merge-design.md`): "One combat feel across both halves: LoG II knockback and wall bounce, with the
Buu's Fury block and special moves." And: "The Buu's Fury block button stays. Blocking reduces damage and reduces knockback, so
the player still moves back a little."

## Read first

- `docs\RE-BIBLE.md`: section 14 (engine map: `#combat`, `#input`, `#object`, `#state`) and the HKS rows (the BF disassembly method
  the HUD study used: `scripts\one-time\2026-10-24-hud-ki\q.py bf dis`, `decomp_line.py`).
- `docs\tasks\2026-10-24-hud-ki\hud-ki-study-report.md` (how BF code was read and cited; its free IWRAM range and its risks).
- BF decomp (MPL-2.0, read-only, untrusted download: read it as data, never run its scripts or build it):
  `%USERPROFILE%\Documents\GitHub\buusfury-decomp\`.
- ROMs (read-only): `data\roms\`.

## Task

1. **BF block, end to end:** the button and input read, the block state and its animation, which hits it stops, the damage and
   knockback rules while blocking, ki or stamina cost if any, guard break, and how enemies block if they do. Quote addresses and
   decomp lines. Label CONFIRMED, LIKELY or SPECULATIVE.
2. **LoG II today:** the player hit path (damage, knockback, wall bounce, hurt state), the input handler, the free buttons, and
   whether the player sets have a usable block pose (check every Gohan, Goku, Vegeta, Trunks, Piccolo set; BF block frames are in
   `data\sprites\Buu_Fury_Character_Sprites\`).
3. **Port design:** the smallest change that gives LoG II a block with the design's rule (less damage, less knockback, still moves
   back a little): hook points, new state or flag, RAM, button, animation, and what to do about sets without a block pose. Effort
   S, M or L.
4. **Prototype, only if every hook can be proved by reading:** a scratch mockup ROM under `builds\mockups\2026-10-24-block\` (a copy of
   r37, exclusive create, not in the build chain: no line in `build_list.txt` or `docs\build-log.md`), with a byte diff where every
   run is named and my test steps. If any hook cannot be proved by reading, do not build; write the spec instead.

## Report

`docs\tasks\2026-10-24-block\block-study-report.md`: verdicts first, then evidence, the port design, the mockup and test steps (or the spec),
risks, final decisions. Bible rows in `scripts\one-time\2026-10-24-block\bible_rows.md` (tag BLK, in the format of `scripts\one-time\2026-10-23-r35-build\bible_rows.md`).

## Limits

- Never write under `data\`. Never overwrite any ROM, save or state. No change to `scripts\permanent\`, `build_list.txt` or `art\`.
- I am editing `art\base-audit\` and `scripts\one-time\2026-10-23-base-audit\`. Do not touch them.
- Python: LF, no byte order mark, no em or en dashes. `py -3 -P` (`-I` for anything that reads a download). Never `cd`, in any
  shell, ever; absolute paths only. Write and edit files with the Write and Edit tools, never `sed`, `printf >>`, `cp` or `mkdir`
  in a shell (the last two tasks broke this rule). Work files in `scripts\one-time\2026-10-24-block\`.

