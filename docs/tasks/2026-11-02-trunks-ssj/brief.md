# Trunks tank: Super Saiyan (set 134)

Give Super Saiyan Trunks the same tank top base Trunks already wears. The owner asked for this on
2026-11-02, right after the base back walk went into the manifest.

## What is already true, measured, do not re-derive

Set 134 mirrors set 128 pose for pose. Both resolve through the set table word at `rom:0x959C`,
entry `id - 7`. Set 128 is `rom:0x35BBE0`, set 134 is `rom:0x37FB74`, both in the USA base ROM.

Header pairs, set 128 then set 134, same `(anim, dir, index)` in each:

| pose | set 128 | set 134 |
|---|---|---|
| anim 0 d0 i0 front idle | `0x34F9F0` | `0x373CDC` |
| anim 0 d0 i1 front stand 1 | `0x34FB10` | `0x373E0C` |
| anim 0 d1 i0+i1 back idle | `0x34FC2C` | `0x373F38` |
| anim 0 d2 i0 side idle | `0x34FD38` | `0x374054` |
| anim 0 d2 i1 side stand 1 | `0x34FE38` | `0x374158` |
| anim 1 d0 walk 0-3 | `0x34FF9C` `0x3500A8` `0x3501C0` `0x3502D0` | `0x3742BC` `0x3743D8` `0x3744F8` `0x374614` |
| anim 1 d1 walk 0-3 | `0x3503EC` `0x3504F4` `0x350604` `0x350710` | `0x374738` `0x374848` `0x37495C` `0x374A6C` |
| anim 1 d2 walk 0-3 | `0x350820` `0x350924` `0x350A24` `0x350B28` | `0x374B80` `0x374C88` `0x374D88` `0x374E90` |

Dir 3 reuses the dir 2 record with the OBJ h-flip bit, in both sets. Anim 4 also has an idle
variant per direction: find its headers with `set_records`, do not assume them.

**The bodies are the same.** Comparing vanilla 128 against vanilla 134 at matching poses, rows
16-31: all 12 walk frames differ by 0 px, back idle by 0 px, side idle and side stand 1 by 2 px
(both jacket indices, which we replace anyway). Only front idle and front stand 1 differ really:
23 px, where the SSJ left arm sits one column right at y22-y24, plus belt `(10,21)` `0x27` -> `0x25`.

So for every pose except the two front idles, the SSJ tank frame is exactly: **set 134's own hair
and head, plus the approved base tank frame's body.** The approved base art is in
`art\trunks_tank\`, 17 PNGs, all listed in `manifest.json`.

## Files you need

- `art\trunks_tank\manifest.json` and its 17 PNGs. The manifest is the source of truth for
  headers and keys, and it was generated from the ROM.
- `scripts\permanent\patches\trunks_tank.py`. Its header says set 134 is out of scope. That line
  is what you are changing.
- `docs\sprite-guide.md`. Read it before any pixel work.
- `art\vanilla-sets\set128\` and `art\vanilla-sets\set134\` for the vanilla frames.

## Do

1. Derive the 12 SSJ walk frames and the 2 side idles plus the back idle, by the rule above. Prove
   each one: every pixel must come from either set 134's vanilla frame or the matching approved
   base tank PNG, and nothing else. Print that proof per frame.
2. Front idle and front stand 1: derive what you can and **stop at the arm**. Report what the 23 px
   need and let the owner decide. Do not invent arm pixels.
3. Read every set 134 header and key with `set_records` against the USA ROM. Never copy a header
   from this brief into the manifest without that check.
4. Add the SSJ rows to `manifest.json` and widen `trunks_tank.py` to clone set 134 as well as 128.
   Keep its existing guarantees: the manifest stays the source of truth, each header is validated
   against the set's own records, and a second run still raises.
5. Update `scripts\permanent\tests\test_trunks_tank.py`. Its pinned counts are currently
   `PNG_COUNT, HEADER_COUNT, KEY_COUNT = 17, 20, 28` and there is a sorted `(view, pose)` list.
   Both need the SSJ rows. Give SSJ rows a field that separates them from base rows in that list.
6. Run the full suite once: `py -3.14 -P -m unittest discover -s <LOG>\scripts\permanent\tests
   -t <LOG>\scripts\permanent`. Never pipe it into `tail`: the pipe reports tail's exit code and a
   red suite reads as green. Redirect to a file and read `$?` separately.

## Do not

- Do not touch `data\`, any ROM, save or state. Do not build a ROM.
- Do not edit any file in `art\trunks_tank\` that already exists. The base art is the owner's,
  approved pixel for pixel. You add new SSJ PNGs beside it.
- Do not redraw the SSJ hair. The owner redrew the base back hair on 2026-11-02 to make it rotate
  with the torso, and the SSJ hair has not had that treatment. It is his art and his call. Say in
  your report that the gap exists and leave it.
- Absolute paths only. Never `cd`, `Set-Location` or `Push-Location`.
- Python is `py -3.14 -P`. `py -3` is 3.15 and has no Pillow.

## Report

State per frame where every pixel came from. Label each claim CONFIRMED (read from ROM or file
bytes) or LIKELY. Give the suite's real exit code and its `Ran N tests` line. List what you left
for the owner: the front idle arm, and the SSJ back hair.

One report message, then stop. Do not add a byte order mark.
