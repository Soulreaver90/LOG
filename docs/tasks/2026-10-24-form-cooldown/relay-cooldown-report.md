# Relay cooldown fix: trial module report

Trial build of the plain design I approved on 2026-10-25 ("Agreed, menu unchanged, just plain").

Labels: **C** = CONFIRMED (bytes, listing or interpreter run quoted), **L** = LIKELY, **S** = SPECULATIVE.

---

## SHIPPED and PENDING

The trial ROM, its save and the module are ready to play. Only the in-game check is open.

**SHIPPED**

| Ask | Result |
|---|---|
| "Agreed, menu unchanged, just plain." | Built: every scripted ext 70 clears the cooldown; Switch Characters is byte equal to r39; variant B not built (C) |
| Trial module and tests | `scripts\permanent\patches\relay_cooldown.py`, `scripts\permanent\tests\test_relay_cooldown.py` (18 tests, all pass) (C) |
| Re-derive every byte and pool word | Hand-encoded from the Thumb formats in `make_trial_cooldown.py`, with no shared code with the encoder or `thumb_dis`. Equal to the report bytes and to the built bytes (C) |
| Free space by the project's allocator | `alloc.alloc(28)` gave `rom:0x90A308`. All 0xFF in r39, and no ROM word names it (C, `free_check.txt`) |
| No other module writes the same bytes | No r39, `celljr_fight` or `vegeta_ssj_scene` site overlaps. The ext 70 word is vanilla in both trials (C) |
| New list | `scripts\permanent\build_list_trial_cooldown.txt` = `build_list.txt` lines + `relay_cooldown`. No other list changed. `--list` still gives r39 `aa51dc16...` (C) |
| Trial ROM | `builds\mockups\2026-10-25-relay-cooldown\log2_poc_r39_cooldown.gba`, SHA-1 `22943be822a97d279f06d7ad31b02cdc5196f136` (C) |
| Save | `builds\mockups\2026-10-25-relay-cooldown\log2_poc_r39_cooldown.sav`, SHA-1 `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` (byte copy of the celljr save) (C) |
| Diff runs r39 to new | 2 runs, 31 bytes, both inside named sites (C) |
| Full suite | Run once at the end with the `global.md` command: `Ran 744 tests in 379.311s`, `OK`, no failures, errors or skips. That includes the 18 new tests (C, `suite.txt`) |
| Bible rows | `scripts\one-time\2026-10-25-relay-cooldown\bible_rows.md`, tag RCD, sections 6, 11, 12, 13 |

**PENDING**

| Item | Who does the next step |
|---|---|
| Play the trial (steps below) and say yes or no | Me |
| On yes: move the `relay_cooldown` line into `build_list.txt`, retire `build_list_trial_cooldown.txt`, merge the RCD rows | Me |
| Merge order with the other trials: the wrapper address depends on the list order (see "Other trials"). Each build allocates its own space, so any order works | Me |

---

## The bytes and their decode

The module writes one table word and one 28-byte wrapper. No vanilla code byte changes.

**Hook (C).** The ext op table is `0x083B5D28`. Word 70 is `0x3B5D28 + 4 x 70 = rom:0x3B5E40`.

- Exactly two ROM words name the table: `rom:0x921C` and `rom:0x92DC` (`@0x08009232` `ldr r0,=0x083b5d28` reads `rom:0x92DC`). Both are unchanged, so every dispatch variant reads the hooked word (`test_every_dispatch_reads_the_hooked_table`).
- Vanilla ext 70 has no other name. Before: the only word equal to `0x0800A785` is `rom:0x3B5E40`. After: the only one is the wrapper's own pool word `rom:0x90A31C` (`test_vanilla_ext70_has_no_other_name`). Codemap `functions.csv` lists 0 BL callers for `0x0800A784` (C).

| | Before (base, r39) | After (trial) |
|---|---|---|
| `rom:0x3B5E40` | `85 A7 00 08` = `0x0800A785` (vanilla ext 70) | `09 A3 90 08` = `0x0890A309` (wrapper, Thumb bit) |

**Wrapper at `rom:0x90A308` (C).** `make_trial_cooldown.txt`, decoded by `thumb_dis`:

```
0890a308  10b5      push {r4,lr}
0890a30a  044b      ldr r3,=0x0800a785     ; vanilla ext 70
0890a30c  00f005f8  bl 0x890a31a           ; lands on bx r3
0890a310  0349      ldr r1,=0x086f7e50
0890a312  4968      ldr r1,[r1,#0x4]       ; 0x03000E90, save struct
0890a314  0022      mov r2,#0x0
0890a316  8a60      str r2,[r1,#0x8]       ; cooldown 0x03000E98 = 0
0890a318  10bd      pop {r4,pc}
0890a31a  1847      bx r3                  ; to 0x0800A784, Thumb
0890a31c  .word 0x0800A785
0890a320  .word 0x086F7E50
```

