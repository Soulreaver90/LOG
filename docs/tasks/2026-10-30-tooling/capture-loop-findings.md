# Capture loop: what I proved by running it (2026-10-30 11:00 PM)

Every line below comes from a run on this machine, not from documentation. Labels: C = CONFIRMED by my own run,
L = LIKELY, S = SPECULATIVE. Probe scripts and output: a scratch folder outside the project, `bizprobe\`.

## The headline

BizHawk 2.11.1 runs a Lua script to completion with no window, no dialog and no click, and exits by itself.

```
EmuHawk.exe --config=<our copy> --chromeless --lua=<script.lua> <rom.gba>
```

Four runs, every one exit code 0. The script ends with `client.exit()`. (C)

## Confirmed by run

| Fact | Evidence |
|---|---|
| The GBA core is `mgba.dll` | `dll\mgba.dll` in the install. So captures match my own emulator (C for the file, L for pixel equality) |
| Screenshots are native GBA size | `client.screenshot(path)` gives 240x160 RGB PNG (C, Pillow read) |
| Lua can return data | `io.open(...)` writes a result file (C). **`console.log` does not reach stdout under `--chromeless`**, so a file is the only result channel (C) |
| Memory reads work | `memory.read_u16_le`, `emu.framecount()` (C) |
| Input works, **but not the way I first wrote it** | `joypad.set({Start=true})` with **no controller number**. The GBA core has one me, so `joypad.set({...}, 1)` sets nothing at all. My original line here claimed the `, 1)` form worked and labelled it C. That was WRONG: my probe sat on the title screen for ten blocks and I read the menu appearing on its own as proof of input. Corrected by the capture-loop task, which lost four runs to the same mistake (C) |
| Full boot to the title menu | About 2100 frames: Atari, Webfoot, the Piccolo and Vegeta attract, Super Saiyan Goku, title, then START and OPTIONS (C, 10-shot contact sheet) |

## Three findings that shape the design

**1. BizHawk cannot load my mGBA save states.** `savestate.load()` on a real `.ss1` returns **false** (C).
**My original evidence for this was invalid and I had labelled it C.** My probe's path walked six `..` out of the
scratch folder, which leaves the project tree, so it loaded a file that does not exist, and a missing path also
returns false. The claim happened to be true; my test did not show it. The capture-loop task retested against an
`.ss1` it first proved exists, and separately showed a BizHawk `.State` returns true. So the loop cannot start from any existing `.ss1`. It must either drive input from
boot, or build its own BizHawk states once. That is the `tooling.md` "story-point saves" item: make it emit BizHawk
states, and no hand-made state is ever needed again.

**2. A config copy alone does not keep writes out of my install.** BizHawk rewrites its config on exit and
normalises path entries. Redirecting each `Save RAM` and `Screenshots` entry in our copy still left
`<install>\GBA\SaveRAM\log2 poc r40.SaveRAM` behind (C). Setting the **GBA `Base` entry** to an absolute scratch path
fixed it: the next run put nothing in the install (C, `find -newer` came back empty). Every run must use a config copy
whose GBA `Base` is absolute and project-owned.

**3. Speed: solved, and not by the key I guessed.** My run was real time, 3000 frames in 53.3 s, about 56 fps (C).
I guessed the fix was `client.speedmode` or a speed percent. Both are wrong. The key is **`Unthrottled`**: throttled
at 400 percent gives 237 fps, unthrottled gives about 1000 fps whatever the percent (C, capture-loop task). A cold
boot to the card 4 scene now costs about 8 seconds.

## mGBA stays useful

mGBA 0.10.5 is my own player and reads my `.ss1` states. Its documented API has `Core.screenshot`,
`Core.loadStateFile`, `Core.runFrame` and the `Core.read*` family, but it has **no `--script` command line flag**
(C: I read `--help` on both `mGBA.exe` and `mgba-sdl.exe`), so it needs one click per session. Use BizHawk for
unattended work and mGBA when a run must start from one of his states.

## .NET

Not a gap. The machine has the .NET 10 Core, AspNetCore and WindowsDesktop runtimes, and all four BizHawk runs
returned 0 (C). .NET Framework 3.5 belongs to BizHawk 1.x and is not needed here.

## Left behind, needs my word

My first run, before the Base fix, created `<install>\GBA\SaveRAM\log2 poc r40.SaveRAM`. It is my artifact and I have
not deleted anything inside my install. Say the word and I remove it.

Unrelated, and my own: `<install>\GBA\SaveRAM\log2 poc r40 celljr v8.SaveRAM` and a config write, both at
10:27 PM, from his own BizHawk session with the Cell Jr v8 ROM.

## Corrections after the capture loop was built (2026-10-31, me)

Three lines above were rewritten. Two of them were mine and were labelled CONFIRMED when they should not have been:
the `joypad.set` my number, and the `.ss1` test whose path left the project tree. The lesson is the one the
project rules already state: a probe proves nothing until you show it finds a file that exists. I have also verified
the loop myself: `test_capture.py` is 31 tests OK in 0.08 s with no emulator, and the three captured card 4 branches
match my own mGBA screenshots from my play test, which is the comparison the task could not make because
those images were never on disk.
