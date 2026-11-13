# Brief: move Goku's Super Saiyan set from the chamber ENTRY to the chamber EXIT

## The owner's design call, 2026-11-13

"Goku should not be super saiyan when he enters the chamber, only when he exits."

Today `fullpower_ssj` sets Goku's appearance in the chamber ENTRY scene, where Vegeta and Trunks
come out and Goku and Gohan go in. That is the wrong moment. It must happen in the EXIT scene.

## What is there now, and must be removed

`scripts\permanent\patches\fullpower_ssj.py`, `RECORDS["door_seq33"]`:

    "door_seq33": (0x3DE620, 0xB2, 0x3DE774, "e894d9b3cca20bc754af321858f5c2c4cdb20d07",
                   0x90, "00020246", "00020246" "0004003d0249"),

That inserts `push 4 ; push 61 ; ext 73` (Goku to set 61, appearance entry 20) into the entry
scene. Remove the insert. The entry scene must go back to vanilla for Goku.

Earlier today the anchor was moved from `set_flag(149)` (0x7C) to `leader(2)` (0x90), because
`appearance_revert` runs inside ext 70 and spares only the new leader (bible B0554). That ordering
fix is now moot in this record, because the op leaves it entirely. Keep the B0554 knowledge: it
still governs where the op may sit in its new home.

## Where it goes, measured

- Chamber EXIT scene table: `rom:0x3DBDD4`, 35 words.
- Word 2 names record **`rom:0x3DB59C`**, length **0xCC**, base ROM SHA-1
  **`16fac4c3c134432c320aabcd1270b928e4064368`**.
- Table word for that record: `rom:0x3DBDDC`.
- **The exit scene contains NO ext 70 leader change** in any of its first 12 records. Verified with
  `scene_harness.run_record`. So an appearance set there cannot be reverted by the scene. This is
  why it is the right home and needs no ordering trick.
- The record already carries Gohan's appearance change, which is `fullpower_ssj`'s own
  `GOHAN_EXIT = {0x3DB62A: (157, 158)}`. Goku's set belongs beside it.

## The wrinkle: the record's bytes change DURING the build

At record offset 0x8B the base ROM holds the zigzag form `1d 02 00 70 02 49`, which is
`appearance(Gohan, set 56)`. `0x70` is a one byte argument. Then:

1. a gi module rewrites that set to **157**,
2. `fullpower_ssj`'s `GOHAN_EXIT` rewrites 157 to **158** at `rom:0x3DB62A`.

So the bytes at insert time are NOT the vanilla bytes. Work out the actual state at the moment
`fullpower_ssj` runs, and anchor on that. Do not anchor on a value you have not read from a real
build at that point in the list. Note the record uses the ZIGZAG argument encoding
(`scene_lib.appearance(...)`), while `RECORDS` elsewhere uses the plain `00NN` push form. Both
assemble; use whichever keeps the record valid, and say which you used and why.

## Tests to update

`scripts\permanent\tests\test_fullpower_ssj.py` has two assertions that pin the ENTRY placement.
They were updated earlier today to expect the op after `leader(2)`. Both must now assert the op is
GONE from the entry record and PRESENT in the exit record:

- `StretchFlagTests.test_start_flag_set_with_gokus_record_at_the_door`
- `ScriptTests.test_door_record_is_old_plus_gokus_record`

Rename them if the name now lies. A test named for the door that checks the exit is worse than a
failing one.

`tests\test_battle_start.py` carries a census rule, `forms_lost_at_the_leader_change`, that found
the original defect. It must still pass. Do not touch that file.

## Proof required

1. Run `test_fullpower_ssj.py` and `test_battle_start.py` alone. Give run, failures, errors, skips.
2. Prove from a BUILT dev ROM, through `scene_harness.run_record`, that:
   - the entry record `rom:0x3DE774`'s scene no longer sets Goku's appearance at all, and
   - the exit record `rom:0x3DB59C` sets Goku to set 61, and
   - no ext 70 precedes it in that record.
   Paste the op listings.
3. Name any other test that changed state, and why.

## Rules

- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Never write under `data\`. Never create or overwrite a ROM, save or state. Build in memory only.
- No em dashes or en dashes. ASD-STE100 in comments, WHY only.
- Do not run the whole suite. Do not commit. Do not build a ROM file.

One report message, then stop. Do not add a byte order mark.
