# Catalogue: what is useful to LOG in dragonbyte-z

**Study only.** No code from `C:\Users\josephgonzalez\Documents\GitHub\dragonbyte-z` was run, imported or
copied. Every number below came from reading their files, or from our own scripts in
`scripts\one-time\2026-11-06-dragonbyte-review\` run with `py -3.14 -I` against our base ROM.

**Credit.** The author is **Cale** (`siruiusamory@gmail.com`, GitHub `siruiusamory-cmyk`). The repository is
MPL-2.0. Use that name in anything we build from it. Their own `config/roms.yaml` says "Owner Cale approved
this declaration on 2026-10-31", and `git log` on `legacyofgoku2-disasm` shows 50 commits by
`Cale <siruiusamory@gmail.com>`. The single squashed commit in dragonbyte-z is authored
`Postboy <siruiusamory@gmail.com>`, the same address.

| Item | Value |
|---|---|
| Target | `GitHub\dragonbyte-z`, HEAD `5e8c3b9`, cloned 2026-11-06 |
| Size | 286 files under `docs\`, 110 Lua scripts, 387 test files |
| Licence | MPL-2.0 (`LICENSE`, `pyproject.toml:11`), with per-upstream exceptions in `THIRD-PARTY-NOTICES.md` |
| Our side | `docs\RE-BIBLE.md` (2,068 lines, 17 sections), `docs\tool-index.md` |

---

## 0. Five corrections to the brief, before the catalogue

The brief asked me to use several search shapes. Four of its own statements did not survive that.

### 0.1 Their Legacy of Goku II ROM is byte identical to ours. CONFIRMED

`config/roms.yaml:548` declares `sha1: 18e0715dec419f3501c301511530d2edcd590f8b` for profile
`legacy_of_goku_ii_usa_rev0_204142e1`. `docs\tasks\global.md` pins our base ROM at the same SHA-1.

This is the most load-bearing fact in the review and the brief does not state it. Every LoG2 number in their
repository is a measurement of **our exact file**, not of a cousin. DIRECT applicability is therefore not a
judgement call for those items. It is an identity.

### 0.2 `LOGX_*` means LOGExtractor, and every LOGX document is measured on Buu's Fury. CONFIRMED

The brief says `LOGX_*` means "Legacy of Goku GENERALLY". Four independent shapes disagree.

| Shape | Result |
|---|---|
| Grep `LOGExtractor` in `LOGX_SYNTHESIS.md` | 10 hits. Line 1: "canonical LOGExtractor knowledge". Line 34 names `mainant/LOGExtractor` |
| Grep the canonical SHA in all 24 `LOGX_*.md` | 23 carry the Buu's Fury SHA `940AD5F0`. The 24th carries none |
| Grep `ALFE`, `LOGII`, `Legacy of Goku II` in all 24 | the search returned nothing |
| Our own `docs\RE-BIBLE.md` line 1272 | already names `Fralacticus/LOGExtractor` and `mainant/LOGExtractor` as Buu's Fury tools |

So `LOGX` is a ticket prefix for "answers LOGExtractor got first", measured on Buu's Fury.

**The practical ranking does not change.** The engine is shared enough that their formats should carry. But the
label is SHARED ENGINE, not DIRECT, and every address in a LOGX document must be re-derived for our ROM.

### 0.3 The brief's list of six was right. My first grep was wrong, and there is a seventh

I first ran `grep -l "6e6c370c"` and reported that `CELL_PALETTE_ROUTE_C.md` was missing from the six. That
was a case-sensitive grep, and that file writes the digest in upper case. `grep -il` finds it.

**Retracted.** The brief's six are correct. The complete case-insensitive list under `docs/` is nine paths:
the brief's six, plus `LOGII_16MIB_RUNTIME.md`, which the brief lists separately but not in this group, plus
`docs/rom-profiles.md` and `docs/upstream-audit.md` outside `docs/research/`.

I am leaving my error in this document on purpose. It is the same failure the brief warns about, committed
inside the review that was warning about it.

### 0.4 The three negative-zero example sites are raw-sweep artifacts. CONFIRMED

This one matters, because it changes what guard we should write. See section 3.

Reading a varint at `rom:0x3B0034`, `rom:0x3B0017` and `rom:0x3B0106` does reproduce the brief's result
exactly. But a varint can be read at **any** byte, so the finding only means something if a real decode
reaches those offsets as operands. Three shapes say none of them does.

| Measurement | Result |
|---|---|
| The three named sites, decoded and re-encoded | all three differ, exactly as the brief says |
| Are the three sites inside any of the 112 op-bearing records this sweep decoded | no, none of them |
| Aligned words anywhere in the 8 MB ROM naming any of the three | **0** |
| The byte at `rom:0x3B0034` | `0x01`, which is the op 1 **opcode** byte. Reading it as an operand reads the opcode itself |
| The bytes at `rom:0x3B0017` and `rom:0x3B0106` | `0x80`, a varint continuation byte |
| Real varint operands reached by walking 7 scene tables | **962** |
| Of those 962, how many our `zigzag()` cannot reproduce byte for byte | **0** |
| Varint operands reached structurally in their whole static43 corpus | 1, and it is canonical |

Scripts: `scene_varint_sweep.py` and `verify_direct.py` in
`scripts\one-time\2026-11-06-dragonbyte-review\`.

**Coverage of that sweep, stated properly.** The 7 tables hold 290 record pointers: 112 type 0 (code), 95
type 1 (text) and 83 type 2 (stream). Only a type 0 record holds script ops. The sweep decoded **112 of 112**
type 0 records. The 177 "failures" are text and stream records, which carry no ops at all, so the sweep is
complete for those 7 tables rather than a 39 percent sample.

**Label: LIKELY, not CONFIRMED.** "Raw-sweep artifact" is the best explanation of all three shapes, but my
7 tables sit at `rom:0x3D37BC` to `rom:0x3E6078` and could never have reached `rom:0x3B00xx` by walking. The
zero-inbound-words result is the strongest shape, and it is a static one.

The trap their `SCRIPT_VM.md:60-61` describes is **real as a rule** and we should respect it. Its measured
rate in real LoG II data, in the corpus I could reach, is zero.

> Honest limit: 7 tables and 113 records is a sample, not the game. A non-canonical operand elsewhere would not
> appear here. I did not sweep every scene table.

### 0.5 We already depend on this author's work

`git remote -v` in `GitHub\legacyofgoku2-disasm` returns
`https://github.com/siruiusamory-cmyk/legacyofgoku2-disasm.git`. The dragonbyte-z HEAD commit is a merge from
`siruiusamory-cmyk/repository-cleanup-001`. The disassembly our CLAUDE.md calls byte exact, and this
repository, come from the same person. This is already a collaboration.

