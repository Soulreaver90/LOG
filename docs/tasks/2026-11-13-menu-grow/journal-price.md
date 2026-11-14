# The 44th journal quest: what it really costs

A study. No module was written, no build list was touched, and no ROM was built. Measured
2026-11-13 on the base USA ROM.

The owner has not chosen between growing the menu object and replacing a vanilla quest. This page
gives him the real number for each, and one recommendation.

---

## 1. The eight edit price HOLDS, and it is now stronger than it was

The census of `docs\tasks\2026-11-13-journal-menu\census.md` priced the grow at eight same length
edits. The same four shapes were run again, plus a fifth that did not exist when the census was
written.

| Shape | Tool | What it returned in the journal window, RE-RUN 2026-11-13 |
|---|---|---|
| A, `mov ; lsl` in named spans | `census.py` | `0x2B0` at `rom:0x4A52`, `rom:0x4AF2`, `rom:0x4CA2`; `0x444` read at `rom:0x4A04`; `0x40C` read at `rom:0x4B98` and the `rom:0x4DA0` trap. 17 `add` sites of `0x18` or more, every one read by eye |
| B, adjacent `mov ; lsl`, image wide | `imagewide.py` | `0x2B0` x3, `0x400` x1 in the window, `0x154` x0, `0x444` x0 |
| C, aligned word scan | inline | `0x444` x2 image wide, 1 in the window (`rom:0x4C64`); `0x40C` x20, 2 in the window (`rom:0x4C94`, and `rom:0x4E9C` which is the allocator trap); `0x154` x2 and `0x2B0` x4 image wide, **none in the window** |
| D, pc relative loads, image wide | `poolrefs.py` | `0x444` at `rom:0x4C64`, read by `rom:0x4A04`; `0x40C` at `rom:0x4C94`, read by `rom:0x4B98` |
| **E, GAPPED `mov ; lsl`, image wide** | **`gapscan.py`, new** | **the same four sites and NO others** |

**Shape E is the one that matters.** It is the shape that found four scouter sites the census
missed, three of them gapped pairs and one an add chain. Run over `rom:0x4900` to `rom:0x5100` it
adds nothing to the journal count.

Shape E was then FIXED and re-run, because review found two faults in it: its drop branch tested
shifts 1 to 3 only, and it counted `tst`, `cmp` and `cmn` as register writes. The fixed tool
returns **the same four sites** and 28 drops instead of 2. Every drop that could reach `[0x154,
0x15C]`, `[0x2B0,0x2C0]`, `[0x400,0x41C]` or `0x444` was read by eye. All 28 are a value stored to
the stack, a value stored into a field, a call argument, or a `mov rX,#imm ; bx lr` accessor.
`rom:0x4A62` and `rom:0x4A66` are arguments to the call at `rom:0x4A6C`.

**Every `add` in `rom:0x49EC` to `rom:0x4CB8` was then read by eye**, because no image wide shape
covers an add chain. Only two chains build a layout offset, `rom:0x4B02` and `rom:0x4C5A`, and both
build `+0x154`, which does not move. The scouter's hidden add chain at `rom:0x1972A` has no twin
here.

### So the eight edits are unchanged

| Change | From | To | Shape kept |
|---|---|---|---|
| object size, pool word `rom:0x4C64` | `0x444` | `0x454` | a word |
| done list header, `rom:0x4A52`, `rom:0x4AF2`, `rom:0x4CA2` | `mov #0x2b ; lsl #4` | `mov #0x57 ; lsl #3` | two instructions |
| tail field `rom:0x4B86` | `mov #0x1 ; lsl #10` | `mov #0x41 ; lsl #4` | two instructions |
| tail field add chain `rom:0x4A5E` | `add #0x5d` | `add #0x65` | one instruction |
| tail field pool word `rom:0x4C94` | `0x40C` | `0x41C` | a word |
| loop bound `rom:0x4AE2` | `cmp r6,#0x2b` | `cmp r6,#0x2c` | one instruction |

The arithmetic a test must pin: `0x154 + 4 + 44 x 8 = 0x2B8`, `0x2B8 + 4 + 44 x 8 = 0x41C`, and
`0x41C + (0x444 - 0x40C) = 0x454`.

---

## 2. Three census statements that needed correcting

None of them changes the price. All three change what the page can be trusted on.

- **`+0x40C` is not a list, and nothing writes a zero count to it.** The census says
  `sub_080049FC` "writes zero to `+0x40C`, which is the shape of a list count". It does not. At
  `rom:0x4A60` the store `str r5,[r2,#0x0]` writes to r2, which still holds `object + 0x2B0`. The
  constructor then calls `sub_08020E5C` with `object + 0x40C` in r0, and fills `+0x418` with
  `menu_font` and `+0x42C` with `glyph_draw`. **`+0x40C` is a text drawing sub-object of `0x38`
  bytes**, not a list. The `List_RemoveValue` worry rested on a reading that the handler does not
  support.
- **`+0x400` and `+0x40C` are the SAME sub-object.** `rom:0x4B86` builds `+0x400` and then reads
  `[r0,#0x30]`, which is `+0x430`. `rom:0x4B98` builds `+0x40C` and reads `+0x0`, `+0x4`, `+0x8`.
  Both land inside `0x40C` to `0x444`. That is why both must move, and why both move by the same
  `0x10`.
