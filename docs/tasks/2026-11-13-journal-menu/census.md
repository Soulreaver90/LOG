# Menu layout census: the journal, and a correction to the scouter design

Measured 2026-11-13 on the base USA ROM. No ROM was written. Two tools, both in
`scripts\one-time\2026-11-13-journal-menu\`:

- `census.py` reads a listing of each named function and finds `mov ; lsl`, pool loads and `add`
  chains. It is scoped to the function spans I chose, so its counts are a floor for that window.
- `imagewide.py` decodes every aligned halfword pair in all 8 MB. It cannot miss a site because I
  failed to guess its function. A third shape, an aligned word scan, finds the pool constants.

> [!WARNING]
> **The approved scouter design misses a site.** `docs\design\2026-11-09-scouter-menu-grow.md` lists
> FOUR readers of the `+0x680` live block. There are FIVE. Fix the design before anyone builds it.

---

## 1. The scouter correction

| Site | Function | Shape |
|---|---|---|
| `rom:0x192A8` | `sub_08019204` | `mov r1,#0xd ; lsl r1,r1,#7` |
| **`rom:0x192DE`** | **`sub_080192D6`** | **`mov r1,#0xd ; lsl r1,r1,#7`, then `add r4,r0,r1`** |
| `rom:0x1966E` | `sub_0801963C` | `mov r1,#0xd ; lsl r1,r1,#7` |
| `rom:0x19726` | `sub_0801970A` | `mov r1,#0xd ; lsl r1,r1,#7` |
| `rom:0x19866` | `sub_08019844` | `mov r0,#0xd ; lsl r0,r0,#7` |

**Why the first census missed it.** That census read seven listing files, one per named function. The
file for `sub_08019204` declares `size 0xd2`, so it ends at `rom:0x192D6`. The site is 8 bytes past
that end, inside a function that starts at `rom:0x192D6` with `push {r4,lr}` and that the family list
never named. The tool was right. The family list was short.

`sub_080192D6` reads the block it builds: `ldr r0,[r4,#0x28]` and `ldr r0,[r4,#0x1c]`. So it is a
real reader, not a coincidence of the value.

**The cost if this ships as designed.** Four sites move to the new block address and the fifth keeps
writing at `+0x680`, which the grown list 2 now occupies. That is the silent late game overrun the
design was written to prevent.

**The lesson, which is the project's own rule.** One grep enumerates its own shape. A family list
built from named functions misses any code the index does not name. The image wide scan costs one
second and does not care what anything is called.

---

## 2. The journal menu, measured

`sub_080049FC` allocates the object. Both lists hold exactly 43 quests (bible B2338, B2351).

### How each list header is really built

Read from the listing, not from a grep:

| Address | Instruction | Running value |
|---|---|---|
| `rom:0x4A1A` | `add r0,r4,#0` | object base |
| `rom:0x4A1C` | `add r0,#0xff` | `+0xFF` |
| `rom:0x4A1E` | `add r0,#0x1d` | `+0x11C` |
| `rom:0x4A36` | `add r2,r0,#0` | `+0x11C` |
| `rom:0x4A38` | `add r2,#0x20` | `+0x13C` |
| `rom:0x4A48` | `add r2,#0x18` | **`+0x154`, the active list header** |
| `rom:0x4A52` | `mov r0,#0x2b ; lsl r0,r0,#4` | **`+0x2B0`, the done list header** |
| `rom:0x4A5C` | `add r0,#0xff` | `+0x3AF` |
| `rom:0x4A5E` | `add r0,#0x5d` | **`+0x40C`, the next field** |
| `rom:0x4AE2` | `cmp r6,#0x2b` | the loop bound, 43 |

`0x2B0 - 0x154` is `0x15C`, which is `4 + 43 * 8` exactly. `0x40C - 0x2B0` is `0x15C` again.

### Every site, by the three shapes

| Value | Sites | Shape that found it |
|---|---|---|
| `0x444` object size | `rom:0x4A04` loads the pool word at `rom:0x4C64` | pool load, and word scan |
| `0x2B0` done list | `rom:0x4A52`, `rom:0x4AF2`, `rom:0x4CA2` | **image wide**, exactly three in all 8 MB |
| `0x40C` next field | `rom:0x4A5C` add chain; `rom:0x4B98` and `rom:0x4DA0` load pool words `rom:0x4C94` and `rom:0x4E9C` | span scan, and word scan |
| `0x154` active list | `rom:0x4A48` chain; `rom:0x4B02` and `rom:0x4C5A` build it as `add #0xff ; add #0x55` | span scan ONLY |

**The design named one site for each. Two of the four have three.**

### What this count is, and what it is not

- `0x2B0` is a firm count. The image wide pass decodes every halfword pair in the ROM.
- `0x40C` and `0x444` are firm for the pool shape, because the word scan is image wide too.
- **`0x154` is a floor, not a total.** Its sites are `add` pairs, and no image wide pass covers those.
  A reader that holds `0x154` in another register would appear in no shape used here.
- The word scan returns many `0x40C` words outside the menu. They are ordinary data. Only the two in
  the journal pool range are readers.

---

## 3. What the fix now costs

Make the lists hold 44. Keep `+0x154` where it is and move everything after it.

| Change | From | To | Shape kept |
|---|---|---|---|
| object size pool word `rom:0x4C64` | `0x444` | `0x454` | a word, so any value fits |
| done list header, 3 sites | `mov #0x2b ; lsl #4` | `mov #0x57 ; lsl #3` | same two instructions |
| next field pool words, 2 words | `0x40C` | `0x41C` | a word |
| next field add chain `rom:0x4A5E` | `add #0x5d` | `add #0x65` | same instruction |
| loop bound `rom:0x4AE2` | `cmp r6,#0x2b` | `cmp r6,#0x2c` | same instruction |

That is 8 edits, not the 6 the design estimated, and every one keeps its instruction length.

`0x154 + 4 + 44 * 8` is `0x2B8`. `0x2B8 + 4 + 44 * 8` is `0x41C`. `0x41C` plus the old tail
`0x444 - 0x40C` is `0x454`. The three numbers agree, which is the arithmetic the design asks a test
to pin.

---

## 4. Still open, and still the owner's call

Growing the menu gives room for a 44th quest. It does not decide what the 44th quest IS. The design
offers three options and all 43 vanilla quests are real, so none is free to take. That decision is
his.
