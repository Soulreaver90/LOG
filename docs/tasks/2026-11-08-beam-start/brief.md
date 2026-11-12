# Brief: move the beam's start to Trunks' hands, three periods, and the transition length

The owner played `finale_poses_wip1.gba` and said: **"the current version is perfect, trunks is
holding his pose"**. The poses are DONE. Do not touch them. Three narrow fixes only.

Read first: `docs\tasks\global.md`, then this brief. Files you will edit:
`scripts\permanent\patches\finale_blast.py`, `scripts\permanent\patches\ending_fight.py`,
`scripts\permanent\patches\plateau.py`, and their tests.

---

## Job 1: the beam starts at Trunks' feet. It must start at his hands.

His words, with a screenshot: "it needs to start where trunks hands are, right above it" and
"overshooting cell is fine, thats how it is in vanilla aginst perfect cell, the complaint is the
starting position of the beam, that is all".

**Overshooting Cell is CORRECT. Do not shorten the beam. Do not move either fighter.** The only
defect is where the beam begins.

### Measured by the controller

- The firing frame, header `0x36AE4C`, is 16x32 at dx 0, **dy -24**. Its raised hands occupy roughly
  rows 3 to 10 of the frame, so **about 22 px above the actor's own point**.
- The beam's dir 1 (UP) run, gold set `0x08704604 + 96`, has a y extent of **dy -32 to +16** measured
  from the actor's own point. So the beam's bottom cap sits **16 px BELOW his feet**.
- The muzzle offset table `0x08701DF0` is 8 bytes per direction and **dir 1 is (0, 0)**, which is why
  the beam spawns on the actor's point.

So the beam needs to move **up by about 36 px**. Treat 36 as a STARTING value, not a fact: he judges
by eye and will want to nudge it. Put it in ONE named constant with a comment saying what it is
measured against.

### Where to apply it

The gold op already owns a CLONED builder, a copy of `sub_0801D84C`, at `rom:0x94DAA0`, re-authored
instruction by instruction through `ssj2_form.assemble`. Apply the offset THERE. Do not edit the
vanilla muzzle offset table `0x08701DF0` and do not edit the vanilla builder: both are shared with the
blue beam, and Gohan's Cell Games Kamehameha must stay exactly as it is.

Prove in your report that the vanilla builder, the vanilla muzzle table and Imperfect Cell's own
`ext 137` record at `rom:0x3E147E` are byte identical to the base ROM after your change.

## Job 2: three boxes shipped with no terminal punctuation

He said: "the new dialogue is missing period punctuations". The controller decoded the build. Every
plateau and finale line already carries its period. **Only these three boxes end bare, both in the
ending records:**

| Where | Shipped | Write this |
| --- | --- | --- |
| word 12 box 1 | `I wish I could say that it's all over` | `I wish I could say that it's all over.` |
| word 12 box 2 | `but there is one more thing that has to be done` | `But there is one more thing that has to be done.` |
| word 22 box 1 | `If you can get past me, then you can get to the past` | `If you can get past me, then you can get to the past.` |

Note word 12 becomes TWO sentences, so `but` becomes `But`. That is the consequence of the period he
asked for, not a re-wording. Everything else in both records stays exactly as it is, including
`... Cell` and `But I won't let you!`.

Measure every box afterwards with
`scripts\one-time\2026-11-08-dialogue-typos\measure_lines.py`'s model and confirm none passes 4 lines
or the 294 px the ending talk already renders.

## Job 3: the transition is still too long, because we made it longer

He said it twice, then asked "what is the normal transition length in vanilla???".

**The controller measured it.** `scripts\one-time\2026-11-08-finale-poses\vanilla_transition_census.py`
walks every map-owned scene table and totals the blocking frames between each `fade_out` and its
`fade_in`. Over the **17 map-load transitions** the walk reaches:

- median total black **240 frames, 4.02 s**; most common value 240 (5 records)
- range 60 to 600 frames
- **only 3 of 17 carry ANY wait between the fades; the median wait is 0**

So deleting `LOAD_SETTLE` was right and must stay deleted. But raising the fades to 120/120 made the
transition 240 frames, where the previous build was 30 + 120 + 30 = 180. **We made it 60 frames
SLOWER than the version he was already calling too long.**

**Use vanilla's own FASTEST map-load transition instead: `rom:0x3E424A`, `fade_out(30)`, no wait,
`fade_in(30)`, 60 frames, 1.0 second.** It is a real vanilla record, so this still follows his rule
"the game has loads of transitions, find out the length of time, and thats what we use".

Apply it to BOTH hand-offs, `plateau.split()` and `ending_fight.arrive()`. Keep the staging ops
between the load and the fade in, which is vanilla's shape and costs nothing extra.

**One thing to check, not assume:** the previous agent reported that `ext 57 (28, 3)` blocks for 64
frames and called it the load margin. With a 30 frame fade that block is now the largest single piece
of the black. Read it, say what it costs, and say whether the load is still covered.

---

## Build and verify

- Build from `scripts\permanent\build_list_trial_plateau.txt` to
  `builds\mockups\future\beam_start_wip1.gba`. **Never overwrite an existing ROM**: if that name
  exists, use the next number. Never touch `build_list.txt` or `build_list_dev.txt`.
- Run the full suite ONCE at the end, redirected to a file. Never pipe a test run into head or tail.
  `test_battle_start.test_form_survives_the_leader_change` is a known red that predates this work.
- Bank bible rows in `docs\tasks\2026-11-08-beam-start\rows.md` as `## Section N` table blocks, tag
  `BST`. Do not edit `docs\RE-BIBLE.md`.

## Hard rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`. Never `py -3`.
- Never write under `data\`. Never overwrite a ROM, save or state: check absence, then create.
- Never put a Windows path inside a Python string literal in `python -c` or a heredoc.
- No em dashes or en dashes in any output.
- Never re-word his dialogue beyond the exact table above.
- Do not read or write inside `art\Owner Build - Trunks Tank\`. That is his live art.
- **Do not touch the poses.** He called them perfect.

One report message, then stop. Do not add a byte order mark.
