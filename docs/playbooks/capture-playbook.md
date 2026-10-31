# Capture playbook: see a build run without me

One page. How to capture a scene from a LOG build with no window, no click and no play test.

Tools: `scripts\permanent\emu\capture.py` (the wrapper), `scripts\permanent\emu\capture.lua` (the Lua side),
`scripts\permanent\emu\actors.py` (the RAM actor walk). Emulator:
`%USERPROFILE%\Downloads\BizHawk-2.11.1-win-x64\EmuHawk.exe`, GBA core `dll\mgba.dll`.

---

## Run a capture

1. Write a job file. Put a one-time job in `scripts\one-time\<date>-<task>\`.
2. Check it without launching anything:
   `py -3.14 -P scripts\permanent\emu\capture.py <job.txt> --dry-run`
3. Run it:
   `py -3.14 -P scripts\permanent\emu\capture.py <job.txt> [--run-dir <folder>]`
   The default run folder is `scratch\capture\<name>-<stamp>\`.
4. Read the actors out of the dumps:
   `py -3.14 -P scripts\permanent\emu\actors.py <run folder> <rom.gba> [dump tag]`

The run folder holds `result.txt` (one line a step), `shots\*.png` (240x160 native), the `*.bin` dumps,
`config.ini`, `steps.txt`, `run.lua` and `command.txt`.

## The job format

One key or step a line. `#` starts a comment. Use forward slashes in every path.

| Line | Meaning |
|---|---|
| `rom <path>` | the build to run. It must live under `builds\`, or the wrapper refuses |
| `seed <path>` | our 8192-byte `.sav`, copied in as BizHawk's SaveRAM |
| `speed <percent>` | only matters with `--throttled`; see "Speed" |
| `timeout <seconds>` | the wall-clock limit. The wrapper kills BizHawk when it passes |
| `name <word>` | names the default run folder |
| `wait <frames>` | advance that many frames |
| `press <button> <frames>` | hold the button for that many frames. A, B, Start, Select, Up, Down, Left, Right, L, R |
| `shot <name>` | write `shots\<name>.png` |
| `read <addr> <width> <label>` | up to 8 bytes goes in `result.txt`; wider goes to `<label>.bin` |
| `savestate <path>` | write a BizHawk state. The wrapper refuses a path that already exists |
| `end` | the last line. Every job needs one |

## The route to a story point

Boot to the title takes about 2100 frames. From there, with a seeded save:

| Step | Frames |
|---|---|
| `press A` at the title | the file select opens about 90 frames later |
| `press Down` once a slot, then `press A` | Continue runs, and the chapter card plays |
| the world map appears | about 1000 frames after that A press |
| `press A` on the map star | the landing scene starts |

The frames above are measured on `log2_poc_r40_chapters_v10.gba`. Re-measure with a strip job (a `shot`
every 10 to 120 frames) when the build or the save changes.

## Reading the actors

`actors.py` walks the world object list and gives each actor's spot, facing and sprite set.

- World object `0x03001120`: +4 count, +8 the active list of 128 pointers, +0x40C the second list.
- Actor object: +0x10 facing (0 down, 1 up, 2 left, 3 right), +0x48 the sprite set, +0x158 and +0x15C the
  anchor, so the world spot is the value shifted down 8 bits.
- The player object pointer is the word at `0x03001FA8`.
- The set id comes from the live set table that the ROM word at `rom:0x959C` names; entry i is set id i + 7.

A job that wants this must dump both regions:
`read 0x03000000 32768 iwram` and `read 0x02000000 262144 ewram`.

## Speed

> [!NOTE]
> The config key `Unthrottled` is what frees the speed, not `SpeedPercent` and not `client.speedmode`.
> `capture.py` sets it on every run, so a capture reaches about 900 to 1000 frames a second. A full route
> from boot to a story point costs about 8 seconds of wall clock.

`--throttled` keeps BizHawk's throttle, and then `SpeedPercent` rules: 400 gives about 237 frames a second.
Use it only to compare.

## Traps

> [!WARNING]
> **Never let BizHawk write inside its install.** A config copy alone does not stop it. `capture.py` points
> the GBA `Base` path entry at an absolute run folder and checks the install after every run. If a run
> reports install writes, stop and tell me.

- **`joypad.set` takes no controller number.** The GBA core has one controller and no `P1 ` prefix, so
  `joypad.set({A = true}, 1)` sets nothing and the game never sees the button.
- **`console.log` does not reach stdout under `--chromeless`.** `result.txt` is the only channel.
- **BizHawk cannot load an mGBA `.ss1` state.** `savestate.load` returns false on a file that exists.
  BizHawk `.State` files that this loop writes do load.
- **BizHawk names the SaveRAM file after the ROM with every `_` turned into a space**, so
  `log2_poc_r40_chapters_v10.gba` reads `log2 poc r40 chapters v10.SaveRAM`. A wrong name fails silently:
  the file select shows empty slots and Continue starts a new game.
- **A screenshot of a moving frame can be one frame out.** The RAM read is always exact. Two runs of the
  same job gave identical dumps and identical shots, but a throttled run differed from an unthrottled run
  by about 1000 pixels on frames where sprites were moving, and not at all on a still frame. Take the
  picture on a still frame.
- **A facing is applied after the actor reaches its spot, one actor at a time.** In the card 4 arrival the
  spots are final as the actors land, and the last facing lands four frames later. Find the first settled
  frame with a one-frame strip that reads each actor's byte at object +0x10, as `job_explore4.txt` does.
- **Never overwrite a save or a state.** `capture.py` refuses a `savestate` path that already exists.
- **An exit code of 0 does not mean the job worked.** `capture.lua` catches its own faults and exits
  cleanly, so check `# done ok=true` and the `end` line in `result.txt`. `capture.py` does that for you and
  returns nonzero when either is missing.
- **A timeout kills the run's own process tree by pid.** Never kill by image name: I may have
  BizHawk open, and another task may be capturing at the same time.
