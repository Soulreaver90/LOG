# The scouter menu layout sites, re-measured. HALF 1 IS STOPPED.

Measured 2026-11-13 on the base USA ROM. No ROM was written. No module was changed. No build list
was touched.

> [!WARNING]
> **The brief names NINE edit sites. There are FOURTEEN.** The brief's own gate says to stop and
> report when a shape finds a site it does not name. Four such sites exist, and every one of them is
> a real reader or writer of the block the grow has to move. Moving nine and leaving five is the
> silent overrun this work exists to prevent, so nothing was written.

---

## 1. Why the earlier count was short

`scripts\one-time\2026-11-13-journal-menu\imagewide.py` decodes ADJACENT halfword pairs only. The
compiler puts an unrelated instruction between the `mov` and the `lsl` whenever a register is free.
Every such site is invisible to that tool. A site built by an add chain is invisible to it as well.

`scripts\one-time\2026-11-13-menu-grow\gapscan.py` was written for this task. It allows a gap of up
to 10 halfwords, it drops a candidate only when something in between writes the register, it prints
every drop, and it watches value RANGES instead of single values.

---

## 2. Every site, by value

Each row was read in the listing. The proof column names the register that holds the object, and the
first field the code touches through the new pointer.

### `0x6B0`, the object size: ONE site

| Site | In | Shape | Proof |
|---|---|---|---|
| `rom:0x1920A` | `sub_08019204` | `mov r0,#0x6b ; lsl r0,r0,#4` | the argument to the allocator at `rom:0x1920E` |

New encoding: `mov r0,#0x6e ; lsl r0,r0,#4`, which is `0x6E0`.

### `0x280`, list 2's count word: FOUR sites, not two

| Site | In | Shape | Proof |
|---|---|---|---|
| `rom:0x1922A` and `rom:0x1922E` | `sub_08019204` | `mov r0,#0x5` ... `lsl r0,r0,#7`, **GAP 1** | `add r0,r4,r0`, then `str r2,[r0,#0x0]` zeroes the count |
| `rom:0x193AE` | `sub_08019320` | `mov r1,#0x5 ; lsl r1,r1,#7` | `add r6,r2,r1`, r2 is the object from the stack |
| `rom:0x1972A` | `sub_0801970A` | `add r2,#0x34` onto `0x24C`, **ADD CHAIN** | `add r6,r5,r2`, r5 is the object; `ldr r0,[r0,#0x4]` reads an entry |
| `rom:0x19848` | `sub_08019844` | `mov r0,#0x5 ; lsl r0,r0,#7` | `add r1,r5,r0`, r5 is the object |

New encoding: `mov rX,#0x52 ; lsl rX,rX,#3`, which is `0x290`. The add chain becomes `add r2,#0x44`,
because `0x24C + 0x44` is `0x290`.

> [!NOTE]
> `rom:0x1922E` is already named in the module's own header and in bible row B2268. The brief
> contradicts its own source row.

### `0x680`, the live block: EIGHT sites, not five

| Site | In | Gap | Proof: the object register, and the first field read |
|---|---|---|---|
| `rom:0x192A8` + `0x192AA` | `sub_08019204` | adjacent | `add r1,r4,r1`; writes `+0x4`, `+0x8`, `+0x1C`, `+0x20`, `+0x24` |
| `rom:0x192DE` + `0x192E0` | `sub_080192D6` | adjacent | `add r4,r0,r1`; reads `+0x28`, `+0x1C`, `+0xC`, `+0x10`, `+0x2C` |
| `rom:0x19324` + `0x19330` | `sub_08019320` | **GAP 5** | `add r4,r1,r0`, r1 is the pushed r0; reads `+0x24` |
| `rom:0x1966E` + `0x19670` | `sub_0801963C` | adjacent | `add r7,r4,r1`; reads `+0x24`, writes `+0x28`, `+0x2C` |
| `rom:0x19726` + `0x19728` | `sub_0801970A` | adjacent | `add r4,r5,r1`; reads and writes `+0x20` |
| `rom:0x197BC` + `0x197C0` | `sub_080197B4` | **GAP 1** | `add r4,r5,r2`; reads and writes `+0x28`, reads `+0x2C` |
| `rom:0x19866` + `0x19868` | `sub_08019844` | adjacent | `add r4,r5,r0`; reads `+0x20`, `+0x24` |
| `rom:0x199A0` + `0x199A4` | `sub_08019934` | **GAP 1** | `add r7,r2,r1`, r2 is the pushed r0 at `sp+0x10`; writes `+0xC`, `+0x10`, `+0x14`, `+0x18` |

New encoding: `mov rX,#0xd6 ; lsl rX,rX,#3`, which is `0x6B0`.

### The list bound: ONE site

`rom:0x19260` `cmp r2,#0x80` becomes `cmp r2,#0x83`. The immediate is the FIRST byte of the pair.

---

## 3. A warning the builder must carry

**A gapped site needs TWO separate halfword writes**, one at the `mov` and one at the `lsl`. A four
byte write at the `mov` address destroys the instruction that sits between them. Three sites are
gapped, and `rom:0x19324` has five instructions between its two halves.

