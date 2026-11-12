# Overnight report, 2026-11-05 into 2026-11-06

Written for the owner. Times are Eastern. Your cap of two agents at a time was held: never more than
two, and only one is still running as this is written.

---

## SHIPPED

| Your ask | What is on disk now |
|---|---|
| "Maybe this should be a unique map, a new one, no npcs, no exits or save point, just a battle arena / so a clone" | `builds\mockups\2026-11-05-ending-arena\log2_poc_r41_arena_v1.gba`, SHA-1 `d6348550` confirmed on disk, save beside it. Map 6,100 is a new 328th map table entry: combat on, no regions, no NPC list, one enemy item. `build_list.txt` is untouched. **Waiting on your eye.** |
| "continue the dissam? finish the function naming in the dissam? (maybe a local branch on here)" | Seven engine functions named on local branch `naming-2026-11-05` in `legacyofgoku2-disasm`. Never pushed, `master` untouched at `075b23c`, tree clean. I re-ran the behaviour tests myself: 35 passed, real exit 0, both new batches PASSED not SKIPPED. |
| "work on the sprites?" | `docs\design\plans\2026-11-05-sprite-suite-plan.md`, 833 lines, nine tasks. No code and no ROM, which is right: the gate was the plan. **It says the centre of your approved design is wrong, and I reproduced the measurement myself.** See below. **Six decisions are yours.** |

## PENDING, your call

| Item | Why it is yours |
|---|---|
| **The arena play test, 8 checks** | The one thing no measurement can close. The list is in the queue row and in the arena report, section 4. Check 7 matters most: walk through a few other zones, because the whole map table moved. |
| **A rule breach I am not hiding** | The naming agent ran the ARM toolchain out of `Downloads` to get the byte-exact gate, because the only ADS 1.2 on this machine lives there. Our rule says downloads are never run. I did not re-run the gate, so `GATE PASS` rests on that run alone. Your call on the weight it carries and whether the toolchain moves somewhere legitimate. |
| **An install to undo** | The agent installed cmake as a user package and it did nothing useful. `python -m pip uninstall cmake` when you want it gone. pytest stays, it is needed. |
| **The arena banner** | Map 6,100 still carries map 6,1's `+0x0C` value `0xBE`, which brings back the Capsule Corp banner you called a fault. `0xDD` is a value 5 vanilla entries already carry and is read as "no name", but that reading is LIKELY, not confirmed. One word, one play test. |
| **r41** | It is already in the working tree, uncommitted. The pins, `STATUS.md` and `CLAUDE.md` all agree on `acf1b15f` and `ffbd2bfc` and the suite is green. Only the commit and the scope are open. |

---

## The sprite design's central idea does not survive measurement

The design's affordability rests on one row: **letter the gold master once, project its naming onto
every other frame.** The design itself flagged that row as the one most likely to need a rethink. It
does. I re-ran both probes on the real down run frames and got the agent's numbers exactly.

**It is the worst available source.** The gold master idle accepts 26% to 33% of a run frame. The
nearest already lettered frame of the same phase accepts 70% to 76%.

**And it fails in the half that decides a swap.** Inside the garment mask, the only region a region map
decides:

```
pair                pool  accepted  accept%  letter%
run0 -> run2          42        19      45%      79%
run1 -> run3          34        18      53%      89%
side idle -> walk2    40         5      12%      80%
```

So 11% to 22% of what it accepts is **wrong**, carrying index `0x51` and saying torso where the truth is
arm. That is your second rejected down run draft exactly. The mechanism would have repeated the failure
it exists to prevent, with confidence. Outside the garment the same gate scores 96% to 100%, so hair,
face, trousers and boots come free.

The plan's answer: **project the structure, hand letter the decision.** The garment mask and both
frames' hands are refused outright. The gold master becomes the feature reference for Failure B, not the
region source. The eye bill falls from about 300 lit pixels a frame to 58 to 68.

Three more findings I checked:

- **The 32 wide blocker is one file.** Only `show_regions.py` hardcodes `W, H = 16, 32`, at line 29. I
  confirmed every other permanent tool already runs at 32 wide. The real cost is art: 174 of 288
  records, 60%, not the design's "half".
- **The one highlight rule cannot be written over colour.** A naive version flags 19 of 33 approved
  frames, because the guide already says a chest is not a limb. Section 7's constraint from a new angle.
- **The guide's known back idle defect repeats across the whole back row**, all four base walks and all
  four Super Saiyan ones. New fact, and the calibration fixture for the audit task.

### A real defect in one of our tools

`sprite_loop.py` exits 1 with `EOFError` whenever two consecutive frames are byte identical. Found at 32
wide; I isolated it and **the width has nothing to do with it**. On the approved 16 wide tank walk: four
different frames exit 0, two different frames exit 0, the same frame twice crashes. Pillow drops a
duplicate frame and extends its duration, so the decode check walks off the end of the GIF.

