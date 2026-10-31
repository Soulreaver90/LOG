# LOG active todos

## 2026-10-31: flat imports broken by the rom\ move

This morning's reorg moved 13 modules into `scripts\permanent\rom\`. **193 scripts under
`scripts\one-time\` still import them flatly and now fail**, measured, not estimated:

| module | scripts that import it flatly |
|---|---|
| `webfoot_decompress` | 163 |
| `log2_sprites` | 89 |
| `thumb_dis` | 70 |
| `rom_sheet` | 47 |
| `log2_save` | 35 |
| `state_dump` | 31 |
| `rom_space` | 24 |
| `re_sym` | 1 |

Confirmed in practice, not in theory: `scripts\one-time\2026-10-25-chapter-cards\c4v_patch.py` raises
`ModuleNotFoundError: No module named 'webfoot_decompress'`. The card 4 v10, v11 and v12 tools all import
it, so the card 4 tool chain carries the fault. The v12 task restated the rule in its own `c4y_lib.py`
rather than repair another task's folder, which was the right call for its brief.

This is fallout from my own reorg, so it is mine to fix, not a pre-existing defect.

**Final decisions, not urgent.** One-time scripts are historical records that already ran. Three ways:

1. Leave them. They are records. Repair one only when a task needs it, as the v12 task did.
2. Add 13 one-line shim modules at `scripts\permanent\` that re-export from `rom\`. Cheap, and it undoes
   some of the reorg's point.
3. Rewrite the 193 import lines. Thorough, mechanical, and touches a lot of history for little gain.

My recommendation is 1, because nothing in `permanent\` is affected and the suite is green.
