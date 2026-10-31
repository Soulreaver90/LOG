# Slice 1 Proof of Concept Implementation Plan

> Work through this plan one task at a time. Steps use checkbox (`- [ ]`) syntax for tracking.

Author: Joseph Gonzalez.

**Goal:** A patched LoG II (USA) ROM where playable Gohan wears the purple gi after the Time Chamber, and can transform into a usable Super Saiyan 2 (+20 stats, ki drain, "Z2" HUD icon) after Cell is beaten.

**Architecture:** A Python build script copies the untouched base ROM and applies patch modules in order. New art goes into free ROM space as raw (type 0) frames inside cloned sprite sets, so no compressor is needed and the original sets stay intact for cutscenes. Code and table changes come from reverse-engineering notes written in Tasks 3 and 4, each proven before it is used.

**Tech Stack:** Python 3.14 (`py -3 -I`) with Pillow, stdlib `unittest`; headless Ghidra 12.1.4 for reading code; mGBA 0.10.5 for my test.

**Spec:** `docs\design\2026-10-16-log-merge-design.md` (section 8). Research: `research-notes.md`, `re-sprite-decompression.md`, `re-save-format.md` in the same folder.

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

---

### Task 1: Build pipeline and free space

**Files:**
- Create: `scripts\permanent\rom\rom_space.py`
- Create: `scripts\permanent\log2_build.py`
- Create: `scripts\permanent\patches\__init__.py` (empty)
- Create: `scripts\permanent\tests\test_build.py`
- Create: `docs\build-log.md`

**Interfaces:**
- Produces: `find_free(rom: bytes, min_len: int = 0x1000) -> list[tuple[int, int]]` returns 4-aligned runs `(offset, length)` of a single fill byte (0xFF or 0x00) at least `min_len` long, that no known pointer targets.
- Produces: `class Allocator(rom_len: int, regions: list[tuple[int, int]])` with `alloc(size: int, align: int = 4) -> int` (file offset; raises `MemoryError` when full) and `used() -> list[tuple[int, int]]`.
- Produces: `build(base: Path, out: Path, patch_names: list[str]) -> str` returns the output SHA-1. Each patch is a module `patches.<name>` with `apply(rom: bytearray, alloc: Allocator) -> None`.

- [ ] **Step 1: Write the failing tests**

```python
def test_build_without_patches_matches_base():
    sha = build(BASE, OUT, [])
    assert sha == "18e0715dec419f3501c301511530d2edcd590f8b"

def test_build_never_writes_under_data():
    with self.assertRaises(ValueError):
        build(BASE, ROOT / "data" / "x.gba", [])

def test_free_space_found_and_size_kept():
    runs = find_free(BASE.read_bytes())
    assert runs == [] or all(length >= 0x1000 for _, length in runs)   # base 8 MB is full (Task 1 finding)
    assert len(OUT.read_bytes()) == 16777216   # expanded build

def test_allocator_never_overlaps():
    a = Allocator(8388608, [(0x700000, 0x100)])
    x, y = a.alloc(0x80), a.alloc(0x80)
    assert y >= x + 0x80
    with self.assertRaises(MemoryError):
        a.alloc(0x10)
```

- [ ] **Step 2: Run the tests and see them fail** (module not found).
- [ ] **Step 3: Implement `rom_space.py` and `log2_build.py`.** `find_free` must skip runs that any 4-aligned ROM word points into (`0x08000000 + offset` inside the run), so a table of 0xFF bytes in use is not mistaken for space. If total free space is below `0x40000`, stop and report the number to me.
- [ ] **Step 4: Run the tests and see them pass.**
- [ ] **Step 5: Record** the free-space total and the largest run in `docs\build-log.md`.

---

### Task 2: Sprite export, import and set cloning

**Files:**
- Create: `scripts\permanent\rom\log2_sprites.py`
- Create: `scripts\permanent\tests\test_sprites.py`

**Interfaces:**
- Consumes: `webfoot_decompress.read_set`, `read_record`, `frames_of`, `unpack_frame(rom, hdr) -> (type, size, data, packed)`; `rom_space.Allocator`.
- Produces: `tiles_to_image(data: bytes, w: int, h: int, palette: bytes) -> PIL.Image` (mode "P", 8bpp tiles in 1D order to pixels) and `image_to_tiles(img: PIL.Image) -> bytes` (exact inverse).
- Produces: `export_set(rom: bytes, set_off: int, out_dir: Path) -> Path` writes one indexed PNG per unique frame header and `manifest.json` (list of `{anim, dir, index, dx, dy, w, h, attr0, attr1, header, png}`), returns the manifest path.
- Produces: `clone_set(rom: bytearray, src_set_off: int, frames: dict[int, bytes], alloc: Allocator) -> int`. Copies the set header, its animation tables and record lists into allocated space. Every record keeps dx, dy, w, h and attributes. A record whose header offset is a key in `frames` points to a new raw frame `{u32 0, u32 len, data}`; other records keep their original header pointer. Returns the new set offset.

- [ ] **Step 1: Write the failing tests**