---

## 1. Ranked, actionable items

Ranked by value to LOG, highest first. **Applicability** is DIRECT (their evidence is our exact ROM), SHARED
ENGINE (re-derive the addresses, carry the format) or BUU ONLY (no path to LoG II found).

| # | Item | Applicability | Label | Effort | Blocked on |
|---|---|---|---|---|---|
| 1 | Scripted save-state production on stock mGBA 0.10.5 | SHARED ENGINE (emulator, not game) | C for the API, **L** for our ROM | Medium | One proving run |
| 2 | Their LoG II ROM profile: pool bounds, counts, free region | DIRECT | **C**, six of their claims re-measured here | Low | Nothing |
| 3 | The static43 corpus as a conformance oracle for our script decoder | DIRECT | **C**, measured | Low (already run) | Nothing |
| 4 | The `+0x40`/`+0x44` door list, and the search shape that finds it | SHARED ENGINE | C for Buu, **L** for ours | Medium | Re-derive for LoG II |
| 5 | Per-sprite colour depth and palette bank: a route to new colours | SHARED ENGINE | **L**, with one precondition already C on our ROM | Medium | Owner ruling, it touches a standing constraint |
| 6 | `LOGII_TEXT_FORMAT.md` plus its 22-test suite on the UI string table | DIRECT | **C**, re-measured here | Low | Nothing |
| 7 | `LOGII_16MIB_RUNTIME.md`: our expansion decision, independently proven | DIRECT | **C** (their runtime measurement) | None (read it) | Nothing |
| 8 | The Webfoot literal-base rule, proven on the engine | SHARED ENGINE | **C**, and we already comply | None | Nothing |
| 9 | The liveness-channel rule for any silent probe | Method | **C** (their two invalidated tickets) | Low | Nothing |
| 10 | `mstan/DragonBallZLegacyofGokuIIRecomp`, a LoG II recompilation lead | DIRECT lead | **L**, cited not opened | Low to check | Nothing |
| 11 | Their Ghidra scripts and free-space audit tooling | SHARED ENGINE | C | Medium | Low payoff, we have `disasm\` |
| 12 | The Buu's Fury SDK, editors and randomizers | BUU ONLY | **L** on two shapes | High | Not worth it |

> The detail sections below keep their original numbering, 1 to 11, and item 5 in this table is the new one
> described immediately after item 4.

---

### 1. Scripted save-state production on stock mGBA 0.10.5

**What it is.** `tools/runtime/rom006_bootstrap.lua` is 57 lines. It asserts the game code and the ROM size,
resets the core, registers a `frame` callback, and pulses A on named frames (1210, 1810, 2410). At frame 2420
it takes a screenshot, calls `emu:saveStateFile(output_state)`, removes its own callback and stops.

**What LOG gains.** This is the exact answer to our biggest workflow cost. Today the owner hand-makes every
save state so I can measure. A script of this shape produces a state at a named frame, deterministically,
with nobody holding the pad.

**Why it carries to our ROM.** The API is the emulator's, not the game's. Only the two asserts and the frame
numbers are Buu's Fury. Nothing about `callbacks:add`, `emu:addKey` or `emu:saveStateFile` depends on which
GBA game is loaded.

**Files worth reading, in order:**

| File | What it gives |
|---|---|
| `docs/skills/mgba-runtime.md` | The whole rulebook. Every failure in it has actually happened |
| `tools/runtime/load_mgba_lua.ps1` | The 0.10.5 launcher, pinned by `VersionInfo.FileVersion` |
| `tools/runtime/inject_mgba_lua.ps1` | Loads the Lua into the Scripting window by UI Automation |
| `tools/runtime/rom006_bootstrap.lua` | The pattern itself |
| `tools/runtime/o1_clean_gameplay_route.lua` | The only Lua they ran on **our** ROM |

**Effort.** Medium. We write our own Lua. The injector is the work, because 0.10.5 has no startup switch for
Lua. Section 6 assesses that honestly.

---

### 2. Their Legacy of Goku II ROM profile

**What it is.** `config/roms.yaml:540-731`, 192 lines, every claim carrying its own evidence paragraph.
Because of correction 0.1, this is a measurement of our file.

**What is new to us.** I checked each address against `docs\RE-BIBLE.md` with two grep shapes, the bare file
offset and the full GBA address.

| Their claim | What our bible holds | Verdict |
|---|---|---|
| `scripts` table `0x086d68dc`, 43 entries, stride 16, slots `+4` and `+8`, caller `0x08004A86..0x08004AE4` | line 706: the same table, the same count, the same caller range, and `+4`/`+8` named "done script, active script" | **Two independent derivations agree exactly.** Strong mutual validation |
| Script **pool** `0x086d66c0`, 539 bytes | the search returned nothing for `6D66C0` | **New.** It gives the corpus its bounds |
| `text_strings` pointer table `0x080e2840`, 260 entries | line 1778 has the table and the count | agree |
| Text **pool** `0x080e2c50`, 5,184 bytes, 246 distinct strings, 9 targets aliased by 14 extra slots | the search returned nothing for `0E2C50` | **New.** The aliasing is why the table cannot be relocated |
| `enemy_stats` `0x086d56ac`, 109 records of 0x18, HP u32 at `+0x04`, constructor `0x0800E280` | line 1797: the same table, stride and constructor | agree, and we are far ahead on the fields. See section 2 |
| **Count is 109**, bounded by the maximum index in the 128-entry scouter directory | the search returned nothing for a count | **New** |

**I measured their four load-bearing Legacy of Goku II claims against our ROM myself**, rather than relaying
them. Script: `scripts\one-time\2026-11-06-dragonbyte-review\verify_direct.py`.

| Their claim | My measurement on our base ROM | Verdict |
|---|---|---|
| 260 pointers all land inside the pool | 260 of 260 | CONFIRMED |
| 246 distinct targets | 246 | CONFIRMED |
| The pool is tiled exhaustively by NUL-terminated strings | 246 strings, the last ending exactly at pool end | CONFIRMED |
| Every pointer lands on a string start | yes | CONFIRMED |
| The scouter directory's maximum `+0x10` index is 108 | 108 | CONFIRMED, so the enemy count is 109 |
| The enemy table has exactly three references image-wide | `words_naming()` returns `0xE79C`, `0x17A38`, `0x1912C` | CONFIRMED, the same three |

Every one holds. That is six independent agreements, so I would treat their other Legacy of Goku II
measurements as reliable until one fails.
| Free region at file `0x007fea01`, **384 bytes**, status CONFIRMED | `global.md` says "the base 8 MB has no usable free space (Task 1 finding)" | **A direct tension, worth reading** |

> [!WARNING]
> The 384-byte free region is the one item here I would not act on. They say why themselves: the number "is
> dependent on a policy constant rather than on a property of the ROM", and it falls to ZERO at a 1,216-byte
> margin instead of their 1,024. It is a licence to allocate inside the canonical 8 MiB. We do not need it,
> because we expanded to 16 MB. Record it. Do not spend it.

**One more useful negative.** Their notes decline to declare `map_entries` for LoG II: the 0x38-stride table
at `0x08409368` is real, but its records are "a variant type rather than the Buu MapEntry layout". Our
`map_view.py` hardcodes that same table with 327 entries. So they confirm our table and our stride, and they
confirm that the Buu codec does not read it.

---

### 3. The static43 corpus as a conformance oracle

**What it is.** `docs/research/SCRIPT_VM.md` documents the Legacy of Goku II bytecode VM from the dispatch
table at `0x083B5C00`, with 804 passing tests and a byte-exact round trip of the whole static43 family.

`0x083B5C00` is **our** base op table too. `scene_lib.py:145` says "Every row is read from its handler in the
base op table rom:0x3B5C00". We document the same table from the same end, not from the other end.

**What LOG gains.** A second, independently derived decoder for the same bytes. I ran ours against their
corpus. Script: `scripts\one-time\2026-11-06-dragonbyte-review\varint_roundtrip.py`.

| Measurement | Result |
|---|---|
| Script runs reached from their table (43 entries, slots `+4` and `+8`) | 86 |
| Runs our `op_end()` walks cleanly to the end opcode `0x11` | **86 of 86**, zero failures |
| Runs whose start lies inside their declared 539-byte pool | **86 of 86** |
| Runs where `relocate(rom, rec, len, {})` returns the original bytes | **86 of 86** |

CONFIRMED: our op-length table and theirs agree over their whole supported corpus. That is free validation of
`scene_lib._op_end` against work we did not do.

Their opcode numbering is hexadecimal and ours is decimal. Read across carefully: their `0x11` is our 17
(end), their `0x12`, `0x13` and `0x1C` are our 18, 19 and 28 (the jumps), and their `0x15..0x1A` are our 21
to 26.

---

### 4. The `+0x40`/`+0x44` door list, and the search shape that finds it

**What it is.** `docs/research/LOGX_CONNECTOR_PROVENANCE.md`. On a Buu's Fury map root, `+0x40` is a 4-byte
count and `+0x44` is a pointer to that many 4-byte elements. Each element names a record whose first word is
a constructor function pointer that the registry calls.

Their corpus figures: 452 roots, 104 with both fields zero, 348 with both non-null, and `+0x40 == 0` holds if
and only if `+0x44 == 0`. No `+0x44` value is shared between two roots. The array enumerates 735 references.

**Why this ranks high.** Our own `docs\tool-index.md` names this exact gap twice, for `map_view.py` and for
`scene_probe.py`: "it never reads the layout's own door list at `+0x40`/`+0x44`, so a map's real exits do not
appear". The offsets match. A shared layout is LIKELY.

**The part worth more than the format.** Their section 3.5 records why a search missed the reader:

```text
08009672  adds  r1, #0x40        ; r1 = selector-1 root + 0x40
08009676  ldm   r1, {r1, r2}     ; r1 = root[+0x40] (count), r2 = root[+0x44] (array)
```

A constant-immediate scan for `ldr ..., #0x40` finds three unrelated sites and misses the real consumer,
because the consumer reads **eight bytes atomically with `ldm`**. Their own words: "an empty scan result is
not evidence of absence."

