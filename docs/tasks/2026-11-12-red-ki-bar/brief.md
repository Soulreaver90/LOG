# A red ki bar for a second transformation, and Z+ into the pool at all

Study and build in one run. Three jobs, in this order. Job 1 is the one the owner asked for.

## What the owner asked for

His words: "in buus fury, a second transformation adds a new more red ki bar over the base z yellow
bar. Right now Z+ reverts the yellow ki back to green. Can you look into the buus fury code for this
red ki bar (super saiyan 3 goku or gotenks) and see if we can port that?"

## Job 1: find Buu's Fury's red bar, and say how it is selected

Buu's Fury is `data\roms\Dragon Ball Z - Buu's Fury (USA).gba`, read only, loaded through
`patches.bf_hud.load_bf()` which checks its SHA-1. Never write to it.

What I measured myself, so do not re-derive it:

- The ki step table is `BF_KI = 0x08071F40`, 41 steps of 16 bytes, 4 words each. Its words are
  buffer offsets, 106 distinct ones, `0x0` to `0x486`.
- `bf_ki_pool.yellow_image()` builds the yellow bar as `bf[BF_YELLOW + o]` for each of those
  offsets, with `BF_YELLOW = 0x713AD8`.
- At those offsets the yellow image uses BF palette indices **26, 27, 28, 29, 30** and 0.
  `bf_hud.BF_TO_LOG2` maps them to our 41, 40, 46, 131, 123.
- **CORRECTED 2026-11-12. There IS a second bar image, at `BF_YELLOW + 0x500` = `0x713FD8`.**
  My first pass claimed there was none. That was a FALSE NEGATIVE of my own making: the sweep
  printed 933 candidates and named `0x713FD8` on line 887, and I piped it through `head -30` and
  read 26 lines before declaring a negative. Never cut an enumeration. The two images agree at
  1 of the 106 ki offsets and differ at the other 105, mapping BF index 26 to 107, 27 to 108,
  28 to 4, 29 to 109 and 30 to 110.

Find the real answer. Read the BF code that draws the ki bar and the code that picks its colour.
Report the addresses, say whether it is a second image, a palette swap or something else, and label
the finding CONFIRMED, LIKELY or SPECULATIVE. **If Buu's Fury turns out not to do this at all, say
so plainly.** That is a useful answer and the owner would rather hear it than a guess.

## Job 2: Z+ does not run the pool at all. That is why the bar goes green.

Measured by me in `builds\mockups\2026-11-12-vegeta-zplus\log2_zplus_v3.gba`:

```
Z   form object 0x030021EC  vtable 0x08024C58  tick 0x0890A06F  enter 0x0890A325   <- bf_ki_pool's
Z+  form object 0x030021E8  vtable 0x0802526C  tick 0x080171E5  enter 0x0801727D   <- VANILLA
```

`bf_ki_pool` hooks the Super Saiyan object only, because nobody had ever stood in the ascended one.
So in Z+ the vanilla EP drain runs and the EP row draws green.

`piccolo_z_start.py` solved exactly this shape for the Namek object `0x030021F0`: it taught
`pool_ref` to accept a second form object, pointed the vtable tick at `tick_ssj`, and pointed the
transform state's `+0x14` at `fill_end`. **Read that module first.** Its accept change is fixed size
on purpose, so no label, literal or later module address moves. Do the same for `0x030021E8`.

## Job 3: draw the pool RED while the leader is in a second transformation

Our OBJ palette carries a red ramp that mirrors the yellow one five for five, which I checked in the
built ROM:

```
yellow  41 #989800   40 #C8C800   46 #F8F838   131 #E0E878   123 #E0F8C8
red     25 #D01028   24 #F81838   31 #F84848    30 #F87070    29 #F89090
```

The whole OBJ table is legal to draw with (B0250), so no palette entry has to be written.

A SECOND transformation means Gohan's Super Saiyan 2 (`ssj2_form`'s object) and Vegeta's Z+
(`0x030021E8`). Plain Super Saiyan and Super Namek stay yellow. Decide the test by reading the form
object the leader holds, not by character.

If job 1 finds that Buu's Fury does it a different way, follow Buu's Fury and say why in the report.

## Scope

- `scripts\permanent\patches\bf_ki_pool.py` and its tests, plus a new trial build list if you need one.
- Do NOT touch `vegeta_zplus.py`, `piccolo_z_start.py`, the appearance table, `art_inject.py`,
  `portraits.json`, `build_list.txt`, `build_list_core.txt` or `build_list_dev.txt`.
- `bf_ki_pool` is in `build_list_core.txt`, so a change to it moves both master SHA-1s. Expect
  `test_golden.py` to fail on its pins, say so in the report, and LEAVE THE PINS ALONE.
- Build a trial ROM that includes `vegeta_zplus`, so the owner can see Z+ with the new bar. Pair a
  save. Never overwrite a ROM, save or save state: check absence, then create.

## Files to read first

- `scripts\permanent\patches\bf_ki_pool.py` : the pool, `pool_ref`, the HUD hook and `yellow_image`
- `scripts\permanent\patches\piccolo_z_start.py` : the precedent for adding a second form object
- `scripts\permanent\patches\bf_hud.py` : `load_bf`, `remap`, `t_bf`, `BF_TO_LOG2`, the step tables
- `docs\tasks\global.md` : the global constraints, which all apply

## Done means

1. A written answer to job 1 with addresses and a confidence label.
2. Z+ runs the pool: the bar is yellow or red, never green, and the pool drains.
3. The red bar shows for a second transformation and only for one.
4. Tests for each: the vtable words, the accept, and the colour choice per form object.
5. The trial ROM built, SHA-1 printed, its build log line IN YOUR REPORT, not in `docs\build-log.md`.
6. Bible rows in `rows.md` beside this brief, as `## Section N` table blocks.
7. A `report.md` beside this brief.

Do NOT run the full suite. Run your own test modules by name. I run the full suite here.

Report any place where my measurements above disagree with what you read. Deviate and flag it rather
than forcing the design onto a ROM that does not match.

One report message, then stop. Do not add a byte order mark.
