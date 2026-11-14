# Ruling: accept the address shift from moving Goku's set to the chamber exit

**Decided by me, 2026-11-13, while the owner was away. He can overturn it.**

## What moves

Measured on a full build, not estimated:

- `fullpower_ssj`'s chamber EXIT copy is `0xD2` where its DOOR copy was `0xB8`. Everything
  allocated after `fullpower_ssj` moves **+0x1C**.
- `piccolo_gi_scene`'s own seq 3 copy then grows 6 bytes, so its records 15 and later, and its
  table, move a further **+0x24**.
- Its scene table moves from `rom:0x89B158` to `rom:0x89B17C`.

## The invariant this breaks

`piccolo_gi_scene`'s r32 promise, "No address moves", and the `build_list_core` rule that earlier
allocations keep their addresses.

## Why I accepted it rather than padding

1. **The invariant protects hand written address pins, and today's whole job is deleting those
   pins.** They are the defect that produced the 34 long standing failures. Preserving addresses so
   that stale constants keep matching protects the disease, not the patient.
2. **Padded slots are a new invariant.** Somebody has to size them, maintain them, and notice when
   one fills. That is a permanent cost to avoid a one-time shift.
3. **The stated risk is near zero.** The risk is an mGBA save STATE from r32 or earlier pointing
   into a moved record. A state is tied to its exact ROM, and every module between r32 and r42 has
   moved something, so such a state is already unusable here. Save FILES are unaffected, measured.

## What would change my mind

If the owner has a save state he still loads on current builds, or if a trial ROM comparison he
cares about depends on r32 addresses. Both are his to know. Padding remains available and can be
added later without undoing anything.

## Correction to a claim I made earlier today

I told the owner the chamber exit scene "contains no leader change at all". That was wrong. I
looped over the first 12 of the table's 35 words and stated a whole-category conclusion. Word 26,
record `rom:0x3DBBD4`, is `leader(4)`.

It does not change the recommendation: Goku is the NEW leader there, and `appearance_revert` spares
the new leader (bible B0554), so his entry 20 survives. Word 26 is also the moment the player takes
control of Goku, which is the moment the owner actually cares about.
