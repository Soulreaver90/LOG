# Menu layout census: the journal, and a correction to the scouter design

Measured 2026-11-13 on the base USA ROM. No ROM was written. Four shapes, three tools in
`scripts\one-time\2026-11-13-journal-menu\`:

| Shape | Tool | What it sees | What it cannot see |
|---|---|---|---|
| A, `mov ; lsl` in named functions | `census.py` | a constant built in two instructions | anything outside the spans I chose |
| B, `mov ; lsl` image wide | `imagewide.py` | every such pair in all 8 MB | a pool word, or a value from another register |
| C, aligned word scan | inline | every pool word holding the value | which code, if any, reads it |
| D, pc relative loads image wide | `poolrefs.py` | every `ldr rX,[pc,#imm]` and the word it reads | a value formed by arithmetic |

Shape A alone is what produced the scouter error below. Shape A is never enough.

---

## 1. The scouter correction

`docs\design\2026-11-09-scouter-menu-grow.md` lists FOUR readers of the `+0x680` live block.

**Shape B finds five.** The fifth is `rom:0x192DE`, `mov r1,#0xd ; lsl r1,r1,#7`, then `add r4,r0,r1`.

**Why the first census missed it.** That census read one listing file per named function. The file
for `sub_08019204` declares `size 0xd2`, so it ends at `rom:0x192D6`. The site is 8 bytes past that
end, inside a function starting at `rom:0x192D6` with `push {r4,lr}`, which the family list never
named. The tool was right. The family list was short.

`sub_080192D6` reads the block it builds (`ldr r0,[r4,#0x28]`, `ldr r0,[r4,#0x1c]`), so it is a real
reader, not a coincidence of the value.

**The count, tied to its shapes.** Five by shape B, which is image wide for this encoding. Shape C
finds four aligned words equal to `0x680` at `rom:0x289F0`, `0x28A2C`, `0x28ADC` and `0x28C30`, and
**shape D proves no pc relative load reads any of them**, so they are data and not a sixth site. A
site that forms `0x680` from another register appears in no shape here.

**The cost if the design ships as written.** Four sites move and the fifth keeps writing at `+0x680`,
which the grown list 2 now occupies. That is the silent late game overrun the design exists to stop.

---

## 2. The journal menu, measured

`sub_080049FC` allocates the object. Both lists hold exactly 43 quests (bible B2338, B2351).

### How each list header is really built

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
| `rom:0x4A5E` | `add r0,#0x5d` | **`+0x40C`, a tail field** |
| `rom:0x4AE2` | `cmp r6,#0x2b` | the loop bound, 43 |

`0x2B0 - 0x154` is `0x15C`, which is `4 + 43 * 8` exactly. `0x40C - 0x2B0` is `0x15C` again.

### The real site list, after shapes A to D

**Growing the done list pushes EVERY tail field up, not only the three the design names.** Reading
`sub_08004B62` found `+0x400` as well, built at `rom:0x4B86` as `mov r0,#0x1 ; lsl r0,r0,#10`, used
as `ldr r1,[r0,#0x30]`, so `+0x430`. The object is `0x444` bytes, so that field is inside it.

| Offset | Sites | Note |
|---|---|---|
| `0x444`, object size | pool word `rom:0x4C64`, read by `rom:0x4A04` | a word, so any value fits |
| `0x2B0`, done list | `rom:0x4A52`, `rom:0x4AF2`, `rom:0x4CA2` | three by shape B, image wide |
| `0x400`, a tail field | `rom:0x4B86` | **missed by the design entirely** |
| `0x40C`, a tail field | `rom:0x4A5E` add chain; pool word `rom:0x4C94`, read by `rom:0x4B98` | |
| `0x154`, active list | `rom:0x4A48` chain; `rom:0x4B02` and `rom:0x4C5A` as `add #0xff ; add #0x55` | stays where it is |
| bound | `rom:0x4AE2` | `cmp r6,#0x2b` |

### Two false positives I had to remove

- **`rom:0x4DA0` is NOT a journal field reader.** It is `ldr r0,=0x40c ; bl 0x801f08c`, which
  ALLOCATES a 0x40C byte object of its own. Five more sites image wide do the same. The allocator is
  the same one the journal calls at `rom:0x4A06` with `0x444`, which is what makes the shape look
  convincing until the next instruction is read.
- **Eleven more `0x40C` pool readers exist** in `rom:0x6904` to `rom:0x719A` and at `rom:0x22F36`.
  Each does `add rX,rY,0x40C` then loads through it, which is the field shape. **I did not trace what
  `rY` holds, so I do not know whether they index the journal object.** They are outside the
  `rom:0x49FC` to `rom:0x4FEE` family window. **This is the one gap left in this census.** Close it
  before any edit, by reading what reaches those functions.

---

## 3. What the fix costs, corrected

Keep `+0x154` where it is. Move everything above it by `0x10`.

| Change | From | To | Shape kept |
|---|---|---|---|
| object size, pool word `rom:0x4C64` | `0x444` | `0x454` | a word |
| done list header, 3 sites | `mov #0x2b ; lsl #4` | `mov #0x57 ; lsl #3` | two instructions |
| tail field `rom:0x4B86` | `mov #0x1 ; lsl #10` | `mov #0x41 ; lsl #4` | two instructions |
| tail field add chain `rom:0x4A5E` | `add #0x5d` | `add #0x65` | one instruction |
| tail field pool word `rom:0x4C94` | `0x40C` | `0x41C` | a word |
| loop bound `rom:0x4AE2` | `cmp r6,#0x2b` | `cmp r6,#0x2c` | one instruction |

Eight edits, every one the same length. The arithmetic a test must pin:
`0x154 + 4 + 44 * 8 = 0x2B8`, `0x2B8 + 4 + 44 * 8 = 0x41C`, and `0x41C + (0x444 - 0x40C) = 0x454`.

---

## 4. What this changes for the owner's choice

The design priced a grow at about six edits against "replace a vanilla quest" at one table entry.
The grow is eight edits, it touches a tail field the design never saw, and eleven possible readers
are still untraced. **The gap between the two options is wider than the design says.** The decision
is still his, and it should be made with this number, not the old one.