---

## 4. The block length, and why the new numbers fit

The highest field any of the eight sites touches is `+0x2C`, a word, so the block is at least `0x30`
bytes. The vanilla object proves it is exactly `0x30`, because `0x680 + 0x30` is `0x6B0`, the whole
object size.

| Claim | Arithmetic | Slack |
|---|---|---|
| list 1 holds 131 entries | `0x80 + 4 x 131` = `0x28C`, at or below the new header `0x290` | 4 bytes |
| list 2 holds 131 entries | `0x294 + 8 x 131` = `0x6AC`, at or below the new block `0x6B0` | 4 bytes |
| the block still fits | `0x6B0 + 0x30` = `0x6E0`, at or below the new size `0x6E0` | exact |

> [!WARNING]
> The brief's test text says `0x284 + 8 * 131`. That is the OLD list 2 base. The test must derive
> the base from the NEW header, `0x290 + 4` = `0x294`. Derive every number, never type it twice.

---

## 5. What each shape returned, and what each one cannot see

| Shape | Tool | `0x6B0` | `0x280` | `0x680` |
|---|---|---|---|---|
| adjacent `mov ; lsl`, image wide | `imagewide.py` | 1 | 2 in the family | 5 |
| gapped `mov ; lsl`, image wide | `gapscan.py` | 1 | 3 in the family | 8 |
| pc relative loads, image wide | `poolrefs.py` | 0 | 0 in the family | 0 |
| aligned word scan | inline | 0 words | 12 words | 8 words |
| add chains, by eye | the listings | 0 | **1** | 0 |

**Reconciled total: 14 edit sites.** The counts agree once the gap is allowed, and the add chain at
`rom:0x1972A` is found by no image wide shape at all.

### The whole code region was then swept, and nothing outside the family touches this object

`gapscan.py` was run over `rom:0x0` to `rom:0x400000` watching the RANGES `[0x280,0x290]` and
`[0x680,0x6B0]`, so a folded block-plus-field offset could not hide.

**The code boundary is measured, not guessed.** `disasm\data\coverage.txt` gives the code region as
`rom:0x0` to `rom:0x28724`, and the highest function start in `functions.csv` is `rom:0x286A4`.
There is one other code region, the IWRAM block at `rom:0x7FD6BC` of `0xE7C` bytes, which the game
copies to `0x3000000`. **That block was swept too and holds ZERO sites.** Every hit above
`rom:0x28724` and below `rom:0x7FD6BC` is therefore data that decodes as a pair.

Every hit inside the code region was identified:

| Hit | In | Verdict |
|---|---|---|
| `rom:0x655C`, `0x6590`, `0x65C4`, `0x66DE`, `0x6852`, `0x6870`, `0x6D06`, all `0x690` | `sub_08006534` and `sub_08006664` | a shared 10 byte stride table at another object's `+0x690`. **61 `bl` callers of `sub_08006664` and 3 of `sub_08006534` were decoded image wide: NOT ONE is in `rom:0x19000` to `rom:0x19B30`** |
| `rom:0x16948`, `0x280` | `sub_0801684C` | a range argument to `rand_n`, then `sub #0xff ; sub #0x41` to centre it |
| `rom:0x8230` `0x288`; `rom:0x17134`, `rom:0x1742A`, `rom:0x1D2C8` `0x290` | `sub_0800811E`, `sub_0801710E`, `sub_0801D2BC` | other object types, each with its own vtable, and none builds a vanilla scouter value |

**The scouter DOES call the shared list helper, and it passes the WORLD, not its own object.**
Every `bl` to `List_RemoveValue` at `0x080068CA` was decoded: 57 callers, two of them in the
scouter at `rom:0x194D4` and `rom:0x19548`. Both load r0 from `[0x086FD864 + 0xC]`, a global world
object, and pass the BLOCK's `+0x4` and `+0x8` child objects in r1. The menu object is never the
argument, so that helper's own `+0x40C` never reaches it.

### The family is now closed BY CONSTRUCTION, not by one more grep

A Thumb word load or store with an immediate offset reaches `+0x7C` at most. So every access at
`+0x80` or above must take one of exactly three paths, and all three were swept over `rom:0x19000`
to `rom:0x19B30`:

| Path | Count | Result |
|---|---|---|
| an `add` that derives a pointer | every `add` in the range | read by eye; it is where all 14 sites live |
| a register offset load or store, `[rB,rO]` | 7 | all clear, see below |
| a high register add, the `0x44xx` forms | 25 | **all 25 are `add rX,sp` or `add sp,rX`**, stack frame arithmetic in `sub_08019320` |

The 7 register offset sites:

| Site | What it really is |
|---|---|
| `rom:0x196F2`, `rom:0x19900` | `ldrb rX,[rObj,rY]` with rY holding `0x7A`, a byte field BELOW `0x7C`, so it does not move |
| `rom:0x19044` | the base carries vtable `0x08025770`, a DIFFERENT object type, not the menu's `0x08024688` |
| `rom:0x1948E` | `ldr r1,[r1,r0]` with r1 the `string_table` and r0 `0xAC`, a table index |
| `rom:0x19092` | `ldrb r0,[r1,r0]` with r1 the ROM table `0x086FD4F8` |
| `rom:0x19AC2` | `strb r6,[r0,r1]` with r1 `0x04000000`, an I/O register |
| `rom:0x191EC` | a literal pool word, `0x0802517C`, that decodes as a store |

