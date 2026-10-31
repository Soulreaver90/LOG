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

