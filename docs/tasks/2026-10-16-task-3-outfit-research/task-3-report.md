# Task 3 report: outfit selection

Status: DONE_WITH_CONCERNS. Date 2026-10-16.

Full evidence: `docs\research\re-outfit.md`. Bible: about 30 new or changed lines in `docs\RE-BIBLE.md` (source tag `OUT`).

## Findings

| # | Finding | Label |
|---|---|---|
| 1 | `get_set(id)` 0x08009324: id 0 = player obj+0x48 or the leader's appearance; ids 1-6 = character record id-1 (struct 0x03000E90), appearance +1 through 0x0802645C; id >= 7 = set table. The "run-time 28-byte table" is the save struct's character records | CONFIRMED |
| 2 | Every playable path reads appearance +1: map load 0x0800C584, player refresh 0x080085FC, set leader 0x0800A680 (ext 70, ext 115), Switch Characters 0x08011172, transform 0x08014D58, menus 0x08010BCE and 0x08001AB8 | CONFIRMED |
| 3 | Gohan appearance entries: 0 = set 53, 1 = 55, 2 = 56 (+4 = 5), 3 = 57, 4 = 58 Rage, 5 = 59 SSJ (+4 = 4, +5 = 2). +4 transform target, +5 revert target | CONFIRMED |
| 4 | ext 73 `(char, set)` 0x0800A8EC: reverse lookup 0x080042BC (first entry with +1 == set) writes record +8; if char is leader, player obj+0x48 = get_set(raw set) | CONFIRMED |
| 5 | Reverse lookup with no match hangs the game: assert "Unable to find sprite index in character display data" (0x0801F878, ends `b .` at 0x0801F972) | CONFIRMED |
| 6 | Scripts find actors by set pointer (message 5, 0x08007894 `ldr r1,[r0,#0x48] ; cmp r1,r2`) | CONFIRMED |
| 7 | Cutscenes name Gohan by literal 56 (chamber exit 0x083DB5D0, walk-off 0x083DBD63, Cell Games 0x083E866C-0x083E939C, post-Cell 0x083EC021) or set the player sprite with ext 73 (0, 56) at 0x083EBFFC. No script uses actor id 1 by a constant | CONFIRMED (constant search shape; a run-time variable id would not appear) |
| 8 | Chamber exit 0x083DB59F spawns Goku 60 and Gohan 56 as NPCs, then ext 73 (0, 56). Leader is not Gohan there | CONFIRMED (script), LIKELY (leader) |
| 9 | Gohan becomes the player in the Cell Games at ext 70 (0) 0x083E93A8; post-Cell ext 70 (1) at 0x083EC00F | CONFIRMED |
| 10 | Map NPCs: map 2,1 set 55; map 14,1 set 56 (leader not Gohan, flag 195 clear); map 14,3 set 56 (flag 192 clear) | CONFIRMED |
| 11 | Set table ends rom:0x3B50E7; rom:0x3B50E8 is another table. Only literal rom:0x959C | CONFIRMED |
| 12 | Scouter entry 36 "Gohan" uses id 1, so it follows the appearance | CONFIRMED |

## Patch site for Task 5 (original bytes CONFIRMED)

| rom offset | Original | New |
|---|---|---|
| `0x1D96A5` (appearance 2 +1) | `38` | gi base set id (157 = 0x9D, first free) |
| `0x1D96E1` (appearance 5 +1) | `3B` | gi Super Saiyan set id (for example 158) |
| `0x42F0` (literal of 0x080042BC, ldr at 0x080042BE only) | `7C 96 1D 08` | GBA address of an unchanged copy of rom:0x1D967C-0x1D9833 (440 bytes) |
| `0x959C` (set table literal, ldr at 0x08009364 only) | `90 4E 3B 08` | GBA address of rom:0x3B4E90-0x3B50E7 copied, plus one word per new id (id N = word N-7) |

All four are needed. Without the third, both ext 73 (0, 56) calls hang the game. Suggested extra test: the table at the rom:0x42F0 literal still maps set 56 to entry 2, 58 to 4, 53 to 0.

## Animation end (Ruling 7)

- 0x0800775A computes `row[obj+0x10] + obj+0x14 * 12`, where obj+0x4C is the animation row and obj+0x10 the direction. There is no bound and no terminator test. CONFIRMED.
- Per-state tick routines set obj+0x14 and end the animation by count. Anim 0 = 2 (0x08007570), anim 1 = 4 (0x08007532, 0x0801C120, 0x0801CF8C), anim 16 = 7 (0x08010774) or appearance +6 = 6 (0x080083C2). These equal the `frames_of()` counts in sets 53, 56, 58, 59. CONFIRMED. Other animations: count = `frames_of()` count, LIKELY.
- The 12-byte item `01 00 00 00 00 02 00 00 45 11 00 20` is the next frame header (type 1, size 0x200, first stream word 0x20001145 whose top byte is the literal-mode code). One list per set ends on the set's own header. CONFIRMED over sets 53-59.
- A cloned record list does not need to copy the item. `clone_set` is correct as it stands.

## Concerns

1. My question: the Cell Games Arena NPC Gohan (map 14,1) stays in armor while another character leads.
2. My question: in the Cell Games the NPC Gohan is armor, then the player Gohan is the gi (0x083E93A8), then Rage (58), then armor in the post-Cell scene.
3. Scouting an armored NPC Gohan no longer matches scouter entry 36. Minor.
4. Entry 5 +4 = 4 (Rage). Task 4 and Task 6 must check the transform input.
5. Not tested in game. The effects list in re-outfit.md section 6 is LIKELY.

## Files changed

- Created `docs\research\re-outfit.md`.
- Edited `docs\RE-BIBLE.md` (source list, sections 4, 6, 8, 9, 11, 13).
- Created scratch tools and output in `scripts\one-time\2026-10-16-task-3-outfit-research\` (extscan.py, setargs.py, sweep.py, mapsets.py, tails.py, tails2.py, decompiles and scan text).
- Ghidra project `scratch\ghidra\LoG2.gpr` saved new function definitions from the Decomp runs.
- Nothing under `data\` or `scripts\permanent\`. Tests: 17 OK.

## Open questions

- My answers to concerns 1 and 2.
- 106 of the 117 strh-to-obj+0x14 sites are not checked (11 checked).
- ext 29 / ext 30 broadcast message 4 (`2n+1` / `2n`). "Party add / remove" remains LIKELY.
