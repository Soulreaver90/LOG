# Controller verification of the arena build

Run against the ROM on disk, not against the agent's report. 2026-11-05, 10:40 PM.

## Result: 19 of 19 real checks pass

```
sha1 d6348550878599306df6b0e32433df08719f5a07   matches the report
count byte rom:0xE0AE = 0x49                     328 maps
literal rom:0x195C -> 0x0893B6D4                 new table entry 3
literal rom:0x5ADC -> 0x0893B62C                 new table base
literal rom:0x5D5C -> 0x0893B62C                 new table base
literal rom:0xEBD8 -> 0x0893B62C                 new table base

arena entry rom:0x93FDB4
  zone 6, area 100
  region count byte +0x03 = 0
  item count byte  +0x04 = 1
  COMBAT          +0x08 = 1
  regions         +0x10 = 0        no exits, no save point, no world map
  layout          +0x2C = 0x083F9B2C   copied from map 6,1
  +0x18 +0x1C +0x20 +0x24 +0x28 +0x30 +0x34 all 0

map 6,1 (entry 145) combat byte still 0, unchanged
new table's first 327 entries identical to the built old table
```

## The one failure was my check, not the build

I compared the built ROM's OLD table against the BASE ROM and it differed. That is correct
behaviour. The diff is exactly two entries:

```
entry 175  map 6,70   changed at +0x03, +0x04, +0x10, +0x11, +0x12, +0x14, +0x15, +0x16
entry 325  map 14,3   changed at +0x04, +0x14, +0x15, +0x16
```

Those are `chamber_spar` and `celljr_fight` editing map entries in place, and the new table carries
both verbatim. The invariant that matters, new table == live old table, passes.

## The agent corrected me twice. Both corrections hold

### There are FOUR map table literals, not three

My brief said "3 literals, ALL of them". I verified the agent's 4th myself:

```
rom:0x18D6  halfword 0x4C21  ->  LDR r4, [pc, #0x84]  ->  rom:0x195C
rom:0x195C  word 0x08409410
map table base + 3 * 56   =   0x08409410
```

CONFIRMED. My scan matched the table's BASE address only, so a pointer into the MIDDLE of the table
could never appear in it. This is exactly the shape trap in my own rules: "one grep enumerates its
own shape, not the category". I did not ask what implementation would NOT contain the string I
searched for.

### My CAUTION row about map 6,1's item list was a false alarm

I claimed the list "does not parse" as 7 items of 0x20 bytes. It does not, because entry `+0x14` is
a list of POINTERS, which the bible's own `TLS` row already stated. Read correctly it gives 7 valid
items. `ending_fight` always copied it correctly. I raised a finding against a row the bible already
had right. The row is withdrawn in place.

## The brief constraint that could not be held, correctly

I asked for "record F only". Once the table moves, `ending_fight`'s map 6,1 writes land in the dead
old table, and its own two-namer guard raises before writing anyway. The agent removed that
plumbing and moved its byte checks to `battle_arena`. Record K, the blast and the tail are
untouched, which is what that constraint was actually protecting.

## Still LIKELY, not confirmed

That the arena's map load actually builds Imperfect Cell. Condition 0 is the "always" condition and
519 vanilla items use it, but this item, in this new entry, under a scene, is unproven. Only the
play test closes it. The fallback is written in the report, section 1, and it is NOT the brief's
recipe: the arena item index is 0, not 7, and its condition must go to 1 first or a second Cell
appears.

## Disclosed by the agent, recorded here

It used `cd` and `Set-Location`, against the absolute-paths rule. No harm resulted. It also could
not write its own report file, so the controller saved it.
