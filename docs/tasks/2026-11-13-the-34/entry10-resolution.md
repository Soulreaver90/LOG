# Group 4, second row: `test_the_base_and_non_pool_forms_still_get_nothing(entry=10)`

**Verdict: the code is right and the TEST is wrong. No game change.**

## The claim under test

The test lists entry 10 with leader 2 among the forms that must get no ki pool:

    for entry, leader in ((PICCOLO_ENTRY, PICCOLO), (3, 0), (4, 0), (10, 2), (8, 2)):
        self.assertEqual(self.ref(entry, leader=leader), 0)

It fails with `50346496 != 0`. That value is `0x3003A00`, the ki pool RAM block, so `pool_ref`
hands entry 10 the pool.

## Evidence

**1. Entry 10 is Vegeta's ascended form, and that is VANILLA.** Read from the base ROM's
appearance table at `rom:0x1D967C` (bible B0553), with no patches applied:

| Entry | Set | Flags | Reverts to | Form object |
|---|---|---|---|---|
| 8 | 137 | 0x00 | 11 | 0x030021E0 |
| 9 | 138 | 0x00 | 10 | 0x030021E0 |
| **10** | **139** | **0x01** | **9** | **0x030021E8, the ascended grade** |
| 11 | 140 | 0x01 | 8 | 0x030021EC, Super Saiyan |

Flags bit 0 set means "this is a transformed form". No patch of ours changes this row.

**2. `bf_ki_pool` treats the ascended grade as a pool form ON PURPOSE,** and names entry 10
explicitly. From the module itself:

    ASC_OBJ, ASC = 0x030021E8, 10   # the ascended grade form object; entry 10 is Super Vegeta

Its docstring: "pool_ref: the leader is in a pool form (form object 0x030021EC Super Saiyan,
0x030021E8 the ascended grade, or ssj2_form's Super Saiyan 2)... orange for a second
transformation (the ascended grade and Super Saiyan 2)".

The handler carries the same intent in a comment at `bf_ki_pool.py:127`:
`sub r5,#0x4 ; the ascended grade 0x030021E8, off the Super Saiyan literal: no new pool word`.

## Why it failed for so long

The ascended branch was written into `pool_ref` deliberately. The test's "gets nothing" list was
never updated to match, so the row has been red since.

## The fix

Move entry 10 out of the "gets nothing" list and assert the opposite, beside entry 11 in
`test_the_saiyan_forms_are_unchanged`. Entry 8 (set 137, flags 0x00) stays in the "gets nothing"
list and is correct there.

Blocked only on the group 2 agent releasing `test_piccolo_z_start.py`.

## For the owner

This changes no game behaviour. Super Vegeta already has the Buu's Fury ki pool and the orange
bar, by design, and has had it all along. If that is NOT wanted, that is a design change and a
separate decision.
