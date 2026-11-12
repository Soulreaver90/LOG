# Scouter entries for the three future enemies

The owner, 2026-11-08: "They should read as Future 17, Future 18 and Future Cell. With new bios to
match, and they should be scannable." Then: "Maybe just reuse the bios for the vanilla, they are
essentially the same. Maybe something omnious at the end like 'Their bio suggest they are not of
this time' or something of the sort."

## The approach, and why it is better than authoring three bios

Reuse each vanilla bio verbatim and append ONE shared closing line.

The shared line is the same sentence on all three ON PURPOSE. It reads as the machine's own
conclusion, repeated, rather than as three authored flourishes. It is also canon-true: the player
scanned the present-day Android 17, Android 18 and Cell during the main game, so the database really
does already hold these beings. The scanner is not being poetic. It is reporting a duplicate it
cannot explain.

## Names and entry fields

| name | bio source | set | portrait | `+0x10` enemy type |
| --- | --- | --- | --- | --- |
| `Future 17` | vanilla entry 2, `Android 17` | 9 | 28 | the new weakened type |
| `Future 18` | vanilla entry 3, `Android 18` | 11 | 29 | the new weakened type |
| `Future Cell` | vanilla entry 11, `Cell` | 28 | 38 | the new weakened type |

`+0x10` must name each enemy's OWN new type index, which is what makes the scan show the weakened
HP, STR, POW and END rather than "???" (bible **B1793**).

## The closing line

```
  This record matches an entry already held in this database.  These readings do not belong to this time.
```

105 characters, two spaces after each full stop, matching vanilla's own separator.

## Lengths, measured on the base ROM

**The longest bio anywhere in the 128 entry table is 582 characters.** That is the only proven
ceiling we have, so a string past it is asking the text box to do something the game never does.

| entry | vanilla | plus tail | vs the 582 ceiling |
| --- | --- | --- | --- |
| Future 17 | 476 | 581 | -1 |
| Future 18 | 477 | 582 | 0 |
| Future Cell | 524 | 629 | **+47** |

Cell overshoots because his vanilla bio is the longer one. **Recommendation: drop one sentence from
Cell's copy, `Extraterrestrial origin may be possible.`** It is the least load-bearing line in that
bio and it is the one least true of a Cell the player has already met. That gives 482 + 105 = 587,
which is +5 against the ceiling. All three then sit inside territory the game itself proves.

**The build must still confirm the text box handles 587**, rather than assume that +5 is free.

## The constraint the entries have to fit

Measured on the base ROM 2026-11-08 with `scouter_census.py`:

- The table at `rom:0x6F8E40` holds 128 entries of 20 bytes and **all 128 are in use**. Not one has a
  null name or bio pointer. There is nothing free to take.
- 20 names are duplicated across entries, but each duplicate is a different enemy type that shares a
  display name, so repurposing one removes a real enemy's scan.
- The save stores one bit per entry at `+0x11A` (`log2_save.py` line 42: `O_SCOUTER, SCOUTER_BITS =
  0x11A, 128`). Item counts start at `+0x12B` (line 43). 128 bits is 16 bytes, `0x11A` to `0x129`,
  so **exactly one byte, `0x12A`, sits unaccounted between them.** Eight spare bits, enough for three
  new entries, IF that byte is really free. **NOT PROVEN. Prove it before building anything.**

So the table must grow, and growing it needs:

1. The table relocated to the expansion area. It has 5 literal sites (bible **B0594**):
   `@0x08018E40`, `@0x08018F94`, `@0x08019130`, `@0x080195F8`, `@0x08019924`.
2. The 128 bound raised in the type matcher `@0x080190D4` (**B2297**), the set matcher
   `@0x08019102` (**B0045**), and the database list loop `@0x0801923A` to `@0x08019262` (**B0583**).
3. Three new strings in the expansion area. The string pool at `rom:0x6F9840` starts immediately
   after the table and is contiguous, so nothing can be inserted into it. Bio text is COPIED from
   the vanilla string rather than pointed at it, because the tail makes it a different string.

## The save bit blocker: ANSWERED, 2026-11-08

`save_gaps.py` walked every `.sav` on disk, 293 files, 879 slots, and split them into real saves and
erased EEPROM slots (a slot over 80 percent `0xFF`).

**862 real save slots. Byte `0x12A` is ZERO in every one of them.** The only 17 slots holding a
nonzero value there are erased slots, where it reads `0xFF` along with every other spare byte.

**The control that makes this worth believing:** the same scan reported `0x10D`, `0x10E` and `0x10F`
as NONZERO in 844 of the same real slots. Those three sit in the gap after the documented 297
visited-map bits (`O_VISITED 0xE7`, 38 bytes, ending `0x10C`), so the documented layout has a gap
there that is NOT free. The method therefore detects a spare byte that is really in use. It found
those three and found `0x12A` clean.

So the eight bits of `0x12A` are available for scouter entries 128 to 135, which covers the three we
need with five to spare. Raising the list loop bound from 128 to 131 makes it read `0x11A + (130 >>
3)` = `0x12A`, which is exactly one byte past the current field and no further.

**This is EVIDENCE, not proof.** 862 saves agreeing is strong, and the control shows the scan is not
blind, but only a reader search over the ROM proves nothing writes `0x12A`. A save-struct offset is
built in stages in this engine (the scouter loop itself is `add r3,#0xff ; add r3,#0x11 ; ldrb
r3,[r3,#0xa]` for `0x11A`), so no single search shape enumerates every reader. **Blast radius if
wrong is small and cosmetic:** the three new entries' "already scanned" flags would collide with an
unknown field, which shows up as a wrong tick in the database list, not a crash or a lost save.

## Side finding, worth its own bible row

`O_VISITED` is documented as 297 bits at `0xE7`, which ends at byte `0x10C`. Bytes `0x10D` to
`0x10F` are undocumented and hold `0xFF` in 844 of 862 real slots. Either the visited field is wider
than 297 bits or an undocumented field lives there. `log2_save.py` line 41 is the place that would
need correcting. NOT investigated further; it does not block the scouter work, because the scouter
work only needs `0x12A`.