All 28 bytes: `10b5044b00f005f80349496800228a6010bd184785a70008507e6f08`.

**Why each word is right (C).**

- `0x0800A785` is vanilla ext 70. Body `rom:0xA784` = `08b5fff77bff9d48006af9f7a1fb08bd` = `push {r3,lr} ; bl 0x800a680 (set_leader) ; ldr r0,=0x083b5c78 ; ldr r0,[r0,#0x20] ; bl 0x8003ed4 (appearance_revert) ; pop {r3,pc}`. The module checks these 16 bytes before the first write.
- `0x086F7E50` is the pointer that the vanilla base tick uses: `@0x0801702A ldr r7,=0x086f7e50 ; @0x0801702C ldr r0,[r7,#0x4] ; ... ; @0x08017036 str r2,[r0,#0x8]`. `rom:0x6F7E54` = `0x03000E90` in base and r39. The module also checks this word.
- The call goes through `bx r3`, because a Thumb BL reaches only about 4 MB. `rom:0xA784` is about 9 MB below `rom:0x90A308`.
- r0 (the script context) is not written before the call, so set_leader pops its argument from the right script. r0 after the call (the handler result) is not written either.

**Interpreter run on the trial ROM (C, not in game).** `tests.test_ssj2.Cpu` runs the thumb_dis text, with vanilla ext 70 stubbed:

- The stub sees r0 = the context passed in.
- After the wrapper: cooldown 0x500 becomes 0. r0 = the stub's 0x1234. r4 and sp are restored. The leader byte is unchanged.
- Then the ROM's own ability 12 test word (`rom:0x1D99C8`) for Vegeta (record 2, entry 9, EP 120, `flag:149`) returns 1.
- Control: without the wrapper, cooldown 0x500 gives 0.

---

## Checks before the first write (module rules)

The module refuses before it writes anything when a source byte differs. Tests flip each source byte and confirm that the ROM is unchanged.

1. `"relay_cooldown"` already in `alloc.notes`: raise (second run). A second run on the built ROM also fails on the table word.
2. Table word `rom:0x3B5E40` = `0x0800A785`.
3. Ext 70 body `rom:0xA784` = the 16 bytes above.
4. Save pointer word `rom:0x6F7E54` = `0x03000E90`.
5. No earlier module lists `rom:0x3B5E40` in its `"sites"`. Both shapes are covered: triples, and bare offsets (`superperfect_cell`).
6. The allocated 28 bytes are all 0xFF, and no absolute aligned ROM word names them (`bf_ki_pool.words_naming` with no base-relative vtable ranges). A named chunk stays unused and goes into notes `"skipped"` (here: none). A vtable slot that points into 0xFF bytes would point at no code, so the base-relative half is not needed here (L).
7. The wrapper is assembled at the real address. A size change raises.

---

## Diff runs r39 to the trial ROM

Two runs, both inside the module's sites (C, `make_trial_cooldown.txt`):

| Run | Bytes | Site |
|---|---|---|
| `rom:0x3B5E40`-`0x3B5E42` | 3 | ext 70 table word (its top byte 0x08 does not change) |
| `rom:0x90A308`-`0x90A323` | 28 | ext 70 cooldown wrapper |

**Menu swap path byte equal to r39 (C, `test_menu_swap_path_is_byte_equal_to_r39`).** `switch_characters` `rom:0x11172` (264 bytes, codemap), `set_leader` `rom:0xA680` (140), `appearance_revert` `rom:0x3ED4` (50), party screen vtable slot `rom:0x247CC` (`0x080247A8` +0x24, names `switch_characters`), the ext 70 body, the dispatch `@0x08009224` (44), the word `rom:0x3B6088`, and the ext 115 word `rom:0x3B5EF4`. The whole-ROM diff test also proves that every other byte is equal.

**Correction to the FCD dispatch row.** FCD says a second per-op table `0x083B5F70` is called after the handler with the same op number. Word 70 of that table, `rom:0x3B6088`, is `0x7A74FA08`, which is not a ROM address (C). So either ext 70 does not run through the `@0x08009224` variant, or that table is not one pointer per op (S: not traced). The hook proof does not rest on that listing: it rests on the two table pool words and on the one name of vanilla ext 70 (above).

---

## Builds and SHA-1s

Every build below came from the same base ROM (C, `make_trial_cooldown.txt`).

