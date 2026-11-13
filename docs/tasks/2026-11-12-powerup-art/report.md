# His power-up frames are in the ROM: Vegeta on set 140, Piccolo on set 104

Built 2026-11-12. Two trial ROMs, one per character. Not one of his pixels was changed.

## What shipped

| Character | Set, row | His four frames, in order | Trial ROM, SHA-1 |
| --- | --- | --- | --- |
| Vegeta Z+ | `set:140` anim 9, row `rom:0x39D3D0` | `Frame_1`, `Frame_2`, `vegeta_pu_sway_left`, `vegeta_pu_sway_right` | `log2_vegeta_powerup_v1.gba` `9d196a4087bbc63703a1ae39289c252c043c1107` |
| Piccolo Z+ | `set:104` anim 9, row `rom:0x31D950` | `P_Frame1`, `P_Frame2`, `P_Frame3`, `P_Frame4` | `log2_piccolo_powerup_v1.gba` `39b3a4273e7c4a4330407e89789953e0d2faa1ba` |

Both ROMs are in `builds\mockups\2026-11-12-powerup-art\`. Each is paired with a `.sav` seeded from
`builds\log2_poc_r40.sav`, which the build script chose and printed. Both build-log lines are in
`docs\build-log.md`.

> [!WARNING]
> **Both SHA-1s are provisional.** Both lists include `build_list_dev.txt`, and a second agent was
> mid-edit on `bf_ki_pool.py` and `fullpower_hud.py` when these ran at 7:03 PM. So neither SHA-1
> reproduces once that work lands, and the ki and HUD behaviour in the Vegeta ROM is not a stable
> play-test baseline. **Rebuild both lists after the merge.** The anim 9 rows themselves do not
> depend on that module and will not change.

Review sheets, rendered from the built ROMs and looked at by eye:

- `vegeta_anim9_sheet.png` : sets 137, 139 and 140, anim 9, all four directions
- `piccolo_anim9_sheet.png` : sets 103 and 104, anim 9, all four directions
- `vegeta_f0_green_eyes.png` : his open eyes in frame 1, below

**Bible rows are in `rows.md` beside this file, tagged `PWA`, not `PUA`.** `PUA` was free when I
picked it and was used at 7:27 PM by the row carrying his green-eye answer, and
`merge_bible_rows.py` refuses a tag the bible already holds.

---

## Where the frames and the row go, and what moved

**Nothing moved.** Appending a row is cheaper than the brief feared. The row already exists as four
null words inside the set header, so filling it is a 16 byte write in place. Everything else is
appended to the expansion area, which no other data names.

Per character:

| Part | Size | Where |
| --- | --- | --- |
| 4 raw type 0 frames | `4 x (8 + 0x400)` = 4128 bytes | expansion area |
| 1 record list, 4 records | 48 bytes | expansion area |
| a 12 byte stop after the list | 12 bytes | expansion area |
| the anim 9 row itself | 16 bytes, written in place | base ROM |
| **total** | **4204 bytes, 4188 of them appended** | |

In the 7:03 PM builds, Vegeta's frames landed at `rom:0x93D244`, `0x93D64C`, `0x93DA54`, `0x93DE5C`
with the list at `rom:0x93E264`, and Piccolo's at `rom:0x93C9D4`, `0x93CDDC`, `0x93D1E4`, `0x93D5EC`
with the list at `rom:0x93D9F4`. Both are well inside the expansion area `rom:0x800000-0xEFFFFF`.
**Those six addresses move with every earlier module**, because the allocator is a bump allocator:
they had already moved by 7:35 PM, under the other agent's work. Nothing reads them by value. The
two row offsets, `rom:0x39D3D0` and `rom:0x31D950`, are fixed and do not move.

**The only base ROM bytes either module changes are its own 16 byte row.** A test proves it per
module by comparing the whole first 8 MB before and after. CONFIRMED.

> The 12 byte stop is for our own readers, not for the game. The game's frame count is in code, not
> in the set (B0042, B0063); B0042 reads it out of the enter and tick pair for anims 0, 1 and 16 and
> labels the rest LIKELY, and anim 9 is among the rest. `frames_of` walks records until one stops
> looking valid and is known to read past a list end when the next record still looks valid (B0173).
> In vanilla a list ends because the next thing in the ROM is not a record: `set:139`'s anim 21 list
> at `rom:0x39D2C4` runs straight into `set:140`'s header 48 bytes on. An appended list has no such
> neighbour, so a later allocation could read as a fifth record. CONFIRMED.

---

## Where my facts disagreed with the brief

**1. Vegeta had five candidate files for four records.** The brief named `his-edit\v2\build-ready\`,
which holds three frames, plus `Frame_1` and `Frame_2`. I did not choose by name. I decoded every
frame of the review GIF filed with his frames, `his-edit\v2\full_powerup.gif`, sampled each back
down to 32x32 and matched it to a source file. The six GIF frames are `Frame_1`, `Frame_2`,
`sway_left`, `sway_right`, `sway_left`, `sway_right`, and each match is exact apart from the GIF's
background. CONFIRMED.

So the row is `Frame_1`, `Frame_2`, `sway_left`, `sway_right`, and `vegeta_pu_straight` is a pose
reference that is not in the cycle. **That ORDER is LIKELY, not CONFIRMED**: the GIF is a review
picture an earlier agent built, and what he signed off on 2026-11-12 was the frames. Two things back
it. Vanilla `set:137` anim 9 is two build frames then a sway pair, and his set maps onto that one for
one. And the brief named five files for four slots, with "straight" the un-swayed one. **If he wants
"straight" in the row instead, it is one line in `POWER_UP_PNGS` and a rebuild.**

`vegeta_pu_straight_rgba.png` differs from his `Frame_3.png` by a single pixel, so "straight" is his
corrected frame 3, the one he then swayed both ways. CONFIRMED.

**2. The Piccolo frames are NOT keyed, and the build reads a copy, which I checked against his
original.** The brief said to check for the key before converting, and the check changed the answer:
`P_Frame1..4.png` carry real alpha and zero magenta pixels, so `--key F800F8` was never needed for
them. An `indexed\` folder also already sat beside them.

His true originals are at **`art\kits\P_Frame1..4.png`**, the kits root, not inside the kit folder.
The kit README says so and the brief points at the copies. I compared all three versions of each
frame pixel for pixel: original, kit copy and indexed copy are **identical, 0 of 1024 pixels
differing, on all four frames**. So nothing is stale and the copy the build reads is his art.
CONFIRMED.

**3. B2388 cannot be CONFIRMED for `set:140` or `set:104`.** The brief asked me to confirm that anim
9 uses the same four frame headers in all four directions on those two sets before relying on it.
I cannot: their anim 9 rows are null, so there is nothing in them to read. What I can confirm is the
neighbouring evidence, and it all points one way: their anim 21 rows each name ONE list in all four
directions, and the sibling sets 137 and 103 do the same for anim 9. I built the rows as one shared
list on that basis and label it **LIKELY, not CONFIRMED**. If a direction ever needs its own drawing,
the row is four separate words and takes it without any code change.

**4. The dev master repaints one OBJ palette entry, and it broke my first check.** Index 172 is
`(32, 208, 168)` in the base ROM and `(248, 200, 192)` after `art_inject`. His indexed frames were
converted against the base ROM, so their embedded palette disagrees with every build at that one
entry. My first version of the loader compared all 256 entries and refused his art over a colour it
never uses. The rule is now "every index the drawing USES must name the same colour in the frame and
in this ROM", which is the real invariant. CONFIRMED, and it is a trap for any future art module.

**5. `set:139` keeps its borrow, as the brief says, and that is still right.** It is where Vegeta
STANDS in Z+. A power-up played there would flash black hair. **No input reaches it today: LIKELY.**
`vegeta_zplus`'s gate sends entry 23 straight to the vanilla revert action, which is the only path I
read; another caller of the power-up state would not show in that reading. The borrow only stops the
crash. The sheet shows set 139 and set 137 drawing the same four frames, which is the borrow working
as intended.

---

## His eyes are open in frame 1, and that is deliberate

**`Frame_1.png` is the only one of his eight frames with green in it.** Vegeta's two eyes are palette
index 50 `(16, 120, 0)` at `(15,15)` and `(17,15)` and index 49 `(48, 168, 0)` at `(15,16)` and
`(17,16)`. His `Frame_2`, his two sway frames, his four Piccolo frames and all four vanilla
`set:137` anim 9 frames have no green anywhere, and they draw those same four cells in skin and
shadow indices.

It is built exactly as he saved it. **I changed nothing**, and nothing needs changing. The picture is
`vegeta_f0_green_eyes.png`: his frame 0, his frame 1 and vanilla frame 02 side by side, with the
palette index in every cell.

**He answered while this was being built**, at 7:27 PM: "deliberate, his eyes are open then he
closed them in frame 2-4." So the green is his Super Saiyan irises, and the frames read open eyes,
then shut as he screams. The answer is already a bible row in section 12 under the tag `PUA`.

> [!WARNING]
> **The two greens are the values Piccolo's sprite uses**, so any later stray hunt or palette audit
> will flag them in a Vegeta frame. That is a false positive. The row in section 12 says so.

---

## What was built

### `scripts\permanent\art\to_indexed.py` grew one reusable reader

`frame_indices(src, want, pal, key)` returns `((w, h), one palette index per pixel)` and raises,
naming the file, for an unknown colour, a part transparent pixel, a reserved index or an indexed
file whose palette disagrees with this ROM at an index the drawing uses. The command line tool now
runs through it, so **a build and a review refuse the same frame for the same reason**. Nothing is
ever snapped to a near colour: a snapped pixel is his art changed without him seeing it.

An indexed file keeps its own indices rather than going back through the colour map, because a
colour that sits at several palette indices would come back as the lowest one, which is a different
index for the same picture.

### `scripts\permanent\patches\vegeta_zplus.py` grew the row writer

- `shared_list(rom, set_id, anim)` : the one record list all four directions name, and its records.
  Raises rather than taking direction 0 and drawing the other three wrong.
- `hand_frames(rom, paths)` : his drawings as ROM tile bytes, through `frame_indices`.
- `plan_anim_frames(...)` : every check, and no write.
- `write_anim_row(...)` : the frames, the list, the stop and the row.

`plan_anim_frames` keeps all four guards `borrow_anim_row` has, and adds two:

| Guard | Why |
| --- | --- |
| the target row is empty | never overwrite a row the set already has |
| the lending row is whole in all four directions | a null lender has no shape to copy |
| the two sets share one OBJ slot | the OBJ buffer would not fit |
| the records match the geometry the target already draws | the frames would tear |
| the record count equals the lending row's | the frame count is in code, not in the row |
| each frame is `w * h` bytes and fits the slot | a short frame draws garbage |

Each record's `dx`, `dy`, `w`, `h`, `attr0` and `attr1` are **copied from the lending set's own
records**, never typed in. `BORROWERS` is now `(139,)`: set 140 gets his frames instead of the
borrow.

### `scripts\permanent\patches\piccolo_powerup_art.py` is new

Art only. **No appearance entry, no form object, no portrait, no unlock.** It fills the null anim 9
row that Piccolo Z+ needs before a power-up on `set:104` can play at all. Its own test asserts that
its note names a row, a list and four frames and nothing else, and that it adds exactly one name to
the build's notes.

I named it `piccolo_powerup_art`, not `piccolo_zplus_art`, because it builds no part of Z+.

### Build lists

- `build_list_trial_vegeta_zplus.txt` : unchanged. The Vegeta work is inside `vegeta_zplus`.
- `build_list_trial_piccolo_art.txt` : new, `include build_list_dev.txt` plus the one module.
- `build_list.txt`, `build_list_dev.txt` and `build_list_core.txt` are untouched, so both master
  SHA-1s are unchanged. A test per module pins that.

---

## Tests

### New

| Test | What it proves |
| --- | --- |
| `test_set_140_names_one_new_record_list_in_all_four_directions` | the row is no longer a borrow, and all four directions name one new list of four records |
| `test_set_140_anim_9_decodes_back_to_his_own_pixels` | every record, in every direction, decodes back to the file HE saved |
| `test_base_vegetas_power_up_is_byte_for_byte_unchanged` | `set:137` anim 9: the row, the record list and every frame's packed bytes |
| `test_the_new_frames_use_existing_obj_palette_indices_only` | the shared OBJ palette is not changed and no reserved index is used |
| `test_only_the_zplus_set_borrows_base_vegetas_list` | one borrow note now, set 139, and 140 is not it |
| `test_piccolo_powerup_art`, 11 tests | the same for `set:104`, plus `set:103` byte for byte, plus art-only, plus failing closed |

The "decodes back to his pixels" tests read the built ROM through `unpack_frame` and
`tiles_to_image`, then compare RGB against his original RGBA files, including the `_rgba` Piskel
exports rather than our converted copies. A conversion bug cannot pass them.

### Updated on purpose

`test_both_borrowed_rows_are_base_vegetas_own_list` expected two borrow notes and is now
`test_only_the_zplus_set_borrows_base_vegetas_list`. Two site-list tests had to learn about the new
row. These are my own changes, not failures.

### One test of mine was over-specified, and the moving tree caught it

`test_the_base_8mb_differs_only_at_super_nameks_own_row` first asserted that the diff IS the 16 row
bytes. It passed at 7:03 PM and failed at 7:35 PM, because by then the record list had landed at an
address ending in `0x00`, so the low byte of each of the four pointer words already held the value
it needed and stayed equal. **A byte that does not change is simply absent from a diff.** The
assertion is now the right one, the same shape `test_vegeta_zplus` uses: every differing byte lies
INSIDE the row. Fixed, re-run, 11 of 11 pass.

### The suite

Run once, at the end, in one process, with a real exit code and **no pipe into anything**.

```
Ran 2035 tests in 949.453s
FAILED (failures=30, errors=4, skipped=10, expected failures=1)
exit=1
```

**A second agent was editing `bf_ki_pool.py`, `fullpower_hud.py`, `test_bf_hud.py` and
`test_bf_ki_pool.py` while it ran**, as the brief said it would be.

**None of the 34 is new from my work.** All 11 of my `test_piccolo_powerup_art` tests pass, and that
module does not appear in the failure list at all. 32 of the 34 sit in modules I did not touch. Two
are inside `test_vegeta_zplus.py`, which I did touch, and they are still not mine:

- `test_the_table_moved_and_every_namer_followed`
- `test_a_stray_namer_of_the_table_raises`

Both fail on the pinned literal addresses `0x90A250` and `0x90A3E0`, which are now `0x90B318` and
`0x90B4A8`, `0x10C8` further on. The test's own comment names those literals as living in
`ssj2_form`, `status_bonus`, `fullpower_ssj`, `bf_ki_pool` and `fullpower_hud`, all dev master
modules. `bf_ki_pool` is in core, so its window growing moves every later literal in the dev master.
The dev master now builds to `db182dc6`, against the `ffbd2bfc` pin and the `26e6ffc8` the red ki
bar work reported, so it has moved twice today under other hands.

**The proof my edits cannot move a dev master address**, which that claim needs:

| Check | Result |
| --- | --- |
| `grep -rn to_indexed scripts\permanent\` | only `art\to_indexed.py`, `patches\vegeta_zplus.py` and `tests\test_vegeta_zplus.py` |
| `vegeta_zplus` or `piccolo_powerup_art` in a master list | no match in `build_list.txt`, `build_list_dev.txt` or `build_list_core.txt` |
| everything else I changed | two test modules, one new trial list, `docs\` |

So no module of either master reads a byte I changed. CONFIRMED. These are the same stale-pin family
as the roughly 17 golden pins the brief told me to leave alone, and I left every one alone.

The 34 by module: `fullpower_hud` 7, `bf_hud` 6, `roundtrip` 5, `golden` 2, `beam_struggle` 2,
`piccolo_z_start` 2, `vegeta_zplus` 2, and one each in `battle_start`, `celljr_fight`,
`chapter_cards`, `gi_base_audit`, `relay_cooldown`, `sprite_lab`, `vegeta_19_reveal` and
`vegeta_ssj_scene`. Every one is a pinned SHA-1, a pinned address or a pinned "before" ROM.
`piccolo_z_start`'s pair belongs to the red ki bar work, not to my `piccolo_powerup_art`: its
`test_the_base_and_non_pool_forms_still_get_nothing` fails at `entry=10`, and the red ki bar rows
say entry 10 is now a pool form.

---

## What this does NOT do

- **Piccolo Z+ itself does not exist**, so nothing in the game reaches `set:104` anim 9 yet. The
  Piccolo trial ROM is therefore **not play-testable for this change**: `set:104`'s row was null in
  vanilla and never crashed, so no vanilla path plays it (LIKELY). The review sheet is the only way
  to see his frames until the form is built.
- The Vegeta ROM IS play-testable: step up to Z+ out of Super Vegeta and the power-up is his.
- `set:139`, Trunks `set:133` and Goku `set:61` keep their own null or borrowed rows. A test names
  all of them.
