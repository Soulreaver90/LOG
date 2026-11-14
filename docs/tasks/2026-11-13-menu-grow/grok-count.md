# Verified: an independent site count (Grok 4.7 high)

Grok was given the disassembly ALONE, from `rom:0x19204` to `rom:0x19CF4`, the object layout, and
the grow. It was not told the answer, and it was told to read no other file. The point was an
independent count, not agreement.

**It returned 14: one size, four `0x280`, eight `0x680`, one bound. That is the agent's count and
mine, reached three different ways.**

It found the folded add chain at `rom:0x1972A` on its own, by tracing registers to their use. That
is the site no image wide shape can see, so it is the one worth an independent pass.

## What it adds that neither the agent nor I had written

- **`lsl #7` cannot build `0x290` or `0x6B0`**, because neither is a multiple of 128. So at every
  plain `0x280` and `0x680` site BOTH halfwords change. Only the size site keeps its shift, because
  `0x6E0` is still `0x6E << 4`. This is exactly what the agent's halfword table does, now confirmed
  by a second reading of the encodings.
- **`rom:0x1972A`'s `mov`/`lsl` pair must STAY.** The `0x24C` it builds also feeds
  `rom:0x19724` `add r7,r2,r1`, where r1 is the ROM address `0x080E15B0`. Only the `add r2,#0x34`
  byte moves. The agent's table says the same.
- **`rom:0x19260` is the ONLY hardcoded 128.** The second loop at `rom:0x192A4` compares against the
  count stored at `+0x7C`, so it follows automatically.
- **Why `+0x7C` is the boundary.** A Thumb word displacement is a 5 bit word count, so `0x7C` is the
  last reachable offset. List 1's count sits exactly at `+0x7C`, and the first entry at `+0x80` is
  already out of reach. That is why this code keeps a pointer there at all.

## One claim I do NOT accept

Grok says a 4 byte write covers an adjacent pair "only when the first address is a multiple of 4",
and lists five adjacent sites as needing two writes for that reason: `rom:0x192DE`, `rom:0x193AE`,
`rom:0x1966E`, `rom:0x19726`, `rom:0x19866`, all 2 mod 4.

**That is true of an aligned 32 bit store at runtime. It is not true of writing bytes into a ROM
image.** A 4 byte write at a 2 mod 4 file offset lands exactly where it is put and covers both
halves correctly. The reasoning is sound, the conclusion does not transfer to file patching.

It does not matter either way, because of the rule below.

## The rule for the builder

**Write every site as individual halfwords.** Then neither the gaps nor the alignment can bite, and
no site needs a special case. Four sites are genuinely gapped (`rom:0x1922A`, `rom:0x19324`,
`rom:0x197BC`, `rom:0x199A0`), and at `rom:0x19324` five instructions sit between the halves, one of
which builds the `0x1080` stack frame. A 4 byte write there destroys live code.

Raw output: `scratch\cursor\2026-11-13-scouter-sites\raw.txt`. Prompt and listing beside it.