**What no shape here covers.** A site that forms an offset from another register whose value comes
from somewhere none of these paths reaches. Every path a Thumb instruction has to reach `+0x80` or
above was swept, so the 14 sites are complete for this family by this argument. A site in code that
is not in `rom:0x19000` to `rom:0x19B30` and does not build a constant would still not appear.

### Two census claims that needed a correction of their own

- Of the 12 aligned words equal to `0x280`, exactly ONE has a pc relative reader: `rom:0x618AB8`,
  read by `rom:0x618A34`. Both sit at 6.3 MB, far past the code region, so the pair is data that
  decodes as a load. None of the other 11, and none of the 8 words equal to `0x680`, is read.
- `gapscan.py` had two faults of its own, found in review and fixed before the numbers above were
  taken. Its drop branch tested shifts 1 to 3 only, which would have hidden a dropped
  `mov rX,#0xd` before an `lsl #7`, the exact shape of the block sites. It also counted `tst`,
  `cmp` and `cmn` as writes, which produced false drops. The fixed tool returns the same 12 sites.

### Two census claims that did not hold

- The 2026-11-13 census says shape C finds FOUR aligned words equal to `0x680`. It finds **eight**:
  `rom:0x289F0`, `0x28A2C`, `0x28ADC`, `0x28C30`, and a second copy of the same block at
  `rom:0x7FC08C`, `0x7FC0C8`, `0x7FC178`, `0x7FC2CC`. The four deltas are identical in both copies.
  No pc relative load reads any of the eight, so all eight are data. The conclusion stands.
- `rom:0x16948` builds `0x280` with `mov r0,#0x5 ; lsl r0,r0,#7`, and it is NOT a scouter site. It
  is in `sub_0801684C`, and the value is a range argument to `rand_n`.

---

## 6. The exact halfwords, ready to apply

Computed from the base ROM. Every register check passed: in all 12 pairs the `lsl` source and
destination are the `mov` destination, so the pair really is one constant.

| Value | `mov` site | now | new | `lsl` site | now | new |
|---|---|---|---|---|---|---|
| `0x6B0` to `0x6E0` | `rom:0x1920A` | `206b` | `206e` | `rom:0x1920C` | `0100` | unchanged |
| `0x280` to `0x290` | `rom:0x1922A` | `2005` | `2052` | `rom:0x1922E` | `01c0` | `00c0` |
| `0x280` to `0x290` | `rom:0x193AE` | `2105` | `2152` | `rom:0x193B0` | `01c9` | `00c9` |
| `0x280` to `0x290` | `rom:0x19848` | `2005` | `2052` | `rom:0x1984A` | `01c0` | `00c0` |
| `0x680` to `0x6B0` | `rom:0x192A8` | `210d` | `21d6` | `rom:0x192AA` | `01c9` | `00c9` |
| `0x680` to `0x6B0` | `rom:0x192DE` | `210d` | `21d6` | `rom:0x192E0` | `01c9` | `00c9` |
| `0x680` to `0x6B0` | `rom:0x19324` | `200d` | `20d6` | `rom:0x19330` | `01c0` | `00c0` |
| `0x680` to `0x6B0` | `rom:0x1966E` | `210d` | `21d6` | `rom:0x19670` | `01c9` | `00c9` |
| `0x680` to `0x6B0` | `rom:0x19726` | `210d` | `21d6` | `rom:0x19728` | `01c9` | `00c9` |
| `0x680` to `0x6B0` | `rom:0x197BC` | `220d` | `22d6` | `rom:0x197C0` | `01d2` | `00d2` |
| `0x680` to `0x6B0` | `rom:0x19866` | `200d` | `20d6` | `rom:0x19868` | `01c0` | `00c0` |
| `0x680` to `0x6B0` | `rom:0x199A0` | `210d` | `21d6` | `rom:0x199A4` | `01c9` | `00c9` |

The two single byte edits, stated as BYTES so no halfword order can be misread:

| Site | Instruction | Byte now | Byte new | Why |
|---|---|---|---|---|
| `rom:0x1972A` | `add r2,#imm` | `0x34` | `0x44` | `0x24C + 0x44` is `0x290` |
| `rom:0x19260` | `cmp r2,#imm` | `0x80` | `0x83` | the list bound, 128 to 131 |

Every value above is derived, never typed twice: a module must compute `0x6E0`, `0x290` and `0x6B0`
from the entry count and the entry sizes, and build each halfword from the register the base ROM
already uses at that site.

---

## 7. What the controller has to decide

The edit list above is complete to the shapes named, and every site is proved in the listing. The
work is the same KIND the brief approved, and it is 14 sites instead of 9. Half 1 needs one yes
before a byte is written.
