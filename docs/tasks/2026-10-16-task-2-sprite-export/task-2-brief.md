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

