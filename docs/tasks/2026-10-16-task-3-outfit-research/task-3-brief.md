## Global Constraints

- Base ROM: `data\roms\Dragon Ball Z - The Legacy of Goku II (USA).gba`, SHA-1 `18e0715dec419f3501c301511530d2edcd590f8b`. Never write anything under `data\`.
- Builds go to `builds\`. Each build prints its SHA-1 and appends a line to `docs\build-log.md`.
- ROM size: every build is expanded to 16 MB (16777216 bytes) with 0xFF fill. New data goes in the expansion area rom:0x800000-rom:0xFFFFFF. The base 8 MB has no usable free space (Task 1 finding). I approved expansion 2026-10-16 after a 16 MB padded ROM passed the anti-piracy point (East District 439 to the world map).
- The shared OBJ palette at ROM `0x1DA6C8` is not changed. New art uses existing palette indices only.
- The save format is not changed. No new save fields. Old saves must load.
- Rage in the Cell fight is unchanged: its stats, its art set id behavior, and no ki drain. Only playable forms change.
- Super Saiyan 2 values (mine): +20 to STR, POW and END. Ki drain higher than Super Saiyan; start at twice the Super Saiyan drain. Unlock: story flag 195 (Cell beaten).
- Gi look (mine): no white neck piece, brown boots (palette 34, 35), purple toward Piccolo (palette 88, 89, outline 211), red sash, blue wristbands.
- Cutscenes between the Time Chamber and the point where Gohan is playable keep the armor (mine).
- Tests: `py -3 -I -m unittest discover -s scripts\permanent\tests -t scripts\permanent -v` from the root. All must pass before a task is done.
- Python files carry a header block like the existing scripts. No em or en dashes in any file. No byte order mark.
- Install nothing. No git (this folder is not a repo): the build log replaces commits.
- Every reverse-engineering claim is labelled CONFIRMED (with address and disassembly or bytes), LIKELY or SPECULATIVE. Code changes build only on CONFIRMED claims.
- **RE bible:** `docs\RE-BIBLE.md` is the index of every known fact. Read it before a task. Every task that learns a fact adds one line to it, with the tag shapes in its section 1, in the same task. Search it before you search the ROM.

## Review Focus

1. **Old saves after the chamber.** A save made before this patch, with Gohan post-chamber (appearance id 2), loads and shows the gi when playable. Expected: yes. Owned by Task 5 (`test_appearance_2_resolves_to_gi_clone`).
2. **Cutscenes keep the armor.** Every code path that shows armored Gohan without going through the playable appearance still points at the original armor sets. Owned by Task 5 (`test_armor_sets_untouched`).
3. **Super Saiyan 2 before Cell is beaten.** With flag 195 clear, the transform input never reaches Super Saiyan 2, and the Cell fight still forces Rage. Owned by Task 6 (`test_ssj2_gate_reads_flag_195` plus my test 4).
4. **Ki runs out in Super Saiyan 2.** Gohan drops out of the form the same way he does from Super Saiyan. Owned by Task 6 (my test 3).
5. **An animation the source set lacks.** A cloned set never points at a missing or corrupt frame; every record decodes to w*h bytes. Owned by Task 2 (`test_clone_every_record_decodes`).

## Review Focus

1. **Old saves after the chamber.** A save made before this patch, with Gohan post-chamber (appearance id 2), loads and shows the gi when playable. Expected: yes. Owned by Task 5 (`test_appearance_2_resolves_to_gi_clone`).
2. **Cutscenes keep the armor.** Every code path that shows armored Gohan without going through the playable appearance still points at the original armor sets. Owned by Task 5 (`test_armor_sets_untouched`).
3. **Super Saiyan 2 before Cell is beaten.** With flag 195 clear, the transform input never reaches Super Saiyan 2, and the Cell fight still forces Rage. Owned by Task 6 (`test_ssj2_gate_reads_flag_195` plus my test 4).
4. **Ki runs out in Super Saiyan 2.** Gohan drops out of the form the same way he does from Super Saiyan. Owned by Task 6 (my test 3).
5. **An animation the source set lacks.** A cloned set never points at a missing or corrupt frame; every record decodes to w*h bytes. Owned by Task 2 (`test_clone_every_record_decodes`).

---

### Task 3: Reverse engineering, outfit selection

**Files:**
- Create: `docs\research\re-outfit.md`

**Interfaces:**
- Produces, as CONFIRMED facts with addresses: (a) how a character record's appearance id becomes a sprite set during play (the run-time table near `0x08009350`), (b) every code path or script that uses sets 55 and 56 (or their appearance ids), split into "playable" and "cutscene", (c) the exact patch site Task 5 will change, with its original bytes.

- [ ] **Step 1: Trace appearance id 2 to set 56** using the post-Cell test save `test-data\saves\log2_lv40_postcell.sav` (Gohan appearance 2, set 56). Start from the appearance table at `rom:0x1D967C` (22 entries of 20 bytes: +1 set id, +0 bit 0 transformed, +4 transform target, +5 base form) and its readers `@0x080042BC`, `@0x08003ED4`. If the playable sprite reads set id from this table, changing entry 2's +1 (and the Super Saiyan entry it names at +4) may be the whole outfit switch.
- [ ] **Step 2: List every user of sets 55 and 56** (code xrefs to their table entries, and script commands in the event scripts that name them).
- [ ] **Step 3: Choose the patch site** with this rule: change only what playable appearance 2 resolves to, so old saves get the gi and cutscenes that use set ids directly keep the armor. If cutscenes also go through appearance 2, stop and report the conflict to me with options.
- [ ] **Step 4: I verify** each CONFIRMED line against the disassembly before Task 5 starts.

---