- **`sub_08004B62` is not a function our codemap holds.** `functions.csv` has a row at
  `rom:0x4B58` of 10 bytes, then nothing until `rom:0x4C56`. The body is reached by a branch from
  the stub at `rom:0x4CA0`. This is the SAME defect that hid the scouter's fifth site, so the
  journal family list has the same weakness, and shape E is what closes it.

---

## 3. What is the 44th quest?

The owner, 2026-11-09: "Take the time machine back to the future, or something of that sort".

All 43 vanilla entries were dumped and read again
(`scripts\one-time\2026-11-09-worldmap-star\quests.py`). **There is no spare, placeholder or
duplicate slot.** The table is `rom:0x6D68DC`, 43 entries of 16 bytes:
`{u32 category, u32 done script, u32 active script, u32 text}`.

The fill loop at `rom:0x4A86` was read in full. It runs every one of the 43 with no category
filter. A quest whose DONE script returns non zero goes to the done list at `+0x2B0`. Otherwise its
ACTIVE script runs, and on a non zero result it goes to the active list at `+0x154`. A quest whose
two scripts both return zero goes into NEITHER list. So each list alone must still hold all 43, and
the census arithmetic is right.

### The replacement candidate

Entry 0, "Talk to Dende on the Lookout", is the main story quest immediately before the Cell Games.
Entry 1 is "Enter the Cell Games". Both are the "what do I do now" line at the very end of the
story, which is the same place the time machine line belongs.

### MEASURED: the quest table has exactly ONE reader in the whole ROM

This is the fact the price of a replacement rests on, so it was measured and not assumed.

- **Aligned word scan.** Exactly ONE word in all 8 MB points into
  `[0x086D68DC, 0x086D6B8C)`: the pool word at `rom:0x4C80`, which holds the table base.
- **Pc relative load scan.** Exactly ONE instruction reads that word: `rom:0x4A86`, the head of the
  fill loop in `sub_080049FC`.

So **no completion count, no ending check and no script indexes the quest table.** A journal entry
really is a display row, and replacing one changes only the line the menu renders.

What these two shapes cannot see: a reader that computes the table address by arithmetic from
another base rather than loading it. No such reader is suggested by anything here, and neither
shape rules one out.

---

## 4. The recommendation: REPLACE entry 0, do not grow

### Why

1. **The grow is not forced.** The scouter grow is forced, because entries 128 to 130 already exist
   and already scan in battle. The 44th quest does not exist yet, so nothing is broken today.
2. **A sequencing argument, which applies only if the owner approves the scouter grow.** That grow
   is stopped until it gets a yes, and it carries 14 sites of exactly this risk class. If it is
   approved and both grows ship together, and a late save then corrupts, the owner cannot tell
   which menu object did it. He play-tests by eye on real saves, and this failure shows only on a
   save that fills a list. **Whatever he decides here, ship the two grows in separate cycles.**
3. **A replacement is structurally zero.** It writes a 16 byte table entry, two scripts and one
   string. No offset moves, no object grows, and no shape can be short, because there is no site
   census to get wrong.
4. **The price of the grow is honest at eight, but its last hole is the one that just bit us.** An
   add chain in journal code OUTSIDE `rom:0x49EC` to `rom:0x4CB8` would be invisible to every tool
   here. The image wide `0x2B0` count does not bound that hole, because an add chain never forms
   `0x2B0` as a `mov ; lsl` at all. That is precisely how `rom:0x1972A` hid in the scouter.

### What it costs if this recommendation is wrong

**The player loses one journal line: "Talk to Dende on the Lookout".** The quest itself still works,
because the journal entry is a display row and not the quest logic. The loss is the prompt that
tells a player where to go in the stretch before the Cell Games.

That is the whole cost. It is visible, it is one line, and it is reversible: the grow can be done
later as its own cycle, and the replaced entry restored, with no rework of anything else.

### What the grow would cost if IT were chosen and wrong

A silent write of 8 bytes past a list, on a save with 44 quests in one list, late in the game. It
passes every test, it passes a fresh playthrough, and it shows up on the owner's own long save. That
asymmetry is the whole argument.

---

## 5. The open question, stated plainly

**Does any journal code outside `rom:0x49EC` to `rom:0x4CB8` build `+0x154`, `+0x2B0`, `+0x400`,
`+0x40C` or `0x444` from an add chain?** No shape here answers it. Closing it needs the journal
object's own method list taken from a source that can be trusted, and every `add` in each method
read by eye. That work is worth doing before any grow, and it is not worth doing to ship one
journal line.

**Two checks were NOT done**, and neither is needed for the price above. Named here so the next
agent does not assume they were:

- The `bl` callees of the journal family that receive the object in r0 were not enumerated. The
  equivalent sweep WAS done for the scouter, and it is what proved the scouter passes the world and
  not its own object to the shared list helper.
- The journal object's own vtable was not resolved from a trustworthy source. A self relative
  decode was tried and REJECTED, because its targets for `0x08023c50` decode as mid instruction
  garbage while `listing.py` names `sub_08004AEA` for the same slot. No claim here rests on it.

The 57 caller decode of `List_RemoveValue` is not disturbed by anything above. No caller lies inside
the journal menu range, and section 2 shows the `+0x40C` in that helper was never the journal's
field in the first place.
