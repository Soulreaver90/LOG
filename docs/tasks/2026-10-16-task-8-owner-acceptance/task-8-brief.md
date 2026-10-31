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

### Task 8: My acceptance run

**Files:**
- Modify: `docs\build-log.md`

- [ ] **Step 1: I load** `builds\log2_poc.gba` with `test-data\saves\log2_lv40_postcell.sav` (File > Load alternate save game, cheat off, cold boot).
- [ ] **Step 2: I run the design's acceptance tests 1, 2, 3, 4 and 5** (section 8.3). For test 3, I read the RAM addresses from `docs\research\re-forms.md` in the mGBA memory viewer before and after the transform, and hits the same enemy in Super Saiyan and in Super Saiyan 2.
- [ ] **Step 3: Record** pass or fail per test, with screenshots, in `docs\build-log.md`. Failures go back to the owning task.