```python
def test_tiles_image_round_trip():          # set 53, every frame
    for hdr, data, w, h in frames_53:
        assert image_to_tiles(tiles_to_image(data, w, h, PALETTE)) == data

def test_clone_unchanged_is_identical():     # set 56 cloned with no new frames
    new = clone_set(rom, SET_56, {}, alloc)
    assert decoded_frames(rom, new) == decoded_frames(rom, SET_56)

def test_clone_every_record_decodes():       # Review Focus 5
    new = clone_set(rom, SET_59, {h: bytes(len(d)) for h, d in frames_59.items()}, alloc)
    for rec in all_records(rom, new):
        _, size, data, _ = unpack_frame(rom, rec["header"])
        assert size == rec["w"] * rec["h"] == len(data)

def test_clone_writes_only_allocated_space():
    before = bytes(rom); clone_set(rom, SET_59, new_frames, alloc)
    assert changed_ranges(before, rom) <= alloc.used()
```

- [ ] **Step 2: Run and see them fail.**
- [ ] **Step 3: Implement `log2_sprites.py`.** Set and record layout: `re-sprite-decompression.md` (set table `0x3B4E90`, id N >= 7 uses entry N-7; record is 12 bytes). Confirm in the dispatcher at `0x0801F394` that type 0 copies `size` bytes from `header + 8`; label that check CONFIRMED in the doc before relying on it.
- [ ] **Step 4: Run and see them pass.**
- [ ] **Step 5: Export sets 53, 55, 56, 58 and 59** to `art\vanilla-sets\set53\` and so on, and record frame counts per animation in `docs\build-log.md`.

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

### Task 4: Reverse engineering, forms, transform input and HUD

**Files:**
- Create: `docs\research\re-forms.md`

**Interfaces:**
- Produces, as CONFIRMED facts: (a) the form table (per form: stat bonus, ki drain, sprite set or appearance, HUD icon), with the Super Saiyan values (+10 expected) and the Rage values; (b) the transform input handler and how it steps forms (the Z button); (c) how the Cell event forces Rage and keeps ki from draining; (d) where the HUD form icon ("Z") is stored and drawn, and how Buu's Fury draws its "Z3" (reference: `data\sprites\... Buu's Fury - Miscellaneous - HUD.png`); (e) the RAM addresses of Gohan's live STR, POW, END and EP while transformed, for my memory check; (f) the exact patch sites for Task 6 with original bytes.

- [ ] **Step 1: Find the form table** from the Super Saiyan +10 (status screen values 100 to 110 in my screenshot). Start from the appearance table at `rom:0x1D967C`: +0 bit 0 marks a transformed form and +4 names the form to transform into, so the stat bonus and ki drain are likely keyed by appearance entry.
- [ ] **Step 2: Trace the transform input** from the Z button press to the form change.
- [ ] **Step 3: Trace Rage** in the Cell event: which form id, and what stops the drain.
- [ ] **Step 4: Find the HUD icon** graphics (codec or raw) and its draw call.
- [ ] **Step 5: I verify** each CONFIRMED line before Task 6 starts. If the form system is hard-coded per event so that a new form needs large code changes, stop and report to me.

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

**Superseded by rulings** (full text in `docs\ledger\progress.md`):
- Ruling 13: Super Saiyan 2 art uses the set 59 layout, because set 58 lacks anims 9 and 21.
- Ruling 18: new set ids 157, 158 and 159, with the set table relocated at `rom:0x959C`.
- Ruling 27: each gi frame starts from the same-form original, not from set 53 (a style reference only).
- Ruling 30: each gi frame keeps the record geometry of its original frame.
- Ruling 35: every gi frame fits the 1024-byte slot. Set header +1 is not a direction count.
- Ruling 36: `make_gi_set` and `form_layout` replace `make_gi_base` and `make_gi_form`.

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

**Superseded by rulings** (full text in `docs\ledger\progress.md`):
- Ruling 19: the Super Saiyan 2 lightning must be blue.
- Ruling 31: the lightning is blue spark pixels in the set 159 frames, not a Rage aura object. Rage stays on armor set 58.
- Ruling 13: set 159 uses the set 59 layout (Task 5 note).
- Ruling 35: header +1 of a set is not a direction count (Task 5 note).

---

### Task 7 (optional): Gi portraits

**Files:**
- Create: `scripts\permanent\patches\gohan_portraits.py`, `docs\research\re-portraits.md`

- [ ] **Step 1: Find portrait storage and format** (probably the same codec). Time box: if it is not CONFIRMED within one task run, skip this task and log it as deferred to slice 2.
- [ ] **Step 2: Convert** Gohan's gi portraits from `data\reference\122601.png` (International sheet) for base, Super Saiyan and Super Saiyan 2. I approve them.
- [ ] **Step 3: Add the patch, rebuild** `builds\log2_poc.gba`, and log its SHA-1.

---

### Task 8: My acceptance run

**Files:**
- Modify: `docs\build-log.md`

- [ ] **Step 1: I load** `builds\log2_poc.gba` with `test-data\saves\log2_lv40_postcell.sav` (File > Load alternate save game, cheat off, cold boot).
- [ ] **Step 2: I run the design's acceptance tests 1, 2, 3, 4 and 5** (section 8.3). For test 3, I read the RAM addresses from `docs\research\re-forms.md` in the mGBA memory viewer before and after the transform, and hits the same enemy in Super Saiyan and in Super Saiyan 2.
- [ ] **Step 3: Record** pass or fail per test, with screenshots, in `docs\build-log.md`. Failures go back to the owning task.
