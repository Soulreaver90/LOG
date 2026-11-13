# Gate Z+ on the chamber exit the game already has

Build in one run. The design is the owner's and it is decided. Do not re-open it.

**You are in a git worktree**, `C:\Users\josephgonzalez\Documents\Projects\.worktrees\zplus-unlock`,
on branch `feature/zplus-unlock`. Every path you read or write is under it. Another agent is editing
`bf_ki_pool.py` in the main tree at the same time, which is why you are here. Do not touch the main
tree at `...\Workspace\LOG` for anything but reading the Buu's Fury and LoG II ROMs under `data\`.

## What the owner worked out, and it is better than what we built

His words: "once he leaves the chamber and the user has control, he automatically uses the new
transformation as the default Z. So instead, we grant Z+."

He is right about the game, and I verified every line of this myself in the base ROM:

```
entry  8  set 137  portrait 106  +4 = 11  +5 = 11  obj 0x030021E0   base, pre-chamber
entry  9  set 138  portrait 106  +4 = 10  +5 = 10  obj 0x030021E0   base, POST-chamber
entry 10  set 139  portrait 107  +4 =  9  +5 =  9  obj 0x030021E8   ascended, +15/+10/+15
entry 11  set 140  portrait 107  +4 =  8  +5 =  8  obj 0x030021EC   Super Saiyan, +10/+10/+10
```

- `ext 73 (2, 138)` at `rom:0x3DE6BB` moves Vegeta from entry 8 to entry 9. **One hit in the whole
  ROM.** `ext 73 (3, 129)` at `rom:0x3DE6B4` does the same for Trunks, 7 bytes earlier, in the same
  record, right after the `ext 70 (2)` at `rom:0x3DE6B2`.
- Both sit in the chamber exit scene. I read the text beside them: "Tripled? Hahahaha... You have no
  idea, Kakarot."
- `ext 73 (2, 137)`, which would put him back, has ONE hit at `rom:0x3E778B`, and the text beside it
  is Android 16 at Capsule Corp, which is BEFORE the chamber. **So nothing ever undoes the swap.**
- Bible row at `docs\RE-BIBLE.md` line 600 cites `@0x083DE620` for this. That is 0x9B bytes short
  and holds a walk, not an `ext 73`. **Correct that row in your `rows.md`.**

So vanilla already upgrades his Z silently at the chamber. We turn that into granting Z+ instead.

## The design. Build exactly this.

| | base entry | Z | Z+ |
|---|---|---|---|
| before the chamber | 8 | entry 11, `set:140`, +10 | unreachable |
| after the chamber | 9 | a NEW entry, `set:140`, +10 | entry 10, `set:139`, +15, portrait 122 |

1. **Leave `rom:0x3DE6BB` and `rom:0x3DE6B4` alone.** The vanilla op is the unlock. Write no flag,
   set no ability bit, and add no code gate. If you find you need one, STOP and report why.
2. **A new appearance entry, the post-chamber Z.** Copy entry 11 (`set:140`, portrait 107, form
   object `0x030021EC`), set its `+4` to 10 and its `+5` to 9.
3. **Entry 9 `+4`: 10 becomes the new entry.** His Z stays the regular Super Saiyan after the chamber.
4. **Entry 10 becomes Z+.** Set its `+5` to 9 (it already is) and its portrait `+2` to **122**, the
   owner's drawing, which `vegeta_zplus` already wires. Leave its form object alone: `0x030021E8`
   carries the +15/+10/+15 and that is the point.
5. **Entry 11 keeps `+4` = 8.** Pre-chamber Vegeta reaches Z and stops. That is the gate, and it is
   data, not code.
6. **Entry 23, the Z+ entry the current module appends, is no longer needed** in this shape. Either
   reuse it as the new post-chamber Z entry or drop it. Say which and why.

Trunks is the mirror and is OUT of scope. His portrait does not exist.

## Things already true that you must not break

- `set:139`, `set:140` and `set:137` all carry a live anim 9 power-up row now, borrowed from 137.
  A transform onto a set with a null anim 9 crashes: the lookup `@0x0800775A` has no existence test.
  **Entry 10 will now be stepped INTO, so its set 139 row must stay live.** Assert it.
- `set:139` and `set:140` decode to the same tiles in all 64 rows (B0221), so Z and Z+ look alike
  until the owner draws something. That is expected and is not yours to fix.
- The owner is drawing new anim 9 frames right now. Do not touch art, and do not change the borrow.

## Scope

`scripts\permanent\patches\vegeta_zplus.py`, its tests, and a TRIAL build, all inside your worktree.

Do NOT touch `bf_ki_pool.py`, `piccolo_z_start.py`, `fullpower_ssj.py`, `build_list.txt`,
`build_list_core.txt` or `build_list_dev.txt`. Do not run the full suite: run your own test modules
by name. I run the full suite in the main tree.

Build your trial ROM inside the worktree and print its SHA-1. Never overwrite a ROM, save or save
state: check absence, then create.

## Files to read first

- `scripts\permanent\patches\vegeta_zplus.py` : what exists today, including `borrow_anim_row`
- `scripts\permanent\patches\ssj2_form.py` : how the appearance table is relocated and appended
- `scripts\permanent\tests\test_vegeta_zplus.py` : the test shape to extend
- `docs\tasks\global.md` : the global constraints, which all apply

## Done means

1. Pre-chamber Vegeta reaches Z and cannot reach Z+. Post-chamber he reaches Z then Z+.
   A test proves BOTH, by walking the entry chain from entry 8 and from entry 9.
2. No flag is read and no ability bit is written. A test asserts the two `ext 73` sites are vanilla.
3. Entry 10 carries portrait 122 and form object `0x030021E8`.
4. Every set in the chain has a live anim 9 row.
5. The trial ROM built, SHA-1 printed, its build log line IN YOUR REPORT.
6. `rows.md` beside this brief, `## Section N` table blocks, including the line 600 correction.
7. A `report.md` beside this brief.

Report any place where my measurements disagree with the ROM. Deviate and flag it rather than
forcing the design onto a table that does not match.

One report message, then stop. Do not add a byte order mark.
