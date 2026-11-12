## Section 8

| Fact | Tags | Label | Tag |
|---|---|---|---|
| `set_leader` `sub_0800A680` cannot be found by a literal sweep. ZERO aligned ROM words equal `0x0800A680`, and no Thumb pc-relative load in the code region `rom:0x0` to `rom:0x28724` names it. Its only stored pointer is the Thumb word `0x0800A681` at `rom:0x3B5EF4`, which is `script_ext_ops` `rom:0x3B5D28` + 0x1CC, slot 115. So a sweep for its callers must use BL, not a word scan. IWRAM ARM code and unaligned words were not scanned | #script #tool | C (`whatis.py`, two shapes, controller verified) | WIS |

## Section 14

| Fact | Tags | Label | Tag |
|---|---|---|---|
| `0x03001FA8` is `Sprite_CurrentDirectory`, the name `RAM_LEDGER.csv` gives it with a behaviour test. Our own `disasm\symbols.py` called it `player_ptr` until 2026-11-05, and that wrong name cost hours: an agent and a cross-model review both repeated it back, and a whole diagnosis built on "the player pointer is NULL" was wrong, because zero is its normal resting value during play. The symbol is renamed and `test_whatis.py` fails if `player_ptr` returns. 61 more of our symbols read under a different name in `CODE_INDEX.md`, so open the handler before trusting either name | #object #tool | C (both files, the rename, the test) | WIS |