| Build | SHA-1 |
|---|---|
| r39 (`builds\log2_poc_r39.gba`, file read) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0` |
| `log2_build.py --list` (CLI, `scratch\test-roms\cooldown_cli_main.gba`) | `aa51dc16da5f6b633c0f50dc566864fe43f89ff0`, bytes equal to r39 |
| Trial ROM, in memory, written with `"xb"` | `22943be822a97d279f06d7ad31b02cdc5196f136` |
| `log2_build.py --list build_list_trial_cooldown.txt` (CLI, `scratch\test-roms\cooldown_cli_trial.gba`) | `22943be822a97d279f06d7ad31b02cdc5196f136` |
| Trial save (copy of `log2_poc_r39_celljr.sav`) | `aa8efb2adaa7aa87f4cff27ceb7244368bd02759` (source checked equal first) |

`docs\build-log.md` has one new line: `2026-10-25 10:49 build log2_poc_r39_cooldown.gba ... sha1=22943be8...`. The CLI builds wrote to `scratch\test-roms\cooldown-cli-log.md`, not to the build log.

---

## Other trials

The module was applied in memory after each other trial list (C, `make_trial_cooldown.txt`). No file of those trials was touched.

| List | ext 70 word before | Wrapper | Runs | Overlap with `celljr_fight`, `vegeta_ssj_scene`, `superperfect_cell` sites |
|---|---|---|---|---|
| `build_list_trial.txt` (celljr_fight) | `0x0800A785` | `rom:0x90A67C` | 2, inside its sites | none |
| `build_list_trial_vegeta.txt` | `0x0800A785` | `rom:0x90A800` | 2, inside its sites | none |

- In the cooldown trial ROM the wrapper sits at `rom:0x90A308`. In the celljr trial ROM, that address holds the seq 31 copy. These are separate ROMs, and each build allocates its own space, so there is no clash (C).
- The vegeta module is being changed by another task. The vegeta row is true for the module as it was at 10:49 AM (L for later versions).

**`rom_space.find_free` (C, `free_check.txt`).** It shows no free run at the wrapper. The r39 0xFF run `rom:0x90A308`-`0xF2813F` is 0x61DE38 bytes long, and 6,480 aligned words name an address inside it (base data that looks like a pointer, for example `rom:0x7DC4` = `0x08C93104`). find_free drops a whole run for one such word. The modules check only their own chunk, and no word names `rom:0x90A308`-`0x90A323`.

---

## Effects and risks

The fix changes what happens at every scripted ext 70, as the study said.

| Effect | Assessment |
|---|---|
| Every scripted `ext 70` clears the cooldown: the Cell Games relay, chamber entry and exit, story leader changes (FCD site list) | The new leader starts ready to transform. Harmless: revert does not read the cooldown, and the Super Saiyan 2 step does not test it (FCD, C) |
| `ext 70` with the same leader also clears it | I chose the plain design over variant B (C, my words) |
| Switch Characters in the menu | Unchanged: byte equal to r39, and it does not run ext 70 (C) |
| ext 115 (set_leader, no revert) | Not hooked. No relay uses it (FCD, C for its one decoded site) |
| HUD cooldown bar | The HUD repaints when its cached index differs, so the bar should clear on the next frame (FCD: C code, L in game) |
| Saves | Only a value changes. No format change (C) |

---

## My play steps

The trial needs one run through the vanilla Cell Jr relay. This ROM does not have `celljr_fight`, so the Jr fights are the vanilla ones.

1. Load `builds\mockups\2026-10-25-relay-cooldown\log2_poc_r39_cooldown.gba`. mGBA pairs `log2_poc_r39_cooldown.sav` by name.
2. Pick **slot 3**: Goku at the Cell Games Arena arrival (map 14,1,1), `flag:191` set, cooldown 0 in the slot (`log2_save.py info`: "+8 0x0").
3. Play Goku's fight and the scenes up to Cell spawning the Jrs. The Cell Games has no save point, so **make a save state before the Jr fights start**.
4. **Piccolo vs Jr.** Transform to Super Namek, then win the fight while you are still transformed.
5. **Vegeta takes over.** Transform at once. Pass: Vegeta transforms, with no refusal sound. Optional: the mGBA memory viewer shows u32 `0x03000E98` = 0 on his first controlled frame.
6. **Vegeta vs Jr.** Stay transformed and win.
7. **Trunks takes over.** Transform at once. Pass: Trunks transforms, with no refusal sound.
8. **Control (optional).** The same moment on r39 plays the refusal sound (FCD: cooldown about 0x4EC to 0x500).

The menu swap is not part of the play test. Switch Characters opens only from a save point menu, and zone 14 has none (bible R27 row). Its bytes are equal to r39 (C).

---

## Files

- `scripts\permanent\patches\relay_cooldown.py`: the trial module.
- `scripts\permanent\tests\test_relay_cooldown.py`: 18 tests (list, refusals, decode, names, diff, menu path, interpreter).
- `scripts\permanent\build_list_trial_cooldown.txt`: the trial list.
- `scripts\one-time\2026-10-25-relay-cooldown\make_trial_cooldown.py` and `make_trial_cooldown.txt`: hand encoding, build, save copy, CLI builds, diff runs, other trials.
- `scripts\one-time\2026-10-25-relay-cooldown\free_check.py` and `free_check.txt`: the find_free explanation.
- `scripts\one-time\2026-10-25-relay-cooldown\suite.txt`: the full suite output.
- `scripts\one-time\2026-10-25-relay-cooldown\bible_rows.md`: RCD rows.
