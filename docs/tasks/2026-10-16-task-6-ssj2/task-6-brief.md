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

### Task 6: Usable Super Saiyan 2

**Files:**
- Create: `scripts\permanent\patches\ssj2_form.py`
- Create: `scripts\permanent\tests\test_ssj2.py`
- Output: Z2 icon art `art\hud_z2.png`

**Interfaces:**
- Consumes: patch sites and form table from `docs\research\re-forms.md` (Task 4); the gi Super Saiyan 2 clone offset from `patches.gohan_gi` (Task 5).
- Produces: `patches.ssj2_form.apply(rom, alloc)`; it runs after `gohan_gi`.

- [ ] **Step 1: Write the failing tests**

```python
def test_ssj2_form_values():
    rom = built_rom(["gohan_gi", "ssj2_form"])
    f = read_form(rom, SSJ2_FORM_ID)
    assert (f.str_bonus, f.pow_bonus, f.end_bonus) == (20, 20, 20)
    assert f.ki_drain == 2 * read_form(rom, SSJ_FORM_ID).ki_drain

def test_ssj2_gate_reads_flag_195():            # Review Focus 3
    assert transform_step_condition(built_rom(...), from_form=SSJ_FORM_ID) == ("flag", 195)

def test_rage_unchanged():
    assert read_form(built_rom(...), RAGE_FORM_ID) == read_form(BASE_ROM, RAGE_FORM_ID)
```

- [ ] **Step 2: Run and see them fail.**
- [ ] **Step 3: Draw the Z2 icon** from the LoG II HUD "Z" with a "2", in the style of the Buu's Fury "Z3". I approve it with the Task 5 art gate if it is ready by then, or alone.
- [ ] **Step 4: Implement `ssj2_form.apply`.** Add the Super Saiyan 2 form entry (gi Super Saiyan 2 clone, Rage lightning aura, +20, drain twice Super Saiyan), make the transform input step base, Super Saiyan, Super Saiyan 2 only when flag 195 is set, and show the Z2 icon while in the form.
- [ ] **Step 5: Run all tests and see them pass. Build** `builds\log2_poc.gba` and log its SHA-1.

---