The decode check is that tool's whole point and a held pose is ordinary. Logged in
`docs\backlog\active-todos.md` with the reproduction and the cause. **Not fixed on purpose**: accepting a
shorter GIF would weaken the check, so the real fix has to map our frame index to the GIF's own and say
when the encoder collapsed a duplicate. That is not a change to make to a verification tool unreviewed
at half past midnight.

## The finding that changes how I work

`GitHub\legacyofgoku2-gnu\build\code` is a **stale** copy of the generated assembly, and `CLAUDE.md`
step 2 has been sending every session there, including me all night.

```
disasm 1476 files, 1244 starts
gnu    1333 files, 1094 starts
missing from the gnu tree: 154 function starts
shared starts 1090, bodies differ in 29   (the gnu file is LONGER in all 29)
```

It is longer because it bundles code the disasm repo has since split into its own function, so a read
there can hand a callee to the wrong function. I rewrote `CLAUDE.md` step 2 to point at the disasm
repo's own `build\code` and to state the measurement, and promoted the check to
`scripts\permanent\disasm\compare_code_trees.py`.

**Then I asked whether it cost anything tonight.** I listed all 15 functions this session reasoned from
and checked each. Fourteen are byte identical in both trees. The one that differs is `0x0800A784`, the
ext 70 handler, and only because the gnu copy bundles a second function behind it. **No conclusion of
tonight changes.**

## Three of our labels claim more than the code proves

The naming agent would not use our words, and it is right on all three. These are now bible rows that
separate what the body proves from what we assume.

- **ext 86 is not proven to be the HUD.** The body proves `Object_SetActive` on the character record
  bank and nothing more. The HUD reading is your eye, and may well be right.
- **ext 52's body does not prove a remove.** It allocates eight bytes, writes a method table and queues
  the block. What the queued job does sits elsewhere.
- **ext 104 is not "build item as enemy".** It proves a REPLACE: remove the selected sprite, spawn a map
  entry at that sprite's point and facing.

It also found that `0x08008952`, which I read as the player message handler, is **not a function
start**. `FUNCTION_BOUNDS.csv` carries it as unreferenced with a block limb and its first instruction is
`BGT` reading registers it never sets. I verified both census rows and the file. The real start is near
`0x080088E0`. The older bible row is annotated in place.

## The boss fight study, merged and checked

It had been sitting unmerged since 4:59 PM. 20 `TBF` rows are in. I decoded its load-bearing sites out
of the ROM rather than trusting it:

- Perfect Cell already forces Trunks: `push 3` at `rom:0x3E6E1D`, `ext 70` at `rom:0x3E6E1F`.
- Android 18's approach record `rom:0x3D8B38` arms a **real fight**: three removes, then `ext 84 (0)`,
  `ext 86 (1)` and `ext 90 (11,50,100)`.
- The party window: Trunks leaves at `rom:0x3B7ABA`, rejoins at `rom:0x3DF2A8`.

That last one **closes the open risk I flagged on the ending fight v2**: `ext 70 (3)` runs after his
rejoin, so it is safe. It also means he cannot lead Android 18's main-game fight, because she dies
before he rejoins.

## My own errors tonight, all caught before they reached you

1. **The rename broke the suite and I did not notice until the run finished.** Renaming `player_ptr` to
   `Sprite_CurrentDirectory` left `disasm\data\symbols.json` stale, and `test_re_tools` failed: exit 1
   on 1271 tests. Fixed through the GENERATOR, re-running `symbols.py json`, not by editing the output,
   because a hand fix gets reverted on the next run. Re-run is 1271 OK, exit 0, no pipe.
2. **My verification of the boss fight study was itself wrong first time.** My decoder helper stopped as
   soon as it had the number of ops I asked for, and I asked for one, so on every site beginning with a
   push it printed the push and stopped BEFORE the op it was meant to prove. I had already written
   "every load-bearing byte checks out". Six of seven sites were unproven at that moment. Re-run
   properly, all of them hold.
3. **I piped a pytest run into `Select-Object`**, which is the exact trap I have a rule about, and
   caught it before reading the result. Re-ran clean.
4. **Backticks inside a bash double-quoted `python -c` ran as command substitution**, so a report header
   was written with two names silently blanked while the script reported success. Sixth door on that
   trap, now recorded.

## Housekeeping done

Two agent reports recovered and saved (the harness refuses a subagent writing a report file). 29 bible
rows merged across three tags: `WIS` 2, `DNM` 7, `TBF` 20. One earlier `ARN` row corrected for an
off-by-one it had in its count sentence. Ledger entries for all three. Tool index regenerated at 31
permanent tools. Every file written tonight scanned byte by byte: no byte order mark, no control byte,
no em or en dash, 15 of 15 clean.