That is our verification rule, proven on this engine. When we hunt the Legacy of Goku II door-list reader,
grepping the disassembly for `#0x40` will return nothing useful. Search for an `ldm` on a map root instead.

**Effort.** Medium. Their addresses are Buu's. The structure and the instruction shape are the gift.

---

### 4a. Per-sprite colour depth and palette bank (new item 5 in the table)

**What it is.** `docs/research/CELL_PALETTE_ROUTE_C.md`, a design note for giving one actor its own colours.
Its two mechanism claims:

- **Colour depth is per sprite**, not global. OAM `attr0` bit 13 selects 16-colour or 256-colour for that
  sprite alone, and the engine copies the piece attribute word verbatim into the sprite's first OAM word.
- **The palette bank is `attr2` bits 12 to 15**, and their OAM builder clears only the priority bits 10-11
  and the tile-index bits 0-9, so bits 12-15 survive whatever the record carries.

**Applicability, carefully.** The document names BOTH SHAs, which is why it looked DIRECT. It is not. The
quoted addresses `0x0800F254` and `0x0800F2A0..0x0800F2BE` are **Buu's Fury**. Our own OAM builder is
`@0x08007784` (bible line 119) and our priority insert is `@0x080077A4..0x080077B6` (line 218). The Legacy
of Goku II SHA appears because they read colour values from our palette at `0x081DA6C8`. **SHARED ENGINE.**

