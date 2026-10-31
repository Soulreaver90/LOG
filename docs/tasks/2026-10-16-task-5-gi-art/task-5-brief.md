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

### Task 5: Gi art and the outfit switch

**Files:**
- Create: `scripts\permanent\art\gi_art.py`
- Create: `scripts\permanent\patches\gohan_gi.py`
- Create: `scripts\permanent\tests\test_gi.py`
- Output: `art\gi_base\`, `art\gi_ssj\`, `art\gi_ssj2\`, contact sheets `art\*_sheet.png`

**Interfaces:**
- Consumes: `export_set`, `clone_set`, `image_to_tiles` (Task 2); the patch site from `docs\research\re-outfit.md` (Task 3).
- Produces: `make_gi_base(set53_dir: Path, out_dir: Path) -> None`, `make_gi_form(gi_base_dir: Path, hair_set_dir: Path, out_dir: Path) -> list[str]` (returns the frame keys it could not match, for hand work), and `patches.gohan_gi.apply(rom, alloc)`.
- Frame correspondence: the gi sets follow the record layout of the set they replace (gi base follows 56, gi Super Saiyan follows 59, gi Super Saiyan 2 follows 58 where 58 has the frame and 59 otherwise). Match frames by (anim, dir, index).

- [ ] **Step 1: Write the failing tests**

```python
def test_gi_uses_only_allowed_indices():      # palette rule
    for img in gi_frames():
        assert set(img.getdata()) <= ALLOWED_INDICES   # indices already used by sets 53, 56, 58, 59 plus 34, 35, 88, 89, 211, 26, 72, 195

def test_gi_frames_keep_record_sizes():
    for key, img in gi_frames_by_key():
        assert img.size == source_record_size(key)   # w, h of the record the frame replaces

def test_appearance_2_resolves_to_gi_clone():  # Review Focus 1
    rom = built_rom(["gohan_gi"])
    assert resolve_playable_appearance(rom, 2) == gi_base_set_offset(rom)

def test_armor_sets_untouched():               # Review Focus 2
    rom = built_rom(["gohan_gi"])
    assert set_bytes(rom, 55) == set_bytes(BASE, 55) and set_bytes(rom, 56) == set_bytes(BASE, 56)
```

- [ ] **Step 2: Run and see them fail.**
- [ ] **Step 3: Implement `make_gi_base`.** Start from set 53 (Demon Clothes). Map its outfit indices to the gi colors in Global Constraints. Replace the neck piece with gi or skin pixels. Reshape the feet to brown boots like Piccolo's (Piccolo sheet in `data\sprites\`). Keep every frame's size.
- [ ] **Step 4: Implement `make_gi_form`.** Copy hair and face pixels from the hair set frame onto the matching gi base body. Return unmatched keys.
- [ ] **Step 5: my art gate.** Build the three contact sheets and stop. I approve or marks frames for change. Do not build a ROM with unapproved art.
- [ ] **Step 6: Implement `patches.gohan_gi.apply`.** Clone sets 56, 59 and 58 with the approved frames, then change the patch site from Task 3 so playable appearance 2 resolves to the gi base clone, and the Super Saiyan form resolves to the gi Super Saiyan clone.
- [ ] **Step 7: Run all tests and see them pass. Build** `builds\log2_poc_gi.gba` and log its SHA-1.

---

