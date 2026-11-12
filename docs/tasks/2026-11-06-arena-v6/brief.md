# Brief: arena v6, put the 17/18 scene back and make the player Trunks for the Cell scene only

Build task. Build a trial ROM and run the full suite once at the end. Follow `docs\tasks\global.md`.
Read `docs\tasks\2026-11-06-arena-v5\report.md` first: v6 is a scope correction to v5, not a new design.

## Why v5 is wrong

The owner play-tested v5 and Trunks vanishes. Then he set the scope:

> "Remember there are two sections, the scene against 17/18, which we are NOT doing at this time. And the
> future cell scene."

v5 edited both sections. It also deleted `spawn(133, 496, 504)` at `rom:0x3B7C41` while leaving the
`remove(set=132)` at `rom:0x3B7C37` in place. **Those two ops are one transformation**: base Trunks is
removed and Super Saiyan Trunks spawns on the same spot. Deleting half of it leaves nobody on screen, which
is exactly what he saw, right before the line "TRUNKS: The name's Trunks...".

## The boundary, CONFIRMED by my own decode of the base ROM

Vanilla record 13 at `rom:0x3B7E4A`:

```
wait(60) ; fade_out(frames=180)
load_map(zone=6, area=1, var=1, x=136, y=432)     <-- rom:0x3B7E5E, the future Cell scene starts HERE
wait(120) ; walk(set=133, x=248, y=568) ; wait(100)
```

Everything before `rom:0x3B7E5E` is the 17/18 scene and is **out of scope**.

## Part 1: undo v5's edits inside the 17/18 scene

Restore all seven to vanilla:

| Address | v5 made it | Restore to |
|---|---|---|
| `rom:0x3B7C41` | deleted | `spawn(133, 496, 504)` |
| `rom:0x3B7C72` | `face(0, 1)` | `face(133, 1)` |
| `rom:0x3B7CA2` | `attack(0, 11, 100)` | `attack(133, 11, 100)` |
| `rom:0x3B7CDE` | `attack(0, 11, 100)` | `attack(133, 11, 100)` |
| `rom:0x3B7D80` | `attack(0, 9, 100)` | `attack(133, 9, 100)` |
| `rom:0x3B7DBC` | `attack(0, 9, 100)` | `attack(133, 9, 100)` |
| `rom:0x3B7E06` | `face(0, 0)` | `face(133, 0)` |

Prefer dropping those records from the module's relocation set entirely, so the vanilla records are simply
left alone and the table words point back at them. That is cleaner than re-editing copies, and it shrinks
the diff. If a record must still be copied for another reason, say why in the report.

After this, the 17/18 scene is byte-identical to vanilla. **Prove it**, by comparing the reachable records
of words 0 to 12 in the built ROM against the base ROM.

## Part 2: the future Cell scene, the part we ARE doing

The owner's design, in his words:

> "Just kick the NPC out from the start, never load it in, just load the player control trunks, have it
> follow the same path as the NPC, no hand off needed."

Applied to this section only: from the Capsule Corp load onward, the player IS Super Saiyan Trunks.

In record 13, **under the existing `fade_out(180)` and before the load at `rom:0x3B7E5E`**:

- `ext 73 (3, 133)` then `ext 70 (3)`. The order matters: `appearance_revert @0x08003ED4` skips the record
  whose index equals the leader byte, and `ext 70`'s body install is guarded, so the map load that follows
  is what builds the player's body. Both CONFIRMED, see the v5 report.
- Then `walk(0, 248, 568)` in place of `walk(133, 248, 568)`, so the player walks the NPC's own path.

**One thing you must READ, not assume.** Does NPC set 133 survive the `load_map` into 6,1? Vanilla's
`walk(133, ...)` runs after that load, which suggests he does. Read `map_load @0x0800C584` and settle it:

- If scene-owned actors survive the load, emit a `remove(133)` BEFORE the load, or two Trunkses appear.
- If the load destroys them, emit no remove, because removing a missing actor may block the scene.

State which it is, with the proving instruction, and label it CONFIRMED. **Do not guess.** A wrong call here
reproduces the v5 defect in a new place.

## Part 3: record F

Keep v5's record F as built. It is the vanilla battle-start shape and its fade is the fix for the camera
snap. Its `appearance(3,133)` and `leader(3)` become redundant once record 13 does the same, which is
harmless and guards against the player having switched character. Say in the report if you disagree.

The fighter spots are settled: Cell (244,504), player (248,568). Do not move them.

**The owner has not ruled on the 5 second pause** (`fade_out(120)` plus `fade_in(120)` plus `wait(60)`).
Leave the three constants as they are and flag them again in the report.

## What you must NOT do

- Do not touch `fullpower_ssj`. **`test_form_survives_the_leader_change` is EXPECTED to stay RED with
  exactly one finding, `rom:0x89A9C0`.** Do not declare an exception and do not make it pass.
- Do not touch `chamber_spar`, and add `BATTLE_START_EXCEPTIONS` to no module.
- Do not touch set 132's ops. After part 1 they are vanilla again.

## Expected end state

- The 17/18 scene byte-identical to vanilla, proven by comparison.
- `test_map_load_is_covered` GREEN, `test_control_record_shows_the_hud` GREEN.
- `test_form_survives_the_leader_change` RED, one finding.
- Everything else green. Report the exact `Ran N tests` and `FAILED (failures=N)` lines.

## Build and rules

- Trial to `builds\mockups\2026-11-06-arena-v6\` from `build_list_trial_ending.txt`. Print the SHA-1, pair a
  `.sav`.
- Run the suite once at the end. **Redirect to a file and read the file.** A pipe or a trailing command
  reports the LAST command's exit code: on 2026-11-06 that showed "exit code 0" on a run with 3 failures.
- Every source byte, word and record checked before the first write; a second run raises.
- Python header block, no em or en dashes, no byte order mark. Label claims CONFIRMED, LIKELY or SPECULATIVE.
- Write `docs\tasks\2026-11-06-arena-v6\report.md` content as your report message, and `rows.md` with tag
  `AR6` if you learn a ROM fact.

One report message, then stop. Do not add a byte order mark.
