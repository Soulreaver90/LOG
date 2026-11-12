# Addendum: two more jobs, both fully measured. This is likely the LAST build this week.

The owner, 2026-11-09: "We dont have alot of tokens for the week so this may be the last build. Make
it count". He then agreed the scope below and explicitly ruled OUT the interactive time machine and
player control redesign, which stays for a later cycle.

**So five things ship: the beam tick, the plateau music, the android explosions, and jobs 4 and 5
below.** Build ONCE, at the end, with all five in.

---

## Job 4: the ending music must not change when Gohan flies off

His words: "When the game ends and gohan flies off, lets change it so music doesnt change".

**Measured by the controller:**

- Dende farewell record 87 `rom:0x3DCEDC` opens with **`music(18)`**. That is the track playing while
  Gohan flies home. It ends `fade_out(300) ; ext125`.
- Ending table `rom:0x3B8140` word 0 `rom:0x9408CC` then runs **`music(42)`**.
- Map 6,23, sunny Capsule Corp with the time machine, carries **`+0x24` = 42**.

So the change is **18 to 42**, in two places that agree with each other.

**The fix is bible B1191's own rule, the same one used for the plateau: name the song that is
playing.**

1. Drop the `music(42)` from ending word 0.
2. Set map 6,23's `+0x24` to **18**.

Both are needed. B2176: `ext 38` and `ext 39` read the new map's `+0x24` and restart the music
unless it names the song already playing, and B1191 adds that there is no "leave it alone" value.

**One thing NOT measured, and worth a cheap look before you rely on it.** `ext 125` is at
`@0x0800AF44`. Its own handler touches no music: it allocates a `0x54` object with vtable
`0x08023EB8`, calls `scene_push`, and does a DMA clear. Whether the object it starts (the credits)
changes the track is unread. **Naming 18 is correct either way** (if 18 is playing it continues; if
the credits changed it, it comes back to 18), so this does not block you. If reading the vtable tick
is cheap, say what it does; if not, say you did not read it. Do not claim either way.

## Job 5: the journal entry, in full

His words: "then it fades to trunks at capsule corp with the journael entry update". He chose the
FULL entry over a box alone, once the price was measured: "do both scouter and journals if cheap",
then "Agreed" to journal now, scouter later.

### Why it is cheap, measured by the controller

| Fact | Value |
| --- | --- |
| Quest table | `rom:0x6D68DC`, **43** entries, 16 bytes each (`lsl r0,r6,#4`) |
| Entry shape | `+0x00` category byte, `+0x04` done script, `+0x08` active script, `+0x0C` text |
| **References to the table in the WHOLE ROM** | **exactly one**: pool word `rom:0x4C80`, loaded at `sub_080049FC+0x8a` (`rom:0x4A86`) |
| The loop bound | `cmp r6,#0x2b` at **`rom:0x4AE2`**, one byte, 0x2b = 43 |
| Text pool | the 43 texts run contiguously from `rom:0x6D6B8C`, which is the table's last byte + 1 |
| Category word table | `0x081D9C80`, indexed by the `+0x00` byte at `rom:0x4AD6` |

So: relocate the 688 byte table to expansion, append a 44th entry, repoint ONE pool word, and change
ONE bound byte. That is the same move four other modules already make.

### The box

Bible **B0706**: sound 62 is the vanilla "Journal Updated!" chime, and all 48 vanilla
`@^Journal Updated!` records carry `ext 46 (62)` within the 24 bytes before the box. There is already
a test, `test_vanilla_plays_62_right_before_every_journal_box`. **Follow that shape exactly**, and
keep that test green.

Place the box in the Capsule Corp beat of ending word 0, after the screen is up. Word 0 is a type 0
record and a text box needs a type 1, so it has to be split or routed through a spare ending word.
`ending_fight` already splits ending records and uses spare words, so follow its pattern rather than
inventing one.

### The entry's own streams

`+0x04` done and `+0x08` active are ordinary scene bytecode and the vanilla ones use ops 0, 1, 2, 4,
5 and 17 with ext 19 and ext 21 only, which are flag tests (B0775). Drive the new entry from a flag
that is already set at this point in the story. **Flag 196 is set by farewell record 87 at
`rom:0x3DCEF7`**, immediately before the ending begins, so it is true for the whole ending and is the
natural candidate. Check it rather than assume it.

### The TEXT of the entry

**The controller is asking the owner for his own wording.** Do not invent it. If the wording has not
reached you by the time you need it, build everything else, leave the string as the single clearly
marked placeholder `[[JOURNAL TEXT PENDING]]`, and say so loudly in your report so it is the last
thing swapped in before the build.

---

## Build and verify

- Build ONCE, at the very end, from `scripts\permanent\build_list_trial_plateau.txt` to
  `builds\mockups\future\future_v3.gba`. **This one is the candidate, not a scratch name.** Never
  overwrite an existing ROM; if that name exists, stop and say so.
- Full suite once, redirected to a file, never piped.
- Keep the fail-then-pass proofs for the beam and the music, and add one for the journal: a test that
  the bound, the relocated table and the entry count agree arithmetically, and that the box follows
  the sound 62 shape.
- Bible rows in `docs\tasks\2026-11-09-beam-tick-music\rows.md`, tag `BTM`. **Check the tag is free
  first**: `grep '| BTM |' docs\RE-BIBLE.md`. A reused tag reads as "already merged" and silently
  loses the batch.

## Explicitly OUT of scope

The interactive time machine, player control at Capsule Corp, moving the form and leader change
earlier, and removing the NPC puppet. The owner ruled all of it out for this build. Do not start it.
Design notes are in `docs\design\2026-11-09-ending-opening.md` for the next cycle.