**Why it still matters, and a lot.** The mechanism's precondition is already CONFIRMED on our ROM by our own
work. Bible line 119: "OAM build `@0x08007784`: record +4 word (attr0, attr1) goes into OAM". Line 1887 says
the same. So on our ROM too, an actor's own frame record decides its attr0, which is where bit 13 lives.

**The tension to put to the owner.** `global.md` says "The shared OBJ palette at ROM `0x1DA6C8` is not
changed. New art uses existing palette indices only." Our bible line 339 explains why: every OBJ in our game
is 8bpp, so banks isolate nothing. This route is the other door. If a sprite can be switched to 4bpp, it gets
its own 16-colour bank and stops competing for shared indices.

That is a real option for the gi colours, the blue Super Saiyan 2 lightning and Super Perfect Cell. It is
also a change to a standing constraint, so it needs an owner ruling before anyone spends a day on it.

**Blocked on:** an owner ruling, then re-deriving their two sites in our ROM around `@0x08007784`.

---

### 5. `LOGII_TEXT_FORMAT.md` and its test suite

**What it is.** DIRECT evidence on the UI string table we already know as `@0x080E2840`, plus
`tests/integration/test_logii_text_rom.py`, which holds 22 tests.

What that suite proves, on our bytes: the pointer table abuts the pool with no bytes between it; every
pointer targets a string start inside the pool; the table aliases, so its pointers are neither unique nor
ascending; the pool is exhaustively tiled; the pool holds only printable ASCII and two newlines; the whole
pool round trips byte for byte; an unedited plan is a no-op over every string; and the format specifiers and
the embedded newline survive a round trip.

**What LOG gains.** Our bible line 1778 gives the table and the count. It does not give the pool bounds, the
aliasing, or an exhaustive tiling proof. Those are the facts that decide whether we can ever edit this text
safely. The aliasing is why they mark the table `relocatable: false`.

Their note also warns that this table is menu, item, quest and map-name text. It is **not** the dialogue
system, which they call a script-interleaved, partly JCALG1-compressed stream that they do not declare.

---

### 6. `LOGII_16MIB_RUNTIME.md`

**What it is.** DIRECT runtime evidence that a 16 MiB Legacy of Goku II image boots to interactive gameplay,
and that the guest CPU performs a data read above the 8 MiB boundary.

**What LOG gains.** Independent corroboration of the expansion we approved on 2026-10-16. We proved ours by
passing the anti-piracy point. They proved theirs with a GDB read watchpoint on a relocated 12-byte object,
over 5,520 measured frames. Two unrelated methods, one conclusion.

**The method is worth as much as the result.** Their control table shows a `Z3` read watchpoint does not fire
on an instruction fetch, only on a data load. Without that control, a silent channel and a real negative
would have been indistinguishable. They also state their limits plainly: one emulator, one address, no mapper
claim, and a route tuned to one area.

---

### 7. The Webfoot literal-base rule

**What it is.** `docs/research/WEBFOOT_LZ_LITERAL_BASE.md`. The packed-container grammar clears the literal
base when the stream returns to 8-bit literals. Their shipping decoders kept a stale base, which shifts
palette indices while keeping tile geometry. The symptom is "correctly shaped tiles in the wrong colours".

**We are already correct.** `scripts\permanent\rom\webfoot_decompress.py:142-144`:

```python
lit_bits, lit_base = 7 + r.bit(), 0
if lit_bits == 7:
    lit_base = r.bits(8)
```

The base is set to 0 on every mode change, and a new base is read only for 7-bit mode. That is their corrected
rule. CONFIRMED: our decoder does not carry the defect.

Our encoder is unaffected as well. `webfoot_lz_pack.py` writes every literal as `bit(1)` plus 8 raw bits, and
never emits 7-bit literal mode. Its header says the stream sets 8-bit mode before the first literal.

**So why list it.** Because the rule is now proven against the retail engine's own character memory, not
inferred from an external tool. That upgrades our codec row from "it works" to "it matches the engine". File
the corroboration. Change no code.

---

### 8. The liveness-channel rule

`docs/skills/mgba-runtime.md` section 8, "Prove the instrument before believing a negative". Give every probe
a second breakpoint on something known to fire in the same run.

| Target | Liveness | Conclusion |
|---|---|---|
| silent | silent | **nothing**. The instrument is unproven |
| silent | fires | a real negative. That path was not taken |
| fires | any | execution observed |

With the trap that a construction-time breakpoint is silent by construction in a run that loads a savestate,
so it is not a liveness channel there. Two of their tickets were invalidated for exactly this.

This is cheap to adopt, and it is our own "say the search returned nothing" rule in runtime form.

---

### 9. `mstan/DragonBallZLegacyofGokuIIRecomp`

Cited in `config/roms.yaml` under `sources`, pinned at `add98b5d76fb2b822be870f29fa27b22c9a95631`, as
independent corroboration of the Legacy of Goku II hash. It is a **recompilation** project for our exact game.

Grepping our bible for `mstan` returned nothing, and its `recomp` hits are our own disassembly repository's
`tools\recomp` folder. So this is LIKELY a lead we do not have. It belongs in bible section 10a once checked.

---

### 10 and 11. Lower value, recorded so nobody re-reviews them

