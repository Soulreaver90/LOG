# Growing the scouter database menu so the three future entries appear

The owner, 2026-11-09, approved this together with a full journal entry: "Got it, do both then".

Entries 128 `Future 17`, 129 `Future 18` and 130 `Future Cell` already exist and already SCAN in
battle. `scouter_future` relocated and grew the 128 entry table at `rom:0x6F8E40` to 131. **Only the
menu is left**, and the menu is not a table: it is a RAM object whose two inner lists are exactly
full, with zero spare bytes.

## The object, from bible rows and confirmed by the listings below

| Piece | Offset | Note |
| --- | --- | --- |
| whole object | `0x6B0` bytes | allocated in `sub_08019204` |
| list 1, 4 bytes per SCANNED entry | base `+0x80` | its 128th entry ends exactly on `+0x280` |
| list 2 COUNT word | `+0x280` | sits on list 1's last byte + 1 |
| list 2, 8 bytes per distinct NAME | base `+0x284` | its 128th entry ends at `+0x684` |
| a live block the menu writes | `+0x680` | overlapped by list 2's tail |

**Raising the list bound at `rom:0x19260` alone writes past live memory.** It passes every test and
only shows on a late game save, which is why it was deferred rather than done cheaply.

## Every site that encodes the layout, MEASURED 2026-11-09

Scanned with `scripts\one-time\2026-11-09-scouter-menu\layout_sites.py` over the whole menu family:
`sub_0801915C`, `sub_08019204`, `sub_08019320`, `sub_0801963C`, `sub_0801970A`, `sub_08019844` and
`sub_08019934`. Full output: `scratch\2026-11-09-scouter-menu\layout_sites.txt`.

### `0x6B0`, the object size: ONE site

| Site | Shape |
| --- | --- |
| `rom:0x1920A` | `mov r0,#0x6b ; lsl r0,r0,#4` |

### `0x680`, the live block: FOUR sites

| Site | In | Shape |
| --- | --- | --- |
| `rom:0x192A8` | `sub_08019204` | `mov r1,#0xd ; lsl r1,r1,#7` |
| `rom:0x1966E` | `sub_0801963C` | `mov r1,#0xd ; lsl r1,r1,#7` |
| `rom:0x19726` | `sub_0801970A` | `mov r1,#0xd ; lsl r1,r1,#7` |
| `rom:0x19866` | `sub_08019844` | `mov r0,#0xd ; lsl r0,r0,#7` |

### `0x280`, list 2's count word: TWO sites

| Site | In | Shape |
| --- | --- | --- |
| `rom:0x193AE` | `sub_08019320` | `mov r1,#0x5 ; lsl r1,r1,#7` |
| `rom:0x19848` | `sub_08019844` | `mov r0,#0x5 ; lsl r0,r0,#7` |

**So seven sites, not the two the backlog named.** The backlog said the offsets are "also read by
`sub_08019320` and `sub_0801963C`". That was right but incomplete: `sub_0801970A` and `sub_08019844`
read `+0x680` as well, and `sub_08019844` reads BOTH offsets.

## What this census CANNOT see, and must be read by eye

The scan finds the `mov ; lsl` shape only. **A site that forms an offset by `add`, from a pool word,
or from another register will not appear.** These `add` immediates sit in the same functions and are
the likely list 1 base (`+0x80`) sites, since `0x7c + 4` is `0x80`:

| Site | In | Shape |
| --- | --- | --- |
| `rom:0x19230` | `sub_08019204` | `add r1,#0x7c` |
| `rom:0x19336` | `sub_08019320` | `add r1,#0x7c` |
| `rom:0x19678` | `sub_0801963C` | `add r0,#0x7c` |
| `rom:0x193AA` | `sub_08019320` | `add r3,#0x80`, immediately before the `0x280` site at `0x193AE` |
| `rom:0x19226`, `rom:0x192B6`, `rom:0x193A4`, `rom:0x19640`, `rom:0x197AE` | several | `add ...,#0x70` |

**Read every one of these before changing any constant.** The `0x70` and `0x7c` values are small
enough to be ordinary struct fields rather than list bases, so they must be distinguished, not
assumed.

## The shape of the fix, from the backlog's own working

Grow the object and move what sits after each list:

- `0x6B0` becomes `0x6E0` (`mov r0,#0x6e ; lsl r0,r0,#4` keeps the same two instruction shape)
- list 2's base moves from `0x280` to `0x290` (`mov r0,#0x52 ; lsl r0,r0,#3`)
- the block at `0x680` moves to `0x6B0` (`mov r1,#0xd6 ; lsl r1,r1,#3`)
- then the list bound at `rom:0x19260` can go from 128 to 131

Every replacement must keep the same instruction LENGTH, because these sit inside vanilla functions
that are not being relocated. All four shapes above are two Thumb instructions, same as the originals.

## Why this is worth care rather than speed

The failure mode is silent. The object is allocated once and the overrun only happens when a save has
enough entries scanned to reach the end of a list, so a build can pass every test and look perfect
until a late game save loads. **A test must prove the new bases and the new size agree with each
other arithmetically**, not merely that the ROM assembled.
