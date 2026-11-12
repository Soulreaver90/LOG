# Ascended Super Saiyan for Trunks and Vegeta: the grade already exists

Owner, 2026-11-08: "one of the plans was to use the protorype ascenced super saiyan as new
sprite/transofmrations for trunks/vegeta."

This note records what the game already does, found while answering "129 vs 132, what's the
difference". It changes what that feature costs.

## The finding

**The ascended grade is already implemented and already wired to both characters. Only the art is
missing.**

The appearance table at `rom:0x1D967C` holds 20 byte entries. Byte +1 is the set id, byte +4 is the
transform target entry, and the word at +16 is the form object.

| Character | Base entry | Set | Transforms to | Set | Form object | Grade |
| --- | --- | --- | --- | --- | --- | --- |
| Trunks | 13 | 129 armour | entry 14 | 130 | `0x030021E8` | **ascended** |
| Trunks | 15 | 132 armour | entry 16 | 133 | `0x030021EC` | ordinary |
| Vegeta | 9 | 138 | entry 10 | 139 | `0x030021E8` | **ascended** |
| Vegeta | 8 | 137 | entry 11 | 140 | `0x030021EC` | ordinary |

The two form objects are different grades, both CONFIRMED in the bible:

- `0x030021E8`, the ascended grade (B0427): **+15 STR, +10 POW, +15 END, and slower** movement,
  speed 0.75 / 1.75.
- `0x030021EC`, the ordinary Super Saiyan grade (B0426): **+10 to each core stat**.

The slower speed is the detail that matters. It is the ascended form's own drawback, already
modelled, and it is exactly the trade the anime gives that form.

## Why the sets look the same

Set 132 is **byte identical** to set 129, and set 133 to set 130. All 288 records name the same
record header addresses and not one pixel differs. MEASURED, and validated against a control: set
128 against set 129 shares zero headers and differs in 280 of 288 frames.

So the developers built two appearance pairs over ONE set of armour art, and used the pair only to
choose a stat grade. They never drew a bulked sprite for the ascended form.

## Where the art comes from

**The bulked sprites are NOT in our retail ROM.** Owner, 2026-11-08: "these are from the prototype
rom that was leaked. its not complete but we have a reference."

So the reference is the leaked LoG II PROTOTYPE build. Rips titled "Beta Super Trunks" and "Beta
Super Vegeta", credited to Yenebi on Spriters-Resource, show a bulked gold Trunks and a bulked gold
Vegeta that the retail game never shipped.

Confirmed against our own ROM: a contact sheet of all 150 live sets
(`art/vanilla-sets/all-sets-contact.png`) holds no bulked Trunks or Vegeta beyond the known sets,
and sets 129/132 and 130/133 are byte identical pairs. Nothing is hiding in the retail ROM.

**The art rule, as I read it.** The project rule says Buu's Fury art is official and may be ported,
never copy other modders' art, and the Z Hack is clean-room inspiration only. A leaked prototype of
THIS GAME is Webfoot's own art for this game, so it sits on the official side, not the modder side.
The rip is somebody's extraction, but the pixels are the studio's. **Worth one explicit yes from the
owner before any pixel is ported**, because it extends a rule rather than following one.

The rip is also incomplete, so some frames will have to be drawn to match it rather than ported.

Downloads of prototype material are untrusted: give them their own folder, read with `py -I`, never
run them.

## What the feature therefore costs

Not new form code. The transform, the stat bonus, the speed penalty and the revert target all exist
and are reachable today.

1. **Port the bulked sprites from the prototype, and draw the frames it does not cover.** This is
   the whole job, and it needs the owner's yes on the art rule first (see above).
2. **Point the ascended entries at the new sets.** Change byte +1 of entry 14 (Trunks) and entry 10
   (Vegeta) to the new set ids. Two bytes.
3. **Decide how the player reaches it.** See the open question below.

## Open, and not yet measured

- **Which pair does playable Trunks actually use today?** Bible B0642 calls entry 15 and 16 "Trunks'
  appearance pair", which suggests the playable path takes the ORDINARY grade, and that the ascended
  pair 13/14 may be unused or cutscene only. **This is not measured.** If the ascended pair is
  already live somewhere, changing its art changes that scene too.
- The same question for Vegeta, entries 9 and 10.
- Whether a flag should gate the ascended form, the way Super Saiyan 2 is gated on story flag 195.
- Whether both characters get it, or Trunks first.

Related: `docs\RE-BIBLE.md` rows B0426, B0427, B0458, B0459, B0642, and the banked rows at
`docs\tasks\2026-11-08-trunks-sets\rows.md` (tag TKS).