- **`tools/ghidra/` (11 files)** and **`tools/research/free_space_audit.py`, `capacity_proof.py`,
  `thumb_mem_operands.py`**. Competent work, but we have `scripts\permanent\disasm\` and `rom_space.py`, and
  the disassembly repository answers most of what Ghidra would. Read what `thumb_mem_operands.py` **missed**,
  in section 4 above, rather than the tool itself.
- **The Buu's Fury SDK, the text editor, the warp and enemy randomizers, and the Astro website.** BUU ONLY.
  I say BUU ONLY on two shapes, not one. First, no LOGX or Buu research document names `ALFE`. Second,
  `config/roms.yaml` declares no `actor_sprites`, `placement_types`, `map_entries` or `appearances` table for
  the Legacy of Goku II profile, only `scripts`, `text_strings` and `enemy_stats`. A Legacy of Goku II path
  that neither shape reaches could still exist.

---

## 2. Where we are ahead, so the owner can trade back

Checked by reading their `config/roms.yaml` notes and their own BLOCKED and UNRESOLVED verdicts against our
bible's 17 sections. Six places. The brief knew one.

### 2.1 Map collision. We have it. They are BLOCKED

`docs/research/COLLISION_FORMAT.md` opens: "**Outcome: BLOCKED at the evidence gate.** No bounded static
collision family with verified movement-blocking semantics was established. No codec was written."

They even grepped five upstreams for `collision|walkab|passab|blocking|solid|terrain|obstacle` and got
nothing, and they refuted their own earlier candidate `0x08046AA4` by disassembling it to a row of `bx`
trampolines.

Our Legacy of Goku II collision format is confirmed from `collision_test @0x08005D6C`, with the stride and bit
order pinned. **This is the strongest thing we can offer them.** Their engine is Buu's Fury, so our addresses
will not transfer, but the format, the stride and the bit order give them a hypothesis to test instead of a
blank page.

### 2.2 The enemy stat record. We name six fields they call unread

They declare only HP, the u32 at `+0x04`. Their note says the other fields "have no located reader", "take
only three measured values", or are a pointer to a descriptor struct.

Our bible line 1797 names the whole 24-byte record: `+0` EXP (bosses 0), `+4` HP and max HP, `+8` AI id,
`+0xC`/`+0xD`/`+0xE` STR, POW and END, `+0xF`/`+0x10` melee and ki factors, `+0x14` death descriptor
(`0x086D2B6C` normal, `0x086FF3C4` boss).

They noticed that the scouter loads `+0x0C`, `+0x0D` and `+0x0E` as three separate bytes and could not say
why. We can: they are the three stats the scan screen prints.

### 2.3 The scouter directory. We have the layout, they have only the index

They use the 128-entry directory at file `0x006F8E40`, stride `0x14`, purely to bound the enemy table through
its `+0x10` word. Our bible line 1832 holds the whole 20-byte record: `+0` name, `+4` text, `+8` set id,
`+0xC` portrait id, `+0x10` enemy type, plus the screen that reads it (`@0x08018A38`).

### 2.4 The Legacy of Goku II scene and dialogue system. They declare none of it

Their note: "LOGII dialogue is a script-interleaved, partly JCALG1-compressed stream that cannot be
enumerated without script-VM work; neither is declared approximately."

We have the whole model in bible section 8 and in `scene_lib.py`: the scene runner `@0x0800B520`, record types
0 to 5 with a handler address each, the type table `@0x083EC84C`, the ext handler table `rom:0x3B5D28`, named
ext ops, table walking, and `copy_and_redirect`. Their script support stops at the 43-entry journal family.

### 2.5 Legacy of Goku II sprite sets and palettes. Declared for Buu only

Their `actor_sprites` block, with the 297-entry character table and the 10,980 frame records, is declared for
Buu's Fury only. We have Legacy of Goku II sprite sets, set cloning, the shared OBJ palette at `0x1DA6C8`,
portraits, and the whole sprite guide.

### 2.6 A 16 MB build that ships

They proved a 16 MiB image boots and reads high. We ship builds at that size with patches in the expansion
area and a save that still loads. Their own wording is careful: a declared expansion "is a licence to
generate and allocate", and is "not by itself evidence that the engine reads any particular address".

> [!NOTE]
> One tension to settle with them, not a win. Our bible line 1266 records a community claim that Legacy of
> Goku II and Buu's Fury "do NOT share one engine". This repository is evidence the other way, but the
> evidence has to be the right kind.
>
> **Not evidence:** that their dispatch table is `0x083B5C00` and ours is `rom:0x3B5C00`. `SCRIPT_VM.md`
> measures the Legacy of Goku II profile, so that is our own ROM's table. It matches because it is the same
> file.
>
> **Evidence:** `BUU_SCRIPT_VM.md` gives Buu's own numbers, and they are different addresses with the same
> grammar. Buu's interpreter is `0x08004038` and its primary dispatch table `0x080554C0` with 31 slots,
> `0x00..0x1E`, slot `0x11` NULL meaning terminate. Ours is interpreter `0x080092E4`, table `0x083B5C00`,
> slots 0 to 29, null at slot 17, which is `0x11`. Same shape, same terminator slot, same
> secondary-dispatch byte on ops 02 and 03. Add the shared Webfoot container codec.
>
> So: the FORMATS are shared and the ADDRESSES are not. The community claim is too strong as written. I would
> soften it rather than call it refuted, because nobody has compared a single instruction across both ROMs.

---

## 3. The negative-zero trap: confirmed, measured, and the guard I propose

The brief asked me to confirm that we are safe only because `relocate()` copies untouched ops verbatim, and
to propose a guard test without changing code. Here is the whole picture.

### 3.1 The rule is real

`SCRIPT_VM.md:60-61`: "Negative zero is representable and must round-trip unchanged. Do not canonicalize
encoding or silently discard overflow."

Our encoder cannot honour that. `scene_lib.zigzag()` computes `(v << 1) if v >= 0 else ((-v) << 1) | 1`, and
in Python `-0 == 0`, so the sign bit can never be set for zero. It also emits the shortest group sequence, so
redundant `0x80` padding is dropped.

### 3.2 Both writer paths are safe. CONFIRMED

There are two, not one, and the brief named only the first.

| Path | Line | Behaviour |
|---|---|---|
| `relocate()` | `scene_lib.py:125` | `out += rom[s:_op_end(rom, s)]` copies every untouched op verbatim. It never calls `zigzag()` |
| `copy_and_redirect()` | `scene_lib.py:636` | `data = relocate(...) if edits else bytes(rom[src:src + length])`. Both arms preserve bytes |

`relocate()` touches only two kinds of byte: an edit the caller supplied as hex, and a jump operand it
rewrites in place at `out[new_at[s] - rec + 1]`. Nothing is re-encoded.

Measured, not only read: `relocate(rom, rec, len, {})` returned the original bytes on **86 of 86** real script
runs.

### 3.3 A second trap of the same class, which the brief does not name

`push()` picks the opcode from the value, so it is not an inverse of a decode.

```text
push(0)    -> 0000        (op 0, two bytes)
push(255)  -> 00ff        (op 0, two bytes)
push(256)  -> 1d018400    (op 29 list, four bytes)
push(-1)   -> 1d0103      (op 29 list, three bytes)
```

A decoded op 1 carrying 0 would come back as op 0. A one-value op 29 list would come back as op 0. The
**length and the opcode** both change, not just the bytes.

Good news: this fails closed. `relocate()` verifies `rom[s:end].hex() != old` and raises before any write, so
an `old` string built from a re-encode, rather than sliced from the ROM, stops the build.

I searched with three shapes, and the third one found something. **I first wrote that the search returned
nothing. That was wrong.**

| Shape | Result |
|---|---|
| A value from `unzigzag()` fed back into `zigzag()` or `push()` | the search returned nothing. The only `unzigzag` consumers are `scene_harness.py:252` and `:256`, which push onto an interpreter stack and never re-encode |
| `push(` or `zigzag(` fed from a decoded `.args` | the search returned nothing |
| An `old` hex **built** rather than sliced from the ROM | **two sites** |

The two sites:

- `patches\vegeta_ssj_scene.py:153`
  `out = {rec + o: (push(*v).hex(), push(*_ssj(v)).hex()) for o, v in pushes.items()}`
- `patches\chapter_cards.py:1114`, which concatenates `story_ops(card).hex()` onto an `old`

Neither is a decode-then-re-encode: the values come from a hand-written `EDITS` table, not from
`unzigzag()`. But both build the `old` string by encoding, so if the ROM bytes at those offsets were ever
non-canonical, `relocate()` would refuse and the build would stop. These two modules build today, which is
itself evidence that their target pushes are canonical.

### 3.4 The existing test checks the wrong direction

`scripts\permanent\tests\test_scene_lib.py:44-46` is `test_zigzag_round_trips`, and it asserts
`unzigzag(zigzag(v)) == v`. That is encode then decode, which can never fail. The lossy direction is decode
then encode, and nothing tests it.

### 3.5 The guard I propose. Do not add it in this task

Two small tests in `test_scene_lib.py`, both of which pass today:

1. **Identity under relocate.** For a fixed list of real records, assert
   `relocate(rom, rec, length, {}) == rom[rec:rec + length]`. This pins the verbatim-copy property, so a
   future "tidy-up" of `relocate()` that re-encodes ops fails immediately. Proven on 86 runs already.
2. **A named non-inverse.** Assert that `zigzag(unzigzag(b"\x01", 0)[0]) != b"\x01"`, with a comment naming
   `SCRIPT_VM.md`. A test that states the asymmetry is worth more than one that hides it, because the next
   reader will otherwise assume the pair is a bijection.

> [!WARNING]
> Do not write a test that sweeps the script region for non-canonical varints. That is what produced the three
> false examples in the brief. A varint can be read at any byte. Only a structural walk means anything.

---

## 4. Their tests

387 test files, split `tests/unit/` and `tests/integration/`, run with pytest.

### 4.1 What is a harness we could point at our ROM

Five files gate on the Legacy of Goku II SHA-256 and therefore run against our exact file:

| File | Tests | What it proves |
|---|---|---|
| `tests/integration/test_script_vm_rom.py` | 4 | Byte-exact identity over the whole supported script corpus, plus contract tampering and dispatch |
| `tests/integration/test_logii_text_rom.py` | 22 | The UI string table and pool, end to end. See item 5 |
| `tests/integration/test_authored_image_lg2_rom.py` | - | The authored-image insertion route on our ROM |
| `tests/integration/test_cross_profile_invariants.py` | 12 | A no-op project rebuilds the ROM byte for byte, and the two games cannot be crossed |
| `tests/unit/test_log2_16mib_expansion.py` | 6 | The 16 MiB declaration, determinism, and prefix preservation |
| `tests/unit/test_profile_code_anchors.py` | ~20 | That every declared code anchor resolves, with its evidence class |
| `tests/unit/test_authored_image_lg2_route.py` | - | The same route, portable half |
| `tests/unit/test_rom_editor_coverage.py`, `test_stat_tables.py`, `test_script_vm.py`, `test_free_space_audit.py` | - | Coverage ledger, the 0x18 stat codec, the VM, the free-space audit |

> A first grep of mine, cut off by `head -60`, found only five of these. A case-insensitive grep with no
> `head` returns **25** test files that touch the Legacy of Goku II profile. The eight above are the ones
> that gate on our ROM or on its declared tables.

Their ROM fixture expects `roms/Dragon Ball Z - The Legacy of Goku II (USA).gba`, the same filename we use,
and skips when it is absent. It reads the file before and after and asserts it is unchanged.

### 4.2 Is any of it a conformance suite for a shared format

Yes, two.

1. **`test_script_vm_rom.py::test_exhaustive_supported_corpus_identity`** is a conformance suite for the
   script VM. I already got its value without running it: our decoder walks all 86 runs cleanly. See item 3.
2. **`tests/integration/test_logx_codec_rom.py::test_every_packed_container_decodes_identically`** is a
   differential between two independent decoder implementations of the Webfoot codec. The pattern is worth
   copying even though the corpus is Buu's.

### 4.3 The honest caveat

> [!WARNING]
> Running their tests means running their code. That is barred in this task and it is a decision for the
> owner, not for me. Every one of those tests imports `tools.webfoot.*`, so there is no way to run one
> without executing their package. **My recommendation is that we never run them.** Take the facts the tests
> encode, and write our own tests in our own suite. We get the same assurance without executing a
> third-party package against our ROM.

The rest of the 387 files test their SDK, their Qt workbench, their randomizers and their CI. BUU ONLY or not
about a ROM at all.

---

## 5. The mGBA Lua route, assessed honestly

Our biggest workflow cost is that the owner hand-makes save states so I can measure. This is the section that
decides whether that can change.

### 5.1 What is PROVEN on stock mGBA 0.10.5, the owner's build

I sorted their evidence by emulator build, not by game, because the API does not depend on the game. Two
shapes separate the builds: a script asserting `getGameCode() == "AGB-..."` ran on 0.10.5, because 0.11
returns the bare code; and each launcher's `-RequiredMGBVersion` default.

| Capability | Evidence | Label |
|---|---|---|
| Reading memory, `emu:read` and `readRange` | used throughout the 0.10.5 captures | CONFIRMED |
| Driving input, `emu:setKeys`, `addKey`, `clearKey` | `LOGII_16MIB_RUNTIME.md`: input confirmed reaching the console by reading `KEYINPUT` at `0x04000130`, values `0x037F` LEFT, `0x03DF` UP, `0x03EF` RIGHT, `0x03BF` DOWN. **On our ROM** | CONFIRMED, DIRECT |
| The `frame` callback as a clock | same document, 5,520 frames counted from the emulator's own callback | CONFIRMED |
| `emu:screenshot` | same run produced 47 screenshots, 39 distinct by digest | CONFIRMED |
| **Writing a save state, `emu:saveStateFile`** | `rom006_bootstrap.lua:41`, allowlisted in `inject_mgba_lua.ps1` with the note that both ROM-006 scripts "are only valid on the 0.10.5 build". `consumer-analysis.md:184` describes the run, and `:195` and `:199` show a later probe being handed `-ExpectedState "build\rom006\bootstrap.mss"`, so a downstream tool consumes the produced state | **LIKELY**, on Buu's Fury. I found a described run and a consumer, not a recorded digest of the produced state |
| `emu:reset` | `rom006_bootstrap.lua:31` | CONFIRMED |

**The headline: a state can be produced by script on the owner's build.** That is the capability we want.

### 5.2 What is NOT proven, stated plainly

| Not proven | Why |
|---|---|
| `emu:setBreakpoint` on 0.10.5 | Their table says plainly: 0.10.5 **no**, 0.11 dev **yes**. `mgba_api_probe.lua` exists because it failed |
| `emu:readRegister` on 0.10.5 | Registers come from GDB or the 0.11 build in every capture I read |
| **`emu:loadStateFile` on 0.10.5** | Their section 5 says it "is available on the 0.11 build and is the mechanism". It is silent on 0.10.5. The one Lua caller, `varlen001`, wraps it in `pcall`, which is what you write when you expect it to fail |
| GDB and Lua in one run | Under the GDB launcher a Lua `frame` callback recorded **zero ticks**. They do not combine |
| Any of this on **our** ROM beyond input and frames | Only one Lua script pair ever ran on our ROM: `o1_clean_gameplay_route.lua` with `o1_run_gameplay_route.ps1` |

### 5.3 The real cost, and it is not small

`docs/consumer-analysis.md:580`: "Local mGBA 0.10.5 exposes GDB and savestate startup switches but no Lua
startup switch. GUI scripting is therefore the one required GUI stage."

So on the owner's build there is no `--script`. The Lua must be typed into the Scripting window, and their
answer is `inject_mgba_lua.ps1`, which drives that window by UI Automation. Two details in it are
load-bearing and easy to get wrong: the prompt must be selected by `AutomationId` ending `.prompt`, because
Qt reports an empty `IsReadOnly` for all three edit boxes and "first non-read-only" picks the log pane; and
the Run button must be invoked in a bounded helper process, because mGBA can fail to return from it.

0.10.5 **does** take a savestate startup switch, so loading a state at launch is a command-line matter even
though loading one from Lua is unproven.

### 5.4 What I recommend

1. Write our own Lua, in the shape of `rom006_bootstrap.lua`: assert `ALFE` and 16,777,216 bytes, drive a
   frame schedule, screenshot, `saveStateFile`, then remove the callback and stop.
2. Prove `saveStateFile` on 0.10.5 **with our ROM** first, in a single throwaway run. That is the one
   unproven link in the chain, and it is cheap to settle.
3. Check that `state_dump.py` reads what `saveStateFile` writes. Our `load_state()` already accepts a PNG
   save state, a zlib blob, or a raw file, so it LIKELY works. It is one run to find out.
4. Keep the owner's hand-made states until step 2 passes. Do not retire a working process for an unproven one.

> [!NOTE]
> Their rule, learned twice the hard way, applies to us: the script that launches mGBA for a human session
> must start it and exit, holding no wait loop and no cleanup. Wrapping it in a background job killed two
> live sessions after about twenty seconds.

---

## 6. Vendoring recommendation

**Nothing was copied in this task.** This is the recommendation only.

### 6.1 The licence position

| Question | Answer |
|---|---|
| Their root licence | MPL-2.0 (`LICENSE`, `pyproject.toml:11`) |
| A **fact** we read and re-derive | Free. A table address is not copyrightable, and we cite the source anyway |
| A **file** we copy | Stays MPL-2.0 and keeps its notice. Copying does not relicense it |
| Do copyleft duties trigger today | No. LOG is private and undistributed. MPL-2.0 duties attach on distribution |
| What travels with the file | The notice. Keep it, and keep their provenance comments |

> [!WARNING]
> The root licence is not the whole story. `THIRD-PARTY-NOTICES.md` records that
> `tools/webfoot/formats/webfoot_lz.py` is a cross-language derivative of `spicybung/DragonByteZ`, which is
> **MIT**, and that its distance ladder constants were carried over deliberately. Their own note says "Do not
> remove them" about its provenance comments. They also mark `Arefu/Legacy` as unlicensed research reference:
> take facts from it, never code. Read `THIRD-PARTY-NOTICES.md` before copying any single file.

### 6.2 Where it should live

Use the `zhack\` precedent. `.gitignore` already carries a top-level folder for another modder's work, with
the comment "another modder's hack: the source ROM, its IPS patch, and the study sheets taken from it".

**Recommendation:** a new top-level `reference\dragonbyte-z\` folder, added to `.gitignore` beside `zhack/`,
holding a read-only copy. Reasons: it matches a rule the owner already set, it keeps third-party material out
of `docs\` and `scripts\`, and it never lands under `data\`, which we never write to.

### 6.3 What to copy, and what to leave in the clone

**Copy (documents only, about 20 files).** These are the ones we will re-read many times, and a local copy
survives the clone being updated or deleted.

| Path in their repo | Why |
|---|---|
| `docs/research/SCRIPT_VM.md` | DIRECT. The VM, the opcode table, the negative-zero rule |
| `docs/research/LOGII_TEXT_FORMAT.md` | DIRECT. The string table and pool |
| `docs/research/LOGII_AUTHORED_IMAGE_ROUTE.md` | DIRECT |
| `docs/research/LOGII_16MIB_RUNTIME.md` | DIRECT. Corroborates our expansion |
| `docs/research/MAP_RECORD_EDITING_VERIFICATION.md` | DIRECT |
| `docs/research/CELL_PALETTE_ROUTE_C.md` | Names our game in prose |
| `config/roms.yaml` | The profile block for our ROM, with its evidence |
| `docs/skills/mgba-runtime.md` | The runtime rulebook. The single most useful file for our workflow |
| `docs/runtime-capture.md` | Its canonical ordering |
| `docs/research/LOGX_CONNECTOR_PROVENANCE.md` and `_VERIFICATION.md` | The door list, and the `ldm` lesson |
| `docs/research/LOGX_CODEC_PROVENANCE.md` and `docs/research/WEBFOOT_LZ_LITERAL_BASE.md` | Codec corroboration |
| `docs/research/COLLISION_FORMAT.md` | The place we can help them |
| `docs/research-conventions.md` | Their evidence and readiness vocabulary |
| `LICENSE` and `THIRD-PARTY-NOTICES.md` | **Mandatory.** The notice travels with the files |

**Leave in the clone and simply read:** `src/` (an Astro website), `tools/webfoot/` (the Buu SDK, 61 files),
`tools/buufury_text/`, the randomizers, `tests/` (387 files), `package-lock.json`, `uv.lock`, the CI, and the
other 260-odd documents. Nothing there pays for the weight.

**Do not copy any of their `.py`, `.lua` or `.ps1` into our tree.** Two reasons, and the second is the real
one. First, the untrusted-code rule. Second, our tool index says a tool almost always exists and writing a
second one is the default failure here. We want their **rules**, written into our own scripts with credit, not
their files sitting beside ours where a future agent runs one by mistake.

The one exception worth discussing with the owner is a side-by-side **read-only** copy of
`tools/runtime/rom006_bootstrap.lua`, `load_mgba_lua.ps1` and `inject_mgba_lua.ps1` inside
`reference\dragonbyte-z\`, purely as a model while we write ours. They stay in the ignored folder. They are
never on a build list and never run.

---

## 7. What I did not do, and what a later pass should

Stated so nobody reads this catalogue as complete.

- **I read about 25 of their 286 documents in full.** The rest I reached by grep. A document that names our
  game only in prose, and never by digest, could have escaped every shape I used.
- **The scene varint sweep covered 7 tables and 113 records.** The game has many more. A non-canonical
  operand elsewhere would not appear in my count of zero.
- **I did not re-derive a single Buu address for our ROM.** Every SHARED ENGINE item is a format plus a
  method, not an address.
- **I did not run their tests, their SDK or any of their Lua.** By instruction, and I recommend we keep it
  that way.
- **`emu:saveStateFile` on 0.10.5 is proven on Buu's Fury, not on our ROM.** One run settles it.
- **Their BUU ONLY verdict rests on two shapes**, the absence of `ALFE` in their research documents and the
  absence of those table declarations in `roms.yaml`. A Legacy of Goku II path neither shape reaches could
  exist.

## 8. The three things I would do next, in order

1. **Prove `emu:saveStateFile` on stock mGBA 0.10.5 with our ROM.** It is one run, and it unblocks the
   workflow change that is worth more than everything else in this catalogue. Note that I could not find a
   recorded digest of a state their script produced, only the run description and a consumer, so this is the
   weakest link in my highest-ranked item.
1a. **Compare the owner's `mGBA.exe` SHA-256 with their pinned `5A3C98C2...F247`.** One command. If it
   matches, every 0.10.5 result in their repository applies to his exact binary rather than to a version
   string.
2. **Merge the DIRECT facts into the bible.** `rows.md` in this folder holds them, tagged `DBZ`.
3. **Add the two guard tests from section 3.5** to `test_scene_lib.py`, in a task that owns that file. Not
   now: another agent is working in this tree.

## 9. Scripts this review wrote

All in `scripts\one-time\2026-11-06-dragonbyte-review\`. Each reads the base ROM, writes nothing, imports
only our `scene_lib`, and runs under `py -3.14 -I`.

| Script | What it answered |
|---|---|
| `varint_roundtrip.py` | The brief's three sites, their static43 corpus against our op walker, and relocate identity |
| `varint_structural.py` | How many varint operands a structural walk actually reaches in their corpus. One |
| `scene_varint_sweep.py` | 962 real operands over 7 scene tables, and whether the brief's three sites are inside any record |
